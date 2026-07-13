"""Observer-rank readout for Exp 137 (observables O1-O4, frozen in PREREG.md)."""

import numpy as np


def corrmat(x):
    """Correlation matrix of channels; x shape (T, N)."""
    return np.corrcoef(x.T)


def dpr(eigs):
    """Participation ratio (sum(l))^2 / sum(l^2) over non-negative eigenvalues."""
    e = np.clip(np.asarray(eigs, dtype=float), 0.0, None)
    s2 = np.sum(e * e)
    if s2 == 0.0:
        return 0.0
    return float(np.sum(e) ** 2 / s2)


def dpr_raw(c):
    """O1: participation ratio of the correlation eigenspectrum."""
    return dpr(np.linalg.eigvalsh(c))


def dpr_sub(c):
    """O2: participation ratio after removing the top eigenvector (global mode).

    The explicit-whitening form of self-subtraction required by RAW 134 sec. 8.
    """
    e = np.sort(np.linalg.eigvalsh(c))[:-1]
    return dpr(e)


def mds_dim90_from_dist(d):
    """Classical MDS on distance matrix d; smallest k whose top-k positive
    eigenvalues carry >= 90% of the total positive eigenvalue mass."""
    n = d.shape[0]
    j = np.eye(n) - np.ones((n, n)) / n
    b = -0.5 * j @ (d * d) @ j
    e = np.sort(np.linalg.eigvalsh(b))[::-1]
    pos = e[e > 0]
    if pos.size == 0:
        return 0
    frac = np.cumsum(pos) / np.sum(pos)
    return int(np.searchsorted(frac, 0.9) + 1)


def mds_dim90(c):
    """O3: MDS dimension from correlation distance d_ij = sqrt(2 (1 - r_ij))."""
    d = np.sqrt(np.clip(2.0 * (1.0 - c), 0.0, None))
    np.fill_diagonal(d, 0.0)
    return mds_dim90_from_dist(d)


def corr_decay(c, taps, dist_by_tap):
    """O4: mean |r| at graph distance 1 vs distance 6 among taps.

    dist_by_tap: dict tap -> {node: dist} (BFS from each tap).
    Returns (mean_abs_r_d1, mean_abs_r_d6); nan if a bin is empty.
    """
    bins = {1: [], 6: []}
    for i in range(len(taps)):
        di = dist_by_tap[int(taps[i])]
        for k in range(i + 1, len(taps)):
            d = di.get(int(taps[k]))
            if d in bins:
                bins[d].append(abs(c[i, k]))
    return (
        float(np.mean(bins[1])) if bins[1] else float("nan"),
        float(np.mean(bins[6])) if bins[6] else float("nan"),
    )
