"""
Bridge JSON contracts into swop's native :class:`~swop.scan.Detection` model.

This eliminates duplication between hand-written API contracts
(``*.{command,query,event}.json``) and the artefacts discovered by the AST
scanner.  A :class:`ContractDetectionAdapter` turns every contract into a
*declared* ``Detection`` with ``via="contract"`` and ``confidence=1.0`` so
that ``swop resolve`` can diff ``declared`` vs ``implemented``.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, List, Optional

from swop.scan.report import Detection, FieldDef


def _contract_kind(contract: Dict[str, Any]) -> str:
    if "command" in contract:
        return "command"
    if "query" in contract:
        return "query"
    if "event" in contract:
        return "event"
    raise ValueError("Contract lacks one of command/query/event discriminator")


def _contract_name(contract: Dict[str, Any]) -> str:
    return contract.get("command") or contract.get("query") or contract.get("event") or "Unknown"


def _contract_context(contract: Dict[str, Any]) -> str:
    return contract.get("module", "default")


def _contract_fields(contract: Dict[str, Any]) -> List[FieldDef]:
    """Extract :class:`FieldDef` list from ``input``, ``output`` or ``payload``."""
    kind = _contract_kind(contract)
    if kind in ("command", "query"):
        src = contract.get("input", {})
    else:  # event
        src = contract.get("payload", {})

    fields: List[FieldDef] = []
    for name, meta in src.items():
        if not isinstance(meta, dict):
            continue
        fields.append(
            FieldDef(
                name=name,
                type=meta.get("type", ""),
                required=bool(meta.get("required", True)),
                default=meta.get("default"),
            )
        )
    return fields


def contract_to_detection(
    contract: Dict[str, Any],
    *,
    source_file: Optional[str] = None,
    source_line: int = 1,
) -> Detection:
    """Turn a single JSON contract dict into a swop :class:`Detection`."""
    kind = _contract_kind(contract)
    name = _contract_name(contract)
    context = _contract_context(contract)
    file_name = source_file or contract.get("_file", "unknown")

    # Events emitted by a command are stored under contract["events"]
    emits: List[str] = []
    if kind == "command" and "events" in contract:
        ev = contract["events"]
        if isinstance(ev, dict):
            emits = list(ev.values())
        elif isinstance(ev, list):
            emits = ev

    return Detection(
        kind=kind,
        name=name,
        qualname=f"{context}.{name}",
        module=context,
        context=context,
        source_file=file_name,
        source_line=source_line,
        via="contract",
        confidence=1.0,
        bases=[],
        decorators=[],
        handles=None,
        emits=emits,
        reason="json contract",
        fields=_contract_fields(contract),
        file_fingerprint=None,
        handler_method=None,
    )


def contracts_to_detections(
    contracts: List[Dict[str, Any]],
    *,
    project_root: Optional[Path] = None,
) -> List[Detection]:
    """Convert every contract into a :class:`Detection`.

    Args:
        contracts: Result of :func:`swop.contracts.load_contracts`.
        project_root: If given, layer paths are resolved relative to it
            and stored as the ``source_file`` of the detection.

    Returns:
        A list of ``Detection`` objects with ``via="contract"``.
    """
    detections: List[Detection] = []
    for c in contracts:
        path = c.get("_path")
        src = str(Path(path).relative_to(project_root)) if project_root and path else path
        detections.append(contract_to_detection(c, source_file=src, source_line=1))
    return detections


class ContractDetectionAdapter:
    """High-level adapter that loads contracts and produces a *declared*
    :class:`~swop.scan.ScanReport`-like summary.

    Usage::

        adapter = ContractDetectionAdapter.from_directory(Path("./contracts"))
        for det in adapter.detections:
            print(det.kind, det.name)
    """

    def __init__(self, contracts: List[Dict[str, Any]], root: Optional[Path] = None) -> None:
        self.contracts = contracts
        self.root = root
        self.detections = contracts_to_detections(contracts, project_root=root)

    @classmethod
    def from_directory(cls, contracts_dir: Path, root: Optional[Path] = None) -> "ContractDetectionAdapter":
        from swop.contracts.reader import load_contracts

        contracts = load_contracts(contracts_dir)
        return cls(contracts, root=root or contracts_dir.parent)

    def by_kind(self, kind: str) -> List[Detection]:
        return [d for d in self.detections if d.kind == kind]

    def by_context(self, context: str) -> List[Detection]:
        return [d for d in self.detections if d.context == context]

    def contexts(self) -> List[str]:
        return sorted({d.context for d in self.detections})

    def summary(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for d in self.detections:
            out[d.kind] = out.get(d.kind, 0) + 1
        return out
