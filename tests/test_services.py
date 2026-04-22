"""
Tests for swop.services (service skeleton + docker-compose generator).
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

from swop.cli import main
from swop.config import load_config
from swop.manifests import generate_manifests
from swop.proto import compile_proto_python, generate_proto_from_manifests
from swop.scan import scan_project
from swop.services import generate_services
from swop.tools import init_project


HAS_GRPC_TOOLS = importlib.util.find_spec("grpc_tools") is not None


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body), encoding="utf-8")


@pytest.fixture
def project_with_manifests(tmp_path: Path) -> Path:
    init_project(tmp_path, project_name="toy")
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: toy
        source_roots: [src]
        bounded_contexts:
          - name: billing
            source: src/billing
          - name: customer
            source: src/customer
        bus:
          type: rabbitmq
          url: "amqp://localhost"
        """,
    )
    _write(
        tmp_path / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from typing import Optional
        from swop import command, query, event

        @command("billing", emits=["InvoiceIssued"])
        @dataclass
        class IssueInvoice:
            customer_id: int
            amount: float
            currency: str = "EUR"
            reference: Optional[str] = None

        @query("billing")
        @dataclass
        class GetInvoice:
            invoice_id: int

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    _write(
        tmp_path / "src/customer/ops.py",
        """\
        from dataclasses import dataclass
        from swop import command

        @command("customer")
        @dataclass
        class CreateCustomer:
            name: str
        """,
    )
    cfg = load_config(tmp_path / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    generate_manifests(report, cfg, out_dir=tmp_path / ".swop" / "manifests")
    return tmp_path


# ----------------------------------------------------------------------
# Core generator
# ----------------------------------------------------------------------


def test_generate_services_writes_package_per_context(project_with_manifests):
    out = project_with_manifests / "services"
    result = generate_services(
        project_with_manifests / ".swop" / "manifests",
        out,
        bus="rabbitmq",
    )
    assert result.bus == "rabbitmq"
    assert result.compose_path == out / "docker-compose.cqrs.yml"
    assert result.compose_path.exists()

    contexts = {f.context for f in result.files if f.context}
    assert contexts == {"billing", "customer"}

    for context in contexts:
        ctx_dir = out / context
        for expected in (
            "__init__.py",
            "worker.py",
            "server.py",
            "publisher.py",
            "requirements.txt",
            "Dockerfile",
            ".env.example",
        ):
            assert (ctx_dir / expected).exists(), f"missing {context}/{expected}"


def test_generate_services_rejects_unknown_bus(project_with_manifests):
    with pytest.raises(ValueError):
        generate_services(
            project_with_manifests / ".swop" / "manifests",
            project_with_manifests / "services",
            bus="mqtt",
        )


def test_generated_python_files_are_syntactically_valid(project_with_manifests):
    out = project_with_manifests / "services"
    generate_services(
        project_with_manifests / ".swop" / "manifests", out, bus="rabbitmq"
    )
    for py_file in out.rglob("*.py"):
        ast.parse(py_file.read_text(encoding="utf-8"))


def test_generated_server_has_servicers_and_methods(project_with_manifests):
    out = project_with_manifests / "services"
    generate_services(
        project_with_manifests / ".swop" / "manifests", out, bus="memory"
    )
    server = (out / "billing" / "server.py").read_text()
    assert "class BillingCommandServicer" in server
    assert "class BillingQueryServicer" in server
    assert "def IssueInvoice(" in server
    assert "def GetInvoice(" in server
    # memory bus → publish call omitted? No: emits is set → publish block present.
    assert "self.bus.publish(" in server


def test_generated_worker_respects_grpc_port(project_with_manifests):
    out = project_with_manifests / "services"
    generate_services(
        project_with_manifests / ".swop" / "manifests",
        out,
        bus="memory",
        grpc_port=60000,
    )
    # billing is first → 60000; customer is second → 60001
    billing_worker = (out / "billing" / "worker.py").read_text()
    customer_worker = (out / "customer" / "worker.py").read_text()
    assert "\"60000\"" in billing_worker
    assert "\"60001\"" in customer_worker


def test_requirements_match_bus(project_with_manifests):
    out = project_with_manifests / "services"
    generate_services(
        project_with_manifests / ".swop" / "manifests", out, bus="redis"
    )
    req = (out / "billing" / "requirements.txt").read_text()
    assert "grpcio" in req
    assert "redis" in req
    assert "pika" not in req


def test_publisher_module_is_importable_in_memory_mode(project_with_manifests, monkeypatch):
    out = project_with_manifests / "services"
    generate_services(
        project_with_manifests / ".swop" / "manifests", out, bus="memory"
    )
    pub_path = out / "billing" / "publisher.py"
    spec = importlib.util.spec_from_file_location("billing_publisher", pub_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    monkeypatch.setenv("BUS_BACKEND", "memory")
    publisher = module.BusPublisher.from_env()
    publisher.publish("customer.events", {"foo": "bar"})
    assert publisher.sent == [("customer.events", {"foo": "bar"})]


# ----------------------------------------------------------------------
# docker-compose
# ----------------------------------------------------------------------


def test_compose_has_bus_and_services(project_with_manifests):
    out = project_with_manifests / "services"
    generate_services(
        project_with_manifests / ".swop" / "manifests", out, bus="rabbitmq"
    )
    compose = yaml.safe_load((out / "docker-compose.cqrs.yml").read_text())
    services = compose["services"]
    assert "rabbitmq" in services
    assert "billing" in services
    assert "customer" in services
    billing = services["billing"]
    assert billing["build"]["context"] == "./billing"
    assert billing["environment"]["BUS_BACKEND"] == "rabbitmq"
    assert billing["environment"]["GRPC_PORT"] == "50051"
    assert billing["environment"]["BUS_URL"].startswith("amqp://")
    assert "rabbitmq" in billing["depends_on"]


def test_compose_redis_bus(project_with_manifests):
    out = project_with_manifests / "services"
    generate_services(
        project_with_manifests / ".swop" / "manifests", out, bus="redis"
    )
    compose = yaml.safe_load((out / "docker-compose.cqrs.yml").read_text())
    assert "redis" in compose["services"]
    assert "rabbitmq" not in compose["services"]
    assert compose["services"]["billing"]["environment"]["BUS_URL"].startswith("redis://")


def test_compose_memory_bus_has_no_broker(project_with_manifests):
    out = project_with_manifests / "services"
    generate_services(
        project_with_manifests / ".swop" / "manifests", out, bus="memory"
    )
    compose = yaml.safe_load((out / "docker-compose.cqrs.yml").read_text())
    assert set(compose["services"].keys()) == {"billing", "customer"}
    assert "depends_on" not in compose["services"]["billing"]


# ----------------------------------------------------------------------
# pb2 copy integration
# ----------------------------------------------------------------------


@pytest.mark.skipif(not HAS_GRPC_TOOLS, reason="grpcio-tools not installed")
def test_generate_services_copies_pb2_when_available(project_with_manifests):
    proto_dir = project_with_manifests / "proto"
    generate_proto_from_manifests(
        project_with_manifests / ".swop" / "manifests", proto_dir
    )
    py_dir = project_with_manifests / "py"
    compile_proto_python(proto_dir, py_dir)

    out = project_with_manifests / "services"
    result = generate_services(
        project_with_manifests / ".swop" / "manifests",
        out,
        bus="memory",
        proto_python_dir=py_dir,
    )
    # pb2 + pb2_grpc copied into each context dir.
    billing_dir = out / "billing"
    assert any(p.name.endswith("_pb2.py") for p in billing_dir.iterdir())
    assert any(p.name.endswith("_pb2_grpc.py") for p in billing_dir.iterdir())

    # And worker.py references pb_grpc (not the placeholder comment).
    worker = (billing_dir / "worker.py").read_text()
    assert "# from . import <your_pb2_grpc>" not in worker

    # And at least one of the generated files is tracked in the result.
    assert any(f.kind == "proto-pb2" for f in result.files)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def test_cli_gen_services_defaults_bus_from_config(project_with_manifests, capsys):
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "gen",
            "services",
            "--root",
            str(project_with_manifests),
            "--out",
            str(project_with_manifests / "cli_services"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0, captured.err
    assert "[SERVICES]" in captured.out
    # swop.yaml declares rabbitmq → compose must contain it
    compose = yaml.safe_load(
        (project_with_manifests / "cli_services" / "docker-compose.cqrs.yml").read_text()
    )
    assert "rabbitmq" in compose["services"]


def test_cli_gen_services_requires_manifests(tmp_path, capsys):
    init_project(tmp_path, project_name="x")
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: x
        source_roots: [src]
        """,
    )
    exit_code = main(["--mode", "SOFT", "gen", "services", "--root", str(tmp_path)])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "manifests directory not found" in captured.err


def test_cli_gen_services_bus_override(project_with_manifests, capsys):
    out_dir = project_with_manifests / "cli_services"
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "gen",
            "services",
            "--root",
            str(project_with_manifests),
            "--out",
            str(out_dir),
            "--bus",
            "memory",
        ]
    )
    assert exit_code == 0
    compose = yaml.safe_load((out_dir / "docker-compose.cqrs.yml").read_text())
    assert "rabbitmq" not in compose["services"]
    assert "redis" not in compose["services"]
