"""
Post-run analysis and plotting for V18 orbital dynamics experiment.

Classifies trajectories (circular, elliptical, collapse, escape, stable_radius,
chaotic) and generates diagnostic plots for comparison with V10 benchmarks.

Usage:
    python analysis.py results/orbital_sl1_standard_p500.json

Date: February 2026
"""

import json
import math
import argparse
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


@dataclass
class TrajectoryClassification:
    """Classification result for a single orbital trajectory."""
    label: str
    classification: str  # circular/elliptical/collapse/escape/stable_radius/chaotic
    r_min: float
    r_max: float
    r_mean: float
    r_std: float
    eccentricity: float
    revolutions: float
    orbital_period: Optional[float]
    angular_momentum_mean: float
    angular_momentum_conservation: float  # std(L) / mean(|L|), lower = better
    trend: str  # "inward", "outward", "stable"


# ============================================================================
# Core analysis functions
# ============================================================================

def count_revolutions(positions, origin=(0, 0, 0)):
    """Track cumulative angle via atan2, count 2*pi crossings.

    Args:
        positions: List of (x, y, z) positions
        origin: Center point to measure angles from

    Returns:
        Number of complete revolutions (float)
    """
    if len(positions) < 3:
        return 0.0

    cumulative_angle = 0.0
    prev_angle = math.atan2(
        positions[0][1] - origin[1],
        positions[0][0] - origin[0],
    )

    for pos in positions[1:]:
        angle = math.atan2(pos[1] - origin[1], pos[0] - origin[0])
        delta = angle - prev_angle
        # Handle wraparound
        if delta > math.pi:
            delta -= 2 * math.pi
        elif delta < -math.pi:
            delta += 2 * math.pi
        cumulative_angle += delta
        prev_angle = angle

    return abs(cumulative_angle) / (2 * math.pi)


def compute_eccentricity(distances):
    """Compute orbital eccentricity from distance time series.

    e = (r_max - r_min) / (r_max + r_min)
    e = 0 for perfect circle, e -> 1 for highly elliptical
    """
    if not distances:
        return 0.0
    r_max = max(distances)
    r_min = min(distances)
    denom = r_max + r_min
    if denom == 0:
        return 0.0
    return (r_max - r_min) / denom


def compute_angular_momentum(positions, velocities):
    """Compute L_z = x*vy - y*vx per tick.

    Args:
        positions: List of (x, y, z) positions
        velocities: List of (vx, vy, vz) velocities

    Returns:
        List of L_z values
    """
    L = []
    for pos, vel in zip(positions, velocities):
        lz = pos[0] * vel[1] - pos[1] * vel[0]
        L.append(lz)
    return L


def estimate_orbital_period(distances):
    """Estimate orbital period via autocorrelation of r(t).

    Returns the lag of the first significant autocorrelation peak,
    or None if no periodic signal is found.
    """
    if len(distances) < 20:
        return None

    r = np.array(distances, dtype=float)
    r = r - np.mean(r)
    std = np.std(r)
    if std < 1e-6:
        return None

    r = r / std
    n = len(r)
    autocorr = np.correlate(r, r, mode="full")
    autocorr = autocorr[n - 1:]  # Positive lags only
    autocorr = autocorr / autocorr[0]  # Normalize

    # Find first peak after initial decay
    for i in range(2, len(autocorr) - 1):
        if (autocorr[i] > autocorr[i - 1]
                and autocorr[i] > autocorr[i + 1]
                and autocorr[i] > 0.3):
            return float(i)

    return None


def classify_trajectory(trajectory_data, origin=(0, 0, 0)):
    """Classify a trajectory from experiment results JSON.

    Args:
        trajectory_data: Dict with "trajectory" list and "label" string
        origin: Center point for radial distance calculations

    Returns:
        TrajectoryClassification or None if trajectory is empty
    """
    points = trajectory_data["trajectory"]
    if not points:
        return None

    label = trajectory_data.get("label", "unknown")
    positions = [tuple(p["position"]) for p in points]
    velocities = [tuple(p["velocity"]) for p in points]
    distances = [p["r"] for p in points]

    # Use last 500 ticks (or all if shorter) for classification
    analysis_window = min(500, len(distances))
    recent_r = distances[-analysis_window:]
    recent_pos = positions[-analysis_window:]

    r_min = min(recent_r)
    r_max = max(recent_r)
    r_mean = float(np.mean(recent_r))
    r_std = float(np.std(recent_r))

    # Trend: compare first and last quarter of analysis window
    quarter = max(1, len(recent_r) // 4)
    first_q = float(np.mean(recent_r[:quarter]))
    last_q = float(np.mean(recent_r[-quarter:]))
    if last_q < first_q * 0.8:
        trend = "inward"
    elif last_q > first_q * 1.2:
        trend = "outward"
    else:
        trend = "stable"

    ecc = compute_eccentricity(recent_r)
    revs = count_revolutions(recent_pos, origin)
    period = estimate_orbital_period(recent_r)

    # Angular momentum analysis
    L = compute_angular_momentum(positions, velocities)
    L_recent = L[-analysis_window:]
    L_mean = float(np.mean(L_recent))
    L_abs_mean = float(np.mean([abs(l) for l in L_recent]))
    if L_abs_mean > 1e-6:
        L_conservation = float(np.std(L_recent)) / L_abs_mean
    else:
        L_conservation = float("inf")

    # Classification logic
    if r_min < 3:
        classification = "collapse"
    elif trend == "outward" and last_q > distances[0] * 2:
        classification = "escape"
    elif r_std / r_mean < 0.1 and revs >= 2:
        classification = "circular"
    elif revs >= 1.5 and ecc > 0.1:
        classification = "elliptical"
    elif trend == "stable" and r_std / r_mean < 0.3:
        classification = "stable_radius"
    else:
        classification = "chaotic"

    return TrajectoryClassification(
        label=label,
        classification=classification,
        r_min=r_min,
        r_max=r_max,
        r_mean=r_mean,
        r_std=r_std,
        eccentricity=ecc,
        revolutions=revs,
        orbital_period=period,
        angular_momentum_mean=L_mean,
        angular_momentum_conservation=L_conservation,
        trend=trend,
    )


# ============================================================================
# Plot functions
# ============================================================================

def plot_gamma_profile(gamma_profile, output_dir):
    """Bar chart of gamma vs distance after planet formation."""
    radii = sorted([int(k) for k in gamma_profile.keys()])
    values = [gamma_profile[str(r)] for r in radii]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(radii, values, color="steelblue", alpha=0.8)
    ax.set_xlabel("Distance from origin")
    ax.set_ylabel("Total gamma in shell")
    ax.set_title("Gamma Radial Profile After Planet Formation")
    if radii:
        ax.set_xlim(-0.5, min(max(radii) + 0.5, 60))
    fig.tight_layout()
    fig.savefig(output_dir / "gamma_profile.png", dpi=150)
    plt.close(fig)
    print("  Saved gamma_profile.png")


def plot_gradient_vs_distance(gradient_analysis, output_dir):
    """Gradient magnitude vs distance - standard and smoothed."""
    distances = [g["distance"] for g in gradient_analysis]
    standard = [g["standard_gradient_mag"] for g in gradient_analysis]
    smoothed = [g["smoothed_gradient_mag"] for g in gradient_analysis]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(distances, standard, "o-", label="Standard gradient (pos+-1)", color="blue")
    ax.plot(distances, smoothed, "s-", label="Smoothed gradient (r=5)", color="red")
    ax.set_xlabel("Distance from origin")
    ax.set_ylabel("Gradient magnitude")
    ax.set_title("Gradient Magnitude vs Distance")
    ax.legend()

    # Use log scale if values span orders of magnitude, but handle zeros
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

    # Shade planet region
    circle = plt.Circle((0, 0), 5, color="gray", alpha=0.2, label="Planet region")
    ax.add_patch(circle)

    colors = plt.cm.tab10(np.linspace(0, 1, max(len(approach_a), 1)))
    for i, (label, data) in enumerate(approach_a.items()):
        points = data["trajectory"]
        xs = [p["position"][0] for p in points]
        ys = [p["position"][1] for p in points]
        ax.plot(xs, ys, "-", color=colors[i], alpha=0.7, linewidth=0.5, label=label)
        # Mark start (circle) and end (X)
        if xs:
            ax.plot(xs[0], ys[0], "o", color=colors[i], markersize=8)
            ax.plot(xs[-1], ys[-1], "x", color=colors[i], markersize=8)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Approach A: X-Y Trajectories")
    ax.set_aspect("equal")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "trajectories_xy.png", dpi=150)
    plt.close(fig)
    print("  Saved trajectories_xy.png")


def plot_radial_distance(approach_a, output_dir):
    """r(t) curves - THE key diagnostic plot."""
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = plt.cm.tab10(np.linspace(0, 1, max(len(approach_a), 1)))
    for i, (label, data) in enumerate(approach_a.items()):
        points = data["trajectory"]
        ticks = [p["tick"] for p in points]
        rs = [p["r"] for p in points]
        ax.plot(ticks, rs, "-", color=colors[i], alpha=0.8, label=label)

    ax.set_xlabel("Tick")
    ax.set_ylabel("Distance from origin")
    ax.set_title("Approach A: Radial Distance r(t)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "radial_distance.png", dpi=150)
    plt.close(fig)
    print("  Saved radial_distance.png")


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
        ax.set_title("Approach B: Final Distance by Initial Ring")
        ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_dir / "approach_b_histogram.png", dpi=150)
    plt.close(fig)
    print("  Saved approach_b_histogram.png")


def plot_angular_momentum(approach_a, output_dir):
    """Angular momentum L(t) conservation check for Approach A."""
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
    ax.set_title("Approach A: Angular Momentum Conservation")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "angular_momentum.png", dpi=150)
    plt.close(fig)
    print("  Saved angular_momentum.png")


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
    ax.bar(radii[:30], values[:30], color="steelblue", alpha=0.8)
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
        "V18 Orbital Dynamics - Summary Dashboard",
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
    """Analyze experiment results and generate all plots.

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

    print("=" * 60)
    print("V18 Orbital Dynamics Analysis")
    print("=" * 60)
    print(f"  planet_count      = {config['planet_count']}")
    print(f"  speed_limit       = {config['speed_limit']}")
    print(f"  smoothed_gradient = {config['use_smoothed_gradient']}")
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

        # Summary comparison with V10
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
    if gradient_analysis:
        plot_gradient_vs_distance(gradient_analysis, output_dir)
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
        description="Analyze V18 orbital dynamics experiment results"
    )
    parser.add_argument(
        "results", type=str,
        help="Path to results JSON file",
    )
    args = parser.parse_args()
    analyze_experiment(args.results)


if __name__ == "__main__":
    main()
