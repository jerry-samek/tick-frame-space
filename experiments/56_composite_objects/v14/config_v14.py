"""
V14 Configuration - Tick Skipping for Time Dilation

Simplifies V13's 10 parameters down to 2:
1. jitter_strength - the ONE constant (push force)
2. gamma_decay - memory persistence (also determines skip sensitivity)

Time dilation emerges from tick skipping:
- Entity in gravitational well (high gamma gradient) must "pay" by skipping ticks
- skip_probability = |gamma_gradient| * sensitivity
- sensitivity = 1 - gamma_decay (derived, not a parameter)

Physical interpretation:
- Gamma well = accumulated memory = gravitational potential
- Pull = gradient of gamma field toward center
- Energy = what entity receives per tick (1, always)
- Tick skipping = entity spends energy to resist falling in

V13 had 6 extra time dilation params: load_diffusion, load_damping, energy_regen,
energy_max, energy_drain_rate, time_dilation_enabled - all REMOVED.

Author: V14 Implementation
Date: 2026-01-31
Based on: V13 + tick skipping simplification
"""


class LayeredSubstrateConfig:
    """Configuration for V14 layered substrate.

    TWO parameters only:
    1. jitter_strength - push force (any value in [0.075, 0.5])
    2. gamma_decay - memory persistence (also sets skip sensitivity)
    """

    # ========================================================================
    # THE TWO PARAMETERS
    # ========================================================================

    # Jitter strength - the push force
    # V12d validated this value: 100k ticks with drift of 0.000604
    DEFAULT_JITTER_STRENGTH = 0.119

    # Gamma decay - memory persistence
    # Also determines skip sensitivity: sensitivity = 1 - gamma_decay
    DEFAULT_GAMMA_DECAY = 0.99

    # ========================================================================
    # Fixed Constants (not tunable)
    # ========================================================================

    # Gamma imprint strength - always 1.0 (one action = one imprint)
    GAMMA_IMPRINT_STRENGTH = 1.0

    # ========================================================================
    # Grid Configuration
    # ========================================================================

    def __init__(
        self,
        grid_size: int = 100,
        jitter_strength: float = None,
        gamma_decay: float = None,
        random_seed: int = 42
    ):
        """Initialize configuration.

        Args:
            grid_size: Grid dimension (width = height)
            jitter_strength: Jitter strength (default: 0.119)
            gamma_decay: Gamma decay rate (default: 0.99)
            random_seed: Random seed for reproducibility
        """
        self.grid_size = grid_size
        self.grid_width = grid_size
        self.grid_height = grid_size
        self._jitter_strength = jitter_strength if jitter_strength is not None else self.DEFAULT_JITTER_STRENGTH
        self._gamma_decay = gamma_decay if gamma_decay is not None else self.DEFAULT_GAMMA_DECAY
        self.random_seed = random_seed

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def jitter_strength(self) -> float:
        """Parameter 1: Jitter strength (push force)."""
        return self._jitter_strength

    @property
    def gamma_decay(self) -> float:
        """Parameter 2: Gamma decay (memory persistence)."""
        return self._gamma_decay

    @property
    def gamma_imprint_strength(self) -> float:
        """Fixed: Always 1.0 (one action = one imprint)."""
        return self.GAMMA_IMPRINT_STRENGTH

    @property
    def skip_sensitivity(self) -> float:
        """Derived: Sensitivity to gamma gradient for tick skipping.

        Higher decay = faster fading = less pull effect = lower sensitivity.
        sensitivity = 1 - gamma_decay
        """
        return 1.0 - self._gamma_decay

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
            f"V14 Layered Substrate Config (grid={self.grid_size})",
            "=" * 60,
            "",
            "THE TWO PARAMETERS:",
            f"  1. jitter_strength = {self.jitter_strength}  (push force)",
            f"  2. gamma_decay = {self.gamma_decay}  (memory persistence)",
            "",
            "DERIVED (not tunable):",
            f"  skip_sensitivity = {self.skip_sensitivity:.4f}  (= 1 - gamma_decay)",
            f"  gamma_imprint_strength = {self.gamma_imprint_strength}  (fixed)",
            "",
            "TIME DILATION:",
            "  Emerges from tick skipping (no extra parameters)",
            "  skip_prob = |gamma_gradient| * skip_sensitivity",
            "  Entity skips tick -> experiences fewer ticks (time dilation)",
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
        return f"LayeredSubstrateConfig(grid={self.grid_size}, jitter={self.jitter_strength}, decay={self.gamma_decay})"


# ========================================================================
# Factory functions
# ========================================================================

def create_config(
    grid_size: int = 100,
    jitter_strength: float = None,
    gamma_decay: float = None,
    random_seed: int = 42
) -> LayeredSubstrateConfig:
    """Create a V14 configuration.

    Args:
        grid_size: Grid dimension
        jitter_strength: Jitter strength (default: 0.119)
        gamma_decay: Gamma decay (default: 0.99)
        random_seed: Random seed

    Returns:
        Configured LayeredSubstrateConfig
    """
    return LayeredSubstrateConfig(
        grid_size=grid_size,
        jitter_strength=jitter_strength,
        gamma_decay=gamma_decay,
        random_seed=random_seed
    )


# ========================================================================
# Preset configurations
# ========================================================================

class SmallConfig(LayeredSubstrateConfig):
    """Small grid for quick tests."""
    def __init__(self, jitter_strength: float = None, gamma_decay: float = None, random_seed: int = 42):
        super().__init__(grid_size=50, jitter_strength=jitter_strength, gamma_decay=gamma_decay, random_seed=random_seed)


class StandardConfig(LayeredSubstrateConfig):
    """Standard grid size."""
    def __init__(self, jitter_strength: float = None, gamma_decay: float = None, random_seed: int = 42):
        super().__init__(grid_size=100, jitter_strength=jitter_strength, gamma_decay=gamma_decay, random_seed=random_seed)


class LargeConfig(LayeredSubstrateConfig):
    """Large grid for detailed analysis."""
    def __init__(self, jitter_strength: float = None, gamma_decay: float = None, random_seed: int = 42):
        super().__init__(grid_size=200, jitter_strength=jitter_strength, gamma_decay=gamma_decay, random_seed=random_seed)


if __name__ == "__main__":
    print("V14 Configuration")
    print("=" * 70)

    config = create_config(grid_size=100)
    print(config.describe())
    print()

    print("Preset configurations:")
    print("-" * 40)

    for name, cls in [("Small", SmallConfig), ("Standard", StandardConfig), ("Large", LargeConfig)]:
        c = cls()
        print(f"{name}: grid={c.grid_size}, jitter={c.jitter_strength}, decay={c.gamma_decay}")

    print()
    print("Parameter comparison with V13:")
    print("-" * 40)
    print("V13: 10 parameters (jitter + gamma + 6 time dilation + pull_strength)")
    print("V14:  2 parameters (jitter + gamma_decay)")
    print("Reduction: 80%")
    print()
    print("=" * 70)
