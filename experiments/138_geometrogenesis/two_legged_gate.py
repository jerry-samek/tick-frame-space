"""Manifold gate for P1d (RAW 136 A.8; PREREG_P1d prerequisite).

A.8 killed the solo LOCAL observable (girth-Qg false-positives small-world). The
P1d channel build (159611c) then killed the TWO-legged gate too: it false-positives
on the substrate's OWN native output -- the directed-growth engine makes a degree-
HETEROGENEOUS hub graph (mean deg ~4, max ~34, 40% deg<=2), yet Qg>0 is manufactured
by the re-convergence SELECTOR and D is low, so (Qg,D) alone says MANIFOLD. So the
gate gets a THIRD leg and the bare-growth graph as an explicit held-out null.

  local leg   Qg  -- girth re-convergence density. Manifold high; tree/expander ~0.
  global leg  D   -- lag-rank (RAW 137). Low-d manifold low; expander high; small-world elevated.
  regularity  cv  -- degree coefficient of variation std(deg)/mean(deg). A manifold
                     is locally Euclidean => bounded UNIFORM degree => cv~0. A hub /
                     scale-free / growth graph has cv >> 0. (Inside-out: an element
                     compares its own degree with its neighbours'.) Rejects the
                     growth-null that Qg,D miss. THRESHOLD is a fixed principled value
                     (lattices are degree-regular), NOT tuned to the null; the null is
                     held out.

  [reported only] l = mean-path/log(N): CONFOUNDS dimension with crumpling; not used.

MANIFOLD iff  Qg >= Qg_lo  AND  D <= D_lo  AND  cv <= cv_hi.
Thresholds Qg_lo, D_lo FROZEN from the calibration triple {torus2d, tree,
random_regular} only; cv_hi = 0.60 fixed (principled). GATE PASSES iff held-out
tests classify right: low-d manifolds {torus3d, honeycomb} -> MANIFOLD;
small_world p=0.1 -> NON (global leg); GROWTH-NULL -> NON (regularity leg).

Honesty limit: 'validated against this zoo' never means 'proven sufficient'. Each
new substrate output is a new null until shown otherwise (the standing §12.6 wall).
"""

import math
import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import torus2d, torus3d, random_regular, binary_tree  # noqa: E402
from boundary_layer_dim import honeycomb, hypercube, small_world, perceived_dim  # noqa: E402
from plaquette_closure_probe import plaquette_Q, torus2d_plus_chords  # noqa: E402
from p1_growth import grow  # bare growth+selection = the substrate's native null  # noqa: E402

LOWD_MANIFOLDS = {"torus2d(30)", "torus3d(11)", "honeycomb(24)"}
CV_HI = 0.60  # fixed principled regularity threshold (lattices are degree-regular)


def growth_null(seed=1, max_births=1500):
    """The directed-growth + re-convergence-selection graph WITHOUT dissipation --
    the substrate's own output the gate must not mistake for a manifold."""
    r = grow(dict(q=0.5, p_parents=2, L_cycle=4, W_window=8, decay=True,
                  return_graph=True), seed=seed, max_births=max_births)
    return r["final_lcc_adj"] or [[]]


def path_stretch(adj, rng, n_src=60):
    n = len(adj)
    srcs = rng.choice(n, min(n_src, n), replace=False)
    tot, cnt = 0, 0
    for s in srcs:
        d = {int(s): 0}; q = deque([int(s)])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in d:
                    d[y] = d[x] + 1; q.append(y)
        tot += sum(d.values()); cnt += len(d) - 1
    return tot / max(cnt, 1) / math.log(n)


def legs(name, adj, rng):
    nodes = sorted(int(x) for x in rng.choice(len(adj), min(300, len(adj)), replace=False))
    _, qg, _ = plaquette_Q(adj, nodes, rng)
    D = float(np.median([perceived_dim(adj, seed=s) for s in (1, 2, 3)]))
    deg = np.array([len(a) for a in adj], float)
    cv = float(deg.std() / deg.mean()) if deg.mean() > 0 else float("nan")
    return {"name": name, "n": len(adj), "Qg": qg, "D": D, "cv": cv,
            "l": path_stretch(adj, rng)}


def main():
    rng = np.random.default_rng(0)
    zoo = [
        ("torus2d(30)",     torus2d(30),                 "manifold",    "CAL"),
        ("binary_tree(11)", binary_tree(11),             "tree",        "CAL"),
        ("random_reg d4",   random_regular(1600, 4, rng),"expander",    "CAL"),
        ("small_world p.1", small_world(1600, 6, 0.1, 1),"crumple",     "TEST*"),
        ("GROWTH-NULL",     growth_null(),               "hub/growth",  "TEST*"),
        ("honeycomb(24)",   honeycomb(24),               "manifold",    "TEST"),
        ("torus3d(11)",     torus3d(11),                 "manifold",    "TEST"),
        ("hypercube(10)",   hypercube(10),               "manifold-hiD","TEST"),
        ("torus2d+chords",  torus2d_plus_chords(30, 300, rng), "crumple", "TEST"),
    ]
    rows = [legs(nm, g, rng) | {"truth": t, "role": r} for nm, g, t, r in zoo]

    cal = {r["name"]: r for r in rows if r["role"] == "CAL"}
    m, t, e = cal["torus2d(30)"], cal["binary_tree(11)"], cal["random_reg d4"]
    Qg_lo = math.sqrt(m["Qg"] * max(t["Qg"], e["Qg"]))
    D_lo = 2.0 * m["D"]

    def classify(r):
        if r["Qg"] >= Qg_lo and r["D"] <= D_lo and r["cv"] <= CV_HI:
            return "MANIFOLD"
        # label by the strongest disqualifier
        if r["cv"] > CV_HI:
            return "hub/irregular"
        if r["D"] > D_lo:
            return "expander/crumple"
        return "tree/sparse"

    print("Three-legged manifold gate (PREREG_P1d). Frozen from calibration triple:")
    print(f"  Qg_lo={Qg_lo:.3f}  D_lo={D_lo:.2f}   cv_hi={CV_HI:.2f} (fixed principled)\n")
    print(f"{'graph':<16}{'role':<7}{'truth':<13}{'Qg':>7}{'D':>6}{'cv':>7}   verdict")
    ok = True
    for r in rows:
        v = classify(r)
        expect_manifold = r["name"] in LOWD_MANIFOLDS
        correct = (v == "MANIFOLD") == expect_manifold
        if r["role"].startswith("TEST"):
            ok &= correct
        mark = "" if correct else "  <-- MISCLASSIFIED"
        print(f"{r['name']:<16}{r['role']:<7}{r['truth']:<13}"
              f"{r['Qg']:>7.3f}{r['D']:>6.1f}{r['cv']:>7.2f}   {v}{mark}")

    gn = next(r for r in rows if r["name"] == "GROWTH-NULL")
    sw = next(r for r in rows if r["name"] == "small_world p.1")
    print("\n--- held-out acid tests (thresholds not tuned to these) ---")
    print(f"  GROWTH-NULL     -> {classify(gn):<16} cv={gn['cv']:.2f} (> {CV_HI} => hub, "
          f"caught by REGULARITY leg; Qg={gn['Qg']:.2f} D={gn['D']:.1f} would have passed 2-leg)")
    print(f"  small_world p.1 -> {classify(sw):<16} D={sw['D']:.1f} (> {D_lo:.2f} => global leg)")
    verdict = "PASS -- gate is P1d-ready" if ok else \
        "FAIL -- a held-out graph misclassified"
    print(f"\nGATE VALIDATION: {verdict}")
    print("(PASS => channel output readable with this gate. -- PREREG_P1d. Note: "
          "'validated against this zoo' != 'proven sufficient'; §12.6 stands.)")


if __name__ == "__main__":
    main()
