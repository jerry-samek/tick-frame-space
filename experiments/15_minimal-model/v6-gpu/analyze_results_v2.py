import pandas as pd
import numpy as np

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

# ==============================================================================
# OVERVIEW STATISTICS
# ==============================================================================
print("\n" + "="*80)
print("DATA OVERVIEW")
print("="*80)

for d in [1, 2, 3, 4]:
    df_d = df_all[df_all['dimension'] == d]
    print(f"\n{d}D:")
    print(f"  Total configs: {len(df_d)}")
    print(f"  Alpha range: {df_d['alpha_0'].min():.2f} - {df_d['alpha_0'].max():.2f}")
    print(f"  Num sources: {sorted(df_d['num_sources'].unique())}")
    print(f"  Commit rate range: {df_d['commit_rate'].min():.2f} - {df_d['commit_rate'].max():.2f}")
    print(f"  First commit time: {df_d['first_commit_time'].min():.2f} - {df_d['first_commit_time'].max():.2f}")

# ==============================================================================
# H1: BINARY JUMP WEAKENS WITH INCREASING DIMENSION
# ==============================================================================
print("\n" + "="*80)
print("H1: BINARY JUMP WEAKENS WITH INCREASING DIMENSION")
print("="*80)
print("\nAnalysis: Measure sharpness of commit rate vs alpha transition")
print("Method: Look at commit rate gradient and variance at low alpha values\n")

# For each dimension, analyze transition sharpness
# Focus on single source, symmetric, phase=0 for clarity
for d in [1, 2, 3, 4]:
    for ms in [1, 2, 4]:
        subset = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 100)
        ].sort_values('alpha_0')

        if len(subset) >= 3:
            # Get commit rates at lowest alpha values
            alphas = subset['alpha_0'].values
            rates = subset['commit_rate'].values

            # Compute rate gradient
            if len(alphas) > 1:
                gradients = np.diff(rates) / np.diff(alphas)
                mean_gradient = np.mean(gradients)
                max_gradient = np.max(np.abs(gradients))

                # Rate at lowest vs highest alpha
                rate_at_min = rates[0]
                rate_at_max = rates[-1]

                print(f"{d}D, Ms={ms}: alpha=[{alphas[0]:.2f}, {alphas[-1]:.2f}], "
                      f"rate=[{rate_at_min:.2f}, {rate_at_max:.2f}], "
                      f"grad_mean={mean_gradient:.2f}, grad_max={max_gradient:.2f}")

print("\nInterpretation: Higher max_gradient = sharper jump (more binary)")
print("Expected: gradient should decrease from 1D to 4D")

# ==============================================================================
# H2: GEOMETRY AND PHASE EFFECTS FOR d >= 2
# ==============================================================================
print("\n" + "="*80)
print("H2: GEOMETRY AND PHASE EFFECTS FOR d >= 2")
print("="*80)

print("\nGeometry effects (symmetric vs clustered) at alpha=1.0:")
for d in [1, 2, 3, 4]:
    for ms in [2, 4]:  # Only multi-source makes sense for geometry
        sym = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['T'] == 200)
        ]['commit_rate'].mean()

        clust = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'clustered') &
            (df_all['phase_offset'] == 0) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['T'] == 200)
        ]['commit_rate'].mean()

        if not pd.isna(sym) and not pd.isna(clust):
            diff = abs(sym - clust)
            pct_diff = 100 * diff / max(sym, clust)
            sig = "***" if pct_diff >= 10 else ""
            print(f"{d}D, Ms={ms}: sym={sym:.3f}, clust={clust:.3f}, "
                  f"diff={diff:.3f} ({pct_diff:.1f}%) {sig}")

print("\nPhase effects (phase=0 vs phase=1) at alpha=1.0:")
for d in [1, 2, 3, 4]:
    for ms in [2, 4]:  # Only multi-source makes sense for phase
        p0 = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['T'] == 200)
        ]['commit_rate'].mean()

        p1 = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 1) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['T'] == 200)
        ]['commit_rate'].mean()

        if not pd.isna(p0) and not pd.isna(p1):
            diff = abs(p0 - p1)
            pct_diff = 100 * diff / max(p0, p1)
            sig = "***" if pct_diff >= 10 else ""
            print(f"{d}D, Ms={ms}: phi=0: {p0:.3f}, phi=pi: {p1:.3f}, "
                  f"diff={diff:.3f} ({pct_diff:.1f}%) {sig}")

print("\n*** indicates >=10% difference (significant by test plan)")

# ==============================================================================
# H3: TIME-DEPENDENT THRESHOLD PERSISTS
# ==============================================================================
print("\n" + "="*80)
print("H3: TIME-DEPENDENT THRESHOLD PERSISTS ACROSS DIMENSIONS")
print("="*80)

print("\nCommit rates vs horizon T (alpha=1.0, Ms=2, symmetric, phi=0, gamma=0.001):")
for d in [1, 2, 3, 4]:
    rates = {}
    for T in [100, 200, 500]:
        rate = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == 2) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == T)
        ]['commit_rate'].mean()
        rates[T] = rate

    if all(not pd.isna(v) for v in rates.values()):
        print(f"{d}D: T=100: {rates[100]:.3f}, T=200: {rates[200]:.3f}, "
              f"T=500: {rates[500]:.3f}, ratio(500/100)={rates[500]/rates[100]:.2f}")

print("\nFirst commit time vs T:")
for d in [1, 2, 3, 4]:
    fct = {}
    for T in [100, 200, 500]:
        time = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == 2) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == T)
        ]['first_commit_time'].mean()
        fct[T] = time

    if all(not pd.isna(v) for v in fct.values()):
        print(f"{d}D: T=100: {fct[100]:.2f}, T=200: {fct[200]:.2f}, "
              f"T=500: {fct[500]:.2f}")

# ==============================================================================
# H4: THRESHOLD SCALING WITH NUM_SOURCES
# ==============================================================================
print("\n" + "="*80)
print("H4: THRESHOLD SCALES AS alpha prop to Ms^-beta(d), WITH beta(d) -> 0.5")
print("="*80)

print("\nCommit rate scaling with Ms (at alpha=1.0, T=200, symmetric, phi=0, gamma=0.001):")
for d in [1, 2, 3, 4]:
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

    if all(not pd.isna(v) for v in rates.values()):
        # Compute effective scaling exponent
        # rate prop to Ms^rho => log(rate) = rho*log(Ms) + const
        # From Ms=1 to Ms=4: rho ≈ log(rate_4/rate_1)/log(4)
        if rates[1] > 0:
            rho = np.log(rates[4] / rates[1]) / np.log(4)
            print(f"{d}D: Ms=1: {rates[1]:.3f}, Ms=2: {rates[2]:.3f}, "
                  f"Ms=4: {rates[4]:.3f}, rho≈{rho:.3f}")

print("\nFirst commit time scaling with Ms:")
for d in [1, 2, 3, 4]:
    times = {}
    for ms in [1, 2, 4]:
        time = df_all[
            (df_all['dimension'] == d) &
            (df_all['num_sources'] == ms) &
            (df_all['geometry'] == 'symmetric') &
            (df_all['phase_offset'] == 0) &
            (df_all['alpha_0'] == 1.0) &
            (df_all['gamma'] == 0.001) &
            (df_all['T'] == 200)
        ]['first_commit_time'].mean()
        times[ms] = time

    if all(not pd.isna(v) for v in times.values()):
        print(f"{d}D: Ms=1: {times[1]:.2f}, Ms=2: {times[2]:.2f}, "
              f"Ms=4: {times[4]:.2f}, ratio(1/4)={times[1]/times[4]:.2f}")

# ==============================================================================
# H5: STABILIZATION FOR d >= 4
# ==============================================================================
print("\n" + "="*80)
print("H5: FOR d >= 4, THRESHOLD AND RATE SCALING STABILIZE")
print("="*80)

print("\n3D vs 4D comparison (alpha=1.0, T=200, symmetric, phi=0, gamma=0.001):")
print("\nCommit rates:")
for ms in [1, 2, 4]:
    rate_3d = df_all[
        (df_all['dimension'] == 3) &
        (df_all['num_sources'] == ms) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    rate_4d = df_all[
        (df_all['dimension'] == 4) &
        (df_all['num_sources'] == ms) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['commit_rate'].mean()

    if not pd.isna(rate_3d) and not pd.isna(rate_4d):
        diff = abs(rate_3d - rate_4d)
        pct_diff = 100 * diff / rate_3d
        print(f"  Ms={ms}: 3D={rate_3d:.3f}, 4D={rate_4d:.3f}, "
              f"diff={diff:.3f} ({pct_diff:.1f}%)")

print("\nFirst commit times:")
for ms in [1, 2, 4]:
    fct_3d = df_all[
        (df_all['dimension'] == 3) &
        (df_all['num_sources'] == ms) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['first_commit_time'].mean()

    fct_4d = df_all[
        (df_all['dimension'] == 4) &
        (df_all['num_sources'] == ms) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['first_commit_time'].mean()

    if not pd.isna(fct_3d) and not pd.isna(fct_4d):
        diff = abs(fct_3d - fct_4d)
        pct_diff = 100 * diff / fct_3d
        print(f"  Ms={ms}: 3D={fct_3d:.2f}, 4D={fct_4d:.2f}, "
              f"diff={diff:.2f} ({pct_diff:.1f}%)")

# ==============================================================================
# DIMENSIONAL SCALING SUMMARY
# ==============================================================================
print("\n" + "="*80)
print("DIMENSIONAL SCALING SUMMARY")
print("="*80)

print("\nSalience amplification (max_salience) by dimension:")
print("(alpha=1.0, Ms=2, T=200, symmetric, phi=0, gamma=0.001)")
for d in [1, 2, 3, 4]:
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
        print(f"  {d}D: {sal:.6f}")

print("\nFinal Psi by dimension:")
for d in [1, 2, 3, 4]:
    psi = df_all[
        (df_all['dimension'] == d) &
        (df_all['num_sources'] == 2) &
        (df_all['geometry'] == 'symmetric') &
        (df_all['phase_offset'] == 0) &
        (df_all['alpha_0'] == 1.0) &
        (df_all['gamma'] == 0.001) &
        (df_all['T'] == 200)
    ]['final_psi'].mean()

    if not pd.isna(psi):
        print(f"  {d}D: {psi:.6f}")

# ==============================================================================
# COMPREHENSIVE STATISTICS TABLE
# ==============================================================================
print("\n" + "="*80)
print("COMPREHENSIVE STATISTICS TABLE")
print("="*80)

summary = []
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

# Show sample for each dimension
print("\nSample statistics (Ms=2, symmetric, phi=0, gamma=0.001, T=200):")
sample = df_summary[
    (df_summary['Ms'] == 2) &
    (df_summary['geom'] == 'symm') &
    (df_summary['phi'] == 0) &
    (df_summary['gamma'] == 0.001) &
    (df_summary['T'] == 200)
][['d', 'n', 'rate_mean', 'rate_std', 'fct_mean', 'sal_max']]
print(sample.to_string(index=False))

# Save full summary
df_summary.to_csv(r'W:\foundation\15 experiment\v6-gpu\analysis_summary.csv', index=False)
print(f"\nFull summary saved to: analysis_summary.csv ({len(df_summary)} rows)")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
