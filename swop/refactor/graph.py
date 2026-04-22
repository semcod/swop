"""
Lightweight graph model used by the refactor pipeline.

Nodes are keyed by stable string ids prefixed with their type
(``ui:``, ``api:``, ``model:``, ``table:``). Edges are undirected and
accumulate weights when the same pair is observed multiple times.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Tuple


@dataclass
class Node:
    id: str
    type: str  # "ui" | "api" | "model" | "table" | "event"
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    source: str
    target: str
    weight: float = 1.0
    kind: str = "coupling"  # "coupling" | "uses" | "binds"


class RefactorGraph:
    """Undirected weighted graph tailored for system decomposition."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        self._edges: Dict[Tuple[str, str], Edge] = {}

    # ---------------- node / edge API --------------------------------

    def add_node(self, node_id: str, node_type: str, **payload: Any) -> Node:
        if node_id in self.nodes:
            self.nodes[node_id].payload.update(payload)
            return self.nodes[node_id]
        node = Node(id=node_id, type=node_type, payload=dict(payload))
        self.nodes[node_id] = node
        return node

    def add_edge(self, a: str, b: str, weight: float = 1.0, kind: str = "coupling") -> Edge:
        if a == b:
            raise ValueError(f"self-loop not allowed: {a}")
        key = tuple(sorted((a, b)))
        edge = self._edges.get(key)
        if edge is None:
            edge = Edge(source=key[0], target=key[1], weight=weight, kind=kind)
            self._edges[key] = edge
        else:
            edge.weight += weight
        return edge

    # ---------------- queries ----------------------------------------

    @property
    def edges(self) -> List[Edge]:
        return list(self._edges.values())

    def neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        out: List[Tuple[str, float]] = []
        for (a, b), edge in self._edges.items():
            if a == node_id:
                out.append((b, edge.weight))
            elif b == node_id:
                out.append((a, edge.weight))
        return out

    def nodes_of_type(self, node_type: str) -> List[Node]:
        return [n for n in self.nodes.values() if n.type == node_type]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {
                nid: {"type": n.type, "payload": n.payload}
                for nid, n in self.nodes.items()
            },
            "edges": [
                {"source": e.source, "target": e.target, "weight": e.weight, "kind": e.kind}
                for e in self._edges.values()
            ],
        }

    # ---------------- convenience constructors -----------------------

    @classmethod
    def from_iterables(
        cls,
        nodes: Iterable[Tuple[str, str]],
        edges: Iterable[Tuple[str, str]],
    ) -> "RefactorGraph":
        graph = cls()
        for node_id, node_type in nodes:
            graph.add_node(node_id, node_type)
        for a, b in edges:
            graph.add_edge(a, b)
        return graph
