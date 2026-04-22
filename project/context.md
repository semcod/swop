# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/inspect
- **Primary Language**: python
- **Languages**: python: 21, yaml: 8, md: 6, shell: 2, toml: 1
- **Analysis Mode**: static
- **Total Functions**: 114
- **Total Classes**: 31
- **Modules**: 40
- **Entry Points**: 112

## Architecture by Module

### SUMD
- **Functions**: 21
- **File**: `SUMD.md`

### project.map.toon
- **Functions**: 21
- **File**: `map.toon.yaml`

### swop.cli
- **Functions**: 8
- **File**: `cli.py`

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

### swop.refactor.graph
- **Functions**: 7
- **Classes**: 3
- **File**: `graph.py`

### swop.refactor.scanner.backend
- **Functions**: 6
- **Classes**: 4
- **File**: `backend.py`

### swop.introspect.backend
- **Functions**: 4
- **Classes**: 1
- **File**: `backend.py`

### swop.sync
- **Functions**: 3
- **Classes**: 1
- **File**: `sync.py`

### swop.utils
- **Functions**: 3
- **File**: `utils.py`

### swop.refactor.scanner.db
- **Functions**: 3
- **Classes**: 2
- **File**: `db.py`

### swop.export.docker
- **Functions**: 2
- **Classes**: 1
- **File**: `docker.py`

### swop.export.yaml
- **Functions**: 2
- **Classes**: 1
- **File**: `yaml.py`

### swop.introspect.frontend
- **Functions**: 2
- **Classes**: 1
- **File**: `frontend.py`

### swop.versioning
- **Functions**: 1
- **Classes**: 1
- **File**: `versioning.py`

### swop.graph
- **Functions**: 0
- **Classes**: 6
- **File**: `graph.py`

## Key Entry Points

Main execution flows into the system:

### swop.refactor.scanner.frontend.FrontendScanner.scan_file
- **Calls**: path.read_text, PageSignals, sorted, sorted, sorted, sorted, sorted, sorted

### swop.refactor.scanner.backend.BackendScanner._extract_models
- **Calls**: ast.walk, ast.parse, ModelSignals, out.append, path.read_text, isinstance, self._looks_like_model, isinstance

### swop.refactor.scanner.frontend.FrontendScanner.find_pages_for_route
> Best-effort match between a URL route and page files on disk.
- **Calls**: self._route_token, self.iter_pages, page.stem.lower, len, None.join, self.iter_pages, stem.startswith, matches.append

### swop.refactor.clustering.SeededClusterer.run
- **Calls**: defaultdict, best_cluster.items, Cluster, cluster_ids.append, None.items, Cluster, None.nodes.append, output.append

### swop.reconcile.DriftDetector.compute
- **Calls**: Drift, set, sorted, sorted, actual.get, graph.models.values, drift.invalid_bindings.append, graph.services.values

### swop.sync.SyncEngine.merge_backend
> Merge backend models and routes into the graph.
- **Calls**: None.items, backend_state.get, backend_state.get, DataModel, graph.services.get, Service, service.routes.setdefault, ModelField

### swop.core.SwopRuntime.__init__
- **Calls**: ProjectGraph, SyncEngine, ResyncEngine, Versioning, StateExporter, DockerExporter, BackendIntrospector, FrontendIntrospector

### swop.core.SwopRuntime.run_sync
> Run one reconciliation pass and return the drift report.
- **Calls**: self.introspect, self.sync_engine.merge_backend, self.sync_engine.merge_frontend, self.resync.reconcile, print, print, actual.get, self.state_exporter.export_yaml

### swop.export.yaml.StateExporter.to_dict
- **Calls**: asdict, list, sorted, model.fields.keys, graph.models.items, service.routes.keys, graph.services.items, list

### swop.refactor.clustering.LouvainLike._collect
- **Calls**: defaultdict, self._cluster_of.items, None.append, Cluster, enumerate, sorted, sorted, buckets.items

### swop.refactor.clustering.SeededClusterer._bfs
- **Calls**: float, frontier.pop, self.graph.neighbors, float, scores.get, visited.add, frontier.append, float

### swop.introspect.frontend.FrontendIntrospector.from_html
> Extract bindings and events from an HTML string.

This is intentionally a lightweight regex-based extractor; for a
full parser wire in ``beautifulsoup
- **Calls**: _SELECTOR_RE.finditer, re.findall, match.group, raw.split, selectors.append, None.startswith, match.group

### swop.refactor.scanner.backend.BackendScanner._iter_py
- **Calls**: set, base.rglob, base.exists, any, seen.add, path.is_file, path.match

### swop.refactor.scanner.backend.BackendScanner.scan
- **Calls**: BackendSignals, self._iter_py, self._iter_py, signals.models.extend, signals.routes.extend, self._extract_models, self._extract_routes

### swop.refactor.scanner.backend.BackendScanner._extract_routes
- **Calls**: _RX_ROUTE_DECORATOR.finditer, path.read_text, out.append, match.group, match.group, RouteSignals, method.upper

### swop.reconcile.ResyncEngine._log_drift
- **Calls**: print, print, print, print, print, print

### swop.cli._cmd_inspect
- **Calls**: swop.cli._build_runtime, print, runtime.backend.introspect, print, print, runtime.frontend.introspect

### swop.core.SwopRuntime.introspect
> Return a merged snapshot of actual backend + frontend state.
- **Calls**: self.backend.introspect, self.frontend.introspect, backend_state.get, backend_state.get, frontend_state.get, frontend_state.get

### swop.refactor.scanner.db.DbScanner.scan
- **Calls**: self.root.rglob, self.root.exists, out.append, self._scan_file, path.is_file, path.suffix.lower

### swop.reconcile.ResyncEngine.reconcile
- **Calls**: self.detector.compute, self._log_drift, self._has_critical, DriftError, self._auto_heal

### swop.refactor.scanner.db.DbScanner._scan_file
- **Calls**: DbSignals, sqlite3.connect, conn.execute, conn.close, cursor.fetchall

### swop.refactor.graph.RefactorGraph.add_edge
- **Calls**: tuple, self._edges.get, ValueError, sorted, Edge

### swop.refactor.scanner.frontend.FrontendScanner.iter_pages
- **Calls**: self._pages_root, set, pages_root.glob, path.is_file, seen.add

### swop.refactor.scanner.backend.BackendScanner._looks_like_model
- **Calls**: any, isinstance, base_names.append, isinstance, base_names.append

### swop.cli._cmd_state
- **Calls**: swop.cli._build_runtime, runtime.run_sync, print, runtime.state_yaml

### swop.cli._cmd_export
- **Calls**: swop.cli._build_runtime, print, print, runtime.docker_compose

### swop.versioning.Versioning.commit
- **Calls**: GraphVersion, graph.history.append, print, time.time

### swop.utils.stable_hash
> Return a deterministic SHA-1 hash of a JSON-serializable payload.
- **Calls**: json.dumps, None.hexdigest, hashlib.sha1, serialized.encode

### swop.export.docker.DockerExporter.to_dict
- **Calls**: graph.services.items, None.join, sorted, service.routes.keys

### swop.refactor.clustering.LouvainLike._step
- **Calls**: list, self._gain_for, self._gain_for, self.graph.neighbors

## Process Flows

Key execution flows identified:

### Flow 1: scan_file
```
scan_file [swop.refactor.scanner.frontend.FrontendScanner]
```

### Flow 2: _extract_models
```
_extract_models [swop.refactor.scanner.backend.BackendScanner]
```

### Flow 3: find_pages_for_route
```
find_pages_for_route [swop.refactor.scanner.frontend.FrontendScanner]
```

### Flow 4: run
```
run [swop.refactor.clustering.SeededClusterer]
```

### Flow 5: compute
```
compute [swop.reconcile.DriftDetector]
```

### Flow 6: merge_backend
```
merge_backend [swop.sync.SyncEngine]
```

### Flow 7: __init__
```
__init__ [swop.core.SwopRuntime]
```

### Flow 8: run_sync
```
run_sync [swop.core.SwopRuntime]
```

### Flow 9: to_dict
```
to_dict [swop.export.yaml.StateExporter]
```

### Flow 10: _collect
```
_collect [swop.refactor.clustering.LouvainLike]
```

## Key Classes

### swop.core.SwopRuntime
> Main orchestrator for the swop reconciliation system.
- **Methods**: 8
- **Key Methods**: swop.core.SwopRuntime.__init__, swop.core.SwopRuntime.add_model, swop.core.SwopRuntime.add_service, swop.core.SwopRuntime.add_ui_binding, swop.core.SwopRuntime.introspect, swop.core.SwopRuntime.run_sync, swop.core.SwopRuntime.state_yaml, swop.core.SwopRuntime.docker_compose

### swop.refactor.graph.RefactorGraph
> Undirected weighted graph tailored for system decomposition.
- **Methods**: 8
- **Key Methods**: swop.refactor.graph.RefactorGraph.__init__, swop.refactor.graph.RefactorGraph.add_node, swop.refactor.graph.RefactorGraph.add_edge, swop.refactor.graph.RefactorGraph.edges, swop.refactor.graph.RefactorGraph.neighbors, swop.refactor.graph.RefactorGraph.nodes_of_type, swop.refactor.graph.RefactorGraph.as_dict, swop.refactor.graph.RefactorGraph.from_iterables

### swop.refactor.scanner.frontend.FrontendScanner
> Scan a frontend project root and emit ``PageSignals`` per page.
- **Methods**: 8
- **Key Methods**: swop.refactor.scanner.frontend.FrontendScanner.__init__, swop.refactor.scanner.frontend.FrontendScanner._pages_root, swop.refactor.scanner.frontend.FrontendScanner.iter_pages, swop.refactor.scanner.frontend.FrontendScanner.scan, swop.refactor.scanner.frontend.FrontendScanner.scan_file, swop.refactor.scanner.frontend.FrontendScanner.find_pages_for_route, swop.refactor.scanner.frontend.FrontendScanner._route_token, swop.refactor.scanner.frontend.FrontendScanner._slug_for

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

### swop.introspect.backend.BackendIntrospector
> Introspect backend services to produce a runtime state dict.
- **Methods**: 4
- **Key Methods**: swop.introspect.backend.BackendIntrospector.__init__, swop.introspect.backend.BackendIntrospector.introspect, swop.introspect.backend.BackendIntrospector.register_model, swop.introspect.backend.BackendIntrospector.register_route

### swop.sync.SyncEngine
> Move state between a ``ProjectGraph`` and introspected snapshots.
- **Methods**: 3
- **Key Methods**: swop.sync.SyncEngine.frontend_to_graph, swop.sync.SyncEngine.merge_frontend, swop.sync.SyncEngine.merge_backend

### swop.refactor.scanner.db.DbScanner
> Scan a directory for SQLite databases and enumerate their tables.
- **Methods**: 3
- **Key Methods**: swop.refactor.scanner.db.DbScanner.__init__, swop.refactor.scanner.db.DbScanner.scan, swop.refactor.scanner.db.DbScanner._scan_file

### swop.refactor.clustering.SeededClusterer
> Grow one cluster per seed node via weighted BFS.

Nodes are assigned to the seed cluster that reache
- **Methods**: 3
- **Key Methods**: swop.refactor.clustering.SeededClusterer.__init__, swop.refactor.clustering.SeededClusterer.run, swop.refactor.clustering.SeededClusterer._bfs

### swop.export.docker.DockerExporter
> Render a ``ProjectGraph`` into a docker-compose specification.
- **Methods**: 2
- **Key Methods**: swop.export.docker.DockerExporter.to_dict, swop.export.docker.DockerExporter.export_yaml

### swop.export.yaml.StateExporter
> Serialize a ``ProjectGraph`` plus a ``Drift`` to YAML.
- **Methods**: 2
- **Key Methods**: swop.export.yaml.StateExporter.to_dict, swop.export.yaml.StateExporter.export_yaml

### swop.introspect.frontend.FrontendIntrospector
> Introspect frontend artifacts to produce a runtime state dict.
- **Methods**: 2
- **Key Methods**: swop.introspect.frontend.FrontendIntrospector.introspect, swop.introspect.frontend.FrontendIntrospector.from_html

### swop.reconcile.Drift
- **Methods**: 1
- **Key Methods**: swop.reconcile.Drift.exists

### swop.reconcile.DriftDetector
> Compare a declared graph with the actual runtime state.
- **Methods**: 1
- **Key Methods**: swop.reconcile.DriftDetector.compute

### swop.versioning.Versioning
> Append a new ``GraphVersion`` entry whenever the graph mutates.
- **Methods**: 1
- **Key Methods**: swop.versioning.Versioning.commit

### swop.reconcile.DriftError
> Raised when drift is detected while running in STRICT mode.
- **Methods**: 0
- **Inherits**: Exception

### swop.graph.ModelField
- **Methods**: 0

### swop.graph.DataModel
- **Methods**: 0

### swop.graph.UIBinding
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### swop.cli._build_parser
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_subparsers, None.set_defaults, sub.add_parser

### SUMD._build_parser

### project.map.toon._build_parser

## Behavioral Patterns

### state_machine_StateExporter
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: swop.export.yaml.StateExporter.to_dict, swop.export.yaml.StateExporter.export_yaml

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `swop.refactor.scanner.frontend.FrontendScanner.scan_file` - 20 calls
- `swop.refactor.scanner.frontend.FrontendScanner.find_pages_for_route` - 13 calls
- `swop.refactor.clustering.SeededClusterer.run` - 12 calls
- `swop.reconcile.DriftDetector.compute` - 8 calls
- `swop.sync.SyncEngine.merge_backend` - 8 calls
- `swop.core.SwopRuntime.run_sync` - 8 calls
- `swop.export.yaml.StateExporter.to_dict` - 8 calls
- `swop.introspect.frontend.FrontendIntrospector.from_html` - 7 calls
- `swop.refactor.scanner.backend.BackendScanner.scan` - 7 calls
- `swop.core.SwopRuntime.introspect` - 6 calls
- `swop.refactor.scanner.db.DbScanner.scan` - 6 calls
- `swop.reconcile.ResyncEngine.reconcile` - 5 calls
- `swop.refactor.graph.RefactorGraph.add_edge` - 5 calls
- `swop.refactor.scanner.frontend.FrontendScanner.iter_pages` - 5 calls
- `swop.versioning.Versioning.commit` - 4 calls
- `swop.utils.stable_hash` - 4 calls
- `swop.export.docker.DockerExporter.to_dict` - 4 calls
- `swop.cli.main` - 3 calls
- `swop.core.SwopRuntime.add_model` - 3 calls
- `swop.core.SwopRuntime.add_ui_binding` - 3 calls
- `swop.refactor.graph.RefactorGraph.add_node` - 3 calls
- `swop.refactor.graph.RefactorGraph.neighbors` - 3 calls
- `swop.refactor.graph.RefactorGraph.from_iterables` - 3 calls
- `swop.refactor.clustering.LouvainLike.run` - 3 calls
- `swop.sync.SyncEngine.merge_frontend` - 2 calls
- `swop.core.SwopRuntime.add_service` - 2 calls
- `swop.core.SwopRuntime.state_yaml` - 2 calls
- `swop.export.docker.DockerExporter.export_yaml` - 2 calls
- `swop.export.yaml.StateExporter.export_yaml` - 2 calls
- `swop.introspect.backend.BackendIntrospector.introspect` - 2 calls
- `swop.refactor.graph.RefactorGraph.as_dict` - 2 calls
- `swop.refactor.scanner.frontend.FrontendScanner.scan` - 2 calls
- `swop.reconcile.Drift.exists` - 1 calls
- `swop.sync.SyncEngine.frontend_to_graph` - 1 calls
- `swop.utils.is_callable` - 1 calls
- `swop.utils.get_docstring` - 1 calls
- `swop.core.SwopRuntime.docker_compose` - 1 calls
- `swop.introspect.frontend.FrontendIntrospector.introspect` - 1 calls
- `swop.introspect.backend.BackendIntrospector.register_model` - 1 calls
- `swop.introspect.backend.BackendIntrospector.register_route` - 1 calls

## System Interactions

How components interact:

```mermaid
graph TD
    scan_file --> read_text
    scan_file --> PageSignals
    scan_file --> sorted
    _extract_models --> walk
    _extract_models --> parse
    _extract_models --> ModelSignals
    _extract_models --> append
    _extract_models --> read_text
    find_pages_for_route --> _route_token
    find_pages_for_route --> iter_pages
    find_pages_for_route --> lower
    find_pages_for_route --> len
    find_pages_for_route --> join
    run --> defaultdict
    run --> items
    run --> Cluster
    run --> append
    compute --> Drift
    compute --> set
    compute --> sorted
    compute --> get
    merge_backend --> items
    merge_backend --> get
    merge_backend --> DataModel
    __init__ --> ProjectGraph
    __init__ --> SyncEngine
    __init__ --> ResyncEngine
    __init__ --> Versioning
    __init__ --> StateExporter
    run_sync --> introspect
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.