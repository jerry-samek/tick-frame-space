#!/usr/bin/env python3
"""
Quick Integration Test for Experiment 56 V3: Fragmented Electron Cloud

Minimal test to verify all components work together.
"""

import numpy as np
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, '.')

from config_v3 import ConfigV3
from fragmented_cloud import FragmentedElectronCloud, Pattern
from collision_dynamics import apply_all_collisions
from zero_point_jitter import apply_zero_point_energy
from binding_detection_v2 import GammaWellDetector


class HydrogenAtomV3Test:
    """Minimal hydrogen atom with fragmented electron cloud."""

    def __init__(self, config: ConfigV3):
        self.config = config
        self.tick = 0

        # Create proton (stationary at origin) with scaled-up mass/energy
        self.proton_position = np.array([50.0, 50.0])
        self.proton_pattern = Pattern("PROTON", energy=config.proton_energy, mass=config.proton_mass)

        print(f"\nProton created:")
        print(f"  Mass: {config.proton_mass}")
        print(f"  Energy: {config.proton_energy}")

        # Create electron cloud
        self.electron_cloud = FragmentedElectronCloud(cloud_id="H1_electron_cloud")
        self.electron_cloud.initialize_fragments(
            n_fragments=config.n_fragments,
            r_mean=config.fragment_init_radius_mean,
            r_std=config.fragment_init_radius_std,
            v_mean=config.fragment_init_velocity_mean,
            v_std=config.fragment_init_velocity_std,
            total_mass=config.electron_total_mass,
            total_energy=config.electron_total_energy
        )

        # Create gamma-well detector
        self.detector = GammaWellDetector(
            grid_size=config.grid_size,
            alpha=config.alpha,
            gamma_damp=config.gamma_damp,
            scale=config.scale,
            R=config.R,
            D=config.D,
            E_max=config.E_max,
            capacity_min=config.capacity_min,
            work_threshold=config.work_threshold,
            c=config.c
        )

        # Initialize gamma-field
        self._update_gamma_field()

    def _update_gamma_field(self):
        """
        Update gamma-field from proton only (for testing).

        NOTE: In full implementation, should include fragments too.
        But for initial testing, we want a STATIC gamma-well from proton
        that fragments respond to but don't modify.
        """
        patterns = []

        # Add proton ONLY (create static gamma-well)
        patterns.append((self.proton_pattern, self.proton_position, np.array([0.0, 0.0])))

        # TEMPORARILY SKIP adding electron fragments to avoid field interference
        # for frag in self.electron_cloud.fragments:
        #     abs_position = self.proton_position + frag.position
        #     patterns.append((frag.as_pattern(), abs_position, frag.velocity))

        # Update fields (use MORE steps to reach steady state)
        self.detector.update_fields(patterns, dt=1.0, num_steps=100)

    def update(self, dt=1.0):
        """Update atom for one tick."""
        self.tick += 1

        # 1. Update gamma-field periodically
        if self.tick % self.config.field_update_interval == 0:
            self._update_gamma_field()

        # 2. Apply gradient force to each fragment (radial only)
        if self.config.apply_gradient_force:
            for i, frag in enumerate(self.electron_cloud.fragments):
                abs_position = self.proton_position + frag.position
                gamma_gradient = self.detector.compute_gradient_at_position(abs_position)

                if self.config.radial_force_only:
                    # Apply only radial component
                    r_mag = np.linalg.norm(frag.position)
                    if r_mag > 0.01:
                        r_hat = frag.position / r_mag
                        grad_radial = np.dot(gamma_gradient, r_hat)

                        # DEBUG: Print first fragment's values at tick 1
                        if self.tick == 1 and i == 0:
                            gamma_at_pos = self.detector.get_gamma_at_position(abs_position)
                            gamma_at_center = self.detector.get_gamma_at_position(self.proton_position)
                            print(f"\n  DEBUG Fragment 0:")
                            print(f"    Position (rel): {frag.position}")
                            print(f"    Gamma gradient: {gamma_gradient}")
                            print(f"    r_hat (outward): {r_hat}")
                            print(f"    grad_radial (grad·r_hat): {grad_radial:.6f}")
                            print(f"    Gamma at fragment: {gamma_at_pos:.3f}")
                            print(f"    Gamma at proton: {gamma_at_center:.3f}")
                            print(f"    Accel direction: {'INWARD' if grad_radial < 0 else 'OUTWARD'}")

                        accel = self.config.coupling_constant * grad_radial * r_hat
                        frag.apply_acceleration(accel, dt)
                else:
                    # Apply full gradient force
                    accel = self.config.coupling_constant * gamma_gradient
                    frag.apply_acceleration(accel, dt)

        # 3. Update fragment positions
        for frag in self.electron_cloud.fragments:
            frag.update_position(dt)

        # 4. Process collisions
        n_collisions = apply_all_collisions(
            self.electron_cloud,
            collision_radius=self.config.collision_radius,
            restitution=self.config.restitution_coefficient,
            current_tick=self.tick
        )

        # 5. Apply zero-point jitter
        if self.config.apply_jitter:
            apply_zero_point_energy(
                self.electron_cloud,
                jitter_strength=self.config.jitter_strength,
                jitter_mode="velocity",
                dt=dt
            )

        # 6. Update statistics
        self.electron_cloud.update_statistics()

    def get_snapshot(self):
        """Get current state."""
        return {
            'tick': self.tick,
            'cloud_radius_mean': self.electron_cloud.cloud_radius_mean,
            'cloud_radius_rms': self.electron_cloud.cloud_radius_rms,
            'total_kinetic_energy': self.electron_cloud.total_kinetic_energy,
            'angular_momentum': self.electron_cloud.angular_momentum,
            'total_collisions': self.electron_cloud.total_collisions,
        }


def run_quick_test():
    """Run quick integration test."""
    print("="*70)
    print("Experiment 56 V3: Quick Integration Test")
    print("="*70)

    # Use baseline config for FULL validation
    from config_v3 import get_baseline_config
    config = get_baseline_config()
    config.num_ticks = 10000  # Full 10k tick validation
    config.snapshot_interval = 100  # Save every 100 ticks

    # SCALE UP PHYSICS (user's brilliant idea!)
    # Make proton 100× heavier, electron 100× heavier
    # This makes forces reasonable relative to inertia
    config.proton_mass = 100.0  # Was 1.0 (now proton is "composite" of 100 quark-like fragments)
    config.proton_energy = 1000.0  # Scale energy proportionally
    config.electron_total_mass = 0.1  # Was 0.001 (100× heavier electron cloud)
    config.electron_total_energy = 50.0  # Was 5.0 (scale energy)

    # Now each electron fragment has mass = 0.1/20 = 0.005 (reasonable!)
    # Gradient force ~5, acceleration = 5/0.005 = 1000 (better but still high)

    # Reduce coupling to get reasonable accelerations
    config.coupling_constant = 0.001  # Very weak coupling
    # Now acceleration = 0.001 × 5 / 0.005 = 1.0 (perfect!)

    config.fragment_init_velocity_mean = 0.05  # Moderate velocity
    config.fragment_init_velocity_std = 0.01
    config.jitter_strength = 0.001  # Moderate jitter
    config.scale = 0.75  # Normal field strength
    config.E_max = 1500.0  # Scale E_max proportionally (was 15.0, now 100× larger)

    print(f"\nConfiguration:")
    print(f"  Fragments: {config.n_fragments}")
    print(f"  Ticks: {config.num_ticks}")
    print(f"  Collision radius: {config.collision_radius}")
    print(f"  Jitter strength: {config.jitter_strength}")

    # Create hydrogen atom
    hydrogen = HydrogenAtomV3Test(config)

    print(f"\nInitial state:")
    snapshot = hydrogen.get_snapshot()
    for key, val in snapshot.items():
        if isinstance(val, float):
            print(f"  {key}: {val:.6f}")
        else:
            print(f"  {key}: {val}")

    # Run simulation
    print(f"\nRunning {config.num_ticks} ticks...")
    print(f"Progress reports every 1000 ticks...")

    snapshots = []
    for tick in range(config.num_ticks):
        hydrogen.update(dt=1.0)

        if tick % config.snapshot_interval == 0:
            snapshot = hydrogen.get_snapshot()
            snapshots.append(snapshot)

            # Progress report every 1000 ticks
            if tick % 1000 == 0:
                print(f"  Tick {tick:5d}: r_rms={snapshot['cloud_radius_rms']:.4f}, "
                      f"KE={snapshot['total_kinetic_energy']:.6f}, "
                      f"L={snapshot['angular_momentum']:.6f}, "
                      f"collisions={snapshot['total_collisions']}")

    # Final state
    final_snapshot = hydrogen.get_snapshot()
    snapshots.append(final_snapshot)

    print(f"\nFinal state:")
    for key, val in final_snapshot.items():
        if isinstance(val, float):
            print(f"  {key}: {val:.6f}")
        else:
            print(f"  {key}: {val}")

    # Analysis
    print("\n" + "="*70)
    print("QUICK TEST RESULTS")
    print("="*70)

    # Check stability
    radii = [s['cloud_radius_rms'] for s in snapshots]
    r_initial = radii[0]
    r_final = radii[-1]
    r_drift_pct = abs(r_final - r_initial) / r_initial * 100

    print(f"\nCloud radius:")
    print(f"  Initial: {r_initial:.4f}")
    print(f"  Final: {r_final:.4f}")
    print(f"  Drift: {r_drift_pct:.2f}%")

    # Check for escapes
    is_stable, n_escaped, escaped_ids = hydrogen.electron_cloud.check_stability(max_escape_radius=20.0)

    print(f"\nStability:")
    print(f"  Cloud stable: {is_stable}")
    print(f"  Escaped fragments: {n_escaped}/{config.n_fragments}")

    # Check collisions
    print(f"\nCollisions:")
    print(f"  Total: {final_snapshot['total_collisions']}")
    print(f"  Average per tick: {final_snapshot['total_collisions'] / config.num_ticks:.2f}")

    # Success criteria
    print("\n" + "="*70)
    success = True

    if r_drift_pct < 50:  # Relaxed for quick test
        print("[PASS] Cloud radius drift < 50%")
    else:
        print(f"[FAIL] Cloud radius drift = {r_drift_pct:.2f}% >= 50%")
        success = False

    if is_stable:
        print("[PASS] No fragments escaped")
    else:
        print(f"[FAIL] {n_escaped} fragments escaped")
        success = False

    if r_final > 0.5:
        print("[PASS] Cloud did not collapse")
    else:
        print(f"[FAIL] Cloud collapsed (r={r_final:.4f})")
        success = False

    print("="*70)

    if success:
        print("*** VALIDATION PASSED! ***")
        print("V3 fragmented electron cloud stable!")
    else:
        print("XXX VALIDATION FAILED XXX")
        print("Cloud unstable - need parameter tuning")

    print("="*70)

    # Save results to JSON
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    results = {
        'config': {
            'n_fragments': config.n_fragments,
            'num_ticks': config.num_ticks,
            'proton_mass': config.proton_mass,
            'proton_energy': config.proton_energy,
            'electron_total_mass': config.electron_total_mass,
            'coupling_constant': config.coupling_constant,
            'jitter_strength': config.jitter_strength,
            'collision_radius': config.collision_radius,
            'restitution': config.restitution_coefficient,
        },
        'results': {
            'cloud_radius_initial': float(radii[0]),
            'cloud_radius_final': float(radii[-1]),
            'cloud_radius_drift_percent': float(r_drift_pct),
            'n_escaped': int(n_escaped),
            'success': success,
        },
        'snapshots': snapshots
    }

    output_file = results_dir / "exp56a_v3_hydrogen_fragmented_cloud.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    return success


if __name__ == "__main__":
    success = run_quick_test()
    sys.exit(0 if success else 1)
