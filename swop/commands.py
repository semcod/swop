"""Command handlers for the swop CLI."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from swop.core import SwopRuntime
from swop.graph import DataModel, ModelField, Service
from swop.markpact import DoqlBridge, ManifestParser, ManifestSyncEngine, build_project_graph
from swop.config import SwopConfigError, load_config
from swop.manifests import generate_manifests
from swop.proto import (
    compile_proto_python,
    compile_proto_typescript,
    generate_proto_from_manifests,
)
from swop.refactor import RefactorPipeline
from swop.resolve import apply_resolution, resolve_schema_drift
from swop.services import generate_services
from swop.scan import scan_project
from swop.scan.render import render_json, write_report
from swop.tools import (
    hook_status,
    init_project,
    install_hook,
    run_deep_doctor,
    run_doctor,
    uninstall_hook,
)
from swop.registry import (
    cross_check_contracts,
    load_contracts,
    validate_contract,
    write_registry,
)
from swop.watch import WatchEngine, rebuild_once


def _build_runtime(mode: str) -> SwopRuntime:
    runtime = SwopRuntime(mode=mode)
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

    deep_ok = True
    if getattr(args, "deep", False):
        config_path = Path(args.config) if getattr(args, "config", None) else root / "swop.yaml"
        try:
            config = load_config(config_path)
        except SwopConfigError as exc:
            print(f"\n[ERROR] --deep requires a loadable swop.yaml: {exc}", file=sys.stderr)
            return 2
        print()
        deep_report = run_deep_doctor(config)
        print(deep_report.format())
        deep_ok = deep_report.ok

    if not report.ok:
        return 1
    if not deep_ok:
        return 1
    return 0


def _cmd_hook(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    action = getattr(args, "hook_action", None)
    if action == "install":
        result = install_hook(root, force=bool(getattr(args, "force", False)))
    elif action == "uninstall":
        result = uninstall_hook(root)
    elif action == "status":
        result = hook_status(root)
    else:
        print("usage: swop hook {install,uninstall,status}", file=sys.stderr)
        return 2
    print(result.format())
    if result.status == "error":
        return 2
    return 0


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


def _cmd_gen_services(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    config_path = Path(args.config) if args.config else root / "swop.yaml"
    try:
        config = load_config(config_path)
    except SwopConfigError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    manifests_dir = (
        Path(args.manifests) if args.manifests else config.state_path / "manifests"
    )
    if not manifests_dir.exists():
        print(
            f"[ERROR] manifests directory not found: {manifests_dir}\n"
            f"        run `swop gen manifests` first.",
            file=sys.stderr,
        )
        return 2

    out_dir = Path(args.out) if args.out else config.state_path / "generated" / "services"
    proto_python_dir = (
        Path(args.proto_python)
        if args.proto_python
        else config.state_path / "generated" / "python"
    )
    bus = args.bus or (config.bus.type if config.bus else "memory")

    try:
        result = generate_services(
            manifests_dir,
            out_dir,
            bus=bus,
            base_image=args.base_image,
            grpc_port=args.grpc_port,
            proto_python_dir=proto_python_dir if proto_python_dir.exists() else None,
        )
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    print(result.format())
    return 0


def _cmd_gen_registry(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    contracts_dir = Path(args.contracts) if getattr(args, "contracts", None) else root / "contracts"
    contracts = load_contracts(contracts_dir)
    if not contracts:
        print(f"[REGISTRY] no contracts found in {contracts_dir}")
        return 0

    all_valid = True
    for c in contracts:
        result = validate_contract(c, root=root)
        if not result.ok:
            all_valid = False
            print(f"  ❌ {c.path.name}: {result.format()}", file=sys.stderr)
        else:
            print(f"  ✅ {c.name}")

    if not all_valid:
        print("\n❌ Validation failed. Fix errors above before generating.", file=sys.stderr)
        return 1

    # Optional cross-check against Pydantic Literal[...] annotations in layers.python.
    if getattr(args, "cross_check_pydantic", False):
        cross_results = cross_check_contracts(contracts, root=root)
        cross_errors = [(c, r) for c, r in cross_results if not r.ok]
        if cross_errors:
            print("\n❌ Cross-check failed (contract enum vs Pydantic Literal):", file=sys.stderr)
            for contract, result in cross_errors:
                for err in result.errors:
                    print(f"  ❌ {err}", file=sys.stderr)
            return 1
        else:
            print("\n🔗 Cross-check passed (contract enums match Pydantic Literal[...] annotations)")

    if getattr(args, "check", False):
        print("\n✅ All contracts valid (--check mode, no files written)")
        return 0

    result = write_registry(contracts_dir, contracts)
    print(result.format())
    return 0


def _cmd_watch(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    config_path = Path(args.config) if args.config else root / "swop.yaml"
    try:
        config = load_config(config_path)
    except SwopConfigError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    if args.once:
        rebuild = rebuild_once(config, incremental=not args.no_incremental)
        print(rebuild.format())
        return 0

    engine = WatchEngine(
        config=config,
        interval=args.interval,
        debounce=args.debounce,
    )
    print(
        f"[WATCH] watching {', '.join(config.source_roots) or config.root} "
        f"(interval={args.interval}s, debounce={args.debounce}s). Press Ctrl+C to stop."
    )
    engine.poll_once()
    initial = rebuild_once(config, incremental=not args.no_incremental)
    print(initial.format())
    engine.run(on_rebuild=lambda r: print(r.format()))
    return 0


def _cmd_resolve(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path.cwd()
    config_path = Path(args.config) if args.config else root / "swop.yaml"
    try:
        config = load_config(config_path)
    except SwopConfigError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    manifests_dir = (
        Path(args.manifests) if args.manifests else config.state_path / "manifests"
    )
    report = scan_project(config, incremental=not args.no_incremental)
    resolution = resolve_schema_drift(report, config, manifests_dir=manifests_dir)

    if args.json:
        print(resolution.to_json())
    else:
        print(resolution.format())

    if args.apply:
        target = apply_resolution(report, config, resolution, out_dir=manifests_dir)
        print(f"[RESOLVE] applied: manifests refreshed under {target}")

    if args.strict and resolution.breaking:
        return 1
    return 0


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


def _generate_parse_manifest(args: argparse.Namespace):
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"[ERROR] Manifest not found: {manifest_path}", file=sys.stderr)
        return None, None
    print(f"[GENERATE] Parsing manifest: {manifest_path}")
    parser = ManifestParser(base_dir=manifest_path.parent)
    blocks = parser.parse_file(manifest_path)
    return parser, blocks


def _generate_build_graph(blocks: list, args: argparse.Namespace):
    doql_blocks = [b for b in blocks if b.kind == "doql"]
    graph_blocks = [b for b in blocks if b.kind == "graph"]
    file_blocks = [b for b in blocks if b.kind == "file"]

    print(
        f"[GENERATE] Found {len(blocks)} blocks: "
        f"doql={len(doql_blocks)} graph={len(graph_blocks)} file={len(file_blocks)}"
    )

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
                graph.services[svc_name] = Service(
                    name=svc_name, routes={r: {} for r in routes}
                )
    else:
        print(
            "[ERROR] No markpact:doql or markpact:graph blocks found.",
            file=sys.stderr,
        )
        return None

    print(
        f"[GENERATE] ProjectGraph: {len(graph.models)} models, "
        f"{len(graph.services)} services, {len(graph.ui_bindings)} ui_bindings"
    )
    return graph


def _generate_check_files(manifest_path: Path, args: argparse.Namespace) -> int:
    if not args.check_files:
        return 0
    engine = ManifestSyncEngine(base_dir=manifest_path.parent)
    diffs = engine.diff(manifest_path)
    drifted = [d for d in diffs if d[1] != "ok" and d[1] != "untracked"]
    print(f"[GENERATE] Check files: {len(diffs)} tracked, {len(drifted)} drifted")
    for path, status, detail in diffs:
        if status != "untracked":
            print(f"  [{status}] {path} ({detail})")
    if drifted and args.mode == "STRICT":
        return 1
    return 0


def _generate_update_from_disk(manifest_path: Path, args: argparse.Namespace) -> None:
    if not args.from_disk and not args.from_disk_dry_run:
        return
    engine = ManifestSyncEngine(base_dir=manifest_path.parent)
    updated = engine.update_manifest(manifest_path, dry_run=args.from_disk_dry_run)
    mode_str = "(dry-run)" if args.from_disk_dry_run else ""
    print(f"[GENERATE] Update manifest from disk {mode_str}: {len(updated)} block(s)")
    for u in updated:
        print(f"  <- {u}")


def _generate_sync_files(manifest_path: Path, args: argparse.Namespace) -> None:
    if not args.sync_files and not args.sync_files_dry_run:
        return
    engine = ManifestSyncEngine(base_dir=manifest_path.parent)
    written = engine.sync_to_disk(manifest_path, dry_run=args.sync_files_dry_run)
    mode_str = "(dry-run)" if args.sync_files_dry_run else ""
    print(f"[GENERATE] Sync files {mode_str}: {len(written)} file(s)")
    for w in written:
        print(f"  -> {w}")


def _generate_outputs(runtime: SwopRuntime, args: argparse.Namespace) -> None:
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


def _cmd_generate(args: argparse.Namespace) -> int:
    parser, blocks = _generate_parse_manifest(args)
    if blocks is None:
        return 2

    graph = _generate_build_graph(blocks, args)
    if graph is None:
        return 2

    manifest_path = Path(args.manifest)

    exit_code = _generate_check_files(manifest_path, args)
    if exit_code:
        return exit_code

    _generate_update_from_disk(manifest_path, args)
    _generate_sync_files(manifest_path, args)

    runtime = SwopRuntime(mode=args.mode)
    runtime.graph = graph

    if args.sync:
        drift = runtime.run_sync()
        if drift.exists():
            print(f"[GENERATE] Drift detected (mode={args.mode})")
            if args.mode == "STRICT":
                exit_code = 1

    _generate_outputs(runtime, args)
    return exit_code
