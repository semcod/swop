# swop

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `swop`
- **version**: `0.2.6`
- **python_requires**: `>=3.8`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, app.doql.less, goal.yaml, .env.example, project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: swop;
  version: 0.2.6;
}

dependencies {
  runtime: pyyaml>=6.0;
  dev: "pytest>=7.0, pytest-cov>=4.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
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

## Dependencies

### Runtime

```text markpact:deps python
pyyaml>=6.0
```

### Development

```text markpact:deps python scope=dev
pytest>=7.0
pytest-cov>=4.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Call Graph

*174 nodes · 180 edges · 26 modules · CC̄=1.5*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_build_parser` *(in swop.cli)* | 1 | 1 | 132 | **133** |
| `print` *(in README)* | 0 | 78 | 0 | **78** |
| `generate_registry_md` *(in swop.registry.generator)* | 32 ⚠ | 1 | 65 | **66** |
| `render_proto_for_context` *(in swop.proto.generator)* | 12 ⚠ | 1 | 43 | **44** |
| `_diff_fields` *(in swop.resolve.resolver)* | 11 ⚠ | 1 | 43 | **44** |
| `_map_python_type` *(in swop.proto.generator)* | 15 ⚠ | 3 | 25 | **28** |
| `_check_proto_vs_python` *(in swop.tools.doctor_deep)* | 15 ⚠ | 1 | 25 | **26** |
| `_from_dict` *(in swop.config)* | 8 | 1 | 25 | **26** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/inspect
# nodes: 174 | edges: 180 | modules: 26
# CC̄=1.5

HUBS[20]:
  swop.cli._build_parser
    CC=1  in:1  out:132  total:133
  README.print
    CC=0  in:78  out:0  total:78
  swop.registry.generator.generate_registry_md
    CC=32  in:1  out:65  total:66
  swop.proto.generator.render_proto_for_context
    CC=12  in:1  out:43  total:44
  swop.resolve.resolver._diff_fields
    CC=11  in:1  out:43  total:44
  swop.proto.generator._map_python_type
    CC=15  in:3  out:25  total:28
  swop.tools.doctor_deep._check_proto_vs_python
    CC=15  in:1  out:25  total:26
  swop.config._from_dict
    CC=8  in:1  out:25  total:26
  swop.scan.render.render_html
    CC=8  in:1  out:25  total:26
  swop.tools.doctor_deep._check_manifests_vs_proto
    CC=15  in:1  out:24  total:25
  swop.proto.compiler.compile_proto_typescript
    CC=10  in:0  out:23  total:23
  swop.commands._generate_build_graph
    CC=14  in:1  out:22  total:23
  swop.tools.doctor_deep._check_manifests_vs_services
    CC=15  in:1  out:22  total:23
  swop.resolve.resolver._index_from_manifests
    CC=15  in:1  out:21  total:22
  swop.services.generator._write_context_package
    CC=7  in:1  out:20  total:21
  swop.scan.scanner._scan_file
    CC=13  in:1  out:20  total:21
  swop.tools.hook._git_dir
    CC=13  in:1  out:20  total:21
  swop.proto.compiler.compile_proto_python
    CC=8  in:0  out:21  total:21
  swop.commands._cmd_scan
    CC=14  in:0  out:20  total:20
  swop.proto.generator.generate_proto_from_manifests
    CC=8  in:0  out:20  total:20

MODULES:
  README  [1 funcs]
    print  CC=0  out:0
  project.map.toon  [20 funcs]
    _diff_snapshots  CC=0  out:0
    _hash  CC=0  out:0
    _tokenize  CC=0  out:0
    apply_resolution  CC=0  out:0
    build_project_graph  CC=0  out:0
    compile_proto_python  CC=0  out:0
    compile_proto_typescript  CC=0  out:0
    generate_manifests  CC=0  out:0
    generate_proto_from_manifests  CC=0  out:0
    hook_status  CC=0  out:0
  swop.cli  [2 funcs]
    _build_parser  CC=1  out:132
    main  CC=1  out:3
  swop.commands  [26 funcs]
    _build_runtime  CC=1  out:4
    _cmd_diff  CC=2  out:3
    _cmd_doctor  CC=7  out:15
    _cmd_export  CC=2  out:4
    _cmd_gen_grpc_python  CC=7  out:11
    _cmd_gen_grpc_ts  CC=7  out:11
    _cmd_gen_manifests  CC=8  out:11
    _cmd_gen_proto  CC=7  out:13
    _cmd_gen_registry  CC=8  out:17
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
  swop.core  [1 funcs]
    run_sync  CC=1  out:8
  swop.cqrs.decorators  [4 funcs]
    _collect_source  CC=3  out:2
    _make_decorator  CC=1  out:11
    _normalize_emits  CC=4  out:5
    handler  CC=7  out:12
  swop.manifests.generator  [10 funcs]
    _camel_to_dot  CC=5  out:9
    _handler_index  CC=4  out:1
    _render_bus  CC=6  out:3
    _render_entry  CC=10  out:7
    _render_field  CC=3  out:0
    _render_handler  CC=2  out:0
    _render_manifest  CC=2  out:3
    _render_source  CC=2  out:0
    _safe_dirname  CC=2  out:3
    generate_manifests  CC=10  out:11
  swop.markpact.sync_engine  [1 funcs]
    check  CC=7  out:11
  swop.proto.compiler  [4 funcs]
    _iter_proto_files  CC=1  out:3
    _run  CC=2  out:3
    compile_proto_python  CC=8  out:21
    compile_proto_typescript  CC=10  out:23
  swop.proto.generator  [7 funcs]
    _iter_contexts  CC=6  out:7
    _load_manifest  CC=4  out:4
    _map_python_type  CC=15  out:25
    _render_message  CC=8  out:10
    _safe_ident  CC=3  out:3
    generate_proto_from_manifests  CC=8  out:20
    render_proto_for_context  CC=12  out:43
  swop.reconcile  [2 funcs]
    _auto_heal  CC=4  out:2
    _log_drift  CC=1  out:6
  swop.refactor.pipeline  [1 funcs]
    _link_models_to_ui  CC=8  out:7
  swop.registry.generator  [3 funcs]
    generate_registry_json  CC=7  out:17
    generate_registry_md  CC=32  out:65
    write_registry  CC=2  out:14
  swop.registry.validator  [4 funcs]
    _check_keys  CC=3  out:1
    _check_kind  CC=2  out:3
    _check_layer_paths  CC=7  out:7
    validate_contract  CC=5  out:11
  swop.resolve.resolver  [9 funcs]
    _diff_entry  CC=3  out:4
    _diff_fields  CC=11  out:43
    _diff_metadata  CC=9  out:16
    _handler_shape  CC=3  out:0
    _handler_sig  CC=8  out:4
    _index_from_detections  CC=10  out:6
    _index_from_manifests  CC=15  out:21
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
  swop.tools.doctor  [3 funcs]
    _check_binary  CC=4  out:5
    _first_version  CC=3  out:2
    _run_version  CC=5  out:3
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
  swop.versioning  [1 funcs]
    commit  CC=1  out:4
  swop.watch.engine  [3 funcs]
    poll_once  CC=5  out:7
    run  CC=9  out:5
    rebuild_once  CC=2  out:6

EDGES:
  swop.config._parse_context → swop.config._pop_known
  swop.config._parse_bus → swop.config._pop_known
  swop.config._parse_read_models → swop.config._pop_known
  swop.config.load_config → swop.config._from_dict
  swop.config.load_config → swop.config._expand_env
  swop.reconcile.ResyncEngine._auto_heal → README.print
  swop.reconcile.ResyncEngine._log_drift → README.print
  swop.versioning.Versioning.commit → README.print
  swop.core.SwopRuntime.run_sync → README.print
  swop.scan.render.write_report → swop.scan.render.render_json
  swop.scan.render.write_report → swop.scan.render.render_html
  swop.scan.scanner._scan_file → swop.scan.scanner._context_for_path
  swop.scan.scanner._scan_file → swop.scan.scanner._extract_detections
  swop.scan.scanner.scan_project → swop.scan.scanner._resolve_contexts
  swop.scan.scanner.scan_project → swop.scan.scanner._iter_python_files
  swop.scan.scanner.scan_project → project.map.toon.load_config
  swop.scan.scanner.scan_project → swop.scan.scanner._scan_file
  swop.scan.scanner._iter_python_files → swop.scan.scanner._matches_any
  swop.scan.scanner._extract_detections → swop.scan.scanner._module_name_from_path
  swop.scan.scanner._extract_detections → swop.scan.scanner._classify
  swop.scan.scanner._extract_detections → swop.scan.scanner._extract_fields
  swop.scan.scanner._extract_detections → swop.scan.scanner._handler_method_name
  swop.scan.scanner._classify_decorator → swop.scan.scanner._decorator_name
  swop.scan.scanner._classify_decorator → swop.scan.scanner._extract_decorator_emits
  swop.scan.scanner._classify_decorator → swop.scan.scanner._extract_handler_target
  swop.scan.scanner._classify_decorator → swop.scan.scanner._extract_decorator_context
  swop.scan.scanner._classify_heuristic → swop.scan.scanner._kind_by_suffix
  swop.scan.scanner._classify_heuristic → swop.scan.scanner._kind_by_base
  swop.scan.scanner._classify_heuristic → swop.scan.scanner._handler_target_from_method
  swop.scan.scanner._classify → swop.scan.scanner._classify_heuristic
  swop.scan.scanner._classify → swop.scan.scanner._decorator_name
  swop.scan.scanner._classify → swop.scan.scanner._base_name
  swop.scan.scanner._classify → swop.scan.scanner._classify_decorator
  swop.scan.scanner._extract_ann_field → swop.scan.scanner._unparse
  swop.scan.scanner._extract_ann_field → swop.scan.scanner._render_default
  swop.scan.scanner._extract_ann_field → swop.scan.scanner._annotation_is_optional
  swop.scan.scanner._extract_plain_field → swop.scan.scanner._render_default
  swop.scan.scanner._extract_fields → swop.scan.scanner._extract_ann_field
  swop.scan.scanner._extract_fields → swop.scan.scanner._extract_plain_field
  swop.scan.scanner._render_default → swop.scan.scanner._unparse
  swop.services.generator._write_context_package → swop.services.generator._safe_ident
  swop.services.generator._write_context_package → swop.services.generator._camel
  swop.services.generator._write_context_package → swop.services.generator._render_init
  swop.services.generator._write_context_package → swop.services.generator._render_worker
  swop.services.generator._write_context_package → swop.services.generator._render_server
  swop.services.generator._write_context_package → swop.services.generator._render_publisher
  swop.services.generator._write_context_package → swop.services.generator._render_requirements
  swop.services.generator._write_context_package → swop.services.generator._render_dockerfile
  swop.services.generator._render_compose → swop.services.generator._default_bus_url
  swop.tools.doctor._check_binary → swop.tools.doctor._run_version
```

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/inspect
# nodes: 174 | edges: 180 | modules: 26
# CC̄=1.5

HUBS[20]:
  swop.cli._build_parser
    CC=1  in:1  out:132  total:133
  README.print
    CC=0  in:78  out:0  total:78
  swop.registry.generator.generate_registry_md
    CC=32  in:1  out:65  total:66
  swop.proto.generator.render_proto_for_context
    CC=12  in:1  out:43  total:44
  swop.resolve.resolver._diff_fields
    CC=11  in:1  out:43  total:44
  swop.proto.generator._map_python_type
    CC=15  in:3  out:25  total:28
  swop.tools.doctor_deep._check_proto_vs_python
    CC=15  in:1  out:25  total:26
  swop.config._from_dict
    CC=8  in:1  out:25  total:26
  swop.scan.render.render_html
    CC=8  in:1  out:25  total:26
  swop.tools.doctor_deep._check_manifests_vs_proto
    CC=15  in:1  out:24  total:25
  swop.proto.compiler.compile_proto_typescript
    CC=10  in:0  out:23  total:23
  swop.commands._generate_build_graph
    CC=14  in:1  out:22  total:23
  swop.tools.doctor_deep._check_manifests_vs_services
    CC=15  in:1  out:22  total:23
  swop.resolve.resolver._index_from_manifests
    CC=15  in:1  out:21  total:22
  swop.services.generator._write_context_package
    CC=7  in:1  out:20  total:21
  swop.scan.scanner._scan_file
    CC=13  in:1  out:20  total:21
  swop.tools.hook._git_dir
    CC=13  in:1  out:20  total:21
  swop.proto.compiler.compile_proto_python
    CC=8  in:0  out:21  total:21
  swop.commands._cmd_scan
    CC=14  in:0  out:20  total:20
  swop.proto.generator.generate_proto_from_manifests
    CC=8  in:0  out:20  total:20

MODULES:
  README  [1 funcs]
    print  CC=0  out:0
  project.map.toon  [20 funcs]
    _diff_snapshots  CC=0  out:0
    _hash  CC=0  out:0
    _tokenize  CC=0  out:0
    apply_resolution  CC=0  out:0
    build_project_graph  CC=0  out:0
    compile_proto_python  CC=0  out:0
    compile_proto_typescript  CC=0  out:0
    generate_manifests  CC=0  out:0
    generate_proto_from_manifests  CC=0  out:0
    hook_status  CC=0  out:0
  swop.cli  [2 funcs]
    _build_parser  CC=1  out:132
    main  CC=1  out:3
  swop.commands  [26 funcs]
    _build_runtime  CC=1  out:4
    _cmd_diff  CC=2  out:3
    _cmd_doctor  CC=7  out:15
    _cmd_export  CC=2  out:4
    _cmd_gen_grpc_python  CC=7  out:11
    _cmd_gen_grpc_ts  CC=7  out:11
    _cmd_gen_manifests  CC=8  out:11
    _cmd_gen_proto  CC=7  out:13
    _cmd_gen_registry  CC=8  out:17
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
  swop.core  [1 funcs]
    run_sync  CC=1  out:8
  swop.cqrs.decorators  [4 funcs]
    _collect_source  CC=3  out:2
    _make_decorator  CC=1  out:11
    _normalize_emits  CC=4  out:5
    handler  CC=7  out:12
  swop.manifests.generator  [10 funcs]
    _camel_to_dot  CC=5  out:9
    _handler_index  CC=4  out:1
    _render_bus  CC=6  out:3
    _render_entry  CC=10  out:7
    _render_field  CC=3  out:0
    _render_handler  CC=2  out:0
    _render_manifest  CC=2  out:3
    _render_source  CC=2  out:0
    _safe_dirname  CC=2  out:3
    generate_manifests  CC=10  out:11
  swop.markpact.sync_engine  [1 funcs]
    check  CC=7  out:11
  swop.proto.compiler  [4 funcs]
    _iter_proto_files  CC=1  out:3
    _run  CC=2  out:3
    compile_proto_python  CC=8  out:21
    compile_proto_typescript  CC=10  out:23
  swop.proto.generator  [7 funcs]
    _iter_contexts  CC=6  out:7
    _load_manifest  CC=4  out:4
    _map_python_type  CC=15  out:25
    _render_message  CC=8  out:10
    _safe_ident  CC=3  out:3
    generate_proto_from_manifests  CC=8  out:20
    render_proto_for_context  CC=12  out:43
  swop.reconcile  [2 funcs]
    _auto_heal  CC=4  out:2
    _log_drift  CC=1  out:6
  swop.refactor.pipeline  [1 funcs]
    _link_models_to_ui  CC=8  out:7
  swop.registry.generator  [3 funcs]
    generate_registry_json  CC=7  out:17
    generate_registry_md  CC=32  out:65
    write_registry  CC=2  out:14
  swop.registry.validator  [4 funcs]
    _check_keys  CC=3  out:1
    _check_kind  CC=2  out:3
    _check_layer_paths  CC=7  out:7
    validate_contract  CC=5  out:11
  swop.resolve.resolver  [9 funcs]
    _diff_entry  CC=3  out:4
    _diff_fields  CC=11  out:43
    _diff_metadata  CC=9  out:16
    _handler_shape  CC=3  out:0
    _handler_sig  CC=8  out:4
    _index_from_detections  CC=10  out:6
    _index_from_manifests  CC=15  out:21
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
  swop.tools.doctor  [3 funcs]
    _check_binary  CC=4  out:5
    _first_version  CC=3  out:2
    _run_version  CC=5  out:3
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
  swop.versioning  [1 funcs]
    commit  CC=1  out:4
  swop.watch.engine  [3 funcs]
    poll_once  CC=5  out:7
    run  CC=9  out:5
    rebuild_once  CC=2  out:6

EDGES:
  swop.config._parse_context → swop.config._pop_known
  swop.config._parse_bus → swop.config._pop_known
  swop.config._parse_read_models → swop.config._pop_known
  swop.config.load_config → swop.config._from_dict
  swop.config.load_config → swop.config._expand_env
  swop.reconcile.ResyncEngine._auto_heal → README.print
  swop.reconcile.ResyncEngine._log_drift → README.print
  swop.versioning.Versioning.commit → README.print
  swop.core.SwopRuntime.run_sync → README.print
  swop.scan.render.write_report → swop.scan.render.render_json
  swop.scan.render.write_report → swop.scan.render.render_html
  swop.scan.scanner._scan_file → swop.scan.scanner._context_for_path
  swop.scan.scanner._scan_file → swop.scan.scanner._extract_detections
  swop.scan.scanner.scan_project → swop.scan.scanner._resolve_contexts
  swop.scan.scanner.scan_project → swop.scan.scanner._iter_python_files
  swop.scan.scanner.scan_project → project.map.toon.load_config
  swop.scan.scanner.scan_project → swop.scan.scanner._scan_file
  swop.scan.scanner._iter_python_files → swop.scan.scanner._matches_any
  swop.scan.scanner._extract_detections → swop.scan.scanner._module_name_from_path
  swop.scan.scanner._extract_detections → swop.scan.scanner._classify
  swop.scan.scanner._extract_detections → swop.scan.scanner._extract_fields
  swop.scan.scanner._extract_detections → swop.scan.scanner._handler_method_name
  swop.scan.scanner._classify_decorator → swop.scan.scanner._decorator_name
  swop.scan.scanner._classify_decorator → swop.scan.scanner._extract_decorator_emits
  swop.scan.scanner._classify_decorator → swop.scan.scanner._extract_handler_target
  swop.scan.scanner._classify_decorator → swop.scan.scanner._extract_decorator_context
  swop.scan.scanner._classify_heuristic → swop.scan.scanner._kind_by_suffix
  swop.scan.scanner._classify_heuristic → swop.scan.scanner._kind_by_base
  swop.scan.scanner._classify_heuristic → swop.scan.scanner._handler_target_from_method
  swop.scan.scanner._classify → swop.scan.scanner._classify_heuristic
  swop.scan.scanner._classify → swop.scan.scanner._decorator_name
  swop.scan.scanner._classify → swop.scan.scanner._base_name
  swop.scan.scanner._classify → swop.scan.scanner._classify_decorator
  swop.scan.scanner._extract_ann_field → swop.scan.scanner._unparse
  swop.scan.scanner._extract_ann_field → swop.scan.scanner._render_default
  swop.scan.scanner._extract_ann_field → swop.scan.scanner._annotation_is_optional
  swop.scan.scanner._extract_plain_field → swop.scan.scanner._render_default
  swop.scan.scanner._extract_fields → swop.scan.scanner._extract_ann_field
  swop.scan.scanner._extract_fields → swop.scan.scanner._extract_plain_field
  swop.scan.scanner._render_default → swop.scan.scanner._unparse
  swop.services.generator._write_context_package → swop.services.generator._safe_ident
  swop.services.generator._write_context_package → swop.services.generator._camel
  swop.services.generator._write_context_package → swop.services.generator._render_init
  swop.services.generator._write_context_package → swop.services.generator._render_worker
  swop.services.generator._write_context_package → swop.services.generator._render_server
  swop.services.generator._write_context_package → swop.services.generator._render_publisher
  swop.services.generator._write_context_package → swop.services.generator._render_requirements
  swop.services.generator._write_context_package → swop.services.generator._render_dockerfile
  swop.services.generator._render_compose → swop.services.generator._default_bus_url
  swop.tools.doctor._check_binary → swop.tools.doctor._run_version
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 83f 17871L | python:63,yaml:8,md:7,shell:2,json:1,toml:1,txt:1 | 2026-04-23
# CC̄=1.5 | critical:8/1079 | dups:0 | cycles:0

HEALTH[8]:
  🟡 CC    _check_manifests_vs_proto CC=15 (limit:15)
  🟡 CC    _check_proto_vs_python CC=15 (limit:15)
  🟡 CC    _check_manifests_vs_services CC=15 (limit:15)
  🟡 CC    _map_python_type CC=15 (limit:15)
  🟡 CC    _cluster_to_spec CC=23 (limit:15)
  🟡 CC    _index_from_manifests CC=15 (limit:15)
  🟡 CC    validate_contract CC=21 (limit:15)
  🟡 CC    generate_registry_md CC=32 (limit:15)

REFACTOR[1]:
  1. split 8 high-CC methods  (CC>15)

PIPELINES[217]:
  [1] Src [list_devices]: list_devices
      PURITY: 100% pure
  [2] Src [create_reading]: create_reading
      PURITY: 100% pure
  [3] Src [iter_source_roots]: iter_source_roots
      PURITY: 100% pure
  [4] Src [load_config]: load_config → _from_dict → _parse_context → _pop_known
      PURITY: 100% pure
  [5] Src [exists]: exists
      PURITY: 100% pure

LAYERS:
  swop/                           CC̄=4.5    ←in:0  →out:110  !! split
  │ !! generator                  686L  2C   17m  CC=11     ←0
  │ !! scanner                    595L  0C   27m  CC=13     ←0
  │ !! commands                   550L  0C   26m  CC=14     ←0
  │ !! cli                        517L  0C    2m  CC=1      ←0
  │ !! doql_bridge                506L  2C   28m  CC=13     ←0
  │ !! resolver                   456L  3C   15m  CC=15     ←0
  │ !! generator                  413L  3C   11m  CC=15     ←0
  │ !! doctor_deep                369L  3C   10m  CC=15     ←0
  │ !! pipeline                   284L  2C   10m  CC=23     ←0
  │ generator                  244L  2C   12m  CC=10     ←0
  │ hook                       220L  1C    8m  CC=13     ←0
  │ engine                     212L  2C    7m  CC=9      ←0
  │ spec_models                212L  20C    0m  CC=0.0    ←0
  │ config                     209L  5C    9m  CC=8      ←0
  │ report                     209L  4C   11m  CC=7      ←1
  │ compiler                   207L  1C    6m  CC=10     ←0
  │ sync_engine                201L  2C    7m  CC=11     ←0
  │ doctor                     193L  2C   10m  CC=7      ←0
  │ __init__                   168L  0C    0m  CC=0.0    ←0
  │ adapter                    162L  1C   12m  CC=6      ←0
  │ init                       160L  1C    3m  CC=14     ←0
  │ decorators                 158L  0C    4m  CC=7      ←0
  │ clustering                 158L  3C    8m  CC=12     ←0
  │ backend                    156L  4C    7m  CC=11     ←0
  │ !! reader                     154L  1C    4m  CC=21     ←2
  │ render                     141L  0C    3m  CC=8      ←0
  │ parser                     141L  2C   11m  CC=11     ←0
  │ frontend                   128L  2C    8m  CC=10     ←0
  │ reconcile                  111L  4C    7m  CC=7      ←0
  │ cache                      111L  2C   10m  CC=7      ←1
  │ core                       105L  1C    8m  CC=3      ←0
  │ registry                   105L  2C   12m  CC=3      ←0
  │ graph                      100L  3C    7m  CC=4      ←0
  │ !! generator                  100L  1C    6m  CC=32     ←1
  │ validator                   95L  1C    5m  CC=7      ←0
  │ db                          53L  2C    3m  CC=5      ←0
  │ bridge                      50L  0C    2m  CC=9      ←0
  │ graph                       49L  6C    0m  CC=0.0    ←0
  │ yaml                        48L  1C    2m  CC=5      ←0
  │ sync                        47L  1C    3m  CC=7      ←0
  │ __init__                    43L  0C    0m  CC=0.0    ←0
  │ frontend                    40L  1C    2m  CC=4      ←0
  │ loader                      39L  1C    1m  CC=8      ←0
  │ __init__                    37L  0C    0m  CC=0.0    ←0
  │ __init__                    36L  0C    0m  CC=0.0    ←0
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
  examples/                       CC̄=0.4    ←in:0  →out:0
  │ manifest.md                387L  2C    3m  CC=0.0    ←0
  │ models                      16L  2C    0m  CC=0.0    ←0
  │ api                         12L  0C    2m  CC=1      ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! SUMD.md                   1075L  0C  359m  CC=0.0    ←0
  │ !! SUMR.md                    886L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ README.md                  360L  2C    2m  CC=0.0    ←5
  │ CHANGELOG.md               236L  0C    0m  CC=0.0    ←0
  │ sumd.json                  102L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              76L  0C    0m  CC=0.0    ←0
  │ project.sh                  43L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                2556L  0C    0m  CC=0.0    ←0
  │ !! map.toon.yaml              686L  0C  359m  CC=0.0    ←8
  │ !! context.md                 589L  0C    0m  CC=0.0    ←0
  │ README.md                  339L  0C    0m  CC=0.0    ←0
  │ calls.toon.yaml            230L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         132L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml       84L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         78L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           51L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                            swop          README     project.map      swop.watch   swop.refactor  swop.contracts       swop.cqrs   swop.markpact      swop.tools   swop.registry    swop.resolve       swop.scan
            swop              ──              77              30                                               2                                                               1                                  !! fan-out
          README             ←77              ──                              ←1                                                                                                                                  hub
     project.map             ←30                              ──              ←4              ←4                              ←2              ←2              ←2                              ←1              ←1  hub
      swop.watch                               1               4              ──                                                                                                                                
   swop.refactor                                               4                              ──                                                                                                                
  swop.contracts              ←2                                                                              ──                                                                                                
       swop.cqrs                                               2                                                              ──                                                                                
   swop.markpact                                               2                                                                              ──                                                                
      swop.tools                                               2                                                                                              ──                                                
   swop.registry              ←1                                                                                                                                              ──                                
    swop.resolve                                               1                                                                                                                              ──                
       swop.scan                                               1                                                                                                                                              ──
  CYCLES: none
  HUB: README/ (fan-in=78)
  HUB: project.map/ (fan-in=46)
  SMELL: swop/ fan-out=110 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 6 groups | 65f 10026L | 2026-04-23

SUMMARY:
  files_scanned: 65
  total_lines:   10026
  dup_groups:    6
  dup_fragments: 12
  saved_lines:   72
  scan_ms:       4519

HOTSPOTS[7] (files with most duplication):
  swop/markpact/graph_builder.py  dup=54L  groups=1  frags=2  (0.5%)
  swop/config.py  dup=24L  groups=1  frags=2  (0.2%)
  swop/commands.py  dup=18L  groups=1  frags=2  (0.2%)
  swop/proto/generator.py  dup=15L  groups=2  frags=2  (0.1%)
  swop/services/generator.py  dup=11L  groups=2  frags=2  (0.1%)
  swop/tools/doctor.py  dup=10L  groups=1  frags=1  (0.1%)
  swop/tools/doctor_deep.py  dup=10L  groups=1  frags=1  (0.1%)

DUPLICATES[6] (ranked by impact):
  [efccf54f46437221]   STRU  _build_environments  L=27 N=2 saved=27 sim=1.00
      swop/markpact/graph_builder.py:261-287  (_build_environments)
      swop/markpact/graph_builder.py:290-316  (_build_infrastructures)
  [74019da8a30208a6]   STRU  _parse_bus  L=11 N=2 saved=11 sim=1.00
      swop/config.py:135-145  (_parse_bus)
      swop/config.py:148-160  (_parse_read_models)
  [f8704ba8fb938ef5]   STRU  format  L=10 N=2 saved=10 sim=1.00
      swop/tools/doctor.py:64-73  (format)
      swop/tools/doctor_deep.py:98-107  (format)
  [1615571e1d3ba70f]   STRU  _generate_update_from_disk  L=9 N=2 saved=9 sim=1.00
      swop/commands.py:486-494  (_generate_update_from_disk)
      swop/commands.py:497-505  (_generate_sync_files)
  [24a81bc8467ea7c4]   STRU  _render_query_response  L=8 N=2 saved=8 sim=1.00
      swop/proto/generator.py:388-395  (_render_query_response)
      swop/services/generator.py:232-235  (_render_init)
  [ad43bea74422d1bd]   STRU  _safe_ident  L=7 N=2 saved=7 sim=1.00
      swop/proto/generator.py:407-413  (_safe_ident)
      swop/services/generator.py:675-681  (_safe_ident)

REFACTOR[6] (ranked by priority):
  [1] ○ extract_function   → swop/markpact/utils/_build_environments.py
      WHY: 2 occurrences of 27-line block across 1 files — saves 27 lines
      FILES: swop/markpact/graph_builder.py
  [2] ○ extract_function   → swop/utils/_parse_bus.py
      WHY: 2 occurrences of 11-line block across 1 files — saves 11 lines
      FILES: swop/config.py
  [3] ○ extract_function   → swop/tools/utils/format.py
      WHY: 2 occurrences of 10-line block across 2 files — saves 10 lines
      FILES: swop/tools/doctor.py, swop/tools/doctor_deep.py
  [4] ○ extract_function   → swop/utils/_generate_update_from_disk.py
      WHY: 2 occurrences of 9-line block across 1 files — saves 9 lines
      FILES: swop/commands.py
  [5] ○ extract_function   → swop/utils/_render_query_response.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: swop/proto/generator.py, swop/services/generator.py
  [6] ○ extract_function   → swop/utils/_safe_ident.py
      WHY: 2 occurrences of 7-line block across 2 files — saves 7 lines
      FILES: swop/proto/generator.py, swop/services/generator.py

QUICK_WINS[6] (low risk, high savings — do first):
  [1] extract_function   saved=27L  → swop/markpact/utils/_build_environments.py
      FILES: graph_builder.py
  [2] extract_function   saved=11L  → swop/utils/_parse_bus.py
      FILES: config.py
  [3] extract_function   saved=10L  → swop/tools/utils/format.py
      FILES: doctor.py, doctor_deep.py
  [4] extract_function   saved=9L  → swop/utils/_generate_update_from_disk.py
      FILES: commands.py
  [5] extract_function   saved=8L  → swop/utils/_render_query_response.py
      FILES: generator.py, generator.py
  [6] extract_function   saved=7L  → swop/utils/_safe_ident.py
      FILES: generator.py, generator.py

EFFORT_ESTIMATE (total ≈ 2.4h):
  medium _build_environments                 saved=27L  ~54min
  easy   _parse_bus                          saved=11L  ~22min
  easy   format                              saved=10L  ~20min
  easy   _generate_update_from_disk          saved=9L  ~18min
  easy   _render_query_response              saved=8L  ~16min
  easy   _safe_ident                         saved=7L  ~14min

METRICS-TARGET:
  dup_groups:  6 → 0
  saved_lines: 72 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 1074 func | 46f | 2026-04-23

NEXT[10] (ranked by impact):
  [1] !! SPLIT           swop/scan/scanner.py
      WHY: 595L, 0 classes, max CC=13
      EFFORT: ~4h  IMPACT: 7735

  [2] !! SPLIT           swop/commands.py
      WHY: 550L, 0 classes, max CC=14
      EFFORT: ~4h  IMPACT: 7700

  [3] !! SPLIT           swop/services/generator.py
      WHY: 686L, 2 classes, max CC=11
      EFFORT: ~4h  IMPACT: 7546

  [4] !! SPLIT-FUNC      generate_registry_md  CC=32  fan=19
      WHY: CC=32 exceeds 15
      EFFORT: ~1h  IMPACT: 608

  [5] !  SPLIT-FUNC      _check_manifests_vs_proto  CC=15  fan=18
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 270

  [6] !  SPLIT-FUNC      _check_proto_vs_python  CC=15  fan=18
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 270

  [7] !  SPLIT-FUNC      _check_manifests_vs_services  CC=15  fan=17
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 255

  [8] !  SPLIT-FUNC      _index_from_manifests  CC=15  fan=15
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 225

  [9] !  SPLIT-FUNC      RefactorPipeline._cluster_to_spec  CC=23  fan=8
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 184

  [10] !  SPLIT-FUNC      _map_python_type  CC=15  fan=12
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 180


RISKS[3]:
  ⚠ Splitting swop/services/generator.py may break 17 import paths
  ⚠ Splitting swop/scan/scanner.py may break 27 import paths
  ⚠ Splitting swop/commands.py may break 26 import paths

METRICS-TARGET:
  CC̄:          1.5 → ≤1.0
  max-CC:      32 → ≤16
  god-modules: 6 → 0
  high-CC(≥15): 8 → ≤4
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
  prev CC̄=1.4 → now CC̄=1.5
```

## Intent

Bi-directional runtime reconciler and drift-aware state graph for full-stack systems
