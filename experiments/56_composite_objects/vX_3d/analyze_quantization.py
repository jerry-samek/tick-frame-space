#!/usr/bin/env python3
"""
Quantization Analysis for Experiment 56 V4

Analyzes 100k tick simulation results to test quantization hypothesis from Doc 070_01 §4:
"This process naturally drives the system toward stable orbital levels, quantized
energy states, and robust equilibrium distributions."

Tests for:
1. Radial shell formation (discrete peaks in ρ(r))
2. Energy level discretization (gaps in energy histogram)
3. Velocity distribution equilibration (Maxwell-Boltzmann)
4. Angular momentum quantization
5. Correlation functions (g(r), autocorrelations)
"""

import numpy as np
import json
from pathlib import Path
from scipy import stats
from scipy.signal import find_peaks
import matplotlib.pyplot as plt


class QuantizationAnalyzer:
    """Analyze simulation results for quantization signatures."""

    def __init__(self, results_file):
        """Load simulation results."""
        print(f"Loading results from: {results_file}")
        with open(results_file, 'r') as f:
            data = json.load(f)

        self.config = data['config']
        self.results = data['results']
        self.snapshots = data['snapshots']
        self.detailed_snapshots = data.get('detailed_snapshots', [])

        print(f"  Loaded {len(self.snapshots)} snapshots")
        print(f"  Loaded {len(self.detailed_snapshots)} detailed snapshots")

        # Extract time series
        self.ticks = np.array([s['tick'] for s in self.snapshots])
        self.radii_rms = np.array([s['cloud_radius_rms'] for s in self.snapshots])
        self.radii_mean = np.array([s['cloud_radius_mean'] for s in self.snapshots])
        self.kinetic_energies = np.array([s['total_kinetic_energy'] for s in self.snapshots])
        self.angular_momenta = np.array([s['angular_momentum'] for s in self.snapshots])

        if 'total_energy' in self.snapshots[0]:
            self.total_energies = np.array([s['total_energy'] for s in self.snapshots])
            self.potential_energies = np.array([s['total_potential_energy'] for s in self.snapshots])
        else:
            self.total_energies = None
            self.potential_energies = None

    def detect_equilibration(self, observable, window=100):
        """
        Detect equilibration point (where variance stabilizes).

        Returns:
            eq_index: Index in snapshots array where equilibration occurs
        """
        if len(observable) < window * 2:
            return len(observable) // 2  # Default to midpoint

        # Compute rolling standard deviation
        rolling_std = []
        for i in range(len(observable) - window):
            rolling_std.append(np.std(observable[i:i+window]))

        rolling_std = np.array(rolling_std)

        # Equilibration = where std stops decreasing (gradient near zero)
        gradient = np.gradient(rolling_std)

        # Find first point where gradient is near zero and stays near zero
        threshold = np.std(gradient) * 0.1  # 10% of typical fluctuation
        equilibrated = np.where(np.abs(gradient) < threshold)[0]

        if len(equilibrated) > 0:
            eq_index = equilibrated[0]
        else:
            eq_index = len(observable) // 2

        return eq_index

    def analyze_radial_shells(self, prominence=0.05):
        """
        Analyze radial density profile for shell structure.

        Returns:
            dict with shell detection results
        """
        print("\n" + "="*70)
        print("RADIAL SHELL ANALYSIS")
        print("="*70)

        # Use equilibrated portion of simulation
        eq_index = self.detect_equilibration(self.radii_rms)
        eq_tick = self.ticks[eq_index]

        print(f"\nEquilibration detected at tick {eq_tick}")
        print(f"Analyzing radial density from equilibrated snapshots...")

        # Get radial profiles from detailed snapshots after equilibration
        profiles = []
        for snap in self.detailed_snapshots:
            if snap['tick'] >= eq_tick and 'radial_profile_densities' in snap:
                profiles.append(np.array(snap['radial_profile_densities']))

        if len(profiles) == 0:
            print("WARNING: No radial density profiles found in detailed snapshots")
            return {'n_shells': 0, 'peaks': [], 'evidence': 'insufficient_data'}

        # Average radial profile over equilibrated period
        radial_bins = np.array(self.detailed_snapshots[0]['radial_profile_bins'])
        avg_density = np.mean(profiles, axis=0)
        std_density = np.std(profiles, axis=0)

        # Detect peaks (shells)
        peaks, properties = find_peaks(avg_density, prominence=prominence)

        n_shells = len(peaks)
        shell_radii = radial_bins[peaks]
        shell_densities = avg_density[peaks]

        print(f"\nShell Detection Results:")
        print(f"  Number of shells detected: {n_shells}")

        if n_shells > 0:
            print(f"  Shell radii: {shell_radii}")
            print(f"  Shell densities: {shell_densities}")
            print(f"  Prominences: {properties['prominences']}")

            # Check if shells are stable (low variance)
            shell_stability = []
            for i, peak in enumerate(peaks):
                peak_densities = [prof[peak] for prof in profiles]
                variance = np.std(peak_densities) / np.mean(peak_densities)
                shell_stability.append(variance)
                print(f"  Shell {i+1} stability (CV): {variance:.3f}")

            evidence = 'strong' if n_shells >= 2 else 'weak'
        else:
            print("  No discrete shells detected - smooth distribution")
            shell_stability = []
            evidence = 'none'

        return {
            'n_shells': n_shells,
            'peaks': shell_radii.tolist() if n_shells > 0 else [],
            'densities': shell_densities.tolist() if n_shells > 0 else [],
            'stability': shell_stability,
            'radial_bins': radial_bins.tolist(),
            'avg_density': avg_density.tolist(),
            'std_density': std_density.tolist(),
            'evidence': evidence
        }

    def analyze_energy_levels(self, gap_threshold=0.001):
        """
        Analyze fragment energy distribution for quantization.

        Returns:
            dict with energy level analysis results
        """
        print("\n" + "="*70)
        print("ENERGY LEVEL ANALYSIS")
        print("="*70)

        # Extract fragment energies from equilibrated detailed snapshots
        eq_index = self.detect_equilibration(self.kinetic_energies)
        eq_tick = self.ticks[eq_index]

        print(f"\nAnalyzing fragment energies from tick {eq_tick} onward...")

        all_energies = []
        for snap in self.detailed_snapshots:
            if snap['tick'] >= eq_tick and 'fragment_data' in snap:
                for frag in snap['fragment_data']:
                    all_energies.append(frag['kinetic_energy'])

        if len(all_energies) == 0:
            print("WARNING: No fragment energy data found")
            return {'n_levels': 0, 'gaps': [], 'evidence': 'insufficient_data'}

        all_energies = np.array(all_energies)

        print(f"  Total fragment energy samples: {len(all_energies)}")
        print(f"  Energy range: [{np.min(all_energies):.6f}, {np.max(all_energies):.6f}]")

        # Create histogram
        n_bins = self.config['energy_histogram_bins']
        hist, bins = np.histogram(all_energies, bins=n_bins)

        # Detect gaps (forbidden energy levels)
        gaps = []
        in_gap = False
        gap_start = None

        for i in range(1, len(hist) - 1):
            if hist[i] == 0 and hist[i-1] > 0:
                # Start of gap
                gap_start = bins[i]
                in_gap = True
            elif hist[i] > 0 and in_gap:
                # End of gap
                gap_end = bins[i]
                gap_width = gap_end - gap_start
                if gap_width >= gap_threshold:
                    gaps.append((gap_start, gap_end, gap_width))
                in_gap = False

        n_gaps = len(gaps)

        print(f"\nEnergy Gap Detection:")
        print(f"  Number of gaps detected: {n_gaps}")

        if n_gaps > 0:
            for i, (start, end, width) in enumerate(gaps):
                print(f"  Gap {i+1}: [{start:.6f}, {end:.6f}], width = {width:.6f}")
            evidence = 'strong' if n_gaps >= 2 else 'weak'
        else:
            print("  No discrete energy gaps - continuous distribution")
            evidence = 'none'

        # Compute discrete peaks in energy distribution
        peaks, _ = find_peaks(hist, prominence=len(all_energies) * 0.01)
        energy_peaks = bins[peaks]

        return {
            'n_levels': len(peaks),
            'n_gaps': n_gaps,
            'gaps': [(float(s), float(e), float(w)) for s, e, w in gaps],
            'energy_peaks': energy_peaks.tolist(),
            'histogram': hist.tolist(),
            'bins': bins.tolist(),
            'evidence': evidence
        }

    def analyze_velocity_distribution(self):
        """
        Test if velocity distribution follows Maxwell-Boltzmann.

        Returns:
            dict with MB fit results and p-value
        """
        print("\n" + "="*70)
        print("VELOCITY DISTRIBUTION ANALYSIS")
        print("="*70)

        # Extract equilibrated velocity data
        eq_index = self.detect_equilibration(self.kinetic_energies)
        eq_tick = self.ticks[eq_index]

        print(f"\nAnalyzing velocities from tick {eq_tick} onward...")

        all_speeds = []
        for snap in self.detailed_snapshots:
            if snap['tick'] >= eq_tick and 'velocity_speeds' in snap:
                all_speeds.extend(snap['velocity_speeds'])

        if len(all_speeds) == 0:
            print("WARNING: No velocity data found")
            return {'mb_fit': False, 'p_value': 0.0, 'evidence': 'insufficient_data'}

        all_speeds = np.array(all_speeds)

        print(f"  Total velocity samples: {len(all_speeds)}")
        print(f"  Mean speed: {np.mean(all_speeds):.6f}")
        print(f"  Std speed: {np.std(all_speeds):.6f}")

        # Fit to Rayleigh distribution (2D Maxwell-Boltzmann for speeds)
        # P(v) = (v/σ²) × exp(-v²/(2σ²))
        scale_fit = stats.rayleigh.fit(all_speeds, floc=0)[0]

        # Kolmogorov-Smirnov test
        D, p_value = stats.kstest(all_speeds, lambda x: stats.rayleigh.cdf(x, scale=scale_fit))

        print(f"\nMaxwell-Boltzmann Fit:")
        print(f"  Fitted scale parameter: {scale_fit:.6f}")
        print(f"  KS test statistic: {D:.6f}")
        print(f"  p-value: {p_value:.6f}")

        if p_value > 0.05:
            print(f"  [PASS] MB distribution confirmed (p > 0.05)")
            mb_fit = True
            evidence = 'strong'
        else:
            print(f"  [FAIL] MB distribution rejected (p < 0.05)")
            mb_fit = False
            evidence = 'none'

        # Extract effective temperature
        fragment_mass = self.config['electron_total_mass'] / self.config['n_fragments']
        T_effective = (scale_fit ** 2) * fragment_mass  # kT = m × σ²

        print(f"  Effective temperature: {T_effective:.9f}")

        return {
            'mb_fit': mb_fit,
            'p_value': float(p_value),
            'scale': float(scale_fit),
            'temperature': float(T_effective),
            'mean_speed': float(np.mean(all_speeds)),
            'std_speed': float(np.std(all_speeds)),
            'evidence': evidence
        }

    def analyze_angular_momentum(self):
        """
        Check if angular momentum converges to quantized value.

        Returns:
            dict with L convergence results
        """
        print("\n" + "="*70)
        print("ANGULAR MOMENTUM ANALYSIS")
        print("="*70)

        # Compute rolling statistics
        window = 100
        if len(self.angular_momenta) < window:
            window = len(self.angular_momenta) // 2

        L_mean_rolling = []
        L_std_rolling = []
        ticks_rolling = []

        for i in range(len(self.angular_momenta) - window):
            L_mean_rolling.append(np.mean(self.angular_momenta[i:i+window]))
            L_std_rolling.append(np.std(self.angular_momenta[i:i+window]))
            ticks_rolling.append(self.ticks[i + window//2])

        L_mean_rolling = np.array(L_mean_rolling)
        L_std_rolling = np.array(L_std_rolling)

        # Check convergence (std decreases over time)
        L_std_initial = L_std_rolling[0]
        L_std_final = L_std_rolling[-1]
        convergence_ratio = L_std_final / L_std_initial

        # Final value and stability
        L_final_mean = np.mean(self.angular_momenta[-window:])
        L_final_std = np.std(self.angular_momenta[-window:])

        print(f"\nAngular Momentum Convergence:")
        print(f"  Initial std: {L_std_initial:.6f}")
        print(f"  Final std: {L_std_final:.6f}")
        print(f"  Convergence ratio: {convergence_ratio:.3f}")
        print(f"  Final mean L: {L_final_mean:.6f}")
        print(f"  Final std L: {L_final_std:.6f}")
        print(f"  Relative stability: {L_final_std / abs(L_final_mean) * 100:.2f}%")

        if convergence_ratio < 0.5 and L_final_std < 0.001:
            print(f"  [PASS] Angular momentum quantized")
            quantized = True
            evidence = 'strong'
        elif convergence_ratio < 0.8:
            print(f"  [WEAK] Angular momentum shows partial convergence")
            quantized = False
            evidence = 'weak'
        else:
            print(f"  [FAIL] Angular momentum not converged")
            quantized = False
            evidence = 'none'

        return {
            'quantized': quantized,
            'L_mean': float(L_final_mean),
            'L_std': float(L_final_std),
            'convergence_ratio': float(convergence_ratio),
            'evidence': evidence,
            'rolling_mean': L_mean_rolling.tolist(),
            'rolling_std': L_std_rolling.tolist(),
            'ticks': ticks_rolling
        }

    def analyze_energy_conservation(self):
        """Check total energy conservation."""
        print("\n" + "="*70)
        print("ENERGY CONSERVATION ANALYSIS")
        print("="*70)

        if self.total_energies is None:
            print("WARNING: No total energy data available")
            return {'conserved': False, 'drift': None}

        E_initial = self.total_energies[0]
        E_final = self.total_energies[-1]
        E_mean = np.mean(self.total_energies)
        E_std = np.std(self.total_energies)
        drift = abs(E_final - E_initial) / abs(E_initial) * 100

        print(f"\nTotal Energy:")
        print(f"  Initial: {E_initial:.6f}")
        print(f"  Final: {E_final:.6f}")
        print(f"  Mean: {E_mean:.6f}")
        print(f"  Std: {E_std:.6f}")
        print(f"  Drift: {drift:.4f}%")

        if drift < 1.0:
            print(f"  [PASS] Energy conserved (drift < 1%)")
            conserved = True
        else:
            print(f"  [FAIL] Energy not conserved (drift >= 1%)")
            conserved = False

        return {
            'conserved': conserved,
            'drift': float(drift),
            'E_initial': float(E_initial),
            'E_final': float(E_final),
            'E_mean': float(E_mean),
            'E_std': float(E_std)
        }

    def generate_summary_report(self, shell_results, energy_results, velocity_results, L_results, E_results):
        """Generate comprehensive summary report."""
        print("\n" + "="*70)
        print("QUANTIZATION HYPOTHESIS SUMMARY")
        print("="*70)

        print("\n1. RADIAL SHELL FORMATION:")
        print(f"   Shells detected: {shell_results['n_shells']}")
        print(f"   Evidence: {shell_results['evidence'].upper()}")

        print("\n2. ENERGY LEVEL DISCRETIZATION:")
        print(f"   Energy levels detected: {energy_results['n_levels']}")
        print(f"   Energy gaps detected: {energy_results['n_gaps']}")
        print(f"   Evidence: {energy_results['evidence'].upper()}")

        print("\n3. MAXWELL-BOLTZMANN DISTRIBUTION:")
        print(f"   MB fit: {'YES' if velocity_results['mb_fit'] else 'NO'}")
        print(f"   p-value: {velocity_results['p_value']:.4f}")
        print(f"   Evidence: {velocity_results['evidence'].upper()}")

        print("\n4. ANGULAR MOMENTUM QUANTIZATION:")
        print(f"   Quantized: {'YES' if L_results['quantized'] else 'NO'}")
        print(f"   Final L: {L_results['L_mean']:.6f} ± {L_results['L_std']:.6f}")
        print(f"   Evidence: {L_results['evidence'].upper()}")

        print("\n5. ENERGY CONSERVATION:")
        if E_results['drift'] is not None:
            print(f"   Conserved: {'YES' if E_results['conserved'] else 'NO'}")
            print(f"   Drift: {E_results['drift']:.4f}%")
        else:
            print(f"   No data available")

        print("\n" + "="*70)
        print("OVERALL VERDICT:")
        print("="*70)

        # Count strong evidence
        strong_evidence = sum([
            shell_results['evidence'] == 'strong',
            energy_results['evidence'] == 'strong',
            velocity_results['evidence'] == 'strong',
            L_results['evidence'] == 'strong'
        ])

        if strong_evidence >= 2:
            print("\n*** QUANTIZATION HYPOTHESIS CONFIRMED ***")
            print(f"Found {strong_evidence}/4 strong signatures of quantization!")
            verdict = 'confirmed'
        elif strong_evidence >= 1:
            print("\n~~ QUANTIZATION HYPOTHESIS PARTIALLY CONFIRMED ~~")
            print(f"Found {strong_evidence}/4 strong signatures of quantization")
            verdict = 'partial'
        else:
            print("\nXXX QUANTIZATION HYPOTHESIS NOT CONFIRMED XXX")
            print("No strong evidence of discrete quantization found")
            verdict = 'rejected'

        print("="*70)

        return verdict

    def run_full_analysis(self):
        """Run all quantization tests."""
        print("\n" + "="*70)
        print("QUANTIZATION ANALYSIS - FULL SUITE")
        print("="*70)

        # Run all analyses
        shell_results = self.analyze_radial_shells()
        energy_results = self.analyze_energy_levels()
        velocity_results = self.analyze_velocity_distribution()
        L_results = self.analyze_angular_momentum()
        E_results = self.analyze_energy_conservation()

        # Generate summary
        verdict = self.generate_summary_report(
            shell_results, energy_results, velocity_results, L_results, E_results
        )

        # Package results
        analysis_results = {
            'verdict': verdict,
            'radial_shells': shell_results,
            'energy_levels': energy_results,
            'velocity_distribution': velocity_results,
            'angular_momentum': L_results,
            'energy_conservation': E_results
        }

        return analysis_results


def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


def main():
    """Main analysis script."""
    import sys

    # Load results
    results_file = Path("results/exp56a_v4_quantization_100k.json")

    if not results_file.exists():
        print(f"ERROR: Results file not found: {results_file}")
        print("Please run experiment_56a_v4_quantization.py first!")
        sys.exit(1)

    # Run analysis
    analyzer = QuantizationAnalyzer(results_file)
    analysis_results = analyzer.run_full_analysis()

    # Convert numpy types to Python types for JSON serialization
    analysis_results = convert_numpy_types(analysis_results)

    # Save analysis results
    output_file = Path("results/quantization_analysis_results.json")
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)

    print(f"\nAnalysis results saved to: {output_file}")

    # Return verdict
    verdict = analysis_results['verdict']
    sys.exit(0 if verdict in ['confirmed', 'partial'] else 1)


if __name__ == "__main__":
    main()
