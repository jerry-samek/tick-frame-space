"""
V16 Configuration - Expanding Grid Zero-Parameter Model

Extends V15-3D configuration with expansion parameters.

Physical model (same as V15-3D):
- Entity receives 1 energy per tick
- Entity pays gamma_cost = effective_gamma to maintain memory/presence
- Entity has jitter_budget = 1 - gamma_cost left for movement
- Skip probability = |gradient| * SKIP_SENSITIVITY

New in V16:
- Grid expands over time (space expansion)
- Memory monitoring for safety
- Initial size starts smaller, grows to large

Author: V16 Implementation
Date: 2026-02-01
Based on: V15-3D config + expansion parameters
"""


class SubstrateConfig16:
    """Configuration for V16 expanding substrate - zero tunable parameters.

    All behavior emerges from the energy budget model:
    - jitter = 1 - effective_gamma (derived)
    - skip_prob = |gradient| * SKIP_SENSITIVITY (fixed)

    Expansion mechanics are observational parameters, not physics tuning.
    """

    # ========================================================================
    # FIXED CONSTANTS (not tunable) - same as V15
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
    # Expansion Parameters (observational, not physics)
    # ========================================================================

    def __init__(
        self,
        initial_size: int = 20,
        expansion_rate: int = 5,
        max_memory_mb: float = 2000.0,
        max_ticks: int = 500,
        random_seed: int = 42
    ):
        """Initialize V16 configuration.

        Args:
            initial_size: Starting grid dimension (initial_size^3 cells)
            expansion_rate: Expand grid every N ticks
            max_memory_mb: Maximum memory usage in MB (safety limit)
            max_ticks: Maximum ticks to run (hard limit for experiment)
            random_seed: Random seed for reproducibility
        """
        self.initial_size = initial_size
        self.expansion_rate = expansion_rate
        self.max_memory_mb = max_memory_mb
        self.max_ticks = max_ticks
        self.random_seed = random_seed

        # Current grid size (will change during simulation)
        self._current_size = initial_size

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
    def creation_rate(self) -> int:
        """Entities created per tick (always 1)."""
        return 1

    # ========================================================================
    # Expansion Calculations
    # ========================================================================

    def get_size_at_tick(self, tick: int) -> int:
        """Calculate expected grid size at a given tick.

        Grid expands by 2 cells (1 on each side) every expansion_rate ticks.

        Args:
            tick: Tick number

        Returns:
            Expected grid size
        """
        if tick <= 0:
            return self.initial_size
        expansions = tick // self.expansion_rate
        return self.initial_size + (expansions * 2)

    def estimate_memory_at_tick(self, tick: int) -> float:
        """Estimate memory usage at a given tick (in MB).

        Memory = gamma (float64) + layers (int8 each)

        Args:
            tick: Tick number

        Returns:
            Estimated memory in MB
        """
        size = self.get_size_at_tick(tick)
        num_cells = size ** 3

        # Gamma field: float64 = 8 bytes per cell
        gamma_bytes = num_cells * 8

        # Entity layers: int8 = 1 byte per cell, one layer per tick
        num_entities = tick
        layer_bytes = num_cells * num_entities

        total_bytes = gamma_bytes + layer_bytes
        return total_bytes / (1024 * 1024)

    # ========================================================================
    # Description
    # ========================================================================

    def describe(self) -> str:
        """Human-readable description of configuration."""
        lines = [
            f"V16 Expanding Grid Zero-Parameter Config",
            "=" * 60,
            "",
            "ZERO TUNABLE PARAMETERS (same as V15)",
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
            "EXPANSION PARAMETERS (observational):",
            f"  initial_size = {self.initial_size}^3 = {self.initial_size**3:,} cells",
            f"  expansion_rate = every {self.expansion_rate} ticks",
            f"  max_memory_mb = {self.max_memory_mb} MB",
            f"  max_ticks = {self.max_ticks}",
            "",
            "EXPANSION SCHEDULE:",
            f"  Tick 0: {self.get_size_at_tick(0)}^3 = {self.get_size_at_tick(0)**3:,} cells",
            f"  Tick 100: {self.get_size_at_tick(100)}^3 = {self.get_size_at_tick(100)**3:,} cells",
            f"  Tick 250: {self.get_size_at_tick(250)}^3 = {self.get_size_at_tick(250)**3:,} cells",
            f"  Tick 500: {self.get_size_at_tick(500)}^3 = {self.get_size_at_tick(500)**3:,} cells",
            "",
            "ESTIMATED MEMORY:",
            f"  At tick 100: ~{self.estimate_memory_at_tick(100):.1f} MB",
            f"  At tick 250: ~{self.estimate_memory_at_tick(250):.1f} MB",
            f"  At tick 500: ~{self.estimate_memory_at_tick(500):.1f} MB",
            "",
            "PHYSICAL MODEL:",
            "  Entity receives: 1.0 energy per tick",
            "  Entity pays: gamma_cost = effective_gamma (to maintain memory)",
            "  Entity has left: jitter = 1.0 - effective_gamma (for movement)",
            "  Space expands: grid grows every expansion_rate ticks",
            "",
            f"  random_seed = {self.random_seed}",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"SubstrateConfig16(initial={self.initial_size}^3, "
            f"expansion_rate={self.expansion_rate}, "
            f"max_ticks={self.max_ticks}, "
            f"seed={self.random_seed})"
        )


# ========================================================================
# Factory functions
# ========================================================================

def create_config(
    initial_size: int = 20,
    expansion_rate: int = 5,
    max_memory_mb: float = 2000.0,
    max_ticks: int = 500,
    random_seed: int = 42
) -> SubstrateConfig16:
    """Create a V16 configuration.

    Args:
        initial_size: Starting grid dimension (default 20)
        expansion_rate: Expand every N ticks (default 5)
        max_memory_mb: Memory limit in MB (default 2000)
        max_ticks: Maximum ticks (default 500)
        random_seed: Random seed

    Returns:
        Configured SubstrateConfig16
    """
    return SubstrateConfig16(
        initial_size=initial_size,
        expansion_rate=expansion_rate,
        max_memory_mb=max_memory_mb,
        max_ticks=max_ticks,
        random_seed=random_seed
    )


# ========================================================================
# Preset configurations
# ========================================================================

class QuickTestConfig(SubstrateConfig16):
    """Quick test: 100 ticks, smaller memory budget."""
    def __init__(self, random_seed: int = 42):
        super().__init__(
            initial_size=15,
            expansion_rate=5,
            max_memory_mb=500.0,
            max_ticks=100,
            random_seed=random_seed
        )


class StandardConfig(SubstrateConfig16):
    """Standard experiment: 500 ticks."""
    def __init__(self, random_seed: int = 42):
        super().__init__(
            initial_size=20,
            expansion_rate=5,
            max_memory_mb=2000.0,
            max_ticks=500,
            random_seed=random_seed
        )


class LongRunConfig(SubstrateConfig16):
    """Long run: 1000 ticks with larger memory budget."""
    def __init__(self, random_seed: int = 42):
        super().__init__(
            initial_size=20,
            expansion_rate=10,  # Slower expansion for longer runs
            max_memory_mb=4000.0,
            max_ticks=1000,
            random_seed=random_seed
        )


if __name__ == "__main__":
    print("V16 Configuration")
    print("=" * 70)

    config = create_config()
    print(config.describe())
    print()

    print("Preset configurations:")
    print("-" * 40)

    for name, cls in [("QuickTest", QuickTestConfig), ("Standard", StandardConfig), ("LongRun", LongRunConfig)]:
        c = cls()
        print(f"{name}: initial={c.initial_size}^3, rate={c.expansion_rate}, max_ticks={c.max_ticks}")
        print(f"  Final size at max_ticks: {c.get_size_at_tick(c.max_ticks)}^3")
        print(f"  Estimated final memory: {c.estimate_memory_at_tick(c.max_ticks):.1f} MB")
        print()

    print("=" * 70)
