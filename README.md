# swop

**Bi-directional runtime reconciler and drift-aware state graph for full-stack systems.**

[![Version](https://img.shields.io/badge/version-0.2.11-blue)](VERSION)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.2.11-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$2.55-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-7.6h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $2.5500 (17 commits)
- 👤 **Human dev:** ~$758 (7.6h @ $100/h, 30min dedup)

Generated on 2026-04-24 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

Swop is a Python toolkit for inspecting, reconciling, and maintaining the
architecture of full-stack CQRS projects. It scans Python source for
commands, queries, events, and handlers; generates deterministic manifests;
detects schema drift; and exports the runtime state graph to multiple formats.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CQRS Decorators](#cqrs-decorators)
- [CLI Reference](#cli-reference)
- [Python API](#python-api)
- [Configuration](#configuration)
- [Manifest Generation](#manifest-generation)
- [Watch Mode](#watch-mode)
- [Drift Detection & Resolution](#drift-detection--resolution)
- [Refactoring](#refactoring)
- [Registry Generation](#registry-generation)
- [Markpact Generation](#markpact-generation)
- [Development](#development)
- [License](#license)

---

## Installation

```bash
pip install swop
```

Development install:

```bash
pip install -e ".[dev]"
```

Requires Python 3.8+ and PyYAML.

---

## Quick Start

### 1. Initialise a project

```bash
swop init
```

Scaffolds `swop.yaml` and the `.swop/` state directory in the current folder.

### 2. Annotate your domain code

```python
from dataclasses import dataclass
from swop import command, handler

@command("billing")
@dataclass
class IssueInvoice:
    customer_id: int
    amount: float

@handler(IssueInvoice)
class IssueInvoiceHandler:
    def handle(self, cmd: IssueInvoice) -> int:
        return cmd.customer_id
```

### 3. Scan and generate manifests

```bash
swop scan --format json
swop gen manifests
```

### 4. Watch for changes

```bash
swop watch
```

Re-runs the scan and regenerates manifests automatically when any `.py` file
changes.

---

## CQRS Decorators

`swop` provides lightweight, no-op decorators that register decorated classes
in a module-global registry. They do not change runtime behaviour, so existing
code continues to work unchanged.

| Decorator | Purpose | Example |
|---|---|---|
| `@command(context)` | Register a command | `@command("billing") @dataclass class IssueInvoice: ...` |
| `@query(context)` | Register a query | `@query("catalog") @dataclass class ListProducts: ...` |
| `@event(context, emits=[...])` | Register a domain event | `@event("billing", emits=["InvoiceIssued"]) class PaymentReceived: ...` |
| `@handler(Target)` | Register a command/query handler | `@handler(IssueInvoice) class IssueInvoiceHandler: ...` |

All decorators expose a `__swop_cqrs__` attribute on the decorated class with
metadata including `kind`, `context`, `source_file`, and `source_line`.

---

## CLI Reference

```
swop [--mode {STRICT,SOFT,OBSERVE,AUTO_HEAL}] <command>
```

| Command | Description |
|---|---|
| `swop init` | Scaffold `swop.yaml` and `.swop/` state dir |
| `swop scan [--format {text,json,html}] [--json-out FILE] [--html-out FILE] [--strict-heuristics] [--strict-errors]` | Walk source roots and classify CQRS artifacts |
| `swop gen manifests` | Generate per-context YAML manifests |
| `swop gen proto [--out PATH]` | Generate `.proto` from manifests |
| `swop gen grpc-python` | Compile Python gRPC bindings |
| `swop gen grpc-ts` | Compile TypeScript gRPC bindings |
| `swop gen services [--bus TYPE] [--base-image IMG] [--grpc-port N]` | Generate service stubs + docker-compose.cqrs.yml from manifests |
| `swop watch [--once]` | Watch source files and rebuild on change |
| `swop sync` | Run one reconciliation pass |
| `swop diff` | Compute drift and exit non-zero if drift exists |
| `swop state` | Dump current runtime state as YAML |
| `swop inspect backend\|frontend` | Introspect actual runtime state |
| `swop resolve` | Diff current scan against stored manifests |
| `swop gen registry [--contracts DIR] [--check]` | Generate `registry.json` + `REGISTRY.md` from `contracts/*.json` files |
| `swop generate --from-markpact FILE.md [--sync] [--sync-files] [--check-files] [--output-yaml PATH] [--output-docker PATH]` | Build a ProjectGraph from a Markpact manifest |
| `swop refactor --frontend PATH [--backend PATH] [--db PATH] [--route /path] [--strategy {seeded,louvain}] --out <dir>` | Extract modules into a new directory |
| `swop doctor [--deep]` | Verify the local swop environment |
| `swop hook install\|uninstall\|status` | Manage the git pre-commit hook |

### Reconciliation modes

| Mode | Behaviour |
|---|---|
| `STRICT` | Fail on any drift |
| `SOFT` | Log drift, continue (default) |
| `OBSERVE` | Read-only, never modify |
| `AUTO_HEAL` | Apply detected fixes automatically |

---

## Python API

### Scan a project

```python
from swop import scan_project, load_config

cfg = load_config("swop.yaml")
report = scan_project(cfg)

for det in report.detections:
    print(f"{det.kind:8} {det.name:20} ({det.confidence:.1f} via {det.via})")
```

### Generate manifests

```python
from swop import generate_manifests

manifests = generate_manifests(report, cfg)
for mf in manifests.files:
    print(mf.path)
```

### Watch programmatically

```python
from swop import WatchEngine, load_config

cfg = load_config("swop.yaml")
engine = WatchEngine(config=cfg, interval=0.5, debounce=0.3)

# Single-shot rebuild
from swop import rebuild_once
result = rebuild_once(cfg, incremental=True)
print(result.format())
```

### Runtime graph

```python
from swop import SwopRuntime

rt = SwopRuntime(mode="SOFT")
rt.add_model("Pressure", ["temp", "pressure_low", "pressure_high"])
rt.add_service("api", ["/pressure", "/status"])
rt.add_ui_binding("#sensor-temp", "temp")

drift = rt.run_sync()
print(rt.state_yaml())
```

---

## Configuration

`swop.yaml` describes the project structure:

```yaml
version: 1
project: my-service
source_roots: [src]
exclude: ["tests/*", "__pycache__/*"]
bounded_contexts:
  - name: billing
    source: src/billing
  - name: catalog
    source: src/catalog
    external: false
bus:
  type: rabbitmq
  url: amqp://localhost
read_models:
  engine: postgresql
  url: postgresql://localhost/mydb
state_dir: .swop
```

| Key | Description |
|---|---|
| `source_roots` | Directories to scan (relative to project root) |
| `bounded_contexts` | Named contexts with source paths |
| `exclude` | Glob patterns to skip |
| `bus` | Message-bus configuration |
| `read_models` | Read-model store configuration |
| `state_dir` | Local state / cache directory |

---

## Manifest Generation

For each bounded context swop generates three manifest files under
`.swop/manifests/<context>/`:

- `commands.yml` — all detected commands with fields
- `queries.yml` — all detected queries with fields
- `events.yml` — all detected events with fields

Example output (`billing/commands.yml`):

```yaml
version: 1
context: billing
commands:
  IssueInvoice:
    module: billing.ops
    fields:
      - name: customer_id
        type: int
        required: true
      - name: amount
        type: float
        required: true
```

These manifests are the single source of truth for downstream generators
(proto, gRPC, service stubs).

---

## Watch Mode

The watcher uses stdlib-only `mtime` polling — no extra dependencies.

```bash
# Continuous watch
swop watch

# One-shot (CI friendly)
swop watch --once --no-incremental
```

The watcher automatically:
- Skips the state directory (`.swop/`) so regenerated manifests do not
  re-trigger a rebuild.
- Debounces bursts of changes into a single rebuild pass.
- Tracks file creation, modification, and deletion.

---

## Drift Detection & Resolution

Swop compares the *expected* state (from manifests) with the *actual* state
(introspected from running backend/frontend) and reports drift:

```bash
swop diff
swop resolve [--json] [--apply] [--strict] [--no-incremental]
```

Drift categories:
- `schema` — field additions, removals, type changes
- `missing` — expected artifacts not found in runtime
- `unexpected` — runtime artifacts not in manifests

Use `swop sync --mode AUTO_HEAL` to apply fixes automatically.

---

## Refactoring

Extract modules from a full-stack project into a clean output directory:

```bash
swop refactor --out ./refactored
```

The refactor pipeline clusters related code, builds a composed module graph,
and generates new file layouts while preserving behaviour.

---

## Registry Generation

Generate a `registry.json` and `REGISTRY.md` from JSON contract files in a `contracts/` directory:

```bash
swop gen registry [--contracts DIR] [--check]
```

| Flag | Description |
|---|---|
| `--contracts DIR` | Contracts directory (default: `<root>/contracts`) |
| `--check` | Validate only; do not write output files |

---

## Markpact Generation

Build a `SwopRuntime` graph directly from a Markpact manifest (`.md` file with `markpact:*` blocks):

```bash
swop generate --from-markpact manifest.md \
  [--strict] [--sync] [--sync-files] [--sync-files-dry-run] \
  [--check-files] [--from-disk] [--from-disk-dry-run] \
  [--output-yaml PATH] [--output-docker PATH]
```

| Flag | Description |
|---|---|
| `--from-markpact FILE` | Path to Markpact manifest (required) |
| `--strict` | Fail fast on any DOQL parse error |
| `--sync` | Run sync engine after building the graph |
| `--sync-files` | Materialise `markpact:file` blocks to their declared paths |
| `--sync-files-dry-run` | Report which files would be written without writing |
| `--check-files` | Report drift between `markpact:file` blocks and filesystem |
| `--from-disk` | Reverse sync: rewrite blocks with disk content |
| `--from-disk-dry-run` | Report which blocks would be updated without writing |
| `--output-yaml PATH` | Write runtime state YAML to this path |
| `--output-docker PATH` | Write docker-compose YAML to this path |

---

## Development

### Run tests

```bash
pytest
```

160 tests, all passing.

### Project structure

```
swop/
├── cli.py              # CLI entry point
├── commands.py         # Command implementations
├── config.py           # swop.yaml loader
├── core.py             # SwopRuntime orchestrator
├── cqrs/               # @command, @query, @event, @handler decorators
├── graph.py            # ProjectGraph, DataModel, Service
├── introspect/         # Backend & frontend state introspection
├── manifests/          # YAML manifest generator
├── markpact/           # Manifest parsing and sync engine
├── proto/              # Protobuf generation & compilation
├── reconcile.py        # Drift detection & resync
├── refactor/           # Code clustering & module extraction
├── resolve.py          # Schema-evolution resolution
├── scan/               # AST scanner for CQRS artifacts
├── services/           # Service stub generator
├── sync.py             # Sync engine
├── tools/              # Project init, doctor, git hooks
├── versioning.py       # Graph versioning
└── watch/              # mtime-polling file watcher
```

---

## License

Licensed under Apache-2.0.
