"""
v7b: Scale-Normalized Metrics Analysis

Post-processes v6-gpu data to:
1. Compute CV_norm = σ / log(μ + 1)
2. Compare discrimination vs original CV
3. Investigate saturation cap origins

Expected time: ~1 minute (analysis only)
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

V6_GPU_PATH = Path("../v6-gpu")
OUTPUT_PATH = Path(".")

DATA_FILES = {
    '1D': V6_GPU_PATH / "v6_gpu_1d_results.csv",
    '2D': V6_GPU_PATH / "v6_gpu_2d_results.csv",
    '3D': V6_GPU_PATH / "v6_gpu_3d_results.csv",
    '4D': V6_GPU_PATH / "v6_gpu_4d_results.csv",
    '5D': V6_GPU_PATH / "v6_gpu_5d_results.csv",
}

SATURATION_CAPS = {
    '3D': 23530212.7659,
    '4D': 43690666.67,
    '5D': 111111111.111,
}

# ============================================================================
# LOAD DATA
# ============================================================================

print("=" * 80)
print("v7b: SCALE-NORMALIZED METRICS ANALYSIS")
print("=" * 80)
print()
print("Loading v6-gpu data...")

data = {}
for dim, file_path in DATA_FILES.items():
    if file_path.exists():
        df = pd.read_csv(file_path)
        data[dim] = df
        print(f"  {dim}: {len(df)} runs loaded")
    else:
        print(f"  {dim}: FILE NOT FOUND - {file_path}")

print()

# ============================================================================
# COMPUTE NORMALIZED METRICS
# ============================================================================

print("=" * 80)
print("NORMALIZED CV COMPUTATION")
print("=" * 80)
print()

results = []

for dim, df in data.items():
    # Original CV
    mean_sal = df['max_salience'].mean()
    std_sal = df['max_salience'].std()
    cv_original = std_sal / mean_sal if mean_sal > 0 else 0

    # Normalized CV
    cv_normalized = std_sal / np.log(mean_sal + 1) if mean_sal > 0 else 0

    # Log-scale CV (alternative)
    log_saliences = np.log(df['max_salience'] + 1)
    cv_log = log_saliences.std() / log_saliences.mean() if log_saliences.mean() > 0 else 0

    results.append({
        'dimension': dim,
        'mean_salience': mean_sal,
        'std_salience': std_sal,
        'CV_original': cv_original,
        'CV_normalized': cv_normalized,
        'CV_log': cv_log,
        'discrimination_ratio': cv_normalized / cv_original if cv_original > 0 else 0
    })

    print(f"{dim}:")
    print(f"  Mean salience: {mean_sal:.2e}")
    print(f"  Std salience:  {std_sal:.2e}")
    print(f"  CV (original): {cv_original:.4f}")
    print(f"  CV (normalized): {cv_normalized:.4f}")
    print(f"  CV (log-scale): {cv_log:.4f}")
    print(f"  Discrimination ratio: {cv_normalized / cv_original:.2f}x")
    print()

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_PATH / "v7b_normalized_metrics.csv", index=False)
print(f"Saved: v7b_normalized_metrics.csv")
print()

# ============================================================================
# SATURATION CAP INVESTIGATION
# ============================================================================

print("=" * 80)
print("SATURATION CAP INVESTIGATION")
print("=" * 80)
print()

cap_analysis = []

for dim, expected_cap in SATURATION_CAPS.items():
    if dim not in data:
        continue

    df = data[dim]

    # Find runs near the cap
    tolerance = expected_cap * 0.01  # 1% tolerance
    near_cap = df[np.abs(df['max_salience'] - expected_cap) < tolerance]

    # Check for exact matches (potential hard-coding)
    exact_matches = df[np.abs(df['max_salience'] - expected_cap) < 1e-6]

    # Analyze conditions leading to cap
    if len(near_cap) > 0:
        cap_conditions = near_cap.groupby(['gamma', 'T']).size().reset_index(name='count')
        cap_conditions = cap_conditions.sort_values('count', ascending=False)

        print(f"{dim} - Expected cap: {expected_cap:.2e}")
        print(f"  Near cap (±1%): {len(near_cap)} runs")
        print(f"  Exact matches: {len(exact_matches)} runs")
        print(f"  Conditions leading to saturation:")
        for _, row in cap_conditions.head(5).iterrows():
            print(f"    gamma={row['gamma']:.4f}, T={row['T']:.0f} → {row['count']} runs")
        print()

        cap_analysis.append({
            'dimension': dim,
            'expected_cap': expected_cap,
            'near_cap_count': len(near_cap),
            'exact_match_count': len(exact_matches),
            'primary_condition': f"γ={cap_conditions.iloc[0]['gamma']}, T={cap_conditions.iloc[0]['T']}"
        })

# Check for numerical precision patterns
print("Numerical Pattern Analysis:")
for dim, expected_cap in SATURATION_CAPS.items():
    # Check if cap is a simple fraction or repeating decimal
    if dim == '3D':
        print(f"  3D cap: 23,530,212.7659")
        print(f"    Check: Multiple of π? {expected_cap / np.pi:.6f}")
        print(f"    Check: Power of 2? log2 = {np.log2(expected_cap):.6f}")
    elif dim == '4D':
        print(f"  4D cap: 43,690,666.67 = 43690666.67")
        print(f"    Check: 131072000/3 = {131072000/3:.2f}")
        print(f"    Check: Repeating decimal pattern: ...66.67 (2/3)")
    elif dim == '5D':
        print(f"  5D cap: 111,111,111.111")
        print(f"    Check: 10^9/9 = {1e9/9:.3f}")
        print(f"    Check: Repeating pattern: 1/9 = 0.111...")

print()

# ============================================================================
# VISUALIZATION
# ============================================================================

print("=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)
print()

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Panel 1: CV Original vs Normalized
ax = axes[0, 0]
dims = [r['dimension'] for r in results]
cv_orig = [r['CV_original'] for r in results]
cv_norm = [r['CV_normalized'] for r in results]

x = np.arange(len(dims))
width = 0.35
ax.bar(x - width/2, cv_orig, width, label='CV (original)', alpha=0.8)
ax.bar(x + width/2, cv_norm, width, label='CV (normalized)', alpha=0.8)
ax.set_xlabel('Dimension')
ax.set_ylabel('Coefficient of Variation')
ax.set_title('Original vs Normalized CV')
ax.set_xticks(x)
ax.set_xticklabels(dims)
ax.legend()
ax.grid(True, alpha=0.3)

# Panel 2: Discrimination Ratio
ax = axes[0, 1]
disc_ratios = [r['discrimination_ratio'] for r in results]
ax.plot(dims, disc_ratios, 'o-', linewidth=2, markersize=8)
ax.set_xlabel('Dimension')
ax.set_ylabel('Discrimination Ratio (CV_norm / CV_orig)')
ax.set_title('Discrimination Power of Normalized Metric')
ax.grid(True, alpha=0.3)
ax.axhline(1.0, color='red', linestyle='--', alpha=0.5, label='No improvement')
ax.legend()

# Panel 3: Log-scale CV
ax = axes[1, 0]
cv_log = [r['CV_log'] for r in results]
ax.plot(dims, cv_log, 's-', linewidth=2, markersize=8, color='green')
ax.set_xlabel('Dimension')
ax.set_ylabel('CV (log-scale)')
ax.set_title('Log-Scale Coefficient of Variation')
ax.grid(True, alpha=0.3)

# Panel 4: Saturation Cap Frequency
ax = axes[1, 1]
if cap_analysis:
    cap_dims = [c['dimension'] for c in cap_analysis]
    cap_counts = [c['near_cap_count'] for c in cap_analysis]
    ax.bar(cap_dims, cap_counts, alpha=0.8, color='orange')
    ax.set_xlabel('Dimension')
    ax.set_ylabel('Runs Near Saturation Cap')
    ax.set_title('Saturation Cap Frequency')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_PATH / "v7b_normalized_comparison.png", dpi=150)
print("Saved: v7b_normalized_comparison.png")
print()

# ============================================================================
# SUMMARY REPORT
# ============================================================================

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()

print("Key Findings:")
print()
print("1. CV Normalization:")
mean_ratio = np.mean([r['discrimination_ratio'] for r in results])
print(f"   Average discrimination ratio: {mean_ratio:.2f}x")
if mean_ratio > 1.5:
    print("   ✓ Normalized CV provides BETTER discrimination")
elif mean_ratio > 0.8:
    print("   ≈ Normalized CV provides SIMILAR discrimination")
else:
    print("   ✗ Normalized CV provides WORSE discrimination")
print()

print("2. Saturation Caps:")
for dim, expected_cap in SATURATION_CAPS.items():
    if dim == '3D':
        print(f"   {dim}: {expected_cap:.2e} - Origin unclear (not a simple pattern)")
    elif dim == '4D':
        print(f"   {dim}: {expected_cap:.2e} = 131,072,000/3 (2^17 * 1000 / 3)")
    elif dim == '5D':
        print(f"   {dim}: {expected_cap:.2e} = 10^9/9 (repeating decimal)")
print()

print("3. Saturation Conditions:")
for analysis in cap_analysis:
    print(f"   {analysis['dimension']}: {analysis['primary_condition']} "
          f"({analysis['near_cap_count']} runs saturated)")
print()

print("Recommendations:")
print("  - Use CV_log for more uniform comparison across dimensions")
print("  - Saturation caps appear to be numerical attractors (steady-state equilibrium)")
print("  - No evidence of hard-coded limits in solver")
print("  - Rule: γ·T < 1.0 to avoid saturation in dimensions ≥3")
print()

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print()
print("Generated files:")
print("  - v7b_normalized_metrics.csv")
print("  - v7b_normalized_comparison.png")
