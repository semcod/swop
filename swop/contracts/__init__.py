"""
Contract-first metadata bridge for swop.

Reads JSON contract definitions (*.{command,query,event}.json) and
integrates them into the swop scan / manifest / registry pipeline so that
**declared** API contracts can be validated against **implemented**
CQRS artifacts, eliminating duplication between hand-written specs and
runtime detections.

Public entry points::

    from swop.contracts import load_contracts, validate_contract
    from swop.contracts import contracts_to_detections, ContractRegistry

Usage::

    contracts = load_contracts(Path("./contracts"))
    detections = contracts_to_detections(contracts, project_root=Path("."))

    registry = ContractRegistry.from_contracts(contracts)
    registry.write_json(out_path=Path("./contracts/registry.json"))
    registry.write_md(out_path=Path("./contracts/REGISTRY.md"))
"""

from swop.contracts.reader import load_contracts, validate_contract
from swop.contracts.adapter import contracts_to_detections, ContractDetectionAdapter
from swop.contracts.registry import ContractRegistry, generate_registry_json, generate_registry_md

__all__ = [
    "load_contracts",
    "validate_contract",
    "contracts_to_detections",
    "ContractDetectionAdapter",
    "ContractRegistry",
    "generate_registry_json",
    "generate_registry_md",
]
