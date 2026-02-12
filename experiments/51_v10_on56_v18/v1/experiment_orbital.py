"""
Main experiment runner for V18 orbital dynamics test.

Tests whether stable orbits emerge from the V18 canvas substrate using only
gradient-following and skip-based time dilation, without reaction-diffusion PDE.

Two approaches:
  A) OrbitalTestProcess with integer velocity and gradient acceleration
  B) Pure V18 SimpleDegenerateProcess (gradient-following only, no velocity)

FORBIDDEN: No scipy, no Lorentz factor, no continuous positions,
no analytical gravitational profiles.

Usage:
    python experiment_orbital.py --planet-count 100 --speed-limit 1
    python experiment_orbital.py --planet-count 500 --speed-limit 5 --smoothed-gradient

Date: February 2026
"""

import sys
import json
import math
import time
import argparse
import numpy as np
from pathlib import Path
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "56_composite_objects"))
from v18 import Canvas3D_V18, SimpleDegenerateProcess

from orbital_process import (
    OrbitalTestProcess,
    get_smoothed_gradient,
    create_planet_processes,
    create_ring_processes,
)


@dataclass
class ExperimentConfig:
    planet_count: int = 500
    planet_spread_radius: int = 3
    planet_formation_ticks: int = 500
    orbital_test_ticks: int = 4500
    speed_limit: int = 1
    use_smoothed_gradient: bool = False
    gradient_sample_radius: int = 5
    approach: str = "both"  # "A", "B", or "both"
    approach_b_radii: list = None
    approach_b_per_ring: int = 10
    wake_decay_rate: float = 0.05
    random_seed: int = 42
    snapshot_interval: int = 100

    def __post_init__(self):
        if self.approach_b_radii is None:
            self.approach_b_radii = [20, 30, 50]


class OrbitalExperiment:
    """Main experiment orchestrator.

    Phase 0: Planet formation - create gamma mass at origin
    Phase 1: Orbital tests - inject test processes and observe dynamics
    """

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.canvas = Canvas3D_V18()
        self.planet_processes = []
        self.orbital_processes = []
        self.pure_v18_processes = []
        self.approach_b_trajectories = {}  # pid -> List[Pos3D]
        self.tick_count = 0
        self.gamma_profile = {}
        self.gradient_analysis = []

        # Seed numpy global RNG for reproducibility
        # (CompositeProcess.step() uses np.random.random() internally)
        np.random.seed(config.random_seed)

    def run(self):
        """Run the full experiment."""
        print("=" * 60)
        print("V18 Orbital Dynamics Experiment")
        print("=" * 60)
        print(f"  planet_count     = {self.config.planet_count}")
        print(f"  speed_limit      = {self.config.speed_limit}")
        print(f"  smoothed_gradient= {self.config.use_smoothed_gradient}")
        print(f"  approach         = {self.config.approach}")
        print(f"  formation_ticks  = {self.config.planet_formation_ticks}")
        print(f"  orbital_ticks    = {self.config.orbital_test_ticks}")
        print(f"  seed             = {self.config.random_seed}")
        print()

        self._phase0_planet_formation()
        self._phase1_orbital_tests()
        self._save_results()

    def _phase0_planet_formation(self):
        """Phase 0: Create gamma mass at origin by evolving planet processes."""
        ticks = self.config.planet_formation_ticks
        print(f"--- Phase 0: Planet Formation ({ticks} ticks) ---")

        self.planet_processes = create_planet_processes(
            self.config.planet_count,
            self.config.planet_spread_radius,
            self.config.random_seed,
        )
        print(f"  Created {len(self.planet_processes)} planet processes "
              f"within radius {self.config.planet_spread_radius}")

        t0 = time.time()
        for tick in range(ticks):
            for p in self.planet_processes:
                p.step(self.canvas)

            self.canvas.decay_wake(self.config.wake_decay_rate)
            self.tick_count += 1

            if (tick + 1) % self.config.snapshot_interval == 0:
                elapsed = time.time() - t0
                stats = self.canvas.get_statistics()
                rate = (tick + 1) / elapsed if elapsed > 0 else 0
                print(f"  Tick {tick + 1:5d}/{ticks} "
                      f"({elapsed:6.1f}s, {rate:.0f} t/s) | "
                      f"cells={stats['painted_cells']:6d}, "
                      f"gamma={stats['total_gamma']:8.0f}, "
                      f"r_max={stats['r_max']:5.1f}")

        # Record gamma radial profile
        self.gamma_profile = self.canvas.get_radial_distribution()

        # Print gamma profile
        print(f"\n  Gamma radial profile (after {ticks} ticks of formation):")
        sorted_radii = sorted(self.gamma_profile.keys())
        for r in sorted_radii[:25]:
            bar = "#" * min(60, int(self.gamma_profile[r] / max(self.gamma_profile.values()) * 60))
            print(f"    r={r:3d}: {self.gamma_profile[r]:8.1f}  {bar}")
        if len(sorted_radii) > 25:
            print(f"    ... ({len(sorted_radii) - 25} more shells)")

        # Gradient analysis at test distances
        print(f"\n  Gradient analysis at test distances:")
        print(f"    {'r':>4s} | {'std_grad':>10s} | {'smooth_grad':>12s} | {'local_gamma':>12s}")
        print(f"    {'':->4s}-+-{'':->10s}-+-{'':->12s}-+-{'':->12s}")

        test_distances = [5, 10, 15, 20, 25, 30, 40, 50]
        for r in test_distances:
            pos = (r, 0, 0)
            grad = self.canvas.get_gradient(pos)
            grad_mag = math.sqrt(sum(g * g for g in grad))
            smooth_grad = get_smoothed_gradient(
                self.canvas, pos, self.config.gradient_sample_radius
            )
            smooth_mag = math.sqrt(sum(g * g for g in smooth_grad))
            local_gamma = self.canvas.get_local_gamma_sum(pos, 3)

            self.gradient_analysis.append({
                "distance": r,
                "standard_gradient_mag": grad_mag,
                "smoothed_gradient_mag": smooth_mag,
                "local_gamma": local_gamma,
            })
            print(f"    {r:4d} | {grad_mag:10.4f} | {smooth_mag:12.4f} | {local_gamma:12.1f}")

        print()

    def _phase1_orbital_tests(self):
        """Phase 1: Inject test processes and run orbital dynamics."""
        total_ticks = self.config.orbital_test_ticks
        print(f"--- Phase 1: Orbital Tests ({total_ticks} ticks) ---")

        # Create Approach A processes
        if self.config.approach in ("A", "both"):
            self._create_approach_a_processes()

        # Create Approach B processes
        if self.config.approach in ("B", "both"):
            self._create_approach_b_processes()

        print()
        t0 = time.time()
        for tick in range(total_ticks):
            current_tick = self.config.planet_formation_ticks + tick

            # Step planet processes (keep painting to maintain field)
            for p in self.planet_processes:
                p.step(self.canvas)

            # Step Approach A orbital processes
            for op in self.orbital_processes:
                op.step(self.canvas, current_tick)

            # Step Approach B pure V18 processes and record positions
            for bp in self.pure_v18_processes:
                bp.step(self.canvas)
                pid = bp.process_id
                if pid not in self.approach_b_trajectories:
                    self.approach_b_trajectories[pid] = []
                self.approach_b_trajectories[pid].append(bp.center)

            self.canvas.decay_wake(self.config.wake_decay_rate)
            self.tick_count += 1

            if (tick + 1) % self.config.snapshot_interval == 0:
                elapsed = time.time() - t0
                rate = (tick + 1) / elapsed if elapsed > 0 else 0

                # Show orbital process distances
                orbit_info = []
                for op in self.orbital_processes:
                    if op.trajectory:
                        r = op.trajectory[-1].distance_from_origin
                        orbit_info.append(f"{op.label}:r={r:.1f}")

                orbit_str = ", ".join(orbit_info) if orbit_info else ""
                stats = self.canvas.get_statistics()

                print(f"  Tick {tick + 1:5d}/{total_ticks} "
                      f"({elapsed:6.1f}s, {rate:.0f} t/s) | "
                      f"cells={stats['painted_cells']:6d} | "
                      f"{orbit_str}")

        # Final status
        print(f"\n  Final orbital process status:")
        for op in self.orbital_processes:
            if op.trajectory:
                last = op.trajectory[-1]
                print(f"    {op.label}: r={last.distance_from_origin:.1f}, "
                      f"v={op.velocity}, "
                      f"acts={op.acts_count}, skips={op.skips_count}")

        if self.pure_v18_processes:
            print(f"\n  Approach B final distances:")
            for bp in self.pure_v18_processes:
                r = math.sqrt(sum(c * c for c in bp.center))
                print(f"    pid={bp.process_id}: r={r:.1f}, center={bp.center}")

        print()

    def _create_approach_a_processes(self):
        """Create Approach A orbital test processes with velocity."""
        base_id = self.config.planet_count + 1000
        sl = self.config.speed_limit

        # Scale initial tangential velocity for higher speed limits
        # At max_speed=1: v_tang=1 (=c, minimum nonzero)
        # At max_speed=5: v_tang=3 (~0.6c effective)
        v_tang = max(1, sl * 3 // 5) if sl > 1 else 1

        configs = [
            ("T1", (30, 0, 0), (0, v_tang, 0), "Circular attempt r=30"),
            ("T2", (30, 0, 0), (0, 0, 0),      "Radial infall control"),
            ("T3", (20, 0, 0), (0, v_tang, 0), "Closer orbit r=20"),
            ("T4", (50, 0, 0), (0, v_tang, 0), "Farther orbit r=50"),
            ("T6", (40, 0, 0), (0, v_tang, 0), "Medium distance r=40"),
        ]

        print(f"  Approach A: {len(configs)} orbital test processes "
              f"(max_speed={sl}, v_tang={v_tang})")
        for i, (label, pos, vel, desc) in enumerate(configs):
            op = OrbitalTestProcess(
                process_id=base_id + i,
                center=pos,
                velocity=vel,
                label=label,
                max_speed=sl,
                skip_sensitivity=0.1,
                use_smoothed_gradient=self.config.use_smoothed_gradient,
                gradient_sample_radius=self.config.gradient_sample_radius,
            )
            self.orbital_processes.append(op)
            print(f"    {label}: pos={pos}, vel={vel} - {desc}")

    def _create_approach_b_processes(self):
        """Create Approach B pure V18 ring processes."""
        base_id = self.config.planet_count + 2000
        total = 0
        for radius in self.config.approach_b_radii:
            ring = create_ring_processes(
                base_id + total,
                radius,
                self.config.approach_b_per_ring,
            )
            self.pure_v18_processes.extend(ring)
            total += len(ring)
            print(f"  Approach B: {len(ring)} processes on ring r={radius}")

    def _save_results(self):
        """Save experiment results to JSON."""
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        results = {
            "config": {
                "planet_count": self.config.planet_count,
                "planet_spread_radius": self.config.planet_spread_radius,
                "planet_formation_ticks": self.config.planet_formation_ticks,
                "orbital_test_ticks": self.config.orbital_test_ticks,
                "speed_limit": self.config.speed_limit,
                "use_smoothed_gradient": self.config.use_smoothed_gradient,
                "gradient_sample_radius": self.config.gradient_sample_radius,
                "approach": self.config.approach,
                "approach_b_radii": self.config.approach_b_radii,
                "approach_b_per_ring": self.config.approach_b_per_ring,
                "wake_decay_rate": self.config.wake_decay_rate,
                "random_seed": self.config.random_seed,
                "total_ticks": self.tick_count,
            },
            "gamma_profile": {
                str(k): v for k, v in sorted(self.gamma_profile.items())
            },
            "gradient_analysis": self.gradient_analysis,
            "approach_a": {},
            "approach_b": {},
            "canvas_stats": self.canvas.get_statistics(),
        }

        # Approach A trajectories
        for op in self.orbital_processes:
            results["approach_a"][op.label] = {
                "config": {
                    "start_position": list(op.initial_position),
                    "initial_velocity": list(op.initial_velocity),
                    "max_speed": op.max_speed,
                    "use_smoothed_gradient": op.use_smoothed_gradient,
                },
                "acts": op.acts_count,
                "skips": op.skips_count,
                "trajectory": [
                    {
                        "tick": tp.tick,
                        "position": list(tp.position),
                        "velocity": list(tp.velocity),
                        "r": tp.distance_from_origin,
                        "local_gamma": tp.local_gamma,
                        "gradient_mag": tp.gradient_mag,
                        "skipped": tp.skipped,
                    }
                    for tp in op.trajectory
                ],
            }

        # Approach B trajectories
        for pid, positions in self.approach_b_trajectories.items():
            initial_r = math.sqrt(sum(c * c for c in positions[0])) if positions else 0
            final_r = math.sqrt(sum(c * c for c in positions[-1])) if positions else 0
            results["approach_b"][str(pid)] = {
                "initial_distance": initial_r,
                "final_distance": final_r,
                "trajectory": [list(p) for p in positions],
            }

        # Build filename from config
        sl = self.config.speed_limit
        sg = "smoothed" if self.config.use_smoothed_gradient else "standard"
        filename = f"orbital_sl{sl}_{sg}_p{self.config.planet_count}.json"
        filepath = results_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)

        stats = results["canvas_stats"]
        print(f"Results saved to {filepath}")
        print(f"  Canvas: {stats['painted_cells']} cells, "
              f"{stats['total_gamma']:.0f} total gamma, "
              f"r_max={stats['r_max']:.1f}")
        print(f"  Approach A: {len(self.orbital_processes)} processes")
        print(f"  Approach B: {len(self.pure_v18_processes)} processes")


def main():
    parser = argparse.ArgumentParser(
        description="V18 Orbital Dynamics Experiment - "
                    "Tests orbital mechanics on pure gamma accumulation substrate"
    )
    parser.add_argument(
        "--planet-count", type=int, default=500,
        help="Number of planet processes (default: 500)",
    )
    parser.add_argument(
        "--speed-limit", type=int, default=1,
        help="Max velocity per component in cells/tick (default: 1 = c)",
    )
    parser.add_argument(
        "--formation-ticks", type=int, default=500,
        help="Ticks for planet formation phase (default: 500)",
    )
    parser.add_argument(
        "--orbital-ticks", type=int, default=4500,
        help="Ticks for orbital test phase (default: 4500)",
    )
    parser.add_argument(
        "--approach", choices=["A", "B", "both"], default="both",
        help="Which approach to run (default: both)",
    )
    parser.add_argument(
        "--smoothed-gradient", action="store_true",
        help="Use smoothed long-range gradient instead of standard pos+-1",
    )
    parser.add_argument(
        "--gradient-radius", type=int, default=5,
        help="Sample radius for smoothed gradient (default: 5)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--snapshot-interval", type=int, default=100,
        help="Progress logging interval in ticks (default: 100)",
    )

    args = parser.parse_args()

    config = ExperimentConfig(
        planet_count=args.planet_count,
        speed_limit=args.speed_limit,
        planet_formation_ticks=args.formation_ticks,
        orbital_test_ticks=args.orbital_ticks,
        approach=args.approach,
        use_smoothed_gradient=args.smoothed_gradient,
        gradient_sample_radius=args.gradient_radius,
        random_seed=args.seed,
        snapshot_interval=args.snapshot_interval,
    )

    experiment = OrbitalExperiment(config)
    experiment.run()


if __name__ == "__main__":
    main()
