"""
Markpact integration for swop.

Provides:
- Block parser for markdown manifests containing multiple definition formats
- DOQL bridge: markpact blocks -> DoqlSpec -> ProjectGraph
- Validation and filesystem sync for manifest blocks
- CLI hook: ``swop generate --from-markpact manifest.md``

Pipeline::

    README.md → markpact:* blocks → DoqlSpec → swop ProjectGraph → runtime
"""

from swop.markpact.parser import ManifestParser, ManifestBlock
from swop.markpact.doql_bridge import DoqlBridge, MarkpactValidationError
from swop.markpact.graph_builder import build_project_graph
from swop.markpact.sync_engine import ManifestSyncEngine

__all__ = [
    "ManifestParser",
    "ManifestBlock",
    "DoqlBridge",
    "MarkpactValidationError",
    "build_project_graph",
    "ManifestSyncEngine",
]
