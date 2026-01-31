"""
V12d Minimal Evolution - Jitter Only, No CA Rules

Key insight: On the substrate level, there is only ONE real constant.

- Creation: happens with each tick (1 entity per tick)
- Death: **impossible** - entities can't be removed
- Forgetting: entities outside the observation window become unobservable

The CA "death" rules were implementing forgetting at the wrong level.
An entity with insufficient neighbors isn't dying - it's becoming
incoherent as a pattern. But the substrate should preserve it.

This class eliminates ALL CA parameters:
- No survival threshold (entities persist forever)
- No creation threshold (creation = tick)
- No decay (only forgetting via window)

The only dynamics is jitter - the ONE constant.

Author: V12d Implementation
Date: 2026-01-31
Based on: V12c Tick-Unified + user insight on substrate constants
"""

import numpy as np
from planck_grid import PlanckGrid
from planck_jitter import PlanckJitter


class MinimalEvolution:
    """Minimal evolution: only jitter, no CA rules.

    Entities persist forever. No creation/death rules at substrate level.
    Jitter is the only dynamics.

    Pattern coherence emerges from:
    - Jitter dynamics (the one constant)
    - Gamma field (memory of where entities were)
    - Window (how far back we "remember")
    """

    def __init__(self, grid: PlanckGrid, jitter: PlanckJitter):
        """Initialize minimal evolution.

        Args:
            grid: PlanckGrid to evolve
            jitter: PlanckJitter for zero-point fluctuations
        """
        self.grid = grid
        self.jitter = jitter

    def evolve_one_tick(self):
        """Execute one tick of evolution: only apply jitter.

        No CA rules - just jitter. The substrate preserves everything.
        """
        self.jitter.apply_jitter(self.grid)

    def evolve_n_ticks(self, n_ticks: int, progress_interval: int = 100) -> list:
        """Evolve grid for n ticks and track statistics.

        Args:
            n_ticks: Number of ticks to evolve
            progress_interval: Report progress every N ticks

        Returns:
            List of statistics dicts (one per progress_interval)
        """
        history = []

        for tick in range(n_ticks):
            self.evolve_one_tick()

            if (tick + 1) % progress_interval == 0:
                stats = self.grid.get_field_statistics()
                stats['tick'] = tick + 1
                history.append(stats)

                print(f"[{tick+1:6d}/{n_ticks:6d}] "
                      f"energy={stats['total_energy']:5d}, "
                      f"nonzero={stats['nonzero_fraction']*100:5.1f}%")

        return history


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add parent versions to path
    v6_path = Path(__file__).parent.parent / "v6"
    sys.path.insert(0, str(v6_path))

    from planck_grid import PlanckGrid, visualize_grid_ascii
    from planck_jitter import PlanckJitter
    from pattern_library import PatternLibrary

    print("MinimalEvolution Demo (V12d)")
    print("=" * 70)
    print()
    print("KEY INSIGHT: Only jitter, no CA rules")
    print("Entities persist forever - only forgetting via observation window")
    print()

    # Create grid and jitter
    grid = PlanckGrid(50, 50)
    jitter = PlanckJitter.create_symmetric(jitter_strength=0.119)

    print(f"Grid: {grid}")
    print(f"Jitter: {jitter}")
    print()

    # Initialize with a simple pattern at center
    library = PatternLibrary(pattern_size=5)
    monopole = library.get_pattern("monopole")
    grid.write_region(22, 22, monopole)

    print("Initialized monopole pattern at center (25, 25)")
    print()

    stats_initial = grid.get_field_statistics()
    print(f"Initial: energy={stats_initial['total_energy']}, "
          f"nonzero={stats_initial['nonzero_fraction']*100:.1f}%")
    print()

    # Create minimal evolution (jitter only)
    evolution = MinimalEvolution(grid, jitter)

    # Evolve for 500 ticks
    print("Evolving for 500 ticks (jitter only, no CA rules)...")
    print()
    history = evolution.evolve_n_ticks(500, progress_interval=100)
    print()

    # Final statistics
    stats_final = grid.get_field_statistics()
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Initial energy: {stats_initial['total_energy']}")
    print(f"Final energy: {stats_final['total_energy']}")
    print(f"Energy change: {stats_final['total_energy'] - stats_initial['total_energy']}")
    print()
    print(f"Initial nonzero: {stats_initial['nonzero_fraction']*100:.1f}%")
    print(f"Final nonzero: {stats_final['nonzero_fraction']*100:.1f}%")
    print()

    # Visualize final state
    print("Final grid state (central 30×30 region):")
    print(visualize_grid_ascii(grid, 10, 10, 30, 30))
    print()

    print("=" * 70)
    print("OBSERVATION:")
    print("Without CA rules, jitter alone creates/destroys field values")
    print("but there's no coherent pattern persistence mechanism.")
    print("The gamma field provides memory but doesn't enforce structure.")
    print("=" * 70)
