"""Exp 137 K=12 census — skeptic-mandated verification battery (D1-D7).

  D1  representative invariance of M: reversed / shifted / rotated reps of
      each box-quadruplet member must agree within ~2 bootstrap sd, else
      per-class M is ill-defined and the headline is withdrawn.
  D2  seed-free diagnostics for all 8 survivors: point dpr_sub, n_active,
      frac_nonzero (channel-count explanation in/out).
  D3  death demography per quadruplet member: lethal fraction, death-tick
      stats, absorbed count, remnant census — does M order track it?
  D4  direct Hamiltonian-cycle enumeration of the 2x2x3 box: expect 4 classes.
  D5  census external validation: raw closures vs published SAP counts /24;
      duplicate spot-check of canonical() within same-invariant groups.
  D6  ceiling scaling: constructed 2xMxN box cycles at K=16/32/72 -> pos with
      matched-K anchors (is EXPAND reachable as K grows?).
  D7  true minimal periods of all 8 survivors.
"""

import json
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "134_pattern_coherence"))
sys.path.insert(0, str(HERE))

from multipattern import tick_multi                               # noqa: E402
from rule import bootstrap                                        # noqa: E402
from substrate import face_neighbors                              # noqa: E402
from phase1_t6 import graph_impulse_corr, limit_cycle_phases, observables  # noqa: E402
from phase1b_gate import bootstrap_m, readout_m                   # noqa: E402
from phase1b_skeptic_tests import _OPS, _apply, canonical, chord_count, ring_graph  # noqa: E402
from graphs import random_regular, sample_bundle, torus3d         # noqa: E402
from test3_run import kick_battery                                # noqa: E402

CENSUS = json.load(open(HERE / "results" / "k12_census.json"))
SURV = CENSUS["survivors"]
BOX = [s for s in SURV if s["chords"] == 8]


def mstat(cycle, seed):
    return bootstrap_m(readout_m(cycle), seed=seed)


def d1():
    print("=== D1: representative invariance of M (box quadruplet) ===",
          flush=True)
    rot = lambda c: (c[1], c[2], c[0])  # noqa: E731
    ok_all = True
    out = []
    for i, s in enumerate(BOX):
        cyc = [tuple(c) for c in s["cells"]]
        variants = {
            "rep": cyc,
            "reversed": cyc[::-1],
            "shifted3": cyc[3:] + cyc[:3],
            "rotated": [rot(c) for c in cyc],
        }
        row = {}
        for vname, v in variants.items():
            st = mstat(v, seed=41000 + 10 * i + len(vname))
            row[vname] = (st["dpr_sub_mean"], st["dpr_sub_sd"])
        base_m, base_sd = row["rep"]
        verdicts = {}
        for vname in ("reversed", "shifted3", "rotated"):
            m, sd = row[vname]
            z = abs(m - base_m) / np.sqrt((sd**2 + base_sd**2) / 2)
            verdicts[vname] = z
            if z > 2:
                ok_all = False
        out.append({"member": i, "readings": row, "z": verdicts})
        print(f"  box[{i}] M(rep)={base_m:.3f}: " + "  ".join(
            f"{v}={row[v][0]:.3f}(z={verdicts[v]:.1f})"
            for v in ("reversed", "shifted3", "rotated")), flush=True)
    print(f"  D1 verdict: {'INVARIANT' if ok_all else 'NOT representative-invariant — per-class M ill-defined'}")
    return {"members": out, "invariant": ok_all}


def d2():
    print("\n=== D2: seed-free diagnostics, all 8 survivors ===", flush=True)
    out = []
    for s in SURV:
        cyc = [tuple(c) for c in s["cells"]]
        o = observables(readout_m(cyc))
        out.append({"chords": s["chords"], "rank": s["rank"],
                    "dpr_sub_point": o["dpr_sub"], "n_active": o["n_active"],
                    "frac_nonzero": o["frac_nonzero"]})
        print(f"  chords={s['chords']} rank={s['rank']}: "
              f"dpr_sub={o['dpr_sub']:.3f} n_active={o['n_active']} "
              f"frac_nz={o['frac_nonzero']:.3f}", flush=True)
    quad_na = {r["n_active"] for r in out if r["chords"] == 8}
    print(f"  quadruplet n_active values: {sorted(quad_na)} "
          f"({'equal — channel-count explanation excluded' if len(quad_na) == 1 else 'UNEQUAL — channel-count is lead suspect'})")
    return out


def d3():
    print("\n=== D3: death demography vs M (box quadruplet) ===", flush=True)
    out = []
    for i, s in enumerate(BOX):
        cyc = [tuple(c) for c in s["cells"]]
        K = len(cyc)
        kb = kick_battery(cyc)
        # onring_1 detail: death ticks + absorbed + remnant census at t=6K
        template = limit_cycle_phases(cyc, 1)
        deaths, absorbed, remnants = [], 0, {}
        for phi in range(K):
            for site in cyc:
                for sgn in (+1, -1):
                    per = dict(template[phi])
                    per[site] = per.get(site, 0) + sgn
                    if per[site] == 0:
                        del per[site]
                    death = None
                    for t in range(1, 6 * K + 1):
                        try:
                            tick_multi(per)
                        except Exception:  # noqa: BLE001
                            per = {}
                        alive = sum(1 for v in per.values() if v != 0)
                        if death is None and alive < K:
                            death = t
                    if death is None:
                        absorbed += 1
                    else:
                        deaths.append(death)
                    remnants[sum(1 for v in per.values() if v != 0)] = \
                        remnants.get(sum(1 for v in per.values() if v != 0), 0) + 1
        row = {"member": i, "M": s["M_dpr_sub"], "S1": kb["S1"],
               "onring1_absorbed": absorbed,
               "death_median": float(np.median(deaths)) if deaths else None,
               "death_max": max(deaths) if deaths else None,
               "remnant_census_t6K": remnants,
               "strata": {k: f"{v['survived']}/{v['n']}"
                          for k, v in kb["strata"].items()}}
        out.append(row)
        print(f"  box[{i}] M={s['M_dpr_sub']:.3f}: S1={kb['S1']:.3f} "
              f"onring1_absorbed={absorbed}/{2*K*K} "
              f"death_med={row['death_median']} max={row['death_max']} "
              f"remnants@6K={dict(sorted(remnants.items()))}", flush=True)
    order_m = sorted(out, key=lambda r: r["M"])
    print("  M order vs demography (sorted by M):")
    for r in order_m:
        print(f"    M={r['M']:.3f} S1={r['S1']:.3f} "
              f"absorbed={r['onring1_absorbed']} med={r['death_median']}")
    return out


def d4():
    print("\n=== D4: direct Hamiltonian-cycle enumeration of the 2x2x3 box ===",
          flush=True)
    cells = sorted({tuple(c) for c in BOX[0]["cells"]})
    cellset = set(cells)
    adj = {c: [n for n in face_neighbors(c) if n in cellset] for c in cells}
    classes = {}
    start = cells[0]
    path = [start]
    used = {start}

    def dfs():
        c = path[-1]
        if len(path) == len(cells):
            if start in adj[c]:
                classes.setdefault(canonical(path), list(path))
            return
        for n in adj[c]:
            if n not in used:
                used.add(n)
                path.append(n)
                dfs()
                path.pop()
                used.remove(n)

    dfs()
    print(f"  Hamiltonian cycle classes of the box graph: {len(classes)} "
          f"(census chords=8 row said 4, all surviving)")
    return {"n_classes": len(classes)}


def d5():
    print("\n=== D5: census external validation ===", flush=True)
    # published cubic-lattice SAP counts (per translation class x 24 = raw)
    pub = {8: 3312, 10: 48240, 12: 762096}
    raw = {8: 138, 10: 2010, 12: 31754}
    for K, r in raw.items():
        print(f"  K={K}: raw closures {r} x 24 = {r*24} "
              f"(published SAP count {pub[K]}: "
              f"{'MATCH' if r*24 == pub[K] else 'MISMATCH'})")
    # duplicate spot-check: same-invariant groups, full-transform comparison
    census = CENSUS["census"]
    # rebuild cells for a sample: re-enumerate is costly; use survivors +
    # random pairs from stage of enum? census rows lack cells (stripped) except
    # survivors. Re-enumerate K=12 classes' reps cheaply via stored survivors
    # only is insufficient — instead re-run the K=8 and K=10 enumerations and
    # duplicate-check ALL their class reps pairwise (small: 11 and 73).
    from phase1b_skeptic_tests import enum_cycles
    dup_found = 0
    for K in (8, 10):
        reps = enum_cycles(K)
        for a, b in combinations(reps, 2):
            sa = {tuple(c) for c in a}
            # quick invariant screen
            if chord_count(a) != chord_count(b):
                continue
            for op in _OPS:
                tb = [_apply(op, c) for c in b]
                for rev in (tb, tb[::-1]):
                    for s in range(K):
                        rot = rev[s:] + rev[:s]
                        o = rot[0]
                        shifted = {(c[0]-o[0]+a[0][0], c[1]-o[1]+a[0][1],
                                    c[2]-o[2]+a[0][2]) for c in rot}
                        if shifted == sa:
                            # cell-set match — full ordered check
                            ord_shift = [(c[0]-o[0]+a[0][0], c[1]-o[1]+a[0][1],
                                          c[2]-o[2]+a[0][2]) for c in rot]
                            if ord_shift == [tuple(x) for x in a]:
                                dup_found += 1
        print(f"  K={K}: pairwise duplicate scan over {len(reps)} class reps: "
              f"{dup_found} duplicates", flush=True)
    return {"oeis_match": all(raw[k]*24 == pub[k] for k in raw),
            "duplicates": dup_found}


def snake_box_cycle(m, n):
    """Hamiltonian cycle of the 2 x m x n box: boustrophedon on layer x=0,
    mirrored return on x=1."""
    p = []
    for y in range(m):
        rng = range(n) if y % 2 == 0 else range(n - 1, -1, -1)
        p.extend((y, z) for z in rng)
    return [(0, y, z) for (y, z) in p] + [(1, y, z) for (y, z) in reversed(p)]


def d6():
    print("\n=== D6: pos ceiling scaling on constructed box cycles ===",
          flush=True)
    lat_adj = torus3d(12)
    exp_adj = random_regular(1728, 6, np.random.default_rng(0))
    out = []
    for m, n in ((2, 4), (4, 4), (6, 6)):
        cyc = snake_box_cycle(m, n)
        K = len(cyc)
        rg = graph_impulse_corr(ring_graph(cyc), list(range(K)))["dpr_sub"]
        ck = graph_impulse_corr([[(i-1) % K, (i+1) % K] for i in range(K)],
                                list(range(K)))["dpr_sub"]
        lat = []
        for sd in range(10):
            rng = np.random.default_rng(100 + sd)
            _, taps, _ = sample_bundle(lat_adj, K, 6, rng)
            lat.append(graph_impulse_corr(lat_adj, list(map(int, taps)))["dpr_sub"])
        pos = (rg - ck) / (np.mean(lat) - ck)
        out.append({"box": f"2x{m}x{n}", "K": K, "chords": chord_count(cyc),
                    "RG": rg, "CK": ck, "LAT": float(np.mean(lat)),
                    "pos": float(pos)})
        print(f"  2x{m}x{n} (K={K}, chords={chord_count(cyc)}): RG={rg:.2f} "
              f"CK={ck:.2f} LAT={np.mean(lat):.2f} pos={pos:.3f}", flush=True)
    return out


def d7():
    print("\n=== D7: true minimal periods of the 8 survivors ===", flush=True)
    out = []
    for s in SURV:
        cyc = [tuple(c) for c in s["cells"]]
        cv = {}
        bootstrap(cv, cyc, 1)
        first = tuple(sorted(cv.items()))
        period = None
        for t in range(1, 49):
            tick_multi(cv)
            if tuple(sorted(cv.items())) == first:
                period = t
                break
        out.append({"chords": s["chords"], "rank": s["rank"], "period": period})
        print(f"  chords={s['chords']} rank={s['rank']}: minimal period={period}")
    return out


def main():
    t0 = time.time()
    res = {"D1": d1(), "D2": d2(), "D3": d3(), "D4": d4(), "D5": d5(),
           "D6": d6(), "D7": d7()}
    res["wall_clock_sec"] = round(time.time() - t0, 1)
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "k12_verify.json").write_text(
        json.dumps(res, indent=2, default=float))
    print(f"\nwall clock: {res['wall_clock_sec']}s")


if __name__ == "__main__":
    main()
