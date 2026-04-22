"""
Refactor subpackage.

Extracts a dependency graph from a full-stack project (frontend + backend
+ database), clusters the graph into modules (seeded by frontend routes
or via a Louvain-like algorithm) and writes each module as a self-
contained folder with a ``docker-compose.yml``.

Programmatic usage::

    from swop.refactor import RefactorPipeline

    pipeline = RefactorPipeline(
        frontend="/path/to/frontend",
        backend="/path/to/backend",
        db="/path/to/db",
        routes=["/connect-test/devices", "/connect-data"],
        out_dir="modules",
    )
    result = pipeline.run()
"""

from swop.refactor.clustering import LouvainLike, SeededClusterer
from swop.refactor.compose_builder import ComposeBuilder
from swop.refactor.graph import Edge, Node, RefactorGraph
from swop.refactor.module_builder import ModuleBuilder
from swop.refactor.pipeline import RefactorPipeline, RefactorResult
from swop.refactor.scanner import BackendScanner, DbScanner, FrontendScanner

__all__ = [
    "RefactorGraph",
    "Node",
    "Edge",
    "FrontendScanner",
    "BackendScanner",
    "DbScanner",
    "LouvainLike",
    "SeededClusterer",
    "ModuleBuilder",
    "ComposeBuilder",
    "RefactorPipeline",
    "RefactorResult",
]
