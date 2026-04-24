"""
CQRS project scanner.

Given a :class:`~swop.config.SwopConfig`, walks every source root, parses
each Python file, and extracts a :class:`ScanReport`. Detection logic:

1. **Decorator detection** — any class decorated with ``@command``,
   ``@query``, ``@event`` or ``@handler`` (matched by bare name or
   attribute access such as ``swop.command``). Confidence 1.0.

2. **Heuristic detection** — classes whose name ends with one of
   ``Command``, ``Cmd``, ``Query``, ``Qry``, ``Event``, ``Evt``,
   ``Handler``; or whose direct base class is one of ``BaseCommand``,
   ``BaseQuery``, ``BaseEvent``, ``BaseHandler`` (or the same names
   without the ``Base`` prefix). Confidence 0.7–0.9.

The scanner never imports user code, so even projects with broken
imports can be scanned safely.
"""

from __future__ import annotations

import ast
import fnmatch
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from swop.config import BoundedContextConfig, SwopConfig, load_config
from swop.scan.cache import FingerprintCache
from swop.scan.report import Detection, FieldDef, ScanReport


# ----------------------------------------------------------------------
# Heuristic tables
# ----------------------------------------------------------------------


_DECORATOR_KINDS = {
    "command": "command",
    "query": "query",
    "event": "event",
    "handler": "handler",
}

_NAME_SUFFIX_KINDS: List[Tuple[str, str]] = [
    ("Command", "command"),
    ("Cmd", "command"),
    ("Query", "query"),
    ("Qry", "query"),
    ("Event", "event"),
    ("Evt", "event"),
    ("Handler", "handler"),
]

_BASE_KINDS: Dict[str, str] = {
    "BaseCommand": "command",
    "Command": "command",
    "CommandBase": "command",
    "BaseQuery": "query",
    "Query": "query",
    "QueryBase": "query",
    "BaseEvent": "event",
    "Event": "event",
    "EventBase": "event",
    "DomainEvent": "event",
    "BaseHandler": "handler",
    "Handler": "handler",
    "CommandHandler": "handler",
    "QueryHandler": "handler",
}


_PY_SUFFIX = ".py"


# ----------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------


def _scan_file(
    py_path: Path,
    project_root: Path,
    config: SwopConfig,
    contexts: Dict[str, BoundedContextConfig],
    cache: Optional[FingerprintCache],
    incremental: bool,
    report: ScanReport,
) -> None:
    rel = py_path.relative_to(project_root)
    rel_str = rel.as_posix()

    context = _context_for_path(rel_str, contexts, project_root)
    if context is None:
        report.ignored.append(rel_str)
        return

    ctx_cfg = config.context(context)
    if ctx_cfg is not None and ctx_cfg.external:
        report.ignored.append(rel_str)
        return

    try:
        text = py_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        report.errors.append(f"{rel_str}: read failed ({exc})")
        report.files_skipped += 1
        return

    fingerprint = FingerprintCache.fingerprint(text)

    cached: Optional[List[Detection]] = None
    if cache is not None and incremental:
        cached = cache.get(rel_str, fingerprint)

    summary = report.contexts.setdefault(context, _new_ctx_summary(context))

    if cached is not None:
        report.files_cached += 1
        summary.files_cached += 1
        for det in cached:
            report.add(det)
        return

    try:
        tree = ast.parse(text, filename=str(py_path))
    except SyntaxError as exc:
        report.errors.append(f"{rel_str}: parse failed ({exc.msg} line {exc.lineno})")
        report.files_skipped += 1
        if cache is not None:
            cache.drop(rel_str)
        return

    detections = _extract_detections(tree, py_path, rel_str, context, fingerprint)

    report.files_scanned += 1
    summary.files_scanned += 1
    for det in detections:
        report.add(det)

    if cache is not None:
        cache.put(rel_str, fingerprint, detections)


def scan_project(
    config: Optional[SwopConfig] = None,
    *,
    root: Optional[Path] = None,
    incremental: bool = True,
    cache: Optional[FingerprintCache] = None,
) -> ScanReport:
    """Scan the project described by ``config`` and return a report."""

    if config is None:
        config = load_config((Path(root) / "swop.yaml") if root else None)

    project_root = config.project_root
    report = ScanReport(project=config.project, project_root=project_root)

    if cache is None and incremental:
        cache = FingerprintCache(config.state_path / "cache" / "scan.json")
    if cache is not None and incremental:
        cache.load()

    excludes = tuple(config.exclude)
    contexts = _resolve_contexts(config)

    discovered_keys: List[str] = []

    for py_path in _iter_python_files(project_root, config.source_roots, excludes):
        rel_str = py_path.relative_to(project_root).as_posix()
        discovered_keys.append(rel_str)
        _scan_file(py_path, project_root, config, contexts, cache, incremental, report)

    if cache is not None and incremental:
        cache.prune(discovered_keys)
        cache.save()

    return report


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _new_ctx_summary(name: str):
    from swop.scan.report import ContextSummary

    return ContextSummary(name=name)


def _resolve_contexts(config: SwopConfig) -> List[BoundedContextConfig]:
    """Return contexts sorted by source specificity (longest first)."""
    return sorted(
        config.bounded_contexts,
        key=lambda c: len(Path(c.source).parts),
        reverse=True,
    )


def _iter_python_files(
    root: Path,
    source_roots: Iterable[str],
    excludes: Iterable[str],
) -> Iterable[Path]:
    seen: set[Path] = set()
    source_list = list(source_roots) or ["."]
    for rel in source_list:
        base = (root / rel).resolve()
        if not base.exists() or not base.is_dir():
            continue
        for path in base.rglob("*" + _PY_SUFFIX):
            if not path.is_file():
                continue
            try:
                relative = path.relative_to(root)
            except ValueError:
                continue
            rel_str = relative.as_posix()
            if _matches_any(rel_str, excludes):
                continue
            if path in seen:
                continue
            seen.add(path)
            yield path


def _matches_any(path: str, patterns: Iterable[str]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
        # Also match by any path segment (e.g. "tests" should skip any tests/ dir).
        if pattern.strip("*/") and pattern.strip("*/") in path.split("/"):
            return True
    return False


def _context_for_path(
    rel_path: str,
    contexts: List[BoundedContextConfig],
    project_root: Path,
) -> Optional[str]:
    if not contexts:
        # When no bounded_contexts are declared, use the first path segment
        # as context so that everything is classified rather than ignored.
        parts = rel_path.split("/")
        if not parts:
            return None
        return parts[0] or "default"

    for ctx in contexts:
        src = ctx.source.replace("\\", "/").rstrip("/")
        if not src:
            continue
        if rel_path == src or rel_path.startswith(src + "/"):
            return ctx.name
    return None


# ----------------------------------------------------------------------
# AST extraction
# ----------------------------------------------------------------------


def _extract_detections(
    tree: ast.AST,
    path: Path,
    rel_path: str,
    context: str,
    fingerprint: Optional[str],
) -> List[Detection]:
    module = _module_name_from_path(rel_path)
    out: List[Detection] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        detection = _classify(node, path, rel_path, module, context)
        if detection is None:
            continue
        detection.file_fingerprint = fingerprint
        if detection.kind in {"command", "query", "event"}:
            detection.fields = _extract_fields(node)
        if detection.kind == "handler" and not detection.handler_method:
            detection.handler_method = _handler_method_name(node)
        out.append(detection)
    return out


def _module_name_from_path(rel_path: str) -> str:
    without_suffix = rel_path[:-len(_PY_SUFFIX)] if rel_path.endswith(_PY_SUFFIX) else rel_path
    parts = [p for p in without_suffix.split("/") if p]
    # Drop a trailing "__init__" segment so that e.g. ``pkg/__init__.py`` becomes ``pkg``.
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) or "__root__"


def _decorator_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return ""


def _base_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _extract_decorator_emits(call: ast.Call) -> List[str]:
    emits: List[str] = []
    for kw in call.keywords:
        if kw.arg != "emits":
            continue
        if isinstance(kw.value, (ast.List, ast.Tuple, ast.Set)):
            for elt in kw.value.elts:
                if isinstance(elt, ast.Name):
                    emits.append(elt.id)
                elif isinstance(elt, ast.Attribute):
                    emits.append(elt.attr)
                elif isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    emits.append(elt.value)
    return emits


def _extract_decorator_context(call: ast.Call) -> Optional[str]:
    if call.args:
        first = call.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    for kw in call.keywords:
        if kw.arg == "context" and isinstance(kw.value, ast.Constant):
            value = kw.value.value
            if isinstance(value, str):
                return value
    return None


def _extract_handler_target(call: ast.Call) -> Optional[str]:
    if call.args:
        first = call.args[0]
        if isinstance(first, ast.Name):
            return first.id
        if isinstance(first, ast.Attribute):
            return first.attr
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    return None


def _classify_decorator(
    node: ast.ClassDef,
    decorator_node: ast.expr,
    decorator_names: List[str],
    bases: List[str],
    qualname: str,
    module: str,
    context: str,
    rel_path: str,
) -> Optional[Detection]:
    name = _decorator_name(decorator_node)
    if name not in _DECORATOR_KINDS:
        return None
    kind = _DECORATOR_KINDS[name]
    emits: List[str] = []
    handles: Optional[str] = None
    deco_context: Optional[str] = None
    if isinstance(decorator_node, ast.Call):
        emits = _extract_decorator_emits(decorator_node)
        if kind == "handler":
            handles = _extract_handler_target(decorator_node)
        else:
            deco_context = _extract_decorator_context(decorator_node)
    resolved_context = deco_context or context
    return Detection(
        kind=kind,
        name=node.name,
        qualname=qualname,
        module=module,
        context=resolved_context,
        source_file=rel_path,
        source_line=node.lineno,
        via="decorator",
        confidence=1.0,
        bases=bases,
        decorators=decorator_names,
        handles=handles,
        emits=emits,
        reason=f"@{name}",
    )


def _classify_heuristic(
    node: ast.ClassDef,
    decorator_names: List[str],
    bases: List[str],
    qualname: str,
    module: str,
    context: str,
    rel_path: str,
) -> Optional[Detection]:
    suffix_kind = _kind_by_suffix(node.name)
    base_kind = _kind_by_base(bases)

    if suffix_kind and base_kind and suffix_kind == base_kind:
        confidence = 0.9
        reason = f"name suffix + base ({','.join(bases)})"
        kind = suffix_kind
    elif base_kind:
        confidence = 0.8
        reason = f"base class ({','.join(bases)})"
        kind = base_kind
    elif suffix_kind:
        confidence = 0.7
        reason = f"name suffix {suffix_kind!r}"
        kind = suffix_kind
    else:
        return None

    handles: Optional[str] = None
    if kind == "handler":
        handles = _handler_target_from_method(node)

    return Detection(
        kind=kind,
        name=node.name,
        qualname=qualname,
        module=module,
        context=context,
        source_file=rel_path,
        source_line=node.lineno,
        via="heuristic",
        confidence=confidence,
        bases=bases,
        decorators=decorator_names,
        handles=handles,
        emits=[],
        reason=reason,
    )


def _classify(
    node: ast.ClassDef,
    path: Path,
    rel_path: str,
    module: str,
    context: str,
) -> Optional[Detection]:
    decorator_names = [_decorator_name(d) for d in node.decorator_list]
    decorator_names = [name for name in decorator_names if name]

    bases = [_base_name(b) for b in node.bases if _base_name(b)]
    qualname = f"{module}.{node.name}" if module != "__root__" else node.name

    for decorator_node in node.decorator_list:
        det = _classify_decorator(
            node, decorator_node, decorator_names, bases, qualname, module, context, rel_path
        )
        if det is not None:
            return det

    return _classify_heuristic(
        node, decorator_names, bases, qualname, module, context, rel_path
    )


def _kind_by_suffix(name: str) -> Optional[str]:
    for suffix, kind in _NAME_SUFFIX_KINDS:
        if name.endswith(suffix) and name != suffix:
            return kind
    return None


def _kind_by_base(bases: Iterable[str]) -> Optional[str]:
    for base in bases:
        if base in _BASE_KINDS:
            return _BASE_KINDS[base]
    return None


def _handler_target_from_method(node: ast.ClassDef) -> Optional[str]:
    """Infer which command/query a handler handles from the type of its first arg."""
    for stmt in node.body:
        if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if stmt.name not in {"handle", "__call__", "execute", "run"}:
            continue
        args = stmt.args.args
        # skip `self` / `cls`
        payload_args = [a for a in args if a.arg not in {"self", "cls"}]
        if not payload_args:
            continue
        annotation = payload_args[0].annotation
        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Attribute):
            return annotation.attr
        if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
            return annotation.value.id
    return None


def _handler_method_name(node: ast.ClassDef) -> Optional[str]:
    """Return the name of the first handler-method in a handler class."""
    for stmt in node.body:
        if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if stmt.name in {"handle", "__call__", "execute", "run"}:
            return stmt.name
    return None


def _extract_ann_field(stmt: ast.AnnAssign, seen: set[str]) -> Optional[FieldDef]:
    if not isinstance(stmt.target, ast.Name):
        return None
    name = stmt.target.id
    if name.startswith("_") or name in seen:
        return None
    type_str = _unparse(stmt.annotation) if stmt.annotation is not None else ""
    default = _render_default(stmt.value) if stmt.value is not None else None
    nullable = _annotation_is_optional(stmt.annotation)
    required = default is None and not nullable
    seen.add(name)
    return FieldDef(
        name=name,
        type=type_str,
        required=required,
        nullable=nullable,
        default=default,
    )


def _extract_plain_field(stmt: ast.Assign, seen: set[str]) -> Iterator[FieldDef]:
    for target in stmt.targets:
        if not isinstance(target, ast.Name):
            continue
        name = target.id
        if name.startswith("_") or name in seen or name.isupper():
            continue
        default = _render_default(stmt.value)
        seen.add(name)
        yield FieldDef(name=name, type="", required=False, nullable=False, default=default)


def _extract_fields(node: ast.ClassDef) -> List[FieldDef]:
    """Extract attribute declarations from a dataclass / plain class body."""
    out: List[FieldDef] = []
    seen: set[str] = set()
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign):
            field = _extract_ann_field(stmt, seen)
            if field:
                out.append(field)
        elif isinstance(stmt, ast.Assign):
            out.extend(_extract_plain_field(stmt, seen))
    return out


def _unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - defensive, very old Python versions
        return ""


def _render_default(node: Optional[ast.AST]) -> Optional[str]:
    if node is None:
        return None
    if isinstance(node, ast.Constant):
        return repr(node.value)
    return _unparse(node)


def _annotation_is_optional(node: Optional[ast.AST]) -> bool:
    """Return True for ``Optional[X]``, ``X | None`` or similar shapes."""
    if node is None:
        return False
    # Optional[...] or typing.Optional[...]
    if isinstance(node, ast.Subscript):
        value = node.value
        name = ""
        if isinstance(value, ast.Name):
            name = value.id
        elif isinstance(value, ast.Attribute):
            name = value.attr
        if name == "Optional":
            return True
    # X | None in PEP 604 union syntax.
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        for side in (node.left, node.right):
            if isinstance(side, ast.Constant) and side.value is None:
                return True
            if isinstance(side, ast.Name) and side.id == "None":
                return True
    return False
