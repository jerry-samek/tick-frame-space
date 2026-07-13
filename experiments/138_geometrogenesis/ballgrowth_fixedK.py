"""Fixture-independent local ball-growth dimension reader (v2).

Rebuilds the dimension reader after a skeptic REFUTED `local_ballgrowth.py`:
its tree-rejection was a knife-edge overfit (R_max=12 = the tree fixture's depth+1)
and at that window the cone covered 70-80% of the graph (semi-global, not local).

Fixes:
  1. FIXTURE-INDEPENDENT, LOCAL window: each observer grows its ball to a fixed
     ABSOLUTE node count K (not a fixed radius, not a fixed graph fraction). Same
     local neighbourhood size for every graph regardless of N or depth; coverage
     is reported to prove it stays local (K << N).
  2. HONEST SCOPE: the skeptic's structural point stands -- ball-growth is BLIND to
     cycles, so it cannot reject a tree while local (a tree's local ball looks
     polynomial from a leaf). This reader is therefore a DIMENSION + EXPANDER reader
     ONLY; TREE-REJECTION IS DELEGATED TO Qg (girth re-convergence, which reads
     tree=0 and is already the gate's local leg). Both are printed so the delegation
     is explicit and checkable.
  3. Fit the growth slope over r >= R_FIT_MIN (skip the discretized r=1 shell).
  4. Report the field-of-frames DISTRIBUTION, and validate STABILITY across K
     (not a knife-edge) against a HARDER null zoo: a DEEPER tree and a same-N
     (~2300, matching the P1d graphs) random-4-regular.

An observer classifies EXP (expander) if its cumulative ball fits log B vs r better
than log B vs log r. frac_exp>0 flags locally-expander structure. Dimension is the
poly slope (honest ceiling: saturates above ~d4 in finite local windows; the P1d
question is d in 1..3, which it must resolve).
"""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import torus2d, torus3d, random_regular, binary_tree  # noqa: E402
from boundary_layer_dim import honeycomb, hypercube, small_world  # noqa: E402
from plaquette_closure_probe import plaquette_Q, torus2d_plus_chords  # noqa: E402

R_FIT_MIN = 2      # skip the r=1 discretized shell
R_HARD = 60        # safety cap on BFS depth


def _ball_to_K(adj, obs, K):
    """Cumulative ball B(r) from obs, grown until it holds >= K nodes (or graph
    exhausted). Returns (rs, B, coverage_fraction)."""
    seen = {obs}; frontier = [obs]; B = []
    for _ in range(R_HARD):
        nxt = []
        for v in frontier:
            for u in adj[v]:
                if u not in seen:
                    seen.add(u); nxt.append(u)
        if not nxt:
            break
        B.append(len(seen) - 1)
        frontier = nxt
        if len(seen) >= K:
            break
    return (np.arange(1, len(B) + 1, dtype=float), np.array(B, float),
            len(seen) / len(adj))


def _fit(rs, B):
    """poly (log B ~ log r, slope=d) vs exp (log B ~ r); classify by R^2 over the
    window r >= R_FIT_MIN (fall back to all shells if too few). Returns (cls,d)."""
    mask = rs >= R_FIT_MIN
    if mask.sum() < 3:
        mask = np.ones_like(rs, bool)
    if mask.sum() < 3:
        return None
    x, y = rs[mask], np.log(np.clip(B[mask], 1e-9, None))

    def lsq(xx):
        A = np.vstack([xx, np.ones_like(xx)]).T
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        resid = y - A @ coef
        ss = float(np.sum((y - y.mean()) ** 2))
        return float(coef[0]), (1 - float(np.sum(resid ** 2)) / ss if ss > 0 else 0.0)

    d, r2p = lsq(np.log(x))
    _, r2e = lsq(x)
    return ("exp" if r2e > r2p else "poly"), d


def ballgrowth_dim(adj, K=200, n_obs=150, seed=0):
    rng = np.random.default_rng(seed)
    obs = rng.choice(len(adj), min(n_obs, len(adj)), replace=False)
    ds, exp_flags, covs = [], [], []
    for o in obs:
        rs, B, cov = _ball_to_K(adj, int(o), K)
        r = _fit(rs, B)
        if r is None:
            continue
        cls, d = r
        exp_flags.append(cls == "exp"); covs.append(cov)
        if cls == "poly":
            ds.append(d)
    if not exp_flags:
        return {"frac_exp": float("nan"), "d_med": float("nan"),
                "cov": float("nan"), "n": 0}
    ds = np.array(ds) if ds else np.array([np.nan])
    return {"frac_exp": float(np.mean(exp_flags)), "d_med": float(np.median(ds)),
            "d_iqr": float(np.subtract(*np.percentile(ds, [75, 25]))) if len(ds) > 1 else 0.0,
            "cov": float(np.median(covs)), "n": len(exp_flags)}


def _qg(adj, seed=1):
    rng = np.random.default_rng(seed)
    nodes = sorted(int(x) for x in rng.choice(len(adj), min(300, len(adj)), replace=False))
    return plaquette_Q(adj, nodes, rng)[1]


def main():
    rng = np.random.default_rng(0)
    print("Fixture-independent local ball-growth dimension reader (v2).")
    print("Dimension + EXPANDER only; TREE-rejection DELEGATED to Qg (shown). "
          "Stability checked across K.\n")
    zoo = [
        ("torus2d(40)",     torus2d(40),                  "manifold d2"),
        ("torus3d(12)",     torus3d(12),                  "manifold d3"),
        ("honeycomb(28)",   honeycomb(28),                "manifold d2"),
        ("hypercube(11)",   hypercube(11),                "manifold hi-d"),
        ("tree depth11",    binary_tree(11),              "TREE (Qg's job)"),
        ("tree depth14",    binary_tree(14),              "TREE deeper (Qg's job)"),
        ("random_reg N2300",random_regular(2300, 4, rng), "EXPANDER"),
        ("small_world",     small_world(2300, 6, 0.1, 1), "EXPANDER"),
        ("torus2d+chords",  torus2d_plus_chords(40, 500, rng), "crumple"),
    ]
    Ks = [100, 200, 400]
    print(f"{'graph':<19}{'expected':<18}" + "".join(f"K{K:<11}" for K in Ks) + "  Qg")
    print(f"{'':<37}" + "".join(f"{'d(fexp,cov)':<12}" for _ in Ks))
    for name, g, exp in zoo:
        cells = []
        for K in Ks:
            r = ballgrowth_dim(g, K=K, seed=1)
            cells.append(f"{r['d_med']:.1f}({r['frac_exp']:.2f},{r['cov']:.0%})")
        qg = _qg(g)
        print(f"{name:<19}{exp:<18}" + "".join(f"{c:<12}" for c in cells) + f"  {qg:.2f}")

    print("\nVALIDATION CRITERIA (this reader's honest scope):")
    print("  DIMENSION: manifolds read poly d rising with true d (torus2d<torus3d),")
    print("    STABLE across K (not a knife-edge). Ceiling above ~d4 accepted.")
    print("  EXPANDER: random/small-world read high frac_exp across K.")
    print("  TREE: delegated -- ball-growth may read the tree as poly (its blind")
    print("    spot), but Qg~0 for both trees vs Qg>0 for manifolds catches it.")

    print("\n--- APPLY to the P1d cells (gate already certified non-tree via Qg, "
          "non-hub via cv); read dimension + heterogeneity ---")
    from p1d_channel import grow_dissipative, BASE
    for tag, q, c in [("manifold q0.20", 0.20, 1.0), ("mid q0.30", 0.30, 1.0),
                      ("hub q0.50", 0.50, 1.0)]:
        rows = []
        for sd in (1, 2, 3):
            g = grow_dissipative(dict(BASE, mode="scalar_flux", q=q, c=c), sd, 3000)
            adj = g["lcc_adj"]
            if len(adj) < 200:
                continue
            r = ballgrowth_dim(adj, K=200, seed=7)
            rows.append((r["d_med"], r["frac_exp"], r["cov"], len(adj), _qg(adj)))
        if rows:
            d = np.mean([x[0] for x in rows]); fe = np.mean([x[1] for x in rows])
            cov = np.mean([x[2] for x in rows]); qg = np.mean([x[4] for x in rows])
            print(f"  {tag:<14}: d~{d:.1f}  frac_exp~{fe:.2f}  cov~{cov:.0%}  "
                  f"Qg~{qg:.2f}  (n_survivors={len(rows)})")
    print("  -> read the P1d dimension HONESTLY: stable-across-K poly d, the "
          "heterogeneity frac_exp, and Qg (non-tree). Ceiling & any residual "
          "window-sensitivity reported, not hidden.")


if __name__ == "__main__":
    main()
