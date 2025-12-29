"""
Generic Substrate for Tick-Frame Physics Engine

The substrate represents the underlying graph structure and node states.
It is parameterized by a Law that defines how states evolve.
"""

from typing import Dict, List, Generic, Optional
from collections import deque
from tick_engine.core.law_interface import SubstrateLaw, StateType


class Substrate(Generic[StateType]):
    """
    Generic substrate that works with any law implementing SubstrateLaw protocol.

    The substrate maintains:
    - Graph topology (nodes and edges)
    - Node states (governed by the law)
    - Growth logic (delegated to the law)
    """

    def __init__(
        self,
        graph: Dict[int, List[int]],
        initial_state: Dict[int, StateType],
        law: SubstrateLaw[StateType]
    ):
        """
        Initialize substrate with graph, initial state, and evolution law.

        Args:
            graph: Dict mapping node_id -> list of neighbor node_ids
            initial_state: Dict mapping node_id -> initial state value
            law: The evolution law to use
        """
        self.graph = graph
        self.state = initial_state
        self.law = law

    def grow(self) -> int:
        """
        Grow the graph by adding new nodes where the law permits.

        Returns:
            Number of new nodes added
        """
        # Find next available node ID
        if self.graph:
            next_id = max(self.graph.keys()) + 1
        else:
            next_id = 0

        # Track nodes to add (don't modify dict while iterating)
        nodes_to_add = []

        # Ask law if each node should grow
        for node in list(self.graph.keys()):
            if node not in self.graph:  # Node might have been removed
                continue

            neighbors = self.graph[node]
            neighbor_states = [self.state[n] for n in neighbors if n in self.state]

            if self.law.should_grow(node, self.state[node], neighbors, neighbor_states):
                nodes_to_add.append(node)

        # Add new nodes
        for parent_node in nodes_to_add:
            new_node = next_id
            next_id += 1

            # Initialize parent if needed
            if parent_node not in self.graph:
                self.graph[parent_node] = []

            # Add bidirectional edge
            self.graph[parent_node].append(new_node)
            self.graph[new_node] = [parent_node]

            # Initialize state using law
            self.state[new_node] = self.law.initial_state(new_node)

        return len(nodes_to_add)

    def prune_to_horizon(self, root: int, horizon: int):
        """
        Remove nodes beyond the horizon distance from root.

        Uses BFS to find all nodes within horizon steps of root,
        then removes everything else.

        Args:
            root: Starting node for horizon calculation
            horizon: Maximum distance to keep
        """
        keep = self._bfs_horizon(root, horizon)

        # Remove nodes outside horizon
        for node in list(self.graph.keys()):
            if node not in keep:
                del self.graph[node]
                if node in self.state:
                    del self.state[node]

        # Remove edges to deleted nodes
        for node in self.graph:
            self.graph[node] = [n for n in self.graph[node] if n in keep]

    def collapse_to_last_n_edges(self, n: int = 10):
        """
        Collapse graph to only the last N edges (by recency).

        Assumes higher node IDs = more recent creation.

        Args:
            n: Number of edges to keep
        """
        # Collect all edges
        all_edges = set()
        for a, neighbors in self.graph.items():
            for b in neighbors:
                edge = (min(a, b), max(a, b))
                all_edges.add(edge)

        if not all_edges:
            self.graph = {}
            self.state = {}
            return

        # Sort by recency (max node ID in edge)
        sorted_edges = sorted(all_edges, key=lambda e: max(e))

        # Keep last N edges
        selected = sorted_edges[-n:]

        # Build new graph from selected edges
        new_graph = {}
        new_state = {}

        for a, b in selected:
            new_graph.setdefault(a, []).append(b)
            new_graph.setdefault(b, []).append(a)
            new_state[a] = self.state.get(a, self.law.initial_state(a))
            new_state[b] = self.state.get(b, self.law.initial_state(b))

        self.graph = new_graph
        self.state = new_state

    def _bfs_horizon(self, root: int, horizon: int) -> set:
        """
        BFS to find all nodes within horizon distance of root.

        Args:
            root: Starting node
            horizon: Maximum distance

        Returns:
            Set of node IDs within horizon
        """
        if root not in self.graph:
            return set()

        visited = {root}
        queue = deque([(root, 0)])

        while queue:
            node, dist = queue.popleft()
            if dist >= horizon:
                continue

            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))

        return visited

    def node_count(self) -> int:
        """Return number of nodes in graph"""
        return len(self.graph)

    def edge_count(self) -> int:
        """Return number of edges in graph (undirected)"""
        edges = set()
        for a, neighbors in self.graph.items():
            for b in neighbors:
                edges.add((min(a, b), max(a, b)))
        return len(edges)

    def get_stats(self) -> Dict:
        """Return substrate statistics"""
        return {
            "nodes": self.node_count(),
            "edges": self.edge_count(),
            "law": self.law.name
        }
