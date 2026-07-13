"""Boundary-layer dimension instrument (RAW 137).

Measures perceived dimension the framework's way: inside-out, from an
observer's boundary layer, via LAG — no god-view, no field.

Observer = a bundle of N nearby taps (an "eye"). Each tap reads its lag
(graph distance) to a sample of source entities; deposits arrive down direct
pipes with a delay = that lag. Perceived ANGULAR dimension = participation-
ratio rank of the tap x tap correlation of lag-vectors (near taps share their
lag-pattern -> correlated -> low rank; independent directions -> high rank).
This is CCM 2017 / V3 ch003 grounded in propagation delay, and the properly
grounded form of Exp 137's D_PR.

Pairs with ball-growth (radial): a tree reads low angular rank but exponential
growth, so angular-rank alone cannot separate a 1-manifold from a tree; the two
observer-native observables together (angular rank + radial growth) do.

Validated against the adversarial zoo that broke the god-view instruments
(P1c d_s; the shell+4cycle gate — hypercube false-positive, honeycomb
false-negative). Run this file to reproduce the table in RAW 137.
"""

import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import binary_tree, random_regular, torus2d, torus3d  # noqa: E402


def _bfs(adj, s, cutoff):
    d = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        if d[u] >= cutoff:
            continue
        for v in adj[u]:
            if v not in d:
                d[v] = d[u] + 1
                q.append(v)
    return d


def _pr(eigs):
    e = np.clip(eigs, 0.0, None)
    s2 = float((e * e).sum())
    return float(e.sum() ** 2 / s2) if s2 > 0 else 0.0


def perceived_dim(adj, n_taps=24, n_src=200, tap_radius=3, seed=0):
    """Lag-correlation participation-ratio rank read by an observer bundle."""
    rng = np.random.default_rng(seed)
    n = len(adj)
    center = int(rng.integers(n))
    ball = sorted(_bfs(adj, center, tap_radius).keys())
    taps = ball[:n_taps] if len(ball) >= n_taps else ball
    srcs = sorted(int(x) for x in rng.choice(n, min(n_src, n), replace=False))
    lag = np.zeros((len(taps), len(srcs)))
    for i, t in enumerate(taps):
        dt = _bfs(adj, t, 30)
        for j, s in enumerate(srcs):
            lag[i, j] = dt.get(s, 30)
    lag = lag[np.std(lag, axis=1) > 1e-9]
    if len(lag) < 3:
        return float("nan")
    c = np.nan_to_num(np.corrcoef(lag))
    return _pr(np.linalg.eigvalsh(c))


# ---- adversarial-zoo generators (non-lattice cases) ----

def hypercube(d):
    n = 1 << d
    adj = [[] for _ in range(n)]
    for x in range(n):
        for b in range(d):
            adj[x].append(x ^ (1 << b))
    return [sorted(a) for a in adj]


def honeycomb(L):
    """Brick-wall honeycomb (girth 6, genuine 2-manifold, zero 4-cycles)."""
    idx = lambda r, c: (r % L) * L + (c % L)  # noqa: E731
    adj = [set() for _ in range(L * L)]
    for r in range(L):
        for c in range(L):
            v = idx(r, c)
            adj[v] |= {idx(r, c + 1), idx(r, c - 1)}
            o = idx(r + 1, c) if (r + c) % 2 == 0 else idx(r - 1, c)
            adj[v].add(o)
            adj[o].add(v)
    return [sorted(a) for a in adj]


def small_world(n, k, p, seed):
    rng = np.random.default_rng(seed)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(1, k // 2 + 1):
            adj[i].add((i + j) % n)
            adj[(i + j) % n].add(i)
    for i in range(n):
        for j in range(1, k // 2 + 1):
            if rng.random() < p:
                a = (i + j) % n
                adj[i].discard(a)
                adj[a].discard(i)
                b = int(rng.integers(n))
                while b == i or b in adj[i]:
                    b = int(rng.integers(n))
                adj[i].add(b)
                adj[b].add(i)
    return [sorted(a) for a in adj]


def main():
    cases = [
        ("torus2d(24)", "manifold-2", torus2d(24)),
        ("torus3d(11)", "manifold-3", torus3d(11)),
        ("honeycomb(30)", "manifold-2", honeycomb(30)),
        ("binary_tree(12)", "tree", binary_tree(12)),
        ("random_reg(2000,4)", "expander", random_regular(2000, 4, np.random.default_rng(0))),
        ("hypercube(10)", "non(d=10)", hypercube(10)),
        ("small_world p=.1", "expander", small_world(2000, 6, 0.1, 0)),
        ("small_world p=.01", "near-manifold", small_world(2000, 6, 0.01, 0)),
    ]
    print(f"{'graph':<20}{'truth':<15}perceived_dim (lag-rank), seeds 1/2/3")
    for name, truth, g in cases:
        vals = [perceived_dim(g, seed=s) for s in (1, 2, 3)]
        print(f"{name:<20}{truth:<15}{[round(v, 1) for v in vals]}")


if __name__ == "__main__":
    main()
