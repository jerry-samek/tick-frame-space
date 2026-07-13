#!/usr/bin/env python3
"""Phase 1: Conservation + diffusion sanity.

Per spec §5 Phase 1:
  - random uniform energy across all cells
  - run 1000 ticks
  - verify: total energy invariant every tick (built-in assertion)
  - α=0: distribution stays statistically uniform (pure diffusion baseline)
  - α>0: no obvious instability (no runaway concentration, no explosive osc.)

Failure here = bug, not physics. Must pass before later phases mean anything.
"""

import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from metrics import per_tick_summary


N_NODES = 50_000      # smaller for fast Phase 1
RADIUS = 0.04         # tuned for mean degree ~12
N_TICKS = 1_000
ENERGY_PER_CELL = 100  # avg energy per cell; needs to be >> degree for active flow
SEED = 42

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def run(alpha: float):
    print(f"=== Phase 1 sanity, α={alpha} ===")
    rng = np.random.default_rng(SEED)
    print(f"Building RGG: N={N_NODES}, radius={RADIUS}")
    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)
    mean_degree = n_directed / N_NODES
    print(f"  edges (directed): {n_directed:,}, mean degree: {mean_degree:.1f}")

    energy_init = rng.integers(
        ENERGY_PER_CELL // 2, (3 * ENERGY_PER_CELL) // 2,
        size=N_NODES, dtype=np.int64,
    )
    total_initial = int(energy_init.sum())
    print(f"  total energy: {total_initial:,}, mean E per cell: {energy_init.mean():.1f}")

    E, received = init_state(N_NODES, n_directed, energy_init)

    log = []
    t0 = time.time()
    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=alpha)

        # Conservation invariant — fail loudly if violated
        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(
                f"CONSERVATION VIOLATED at tick {t}: {total} != {total_initial}"
            )

        if t % 100 == 0:
            summary = per_tick_summary(E, src)
            summary['tick'] = t
            summary['alpha'] = alpha
            summary['std_E'] = float(np.std(E))
            log.append(summary)
            elapsed = time.time() - t0
            rate = t / elapsed
            eta = (N_TICKS - t) / rate
            print(
                f"  tick {t:>5d} max_E={summary['max_E']:>5d} "
                f"std_E={summary['std_E']:>6.2f} firing={summary['n_firing_cells']:>6d} "
                f"({rate:.0f} t/s, eta {eta:.0f}s)"
            )

    # Save summary
    out_path = os.path.join(OUT_DIR, f'phase1_alpha{alpha}.json')
    with open(out_path, 'w') as f:
        json.dump(log, f, indent=2)
    print(f"  saved {out_path}")

    # Sanity checks
    final_std = log[-1]['std_E']
    initial_std = float(np.std(energy_init))
    if alpha == 0.0:
        # Pure diffusion: std should NOT increase. Allow some fluctuation due to
        # threshold-firing dynamics (cells holding integer residues).
        if final_std > 1.5 * initial_std:
            print(f"  WARN: std grew from {initial_std:.2f} to {final_std:.2f} at α=0 — investigate")
        else:
            print(f"  OK: std stable at α=0 ({initial_std:.2f} → {final_std:.2f})")
    else:
        # With wake bias, some structure may form, but not runaway.
        max_E = log[-1]['max_E']
        if max_E > 10 * ENERGY_PER_CELL:
            print(f"  WARN: max_E={max_E} indicates possible runaway concentration")
        else:
            print(f"  OK: max_E={max_E} bounded")

    return log


if __name__ == '__main__':
    log_alpha0 = run(alpha=0.0)
    log_alpha1 = run(alpha=1.0)
    print("\nPhase 1 complete. Conservation passed all ticks.")
