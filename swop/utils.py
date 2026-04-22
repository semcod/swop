"""
Miscellaneous helpers used across the swop package.
"""

import hashlib
import json
from typing import Any


def stable_hash(payload: Any) -> str:
    """Return a deterministic SHA-1 hash of a JSON-serializable payload."""
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha1(serialized.encode("utf-8")).hexdigest()


def is_callable(obj: Any) -> bool:
    """Return ``True`` if ``obj`` is callable."""
    return callable(obj)


def get_docstring(obj: Any):
    """Return the ``__doc__`` attribute of ``obj`` or ``None``."""
    return getattr(obj, "__doc__", None)
