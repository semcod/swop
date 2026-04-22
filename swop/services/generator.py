"""
Per-context service skeleton generator.

Renders a minimal, runnable Python package per bounded context plus a
single ``docker-compose.cqrs.yml`` that brings up the chosen bus and
all context services together.

The generated code is intentionally small and boring: it imports the
user's handlers, exposes a gRPC server for commands + queries, and
provides a pluggable ``BusPublisher`` for emitting events. The idea is
that the user will refine the TODO blocks without having to rewrite the
scaffolding.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml


SUPPORTED_BUSES = {"rabbitmq", "redis", "memory", "kafka"}

DEFAULT_BASE_IMAGE = "python:3.12-slim"
DEFAULT_GRPC_PORT = 50051


# ----------------------------------------------------------------------
# Result objects
# ----------------------------------------------------------------------


@dataclass
class ServiceFile:
    path: Path
    kind: str  # "worker" | "server" | "publisher" | "dockerfile" | ...
    context: Optional[str] = None


@dataclass
class ServiceGenerationResult:
    files: List[ServiceFile] = field(default_factory=list)
    out_dir: Optional[Path] = None
    bus: str = "memory"
    compose_path: Optional[Path] = None

    def format(self) -> str:
        if not self.files:
            return "[SERVICES] no service files written"
        lines = [
            f"[SERVICES] wrote {len(self.files)} file(s) (bus: {self.bus})"
        ]
        by_ctx: Dict[str, List[ServiceFile]] = {}
        for f in self.files:
            by_ctx.setdefault(f.context or "_root", []).append(f)
        for ctx, items in sorted(by_ctx.items()):
            if ctx == "_root":
                for item in items:
                    lines.append(f"  -> {item.path}")
            else:
                lines.append(f"  context: {ctx}")
                for item in items:
                    lines.append(f"    -> {item.path}")
        if self.compose_path:
            lines.append(f"  compose: {self.compose_path}")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------


def generate_services(
    manifests_dir: Path,
    out_dir: Path,
    *,
    bus: str = "rabbitmq",
    base_image: str = DEFAULT_BASE_IMAGE,
    grpc_port: int = DEFAULT_GRPC_PORT,
    proto_python_dir: Optional[Path] = None,
) -> ServiceGenerationResult:
    """Generate one service package per context + a docker-compose file."""

    bus_key = bus.lower().strip()
    if bus_key not in SUPPORTED_BUSES:
        raise ValueError(
            f"unsupported bus {bus!r}; choose one of {sorted(SUPPORTED_BUSES)}"
        )

    manifests_dir = Path(manifests_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = ServiceGenerationResult(out_dir=out_dir, bus=bus_key)

    contexts: List[str] = []
    for entry in sorted(manifests_dir.iterdir() if manifests_dir.exists() else []):
        if not entry.is_dir():
            continue
        cmd = _load_yaml(entry / "commands.yml")
        qry = _load_yaml(entry / "queries.yml")
        evt = _load_yaml(entry / "events.yml")
        commands = cmd.get("commands", []) if cmd else []
        queries = qry.get("queries", []) if qry else []
        events = evt.get("events", []) if evt else []
        if not (commands or queries or events):
            continue
        contexts.append(entry.name)

        ctx_dir = out_dir / entry.name
        ctx_dir.mkdir(parents=True, exist_ok=True)
        port = grpc_port + len(contexts) - 1
        _write_context_package(
            ctx_dir=ctx_dir,
            context=entry.name,
            commands=commands,
            queries=queries,
            events=events,
            bus=bus_key,
            base_image=base_image,
            grpc_port=port,
            proto_python_dir=proto_python_dir,
            result=result,
        )

    compose_path = out_dir / "docker-compose.cqrs.yml"
    compose_path.write_text(
        _render_compose(contexts, bus_key, grpc_port=grpc_port),
        encoding="utf-8",
    )
    result.files.append(ServiceFile(path=compose_path, kind="compose", context=None))
    result.compose_path = compose_path

    # Top-level README helping the user understand the artefact.
    readme_path = out_dir / "README.md"
    readme_path.write_text(_render_readme(contexts, bus_key), encoding="utf-8")
    result.files.append(ServiceFile(path=readme_path, kind="readme", context=None))

    return result


# ----------------------------------------------------------------------
# Per-context package
# ----------------------------------------------------------------------


def _write_context_package(
    *,
    ctx_dir: Path,
    context: str,
    commands: List[Dict[str, Any]],
    queries: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    bus: str,
    base_image: str,
    grpc_port: int,
    proto_python_dir: Optional[Path],
    result: ServiceGenerationResult,
) -> None:
    pkg = _safe_ident(context)
    service_class = _camel(context)

    # Optionally copy pb2 / pb2_grpc stubs into the service package so it
    # is fully self-contained.
    pb_module = None
    pb_grpc_module = None
    if proto_python_dir and proto_python_dir.exists():
        ctx_proto = proto_python_dir / context / "v1"
        for suffix, kind in (("_pb2.py", "pb2"), ("_pb2_grpc.py", "pb2_grpc")):
            source = next(ctx_proto.glob(f"*{suffix}"), None)
            if source is not None:
                target = ctx_dir / source.name
                shutil.copy2(source, target)
                result.files.append(
                    ServiceFile(path=target, kind=f"proto-{kind}", context=context)
                )
                if kind == "pb2":
                    pb_module = source.stem
                else:
                    pb_grpc_module = source.stem

    files = {
        "__init__.py": _render_init(context),
        "worker.py": _render_worker(
            context=context,
            service_class=service_class,
            pb_grpc_module=pb_grpc_module,
            grpc_port=grpc_port,
        ),
        "server.py": _render_server(
            context=context,
            service_class=service_class,
            commands=commands,
            queries=queries,
            pb_module=pb_module,
            pb_grpc_module=pb_grpc_module,
        ),
        "publisher.py": _render_publisher(bus),
        "requirements.txt": _render_requirements(bus),
        "Dockerfile": _render_dockerfile(base_image, pkg=pkg),
        ".env.example": _render_env(bus=bus, context=context, grpc_port=grpc_port),
    }
    for name, body in files.items():
        path = ctx_dir / name
        path.write_text(body, encoding="utf-8")
        result.files.append(
            ServiceFile(path=path, kind=_classify_file(name), context=context)
        )


def _classify_file(name: str) -> str:
    if name == "Dockerfile":
        return "dockerfile"
    if name == "requirements.txt":
        return "requirements"
    if name == ".env.example":
        return "env"
    if name.endswith(".py"):
        return name[:-3]
    return name


# ----------------------------------------------------------------------
# Templates
# ----------------------------------------------------------------------


def _render_init(context: str) -> str:
    return (
        f'"""Auto-generated service package for the `{context}` bounded context."""\n'
    )


def _render_worker(
    *,
    context: str,
    service_class: str,
    pb_grpc_module: Optional[str],
    grpc_port: int,
) -> str:
    import_line = (
        f"from . import {pb_grpc_module} as pb_grpc"
        if pb_grpc_module
        else "# from . import <your_pb2_grpc> as pb_grpc  # run `swop gen grpc-python` first"
    )
    return f'''"""
Auto-generated worker for the `{context}` bounded context.
Do not edit by hand; re-run `swop gen services`.
"""

from __future__ import annotations

import logging
import os
import signal
import sys
from concurrent import futures

import grpc

{import_line}
from .publisher import BusPublisher
from .server import {service_class}CommandServicer, {service_class}QueryServicer


def main() -> int:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    log = logging.getLogger("{context}.worker")

    bus = BusPublisher.from_env()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    cmd_servicer = {service_class}CommandServicer(bus=bus)
    qry_servicer = {service_class}QueryServicer()
    try:
        pb_grpc.add_{service_class}CommandServiceServicer_to_server(cmd_servicer, server)
        pb_grpc.add_{service_class}QueryServiceServicer_to_server(qry_servicer, server)
    except NameError:
        log.error("gRPC stubs not found – run `swop gen grpc-python` first.")
        return 2

    port = int(os.environ.get("GRPC_PORT", "{grpc_port}"))
    server.add_insecure_port(f"[::]:{{port}}")
    server.start()
    log.info("{context} gRPC server listening on :%s", port)

    def _stop(*_):
        log.info("{context} shutting down…")
        server.stop(grace=5)

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    server.wait_for_termination()
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _render_server(
    *,
    context: str,
    service_class: str,
    commands: List[Dict[str, Any]],
    queries: List[Dict[str, Any]],
    pb_module: Optional[str],
    pb_grpc_module: Optional[str],
) -> str:
    if pb_module and pb_grpc_module:
        pb_import = f"from . import {pb_module} as pb"
        pb_grpc_import = f"from . import {pb_grpc_module} as pb_grpc"
        cmd_base = f"pb_grpc.{service_class}CommandServiceServicer"
        qry_base = f"pb_grpc.{service_class}QueryServiceServicer"
    else:
        pb_import = "# from . import <your_pb2> as pb          # run `swop gen grpc-python` first"
        pb_grpc_import = "# from . import <your_pb2_grpc> as pb_grpc"
        cmd_base = "object"
        qry_base = "object"

    def _cmd_method(cmd: Dict[str, Any]) -> str:
        name = cmd.get("name", "")
        emits = cmd.get("emits", [])
        emits_line = ", ".join(repr(e) for e in emits) or ""
        body_emits = (
            f"        # TODO: publish real events to the bus.\n"
            f"        self.bus.publish(\n"
            f"            topic=\"{context}.events\",\n"
            f"            payload={{'type': 'stub', 'command': '{name}'}},\n"
            f"        )\n"
            if emits
            else ""
        )
        return (
            f"    def {name}(self, request, context):  # noqa: N802 (gRPC casing)\n"
            f"        # TODO: wire up the {name}Handler for the `{context}` context.\n"
            f"        # emits={[*emits]}\n"
            f"{body_emits}"
            f"        return pb.{name}Response(id=\"\", emitted_events=[{emits_line}])\n"
        )

    def _qry_method(qry: Dict[str, Any]) -> str:
        name = qry.get("name", "")
        return (
            f"    def {name}(self, request, context):  # noqa: N802 (gRPC casing)\n"
            f"        # TODO: wire up the {name}Handler for the `{context}` context.\n"
            f"        return pb.{name}Response(result_json=\"{{}}\")\n"
        )

    cmd_methods = "\n".join(_cmd_method(c) for c in commands) or (
        "    # no commands declared in the manifest — add @command-decorated classes.\n"
        "    pass\n"
    )
    qry_methods = "\n".join(_qry_method(q) for q in queries) or (
        "    # no queries declared in the manifest — add @query-decorated classes.\n"
        "    pass\n"
    )

    return f'''"""
gRPC servicer stubs for the `{context}` bounded context.

Each method is a starting point — replace the TODO blocks with calls
into your actual command / query handlers.
"""

from __future__ import annotations

from typing import Any

{pb_import}
{pb_grpc_import}

from .publisher import BusPublisher


class {service_class}CommandServicer({cmd_base}):
    def __init__(self, bus: BusPublisher) -> None:
        self.bus = bus

{cmd_methods}

class {service_class}QueryServicer({qry_base}):
{qry_methods}
'''


def _render_publisher(bus: str) -> str:
    return f'''"""
Minimal pluggable bus publisher.

Supported backends: rabbitmq, redis, kafka, memory.
Selection happens via the ``BUS_BACKEND`` env var (default: {bus!r}).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Protocol


log = logging.getLogger(__name__)


class BusPublisher(Protocol):
    def publish(self, topic: str, payload: Dict[str, Any]) -> None: ...  # pragma: no cover

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @staticmethod
    def from_env() -> "BusPublisher":
        backend = os.environ.get("BUS_BACKEND", "{bus}").lower()
        if backend == "memory":
            return InMemoryPublisher()
        url = os.environ.get("BUS_URL", "")
        if backend == "rabbitmq":
            return RabbitMQPublisher(url)
        if backend == "redis":
            return RedisPublisher(url)
        if backend == "kafka":
            return KafkaPublisher(url)
        raise ValueError(f"unknown BUS_BACKEND: {{backend!r}}")


class InMemoryPublisher:
    def __init__(self) -> None:
        self.sent: list[tuple[str, Dict[str, Any]]] = []

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        log.info("[memory] %s %s", topic, payload)
        self.sent.append((topic, payload))


class RabbitMQPublisher:
    def __init__(self, url: str) -> None:
        if not url:
            raise ValueError("BUS_URL must be set for rabbitmq")
        try:
            import pika  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - optional dep
            raise RuntimeError("install `pika` for RabbitMQ support") from exc
        params = pika.URLParameters(url)
        self._conn = pika.BlockingConnection(params)
        self._channel = self._conn.channel()

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        self._channel.basic_publish(
            exchange=topic, routing_key="", body=json.dumps(payload).encode("utf-8")
        )


class RedisPublisher:
    def __init__(self, url: str) -> None:
        if not url:
            raise ValueError("BUS_URL must be set for redis")
        try:
            import redis  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - optional dep
            raise RuntimeError("install `redis` for Redis support") from exc
        self._client = redis.from_url(url)

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        self._client.publish(topic, json.dumps(payload))


class KafkaPublisher:
    def __init__(self, url: str) -> None:
        if not url:
            raise ValueError("BUS_URL must be set for kafka")
        try:
            from kafka import KafkaProducer  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - optional dep
            raise RuntimeError("install `kafka-python` for Kafka support") from exc
        self._producer = KafkaProducer(bootstrap_servers=url)

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        self._producer.send(topic, json.dumps(payload).encode("utf-8"))
        self._producer.flush()
'''


def _render_requirements(bus: str) -> str:
    lines = [
        "grpcio>=1.60",
        "grpcio-tools>=1.60",
        "protobuf>=4.25",
    ]
    if bus == "rabbitmq":
        lines.append("pika>=1.3")
    elif bus == "redis":
        lines.append("redis>=5.0")
    elif bus == "kafka":
        lines.append("kafka-python>=2.0")
    return "\n".join(lines) + "\n"


def _render_dockerfile(base_image: str, *, pkg: str) -> str:
    return f"""# Auto-generated by swop gen services.
FROM {base_image}

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./{pkg}/
ENV PYTHONPATH=/app

CMD ["python", "-m", "{pkg}.worker"]
"""


def _render_env(*, bus: str, context: str, grpc_port: int) -> str:
    default_url = {
        "rabbitmq": "amqp://guest:guest@rabbitmq:5672/",
        "redis": "redis://redis:6379/0",
        "kafka": "kafka:9092",
        "memory": "",
    }.get(bus, "")
    return (
        f"# Environment for the `{context}` service.\n"
        f"CONTEXT={context}\n"
        f"GRPC_PORT={grpc_port}\n"
        f"BUS_BACKEND={bus}\n"
        f"BUS_URL={default_url}\n"
        f"LOG_LEVEL=INFO\n"
    )


# ----------------------------------------------------------------------
# docker-compose
# ----------------------------------------------------------------------


def _render_compose(contexts: List[str], bus: str, *, grpc_port: int) -> str:
    services: Dict[str, Any] = {}
    depends_on: List[str] = []

    if bus == "rabbitmq":
        services["rabbitmq"] = {
            "image": "rabbitmq:3-management",
            "ports": ["5672:5672", "15672:15672"],
            "healthcheck": {
                "test": ["CMD", "rabbitmq-diagnostics", "ping"],
                "interval": "10s",
                "retries": 5,
            },
        }
        depends_on.append("rabbitmq")
    elif bus == "redis":
        services["redis"] = {
            "image": "redis:7-alpine",
            "ports": ["6379:6379"],
            "healthcheck": {
                "test": ["CMD", "redis-cli", "ping"],
                "interval": "10s",
                "retries": 5,
            },
        }
        depends_on.append("redis")
    elif bus == "kafka":
        services["kafka"] = {
            "image": "bitnami/kafka:latest",
            "ports": ["9092:9092"],
            "environment": {
                "KAFKA_ENABLE_KRAFT": "yes",
                "KAFKA_CFG_PROCESS_ROLES": "broker,controller",
                "KAFKA_CFG_LISTENERS": "PLAINTEXT://:9092,CONTROLLER://:9093",
            },
        }
        depends_on.append("kafka")

    for idx, context in enumerate(contexts):
        port = grpc_port + idx
        entry: Dict[str, Any] = {
            "build": {"context": f"./{context}"},
            "environment": {
                "CONTEXT": context,
                "GRPC_PORT": str(port),
                "BUS_BACKEND": bus,
                "BUS_URL": _default_bus_url(bus),
                "LOG_LEVEL": "INFO",
            },
            "ports": [f"{port}:{port}"],
        }
        if depends_on:
            entry["depends_on"] = list(depends_on)
        services[context] = entry

    compose = {
        "version": "3.9",
        "services": services,
    }
    return (
        "# Auto-generated by swop gen services.\n"
        + yaml.safe_dump(compose, sort_keys=False, default_flow_style=False)
    )


def _default_bus_url(bus: str) -> str:
    return {
        "rabbitmq": "amqp://guest:guest@rabbitmq:5672/",
        "redis": "redis://redis:6379/0",
        "kafka": "kafka:9092",
        "memory": "",
    }.get(bus, "")


# ----------------------------------------------------------------------
# README
# ----------------------------------------------------------------------


def _render_readme(contexts: List[str], bus: str) -> str:
    joined = "\n".join(f"- `{c}/`" for c in contexts) or "- (no contexts detected)"
    return f"""# swop services

Auto-generated service scaffolding.
Bus: **{bus}**

## Contexts

{joined}

## Layout

Each `<context>/` directory contains:

- `worker.py` – process entry point (starts gRPC server + bus consumer)
- `server.py` – gRPC servicer stubs for the commands / queries of the context
- `publisher.py` – pluggable bus publisher (rabbitmq / redis / kafka / memory)
- `Dockerfile` + `requirements.txt` – container build recipe
- `.env.example` – default environment variables

## Running locally

```bash
docker compose -f docker-compose.cqrs.yml up --build
```

## Regenerating

Do not edit the files in-place; re-run:

```bash
swop gen services --bus {bus}
```
"""


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _load_yaml(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None


_SAFE_IDENT = re.compile(r"[^a-zA-Z0-9_]+")


def _safe_ident(name: str) -> str:
    cleaned = _SAFE_IDENT.sub("_", name).strip("_")
    if not cleaned:
        return "svc"
    if cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned


def _camel(name: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p) or "Service"
