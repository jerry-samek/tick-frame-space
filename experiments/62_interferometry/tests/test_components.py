"""
Test Suite for Phase 3: Optical Components

Tests 7-8 from the interferometry validation suite:
- Test 7: Beam splitter (50/50 split, T+R=1)
- Test 8: Mirror (elastic reflection, phase preserved)

Success Criteria:
- Beam splitter: T + R = 1 within 1% error
- Mirror: R = 1 within 1% error, direction reversed

Based on:
- Doc 062: Tick-Frame Interferometry §2.3
- Phase 3 implementation plan

Author: Tick-Frame Physics Project
Date: January 2026
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from optical_components import (
    BeamSplitterConfig,
    MirrorConfig,
    beam_splitter_50_50,
    mirror_reflect,
    verify_beam_splitter_energy_conservation,
    verify_mirror_energy_conservation,
    compute_intensity
)
from wave_mechanics import create_gaussian_wave_packet_1d


# Test configuration constants
WAVELENGTH = 100.0
GRID_SIZE = 4096
X0 = GRID_SIZE / 2
SIGMA = WAVELENGTH
K0 = 2 * np.pi / WAVELENGTH

# Tolerance parameters
ENERGY_CONSERVATION_TOLERANCE = 0.01  # 1% error tolerance
SPLIT_RATIO_TOLERANCE = 0.02  # 2% tolerance for split ratios


class TestBeamSplitter:
    """Test 7: Beam Splitter"""

    def test_50_50_split_ratios(self):
        """
        50/50 beam splitter should split intensity equally.
        Expected: I_T = I_R = 0.5 × I_incident
        """
        # Create incident wave
        incident_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        I_incident = compute_intensity(incident_wave)

        # Apply beam splitter
        transmitted, reflected = beam_splitter_50_50(incident_wave)

        I_transmitted = compute_intensity(transmitted)
        I_reflected = compute_intensity(reflected)

        # Check split ratios
        T_ratio = I_transmitted / I_incident
        R_ratio = I_reflected / I_incident

        assert abs(T_ratio - 0.5) < SPLIT_RATIO_TOLERANCE, (
            f"Transmission ratio {T_ratio:.4f} not equal to 0.5 (error > {SPLIT_RATIO_TOLERANCE})"
        )

        assert abs(R_ratio - 0.5) < SPLIT_RATIO_TOLERANCE, (
            f"Reflection ratio {R_ratio:.4f} not equal to 0.5 (error > {SPLIT_RATIO_TOLERANCE})"
        )

    def test_beam_splitter_energy_conservation(self):
        """
        Beam splitter must conserve energy.
        Expected: I_T + I_R = I_incident within 1% error
        """
        # Create incident wave
        incident_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        I_incident = compute_intensity(incident_wave)

        # Apply beam splitter
        transmitted, reflected = beam_splitter_50_50(incident_wave)

        I_transmitted = compute_intensity(transmitted)
        I_reflected = compute_intensity(reflected)

        # Verify energy conservation
        is_conserved, error = verify_beam_splitter_energy_conservation(
            I_incident, I_transmitted, I_reflected,
            tolerance=ENERGY_CONSERVATION_TOLERANCE
        )

        assert is_conserved, (
            f"Energy not conserved: error {error:.4%} > {ENERGY_CONSERVATION_TOLERANCE:.0%}"
        )

    def test_custom_split_ratios(self):
        """
        Custom beam splitter (70/30) should split according to configuration.
        Expected: T + R = 1, with T=0.7, R=0.3
        """
        # Create incident wave
        incident_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        I_incident = compute_intensity(incident_wave)

        # Apply custom 70/30 beam splitter
        config = BeamSplitterConfig(
            transmission_coefficient=0.7,
            reflection_coefficient=0.3
        )

        transmitted, reflected = beam_splitter_50_50(incident_wave, config)

        I_transmitted = compute_intensity(transmitted)
        I_reflected = compute_intensity(reflected)

        # Check split ratios
        T_ratio = I_transmitted / I_incident
        R_ratio = I_reflected / I_incident

        assert abs(T_ratio - 0.7) < SPLIT_RATIO_TOLERANCE, (
            f"Transmission ratio {T_ratio:.4f} not equal to 0.7"
        )

        assert abs(R_ratio - 0.3) < SPLIT_RATIO_TOLERANCE, (
            f"Reflection ratio {R_ratio:.4f} not equal to 0.3"
        )

        # Verify energy conservation
        is_conserved, error = verify_beam_splitter_energy_conservation(
            I_incident, I_transmitted, I_reflected,
            tolerance=ENERGY_CONSERVATION_TOLERANCE
        )

        assert is_conserved, (
            f"Energy not conserved for 70/30 split: error {error:.4%}"
        )

    def test_beam_splitter_phase_shifts(self):
        """
        Beam splitter should apply correct phase shifts.
        Standard: φ_T = 0, φ_R = π/2
        """
        # Create incident wave
        incident_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        # Apply beam splitter with standard phase shifts
        config = BeamSplitterConfig(
            transmission_phase_shift=0.0,
            reflection_phase_shift=np.pi/2
        )

        transmitted, reflected = beam_splitter_50_50(incident_wave, config)

        # Check phase shifts
        assert np.isclose(transmitted.phi0, 0.0, atol=1e-10), (
            f"Transmitted phase {transmitted.phi0:.6f} != 0"
        )

        assert np.isclose(reflected.phi0, np.pi/2, atol=1e-6), (
            f"Reflected phase {reflected.phi0:.6f} != π/2"
        )

    def test_invalid_beam_splitter_config(self):
        """
        Beam splitter config with T + R ≠ 1 should raise error.
        """
        with pytest.raises(ValueError, match="Energy conservation violated"):
            BeamSplitterConfig(
                transmission_coefficient=0.6,
                reflection_coefficient=0.5  # T + R = 1.1 > 1
            )


class TestMirror:
    """Test 8: Mirror"""

    def test_mirror_perfect_reflection(self):
        """
        Perfect mirror should reflect 100% of energy.
        Expected: I_reflected = I_incident
        """
        # Create incident wave
        incident_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        I_incident = compute_intensity(incident_wave)

        # Apply mirror
        reflected = mirror_reflect(incident_wave)

        I_reflected = compute_intensity(reflected)

        # Check reflection ratio
        R_ratio = I_reflected / I_incident

        assert abs(R_ratio - 1.0) < ENERGY_CONSERVATION_TOLERANCE, (
            f"Reflection ratio {R_ratio:.4f} not equal to 1.0 (error > {ENERGY_CONSERVATION_TOLERANCE})"
        )

    def test_mirror_energy_conservation(self):
        """
        Mirror must conserve energy (no absorption).
        Expected: I_reflected = I_incident within 1% error
        """
        # Create incident wave
        incident_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        I_incident = compute_intensity(incident_wave)

        # Apply mirror
        reflected = mirror_reflect(incident_wave)

        I_reflected = compute_intensity(reflected)

        # Verify energy conservation
        is_conserved, error = verify_mirror_energy_conservation(
            I_incident, I_reflected,
            tolerance=ENERGY_CONSERVATION_TOLERANCE
        )

        assert is_conserved, (
            f"Energy not conserved: error {error:.4%} > {ENERGY_CONSERVATION_TOLERANCE:.0%}"
        )

    def test_mirror_direction_reversal(self):
        """
        Mirror should reverse wave direction.
        Expected: k_reflected = -k_incident
        """
        # Create incident wave
        incident_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=0.0
        )

        # Apply mirror
        reflected = mirror_reflect(incident_wave)

        # Check direction reversal
        assert np.isclose(reflected.k0, -incident_wave.k0, atol=1e-10), (
            f"Wave number not reversed: k_reflected = {reflected.k0:.6f}, "
            f"expected {-incident_wave.k0:.6f}"
        )

        # Check frequency unchanged
        assert np.isclose(reflected.omega0, incident_wave.omega0, atol=1e-10), (
            f"Frequency changed: ω_reflected = {reflected.omega0:.6f}, "
            f"expected {incident_wave.omega0:.6f}"
        )

    def test_mirror_phase_preservation(self):
        """
        Mirror with no phase shift should preserve phase.
        Expected: φ_reflected = φ_incident (default config)
        """
        # Create incident wave with non-zero phase
        phi_incident = np.pi/4
        incident_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=phi_incident
        )

        # Apply mirror with no phase shift
        config = MirrorConfig(reflection_phase_shift=0.0)
        reflected = mirror_reflect(incident_wave, config)

        # Check phase preservation
        assert np.isclose(reflected.phi0, phi_incident, atol=1e-10), (
            f"Phase not preserved: φ_reflected = {reflected.phi0:.6f}, "
            f"expected {phi_incident:.6f}"
        )

    def test_mirror_with_phase_shift(self):
        """
        Mirror with π phase shift should add π to phase.
        Expected: φ_reflected = φ_incident + π
        """
        # Create incident wave
        phi_incident = 0.0
        incident_wave = create_gaussian_wave_packet_1d(
            grid_size=GRID_SIZE,
            x0=X0,
            k0=K0,
            sigma=SIGMA,
            phi0=phi_incident
        )

        # Apply mirror with π phase shift
        config = MirrorConfig(reflection_phase_shift=np.pi)
        reflected = mirror_reflect(incident_wave, config)

        # Check phase shift
        expected_phase = phi_incident + np.pi
        assert np.isclose(reflected.phi0, expected_phase, atol=1e-10), (
            f"Phase shift incorrect: φ_reflected = {reflected.phi0:.6f}, "
            f"expected {expected_phase:.6f}"
        )


# =======================
# Summary Report
# =======================

def test_phase_3_summary(capsys):
    """
    Summary test that runs all Phase 3 tests and reports results.
    """
    print()
    print("=" * 80)
    print("PHASE 3 VALIDATION SUMMARY: Optical Components")
    print("=" * 80)
    print()

    # Test beam splitter
    incident_wave = create_gaussian_wave_packet_1d(
        grid_size=GRID_SIZE,
        x0=X0,
        k0=K0,
        sigma=SIGMA,
        phi0=0.0
    )

    I_incident = compute_intensity(incident_wave)

    transmitted, reflected = beam_splitter_50_50(incident_wave)
    I_transmitted = compute_intensity(transmitted)
    I_reflected = compute_intensity(reflected)

    bs_conserved, bs_error = verify_beam_splitter_energy_conservation(
        I_incident, I_transmitted, I_reflected
    )

    # Test mirror
    reflected_mirror = mirror_reflect(incident_wave)
    I_reflected_mirror = compute_intensity(reflected_mirror)

    mirror_conserved, mirror_error = verify_mirror_energy_conservation(
        I_incident, I_reflected_mirror
    )

    print(f"Test 7: Beam Splitter (50/50 split)")
    print(f"  Transmission: {I_transmitted/I_incident:.4f} (target: 0.5000)")
    print(f"  Reflection: {I_reflected/I_incident:.4f} (target: 0.5000)")
    print(f"  Energy conservation error: {bs_error:.4%}")
    print(f"  Status: {'PASS' if bs_conserved else 'FAIL'}")
    print()

    print(f"Test 8: Mirror (Elastic Reflection)")
    print(f"  Reflection: {I_reflected_mirror/I_incident:.4f} (target: 1.0000)")
    print(f"  Direction reversed: {reflected_mirror.k0 == -incident_wave.k0}")
    print(f"  Energy conservation error: {mirror_error:.4%}")
    print(f"  Status: {'PASS' if mirror_conserved else 'FAIL'}")
    print()

    # Overall status
    all_pass = bs_conserved and mirror_conserved

    print("=" * 80)
    if all_pass:
        print("PHASE 3 COMPLETE: All optical components validated!")
    else:
        print("PHASE 3 INCOMPLETE: Some components failed")
    print("=" * 80)
    print()

    assert all_pass, "Phase 3 validation incomplete"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
