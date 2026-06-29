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

