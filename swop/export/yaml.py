"""
YAML state exporter.

Produces a human-readable snapshot of the current project graph plus the
latest drift report. The snapshot is deliberately flat so that it can be
diffed between runs and committed to version control.
"""

from dataclasses import asdict
from typing import Any, Dict

import yaml

from swop.graph import ProjectGraph
from swop.reconcile import Drift


class StateExporter:
    """Serialize a ``ProjectGraph`` plus a ``Drift`` to YAML."""

    def to_dict(self, graph: ProjectGraph, drift: Drift) -> Dict[str, Any]:
        return {
            "graph_version": graph.version,
            "models": {
                name: list(model.fields.keys())
                for name, model in graph.models.items()
            },
            "services": {
                name: sorted(service.routes.keys())
                for name, service in graph.services.items()
            },
            "ui_bindings": [
                {"selector": b.selector, "model_field": b.model_field}
                for b in graph.ui_bindings
            ],
            "drift": asdict(drift),
            "history": [
                {
                    "version": v.version,
                    "timestamp": v.timestamp,
                    "changes": list(v.changes),
                }
                for v in graph.history
            ],
        }

    def export_yaml(self, graph: ProjectGraph, drift: Drift) -> str:
        return yaml.dump(self.to_dict(graph, drift), sort_keys=False)
