import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class TickSnapshot:
    """Immutable snapshot of substrate state at a specific tick"""
    tick: int
    graph: Dict[int, list]  # node -> [neighbors]
    state: Dict[int, Tuple[float, float, float, float]]  # node -> quaternion
    timestamp: float  # wall-clock time when snapshot was created


class TickEngine:
    """
    Asynchronous tick producer that runs simulation independently.
    Stores snapshots in a buffer for visualization to consume.
    """

    def __init__(self, substrate, compute_parity_fn, apply_law_fn, buffer_size=100):
        self.substrate = substrate
        self.compute_parity = compute_parity_fn
        self.apply_law = apply_law_fn
        self.buffer_size = buffer_size

        # Snapshot buffer (bounded queue)
        self.snapshots = deque(maxlen=buffer_size)
        self.lock = threading.Lock()

        # Control flags
        self.running = False
        self.thread = None
        self.current_tick = 0

    def start(self):
        """Start the simulation engine in a background thread"""
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

            # Compute next state
            parity_map = self.compute_parity(self.substrate.graph, self.substrate.state)
            self.substrate.grow(parity_map)
            self.substrate.state = self.apply_law(self.substrate.graph, self.substrate.state, t)

            # Keep graph bounded by collapsing frequently
            if t % 10 == 0:  # Every 10 ticks
                self.substrate.collapse_to_last_n_edges(5)

            # Create immutable snapshot (deep copy to avoid mutation)
            snapshot = TickSnapshot(
                tick=t,
                graph={k: list(v) for k, v in self.substrate.graph.items()},  # deep copy
                state=dict(self.substrate.state),  # quaternions are immutable tuples
                timestamp=time.time()
            )

            # Add to buffer (thread-safe)
            with self.lock:
                self.snapshots.append(snapshot)

            # Add small delay to prevent CPU saturation and allow other threads to run
            time.sleep(0.0001)  # 0.1ms delay

    def get_latest_snapshot(self) -> TickSnapshot | None:
        """Get the most recent snapshot (non-blocking)"""
        with self.lock:
            return self.snapshots[-1] if self.snapshots else None

    def get_snapshot_at_tick(self, tick: int) -> TickSnapshot | None:
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

    def get_tick_range(self) -> Tuple[int, int] | None:
        """Get (oldest_tick, newest_tick) available in buffer"""
        with self.lock:
            if not self.snapshots:
                return None
            return (self.snapshots[0].tick, self.snapshots[-1].tick)
