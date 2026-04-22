"""
Tests for the refactor subpackage.

We build a tiny synthetic full-stack project inside ``tmp_path`` so the
tests remain hermetic and do not depend on any external repository.
"""

from pathlib import Path

import pytest

from swop.refactor import (
    BackendScanner,
    FrontendScanner,
    LouvainLike,
    RefactorGraph,
    RefactorPipeline,
    SeededClusterer,
)


# ----------------------------------------------------------------------
# Synthetic project scaffolding
# ----------------------------------------------------------------------


FRONTEND_PAGE_A = """
import { ConfigAPI } from '../modules/connect-config/connect-config.api';

export class NetworkPage {
  render(): string {
    return `
      <div id="network-content" class="section-content">
        <button id="network-save">save</button>
        <button id="network-test">test</button>
      </div>
    `;
  }

  save() {
    ConfigAPI.saveSection('network', {});
  }
}
""".strip()


FRONTEND_PAGE_B = """
import { ConfigAPI } from '../modules/connect-config/connect-config.api';

export class DevicesPage {
  render(): string {
    return `
      <div id="devices-content" class="section-content">
        <button id="devices-refresh">refresh</button>
      </div>
    `;
  }

  refresh() {
    ConfigAPI.getSection('devices');
  }
}
""".strip()


BACKEND_MODEL = """
from app.db import Base
from sqlalchemy import Column, String

class Device(Base):
    __tablename__ = 'devices'
    id = Column(String, primary_key=True)
    serial = Column(String)

class Network(Base):
    __tablename__ = 'networks'
    id = Column(String, primary_key=True)
    ip_address = Column(String)
""".strip()


@pytest.fixture
def synthetic_project(tmp_path: Path) -> Path:
    frontend_pages = tmp_path / "frontend" / "src" / "pages"
    frontend_pages.mkdir(parents=True)
    (frontend_pages / "connect-config-network.page.ts").write_text(FRONTEND_PAGE_A)
    (frontend_pages / "connect-test-devices-search.page.ts").write_text(FRONTEND_PAGE_B)

    backend_models = tmp_path / "backend" / "app" / "models"
    backend_models.mkdir(parents=True)
    (backend_models / "__init__.py").write_text("")
    (backend_models / "demo.py").write_text(BACKEND_MODEL)

    return tmp_path


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_frontend_scanner_extracts_ids_and_api_calls(synthetic_project):
    scanner = FrontendScanner(synthetic_project / "frontend")
    pages = scanner.scan()
    by_slug = {p.slug: p for p in pages}
    assert "connect-config-network" in by_slug

    network = by_slug["connect-config-network"]
    assert "network-save" in network.ids
    assert "network-test" in network.ids
    assert "ConfigAPI.saveSection" in network.api_calls


def test_backend_scanner_extracts_models(synthetic_project):
    scanner = BackendScanner(synthetic_project / "backend")
    signals = scanner.scan()
    names = {m.name for m in signals.models}
    assert {"Device", "Network"} <= names

    tablenames = {m.tablename for m in signals.models}
    assert {"devices", "networks"} <= tablenames


def test_frontend_find_pages_for_route(synthetic_project):
    scanner = FrontendScanner(synthetic_project / "frontend")
    matches = scanner.find_pages_for_route("/connect-config-network")
    assert len(matches) == 1
    assert matches[0].name == "connect-config-network.page.ts"


def test_refactor_pipeline_seeded_writes_modules(synthetic_project, tmp_path):
    out_dir = tmp_path / "modules"
    pipeline = RefactorPipeline(
        frontend=synthetic_project / "frontend",
        backend=synthetic_project / "backend",
        routes=["/connect-config-network", "/connect-test/devices"],
        out_dir=out_dir,
    )
    result = pipeline.run()

    assert len(result.modules) == 2
    names = {m.name for m in result.modules}
    assert "connect-config-network" in names
    assert "connect-test-devices" in names

    network_dir = out_dir / "connect-config-network"
    assert (network_dir / "module.yaml").is_file()
    assert (network_dir / "ui" / "connect-config-network.page.ts").is_file()
    assert (network_dir / "ui" / "selectors.yaml").is_file()
    assert (network_dir / "docker-compose.yml").is_file()

    # Top-level compose bundles both modules.
    top_compose = out_dir / "docker-compose.yml"
    assert top_compose.is_file()
    top_compose_text = top_compose.read_text()
    assert "connect-config-network" in top_compose_text
    assert "connect-test-devices" in top_compose_text


def test_louvain_like_groups_connected_nodes():
    graph = RefactorGraph()
    for nid in ("ui:a", "ui:b", "api:x", "model:m", "ui:isolated"):
        node_type = nid.split(":", 1)[0]
        graph.add_node(nid, node_type)
    graph.add_edge("ui:a", "api:x")
    graph.add_edge("ui:b", "api:x")
    graph.add_edge("api:x", "model:m")

    clusters = LouvainLike(graph).run()
    # The connected component must live in a single cluster.
    by_node = {node: cluster.id for cluster in clusters for node in cluster.nodes}
    assert by_node["ui:a"] == by_node["api:x"] == by_node["model:m"]
    assert by_node["ui:isolated"] != by_node["ui:a"]


def test_seeded_clusterer_assigns_by_best_score():
    graph = RefactorGraph()
    for nid in ("ui:alpha", "ui:beta", "api:shared", "model:alpha_model"):
        graph.add_node(nid, nid.split(":", 1)[0])
    graph.add_edge("ui:alpha", "api:shared", weight=2.0)
    graph.add_edge("ui:beta", "api:shared", weight=1.0)
    graph.add_edge("ui:alpha", "model:alpha_model", weight=3.0)

    clusters = SeededClusterer(graph).run(
        [("alpha", "ui:alpha"), ("beta", "ui:beta")]
    )
    by_name = {c.id: set(c.nodes) for c in clusters}
    assert "ui:alpha" in by_name["alpha"]
    assert "model:alpha_model" in by_name["alpha"]
    assert "ui:beta" in by_name["beta"]
