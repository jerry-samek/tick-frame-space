"""
Phase A: Geometry and Source Count Experiment

Tests how the number and arrangement of sources affects the threshold.

Research questions:
1. Does threshold decrease with more sources (alpha_0_threshold ~ M_s^(-1/2))?
2. Does symmetric vs asymmetric layout matter?
3. How does this interact with time horizon T?
"""

import numpy as np
import json
import csv
from datetime import datetime
from multi_source_simulation import (
    run_multi_source_simulation,
    create_symmetric_config,
    create_asymmetric_config
)

# -----------------------------
# Phase A parameters
# -----------------------------

# Source counts to test
num_sources_list = [1, 2, 4, 8]

# Time horizons (from V4)
time_horizons = [100.0, 200.0, 500.0]

# Alpha_0 range to test (based on V4 findings)
# For single source: threshold at 1.88-1.90 for T=100s
# Hypothesis: Multi-source should lower threshold
alpha_0_values = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

# Fixed parameters (optimal from V3/V4)
alpha_1 = 0.0
gamma = 0.001
M = 1

# Geometries to test
geometries = ['symmetric', 'asymmetric']

# -----------------------------
# Run Phase A sweep
# -----------------------------

print("=" * 80)
print("PHASE A: GEOMETRY AND SOURCE COUNT ANALYSIS")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nResearch questions:")
print(f"  1. How does threshold scale with source count?")
print(f"  2. Does geometry (symmetric vs asymmetric) affect threshold?")
print(f"  3. How does this interact with time horizon T?")
print(f"\nTest parameters:")
print(f"  Source counts: {num_sources_list}")
print(f"  Geometries: {geometries}")
print(f"  Alpha_0 range: {alpha_0_values}")
print(f"  Time horizons: {time_horizons}s")
print(f"  Fixed: gamma={gamma:.4f}, M={M}")
print(f"\nTotal runs: {len(num_sources_list) * len(geometries) * len(alpha_0_values) * len(time_horizons)}")
print("=" * 80)

results = []
L = 1.0

for num_sources in num_sources_list:
    print(f"\n{'='*70}")
    print(f"SOURCE COUNT: M_s = {num_sources}")
    print(f"{'='*70}")

    for geometry in geometries:
        print(f"\n  Geometry: {geometry}")
        print(f"  {'-'*60}")

        for T in time_horizons:
            print(f"\n    T = {T:.0f}s")

            threshold_found = False
            first_commit_alpha = None

            for alpha_0 in alpha_0_values:
                # Create configuration
                if geometry == 'symmetric':
                    config = create_symmetric_config(num_sources, L, alpha_0)
                else:
                    config = create_asymmetric_config(num_sources, L, alpha_0)

                # Run simulation
                result = run_multi_source_simulation(
                    config, alpha_0, alpha_1, gamma, M, T
                )

                if result is None:
                    print(f"      alpha_0={alpha_0:.2f}: SKIPPED (CFL)")
                    continue

                # Store result
                result['parameters']['geometry'] = geometry
                results.append(result)

                stats = result['statistics']
                has_commits = stats['has_commits']

                # Report
                if has_commits and not threshold_found:
                    threshold_found = True
                    first_commit_alpha = alpha_0
                    print(f"      alpha_0={alpha_0:.2f}: *** THRESHOLD CROSSED ***")
                    print(f"        Commits: {stats['agent_commit_count']}")
                    print(f"        First at: t={stats['first_commit_time']:.1f}s")
                    print(f"        Rate: {stats['commit_rate']:.4f}")
                elif has_commits:
                    print(f"      alpha_0={alpha_0:.2f}: {stats['agent_commit_count']} commits (rate={stats['commit_rate']:.4f})")
                else:
                    print(f"      alpha_0={alpha_0:.2f}: No commits (Psi={stats['final_psi']:.4f})")

            # Summary for this configuration
            if first_commit_alpha is not None:
                print(f"\n    >>> Threshold for M_s={num_sources}, {geometry}, T={T:.0f}s: alpha_0 >= {first_commit_alpha:.2f}")

# -----------------------------
# Save results
# -----------------------------

print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

json_file = "phase_a_geometry_results.json"
with open(json_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Full results saved to: {json_file}")

csv_file = "phase_a_geometry_results.csv"
with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'num_sources', 'geometry', 'alpha_0', 'T', 'gamma', 'M',
        'has_commits', 'agent_commit_count', 'commit_rate',
        'first_commit_time', 'final_psi', 'max_salience'
    ])
    writer.writeheader()
    for r in results:
        p = r['parameters']
        s = r['statistics']
        writer.writerow({
            'num_sources': p['num_sources'],
            'geometry': p['geometry'],
            'alpha_0': p['alpha_0'],
            'T': p['T'],
            'gamma': p['gamma'],
            'M': p['M'],
            'has_commits': s['has_commits'],
            'agent_commit_count': s['agent_commit_count'],
            'commit_rate': s['commit_rate'],
            'first_commit_time': s['first_commit_time'] if s['first_commit_time'] else '',
            'final_psi': s['final_psi'],
            'max_salience': s['max_salience']
        })
print(f"CSV data saved to: {csv_file}")

# -----------------------------
# Analysis: Threshold scaling
# -----------------------------

print("\n" + "=" * 80)
print("THRESHOLD SCALING ANALYSIS")
print("=" * 80)

print("\nThreshold vs source count (T=100s, symmetric):")
print(f"{'M_s':<10} {'alpha_0_threshold':<20} {'Scaling factor'}")
print("-" * 50)

baseline_threshold = None

for num_sources in num_sources_list:
    # Find threshold for this source count
    matching = [r for r in results
               if r['parameters']['num_sources'] == num_sources
               and r['parameters']['geometry'] == 'symmetric'
               and r['parameters']['T'] == 100.0
               and r['statistics']['has_commits']]

    if matching:
        # Find minimum alpha_0 with commits
        threshold = min(r['parameters']['alpha_0'] for r in matching)

        if baseline_threshold is None:
            baseline_threshold = threshold
            scaling_factor = 1.0
        else:
            scaling_factor = threshold / baseline_threshold

        print(f"{num_sources:<10} {threshold:<20.2f} {scaling_factor:.3f}")

        # Check theoretical prediction: threshold ~ M_s^(-1/2)
        theoretical_factor = 1.0 / np.sqrt(num_sources)
        print(f"           Theoretical M_s^(-1/2): {theoretical_factor:.3f}")

print("\n" + "=" * 80)
print("GEOMETRY COMPARISON")
print("=" * 80)

print("\nThreshold difference: symmetric vs asymmetric (T=100s)")
print(f"{'M_s':<10} {'Symmetric':<15} {'Asymmetric':<15} {'Difference'}")
print("-" * 55)

for num_sources in num_sources_list:
    thresholds = {}

    for geometry in geometries:
        matching = [r for r in results
                   if r['parameters']['num_sources'] == num_sources
                   and r['parameters']['geometry'] == geometry
                   and r['parameters']['T'] == 100.0
                   and r['statistics']['has_commits']]

        if matching:
            thresholds[geometry] = min(r['parameters']['alpha_0'] for r in matching)

    if 'symmetric' in thresholds and 'asymmetric' in thresholds:
        diff = thresholds['asymmetric'] - thresholds['symmetric']
        print(f"{num_sources:<10} {thresholds['symmetric']:<15.2f} "
              f"{thresholds['asymmetric']:<15.2f} {diff:+.2f}")

print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
