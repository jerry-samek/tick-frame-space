"""Exp 137 Test 3 — stability-selection vs observer-rank (PREREG_test3.md).

Fixtures: the complete K<=10 survivor family (Phase 1b census).
Readings: frozen M readout + impulse anchors at matched channel count N=K
  (C_K intrinsic anchor, ring-graph prediction, lattice3d / expander6 ambient
  bundles).
Self-maintenance: S1 kick-battery survival fraction (exhaustive, deterministic),
  S2 noise time-to-death (p=0.005 magnitude jitter, 12 seeds, median).
Decisions: T3-A (cluster-low vs expand), T3-B (Spearman M vs ring-graph),
  T3-C (within-pair robustness x rank signs), T3-D (normalized table).
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "134_pattern_coherence"))
sys.path.insert(0, str(HERE))

from fixtures import F1_K4_SQUARE, F2_K6_PERIMETER, F3_K8_RING  # noqa: E402
from multipattern import tick_multi                             # noqa: E402
from substrate import face_neighbors                            # noqa: E402
from rule import bootstrap                                      # noqa: E402
from phase1_t6 import graph_impulse_corr, limit_cycle_phases    # noqa: E402
from phase1_t6_embed import CUBE_K8                             # noqa: E402
from phase1b_gate import bootstrap_m, readout_m                 # noqa: E402
from phase1b_skeptic_tests import ring_graph, chord_count, planarity_rank  # noqa: E402
from graphs import random_regular, sample_bundle, torus3d       # noqa: E402

FLAT_K10 = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0),
            (4, 1, 0), (3, 1, 0), (2, 1, 0), (1, 1, 0), (0, 1, 0)]
TOWER_K10 = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (2, 1, 0), (1, 1, 0), (0, 1, 0),
             (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)]

FAMILY = {
    "FLAT_K4": F1_K4_SQUARE, "FLAT_K6": F2_K6_PERIMETER,
    "FLAT_K8": F3_K8_RING, "CUBE_K8": CUBE_K8,
    "FLAT_K10": FLAT_K10, "TOWER_K10": TOWER_K10,
}
PAIRS = [("FLAT_K8", "CUBE_K8"), ("FLAT_K10", "TOWER_K10")]
N_BUNDLE_SEEDS = 10


# ---------- impulse anchors ----------

def cycle_graph(K):
    return [[(i - 1) % K, (i + 1) % K] for i in range(K)]


def anchors_for_K(K, lat_adj, exp_adj):
    ck = graph_impulse_corr(cycle_graph(K), list(range(K)))["dpr_sub"]
    lat, expd = [], []
    for s in range(N_BUNDLE_SEEDS):
        rng = np.random.default_rng(100 + s)
        _, taps, _ = sample_bundle(lat_adj, K, 6, rng)
        lat.append(graph_impulse_corr(lat_adj, list(map(int, taps)))["dpr_sub"])
        rng = np.random.default_rng(200 + s)
        _, taps, _ = sample_bundle(exp_adj, K, 6, rng)
        expd.append(graph_impulse_corr(exp_adj, list(map(int, taps)))["dpr_sub"])
    return {"CK": ck,
            "LAT_mean": float(np.mean(lat)), "LAT_sd": float(np.std(lat)),
            "EXP_mean": float(np.mean(expd)), "EXP_sd": float(np.std(expd))}


# ---------- S1: kick battery ----------

def survives(canvas, K):
    """Evolve 50*K ticks; survival = exactly K nonzero cells over one further
    period AND exact period-K recurrence (translation/phase-shift allowed).
    Returns 'survived' | 'died' | 'mutated'."""
    cv = dict(canvas)
    try:
        for _ in range(50 * K):
            tick_multi(cv)
        snaps = []
        for _ in range(K + 1):
            snaps.append(tuple(sorted((c, v) for c, v in cv.items() if v != 0)))
            if not all(len(s) == 0 or True for s in snaps):
                pass
            tick_multi(cv)
    except Exception:  # noqa: BLE001 (wedged / empty canvas)
        return "died"
    counts = {len(s) for s in snaps}
    if counts == {K} and snaps[0] == snaps[K]:
        return "survived"
    if 0 in counts or min(counts) < K:
        return "died"
    return "mutated"


def kick_battery(cycle):
    K = len(cycle)
    template = limit_cycle_phases(cycle, 1)
    ring = set(cycle)
    collar = sorted({nb for c in cycle for nb in face_neighbors(c)} - ring)
    kicks = []  # (stratum, phase, cell, delta_or_None)
    for phi in range(K):
        for s in cycle:
            for sgn in (+1, -1):
                kicks.append(("onring_1", phi, s, sgn * 1))
                kicks.append(("onring_K", phi, s, sgn * K))
        for c in collar:
            kicks.append(("offring_K", phi, c, K))
        for s in cycle:
            kicks.append(("delete", phi, s, None))
    tallies = {}
    for stratum, phi, cell, dv in kicks:
        per = dict(template[phi])
        if dv is None:
            per.pop(cell, None)
        else:
            per[cell] = per.get(cell, 0) + dv
            if per[cell] == 0:
                del per[cell]
        r = survives(per, K)
        t = tallies.setdefault(stratum, {"survived": 0, "died": 0, "mutated": 0, "n": 0})
        t[r] += 1
        t["n"] += 1
    total = sum(t["n"] for t in tallies.values())
    surv = sum(t["survived"] for t in tallies.values())
    return {"strata": tallies, "S1": surv / total, "n_total": total}


# ---------- S2: noise time-to-death ----------

def noise_ttd(cycle, p=0.005, T=4000, n_seeds=12):
    """Magnitude jitter (phase1b_recon r1_drive protocol); death = first tick
    where the canvas holds fewer than K nonzero cells (position-free, so a
    translated survivor does not count as dead). Returns per-seed ticks, median."""
    K = len(cycle)
    ttds = []
    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        cv = {}
        bootstrap(cv, cycle, 1)
        t_death = T
        for t in range(T):
            for c in list(cv.keys()):
                if rng.random() < p:
                    cv[c] += 1 if rng.random() < 0.5 else -1
                    if cv[c] == 0:
                        del cv[c]
            try:
                tick_multi(cv)
            except Exception:  # noqa: BLE001
                t_death = t
                break
            if sum(1 for v in cv.values() if v != 0) < K:
                t_death = t
                break
        ttds.append(t_death)
    return {"ttds": ttds, "S2_median": float(np.median(ttds))}


# ---------- decisions ----------

def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def main():
    t0 = time.time()
    out = {"prereg": "PREREG_test3.md", "fixtures": {}, "anchors": {},
           "decisions": {}}

    print("=== readings: M (frozen) + fixture structure ===", flush=True)
    for name, cyc in FAMILY.items():
        st = bootstrap_m(readout_m(cyc), seed=abs(hash(("t3", name))) % 2**32)
        rg = graph_impulse_corr(ring_graph(cyc), list(range(len(cyc))))["dpr_sub"]
        out["fixtures"][name] = {
            "K": len(cyc), "rank3d": planarity_rank(cyc),
            "chords": chord_count(cyc),
            "M_dpr_sub": st["dpr_sub_mean"], "M_sd": st["dpr_sub_sd"],
            "RG_dpr_sub": rg,
        }
        print(f"  {name}: K={len(cyc)} rank={planarity_rank(cyc)} "
              f"chords={chord_count(cyc)} M={st['dpr_sub_mean']:.3f}"
              f"+/-{st['dpr_sub_sd']:.3f} RG={rg:.3f}", flush=True)

    print("\n=== impulse anchors at matched N=K ===", flush=True)
    grng = np.random.default_rng(0)
    lat_adj = torus3d(12)
    exp_adj = random_regular(1728, 6, grng)
    for K in sorted({len(c) for c in FAMILY.values()}):
        a = anchors_for_K(K, lat_adj, exp_adj)
        out["anchors"][str(K)] = a
        print(f"  K={K}: CK={a['CK']:.3f} LAT={a['LAT_mean']:.3f}"
              f"+/-{a['LAT_sd']:.3f} EXP={a['EXP_mean']:.3f}+/-{a['EXP_sd']:.3f}",
              flush=True)

    print("\n=== S1: kick battery ===", flush=True)
    for name, cyc in FAMILY.items():
        kb = kick_battery(cyc)
        out["fixtures"][name]["kick"] = kb
        strata = " ".join(f"{s}:{t['survived']}/{t['n']}"
                          for s, t in kb["strata"].items())
        print(f"  {name}: S1={kb['S1']:.3f} ({strata})", flush=True)

    print("\n=== S2: noise time-to-death (p=0.005, 12 seeds) ===", flush=True)
    for name, cyc in FAMILY.items():
        nt = noise_ttd(cyc)
        out["fixtures"][name]["S2_median"] = nt["S2_median"]
        out["fixtures"][name]["S2_ttds"] = nt["ttds"]
        print(f"  {name}: S2_median={nt['S2_median']:.0f} ticks={nt['ttds']}",
              flush=True)

    # ---- T3-A ----
    print("\n=== decisions ===")
    posv, expand_hits = {}, []
    for name, f in out["fixtures"].items():
        a = out["anchors"][str(f["K"])]
        pos = (f["RG_dpr_sub"] - a["CK"]) / (a["LAT_mean"] - a["CK"])
        posv[name] = pos
        if f["RG_dpr_sub"] >= a["LAT_mean"] - 2 * a["LAT_sd"]:
            expand_hits.append(name)
        print(f"  T3-A {name}: pos={pos:.3f} "
              f"(RG={f['RG_dpr_sub']:.3f}, CK={a['CK']:.3f}, "
              f"LAT={a['LAT_mean']:.3f}-2sd={a['LAT_mean']-2*a['LAT_sd']:.3f})")
    if expand_hits:
        t3a = f"EXPAND (claim-5 falsified): {expand_hits} ambient-indistinguishable or beyond"
    elif all(p <= 0.5 for p in posv.values()):
        t3a = "CLUSTER-LOW"
    else:
        t3a = "INTERMEDIATE (strong claim-5 fails; not ambient-like either)"
    out["decisions"]["T3_A_pos"] = posv
    out["decisions"]["T3_A"] = t3a
    print(f"  T3-A verdict: {t3a}")

    # ---- T3-B ----
    names = list(FAMILY)
    rho = spearman([out["fixtures"][n]["M_dpr_sub"] for n in names],
                   [out["fixtures"][n]["RG_dpr_sub"] for n in names])
    out["decisions"]["T3_B_spearman"] = rho
    out["decisions"]["T3_B"] = ("M tracks graph structure family-wide"
                                if rho >= 0.8 else
                                "attribution does NOT generalize (open anomaly)")
    print(f"  T3-B: Spearman(M, RG) = {rho:.3f} -> {out['decisions']['T3_B']}")

    # ---- T3-C ----
    signs = []
    for a, b in PAIRS:
        fa, fb = out["fixtures"][a], out["fixtures"][b]
        d_rank = fb["M_dpr_sub"] - fa["M_dpr_sub"]
        for score in ("kick", "S2_median"):
            d_rob = ((fb["kick"]["S1"] - fa["kick"]["S1"]) if score == "kick"
                     else fb["S2_median"] - fa["S2_median"])
            if d_rob == 0:
                signs.append((f"{a}vs{b}:{score}", "zero-variance"))
                print(f"  T3-C {a} vs {b} [{score}]: robustness tie "
                      f"(d_rob=0) — no sign")
                continue
            s = "negative" if d_rob * d_rank < 0 else "positive"
            signs.append((f"{a}vs{b}:{score}", s))
            print(f"  T3-C {a} vs {b} [{score}]: d_rob={d_rob:+.3f} "
                  f"d_rank={d_rank:+.3f} -> {s}")
    usable = [s for _, s in signs if s != "zero-variance"]
    neg, pos = usable.count("negative"), usable.count("positive")
    if len(usable) < 3:
        t3c = f"INCONCLUSIVE (only {len(usable)} usable signs; pre-named saturation trap)"
    elif neg >= 3:
        t3c = "claim-5-consistent (more robust -> lower rank)"
    elif pos >= 3:
        t3c = "claim-5-FALSIFIED (more robust -> rank expansion)"
    else:
        t3c = "INCONCLUSIVE"
    out["decisions"]["T3_C_signs"] = signs
    out["decisions"]["T3_C"] = t3c
    print(f"  T3-C verdict: {t3c}")

    # ---- T3-D ----
    print("  T3-D normalized (dpr_sub/(N-1)): ", end="")
    t3d = {}
    for name, f in out["fixtures"].items():
        a = out["anchors"][str(f["K"])]
        t3d[name] = {"M_norm": f["M_dpr_sub"] / (f["K"] - 1),
                     "LAT_norm": a["LAT_mean"] / (f["K"] - 1),
                     "EXP_norm": a["EXP_mean"] / (f["K"] - 1)}
    out["decisions"]["T3_D"] = t3d
    print({k: round(v["M_norm"], 3) for k, v in t3d.items()})

    out["wall_clock_sec"] = round(time.time() - t0, 1)
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "test3.json").write_text(
        json.dumps(out, indent=2, default=float))
    print(f"\nwall clock: {out['wall_clock_sec']}s")


if __name__ == "__main__":
    main()
