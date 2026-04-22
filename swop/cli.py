"""Command line interface for swop."""

import argparse
from typing import List, Optional

from swop.commands import (
    _cmd_diff,
    _cmd_doctor,
    _cmd_export,
    _cmd_generate,
    _cmd_gen_grpc_python,
    _cmd_gen_grpc_ts,
    _cmd_gen_manifests,
    _cmd_gen_proto,
    _cmd_gen_services,
    _cmd_init,
    _cmd_inspect,
    _cmd_refactor,
    _cmd_resolve,
    _cmd_scan,
    _cmd_state,
    _cmd_sync,
    _cmd_watch,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="swop", description="Swop runtime reconciler")
    parser.add_argument(
        "--mode",
        choices=["STRICT", "SOFT", "OBSERVE", "AUTO_HEAL"],
        default="SOFT",
        help="Reconciliation mode",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sync", help="Run one reconciliation pass").set_defaults(func=_cmd_sync)

    p_inspect = sub.add_parser("inspect", help="Introspect backend or frontend")
    p_inspect.add_argument("target", choices=["backend", "frontend"])
    p_inspect.set_defaults(func=_cmd_inspect)

    sub.add_parser("diff", help="Compute drift and exit non-zero if drift exists").set_defaults(func=_cmd_diff)

    sub.add_parser("state", help="Dump current runtime state as YAML").set_defaults(func=_cmd_state)

    p_export = sub.add_parser("export", help="Export graph to an external format")
    p_export.add_argument("target", choices=["docker"])
    p_export.set_defaults(func=_cmd_export)

    p_doctor = sub.add_parser("doctor", help="Verify the local swop environment")
    p_doctor.add_argument(
        "--root",
        default=None,
        help="Project root to check (default: current working directory)",
    )
    p_doctor.set_defaults(func=_cmd_doctor)

    p_init = sub.add_parser(
        "init",
        help="Scaffold swop.yaml and .swop/ in the current project",
    )
    p_init.add_argument(
        "--root",
        default=None,
        help="Project root to initialise (default: current working directory)",
    )
    p_init.add_argument(
        "--name",
        default=None,
        help="Project name written to swop.yaml (default: folder name)",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing swop.yaml",
    )
    p_init.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Do not add swop entries to .gitignore",
    )
    p_init.set_defaults(func=_cmd_init)

    p_scan = sub.add_parser(
        "scan",
        help="Walk source roots and classify every CQRS artifact",
    )
    p_scan.add_argument(
        "--root",
        default=None,
        help="Project root containing swop.yaml (default: cwd)",
    )
    p_scan.add_argument(
        "--config",
        default=None,
        help="Path to swop.yaml (default: <root>/swop.yaml)",
    )
    p_scan.add_argument(
        "--incremental",
        dest="incremental",
        action="store_true",
        default=True,
        help="Use the fingerprint cache (default: on)",
    )
    p_scan.add_argument(
        "--no-incremental",
        dest="incremental",
        action="store_false",
        help="Disable the fingerprint cache and re-parse every file",
    )
    p_scan.add_argument(
        "--json",
        action="store_true",
        help="Print the full report to stdout as JSON",
    )
    p_scan.add_argument(
        "--json-out",
        default=None,
        dest="json_out",
        help="Write a JSON report to this file",
    )
    p_scan.add_argument(
        "--html-out",
        default=None,
        dest="html_out",
        help="Write an HTML report to this file",
    )
    p_scan.add_argument(
        "--strict-heuristics",
        action="store_true",
        help="Exit non-zero if any detection came from a heuristic",
    )
    p_scan.add_argument(
        "--strict-errors",
        action="store_true",
        help="Exit non-zero if any file failed to parse",
    )
    p_scan.set_defaults(func=_cmd_scan)

    p_gen = sub.add_parser(
        "gen",
        help="Generate manifests, proto, gRPC bindings or services",
    )
    gen_sub = p_gen.add_subparsers(dest="gen_command", required=True)

    p_gen_manifests = gen_sub.add_parser(
        "manifests",
        help="Write per-context commands/queries/events YAML manifests",
    )
    p_gen_manifests.add_argument(
        "--root",
        default=None,
        help="Project root containing swop.yaml (default: cwd)",
    )
    p_gen_manifests.add_argument(
        "--config",
        default=None,
        help="Path to swop.yaml (default: <root>/swop.yaml)",
    )
    p_gen_manifests.add_argument(
        "--out",
        default=None,
        help="Output directory for manifests (default: <state_dir>/manifests)",
    )
    p_gen_manifests.add_argument(
        "--incremental",
        dest="incremental",
        action="store_true",
        default=True,
        help="Use the fingerprint cache (default: on)",
    )
    p_gen_manifests.add_argument(
        "--no-incremental",
        dest="incremental",
        action="store_false",
        help="Disable the fingerprint cache and re-parse every file",
    )
    p_gen_manifests.add_argument(
        "--skip-heuristics",
        action="store_true",
        help="Only include detections from explicit @command/@query/@event decorators",
    )
    p_gen_manifests.set_defaults(func=_cmd_gen_manifests)

    p_gen_proto = gen_sub.add_parser(
        "proto",
        help="Render .proto files from per-context manifests",
    )
    p_gen_proto.add_argument("--root", default=None, help="Project root (default: cwd)")
    p_gen_proto.add_argument("--config", default=None, help="Path to swop.yaml")
    p_gen_proto.add_argument(
        "--manifests",
        default=None,
        help="Manifests directory (default: <state_dir>/manifests)",
    )
    p_gen_proto.add_argument(
        "--out",
        default=None,
        help="Output directory (default: <state_dir>/generated/proto)",
    )
    p_gen_proto.set_defaults(func=_cmd_gen_proto)

    p_gen_grpc_py = gen_sub.add_parser(
        "grpc-python",
        help="Compile .proto files into Python + gRPC stubs",
    )
    p_gen_grpc_py.add_argument("--root", default=None, help="Project root (default: cwd)")
    p_gen_grpc_py.add_argument("--config", default=None, help="Path to swop.yaml")
    p_gen_grpc_py.add_argument(
        "--proto",
        default=None,
        help="Proto input directory (default: <state_dir>/generated/proto)",
    )
    p_gen_grpc_py.add_argument(
        "--out",
        default=None,
        help="Python output directory (default: <state_dir>/generated/python)",
    )
    p_gen_grpc_py.add_argument(
        "--no-grpc",
        action="store_true",
        help="Generate only pb2 (no grpc stubs)",
    )
    p_gen_grpc_py.set_defaults(func=_cmd_gen_grpc_python)

    p_gen_grpc_ts = gen_sub.add_parser(
        "grpc-ts",
        help="Compile .proto files into TypeScript bindings (requires protoc + ts-proto)",
    )
    p_gen_grpc_ts.add_argument("--root", default=None, help="Project root (default: cwd)")
    p_gen_grpc_ts.add_argument("--config", default=None, help="Path to swop.yaml")
    p_gen_grpc_ts.add_argument(
        "--proto",
        default=None,
        help="Proto input directory (default: <state_dir>/generated/proto)",
    )
    p_gen_grpc_ts.add_argument(
        "--out",
        default=None,
        help="TS output directory (default: <state_dir>/generated/ts)",
    )
    p_gen_grpc_ts.add_argument(
        "--plugin",
        default=None,
        help="Path to protoc-gen-ts_proto (default: resolved from PATH)",
    )
    p_gen_grpc_ts.set_defaults(func=_cmd_gen_grpc_ts)

    p_gen_services = gen_sub.add_parser(
        "services",
        help="Render per-context service packages + docker-compose.cqrs.yml",
    )
    p_gen_services.add_argument("--root", default=None, help="Project root (default: cwd)")
    p_gen_services.add_argument("--config", default=None, help="Path to swop.yaml")
    p_gen_services.add_argument(
        "--manifests",
        default=None,
        help="Manifests directory (default: <state_dir>/manifests)",
    )
    p_gen_services.add_argument(
        "--proto-python",
        dest="proto_python",
        default=None,
        help="Path to compiled pb2 stubs to copy into each service "
        "(default: <state_dir>/generated/python)",
    )
    p_gen_services.add_argument(
        "--out",
        default=None,
        help="Output directory (default: <state_dir>/generated/services)",
    )
    p_gen_services.add_argument(
        "--bus",
        default=None,
        choices=sorted({"rabbitmq", "redis", "memory", "kafka"}),
        help="Bus backend (default: from swop.yaml, else memory)",
    )
    p_gen_services.add_argument(
        "--base-image",
        dest="base_image",
        default="python:3.12-slim",
        help="Dockerfile base image (default: python:3.12-slim)",
    )
    p_gen_services.add_argument(
        "--grpc-port",
        dest="grpc_port",
        type=int,
        default=50051,
        help="Starting gRPC port (incremented per context, default: 50051)",
    )
    p_gen_services.set_defaults(func=_cmd_gen_services)

    # ------------------------------------------------------------------
    # swop watch
    # ------------------------------------------------------------------
    p_watch = sub.add_parser(
        "watch",
        help="Watch source files and re-run scan + gen manifests on change",
    )
    p_watch.add_argument("--root", default=None, help="Project root (default: cwd)")
    p_watch.add_argument("--config", default=None, help="Path to swop.yaml")
    p_watch.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Polling interval in seconds (default: 0.5)",
    )
    p_watch.add_argument(
        "--debounce",
        type=float,
        default=0.3,
        help="Debounce window in seconds (default: 0.3)",
    )
    p_watch.add_argument(
        "--once",
        action="store_true",
        help="Run a single rebuild pass and exit (useful for CI and tests)",
    )
    p_watch.add_argument(
        "--no-incremental",
        action="store_true",
        help="Disable the fingerprint cache (re-parse every file every time)",
    )
    p_watch.set_defaults(func=_cmd_watch)

    # ------------------------------------------------------------------
    # swop resolve
    # ------------------------------------------------------------------
    p_resolve = sub.add_parser(
        "resolve",
        help="Diff current scan against stored manifests and classify changes",
    )
    p_resolve.add_argument("--root", default=None, help="Project root (default: cwd)")
    p_resolve.add_argument("--config", default=None, help="Path to swop.yaml")
    p_resolve.add_argument(
        "--manifests",
        default=None,
        help="Manifests directory (default: <state_dir>/manifests)",
    )
    p_resolve.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON report instead of text",
    )
    p_resolve.add_argument(
        "--apply",
        action="store_true",
        help="Accept drift by re-writing manifests from the current scan",
    )
    p_resolve.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when breaking changes are detected",
    )
    p_resolve.add_argument(
        "--no-incremental",
        action="store_true",
        help="Disable the fingerprint cache",
    )
    p_resolve.set_defaults(func=_cmd_resolve)

    p_refactor = sub.add_parser(
        "refactor",
        help="Extract modules from a full-stack project into an output directory",
    )
    p_refactor.add_argument("--frontend", required=True, help="Path to the frontend project root")
    p_refactor.add_argument("--backend", default=None, help="Path to the backend project root")
    p_refactor.add_argument("--db", default=None, help="Path to the database project root")
    p_refactor.add_argument(
        "--route",
        action="append",
        default=[],
        help="Route seed (repeatable), e.g. --route /connect-data",
    )
    p_refactor.add_argument("--out", default="modules", help="Output directory for extracted modules")
    p_refactor.add_argument(
        "--strategy",
        choices=["seeded", "louvain"],
        default="seeded",
        help="Clustering strategy",
    )
    p_refactor.add_argument(
        "--pages-subdir",
        default="src/pages",
        help="Subdirectory of the frontend root containing page files",
    )
    p_refactor.add_argument("--json", action="store_true", help="Emit a JSON summary instead of text")
    p_refactor.set_defaults(func=_cmd_refactor)

    p_generate = sub.add_parser(
        "generate",
        help="Generate a swop ProjectGraph from a Markpact manifest",
    )
    p_generate.add_argument(
        "--from-markpact",
        dest="manifest",
        required=True,
        help="Path to a Markpact manifest (.md) with markpact:* blocks",
    )
    p_generate.add_argument(
        "--strict",
        action="store_true",
        help="Fail fast on any DOQL parse error",
    )
    p_generate.add_argument(
        "--sync",
        action="store_true",
        help="Run sync engine after building the graph",
    )
    p_generate.add_argument(
        "--sync-files",
        action="store_true",
        help="Materialise markpact:file blocks to their declared paths",
    )
    p_generate.add_argument(
        "--sync-files-dry-run",
        action="store_true",
        help="Report which files would be written without writing them",
    )
    p_generate.add_argument(
        "--check-files",
        action="store_true",
        help="Report drift between markpact:file blocks and the filesystem",
    )
    p_generate.add_argument(
        "--from-disk",
        action="store_true",
        help="Reverse sync: rewrite markpact:file block bodies with disk content",
    )
    p_generate.add_argument(
        "--from-disk-dry-run",
        action="store_true",
        help="Report which blocks would be updated from disk without writing",
    )
    p_generate.add_argument(
        "--output-yaml",
        default=None,
        help="Write runtime state YAML to this path",
    )
    p_generate.add_argument(
        "--output-docker",
        default=None,
        help="Write docker-compose YAML to this path",
    )
    p_generate.set_defaults(func=_cmd_generate)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
