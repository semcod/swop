"""
Graph versioning.

Tracks every mutation as a ``GraphVersion`` entry in the project graph so
that the system is replayable and migrations can be generated later.
"""

import time

from swop.graph import GraphVersion, ProjectGraph


class Versioning:
    """Append a new ``GraphVersion`` entry whenever the graph mutates."""

    def commit(self, graph: ProjectGraph, message: str) -> GraphVersion:
        graph.version += 1
        entry = GraphVersion(
            version=graph.version,
            timestamp=time.time(),
            changes=[message],
        )
        graph.history.append(entry)
        print(f"[VERSION] -> {graph.version}: {message}")
        return entry
