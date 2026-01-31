#!/usr/bin/env python3
"""
Configuration for Experiment 56 Phase 4 V4: Quantization Study

Extended 100k tick simulation to test quantization hypothesis (Doc 070_01 §4).
Based on successful V3 baseline with enhanced tracking for quantization analysis.
"""

from dataclasses import dataclass


@dataclass
class ConfigV4:
    """Configuration parameters for V4 quantization study."""

    # ========================================================================
    # Fragment Parameters (Same as V3 successful baseline)
    # ========================================================================

    n_fragments: int = 50
    """Number of electron fragments (micro-patterns) in the cloud"""

    fragment_init_radius_mean: float = 2.0
    """Mean initial radius for fragment distribution (Bohr radius analog)"""

    fragment_init_radius_std: float = 0.5
    """Standard deviation of initial radius distribution"""

    fragment_init_velocity_mean: float = 0.05
    """Mean magnitude of initial fragment velocities (V3 scaled value)"""

    fragment_init_velocity_std: float = 0.01
    """Standard deviation of initial velocity magnitudes"""

    electron_total_mass: float = 0.1
    """Total electron mass (V3 scaled: 100× heavier)"""

    electron_total_energy: float = 50.0
    """Total electron energy (V3 scaled)"""

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
    # Gradient-Following Parameters (V3 scaled physics)
    # ========================================================================

    coupling_constant: float = 0.001
    """Strength of gamma-gradient coupling (V3 scaled: weak coupling)"""

    apply_gradient_force: bool = True
    """Enable/disable gradient force for ablation studies"""

    radial_force_only: bool = True
    """
    If True: Apply only radial component of gradient (centripetal force).
    If False: Apply full gradient force vector.
    """

    # ========================================================================
    # Field Dynamics Parameters (from V3 baseline)
    # ========================================================================

    grid_size: int = 100
    """Size of simulation grid"""

    field_update_interval: int = 10
    """Recompute gamma-field every N ticks (performance optimization)"""

    # Field equation parameters (from v11 baseline)
    alpha: float = 0.012  # Diffusion coefficient for load field
    gamma_damp: float = 0.0005  # Nonlinear damping for load field
    scale: float = 0.75  # Source strength scaling
    R: float = 1.2  # Energy regeneration rate
    D: float = 0.01  # Load-dependent drainage
    E_max: float = 1500.0  # Maximum energy capacity (V3 scaled)
    capacity_min: float = 0.1  # Minimum effective capacity
    work_threshold: float = 0.5  # Minimum energy for work
    c: float = 1.0  # Speed of light

    # ========================================================================
    # Proton Parameters (V3 scaled physics)
    # ========================================================================

    proton_mass: float = 100.0
    """Proton mass (V3 scaled: composite of ~100 quark fragments)"""

    proton_energy: float = 1000.0
    """Proton energy (V3 scaled proportionally)"""

    proton_position: tuple = (50.0, 50.0)
    """Proton position (center of grid)"""

    # ========================================================================
    # Extended Simulation Parameters (V4 QUANTIZATION STUDY)
    # ========================================================================

    num_ticks: int = 100000
    """Total number of simulation ticks (10× longer than V3 for quantization)"""

    snapshot_interval: int = 100
    """Save snapshot every N ticks (1000 total snapshots)"""

    detailed_snapshot_interval: int = 1000
    """Save full fragment data every N ticks (for correlation analysis)"""

    progress_report_interval: int = 10000
    """Print progress every N ticks"""

    # ========================================================================
    # Enhanced Tracking (V4 NEW)
    # ========================================================================

    track_fragment_energies: bool = True
    """Save individual fragment energies (KE + PE) at each snapshot"""

    track_velocity_distribution: bool = True
    """Save velocity distribution data at each detailed snapshot"""

    track_radial_density_profile: bool = True
    """Save full radial density profile at each detailed snapshot"""

    compute_potential_energy: bool = True
    """Compute potential energy from gamma-field for energy conservation check"""

    # ========================================================================
    # Analysis Parameters (Enhanced for quantization detection)
    # ========================================================================

    radial_bins: int = 100
    """Number of bins for radial density profile (higher resolution)"""

    max_analysis_radius: float = 20.0
    """Maximum radius for density profile analysis"""

    energy_histogram_bins: int = 50
    """Number of bins for energy distribution histogram"""

    velocity_histogram_bins: int = 40
    """Number of bins for velocity distribution histogram"""

    # Quantization detection parameters
    shell_detection_prominence: float = 0.05
    """Minimum prominence for radial shell peak detection"""

    energy_gap_threshold: float = 0.001
    """Minimum gap size to consider as forbidden energy level"""

    equilibration_window: int = 1000
    """Window size for equilibration detection (in snapshots)"""

    # ========================================================================
    # Success Criteria (Same as V3)
    # ========================================================================

    max_cloud_drift_percent: float = 10.0
    """Maximum allowable cloud radius drift percentage"""

    max_fragment_escape_radius: float = 20.0
    """Fragments beyond this radius considered escaped"""

    min_stability_duration: int = 50000
    """Minimum ticks for cloud to remain stable (extended for V4)"""


# ============================================================================
# Preset Configurations
# ============================================================================

def get_quantization_config() -> ConfigV4:
    """Get configuration for quantization study (100k ticks)."""
    return ConfigV4()


def get_short_test_config() -> ConfigV4:
    """Get configuration for quick testing (10k ticks like V3)."""
    config = ConfigV4()
    config.num_ticks = 10000
    config.snapshot_interval = 100
    config.detailed_snapshot_interval = 500
    return config


def get_ultra_long_config() -> ConfigV4:
    """
    Get configuration for ultra-long quantization study (200k ticks).

    Uses V3 PROVEN baseline (50 fragments) with extended duration.
    This configuration is RECOMMENDED after 100-fragment runaway.
    """
    config = ConfigV4()
    config.n_fragments = 50  # V3 proven baseline
    config.num_ticks = 200000  # 2× longer than V3 for quantization
    config.snapshot_interval = 200
    config.detailed_snapshot_interval = 2000
    config.progress_report_interval = 1000  # More frequent updates
    return config


def get_high_resolution_config() -> ConfigV4:
    """Get configuration with more fragments for smoother quantization."""
    config = ConfigV4()
    config.n_fragments = 100
    config.radial_bins = 150
    config.energy_histogram_bins = 75
    return config


def get_high_res_ultra_long_config() -> ConfigV4:
    """
    Get configuration with 100 fragments and 200k ticks.

    Tests natural fragment ejection hypothesis: collisions should self-regulate
    fragment count by ejecting excess fragments from the cloud.
    """
    config = ConfigV4()
    config.n_fragments = 100  # Test with 2× fragments
    config.num_ticks = 200000  # 2× longer for equilibration
    config.snapshot_interval = 200
    config.detailed_snapshot_interval = 2000
    config.progress_report_interval = 1000  # More frequent updates
    config.radial_bins = 150
    config.energy_histogram_bins = 75
    config.electron_total_mass = 0.1  # Keep same total mass (fragments are lighter)
    return config


if __name__ == "__main__":
    # Print quantization study configuration
    config = get_quantization_config()
    print("=" * 70)
    print("V4 Quantization Study Configuration")
    print("=" * 70)
    print(f"\nPhysics Parameters (V3 scaled baseline):")
    print(f"  Fragments: {config.n_fragments}")
    print(f"  Proton mass: {config.proton_mass}")
    print(f"  Electron mass: {config.electron_total_mass}")
    print(f"  Coupling constant: {config.coupling_constant}")
    print(f"  Jitter strength: {config.jitter_strength}")

    print(f"\nSimulation Parameters:")
    print(f"  Total ticks: {config.num_ticks:,}")
    print(f"  Expected runtime: ~{config.num_ticks // 10000 * 45:.0f} seconds ({config.num_ticks // 10000 * 45 // 60:.0f} minutes)")
    print(f"  Snapshots: {config.num_ticks // config.snapshot_interval}")
    print(f"  Detailed snapshots: {config.num_ticks // config.detailed_snapshot_interval}")

    print(f"\nQuantization Analysis:")
    print(f"  Radial bins: {config.radial_bins}")
    print(f"  Energy bins: {config.energy_histogram_bins}")
    print(f"  Shell detection prominence: {config.shell_detection_prominence}")
    print(f"  Energy gap threshold: {config.energy_gap_threshold}")

    print("\n" + "=" * 70)
