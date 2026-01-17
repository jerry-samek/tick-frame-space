#!/usr/bin/env python3
"""
Analysis Module for Experiment 51i (V9)

Post-processing tools for time dilation decomposition and validation.
"""

import numpy as np
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from dataclasses import dataclass

from entity_motion import MovingEntity, lorentz_gamma


@dataclass
class TimeDilationDecomposition:
    """Results of time dilation decomposition analysis."""
    entity_id: str

    # Measured
    gamma_eff_measured: float
    proper_time: float
    coordinate_time: int

    # Predicted components
    gamma_SR_avg: float
    gamma_grav_avg: float
    gamma_total_predicted: float

    # Validation
    relative_error: float
    passes_threshold: bool

    # Trajectory stats
    avg_distance: float
    avg_speed: float
    trajectory_length: int


def analyze_entity_time_dilation(entity: MovingEntity, planet_center: Tuple[float, float]) -> TimeDilationDecomposition:
    """
    Decompose measured time dilation into gravitational and SR components.

    Args:
        entity: MovingEntity with history
        planet_center: (cx, cy) center of gravitational source

    Returns:
        TimeDilationDecomposition with all statistics
    """
    # Measured effective gamma
    if entity.proper_time < 1e-10:
        gamma_eff_measured = 1.0
    else:
        gamma_eff_measured = entity.coordinate_time / entity.proper_time

    # Average special relativistic gamma
    if len(entity.gamma_SR_history) > 0:
        gamma_SR_avg = float(np.mean(entity.gamma_SR_history))
    else:
        gamma_SR_avg = entity.gamma_SR

    # Average gravitational gamma
    if len(entity.gamma_grav_history) > 0:
        gamma_grav_avg = float(np.mean(entity.gamma_grav_history))
    else:
        gamma_grav_avg = 1.0

    # Predicted combined gamma
    gamma_total_predicted = gamma_SR_avg * gamma_grav_avg

    # Validation: relative error
    if gamma_eff_measured > 1e-10:
        relative_error = abs(gamma_total_predicted - gamma_eff_measured) / gamma_eff_measured
    else:
        relative_error = float('inf')

    passes_threshold = relative_error < 0.15  # 15% tolerance

    # Trajectory statistics
    if len(entity.position_history) > 0:
        positions = np.array(entity.position_history)
        center = np.array(planet_center)
        distances = np.linalg.norm(positions - center, axis=1)
        avg_distance = float(np.mean(distances))
        trajectory_length = len(entity.position_history)
    else:
        avg_distance = float(np.linalg.norm(entity.position - np.array(planet_center)))
        trajectory_length = 0

    avg_speed = entity.speed

    return TimeDilationDecomposition(
        entity_id=entity.entity_id,
        gamma_eff_measured=gamma_eff_measured,
        proper_time=entity.proper_time,
        coordinate_time=entity.coordinate_time,
        gamma_SR_avg=gamma_SR_avg,
        gamma_grav_avg=gamma_grav_avg,
        gamma_total_predicted=gamma_total_predicted,
        relative_error=relative_error,
        passes_threshold=passes_threshold,
        avg_distance=avg_distance,
        avg_speed=avg_speed,
        trajectory_length=trajectory_length
    )


def analyze_velocity_regime(
    entities: List[MovingEntity],
    planet_center: Tuple[float, float],
    regime_name: str = "unknown"
) -> Dict:
    """
    Analyze all entities in a velocity regime.

    Args:
        entities: List of entities in same velocity regime
        planet_center: (cx, cy) gravitational center
        regime_name: Name of velocity regime

    Returns:
        Dictionary with aggregate statistics
    """
    decompositions = [
        analyze_entity_time_dilation(entity, planet_center)
        for entity in entities
    ]

    # Aggregate statistics
    gamma_eff_measured = [d.gamma_eff_measured for d in decompositions]
    gamma_SR_avg = [d.gamma_SR_avg for d in decompositions]
    gamma_grav_avg = [d.gamma_grav_avg for d in decompositions]
    gamma_predicted = [d.gamma_total_predicted for d in decompositions]
    relative_errors = [d.relative_error for d in decompositions]

    passes_count = sum(d.passes_threshold for d in decompositions)
    pass_rate = passes_count / len(decompositions) if decompositions else 0.0

    return {
        'regime_name': regime_name,
        'count': len(entities),
        'avg_gamma_eff': float(np.mean(gamma_eff_measured)),
        'std_gamma_eff': float(np.std(gamma_eff_measured)),
        'avg_gamma_SR': float(np.mean(gamma_SR_avg)),
        'avg_gamma_grav': float(np.mean(gamma_grav_avg)),
        'avg_gamma_predicted': float(np.mean(gamma_predicted)),
        'avg_relative_error': float(np.mean(relative_errors)),
        'max_relative_error': float(np.max(relative_errors)),
        'pass_rate': pass_rate,
        'passes_threshold': pass_rate > 0.8,  # 80% must pass
        'decompositions': decompositions
    }


def analyze_gravitational_gradient(
    entities: List[MovingEntity],
    planet_center: Tuple[float, float],
    distance_bins: List[float] = None
) -> Dict:
    """
    Analyze time dilation vs distance from planet.

    Args:
        entities: All entities
        planet_center: (cx, cy) center
        distance_bins: Radial bins for grouping

    Returns:
        Dictionary with gradient statistics
    """
    if distance_bins is None:
        distance_bins = [0, 15, 25, 35, 45, 60]

    # Bin entities by average distance
    binned_entities = {i: [] for i in range(len(distance_bins) - 1)}

    for entity in entities:
        decomp = analyze_entity_time_dilation(entity, planet_center)

        # Find appropriate bin
        for i in range(len(distance_bins) - 1):
            if distance_bins[i] <= decomp.avg_distance < distance_bins[i+1]:
                binned_entities[i].append(decomp)
                break

    # Compute statistics per bin
    gradient_data = []
    for i in range(len(distance_bins) - 1):
        decomps = binned_entities[i]

        if len(decomps) == 0:
            continue

        r_center = (distance_bins[i] + distance_bins[i+1]) / 2

        gamma_grav_values = [d.gamma_grav_avg for d in decomps]
        gamma_eff_values = [d.gamma_eff_measured for d in decomps]

        gradient_data.append({
            'distance': r_center,
            'count': len(decomps),
            'avg_gamma_grav': float(np.mean(gamma_grav_values)),
            'std_gamma_grav': float(np.std(gamma_grav_values)),
            'avg_gamma_eff': float(np.mean(gamma_eff_values)),
            'std_gamma_eff': float(np.std(gamma_eff_values))
        })

    # Check for gradient (gamma should decrease with distance)
    gammas = [d['avg_gamma_grav'] for d in gradient_data]
    has_gradient = all(gammas[i] >= gammas[i+1] for i in range(len(gammas)-1))

    return {
        'gradient_data': gradient_data,
        'has_monotonic_gradient': has_gradient,
        'max_gamma': float(np.max(gammas)) if gammas else 1.0,
        'min_gamma': float(np.min(gammas)) if gammas else 1.0,
        'gradient_strength': float(np.max(gammas) - np.min(gammas)) if gammas else 0.0
    }


def validate_experiment(
    entities: List[MovingEntity],
    planet_center: Tuple[float, float],
    verbose: bool = True
) -> Dict:
    """
    Validate experiment against success criteria.

    Success Criteria:
    1. Gravitational gradient exists (gamma decreases with distance)
    2. Velocity effects match SR (gamma_SR = 1/sqrt(1-v^2) within 10%)
    3. Effects multiply (gamma_total = gamma_grav * gamma_SR within 15%)
    4. Stable equilibrium (no collapse, no runaway)
    5. Smooth fields (no binary cutoffs)

    Args:
        entities: All mobile entities
        planet_center: (cx, cy) center
        verbose: Print detailed results

    Returns:
        Dictionary with validation results
    """
    # Organize entities by velocity regime
    slow = [e for e in entities if e.speed < 0.2]
    moderate = [e for e in entities if 0.2 <= e.speed < 0.7]
    fast = [e for e in entities if 0.7 <= e.speed < 0.95]
    ultra = [e for e in entities if e.speed >= 0.95]

    regimes = {
        'slow': slow,
        'moderate': moderate,
        'fast': fast,
        'ultra': ultra
    }

    # Analyze each regime
    regime_results = {}
    for name, regime_entities in regimes.items():
        if len(regime_entities) > 0:
            regime_results[name] = analyze_velocity_regime(
                regime_entities,
                planet_center,
                regime_name=name
            )

    # Criterion 1: Gravitational gradient
    gradient_analysis = analyze_gravitational_gradient(entities, planet_center)
    criterion_1 = gradient_analysis['has_monotonic_gradient']

    # Criterion 2: Velocity effects match SR
    # Check if gamma_SR matches 1/sqrt(1-v^2) for each entity
    sr_errors = []
    for entity in entities:
        expected_gamma_SR = lorentz_gamma(tuple(entity.velocity))
        measured_gamma_SR = np.mean(entity.gamma_SR_history) if entity.gamma_SR_history else entity.gamma_SR
        if expected_gamma_SR > 1e-10:
            error = abs(expected_gamma_SR - measured_gamma_SR) / expected_gamma_SR
            sr_errors.append(error)

    criterion_2 = np.mean(sr_errors) < 0.1 if sr_errors else False

    # Criterion 3: Effects multiply (checked in regime analysis)
    criterion_3_results = [
        result['passes_threshold']
        for result in regime_results.values()
    ]
    criterion_3 = all(criterion_3_results) if criterion_3_results else False

    # Criterion 4: Stable equilibrium
    # Check if any entity has runaway gamma (> 100) or collapse (gamma < 0.5)
    gammas = [
        analyze_entity_time_dilation(e, planet_center).gamma_eff_measured
        for e in entities
    ]
    criterion_4 = all(0.5 < g < 100 for g in gammas)

    # Criterion 5: Smooth fields
    # Check standard deviation of gamma within each distance bin
    criterion_5 = all(
        d['std_gamma_grav'] < 0.5
        for d in gradient_analysis['gradient_data']
    )

    # Overall success
    all_criteria = [criterion_1, criterion_2, criterion_3, criterion_4, criterion_5]
    success = all(all_criteria)

    validation_results = {
        'success': success,
        'criteria': {
            '1_gravitational_gradient': criterion_1,
            '2_velocity_effects_match_SR': criterion_2,
            '3_effects_multiply': criterion_3,
            '4_stable_equilibrium': criterion_4,
            '5_smooth_fields': criterion_5
        },
        'regime_results': regime_results,
        'gradient_analysis': gradient_analysis,
        'sr_error_avg': float(np.mean(sr_errors)) if sr_errors else 0.0
    }

    if verbose:
        print_validation_report(validation_results)

    return validation_results


def print_validation_report(results: Dict):
    """Print human-readable validation report."""
    print("=" * 70)
    print("VALIDATION REPORT")
    print("=" * 70)
    print()

    # Overall success
    status = "PASS" if results['success'] else "FAIL"
    print(f"Overall Status: {status}")
    print()

    # Criteria breakdown
    print("Success Criteria:")
    criteria = results['criteria']
    for name, passes in criteria.items():
        symbol = "PASS" if passes else "FAIL"
        print(f"  {symbol} {name.replace('_', ' ').title()}")
    print()

    # Regime results
    print("Velocity Regime Analysis:")
    print(f"{'Regime':<12} {'Count':<6} {'g_eff':<8} {'g_grav':<8} {'g_SR':<8} {'Error':<8} {'Pass'}")
    print("-" * 70)

    for regime_name, data in results['regime_results'].items():
        symbol = "PASS" if data['passes_threshold'] else "FAIL"
        print(f"{regime_name:<12} {data['count']:<6} "
              f"{data['avg_gamma_eff']:<8.3f} {data['avg_gamma_grav']:<8.3f} "
              f"{data['avg_gamma_SR']:<8.3f} {data['avg_relative_error']:<8.2%} {symbol}")
    print()

    # Gradient analysis
    print("Gravitational Gradient:")
    gradient = results['gradient_analysis']
    print(f"  Monotonic: {'Yes' if gradient['has_monotonic_gradient'] else 'No'}")
    print(f"  Strength: {gradient['gradient_strength']:.3f}")
    print(f"  Range: {gradient['min_gamma']:.3f} - {gradient['max_gamma']:.3f}")
    print()

    # Distance profile
    print(f"{'Distance':<10} {'Count':<8} {'g_grav':<10} {'g_eff':<10}")
    print("-" * 40)
    for data in gradient['gradient_data']:
        print(f"{data['distance']:<10.1f} {data['count']:<8} "
              f"{data['avg_gamma_grav']:<10.3f} {data['avg_gamma_eff']:<10.3f}")
    print()


def export_analysis_csv(
    entities: List[MovingEntity],
    planet_center: Tuple[float, float],
    output_path: str
):
    """
    Export detailed analysis to CSV for external processing.

    Args:
        entities: All entities
        planet_center: (cx, cy) center
        output_path: Path to output CSV file
    """
    import csv

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'entity_id', 'speed', 'avg_distance',
            'proper_time', 'coordinate_time',
            'gamma_eff_measured', 'gamma_SR_avg', 'gamma_grav_avg',
            'gamma_predicted', 'relative_error', 'passes_threshold'
        ])

        # Data rows
        for entity in entities:
            decomp = analyze_entity_time_dilation(entity, planet_center)
            writer.writerow([
                decomp.entity_id,
                f"{decomp.avg_speed:.4f}",
                f"{decomp.avg_distance:.2f}",
                f"{decomp.proper_time:.2f}",
                decomp.coordinate_time,
                f"{decomp.gamma_eff_measured:.4f}",
                f"{decomp.gamma_SR_avg:.4f}",
                f"{decomp.gamma_grav_avg:.4f}",
                f"{decomp.gamma_total_predicted:.4f}",
                f"{decomp.relative_error:.4f}",
                decomp.passes_threshold
            ])

    print(f"Analysis exported to {output_path}")


if __name__ == "__main__":
    # Demo: Analyze mock results
    print("=" * 70)
    print("ANALYSIS MODULE - DEMO")
    print("=" * 70)
    print()

    # This would normally load results from an experiment run
    print("This module is designed to be imported and used with Experiment51i results.")
    print()
    print("Usage example:")
    print("""
    from analysis import validate_experiment

    # After running experiment
    experiment = Experiment51i(config)
    experiment.run()

    # Validate results
    validation = validate_experiment(
        experiment.mobile_entities,
        planet_center=(50.0, 50.0),
        verbose=True
    )

    # Export to CSV
    export_analysis_csv(
        experiment.mobile_entities,
        planet_center=(50.0, 50.0),
        output_path='results/analysis.csv'
    )
    """)
    print()
