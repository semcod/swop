# swop

Bi-directional runtime reconciler and drift-aware state graph for full-stack systems

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `swop`
- **version**: `0.2.16`
- **python_requires**: `>=3.8`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(9 mod), project/(3 analysis files)

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

## Interfaces

### CLI Entry Points

- `swop`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m swop
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m swop --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m swop --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m swop --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 4 assertions from pytest
ASSERT[4]{field, operator, expected}:
  graph.services.integration-mailgun.routes./type.type, ==, "email"
  graph.services.data-weather.routes./url.url, ==, "https://api.weather.com"
  graph.services.integration-mailgun.routes./type.type, ==, "email"
  graph.services.data-weather.routes./url.url, ==, "https://api.weather.com"
```

## Configuration

```yaml
project:
  name: swop
  version: 0.2.16
  env: local
```

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

## Deployment

```bash markpact:run
pip install swop

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `sk-or-v1-...` | OpenRouter API Key (required for real cost calculation) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Default AI model for cost analysis |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`inspect`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `swop/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# swop | 87f 16339L | python:84,shell:2,less:1 | 2026-05-29
# stats: 444 func | 104 cls | 87 mod | CC̄=4.9 | critical:47 | cycles:0
# alerts[5]: CC generate_registry_md=32; CC render_proto_for_context=26; CC validate_contract=21; CC test_render_proto_for_context_builds_expected_shape=20; CC test_manifest_yaml_shape_for_command=19
# hotspots[5]: build_project_graph fan=19; generate_services fan=19; render_proto_for_context fan=18; _write_context_package fan=18; _scan_file fan=16
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[87]:
  app.doql.less,34
  examples/src/api.py,12
  examples/src/models.py,16
  project.sh,44
  swop/__init__.py,169
  swop/cli.py,553
  swop/commands.py,595
  swop/config.py,210
  swop/contracts/__init__.py,42
  swop/contracts/adapter.py,173
  swop/contracts/reader.py,170
  swop/core.py,108
  swop/cqrs/__init__.py,29
  swop/cqrs/decorators.py,159
  swop/cqrs/registry.py,106
  swop/export/__init__.py,12
  swop/export/docker.py,33
  swop/export/yaml.py,48
  swop/graph.py,50
  swop/introspect/__init__.py,13
  swop/introspect/backend.py,33
  swop/introspect/frontend.py,41
  swop/manifests/__init__.py,24
  swop/manifests/generator.py,746
  swop/markpact/__init__.py,28
  swop/markpact/doql_bridge.py,532
  swop/markpact/graph_builder.py,541
  swop/markpact/parser.py,142
  swop/markpact/spec_models.py,213
  swop/markpact/sync_engine.py,212
  swop/proto/__init__.py,31
  swop/proto/compiler.py,206
  swop/proto/generator.py,534
  swop/reconcile.py,106
  swop/refactor/__init__.py,44
  swop/refactor/clustering.py,161
  swop/refactor/compose_builder.py,120
  swop/refactor/graph.py,108
  swop/refactor/module_builder.py,309
  swop/refactor/pipeline.py,302
  swop/refactor/scanner/__init__.py,8
  swop/refactor/scanner/backend.py,164
  swop/refactor/scanner/db.py,54
  swop/refactor/scanner/frontend.py,139
  swop/registry/__init__.py,45
  swop/registry/bridge.py,77
  swop/registry/generator.py,196
  swop/registry/loader.py,40
  swop/registry/pydantic_cross_check.py,360
  swop/registry/validator.py,112
  swop/resolve/__init__.py,35
  swop/resolve/resolver.py,482
  swop/scan/__init__.py,33
  swop/scan/cache.py,116
  swop/scan/render.py,142
  swop/scan/report.py,217
  swop/scan/scanner.py,616
  swop/services/__init__.py,31
  swop/services/generator.py,684
  swop/sync.py,48
  swop/tools/__init__.py,33
  swop/tools/doctor.py,195
  swop/tools/doctor_deep.py,369
  swop/tools/hook.py,222
  swop/tools/init.py,161
  swop/utils.py,24
  swop/versioning.py,26
  swop/watch/__init__.py,18
  swop/watch/engine.py,211
  tests/__init__.py,4
  tests/test_cli.py,27
  tests/test_config.py,128
  tests/test_core.py,82
  tests/test_cqrs.py,145
  tests/test_doctor_deep.py,276
  tests/test_hook.py,170
  tests/test_manifests.py,417
  tests/test_markpact.py,803
  tests/test_proto.py,413
  tests/test_pydantic_cross_check.py,437
  tests/test_refactor.py,191
  tests/test_resolve.py,423
  tests/test_scan.py,351
  tests/test_services.py,351
  tests/test_tools.py,78
  tests/test_watch.py,174
  tree.sh,2
D:
  examples/src/api.py:
    e: list_devices,create_reading
    list_devices()
    create_reading(reading)
  examples/src/models.py:
    e: Device,Reading
    Device:
    Reading:
  swop/__init__.py:
  swop/cli.py:
    e: _build_parser,main
    _build_parser()
    main(argv)
  swop/commands.py:
    e: _build_runtime,_cmd_sync,_cmd_inspect,_cmd_diff,_cmd_state,_cmd_export,_cmd_doctor,_cmd_hook,_cmd_init,_cmd_scan,_cmd_gen_manifests,_cmd_gen_proto,_cmd_gen_grpc_python,_cmd_gen_grpc_ts,_cmd_gen_services,_cmd_gen_registry,_cmd_watch,_cmd_resolve,_cmd_refactor,_generate_parse_manifest,_generate_build_graph,_generate_check_files,_generate_update_from_disk,_generate_sync_files,_generate_outputs,_cmd_generate
    _build_runtime(mode)
    _cmd_sync(args)
    _cmd_inspect(args)
    _cmd_diff(args)
    _cmd_state(args)
    _cmd_export(args)
    _cmd_doctor(args)
    _cmd_hook(args)
    _cmd_init(args)
    _cmd_scan(args)
    _cmd_gen_manifests(args)
    _cmd_gen_proto(args)
    _cmd_gen_grpc_python(args)
    _cmd_gen_grpc_ts(args)
    _cmd_gen_services(args)
    _cmd_gen_registry(args)
    _cmd_watch(args)
    _cmd_resolve(args)
    _cmd_refactor(args)
    _generate_parse_manifest(args)
    _generate_build_graph(blocks;args)
    _generate_check_files(manifest_path;args)
    _generate_update_from_disk(manifest_path;args)
    _generate_sync_files(manifest_path;args)
    _generate_outputs(runtime;args)
    _cmd_generate(args)
  swop/config.py:
    e: _expand_env,_pop_known,_parse_context,_parse_bus,_parse_read_models,load_config,_from_dict,SwopConfigError,BoundedContextConfig,BusConfig,ReadModelConfig,SwopConfig
    SwopConfigError:  # Raised when ``swop.yaml`` is malformed.
    BoundedContextConfig:
    BusConfig:
    ReadModelConfig:
    SwopConfig: project_root(0),state_path(0),context(1),iter_source_roots(0)
    _expand_env(value)
    _pop_known(data;keys)
    _parse_context(raw)
    _parse_bus(raw)
    _parse_read_models(raw)
    load_config(path)
    _from_dict(data;cfg_path)
  swop/contracts/__init__.py:
  swop/contracts/adapter.py:
    e: _contract_kind,_contract_name,_contract_context,_contract_fields,contract_to_detection,contracts_to_detections,ContractDetectionAdapter
    ContractDetectionAdapter: __init__(2),from_directory(3),by_kind(1),by_context(1),contexts(0),summary(0)  # High-level adapter that loads contracts and produces a *decl
    _contract_kind(contract)
    _contract_name(contract)
    _contract_context(contract)
    _contract_fields(contract)
    contract_to_detection(contract)
    contracts_to_detections(contracts)
  swop/contracts/reader.py:
    e: load_contracts,_check_layer_paths,validate_contract,validate_all,ContractValidationError
    ContractValidationError:  # Raised when a contract file fails structural validation.
    load_contracts(contracts_dir)
    _check_layer_paths(contract;errors;root)
    validate_contract(contract)
    validate_all(contracts)
  swop/core.py:
    e: SwopRuntime
    SwopRuntime: __init__(3),add_model(3),add_service(2),add_ui_binding(2),introspect(0),run_sync(0),state_yaml(0),docker_compose(0)  # Main orchestrator for the swop reconciliation system.
  swop/cqrs/__init__.py:
  swop/cqrs/decorators.py:
    e: _collect_source,_normalize_emits,_make_decorator,handler
    _collect_source(cls)
    _normalize_emits(emits)
    _make_decorator(kind)
    handler(target)
  swop/cqrs/registry.py:
    e: get_registry,reset_registry,CqrsRecord,CqrsRegistry
    CqrsRecord:  # One registered CQRS artifact.
    CqrsRegistry: __init__(0),register(1),clear(0),all(0),of_kind(1),by_context(1),contexts(0),summary(0),__len__(0),__iter__(0)  # Thread-safe map of decorator-registered CQRS artifacts.
    get_registry()
    reset_registry()
  swop/export/__init__.py:
  swop/export/docker.py:
    e: DockerExporter
    DockerExporter: to_dict(1),export_yaml(1)  # Render a ``ProjectGraph`` into a docker-compose specificatio
  swop/export/yaml.py:
    e: StateExporter
    StateExporter: to_dict(2),export_yaml(2)  # Serialize a ``ProjectGraph`` plus a ``Drift`` to YAML.
  swop/graph.py:
    e: ModelField,DataModel,UIBinding,Service,GraphVersion,ProjectGraph
    ModelField:
    DataModel:
    UIBinding:
    Service:
    GraphVersion:
    ProjectGraph:
  swop/introspect/__init__.py:
  swop/introspect/backend.py:
    e: BackendIntrospector
    BackendIntrospector: __init__(2),introspect(0),register_model(2),register_route(1)  # Introspect backend services to produce a runtime state dict.
  swop/introspect/frontend.py:
    e: FrontendIntrospector
    FrontendIntrospector: introspect(1),from_html(1)  # Introspect frontend artifacts to produce a runtime state dic
  swop/manifests/__init__.py:
  swop/manifests/generator.py:
    e: generate_manifests,_handler_index,_render_manifest,_render_entry,_render_source,_render_field,_render_handler,_render_bus,_camel_to_dot,_safe_dirname,_render_query_response_metadata,_collect_supporting_types,_collect_supporting_types_from_fields,_annotation_type_names,_first_custom_type_name,_find_handler_return_type,_module_ast,_module_classes,_find_class_in_module,_module_imports,_resolve_import_module_paths,_resolve_class_definition,_resolve_symbol_from_module,_search_class_files,_is_enum_class,_render_enum_type,_extract_class_fields,_expr_name,_unparse,_render_default,_annotation_is_optional,_dedupe_type_defs,ManifestFile,ManifestGenerationResult
    ManifestFile:
    ManifestGenerationResult: total_entries(0),by_context(0),format(0)
    generate_manifests(report;config)
    _handler_index(detections)
    _render_manifest(context;kind;detections;handler_index;config)
    _render_entry(detection;kind;handler_index;config;cache)
    _render_source(detection)
    _render_field(field_def)
    _render_handler(handler)
    _render_bus(detection;config)
    _camel_to_dot(name)
    _safe_dirname(name)
    _render_query_response_metadata(handler;config;cache)
    _collect_supporting_types(source_file;fields;config;cache)
    _collect_supporting_types_from_fields(source_path;fields;config;cache;seen)
    _annotation_type_names(annotation)
    _first_custom_type_name(annotation)
    _find_handler_return_type(class_node;method_name)
    _module_ast(path;cache)
    _module_classes(path;cache)
    _find_class_in_module(path;class_name;cache)
    _module_imports(path;project_root;cache)
    _resolve_import_module_paths(source_path;project_root;module_name;level)
    _resolve_class_definition(class_name;source_path;project_root;cache)
    _resolve_symbol_from_module(module_path;symbol_name;project_root;cache;seen)
    _search_class_files(class_name;project_root;cache)
    _is_enum_class(node)
    _render_enum_type(name;node)
    _extract_class_fields(node)
    _expr_name(node)
    _unparse(node)
    _render_default(node)
    _annotation_is_optional(node)
    _dedupe_type_defs(type_defs)
  swop/markpact/__init__.py:
  swop/markpact/doql_bridge.py:
    e: MarkpactValidationError,DoqlBridge
    MarkpactValidationError: __init__(2)  # Raised when a manifest block cannot be parsed into a DOQL sp
    DoqlBridge: __init__(0),_try_import_doql(0),from_blocks(1),_parse_block(1),_merge_fragment(2),_build_spec(1),_load_entities(2),_load_databases(2),_load_interfaces(2),_load_workflows(2),_load_roles(2),_load_integrations(2),_load_webhooks(2),_load_api_clients(2),_load_data_sources(2),_load_templates(2),_load_documents(2),_load_reports(2),_load_environments(2),_load_infrastructures(2),_load_ingresses(2),_load_ci_configs(2),_load_deploy(2),_build_minimal_spec(1),from_file(1),from_files(1),from_text(1)  # Convert a collection of ``ManifestBlock`` objects into a Doq
  swop/markpact/graph_builder.py:
    e: build_project_graph,_build_models,_build_services,_build_ui_bindings,_build_databases,_build_workflows,_build_roles,_build_integrations,_build_webhooks,_build_api_clients,_build_environments,_build_infrastructures,_build_ingresses,_build_ci_configs,_build_data_sources,_build_templates,_build_documents,_build_reports,_build_deploy
    build_project_graph(spec)
    _build_models(graph;spec)
    _build_services(graph;spec)
    _build_ui_bindings(graph;spec)
    _build_databases(graph;spec)
    _build_workflows(graph;spec)
    _build_roles(graph;spec)
    _build_integrations(graph;spec)
    _build_webhooks(graph;spec)
    _build_api_clients(graph;spec)
    _build_environments(graph;spec)
    _build_infrastructures(graph;spec)
    _build_ingresses(graph;spec)
    _build_ci_configs(graph;spec)
    _build_data_sources(graph;spec)
    _build_templates(graph;spec)
    _build_documents(graph;spec)
    _build_reports(graph;spec)
    _build_deploy(graph;spec)
  swop/markpact/parser.py:
    e: ManifestBlock,ManifestParser
    ManifestBlock: get_meta_value(1),as_yaml(0),as_json(0)
    ManifestParser: __init__(1),parse_file(1),parse(1),parse_by_kind(2),parse_doql_blocks(1),parse_graph_blocks(1),parse_file_blocks(1),parse_config_blocks(1)  # Parse markpact blocks from markdown manifests.
  swop/markpact/spec_models.py:
    e: MinimalEntityField,MinimalEntity,MinimalInterface,MinimalDatabase,MinimalDeploy,MinimalWorkflowStep,MinimalWorkflow,MinimalRole,MinimalIntegration,MinimalWebhook,MinimalApiClient,MinimalEnvironment,MinimalInfrastructure,MinimalIngress,MinimalCiConfig,MinimalDataSource,MinimalTemplate,MinimalDocument,MinimalReport,MinimalDoqlSpec
    MinimalEntityField:
    MinimalEntity:
    MinimalInterface:
    MinimalDatabase:
    MinimalDeploy:
    MinimalWorkflowStep:
    MinimalWorkflow:
    MinimalRole:
    MinimalIntegration:
    MinimalWebhook:
    MinimalApiClient:
    MinimalEnvironment:
    MinimalInfrastructure:
    MinimalIngress:
    MinimalCiConfig:
    MinimalDataSource:
    MinimalTemplate:
    MinimalDocument:
    MinimalReport:
    MinimalDoqlSpec:
  swop/markpact/sync_engine.py:
    e: _hash,SyncStatus,ManifestSyncEngine
    SyncStatus:
    ManifestSyncEngine: __init__(1),check(1),diff(1),sync_to_disk(1),sync_from_disk(1),update_manifest(1)  # Check and sync ``markpact:file`` blocks against the filesyst
    _hash(text)
  swop/proto/__init__.py:
  swop/proto/compiler.py:
    e: _iter_proto_files,_proto_roots,_run,compile_proto_python,compile_proto_typescript,CompilationResult
    CompilationResult: format(0)
    _iter_proto_files(proto_dir)
    _proto_roots(proto_files;proto_dir)
    _run(cmd;cwd)
    compile_proto_python(proto_dir;out_dir)
    compile_proto_typescript(proto_dir;out_dir)
  swop/proto/generator.py:
    e: _map_python_type,_load_manifest,_iter_contexts,generate_proto_from_manifests,render_proto_for_context,_render_message,_render_command_response,_render_query_response,_collect_known_types,_render_type_definition,_render_enum,_service_name,_safe_ident,ProtoFile,ProtoGenerationResult,_ProtoType
    ProtoFile: total_rpcs(0)
    ProtoGenerationResult: format(0)
    _ProtoType:
    _map_python_type(annotation)
    _load_manifest(path)
    _iter_contexts(manifests_dir)
    generate_proto_from_manifests(manifests_dir;out_dir)
    render_proto_for_context(context;commands;queries;events)
    _render_message(name;fields;imports;context;known_type_names)
    _render_command_response(name;emits)
    _render_query_response(name;result_type)
    _collect_known_types(commands;queries;events)
    _render_type_definition(type_def;imports;context;known_type_names)
    _render_enum(name;values)
    _service_name(context;suffix)
    _safe_ident(name)
  swop/reconcile.py:
    e: DriftError,Drift,DriftDetector,ResyncEngine
    DriftError:  # Raised when drift is detected while running in STRICT mode.
    Drift: exists(0)
    DriftDetector: compute(2)  # Compare a declared graph with the actual runtime state.
    ResyncEngine: __init__(1),reconcile(2),_has_critical(1),_auto_heal(2),_log_drift(1)  # Continuously reconcile the declared graph against actual sta
  swop/refactor/__init__.py:
  swop/refactor/clustering.py:
    e: Cluster,LouvainLike,SeededClusterer
    Cluster:
    LouvainLike: __init__(2),run(0),_step(0),_gain_for(3),_collect(0)  # Dependency-free modularity-gain clusterer.
    SeededClusterer: __init__(2),run(1),_bfs(1)  # Grow one cluster per seed node via weighted BFS.
  swop/refactor/compose_builder.py:
    e: ComposeBuilder
    ComposeBuilder: __init__(2),write(1),_write_module_compose(3),_service_name(1),_write_dockerfile(1)  # Render docker-compose manifests for a set of modules.
  swop/refactor/graph.py:
    e: Node,Edge,RefactorGraph
    Node:
    Edge:
    RefactorGraph: __init__(0),add_node(2),add_edge(4),edges(0),neighbors(1),nodes_of_type(1),as_dict(0),from_iterables(3)  # Undirected weighted graph tailored for system decomposition.
  swop/refactor/module_builder.py:
    e: ModuleSpec,ModuleWriteResult,ModuleBuilder
    ModuleSpec:
    ModuleWriteResult:
    ModuleBuilder: __init__(1),write(1),_write_ui(3),_write_api(3),_write_models(3),_write_db(3),_write_api_server(3),_write_manifest(3)  # Write a :class:`ModuleSpec` to disk.
  swop/refactor/pipeline.py:
    e: _tokenize,RefactorResult,RefactorPipeline
    RefactorResult: summary(0)
    RefactorPipeline: __init__(7),run(0),_build_graph(3),_link_models_to_ui(1),_link_models_to_tables(2),_seed_nodes(2),_seed_cluster_name(1),_cluster_to_spec(6)  # High-level orchestrator for graph-based module extraction.
    _tokenize(text)
  swop/refactor/scanner/__init__.py:
  swop/refactor/scanner/backend.py:
    e: ModelSignals,RouteSignals,BackendSignals,BackendScanner
    ModelSignals:
    RouteSignals:
    BackendSignals:
    BackendScanner: __init__(4),_iter_py(1),scan(0),_extract_model_fields(1),_extract_models(1),_looks_like_model(1),_extract_routes(1)  # Scan a Python backend root for models and routes.
  swop/refactor/scanner/db.py:
    e: DbSignals,DbScanner
    DbSignals:
    DbScanner: __init__(2),scan(0),_scan_file(1)  # Scan a directory for SQLite databases and enumerate their ta
  swop/refactor/scanner/frontend.py:
    e: PageSignals,FrontendScanner
    PageSignals:
    FrontendScanner: __init__(3),_pages_root(0),iter_pages(0),scan(0),scan_file(1),find_pages_for_route(1),_route_token(1),_slug_for(1)  # Scan a frontend project root and emit ``PageSignals`` per pa
  swop/registry/__init__.py:
  swop/registry/bridge.py:
    e: _fields,bridge_contracts_to_detections
    _fields(raw;key)
    bridge_contracts_to_detections(contracts)
  swop/registry/generator.py:
    e: _ep,_ch,generate_registry_json,generate_registry_md,write_registry,RegistryGenerationResult
    RegistryGenerationResult: format(0)
    _ep(http)
    _ch(ws)
    generate_registry_json(contracts)
    generate_registry_md(contracts)
    write_registry(contracts_dir;contracts)
  swop/registry/loader.py:
    e: load_contracts,Contract
    Contract:  # One JSON contract loaded from disk.
    load_contracts(contracts_dir)
  swop/registry/pydantic_cross_check.py:
    e: _extract_literal_values,_node_name,_literal_slice_values,_collect_literal_fields,_load_literal_fields,_iter_enum_fields,_contract_schemas,_classify_drift,_parse_layer_path,cross_check_contract,cross_check_contracts,CrossCheckResult
    CrossCheckResult: format(0)
    _extract_literal_values(annotation)
    _node_name(node)
    _literal_slice_values(slice_node)
    _collect_literal_fields(tree)
    _load_literal_fields(python_path)
    _iter_enum_fields(schema;prefix)
    _contract_schemas(raw)
    _classify_drift(block_kind;contract_set;pydantic_set)
    _parse_layer_path(raw_layer)
    cross_check_contract(contract)
    cross_check_contracts(contracts)
  swop/registry/validator.py:
    e: validate_contract,_check_keys,_check_kind,_check_layer_paths,ValidationResult
    ValidationResult: format(0)
    validate_contract(contract)
    _check_keys(raw;required;errors)
    _check_kind(raw;expected;errors)
    _check_layer_paths(raw;root;errors)
  swop/resolve/__init__.py:
  swop/resolve/resolver.py:
    e: resolve_schema_drift,apply_resolution,_index_from_detections,_handler_shape,_index_from_manifests,_diff_context_kind,_diff_fields,_diff_metadata,_diff_entry,_field_signature,_handler_sig,ChangeKind,Change,ResolutionReport
    ChangeKind:
    Change: format(0)
    ResolutionReport: breaking(0),non_breaking(0),counts(0),to_json(0),format(0)
    resolve_schema_drift(report;config)
    apply_resolution(report;config;resolution)
    _index_from_detections(detections)
    _handler_shape(det)
    _index_from_manifests(manifests_root)
    _diff_context_kind(context;kind;current;stored;resolution)
    _diff_fields(context;kind;name;old_fields;new_fields;resolution)
    _diff_metadata(context;kind;name;old;new;resolution)
    _diff_entry(context;kind;name;old;new;resolution)
    _field_signature(entry)
    _handler_sig(handler)
  swop/scan/__init__.py:
  swop/scan/cache.py:
    e: CacheEntry,FingerprintCache
    CacheEntry:
    FingerprintCache: __init__(1),load(0),save(0),fingerprint(1),get(2),put(3),drop(1),prune(1),__len__(0),__contains__(1)  # Persistent sha256-based cache of scanner detections.
  swop/scan/render.py:
    e: render_json,render_html,write_report
    render_json(report;pretty)
    render_html(report)
    write_report(report;json_path;html_path)
  swop/scan/report.py:
    e: FieldDef,Detection,ContextSummary,ScanReport
    FieldDef: to_dict(0)  # One attribute declaration extracted from a CQRS class body.
    Detection: to_dict(0),from_dict(1)
    ContextSummary: add(1),total(0)
    ScanReport: add(1),kinds(0),via(0),of_kind(1),of_context(1),to_dict(0),format_text(0)
  swop/scan/scanner.py:
    e: _scan_file,scan_project,_new_ctx_summary,_resolve_contexts,_iter_python_files,_matches_any,_context_for_path,_extract_detections,_module_name_from_path,_decorator_name,_base_name,_extract_decorator_emits,_extract_decorator_context,_extract_handler_target,_classify_decorator,_classify_heuristic,_classify,_kind_by_suffix,_kind_by_base,_handler_target_from_method,_handler_method_name,_extract_ann_field,_extract_plain_field,_extract_fields,_unparse,_render_default,_annotation_is_optional
    _scan_file(py_path;project_root;config;contexts;cache;incremental;report)
    scan_project(config)
    _new_ctx_summary(name)
    _resolve_contexts(config)
    _iter_python_files(root;source_roots;excludes)
    _matches_any(path;patterns)
    _context_for_path(rel_path;contexts;project_root)
    _extract_detections(tree;path;rel_path;context;fingerprint)
    _module_name_from_path(rel_path)
    _decorator_name(node)
    _base_name(node)
    _extract_decorator_emits(call)
    _extract_decorator_context(call)
    _extract_handler_target(call)
    _classify_decorator(node;decorator_node;decorator_names;bases;qualname;module;context;rel_path)
    _classify_heuristic(node;decorator_names;bases;qualname;module;context;rel_path)
    _classify(node;path;rel_path;module;context)
    _kind_by_suffix(name)
    _kind_by_base(bases)
    _handler_target_from_method(node)
    _handler_method_name(node)
    _extract_ann_field(stmt;seen)
    _extract_plain_field(stmt;seen)
    _extract_fields(node)
    _unparse(node)
    _render_default(node)
    _annotation_is_optional(node)
  swop/services/__init__.py:
  swop/services/generator.py:
    e: generate_services,_write_context_package,_classify_file,_render_init,_render_worker,_render_server,_render_publisher,_render_requirements,_render_dockerfile,_render_env,_render_compose,_default_bus_url,_render_readme,_load_yaml,_safe_ident,_camel,ServiceFile,ServiceGenerationResult
    ServiceFile:
    ServiceGenerationResult: format(0)
    generate_services(manifests_dir;out_dir)
    _write_context_package()
    _classify_file(name)
    _render_init(context)
    _render_worker()
    _render_server()
    _render_publisher(bus)
    _render_requirements(bus)
    _render_dockerfile(base_image)
    _render_env()
    _render_compose(contexts;bus)
    _default_bus_url(bus)
    _render_readme(contexts;bus)
    _load_yaml(path)
    _safe_ident(name)
    _camel(name)
  swop/sync.py:
    e: SyncEngine
    SyncEngine: frontend_to_graph(1),merge_frontend(2),merge_backend(2)  # Move state between a ``ProjectGraph`` and introspected snaps
  swop/tools/__init__.py:
  swop/tools/doctor.py:
    e: _check_python,_check_swop,_check_pyyaml,_run_version,_first_version,_check_binary,_check_git_repo,run_doctor,DoctorCheck,DoctorReport
    DoctorCheck: ok(0),format(0)
    DoctorReport: failed(0),warnings(0),ok(0),format(0)
    _check_python()
    _check_swop()
    _check_pyyaml()
    _run_version(cmd)
    _first_version(text)
    _check_binary(binary;version_args)
    _check_git_repo(root)
    run_doctor(root)
  swop/tools/doctor_deep.py:
    e: _check_scan_vs_manifests,_check_manifests_vs_proto,_check_proto_vs_python,_check_manifests_vs_services,run_deep_doctor,_latest_mtime,DeepIssue,DeepCheck,DeepReport
    DeepIssue: format(0)
    DeepCheck: ok(0),mark(1),format(0)
    DeepReport: failed(0),warnings(0),ok(0),format(0)
    _check_scan_vs_manifests(config)
    _check_manifests_vs_proto(config)
    _check_proto_vs_python(config)
    _check_manifests_vs_services(config)
    run_deep_doctor(config)
    _latest_mtime(directory)
  swop/tools/hook.py:
    e: _git_dir,_hook_path,_is_swop_hook,install_hook,uninstall_hook,hook_status,_make_executable,HookResult
    HookResult: format(0)
    _git_dir(root)
    _hook_path(root)
    _is_swop_hook(path)
    install_hook(root)
    uninstall_hook(root)
    hook_status(root)
    _make_executable(path)
  swop/tools/init.py:
    e: init_project,_merge_gitignore,InitResult
    InitResult: format(0)
    init_project(root)
    _merge_gitignore(path;entries)
  swop/utils.py:
    e: stable_hash,is_callable,get_docstring
    stable_hash(payload)
    is_callable(obj)
    get_docstring(obj)
  swop/versioning.py:
    e: Versioning
    Versioning: commit(2)  # Append a new ``GraphVersion`` entry whenever the graph mutat
  swop/watch/__init__.py:
  swop/watch/engine.py:
    e: rebuild_once,_diff_snapshots,WatchRebuild,WatchEngine
    WatchRebuild: format(0)  # The result of a single rebuild pass.
    WatchEngine: snapshot(0),_maybe_add(2),poll_once(0),run(0)  # mtime-polling watcher for Python source files.
    rebuild_once(config)
    _diff_snapshots(before;after)
  tests/__init__.py:
  tests/test_cli.py:
    e: test_cli_state_command,test_cli_export_docker,test_cli_inspect_backend
    test_cli_state_command(capsys)
    test_cli_export_docker(capsys)
    test_cli_inspect_backend(capsys)
  tests/test_config.py:
    e: _write,test_load_minimal_config,test_load_full_config,test_env_vars_keep_literal_when_missing,test_missing_config_raises,test_bounded_context_without_required_fields,test_unknown_keys_stored_in_extra
    _write(path;body)
    test_load_minimal_config(tmp_path)
    test_load_full_config(tmp_path;monkeypatch)
    test_env_vars_keep_literal_when_missing(tmp_path)
    test_missing_config_raises(tmp_path)
    test_bounded_context_without_required_fields(tmp_path)
    test_unknown_keys_stored_in_extra(tmp_path)
  tests/test_core.py:
    e: _runtime,test_add_model_commits_version,test_run_sync_detects_invalid_bindings,test_auto_heal_removes_invalid_bindings,test_strict_mode_raises_on_invalid_binding,test_state_yaml_is_serializable,test_docker_export_contains_services
    _runtime(mode)
    test_add_model_commits_version()
    test_run_sync_detects_invalid_bindings()
    test_auto_heal_removes_invalid_bindings()
    test_strict_mode_raises_on_invalid_binding()
    test_state_yaml_is_serializable()
    test_docker_export_contains_services()
  tests/test_cqrs.py:
    e: _reset,test_command_decorator_registers_class,test_query_and_event_decorators_kept_separate,test_handler_decorator_links_to_target_class,test_handler_decorator_accepts_string_target,test_decorators_reject_non_class_targets,test_registry_summary_groups_by_kind,test_emits_accepts_classes_and_strings,test_reset_registry_clears_state,test_local_registry_is_independent
    _reset()
    test_command_decorator_registers_class()
    test_query_and_event_decorators_kept_separate()
    test_handler_decorator_links_to_target_class()
    test_handler_decorator_accepts_string_target()
    test_decorators_reject_non_class_targets()
    test_registry_summary_groups_by_kind()
    test_emits_accepts_classes_and_strings()
    test_reset_registry_clears_state()
    test_local_registry_is_independent()
  tests/test_doctor_deep.py:
    e: _write,_bump_mtime,full_project,test_run_deep_doctor_reports_ok_when_everything_generated,test_scan_vs_manifests_flags_breaking_change,test_manifests_vs_proto_warns_when_proto_is_stale,test_manifests_vs_proto_fails_when_proto_missing,test_proto_vs_python_fails_when_stubs_missing,test_proto_vs_python_warns_without_python_dir,test_manifests_vs_services_fails_when_package_missing,test_manifests_vs_services_fails_when_incomplete,test_cli_doctor_deep_ok,test_cli_doctor_deep_nonzero_on_drift,test_cli_doctor_without_deep_does_not_require_config
    _write(path;body)
    _bump_mtime(path;delta)
    full_project(tmp_path)
    test_run_deep_doctor_reports_ok_when_everything_generated(full_project)
    test_scan_vs_manifests_flags_breaking_change(full_project)
    test_manifests_vs_proto_warns_when_proto_is_stale(full_project)
    test_manifests_vs_proto_fails_when_proto_missing(full_project)
    test_proto_vs_python_fails_when_stubs_missing(full_project)
    test_proto_vs_python_warns_without_python_dir(tmp_path)
    test_manifests_vs_services_fails_when_package_missing(full_project)
    test_manifests_vs_services_fails_when_incomplete(full_project)
    test_cli_doctor_deep_ok(full_project;capsys)
    test_cli_doctor_deep_nonzero_on_drift(full_project;capsys)
    test_cli_doctor_without_deep_does_not_require_config(tmp_path;capsys)
  tests/test_hook.py:
    e: _fake_git_repo,test_install_hook_creates_executable_file,test_install_hook_on_non_git_repo_returns_error,test_install_hook_refuses_to_overwrite_foreign_hook,test_install_hook_with_force_overwrites,test_install_is_idempotent,test_uninstall_removes_swop_hook,test_uninstall_preserves_foreign_hook,test_uninstall_skipped_when_absent,test_hook_status_reports_all_states,test_install_follows_git_file_worktree_pointer,test_cli_hook_install_and_uninstall,test_cli_hook_install_non_git_errors
    _fake_git_repo(tmp_path)
    test_install_hook_creates_executable_file(tmp_path)
    test_install_hook_on_non_git_repo_returns_error(tmp_path)
    test_install_hook_refuses_to_overwrite_foreign_hook(tmp_path)
    test_install_hook_with_force_overwrites(tmp_path)
    test_install_is_idempotent(tmp_path)
    test_uninstall_removes_swop_hook(tmp_path)
    test_uninstall_preserves_foreign_hook(tmp_path)
    test_uninstall_skipped_when_absent(tmp_path)
    test_hook_status_reports_all_states(tmp_path)
    test_install_follows_git_file_worktree_pointer(tmp_path)
    test_cli_hook_install_and_uninstall(tmp_path;capsys)
    test_cli_hook_install_non_git_errors(tmp_path;capsys)
  tests/test_manifests.py:
    e: _write,customer_project,test_scan_extracts_fields_from_dataclass,test_scan_handler_records_method_name,test_generate_manifests_writes_per_context_files,test_manifest_yaml_shape_for_command,test_manifest_event_has_fields_but_no_bus,test_manifest_heuristic_detection_carries_confidence,test_manifest_query_includes_response_and_types,test_generate_manifests_redis_bus,test_generate_manifests_no_bus_when_unconfigured,test_cli_gen_manifests,test_cli_gen_manifests_skip_heuristics
    _write(path;body)
    customer_project(tmp_path)
    test_scan_extracts_fields_from_dataclass(customer_project)
    test_scan_handler_records_method_name(customer_project)
    test_generate_manifests_writes_per_context_files(customer_project)
    test_manifest_yaml_shape_for_command(customer_project)
    test_manifest_event_has_fields_but_no_bus(customer_project)
    test_manifest_heuristic_detection_carries_confidence(customer_project)
    test_manifest_query_includes_response_and_types(customer_project)
    test_generate_manifests_redis_bus(tmp_path)
    test_generate_manifests_no_bus_when_unconfigured(tmp_path)
    test_cli_gen_manifests(customer_project;capsys)
    test_cli_gen_manifests_skip_heuristics(customer_project;capsys)
  tests/test_markpact.py:
    e: tmp_manifest,test_parser_finds_all_blocks,test_parser_counts_blocks,test_parser_extracts_meta,test_parser_doql_block_body,test_parser_filter_by_kind,test_parser_includes,test_bridge_from_text,test_bridge_missing_any_supported_blocks_raises,test_bridge_strict_mode,test_bridge_merge_multiple_doql,test_graph_from_doql_spec,test_graph_services_from_interfaces,test_graph_ui_bindings_from_pages,test_graph_databases_as_services,test_sync_check_identical,test_sync_check_modified,test_sync_check_missing,test_sync_to_disk,test_sync_to_disk_dry_run,test_sync_from_disk,test_diff_report,test_graph_workflows_as_services,test_graph_roles_as_services,test_graph_api_clients_as_services,test_graph_webhooks_as_services,test_graph_integrations_as_services,test_graph_environments_as_services,test_graph_infrastructures_as_services,test_graph_ingresses_as_services,test_graph_ci_configs_as_services,test_graph_data_sources_as_services,test_graph_templates_as_services,test_graph_documents_as_services,test_graph_reports_as_services,test_graph_deploy_as_service,test_bridge_from_files_merge,test_cli_generate_from_markpact,test_cli_generate_sync_files,test_cli_generate_sync_files_dry_run,test_update_manifest_reverse_sync,test_update_manifest_dry_run,test_update_manifest_preserves_untracked_blocks,test_cli_generate_check_files_ok,test_cli_generate_check_files_strict_fails_on_drift,test_cli_generate_from_disk,test_cli_generate_from_disk_dry_run
    tmp_manifest(tmp_path)
    test_parser_finds_all_blocks(tmp_manifest)
    test_parser_counts_blocks(tmp_manifest)
    test_parser_extracts_meta()
    test_parser_doql_block_body()
    test_parser_filter_by_kind(tmp_manifest)
    test_parser_includes(tmp_path)
    test_bridge_from_text()
    test_bridge_missing_any_supported_blocks_raises()
    test_bridge_strict_mode()
    test_bridge_merge_multiple_doql()
    test_graph_from_doql_spec()
    test_graph_services_from_interfaces()
    test_graph_ui_bindings_from_pages()
    test_graph_databases_as_services()
    test_sync_check_identical(tmp_path)
    test_sync_check_modified(tmp_path)
    test_sync_check_missing(tmp_path)
    test_sync_to_disk(tmp_path)
    test_sync_to_disk_dry_run(tmp_path)
    test_sync_from_disk(tmp_path)
    test_diff_report(tmp_path)
    test_graph_workflows_as_services()
    test_graph_roles_as_services()
    test_graph_api_clients_as_services()
    test_graph_webhooks_as_services()
    test_graph_integrations_as_services()
    test_graph_environments_as_services()
    test_graph_infrastructures_as_services()
    test_graph_ingresses_as_services()
    test_graph_ci_configs_as_services()
    test_graph_data_sources_as_services()
    test_graph_templates_as_services()
    test_graph_documents_as_services()
    test_graph_reports_as_services()
    test_graph_deploy_as_service()
    test_bridge_from_files_merge(tmp_path)
    test_cli_generate_from_markpact(tmp_path)
    test_cli_generate_sync_files(tmp_path)
    test_cli_generate_sync_files_dry_run(tmp_path)
    test_update_manifest_reverse_sync(tmp_path)
    test_update_manifest_dry_run(tmp_path)
    test_update_manifest_preserves_untracked_blocks(tmp_path)
    test_cli_generate_check_files_ok(tmp_path)
    test_cli_generate_check_files_strict_fails_on_drift(tmp_path)
    test_cli_generate_from_disk(tmp_path)
    test_cli_generate_from_disk_dry_run(tmp_path)
  tests/test_proto.py:
    e: _write,test_map_python_type_basic,test_map_python_type_dict_becomes_map,test_map_python_type_unknown_name_is_stub,test_map_python_type_empty_is_string_stub,test_render_proto_for_context_builds_expected_shape,test_render_proto_adds_timestamp_import,test_render_proto_warns_on_unknown_user_type,test_render_proto_renders_query_response_model_and_enum_types,test_render_proto_emits_optional_only_for_nullable_singular_fields,project_with_manifests,test_generate_proto_from_manifests_writes_file,test_generate_proto_skips_empty_context_dirs,test_compile_proto_python_produces_pb2,test_compile_proto_python_without_grpc_tools_returns_helpful_error,test_compile_proto_typescript_missing_protoc_is_reported,test_cli_gen_proto_requires_manifests,test_cli_gen_proto_end_to_end,test_cli_gen_grpc_python_reports_ok_or_missing
    _write(path;body)
    test_map_python_type_basic(annotation;expected_proto;expected_repeated)
    test_map_python_type_dict_becomes_map()
    test_map_python_type_unknown_name_is_stub()
    test_map_python_type_empty_is_string_stub()
    test_render_proto_for_context_builds_expected_shape()
    test_render_proto_adds_timestamp_import()
    test_render_proto_warns_on_unknown_user_type()
    test_render_proto_renders_query_response_model_and_enum_types()
    test_render_proto_emits_optional_only_for_nullable_singular_fields()
    project_with_manifests(tmp_path)
    test_generate_proto_from_manifests_writes_file(project_with_manifests)
    test_generate_proto_skips_empty_context_dirs(tmp_path)
    test_compile_proto_python_produces_pb2(project_with_manifests)
    test_compile_proto_python_without_grpc_tools_returns_helpful_error(tmp_path;monkeypatch)
    test_compile_proto_typescript_missing_protoc_is_reported(tmp_path;monkeypatch)
    test_cli_gen_proto_requires_manifests(tmp_path;capsys)
    test_cli_gen_proto_end_to_end(project_with_manifests;capsys)
    test_cli_gen_grpc_python_reports_ok_or_missing(project_with_manifests;capsys)
  tests/test_pydantic_cross_check.py:
    e: project_root,_write_contract,_write_pydantic_module,test_aligned_enum_and_literal_are_ok,test_contract_enum_narrower_than_literal_is_flagged,test_output_contract_wider_than_literal_is_warning_not_error,test_input_contract_wider_than_literal_is_error,test_input_pydantic_wider_than_contract_is_ok,test_missing_pydantic_field_is_silently_skipped,test_contract_without_layers_python_is_skipped,test_optional_literal_union_is_handled,test_cross_check_contracts_returns_pairs
    project_root(tmp_path)
    _write_contract(project_root;filename;data)
    _write_pydantic_module(project_root;body)
    test_aligned_enum_and_literal_are_ok(project_root)
    test_contract_enum_narrower_than_literal_is_flagged(project_root)
    test_output_contract_wider_than_literal_is_warning_not_error(project_root)
    test_input_contract_wider_than_literal_is_error(project_root)
    test_input_pydantic_wider_than_contract_is_ok(project_root)
    test_missing_pydantic_field_is_silently_skipped(project_root)
    test_contract_without_layers_python_is_skipped(tmp_path)
    test_optional_literal_union_is_handled(project_root)
    test_cross_check_contracts_returns_pairs(project_root)
  tests/test_refactor.py:
    e: synthetic_project,test_frontend_scanner_extracts_ids_and_api_calls,test_backend_scanner_extracts_models,test_frontend_find_pages_for_route,test_refactor_pipeline_seeded_writes_modules,test_louvain_like_groups_connected_nodes,test_seeded_clusterer_assigns_by_best_score
    synthetic_project(tmp_path)
    test_frontend_scanner_extracts_ids_and_api_calls(synthetic_project)
    test_backend_scanner_extracts_models(synthetic_project)
    test_frontend_find_pages_for_route(synthetic_project)
    test_refactor_pipeline_seeded_writes_modules(synthetic_project;tmp_path)
    test_louvain_like_groups_connected_nodes()
    test_seeded_clusterer_assigns_by_best_score()
  tests/test_resolve.py:
    e: _write,_scan,project,test_no_changes_when_manifests_match,test_added_optional_field_is_non_breaking,test_added_required_field_is_breaking,test_removed_field_and_type_change_are_breaking,test_rename_detection,test_emits_change_is_metadata_only,test_apply_resolution_rewrites_manifests,test_resolution_json,test_cli_resolve_strict_exits_nonzero_on_breaking,test_cli_resolve_apply_fast_forwards,test_cli_resolve_json_flag
    _write(path;body)
    _scan(cfg_path)
    project(tmp_path)
    test_no_changes_when_manifests_match(project)
    test_added_optional_field_is_non_breaking(project)
    test_added_required_field_is_breaking(project)
    test_removed_field_and_type_change_are_breaking(project)
    test_rename_detection(project)
    test_emits_change_is_metadata_only(project)
    test_apply_resolution_rewrites_manifests(project)
    test_resolution_json(project)
    test_cli_resolve_strict_exits_nonzero_on_breaking(project;capsys)
    test_cli_resolve_apply_fast_forwards(project;capsys)
    test_cli_resolve_json_flag(project;capsys)
  tests/test_scan.py:
    e: _write,customer_project,test_scan_detects_decorator_based,test_scan_detects_heuristics_in_device_context,test_scan_skips_excluded_paths,test_scan_assigns_contexts_by_longest_match,test_scan_reports_syntax_error,test_incremental_scan_reuses_cache,test_incremental_scan_invalidates_on_change,test_cache_prunes_deleted_files,test_render_json_roundtrip,test_render_html_contains_summary,test_cli_scan_text_output,test_cli_scan_json_roundtrip,test_cli_scan_strict_heuristics_fails
    _write(path;body)
    customer_project(tmp_path)
    test_scan_detects_decorator_based(customer_project)
    test_scan_detects_heuristics_in_device_context(customer_project)
    test_scan_skips_excluded_paths(customer_project)
    test_scan_assigns_contexts_by_longest_match(tmp_path)
    test_scan_reports_syntax_error(tmp_path)
    test_incremental_scan_reuses_cache(customer_project)
    test_incremental_scan_invalidates_on_change(customer_project)
    test_cache_prunes_deleted_files(customer_project)
    test_render_json_roundtrip(customer_project)
    test_render_html_contains_summary(customer_project)
    test_cli_scan_text_output(customer_project;capsys)
    test_cli_scan_json_roundtrip(customer_project;capsys;tmp_path)
    test_cli_scan_strict_heuristics_fails(customer_project)
  tests/test_services.py:
    e: _write,project_with_manifests,test_generate_services_writes_package_per_context,test_generate_services_rejects_unknown_bus,test_generated_python_files_are_syntactically_valid,test_generated_server_has_servicers_and_methods,test_generated_worker_respects_grpc_port,test_requirements_match_bus,test_publisher_module_is_importable_in_memory_mode,test_compose_has_bus_and_services,test_compose_redis_bus,test_compose_memory_bus_has_no_broker,test_generate_services_copies_pb2_when_available,test_cli_gen_services_defaults_bus_from_config,test_cli_gen_services_requires_manifests,test_cli_gen_services_bus_override
    _write(path;body)
    project_with_manifests(tmp_path)
    test_generate_services_writes_package_per_context(project_with_manifests)
    test_generate_services_rejects_unknown_bus(project_with_manifests)
    test_generated_python_files_are_syntactically_valid(project_with_manifests)
    test_generated_server_has_servicers_and_methods(project_with_manifests)
    test_generated_worker_respects_grpc_port(project_with_manifests)
    test_requirements_match_bus(project_with_manifests)
    test_publisher_module_is_importable_in_memory_mode(project_with_manifests;monkeypatch)
    test_compose_has_bus_and_services(project_with_manifests)
    test_compose_redis_bus(project_with_manifests)
    test_compose_memory_bus_has_no_broker(project_with_manifests)
    test_generate_services_copies_pb2_when_available(project_with_manifests)
    test_cli_gen_services_defaults_bus_from_config(project_with_manifests;capsys)
    test_cli_gen_services_requires_manifests(tmp_path;capsys)
    test_cli_gen_services_bus_override(project_with_manifests;capsys)
  tests/test_tools.py:
    e: test_run_doctor_basic,test_init_project_writes_scaffold,test_init_project_respects_no_gitignore,test_init_project_appends_to_existing_gitignore,test_cli_doctor,test_cli_init
    test_run_doctor_basic()
    test_init_project_writes_scaffold(tmp_path)
    test_init_project_respects_no_gitignore(tmp_path)
    test_init_project_appends_to_existing_gitignore(tmp_path)
    test_cli_doctor(capsys)
    test_cli_init(tmp_path;capsys)
  tests/test_watch.py:
    e: _write,project,test_rebuild_once_runs_scan_and_manifests,test_engine_first_poll_returns_none,test_engine_detects_modifications,test_engine_detects_new_and_deleted_files,test_engine_ignores_state_dir_writes,test_engine_run_stops_after_first_rebuild,test_cli_watch_once
    _write(path;body)
    project(tmp_path)
    test_rebuild_once_runs_scan_and_manifests(project)
    test_engine_first_poll_returns_none(project)
    test_engine_detects_modifications(project)
    test_engine_detects_new_and_deleted_files(project)
    test_engine_ignores_state_dir_writes(project)
    test_engine_run_stops_after_first_rebuild(project)
    test_cli_watch_once(project;capsys)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('swop', '0.2.16', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 34, 'less').
project_file('examples/src/api.py', 12, 'python').
project_file('examples/src/models.py', 16, 'python').
project_file('project.sh', 44, 'shell').
project_file('swop/__init__.py', 169, 'python').
project_file('swop/cli.py', 553, 'python').
project_file('swop/commands.py', 595, 'python').
project_file('swop/config.py', 210, 'python').
project_file('swop/contracts/__init__.py', 42, 'python').
project_file('swop/contracts/adapter.py', 173, 'python').
project_file('swop/contracts/reader.py', 170, 'python').
project_file('swop/core.py', 108, 'python').
project_file('swop/cqrs/__init__.py', 29, 'python').
project_file('swop/cqrs/decorators.py', 159, 'python').
project_file('swop/cqrs/registry.py', 106, 'python').
project_file('swop/export/__init__.py', 12, 'python').
project_file('swop/export/docker.py', 33, 'python').
project_file('swop/export/yaml.py', 48, 'python').
project_file('swop/graph.py', 50, 'python').
project_file('swop/introspect/__init__.py', 13, 'python').
project_file('swop/introspect/backend.py', 33, 'python').
project_file('swop/introspect/frontend.py', 41, 'python').
project_file('swop/manifests/__init__.py', 24, 'python').
project_file('swop/manifests/generator.py', 746, 'python').
project_file('swop/markpact/__init__.py', 28, 'python').
project_file('swop/markpact/doql_bridge.py', 532, 'python').
project_file('swop/markpact/graph_builder.py', 541, 'python').
project_file('swop/markpact/parser.py', 142, 'python').
project_file('swop/markpact/spec_models.py', 213, 'python').
project_file('swop/markpact/sync_engine.py', 212, 'python').
project_file('swop/proto/__init__.py', 31, 'python').
project_file('swop/proto/compiler.py', 206, 'python').
project_file('swop/proto/generator.py', 534, 'python').
project_file('swop/reconcile.py', 106, 'python').
project_file('swop/refactor/__init__.py', 44, 'python').
project_file('swop/refactor/clustering.py', 161, 'python').
project_file('swop/refactor/compose_builder.py', 120, 'python').
project_file('swop/refactor/graph.py', 108, 'python').
project_file('swop/refactor/module_builder.py', 309, 'python').
project_file('swop/refactor/pipeline.py', 302, 'python').
project_file('swop/refactor/scanner/__init__.py', 8, 'python').
project_file('swop/refactor/scanner/backend.py', 164, 'python').
project_file('swop/refactor/scanner/db.py', 54, 'python').
project_file('swop/refactor/scanner/frontend.py', 139, 'python').
project_file('swop/registry/__init__.py', 45, 'python').
project_file('swop/registry/bridge.py', 77, 'python').
project_file('swop/registry/generator.py', 196, 'python').
project_file('swop/registry/loader.py', 40, 'python').
project_file('swop/registry/pydantic_cross_check.py', 360, 'python').
project_file('swop/registry/validator.py', 112, 'python').
project_file('swop/resolve/__init__.py', 35, 'python').
project_file('swop/resolve/resolver.py', 482, 'python').
project_file('swop/scan/__init__.py', 33, 'python').
project_file('swop/scan/cache.py', 116, 'python').
project_file('swop/scan/render.py', 142, 'python').
project_file('swop/scan/report.py', 217, 'python').
project_file('swop/scan/scanner.py', 616, 'python').
project_file('swop/services/__init__.py', 31, 'python').
project_file('swop/services/generator.py', 684, 'python').
project_file('swop/sync.py', 48, 'python').
project_file('swop/tools/__init__.py', 33, 'python').
project_file('swop/tools/doctor.py', 195, 'python').
project_file('swop/tools/doctor_deep.py', 369, 'python').
project_file('swop/tools/hook.py', 222, 'python').
project_file('swop/tools/init.py', 161, 'python').
project_file('swop/utils.py', 24, 'python').
project_file('swop/versioning.py', 26, 'python').
project_file('swop/watch/__init__.py', 18, 'python').
project_file('swop/watch/engine.py', 211, 'python').
project_file('tests/__init__.py', 4, 'python').
project_file('tests/test_cli.py', 27, 'python').
project_file('tests/test_config.py', 128, 'python').
project_file('tests/test_core.py', 82, 'python').
project_file('tests/test_cqrs.py', 145, 'python').
project_file('tests/test_doctor_deep.py', 276, 'python').
project_file('tests/test_hook.py', 170, 'python').
project_file('tests/test_manifests.py', 417, 'python').
project_file('tests/test_markpact.py', 803, 'python').
project_file('tests/test_proto.py', 413, 'python').
project_file('tests/test_pydantic_cross_check.py', 437, 'python').
project_file('tests/test_refactor.py', 191, 'python').
project_file('tests/test_resolve.py', 423, 'python').
project_file('tests/test_scan.py', 351, 'python').
project_file('tests/test_services.py', 351, 'python').
project_file('tests/test_tools.py', 78, 'python').
project_file('tests/test_watch.py', 174, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('examples/src/api.py', 'list_devices', 0, 1, 1).
python_function('examples/src/api.py', 'create_reading', 1, 1, 1).
python_function('swop/cli.py', '_build_parser', 0, 1, 6).
python_function('swop/cli.py', 'main', 1, 1, 3).
python_function('swop/commands.py', '_build_runtime', 1, 1, 4).
python_function('swop/commands.py', '_cmd_sync', 1, 3, 3).
python_function('swop/commands.py', '_cmd_inspect', 1, 3, 3).
python_function('swop/commands.py', '_cmd_diff', 1, 2, 3).
python_function('swop/commands.py', '_cmd_state', 1, 1, 4).
python_function('swop/commands.py', '_cmd_export', 1, 2, 3).
python_function('swop/commands.py', '_cmd_doctor', 1, 7, 9).
python_function('swop/commands.py', '_cmd_hook', 1, 6, 10).
python_function('swop/commands.py', '_cmd_init', 1, 2, 6).
python_function('swop/commands.py', '_cmd_scan', 1, 14, 12).
python_function('swop/commands.py', '_cmd_gen_manifests', 1, 8, 8).
python_function('swop/commands.py', '_cmd_gen_proto', 1, 7, 8).
python_function('swop/commands.py', '_cmd_gen_grpc_python', 1, 7, 7).
python_function('swop/commands.py', '_cmd_gen_grpc_ts', 1, 7, 7).
python_function('swop/commands.py', '_cmd_gen_services', 1, 12, 8).
python_function('swop/commands.py', '_cmd_gen_registry', 1, 14, 10).
python_function('swop/commands.py', '_cmd_watch', 1, 6, 11).
python_function('swop/commands.py', '_cmd_resolve', 1, 9, 10).
python_function('swop/commands.py', '_cmd_refactor', 1, 7, 7).
python_function('swop/commands.py', '_generate_parse_manifest', 1, 2, 5).
python_function('swop/commands.py', '_generate_build_graph', 2, 14, 12).
python_function('swop/commands.py', '_generate_check_files', 2, 9, 4).
python_function('swop/commands.py', '_generate_update_from_disk', 2, 5, 4).
python_function('swop/commands.py', '_generate_sync_files', 2, 5, 4).
python_function('swop/commands.py', '_generate_outputs', 2, 5, 5).
python_function('swop/commands.py', '_cmd_generate', 1, 7, 11).
python_function('swop/config.py', '_expand_env', 1, 6, 6).
python_function('swop/config.py', '_pop_known', 2, 3, 1).
python_function('swop/config.py', '_parse_context', 1, 3, 7).
python_function('swop/config.py', '_parse_bus', 1, 3, 8).
python_function('swop/config.py', '_parse_read_models', 1, 3, 8).
python_function('swop/config.py', 'load_config', 1, 6, 10).
python_function('swop/config.py', '_from_dict', 2, 8, 12).
python_function('swop/contracts/adapter.py', '_contract_kind', 1, 4, 1).
python_function('swop/contracts/adapter.py', '_contract_name', 1, 4, 1).
python_function('swop/contracts/adapter.py', '_contract_context', 1, 1, 1).
python_function('swop/contracts/adapter.py', '_contract_fields', 1, 4, 7).
python_function('swop/contracts/adapter.py', 'contract_to_detection', 1, 6, 9).
python_function('swop/contracts/adapter.py', 'contracts_to_detections', 1, 4, 6).
python_function('swop/contracts/reader.py', 'load_contracts', 1, 5, 8).
python_function('swop/contracts/reader.py', '_check_layer_paths', 3, 6, 6).
python_function('swop/contracts/reader.py', 'validate_contract', 1, 21, 3).
python_function('swop/contracts/reader.py', 'validate_all', 1, 4, 5).
python_function('swop/cqrs/decorators.py', '_collect_source', 1, 3, 2).
python_function('swop/cqrs/decorators.py', '_normalize_emits', 1, 4, 4).
python_function('swop/cqrs/decorators.py', '_make_decorator', 1, 1, 10).
python_function('swop/cqrs/decorators.py', 'handler', 1, 7, 9).
python_function('swop/cqrs/registry.py', 'get_registry', 0, 1, 0).
python_function('swop/cqrs/registry.py', 'reset_registry', 0, 1, 1).
python_function('swop/manifests/generator.py', 'generate_manifests', 2, 10, 11).
python_function('swop/manifests/generator.py', '_handler_index', 1, 4, 1).
python_function('swop/manifests/generator.py', '_render_manifest', 5, 2, 3).
python_function('swop/manifests/generator.py', '_render_entry', 5, 14, 13).
python_function('swop/manifests/generator.py', '_render_source', 1, 2, 0).
python_function('swop/manifests/generator.py', '_render_field', 1, 3, 2).
python_function('swop/manifests/generator.py', '_render_handler', 1, 2, 0).
python_function('swop/manifests/generator.py', '_render_bus', 2, 6, 3).
python_function('swop/manifests/generator.py', '_camel_to_dot', 1, 5, 4).
python_function('swop/manifests/generator.py', '_safe_dirname', 1, 2, 2).
python_function('swop/manifests/generator.py', '_render_query_response_metadata', 3, 7, 8).
python_function('swop/manifests/generator.py', '_collect_supporting_types', 4, 1, 2).
python_function('swop/manifests/generator.py', '_collect_supporting_types_from_fields', 5, 7, 11).
python_function('swop/manifests/generator.py', '_annotation_type_names', 1, 6, 3).
python_function('swop/manifests/generator.py', '_first_custom_type_name', 1, 2, 1).
python_function('swop/manifests/generator.py', '_find_handler_return_type', 2, 6, 2).
python_function('swop/manifests/generator.py', '_module_ast', 2, 4, 3).
python_function('swop/manifests/generator.py', '_module_classes', 2, 5, 2).
python_function('swop/manifests/generator.py', '_find_class_in_module', 3, 1, 2).
python_function('swop/manifests/generator.py', '_module_imports', 3, 14, 6).
python_function('swop/manifests/generator.py', '_resolve_import_module_paths', 4, 9, 6).
python_function('swop/manifests/generator.py', '_resolve_class_definition', 4, 6, 5).
python_function('swop/manifests/generator.py', '_resolve_symbol_from_module', 5, 5, 6).
python_function('swop/manifests/generator.py', '_search_class_files', 3, 6, 3).
python_function('swop/manifests/generator.py', '_is_enum_class', 1, 3, 1).
python_function('swop/manifests/generator.py', '_render_enum_type', 2, 6, 3).
python_function('swop/manifests/generator.py', '_extract_class_fields', 1, 16, 9).
python_function('swop/manifests/generator.py', '_expr_name', 1, 4, 2).
python_function('swop/manifests/generator.py', '_unparse', 1, 2, 1).
python_function('swop/manifests/generator.py', '_render_default', 1, 3, 3).
python_function('swop/manifests/generator.py', '_annotation_is_optional', 1, 11, 2).
python_function('swop/manifests/generator.py', '_dedupe_type_defs', 1, 4, 5).
python_function('swop/markpact/graph_builder.py', 'build_project_graph', 1, 1, 19).
python_function('swop/markpact/graph_builder.py', '_build_models', 2, 7, 3).
python_function('swop/markpact/graph_builder.py', '_build_services', 2, 13, 7).
python_function('swop/markpact/graph_builder.py', '_build_ui_bindings', 2, 11, 8).
python_function('swop/markpact/graph_builder.py', '_build_databases', 2, 6, 2).
python_function('swop/markpact/graph_builder.py', '_build_workflows', 2, 9, 3).
python_function('swop/markpact/graph_builder.py', '_build_roles', 2, 6, 2).
python_function('swop/markpact/graph_builder.py', '_build_integrations', 2, 4, 2).
python_function('swop/markpact/graph_builder.py', '_build_webhooks', 2, 7, 2).
python_function('swop/markpact/graph_builder.py', '_build_api_clients', 2, 8, 2).
python_function('swop/markpact/graph_builder.py', '_build_environments', 2, 6, 2).
python_function('swop/markpact/graph_builder.py', '_build_infrastructures', 2, 6, 2).
python_function('swop/markpact/graph_builder.py', '_build_ingresses', 2, 6, 2).
python_function('swop/markpact/graph_builder.py', '_build_ci_configs', 2, 7, 3).
python_function('swop/markpact/graph_builder.py', '_build_data_sources', 2, 10, 2).
python_function('swop/markpact/graph_builder.py', '_build_templates', 2, 7, 2).
python_function('swop/markpact/graph_builder.py', '_build_documents', 2, 7, 2).
python_function('swop/markpact/graph_builder.py', '_build_reports', 2, 7, 2).
python_function('swop/markpact/graph_builder.py', '_build_deploy', 2, 5, 4).
python_function('swop/markpact/sync_engine.py', '_hash', 1, 1, 3).
python_function('swop/proto/compiler.py', '_iter_proto_files', 1, 1, 3).
python_function('swop/proto/compiler.py', '_proto_roots', 2, 1, 2).
python_function('swop/proto/compiler.py', '_run', 2, 2, 3).
python_function('swop/proto/compiler.py', 'compile_proto_python', 2, 8, 14).
python_function('swop/proto/compiler.py', 'compile_proto_typescript', 2, 10, 14).
python_function('swop/proto/generator.py', '_map_python_type', 1, 18, 8).
python_function('swop/proto/generator.py', '_load_manifest', 1, 4, 4).
python_function('swop/proto/generator.py', '_iter_contexts', 1, 6, 6).
python_function('swop/proto/generator.py', 'generate_proto_from_manifests', 2, 8, 13).
python_function('swop/proto/generator.py', 'render_proto_for_context', 4, 26, 18).
python_function('swop/proto/generator.py', '_render_message', 5, 13, 9).
python_function('swop/proto/generator.py', '_render_command_response', 2, 2, 1).
python_function('swop/proto/generator.py', '_render_query_response', 2, 2, 0).
python_function('swop/proto/generator.py', '_collect_known_types', 3, 6, 4).
python_function('swop/proto/generator.py', '_render_type_definition', 4, 7, 4).
python_function('swop/proto/generator.py', '_render_enum', 2, 7, 8).
python_function('swop/proto/generator.py', '_service_name', 2, 3, 3).
python_function('swop/proto/generator.py', '_safe_ident', 1, 3, 3).
python_function('swop/refactor/pipeline.py', '_tokenize', 1, 4, 4).
python_function('swop/registry/bridge.py', '_fields', 2, 3, 6).
python_function('swop/registry/bridge.py', 'bridge_contracts_to_detections', 1, 9, 9).
python_function('swop/registry/generator.py', '_ep', 1, 3, 3).
python_function('swop/registry/generator.py', '_ch', 1, 3, 3).
python_function('swop/registry/generator.py', 'generate_registry_json', 1, 7, 7).
python_function('swop/registry/generator.py', 'generate_registry_md', 1, 32, 13).
python_function('swop/registry/generator.py', 'write_registry', 2, 2, 7).
python_function('swop/registry/loader.py', 'load_contracts', 1, 8, 9).
python_function('swop/registry/pydantic_cross_check.py', '_extract_literal_values', 1, 7, 4).
python_function('swop/registry/pydantic_cross_check.py', '_node_name', 1, 4, 2).
python_function('swop/registry/pydantic_cross_check.py', '_literal_slice_values', 1, 6, 4).
python_function('swop/registry/pydantic_cross_check.py', '_collect_literal_fields', 1, 7, 3).
python_function('swop/registry/pydantic_cross_check.py', '_load_literal_fields', 1, 3, 3).
python_function('swop/registry/pydantic_cross_check.py', '_iter_enum_fields', 2, 12, 6).
python_function('swop/registry/pydantic_cross_check.py', '_contract_schemas', 1, 3, 3).
python_function('swop/registry/pydantic_cross_check.py', '_classify_drift', 3, 6, 2).
python_function('swop/registry/pydantic_cross_check.py', '_parse_layer_path', 1, 4, 2).
python_function('swop/registry/pydantic_cross_check.py', 'cross_check_contract', 1, 14, 14).
python_function('swop/registry/pydantic_cross_check.py', 'cross_check_contracts', 1, 2, 1).
python_function('swop/registry/validator.py', 'validate_contract', 1, 5, 6).
python_function('swop/registry/validator.py', '_check_keys', 3, 3, 1).
python_function('swop/registry/validator.py', '_check_kind', 3, 2, 2).
python_function('swop/registry/validator.py', '_check_layer_paths', 3, 7, 6).
python_function('swop/resolve/resolver.py', 'resolve_schema_drift', 2, 4, 9).
python_function('swop/resolve/resolver.py', 'apply_resolution', 3, 3, 2).
python_function('swop/resolve/resolver.py', '_index_from_detections', 1, 10, 6).
python_function('swop/resolve/resolver.py', '_handler_shape', 1, 3, 0).
python_function('swop/resolve/resolver.py', '_index_from_manifests', 1, 15, 10).
python_function('swop/resolve/resolver.py', '_diff_context_kind', 5, 11, 9).
python_function('swop/resolve/resolver.py', '_diff_fields', 6, 13, 7).
python_function('swop/resolve/resolver.py', '_diff_metadata', 6, 9, 5).
python_function('swop/resolve/resolver.py', '_diff_entry', 6, 3, 3).
python_function('swop/resolve/resolver.py', '_field_signature', 1, 4, 5).
python_function('swop/resolve/resolver.py', '_handler_sig', 1, 8, 2).
python_function('swop/scan/render.py', 'render_json', 2, 2, 2).
python_function('swop/scan/render.py', 'render_html', 1, 8, 10).
python_function('swop/scan/render.py', 'write_report', 3, 3, 5).
python_function('swop/scan/scanner.py', '_scan_file', 7, 13, 16).
python_function('swop/scan/scanner.py', 'scan_project', 1, 10, 14).
python_function('swop/scan/scanner.py', '_new_ctx_summary', 1, 1, 1).
python_function('swop/scan/scanner.py', '_resolve_contexts', 1, 1, 3).
python_function('swop/scan/scanner.py', '_iter_python_files', 3, 10, 11).
python_function('swop/scan/scanner.py', '_matches_any', 2, 5, 3).
python_function('swop/scan/scanner.py', '_context_for_path', 3, 8, 4).
python_function('swop/scan/scanner.py', '_extract_detections', 5, 7, 7).
python_function('swop/scan/scanner.py', '_module_name_from_path', 1, 7, 4).
python_function('swop/scan/scanner.py', '_decorator_name', 1, 4, 2).
python_function('swop/scan/scanner.py', '_base_name', 1, 3, 1).
python_function('swop/scan/scanner.py', '_extract_decorator_emits', 1, 9, 2).
python_function('swop/scan/scanner.py', '_extract_decorator_context', 1, 8, 1).
python_function('swop/scan/scanner.py', '_extract_handler_target', 1, 6, 1).
python_function('swop/scan/scanner.py', '_classify_decorator', 8, 5, 6).
python_function('swop/scan/scanner.py', '_classify_heuristic', 7, 7, 5).
python_function('swop/scan/scanner.py', '_classify', 5, 9, 4).
python_function('swop/scan/scanner.py', '_kind_by_suffix', 1, 4, 1).
python_function('swop/scan/scanner.py', '_kind_by_base', 1, 3, 0).
python_function('swop/scan/scanner.py', '_handler_target_from_method', 1, 11, 1).
python_function('swop/scan/scanner.py', '_handler_method_name', 1, 4, 1).
python_function('swop/scan/scanner.py', '_extract_ann_field', 2, 7, 7).
python_function('swop/scan/scanner.py', '_extract_plain_field', 2, 6, 6).
python_function('swop/scan/scanner.py', '_extract_fields', 1, 5, 6).
python_function('swop/scan/scanner.py', '_unparse', 1, 2, 1).
python_function('swop/scan/scanner.py', '_render_default', 1, 3, 3).
python_function('swop/scan/scanner.py', '_annotation_is_optional', 1, 13, 1).
python_function('swop/services/generator.py', 'generate_services', 2, 11, 19).
python_function('swop/services/generator.py', '_write_context_package', 0, 7, 18).
python_function('swop/services/generator.py', '_classify_file', 1, 5, 1).
python_function('swop/services/generator.py', '_render_init', 1, 1, 0).
python_function('swop/services/generator.py', '_render_worker', 0, 2, 0).
python_function('swop/services/generator.py', '_render_server', 0, 7, 5).
python_function('swop/services/generator.py', '_render_publisher', 1, 1, 0).
python_function('swop/services/generator.py', '_render_requirements', 1, 4, 2).
python_function('swop/services/generator.py', '_render_dockerfile', 1, 1, 0).
python_function('swop/services/generator.py', '_render_env', 0, 1, 1).
python_function('swop/services/generator.py', '_render_compose', 2, 6, 6).
python_function('swop/services/generator.py', '_default_bus_url', 1, 1, 1).
python_function('swop/services/generator.py', '_render_readme', 2, 3, 1).
python_function('swop/services/generator.py', '_load_yaml', 1, 3, 3).
python_function('swop/services/generator.py', '_safe_ident', 1, 3, 3).
python_function('swop/services/generator.py', '_camel', 1, 4, 3).
python_function('swop/tools/doctor.py', '_check_python', 0, 3, 1).
python_function('swop/tools/doctor.py', '_check_swop', 0, 1, 1).
python_function('swop/tools/doctor.py', '_check_pyyaml', 0, 3, 1).
python_function('swop/tools/doctor.py', '_run_version', 1, 5, 3).
python_function('swop/tools/doctor.py', '_first_version', 1, 3, 2).
python_function('swop/tools/doctor.py', '_check_binary', 2, 4, 4).
python_function('swop/tools/doctor.py', '_check_git_repo', 1, 7, 6).
python_function('swop/tools/doctor.py', 'run_doctor', 1, 2, 9).
python_function('swop/tools/doctor_deep.py', '_check_scan_vs_manifests', 1, 8, 8).
python_function('swop/tools/doctor_deep.py', '_check_manifests_vs_proto', 1, 15, 13).
python_function('swop/tools/doctor_deep.py', '_check_proto_vs_python', 1, 15, 12).
python_function('swop/tools/doctor_deep.py', '_check_manifests_vs_services', 1, 15, 10).
python_function('swop/tools/doctor_deep.py', 'run_deep_doctor', 1, 1, 6).
python_function('swop/tools/doctor_deep.py', '_latest_mtime', 1, 6, 4).
python_function('swop/tools/hook.py', '_git_dir', 1, 13, 12).
python_function('swop/tools/hook.py', '_hook_path', 1, 2, 2).
python_function('swop/tools/hook.py', '_is_swop_hook', 1, 2, 1).
python_function('swop/tools/hook.py', 'install_hook', 1, 5, 6).
python_function('swop/tools/hook.py', 'uninstall_hook', 1, 4, 5).
python_function('swop/tools/hook.py', 'hook_status', 1, 4, 4).
python_function('swop/tools/hook.py', '_make_executable', 1, 2, 2).
python_function('swop/tools/init.py', 'init_project', 1, 14, 9).
python_function('swop/tools/init.py', '_merge_gitignore', 2, 9, 7).
python_function('swop/utils.py', 'stable_hash', 1, 1, 4).
python_function('swop/utils.py', 'is_callable', 1, 1, 1).
python_function('swop/utils.py', 'get_docstring', 1, 1, 1).
python_function('swop/watch/engine.py', 'rebuild_once', 1, 2, 5).
python_function('swop/watch/engine.py', '_diff_snapshots', 2, 5, 4).
python_function('tests/test_cli.py', 'test_cli_state_command', 1, 3, 2).
python_function('tests/test_cli.py', 'test_cli_export_docker', 1, 3, 2).
python_function('tests/test_cli.py', 'test_cli_inspect_backend', 1, 3, 2).
python_function('tests/test_config.py', '_write', 2, 1, 1).
python_function('tests/test_config.py', 'test_load_minimal_config', 1, 10, 2).
python_function('tests/test_config.py', 'test_load_full_config', 2, 13, 5).
python_function('tests/test_config.py', 'test_env_vars_keep_literal_when_missing', 1, 3, 2).
python_function('tests/test_config.py', 'test_missing_config_raises', 1, 1, 2).
python_function('tests/test_config.py', 'test_bounded_context_without_required_fields', 1, 1, 3).
python_function('tests/test_config.py', 'test_unknown_keys_stored_in_extra', 1, 2, 2).
python_function('tests/test_core.py', '_runtime', 1, 1, 3).
python_function('tests/test_core.py', 'test_add_model_commits_version', 0, 4, 2).
python_function('tests/test_core.py', 'test_run_sync_detects_invalid_bindings', 0, 3, 4).
python_function('tests/test_core.py', 'test_auto_heal_removes_invalid_bindings', 0, 4, 4).
python_function('tests/test_core.py', 'test_strict_mode_raises_on_invalid_binding', 0, 1, 5).
python_function('tests/test_core.py', 'test_state_yaml_is_serializable', 0, 3, 5).
python_function('tests/test_core.py', 'test_docker_export_contains_services', 0, 3, 3).
python_function('tests/test_cqrs.py', '_reset', 0, 1, 2).
python_function('tests/test_cqrs.py', 'test_command_decorator_registers_class', 0, 7, 6).
python_function('tests/test_cqrs.py', 'test_query_and_event_decorators_kept_separate', 0, 3, 5).
python_function('tests/test_cqrs.py', 'test_handler_decorator_links_to_target_class', 0, 4, 5).
python_function('tests/test_cqrs.py', 'test_handler_decorator_accepts_string_target', 0, 3, 3).
python_function('tests/test_cqrs.py', 'test_decorators_reject_non_class_targets', 0, 1, 2).
python_function('tests/test_cqrs.py', 'test_registry_summary_groups_by_kind', 0, 2, 6).
python_function('tests/test_cqrs.py', 'test_emits_accepts_classes_and_strings', 0, 2, 3).
python_function('tests/test_cqrs.py', 'test_reset_registry_clears_state', 0, 3, 4).
python_function('tests/test_cqrs.py', 'test_local_registry_is_independent', 0, 3, 5).
python_function('tests/test_doctor_deep.py', '_write', 2, 1, 3).
python_function('tests/test_doctor_deep.py', '_bump_mtime', 2, 1, 2).
python_function('tests/test_doctor_deep.py', 'full_project', 1, 2, 8).
python_function('tests/test_doctor_deep.py', 'test_run_deep_doctor_reports_ok_when_everything_generated', 1, 8, 6).
python_function('tests/test_doctor_deep.py', 'test_scan_vs_manifests_flags_breaking_change', 1, 3, 4).
python_function('tests/test_doctor_deep.py', 'test_manifests_vs_proto_warns_when_proto_is_stale', 1, 3, 3).
python_function('tests/test_doctor_deep.py', 'test_manifests_vs_proto_fails_when_proto_missing', 1, 3, 3).
python_function('tests/test_doctor_deep.py', 'test_proto_vs_python_fails_when_stubs_missing', 1, 3, 7).
python_function('tests/test_doctor_deep.py', 'test_proto_vs_python_warns_without_python_dir', 1, 2, 6).
python_function('tests/test_doctor_deep.py', 'test_manifests_vs_services_fails_when_package_missing', 1, 4, 5).
python_function('tests/test_doctor_deep.py', 'test_manifests_vs_services_fails_when_incomplete', 1, 3, 4).
python_function('tests/test_doctor_deep.py', 'test_cli_doctor_deep_ok', 2, 4, 4).
python_function('tests/test_doctor_deep.py', 'test_cli_doctor_deep_nonzero_on_drift', 2, 4, 4).
python_function('tests/test_doctor_deep.py', 'test_cli_doctor_without_deep_does_not_require_config', 2, 3, 3).
python_function('tests/test_hook.py', '_fake_git_repo', 1, 1, 1).
python_function('tests/test_hook.py', 'test_install_hook_creates_executable_file', 1, 6, 4).
python_function('tests/test_hook.py', 'test_install_hook_on_non_git_repo_returns_error', 1, 3, 1).
python_function('tests/test_hook.py', 'test_install_hook_refuses_to_overwrite_foreign_hook', 1, 4, 4).
python_function('tests/test_hook.py', 'test_install_hook_with_force_overwrites', 1, 3, 4).
python_function('tests/test_hook.py', 'test_install_is_idempotent', 1, 4, 3).
python_function('tests/test_hook.py', 'test_uninstall_removes_swop_hook', 1, 3, 4).
python_function('tests/test_hook.py', 'test_uninstall_preserves_foreign_hook', 1, 4, 5).
python_function('tests/test_hook.py', 'test_uninstall_skipped_when_absent', 1, 3, 2).
python_function('tests/test_hook.py', 'test_hook_status_reports_all_states', 1, 7, 4).
python_function('tests/test_hook.py', 'test_install_follows_git_file_worktree_pointer', 1, 3, 3).
python_function('tests/test_hook.py', 'test_cli_hook_install_and_uninstall', 2, 7, 4).
python_function('tests/test_hook.py', 'test_cli_hook_install_non_git_errors', 2, 3, 3).
python_function('tests/test_manifests.py', '_write', 2, 1, 3).
python_function('tests/test_manifests.py', 'customer_project', 1, 1, 2).
python_function('tests/test_manifests.py', 'test_scan_extracts_fields_from_dataclass', 1, 13, 3).
python_function('tests/test_manifests.py', 'test_scan_handler_records_method_name', 1, 5, 3).
python_function('tests/test_manifests.py', 'test_generate_manifests_writes_per_context_files', 1, 6, 5).
python_function('tests/test_manifests.py', 'test_manifest_yaml_shape_for_command', 1, 19, 6).
python_function('tests/test_manifests.py', 'test_manifest_event_has_fields_but_no_bus', 1, 9, 7).
python_function('tests/test_manifests.py', 'test_manifest_heuristic_detection_carries_confidence', 1, 5, 5).
python_function('tests/test_manifests.py', 'test_manifest_query_includes_response_and_types', 1, 11, 6).
python_function('tests/test_manifests.py', 'test_generate_manifests_redis_bus', 1, 2, 7).
python_function('tests/test_manifests.py', 'test_generate_manifests_no_bus_when_unconfigured', 1, 2, 7).
python_function('tests/test_manifests.py', 'test_cli_gen_manifests', 2, 4, 4).
python_function('tests/test_manifests.py', 'test_cli_gen_manifests_skip_heuristics', 2, 4, 3).
python_function('tests/test_markpact.py', 'tmp_manifest', 1, 1, 1).
python_function('tests/test_markpact.py', 'test_parser_finds_all_blocks', 1, 3, 2).
python_function('tests/test_markpact.py', 'test_parser_counts_blocks', 1, 2, 3).
python_function('tests/test_markpact.py', 'test_parser_extracts_meta', 0, 5, 3).
python_function('tests/test_markpact.py', 'test_parser_doql_block_body', 0, 5, 2).
python_function('tests/test_markpact.py', 'test_parser_filter_by_kind', 1, 3, 3).
python_function('tests/test_markpact.py', 'test_parser_includes', 1, 3, 4).
python_function('tests/test_markpact.py', 'test_bridge_from_text', 0, 5, 3).
python_function('tests/test_markpact.py', 'test_bridge_missing_any_supported_blocks_raises', 0, 1, 3).
python_function('tests/test_markpact.py', 'test_bridge_strict_mode', 0, 2, 2).
python_function('tests/test_markpact.py', 'test_bridge_merge_multiple_doql', 0, 4, 4).
python_function('tests/test_markpact.py', 'test_graph_from_doql_spec', 0, 6, 4).
python_function('tests/test_markpact.py', 'test_graph_services_from_interfaces', 0, 4, 4).
python_function('tests/test_markpact.py', 'test_graph_ui_bindings_from_pages', 0, 3, 5).
python_function('tests/test_markpact.py', 'test_graph_databases_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_sync_check_identical', 1, 3, 5).
python_function('tests/test_markpact.py', 'test_sync_check_modified', 1, 3, 4).
python_function('tests/test_markpact.py', 'test_sync_check_missing', 1, 2, 3).
python_function('tests/test_markpact.py', 'test_sync_to_disk', 1, 3, 4).
python_function('tests/test_markpact.py', 'test_sync_to_disk_dry_run', 1, 3, 4).
python_function('tests/test_markpact.py', 'test_sync_from_disk', 1, 2, 4).
python_function('tests/test_markpact.py', 'test_diff_report', 1, 6, 4).
python_function('tests/test_markpact.py', 'test_graph_workflows_as_services', 0, 5, 4).
python_function('tests/test_markpact.py', 'test_graph_roles_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_api_clients_as_services', 0, 4, 4).
python_function('tests/test_markpact.py', 'test_graph_webhooks_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_integrations_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_environments_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_infrastructures_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_ingresses_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_ci_configs_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_data_sources_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_templates_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_documents_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_reports_as_services', 0, 3, 4).
python_function('tests/test_markpact.py', 'test_graph_deploy_as_service', 0, 4, 4).
python_function('tests/test_markpact.py', 'test_bridge_from_files_merge', 1, 4, 4).
python_function('tests/test_markpact.py', 'test_cli_generate_from_markpact', 1, 6, 5).
python_function('tests/test_markpact.py', 'test_cli_generate_sync_files', 1, 4, 5).
python_function('tests/test_markpact.py', 'test_cli_generate_sync_files_dry_run', 1, 3, 4).
python_function('tests/test_markpact.py', 'test_update_manifest_reverse_sync', 1, 4, 5).
python_function('tests/test_markpact.py', 'test_update_manifest_dry_run', 1, 3, 5).
python_function('tests/test_markpact.py', 'test_update_manifest_preserves_untracked_blocks', 1, 3, 5).
python_function('tests/test_markpact.py', 'test_cli_generate_check_files_ok', 1, 2, 5).
python_function('tests/test_markpact.py', 'test_cli_generate_check_files_strict_fails_on_drift', 1, 2, 3).
python_function('tests/test_markpact.py', 'test_cli_generate_from_disk', 1, 3, 6).
python_function('tests/test_markpact.py', 'test_cli_generate_from_disk_dry_run', 1, 3, 6).
python_function('tests/test_proto.py', '_write', 2, 1, 3).
python_function('tests/test_proto.py', 'test_map_python_type_basic', 3, 3, 2).
python_function('tests/test_proto.py', 'test_map_python_type_dict_becomes_map', 0, 3, 1).
python_function('tests/test_proto.py', 'test_map_python_type_unknown_name_is_stub', 0, 3, 1).
python_function('tests/test_proto.py', 'test_map_python_type_empty_is_string_stub', 0, 3, 1).
python_function('tests/test_proto.py', 'test_render_proto_for_context_builds_expected_shape', 0, 20, 2).
python_function('tests/test_proto.py', 'test_render_proto_adds_timestamp_import', 0, 3, 1).
python_function('tests/test_proto.py', 'test_render_proto_warns_on_unknown_user_type', 0, 2, 2).
python_function('tests/test_proto.py', 'test_render_proto_renders_query_response_model_and_enum_types', 0, 10, 2).
python_function('tests/test_proto.py', 'test_render_proto_emits_optional_only_for_nullable_singular_fields', 0, 6, 2).
python_function('tests/test_proto.py', 'project_with_manifests', 1, 1, 5).
python_function('tests/test_proto.py', 'test_generate_proto_from_manifests_writes_file', 1, 9, 3).
python_function('tests/test_proto.py', 'test_generate_proto_skips_empty_context_dirs', 1, 2, 2).
python_function('tests/test_proto.py', 'test_compile_proto_python_produces_pb2', 1, 8, 5).
python_function('tests/test_proto.py', 'test_compile_proto_python_without_grpc_tools_returns_helpful_error', 2, 3, 7).
python_function('tests/test_proto.py', 'test_compile_proto_typescript_missing_protoc_is_reported', 2, 3, 4).
python_function('tests/test_proto.py', 'test_cli_gen_proto_requires_manifests', 2, 3, 5).
python_function('tests/test_proto.py', 'test_cli_gen_proto_end_to_end', 2, 4, 4).
python_function('tests/test_proto.py', 'test_cli_gen_grpc_python_reports_ok_or_missing', 2, 6, 4).
python_function('tests/test_pydantic_cross_check.py', 'project_root', 1, 1, 2).
python_function('tests/test_pydantic_cross_check.py', '_write_contract', 3, 3, 4).
python_function('tests/test_pydantic_cross_check.py', '_write_pydantic_module', 2, 1, 2).
python_function('tests/test_pydantic_cross_check.py', 'test_aligned_enum_and_literal_are_ok', 1, 3, 3).
python_function('tests/test_pydantic_cross_check.py', 'test_contract_enum_narrower_than_literal_is_flagged', 1, 3, 4).
python_function('tests/test_pydantic_cross_check.py', 'test_output_contract_wider_than_literal_is_warning_not_error', 1, 3, 5).
python_function('tests/test_pydantic_cross_check.py', 'test_input_contract_wider_than_literal_is_error', 1, 3, 4).
python_function('tests/test_pydantic_cross_check.py', 'test_input_pydantic_wider_than_contract_is_ok', 1, 3, 3).
python_function('tests/test_pydantic_cross_check.py', 'test_missing_pydantic_field_is_silently_skipped', 1, 2, 3).
python_function('tests/test_pydantic_cross_check.py', 'test_contract_without_layers_python_is_skipped', 1, 2, 3).
python_function('tests/test_pydantic_cross_check.py', 'test_optional_literal_union_is_handled', 1, 2, 4).
python_function('tests/test_pydantic_cross_check.py', 'test_cross_check_contracts_returns_pairs', 1, 6, 4).
python_function('tests/test_refactor.py', 'synthetic_project', 1, 1, 2).
python_function('tests/test_refactor.py', 'test_frontend_scanner_extracts_ids_and_api_calls', 1, 6, 2).
python_function('tests/test_refactor.py', 'test_backend_scanner_extracts_models', 1, 5, 2).
python_function('tests/test_refactor.py', 'test_frontend_find_pages_for_route', 1, 3, 3).
python_function('tests/test_refactor.py', 'test_refactor_pipeline_seeded_writes_modules', 2, 12, 5).
python_function('tests/test_refactor.py', 'test_louvain_like_groups_connected_nodes', 0, 6, 6).
python_function('tests/test_refactor.py', 'test_seeded_clusterer_assigns_by_best_score', 0, 6, 7).
python_function('tests/test_resolve.py', '_write', 2, 1, 3).
python_function('tests/test_resolve.py', '_scan', 1, 1, 2).
python_function('tests/test_resolve.py', 'project', 1, 1, 4).
python_function('tests/test_resolve.py', 'test_no_changes_when_manifests_match', 1, 3, 3).
python_function('tests/test_resolve.py', 'test_added_optional_field_is_non_breaking', 1, 6, 4).
python_function('tests/test_resolve.py', 'test_added_required_field_is_breaking', 1, 5, 4).
python_function('tests/test_resolve.py', 'test_removed_field_and_type_change_are_breaking', 1, 13, 4).
python_function('tests/test_resolve.py', 'test_rename_detection', 1, 7, 4).
python_function('tests/test_resolve.py', 'test_emits_change_is_metadata_only', 1, 5, 4).
python_function('tests/test_resolve.py', 'test_apply_resolution_rewrites_manifests', 1, 3, 4).
python_function('tests/test_resolve.py', 'test_resolution_json', 1, 4, 7).
python_function('tests/test_resolve.py', 'test_cli_resolve_strict_exits_nonzero_on_breaking', 2, 3, 4).
python_function('tests/test_resolve.py', 'test_cli_resolve_apply_fast_forwards', 2, 5, 4).
python_function('tests/test_resolve.py', 'test_cli_resolve_json_flag', 2, 4, 5).
python_function('tests/test_scan.py', '_write', 2, 1, 3).
python_function('tests/test_scan.py', 'customer_project', 1, 1, 2).
python_function('tests/test_scan.py', 'test_scan_detects_decorator_based', 1, 13, 4).
python_function('tests/test_scan.py', 'test_scan_detects_heuristics_in_device_context', 1, 9, 3).
python_function('tests/test_scan.py', 'test_scan_skips_excluded_paths', 1, 2, 3).
python_function('tests/test_scan.py', 'test_scan_assigns_contexts_by_longest_match', 1, 4, 3).
python_function('tests/test_scan.py', 'test_scan_reports_syntax_error', 1, 4, 5).
python_function('tests/test_scan.py', 'test_incremental_scan_reuses_cache', 1, 7, 4).
python_function('tests/test_scan.py', 'test_incremental_scan_invalidates_on_change', 1, 5, 6).
python_function('tests/test_scan.py', 'test_cache_prunes_deleted_files', 1, 2, 5).
python_function('tests/test_scan.py', 'test_render_json_roundtrip', 1, 4, 4).
python_function('tests/test_scan.py', 'test_render_html_contains_summary', 1, 4, 3).
python_function('tests/test_scan.py', 'test_cli_scan_text_output', 2, 4, 3).
python_function('tests/test_scan.py', 'test_cli_scan_json_roundtrip', 3, 7, 6).
python_function('tests/test_scan.py', 'test_cli_scan_strict_heuristics_fails', 1, 2, 2).
python_function('tests/test_services.py', '_write', 2, 1, 3).
python_function('tests/test_services.py', 'project_with_manifests', 1, 1, 5).
python_function('tests/test_services.py', 'test_generate_services_writes_package_per_context', 1, 10, 2).
python_function('tests/test_services.py', 'test_generate_services_rejects_unknown_bus', 1, 1, 2).
python_function('tests/test_services.py', 'test_generated_python_files_are_syntactically_valid', 1, 2, 4).
python_function('tests/test_services.py', 'test_generated_server_has_servicers_and_methods', 1, 6, 2).
python_function('tests/test_services.py', 'test_generated_worker_respects_grpc_port', 1, 3, 2).
python_function('tests/test_services.py', 'test_requirements_match_bus', 1, 4, 2).
python_function('tests/test_services.py', 'test_publisher_module_is_importable_in_memory_mode', 2, 3, 7).
python_function('tests/test_services.py', 'test_compose_has_bus_and_services', 1, 9, 4).
python_function('tests/test_services.py', 'test_compose_redis_bus', 1, 4, 4).
python_function('tests/test_services.py', 'test_compose_memory_bus_has_no_broker', 1, 3, 5).
python_function('tests/test_services.py', 'test_generate_services_copies_pb2_when_available', 1, 5, 8).
python_function('tests/test_services.py', 'test_cli_gen_services_defaults_bus_from_config', 2, 4, 5).
python_function('tests/test_services.py', 'test_cli_gen_services_requires_manifests', 2, 3, 5).
python_function('tests/test_services.py', 'test_cli_gen_services_bus_override', 2, 4, 4).
python_function('tests/test_tools.py', 'test_run_doctor_basic', 0, 9, 1).
python_function('tests/test_tools.py', 'test_init_project_writes_scaffold', 1, 11, 4).
python_function('tests/test_tools.py', 'test_init_project_respects_no_gitignore', 1, 2, 2).
python_function('tests/test_tools.py', 'test_init_project_appends_to_existing_gitignore', 1, 5, 4).
python_function('tests/test_tools.py', 'test_cli_doctor', 1, 3, 2).
python_function('tests/test_tools.py', 'test_cli_init', 2, 4, 4).
python_function('tests/test_watch.py', '_write', 2, 1, 3).
python_function('tests/test_watch.py', 'project', 1, 1, 2).
python_function('tests/test_watch.py', 'test_rebuild_once_runs_scan_and_manifests', 1, 4, 3).
python_function('tests/test_watch.py', 'test_engine_first_poll_returns_none', 1, 2, 3).
python_function('tests/test_watch.py', 'test_engine_detects_modifications', 1, 5, 6).
python_function('tests/test_watch.py', 'test_engine_detects_new_and_deleted_files', 1, 5, 6).
python_function('tests/test_watch.py', 'test_engine_ignores_state_dir_writes', 1, 2, 5).
python_function('tests/test_watch.py', 'test_engine_run_stops_after_first_rebuild', 1, 2, 7).
python_function('tests/test_watch.py', 'test_cli_watch_once', 2, 4, 4).

% ── Python Classes ───────────────────────────────────────
python_class('examples/src/models.py', 'Device').
python_class('examples/src/models.py', 'Reading').
python_class('swop/config.py', 'SwopConfigError').
python_class('swop/config.py', 'BoundedContextConfig').
python_class('swop/config.py', 'BusConfig').
python_class('swop/config.py', 'ReadModelConfig').
python_class('swop/config.py', 'SwopConfig').
python_method('SwopConfig', 'project_root', 0, 2, 1).
python_method('SwopConfig', 'state_path', 0, 1, 0).
python_method('SwopConfig', 'context', 1, 3, 0).
python_method('SwopConfig', 'iter_source_roots', 0, 2, 1).
python_class('swop/contracts/adapter.py', 'ContractDetectionAdapter').
python_method('ContractDetectionAdapter', '__init__', 2, 1, 1).
python_method('ContractDetectionAdapter', 'from_directory', 3, 2, 2).
python_method('ContractDetectionAdapter', 'by_kind', 1, 3, 0).
python_method('ContractDetectionAdapter', 'by_context', 1, 3, 0).
python_method('ContractDetectionAdapter', 'contexts', 0, 2, 1).
python_method('ContractDetectionAdapter', 'summary', 0, 2, 1).
python_class('swop/contracts/reader.py', 'ContractValidationError').
python_class('swop/core.py', 'SwopRuntime').
python_method('SwopRuntime', '__init__', 3, 3, 8).
python_method('SwopRuntime', 'add_model', 3, 2, 3).
python_method('SwopRuntime', 'add_service', 2, 2, 2).
python_method('SwopRuntime', 'add_ui_binding', 2, 1, 3).
python_method('SwopRuntime', 'introspect', 0, 1, 2).
python_method('SwopRuntime', 'run_sync', 0, 1, 7).
python_method('SwopRuntime', 'state_yaml', 0, 2, 2).
python_method('SwopRuntime', 'docker_compose', 0, 1, 1).
python_class('swop/cqrs/registry.py', 'CqrsRecord').
python_class('swop/cqrs/registry.py', 'CqrsRegistry').
python_method('CqrsRegistry', '__init__', 0, 1, 1).
python_method('CqrsRegistry', 'register', 1, 1, 0).
python_method('CqrsRegistry', 'clear', 0, 1, 1).
python_method('CqrsRegistry', 'all', 0, 1, 2).
python_method('CqrsRegistry', 'of_kind', 1, 3, 1).
python_method('CqrsRegistry', 'by_context', 1, 3, 1).
python_method('CqrsRegistry', 'contexts', 0, 2, 2).
python_method('CqrsRegistry', 'summary', 0, 2, 2).
python_method('CqrsRegistry', '__len__', 0, 1, 1).
python_method('CqrsRegistry', '__iter__', 0, 1, 2).
python_class('swop/export/docker.py', 'DockerExporter').
python_method('DockerExporter', 'to_dict', 1, 3, 4).
python_method('DockerExporter', 'export_yaml', 1, 1, 2).
python_class('swop/export/yaml.py', 'StateExporter').
python_method('StateExporter', 'to_dict', 2, 5, 5).
python_method('StateExporter', 'export_yaml', 2, 1, 2).
python_class('swop/graph.py', 'ModelField').
python_class('swop/graph.py', 'DataModel').
python_class('swop/graph.py', 'UIBinding').
python_class('swop/graph.py', 'Service').
python_class('swop/graph.py', 'GraphVersion').
python_class('swop/graph.py', 'ProjectGraph').
python_class('swop/introspect/backend.py', 'BackendIntrospector').
python_method('BackendIntrospector', '__init__', 2, 3, 0).
python_method('BackendIntrospector', 'introspect', 0, 1, 2).
python_method('BackendIntrospector', 'register_model', 2, 1, 1).
python_method('BackendIntrospector', 'register_route', 1, 2, 1).
python_class('swop/introspect/frontend.py', 'FrontendIntrospector').
python_method('FrontendIntrospector', 'introspect', 1, 2, 1).
python_method('FrontendIntrospector', 'from_html', 1, 4, 6).
python_class('swop/manifests/generator.py', 'ManifestFile').
python_class('swop/manifests/generator.py', 'ManifestGenerationResult').
python_method('ManifestGenerationResult', 'total_entries', 0, 2, 1).
python_method('ManifestGenerationResult', 'by_context', 0, 2, 2).
python_method('ManifestGenerationResult', 'format', 0, 3, 3).
python_class('swop/markpact/doql_bridge.py', 'MarkpactValidationError').
python_method('MarkpactValidationError', '__init__', 2, 1, 2).
python_class('swop/markpact/doql_bridge.py', 'DoqlBridge').
python_method('DoqlBridge', '__init__', 0, 1, 1).
python_method('DoqlBridge', '_try_import_doql', 0, 2, 0).
python_method('DoqlBridge', 'from_blocks', 1, 13, 7).
python_method('DoqlBridge', '_parse_block', 1, 5, 4).
python_method('DoqlBridge', '_merge_fragment', 2, 9, 7).
python_method('DoqlBridge', '_build_spec', 1, 5, 2).
python_method('DoqlBridge', '_load_entities', 2, 4, 5).
python_method('DoqlBridge', '_load_databases', 2, 3, 4).
python_method('DoqlBridge', '_load_interfaces', 2, 3, 4).
python_method('DoqlBridge', '_load_workflows', 2, 4, 5).
python_method('DoqlBridge', '_load_roles', 2, 3, 4).
python_method('DoqlBridge', '_load_integrations', 2, 3, 4).
python_method('DoqlBridge', '_load_webhooks', 2, 3, 4).
python_method('DoqlBridge', '_load_api_clients', 2, 3, 4).
python_method('DoqlBridge', '_load_data_sources', 2, 3, 4).
python_method('DoqlBridge', '_load_templates', 2, 3, 4).
python_method('DoqlBridge', '_load_documents', 2, 3, 4).
python_method('DoqlBridge', '_load_reports', 2, 3, 4).
python_method('DoqlBridge', '_load_environments', 2, 3, 4).
python_method('DoqlBridge', '_load_infrastructures', 2, 3, 4).
python_method('DoqlBridge', '_load_ingresses', 2, 3, 4).
python_method('DoqlBridge', '_load_ci_configs', 2, 3, 4).
python_method('DoqlBridge', '_load_deploy', 2, 2, 3).
python_method('DoqlBridge', '_build_minimal_spec', 1, 1, 19).
python_method('DoqlBridge', 'from_file', 1, 1, 3).
python_method('DoqlBridge', 'from_files', 1, 2, 4).
python_method('DoqlBridge', 'from_text', 1, 1, 3).
python_class('swop/markpact/parser.py', 'ManifestBlock').
python_method('ManifestBlock', 'get_meta_value', 1, 2, 2).
python_method('ManifestBlock', 'as_yaml', 0, 2, 1).
python_method('ManifestBlock', 'as_json', 0, 1, 1).
python_class('swop/markpact/parser.py', 'ManifestParser').
python_method('ManifestParser', '__init__', 1, 2, 1).
python_method('ManifestParser', 'parse_file', 1, 1, 3).
python_method('ManifestParser', 'parse', 1, 11, 15).
python_method('ManifestParser', 'parse_by_kind', 2, 3, 1).
python_method('ManifestParser', 'parse_doql_blocks', 1, 1, 1).
python_method('ManifestParser', 'parse_graph_blocks', 1, 1, 1).
python_method('ManifestParser', 'parse_file_blocks', 1, 1, 1).
python_method('ManifestParser', 'parse_config_blocks', 1, 1, 1).
python_class('swop/markpact/spec_models.py', 'MinimalEntityField').
python_class('swop/markpact/spec_models.py', 'MinimalEntity').
python_class('swop/markpact/spec_models.py', 'MinimalInterface').
python_class('swop/markpact/spec_models.py', 'MinimalDatabase').
python_class('swop/markpact/spec_models.py', 'MinimalDeploy').
python_class('swop/markpact/spec_models.py', 'MinimalWorkflowStep').
python_class('swop/markpact/spec_models.py', 'MinimalWorkflow').
python_class('swop/markpact/spec_models.py', 'MinimalRole').
python_class('swop/markpact/spec_models.py', 'MinimalIntegration').
python_class('swop/markpact/spec_models.py', 'MinimalWebhook').
python_class('swop/markpact/spec_models.py', 'MinimalApiClient').
python_class('swop/markpact/spec_models.py', 'MinimalEnvironment').
python_class('swop/markpact/spec_models.py', 'MinimalInfrastructure').
python_class('swop/markpact/spec_models.py', 'MinimalIngress').
python_class('swop/markpact/spec_models.py', 'MinimalCiConfig').
python_class('swop/markpact/spec_models.py', 'MinimalDataSource').
python_class('swop/markpact/spec_models.py', 'MinimalTemplate').
python_class('swop/markpact/spec_models.py', 'MinimalDocument').
python_class('swop/markpact/spec_models.py', 'MinimalReport').
python_class('swop/markpact/spec_models.py', 'MinimalDoqlSpec').
python_class('swop/markpact/sync_engine.py', 'SyncStatus').
python_class('swop/markpact/sync_engine.py', 'ManifestSyncEngine').
python_method('ManifestSyncEngine', '__init__', 1, 1, 2).
python_method('ManifestSyncEngine', 'check', 1, 7, 9).
python_method('ManifestSyncEngine', 'diff', 1, 11, 10).
python_method('ManifestSyncEngine', 'sync_to_disk', 1, 5, 5).
python_method('ManifestSyncEngine', 'sync_from_disk', 1, 5, 4).
python_method('ManifestSyncEngine', 'update_manifest', 1, 3, 10).
python_class('swop/proto/compiler.py', 'CompilationResult').
python_method('CompilationResult', 'format', 0, 6, 4).
python_class('swop/proto/generator.py', 'ProtoFile').
python_method('ProtoFile', 'total_rpcs', 0, 1, 0).
python_class('swop/proto/generator.py', 'ProtoGenerationResult').
python_method('ProtoGenerationResult', 'format', 0, 6, 3).
python_class('swop/proto/generator.py', '_ProtoType').
python_class('swop/reconcile.py', 'DriftError').
python_class('swop/reconcile.py', 'Drift').
python_method('Drift', 'exists', 0, 4, 1).
python_class('swop/reconcile.py', 'DriftDetector').
python_method('DriftDetector', 'compute', 2, 7, 6).
python_class('swop/reconcile.py', 'ResyncEngine').
python_method('ResyncEngine', '__init__', 1, 1, 1).
python_method('ResyncEngine', 'reconcile', 2, 4, 5).
python_method('ResyncEngine', '_has_critical', 1, 2, 1).
python_method('ResyncEngine', '_auto_heal', 2, 4, 2).
python_method('ResyncEngine', '_log_drift', 1, 1, 1).
python_class('swop/refactor/clustering.py', 'Cluster').
python_class('swop/refactor/clustering.py', 'LouvainLike').
python_method('LouvainLike', '__init__', 2, 1, 1).
python_method('LouvainLike', 'run', 0, 12, 3).
python_method('LouvainLike', '_step', 0, 8, 3).
python_method('LouvainLike', '_gain_for', 3, 5, 1).
python_method('LouvainLike', '_collect', 0, 3, 6).
python_class('swop/refactor/clustering.py', 'SeededClusterer').
python_method('SeededClusterer', '__init__', 2, 1, 0).
python_method('SeededClusterer', 'run', 1, 12, 7).
python_method('SeededClusterer', '_bfs', 1, 7, 6).
python_class('swop/refactor/compose_builder.py', 'ComposeBuilder').
python_method('ComposeBuilder', '__init__', 2, 1, 1).
python_method('ComposeBuilder', 'write', 1, 5, 8).
python_method('ComposeBuilder', '_write_module_compose', 3, 2, 5).
python_method('ComposeBuilder', '_service_name', 1, 1, 1).
python_method('ComposeBuilder', '_write_dockerfile', 1, 3, 4).
python_class('swop/refactor/graph.py', 'Node').
python_class('swop/refactor/graph.py', 'Edge').
python_class('swop/refactor/graph.py', 'RefactorGraph').
python_method('RefactorGraph', '__init__', 0, 1, 0).
python_method('RefactorGraph', 'add_node', 2, 2, 3).
python_method('RefactorGraph', 'add_edge', 4, 3, 5).
python_method('RefactorGraph', 'edges', 0, 1, 2).
python_method('RefactorGraph', 'neighbors', 1, 4, 2).
python_method('RefactorGraph', 'nodes_of_type', 1, 3, 1).
python_method('RefactorGraph', 'as_dict', 0, 3, 2).
python_method('RefactorGraph', 'from_iterables', 3, 3, 3).
python_class('swop/refactor/module_builder.py', 'ModuleSpec').
python_class('swop/refactor/module_builder.py', 'ModuleWriteResult').
python_class('swop/refactor/module_builder.py', 'ModuleBuilder').
python_method('ModuleBuilder', '__init__', 1, 1, 1).
python_method('ModuleBuilder', 'write', 1, 1, 8).
python_method('ModuleBuilder', '_write_ui', 3, 4, 5).
python_method('ModuleBuilder', '_write_api', 3, 3, 6).
python_method('ModuleBuilder', '_write_models', 3, 6, 7).
python_method('ModuleBuilder', '_write_db', 3, 2, 6).
python_method('ModuleBuilder', '_write_api_server', 3, 1, 3).
python_method('ModuleBuilder', '_write_manifest', 3, 3, 5).
python_class('swop/refactor/pipeline.py', 'RefactorResult').
python_method('RefactorResult', 'summary', 0, 5, 2).
python_class('swop/refactor/pipeline.py', 'RefactorPipeline').
python_method('RefactorPipeline', '__init__', 7, 4, 2).
python_method('RefactorPipeline', 'run', 0, 10, 18).
python_method('RefactorPipeline', '_build_graph', 3, 8, 6).
python_method('RefactorPipeline', '_link_models_to_ui', 1, 8, 4).
python_method('RefactorPipeline', '_link_models_to_tables', 2, 4, 1).
python_method('RefactorPipeline', '_seed_nodes', 2, 5, 4).
python_method('RefactorPipeline', '_seed_cluster_name', 1, 4, 3).
python_method('RefactorPipeline', '_cluster_to_spec', 6, 23, 7).
python_class('swop/refactor/scanner/backend.py', 'ModelSignals').
python_class('swop/refactor/scanner/backend.py', 'RouteSignals').
python_class('swop/refactor/scanner/backend.py', 'BackendSignals').
python_class('swop/refactor/scanner/backend.py', 'BackendScanner').
python_method('BackendScanner', '__init__', 4, 1, 2).
python_method('BackendScanner', '_iter_py', 1, 8, 7).
python_method('BackendScanner', 'scan', 0, 3, 5).
python_method('BackendScanner', '_extract_model_fields', 1, 11, 4).
python_method('BackendScanner', '_extract_models', 1, 5, 8).
python_method('BackendScanner', '_looks_like_model', 1, 5, 3).
python_method('BackendScanner', '_extract_routes', 1, 3, 6).
python_class('swop/refactor/scanner/db.py', 'DbSignals').
python_class('swop/refactor/scanner/db.py', 'DbScanner').
python_method('DbScanner', '__init__', 2, 1, 2).
python_method('DbScanner', 'scan', 0, 5, 6).
python_method('DbScanner', '_scan_file', 1, 4, 5).
python_class('swop/refactor/scanner/frontend.py', 'PageSignals').
python_class('swop/refactor/scanner/frontend.py', 'FrontendScanner').
python_method('FrontendScanner', '__init__', 3, 1, 2).
python_method('FrontendScanner', '_pages_root', 0, 2, 1).
python_method('FrontendScanner', 'iter_pages', 0, 5, 5).
python_method('FrontendScanner', 'scan', 0, 2, 2).
python_method('FrontendScanner', 'scan_file', 1, 5, 7).
python_method('FrontendScanner', 'find_pages_for_route', 1, 10, 9).
python_method('FrontendScanner', '_route_token', 1, 3, 4).
python_method('FrontendScanner', '_slug_for', 1, 3, 2).
python_class('swop/registry/generator.py', 'RegistryGenerationResult').
python_method('RegistryGenerationResult', 'format', 0, 1, 0).
python_class('swop/registry/loader.py', 'Contract').
python_class('swop/registry/pydantic_cross_check.py', 'CrossCheckResult').
python_method('CrossCheckResult', 'format', 0, 4, 2).
python_class('swop/registry/validator.py', 'ValidationResult').
python_method('ValidationResult', 'format', 0, 2, 1).
python_class('swop/resolve/resolver.py', 'ChangeKind').
python_class('swop/resolve/resolver.py', 'Change').
python_method('Change', 'format', 0, 6, 0).
python_class('swop/resolve/resolver.py', 'ResolutionReport').
python_method('ResolutionReport', 'breaking', 0, 3, 0).
python_method('ResolutionReport', 'non_breaking', 0, 3, 0).
python_method('ResolutionReport', 'counts', 0, 2, 2).
python_method('ResolutionReport', 'to_json', 0, 3, 4).
python_method('ResolutionReport', 'format', 0, 6, 5).
python_class('swop/scan/cache.py', 'CacheEntry').
python_class('swop/scan/cache.py', 'FingerprintCache').
python_method('FingerprintCache', '__init__', 1, 1, 1).
python_method('FingerprintCache', 'load', 0, 7, 7).
python_method('FingerprintCache', 'save', 0, 3, 5).
python_method('FingerprintCache', 'fingerprint', 1, 1, 3).
python_method('FingerprintCache', 'get', 2, 3, 3).
python_method('FingerprintCache', 'put', 3, 1, 3).
python_method('FingerprintCache', 'drop', 1, 1, 2).
python_method('FingerprintCache', 'prune', 1, 3, 5).
python_method('FingerprintCache', '__len__', 0, 1, 2).
python_method('FingerprintCache', '__contains__', 1, 1, 1).
python_class('swop/scan/report.py', 'FieldDef').
python_method('FieldDef', 'to_dict', 0, 3, 0).
python_class('swop/scan/report.py', 'Detection').
python_method('Detection', 'to_dict', 0, 3, 3).
python_method('Detection', 'from_dict', 1, 7, 8).
python_class('swop/scan/report.py', 'ContextSummary').
python_method('ContextSummary', 'add', 1, 1, 0).
python_method('ContextSummary', 'total', 0, 1, 0).
python_class('swop/scan/report.py', 'ScanReport').
python_method('ScanReport', 'add', 1, 1, 4).
python_method('ScanReport', 'kinds', 0, 2, 1).
python_method('ScanReport', 'via', 0, 2, 1).
python_method('ScanReport', 'of_kind', 1, 3, 0).
python_method('ScanReport', 'of_context', 1, 3, 0).
python_method('ScanReport', 'to_dict', 0, 3, 8).
python_method('ScanReport', 'format_text', 0, 6, 7).
python_class('swop/services/generator.py', 'ServiceFile').
python_class('swop/services/generator.py', 'ServiceGenerationResult').
python_method('ServiceGenerationResult', 'format', 0, 9, 6).
python_class('swop/sync.py', 'SyncEngine').
python_method('SyncEngine', 'frontend_to_graph', 1, 2, 1).
python_method('SyncEngine', 'merge_frontend', 2, 4, 2).
python_method('SyncEngine', 'merge_backend', 2, 7, 6).
python_class('swop/tools/doctor.py', 'DoctorCheck').
python_method('DoctorCheck', 'ok', 0, 1, 0).
python_method('DoctorCheck', 'format', 0, 4, 1).
python_class('swop/tools/doctor.py', 'DoctorReport').
python_method('DoctorReport', 'failed', 0, 3, 0).
python_method('DoctorReport', 'warnings', 0, 3, 0).
python_method('DoctorReport', 'ok', 0, 1, 0).
python_method('DoctorReport', 'format', 0, 4, 5).
python_class('swop/tools/doctor_deep.py', 'DeepIssue').
python_method('DeepIssue', 'format', 0, 4, 1).
python_class('swop/tools/doctor_deep.py', 'DeepCheck').
python_method('DeepCheck', 'ok', 0, 1, 0).
python_method('DeepCheck', 'mark', 1, 2, 0).
python_method('DeepCheck', 'format', 0, 4, 5).
python_class('swop/tools/doctor_deep.py', 'DeepReport').
python_method('DeepReport', 'failed', 0, 3, 0).
python_method('DeepReport', 'warnings', 0, 3, 0).
python_method('DeepReport', 'ok', 0, 1, 0).
python_method('DeepReport', 'format', 0, 4, 5).
python_class('swop/tools/hook.py', 'HookResult').
python_method('HookResult', 'format', 0, 3, 2).
python_class('swop/tools/init.py', 'InitResult').
python_method('InitResult', 'format', 0, 5, 2).
python_class('swop/versioning.py', 'Versioning').
python_method('Versioning', 'commit', 2, 1, 4).
python_class('swop/watch/engine.py', 'WatchRebuild').
python_method('WatchRebuild', 'format', 0, 2, 3).
python_class('swop/watch/engine.py', 'WatchEngine').
python_method('WatchEngine', 'snapshot', 0, 9, 7).
python_method('WatchEngine', '_maybe_add', 2, 5, 3).
python_method('WatchEngine', 'poll_once', 0, 5, 6).
python_method('WatchEngine', 'run', 0, 9, 5).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', 'sk-or-v1-...', 'OpenRouter API Key (required for real cost calculation)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Default AI model for cost analysis').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('api', '').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
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

## Intent

Bi-directional runtime reconciler and drift-aware state graph for full-stack systems
