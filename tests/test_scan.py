"""
Tests for swop.scan (CQRS scanner).
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest

from swop.cli import main
from swop.config import load_config
from swop.scan import FingerprintCache, scan_project
from swop.scan.render import render_html, render_json
from swop.tools import init_project


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body), encoding="utf-8")


@pytest.fixture
def customer_project(tmp_path: Path) -> Path:
    """A toy project with explicit @command/@query/@event/@handler decorators."""
    init_project(tmp_path, project_name="toy")
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: toy
        language: python
        source_roots:
          - src
        exclude:
          - "**/tests/**"
        bounded_contexts:
          - name: customer
            source: src/customer
          - name: device
            source: src/device
        """,
    )
    _write(
        tmp_path / "src/customer/commands.py",
        """\
        from dataclasses import dataclass
        from swop import command, event, query

        @command("customer")
        @dataclass
        class CreateCustomer:
            name: str
            email: str

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
    _write(
        tmp_path / "src/customer/handlers.py",
        """\
        from swop import handler
        from .commands import CreateCustomer

        @handler(CreateCustomer)
        class CreateCustomerHandler:
            def handle(self, cmd: CreateCustomer) -> int:
                return 1
        """,
    )
    _write(
        tmp_path / "src/device/heuristic.py",
        """\
        from dataclasses import dataclass

        @dataclass
        class PowerOnCommand:
            device_id: str

        class BaseEvent:
            pass

        class DevicePoweredOn(BaseEvent):
            pass

        class PowerOnHandler:
            def handle(self, cmd: PowerOnCommand) -> bool:
                return True
        """,
    )
    # Noise that must be excluded.
    _write(
        tmp_path / "src/device/tests/test_power.py",
        """\
        class IgnoredTestCommand:
            pass
        """,
    )
    return tmp_path


# ----------------------------------------------------------------------
# Core behaviour
# ----------------------------------------------------------------------


def test_scan_detects_decorator_based(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)

    decorator_dets = [d for d in report.detections if d.via == "decorator"]
    assert len(decorator_dets) == 4  # CreateCustomer, GetCustomer, CustomerCreated, handler

    kinds = report.kinds()
    assert kinds["command"] >= 1
    assert kinds["query"] >= 1
    assert kinds["event"] >= 1
    assert kinds["handler"] >= 1

    names = {d.name for d in report.detections}
    assert "CreateCustomer" in names
    assert "GetCustomer" in names
    assert "CustomerCreated" in names
    assert "CreateCustomerHandler" in names


def test_scan_detects_heuristics_in_device_context(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)

    device = [d for d in report.detections if d.context == "device"]
    assert any(d.name == "PowerOnCommand" and d.via == "heuristic" for d in device)
    assert any(d.name == "DevicePoweredOn" and d.via == "heuristic" for d in device)
    assert any(d.name == "PowerOnHandler" and d.via == "heuristic" for d in device)

    handler_dets = [d for d in device if d.kind == "handler"]
    assert handler_dets[0].handles == "PowerOnCommand"


def test_scan_skips_excluded_paths(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    assert not any("IgnoredTestCommand" == d.name for d in report.detections)


def test_scan_assigns_contexts_by_longest_match(tmp_path):
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: overlap
        source_roots:
          - src
        bounded_contexts:
          - name: outer
            source: src
          - name: inner
            source: src/inner
        """,
    )
    _write(
        tmp_path / "src/top.py",
        """\
        class FooCommand:
            pass
        """,
    )
    _write(
        tmp_path / "src/inner/deep.py",
        """\
        class BarCommand:
            pass
        """,
    )
    cfg = load_config(tmp_path / "swop.yaml")
    report = scan_project(cfg, incremental=False)

    by_name = {d.name: d for d in report.detections}
    assert by_name["FooCommand"].context == "outer"
    assert by_name["BarCommand"].context == "inner"


def test_scan_reports_syntax_error(tmp_path):
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: broken
        source_roots:
          - src
        """,
    )
    _write(tmp_path / "src/__init__.py", "")
    _write(tmp_path / "src/bad.py", "class BadCmd(:  # syntax error")

    cfg = load_config(tmp_path / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    assert report.files_skipped == 1
    assert any("bad.py" in err for err in report.errors)
    # should not crash; no detections from the broken file
    assert all(d.source_file != "src/bad.py" for d in report.detections)


# ----------------------------------------------------------------------
# Cache
# ----------------------------------------------------------------------


def test_incremental_scan_reuses_cache(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    cache_path = cfg.state_path / "cache" / "scan.json"

    first = scan_project(cfg, incremental=True)
    assert first.files_scanned > 0
    assert first.files_cached == 0
    assert cache_path.exists()

    second = scan_project(cfg, incremental=True)
    assert second.files_scanned == 0
    assert second.files_cached == first.files_scanned
    # Detection totals must stay identical.
    assert second.kinds() == first.kinds()


def test_incremental_scan_invalidates_on_change(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    first = scan_project(cfg, incremental=True)

    # Touch a file with a new decorated command.
    target = customer_project / "src/customer/commands.py"
    body = target.read_text() + dedent(
        """\

        @command("customer")
        class SuspendCustomer:
            pass
        """
    )
    target.write_text(body, encoding="utf-8")

    second = scan_project(cfg, incremental=True)
    assert second.files_scanned == 1  # only commands.py re-parsed
    names = {d.name for d in second.detections}
    assert "SuspendCustomer" in names
    assert second.kinds()["command"] == first.kinds()["command"] + 1


def test_cache_prunes_deleted_files(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    scan_project(cfg, incremental=True)

    deleted = customer_project / "src/customer/handlers.py"
    deleted.unlink()

    scan_project(cfg, incremental=True)
    cache = FingerprintCache(cfg.state_path / "cache" / "scan.json")
    cache.load()
    assert "src/customer/handlers.py" not in cache


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------


def test_render_json_roundtrip(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    payload = json.loads(render_json(report))
    assert payload["project"] == "toy"
    assert "detections" in payload
    assert payload["summary"]["kinds"]["command"] >= 1


def test_render_html_contains_summary(customer_project):
    cfg = load_config(customer_project / "swop.yaml")
    report = scan_project(cfg, incremental=False)
    out = render_html(report)
    assert "<title>swop scan — toy</title>" in out
    assert "CreateCustomer" in out
    assert "PowerOnCommand" in out


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def test_cli_scan_text_output(customer_project, capsys):
    exit_code = main(["--mode", "SOFT", "scan", "--root", str(customer_project)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "swop scan" in captured.out
    assert "commands" in captured.out


def test_cli_scan_json_roundtrip(customer_project, capsys, tmp_path):
    out_json = tmp_path / "out.json"
    out_html = tmp_path / "out.html"
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "scan",
            "--root",
            str(customer_project),
            "--json-out",
            str(out_json),
            "--html-out",
            str(out_html),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert out_json.exists()
    assert out_html.exists()
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["project"] == "toy"
    assert "report (json)" in captured.out
    assert "report (html)" in captured.out


def test_cli_scan_strict_heuristics_fails(customer_project):
    exit_code = main(
        [
            "--mode",
            "SOFT",
            "scan",
            "--root",
            str(customer_project),
            "--strict-heuristics",
        ]
    )
    # Heuristic detections in src/device/heuristic.py → must fail.
    assert exit_code == 1
