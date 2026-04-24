"""
Scan report dataclasses.

Used by :mod:`swop.scan.scanner` to return the outcome of a project
walk and by :mod:`swop.scan.render` for text / JSON / HTML output.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

DetectionKind = str  # "command" | "query" | "event" | "handler"
DetectionVia = str  # "decorator" | "heuristic"


@dataclass
class FieldDef:
    """One attribute declaration extracted from a CQRS class body."""

    name: str
    type: str = ""
    required: bool = True
    nullable: bool = False
    default: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "nullable": self.nullable,
            "default": self.default,
        }


@dataclass
class Detection:
    kind: DetectionKind
    name: str
    qualname: str
    module: str
    context: str
    source_file: str
    source_line: int
    via: DetectionVia
    confidence: float = 1.0
    bases: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    handles: Optional[str] = None  # for handlers
    emits: List[str] = field(default_factory=list)  # for commands
    reason: str = ""
    fields: List[FieldDef] = field(default_factory=list)
    file_fingerprint: Optional[str] = None
    handler_method: Optional[str] = None  # for handlers: `handle` / `execute` / ...

    def to_dict(self) -> Dict[str, object]:
        out = asdict(self)
        out["fields"] = [f.to_dict() if isinstance(f, FieldDef) else f for f in self.fields]
        return out

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Detection":
        raw_fields = data.get("fields") or []
        parsed_fields: List[FieldDef] = []
        for item in raw_fields:
            if isinstance(item, FieldDef):
                parsed_fields.append(item)
            elif isinstance(item, dict):
                parsed_fields.append(
                    FieldDef(
                        name=str(item.get("name", "")),
                        type=str(item.get("type", "")),
                        required=bool(item.get("required", True)),
                        nullable=bool(item.get("nullable", False)),
                        default=item.get("default"),
                    )
                )
        clean = {k: v for k, v in data.items() if k != "fields"}
        return Detection(fields=parsed_fields, **clean)


@dataclass
class ContextSummary:
    name: str
    files_scanned: int = 0
    files_cached: int = 0
    commands: int = 0
    queries: int = 0
    events: int = 0
    handlers: int = 0

    def add(self, detection: Detection) -> None:
        if detection.kind == "command":
            self.commands += 1
        elif detection.kind == "query":
            self.queries += 1
        elif detection.kind == "event":
            self.events += 1
        elif detection.kind == "handler":
            self.handlers += 1

    @property
    def total(self) -> int:
        return self.commands + self.queries + self.events + self.handlers


@dataclass
class ScanReport:
    project: str
    project_root: Path
    detections: List[Detection] = field(default_factory=list)
    contexts: Dict[str, ContextSummary] = field(default_factory=dict)
    files_scanned: int = 0
    files_cached: int = 0
    files_skipped: int = 0
    errors: List[str] = field(default_factory=list)
    ignored: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # aggregation helpers
    # ------------------------------------------------------------------

    def add(self, detection: Detection) -> None:
        self.detections.append(detection)
        ctx = self.contexts.setdefault(detection.context, ContextSummary(name=detection.context))
        ctx.add(detection)

    def kinds(self) -> Dict[str, int]:
        out: Dict[str, int] = {"command": 0, "query": 0, "event": 0, "handler": 0}
        for d in self.detections:
            out[d.kind] = out.get(d.kind, 0) + 1
        return out

    def via(self) -> Dict[str, int]:
        out: Dict[str, int] = {"decorator": 0, "heuristic": 0}
        for d in self.detections:
            out[d.via] = out.get(d.via, 0) + 1
        return out

    def of_kind(self, kind: DetectionKind) -> List[Detection]:
        return [d for d in self.detections if d.kind == kind]

    def of_context(self, context: str) -> List[Detection]:
        return [d for d in self.detections if d.context == context]

    # ------------------------------------------------------------------
    # serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, object]:
        return {
            "project": self.project,
            "project_root": str(self.project_root),
            "summary": {
                "kinds": self.kinds(),
                "via": self.via(),
                "files_scanned": self.files_scanned,
                "files_cached": self.files_cached,
                "files_skipped": self.files_skipped,
                "errors": len(self.errors),
            },
            "contexts": [
                {
                    "name": c.name,
                    "files_scanned": c.files_scanned,
                    "files_cached": c.files_cached,
                    "total": c.total,
                    "commands": c.commands,
                    "queries": c.queries,
                    "events": c.events,
                    "handlers": c.handlers,
                }
                for c in sorted(self.contexts.values(), key=lambda x: x.name)
            ],
            "detections": [d.to_dict() for d in self.detections],
            "errors": list(self.errors),
            "ignored": list(self.ignored),
        }

    # ------------------------------------------------------------------
    # quick formatters
    # ------------------------------------------------------------------

    def format_text(self) -> str:
        kinds = self.kinds()
        via = self.via()
        lines = [
            f"swop scan — {self.project}",
            f"  files scanned: {self.files_scanned} (cached: {self.files_cached}, skipped: {self.files_skipped})",
            "  detections:",
            f"    {kinds['command']:>4} commands   ({via['decorator']} decorator / {via['heuristic']} heuristic overall)",
            f"    {kinds['query']:>4} queries",
            f"    {kinds['event']:>4} events",
            f"    {kinds['handler']:>4} handlers",
        ]
        if self.contexts:
            lines.append("  contexts:")
            for ctx in sorted(self.contexts.values(), key=lambda x: x.name):
                lines.append(
                    f"    {ctx.name:<20} "
                    f"cmd={ctx.commands} qry={ctx.queries} "
                    f"evt={ctx.events} hdl={ctx.handlers}"
                )
        if self.errors:
            lines.append(f"  errors: {len(self.errors)}")
            for err in self.errors[:5]:
                lines.append(f"    - {err}")
            if len(self.errors) > 5:
                lines.append(f"    ... and {len(self.errors) - 5} more")
        return "\n".join(lines)
