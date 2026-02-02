"""
V15 Configuration - Zero Tunable Parameters

Eliminates the 2 remaining parameters from V14:
- jitter_strength: REMOVED (derived from local gamma)
- gamma_decay: REMOVED (gamma accumulates forever, use relative values)

Physical model:
- Entity receives 1 energy per tick
- Entity pays gamma_cost = effective_gamma to maintain memory/presence
- Entity has jitter_budget = 1 - gamma_cost left for movement
- Skip probability = |gradient| * SKIP_SENSITIVITY

Behavior by region:
| Region         | Gamma_eff | Jitter | Skip Prob | Behavior           |
|----------------|-----------|--------|-----------|-------------------|
| Origin (dense) | ~1.0      | ~0.0   | High      | Frozen, time-dilated |
| Mid-range      | ~0.5      | ~0.5   | Medium    | Balanced           |
| Edge (sparse)  | ~0.0      | ~1.0   | Low       | Mobile, normal time |

Author: V15 Implementation
Date: 2026-01-31
Based on: V14 config simplified
"""


class SubstrateConfig:
    """Configuration for V15 substrate - zero tunable parameters.

    All behavior emerges from the energy budget model:
    - jitter = 1 - effective_gamma (derived)
    - skip_prob = |gradient| * SKIP_SENSITIVITY (fixed)
    """

    # ========================================================================
    # FIXED CONSTANTS (not tunable)
    # ========================================================================

    # Skip sensitivity - probability per unit gradient
    # TODO (V16?): Derive from something fundamental
    SKIP_SENSITIVITY = 0.01

    # Gamma imprint strength - one action = one imprint
    GAMMA_IMPRINT = 1.0

    # Energy per tick - entity receives this much energy each tick
    ENERGY_PER_TICK = 1.0

    # ========================================================================
    # Grid Configuration
    # ========================================================================

    def __init__(
        self,
        grid_size: int = 100,
        random_seed: int = 42
    ):
        """Initialize configuration.

        Args:
            grid_size: Grid dimension (width = height)
            random_seed: Random seed for reproducibility
        """
        self.grid_size = grid_size
        self.grid_width = grid_size
        self.grid_height = grid_size
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
        """Origin position where all entities spawn."""
        return (self.grid_width // 2, self.grid_height // 2)

    @property
    def creation_rate(self) -> int:
        """Entities created per tick (always 1)."""
        return 1

    # ========================================================================
    # Description
    # ========================================================================

    def describe(self) -> str:
        """Human-readable description of configuration."""
        lines = [
            f"V15 Zero-Parameter Substrate Config (grid={self.grid_size})",
            "=" * 60,
            "",
            "ZERO TUNABLE PARAMETERS",
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
            f"  size = {self.grid_width} x {self.grid_height}",
            f"  random_seed = {self.random_seed}",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"SubstrateConfig(grid={self.grid_size}, seed={self.random_seed})"


# ========================================================================
# Factory functions
# ========================================================================

def create_config(
    grid_size: int = 100,
    random_seed: int = 42
) -> SubstrateConfig:
    """Create a V15 configuration.

    Args:
        grid_size: Grid dimension
        random_seed: Random seed

    Returns:
        Configured SubstrateConfig
    """
    return SubstrateConfig(
        grid_size=grid_size,
        random_seed=random_seed
    )


# ========================================================================
# Preset configurations
# ========================================================================

class SmallConfig(SubstrateConfig):
    """Small grid for quick tests."""
    def __init__(self, random_seed: int = 42):
        super().__init__(grid_size=50, random_seed=random_seed)


class StandardConfig(SubstrateConfig):
    """Standard grid size."""
    def __init__(self, random_seed: int = 42):
        super().__init__(grid_size=100, random_seed=random_seed)


class LargeConfig(SubstrateConfig):
    """Large grid for detailed analysis."""
    def __init__(self, random_seed: int = 42):
        super().__init__(grid_size=200, random_seed=random_seed)


if __name__ == "__main__":
    print("V15 Configuration")
    print("=" * 70)

    config = create_config(grid_size=100)
    print(config.describe())
    print()

    print("Preset configurations:")
    print("-" * 40)

    for name, cls in [("Small", SmallConfig), ("Standard", StandardConfig), ("Large", LargeConfig)]:
        c = cls()
        print(f"{name}: grid={c.grid_size}")

    print()
    print("Parameter comparison:")
    print("-" * 40)
    print("V13: 10 parameters")
    print("V14:  2 parameters (jitter + gamma_decay)")
    print("V15:  0 parameters (all derived or fixed)")
    print("Total reduction: 100%")
    print()
    print("=" * 70)
