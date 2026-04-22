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


def test_bridge_missing_doql_raises() -> None:
    bridge = DoqlBridge()
    with pytest.raises(Exception):
        bridge.from_text("# no doql blocks")


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


def test_cli_generate_from_markpact(tmp_path: Path) -> None:
    from swop.cli import main

    manifest = tmp_path / "manifest.md"
    manifest.write_text(SIMPLE_MANIFEST, encoding="utf-8")

    out_yaml = tmp_path / "state.yaml"
    argv = [
        "generate",
        "--from-markpact", str(manifest),
        "--output-yaml", str(out_yaml),
    ]
    rc = main(argv)
    assert rc == 0
    assert out_yaml.exists()
    text = out_yaml.read_text(encoding="utf-8")
    assert "TestApp" in text or "User" in text
