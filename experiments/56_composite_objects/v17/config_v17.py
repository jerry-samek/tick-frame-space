"""
V17 Configuration - Canvas Ontology with Sparse Storage

Simplified configuration - no grid size needed since space is infinite
and we only store where paint exists.

Physical model (same as V16):
- Entity receives 1 energy per tick
- Entity pays gamma_cost = effective_gamma to maintain memory/presence
- Entity has jitter_budget = 1 - gamma_cost left for movement
- Skip probability = |gradient| * SKIP_SENSITIVITY

New in V17:
- No grid size - sparse storage means infinite space
- No expansion parameters - space is inherently unlimited
- Memory scales with O(painted_cells) not O(grid^3)

Author: V17 Implementation
Date: 2026-02-01
Based on: V16 config - simplified for sparse storage
"""


class Config17:
    """Configuration for V17 canvas ontology - zero tunable parameters.

    All behavior emerges from the energy budget model:
    - jitter = 1 - effective_gamma (derived)
    - skip_prob = |gradient| * SKIP_SENSITIVITY (fixed)

    No grid size needed - space is infinite, we only store paint.
    """

    # ========================================================================
    # FIXED CONSTANTS (not tunable) - same as V15/V16
    # ========================================================================

    # Skip sensitivity - probability per unit gradient
    # Higher = more time dilation near gamma concentrations
    SKIP_SENSITIVITY = 0.01

    # Jitter strength - probability of random step when gradient ~0
    # Used when no significant gradient to follow
    JITTER_STRENGTH = 1


    # Gradient threshold - below this magnitude, use jitter instead of gradient
    # Prevents noise from causing erratic movement
    GRADIENT_THRESHOLD = 0.01

    # Gamma imprint strength - one action = one imprint
    GAMMA_IMPRINT = 1.0

    # Energy per tick - entity receives this much energy each tick
    ENERGY_PER_TICK = 1.0

    # Number of dimensions
    DIMENSIONS = 3

    # Radius for local gamma sampling (effective_gamma calculation)
    LOCAL_RADIUS = 3

    # ========================================================================
    # Experiment Parameters (observational, not physics)
    # ========================================================================

    def __init__(
        self,
        max_ticks: int = 1000,
        max_memory_mb: float = 2000.0,
        random_seed: int = 42
    ):
        """Initialize V17 configuration.

        Args:
            max_ticks: Maximum ticks to run (hard limit for experiment)
            max_memory_mb: Maximum memory usage in MB (safety limit)
            random_seed: Random seed for reproducibility
        """
        self.max_ticks = max_ticks
        self.max_memory_mb = max_memory_mb
        self.random_seed = random_seed

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def skip_sensitivity(self) -> float:
        """Fixed skip sensitivity constant."""
        return self.SKIP_SENSITIVITY

    @property
    def jitter_strength(self) -> float:
        """Fixed jitter strength when gradient is near zero."""
        return self.JITTER_STRENGTH

    @property
    def gradient_threshold(self) -> float:
        """Threshold below which gradient is considered zero."""
        return self.GRADIENT_THRESHOLD

    @property
    def gamma_imprint(self) -> float:
        """Fixed gamma imprint strength."""
        return self.GAMMA_IMPRINT

    @property
    def energy_per_tick(self) -> float:
        """Fixed energy per tick."""
        return self.ENERGY_PER_TICK

    @property
    def local_radius(self) -> int:
        """Radius for local gamma sampling."""
        return self.LOCAL_RADIUS

    # ========================================================================
    # Memory Estimation
    # ========================================================================

    def estimate_memory_at_tick(self, tick: int, avg_paint_per_entity: float = 10.0) -> float:
        """Estimate memory usage at a given tick (in MB).

        Memory = painted_cells * (key_size + value_size)
        Key: 3 ints (24 bytes for tuple overhead + 3*8 bytes) ≈ 48 bytes
        Value: 1 float64 = 8 bytes
        Total per cell ≈ 56 bytes (plus dict overhead ≈ 100 bytes per entry)

        Args:
            tick: Tick number
            avg_paint_per_entity: Average cells painted per entity (estimate)

        Returns:
            Estimated memory in MB
        """
        num_entities = tick
        estimated_cells = num_entities * avg_paint_per_entity

        # Dict overhead: approximately 100 bytes per entry (key + value + pointers)
        bytes_per_cell = 100

        total_bytes = estimated_cells * bytes_per_cell
        return total_bytes / (1024 * 1024)

    # ========================================================================
    # Description
    # ========================================================================

    def describe(self) -> str:
        """Human-readable description of configuration."""
        lines = [
            "V17 Canvas Ontology with Sparse Storage",
            "=" * 60,
            "",
            "ZERO TUNABLE PARAMETERS (same as V15/V16)",
            "",
            "FIXED CONSTANTS:",
            f"  SKIP_SENSITIVITY = {self.SKIP_SENSITIVITY}  (skip prob per unit gradient)",
            f"  JITTER_STRENGTH = {self.JITTER_STRENGTH}  (random step prob when gradient ~0)",
            f"  GRADIENT_THRESHOLD = {self.GRADIENT_THRESHOLD}  (below this, use jitter)",
            f"  GAMMA_IMPRINT = {self.GAMMA_IMPRINT}  (one action = one imprint)",
            f"  ENERGY_PER_TICK = {self.ENERGY_PER_TICK}  (entity receives 1 energy/tick)",
            f"  LOCAL_RADIUS = {self.LOCAL_RADIUS}  (for effective_gamma sampling)",
            "",
            "MOVEMENT MODEL:",
            "  1. Gradient pulls renderer toward higher gamma (like gravity)",
            "  2. Skip probability = |gradient| * SKIP_SENSITIVITY (resistance)",
            "  3. If gradient > threshold: move in gradient direction",
            "  4. If gradient ~0: small random jitter with JITTER_STRENGTH",
            "",
            "SPARSE STORAGE (NEW IN V17):",
            "  - No grid size - space is infinite",
            "  - Only painted cells stored in dict",
            "  - Memory scales with O(painted_cells)",
            "",
            "EXPERIMENT PARAMETERS (observational):",
            f"  max_ticks = {self.max_ticks}",
            f"  max_memory_mb = {self.max_memory_mb} MB",
            "",
            "ESTIMATED MEMORY:",
            f"  At tick 100: ~{self.estimate_memory_at_tick(100):.1f} MB",
            f"  At tick 1000: ~{self.estimate_memory_at_tick(1000):.1f} MB",
            f"  At tick 10000: ~{self.estimate_memory_at_tick(10000):.1f} MB",
            "",
            "CANVAS ONTOLOGY:",
            "  Renderer = Stateless head (decides where to paint)",
            "  Canvas = Accumulated paint (gamma field)",
            "  Tick = Renderer reads canvas, paints new position",
            "",
            f"  random_seed = {self.random_seed}",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"Config17(max_ticks={self.max_ticks}, "
            f"max_memory_mb={self.max_memory_mb}, "
            f"seed={self.random_seed})"
        )


# ========================================================================
# Preset configurations
# ========================================================================

class QuickTestConfig(Config17):
    """Quick test: 100 ticks."""
    def __init__(self, random_seed: int = 42):
        super().__init__(
            max_ticks=100,
            max_memory_mb=500.0,
            random_seed=random_seed
        )


class StandardConfig(Config17):
    """Standard experiment: 1000 ticks."""
    def __init__(self, random_seed: int = 42):
        super().__init__(
            max_ticks=1000,
            max_memory_mb=2000.0,
            random_seed=random_seed
        )


class LongRunConfig(Config17):
    """Long run: 10000 ticks."""
    def __init__(self, random_seed: int = 42):
        super().__init__(
            max_ticks=10000,
            max_memory_mb=4000.0,
            random_seed=random_seed
        )


if __name__ == "__main__":
    print("V17 Configuration")
    print("=" * 70)

    config = Config17()
    print(config.describe())
    print()

    print("Preset configurations:")
    print("-" * 40)

    for name, cls in [("QuickTest", QuickTestConfig), ("Standard", StandardConfig), ("LongRun", LongRunConfig)]:
        c = cls()
        print(f"{name}: max_ticks={c.max_ticks}, max_memory={c.max_memory_mb} MB")
        print(f"  Estimated memory at max_ticks: {c.estimate_memory_at_tick(c.max_ticks):.1f} MB")
        print()

    print("=" * 70)
