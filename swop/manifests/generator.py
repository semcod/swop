"""
Per-context manifest generator.

For every bounded context that has at least one detection of the given
kind, write ``<out_dir>/<context>/<kind>s.yml`` with a deterministic
shape that downstream generators (proto, gRPC, services) can consume
without re-parsing Python source.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import yaml

from swop.config import SwopConfig
from swop.scan.report import Detection, ScanReport

MANIFEST_VERSION = 1

# Filenames per kind.
KIND_FILENAMES = {
    "command": "commands.yml",
    "query": "queries.yml",
    "event": "events.yml",
}

# Plural block name in the YAML body.
KIND_BLOCK = {
    "command": "commands",
    "query": "queries",
    "event": "events",
}

IGNORED_TYPE_NAMES = {
    "Any",
    "Dict",
    "FrozenSet",
    "Iterable",
    "Iterator",
    "List",
    "Literal",
    "Mapping",
    "None",
    "NoneType",
    "Optional",
    "Sequence",
    "Set",
    "Tuple",
}

IGNORED_FIELD_TYPES = {
    "Any",
    "Decimal",
    "Path",
    "UUID",
    "bool",
    "boolean",
    "bytes",
    "date",
    "datetime",
    "double",
    "float",
    "int",
    "integer",
    "number",
    "object",
    "str",
    "string",
    "uuid",
}

TYPE_NAME_RX = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


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
            path = ctx_dir / KIND_FILENAMES[kind]
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
    cache: Dict[str, Any] = {
        "modules": {},
        "imports": {},
        "classes": {},
        "search": {},
    }
    block = KIND_BLOCK[kind]
    entries = [
        _render_entry(d, kind, handler_index, config, cache)
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
    cache: Dict[str, Any],
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
            if kind == "query":
                response = _render_query_response_metadata(handler, config, cache)
                if response is not None:
                    entry["response"] = response

    type_defs = _collect_supporting_types(
        detection.source_file,
        entry["fields"],
        config,
        cache,
    )
    response = entry.get("response")
    if isinstance(response, dict):
        type_defs.extend(response.pop("types", []))
    if type_defs:
        entry["types"] = _dedupe_type_defs(type_defs)

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


def _render_query_response_metadata(
    handler: Detection,
    config: SwopConfig,
    cache: Dict[str, Any],
) -> Optional[Dict[str, object]]:
    source_path = config.project_root / handler.source_file
    class_node = _find_class_in_module(source_path, handler.name, cache)
    if class_node is None:
        return None
    method_name = handler.handler_method or "handle"
    return_type = _find_handler_return_type(class_node, method_name)
    if not return_type:
        return None
    root_name = _first_custom_type_name(return_type)
    if not root_name:
        return {"type": return_type}
    resolved = _resolve_class_definition(root_name, source_path, config.project_root, cache)
    if resolved is None:
        return {"type": root_name}
    response_path, response_class = resolved
    if _is_enum_class(response_class):
        return {
            "type": root_name,
            "types": [_render_enum_type(root_name, response_class)],
        }
    response_fields = _extract_class_fields(response_class)
    response_types = _collect_supporting_types_from_fields(
        response_path,
        response_fields,
        config,
        cache,
        seen={root_name},
    )
    return {
        "type": root_name,
        "fields": response_fields,
        "types": response_types,
    }


def _collect_supporting_types(
    source_file: str,
    fields: Iterable[Dict[str, object]],
    config: SwopConfig,
    cache: Dict[str, Any],
) -> List[Dict[str, object]]:
    source_path = config.project_root / source_file
    return _collect_supporting_types_from_fields(source_path, fields, config, cache, seen=set())


def _collect_supporting_types_from_fields(
    source_path: Path,
    fields: Iterable[Dict[str, object]],
    config: SwopConfig,
    cache: Dict[str, Any],
    seen: Set[str],
) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for field in fields:
        annotation = str(field.get("type", "") or "")
        for symbol in _annotation_type_names(annotation):
            if symbol in seen:
                continue
            resolved = _resolve_class_definition(symbol, source_path, config.project_root, cache)
            if resolved is None:
                continue
            resolved_path, resolved_class = resolved
            seen.add(symbol)
            if _is_enum_class(resolved_class):
                out.append(_render_enum_type(symbol, resolved_class))
                continue
            nested_fields = _extract_class_fields(resolved_class)
            out.append({"kind": "message", "name": symbol, "fields": nested_fields})
            out.extend(
                _collect_supporting_types_from_fields(
                    resolved_path,
                    nested_fields,
                    config,
                    cache,
                    seen,
                )
            )
    return out


def _annotation_type_names(annotation: str) -> List[str]:
    names: List[str] = []
    for token in TYPE_NAME_RX.findall(annotation or ""):
        if token in IGNORED_TYPE_NAMES or token in IGNORED_FIELD_TYPES:
            continue
        if not token[:1].isupper():
            continue
        names.append(token)
    return names


def _first_custom_type_name(annotation: str) -> Optional[str]:
    names = _annotation_type_names(annotation)
    return names[0] if names else None


def _find_handler_return_type(class_node: ast.ClassDef, method_name: str) -> Optional[str]:
    for stmt in class_node.body:
        if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if stmt.name != method_name:
            continue
        if stmt.returns is None:
            return None
        try:
            return ast.unparse(stmt.returns)
        except Exception:
            return None
    return None


def _module_ast(path: Path, cache: Dict[str, Any]) -> Optional[ast.Module]:
    modules = cache["modules"]
    if path in modules:
        return modules[path]
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        modules[path] = None
        return None
    try:
        module = ast.parse(text, filename=str(path))
    except SyntaxError:
        modules[path] = None
        return None
    modules[path] = module
    return module


def _module_classes(path: Path, cache: Dict[str, Any]) -> Dict[str, ast.ClassDef]:
    classes = cache["classes"]
    if path in classes:
        return classes[path]
    module = _module_ast(path, cache)
    if module is None:
        classes[path] = {}
        return classes[path]
    index = {
        node.name: node
        for node in module.body
        if isinstance(node, ast.ClassDef)
    }
    classes[path] = index
    return index


def _find_class_in_module(path: Path, class_name: str, cache: Dict[str, Any]) -> Optional[ast.ClassDef]:
    return _module_classes(path, cache).get(class_name)


def _module_imports(path: Path, project_root: Path, cache: Dict[str, Any]) -> Dict[str, List[Path]]:
    imports = cache["imports"]
    if path in imports:
        return imports[path]
    module = _module_ast(path, cache)
    mapping: Dict[str, List[Path]] = {}
    if module is None:
        imports[path] = mapping
        return mapping
    for stmt in module.body:
        if isinstance(stmt, ast.ImportFrom):
            targets = _resolve_import_module_paths(path, project_root, stmt.module, stmt.level)
            if not targets:
                continue
            for alias in stmt.names:
                if alias.name == "*":
                    continue
                mapping.setdefault(alias.asname or alias.name, []).extend(targets)
        elif isinstance(stmt, ast.Import):
            for alias in stmt.names:
                name = alias.asname or alias.name.split(".")[-1]
                mapping.setdefault(name, []).extend(
                    _resolve_import_module_paths(path, project_root, alias.name, 0)
                )
    imports[path] = mapping
    return mapping


def _resolve_import_module_paths(
    source_path: Path,
    project_root: Path,
    module_name: Optional[str],
    level: int,
) -> List[Path]:
    bases: List[Path] = []
    if level > 0:
        base = source_path.parent
        for _ in range(level - 1):
            base = base.parent
        bases.append(base)
    elif module_name:
        bases.append(project_root.joinpath(*module_name.split(".")))
    if level > 0 and module_name:
        rel_base = bases[0].joinpath(*module_name.split("."))
        bases = [rel_base]
    candidates: List[Path] = []
    for base in bases:
        file_candidate = base.with_suffix(".py")
        init_candidate = base / "__init__.py"
        if file_candidate.exists():
            candidates.append(file_candidate)
        if init_candidate.exists():
            candidates.append(init_candidate)
    return candidates


def _resolve_class_definition(
    class_name: str,
    source_path: Path,
    project_root: Path,
    cache: Dict[str, Any],
) -> Optional[Tuple[Path, ast.ClassDef]]:
    local = _find_class_in_module(source_path, class_name, cache)
    if local is not None:
        return source_path, local
    for candidate in _module_imports(source_path, project_root, cache).get(class_name, []):
        target = _find_class_in_module(candidate, class_name, cache)
        if target is not None:
            return candidate, target
    for candidate in _search_class_files(class_name, project_root, cache):
        target = _find_class_in_module(candidate, class_name, cache)
        if target is not None:
            return candidate, target
    return None


def _search_class_files(class_name: str, project_root: Path, cache: Dict[str, Any]) -> List[Path]:
    search = cache["search"]
    if class_name in search:
        return search[class_name]
    matches: List[Path] = []
    needle = f"class {class_name}"
    for candidate in project_root.rglob("*.py"):
        if "__pycache__" in candidate.parts:
            continue
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if needle in text:
            matches.append(candidate)
    search[class_name] = matches
    return matches


def _is_enum_class(node: ast.ClassDef) -> bool:
    for base in node.bases:
        name = _expr_name(base)
        if name in {"Enum", "IntEnum", "StrEnum"}:
            return True
    return False


def _render_enum_type(name: str, node: ast.ClassDef) -> Dict[str, object]:
    values: List[Dict[str, object]] = []
    for stmt in node.body:
        if not isinstance(stmt, ast.Assign):
            continue
        if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
            continue
        member_name = stmt.targets[0].id
        member_value = None
        if isinstance(stmt.value, ast.Constant):
            member_value = stmt.value.value
        values.append({"name": member_name, "value": member_value})
    return {"kind": "enum", "name": name, "values": values}


def _extract_class_fields(node: ast.ClassDef) -> List[Dict[str, object]]:
    seen: Set[str] = set()
    fields: List[Dict[str, object]] = []
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            name = stmt.target.id
            if name.startswith("_") or name in seen:
                continue
            default = _render_default(stmt.value) if stmt.value is not None else None
            required = default is None and not _annotation_is_optional(stmt.annotation)
            seen.add(name)
            fields.append(
                {
                    "name": name,
                    "type": _unparse(stmt.annotation) if stmt.annotation is not None else "",
                    "required": required,
                    **({"default": default} if default is not None else {}),
                }
            )
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if not isinstance(target, ast.Name):
                    continue
                name = target.id
                if name.startswith("_") or name in seen or name.isupper():
                    continue
                seen.add(name)
                fields.append(
                    {
                        "name": name,
                        "required": False,
                        "default": _render_default(stmt.value),
                    }
                )
    return fields


def _expr_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return _expr_name(node.value)
    return ""


def _unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _render_default(node: Optional[ast.AST]) -> Optional[str]:
    if node is None:
        return None
    if isinstance(node, ast.Constant):
        return repr(node.value)
    return _unparse(node)


def _annotation_is_optional(node: Optional[ast.AST]) -> bool:
    if node is None:
        return False
    if isinstance(node, ast.Subscript):
        name = _expr_name(node.value)
        if name == "Optional":
            return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        for side in (node.left, node.right):
            if isinstance(side, ast.Constant) and side.value is None:
                return True
            if isinstance(side, ast.Name) and side.id == "None":
                return True
    return False


def _dedupe_type_defs(type_defs: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    by_name: Dict[Tuple[str, str], Dict[str, object]] = {}
    for item in type_defs:
        kind = str(item.get("kind", ""))
        name = str(item.get("name", ""))
        if not kind or not name:
            continue
        by_name.setdefault((kind, name), item)
    return list(by_name.values())
