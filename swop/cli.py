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
from swop.refactor import RefactorPipeline


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

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
