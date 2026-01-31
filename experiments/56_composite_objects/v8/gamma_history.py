"""
Gamma History Committer - Late commit of pattern existence to gamma field.

Implements a sample window mechanism where patterns move freely, then their
movement history gets imprinted into the gamma field after the window closes.
The gamma field becomes an "existence log" of where patterns have been.

Flow:
1. Patterns move within a sample window (N ticks)
2. Positions are accumulated during the window (time-weighted)
3. After window closes: accumulated history commits to gamma field
4. Accumulator resets, new window begins

Author: V8 Late Gamma Commit
Date: 2026-01-30
"""

import numpy as np
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from planck_grid import PlanckGrid
    from sample_cell import PatternInstance
    from projectile import Projectile


class GammaHistoryCommitter:
    """Track pattern positions and commit to gamma field at window boundaries."""

    def __init__(
        self,
        grid: 'PlanckGrid',
        window_size: int,
        imprint_strength: float,
        decay: float = 0.0
    ):
        """
        Initialize gamma history committer.

        Args:
            grid: The Planck grid
            window_size: Number of ticks per sample window
            imprint_strength: Imprint strength parameter (k)
            decay: History decay factor (0 = no decay/accumulate, 1 = full reset)
        """
        self.grid = grid
        self.window_size = window_size
        self.imprint_strength = imprint_strength
        self.decay = decay

        # Accumulator for current window (counts ticks at each position)
        self.accumulator = np.zeros((grid.height, grid.width), dtype=np.float32)

        # Persistent history layer (added to gamma_wells)
        self.history_layer = np.zeros((grid.height, grid.width), dtype=np.float32)

        self.ticks_in_window = 0
        self.total_commits = 0

    def record_tick(self, patterns: List['PatternInstance']):
        """
        Record pattern positions for this tick.

        Args:
            patterns: List of PatternInstance objects to track
        """
        for pattern in patterns:
            cx = int(pattern.sample.center_x)
            cy = int(pattern.sample.center_y)
            size = pattern.sample.size

            # Mark cells occupied by pattern
            half_size = size // 2
            for dy in range(size):
                for dx in range(size):
                    x = cx - half_size + dx
                    y = cy - half_size + dy
                    if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                        self.accumulator[y, x] += 1

        self.ticks_in_window += 1

    def record_projectile_tick(self, projectile: 'Projectile'):
        """
        Record projectile position for this tick.

        Args:
            projectile: The projectile to track
        """
        if not projectile.state.active:
            return

        # Projectile position is relative to center, convert to grid coords
        x = int(projectile.center_x + projectile.state.x)
        y = int(projectile.center_y + projectile.state.y)
        size = projectile.pattern_size

        # Mark cells occupied by projectile
        half_size = size // 2
        for dy in range(size):
            for dx in range(size):
                px = x - half_size + dx
                py = y - half_size + dy
                if 0 <= px < self.grid.width and 0 <= py < self.grid.height:
                    self.accumulator[py, px] += 1

    def should_commit(self) -> bool:
        """Check if window is complete and ready to commit."""
        return self.ticks_in_window >= self.window_size

    def commit(self) -> dict:
        """
        Commit accumulated history to persistent layer.

        Returns:
            Dict with commit statistics
        """
        # Normalize current window contribution:
        # γ_history_new = γ_history_old * (1 - decay) + k * (ticks_at_position / window_size)
        window_contribution = self.accumulator * (self.imprint_strength / self.window_size)

        # Apply decay to old history, add new contribution
        self.history_layer = self.history_layer * (1 - self.decay) + window_contribution

        # Track statistics
        max_contribution = float(np.max(window_contribution))
        total_accumulated = float(np.sum(self.accumulator))
        nonzero_cells = int(np.count_nonzero(self.accumulator))

        # Reset accumulator for next window
        self.accumulator.fill(0)
        self.ticks_in_window = 0
        self.total_commits += 1

        return {
            "commit_number": self.total_commits,
            "max_contribution": max_contribution,
            "total_accumulated": total_accumulated,
            "nonzero_cells": nonzero_cells,
            "history_max": float(np.max(self.history_layer)),
            "history_mean": float(np.mean(self.history_layer)),
        }

    def get_history_contribution(self, x: int, y: int) -> float:
        """
        Get gamma contribution from history at position.

        Args:
            x, y: Grid position

        Returns:
            History contribution to gamma at this position
        """
        if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
            return float(self.history_layer[y, x])
        return 0.0

    def get_history_layer(self) -> np.ndarray:
        """Get the full history layer array (read-only view)."""
        return self.history_layer

    def reset(self):
        """Reset both accumulator and history layer."""
        self.accumulator.fill(0)
        self.history_layer.fill(0)
        self.ticks_in_window = 0
        self.total_commits = 0

    def get_state(self) -> dict:
        """Get current state for debugging/logging."""
        return {
            "ticks_in_window": self.ticks_in_window,
            "window_size": self.window_size,
            "total_commits": self.total_commits,
            "accumulator_nonzero": int(np.count_nonzero(self.accumulator)),
            "history_max": float(np.max(self.history_layer)),
            "history_mean": float(np.mean(self.history_layer)),
        }

    def __repr__(self) -> str:
        return (
            f"GammaHistoryCommitter("
            f"window={self.window_size}, "
            f"k={self.imprint_strength}, "
            f"decay={self.decay}, "
            f"commits={self.total_commits})"
        )


if __name__ == "__main__":
    # Demo
    import sys
    from pathlib import Path
    v6_path = Path(__file__).parent.parent / "v6"
    sys.path.insert(0, str(v6_path))

    from planck_grid import PlanckGrid

    print("GammaHistoryCommitter Demo")
    print("=" * 60)

    # Create grid
    grid = PlanckGrid(50, 50)

    # Create committer
    committer = GammaHistoryCommitter(
        grid,
        window_size=10,
        imprint_strength=5.0,
        decay=0.0
    )
    print(f"Created: {committer}")
    print()

    # Simulate a simple pattern staying in place
    class MockPattern:
        class MockSample:
            def __init__(self, cx, cy, size):
                self.center_x = cx
                self.center_y = cy
                self.size = size
        def __init__(self, cx, cy, size=3):
            self.sample = self.MockSample(cx, cy, size)

    # Pattern stays at (25, 25) for full window
    pattern = MockPattern(25, 25, 3)

    print("Simulating pattern at (25, 25) for 10 ticks...")
    for tick in range(10):
        committer.record_tick([pattern])

    print(f"State before commit: {committer.get_state()}")
    print()

    # Check if ready to commit
    print(f"Should commit: {committer.should_commit()}")

    # Commit
    stats = committer.commit()
    print(f"Commit stats: {stats}")
    print()

    # Check history at center
    print(f"History at (25, 25): {committer.get_history_contribution(25, 25):.3f}")
    print(f"History at (10, 10): {committer.get_history_contribution(10, 10):.3f}")
    print()

    # Run another window with pattern at different position
    print("Simulating pattern at (30, 30) for another window...")
    pattern2 = MockPattern(30, 30, 3)
    for tick in range(10):
        committer.record_tick([pattern2])

    stats2 = committer.commit()
    print(f"Second commit stats: {stats2}")
    print()

    # History should now have both positions (decay=0 means accumulation)
    print(f"History at (25, 25) after 2nd window: {committer.get_history_contribution(25, 25):.3f}")
    print(f"History at (30, 30) after 2nd window: {committer.get_history_contribution(30, 30):.3f}")

    print()
    print("=" * 60)
