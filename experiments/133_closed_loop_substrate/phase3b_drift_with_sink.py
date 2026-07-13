#!/usr/bin/env python3
"""Phase 3b: Test pattern drift in source+sink field.

Phase 2d showed source+sink produces a clean radial density gradient:
  ρ ∝ r^(-1) at α=0 → |∇ρ| ∝ r^(-2) → Newton's 1/r² force on test patterns
  ρ ∝ r^(-0.83) at α=1 → soft Newton

This script tests whether a real test pattern (planet) actually drifts
toward the star under that gradient. If yes, we have substrate gravity
(via source+sink, not pure conservation).

Setup:
  - star: 50 cells at center, replenished to fixed E each tick (source)
  - planet: 5 cells at hop ~30 from star, NOT replenished (so we see drift)
  - sink: cells beyond r > 0.45 from star zeroed each tick

Tracks planet centroid every 25 ticks. Runs short enough that the planet
survives long enough to be observed (under wake bias + integer quantization,
unprotected planets dissipate within a few hundred ticks).
"""

import argparse
import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from metrics import cluster_high_energy
from visualization import plot_trajectory


N_NODES = 100_000
RADIUS = 0.025
N_TICKS = 1_500
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
PLANET_CENTER = np.array([0.7, 0.5, 0.5])  # offset radially from star
STAR_MASS = 1000
STAR_CELLS = 50
PLANET_MASS = 300  # larger than original 30 so it persists longer
PLANET_CELLS = 10
BACKGROUND_PER_CELL = 20
SINK_RADIUS = 0.45

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def main(alpha: float):
    print(f"Phase 3b: drift test in source+sink field, alpha={alpha}")
    print(f"Building RGG: N={N_NODES}, radius={RADIUS}")
    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)
    print(f"  directed edges: {n_directed:,}, mean degree: {n_directed/N_NODES:.1f}")

    d_star = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(d_star)[:STAR_CELLS]
    star_cell_E = STAR_MASS // STAR_CELLS

    d_planet_from_planet_center = np.linalg.norm(coords - PLANET_CENTER[None, :], axis=1)
    planet_idx = np.argsort(d_planet_from_planet_center)[:PLANET_CELLS]
    initial_planet_dist = float(np.linalg.norm(PLANET_CENTER - STAR_CENTER))
    print(f"  initial planet distance from star: {initial_planet_dist:.4f}")

    sink_mask = d_star > SINK_RADIUS
    print(f"  sink cells: {int(sink_mask.sum())}")

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] = star_cell_E + BACKGROUND_PER_CELL
    energy_init[planet_idx] += PLANET_MASS // PLANET_CELLS  # planet is heavier than background
    energy_init[sink_mask] = 0

    E, received = init_state(N_NODES, n_directed, energy_init)

    planet_positions = []  # (tick, centroid)
    star_only_mass_history = []
    t0 = time.time()

    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=alpha)

        # Source: replenish star
        E[star_idx] = star_cell_E + BACKGROUND_PER_CELL
        # Sink: zero outer shell
        E[sink_mask] = 0

        if t % 25 == 0 or t == 1:
            # Identify clusters; star is biggest, planet should be second
            clusters = cluster_high_energy(E, coords, threshold_quantile=0.99)

            # Match planet by proximity to last known planet position (or initial seed for first detection)
            ref_pos = planet_positions[-1][1] if planet_positions else PLANET_CENTER
            best = None
            best_dist = float('inf')
            for c in clusters:
                # Skip the star cluster (closest to STAR_CENTER)
                star_dist = np.linalg.norm(np.array(c['centroid']) - STAR_CENTER)
                if star_dist < 0.1:
                    continue
                d = np.linalg.norm(np.array(c['centroid']) - np.array(ref_pos))
                if d < best_dist:
                    best_dist = d
                    best = c

            if best is not None and best_dist < 0.15:
                planet_positions.append((t, best['centroid']))

            if t % 100 == 0 or t == 1:
                rate = t / (time.time() - t0)
                if planet_positions:
                    last = np.array(planet_positions[-1][1])
                    pd = float(np.linalg.norm(last - STAR_CENTER))
                    pmass = best['mass'] if best is not None else 0
                else:
                    pd = float('nan')
                    pmass = 0
                print(f"  tick {t:>5d}  planet_dist={pd:.4f}  planet_mass={pmass:>5d}  "
                      f"({rate:.0f} t/s)")

    # Save trajectory and analyze drift
    if len(planet_positions) >= 2:
        ticks_arr = np.array([p[0] for p in planet_positions])
        traj = np.array([p[1] for p in planet_positions])
        distances = np.linalg.norm(traj - STAR_CENTER, axis=1)

        with open(os.path.join(OUT_DIR, f'phase3b_alpha{alpha}.json'), 'w') as f:
            json.dump({
                'ticks': ticks_arr.tolist(),
                'positions': traj.tolist(),
                'distances_from_star': distances.tolist(),
            }, f, indent=2)

        plot_trajectory(traj, star_pos=STAR_CENTER,
                        out_path=os.path.join(OUT_DIR, f'phase3b_alpha{alpha}_traj.png'),
                        title=f'Phase 3b drift (alpha={alpha})')

        # Compute drift velocity over first 500 ticks (before planet dissipates much)
        early = ticks_arr <= 500
        if early.sum() >= 3:
            r_early = distances[early]
            t_early = ticks_arr[early]
            # Linear fit r(t) = r0 + v*t
            v_early, r0 = np.polyfit(t_early, r_early, 1)
            print(f"\nEarly drift (first 500 ticks): r(t) = {r0:.4f} + {v_early:.6f}*t")
            print(f"  velocity inward: {-v_early*1000:.4f} units / 1000 ticks")

        # Fit acceleration: r(t) ~ r0 + v0*t + 0.5*a*t^2
        if len(ticks_arr) >= 5:
            quad_fit = np.polyfit(ticks_arr, distances, 2)
            print(f"  quadratic fit: a/2={quad_fit[0]:+.2e}, v0={quad_fit[1]:+.4e}, r0={quad_fit[2]:.4f}")
            if quad_fit[0] < 0:
                print(f"  INWARD ACCELERATION DETECTED: planet is being attracted toward star.")
            else:
                print(f"  No inward acceleration -- planet drift is at most linear or outward.")

        initial_dist = distances[0]
        final_dist = distances[-1]
        drift = initial_dist - final_dist
        print(f"\nInitial planet distance: {initial_dist:.4f}")
        print(f"Final planet distance:   {final_dist:.4f}")
        print(f"Net drift (positive = inward): {drift:+.4f}")

        if drift > 0.01:
            print("\nPhase 3b PASS: planet drifted toward star by measurable amount.")
        elif drift > 0:
            print("\nPhase 3b WEAK: small inward drift, gradient response detectable.")
        else:
            print("\nPhase 3b FAIL: planet did not drift toward star.")
    else:
        print(f"\nPhase 3b: only {len(planet_positions)} planet sightings -- planet may have "
              f"dissipated too quickly. Try larger PLANET_MASS or shorter run.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--alpha', type=float, default=0.0)
    args = parser.parse_args()
    main(args.alpha)
