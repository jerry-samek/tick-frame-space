from collections import defaultdict, deque
from typing import Optional

from .base import Observer


class GenesisObserver(Observer):
    """
    Observer for genesis-related metrics:
    - adjacency frontier (outermost shell)
    - horizon radius (max BFS depth)
    - shell populations
    - branching factor
    - entity and edge counts
    """

    def __init__(self, log_interval: int = 1, output_dir: Optional[str] = None):
        super().__init__(name="Genesis", log_interval=log_interval, output_dir=output_dir)

        self.memory["horizon_history"] = []
        self.memory["frontier_size_history"] = []
        self.memory["entity_count_history"] = []
        self.memory["edge_count_history"] = []
        self.memory["branching_factor_history"] = []

    def on_post_tick(self, state) -> None:
        tick = state.tick
        graph = state.adjacency

        if graph.number_of_nodes() == 0:
            return

        # Pick seed (first node)
        root = next(iter(graph.nodes))

        # Compute BFS shells
        shells = self._compute_shells(graph, root)

        # Horizon = deepest shell index
        horizon = max(shells.keys())

        # Frontier = outermost shell
        frontier_size = len(shells[horizon])

        # Basic counts
        num_entities = graph.number_of_nodes()
        num_edges = graph.number_of_edges()

        # Branching factor = |S_{k+1}| / |S_k|
        branching_factor = self._compute_branching_factor(shells)

        # Store history
        self.memory["horizon_history"].append(horizon)
        self.memory["frontier_size_history"].append(frontier_size)
        self.memory["entity_count_history"].append(num_entities)
        self.memory["edge_count_history"].append(num_edges)
        self.memory["branching_factor_history"].append(branching_factor)

        # Logging
        if self.should_log(tick):
            data = {
                "tick": tick,
                "horizon": horizon,
                "frontier_size": frontier_size,
                "num_entities": num_entities,
                "num_edges": num_edges,
                "branching_factor": branching_factor,
            }
            self.log_csv("genesis_metrics.csv", data)

            summary = (
                f"[Genesis t={tick}] "
                f"Horizon: {horizon}, "
                f"Frontier: {frontier_size}, "
                f"Entities: {num_entities}, "
                f"Edges: {num_edges}, "
                f"Branching: {branching_factor:.3f}\n"
            )
            self.log_text("genesis_log.txt", summary)

    # ---------------------------------------------------------
    # BFS shells
    # ---------------------------------------------------------
    def _compute_shells(self, graph, root):
        shells = defaultdict(list)
        visited = {root}
        queue = deque([(root, 0)])

        while queue:
            node, dist = queue.popleft()
            shells[dist].append(node)

            for nbr in graph.neighbors(node):
                if nbr not in visited:
                    visited.add(nbr)
                    queue.append((nbr, dist + 1))

        return shells

    # ---------------------------------------------------------
    # Branching factor
    # ---------------------------------------------------------
    def _compute_branching_factor(self, shells):
        # Average |S_{k+1}| / |S_k|
        ratios = []
        for k in range(max(shells.keys())):
            S_k = len(shells[k])
            S_k1 = len(shells[k + 1])
            if S_k > 0:
                ratios.append(S_k1 / S_k)

        return sum(ratios) / len(ratios) if ratios else 0.0
