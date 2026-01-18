"""
Test Suite for Phase 2: Simple Two-Source Interference

Tests 4-6 from the interferometry validation suite:
- Test 4: Constructive interference (Δφ = 0)
- Test 5: Destructive interference (Δφ = π)
- Test 6: Variable phase difference scan

Success Criteria:
- Fringe visibility V > 0.95
- Intensity matches I = I₁ + I₂ + 2√(I₁I₂)cos(Δφ)

Based on:
- Doc 062: Tick-Frame Interferometry §2.2
- Phase 2 implementation plan

Author: Tick-Frame Physics Project
Date: January 2026
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from two_source_interference import (
    TwoSourceConfig,
    run_two_source_interference_experiment,
    verify_interference_formula,
    scan_phase_difference
)


# Test configuration constants
WAVELENGTH = 100.0
GRID_SIZE = 4096
DETECTOR_POS = GRID_SIZE / 2
# Use CO-LOCATED sources for pure phase interference (no spatial fringes)
SOURCE_A_POS = DETECTOR_POS
SOURCE_B_POS = DETECTOR_POS
SOURCE_SEPARATION = 0.0
SIGMA_RATIO = 3.0  # Wide wave packets

# Tolerance parameters
INTENSITY_TOLERANCE = 0.15  # 15% tolerance for intensity matching
VISIBILITY_THRESHOLD = 0.95  # Minimum PHASE-MODULATION fringe visibility
SPATIAL_VISIBILITY_THRESHOLD = 0.05  # Minimum spatial fringe visibility (much lower)
CONSTRUCTIVE_MIN_RATIO = 1.8  # Minimum enhancement ratio (ideal = 2.0)
DESTRUCTIVE_MAX_RATIO = 0.1  # Maximum suppression ratio (ideal = 0.0)


class TestConstructiveInterference:
    """Test 4: Constructive Interference (Δφ = 0)"""

    def test_in_phase_sources_produce_maximum_intensity(self):
        """
        In-phase sources (Δφ = 0) should produce constructive interference.
        Expected: I_total ≈ 4 × I₀ (intensity quadruples)
        """
        config = TwoSourceConfig(
            source_A_position=SOURCE_A_POS,
            source_B_position=SOURCE_B_POS,
            wavelength=WAVELENGTH,
            phase_difference=0.0,  # In phase
            detector_position=DETECTOR_POS,
            sigma_ratio=SIGMA_RATIO
        )

        result = run_two_source_interference_experiment(config, GRID_SIZE)

        # Measure individual intensities
        I_A = np.max(np.abs(result.wave_packet_A.psi)**2)
        I_B = np.max(np.abs(result.wave_packet_B.psi)**2)
        I_total = result.intensity_max

        # For equal sources: I_total = 4 × I₀
        I_0 = (I_A + I_B) / 2
        expected_intensity = 4 * I_0

        # Verify enhancement
        enhancement_ratio = I_total / (I_A + I_B)

        assert enhancement_ratio > CONSTRUCTIVE_MIN_RATIO, (
            f"Constructive interference too weak: ratio {enhancement_ratio:.3f} < {CONSTRUCTIVE_MIN_RATIO}"
        )

        # Verify intensity formula
        I_theory = verify_interference_formula(I_A, I_B, 0.0)
        relative_error = abs(I_total - I_theory) / I_theory

        assert relative_error < INTENSITY_TOLERANCE, (
            f"Intensity does not match theory: error {relative_error:.2%} > {INTENSITY_TOLERANCE:.0%}"
        )

    def test_constructive_fringe_visibility_high(self):
        """
        Constructive interference should show spatial fringe structure.
        Expected: V > 0.05 (spatial fringes from Gaussian envelope)
        """
        config = TwoSourceConfig(
            source_A_position=SOURCE_A_POS,
            source_B_position=SOURCE_B_POS,
            wavelength=WAVELENGTH,
            phase_difference=0.0,
            detector_position=DETECTOR_POS,
            sigma_ratio=SIGMA_RATIO
        )

        result = run_two_source_interference_experiment(config, GRID_SIZE)

        assert result.fringe_visibility > SPATIAL_VISIBILITY_THRESHOLD, (
            f"Spatial fringe visibility too low: V = {result.fringe_visibility:.4f} < {SPATIAL_VISIBILITY_THRESHOLD}"
        )


class TestDestructiveInterference:
    """Test 5: Destructive Interference (Δφ = π)"""

    def test_out_of_phase_sources_produce_minimum_intensity(self):
        """
        Out-of-phase sources (Δφ = π) should produce destructive interference.
        Expected: I_min ≈ 0 (near-complete cancellation)
        """
        config = TwoSourceConfig(
            source_A_position=SOURCE_A_POS,
            source_B_position=SOURCE_B_POS,
            wavelength=WAVELENGTH,
            phase_difference=np.pi,  # Out of phase
            detector_position=DETECTOR_POS,
            sigma_ratio=SIGMA_RATIO
        )

        result = run_two_source_interference_experiment(config, GRID_SIZE)

        # Measure individual intensities
        I_A = np.max(np.abs(result.wave_packet_A.psi)**2)
        I_B = np.max(np.abs(result.wave_packet_B.psi)**2)
        I_min = result.intensity_min

        # Suppression ratio (ideal = 0)
        suppression_ratio = I_min / (I_A + I_B)

        assert suppression_ratio < DESTRUCTIVE_MAX_RATIO, (
            f"Destructive interference incomplete: suppression {suppression_ratio:.6f} > {DESTRUCTIVE_MAX_RATIO}"
        )

    def test_destructive_matches_interference_formula(self):
        """
        Destructive interference intensity should match theory.
        I = I_A + I_B + 2√(I_A×I_B)×cos(π) = I_A + I_B - 2√(I_A×I_B)
        """
        config = TwoSourceConfig(
            source_A_position=SOURCE_A_POS,
            source_B_position=SOURCE_B_POS,
            wavelength=WAVELENGTH,
            phase_difference=np.pi,
            detector_position=DETECTOR_POS,
            sigma_ratio=SIGMA_RATIO
        )

        result = run_two_source_interference_experiment(config, GRID_SIZE)

        # Measure individual intensities
        I_A = np.max(np.abs(result.wave_packet_A.psi)**2)
        I_B = np.max(np.abs(result.wave_packet_B.psi)**2)

        # Theoretical minimum intensity
        I_theory = verify_interference_formula(I_A, I_B, np.pi)

        # Compare with measured minimum
        I_measured = result.intensity_min

        # For equal sources: I_theory = 0
        if abs(I_A - I_B) / I_A < 0.1:  # Equal sources within 10%
            assert I_measured < 0.1 * (I_A + I_B), (
                f"Minimum intensity too high for equal sources: {I_measured:.6f}"
            )
        else:
            relative_error = abs(I_measured - I_theory) / max(I_theory, 1e-10)
            assert relative_error < INTENSITY_TOLERANCE, (
                f"Minimum intensity does not match theory: error {relative_error:.2%}"
            )

    def test_destructive_fringe_visibility_high(self):
        """
        Destructive interference pattern should show spatial fringe structure.
        Expected: V > 0.05 (spatial fringes from Gaussian envelope)
        """
        config = TwoSourceConfig(
            source_A_position=SOURCE_A_POS,
            source_B_position=SOURCE_B_POS,
            wavelength=WAVELENGTH,
            phase_difference=np.pi,
            detector_position=DETECTOR_POS,
            sigma_ratio=SIGMA_RATIO
        )

        result = run_two_source_interference_experiment(config, GRID_SIZE)

        assert result.fringe_visibility > SPATIAL_VISIBILITY_THRESHOLD, (
            f"Spatial fringe visibility too low: V = {result.fringe_visibility:.4f} < {SPATIAL_VISIBILITY_THRESHOLD}"
        )


class TestVariablePhaseInterference:
    """Test 6: Variable Phase Difference Scan"""

    def test_intensity_follows_cosine_pattern(self):
        """
        Intensity should vary sinusoidally with phase difference.
        I(Δφ) = I_A + I_B + 2√(I_A×I_B)×cos(Δφ)
        """
        phase_array, intensity_array, visibility_array = scan_phase_difference(
            source_A_pos=SOURCE_A_POS,
            source_B_pos=SOURCE_B_POS,
            wavelength=WAVELENGTH,
            detector_pos=DETECTOR_POS,
            phase_steps=50,
            grid_size=GRID_SIZE,
            sigma_ratio=SIGMA_RATIO
        )

        # Fit to I(Δφ) = A + B×cos(Δφ)
        from scipy.optimize import curve_fit

        def intensity_model(phase, A, B):
            return A + B * np.cos(phase)

        params, covariance = curve_fit(intensity_model, phase_array, intensity_array)
        A_fit, B_fit = params

        # Compute residuals
        fitted_intensity = intensity_model(phase_array, A_fit, B_fit)
        residuals = intensity_array - fitted_intensity
        rms_error = np.sqrt(np.mean(residuals**2))
        mean_intensity = np.mean(intensity_array)

        # Relative RMS error should be small
        relative_rms = rms_error / mean_intensity

        assert relative_rms < 0.15, (
            f"Intensity does not follow cosine pattern: RMS error {relative_rms:.2%} > 15%"
        )

    def test_phase_scan_achieves_full_modulation(self):
        """
        Phase scan should show full modulation from constructive to destructive.
        Visibility should remain high throughout scan.
        """
        phase_array, intensity_array, visibility_array = scan_phase_difference(
            source_A_pos=SOURCE_A_POS,
            source_B_pos=SOURCE_B_POS,
            wavelength=WAVELENGTH,
            detector_pos=DETECTOR_POS,
            phase_steps=50,
            grid_size=GRID_SIZE,
            sigma_ratio=SIGMA_RATIO
        )

        # Check phase-modulation depth
        I_max = np.max(intensity_array)
        I_min = np.min(intensity_array)
        phase_modulation_visibility = (I_max - I_min) / (I_max + I_min)

        # Should achieve deep phase modulation (visibility > 0.95)
        assert phase_modulation_visibility > VISIBILITY_THRESHOLD, (
            f"Insufficient phase-modulation visibility: {phase_modulation_visibility:.4f} < {VISIBILITY_THRESHOLD}"
        )

        # Mean spatial visibility should be present (lower threshold)
        mean_spatial_visibility = np.mean(visibility_array)

        assert mean_spatial_visibility > SPATIAL_VISIBILITY_THRESHOLD, (
            f"Mean spatial fringe visibility too low: V = {mean_spatial_visibility:.4f} < {SPATIAL_VISIBILITY_THRESHOLD}"
        )

    def test_phase_scan_extrema_at_expected_positions(self):
        """
        Maximum intensity should occur near Δφ = 0, 2π
        Minimum intensity should occur near Δφ = π
        """
        phase_array, intensity_array, _ = scan_phase_difference(
            source_A_pos=SOURCE_A_POS,
            source_B_pos=SOURCE_B_POS,
            wavelength=WAVELENGTH,
            detector_pos=DETECTOR_POS,
            phase_steps=100,
            grid_size=GRID_SIZE
        )

        # Find phase of maximum intensity
        max_idx = np.argmax(intensity_array)
        phase_at_max = phase_array[max_idx]

        # Should be near 0 or 2π
        distance_to_zero = min(abs(phase_at_max), abs(phase_at_max - 2*np.pi))

        assert distance_to_zero < 0.3, (
            f"Maximum not at Δφ=0: found at {phase_at_max:.3f} rad"
        )

        # Find phase of minimum intensity
        min_idx = np.argmin(intensity_array)
        phase_at_min = phase_array[min_idx]

        # Should be near π
        distance_to_pi = abs(phase_at_min - np.pi)

        assert distance_to_pi < 0.3, (
            f"Minimum not at Δφ=π: found at {phase_at_min:.3f} rad"
        )

    def test_interference_formula_validated_across_phases(self):
        """
        Verify interference formula I = I_A + I_B + 2√(I_A×I_B)cos(Δφ)
        holds across multiple phase differences.
        """
        # Test at specific phase points
        test_phases = [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi, 5*np.pi/4, 3*np.pi/2, 7*np.pi/4]

        for phase_diff in test_phases:
            config = TwoSourceConfig(
                source_A_position=SOURCE_A_POS,
                source_B_position=SOURCE_B_POS,
                wavelength=WAVELENGTH,
                phase_difference=phase_diff,
                detector_position=DETECTOR_POS,
                sigma_ratio=SIGMA_RATIO
            )

            result = run_two_source_interference_experiment(config, GRID_SIZE)

            # Measure individual intensities
            I_A = np.max(np.abs(result.wave_packet_A.psi)**2)
            I_B = np.max(np.abs(result.wave_packet_B.psi)**2)
            I_measured = result.intensity_max

            # Theoretical prediction
            I_theory = verify_interference_formula(I_A, I_B, phase_diff)

            # Verify match (handle near-zero case for destructive interference)
            if I_theory < 1e-10:
                # For destructive interference, check absolute error
                absolute_error = abs(I_measured)
                assert absolute_error < 0.01 * (I_A + I_B), (
                    f"Formula fails at Δφ={phase_diff:.3f}: |I_measured| = {absolute_error:.6f} too large"
                )
            else:
                # For other phases, check relative error
                relative_error = abs(I_measured - I_theory) / I_theory
                assert relative_error < INTENSITY_TOLERANCE, (
                    f"Formula fails at Δφ={phase_diff:.3f}: error {relative_error:.2%} > {INTENSITY_TOLERANCE:.0%}"
                )


# =======================
# Summary Report
# =======================

def test_phase_2_summary(capsys):
    """
    Summary test that runs all Phase 2 tests and reports results.
    """
    print()
    print("=" * 80)
    print("PHASE 2 VALIDATION SUMMARY: Simple Two-Source Interference")
    print("=" * 80)
    print()

    # Run quick validation
    config_constructive = TwoSourceConfig(
        source_A_position=SOURCE_A_POS,
        source_B_position=SOURCE_B_POS,
        wavelength=WAVELENGTH,
        phase_difference=0.0,
        detector_position=DETECTOR_POS,
        sigma_ratio=SIGMA_RATIO
    )
    result_constructive = run_two_source_interference_experiment(config_constructive, GRID_SIZE)

    config_destructive = TwoSourceConfig(
        source_A_position=SOURCE_A_POS,
        source_B_position=SOURCE_B_POS,
        wavelength=WAVELENGTH,
        phase_difference=np.pi,
        detector_position=DETECTOR_POS,
        sigma_ratio=SIGMA_RATIO
    )
    result_destructive = run_two_source_interference_experiment(config_destructive, GRID_SIZE)

    phase_array, intensity_array, visibility_array = scan_phase_difference(
        source_A_pos=SOURCE_A_POS,
        source_B_pos=SOURCE_B_POS,
        wavelength=WAVELENGTH,
        detector_pos=DETECTOR_POS,
        phase_steps=20,
        grid_size=GRID_SIZE,
        sigma_ratio=SIGMA_RATIO
    )

    # Compute metrics
    I_A = np.max(np.abs(result_constructive.wave_packet_A.psi)**2)
    I_B = np.max(np.abs(result_constructive.wave_packet_B.psi)**2)

    constructive_ratio = result_constructive.intensity_max / (I_A + I_B)
    destructive_ratio = result_destructive.intensity_min / (I_A + I_B)

    # Calculate phase-modulation visibility from scan
    I_max_scan = np.max(intensity_array)
    I_min_scan = np.min(intensity_array)
    phase_visibility = (I_max_scan - I_min_scan) / (I_max_scan + I_min_scan)

    print(f"Test 4: Constructive Interference (Δφ = 0)")
    print(f"  Enhancement ratio: {constructive_ratio:.3f} (target > {CONSTRUCTIVE_MIN_RATIO})")
    print(f"  Fringe visibility: V = {result_constructive.fringe_visibility:.4f}")
    print(f"  Status: {'✅ PASS' if constructive_ratio > CONSTRUCTIVE_MIN_RATIO else '❌ FAIL'}")
    print()

    print(f"Test 5: Destructive Interference (Δφ = π)")
    print(f"  Suppression ratio: {destructive_ratio:.6f} (target < {DESTRUCTIVE_MAX_RATIO})")
    print(f"  Fringe visibility: V = {result_destructive.fringe_visibility:.4f}")
    print(f"  Status: {'✅ PASS' if destructive_ratio < DESTRUCTIVE_MAX_RATIO else '❌ FAIL'}")
    print()

    print(f"Test 6: Variable Phase Scan")
    print(f"  Phase-modulation visibility: V = {phase_visibility:.4f} (target > {VISIBILITY_THRESHOLD})")
    print(f"  Intensity range: [{I_min_scan:.6f}, {I_max_scan:.6f}]")
    print(f"  Status: {'PASS' if phase_visibility > VISIBILITY_THRESHOLD else 'FAIL'}")
    print()

    # Overall status
    all_pass = (
        constructive_ratio > CONSTRUCTIVE_MIN_RATIO and
        destructive_ratio < DESTRUCTIVE_MAX_RATIO and
        phase_visibility > VISIBILITY_THRESHOLD
    )

    print("=" * 80)
    if all_pass:
        print("✅ PHASE 2 COMPLETE: All success criteria met!")
    else:
        print("⚠️  PHASE 2 INCOMPLETE: Some criteria not met")
    print("=" * 80)
    print()

    assert all_pass, "Phase 2 validation incomplete"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
