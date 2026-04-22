"""
Proto / gRPC code generation.

This package turns per-context manifest YAML (produced by
:mod:`swop.manifests`) into ``.proto`` files and, optionally, wraps
``grpc_tools.protoc`` to compile them into Python or TypeScript
bindings.
"""

from swop.proto.compiler import (
    CompilationResult,
    compile_proto_python,
    compile_proto_typescript,
)
from swop.proto.generator import (
    ProtoFile,
    ProtoGenerationResult,
    generate_proto_from_manifests,
    render_proto_for_context,
)

__all__ = [
    "ProtoFile",
    "ProtoGenerationResult",
    "generate_proto_from_manifests",
    "render_proto_for_context",
    "CompilationResult",
    "compile_proto_python",
    "compile_proto_typescript",
]
