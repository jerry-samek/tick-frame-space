# observers/horizon_observer.py

from collections import deque
from typing import Optional

from .base import Observer


class HorizonObserver(Observer):
    """
    Tracks causal reachability from a chosen root entity.
    Computes adjacency shells and horizon radius over time.
    """

    def __init__(self, root_id: int = 0, max_depth: int = 10, log_interval: int = 10, output_dir: Optional[str] = None):
        super().__init__(name="Horizon", log_interval=log_interval, output_dir=output_dir)
        self.root_id = root_id
        self.max_depth = max_depth

    def bfs_shells(self, adjacency, root, max_depth):
        """Return list of shells: shells[d] = list of nodes at distance d."""
        if root not in adjacency:
            return []

        visited = {root}
        queue = deque([(root, 0)])
        shells = [[] for _ in range(max_depth + 1)]

        while queue:
            node, depth = queue.popleft()
            if depth > max_depth:
                break

            shells[depth].append(node)

            for nbr in adjacency.neighbors(node):
                if nbr not in visited:
                    visited.add(nbr)
                    queue.append((nbr, depth + 1))

        return shells

    def on_post_tick(self, state):
        tick = state.tick

        shells = self.bfs_shells(state.adjacency, self.root_id, self.max_depth)

        horizon_radius = 0
        for d, shell in enumerate(shells):
            if len(shell) > 0:
                horizon_radius = d

        # Log horizon metrics
        if self.should_log(tick):
            # Main metrics to CSV
            data = {
                "tick": tick,
                "horizon_radius": horizon_radius,
                "total_reachable": sum(len(shell) for shell in shells)
            }
            self.log_csv("horizon_metrics.csv", data)

            # Detailed shell information
            for d, shell in enumerate(shells):
                if len(shell) > 0:
                    shell_data = {
                        "tick": tick,
                        "distance": d,
                        "shell_size": len(shell)
                    }
                    self.log_csv("horizon_shells.csv", shell_data)

            # Summary text log
            summary = (
                f"[Horizon t={tick}] "
                f"Root={self.root_id}, Radius={horizon_radius}, "
                f"Reachable={sum(len(s) for s in shells)}\n"
            )
            self.log_text("horizon_log.txt", summary)
