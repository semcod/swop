"""
swop - bi-directional runtime reconciler for full-stack state graphs.
"""

__version__ = "0.2.3"

from swop.core import SwopRuntime, SynqerRuntime
from swop.graph import (
    DataModel,
    GraphVersion,
    ModelField,
    ProjectGraph,
    Service,
    UIBinding,
)
from swop.introspect import BackendIntrospector, FrontendIntrospector
from swop.reconcile import Drift, DriftDetector, DriftError, ResyncEngine
from swop.refactor import RefactorPipeline, RefactorResult
from swop.sync import SyncEngine
from swop.versioning import Versioning
from swop.markpact import (
    ManifestParser,
    DoqlBridge,
    build_project_graph,
    ManifestSyncEngine,
)

__all__ = [
    "SwopRuntime",
    "SynqerRuntime",
    "ProjectGraph",
    "DataModel",
    "ModelField",
    "UIBinding",
    "Service",
    "GraphVersion",
    "BackendIntrospector",
    "FrontendIntrospector",
    "Drift",
    "DriftDetector",
    "DriftError",
    "ResyncEngine",
    "SyncEngine",
    "Versioning",
    "RefactorPipeline",
    "RefactorResult",
    "ManifestParser",
    "DoqlBridge",
    "build_project_graph",
    "ManifestSyncEngine",
]
