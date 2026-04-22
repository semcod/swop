"""DOQL bridge — markpact blocks → DoqlSpec → ProjectGraph intermediates.

This module is designed to work **with or without** the ``doql`` package
installed.  When ``doql`` is available it reuses the canonical parsers and
models; otherwise it falls back to a minimal in-memory representation that is
still enough to build a swop :class:`~swop.graph.ProjectGraph`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from swop.markpact.parser import ManifestBlock, ManifestParser

if TYPE_CHECKING:
    from doql.parsers.models import DoqlSpec


# ─── Fallback minimal DoqlSpec ──────────────────────────────────────

@dataclass
class _MinimalEntityField:
    name: str
    type: str = "string"
    required: bool = False


@dataclass
class _MinimalEntity:
    name: str
    fields: List[_MinimalEntityField] = field(default_factory=list)


@dataclass
class _MinimalInterface:
    name: str
    type: str = "spa"
    pages: List[Dict[str, Any]] = field(default_factory=list)
    framework: Optional[str] = None
    target: Optional[str] = None


@dataclass
class _MinimalDatabase:
    name: str
    type: str = "sqlite"
    file: Optional[str] = None
    url: Optional[str] = None


@dataclass
class _MinimalDeploy:
    target: str = "docker-compose"
    rootless: bool = False


@dataclass
class _MinimalDoqlSpec:
    app_name: str = "Untitled"
    version: str = "0.1.0"
    domain: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    entities: List[_MinimalEntity] = field(default_factory=list)
    databases: List[_MinimalDatabase] = field(default_factory=list)
    interfaces: List[_MinimalInterface] = field(default_factory=list)
    workflows: List[Any] = field(default_factory=list)
    integrations: List[Any] = field(default_factory=list)
    api_clients: List[Any] = field(default_factory=list)
    roles: List[Any] = field(default_factory=list)
    deploy: _MinimalDeploy = field(default_factory=_MinimalDeploy)
    parse_errors: List[Any] = field(default_factory=list)


# ─── Error types ───────────────────────────────────────────────────

class MarkpactValidationError(Exception):
    """Raised when a manifest block cannot be parsed into a DOQL spec."""

    def __init__(self, message: str, blocks: Optional[List[ManifestBlock]] = None) -> None:
        super().__init__(message)
        self.blocks = blocks or []


# ─── Bridge ────────────────────────────────────────────────────────

class DoqlBridge:
    """Convert a collection of ``ManifestBlock`` objects into a DoqlSpec."""

    def __init__(self, *, strict: bool = False) -> None:
        self.strict = strict
        self._has_doql = False
        self._spec_cls: Any = _MinimalDoqlSpec
        self._import_yaml: Any = None
        self._try_import_doql()

    def _try_import_doql(self) -> None:
        try:
            from doql.parsers.models import DoqlSpec  # type: ignore[import]
            from doql.importers.yaml_importer import import_yaml  # type: ignore[import]
            self._spec_cls = DoqlSpec
            self._import_yaml = import_yaml
            self._has_doql = True
        except ImportError:
            self._has_doql = False

    def from_blocks(self, blocks: List[ManifestBlock]) -> Any:
        """Merge all ``markpact:doql`` blocks into a single DoqlSpec."""
        doql_blocks = [b for b in blocks if b.kind == "doql"]
        if not doql_blocks:
            raise MarkpactValidationError(
                "No markpact:doql blocks found in manifest.",
                blocks=blocks,
            )

        merged: Dict[str, Any] = {
            "app_name": "Untitled",
            "version": "0.1.0",
        }

        for block in doql_blocks:
            try:
                fragment = self._parse_block(block)
            except Exception as exc:
                msg = f"Failed to parse doql block at line {block.line_start}: {exc}"
                if self.strict:
                    raise MarkpactValidationError(msg, blocks=[block]) from exc
                continue
            merged = self._merge_fragment(merged, fragment)

        return self._build_spec(merged)

    @staticmethod
    def _parse_block(block: ManifestBlock) -> Dict[str, Any]:
        lang = block.lang.lower()
        if lang in ("yaml", "yml"):
            import yaml
            return yaml.safe_load(block.body) or {}
        if lang == "json":
            import json
            return json.loads(block.body)
        if lang in ("doql", "css", "less", "sass"):
            return {"_raw_doql": block.body}
        raise ValueError(f"Unsupported doql block language: {lang}")

    @staticmethod
    def _merge_fragment(base: Dict[str, Any], fragment: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(base)

        for key, value in fragment.items():
            if key.startswith("_"):
                continue
            if isinstance(value, list) and key in result:
                existing = result.get(key, [])
                if isinstance(existing, list):
                    result[key] = existing + list(value)
                else:
                    result[key] = list(value)
            elif isinstance(value, dict) and key in result:
                existing = result.get(key, {})
                if isinstance(existing, dict):
                    merged_dict = dict(existing)
                    merged_dict.update(value)
                    result[key] = merged_dict
                else:
                    result[key] = dict(value)
            else:
                result[key] = value

        return result

    def _build_spec(self, data: Dict[str, Any]) -> Any:
        if self._has_doql and self._import_yaml is not None:
            try:
                return self._import_yaml(data)
            except Exception:
                if self.strict:
                    raise
        return self._build_minimal_spec(data)

    def _build_minimal_spec(self, data: Dict[str, Any]) -> _MinimalDoqlSpec:
        spec = _MinimalDoqlSpec(
            app_name=data.get("app_name", "Untitled"),
            version=data.get("version", "0.1.0"),
            domain=data.get("domain"),
            languages=data.get("languages", []),
        )

        for e in data.get("entities", []):
            if isinstance(e, dict):
                fields = [
                    _MinimalEntityField(
                        name=f.get("name", "unknown"),
                        type=f.get("type", "string"),
                        required=f.get("required", False),
                    )
                    for f in e.get("fields", [])
                ]
                spec.entities.append(_MinimalEntity(name=e.get("name", "unknown"), fields=fields))

        for d in data.get("databases", []):
            if isinstance(d, dict):
                spec.databases.append(
                    _MinimalDatabase(
                        name=d.get("name", "default"),
                        type=d.get("type", "sqlite"),
                        file=d.get("file"),
                        url=d.get("url"),
                    )
                )

        for i in data.get("interfaces", []):
            if isinstance(i, dict):
                spec.interfaces.append(
                    _MinimalInterface(
                        name=i.get("name", "default"),
                        type=i.get("type", "spa"),
                        pages=i.get("pages", []),
                        framework=i.get("framework"),
                        target=i.get("target"),
                    )
                )

        deploy = data.get("deploy", {})
        if isinstance(deploy, dict):
            spec.deploy = _MinimalDeploy(
                target=deploy.get("target", "docker-compose"),
                rootless=deploy.get("rootless", False),
            )

        return spec

    def from_file(self, path: Path) -> Any:
        parser = ManifestParser(base_dir=path.parent)
        blocks = parser.parse_file(path)
        return self.from_blocks(blocks)

    def from_text(self, text: str) -> Any:
        parser = ManifestParser()
        blocks = parser.parse(text)
        return self.from_blocks(blocks)
