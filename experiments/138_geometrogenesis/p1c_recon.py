"""Exp 138 P1c — pre-freeze reconnaissance (reachable-range rule).

Numbers the PREREG_P1C gates must be calibrated against BEFORE freezing:
  R1  d_s of the T5 frozen quench state (the FAIL baseline arm B must beat)
  R2  size-matched d_s + instrument anchors at N~2000: torus2d(45),
      tube C500xC4, torus3d(13)
  R3  growth-shape classifier validation: synthetic N(t)=c*t^2 must read
      poly-t; P1b production trajectories previously read 100/100 exp-t
  R4  non-descendant selector under quench: does turnover persist
      post-quench (engagement per window), or does it freeze?
"""

import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import torus2d, torus3d  # noqa: E402
from instrument import classify  # noqa: E402
from p1_growth import grow  # noqa: E402


def ds_sparse(adj, t_max=200, n_src=50, seed=0):
    """Spectral dimension via lazy-walk return probability, sparse,
    sampled sources. Same estimator family as p0_autopsy A4."""
    n = len(adj)
    rng = np.random.default_rng(seed)
    srcs = sorted(int(x) for x in rng.choice(n, min(n_src, n), replace=False))
    rows, cols, vals = [], [], []
    for i in range(n):
        d = len(adj[i])
        for j in adj[i]:
            rows.append(i)
            cols.append(j)
            vals.append(0.5 / d)
        rows.append(i)
        cols.append(i)
        vals.append(0.5)
    P = sp.csr_matrix((vals, (rows, cols)), shape=(n, n))
    X = np.zeros((n, len(srcs)))
    for k, s in enumerate(srcs):
        X[s, k] = 1.0
    rets = []
    for _ in range(t_max):
        X = P.T @ X
        rets.append(float(np.mean([X[s, k] for k, s in enumerate(srcs)])))
    ts = np.arange(20, t_max + 1)
    ys = np.log(np.array(rets[19:]))
    A = np.vstack([np.log(ts), np.ones_like(ts, float)]).T
    slope, _ = np.linalg.lstsq(A, ys, rcond=None)[0]
    return -2.0 * float(slope)


def tube(length, girth=4):
    idx = lambda a, b: a * girth + b  # noqa: E731
    n = length * girth
    adj = [[] for _ in range(n)]
    for a in range(length):
        for b in range(girth):
            adj[idx(a, b)] = sorted({idx((a + 1) % length, b),
                                     idx((a - 1) % length, b),
                                     idx(a, (b + 1) % girth),
                                     idx(a, (b - 1) % girth)})
    return adj


def growth_shape(traj):
    tr = [a for a in traj if a > 8]
    if len(tr) < 20:
        return "too-short", float("nan")
    y = np.log(np.array(tr, float))
    t = np.arange(1, len(tr) + 1, dtype=float)

    def fit(x):
        A = np.vstack([x, np.ones_like(x)]).T
        c, *_ = np.linalg.lstsq(A, y, rcond=None)
        res = y - A @ c
        sst = ((y - y.mean()) ** 2).sum()
        return (1 - res @ res / sst if sst > 0 else 0), c[0]

    r2p, ep = fit(np.log(t))
    r2e, _ = fit(t)
    return ("poly-t" if r2p > r2e else "exp-t"), float(ep)


def main():
    print("=== R2: size-matched anchors (N ~ 2000) ===", flush=True)
    anchors = {}
    for name, g in (("torus2d_45", torus2d(45)), ("tube_500x4", tube(500)),
                    ("torus3d_13", torus3d(13))):
        ds = ds_sparse(g)
        f = classify(g, np.random.default_rng(1))
        anchors[name] = ds
        print(f"  {name} (N={len(g)}): d_s={ds:.3f} cls={f['cls']} "
              f"e_hat={f['e_hat']:.3f}", flush=True)

    print("\n=== R1: T5 frozen-state baseline (registered selector) ===",
          flush=True)
    p = dict(q=0.3, p_parents=2, L_cycle=4, W_window=8, decay=True,
             quench_at_alive=2000, q2=0.05, return_graph=True)
    r = grow(p, seed=9, max_births=40000)
    adj = r["final_lcc_adj"]
    ds = ds_sparse(adj)
    f = classify(adj, np.random.default_rng(2))
    print(f"  T5 state (N={len(adj)}): d_s={ds:.3f} cls={f['cls']} "
          f"e_hat={f['e_hat']:.3f} deaths={r['deaths']}")

    print("\n=== R3: growth-shape classifier validation ===", flush=True)
    synth = [max(1, int(0.5 * t * t)) for t in range(1, 200)]
    print(f"  synthetic t^2: {growth_shape(synth)}")
    synth1 = [max(1, int(3 * t)) for t in range(1, 200)]
    print(f"  synthetic t^1: {growth_shape(synth1)}")
    print("  (P1b production: 100/100 exp-t, results_p1_growthshape_console)")

    print("\n=== R4: non-descendant selector under quench (turnover?) ===",
          flush=True)
    p = dict(q=0.3, p_parents=2, L_cycle=4, W_window=8, decay=True,
             nondescendant=True, quench_at_alive=2000, q2=0.05,
             return_graph=True)
    r = grow(p, seed=9, max_births=40000)
    adj = r["final_lcc_adj"]
    if adj and len(adj) > 64:
        ds = ds_sparse(adj)
        f = classify(adj, np.random.default_rng(3))
        print(f"  outcome={r['outcome']} alive={r['final_alive']} "
              f"deaths={r['deaths']} d_s={ds:.3f} cls={f['cls']} "
              f"e_hat={f['e_hat']:.3f}")
    else:
        print(f"  outcome={r['outcome']} alive={r['final_alive']} "
              f"deaths={r['deaths']} (graph too small for d_s)")
    tail = [(c["births"], c["alive"], c["deaths"]) for c in r["checkpoints"]]
    print(f"  checkpoints (births, alive, deaths): {tail}")


if __name__ == "__main__":
    main()
