"""Exp 138 — Ollivier-Ricci curvature: exact (LP transport) and Jost-Liu bound.

kappa(i,j) = 1 - W1(mu_i, mu_j), mu_v uniform on neighbors of v, ground
metric = graph distance. Exact W1 via scipy linprog (small supports).
Jost-Liu combinatorial lower bound for the O(1) fast path (P0's declared
action). Cross-validation required before the fast path is used at scale.
"""

import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import bfs_distances  # noqa: E402


def kappa_exact(adj, i, j):
    """Exact Ollivier curvature via LP optimal transport."""
    si, sj = sorted(adj[i]), sorted(adj[j])
    ni, nj = len(si), len(sj)
    cutoff = 3  # supports are neighbors of adjacent nodes: d <= 3 suffices
    cost = np.empty((ni, nj))
    for a, u in enumerate(si):
        dist = bfs_distances(adj, u, cutoff=cutoff)
        for b, v in enumerate(sj):
            cost[a, b] = dist.get(v, cutoff + 1)
    # LP: minimize sum c_ab x_ab, rows sum to 1/ni, cols sum to 1/nj
    A_eq = []
    b_eq = []
    for a in range(ni):
        row = np.zeros(ni * nj)
        row[a * nj : (a + 1) * nj] = 1
        A_eq.append(row)
        b_eq.append(1.0 / ni)
    for b in range(nj):
        col = np.zeros(ni * nj)
        col[b::nj] = 1
        A_eq.append(col)
        b_eq.append(1.0 / nj)
    res = linprog(cost.ravel(), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=(0, None), method="highs")
    if not res.success:
        raise RuntimeError(f"transport LP failed on edge ({i},{j})")
    return 1.0 - float(res.fun)


def kappa_jl(adj, i, j):
    """Jost-Liu lower bound (uniform measures, unweighted graph)."""
    di, dj = len(adj[i]), len(adj[j])
    t = len(set(adj[i]) & set(adj[j]))  # common neighbors (triangles on edge)
    pos = lambda x: max(x, 0.0)  # noqa: E731
    return (-pos(1 - 1.0 / di - 1.0 / dj - t / min(di, dj))
            - pos(1 - 1.0 / di - 1.0 / dj - t / max(di, dj))
            + t / max(di, dj))


def validate(adj, edges, tol=1e-9):
    """Check kappa_jl <= kappa_exact on the given edges; return stats."""
    diffs = []
    for (i, j) in edges:
        ke = kappa_exact(adj, i, j)
        kj = kappa_jl(adj, i, j)
        if kj > ke + tol:
            raise AssertionError(f"JL bound violated on ({i},{j}): {kj} > {ke}")
        diffs.append(ke - kj)
    return {"n": len(diffs), "mean_gap": float(np.mean(diffs)),
            "max_gap": float(np.max(diffs))}
