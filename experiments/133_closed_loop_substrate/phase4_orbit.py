#!/usr/bin/env python3
"""Phase 4: Orbit -- the goal.

Per spec section 5 Phase 4:
  - Phase 3 setup
  - tangential bias seeded on planet (initial wake-bias state biased tangentially)
  - run for several orbital periods
  - measure: closed trajectory, T^2 prop a^3, coherence over many orbits

Success: stable Keplerian orbit within 5-10%. The weekend goal.
"""

import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from metrics import per_tick_summary, cluster_high_energy
from visualization import plot_trajectory


N_NODES = 100_000
RADIUS = 0.025
N_TICKS = 30_000
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
PLANET_CENTER = np.array([0.7, 0.5, 0.5])
STAR_MASS = 1000
PLANET_MASS = 30
STAR_CELLS = 50
PLANET_CELLS = 5
BACKGROUND_PER_CELL = 20
ALPHA = 1.0

# Tangential direction (perpendicular to star->planet vector, in xy plane)
TANGENT = np.array([0.0, 1.0, 0.0])
TANGENT_BIAS_QUANTA = 50  # quanta to seed in tangential direction per planet cell

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def seed_tangential_bias(received, planet_idx, src, dst, coords, tangent, mass_per_cell):
    """For each planet cell, seed non-zero `received` on the edge most aligned with `tangent`.

    This puts the wake-bias machinery in a state where the planet 'just received'
    energy from the trailing direction, so its first-tick outflow biases tangentially-forward.
    """
    for cell in planet_idx:
        # Find directed edges incoming to this cell
        in_edges = np.where(dst == cell)[0]
        if len(in_edges) == 0:
            continue

        # For each incoming edge, the source-to-cell vector
        sources = src[in_edges]
        directions = coords[cell] - coords[sources]
        norms = np.linalg.norm(directions, axis=1)
        norms = np.where(norms > 0, norms, 1)
        directions = directions / norms[:, None]

        # Pick the edge whose incoming direction best aligns with `tangent`.
        # (We want energy "to be coming from behind" relative to forward = tangent.)
        alignment = directions @ tangent
        best = int(np.argmax(alignment))
        received[in_edges[best]] += mass_per_cell


def main():
    rng = np.random.default_rng(SEED)
    print(f"Phase 4: orbit, alpha={ALPHA}, tangent_bias={TANGENT_BIAS_QUANTA}")

    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)

    d_star = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(d_star)[:STAR_CELLS]

    d_planet = np.linalg.norm(coords - PLANET_CENTER[None, :], axis=1)
    planet_idx = np.argsort(d_planet)[:PLANET_CELLS]

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] += STAR_MASS // STAR_CELLS
    energy_init[planet_idx] += PLANET_MASS // PLANET_CELLS

    total_initial = int(energy_init.sum())

    E, received = init_state(N_NODES, n_directed, energy_init)

    # Seed tangential bias by editing `received` directly
    seed_tangential_bias(received, planet_idx, src, dst, coords, TANGENT,
                         mass_per_cell=TANGENT_BIAS_QUANTA)
    # The bias adds to total energy via the wake mechanism, so update budget assertion baseline
    # -- actually no: `received` is wake-history, not actual energy. Energy balance unaffected.

    planet_positions = []
    t0 = time.time()
    log = []

    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=ALPHA)
        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(f"CONSERVATION at tick {t}")

        if t % 25 == 0:
            clusters = cluster_high_energy(E, coords, threshold_quantile=0.995)
            if len(clusters) >= 2:
                planet_centroid = clusters[1]['centroid']
                planet_positions.append((t, planet_centroid))

            if t % 500 == 0:
                rate = t / (time.time() - t0)
                if planet_positions:
                    last_pos = np.array(planet_positions[-1][1])
                    dist = float(np.linalg.norm(last_pos - STAR_CENTER))
                else:
                    dist = float('nan')
                print(f"  tick {t:>6d} planet_dist={dist:.4f} ({rate:.0f} t/s)")

    # Save trajectory
    if planet_positions:
        traj = np.array([p[1] for p in planet_positions])
        ticks_at = np.array([p[0] for p in planet_positions])

        # Detect orbit: does trajectory return near start?
        start_pos = traj[0]
        distances_from_start = np.linalg.norm(traj - start_pos, axis=1)
        # First tick where it returns within 0.05 of start (after at least 100 ticks of motion)
        returned = np.where((distances_from_start < 0.05) & (ticks_at > ticks_at[0] + 1000))[0]
        period_ticks = ticks_at[returned[0]] if len(returned) > 0 else None

        plot_trajectory(traj, star_pos=STAR_CENTER,
                        out_path=os.path.join(OUT_DIR, 'phase4_orbit.png'),
                        title=f'Phase 4: orbit trajectory ({len(traj)} samples)')

        with open(os.path.join(OUT_DIR, 'phase4_traj.json'), 'w') as f:
            json.dump({
                'ticks': ticks_at.tolist(),
                'positions': traj.tolist(),
                'period_ticks': int(period_ticks) if period_ticks is not None else None,
            }, f, indent=2)

        if period_ticks is not None:
            print(f"\nPhase 4: planet returned to start near tick {period_ticks} -> orbit detected")
        else:
            print("\nPhase 4: no closed orbit detected within run length -- increase ticks or tune alpha/tangent_bias")

    print("Phase 4 done.")


if __name__ == '__main__':
    main()
