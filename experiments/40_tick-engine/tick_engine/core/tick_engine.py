"""
Generic Tick Engine for Tick-Frame Physics

Runs substrate evolution asynchronously in background thread.
Produces tick snapshots for visualization to consume.
"""

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Generic

from tick_engine.core.law_interface import SubstrateLaw, StateType
from tick_engine.core.substrate import Substrate


@dataclass
class TickSnapshot(Generic[StateType]):
    """Immutable snapshot of substrate state at a specific tick"""
    tick: int
    graph: Dict[int, List[int]]
    state: Dict[int, StateType]
    timestamp: float
    law_name: str


class TickEngine(Generic[StateType]):
    """
    Asynchronous tick producer that runs simulation independently.

    The engine runs in a background thread, continuously evolving the substrate
    according to its law and storing snapshots in a bounded buffer.

    Visualization engines consume snapshots at their own pace without blocking
    the simulation.
    """

    def __init__(
        self,
        substrate: Substrate[StateType],
        buffer_size: int = 200,
        collapse_interval: int = 10,
        collapse_size: int = 5
    ):
        """
        Initialize tick engine.

        Args:
            substrate: The substrate to evolve (contains the law)
            buffer_size: Maximum snapshots to keep in buffer
            collapse_interval: How often to collapse graph (in ticks, 0=never)
            collapse_size: How many edges to keep when collapsing
        """
        self.substrate = substrate
        self.buffer_size = buffer_size
        self.collapse_interval = collapse_interval
        self.collapse_size = collapse_size

        # Snapshot buffer (bounded FIFO queue)
        self.snapshots = deque(maxlen=buffer_size)
        self.lock = threading.Lock()

        # Control flags
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.current_tick = 0

    def start(self):
        """Start the simulation engine in background thread"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the simulation engine"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)

    def _run_loop(self):
        """Main simulation loop running in background thread"""
        while self.running:
            self.current_tick += 1
            t = self.current_tick

            # Grow substrate
            self.substrate.grow()

            # Evolve state according to law
            self.substrate.state = self.substrate.law.evolve(
                self.substrate.graph,
                self.substrate.state,
                t
            )

            # Periodic collapse to keep graph bounded
            if self.collapse_interval > 0 and t % self.collapse_interval == 0:
                self.substrate.collapse_to_last_n_edges(self.collapse_size)

            # Create immutable snapshot (deep copy to avoid race conditions)
            snapshot = TickSnapshot(
                tick=t,
                graph={k: list(v) for k, v in self.substrate.graph.items()},
                state=dict(self.substrate.state),
                timestamp=time.time(),
                law_name=self.substrate.law.name
            )

            # Add to buffer (thread-safe)
            with self.lock:
                self.snapshots.append(snapshot)

            # Small delay to prevent CPU saturation
            time.sleep(0.0001)  # 0.1ms

    def get_latest_snapshot(self) -> Optional[TickSnapshot[StateType]]:
        """Get most recent snapshot (non-blocking)"""
        with self.lock:
            return self.snapshots[-1] if self.snapshots else None

    def get_snapshot_at_tick(self, tick: int) -> Optional[TickSnapshot[StateType]]:
        """Get snapshot at specific tick (if available in buffer)"""
        with self.lock:
            for snapshot in reversed(self.snapshots):
                if snapshot.tick == tick:
                    return snapshot
        return None

    def get_snapshot_count(self) -> int:
        """Get number of snapshots in buffer"""
        with self.lock:
            return len(self.snapshots)

    def get_tick_range(self) -> Optional[Tuple[int, int]]:
        """Get (oldest_tick, newest_tick) available in buffer"""
        with self.lock:
            if not self.snapshots:
                return None
            return (self.snapshots[0].tick, self.snapshots[-1].tick)

    def get_current_tick(self) -> int:
        """Get current tick number"""
        return self.current_tick

    def get_stats(self) -> Dict:
        """Get engine statistics"""
        with self.lock:
            buffer_count = len(self.snapshots)
            tick_range = (
                (self.snapshots[0].tick, self.snapshots[-1].tick)
                if self.snapshots else None
            )

        return {
            "current_tick": self.current_tick,
            "running": self.running,
            "buffer_size": buffer_count,
            "buffer_capacity": self.buffer_size,
            "tick_range": tick_range,
            "law": self.substrate.law.name
        }
