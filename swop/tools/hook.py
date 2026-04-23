"""
Install / uninstall a git pre-commit hook that runs `swop resolve --strict`.

The hook is intentionally tiny and idempotent:

* It writes a shell script to ``<git-dir>/hooks/pre-commit``.
* A marker line identifies hooks managed by swop so we can safely
  upgrade or remove them without touching user-provided hooks.
* When the target file already exists and was not produced by swop,
  the caller must pass ``force=True`` to overwrite it.

All operations return a :class:`HookResult` describing the outcome for
clean CLI surfacing and test assertions.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

HOOK_MARKER = "# swop:managed-hook"
HOOK_NAME = "pre-commit"

HOOK_TEMPLATE = f"""#!/usr/bin/env sh
{HOOK_MARKER}
# Installed by `swop hook install`. Re-run the installer after upgrading swop.
# Remove with `swop hook uninstall`.

set -e

command -v swop >/dev/null 2>&1 || {{
  echo "[swop hook] swop is not on PATH; skipping check." >&2
  exit 0
}}

exec swop resolve --strict --no-incremental "$@"
"""


# ----------------------------------------------------------------------
# Result objects
# ----------------------------------------------------------------------


@dataclass
class HookResult:
    action: str  # "install" | "uninstall" | "status"
    hook_path: Optional[Path] = None
    status: str = "ok"  # "ok" | "skipped" | "error"
    detail: str = ""

    def format(self) -> str:
        symbol = {"ok": "✔", "skipped": "⚠", "error": "✖"}.get(self.status, "?")
        target = str(self.hook_path) if self.hook_path else "-"
        head = f"[HOOK] {self.action} {symbol} {target}"
        if self.detail:
            return head + f"\n       {self.detail}"
        return head


# ----------------------------------------------------------------------
# Resolution helpers
# ----------------------------------------------------------------------


def _git_dir(root: Path) -> Optional[Path]:
    """Return the path to the git dir for ``root`` (or None if not a repo)."""
    root = Path(root).resolve()
    git_path = root / ".git"
    if git_path.is_dir():
        return git_path
    if git_path.is_file():
        # worktree: ``gitdir: …``
        try:
            body = git_path.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        if body.startswith("gitdir:"):
            target = Path(body.split(":", 1)[1].strip())
            if not target.is_absolute():
                target = (root / target).resolve()
            return target if target.exists() else None
    if not shutil.which("git"):
        return None
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    raw = proc.stdout.strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = (root / path).resolve()
    return path if path.exists() else None


def _hook_path(root: Path) -> Optional[Path]:
    gitdir = _git_dir(root)
    if gitdir is None:
        return None
    hooks_dir = gitdir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    return hooks_dir / HOOK_NAME


def _is_swop_hook(path: Path) -> bool:
    try:
        body = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return HOOK_MARKER in body


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def install_hook(root: Path, *, force: bool = False) -> HookResult:
    """Install the pre-commit hook."""
    hook = _hook_path(root)
    if hook is None:
        return HookResult(
            action="install",
            status="error",
            detail=f"{root} is not a git repository (no .git dir)",
        )
    if hook.exists() and not _is_swop_hook(hook) and not force:
        return HookResult(
            action="install",
            hook_path=hook,
            status="skipped",
            detail=(
                "an existing non-swop hook is present; pass --force to overwrite."
            ),
        )
    hook.write_text(HOOK_TEMPLATE, encoding="utf-8")
    _make_executable(hook)
    return HookResult(
        action="install",
        hook_path=hook,
        status="ok",
        detail="pre-commit will run `swop resolve --strict`",
    )


def uninstall_hook(root: Path) -> HookResult:
    """Remove a previously installed swop hook (only if we own it)."""
    hook = _hook_path(root)
    if hook is None:
        return HookResult(
            action="uninstall",
            status="error",
            detail=f"{root} is not a git repository",
        )
    if not hook.exists():
        return HookResult(
            action="uninstall",
            hook_path=hook,
            status="skipped",
            detail="no pre-commit hook installed",
        )
    if not _is_swop_hook(hook):
        return HookResult(
            action="uninstall",
            hook_path=hook,
            status="skipped",
            detail="hook is not managed by swop; leaving untouched.",
        )
    hook.unlink()
    return HookResult(
        action="uninstall",
        hook_path=hook,
        status="ok",
        detail="removed",
    )


def hook_status(root: Path) -> HookResult:
    hook = _hook_path(root)
    if hook is None:
        return HookResult(action="status", status="error", detail="not a git repo")
    if not hook.exists():
        return HookResult(action="status", hook_path=hook, status="skipped", detail="not installed")
    if _is_swop_hook(hook):
        return HookResult(action="status", hook_path=hook, status="ok", detail="swop-managed")
    return HookResult(
        action="status",
        hook_path=hook,
        status="skipped",
        detail="hook present but not managed by swop",
    )


# ----------------------------------------------------------------------
# Internals
# ----------------------------------------------------------------------


def _make_executable(path: Path) -> None:
    try:
        st = path.stat()
    except OSError:
        return
    path.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
