# swop

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `swop`
- **version**: `0.2.16`
- **python_requires**: `>=3.8`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(9 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: swop;
  version: 0.2.16;
}

dependencies {
  runtime: pyyaml>=6.0;
  dev: "pytest>=9.0.0, pytest-cov>=7.0.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="swop"] {

}

deploy {
  target: pip;
}

environment[name="local"] {
  runtime: python;
  env_file: .env;
  python_version: >=3.8;
}
```

### Source Modules

- `swop.cli`
- `swop.commands`
- `swop.config`
- `swop.core`
- `swop.graph`
- `swop.reconcile`
- `swop.sync`
- `swop.utils`
- `swop.versioning`

## Dependencies

### Runtime

```text markpact:deps python
pyyaml>=6.0
```

### Development

```text markpact:deps python scope=dev
pytest>=9.0.0
pytest-cov>=7.0.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `swop.commands` (`swop/commands.py`)

```python
def _build_runtime(mode)  # CC=1, fan=4
def _cmd_sync(args)  # CC=3, fan=3
def _cmd_inspect(args)  # CC=3, fan=3
def _cmd_diff(args)  # CC=2, fan=3
def _cmd_state(args)  # CC=1, fan=4
def _cmd_export(args)  # CC=2, fan=3
def _cmd_doctor(args)  # CC=7, fan=9
def _cmd_hook(args)  # CC=6, fan=10
def _cmd_init(args)  # CC=2, fan=6
def _cmd_scan(args)  # CC=14, fan=12 ⚠
def _cmd_gen_manifests(args)  # CC=8, fan=8
def _cmd_gen_proto(args)  # CC=7, fan=8
def _cmd_gen_grpc_python(args)  # CC=7, fan=7
def _cmd_gen_grpc_ts(args)  # CC=7, fan=7
def _cmd_gen_services(args)  # CC=12, fan=8 ⚠
def _cmd_gen_registry(args)  # CC=14, fan=10 ⚠
def _cmd_watch(args)  # CC=6, fan=11
def _cmd_resolve(args)  # CC=9, fan=10
def _cmd_refactor(args)  # CC=7, fan=7
def _generate_parse_manifest(args)  # CC=2, fan=5
def _generate_build_graph(blocks, args)  # CC=14, fan=12 ⚠
def _generate_check_files(manifest_path, args)  # CC=9, fan=4
def _generate_update_from_disk(manifest_path, args)  # CC=5, fan=4
def _generate_sync_files(manifest_path, args)  # CC=5, fan=4
def _generate_outputs(runtime, args)  # CC=5, fan=5
def _cmd_generate(args)  # CC=7, fan=11
```

### `swop.config` (`swop/config.py`)

```python
def _expand_env(value)  # CC=6, fan=6
def _pop_known(data, keys)  # CC=3, fan=1
def _parse_context(raw)  # CC=3, fan=7
def _parse_bus(raw)  # CC=3, fan=8
def _parse_read_models(raw)  # CC=3, fan=8
def load_config(path)  # CC=6, fan=10
def _from_dict(data, cfg_path)  # CC=8, fan=12
class SwopConfigError:  # Raised when ``swop.yaml`` is malformed.
class BoundedContextConfig:
class BusConfig:
class ReadModelConfig:
class SwopConfig:
    def project_root()  # CC=2
    def state_path()  # CC=1
    def context(name)  # CC=3
    def iter_source_roots()  # CC=2
```

### `swop.core` (`swop/core.py`)

```python
class SwopRuntime:  # Main orchestrator for the swop reconciliation system.
    def __init__(mode, backend, frontend)  # CC=3
    def add_model(name, fields, field_type)  # CC=2
    def add_service(name, routes)  # CC=2
    def add_ui_binding(selector, model_field)  # CC=1
    def introspect()  # CC=1
    def run_sync()  # CC=1
    def state_yaml()  # CC=2
    def docker_compose()  # CC=1
```

### `swop.reconcile` (`swop/reconcile.py`)

```python
class DriftError:  # Raised when drift is detected while running in STRICT mode.
class Drift:
    def exists()  # CC=4
class DriftDetector:  # Compare a declared graph with the actual runtime state.
    def compute(graph, actual)  # CC=7
class ResyncEngine:  # Continuously reconcile the declared graph against actual sta
    def __init__(mode)  # CC=1
    def reconcile(graph, actual)  # CC=4
    def _has_critical(drift)  # CC=2
    def _auto_heal(graph, drift)  # CC=4
    def _log_drift(drift)  # CC=1
```

### `swop.sync` (`swop/sync.py`)

```python
class SyncEngine:  # Move state between a ``ProjectGraph`` and introspected snaps
    def frontend_to_graph(selectors)  # CC=2
    def merge_frontend(graph, selectors)  # CC=4
    def merge_backend(graph, backend_state)  # CC=7
```

## Call Graph

*196 nodes · 203 edges · 24 modules · CC̄=4.7*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_build_parser` *(in swop.cli)* | 1 | 1 | 133 | **134** |
| `generate_registry_md` *(in swop.registry.generator)* | 32 ⚠ | 1 | 65 | **66** |
| `render_proto_for_context` *(in swop.proto.generator)* | 26 ⚠ | 1 | 64 | **65** |
| `_diff_fields` *(in swop.resolve.resolver)* | 13 ⚠ | 1 | 59 | **60** |
| `_map_python_type` *(in swop.proto.generator)* | 18 ⚠ | 3 | 32 | **35** |
| `render_html` *(in swop.scan.render)* | 8 | 1 | 25 | **26** |
| `_from_dict` *(in swop.config)* | 8 | 1 | 25 | **26** |
| `init_project` *(in swop.tools.init)* | 14 ⚠ | 1 | 25 | **26** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/swop
# generated in 0.09s
# nodes: 196 | edges: 203 | modules: 24
# CC̄=4.7

HUBS[20]:
  swop.cli._build_parser
    CC=1  in:1  out:133  total:134
  swop.registry.generator.generate_registry_md
    CC=32  in:1  out:65  total:66
  swop.proto.generator.render_proto_for_context
    CC=26  in:1  out:64  total:65
  swop.resolve.resolver._diff_fields
    CC=13  in:1  out:59  total:60
  swop.proto.generator._map_python_type
    CC=18  in:3  out:32  total:35
  swop.scan.render.render_html
    CC=8  in:1  out:25  total:26
  swop.config._from_dict
    CC=8  in:1  out:25  total:26
  swop.tools.init.init_project
    CC=14  in:1  out:25  total:26
  swop.tools.doctor_deep._check_proto_vs_python
    CC=15  in:1  out:25  total:26
  swop.tools.doctor_deep._check_manifests_vs_proto
    CC=15  in:1  out:24  total:25
  swop.proto.compiler.compile_proto_typescript
    CC=10  in:1  out:23  total:24
  swop.resolve.resolver._index_from_manifests
    CC=15  in:1  out:23  total:24
  swop.commands._generate_build_graph
    CC=14  in:1  out:22  total:23
  swop.tools.doctor_deep._check_manifests_vs_services
    CC=15  in:1  out:22  total:23
  swop.proto.compiler.compile_proto_python
    CC=8  in:1  out:21  total:22
  swop.commands._cmd_gen_registry
    CC=14  in:0  out:22  total:22
  swop.config.load_config
    CC=6  in:10  out:12  total:22
  swop.tools.hook._git_dir
    CC=13  in:1  out:20  total:21
  swop.scan.scanner._scan_file
    CC=13  in:1  out:20  total:21
  swop.services.generator._write_context_package
    CC=7  in:1  out:20  total:21

MODULES:
  swop.cli  [2 funcs]
    _build_parser  CC=1  out:133
    main  CC=1  out:3
  swop.commands  [25 funcs]
    _build_runtime  CC=1  out:4
    _cmd_diff  CC=2  out:3
    _cmd_doctor  CC=7  out:15
    _cmd_export  CC=2  out:4
    _cmd_gen_grpc_python  CC=7  out:11
    _cmd_gen_grpc_ts  CC=7  out:11
    _cmd_gen_manifests  CC=8  out:11
    _cmd_gen_proto  CC=7  out:13
    _cmd_gen_registry  CC=14  out:22
    _cmd_gen_services  CC=12  out:16
  swop.config  [7 funcs]
    _expand_env  CC=6  out:10
    _from_dict  CC=8  out:25
    _parse_bus  CC=3  out:9
    _parse_context  CC=3  out:8
    _parse_read_models  CC=3  out:9
    _pop_known  CC=3  out:1
    load_config  CC=6  out:12
  swop.contracts.adapter  [8 funcs]
    __init__  CC=1  out:1
    from_directory  CC=2  out:2
    _contract_context  CC=1  out:1
    _contract_fields  CC=4  out:11
    _contract_kind  CC=4  out:1
    _contract_name  CC=4  out:3
    contract_to_detection  CC=6  out:10
    contracts_to_detections  CC=4  out:6
  swop.contracts.reader  [4 funcs]
    _check_layer_paths  CC=6  out:6
    load_contracts  CC=5  out:8
    validate_all  CC=4  out:6
    validate_contract  CC=21  out:12
  swop.cqrs.decorators  [4 funcs]
    _collect_source  CC=3  out:2
    _make_decorator  CC=1  out:11
    _normalize_emits  CC=4  out:5
    handler  CC=7  out:12
  swop.manifests.generator  [31 funcs]
    _annotation_is_optional  CC=11  out:6
    _annotation_type_names  CC=6  out:3
    _camel_to_dot  CC=5  out:9
    _collect_supporting_types  CC=1  out:2
    _collect_supporting_types_from_fields  CC=7  out:12
    _dedupe_type_defs  CC=4  out:7
    _expr_name  CC=4  out:4
    _extract_class_fields  CC=16  out:17
    _find_class_in_module  CC=1  out:2
    _find_handler_return_type  CC=6  out:2
  swop.markpact.graph_builder  [10 funcs]
    _build_api_clients  CC=8  out:6
    _build_databases  CC=6  out:6
    _build_integrations  CC=4  out:5
    _build_models  CC=7  out:7
    _build_roles  CC=6  out:4
    _build_services  CC=13  out:14
    _build_ui_bindings  CC=11  out:12
    _build_webhooks  CC=7  out:6
    _build_workflows  CC=9  out:11
    build_project_graph  CC=1  out:19
  swop.markpact.sync_engine  [2 funcs]
    check  CC=7  out:11
    _hash  CC=1  out:3
  swop.proto.compiler  [4 funcs]
    _iter_proto_files  CC=1  out:3
    _run  CC=2  out:3
    compile_proto_python  CC=8  out:21
    compile_proto_typescript  CC=10  out:23
  swop.proto.generator  [10 funcs]
    _collect_known_types  CC=6  out:7
    _iter_contexts  CC=6  out:7
    _load_manifest  CC=4  out:4
    _map_python_type  CC=18  out:32
    _render_enum  CC=7  out:12
    _render_message  CC=13  out:14
    _render_type_definition  CC=7  out:8
    _safe_ident  CC=3  out:3
    generate_proto_from_manifests  CC=8  out:20
    render_proto_for_context  CC=26  out:64
  swop.refactor.pipeline  [2 funcs]
    _link_models_to_ui  CC=8  out:7
    _tokenize  CC=4  out:4
  swop.registry.generator  [3 funcs]
    generate_registry_json  CC=7  out:17
    generate_registry_md  CC=32  out:65
    write_registry  CC=2  out:14
  swop.registry.pydantic_cross_check  [10 funcs]
    _collect_literal_fields  CC=7  out:5
    _contract_schemas  CC=3  out:3
    _extract_literal_values  CC=7  out:8
    _iter_enum_fields  CC=12  out:13
    _literal_slice_values  CC=6  out:6
    _load_literal_fields  CC=3  out:3
    _node_name  CC=4  out:3
    _parse_layer_path  CC=4  out:2
    cross_check_contract  CC=14  out:18
    cross_check_contracts  CC=2  out:1
  swop.registry.validator  [4 funcs]
    _check_keys  CC=3  out:1
    _check_kind  CC=2  out:3
    _check_layer_paths  CC=7  out:7
    validate_contract  CC=5  out:11
  swop.resolve.resolver  [9 funcs]
    _diff_entry  CC=3  out:4
    _diff_fields  CC=13  out:59
    _diff_metadata  CC=9  out:16
    _handler_shape  CC=3  out:0
    _handler_sig  CC=8  out:4
    _index_from_detections  CC=10  out:8
    _index_from_manifests  CC=15  out:23
    apply_resolution  CC=3  out:2
    resolve_schema_drift  CC=4  out:14
  swop.scan.render  [3 funcs]
    render_html  CC=8  out:25
    render_json  CC=2  out:2
    write_report  CC=3  out:8
  swop.scan.scanner  [26 funcs]
    _annotation_is_optional  CC=13  out:7
    _base_name  CC=3  out:2
    _classify  CC=9  out:5
    _classify_decorator  CC=5  out:6
    _classify_heuristic  CC=7  out:6
    _context_for_path  CC=8  out:4
    _decorator_name  CC=4  out:4
    _extract_ann_field  CC=7  out:7
    _extract_decorator_context  CC=8  out:4
    _extract_decorator_emits  CC=9  out:8
  swop.services.generator  [11 funcs]
    _camel  CC=4  out:3
    _default_bus_url  CC=1  out:1
    _render_compose  CC=6  out:8
    _render_dockerfile  CC=1  out:0
    _render_init  CC=1  out:0
    _render_publisher  CC=1  out:0
    _render_requirements  CC=4  out:4
    _render_server  CC=7  out:9
    _render_worker  CC=2  out:0
    _safe_ident  CC=3  out:3
  swop.tools.doctor  [4 funcs]
    _check_binary  CC=4  out:5
    _first_version  CC=3  out:2
    _run_version  CC=5  out:3
    run_doctor  CC=2  out:17
  swop.tools.doctor_deep  [6 funcs]
    _check_manifests_vs_proto  CC=15  out:24
    _check_manifests_vs_services  CC=15  out:22
    _check_proto_vs_python  CC=15  out:25
    _check_scan_vs_manifests  CC=8  out:10
    _latest_mtime  CC=6  out:4
    run_deep_doctor  CC=1  out:9
  swop.tools.hook  [7 funcs]
    _git_dir  CC=13  out:20
    _hook_path  CC=2  out:2
    _is_swop_hook  CC=2  out:1
    _make_executable  CC=2  out:2
    hook_status  CC=4  out:7
    install_hook  CC=5  out:8
    uninstall_hook  CC=4  out:8
  swop.tools.init  [1 funcs]
    init_project  CC=14  out:25
  swop.watch.engine  [3 funcs]
    poll_once  CC=5  out:7
    _diff_snapshots  CC=5  out:6
    rebuild_once  CC=2  out:6

EDGES:
  swop.cli.main → swop.cli._build_parser
  swop.scan.render.write_report → swop.scan.render.render_json
  swop.scan.render.write_report → swop.scan.render.render_html
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_models
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_services
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_ui_bindings
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_databases
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_workflows
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_roles
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_integrations
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_webhooks
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_api_clients
  swop.registry.pydantic_cross_check._extract_literal_values → swop.registry.pydantic_cross_check._node_name
  swop.registry.pydantic_cross_check._extract_literal_values → swop.registry.pydantic_cross_check._literal_slice_values
  swop.registry.pydantic_cross_check._collect_literal_fields → swop.registry.pydantic_cross_check._extract_literal_values
  swop.registry.pydantic_cross_check._load_literal_fields → swop.registry.pydantic_cross_check._collect_literal_fields
  swop.registry.pydantic_cross_check.cross_check_contract → swop.registry.pydantic_cross_check._parse_layer_path
  swop.registry.pydantic_cross_check.cross_check_contract → swop.registry.pydantic_cross_check._load_literal_fields
  swop.registry.pydantic_cross_check.cross_check_contract → swop.registry.pydantic_cross_check._contract_schemas
  swop.registry.pydantic_cross_check.cross_check_contract → swop.registry.pydantic_cross_check._iter_enum_fields
  swop.registry.pydantic_cross_check.cross_check_contracts → swop.registry.pydantic_cross_check.cross_check_contract
  swop.registry.generator.write_registry → swop.registry.generator.generate_registry_json
  swop.registry.generator.write_registry → swop.registry.generator.generate_registry_md
  swop.proto.generator.generate_proto_from_manifests → swop.proto.generator._iter_contexts
  swop.proto.generator.generate_proto_from_manifests → swop.proto.generator._load_manifest
  swop.proto.generator.generate_proto_from_manifests → swop.proto.generator.render_proto_for_context
  swop.proto.generator.render_proto_for_context → swop.proto.generator._collect_known_types
  swop.proto.generator._render_message → swop.proto.generator._safe_ident
  swop.proto.generator._render_message → swop.proto.generator._map_python_type
  swop.proto.generator._render_type_definition → swop.proto.generator._render_message
  swop.proto.generator._render_type_definition → swop.proto.generator._render_enum
  swop.proto.generator._render_enum → swop.proto.generator._safe_ident
  swop.proto.compiler.compile_proto_python → swop.proto.compiler._iter_proto_files
  swop.proto.compiler.compile_proto_typescript → swop.proto.compiler._iter_proto_files
  swop.proto.compiler.compile_proto_typescript → swop.proto.compiler._run
  swop.markpact.sync_engine.ManifestSyncEngine.check → swop.markpact.sync_engine._hash
  swop.contracts.adapter._contract_fields → swop.contracts.adapter._contract_kind
  swop.contracts.adapter.contract_to_detection → swop.contracts.adapter._contract_kind
  swop.contracts.adapter.contract_to_detection → swop.contracts.adapter._contract_name
  swop.contracts.adapter.contract_to_detection → swop.contracts.adapter._contract_context
  swop.contracts.adapter.contract_to_detection → swop.contracts.adapter._contract_fields
  swop.contracts.adapter.contracts_to_detections → swop.contracts.adapter.contract_to_detection
  swop.contracts.adapter.ContractDetectionAdapter.__init__ → swop.contracts.adapter.contracts_to_detections
  swop.contracts.adapter.ContractDetectionAdapter.from_directory → swop.contracts.reader.load_contracts
  swop.contracts.reader.validate_contract → swop.contracts.reader._check_layer_paths
  swop.contracts.reader.validate_all → swop.contracts.reader.validate_contract
  swop.tools.hook._hook_path → swop.tools.hook._git_dir
  swop.tools.hook.install_hook → swop.tools.hook._hook_path
  swop.tools.hook.install_hook → swop.tools.hook._make_executable
  swop.tools.hook.install_hook → swop.tools.hook._is_swop_hook
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/swop
# generated in 0.09s
# nodes: 196 | edges: 203 | modules: 24
# CC̄=4.7

HUBS[20]:
  swop.cli._build_parser
    CC=1  in:1  out:133  total:134
  swop.registry.generator.generate_registry_md
    CC=32  in:1  out:65  total:66
  swop.proto.generator.render_proto_for_context
    CC=26  in:1  out:64  total:65
  swop.resolve.resolver._diff_fields
    CC=13  in:1  out:59  total:60
  swop.proto.generator._map_python_type
    CC=18  in:3  out:32  total:35
  swop.scan.render.render_html
    CC=8  in:1  out:25  total:26
  swop.config._from_dict
    CC=8  in:1  out:25  total:26
  swop.tools.init.init_project
    CC=14  in:1  out:25  total:26
  swop.tools.doctor_deep._check_proto_vs_python
    CC=15  in:1  out:25  total:26
  swop.tools.doctor_deep._check_manifests_vs_proto
    CC=15  in:1  out:24  total:25
  swop.proto.compiler.compile_proto_typescript
    CC=10  in:1  out:23  total:24
  swop.resolve.resolver._index_from_manifests
    CC=15  in:1  out:23  total:24
  swop.commands._generate_build_graph
    CC=14  in:1  out:22  total:23
  swop.tools.doctor_deep._check_manifests_vs_services
    CC=15  in:1  out:22  total:23
  swop.proto.compiler.compile_proto_python
    CC=8  in:1  out:21  total:22
  swop.commands._cmd_gen_registry
    CC=14  in:0  out:22  total:22
  swop.config.load_config
    CC=6  in:10  out:12  total:22
  swop.tools.hook._git_dir
    CC=13  in:1  out:20  total:21
  swop.scan.scanner._scan_file
    CC=13  in:1  out:20  total:21
  swop.services.generator._write_context_package
    CC=7  in:1  out:20  total:21

MODULES:
  swop.cli  [2 funcs]
    _build_parser  CC=1  out:133
    main  CC=1  out:3
  swop.commands  [25 funcs]
    _build_runtime  CC=1  out:4
    _cmd_diff  CC=2  out:3
    _cmd_doctor  CC=7  out:15
    _cmd_export  CC=2  out:4
    _cmd_gen_grpc_python  CC=7  out:11
    _cmd_gen_grpc_ts  CC=7  out:11
    _cmd_gen_manifests  CC=8  out:11
    _cmd_gen_proto  CC=7  out:13
    _cmd_gen_registry  CC=14  out:22
    _cmd_gen_services  CC=12  out:16
  swop.config  [7 funcs]
    _expand_env  CC=6  out:10
    _from_dict  CC=8  out:25
    _parse_bus  CC=3  out:9
    _parse_context  CC=3  out:8
    _parse_read_models  CC=3  out:9
    _pop_known  CC=3  out:1
    load_config  CC=6  out:12
  swop.contracts.adapter  [8 funcs]
    __init__  CC=1  out:1
    from_directory  CC=2  out:2
    _contract_context  CC=1  out:1
    _contract_fields  CC=4  out:11
    _contract_kind  CC=4  out:1
    _contract_name  CC=4  out:3
    contract_to_detection  CC=6  out:10
    contracts_to_detections  CC=4  out:6
  swop.contracts.reader  [4 funcs]
    _check_layer_paths  CC=6  out:6
    load_contracts  CC=5  out:8
    validate_all  CC=4  out:6
    validate_contract  CC=21  out:12
  swop.cqrs.decorators  [4 funcs]
    _collect_source  CC=3  out:2
    _make_decorator  CC=1  out:11
    _normalize_emits  CC=4  out:5
    handler  CC=7  out:12
  swop.manifests.generator  [31 funcs]
    _annotation_is_optional  CC=11  out:6
    _annotation_type_names  CC=6  out:3
    _camel_to_dot  CC=5  out:9
    _collect_supporting_types  CC=1  out:2
    _collect_supporting_types_from_fields  CC=7  out:12
    _dedupe_type_defs  CC=4  out:7
    _expr_name  CC=4  out:4
    _extract_class_fields  CC=16  out:17
    _find_class_in_module  CC=1  out:2
    _find_handler_return_type  CC=6  out:2
  swop.markpact.graph_builder  [10 funcs]
    _build_api_clients  CC=8  out:6
    _build_databases  CC=6  out:6
    _build_integrations  CC=4  out:5
    _build_models  CC=7  out:7
    _build_roles  CC=6  out:4
    _build_services  CC=13  out:14
    _build_ui_bindings  CC=11  out:12
    _build_webhooks  CC=7  out:6
    _build_workflows  CC=9  out:11
    build_project_graph  CC=1  out:19
  swop.markpact.sync_engine  [2 funcs]
    check  CC=7  out:11
    _hash  CC=1  out:3
  swop.proto.compiler  [4 funcs]
    _iter_proto_files  CC=1  out:3
    _run  CC=2  out:3
    compile_proto_python  CC=8  out:21
    compile_proto_typescript  CC=10  out:23
  swop.proto.generator  [10 funcs]
    _collect_known_types  CC=6  out:7
    _iter_contexts  CC=6  out:7
    _load_manifest  CC=4  out:4
    _map_python_type  CC=18  out:32
    _render_enum  CC=7  out:12
    _render_message  CC=13  out:14
    _render_type_definition  CC=7  out:8
    _safe_ident  CC=3  out:3
    generate_proto_from_manifests  CC=8  out:20
    render_proto_for_context  CC=26  out:64
  swop.refactor.pipeline  [2 funcs]
    _link_models_to_ui  CC=8  out:7
    _tokenize  CC=4  out:4
  swop.registry.generator  [3 funcs]
    generate_registry_json  CC=7  out:17
    generate_registry_md  CC=32  out:65
    write_registry  CC=2  out:14
  swop.registry.pydantic_cross_check  [10 funcs]
    _collect_literal_fields  CC=7  out:5
    _contract_schemas  CC=3  out:3
    _extract_literal_values  CC=7  out:8
    _iter_enum_fields  CC=12  out:13
    _literal_slice_values  CC=6  out:6
    _load_literal_fields  CC=3  out:3
    _node_name  CC=4  out:3
    _parse_layer_path  CC=4  out:2
    cross_check_contract  CC=14  out:18
    cross_check_contracts  CC=2  out:1
  swop.registry.validator  [4 funcs]
    _check_keys  CC=3  out:1
    _check_kind  CC=2  out:3
    _check_layer_paths  CC=7  out:7
    validate_contract  CC=5  out:11
  swop.resolve.resolver  [9 funcs]
    _diff_entry  CC=3  out:4
    _diff_fields  CC=13  out:59
    _diff_metadata  CC=9  out:16
    _handler_shape  CC=3  out:0
    _handler_sig  CC=8  out:4
    _index_from_detections  CC=10  out:8
    _index_from_manifests  CC=15  out:23
    apply_resolution  CC=3  out:2
    resolve_schema_drift  CC=4  out:14
  swop.scan.render  [3 funcs]
    render_html  CC=8  out:25
    render_json  CC=2  out:2
    write_report  CC=3  out:8
  swop.scan.scanner  [26 funcs]
    _annotation_is_optional  CC=13  out:7
    _base_name  CC=3  out:2
    _classify  CC=9  out:5
    _classify_decorator  CC=5  out:6
    _classify_heuristic  CC=7  out:6
    _context_for_path  CC=8  out:4
    _decorator_name  CC=4  out:4
    _extract_ann_field  CC=7  out:7
    _extract_decorator_context  CC=8  out:4
    _extract_decorator_emits  CC=9  out:8
  swop.services.generator  [11 funcs]
    _camel  CC=4  out:3
    _default_bus_url  CC=1  out:1
    _render_compose  CC=6  out:8
    _render_dockerfile  CC=1  out:0
    _render_init  CC=1  out:0
    _render_publisher  CC=1  out:0
    _render_requirements  CC=4  out:4
    _render_server  CC=7  out:9
    _render_worker  CC=2  out:0
    _safe_ident  CC=3  out:3
  swop.tools.doctor  [4 funcs]
    _check_binary  CC=4  out:5
    _first_version  CC=3  out:2
    _run_version  CC=5  out:3
    run_doctor  CC=2  out:17
  swop.tools.doctor_deep  [6 funcs]
    _check_manifests_vs_proto  CC=15  out:24
    _check_manifests_vs_services  CC=15  out:22
    _check_proto_vs_python  CC=15  out:25
    _check_scan_vs_manifests  CC=8  out:10
    _latest_mtime  CC=6  out:4
    run_deep_doctor  CC=1  out:9
  swop.tools.hook  [7 funcs]
    _git_dir  CC=13  out:20
    _hook_path  CC=2  out:2
    _is_swop_hook  CC=2  out:1
    _make_executable  CC=2  out:2
    hook_status  CC=4  out:7
    install_hook  CC=5  out:8
    uninstall_hook  CC=4  out:8
  swop.tools.init  [1 funcs]
    init_project  CC=14  out:25
  swop.watch.engine  [3 funcs]
    poll_once  CC=5  out:7
    _diff_snapshots  CC=5  out:6
    rebuild_once  CC=2  out:6

EDGES:
  swop.cli.main → swop.cli._build_parser
  swop.scan.render.write_report → swop.scan.render.render_json
  swop.scan.render.write_report → swop.scan.render.render_html
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_models
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_services
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_ui_bindings
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_databases
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_workflows
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_roles
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_integrations
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_webhooks
  swop.markpact.graph_builder.build_project_graph → swop.markpact.graph_builder._build_api_clients
  swop.registry.pydantic_cross_check._extract_literal_values → swop.registry.pydantic_cross_check._node_name
  swop.registry.pydantic_cross_check._extract_literal_values → swop.registry.pydantic_cross_check._literal_slice_values
  swop.registry.pydantic_cross_check._collect_literal_fields → swop.registry.pydantic_cross_check._extract_literal_values
  swop.registry.pydantic_cross_check._load_literal_fields → swop.registry.pydantic_cross_check._collect_literal_fields
  swop.registry.pydantic_cross_check.cross_check_contract → swop.registry.pydantic_cross_check._parse_layer_path
  swop.registry.pydantic_cross_check.cross_check_contract → swop.registry.pydantic_cross_check._load_literal_fields
  swop.registry.pydantic_cross_check.cross_check_contract → swop.registry.pydantic_cross_check._contract_schemas
  swop.registry.pydantic_cross_check.cross_check_contract → swop.registry.pydantic_cross_check._iter_enum_fields
  swop.registry.pydantic_cross_check.cross_check_contracts → swop.registry.pydantic_cross_check.cross_check_contract
  swop.registry.generator.write_registry → swop.registry.generator.generate_registry_json
  swop.registry.generator.write_registry → swop.registry.generator.generate_registry_md
  swop.proto.generator.generate_proto_from_manifests → swop.proto.generator._iter_contexts
  swop.proto.generator.generate_proto_from_manifests → swop.proto.generator._load_manifest
  swop.proto.generator.generate_proto_from_manifests → swop.proto.generator.render_proto_for_context
  swop.proto.generator.render_proto_for_context → swop.proto.generator._collect_known_types
  swop.proto.generator._render_message → swop.proto.generator._safe_ident
  swop.proto.generator._render_message → swop.proto.generator._map_python_type
  swop.proto.generator._render_type_definition → swop.proto.generator._render_message
  swop.proto.generator._render_type_definition → swop.proto.generator._render_enum
  swop.proto.generator._render_enum → swop.proto.generator._safe_ident
  swop.proto.compiler.compile_proto_python → swop.proto.compiler._iter_proto_files
  swop.proto.compiler.compile_proto_typescript → swop.proto.compiler._iter_proto_files
  swop.proto.compiler.compile_proto_typescript → swop.proto.compiler._run
  swop.markpact.sync_engine.ManifestSyncEngine.check → swop.markpact.sync_engine._hash
  swop.contracts.adapter._contract_fields → swop.contracts.adapter._contract_kind
  swop.contracts.adapter.contract_to_detection → swop.contracts.adapter._contract_kind
  swop.contracts.adapter.contract_to_detection → swop.contracts.adapter._contract_name
  swop.contracts.adapter.contract_to_detection → swop.contracts.adapter._contract_context
  swop.contracts.adapter.contract_to_detection → swop.contracts.adapter._contract_fields
  swop.contracts.adapter.contracts_to_detections → swop.contracts.adapter.contract_to_detection
  swop.contracts.adapter.ContractDetectionAdapter.__init__ → swop.contracts.adapter.contracts_to_detections
  swop.contracts.adapter.ContractDetectionAdapter.from_directory → swop.contracts.reader.load_contracts
  swop.contracts.reader.validate_contract → swop.contracts.reader._check_layer_paths
  swop.contracts.reader.validate_all → swop.contracts.reader.validate_contract
  swop.tools.hook._hook_path → swop.tools.hook._git_dir
  swop.tools.hook.install_hook → swop.tools.hook._hook_path
  swop.tools.hook.install_hook → swop.tools.hook._make_executable
  swop.tools.hook.install_hook → swop.tools.hook._is_swop_hook
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 76f 13663L | python:67,md:4,shell:2,yaml:1,json:1,toml:1 | 2026-05-29
# generated in 0.03s
# CC̅=4.7 | critical:10/425 | dups:0 | cycles:0

HEALTH[10]:
  🟡 CC    generate_registry_md CC=32 (limit:15)
  🟡 CC    _map_python_type CC=18 (limit:15)
  🟡 CC    render_proto_for_context CC=26 (limit:15)
  🟡 CC    validate_contract CC=21 (limit:15)
  🟡 CC    _extract_class_fields CC=16 (limit:15)
  🟡 CC    _cluster_to_spec CC=23 (limit:15)
  🟡 CC    _check_manifests_vs_proto CC=15 (limit:15)
  🟡 CC    _check_proto_vs_python CC=15 (limit:15)
  🟡 CC    _check_manifests_vs_services CC=15 (limit:15)
  🟡 CC    _index_from_manifests CC=15 (limit:15)

REFACTOR[1]:
  1. split 10 high-CC methods  (CC>15)

PIPELINES[211]:
  [1] Src [__init__]: __init__
      PURITY: 100% pure
  [2] Src [add_model]: add_model
      PURITY: 100% pure
  [3] Src [add_service]: add_service
      PURITY: 100% pure
  [4] Src [add_ui_binding]: add_ui_binding
      PURITY: 100% pure
  [5] Src [introspect]: introspect
      PURITY: 100% pure
  [6] Src [run_sync]: run_sync
      PURITY: 100% pure
  [7] Src [state_yaml]: state_yaml
      PURITY: 100% pure
  [8] Src [docker_compose]: docker_compose
      PURITY: 100% pure
  [9] Src [main]: main → _build_parser
      PURITY: 100% pure
  [10] Src [frontend_to_graph]: frontend_to_graph
      PURITY: 100% pure
  [11] Src [merge_frontend]: merge_frontend
      PURITY: 100% pure
  [12] Src [merge_backend]: merge_backend
      PURITY: 100% pure
  [13] Src [to_dict]: to_dict
      PURITY: 100% pure
  [14] Src [export_yaml]: export_yaml
      PURITY: 100% pure
  [15] Src [commit]: commit
      PURITY: 100% pure
  [16] Src [stable_hash]: stable_hash
      PURITY: 100% pure
  [17] Src [is_callable]: is_callable
      PURITY: 100% pure
  [18] Src [get_docstring]: get_docstring
      PURITY: 100% pure
  [19] Src [to_dict]: to_dict
      PURITY: 100% pure
  [20] Src [export_yaml]: export_yaml
      PURITY: 100% pure
  [21] Src [list_devices]: list_devices
      PURITY: 100% pure
  [22] Src [create_reading]: create_reading
      PURITY: 100% pure
  [23] Src [__init__]: __init__
      PURITY: 100% pure
  [24] Src [__init__]: __init__
      PURITY: 100% pure
  [25] Src [from_blocks]: from_blocks
      PURITY: 100% pure
  [26] Src [_parse_block]: _parse_block
      PURITY: 100% pure
  [27] Src [_merge_fragment]: _merge_fragment
      PURITY: 100% pure
  [28] Src [_build_spec]: _build_spec
      PURITY: 100% pure
  [29] Src [_load_entities]: _load_entities
      PURITY: 100% pure
  [30] Src [_load_databases]: _load_databases
      PURITY: 100% pure
  [31] Src [_load_interfaces]: _load_interfaces
      PURITY: 100% pure
  [32] Src [_load_workflows]: _load_workflows
      PURITY: 100% pure
  [33] Src [_load_roles]: _load_roles
      PURITY: 100% pure
  [34] Src [_load_integrations]: _load_integrations
      PURITY: 100% pure
  [35] Src [_load_webhooks]: _load_webhooks
      PURITY: 100% pure
  [36] Src [_load_api_clients]: _load_api_clients
      PURITY: 100% pure
  [37] Src [_load_data_sources]: _load_data_sources
      PURITY: 100% pure
  [38] Src [_load_templates]: _load_templates
      PURITY: 100% pure
  [39] Src [_load_documents]: _load_documents
      PURITY: 100% pure
  [40] Src [_load_reports]: _load_reports
      PURITY: 100% pure
  [41] Src [_load_environments]: _load_environments
      PURITY: 100% pure
  [42] Src [_load_infrastructures]: _load_infrastructures
      PURITY: 100% pure
  [43] Src [_load_ingresses]: _load_ingresses
      PURITY: 100% pure
  [44] Src [_load_ci_configs]: _load_ci_configs
      PURITY: 100% pure
  [45] Src [_load_deploy]: _load_deploy
      PURITY: 100% pure
  [46] Src [_build_minimal_spec]: _build_minimal_spec
      PURITY: 100% pure
  [47] Src [from_file]: from_file
      PURITY: 100% pure
  [48] Src [from_files]: from_files
      PURITY: 100% pure
  [49] Src [from_text]: from_text
      PURITY: 100% pure
  [50] Src [get_meta_value]: get_meta_value
      PURITY: 100% pure

LAYERS:
  swop/                           CC̄=4.8    ←in:1  →out:25  !! split
  │ !! generator                  745L  2C   34m  CC=16     ←3
  │ !! generator                  683L  2C   17m  CC=11     ←1
  │ !! scanner                    615L  0C   27m  CC=13     ←3
  │ !! commands                   594L  0C   26m  CC=14     ←0
  │ !! cli                        552L  0C    2m  CC=1      ←0
  │ !! graph_builder              540L  0C   19m  CC=13     ←1
  │ !! generator                  533L  3C   14m  CC=26     ←1
  │ !! doql_bridge                531L  2C   28m  CC=13     ←0
  │ !! resolver                   481L  3C   15m  CC=15     ←2
  │ !! doctor_deep                368L  3C   10m  CC=15     ←1
  │ pydantic_cross_check       359L  1C   12m  CC=14     ←1
  │ module_builder             308L  3C    8m  CC=6      ←0
  │ !! pipeline                   301L  2C   10m  CC=23     ←0
  │ hook                       221L  1C    8m  CC=13     ←1
  │ report                     216L  4C   11m  CC=7      ←0
  │ spec_models                212L  20C    0m  CC=0.0    ←0
  │ sync_engine                211L  2C    7m  CC=11     ←0
  │ engine                     210L  2C    7m  CC=9      ←1
  │ config                     209L  5C    9m  CC=8      ←2
  │ compiler                   205L  1C    6m  CC=10     ←1
  │ !! generator                  195L  1C    6m  CC=32     ←1
  │ doctor                     194L  2C   10m  CC=7      ←1
  │ adapter                    172L  1C   12m  CC=6      ←0
  │ !! reader                     169L  1C    4m  CC=21     ←2
  │ __init__                   168L  0C    0m  CC=0.0    ←0
  │ backend                    163L  4C    7m  CC=11     ←0
  │ init                       160L  1C    3m  CC=14     ←1
  │ clustering                 160L  3C    8m  CC=12     ←0
  │ decorators                 158L  0C    4m  CC=7      ←0
  │ render                     141L  0C    3m  CC=8      ←1
  │ parser                     141L  2C   11m  CC=11     ←0
  │ frontend                   138L  2C    8m  CC=10     ←0
  │ compose_builder            119L  1C    5m  CC=5      ←0
  │ cache                      115L  2C   10m  CC=7      ←0
  │ validator                  111L  1C    5m  CC=7      ←0
  │ core                       107L  1C    8m  CC=3      ←0
  │ graph                      107L  3C    7m  CC=4      ←0
  │ reconcile                  105L  4C    7m  CC=7      ←0
  │ registry                   105L  2C   12m  CC=3      ←1
  │ bridge                      76L  0C    2m  CC=9      ←0
  │ db                          53L  2C    3m  CC=5      ←0
  │ graph                       49L  6C    0m  CC=0.0    ←0
  │ sync                        47L  1C    3m  CC=7      ←0
  │ yaml                        47L  1C    2m  CC=5      ←0
  │ __init__                    44L  0C    0m  CC=0.0    ←0
  │ __init__                    43L  0C    0m  CC=0.0    ←0
  │ __init__                    41L  0C    0m  CC=0.0    ←0
  │ frontend                    40L  1C    2m  CC=4      ←0
  │ loader                      39L  1C    1m  CC=8      ←0
  │ __init__                    34L  0C    0m  CC=0.0    ←0
  │ docker                      32L  1C    2m  CC=3      ←0
  │ backend                     32L  1C    4m  CC=3      ←0
  │ __init__                    32L  0C    0m  CC=0.0    ←0
  │ __init__                    32L  0C    0m  CC=0.0    ←0
  │ __init__                    30L  0C    0m  CC=0.0    ←0
  │ __init__                    30L  0C    0m  CC=0.0    ←0
  │ __init__                    28L  0C    0m  CC=0.0    ←0
  │ __init__                    27L  0C    0m  CC=0.0    ←0
  │ versioning                  25L  1C    1m  CC=1      ←0
  │ utils                       23L  0C    3m  CC=1      ←0
  │ __init__                    23L  0C    0m  CC=0.0    ←0
  │ __init__                    17L  0C    0m  CC=0.0    ←0
  │ __init__                    12L  0C    0m  CC=0.0    ←0
  │ __init__                    11L  0C    0m  CC=0.0    ←0
  │ __init__                     7L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=1.0    ←in:0  →out:0
  │ manifest.md                387L  0C    0m  CC=0.0    ←0
  │ models                      16L  2C    0m  CC=0.0    ←0
  │ api                         12L  0C    2m  CC=1      ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ README.md                  432L  0C    0m  CC=0.0    ←0
  │ CHANGELOG.md               377L  0C    0m  CC=0.0    ←0
  │ sumd.json                  102L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              76L  0C    0m  CC=0.0    ←0
  │ project.sh                  44L  0C    0m  CC=0.0    ←0
  │ TODO.md                      8L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                            swop       swop.scan      swop.tools    swop.resolve      swop.watch  swop.manifests      swop.proto  swop.contracts   swop.registry   swop.markpact   swop.services
            swop              ──               5               6               2               2               1               3               2               2               1               1  !! fan-out
       swop.scan               1              ──              ←1                              ←1                                                                                                  hub
      swop.tools              ←6               1              ──               1                                                                                                                  hub
    swop.resolve              ←2                              ←1              ──                               1                                                                                
      swop.watch              ←2               1                                              ──               1                                                                                
  swop.manifests              ←1                                              ←1              ←1              ──                                                                                
      swop.proto              ←3                                                                                              ──                                                                
  swop.contracts              ←2                                                                                                              ──                                                
   swop.registry              ←2                                                                                                                              ──                                
   swop.markpact              ←1                                                                                                                                              ──                
   swop.services              ←1                                                                                                                                                              ──
  CYCLES: none
  HUB: swop.tools/ (fan-in=6)
  HUB: swop.scan/ (fan-in=7)
  SMELL: swop/ fan-out=25 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 7 groups | 66f 11512L | 2026-05-29

SUMMARY:
  files_scanned: 66
  total_lines:   11512
  dup_groups:    7
  dup_fragments: 14
  saved_lines:   73
  scan_ms:       2162

HOTSPOTS[7] (files with most duplication):
  swop/markpact/graph_builder.py  dup=54L  groups=1  frags=2  (0.5%)
  swop/config.py  dup=24L  groups=1  frags=2  (0.2%)
  swop/manifests/generator.py  dup=19L  groups=3  frags=3  (0.2%)
  swop/scan/scanner.py  dup=19L  groups=3  frags=3  (0.2%)
  swop/commands.py  dup=18L  groups=1  frags=2  (0.2%)
  swop/proto/generator.py  dup=7L  groups=1  frags=1  (0.1%)
  swop/services/generator.py  dup=7L  groups=1  frags=1  (0.1%)

DUPLICATES[7] (ranked by impact):
  [efccf54f46437221]   STRU  _build_environments  L=27 N=2 saved=27 sim=1.00
      swop/markpact/graph_builder.py:270-296  (_build_environments)
      swop/markpact/graph_builder.py:299-325  (_build_infrastructures)
  [74019da8a30208a6]   STRU  _parse_bus  L=11 N=2 saved=11 sim=1.00
      swop/config.py:135-145  (_parse_bus)
      swop/config.py:148-160  (_parse_read_models)
  [1615571e1d3ba70f]   STRU  _generate_update_from_disk  L=9 N=2 saved=9 sim=1.00
      swop/commands.py:530-538  (_generate_update_from_disk)
      swop/commands.py:541-549  (_generate_sync_files)
  [210edb0d2eb9b1a3]   STRU  _expr_name  L=8 N=2 saved=8 sim=1.00
      swop/manifests/generator.py:694-701  (_expr_name)
      swop/scan/scanner.py:301-308  (_decorator_name)
  [ad43bea74422d1bd]   STRU  _safe_ident  L=7 N=2 saved=7 sim=1.00
      swop/proto/generator.py:527-533  (_safe_ident)
      swop/services/generator.py:672-678  (_safe_ident)
  [5849e29d70631e5d]   EXAC  _render_default  L=6 N=2 saved=6 sim=1.00
      swop/manifests/generator.py:711-716  (_render_default)
      swop/scan/scanner.py:586-591  (_render_default)
  [6b4c27efef5a18e0]   EXAC  _unparse  L=5 N=2 saved=5 sim=1.00
      swop/manifests/generator.py:704-708  (_unparse)
      swop/scan/scanner.py:579-583  (_unparse)

REFACTOR[7] (ranked by priority):
  [1] ○ extract_function   → swop/markpact/utils/_build_environments.py
      WHY: 2 occurrences of 27-line block across 1 files — saves 27 lines
      FILES: swop/markpact/graph_builder.py
  [2] ○ extract_function   → swop/utils/_parse_bus.py
      WHY: 2 occurrences of 11-line block across 1 files — saves 11 lines
      FILES: swop/config.py
  [3] ○ extract_function   → swop/utils/_generate_update_from_disk.py
      WHY: 2 occurrences of 9-line block across 1 files — saves 9 lines
      FILES: swop/commands.py
  [4] ○ extract_function   → swop/utils/_expr_name.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: swop/manifests/generator.py, swop/scan/scanner.py
  [5] ○ extract_function   → swop/utils/_safe_ident.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: swop/proto/generator.py, swop/services/generator.py
  [6] ○ extract_function   → swop/utils/_render_default.py
      WHY: 2 occurrences of 6-line block across 2 files — saves 6 lines
      FILES: swop/manifests/generator.py, swop/scan/scanner.py
  [7] ○ extract_function   → swop/utils/_unparse.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: swop/manifests/generator.py, swop/scan/scanner.py

QUICK_WINS[6] (low risk, high savings — do first):
  [1] extract_function   saved=27L  → swop/markpact/utils/_build_environments.py
      FILES: graph_builder.py
  [2] extract_function   saved=11L  → swop/utils/_parse_bus.py
      FILES: config.py
  [3] extract_function   saved=9L  → swop/utils/_generate_update_from_disk.py
      FILES: commands.py
  [4] extract_function   saved=8L  → swop/utils/_expr_name.py
      FILES: generator.py, scanner.py
  [5] extract_function   saved=7L  → swop/utils/_safe_ident.py
      FILES: generator.py, generator.py
  [6] extract_function   saved=6L  → swop/utils/_render_default.py
      FILES: generator.py, scanner.py

EFFORT_ESTIMATE (total ≈ 2.4h):
  medium _build_environments                 saved=27L  ~54min
  easy   _parse_bus                          saved=11L  ~22min
  easy   _generate_update_from_disk          saved=9L  ~18min
  easy   _expr_name                          saved=8L  ~16min
  easy   _safe_ident                         saved=7L  ~14min
  easy   _render_default                     saved=6L  ~12min
  easy   _unparse                            saved=5L  ~10min

METRICS-TARGET:
  dup_groups:  7 → 0
  saved_lines: 73 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 423 func | 47f | 2026-05-29
# generated in 0.00s

NEXT[10] (ranked by impact):
  [1] !! SPLIT           swop/manifests/generator.py
      WHY: 745L, 2 classes, max CC=16
      EFFORT: ~4h  IMPACT: 11920

  [2] !! SPLIT           swop/scan/scanner.py
      WHY: 615L, 0 classes, max CC=13
      EFFORT: ~4h  IMPACT: 7995

  [3] !! SPLIT           swop/services/generator.py
      WHY: 683L, 2 classes, max CC=11
      EFFORT: ~4h  IMPACT: 7513

  [4] !! SPLIT-FUNC      render_proto_for_context  CC=26  fan=28
      WHY: CC=26 exceeds 15
      EFFORT: ~1h  IMPACT: 728

  [5] !! SPLIT-FUNC      generate_registry_md  CC=32  fan=19
      WHY: CC=32 exceeds 15
      EFFORT: ~1h  IMPACT: 608

  [6] !  SPLIT-FUNC      _check_manifests_vs_proto  CC=15  fan=18
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 270

  [7] !  SPLIT-FUNC      _check_proto_vs_python  CC=15  fan=18
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 270

  [8] !  SPLIT-FUNC      _check_manifests_vs_services  CC=15  fan=17
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 255

  [9] !  SPLIT-FUNC      _map_python_type  CC=18  fan=14
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 252

  [10] !  SPLIT-FUNC      _index_from_manifests  CC=15  fan=15
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 225


RISKS[3]:
  ⚠ Splitting swop/manifests/generator.py may break 34 import paths
  ⚠ Splitting swop/services/generator.py may break 17 import paths
  ⚠ Splitting swop/scan/scanner.py may break 27 import paths

METRICS-TARGET:
  CC̄:          4.8 → ≤3.4
  max-CC:      32 → ≤16
  god-modules: 9 → 0
  high-CC(≥15): 10 → ≤5
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=1.4 → now CC̄=4.8
```

## Intent

Bi-directional runtime reconciler and drift-aware state graph for full-stack systems
