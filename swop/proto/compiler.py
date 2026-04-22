"""
Thin wrappers around ``grpc_tools.protoc`` and ``protoc`` for turning
``.proto`` files into Python or TypeScript bindings.

These functions never install toolchains for the user; they only check
whether the required binary / module is importable and execute it.
Consumers get a :class:`CompilationResult` describing which files were
produced and any warnings / errors emitted by protoc.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence


@dataclass
class CompilationResult:
    target: str  # "python" | "typescript"
    proto_files: List[Path] = field(default_factory=list)
    output_dir: Optional[Path] = None
    outputs: List[Path] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    tool_invocation: Optional[str] = None
    ok: bool = True

    def format(self) -> str:
        status = "ok" if self.ok else "FAILED"
        lines = [
            f"[GRPC-{self.target.upper()}] {status} "
            f"({len(self.proto_files)} proto file(s) → {len(self.outputs)} output(s))"
        ]
        if self.output_dir:
            lines.append(f"  output dir: {self.output_dir}")
        if self.tool_invocation:
            lines.append(f"  tool: {self.tool_invocation}")
        for w in self.warnings[:10]:
            lines.append(f"  [warn] {w}")
        for err in self.errors[:10]:
            lines.append(f"  [err] {err}")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Discovery helpers
# ----------------------------------------------------------------------


def _iter_proto_files(proto_dir: Path) -> List[Path]:
    return sorted(Path(proto_dir).rglob("*.proto"))


def _proto_roots(proto_files: Iterable[Path], proto_dir: Path) -> List[Path]:
    """Include the proto_dir root in the -I search path."""
    return [Path(proto_dir).resolve()]


def _run(cmd: Sequence[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        list(cmd),
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )


# ----------------------------------------------------------------------
# Python
# ----------------------------------------------------------------------


def compile_proto_python(
    proto_dir: Path,
    out_dir: Path,
    *,
    grpc: bool = True,
) -> CompilationResult:
    """Compile every .proto under ``proto_dir`` with grpc_tools.protoc."""

    proto_dir = Path(proto_dir).resolve()
    out_dir = Path(out_dir).resolve()
    result = CompilationResult(target="python", output_dir=out_dir)

    proto_files = _iter_proto_files(proto_dir)
    result.proto_files = proto_files
    if not proto_files:
        result.warnings.append(f"no .proto files found under {proto_dir}")
        return result

    try:
        import grpc_tools  # noqa: F401
        from grpc_tools import protoc  # noqa: F401
    except ImportError:
        result.ok = False
        result.errors.append(
            "grpc_tools is not installed. Install it with: "
            "pip install grpcio-tools"
        )
        return result

    out_dir.mkdir(parents=True, exist_ok=True)
    includes = [f"-I{p}" for p in _proto_roots(proto_files, proto_dir)]
    # Also include grpc_tools' builtin well-known protos.
    import grpc_tools  # re-import for path access

    builtin = Path(grpc_tools.__file__).parent / "_proto"
    if builtin.exists():
        includes.append(f"-I{builtin}")

    argv = [
        "grpc_tools.protoc",
        *includes,
        f"--python_out={out_dir}",
    ]
    if grpc:
        argv.append(f"--grpc_python_out={out_dir}")
    argv.extend(str(p) for p in proto_files)
    result.tool_invocation = " ".join(argv)

    from grpc_tools.protoc import main as protoc_main  # type: ignore[attr-defined]

    exit_code = protoc_main(argv)
    if exit_code != 0:
        result.ok = False
        result.errors.append(f"grpc_tools.protoc exited with code {exit_code}")

    result.outputs = sorted(out_dir.rglob("*.py"))
    return result


# ----------------------------------------------------------------------
# TypeScript
# ----------------------------------------------------------------------


def compile_proto_typescript(
    proto_dir: Path,
    out_dir: Path,
    *,
    ts_plugin: Optional[str] = None,
) -> CompilationResult:
    """Compile every .proto under ``proto_dir`` into TypeScript bindings.

    Requires ``protoc`` on ``PATH`` and either ``ts-proto``'s
    ``protoc-gen-ts_proto`` plugin (default) or a path supplied via
    ``ts_plugin``. When the plugin is not found we return a
    non-zero :class:`CompilationResult` with a helpful ``errors`` entry
    instead of raising, so that callers can surface the message.
    """

    proto_dir = Path(proto_dir).resolve()
    out_dir = Path(out_dir).resolve()
    result = CompilationResult(target="typescript", output_dir=out_dir)

    proto_files = _iter_proto_files(proto_dir)
    result.proto_files = proto_files
    if not proto_files:
        result.warnings.append(f"no .proto files found under {proto_dir}")
        return result

    protoc = shutil.which("protoc")
    if not protoc:
        result.ok = False
        result.errors.append(
            "`protoc` not found on PATH. Install Protocol Buffers compiler."
        )
        return result

    plugin = ts_plugin or shutil.which("protoc-gen-ts_proto")
    if not plugin:
        result.ok = False
        result.errors.append(
            "`protoc-gen-ts_proto` not found. Install ts-proto via "
            "`npm install -D ts-proto` and re-run `swop gen grpc-ts`."
        )
        return result

    out_dir.mkdir(parents=True, exist_ok=True)
    includes = [f"-I{p}" for p in _proto_roots(proto_files, proto_dir)]
    argv = [
        protoc,
        f"--plugin=protoc-gen-ts_proto={plugin}",
        f"--ts_proto_out={out_dir}",
        "--ts_proto_opt=esModuleInterop=true,outputServices=grpc-js",
        *includes,
        *[str(p) for p in proto_files],
    ]
    result.tool_invocation = " ".join(argv)

    proc = _run(argv)
    if proc.returncode != 0:
        result.ok = False
        if proc.stderr:
            result.errors.append(proc.stderr.strip())
        else:
            result.errors.append(f"protoc exited with code {proc.returncode}")
    elif proc.stderr:
        result.warnings.append(proc.stderr.strip())

    result.outputs = sorted(out_dir.rglob("*.ts"))
    return result
