"""
V13 Configuration - Layered Substrate with Shared Memory

Key principles:
- Jitter (0.119) is the ONE constant (from V12d)
- Entities spawn at origin only (head prepending)
- Creation rate: 1 entity per tick
- Gamma field is shared memory (all entities contribute)
- Layers are isolated (each entity has its own layer)

Pull/Push model:
- Gamma = Pull (memory attracts)
- Jitter = Push (back-pressure compensates)
- Pattern = where forces balance

Time Dilation (Experiment 51 integration):
- Added reaction-diffusion load/energy fields
- Spatially-varying gamma decay based on energy depletion
- Result: Time dilation works - gamma persists 2.5x longer in dense regions
- Parameters added: load_diffusion, load_damping, energy_regen, energy_max,
  energy_drain_rate, time_dilation_enabled (6 total)
- NOTE: Superseded by V14 tick skipping approach (0 new parameters)

Author: V13 Implementation
Date: 2026-01-31
Based on: V12d substrate config + layered architecture
"""


class LayeredSubstrateConfig:
    """Configuration for V13 layered substrate.

    Minimal configuration - only the ONE constant plus grid size.
    """

    # ========================================================================
    # THE ONE CONSTANT (default value)
    # ========================================================================

    # Jitter strength - the only tunable parameter
    # V12d validated this value: 100k ticks with drift of 0.000604
    # Now configurable to investigate if it's truly fundamental
    DEFAULT_JITTER_STRENGTH = 0.119

    # ========================================================================
    # Grid Configuration
    # ========================================================================

    def __init__(self, grid_size: int = 100, jitter_strength: float = None, random_seed: int = 42):
        """Initialize configuration.

        Args:
            grid_size: Grid dimension (width = height)
            jitter_strength: Jitter strength (default: 0.119). Set to investigate
                            if jitter is fundamental (0 or 1) or emergent.
            random_seed: Random seed for reproducibility
        """
        self.grid_size = grid_size
        self.grid_width = grid_size
        self.grid_height = grid_size
        self._jitter_strength = jitter_strength if jitter_strength is not None else self.DEFAULT_JITTER_STRENGTH
        self.random_seed = random_seed

    # ========================================================================
    # Derived Properties
    # ========================================================================

    @property
    def jitter_strength(self) -> float:
        """The ONE constant: jitter strength (now configurable for investigation)."""
        return self._jitter_strength

    @property
    def origin(self) -> tuple:
        """Origin position where all entities spawn."""
        return (self.grid_width // 2, self.grid_height // 2)

    @property
    def creation_rate(self) -> int:
        """Entities created per tick (always 1)."""
        return 1

    # ========================================================================
    # Gamma Field Parameters
    # ========================================================================

    # Gamma decay - how quickly memory fades
    # Set to 0.99 for slow decay (95% retained per tick)
    gamma_decay: float = 0.99

    # Gamma imprint strength - how strongly presence imprints
    # Higher = stronger memory
    gamma_imprint_strength: float = 1.0

    # ========================================================================
    # Pull/Push Model Parameters
    # ========================================================================

    # Pull strength - how strongly gamma gradient affects evolution
    # This determines the "temperature" of the pattern
    pull_strength: float = 0.1

    # ========================================================================
    # Time Dilation Parameters (from Experiment 51v9 Goldilocks)
    # ========================================================================

    # Load diffusion - how load spreads spatially (alpha in reaction-diffusion)
    load_diffusion: float = 0.012

    # Load damping - nonlinear decay term (gamma_damp * L^2)
    load_damping: float = 0.0005

    # Energy regeneration rate - capacity recovery per tick
    energy_regen: float = 1.2

    # Maximum energy capacity
    energy_max: float = 15.0

    # Energy drain rate - how load depletes energy (D in dE/dt = R - D*L)
    energy_drain_rate: float = 0.1

    # Enable time dilation (can be disabled for baseline comparison)
    time_dilation_enabled: bool = True

    # ========================================================================
    # Description
    # ========================================================================

    def describe(self) -> str:
        """Human-readable description of configuration."""
        lines = [
            f"V13 Layered Substrate Config (grid={self.grid_size})",
            "=" * 60,
            "",
            "THE ONE CONSTANT:",
            f"  jitter_strength = {self.jitter_strength}",
            "",
            "SPAWN MECHANICS:",
            f"  origin = {self.origin}",
            f"  creation_rate = {self.creation_rate} entity/tick",
            "",
            "GAMMA FIELD (shared memory):",
            f"  gamma_decay = {self.gamma_decay}",
            f"  gamma_imprint_strength = {self.gamma_imprint_strength}",
            "",
            "PULL/PUSH MODEL:",
            f"  pull_strength = {self.pull_strength}",
            "  (jitter provides compensating push)",
            "",
            "TIME DILATION (Exp 51):",
            f"  enabled = {self.time_dilation_enabled}",
            f"  load_diffusion = {self.load_diffusion}",
            f"  load_damping = {self.load_damping}",
            f"  energy_regen = {self.energy_regen}",
            f"  energy_max = {self.energy_max}",
            f"  energy_drain_rate = {self.energy_drain_rate}",
            "",
            "GRID:",
            f"  size = {self.grid_width} x {self.grid_height}",
            f"  random_seed = {self.random_seed}",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"LayeredSubstrateConfig(grid={self.grid_size}, jitter={self.jitter_strength})"


# ========================================================================
# Factory functions
# ========================================================================

def create_config(
    grid_size: int = 100,
    jitter_strength: float = None,
    random_seed: int = 42
) -> LayeredSubstrateConfig:
    """Create a V13 configuration.

    Args:
        grid_size: Grid dimension
        jitter_strength: Jitter strength (default: 0.119)
        random_seed: Random seed

    Returns:
        Configured LayeredSubstrateConfig
    """
    return LayeredSubstrateConfig(
        grid_size=grid_size,
        jitter_strength=jitter_strength,
        random_seed=random_seed
    )


# ========================================================================
# Preset configurations
# ========================================================================

class SmallConfig(LayeredSubstrateConfig):
    """Small grid for quick tests."""
    def __init__(self, jitter_strength: float = None, random_seed: int = 42):
        super().__init__(grid_size=50, jitter_strength=jitter_strength, random_seed=random_seed)


class StandardConfig(LayeredSubstrateConfig):
    """Standard grid size."""
    def __init__(self, jitter_strength: float = None, random_seed: int = 42):
        super().__init__(grid_size=100, jitter_strength=jitter_strength, random_seed=random_seed)


class LargeConfig(LayeredSubstrateConfig):
    """Large grid for detailed analysis."""
    def __init__(self, jitter_strength: float = None, random_seed: int = 42):
        super().__init__(grid_size=200, jitter_strength=jitter_strength, random_seed=random_seed)


if __name__ == "__main__":
    print("V13 Configuration")
    print("=" * 70)

    config = create_config(grid_size=100)
    print(config.describe())
    print()

    print("Preset configurations:")
    print("-" * 40)

    for name, cls in [("Small", SmallConfig), ("Standard", StandardConfig), ("Large", LargeConfig)]:
        c = cls()
        print(f"{name}: grid={c.grid_size}, origin={c.origin}")

    print()
    print("=" * 70)
