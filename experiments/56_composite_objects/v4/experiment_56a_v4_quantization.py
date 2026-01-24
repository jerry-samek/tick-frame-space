#!/usr/bin/env python3
"""
Experiment 56 Phase 4 V4: Quantization Study

Extended 100k tick simulation with enhanced tracking to test quantization hypothesis
from Doc 070_01 §4: "This process naturally drives the system toward stable orbital
levels, quantized energy states, and robust equilibrium distributions."

Based on successful V3 baseline with added energy conservation tracking.
"""

import numpy as np
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, '.')

from config_v4 import ConfigV4
from fragmented_cloud import FragmentedElectronCloud, Pattern
from collision_dynamics import apply_all_collisions
from zero_point_jitter import apply_zero_point_energy
from binding_detection_v2 import GammaWellDetector


class HydrogenAtomV4:
    """Hydrogen atom with fragmented electron cloud - extended quantization study."""

    def __init__(self, config: ConfigV4):
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
        Update gamma-field from proton only.

        Static gamma-well from proton that fragments respond to but don't modify.
        """
        patterns = []

        # Add proton ONLY (create static gamma-well)
        patterns.append((self.proton_pattern, self.proton_position, np.array([0.0, 0.0])))

        # Update fields (100 relaxation steps to reach steady state)
        self.detector.update_fields(patterns, dt=1.0, num_steps=100)

    def compute_potential_energy(self):
        """
        Compute total potential energy from gamma-well.

        PE = Σ_i m_i × γ(r_i) × coupling_constant

        (Simple approximation - actual potential depends on field structure)
        """
        total_pe = 0.0
        for frag in self.electron_cloud.fragments:
            abs_position = self.proton_position + frag.position
            gamma_value = self.detector.get_gamma_at_position(abs_position)

            # Potential energy: higher gamma = deeper well = more negative PE
            # PE ∝ -γ (attractive potential)
            pe = -frag.mass * gamma_value * self.config.coupling_constant
            total_pe += pe

        return total_pe

    def update(self, dt=1.0):
        """Update atom for one tick."""
        self.tick += 1

        # 1. Update gamma-field periodically
        if self.tick % self.config.field_update_interval == 0:
            self._update_gamma_field()

        # 2. Apply gradient force to each fragment (radial only)
        if self.config.apply_gradient_force:
            for frag in self.electron_cloud.fragments:
                abs_position = self.proton_position + frag.position
                gamma_gradient = self.detector.compute_gradient_at_position(abs_position)

                if self.config.radial_force_only:
                    # Apply only radial component
                    r_mag = np.linalg.norm(frag.position)
                    if r_mag > 0.01:
                        r_hat = frag.position / r_mag
                        grad_radial = np.dot(gamma_gradient, r_hat)
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

    def get_snapshot(self, detailed=False):
        """
        Get current state snapshot.

        Args:
            detailed: If True, include full fragment data and distributions
        """
        snapshot = {
            'tick': self.tick,
            'cloud_radius_mean': self.electron_cloud.cloud_radius_mean,
            'cloud_radius_rms': self.electron_cloud.cloud_radius_rms,
            'cloud_radius_std': self.electron_cloud.cloud_radius_std,
            'total_kinetic_energy': self.electron_cloud.total_kinetic_energy,
            'angular_momentum': self.electron_cloud.angular_momentum,
            'total_collisions': self.electron_cloud.total_collisions,
        }

        # Add potential energy if tracking enabled
        if self.config.compute_potential_energy:
            snapshot['total_potential_energy'] = self.compute_potential_energy()
            snapshot['total_energy'] = snapshot['total_kinetic_energy'] + snapshot['total_potential_energy']

        # Add fragment energies if tracking enabled
        if self.config.track_fragment_energies:
            fragment_kinetic_energies = [f.kinetic_energy for f in self.electron_cloud.fragments]
            snapshot['fragment_ke_mean'] = float(np.mean(fragment_kinetic_energies))
            snapshot['fragment_ke_std'] = float(np.std(fragment_kinetic_energies))

        # Add detailed data (full distributions) for analysis
        if detailed:
            # Velocity distribution
            if self.config.track_velocity_distribution:
                speeds = [f.speed for f in self.electron_cloud.fragments]
                snapshot['velocity_speeds'] = [float(v) for v in speeds]
                snapshot['velocity_mean'] = float(np.mean(speeds))
                snapshot['velocity_std'] = float(np.std(speeds))

            # Radial density profile
            if self.config.track_radial_density_profile:
                radii, densities = self.electron_cloud.compute_radial_density_profile(
                    n_bins=self.config.radial_bins,
                    max_radius=self.config.max_analysis_radius
                )
                snapshot['radial_profile_bins'] = radii.tolist()
                snapshot['radial_profile_densities'] = densities.tolist()

            # Individual fragment data (for correlation analysis)
            snapshot['fragment_data'] = [
                {
                    'id': f.fragment_id,
                    'position': f.position.tolist(),
                    'velocity': f.velocity.tolist(),
                    'speed': float(f.speed),
                    'radius': float(f.distance_from_origin),
                    'kinetic_energy': float(f.kinetic_energy),
                }
                for f in self.electron_cloud.fragments
            ]

        return snapshot


def run_quantization_study(config_type="ultra_long"):
    """
    Run extended quantization study.

    Args:
        config_type: Configuration to use:
            - "quantization": 50 fragments, 100k ticks (original V4)
            - "high_resolution": 100 fragments, 100k ticks
            - "ultra_long": 50 fragments, 200k ticks (FAILED in 2D - runaway at 51k)
            - "high_res_ultra_long": 100 fragments, 200k ticks (FAILED - runaway at ~70k ticks)
            - "energy_diagnostic": 50 fragments, 100k ticks, jitter=0.0005 (half strength)
            - "energy_diag_weak": 50 fragments, 100k ticks, jitter=0.0002 (20% strength)
            - "energy_diag_minimal": 50 fragments, 100k ticks, jitter=0.0001 (10% strength)
    """
    print("="*70)
    print("Experiment 56 V4: Quantization Study")
    print("="*70)
    print("\nTesting Doc 070_01 §4 hypothesis:")
    print("  'Collision dynamics drive system toward stable orbital levels,")
    print("   quantized energy states, and robust equilibrium distributions.'")
    print("\nAdditional hypothesis: Collisions naturally eject excess fragments,")
    print("  creating self-regulating fragment count.")
    print("="*70)

    # Select configuration
    from config_v4 import (get_quantization_config, get_high_resolution_config,
                           get_ultra_long_config, get_high_res_ultra_long_config,
                           get_energy_diagnostic_config, get_quantization_200k_config)

    config_map = {
        "quantization": get_quantization_config,
        "high_resolution": get_high_resolution_config,
        "ultra_long": get_ultra_long_config,
        "high_res_ultra_long": get_high_res_ultra_long_config,
        "energy_diagnostic": get_energy_diagnostic_config,
        "energy_diag_weak": lambda: get_energy_diagnostic_config(jitter_scale=0.2),
        "energy_diag_minimal": lambda: get_energy_diagnostic_config(jitter_scale=0.1),
        "quantization_200k": get_quantization_200k_config,
    }

    if config_type not in config_map:
        print(f"ERROR: Unknown config type '{config_type}'")
        print(f"Available: {list(config_map.keys())}")
        sys.exit(1)

    config = config_map[config_type]()
    print(f"\nUsing configuration: {config_type}")

    print(f"\nConfiguration:")
    print(f"  Fragments: {config.n_fragments}")
    print(f"  Total ticks: {config.num_ticks:,}")
    print(f"  Expected runtime: ~{config.num_ticks // 10000 * 45:.0f} seconds ({config.num_ticks // 10000 * 45 // 60:.0f} minutes)")
    print(f"  Snapshots: {config.num_ticks // config.snapshot_interval}")
    print(f"  Detailed snapshots: {config.num_ticks // config.detailed_snapshot_interval}")

    print(f"\nPhysics (V3 scaled baseline):")
    print(f"  Proton mass: {config.proton_mass}")
    print(f"  Electron mass: {config.electron_total_mass}")
    print(f"  Coupling constant: {config.coupling_constant}")
    print(f"  Jitter strength: {config.jitter_strength}")
    print(f"  Collision radius: {config.collision_radius}")
    print(f"  Restitution: {config.restitution_coefficient}")

    # Create hydrogen atom
    hydrogen = HydrogenAtomV4(config)

    print(f"\nInitial state:")
    snapshot = hydrogen.get_snapshot()
    for key, val in snapshot.items():
        if isinstance(val, float):
            print(f"  {key}: {val:.6f}")
        else:
            print(f"  {key}: {val}")

    # Run simulation
    print(f"\nRunning {config.num_ticks:,} ticks...")
    print(f"Progress reports every {config.progress_report_interval:,} ticks...")
    print(f"Detailed snapshots every {config.detailed_snapshot_interval:,} ticks...")
    print()

    snapshots = []
    detailed_snapshots = []

    import time
    start_time = time.time()

    for tick in range(1, config.num_ticks + 1):
        hydrogen.update(dt=1.0)

        # Regular snapshots
        if tick % config.snapshot_interval == 0:
            snapshot = hydrogen.get_snapshot(detailed=False)
            snapshots.append(snapshot)

        # Detailed snapshots (with full distributions)
        if tick % config.detailed_snapshot_interval == 0:
            detailed_snapshot = hydrogen.get_snapshot(detailed=True)
            detailed_snapshots.append(detailed_snapshot)

        # Progress report (detailed stats)
        if tick % config.progress_report_interval == 0:
            elapsed = time.time() - start_time
            ticks_per_sec = tick / elapsed if elapsed > 0 else 0
            eta_sec = (config.num_ticks - tick) / ticks_per_sec if ticks_per_sec > 0 else 0

            s = hydrogen.get_snapshot()
            print(f"[{tick:7d}/{config.num_ticks:7d}] ({100*tick/config.num_ticks:5.1f}%) "
                  f"{elapsed:.1f}s elapsed, ETA: {eta_sec:.1f}s")
            print(f"  r_rms={s['cloud_radius_rms']:.4f}, "
                  f"KE={s['total_kinetic_energy']:.6f}, "
                  f"L_z={s['angular_momentum']:.6f}")
            print(f"  collisions={s['total_collisions']} total "
                  f"({s['total_collisions']/tick:.2f}/tick)")
            if config.compute_potential_energy:
                print(f"  PE={s.get('total_potential_energy', 0):.6f}, "
                      f"E_total={s.get('total_energy', 0):.6f}")

            # Check for fragment escapes in real-time
            is_stable, n_escaped, _ = hydrogen.electron_cloud.check_stability(
                max_escape_radius=config.max_fragment_escape_radius
            )
            if not is_stable:
                print(f"  WARNING: {n_escaped} fragments have escaped!")
            print()

    # Final state
    final_snapshot = hydrogen.get_snapshot(detailed=True)
    snapshots.append(final_snapshot)
    detailed_snapshots.append(final_snapshot)

    print(f"\nFinal state:")
    for key, val in final_snapshot.items():
        if isinstance(val, float):
            print(f"  {key}: {val:.6f}")
        elif isinstance(val, int):
            print(f"  {key}: {val}")

    # Analysis
    print("\n" + "="*70)
    print("QUANTIZATION STUDY RESULTS")
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
    print(f"  Mean: {np.mean(radii):.4f}")
    print(f"  Std: {np.std(radii):.4f}")

    # Check for escapes
    is_stable, n_escaped, escaped_ids = hydrogen.electron_cloud.check_stability(
        max_escape_radius=config.max_fragment_escape_radius
    )

    print(f"\nStability:")
    print(f"  Cloud stable: {is_stable}")
    print(f"  Escaped fragments: {n_escaped}/{config.n_fragments}")

    # Check collisions
    print(f"\nCollisions:")
    print(f"  Total: {final_snapshot['total_collisions']}")
    print(f"  Average per tick: {final_snapshot['total_collisions'] / config.num_ticks:.2f}")

    # Energy conservation
    if config.compute_potential_energy:
        energies_total = [s.get('total_energy', 0) for s in snapshots]
        e_initial = energies_total[0]
        e_final = energies_total[-1]
        e_drift = abs(e_final - e_initial) / abs(e_initial) * 100

        print(f"\nEnergy conservation:")
        print(f"  Initial total energy: {e_initial:.6f}")
        print(f"  Final total energy: {e_final:.6f}")
        print(f"  Drift: {e_drift:.2f}%")

    # Success criteria
    print("\n" + "="*70)
    success = True

    if r_drift_pct < config.max_cloud_drift_percent:
        print(f"[PASS] Cloud radius drift {r_drift_pct:.2f}% < {config.max_cloud_drift_percent}%")
    else:
        print(f"[FAIL] Cloud radius drift = {r_drift_pct:.2f}% >= {config.max_cloud_drift_percent}%")
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
        print("V4 quantization study completed successfully!")
        print("Proceed to analyze_quantization.py for quantization analysis...")
    else:
        print("XXX VALIDATION FAILED XXX")
        print("Cloud unstable - check parameters")

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
            'electron_total_energy': config.electron_total_energy,
            'coupling_constant': config.coupling_constant,
            'jitter_strength': config.jitter_strength,
            'collision_radius': config.collision_radius,
            'restitution': config.restitution_coefficient,
            'radial_bins': config.radial_bins,
            'energy_histogram_bins': config.energy_histogram_bins,
        },
        'results': {
            'cloud_radius_initial': float(radii[0]),
            'cloud_radius_final': float(radii[-1]),
            'cloud_radius_mean': float(np.mean(radii)),
            'cloud_radius_std': float(np.std(radii)),
            'cloud_radius_drift_percent': float(r_drift_pct),
            'n_escaped': int(n_escaped),
            'success': success,
        },
        'snapshots': snapshots,
        'detailed_snapshots': detailed_snapshots
    }

    # Save main results
    output_filename = f"exp56a_v4_{config.n_fragments}frags_{config.num_ticks//1000}k.json"
    output_file = results_dir / output_filename
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")

    return success


if __name__ == "__main__":
    import sys

    # Allow config selection via command line
    # Default changed to ultra_long after high_res_ultra_long runaway
    config_type = sys.argv[1] if len(sys.argv) > 1 else "ultra_long"

    print(f"Configuration selected: {config_type}")
    print(f"(Use: python {sys.argv[0]} [quantization|high_resolution|ultra_long|high_res_ultra_long])")
    print()

    success = run_quantization_study(config_type=config_type)
    sys.exit(0 if success else 1)
