"""Two-legged re-convergence gate (RAW 136 A.8; PREREG_P1d prerequisite).

A.8 killed the solo local observable: girth-Qg false-positives small-world (Qg =
honeycomb) because it is blind to global shortcuts. The gate therefore needs a
SECOND, GLOBAL leg. This builds and VALIDATES it before the P1d channel is read.

  local leg   Qg  -- girth-aware re-convergence density (plaquette_closure_probe).
              manifold high; tree & expander ~0.
  global leg  D   -- lag-correlation rank (RAW 137 `perceived_dim`). THE PRE-
              REGISTERED global leg (PREREG_P1d). Low-d manifold low (~1-2);
              expander high (~10); small-world ELEVATED (~3.5, A.8). This is what
              separates a clean low-d manifold from a small-world crumple.

  [note] path-stretch l = mean-path/log(N) is reported for interpretation only. It
  CONFOUNDS dimension with crumpling (a high-d manifold has intrinsically short
  paths, so torus3d/hypercube read low l like an expander). It is NOT used to
  classify -- a first build that used it as the primary leg misclassified torus3d
  and hypercube; reverting to the pre-registered D leg fixes it. (Kept as a live
  reminder of why the pre-registration is D, not l.)

Joint classifier (thresholds FROZEN from the calibration triple {torus2d,
binary_tree, random_regular d=4} ONLY):
  MANIFOLD (low-d) iff  Qg >= Qg_lo  AND  D <= D_lo,
    Qg_lo = geomean(torus2d Qg, max(tree,expander) Qg)   [local separation]
    D_lo  = 2.0 * torus2d D                              [global, from the clean manifold]
  - tree:        Qg ~0                    -> rejected (local leg)
  - expander:    Qg ~0, D high            -> rejected (both)
  - small-world: Qg high, D elevated>D_lo -> rejected by GLOBAL leg  <-- A.8 acid test
  - hypercube:   Qg high but D>D_lo (10-d, not the low-d target) -> correctly non-(low-d)-manifold

Scope: the P1d target is a finite LOW-d (2-4) manifold, so the gate's job is
low-d-manifold vs {tree, expander, crumple, high-d}. GATE PASSES iff, under the
frozen thresholds, the held-out low-d manifolds {torus3d, honeycomb} read
MANIFOLD and small_world p=0.1 reads NON-manifold (decisive).
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

LOWD_MANIFOLDS = {"torus2d(30)", "torus3d(11)", "honeycomb(24)"}


def path_stretch(adj, rng, n_src=60):
    """l = mean shortest-path length / log(N) -- reported only (dimension-confounded)."""
    n = len(adj)
    srcs = rng.choice(n, min(n_src, n), replace=False)
    tot, cnt = 0, 0
    for s in srcs:
        d = {int(s): 0}
        q = deque([int(s)])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in d:
                    d[y] = d[x] + 1
                    q.append(y)
        tot += sum(d.values())
        cnt += len(d) - 1
    return tot / max(cnt, 1) / math.log(n)


def legs(name, adj, rng):
    nodes = sorted(int(x) for x in rng.choice(len(adj), min(300, len(adj)), replace=False))
    _, qg, _ = plaquette_Q(adj, nodes, rng)
    ds = [perceived_dim(adj, seed=s) for s in (1, 2, 3)]
    return {"name": name, "n": len(adj), "Qg": qg,
            "D": float(np.median(ds)), "D_seeds": [round(x, 1) for x in ds],
            "l": path_stretch(adj, rng)}


def main():
    rng = np.random.default_rng(0)
    zoo = [
        ("torus2d(30)",     torus2d(30),                 "manifold",    "CAL"),
        ("binary_tree(11)", binary_tree(11),             "tree",        "CAL"),
        ("random_reg d4",   random_regular(1600, 4, rng),"expander",    "CAL"),
        ("small_world p.1", small_world(1600, 6, 0.1, 1),"crumple",     "TEST*"),
        ("honeycomb(24)",   honeycomb(24),               "manifold",    "TEST"),
        ("torus3d(11)",     torus3d(11),                 "manifold",    "TEST"),
        ("hypercube(10)",   hypercube(10),               "manifold-hiD","TEST"),
        ("torus2d+chords",  torus2d_plus_chords(30, 300, rng), "crumple", "TEST"),
    ]
    rows = [legs(nm, g, rng) | {"truth": t, "role": r} for nm, g, t, r in zoo]

    cal = {r["name"]: r for r in rows if r["role"] == "CAL"}
    man, tree, exp = cal["torus2d(30)"], cal["binary_tree(11)"], cal["random_reg d4"]
    Qg_lo = math.sqrt(man["Qg"] * max(tree["Qg"], exp["Qg"]))
    D_lo = 2.0 * man["D"]

    def classify(r):
        if r["Qg"] >= Qg_lo and r["D"] <= D_lo:
            return "MANIFOLD"
        if r["Qg"] < Qg_lo and r["D"] <= D_lo:
            return "tree/sparse"
        return "expander/crumple"

    print("Two-legged gate (PREREG_P1d prerequisite). Global leg = D (lag-rank),")
    print(f"as pre-registered. Thresholds FROZEN from the calibration triple only:")
    print(f"  Qg_lo = {Qg_lo:.3f}   D_lo = {D_lo:.2f}   (l shown for interpretation only)\n")
    print(f"{'graph':<17}{'role':<7}{'truth':<13}{'Qg':>7}{'D':>6}{'l':>6}   verdict")
    ok = True
    for r in rows:
        v = classify(r)
        expect_manifold = r["name"] in LOWD_MANIFOLDS
        correct = (v == "MANIFOLD") == expect_manifold
        if r["role"].startswith("TEST"):
            ok &= correct
        mark = "" if correct else "  <-- MISCLASSIFIED"
        print(f"{r['name']:<17}{r['role']:<7}{r['truth']:<13}"
              f"{r['Qg']:>7.3f}{r['D']:>6.1f}{r['l']:>6.2f}   {v}{mark}")

    sw = next(r for r in rows if r["name"] == "small_world p.1")
    hc = next(r for r in rows if r["name"] == "honeycomb(24)")
    t3 = next(r for r in rows if r["name"] == "torus3d(11)")
    print("\n--- acid tests (held out; thresholds not tuned to them) ---")
    print(f"  small_world p=0.1 -> {classify(sw):<16} Qg={sw['Qg']:.2f} (manifold-like) "
          f"D={sw['D']:.1f} > D_lo={D_lo:.2f}  -> caught by GLOBAL leg. seeds D={sw['D_seeds']}")
    print(f"  honeycomb(24)     -> {classify(hc):<16} Qg={hc['Qg']:.2f} D={hc['D']:.1f} (6-cyc manifold)")
    print(f"  torus3d(11)       -> {classify(t3):<16} Qg={t3['Qg']:.2f} D={t3['D']:.1f} "
          f"(low-d manifold must pass). margin to small-world on D: "
          f"{sw['D']:.1f} vs {t3['D']:.1f}")
    verdict = "PASS -- gate is P1d-ready" if ok else \
        "FAIL -- gate NOT P1d-ready (a held-out graph misclassified)"
    print(f"\nGATE VALIDATION: {verdict}")
    print("(PASS => the P1d channel output can be read with this gate. FAIL => the")
    print(" channel is not interpretable; do not run/trust it. -- PREREG_P1d)")


if __name__ == "__main__":
    main()
