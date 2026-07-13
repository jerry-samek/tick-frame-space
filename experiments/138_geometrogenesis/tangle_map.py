"""Where does the tangle live? -- RELATIONAL map of the P1d heterogeneity.

Context / honest scope: the P1d 'manifold' graph is ~2200 nodes; the real universe
is ~10^80. We CANNOT and DO NOT simulate real scale, and a 2200-node blob has no
meaningful absolute shape. So this asks ONLY scale-independent RELATIONAL questions:
does the locally-tangled fraction (frac_exp~0.5) correlate with anything intrinsic,
or is it random speckle? A correlation is a correlation at any scale; it is a
statement about the MECHANISM, not about physics or geometry-at-scale. No claim is
made here about physical meaning.

Per node we flag its local neighborhood tangled (exp) or geometric (poly) with the
validated v2 reader (`ballgrowth_fixedK`). Then three relational tests on the P1d
manifold cell (q=0.20, c=1.0):
  1. tangle rate vs DEGREE bucket   -- is tangle at the hubs or the sparse spots?
  2. tangle rate vs DISTANCE from the biggest hub -- central (old core) or edge?
  3. CLUSTERING: are tangled nodes adjacent to tangled nodes more than chance?
     (edge same-status fraction vs a label-shuffle null) -- the random-vs-structured
     test. This is the decisive one.
"""

import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from ballgrowth_fixedK import _ball_to_K, _fit  # the validated v2 reader internals  # noqa: E402
from p1d_channel import grow_dissipative, BASE  # noqa: E402


def node_flags(adj, K=200):
    """Per-node local tangle flag: True=exp (tangled), False=poly (geometric),
    None=degenerate. Every node is an observer of its own local cone."""
    flags = [None] * len(adj)
    for v in range(len(adj)):
        rs, B, _ = _ball_to_K(adj, v, K)
        r = _fit(rs, B)
        flags[v] = None if r is None else (r[0] == "exp")
    return flags


def _dist_from(adj, src):
    d = {src: 0}; q = deque([src])
    while q:
        x = q.popleft()
        for y in adj[x]:
            if y not in d:
                d[y] = d[x] + 1; q.append(y)
    return d


def analyze(adj, flags, seed):
    deg = np.array([len(a) for a in adj])
    valid = np.array([f is not None for f in flags])
    tang = np.array([bool(f) for f in flags])
    p = tang[valid].mean()
    print(f"  overall tangle rate p = {p:.2f}  (n_valid={valid.sum()}/{len(adj)})")

    # 1. tangle vs degree
    print("  [1] tangle rate by DEGREE:")
    for lo, hi, lab in [(1, 2, "deg 1-2 (sparse)"), (3, 4, "deg 3-4"),
                        (5, 8, "deg 5-8"), (9, 10**9, "deg 9+ (hubs)")]:
        m = valid & (deg >= lo) & (deg <= hi)
        if m.sum() >= 10:
            print(f"      {lab:<18} tangle={tang[m].mean():.2f}  (n={int(m.sum())})")

    # 2. tangle vs distance from the biggest hub
    hub = int(np.argmax(deg))
    dd = _dist_from(adj, hub)
    dist = np.array([dd.get(v, -1) for v in range(len(adj))])
    print(f"  [2] tangle rate by DISTANCE from biggest hub (deg {deg[hub]}):")
    for r in range(0, int(dist[valid].max()) + 1, 2):
        m = valid & (dist >= r) & (dist < r + 2)
        if m.sum() >= 15:
            print(f"      dist {r}-{r+1:<3} tangle={tang[m].mean():.2f}  (n={int(m.sum())})")

    # 3. clustering: same-status edge fraction vs label-shuffle null
    edges = [(u, v) for u in range(len(adj)) for v in adj[u]
             if u < v and valid[u] and valid[v]]
    if edges:
        same = np.mean([tang[u] == tang[v] for u, v in edges])
        rng = np.random.default_rng(seed)
        idx = np.where(valid)[0]
        null = []
        for _ in range(200):
            perm = tang.copy()
            perm[idx] = rng.permutation(tang[idx])
            null.append(np.mean([perm[u] == perm[v] for u, v in edges]))
        null = np.array(null)
        z = (same - null.mean()) / (null.std() + 1e-9)
        print(f"  [3] CLUSTERING: same-status edge fraction = {same:.3f} vs "
              f"shuffle-null {null.mean():.3f}±{null.std():.3f}  (z={z:+.1f})")
        print(f"      (z is INFLATED: adjacent nodes' K={200}-balls overlap ~99% -> "
              "forced agreement. The real test is [4].)")

    # 4. THE decisive control: does agreement persist BEYOND the ball-overlap
    # scale? Window radius for K=200 at d~2.5 is ~9 hops. If P(same) decays to the
    # null (~p^2+(1-p)^2) by ~2x that, [3] was just window overlap; if it stays
    # above the null well beyond, the tangle is genuinely regional.
    null_same = p * p + (1 - p) * (1 - p)
    rng2 = np.random.default_rng(seed + 7)
    idx = np.where(valid)[0]
    srcs = rng2.choice(idx, min(120, len(idx)), replace=False)
    from collections import defaultdict
    bins = defaultdict(list)
    for s in srcs:
        dd = _dist_from(adj, int(s))
        for v, dv in dd.items():
            if dv > 0 and valid[v]:
                bins[dv].append(tang[s] == tang[v])
    print(f"  [4] P(same status) vs graph-distance  (null={null_same:.2f}; "
          "ball radius ~9 -> overlap fades by ~18):")
    row = []
    for dd in (1, 3, 6, 9, 12, 18, 24, 30):
        if len(bins[dd]) >= 30:
            row.append(f"d{dd}={np.mean(bins[dd]):.2f}")
    print("      " + "  ".join(row))


def main():
    print(__doc__.split("\n\n")[0])
    print("(relational only; ~2200-node toy; NO claim about physical scale.)\n")
    for sd in (1, 2):
        g = grow_dissipative(dict(BASE, mode="scalar_flux", q=0.20, c=1.0), sd, 3000)
        adj = g["lcc_adj"]
        if len(adj) < 500:
            print(f"seed {sd}: extinct/tiny (n={len(adj)}) -- skip"); continue
        print(f"--- P1d manifold cell, seed {sd} (n={len(adj)}) ---")
        flags = node_flags(adj)
        analyze(adj, flags, sd)
        print()
    print("Reading: if [3] is STRUCTURED and [1]/[2] show a gradient (tangle tracks "
          "hubs or the core), the non-uniformity is ORGANIZED by the mechanism -- a "
          "real lead. If [3] is random speckle and [1]/[2] are flat, it is just messy "
          "emergence. Either way: relational statement only, no physical claim.")


if __name__ == "__main__":
    main()
