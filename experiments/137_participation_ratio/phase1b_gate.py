"""Exp 137 Phase 1b — redesigned applicability gate (PREREG_phase1b.md).

Certifies whether the inside-consistent readout M distinguishes Exp 134
survivors by their 3D embedding at FIXED period K (reads geometry, not
period/size).

Readout M (frozen in PREREG_phase1b.md sec. 2):
  - perturbation ensemble: exhaustive (phase phi in 0..K-1, ring-site s, sign +/-1),
    single +/-1 kick;
  - reference = the observer's MEMORIZED period-K template (inside-consistent
    for a periodic survivor; numerically == R2, see recon F2) — implemented
    literally: d(t) = gamma_pert(t) - template[(phi0 + t) mod K], horizon W = 6K;
  - channels = ring cells + face-neighbor collar; zero-variance channels dropped;
    observables dpr_sub (decisive, per recon) and mds_dim90c (reported);
  - statistics: bootstrap B = 200 resamples over the perturbation ensemble.

Gates (pre-registered):
  G-M1  embedding discrimination: CUBE_K8 vs FLAT_K8 >= 2 pooled sd (dpr_sub).
  G-M2  same-embedding negative control: FLAT_K8 set A vs set B < 2 pooled sd.
  G-M3  calibration transfer: impulse readout reproduces Phase 0's signed
        separation (expander6 > lattice3d).
  G-M4  inside-consistency: by construction (memorized-template reference,
        position-free channel observables).
PASS = G-M1 and G-M2 and G-M3 (and G-M4 by construction).

Also run (PREREG sec. 3, non-gating): the K4/K6/K8 planar period-axis context,
and the family-widening probes — second planar K8 candidates (3x3 ring,
zigzag) and a 3D K=6 candidate (Petrie hexagon) under sustains(); any that
sustains gets an M reading; failures are logged as substrate limits.
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
from phase1_t6 import (                                          # noqa: E402
    graph_impulse_corr, limit_cycle_phases, observables, ring_window)
from phase1_t6_embed import CUBE_K8, sustains                    # noqa: E402
from graphs import random_regular, sample_bundle, torus3d       # noqa: E402

B_BOOT = 200
W_FACTOR = 6

# --- family-widening candidates (PREREG_phase1b.md sec. 3, probed not assumed) ---
RING3x3_K8 = [  # 3x3 perimeter; known geometric-constraint violation (interior hole)
    (0, 0, 0), (1, 0, 0), (2, 0, 0), (2, 1, 0),
    (2, 2, 0), (1, 2, 0), (0, 2, 0), (0, 1, 0),
]
ZIGZAG_K8 = [  # L/staircase planar 8-cycle; cell (1,1,0) has 4 ring neighbors
    (0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 1, 0),
    (2, 2, 0), (1, 2, 0), (0, 2, 0), (0, 1, 0),
]
HEX3D_K6 = [  # Petrie hexagon of the cube: genuinely 3D K=6 cycle
    (0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1), (0, 0, 1),
]


def readout_m(cycle, sign=1, mag=1):
    """Readout M: divergence of the perturbed trajectory from the observer's
    memorized period-K template. The reference is NEVER evolved — it is read
    from the memorized template (G-M4's inside-consistency, by construction)."""
    K = len(cycle)
    W = W_FACTOR * K
    window = ring_window(cycle)
    template = limit_cycle_phases(cycle, sign)  # the memorized period
    samples = []
    for phi in range(K):
        for s in cycle:
            for sgn in (+1, -1):
                per = dict(template[phi])
                per[s] = per.get(s, 0) + sgn * mag
                if per[s] == 0:
                    del per[s]
                for t in range(1, W + 1):
                    tick_multi(per)
                    ref = template[(phi + t) % K]
                    samples.append([per.get(c, 0) - ref.get(c, 0) for c in window])
    return np.array(samples, dtype=float)


def bootstrap_m(samples, seed):
    """B_BOOT bootstrap resamples over the perturbation ensemble rows.
    Returns mean/sd for dpr_sub (decisive) and mds_dim90c (reported)."""
    rng = np.random.default_rng(seed)
    n = samples.shape[0]
    dpr, mds = [], []
    for _ in range(B_BOOT):
        o = observables(samples[rng.integers(0, n, n)])
        dpr.append(o["dpr_sub"])
        mds.append(o["mds_dim90c"])
    return {"dpr_sub_mean": float(np.mean(dpr)), "dpr_sub_sd": float(np.std(dpr)),
            "mds_mean": float(np.mean(mds)), "mds_sd": float(np.std(mds))}


def separation(a, b):
    pooled = np.sqrt((a["dpr_sub_sd"] ** 2 + b["dpr_sub_sd"] ** 2) / 2)
    if pooled == 0:
        return float("inf")
    return abs(a["dpr_sub_mean"] - b["dpr_sub_mean"]) / pooled


def main():
    t0 = time.time()
    out = {"prereg": "PREREG_phase1b.md", "B_boot": B_BOOT, "fixtures": {},
           "probes": {}, "gates": {}}

    # --- sustains audit of the frozen family ---
    print("=== frozen fixture family: sustains audit ===", flush=True)
    frozen = {"FLAT_K4": F1_K4_SQUARE, "FLAT_K6": F2_K6_PERIMETER,
              "FLAT_K8": F3_K8_RING, "CUBE_K8": CUBE_K8}
    for name, cyc in frozen.items():
        ok, msg = sustains(cyc)
        print(f"  {name}: sustains={ok} ({msg})")
        if not ok:
            raise SystemExit(f"frozen fixture {name} does not sustain — abort")

    # --- readout M on the frozen family ---
    print("\n=== readout M (memorized-template reference), bootstrap "
          f"B={B_BOOT} ===", flush=True)
    m_samples = {name: readout_m(cyc) for name, cyc in frozen.items()}
    stats = {}
    for name in frozen:
        stats[name] = bootstrap_m(m_samples[name], seed=hash(name) % (2**32))
        s = stats[name]
        print(f"  {name}: dpr_sub={s['dpr_sub_mean']:.3f}+/-{s['dpr_sub_sd']:.3f} "
              f"mds_dim90c={s['mds_mean']:.2f}+/-{s['mds_sd']:.2f} "
              f"n_rows={m_samples[name].shape[0]}", flush=True)
    # same-fixture second bootstrap set for G-M2 (independent seeds A/B)
    flat_a = bootstrap_m(m_samples["FLAT_K8"], seed=1001)
    flat_b = bootstrap_m(m_samples["FLAT_K8"], seed=2002)
    out["fixtures"] = {"stats": stats,
                       "FLAT_K8_setA": flat_a, "FLAT_K8_setB": flat_b}

    # --- gates ---
    g = {}
    z1 = separation(stats["CUBE_K8"], stats["FLAT_K8"])
    g["G_M1_z"] = z1
    g["G_M1_embedding_discrimination"] = bool(z1 >= 2.0)
    z2 = separation(flat_a, flat_b)
    g["G_M2_z"] = z2
    g["G_M2_no_self_separation"] = bool(z2 < 2.0)

    # G-M3: calibration transfer (same impulse readout as T6.3, re-verified)
    print("\n=== G-M3 calibration transfer (Phase-0 graph fixtures) ===", flush=True)
    gt = {}
    for gname, gen in (("lattice3d", lambda r: torus3d(12)),
                       ("expander6", lambda r: random_regular(1728, 6, r))):
        grng = np.random.default_rng(0)
        adj = gen(grng)
        _, taps, _ = sample_bundle(adj, 64, 6, grng)
        gt[gname] = graph_impulse_corr(adj, taps)
        print(f"  {gname}: {gt[gname]}", flush=True)
    g["G_M3_transfer_sign"] = bool(gt["expander6"]["dpr_sub"]
                                   > gt["lattice3d"]["dpr_sub"])
    g["G_M3_detail"] = {k: v["dpr_sub"] for k, v in gt.items()}
    g["G_M4_inside_consistency"] = ("by construction: memorized-template "
                                    "reference, position-free channel observables")

    g["PHASE1B_PASS"] = bool(g["G_M1_embedding_discrimination"]
                             and g["G_M2_no_self_separation"]
                             and g["G_M3_transfer_sign"])
    out["gates"] = g

    # --- period-axis context (reported, non-gating) ---
    out["period_axis"] = {k: stats[k]["dpr_sub_mean"]
                          for k in ("FLAT_K4", "FLAT_K6", "FLAT_K8")}

    # --- family-widening probes (PREREG sec. 3, non-gating) ---
    print("\n=== family-widening probes (substrate question, non-gating) ===",
          flush=True)
    probes = {}
    for name, cyc in (("RING3x3_K8", RING3x3_K8), ("ZIGZAG_K8", ZIGZAG_K8),
                      ("HEX3D_K6", HEX3D_K6)):
        ok, msg = sustains(cyc)
        probes[name] = {"sustains": bool(ok), "detail": msg}
        print(f"  {name}: sustains={ok} ({msg})")
        if ok:
            s = bootstrap_m(readout_m(cyc), seed=hash(name) % (2**32))
            probes[name]["M"] = s
            print(f"    M: dpr_sub={s['dpr_sub_mean']:.3f}+/-{s['dpr_sub_sd']:.3f}")
    # second same-K pair, if any planar K8 probe sustained
    for name in ("RING3x3_K8", "ZIGZAG_K8"):
        if probes[name]["sustains"]:
            z = separation(probes[name]["M"], stats["FLAT_K8"])
            probes[name]["z_vs_FLAT_K8"] = z
            print(f"  second-pair separation {name} vs FLAT_K8: {z:.2f} pooled-sd")
    out["probes"] = probes

    out["wall_clock_sec"] = round(time.time() - t0, 1)
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "phase1b_gate.json").write_text(
        json.dumps(out, indent=2, default=float))

    print("\n=== Phase 1b gate ===")
    print(f"  G-M1 embedding discrimination: z={g['G_M1_z']:.2f} "
          f"-> {'PASS' if g['G_M1_embedding_discrimination'] else 'FAIL'}")
    print(f"  G-M2 same-embedding control:   z={g['G_M2_z']:.2f} "
          f"-> {'PASS' if g['G_M2_no_self_separation'] else 'FAIL'}")
    print(f"  G-M3 calibration transfer:     "
          f"expander6 {gt['expander6']['dpr_sub']:.2f} vs "
          f"lattice3d {gt['lattice3d']['dpr_sub']:.2f} "
          f"-> {'PASS' if g['G_M3_transfer_sign'] else 'FAIL'}")
    print(f"\nPHASE1B_PASS = {g['PHASE1B_PASS']}")
    print(f"wall clock: {out['wall_clock_sec']}s")


if __name__ == "__main__":
    main()
