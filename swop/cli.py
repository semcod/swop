"""
Command line interface for swop.

Commands:
    swop sync [--mode MODE]
    swop inspect backend
    swop inspect frontend
    swop diff
    swop state [--yaml]
    swop export docker
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from swop.core import SwopRuntime
from swop.graph import DataModel, ModelField
from swop.markpact import DoqlBridge, ManifestParser, ManifestSyncEngine, build_project_graph
from swop.config import SwopConfigError, load_config
from swop.manifests import generate_manifests
from swop.proto import (
    compile_proto_python,
    compile_proto_typescript,
    generate_proto_from_manifests,
)
from swop.refactor import RefactorPipeline
from swop.scan import scan_project
from swop.scan.render import render_json, write_report
from swop.tools import init_project, run_doctor


def _build_runtime(mode: str) -> SwopRuntime:
    runtime = SwopRuntime(mode=mode)
    # Seed with a tiny demo graph so CLI output is meaningful without a DSL.
    runtime.add_model("Pressure", ["temp", "pressure_low", "pressure_high"])
    runtime.add_service("api", ["/pressure", "/status"])
    runtime.add_ui_binding("#sensor-temp", "temp")
    return runtime


def _cmd_sync(args: argparse.Namespace) -> int:
    runtime = _build_runtime(args.mode)
    drift = runtime.run_sync()
    return 1 if drift.exists() and args.mode == "STRICT" else 0


def _cmd_inspect(args: argparse.Namespace) -> int:
    runtime = _build_runtime(args.mode)
    if args.target == "backend":
        print(runtime.backend.introspect())
    elif args.target == "frontend":
        print(runtime.frontend.introspect())
    else:
        print(f"unknown inspect target: {args.target}", file=sys.stderr)
        return 2
    return 0


def _cmd_diff(args: argparse.Namespace) -> int:
    runtime = _build_runtime(args.mode)
    drift = runtime.run_sync()
    return 1 if drift.exists() else 0


def _cmd_state(args: argparse.Namespace) -> int:
    runtime = _build_runtime(args.mode)
    runtime.run_sync()
    print(runtime.state_yaml())
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    runtime = _build_runtime(args.mode)
    if args.target == "docker":
        print(runtime.docker_compose())
    else:
        print(f"unknown export target: {args.target}", file=sys.stderr)
        return 2
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    report = run_doctor(root)
    print(report.format())
    return 0 if report.ok else 1


def _cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    result = init_project(
        root,
        project_name=args.name,
        force=args.force,
        update_gitignore=not args.no_gitignore,
    )
    print(f"[INIT] swop project scaffolded at {root}")
    print(result.format())
    return 0


def _cmd_scan(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    config_path = Path(args.config) if args.config else root / "swop.yaml"
    try:
        config = load_config(config_path)
    except SwopConfigError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    report = scan_project(config, incremental=args.incremental)

    if args.json_out or args.html_out:
        written = write_report(
            report,
            json_path=Path(args.json_out) if args.json_out else None,
            html_path=Path(args.html_out) if args.html_out else None,
        )
        for label, path in written.items():
            print(f"[SCAN] report ({label}) -> {path}")

    if args.json:
        print(render_json(report))
    else:
        print(report.format_text())

    if args.strict_heuristics and report.via().get("heuristic", 0):
        print(
            f"[SCAN] {report.via()['heuristic']} detections via heuristic "
            "(strict mode: failing)",
            file=sys.stderr,
        )
        return 1
    if args.strict_errors and report.errors:
        return 1
    return 0


def _cmd_gen_manifests(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    config_path = Path(args.config) if args.config else root / "swop.yaml"
    try:
        config = load_config(config_path)
    except SwopConfigError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    report = scan_project(config, incremental=args.incremental)
    if args.skip_heuristics:
        report.detections = [d for d in report.detections if d.via != "heuristic"]

    out_dir = Path(args.out) if args.out else config.state_path / "manifests"
    result = generate_manifests(report, config, out_dir=out_dir)
    print(result.format())
    if not result.files:
        return 0
    return 0


def _cmd_gen_proto(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    config_path = Path(args.config) if args.config else root / "swop.yaml"
    try:
        config = load_config(config_path)
    except SwopConfigError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    manifests_dir = Path(args.manifests) if args.manifests else config.state_path / "manifests"
    if not manifests_dir.exists():
        print(
            f"[ERROR] manifests directory not found: {manifests_dir}\n"
            f"        run `swop gen manifests` first.",
            file=sys.stderr,
        )
        return 2

    out_dir = Path(args.out) if args.out else config.state_path / "generated" / "proto"
    result = generate_proto_from_manifests(manifests_dir, out_dir)
    print(result.format())
    return 0


def _cmd_gen_grpc_python(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    config_path = Path(args.config) if args.config else root / "swop.yaml"
    try:
        config = load_config(config_path)
    except SwopConfigError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    proto_dir = Path(args.proto) if args.proto else config.state_path / "generated" / "proto"
    out_dir = Path(args.out) if args.out else config.state_path / "generated" / "python"
    result = compile_proto_python(proto_dir, out_dir, grpc=not args.no_grpc)
    print(result.format())
    return 0 if result.ok else 1


def _cmd_gen_grpc_ts(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    config_path = Path(args.config) if args.config else root / "swop.yaml"
    try:
        config = load_config(config_path)
    except SwopConfigError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    proto_dir = Path(args.proto) if args.proto else config.state_path / "generated" / "proto"
    out_dir = Path(args.out) if args.out else config.state_path / "generated" / "ts"
    result = compile_proto_typescript(proto_dir, out_dir, ts_plugin=args.plugin)
    print(result.format())
    return 0 if result.ok else 1


def _cmd_refactor(args: argparse.Namespace) -> int:
    pipeline = RefactorPipeline(
        frontend=Path(args.frontend),
        backend=Path(args.backend) if args.backend else None,
        db=Path(args.db) if args.db else None,
        routes=args.route or [],
        out_dir=Path(args.out),
        strategy=args.strategy,
        frontend_pages_subdir=args.pages_subdir,
    )
    result = pipeline.run()
    summary = result.summary()
    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    else:
        print(f"[REFACTOR] graph nodes={summary['nodes']} edges={summary['edges']}")
        print(f"[REFACTOR] clusters={summary['clusters']} modules={len(summary['modules'])}")
        for module in summary["modules"]:
            print(
                f"  - {module['name']:<32} route={module['route']} "
                f"pages={len(module['pages'])} models={len(module['models'])}"
            )
        if summary["compose"]:
            print(f"[REFACTOR] docker-compose -> {summary['compose']}")
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"[ERROR] Manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    print(f"[GENERATE] Parsing manifest: {manifest_path}")
    parser = ManifestParser(base_dir=manifest_path.parent)
    blocks = parser.parse_file(manifest_path)

    doql_blocks = [b for b in blocks if b.kind == "doql"]
    graph_blocks = [b for b in blocks if b.kind == "graph"]
    file_blocks = [b for b in blocks if b.kind == "file"]

    print(f"[GENERATE] Found {len(blocks)} blocks: doql={len(doql_blocks)} graph={len(graph_blocks)} file={len(file_blocks)}")

    if doql_blocks:
        bridge = DoqlBridge(strict=args.strict)
        spec = bridge.from_blocks(blocks)
        graph = build_project_graph(spec)
    elif graph_blocks:
        import yaml
        graph = SwopRuntime().graph
        for block in graph_blocks:
            data = yaml.safe_load(block.body)
            for model_name, fields in data.get("models", {}).items():
                graph.models[model_name] = DataModel(
                    name=model_name,
                    fields={f: ModelField(f, "string") for f in fields},
                )
            for svc_name, routes in data.get("services", {}).items():
                graph.services[svc_name] = Service(name=svc_name, routes={r: {} for r in routes})
    else:
        print("[ERROR] No markpact:doql or markpact:graph blocks found.", file=sys.stderr)
        return 2

    print(f"[GENERATE] ProjectGraph: {len(graph.models)} models, {len(graph.services)} services, {len(graph.ui_bindings)} ui_bindings")

    # File-level sync (manifest <-> filesystem)
    if args.check_files:
        engine = ManifestSyncEngine(base_dir=manifest_path.parent)
        diffs = engine.diff(manifest_path)
        drifted = [d for d in diffs if d[1] != "ok" and d[1] != "untracked"]
        print(f"[GENERATE] Check files: {len(diffs)} tracked, {len(drifted)} drifted")
        for path, status, detail in diffs:
            if status != "untracked":
                print(f"  [{status}] {path} ({detail})")
        if drifted and args.mode == "STRICT":
            return 1

    if args.from_disk or args.from_disk_dry_run:
        engine = ManifestSyncEngine(base_dir=manifest_path.parent)
        updated = engine.update_manifest(manifest_path, dry_run=args.from_disk_dry_run)
        mode_str = "(dry-run)" if args.from_disk_dry_run else ""
        print(f"[GENERATE] Update manifest from disk {mode_str}: {len(updated)} block(s)")
        for u in updated:
            print(f"  <- {u}")

    if args.sync_files or args.sync_files_dry_run:
        engine = ManifestSyncEngine(base_dir=manifest_path.parent)
        written = engine.sync_to_disk(manifest_path, dry_run=args.sync_files_dry_run)
        mode_str = "(dry-run)" if args.sync_files_dry_run else ""
        print(f"[GENERATE] Sync files {mode_str}: {len(written)} file(s)")
        for w in written:
            print(f"  -> {w}")

    runtime = SwopRuntime(mode=args.mode)
    runtime.graph = graph

    exit_code = 0
    if args.sync:
        drift = runtime.run_sync()
        if drift.exists():
            print(f"[GENERATE] Drift detected (mode={args.mode})")
            if args.mode == "STRICT":
                exit_code = 1

    if args.output_yaml:
        out_path = Path(args.output_yaml)
        out_path.write_text(runtime.state_yaml(), encoding="utf-8")
        print(f"[GENERATE] YAML state written to {out_path}")

    if args.output_docker:
        out_path = Path(args.output_docker)
        out_path.write_text(runtime.docker_compose(), encoding="utf-8")
        print(f"[GENERATE] docker-compose written to {out_path}")

    if not args.output_yaml and not args.output_docker:
        print(runtime.state_yaml())

    return exit_code


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
