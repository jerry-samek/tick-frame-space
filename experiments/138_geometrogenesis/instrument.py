"""Exp 138 — ball-growth-exponent instrument (frozen in PREREG_I0.md).

Shell counts N(r) over BFS shells, mean over sources; polynomial vs
exponential classification by R² on the pre-peak window r in [2, r_peak].
"""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import bfs_distances  # noqa: E402

N_SOURCES = 64


def shell_counts(adj, sources):
    """Mean shell counts N̄(r) over the given sources; length = max dist + 1."""
    rows = []
    for s in sources:
        dist = bfs_distances(adj, int(s))
        counts = np.bincount(np.fromiter(dist.values(), dtype=int))
        rows.append(counts)
    r_max = max(len(c) for c in rows)
    acc = np.zeros(r_max)
    for c in rows:
        acc[: len(c)] += c
    return acc / len(rows)


def fit_exponent(nbar):
    """I0b estimator (PREREG_I0b.md): window r in [1, r_cut] with cumulative
    ball <= N/2; features = median shell ratio + both fits; `exp` iff
    ratio >= 1.9 OR R2_exp > R2_poly."""
    total = float(np.sum(nbar))
    cum = np.cumsum(nbar)
    below = np.where(cum <= total / 2)[0]
    r_cut = int(below[-1]) if below.size else 0
    rs = np.arange(1, r_cut + 1)
    if rs.size < 3:
        return {"cls": "degenerate", "e_hat": float("nan"),
                "rate_exp": float("nan"), "r2_poly": float("nan"),
                "r2_exp": float("nan"), "ratio_med": float("nan"),
                "window": (1, r_cut)}
    vals = np.clip(nbar[1 : r_cut + 1], 1e-12, None)
    y = np.log(vals)
    ratio_med = float(np.median(vals[1:] / vals[:-1]))

    def lsq(x):
        A = np.vstack([x, np.ones_like(x)]).T
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        resid = y - A @ coef
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1.0 - float(np.sum(resid**2)) / ss_tot if ss_tot > 0 else 0.0
        return float(coef[0]), r2

    e_hat, r2_poly = lsq(np.log(rs.astype(float)))
    rate, r2_exp = lsq(rs.astype(float))
    # I0c (PREREG_I0c.md): classification by R2 comparison ONLY; ratio_med
    # is a reported diagnostic, not a classifier.
    is_exp = r2_exp > r2_poly
    return {"cls": "exp" if is_exp else "poly",
            "e_hat": e_hat, "rate_exp": rate,
            "r2_poly": r2_poly, "r2_exp": r2_exp,
            "ratio_med": ratio_med, "window": (1, r_cut)}


def classify(adj, rng, n_sources=N_SOURCES):
    """Sample sources with the given rng, return fit dict (+ sources used)."""
    n = len(adj)
    if n <= n_sources:
        sources = list(range(n))
    else:
        sources = sorted(int(x) for x in rng.choice(n, n_sources, replace=False))
    out = fit_exponent(shell_counts(adj, sources))
    out["n_sources"] = len(sources)
    return out
