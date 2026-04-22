"""
CQRS registry.

Stores every class decorated with ``@command``, ``@query``, ``@event`` or
``@handler`` so that downstream tools (scanners, manifest generators,
proto generators) can enumerate them without re-parsing source.

The registry is process-global and reset-able for tests.
"""

from dataclasses import dataclass, field
from threading import RLock
from typing import Callable, Dict, Iterable, List, Optional, Tuple

CqrsKind = str  # "command" | "query" | "event" | "handler"


@dataclass(frozen=True)
class CqrsRecord:
    """One registered CQRS artifact."""

    kind: CqrsKind
    context: str
    qualname: str
    module: str
    cls: type
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    emits: Tuple[str, ...] = field(default_factory=tuple)
    handles: Optional[str] = None  # for @handler: the command/query it handles


class CqrsRegistry:
    """Thread-safe map of decorator-registered CQRS artifacts."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._records: Dict[Tuple[CqrsKind, str], CqrsRecord] = {}

    # ------------------------------------------------------------------
    # mutation
    # ------------------------------------------------------------------

    def register(self, record: CqrsRecord) -> CqrsRecord:
        key = (record.kind, record.qualname)
        with self._lock:
            self._records[key] = record
        return record

    def clear(self) -> None:
        with self._lock:
            self._records.clear()

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------

    def all(self) -> List[CqrsRecord]:
        with self._lock:
            return list(self._records.values())

    def of_kind(self, kind: CqrsKind) -> List[CqrsRecord]:
        with self._lock:
            return [r for r in self._records.values() if r.kind == kind]

    def by_context(self, context: str) -> List[CqrsRecord]:
        with self._lock:
            return [r for r in self._records.values() if r.context == context]

    def contexts(self) -> List[str]:
        with self._lock:
            return sorted({r.context for r in self._records.values()})

    def summary(self) -> Dict[str, int]:
        with self._lock:
            out: Dict[str, int] = {}
            for record in self._records.values():
                out[record.kind] = out.get(record.kind, 0) + 1
            return out

    # Python-style helpers

    def __len__(self) -> int:
        with self._lock:
            return len(self._records)

    def __iter__(self) -> Iterable[CqrsRecord]:
        return iter(self.all())


# ----------------------------------------------------------------------
# Module-global registry
# ----------------------------------------------------------------------

_REGISTRY = CqrsRegistry()


def get_registry() -> CqrsRegistry:
    """Return the global CQRS registry."""
    return _REGISTRY


def reset_registry() -> None:
    """Clear the global registry (intended for tests)."""
    _REGISTRY.clear()
