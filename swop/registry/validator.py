"""
Validate JSON contracts.

* Checks required top-level keys (``command`` / ``query`` / ``event``, ``kind``, ``version`` …).
* Checks that ``kind`` matches the discriminator.
* Checks that every path in ``layers`` resolves to an existing file on disk.
* Reports layer path errors stripped of ``::ClassName`` suffixes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from swop.registry.loader import Contract


@dataclass
class ValidationResult:
    ok: bool = True
    errors: List[str] = field(default_factory=list)

    def format(self) -> str:
        if self.ok:
            return "valid"
        return "; ".join(self.errors)


_REQUIRED_COMMAND = ("command", "kind", "version", "input", "output", "transport", "layers")
_REQUIRED_QUERY = ("query", "kind", "version", "input", "output", "transport", "layers")
_REQUIRED_EVENT = ("event", "kind", "version", "payload", "producers")


def validate_contract(contract: Contract, *, root: Optional[Path] = None) -> ValidationResult:
    """Validate a single :class:`Contract`.

    *root* is the project root used to resolve relative paths in ``layers``.
    """
    errors: List[str] = []
    raw = contract.raw

    if "command" in raw:
        _check_keys(raw, _REQUIRED_COMMAND, errors)
        _check_kind(raw, "CQRS_COMMAND", errors)
        _check_layer_paths(raw, root, errors)
    elif "query" in raw:
        _check_keys(raw, _REQUIRED_QUERY, errors)
        _check_kind(raw, "CQRS_QUERY", errors)
        _check_layer_paths(raw, root, errors)
    elif "event" in raw:
        _check_keys(raw, _REQUIRED_EVENT, errors)
        kind = raw.get("kind", "")
        if kind not in ("DOMAIN_EVENT", "INTEGRATION_EVENT"):
            errors.append(f"event kind must be DOMAIN_EVENT or INTEGRATION_EVENT, got {kind!r}")
    else:
        errors.append("missing discriminator: one of 'command', 'query', 'event' required")

    return ValidationResult(ok=not errors, errors=errors)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _check_keys(raw: Dict[str, Any], required: tuple, errors: List[str]) -> None:
    for key in required:
        if key not in raw:
            errors.append(f"missing required field: {key!r}")


def _check_kind(raw: Dict[str, Any], expected: str, errors: List[str]) -> None:
    if raw.get("kind") != expected:
        errors.append(f"kind must be {expected!r}, got {raw.get('kind')!r}")


def _check_layer_paths(raw: Dict[str, Any], root: Optional[Path], errors: List[str]) -> None:
    layers = raw.get("layers", {})
    if not isinstance(layers, dict):
        return
    for key, value in layers.items():
        if not isinstance(value, str):
            continue
        # strip ::ClassName suffix
        raw_path = value.split("::")[0]
        if not raw_path:
            continue
        if root is not None:
            resolved = root / raw_path
            if not resolved.exists():
                errors.append(f"layers.{key} path not found: {raw_path}")


from typing import Any  # noqa: E402
