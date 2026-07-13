#!/usr/bin/env python3
"""Phase 2c: alpha sweep.

Phase 2b showed slope ~0, r^2 < 0.22 at every tick at alpha=1.0 -- the
rule does not drive radial flow at this wake-bias strength. This script
tests whether *stronger* wake bias creates a measurable gradient.

Tries alpha in {3.0, 5.0, 10.0}, 2000 ticks each, slope measured at
snapshot ticks. Reports a comparison table.
"""

import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from metrics import per_tick_summary
from visualization import radial_density_profile, fit_loglog_slope


N_NODES = 100_000
RADIUS = 0.025
N_TICKS = 2_000
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
STAR_MASS = 1000
STAR_CELLS = 50
BACKGROUND_PER_CELL = 20

ALPHAS = [3.0, 5.0, 10.0]
SNAPSHOT_TICKS = [10, 30, 100, 300, 500, 1000, 2000]

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def run_alpha(coords, src, dst, back_edge, alpha):
    n_directed = len(src)

    distances = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(distances)[:STAR_CELLS]

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] += STAR_MASS // STAR_CELLS
    total_initial = int(energy_init.sum())

    E, received = init_state(N_NODES, n_directed, energy_init)

    snapshots = []
    t0 = time.time()
    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=alpha)
        if int(E.sum()) != total_initial:
            raise AssertionError(f"CONSERVATION at tick {t}, alpha={alpha}")

        if t in SNAPSHOT_TICKS:
            r_centers, density = radial_density_profile(
                E, coords, STAR_CENTER, n_bins=25
            )
            slope, _, r2 = fit_loglog_slope(r_centers, density)
            snapshots.append({
                'tick': t, 'slope': slope, 'r_squared': r2, 'max_E': int(E.max()),
            })

    rate = N_TICKS / (time.time() - t0)
    return snapshots, rate


def main():
    print(f"Phase 2c: alpha sweep over {ALPHAS}, {N_TICKS} ticks each")
    print(f"Building RGG: N={N_NODES}, radius={RADIUS}")
    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    print(f"  directed edges: {len(src):,}, mean degree: {len(src)/N_NODES:.1f}\n")

    all_results = {}
    for alpha in ALPHAS:
        print(f"--- alpha = {alpha} ---")
        snapshots, rate = run_alpha(coords, src, dst, back_edge, alpha)
        all_results[alpha] = snapshots
        for s in snapshots:
            print(f"  tick {s['tick']:>5d}  slope={s['slope']:>7.3f}  "
                  f"r2={s['r_squared']:>5.3f}  max_E={s['max_E']:>5d}")
        print(f"  ({rate:.0f} t/s)\n")

    with open(os.path.join(OUT_DIR, 'phase2c_alpha_sweep.json'), 'w') as f:
        json.dump({str(a): all_results[a] for a in ALPHAS}, f, indent=2)

    # Verdict
    print("=== Best slope per alpha (across all snapshots) ===")
    any_pass = False
    for alpha in ALPHAS:
        best = min(all_results[alpha], key=lambda s: s['slope'])
        print(f"  alpha={alpha:>5.1f}  best_slope={best['slope']:>7.3f}  "
              f"at tick {best['tick']:>5d}  r2={best['r_squared']:>5.3f}")
        if -2.5 < best['slope'] < -1.5 and best['r_squared'] > 0.5:
            any_pass = True

    if any_pass:
        print("\nPhase 2c RESULT: at least one alpha showed a 1/r^2-shaped field.")
    else:
        print("\nPhase 2c RESULT: no alpha in the sweep produced a 1/r^2 gradient. "
              "The rule does not drive radial flow at any tested wake-bias strength.")


if __name__ == '__main__':
    main()
