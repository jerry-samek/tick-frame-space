"""
V5 Integer Arithmetic Validation Experiment

200k ticks validation with 50 fragments.
Compares integer arithmetic results against V4 float baseline.

Author: V5 Integer Conversion
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
from harmonic_field_v5 import HarmonicField


def initialize_cloud(config: ConfigV5) -> FragmentedCloudV5:
    """Initialize fragmented electron cloud with random positions/velocities."""
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

    # Update statistics
    cloud.update_statistics()

    print(f"  Mean radius: {FixedPoint.to_float(cloud.cloud_radius_mean):.4f}")
    print(f"  RMS radius: {FixedPoint.to_float(cloud.cloud_radius_rms):.4f}")
    print(f"  Total mass: {FixedPoint.to_float(cloud.total_mass):.6f}")
    print(f"  Total energy: {FixedPoint.to_float(cloud.total_energy):.4f}")
    print()

    return cloud


def run_simulation(config: ConfigV5):
    """Run 200k tick simulation."""
    print("=" * 70)
    print("V5 Integer Arithmetic Validation Experiment")
    print("=" * 70)
    print()
    print(f"Configuration:")
    print(f"  Fragments: {config.n_fragments}")
    print(f"  Total ticks: {config.num_ticks:,}")
    print(f"  Jitter strength: {FixedPoint.to_float(config.jitter_strength):.6f}")
    print(f"  Collision radius: {FixedPoint.to_float(config.collision_radius):.2f}")
    print(f"  Restitution: {FixedPoint.to_float(config.restitution):.2f}")
    print()

    # Initialize cloud
    cloud = initialize_cloud(config)
    initial_radius_rms = cloud.cloud_radius_rms

    # Initialize harmonic confinement field
    harmonic_field = HarmonicField(config.harmonic_k)

    print(f"Harmonic field initialized:")
    print(f"  Spring constant k = {FixedPoint.to_float(config.harmonic_k):.8f}")
    print(f"  Force at r=2.0: F = {FixedPoint.to_float(config.harmonic_k) * 2.0:.8f}")
    print()

    # Statistics tracking
    radii_history = []
    collision_rate_history = []

    start_time = time.time()

    # Main simulation loop
    print(f"Running {config.num_ticks:,} ticks...")
    print(f"Progress reports every {config.progress_report_interval:,} ticks...")
    print()

    for tick in range(config.num_ticks):
        # 1. Apply zero-point jitter
        apply_jitter_v5(cloud, config.jitter_strength)

        # 2. Apply harmonic confinement force
        for frag in cloud.fragments:
            # Compute force at fragment position: F = -k × (x, y)
            force_x, force_y = harmonic_field.compute_force(frag.x, frag.y)

            # Acceleration: a = F / mass
            accel_x = FixedPoint.divide(force_x, frag.mass)
            accel_y = FixedPoint.divide(force_y, frag.mass)

            # Update velocity
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

        # Track history
        radii_history.append(cloud.cloud_radius_rms)
        if tick > 0:
            collision_rate_history.append(n_collisions)

        # Progress report
        if (tick + 1) % config.progress_report_interval == 0:
            elapsed = time.time() - start_time
            eta = elapsed / (tick + 1) * (config.num_ticks - tick - 1)

            avg_collisions = sum(collision_rate_history[-1000:]) / min(len(collision_rate_history), 1000)

            print(f"[{tick+1:7d}/{config.num_ticks:7d}] ({100*(tick+1)/config.num_ticks:5.1f}%) "
                  f"{elapsed:.1f}s elapsed, ETA: {eta:.1f}s")
            print(f"  r_rms={FixedPoint.to_float(cloud.cloud_radius_rms):.4f}, "
                  f"KE={FixedPoint.to_float(cloud.total_kinetic_energy):.6f}, "
                  f"L_z={FixedPoint.to_float(cloud.angular_momentum):.6f}")
            print(f"  collisions={cloud.total_collisions} total ({avg_collisions:.2f}/tick)")
            print()

    elapsed_total = time.time() - start_time

    # Final statistics
    print()
    print("=" * 70)
    print("FINAL RESULTS")
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

    avg_collision_rate = cloud.total_collisions / config.num_ticks
    print(f"Collisions:")
    print(f"  Total: {cloud.total_collisions:,}")
    print(f"  Average per tick: {avg_collision_rate:.2f}")
    print()

    print(f"Performance:")
    print(f"  Total time: {elapsed_total:.1f}s")
    print(f"  Ticks per second: {config.num_ticks / elapsed_total:.1f}")
    print()

    print("=" * 70)

    # Validation
    if drift_percent < config.max_drift_percent:
        print("[PASS] Cloud radius drift < 10%")
    else:
        print(f"[FAIL] Cloud radius drift = {drift_percent:.2f}% >= 10%")

    print("=" * 70)


if __name__ == "__main__":
    config = ConfigV5()
    run_simulation(config)
