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
    containers: List[Dict[str, Any]] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    directives: Dict[str, str] = field(default_factory=dict)


@dataclass
class _MinimalWorkflowStep:
    action: str = ""
    target: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class _MinimalWorkflow:
    name: str = ""
    trigger: Optional[str] = None
    schedule: Optional[str] = None
    condition: Optional[str] = None
    steps: List[_MinimalWorkflowStep] = field(default_factory=list)


@dataclass
class _MinimalRole:
    name: str = ""
    permissions: List[str] = field(default_factory=list)


@dataclass
class _MinimalIntegration:
    name: str = ""
    type: str = "email"
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class _MinimalWebhook:
    name: str = ""
    source: Optional[str] = None
    event: Optional[str] = None
    auth: Optional[str] = None
    secret: Optional[str] = None


@dataclass
class _MinimalApiClient:
    name: str = ""
    base_url: Optional[str] = None
    auth: Optional[str] = None
    token: Optional[str] = None
    openapi: Optional[str] = None
    retry: int = 0
    timeout: Optional[str] = None
    methods: List[str] = field(default_factory=list)


@dataclass
class _MinimalEnvironment:
    name: str = ""
    runtime: str = "docker-compose"
    ssh_host: Optional[str] = None
    env_file: Optional[str] = None
    replicas: int = 1
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class _MinimalInfrastructure:
    name: str = ""
    type: str = "docker-compose"
    provider: Optional[str] = None
    namespace: Optional[str] = None
    replicas: int = 1
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class _MinimalIngress:
    name: str = ""
    type: str = "traefik"
    tls: bool = False
    cert_manager: Optional[str] = None
    rate_limit: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class _MinimalCiConfig:
    name: str = ""
    type: str = "github"
    runner: Optional[str] = None
    stages: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class _MinimalDataSource:
    name: str = ""
    source: str = "json"
    file: Optional[str] = None
    url: Optional[str] = None
    schema: Optional[str] = None
    auth: Optional[str] = None
    token: Optional[str] = None
    cache: Optional[str] = None
    read_only: bool = False
    env_overrides: bool = False


@dataclass
class _MinimalTemplate:
    name: str = ""
    type: str = "html"
    file: Optional[str] = None
    content: Optional[str] = None
    vars: List[str] = field(default_factory=list)
    engine: str = "jinja2"


@dataclass
class _MinimalDocument:
    name: str = ""
    type: str = "pdf"
    template: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    output: Optional[str] = None
    styling: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: Dict[str, Any] = field(default_factory=dict)
    hooks: Dict[str, Any] = field(default_factory=dict)
    partials: List[str] = field(default_factory=list)


@dataclass
class _MinimalReport:
    name: str = ""
    schedule: Optional[str] = None
    template: Optional[str] = None
    output: str = "pdf"
    query: Dict[str, Any] = field(default_factory=dict)
    recipients: Dict[str, Any] = field(default_factory=dict)
    retention: Optional[str] = None


@dataclass
class _MinimalDoqlSpec:
    app_name: str = "Untitled"
    version: str = "0.1.0"
    domain: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    entities: List[_MinimalEntity] = field(default_factory=list)
    databases: List[_MinimalDatabase] = field(default_factory=list)
    interfaces: List[_MinimalInterface] = field(default_factory=list)
    data_sources: List[_MinimalDataSource] = field(default_factory=list)
    templates: List[_MinimalTemplate] = field(default_factory=list)
    documents: List[_MinimalDocument] = field(default_factory=list)
    reports: List[_MinimalReport] = field(default_factory=list)
    api_clients: List[_MinimalApiClient] = field(default_factory=list)
    webhooks: List[_MinimalWebhook] = field(default_factory=list)
    integrations: List[_MinimalIntegration] = field(default_factory=list)
    workflows: List[_MinimalWorkflow] = field(default_factory=list)
    roles: List[_MinimalRole] = field(default_factory=list)
    environments: List[_MinimalEnvironment] = field(default_factory=list)
    infrastructures: List[_MinimalInfrastructure] = field(default_factory=list)
    ingresses: List[_MinimalIngress] = field(default_factory=list)
    ci_configs: List[_MinimalCiConfig] = field(default_factory=list)
    deploy: _MinimalDeploy = field(default_factory=_MinimalDeploy)
    scenarios: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    env_refs: List[str] = field(default_factory=list)
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

    # Kinds that the bridge understands and maps to top-level spec keys
    _STRUCTURAL_KINDS = frozenset({
        "doql", "workflows", "roles", "integrations", "webhooks",
        "api_clients", "environments", "infrastructures", "ingresses",
        "ci_configs", "data_sources", "templates", "documents", "reports",
        "scenarios", "tests", "deploy",
    })

    def from_blocks(self, blocks: List[ManifestBlock]) -> Any:
        """Merge all known ``markpact:*`` blocks into a single DoqlSpec.

        Supports ``doql``, ``workflows``, ``roles``, ``deploy``,
        ``integrations``, ``webhooks``, ``api_clients``, ``environments``,
        ``infrastructures``, ``ingresses``, ``ci_configs``, ``data_sources``,
        ``templates``, ``documents``, ``reports``, ``scenarios``, ``tests``.
        """
        relevant = [b for b in blocks if b.kind in self._STRUCTURAL_KINDS]
        if not relevant:
            raise MarkpactValidationError(
                "No supported markpact blocks found in manifest.",
                blocks=blocks,
            )

        merged: Dict[str, Any] = {
            "app_name": "Untitled",
            "version": "0.1.0",
        }

        for block in relevant:
            try:
                fragment = self._parse_block(block)
            except Exception as exc:
                msg = f"Failed to parse {block.kind} block at line {block.line_start}: {exc}"
                if self.strict:
                    raise MarkpactValidationError(msg, blocks=[block]) from exc
                continue

            if block.kind == "doql":
                merged = self._merge_fragment(merged, fragment)
            elif block.kind == "deploy":
                deploy = fragment.get("deploy", fragment)
                if isinstance(deploy, dict):
                    merged["deploy"] = self._merge_fragment(
                        merged.get("deploy", {}), deploy
                    )
            else:
                # e.g. workflows, roles, api_clients ...
                items = fragment.get(block.kind, fragment)
                if isinstance(items, list):
                    existing = merged.get(block.kind, [])
                    if isinstance(existing, list):
                        merged[block.kind] = existing + list(items)
                    else:
                        merged[block.kind] = list(items)
                elif isinstance(items, dict):
                    merged[block.kind] = self._merge_fragment(
                        merged.get(block.kind, {}), items
                    )
                else:
                    merged[block.kind] = items

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
            scenarios=data.get("scenarios", []),
            tests=data.get("tests", []),
            env_refs=data.get("env_refs", []),
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

        for w in data.get("workflows", []):
            if isinstance(w, dict):
                steps = [
                    _MinimalWorkflowStep(
                        action=s.get("action", ""),
                        target=s.get("target"),
                        params=s.get("params", {}),
                    )
                    for s in w.get("steps", [])
                ]
                spec.workflows.append(
                    _MinimalWorkflow(
                        name=w.get("name", ""),
                        trigger=w.get("trigger"),
                        schedule=w.get("schedule"),
                        condition=w.get("condition"),
                        steps=steps,
                    )
                )

        for r in data.get("roles", []):
            if isinstance(r, dict):
                spec.roles.append(
                    _MinimalRole(
                        name=r.get("name", ""),
                        permissions=r.get("permissions", []),
                    )
                )

        for ing in data.get("integrations", []):
            if isinstance(ing, dict):
                spec.integrations.append(
                    _MinimalIntegration(
                        name=ing.get("name", ""),
                        type=ing.get("type", "email"),
                        config=ing.get("config", {}),
                    )
                )

        for wh in data.get("webhooks", []):
            if isinstance(wh, dict):
                spec.webhooks.append(
                    _MinimalWebhook(
                        name=wh.get("name", ""),
                        source=wh.get("source"),
                        event=wh.get("event"),
                        auth=wh.get("auth"),
                        secret=wh.get("secret"),
                    )
                )

        for ac in data.get("api_clients", []):
            if isinstance(ac, dict):
                spec.api_clients.append(
                    _MinimalApiClient(
                        name=ac.get("name", ""),
                        base_url=ac.get("base_url"),
                        auth=ac.get("auth"),
                        token=ac.get("token"),
                        openapi=ac.get("openapi"),
                        retry=ac.get("retry", 0),
                        timeout=ac.get("timeout"),
                        methods=ac.get("methods", []),
                    )
                )

        for ds in data.get("data_sources", []):
            if isinstance(ds, dict):
                spec.data_sources.append(
                    _MinimalDataSource(
                        name=ds.get("name", ""),
                        source=ds.get("source", "json"),
                        file=ds.get("file"),
                        url=ds.get("url"),
                        schema=ds.get("schema"),
                        auth=ds.get("auth"),
                        token=ds.get("token"),
                        cache=ds.get("cache"),
                        read_only=ds.get("read_only", False),
                        env_overrides=ds.get("env_overrides", False),
                    )
                )

        for t in data.get("templates", []):
            if isinstance(t, dict):
                spec.templates.append(
                    _MinimalTemplate(
                        name=t.get("name", ""),
                        type=t.get("type", "html"),
                        file=t.get("file"),
                        content=t.get("content"),
                        vars=t.get("vars", []),
                        engine=t.get("engine", "jinja2"),
                    )
                )

        for d in data.get("documents", []):
            if isinstance(d, dict):
                spec.documents.append(
                    _MinimalDocument(
                        name=d.get("name", ""),
                        type=d.get("type", "pdf"),
                        template=d.get("template"),
                        data=d.get("data", {}),
                        output=d.get("output"),
                        styling=d.get("styling", {}),
                        metadata=d.get("metadata", {}),
                        signature=d.get("signature", {}),
                        hooks=d.get("hooks", {}),
                        partials=d.get("partials", []),
                    )
                )

        for r in data.get("reports", []):
            if isinstance(r, dict):
                spec.reports.append(
                    _MinimalReport(
                        name=r.get("name", ""),
                        schedule=r.get("schedule"),
                        template=r.get("template"),
                        output=r.get("output", "pdf"),
                        query=r.get("query", {}),
                        recipients=r.get("recipients", {}),
                        retention=r.get("retention"),
                    )
                )

        for env in data.get("environments", []):
            if isinstance(env, dict):
                spec.environments.append(
                    _MinimalEnvironment(
                        name=env.get("name", ""),
                        runtime=env.get("runtime", "docker-compose"),
                        ssh_host=env.get("ssh_host"),
                        env_file=env.get("env_file"),
                        replicas=env.get("replicas", 1),
                        config=env.get("config", {}),
                    )
                )

        for infra in data.get("infrastructures", []):
            if isinstance(infra, dict):
                spec.infrastructures.append(
                    _MinimalInfrastructure(
                        name=infra.get("name", ""),
                        type=infra.get("type", "docker-compose"),
                        provider=infra.get("provider"),
                        namespace=infra.get("namespace"),
                        replicas=infra.get("replicas", 1),
                        config=infra.get("config", {}),
                    )
                )

        for ing in data.get("ingresses", []):
            if isinstance(ing, dict):
                spec.ingresses.append(
                    _MinimalIngress(
                        name=ing.get("name", ""),
                        type=ing.get("type", "traefik"),
                        tls=ing.get("tls", False),
                        cert_manager=ing.get("cert_manager"),
                        rate_limit=ing.get("rate_limit"),
                        config=ing.get("config", {}),
                    )
                )

        for ci in data.get("ci_configs", []):
            if isinstance(ci, dict):
                spec.ci_configs.append(
                    _MinimalCiConfig(
                        name=ci.get("name", ""),
                        type=ci.get("type", "github"),
                        runner=ci.get("runner"),
                        stages=ci.get("stages", []),
                        config=ci.get("config", {}),
                    )
                )

        deploy = data.get("deploy", {})
        if isinstance(deploy, dict):
            spec.deploy = _MinimalDeploy(
                target=deploy.get("target", "docker-compose"),
                rootless=deploy.get("rootless", False),
                containers=deploy.get("containers", []),
                config=deploy.get("config", {}),
                directives=deploy.get("directives", {}),
            )

        return spec

    def from_file(self, path: Path) -> Any:
        parser = ManifestParser(base_dir=path.parent)
        blocks = parser.parse_file(path)
        return self.from_blocks(blocks)

    def from_files(self, paths: List[Path]) -> Any:
        """Merge multiple manifest files into a single DoqlSpec."""
        all_blocks: List[ManifestBlock] = []
        for path in paths:
            parser = ManifestParser(base_dir=path.parent)
            all_blocks.extend(parser.parse_file(path))
        return self.from_blocks(all_blocks)

    def from_text(self, text: str) -> Any:
        parser = ManifestParser()
        blocks = parser.parse(text)
        return self.from_blocks(blocks)
