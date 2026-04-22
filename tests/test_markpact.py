"""Tests for swop.markpact integration.

Covers:
- ManifestParser (multi-format block extraction)
- DoqlBridge (blocks -> DoqlSpec)
- build_project_graph (DoqlSpec -> ProjectGraph)
- ManifestSyncEngine (filesystem sync check)
"""

import json
from pathlib import Path

import pytest

from swop.graph import DataModel, ProjectGraph
from swop.markpact import (
    DoqlBridge,
    ManifestParser,
    ManifestSyncEngine,
    build_project_graph,
)


# ──────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────

SIMPLE_MANIFEST = """
# My System

```yaml markpact:doql
app_name: "TestApp"
version: "1.0.0"

entities:
  - name: User
    fields:
      - name: id
        type: string
        required: true
      - name: email
        type: string
        required: true
```

```json markpact:graph
{
  "services": {
    "api": {
      "routes": ["/users", "/health"]
    }
  }
}
```

```python markpact:file path=src/main.py
print("hello")
```

```yaml markpact:config
debug: true
```
""".strip()


@pytest.fixture
def tmp_manifest(tmp_path: Path) -> Path:
    p = tmp_path / "manifest.md"
    p.write_text(SIMPLE_MANIFEST, encoding="utf-8")
    return p


# ──────────────────────────────────────────
# ManifestParser
# ──────────────────────────────────────────


def test_parser_finds_all_blocks(tmp_manifest: Path) -> None:
    parser = ManifestParser(base_dir=tmp_manifest.parent)
    blocks = parser.parse_file(tmp_manifest)

    kinds = {b.kind for b in blocks}
    assert kinds == {"doql", "graph", "file", "config"}


def test_parser_counts_blocks(tmp_manifest: Path) -> None:
    parser = ManifestParser(base_dir=tmp_manifest.parent)
    blocks = parser.parse_file(tmp_manifest)
    assert len(blocks) == 4


def test_parser_extracts_meta() -> None:
    parser = ManifestParser()
    blocks = parser.parse(SIMPLE_MANIFEST)
    file_block = [b for b in blocks if b.kind == "file"][0]
    assert file_block.get_meta_value("path") == "src/main.py"
    assert file_block.lang == "python"


def test_parser_doql_block_body() -> None:
    parser = ManifestParser()
    blocks = parser.parse(SIMPLE_MANIFEST)
    doql_block = [b for b in blocks if b.kind == "doql"][0]
    assert "app_name: \"TestApp\"" in doql_block.body
    assert "entities:" in doql_block.body


def test_parser_filter_by_kind(tmp_manifest: Path) -> None:
    parser = ManifestParser(base_dir=tmp_manifest.parent)
    doql_blocks = parser.parse_by_kind(SIMPLE_MANIFEST, "doql")
    assert len(doql_blocks) == 1
    assert doql_blocks[0].lang == "yaml"


def test_parser_includes(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "included.md").write_text(
        '```yaml markpact:doql\napp_name: "Included"\n```',
        encoding="utf-8",
    )
    root = tmp_path / "root.md"
    root.write_text(
        f"# Root\n<!-- markpact:include path=sub/included.md -->\n",
        encoding="utf-8",
    )

    parser = ManifestParser(base_dir=tmp_path)
    blocks = parser.parse_file(root)
    names = {b.kind for b in blocks}
    assert "doql" in names


# ──────────────────────────────────────────
# DoqlBridge
# ──────────────────────────────────────────


def test_bridge_from_text() -> None:
    bridge = DoqlBridge()
    spec = bridge.from_text(SIMPLE_MANIFEST)

    assert spec.app_name == "TestApp"
    assert spec.version == "1.0.0"
    assert len(spec.entities) == 1
    assert spec.entities[0].name == "User"


def test_bridge_missing_any_supported_blocks_raises() -> None:
    bridge = DoqlBridge()
    with pytest.raises(Exception):
        bridge.from_text("# no supported blocks")


def test_bridge_strict_mode() -> None:
    bridge = DoqlBridge(strict=True)
    spec = bridge.from_text(SIMPLE_MANIFEST)
    assert spec.app_name == "TestApp"


def test_bridge_merge_multiple_doql() -> None:
    text = """
```yaml markpact:doql
app_name: "App"
entities:
  - name: A
    fields: []
```

```yaml markpact:doql
databases:
  - name: db1
    type: sqlite
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(text)
    assert spec.app_name == "App"
    assert len(spec.entities) == 1
    assert len(spec.databases) == 1


# ──────────────────────────────────────────
# build_project_graph
# ──────────────────────────────────────────


def test_graph_from_doql_spec() -> None:
    bridge = DoqlBridge()
    spec = bridge.from_text(SIMPLE_MANIFEST)
    graph = build_project_graph(spec)

    assert isinstance(graph, ProjectGraph)
    assert "User" in graph.models
    user_model = graph.models["User"]
    assert isinstance(user_model, DataModel)
    assert "id" in user_model.fields
    assert "email" in user_model.fields


def test_graph_services_from_interfaces() -> None:
    manifest = """
```yaml markpact:doql
interfaces:
  - name: web
    type: spa
    pages:
      - name: Home
        path: /
      - name: Admin
        path: /admin
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)

    assert "web" in graph.services
    assert "/" in graph.services["web"].routes
    assert "/admin" in graph.services["web"].routes


def test_graph_ui_bindings_from_pages() -> None:
    manifest = """
```yaml markpact:doql
interfaces:
  - name: web
    type: spa
    pages:
      - name: Dashboard
        path: /dashboard
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)

    selectors = {b.selector for b in graph.ui_bindings}
    assert any("dashboard" in s for s in selectors)


def test_graph_databases_as_services() -> None:
    manifest = """
```yaml markpact:doql
databases:
  - name: main
    type: sqlite
    file: app.db
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)

    assert "db-main" in graph.services
    assert "/schema" in graph.services["db-main"].routes


# ──────────────────────────────────────────
# ManifestSyncEngine
# ──────────────────────────────────────────


def test_sync_check_identical(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.md"
    manifest.write_text(
        '```python markpact:file path=src/hello.py\nprint("hello")\n```',
        encoding="utf-8",
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "hello.py").write_text('print("hello")', encoding="utf-8")

    engine = ManifestSyncEngine(base_dir=tmp_path)
    statuses = engine.check(manifest)
    assert len(statuses) == 1
    assert statuses[0].identical is True


def test_sync_check_modified(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.md"
    manifest.write_text(
        '```python markpact:file path=src/hello.py\nprint("hello")\n```',
        encoding="utf-8",
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "hello.py").write_text('print("world")', encoding="utf-8")

    engine = ManifestSyncEngine(base_dir=tmp_path)
    statuses = engine.check(manifest)
    assert statuses[0].identical is False
    assert statuses[0].on_disk is True


def test_sync_check_missing(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.md"
    manifest.write_text(
        '```python markpact:file path=src/hello.py\nprint("hello")\n```',
        encoding="utf-8",
    )

    engine = ManifestSyncEngine(base_dir=tmp_path)
    statuses = engine.check(manifest)
    assert statuses[0].on_disk is False


def test_sync_to_disk(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.md"
    manifest.write_text(
        '```python markpact:file path=src/main.py\ndef main(): pass\n```',
        encoding="utf-8",
    )

    engine = ManifestSyncEngine(base_dir=tmp_path)
    written = engine.sync_to_disk(manifest)
    assert "src/main.py" in written
    assert (tmp_path / "src" / "main.py").read_text(encoding="utf-8") == "def main(): pass"


def test_sync_to_disk_dry_run(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.md"
    manifest.write_text(
        '```python markpact:file path=src/main.py\ndef main(): pass\n```',
        encoding="utf-8",
    )

    engine = ManifestSyncEngine(base_dir=tmp_path)
    written = engine.sync_to_disk(manifest, dry_run=True)
    assert "src/main.py" in written
    assert not (tmp_path / "src" / "main.py").exists()


def test_sync_from_disk(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.md"
    manifest.write_text(
        '```python markpact:file path=src/main.py\nold\n```',
        encoding="utf-8",
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("new\n", encoding="utf-8")

    engine = ManifestSyncEngine(base_dir=tmp_path)
    updated = engine.sync_from_disk(manifest)
    assert updated["src/main.py"] == "new\n"


def test_diff_report(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.md"
    manifest.write_text(
        '```python markpact:file path=src/a.py\na\n```',
        encoding="utf-8",
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.py").write_text("b\n", encoding="utf-8")

    engine = ManifestSyncEngine(base_dir=tmp_path)
    diffs = engine.diff(manifest)
    paths = {d[0] for d in diffs}
    assert "src/a.py" in paths
    statuses = {d[1] for d in diffs if d[0] == "src/a.py"}
    assert "modified" in statuses


# ──────────────────────────────────────────
# CLI integration
# ──────────────────────────────────────────


def test_graph_workflows_as_services() -> None:
    manifest = """
```yaml markpact:workflows
workflows:
  - name: onboard
    trigger: signup
    steps:
      - action: email
        target: admin@test.com
      - action: slack
        target: "#ops"
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "workflow-onboard" in graph.services
    wf = graph.services["workflow-onboard"]
    assert "/trigger/signup" in wf.routes
    assert "/step/0" in wf.routes
    assert wf.routes["/step/0"]["action"] == "email"


def test_graph_roles_as_services() -> None:
    manifest = """
```yaml markpact:roles
roles:
  - name: admin
    permissions:
      - users:write
      - devices:delete
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "role-admin" in graph.services
    assert "/perm/users:write" in graph.services["role-admin"].routes


def test_graph_api_clients_as_services() -> None:
    manifest = """
```yaml markpact:api_clients
api_clients:
  - name: stripe
    base_url: "https://api.stripe.com"
    methods:
      - POST
      - GET
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "api-stripe" in graph.services
    assert "/base_url" in graph.services["api-stripe"].routes
    assert "/method/POST" in graph.services["api-stripe"].routes


def test_graph_webhooks_as_services() -> None:
    manifest = """
```yaml markpact:webhooks
webhooks:
  - name: github-push
    source: github
    event: push
    auth: hmac
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "webhook-github-push" in graph.services
    assert graph.services["webhook-github-push"].routes["/event"]["event"] == "push"


def test_graph_integrations_as_services() -> None:
    manifest = """
```yaml markpact:integrations
integrations:
  - name: mailgun
    type: email
    config:
      domain: mg.example.com
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "integration-mailgun" in graph.services
    assert graph.services["integration-mailgun"].routes["/type"]["type"] == "email"


def test_graph_environments_as_services() -> None:
    manifest = """
```yaml markpact:environments
environments:
  - name: prod
    runtime: kubernetes
    replicas: 3
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "env-prod" in graph.services
    assert graph.services["env-prod"].routes["/runtime"]["runtime"] == "kubernetes"


def test_graph_infrastructures_as_services() -> None:
    manifest = """
```yaml markpact:infrastructures
infrastructures:
  - name: do-k8s
    type: kubernetes
    provider: digitalocean
    namespace: app
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "infra-do-k8s" in graph.services
    assert graph.services["infra-do-k8s"].routes["/provider"]["provider"] == "digitalocean"


def test_graph_ingresses_as_services() -> None:
    manifest = """
```yaml markpact:ingresses
ingresses:
  - name: main
    type: traefik
    tls: true
    rate_limit: "100r/m"
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "ingress-main" in graph.services
    assert graph.services["ingress-main"].routes["/tls"]["enabled"] is True


def test_graph_ci_configs_as_services() -> None:
    manifest = """
```yaml markpact:ci_configs
ci_configs:
  - name: gh
    type: github
    stages:
      - lint
      - test
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "ci-gh" in graph.services
    assert "/stage/0" in graph.services["ci-gh"].routes


def test_graph_data_sources_as_services() -> None:
    manifest = """
```yaml markpact:data_sources
data_sources:
  - name: weather
    source: json
    url: "https://api.weather.com"
    read_only: true
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "data-weather" in graph.services
    assert graph.services["data-weather"].routes["/url"]["url"] == "https://api.weather.com"


def test_graph_templates_as_services() -> None:
    manifest = """
```yaml markpact:templates
templates:
  - name: alert
    type: html
    engine: jinja2
    vars:
      - name
      - value
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "template-alert" in graph.services
    assert graph.services["template-alert"].routes["/engine"]["engine"] == "jinja2"


def test_graph_documents_as_services() -> None:
    manifest = """
```yaml markpact:documents
documents:
  - name: cert
    type: pdf
    template: alert
    output: "certs/{id}.pdf"
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "doc-cert" in graph.services
    assert graph.services["doc-cert"].routes["/output"]["output"] == "certs/{id}.pdf"


def test_graph_reports_as_services() -> None:
    manifest = """
```yaml markpact:reports
reports:
  - name: daily
    schedule: "0 6 * * *"
    output: pdf
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "report-daily" in graph.services
    assert graph.services["report-daily"].routes["/schedule"]["schedule"] == "0 6 * * *"


def test_graph_deploy_as_service() -> None:
    manifest = """
```yaml markpact:doql
deploy:
  target: docker-compose
  rootless: false
  containers:
    - name: api
      image: api:latest
```
""".strip()
    bridge = DoqlBridge()
    spec = bridge.from_text(manifest)
    graph = build_project_graph(spec)
    assert "deploy" in graph.services
    assert graph.services["deploy"].routes["/target"]["target"] == "docker-compose"
    assert "/container/0" in graph.services["deploy"].routes


def test_bridge_from_files_merge(tmp_path: Path) -> None:
    m1 = tmp_path / "entities.md"
    m1.write_text(
        '```yaml markpact:doql\napp_name: "MergedApp"\nentities:\n  - name: User\n    fields: []\n```',
        encoding="utf-8",
    )
    m2 = tmp_path / "workflows.md"
    m2.write_text(
        '```yaml markpact:workflows\nworkflows:\n  - name: signup\n    steps:\n      - action: email\n```',
        encoding="utf-8",
    )
    bridge = DoqlBridge()
    spec = bridge.from_files([m1, m2])
    assert spec.app_name == "MergedApp"
    assert len(spec.entities) == 1
    assert len(spec.workflows) == 1


def test_cli_generate_from_markpact(tmp_path: Path) -> None:
    from swop.cli import main

    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")

    out_yaml = tmp_path / "state.yaml"
    out_docker = tmp_path / "docker-compose.yaml"
    argv = [
        "generate",
        "--from-markpact", str(manifest),
        "--output-yaml", str(out_yaml),
        "--output-docker", str(out_docker),
    ]
    rc = main(argv)
    assert rc == 0
    assert out_yaml.exists()
    text = out_yaml.read_text(encoding="utf-8")
    assert "TestApp" in text or "User" in text
    assert out_docker.exists()
    docker_text = out_docker.read_text(encoding="utf-8")
    assert "version" in docker_text


def test_cli_generate_sync_files(tmp_path: Path) -> None:
    from swop.cli import main

    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")

    argv = [
        "generate",
        "--from-markpact", str(manifest),
        "--sync-files",
    ]
    rc = main(argv)
    assert rc == 0
    assert (tmp_path / "src" / "main.py").exists()
    content = (tmp_path / "src" / "main.py").read_text(encoding="utf-8")
    assert "print(\"hello\")" in content


def test_cli_generate_sync_files_dry_run(tmp_path: Path) -> None:
    from swop.cli import main

    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")

    argv = [
        "generate",
        "--from-markpact", str(manifest),
        "--sync-files-dry-run",
    ]
    rc = main(argv)
    assert rc == 0
    assert not (tmp_path / "src" / "main.py").exists()


def test_update_manifest_reverse_sync(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")

    engine = ManifestSyncEngine(base_dir=tmp_path)
    engine.sync_to_disk(manifest)

    # Modify the file on disk
    (tmp_path / "src" / "main.py").write_text('print("modified on disk")\n', encoding="utf-8")

    updated = engine.update_manifest(manifest)
    assert "src/main.py" in updated

    new_text = manifest.read_text(encoding="utf-8")
    assert 'print("modified on disk")' in new_text
    assert 'print("hello")' not in new_text


def test_update_manifest_dry_run(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")
    original = manifest.read_text(encoding="utf-8")

    engine = ManifestSyncEngine(base_dir=tmp_path)
    engine.sync_to_disk(manifest)
    (tmp_path / "src" / "main.py").write_text('print("modified")\n', encoding="utf-8")

    updated = engine.update_manifest(manifest, dry_run=True)
    assert "src/main.py" in updated
    # Manifest unchanged on disk
    assert manifest.read_text(encoding="utf-8") == original


def test_update_manifest_preserves_untracked_blocks(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")

    engine = ManifestSyncEngine(base_dir=tmp_path)
    engine.sync_to_disk(manifest)
    (tmp_path / "src" / "main.py").write_text('print("x")\n', encoding="utf-8")
    engine.update_manifest(manifest)

    new_text = manifest.read_text(encoding="utf-8")
    # DOQL block preserved unchanged
    assert 'app_name: "TestApp"' in new_text
    assert "markpact:doql" in new_text


def test_cli_generate_check_files_ok(tmp_path: Path) -> None:
    from swop.cli import main

    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")

    # Materialise first so files are in sync
    engine = ManifestSyncEngine(base_dir=tmp_path)
    engine.sync_to_disk(manifest)

    rc = main(["generate", "--from-markpact", str(manifest), "--check-files"])
    assert rc == 0


def test_cli_generate_check_files_strict_fails_on_drift(tmp_path: Path) -> None:
    from swop.cli import main

    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")

    # Don't sync — file is missing on disk → drift
    rc = main([
        "--mode", "STRICT",
        "generate", "--from-markpact", str(manifest), "--check-files",
    ])
    assert rc == 1


def test_cli_generate_from_disk(tmp_path: Path) -> None:
    from swop.cli import main

    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")

    # Sync then modify on disk
    engine = ManifestSyncEngine(base_dir=tmp_path)
    engine.sync_to_disk(manifest)
    (tmp_path / "src" / "main.py").write_text('print("cli modified")\n', encoding="utf-8")

    rc = main(["generate", "--from-markpact", str(manifest), "--from-disk"])
    assert rc == 0
    assert 'print("cli modified")' in manifest.read_text(encoding="utf-8")


def test_cli_generate_from_disk_dry_run(tmp_path: Path) -> None:
    from swop.cli import main

    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")
    original = manifest.read_text(encoding="utf-8")

    engine = ManifestSyncEngine(base_dir=tmp_path)
    engine.sync_to_disk(manifest)
    (tmp_path / "src" / "main.py").write_text('print("dry")\n', encoding="utf-8")

    rc = main(["generate", "--from-markpact", str(manifest), "--from-disk-dry-run"])
    assert rc == 0
    assert manifest.read_text(encoding="utf-8") == original
