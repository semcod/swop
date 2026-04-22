"""DOQL bridge — markpact blocks → DoqlSpec → ProjectGraph intermediates.

This module is designed to work **with or without** the ``doql`` package
installed.  When ``doql`` is available it reuses the canonical parsers and
models; otherwise it falls back to a minimal in-memory representation that is
still enough to build a swop :class:`~swop.graph.ProjectGraph`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from swop.markpact.parser import ManifestBlock, ManifestParser
from swop.markpact.spec_models import (
    MinimalApiClient as _MinimalApiClient,
    MinimalCiConfig as _MinimalCiConfig,
    MinimalDatabase as _MinimalDatabase,
    MinimalDataSource as _MinimalDataSource,
    MinimalDeploy as _MinimalDeploy,
    MinimalDoqlSpec as _MinimalDoqlSpec,
    MinimalDocument as _MinimalDocument,
    MinimalEntity as _MinimalEntity,
    MinimalEntityField as _MinimalEntityField,
    MinimalEnvironment as _MinimalEnvironment,
    MinimalIngress as _MinimalIngress,
    MinimalInfrastructure as _MinimalInfrastructure,
    MinimalIntegration as _MinimalIntegration,
    MinimalInterface as _MinimalInterface,
    MinimalReport as _MinimalReport,
    MinimalRole as _MinimalRole,
    MinimalTemplate as _MinimalTemplate,
    MinimalWebhook as _MinimalWebhook,
    MinimalWorkflow as _MinimalWorkflow,
    MinimalWorkflowStep as _MinimalWorkflowStep,
)

if TYPE_CHECKING:
    from doql.parsers.models import DoqlSpec


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


    # --- per-type loaders (extracted to shrink cyclomatic complexity) ---

    @staticmethod
    def _load_entities(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for e in data.get('entities', []):
            if not isinstance(e, dict):
                continue
            fields = [
                _MinimalEntityField(
                    name=f.get('name', 'unknown'),
                    type=f.get('type', 'string'),
                    required=f.get('required', False),
                )
                for f in e.get('fields', [])
            ]
            spec.entities.append(_MinimalEntity(name=e.get('name', 'unknown'), fields=fields))

    @staticmethod
    def _load_databases(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for d in data.get('databases', []):
            if not isinstance(d, dict):
                continue
            spec.databases.append(
                _MinimalDatabase(
                    name=d.get('name', 'default'),
                    type=d.get('type', 'sqlite'),
                    file=d.get('file'),
                    url=d.get('url'),
                )
            )

    @staticmethod
    def _load_interfaces(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for i in data.get('interfaces', []):
            if not isinstance(i, dict):
                continue
            spec.interfaces.append(
                _MinimalInterface(
                    name=i.get('name', 'default'),
                    type=i.get('type', 'spa'),
                    pages=i.get('pages', []),
                    framework=i.get('framework'),
                    target=i.get('target'),
                )
            )

    @staticmethod
    def _load_workflows(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for w in data.get('workflows', []):
            if not isinstance(w, dict):
                continue
            steps = [
                _MinimalWorkflowStep(
                    action=s.get('action', ''),
                    target=s.get('target'),
                    params=s.get('params', {}),
                )
                for s in w.get('steps', [])
            ]
            spec.workflows.append(
                _MinimalWorkflow(
                    name=w.get('name', ''),
                    trigger=w.get('trigger'),
                    schedule=w.get('schedule'),
                    condition=w.get('condition'),
                    steps=steps,
                )
            )

    @staticmethod
    def _load_roles(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for r in data.get('roles', []):
            if not isinstance(r, dict):
                continue
            spec.roles.append(
                _MinimalRole(
                    name=r.get('name', ''),
                    permissions=r.get('permissions', []),
                )
            )

    @staticmethod
    def _load_integrations(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for ing in data.get('integrations', []):
            if not isinstance(ing, dict):
                continue
            spec.integrations.append(
                _MinimalIntegration(
                    name=ing.get('name', ''),
                    type=ing.get('type', 'email'),
                    config=ing.get('config', {}),
                )
            )

    @staticmethod
    def _load_webhooks(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for wh in data.get('webhooks', []):
            if not isinstance(wh, dict):
                continue
            spec.webhooks.append(
                _MinimalWebhook(
                    name=wh.get('name', ''),
                    source=wh.get('source'),
                    event=wh.get('event'),
                    auth=wh.get('auth'),
                    secret=wh.get('secret'),
                )
            )

    @staticmethod
    def _load_api_clients(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for ac in data.get('api_clients', []):
            if not isinstance(ac, dict):
                continue
            spec.api_clients.append(
                _MinimalApiClient(
                    name=ac.get('name', ''),
                    base_url=ac.get('base_url'),
                    auth=ac.get('auth'),
                    token=ac.get('token'),
                    openapi=ac.get('openapi'),
                    retry=ac.get('retry', 0),
                    timeout=ac.get('timeout'),
                    methods=ac.get('methods', []),
                )
            )

    @staticmethod
    def _load_data_sources(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for ds in data.get('data_sources', []):
            if not isinstance(ds, dict):
                continue
            spec.data_sources.append(
                _MinimalDataSource(
                    name=ds.get('name', ''),
                    source=ds.get('source', 'json'),
                    file=ds.get('file'),
                    url=ds.get('url'),
                    schema=ds.get('schema'),
                    auth=ds.get('auth'),
                    token=ds.get('token'),
                    cache=ds.get('cache'),
                    read_only=ds.get('read_only', False),
                    env_overrides=ds.get('env_overrides', False),
                )
            )

    @staticmethod
    def _load_templates(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for t in data.get('templates', []):
            if not isinstance(t, dict):
                continue
            spec.templates.append(
                _MinimalTemplate(
                    name=t.get('name', ''),
                    type=t.get('type', 'html'),
                    file=t.get('file'),
                    content=t.get('content'),
                    vars=t.get('vars', []),
                    engine=t.get('engine', 'jinja2'),
                )
            )

    @staticmethod
    def _load_documents(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for d in data.get('documents', []):
            if not isinstance(d, dict):
                continue
            spec.documents.append(
                _MinimalDocument(
                    name=d.get('name', ''),
                    type=d.get('type', 'pdf'),
                    template=d.get('template'),
                    data=d.get('data', {}),
                    output=d.get('output'),
                    styling=d.get('styling', {}),
                    metadata=d.get('metadata', {}),
                    signature=d.get('signature', {}),
                    hooks=d.get('hooks', {}),
                    partials=d.get('partials', []),
                )
            )

    @staticmethod
    def _load_reports(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for r in data.get('reports', []):
            if not isinstance(r, dict):
                continue
            spec.reports.append(
                _MinimalReport(
                    name=r.get('name', ''),
                    schedule=r.get('schedule'),
                    template=r.get('template'),
                    output=r.get('output', 'pdf'),
                    query=r.get('query', {}),
                    recipients=r.get('recipients', {}),
                    retention=r.get('retention'),
                )
            )

    @staticmethod
    def _load_environments(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for env in data.get('environments', []):
            if not isinstance(env, dict):
                continue
            spec.environments.append(
                _MinimalEnvironment(
                    name=env.get('name', ''),
                    runtime=env.get('runtime', 'docker-compose'),
                    ssh_host=env.get('ssh_host'),
                    env_file=env.get('env_file'),
                    replicas=env.get('replicas', 1),
                    config=env.get('config', {}),
                )
            )

    @staticmethod
    def _load_infrastructures(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for infra in data.get('infrastructures', []):
            if not isinstance(infra, dict):
                continue
            spec.infrastructures.append(
                _MinimalInfrastructure(
                    name=infra.get('name', ''),
                    type=infra.get('type', 'docker-compose'),
                    provider=infra.get('provider'),
                    namespace=infra.get('namespace'),
                    replicas=infra.get('replicas', 1),
                    config=infra.get('config', {}),
                )
            )

    @staticmethod
    def _load_ingresses(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for ing in data.get('ingresses', []):
            if not isinstance(ing, dict):
                continue
            spec.ingresses.append(
                _MinimalIngress(
                    name=ing.get('name', ''),
                    type=ing.get('type', 'traefik'),
                    tls=ing.get('tls', False),
                    cert_manager=ing.get('cert_manager'),
                    rate_limit=ing.get('rate_limit'),
                    config=ing.get('config', {}),
                )
            )

    @staticmethod
    def _load_ci_configs(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        for ci in data.get('ci_configs', []):
            if not isinstance(ci, dict):
                continue
            spec.ci_configs.append(
                _MinimalCiConfig(
                    name=ci.get('name', ''),
                    type=ci.get('type', 'github'),
                    runner=ci.get('runner'),
                    stages=ci.get('stages', []),
                    config=ci.get('config', {}),
                )
            )

    @staticmethod
    def _load_deploy(data: Dict[str, Any], spec: _MinimalDoqlSpec) -> None:
        deploy = data.get('deploy', {})
        if isinstance(deploy, dict):
            spec.deploy = _MinimalDeploy(
                target=deploy.get('target', 'docker-compose'),
                rootless=deploy.get('rootless', False),
                containers=deploy.get('containers', []),
                config=deploy.get('config', {}),
                directives=deploy.get('directives', {}),
            )

    def _build_minimal_spec(self, data: Dict[str, Any]) -> _MinimalDoqlSpec:
        spec = _MinimalDoqlSpec(
            app_name=data.get('app_name', 'Untitled'),
            version=data.get('version', '0.1.0'),
            domain=data.get('domain'),
            languages=data.get('languages', []),
            scenarios=data.get('scenarios', []),
            tests=data.get('tests', []),
            env_refs=data.get('env_refs', []),
        )
        self._load_entities(data, spec)
        self._load_databases(data, spec)
        self._load_interfaces(data, spec)
        self._load_workflows(data, spec)
        self._load_roles(data, spec)
        self._load_integrations(data, spec)
        self._load_webhooks(data, spec)
        self._load_api_clients(data, spec)
        self._load_data_sources(data, spec)
        self._load_templates(data, spec)
        self._load_documents(data, spec)
        self._load_reports(data, spec)
        self._load_environments(data, spec)
        self._load_infrastructures(data, spec)
        self._load_ingresses(data, spec)
        self._load_ci_configs(data, spec)
        self._load_deploy(data, spec)
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
