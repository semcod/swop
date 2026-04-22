"""
Swop runtime.

Wires the graph, introspection, sync, reconciliation, versioning and
export layers into a single runtime object that can be driven from code
or from the CLI.
"""

from typing import Dict, Iterable, Optional

from swop.export.docker import DockerExporter
from swop.export.yaml import StateExporter
from swop.graph import DataModel, ModelField, ProjectGraph, Service, UIBinding
from swop.introspect.backend import BackendIntrospector
from swop.introspect.frontend import FrontendIntrospector
from swop.reconcile import Drift, ResyncEngine, SyncMode
from swop.sync import SyncEngine
from swop.versioning import Versioning


class SwopRuntime:
    """Main orchestrator for the swop reconciliation system."""

    def __init__(
        self,
        mode: SyncMode = "SOFT",
        backend: Optional[BackendIntrospector] = None,
        frontend: Optional[FrontendIntrospector] = None,
    ) -> None:
        self.graph = ProjectGraph()
        self.backend = backend or BackendIntrospector()
        self.frontend = frontend or FrontendIntrospector()
        self.sync_engine = SyncEngine()
        self.resync = ResyncEngine(mode=mode)
        self.versioning = Versioning()
        self.state_exporter = StateExporter()
        self.docker_exporter = DockerExporter()
        self._last_drift: Optional[Drift] = None

    # ------------------------------------------------------------------
    # DSL ingestion
    # ------------------------------------------------------------------

    def add_model(self, name: str, fields: Iterable[str], field_type: str = "float") -> None:
        self.graph.models[name] = DataModel(
            name=name,
            fields={f: ModelField(f, field_type) for f in fields},
        )
        self.versioning.commit(self.graph, f"add_model:{name}")

    def add_service(self, name: str, routes: Iterable[str]) -> None:
        self.graph.services[name] = Service(
            name=name,
            routes={route: {} for route in routes},
        )
        self.versioning.commit(self.graph, f"add_service:{name}")

    def add_ui_binding(self, selector: str, model_field: str) -> None:
        self.graph.ui_bindings.append(UIBinding(selector, model_field))
        self.versioning.commit(self.graph, f"bind:{selector}->{model_field}")

    # ------------------------------------------------------------------
    # Sync loop
    # ------------------------------------------------------------------

    def introspect(self) -> Dict:
        """Return a merged snapshot of actual backend + frontend state."""
        backend_state = self.backend.introspect()
        frontend_state = self.frontend.introspect()
        return {
            "models": backend_state.get("models", {}),
            "routes": backend_state.get("routes", []),
            "bindings": frontend_state.get("bindings", []),
            "events": frontend_state.get("events", []),
        }

    def run_sync(self) -> Drift:
        """Run one reconciliation pass and return the drift report."""
        actual = self.introspect()

        self.sync_engine.merge_backend(self.graph, actual)
        self.sync_engine.merge_frontend(self.graph, actual.get("bindings", []))

        drift = self.resync.reconcile(self.graph, actual)
        self._last_drift = drift

        print("\n[YAML STATE]")
        print(self.state_exporter.export_yaml(self.graph, drift))

        return drift

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    def state_yaml(self) -> str:
        drift = self._last_drift or Drift()
        return self.state_exporter.export_yaml(self.graph, drift)

    def docker_compose(self) -> str:
        return self.docker_exporter.export_yaml(self.graph)


# Backwards-compatible alias used in README examples.
SynqerRuntime = SwopRuntime
