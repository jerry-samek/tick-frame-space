#!/usr/bin/env python3
"""
Experiment 56a: Hydrogen Atom Formation and Binding Validation

Tests whether a hydrogen atom (proton + electron) maintains stable binding
over 10,000+ ticks using gamma-well physics.

Success Criteria:
- Electron remains bound to proton for 10,000+ ticks
- Orbital motion is stable (no escape, no collapse)
- Binding energy remains negative (bound state)
- Gamma-well depth consistent over time
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from typing import List, Dict

# Import modules from Experiment 56
from composite_structure import (
    CompositeObject, CompositeBuilder, CompositeType, Pattern, PatternType
)
from binding_detection import CompositeBindingManager, GammaWellDetector


# ============================================================================
# Experiment Configuration
# ============================================================================

class Exp56aConfig:
    """Configuration for hydrogen atom stability test."""

    # Simulation parameters
    grid_size = 100
    num_ticks = 10000
    snapshot_interval = 100  # Save state every N ticks

    # Hydrogen atom parameters
    proton_mass = 1.0
    proton_energy = 10.0
    electron_mass = 0.001
    electron_energy = 5.0
    orbital_radius = 2.0
    binding_energy_initial = -13.6  # eV analog

    # Composite position
    center_position = np.array([50.0, 50.0])

    # Field parameters (from v11 baseline)
    alpha = 0.012
    gamma_damp = 0.0005
    scale = 0.75
    R = 1.2
    D = 0.01
    E_max = 15.0
    capacity_min = 0.1
    work_threshold = 0.5


# ============================================================================
# Experiment Runner
# ============================================================================

class HydrogenStabilityExperiment:
    """
    Runs hydrogen atom stability test over 10,000 ticks.
    """

    def __init__(self, config: Exp56aConfig = None):
        self.config = config or Exp56aConfig()

        # Initialize binding manager
        self.manager = CompositeBindingManager(
            grid_size=self.config.grid_size,
            well_detector=GammaWellDetector(
                grid_size=self.config.grid_size,
                alpha=self.config.alpha,
                gamma_damp=self.config.gamma_damp,
                scale=self.config.scale,
                R=self.config.R,
                D=self.config.D,
                E_max=self.config.E_max,
                capacity_min=self.config.capacity_min,
                work_threshold=self.config.work_threshold
            )
        )

        # Create hydrogen atom
        self.hydrogen = CompositeBuilder.create_hydrogen_atom(
            composite_id="H_001",
            center_position=self.config.center_position,
            orbital_radius=self.config.orbital_radius,
            binding_energy=self.config.binding_energy_initial
        )

        self.manager.add_composite(self.hydrogen)

        # Tracking data
        self.history = {
            'tick': [],
            'binding_energy': [],
            'gamma_at_center': [],
            'electron_distance': [],
            'electron_phase': [],
            'stable': [],
            'num_constituents': []
        }

    def run(self, verbose: bool = True):
        """
        Run the experiment for configured number of ticks.

        Args:
            verbose: If True, print progress updates
        """
        if verbose:
            print("=" * 70)
            print("EXPERIMENT 56a: HYDROGEN ATOM STABILITY TEST")
            print("=" * 70)
            print()
            print(f"Configuration:")
            print(f"  Grid size: {self.config.grid_size}")
            print(f"  Number of ticks: {self.config.num_ticks}")
            print(f"  Snapshot interval: {self.config.snapshot_interval}")
            print(f"  Orbital radius: {self.config.orbital_radius:.3f}")
            print(f"  Initial binding energy: {self.config.binding_energy_initial:.1f}")
            print()
            print("Starting simulation...")
            print()

        for tick in range(self.config.num_ticks):
            # Update composites
            update_fields = (tick % 10 == 0)  # Update fields every 10 ticks
            self.manager.update_all_composites(dt=1.0, update_fields=update_fields)

            # Record snapshot
            if tick % self.config.snapshot_interval == 0:
                self._record_snapshot(tick)

                if verbose and tick % 1000 == 0:
                    self._print_status(tick)

        if verbose:
            print()
            print("Simulation complete!")
            print()
            self._print_final_summary()

    def _record_snapshot(self, tick: int):
        """Record current state to history."""
        # Get binding analysis
        analysis = self.manager.analyze_composite_binding(self.hydrogen)

        # Get electron state
        electrons = self.hydrogen.get_constituent_by_type(PatternType.ELECTRON)
        if electrons:
            electron = electrons[0]
            electron_distance = electron.distance_from_center
            electron_phase = electron.orbital_phase
        else:
            electron_distance = 0.0
            electron_phase = 0.0

        # Record data
        self.history['tick'].append(tick)
        self.history['binding_energy'].append(analysis['binding_energy'])
        self.history['gamma_at_center'].append(analysis['gamma_at_center'])
        self.history['electron_distance'].append(electron_distance)
        self.history['electron_phase'].append(electron_phase)
        self.history['stable'].append(self.hydrogen.stable)
        self.history['num_constituents'].append(len(self.hydrogen.constituents))

    def _print_status(self, tick: int):
        """Print current status."""
        analysis = self.manager.analyze_composite_binding(self.hydrogen)
        electrons = self.hydrogen.get_constituent_by_type(PatternType.ELECTRON)

        print(f"  Tick {tick:5d}:")
        print(f"    Binding energy: {analysis['binding_energy']:8.3f}")
        print(f"    Gamma at center: {analysis['gamma_at_center']:7.3f}")
        print(f"    Electron distance: {electrons[0].distance_from_center:6.3f}" if electrons else "    No electron")
        print(f"    Stable: {self.hydrogen.stable}")

    def _print_final_summary(self):
        """Print final experiment summary."""
        print("=" * 70)
        print("FINAL RESULTS")
        print("=" * 70)
        print()

        # Check success criteria
        final_stable = self.history['stable'][-1]
        final_constituents = self.history['num_constituents'][-1]
        final_binding = self.history['binding_energy'][-1]

        mean_binding = np.mean(self.history['binding_energy'])
        std_binding = np.std(self.history['binding_energy'])

        mean_gamma = np.mean(self.history['gamma_at_center'])
        std_gamma = np.std(self.history['gamma_at_center'])

        mean_distance = np.mean(self.history['electron_distance'])
        std_distance = np.std(self.history['electron_distance'])

        print(f"Stability Check:")
        print(f"  Final tick: {self.history['tick'][-1]}")
        print(f"  Composite stable: {final_stable}")
        print(f"  Constituents retained: {final_constituents}/2")
        print()

        print(f"Binding Energy:")
        print(f"  Final: {final_binding:.3f}")
        print(f"  Mean: {mean_binding:.3f} +/- {std_binding:.3f}")
        print(f"  Bound state: {'YES' if final_binding < 0 else 'NO'}")
        print()

        print(f"Gamma-Well Depth:")
        print(f"  Mean: {mean_gamma:.3f} +/- {std_gamma:.3f}")
        print()

        print(f"Electron Orbital Distance:")
        print(f"  Target: {self.config.orbital_radius:.3f}")
        print(f"  Mean: {mean_distance:.3f} +/- {std_distance:.3f}")
        print(f"  Deviation: {abs(mean_distance - self.config.orbital_radius):.3f}")
        print()

        # Success verdict
        print("=" * 70)
        success = (
            final_stable and
            final_constituents == 2 and
            final_binding < 0 and
            abs(mean_distance - self.config.orbital_radius) < 0.5
        )

        if success:
            print("VERDICT: SUCCESS")
            print("Hydrogen atom remained stable for 10,000+ ticks!")
        else:
            print("VERDICT: FAILURE")
            print("Composite became unstable or lost constituents.")
        print("=" * 70)

    def plot_results(self, save_path: Path = None):
        """
        Plot experiment results.

        Args:
            save_path: If provided, save plot to this path
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Experiment 56a: Hydrogen Atom Stability Test', fontsize=16)

        ticks = self.history['tick']

        # Plot 1: Binding energy over time
        ax1 = axes[0, 0]
        ax1.plot(ticks, self.history['binding_energy'], 'b-', linewidth=1)
        ax1.axhline(y=0, color='r', linestyle='--', label='Unbound threshold')
        ax1.set_xlabel('Tick')
        ax1.set_ylabel('Binding Energy')
        ax1.set_title('Binding Energy (negative = bound)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Plot 2: Gamma-well depth
        ax2 = axes[0, 1]
        ax2.plot(ticks, self.history['gamma_at_center'], 'g-', linewidth=1)
        ax2.set_xlabel('Tick')
        ax2.set_ylabel('Gamma at Center')
        ax2.set_title('Gamma-Well Depth (time dilation)')
        ax2.grid(True, alpha=0.3)

        # Plot 3: Electron orbital distance
        ax3 = axes[1, 0]
        ax3.plot(ticks, self.history['electron_distance'], 'm-', linewidth=1)
        ax3.axhline(y=self.config.orbital_radius, color='r', linestyle='--',
                   label=f'Target radius: {self.config.orbital_radius:.2f}')
        ax3.set_xlabel('Tick')
        ax3.set_ylabel('Electron Distance from Center')
        ax3.set_title('Orbital Stability')
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        # Plot 4: Electron orbital phase
        ax4 = axes[1, 1]
        ax4.plot(ticks, self.history['electron_phase'], 'c-', linewidth=1)
        ax4.set_xlabel('Tick')
        ax4.set_ylabel('Orbital Phase (radians)')
        ax4.set_title('Orbital Motion (phase accumulation)')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
            print(f"Plot saved to: {save_path}")
        else:
            plt.show()

    def save_results(self, output_path: Path):
        """
        Save experiment results to JSON file.

        Args:
            output_path: Path to save results
        """
        results = {
            'experiment': 'Experiment 56a: Hydrogen Atom Stability',
            'config': {
                'grid_size': self.config.grid_size,
                'num_ticks': self.config.num_ticks,
                'orbital_radius': self.config.orbital_radius,
                'binding_energy_initial': self.config.binding_energy_initial
            },
            'history': {
                'tick': self.history['tick'],
                'binding_energy': self.history['binding_energy'],
                'gamma_at_center': self.history['gamma_at_center'],
                'electron_distance': self.history['electron_distance'],
                'electron_phase': self.history['electron_phase'],
                'stable': self.history['stable'],
                'num_constituents': self.history['num_constituents']
            },
            'final_summary': {
                'final_tick': self.history['tick'][-1],
                'final_stable': self.history['stable'][-1],
                'final_binding_energy': self.history['binding_energy'][-1],
                'mean_binding_energy': float(np.mean(self.history['binding_energy'])),
                'std_binding_energy': float(np.std(self.history['binding_energy'])),
                'mean_gamma': float(np.mean(self.history['gamma_at_center'])),
                'mean_electron_distance': float(np.mean(self.history['electron_distance'])),
                'std_electron_distance': float(np.std(self.history['electron_distance']))
            }
        }

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to: {output_path}")


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    # Run experiment
    experiment = HydrogenStabilityExperiment()
    experiment.run(verbose=True)

    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)

    experiment.save_results(output_dir / "exp56a_hydrogen_stability.json")
    experiment.plot_results(save_path=output_dir / "exp56a_hydrogen_stability.png")

    print()
    print("Experiment 56a complete!")
    print(f"Results saved to: {output_dir}")
