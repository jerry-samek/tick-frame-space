"""Exp 137 — K=12 cycle census (RESULTS_test3.md / RAW 134 §16.2 path (a)).

Scope (stated up front, per the reachable-range process rule):
  This is a CENSUS + instrument reconnaissance, not a registered decision test.
  It computes, over ALL closed self-avoiding face-adjacent 12-cycles in Z^3
  up to isometry x cyclic shift x reversal:
    C1  class count and survivor set under the Exp 134 rule (sustains());
    C2  the reachable range of the Test-3 pos statistic (census ceiling) —
        is the claim-5 EXPAND falsifier attainable at K=12?
    C3  chord/3D decoupling: does the K=12 family contain survivors (or
        classes) where chord count and planarity rank decouple — the
        prerequisite for breaking Test 3's common-cause null;
    C4  the fixed-chords survivor-vs-non-survivor RG contrast (Test 3's
        unpowered hint, at K=12 statistics);
    C5  M readings for all survivors (descriptive).
  Any actual claim-5 test on these fixtures requires a fresh PREREG.

Enumeration speedups vs phase1b enum_cycles (validated against its K=8: 11
and K=10: 73 class counts before K=12 runs):
  - symmetry-restricted DFS: cell0 = origin, step0 = +x, first non-x step
    (if any) = +y — every isometry class has such a representative;
  - parity + L1 closure pruning;
  - two-stage dedupe: cheap stage-1 key (cyclic shift x reversal only),
    full 48-op canonical form computed only for stage-1-new cycles.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "134_pattern_coherence"))
sys.path.insert(0, str(HERE))

from phase1_t6 import graph_impulse_corr                          # noqa: E402
from phase1_t6_embed import sustains                              # noqa: E402
from phase1b_gate import bootstrap_m, readout_m                   # noqa: E402
from phase1b_skeptic_tests import (                                # noqa: E402
    canonical, chord_count, planarity_rank, ring_graph)
from graphs import random_regular, sample_bundle, torus3d         # noqa: E402

STEPS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
PRE_TURN_STEPS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0)]  # first non-x step = +y


def stage1_key(cycle):
    """Min over cyclic shift x reversal of the origin-anchored tuple (cheap)."""
    K = len(cycle)
    best = None
    for rev in (cycle, cycle[::-1]):
        for s in range(K):
            rot = rev[s:] + rev[:s]
            o = rot[0]
            t = tuple((c[0] - o[0], c[1] - o[1], c[2] - o[2]) for c in rot)
            if best is None or t < best:
                best = t
    return best


def enum_cycles_fast(K, log_every=200000):
    classes = {}
    stage1 = set()
    raw = [0]
    t0 = time.time()
    path = [(0, 0, 0), (1, 0, 0)]
    used = {(0, 0, 0), (1, 0, 0)}

    def dfs(has_turned):
        c = path[-1]
        rem = K - len(path)
        if rem == 0:
            if abs(c[0]) + abs(c[1]) + abs(c[2]) == 1:
                raw[0] += 1
                if raw[0] % log_every == 0:
                    print(f"    ... raw closures {raw[0]} "
                          f"stage1 {len(stage1)} classes {len(classes)} "
                          f"({time.time()-t0:.0f}s)", flush=True)
                k1 = stage1_key(path)
                if k1 not in stage1:
                    stage1.add(k1)
                    classes.setdefault(canonical(path), list(path))
            return
        steps = STEPS if has_turned else PRE_TURN_STEPS
        for dx, dy, dz in steps:
            n = (c[0] + dx, c[1] + dy, c[2] + dz)
            if n in used:
                continue
            l1 = abs(n[0]) + abs(n[1]) + abs(n[2])
            # after n there are rem-1 steps; the final cell must sit at L1 == 1
            # (the cycle closes by adjacency to the origin, not by returning to it)
            if l1 > rem or (rem - l1) % 2:  # unreachable / parity mismatch
                continue
            used.add(n)
            path.append(n)
            dfs(has_turned or dy != 0 or dz != 0)
            path.pop()
            used.remove(n)

    dfs(False)
    print(f"  K={K}: raw closures {raw[0]}, stage1 {len(stage1)}, "
          f"classes {len(classes)} ({time.time()-t0:.0f}s)", flush=True)
    return list(classes.values())


def anchors_for_K12():
    ck = graph_impulse_corr([[(i - 1) % 12, (i + 1) % 12] for i in range(12)],
                            list(range(12)))["dpr_sub"]
    lat_adj = torus3d(12)
    exp_adj = random_regular(1728, 6, np.random.default_rng(0))
    lat, expd = [], []
    for s in range(10):
        rng = np.random.default_rng(100 + s)
        _, taps, _ = sample_bundle(lat_adj, 12, 6, rng)
        lat.append(graph_impulse_corr(lat_adj, list(map(int, taps)))["dpr_sub"])
        rng = np.random.default_rng(200 + s)
        _, taps, _ = sample_bundle(exp_adj, 12, 6, rng)
        expd.append(graph_impulse_corr(exp_adj, list(map(int, taps)))["dpr_sub"])
    return {"CK": ck, "LAT_mean": float(np.mean(lat)), "LAT_sd": float(np.std(lat)),
            "EXP_mean": float(np.mean(expd)), "EXP_sd": float(np.std(expd))}


def main():
    validate = "--skip-validate" not in sys.argv
    t0 = time.time()

    if validate:
        print("=== validation against phase1b census ===", flush=True)
        n8 = len(enum_cycles_fast(8))
        n10 = len(enum_cycles_fast(10))
        assert n8 == 11, f"K=8 expected 11 classes, got {n8}"
        assert n10 == 73, f"K=10 expected 73 classes, got {n10}"
        print("  validation OK (11 / 73)", flush=True)

    print("\n=== K=12 enumeration ===", flush=True)
    classes = enum_cycles_fast(12)

    print("\n=== anchors (K=12) ===", flush=True)
    a = anchors_for_K12()
    print(f"  CK={a['CK']:.3f} LAT={a['LAT_mean']:.3f}+/-{a['LAT_sd']:.3f} "
          f"EXP={a['EXP_mean']:.3f}+/-{a['EXP_sd']:.3f}", flush=True)

    print("\n=== census sweep: sustains + RG for every class ===", flush=True)
    rows = []
    tswp = time.time()
    for i, cyc in enumerate(classes):
        ok, _ = sustains(cyc)
        rg = graph_impulse_corr(ring_graph(cyc), list(range(12)))["dpr_sub"]
        rows.append({"i": i, "survives": bool(ok), "chords": chord_count(cyc),
                     "rank": planarity_rank(cyc), "RG": rg,
                     "pos": (rg - a["CK"]) / (a["LAT_mean"] - a["CK"]),
                     "cells": cyc})
        if (i + 1) % 200 == 0:
            print(f"    ... {i+1}/{len(classes)} "
                  f"({time.time()-tswp:.0f}s)", flush=True)

    surv = [r for r in rows if r["survives"]]
    non = [r for r in rows if not r["survives"]]

    # C1
    print(f"\nC1: {len(classes)} classes, {len(surv)} survivors", flush=True)
    for r in surv:
        print(f"  survivor: rank={r['rank']} chords={r['chords']} "
              f"RG={r['RG']:.3f} pos={r['pos']:.3f} cells={r['cells']}")

    # C2: reachable range of pos
    ceil_row = max(rows, key=lambda r: r["pos"])
    print(f"\nC2: pos range over census: [{min(r['pos'] for r in rows):.3f}, "
          f"{ceil_row['pos']:.3f}] (ceiling class: chords={ceil_row['chords']} "
          f"rank={ceil_row['rank']}); EXPAND (pos>=1) reachable: "
          f"{ceil_row['pos'] >= 1.0}")
    print(f"    max chords in census: {max(r['chords'] for r in rows)}")

    # C3: chord/3D decoupling
    print("\nC3: chords x rank cross-tab (all classes; survivors in [])")
    tab = {}
    for r in rows:
        key = (r["chords"], r["rank"])
        tab.setdefault(key, [0, 0])
        tab[key][0] += 1
        tab[key][1] += r["survives"]
    for (c, k), (n, s) in sorted(tab.items()):
        print(f"    chords={c} rank={k}: {n} classes [{s} survivors]")
    s_planar_chordy = [r for r in surv if r["rank"] == 2 and r["chords"] >= 4]
    s_3d_flat = [r for r in surv if r["rank"] == 3 and r["chords"] <= 3]
    print(f"    decoupling survivors: planar-chordy(>=4)={len(s_planar_chordy)} "
          f"3D-fewchord(<=3)={len(s_3d_flat)}")

    # C4: fixed-chords survivor vs non-survivor RG contrast
    print("\nC4: fixed-chords survivor-vs-non contrast (pos)")
    for c in sorted({r["chords"] for r in surv}):
        s_at = [r["pos"] for r in surv if r["chords"] == c]
        n_at = [r["pos"] for r in non if r["chords"] == c]
        if n_at:
            print(f"    chords={c}: survivors "
                  f"{[round(x, 3) for x in sorted(s_at)]} vs non-survivors "
                  f"median={np.median(n_at):.3f} IQR="
                  f"[{np.percentile(n_at, 25):.3f},{np.percentile(n_at, 75):.3f}] "
                  f"(n={len(n_at)})")

    # C5: M readings for survivors
    print("\nC5: M readings (frozen readout) for K=12 survivors", flush=True)
    for r in surv:
        st = bootstrap_m(readout_m(r["cells"]), seed=12000 + r["i"])
        r["M_dpr_sub"] = st["dpr_sub_mean"]
        r["M_sd"] = st["dpr_sub_sd"]
        print(f"  rank={r['rank']} chords={r['chords']}: "
              f"M={st['dpr_sub_mean']:.3f}+/-{st['dpr_sub_sd']:.3f}")

    out = {"anchors": a, "n_classes": len(classes), "n_survivors": len(surv),
           "survivors": surv,
           "census": [{k: v for k, v in r.items() if k != "cells"}
                      for r in rows],
           "wall_clock_sec": round(time.time() - t0, 1)}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "k12_census.json").write_text(
        json.dumps(out, indent=2, default=float))
    print(f"\nwall clock: {out['wall_clock_sec']}s")


if __name__ == "__main__":
    main()
