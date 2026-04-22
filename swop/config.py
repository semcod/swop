"""
swop.yaml configuration loader.

Parses the top-level ``swop.yaml`` that the ``swop init`` command
writes. The schema is intentionally permissive: unknown keys are kept on
``SwopConfig.extra`` so users can extend it without swop blocking.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("swop requires PyYAML; run `pip install pyyaml`.") from exc


DEFAULT_CONFIG_NAME = "swop.yaml"
DEFAULT_STATE_DIR = ".swop"


class SwopConfigError(ValueError):
    """Raised when ``swop.yaml`` is malformed."""


@dataclass
class BoundedContextConfig:
    name: str
    source: str
    external: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BusConfig:
    type: str = "rabbitmq"
    url: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReadModelConfig:
    engine: str = "postgresql"
    url: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SwopConfig:
    version: int = 1
    project: str = "unnamed"
    language: str = "python"
    source_roots: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    bounded_contexts: List[BoundedContextConfig] = field(default_factory=list)
    bus: Optional[BusConfig] = None
    read_models: Optional[ReadModelConfig] = None
    state_dir: str = DEFAULT_STATE_DIR
    extra: Dict[str, Any] = field(default_factory=dict)

    # Path where the config was loaded from; used for resolving relatives.
    config_path: Optional[Path] = None

    # ------------------------------------------------------------------

    @property
    def project_root(self) -> Path:
        if self.config_path is None:
            return Path.cwd()
        return self.config_path.parent

    @property
    def state_path(self) -> Path:
        return self.project_root / self.state_dir

    def context(self, name: str) -> Optional[BoundedContextConfig]:
        for ctx in self.bounded_contexts:
            if ctx.name == name:
                return ctx
        return None

    def iter_source_roots(self) -> Iterable[Path]:
        root = self.project_root
        for rel in self.source_roots:
            yield (root / rel).resolve()


# ----------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------


_ENV_RX = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return _ENV_RX.sub(lambda m: os.environ.get(m.group(1), m.group(0)), value)
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    return value


def _pop_known(
    data: Dict[str, Any], keys: Iterable[str]
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    known: Dict[str, Any] = {}
    for key in keys:
        if key in data:
            known[key] = data.pop(key)
    return known, data


def _parse_context(raw: Dict[str, Any]) -> BoundedContextConfig:
    if "name" not in raw or "source" not in raw:
        raise SwopConfigError(
            f"bounded_contexts entry missing 'name' or 'source': {raw!r}"
        )
    known, extra = _pop_known(dict(raw), ("name", "source", "external"))
    return BoundedContextConfig(
        name=str(known["name"]),
        source=str(known["source"]),
        external=bool(known.get("external", False)),
        extra=extra,
    )


def _parse_bus(raw: Optional[Dict[str, Any]]) -> Optional[BusConfig]:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise SwopConfigError(f"bus must be a mapping, got {type(raw).__name__}")
    known, extra = _pop_known(dict(raw), ("type", "url"))
    return BusConfig(
        type=str(known.get("type", "rabbitmq")),
        url=known.get("url"),
        extra=extra,
    )


def _parse_read_models(raw: Optional[Dict[str, Any]]) -> Optional[ReadModelConfig]:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise SwopConfigError(
            f"read_models must be a mapping, got {type(raw).__name__}"
        )
    known, extra = _pop_known(dict(raw), ("engine", "url"))
    return ReadModelConfig(
        engine=str(known.get("engine", "postgresql")),
        url=known.get("url"),
        extra=extra,
    )


def load_config(path: Optional[Path] = None) -> SwopConfig:
    """Load and validate ``swop.yaml`` from ``path`` (default: cwd)."""
    cfg_path = Path(path) if path else Path.cwd() / DEFAULT_CONFIG_NAME
    if not cfg_path.exists():
        raise SwopConfigError(f"swop config not found: {cfg_path}")
    try:
        raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise SwopConfigError(f"invalid YAML in {cfg_path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise SwopConfigError(
            f"swop.yaml must be a mapping at the top level, got {type(raw).__name__}"
        )
    return _from_dict(_expand_env(raw), cfg_path)


def _from_dict(data: Dict[str, Any], cfg_path: Optional[Path]) -> SwopConfig:
    data = dict(data)  # copy; we'll pop
    version = int(data.pop("version", 1))
    project = str(data.pop("project", "unnamed"))
    language = str(data.pop("language", "python"))
    source_roots = list(data.pop("source_roots", []) or [])
    exclude = list(data.pop("exclude", []) or [])
    bounded_contexts_raw = data.pop("bounded_contexts", []) or []
    bus_raw = data.pop("bus", None)
    read_models_raw = data.pop("read_models", None)
    state_dir = str(data.pop("state_dir", DEFAULT_STATE_DIR))

    if not isinstance(bounded_contexts_raw, list):
        raise SwopConfigError(
            f"bounded_contexts must be a list, got {type(bounded_contexts_raw).__name__}"
        )
    contexts = [_parse_context(item) for item in bounded_contexts_raw]

    return SwopConfig(
        version=version,
        project=project,
        language=language,
        source_roots=[str(x) for x in source_roots],
        exclude=[str(x) for x in exclude],
        bounded_contexts=contexts,
        bus=_parse_bus(bus_raw),
        read_models=_parse_read_models(read_models_raw),
        state_dir=state_dir,
        extra=data,  # whatever keys remain
        config_path=cfg_path,
    )
