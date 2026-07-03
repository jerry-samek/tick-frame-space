"""Exp 137 Phase 0b — skeptic-mandated deconfounding controls (T1, T2, T4, +A3 fix).

Run AFTER the skeptic review of Phase 0. The charitable null under test:
"the instrument is a correlation-amplitude meter (degree meter), not a
geometry reader."

T1: degree-matched expanders — random 6-regular (vs lattice3d, deg 6) and
    random 4-regular (vs lattice2d, deg 4).
    null: collapse with the matched lattice; geometry: separation.
T2: 2D Moore torus (deg 8) vs 3D von Neumann torus (deg 6).
    Opposite-sign predictions: geometry -> moore2d reads BELOW lattice3d;
    amplitude-null -> moore2d (higher degree, weaker r) reads ABOVE lattice3d.
T4: geometry-destroyed baselines on lattice3d — (i) taps uniform over the
    whole graph instead of one ball; (ii) per-channel independent time
    shuffle of the recorded series (destroys all cross-correlation).
A3 fix: continuous MDS observable mds_dim90c (linear interpolation of the
    90%-mass crossing) reported alongside the integer mds_dim90.
"""

import json
import time
from pathlib import Path

import numpy as np

from graphs import torus3d, torus2d, random_regular, bfs_distances, sample_bundle
from dynamics import run_ar1
from readout import corrmat, dpr_raw, dpr_sub, mds_dim90, corr_decay

LAM, BURN, STEPS = 0.99, 1000, 20000  # frozen Phase 0 (retuned) settings
N_TAP, RADIUS = 64, 6
SEEDS = range(10)


def moore2d(L=42):
    """2D torus with Moore (8-neighbor) connectivity."""
    n = L * L
    adj = [[] for _ in range(n)]
    for x in range(L):
        for y in range(L):
            i = x + L * y
            for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
                j = ((x + dx) % L) + L * ((y + dy) % L)
                adj[i].append(j)
                adj[j].append(i)
    return adj


def mds_dim90c(c):
    """Continuous 90%-mass MDS dimension (A3 fix: interpolated crossing)."""
    d = np.sqrt(np.clip(2.0 * (1.0 - c), 0.0, None))
    np.fill_diagonal(d, 0.0)
    n = d.shape[0]
    j = np.eye(n) - np.ones((n, n)) / n
    b = -0.5 * j @ (d * d) @ j
    e = np.sort(np.linalg.eigvalsh(b))[::-1]
    pos = e[e > 0]
    if pos.size == 0:
        return 0.0
    frac = np.cumsum(pos) / np.sum(pos)
    k = int(np.searchsorted(frac, 0.9))
    if k == 0:
        return float(0.9 / frac[0])
    return float(k + (0.9 - frac[k - 1]) / (frac[k] - frac[k - 1]))


FIXTURES = {
    "lattice3d": lambda rng: torus3d(12),           # reference, deg 6
    "expander6": lambda rng: random_regular(1728, 6, rng),   # T1 match for lattice3d
    "lattice2d": lambda rng: torus2d(42),           # reference, deg 4
    "expander4": lambda rng: random_regular(1764, 4, rng),   # T1 match for lattice2d
    "moore2d": lambda rng: moore2d(42),             # T2, deg 8
}


def observe(c):
    return {"dpr_raw": dpr_raw(c), "dpr_sub": dpr_sub(c),
            "mds_dim90": mds_dim90(c), "mds_dim90c": mds_dim90c(c)}


def run_fixture(name, seed, taps_mode="ball", shuffle=False):
    rng = np.random.default_rng(seed)
    adj = FIXTURES[name](rng)
    if taps_mode == "ball":
        center, taps, _ = sample_bundle(adj, N_TAP, RADIUS, rng)
    else:  # T4(i): uniform taps, geometry of the bundle destroyed
        taps = np.sort(rng.choice(len(adj), size=N_TAP, replace=False))
    x = run_ar1(adj, taps, lam=LAM, burn=BURN, steps=STEPS, rng=rng)
    if shuffle:  # T4(ii): independent time-permutation per channel
        for k in range(x.shape[1]):
            rng.shuffle(x[:, k])
    c = corrmat(x)
    r = observe(c)
    if taps_mode == "ball" and not shuffle:
        dist = {int(t): bfs_distances(adj, int(t), cutoff=RADIUS) for t in taps}
        r["corr_d1"], r["corr_d6"] = corr_decay(c, taps, dist)
    return r


def agg(rows):
    out = {}
    for key in rows[0]:
        v = np.array([r[key] for r in rows], dtype=float)
        out[key] = (float(np.nanmean(v)), float(np.nanstd(v)))
    return out


def sep(stats, a, b, obs):
    """Separation in pooled-sd units (continuous observables only)."""
    ma, sa = stats[a][obs]
    mb, sb = stats[b][obs]
    pooled = np.sqrt((sa**2 + sb**2) / 2)
    return abs(ma - mb) / pooled if pooled > 0 else float("inf")


def main():
    t0 = time.time()
    raw, stats = {}, {}
    jobs = [(n, "ball", False) for n in FIXTURES]
    jobs += [("lattice3d", "uniform", False), ("lattice3d", "ball", True)]
    for name, mode, shuf in jobs:
        label = name if (mode == "ball" and not shuf) else (
            f"{name}_uniformtaps" if mode == "uniform" else f"{name}_shuffled")
        rows = []
        for seed in SEEDS:
            r = run_fixture(name, seed, taps_mode=mode, shuffle=shuf)
            rows.append(r)
            print(f"  {label} seed={seed}: " + ", ".join(
                f"{k}={v:.3f}" for k, v in r.items()), flush=True)
        raw[label], stats[label] = rows, agg(rows)

    verdicts = {
        # T1: geometry predicts separation (>=2 pooled sd on dpr_sub or mds_dim90c);
        #     amplitude-null predicts collapse (<2)
        "T1_expander6_vs_lattice3d_sd": max(
            sep(stats, "expander6", "lattice3d", "dpr_sub"),
            sep(stats, "expander6", "lattice3d", "mds_dim90c")),
        "T1_expander4_vs_lattice2d_sd": max(
            sep(stats, "expander4", "lattice2d", "dpr_sub"),
            sep(stats, "expander4", "lattice2d", "mds_dim90c")),
        # T2: sign of (moore2d - lattice3d); geometry -> negative, null -> positive
        "T2_moore2d_minus_lattice3d_dpr_sub":
            stats["moore2d"]["dpr_sub"][0] - stats["lattice3d"]["dpr_sub"][0],
        "T2_moore2d_minus_lattice3d_mds_dim90c":
            stats["moore2d"]["mds_dim90c"][0] - stats["lattice3d"]["mds_dim90c"][0],
        # T4: distance of destroyed baselines from the intact lattice3d reading
        "T4_uniformtaps_dpr_sub": stats["lattice3d_uniformtaps"]["dpr_sub"][0],
        "T4_shuffled_dpr_sub": stats["lattice3d_shuffled"]["dpr_sub"][0],
        "lattice3d_dpr_sub": stats["lattice3d"]["dpr_sub"][0],
    }

    out = {"stats": stats, "verdicts": verdicts, "raw": raw,
           "wall_clock_sec": round(time.time() - t0, 1)}
    outdir = Path(__file__).parent / "results"
    outdir.mkdir(exist_ok=True)
    (outdir / "phase0b_deconfound.json").write_text(json.dumps(out, indent=2))

    print("\n=== Exp 137 Phase 0b (deconfound) — mean +/- sd, 10 seeds ===")
    for label, s in stats.items():
        line = f"{label:<24}"
        for key in ("dpr_raw", "dpr_sub", "mds_dim90", "mds_dim90c"):
            line += f"{s[key][0]:>9.2f}+/-{s[key][1]:<5.2f}"
        if "corr_d1" in s:
            line += f"  d1/d6={s['corr_d1'][0]:.3f}/{s['corr_d6'][0]:.3f}"
        print(line)
    print("\nverdicts:", json.dumps(verdicts, indent=2))


if __name__ == "__main__":
    main()
