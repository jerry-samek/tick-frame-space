"""
Mach-Zehnder Interferometer in Tick-Frame Spacetime

Implements complete interferometer assembly combining beam splitters and mirrors.

Configuration:
         M1
         /\\
        /  \\
    BS1     BS2 -> D1
    |   \\  /  |
    |    \\/   v
    |    M2   D2
    v
Source

Components:
- BS1: Input beam splitter (50/50)
- M1, M2: Mirrors (path redirection)
- BS2: Output beam splitter (50/50, recombination)
- D1, D2: Detectors (interference measurement)

Based on:
- Doc 062 §2.4: Mach-Zehnder assembly
- Phase 3: Validated optical components

Author: Tick-Frame Physics Project
Date: January 2026
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
from wave_mechanics import WavePacket, create_gaussian_wave_packet_1d
from optical_components import (
    beam_splitter_50_50,
    mirror_reflect,
    compute_intensity,
    BeamSplitterConfig,
    MirrorConfig
)


@dataclass
class MachZehnderConfig:
    """Configuration for Mach-Zehnder interferometer"""
    path_A_length: float = 0.0  # Extra path length in arm A (cells)
    path_B_length: float = 0.0  # Extra path length in arm B (cells)
    bs1_config: Optional[BeamSplitterConfig] = None  # Input beam splitter
    bs2_config: Optional[BeamSplitterConfig] = None  # Output beam splitter
    m1_config: Optional[MirrorConfig] = None  # Mirror 1 (arm A)
    m2_config: Optional[MirrorConfig] = None  # Mirror 2 (arm B)


@dataclass
class InterferometerResult:
    """Results from Mach-Zehnder interferometer measurement"""
    detector_1_intensity: float
    detector_2_intensity: float
    total_output_intensity: float
    source_intensity: float
    fringe_visibility: float
    path_difference: float
    phase_difference: float
    energy_conservation_error: float
    path_A_wave: WavePacket
    path_B_wave: WavePacket
    detector_1_wave: WavePacket
    detector_2_wave: WavePacket


def add_path_length(wave: WavePacket, path_length: float) -> WavePacket:
    """
    Add extra path length by shifting wave phase.

    Path difference ΔL creates phase shift Δφ = k × ΔL

    Args:
        wave: Input wave packet
        path_length: Additional path length (cells)

    Returns:
        Wave packet with phase shift applied
    """
    if path_length == 0:
        return wave

    # Phase shift from path length: Δφ = k × ΔL
    phase_shift = wave.k0 * path_length

    # Apply phase shift to wave function
    psi_shifted = wave.psi * np.exp(1j * phase_shift)

    return WavePacket(
        psi=psi_shifted,
        k0=wave.k0,
        omega0=wave.omega0,
        x0=wave.x0,
        sigma=wave.sigma,
        phi0=wave.phi0 + phase_shift,
        tick=wave.tick
    )


def mach_zehnder_interferometer(
    source_wave: WavePacket,
    config: Optional[MachZehnderConfig] = None
) -> InterferometerResult:
    """
    Run complete Mach-Zehnder interferometer.

    Path sequence:
    1. Source -> BS1 (split into paths A and B)
    2. Path A: BS1 -> M1 -> BS2
    3. Path B: BS1 -> M2 -> BS2
    4. BS2 -> Detectors D1 and D2 (interference)

    Args:
        source_wave: Input wave packet
        config: Interferometer configuration

    Returns:
        InterferometerResult with detector intensities and analysis
    """
    if config is None:
        config = MachZehnderConfig()

    # Source intensity
    I_source = compute_intensity(source_wave)

    # ===== Stage 1: Input Beam Splitter (BS1) =====
    # Split into two paths
    bs1_config = config.bs1_config if config.bs1_config else BeamSplitterConfig()
    path_A_initial, path_B_initial = beam_splitter_50_50(source_wave, bs1_config)

    # ===== Stage 2: Mirrors (M1, M2) =====
    # Redirect beams (in real interferometer, just changes direction)
    # For our 1D simulation, we'll just keep tracking the waves
    m1_config = config.m1_config if config.m1_config else MirrorConfig()
    m2_config = config.m2_config if config.m2_config else MirrorConfig()

    # Mirror reflection (doesn't change physics in 1D, just for completeness)
    path_A_after_mirror = mirror_reflect(path_A_initial, m1_config)
    path_B_after_mirror = mirror_reflect(path_B_initial, m2_config)

    # Mirror again to restore direction (second reflection)
    path_A_after_mirror = mirror_reflect(path_A_after_mirror, m1_config)
    path_B_after_mirror = mirror_reflect(path_B_after_mirror, m2_config)

    # ===== Stage 3: Path Length Difference =====
    # Add extra path length to create phase difference
    path_A_final = add_path_length(path_A_after_mirror, config.path_A_length)
    path_B_final = add_path_length(path_B_after_mirror, config.path_B_length)

    # Calculate path difference and phase difference
    path_difference = config.path_B_length - config.path_A_length
    phase_difference = path_A_final.k0 * path_difference

    # ===== Stage 4: Output Beam Splitter (BS2) =====
    # Recombine beams at BS2
    bs2_config = config.bs2_config if config.bs2_config else BeamSplitterConfig()

    # Path A hits BS2
    path_A_transmitted, path_A_reflected = beam_splitter_50_50(path_A_final, bs2_config)

    # Path B hits BS2
    path_B_transmitted, path_B_reflected = beam_splitter_50_50(path_B_final, bs2_config)

    # ===== Stage 5: Detectors (D1, D2) =====
    # D1 receives: transmitted from A + reflected from B
    # D2 receives: reflected from A + transmitted from B

    # Superpose at each detector
    detector_1_psi = path_A_transmitted.psi + path_B_reflected.psi
    detector_2_psi = path_A_reflected.psi + path_B_transmitted.psi

    detector_1_wave = WavePacket(
        psi=detector_1_psi,
        k0=path_A_transmitted.k0,
        omega0=path_A_transmitted.omega0,
        x0=path_A_transmitted.x0,
        sigma=path_A_transmitted.sigma,
        phi0=0.0,  # Combined phase
        tick=path_A_transmitted.tick
    )

    detector_2_wave = WavePacket(
        psi=detector_2_psi,
        k0=path_A_reflected.k0,
        omega0=path_A_reflected.omega0,
        x0=path_A_reflected.x0,
        sigma=path_A_reflected.sigma,
        phi0=0.0,  # Combined phase
        tick=path_A_reflected.tick
    )

    # Measure intensities
    I_D1 = compute_intensity(detector_1_wave)
    I_D2 = compute_intensity(detector_2_wave)
    I_total = I_D1 + I_D2

    # Calculate fringe visibility
    I_max = max(I_D1, I_D2)
    I_min = min(I_D1, I_D2)
    visibility = (I_max - I_min) / (I_max + I_min) if (I_max + I_min) > 0 else 0

    # Energy conservation error
    energy_error = abs(I_total - I_source) / I_source if I_source > 0 else 0

    return InterferometerResult(
        detector_1_intensity=I_D1,
        detector_2_intensity=I_D2,
        total_output_intensity=I_total,
        source_intensity=I_source,
        fringe_visibility=visibility,
        path_difference=path_difference,
        phase_difference=phase_difference,
        energy_conservation_error=energy_error,
        path_A_wave=path_A_final,
        path_B_wave=path_B_final,
        detector_1_wave=detector_1_wave,
        detector_2_wave=detector_2_wave
    )


def scan_path_difference(
    source_wave: WavePacket,
    path_differences: np.ndarray,
    config: Optional[MachZehnderConfig] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Scan interferometer output vs path difference.

    Args:
        source_wave: Input wave packet
        path_differences: Array of path differences to scan (cells)
        config: Base interferometer configuration

    Returns:
        (path_diffs, D1_intensities, D2_intensities)
    """
    if config is None:
        config = MachZehnderConfig()

    D1_intensities = np.zeros(len(path_differences))
    D2_intensities = np.zeros(len(path_differences))

    for i, path_diff in enumerate(path_differences):
        # Update path difference
        test_config = MachZehnderConfig(
            path_A_length=0.0,
            path_B_length=path_diff,
            bs1_config=config.bs1_config,
            bs2_config=config.bs2_config,
            m1_config=config.m1_config,
            m2_config=config.m2_config
        )

        result = mach_zehnder_interferometer(source_wave, test_config)

        D1_intensities[i] = result.detector_1_intensity
        D2_intensities[i] = result.detector_2_intensity

    return path_differences, D1_intensities, D2_intensities


# =======================
# Example Usage & Testing
# =======================

if __name__ == "__main__":
    print("=" * 80)
    print("Mach-Zehnder Interferometer in Tick-Frame Spacetime")
    print("=" * 80)
    print()

    # Create source wave
    grid_size = 4096
    wavelength = 100.0
    k0 = 2 * np.pi / wavelength
    x0 = grid_size / 2
    sigma = 3 * wavelength

    source_wave = create_gaussian_wave_packet_1d(
        grid_size=grid_size,
        x0=x0,
        k0=k0,
        sigma=sigma,
        phi0=0.0
    )

    print(f"Source wave:")
    print(f"  Wavelength: {wavelength:.1f} cells")
    print(f"  Source intensity: {compute_intensity(source_wave):.6f}")
    print()

    # Test 1: Equal path lengths (constructive)
    print("Test 1: Equal Path Lengths (dL = 0)")
    print("-" * 80)

    config_equal = MachZehnderConfig(
        path_A_length=0.0,
        path_B_length=0.0
    )

    result_equal = mach_zehnder_interferometer(source_wave, config_equal)

    print(f"Path difference: dL = {result_equal.path_difference:.1f} cells")
    print(f"Phase difference: d_phi = {result_equal.phase_difference:.4f} rad")
    print(f"Detector 1: I_D1 = {result_equal.detector_1_intensity:.6f}")
    print(f"Detector 2: I_D2 = {result_equal.detector_2_intensity:.6f}")
    print(f"Total output: I_total = {result_equal.total_output_intensity:.6f}")
    print(f"Fringe visibility: V = {result_equal.fringe_visibility:.4f}")
    print(f"Energy conservation error: {result_equal.energy_conservation_error:.4%}")
    print()

    # Test 2: lambda/2 path difference (destructive)
    print("Test 2: lambda/2 Path Difference (dL = lambda/2)")
    print("-" * 80)

    config_half_lambda = MachZehnderConfig(
        path_A_length=0.0,
        path_B_length=wavelength / 2  # lambda/2 path difference
    )

    result_half_lambda = mach_zehnder_interferometer(source_wave, config_half_lambda)

    print(f"Path difference: dL = {result_half_lambda.path_difference:.1f} cells (lambda/2 = {wavelength/2:.1f})")
    print(f"Phase difference: d_phi = {result_half_lambda.phase_difference:.4f} rad (pi = {np.pi:.4f})")
    print(f"Detector 1: I_D1 = {result_half_lambda.detector_1_intensity:.6f}")
    print(f"Detector 2: I_D2 = {result_half_lambda.detector_2_intensity:.6f}")
    print(f"Total output: I_total = {result_half_lambda.total_output_intensity:.6f}")
    print(f"Fringe visibility: V = {result_half_lambda.fringe_visibility:.4f}")
    print(f"Energy conservation error: {result_half_lambda.energy_conservation_error:.4%}")
    print()

    # Test 3: Path difference scan
    print("Test 3: Path Difference Scan (0 to 2*lambda)")
    print("-" * 80)

    path_diffs = np.linspace(0, 2 * wavelength, 50)
    path_array, D1_array, D2_array = scan_path_difference(source_wave, path_diffs)

    print(f"Scanned {len(path_diffs)} path differences from 0 to {2*wavelength:.1f} cells")
    print(f"D1 intensity range: [{np.min(D1_array):.6f}, {np.max(D1_array):.6f}]")
    print(f"D2 intensity range: [{np.min(D2_array):.6f}, {np.max(D2_array):.6f}]")

    # Calculate visibility from scan
    I_max_scan = max(np.max(D1_array), np.max(D2_array))
    I_min_scan = min(np.min(D1_array), np.min(D2_array))
    visibility_scan = (I_max_scan - I_min_scan) / (I_max_scan + I_min_scan)

    print(f"Scan visibility: V = {visibility_scan:.4f}")
    print()

    # Verify fringes
    # Count intensity peaks in D1
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(D1_array, height=np.mean(D1_array))
    fringe_count = len(peaks)
    expected_fringes = int(2 * wavelength / wavelength)  # Should be ~2

    print(f"Fringe analysis:")
    print(f"  Detected fringes: {fringe_count}")
    print(f"  Expected fringes: ~{expected_fringes} (in 2*lambda scan)")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY: Mach-Zehnder Interferometer Phase 4")
    print("=" * 80)
    print(f"[+] Equal paths: Visibility V = {result_equal.fringe_visibility:.4f}")
    print(f"[+] lambda/2 difference: Visibility V = {result_half_lambda.fringe_visibility:.4f}")
    print(f"[+] Path scan: Visibility V = {visibility_scan:.4f} (target > 0.9)")
    print(f"[+] Energy conservation: {result_equal.energy_conservation_error:.4%} error")
    print()

    success = visibility_scan > 0.9 and result_equal.energy_conservation_error < 0.01
    if success:
        print("[SUCCESS] Mach-Zehnder interferometer validated!")
    else:
        print("[WARNING] Some validation criteria not met")
    print()
