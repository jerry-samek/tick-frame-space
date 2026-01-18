"""
Tick-Frame Wave Mechanics Module

Implements discrete wave equation evolution and Gaussian wave packets
for interferometry experiments in tick-frame spacetime.

IMPLEMENTATION NOTE:
This module uses CONTINUOUS wave mechanics (complex exponentials, floating-point
amplitudes) as a stopgap to validate interference principles. True tick-frame
representation should use:
  - Discrete integer patterns: [s0, s1, ..., sn-1] (e.g., [1, 0, -1, 0])
  - Discrete phase index: φ ∈ {0, 1, 2, ..., n-1}
  - BigInteger substrate values only (Doc 051)

Rationale: Validate core physics first, then refactor to discrete integers.
TODO: Create discrete_wave_mechanics.py with proper integer representation.

Based on:
- Chapter 7 §4: Discrete wave equations and dispersion
- Experiment #55: Pattern phase representation
- Document 051: Photon as periodic imprint (discrete integer patterns)
- Document 062: Interferometry theoretical framework
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional

# Constants
C = 1.0  # Speed of light (1 cell per tick in natural units)
DX = 1.0  # Spatial step (1 cell = 1 Planck length)
DT = 1.0  # Temporal step (1 tick = 1 Planck time)


@dataclass
class WavePacket:
    """
    Represents a Gaussian wave packet in discrete spacetime.

    Attributes:
        psi: Complex amplitude array (shape: [grid_size] or [grid_x, grid_y])
        k0: Central wave number (radians per cell)
        omega0: Central angular frequency (radians per tick)
        x0: Initial center position
        sigma: Spatial width (coherence length in cells)
        phi0: Initial phase (radians)
        tick: Current tick number
    """
    psi: np.ndarray
    k0: float
    omega0: float
    x0: float
    sigma: float
    phi0: float = 0.0
    tick: int = 0

    @property
    def wavelength(self) -> float:
        """Wavelength in cells."""
        return 2 * np.pi / self.k0 if self.k0 > 0 else np.inf

    @property
    def frequency(self) -> float:
        """Frequency in ticks^-1."""
        return self.omega0 / (2 * np.pi)

    @property
    def energy(self) -> float:
        """Total energy (integral of |psi|^2)."""
        return np.sum(np.abs(self.psi)**2) * DX

    @property
    def center(self) -> float:
        """Center position (center of mass)."""
        intensity = np.abs(self.psi)**2
        x = np.arange(len(self.psi))
        return np.sum(x * intensity) / np.sum(intensity) if np.sum(intensity) > 0 else 0

    @property
    def width(self) -> float:
        """Current spatial width (RMS width)."""
        intensity = np.abs(self.psi)**2
        x = np.arange(len(self.psi))
        x_mean = self.center
        variance = np.sum((x - x_mean)**2 * intensity) / np.sum(intensity)
        return np.sqrt(variance)


def create_gaussian_wave_packet_1d(
    grid_size: int,
    x0: float,
    k0: float,
    sigma: float,
    phi0: float = 0.0
) -> WavePacket:
    """
    Create 1D Gaussian wave packet.

    Parameters:
        grid_size: Number of spatial cells
        x0: Initial center position (cells)
        k0: Central wave number (radians/cell), k0 = 2π/λ
        sigma: Spatial width (coherence length, cells)
        phi0: Initial phase (radians)

    Returns:
        WavePacket object with initialized amplitude

    Formula:
        ψ(x,0) = A₀ × exp(-(x-x₀)²/(2σ²)) × exp(i(k₀x + φ₀))
    """
    x = np.arange(grid_size, dtype=float)

    # Gaussian envelope
    envelope = np.exp(-(x - x0)**2 / (2 * sigma**2))

    # Oscillatory carrier wave
    carrier = np.exp(1j * (k0 * x + phi0))

    # Combined wave packet
    psi = envelope * carrier

    # Normalize (unit energy)
    norm = np.sqrt(np.sum(np.abs(psi)**2) * DX)
    if norm > 0:
        psi /= norm

    # Angular frequency from dispersion relation
    omega0 = dispersion_relation_discrete(k0, DT, DX)

    return WavePacket(
        psi=psi,
        k0=k0,
        omega0=omega0,
        x0=x0,
        sigma=sigma,
        phi0=phi0,
        tick=0
    )


def create_gaussian_wave_packet_2d(
    grid_size: Tuple[int, int],
    x0: Tuple[float, float],
    k0: Tuple[float, float],
    sigma: float,
    phi0: float = 0.0
) -> WavePacket:
    """
    Create 2D Gaussian wave packet.

    Parameters:
        grid_size: (nx, ny) grid dimensions
        x0: (x0, y0) initial center position
        k0: (kx, ky) wave vector components
        sigma: Spatial width (isotropic)
        phi0: Initial phase

    Returns:
        WavePacket object with 2D amplitude array

    Formula:
        ψ(x,y,0) = A₀ × exp(-r²/(2σ²)) × exp(i(k⃗·r⃗ + φ₀))
        where r² = (x-x₀)² + (y-y₀)²
    """
    nx, ny = grid_size
    x = np.arange(nx, dtype=float)
    y = np.arange(ny, dtype=float)
    X, Y = np.meshgrid(x, y, indexing='ij')

    # Distance from center
    r_squared = (X - x0[0])**2 + (Y - x0[1])**2

    # Gaussian envelope
    envelope = np.exp(-r_squared / (2 * sigma**2))

    # Oscillatory carrier
    phase = k0[0] * X + k0[1] * Y + phi0
    carrier = np.exp(1j * phase)

    # Combined wave packet
    psi = envelope * carrier

    # Normalize
    norm = np.sqrt(np.sum(np.abs(psi)**2) * DX**2)
    if norm > 0:
        psi /= norm

    # Angular frequency (magnitude of k vector)
    k_magnitude = np.sqrt(k0[0]**2 + k0[1]**2)
    omega0 = dispersion_relation_discrete(k_magnitude, DT, DX)

    return WavePacket(
        psi=psi,
        k0=k_magnitude,
        omega0=omega0,
        x0=x0[0],  # Store x-component for center tracking
        sigma=sigma,
        phi0=phi0,
        tick=0
    )


def dispersion_relation_discrete(k: float, dt: float = DT, dx: float = DX) -> float:
    """
    Discrete spacetime dispersion relation (Ch7 §4).

    ω(k) = (2/Δt) × sin(k×Δx/2)

    This DIFFERS from continuous dispersion ω = c×k.

    Parameters:
        k: Wave number (radians/cell)
        dt: Temporal step (default 1 tick)
        dx: Spatial step (default 1 cell)

    Returns:
        Angular frequency ω (radians/tick)
    """
    return (2 / dt) * np.sin(k * dx / 2)


def group_velocity_discrete(k: float, dt: float = DT, dx: float = DX) -> float:
    """
    Group velocity from discrete dispersion relation.

    v_group = dω/dk = (Δx/Δt) × cos(k×Δx/2) = c × cos(k×Δx/2)

    For low k (long wavelengths): v_group ≈ c
    For high k (short wavelengths): v_group < c (dispersive!)
    At Nyquist limit k = π/Δx: v_group = 0

    Parameters:
        k: Wave number (radians/cell)
        dt: Temporal step
        dx: Spatial step

    Returns:
        Group velocity (cells/tick)
    """
    return (dx / dt) * np.cos(k * dx / 2)


def evolve_1d_wave_discrete(
    psi_n: np.ndarray,
    psi_n_minus_1: np.ndarray,
    dt: float = DT,
    dx: float = DX
) -> np.ndarray:
    """
    Evolve 1D wave amplitude using discrete wave equation.

    Finite-difference scheme (Ch7 §4):
        A(n+1,i) = 2×A(n,i) - A(n-1,i)
                   + (Δt/Δx)² × [A(n,i+1) + A(n,i-1) - 2×A(n,i)]

    Stability condition: c×Δt/Δx ≤ 1 (Courant condition)

    Parameters:
        psi_n: Wave amplitude at tick n
        psi_n_minus_1: Wave amplitude at tick n-1
        dt: Temporal step
        dx: Spatial step

    Returns:
        psi_n_plus_1: Wave amplitude at tick n+1
    """
    # Courant number (should be ≤ 1 for stability)
    c_squared = (C * dt / dx)**2

    # Laplacian (second spatial derivative)
    # Using periodic boundary conditions
    laplacian = (
        np.roll(psi_n, -1) +  # A(i+1)
        np.roll(psi_n, +1) -  # A(i-1)
        2 * psi_n             # -2×A(i)
    )

    # Time evolution
    psi_n_plus_1 = 2 * psi_n - psi_n_minus_1 + c_squared * laplacian

    return psi_n_plus_1


def evolve_2d_wave_discrete(
    psi_n: np.ndarray,
    psi_n_minus_1: np.ndarray,
    dt: float = DT,
    dx: float = DX
) -> np.ndarray:
    """
    Evolve 2D wave amplitude using discrete wave equation.

    A(n+1,i,j) = 2×A(n,i,j) - A(n-1,i,j)
                 + (Δt/Δx)² × [A(n,i+1,j) + A(n,i-1,j)
                               + A(n,i,j+1) + A(n,i,j-1) - 4×A(n,i,j)]

    Parameters:
        psi_n: Wave amplitude at tick n (2D array)
        psi_n_minus_1: Wave amplitude at tick n-1 (2D array)
        dt: Temporal step
        dx: Spatial step

    Returns:
        psi_n_plus_1: Wave amplitude at tick n+1
    """
    c_squared = (C * dt / dx)**2

    # 2D Laplacian
    laplacian = (
        np.roll(psi_n, -1, axis=0) +  # A(i+1,j)
        np.roll(psi_n, +1, axis=0) +  # A(i-1,j)
        np.roll(psi_n, -1, axis=1) +  # A(i,j+1)
        np.roll(psi_n, +1, axis=1) -  # A(i,j-1)
        4 * psi_n                     # -4×A(i,j)
    )

    # Time evolution
    psi_n_plus_1 = 2 * psi_n - psi_n_minus_1 + c_squared * laplacian

    return psi_n_plus_1


def propagate_wave_packet(
    wave_packet: WavePacket,
    n_ticks: int,
    dimension: int = 1,
    store_history: bool = False
) -> Tuple[WavePacket, Optional[np.ndarray]]:
    """
    Propagate wave packet for n ticks using discrete wave equation.

    Parameters:
        wave_packet: Initial wave packet
        n_ticks: Number of ticks to evolve
        dimension: 1 or 2 (spatial dimensions)
        store_history: If True, return full history array

    Returns:
        wave_packet_final: Wave packet after n ticks
        history: Full evolution history if store_history=True, else None
                 Shape: [n_ticks+1, grid_size] or [n_ticks+1, nx, ny]
    """
    # Initialize history
    if store_history:
        if dimension == 1:
            history = np.zeros((n_ticks + 1, len(wave_packet.psi)), dtype=complex)
        else:
            history = np.zeros((n_ticks + 1,) + wave_packet.psi.shape, dtype=complex)
        history[0] = wave_packet.psi
    else:
        history = None

    # Initialize psi at tick 0 and -1 (assume psi[-1] = psi[0] for first step)
    psi_n_minus_1 = wave_packet.psi.copy()
    psi_n = wave_packet.psi.copy()

    # Select evolution function
    evolve_func = evolve_1d_wave_discrete if dimension == 1 else evolve_2d_wave_discrete

    # Evolve
    for tick in range(n_ticks):
        psi_n_plus_1 = evolve_func(psi_n, psi_n_minus_1)

        # Update for next iteration
        psi_n_minus_1 = psi_n
        psi_n = psi_n_plus_1

        # Store if requested
        if store_history:
            history[tick + 1] = psi_n

    # Create final wave packet
    wave_packet_final = WavePacket(
        psi=psi_n,
        k0=wave_packet.k0,
        omega0=wave_packet.omega0,
        x0=wave_packet.x0,
        sigma=wave_packet.sigma,
        phi0=wave_packet.phi0,
        tick=wave_packet.tick + n_ticks
    )

    return wave_packet_final, history


def measure_group_velocity(
    wave_packet_initial: WavePacket,
    wave_packet_final: WavePacket,
    n_ticks: int
) -> float:
    """
    Measure group velocity from center-of-mass displacement.

    v_group = (x_final - x_initial) / n_ticks

    Parameters:
        wave_packet_initial: Wave packet at start
        wave_packet_final: Wave packet after propagation
        n_ticks: Number of ticks elapsed

    Returns:
        v_group: Measured group velocity (cells/tick)
    """
    x_initial = wave_packet_initial.center
    x_final = wave_packet_final.center

    v_group = (x_final - x_initial) / n_ticks

    return v_group


def compute_intensity(psi: np.ndarray) -> np.ndarray:
    """
    Compute intensity distribution I = |ψ|².

    Parameters:
        psi: Complex amplitude

    Returns:
        I: Intensity (real, non-negative)
    """
    return np.abs(psi)**2


def compute_phase(psi: np.ndarray) -> np.ndarray:
    """
    Extract phase from complex amplitude.

    φ = arg(ψ) = arctan2(Im(ψ), Re(ψ))

    Parameters:
        psi: Complex amplitude

    Returns:
        phi: Phase in radians [-π, π]
    """
    return np.angle(psi)


def superpose_wave_packets(
    wave_packet_A: WavePacket,
    wave_packet_B: WavePacket
) -> WavePacket:
    """
    Superpose two wave packets (simple addition).

    ψ_total = ψ_A + ψ_B

    Intensity: I_total = |ψ_A + ψ_B|²
                       = |ψ_A|² + |ψ_B|² + 2Re(ψ_A* ψ_B)
                       = I_A + I_B + 2√(I_A I_B) cos(φ_B - φ_A)  ← INTERFERENCE

    Parameters:
        wave_packet_A: First wave packet
        wave_packet_B: Second wave packet (must have same grid size)

    Returns:
        wave_packet_total: Superposed wave packet
    """
    assert wave_packet_A.psi.shape == wave_packet_B.psi.shape, \
        "Wave packets must have same grid size for superposition"

    # Superpose amplitudes
    psi_total = wave_packet_A.psi + wave_packet_B.psi

    # Combined wave number (average, approximate)
    k0_total = (wave_packet_A.k0 + wave_packet_B.k0) / 2
    omega0_total = (wave_packet_A.omega0 + wave_packet_B.omega0) / 2

    # Create combined wave packet
    wave_packet_total = WavePacket(
        psi=psi_total,
        k0=k0_total,
        omega0=omega0_total,
        x0=(wave_packet_A.x0 + wave_packet_B.x0) / 2,
        sigma=max(wave_packet_A.sigma, wave_packet_B.sigma),
        phi0=0.0,  # Phase no longer well-defined for superposition
        tick=max(wave_packet_A.tick, wave_packet_B.tick)
    )

    return wave_packet_total


def compute_fringe_visibility(
    intensity_max: float,
    intensity_min: float
) -> float:
    """
    Compute fringe visibility (contrast).

    V = (I_max - I_min) / (I_max + I_min)

    V = 1.0: Perfect interference (ideal coherence)
    V = 0.0: No interference (incoherent)

    Parameters:
        intensity_max: Maximum intensity in fringe pattern
        intensity_min: Minimum intensity in fringe pattern

    Returns:
        V: Visibility [0, 1]
    """
    if intensity_max + intensity_min == 0:
        return 0.0

    V = (intensity_max - intensity_min) / (intensity_max + intensity_min)
    return V


def nyquist_frequency(dt: float = DT) -> float:
    """
    Nyquist frequency limit in discrete spacetime.

    f_max = 1 / (2×Δt) ≈ 9.3×10⁴² Hz (for Planck time)

    Waves with f > f_max will alias to lower frequencies.

    Parameters:
        dt: Temporal step (Planck time)

    Returns:
        f_max: Nyquist frequency (ticks⁻¹)
    """
    return 1 / (2 * dt)


def nyquist_wave_number(dx: float = DX) -> float:
    """
    Nyquist wave number limit.

    k_max = π / Δx

    Waves with k > k_max alias to k' = 2π/Δx - k.

    Parameters:
        dx: Spatial step (Planck length)

    Returns:
        k_max: Nyquist wave number (radians/cell)
    """
    return np.pi / dx


# Utility functions for analysis

def energy_conservation_check(
    wave_packet_initial: WavePacket,
    wave_packet_final: WavePacket,
    tolerance: float = 0.01
) -> Tuple[bool, float]:
    """
    Check if energy is conserved during propagation.

    E = ∫|ψ|² dx should be constant.

    Parameters:
        wave_packet_initial: Wave packet at start
        wave_packet_final: Wave packet after propagation
        tolerance: Acceptable relative error (default 1%)

    Returns:
        conserved: True if energy conserved within tolerance
        relative_error: |E_final - E_initial| / E_initial
    """
    E_initial = wave_packet_initial.energy
    E_final = wave_packet_final.energy

    if E_initial == 0:
        return True, 0.0

    relative_error = abs(E_final - E_initial) / E_initial
    conserved = relative_error < tolerance

    return conserved, relative_error


def coherence_length(wave_packet: WavePacket) -> float:
    """
    Estimate coherence length from wave packet width.

    L_coherence ≈ 2σ (spatial extent of coherent oscillations)

    Parameters:
        wave_packet: Wave packet

    Returns:
        L_coherence: Coherence length (cells)
    """
    return 2 * wave_packet.width


def dispersion_check(
    k_values: np.ndarray,
    v_group_measured: np.ndarray,
    dt: float = DT,
    dx: float = DX
) -> Tuple[float, float]:
    """
    Check if measured group velocities match discrete dispersion relation.

    v_group_theory(k) = c × cos(k×Δx/2)

    Parameters:
        k_values: Array of wave numbers
        v_group_measured: Measured group velocities
        dt: Temporal step
        dx: Spatial step

    Returns:
        correlation: Pearson correlation coefficient (r)
        rms_error: Root mean square error
    """
    # Theoretical prediction
    v_group_theory = np.array([group_velocity_discrete(k, dt, dx) for k in k_values])

    # Correlation
    correlation = np.corrcoef(v_group_measured, v_group_theory)[0, 1]

    # RMS error
    rms_error = np.sqrt(np.mean((v_group_measured - v_group_theory)**2))

    return correlation, rms_error


if __name__ == "__main__":
    # Quick test: Create and propagate wave packet
    print("=" * 60)
    print("Tick-Frame Wave Mechanics - Quick Test")
    print("=" * 60)

    # Create 1D Gaussian wave packet
    print("\nCreating 1D Gaussian wave packet...")
    lambda_0 = 100  # wavelength in cells
    k0 = 2 * np.pi / lambda_0
    sigma = 20  # width in cells
    x0 = 500  # center position

    wave_packet = create_gaussian_wave_packet_1d(
        grid_size=2000,
        x0=x0,
        k0=k0,
        sigma=sigma
    )

    print(f"  Wavelength: {wave_packet.wavelength:.2f} cells")
    print(f"  Initial center: {wave_packet.center:.2f}")
    print(f"  Initial width: {wave_packet.width:.2f}")
    print(f"  Initial energy: {wave_packet.energy:.6f}")

    # Propagate
    print("\nPropagating 1000 ticks...")
    wave_packet_final, _ = propagate_wave_packet(wave_packet, n_ticks=1000)

    print(f"  Final center: {wave_packet_final.center:.2f}")
    print(f"  Final width: {wave_packet_final.width:.2f}")
    print(f"  Final energy: {wave_packet_final.energy:.6f}")

    # Measure group velocity
    v_group_measured = measure_group_velocity(wave_packet, wave_packet_final, 1000)
    v_group_theory = group_velocity_discrete(k0)

    print(f"\nGroup velocity:")
    print(f"  Measured: {v_group_measured:.6f} cells/tick")
    print(f"  Theory:   {v_group_theory:.6f} cells/tick")
    print(f"  Error:    {abs(v_group_measured - v_group_theory)/v_group_theory * 100:.2f}%")

    # Energy conservation
    conserved, rel_error = energy_conservation_check(wave_packet, wave_packet_final)
    print(f"\nEnergy conservation:")
    print(f"  Conserved: {conserved}")
    print(f"  Relative error: {rel_error * 100:.4f}%")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
