"""
Schema evolution / drift resolver.

Compares the *current* scan (what the codebase looks like right now)
against the *previously written* per-context manifest YAML files
(the shape that downstream consumers were generated against) and
classifies every change as:

* **added**     — a new command / query / event / field. Safe.
* **removed**   — a symbol / field disappeared. Breaking.
* **renamed**   — same shape, different name. Needs a migration.
* **type-change** — a field changed type. Breaking for consumers.
* **metadata**  — `emits`, `handler`, `bus` changed. Non-breaking.

The resolver returns a :class:`ResolutionReport` which can be printed
for humans, emitted as JSON, or (with ``--apply``) turned into an
updated set of manifests + a migration note.
"""

from swop.resolve.resolver import (
    Change,
    ChangeKind,
    ResolutionReport,
    apply_resolution,
    resolve_schema_drift,
)

__all__ = [
    "Change",
    "ChangeKind",
    "ResolutionReport",
    "resolve_schema_drift",
    "apply_resolution",
]
