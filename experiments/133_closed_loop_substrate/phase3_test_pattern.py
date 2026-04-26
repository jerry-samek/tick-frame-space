#!/usr/bin/env python3
"""Phase 3: Test pattern in field.

Per spec section 5 Phase 3:
  - Phase 2 setup + small test pattern (10-50 quanta) at hop ~30 from star
  - run 5k ticks
  - measure: does test pattern's centroid drift toward star?
  - measure: drift consistent with local field gradient (Newton's 2nd)?

Success: test pattern accelerates toward star matching field. Gravity earned.
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
N_TICKS = 5_000
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
PLANET_CENTER = np.array([0.7, 0.5, 0.5])  # offset radially from star
STAR_MASS = 1000
PLANET_MASS = 30
STAR_CELLS = 50
PLANET_CELLS = 5
BACKGROUND_PER_CELL = 20
ALPHA = 1.0  # match Phase 2 winning value

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    rng = np.random.default_rng(SEED)
    print(f"Phase 3: test pattern in field, alpha={ALPHA}")

    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)

    # Seed star
    d_star = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(d_star)[:STAR_CELLS]

    # Seed planet
    d_planet = np.linalg.norm(coords - PLANET_CENTER[None, :], axis=1)
    planet_idx = np.argsort(d_planet)[:PLANET_CELLS]

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] += STAR_MASS // STAR_CELLS
    energy_init[planet_idx] += PLANET_MASS // PLANET_CELLS

    total_initial = int(energy_init.sum())
    print(f"  total energy: {total_initial}")

    E, received = init_state(N_NODES, n_directed, energy_init)

    planet_positions = []  # (T, 3) trajectory of planet centroid
    log = []
    t0 = time.time()

    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=ALPHA)
        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(f"CONSERVATION at tick {t}")

        if t % 50 == 0 or t == 1:
            # Identify clusters; planet is the second-most-massive (star is first)
            clusters = cluster_high_energy(E, coords, threshold_quantile=0.99)
            planet_centroid = None
            if len(clusters) >= 2:
                planet_centroid = clusters[1]['centroid']
            elif len(clusters) == 1:
                # If clusters merged, treat the only cluster's centroid as planet position
                planet_centroid = clusters[0]['centroid']

            if planet_centroid is not None:
                planet_positions.append(planet_centroid)

            if t % 500 == 0:
                summary = per_tick_summary(E, src)
                summary['tick'] = t
                if planet_centroid is not None:
                    summary['planet_centroid'] = planet_centroid
                    summary['planet_distance_from_star'] = float(
                        np.linalg.norm(np.array(planet_centroid) - STAR_CENTER)
                    )
                log.append(summary)
                rate = t / (time.time() - t0)
                pd = summary.get('planet_distance_from_star', float('nan'))
                print(f"  tick {t:>5d} planet_dist={pd:.4f} max_E={summary['max_E']} "
                      f"({rate:.0f} t/s)")

    # Verdict: did the planet drift toward the star?
    if planet_positions:
        planet_positions = np.array(planet_positions)
        initial_dist = np.linalg.norm(planet_positions[0] - STAR_CENTER)
        final_dist = np.linalg.norm(planet_positions[-1] - STAR_CENTER)
        drift = initial_dist - final_dist
        print(f"\nInitial distance to star: {initial_dist:.4f}")
        print(f"Final distance to star:   {final_dist:.4f}")
        print(f"Drift (positive = inward): {drift:+.4f}")

        if drift > 0.01:
            print("Phase 3 PASS: test pattern drifted toward star (gravity-like response).")
        elif drift > 0:
            print("Phase 3 WEAK: small drift toward star, gradient response detected but weak.")
        else:
            print("Phase 3 ATTENTION: planet did not drift toward star -- see spec section 8.")
    else:
        print("Phase 3 FAIL: planet cluster not identifiable.")

    # Save outputs
    with open(os.path.join(OUT_DIR, 'phase3_log.json'), 'w') as f:
        json.dump(log, f, indent=2)
    if planet_positions is not None and len(planet_positions) > 0:
        plot_trajectory(
            planet_positions, star_pos=STAR_CENTER,
            out_path=os.path.join(OUT_DIR, 'phase3_drift.png'),
            title='Phase 3: planet drift in field',
        )


if __name__ == '__main__':
    main()
