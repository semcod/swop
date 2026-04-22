"""
Graph clustering algorithms.

Two clusterers are provided:

- :class:`LouvainLike`: a compact, dependency-free heuristic inspired by
  the modularity-gain step of the Louvain method.
- :class:`SeededClusterer`: BFS-based clusterer seeded by a list of node
  ids (one cluster per seed). Intended for the typical use-case where a
  handful of frontend routes anchor the modules we want to extract.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from swop.refactor.graph import RefactorGraph


@dataclass
class Cluster:
    id: str
    nodes: List[str] = field(default_factory=list)
    seed: Optional[str] = None


# ----------------------------------------------------------------------
# Louvain-like
# ----------------------------------------------------------------------


class LouvainLike:
    """Dependency-free modularity-gain clusterer."""

    def __init__(self, graph: RefactorGraph, max_iter: int = 25) -> None:
        self.graph = graph
        self.max_iter = max_iter
        self._cluster_of: Dict[str, int] = {
            node: idx for idx, node in enumerate(graph.nodes)
        }

    def run(self) -> List[Cluster]:
        for _ in range(self.max_iter):
            if not self._step():
                break
        return self._collect()

    # -- internals ----------------------------------------------------

    def _step(self) -> bool:
        changed = False
        for node in list(self.graph.nodes):
            best_cluster = self._cluster_of[node]
            best_gain = 0.0
            current_gain = self._gain_for(node, best_cluster, exclude_self=True)

            candidates = {self._cluster_of[n] for n, _ in self.graph.neighbors(node)}
            for cluster_id in candidates:
                if cluster_id == self._cluster_of[node]:
                    continue
                gain = self._gain_for(node, cluster_id)
                if gain > best_gain and gain > current_gain:
                    best_gain = gain
                    best_cluster = cluster_id

            if best_cluster != self._cluster_of[node]:
                self._cluster_of[node] = best_cluster
                changed = True
        return changed

    def _gain_for(self, node: str, cluster_id: int, exclude_self: bool = False) -> float:
        gain = 0.0
        for neighbor, weight in self.graph.neighbors(node):
            if exclude_self and neighbor == node:
                continue
            if self._cluster_of[neighbor] == cluster_id:
                gain += weight
        return gain

    def _collect(self) -> List[Cluster]:
        buckets: Dict[int, List[str]] = defaultdict(list)
        for node, cluster_id in self._cluster_of.items():
            buckets[cluster_id].append(node)
        return [
            Cluster(id=f"cluster_{idx}", nodes=sorted(nodes))
            for idx, (_, nodes) in enumerate(sorted(buckets.items()))
        ]


# ----------------------------------------------------------------------
# Seeded clusterer
# ----------------------------------------------------------------------


class SeededClusterer:
    """Grow one cluster per seed node via weighted BFS.

    Nodes are assigned to the seed cluster that reaches them with the
    highest cumulative edge weight. Unreachable nodes are placed in an
    ``unassigned`` cluster which callers can drop or inspect.
    """

    def __init__(self, graph: RefactorGraph, max_hops: int = 3) -> None:
        self.graph = graph
        self.max_hops = max_hops

    def run(self, seeds: Sequence[Tuple[str, str]]) -> List[Cluster]:
        # seeds: iterable of (cluster_id, seed_node_id)
        best_score: Dict[str, float] = defaultdict(lambda: -1.0)
        best_cluster: Dict[str, str] = {}
        cluster_ids: List[str] = []

        for cluster_id, seed in seeds:
            cluster_ids.append(cluster_id)
            if seed not in self.graph.nodes:
                continue
            for node, score in self._bfs(seed).items():
                if score > best_score[node]:
                    best_score[node] = score
                    best_cluster[node] = cluster_id

        clusters: Dict[str, Cluster] = {
            cid: Cluster(id=cid, seed=seed) for cid, seed in seeds
        }
        for node, cid in best_cluster.items():
            clusters[cid].nodes.append(node)

        unassigned = Cluster(id="unassigned")
        for node in self.graph.nodes:
            if node not in best_cluster:
                unassigned.nodes.append(node)

        output = [clusters[cid] for cid in cluster_ids]
        if unassigned.nodes:
            output.append(unassigned)

        for cluster in output:
            cluster.nodes = sorted(set(cluster.nodes))
        return output

    def _bfs(self, seed: str) -> Dict[str, float]:
        scores: Dict[str, float] = {seed: float("inf")}
        frontier: List[Tuple[str, float, int]] = [(seed, float("inf"), 0)]
        visited: Set[str] = {seed}
        while frontier:
            node, score, hops = frontier.pop(0)
            if hops >= self.max_hops:
                continue
            for neighbor, weight in self.graph.neighbors(node):
                if neighbor in visited:
                    continue
                # Reaching farther nodes should produce lower scores.
                new_score = weight if score == float("inf") else weight / (hops + 1)
                if new_score > scores.get(neighbor, -1.0):
                    scores[neighbor] = new_score
                    visited.add(neighbor)
                    frontier.append((neighbor, new_score, hops + 1))
        return scores
