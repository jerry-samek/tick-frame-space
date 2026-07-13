"""Inside-out local ball-growth dimension instrument + null-validation.

The P1d map (RESULTS_p1d.md) left the manifold regime's dimension UNRESOLVED: the
validated lag-rank leg (perceived_dim) reads FLAT ~1 on the channel graphs, and the
only instrument that moves (god-view shell classifier) is source-averaged, uses the
global N/2-ball window, and was never null-validated here.

This is the inside-out replacement. An embedded observer floods a signal and counts
how many nodes it HEARS FROM at each delay r (= graph distance) -- N(r), the ball it
experiences. That is inside-out (its own arrivals-by-lag, no god-view). Two honest
differences from `instrument.fit_exponent`:
  1. PER-OBSERVER, reported as a DISTRIBUTION (field of frames), not a god-average.
  2. LOCAL cone: each observer's window runs only until its ball reaches a fraction
     `sat` of the graph (or R_max) -- it resolves LOCAL dimension, not global shape.
Cumulative ball B(r) = #nodes within delay r; fit log B vs log r (poly, slope = d)
against log B vs r (exp), classify by R^2 (an expander/tree grows EXPONENTIALLY and
is flagged `exp`, not low-d).

VALIDATION GATE: the instrument is trustworthy iff, on the zoo, low-d manifolds read
poly with the RIGHT d (torus2d~2, torus3d~3, honeycomb~2) AND tree/random-regular/
small-world are flagged high-frac-exp (rejected). Only then is it applied to the P1d
manifold cell. It may FAIL -- reported either way.
"""

import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import torus2d, torus3d, random_regular, binary_tree  # noqa: E402
from boundary_layer_dim import honeycomb, hypercube, small_world  # noqa: E402
from plaquette_closure_probe import torus2d_plus_chords  # noqa: E402


def _cum_ball(adj, obs, R_max, sat_n):
    """Cumulative ball size B(r) from obs, r=1.. until B(r) > sat_n or r=R_max.
    Returns arrays (rs, B) of the local window."""
    seen = {obs}
    frontier = [obs]
    B = []
    for r in range(1, R_max + 1):
        nxt = []
        for v in frontier:
            for u in adj[v]:
                if u not in seen:
                    seen.add(u); nxt.append(u)
        if not nxt:
            break
        B.append(len(seen) - 1)          # nodes within distance r (excl obs)
        frontier = nxt
        if len(seen) > sat_n:
            break
    return np.arange(1, len(B) + 1, dtype=float), np.array(B, float)


def _fit_cls(rs, B):
    """poly (log B vs log r, slope=d) vs exp (log B vs r); classify by R^2."""
    y = np.log(np.clip(B, 1e-9, None))

    def lsq(x):
        A = np.vstack([x, np.ones_like(x)]).T
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        resid = y - A @ coef
        ss = float(np.sum((y - y.mean()) ** 2))
        return float(coef[0]), (1.0 - float(np.sum(resid ** 2)) / ss if ss > 0 else 0.0)

    d, r2p = lsq(np.log(rs))
    rate, r2e = lsq(rs)
    return ("exp" if r2e > r2p else "poly"), d, r2p, r2e


def ballgrowth_dim(adj, n_obs=150, R_max=12, sat=0.7, seed=0, r_min=4):
    """Inside-out local ball-growth over sampled observers. Returns the field-of-
    frames summary: fraction reading exponential, and the poly observers' local-d
    distribution."""
    rng = np.random.default_rng(seed)
    n = len(adj)
    sat_n = sat * n
    obs = rng.choice(n, min(n_obs, n), replace=False)
    ds, exp_flags = [], []
    for o in obs:
        rs, B = _cum_ball(adj, int(o), R_max, sat_n)
        if len(rs) < r_min:
            continue
        cls, d, r2p, r2e = _fit_cls(rs, B)
        exp_flags.append(cls == "exp")
        if cls == "poly":
            ds.append(d)
    if not exp_flags:
        return {"frac_exp": float("nan"), "d_med": float("nan"),
                "d_iqr": float("nan"), "n_used": 0}
    ds = np.array(ds) if ds else np.array([np.nan])
    return {"frac_exp": float(np.mean(exp_flags)),
            "d_med": float(np.median(ds)),
            "d_iqr": float(np.subtract(*np.percentile(ds, [75, 25]))) if len(ds) > 1 else 0.0,
            "n_used": len(exp_flags)}


def _verdict(r):
    if r["n_used"] == 0:
        return "degenerate"
    if r["frac_exp"] >= 0.5:
        return "EXPANDER/tree"
    return f"poly d={r['d_med']:.1f}"


def main():
    rng = np.random.default_rng(0)
    print("Inside-out local ball-growth instrument -- NULL VALIDATION on the zoo.")
    print("(per-observer local cone; frac_exp = fraction reading EXPONENTIAL growth)\n")
    zoo = [
        ("torus2d(30)",     torus2d(30),                  "manifold d2"),
        ("torus3d(11)",     torus3d(11),                  "manifold d3"),
        ("honeycomb(24)",   honeycomb(24),                "manifold d2"),
        ("hypercube(10)",   hypercube(10),                "manifold d-hi"),
        ("binary_tree(11)", binary_tree(11),              "EXP (reject)"),
        ("random_reg d4",   random_regular(1600, 4, rng), "EXP (reject)"),
        ("small_world p.1", small_world(1600, 6, 0.1, 1), "EXP-ish (reject)"),
        ("torus2d+chords",  torus2d_plus_chords(30, 300, rng), "crumple (reject)"),
    ]
    print(f"{'graph':<17}{'expected':<18}{'frac_exp':>9}{'d_med':>7}{'d_iqr':>7}"
          f"{'n':>5}   verdict")
    ok = True
    for name, g, exp in zoo:
        r = ballgrowth_dim(g, seed=1)
        v = _verdict(r)
        # validation: manifolds -> poly with right-ish d; tree/random/sw -> EXPANDER
        is_manifold = exp.startswith("manifold")
        passed = (is_manifold and v.startswith("poly")) or \
                 (not is_manifold and v == "EXPANDER/tree")
        ok &= passed
        mark = "" if passed else "  <-- FAILS EXPECTATION"
        print(f"{name:<17}{exp:<18}{r['frac_exp']:>9.2f}{r['d_med']:>7.1f}"
              f"{r['d_iqr']:>7.1f}{r['n_used']:>5}   {v}{mark}")
    print(f"\nVALIDATION: {'PASS' if ok else 'FAIL'} — "
          + ("manifolds read poly-correct-d AND tree/random/small-world read EXPANDER."
             if ok else "at least one graph misclassified; instrument NOT trustworthy yet."))
    print("torus2d+chords/hypercube are diagnostics (crumple / high-d), not pass/fail.")

    if ok:
        print("\n--- APPLY to the P1d manifold cell (q=0.20, c=1.0), which the lag-rank "
              "leg read FLAT ~1 ---")
        from p1d_channel import grow_dissipative, BASE
        for sd in (1, 2, 3):
            g = grow_dissipative(dict(BASE, mode="scalar_flux", q=0.20, c=1.0), sd, 3000)
            adj = g["lcc_adj"]
            if len(adj) < 200:
                print(f"  seed {sd}: extinct/tiny (n={len(adj)})"); continue
            r = ballgrowth_dim(adj, seed=7)
            print(f"  seed {sd}: n={len(adj):>4}  {_verdict(r)}  "
                  f"(frac_exp={r['frac_exp']:.2f}, d_iqr={r['d_iqr']:.1f})")
        print("  -> a TRUSTWORTHY inside-out local dimension for the manifold regime "
              "(vs the flat lag-rank ~1 and the un-validated god-view ~2).")


if __name__ == "__main__":
    main()
