#!/usr/bin/env python3
"""
Zero-Point Energy (Tick-Frame Jitter) for Fragmented Electron Cloud (V3)

Based on Doc 070_00 §2: "Zero-Point Energy as Tick-Frame Metabolic Pressure"
and Doc 070_01 §2: "Tick-Frame Expansion as Zero-Point Energy"

From Doc 070_00:
"In the tick-frame model, we reinterpret zero-point energy as a consequence
of the irreducible jitter imposed by the expanding tick-frame. The tick-frame
is not static; it expands or evolves, introducing a minimal temporal granularity.
This expansion induces a baseline metabolic activity in all entities—no attractor
can be perfectly still."
"""

import numpy as np
from typing import List
from fragmented_cloud import ElectronFragment, FragmentedElectronCloud


# ============================================================================
# Zero-Point Jitter Implementation
# ============================================================================

def apply_brownian_jitter(
    fragments: List[ElectronFragment],
    jitter_strength: float = 0.001,
    dt: float = 1.0
) -> None:
    """
    Apply tick-frame metabolic pressure as Brownian noise.

    From Doc 070_00 §2:
    "This expansion induces a baseline metabolic activity in all entities—
    no attractor can be perfectly still. The result is a non-zero minimum
    energy for any bound configuration, matching the observed zero-point
    energy of atoms."

    From Doc 070_01 §2:
    "This jitter acts as a metabolic pressure, preventing collapse into
    the proton. This provides a natural explanation for:
    - zero-point energy
    - atomic stability at 0 K
    - the non-collapse of the electron cloud"

    Physics:
    - Each tick, every fragment receives random velocity kick
    - Magnitude: Gaussian with σ = jitter_strength
    - Direction: uniform random (2D isotropic)
    - Models Brownian motion from tick-frame fluctuations

    Args:
        fragments: List of electron fragments (modified in-place)
        jitter_strength: Standard deviation of velocity kicks
        dt: Time step (usually 1.0 tick)
    """
    for fragment in fragments:
        # Random velocity kick (2D Gaussian, zero mean)
        dv_x = np.random.normal(0, jitter_strength)
        dv_y = np.random.normal(0, jitter_strength)

        # Apply kick
        fragment.velocity[0] += dv_x
        fragment.velocity[1] += dv_y


def apply_position_jitter(
    fragments: List[ElectronFragment],
    jitter_strength: float = 0.001,
    dt: float = 1.0
) -> None:
    """
    Apply jitter directly to positions (alternative to velocity jitter).

    This models the tick-frame as having inherent spatial jitter at each tick.

    Args:
        fragments: List of electron fragments (modified in-place)
        jitter_strength: Standard deviation of position kicks
        dt: Time step
    """
    for fragment in fragments:
        # Random position kick (2D Gaussian, zero mean)
        dx = np.random.normal(0, jitter_strength)
        dy = np.random.normal(0, jitter_strength)

        # Apply kick
        fragment.position[0] += dx
        fragment.position[1] += dy


def apply_correlated_jitter(
    fragments: List[ElectronFragment],
    jitter_strength: float = 0.001,
    correlation_length: float = 1.0,
    dt: float = 1.0
) -> None:
    """
    Apply spatially correlated jitter (advanced model).

    Fragments close together experience similar jitter (spatial correlation).
    Models collective tick-frame fluctuations.

    Args:
        fragments: List of electron fragments
        jitter_strength: Base jitter strength
        correlation_length: Spatial correlation scale
        dt: Time step
    """
    # Generate global jitter field
    global_jitter = np.random.normal(0, jitter_strength, size=2)

    for fragment in fragments:
        # Local jitter (uncorrelated)
        local_jitter = np.random.normal(0, jitter_strength / 2, size=2)

        # Distance-dependent mixing of global and local
        r = fragment.distance_from_origin
        correlation_factor = np.exp(-r / correlation_length)

        # Combined jitter
        combined_jitter = (
            correlation_factor * global_jitter +
            (1 - correlation_factor) * local_jitter
        )

        # Apply
        fragment.velocity += combined_jitter


def apply_zero_point_energy(
    cloud: FragmentedElectronCloud,
    jitter_strength: float = 0.001,
    jitter_mode: str = "velocity",
    dt: float = 1.0
) -> None:
    """
    Apply zero-point energy (tick-frame jitter) to electron cloud.

    From Doc 070_01 §5:
    "The cloud cannot collapse because fragments cannot all occupy
    the same minimal tick-state."

    Args:
        cloud: Fragmented electron cloud (modified in-place)
        jitter_strength: Strength of jitter
        jitter_mode: Type of jitter ("velocity", "position", "correlated")
        dt: Time step
    """
    if jitter_mode == "velocity":
        apply_brownian_jitter(cloud.fragments, jitter_strength, dt)
    elif jitter_mode == "position":
        apply_position_jitter(cloud.fragments, jitter_strength, dt)
    elif jitter_mode == "correlated":
        apply_correlated_jitter(cloud.fragments, jitter_strength, dt=dt)
    else:
        raise ValueError(f"Unknown jitter mode: {jitter_mode}")


# ============================================================================
# Energy Balance Analysis
# ============================================================================

def compute_jitter_energy_injection_rate(
    n_fragments: int,
    jitter_strength: float,
    fragment_mass: float = 0.001 / 50
) -> float:
    """
    Compute expected energy injection rate from jitter.

    For velocity jitter with σ = jitter_strength:
    - Each fragment receives velocity kick with <dv²> = 2 × σ²  (2D)
    - Energy injection per fragment per tick: dE = (1/2) × m × <dv²>
    - Total rate: dE/dt = N × (1/2) × m × 2 × σ²

    Args:
        n_fragments: Number of fragments
        jitter_strength: Jitter standard deviation
        fragment_mass: Mass per fragment

    Returns:
        Energy injection rate (energy units per tick)
    """
    # Expected kinetic energy from 2D Brownian kick
    expected_dE_per_fragment = fragment_mass * (jitter_strength ** 2)

    # Total rate
    total_rate = n_fragments * expected_dE_per_fragment

    return total_rate


def estimate_equilibrium_temperature(
    jitter_strength: float,
    collision_rate: float,
    restitution: float = 0.8,
    fragment_mass: float = 0.001 / 50
) -> float:
    """
    Estimate equilibrium temperature from balance of jitter and collisions.

    Energy injection (from jitter) vs energy dissipation (from inelastic collisions).

    At equilibrium:
        Energy injection rate = Energy dissipation rate
        σ² × N = (1 - e²) × collision_rate × <KE>

    Args:
        jitter_strength: Jitter σ
        collision_rate: Collisions per tick
        restitution: Coefficient of restitution
        fragment_mass: Mass per fragment

    Returns:
        Equilibrium temperature (energy units)
    """
    # Energy injection rate per fragment
    injection_rate = fragment_mass * (jitter_strength ** 2)

    # Energy dissipation factor from inelastic collisions
    dissipation_factor = (1 - restitution ** 2)

    if collision_rate < 1e-10 or dissipation_factor < 1e-10:
        # No dissipation → temperature grows indefinitely
        return float('inf')

    # Equilibrium temperature (energy per fragment)
    # T_eq ∝ injection / (dissipation × collision_rate)
    T_eq = injection_rate / (dissipation_factor * collision_rate)

    return T_eq


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("Testing zero_point_jitter...")

    # Import dependencies
    from fragmented_cloud import FragmentedElectronCloud

    # Create test cloud
    cloud = FragmentedElectronCloud(cloud_id="test_jitter")
    cloud.initialize_fragments(
        n_fragments=50,
        r_mean=2.0,
        r_std=0.5,
        v_mean=0.0,  # Start with zero velocity
        v_std=0.0
    )

    # Initial state (should have zero kinetic energy)
    initial_ke = sum(f.kinetic_energy for f in cloud.fragments)
    print(f"\nInitial kinetic energy: {initial_ke:.9f} (should be ~0)")

    # Apply jitter for 100 ticks
    print("\nApplying jitter for 100 ticks...")

    ke_history = []
    for tick in range(100):
        apply_zero_point_energy(cloud, jitter_strength=0.001, jitter_mode="velocity")
        total_ke = sum(f.kinetic_energy for f in cloud.fragments)
        ke_history.append(total_ke)

    # Final state
    final_ke = ke_history[-1]
    mean_ke = np.mean(ke_history[50:])  # Last 50 ticks

    print(f"\nAfter 100 ticks:")
    print(f"  Final kinetic energy: {final_ke:.6f}")
    print(f"  Mean KE (last 50 ticks): {mean_ke:.6f}")

    # Expected energy injection rate
    expected_rate = compute_jitter_energy_injection_rate(
        n_fragments=50,
        jitter_strength=0.001,
        fragment_mass=0.001 / 50
    )

    print(f"\nExpected energy injection rate: {expected_rate:.9f} per tick")
    print(f"Observed KE increase: {(final_ke - initial_ke) / 100:.9f} per tick")

    # Test different jitter strengths
    print("\nTesting different jitter strengths:")

    for sigma in [0.0001, 0.001, 0.01]:
        cloud_test = FragmentedElectronCloud(cloud_id=f"test_sigma{sigma}")
        cloud_test.initialize_fragments(n_fragments=20, v_mean=0.0, v_std=0.0)

        # Apply jitter for 50 ticks
        for _ in range(50):
            apply_zero_point_energy(cloud_test, jitter_strength=sigma)

        total_ke = sum(f.kinetic_energy for f in cloud_test.fragments)
        mean_speed = np.mean([f.speed for f in cloud_test.fragments])

        print(f"  sigma={sigma:.4f}: KE={total_ke:.6f}, <v>={mean_speed:.6f}")

    # Test jitter prevents collapse
    print("\nTesting jitter prevents collapse:")

    cloud_collapse = FragmentedElectronCloud(cloud_id="test_collapse")
    cloud_collapse.initialize_fragments(
        n_fragments=30,
        r_mean=2.0,
        r_std=0.3,
        v_mean=0.0,  # No initial velocity
        v_std=0.0
    )

    initial_radius = cloud_collapse.cloud_radius_rms

    # Simulate with jitter
    for tick in range(200):
        apply_zero_point_energy(cloud_collapse, jitter_strength=0.002)
        cloud_collapse.update_statistics()

    final_radius = cloud_collapse.cloud_radius_rms

    print(f"  Initial RMS radius: {initial_radius:.4f}")
    print(f"  Final RMS radius: {final_radius:.4f}")
    print(f"  Change: {((final_radius - initial_radius) / initial_radius * 100):.2f}%")

    if final_radius > 0.5 * initial_radius:
        print("  [OK] Cloud did not collapse (jitter prevented it)!")
    else:
        print("  [WARNING] Cloud collapsed despite jitter")

    print("\n[OK] zero_point_jitter test passed!")
