#!/usr/bin/env python3
"""Phase 2b: Transient slope measurement.

Hypothesis (post-Phase-2): the flat slope at tick 10000 is a steady-state
artifact of a finite substrate where energy round-trips many times during
the run. If our reading is correct, the slope should be 1/r^2-shaped
*early* in the run (energy in transit outward) and flatten as energy
equilibrates against the boundary.

Same setup as Phase 2; measure slope at every snapshot tick instead of
only at the end.
"""

import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from metrics import per_tick_summary, cluster_high_energy
from visualization import radial_density_profile, fit_loglog_slope, plot_radial_profile


N_NODES = 100_000
RADIUS = 0.025
N_TICKS = 10_000
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
STAR_MASS = 1000
STAR_CELLS = 50
BACKGROUND_PER_CELL = 20
ALPHA = 1.0

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)

SNAPSHOT_TICKS = [10, 30, 100, 300, 500, 1000, 2500, 5000, 7500, 10000]


def main():
    print(f"Phase 2b: transient slope, alpha={ALPHA}")
    print(f"Building RGG: N={N_NODES}, radius={RADIUS}")
    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)
    print(f"  directed edges: {n_directed:,}, mean degree: {n_directed/N_NODES:.1f}")

    distances = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(distances)[:STAR_CELLS]

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] += STAR_MASS // STAR_CELLS

    total_initial = int(energy_init.sum())
    print(f"  total energy: {total_initial:,}")

    E, received = init_state(N_NODES, n_directed, energy_init)

    slopes_per_tick = []
    t0 = time.time()

    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=ALPHA)
        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(f"CONSERVATION at tick {t}")

        if t in SNAPSHOT_TICKS:
            r_centers, density = radial_density_profile(
                E, coords, STAR_CENTER, n_bins=25
            )
            slope, intercept, r2 = fit_loglog_slope(r_centers, density)

            elapsed = time.time() - t0
            rate = t / elapsed
            print(f"  tick {t:>6d} slope={slope:>7.3f} r2={r2:>5.3f} "
                  f"max_E={int(E.max()):>4d} ({rate:.0f} t/s)")

            slopes_per_tick.append({
                'tick': t,
                'slope': slope,
                'intercept': intercept,
                'r_squared': r2,
                'max_E': int(E.max()),
                'r_centers': r_centers.tolist(),
                'density': density.tolist(),
            })

            # Save plot at this tick
            plot_radial_profile(
                r_centers, density, slope=slope,
                out_path=os.path.join(OUT_DIR, f'phase2b_field_t{t}.png'),
                title=f'Phase 2b: tick {t}, slope={slope:.3f}',
            )

    with open(os.path.join(OUT_DIR, 'phase2b_slopes.json'), 'w') as f:
        json.dump(slopes_per_tick, f, indent=2)

    print(f"\nSlope evolution:")
    for s in slopes_per_tick:
        print(f"  tick {s['tick']:>6d}  slope={s['slope']:>7.3f}  r2={s['r_squared']:>5.3f}")

    # Verdict
    early = [s for s in slopes_per_tick if s['tick'] <= 500 and s['r_squared'] > 0.3]
    if early and any(-2.5 < s['slope'] < -1.5 for s in early):
        print("\nPhase 2b RESULT: 1/r^2-shaped transient detected -- substrate-too-small hypothesis CONFIRMED.")
    elif slopes_per_tick and all(s['r_squared'] < 0.3 for s in slopes_per_tick):
        print("\nPhase 2b RESULT: no fit at any tick (r^2 always low) -- rule does not drive radial flow.")
    else:
        print("\nPhase 2b RESULT: slope evolution does not match either prediction -- inspect manually.")


if __name__ == '__main__':
    main()
