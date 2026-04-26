#!/usr/bin/env python3
"""Phase 2: Static star, field formation.

Per spec §5 Phase 2:
  - 1 heavy concentration (~1000 quanta in ~50 cells) + background uniform
  - run 10k ticks
  - measure: cluster persistence, gradient slope (target ~ -2.0, ref -1.968 from 128 v11)

Success: persistent star + 1/r^2 field. Failure modes per spec section 8.
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
STAR_MASS = 1000      # total quanta in star
STAR_CELLS = 50       # number of cells star spans
BACKGROUND_PER_CELL = 20
ALPHA = 1.0           # tunable: try a few values if first attempt is unstable

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    rng = np.random.default_rng(SEED)
    print(f"Phase 2: static star, alpha={ALPHA}")

    print(f"Building RGG: N={N_NODES}, radius={RADIUS}")
    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)
    print(f"  directed edges: {n_directed:,}, mean degree: {n_directed/N_NODES:.1f}")

    # Seed: star at STAR_CENTER, background uniform
    distances = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(distances)[:STAR_CELLS]

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] += STAR_MASS // STAR_CELLS  # spread star mass evenly across star cells

    total_initial = int(energy_init.sum())
    print(f"  total energy: {total_initial:,} (background {BACKGROUND_PER_CELL}/cell, "
          f"star ~{STAR_MASS} concentrated in {STAR_CELLS} cells)")

    E, received = init_state(N_NODES, n_directed, energy_init)

    log = []
    t0 = time.time()
    snapshot_ticks = [10, 100, 500, 1000, 2500, 5000, 7500, 10000]

    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=ALPHA)

        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(f"CONSERVATION at tick {t}: {total} != {total_initial}")

        if t in snapshot_ticks or t % 1000 == 0:
            clusters = cluster_high_energy(E, coords, threshold_quantile=0.99)
            if clusters:
                top = clusters[0]
                star_centroid = top['centroid']
                star_observed_mass = top['mass']
                star_drift = float(np.linalg.norm(np.array(star_centroid) - STAR_CENTER))
            else:
                star_centroid = (None, None, None)
                star_observed_mass = 0
                star_drift = float('nan')

            summary = per_tick_summary(E, src)
            summary['tick'] = t
            summary['star_centroid'] = star_centroid
            summary['star_observed_mass'] = star_observed_mass
            summary['star_drift'] = star_drift
            log.append(summary)

            elapsed = time.time() - t0
            rate = t / elapsed
            print(f"  tick {t:>6d} star_mass={star_observed_mass:>5d} "
                  f"drift={star_drift:.4f} max_E={summary['max_E']} "
                  f"({rate:.0f} t/s)")

    # Final field-slope measurement
    r_centers, density = radial_density_profile(E, coords, STAR_CENTER, n_bins=25)
    slope, intercept, r2 = fit_loglog_slope(r_centers, density)
    print(f"\nField slope = {slope:.3f}  (target: ~ -2.0, 128 v11 ref: -1.968)  r^2={r2:.3f}")

    # Persistence verdict
    final_top = cluster_high_energy(E, coords, threshold_quantile=0.99)
    persisted = bool(final_top) and final_top[0]['mass'] >= 0.5 * STAR_MASS

    print(f"Star persistence: {persisted} (final mass: {final_top[0]['mass'] if final_top else 0})")

    # Save outputs
    with open(os.path.join(OUT_DIR, 'phase2_log.json'), 'w') as f:
        json.dump(log, f, indent=2)

    plot_radial_profile(
        r_centers, density, slope=slope,
        out_path=os.path.join(OUT_DIR, 'phase2_field.png'),
        title=f'Phase 2: field, slope={slope:.3f}',
    )

    print(f"\nSummary written to {OUT_DIR}/phase2_log.json")
    print(f"Field plot: {OUT_DIR}/phase2_field.png")

    # Phase 2 verdict per spec section 5
    if persisted and -2.3 < slope < -1.7:
        print("\nPhase 2 PASS: star persists + field is 1/r^2-shaped.")
    else:
        print("\nPhase 2 ATTENTION: see falsification matrix in spec section 8.")


if __name__ == '__main__':
    main()
