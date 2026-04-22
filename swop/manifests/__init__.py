"""
Manifest generator.

Turns a :class:`~swop.scan.report.ScanReport` + a
:class:`~swop.config.SwopConfig` into per-context YAML manifests under
``.swop/manifests/<context>/{commands,queries,events}.yml``.

Each manifest is intended to be human-reviewable and machine-readable,
and serves as the source of truth for downstream proto / gRPC / service
generation steps.
"""

from swop.manifests.generator import (
    ManifestFile,
    ManifestGenerationResult,
    generate_manifests,
)

__all__ = [
    "ManifestFile",
    "ManifestGenerationResult",
    "generate_manifests",
]
