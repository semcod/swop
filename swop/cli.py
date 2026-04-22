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
import sys
from typing import List, Optional

from swop.core import SwopRuntime


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

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
