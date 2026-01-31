"""
Planck-Level Jitter - Quantum Random Walk on Discrete Grid

Each Planck cell receives ±1 jitter per tick with configurable probability.
This implements the zero-point quantum fluctuation at the Planck scale.

Author: V6 Grid-Based Implementation
Date: 2026-01-24
Based on: ONTOLOGY.md (1 quantum jitter per cell per tick)
"""

import numpy as np
from planck_grid import PlanckGrid


class PlanckJitter:
    """Apply integer jitter at the Planck cell level."""

    def __init__(
        self,
        p_negative: float = 0.25,
        p_zero: float = 0.50,
        p_positive: float = 0.25,
        seed: int = 42
    ):
        """
        Initialize Planck-level jitter.

        Args:
            p_negative: Probability of -1 jitter
            p_zero: Probability of 0 jitter (no change)
            p_positive: Probability of +1 jitter
            seed: Random seed for reproducibility
        """
        if not np.isclose(p_negative + p_zero + p_positive, 1.0):
            raise ValueError("Probabilities must sum to 1.0")

        self.p_negative = p_negative
        self.p_zero = p_zero
        self.p_positive = p_positive
        self.rng = np.random.default_rng(seed)

        # Precompute expected statistics
        self.expected_mean = p_positive - p_negative
        self.expected_variance = p_negative + p_positive - self.expected_mean**2

    def apply_jitter(self, grid: PlanckGrid):
        """
        Apply jitter to all Planck cells in grid.

        Each cell receives ±1 with specified probabilities.
        Results are clamped to {-1, 0, +1}.

        Args:
            grid: PlanckGrid to apply jitter to (modified in-place)
        """
        # Generate jitter for entire grid
        jitter = self.rng.choice(
            [-1, 0, 1],
            size=grid.field.shape,
            p=[self.p_negative, self.p_zero, self.p_positive]
        )

        # Apply jitter with clamping to {-1, 0, +1}
        grid.field = np.clip(grid.field + jitter, -1, 1).astype(np.int8)

    def compute_statistics(self, n_samples: int = 10000) -> dict:
        """
        Compute statistical properties of jitter distribution.

        Args:
            n_samples: Number of samples for statistics

        Returns:
            Dict with mean, variance, and distribution counts
        """
        samples = self.rng.choice(
            [-1, 0, 1],
            size=n_samples,
            p=[self.p_negative, self.p_zero, self.p_positive]
        )

        unique, counts = np.unique(samples, return_counts=True)
        count_map = dict(zip(unique, counts))

        return {
            "mean": float(np.mean(samples)),
            "variance": float(np.var(samples)),
            "std": float(np.std(samples)),
            "expected_mean": self.expected_mean,
            "expected_variance": self.expected_variance,
            "n_negative": count_map.get(-1, 0),
            "n_zero": count_map.get(0, 0),
            "n_positive": count_map.get(1, 0),
            "total_samples": n_samples,
        }

    @classmethod
    def create_symmetric(cls, jitter_strength: float = 0.25, seed: int = 42):
        """
        Create symmetric jitter (p_negative = p_positive).

        Args:
            jitter_strength: Probability of ±1 jitter (0.0 to 0.5)
                p_negative = p_positive = jitter_strength
                p_zero = 1 - 2*jitter_strength
            seed: Random seed

        Returns:
            PlanckJitter instance
        """
        if not (0.0 <= jitter_strength <= 0.5):
            raise ValueError("jitter_strength must be in [0.0, 0.5]")

        return cls(
            p_negative=jitter_strength,
            p_zero=1.0 - 2.0 * jitter_strength,
            p_positive=jitter_strength,
            seed=seed
        )

    @classmethod
    def create_from_v4_parameters(cls, jitter_v4: float = 0.0005, pattern_size: int = 5, seed: int = 42):
        """
        Create jitter calibrated to match V4 diffusion rate.

        From STRUCTURE.md:
            J_planck = J_float / A_pattern

        For V4: jitter_strength = 0.0005, pattern area = 25 (5x5)
            J_planck = 0.0005 / 25 = 0.00002 per cell

        But in discrete model, we need to map this to probability:
            For symmetric jitter: p(±1) should produce equivalent diffusion

        This is an approximation - may need experimental tuning.

        Args:
            jitter_v4: V4 jitter strength (velocity kick magnitude)
            pattern_size: Sample cell size (5 for 5x5)
            seed: Random seed

        Returns:
            PlanckJitter instance
        """
        pattern_area = pattern_size ** 2
        jitter_per_cell = jitter_v4 / pattern_area

        # Map to probability (experimental - may need tuning)
        # For now, use jitter_per_cell directly as probability
        # (this gives very weak jitter, which matches V4's scale)
        jitter_strength = min(0.5, jitter_per_cell * 1000)  # Scale up for visibility

        return cls.create_symmetric(jitter_strength, seed)

    def __repr__(self) -> str:
        return (
            f"PlanckJitter(p_neg={self.p_negative:.3f}, "
            f"p_zero={self.p_zero:.3f}, "
            f"p_pos={self.p_positive:.3f}, "
            f"E[X]={self.expected_mean:.3f}, "
            f"Var[X]={self.expected_variance:.3f})"
        )


if __name__ == "__main__":
    # Demo
    print("PlanckJitter Demo")
    print("=" * 70)

    # Create jitter with default parameters
    jitter = PlanckJitter.create_symmetric(jitter_strength=0.25)
    print(f"Jitter: {jitter}")
    print()

    # Compute statistics
    stats = jitter.compute_statistics(n_samples=100000)
    print("Statistical validation (100k samples):")
    print(f"  Mean: {stats['mean']:.6f} (expected: {stats['expected_mean']:.6f})")
    print(f"  Variance: {stats['variance']:.6f} (expected: {stats['expected_variance']:.6f})")
    print(f"  Std dev: {stats['std']:.6f}")
    print()
    print(f"  Distribution:")
    print(f"    -1: {stats['n_negative']:6d} ({stats['n_negative']/stats['total_samples']*100:.2f}%)")
    print(f"     0: {stats['n_zero']:6d} ({stats['n_zero']/stats['total_samples']*100:.2f}%)")
    print(f"    +1: {stats['n_positive']:6d} ({stats['n_positive']/stats['total_samples']*100:.2f}%)")
    print()

    # Test on small grid
    grid = PlanckGrid(20, 20)
    print(f"Grid before jitter: {grid}")
    print()

    # Apply jitter for 100 ticks
    print("Applying jitter for 100 ticks...")
    for tick in range(100):
        jitter.apply_jitter(grid)

    print(f"Grid after 100 ticks: {grid}")
    print()

    stats_after = grid.get_field_statistics()
    print("Field statistics after 100 ticks:")
    print(f"  Negative cells: {stats_after['n_negative']}")
    print(f"  Zero cells: {stats_after['n_zero']}")
    print(f"  Positive cells: {stats_after['n_positive']}")
    print(f"  Total energy: {stats_after['total_energy']}")
    print(f"  Nonzero fraction: {stats_after['nonzero_fraction']:.1%}")
    print()

    # Visualize final state
    from planck_grid import visualize_grid_ascii
    print("Final grid state (20x20):")
    print(visualize_grid_ascii(grid, 0, 0, 20, 20))
    print()

    # Test V4 equivalence
    print("=" * 70)
    print("V4 Equivalence Test")
    print("=" * 70)
    jitter_v4 = PlanckJitter.create_from_v4_parameters(jitter_v4=0.0005, pattern_size=5)
    print(f"V4-calibrated jitter: {jitter_v4}")
    stats_v4 = jitter_v4.compute_statistics(n_samples=100000)
    print(f"  Mean: {stats_v4['mean']:.6f}")
    print(f"  Variance: {stats_v4['variance']:.6f}")
    print()

    print("=" * 70)
