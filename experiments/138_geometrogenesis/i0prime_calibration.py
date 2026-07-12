"""Exp 138 P1d I0' — calibration run and gate G-I0' (PREREG_I0prime.md).

Runs the null-safe dimension instrument (dimension_instrument.classify_dimension)
against all signed controls: lattices (must read is_manifold=True), a tree and
random-regular graphs at two degrees (must read is_manifold=False, the P1c null).
Freezes cyc_thresh (geometric mean between lattice-min and random-max cyc_density)
and control_margin (the gap) into results/i0prime.json on PASS.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import binary_tree, random_regular, torus2d, torus3d  # noqa: E402
from dimension_instrument import classify_dimension  # noqa: E402


def run_random_seeds(n, d, n_seeds=10, seed_base=100):
    out = []
    for s in range(n_seeds):
        rng = np.random.default_rng(seed_base + s)
        g = random_regular(n, d, rng)
        out.append(classify_dimension(g, rng))
    return out


def main():
    out = {"prereg": "PREREG_I0prime.md", "controls": {}, "gate": {}}

    print("=== I0' controls ===", flush=True)
    t2 = classify_dimension(torus2d(24), np.random.default_rng(1))
    t3 = classify_dimension(torus3d(12), np.random.default_rng(2))
    tr = classify_dimension(binary_tree(10), np.random.default_rng(3))
    rand4 = run_random_seeds(1728, 4, n_seeds=10, seed_base=100)
    rand6 = run_random_seeds(1728, 6, n_seeds=10, seed_base=200)

    def fmt(name, r):
        print(f"  {name}: shell_cls={r['shell_cls']} d_shell={r['d_shell']:.3f} "
              f"d_spectral={r['d_spectral']:.3f} cyc_density={r['cyc_density']:.4f} "
              f"is_manifold={r['is_manifold']}")

    fmt("torus2d", t2)
    fmt("torus3d", t3)
    fmt("tree", tr)
    n4_notmanifold = sum(1 for r in rand4 if not r["is_manifold"])
    n6_notmanifold = sum(1 for r in rand6 if not r["is_manifold"])
    print(f"  random4 (10 seeds): {n4_notmanifold}/10 is_manifold=False, "
          f"cyc_density range=[{min(r['cyc_density'] for r in rand4):.4f}, "
          f"{max(r['cyc_density'] for r in rand4):.4f}]")
    print(f"  random6 (10 seeds): {n6_notmanifold}/10 is_manifold=False, "
          f"cyc_density range=[{min(r['cyc_density'] for r in rand6):.4f}, "
          f"{max(r['cyc_density'] for r in rand6):.4f}]")

    out["controls"] = {
        "torus2d": t2, "torus3d": t3, "tree": tr,
        "random4_seeds": rand4, "random6_seeds": rand6,
    }

    g = {}
    g["torus2d_manifold"] = t2["is_manifold"] is True
    g["torus3d_manifold"] = t3["is_manifold"] is True
    g["tree_not_manifold"] = tr["is_manifold"] is False
    g["random4_null"] = n4_notmanifold >= 9
    g["random6_null"] = n6_notmanifold >= 9
    g["G_I0PRIME_PASS"] = all([
        g["torus2d_manifold"], g["torus3d_manifold"], g["tree_not_manifold"],
        g["random4_null"], g["random6_null"],
    ])

    # Diagnostic: did the tree fail on shell_cls, cyc_density, or both?
    g["tree_shell_cls"] = tr["shell_cls"]
    g["tree_cyc_density"] = tr["cyc_density"]

    lattice_cyc = [t2["cyc_density"], t3["cyc_density"]]
    random_cyc = [r["cyc_density"] for r in rand4 + rand6]
    min_lattice_cyc = float(min(lattice_cyc))
    max_random_cyc = float(max(random_cyc))
    g["min_lattice_cyc_density"] = min_lattice_cyc
    g["max_random_cyc_density"] = max_random_cyc

    if g["G_I0PRIME_PASS"]:
        cyc_thresh = math.sqrt(min_lattice_cyc * max_random_cyc)
        control_margin = min_lattice_cyc - max_random_cyc
        g["cyc_thresh"] = cyc_thresh
        g["control_margin"] = control_margin
    else:
        g["cyc_thresh"] = None
        g["control_margin"] = None

    out["gate"] = g

    print("\n=== gate G-I0' ===")
    for k, v in g.items():
        print(f"  {k}: {v}")

    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "i0prime.json").write_text(
        json.dumps(out, indent=2, default=float))
    print(f"\nG-I0' PASS: {g['G_I0PRIME_PASS']}")


if __name__ == "__main__":
    main()
