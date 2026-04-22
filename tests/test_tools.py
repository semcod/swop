"""
Tests for swop.tools (doctor + init) and their CLI surface.
"""

from pathlib import Path

from swop.cli import main
from swop.config import load_config
from swop.tools import init_project, run_doctor


def test_run_doctor_basic():
    report = run_doctor()
    names = [c.name for c in report.checks]
    assert "swop" in names
    assert "python" in names
    assert "pyyaml" in names
    # swop + pyyaml + python must always pass
    statuses = {c.name: c.status for c in report.checks}
    assert statuses["swop"] == "pass"
    assert statuses["pyyaml"] == "pass"
    assert statuses["python"] in {"pass", "warn"}


def test_init_project_writes_scaffold(tmp_path):
    result = init_project(tmp_path, project_name="demo")
    assert (tmp_path / "swop.yaml").exists()
    assert (tmp_path / ".swop").is_dir()
    assert (tmp_path / ".swop" / "cache").is_dir()
    assert (tmp_path / ".swop" / ".gitignore").exists()
    assert (tmp_path / ".gitignore").exists()

    created_paths = {p.name for p in result.created}
    assert "swop.yaml" in created_paths
    assert ".swop" in created_paths

    # loadable via SwopConfig
    cfg = load_config(tmp_path / "swop.yaml")
    assert cfg.project == "demo"

    # a second call without force should skip swop.yaml
    result2 = init_project(tmp_path, project_name="demo")
    assert tmp_path / "swop.yaml" in result2.skipped


def test_init_project_respects_no_gitignore(tmp_path):
    init_project(tmp_path, update_gitignore=False)
    assert not (tmp_path / ".gitignore").exists()


def test_init_project_appends_to_existing_gitignore(tmp_path):
    gi = tmp_path / ".gitignore"
    gi.write_text("node_modules/\n", encoding="utf-8")
    init_project(tmp_path)
    body = gi.read_text(encoding="utf-8")
    assert "node_modules/" in body
    assert ".swop/" in body
    # no duplicate entries on rerun
    init_project(tmp_path)
    assert body.count(".swop/") <= gi.read_text(encoding="utf-8").count(".swop/")
    assert gi.read_text(encoding="utf-8").count(".swop/") == 1


def test_cli_doctor(capsys):
    exit_code = main(["--mode", "SOFT", "doctor"])
    captured = capsys.readouterr()
    assert "environment check" in captured.out
    # Exit code depends on host, but must not raise.
    assert exit_code in (0, 1)


def test_cli_init(tmp_path, capsys):
    exit_code = main(["--mode", "SOFT", "init", "--root", str(tmp_path), "--name", "playbook"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "INIT" in captured.out
    assert (tmp_path / "swop.yaml").exists()
