"""
Reconciliation engine.

Computes drift between a declared ``ProjectGraph`` and an actual runtime
state snapshot, and applies configurable healing strategies:

- ``STRICT`` - raise on any critical drift.
- ``SOFT`` - log drift and suggest fixes.
- ``OBSERVE`` - log drift only.
- ``AUTO_HEAL`` - remove invalid bindings automatically.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from swop.graph import ProjectGraph


SyncMode = str  # "STRICT" | "SOFT" | "OBSERVE" | "AUTO_HEAL"


class DriftError(Exception):
    """Raised when drift is detected while running in STRICT mode."""


@dataclass
class Drift:
    missing_bindings: List[str] = field(default_factory=list)
    invalid_bindings: List[str] = field(default_factory=list)
    extra_routes: List[str] = field(default_factory=list)
    missing_routes: List[str] = field(default_factory=list)

    def exists(self) -> bool:
        return bool(
            self.missing_bindings
            or self.invalid_bindings
            or self.extra_routes
            or self.missing_routes
        )


class DriftDetector:
    """Compare a declared graph with the actual runtime state."""

    def compute(self, graph: ProjectGraph, actual: Dict) -> Drift:
        drift = Drift()

        model_fields = {
            f_name
            for model in graph.models.values()
            for f_name in model.fields
        }

        for binding in graph.ui_bindings:
            if binding.model_field not in model_fields:
                drift.invalid_bindings.append(binding.selector)

        declared_routes = {
            route
            for service in graph.services.values()
            for route in service.routes
        }
        actual_routes = set(actual.get("routes", []))

        drift.extra_routes = sorted(actual_routes - declared_routes)
        drift.missing_routes = sorted(declared_routes - actual_routes)

        return drift


class ResyncEngine:
    """Continuously reconcile the declared graph against actual state."""

    def __init__(self, mode: SyncMode = "SOFT"):
        self.mode = mode
        self.detector = DriftDetector()

    def reconcile(self, graph: ProjectGraph, actual: Dict) -> Drift:
        drift = self.detector.compute(graph, actual)
        self._log_drift(drift)

        if self.mode == "STRICT" and self._has_critical(drift):
            raise DriftError("DRIFT detected in STRICT mode")

        if self.mode == "AUTO_HEAL":
            self._auto_heal(graph, drift)

        return drift

    @staticmethod
    def _has_critical(drift: Drift) -> bool:
        return bool(drift.invalid_bindings or drift.missing_routes)

    @staticmethod
    def _auto_heal(graph: ProjectGraph, drift: Drift) -> None:
        for selector in drift.invalid_bindings:
            print(f"[AUTO-HEAL] removing invalid binding: {selector}")

        invalid = set(drift.invalid_bindings)
        graph.ui_bindings = [
            b for b in graph.ui_bindings if b.selector not in invalid
        ]

    @staticmethod
    def _log_drift(drift: Drift) -> None:
        print("\n[DRIFT REPORT]")
        print(f"invalid_bindings: {drift.invalid_bindings}")
        print(f"missing_bindings: {drift.missing_bindings}")
        print(f"extra_routes:     {drift.extra_routes}")
        print(f"missing_routes:   {drift.missing_routes}")
        print("-" * 40)
