# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/inspect
- **Primary Language**: python
- **Languages**: python: 51, yaml: 8, md: 7, shell: 2, toml: 1
- **Analysis Mode**: static
- **Total Functions**: 890
- **Total Classes**: 92
- **Modules**: 71
- **Entry Points**: 788

## Architecture by Module

### SUMD
- **Functions**: 316
- **File**: `SUMD.md`

### project.map.toon
- **Functions**: 316
- **File**: `map.toon.yaml`

### swop.scan.scanner
- **Functions**: 22
- **File**: `scanner.py`

### swop.cli
- **Functions**: 20
- **File**: `cli.py`

### swop.services.generator
- **Functions**: 17
- **Classes**: 2
- **File**: `generator.py`

### swop.resolve.resolver
- **Functions**: 13
- **Classes**: 3
- **File**: `resolver.py`

### swop.manifests.generator
- **Functions**: 12
- **Classes**: 2
- **File**: `generator.py`

### swop.cqrs.registry
- **Functions**: 12
- **Classes**: 2
- **File**: `registry.py`

### swop.scan.report
- **Functions**: 11
- **Classes**: 4
- **File**: `report.py`

### swop.markpact.parser
- **Functions**: 11
- **Classes**: 2
- **File**: `parser.py`

### swop.markpact.doql_bridge
- **Functions**: 11
- **Classes**: 22
- **File**: `doql_bridge.py`

### swop.proto.generator
- **Functions**: 11
- **Classes**: 3
- **File**: `generator.py`

### swop.scan.cache
- **Functions**: 10
- **Classes**: 2
- **File**: `cache.py`

### swop.tools.doctor
- **Functions**: 10
- **Classes**: 2
- **File**: `doctor.py`

### swop.refactor.pipeline
- **Functions**: 10
- **Classes**: 2
- **File**: `pipeline.py`

### swop.config
- **Functions**: 9
- **Classes**: 5
- **File**: `config.py`

### swop.core
- **Functions**: 8
- **Classes**: 1
- **File**: `core.py`

### swop.refactor.clustering
- **Functions**: 8
- **Classes**: 3
- **File**: `clustering.py`

### swop.refactor.scanner.frontend
- **Functions**: 8
- **Classes**: 2
- **File**: `frontend.py`

### swop.reconcile
- **Functions**: 7
- **Classes**: 4
- **File**: `reconcile.py`

## Key Entry Points

Main execution flows into the system:

### swop.markpact.doql_bridge.DoqlBridge._build_minimal_spec
- **Calls**: _MinimalDoqlSpec, data.get, data.get, data.get, data.get, data.get, data.get, data.get

### swop.cli._cmd_generate
- **Calls**: Path, examples.manifest.print, ManifestParser, parser.parse_file, examples.manifest.print, examples.manifest.print, SwopRuntime, manifest_path.exists

### swop.markpact.parser.ManifestParser.parse
- **Calls**: CODEBLOCK_RE.finditer, INCLUDE_RE.finditer, set, ManifestBlock, blocks.append, None.resolve, _seen.add, m.group

### swop.refactor.pipeline.RefactorPipeline.run
- **Calls**: FrontendScanner, frontend_scanner.scan, BackendSignals, self._build_graph, self.out_dir.mkdir, ModuleBuilder, RefactorResult, None.scan

### swop.cli._cmd_scan
- **Calls**: swop.scan.scanner.scan_project, None.resolve, Path.cwd, Path, swop.config.load_config, swop.scan.render.write_report, written.items, examples.manifest.print

### swop.refactor.scanner.frontend.FrontendScanner.scan_file
- **Calls**: path.read_text, PageSignals, sorted, sorted, sorted, sorted, sorted, sorted

### swop.cli._cmd_watch
- **Calls**: WatchEngine, examples.manifest.print, engine.poll_once, swop.watch.engine.rebuild_once, examples.manifest.print, engine.run, None.resolve, Path.cwd

### swop.markpact.doql_bridge.DoqlBridge.from_blocks
> Merge all known ``markpact:*`` blocks into a single DoqlSpec.

Supports ``doql``, ``workflows``, ``roles``, ``deploy``,
``integrations``, ``webhooks``
- **Calls**: self._build_spec, MarkpactValidationError, self._parse_block, self._merge_fragment, fragment.get, isinstance, fragment.get, isinstance

### swop.refactor.scanner.backend.BackendScanner._extract_models
- **Calls**: ast.walk, ast.parse, ModelSignals, out.append, path.read_text, isinstance, self._looks_like_model, isinstance

### swop.cli._cmd_gen_services
- **Calls**: examples.manifest.print, None.resolve, Path.cwd, Path, swop.config.load_config, Path, manifests_dir.exists, examples.manifest.print

### swop.cli._cmd_refactor
- **Calls**: RefactorPipeline, pipeline.run, result.summary, examples.manifest.print, examples.manifest.print, examples.manifest.print, Path, Path

### swop.markpact.sync_engine.ManifestSyncEngine.diff
> Return a list of (path, status, detail) for each tracked file.

Status values::

    "ok"       — manifest and disk are identical
    "missing"  — fil
- **Calls**: self.check, self.parser.parse_file, self.base_dir.rglob, b.get_meta_value, result.append, f.is_file, f.name.endswith, str

### swop.markpact.sync_engine.ManifestSyncEngine.update_manifest
> Rewrite ``markpact:file`` block bodies in the manifest with disk content.

Reverse sync: filesystem → manifest. Only the bodies of tracked file
blocks
- **Calls**: manifest_path.read_text, re.compile, pattern.sub, None.strip, re.search, path_match.group, None.rstrip, updated.append

### swop.cli._cmd_resolve
- **Calls**: swop.scan.scanner.scan_project, swop.resolve.resolver.resolve_schema_drift, None.resolve, Path.cwd, Path, swop.config.load_config, Path, examples.manifest.print

### swop.scan.report.Detection.from_dict
- **Calls**: Detection, data.get, isinstance, parsed_fields.append, isinstance, data.items, parsed_fields.append, FieldDef

### swop.refactor.pipeline.RefactorPipeline._build_graph
- **Calls**: RefactorGraph, self._link_models_to_ui, self._link_models_to_tables, graph.add_node, graph.add_node, graph.add_node, graph.add_node, graph.add_edge

### swop.markpact.doql_bridge.DoqlBridge._merge_fragment
- **Calls**: dict, fragment.items, key.startswith, isinstance, result.get, isinstance, list, isinstance

### swop.cli._cmd_gen_proto
- **Calls**: swop.proto.generator.generate_proto_from_manifests, examples.manifest.print, None.resolve, Path.cwd, Path, swop.config.load_config, Path, manifests_dir.exists

### swop.scan.report.ScanReport.format_text
- **Calls**: self.kinds, self.via, None.join, lines.append, sorted, lines.append, self.contexts.values, lines.append

### swop.refactor.scanner.frontend.FrontendScanner.find_pages_for_route
> Best-effort match between a URL route and page files on disk.
- **Calls**: self._route_token, self.iter_pages, page.stem.lower, len, None.join, self.iter_pages, stem.startswith, matches.append

### swop.cqrs.decorators.handler
> Register the decorated class as the handler for ``target``.

``target`` may be the command/query class itself or its qualified
name as a string. If ``
- **Calls**: isinstance, getattr, swop.cqrs.decorators._collect_source, CqrsRecord, None.register, setattr, isinstance, target.strip

### swop.refactor.pipeline.RefactorPipeline._cluster_to_spec
- **Calls**: set, ModuleSpec, sorted, sorted, sorted, nid.startswith, node.payload.get, node.payload.get

### swop.refactor.clustering.SeededClusterer.run
- **Calls**: defaultdict, best_cluster.items, Cluster, cluster_ids.append, None.items, Cluster, None.nodes.append, output.append

### swop.cli._cmd_gen_manifests
- **Calls**: swop.scan.scanner.scan_project, swop.manifests.generator.generate_manifests, examples.manifest.print, None.resolve, Path.cwd, Path, swop.config.load_config, Path

### swop.cli._cmd_gen_grpc_python
- **Calls**: swop.proto.compiler.compile_proto_python, examples.manifest.print, None.resolve, Path.cwd, Path, swop.config.load_config, Path, Path

### swop.cli._cmd_gen_grpc_ts
- **Calls**: swop.proto.compiler.compile_proto_typescript, examples.manifest.print, None.resolve, Path.cwd, Path, swop.config.load_config, Path, Path

### swop.markpact.sync_engine.ManifestSyncEngine.check
> Return a status list for every tracked ``markpact:file`` block.
- **Calls**: self.parser.parse_file, set, block.get_meta_value, seen.add, swop.markpact.sync_engine._hash, statuses.append, full.exists, swop.markpact.sync_engine._hash

### swop.cqrs.decorators._make_decorator
- **Calls**: swop.cqrs.decorators._normalize_emits, ValueError, swop.cqrs.decorators._collect_source, CqrsRecord, None.register, setattr, isinstance, context.strip

### swop.watch.engine.WatchEngine.snapshot
> Walk configured source roots and return {path: mtime}.
- **Calls**: set, seen.add, root.is_file, root.rglob, None.resolve, self.config.root.resolve, root.exists, self._maybe_add

### swop.scan.cache.FingerprintCache.load
- **Calls**: None.items, self.path.exists, json.loads, raw.get, CacheEntry, self.path.read_text, raw.get, Detection.from_dict

## Process Flows

Key execution flows identified:

### Flow 1: _build_minimal_spec
```
_build_minimal_spec [swop.markpact.doql_bridge.DoqlBridge]
```

### Flow 2: _cmd_generate
```
_cmd_generate [swop.cli]
  └─ →> print
  └─ →> print
```

### Flow 3: parse
```
parse [swop.markpact.parser.ManifestParser]
```

### Flow 4: run
```
run [swop.refactor.pipeline.RefactorPipeline]
```

### Flow 5: _cmd_scan
```
_cmd_scan [swop.cli]
  └─ →> scan_project
      └─> _resolve_contexts
      └─> _iter_python_files
      └─ →> load_config
  └─ →> load_config
      └─> _from_dict
```

### Flow 6: scan_file
```
scan_file [swop.refactor.scanner.frontend.FrontendScanner]
```

### Flow 7: _cmd_watch
```
_cmd_watch [swop.cli]
  └─ →> print
  └─ →> print
  └─ →> rebuild_once
      └─ →> scan_project
          └─> _resolve_contexts
          └─> _iter_python_files
```

### Flow 8: from_blocks
```
from_blocks [swop.markpact.doql_bridge.DoqlBridge]
```

### Flow 9: _extract_models
```
_extract_models [swop.refactor.scanner.backend.BackendScanner]
```

### Flow 10: _cmd_gen_services
```
_cmd_gen_services [swop.cli]
  └─ →> print
  └─ →> load_config
      └─> _from_dict
```

## Key Classes

### swop.scan.cache.FingerprintCache
> Persistent sha256-based cache of scanner detections.
- **Methods**: 10
- **Key Methods**: swop.scan.cache.FingerprintCache.__init__, swop.scan.cache.FingerprintCache.load, swop.scan.cache.FingerprintCache.save, swop.scan.cache.FingerprintCache.fingerprint, swop.scan.cache.FingerprintCache.get, swop.scan.cache.FingerprintCache.put, swop.scan.cache.FingerprintCache.drop, swop.scan.cache.FingerprintCache.prune, swop.scan.cache.FingerprintCache.__len__, swop.scan.cache.FingerprintCache.__contains__

### swop.markpact.doql_bridge.DoqlBridge
> Convert a collection of ``ManifestBlock`` objects into a DoqlSpec.
- **Methods**: 10
- **Key Methods**: swop.markpact.doql_bridge.DoqlBridge.__init__, swop.markpact.doql_bridge.DoqlBridge._try_import_doql, swop.markpact.doql_bridge.DoqlBridge.from_blocks, swop.markpact.doql_bridge.DoqlBridge._parse_block, swop.markpact.doql_bridge.DoqlBridge._merge_fragment, swop.markpact.doql_bridge.DoqlBridge._build_spec, swop.markpact.doql_bridge.DoqlBridge._build_minimal_spec, swop.markpact.doql_bridge.DoqlBridge.from_file, swop.markpact.doql_bridge.DoqlBridge.from_files, swop.markpact.doql_bridge.DoqlBridge.from_text

### swop.cqrs.registry.CqrsRegistry
> Thread-safe map of decorator-registered CQRS artifacts.
- **Methods**: 10
- **Key Methods**: swop.cqrs.registry.CqrsRegistry.__init__, swop.cqrs.registry.CqrsRegistry.register, swop.cqrs.registry.CqrsRegistry.clear, swop.cqrs.registry.CqrsRegistry.all, swop.cqrs.registry.CqrsRegistry.of_kind, swop.cqrs.registry.CqrsRegistry.by_context, swop.cqrs.registry.CqrsRegistry.contexts, swop.cqrs.registry.CqrsRegistry.summary, swop.cqrs.registry.CqrsRegistry.__len__, swop.cqrs.registry.CqrsRegistry.__iter__

### swop.core.SwopRuntime
> Main orchestrator for the swop reconciliation system.
- **Methods**: 8
- **Key Methods**: swop.core.SwopRuntime.__init__, swop.core.SwopRuntime.add_model, swop.core.SwopRuntime.add_service, swop.core.SwopRuntime.add_ui_binding, swop.core.SwopRuntime.introspect, swop.core.SwopRuntime.run_sync, swop.core.SwopRuntime.state_yaml, swop.core.SwopRuntime.docker_compose

### swop.markpact.parser.ManifestParser
> Parse markpact blocks from markdown manifests.
- **Methods**: 8
- **Key Methods**: swop.markpact.parser.ManifestParser.__init__, swop.markpact.parser.ManifestParser.parse_file, swop.markpact.parser.ManifestParser.parse, swop.markpact.parser.ManifestParser.parse_by_kind, swop.markpact.parser.ManifestParser.parse_doql_blocks, swop.markpact.parser.ManifestParser.parse_graph_blocks, swop.markpact.parser.ManifestParser.parse_file_blocks, swop.markpact.parser.ManifestParser.parse_config_blocks

### swop.refactor.graph.RefactorGraph
> Undirected weighted graph tailored for system decomposition.
- **Methods**: 8
- **Key Methods**: swop.refactor.graph.RefactorGraph.__init__, swop.refactor.graph.RefactorGraph.add_node, swop.refactor.graph.RefactorGraph.add_edge, swop.refactor.graph.RefactorGraph.edges, swop.refactor.graph.RefactorGraph.neighbors, swop.refactor.graph.RefactorGraph.nodes_of_type, swop.refactor.graph.RefactorGraph.as_dict, swop.refactor.graph.RefactorGraph.from_iterables

### swop.refactor.pipeline.RefactorPipeline
> High-level orchestrator for graph-based module extraction.
- **Methods**: 8
- **Key Methods**: swop.refactor.pipeline.RefactorPipeline.__init__, swop.refactor.pipeline.RefactorPipeline.run, swop.refactor.pipeline.RefactorPipeline._build_graph, swop.refactor.pipeline.RefactorPipeline._link_models_to_ui, swop.refactor.pipeline.RefactorPipeline._link_models_to_tables, swop.refactor.pipeline.RefactorPipeline._seed_nodes, swop.refactor.pipeline.RefactorPipeline._seed_cluster_name, swop.refactor.pipeline.RefactorPipeline._cluster_to_spec

### swop.refactor.scanner.frontend.FrontendScanner
> Scan a frontend project root and emit ``PageSignals`` per page.
- **Methods**: 8
- **Key Methods**: swop.refactor.scanner.frontend.FrontendScanner.__init__, swop.refactor.scanner.frontend.FrontendScanner._pages_root, swop.refactor.scanner.frontend.FrontendScanner.iter_pages, swop.refactor.scanner.frontend.FrontendScanner.scan, swop.refactor.scanner.frontend.FrontendScanner.scan_file, swop.refactor.scanner.frontend.FrontendScanner.find_pages_for_route, swop.refactor.scanner.frontend.FrontendScanner._route_token, swop.refactor.scanner.frontend.FrontendScanner._slug_for

### swop.scan.report.ScanReport
- **Methods**: 7
- **Key Methods**: swop.scan.report.ScanReport.add, swop.scan.report.ScanReport.kinds, swop.scan.report.ScanReport.via, swop.scan.report.ScanReport.of_kind, swop.scan.report.ScanReport.of_context, swop.scan.report.ScanReport.to_dict, swop.scan.report.ScanReport.format_text

### swop.markpact.sync_engine.ManifestSyncEngine
> Check and sync ``markpact:file`` blocks against the filesystem.
- **Methods**: 6
- **Key Methods**: swop.markpact.sync_engine.ManifestSyncEngine.__init__, swop.markpact.sync_engine.ManifestSyncEngine.check, swop.markpact.sync_engine.ManifestSyncEngine.diff, swop.markpact.sync_engine.ManifestSyncEngine.sync_to_disk, swop.markpact.sync_engine.ManifestSyncEngine.sync_from_disk, swop.markpact.sync_engine.ManifestSyncEngine.update_manifest

### swop.refactor.scanner.backend.BackendScanner
> Scan a Python backend root for models and routes.
- **Methods**: 6
- **Key Methods**: swop.refactor.scanner.backend.BackendScanner.__init__, swop.refactor.scanner.backend.BackendScanner._iter_py, swop.refactor.scanner.backend.BackendScanner.scan, swop.refactor.scanner.backend.BackendScanner._extract_models, swop.refactor.scanner.backend.BackendScanner._looks_like_model, swop.refactor.scanner.backend.BackendScanner._extract_routes

### swop.reconcile.ResyncEngine
> Continuously reconcile the declared graph against actual state.
- **Methods**: 5
- **Key Methods**: swop.reconcile.ResyncEngine.__init__, swop.reconcile.ResyncEngine.reconcile, swop.reconcile.ResyncEngine._has_critical, swop.reconcile.ResyncEngine._auto_heal, swop.reconcile.ResyncEngine._log_drift

### swop.refactor.clustering.LouvainLike
> Dependency-free modularity-gain clusterer.
- **Methods**: 5
- **Key Methods**: swop.refactor.clustering.LouvainLike.__init__, swop.refactor.clustering.LouvainLike.run, swop.refactor.clustering.LouvainLike._step, swop.refactor.clustering.LouvainLike._gain_for, swop.refactor.clustering.LouvainLike._collect

### swop.resolve.resolver.ResolutionReport
- **Methods**: 5
- **Key Methods**: swop.resolve.resolver.ResolutionReport.breaking, swop.resolve.resolver.ResolutionReport.non_breaking, swop.resolve.resolver.ResolutionReport.counts, swop.resolve.resolver.ResolutionReport.to_json, swop.resolve.resolver.ResolutionReport.format

### swop.config.SwopConfig
- **Methods**: 4
- **Key Methods**: swop.config.SwopConfig.project_root, swop.config.SwopConfig.state_path, swop.config.SwopConfig.context, swop.config.SwopConfig.iter_source_roots

### swop.tools.doctor.DoctorReport
- **Methods**: 4
- **Key Methods**: swop.tools.doctor.DoctorReport.failed, swop.tools.doctor.DoctorReport.warnings, swop.tools.doctor.DoctorReport.ok, swop.tools.doctor.DoctorReport.format

### swop.introspect.backend.BackendIntrospector
> Introspect backend services to produce a runtime state dict.
- **Methods**: 4
- **Key Methods**: swop.introspect.backend.BackendIntrospector.__init__, swop.introspect.backend.BackendIntrospector.introspect, swop.introspect.backend.BackendIntrospector.register_model, swop.introspect.backend.BackendIntrospector.register_route

### swop.watch.engine.WatchEngine
> mtime-polling watcher for Python source files.

Call :meth:`poll_once` in a loop (or pass it to :met
- **Methods**: 4
- **Key Methods**: swop.watch.engine.WatchEngine.snapshot, swop.watch.engine.WatchEngine._maybe_add, swop.watch.engine.WatchEngine.poll_once, swop.watch.engine.WatchEngine.run

### swop.sync.SyncEngine
> Move state between a ``ProjectGraph`` and introspected snapshots.
- **Methods**: 3
- **Key Methods**: swop.sync.SyncEngine.frontend_to_graph, swop.sync.SyncEngine.merge_frontend, swop.sync.SyncEngine.merge_backend

### swop.markpact.parser.ManifestBlock
- **Methods**: 3
- **Key Methods**: swop.markpact.parser.ManifestBlock.get_meta_value, swop.markpact.parser.ManifestBlock.as_yaml, swop.markpact.parser.ManifestBlock.as_json

## Data Transformation Functions

Key functions that process and transform data:

### swop.config._parse_context
- **Output to**: swop.config._pop_known, BoundedContextConfig, SwopConfigError, dict, str

### swop.config._parse_bus
- **Output to**: swop.config._pop_known, BusConfig, isinstance, SwopConfigError, dict

### swop.config._parse_read_models
- **Output to**: swop.config._pop_known, ReadModelConfig, isinstance, SwopConfigError, dict

### swop.cli._build_parser
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_subparsers, None.set_defaults, sub.add_parser

### swop.scan.scanner._unparse
- **Output to**: ast.unparse

### swop.scan.report.ScanReport.format_text
- **Output to**: self.kinds, self.via, None.join, lines.append, sorted

### swop.services.generator.ServiceGenerationResult.format
- **Output to**: sorted, None.join, None.append, by_ctx.items, lines.append

### swop.tools.init.InitResult.format
- **Output to**: lines.append, lines.append, lines.append, None.join

### swop.tools.doctor.DoctorCheck.format
- **Output to**: None.get

### swop.tools.doctor.DoctorReport.format
- **Output to**: lines.extend, None.join, lines.append, c.format, lines.append

### swop.markpact.parser.ManifestParser.parse_file
- **Output to**: path.read_text, self.parse, str

### swop.markpact.parser.ManifestParser.parse
- **Output to**: CODEBLOCK_RE.finditer, INCLUDE_RE.finditer, set, ManifestBlock, blocks.append

### swop.markpact.parser.ManifestParser.parse_by_kind
- **Output to**: self.parse

### swop.markpact.parser.ManifestParser.parse_doql_blocks
- **Output to**: self.parse_by_kind

### swop.markpact.parser.ManifestParser.parse_graph_blocks
- **Output to**: self.parse_by_kind

### swop.markpact.parser.ManifestParser.parse_file_blocks
- **Output to**: self.parse_by_kind

### swop.markpact.parser.ManifestParser.parse_config_blocks
- **Output to**: self.parse_by_kind

### swop.markpact.doql_bridge.DoqlBridge._parse_block
- **Output to**: block.lang.lower, ValueError, json.loads, yaml.safe_load

### swop.proto.generator.ProtoGenerationResult.format
- **Output to**: None.join, lines.append, lines.append, lines.append, len

### swop.proto.compiler.CompilationResult.format
- **Output to**: None.join, lines.append, lines.append, lines.append, lines.append

### swop.manifests.generator.ManifestGenerationResult.format
- **Output to**: None.join, lines.append, len

### swop.watch.engine.WatchRebuild.format
- **Output to**: len, len, None.join, lines.append, len

### swop.resolve.resolver.Change.format

### swop.resolve.resolver.ResolutionReport.format
- **Output to**: self.counts, None.join, lines.append, change.format, None.join

### SUMD._build_parser

## Behavioral Patterns

### recursion__expand_env
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: swop.config._expand_env

### recursion__decorator_name
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: swop.scan.scanner._decorator_name

### recursion__map_python_type
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: swop.proto.generator._map_python_type

### state_machine_StateExporter
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: swop.export.yaml.StateExporter.to_dict, swop.export.yaml.StateExporter.export_yaml

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `swop.proto.generator.render_proto_for_context` - 43 calls
- `swop.scan.scanner.scan_project` - 31 calls
- `swop.services.generator.generate_services` - 30 calls
- `swop.scan.render.render_html` - 25 calls
- `swop.tools.init.init_project` - 25 calls
- `swop.markpact.parser.ManifestParser.parse` - 25 calls
- `swop.proto.compiler.compile_proto_typescript` - 23 calls
- `swop.refactor.pipeline.RefactorPipeline.run` - 22 calls
- `swop.proto.compiler.compile_proto_python` - 21 calls
- `swop.proto.generator.generate_proto_from_manifests` - 20 calls
- `swop.refactor.scanner.frontend.FrontendScanner.scan_file` - 20 calls
- `swop.markpact.doql_bridge.DoqlBridge.from_blocks` - 18 calls
- `swop.tools.doctor.run_doctor` - 17 calls
- `swop.markpact.sync_engine.ManifestSyncEngine.diff` - 16 calls
- `swop.markpact.sync_engine.ManifestSyncEngine.update_manifest` - 16 calls
- `swop.scan.report.Detection.from_dict` - 15 calls
- `swop.resolve.resolver.resolve_schema_drift` - 14 calls
- `swop.scan.report.ScanReport.format_text` - 13 calls
- `swop.refactor.scanner.frontend.FrontendScanner.find_pages_for_route` - 13 calls
- `swop.config.load_config` - 12 calls
- `swop.cqrs.decorators.handler` - 12 calls
- `swop.refactor.clustering.SeededClusterer.run` - 12 calls
- `swop.markpact.sync_engine.ManifestSyncEngine.check` - 11 calls
- `swop.manifests.generator.generate_manifests` - 11 calls
- `swop.watch.engine.WatchEngine.snapshot` - 11 calls
- `swop.scan.cache.FingerprintCache.load` - 10 calls
- `swop.services.generator.ServiceGenerationResult.format` - 10 calls
- `swop.scan.report.ScanReport.to_dict` - 9 calls
- `swop.proto.generator.ProtoGenerationResult.format` - 9 calls
- `swop.reconcile.DriftDetector.compute` - 8 calls
- `swop.sync.SyncEngine.merge_backend` - 8 calls
- `swop.core.SwopRuntime.run_sync` - 8 calls
- `swop.export.yaml.StateExporter.to_dict` - 8 calls
- `swop.scan.render.write_report` - 8 calls
- `swop.tools.doctor.DoctorReport.format` - 8 calls
- `swop.proto.compiler.CompilationResult.format` - 8 calls
- `swop.introspect.frontend.FrontendIntrospector.from_html` - 7 calls
- `swop.refactor.scanner.backend.BackendScanner.scan` - 7 calls
- `swop.watch.engine.WatchEngine.poll_once` - 7 calls
- `swop.core.SwopRuntime.introspect` - 6 calls

## System Interactions

How components interact:

```mermaid
graph TD
    _build_minimal_spec --> _MinimalDoqlSpec
    _build_minimal_spec --> get
    _cmd_generate --> Path
    _cmd_generate --> print
    _cmd_generate --> ManifestParser
    _cmd_generate --> parse_file
    parse --> finditer
    parse --> set
    parse --> ManifestBlock
    parse --> append
    run --> FrontendScanner
    run --> scan
    run --> BackendSignals
    run --> _build_graph
    run --> mkdir
    _cmd_scan --> scan_project
    _cmd_scan --> resolve
    _cmd_scan --> cwd
    _cmd_scan --> Path
    _cmd_scan --> load_config
    scan_file --> read_text
    scan_file --> PageSignals
    scan_file --> sorted
    _cmd_watch --> WatchEngine
    _cmd_watch --> print
    _cmd_watch --> poll_once
    _cmd_watch --> rebuild_once
    from_blocks --> _build_spec
    from_blocks --> MarkpactValidationEr
    from_blocks --> _parse_block
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.