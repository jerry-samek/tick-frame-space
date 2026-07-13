"""Exp 137 Phase 0 — calibration gate for the observer-rank instrument.

Runs the frozen pipeline (PREREG.md) on known-geometry fixtures + nulls,
evaluates gates G1-G5, writes results/phase0_calibration.json.
"""

import json
import time
from pathlib import Path

import numpy as np

from graphs import torus3d, torus2d, random_regular, binary_tree, bfs_distances, sample_bundle
from dynamics import run_ar1
from readout import corrmat, dpr_raw, dpr_sub, mds_dim90, corr_decay

LAM, BURN, STEPS = 0.99, 1000, 20000  # lam retuned 0.9 -> 0.99 + lazy walk (logged deviation, see dynamics.py)
N_TAP, RADIUS = 64, 6
SEEDS = range(10)

GRAPH_FIXTURES = {
    "lattice3d": lambda rng: torus3d(12),
    "lattice2d": lambda rng: torus2d(42),
    "expander": lambda rng: random_regular(1750, 3, rng),
    "tree": lambda rng: binary_tree(10),
}


def run_graph_fixture(name, seed):
    rng = np.random.default_rng(seed)
    adj = GRAPH_FIXTURES[name](rng)
    center, taps, _ = sample_bundle(adj, N_TAP, RADIUS, rng)
    x = run_ar1(adj, taps, lam=LAM, burn=BURN, steps=STEPS, rng=rng)
    c = corrmat(x)
    dist_by_tap = {int(t): bfs_distances(adj, int(t), cutoff=RADIUS) for t in taps}
    d1, d6 = corr_decay(c, taps, dist_by_tap)
    return {
        "dpr_raw": dpr_raw(c),
        "dpr_sub": dpr_sub(c),
        "mds_dim90": mds_dim90(c),
        "corr_d1": d1,
        "corr_d6": d6,
    }


def run_null(name, seed):
    rng = np.random.default_rng(seed)
    if name == "null_indep":
        x = rng.standard_normal((STEPS, N_TAP))
    else:  # null_corr: one common signal + 1%-variance independent noise
        x = rng.standard_normal((STEPS, 1)) + 0.1 * rng.standard_normal((STEPS, N_TAP))
    c = corrmat(x)
    return {"dpr_raw": dpr_raw(c), "dpr_sub": dpr_sub(c), "mds_dim90": mds_dim90(c)}


def agg(rows, key):
    v = np.array([r[key] for r in rows], dtype=float)
    return float(np.nanmean(v)), float(np.nanstd(v))


def main():
    t0 = time.time()
    raw = {}
    for name in list(GRAPH_FIXTURES) + ["null_indep", "null_corr"]:
        rows = []
        for seed in SEEDS:
            r = run_graph_fixture(name, seed) if name in GRAPH_FIXTURES else run_null(name, seed)
            rows.append(r)
            print(f"  {name} seed={seed}: {r}", flush=True)
        raw[name] = rows

    stats = {
        name: {key: agg(rows, key) for key in rows[0]}
        for name, rows in raw.items()
    }

    # ---- gates (pre-registered) ----
    gf = list(GRAPH_FIXTURES)
    gates = {}

    # G1: pairwise separation >= 2x pooled sd on at least one of {O2, O3}
    g1_detail = {}
    for i in range(len(gf)):
        for k in range(i + 1, len(gf)):
            a, b = gf[i], gf[k]
            sep = False
            for obs in ("dpr_sub", "mds_dim90"):
                ma, sa = stats[a][obs]
                mb, sb = stats[b][obs]
                pooled = np.sqrt((sa**2 + sb**2) / 2)
                if pooled == 0 and ma != mb:
                    sep = True
                elif pooled > 0 and abs(ma - mb) >= 2 * pooled:
                    sep = True
            g1_detail[f"{a}|{b}"] = sep
    gates["G1_separation"] = all(g1_detail.values())
    gates["G1_detail"] = g1_detail

    # G2: ordering, benchmark-relative
    gates["G2_ordering"] = stats["lattice3d"]["mds_dim90"][0] > stats["lattice2d"]["mds_dim90"][0]

    # G3: honesty — expander reading in [2.5, 3.5] disqualifies that observable
    disq = [
        obs for obs in ("dpr_raw", "dpr_sub", "mds_dim90")
        if 2.5 <= stats["expander"][obs][0] <= 3.5
    ]
    gates["G3_disqualified_observables"] = disq
    gates["G3_pass"] = len(disq) < 3

    # G4: nulls
    gates["G4_nulls"] = (
        stats["null_indep"]["dpr_raw"][0] > 0.8 * N_TAP
        and stats["null_corr"]["dpr_raw"][0] < 1.5
    )

    # G5: positive control — correlation decays with distance on both lattices
    gates["G5_decay"] = all(
        stats[l]["corr_d1"][0] >= 2 * stats[l]["corr_d6"][0]
        for l in ("lattice3d", "lattice2d")
    )

    gates["PHASE0_PASS"] = all(
        gates[k] for k in ("G1_separation", "G2_ordering", "G3_pass", "G4_nulls", "G5_decay")
    )

    out = {"prereg": "PREREG.md", "params": {"lam": LAM, "burn": BURN, "steps": STEPS,
           "n_tap": N_TAP, "radius": RADIUS, "seeds": len(list(SEEDS))},
           "stats": stats, "gates": gates, "raw": raw,
           "wall_clock_sec": round(time.time() - t0, 1)}
    outdir = Path(__file__).parent / "results"
    outdir.mkdir(exist_ok=True)
    (outdir / "phase0_calibration.json").write_text(json.dumps(out, indent=2))

    print("\n=== Exp 137 Phase 0 summary (mean +/- sd over 10 seeds) ===")
    hdr = f"{'fixture':<12}{'dpr_raw':>16}{'dpr_sub':>16}{'mds_dim90':>14}{'corr d1/d6':>18}"
    print(hdr)
    for name in raw:
        s = stats[name]
        decay = (f"{s['corr_d1'][0]:.3f}/{s['corr_d6'][0]:.3f}"
                 if "corr_d1" in s else "-")
        print(f"{name:<12}{s['dpr_raw'][0]:>10.2f}+/-{s['dpr_raw'][1]:<4.2f}"
              f"{s['dpr_sub'][0]:>10.2f}+/-{s['dpr_sub'][1]:<4.2f}"
              f"{s['mds_dim90'][0]:>9.2f}+/-{s['mds_dim90'][1]:<4.2f}{decay:>16}")
    print("\ngates:", {k: v for k, v in gates.items() if not k.endswith("detail")})


if __name__ == "__main__":
    main()
