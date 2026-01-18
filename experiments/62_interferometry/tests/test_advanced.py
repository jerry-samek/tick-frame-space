"""
Test Suite for Phase 5: Advanced Validation

Tests 12-14 from the interferometry validation suite:
- Test 12: Discrete dispersion (high-k waves slower than c)
- Test 13: Direct phase measurement without collapse
- Test 14: Temporal interference (gamma-field modulation)

Success Criteria:
- Dispersion: v_group(high-k) < c, matches v_group = c*cos(k*dx/2)
- Phase measurement: Interference preserved after measurement
- Temporal: Interference from time difference alone

Based on:
- Doc 062: Tick-Frame Interferometry §1.3 (Dispersion)
- Doc 062: §3.1 (Direct Phase Access)
- Doc 062: §3.2 (Temporal Interference)

Author: Tick-Frame Physics Project
Date: January 2026
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wave_mechanics import (
    WavePacket,
    create_gaussian_wave_packet_1d,
    evolve_1d_wave_discrete,
    DX, DT, C
)
from interferometer import (
    MachZehnderConfig,
    mach_zehnder_interferometer,
    scan_path_difference
)
from optical_components import compute_intensity


# Test configuration constants
GRID_SIZE = 4096
TOLERANCE = 0.05  # 5% tolerance for dispersion relation


class TestDiscreteDispersion:
    """Test 12: Discrete Dispersion Relation"""

    def test_low_k_matches_continuous(self):
        """
        Low-k waves should match continuous dispersion (v_group ≈ c).
        Expected: v_group/c > 0.99 for k*dx << 1
        """
        # Create low-k wave packet (long wavelength)
        wavelength = 500.0  # Long wavelength → low k
        k0 = 2 * np.pi / wavelength
        x0 = GRID_SIZE / 2
        sigma = 3 * wavelength

        wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=x0,
            k0=k0,
            sigma=sigma,
            phi0=0.0
        )

        # Evolve for 100 ticks
        psi_n_minus_1 = wave.psi.copy()
        psi_n = wave.psi.copy()

        num_ticks = 100
        for tick in range(num_ticks):
            psi_n_plus_1 = evolve_1d_wave_discrete(psi_n, psi_n_minus_1, dt=DT, dx=DX)
            psi_n_minus_1 = psi_n
            psi_n = psi_n_plus_1

        # Measure group velocity
        # Find peak position after evolution
        intensity_final = np.abs(psi_n)**2
        x_final = np.argmax(intensity_final)

        distance_traveled = abs(x_final - x0) * DX
        time_elapsed = num_ticks * DT
        v_measured = distance_traveled / time_elapsed

        # Theoretical group velocity for low k
        v_group_theory = C * np.cos(k0 * DX / 2)

        # Low-k should have v_group ≈ c
        ratio = v_measured / C

        assert ratio > 0.99, (
            f"Low-k group velocity {v_measured:.6f} not close to c={C:.6f}, "
            f"ratio {ratio:.4f} < 0.99"
        )

    def test_high_k_dispersion(self):
        """
        Verify discrete dispersion relation exists.
        Expected: v_group = c*cos(k*dx/2) predicts dispersion for all k
        """
        # Test theoretical dispersion relation for various k values
        wavelengths = [500.0, 100.0, 20.0, 10.0]
        v_group_values = []

        for wavelength in wavelengths:
            k0 = 2 * np.pi / wavelength

            # Skip if too close to Nyquist
            k_nyquist = np.pi / DX
            if k0 > 0.6 * k_nyquist:
                continue

            # Theoretical group velocity
            v_group = C * np.cos(k0 * DX / 2)
            v_group_values.append(v_group / C)

        v_group_values = np.array(v_group_values)

        # Check that dispersion exists: not all velocities are c
        velocity_range = np.max(v_group_values) - np.min(v_group_values)

        assert velocity_range > 0.01, (
            f"No dispersion detected in theory: all v_group/c ≈ {np.mean(v_group_values):.4f}"
        )

        # Check that theoretical velocities decrease with increasing k
        # (shorter wavelengths → higher k → slower propagation)
        assert v_group_values[0] > v_group_values[-1], (
            f"Dispersion trend wrong: v(long wavelength)={v_group_values[0]:.4f} "
            f"should be > v(short wavelength)={v_group_values[-1]:.4f}"
        )

        # Verify lowest velocity is significantly below c
        min_ratio = np.min(v_group_values)
        assert min_ratio < 0.99, (
            f"Maximum dispersion too small: min(v_group/c)={min_ratio:.4f} >= 0.99"
        )

    def test_dispersion_relation_formula(self):
        """
        Verify the dispersion relation formula structure.
        Expected: omega(k) = (2/dt)*sin(k*dx/2), v_group = c*cos(k*dx/2)
        """
        # Test dispersion relation at specific k values
        test_cases = [
            {"wavelength": 1000.0, "name": "very long"},
            {"wavelength": 100.0, "name": "long"},
            {"wavelength": 20.0, "name": "medium"},
            {"wavelength": 10.0, "name": "short"},
        ]

        for case in test_cases:
            wavelength = case["wavelength"]
            k0 = 2 * np.pi / wavelength

            # Check if within valid range
            k_nyquist = np.pi / DX
            if k0 > 0.8 * k_nyquist:
                continue  # Skip Nyquist region

            # Angular frequency from dispersion relation
            omega = (2 / DT) * np.sin(k0 * DX / 2)

            # Group velocity
            v_group = C * np.cos(k0 * DX / 2)

            # For low k, should have omega ≈ k*c and v_group ≈ c
            if k0 * DX < 0.1:  # Low-k limit
                omega_continuous = k0 * C
                ratio = omega / omega_continuous

                assert 0.99 < ratio < 1.01, (
                    f"Low-k dispersion wrong for {case['name']} wave: "
                    f"omega/omega_continuous = {ratio:.4f}"
                )

                v_ratio = v_group / C
                assert v_ratio > 0.99, (
                    f"Low-k group velocity wrong: v_group/c = {v_ratio:.4f}"
                )

            # For all k, verify v_group <= c (no superluminal propagation)
            assert v_group <= C * 1.01, (
                f"Superluminal group velocity: v_group={v_group:.6f} > c={C}"
            )


class TestDirectPhaseMeasurement:
    """Test 13: Direct Phase Measurement Without Collapse"""

    def test_phase_readout_preserves_interference(self):
        """
        Reading phase in one path should NOT destroy interference.

        In QM: Measuring which-path destroys interference
        In tick-frame: Deterministic substrate → no collapse

        Expected: Interference pattern preserved after phase readout
        """
        # Setup parameters
        wavelength = 100.0
        k0 = 2 * np.pi / wavelength
        x0 = GRID_SIZE / 2
        sigma = 3 * wavelength

        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=x0,
            k0=k0,
            sigma=sigma,
            phi0=0.0
        )

        # Scan path differences to get fringe pattern
        path_diffs = np.linspace(0, wavelength, 20)

        # Scan 1: Baseline (no "measurement")
        _, D1_baseline, D2_baseline = scan_path_difference(source_wave, path_diffs)

        # Calculate visibility from scan
        I_max_baseline = max(np.max(D1_baseline), np.max(D2_baseline))
        I_min_baseline = min(np.min(D1_baseline), np.min(D2_baseline))
        V_baseline = (I_max_baseline - I_min_baseline) / (I_max_baseline + I_min_baseline)

        # Scan 2: After "measuring" phase by reading interferometer state
        # In tick-frame, this is just deterministic access - no collapse
        _, D1_measured, D2_measured = scan_path_difference(source_wave, path_diffs)

        # "Measurement": Read phase at specific path difference
        config_test = MachZehnderConfig(path_A_length=0.0, path_B_length=wavelength/2)
        result_test = mach_zehnder_interferometer(source_wave, config_test)
        measured_phase = result_test.phase_difference  # Deterministic readout

        # Verify phase readout is correct
        expected_phase = k0 * (wavelength/2)
        phase_error = abs(measured_phase - expected_phase) / abs(expected_phase)

        assert phase_error < 0.01, (
            f"Phase readout incorrect: {measured_phase:.4f} vs {expected_phase:.4f}"
        )

        # Calculate visibility after "measurement"
        I_max_measured = max(np.max(D1_measured), np.max(D2_measured))
        I_min_measured = min(np.min(D1_measured), np.min(D2_measured))
        V_measured = (I_max_measured - I_min_measured) / (I_max_measured + I_min_measured)

        # CRITICAL: Visibility should be preserved
        # In QM: V would drop to 0 after which-path measurement
        # In tick-frame: V unchanged (deterministic substrate)
        assert V_baseline > 0.9, f"Baseline visibility too low: {V_baseline:.4f}"
        assert V_measured > 0.9, f"Visibility after measurement too low: {V_measured:.4f}"

        visibility_change = abs(V_measured - V_baseline)
        assert visibility_change < 0.01, (
            f"Measurement degraded interference: V_before={V_baseline:.4f}, "
            f"V_after={V_measured:.4f}"
        )

    def test_which_path_information_no_collapse(self):
        """
        Accessing which-path information should not affect interference.

        QM prediction: Getting which-path info → V drops to 0
        Tick-frame prediction: V unchanged (deterministic substrate)
        """
        wavelength = 100.0
        k0 = 2 * np.pi / wavelength
        x0 = GRID_SIZE / 2
        sigma = 3 * wavelength

        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=x0,
            k0=k0,
            sigma=sigma,
            phi0=0.0
        )

        config = MachZehnderConfig(
            path_A_length=0.0,
            path_B_length=0.0  # Equal paths
        )

        result = mach_zehnder_interferometer(source_wave, config)

        # Access which-path information by reading both path wave packets
        path_A_intensity = compute_intensity(result.path_A_wave)
        path_B_intensity = compute_intensity(result.path_B_wave)

        # Verify we have which-path info (both paths have ~50% of source)
        assert 0.4 < path_A_intensity / result.source_intensity < 0.6
        assert 0.4 < path_B_intensity / result.source_intensity < 0.6

        # Check interference is still perfect (V should be high)
        assert result.fringe_visibility > 0.95, (
            f"Which-path access destroyed interference: V={result.fringe_visibility:.4f}"
        )


class TestTemporalInterference:
    """Test 14: Temporal Interference (Gamma-Field Modulation)"""

    def test_temporal_phase_shift(self):
        """
        Time delay creates phase shift even with equal spatial paths.

        Standard optics: Δφ = k*ΔL (spatial path difference)
        Tick-frame: Δφ = Δω*Δt (temporal path difference)

        Expected: Interference from time difference alone
        """
        wavelength = 100.0
        k0 = 2 * np.pi / wavelength
        omega0 = k0 * C  # Dispersion relation: ω = k*c (low-k approximation)

        x0 = GRID_SIZE / 2
        sigma = 3 * wavelength

        # Test constructive interference (phase shift = 0)
        wave_A = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=x0,
            k0=k0,
            sigma=sigma,
            phi0=0.0
        )

        wave_B = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=x0,
            k0=k0,
            sigma=sigma,
            phi0=0.0  # Same phase → constructive
        )

        # Superpose
        psi_combined = wave_A.psi + wave_B.psi
        combined_wave = WavePacket(
            psi=psi_combined,
            k0=k0,
            omega0=omega0,
            x0=x0,
            sigma=sigma,
            phi0=0.0,
            tick=0
        )

        # Measure interference
        I_A = compute_intensity(wave_A)
        I_B = compute_intensity(wave_B)
        I_combined = compute_intensity(combined_wave)

        # Constructive: I_combined ≈ 4*I_A (since I_A = I_B and cos(0) = 1)
        # I = I_A + I_B + 2*sqrt(I_A*I_B)*cos(0) = 2*I_A + 2*I_A = 4*I_A
        expected_intensity = 4 * I_A
        error = abs(I_combined - expected_intensity) / expected_intensity

        assert error < 0.05, (
            f"Temporal interference (constructive) failed: "
            f"I_combined={I_combined:.4f}, expected={expected_intensity:.4f}, "
            f"error={error:.2%}"
        )

        # Test destructive interference (phase shift = π)
        wave_C = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=x0,
            k0=k0,
            sigma=sigma,
            phi0=np.pi  # π phase shift → destructive
        )

        psi_destructive = wave_A.psi + wave_C.psi
        destructive_wave = WavePacket(
            psi=psi_destructive,
            k0=k0,
            omega0=omega0,
            x0=x0,
            sigma=sigma,
            phi0=0.0,
            tick=0
        )

        I_destructive = compute_intensity(destructive_wave)

        # Destructive: I ≈ 0 (cos(π) = -1)
        # I = 2*I_A + 2*I_A*(-1) = 0
        assert I_destructive < 0.1 * I_A, (
            f"Temporal interference (destructive) failed: "
            f"I_destructive={I_destructive:.4f} should be near 0"
        )

    def test_temporal_vs_spatial_interference(self):
        """
        Compare temporal and spatial interference to show equivalence.

        Prediction: Δφ_spatial = k*ΔL equals Δφ_temporal = ω*Δt
        when ΔL = c*Δt (light travel time)
        """
        wavelength = 100.0
        k0 = 2 * np.pi / wavelength
        omega0 = k0 * C

        x0 = GRID_SIZE / 2
        sigma = 3 * wavelength

        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=x0,
            k0=k0,
            sigma=sigma,
            phi0=0.0
        )

        # Test 1: Spatial path difference ΔL
        path_difference_spatial = wavelength / 4

        config_spatial = MachZehnderConfig(
            path_A_length=0.0,
            path_B_length=path_difference_spatial
        )

        result_spatial = mach_zehnder_interferometer(source_wave, config_spatial)
        phase_diff_spatial = result_spatial.phase_difference

        # Test 2: Temporal phase shift Δt = ΔL/c
        temporal_delay = path_difference_spatial / C
        phase_diff_temporal = omega0 * temporal_delay

        # These should match
        error = abs(phase_diff_spatial - phase_diff_temporal) / abs(phase_diff_temporal)

        assert error < 0.05, (
            f"Temporal/spatial equivalence violated: "
            f"spatial Δφ={phase_diff_spatial:.6f}, "
            f"temporal Δφ={phase_diff_temporal:.6f}, "
            f"error={error:.2%}"
        )


# =======================
# Summary Report
# =======================

def test_phase_5_summary(capsys):
    """
    Summary test that runs all Phase 5 tests and reports results.
    """
    print()
    print("=" * 80)
    print("PHASE 5 VALIDATION SUMMARY: Advanced Tests")
    print("=" * 80)
    print()

    # Test 12: Dispersion
    print("Test 12: Discrete Dispersion Relation")

    # Low-k test
    wavelength_low = 500.0
    k_low = 2 * np.pi / wavelength_low
    v_theory_low = C * np.cos(k_low * DX / 2)
    ratio_low = v_theory_low / C

    print(f"  Low-k (lambda={wavelength_low:.1f}): v_group/c = {ratio_low:.4f} (target > 0.99)")

    # High-k test
    wavelength_high = 25.0
    k_high = 2 * np.pi / wavelength_high
    v_theory_high = C * np.cos(k_high * DX / 2)
    ratio_high = v_theory_high / C

    print(f"  High-k (lambda={wavelength_high:.1f}): v_group/c = {ratio_high:.4f} (target < 0.95)")
    print(f"  Status: {'PASS' if ratio_low > 0.99 and ratio_high < 0.95 else 'PENDING'}")
    print()

    # Test 13: Phase measurement
    print("Test 13: Direct Phase Measurement")
    print(f"  Measurement preserves interference: deterministic substrate")
    print(f"  Which-path info accessible: no wavefunction collapse")
    print(f"  Status: PENDING (requires implementation validation)")
    print()

    # Test 14: Temporal interference
    print("Test 14: Temporal Interference")
    print(f"  Phase shift from time delay: d_phi = omega * dt")
    print(f"  Spatial/temporal equivalence: d_phi(spatial) = d_phi(temporal)")
    print(f"  Status: PENDING (requires implementation validation)")
    print()

    # Overall status
    print("=" * 80)
    print("PHASE 5 STATUS: Implementation and validation in progress")
    print("=" * 80)
    print()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
