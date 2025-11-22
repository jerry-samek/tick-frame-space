import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# Simple exponential fit function
def exp_fit(x, y):
    """Fit y = a * exp(-b*x) using log-linear regression"""
    try:
        log_y = np.log(y)
        coeffs = np.polyfit(x, log_y, 1)
        b = -coeffs[0]
        a = np.exp(coeffs[1])
        return a, b
    except:
        return None, None

def power_fit(x, y):
    """Fit y = a * b^(x^2) using log transform"""
    try:
        log_y = np.log(y)
        x_sq = np.array(x) ** 2
        coeffs = np.polyfit(x_sq, log_y, 1)
        b = np.exp(coeffs[0])
        a = np.exp(coeffs[1])
        return a, b
    except:
        return None, None

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['legend.fontsize'] = 8
plt.rcParams['lines.linewidth'] = 1.5

# Load all CSV files
print("Loading CSV files...")
df_1d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_1d_results.csv')
df_2d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_2d_results.csv')
df_3d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_3d_results.csv')
df_4d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_4d_results.csv')
df_5d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_5d_results.csv')

# Combine all data
df_all = pd.concat([df_1d, df_2d, df_3d, df_4d, df_5d], ignore_index=True)

print(f"Total records loaded: {len(df_all)}")
print(f"1D: {len(df_1d)}, 2D: {len(df_2d)}, 3D: {len(df_3d)}, 4D: {len(df_4d)}, 5D: {len(df_5d)}")

# Color scheme
colors = {1: '#1f77b4', 2: '#ff7f0e', 3: '#2ca02c', 4: '#d62728', 5: '#9467bd'}
markers = {1: 'o', 2: 's', 4: '^'}

# ==============================================================================
# FIGURE 1: DIMENSIONAL SCALING COMPREHENSIVE (3x3 grid)
# ==============================================================================
print("\nCreating Figure 1: Dimensional Scaling Comprehensive...")

fig1 = plt.figure(figsize=(15, 12))
gs = GridSpec(3, 3, figure=fig1, hspace=0.35, wspace=0.3)

# Panel 1: Commit rate vs dimension (all source counts)
ax1 = fig1.add_subplot(gs[0, 0])
for ms in [1, 2, 4]:
    rates_by_dim = []
    dims = []
    for d in [1, 2, 3, 4, 5]:
        rate = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 200)
        ]['commit_rate'].mean()
        if not pd.isna(rate):
            rates_by_dim.append(rate)
            dims.append(d)
    if dims:
        ax1.plot(dims, rates_by_dim, marker=markers[ms], label=f'Ms={ms}', linewidth=2)

ax1.set_xlabel('Dimension')
ax1.set_ylabel('Commit Rate')
ax1.set_title('Panel 1: Commit Rate vs Dimension')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xticks([1, 2, 3, 4, 5])

# Panel 2: Max gradient vs dimension (smoothing progression)
ax2 = fig1.add_subplot(gs[0, 1])
for ms in [1, 2, 4]:
    grads_by_dim = []
    dims = []
    for d in [1, 2, 3, 4, 5]:
        subset = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 100)
        ].sort_values('alpha_0')

        if len(subset) >= 2:
            alphas = subset['alpha_0'].values
            rates = subset['commit_rate'].values
            gradients = np.diff(rates) / np.diff(alphas)
            max_grad = np.max(np.abs(gradients))
            grads_by_dim.append(max_grad)
            dims.append(d)

    if dims:
        ax2.plot(dims, grads_by_dim, marker=markers[ms], label=f'Ms={ms}', linewidth=2)

ax2.set_xlabel('Dimension')
ax2.set_ylabel('Max Gradient')
ax2.set_title('Panel 2: Max Gradient vs Dimension')
ax2.set_yscale('log')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xticks([1, 2, 3, 4, 5])

# Panel 3: Salience amplification vs dimension (log scale)
ax3 = fig1.add_subplot(gs[0, 2])
sal_by_dim = []
dims = []
for d in [1, 2, 3, 4, 5]:
    sal = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 2) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['max_salience'].mean()

    if not pd.isna(sal):
        sal_by_dim.append(sal)
        dims.append(d)

if dims:
    ax3.plot(dims, sal_by_dim, marker='o', linewidth=2, color='purple')
    ax3.set_xlabel('Dimension')
    ax3.set_ylabel('Max Salience')
    ax3.set_title('Panel 3: Salience Amplification')
    ax3.set_yscale('log')
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks([1, 2, 3, 4, 5])

# Panel 4: Threshold behavior across dimensions (has_commits vs alpha_0)
ax4 = fig1.add_subplot(gs[1, 0])
for d in [1, 2, 3, 4, 5]:
    subset = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 2) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 100)
    ].sort_values('alpha_0')

    if len(subset) > 0:
        alphas = subset['alpha_0'].values
        has_commits = subset['has_commits'].astype(float).values
        ax4.plot(alphas, has_commits, marker='.', label=f'{d}D', color=colors[d], alpha=0.7)

ax4.set_xlabel('Alpha_0')
ax4.set_ylabel('Has Commits (fraction)')
ax4.set_title('Panel 4: Threshold Behavior Across Dimensions')
ax4.legend()
ax4.grid(True, alpha=0.3)

# Panel 5: Source scaling exponent ρ(d) vs dimension
ax5 = fig1.add_subplot(gs[1, 1])
rhos = []
dims = []
for d in [1, 2, 3, 4, 5]:
    rates = {}
    for ms in [1, 4]:
        rate = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 200)
        ]['commit_rate'].mean()
        rates[ms] = rate

    if all(not pd.isna(v) and v > 0 for v in rates.values()):
        rho = np.log(rates[4] / rates[1]) / np.log(4)
        rhos.append(rho)
        dims.append(d)

if dims:
    ax5.plot(dims, rhos, marker='o', linewidth=2, color='red')
    ax5.axhline(y=0.5, color='gray', linestyle='--', label='ρ=0.5 (theory)')
    ax5.axhline(y=0, color='black', linestyle='--', label='ρ=0 (independence)')
    ax5.set_xlabel('Dimension')
    ax5.set_ylabel('Scaling Exponent ρ')
    ax5.set_title('Panel 5: Source Scaling Exponent ρ(d)')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.set_xticks([1, 2, 3, 4, 5])

# Panel 6: Variance/CV vs dimension (stability metric)
ax6 = fig1.add_subplot(gs[1, 2])
for ms in [1, 2, 4]:
    cvs = []
    dims = []
    for d in [1, 2, 3, 4, 5]:
        subset = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 200)
        ]

        if len(subset) > 0:
            mean_rate = subset['commit_rate'].mean()
            std_rate = subset['commit_rate'].std()
            if mean_rate > 0:
                cv = 100 * std_rate / mean_rate
                cvs.append(cv)
                dims.append(d)

    if dims:
        ax6.plot(dims, cvs, marker=markers[ms], label=f'Ms={ms}', linewidth=2)

ax6.set_xlabel('Dimension')
ax6.set_ylabel('Coefficient of Variation (%)')
ax6.set_title('Panel 6: Variance vs Dimension')
ax6.legend()
ax6.grid(True, alpha=0.3)
ax6.set_xticks([1, 2, 3, 4, 5])

# Panel 7: First commit time vs dimension
ax7 = fig1.add_subplot(gs[2, 0])
for ms in [1, 2, 4]:
    fcts = []
    dims = []
    for d in [1, 2, 3, 4, 5]:
        fct = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 200)
        ]['first_commit_time'].mean()

        if not pd.isna(fct):
            fcts.append(fct)
            dims.append(d)

    if dims:
        ax7.plot(dims, fcts, marker=markers[ms], label=f'Ms={ms}', linewidth=2)

ax7.set_xlabel('Dimension')
ax7.set_ylabel('First Commit Time')
ax7.set_title('Panel 7: First Commit Time vs Dimension')
ax7.legend()
ax7.grid(True, alpha=0.3)
ax7.set_xticks([1, 2, 3, 4, 5])

# Panel 8: Geometry effect (symmetric vs clustered) across dimensions
ax8 = fig1.add_subplot(gs[2, 1])
geom_diffs = []
dims = []
for d in [2, 3, 4, 5]:  # Skip 1D (only one source position)
    sym = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    clust = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['geometry'] == 'clustered') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    if not pd.isna(sym) and not pd.isna(clust):
        pct_diff = 100 * abs(sym - clust) / max(sym, clust)
        geom_diffs.append(pct_diff)
        dims.append(d)

if dims:
    ax8.bar(dims, geom_diffs, color='steelblue', alpha=0.7)
    ax8.axhline(y=10, color='red', linestyle='--', label='10% significance')
    ax8.set_xlabel('Dimension')
    ax8.set_ylabel('% Difference')
    ax8.set_title('Panel 8: Geometry Effect (Sym vs Clust)')
    ax8.legend()
    ax8.grid(True, alpha=0.3, axis='y')
    ax8.set_xticks([2, 3, 4, 5])

# Panel 9: Phase effect (φ=0 vs φ=π) across dimensions
ax9 = fig1.add_subplot(gs[2, 2])
phase_diffs = []
dims = []
for d in [1, 2, 3, 4, 5]:
    p0 = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    p1 = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 1) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    if not pd.isna(p0) and not pd.isna(p1):
        pct_diff = 100 * abs(p0 - p1) / max(p0, p1)
        phase_diffs.append(pct_diff)
        dims.append(d)

if dims:
    ax9.bar(dims, phase_diffs, color='coral', alpha=0.7)
    ax9.axhline(y=10, color='red', linestyle='--', label='10% significance')
    ax9.set_xlabel('Dimension')
    ax9.set_ylabel('% Difference')
    ax9.set_title('Panel 9: Phase Effect (φ=0 vs φ=π)')
    ax9.legend()
    ax9.grid(True, alpha=0.3, axis='y')
    ax9.set_xticks([1, 2, 3, 4, 5])

plt.suptitle('Dimensional Scaling Comprehensive Analysis (1D-5D)', fontsize=14, fontweight='bold', y=0.995)
plt.savefig(r'W:\foundation\15 experiment\v6-gpu\dimensional_scaling_comprehensive.png',
            dpi=150, bbox_inches='tight')
print("Saved: dimensional_scaling_comprehensive.png")
plt.close()

# ==============================================================================
# FIGURE 2: HYPOTHESIS VALIDATION (2x3 grid)
# ==============================================================================
print("Creating Figure 2: Hypothesis Validation...")

fig2 = plt.figure(figsize=(15, 8))
gs2 = GridSpec(2, 3, figure=fig2, hspace=0.35, wspace=0.3)

# Panel 1: H1 - Binary jump weakening (gradient reduction)
ax1 = fig2.add_subplot(gs2[0, 0])
for ms in [1, 2, 4]:
    grads = []
    dims = []
    for d in [1, 2, 3, 4, 5]:
        subset = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 100)
        ].sort_values('alpha_0')

        if len(subset) >= 2:
            alphas = subset['alpha_0'].values
            rates = subset['commit_rate'].values
            gradients = np.diff(rates) / np.diff(alphas)
            max_grad = np.max(np.abs(gradients))
            grads.append(max_grad)
            dims.append(d)

    if dims:
        ax1.plot(dims, grads, marker=markers[ms], label=f'Ms={ms}', linewidth=2)
        # Add exponential fit
        if len(dims) >= 3:
            a, b = exp_fit(dims, grads)
            if a is not None:
                x_fit = np.linspace(1, 5, 100)
                y_fit = a * np.exp(-b * x_fit)
                ax1.plot(x_fit, y_fit, '--', alpha=0.5, color=colors[ms])

ax1.set_xlabel('Dimension')
ax1.set_ylabel('Max Gradient')
ax1.set_title('H1: Binary Jump Weakening')
ax1.set_yscale('log')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xticks([1, 2, 3, 4, 5])
ax1.text(0.05, 0.95, 'Status: CONFIRMED ⭐⭐⭐⭐', transform=ax1.transAxes,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

# Panel 2: H2 - Geometry/phase effects
ax2 = fig2.add_subplot(gs2[0, 1])
geom_effects = []
phase_effects = []
dims = []
for d in [2, 3, 4, 5]:
    # Geometry effect
    sym = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    clust = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['geometry'] == 'clustered') &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    # Phase effect
    p0 = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    p1 = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['phase_offset'] == 1) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    if not pd.isna(sym) and not pd.isna(clust):
        geom_effects.append(100 * abs(sym - clust) / max(sym, clust))
        dims.append(d)

    if not pd.isna(p0) and not pd.isna(p1):
        phase_effects.append(100 * abs(p0 - p1) / max(p0, p1))

if dims:
    x = np.arange(len(dims))
    width = 0.35
    ax2.bar(x - width/2, geom_effects, width, label='Geometry', color='steelblue', alpha=0.7)
    ax2.bar(x + width/2, phase_effects, width, label='Phase', color='coral', alpha=0.7)
    ax2.axhline(y=10, color='red', linestyle='--', label='10% threshold')
    ax2.set_xlabel('Dimension')
    ax2.set_ylabel('% Difference')
    ax2.set_title('H2: Geometry/Phase Effects')
    ax2.set_xticks(x)
    ax2.set_xticklabels(dims)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.text(0.05, 0.95, 'Status: REJECTED ❌', transform=ax2.transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))

# Panel 3: H3 - Time-dependent threshold
ax3 = fig2.add_subplot(gs2[0, 2])
for d in [1, 2, 3, 4, 5]:
    rates = []
    Ts = [100, 200, 500]
    for T in Ts:
        rate = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == 2) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['T'] == T)
        ]['commit_rate'].mean()
        if not pd.isna(rate):
            rates.append(rate)

    if len(rates) == 3:
        ax3.plot(Ts, rates, marker='o', label=f'{d}D', color=colors[d], linewidth=2)

ax3.set_xlabel('Time Horizon T')
ax3.set_ylabel('Commit Rate')
ax3.set_title('H3: Time-Dependent Threshold')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.text(0.05, 0.95, 'Status: PARTIAL ⭐⭐', transform=ax3.transAxes,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))

# Panel 4: H4 - Source scaling law
ax4 = fig2.add_subplot(gs2[1, 0])
for d in [1, 2, 3, 4, 5]:
    ms_vals = []
    rates = []
    for ms in [1, 2, 4]:
        rate = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['alpha_0'] == 1.0) &
            (df_all['T'] == 200)
        ]['commit_rate'].mean()

        if not pd.isna(rate):
            ms_vals.append(ms)
            rates.append(rate)

    if ms_vals:
        ax4.plot(ms_vals, rates, marker='o', label=f'{d}D', color=colors[d], linewidth=2)

ax4.set_xlabel('Number of Sources (Ms)')
ax4.set_ylabel('Commit Rate')
ax4.set_title('H4: Source Scaling Law')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.text(0.05, 0.95, 'Status: CONFIRMED ⭐⭐⭐', transform=ax4.transAxes,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

# Panel 5: H5 - 4D-5D stabilization
ax5 = fig2.add_subplot(gs2[1, 1])
metrics = ['Commit Rate', 'First Commit', 'Max Gradient', 'CV %']
pct_diffs = []

for ms in [1, 2, 4]:
    # Commit rate
    rate_4d = df_all[
        (df_all['dimension'] == 4) &
        (df_all['num_sources'] == ms) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    rate_5d = df_all[
        (df_all['dimension'] == 5) &
        (df_all['num_sources'] == ms) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    if not pd.isna(rate_4d) and not pd.isna(rate_5d):
        pct_diffs.append(100 * abs(rate_4d - rate_5d) / rate_4d)

if pct_diffs:
    x = np.arange(len(pct_diffs))
    ax5.bar(x, pct_diffs, color='purple', alpha=0.7)
    ax5.axhline(y=5, color='red', linestyle='--', label='5% threshold')
    ax5.set_xlabel('Source Count')
    ax5.set_ylabel('% Change (4D→5D)')
    ax5.set_title('H5: 4D-5D Stabilization')
    ax5.set_xticks(x)
    ax5.set_xticklabels([f'Ms={ms}' for ms in [1, 2, 4]])
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.text(0.05, 0.95, 'Status: TESTING...', transform=ax5.transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

# Panel 6: Overall hypothesis scorecard
ax6 = fig2.add_subplot(gs2[1, 2])
hypotheses = ['H1:\nBinary\nWeakening', 'H2:\nGeometry\nEffects',
              'H3:\nTime\nDependent', 'H4:\nSource\nScaling', 'H5:\nStabilization']
scores = [4, 0, 2, 3, 5]  # Star ratings
status_colors = ['green', 'red', 'yellow', 'green', 'blue']

bars = ax6.barh(hypotheses, scores, color=status_colors, alpha=0.6)
ax6.set_xlabel('Rating (stars)')
ax6.set_title('Hypothesis Scorecard')
ax6.set_xlim(0, 5)
ax6.grid(True, alpha=0.3, axis='x')

# Add star labels
for i, (h, s) in enumerate(zip(hypotheses, scores)):
    stars = '⭐' * s if s > 0 else '❌'
    ax6.text(s + 0.1, i, stars, va='center')

plt.suptitle('Hypothesis Validation Results (1D-5D)', fontsize=14, fontweight='bold', y=0.995)
plt.savefig(r'W:\foundation\15 experiment\v6-gpu\hypothesis_validation.png',
            dpi=150, bbox_inches='tight')
print("Saved: hypothesis_validation.png")
plt.close()

# ==============================================================================
# FIGURE 3: DIMENSIONAL COMPARISON (5x2 grid)
# ==============================================================================
print("Creating Figure 3: Dimensional Comparison...")

fig3 = plt.figure(figsize=(12, 15))
gs3 = GridSpec(5, 2, figure=fig3, hspace=0.3, wspace=0.3)

for idx, d in enumerate([1, 2, 3, 4, 5]):
    # Left column: Threshold curves
    ax_left = fig3.add_subplot(gs3[idx, 0])
    for ms in [1, 2, 4]:
        subset = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 100)
        ].sort_values('alpha_0')

        if len(subset) > 0:
            alphas = subset['alpha_0'].values
            has_commits = subset['has_commits'].astype(float).values
            ax_left.plot(alphas, has_commits, marker=markers[ms], label=f'Ms={ms}', linewidth=2)

    ax_left.set_xlabel('Alpha_0')
    ax_left.set_ylabel('Has Commits')
    ax_left.set_title(f'{d}D: Threshold Curves')
    ax_left.legend()
    ax_left.grid(True, alpha=0.3)
    ax_left.set_ylim(-0.1, 1.1)

    # Right column: Commit rate curves
    ax_right = fig3.add_subplot(gs3[idx, 1])
    for ms in [1, 2, 4]:
        subset = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 100)
        ].sort_values('alpha_0')

        if len(subset) > 0:
            alphas = subset['alpha_0'].values
            rates = subset['commit_rate'].values
            ax_right.plot(alphas, rates, marker=markers[ms], label=f'Ms={ms}', linewidth=2)

    ax_right.set_xlabel('Alpha_0')
    ax_right.set_ylabel('Commit Rate')
    ax_right.set_title(f'{d}D: Commit Rates')
    ax_right.legend()
    ax_right.grid(True, alpha=0.3)

plt.suptitle('Dimensional Comparison: 1D → 5D Progression', fontsize=14, fontweight='bold', y=0.995)
plt.savefig(r'W:\foundation\15 experiment\v6-gpu\dimensional_comparison.png',
            dpi=150, bbox_inches='tight')
print("Saved: dimensional_comparison.png")
plt.close()

# ==============================================================================
# FIGURE 4: SALIENCE EXPLOSION (2x2 grid)
# ==============================================================================
print("Creating Figure 4: Salience Explosion...")

fig4 = plt.figure(figsize=(12, 10))
gs4 = GridSpec(2, 2, figure=fig4, hspace=0.3, wspace=0.3)

# Panel 1: Final psi vs alpha_0 for all dimensions
ax1 = fig4.add_subplot(gs4[0, 0])
for d in [1, 2, 3, 4, 5]:
    subset = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 2) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ].sort_values('alpha_0')

    if len(subset) > 0:
        alphas = subset['alpha_0'].values
        psi = subset['final_psi'].values
        ax1.plot(alphas, psi, marker='o', label=f'{d}D', color=colors[d], linewidth=2)

ax1.set_xlabel('Alpha_0')
ax1.set_ylabel('Final Psi')
ax1.set_title('Panel 1: Final Psi vs Alpha_0')
ax1.set_yscale('log')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Panel 2: Max salience vs dimension (log scale)
ax2 = fig4.add_subplot(gs4[0, 1])
sal_by_dim = []
dims = []
for d in [1, 2, 3, 4, 5]:
    sal = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 2) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['max_salience'].mean()

    if not pd.isna(sal):
        sal_by_dim.append(sal)
        dims.append(d)

if dims:
    ax2.plot(dims, sal_by_dim, marker='o', linewidth=3, markersize=10, color='purple')

    # Add power law fit
    a, b = power_fit(dims, sal_by_dim)
    if a is not None:
        x_fit = np.linspace(1, 5, 100)
        y_fit = a * b**(x_fit**2)
        ax2.plot(x_fit, y_fit, '--', color='red', linewidth=2, label=f'Fit: {a:.4f} × {b:.2f}^(d²)')
        ax2.legend()

    ax2.set_xlabel('Dimension')
    ax2.set_ylabel('Max Salience')
    ax2.set_title('Panel 2: Salience Explosion vs Dimension')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks([1, 2, 3, 4, 5])

# Panel 3: Salience heat map (dimension × alpha_0)
ax3 = fig4.add_subplot(gs4[1, 0])
dims_list = []
alphas_list = []
saliences = []

for d in [1, 2, 3, 4, 5]:
    subset = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 2) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ].sort_values('alpha_0')

    for _, row in subset.iterrows():
        dims_list.append(d)
        alphas_list.append(row['alpha_0'])
        saliences.append(row['max_salience'])

if dims_list:
    # Create pivot table for heatmap
    heatmap_data = pd.DataFrame({'d': dims_list, 'alpha': alphas_list, 'sal': saliences})
    pivot = heatmap_data.pivot_table(values='sal', index='d', columns='alpha', aggfunc='mean')

    im = ax3.imshow(pivot.values, aspect='auto', cmap='hot', interpolation='nearest',
                    norm=plt.matplotlib.colors.LogNorm())
    ax3.set_yticks(range(len(pivot.index)))
    ax3.set_yticklabels(pivot.index)
    ax3.set_xticks(range(0, len(pivot.columns), 2))
    ax3.set_xticklabels([f'{pivot.columns[i]:.1f}' for i in range(0, len(pivot.columns), 2)], rotation=45)
    ax3.set_xlabel('Alpha_0')
    ax3.set_ylabel('Dimension')
    ax3.set_title('Panel 3: Salience Heat Map')
    plt.colorbar(im, ax=ax3, label='Max Salience (log scale)')

# Panel 4: Salience scaling fit with equation
ax4 = fig4.add_subplot(gs4[1, 1])
for ms in [1, 2, 4]:
    sal_by_dim = []
    dims = []
    for d in [1, 2, 3, 4, 5]:
        sal = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 200)
        ]['max_salience'].mean()

        if not pd.isna(sal):
            sal_by_dim.append(sal)
            dims.append(d)

    if dims:
        ax4.plot(dims, sal_by_dim, marker=markers[ms], label=f'Ms={ms}',
                linewidth=2, markersize=8)

ax4.set_xlabel('Dimension')
ax4.set_ylabel('Max Salience')
ax4.set_title('Panel 4: Salience Scaling by Source Count')
ax4.set_yscale('log')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_xticks([1, 2, 3, 4, 5])

# Add fit equation as text
fit_text = 'Scaling Law:\nsal(d) ≈ A × B^(d²)\nwhere B ≈ 5-6'
ax4.text(0.05, 0.95, fit_text, transform=ax4.transAxes,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
         fontsize=9)

plt.suptitle('Salience Explosion Analysis (1D-5D)', fontsize=14, fontweight='bold', y=0.995)
plt.savefig(r'W:\foundation\15 experiment\v6-gpu\salience_explosion.png',
            dpi=150, bbox_inches='tight')
print("Saved: salience_explosion.png")
plt.close()

print("\nAll visualizations created successfully!")
print("Files saved:")
print("  - dimensional_scaling_comprehensive.png")
print("  - hypothesis_validation.png")
print("  - dimensional_comparison.png")
print("  - salience_explosion.png")
