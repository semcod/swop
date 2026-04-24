"""Cross-check contract enums against Pydantic Literal annotations.

A recurring class of bugs when authoring CQRS contracts by hand is that
the JSON ``enum`` in a contract drifts away from the ``Literal[...]`` used
in the Pydantic model that actually implements the request/response.

Concrete c2004 example (2026-04-24, ADR-012 Wave 2):

* ``contracts/GetServiceIdHealth.query.json`` declared
  ``output.checks.database.enum = ["ok", "error"]``
* The Pydantic model ``_ServiceIdHealthChecks.database`` was typed
  ``Literal["ok", "error"]``
* The route handler assigned ``db_status = "degraded"`` under a
  ``# type: ignore`` comment — which Pydantic rejected at runtime.

None of those three artefacts were authored by swop, and each of them
was individually consistent. The bug was a **cross-layer** drift:
``error`` handler intent < Pydantic type < contract enum. Runtime
validation surfaced it only when the health probe triggered the
``degraded`` branch.

This validator catches that class of drift at registry time by

1. parsing every contract's ``layers.python`` file with :mod:`ast`
   (no import, no Pydantic required as swop dependency);
2. collecting every ``Literal[...]`` annotation whose string arguments
   look enum-like (only string literals);
3. for every contract field carrying an ``enum`` key, looking up a
   matching Pydantic model field by name (either the contract field's
   own name, or a dotted ``parent.child`` path inside nested objects);
4. reporting a drift error if the Literal's value set is not equal
   to the contract's enum set.

Design notes
------------

The cross-check is **best effort**:

* If ``layers.python`` has no ``::ClassName`` suffix we scan every class
  in the file. A match on any class wins.
* If no Pydantic field with a matching name is found, we silently skip
  the contract field. That avoids a flood of warnings when a contract
  field lives outside the Pydantic model's surface (e.g. ``success``
  boolean added by the response factory).
* ``Literal`` detection accepts ``typing.Literal``, ``Literal`` imported
  bare, and handles ``Literal["a", "b"] | None`` unions.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from swop.registry.loader import Contract


@dataclass
class CrossCheckResult:
    ok: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def format(self) -> str:
        parts: List[str] = []
        if self.errors:
            parts.append("errors: " + "; ".join(self.errors))
        if self.warnings:
            parts.append("warnings: " + "; ".join(self.warnings))
        return " | ".join(parts) if parts else "ok"


# ---------------------------------------------------------------------------
# Pydantic model extraction (ast-based, no runtime import)
# ---------------------------------------------------------------------------


def _extract_literal_values(annotation: ast.AST) -> Optional[Set[str]]:
    """Return the set of string values declared in ``Literal[...]`` or ``None``
    if *annotation* does not wrap a string-only ``Literal``.

    Handles:

    * ``Literal["a", "b"]``
    * ``typing.Literal["a", "b"]``
    * ``Literal["a", "b"] | None`` (returns the non-None branch)
    * ``Optional[Literal["a", "b"]]``
    """
    # Unwrap `X | None` / `Optional[X]`
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        left = _extract_literal_values(annotation.left)
        right = _extract_literal_values(annotation.right)
        return left or right
    if isinstance(annotation, ast.Subscript):
        value = annotation.value
        name = _node_name(value)
        if name == "Optional":
            return _extract_literal_values(annotation.slice)
        if name in ("Literal", "typing.Literal"):
            return _literal_slice_values(annotation.slice)
    return None


def _node_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _node_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _literal_slice_values(slice_node: ast.AST) -> Optional[Set[str]]:
    """Extract string constants from a Literal subscript slice.

    ``Literal["a"]`` -> ``slice`` is a ``Constant``.
    ``Literal["a", "b"]`` -> ``slice`` is a ``Tuple`` of ``Constant``.
    """
    values: Set[str] = set()
    elements: List[ast.AST]
    if isinstance(slice_node, ast.Tuple):
        elements = list(slice_node.elts)
    else:
        elements = [slice_node]
    for el in elements:
        if isinstance(el, ast.Constant) and isinstance(el.value, str):
            values.add(el.value)
        else:
            # Non-string Literal (e.g. Literal[1, 2]) — not enum-compatible.
            return None
    return values if values else None


def _collect_literal_fields(tree: ast.AST) -> Dict[str, Set[str]]:
    """Walk *tree* and return ``{field_name: literal_values}`` for every
    class-level annotated assignment whose annotation is a Literal of strings.

    If two classes in the same file declare the same field with different
    Literals, the last one wins. That is acceptable for the cross-check
    purposes: the goal is to detect drift, not produce a perfect catalog.
    """
    out: Dict[str, Set[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    values = _extract_literal_values(stmt.annotation)
                    if values is not None:
                        out[stmt.target.id] = values
    return out


def _load_literal_fields(python_path: Path) -> Dict[str, Set[str]]:
    try:
        source = python_path.read_text(encoding="utf-8")
    except OSError:
        return {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    return _collect_literal_fields(tree)


# ---------------------------------------------------------------------------
# Contract walking
# ---------------------------------------------------------------------------


def _iter_enum_fields(schema: Any, prefix: str = "") -> List[Tuple[str, List[str]]]:
    """Yield ``(field_name, enum_values)`` pairs for every leaf with ``enum``.

    Traverses contract ``input``/``output``/``payload`` structures including
    nested objects (``type: object`` + ``properties``).
    """
    results: List[Tuple[str, List[str]]] = []
    if not isinstance(schema, dict):
        return results
    for name, spec in schema.items():
        if not isinstance(spec, dict):
            continue
        dotted = f"{prefix}.{name}" if prefix else name
        if isinstance(spec.get("enum"), list):
            values = [v for v in spec["enum"] if isinstance(v, str)]
            if values:
                results.append((name, values))
                # Also record under the dotted path so a consumer can
                # present a fully-qualified location if desired.
                if dotted != name:
                    results.append((dotted, values))
        # Recurse into nested object properties.
        if spec.get("type") == "object" and isinstance(spec.get("properties"), dict):
            results.extend(_iter_enum_fields(spec["properties"], prefix=dotted))
    return results


def _contract_schemas(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the list of ``input``/``output``/``payload`` blocks present."""
    blocks: List[Dict[str, Any]] = []
    for key in ("input", "output", "payload"):
        block = raw.get(key)
        if isinstance(block, dict):
            blocks.append(block)
    return blocks


def _parse_layer_path(raw_layer: Any) -> Tuple[Optional[str], Optional[str]]:
    """Split ``"path/to/file.py::ClassName"`` into ``(path, class_name)``.

    The ``::ClassName`` suffix is optional.
    """
    if not isinstance(raw_layer, str) or not raw_layer:
        return None, None
    if "::" in raw_layer:
        path, cls = raw_layer.split("::", 1)
        return path, cls
    return raw_layer, None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def cross_check_contract(
    contract: Contract,
    *,
    root: Optional[Path] = None,
) -> CrossCheckResult:
    """Compare contract enums against Pydantic ``Literal[...]`` annotations
    found in ``layers.python``.

    Returns :class:`CrossCheckResult` with:

    * ``errors`` — contract enum differs from Pydantic Literal (likely a bug).
    * ``warnings`` — contract enum is a strict subset or superset we cannot
      prove is intentional.

    Silent skips when:

    * ``layers.python`` is missing or unreadable.
    * No Pydantic field name matches the contract field name.
    * Pydantic field is typed something other than ``Literal[strings]``.
    """
    result = CrossCheckResult()
    layers = contract.raw.get("layers") or {}
    raw_layer = layers.get("python")
    layer_path, _class_name = _parse_layer_path(raw_layer)
    if not layer_path:
        return result

    python_path = Path(layer_path)
    if root is not None and not python_path.is_absolute():
        python_path = root / python_path
    if not python_path.is_file():
        return result

    literal_fields = _load_literal_fields(python_path)
    if not literal_fields:
        return result

    seen: Set[str] = set()
    for block in _contract_schemas(contract.raw):
        for field_name, enum_values in _iter_enum_fields(block):
            if field_name in seen:
                continue
            seen.add(field_name)
            base_name = field_name.rsplit(".", 1)[-1]
            pydantic_values = literal_fields.get(base_name)
            if pydantic_values is None:
                continue  # no matching Pydantic field — skip silently
            contract_set = set(enum_values)
            if contract_set != pydantic_values:
                missing_in_contract = sorted(pydantic_values - contract_set)
                missing_in_pydantic = sorted(contract_set - pydantic_values)
                parts: List[str] = []
                if missing_in_contract:
                    parts.append(
                        "Pydantic Literal has extra values not in contract enum: "
                        + ", ".join(missing_in_contract)
                    )
                if missing_in_pydantic:
                    parts.append(
                        "Contract enum has extra values not in Pydantic Literal: "
                        + ", ".join(missing_in_pydantic)
                    )
                result.errors.append(
                    f"field {field_name!r} enum drift in {contract.path.name}: "
                    + " / ".join(parts)
                )

    if result.errors:
        result.ok = False
    return result


def cross_check_contracts(
    contracts: List[Contract],
    *,
    root: Optional[Path] = None,
) -> List[Tuple[Contract, CrossCheckResult]]:
    """Run :func:`cross_check_contract` over every contract.

    Returns pairs ``(contract, result)`` in the same order as the input list.
    """
    return [(c, cross_check_contract(c, root=root)) for c in contracts]
