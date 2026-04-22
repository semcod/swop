"""
Tests for swop.resolve (schema-evolution diff).
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

from swop.cli import main
from swop.config import load_config
from swop.manifests import generate_manifests
from swop.resolve import ChangeKind, apply_resolution, resolve_schema_drift
from swop.scan import scan_project
from swop.tools import init_project


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body), encoding="utf-8")


def _scan(cfg_path: Path):
    cfg = load_config(cfg_path)
    report = scan_project(cfg, incremental=False)
    return cfg, report


@pytest.fixture
def project(tmp_path: Path) -> Path:
    init_project(tmp_path, project_name="evo")
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: evo
        source_roots: [src]
        bounded_contexts:
          - name: billing
            source: src/billing
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
            currency: str = "EUR"

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    # First-time manifest generation = baseline.
    cfg, report = _scan(tmp_path / "swop.yaml")
    generate_manifests(report, cfg, out_dir=tmp_path / ".swop" / "manifests")
    return tmp_path


# ----------------------------------------------------------------------
# Baseline: no drift
# ----------------------------------------------------------------------


def test_no_changes_when_manifests_match(project):
    cfg, report = _scan(project / "swop.yaml")
    resolution = resolve_schema_drift(report, cfg)
    assert resolution.changes == []
    assert "no drift" in resolution.format()


# ----------------------------------------------------------------------
# Additive: new field → non-breaking if optional
# ----------------------------------------------------------------------


def test_added_optional_field_is_non_breaking(project):
    _write(
        project / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from typing import Optional
        from swop import command, event

        @command("billing", emits=["InvoiceIssued"])
        @dataclass
        class IssueInvoice:
            customer_id: int
            amount: float
            currency: str = "EUR"
            note: Optional[str] = None

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    cfg, report = _scan(project / "swop.yaml")
    resolution = resolve_schema_drift(report, cfg)
    kinds = [c.kind for c in resolution.changes]
    assert ChangeKind.ADDED in kinds
    added_field = next(c for c in resolution.changes if c.field == "note")
    assert added_field.breaking is False


def test_added_required_field_is_breaking(project):
    _write(
        project / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from swop import command, event

        @command("billing", emits=["InvoiceIssued"])
        @dataclass
        class IssueInvoice:
            customer_id: int
            amount: float
            currency: str
            reference: str

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    cfg, report = _scan(project / "swop.yaml")
    resolution = resolve_schema_drift(report, cfg)
    ref = next(c for c in resolution.changes if c.field == "reference")
    assert ref.kind == ChangeKind.ADDED
    assert ref.breaking is True


# ----------------------------------------------------------------------
# Removed field + type change → breaking
# ----------------------------------------------------------------------


def test_removed_field_and_type_change_are_breaking(project):
    _write(
        project / "src/billing/ops.py",
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
    cfg, report = _scan(project / "swop.yaml")
    resolution = resolve_schema_drift(report, cfg)
    removed = [c for c in resolution.changes if c.kind == ChangeKind.REMOVED and c.field == "currency"]
    assert len(removed) == 1
    assert removed[0].breaking is True
    type_changed = [c for c in resolution.changes if c.kind == ChangeKind.TYPE_CHANGED]
    assert len(type_changed) == 1
    assert type_changed[0].field == "customer_id"
    assert type_changed[0].old == "int"
    assert type_changed[0].new == "str"
    assert type_changed[0].breaking is True


# ----------------------------------------------------------------------
# Rename detection (same field shape, different name)
# ----------------------------------------------------------------------


def test_rename_detection(project):
    _write(
        project / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from swop import command, event

        @command("billing", emits=["InvoiceIssued"])
        @dataclass
        class RaiseInvoice:
            customer_id: int
            amount: float
            currency: str = "EUR"

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    cfg, report = _scan(project / "swop.yaml")
    resolution = resolve_schema_drift(report, cfg)
    renames = [c for c in resolution.changes if c.kind == ChangeKind.RENAMED]
    assert len(renames) == 1
    assert renames[0].old == "IssueInvoice"
    assert renames[0].new == "RaiseInvoice"
    assert renames[0].breaking is True


# ----------------------------------------------------------------------
# Metadata change: emits list
# ----------------------------------------------------------------------


def test_emits_change_is_metadata_only(project):
    _write(
        project / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from swop import command, event

        @command("billing", emits=["InvoiceIssued", "InvoiceArchived"])
        @dataclass
        class IssueInvoice:
            customer_id: int
            amount: float
            currency: str = "EUR"

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    cfg, report = _scan(project / "swop.yaml")
    resolution = resolve_schema_drift(report, cfg)
    metadata = [c for c in resolution.changes if c.kind == ChangeKind.METADATA]
    assert metadata, "expected metadata change for emits"
    assert all(not c.breaking for c in metadata)


# ----------------------------------------------------------------------
# apply_resolution
# ----------------------------------------------------------------------


def test_apply_resolution_rewrites_manifests(project):
    _write(
        project / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from swop import command, event

        @command("billing", emits=["InvoiceIssued"])
        @dataclass
        class IssueInvoice:
            customer_id: int
            amount: float
            currency: str = "EUR"
            note: str = ""

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    cfg, report = _scan(project / "swop.yaml")
    resolution = resolve_schema_drift(report, cfg)
    assert resolution.changes  # drift present

    apply_resolution(report, cfg, resolution)
    # Second scan should now show no drift.
    cfg2, report2 = _scan(project / "swop.yaml")
    resolution2 = resolve_schema_drift(report2, cfg2)
    assert resolution2.changes == []


# ----------------------------------------------------------------------
# JSON serialisation
# ----------------------------------------------------------------------


def test_resolution_json(project):
    _write(
        project / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
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
    cfg, report = _scan(project / "swop.yaml")
    resolution = resolve_schema_drift(report, cfg)
    payload = json.loads(resolution.to_json())
    assert "counts" in payload
    assert payload["counts"]["total"] == len(resolution.changes)
    assert all("kind" in c for c in payload["changes"])


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def test_cli_resolve_strict_exits_nonzero_on_breaking(project, capsys):
    _write(
        project / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from swop import command, event

        @command("billing", emits=["InvoiceIssued"])
        @dataclass
        class IssueInvoice:
            customer_id: str
            amount: float
            currency: str = "EUR"

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "resolve",
            "--root",
            str(project),
            "--strict",
            "--no-incremental",
        ]
    )
    assert exit_code == 1
    out = capsys.readouterr().out
    assert "type-changed" in out


def test_cli_resolve_apply_fast_forwards(project, capsys):
    _write(
        project / "src/billing/ops.py",
        """\
        from dataclasses import dataclass
        from swop import command, event

        @command("billing", emits=["InvoiceIssued"])
        @dataclass
        class IssueInvoice:
            customer_id: int
            amount: float
            currency: str = "EUR"
            note: str = ""

        @event("billing")
        @dataclass
        class InvoiceIssued:
            invoice_id: int
        """,
    )
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "resolve",
            "--root",
            str(project),
            "--apply",
            "--no-incremental",
        ]
    )
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "applied" in out

    # Second run: drift is gone.
    exit_code2 = main(
        ["--mode", "SOFT", "resolve", "--root", str(project), "--no-incremental"]
    )
    assert exit_code2 == 0
    out2 = capsys.readouterr().out
    assert "no drift" in out2


def test_cli_resolve_json_flag(project, capsys):
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "resolve",
            "--root",
            str(project),
            "--json",
            "--no-incremental",
        ]
    )
    assert exit_code == 0
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert "counts" in payload
    assert "changes" in payload
