"""
AST-based CQRS scanner.

Walks the ``source_roots`` declared in ``swop.yaml``, parses each Python
file with :mod:`ast`, and classifies every class definition as one of
``command`` / ``query`` / ``event`` / ``handler`` using either an
explicit swop decorator or a conservative name/base heuristic.

The primary entry point is :func:`scan_project`, which returns a
:class:`ScanReport`. The ``swop scan`` CLI command wraps it and adds
incremental caching plus report rendering.
"""

from swop.scan.cache import FingerprintCache
from swop.scan.report import (
    ContextSummary,
    Detection,
    DetectionKind,
    DetectionVia,
    ScanReport,
)
from swop.scan.scanner import scan_project

__all__ = [
    "FingerprintCache",
    "ContextSummary",
    "Detection",
    "DetectionKind",
    "DetectionVia",
    "ScanReport",
    "scan_project",
]
