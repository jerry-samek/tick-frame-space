"""Exp 138 P1c — engagement-vs-connectivity tradeoff sweep (PREREG_P1C.md)."""

import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from instrument import classify  # noqa: E402
from p1_growth import grow  # noqa: E402
from p1c_recon import ds_sparse  # noqa: E402

Q2S = (0.05, 0.10, 0.15, 0.20, 0.25)
SELECTORS = (("registered", False), ("nondescendant", True))
N_SEEDS = 8


def _cell(args):
    selname, nd, q2, seed = args
    p = dict(q=0.3, p_parents=2, L_cycle=4, W_window=8, decay=True,
             nondescendant=nd, quench_at_alive=2000, q2=q2,
             return_graph=True)
    r = grow(p, seed=seed, max_births=40000)
    adj = r["final_lcc_adj"] or []
    lcc = len(adj)
    frac = lcc / max(r["final_alive"], 1)
    eng = r["deaths"] / max(r["n_born"], 1)
    if lcc >= 256:
        ds = ds_sparse(adj)
        f = classify(adj, np.random.default_rng(seed))
        cls, ehat = f["cls"], f["e_hat"]
    else:
        ds, cls, ehat = float("nan"), "undefined", float("nan")
    print(f"  {selname} q2={q2} seed={seed}: alive={r['final_alive']} "
          f"LCC={lcc} frac={frac:.2f} eng={100*eng:.1f}% d_s={ds:.2f} "
          f"cls={cls} ({r['outcome']})", flush=True)
    return {"selector": selname, "q2": q2, "seed": seed,
            "outcome": r["outcome"], "alive": r["final_alive"], "lcc": lcc,
            "lcc_frac": frac, "engagement": eng, "d_s": ds, "cls": cls,
            "e_hat": ehat}


def main():
    t0 = time.time()
    cells = [(sn, nd, q2, 3000 + s) for sn, nd in SELECTORS for q2 in Q2S
             for s in range(N_SEEDS)]
    with Pool(16) as pool:
        runs = pool.map(_cell, cells)

    # gate evaluation (PREREG_P1C.md)
    def cellkey(r):
        return (r["selector"], r["q2"])
    cellmap = {}
    for r in runs:
        cellmap.setdefault(cellkey(r), []).append(r)
    passing = []
    partials = []
    cell_stats = {}
    for key, rs in sorted(cellmap.items()):
        n_geo = sum(1 for r in rs if r["lcc_frac"] >= 0.5
                    and r["engagement"] >= 0.05
                    and 1.7 <= r["d_s"] <= 2.3)
        med = lambda k: float(np.median([r[k] for r in rs]))  # noqa: E731
        cell_stats[str(key)] = {"n_geometric": n_geo,
                                "med_lcc_frac": med("lcc_frac"),
                                "med_engagement": med("engagement"),
                                "med_d_s": float(np.nanmedian(
                                    [r["d_s"] for r in rs]))}
        if n_geo >= 6:
            passing.append(key)
        # partial: connected+engaged but not geometric, or connected+geo but disengaged
        conn_eng = sum(1 for r in rs if r["lcc_frac"] >= 0.5
                       and r["engagement"] >= 0.05)
        if conn_eng >= 6 and n_geo < 6:
            partials.append((str(key), "connected+engaged non-geometric"))

    # tradeoff: Spearman(engagement, lcc_frac) across cells (median per cell)
    engs = [cell_stats[str(k)]["med_engagement"] for k in sorted(cellmap)]
    fracs = [cell_stats[str(k)]["med_lcc_frac"] for k in sorted(cellmap)]
    def spearman(x, y):
        rx = np.argsort(np.argsort(x)).astype(float)
        ry = np.argsort(np.argsort(y)).astype(float)
        return float(np.corrcoef(rx, ry)[0, 1])
    rho = spearman(engs, fracs)

    nonadj = lambda a, b: sum(1 for x, y in zip(a, b) if x != y) >= 2  # noqa
    pass_ok = any(nonadj(a, b) for i, a in enumerate(passing)
                  for b in passing[i + 1:])
    if len(passing) >= 2 and pass_ok:
        verdict = "GEOMETRIC-SELECTION"
    elif rho < 0:
        verdict = "TRADEOFF-CONFIRMED (engagement anticorrelated with connectivity)"
    else:
        verdict = "PARTIAL / INCONCLUSIVE"

    out = {"prereg": "PREREG_P1C.md", "runs": runs, "cell_stats": cell_stats,
           "spearman_eng_lccfrac": rho, "passing_cells": [str(k) for k in passing],
           "partials": partials, "verdict": verdict,
           "wall_clock_sec": round(time.time() - t0, 1)}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p1c.json").write_text(json.dumps(out, indent=2,
                                                          default=float))
    print(f"\n=== P1c ===")
    print(f"  Spearman(engagement, LCC-fraction) across cells: {rho:.3f}")
    print(f"  passing cells: {[str(k) for k in passing]}")
    print(f"  VERDICT: {verdict}")
    print(f"  wall clock: {out['wall_clock_sec']}s")


if __name__ == "__main__":
    main()
