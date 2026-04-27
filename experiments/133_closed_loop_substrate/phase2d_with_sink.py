#!/usr/bin/env python3
"""Phase 2d: with source + absorbing boundary.

Test B from the post-Phase-2 conversation: break strict conservation and
add the source/sink structure that 128 v11 used. If 1/r^2 returns, we've
confirmed: closed-loop pure-conservation is fundamentally incompatible
with sustained gravity in a finite substrate.

Modifications vs Phase 2:
  - Source: star cells held at fixed high E every tick (replenishes outflow)
  - Sink: cells beyond r > 0.45 from STAR_CENTER zeroed every tick (absorbs)

Note: this DELIBERATELY breaks the closed-loop conservation commitment.
It is a diagnostic, not a proposed substrate.

Alpha is set via CLI (default 1.0). Use the winning alpha from Phase 2c
if there was one; otherwise 1.0 reproduces 128 v11's regime closely.
"""

import argparse
import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from visualization import radial_density_profile, fit_loglog_slope, plot_radial_profile


N_NODES = 100_000
RADIUS = 0.025
N_TICKS = 2_000
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
STAR_MASS = 1000
STAR_CELLS = 50
BACKGROUND_PER_CELL = 20
SINK_RADIUS = 0.45  # cells beyond this distance from STAR_CENTER are absorbing

SNAPSHOT_TICKS = [10, 30, 100, 300, 500, 1000, 2000]

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def main(alpha: float):
    print(f"Phase 2d: source + sink, alpha={alpha}")
    print(f"Building RGG: N={N_NODES}, radius={RADIUS}")
    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)
    print(f"  directed edges: {n_directed:,}, mean degree: {n_directed/N_NODES:.1f}")

    distances = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(distances)[:STAR_CELLS]
    star_cell_E = STAR_MASS // STAR_CELLS  # energy per star cell

    sink_mask = distances > SINK_RADIUS
    n_sink = int(sink_mask.sum())
    print(f"  sink cells (r > {SINK_RADIUS}): {n_sink}")

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] = star_cell_E + BACKGROUND_PER_CELL  # star cells heavier
    energy_init[sink_mask] = 0  # sink cells start empty

    E, received = init_state(N_NODES, n_directed, energy_init)

    snapshots = []
    t0 = time.time()

    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=alpha)

        # Source: replenish star cells to fixed value
        E[star_idx] = star_cell_E + BACKGROUND_PER_CELL

        # Sink: zero out cells beyond SINK_RADIUS
        E[sink_mask] = 0

        if t in SNAPSHOT_TICKS:
            r_centers, density = radial_density_profile(
                E, coords, STAR_CENTER, n_bins=25, r_max=SINK_RADIUS * 0.9
            )
            slope, intercept, r2 = fit_loglog_slope(r_centers, density)
            elapsed = time.time() - t0
            rate = t / elapsed
            print(f"  tick {t:>5d}  slope={slope:>7.3f}  r2={r2:>5.3f}  "
                  f"max_E={int(E.max()):>5d}  total_E={int(E.sum()):>9d}  "
                  f"({rate:.0f} t/s)")
            snapshots.append({
                'tick': t, 'slope': slope, 'intercept': intercept,
                'r_squared': r2, 'max_E': int(E.max()),
                'total_E': int(E.sum()),
            })

            plot_radial_profile(
                r_centers, density, slope=slope,
                out_path=os.path.join(OUT_DIR, f'phase2d_field_t{t}.png'),
                title=f'Phase 2d (source+sink, alpha={alpha}): tick {t}, slope={slope:.3f}',
            )

    with open(os.path.join(OUT_DIR, f'phase2d_alpha{alpha}.json'), 'w') as f:
        json.dump(snapshots, f, indent=2)

    # Verdict — look for any tick with -2.5 < slope < -1.5 and r2 > 0.5
    passes = [s for s in snapshots if -2.5 < s['slope'] < -1.5 and s['r_squared'] > 0.5]
    if passes:
        best = min(passes, key=lambda s: abs(s['slope'] + 2.0))
        print(f"\nPhase 2d RESULT: 1/r^2 detected at tick {best['tick']} "
              f"(slope={best['slope']:.3f}, r2={best['r_squared']:.3f})")
        print(f"  -> source/sink structure RESTORES 1/r^2 even with the same rule.")
        print(f"  -> closed-loop pure-conservation is fundamentally incompatible "
              f"with sustained gravity.")
    else:
        print(f"\nPhase 2d RESULT: no 1/r^2 even with source/sink at alpha={alpha}.")
        best = min(snapshots, key=lambda s: s['slope'])
        print(f"  best slope was {best['slope']:.3f} (r2={best['r_squared']:.3f}) "
              f"at tick {best['tick']}.")
        print(f"  -> the rule itself does not drive radial flow even with source/sink. "
              f"Deeper rule revision needed.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--alpha', type=float, default=1.0)
    args = parser.parse_args()
    main(args.alpha)
