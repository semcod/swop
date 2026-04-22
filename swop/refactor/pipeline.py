"""
Refactor pipeline orchestrator.

Pulls the scanners, graph builder, clusterer and writers together into a
single :class:`RefactorPipeline` that can be driven from code, tests, or
the ``swop refactor`` CLI command.

The default strategy is *seeded* clustering: one module per declared
frontend route. Pass ``strategy="louvain"`` to switch to community-
detection-based clustering instead.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from swop.refactor.clustering import Cluster, LouvainLike, SeededClusterer
from swop.refactor.compose_builder import ComposeBuilder
from swop.refactor.graph import RefactorGraph
from swop.refactor.module_builder import ModuleBuilder, ModuleSpec, ModuleWriteResult
from swop.refactor.scanner.backend import BackendScanner, BackendSignals, ModelSignals
from swop.refactor.scanner.db import DbScanner, DbSignals
from swop.refactor.scanner.frontend import FrontendScanner, PageSignals


_CAMEL_RX = re.compile(r"([a-z])([A-Z])")


@dataclass
class RefactorResult:
    graph: RefactorGraph
    clusters: List[Cluster]
    modules: List[ModuleSpec]
    writes: List[ModuleWriteResult]
    compose_path: Optional[Path]

    def summary(self) -> Dict[str, object]:
        return {
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "clusters": len(self.clusters),
            "modules": [
                {
                    "name": m.name,
                    "route": m.route,
                    "pages": [p.path.name for p in m.pages],
                    "models": [model.name for model in m.models],
                    "tables": m.tables,
                }
                for m in self.modules
            ],
            "compose": str(self.compose_path) if self.compose_path else None,
        }


class RefactorPipeline:
    """High-level orchestrator for graph-based module extraction."""

    def __init__(
        self,
        frontend: Path,
        backend: Optional[Path] = None,
        db: Optional[Path] = None,
        routes: Optional[Sequence[str]] = None,
        out_dir: Path = Path("modules"),
        strategy: str = "seeded",
        frontend_pages_subdir: str = "src/pages",
    ) -> None:
        self.frontend = Path(frontend)
        self.backend = Path(backend) if backend else None
        self.db = Path(db) if db else None
        self.routes = list(routes or [])
        self.out_dir = Path(out_dir)
        self.strategy = strategy
        self.frontend_pages_subdir = frontend_pages_subdir

    # ------------------------------------------------------------------
    # Entrypoint
    # ------------------------------------------------------------------

    def run(self) -> RefactorResult:
        frontend_scanner = FrontendScanner(self.frontend, pages_subdir=self.frontend_pages_subdir)
        pages = frontend_scanner.scan()

        backend_signals = BackendSignals()
        if self.backend:
            backend_signals = BackendScanner(self.backend).scan()

        db_signals: List[DbSignals] = []
        if self.db:
            db_signals = DbScanner(self.db).scan()

        graph = self._build_graph(pages, backend_signals, db_signals)

        if self.strategy == "louvain":
            clusters = LouvainLike(graph).run()
        else:
            seeds = self._seed_nodes(frontend_scanner, pages)
            clusters = SeededClusterer(graph).run(seeds)

        route_for_seed = {self._seed_cluster_name(r): r for r in self.routes}
        modules = [
            self._cluster_to_spec(cluster, graph, pages, backend_signals, db_signals, route_for_seed.get(cluster.id))
            for cluster in clusters
            if cluster.id != "unassigned" and cluster.nodes
        ]

        self.out_dir.mkdir(parents=True, exist_ok=True)
        builder = ModuleBuilder(self.out_dir)
        writes = [builder.write(m) for m in modules]

        compose_path: Optional[Path] = None
        if modules:
            compose_path = ComposeBuilder(self.out_dir).write(modules)

        return RefactorResult(
            graph=graph,
            clusters=clusters,
            modules=modules,
            writes=writes,
            compose_path=compose_path,
        )

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def _build_graph(
        self,
        pages: Iterable[PageSignals],
        backend: BackendSignals,
        dbs: Iterable[DbSignals],
    ) -> RefactorGraph:
        graph = RefactorGraph()

        for page in pages:
            ui_id = f"ui:{page.slug}"
            graph.add_node(ui_id, "ui", path=str(page.path), ids=page.ids, events=page.events)
            for call in page.api_calls:
                api_id = f"api:{call}"
                graph.add_node(api_id, "api", label=call)
                graph.add_edge(ui_id, api_id, weight=1.0, kind="uses")
            for url in page.fetched_urls:
                api_id = f"api:{url}"
                graph.add_node(api_id, "api", url=url)
                graph.add_edge(ui_id, api_id, weight=1.0, kind="uses")

        for model in backend.models:
            graph.add_node(
                f"model:{model.name}",
                "model",
                path=str(model.path),
                fields=model.fields,
                tablename=model.tablename,
            )

        for route in backend.routes:
            graph.add_node(
                f"route:{route.method}:{route.route}",
                "api",
                method=route.method,
                route=route.route,
                path=str(route.path),
            )

        for db in dbs:
            for table in db.tables:
                graph.add_node(f"table:{table}", "table", path=str(db.path))

        self._link_models_to_ui(graph)
        self._link_models_to_tables(graph, backend.models)
        return graph

    @staticmethod
    def _link_models_to_ui(graph: RefactorGraph) -> None:
        ui_nodes = [n for n in graph.nodes.values() if n.type == "ui"]
        model_nodes = [n for n in graph.nodes.values() if n.type == "model"]
        for ui in ui_nodes:
            slug_tokens = _tokenize(ui.id.split(":", 1)[-1])
            for model in model_nodes:
                model_tokens = _tokenize(model.id.split(":", 1)[-1])
                if slug_tokens & model_tokens:
                    graph.add_edge(ui.id, model.id, weight=0.5, kind="binds")

    @staticmethod
    def _link_models_to_tables(graph: RefactorGraph, models: Iterable[ModelSignals]) -> None:
        for model in models:
            if not model.tablename:
                continue
            table_id = f"table:{model.tablename}"
            if table_id in graph.nodes:
                graph.add_edge(f"model:{model.name}", table_id, weight=2.0, kind="binds")

    # ------------------------------------------------------------------
    # Seed resolution
    # ------------------------------------------------------------------

    def _seed_nodes(
        self,
        scanner: FrontendScanner,
        pages: Iterable[PageSignals],
    ) -> List[Tuple[str, str]]:
        page_by_path = {p.path: p for p in pages}
        seeds: List[Tuple[str, str]] = []
        for route in self.routes:
            matching = scanner.find_pages_for_route(route)
            if not matching:
                continue
            # Use the first matching page as seed; additional pages will be
            # pulled into the same cluster via the weighted BFS (they share
            # neighbors in the graph).
            primary = matching[0]
            signals = page_by_path.get(primary)
            if signals is None:
                continue
            cluster_name = self._seed_cluster_name(route)
            seeds.append((cluster_name, f"ui:{signals.slug}"))
        return seeds

    @staticmethod
    def _seed_cluster_name(route: str) -> str:
        parts = [p for p in route.strip("/").split("/") if p]
        return "-".join(parts) or "root"

    # ------------------------------------------------------------------
    # Cluster -> ModuleSpec
    # ------------------------------------------------------------------

    def _cluster_to_spec(
        self,
        cluster: Cluster,
        graph: RefactorGraph,
        pages: Iterable[PageSignals],
        backend: BackendSignals,
        dbs: Iterable[DbSignals],
        route: Optional[str],
    ) -> ModuleSpec:
        ids = set(cluster.nodes)

        page_by_slug = {f"ui:{p.slug}": p for p in pages}
        model_by_name = {f"model:{m.name}": m for m in backend.models}
        route_index: Dict[str, str] = {}
        for r in backend.routes:
            route_index[f"route:{r.method}:{r.route}"] = f"{r.method} {r.route}"

        spec = ModuleSpec(
            name=cluster.id,
            route=route,
            cluster_nodes=sorted(ids),
        )
        spec.pages = [page_by_slug[pid] for pid in ids if pid in page_by_slug]
        spec.models = [model_by_name[mid] for mid in ids if mid in model_by_name]
        spec.endpoints = [route_index[rid] for rid in ids if rid in route_index]
        spec.api_calls = sorted(
            {
                node.payload.get("label") or node.payload.get("url") or node.id.split(":", 1)[-1]
                for nid in ids
                for node in [graph.nodes[nid]]
                if node.type == "api" and nid not in route_index
            }
        )

        table_ids = [nid for nid in ids if nid.startswith("table:")]
        spec.tables = sorted({nid.split(":", 1)[-1] for nid in table_ids})

        # If we have no pages inside the cluster (e.g. Louvain created a
        # cluster without UI anchors) we still want to try to surface all
        # pages that share tokens with the cluster id for discoverability.
        if not spec.pages and route:
            spec.pages = [p for p in pages if _tokenize(p.slug) & _tokenize(cluster.id)]
        return spec


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _tokenize(text: str) -> Set[str]:
    # Split on ``-_/.``, lowercase, and expose CamelCase boundaries.
    normalized = _CAMEL_RX.sub(r"\1 \2", text)
    raw = re.split(r"[-_/.:\s]+", normalized)
    return {token.lower() for token in raw if token and len(token) > 2}
