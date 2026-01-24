#!/usr/bin/env python3
"""
Configuration for Experiment 56 Phase 4 V3: Fragmented Electron Cloud

Parameters for fragmented electron cloud simulation based on Doc 070* theory.
"""

from dataclasses import dataclass


@dataclass
class ConfigV3:
    """Configuration parameters for V3 fragmented electron cloud experiment."""

    # ========================================================================
    # Fragment Parameters
    # ========================================================================

    n_fragments: int = 50
    """Number of electron fragments (micro-patterns) in the cloud"""

    fragment_init_radius_mean: float = 2.0
    """Mean initial radius for fragment distribution (Bohr radius analog)"""

    fragment_init_radius_std: float = 0.5
    """Standard deviation of initial radius distribution"""

    fragment_init_velocity_mean: float = 0.1
    """Mean magnitude of initial fragment velocities"""

    fragment_init_velocity_std: float = 0.02
    """Standard deviation of initial velocity magnitudes"""

    electron_total_mass: float = 0.001
    """Total electron mass (distributed among fragments)"""

    electron_total_energy: float = 5.0
    """Total electron energy (distributed among fragments)"""

    # ========================================================================
    # Collision Parameters (Doc 070_01: Collision-Driven Stabilization)
    # ========================================================================

    collision_radius: float = 0.5
    """Distance threshold for fragment-fragment collisions"""

    restitution_coefficient: float = 0.8
    """
    Coefficient of restitution for collisions (0-1).
    e=1.0 → perfectly elastic
    e=0.8 → slight damping (thermalization)
    e=0.0 → perfectly inelastic
    """

    # ========================================================================
    # Zero-Point Energy (Doc 070_00 §2: Tick-Frame Metabolic Pressure)
    # ========================================================================

    jitter_strength: float = 0.001
    """
    Strength of tick-frame jitter (Brownian noise standard deviation).
    Models irreducible metabolic pressure from expanding tick-frame.
    Prevents collapse into nucleus.
    """

    apply_jitter: bool = True
    """Enable/disable zero-point jitter for ablation studies"""

    # ========================================================================
    # Gradient-Following Parameters
    # ========================================================================

    coupling_constant: float = 0.05
    """Strength of gamma-gradient coupling (k in F = k × ∇γ)"""

    apply_gradient_force: bool = True
    """Enable/disable gradient force for ablation studies"""

    radial_force_only: bool = True
    """
    If True: Apply only radial component of gradient (centripetal force).
    If False: Apply full gradient force vector.
    """

    # ========================================================================
    # Field Dynamics Parameters
    # ========================================================================

    grid_size: int = 100
    """Size of simulation grid"""

    field_update_interval: int = 5
    """Recompute gamma-field every N ticks (performance optimization)"""

    # Field equation parameters (from v11 baseline)
    alpha: float = 0.012  # Diffusion coefficient for load field
    gamma_damp: float = 0.0005  # Nonlinear damping for load field
    scale: float = 0.75  # Source strength scaling
    R: float = 1.2  # Energy regeneration rate
    D: float = 0.01  # Load-dependent drainage
    E_max: float = 15.0  # Maximum energy capacity
    capacity_min: float = 0.1  # Minimum effective capacity
    work_threshold: float = 0.5  # Minimum energy for work
    c: float = 1.0  # Speed of light

    # ========================================================================
    # Proton Parameters
    # ========================================================================

    proton_mass: float = 1.0
    """Proton mass"""

    proton_energy: float = 10.0
    """Proton energy"""

    proton_position: tuple = (50.0, 50.0)
    """Proton position (center of grid)"""

    # ========================================================================
    # Simulation Parameters
    # ========================================================================

    num_ticks: int = 10000
    """Total number of simulation ticks"""

    snapshot_interval: int = 100
    """Save snapshot every N ticks"""

    # ========================================================================
    # Analysis Parameters
    # ========================================================================

    radial_bins: int = 50
    """Number of bins for radial density profile"""

    max_analysis_radius: float = 20.0
    """Maximum radius for density profile analysis"""

    energy_histogram_bins: int = 30
    """Number of bins for energy distribution histogram"""

    # ========================================================================
    # Success Criteria
    # ========================================================================

    max_cloud_drift_percent: float = 10.0
    """Maximum allowable cloud radius drift percentage"""

    max_fragment_escape_radius: float = 20.0
    """Fragments beyond this radius considered escaped"""

    min_stability_duration: int = 5000
    """Minimum ticks for cloud to remain stable"""


# ============================================================================
# Preset Configurations
# ============================================================================

def get_baseline_config() -> ConfigV3:
    """Get baseline configuration (default parameters)."""
    return ConfigV3()


def get_debug_config() -> ConfigV3:
    """Get configuration for debugging (fewer fragments, shorter simulation)."""
    config = ConfigV3()
    config.n_fragments = 20
    config.num_ticks = 1000
    config.snapshot_interval = 50
    return config


def get_high_resolution_config() -> ConfigV3:
    """Get configuration for high-resolution simulation."""
    config = ConfigV3()
    config.n_fragments = 100
    config.num_ticks = 20000
    config.snapshot_interval = 200
    config.radial_bins = 100
    return config


def get_ablation_no_jitter_config() -> ConfigV3:
    """Ablation study: disable zero-point jitter."""
    config = ConfigV3()
    config.apply_jitter = False
    return config


def get_ablation_no_collisions_config() -> ConfigV3:
    """Ablation study: disable collisions (set restitution to 1.0, infinite radius)."""
    config = ConfigV3()
    config.collision_radius = 0.0  # No collisions
    return config


def get_ablation_no_gradient_config() -> ConfigV3:
    """Ablation study: disable gradient force (free particles)."""
    config = ConfigV3()
    config.apply_gradient_force = False
    return config


if __name__ == "__main__":
    # Print baseline configuration
    config = get_baseline_config()
    print("Baseline Configuration for V3:")
    print(f"  Fragments: {config.n_fragments}")
    print(f"  Initial radius: {config.fragment_init_radius_mean} ± {config.fragment_init_radius_std}")
    print(f"  Initial velocity: {config.fragment_init_velocity_mean} ± {config.fragment_init_velocity_std}")
    print(f"  Collision radius: {config.collision_radius}")
    print(f"  Restitution: {config.restitution_coefficient}")
    print(f"  Jitter strength: {config.jitter_strength}")
    print(f"  Coupling constant: {config.coupling_constant}")
    print(f"  Simulation: {config.num_ticks} ticks")
