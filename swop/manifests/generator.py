"""
Per-context manifest generator.

For every bounded context that has at least one detection of the given
kind, write ``<out_dir>/<context>/<kind>s.yml`` with a deterministic
shape that downstream generators (proto, gRPC, services) can consume
without re-parsing Python source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml

from swop.config import SwopConfig
from swop.scan.report import Detection, ScanReport


MANIFEST_VERSION = 1

# Filenames per kind.
_KIND_FILENAMES = {
    "command": "commands.yml",
    "query": "queries.yml",
    "event": "events.yml",
}

# Plural block name in the YAML body.
_KIND_BLOCK = {
    "command": "commands",
    "query": "queries",
    "event": "events",
}


@dataclass
class ManifestFile:
    context: str
    kind: str
    path: Path
    entries: int


@dataclass
class ManifestGenerationResult:
    files: List[ManifestFile] = field(default_factory=list)
    out_dir: Optional[Path] = None

    @property
    def total_entries(self) -> int:
        return sum(f.entries for f in self.files)

    def by_context(self) -> Dict[str, List[ManifestFile]]:
        out: Dict[str, List[ManifestFile]] = {}
        for f in self.files:
            out.setdefault(f.context, []).append(f)
        return out

    def format(self) -> str:
        if not self.files:
            return "[GEN] no manifests written (no detections)"
        lines = [f"[GEN] wrote {len(self.files)} manifest file(s):"]
        for f in self.files:
            lines.append(f"  -> {f.path} ({f.entries} {f.kind}(s))")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------


def generate_manifests(
    report: ScanReport,
    config: SwopConfig,
    *,
    out_dir: Optional[Path] = None,
) -> ManifestGenerationResult:
    """Write commands/queries/events YAML files per context."""

    out_root = Path(out_dir) if out_dir is not None else config.state_path / "manifests"
    result = ManifestGenerationResult(out_dir=out_root)

    handler_index = _handler_index(report.detections)

    for context in sorted({d.context for d in report.detections}):
        context_dets = [d for d in report.detections if d.context == context]
        ctx_dir = out_root / _safe_dirname(context)
        ctx_dir.mkdir(parents=True, exist_ok=True)
        for kind in ("command", "query", "event"):
            kind_dets = [d for d in context_dets if d.kind == kind]
            if not kind_dets:
                continue
            body = _render_manifest(context, kind, kind_dets, handler_index, config)
            path = ctx_dir / _KIND_FILENAMES[kind]
            path.write_text(body, encoding="utf-8")
            result.files.append(
                ManifestFile(context=context, kind=kind, path=path, entries=len(kind_dets))
            )

    return result


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _handler_index(detections: Iterable[Detection]) -> Dict[str, Detection]:
    """Map target-class-name → handler Detection for quick lookup."""
    index: Dict[str, Detection] = {}
    for det in detections:
        if det.kind != "handler" or not det.handles:
            continue
        # First handler wins — if multiple classes handle the same target
        # we keep the earliest (by source order).
        index.setdefault(det.handles, det)
    return index


def _render_manifest(
    context: str,
    kind: str,
    detections: List[Detection],
    handler_index: Dict[str, Detection],
    config: SwopConfig,
) -> str:
    block = _KIND_BLOCK[kind]
    entries = [
        _render_entry(d, kind, handler_index, config)
        for d in sorted(detections, key=lambda x: x.name)
    ]
    payload = {
        "version": MANIFEST_VERSION,
        "context": context,
        block: entries,
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def _render_entry(
    detection: Detection,
    kind: str,
    handler_index: Dict[str, Detection],
    config: SwopConfig,
) -> Dict[str, object]:
    entry: Dict[str, object] = {
        "name": detection.name,
        "source": _render_source(detection),
        "fields": [_render_field(f) for f in detection.fields],
    }
    detected_via: Dict[str, object] = {"via": detection.via}
    if detection.confidence != 1.0 or detection.via == "heuristic":
        detected_via["confidence"] = round(detection.confidence, 2)
    if detection.reason:
        detected_via["reason"] = detection.reason
    entry["detected"] = detected_via

    if kind in {"command", "query"}:
        handler = handler_index.get(detection.name)
        if handler is not None:
            entry["handler"] = _render_handler(handler)

    if kind == "command":
        if detection.emits:
            entry["emits"] = list(detection.emits)
        bus_section = _render_bus(detection, config)
        if bus_section is not None:
            entry["bus"] = bus_section

    return entry


def _render_source(detection: Detection) -> Dict[str, object]:
    src: Dict[str, object] = {
        "file": detection.source_file,
        "class": detection.name,
        "line": detection.source_line,
    }
    if detection.file_fingerprint:
        src["fingerprint"] = f"sha256:{detection.file_fingerprint}"
    return src


def _render_field(field_def) -> Dict[str, object]:
    out: Dict[str, object] = {"name": field_def.name}
    if field_def.type:
        out["type"] = field_def.type
    out["required"] = field_def.required
    if field_def.default is not None:
        out["default"] = field_def.default
    return out


def _render_handler(handler: Detection) -> Dict[str, object]:
    out: Dict[str, object] = {
        "file": handler.source_file,
        "class": handler.name,
    }
    if handler.handler_method:
        out["method"] = handler.handler_method
    return out


def _render_bus(detection: Detection, config: SwopConfig) -> Optional[Dict[str, object]]:
    if config.bus is None:
        return None
    bus_type = (config.bus.type or "rabbitmq").lower()
    context_key = _safe_dirname(detection.context)
    routing_key = f"{context_key}.{_camel_to_dot(detection.name)}"
    if bus_type == "rabbitmq":
        return {
            "exchange": f"{context_key}.commands",
            "routing_key": routing_key,
        }
    if bus_type in {"redis", "redis-streams"}:
        return {"stream": f"{context_key}.commands"}
    if bus_type in {"kafka"}:
        return {"topic": f"{context_key}.commands"}
    return {"type": bus_type, "routing_key": routing_key}


def _camel_to_dot(name: str) -> str:
    """``CreateCustomer`` -> ``create.customer``; leading verb becomes first token."""
    out: List[str] = []
    current: List[str] = []
    for char in name:
        if char.isupper() and current:
            out.append("".join(current).lower())
            current = [char]
        else:
            current.append(char)
    if current:
        out.append("".join(current).lower())
    return ".".join(out)


def _safe_dirname(name: str) -> str:
    # Keep it file-system safe without surprising the user.
    cleaned = name.strip().replace("/", "_").replace("\\", "_")
    return cleaned or "default"
