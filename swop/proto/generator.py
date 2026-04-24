"""
.proto generator.

Reads per-context YAML manifests written by :mod:`swop.manifests` and
renders a single ``.proto`` file per context under
``<out_dir>/<context>/v1/<context>.proto``.

Each file contains:

* One ``<Context>CommandService`` service with one RPC per command.
* One ``<Context>QueryService`` service with one RPC per query.
* One message per command / query request (mirroring the manifest
  fields) plus a generic ``<Cmd>Response`` / ``<Qry>Response`` message.
* One message per event (mirroring the manifest fields).

The emitted proto is intended as a starting contract; humans may refine
types the scanner could not resolve.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import yaml


PROTO_SYNTAX = "proto3"
PACKAGE_VERSION = "v1"


# ----------------------------------------------------------------------
# Result objects
# ----------------------------------------------------------------------


@dataclass
class ProtoFile:
    context: str
    path: Path
    commands: int = 0
    queries: int = 0
    events: int = 0

    @property
    def total_rpcs(self) -> int:
        return self.commands + self.queries


@dataclass
class ProtoGenerationResult:
    files: List[ProtoFile] = field(default_factory=list)
    out_dir: Optional[Path] = None
    warnings: List[str] = field(default_factory=list)

    def format(self) -> str:
        if not self.files:
            return "[PROTO] no .proto files written"
        lines = [f"[PROTO] wrote {len(self.files)} .proto file(s):"]
        for f in self.files:
            lines.append(
                f"  -> {f.path} "
                f"(cmds={f.commands} qrys={f.queries} evts={f.events})"
            )
        if self.warnings:
            lines.append(f"  warnings: {len(self.warnings)}")
            for w in self.warnings[:5]:
                lines.append(f"    - {w}")
            if len(self.warnings) > 5:
                lines.append(f"    ... and {len(self.warnings) - 5} more")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Type mapping (Python annotation → proto3 scalar or stub)
# ----------------------------------------------------------------------


_SIMPLE_PY_TO_PROTO: Dict[str, str] = {
    "str": "string",
    "string": "string",
    "bytes": "bytes",
    "bool": "bool",
    "boolean": "bool",
    "int": "int64",
    "integer": "int64",
    "float": "double",
    "number": "double",
    "double": "double",
    "Decimal": "string",
    "datetime": "google.protobuf.Timestamp",
    "date": "string",
    "UUID": "string",
    "uuid.UUID": "string",
    "Path": "string",
    "Any": "google.protobuf.Any",
}


_TIMESTAMP_IMPORT = 'import "google/protobuf/timestamp.proto";'
_ANY_IMPORT = 'import "google/protobuf/any.proto";'


@dataclass
class _ProtoType:
    proto: str
    repeated: bool = False
    well_known_import: Optional[str] = None
    stub: bool = False  # True when we invented a name the user must supply


def _map_python_type(annotation: str) -> _ProtoType:
    """Map a Python type annotation string to a proto scalar / message name."""
    if not annotation:
        return _ProtoType(proto="string", stub=True)
    raw = annotation.strip()
    # Strip Optional[...]
    m = re.match(r"Optional\[(.+)\]$", raw)
    if m:
        raw = m.group(1).strip()
    # Strip `X | None` unions — take the non-None branch.
    if "|" in raw:
        parts = [p.strip() for p in raw.split("|")]
        parts = [p for p in parts if p not in {"None", "NoneType"}]
        if parts:
            raw = parts[0]

    # Repeated: list[X], List[X], Sequence[X], Iterable[X], tuple[X, ...]
    repeated = False
    list_m = re.match(r"(?:list|List|Sequence|Iterable)\[(.+)\]$", raw)
    if list_m:
        repeated = True
        raw = list_m.group(1).strip()
    tup_m = re.match(r"(?:tuple|Tuple)\[(.+?)\s*,\s*\.\.\.\]$", raw)
    if tup_m:
        repeated = True
        raw = tup_m.group(1).strip()

    # Dict[K, V] → map<K, V>
    dict_m = re.match(r"(?:dict|Dict|Mapping)\[(.+?),\s*(.+)\]$", raw)
    if dict_m:
        key_type = _map_python_type(dict_m.group(1))
        val_type = _map_python_type(dict_m.group(2))
        return _ProtoType(
            proto=f"map<{key_type.proto}, {val_type.proto}>",
            well_known_import=val_type.well_known_import or key_type.well_known_import,
        )

    # Simple scalar.
    if raw in _SIMPLE_PY_TO_PROTO:
        proto = _SIMPLE_PY_TO_PROTO[raw]
        imp = None
        if proto.startswith("google.protobuf.Timestamp"):
            imp = _TIMESTAMP_IMPORT
        elif proto.startswith("google.protobuf.Any"):
            imp = _ANY_IMPORT
        return _ProtoType(proto=proto, repeated=repeated, well_known_import=imp)

    # JSON Schema fallback types (object, array) → safe proto stubs
    if raw == "object":
        return _ProtoType(proto="string", repeated=repeated, stub=True)
    if raw == "array":
        return _ProtoType(proto="string", repeated=True, stub=True)

    # Identifier → treat as a message name (user-defined type).
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", raw):
        return _ProtoType(proto=raw, repeated=repeated, stub=True)

    # Fallback: coerce to string and flag it.
    return _ProtoType(proto="string", repeated=repeated, stub=True)


# ----------------------------------------------------------------------
# Manifest discovery
# ----------------------------------------------------------------------


def _load_manifest(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def _iter_contexts(manifests_dir: Path) -> List[str]:
    if not manifests_dir.exists() or not manifests_dir.is_dir():
        return []
    return sorted(
        entry.name
        for entry in manifests_dir.iterdir()
        if entry.is_dir() and any(entry.glob("*.yml"))
    )


# ----------------------------------------------------------------------
# Public entry points
# ----------------------------------------------------------------------


def generate_proto_from_manifests(
    manifests_dir: Path,
    out_dir: Path,
) -> ProtoGenerationResult:
    """Walk ``manifests_dir`` and render one .proto file per context."""

    manifests_dir = Path(manifests_dir)
    out_dir = Path(out_dir)
    result = ProtoGenerationResult(out_dir=out_dir)

    for context in _iter_contexts(manifests_dir):
        ctx_dir = manifests_dir / context
        commands = _load_manifest(ctx_dir / "commands.yml")
        queries = _load_manifest(ctx_dir / "queries.yml")
        events = _load_manifest(ctx_dir / "events.yml")

        commands_list = commands.get("commands", []) if commands else []
        queries_list = queries.get("queries", []) if queries else []
        events_list = events.get("events", []) if events else []
        if not (commands_list or queries_list or events_list):
            continue

        rendered, warnings = render_proto_for_context(
            context=context,
            commands=commands_list,
            queries=queries_list,
            events=events_list,
        )
        target = out_dir / context / PACKAGE_VERSION / f"{_safe_ident(context)}.proto"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        result.warnings.extend(warnings)
        result.files.append(
            ProtoFile(
                context=context,
                path=target,
                commands=len(commands_list),
                queries=len(queries_list),
                events=len(events_list),
            )
        )

    return result


def render_proto_for_context(
    context: str,
    commands: Iterable[Dict[str, Any]],
    queries: Iterable[Dict[str, Any]],
    events: Iterable[Dict[str, Any]],
) -> Tuple[str, List[str]]:
    """Render one ``.proto`` file body for a single context."""

    commands = list(commands)
    queries = list(queries)
    events = list(events)

    package = f"{_safe_ident(context)}.{PACKAGE_VERSION}"
    warnings: List[str] = []
    imports: set[str] = set()
    messages: List[str] = []
    rendered_type_names: Set[str] = set()
    known_types = _collect_known_types(commands, queries, events)
    known_type_names = set(known_types)

    for qry in queries:
        response = qry.get("response") or {}
        response_type = response.get("type")
        response_fields = response.get("fields") or []
        if response_type and response_fields:
            known_type_names.add(str(response_type))

    for type_name, type_def in known_types.items():
        rendered, type_warn = _render_type_definition(
            type_def,
            imports,
            context,
            known_type_names,
        )
        warnings.extend(type_warn)
        if rendered:
            messages.append(rendered)
            rendered_type_names.add(type_name)

    # ---------------- commands ----------------
    cmd_rpcs: List[str] = []
    for cmd in commands:
        name = cmd.get("name", "")
        if not name:
            continue
        req_name = f"{name}Request"
        res_name = f"{name}Response"
        req_body, req_warn = _render_message(
            req_name, cmd.get("fields", []), imports, context, known_type_names
        )
        warnings.extend(req_warn)
        messages.append(req_body)
        messages.append(_render_command_response(res_name, cmd.get("emits", [])))
        cmd_rpcs.append(f"  rpc {name}({req_name}) returns ({res_name});")

    # ---------------- queries -----------------
    qry_rpcs: List[str] = []
    for qry in queries:
        name = qry.get("name", "")
        if not name:
            continue
        req_name = f"{name}Request"
        res_name = f"{name}Response"
        req_body, req_warn = _render_message(
            req_name, qry.get("fields", []), imports, context, known_type_names
        )
        warnings.extend(req_warn)
        messages.append(req_body)
        response = qry.get("response") or {}
        response_type = str(response.get("type", "") or "")
        response_fields = response.get("fields") or []
        if response_type and response_fields and response_type not in rendered_type_names:
            response_body, response_warn = _render_message(
                response_type,
                response_fields,
                imports,
                context,
                known_type_names,
            )
            warnings.extend(response_warn)
            messages.append(response_body)
            rendered_type_names.add(response_type)
        messages.append(_render_query_response(res_name, response_type or None))
        qry_rpcs.append(f"  rpc {name}({req_name}) returns ({res_name});")

    # ---------------- events ------------------
    for evt in events:
        name = evt.get("name", "")
        if not name:
            continue
        body, evt_warn = _render_message(
            name,
            evt.get("fields", []),
            imports,
            context,
            known_type_names,
        )
        warnings.extend(evt_warn)
        messages.append(body)

    # ---------------- services ----------------
    services: List[str] = []
    if cmd_rpcs:
        services.append(
            f"service {_service_name(context, 'Command')} {{\n"
            + "\n".join(cmd_rpcs)
            + "\n}"
        )
    if qry_rpcs:
        services.append(
            f"service {_service_name(context, 'Query')} {{\n"
            + "\n".join(qry_rpcs)
            + "\n}"
        )

    # ---------------- assemble ----------------
    header = [
        f"// Generated by swop gen proto. Do not edit by hand.",
        f"// Context: {context}",
        f'syntax = "{PROTO_SYNTAX}";',
        "",
        f"package {package};",
    ]
    import_lines = sorted(imports)
    if import_lines:
        header.append("")
        header.extend(import_lines)

    body_parts = []
    if services:
        body_parts.append("\n\n".join(services))
    if messages:
        body_parts.append("\n\n".join(messages))

    text = "\n".join(header) + "\n\n" + "\n\n".join(body_parts).rstrip() + "\n"
    return text, warnings


# ----------------------------------------------------------------------
# Rendering helpers
# ----------------------------------------------------------------------


def _render_message(
    name: str,
    fields: Iterable[Dict[str, Any]],
    imports: set,
    context: str,
    known_type_names: Optional[Set[str]] = None,
) -> Tuple[str, List[str]]:
    """Render one message block; accumulate proto imports in ``imports``."""
    warnings: List[str] = []
    known_type_names = known_type_names or set()
    lines = [f"message {name} {{"]
    index = 1
    for field_def in fields or []:
        fname = field_def.get("name")
        if not fname:
            continue
        proto_ident = _safe_ident(fname)
        annotation = field_def.get("type", "")
        mapped = _map_python_type(annotation)
        if mapped.stub and mapped.proto not in known_type_names:
            warnings.append(
                f"{context}.{name}.{proto_ident}: "
                f"type {annotation!r} mapped to {mapped.proto!r} "
                f"(review the generated message)"
            )
        if mapped.well_known_import:
            imports.add(mapped.well_known_import)
        is_map = mapped.proto.startswith("map<")
        is_nullable = bool(field_def.get("nullable", False))
        optional_prefix = "optional " if is_nullable and not mapped.repeated and not is_map else ""
        prefix = "repeated " if mapped.repeated else ""
        lines.append(f"  {optional_prefix}{prefix}{mapped.proto} {proto_ident} = {index};")
        index += 1
    if index == 1:
        lines.append("  // no fields detected from the manifest")
    lines.append("}")
    return "\n".join(lines), warnings


def _render_command_response(name: str, emits: List[str]) -> str:
    comment = (
        f"  // Emits: {', '.join(emits)}\n" if emits else ""
    )
    return (
        f"message {name} {{\n"
        f"{comment}"
        f"  string id = 1;\n"
        f"  repeated string emitted_events = 2;\n"
        f"}}"
    )


def _render_query_response(name: str, result_type: Optional[str] = None) -> str:
    if result_type:
        return (
            f"message {name} {{\n"
            f"  {result_type} result = 1;\n"
            f"}}"
        )
    return (
        f"message {name} {{\n"
        f"  // The query result is serialised into `result_json` until a\n"
        f"  // bespoke read-model message is declared for this query.\n"
        f"  string result_json = 1;\n"
        f"}}"
    )


def _collect_known_types(
    commands: Iterable[Dict[str, Any]],
    queries: Iterable[Dict[str, Any]],
    events: Iterable[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    known: Dict[str, Dict[str, Any]] = {}
    for entry in list(commands) + list(queries) + list(events):
        for type_def in entry.get("types", []) or []:
            name = str(type_def.get("name", "") or "")
            if name:
                known.setdefault(name, type_def)
    return known


def _render_type_definition(
    type_def: Dict[str, Any],
    imports: set,
    context: str,
    known_type_names: Set[str],
) -> Tuple[str, List[str]]:
    kind = str(type_def.get("kind", "") or "")
    name = str(type_def.get("name", "") or "")
    if not kind or not name:
        return "", []
    if kind == "enum":
        return _render_enum(name, type_def.get("values", [])), []
    if kind == "message":
        return _render_message(name, type_def.get("fields", []), imports, context, known_type_names)
    return "", []


def _render_enum(name: str, values: Iterable[Dict[str, Any]]) -> str:
    lines = [f"enum {name} {{"]
    index = 0
    seen: Set[str] = set()
    for item in values or []:
        member_name = _safe_ident(str(item.get("name", "") or "")).upper()
        if not member_name or member_name in seen:
            continue
        seen.add(member_name)
        lines.append(f"  {member_name} = {index};")
        index += 1
    if index == 0:
        lines.append(f"  {_safe_ident(name).upper()}_UNSPECIFIED = 0;")
    lines.append("}")
    return "\n".join(lines)


def _service_name(context: str, suffix: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", context)
    camel = "".join(part[:1].upper() + part[1:] for part in parts if part)
    return f"{camel}{suffix}Service"


_SAFE_RX = re.compile(r"[^a-zA-Z0-9_]+")


def _safe_ident(name: str) -> str:
    cleaned = _SAFE_RX.sub("_", name).strip("_")
    if not cleaned:
        return "_"
    if cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned
