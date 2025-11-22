import pandas as pd
import numpy as np
import json

def ttest_ind(a, b):
    """Simple t-test implementation"""
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return 0, 1
    var1, var2 = np.var(a, ddof=1), np.var(b, ddof=1)
    pooled_se = np.sqrt(var1/n1 + var2/n2)
    if pooled_se == 0:
        return 0, 1
    t = (np.mean(a) - np.mean(b)) / pooled_se
    return t, 0  # Return t-stat only, p-value approximation not needed

# Load all CSV files
print("Loading CSV files...")
df_1d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_1d_results.csv')
df_2d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_2d_results.csv')
df_3d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_3d_results.csv')
df_4d = pd.read_csv(r'W:\foundation\15 experiment\v6-gpu\v6_gpu_4d_results.csv')

# Combine all data
df_all = pd.concat([df_1d, df_2d, df_3d, df_4d], ignore_index=True)

print(f"\nTotal records loaded: {len(df_all)}")
print(f"1D: {len(df_1d)}, 2D: {len(df_2d)}, 3D: {len(df_3d)}, 4D: {len(df_4d)}")
print(f"\nColumns: {df_all.columns.tolist()}")

# ==============================================================================
# BASIC STATISTICS
# ==============================================================================
print("\n" + "="*80)
print("BASIC STATISTICS BY DIMENSION")
print("="*80)

for d in [1, 2, 3, 4]:
    df_d = df_all[df_all['dimension'] == d]
    print(f"\n{d}D Results:")
    print(f"  Total runs: {len(df_d)}")
    print(f"  Runs with commits: {df_d['has_commits'].sum()} ({100*df_d['has_commits'].mean():.1f}%)")
    print(f"  Alpha range: {df_d['alpha_0'].min():.3f} to {df_d['alpha_0'].max():.3f}")
    print(f"  Num sources: {sorted(df_d['num_sources'].unique())}")
    print(f"  Geometries: {sorted(df_d['geometry'].unique())}")
    print(f"  Phase offsets: {sorted(df_d['phase_offset'].unique())}")
    print(f"  Gammas: {sorted(df_d['gamma'].unique())}")
    print(f"  T values: {sorted(df_d['T'].unique())}")

# ==============================================================================
# H1: BINARY JUMP WEAKENS WITH INCREASING DIMENSION
# ==============================================================================
print("\n" + "="*80)
print("H1: BINARY JUMP WEAKENS WITH INCREASING DIMENSION")
print("="*80)

# Analyze threshold transitions for each dimension
# Binary jump = sharp transition from no commits to commits as alpha increases

results_h1 = []

for d in [1, 2, 3, 4]:
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
                        ].sort_values('alpha_0')

                        if len(subset) < 3:
                            continue

                        # Find threshold: minimum alpha where commits occur
                        commits_subset = subset[subset['has_commits'] == True]
                        no_commits_subset = subset[subset['has_commits'] == False]

                        if len(commits_subset) > 0 and len(no_commits_subset) > 0:
                            alpha_threshold = commits_subset['alpha_0'].min()
                            alpha_below = no_commits_subset[no_commits_subset['alpha_0'] < alpha_threshold]['alpha_0'].max()

                            # Compute transition sharpness
                            # Look at commit rate gradient near threshold
                            near_threshold = subset[
                                (subset['alpha_0'] >= alpha_threshold - 0.3) &
                                (subset['alpha_0'] <= alpha_threshold + 0.3)
                            ].copy()

                            if len(near_threshold) > 2:
                                # Compute gradient of commit rate vs alpha
                                near_threshold['commit_rate_filled'] = near_threshold['commit_rate'].fillna(0)
                                alphas = near_threshold['alpha_0'].values
                                rates = near_threshold['commit_rate_filled'].values

                                if len(alphas) > 1 and alphas[-1] > alphas[0]:
                                    gradient = (rates[-1] - rates[0]) / (alphas[-1] - alphas[0])

                                    results_h1.append({
                                        'dimension': d,
                                        'num_sources': ms,
                                        'geometry': geom,
                                        'phase_offset': phase,
                                        'gamma': gamma,
                                        'T': T,
                                        'alpha_threshold': alpha_threshold,
                                        'alpha_below': alpha_below,
                                        'threshold_gap': alpha_threshold - alpha_below,
                                        'gradient': gradient
                                    })

df_h1 = pd.DataFrame(results_h1)

print("\nThreshold Jump Analysis (mean threshold gap by dimension):")
for d in [1, 2, 3, 4]:
    d_data = df_h1[df_h1['dimension'] == d]
    if len(d_data) > 0:
        print(f"{d}D: gap = {d_data['threshold_gap'].mean():.4f} ± {d_data['threshold_gap'].std():.4f}, "
              f"gradient = {d_data['gradient'].mean():.3f} ± {d_data['gradient'].std():.3f}")

print("\nStatistical test (threshold gap decreasing with dimension):")
for i, d in enumerate([1, 2, 3, 4]):
    d_gaps = df_h1[df_h1['dimension'] == d]['threshold_gap'].values
    if i < 3:
        d_next_gaps = df_h1[df_h1['dimension'] == (d+1)]['threshold_gap'].values
        if len(d_gaps) > 0 and len(d_next_gaps) > 0:
            t_stat, _ = ttest_ind(d_gaps, d_next_gaps)
            print(f"  {d}D vs {d+1}D: t={t_stat:.3f}, mean_diff={np.mean(d_gaps)-np.mean(d_next_gaps):.4f}")

# ==============================================================================
# H2: GEOMETRY AND PHASE EFFECTS FOR d ≥ 2
# ==============================================================================
print("\n" + "="*80)
print("H2: GEOMETRY AND PHASE MEASURABLY AFFECT THRESHOLD AND COMMIT RATES FOR d ≥ 2")
print("="*80)

results_h2 = []

for d in [1, 2, 3, 4]:
    for ms in [1, 2, 4]:
        for gamma in [0.001, 0.005]:
            for T in [100, 200, 500]:
                # Compare geometries (phase=0)
                sym = df_all[
                    (df_all['dimension'] == d) &
                    (df_all['num_sources'] == ms) &
                    (df_all['geometry'] == 'symmetric') &
                    (df_all['phase_offset'] == 0) &
                    (df_all['gamma'] == gamma) &
                    (df_all['T'] == T)
                ]
                clust = df_all[
                    (df_all['dimension'] == d) &
                    (df_all['num_sources'] == ms) &
                    (df_all['geometry'] == 'clustered') &
                    (df_all['phase_offset'] == 0) &
                    (df_all['gamma'] == gamma) &
                    (df_all['T'] == T)
                ]

                if len(sym) > 0 and len(clust) > 0:
                    sym_commits = sym[sym['has_commits'] == True]
                    clust_commits = clust[clust['has_commits'] == True]

                    if len(sym_commits) > 0 and len(clust_commits) > 0:
                        alpha_sym = sym_commits['alpha_0'].min()
                        alpha_clust = clust_commits['alpha_0'].min()

                        # Get commit rates at same alpha
                        alpha_compare = max(alpha_sym, alpha_clust)
                        sym_rate = sym[sym['alpha_0'] == alpha_compare]['commit_rate'].mean()
                        clust_rate = clust[clust['alpha_0'] == alpha_compare]['commit_rate'].mean()

                        results_h2.append({
                            'dimension': d,
                            'num_sources': ms,
                            'gamma': gamma,
                            'T': T,
                            'comparison': 'geometry',
                            'alpha_diff': abs(alpha_sym - alpha_clust),
                            'rate_diff': abs(sym_rate - clust_rate) if not pd.isna(sym_rate) and not pd.isna(clust_rate) else np.nan
                        })

                # Compare phases (symmetric geometry)
                phase0 = df_all[
                    (df_all['dimension'] == d) &
                    (df_all['num_sources'] == ms) &
                    (df_all['geometry'] == 'symmetric') &
                    (df_all['phase_offset'] == 0) &
                    (df_all['gamma'] == gamma) &
                    (df_all['T'] == T)
                ]
                phase1 = df_all[
                    (df_all['dimension'] == d) &
                    (df_all['num_sources'] == ms) &
                    (df_all['geometry'] == 'symmetric') &
                    (df_all['phase_offset'] == 1) &
                    (df_all['gamma'] == gamma) &
                    (df_all['T'] == T)
                ]

                if len(phase0) > 0 and len(phase1) > 0:
                    p0_commits = phase0[phase0['has_commits'] == True]
                    p1_commits = phase1[phase1['has_commits'] == True]

                    if len(p0_commits) > 0 and len(p1_commits) > 0:
                        alpha_p0 = p0_commits['alpha_0'].min()
                        alpha_p1 = p1_commits['alpha_0'].min()

                        # Get commit rates at same alpha
                        alpha_compare = max(alpha_p0, alpha_p1)
                        p0_rate = phase0[phase0['alpha_0'] == alpha_compare]['commit_rate'].mean()
                        p1_rate = phase1[phase1['alpha_0'] == alpha_compare]['commit_rate'].mean()

                        results_h2.append({
                            'dimension': d,
                            'num_sources': ms,
                            'gamma': gamma,
                            'T': T,
                            'comparison': 'phase',
                            'alpha_diff': abs(alpha_p0 - alpha_p1),
                            'rate_diff': abs(p0_rate - p1_rate) if not pd.isna(p0_rate) and not pd.isna(p1_rate) else np.nan
                        })

df_h2 = pd.DataFrame(results_h2)

print("\nGeometry effects by dimension (threshold difference):")
geom_effects = df_h2[df_h2['comparison'] == 'geometry'].groupby('dimension')['alpha_diff'].agg(['mean', 'std', 'count'])
print(geom_effects)

print("\nPhase effects by dimension (threshold difference):")
phase_effects = df_h2[df_h2['comparison'] == 'phase'].groupby('dimension')['alpha_diff'].agg(['mean', 'std', 'count'])
print(phase_effects)

print("\nSignificant effects (Δα ≥ 0.02):")
for d in [1, 2, 3, 4]:
    geom_sig = df_h2[(df_h2['dimension'] == d) & (df_h2['comparison'] == 'geometry') & (df_h2['alpha_diff'] >= 0.02)]
    phase_sig = df_h2[(df_h2['dimension'] == d) & (df_h2['comparison'] == 'phase') & (df_h2['alpha_diff'] >= 0.02)]
    print(f"{d}D: Geometry {len(geom_sig)}/{len(df_h2[(df_h2['dimension'] == d) & (df_h2['comparison'] == 'geometry')])}, "
          f"Phase {len(phase_sig)}/{len(df_h2[(df_h2['dimension'] == d) & (df_h2['comparison'] == 'phase')])}")

# ==============================================================================
# H3: TIME-DEPENDENT THRESHOLD PERSISTS
# ==============================================================================
print("\n" + "="*80)
print("H3: TIME-DEPENDENT THRESHOLD PERSISTS ACROSS DIMENSIONS")
print("="*80)

results_h3 = []

for d in [1, 2, 3, 4]:
    for ms in [1, 2, 4]:
        for geom in ['symmetric', 'clustered']:
            for phase in [0, 1]:
                for gamma in [0.001, 0.005]:
                    # Get thresholds for different T values
                    thresholds = {}
                    for T in [100, 200, 500]:
                        subset = df_all[
                            (df_all['dimension'] == d) &
                            (df_all['num_sources'] == ms) &
                            (df_all['geometry'] == geom) &
                            (df_all['phase_offset'] == phase) &
                            (df_all['gamma'] == gamma) &
                            (df_all['T'] == T) &
                            (df_all['has_commits'] == True)
                        ]
                        if len(subset) > 0:
                            thresholds[T] = subset['alpha_0'].min()

                    if len(thresholds) >= 2:
                        results_h3.append({
                            'dimension': d,
                            'num_sources': ms,
                            'geometry': geom,
                            'phase_offset': phase,
                            'gamma': gamma,
                            'T_100': thresholds.get(100, np.nan),
                            'T_200': thresholds.get(200, np.nan),
                            'T_500': thresholds.get(500, np.nan)
                        })

df_h3 = pd.DataFrame(results_h3)

print("\nThreshold scaling with T (mean by dimension):")
for d in [1, 2, 3, 4]:
    d_data = df_h3[df_h3['dimension'] == d]
    if len(d_data) > 0:
        print(f"{d}D:")
        print(f"  T=100: {d_data['T_100'].mean():.4f} ± {d_data['T_100'].std():.4f}")
        print(f"  T=200: {d_data['T_200'].mean():.4f} ± {d_data['T_200'].std():.4f}")
        print(f"  T=500: {d_data['T_500'].mean():.4f} ± {d_data['T_500'].std():.4f}")

        # Compute scaling exponent (α ∝ T^β)
        valid = d_data[d_data['T_100'].notna() & d_data['T_500'].notna()]
        if len(valid) > 0:
            log_ratio = np.log(valid['T_500'].mean() / valid['T_100'].mean())
            log_T_ratio = np.log(500 / 100)
            beta = log_ratio / log_T_ratio
            print(f"  Scaling: α(T=500)/α(T=100) = {valid['T_500'].mean()/valid['T_100'].mean():.3f}, β ≈ {beta:.3f}")

# ==============================================================================
# H4: THRESHOLD SCALING WITH NUM_SOURCES
# ==============================================================================
print("\n" + "="*80)
print("H4: THRESHOLD SCALES AS α₀ ∝ Mₛ^-β(d), WITH β(d) INCREASING TOWARD 0.5")
print("="*80)

results_h4 = []

for d in [1, 2, 3, 4]:
    for geom in ['symmetric', 'clustered']:
        for phase in [0, 1]:
            for gamma in [0.001, 0.005]:
                for T in [100, 200, 500]:
                    # Get thresholds for different num_sources
                    thresholds = {}
                    for ms in [1, 2, 4]:
                        subset = df_all[
                            (df_all['dimension'] == d) &
                            (df_all['num_sources'] == ms) &
                            (df_all['geometry'] == geom) &
                            (df_all['phase_offset'] == phase) &
                            (df_all['gamma'] == gamma) &
                            (df_all['T'] == T) &
                            (df_all['has_commits'] == True)
                        ]
                        if len(subset) > 0:
                            thresholds[ms] = subset['alpha_0'].min()

                    if len(thresholds) >= 2:
                        results_h4.append({
                            'dimension': d,
                            'geometry': geom,
                            'phase_offset': phase,
                            'gamma': gamma,
                            'T': T,
                            'Ms_1': thresholds.get(1, np.nan),
                            'Ms_2': thresholds.get(2, np.nan),
                            'Ms_4': thresholds.get(4, np.nan)
                        })

df_h4 = pd.DataFrame(results_h4)

print("\nThreshold scaling with Mₛ (mean by dimension):")
print("Format: Mₛ=1 -> Mₛ=2 -> Mₛ=4")
for d in [1, 2, 3, 4]:
    d_data = df_h4[df_h4['dimension'] == d]
    if len(d_data) > 0:
        print(f"{d}D:")
        print(f"  Mₛ=1: {d_data['Ms_1'].mean():.4f} ± {d_data['Ms_1'].std():.4f}")
        print(f"  Mₛ=2: {d_data['Ms_2'].mean():.4f} ± {d_data['Ms_2'].std():.4f}")
        print(f"  Mₛ=4: {d_data['Ms_4'].mean():.4f} ± {d_data['Ms_4'].std():.4f}")

        # Compute β from Ms=1 to Ms=4
        valid = d_data[d_data['Ms_1'].notna() & d_data['Ms_4'].notna()]
        if len(valid) > 0:
            ratio = valid['Ms_4'].mean() / valid['Ms_1'].mean()
            beta = -np.log(ratio) / np.log(4)
            print(f"  α(Mₛ=4)/α(Mₛ=1) = {ratio:.3f}, β ≈ {beta:.3f}")

# ==============================================================================
# H5: STABILIZATION FOR d ≥ 4
# ==============================================================================
print("\n" + "="*80)
print("H5: FOR d ≥ 4, THRESHOLD AND RATE SCALING STABILIZE")
print("="*80)

# Compare 3D vs 4D scaling parameters
print("\nComparing 3D vs 4D:")

# Threshold levels
for ms in [1, 2, 4]:
    alpha_3d = df_all[(df_all['dimension'] == 3) & (df_all['num_sources'] == ms) & (df_all['has_commits'] == True)]['alpha_0'].min()
    alpha_4d = df_all[(df_all['dimension'] == 4) & (df_all['num_sources'] == ms) & (df_all['has_commits'] == True)]['alpha_0'].min()
    print(f"  Mₛ={ms}: α_3D={alpha_3d:.4f}, α_4D={alpha_4d:.4f}, diff={abs(alpha_3d-alpha_4d):.4f}")

# Commit rates
print("\nCommit rate patterns (at threshold):")
for d in [1, 2, 3, 4]:
    # Get commit rates at threshold for each config
    rates = []
    for ms in [1, 2, 4]:
        subset = df_all[(df_all['dimension'] == d) & (df_all['num_sources'] == ms) & (df_all['has_commits'] == True)]
        if len(subset) > 0:
            threshold_alpha = subset['alpha_0'].min()
            threshold_rates = subset[subset['alpha_0'] == threshold_alpha]['commit_rate'].values
            rates.extend(threshold_rates)

    if len(rates) > 0:
        print(f"{d}D: mean={np.mean(rates):.3f}, std={np.std(rates):.3f}, n={len(rates)}")

# ==============================================================================
# DIMENSIONAL SCALING ANALYSIS
# ==============================================================================
print("\n" + "="*80)
print("DIMENSIONAL SCALING ANALYSIS")
print("="*80)

print("\nFirst commit time by dimension (mean ± std):")
for d in [1, 2, 3, 4]:
    commits = df_all[(df_all['dimension'] == d) & (df_all['has_commits'] == True)]
    if len(commits) > 0:
        fct = commits['first_commit_time']
        print(f"{d}D: {fct.mean():.2f} ± {fct.std():.2f} timesteps (n={len(fct)})")

print("\nSalience amplification (max_salience) by dimension:")
for d in [1, 2, 3, 4]:
    d_data = df_all[df_all['dimension'] == d]
    if len(d_data) > 0:
        print(f"{d}D: {d_data['max_salience'].mean():.6f} ± {d_data['max_salience'].std():.6f}")

print("\nCommit rate scaling with Mₛ:")
for d in [1, 2, 3, 4]:
    print(f"{d}D:")
    for ms in [1, 2, 4]:
        commits = df_all[(df_all['dimension'] == d) & (df_all['num_sources'] == ms) & (df_all['has_commits'] == True)]
        if len(commits) > 0:
            print(f"  Mₛ={ms}: {commits['commit_rate'].mean():.3f} ± {commits['commit_rate'].std():.3f}")

# ==============================================================================
# SUMMARY STATISTICS
# ==============================================================================
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

summary = []
for d in [1, 2, 3, 4]:
    for ms in [1, 2, 4]:
        subset = df_all[(df_all['dimension'] == d) & (df_all['num_sources'] == ms)]
        commits = subset[subset['has_commits'] == True]

        if len(commits) > 0:
            summary.append({
                'dimension': d,
                'num_sources': ms,
                'n_configs': len(subset),
                'commit_pct': 100 * len(commits) / len(subset),
                'threshold_min': commits['alpha_0'].min(),
                'threshold_mean': commits['alpha_0'].mean(),
                'commit_rate_mean': commits['commit_rate'].mean(),
                'first_commit_mean': commits['first_commit_time'].mean(),
                'max_salience_mean': commits['max_salience'].mean()
            })

df_summary = pd.DataFrame(summary)
print(df_summary.to_string(index=False))

# Save results
df_summary.to_csv(r'W:\foundation\15 experiment\v6-gpu\analysis_summary.csv', index=False)
df_h1.to_csv(r'W:\foundation\15 experiment\v6-gpu\h1_binary_jump.csv', index=False)
df_h2.to_csv(r'W:\foundation\15 experiment\v6-gpu\h2_geometry_phase.csv', index=False)
df_h3.to_csv(r'W:\foundation\15 experiment\v6-gpu\h3_time_dependence.csv', index=False)
df_h4.to_csv(r'W:\foundation\15 experiment\v6-gpu\h4_source_scaling.csv', index=False)

print("\n" + "="*80)
print("Analysis complete. Results saved to CSV files.")
print("="*80)
