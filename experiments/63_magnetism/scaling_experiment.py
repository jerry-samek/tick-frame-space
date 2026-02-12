"""
Scaling Experiment: Resolution and Entity Density
==================================================
Tests whether transport anisotropy signal survives at larger grids
and higher entity density, or if it's lattice contamination.

Two axes:
  Resolution:  64x64/sp16 -> 128x128/sp32 -> 256x256/sp64 (same 4x4 entities)
  Density:     4x4/sp16   -> 8x8/sp8  (same 64x64 grid, more entities)

All runs use signed mode (the one with real magnetic signal).
"""

import sys
import time
import math
import json
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from magnetism_experiment import (
    GammaField, RotatingEntity, ProbeEntity, DIRECTIONS,
    equilibrate, run_probes, decompose_field,
    compute_net_magnetization_signed, compute_deflection_asymmetries,
    compute_conductivity_tensor, fourier_symmetry,
    W_CENTER, W_TANGENTIAL, DEFAULT_LAG, PROBE_SPEED,
    EQUILIBRATION_TICKS, PROBE_TICKS, PROBE_RECORD_INTERVAL,
)

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

CONFIGS = [
    {"name": "64x64_4x4",   "grid": 64,  "n_ent": 4, "spacing": 16, "offset": 8},
    {"name": "128x128_4x4",  "grid": 128, "n_ent": 4, "spacing": 32, "offset": 16},
    {"name": "256x256_4x4",  "grid": 256, "n_ent": 4, "spacing": 64, "offset": 32},
    {"name": "64x64_8x8",   "grid": 64,  "n_ent": 8, "spacing": 8,  "offset": 4},
]

PATTERN_NAMES = ["checkerboard", "stripe", "ferromagnetic", "antiferromagnetic"]
NUM_RUNS = 3


# ---------------------------------------------------------------------------
# Pattern and entity generation (parameterized)
# ---------------------------------------------------------------------------

def make_pattern(name, n):
    """Generate n x n omega grid for a named pattern."""
    if name == "ferromagnetic":
        return [[+1] * n for _ in range(n)]
    elif name == "checkerboard":
        return [[(+1 if (r + c) % 2 == 0 else -1) for c in range(n)] for r in range(n)]
    elif name == "antiferromagnetic":
        return [[(+1 if c % 2 == 0 else -1) for c in range(n)] for r in range(n)]
    elif name == "stripe":
        return [[(+2 if ((r // 2) + (c // 2)) % 2 == 0 else -2) for c in range(n)]
                for r in range(n)]
    raise ValueError(f"Unknown pattern: {name}")


def make_entities_cfg(pattern_name, rng, cfg):
    omega_grid = make_pattern(pattern_name, cfg["n_ent"])
    entities = []
    for row in range(cfg["n_ent"]):
        for col in range(cfg["n_ent"]):
            x = cfg["offset"] + col * cfg["spacing"]
            y = cfg["offset"] + row * cfg["spacing"]
            entities.append(RotatingEntity(x, y, omega_grid[row][col], DEFAULT_LAG,
                                           int(rng.integers(0, 8))))
    return entities


def make_probes_cfg(grid_size):
    s = grid_size
    positions = [(s * 0.25, s * 0.25), (s * 0.75, s * 0.25),
                 (s * 0.25, s * 0.75), (s * 0.75, s * 0.75)]
    velocities = [(0, +PROBE_SPEED, "N"), (+PROBE_SPEED, 0, "E"),
                  (0, -PROBE_SPEED, "S"), (-PROBE_SPEED, 0, "W")]
    probes = []
    for pi, (px, py) in enumerate(positions):
        for vx, vy, vdir in velocities:
            probes.append(ProbeEntity(px, py, vx, vy, f"P{pi}_{vdir}"))
    return probes


# ---------------------------------------------------------------------------
# Single run
# ---------------------------------------------------------------------------

def run_one(cfg, pattern_name, seed):
    rng = np.random.default_rng(seed)
    field = GammaField(cfg["grid"])
    entities = make_entities_cfg(pattern_name, rng, cfg)

    equilibrate(entities, field, EQUILIBRATION_TICKS, use_signed_tang=True)
    frozen = field.copy()

    probes = make_probes_cfg(cfg["grid"])
    run_probes(probes, frozen, PROBE_TICKS, PROBE_RECORD_INTERVAL)

    W_radial, W_tang_x, W_tang_y = decompose_field(frozen, entities)
    W_tang_mag = np.sqrt(W_tang_x**2 + W_tang_y**2)
    M_net = compute_net_magnetization_signed(frozen.tang)
    A_NS, A_EW, _ = compute_deflection_asymmetries(probes)
    sigma = compute_conductivity_tensor(probes)
    mode_power = fourier_symmetry(W_tang_mag)

    return {
        "M_net": M_net, "A_NS": A_NS, "A_EW": A_EW,
        "max_W_tang": float(np.max(W_tang_mag)),
        "mode_power": mode_power,
        "sigma": sigma.tolist(),
    }


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate(results):
    A_NSs = [r["A_NS"] for r in results]
    A_EWs = [r["A_EW"] for r in results]
    M_nets = [r["M_net"] for r in results]
    max_tangs = [r["max_W_tang"] for r in results]
    defl_mags = [math.sqrt(a**2 + e**2) for a, e in zip(A_NSs, A_EWs)]

    A_NS_mean = float(np.mean(A_NSs))
    A_EW_mean = float(np.mean(A_EWs))
    A_NS_std = float(np.std(A_NSs, ddof=1)) if len(A_NSs) > 1 else 0.0
    A_EW_std = float(np.std(A_EWs, ddof=1)) if len(A_EWs) > 1 else 0.0
    defl_mean = float(np.mean(defl_mags))
    defl_std = float(np.std(defl_mags, ddof=1)) if len(defl_mags) > 1 else 0.0

    mode_mean = {}
    for m in range(1, 9):
        mode_mean[m] = float(np.mean([r["mode_power"][m] for r in results]))

    sigma_mean = np.mean([np.array(r["sigma"]) for r in results], axis=0)

    return {
        "M_net_mean": float(np.mean(M_nets)),
        "A_NS_mean": A_NS_mean, "A_NS_std": A_NS_std,
        "A_EW_mean": A_EW_mean, "A_EW_std": A_EW_std,
        "defl_mean": defl_mean, "defl_std": defl_std,
        "max_W_tang_mean": float(np.mean(max_tangs)),
        "mode_power": mode_mean,
        "sigma_mean": sigma_mean.tolist(),
        "snr_NS": abs(A_NS_mean) / A_NS_std if A_NS_std > 1e-15 else float("inf"),
        "snr_EW": abs(A_EW_mean) / A_EW_std if A_EW_std > 1e-15 else float("inf"),
        "snr_defl": defl_mean / defl_std if defl_std > 1e-15 else float("inf"),
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_summary(all_agg):
    """Print comparison table to stdout."""
    print("\n" + "=" * 90)
    print("SCALING SUMMARY — Signed Mode")
    print("=" * 90)

    # Transport anisotropy table
    print("\n--- Transport Anisotropy (altermagnetic candidates) ---")
    print(f"{'Config':<18} {'Pattern':<16} {'|A_NS|':>8} {'std':>8} {'|A_EW|':>8} "
          f"{'std':>8} {'|defl|':>8} {'std':>8} {'SNR':>6}")
    print("-" * 90)
    for cfg_name in [c["name"] for c in CONFIGS]:
        for pat in ["checkerboard", "stripe"]:
            a = all_agg[cfg_name][pat]
            print(f"{cfg_name:<18} {pat:<16} {abs(a['A_NS_mean']):8.4f} {a['A_NS_std']:8.4f} "
                  f"{abs(a['A_EW_mean']):8.4f} {a['A_EW_std']:8.4f} "
                  f"{a['defl_mean']:8.4f} {a['defl_std']:8.4f} {a['snr_defl']:6.2f}")

    # M_net table (should be ~0 for non-ferro, huge for ferro)
    print("\n--- M_net (compensated magnetism check) ---")
    print(f"{'Config':<18} {'checker':>12} {'stripe':>12} {'ferro':>12} {'antiferro':>12}")
    print("-" * 70)
    for cfg_name in [c["name"] for c in CONFIGS]:
        vals = [all_agg[cfg_name][p]["M_net_mean"] for p in PATTERN_NAMES]
        print(f"{cfg_name:<18} {vals[0]:12.2e} {vals[1]:12.2e} {vals[2]:12.1f} {vals[3]:12.2e}")

    # Fourier modes (for checker and stripe)
    print("\n--- Dominant Fourier Modes (tangential gradient) ---")
    print(f"{'Config':<18} {'Pattern':<16} {'m=1':>6} {'m=2':>6} {'m=4':>6} "
          f"{'m=6':>6} {'m=8':>6} {'dom':>4}")
    print("-" * 80)
    for cfg_name in [c["name"] for c in CONFIGS]:
        for pat in ["checkerboard", "stripe", "antiferromagnetic"]:
            mp = all_agg[cfg_name][pat]["mode_power"]
            dom = max(mp, key=mp.get)
            print(f"{cfg_name:<18} {pat:<16} {mp[1]:6.3f} {mp[2]:6.3f} {mp[4]:6.3f} "
                  f"{mp[6]:6.3f} {mp[8]:6.3f}  m={dom}")

    # Conductivity tensor off-diagonal comparison
    print("\n--- Off-Diagonal Conductivity (sigma_xy) ---")
    print(f"{'Config':<18} {'checker':>10} {'stripe':>10} {'ferro':>10} {'antiferro':>10}")
    print("-" * 60)
    for cfg_name in [c["name"] for c in CONFIGS]:
        vals = [all_agg[cfg_name][p]["sigma_mean"][0][1] for p in PATTERN_NAMES]
        print(f"{cfg_name:<18} {vals[0]:10.4f} {vals[1]:10.4f} {vals[2]:10.4f} {vals[3]:10.4f}")


def save_markdown(all_agg):
    """Save results as markdown report."""
    lines = [
        "# Scaling Experiment Results",
        "",
        f"**Date**: {time.strftime('%Y-%m-%d')}",
        f"**Mode**: signed only",
        f"**Parameters**: eq={EQUILIBRATION_TICKS}, probe={PROBE_TICKS}, "
        f"runs={NUM_RUNS}, speed={PROBE_SPEED}",
        "",
        "## Configurations",
        "",
        "| Config | Grid | Entities | Spacing | Purpose |",
        "|--------|------|----------|---------|---------|",
        "| 64x64_4x4 | 64x64 | 4x4 (16) | 16 | Baseline |",
        "| 128x128_4x4 | 128x128 | 4x4 (16) | 32 | 2x resolution |",
        "| 256x256_4x4 | 256x256 | 4x4 (16) | 64 | 4x resolution |",
        "| 64x64_8x8 | 64x64 | 8x8 (64) | 8 | 4x entity density |",
        "",
        "## Transport Anisotropy — Signal vs Noise",
        "",
        "| Config | Pattern | |A_NS| | std | |A_EW| | std | |defl| | std | SNR |",
        "|--------|---------|--------|-----|--------|-----|-------|-----|-----|",
    ]

    for cfg_name in [c["name"] for c in CONFIGS]:
        for pat in ["checkerboard", "stripe"]:
            a = all_agg[cfg_name][pat]
            lines.append(
                f"| {cfg_name} | {pat} | {abs(a['A_NS_mean']):.4f} | {a['A_NS_std']:.4f} | "
                f"{abs(a['A_EW_mean']):.4f} | {a['A_EW_std']:.4f} | "
                f"{a['defl_mean']:.4f} | {a['defl_std']:.4f} | {a['snr_defl']:.2f} |"
            )

    lines += [
        "",
        "SNR = |mean deflection| / std(deflection). Higher = cleaner signal.",
        "If SNR increases with resolution, the physics is real.",
        "If SNR stays flat or decreases, it's lattice noise.",
        "",
        "## M_net (Compensated Magnetism)",
        "",
        "| Config | Checkerboard | Stripe | Ferromagnetic | Antiferromagnetic |",
        "|--------|-------------|--------|---------------|-------------------|",
    ]
    for cfg_name in [c["name"] for c in CONFIGS]:
        vals = [all_agg[cfg_name][p]["M_net_mean"] for p in PATTERN_NAMES]
        lines.append(f"| {cfg_name} | {vals[0]:.2e} | {vals[1]:.2e} | "
                     f"{vals[2]:.1f} | {vals[3]:.2e} |")

    lines += [
        "",
        "## Fourier Angular Modes",
        "",
        "| Config | Pattern | m=1 | m=2 | m=4 | m=6 | m=8 | Dominant |",
        "|--------|---------|-----|-----|-----|-----|-----|----------|",
    ]
    for cfg_name in [c["name"] for c in CONFIGS]:
        for pat in ["checkerboard", "stripe", "antiferromagnetic"]:
            mp = all_agg[cfg_name][pat]["mode_power"]
            dom = max(mp, key=mp.get)
            lines.append(
                f"| {cfg_name} | {pat} | {mp[1]:.3f} | {mp[2]:.3f} | {mp[4]:.3f} | "
                f"{mp[6]:.3f} | {mp[8]:.3f} | m={dom} |"
            )

    lines += [
        "",
        "## Off-Diagonal Conductivity (sigma_xy)",
        "",
        "| Config | Checkerboard | Stripe | Ferromagnetic | Antiferromagnetic |",
        "|--------|-------------|--------|---------------|-------------------|",
    ]
    for cfg_name in [c["name"] for c in CONFIGS]:
        vals = [all_agg[cfg_name][p]["sigma_mean"][0][1] for p in PATTERN_NAMES]
        lines.append(f"| {cfg_name} | {vals[0]:.4f} | {vals[1]:.4f} | "
                     f"{vals[2]:.4f} | {vals[3]:.4f} |")

    path = RESULTS_DIR / "scaling_results.md"
    path.write_text("\n".join(lines))
    print(f"\nMarkdown saved to: {path}")


def plot_comparison(all_agg):
    """Generate comparison plots across configurations."""
    config_names = [c["name"] for c in CONFIGS]
    n_cfg = len(config_names)
    x = np.arange(n_cfg)

    # --- Plot 1: SNR comparison for checker and stripe ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Scaling: Transport Anisotropy Signal-to-Noise", fontsize=14)

    width = 0.35
    for ax_idx, (metric, label) in enumerate([
        ("snr_defl", "SNR (|deflection|)"),
        ("snr_NS", "SNR (A_NS)"),
        ("snr_EW", "SNR (A_EW)"),
    ]):
        checker_vals = [all_agg[c]["checkerboard"][metric] for c in config_names]
        stripe_vals = [all_agg[c]["stripe"][metric] for c in config_names]
        # Cap inf for plotting
        checker_vals = [min(v, 100) for v in checker_vals]
        stripe_vals = [min(v, 100) for v in stripe_vals]

        axes[ax_idx].bar(x - width / 2, checker_vals, width, label="checkerboard",
                         color="#3498db", edgecolor="black")
        axes[ax_idx].bar(x + width / 2, stripe_vals, width, label="stripe",
                         color="#e74c3c", edgecolor="black")
        axes[ax_idx].set_ylabel(label)
        axes[ax_idx].set_xticks(x)
        axes[ax_idx].set_xticklabels(config_names, rotation=30, ha="right", fontsize=8)
        axes[ax_idx].legend(fontsize=8)
        axes[ax_idx].axhline(y=1.0, color="gray", linestyle="--", alpha=0.5, label="SNR=1")

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "scaling_snr.png", dpi=150)
    plt.close(fig)

    # --- Plot 2: Deflection magnitude across configs ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Scaling: Deflection Magnitude", fontsize=14)

    for ax_idx, pat in enumerate(["checkerboard", "stripe"]):
        means = [all_agg[c][pat]["defl_mean"] for c in config_names]
        stds = [all_agg[c][pat]["defl_std"] for c in config_names]
        axes[ax_idx].bar(x, means, 0.6, yerr=stds, capsize=5,
                         color="#2ecc71", edgecolor="black")
        axes[ax_idx].set_ylabel("|Deflection|")
        axes[ax_idx].set_title(pat)
        axes[ax_idx].set_xticks(x)
        axes[ax_idx].set_xticklabels(config_names, rotation=30, ha="right", fontsize=8)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "scaling_deflection.png", dpi=150)
    plt.close(fig)

    # --- Plot 3: Fourier mode comparison ---
    fig, axes = plt.subplots(2, len(CONFIGS), figsize=(5 * n_cfg, 8))
    fig.suptitle("Scaling: Fourier Angular Modes", fontsize=14)
    modes = list(range(1, 9))

    for ci, cfg_name in enumerate(config_names):
        for ri, pat in enumerate(["checkerboard", "stripe"]):
            mp = all_agg[cfg_name][pat]["mode_power"]
            powers = [mp[m] for m in modes]
            ax = axes[ri, ci] if n_cfg > 1 else axes[ri]
            ax.bar(modes, powers, color="steelblue", edgecolor="black")
            ax.set_title(f"{cfg_name}\n{pat}", fontsize=9)
            ax.set_xticks(modes)
            ax.set_ylim(0, 0.7)
            if ci == 0:
                ax.set_ylabel("Normalized Power")
            if ri == 1:
                ax.set_xlabel("Angular Mode m")

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "scaling_fourier.png", dpi=150)
    plt.close(fig)

    print("Plots saved.")


def save_json(all_agg):
    """Save raw aggregated data as JSON."""
    # Convert any numpy types to Python types for JSON serialization
    def clean(obj):
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {str(k): clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj

    path = RESULTS_DIR / "scaling_results.json"
    path.write_text(json.dumps(clean(all_agg), indent=2))
    print(f"JSON saved to: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("SCALING EXPERIMENT — Resolution and Entity Density")
    print("=" * 70)
    print(f"Mode: signed only")
    print(f"eq_ticks={EQUILIBRATION_TICKS}, probe_ticks={PROBE_TICKS}")
    print(f"Runs per (config, pattern): {NUM_RUNS}")
    print()

    all_results = {}  # {config_name: {pattern: [run_dicts]}}
    t_start = time.time()

    for cfg in CONFIGS:
        name = cfg["name"]
        n_total = cfg["n_ent"] ** 2
        print(f"\n{'='*60}")
        print(f"CONFIG: {name} (grid={cfg['grid']}, {cfg['n_ent']}x{cfg['n_ent']}="
              f"{n_total} entities, spacing={cfg['spacing']})")
        print(f"{'='*60}")

        all_results[name] = {}

        for pat in PATTERN_NAMES:
            results = []
            for run_idx in range(NUM_RUNS):
                seed = 1000 * PATTERN_NAMES.index(pat) + run_idx
                t0 = time.time()
                r = run_one(cfg, pat, seed)
                dt = time.time() - t0
                print(f"  {pat:20s} run {run_idx+1}/{NUM_RUNS} ({dt:.1f}s): "
                      f"M_net={r['M_net']:.2e}, A_NS={r['A_NS']:+.4f}, "
                      f"A_EW={r['A_EW']:+.4f}")
                results.append(r)
            all_results[name][pat] = results

    elapsed = time.time() - t_start
    print(f"\nTotal time: {elapsed:.0f}s ({elapsed/60:.1f} min)")

    # Aggregate
    all_agg = {}
    for cfg_name, patterns in all_results.items():
        all_agg[cfg_name] = {}
        for pat, runs in patterns.items():
            all_agg[cfg_name][pat] = aggregate(runs)

    # Report
    print_summary(all_agg)
    save_markdown(all_agg)
    save_json(all_agg)
    plot_comparison(all_agg)


if __name__ == "__main__":
    main()
