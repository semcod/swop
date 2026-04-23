"""
JSON contract loader and validator.

Mirrors the validation logic from ``generate-registry.py`` so that swop
can consume the same ``contracts/*.{command,query,event}.json`` files
used by downstream code generators.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CONTRACT_PATTERNS = ("*.command.json", "*.query.json", "*.event.json")


def load_contracts(contracts_dir: Path) -> List[Dict[str, Any]]:
    """Load every ``*.{command,query,event}.json`` file under *contracts_dir*."""
    contracts: List[Dict[str, Any]] = []
    if not contracts_dir.exists():
        return contracts

    for pattern in CONTRACT_PATTERNS:
        for path in sorted(contracts_dir.glob(pattern)):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ContractValidationError(
                    f"Invalid JSON in {path.name}: {exc}"
                ) from exc
            data["_file"] = path.name
            data["_path"] = str(path)
            contracts.append(data)

    return contracts


class ContractValidationError(ValueError):
    """Raised when a contract file fails structural validation."""


def _check_layer_paths(
    contract: Dict[str, Any],
    errors: List[str],
    root: Optional[Path] = None,
) -> None:
    """Validate that file paths in 'layers' exist on disk.

    Strips ``::ClassName`` suffix before checking.
    """
    for key, value in contract.get("layers", {}).items():
        raw = value.split("::")[0] if isinstance(value, str) else None
        if raw is None:
            continue
        if root is not None:
            resolved = root / raw
            if not resolved.exists():
                errors.append(f"layers.{key} path not found: {raw}")


def validate_contract(
    contract: Dict[str, Any],
    *,
    root: Optional[Path] = None,
    strict: bool = False,
) -> List[str]:
    """Validate a single contract dict and return a list of error strings.

    Args:
        contract: The loaded JSON object.
        root: Project root used to resolve relative layer paths.
        strict: When ``True``, treat a missing ``root`` as an error
            instead of silently skipping layer-path checks.

    Returns:
        A list of human-readable error messages. An empty list means the
        contract is valid.
    """
    errors: List[str] = []
    kind = contract.get("kind")

    if "command" in contract:
        required = ["command", "kind", "version", "input", "output", "transport", "layers"]
        for key in required:
            if key not in contract:
                errors.append(f"Missing required field: '{key}'")
        if kind != "CQRS_COMMAND":
            errors.append(f"'kind' for command must be CQRS_COMMAND, got: {kind}")
        if root is not None or not strict:
            _check_layer_paths(contract, errors, root=root)
        elif strict and "layers" in contract:
            errors.append("Cannot validate layer paths without a project root")

    elif "query" in contract:
        required = ["query", "kind", "version", "input", "output", "transport", "layers"]
        for key in required:
            if key not in contract:
                errors.append(f"Missing required field: '{key}'")
        if kind != "CQRS_QUERY":
            errors.append(f"'kind' for query must be CQRS_QUERY, got: {kind}")
        if root is not None or not strict:
            _check_layer_paths(contract, errors, root=root)
        elif strict and "layers" in contract:
            errors.append("Cannot validate layer paths without a project root")

    elif "event" in contract:
        required = ["event", "kind", "version", "payload", "producers"]
        for key in required:
            if key not in contract:
                errors.append(f"Missing required field: '{key}'")
        if kind not in ("DOMAIN_EVENT", "INTEGRATION_EVENT"):
            errors.append(
                f"'kind' for event must be DOMAIN_EVENT or INTEGRATION_EVENT, got: {kind}"
            )
    else:
        errors.append(
            "Missing discriminator field: one of 'command', 'query', 'event' is required"
        )

    return errors


def validate_all(
    contracts: List[Dict[str, Any]],
    *,
    root: Optional[Path] = None,
    fail_fast: bool = False,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Validate every contract and return *(valid, errors)*.

    Args:
        contracts: List of loaded contract dicts.
        root: Project root for layer-path resolution.
        fail_fast: Raise ``ContractValidationError`` on the first invalid contract.

    Returns:
        A 2-tuple of *(valid_contracts, error_messages)*.
    """
    valid: List[Dict[str, Any]] = []
    all_errors: List[str] = []

    for c in contracts:
        errors = validate_contract(c, root=root)
        if errors:
            msg = f"{c.get('_file', '?' )}: {'; '.join(errors)}"
            if fail_fast:
                raise ContractValidationError(msg)
            all_errors.append(msg)
        else:
            valid.append(c)

    return valid, all_errors
