#!/usr/bin/env python3
"""Phase 5: Emergent orbit (stretch goal).

Per spec section 5 Phase 5:
  - same setup as Phase 4 minus the seeded tangential bias
  - if a coherent orbit emerges anyway, renewal-not-identity is earned in
    the strongest possible sense

Don't be disappointed if this fails. Phase 4 success is already the weekend win.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import everything from phase4 and override TANGENT_BIAS_QUANTA to 0
import phase4_orbit
phase4_orbit.TANGENT_BIAS_QUANTA = 0
phase4_orbit.OUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'results'
)


# Override the output filenames so we don't overwrite Phase 4 results
def _patched_main():
    # Re-run main with bias=0 and different output names
    import json
    import time
    import numpy as np
    from substrate import build_rgg, init_state, tick
    from metrics import per_tick_summary, cluster_high_energy
    from visualization import plot_trajectory

    p = phase4_orbit
    print(f"Phase 5 (emergent): alpha={p.ALPHA}, tangent_bias=0")

    coords, src, dst, back_edge = build_rgg(p.N_NODES, p.RADIUS, seed=p.SEED)
    n_directed = len(src)

    d_star = np.linalg.norm(coords - p.STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(d_star)[:p.STAR_CELLS]
    d_planet = np.linalg.norm(coords - p.PLANET_CENTER[None, :], axis=1)
    planet_idx = np.argsort(d_planet)[:p.PLANET_CELLS]

    energy_init = np.full(p.N_NODES, p.BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] += p.STAR_MASS // p.STAR_CELLS
    energy_init[planet_idx] += p.PLANET_MASS // p.PLANET_CELLS
    total_initial = int(energy_init.sum())

    E, received = init_state(p.N_NODES, n_directed, energy_init)
    # NO tangential bias seed

    planet_positions = []
    t0 = time.time()
    for t in range(1, p.N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=p.ALPHA)
        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(f"CONSERVATION at tick {t}")

        if t % 25 == 0:
            clusters = cluster_high_energy(E, coords, threshold_quantile=0.995)
            if len(clusters) >= 2:
                planet_positions.append((t, clusters[1]['centroid']))
            if t % 500 == 0:
                rate = t / (time.time() - t0)
                print(f"  tick {t}, {rate:.0f} t/s")

    if planet_positions:
        traj = np.array([pp[1] for pp in planet_positions])
        plot_trajectory(traj, star_pos=p.STAR_CENTER,
                        out_path=os.path.join(p.OUT_DIR, 'phase5_emergent.png'),
                        title='Phase 5: emergent (no tangent bias)')
        with open(os.path.join(p.OUT_DIR, 'phase5_traj.json'), 'w') as f:
            json.dump({
                'ticks': [int(pp[0]) for pp in planet_positions],
                'positions': [list(pp[1]) for pp in planet_positions],
            }, f, indent=2)

    print("Phase 5 done.")


if __name__ == '__main__':
    _patched_main()
