"""
Tests for swop doctor --deep (cross-layer drift).
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from textwrap import dedent

import pytest

from swop.cli import main
from swop.config import load_config
from swop.manifests import generate_manifests
from swop.proto import compile_proto_python, generate_proto_from_manifests
from swop.scan import scan_project
from swop.services import generate_services
from swop.tools import run_deep_doctor
from swop.tools.doctor_deep import (
    _check_manifests_vs_proto,
    _check_manifests_vs_services,
    _check_proto_vs_python,
    _check_scan_vs_manifests,
)
from swop.tools import init_project


HAS_GRPC_TOOLS = importlib.util.find_spec("grpc_tools") is not None


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body), encoding="utf-8")


def _bump_mtime(path: Path, delta: float) -> None:
    st = path.stat()
    os.utime(path, (st.st_atime + delta, st.st_mtime + delta))


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def full_project(tmp_path: Path) -> Path:
    """Project where manifests + proto + services have all been generated."""
    init_project(tmp_path, project_name="full")
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: full
        source_roots: [src]
        bounded_contexts:
          - name: billing
            source: src/billing
        bus:
          type: memory
        """,
    )
    _write(
        tmp_path / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from typing import Optional
        from swop import command, event

        @command("billing", emits=["InvoiceIssued"])
        @dataclass
        class IssueInvoice:
            customer_id: int
            amount: float

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    cfg = load_config(tmp_path / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    generate_manifests(report, cfg, out_dir=cfg.state_path / "manifests")
    generate_proto_from_manifests(
        cfg.state_path / "manifests",
        cfg.state_path / "generated" / "proto",
    )
    if HAS_GRPC_TOOLS:
        compile_proto_python(
            cfg.state_path / "generated" / "proto",
            cfg.state_path / "generated" / "python",
        )
    generate_services(
        cfg.state_path / "manifests",
        cfg.state_path / "generated" / "services",
        bus="memory",
        proto_python_dir=cfg.state_path / "generated" / "python",
    )
    return tmp_path


# ----------------------------------------------------------------------
# Full pipeline happy path
# ----------------------------------------------------------------------


@pytest.mark.skipif(not HAS_GRPC_TOOLS, reason="grpcio-tools not installed")
def test_run_deep_doctor_reports_ok_when_everything_generated(full_project):
    cfg = load_config(full_project / "swop.yaml")
    report = run_deep_doctor(cfg)
    assert report.ok, report.format()
    summaries = {c.name: c.summary for c in report.checks}
    assert "scan ↔ manifests" in summaries
    assert "manifests ↔ proto" in summaries
    assert "proto ↔ grpc-python" in summaries
    assert "manifests ↔ services" in summaries
    assert all("in sync" in s or "no drift" in s for s in summaries.values())


# ----------------------------------------------------------------------
# Individual checks
# ----------------------------------------------------------------------


def test_scan_vs_manifests_flags_breaking_change(full_project):
    _write(
        full_project / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from swop import command, event

        @command("billing", emits=["InvoiceIssued"])
        @dataclass
        class IssueInvoice:
            customer_id: str
            amount: float

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    cfg = load_config(full_project / "swop.yaml")
    check = _check_scan_vs_manifests(cfg)
    assert check.status == "fail"
    assert any("type-changed" in issue.detail for issue in check.issues)


def test_manifests_vs_proto_warns_when_proto_is_stale(full_project):
    cfg = load_config(full_project / "swop.yaml")
    # Bump the manifests forward in time — proto becomes stale.
    manifest = cfg.state_path / "manifests" / "billing" / "commands.yml"
    _bump_mtime(manifest, 1000.0)

    check = _check_manifests_vs_proto(cfg)
    assert check.status == "warn"
    assert "stale" in check.summary


def test_manifests_vs_proto_fails_when_proto_missing(full_project):
    cfg = load_config(full_project / "swop.yaml")
    proto_file = cfg.state_path / "generated" / "proto" / "billing" / "v1" / "billing.proto"
    proto_file.unlink()
    check = _check_manifests_vs_proto(cfg)
    assert check.status == "fail"
    assert "missing" in check.summary


@pytest.mark.skipif(not HAS_GRPC_TOOLS, reason="grpcio-tools not installed")
def test_proto_vs_python_fails_when_stubs_missing(full_project):
    cfg = load_config(full_project / "swop.yaml")
    pb2 = next(
        (cfg.state_path / "generated" / "python" / "billing" / "v1").glob("*_pb2.py")
    )
    pb2.unlink()
    check = _check_proto_vs_python(cfg)
    assert check.status == "fail"
    assert any("pb2" in issue.detail for issue in check.issues)


def test_proto_vs_python_warns_without_python_dir(tmp_path):
    """When grpc-python was never generated, this is a warning, not failure."""
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: tiny
        source_roots: [src]
        """,
    )
    init_project(tmp_path, project_name="tiny")
    (tmp_path / ".swop" / "generated" / "proto").mkdir(parents=True)
    (tmp_path / ".swop" / "generated" / "proto" / "x.proto").write_text(
        'syntax = "proto3";\n', encoding="utf-8"
    )
    cfg = load_config(tmp_path / "swop.yaml")
    check = _check_proto_vs_python(cfg)
    assert check.status == "warn"


def test_manifests_vs_services_fails_when_package_missing(full_project):
    cfg = load_config(full_project / "swop.yaml")
    services_dir = cfg.state_path / "generated" / "services" / "billing"
    # Nuke the service package.
    for item in services_dir.iterdir():
        item.unlink()
    services_dir.rmdir()
    check = _check_manifests_vs_services(cfg)
    assert check.status == "fail"
    assert "missing" in check.summary


def test_manifests_vs_services_fails_when_incomplete(full_project):
    cfg = load_config(full_project / "swop.yaml")
    (cfg.state_path / "generated" / "services" / "billing" / "worker.py").unlink()
    check = _check_manifests_vs_services(cfg)
    assert check.status == "fail"
    assert any("worker.py" in issue.detail for issue in check.issues)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


@pytest.mark.skipif(not HAS_GRPC_TOOLS, reason="grpcio-tools not installed")
def test_cli_doctor_deep_ok(full_project, capsys):
    exit_code = main(
        ["--mode", "SOFT", "doctor", "--root", str(full_project), "--deep"]
    )
    captured = capsys.readouterr()
    assert exit_code == 0, captured.err
    assert "[DOCTOR --deep]" in captured.out
    assert "All layers are in sync" in captured.out or "layers pass" in captured.out


def test_cli_doctor_deep_nonzero_on_drift(full_project, capsys):
    _write(
        full_project / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from swop import command, event

        @command("billing", emits=["InvoiceIssued"])
        @dataclass
        class IssueInvoice:
            customer_id: str
            amount: float

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    exit_code = main(
        ["--mode", "SOFT", "doctor", "--root", str(full_project), "--deep"]
    )
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "[DOCTOR --deep]" in captured.out
    assert "scan ↔ manifests" in captured.out


def test_cli_doctor_without_deep_does_not_require_config(tmp_path, capsys):
    # Plain `swop doctor` must still work without a swop.yaml.
    exit_code = main(["--mode", "SOFT", "doctor", "--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert "environment check" in out
    # Exit code depends on presence of required tools; we only care we ran.
    assert exit_code in (0, 1)
