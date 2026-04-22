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
    _build_workflows(graph, spec)
    _build_roles(graph, spec)
    _build_integrations(graph, spec)
    _build_webhooks(graph, spec)
    _build_api_clients(graph, spec)
    _build_environments(graph, spec)
    _build_infrastructures(graph, spec)
    _build_ingresses(graph, spec)
    _build_ci_configs(graph, spec)
    _build_data_sources(graph, spec)
    _build_templates(graph, spec)
    _build_documents(graph, spec)
    _build_reports(graph, spec)
    _build_deploy(graph, spec)

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


def _build_workflows(graph: ProjectGraph, spec: Any) -> None:
    workflows = getattr(spec, "workflows", None)
    if not workflows:
        return

    for wf in workflows:
        name = getattr(wf, "name", None)
        if not name:
            continue

        trigger = getattr(wf, "trigger", None)
        schedule = getattr(wf, "schedule", None)
        condition = getattr(wf, "condition", None)
        steps = getattr(wf, "steps", None) or []

        service_name = f"workflow-{name}"
        routes: Dict[str, Any] = {}
        if trigger:
            routes[f"/trigger/{trigger}"] = {"trigger": trigger}
        if schedule:
            routes["/schedule"] = {"cron": schedule}
        if condition:
            routes["/condition"] = {"condition": condition}
        for idx, step in enumerate(steps):
            action = getattr(step, "action", "")
            target = getattr(step, "target", None)
            params = getattr(step, "params", {})
            routes[f"/step/{idx}"] = {"action": action, "target": target, "params": params}

        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_roles(graph: ProjectGraph, spec: Any) -> None:
    roles = getattr(spec, "roles", None)
    if not roles:
        return

    for role in roles:
        name = getattr(role, "name", None)
        if not name:
            continue

        perms = getattr(role, "permissions", None) or []
        service_name = f"role-{name}"
        routes: Dict[str, Any] = {f"/perm/{p}": {"allowed": True} for p in perms}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_integrations(graph: ProjectGraph, spec: Any) -> None:
    integrations = getattr(spec, "integrations", None)
    if not integrations:
        return

    for ing in integrations:
        name = getattr(ing, "name", None)
        if not name:
            continue

        itype = getattr(ing, "type", "email")
        config = getattr(ing, "config", {})
        service_name = f"integration-{name}"
        routes = {
            "/type": {"type": itype},
            "/config": config,
        }
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_webhooks(graph: ProjectGraph, spec: Any) -> None:
    webhooks = getattr(spec, "webhooks", None)
    if not webhooks:
        return

    for wh in webhooks:
        name = getattr(wh, "name", None)
        if not name:
            continue

        source = getattr(wh, "source", None)
        event = getattr(wh, "event", None)
        auth = getattr(wh, "auth", None)
        service_name = f"webhook-{name}"
        routes: Dict[str, Any] = {}
        if source:
            routes["/source"] = {"source": source}
        if event:
            routes["/event"] = {"event": event}
        if auth:
            routes["/auth"] = {"auth": auth}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_api_clients(graph: ProjectGraph, spec: Any) -> None:
    clients = getattr(spec, "api_clients", None)
    if not clients:
        return

    for client in clients:
        name = getattr(client, "name", None)
        if not name:
            continue

        base_url = getattr(client, "base_url", None)
        openapi = getattr(client, "openapi", None)
        methods = getattr(client, "methods", None) or []
        service_name = f"api-{name}"
        routes: Dict[str, Any] = {}
        if base_url:
            routes["/base_url"] = {"url": base_url}
        if openapi:
            routes["/openapi"] = {"spec": openapi}
        for m in methods:
            routes[f"/method/{m}"] = {"method": m}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_environments(graph: ProjectGraph, spec: Any) -> None:
    envs = getattr(spec, "environments", None)
    if not envs:
        return

    for env in envs:
        name = getattr(env, "name", None)
        if not name:
            continue

        runtime = getattr(env, "runtime", "docker-compose")
        ssh_host = getattr(env, "ssh_host", None)
        env_file = getattr(env, "env_file", None)
        replicas = getattr(env, "replicas", 1)
        config = getattr(env, "config", {})

        service_name = f"env-{name}"
        routes: Dict[str, Any] = {
            "/runtime": {"runtime": runtime},
            "/replicas": {"replicas": replicas},
            "/config": config,
        }
        if ssh_host:
            routes["/ssh"] = {"host": ssh_host}
        if env_file:
            routes["/env_file"] = {"file": env_file}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_infrastructures(graph: ProjectGraph, spec: Any) -> None:
    infra_list = getattr(spec, "infrastructures", None)
    if not infra_list:
        return

    for infra in infra_list:
        name = getattr(infra, "name", None)
        if not name:
            continue

        itype = getattr(infra, "type", "docker-compose")
        provider = getattr(infra, "provider", None)
        namespace = getattr(infra, "namespace", None)
        replicas = getattr(infra, "replicas", 1)
        config = getattr(infra, "config", {})

        service_name = f"infra-{name}"
        routes: Dict[str, Any] = {
            "/type": {"type": itype},
            "/replicas": {"replicas": replicas},
            "/config": config,
        }
        if provider:
            routes["/provider"] = {"provider": provider}
        if namespace:
            routes["/namespace"] = {"namespace": namespace}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_ingresses(graph: ProjectGraph, spec: Any) -> None:
    ingresses = getattr(spec, "ingresses", None)
    if not ingresses:
        return

    for ing in ingresses:
        name = getattr(ing, "name", None)
        if not name:
            continue

        itype = getattr(ing, "type", "traefik")
        tls = getattr(ing, "tls", False)
        cert_manager = getattr(ing, "cert_manager", None)
        rate_limit = getattr(ing, "rate_limit", None)
        config = getattr(ing, "config", {})

        service_name = f"ingress-{name}"
        routes: Dict[str, Any] = {
            "/type": {"type": itype},
            "/tls": {"enabled": tls},
            "/config": config,
        }
        if cert_manager:
            routes["/cert_manager"] = {"cert_manager": cert_manager}
        if rate_limit:
            routes["/rate_limit"] = {"rate_limit": rate_limit}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_ci_configs(graph: ProjectGraph, spec: Any) -> None:
    ci_configs = getattr(spec, "ci_configs", None)
    if not ci_configs:
        return

    for ci in ci_configs:
        name = getattr(ci, "name", None)
        if not name:
            continue

        ctype = getattr(ci, "type", "github")
        runner = getattr(ci, "runner", None)
        stages = getattr(ci, "stages", None) or []
        config = getattr(ci, "config", {})

        service_name = f"ci-{name}"
        routes: Dict[str, Any] = {
            "/type": {"type": ctype},
            "/config": config,
        }
        if runner:
            routes["/runner"] = {"runner": runner}
        for idx, stage in enumerate(stages):
            routes[f"/stage/{idx}"] = {"stage": stage}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_data_sources(graph: ProjectGraph, spec: Any) -> None:
    sources = getattr(spec, "data_sources", None)
    if not sources:
        return

    for ds in sources:
        name = getattr(ds, "name", None)
        if not name:
            continue

        source_type = getattr(ds, "source", "json")
        file_path = getattr(ds, "file", None)
        url = getattr(ds, "url", None)
        schema = getattr(ds, "schema", None)
        auth = getattr(ds, "auth", None)
        token = getattr(ds, "token", None)
        cache = getattr(ds, "cache", None)
        read_only = getattr(ds, "read_only", False)
        env_overrides = getattr(ds, "env_overrides", False)

        service_name = f"data-{name}"
        routes: Dict[str, Any] = {
            "/source": {"type": source_type},
            "/read_only": {"read_only": read_only},
            "/env_overrides": {"env_overrides": env_overrides},
        }
        if file_path:
            routes["/file"] = {"file": file_path}
        if url:
            routes["/url"] = {"url": url}
        if schema:
            routes["/schema"] = {"schema": schema}
        if auth:
            routes["/auth"] = {"auth": auth}
        if token:
            routes["/token"] = {"token": token}
        if cache:
            routes["/cache"] = {"cache": cache}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_templates(graph: ProjectGraph, spec: Any) -> None:
    templates = getattr(spec, "templates", None)
    if not templates:
        return

    for t in templates:
        name = getattr(t, "name", None)
        if not name:
            continue

        ttype = getattr(t, "type", "html")
        engine = getattr(t, "engine", "jinja2")
        file_path = getattr(t, "file", None)
        content = getattr(t, "content", None)
        vars_list = getattr(t, "vars", None) or []

        service_name = f"template-{name}"
        routes: Dict[str, Any] = {
            "/type": {"type": ttype},
            "/engine": {"engine": engine},
            "/vars": {"vars": vars_list},
        }
        if file_path:
            routes["/file"] = {"file": file_path}
        if content:
            routes["/content"] = {"content": content}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_documents(graph: ProjectGraph, spec: Any) -> None:
    documents = getattr(spec, "documents", None)
    if not documents:
        return

    for doc in documents:
        name = getattr(doc, "name", None)
        if not name:
            continue

        dtype = getattr(doc, "type", "pdf")
        template = getattr(doc, "template", None)
        output = getattr(doc, "output", None)
        data = getattr(doc, "data", {})
        styling = getattr(doc, "styling", {})
        metadata = getattr(doc, "metadata", {})
        partials = getattr(doc, "partials", None) or []

        service_name = f"doc-{name}"
        routes: Dict[str, Any] = {
            "/type": {"type": dtype},
            "/data": data,
            "/styling": styling,
            "/metadata": metadata,
            "/partials": {"partials": partials},
        }
        if template:
            routes["/template"] = {"template": template}
        if output:
            routes["/output"] = {"output": output}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_reports(graph: ProjectGraph, spec: Any) -> None:
    reports = getattr(spec, "reports", None)
    if not reports:
        return

    for rep in reports:
        name = getattr(rep, "name", None)
        if not name:
            continue

        schedule = getattr(rep, "schedule", None)
        template = getattr(rep, "template", None)
        output = getattr(rep, "output", "pdf")
        query = getattr(rep, "query", {})
        recipients = getattr(rep, "recipients", {})
        retention = getattr(rep, "retention", None)

        service_name = f"report-{name}"
        routes: Dict[str, Any] = {
            "/output": {"output": output},
            "/query": query,
            "/recipients": recipients,
        }
        if schedule:
            routes["/schedule"] = {"schedule": schedule}
        if template:
            routes["/template"] = {"template": template}
        if retention:
            routes["/retention"] = {"retention": retention}
        graph.services[service_name] = Service(name=service_name, routes=routes)


def _build_deploy(graph: ProjectGraph, spec: Any) -> None:
    deploy = getattr(spec, "deploy", None)
    if not deploy:
        return

    target = getattr(deploy, "target", "docker-compose")
    rootless = getattr(deploy, "rootless", False)
    containers = getattr(deploy, "containers", None) or []
    config = getattr(deploy, "config", {})
    directives = getattr(deploy, "directives", {})

    service_name = "deploy"
    routes: Dict[str, Any] = {
        "/target": {"target": target},
        "/rootless": {"rootless": rootless},
        "/config": config,
        "/directives": directives,
    }
    for idx, c in enumerate(containers):
        routes[f"/container/{idx}"] = c if isinstance(c, dict) else {"container": c}

    graph.services[service_name] = Service(name=service_name, routes=routes)
