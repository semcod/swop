"""
`swop doctor --deep` — cross-layer drift checker.

Verifies that each generation tier is consistent with the previous one:

1. **scan ↔ manifests** — current code matches stored manifests
   (via :func:`swop.resolve.resolve_schema_drift`).
2. **manifests ↔ proto** — each context has a ``<ctx>.proto`` at
   ``<state>/generated/proto/<ctx>/v1/`` and the proto is not older
   than the manifests.
3. **proto ↔ grpc-python** — each ``.proto`` has matching ``_pb2.py``
   and ``_pb2_grpc.py`` modules that are not older than the proto.
4. **manifests ↔ services** — each context has a generated service
   package at ``<state>/generated/services/<ctx>/`` with the expected
   entrypoints.

Every layer returns a :class:`DeepCheck` with a ``status`` of
``"pass"``, ``"warn"``, or ``"fail"``. The CLI surfaces the whole
report and exits non-zero when any layer fails.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from swop.config import SwopConfig
from swop.resolve import ChangeKind, resolve_schema_drift
from swop.scan import scan_project


CheckStatus = str  # "pass" | "warn" | "fail"


# ----------------------------------------------------------------------
# Result objects
# ----------------------------------------------------------------------


@dataclass
class DeepIssue:
    context: Optional[str]
    detail: str
    severity: CheckStatus = "warn"

    def format(self) -> str:
        symbol = {"pass": "✔", "warn": "⚠", "fail": "✖"}.get(self.severity, "?")
        prefix = f"{self.context}: " if self.context else ""
        return f"      {symbol} {prefix}{self.detail}"


@dataclass
class DeepCheck:
    name: str
    status: CheckStatus = "pass"
    summary: str = ""
    issues: List[DeepIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.status == "pass"

    def mark(self, status: CheckStatus) -> None:
        # Escalate but never downgrade.
        order = {"pass": 0, "warn": 1, "fail": 2}
        if order[status] > order[self.status]:
            self.status = status

    def format(self) -> str:
        symbol = {"pass": "✔", "warn": "⚠", "fail": "✖"}.get(self.status, "?")
        head = f"  {symbol} {self.name:<24}: {self.summary or self.status}"
        lines = [head]
        for issue in self.issues[:20]:
            lines.append(issue.format())
        if len(self.issues) > 20:
            lines.append(f"      … {len(self.issues) - 20} more")
        return "\n".join(lines)


@dataclass
class DeepReport:
    checks: List[DeepCheck] = field(default_factory=list)
    root: Optional[Path] = None

    @property
    def failed(self) -> List[DeepCheck]:
        return [c for c in self.checks if c.status == "fail"]

    @property
    def warnings(self) -> List[DeepCheck]:
        return [c for c in self.checks if c.status == "warn"]

    @property
    def ok(self) -> bool:
        return not self.failed

    def format(self) -> str:
        lines = [f"[DOCTOR --deep] {len(self.checks)} layer(s) checked"]
        lines.extend(c.format() for c in self.checks)
        if self.failed:
            lines.append(f"\n{len(self.failed)} layer(s) failed — run the matching `swop gen …` command.")
        elif self.warnings:
            lines.append(f"\nAll layers pass with {len(self.warnings)} warning(s).")
        else:
            lines.append("\nAll layers are in sync.")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Individual layer checks
# ----------------------------------------------------------------------


def _check_scan_vs_manifests(config: SwopConfig) -> DeepCheck:
    check = DeepCheck(name="scan ↔ manifests")
    manifests_dir = config.state_path / "manifests"
    if not manifests_dir.exists():
        check.status = "fail"
        check.summary = "manifests directory missing — run `swop gen manifests`"
        check.issues.append(
            DeepIssue(
                context=None,
                detail=f"expected {manifests_dir}",
                severity="fail",
            )
        )
        return check

    report = scan_project(config, incremental=False)
    resolution = resolve_schema_drift(report, config, manifests_dir=manifests_dir)
    if not resolution.changes:
        check.summary = "no drift"
        return check

    counts = resolution.counts()
    check.summary = (
        f"{counts['total']} change(s)"
        + (f", {counts['breaking']} breaking" if counts["breaking"] else "")
    )
    for change in resolution.changes:
        severity: CheckStatus = "fail" if change.breaking else "warn"
        detail = (
            f"{change.kind.value} {change.target} {change.name}"
            + (f".{change.field}" if change.field else "")
            + (f" — {change.detail}" if change.detail else "")
        )
        check.issues.append(
            DeepIssue(context=change.context, detail=detail, severity=severity)
        )
        check.mark(severity)
    return check


def _check_manifests_vs_proto(config: SwopConfig) -> DeepCheck:
    check = DeepCheck(name="manifests ↔ proto")
    manifests_dir = config.state_path / "manifests"
    proto_dir = config.state_path / "generated" / "proto"

    if not manifests_dir.exists():
        check.status = "fail"
        check.summary = "manifests missing"
        return check
    if not proto_dir.exists():
        check.status = "fail"
        check.summary = "proto not generated — run `swop gen proto`"
        return check

    contexts = sorted(
        p.name for p in manifests_dir.iterdir() if p.is_dir()
    )
    missing: List[str] = []
    stale: List[str] = []

    for ctx in contexts:
        proto_file = proto_dir / ctx / "v1" / f"{ctx}.proto"
        if not proto_file.exists():
            missing.append(ctx)
            check.issues.append(
                DeepIssue(
                    context=ctx,
                    detail=f"no {proto_file.relative_to(config.state_path)} "
                    f"— run `swop gen proto`",
                    severity="fail",
                )
            )
            continue
        newest_manifest = _latest_mtime(manifests_dir / ctx)
        if newest_manifest and proto_file.stat().st_mtime < newest_manifest:
            stale.append(ctx)
            check.issues.append(
                DeepIssue(
                    context=ctx,
                    detail="proto older than manifest — run `swop gen proto`",
                    severity="warn",
                )
            )

    if missing:
        check.mark("fail")
    if stale and not missing:
        check.mark("warn")

    parts: List[str] = []
    if missing:
        parts.append(f"{len(missing)} missing")
    if stale:
        parts.append(f"{len(stale)} stale")
    if not parts:
        parts.append("all in sync")
    check.summary = ", ".join(parts)
    return check


def _check_proto_vs_python(config: SwopConfig) -> DeepCheck:
    check = DeepCheck(name="proto ↔ grpc-python")
    proto_dir = config.state_path / "generated" / "proto"
    py_dir = config.state_path / "generated" / "python"

    if not proto_dir.exists():
        check.status = "warn"
        check.summary = "proto not generated"
        return check
    if not py_dir.exists():
        check.status = "warn"
        check.summary = "python stubs not generated — run `swop gen grpc-python`"
        return check

    proto_files = sorted(proto_dir.rglob("*.proto"))
    if not proto_files:
        check.summary = "no proto files"
        return check

    missing: List[str] = []
    stale: List[str] = []
    for proto in proto_files:
        rel = proto.relative_to(proto_dir).with_suffix("")
        pb2 = py_dir / rel.parent / f"{rel.name}_pb2.py"
        pb2_grpc = py_dir / rel.parent / f"{rel.name}_pb2_grpc.py"
        ctx = proto.parts[-3] if len(proto.parts) >= 3 else proto.stem
        for target, kind in ((pb2, "pb2"), (pb2_grpc, "pb2_grpc")):
            if not target.exists():
                missing.append(f"{ctx}/{kind}")
                check.issues.append(
                    DeepIssue(
                        context=ctx,
                        detail=f"missing {target.name} — run `swop gen grpc-python`",
                        severity="fail",
                    )
                )
            elif target.stat().st_mtime < proto.stat().st_mtime:
                stale.append(f"{ctx}/{kind}")
                check.issues.append(
                    DeepIssue(
                        context=ctx,
                        detail=f"{target.name} older than {proto.name}",
                        severity="warn",
                    )
                )

    if missing:
        check.mark("fail")
    if stale and not missing:
        check.mark("warn")

    parts: List[str] = []
    if missing:
        parts.append(f"{len(missing)} missing")
    if stale:
        parts.append(f"{len(stale)} stale")
    if not parts:
        parts.append("all in sync")
    check.summary = ", ".join(parts)
    return check


SERVICE_REQUIRED_FILES = (
    "worker.py",
    "server.py",
    "publisher.py",
    "Dockerfile",
    "requirements.txt",
)


def _check_manifests_vs_services(config: SwopConfig) -> DeepCheck:
    check = DeepCheck(name="manifests ↔ services")
    manifests_dir = config.state_path / "manifests"
    services_dir = config.state_path / "generated" / "services"

    if not manifests_dir.exists():
        check.status = "fail"
        check.summary = "manifests missing"
        return check
    if not services_dir.exists():
        check.status = "warn"
        check.summary = "services not generated — run `swop gen services`"
        return check

    contexts = sorted(p.name for p in manifests_dir.iterdir() if p.is_dir())
    missing: List[str] = []
    incomplete: List[str] = []

    for ctx in contexts:
        ctx_dir = services_dir / ctx
        if not ctx_dir.exists() or not ctx_dir.is_dir():
            missing.append(ctx)
            check.issues.append(
                DeepIssue(
                    context=ctx,
                    detail="no service package — run `swop gen services`",
                    severity="fail",
                )
            )
            continue
        for filename in SERVICE_REQUIRED_FILES:
            if not (ctx_dir / filename).exists():
                incomplete.append(f"{ctx}/{filename}")
                check.issues.append(
                    DeepIssue(
                        context=ctx,
                        detail=f"missing {filename} — re-run `swop gen services`",
                        severity="fail",
                    )
                )

    if missing or incomplete:
        check.mark("fail")
    parts: List[str] = []
    if missing:
        parts.append(f"{len(missing)} missing")
    if incomplete:
        parts.append(f"{len(incomplete)} incomplete")
    if not parts:
        parts.append("all in sync")
    check.summary = ", ".join(parts)
    return check


# ----------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------


def run_deep_doctor(config: SwopConfig) -> DeepReport:
    """Run every cross-layer check against the given config."""
    report = DeepReport(root=config.project_root)
    report.checks.append(_check_scan_vs_manifests(config))
    report.checks.append(_check_manifests_vs_proto(config))
    report.checks.append(_check_proto_vs_python(config))
    report.checks.append(_check_manifests_vs_services(config))
    return report


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _latest_mtime(directory: Path) -> Optional[float]:
    if not directory.exists():
        return None
    latest: Optional[float] = None
    for path in directory.rglob("*"):
        if path.is_file():
            mt = path.stat().st_mtime
            if latest is None or mt > latest:
                latest = mt
    return latest
