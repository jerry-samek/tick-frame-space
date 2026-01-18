"""
Two-Source Interference in Discrete Tick-Frame Spacetime

Implements simple two-source interference patterns to validate:
- Constructive interference (Δφ = 0)
- Destructive interference (Δφ = π)
- Variable phase interference patterns
- Fringe visibility measurements

Based on:
- Doc 062: Tick-Frame Interferometry
- Ch7 §4: Discrete wave equations
- Exp #55: Phase representation

Author: Tick-Frame Physics Project
Date: January 2026
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List
from wave_mechanics import (
    WavePacket,
    create_gaussian_wave_packet_1d,
    evolve_1d_wave_discrete,
    superpose_wave_packets,
    compute_fringe_visibility,
    DT, DX, C
)


@dataclass
class TwoSourceConfig:
    """Configuration for two-source interference experiment"""
    source_A_position: float
    source_B_position: float
    wavelength: float
    phase_difference: float  # Δφ between sources
    detector_position: float
    amplitude_A: float = 1.0
    amplitude_B: float = 1.0
    sigma_ratio: float = 1.0  # Wave packet width as ratio of wavelength


@dataclass
class InterferenceResult:
    """Results from two-source interference experiment"""
    intensity_pattern: np.ndarray
    positions: np.ndarray
    intensity_max: float
    intensity_min: float
    fringe_visibility: float
    phase_difference: float
    wave_packet_A: WavePacket
    wave_packet_B: WavePacket
    superposed_packet: WavePacket


def create_two_coherent_sources_1d(
    grid_size: int,
    source_A_pos: float,
    source_B_pos: float,
    wavelength: float,
    phase_difference: float = 0.0,
    amplitude_A: float = 1.0,
    amplitude_B: float = 1.0,
    sigma_ratio: float = 1.0
) -> Tuple[WavePacket, WavePacket]:
    """
    Create two coherent wave packet sources at different positions.

    Args:
        grid_size: Number of grid points
        source_A_pos: Position of source A (cells)
        source_B_pos: Position of source B (cells)
        wavelength: Wavelength λ (cells)
        phase_difference: Phase difference Δφ = φ_B - φ_A (radians)
        amplitude_A: Amplitude of source A
        amplitude_B: Amplitude of source B
        sigma_ratio: Wave packet width σ = sigma_ratio × wavelength

    Returns:
        (wave_packet_A, wave_packet_B): Two coherent wave packets
    """
    # Wave number k = 2π/λ
    k0 = 2 * np.pi / wavelength

    # Spatial width σ
    sigma = sigma_ratio * wavelength

    # Create source A with phase φ_A = 0
    packet_A = create_gaussian_wave_packet_1d(
        grid_size=grid_size,
        x0=source_A_pos,
        k0=k0,
        sigma=sigma,
        phi0=0.0
    )

    # Create source B with phase φ_B = φ_A + Δφ
    packet_B = create_gaussian_wave_packet_1d(
        grid_size=grid_size,
        x0=source_B_pos,
        k0=k0,
        sigma=sigma,
        phi0=phase_difference
    )

    # Adjust amplitudes
    if amplitude_A != 1.0:
        packet_A.psi *= amplitude_A
    if amplitude_B != 1.0:
        packet_B.psi *= amplitude_B

    return packet_A, packet_B


def propagate_to_detector_region_1d(
    packet_A: WavePacket,
    packet_B: WavePacket,
    detector_position: float,
    ticks: int
) -> Tuple[WavePacket, WavePacket]:
    """
    Propagate both wave packets to the detector region.

    Args:
        packet_A: Wave packet from source A
        packet_B: Wave packet from source B
        detector_position: Center of detector region (cells)
        ticks: Number of ticks to propagate

    Returns:
        (evolved_packet_A, evolved_packet_B): Propagated wave packets
    """
    # Store previous states for wave equation
    psi_A_n_minus_1 = packet_A.psi.copy()
    psi_A_n = packet_A.psi.copy()

    psi_B_n_minus_1 = packet_B.psi.copy()
    psi_B_n = packet_B.psi.copy()

    # Evolve both packets
    for tick in range(ticks):
        # Evolve packet A
        psi_A_n_plus_1 = evolve_1d_wave_discrete(psi_A_n, psi_A_n_minus_1)
        psi_A_n_minus_1 = psi_A_n
        psi_A_n = psi_A_n_plus_1

        # Evolve packet B
        psi_B_n_plus_1 = evolve_1d_wave_discrete(psi_B_n, psi_B_n_minus_1)
        psi_B_n_minus_1 = psi_B_n
        psi_B_n = psi_B_n_plus_1

    # Create updated wave packets
    packet_A_final = WavePacket(
        psi=psi_A_n,
        k0=packet_A.k0,
        omega0=packet_A.omega0,
        x0=packet_A.x0 + ticks * (DX/DT) * np.cos(packet_A.k0 * DX / 2),  # Approximate center
        sigma=packet_A.sigma,
        phi0=packet_A.phi0,
        tick=packet_A.tick + ticks
    )

    packet_B_final = WavePacket(
        psi=psi_B_n,
        k0=packet_B.k0,
        omega0=packet_B.omega0,
        x0=packet_B.x0 + ticks * (DX/DT) * np.cos(packet_B.k0 * DX / 2),
        sigma=packet_B.sigma,
        phi0=packet_B.phi0,
        tick=packet_B.tick + ticks
    )

    return packet_A_final, packet_B_final


def measure_interference_pattern_1d(
    packet_A: WavePacket,
    packet_B: WavePacket,
    detector_region: Tuple[int, int] = None
) -> InterferenceResult:
    """
    Measure interference pattern from two wave packets.

    Args:
        packet_A: Wave packet from source A
        packet_B: Wave packet from source B
        detector_region: (start_idx, end_idx) detector region, or None for full grid

    Returns:
        InterferenceResult with intensity pattern and fringe visibility
    """
    # Superpose wave packets
    superposed = superpose_wave_packets(packet_A, packet_B)

    # Compute intensity I = |ψ|²
    intensity_A = np.abs(packet_A.psi)**2
    intensity_B = np.abs(packet_B.psi)**2
    intensity_total = np.abs(superposed.psi)**2

    # Extract detector region
    if detector_region is not None:
        start_idx, end_idx = detector_region
        intensity_pattern = intensity_total[start_idx:end_idx]
        positions = np.arange(start_idx, end_idx, dtype=float)
    else:
        intensity_pattern = intensity_total
        positions = np.arange(len(intensity_total), dtype=float)

    # Find intensity extrema in detector region
    intensity_max = np.max(intensity_pattern)
    intensity_min = np.min(intensity_pattern)

    # Compute fringe visibility V = (I_max - I_min) / (I_max + I_min)
    visibility = compute_fringe_visibility(intensity_max, intensity_min)

    # Phase difference
    phase_diff = packet_B.phi0 - packet_A.phi0

    return InterferenceResult(
        intensity_pattern=intensity_pattern,
        positions=positions,
        intensity_max=intensity_max,
        intensity_min=intensity_min,
        fringe_visibility=visibility,
        phase_difference=phase_diff,
        wave_packet_A=packet_A,
        wave_packet_B=packet_B,
        superposed_packet=superposed
    )


def run_two_source_interference_experiment(
    config: TwoSourceConfig,
    grid_size: int = 4096,
    propagation_ticks: int = 0
) -> InterferenceResult:
    """
    Run complete two-source interference experiment.

    Args:
        config: TwoSourceConfig with experiment parameters
        grid_size: Grid size (default 4096)
        propagation_ticks: Number of ticks to propagate before measurement

    Returns:
        InterferenceResult with full measurement data
    """
    # Create coherent sources
    packet_A, packet_B = create_two_coherent_sources_1d(
        grid_size=grid_size,
        source_A_pos=config.source_A_position,
        source_B_pos=config.source_B_position,
        wavelength=config.wavelength,
        phase_difference=config.phase_difference,
        amplitude_A=config.amplitude_A,
        amplitude_B=config.amplitude_B,
        sigma_ratio=config.sigma_ratio
    )

    # Propagate to detector region if needed
    if propagation_ticks > 0:
        packet_A, packet_B = propagate_to_detector_region_1d(
            packet_A=packet_A,
            packet_B=packet_B,
            detector_position=config.detector_position,
            ticks=propagation_ticks
        )

    # Determine detector region (centered on detector_position)
    # Use moderate region to capture interference fringes
    detector_width = int(2 * config.wavelength)  # 2λ detector width
    detector_start = int(config.detector_position - detector_width // 2)
    detector_end = int(config.detector_position + detector_width // 2)
    detector_region = (detector_start, detector_end)

    # Measure interference pattern
    result = measure_interference_pattern_1d(
        packet_A=packet_A,
        packet_B=packet_B,
        detector_region=detector_region
    )

    return result


def scan_phase_difference(
    source_A_pos: float,
    source_B_pos: float,
    wavelength: float,
    detector_pos: float,
    phase_steps: int = 100,
    grid_size: int = 4096,
    sigma_ratio: float = 1.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Scan interference intensity vs phase difference.

    Args:
        source_A_pos: Position of source A (cells)
        source_B_pos: Position of source B (cells)
        wavelength: Wavelength λ (cells)
        detector_pos: Detector position (cells)
        phase_steps: Number of phase points to sample
        grid_size: Grid size
        sigma_ratio: Wave packet width ratio (sigma = sigma_ratio * wavelength)

    Returns:
        (phase_array, intensity_array, visibility_array):
            - phase_array: Phase differences tested (radians)
            - intensity_array: Peak intensity at each phase
            - visibility_array: Fringe visibility at each phase
    """
    phase_array = np.linspace(0, 2 * np.pi, phase_steps)
    intensity_array = np.zeros(phase_steps)
    visibility_array = np.zeros(phase_steps)

    for i, phase_diff in enumerate(phase_array):
        config = TwoSourceConfig(
            source_A_position=source_A_pos,
            source_B_position=source_B_pos,
            wavelength=wavelength,
            phase_difference=phase_diff,
            detector_position=detector_pos,
            sigma_ratio=sigma_ratio
        )

        result = run_two_source_interference_experiment(
            config=config,
            grid_size=grid_size,
            propagation_ticks=0
        )

        intensity_array[i] = result.intensity_max
        visibility_array[i] = result.fringe_visibility

    return phase_array, intensity_array, visibility_array


def verify_interference_formula(
    intensity_A: float,
    intensity_B: float,
    phase_difference: float
) -> float:
    """
    Compute theoretical intensity from interference formula.

    I_total = I_A + I_B + 2√(I_A × I_B) × cos(Δφ)

    Args:
        intensity_A: Intensity of source A
        intensity_B: Intensity of source B
        phase_difference: Phase difference Δφ (radians)

    Returns:
        Theoretical total intensity
    """
    cross_term = 2 * np.sqrt(intensity_A * intensity_B) * np.cos(phase_difference)
    return intensity_A + intensity_B + cross_term


# =======================
# Example Usage & Testing
# =======================

if __name__ == "__main__":
    print("=" * 80)
    print("Two-Source Interference in Discrete Tick-Frame Spacetime")
    print("=" * 80)
    print()

    # Test parameters
    wavelength = 100.0  # cells
    grid_size = 4096

    # Source positions (CO-LOCATED for pure phase interference without spatial fringes)
    detector_pos = grid_size // 2
    source_A_pos = detector_pos  # Both sources at same position!
    source_B_pos = detector_pos  # This tests PURE phase interference
    source_separation = 0.0

    print(f"Configuration:")
    print(f"  Wavelength: {wavelength:.1f} cells")
    print(f"  Source A position: {source_A_pos:.1f}")
    print(f"  Source B position: {source_B_pos:.1f}")
    print(f"  Detector position: {detector_pos:.1f}")
    print(f"  Source separation: {source_separation:.1f} cells")
    print()

    # Test 1: Constructive interference (Δφ = 0)
    print("Test 1: Constructive Interference (d_phi = 0)")
    print("-" * 80)
    config_constructive = TwoSourceConfig(
        source_A_position=source_A_pos,
        source_B_position=source_B_pos,
        wavelength=wavelength,
        phase_difference=0.0,  # In phase
        detector_position=detector_pos,
        sigma_ratio=3.0  # Wide wave packets for good overlap
    )
    result_constructive = run_two_source_interference_experiment(config_constructive, grid_size)

    # Measure individual source intensities (for comparison)
    I_A = np.max(np.abs(result_constructive.wave_packet_A.psi)**2)
    I_B = np.max(np.abs(result_constructive.wave_packet_B.psi)**2)
    I_total_constructive = result_constructive.intensity_max
    I_theory_constructive = verify_interference_formula(I_A, I_B, 0.0)

    print(f"  Individual source intensities:")
    print(f"    I_A = {I_A:.6f}")
    print(f"    I_B = {I_B:.6f}")
    print(f"  Combined intensity:")
    print(f"    Measured: I_total = {I_total_constructive:.6f}")
    print(f"    Theory:   I_total = {I_theory_constructive:.6f}")
    print(f"    Expected: I_total = 4*I_0 = {4 * I_A:.6f} (perfect constructive)")
    print(f"  Fringe visibility: V = {result_constructive.fringe_visibility:.4f}")
    ratio_constructive = I_total_constructive / (I_A + I_B)
    print(f"  Enhancement ratio: {ratio_constructive:.3f} (ideal = 2.0)")
    print()

    # Test 2: Destructive interference (Δφ = π)
    print("Test 2: Destructive Interference (d_phi = pi)")
    print("-" * 80)
    config_destructive = TwoSourceConfig(
        source_A_position=source_A_pos,
        source_B_position=source_B_pos,
        wavelength=wavelength,
        phase_difference=np.pi,  # Out of phase
        detector_position=detector_pos,
        sigma_ratio=3.0  # Wide wave packets for good overlap
    )
    result_destructive = run_two_source_interference_experiment(config_destructive, grid_size)

    I_total_destructive = result_destructive.intensity_max
    I_min_destructive = result_destructive.intensity_min
    I_theory_destructive = verify_interference_formula(I_A, I_B, np.pi)

    print(f"  Individual source intensities:")
    print(f"    I_A = {I_A:.6f}")
    print(f"    I_B = {I_B:.6f}")
    print(f"  Combined intensity:")
    print(f"    Measured max: I_max = {I_total_destructive:.6f}")
    print(f"    Measured min: I_min = {I_min_destructive:.6f}")
    print(f"    Theory:       I_total = {I_theory_destructive:.6f}")
    print(f"    Expected:     I_min ~= 0 (perfect destructive)")
    print(f"  Fringe visibility: V = {result_destructive.fringe_visibility:.4f}")
    suppression_ratio = I_min_destructive / (I_A + I_B)
    print(f"  Suppression ratio: {suppression_ratio:.6f} (ideal = 0.0)")
    print()

    # Test 3: Variable phase scan
    print("Test 3: Variable Phase Scan")
    print("-" * 80)
    phase_array, intensity_array, visibility_array = scan_phase_difference(
        source_A_pos=source_A_pos,
        source_B_pos=source_B_pos,
        wavelength=wavelength,
        detector_pos=detector_pos,
        phase_steps=20,
        grid_size=grid_size,
        sigma_ratio=3.0
    )

    # Calculate TRUE phase-modulation visibility from scan
    I_max_phase_scan = np.max(intensity_array)
    I_min_phase_scan = np.min(intensity_array)
    visibility_phase_modulation = (I_max_phase_scan - I_min_phase_scan) / (I_max_phase_scan + I_min_phase_scan)

    print(f"  Scanned {len(phase_array)} phase points from 0 to 2*pi")
    print(f"  Intensity range:")
    print(f"    Max: {I_max_phase_scan:.6f} (at d_phi ~= 0)")
    print(f"    Min: {I_min_phase_scan:.6f} (at d_phi ~= pi)")
    print(f"  Phase-modulation visibility: V = {visibility_phase_modulation:.4f}")
    print(f"  (Spatial fringe visibility: V = {np.mean(visibility_array):.4f})")
    print()

    # Verify sinusoidal pattern
    # Fit I(d_phi) = A + B*cos(d_phi)
    from scipy.optimize import curve_fit

    def intensity_model(phase, A, B):
        return A + B * np.cos(phase)

    try:
        params, _ = curve_fit(intensity_model, phase_array, intensity_array)
        A_fit, B_fit = params
        print(f"  Fit to I(d_phi) = A + B*cos(d_phi):")
        print(f"    A = {A_fit:.6f} (baseline)")
        print(f"    B = {B_fit:.6f} (modulation)")
        print(f"    Expected: A = I_A + I_B = {I_A + I_B:.6f}")
        print(f"    Expected: B = 2*sqrt(I_A*I_B) = {2 * np.sqrt(I_A * I_B):.6f}")
        print()
    except Exception as e:
        print(f"  Fit failed: {e}")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY: Phase 2 Two-Source Interference")
    print("=" * 80)
    print(f"[+] Constructive interference: Enhancement ratio = {ratio_constructive:.3f} (target: 2.0)")
    print(f"[+] Destructive interference: Suppression ratio = {suppression_ratio:.6f} (target: 0.0)")
    print(f"[+] Variable phase: Phase-modulation visibility V = {visibility_phase_modulation:.4f} (target: >0.95)")
    print()

    # Success criteria
    success_constructive = ratio_constructive > 1.8  # Within 10% of ideal
    success_destructive = suppression_ratio < 0.1  # Nearly complete cancellation
    success_visibility = visibility_phase_modulation > 0.95  # Phase modulation visibility

    if success_constructive and success_destructive and success_visibility:
        print("[SUCCESS] ALL TESTS PASSED - Phase 2 success criteria met!")
    else:
        print("[WARNING] Some tests did not meet success criteria:")
        if not success_constructive:
            print(f"  - Constructive interference: ratio {ratio_constructive:.3f} < 1.8")
        if not success_destructive:
            print(f"  - Destructive interference: suppression {suppression_ratio:.6f} > 0.1")
        if not success_visibility:
            print(f"  - Phase-modulation visibility: V {visibility_phase_modulation:.4f} < 0.95")
    print()
