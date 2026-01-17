#!/usr/bin/env python3
"""
Complete Analysis Pipeline for Experiment 51i (V9)

Runs experiment, performs analysis, generates visualizations, and validates results.
"""

import sys
import os
from pathlib import Path

from config import get_config, list_configurations
from experiment_51i import Experiment51i
from analysis import validate_experiment, export_analysis_csv
from visualize import (
    plot_summary_dashboard,
    plot_gamma_field,
    plot_load_energy_fields,
    plot_entity_trajectories,
    plot_gamma_vs_distance,
    plot_gamma_vs_velocity,
    create_animation
)


def run_full_pipeline(config_name: str = "baseline", output_dir: str = "results"):
    """
    Run complete experimental pipeline.

    Args:
        config_name: Configuration to use
        output_dir: Directory for outputs
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    print(f"Output directory: {output_path.absolute()}")
    print()

    # Load configuration
    print("=" * 70)
    print("LOADING CONFIGURATION")
    print("=" * 70)
    config = get_config(config_name)
    print(config.summary())
    print()

    # Run experiment
    print("=" * 70)
    print("RUNNING EXPERIMENT")
    print("=" * 70)
    experiment = Experiment51i(config)
    experiment.run()
    experiment.print_results()

    planet_center = config.entities.planet_center
    planet_radius = config.entities.planet_radius

    # Validate results
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)
    validation = validate_experiment(
        experiment.mobile_entities,
        planet_center=planet_center,
        verbose=True
    )
    print()

    # Export analysis CSV
    csv_path = output_path / f"{config_name}_analysis.csv"
    export_analysis_csv(
        experiment.mobile_entities,
        planet_center=planet_center,
        output_path=str(csv_path)
    )
    print()

    # Generate visualizations
    print("=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)

    # 1. Summary dashboard
    print("Creating summary dashboard...")
    plot_summary_dashboard(
        experiment.mobile_entities,
        experiment.fields,
        planet_center=planet_center,
        planet_radius=planet_radius,
        save_path=str(output_path / f"{config_name}_dashboard.png")
    )

    # 2. Gamma field
    print("Creating gamma field plot...")
    plot_gamma_field(
        experiment.fields,
        planet_center=planet_center,
        planet_radius=planet_radius,
        save_path=str(output_path / f"{config_name}_gamma_field.png")
    )

    # 3. Load and energy fields
    print("Creating load/energy fields plot...")
    plot_load_energy_fields(
        experiment.fields,
        planet_center=planet_center,
        planet_radius=planet_radius,
        save_path=str(output_path / f"{config_name}_fields.png")
    )

    # 4. Entity trajectories
    print("Creating trajectory plot...")
    plot_entity_trajectories(
        experiment.mobile_entities,
        experiment.fields,
        planet_center=planet_center,
        planet_radius=planet_radius,
        save_path=str(output_path / f"{config_name}_trajectories.png")
    )

    # 5. Gamma vs distance
    print("Creating gamma vs distance plot...")
    plot_gamma_vs_distance(
        experiment.mobile_entities,
        planet_center=planet_center,
        save_path=str(output_path / f"{config_name}_gamma_distance.png")
    )

    # 6. Gamma vs velocity
    print("Creating gamma vs velocity plot...")
    plot_gamma_vs_velocity(
        experiment.mobile_entities,
        planet_center=planet_center,
        save_path=str(output_path / f"{config_name}_gamma_velocity.png")
    )

    # 7. Animation (optional - can be slow)
    if len(experiment.snapshots) > 0:
        print("Creating animation (this may take a while)...")
        try:
            create_animation(
                experiment,
                output_path=str(output_path / f"{config_name}_animation.gif"),
                fps=5,
                max_frames=50
            )
        except Exception as e:
            print(f"Warning: Animation creation failed: {e}")
            print("Continuing without animation...")

    print()
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print()
    print(f"Results saved to: {output_path.absolute()}")
    print()

    # Print validation summary
    if validation['success']:
        print("✓ EXPERIMENT PASSED ALL SUCCESS CRITERIA")
    else:
        print("✗ EXPERIMENT FAILED SOME CRITERIA")
        failed = [name for name, passed in validation['criteria'].items() if not passed]
        print(f"  Failed criteria: {', '.join(failed)}")

    print()

    return experiment, validation


def compare_configurations(config_names: list, output_dir: str = "comparison"):
    """
    Run multiple configurations and compare results.

    Args:
        config_names: List of configuration names to compare
        output_dir: Directory for comparison outputs
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    results = {}

    for config_name in config_names:
        print()
        print("=" * 70)
        print(f"RUNNING CONFIGURATION: {config_name}")
        print("=" * 70)
        print()

        config = get_config(config_name)
        experiment = Experiment51i(config)
        experiment.run()

        validation = validate_experiment(
            experiment.mobile_entities,
            planet_center=config.entities.planet_center,
            verbose=False
        )

        results[config_name] = {
            'experiment': experiment,
            'validation': validation,
            'config': config
        }

    # Print comparison table
    print()
    print("=" * 70)
    print("CONFIGURATION COMPARISON")
    print("=" * 70)
    print()

    print(f"{'Configuration':<20} {'Success':<10} {'Gradient':<10} {'SR Match':<10} {'Multiply':<10}")
    print("-" * 70)

    for name, data in results.items():
        val = data['validation']
        success = "✓" if val['success'] else "✗"
        c1 = "✓" if val['criteria']['1_gravitational_gradient'] else "✗"
        c2 = "✓" if val['criteria']['2_velocity_effects_match_SR'] else "✗"
        c3 = "✓" if val['criteria']['3_effects_multiply'] else "✗"

        print(f"{name:<20} {success:<10} {c1:<10} {c2:<10} {c3:<10}")

    print()

    return results


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_analysis.py <config_name> [output_dir]")
        print()
        print("  python run_analysis.py compare <config1> <config2> ... [output_dir]")
        print()
        print("Available configurations:")
        for name in list_configurations():
            print(f"  - {name}")
        print()
        return

    command = sys.argv[1]

    if command == "compare":
        # Comparison mode
        if len(sys.argv) < 3:
            print("Error: Need at least 2 configurations to compare")
            return

        config_names = sys.argv[2:]
        output_dir = "comparison"

        # Check if last arg is output dir
        if not config_names[-1] in list_configurations():
            output_dir = config_names[-1]
            config_names = config_names[:-1]

        compare_configurations(config_names, output_dir)

    else:
        # Single run mode
        config_name = command
        output_dir = sys.argv[2] if len(sys.argv) > 2 else f"results_{config_name}"

        run_full_pipeline(config_name, output_dir)


if __name__ == "__main__":
    main()
