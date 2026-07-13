"""Diagnostic for the single permitted G5 retune (see PREREG.md 'Deviations').

Scans lambda x {plain, lazy} walk on lattice3d + expander, one seed, short T.
NOT the experiment — instrument tuning only; the chosen setting is then frozen
and Phase 0 re-run in full.
"""

import numpy as np

from graphs import torus3d, random_regular, bfs_distances, sample_bundle
from readout import corrmat, corr_decay
import dynamics as dyn
from scipy import sparse


def run(adj, taps, lam, lazy, rng, burn=500, steps=10000):
    p = dyn.walk_matrix(adj)
    if lazy:
        p = 0.5 * (sparse.identity(p.shape[0], format="csr") + p)
    n = len(adj)
    x = np.zeros(n)
    out = np.empty((steps, len(taps)))
    for t in range(burn + steps):
        x = lam * (p @ x) + rng.standard_normal(n)
        if t >= burn:
            out[t - burn] = x[taps]
    return out


def main():
    for name, gen in (("lattice3d", lambda r: torus3d(12)),
                      ("expander", lambda r: random_regular(1750, 3, r))):
        for lam in (0.9, 0.99, 0.999):
            for lazy in (False, True):
                rng = np.random.default_rng(0)
                adj = gen(rng)
                center, taps, _ = sample_bundle(adj, 64, 6, rng)
                x = run(adj, taps, lam, lazy, rng)
                c = corrmat(x)
                dist = {int(t): bfs_distances(adj, int(t), cutoff=6) for t in taps}
                d1, d6 = corr_decay(c, taps, dist)
                print(f"{name:<10} lam={lam:<6} lazy={lazy!s:<6} "
                      f"d1={d1:.4f} d6={d6:.4f} ratio={d1 / d6 if d6 else float('nan'):.2f}",
                      flush=True)


if __name__ == "__main__":
    main()
