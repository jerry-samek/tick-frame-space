"""
Phase D: Phase and Interference Effects

Tests how emission timing (phase) between sources affects interference patterns.

Research questions:
1. Do in-phase sources create constructive interference (lower threshold)?
2. Do anti-phase sources create destructive interference (higher threshold)?
3. Can we quantify interference factor kappa?
"""

import numpy as np
import json
import csv
from datetime import datetime
from multi_source_simulation import (
    run_multi_source_simulation,
    create_symmetric_config,
    create_phased_config
)

# -----------------------------
# Phase D parameters
# -----------------------------

# Two-source configuration
num_sources = 2

# Phase offsets to test (in ticks)
# 0 = in-phase (simultaneous)
# 1 = alternating (anti-phase for M=1)
# 2 = every other tick staggered
phase_offsets = [0, 1, 2]

# Time horizon
T = 200.0  # Use medium horizon from V4

# Alpha_0 range around expected two-source threshold
alpha_0_values = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2]

# Fixed parameters
alpha_1 = 0.0
gamma = 0.001
M = 1

# -----------------------------
# Run Phase D sweep
# -----------------------------

print("=" * 80)
print("PHASE D: INTERFERENCE AND PHASE ANALYSIS")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nResearch questions:")
print(f"  1. How does emission phase affect threshold?")
print(f"  2. Constructive vs destructive interference")
print(f"  3. Quantify interference factor kappa")
print(f"\nTest parameters:")
print(f"  Sources: {num_sources} (symmetric)")
print(f"  Phase offsets: {phase_offsets} ticks")
print(f"  Alpha_0 range: {alpha_0_values}")
print(f"  Time horizon: T={T:.0f}s")
print(f"  Fixed: gamma={gamma:.4f}, M={M}")
print(f"\nTotal runs: {len(phase_offsets) * len(alpha_0_values)}")
print("=" * 80)

results = []
L = 1.0

for phase_offset in phase_offsets:
    print(f"\n{'='*70}")
    print(f"PHASE OFFSET: {phase_offset} ticks")
    if phase_offset == 0:
        print("  (In-phase: simultaneous emissions)")
    elif phase_offset == 1:
        print("  (Anti-phase: alternating emissions)")
    else:
        print(f"  (Staggered: {phase_offset}-tick delay)")
    print(f"{'='*70}")

    threshold_found = False
    first_commit_alpha = None

    for alpha_0 in alpha_0_values:
        # Create phased configuration
        config = create_phased_config(num_sources, L, alpha_0, phase_offset)

        # Run simulation
        result = run_multi_source_simulation(
            config, alpha_0, alpha_1, gamma, M, T
        )

        if result is None:
            print(f"  alpha_0={alpha_0:.2f}: SKIPPED (CFL)")
            continue

        # Store result
        result['parameters']['phase_offset'] = phase_offset
        result['parameters']['geometry'] = 'symmetric_phased'
        results.append(result)

        stats = result['statistics']
        has_commits = stats['has_commits']

        # Report
        if has_commits and not threshold_found:
            threshold_found = True
            first_commit_alpha = alpha_0
            print(f"  alpha_0={alpha_0:.2f}: *** THRESHOLD CROSSED ***")
            print(f"    Commits: {stats['agent_commit_count']}")
            print(f"    First at: t={stats['first_commit_time']:.1f}s")
            print(f"    Rate: {stats['commit_rate']:.4f}")
            print(f"    Source emissions: {stats['source_emission_counts']}")
        elif has_commits:
            print(f"  alpha_0={alpha_0:.2f}: {stats['agent_commit_count']} commits "
                  f"(rate={stats['commit_rate']:.4f})")
        else:
            print(f"  alpha_0={alpha_0:.2f}: No commits (Psi={stats['final_psi']:.4f})")

    if first_commit_alpha is not None:
        print(f"\n  >>> Threshold for phase={phase_offset}: alpha_0 >= {first_commit_alpha:.2f}")

# -----------------------------
# Save results
# -----------------------------

print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

json_file = "phase_d_interference_results.json"
with open(json_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Full results saved to: {json_file}")

csv_file = "phase_d_interference_results.csv"
with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'phase_offset', 'alpha_0', 'T', 'gamma', 'M',
        'has_commits', 'agent_commit_count', 'commit_rate',
        'first_commit_time', 'final_psi', 'max_salience'
    ])
    writer.writeheader()
    for r in results:
        p = r['parameters']
        s = r['statistics']
        writer.writerow({
            'phase_offset': p['phase_offset'],
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
# Analysis: Interference effects
# -----------------------------

print("\n" + "=" * 80)
print("INTERFERENCE ANALYSIS")
print("=" * 80)

print("\nThreshold vs phase offset:")
print(f"{'Phase':<15} {'alpha_0_threshold':<20} {'Interpretation'}")
print("-" * 70)

thresholds_by_phase = {}

for phase_offset in phase_offsets:
    matching = [r for r in results
               if r['parameters']['phase_offset'] == phase_offset
               and r['statistics']['has_commits']]

    if matching:
        threshold = min(r['parameters']['alpha_0'] for r in matching)
        thresholds_by_phase[phase_offset] = threshold

        if phase_offset == 0:
            interpretation = "In-phase (constructive)"
        elif phase_offset == 1:
            interpretation = "Anti-phase (destructive)"
        else:
            interpretation = f"Staggered ({phase_offset} ticks)"

        print(f"{phase_offset:<15} {threshold:<20.2f} {interpretation}")

# Calculate interference factors
if 0 in thresholds_by_phase:
    baseline = thresholds_by_phase[0]
    print(f"\n\nInterference factors (relative to in-phase baseline={baseline:.2f}):")
    print(f"{'Phase':<15} {'Threshold':<15} {'Factor kappa':<15} {'Effect'}")
    print("-" * 70)

    for phase_offset in sorted(thresholds_by_phase.keys()):
        threshold = thresholds_by_phase[phase_offset]
        kappa = threshold / baseline

        if kappa < 0.95:
            effect = "Strong constructive"
        elif kappa < 1.05:
            effect = "Neutral"
        elif kappa < 1.15:
            effect = "Weak destructive"
        else:
            effect = "Strong destructive"

        print(f"{phase_offset:<15} {threshold:<15.2f} {kappa:<15.3f} {effect}")

# Commit count comparison
print("\n\nCommit counts at alpha_0=2.0:")
print(f"{'Phase':<15} {'Commits':<15} {'Rate':<15} {'Relative to in-phase'}")
print("-" * 70)

baseline_commits = None

for phase_offset in phase_offsets:
    matching = [r for r in results
               if r['parameters']['phase_offset'] == phase_offset
               and abs(r['parameters']['alpha_0'] - 2.0) < 0.01]

    if matching:
        r = matching[0]
        commits = r['statistics']['agent_commit_count']
        rate = r['statistics']['commit_rate']

        if baseline_commits is None:
            baseline_commits = commits
            relative = 1.0
        else:
            relative = commits / baseline_commits if baseline_commits > 0 else 0.0

        print(f"{phase_offset:<15} {commits:<15} {rate:<15.4f} {relative:.3f}x")

print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
