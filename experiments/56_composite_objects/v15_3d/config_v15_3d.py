"""
V15-3D Configuration - Zero Tunable Parameters in 3D

Extends V15 (2D) to 3D while keeping zero tunable parameters.

Key differences from 2D:
- Grid is 3D: (depth, height, width)
- Smaller default size (30^3 = 27k cells vs 100² = 10k cells)
- Origin is 3D: (x, y, z)

Physical model (same as V15 2D):
- Entity receives 1 energy per tick
- Entity pays gamma_cost = effective_gamma to maintain memory/presence
- Entity has jitter_budget = 1 - gamma_cost left for movement
- Skip probability = |gradient| * SKIP_SENSITIVITY

Author: V15-3D Implementation
Date: 2026-02-01
Based on: V15 config + 3D extensions
"""


class SubstrateConfig3D:
    """Configuration for V15-3D substrate - zero tunable parameters.

    All behavior emerges from the energy budget model:
    - jitter = 1 - effective_gamma (derived)
    - skip_prob = |gradient| * SKIP_SENSITIVITY (fixed)
    """

    # ========================================================================
    # FIXED CONSTANTS (not tunable) - same as V15 2D
    # ========================================================================

    # Skip sensitivity - probability per unit gradient
    SKIP_SENSITIVITY = 0.01

    # Gamma imprint strength - one action = one imprint
    GAMMA_IMPRINT = 1.0

    # Energy per tick - entity receives this much energy each tick
    ENERGY_PER_TICK = 1.0

    # Number of dimensions
    DIMENSIONS = 3

    # ========================================================================
    # Grid Configuration
    # ========================================================================

    def __init__(
        self,
        grid_size: int = 30,
        random_seed: int = 42
    ):
        """Initialize 3D configuration.

        Args:
            grid_size: Grid dimension (depth = height = width)
            random_seed: Random seed for reproducibility

        Note: Default grid_size is 30 (30^3 = 27k cells) vs 100 in 2D (10k cells)
              This keeps memory usage comparable while enabling 3D dynamics.
        """
        self.grid_size = grid_size
        self.grid_depth = grid_size
        self.grid_height = grid_size
        self.grid_width = grid_size
        self.random_seed = random_seed

        # NO jitter_strength parameter
        # NO gamma_decay parameter

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def skip_sensitivity(self) -> float:
        """Fixed skip sensitivity constant."""
        return self.SKIP_SENSITIVITY

    @property
    def gamma_imprint(self) -> float:
        """Fixed gamma imprint strength."""
        return self.GAMMA_IMPRINT

    @property
    def energy_per_tick(self) -> float:
        """Fixed energy per tick."""
        return self.ENERGY_PER_TICK

    @property
    def origin(self) -> tuple:
        """Origin position where all entities spawn (3D center)."""
        c = self.grid_size // 2
        return (c, c, c)  # (x, y, z)

    @property
    def creation_rate(self) -> int:
        """Entities created per tick (always 1)."""
        return 1

    @property
    def total_cells(self) -> int:
        """Total number of cells in the 3D grid."""
        return self.grid_depth * self.grid_height * self.grid_width

    # ========================================================================
    # Description
    # ========================================================================

    def describe(self) -> str:
        """Human-readable description of configuration."""
        lines = [
            f"V15-3D Zero-Parameter Substrate Config (grid={self.grid_size}^3)",
            "=" * 60,
            "",
            "ZERO TUNABLE PARAMETERS (same as V15 2D)",
            "",
            "FIXED CONSTANTS:",
            f"  SKIP_SENSITIVITY = {self.SKIP_SENSITIVITY}  (fixed)",
            f"  GAMMA_IMPRINT = {self.GAMMA_IMPRINT}  (one action = one imprint)",
            f"  ENERGY_PER_TICK = {self.ENERGY_PER_TICK}  (entity receives 1 energy/tick)",
            "",
            "DERIVED BEHAVIOR:",
            "  effective_gamma = (gamma - min) / (max - min)  [0, 1]",
            "  jitter_strength = 1 - effective_gamma  (energy budget leftover)",
            "  skip_prob = |gradient| * SKIP_SENSITIVITY",
            "",
            "3D SPECIFICS:",
            f"  Dimensions = {self.DIMENSIONS}",
            f"  Grid shape = {self.grid_depth} x {self.grid_height} x {self.grid_width}",
            f"  Total cells = {self.total_cells:,}",
            f"  Neighbors = 26 (3^3 - 1)",
            "",
            "PHYSICAL MODEL:",
            "  Entity receives: 1.0 energy per tick",
            "  Entity pays: gamma_cost = effective_gamma (to maintain memory)",
            "  Entity has left: jitter = 1.0 - effective_gamma (for movement)",
            "",
            "BEHAVIOR BY REGION:",
            "  Origin (dense):  gamma_eff ~1.0, jitter ~0.0, time-dilated",
            "  Mid-range:       gamma_eff ~0.5, jitter ~0.5, balanced",
            "  Edge (sparse):   gamma_eff ~0.0, jitter ~1.0, mobile",
            "",
            "SPAWN MECHANICS:",
            f"  origin = {self.origin}",
            f"  creation_rate = {self.creation_rate} entity/tick",
            "",
            "GRID:",
            f"  size = {self.grid_depth} x {self.grid_height} x {self.grid_width}",
            f"  random_seed = {self.random_seed}",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"SubstrateConfig3D(grid={self.grid_size}^3, seed={self.random_seed})"


# ========================================================================
# Factory functions
# ========================================================================

def create_config(
    grid_size: int = 30,
    random_seed: int = 42
) -> SubstrateConfig3D:
    """Create a V15-3D configuration.

    Args:
        grid_size: Grid dimension (default 30 for 3D)
        random_seed: Random seed

    Returns:
        Configured SubstrateConfig3D
    """
    return SubstrateConfig3D(
        grid_size=grid_size,
        random_seed=random_seed
    )


# ========================================================================
# Preset configurations
# ========================================================================

class SmallConfig3D(SubstrateConfig3D):
    """Small 3D grid for quick tests (20^3 = 8k cells)."""
    def __init__(self, random_seed: int = 42):
        super().__init__(grid_size=20, random_seed=random_seed)


class StandardConfig3D(SubstrateConfig3D):
    """Standard 3D grid size (30^3 = 27k cells)."""
    def __init__(self, random_seed: int = 42):
        super().__init__(grid_size=30, random_seed=random_seed)


class LargeConfig3D(SubstrateConfig3D):
    """Large 3D grid for detailed analysis (40^3 = 64k cells)."""
    def __init__(self, random_seed: int = 42):
        super().__init__(grid_size=40, random_seed=random_seed)


if __name__ == "__main__":
    print("V15-3D Configuration")
    print("=" * 70)

    config = create_config(grid_size=30)
    print(config.describe())
    print()

    print("Preset configurations:")
    print("-" * 40)

    for name, cls in [("Small", SmallConfig3D), ("Standard", StandardConfig3D), ("Large", LargeConfig3D)]:
        c = cls()
        print(f"{name}: grid={c.grid_size}^3 = {c.total_cells:,} cells")

    print()
    print("Comparison with V15 2D:")
    print("-" * 40)
    print("V15 2D:  100^2 = 10,000 cells,  8 neighbors")
    print("V15-3D:   30^3 = 27,000 cells, 26 neighbors")
    print()
    print("Theory prediction:")
    print("  2D variance: 22%")
    print("  3D variance:  5% (Goldilocks dimension)")
    print()
    print("=" * 70)
