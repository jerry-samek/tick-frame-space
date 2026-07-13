"""AR(1) diffusion dynamics for Exp 137 Phase 0.

x_{t+1} = lam * P_lazy x_t + xi_t,  P_lazy = (I + D^-1 A)/2,  xi ~ N(0, I).

Deliberately inert: no force law, no consumption, no entities. Phase 0 tests
the readout, not a mechanism.

RETUNE (2026-07-03, the single G5-permitted deviation, logged in RESULTS):
the PREREG dynamics (plain walk, lam=0.9) failed the G5 positive control —
correlations sat below the sampling floor, and on bipartite fixtures the
checkerboard mode (mu ~ -1, variance ~ 1/(1 - lam^2 mu^2)) inverted the
distance profile (d6 > d1). Fix: lazy walk (spectrum -> [0,1], kills the
parity mode) + lam=0.99 (correlations above floor across the R=6 ball).
Chosen via diagnostic_dynamics.py scan, then frozen.
"""

import numpy as np
from scipy import sparse


def walk_matrix(adj):
    n = len(adj)
    rows, cols = [], []
    for i, nbrs in enumerate(adj):
        rows.extend([i] * len(nbrs))
        cols.extend(nbrs)
    a = sparse.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    deg = np.asarray(a.sum(axis=1)).ravel()
    return sparse.diags(1.0 / deg) @ a


def run_ar1(adj, taps, lam=0.99, burn=1000, steps=20000, rng=None):
    """Run the diffusion; return (steps, len(taps)) tap recordings."""
    rng = rng or np.random.default_rng()
    p = walk_matrix(adj)
    p = 0.5 * (sparse.identity(p.shape[0], format="csr") + p)  # lazy walk
    n = len(adj)
    x = np.zeros(n)
    out = np.empty((steps, len(taps)))
    for t in range(burn + steps):
        x = lam * (p @ x) + rng.standard_normal(n)
        if t >= burn:
            out[t - burn] = x[taps]
    return out
