"""Exp 138 Phase I0b — calibration run and gate G-I0 (PREREG_I0b.md)."""

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import binary_tree, random_regular, torus2d, torus3d  # noqa: E402
from instrument import classify  # noqa: E402


def main():
    out = {"prereg": "PREREG_I0c.md", "controls": {}, "gate": {}}

    print("=== I0c controls ===", flush=True)
    t2 = classify(torus2d(24), np.random.default_rng(1))
    t3 = classify(torus3d(12), np.random.default_rng(2))
    tr = classify(binary_tree(10), np.random.default_rng(3))
    exps = []
    for s in range(10):
        rng = np.random.default_rng(100 + s)
        exps.append(classify(random_regular(1728, 6, rng), rng))
    for name, f in (("torus2d", t2), ("torus3d", t3), ("tree", tr)):
        print(f"  {name}: cls={f['cls']} e_hat={f['e_hat']:.3f} "
              f"rate={f['rate_exp']:.3f} ratio_med={f['ratio_med']:.3f} "
              f"window={f['window']}")
    n_exp = sum(1 for f in exps if f["cls"] == "exp")
    print(f"  expander6 (10 seeds): {n_exp}/10 exp, "
          f"ratio_med={[round(f['ratio_med'], 2) for f in exps[:3]]}..., "
          f"rate={np.mean([f['rate_exp'] for f in exps]):.3f}")
    out["controls"] = {"torus2d": t2, "torus3d": t3, "tree": tr,
                       "expander_seeds": exps}

    g = {}
    g["torus2d_poly"] = t2["cls"] == "poly"
    g["torus3d_poly"] = t3["cls"] == "poly"
    g["tree_exp"] = tr["cls"] == "exp" and tr["rate_exp"] > 0.3
    g["expander_exp"] = (n_exp >= 9
                         and np.mean([f["rate_exp"] for f in exps]) > 0.3)
    # I0c: margins recorded, not thresholded (PREREG_I0c.md)
    all_gaps = [abs(f["r2_poly"] - f["r2_exp"])
                for f in [t2, t3, tr] + exps]
    g["control_margin"] = float(min(all_gaps))
    g["G_I0_PASS"] = all([g["torus2d_poly"], g["torus3d_poly"], g["tree_exp"],
                          g["expander_exp"]])
    if g["G_I0_PASS"]:
        g["band_2d"] = [t2["e_hat"] - 0.25, t2["e_hat"] + 0.25]
        g["band_3d"] = [t3["e_hat"] - 0.25, t3["e_hat"] + 0.25]
    out["gate"] = g

    print("\n=== gate G-I0 ===")
    for k, v in g.items():
        print(f"  {k}: {v}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "i0.json").write_text(json.dumps(out, indent=2,
                                                         default=float))


if __name__ == "__main__":
    main()
