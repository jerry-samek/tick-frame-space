"""Exp 138 — Ollivier-Ricci curvature: exact (LP transport) and Jost-Liu bound.

kappa(i,j) = 1 - W1(mu_i, mu_j), mu_v uniform on neighbors of v, ground
metric = graph distance. Exact W1 via scipy linprog (small supports), or the
matching fast path for equal degrees (P0's declared action — NOT Jost-Liu,
which is degree-constant under the hard-core condition; see PREREG_P0.md).
Jost-Liu retained as a validated lower bound for reference only.
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


_PERMS4 = None


def kappa_exact_regular(adj, i, j):
    """Exact Ollivier curvature for equal-degree endpoints via min-cost
    perfect matching (Birkhoff: equal uniform marginals -> permutation
    extreme points). Enumerates k! permutations; intended for k = 4.
    Distances by 3-level set expansion (fast path; == BFS cutoff 3).
    Row/column order of the cost matrix is irrelevant to the matching min,
    so adjacency may be sets or lists."""
    global _PERMS4
    si, sj = list(adj[i]), list(adj[j])
    k = len(si)
    if len(sj) != k:
        return kappa_exact(adj, i, j)  # unequal degrees: fall back to LP
    if _PERMS4 is None or len(_PERMS4[0]) != k:
        from itertools import permutations
        _PERMS4 = list(permutations(range(k)))
    cost = [[0.0] * k for _ in range(k)]
    for a, u in enumerate(si):
        d1 = set(adj[u])
        d2 = set()
        for x in d1:
            d2 |= set(adj[x])
        d2 -= d1
        d2.discard(u)
        d3 = set()
        for x in d2:
            d3 |= set(adj[x])
        d3 -= d2
        d3 -= d1
        d3.discard(u)
        row = cost[a]
        for b, v in enumerate(sj):
            row[b] = (0.0 if v == u else 1.0 if v in d1
                      else 2.0 if v in d2 else 3.0 if v in d3 else 4.0)
    best = min(sum(cost[a][p[a]] for a in range(k)) for p in _PERMS4)
    return 1.0 - best / k


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
