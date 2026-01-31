"""
Quick 10k tick confinement test for V5 with tuned field_coupling_constant.

Tests whether field_coupling_constant = 0.1 provides adequate confinement.
Target: < 10% cloud radius drift over 10k ticks.

Author: V5 Parameter Tuning
Date: 2026-01-24
"""

import time
import math
from config_v5 import ConfigV5
from fragment_v5 import FragmentV5, FragmentedCloudV5
from collision_v5 import apply_all_collisions_v5
from jitter_v5 import apply_jitter_v5
from random_v5 import gaussian_int, uniform_angle
from fixed_point import FixedPoint
from gamma_field_v5 import RadialGammaField


def initialize_cloud(config: ConfigV5) -> FragmentedCloudV5:
    """Initialize fragmented electron cloud."""
    cloud = FragmentedCloudV5("electron_cloud_v5")

    print(f"Initializing {config.n_fragments} electron fragments...")

    for i in range(config.n_fragments):
        # Random radius (Gaussian)
        r = gaussian_int(config.r_mean, config.r_std)
        if r < FixedPoint.from_float(0.1):
            r = FixedPoint.from_float(0.1)

        # Random angle
        theta = uniform_angle()

        # Position
        x = FixedPoint.multiply(r, FixedPoint.from_float(math.cos(FixedPoint.to_float(theta))))
        y = FixedPoint.multiply(r, FixedPoint.from_float(math.sin(FixedPoint.to_float(theta))))

        # Random velocity magnitude (Gaussian)
        v_mag = gaussian_int(config.v_mean, config.v_std)
        if v_mag < 0:
            v_mag = 0

        # Random velocity angle
        v_angle = uniform_angle()

        # Velocity
        vx = FixedPoint.multiply(v_mag, FixedPoint.from_float(math.cos(FixedPoint.to_float(v_angle))))
        vy = FixedPoint.multiply(v_mag, FixedPoint.from_float(math.sin(FixedPoint.to_float(v_angle))))

        frag = FragmentV5(
            fragment_id=f"efrag_{i}",
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            energy=config.fragment_energy,
            mass=config.fragment_mass,
        )

        cloud.add_fragment(frag)

    cloud.update_statistics()

    print(f"  Mean radius: {FixedPoint.to_float(cloud.cloud_radius_mean):.4f}")
    print(f"  RMS radius: {FixedPoint.to_float(cloud.cloud_radius_rms):.4f}")
    print()

    return cloud


def run_10k_test():
    """Run 10k tick confinement test."""
    print("=" * 70)
    print("V5 10k Tick Confinement Test")
    print("Testing field_coupling_constant = 0.1")
    print("=" * 70)
    print()

    config = ConfigV5()
    config.num_ticks = 10_000
    config.progress_report_interval = 1_000

    print(f"Configuration:")
    print(f"  Fragments: {config.n_fragments}")
    print(f"  Total ticks: {config.num_ticks:,}")
    print(f"  Jitter strength: {FixedPoint.to_float(config.jitter_strength):.6f}")
    print(f"  Gamma well k: {FixedPoint.to_float(config.gamma_well_k):.2f}")
    print(f"  Field coupling: {FixedPoint.to_float(config.field_coupling_constant):.3f}")
    print(f"  Collision radius: {FixedPoint.to_float(config.collision_radius):.2f}")
    print()

    # Initialize cloud
    cloud = initialize_cloud(config)
    initial_radius_rms = cloud.cloud_radius_rms

    # Initialize gamma field
    gamma_field = RadialGammaField(config.gamma_well_k)

    print(f"Running {config.num_ticks:,} ticks...")
    print()

    start_time = time.time()

    # Main simulation loop
    for tick in range(config.num_ticks):
        # 1. Apply zero-point jitter
        apply_jitter_v5(cloud, config.jitter_strength)

        # 2. Apply gamma field gradient forces
        for frag in cloud.fragments:
            grad_x, grad_y = gamma_field.compute_gradient(frag.x, frag.y)
            accel_x = FixedPoint.multiply(config.field_coupling_constant, grad_x)
            accel_y = FixedPoint.multiply(config.field_coupling_constant, grad_y)
            frag.vx += accel_x
            frag.vy += accel_y

        # 3. Process collisions
        n_collisions = apply_all_collisions_v5(
            cloud,
            collision_radius_scaled=config.collision_radius,
            restitution_scaled=config.restitution,
            current_tick=tick
        )

        # 4. Update positions
        for frag in cloud.fragments:
            frag.update_position()

        # 5. Update statistics
        cloud.update_statistics()

        # Progress report
        if (tick + 1) % config.progress_report_interval == 0:
            elapsed = time.time() - start_time
            print(f"[{tick+1:7d}/{config.num_ticks:7d}] ({100*(tick+1)/config.num_ticks:5.1f}%) {elapsed:.1f}s")
            print(f"  r_rms={FixedPoint.to_float(cloud.cloud_radius_rms):.4f}, "
                  f"KE={FixedPoint.to_float(cloud.total_kinetic_energy):.6f}")
            print()

    elapsed_total = time.time() - start_time

    # Final results
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()

    final_radius_rms = cloud.cloud_radius_rms
    initial_radius_float = FixedPoint.to_float(initial_radius_rms)
    final_radius_float = FixedPoint.to_float(final_radius_rms)

    drift_percent = abs(final_radius_float - initial_radius_float) / initial_radius_float * 100

    print(f"Cloud radius:")
    print(f"  Initial RMS: {initial_radius_float:.4f}")
    print(f"  Final RMS: {final_radius_float:.4f}")
    print(f"  Drift: {drift_percent:.2f}%")
    print()

    print(f"Collisions:")
    print(f"  Total: {cloud.total_collisions:,}")
    print()

    print(f"Performance:")
    print(f"  Total time: {elapsed_total:.1f}s")
    print(f"  Ticks per second: {config.num_ticks / elapsed_total:.1f}")
    print()

    print("=" * 70)

    if drift_percent < 10.0:
        print(f"[PASS] Cloud radius drift = {drift_percent:.2f}% < 10%")
        print("Confinement is adequate. Proceeding to 200k validation...")
    else:
        print(f"[FAIL] Cloud radius drift = {drift_percent:.2f}% >= 10%")
        print("Need to increase field_coupling_constant further.")

    print("=" * 70)


if __name__ == "__main__":
    run_10k_test()
