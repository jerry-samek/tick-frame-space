"""Exp 138 P1b — skeptic-mandated tests (run BEFORE RESULTS_p1.md).

  T1  selection-engagement census from the existing production JSON:
      deaths/births per cell — was there ever a tug-of-war?
  T2  criticality-line scan: Euler-Lotka predictor (1 = q * sum_{a=1..W}
      lam^-a  <=>  boundary near qW ~ 1) vs measured outcomes on a
      ring-seeded, grace-period scan of q x W. Upgrades the grid negative
      to a rule-family statement if outcomes track the line with no
      stationary band.
  T3  non-descendant-younger selector variant on the two corner cells that
      showed any deaths: does selection engagement rise from ~0?
  T5  mature-population quench: grow at q=0.3 to 2000 alive, quench to
      q=0.05 — does selection dismantle a mature structure (extinction/
      shrinkage) or freeze? ("Selection wins" was never observed away from
      the trivial seed phase.)
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from p1_growth import grow  # noqa: E402


def t1():
    print("=== T1: selection-engagement census (production JSON) ===",
          flush=True)
    data = json.load(open(HERE / "results" / "p1.json"))
    cells = {}
    for r in data["runs"]:
        p = r["params"]
        key = p.get("control") or (f"q{p['q']}p{p['p_parents']}"
                                   f"L{p['L_cycle']}W{p['W_window']}")
        c = cells.setdefault(key, {"births": 0, "deaths": 0})
        c["births"] += r["n_born"]
        c["deaths"] += r["deaths"]
    tot_b = tot_d = 0
    for key, c in sorted(cells.items()):
        rate = c["deaths"] / max(c["births"], 1)
        if "q" in key or "control" not in key:
            tot_b += c["births"]
            tot_d += c["deaths"]
        print(f"  {key}: deaths/births = {c['deaths']}/{c['births']} "
              f"({100*rate:.3f}%)")
    print(f"  TOTAL: {tot_d}/{tot_b} ({100*tot_d/max(tot_b,1):.4f}%)")
    return cells


def t2():
    print("\n=== T2: criticality-line scan (ring seed 8, grace W+2) ===",
          flush=True)
    rows = []
    for W in (2, 4, 8, 16):
        for q in (0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.45, 0.6):
            # Euler-Lotka: growth lam solves 1 = q * sum_{a=1..W} lam^-a;
            # supercritical iff q*W > 1
            pred = "explode" if q * W > 1 else "die"
            p = dict(q=q, p_parents=2, L_cycle=4, W_window=W, decay=True,
                     seed_ring=8, grace=W + 2)
            r = grow(p, seed=42, max_births=15000)
            stat = "stationary" if r["outcome"] == "stationary" else \
                ("explode" if r["outcome"] in ("exp-explosion", "max-births")
                 and r["final_alive"] > 5000 else
                 "die" if r["final_alive"] < 20 else r["outcome"])
            rows.append({"q": q, "W": W, "qW": q * W, "pred": pred,
                         "measured": stat, "alive": r["final_alive"],
                         "deaths": r["deaths"]})
            print(f"  q={q} W={W} qW={q*W:.1f}: predicted={pred} "
                  f"measured={stat} (alive={r['final_alive']} "
                  f"deaths={r['deaths']})", flush=True)
    agree = sum(1 for r in rows if r["pred"] == r["measured"])
    n_stat = sum(1 for r in rows if r["measured"] == "stationary")
    print(f"  Euler-Lotka agreement: {agree}/{len(rows)}; "
          f"stationary cells found: {n_stat}")
    return rows


def t3():
    print("\n=== T3: non-descendant-younger selector (corner cells) ===",
          flush=True)
    out = []
    for L, W in ((4, 8), (4, 16)):
        for variant, nd in (("registered", False), ("nondescendant", True)):
            p = dict(q=0.3, p_parents=2, L_cycle=L, W_window=W, decay=True,
                     nondescendant=nd)
            r = grow(p, seed=7, max_births=15000)
            rate = r["deaths"] / max(r["n_born"], 1)
            out.append({"L": L, "W": W, "variant": variant,
                        "deaths": r["deaths"], "births": r["n_born"],
                        "rate": rate, "outcome": r["outcome"]})
            print(f"  L={L} W={W} {variant}: deaths={r['deaths']}/"
                  f"{r['n_born']} ({100*rate:.2f}%) -> {r['outcome']}",
                  flush=True)
    return out


def t5():
    print("\n=== T5: mature-population quench (q 0.3 -> 0.05 at 2000 alive) "
          "===", flush=True)
    p = dict(q=0.3, p_parents=2, L_cycle=4, W_window=8, decay=True,
             quench_at_alive=2000, q2=0.05)
    r = grow(p, seed=9, max_births=40000)
    traj = r["alive_trajectory"]
    print(f"  outcome={r['outcome']} final_alive={r['final_alive']} "
          f"deaths={r['deaths']} peak_alive={max(traj)}")
    print(f"  alive trajectory (sampled): {traj[:5]} ... {traj[-8:]}")
    return {"outcome": r["outcome"], "final_alive": r["final_alive"],
            "deaths": r["deaths"], "peak": max(traj)}


def main():
    t0 = time.time()
    res = {"T1": t1(), "T5": t5(), "T3": t3(), "T2": t2()}
    res["wall_clock_sec"] = round(time.time() - t0, 1)
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p1_skeptic_tests.json").write_text(
        json.dumps(res, indent=2, default=float))
    print(f"\nwall clock: {res['wall_clock_sec']}s")


if __name__ == "__main__":
    main()
