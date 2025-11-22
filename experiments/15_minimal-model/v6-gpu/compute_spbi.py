"""
SPBI Analysis Script for v6-gpu Experiment Data
Computes Stability-Probability Balance Index and related metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

# Data file paths
DATA_DIR = Path(r"W:\foundation\15 experiment\v6-gpu")
OUTPUT_DIR = DATA_DIR

DATA_FILES = {
    1: DATA_DIR / "v6_gpu_1d_results.csv",
    2: DATA_DIR / "v6_gpu_2d_results.csv",
    3: DATA_DIR / "v6_gpu_3d_results.csv",
    4: DATA_DIR / "v6_gpu_4d_results.csv",
    5: DATA_DIR / "v6_gpu_5d_results.csv"
}

print("=" * 80)
print("SPBI ANALYSIS - v6-gpu Experiment")
print("=" * 80)
print()

# Load all data
print("Loading data files...")
all_data = []
for dim, filepath in DATA_FILES.items():
    print(f"  Loading {dim}D data from {filepath.name}...")
    df = pd.read_csv(filepath)
    # Ensure dimension column exists
    if 'dimension' not in df.columns:
        df['dimension'] = dim
    all_data.append(df)
    print(f"    Loaded {len(df)} runs")

combined_df = pd.concat(all_data, ignore_index=True)
print(f"\nTotal runs loaded: {len(combined_df)}")
print(f"Dimensions: {sorted(combined_df['dimension'].unique())}")
print()

# Check for missing values in key columns
print("Data quality check:")
print(f"  Missing max_salience: {combined_df['max_salience'].isna().sum()}")
print(f"  Missing num_sources: {combined_df['num_sources'].isna().sum()}")
print(f"  Missing geometry: {combined_df['geometry'].isna().sum()}")
print(f"  Missing phase_offset: {combined_df['phase_offset'].isna().sum()}")
print()

# Remove any rows with missing critical data
combined_df = combined_df.dropna(subset=['max_salience', 'num_sources', 'gamma', 'T'])
print(f"After removing missing data: {len(combined_df)} runs")
print()

# Count runs per dimension
print("Runs per dimension:")
for dim in sorted(combined_df['dimension'].unique()):
    count = len(combined_df[combined_df['dimension'] == dim])
    print(f"  {dim}D: {count} runs")
print()

# ============================================================================
# METRIC COMPUTATION FUNCTIONS
# ============================================================================

def compute_cv(data, value_col='max_salience'):
    """Compute Coefficient of Variation (CV) = σ / μ"""
    values = data[value_col]
    if len(values) < 2:
        return np.nan
    mean = values.mean()
    std = values.std()
    if mean == 0:
        return np.nan
    return std / mean

def compute_source_correlation(data, value_col='max_salience'):
    """Compute correlation between num_sources and max_salience"""
    if len(data) < 3:
        return np.nan
    # Use Pearson correlation
    corr, pval = stats.pearsonr(data['num_sources'], data[value_col])
    return corr

def compute_slf(rho):
    """Compute Stability Lock Factor: SLF = 1 - ρ, clamped to [0, 1]"""
    slf = 1 - rho
    return np.clip(slf, 0, 1)

def compute_gpn_geometry(data, value_col='max_salience'):
    """Compute Geometry/Phase Neutrality for geometry"""
    if 'geometry' not in data.columns:
        return np.nan

    symmetric = data[data['geometry'] == 'symmetric'][value_col]
    clustered = data[data['geometry'] == 'clustered'][value_col]

    if len(symmetric) == 0 or len(clustered) == 0:
        return np.nan

    mu_symmetric = symmetric.mean()
    mu_clustered = clustered.mean()
    mu_all = data[value_col].mean()

    if mu_all == 0:
        return np.nan

    gpn = 1 - abs(mu_symmetric - mu_clustered) / mu_all
    return gpn

def compute_gpn_phase(data, value_col='max_salience'):
    """Compute Geometry/Phase Neutrality for phase_offset"""
    if 'phase_offset' not in data.columns:
        return np.nan

    phase0 = data[data['phase_offset'] == 0][value_col]
    phase1 = data[data['phase_offset'] == 1][value_col]

    if len(phase0) == 0 or len(phase1) == 0:
        return np.nan

    mu_phase0 = phase0.mean()
    mu_phase1 = phase1.mean()
    mu_all = data[value_col].mean()

    if mu_all == 0:
        return np.nan

    gpn = 1 - abs(mu_phase0 - mu_phase1) / mu_all
    return gpn

def compute_spbi(cv, slf):
    """Compute SPBI = CV / SLF"""
    if slf == 0 or np.isnan(slf) or np.isnan(cv):
        return np.nan
    return cv / slf

def classify_verdict(spbi, cv, slf, gpn):
    """Classify dimension based on SPBI and other metrics"""
    if np.isnan(spbi):
        return "INSUFFICIENT_DATA"

    # Target SPBI band: 0.05 - 0.10
    if spbi > 0.15:
        return "TOO_UNSTABLE"
    elif 0.05 <= spbi <= 0.10:
        if slf > 0.7 and gpn > 0.90:
            return "UNIVERSE_LIKE"
        else:
            return "NEAR_UNIVERSE_LIKE"
    elif spbi < 0.02:
        return "TOO_STABLE"
    else:
        # 0.02 <= SPBI < 0.05 or 0.10 < SPBI <= 0.15
        return "MODERATE"

# ============================================================================
# PER-DIMENSION ANALYSIS
# ============================================================================

print("=" * 80)
print("COMPUTING METRICS PER DIMENSION")
print("=" * 80)
print()

dimension_results = []

for dim in sorted(combined_df['dimension'].unique()):
    print(f"\n{'-' * 80}")
    print(f"Dimension: {dim}D")
    print(f"{'-' * 80}")

    dim_data = combined_df[combined_df['dimension'] == dim]
    print(f"Total runs: {len(dim_data)}")

    # Overall metrics
    cv = compute_cv(dim_data)
    rho = compute_source_correlation(dim_data)
    slf = compute_slf(rho)
    gpn_geom = compute_gpn_geometry(dim_data)
    gpn_phase = compute_gpn_phase(dim_data)
    gpn = np.nanmean([gpn_geom, gpn_phase])
    spbi = compute_spbi(cv, slf)
    verdict = classify_verdict(spbi, cv, slf, gpn)

    print(f"  CV (Residual Variance):        {cv:.6f}")
    print(f"  rho (Source Correlation):      {rho:.6f}")
    print(f"  SLF (Stability Lock Factor):   {slf:.6f}")
    print(f"  GPN_geom:                      {gpn_geom:.6f}")
    print(f"  GPN_phase:                     {gpn_phase:.6f}")
    print(f"  GPN (combined):                {gpn:.6f}")
    print(f"  SPBI:                          {spbi:.6f}")
    print(f"  Verdict:                       {verdict}")

    # Store results
    dimension_results.append({
        'dimension': dim,
        'n_runs': len(dim_data),
        'CV': cv,
        'rho': rho,
        'SLF': slf,
        'GPN_geom': gpn_geom,
        'GPN_phase': gpn_phase,
        'GPN': gpn,
        'SPBI': spbi,
        'verdict': verdict,
        'mean_max_salience': dim_data['max_salience'].mean(),
        'std_max_salience': dim_data['max_salience'].std()
    })

# Create summary dataframe
summary_df = pd.DataFrame(dimension_results)

# ============================================================================
# PER-CONFIGURATION ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("COMPUTING METRICS PER CONFIGURATION")
print("=" * 80)
print()

detailed_results = []

for dim in sorted(combined_df['dimension'].unique()):
    dim_data = combined_df[combined_df['dimension'] == dim]

    # Group by gamma and T
    for (gamma, T), group in dim_data.groupby(['gamma', 'T']):
        if len(group) < 3:
            continue  # Skip configs with too few runs

        cv = compute_cv(group)
        rho = compute_source_correlation(group)
        slf = compute_slf(rho)
        gpn_geom = compute_gpn_geometry(group)
        gpn_phase = compute_gpn_phase(group)
        gpn = np.nanmean([gpn_geom, gpn_phase])
        spbi = compute_spbi(cv, slf)

        detailed_results.append({
            'dimension': dim,
            'gamma': gamma,
            'T': T,
            'n_runs': len(group),
            'CV': cv,
            'rho': rho,
            'SLF': slf,
            'GPN_geom': gpn_geom,
            'GPN_phase': gpn_phase,
            'GPN': gpn,
            'SPBI': spbi,
            'mean_max_salience': group['max_salience'].mean(),
            'std_max_salience': group['max_salience'].std()
        })

detailed_df = pd.DataFrame(detailed_results)

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)
print()

# Save summary
summary_path = OUTPUT_DIR / "spbi_analysis.csv"
summary_df.to_csv(summary_path, index=False)
print(f"Saved: {summary_path}")

# Save detailed
detailed_path = OUTPUT_DIR / "spbi_detailed.csv"
detailed_df.to_csv(detailed_path, index=False)
print(f"Saved: {detailed_path}")

# Save quick verdict
verdict_path = OUTPUT_DIR / "spbi_verdict.txt"
with open(verdict_path, 'w') as f:
    f.write("SPBI ANALYSIS - QUICK VERDICT\n")
    f.write("=" * 80 + "\n\n")
    f.write("Target SPBI range for 'Universe-Like' substrate: 0.05 - 0.10\n\n")

    for _, row in summary_df.iterrows():
        f.write(f"{int(row['dimension'])}D: SPBI = {row['SPBI']:.6f} | Verdict: {row['verdict']}\n")
        f.write(f"     CV={row['CV']:.4f}, SLF={row['SLF']:.4f}, GPN={row['GPN']:.4f}\n\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write("KEY FINDINGS:\n\n")

    universe_like = summary_df[summary_df['verdict'].str.contains('UNIVERSE')]
    if len(universe_like) > 0:
        f.write(f"Universe-like dimensions: {', '.join([f'{int(d)}D' for d in universe_like['dimension']])}\n")
    else:
        f.write("No dimensions fall in the ideal 'Universe-Like' range.\n")

    too_stable = summary_df[summary_df['verdict'] == 'TOO_STABLE']
    if len(too_stable) > 0:
        f.write(f"Too stable (over-determined): {', '.join([f'{int(d)}D' for d in too_stable['dimension']])}\n")

    too_unstable = summary_df[summary_df['verdict'] == 'TOO_UNSTABLE']
    if len(too_unstable) > 0:
        f.write(f"Too unstable (chaotic): {', '.join([f'{int(d)}D' for d in too_unstable['dimension']])}\n")

print(f"Saved: {verdict_path}")

# ============================================================================
# VISUALIZATION
# ============================================================================

print("\n" + "=" * 80)
print("GENERATING VISUALIZATION")
print("=" * 80)
print()

fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Panel 1: SPBI vs Dimension
ax1 = fig.add_subplot(gs[0, 0])
dims = summary_df['dimension'].values
spbi_vals = summary_df['SPBI'].values
ax1.plot(dims, spbi_vals, 'o-', linewidth=2, markersize=10, color='#2E86AB')
ax1.axhspan(0.05, 0.10, alpha=0.2, color='green', label='Universe-Like Range')
ax1.set_xlabel('Dimension', fontweight='bold')
ax1.set_ylabel('SPBI', fontweight='bold')
ax1.set_title('SPBI vs Dimension', fontweight='bold', fontsize=12)
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xticks(dims)

# Panel 2: CV vs Dimension
ax2 = fig.add_subplot(gs[0, 1])
cv_vals = summary_df['CV'].values
ax2.plot(dims, cv_vals, 'o-', linewidth=2, markersize=10, color='#A23B72')
ax2.set_xlabel('Dimension', fontweight='bold')
ax2.set_ylabel('CV (Coefficient of Variation)', fontweight='bold')
ax2.set_title('Residual Variance (CV) vs Dimension', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3)
ax2.set_xticks(dims)

# Panel 3: SLF vs Dimension
ax3 = fig.add_subplot(gs[0, 2])
slf_vals = summary_df['SLF'].values
ax3.plot(dims, slf_vals, 'o-', linewidth=2, markersize=10, color='#F18F01')
ax3.set_xlabel('Dimension', fontweight='bold')
ax3.set_ylabel('SLF (Stability Lock Factor)', fontweight='bold')
ax3.set_title('Stability Lock Factor vs Dimension', fontweight='bold', fontsize=12)
ax3.grid(True, alpha=0.3)
ax3.set_xticks(dims)
ax3.set_ylim([0, 1.05])

# Panel 4: GPN vs Dimension
ax4 = fig.add_subplot(gs[1, 0])
gpn_vals = summary_df['GPN'].values
gpn_geom_vals = summary_df['GPN_geom'].values
gpn_phase_vals = summary_df['GPN_phase'].values
ax4.plot(dims, gpn_vals, 'o-', linewidth=2, markersize=10, label='GPN (combined)', color='#06A77D')
ax4.plot(dims, gpn_geom_vals, 's--', linewidth=1.5, markersize=7, label='GPN_geom', color='#06A77D', alpha=0.6)
ax4.plot(dims, gpn_phase_vals, '^--', linewidth=1.5, markersize=7, label='GPN_phase', color='#06A77D', alpha=0.6)
ax4.set_xlabel('Dimension', fontweight='bold')
ax4.set_ylabel('GPN (Geometry/Phase Neutrality)', fontweight='bold')
ax4.set_title('Neutrality vs Dimension', fontweight='bold', fontsize=12)
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_xticks(dims)
ax4.set_ylim([0.85, 1.01])

# Panel 5: SPBI breakdown by (gamma, T) - heatmap for each dimension
ax5 = fig.add_subplot(gs[1, 1:])
# Create a pivot table for heatmap
pivot_data = detailed_df.pivot_table(values='SPBI',
                                      index=['dimension', 'gamma'],
                                      columns='T',
                                      aggfunc='mean')
# Create custom labels for y-axis
y_labels = [f"{int(dim)}D γ={gamma}" for dim, gamma in pivot_data.index]
sns.heatmap(pivot_data.values, annot=True, fmt='.3f', cmap='RdYlGn_r',
            cbar_kws={'label': 'SPBI'}, ax=ax5,
            yticklabels=y_labels, xticklabels=pivot_data.columns)
ax5.set_xlabel('Horizon T', fontweight='bold')
ax5.set_ylabel('Dimension & Damping', fontweight='bold')
ax5.set_title('SPBI by Configuration (Dimension, γ, T)', fontweight='bold', fontsize=12)

# Panel 6: Phase space: CV vs SLF with SPBI contours
ax6 = fig.add_subplot(gs[2, :])
scatter = ax6.scatter(summary_df['SLF'], summary_df['CV'],
                     c=summary_df['SPBI'], s=200, cmap='viridis',
                     edgecolors='black', linewidth=1.5, alpha=0.7)
# Add dimension labels
for _, row in summary_df.iterrows():
    ax6.annotate(f"{int(row['dimension'])}D",
                (row['SLF'], row['CV']),
                fontsize=11, fontweight='bold',
                ha='center', va='center')
# Add SPBI contours
slf_range = np.linspace(0.1, 1.0, 100)
for spbi_val in [0.02, 0.05, 0.10, 0.15]:
    cv_contour = spbi_val * slf_range
    ax6.plot(slf_range, cv_contour, '--', alpha=0.5, linewidth=1.5,
            label=f'SPBI = {spbi_val}')
ax6.set_xlabel('SLF (Stability Lock Factor)', fontweight='bold')
ax6.set_ylabel('CV (Coefficient of Variation)', fontweight='bold')
ax6.set_title('Phase Space: CV vs SLF with SPBI Contours', fontweight='bold', fontsize=12)
ax6.legend(loc='upper left')
ax6.grid(True, alpha=0.3)
cbar = plt.colorbar(scatter, ax=ax6)
cbar.set_label('SPBI', fontweight='bold')

plt.suptitle('SPBI Analysis - v6-gpu Experiment',
             fontsize=16, fontweight='bold', y=0.995)

viz_path = OUTPUT_DIR / "spbi_visualization.png"
plt.savefig(viz_path, dpi=150, bbox_inches='tight')
print(f"Saved: {viz_path}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
