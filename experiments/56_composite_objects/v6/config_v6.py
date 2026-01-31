"""
Configuration for V6 Grid-Based Tick-Frame Experiments

All parameters for grid-based cellular automaton physics.
Uses floating-point for easier tuning (discrete grid, continuous field values).

Author: V6 Grid-Based Implementation
Date: 2026-01-24
"""


class ConfigV6:
    """Configuration for V6 experiments."""

    # ========================================================================
    # Grid Parameters
    # ========================================================================

    grid_width = 200  # Planck cells
    grid_height = 200  # Planck cells

    # ========================================================================
    # Pattern Parameters
    # ========================================================================

    pattern_size = 5  # 5×5 sample cells (recommended from STRUCTURE.md)
    n_patterns = 50  # Number of initial patterns

    # Initial pattern distribution (in Planck cells from grid center)
    pattern_init_radius_mean = 20.0  # Mean radius (Planck cells)
    pattern_init_radius_std = 5.0  # Std deviation

    # ========================================================================
    # Jitter Parameters (Planck-level quantum fluctuations)
    # ========================================================================

    # Symmetric jitter: p(-1) = p(+1) = jitter_strength
    # p(0) = 1 - 2*jitter_strength
    jitter_strength = 0.05  # Default: 5% chance of ±1 per cell per tick

    # ========================================================================
    # Cellular Automaton Evolution Parameters
    # ========================================================================

    # Gamma field modulation strength (0.0 = no effect, 1.0 = full effect)
    gamma_modulation_strength = 1.0

    # CA survival threshold (base: need this many same-sign neighbors to survive)
    ca_survival_threshold = 3  # Out of 8 neighbors

    # CA creation threshold (need this many same-sign neighbors to create)
    ca_creation_threshold = 5  # Out of 8 neighbors

    # ========================================================================
    # Gamma Field Parameters (Radial Confinement)
    # ========================================================================

    # Gamma function: γ(r) = 1 + k/r²
    # Higher k → stronger confinement
    gamma_field_k = 100.0  # Field strength

    # Gamma range (clamped to [gamma_min, gamma_max])
    gamma_min = 1.0
    gamma_max = 2.0

    # ========================================================================
    # Field Confinement Parameters (Phase 4)
    # ========================================================================

    # Gamma-dependent creation threshold
    # creation_threshold = ca_creation_threshold + (2.0 - gamma) * creation_sensitivity
    # Higher creation_sensitivity → harder to create field at low gamma
    creation_sensitivity = 0.0  # 0.0 = no gamma effect (baseline)

    # Field decay in low-gamma regions
    field_decay_threshold = 0.0  # Gamma below which decay applies (0.0 = no decay)
    field_decay_rate = 0.0  # Probability of decay per tick (0.0-1.0)

    # ========================================================================
    # Simulation Parameters
    # ========================================================================

    num_ticks = 1000  # Total simulation ticks
    progress_interval = 100  # Report progress every N ticks

    # Validation thresholds
    max_radius_drift_percent = 50.0  # Maximum acceptable drift

    # Random seed
    random_seed = 42


class TuningConfigLowJitter(ConfigV6):
    """Low jitter strength (p=0.01) for stability testing."""
    jitter_strength = 0.01
    gamma_modulation_strength = 0.5


class TuningConfigMediumJitter(ConfigV6):
    """Medium jitter strength (p=0.02) for balance testing."""
    jitter_strength = 0.02
    gamma_modulation_strength = 0.5


class TuningConfigHighJitter(ConfigV6):
    """High jitter strength (p=0.05) for diffusion testing."""
    jitter_strength = 0.05
    gamma_modulation_strength = 0.5


class TuningConfigStrongGamma(ConfigV6):
    """Strong gamma modulation (strength=1.0) for confinement testing."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0


class TuningConfigVeryStrongGamma(ConfigV6):
    """Very strong gamma modulation (strength=2.0) for maximum confinement."""
    jitter_strength = 0.02
    gamma_modulation_strength = 2.0


class ValidationConfig10k(ConfigV6):
    """10k tick validation configuration."""
    num_ticks = 10_000
    progress_interval = 500
    jitter_strength = 0.02  # Best from tuning (to be determined)
    gamma_modulation_strength = 1.0


class ValidationConfig10kFieldConfined(ConfigV6):
    """10k tick validation with optimal field confinement (hybrid_strong)."""
    num_ticks = 10_000
    progress_interval = 500
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    # Optimal field confinement parameters from Phase 4A tuning
    creation_sensitivity = 2.0
    field_decay_threshold = 1.5
    field_decay_rate = 0.05


class ValidationConfig200k(ConfigV6):
    """200k tick validation configuration."""
    num_ticks = 200_000
    progress_interval = 1000
    jitter_strength = 0.02  # Best from tuning (to be determined)
    gamma_modulation_strength = 1.0


def get_tuning_configs():
    """Get all tuning configurations for parameter sweep."""
    return {
        "jitter_0.01_gamma_0.5": TuningConfigLowJitter(),
        "jitter_0.02_gamma_0.5": TuningConfigMediumJitter(),
        "jitter_0.05_gamma_0.5": TuningConfigHighJitter(),
        "jitter_0.02_gamma_1.0": TuningConfigStrongGamma(),
        "jitter_0.02_gamma_2.0": TuningConfigVeryStrongGamma(),
    }


# ========================================================================
# Phase 4: Field Confinement Tuning Configurations
# ========================================================================

class FieldConfinementBaselineConfig(ConfigV6):
    """Baseline: No field confinement (Phase 3 parameters)."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0  # No gamma effect on creation
    field_decay_threshold = 0.0  # No field decay
    field_decay_rate = 0.0


class FieldConfinementCreationLowConfig(ConfigV6):
    """Test gamma-dependent creation: low sensitivity."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.5  # Mild gamma effect
    field_decay_threshold = 0.0  # No decay
    field_decay_rate = 0.0


class FieldConfinementCreationMediumConfig(ConfigV6):
    """Test gamma-dependent creation: medium sensitivity."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 1.0  # Moderate gamma effect
    field_decay_threshold = 0.0  # No decay
    field_decay_rate = 0.0


class FieldConfinementCreationHighConfig(ConfigV6):
    """Test gamma-dependent creation: high sensitivity."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 2.0  # Strong gamma effect
    field_decay_threshold = 0.0  # No decay
    field_decay_rate = 0.0


class FieldConfinementDecayLowConfig(ConfigV6):
    """Test field decay: low decay rate."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0  # No gamma effect on creation
    field_decay_threshold = 1.3  # Decay below gamma=1.3
    field_decay_rate = 0.01  # 1% decay per tick


class FieldConfinementDecayMediumConfig(ConfigV6):
    """Test field decay: medium decay rate."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0  # No gamma effect on creation
    field_decay_threshold = 1.3  # Decay below gamma=1.3
    field_decay_rate = 0.02  # 2% decay per tick


class FieldConfinementDecayHighConfig(ConfigV6):
    """Test field decay: high decay rate."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0  # No gamma effect on creation
    field_decay_threshold = 1.3  # Decay below gamma=1.3
    field_decay_rate = 0.05  # 5% decay per tick


class FieldConfinementHybridLowConfig(ConfigV6):
    """Hybrid: gamma-dependent creation + field decay (conservative)."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 1.0  # Moderate creation sensitivity
    field_decay_threshold = 1.3  # Decay below gamma=1.3
    field_decay_rate = 0.01  # Low decay rate


class FieldConfinementHybridMediumConfig(ConfigV6):
    """Hybrid: gamma-dependent creation + field decay (balanced)."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 1.0  # Moderate creation sensitivity
    field_decay_threshold = 1.3  # Decay below gamma=1.3
    field_decay_rate = 0.02  # Medium decay rate


class FieldConfinementHybridHighConfig(ConfigV6):
    """Hybrid: gamma-dependent creation + field decay (aggressive)."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 2.0  # Strong creation sensitivity
    field_decay_threshold = 1.3  # Decay below gamma=1.3
    field_decay_rate = 0.02  # Medium decay rate


class FieldConfinementHybridStrongConfig(ConfigV6):
    """Hybrid: gamma-dependent creation + field decay (very aggressive)."""
    jitter_strength = 0.02
    gamma_modulation_strength = 1.0
    creation_sensitivity = 2.0  # Strong creation sensitivity
    field_decay_threshold = 1.5  # Higher threshold (decay in larger region)
    field_decay_rate = 0.05  # High decay rate


# ========================================================================
# Phase 5: High-Jitter Configurations (Pattern Stability via Zero-Point Energy)
# ========================================================================

class JitterSweepConfig03(ConfigV6):
    """Jitter sweep: 3% zero-point fluctuations."""
    jitter_strength = 0.03
    gamma_modulation_strength = 1.0
    # No field confinement (test pure jitter effect)
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig04(ConfigV6):
    """Jitter sweep: 4% zero-point fluctuations."""
    jitter_strength = 0.04
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig05(ConfigV6):
    """Jitter sweep: 5% zero-point fluctuations."""
    jitter_strength = 0.05
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig06(ConfigV6):
    """Jitter sweep: 6% zero-point fluctuations (aggressive)."""
    jitter_strength = 0.06
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig07(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.07
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig08(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.08
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig09(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.09
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig10(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.10
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig11(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.11
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig115(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.115
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig117(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.117
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig118(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.118
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig119(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.119
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig12(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.12
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig13(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.13
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig14(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.14
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig15(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.15
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0

class JitterSweepConfig16(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.16
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0

class JitterSweepConfig17(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.17
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0

class JitterSweepConfig18(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.18
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0

class JitterSweepConfig19(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.19
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0

class JitterSweepConfig20(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.20
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig30(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.30
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


class JitterSweepConfig40(ConfigV6):
    """Jitter sweep: 7% zero-point fluctuations (very aggressive)."""
    jitter_strength = 0.40
    gamma_modulation_strength = 1.0
    creation_sensitivity = 0.0
    field_decay_threshold = 0.0
    field_decay_rate = 0.0


def get_jitter_sweep_configs():
    """Get jitter sweep configurations (Phase 5: counteract gravitational collapse)."""
    return {
        "jitter_0.03": JitterSweepConfig03(),
        "jitter_0.04": JitterSweepConfig04(),
        "jitter_0.05": JitterSweepConfig05(),
        "jitter_0.06": JitterSweepConfig06(),
        "jitter_0.07": JitterSweepConfig07(),
    }


def get_field_confinement_configs():
    """Get all field confinement tuning configurations for Phase 4."""
    return {
        "baseline": FieldConfinementBaselineConfig(),
        "creation_low": FieldConfinementCreationLowConfig(),
        "creation_medium": FieldConfinementCreationMediumConfig(),
        "creation_high": FieldConfinementCreationHighConfig(),
        "decay_low": FieldConfinementDecayLowConfig(),
        "decay_medium": FieldConfinementDecayMediumConfig(),
        "decay_high": FieldConfinementDecayHighConfig(),
        "hybrid_low": FieldConfinementHybridLowConfig(),
        "hybrid_medium": FieldConfinementHybridMediumConfig(),
        "hybrid_high": FieldConfinementHybridHighConfig(),
        "hybrid_strong": FieldConfinementHybridStrongConfig(),
    }


if __name__ == "__main__":
    # Print all configurations
    print("V6 Configuration Summary")
    print("=" * 70)

    configs = get_tuning_configs()

    for name, config in configs.items():
        print(f"\n{name}:")
        print(f"  Grid: {config.grid_width}×{config.grid_height}")
        print(
            f"  Patterns: {config.n_patterns} (init radius: {config.pattern_init_radius_mean:.1f} ± {config.pattern_init_radius_std:.1f})")
        print(f"  Jitter strength: {config.jitter_strength:.3f}")
        print(f"  Gamma modulation: {config.gamma_modulation_strength:.1f}")
        print(f"  Gamma field k: {config.gamma_field_k:.1f}")
        print(f"  CA survival threshold: {config.ca_survival_threshold}")
        print(f"  Ticks: {config.num_ticks:,}")

    print("\n" + "=" * 70)
