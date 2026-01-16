#!/usr/bin/env python3
"""
Validates dimensional equivalence hypothesis:
- Does (2D+t) behave like 3D?
- Does (3D+t) behave like 4D?
- Does (4D+t) behave like 5D?

Compares metrics from variant A (time as physics) and variant B (time as storage)
against baseline dimensional results from Experiment #15.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

def load_results(results_dir):
    """Load all experimental results."""
    results_dir = Path(results_dir)

    baseline = pd.read_csv(results_dir / "baseline_validation.csv")

    # Variant A: time as physics dimension
    variant_a_2d_t = pd.read_csv(results_dir / "variant_a_2d_plus_time.csv")
    variant_a_3d_t = pd.read_csv(results_dir / "variant_a_3d_plus_time.csv")
    variant_a_4d_t = pd.read_csv(results_dir / "variant_a_4d_plus_time.csv")

    # Variant B: time as storage/rendering
    variant_b_2d = pd.read_csv(results_dir / "variant_b_2d.csv")
    variant_b_3d = pd.read_csv(results_dir / "variant_b_3d.csv")
    variant_b_4d = pd.read_csv(results_dir / "variant_b_4d.csv")

    return {
        'baseline': baseline,
        'variant_a': {
            '2d_t': variant_a_2d_t,
            '3d_t': variant_a_3d_t,
            '4d_t': variant_a_4d_t
        },
        'variant_b': {
            '2d': variant_b_2d,
            '3d': variant_b_3d,
            '4d': variant_b_4d
        }
    }

def compute_cv(df):
    """Compute coefficient of variation for key metrics."""
    metrics = {}

    # Commit rate CV
    if 'commit_rate' in df.columns and len(df) > 1:
        metrics['cv_commit_rate'] = df['commit_rate'].std() / df['commit_rate'].mean() if df['commit_rate'].mean() > 0 else np.nan

    # Max salience CV
    if 'max_salience' in df.columns and len(df) > 1:
        metrics['cv_max_salience'] = df['max_salience'].std() / df['max_salience'].mean() if df['max_salience'].mean() > 0 else np.nan

    # Final psi CV
    if 'final_psi' in df.columns and len(df) > 1:
        metrics['cv_final_psi'] = df['final_psi'].std() / df['final_psi'].mean() if df['final_psi'].mean() > 0 else np.nan

    return metrics

def compute_source_independence(df):
    """Compute source scaling exponent (ρ)."""
    if 'num_sources' not in df.columns or 'max_salience' not in df.columns:
        return {'rho': np.nan}

    # Group by source count and compute mean salience
    source_groups = df.groupby('num_sources')['max_salience'].mean()

    if len(source_groups) < 2:
        return {'rho': np.nan}

    # Fit log-log relationship: log(salience) = ρ * log(num_sources) + c
    sources = np.array(source_groups.index)
    saliences = np.array(source_groups.values)

    # Filter out zeros
    mask = (sources > 0) & (saliences > 0)
    if mask.sum() < 2:
        return {'rho': np.nan}

    log_sources = np.log(sources[mask])
    log_saliences = np.log(saliences[mask])

    # Linear regression
    rho = np.polyfit(log_sources, log_saliences, 1)[0]

    return {'rho': rho}

def aggregate_metrics(df, dimension_label):
    """Aggregate all metrics for a dataset."""
    metrics = {
        'dimension': dimension_label,
        'n_configs': len(df),
        'mean_commit_rate': df['commit_rate'].mean() if 'commit_rate' in df.columns else np.nan,
        'mean_max_salience': df['max_salience'].mean() if 'max_salience' in df.columns else np.nan,
        'mean_final_psi': df['final_psi'].mean() if 'final_psi' in df.columns else np.nan,
        'std_commit_rate': df['commit_rate'].std() if 'commit_rate' in df.columns else np.nan,
        'std_max_salience': df['max_salience'].std() if 'max_salience' in df.columns else np.nan,
        'std_final_psi': df['final_psi'].std() if 'final_psi' in df.columns else np.nan,
    }

    # Add CV metrics
    cv_metrics = compute_cv(df)
    metrics.update(cv_metrics)

    # Add source independence
    rho_metrics = compute_source_independence(df)
    metrics.update(rho_metrics)

    return metrics

def compare_dimensions(baseline_metrics, variant_metrics, baseline_dim, variant_label, tolerance=0.1):
    """Compare metrics between baseline and variant to test equivalence."""

    comparison = {
        'test': f"{variant_label} vs {baseline_dim}D",
        'baseline_dim': baseline_dim,
        'variant_label': variant_label,
        'passes': [],
        'fails': [],
        'warnings': []
    }

    # Define key metrics to compare
    key_metrics = ['mean_commit_rate', 'mean_max_salience', 'cv_commit_rate', 'cv_max_salience', 'rho']

    for metric in key_metrics:
        baseline_val = baseline_metrics.get(metric, np.nan)
        variant_val = variant_metrics.get(metric, np.nan)

        if np.isnan(baseline_val) or np.isnan(variant_val):
            comparison['warnings'].append(f"{metric}: insufficient data")
            continue

        # Compute relative difference
        if baseline_val != 0:
            rel_diff = abs(variant_val - baseline_val) / abs(baseline_val)
        else:
            rel_diff = abs(variant_val - baseline_val)

        pct_diff = rel_diff * 100

        if rel_diff <= tolerance:
            comparison['passes'].append(f"{metric}: {pct_diff:.1f}% (PASS)")
        else:
            comparison['fails'].append(f"{metric}: {pct_diff:.1f}% (FAIL)")

    # Overall assessment
    total_tests = len(comparison['passes']) + len(comparison['fails'])
    if total_tests > 0:
        pass_rate = len(comparison['passes']) / total_tests
        comparison['pass_rate'] = pass_rate
        comparison['verdict'] = 'PASS' if pass_rate >= 0.8 else 'FAIL'
    else:
        comparison['pass_rate'] = 0.0
        comparison['verdict'] = 'INCONCLUSIVE'

    return comparison

def main():
    results_dir = Path(__file__).parent.parent / "results"

    print("=" * 80)
    print("EXPERIMENT 50: DIMENSIONAL EQUIVALENCE VALIDATION")
    print("=" * 80)
    print()

    # Load data
    print("Loading experimental results...")
    data = load_results(results_dir)
    print(f"  Baseline: {len(data['baseline'])} configs")
    print(f"  Variant A (2D+t): {len(data['variant_a']['2d_t'])} configs")
    print(f"  Variant A (3D+t): {len(data['variant_a']['3d_t'])} configs")
    print(f"  Variant A (4D+t): {len(data['variant_a']['4d_t'])} configs")
    print(f"  Variant B (2D): {len(data['variant_b']['2d'])} configs")
    print(f"  Variant B (3D): {len(data['variant_b']['3d'])} configs")
    print(f"  Variant B (4D): {len(data['variant_b']['4d'])} configs")
    print()

    # Extract baseline by dimension
    baseline_3d = data['baseline'][data['baseline']['dimension'] == 3]
    baseline_4d = data['baseline'][data['baseline']['dimension'] == 4]
    baseline_5d = data['baseline'][data['baseline']['dimension'] == 5]

    # Compute metrics for all datasets
    print("Computing aggregated metrics...")
    metrics = {
        'baseline_3d': aggregate_metrics(baseline_3d, '3D'),
        'baseline_4d': aggregate_metrics(baseline_4d, '4D'),
        'baseline_5d': aggregate_metrics(baseline_5d, '5D'),
        'variant_a_2d_t': aggregate_metrics(data['variant_a']['2d_t'], '2D+t (physics)'),
        'variant_a_3d_t': aggregate_metrics(data['variant_a']['3d_t'], '3D+t (physics)'),
        'variant_a_4d_t': aggregate_metrics(data['variant_a']['4d_t'], '4D+t (physics)'),
        'variant_b_2d': aggregate_metrics(data['variant_b']['2d'], '2D+t (rendering)'),
        'variant_b_3d': aggregate_metrics(data['variant_b']['3d'], '3D+t (rendering)'),
        'variant_b_4d': aggregate_metrics(data['variant_b']['4d'], '4D+t (rendering)'),
    }
    print()

    # Perform comparisons
    print("=" * 80)
    print("DIMENSIONAL EQUIVALENCE TESTS")
    print("=" * 80)
    print()

    comparisons = []

    # Test 1: (2D+t physics) vs 3D
    print("TEST 1: (2D+t physics) vs 3D")
    print("-" * 80)
    comp1 = compare_dimensions(metrics['baseline_3d'], metrics['variant_a_2d_t'], 3, '2D+t (physics)')
    comparisons.append(comp1)
    print(f"  Verdict: {comp1['verdict']} (pass rate: {comp1['pass_rate']*100:.0f}%)")
    print(f"  Passes: {len(comp1['passes'])}, Fails: {len(comp1['fails'])}, Warnings: {len(comp1['warnings'])}")
    for p in comp1['passes']:
        print(f"    + {p}")
    for f in comp1['fails']:
        print(f"    - {f}")
    for w in comp1['warnings']:
        print(f"    ! {w}")
    print()

    # Test 2: (3D+t physics) vs 4D
    print("TEST 2: (3D+t physics) vs 4D")
    print("-" * 80)
    comp2 = compare_dimensions(metrics['baseline_4d'], metrics['variant_a_3d_t'], 4, '3D+t (physics)')
    comparisons.append(comp2)
    print(f"  Verdict: {comp2['verdict']} (pass rate: {comp2['pass_rate']*100:.0f}%)")
    print(f"  Passes: {len(comp2['passes'])}, Fails: {len(comp2['fails'])}, Warnings: {len(comp2['warnings'])}")
    for p in comp2['passes']:
        print(f"    + {p}")
    for f in comp2['fails']:
        print(f"    - {f}")
    for w in comp2['warnings']:
        print(f"    ! {w}")
    print()

    # Test 3: (4D+t physics) vs 5D
    print("TEST 3: (4D+t physics) vs 5D")
    print("-" * 80)
    comp3 = compare_dimensions(metrics['baseline_5d'], metrics['variant_a_4d_t'], 5, '4D+t (physics)')
    comparisons.append(comp3)
    print(f"  Verdict: {comp3['verdict']} (pass rate: {comp3['pass_rate']*100:.0f}%)")
    print(f"  Passes: {len(comp3['passes'])}, Fails: {len(comp3['fails'])}, Warnings: {len(comp3['warnings'])}")
    for p in comp3['passes']:
        print(f"    + {p}")
    for f in comp3['fails']:
        print(f"    - {f}")
    for w in comp3['warnings']:
        print(f"    ! {w}")
    print()

    # Test 4: (2D+t rendering) vs 3D
    print("TEST 4: (2D+t rendering) vs 3D")
    print("-" * 80)
    comp4 = compare_dimensions(metrics['baseline_3d'], metrics['variant_b_2d'], 3, '2D+t (rendering)')
    comparisons.append(comp4)
    print(f"  Verdict: {comp4['verdict']} (pass rate: {comp4['pass_rate']*100:.0f}%)")
    print(f"  Passes: {len(comp4['passes'])}, Fails: {len(comp4['fails'])}, Warnings: {len(comp4['warnings'])}")
    for p in comp4['passes']:
        print(f"    + {p}")
    for f in comp4['fails']:
        print(f"    - {f}")
    for w in comp4['warnings']:
        print(f"    ! {w}")
    print()

    # Test 5: (3D+t rendering) vs 4D
    print("TEST 5: (3D+t rendering) vs 4D")
    print("-" * 80)
    comp5 = compare_dimensions(metrics['baseline_4d'], metrics['variant_b_3d'], 4, '3D+t (rendering)')
    comparisons.append(comp5)
    print(f"  Verdict: {comp5['verdict']} (pass rate: {comp5['pass_rate']*100:.0f}%)")
    print(f"  Passes: {len(comp5['passes'])}, Fails: {len(comp5['fails'])}, Warnings: {len(comp5['warnings'])}")
    for p in comp5['passes']:
        print(f"    + {p}")
    for f in comp5['fails']:
        print(f"    - {f}")
    for w in comp5['warnings']:
        print(f"    ! {w}")
    print()

    # Test 6: (4D+t rendering) vs 5D
    print("TEST 6: (4D+t rendering) vs 5D")
    print("-" * 80)
    comp6 = compare_dimensions(metrics['baseline_5d'], metrics['variant_b_4d'], 5, '4D+t (rendering)')
    comparisons.append(comp6)
    print(f"  Verdict: {comp6['verdict']} (pass rate: {comp6['pass_rate']*100:.0f}%)")
    print(f"  Passes: {len(comp6['passes'])}, Fails: {len(comp6['fails'])}, Warnings: {len(comp6['warnings'])}")
    for p in comp6['passes']:
        print(f"    + {p}")
    for f in comp6['fails']:
        print(f"    - {f}")
    for w in comp6['warnings']:
        print(f"    ! {w}")
    print()

    # Overall summary
    print("=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print()

    passed = sum(1 for c in comparisons if c['verdict'] == 'PASS')
    failed = sum(1 for c in comparisons if c['verdict'] == 'FAIL')
    inconclusive = sum(1 for c in comparisons if c['verdict'] == 'INCONCLUSIVE')

    print(f"Tests passed: {passed}/{len(comparisons)}")
    print(f"Tests failed: {failed}/{len(comparisons)}")
    print(f"Inconclusive: {inconclusive}/{len(comparisons)}")
    print()

    # Determine final conclusion
    if passed >= 5:
        conclusion = "DIMENSIONAL EQUIVALENCE CONFIRMED"
        explanation = "Time behaves as a physical dimension in most or all tested cases."
    elif failed >= 4:
        conclusion = "GENERATOR DISTINCTION CONFIRMED"
        explanation = "Time exhibits qualitatively different behavior from spatial dimensions."
    else:
        conclusion = "MIXED RESULTS"
        explanation = "Some dimensional equivalences hold while others do not. Further investigation needed."

    print(f"CONCLUSION: {conclusion}")
    print(f"  {explanation}")
    print()

    # Detailed metric table
    print("=" * 80)
    print("DETAILED METRICS TABLE")
    print("=" * 80)
    print()
    print(f"{'Dimension':<25} {'Commit Rate':<15} {'Max Salience':<15} {'CV(Commit)':<12} {'CV(Salience)':<12} {'rho':<8}")
    print("-" * 80)

    for key in ['baseline_3d', 'variant_a_2d_t', 'variant_b_2d',
                'baseline_4d', 'variant_a_3d_t', 'variant_b_3d',
                'baseline_5d', 'variant_a_4d_t', 'variant_b_4d']:
        m = metrics[key]
        print(f"{m['dimension']:<25} "
              f"{m['mean_commit_rate']:>14.2f} "
              f"{m['mean_max_salience']:>14.4f} "
              f"{m.get('cv_commit_rate', np.nan):>11.4f} "
              f"{m.get('cv_max_salience', np.nan):>11.4f} "
              f"{m.get('rho', np.nan):>7.3f}")

        # Add separator after each dimension group
        if key in ['variant_b_2d', 'variant_b_3d']:
            print()

    print()

    # Save results
    output_file = results_dir / "dimensional_equivalence_validation.json"
    output_data = {
        'metrics': metrics,
        'comparisons': comparisons,
        'summary': {
            'passed': passed,
            'failed': failed,
            'inconclusive': inconclusive,
            'conclusion': conclusion,
            'explanation': explanation
        }
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"Detailed results saved to: {output_file}")
    print()

if __name__ == "__main__":
    main()
