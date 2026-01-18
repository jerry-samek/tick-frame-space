"""
Optical Components for Tick-Frame Interferometry

Implements beam splitters and mirrors for Mach-Zehnder interferometer
in discrete tick-frame spacetime.

Components:
- BeamSplitter: 50/50 split with T + R = 1 energy conservation
- Mirror: Elastic reflection with phase preservation

Based on:
- Doc 062 §2.3: Optical component specifications
- Standard interferometry: Phase shifts and energy conservation

Author: Tick-Frame Physics Project
Date: January 2026
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
from wave_mechanics import WavePacket


@dataclass
class BeamSplitterConfig:
    """Configuration for beam splitter"""
    transmission_coefficient: float = 0.5  # T (default 50/50)
    reflection_coefficient: float = 0.5    # R (default 50/50)
    transmission_phase_shift: float = 0.0  # Phase shift for transmitted beam
    reflection_phase_shift: float = np.pi/2  # Phase shift for reflected beam (π/2 standard)

    def __post_init__(self):
        """Validate energy conservation"""
        total = self.transmission_coefficient + self.reflection_coefficient
        if not np.isclose(total, 1.0, atol=1e-6):
            raise ValueError(
                f"Energy conservation violated: T + R = {total:.6f} ≠ 1.0"
            )


@dataclass
class MirrorConfig:
    """Configuration for mirror"""
    reflection_coefficient: float = 1.0  # R = 1 (perfect reflection)
    reflection_phase_shift: float = 0.0  # Phase shift on reflection


def beam_splitter_50_50(
    incident_wave: WavePacket,
    config: Optional[BeamSplitterConfig] = None
) -> Tuple[WavePacket, WavePacket]:
    """
    Apply 50/50 beam splitter to incident wave packet.

    Physics:
    - Transmitted beam: amplitude *= sqrt(T), phase += φ_T
    - Reflected beam: amplitude *= sqrt(R), phase += φ_R
    - Energy conservation: T + R = 1
    - Standard: φ_R = π/2 (relative phase shift)

    Args:
        incident_wave: Incoming wave packet
        config: Beam splitter configuration (default 50/50)

    Returns:
        (transmitted_wave, reflected_wave): Split wave packets
    """
    if config is None:
        config = BeamSplitterConfig()

    # Extract incident wave properties
    psi_incident = incident_wave.psi

    # Transmitted beam: amplitude *= sqrt(T), add phase shift
    psi_transmitted = psi_incident * np.sqrt(config.transmission_coefficient)
    if config.transmission_phase_shift != 0:
        psi_transmitted *= np.exp(1j * config.transmission_phase_shift)

    transmitted_wave = WavePacket(
        psi=psi_transmitted,
        k0=incident_wave.k0,
        omega0=incident_wave.omega0,
        x0=incident_wave.x0,
        sigma=incident_wave.sigma,
        phi0=incident_wave.phi0 + config.transmission_phase_shift,
        tick=incident_wave.tick
    )

    # Reflected beam: amplitude *= sqrt(R), add phase shift
    psi_reflected = psi_incident * np.sqrt(config.reflection_coefficient)
    if config.reflection_phase_shift != 0:
        psi_reflected *= np.exp(1j * config.reflection_phase_shift)

    reflected_wave = WavePacket(
        psi=psi_reflected,
        k0=incident_wave.k0,
        omega0=incident_wave.omega0,
        x0=incident_wave.x0,
        sigma=incident_wave.sigma,
        phi0=incident_wave.phi0 + config.reflection_phase_shift,
        tick=incident_wave.tick
    )

    return transmitted_wave, reflected_wave


def mirror_reflect(
    incident_wave: WavePacket,
    config: Optional[MirrorConfig] = None
) -> WavePacket:
    """
    Reflect wave packet from perfect mirror.

    Physics:
    - Reflection coefficient R = 1.0 (100% reflection)
    - Direction reversal: k → -k
    - Optional phase shift φ_R (typically 0 or π)
    - Energy conservation: all energy reflected

    Args:
        incident_wave: Incoming wave packet
        config: Mirror configuration (default R=1, φ=0)

    Returns:
        reflected_wave: Reflected wave packet with reversed direction
    """
    if config is None:
        config = MirrorConfig()

    # Extract incident wave properties
    psi_incident = incident_wave.psi

    # Reflected beam: amplitude *= sqrt(R), add phase shift, reverse k
    psi_reflected = psi_incident * np.sqrt(config.reflection_coefficient)
    if config.reflection_phase_shift != 0:
        psi_reflected *= np.exp(1j * config.reflection_phase_shift)

    # Direction reversal: k → -k
    k_reflected = -incident_wave.k0

    reflected_wave = WavePacket(
        psi=psi_reflected,
        k0=k_reflected,  # Reversed wave number
        omega0=incident_wave.omega0,  # Frequency unchanged
        x0=incident_wave.x0,
        sigma=incident_wave.sigma,
        phi0=incident_wave.phi0 + config.reflection_phase_shift,
        tick=incident_wave.tick
    )

    return reflected_wave


def verify_beam_splitter_energy_conservation(
    incident_intensity: float,
    transmitted_intensity: float,
    reflected_intensity: float,
    tolerance: float = 0.01
) -> Tuple[bool, float]:
    """
    Verify energy conservation in beam splitter.

    Energy conservation: I_T + I_R = I_incident

    Args:
        incident_intensity: Incident beam intensity
        transmitted_intensity: Transmitted beam intensity
        reflected_intensity: Reflected beam intensity
        tolerance: Relative error tolerance (default 1%)

    Returns:
        (is_conserved, relative_error): Conservation status and error
    """
    total_output = transmitted_intensity + reflected_intensity
    relative_error = abs(total_output - incident_intensity) / incident_intensity
    is_conserved = relative_error < tolerance

    return is_conserved, relative_error


def verify_mirror_energy_conservation(
    incident_intensity: float,
    reflected_intensity: float,
    tolerance: float = 0.01
) -> Tuple[bool, float]:
    """
    Verify energy conservation in mirror.

    Energy conservation: I_R = I_incident (perfect reflection)

    Args:
        incident_intensity: Incident beam intensity
        reflected_intensity: Reflected beam intensity
        tolerance: Relative error tolerance (default 1%)

    Returns:
        (is_conserved, relative_error): Conservation status and error
    """
    relative_error = abs(reflected_intensity - incident_intensity) / incident_intensity
    is_conserved = relative_error < tolerance

    return is_conserved, relative_error


def compute_intensity(wave: WavePacket) -> float:
    """
    Compute total intensity (energy) of wave packet.

    I = ∫|ψ|² dx

    Args:
        wave: Wave packet

    Returns:
        Total intensity
    """
    from wave_mechanics import DX
    return np.sum(np.abs(wave.psi)**2) * DX


# =======================
# Example Usage & Testing
# =======================

if __name__ == "__main__":
    from wave_mechanics import create_gaussian_wave_packet_1d

    print("=" * 80)
    print("Optical Components Testing: Beam Splitter & Mirror")
    print("=" * 80)
    print()

    # Create test wave packet
    grid_size = 4096
    wavelength = 100.0
    k0 = 2 * np.pi / wavelength
    x0 = grid_size / 2
    sigma = wavelength

    incident_wave = create_gaussian_wave_packet_1d(
        grid_size=grid_size,
        x0=x0,
        k0=k0,
        sigma=sigma,
        phi0=0.0
    )

    print(f"Incident wave packet:")
    print(f"  Wavelength: {wavelength:.1f} cells")
    print(f"  Center position: {x0:.1f}")
    print(f"  Width: {sigma:.1f}")

    # Compute incident intensity
    I_incident = compute_intensity(incident_wave)
    print(f"  Intensity: {I_incident:.6f}")
    print()

    # Test 1: Beam Splitter 50/50
    print("Test 1: Beam Splitter (50/50 split)")
    print("-" * 80)

    transmitted, reflected = beam_splitter_50_50(incident_wave)

    I_transmitted = compute_intensity(transmitted)
    I_reflected = compute_intensity(reflected)

    print(f"Transmitted beam:")
    print(f"  Intensity: {I_transmitted:.6f}")
    print(f"  Fraction: {I_transmitted/I_incident:.4f} (expected: 0.5000)")
    print()

    print(f"Reflected beam:")
    print(f"  Intensity: {I_reflected:.6f}")
    print(f"  Fraction: {I_reflected/I_incident:.4f} (expected: 0.5000)")
    print()

    # Verify energy conservation
    is_conserved, error = verify_beam_splitter_energy_conservation(
        I_incident, I_transmitted, I_reflected
    )

    print(f"Energy conservation:")
    print(f"  I_T + I_R = {I_transmitted + I_reflected:.6f}")
    print(f"  I_incident = {I_incident:.6f}")
    print(f"  Relative error: {error:.6%}")
    print(f"  Status: {'PASS' if is_conserved else 'FAIL'} (tolerance: 1%)")
    print()

    # Test 2: Mirror Reflection
    print("Test 2: Mirror (Perfect Reflection)")
    print("-" * 80)

    reflected_mirror = mirror_reflect(incident_wave)

    I_reflected_mirror = compute_intensity(reflected_mirror)

    print(f"Reflected beam:")
    print(f"  Intensity: {I_reflected_mirror:.6f}")
    print(f"  Fraction: {I_reflected_mirror/I_incident:.4f} (expected: 1.0000)")
    print(f"  Wave number k: {reflected_mirror.k0:.6f}")
    print(f"  Incident k: {incident_wave.k0:.6f}")
    print(f"  Direction reversed: {np.sign(reflected_mirror.k0) != np.sign(incident_wave.k0)}")
    print()

    # Verify energy conservation
    is_conserved_mirror, error_mirror = verify_mirror_energy_conservation(
        I_incident, I_reflected_mirror
    )

    print(f"Energy conservation:")
    print(f"  I_reflected = {I_reflected_mirror:.6f}")
    print(f"  I_incident = {I_incident:.6f}")
    print(f"  Relative error: {error_mirror:.6%}")
    print(f"  Status: {'PASS' if is_conserved_mirror else 'FAIL'} (tolerance: 1%)")
    print()

    # Test 3: Custom beam splitter (70/30 split)
    print("Test 3: Custom Beam Splitter (70/30 split)")
    print("-" * 80)

    config_70_30 = BeamSplitterConfig(
        transmission_coefficient=0.7,
        reflection_coefficient=0.3,
        transmission_phase_shift=0.0,
        reflection_phase_shift=np.pi/2
    )

    transmitted_70, reflected_30 = beam_splitter_50_50(incident_wave, config_70_30)

    I_transmitted_70 = compute_intensity(transmitted_70)
    I_reflected_30 = compute_intensity(reflected_30)

    print(f"Transmitted beam (70%):")
    print(f"  Intensity: {I_transmitted_70:.6f}")
    print(f"  Fraction: {I_transmitted_70/I_incident:.4f} (expected: 0.7000)")
    print()

    print(f"Reflected beam (30%):")
    print(f"  Intensity: {I_reflected_30:.6f}")
    print(f"  Fraction: {I_reflected_30/I_incident:.4f} (expected: 0.3000)")
    print()

    is_conserved_70_30, error_70_30 = verify_beam_splitter_energy_conservation(
        I_incident, I_transmitted_70, I_reflected_30
    )

    print(f"Energy conservation:")
    print(f"  I_T + I_R = {I_transmitted_70 + I_reflected_30:.6f}")
    print(f"  I_incident = {I_incident:.6f}")
    print(f"  Relative error: {error_70_30:.6%}")
    print(f"  Status: {'PASS' if is_conserved_70_30 else 'FAIL'}")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY: Optical Components Phase 3")
    print("=" * 80)
    print(f"[+] Beam splitter 50/50: Energy conservation error = {error:.6%}")
    print(f"[+] Mirror reflection: Energy conservation error = {error_mirror:.6%}")
    print(f"[+] Custom 70/30 split: Energy conservation error = {error_70_30:.6%}")
    print()

    all_pass = is_conserved and is_conserved_mirror and is_conserved_70_30
    if all_pass:
        print("[SUCCESS] All optical components validated!")
    else:
        print("[WARNING] Some components failed validation")
    print()
