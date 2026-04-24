"""
Tests for swop.manifests (manifest YAML generator) and field extraction.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
import yaml

from swop.cli import main
from swop.config import load_config
from swop.manifests import generate_manifests
from swop.scan import scan_project
from swop.tools import init_project


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body), encoding="utf-8")


@pytest.fixture
def customer_project(tmp_path: Path) -> Path:
    init_project(tmp_path, project_name="toy")
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: toy
        language: python
        source_roots:
          - src
        bounded_contexts:
          - name: customer
            source: src/customer
          - name: device
            source: src/device
        bus:
          type: rabbitmq
          url: "amqp://localhost"
        """,
    )
    _write(
        tmp_path / "src/customer/commands.py",
        """\
        from dataclasses import dataclass
        from typing import Optional
        from swop import command, event

        @command("customer", emits=["CustomerCreated"])
        @dataclass
        class CreateCustomer:
            name: str
            email: str
            tax_id: Optional[str] = None
            age: int | None = None

        @event("customer")
        @dataclass
        class CustomerCreated:
            customer_id: int
            name: str = "anonymous"
        """,
    )
    _write(
        tmp_path / "src/customer/handlers.py",
        """\
        from swop import handler
        from .commands import CreateCustomer
        from .public_models import CustomerStatus, CustomerView
        from .queries import GetCustomer

        @handler(CreateCustomer)
        class CreateCustomerHandler:
            def handle(self, cmd: CreateCustomer) -> int:
                return 1

        @handler(GetCustomer)
        class GetCustomerHandler:
            def handle(self, query: GetCustomer) -> CustomerView:
                return CustomerView(customer_id=query.customer_id, status=CustomerStatus.ACTIVE)
        """,
    )
    _write(
        tmp_path / "src/customer/queries.py",
        """\
        from dataclasses import dataclass
        from swop import query

        @query("customer")
        @dataclass
        class GetCustomer:
            customer_id: int
        """,
    )
    _write(
        tmp_path / "src/customer/models.py",
        """\
        from dataclasses import dataclass
        from .enums import CustomerStatus

        @dataclass
        class CustomerView:
            customer_id: int
            status: CustomerStatus | None = None
        """,
    )
    _write(
        tmp_path / "src/customer/public_models.py",
        """\
        from .models import CustomerView
        from .enums import CustomerStatus
        """,
    )
    _write(
        tmp_path / "src/customer/enums.py",
        """\
        from .shared_enums import CustomerStatus
        """,
    )
    _write(
        tmp_path / "src/customer/shared_enums.py",
        """\
        from enum import Enum

        class CustomerStatus(str, Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"
        """,
    )
    _write(
        tmp_path / "src/a_shadow/confuser.py",
        """\
        from dataclasses import dataclass
        from enum import Enum

        class CustomerStatus(str, Enum):
            WRONG = "wrong"

        @dataclass
        class CustomerView:
            customer_id: int
            status: CustomerStatus
        """,
    )
    _write(
        tmp_path / "src/device/heuristic.py",
        """\
        class PowerOnCommand:
            device_id: str
            reason: str = "manual"
        """,
    )
    return tmp_path


# ----------------------------------------------------------------------
# Field extraction (scanner side)
# ----------------------------------------------------------------------


def test_scan_extracts_fields_from_dataclass(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)

    create = next(d for d in report.detections if d.name == "CreateCustomer")
    field_names = {f.name for f in create.fields}
    assert field_names == {"name", "email", "tax_id", "age"}

    by_name = {f.name: f for f in create.fields}
    assert by_name["name"].required is True
    assert by_name["email"].type == "str"
    assert by_name["tax_id"].required is False       # Optional[str]
    assert by_name["age"].required is False          # int | None
    assert by_name["tax_id"].nullable is True
    assert by_name["age"].nullable is True
    assert create.file_fingerprint is not None


def test_scan_handler_records_method_name(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    handler_det = next(d for d in report.detections if d.name == "CreateCustomerHandler")
    assert handler_det.handles == "CreateCustomer"
    assert handler_det.handler_method == "handle"


# ----------------------------------------------------------------------
# Manifest generation
# ----------------------------------------------------------------------


def test_generate_manifests_writes_per_context_files(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    out = tmp = customer_project / ".swop" / "manifests"

    result = generate_manifests(report, cfg, out_dir=out)

    paths = {f.path.relative_to(out).as_posix() for f in result.files}
    assert "customer/commands.yml" in paths
    assert "customer/queries.yml" in paths
    assert "customer/events.yml" in paths
    # Device has only heuristic detections (a command) — still written.
    assert "device/commands.yml" in paths


def test_manifest_yaml_shape_for_command(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    out = customer_project / "out"
    generate_manifests(report, cfg, out_dir=out)

    manifest = yaml.safe_load((out / "customer" / "commands.yml").read_text())
    assert manifest["version"] == 1
    assert manifest["context"] == "customer"
    commands = {c["name"]: c for c in manifest["commands"]}
    create = commands["CreateCustomer"]

    # source block
    assert create["source"]["file"] == "src/customer/commands.py"
    assert create["source"]["class"] == "CreateCustomer"
    assert create["source"]["fingerprint"].startswith("sha256:")

    # fields carry over with required flag
    field_map = {f["name"]: f for f in create["fields"]}
    assert field_map["name"]["required"] is True
    assert field_map["email"]["type"] == "str"
    assert field_map["tax_id"]["required"] is False
    assert field_map["tax_id"]["nullable"] is True

    # handler linked
    assert create["handler"]["file"] == "src/customer/handlers.py"
    assert create["handler"]["class"] == "CreateCustomerHandler"
    assert create["handler"]["method"] == "handle"

    # emits + bus (rabbitmq)
    assert create["emits"] == ["CustomerCreated"]
    bus = create["bus"]
    assert bus["exchange"] == "customer.commands"
    assert bus["routing_key"] == "customer.create.customer"

    # decorator-based detection recorded as via=decorator
    assert create["detected"]["via"] == "decorator"


def test_manifest_event_has_fields_but_no_bus(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    out = customer_project / "out"
    generate_manifests(report, cfg, out_dir=out)

    events = yaml.safe_load((out / "customer" / "events.yml").read_text())
    created = events["events"][0]
    assert created["name"] == "CustomerCreated"
    assert "bus" not in created
    assert "handler" not in created
    assert any(f["name"] == "customer_id" for f in created["fields"])
    default_name = next(f for f in created["fields"] if f["name"] == "name")
    assert default_name["required"] is False
    assert default_name["default"] == "'anonymous'"


def test_manifest_heuristic_detection_carries_confidence(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    out = customer_project / "out"
    generate_manifests(report, cfg, out_dir=out)

    device = yaml.safe_load((out / "device" / "commands.yml").read_text())
    power_on = device["commands"][0]
    assert power_on["name"] == "PowerOnCommand"
    detected = power_on["detected"]
    assert detected["via"] == "heuristic"
    assert "confidence" in detected
    assert detected["confidence"] < 1.0


def test_manifest_query_includes_response_and_types(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    out = customer_project / "out"
    generate_manifests(report, cfg, out_dir=out)

    manifest = yaml.safe_load((out / "customer" / "queries.yml").read_text())
    query = next(q for q in manifest["queries"] if q["name"] == "GetCustomer")

    assert query["handler"]["class"] == "GetCustomerHandler"
    assert query["response"]["type"] == "CustomerView"
    response_fields = {f["name"]: f for f in query["response"]["fields"]}
    assert response_fields["customer_id"]["type"] == "int"
    assert response_fields["status"]["type"] == "CustomerStatus | None"
    assert response_fields["status"]["nullable"] is True

    types = {(t["kind"], t["name"]): t for t in query["types"]}
    status_enum = types[("enum", "CustomerStatus")]
    assert [v["name"] for v in status_enum["values"]] == ["ACTIVE", "INACTIVE"]


def test_generate_manifests_redis_bus(tmp_path):
    init_project(tmp_path, project_name="redisdemo")
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: redisdemo
        source_roots: [src]
        bounded_contexts:
          - name: billing
            source: src/billing
        bus:
          type: redis
        """,
    )
    _write(
        tmp_path / "src/billing/cmd.py",
        """\
        from swop import command
        @command("billing")
        class InvoiceCustomer:
            customer_id: int = 0
        """,
    )
    cfg = load_config(tmp_path / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    out = tmp_path / "out"
    generate_manifests(report, cfg, out_dir=out)

    manifest = yaml.safe_load((out / "billing" / "commands.yml").read_text())
    bus = manifest["commands"][0]["bus"]
    assert bus == {"stream": "billing.commands"}


def test_generate_manifests_no_bus_when_unconfigured(tmp_path):
    init_project(tmp_path, project_name="nobus")
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: nobus
        source_roots: [src]
        bounded_contexts:
          - name: plain
            source: src/plain
        """,
    )
    _write(
        tmp_path / "src/plain/cmd.py",
        """\
        from swop import command
        @command("plain")
        class Ping:
            x: int = 0
        """,
    )
    cfg = load_config(tmp_path / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    out = tmp_path / "out"
    generate_manifests(report, cfg, out_dir=out)
    manifest = yaml.safe_load((out / "plain" / "commands.yml").read_text())
    assert "bus" not in manifest["commands"][0]


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def test_cli_gen_manifests(customer_project, capsys):
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "gen",
            "manifests",
            "--root",
            str(customer_project),
            "--out",
            str(customer_project / "out"),
            "--no-incremental",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[GEN]" in captured.out
    assert (customer_project / "out" / "customer" / "commands.yml").exists()


def test_cli_gen_manifests_skip_heuristics(customer_project, capsys):
    out_dir = customer_project / "out"
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "gen",
            "manifests",
            "--root",
            str(customer_project),
            "--out",
            str(out_dir),
            "--skip-heuristics",
            "--no-incremental",
        ]
    )
    assert exit_code == 0
    # Decorator-based command file exists, but the heuristic-only device file must not.
    assert (out_dir / "customer" / "commands.yml").exists()
    assert not (out_dir / "device" / "commands.yml").exists()
