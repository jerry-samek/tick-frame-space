"""
V18 Evolution - Main simulation loop with unified composite physics.

Orchestrates:
1. Each tick: new process may be created at origin
2. Each process executes step (reads canvas, transitions state, paints imprint)
3. Canvas accumulates paint (gamma)
4. Wake field decays gradually
5. Statistics recorded

Author: V18 Implementation
Date: 2026-02-04
"""

import numpy as np
from typing import List, Dict, Optional, Any
import time

try:
    from .canvas_v18 import Canvas3D_V18, Pos3D
    from .process import CompositeProcess, SimpleDegenerateProcess
except ImportError:
    from canvas_v18 import Canvas3D_V18, Pos3D
    from process import CompositeProcess, SimpleDegenerateProcess


class TickEvolution_V18:
    """Main evolution loop - unified composite physics."""

    def __init__(self, max_ticks: int = 1000, random_seed: int = 42):
        """Initialize evolution.

        Args:
            max_ticks: Maximum ticks to run
            random_seed: Random seed
        """
        self.max_ticks = max_ticks
        self.random_seed = random_seed
        self.rng = np.random.default_rng(random_seed)

        np.random.seed(random_seed)  # Also set global numpy seed

        # Simulation state
        self.canvas = Canvas3D_V18()
        self.processes: List[CompositeProcess] = []
        self.tick_count = 0

        # Statistics
        self.history: List[Dict[str, Any]] = []
        self.creation_rate = 1  # Processes per tick

    @property
    def origin(self) -> Pos3D:
        """Origin where new processes are created."""
        return (0, 0, 0)

    def create_new_process(self) -> CompositeProcess:
        """Create new process at origin.

        Returns:
            New CompositeProcess
        """
        process_id = self.tick_count
        process = SimpleDegenerateProcess(
            process_id=process_id,
            center=self.origin
        )
        process.birth_tick = self.tick_count
        return process

    def evolve_one_tick(self):
        """Execute one tick of unified physics."""
        self.tick_count += 1

        # 1. Create new process at origin (if within creation rate)
        if self.tick_count % max(1, int(1.0 / self.creation_rate)) == 0:
            new_process = self.create_new_process()
            self.processes.append(new_process)

        # 2. Each process steps (unified execution)
        for process in self.processes[:]:
            continues = process.step(self.canvas)
            if not continues:
                self.canvas.clear_process_paint(process.process_id)
                self.processes.remove(process)

        # 3. Wake field decays gradually
        self.canvas.decay_wake(decay_rate=0.05)

        # 4. Record statistics
        self._record_stats()

    def evolve_n_ticks(
        self,
        n: int,
        progress_interval: int = 100,
        verbose: bool = True,
    ) -> List[Dict[str, Any]]:
        """Evolve for n ticks.

        Args:
            n: Number of ticks
            progress_interval: Print progress every n ticks
            verbose: Print progress

        Returns:
            History of statistics
        """
        start_time = time.time()

        for tick in range(n):
            self.evolve_one_tick()

            if verbose and (tick + 1) % progress_interval == 0:
                elapsed = time.time() - start_time
                rate = (tick + 1) / elapsed
                print(f"  Tick {tick + 1:5d} / {n} "
                      f"({rate:6.1f} ticks/s) "
                      f"processes={len(self.processes)} "
                      f"cells={self.canvas.get_statistics()['painted_cells']}")

        return self.history

    def get_statistics(self) -> Dict[str, Any]:
        """Get current simulation statistics.

        Returns:
            Dict with all relevant stats
        """
        canvas_stats = self.canvas.get_statistics()

        if self.processes:
            process_stats = [p.get_statistics() for p in self.processes]
            avg_time_dilation = np.mean([p.time_dilation_factor for p in self.processes])
            avg_age = np.mean([p.age_ticks for p in self.processes])
        else:
            process_stats = []
            avg_time_dilation = 1.0
            avg_age = 0.0

        return {
            'tick_count': self.tick_count,
            'process_count': len(self.processes),
            'avg_time_dilation': avg_time_dilation,
            'avg_age_ticks': avg_age,
            'painted_cells': canvas_stats['painted_cells'],
            'total_gamma': canvas_stats['total_gamma'],
            'total_wake': canvas_stats['total_wake'],
            'memory_mb': canvas_stats['memory_mb'],
            'r_mean': canvas_stats['r_mean'],
            'r_max': canvas_stats['r_max'],
            'processes': process_stats,
        }

    def _record_stats(self):
        """Record statistics for this tick."""
        stats = self.get_statistics()
        self.history.append({
            'tick': self.tick_count,
            'process_count': stats['process_count'],
            'painted_cells': stats['painted_cells'],
            'total_gamma': stats['total_gamma'],
            'memory_mb': stats['memory_mb'],
            'r_mean': stats['r_mean'],
        })
