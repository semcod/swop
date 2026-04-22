"""
Backend introspection.

Extracts models and routes from a running backend or a static description.
In future iterations this can plug into FastAPI, OpenAPI, GraphQL SDL, or a
database schema dump. For now it exposes a simple stub compatible with the
reconciliation engine.
"""

from typing import Dict, List


class BackendIntrospector:
    """Introspect backend services to produce a runtime state dict."""

    def __init__(self, models: Dict[str, List[str]] = None, routes: List[str] = None):
        self._models = models or {}
        self._routes = routes or []

    def introspect(self) -> Dict:
        """Return the actual backend state as a plain dict."""
        return {
            "models": dict(self._models),
            "routes": list(self._routes),
        }

    def register_model(self, name: str, fields: List[str]) -> None:
        self._models[name] = list(fields)

    def register_route(self, route: str) -> None:
        if route not in self._routes:
            self._routes.append(route)
