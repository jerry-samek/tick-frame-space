import time
from typing import Dict, Tuple, Set


class VisualizationEngine:
    """
    Asynchronous visualization consumer that processes ticks at its own pace.
    Computes state backward from tick delta: Δt = tick(n) - tick(n-v)
    """

    def __init__(self, tick_engine, sample_interval=25):
        self.tick_engine = tick_engine
        self.sample_interval = sample_interval

        # Visualization state
        self.last_visualized_tick = 0
        self.last_snapshot = None
        self.processing_time = 0.0  # Time taken to process last visualization

    def get_next_visualization(self):
        """
        Pull next tick to visualize (only when ready).
        Returns (snapshot, delta_tick, edge_diff) or None if not ready.
        """
        latest = self.tick_engine.get_latest_snapshot()

        if latest is None:
            return None

        # Only visualize at sample intervals
        if latest.tick - self.last_visualized_tick < self.sample_interval:
            return None

        # Compute tick delta
        delta_tick = latest.tick - self.last_visualized_tick

        # Compute backward state difference
        edge_diff = self._compute_edge_diff(self.last_snapshot, latest)

        # Update visualization state
        self.last_visualized_tick = latest.tick
        self.last_snapshot = latest

        return (latest, delta_tick, edge_diff)

    def _compute_edge_diff(self, old_snapshot, new_snapshot):
        """
        Compute edge changes between two snapshots.
        Returns dict with added_edges, removed_edges, and delta_t.
        """
        if old_snapshot is None:
            # First snapshot - all edges are "added"
            current_edges = self._extract_edges(new_snapshot.graph)
            return {
                "tick": new_snapshot.tick,
                "delta_t": new_snapshot.tick,
                "added_edges": list(current_edges),
                "removed_edges": [],
                "processing_time": self.processing_time
            }

        old_edges = self._extract_edges(old_snapshot.graph)
        new_edges = self._extract_edges(new_snapshot.graph)

        added = new_edges - old_edges
        removed = old_edges - new_edges

        return {
            "tick": new_snapshot.tick,
            "delta_t": new_snapshot.tick - old_snapshot.tick,
            "added_edges": list(added),
            "removed_edges": list(removed),
            "processing_time": self.processing_time
        }

    def _extract_edges(self, graph: Dict[int, list]) -> Set[Tuple[int, int]]:
        """Extract normalized edge set from graph"""
        edges = set()
        for a, neighbors in graph.items():
            for b in neighbors:
                # Normalize edge direction
                edge = (min(a, b), max(a, b))
                edges.add(edge)
        return edges

    def mark_processing_complete(self, processing_time: float):
        """Mark that visualization processing is complete"""
        self.processing_time = processing_time

    def get_stats(self):
        """Get visualization statistics"""
        tick_range = self.tick_engine.get_tick_range()
        latest = self.tick_engine.get_latest_snapshot()

        return {
            "last_visualized_tick": self.last_visualized_tick,
            "latest_tick": latest.tick if latest else 0,
            "tick_lag": (latest.tick - self.last_visualized_tick) if latest else 0,
            "buffer_range": tick_range,
            "buffer_size": self.tick_engine.get_snapshot_count(),
            "processing_time_ms": self.processing_time * 1000
        }
