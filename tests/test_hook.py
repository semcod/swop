"""
Tests for the git pre-commit hook installer.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from swop.cli import main
from swop.tools import hook_status, install_hook, uninstall_hook
from swop.tools.hook import HOOK_MARKER


def _fake_git_repo(tmp_path: Path) -> Path:
    (tmp_path / ".git" / "hooks").mkdir(parents=True)
    return tmp_path


# ----------------------------------------------------------------------
# install / uninstall / status
# ----------------------------------------------------------------------


def test_install_hook_creates_executable_file(tmp_path):
    root = _fake_git_repo(tmp_path)
    result = install_hook(root)
    assert result.status == "ok"
    assert result.hook_path == root / ".git" / "hooks" / "pre-commit"
    body = result.hook_path.read_text(encoding="utf-8")
    assert HOOK_MARKER in body
    assert "swop resolve --strict" in body
    # Executable for user.
    mode = result.hook_path.stat().st_mode
    assert mode & stat.S_IXUSR


def test_install_hook_on_non_git_repo_returns_error(tmp_path):
    result = install_hook(tmp_path)
    assert result.status == "error"
    assert "not a git repository" in result.detail


def test_install_hook_refuses_to_overwrite_foreign_hook(tmp_path):
    root = _fake_git_repo(tmp_path)
    hook = root / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")
    result = install_hook(root)
    assert result.status == "skipped"
    assert "force" in result.detail
    # Original content preserved.
    assert "custom" in hook.read_text(encoding="utf-8")


def test_install_hook_with_force_overwrites(tmp_path):
    root = _fake_git_repo(tmp_path)
    hook = root / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")
    result = install_hook(root, force=True)
    assert result.status == "ok"
    assert HOOK_MARKER in hook.read_text(encoding="utf-8")


def test_install_is_idempotent(tmp_path):
    root = _fake_git_repo(tmp_path)
    first = install_hook(root)
    second = install_hook(root)
    assert first.status == "ok"
    assert second.status == "ok"
    # Still exactly one file, content unchanged.
    assert second.hook_path.read_text() == first.hook_path.read_text()


def test_uninstall_removes_swop_hook(tmp_path):
    root = _fake_git_repo(tmp_path)
    install_hook(root)
    result = uninstall_hook(root)
    assert result.status == "ok"
    assert not (root / ".git" / "hooks" / "pre-commit").exists()


def test_uninstall_preserves_foreign_hook(tmp_path):
    root = _fake_git_repo(tmp_path)
    hook = root / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")
    result = uninstall_hook(root)
    assert result.status == "skipped"
    assert hook.exists()
    assert "custom" in hook.read_text(encoding="utf-8")


def test_uninstall_skipped_when_absent(tmp_path):
    root = _fake_git_repo(tmp_path)
    result = uninstall_hook(root)
    assert result.status == "skipped"
    assert "no pre-commit hook" in result.detail


def test_hook_status_reports_all_states(tmp_path):
    root = _fake_git_repo(tmp_path)
    # Before install.
    s1 = hook_status(root)
    assert s1.status == "skipped"
    assert "not installed" in s1.detail

    # After swop install.
    install_hook(root)
    s2 = hook_status(root)
    assert s2.status == "ok"
    assert "swop-managed" in s2.detail

    # Replace with a foreign hook.
    (root / ".git" / "hooks" / "pre-commit").write_text(
        "#!/bin/sh\necho other\n", encoding="utf-8"
    )
    s3 = hook_status(root)
    assert s3.status == "skipped"
    assert "not managed" in s3.detail


# ----------------------------------------------------------------------
# worktree support (.git file, not dir)
# ----------------------------------------------------------------------


def test_install_follows_git_file_worktree_pointer(tmp_path):
    worktree = tmp_path / "wt"
    real_gitdir = tmp_path / "real.git" / "worktrees" / "wt"
    (real_gitdir / "hooks").mkdir(parents=True)
    worktree.mkdir()
    (worktree / ".git").write_text(f"gitdir: {real_gitdir}\n", encoding="utf-8")

    result = install_hook(worktree)
    assert result.status == "ok"
    assert result.hook_path == real_gitdir / "hooks" / "pre-commit"


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def test_cli_hook_install_and_uninstall(tmp_path, capsys):
    root = _fake_git_repo(tmp_path)

    code = main(["--mode", "SOFT", "hook", "--root", str(root), "install"])
    out = capsys.readouterr().out
    assert code == 0
    assert "install" in out and "✔" in out

    code = main(["--mode", "SOFT", "hook", "--root", str(root), "status"])
    out = capsys.readouterr().out
    assert code == 0
    assert "swop-managed" in out

    code = main(["--mode", "SOFT", "hook", "--root", str(root), "uninstall"])
    out = capsys.readouterr().out
    assert code == 0
    assert "removed" in out


def test_cli_hook_install_non_git_errors(tmp_path, capsys):
    code = main(["--mode", "SOFT", "hook", "--root", str(tmp_path), "install"])
    assert code == 2
    out = capsys.readouterr().out
    assert "not a git repository" in out
