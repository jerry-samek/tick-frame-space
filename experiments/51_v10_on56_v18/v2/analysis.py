"""
Post-run analysis and plotting for V18.1 orbital dynamics experiment.

Extends V1 analysis with:
- Log-log gamma profile with power law fit
- Gamma conservation over time plot
- Updated titles for V18.1

Usage:
    python analysis.py results/orbital_sl5_spread_sign_p200.json

Date: February 2026
"""

import json
import math
import argparse
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Import core analysis functions from v1
import sys
import importlib.util
_v1_analysis_path = str(Path(__file__).resolve().parent.parent / "v1" / "analysis.py")
_spec = importlib.util.spec_from_file_location("v1_analysis", _v1_analysis_path)
_v1_analysis = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1_analysis)

classify_trajectory = _v1_analysis.classify_trajectory
count_revolutions = _v1_analysis.count_revolutions
compute_eccentricity = _v1_analysis.compute_eccentricity
compute_angular_momentum = _v1_analysis.compute_angular_momentum
estimate_orbital_period = _v1_analysis.estimate_orbital_period
TrajectoryClassification = _v1_analysis.TrajectoryClassification


# ============================================================================
# New V18.1 plots
# ============================================================================

def plot_gamma_profile_loglog(gamma_profile, output_dir):
    """Log-log scatter of gamma(r) vs r with power law fit.

    Fits gamma ~ r^(-n) using np.polyfit on log-log data.
    Reports fitted exponent n (target: n ~ 1.0 for 1/r).
    """
    radii = sorted([int(k) for k in gamma_profile.keys()])
    values = [gamma_profile[str(r)] for r in radii]

    # Filter to r > 0 and gamma > 0 for log-log
    log_r = []
    log_g = []
    for r, g in zip(radii, values):
        if r > 0 and g > 0:
            log_r.append(np.log10(r))
            log_g.append(np.log10(g))

    fig, ax = plt.subplots(figsize=(10, 6))

    if log_r:
        ax.scatter(log_r, log_g, s=15, alpha=0.7, color="steelblue", label="Data")

        # Power law fit: log(gamma) = -n * log(r) + c
        # Use r >= 3 for fit (exclude near-origin pile)
        fit_mask = [r >= np.log10(3) for r in log_r]
        fit_r = [r for r, m in zip(log_r, fit_mask) if m]
        fit_g = [g for g, m in zip(log_g, fit_mask) if m]

        if len(fit_r) >= 3:
            coeffs = np.polyfit(fit_r, fit_g, 1)
            exponent = -coeffs[0]  # gamma ~ r^(-n), so slope = -n
            fit_line = np.poly1d(coeffs)
            r_range = np.linspace(min(fit_r), max(fit_r), 100)
            ax.plot(r_range, fit_line(r_range), "r--", linewidth=2,
                    label=f"Fit: n = {exponent:.2f} (gamma ~ r^{{-{exponent:.2f}}})")

            ax.set_title(f"V18.1 Gamma Profile (log-log) — Power Law Exponent n = {exponent:.2f}")
        else:
            ax.set_title("V18.1 Gamma Profile (log-log) — Insufficient data for fit")
    else:
        ax.set_title("V18.1 Gamma Profile (log-log) — No data")

    ax.set_xlabel("log10(r)")
    ax.set_ylabel("log10(gamma)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "gamma_profile_loglog.png", dpi=150)
    plt.close(fig)
    print("  Saved gamma_profile_loglog.png")


def plot_gamma_conservation(gamma_history, output_dir):
    """Plot total gamma over time — should be flat if conservation holds."""
    if not gamma_history:
        print("  No gamma history data, skipping conservation plot")
        return

    ticks = [h["tick"] for h in gamma_history]
    gammas = [h["total_gamma"] for h in gamma_history]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Absolute
    ax1.plot(ticks, gammas, "o-", color="steelblue", markersize=3)
    ax1.set_xlabel("Tick")
    ax1.set_ylabel("Total gamma")
    ax1.set_title("V18.1 Total Gamma Over Time")
    ax1.grid(True, alpha=0.3)

    # Relative deviation from initial
    if gammas[0] > 0:
        relative = [(g - gammas[0]) / gammas[0] * 100 for g in gammas]
        ax2.plot(ticks, relative, "o-", color="red", markersize=3)
        ax2.set_xlabel("Tick")
        ax2.set_ylabel("Deviation from initial (%)")
        ax2.set_title("Gamma Conservation — Relative Deviation")
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color="gray", linestyle="--", alpha=0.5)

    fig.tight_layout()
    fig.savefig(output_dir / "gamma_conservation.png", dpi=150)
    plt.close(fig)
    print("  Saved gamma_conservation.png")


# ============================================================================
# Updated V1 plots with V18.1 labels
# ============================================================================

def plot_gamma_profile(gamma_profile, output_dir):
    """Bar chart of gamma vs distance after planet formation."""
    radii = sorted([int(k) for k in gamma_profile.keys()])
    values = [gamma_profile[str(r)] for r in radii]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(radii, values, color="steelblue", alpha=0.8)
    ax.set_xlabel("Distance from origin")
    ax.set_ylabel("Total gamma in shell")
    ax.set_title("V18.1 Gamma Radial Profile After Planet Formation")
    if radii:
        ax.set_xlim(-0.5, min(max(radii) + 0.5, 80))
    fig.tight_layout()
    fig.savefig(output_dir / "gamma_profile.png", dpi=150)
    plt.close(fig)
    print("  Saved gamma_profile.png")


def plot_gradient_vs_distance(gradient_analysis, output_dir):
    """Gradient magnitude vs distance — standard and smoothed."""
    distances = [g["distance"] for g in gradient_analysis]
    standard = [g["standard_gradient_mag"] for g in gradient_analysis]
    smoothed = [g["smoothed_gradient_mag"] for g in gradient_analysis]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(distances, standard, "o-", label="Standard gradient (pos+-1)", color="blue")
    ax.plot(distances, smoothed, "s-", label="Smoothed gradient (r=30)", color="red")
    ax.set_xlabel("Distance from origin")
    ax.set_ylabel("Gradient magnitude")
    ax.set_title("V18.1 Gradient Magnitude vs Distance")
    ax.legend()

    all_vals = [v for v in standard + smoothed if v > 0]
    if all_vals and max(all_vals) / max(min(all_vals), 1e-10) > 100:
        ax.set_yscale("symlog", linthresh=1e-6)

    fig.tight_layout()
    fig.savefig(output_dir / "gradient_vs_distance.png", dpi=150)
    plt.close(fig)
    print("  Saved gradient_vs_distance.png")


def plot_trajectories_xy(approach_a, output_dir):
    """X-Y trajectories for all Approach A test processes."""
    fig, ax = plt.subplots(figsize=(10, 10))

    circle = plt.Circle((0, 0), 5, color="gray", alpha=0.2, label="Planet region")
    ax.add_patch(circle)

    colors = plt.cm.tab10(np.linspace(0, 1, max(len(approach_a), 1)))
    for i, (label, data) in enumerate(approach_a.items()):
        points = data["trajectory"]
        xs = [p["position"][0] for p in points]
        ys = [p["position"][1] for p in points]
        zs = [p["position"][2] for p in points]

        # Check if this is an out-of-plane process (T5)
        has_z = any(z != 0 for z in zs)
        plot_label = f"{label} (z-motion)" if has_z else label

        ax.plot(xs, ys, "-", color=colors[i], alpha=0.7, linewidth=0.5, label=plot_label)
        if xs:
            ax.plot(xs[0], ys[0], "o", color=colors[i], markersize=8)
            ax.plot(xs[-1], ys[-1], "x", color=colors[i], markersize=8)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("V18.1 Approach A: X-Y Trajectories")
    ax.set_aspect("equal")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "trajectories_xy.png", dpi=150)
    plt.close(fig)
    print("  Saved trajectories_xy.png")


def plot_radial_distance(approach_a, output_dir):
    """r(t) curves — THE key diagnostic plot."""
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = plt.cm.tab10(np.linspace(0, 1, max(len(approach_a), 1)))
    for i, (label, data) in enumerate(approach_a.items()):
        points = data["trajectory"]
        ticks = [p["tick"] for p in points]
        rs = [p["r"] for p in points]
        ax.plot(ticks, rs, "-", color=colors[i], alpha=0.8, label=label)

    ax.set_xlabel("Tick")
    ax.set_ylabel("Distance from origin")
    ax.set_title("V18.1 Approach A: Radial Distance r(t)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "radial_distance.png", dpi=150)
    plt.close(fig)
    print("  Saved radial_distance.png")


def plot_angular_momentum(approach_a, output_dir):
    """Angular momentum L(t) conservation check."""
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = plt.cm.tab10(np.linspace(0, 1, max(len(approach_a), 1)))
    for i, (label, data) in enumerate(approach_a.items()):
        points = data["trajectory"]
        ticks = [p["tick"] for p in points]
        positions = [p["position"] for p in points]
        velocities = [p["velocity"] for p in points]
        L = compute_angular_momentum(positions, velocities)
        ax.plot(ticks, L, "-", color=colors[i], alpha=0.8, label=label)

    ax.set_xlabel("Tick")
    ax.set_ylabel("Angular momentum L_z = x*vy - y*vx")
    ax.set_title("V18.1 Approach A: Angular Momentum Conservation")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "angular_momentum.png", dpi=150)
    plt.close(fig)
    print("  Saved angular_momentum.png")


def plot_approach_b_histogram(approach_b, config, output_dir):
    """Final distance distribution by initial ring for Approach B."""
    if not approach_b:
        return

    radii = config.get("approach_b_radii", [20, 30, 50])
    per_ring = config.get("approach_b_per_ring", 10)

    fig, ax = plt.subplots(figsize=(10, 5))
    all_data = []
    labels = []

    entries = list(approach_b.values())
    idx = 0
    for r in radii:
        ring_distances = []
        for _ in range(per_ring):
            if idx < len(entries):
                ring_distances.append(entries[idx]["final_distance"])
                idx += 1
        if ring_distances:
            all_data.append(ring_distances)
            labels.append(f"r={r}")

    if all_data:
        ax.boxplot(all_data, tick_labels=labels)
        ax.axhline(y=0, color="red", linestyle="--", alpha=0.3, label="Origin")
        for i, r in enumerate(radii):
            ax.axhline(y=r, color="gray", linestyle=":", alpha=0.3)
        ax.set_ylabel("Final distance from origin")
        ax.set_title("V18.1 Approach B: Final Distance by Initial Ring")
        ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_dir / "approach_b_histogram.png", dpi=150)
    plt.close(fig)
    print("  Saved approach_b_histogram.png")


def plot_summary_dashboard(
    approach_a,
    gamma_profile,
    gradient_analysis,
    classifications,
    output_dir,
):
    """Multi-panel composite summary figure."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    # Panel 1: Gamma profile
    ax = axes[0, 0]
    radii = sorted([int(k) for k in gamma_profile.keys()])
    values = [gamma_profile[str(r)] for r in radii]
    ax.bar(radii[:40], values[:40], color="steelblue", alpha=0.8)
    ax.set_xlabel("r")
    ax.set_ylabel("gamma")
    ax.set_title("Gamma Profile")

    # Panel 2: Gradient vs distance
    ax = axes[0, 1]
    if gradient_analysis:
        distances = [g["distance"] for g in gradient_analysis]
        standard = [g["standard_gradient_mag"] for g in gradient_analysis]
        smoothed = [g["smoothed_gradient_mag"] for g in gradient_analysis]
        ax.semilogy(
            distances,
            [max(s, 1e-10) for s in standard],
            "o-", label="Standard",
        )
        ax.semilogy(
            distances,
            [max(s, 1e-10) for s in smoothed],
            "s-", label="Smoothed",
        )
        ax.legend(fontsize=8)
    ax.set_xlabel("r")
    ax.set_ylabel("|grad|")
    ax.set_title("Gradient vs Distance")

    # Panel 3: X-Y trajectories
    ax = axes[0, 2]
    circle = plt.Circle((0, 0), 5, color="gray", alpha=0.2)
    ax.add_patch(circle)
    colors = plt.cm.tab10(np.linspace(0, 1, max(len(approach_a), 1)))
    for i, (label, data) in enumerate(approach_a.items()):
        points = data["trajectory"]
        xs = [p["position"][0] for p in points]
        ys = [p["position"][1] for p in points]
        ax.plot(xs, ys, "-", color=colors[i], alpha=0.5, linewidth=0.3, label=label)
    ax.set_aspect("equal")
    ax.legend(fontsize=7, loc="upper right")
    ax.set_title("X-Y Trajectories")

    # Panel 4: r(t) curves
    ax = axes[1, 0]
    for i, (label, data) in enumerate(approach_a.items()):
        points = data["trajectory"]
        ticks = [p["tick"] for p in points]
        rs = [p["r"] for p in points]
        ax.plot(ticks, rs, "-", color=colors[i], alpha=0.8, label=label)
    ax.set_xlabel("Tick")
    ax.set_ylabel("r")
    ax.set_title("Radial Distance r(t)")
    ax.legend(fontsize=7)

    # Panel 5: Angular momentum
    ax = axes[1, 1]
    for i, (label, data) in enumerate(approach_a.items()):
        points = data["trajectory"]
        ticks = [p["tick"] for p in points]
        positions = [p["position"] for p in points]
        velocities = [p["velocity"] for p in points]
        L = compute_angular_momentum(positions, velocities)
        ax.plot(ticks, L, "-", color=colors[i], alpha=0.8, label=label)
    ax.set_xlabel("Tick")
    ax.set_ylabel("L_z")
    ax.set_title("Angular Momentum")
    ax.legend(fontsize=7)

    # Panel 6: Classification summary table
    ax = axes[1, 2]
    ax.axis("off")
    if classifications:
        table_data = []
        for c in classifications:
            table_data.append([
                c.label,
                c.classification,
                f"{c.r_mean:.1f}",
                f"{c.eccentricity:.3f}",
                f"{c.revolutions:.1f}",
                c.trend,
            ])
        table = ax.table(
            cellText=table_data,
            colLabels=["Label", "Class", "r_mean", "ecc", "revs", "trend"],
            loc="center",
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
    ax.set_title("Classification Summary")

    fig.suptitle(
        "V18.1 Orbital Dynamics — Summary Dashboard",
        fontsize=14, fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(output_dir / "summary_dashboard.png", dpi=150)
    plt.close(fig)
    print("  Saved summary_dashboard.png")


# ============================================================================
# Main entry point
# ============================================================================

def analyze_experiment(results_path):
    """Analyze V18.1 experiment results and generate all plots.

    Args:
        results_path: Path to results JSON file

    Returns:
        List of TrajectoryClassification objects
    """
    results_path = Path(results_path)

    with open(results_path) as f:
        results = json.load(f)

    output_dir = results_path.parent
    config = results["config"]
    approach_a = results.get("approach_a", {})
    approach_b = results.get("approach_b", {})
    gamma_profile = results.get("gamma_profile", {})
    gradient_analysis = results.get("gradient_analysis", [])
    gamma_history = results.get("gamma_history", [])

    spreading = config.get("enable_spreading", True)
    accumulator = config.get("use_accumulator", False)
    version = "V18.1" if spreading else "V18 (no spreading)"
    mode = "accumulator" if accumulator else "sign-only"

    print("=" * 60)
    print(f"{version} Orbital Dynamics Analysis ({mode})")
    print("=" * 60)
    print(f"  planet_count      = {config['planet_count']}")
    print(f"  speed_limit       = {config['speed_limit']}")
    print(f"  enable_spreading  = {spreading}")
    print(f"  use_accumulator   = {accumulator}")
    print(f"  total_ticks       = {config['total_ticks']}")
    print()

    # Classify Approach A trajectories
    classifications = []
    if approach_a:
        print("--- Approach A: Trajectory Classification ---")
        print()
        for label, data in approach_a.items():
            data["label"] = label
            c = classify_trajectory(data)
            if c:
                classifications.append(c)
                print(f"  {c.label}: ** {c.classification.upper()} **")
                print(f"    r: min={c.r_min:.1f}, max={c.r_max:.1f}, "
                      f"mean={c.r_mean:.1f}, std={c.r_std:.1f}")
                print(f"    eccentricity={c.eccentricity:.3f}, "
                      f"revolutions={c.revolutions:.2f}, "
                      f"period={c.orbital_period}, trend={c.trend}")
                print(f"    L_mean={c.angular_momentum_mean:.1f}, "
                      f"L_conservation={c.angular_momentum_conservation:.3f}")
                print()

        orbit_count = sum(
            1 for c in classifications
            if c.classification in ("circular", "elliptical")
        )
        stable_count = sum(
            1 for c in classifications
            if c.classification == "stable_radius"
        )
        collapse_count = sum(
            1 for c in classifications
            if c.classification == "collapse"
        )
        print(f"  Summary: {orbit_count} orbits, {stable_count} stable, "
              f"{collapse_count} collapsed out of {len(classifications)} total")
        print(f"  V10 benchmark: 100% orbit rate (18/18), 78% circular")
        print()

    # Approach B summary
    if approach_b:
        print("--- Approach B: Pure V18 Process Distances ---")
        for pid, entry in approach_b.items():
            r0 = entry["initial_distance"]
            rf = entry["final_distance"]
            delta = rf - r0
            direction = "inward" if delta < -1 else "outward" if delta > 1 else "stable"
            print(f"  pid={pid}: r={r0:.1f} -> {rf:.1f} ({direction}, delta={delta:+.1f})")
        print()

    # Generate plots
    print("--- Generating Plots ---")
    if gamma_profile:
        plot_gamma_profile(gamma_profile, output_dir)
        plot_gamma_profile_loglog(gamma_profile, output_dir)
    if gradient_analysis:
        plot_gradient_vs_distance(gradient_analysis, output_dir)
    if gamma_history:
        plot_gamma_conservation(gamma_history, output_dir)
    if approach_a:
        plot_trajectories_xy(approach_a, output_dir)
        plot_radial_distance(approach_a, output_dir)
        plot_angular_momentum(approach_a, output_dir)
    if approach_b:
        plot_approach_b_histogram(approach_b, config, output_dir)
    if approach_a:
        plot_summary_dashboard(
            approach_a, gamma_profile, gradient_analysis,
            classifications, output_dir,
        )

    print()
    print("Analysis complete.")
    return classifications


def main():
    parser = argparse.ArgumentParser(
        description="Analyze V18.1 orbital dynamics experiment results"
    )
    parser.add_argument(
        "results", type=str,
        help="Path to results JSON file",
    )
    args = parser.parse_args()
    analyze_experiment(args.results)


if __name__ == "__main__":
    main()
