"""
Tests for swop.proto (proto generator + gRPC compiler wrappers).
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from textwrap import dedent

import pytest

from swop.cli import main
from swop.config import load_config
from swop.manifests import generate_manifests
from swop.proto import (
    compile_proto_python,
    compile_proto_typescript,
    generate_proto_from_manifests,
    render_proto_for_context,
)
from swop.proto.generator import _map_python_type
from swop.scan import scan_project
from swop.tools import init_project


HAS_GRPC_TOOLS = importlib.util.find_spec("grpc_tools") is not None


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body), encoding="utf-8")


# ----------------------------------------------------------------------
# Type mapping
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "annotation, expected_proto, expected_repeated",
    [
        ("str", "string", False),
        ("int", "int64", False),
        ("float", "double", False),
        ("bool", "bool", False),
        ("bytes", "bytes", False),
        ("Optional[str]", "string", False),
        ("str | None", "string", False),
        ("list[int]", "int64", True),
        ("List[str]", "string", True),
        ("tuple[int, ...]", "int64", True),
        ("datetime", "google.protobuf.Timestamp", False),
    ],
)
def test_map_python_type_basic(annotation, expected_proto, expected_repeated):
    mapped = _map_python_type(annotation)
    assert mapped.proto == expected_proto
    assert mapped.repeated is expected_repeated


def test_map_python_type_dict_becomes_map():
    mapped = _map_python_type("dict[str, int]")
    assert mapped.proto == "map<string, int64>"
    assert mapped.repeated is False


def test_map_python_type_unknown_name_is_stub():
    mapped = _map_python_type("Customer")
    assert mapped.proto == "Customer"
    assert mapped.stub is True


def test_map_python_type_empty_is_string_stub():
    mapped = _map_python_type("")
    assert mapped.proto == "string"
    assert mapped.stub is True


# ----------------------------------------------------------------------
# Renderer
# ----------------------------------------------------------------------


def test_render_proto_for_context_builds_expected_shape():
    commands = [
        {
            "name": "CreateCustomer",
            "fields": [
                {"name": "name", "type": "str", "required": True},
                {"name": "email", "type": "str", "required": True},
                {"name": "tax_id", "type": "Optional[str]", "required": False},
            ],
            "emits": ["CustomerCreated"],
        }
    ]
    queries = [
        {
            "name": "GetCustomer",
            "fields": [{"name": "customer_id", "type": "int", "required": True}],
        }
    ]
    events = [
        {
            "name": "CustomerCreated",
            "fields": [{"name": "customer_id", "type": "int", "required": True}],
        }
    ]

    text, warnings = render_proto_for_context("customer", commands, queries, events)
    assert 'syntax = "proto3";' in text
    assert "package customer.v1;" in text

    # command request + response messages
    assert "message CreateCustomerRequest {" in text
    assert re.search(r"string\s+name\s+=\s+1;", text)
    assert re.search(r"string\s+email\s+=\s+2;", text)
    assert re.search(r"string\s+tax_id\s+=\s+3;", text)
    assert "message CreateCustomerResponse {" in text
    assert "// Emits: CustomerCreated" in text
    assert "repeated string emitted_events = 2;" in text

    # query response message
    assert "message GetCustomerRequest {" in text
    assert "message GetCustomerResponse {" in text
    assert "string result_json = 1;" in text

    # event message
    assert "message CustomerCreated {" in text
    assert re.search(r"int64\s+customer_id\s+=\s+1;", text)

    # services
    assert "service CustomerCommandService {" in text
    assert "rpc CreateCustomer(CreateCustomerRequest) returns (CreateCustomerResponse);" in text
    assert "service CustomerQueryService {" in text
    assert "rpc GetCustomer(GetCustomerRequest) returns (GetCustomerResponse);" in text

    # no spurious warnings for known scalars
    assert warnings == []


def test_render_proto_adds_timestamp_import():
    commands = [
        {
            "name": "ScheduleReminder",
            "fields": [{"name": "at", "type": "datetime", "required": True}],
        }
    ]
    text, _ = render_proto_for_context("scheduler", commands, [], [])
    assert 'import "google/protobuf/timestamp.proto";' in text
    assert "google.protobuf.Timestamp at = 1;" in text


def test_render_proto_warns_on_unknown_user_type():
    commands = [
        {
            "name": "AttachCustomer",
            "fields": [{"name": "payload", "type": "Customer", "required": True}],
        }
    ]
    _, warnings = render_proto_for_context("attach", commands, [], [])
    assert any("payload" in w for w in warnings)


# ----------------------------------------------------------------------
# End-to-end from manifests to .proto
# ----------------------------------------------------------------------


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
          - name: customer
            source: src/customer
        """,
    )
    _write(
        tmp_path / "src/customer/commands.py",
        """\
        from dataclasses import dataclass
        from typing import Optional
        from swop import command, query, event

        @command("customer", emits=["CustomerCreated"])
        @dataclass
        class CreateCustomer:
            name: str
            email: str
            tax_id: Optional[str] = None

        @query("customer")
        @dataclass
        class GetCustomer:
            customer_id: int

        @event("customer")
        @dataclass
        class CustomerCreated:
            customer_id: int
        """,
    )
    cfg = load_config(tmp_path / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    generate_manifests(report, cfg, out_dir=tmp_path / ".swop" / "manifests")
    return tmp_path


def test_generate_proto_from_manifests_writes_file(project_with_manifests):
    out = project_with_manifests / "out"
    result = generate_proto_from_manifests(
        project_with_manifests / ".swop" / "manifests", out
    )
    assert len(result.files) == 1
    proto_file = result.files[0]
    assert proto_file.context == "customer"
    assert proto_file.commands == 1
    assert proto_file.queries == 1
    assert proto_file.events == 1

    text = proto_file.path.read_text(encoding="utf-8")
    assert "package customer.v1;" in text
    assert "service CustomerCommandService" in text
    assert "service CustomerQueryService" in text


def test_generate_proto_skips_empty_context_dirs(tmp_path):
    (tmp_path / "manifests" / "empty").mkdir(parents=True)
    out = tmp_path / "out"
    result = generate_proto_from_manifests(tmp_path / "manifests", out)
    assert result.files == []


# ----------------------------------------------------------------------
# gRPC compilers
# ----------------------------------------------------------------------


@pytest.mark.skipif(not HAS_GRPC_TOOLS, reason="grpcio-tools not installed")
def test_compile_proto_python_produces_pb2(project_with_manifests):
    proto_dir = project_with_manifests / "proto"
    generate_proto_from_manifests(
        project_with_manifests / ".swop" / "manifests", proto_dir
    )
    out = project_with_manifests / "py"
    result = compile_proto_python(proto_dir, out)
    assert result.ok, result.format()
    pb2_files = [p for p in result.outputs if p.name.endswith("_pb2.py")]
    assert pb2_files, f"expected *_pb2.py in {result.outputs}"
    grpc_files = [p for p in result.outputs if p.name.endswith("_pb2_grpc.py")]
    assert grpc_files, f"expected *_pb2_grpc.py in {result.outputs}"


def test_compile_proto_python_without_grpc_tools_returns_helpful_error(tmp_path, monkeypatch):
    (tmp_path / "x.proto").write_text('syntax = "proto3";\n', encoding="utf-8")
    # Simulate absence of grpc_tools by hiding it from sys.modules *and*
    # the finder system.
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "grpc_tools" or name.startswith("grpc_tools."):
            raise ImportError("grpc_tools missing (simulated)")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = compile_proto_python(tmp_path, tmp_path / "out")
    assert result.ok is False
    assert any("grpc_tools" in err for err in result.errors)


def test_compile_proto_typescript_missing_protoc_is_reported(tmp_path, monkeypatch):
    (tmp_path / "x.proto").write_text('syntax = "proto3";\n', encoding="utf-8")
    monkeypatch.setattr("shutil.which", lambda _name: None)
    result = compile_proto_typescript(tmp_path, tmp_path / "out")
    assert result.ok is False
    assert any("protoc" in err for err in result.errors)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def test_cli_gen_proto_requires_manifests(tmp_path, capsys):
    init_project(tmp_path, project_name="x")
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: x
        source_roots: [src]
        """,
    )
    exit_code = main(["--mode", "SOFT", "gen", "proto", "--root", str(tmp_path)])
    captured = capsys.readouterr()
    # No manifests directory exists yet.
    assert exit_code == 2
    assert "manifests directory not found" in captured.err


def test_cli_gen_proto_end_to_end(project_with_manifests, capsys):
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "gen",
            "proto",
            "--root",
            str(project_with_manifests),
            "--out",
            str(project_with_manifests / "cli_out"),
        ]
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "[PROTO]" in captured.out
    assert (
        project_with_manifests / "cli_out" / "customer" / "v1" / "customer.proto"
    ).exists()


def test_cli_gen_grpc_python_reports_ok_or_missing(project_with_manifests, capsys):
    # Pre-generate the proto files so the compiler has something to do.
    generate_proto_from_manifests(
        project_with_manifests / ".swop" / "manifests",
        project_with_manifests / ".swop" / "generated" / "proto",
    )
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "gen",
            "grpc-python",
            "--root",
            str(project_with_manifests),
        ]
    )
    captured = capsys.readouterr()
    if HAS_GRPC_TOOLS:
        assert exit_code == 0
        assert "[GRPC-PYTHON]" in captured.out
    else:
        assert exit_code == 1
        assert "grpc_tools" in captured.out
