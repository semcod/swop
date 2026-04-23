"""
swop - bi-directional runtime reconciler for full-stack state graphs.
"""

__version__ = "0.2.9"

from swop.config import (
    BoundedContextConfig,
    BusConfig,
    ReadModelConfig,
    SwopConfig,
    SwopConfigError,
    load_config,
)
from swop.core import SwopRuntime, SynqerRuntime
from swop.cqrs import (
    CqrsRecord,
    CqrsRegistry,
    command,
    event,
    get_registry,
    handler,
    query,
    reset_registry,
)
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
from swop.manifests import (
    ManifestFile,
    ManifestGenerationResult,
    generate_manifests,
)
from swop.proto import (
    CompilationResult,
    ProtoFile,
    ProtoGenerationResult,
    compile_proto_python,
    compile_proto_typescript,
    generate_proto_from_manifests,
)
from swop.refactor import RefactorPipeline, RefactorResult
from swop.resolve import (
    Change,
    ChangeKind,
    ResolutionReport,
    apply_resolution,
    resolve_schema_drift,
)
from swop.services import (
    ServiceFile,
    ServiceGenerationResult,
    generate_services,
)
from swop.tools import (
    DeepCheck,
    DeepIssue,
    DeepReport,
    HookResult,
    hook_status,
    install_hook,
    run_deep_doctor,
    uninstall_hook,
)
from swop.watch import WatchEngine, WatchRebuild, rebuild_once
from swop.scan import (
    ContextSummary,
    Detection,
    FingerprintCache,
    ScanReport,
    scan_project,
)
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
    # CQRS
    "CqrsRecord",
    "CqrsRegistry",
    "command",
    "event",
    "query",
    "handler",
    "get_registry",
    "reset_registry",
    # Config
    "SwopConfig",
    "SwopConfigError",
    "BoundedContextConfig",
    "BusConfig",
    "ReadModelConfig",
    "load_config",
    # Scan
    "scan_project",
    "ScanReport",
    "Detection",
    "ContextSummary",
    "FingerprintCache",
    # Manifests
    "generate_manifests",
    "ManifestFile",
    "ManifestGenerationResult",
    # Proto / gRPC
    "generate_proto_from_manifests",
    "compile_proto_python",
    "compile_proto_typescript",
    "ProtoFile",
    "ProtoGenerationResult",
    "CompilationResult",
    # Services
    "generate_services",
    "ServiceFile",
    "ServiceGenerationResult",
    # Watch
    "WatchEngine",
    "WatchRebuild",
    "rebuild_once",
    # Resolve / schema evolution
    "resolve_schema_drift",
    "apply_resolution",
    "Change",
    "ChangeKind",
    "ResolutionReport",
    # Deep doctor / hooks
    "run_deep_doctor",
    "DeepCheck",
    "DeepIssue",
    "DeepReport",
    "install_hook",
    "uninstall_hook",
    "hook_status",
    "HookResult",
]
