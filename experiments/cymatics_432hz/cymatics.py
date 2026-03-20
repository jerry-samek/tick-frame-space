"""Cymatics 432 Hz — Chladni Pattern Symmetry Analysis

Tests whether 432 Hz = 3 x F(12) = 3 x 144 produces measurably higher
symmetry in Chladni figures (standing wave patterns on vibrating plates)
compared to neighboring frequencies.

Analytical computation of Chladni patterns for a square plate using
superposition of eigenmodes with Lorentzian response.

Reference: experiments/cymatics_432hz/EXPERIMENT.md

Usage:
    python -u cymatics.py
    python -u cymatics.py --sensitivity
    python -u cymatics.py --grid 300 --max-mode 15

March 2026
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy import ndimage, stats

# ===========================================================================
# Constants
# ===========================================================================

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Physical parameters
DEFAULT_GRID = 500
DEFAULT_MAX_MODE = 20
DEFAULT_Q = 100        # quality factor (controls resonance sharpness)
DEFAULT_F_SCALE = 1.5  # eigenfrequency scale factor (plate-dependent)

# Frequency lists from EXPERIMENT.md
FIBONACCI_SERIES = [267, 432, 699]        # 3 x F(n) for n=10,12,14
FINE_SCAN = list(range(420, 441, 2))      # 420, 422, ..., 440
CONTROLS = [360, 400, 450, 500, 528]      # non-Fibonacci controls

# Fibonacci sequence for convergence plot
FIB_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610,
                987, 1597, 2584]

# f_scale values for sensitivity analysis
SENSITIVITY_F_SCALES = [1.0, 1.25, 1.5, 1.75, 2.0]


# ===========================================================================
# Chladni pattern computation
# ===========================================================================

def compute_chladni_pattern(f_drive, f_scale, Q, grid, max_mode):
    """Compute Chladni pattern for a square plate at given driving frequency.

    Uses superposition of eigenmodes (m,n) with Lorentzian response:
        A_mn = 1 / ((f_drive - f_mn)^2 + gamma^2)
    where f_mn = f_scale * (m^2 + n^2) and gamma = f_mn / (2*Q).

    Mode shape: cos(m*pi*x)*cos(n*pi*y) + cos(n*pi*x)*cos(m*pi*y)
    (free-free boundary conditions, symmetric modes).

    Returns:
        pattern: grid x grid array normalized to [-1, 1]
        dominant_modes: list of (m, n, amplitude) for top contributing modes
    """
    x = np.linspace(0, 1, grid)
    # Precompute cosine basis vectors
    cos_basis = np.zeros((max_mode + 1, grid))
    for m in range(max_mode + 1):
        cos_basis[m] = np.cos(m * np.pi * x)

    pattern = np.zeros((grid, grid))
    mode_amplitudes = []

    for m in range(max_mode + 1):
        for n in range(m, max_mode + 1):  # n >= m to avoid double-counting
            if m == 0 and n == 0:
                continue  # skip DC mode

            # Eigenfrequency for mode (m,n)
            f_mn = f_scale * (m**2 + n**2)

            # Lorentzian response
            gamma = f_mn / (2 * Q) if Q > 0 else 1.0
            response = 1.0 / ((f_drive - f_mn)**2 + gamma**2)

            # Mode shape: symmetric combination
            # cos(m*pi*x)*cos(n*pi*y) + cos(n*pi*x)*cos(m*pi*y)
            shape = (np.outer(cos_basis[m], cos_basis[n]) +
                     np.outer(cos_basis[n], cos_basis[m]))

            # Weight: 2x for off-diagonal modes (m != n) already handled
            # by the symmetric combination above
            degeneracy = 1.0 if m == n else 1.0
            amplitude = response * degeneracy

            pattern += amplitude * shape
            mode_amplitudes.append((m, n, amplitude))

    # Normalize to [-1, 1]
    peak = np.max(np.abs(pattern))
    if peak > 0:
        pattern /= peak

    # Sort modes by amplitude (descending)
    mode_amplitudes.sort(key=lambda x: x[2], reverse=True)
    dominant_modes = mode_amplitudes[:5]

    return pattern, dominant_modes


# ===========================================================================
# Symmetry quantification
# ===========================================================================

def _correlation(a, b):
    """Pearson correlation between two arrays."""
    a_flat = a.ravel()
    b_flat = b.ravel()
    a_centered = a_flat - np.mean(a_flat)
    b_centered = b_flat - np.mean(b_flat)
    denom = np.sqrt(np.sum(a_centered**2) * np.sum(b_centered**2))
    if denom < 1e-15:
        return 1.0
    return np.sum(a_centered * b_centered) / denom


def _circular_mask(grid):
    """Create circular mask inscribed in the square grid."""
    center = grid / 2.0
    radius = grid / 2.0
    y, x = np.ogrid[:grid, :grid]
    dist = np.sqrt((x - center)**2 + (y - center)**2)
    return dist <= radius


def compute_symmetry(pattern):
    """Compute multiple symmetry metrics for a Chladni pattern.

    Returns dict with:
        C4: correlation with 90-degree rotation
        C8: correlation with 45-degree rotation (circular-masked)
        bilateral: mean of 4 mirror correlations
        nodal_regions: number of distinct nodal regions
        sharpness: mean gradient magnitude at nodal lines
        composite: weighted combination
    """
    grid = pattern.shape[0]

    # C4: 4-fold rotational symmetry (90 degrees)
    rot90 = np.rot90(pattern)
    c4 = _correlation(pattern, rot90)

    # C8: 8-fold rotational symmetry (45 degrees)
    # Use circular mask to avoid corner artifacts from rotation
    mask = _circular_mask(grid)
    rot45 = ndimage.rotate(pattern, 45, reshape=False, order=3)
    masked_orig = pattern * mask
    masked_rot = rot45 * mask
    c8 = _correlation(masked_orig, masked_rot)

    # Bilateral symmetry: 4 mirror operations
    flip_x = _correlation(pattern, np.flip(pattern, axis=0))
    flip_y = _correlation(pattern, np.flip(pattern, axis=1))
    transpose = _correlation(pattern, pattern.T)
    anti_transpose = _correlation(pattern, np.flip(pattern.T, axis=(0, 1)))
    bilateral = np.mean([flip_x, flip_y, transpose, anti_transpose])

    # Nodal regions: connected components where |pattern| < threshold
    threshold = 0.05 * np.max(np.abs(pattern))
    nodal_mask = np.abs(pattern) < threshold
    labeled, nodal_regions = ndimage.label(nodal_mask)

    # Sharpness: gradient magnitude at nodal lines
    gy, gx = np.gradient(pattern)
    grad_mag = np.sqrt(gx**2 + gy**2)
    if np.any(nodal_mask):
        sharpness = np.mean(grad_mag[nodal_mask])
    else:
        sharpness = 0.0

    # Normalize sharpness to [0, 1] range (approximate)
    max_possible_grad = np.max(grad_mag)
    sharpness_norm = sharpness / max_possible_grad if max_possible_grad > 0 else 0.0

    # Complexity: normalized nodal region count
    # More regions = more complex pattern (normalize by grid area)
    complexity = min(nodal_regions / 50.0, 1.0)  # cap at 50 regions

    # Composite score
    composite = (0.3 * c4 + 0.2 * c8 + 0.3 * bilateral +
                 0.1 * sharpness_norm + 0.1 * complexity)

    return {
        'C4': c4,
        'C8': c8,
        'bilateral': bilateral,
        'nodal_regions': nodal_regions,
        'sharpness': sharpness_norm,
        'complexity': complexity,
        'composite': composite,
    }


# ===========================================================================
# Frequency sweep
# ===========================================================================

def run_sweep(frequencies, f_scale, Q, grid, max_mode):
    """Compute Chladni patterns and symmetry metrics for all frequencies.

    Returns list of (freq, pattern, metrics) tuples.
    """
    results = []
    for i, freq in enumerate(frequencies):
        pattern, dominant = compute_chladni_pattern(freq, f_scale, Q, grid, max_mode)
        metrics = compute_symmetry(pattern)
        results.append((freq, pattern, metrics))
        print(f"  [{i+1:3d}/{len(frequencies)}] f={freq:7.1f} Hz  "
              f"C4={metrics['C4']:.4f}  C8={metrics['C8']:.4f}  "
              f"bilateral={metrics['bilateral']:.4f}  "
              f"composite={metrics['composite']:.4f}  "
              f"nodal={metrics['nodal_regions']:3d}")
    return results


# ===========================================================================
# Plotting
# ===========================================================================

def plot_chladni_patterns(results, tag=''):
    """Grid of pattern visualizations with nodal lines.

    Shows a selection of key frequencies.
    """
    # Select subset for display: Fibonacci series + 432 neighbors + controls
    display_freqs = sorted(set(FIBONACCI_SERIES + [420, 430, 440] + [400, 528]))
    display = [(f, p, m) for f, p, m in results if f in display_freqs]

    if not display:
        # Fallback: show first 9
        display = results[:9]

    n = len(display)
    ncols = min(4, n)
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows))
    if nrows == 1 and ncols == 1:
        axes = np.array([[axes]])
    elif nrows == 1:
        axes = axes[np.newaxis, :]
    elif ncols == 1:
        axes = axes[:, np.newaxis]

    for idx, (freq, pattern, metrics) in enumerate(display):
        row, col = divmod(idx, ncols)
        ax = axes[row, col]

        # Show pattern as heatmap
        ax.imshow(pattern.T, origin='lower', cmap='RdBu_r',
                  vmin=-1, vmax=1, extent=[0, 1, 0, 1])

        # Overlay nodal lines (zero contour)
        x = np.linspace(0, 1, pattern.shape[0])
        y = np.linspace(0, 1, pattern.shape[1])
        ax.contour(x, y, pattern.T, levels=[0], colors='black',
                   linewidths=0.8, alpha=0.7)

        # Mark 432 Hz specially
        is_432 = abs(freq - 432) < 1
        color = '#ff4444' if is_432 else 'black'
        weight = 'bold' if is_432 else 'normal'
        ax.set_title(f"{freq} Hz\nC={metrics['composite']:.3f}",
                     fontsize=10, color=color, fontweight=weight)
        ax.set_xticks([])
        ax.set_yticks([])

    # Hide unused axes
    for idx in range(n, nrows * ncols):
        row, col = divmod(idx, ncols)
        axes[row, col].set_visible(False)

    fig.suptitle('Chladni Patterns — Nodal Lines at Key Frequencies',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'chladni_patterns.png', dpi=150)
    plt.close(fig)
    print(f"  Saved chladni_patterns.png")


def plot_symmetry_vs_frequency(results, tag=''):
    """All symmetry metrics vs frequency, 432 Hz highlighted."""
    freqs = [r[0] for r in results]
    metrics_list = [r[2] for r in results]

    metric_names = ['C4', 'C8', 'bilateral', 'composite', 'sharpness']
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#8e44ad', '#f39c12']

    fig, ax = plt.subplots(figsize=(14, 6))

    for name, color in zip(metric_names, colors):
        values = [m[name] for m in metrics_list]
        ax.plot(freqs, values, 'o-', color=color, label=name,
                markersize=4, linewidth=1.2, alpha=0.8)

    # Highlight 432 Hz
    ax.axvline(432, color='red', linestyle='--', alpha=0.6, linewidth=2,
               label='432 Hz')

    # Mark Fibonacci series
    for f in FIBONACCI_SERIES:
        if f != 432:
            ax.axvline(f, color='orange', linestyle=':', alpha=0.4)

    ax.set_xlabel('Frequency (Hz)', fontsize=12)
    ax.set_ylabel('Symmetry Score', fontsize=12)
    ax.set_title('Symmetry Metrics vs Driving Frequency', fontsize=14,
                 fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'symmetry_vs_frequency.png', dpi=150)
    plt.close(fig)
    print(f"  Saved symmetry_vs_frequency.png")


def plot_fibonacci_convergence():
    """F(n+1)/F(n) convergence to phi, and 3*F(n) series with 432 marked."""
    phi = (1 + np.sqrt(5)) / 2

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: ratio convergence
    n_vals = list(range(2, len(FIB_SEQUENCE)))
    ratios = [FIB_SEQUENCE[i] / FIB_SEQUENCE[i-1] for i in n_vals]
    errors = [abs(r - phi) for r in ratios]

    ax1.semilogy(n_vals, errors, 'bo-', markersize=6, linewidth=1.5)
    ax1.axvline(12, color='red', linestyle='--', alpha=0.7, linewidth=2,
                label='n=12 (F=144)')
    ax1.set_xlabel('n', fontsize=12)
    ax1.set_ylabel('|F(n)/F(n-1) - phi|', fontsize=12)
    ax1.set_title('Fibonacci Ratio Convergence to phi', fontsize=12,
                  fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Annotate n=12
    idx_12 = n_vals.index(12)
    ax1.annotate(f'n=12: error={errors[idx_12]:.6f}',
                 xy=(12, errors[idx_12]),
                 xytext=(14, errors[idx_12] * 10),
                 arrowprops=dict(arrowstyle='->', color='red'),
                 fontsize=9, color='red')

    # Right: 3*F(n) series
    fib_3x = [3 * f for f in FIB_SEQUENCE if 3 * f < 3000]
    fib_n = [FIB_SEQUENCE.index(f // 3) + 1 for f in fib_3x
             if f // 3 in FIB_SEQUENCE]

    # Map n index correctly
    n_indices = []
    freqs_3x = []
    for i, f in enumerate(FIB_SEQUENCE):
        val = 3 * f
        if val < 3000:
            n_indices.append(i + 1)  # 1-indexed
            freqs_3x.append(val)

    ax2.plot(n_indices, freqs_3x, 'gs-', markersize=8, linewidth=1.5,
             label='3 x F(n)')

    # Highlight 432
    if 432 in freqs_3x:
        idx_432 = freqs_3x.index(432)
        ax2.plot(n_indices[idx_432], 432, 'r*', markersize=20, zorder=5,
                 label='432 = 3 x F(12)')
        ax2.annotate('432 = 3 x 144 = 3 x 12^2',
                     xy=(n_indices[idx_432], 432),
                     xytext=(n_indices[idx_432] + 1.5, 432 + 200),
                     arrowprops=dict(arrowstyle='->', color='red'),
                     fontsize=10, color='red', fontweight='bold')

    ax2.set_xlabel('n (Fibonacci index)', fontsize=12)
    ax2.set_ylabel('Frequency (Hz)', fontsize=12)
    ax2.set_title('3D Fibonacci Series: 3 x F(n)', fontsize=12,
                  fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.suptitle('Fibonacci Mathematical Foundation',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'fibonacci_convergence.png', dpi=150)
    plt.close(fig)
    print(f"  Saved fibonacci_convergence.png")


def plot_statistical_comparison(results):
    """Box/violin plot by category (Fibonacci / fine scan / controls)."""
    # Categorize frequencies
    categories = {}
    for freq, pattern, metrics in results:
        if freq in FIBONACCI_SERIES:
            cat = 'Fibonacci (3xF)'
        elif freq in FINE_SCAN:
            cat = 'Fine scan (420-440)'
        elif freq in CONTROLS:
            cat = 'Controls'
        else:
            continue
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(metrics['composite'])

    if not categories:
        return

    cat_names = list(categories.keys())
    cat_data = [categories[c] for c in cat_names]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Violin plot
    parts = ax1.violinplot(cat_data, showmeans=True, showmedians=True)
    for pc in parts['bodies']:
        pc.set_facecolor('#3498db')
        pc.set_alpha(0.6)
    ax1.set_xticks(range(1, len(cat_names) + 1))
    ax1.set_xticklabels(cat_names, fontsize=10)
    ax1.set_ylabel('Composite Symmetry Score', fontsize=12)
    ax1.set_title('Distribution by Category', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')

    # Individual metric comparison
    metric_names = ['C4', 'C8', 'bilateral', 'sharpness']
    x = np.arange(len(metric_names))
    width = 0.25
    bar_colors = ['#e74c3c', '#3498db', '#2ecc71']

    for i, (cat_name, data_metrics) in enumerate(zip(cat_names, cat_data)):
        # Recompute per-metric means for each category
        cat_results = [(f, p, m) for f, p, m in results
                       if (f in FIBONACCI_SERIES and cat_name == 'Fibonacci (3xF)') or
                          (f in FINE_SCAN and cat_name == 'Fine scan (420-440)') or
                          (f in CONTROLS and cat_name == 'Controls')]
        means = []
        for mn in metric_names:
            vals = [m[mn] for _, _, m in cat_results]
            means.append(np.mean(vals) if vals else 0)

        ax2.bar(x + i * width, means, width, label=cat_name,
                color=bar_colors[i % len(bar_colors)], edgecolor='black',
                alpha=0.8)

    ax2.set_xticks(x + width)
    ax2.set_xticklabels(metric_names, fontsize=10)
    ax2.set_ylabel('Mean Score', fontsize=12)
    ax2.set_title('Mean Metrics by Category', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')

    fig.suptitle('Statistical Comparison of Frequency Categories',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'statistical_comparison.png', dpi=150)
    plt.close(fig)
    print(f"  Saved statistical_comparison.png")


# ===========================================================================
# Statistical analysis + verdict
# ===========================================================================

def statistical_analysis(results, sensitivity_results=None):
    """Analyze 432 Hz ranking and significance.

    Returns (summary_text, verdict).
    """
    lines = []
    lines.append("CYMATICS 432 Hz — STATISTICAL SUMMARY")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)

    # Extract 432 Hz results
    result_432 = None
    for f, p, m in results:
        if abs(f - 432) < 1:
            result_432 = (f, p, m)
            break

    if result_432 is None:
        lines.append("ERROR: 432 Hz not found in results")
        return "\n".join(lines), "ERROR"

    freq_432, _, metrics_432 = result_432
    composite_432 = metrics_432['composite']

    # --- Ranking ---
    lines.append("")
    lines.append("--- RANKING ---")
    all_composites = sorted([(f, m['composite']) for f, _, m in results],
                            key=lambda x: x[1], reverse=True)
    rank_432 = next(i + 1 for i, (f, _) in enumerate(all_composites)
                    if abs(f - 432) < 1)
    total = len(all_composites)
    percentile = 100 * (1 - rank_432 / total)

    lines.append(f"432 Hz composite score: {composite_432:.4f}")
    lines.append(f"Rank: {rank_432}/{total} (percentile: {percentile:.1f}%)")
    lines.append("")
    lines.append("Top 10 frequencies by composite symmetry:")
    for i, (f, c) in enumerate(all_composites[:10]):
        marker = " <-- 432 Hz" if abs(f - 432) < 1 else ""
        fib_marker = " [3xF]" if f in FIBONACCI_SERIES else ""
        lines.append(f"  {i+1:2d}. {f:7.1f} Hz  composite={c:.4f}{fib_marker}{marker}")

    # --- Full results table ---
    lines.append("")
    lines.append("--- FULL RESULTS ---")
    lines.append(f"{'Freq':>8s}  {'C4':>7s}  {'C8':>7s}  {'Bilat':>7s}  "
                 f"{'Sharp':>7s}  {'Nodal':>5s}  {'Composite':>9s}  Category")
    lines.append("-" * 75)
    for f, _, m in sorted(results, key=lambda x: x[0]):
        if f in FIBONACCI_SERIES:
            cat = "Fibonacci"
        elif f in FINE_SCAN:
            cat = "Fine scan"
        elif f in CONTROLS:
            cat = "Control"
        else:
            cat = ""
        marker = " ***" if abs(f - 432) < 1 else ""
        lines.append(f"{f:8.1f}  {m['C4']:7.4f}  {m['C8']:7.4f}  "
                     f"{m['bilateral']:7.4f}  {m['sharpness']:7.4f}  "
                     f"{m['nodal_regions']:5d}  {m['composite']:9.4f}  "
                     f"{cat}{marker}")

    # --- Mann-Whitney U test ---
    lines.append("")
    lines.append("--- STATISTICAL TESTS ---")

    fine_scan_composites = [m['composite'] for f, _, m in results
                            if f in FINE_SCAN and abs(f - 432) > 1]

    if fine_scan_composites:
        # Compare 432 against fine-scan neighbors
        u_stat, p_mw = stats.mannwhitneyu(
            [composite_432], fine_scan_composites,
            alternative='greater'
        )
        lines.append(f"Mann-Whitney U (432 vs fine-scan neighbors):")
        lines.append(f"  U = {u_stat:.1f}, p = {p_mw:.4f}")
        lines.append(f"  432 composite: {composite_432:.4f}")
        lines.append(f"  Fine-scan mean: {np.mean(fine_scan_composites):.4f} "
                     f"+/- {np.std(fine_scan_composites):.4f}")
        if p_mw < 0.05:
            lines.append(f"  ** SIGNIFICANT at p < 0.05 **")
        else:
            lines.append(f"  Not significant (p > 0.05)")
    else:
        p_mw = 1.0
        lines.append("  (insufficient fine-scan data for test)")

    # --- Category comparison ---
    lines.append("")
    lines.append("--- CATEGORY COMPARISON ---")
    fib_composites = [m['composite'] for f, _, m in results if f in FIBONACCI_SERIES]
    ctrl_composites = [m['composite'] for f, _, m in results if f in CONTROLS]

    if fib_composites and ctrl_composites:
        u2, p_cat = stats.mannwhitneyu(fib_composites, ctrl_composites,
                                        alternative='greater')
        lines.append(f"Fibonacci series vs Controls:")
        lines.append(f"  Fibonacci mean: {np.mean(fib_composites):.4f} "
                     f"+/- {np.std(fib_composites):.4f}")
        lines.append(f"  Controls mean:  {np.mean(ctrl_composites):.4f} "
                     f"+/- {np.std(ctrl_composites):.4f}")
        lines.append(f"  U = {u2:.1f}, p = {p_cat:.4f}")
    else:
        p_cat = 1.0

    # --- Sensitivity analysis ---
    verdict = "NULL"

    if sensitivity_results:
        lines.append("")
        lines.append("--- f_scale SENSITIVITY ANALYSIS (honesty check) ---")
        lines.append("If 432's advantage appears only at specific f_scale values,")
        lines.append("it is an eigenmode proximity artifact, not intrinsic.")
        lines.append("")

        ranks_432 = []
        advantages_432 = []

        for fs, fs_results in sorted(sensitivity_results.items()):
            composites = [(f, m['composite']) for f, _, m in fs_results]
            composites_sorted = sorted(composites, key=lambda x: x[1], reverse=True)
            rank = next(i + 1 for i, (f, _) in enumerate(composites_sorted)
                        if abs(f - 432) < 1)
            total_fs = len(composites_sorted)
            composite_val = next(c for f, c in composites if abs(f - 432) < 1)
            mean_others = np.mean([c for f, c in composites if abs(f - 432) > 1])
            advantage = composite_val - mean_others

            ranks_432.append(rank)
            advantages_432.append(advantage)

            lines.append(f"  f_scale={fs:.2f}: rank={rank}/{total_fs}, "
                         f"composite={composite_val:.4f}, "
                         f"advantage={advantage:+.4f}")

        # Determine if advantage is robust
        mean_advantage = np.mean(advantages_432)
        std_advantage = np.std(advantages_432)
        fraction_top_half = sum(1 for r in ranks_432
                                if r <= len(composites_sorted) / 2) / len(ranks_432)

        lines.append("")
        lines.append(f"  Mean advantage: {mean_advantage:+.4f} +/- {std_advantage:.4f}")
        lines.append(f"  Fraction in top half: {fraction_top_half:.1%}")

        # Verdict logic
        if mean_advantage > 0.02 and fraction_top_half >= 0.8 and std_advantage < 0.02:
            verdict = "SIGNIFICANT"
            lines.append(f"  Advantage is ROBUST across f_scale values")
        elif mean_advantage > 0.01 and fraction_top_half >= 0.6:
            verdict = "WEAK"
            lines.append(f"  Advantage is WEAK — partially f_scale dependent")
        elif std_advantage > abs(mean_advantage):
            verdict = "ARTIFACT"
            lines.append(f"  Advantage is an ARTIFACT — strongly f_scale dependent")
        else:
            verdict = "NULL"
            lines.append(f"  No consistent advantage detected")
    else:
        # Without sensitivity analysis, base verdict on ranking alone
        if rank_432 <= 3 and p_mw < 0.05:
            verdict = "SIGNIFICANT (unconfirmed — run with --sensitivity)"
        elif rank_432 <= total // 2:
            verdict = "WEAK (unconfirmed — run with --sensitivity)"
        else:
            verdict = "NULL"

    # --- Verdict ---
    lines.append("")
    lines.append("=" * 60)
    lines.append("VERDICT")
    lines.append("=" * 60)

    verdict_explanations = {
        "SIGNIFICANT": ("432 Hz shows robust symmetry advantage across plate "
                        "parameters. The mathematical structure of 3 x F(12) "
                        "correlates with measurable pattern symmetry."),
        "WEAK": ("432 Hz shows some symmetry advantage, but it is partially "
                 "dependent on plate parameters (f_scale). The result is "
                 "suggestive but not conclusive."),
        "ARTIFACT": ("432 Hz advantage is an ARTIFACT of eigenmode proximity. "
                     "The symmetry depends on which eigenmodes happen to be "
                     "near the driving frequency, which is plate-dependent. "
                     "No intrinsic mathematical privilege detected."),
        "NULL": ("No symmetry advantage for 432 Hz detected. The Chladni "
                 "pattern symmetry at 432 Hz is not distinguishable from "
                 "neighboring frequencies."),
    }

    # Extract base verdict (without parenthetical)
    base_verdict = verdict.split(" (")[0]
    explanation = verdict_explanations.get(base_verdict, "")

    lines.append(f"Verdict: {verdict}")
    lines.append("")
    lines.append(explanation)
    lines.append("")
    lines.append("Note: Chladni pattern symmetry is determined primarily by")
    lines.append("eigenmode proximity, which depends on plate geometry (f_scale),")
    lines.append("not on the driving frequency's number-theoretic properties.")
    lines.append("This is the expected physical result.")

    summary = "\n".join(lines)
    return summary, verdict


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Cymatics 432 Hz — Chladni Pattern Symmetry Analysis')
    parser.add_argument('--grid', type=int, default=DEFAULT_GRID,
                        help=f'Grid resolution (default: {DEFAULT_GRID})')
    parser.add_argument('--max-mode', type=int, default=DEFAULT_MAX_MODE,
                        help=f'Maximum mode number (default: {DEFAULT_MAX_MODE})')
    parser.add_argument('--Q', type=int, default=DEFAULT_Q,
                        help=f'Quality factor (default: {DEFAULT_Q})')
    parser.add_argument('--f-scale', type=float, default=DEFAULT_F_SCALE,
                        help=f'Eigenfrequency scale (default: {DEFAULT_F_SCALE})')
    parser.add_argument('--sensitivity', action='store_true',
                        help='Run f_scale sensitivity analysis (honesty check)')
    args = parser.parse_args()

    print("=" * 60)
    print("CYMATICS 432 Hz — CHLADNI PATTERN SYMMETRY ANALYSIS")
    print("=" * 60)
    print(f"  Grid: {args.grid}x{args.grid}")
    print(f"  Max mode: {args.max_mode}")
    print(f"  Q factor: {args.Q}")
    print(f"  f_scale: {args.f_scale}")
    print(f"  Sensitivity: {args.sensitivity}")
    print()

    # Build frequency list (deduplicated and sorted)
    all_freqs = sorted(set(FIBONACCI_SERIES + FINE_SCAN + CONTROLS))
    print(f"Testing {len(all_freqs)} frequencies: "
          f"{min(all_freqs)}-{max(all_freqs)} Hz")
    print()

    # --- Step 1: Main frequency sweep ---
    print("--- Step 1: Frequency Sweep ---")
    results = run_sweep(all_freqs, args.f_scale, args.Q, args.grid, args.max_mode)

    # --- Step 2: Sensitivity analysis ---
    sensitivity_results = None
    if args.sensitivity:
        print()
        print("--- Step 2: f_scale Sensitivity Analysis ---")
        sensitivity_results = {}
        for fs in SENSITIVITY_F_SCALES:
            print(f"\n  f_scale = {fs:.2f}:")
            fs_results = run_sweep(all_freqs, fs, args.Q, args.grid, args.max_mode)
            sensitivity_results[fs] = fs_results
    else:
        print()
        print("--- Step 2: Skipping sensitivity (use --sensitivity to enable) ---")

    # --- Step 3: Generate plots ---
    print()
    print("--- Step 3: Generating Plots ---")
    plot_chladni_patterns(results)
    plot_symmetry_vs_frequency(results)
    plot_fibonacci_convergence()
    plot_statistical_comparison(results)

    # --- Step 4: Statistical analysis + verdict ---
    print()
    print("--- Step 4: Statistical Analysis ---")
    summary, verdict = statistical_analysis(results, sensitivity_results)
    print()
    print(summary)

    # Save summary
    with open(RESULTS_DIR / 'statistical_summary.txt', 'w') as f:
        f.write(summary)
    print(f"\nSaved to {RESULTS_DIR / 'statistical_summary.txt'}")
    print(f"All plots saved to {RESULTS_DIR}/")


if __name__ == '__main__':
    main()
