"""
Gamma History Committer V10 - Renormalization-based history (no explicit decay).

Key difference from V8:
- V8: history = old × (1-decay) + new  (explicit decay parameter)
- V10: history accumulates, normalization applied on use

The "decay" effect emerges naturally from normalization - as total history
grows, each individual contribution's relative influence diminishes.

Normalization Options:
1. Global Sum: history / (1 + sum(history) / N)
   - Total existence dilutes individual influence
   - Distributed history favored over concentrated

2. Time-Based: history / (1 + commits)
   - Recent history matters more
   - Temporal locality preserved

3. Local Gamma: history / gamma_base
   - High-gamma regions have less history influence
   - Couples history directly to gamma field

Author: V10 Renormalization
Date: 2026-01-30
"""

import numpy as np
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from planck_grid import PlanckGrid
    from sample_cell import PatternInstance
    from projectile import Projectile


class GammaHistoryCommitterV10:
    """Track pattern positions and apply normalization instead of decay.

    Unlike V8 which uses explicit decay:
        history = old × (1 - decay) + new

    V10 accumulates without decay and normalizes on use:
        history = old + new
        contribution = normalize(history)
    """

    def __init__(
        self,
        grid: 'PlanckGrid',
        window_size: int,
        imprint_strength: float,
        normalization_type: str = 'global_sum',
        normalization_scale: float = 1000.0
    ):
        """
        Initialize gamma history committer with renormalization.

        Args:
            grid: The Planck grid
            window_size: Number of ticks per sample window
            imprint_strength: Imprint strength parameter (k)
            normalization_type: One of 'global_sum', 'time_based', 'local_gamma'
            normalization_scale: Scale factor for normalization
        """
        self.grid = grid
        self.window_size = window_size
        self.imprint_strength = imprint_strength
        self.normalization_type = normalization_type
        self.normalization_scale = normalization_scale

        # Accumulator for current window (counts ticks at each position)
        self.accumulator = np.zeros((grid.height, grid.width), dtype=np.float32)

        # Raw history layer (accumulated, NOT decayed)
        self.raw_history = np.zeros((grid.height, grid.width), dtype=np.float32)

        # Normalized history layer (computed on demand)
        self._normalized_cache = None
        self._cache_valid = False

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

        x = int(projectile.center_x + projectile.state.x)
        y = int(projectile.center_y + projectile.state.y)
        size = projectile.pattern_size

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
        Commit accumulated history (no decay, just accumulate).

        Returns:
            Dict with commit statistics
        """
        # Normalize current window contribution
        window_contribution = self.accumulator * (self.imprint_strength / self.window_size)

        # ACCUMULATE without decay (key difference from V8)
        self.raw_history = self.raw_history + window_contribution

        # Invalidate normalized cache
        self._cache_valid = False

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
            "raw_history_max": float(np.max(self.raw_history)),
            "raw_history_mean": float(np.mean(self.raw_history)),
            "raw_history_sum": float(np.sum(self.raw_history)),
        }

    def _compute_normalized_history(self, gamma_base: np.ndarray = None) -> np.ndarray:
        """Compute normalized history based on normalization type.

        Args:
            gamma_base: Base gamma field (needed for 'local_gamma' mode)

        Returns:
            Normalized history array
        """
        if self.normalization_type == 'global_sum':
            # history / (1 + sum(history) / N)
            total = np.sum(self.raw_history)
            norm_factor = 1.0 + total / self.normalization_scale
            return self.raw_history / norm_factor

        elif self.normalization_type == 'time_based':
            # history / (1 + commits)
            norm_factor = 1.0 + self.total_commits
            return self.raw_history / norm_factor

        elif self.normalization_type == 'local_gamma':
            # history / gamma_base
            if gamma_base is None:
                # Fall back to global sum if no gamma provided
                total = np.sum(self.raw_history)
                norm_factor = 1.0 + total / self.normalization_scale
                return self.raw_history / norm_factor
            else:
                # Avoid division by zero
                safe_gamma = np.maximum(gamma_base, 1.0)
                return self.raw_history / safe_gamma

        else:
            raise ValueError(f"Unknown normalization type: {self.normalization_type}")

    def get_history_layer(self, gamma_base: np.ndarray = None) -> np.ndarray:
        """Get the normalized history layer.

        Unlike V8 which returns raw (decayed) history, V10 returns
        normalized history.

        Args:
            gamma_base: Base gamma field (for 'local_gamma' normalization)

        Returns:
            Normalized history layer array
        """
        # For local_gamma mode, we can't cache since gamma_base may change
        if self.normalization_type == 'local_gamma':
            return self._compute_normalized_history(gamma_base)

        # For other modes, use cache
        if not self._cache_valid:
            self._normalized_cache = self._compute_normalized_history()
            self._cache_valid = True

        return self._normalized_cache

    def get_history_contribution(self, x: int, y: int, gamma_base: np.ndarray = None) -> float:
        """
        Get normalized gamma contribution from history at position.

        Args:
            x, y: Grid position
            gamma_base: Base gamma field (for 'local_gamma' normalization)

        Returns:
            Normalized history contribution at this position
        """
        if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
            normalized = self.get_history_layer(gamma_base)
            return float(normalized[y, x])
        return 0.0

    def get_raw_history_layer(self) -> np.ndarray:
        """Get the raw (un-normalized) history layer."""
        return self.raw_history

    def reset(self):
        """Reset both accumulator and history layer."""
        self.accumulator.fill(0)
        self.raw_history.fill(0)
        self._cache_valid = False
        self._normalized_cache = None
        self.ticks_in_window = 0
        self.total_commits = 0

    def get_state(self) -> dict:
        """Get current state for debugging/logging."""
        normalized = self.get_history_layer()
        return {
            "ticks_in_window": self.ticks_in_window,
            "window_size": self.window_size,
            "total_commits": self.total_commits,
            "normalization_type": self.normalization_type,
            "normalization_scale": self.normalization_scale,
            "accumulator_nonzero": int(np.count_nonzero(self.accumulator)),
            "raw_history_max": float(np.max(self.raw_history)),
            "raw_history_mean": float(np.mean(self.raw_history)),
            "raw_history_sum": float(np.sum(self.raw_history)),
            "normalized_max": float(np.max(normalized)),
            "normalized_mean": float(np.mean(normalized)),
            # Effective decay: ratio of normalized to raw
            "effective_norm_factor": float(np.sum(self.raw_history) / max(np.sum(normalized), 1e-10)),
        }

    def __repr__(self) -> str:
        return (
            f"GammaHistoryCommitterV10("
            f"window={self.window_size}, "
            f"k={self.imprint_strength}, "
            f"norm={self.normalization_type}, "
            f"commits={self.total_commits})"
        )


if __name__ == "__main__":
    # Demo
    import sys
    from pathlib import Path
    v6_path = Path(__file__).parent.parent / "v6"
    sys.path.insert(0, str(v6_path))

    from planck_grid import PlanckGrid

    print("GammaHistoryCommitterV10 Demo")
    print("=" * 60)

    # Create grid
    grid = PlanckGrid(50, 50)

    # Test each normalization type
    for norm_type in ['global_sum', 'time_based', 'local_gamma']:
        print(f"\n--- Normalization: {norm_type} ---")

        committer = GammaHistoryCommitterV10(
            grid,
            window_size=10,
            imprint_strength=5.0,
            normalization_type=norm_type,
            normalization_scale=100.0
        )

        class MockPattern:
            class MockSample:
                def __init__(self, cx, cy, size):
                    self.center_x = cx
                    self.center_y = cy
                    self.size = size
            def __init__(self, cx, cy, size=3):
                self.sample = self.MockSample(cx, cy, size)

        pattern = MockPattern(25, 25, 3)

        # Simulate multiple windows
        for window in range(3):
            for tick in range(10):
                committer.record_tick([pattern])
            stats = committer.commit()
            print(f"  Window {window+1}: raw_sum={stats['raw_history_sum']:.1f}, "
                  f"norm_max={committer.get_state()['normalized_max']:.3f}")

    print()
    print("=" * 60)
    print("V10 key difference: History accumulates, normalization applied on use")
