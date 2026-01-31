"""
Configuration for V5 Integer Arithmetic Experiments

All V4 validated parameters converted to scaled integers (SCALE = 10^8).

Author: V5 Integer Conversion
Date: 2026-01-24
Based on: V4 validated parameters (200k ticks, 6.52% drift)
"""

from fixed_point import FixedPoint


class ConfigV5:
    """Configuration with scaled integer parameters."""

    # ========================================================================
    # Fixed-Point Scaling
    # ========================================================================

    SCALE = FixedPoint.SCALE  # 100_000_000 (10^8)

    # ========================================================================
    # Fragment Cloud Parameters (V4 validated)
    # ========================================================================

    n_fragments = 50  # Number of electron fragments

    # Initial distribution (Gaussian)
    r_mean = FixedPoint.from_float(2.0)  # Mean radius
    r_std = FixedPoint.from_float(0.5)   # Radius standard deviation
    v_mean = FixedPoint.from_float(0.01) # Mean velocity magnitude
    v_std = FixedPoint.from_float(0.005) # Velocity standard deviation

    # ========================================================================
    # Physics Parameters (V4 validated - scaled integers)
    # ========================================================================

    # Masses
    proton_mass = FixedPoint.from_float(100.0)  # 10_000_000_000
    electron_mass_total = FixedPoint.from_float(0.1)  # Total electron mass
    fragment_mass = electron_mass_total // n_fragments  # Mass per fragment

    # Energies
    proton_energy = FixedPoint.from_float(1000.0)  # 100_000_000_000
    electron_energy_total = FixedPoint.from_float(50.0)  # Total electron energy
    fragment_energy = electron_energy_total // n_fragments  # Energy per fragment

    # Field coupling
    coupling_constant = FixedPoint.from_float(0.001)  # 100_000

    # Zero-point jitter (CRITICAL - V4 validated optimal)
    jitter_strength = FixedPoint.from_float(0.0005)  # 50_000

    # Collision physics (V4 validated optimal)
    collision_radius = FixedPoint.from_float(0.5)  # 50_000_000
    restitution = FixedPoint.from_float(0.8)  # 80_000_000

    # ========================================================================
    # Harmonic Confinement Field Parameters (F = -k*r)
    # ========================================================================

    # Spring constant (controls confinement strength)
    harmonic_k = FixedPoint.from_float(0.0000003)  # 30 (scaled)
    # Force = -k × (x, y) - linear restoring force
    # At r=2.0: F = -0.0000006 (pulls toward origin)
    # Tuned for r≈2 equilibrium (k=0.000001 gave r≈1.2)

    # ========================================================================
    # Simulation Parameters
    # ========================================================================

    num_ticks = 200_000  # Total simulation ticks
    progress_report_interval = 1_000  # Report every N ticks

    # ========================================================================
    # Validation Thresholds
    # ========================================================================

    max_drift_percent = 10.0  # Maximum cloud radius drift


def get_validation_200k_config():
    """Get configuration for 200k validation run."""
    return ConfigV5()


if __name__ == "__main__":
    # Print configuration
    config = ConfigV5()

    print("V5 Configuration (Scaled Integer Parameters)")
    print("=" * 70)
    print(f"SCALE: {config.SCALE:,}")
    print()
    print("Fragment Cloud:")
    print(f"  n_fragments: {config.n_fragments}")
    print(f"  r_mean: {FixedPoint.to_float(config.r_mean):.4f} ({config.r_mean:,})")
    print(f"  r_std: {FixedPoint.to_float(config.r_std):.4f} ({config.r_std:,})")
    print(f"  v_mean: {FixedPoint.to_float(config.v_mean):.6f} ({config.v_mean:,})")
    print(f"  v_std: {FixedPoint.to_float(config.v_std):.6f} ({config.v_std:,})")
    print()
    print("Physics Parameters:")
    print(f"  proton_mass: {FixedPoint.to_float(config.proton_mass):.2f} ({config.proton_mass:,})")
    print(f"  fragment_mass: {FixedPoint.to_float(config.fragment_mass):.6f} ({config.fragment_mass:,})")
    print(f"  fragment_energy: {FixedPoint.to_float(config.fragment_energy):.4f} ({config.fragment_energy:,})")
    print(f"  coupling_constant: {FixedPoint.to_float(config.coupling_constant):.6f} ({config.coupling_constant:,})")
    print(f"  jitter_strength: {FixedPoint.to_float(config.jitter_strength):.6f} ({config.jitter_strength:,}) [CRITICAL]")
    print(f"  collision_radius: {FixedPoint.to_float(config.collision_radius):.2f} ({config.collision_radius:,}) [OPTIMAL]")
    print(f"  restitution: {FixedPoint.to_float(config.restitution):.2f} ({config.restitution:,})")
    print()
    print("Gamma Field (Radial Potential):")
    print(f"  gamma_well_k: {FixedPoint.to_float(config.gamma_well_k):.2f} ({config.gamma_well_k:,}) [CONFINEMENT]")
    print(f"  field_coupling_constant: {FixedPoint.to_float(config.field_coupling_constant):.6f} ({config.field_coupling_constant:,})")
    print()
    print("Simulation:")
    print(f"  num_ticks: {config.num_ticks:,}")
    print(f"  progress_report_interval: {config.progress_report_interval:,}")
    print("=" * 70)
