"""
V17 Evolution - Tick evolution with canvas ontology.

Orchestrates the canvas/renderer model:
1. Each tick, a new renderer is created at origin
2. Each renderer reads the canvas and decides where to paint
3. The canvas accumulates all paint (gamma)
4. Renderers form patterns through gradient-following behavior

Physical model:
- Gradient pulls renderer toward higher gamma (like gravity toward mass)
- Skip probability = |gradient| * SKIP_SENSITIVITY (time dilation resistance)
- When gradient > threshold: move in gradient direction
- When gradient ~0: small random jitter

Author: V17 Implementation
Date: 2026-02-01
"""

import numpy as np
from typing import List, Optional

try:
    from .config_v17 import Config17
    from .canvas import Canvas3D, Pos3D
    from .renderer import Renderer
except ImportError:
    from config_v17 import Config17
    from canvas import Canvas3D, Pos3D
    from renderer import Renderer


class TickEvolution:
    """Orchestrates the canvas/renderer tick evolution.

    Each tick:
    1. Increment tick count
    2. Create new renderer at origin
    3. Each renderer decides where to paint
    4. Canvas accumulates paint
    5. Renderers track their positions

    Memory scales with O(painted_cells) not O(grid^3).
    """

    def __init__(self, config: Config17):
        """Initialize tick evolution.

        Args:
            config: V17 configuration
        """
        self.config = config
        self.canvas = Canvas3D()
        self.renderers: List[Renderer] = []
        self.tick_count = 0

        # Initialize RNG for entity creation
        self.rng = np.random.default_rng(config.random_seed)

        # Statistics
        self.total_skips = 0
        self.total_acts = 0

    @property
    def origin(self) -> Pos3D:
        """Origin where new entities are born."""
        return (0, 0, 0)

    def create_renderer(self) -> Renderer:
        """Create new renderer at origin.

        Returns:
            New Renderer instance
        """
        renderer = Renderer(
            entity_id=self.tick_count,
            seed=self.config.random_seed
        )
        renderer.set_position(self.origin)
        self.renderers.append(renderer)

        # Initial paint at origin
        self.canvas.paint(self.origin, self.config.gamma_imprint)

        return renderer

    def evolve_one_tick(self) -> dict:
        """Execute one tick of evolution.

        Steps:
        1. Increment tick count
        2. Create new renderer at origin
        3. Each renderer renders to canvas
        4. Collect statistics

        Returns:
            Dict with tick info
        """
        self.tick_count += 1
        self.canvas.tick_count = self.tick_count

        # Memory safety check
        memory_mb = self.canvas.get_memory_usage_mb()
        if memory_mb > self.config.max_memory_mb:
            raise MemoryError(
                f"Memory limit exceeded: {memory_mb:.1f} MB > "
                f"{self.config.max_memory_mb} MB at tick {self.tick_count}"
            )

        tick_info = {
            "tick": self.tick_count,
            "memory_mb": memory_mb,
            "painted_cells": self.canvas.painted_cells,
        }

        # Create new renderer at origin
        self.create_renderer()

        # Each renderer renders to canvas
        acts_this_tick = 0
        skips_this_tick = 0

        for renderer in self.renderers:
            result = renderer.render_tick(
                self.canvas,
                skip_sensitivity=self.config.skip_sensitivity,
                jitter_strength=self.config.jitter_strength,
                gradient_threshold=self.config.gradient_threshold,
                gamma_imprint=self.config.gamma_imprint
            )

            if result is None:
                skips_this_tick += 1
            else:
                acts_this_tick += 1

        self.total_acts += acts_this_tick
        self.total_skips += skips_this_tick

        tick_info["acts"] = acts_this_tick
        tick_info["skips"] = skips_this_tick

        return tick_info

    def evolve_n_ticks(
        self,
        n_ticks: int,
        progress_interval: int = 50,
        verbose: bool = True
    ) -> List[dict]:
        """Evolve for n ticks and track statistics.

        Args:
            n_ticks: Number of ticks to evolve
            progress_interval: Report progress every N ticks
            verbose: Print progress

        Returns:
            List of statistics dicts
        """
        history = []

        for tick in range(n_ticks):
            tick_info = self.evolve_one_tick()

            if (tick + 1) % progress_interval == 0:
                stats = self.get_statistics()
                stats['tick'] = tick + 1
                history.append(stats)

                if verbose:
                    print(
                        f"[{tick+1:6d}/{n_ticks:6d}] "
                        f"renderers={stats['renderer_count']:4d}, "
                        f"painted={stats['painted_cells']:6d}, "
                        f"mem={stats['memory_mb']:.2f}MB, "
                        f"skip={stats['skip_rate']:.2f}, "
                        f"r_mean={stats['r_mean']:.1f}"
                    )

        return history

    def get_statistics(self) -> dict:
        """Get current simulation statistics.

        Returns:
            Dict with evolution statistics
        """
        canvas_stats = self.canvas.get_statistics()

        # Compute average time dilation
        if self.renderers:
            avg_dilation = sum(r.time_dilation_factor for r in self.renderers) / len(self.renderers)
        else:
            avg_dilation = 1.0

        # Global skip rate
        total = self.total_acts + self.total_skips
        skip_rate = self.total_skips / total if total > 0 else 0.0

        # Compute mean radius of paint from origin
        radial = self.canvas.get_radial_distribution(self.origin)
        if radial:
            total_gamma = sum(radial.values())
            weighted_r = sum(r * g for r, g in radial.items())
            r_mean = weighted_r / total_gamma if total_gamma > 0 else 0.0
        else:
            r_mean = 0.0

        # Compute mean renderer distance from origin
        if self.renderers:
            renderer_distances = []
            for r in self.renderers:
                x, y, z = r.last_paint_pos
                dist = np.sqrt(x**2 + y**2 + z**2)
                renderer_distances.append(dist)
            renderer_r_mean = sum(renderer_distances) / len(renderer_distances)
        else:
            renderer_r_mean = 0.0

        # Gradient statistics at renderer positions
        if self.renderers:
            gradient_mags = [
                self.canvas.get_gradient_magnitude(r.last_paint_pos)
                for r in self.renderers
            ]
            gradient_mean = sum(gradient_mags) / len(gradient_mags)
            gradient_max = max(gradient_mags)
        else:
            gradient_mean = 0.0
            gradient_max = 0.0

        return {
            "tick_count": self.tick_count,
            "renderer_count": len(self.renderers),
            # Canvas stats
            "painted_cells": canvas_stats["painted_cells"],
            "gamma_sum": canvas_stats["gamma_sum"],
            "gamma_min": canvas_stats["gamma_min"],
            "gamma_max": canvas_stats["gamma_max"],
            "gamma_mean": canvas_stats["gamma_mean"],
            "memory_mb": canvas_stats["memory_mb"],
            "bounds": canvas_stats["bounds"],
            # Radial distribution
            "r_mean": r_mean,
            "renderer_r_mean": renderer_r_mean,
            # Skip statistics
            "total_skips": self.total_skips,
            "total_acts": self.total_acts,
            "skip_rate": skip_rate,
            "avg_time_dilation": avg_dilation,
            # Gradient statistics
            "gradient_mean": gradient_mean,
            "gradient_max": gradient_max,
        }

    def get_renderer_statistics(self) -> List[dict]:
        """Get statistics for all renderers.

        Returns:
            List of renderer stat dicts
        """
        return [r.get_statistics() for r in self.renderers]

    def __repr__(self) -> str:
        stats = self.get_statistics() if self.tick_count > 0 else {}
        return (
            f"TickEvolution(tick={self.tick_count}, "
            f"renderers={len(self.renderers)}, "
            f"painted={stats.get('painted_cells', 0)}, "
            f"mem={stats.get('memory_mb', 0):.2f}MB)"
        )


if __name__ == "__main__":
    from config_v17 import QuickTestConfig

    print("V17 TickEvolution Demo (Canvas Ontology)")
    print("=" * 70)

    # Create configuration
    config = QuickTestConfig()
    print(config.describe())
    print()

    # Create evolution
    evolution = TickEvolution(config)
    print(f"Created: {evolution}")
    print()

    # Evolve for 100 ticks
    print("Evolving for 100 ticks...")
    print("-" * 70)
    history = evolution.evolve_n_ticks(100, progress_interval=20, verbose=True)
    print()

    # Final state
    print("=" * 70)
    print("FINAL STATE")
    print("=" * 70)
    stats = evolution.get_statistics()
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
    print()

    # Sample renderer statistics
    print("Sample renderer statistics (first 10):")
    for r_stats in evolution.get_renderer_statistics()[:10]:
        print(f"  Entity {r_stats['entity_id']}: "
              f"pos={r_stats['position']}, "
              f"dilation={r_stats['time_dilation']:.2f}")
    print()

    # Canvas visualization
    print("Canvas XY slice at z=0:")
    print(evolution.canvas.visualize_slice_ascii("xy", 0, 31))
    print()

    # Radial distribution
    print("Radial distribution (first 15 shells):")
    radial = evolution.canvas.get_radial_distribution()
    for r in sorted(radial.keys())[:15]:
        bar_len = int(radial[r] / 5)
        bar = "#" * bar_len
        print(f"  r={r:3d}: gamma={radial[r]:6.1f} {bar}")
    print()

    print("=" * 70)
