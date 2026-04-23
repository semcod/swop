"""
Load ``*.command.json``, ``*.query.json`` and ``*.event.json`` files from
a contracts directory.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Contract:
    """One JSON contract loaded from disk."""

    path: Path
    name: str           # the value of "command" / "query" / "event"
    kind: str           # CQRS_COMMAND | CQRS_QUERY | DOMAIN_EVENT | …
    raw: Dict[str, Any]


def load_contracts(contracts_dir: Path) -> List[Contract]:
    """Read every ``*.{command,query,event}.json`` under *contracts_dir*."""
    contracts: List[Contract] = []
    if not contracts_dir.exists() or not contracts_dir.is_dir():
        return contracts

    patterns = ("*.command.json", "*.query.json", "*.event.json")
    for pattern in patterns:
        for path in sorted(contracts_dir.glob(pattern)):
            text = path.read_text(encoding="utf-8")
            raw = json.loads(text)
            name = raw.get("command") or raw.get("query") or raw.get("event")
            if name:
                kind = raw.get("kind", "UNKNOWN")
                contracts.append(Contract(path=path, name=name, kind=kind, raw=raw))
    return contracts
