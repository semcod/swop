"""
Tests for swop.watch (polling file watcher).
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from textwrap import dedent

import pytest

from swop.cli import main
from swop.config import load_config
from swop.tools import init_project
from swop.watch import WatchEngine, rebuild_once


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body), encoding="utf-8")


@pytest.fixture
def project(tmp_path: Path) -> Path:
    init_project(tmp_path, project_name="watched")
    _write(
        tmp_path / "swop.yaml",
        """\
        version: 1
        project: watched
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
        from swop import command

        @command("billing")
        @dataclass
        class IssueInvoice:
            customer_id: int
            amount: float
        """,
    )
    return tmp_path


# ----------------------------------------------------------------------
# rebuild_once
# ----------------------------------------------------------------------


def test_rebuild_once_runs_scan_and_manifests(project):
    cfg = load_config(project / "swop.yaml")
    rebuild = rebuild_once(cfg, incremental=False)
    assert rebuild.duration_ms >= 0
    assert any(d.name == "IssueInvoice" for d in rebuild.report.detections)
    assert any(
        f.path.name == "commands.yml" and f.context == "billing"
        for f in rebuild.manifests.files
    )


# ----------------------------------------------------------------------
# WatchEngine snapshot & diff
# ----------------------------------------------------------------------


def test_engine_first_poll_returns_none(project):
    cfg = load_config(project / "swop.yaml")
    engine = WatchEngine(config=cfg, interval=0.0, debounce=0.0)
    # Priming call.
    assert engine.poll_once() is None


def test_engine_detects_modifications(project):
    cfg = load_config(project / "swop.yaml")
    engine = WatchEngine(config=cfg, interval=0.0, debounce=0.0)
    engine.poll_once()  # prime

    # Bump the mtime of an existing file deterministically.
    target = project / "src/billing/ops.py"
    new_mtime = target.stat().st_mtime + 10
    os.utime(target, (new_mtime, new_mtime))

    # First call after change: records the change but does not rebuild.
    assert engine.poll_once() is None
    # Second call after debounce window (0s): rebuilds.
    rebuild = engine.poll_once()
    assert rebuild is not None
    assert rebuild.changed_files, "expected changed files to be populated"
    assert any(d.name == "IssueInvoice" for d in rebuild.report.detections)


def test_engine_detects_new_and_deleted_files(project):
    cfg = load_config(project / "swop.yaml")
    engine = WatchEngine(config=cfg, interval=0.0, debounce=0.0)
    engine.poll_once()

    new_file = project / "src/billing/extra.py"
    new_file.write_text(
        "from swop import command\n"
        "from dataclasses import dataclass\n"
        "@command('billing')\n"
        "@dataclass\n"
        "class RefundInvoice:\n"
        "    invoice_id: int\n",
        encoding="utf-8",
    )
    engine.poll_once()  # record change
    rebuild = engine.poll_once()
    assert rebuild is not None
    assert any(d.name == "RefundInvoice" for d in rebuild.report.detections)

    # Now delete it.
    new_file.unlink()
    engine.poll_once()  # record delete
    rebuild = engine.poll_once()
    assert rebuild is not None
    assert not any(d.name == "RefundInvoice" for d in rebuild.report.detections)


def test_engine_ignores_state_dir_writes(project):
    """Regenerated manifests must not retrigger the watcher."""
    cfg = load_config(project / "swop.yaml")
    engine = WatchEngine(config=cfg, interval=0.0, debounce=0.0)
    engine.poll_once()
    # Touch something inside the state dir — the watcher should skip it.
    state_file = cfg.state_path / "manifests" / "billing" / "commands.yml"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("noise", encoding="utf-8")
    assert engine.poll_once() is None  # still no change in source tree


def test_engine_run_stops_after_first_rebuild(project):
    cfg = load_config(project / "swop.yaml")
    engine = WatchEngine(config=cfg, interval=0.0, debounce=0.0)
    engine.poll_once()

    # Mutate a file so a rebuild is guaranteed on the next two polls.
    target = project / "src/billing/ops.py"
    os.utime(target, (target.stat().st_mtime + 10,) * 2)

    received = []
    engine.run(
        on_rebuild=received.append,
        stop_after_first_rebuild=True,
    )
    assert len(received) == 1


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def test_cli_watch_once(project, capsys):
    exit_code = main(
        ["--mode", "SOFT", "watch", "--root", str(project), "--once", "--no-incremental"]
    )
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "[WATCH] rebuilt" in out
    # And the manifest actually landed on disk.
    manifests_file = project / ".swop" / "manifests" / "billing" / "commands.yml"
    assert manifests_file.exists()
