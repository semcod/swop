"""
Contract registry for JSON-based CQRS contracts.

Reads ``contracts/*.{command,query,event}.json`` files (the same format
used by c2005 /system), validates them, and produces:

* ``registry.json`` — machine-readable manifest (commands, queries, events)
* ``REGISTRY.md``   — human-readable documentation with tables + details

The bridge layer converts the JSON contracts into swop :class:`~swop.scan.Detection`
objects so the same ``scan → manifests → proto → services`` pipeline
can be driven from a JSON contract directory as well as from Python
source code.
"""

from swop.registry.loader import Contract, load_contracts
from swop.registry.validator import ValidationResult, validate_contract
from swop.registry.generator import (
    RegistryGenerationResult,
    generate_registry_json,
    generate_registry_md,
    write_registry,
)
from swop.registry.bridge import bridge_contracts_to_detections

__all__ = [
    "Contract",
    "load_contracts",
    "ValidationResult",
    "validate_contract",
    "RegistryGenerationResult",
    "generate_registry_json",
    "generate_registry_md",
    "write_registry",
    "bridge_contracts_to_detections",
]
