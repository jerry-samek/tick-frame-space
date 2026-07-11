"""Exp 138 P1b — registered decision-rule evaluation (PREREG_P1b.md + P1b-r1).

Reads results/p1.json; applies the frozen rules verbatim; writes
results/p1_verdict.json.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTROL_MARGIN = 0.02578
E_LO, E_HI = 0.75, 2.25
PLATEAU = 0.15


def run_passes(r):
    """P1b-r1 GEOMETRIC SELECTION per-run test."""
    cps = r["checkpoints"]
    if len(cps) < 5:
        return False, "too-few-checkpoints"
    if cps[-1]["lcc"] < 256:
        return False, "too-small"
    if r["outcome"] == "stationary":
        pass
    elif r["outcome"] == "max-births":
        a = [c["alive"] for c in cps[-3:]]
        if max(a) - min(a) > 0.05 * max(a):
            return False, "not-stationary"
    else:
        return False, r["outcome"]
    if not all(c["cls"] == "poly" for c in cps[-3:]):
        return False, "not-poly-final3"
    e_final = cps[-1]["e_hat"]
    if not (E_LO <= e_final <= E_HI):
        return False, "e-out-of-band"
    es = [c["e_hat"] for c in cps[-5:]]
    if max(es) - min(es) > PLATEAU:
        return False, "no-plateau"
    return True, "PASS"


def cell_key(p):
    return (p["q"], p["p_parents"], p["L_cycle"], p["W_window"])


def nonadjacent(k1, k2):
    return sum(1 for a, b in zip(k1, k2) if a != b) >= 2


def main():
    data = json.load(open(HERE / "results" / "p1.json"))
    runs = data["runs"]
    grid_cells = {}
    controls = {}
    for r in runs:
        p = r["params"]
        if "control" in p:
            controls.setdefault(p["control"], []).append(r)
        else:
            grid_cells.setdefault(cell_key(p), []).append(r)

    verdict = {"cells": {}, "controls": {}, "near_boundary_flags": 0}
    passing_cells = []
    for key, rs in sorted(grid_cells.items()):
        outcomes = {}
        n_pass = 0
        for r in rs:
            ok, why = run_passes(r)
            outcomes[why] = outcomes.get(why, 0) + 1
            if ok:
                n_pass += 1
            for c in r["checkpoints"][-3:]:
                g = c.get("r2_gap")
                if g is not None and g == g and abs(g) < CONTROL_MARGIN:
                    verdict["near_boundary_flags"] += 1
        verdict["cells"][str(key)] = {"outcomes": outcomes, "n_pass": n_pass}
        if n_pass >= 8:
            passing_cells.append(key)
        print(f"  cell q={key[0]} p={key[1]} L={key[2]} W={key[3]}: "
              f"pass={n_pass}/10 {outcomes}")

    ctrl_ok = {}
    for name, expected in (("no_decay", "exp-explosion"),
                           ("any_cycle", "exp-explosion"),
                           ("extinct_side", "extinct")):
        rs = controls.get(name, [])
        n_expected = sum(1 for r in rs if r["outcome"] == expected)
        # invalidity check for (a)/(b): any control run PASSING the geometric
        # criterion invalidates P1b
        n_geom = sum(1 for r in rs if run_passes(r)[0])
        ctrl_ok[name] = {"expected": expected, "n_expected": n_expected,
                         "n_of": len(rs), "n_geometric": n_geom}
        print(f"  control {name}: {n_expected}/{len(rs)} {expected}, "
              f"{n_geom} geometric")
    verdict["controls"] = ctrl_ok

    invalid = (ctrl_ok["no_decay"]["n_geometric"] > 0
               or ctrl_ok["any_cycle"]["n_geometric"] > 0)
    pairs_ok = any(nonadjacent(a, b) for i, a in enumerate(passing_cells)
                   for b in passing_cells[i + 1:])
    if invalid:
        final = "INVALID (a control passed the geometric criterion)"
    elif len(passing_cells) >= 2 and pairs_ok:
        final = "GEOMETRIC SELECTION"
    elif len(passing_cells) == 1 or (len(passing_cells) >= 2 and not pairs_ok):
        final = "KNIFE-EDGE (negative per RAW 134 s12.1)"
    else:
        final = "HONEST NEGATIVE"
    verdict["passing_cells"] = [str(k) for k in passing_cells]
    verdict["FINAL"] = final
    print(f"\nP1b VERDICT: {final}")
    print(f"near-boundary flags (final-3 checkpoints): "
          f"{verdict['near_boundary_flags']}")
    (HERE / "results" / "p1_verdict.json").write_text(
        json.dumps(verdict, indent=2, default=float))


if __name__ == "__main__":
    main()
