"""Bridge JSON contracts → swop.scan.Detection so they feed the same pipeline."""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional
from swop.registry.loader import Contract
from swop.scan.report import Detection, FieldDef

def _fields(raw: dict, key: str) -> List[FieldDef]:
    out: List[FieldDef] = []
    for name, meta in raw.get(key, {}).items():
        if isinstance(meta, dict):
            out.append(FieldDef(name=name, type=meta.get("type",""), required=bool(meta.get("required",True)), default=None))
        else:
            out.append(FieldDef(name=name, type="", required=True))
    return out

def bridge_contracts_to_detections(contracts: List[Contract], *, project_root: Optional[Path] = None) -> List[Detection]:
    """Convert JSON contracts into :class:`swop.scan.Detection` objects.

    The resulting list can be passed straight to
    :func:`swop.manifests.generate_manifests` and the rest of the swop pipeline,
    eliminating the duplication between hand-written ``.command.json`` specs
    and runtime Python AST scanning.
    """
    detections: List[Detection] = []
    for c in contracts:
        kind = "command" if "command" in c.raw else ("query" if "query" in c.raw else ("event" if "event" in c.raw else "unknown"))
        source = c.raw.get("layers", {}).get("python", str(c.path))
        source_path = project_root / source if project_root and not Path(source).is_absolute() else Path(source)
        detection = Detection(
            kind=kind,
            name=c.name,
            qualname=c.name,
            module=c.raw.get("module", ""),
            context=c.raw.get("module", ""),
            source_file=str(source_path),
            source_line=0,
            via="contract",
            confidence=1.0,
            bases=[],
            decorators=[],
            handles=None,
            emits=list(c.raw.get("events", {}).values()) if "events" in c.raw else [],
            reason="loaded from JSON contract",
            fields=_fields(c.raw, "input") if kind in ("command", "query") else _fields(c.raw, "payload"),
            file_fingerprint=None,
            handler_method=None,
        )
        detections.append(detection)
    return detections
