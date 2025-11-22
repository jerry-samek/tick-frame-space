"""
V6 Phase 1: 1D-2D Dimensional Sweep

Tests threshold behavior in 1D and 2D to validate framework before
extending to higher dimensions.

Validates:
- 1D should match V5 results (binary threshold at M_s=1 vs M_s≥2)
- 2D should show if geometry/phase effects emerge
"""

import numpy as np
import json
import csv
from datetime import datetime
from dimensional_wave_solver import (
    run_dimensional_simulation,
    create_symmetric_config_nd,
    create_clustered_config_nd
)

# -------------------------
# Phase 1 Parameters
# -------------------------

# Dimensions to test
dimensions = [1, 2]

# Grid sizes (dimension-specific)
GRID_SIZES = {
    1: (1000,),
    2: (128, 128),
}

# Source counts
num_sources_list = [1, 2, 4]

# Geometries
geometries = ['symmetric', 'clustered']

# Phase offsets (in units of π)
phase_offsets = [0, 1]  # 0 = in-phase, 1 = anti-phase (π offset)

# Time horizons
time_horizons = [100.0, 200.0, 500.0]

# Damping
gamma_values = [0.001, 0.005]

# Sampling
M = 1

# Alpha_0 range (coarse sweep to find threshold region)
alpha_0_values = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4]

# Fixed
alpha_1 = 0.0

# -------------------------
# Run Phase 1 Sweep
# -------------------------

print("="*80)
print("V6 PHASE 1: 1D-2D DIMENSIONAL SWEEP")
print("="*80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nDimensions: {dimensions}")
print(f"Source counts: {num_sources_list}")
print(f"Geometries: {geometries}")
print(f"Phase offsets: {phase_offsets}")
print(f"Time horizons: {time_horizons}")
print(f"Gamma values: {gamma_values}")
print(f"Alpha_0 range: {alpha_0_values}")

total_configs = len(dimensions) * len(num_sources_list) * len(geometries) * \
                len(phase_offsets) * len(time_horizons) * len(gamma_values) * \
                len(alpha_0_values)

print(f"\nTotal configurations: {total_configs}")
print("="*80)

results = []
run_count = 0

for dim in dimensions:
    print(f"\n{'='*70}")
    print(f"DIMENSION: {dim}D")
    print(f"{'='*70}")
    print(f"Grid: {GRID_SIZES[dim]}")

    for num_sources in num_sources_list:
        print(f"\n  M_s = {num_sources}")

        for geometry in geometries:
            print(f"    Geometry: {geometry}")

            for phase_offset in phase_offsets:
                phase_label = "in-phase" if phase_offset == 0 else "anti-phase"

                for T in time_horizons:
                    for gamma in gamma_values:
                        print(f"      T={T:.0f}s, gamma={gamma:.4f}, phase={phase_label}")

                        threshold_found = False
                        first_commit_alpha = None

                        for alpha_0 in alpha_0_values:
                            run_count += 1

                            # Create configuration
                            if geometry == 'symmetric':
                                config = create_symmetric_config_nd(num_sources, dim, 1.0, alpha_0)
                            else:
                                config = create_clustered_config_nd(num_sources, dim, 1.0, alpha_0)

                            # Apply phase offset (convert π units to tick offset)
                            # For simplicity: phase=1 → sources alternate ticks
                            if phase_offset == 1 and num_sources > 1:
                                config.phases = [i % 2 for i in range(num_sources)]

                            # Run simulation
                            result = run_dimensional_simulation(
                                config, dim, GRID_SIZES[dim], alpha_0, alpha_1, gamma, M, T
                            )

                            if result is None:
                                print(f"        alpha_0={alpha_0:.2f}: SKIPPED (CFL)")
                                continue

                            # Store result
                            result['parameters']['geometry'] = geometry
                            result['parameters']['phase_offset'] = phase_offset
                            results.append(result)

                            stats = result['statistics']
                            has_commits = stats['has_commits']

                            # Report
                            if has_commits and not threshold_found:
                                threshold_found = True
                                first_commit_alpha = alpha_0
                                print(f"        alpha_0={alpha_0:.2f}: *** THRESHOLD *** "
                                      f"({stats['agent_commit_count']} commits)")
                            elif has_commits:
                                print(f"        alpha_0={alpha_0:.2f}: {stats['agent_commit_count']} commits")
                            else:
                                if run_count % 10 == 0 or alpha_0 == alpha_0_values[-1]:
                                    print(f"        alpha_0={alpha_0:.2f}: No commits (Psi={stats['final_psi']:.4f})")

                        if first_commit_alpha is not None:
                            print(f"      >>> Threshold: alpha_0 >= {first_commit_alpha:.2f}")

# -------------------------
# Save results
# -------------------------

print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

json_file = "v6_phase1_1d2d_results.json"
with open(json_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Full results saved to: {json_file}")

csv_file = "v6_phase1_1d2d_results.csv"
with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'dimension', 'num_sources', 'geometry', 'phase_offset',
        'alpha_0', 'gamma', 'M', 'T',
        'has_commits', 'agent_commit_count', 'commit_rate',
        'first_commit_time', 'final_psi', 'max_salience'
    ])
    writer.writeheader()
    for r in results:
        p = r['parameters']
        s = r['statistics']
        writer.writerow({
            'dimension': p['dimension'],
            'num_sources': p['num_sources'],
            'geometry': p['geometry'],
            'phase_offset': p['phase_offset'],
            'alpha_0': p['alpha_0'],
            'gamma': p['gamma'],
            'M': p['M'],
            'T': p['T'],
            'has_commits': s['has_commits'],
            'agent_commit_count': s['agent_commit_count'],
            'commit_rate': s['commit_rate'],
            'first_commit_time': s['first_commit_time'] if s['first_commit_time'] else '',
            'final_psi': s['final_psi'],
            'max_salience': s['max_salience']
        })
print(f"CSV data saved to: {csv_file}")

# -------------------------
# Analysis: Compare 1D vs 2D
# -------------------------

print("\n" + "="*80)
print("DIMENSIONAL COMPARISON")
print("="*80)

print("\nThreshold comparison (T=100s, symmetric, in-phase, gamma=0.001):")
print(f"{'Dim':<5} {'M_s':<5} {'alpha_0_threshold':<20} {'Notes'}")
print("-"*60)

for dim in dimensions:
    for num_sources in num_sources_list:
        matching = [r for r in results
                   if r['parameters']['dimension'] == dim
                   and r['parameters']['num_sources'] == num_sources
                   and r['parameters']['geometry'] == 'symmetric'
                   and r['parameters']['phase_offset'] == 0
                   and r['parameters']['T'] == 100.0
                   and r['parameters']['gamma'] == 0.001
                   and r['statistics']['has_commits']]

        if matching:
            threshold = min(r['parameters']['alpha_0'] for r in matching)

            # Compare with V5 1D results
            if dim == 1 and num_sources == 1:
                note = "(should match V5: ~2.00)"
            elif dim == 1 and num_sources >= 2:
                note = "(should match V5: ~1.00)"
            else:
                note = ""

            print(f"{dim}D    {num_sources:<5} {threshold:<20.2f} {note}")

# Geometry effect in 2D
print("\n\nGeometry effect in 2D (M_s=2, T=100s, in-phase, gamma=0.001):")
print(f"{'Geometry':<15} {'alpha_0_threshold':<20} {'Difference'}")
print("-"*55)

thresholds_2d = {}
for geometry in geometries:
    matching = [r for r in results
               if r['parameters']['dimension'] == 2
               and r['parameters']['num_sources'] == 2
               and r['parameters']['geometry'] == geometry
               and r['parameters']['phase_offset'] == 0
               and r['parameters']['T'] == 100.0
               and r['parameters']['gamma'] == 0.001
               and r['statistics']['has_commits']]

    if matching:
        threshold = min(r['parameters']['alpha_0'] for r in matching)
        thresholds_2d[geometry] = threshold
        print(f"{geometry:<15} {threshold:<20.2f}")

if len(thresholds_2d) == 2:
    diff = thresholds_2d['clustered'] - thresholds_2d['symmetric']
    print(f"\nGeometry delta: {diff:+.2f} ({abs(diff)/thresholds_2d['symmetric']*100:.1f}%)")
    if abs(diff) >= 0.02:
        print("  >>> GEOMETRY EFFECT DETECTED in 2D!")
    else:
        print("  >>> No significant geometry effect")

# Phase effect in 2D
print("\n\nPhase effect in 2D (M_s=2, T=100s, symmetric, gamma=0.001):")
print(f"{'Phase':<15} {'alpha_0_threshold':<20} {'Difference'}")
print("-"*55)

thresholds_phase = {}
for phase_offset in phase_offsets:
    phase_label = "in-phase" if phase_offset == 0 else "anti-phase"
    matching = [r for r in results
               if r['parameters']['dimension'] == 2
               and r['parameters']['num_sources'] == 2
               and r['parameters']['geometry'] == 'symmetric'
               and r['parameters']['phase_offset'] == phase_offset
               and r['parameters']['T'] == 100.0
               and r['parameters']['gamma'] == 0.001
               and r['statistics']['has_commits']]

    if matching:
        threshold = min(r['parameters']['alpha_0'] for r in matching)
        thresholds_phase[phase_offset] = threshold
        print(f"{phase_label:<15} {threshold:<20.2f}")

if len(thresholds_phase) == 2:
    diff = thresholds_phase[1] - thresholds_phase[0]
    print(f"\nPhase delta: {diff:+.2f} ({abs(diff)/thresholds_phase[0]*100:.1f}%)")
    if abs(diff) >= 0.02:
        print("  >>> PHASE EFFECT DETECTED in 2D!")
    else:
        print("  >>> No significant phase effect")

print(f"\n\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n" + "="*80)
print("PHASE 1 COMPLETE")
print("="*80)
print("\nNext steps:")
print("  - Review results to validate 1D matches V5")
print("  - Check if 2D shows geometry/phase effects")
print("  - If validated, proceed to Phase 2 (3D-5D)")
