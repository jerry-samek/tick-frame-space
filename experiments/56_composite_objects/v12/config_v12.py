"""
V12 Configuration - Tick-Ratio Parameters (Growth Invariance)

Key insight: The tick-stream is the fundamental substrate.
- Each tick adds 1 causal energy quantum
- Grid grows by 1 each tick (linear growth)
- Invariant: entity_size / tick_stream_size = 1

The grid is a projection/visualization - dimensionality (2D, 3D) is rendering.

Parameters as Tick Ratios:
- gamma_window_size = tick / 2
- gamma_imprint_k = tick / 10
- target_gamma_k = window (V11 coupling)

The window = 5 × imprint coupling emerges naturally:
  tick/2 = 5 × (tick/10)

Goal: Scale-invariant behavior across grid sizes.
"""

import sys
from pathlib import Path

# Add parent versions to path
v6_path = Path(__file__).parent.parent / "v6"
v7_path = Path(__file__).parent.parent / "v7"
v8_path = Path(__file__).parent.parent / "v8"
v10_path = Path(__file__).parent.parent / "v10"
v11_path = Path(__file__).parent.parent / "v11"
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))
sys.path.insert(0, str(v8_path))
sys.path.insert(0, str(v10_path))
sys.path.insert(0, str(v11_path))

from config_v11 import WellWindowConfig


class TickRatioConfig(WellWindowConfig):
    """Configuration with parameters derived from tick ratios.

    Core principle: The grid_size represents "effective tick" - we are
    visualizing the universe at tick = grid_size.

    All temporal parameters derive from this effective tick:
    - gamma_window_size = effective_tick / 2
    - gamma_imprint_k = effective_tick / 10
    - target_gamma_k = gamma_window_size (V11 coupling)

    The "5:1 window:imprint" coupling emerges naturally from tick ratios.
    """

    # ========================================================================
    # Fundamental Ratios (dimensionless constants)
    # ========================================================================

    # Temporal window ratio: what fraction of history do we track?
    WINDOW_RATIO = 2  # window = tick / 2

    # Imprint strength ratio: how strongly does presence imprint?
    IMPRINT_RATIO = 10  # imprint = tick / 10

    # Note: window/imprint = (tick/2)/(tick/10) = 5
    # The 5:1 ratio is DERIVED, not tuned!

    # ========================================================================
    # Fixed "Game Rules" (topological constants)
    # ========================================================================

    # CA thresholds - discrete topology, not tunable
    ca_survival_threshold = 3  # Out of 8 neighbors
    ca_creation_threshold = 5  # Out of 8 neighbors

    # Field decay - these may also be derivable (future work)
    field_decay_threshold = 1.5
    field_decay_rate = 0.05
    creation_sensitivity = 2.0

    # ========================================================================
    # Empirical constant (not yet derived from tick)
    # ========================================================================

    # Jitter strength - is this 12/tick = 0.12? Or fundamental?
    # Current value 0.119 ≈ 12/100, which is suspicious...
    _jitter_strength = 0.119

    @property
    def jitter_strength(self) -> float:
        """Jitter strength (empirical constant for now)."""
        return self._jitter_strength

    @jitter_strength.setter
    def jitter_strength(self, value: float):
        """Set jitter strength."""
        self._jitter_strength = value

    # ========================================================================
    # Grid size = "effective tick"
    # ========================================================================

    # The grid represents a snapshot at tick = grid_size
    # Default: 100×100 = "tick 100"
    _grid_size = 100

    @property
    def grid_size(self) -> int:
        """Grid size (also = effective tick)."""
        return self._grid_size

    @grid_size.setter
    def grid_size(self, value: int):
        """Set grid size (and effective tick)."""
        self._grid_size = value
        # Update grid dimensions
        self.grid_width = value
        self.grid_height = value

    @property
    def effective_tick(self) -> int:
        """The 'tick' we are visualizing (= grid_size)."""
        return self._grid_size

    # ========================================================================
    # Derived Parameters (tick ratios)
    # ========================================================================

    @property
    def gamma_window_size(self) -> int:
        """History window = tick / WINDOW_RATIO."""
        return self._grid_size // self.WINDOW_RATIO

    @gamma_window_size.setter
    def gamma_window_size(self, value: int):
        """Setter exists for parent class compatibility, but value is derived."""
        # In V12, window_size is derived from grid_size, so we ignore the set
        # This setter exists only for compatibility with parent __init__
        pass

    @property
    def gamma_imprint_k(self) -> float:
        """Imprint strength = tick / IMPRINT_RATIO."""
        return self._grid_size / self.IMPRINT_RATIO

    @gamma_imprint_k.setter
    def gamma_imprint_k(self, value: float):
        """Setter for parent compatibility - value is derived from tick."""
        pass

    @property
    def target_gamma_k(self) -> float:
        """Central well strength = window (V11 coupling)."""
        return float(self.gamma_window_size)

    # ========================================================================
    # Scaled pattern parameters
    # ========================================================================

    @property
    def scaled_n_patterns(self) -> int:
        """Number of patterns scales with area (grid^2 / 400)."""
        # At grid=100, we want 25 patterns (V11 baseline)
        # This gives ~1 pattern per 400 cells
        return max(1, (self._grid_size * self._grid_size) // 400)

    @property
    def scaled_init_radius(self) -> float:
        """Pattern init radius scales with grid size."""
        # At grid=100, radius=10 (V11 baseline)
        return self._grid_size / 10.0

    @property
    def entity_tick_init_radius(self) -> float:
        """Init radius for entity=tick: scales with sqrt(n_patterns).

        For entity=tick, we have N patterns where N = grid_size.
        To maintain constant density, radius should scale with sqrt(N).
        At grid=100 with 100 patterns, radius = sqrt(100) × 2 = 20
        (vs standard radius=10, this gives 4x the area for 4x the patterns)
        """
        import math
        return math.sqrt(self._grid_size) * 2.0

    def __init__(self, grid_size: int = 100):
        """Initialize with specific grid size (= effective tick).

        Args:
            grid_size: Grid dimension (also sets effective tick)
        """
        # Set grid_size BEFORE calling parent init (so properties work)
        self._grid_size = grid_size

        # Parent init will try to set gamma_window_size, but our setter ignores it
        super().__init__(window_size=grid_size // self.WINDOW_RATIO)

        self.grid_width = grid_size
        self.grid_height = grid_size

        # Scale pattern count and radius
        self.n_patterns = self.scaled_n_patterns
        self.pattern_init_radius_mean = self.scaled_init_radius

    def describe(self) -> str:
        """Human-readable description of derived parameters."""
        lines = [
            f"V12 Tick-Ratio Config (grid={self.grid_size})",
            "=" * 50,
            "",
            f"Effective tick: {self.effective_tick}",
            "",
            "Derived parameters (tick ratios):",
            f"  gamma_window_size = tick/{self.WINDOW_RATIO} = {self.gamma_window_size}",
            f"  gamma_imprint_k   = tick/{self.IMPRINT_RATIO} = {self.gamma_imprint_k:.1f}",
            f"  target_gamma_k    = window = {self.target_gamma_k:.1f}",
            "",
            "Emergent coupling:",
            f"  window/imprint = {self.gamma_window_size}/{self.gamma_imprint_k:.1f} = {self.gamma_window_size/self.gamma_imprint_k:.1f}",
            "",
            "Scaled geometry:",
            f"  n_patterns = {self.n_patterns}",
            f"  init_radius = {self.pattern_init_radius_mean:.1f}",
            "",
            "Fixed game rules:",
            f"  ca_survival = {self.ca_survival_threshold}",
            f"  ca_creation = {self.ca_creation_threshold}",
            f"  field_decay_threshold = {self.field_decay_threshold}",
            f"  field_decay_rate = {self.field_decay_rate}",
            f"  creation_sensitivity = {self.creation_sensitivity}",
            "",
            "Empirical (not yet derived):",
            f"  jitter_strength = {self.jitter_strength}",
        ]
        return "\n".join(lines)


# ========================================================================
# Scale-specific configurations
# ========================================================================

GRID_SIZES = [50, 100, 200]


class Grid50Config(TickRatioConfig):
    """Grid=50 (small scale, tick 50)."""
    def __init__(self):
        super().__init__(grid_size=50)


class Grid100Config(TickRatioConfig):
    """Grid=100 (V11 baseline, tick 100)."""
    def __init__(self):
        super().__init__(grid_size=100)


class Grid200Config(TickRatioConfig):
    """Grid=200 (large scale, tick 200)."""
    def __init__(self):
        super().__init__(grid_size=200)


def create_tick_ratio_config(grid_size: int) -> TickRatioConfig:
    """Create a config with specific grid size (= effective tick).

    Args:
        grid_size: Grid dimension (also sets effective tick)

    Returns:
        Configured TickRatioConfig
    """
    return TickRatioConfig(grid_size)


# ========================================================================
# Jitter exploration configs
# ========================================================================

class JitterAsTickRatioConfig(TickRatioConfig):
    """Test hypothesis: jitter_strength = 12/tick.

    At tick=100: 12/100 = 0.12 (close to empirical 0.119)
    """

    JITTER_NUMERATOR = 12  # Hypothesis: jitter = 12/tick

    @property
    def jitter_strength(self) -> float:
        """Jitter as tick ratio."""
        return self.JITTER_NUMERATOR / self.effective_tick


class EntityTickConfig(TickRatioConfig):
    """Config where n_patterns = tick (entity count = time).

    Physical meaning: Each tick creates one causal quantum.
    At tick N, you have exactly N entities.

    Density by dimension:
    - 1D: universe is full (100% = tick/tick density)
    - 2D: sparse (tick/tick² = 1/tick density)
    - 3D: very sparse (tick/tick³ = 1/tick² density)

    This tests the hypothesis that the invariant is literally:
        entity_count / tick_stream_size = 1
    """

    @property
    def n_patterns(self) -> int:
        """Entity count = tick count (the core hypothesis)."""
        return self.effective_tick

    @n_patterns.setter
    def n_patterns(self, value: int):
        """Setter for parent compatibility - value is derived from tick."""
        pass

    @property
    def linear_density(self) -> float:
        """1D density: patterns / tick = 1 (always full)."""
        return self.n_patterns / self.effective_tick

    @property
    def area_density(self) -> float:
        """2D density: patterns / tick² = 1/tick."""
        area = self.effective_tick * self.effective_tick
        return self.n_patterns / area if area > 0 else 0.0

    @property
    def volume_density(self) -> float:
        """3D density: patterns / tick³ = 1/tick²."""
        volume = self.effective_tick ** 3
        return self.n_patterns / volume if volume > 0 else 0.0

    def __init__(self, grid_size: int = 100):
        """Initialize with specific grid size (= effective tick = entity count).

        Args:
            grid_size: Grid dimension (also sets effective tick and entity count)
        """
        super().__init__(grid_size)
        # Override parent's area-scaled pattern count
        # Note: n_patterns property will return effective_tick

    def describe(self) -> str:
        """Human-readable description with entity=tick hypothesis."""
        lines = [
            f"V12b Entity=Tick Config (grid={self.grid_size})",
            "=" * 50,
            "",
            f"Effective tick: {self.effective_tick}",
            f"Entity count:   {self.n_patterns} (= tick)",
            "",
            "Density by dimension:",
            f"  1D: {self.linear_density:.4f} (patterns/tick - always 1.0)",
            f"  2D: {self.area_density:.6f} (patterns/tick^2 = 1/tick)",
            f"  3D: {self.volume_density:.8f} (patterns/tick^3 = 1/tick^2)",
            "",
            f"Init radius (entity=tick): {self.entity_tick_init_radius:.1f} (sqrt(tick) * 2)",
            "",
            "Derived parameters (tick ratios):",
            f"  gamma_window_size = tick/{self.WINDOW_RATIO} = {self.gamma_window_size}",
            f"  gamma_imprint_k   = tick/{self.IMPRINT_RATIO} = {self.gamma_imprint_k:.1f}",
            f"  target_gamma_k    = window = {self.target_gamma_k:.1f}",
            "",
            "Emergent coupling:",
            f"  window/imprint = {self.gamma_window_size}/{self.gamma_imprint_k:.1f} = {self.gamma_window_size/self.gamma_imprint_k:.1f}",
            "",
            "Fixed game rules:",
            f"  ca_survival = {self.ca_survival_threshold}",
            f"  ca_creation = {self.ca_creation_threshold}",
            f"  field_decay_threshold = {self.field_decay_threshold}",
            f"  field_decay_rate = {self.field_decay_rate}",
            f"  creation_sensitivity = {self.creation_sensitivity}",
            "",
            "Empirical (not yet derived):",
            f"  jitter_strength = {self.jitter_strength}",
        ]
        return "\n".join(lines)


def create_entity_tick_config(grid_size: int) -> EntityTickConfig:
    """Create a config with entity count = tick count.

    Args:
        grid_size: Grid dimension (= effective tick = entity count)

    Returns:
        Configured EntityTickConfig
    """
    return EntityTickConfig(grid_size)


# ========================================================================
# V12c: Tick-Unified Configuration (window = imprint = well = tick)
# ========================================================================

class TickUnifiedConfig(EntityTickConfig):
    """All gamma parameters = tick.

    Eliminates empirical ratios:
    - window = tick (not tick/2)
    - imprint = tick (not tick/10)
    - well = tick (= window)

    The 5:1 ratio becomes 1:1:1 - everything grows by 1 each tick.

    Dimensional density argument:
    - 1D: see all n entities
    - 2D: see n/n² = 1/n fraction
    - 3D: see n/n³ = 1/n² fraction

    This is the simplest possible model: all temporal parameters = tick.
    """

    # Override ratios - effectively 1:1 (no division)
    WINDOW_RATIO = 1  # window = tick / 1 = tick
    IMPRINT_RATIO = 1  # imprint = tick / 1 = tick

    @property
    def gamma_window_size(self) -> int:
        """Window = tick (1 added per tick)."""
        return self.effective_tick

    @gamma_window_size.setter
    def gamma_window_size(self, value: int):
        """Setter for parent compatibility - value is derived from tick."""
        pass

    @property
    def gamma_imprint_k(self) -> float:
        """Imprint = tick (1 added per tick)."""
        return float(self.effective_tick)

    @gamma_imprint_k.setter
    def gamma_imprint_k(self, value: float):
        """Setter for parent compatibility - value is derived from tick."""
        pass

    @property
    def target_gamma_k(self) -> float:
        """Well = tick (= window)."""
        return float(self.effective_tick)

    def describe(self) -> str:
        """Human-readable description with tick-unified parameters."""
        lines = [
            f"V12c Tick-Unified Config (grid={self.grid_size})",
            "=" * 50,
            "",
            f"Effective tick: {self.effective_tick}",
            f"Entity count:   {self.n_patterns} (= tick)",
            "",
            "TICK-UNIFIED PARAMETERS (all = tick):",
            f"  gamma_window_size = tick = {self.gamma_window_size}",
            f"  gamma_imprint_k   = tick = {self.gamma_imprint_k:.1f}",
            f"  target_gamma_k    = tick = {self.target_gamma_k:.1f}",
            "",
            "Ratios (all 1:1:1):",
            f"  window/imprint = {self.gamma_window_size}/{self.gamma_imprint_k:.1f} = {self.gamma_window_size/self.gamma_imprint_k:.1f}",
            f"  well/window = {self.target_gamma_k:.1f}/{self.gamma_window_size} = {self.target_gamma_k/self.gamma_window_size:.1f}",
            "",
            "Density by dimension:",
            f"  1D: {self.linear_density:.4f} (patterns/tick - always 1.0)",
            f"  2D: {self.area_density:.6f} (patterns/tick^2 = 1/tick)",
            f"  3D: {self.volume_density:.8f} (patterns/tick^3 = 1/tick^2)",
            "",
            f"Init radius: {self.entity_tick_init_radius:.1f} (sqrt(tick) * 2)",
            "",
            "Fixed game rules:",
            f"  ca_survival = {self.ca_survival_threshold}",
            f"  ca_creation = {self.ca_creation_threshold}",
            f"  field_decay_threshold = {self.field_decay_threshold}",
            f"  field_decay_rate = {self.field_decay_rate}",
            f"  creation_sensitivity = {self.creation_sensitivity}",
            "",
            "Empirical (not yet derived):",
            f"  jitter_strength = {self.jitter_strength}",
        ]
        return "\n".join(lines)


# ========================================================================
# V12d: Substrate Configuration (only jitter, no CA rules)
# ========================================================================

class SubstrateConfig(TickUnifiedConfig):
    """Minimal substrate config - only jitter.

    Eliminates ALL CA parameters:
    - No survival threshold (entities persist forever)
    - No creation threshold (creation = tick)
    - No decay (only forgetting via window)

    Key insight: On the substrate level, there is only ONE real constant.

    - Creation: happens with each tick (1 entity per tick)
    - Death: **impossible** - entities can't be removed
    - Forgetting: entities outside the observation window become unobservable

    The CA "death" rules were implementing forgetting at the wrong level.
    An entity with insufficient neighbors isn't dying - it's becoming
    incoherent as a pattern. But the substrate should preserve it.

    Parameter reduction:
    - V11: 8 parameters (window, imprint, well, jitter, 5 CA params)
    - V12b: 6 parameters (tick-ratios for window/imprint/well, jitter, 5 CA)
    - V12c: 6 parameters (all gamma = tick, jitter, 5 CA)
    - V12d: 1 parameter (jitter only)
    """

    # The ONE constant - jitter strength
    # Is this 12/tick = 0.12? Or truly fundamental?
    # Current value 0.119 ≈ 12/100, suspicious...
    JITTER_STRENGTH = 0.119

    # ========================================================================
    # Disabled CA parameters (set to None or 0 to indicate not used)
    # ========================================================================

    # Survival threshold: not used (entities persist forever)
    ca_survival_threshold = None

    # Creation threshold: not used (creation = tick, handled elsewhere)
    ca_creation_threshold = None

    # Creation sensitivity: disabled
    creation_sensitivity = 0.0

    # Field decay: disabled (no decay at substrate level)
    field_decay_threshold = 0.0
    field_decay_rate = 0.0

    @property
    def jitter_strength(self) -> float:
        """The ONE constant: jitter strength."""
        return self.JITTER_STRENGTH

    @jitter_strength.setter
    def jitter_strength(self, value: float):
        """Set jitter strength."""
        self.JITTER_STRENGTH = value

    def describe(self) -> str:
        """Human-readable description with minimal substrate parameters."""
        lines = [
            f"V12d Substrate Config (grid={self.grid_size})",
            "=" * 50,
            "",
            f"Effective tick: {self.effective_tick}",
            f"Entity count:   {self.n_patterns} (= tick)",
            "",
            "THE ONE CONSTANT:",
            f"  jitter_strength = {self.jitter_strength}",
            "",
            "TICK-UNIFIED GAMMA (memory, not dynamics):",
            f"  gamma_window_size = tick = {self.gamma_window_size}",
            f"  gamma_imprint_k   = tick = {self.gamma_imprint_k:.1f}",
            f"  target_gamma_k    = tick = {self.target_gamma_k:.1f}",
            "",
            "DISABLED CA PARAMETERS:",
            f"  ca_survival_threshold = {self.ca_survival_threshold} (entities persist)",
            f"  ca_creation_threshold = {self.ca_creation_threshold} (creation = tick)",
            f"  creation_sensitivity = {self.creation_sensitivity} (disabled)",
            f"  field_decay_threshold = {self.field_decay_threshold} (no decay)",
            f"  field_decay_rate = {self.field_decay_rate} (no decay)",
            "",
            "Density by dimension:",
            f"  1D: {self.linear_density:.4f} (patterns/tick - always 1.0)",
            f"  2D: {self.area_density:.6f} (patterns/tick^2 = 1/tick)",
            f"  3D: {self.volume_density:.8f} (patterns/tick^3 = 1/tick^2)",
            "",
            f"Init radius: {self.entity_tick_init_radius:.1f} (sqrt(tick) * 2)",
        ]
        return "\n".join(lines)


def create_substrate_config(grid_size: int) -> SubstrateConfig:
    """Create a minimal substrate config (jitter only).

    Args:
        grid_size: Grid dimension (= effective tick = entity count)

    Returns:
        Configured SubstrateConfig
    """
    return SubstrateConfig(grid_size)


def create_tick_unified_config(grid_size: int) -> TickUnifiedConfig:
    """Create a config with all gamma parameters = tick.

    Args:
        grid_size: Grid dimension (= effective tick = entity count)

    Returns:
        Configured TickUnifiedConfig
    """
    return TickUnifiedConfig(grid_size)


if __name__ == "__main__":
    print("V12 Tick-Ratio Configuration")
    print("=" * 70)
    print()
    print("KEY INSIGHT: All parameters derive from tick (= grid_size)")
    print()
    print("Fundamental ratios (dimensionless constants):")
    print(f"  WINDOW_RATIO = {TickRatioConfig.WINDOW_RATIO}")
    print(f"  IMPRINT_RATIO = {TickRatioConfig.IMPRINT_RATIO}")
    print()
    print("Emergent coupling:")
    print(f"  window/imprint = IMPRINT_RATIO/WINDOW_RATIO = {TickRatioConfig.IMPRINT_RATIO/TickRatioConfig.WINDOW_RATIO}")
    print()
    print("=" * 70)
    print()

    for gs in GRID_SIZES:
        config = create_tick_ratio_config(gs)
        print(config.describe())
        print()
        print("-" * 70)
        print()

    print("=" * 70)
    print()
    print("SCALE INVARIANCE TEST:")
    print()
    print("If tick-ratio model is correct, these should produce similar")
    print("stability metrics (normalized by scale):")
    print()
    print(f"{'Grid':>6} | {'Window':>6} | {'Imprint':>8} | {'Well':>6} | {'Patterns':>8}")
    print("-" * 50)
    for gs in GRID_SIZES:
        config = create_tick_ratio_config(gs)
        print(f"{gs:>6} | {config.gamma_window_size:>6} | "
              f"{config.gamma_imprint_k:>8.1f} | {config.target_gamma_k:>6.1f} | "
              f"{config.n_patterns:>8}")
    print()
    print("All ratios (window/imprint, well/window) should be constant!")

    print()
    print("=" * 70)
    print()
    print("V12c TICK-UNIFIED COMPARISON")
    print("=" * 70)
    print()
    print("V12c eliminates empirical ratios: all parameters = tick")
    print()
    print(f"{'Grid':>6} | {'V12b Window':>11} | {'V12c Window':>11} | {'V12b Imprint':>12} | {'V12c Imprint':>12}")
    print("-" * 70)
    for gs in GRID_SIZES:
        v12b = create_entity_tick_config(gs)
        v12c = create_tick_unified_config(gs)
        print(f"{gs:>6} | {v12b.gamma_window_size:>11} | {v12c.gamma_window_size:>11} | "
              f"{v12b.gamma_imprint_k:>12.1f} | {v12c.gamma_imprint_k:>12.1f}")
    print()
    print("V12b: window=tick/2, imprint=tick/10 (5:1 ratio)")
    print("V12c: window=tick, imprint=tick (1:1 ratio)")

    print()
    print("=" * 70)
    print()
    print("V12d SUBSTRATE CONFIG (jitter only)")
    print("=" * 70)
    print()
    print("V12d eliminates ALL CA parameters - only jitter remains")
    print()
    for gs in GRID_SIZES:
        v12d = create_substrate_config(gs)
        print(v12d.describe())
        print()
        print("-" * 70)
        print()
