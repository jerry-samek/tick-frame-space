import pandas as pd
import numpy as np

# Load all CSV files
print("Loading CSV files...")
df_1d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_1d_results.csv')
df_2d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_2d_results.csv')
df_3d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_3d_results.csv')
df_4d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_4d_results.csv')
df_5d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_5d_results.csv')

# Combine all data
df_all = pd.concat([df_1d, df_2d, df_3d, df_4d, df_5d], ignore_index=True)

print(f"\n{'='*80}")
print("COMPREHENSIVE 5D ANALYSIS")
print(f"{'='*80}")
print(f"\nTotal records: {len(df_all)}")
print(f"1D: {len(df_1d)}, 2D: {len(df_2d)}, 3D: {len(df_3d)}, 4D: {len(df_4d)}, 5D: {len(df_5d)}")

# ==============================================================================
# KEY METRICS BY DIMENSION
# ==============================================================================
print(f"\n{'='*80}")
print("KEY METRICS BY DIMENSION (Ms=2, symmetric, phi=0, gamma=0.001, T=200)")
print(f"{'='*80}")

metrics_table = []
for d in [1, 2, 3, 4, 5]:
    subset = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 2) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]

    if len(subset) > 0:
        metrics_table.append({
            'Dimension': d,
            'Commit Rate': subset['commit_rate'].mean(),
            'First Commit': subset['first_commit_time'].mean(),
            'Max Salience': subset['max_salience'].mean(),
            'Final Psi': subset['final_psi'].mean()
        })

df_metrics = pd.DataFrame(metrics_table)
print("\n", df_metrics.to_string(index=False))

# ==============================================================================
# GRADIENT ANALYSIS (H1)
# ==============================================================================
print(f"\n{'='*80}")
print("H1: MAX GRADIENT BY DIMENSION (T=100)")
print(f"{'='*80}")

gradient_table = []
for d in [1, 2, 3, 4, 5]:
    for ms in [1, 2, 4]:
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

            gradient_table.append({
                'Dimension': d,
                'Ms': ms,
                'Max Gradient': max_grad
            })

df_gradients = pd.DataFrame(gradient_table)
print("\n", df_gradients.to_string(index=False))

# Calculate gradient reduction
print("\nGradient Reduction (Ms=4):")
for d_start, d_end in [(1, 2), (2, 3), (3, 4), (4, 5)]:
    grad_start = df_gradients[(df_gradients['Dimension'] == d_start) & (df_gradients['Ms'] == 4)]['Max Gradient'].values[0]
    grad_end = df_gradients[(df_gradients['Dimension'] == d_end) & (df_gradients['Ms'] == 4)]['Max Gradient'].values[0]
    reduction = 100 * (grad_start - grad_end) / grad_start
    print(f"  {d_start}D -> {d_end}D: {grad_start:.2f} -> {grad_end:.2f} ({reduction:.1f}% reduction)")

# ==============================================================================
# SCALING EXPONENT RHO (H4)
# ==============================================================================
print(f"\n{'='*80}")
print("H4: SOURCE SCALING EXPONENT rho(d)")
print(f"{'='*80}")

rho_table = []
for d in [1, 2, 3, 4, 5]:
    rates = {}
    for ms in [1, 2, 4]:
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
        rho_table.append({
            'Dimension': d,
            'Ms=1 Rate': rates[1],
            'Ms=4 Rate': rates[4],
            'Ratio (4/1)': rates[4] / rates[1],
            'rho': rho
        })

df_rho = pd.DataFrame(rho_table)
print("\n", df_rho.to_string(index=False))

# ==============================================================================
# COEFFICIENT OF VARIATION (H5 - Stabilization)
# ==============================================================================
print(f"\n{'='*80}")
print("H5: COEFFICIENT OF VARIATION (Stability Metric)")
print(f"{'='*80}")

cv_table = []
for d in [1, 2, 3, 4, 5]:
    for ms in [1, 2, 4]:
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
                cv_table.append({
                    'Dimension': d,
                    'Ms': ms,
                    'Mean Rate': mean_rate,
                    'Std Dev': std_rate,
                    'CV %': cv
                })

df_cv = pd.DataFrame(cv_table)
print("\n", df_cv.to_string(index=False))

# ==============================================================================
# 4D-5D STABILIZATION COMPARISON
# ==============================================================================
print(f"\n{'='*80}")
print("4D -> 5D STABILIZATION ANALYSIS")
print(f"{'='*80}")

stabilization_table = []
for ms in [1, 2, 4]:
    # Commit rate
    rate_4d = df_all[
        (df_all['dimension'] == 4) &
        (df_all['num_sources'] == ms) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    rate_5d = df_all[
        (df_all['dimension'] == 5) &
        (df_all['num_sources'] == ms) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    # First commit time
    fct_4d = df_all[
        (df_all['dimension'] == 4) &
        (df_all['num_sources'] == ms) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['first_commit_time'].mean()

    fct_5d = df_all[
        (df_all['dimension'] == 5) &
        (df_all['num_sources'] == ms) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['first_commit_time'].mean()

    if not pd.isna(rate_4d) and not pd.isna(rate_5d):
        stabilization_table.append({
            'Ms': ms,
            '4D Rate': rate_4d,
            '5D Rate': rate_5d,
            'Rate Delta%': 100 * abs(rate_4d - rate_5d) / rate_4d,
            '4D FCT': fct_4d,
            '5D FCT': fct_5d,
            'FCT Delta%': 100 * abs(fct_4d - fct_5d) / fct_4d if not pd.isna(fct_4d) else np.nan
        })

df_stab = pd.DataFrame(stabilization_table)
print("\n", df_stab.to_string(index=False))

mean_rate_delta = df_stab['Rate Delta%'].mean()
print(f"\nMean rate change 4D->5D: {mean_rate_delta:.2f}%")
if mean_rate_delta < 5:
    print("CHECK STABILIZATION CONFIRMED (< 5% change)")
elif mean_rate_delta < 10:
    print("~ NEAR STABILIZATION (5-10% change)")
else:
    print("X NOT YET STABILIZED (> 10% change)")

# ==============================================================================
# SALIENCE EXPLOSION
# ==============================================================================
print(f"\n{'='*80}")
print("SALIENCE AMPLIFICATION ACROSS DIMENSIONS")
print(f"{'='*80}")

sal_table = []
sal_1d = None
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
        if sal_1d is None:
            sal_1d = sal
        amplification = sal / sal_1d
        sal_table.append({
            'Dimension': d,
            'Max Salience': sal,
            'Amplification vs 1D': amplification
        })

df_sal = pd.DataFrame(sal_table)
print("\n", df_sal.to_string(index=False))

# ==============================================================================
# GEOMETRY AND PHASE EFFECTS (H2)
# ==============================================================================
print(f"\n{'='*80}")
print("H2: GEOMETRY AND PHASE EFFECTS (5D)")
print(f"{'='*80}")

print("\nGeometry Effects (symmetric vs clustered, Ms=4, alpha=1.0, T=200):")
for d in [2, 3, 4, 5]:
    sym = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    clust = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['geometry'] == 'clustered') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    if not pd.isna(sym) and not pd.isna(clust):
        diff_pct = 100 * abs(sym - clust) / max(sym, clust)
        sig = " ***" if diff_pct >= 10 else ""
        print(f"  {d}D: sym={sym:.3f}, clust={clust:.3f}, Delta={diff_pct:.2f}%{sig}")

print("\nPhase Effects (phi=0 vs phi=pi, Ms=4, alpha=1.0, T=200):")
for d in [1, 2, 3, 4, 5]:
    p0 = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    p1 = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 4) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 1) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    if not pd.isna(p0) and not pd.isna(p1):
        diff_pct = 100 * abs(p0 - p1) / max(p0, p1)
        sig = " ***" if diff_pct >= 10 else ""
        print(f"  {d}D: phi=0: {p0:.3f}, phi=pi: {p1:.3f}, Delta={diff_pct:.2f}%{sig}")

# ==============================================================================
# SUMMARY TABLE FOR ALL DIMENSIONS
# ==============================================================================
print(f"\n{'='*80}")
print("COMPREHENSIVE SUMMARY TABLE")
print(f"{'='*80}")

summary = []
for d in [1, 2, 3, 4, 5]:
    for ms in [1, 2, 4]:
        for geom in ['symmetric', 'clustered']:
            for phase in [0, 1]:
                for gamma in [0.001, 0.005]:
                    for T in [100, 200, 500]:
                        subset = df_all[
                            (df_all['dimension'] == d) &
                            (df_all['num_sources'] == ms) &
                            (df_all['geometry'] == geom) &
                            (df_all['phase_offset'] == phase) &
                            (df_all['gamma'] == gamma) &
                            (df_all['T'] == T)
                        ]

                        if len(subset) > 0:
                            summary.append({
                                'd': d,
                                'Ms': ms,
                                'geom': geom[:4],
                                'phi': phase,
                                'gamma': gamma,
                                'T': int(T),
                                'n': len(subset),
                                'alpha_min': subset['alpha_0'].min(),
                                'alpha_max': subset['alpha_0'].max(),
                                'rate_mean': subset['commit_rate'].mean(),
                                'rate_std': subset['commit_rate'].std(),
                                'fct_mean': subset['first_commit_time'].mean(),
                                'sal_max': subset['max_salience'].mean()
                            })

df_summary = pd.DataFrame(summary)
df_summary.to_csv(r'W:\foundation\15 experiment\v6-gpu\analysis_summary.csv', index=False)
print(f"\nFull summary saved to: analysis_summary.csv ({len(df_summary)} rows)")

# Show sample
print("\nSample (Ms=2, symmetric, phi=0, gamma=0.001, T=200):")
sample = df_summary[
    (df_summary['Ms'] == 2) &
    (df_summary['geom'] == 'symm') &
    (df_summary['phi'] == 0) &
    (df_summary['gamma'] == 0.001) &
    (df_summary['T'] == 200)
][['d', 'n', 'rate_mean', 'rate_std', 'fct_mean', 'sal_max']]
print(sample.to_string(index=False))

print(f"\n{'='*80}")
print("ANALYSIS COMPLETE - All dimensions 1D-5D analyzed")
print(f"{'='*80}")
