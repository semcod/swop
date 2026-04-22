"""
swop doctor.

Verifies that the local environment can run the swop playbook: Python
version, PyYAML, swop package, optional tooling (protoc, docker, git)
and whether the cwd is a git repository.

Missing *optional* tools are reported as warnings (``status="warn"``);
missing *required* tools are reported as errors (``status="fail"``).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import swop

# ----------------------------------------------------------------------
# Result objects
# ----------------------------------------------------------------------


CheckStatus = str  # "pass" | "warn" | "fail"


@dataclass
class DoctorCheck:
    name: str
    status: CheckStatus
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "pass"

    def format(self) -> str:
        symbol = {"pass": "✔", "warn": "⚠", "fail": "✖"}.get(self.status, "?")
        return f"  {symbol} {self.name}: {self.detail}"


@dataclass
class DoctorReport:
    checks: List[DoctorCheck] = field(default_factory=list)

    @property
    def failed(self) -> List[DoctorCheck]:
        return [c for c in self.checks if c.status == "fail"]

    @property
    def warnings(self) -> List[DoctorCheck]:
        return [c for c in self.checks if c.status == "warn"]

    @property
    def ok(self) -> bool:
        return not self.failed

    def format(self) -> str:
        lines = [f"swop {swop.__version__} — environment check"]
        lines.extend(c.format() for c in self.checks)
        if self.failed:
            lines.append(f"\n{len(self.failed)} check(s) failed.")
        elif self.warnings:
            lines.append(f"\nAll required checks passed ({len(self.warnings)} warning(s)).")
        else:
            lines.append("\nAll checks passed.")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Check helpers
# ----------------------------------------------------------------------


def _check_python() -> DoctorCheck:
    ver = sys.version_info
    detail = f"{ver.major}.{ver.minor}.{ver.micro}"
    if ver < (3, 8):
        return DoctorCheck("python", "fail", f"{detail} (need >=3.8)")
    if ver < (3, 11):
        return DoctorCheck("python", "warn", f"{detail} (playbook assumes >=3.11)")
    return DoctorCheck("python", "pass", detail)


def _check_swop() -> DoctorCheck:
    return DoctorCheck("swop", "pass", swop.__version__)


def _check_pyyaml() -> DoctorCheck:
    try:
        import yaml  # noqa: F401
    except ImportError:
        return DoctorCheck("pyyaml", "fail", "not installed")
    try:
        from yaml import __version__ as yaml_version  # type: ignore[attr-defined]
    except ImportError:
        yaml_version = "unknown"
    return DoctorCheck("pyyaml", "pass", yaml_version)


def _run_version(cmd: List[str]) -> Optional[str]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    out = (proc.stdout or proc.stderr or "").strip()
    return out.splitlines()[0] if out else None


def _first_version(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"\d+(?:\.\d+){1,2}", text)
    return match.group(0) if match else text


def _check_binary(
    binary: str,
    version_args: Tuple[str, ...],
    *,
    required: bool = False,
) -> DoctorCheck:
    path = shutil.which(binary)
    if not path:
        status: CheckStatus = "fail" if required else "warn"
        return DoctorCheck(binary, status, "not found in PATH")
    raw = _run_version([binary, *version_args])
    version = _first_version(raw) or "unknown"
    return DoctorCheck(binary, "pass", f"{version} ({path})")


def _check_git_repo(root: Path) -> DoctorCheck:
    if not shutil.which("git"):
        return DoctorCheck("git repo", "warn", "git not installed; cannot verify")
    if not (root / ".git").exists():
        # Might be a worktree; ask git directly.
        try:
            proc = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return DoctorCheck("git repo", "warn", "git call failed")
        if proc.returncode != 0:
            return DoctorCheck("git repo", "warn", f"{root} is not a git repo")
    # Try to fetch a short description.
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    if proc.returncode == 0:
        top = proc.stdout.strip()
        return DoctorCheck("git repo", "pass", top or str(root))
    return DoctorCheck("git repo", "warn", f"{root} is not a git repo")


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def run_doctor(root: Optional[Path] = None) -> DoctorReport:
    """Run the full doctor suite and return a report."""
    root = Path(root) if root else Path.cwd()
    report = DoctorReport()
    report.checks.append(DoctorCheck("swop", "pass", swop.__version__))
    report.checks.append(_check_python())
    report.checks.append(_check_pyyaml())
    report.checks.append(_check_binary("docker", ("--version",)))
    report.checks.append(_check_binary("protoc", ("--version",)))
    report.checks.append(_check_binary("git", ("--version",)))
    report.checks.append(_check_git_repo(root))
    return report
