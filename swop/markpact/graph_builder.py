"""ProjectGraph builder from DOQL spec.

Converts a ``DoqlSpec`` (or the minimal fallback) into a swop
:class:`~swop.graph.ProjectGraph` with models, services, and UI bindings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from swop.graph import DataModel, ModelField, ProjectGraph, Service, UIBinding


def build_project_graph(spec: Any) -> ProjectGraph:
    """Build a swop ``ProjectGraph`` from a DOQL-style specification object."""
    graph = ProjectGraph()

    _build_models(graph, spec)
    _build_services(graph, spec)
    _build_ui_bindings(graph, spec)
    _build_databases(graph, spec)

    return graph


def _build_models(graph: ProjectGraph, spec: Any) -> None:
    entities = getattr(spec, "entities", None)
    if not entities:
        return

    for entity in entities:
        name = getattr(entity, "name", None)
        if not name:
            continue

        fields: Dict[str, ModelField] = {}
        entity_fields = getattr(entity, "fields", None)
        if entity_fields:
            for f in entity_fields:
                f_name = getattr(f, "name", None)
                f_type = getattr(f, "type", "string")
                if f_name:
                    fields[f_name] = ModelField(name=f_name, type=f_type)

        graph.models[name] = DataModel(name=name, fields=fields)


def _build_services(graph: ProjectGraph, spec: Any) -> None:
    interfaces = getattr(spec, "interfaces", None)
    if not interfaces:
        return

    api_clients = getattr(spec, "api_clients", None) or []

    for interface in interfaces:
        name = getattr(interface, "name", None)
        if not name:
            continue

        itype = getattr(interface, "type", "spa")
        pages = getattr(interface, "pages", None) or []
        routes: Dict[str, Any] = {}

        for page in pages:
            if isinstance(page, dict):
                page_name = page.get("name", "")
                page_path = page.get("path", "")
                if page_path:
                    routes[page_path] = {"page": page_name, "public": page.get("public", False)}
                elif page_name:
                    routes[f"/{page_name.lower().replace(' ', '-')}"] = {"page": page_name}

        for client in api_clients:
            if hasattr(client, "name") and hasattr(client, "base_url"):
                routes[f"/api/{client.name}"] = {"base_url": client.base_url}

        graph.services[name] = Service(name=name, routes=routes)


def _build_ui_bindings(graph: ProjectGraph, spec: Any) -> None:
    interfaces = getattr(spec, "interfaces", None)
    if not interfaces:
        return

    for interface in interfaces:
        pages = getattr(interface, "pages", None) or []
        for page in pages:
            if not isinstance(page, dict):
                continue
            page_name = page.get("name", "")
            page_path = page.get("path", "")
            if page_name:
                selector = f"#{page_name.lower().replace(' ', '-')}-page"
                graph.ui_bindings.append(
                    UIBinding(selector=selector, model_field=page_name)
                )
            if page_path:
                selector = f"[data-route='{page_path}']"
                if not any(b.selector == selector for b in graph.ui_bindings):
                    graph.ui_bindings.append(
                        UIBinding(selector=selector, model_field=page_name or page_path)
                    )


def _build_databases(graph: ProjectGraph, spec: Any) -> None:
    databases = getattr(spec, "databases", None)
    if not databases:
        return

    for db in databases:
        name = getattr(db, "name", None)
        if not name:
            continue

        db_type = getattr(db, "type", "sqlite")
        file_path = getattr(db, "file", None)
        url = getattr(db, "url", None)

        service_name = f"db-{name}"
        routes: Dict[str, Any] = {
            "/health": {"check": "db"},
        }
        if file_path:
            routes["/schema"] = {"file": file_path}
        if url:
            routes["/connect"] = {"url": url}

        graph.services[service_name] = Service(name=service_name, routes=routes)
