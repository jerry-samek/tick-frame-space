"""
Generic Visualization Engine for Tick-Frame Physics

Consumes tick snapshots asynchronously at its own pace.
Computes backward state differences from tick deltas.
"""

from typing import Dict, Set, Tuple, Optional, Generic, List
from tick_engine.core.law_interface import SubstrateLaw, StateType
from tick_engine.core.tick_engine import TickEngine, TickSnapshot


class VisualizationEngine(Generic[StateType]):
    """
    Asynchronous visualization consumer that processes ticks at its own pace.

    Implements observer-relative time by computing state backward from tick delta:
    Δt = tick(n) - tick(n-v) where v is visualization lag.
    """

    def __init__(
        self,
        tick_engine: TickEngine[StateType],
        law: SubstrateLaw[StateType],
        sample_interval: int = 25
    ):
        """
        Initialize visualization engine.

        Args:
            tick_engine: The tick engine to consume from
            law: The law (for visualization methods)
            sample_interval: Only visualize every N ticks
        """
        self.tick_engine = tick_engine
        self.law = law
        self.sample_interval = sample_interval

        # Visualization state
        self.last_visualized_tick = 0
        self.last_snapshot: Optional[TickSnapshot[StateType]] = None
        self.processing_time = 0.0

    def get_next_visualization(self) -> Optional[Tuple[TickSnapshot[StateType], int, Dict]]:
        """
        Pull next tick to visualize (only when ready).

        Returns:
            (snapshot, delta_tick, edge_diff) or None if not ready

        The edge_diff dict contains:
            - tick: current tick
            - delta_t: ticks elapsed since last visualization
            - added_edges: edges that appeared
            - removed_edges: edges that disappeared
            - processing_time: time taken for last viz
        """
        latest = self.tick_engine.get_latest_snapshot()

        if latest is None:
            return None

        # Only visualize at sample intervals
        if latest.tick - self.last_visualized_tick < self.sample_interval:
            return None

        # Compute tick delta (observer-relative time)
        delta_tick = latest.tick - self.last_visualized_tick

        # Compute backward state difference
        edge_diff = self._compute_edge_diff(self.last_snapshot, latest)

        # Update visualization state
        self.last_visualized_tick = latest.tick
        self.last_snapshot = latest

        return (latest, delta_tick, edge_diff)

    def _compute_edge_diff(
        self,
        old_snapshot: Optional[TickSnapshot[StateType]],
        new_snapshot: TickSnapshot[StateType]
    ) -> Dict:
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

    def _extract_edges(self, graph: Dict[int, List[int]]) -> Set[Tuple[int, int]]:
        """Extract normalized edge set from graph"""
        edges = set()
        for a, neighbors in graph.items():
            for b in neighbors:
                # Normalize an edge direction (smaller ID first)
                edge = (min(a, b), max(a, b))
                edges.add(edge)
        return edges

    def mark_processing_complete(self, processing_time: float):
        """Mark that visualization processing is complete"""
        self.processing_time = processing_time

    def render_3d_points(self, snapshot: TickSnapshot[StateType]) -> List[Dict]:
        """
        Render snapshot as 3D point cloud using law's visualization methods.

        Returns list of dicts with:
            - node_id: int
            - x, y, z: float coordinates
            - r, g, b: int color values [0-255]
            - state_summary: str description
        """
        points = []
        for node_id, state_value in snapshot.state.items():
            x, y, z = self.law.to_3d_coords(state_value)
            r, g, b = self.law.to_color(state_value)

            points.append({
                "node_id": node_id,
                "x": x,
                "y": y,
                "z": z,
                "r": r,
                "g": g,
                "b": b,
                "state": self.law.state_summary(state_value)
            })

        return points

    def get_stats(self) -> Dict:
        """Get visualization statistics"""
        tick_range = self.tick_engine.get_tick_range()
        latest = self.tick_engine.get_latest_snapshot()

        return {
            "last_visualized_tick": self.last_visualized_tick,
            "latest_tick": latest.tick if latest else 0,
            "tick_lag": (latest.tick - self.last_visualized_tick) if latest else 0,
            "buffer_range": tick_range,
            "buffer_size": self.tick_engine.get_snapshot_count(),
            "processing_time_ms": self.processing_time * 1000,
            "law": self.law.name
        }
