"""Graph-Substrate Wave Propagation vs Euclidean Chladni

Phase 2 of the cymatics 432 Hz experiment. Tests whether 432 Hz behaves
differently on a graph substrate with Fibonacci-like propagation compared
to classical wave physics.

Three propagation models on the same 2D grid:
  A. Classical wave (baseline): u(t+1) = 2u(t) - u(t-1) + c^2*Laplacian
  B. Fibonacci-coupled: u(t+1) = u(t) + u(t-1) + coupling*Laplacian
  C. Axis-separable Fibonacci: independent 1D recurrence per axis

Reference: EXPERIMENT_FOLLOWUP.md
Phase 1 results: results/statistical_summary.txt (ARTIFACT verdict)

Usage:
    python -u graph_cymatics.py
    python -u graph_cymatics.py --sensitivity
    python -u graph_cymatics.py --grid 50 --ticks 1000

March 2026
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Import symmetry metrics from Phase 1 (same directory)
sys.path.insert(0, str(Path(__file__).parent))
from cymatics import compute_symmetry

# ===========================================================================
# Constants
# ===========================================================================

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Grid and simulation defaults
DEFAULT_GRID = 100
DEFAULT_TICKS = 2000
DEFAULT_C = 0.3           # wave speed (CFL: must be < 1/sqrt(2) ~ 0.707)
DEFAULT_COUPLING = 0.1    # spatial coupling for Fibonacci model
DEFAULT_DAMPING = 0.005   # light damping for steady-state convergence
PHI = (1 + np.sqrt(5)) / 2  # golden ratio ~ 1.618
DEFAULT_F_SAMPLE = 1000.0 # ticks per second equivalent
DEFAULT_DRIVE_AMP = 1.0
DEFAULT_CLASSICAL_DAMPING = 0.005  # light damping for steady-state convergence

# Frequency lists (identical to Phase 1 for direct comparison)
FIBONACCI_SERIES = [267, 432, 699]
FINE_SCAN = list(range(420, 441, 2))
CONTROLS = [360, 400, 450, 500, 528]

# Phase 1 composite scores at f_scale=1.5 (from results/statistical_summary.txt)
PHASE1_COMPOSITES = {
    267: -0.2042, 360: -0.0021, 400: 0.0755, 420: 0.0922,
    422: 0.0843, 424: 0.0762, 426: 0.1751, 428: 0.3414,
    430: 0.4448, 432: 0.3841, 434: 0.0286, 436: -0.0227,
    438: 0.4362, 440: 0.2262, 450: -0.1391, 500: 0.0525,
    528: 0.0852, 699: 0.7365,
}

# Sensitivity parameters
SENSITIVITY_GRIDS = [50, 100, 200]
SENSITIVITY_CONNECTIVITIES = [4, 8]

# Divergence threshold
DIVERGENCE_THRESHOLD = 1e10


# ===========================================================================
# Grid Laplacian
# ===========================================================================

def laplacian_4(u):
    """4-neighbor discrete Laplacian via np.roll (periodic, then clamp)."""
    L = (np.roll(u, 1, axis=0) + np.roll(u, -1, axis=0) +
         np.roll(u, 1, axis=1) + np.roll(u, -1, axis=1) - 4 * u)
    return L


def laplacian_8(u):
    """8-neighbor isotropic Laplacian.

    Weighting: cardinal neighbors weight 4, diagonal weight 1, center -20.
    Normalized by 6 for isotropy.
    """
    cardinal = (np.roll(u, 1, axis=0) + np.roll(u, -1, axis=0) +
                np.roll(u, 1, axis=1) + np.roll(u, -1, axis=1))
    diagonal = (np.roll(np.roll(u, 1, axis=0), 1, axis=1) +
                np.roll(np.roll(u, 1, axis=0), -1, axis=1) +
                np.roll(np.roll(u, -1, axis=0), 1, axis=1) +
                np.roll(np.roll(u, -1, axis=0), -1, axis=1))
    return (4 * cardinal + diagonal - 20 * u) / 6.0


def apply_dirichlet(u):
    """Clamp boundary to zero (fixed edges)."""
    u[0, :] = 0
    u[-1, :] = 0
    u[:, 0] = 0
    u[:, -1] = 0
    return u


def get_laplacian(connectivity):
    """Return appropriate Laplacian function."""
    return laplacian_8 if connectivity == 8 else laplacian_4


# ===========================================================================
# Propagation Models
# ===========================================================================

def simulate_classical(N, ticks, freq, f_sample, c=DEFAULT_C,
                       damping=DEFAULT_CLASSICAL_DAMPING,
                       connectivity=4, drive_amp=DEFAULT_DRIVE_AMP):
    """Model A: Classical damped wave equation.

    u(t+1) = 2*u(t) - u(t-1) + c^2 * L(u(t)) - gamma*(u(t) - u(t-1)) + drive
    """
    lap_fn = get_laplacian(connectivity)
    u_curr = np.zeros((N, N))
    u_prev = np.zeros((N, N))
    cx, cy = N // 2, N // 2
    omega = 2 * np.pi * freq / f_sample

    warmup = ticks // 2
    accumulator = np.zeros((N, N))
    count = 0

    for t in range(ticks):
        L = lap_fn(u_curr)
        u_next = (2 * u_curr - u_prev + c * c * L
                  - damping * (u_curr - u_prev))
        u_next[cx, cy] += drive_amp * np.sin(omega * t)
        apply_dirichlet(u_next)

        # Divergence check
        if np.max(np.abs(u_next)) > DIVERGENCE_THRESHOLD:
            print(f"    WARNING: Classical diverged at tick {t}, freq={freq}")
            return np.zeros((N, N))

        u_prev = u_curr
        u_curr = u_next

        if t >= warmup:
            accumulator += np.abs(u_curr)
            count += 1

    pattern = accumulator / max(count, 1)
    peak = np.max(np.abs(pattern))
    if peak > 0:
        pattern /= peak
    return pattern


def simulate_fibonacci_coupled(N, ticks, freq, f_sample,
                               coupling=DEFAULT_COUPLING,
                               damping=DEFAULT_DAMPING,
                               connectivity=4,
                               drive_amp=DEFAULT_DRIVE_AMP):
    """Model B: Fibonacci wave equation.

    u(t+1) = phi * u(t) - u(t-1) + coupling * L(u(t)) - damping * u(t) + drive

    Replaces the classical coefficient 2 with phi (golden ratio).
    This is bounded and oscillatory (|z|^2 = 1 from characteristic equation
    z^2 - phi*z + 1 = 0), but with a DIFFERENT eigenfrequency spectrum.

    Base frequency: arccos(phi/2) ~ 0.628 rad/tick (nonzero even without
    spatial coupling — classical base frequency is 0). The spatial modes
    shift this base, producing a phi-modulated resonance structure.
    """
    lap_fn = get_laplacian(connectivity)
    u_curr = np.zeros((N, N))
    u_prev = np.zeros((N, N))
    cx, cy = N // 2, N // 2
    omega = 2 * np.pi * freq / f_sample

    warmup = ticks // 2
    accumulator = np.zeros((N, N))
    count = 0

    for t in range(ticks):
        L = lap_fn(u_curr)
        u_next = (PHI * u_curr - u_prev + coupling * L
                  - damping * u_curr)
        u_next[cx, cy] += drive_amp * np.sin(omega * t)
        apply_dirichlet(u_next)

        if np.max(np.abs(u_next)) > DIVERGENCE_THRESHOLD:
            print(f"    WARNING: Fibonacci diverged at tick {t}, freq={freq}")
            return np.zeros((N, N))

        u_prev = u_curr
        u_curr = u_next

        if t >= warmup:
            accumulator += np.abs(u_curr)
            count += 1

    pattern = accumulator / max(count, 1)
    peak = np.max(np.abs(pattern))
    if peak > 0:
        pattern /= peak
    return pattern


def simulate_separable_fibonacci(N, ticks, freq, f_sample,
                                 damping=DEFAULT_DAMPING,
                                 drive_amp=DEFAULT_DRIVE_AMP):
    """Model C: Axis-separable Fibonacci wave (3 independent tick-series).

    Each axis runs independent 1D phi-wave:
        ux(t+1) = phi * ux(t) - ux(t-1) - damping * ux(t) + drive(t)
    2D pattern = outer product of axis amplitudes.
    """
    center = N // 2
    omega = 2 * np.pi * freq / f_sample

    ux_curr = np.zeros(N)
    ux_prev = np.zeros(N)
    uy_curr = np.zeros(N)
    uy_prev = np.zeros(N)

    warmup = ticks // 2
    accumulator = np.zeros((N, N))
    count = 0

    for t in range(ticks):
        drive = drive_amp * np.sin(omega * t)

        # X-axis: phi-wave with 1D nearest-neighbor coupling
        lap_x = np.roll(ux_curr, 1) + np.roll(ux_curr, -1) - 2 * ux_curr
        ux_next = PHI * ux_curr - ux_prev + 0.1 * lap_x - damping * ux_curr
        ux_next[center] += drive
        ux_next[0] = 0
        ux_next[-1] = 0

        # Y-axis: same phi-wave, independent state
        lap_y = np.roll(uy_curr, 1) + np.roll(uy_curr, -1) - 2 * uy_curr
        uy_next = PHI * uy_curr - uy_prev + 0.1 * lap_y - damping * uy_curr
        uy_next[center] += drive
        uy_next[0] = 0
        uy_next[-1] = 0

        if (np.max(np.abs(ux_next)) > DIVERGENCE_THRESHOLD or
                np.max(np.abs(uy_next)) > DIVERGENCE_THRESHOLD):
            print(f"    WARNING: Separable diverged at tick {t}, freq={freq}")
            return np.zeros((N, N))

        ux_prev = ux_curr
        ux_curr = ux_next
        uy_prev = uy_curr
        uy_curr = uy_next

        if t >= warmup:
            pattern_t = np.outer(np.abs(ux_curr), np.abs(uy_curr))
            accumulator += pattern_t
            count += 1

    pattern = accumulator / max(count, 1)
    peak = np.max(np.abs(pattern))
    if peak > 0:
        pattern /= peak
    return pattern


# ===========================================================================
# Frequency Sweep
# ===========================================================================

def run_graph_sweep(frequencies, model_fn, model_name, N, ticks, f_sample,
                    **model_kwargs):
    """Run simulation at each frequency, compute symmetry metrics."""
    results = []
    t0 = time.time()
    for i, freq in enumerate(frequencies):
        pattern = model_fn(N, ticks, freq, f_sample, **model_kwargs)
        metrics = compute_symmetry(pattern)
        results.append((freq, pattern, metrics))
        print(f"  [{i+1:3d}/{len(frequencies)}] {model_name:12s} f={freq:7.1f} Hz  "
              f"C4={metrics['C4']:.4f}  composite={metrics['composite']:.4f}  "
              f"nodal={metrics['nodal_regions']:3d}")
    elapsed = time.time() - t0
    print(f"  {model_name} sweep: {elapsed:.1f}s")
    return results


# ===========================================================================
# Plotting
# ===========================================================================

def plot_graph_patterns(results_classical, results_fibonacci, results_separable):
    """3-row grid: Classical / Fibonacci / Separable at key frequencies."""
    display_freqs = sorted(set([267, 420, 432, 440, 528, 699]))
    models = [
        ("Classical", results_classical),
        ("Fibonacci", results_fibonacci),
        ("Separable", results_separable),
    ]

    ncols = len(display_freqs)
    nrows = 3
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.5 * ncols, 3.5 * nrows))

    for row, (model_name, results) in enumerate(models):
        freq_map = {f: (p, m) for f, p, m in results}
        for col, freq in enumerate(display_freqs):
            ax = axes[row, col]
            if freq in freq_map:
                pattern, metrics = freq_map[freq]
                ax.imshow(pattern.T, origin='lower', cmap='RdBu_r',
                          vmin=-1, vmax=1, extent=[0, 1, 0, 1])
                x = np.linspace(0, 1, pattern.shape[0])
                y = np.linspace(0, 1, pattern.shape[1])
                ax.contour(x, y, pattern.T, levels=[0], colors='black',
                           linewidths=0.5, alpha=0.5)
                score = metrics['composite']
            else:
                ax.text(0.5, 0.5, 'N/A', ha='center', va='center',
                        transform=ax.transAxes)
                score = 0

            is_432 = abs(freq - 432) < 1
            color = '#ff4444' if is_432 else 'black'
            weight = 'bold' if is_432 else 'normal'

            if row == 0:
                ax.set_title(f"{freq} Hz", fontsize=10, color=color,
                             fontweight=weight)
            if col == 0:
                ax.set_ylabel(f"{model_name}\nC={score:.3f}", fontsize=9)
            else:
                ax.set_ylabel(f"C={score:.3f}", fontsize=8)
            ax.set_xticks([])
            ax.set_yticks([])

    fig.suptitle('Graph-Substrate Patterns: Classical vs Fibonacci vs Separable',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'graph_patterns.png', dpi=150)
    plt.close(fig)
    print(f"  Saved graph_patterns.png")


def plot_graph_symmetry(results_classical, results_fibonacci, results_separable):
    """Composite score vs frequency for each model."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)

    models = [
        ("Classical", results_classical, '#3498db'),
        ("Fibonacci-coupled", results_fibonacci, '#e74c3c'),
        ("Separable Fib", results_separable, '#2ecc71'),
    ]

    for ax, (name, results, color) in zip(axes, models):
        freqs = [r[0] for r in results]
        composites = [r[2]['composite'] for r in results]
        ax.plot(freqs, composites, 'o-', color=color, markersize=5,
                linewidth=1.2)
        ax.axvline(432, color='red', linestyle='--', alpha=0.6, linewidth=2)
        for f in FIBONACCI_SERIES:
            if f != 432:
                ax.axvline(f, color='orange', linestyle=':', alpha=0.4)
        ax.set_xlabel('Frequency (Hz)', fontsize=11)
        ax.set_title(name, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

    axes[0].set_ylabel('Composite Symmetry', fontsize=11)
    fig.suptitle('Graph-Substrate Symmetry vs Frequency',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'graph_symmetry.png', dpi=150)
    plt.close(fig)
    print(f"  Saved graph_symmetry.png")


def plot_graph_vs_euclidean(results_fibonacci):
    """Scatter: Phase 1 Euclidean composite vs Phase 2 Fibonacci composite."""
    fig, ax = plt.subplots(figsize=(8, 8))

    freqs = [r[0] for r in results_fibonacci]
    fib_composites = {r[0]: r[2]['composite'] for r in results_fibonacci}

    for freq in freqs:
        if freq not in PHASE1_COMPOSITES or freq not in fib_composites:
            continue
        x = PHASE1_COMPOSITES[freq]
        y = fib_composites[freq]

        if freq in FIBONACCI_SERIES:
            color, marker, size = '#e74c3c', '*', 120
        elif freq in FINE_SCAN:
            color, marker, size = '#3498db', 'o', 50
        else:
            color, marker, size = '#95a5a6', 's', 50

        ax.scatter(x, y, c=color, marker=marker, s=size, zorder=3,
                   edgecolors='black', linewidths=0.5)

        is_432 = abs(freq - 432) < 1
        if is_432 or freq in FIBONACCI_SERIES or freq in [440, 528]:
            ax.annotate(f'{freq}', (x, y), textcoords='offset points',
                        xytext=(8, 5), fontsize=8,
                        fontweight='bold' if is_432 else 'normal',
                        color='red' if is_432 else 'black')

    # Reference line
    lims = [min(ax.get_xlim()[0], ax.get_ylim()[0]),
            max(ax.get_xlim()[1], ax.get_ylim()[1])]
    ax.plot(lims, lims, '--', color='gray', alpha=0.5, zorder=1)

    ax.set_xlabel('Phase 1: Euclidean Composite', fontsize=12)
    ax.set_ylabel('Phase 2: Fibonacci-Coupled Composite', fontsize=12)
    ax.set_title('Euclidean vs Graph-Substrate Symmetry',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor='#e74c3c',
               markersize=12, label='Fibonacci (3xF)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498db',
               markersize=8, label='Fine scan'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#95a5a6',
               markersize=8, label='Controls'),
    ]
    ax.legend(handles=legend_elements, loc='upper left')

    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'graph_vs_euclidean.png', dpi=150)
    plt.close(fig)
    print(f"  Saved graph_vs_euclidean.png")


def plot_graph_sensitivity(sensitivity_results):
    """432 Hz composite across grid sizes and connectivities."""
    if not sensitivity_results:
        return

    configs = sorted(sensitivity_results.keys())
    n_configs = len(configs)

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(n_configs)
    composites_432 = []
    labels = []

    for config in configs:
        results = sensitivity_results[config]
        c432 = next((m['composite'] for f, _, m in results if abs(f - 432) < 1),
                     0.0)
        composites_432.append(c432)
        grid_size, conn = config
        labels.append(f"N={grid_size}\n{conn}-conn")

    colors = ['#e74c3c' if c > np.mean(composites_432) else '#3498db'
              for c in composites_432]
    ax.bar(x, composites_432, color=colors, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('432 Hz Composite Score', fontsize=12)
    ax.set_title('Fibonacci Model: 432 Hz Sensitivity to Grid Parameters',
                 fontsize=13, fontweight='bold')
    ax.axhline(np.mean(composites_432), color='gray', linestyle='--',
               alpha=0.5, label=f'mean={np.mean(composites_432):.4f}')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'graph_sensitivity.png', dpi=150)
    plt.close(fig)
    print(f"  Saved graph_sensitivity.png")


# ===========================================================================
# Statistical Analysis + Verdict
# ===========================================================================

def graph_statistical_analysis(results_classical, results_fibonacci,
                               results_separable, sensitivity_results=None):
    """Analyze 432 Hz across models and determine verdict."""
    lines = []
    lines.append("GRAPH-SUBSTRATE WAVE PROPAGATION — STATISTICAL SUMMARY")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)

    model_results = {
        'Classical': results_classical,
        'Fibonacci': results_fibonacci,
        'Separable': results_separable,
    }

    # --- Per-model ranking ---
    lines.append("")
    lines.append("--- PER-MODEL RANKING ---")

    for model_name, results in model_results.items():
        composites = sorted([(f, m['composite']) for f, _, m in results],
                            key=lambda x: x[1], reverse=True)
        rank_432 = next(i + 1 for i, (f, _) in enumerate(composites)
                        if abs(f - 432) < 1)
        score_432 = next(c for f, c in composites if abs(f - 432) < 1)
        total = len(composites)

        lines.append(f"\n  {model_name}: 432 Hz rank={rank_432}/{total}, "
                     f"composite={score_432:.4f}")
        for i, (f, c) in enumerate(composites[:5]):
            marker = " <-- 432 Hz" if abs(f - 432) < 1 else ""
            fib = " [3xF]" if f in FIBONACCI_SERIES else ""
            lines.append(f"    {i+1}. {f:7.1f} Hz  C={c:.4f}{fib}{marker}")

    # --- Full results table ---
    lines.append("")
    lines.append("--- FULL RESULTS ---")
    lines.append(f"{'Freq':>8s}  {'Classical':>10s}  {'Fibonacci':>10s}  "
                 f"{'Separable':>10s}  {'Fib-Class':>10s}  Category")
    lines.append("-" * 70)

    classical_map = {f: m['composite'] for f, _, m in results_classical}
    fibonacci_map = {f: m['composite'] for f, _, m in results_fibonacci}
    separable_map = {f: m['composite'] for f, _, m in results_separable}

    all_freqs = sorted(set(f for f, _, _ in results_classical))
    for freq in all_freqs:
        c_cl = classical_map.get(freq, 0)
        c_fb = fibonacci_map.get(freq, 0)
        c_sp = separable_map.get(freq, 0)
        diff = c_fb - c_cl

        if freq in FIBONACCI_SERIES:
            cat = "Fibonacci"
        elif freq in FINE_SCAN:
            cat = "Fine scan"
        elif freq in CONTROLS:
            cat = "Control"
        else:
            cat = ""
        marker = " ***" if abs(freq - 432) < 1 else ""
        lines.append(f"{freq:8.1f}  {c_cl:10.4f}  {c_fb:10.4f}  "
                     f"{c_sp:10.4f}  {diff:+10.4f}  {cat}{marker}")

    # --- Cross-model comparison ---
    lines.append("")
    lines.append("--- CROSS-MODEL COMPARISON ---")

    diffs = [(f, fibonacci_map.get(f, 0) - classical_map.get(f, 0))
             for f in all_freqs]
    diff_432 = next(d for f, d in diffs if abs(f - 432) < 1)
    other_diffs = [d for f, d in diffs if abs(f - 432) > 1]

    lines.append(f"432 Hz (Fibonacci - Classical) difference: {diff_432:+.4f}")
    lines.append(f"Other frequencies mean difference: "
                 f"{np.mean(other_diffs):+.4f} +/- {np.std(other_diffs):.4f}")

    if other_diffs:
        u_stat, p_cross = stats.mannwhitneyu(
            [diff_432], other_diffs, alternative='greater')
        lines.append(f"Mann-Whitney U: U={u_stat:.1f}, p={p_cross:.4f}")
        if p_cross < 0.05:
            lines.append("  ** 432 Hz SIGNIFICANTLY more improved on Fibonacci **")
        else:
            lines.append("  Not significant (p > 0.05)")
    else:
        p_cross = 1.0

    # --- Models different overall? ---
    lines.append("")
    lines.append("--- ARE MODELS DIFFERENT? ---")
    classical_scores = [m['composite'] for _, _, m in results_classical]
    fibonacci_scores = [m['composite'] for _, _, m in results_fibonacci]
    corr_cf = np.corrcoef(classical_scores, fibonacci_scores)[0, 1]
    lines.append(f"Classical vs Fibonacci correlation: r={corr_cf:.4f}")
    if abs(corr_cf) < 0.5:
        lines.append("  Models produce SUBSTANTIALLY DIFFERENT patterns")
        models_different = True
    elif abs(corr_cf) < 0.8:
        lines.append("  Models produce MODERATELY DIFFERENT patterns")
        models_different = True
    else:
        lines.append("  Models produce SIMILAR patterns")
        models_different = False

    # --- Sensitivity analysis ---
    verdict = "NULL"
    if sensitivity_results:
        lines.append("")
        lines.append("--- SENSITIVITY ANALYSIS (honesty check) ---")

        ranks_432 = []
        scores_432 = []

        for config in sorted(sensitivity_results.keys()):
            results = sensitivity_results[config]
            composites = sorted([(f, m['composite']) for f, _, m in results],
                                key=lambda x: x[1], reverse=True)
            rank = next(i + 1 for i, (f, _) in enumerate(composites)
                        if abs(f - 432) < 1)
            score = next(c for f, c in composites if abs(f - 432) < 1)
            total = len(composites)
            ranks_432.append(rank)
            scores_432.append(score)

            grid_size, conn = config
            lines.append(f"  N={grid_size}, {conn}-conn: "
                         f"rank={rank}/{total}, composite={score:.4f}")

        fraction_top = sum(1 for r in ranks_432
                           if r <= len(composites) / 2) / len(ranks_432)
        lines.append(f"\n  Fraction in top half: {fraction_top:.1%}")
        lines.append(f"  Score range: [{min(scores_432):.4f}, "
                     f"{max(scores_432):.4f}]")

        # Verdict with sensitivity
        if p_cross < 0.05 and fraction_top >= 0.8:
            verdict = "GRAPH_PRIVILEGED"
        elif models_different:
            verdict = "GRAPH_DIFFERENT"
        else:
            verdict = "NULL"
    else:
        # Verdict without sensitivity
        if p_cross < 0.05:
            verdict = "GRAPH_PRIVILEGED (unconfirmed — run with --sensitivity)"
        elif models_different:
            verdict = "GRAPH_DIFFERENT"
        else:
            verdict = "NULL"

    # --- Verdict ---
    lines.append("")
    lines.append("=" * 60)
    lines.append("VERDICT")
    lines.append("=" * 60)

    explanations = {
        "GRAPH_PRIVILEGED": (
            "432 Hz shows significantly higher symmetry on the Fibonacci-coupled "
            "substrate than on the classical wave substrate, AND this advantage "
            "is robust across grid parameters. The graph substrate's Fibonacci "
            "temporal dynamics create a measurable resonance privilege at 432 Hz."
        ),
        "GRAPH_DIFFERENT": (
            "The Fibonacci-coupled substrate produces fundamentally different "
            "patterns than classical wave physics, but 432 Hz is NOT specifically "
            "privileged. The graph substrate changes the physics but does not "
            "favor 432 Hz over other frequencies."
        ),
        "NULL": (
            "No meaningful difference between Fibonacci-coupled and classical "
            "substrates at 432 Hz. The graph propagation rule does not create "
            "a resonance privilege for 432 Hz."
        ),
    }

    base_verdict = verdict.split(" (")[0]
    lines.append(f"Verdict: {verdict}")
    lines.append("")
    lines.append(explanations.get(base_verdict, ""))

    summary = "\n".join(lines)
    return summary, verdict


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Graph-Substrate Wave Propagation Experiment')
    parser.add_argument('--grid', type=int, default=DEFAULT_GRID)
    parser.add_argument('--ticks', type=int, default=DEFAULT_TICKS)
    parser.add_argument('--c', type=float, default=DEFAULT_C,
                        help='Wave speed for classical model')
    parser.add_argument('--coupling', type=float, default=DEFAULT_COUPLING,
                        help='Spatial coupling for Fibonacci model')
    parser.add_argument('--damping', type=float, default=DEFAULT_DAMPING,
                        help='Damping for Fibonacci model (>= 0.618)')
    parser.add_argument('--f-sample', type=float, default=DEFAULT_F_SAMPLE)
    parser.add_argument('--connectivity', type=int, default=4, choices=[4, 8])
    parser.add_argument('--sensitivity', action='store_true',
                        help='Run grid-size and connectivity sensitivity')
    args = parser.parse_args()

    print("=" * 60)
    print("GRAPH-SUBSTRATE WAVE PROPAGATION EXPERIMENT")
    print("=" * 60)
    print(f"  Grid: {args.grid}x{args.grid}")
    print(f"  Ticks: {args.ticks}")
    print(f"  Wave speed (classical): {args.c}")
    print(f"  Coupling (Fibonacci): {args.coupling}")
    print(f"  Damping (Fibonacci): {args.damping}")
    print(f"  f_sample: {args.f_sample}")
    print(f"  Connectivity: {args.connectivity}-neighbor")
    print(f"  Sensitivity: {args.sensitivity}")
    print()

    all_freqs = sorted(set(FIBONACCI_SERIES + FINE_SCAN + CONTROLS))
    print(f"Testing {len(all_freqs)} frequencies: "
          f"{min(all_freqs)}-{max(all_freqs)} Hz")
    print()

    # --- Step 1: Frequency sweeps for all 3 models ---
    print("--- Step 1: Classical Wave Sweep ---")
    results_classical = run_graph_sweep(
        all_freqs, simulate_classical, "Classical",
        args.grid, args.ticks, args.f_sample,
        c=args.c, damping=DEFAULT_CLASSICAL_DAMPING,
        connectivity=args.connectivity)

    print()
    print("--- Step 2: Fibonacci-Coupled Sweep ---")
    results_fibonacci = run_graph_sweep(
        all_freqs, simulate_fibonacci_coupled, "Fibonacci",
        args.grid, args.ticks, args.f_sample,
        coupling=args.coupling, damping=args.damping,
        connectivity=args.connectivity)

    print()
    print("--- Step 3: Separable Fibonacci Sweep ---")
    results_separable = run_graph_sweep(
        all_freqs, simulate_separable_fibonacci, "Separable",
        args.grid, args.ticks, args.f_sample,
        damping=args.damping)

    # --- Step 4: Sensitivity analysis ---
    sensitivity_results = None
    if args.sensitivity:
        print()
        print("--- Step 4: Sensitivity Analysis (Fibonacci model) ---")
        sensitivity_results = {}
        for grid_size in SENSITIVITY_GRIDS:
            for conn in SENSITIVITY_CONNECTIVITIES:
                config = (grid_size, conn)
                # Skip default (already computed)
                if grid_size == args.grid and conn == args.connectivity:
                    sensitivity_results[config] = results_fibonacci
                    print(f"  N={grid_size}, {conn}-conn: (reusing default)")
                    continue

                ticks = min(args.ticks, max(1000, args.ticks * 100 // (grid_size * grid_size)))
                print(f"\n  N={grid_size}, {conn}-conn ({ticks} ticks):")
                sr = run_graph_sweep(
                    all_freqs, simulate_fibonacci_coupled, "Fibonacci",
                    grid_size, ticks, args.f_sample,
                    coupling=args.coupling, damping=args.damping,
                    connectivity=conn)
                sensitivity_results[config] = sr
    else:
        print()
        print("--- Step 4: Skipping sensitivity (use --sensitivity) ---")

    # --- Step 5: Plots ---
    print()
    print("--- Step 5: Generating Plots ---")
    plot_graph_patterns(results_classical, results_fibonacci, results_separable)
    plot_graph_symmetry(results_classical, results_fibonacci, results_separable)
    plot_graph_vs_euclidean(results_fibonacci)
    if sensitivity_results:
        plot_graph_sensitivity(sensitivity_results)

    # --- Step 6: Statistical analysis ---
    print()
    print("--- Step 6: Statistical Analysis ---")
    summary, verdict = graph_statistical_analysis(
        results_classical, results_fibonacci, results_separable,
        sensitivity_results)
    print()
    print(summary)

    with open(RESULTS_DIR / 'graph_summary.txt', 'w') as f:
        f.write(summary)
    print(f"\nSaved to {RESULTS_DIR / 'graph_summary.txt'}")
    print(f"All plots saved to {RESULTS_DIR}/")


if __name__ == '__main__':
    main()
