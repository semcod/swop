"""
Bi-directional sync engine.

Projects frontend and backend introspection results onto the project graph
and vice versa. The engine is intentionally minimal and leaves domain-
specific rules to the caller; its job is to move data between the graph
and the introspected world.
"""

from typing import Dict, Iterable, List

from swop.graph import DataModel, ModelField, ProjectGraph, Service, UIBinding


class SyncEngine:
    """Move state between a ``ProjectGraph`` and introspected snapshots."""

    # --- frontend -> graph ---------------------------------------------

    def frontend_to_graph(self, selectors: Iterable[str]) -> List[UIBinding]:
        """Produce placeholder bindings from raw DOM selectors."""
        return [UIBinding(selector=s, model_field="unknown") for s in selectors]

    def merge_frontend(self, graph: ProjectGraph, selectors: Iterable[str]) -> None:
        """Add any missing selectors as unresolved bindings in the graph."""
        known = {b.selector for b in graph.ui_bindings}
        for binding in self.frontend_to_graph(selectors):
            if binding.selector not in known:
                graph.ui_bindings.append(binding)

    # --- backend -> graph ----------------------------------------------

    def merge_backend(self, graph: ProjectGraph, backend_state: Dict) -> None:
        """Merge backend models and routes into the graph."""
        for name, fields in backend_state.get("models", {}).items():
            if name not in graph.models:
                graph.models[name] = DataModel(
                    name=name,
                    fields={f: ModelField(f, "unknown") for f in fields},
                )

        routes = backend_state.get("routes", [])
        if routes:
            service = graph.services.get("api") or Service(name="api", routes={})
            for route in routes:
                service.routes.setdefault(route, {})
            graph.services["api"] = service
