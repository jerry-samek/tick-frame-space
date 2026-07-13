"""Exp 137 Test 3 — skeptic-mandated distinguishing tests (run BEFORE RESULTS).

  F1  non-survivor census sweep (selection baseline): RG/pos for ALL K=8 and
      K=10 cycle classes, survivors and non-survivors. Do survivors sit LOWER
      than non-survivors at fixed K — or does the whole class cluster low?
  F2  pos ceiling (adversarial fixture): the max-pos class per K. If the
      ceiling < 0.5, T3-A's EXPAND branch was unreachable by construction.
  F3  dead-pattern M baseline: R2-style divergence readout (evolved reference;
      god-view for aperiodic — diagnostic only) on non-surviving K=8 classes.
      If their dpr_sub resembles the survivors' (~4.4/4.8), the readout reads
      "graph structure of whatever corpse you kick".
  F4  LAT anchor locality: is the radius-6 ball on the 12^3 torus effectively
      the whole graph (LAT ~ EXP suggests so)? Re-anchor at radius 3.
  F5  RG sensitivity: does the FLAT_K6 vs FLAT_K8 RG ordering (delta=0.029,
      which produced T3-B's rank swap) survive lam/W variation?
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "134_pattern_coherence"))
sys.path.insert(0, str(HERE))

from fixtures import F2_K6_PERIMETER, F3_K8_RING                 # noqa: E402
from multipattern import tick_multi                              # noqa: E402
from phase1_t6 import graph_impulse_corr, observables, ring_window  # noqa: E402
from phase1_t6_embed import sustains                             # noqa: E402
from phase1b_skeptic_tests import (                               # noqa: E402
    chord_count, enum_cycles, planarity_rank, ring_graph)
from graphs import bfs_distances, sample_bundle, torus3d         # noqa: E402
from rule import bootstrap                                       # noqa: E402

ANCH = json.load(open(HERE / "results" / "test3.json"))["anchors"]


def pos_of(rg, K):
    a = ANCH[str(K)]
    return (rg - a["CK"]) / (a["LAT_mean"] - a["CK"])


def f1_f2():
    print("=== F1/F2: full-census RG sweep (survivors vs non-survivors) ===",
          flush=True)
    out = {}
    for K in (8, 10):
        rows = []
        for cyc in enum_cycles(K):
            ok, _ = sustains(cyc)
            rg = graph_impulse_corr(ring_graph(cyc), list(range(K)))["dpr_sub"]
            rows.append({"survives": bool(ok), "chords": chord_count(cyc),
                         "rank": planarity_rank(cyc), "RG": rg,
                         "pos": pos_of(rg, K)})
        surv = [r for r in rows if r["survives"]]
        non = [r for r in rows if not r["survives"]]
        ceiling = max(r["pos"] for r in rows)
        print(f"  K={K}: {len(rows)} classes | survivors pos="
              f"{sorted(round(r['pos'], 3) for r in surv)} | "
              f"non-survivors pos: min={min(r['pos'] for r in non):.3f} "
              f"median={np.median([r['pos'] for r in non]):.3f} "
              f"max={ceiling:.3f} (ceiling class: chords="
              f"{max(rows, key=lambda r: r['pos'])['chords']}, rank="
              f"{max(rows, key=lambda r: r['pos'])['rank']})")
        n_low = sum(1 for r in non if r["pos"] <= 0.5)
        print(f"    non-survivors with pos <= 0.5: {n_low}/{len(non)} | "
              f"EXPAND reachable in class: {ceiling >= 1.0}")
        # fixed-chord contrast: survivors vs non-survivors at same chord count
        for c in sorted({r["chords"] for r in surv}):
            s_at = [r["pos"] for r in surv if r["chords"] == c]
            n_at = [r["pos"] for r in non if r["chords"] == c]
            if n_at:
                print(f"    chords={c}: survivor pos={[round(x,3) for x in s_at]} "
                      f"vs non-survivor median={np.median(n_at):.3f} "
                      f"(n={len(n_at)})")
        out[str(K)] = rows
    return out


def r2_evolved(cycle, W_ticks=48):
    """R2-style divergence with EVOLVED reference (diagnostic; god-view for
    aperiodic patterns). Kick ensemble: on-ring +/-1 at bootstrap + phi ticks."""
    K = len(cycle)
    window = ring_window(cycle)
    samples = []
    for phi in range(K):
        base = {}
        bootstrap(base, cycle, 1)
        dead = False
        for _ in range(phi):
            try:
                tick_multi(base)
            except Exception:  # noqa: BLE001
                dead = True
                break
        if dead:
            continue
        for s in cycle:
            for sgn in (+1, -1):
                ref = dict(base)
                per = dict(base)
                per[s] = per.get(s, 0) + sgn
                if per[s] == 0:
                    del per[s]
                for _ in range(W_ticks):
                    for cv in (ref, per):
                        try:
                            tick_multi(cv)
                        except Exception:  # noqa: BLE001
                            cv.clear()
                    samples.append([per.get(c, 0) - ref.get(c, 0)
                                    for c in window])
    return np.array(samples, dtype=float)


def f3():
    print("\n=== F3: dead-pattern divergence baseline (evolved reference; "
          "diagnostic) ===", flush=True)
    classes = enum_cycles(8)
    non = [c for c in classes if not sustains(c)[0]]
    out = []
    for cyc in non[:3]:
        s = r2_evolved(cyc)
        o = observables(s)
        rg = graph_impulse_corr(ring_graph(cyc), list(range(8)))["dpr_sub"]
        out.append({"chords": chord_count(cyc), "rank": planarity_rank(cyc),
                    "dpr_sub": o["dpr_sub"], "n_active": o["n_active"],
                    "RG": rg})
        print(f"  non-survivor (chords={chord_count(cyc)}, "
              f"rank={planarity_rank(cyc)}): divergence dpr_sub="
              f"{o['dpr_sub']:.3f} n_active={o['n_active']} RG={rg:.3f} "
              f"(survivor M ladder: FLAT 4.36 / CUBE 4.84)")
    return out


def f4():
    print("\n=== F4: LAT anchor locality check ===", flush=True)
    adj = torus3d(12)
    sizes = [len(bfs_distances(adj, c, cutoff=6)) for c in (0, 500, 1000)]
    print(f"  |ball(r=6)| on 12^3 torus (n=1728): {sizes}")
    out = {"ball_r6": sizes, "lat_r3": {}}
    for K in (8, 10):
        vals = []
        for s in range(10):
            rng = np.random.default_rng(300 + s)
            _, taps, _ = sample_bundle(adj, K, 3, rng)
            vals.append(graph_impulse_corr(adj, list(map(int, taps)))["dpr_sub"])
        a = ANCH[str(K)]
        out["lat_r3"][str(K)] = {"mean": float(np.mean(vals)),
                                 "sd": float(np.std(vals))}
        print(f"  K={K}: LAT(r=3)={np.mean(vals):.3f}+/-{np.std(vals):.3f} "
              f"(registered r=6 anchor was {a['LAT_mean']:.3f}; "
              f"EXP={a['EXP_mean']:.3f})")
    return out


def f5():
    print("\n=== F5: RG sensitivity of the T3-B rank swap "
          "(FLAT_K6 vs FLAT_K8) ===", flush=True)
    out = []
    for lam in (0.95, 0.99, 0.999):
        for W in (100, 200, 400):
            r6 = graph_impulse_corr(ring_graph(F2_K6_PERIMETER),
                                    list(range(6)), lam=lam, W=W)["dpr_sub"]
            r8 = graph_impulse_corr(ring_graph(F3_K8_RING),
                                    list(range(8)), lam=lam, W=W)["dpr_sub"]
            out.append({"lam": lam, "W": W, "K6": r6, "K8": r8,
                        "K6_gt_K8": bool(r6 > r8)})
            print(f"  lam={lam} W={W}: RG(K6)={r6:.3f} RG(K8)={r8:.3f} "
                  f"-> K6>K8: {r6 > r8}")
    flips = {r["K6_gt_K8"] for r in out}
    print(f"  ordering stable across grid: {len(flips) == 1}")
    return out


def main():
    t0 = time.time()
    res = {"F1_F2": f1_f2(), "F3": f3(), "F4": f4(), "F5": f5()}
    res["wall_clock_sec"] = round(time.time() - t0, 1)
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "test3_skeptic_tests.json").write_text(
        json.dumps(res, indent=2, default=float))
    print(f"\nwall clock: {res['wall_clock_sec']}s")


if __name__ == "__main__":
    main()
