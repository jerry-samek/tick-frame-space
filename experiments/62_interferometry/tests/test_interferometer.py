"""
Test Suite for Phase 4: Mach-Zehnder Interferometer

Tests 9-11 from the interferometry validation suite:
- Test 9: Equal paths (constructive interference)
- Test 10: lambda/2 path difference (destructive interference)
- Test 11: Path difference scan (fringe visibility > 0.9)

Success Criteria:
- Equal paths: Constructive at one detector
- lambda/2 difference: Destructive at one detector
- Fringe visibility V > 0.9
- Energy conservation: I_D1 + I_D2 = I_source within 1%

Based on:
- Doc 062: Tick-Frame Interferometry §2.4
- Phase 4 implementation plan

Author: Tick-Frame Physics Project
Date: January 2026
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from interferometer import (
    MachZehnderConfig,
    mach_zehnder_interferometer,
    scan_path_difference
)
from wave_mechanics import create_gaussian_wave_packet_1d


# Test configuration constants
WAVELENGTH = 100.0
GRID_SIZE = 4096
X0 = GRID_SIZE / 2
SIGMA = 3 * WAVELENGTH
K0 = 2 * np.pi / WAVELENGTH

# Tolerance parameters
ENERGY_CONSERVATION_TOLERANCE = 0.01  # 1% error tolerance
VISIBILITY_THRESHOLD = 0.9  # Minimum fringe visibility
FRINGE_PERIOD_TOLERANCE = 0.02  # 2% tolerance for fringe period


class TestMachZehnderEqualPaths:
    """Test 9: Equal Paths (Constructive)"""

    def test_equal_paths_constructive_interference(self):
        """
        Equal path lengths should produce constructive interference at one detector.
        Expected: All energy to one detector (perfect constructive)
        """
        # Create source wave
        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        # Equal paths configuration
        config = MachZehnderConfig(
            path_A_length=0.0,
            path_B_length=0.0
        )

        result = mach_zehnder_interferometer(source_wave, config)

        # Verify constructive interference (one detector gets all energy)
        max_detector = max(result.detector_1_intensity, result.detector_2_intensity)
        min_detector = min(result.detector_1_intensity, result.detector_2_intensity)

        # Most energy should go to one detector
        assert max_detector > 0.9 * result.source_intensity, (
            f"Constructive interference incomplete: max detector = {max_detector:.4f}, "
            f"expected > {0.9 * result.source_intensity:.4f}"
        )

        # Other detector should have minimal energy
        assert min_detector < 0.1 * result.source_intensity, (
            f"Destructive interference incomplete: min detector = {min_detector:.4f}, "
            f"expected < {0.1 * result.source_intensity:.4f}"
        )

    def test_equal_paths_energy_conservation(self):
        """
        Energy must be conserved: I_D1 + I_D2 = I_source
        """
        # Create source wave
        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        config = MachZehnderConfig(
            path_A_length=0.0,
            path_B_length=0.0
        )

        result = mach_zehnder_interferometer(source_wave, config)

        # Verify energy conservation
        assert result.energy_conservation_error < ENERGY_CONSERVATION_TOLERANCE, (
            f"Energy not conserved: error {result.energy_conservation_error:.4%} > "
            f"{ENERGY_CONSERVATION_TOLERANCE:.0%}"
        )

    def test_equal_paths_phase_difference(self):
        """
        Equal paths should produce zero phase difference.
        Expected: d_phi = 0
        """
        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        config = MachZehnderConfig(
            path_A_length=0.0,
            path_B_length=0.0
        )

        result = mach_zehnder_interferometer(source_wave, config)

        # Check phase difference
        assert abs(result.phase_difference) < 0.01, (
            f"Phase difference not zero: d_phi = {result.phase_difference:.6f}"
        )


class TestMachZehnderHalfWavelength:
    """Test 10: lambda/2 Path Difference (Destructive)"""

    def test_half_wavelength_destructive_interference(self):
        """
        lambda/2 path difference should produce destructive interference.
        Expected: Energy distribution flipped compared to equal paths
        """
        # Create source wave
        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        # lambda/2 path difference
        config = MachZehnderConfig(
            path_A_length=0.0,
            path_B_length=WAVELENGTH / 2
        )

        result = mach_zehnder_interferometer(source_wave, config)

        # Verify destructive interference (energy flips to other detector)
        max_detector = max(result.detector_1_intensity, result.detector_2_intensity)
        min_detector = min(result.detector_1_intensity, result.detector_2_intensity)

        # Most energy should go to one detector
        assert max_detector > 0.9 * result.source_intensity, (
            f"Constructive interference incomplete: max detector = {max_detector:.4f}"
        )

        # Other detector should have minimal energy
        assert min_detector < 0.1 * result.source_intensity, (
            f"Destructive interference incomplete: min detector = {min_detector:.4f}"
        )

    def test_half_wavelength_phase_difference(self):
        """
        lambda/2 path difference should produce pi phase difference.
        Expected: d_phi = pi
        """
        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        config = MachZehnderConfig(
            path_A_length=0.0,
            path_B_length=WAVELENGTH / 2
        )

        result = mach_zehnder_interferometer(source_wave, config)

        # Check phase difference (should be pi)
        expected_phase = np.pi
        assert abs(result.phase_difference - expected_phase) < 0.1, (
            f"Phase difference not pi: d_phi = {result.phase_difference:.6f}, "
            f"expected {expected_phase:.6f}"
        )

    def test_half_wavelength_energy_conservation(self):
        """
        Energy must be conserved even with lambda/2 path difference.
        """
        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        config = MachZehnderConfig(
            path_A_length=0.0,
            path_B_length=WAVELENGTH / 2
        )

        result = mach_zehnder_interferometer(source_wave, config)

        # Verify energy conservation
        assert result.energy_conservation_error < ENERGY_CONSERVATION_TOLERANCE, (
            f"Energy not conserved: error {result.energy_conservation_error:.4%}"
        )


class TestMachZehnderPathScan:
    """Test 11: Path Difference Scan (Fringe Visibility)"""

    def test_path_scan_produces_fringes(self):
        """
        Scanning path difference should produce interference fringes.
        Expected: Periodic intensity variation with path difference
        """
        # Create source wave
        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        # Scan path differences from 0 to 2*wavelength
        path_diffs = np.linspace(0, 2 * WAVELENGTH, 50)
        path_array, D1_array, D2_array = scan_path_difference(source_wave, path_diffs)

        # Check that intensities vary (not constant)
        D1_variation = np.std(D1_array)
        D2_variation = np.std(D2_array)

        assert D1_variation > 0.1, (
            f"D1 intensity does not vary: std = {D1_variation:.6f}"
        )

        assert D2_variation > 0.1, (
            f"D2 intensity does not vary: std = {D2_variation:.6f}"
        )

    def test_path_scan_high_visibility(self):
        """
        Path scan should produce high fringe visibility.
        Expected: V > 0.9
        """
        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        # Scan path differences
        path_diffs = np.linspace(0, 2 * WAVELENGTH, 50)
        path_array, D1_array, D2_array = scan_path_difference(source_wave, path_diffs)

        # Calculate visibility from scan
        I_max = max(np.max(D1_array), np.max(D2_array))
        I_min = min(np.min(D1_array), np.min(D2_array))
        visibility = (I_max - I_min) / (I_max + I_min)

        assert visibility > VISIBILITY_THRESHOLD, (
            f"Fringe visibility too low: V = {visibility:.4f} < {VISIBILITY_THRESHOLD}"
        )

    def test_path_scan_fringe_period(self):
        """
        Fringe period should match wavelength.
        Expected: One complete fringe per wavelength path difference
        """
        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        # Scan path differences over 2 wavelengths
        path_diffs = np.linspace(0, 2 * WAVELENGTH, 100)
        path_array, D1_array, D2_array = scan_path_difference(source_wave, path_diffs)

        # Count peaks in D1
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(D1_array, height=np.mean(D1_array))
        fringe_count = len(peaks)

        # Expected: ~2 fringes in 2*wavelength scan
        expected_fringes = 2
        error = abs(fringe_count - expected_fringes) / expected_fringes

        assert error < FRINGE_PERIOD_TOLERANCE, (
            f"Fringe count wrong: detected {fringe_count}, expected {expected_fringes}, "
            f"error {error:.2%}"
        )

    def test_path_scan_energy_conservation_throughout(self):
        """
        Energy should be conserved at all path differences.
        Expected: I_D1 + I_D2 = I_source at every point
        """
        source_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        I_source = np.sum(np.abs(source_wave.psi)**2)

        # Scan path differences
        path_diffs = np.linspace(0, WAVELENGTH, 20)
        path_array, D1_array, D2_array = scan_path_difference(source_wave, path_diffs)

        # Check energy conservation at each point
        total_array = D1_array + D2_array
        errors = np.abs(total_array - I_source) / I_source

        max_error = np.max(errors)

        assert max_error < ENERGY_CONSERVATION_TOLERANCE, (
            f"Energy not conserved throughout scan: max error {max_error:.4%}"
        )


# =======================
# Summary Report
# =======================

def test_phase_4_summary(capsys):
    """
    Summary test that runs all Phase 4 tests and reports results.
    """
    print()
    print("=" * 80)
    print("PHASE 4 VALIDATION SUMMARY: Mach-Zehnder Interferometer")
    print("=" * 80)
    print()

    # Create source wave
    source_wave = create_gaussian_wave_packet_1d(
        grid_size=GRID_SIZE,
        x0=X0,
        k0=K0,
        sigma=SIGMA,
        phi0=0.0
    )

    # Test equal paths
    config_equal = MachZehnderConfig(path_A_length=0.0, path_B_length=0.0)
    result_equal = mach_zehnder_interferometer(source_wave, config_equal)

    # Test lambda/2 difference
    config_half = MachZehnderConfig(path_A_length=0.0, path_B_length=WAVELENGTH/2)
    result_half = mach_zehnder_interferometer(source_wave, config_half)

    # Test path scan
    path_diffs = np.linspace(0, 2 * WAVELENGTH, 50)
    path_array, D1_array, D2_array = scan_path_difference(source_wave, path_diffs)

    I_max_scan = max(np.max(D1_array), np.max(D2_array))
    I_min_scan = min(np.min(D1_array), np.min(D2_array))
    visibility_scan = (I_max_scan - I_min_scan) / (I_max_scan + I_min_scan)

    print(f"Test 9: Equal Paths")
    print(f"  D1: {result_equal.detector_1_intensity:.4f}, D2: {result_equal.detector_2_intensity:.4f}")
    print(f"  Visibility: V = {result_equal.fringe_visibility:.4f}")
    print(f"  Energy error: {result_equal.energy_conservation_error:.4%}")
    print(f"  Status: {'PASS' if result_equal.energy_conservation_error < 0.01 else 'FAIL'}")
    print()

    print(f"Test 10: lambda/2 Path Difference")
    print(f"  D1: {result_half.detector_1_intensity:.4f}, D2: {result_half.detector_2_intensity:.4f}")
    print(f"  Phase difference: {result_half.phase_difference:.4f} rad (pi = {np.pi:.4f})")
    print(f"  Visibility: V = {result_half.fringe_visibility:.4f}")
    print(f"  Status: {'PASS' if abs(result_half.phase_difference - np.pi) < 0.1 else 'FAIL'}")
    print()

    print(f"Test 11: Path Difference Scan")
    print(f"  Visibility: V = {visibility_scan:.4f} (target > {VISIBILITY_THRESHOLD})")
    print(f"  Intensity range: [{I_min_scan:.4f}, {I_max_scan:.4f}]")
    print(f"  Status: {'PASS' if visibility_scan > VISIBILITY_THRESHOLD else 'FAIL'}")
    print()

    # Overall status
    all_pass = (
        result_equal.energy_conservation_error < 0.01 and
        abs(result_half.phase_difference - np.pi) < 0.1 and
        visibility_scan > VISIBILITY_THRESHOLD
    )

    print("=" * 80)
    if all_pass:
        print("PHASE 4 COMPLETE: Mach-Zehnder interferometer validated!")
    else:
        print("PHASE 4 INCOMPLETE: Some tests failed")
    print("=" * 80)
    print()

    assert all_pass, "Phase 4 validation incomplete"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
