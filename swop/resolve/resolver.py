"""
Schema-evolution resolver.

Compares the in-memory scan result with the on-disk manifest YAML
files and produces a typed list of changes classified by severity.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

from swop.config import SwopConfig
from swop.manifests import generate_manifests
from swop.scan.report import Detection, ScanReport


# ----------------------------------------------------------------------
# Data model
# ----------------------------------------------------------------------


class ChangeKind(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    RENAMED = "renamed"
    TYPE_CHANGED = "type-changed"
    REQUIRED_CHANGED = "required-changed"
    METADATA = "metadata"


@dataclass
class Change:
    kind: ChangeKind
    context: str
    target: str  # "command" | "query" | "event"
    name: str
    detail: str
    breaking: bool = False
    field: Optional[str] = None
    old: Optional[str] = None
    new: Optional[str] = None

    def format(self) -> str:
        label = self.kind.value
        marker = "!" if self.breaking else " "
        prefix = f"  {marker} [{label:<15}] {self.context}/{self.target} {self.name}"
        if self.field:
            prefix += f".{self.field}"
        if self.detail:
            prefix += f" — {self.detail}"
        return prefix


@dataclass
class ResolutionReport:
    changes: List[Change] = field(default_factory=list)
    manifests_dir: Optional[Path] = None

    # --- computed helpers -------------------------------------------

    @property
    def breaking(self) -> List[Change]:
        return [c for c in self.changes if c.breaking]

    @property
    def non_breaking(self) -> List[Change]:
        return [c for c in self.changes if not c.breaking]

    def counts(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for c in self.changes:
            out[c.kind.value] = out.get(c.kind.value, 0) + 1
        out["breaking"] = len(self.breaking)
        out["total"] = len(self.changes)
        return out

    def to_json(self) -> str:
        payload = {
            "manifests_dir": str(self.manifests_dir) if self.manifests_dir else None,
            "counts": self.counts(),
            "changes": [
                {**asdict(c), "kind": c.kind.value} for c in self.changes
            ],
        }
        return json.dumps(payload, indent=2, sort_keys=False)

    def format(self) -> str:
        counts = self.counts()
        if counts["total"] == 0:
            return "[RESOLVE] no drift — manifests match the current scan."
        lines = [
            f"[RESOLVE] {counts['total']} change(s): "
            + ", ".join(
                f"{k}={v}"
                for k, v in counts.items()
                if k not in {"total", "breaking"}
            )
            + (f"  |  breaking={counts['breaking']}" if counts["breaking"] else "")
        ]
        for change in self.changes:
            lines.append(change.format())
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Public entry points
# ----------------------------------------------------------------------


_KINDS = ("command", "query", "event")
_KIND_BLOCK = {"command": "commands", "query": "queries", "event": "events"}
_KIND_FILENAME = {"command": "commands.yml", "query": "queries.yml", "event": "events.yml"}


def resolve_schema_drift(
    report: ScanReport,
    config: SwopConfig,
    *,
    manifests_dir: Optional[Path] = None,
) -> ResolutionReport:
    """Diff the current scan against stored manifests."""
    manifests_root = Path(manifests_dir) if manifests_dir else config.state_path / "manifests"
    resolution = ResolutionReport(manifests_dir=manifests_root)

    current = _index_from_detections(report.detections)
    stored = _index_from_manifests(manifests_root)

    for context in sorted(set(current.keys()) | set(stored.keys())):
        cur_ctx = current.get(context, {})
        old_ctx = stored.get(context, {})
        for kind in _KINDS:
            cur_items = cur_ctx.get(kind, {})
            old_items = old_ctx.get(kind, {})
            _diff_context_kind(context, kind, cur_items, old_items, resolution)

    return resolution


def apply_resolution(
    report: ScanReport,
    config: SwopConfig,
    resolution: ResolutionReport,
    *,
    out_dir: Optional[Path] = None,
) -> Path:
    """Persist the current scan's manifests to disk, returning the target dir.

    This is the *accept* button for :func:`resolve_schema_drift`: after
    reviewing the resolution report the user calls ``swop resolve
    --apply``, which simply re-emits the manifests from the current
    scan (effectively fast-forwarding the stored schema).
    """
    target = Path(out_dir) if out_dir else (resolution.manifests_dir or config.state_path / "manifests")
    generate_manifests(report, config, out_dir=target)
    return target


# ----------------------------------------------------------------------
# Indexers
# ----------------------------------------------------------------------


def _index_from_detections(
    detections: Iterable[Detection],
) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
    out: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
    handler_index: Dict[Tuple[str, str], Detection] = {}
    for det in detections:
        if det.kind == "handler" and det.handles:
            handler_index[(det.context, det.handles)] = det

    for det in detections:
        if det.kind not in _KINDS:
            continue
        ctx = out.setdefault(det.context, {})
        kind_bucket = ctx.setdefault(det.kind, {})
        kind_bucket[det.name] = {
            "name": det.name,
            "fields": {
                f.name: {
                    "type": f.type or "",
                    "required": bool(f.required),
                    "nullable": bool(getattr(f, "nullable", False)),
                }
                for f in (det.fields or [])
            },
            "emits": list(det.emits or []),
            "handler": _handler_shape(handler_index.get((det.context, det.name))),
        }
    return out


def _handler_shape(det: Optional[Detection]) -> Optional[Dict[str, str]]:
    if det is None:
        return None
    return {
        "file": det.source_file,
        "class": det.name,
        "method": det.handler_method or "",
    }


def _index_from_manifests(
    manifests_root: Path,
) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
    out: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
    if not manifests_root.exists() or not manifests_root.is_dir():
        return out
    for ctx_dir in sorted(manifests_root.iterdir()):
        if not ctx_dir.is_dir():
            continue
        context = ctx_dir.name
        for kind in _KINDS:
            path = ctx_dir / _KIND_FILENAME[kind]
            if not path.exists():
                continue
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            block = data.get(_KIND_BLOCK[kind], []) or []
            bucket = out.setdefault(context, {}).setdefault(kind, {})
            for entry in block:
                name = entry.get("name")
                if not name:
                    continue
                bucket[name] = {
                    "name": name,
                    "fields": {
                        f.get("name"): {
                            "type": f.get("type", ""),
                            "required": bool(f.get("required", False)),
                            "nullable": bool(f.get("nullable", False)),
                        }
                        for f in entry.get("fields", [])
                        if f.get("name")
                    },
                    "emits": list(entry.get("emits", []) or []),
                    "handler": entry.get("handler"),
                }
    return out


# ----------------------------------------------------------------------
# Diff logic
# ----------------------------------------------------------------------


def _diff_context_kind(
    context: str,
    kind: str,
    current: Dict[str, Dict[str, Any]],
    stored: Dict[str, Dict[str, Any]],
    resolution: ResolutionReport,
) -> None:
    cur_names = set(current.keys())
    old_names = set(stored.keys())

    added = sorted(cur_names - old_names)
    removed = sorted(old_names - cur_names)

    # Simple rename detection: same field shape, different name.
    renamed_pairs: List[Tuple[str, str]] = []
    if added and removed:
        for new_name in list(added):
            new_fields = _field_signature(current[new_name])
            for old_name in list(removed):
                if _field_signature(stored[old_name]) == new_fields and new_fields:
                    renamed_pairs.append((old_name, new_name))
                    added.remove(new_name)
                    removed.remove(old_name)
                    break

    for name in added:
        resolution.changes.append(
            Change(
                kind=ChangeKind.ADDED,
                context=context,
                target=kind,
                name=name,
                detail=f"new {kind} detected",
                breaking=False,
            )
        )
    for name in removed:
        resolution.changes.append(
            Change(
                kind=ChangeKind.REMOVED,
                context=context,
                target=kind,
                name=name,
                detail=f"{kind} disappeared from the codebase",
                breaking=True,
            )
        )
    for old_name, new_name in renamed_pairs:
        resolution.changes.append(
            Change(
                kind=ChangeKind.RENAMED,
                context=context,
                target=kind,
                name=new_name,
                detail=f"{old_name} → {new_name}",
                breaking=True,
                old=old_name,
                new=new_name,
            )
        )

    # Diff fields & metadata for symbols that exist in both.
    for name in sorted(cur_names & old_names):
        _diff_entry(context, kind, name, stored[name], current[name], resolution)


def _diff_fields(
    context: str,
    kind: str,
    name: str,
    old_fields: Dict[str, Dict[str, Any]],
    new_fields: Dict[str, Dict[str, Any]],
    resolution: ResolutionReport,
) -> None:
    for fname in sorted(set(new_fields) - set(old_fields)):
        f = new_fields[fname]
        resolution.changes.append(
            Change(
                kind=ChangeKind.ADDED,
                context=context,
                target=kind,
                name=name,
                field=fname,
                detail=f"new field (type={f.get('type','?')!r}, required={f.get('required', False)})",
                breaking=bool(f.get("required", False)),
            )
        )
    for fname in sorted(set(old_fields) - set(new_fields)):
        resolution.changes.append(
            Change(
                kind=ChangeKind.REMOVED,
                context=context,
                target=kind,
                name=name,
                field=fname,
                detail="field removed",
                breaking=True,
            )
        )
    for fname in sorted(set(new_fields) & set(old_fields)):
        old_f = old_fields[fname]
        new_f = new_fields[fname]
        if (old_f.get("type") or "") != (new_f.get("type") or ""):
            resolution.changes.append(
                Change(
                    kind=ChangeKind.TYPE_CHANGED,
                    context=context,
                    target=kind,
                    name=name,
                    field=fname,
                    old=str(old_f.get("type") or ""),
                    new=str(new_f.get("type") or ""),
                    detail=f"{old_f.get('type')!r} → {new_f.get('type')!r}",
                    breaking=True,
                )
            )
        if bool(old_f.get("required", False)) != bool(new_f.get("required", False)):
            resolution.changes.append(
                Change(
                    kind=ChangeKind.REQUIRED_CHANGED,
                    context=context,
                    target=kind,
                    name=name,
                    field=fname,
                    old=str(old_f.get("required", False)),
                    new=str(new_f.get("required", False)),
                    detail=f"required {old_f.get('required', False)} → {new_f.get('required', False)}",
                    breaking=bool(new_f.get("required", False))
                    and not bool(old_f.get("required", False)),
                )
            )
        if bool(old_f.get("nullable", False)) != bool(new_f.get("nullable", False)):
            resolution.changes.append(
                Change(
                    kind=ChangeKind.METADATA,
                    context=context,
                    target=kind,
                    name=name,
                    field=fname,
                    old=str(old_f.get("nullable", False)),
                    new=str(new_f.get("nullable", False)),
                    detail=f"nullable {old_f.get('nullable', False)} → {new_f.get('nullable', False)}",
                    breaking=not bool(new_f.get("nullable", False)) and bool(old_f.get("nullable", False)),
                )
            )


def _diff_metadata(
    context: str,
    kind: str,
    name: str,
    old: Dict[str, Any],
    new: Dict[str, Any],
    resolution: ResolutionReport,
) -> None:
    if sorted(old.get("emits") or []) != sorted(new.get("emits") or []):
        resolution.changes.append(
            Change(
                kind=ChangeKind.METADATA,
                context=context,
                target=kind,
                name=name,
                detail=(
                    f"emits changed: {sorted(old.get('emits') or [])} → "
                    f"{sorted(new.get('emits') or [])}"
                ),
            )
        )
    old_handler = _handler_sig(old.get("handler"))
    new_handler = _handler_sig(new.get("handler"))
    if old_handler != new_handler:
        resolution.changes.append(
            Change(
                kind=ChangeKind.METADATA,
                context=context,
                target=kind,
                name=name,
                detail=f"handler changed: {old_handler or '—'} → {new_handler or '—'}",
            )
        )


def _diff_entry(
    context: str,
    kind: str,
    name: str,
    old: Dict[str, Any],
    new: Dict[str, Any],
    resolution: ResolutionReport,
) -> None:
    _diff_fields(
        context, kind, name,
        old.get("fields", {}) or {},
        new.get("fields", {}) or {},
        resolution,
    )
    _diff_metadata(context, kind, name, old, new, resolution)


def _field_signature(entry: Dict[str, Any]) -> Tuple[Tuple[str, str, bool], ...]:
    fields = entry.get("fields", {}) or {}
    return tuple(
        sorted(
            (name, info.get("type", "") or "", bool(info.get("required", False)))
            for name, info in fields.items()
        )
    )


def _handler_sig(handler: Optional[Dict[str, Any]]) -> Optional[str]:
    if not handler:
        return None
    cls = handler.get("class") or ""
    method = handler.get("method") or ""
    file = handler.get("file") or ""
    if not (cls or method or file):
        return None
    return f"{file}::{cls}.{method}".strip(":.")
