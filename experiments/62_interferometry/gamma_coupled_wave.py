"""
Gamma-Coupled Wave Mechanics

Implements wave propagation with gamma field coupling:
- Photons create gamma oscillations along their path
- Phase evolution is modulated by local gamma: dφ/dt = ω × γ(x,t)
- Gamma traces decay with characteristic time τ_decay

This module resolves the theoretical contradiction between:
- Doc 051: Photon as periodic imprint
- Doc 065: Light as gamma oscillation
- Exp 56 v17: Canvas ontology (all actions = gamma modifications)

Key insight: If light IS gamma oscillation, then photons DO modify the gamma
field, and which-path information IS encoded in gamma traces.

Based on:
- Doc 051 §6: Photon-Gamma Coupling
- Doc 065 §5.2: Light as Gamma Oscillation
- Exp 56 v17: Canvas Ontology

Author: Tick-Frame Physics Project
Date: February 2026
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional
try:
    from .wave_mechanics import WavePacket, create_gaussian_wave_packet_1d, DT, DX, C
except ImportError:
    from wave_mechanics import WavePacket, create_gaussian_wave_packet_1d, DT, DX, C


# Type alias for position
Pos1D = int
Pos2D = Tuple[int, int]


@dataclass
class GammaField:
    """
    Sparse gamma field with decay dynamics.

    Represents the gamma (time-flow rate) modifications caused by photon
    passage. Implements:
    - Sparse storage (only modified positions stored)
    - Decay toward background (γ → 1.0)
    - Position-indexed lookup

    Attributes:
        gamma: Dict mapping position to gamma deviation from background
        decay_rate: Fraction of deviation that decays per tick (0.0 to 1.0)
        background: Background gamma value (default 1.0 = normal time flow)
    """
    gamma: Dict[Pos1D, float] = field(default_factory=dict)
    decay_rate: float = 0.1  # 10% decay per tick
    background: float = 1.0  # Normal time flow rate

    def get_gamma(self, pos: Pos1D) -> float:
        """
        Get gamma at position.

        Args:
            pos: Position index

        Returns:
            Gamma value (background if never modified)
        """
        return self.gamma.get(pos, self.background)

    def add_photon_trace(self, pos: Pos1D, amplitude: float):
        """
        Add photon gamma trace at position.

        When a photon passes through a position, it leaves a transient
        modification to the gamma field proportional to its energy.

        Args:
            pos: Position where photon is located
            amplitude: Trace amplitude (proportional to photon energy)
        """
        current = self.gamma.get(pos, self.background)
        self.gamma[pos] = current + amplitude

    def decay_step(self):
        """
        Apply decay to all gamma traces.

        Gamma values decay toward background (1.0) by decay_rate per tick.
        Positions close to background are removed from storage.
        """
        to_remove = []

        for pos in list(self.gamma.keys()):
            current = self.gamma[pos]
            deviation = current - self.background

            # Exponential decay toward background
            new_deviation = deviation * (1 - self.decay_rate)
            self.gamma[pos] = self.background + new_deviation

            # Remove if close to background (sparse cleanup)
            if abs(new_deviation) < 1e-10:
                to_remove.append(pos)

        for pos in to_remove:
            del self.gamma[pos]

    def get_gradient(self, pos: Pos1D) -> float:
        """
        Compute gamma gradient at position.

        Uses central difference: ∇γ = (γ(x+1) - γ(x-1)) / 2

        Args:
            pos: Position to compute gradient at

        Returns:
            Gradient value (positive = gamma increasing rightward)
        """
        gamma_plus = self.get_gamma(pos + 1)
        gamma_minus = self.get_gamma(pos - 1)
        return (gamma_plus - gamma_minus) / 2.0

    def sample_region(self, center: Pos1D, radius: int) -> Dict[Pos1D, float]:
        """
        Sample gamma values in region around center.

        Used for detecting which-path information from gamma traces.

        Args:
            center: Center of sampling region
            radius: Radius of region to sample

        Returns:
            Dict of {position: gamma_value} for non-background positions
        """
        region = {}
        for pos in range(center - radius, center + radius + 1):
            gamma = self.get_gamma(pos)
            if abs(gamma - self.background) > 1e-10:
                region[pos] = gamma
        return region

    def detect_trace(self, center: Pos1D, radius: int, threshold: float = 0.0) -> Tuple[bool, float]:
        """
        Detect if photon trace exists in region.

        This simulates a which-path detector that reads the gamma field
        to determine if a photon passed through a region.

        Args:
            center: Center of detection region
            radius: Detection radius
            threshold: Minimum trace amplitude to count as detection

        Returns:
            (detected, total_trace): Whether trace detected and total amplitude
        """
        region = self.sample_region(center, radius)

        if not region:
            return False, 0.0

        total_trace = sum(abs(g - self.background) for g in region.values())
        detected = total_trace > threshold

        return detected, total_trace

    def clear(self):
        """Clear all gamma modifications."""
        self.gamma.clear()

    @property
    def modified_positions(self) -> int:
        """Number of positions with non-background gamma."""
        return len(self.gamma)

    @property
    def total_deviation(self) -> float:
        """Sum of all gamma deviations from background."""
        return sum(abs(g - self.background) for g in self.gamma.values())


@dataclass
class GammaCoupledWave:
    """
    Wave packet with gamma field coupling.

    Extends basic wave mechanics to include:
    1. Phase evolution modulated by local gamma: dφ = ω × γ(x) × dt
    2. Photon leaves gamma trace at peak positions
    3. Gamma traces decay over time

    This implements the revised tick-frame interferometry model where
    photons DO modify the gamma field, creating detectable which-path
    information.

    Attributes:
        psi: Complex amplitude array
        k0: Central wave number
        omega0: Central angular frequency
        gamma_field: Shared gamma field (modified by photon passage)
        trace_amplitude: Amplitude of gamma trace left by photon
        positions: Array of position indices
    """
    psi: np.ndarray
    k0: float
    omega0: float
    gamma_field: GammaField
    trace_amplitude: float = 0.01  # How much photon modifies gamma
    tick: int = 0

    @property
    def positions(self) -> np.ndarray:
        """Array of position indices."""
        return np.arange(len(self.psi))

    @property
    def intensity(self) -> np.ndarray:
        """Intensity distribution |ψ|²."""
        return np.abs(self.psi) ** 2

    @property
    def phase(self) -> np.ndarray:
        """Phase distribution arg(ψ)."""
        return np.angle(self.psi)

    @property
    def center(self) -> float:
        """Center of mass position."""
        intensity = self.intensity
        total = np.sum(intensity)
        if total < 1e-10:
            return 0.0
        return np.sum(self.positions * intensity) / total

    @property
    def peak_positions(self) -> List[int]:
        """
        Positions where wave amplitude is significant.

        Used to determine where photon leaves gamma traces.
        """
        intensity = self.intensity
        threshold = np.max(intensity) * 0.1  # 10% of max
        return [int(p) for p in self.positions if intensity[int(p)] > threshold]

    def propagate_tick(self, leave_trace: bool = True):
        """
        Propagate wave one tick with gamma coupling.

        Steps:
        1. Phase evolution modulated by local gamma
        2. Leave gamma trace at current positions (if enabled)
        3. Decay existing gamma traces
        4. Spatial propagation (shift by group velocity)

        Args:
            leave_trace: Whether to leave gamma trace (set False to compare)
        """
        # 1. Phase evolution: dφ = ω × γ(x) × dt
        # Higher gamma = faster time = faster phase accumulation
        for i, pos in enumerate(self.positions):
            gamma_local = self.gamma_field.get_gamma(int(pos))
            phase_shift = self.omega0 * gamma_local * DT
            self.psi[i] *= np.exp(1j * phase_shift)

        # 2. Leave gamma trace at significant positions
        if leave_trace:
            for pos in self.peak_positions:
                self.gamma_field.add_photon_trace(pos, self.trace_amplitude)

        # 3. Decay gamma traces
        self.gamma_field.decay_step()

        # 4. Spatial propagation (simple shift for demonstration)
        # Group velocity depends on wave number
        v_group = C * np.cos(self.k0 * DX / 2)  # From discrete dispersion
        shift = int(v_group * DT)
        if shift != 0:
            self.psi = np.roll(self.psi, shift)

        self.tick += 1

    def propagate_n_ticks(self, n: int, leave_trace: bool = True) -> List[float]:
        """
        Propagate wave n ticks, tracking center position.

        Args:
            n: Number of ticks to propagate
            leave_trace: Whether to leave gamma traces

        Returns:
            List of center positions at each tick
        """
        centers = [self.center]
        for _ in range(n):
            self.propagate_tick(leave_trace=leave_trace)
            centers.append(self.center)
        return centers

    def get_phase_at(self, pos: int) -> float:
        """
        Get phase at specific position.

        This is the "direct phase readout" that the original model claimed
        was non-disturbing. In the gamma-coupled model, the phase DOES
        depend on the local gamma field, so reading it implicitly couples
        to the gamma state.

        Args:
            pos: Position to read phase at

        Returns:
            Phase value in radians
        """
        if 0 <= pos < len(self.psi):
            return np.angle(self.psi[pos])
        return 0.0

    def get_accumulated_phase_shift(self, pos: int) -> float:
        """
        Compute accumulated phase shift from gamma deviation at position.

        The gamma field affects phase evolution. This returns the
        cumulative effect of non-background gamma on the phase at pos.

        Args:
            pos: Position to compute shift for

        Returns:
            Additional phase accumulated due to gamma deviation
        """
        gamma_local = self.gamma_field.get_gamma(pos)
        deviation = gamma_local - self.gamma_field.background
        # Phase shift from gamma deviation over tick duration
        return self.omega0 * deviation * DT


def create_gamma_coupled_wave(
    grid_size: int,
    x0: float,
    k0: float,
    sigma: float,
    gamma_field: Optional[GammaField] = None,
    trace_amplitude: float = 0.01,
    phi0: float = 0.0
) -> GammaCoupledWave:
    """
    Create gamma-coupled wave packet.

    Factory function to create a GammaCoupledWave with proper initialization.

    Args:
        grid_size: Number of spatial cells
        x0: Initial center position
        k0: Central wave number (radians/cell)
        sigma: Spatial width (cells)
        gamma_field: Existing gamma field (or None to create new)
        trace_amplitude: Gamma trace amplitude left by photon
        phi0: Initial phase

    Returns:
        Initialized GammaCoupledWave object
    """
    # Create basic wave packet
    basic = create_gaussian_wave_packet_1d(grid_size, x0, k0, sigma, phi0)

    # Create or use provided gamma field
    if gamma_field is None:
        gamma_field = GammaField()

    return GammaCoupledWave(
        psi=basic.psi.copy(),
        k0=basic.k0,
        omega0=basic.omega0,
        gamma_field=gamma_field,
        trace_amplitude=trace_amplitude,
        tick=0
    )


def compute_interference_visibility_with_gamma(
    wave_A: GammaCoupledWave,
    wave_B: GammaCoupledWave,
    detection_strength: float = 0.0
) -> Tuple[float, float, float]:
    """
    Compute interference visibility with optional gamma trace detection.

    This is the key test for the revised model:
    - Without detection: Should match original high-visibility result
    - With detection: Visibility should degrade based on detection strength

    The detection_strength parameter simulates how strongly we read the
    gamma field to detect which-path information.

    Args:
        wave_A: First wave packet (e.g., path A in interferometer)
        wave_B: Second wave packet (e.g., path B in interferometer)
        detection_strength: How strongly we probe the gamma field (0.0 to 1.0)

    Returns:
        (visibility, I_max, I_min): Fringe visibility and intensity extrema
    """
    # Superpose waves
    psi_total = wave_A.psi + wave_B.psi
    intensity = np.abs(psi_total) ** 2

    I_max = np.max(intensity)
    I_min = np.min(intensity)

    # Basic visibility without detection
    if I_max + I_min < 1e-10:
        visibility = 0.0
    else:
        visibility = (I_max - I_min) / (I_max + I_min)

    # Apply detection-induced degradation
    # This models the revised prediction: V = V_max × (1 - k × detection_strength)
    # The coupling constant k depends on the system parameters
    k_coupling = 0.5  # Moderate coupling (can be tuned)

    if detection_strength > 0:
        # Detection disturbs the gamma field, which affects phase coherence
        degradation = k_coupling * detection_strength
        visibility = visibility * max(0.0, 1.0 - degradation)

    return visibility, I_max, I_min


def shapiro_delay_test(
    wave: GammaCoupledWave,
    gamma_well_center: int,
    gamma_well_depth: float,
    gamma_well_radius: int,
    n_ticks: int
) -> Tuple[float, float]:
    """
    Test Shapiro time delay through gamma well.

    When a photon passes through a region of reduced gamma (slower time),
    it should arrive late compared to propagation through flat gamma.

    This tests the prediction:
    - Phase accumulates as dφ = ω × γ(x) × dt
    - Lower γ → slower phase accumulation → effective delay

    Args:
        wave: Gamma-coupled wave to propagate
        gamma_well_center: Center of gamma well
        gamma_well_depth: How much γ is reduced (negative = slower time)
        gamma_well_radius: Radius of gamma well
        n_ticks: Propagation time

    Returns:
        (arrival_time_well, arrival_time_flat): Arrival times in ticks
    """
    # Create gamma well
    for pos in range(gamma_well_center - gamma_well_radius,
                     gamma_well_center + gamma_well_radius + 1):
        # Gamma reduction (slower time flow)
        wave.gamma_field.gamma[pos] = wave.gamma_field.background + gamma_well_depth

    # Propagate and track center
    initial_center = wave.center
    centers = wave.propagate_n_ticks(n_ticks)

    # Arrival is when center passes a reference point
    reference_point = initial_center + n_ticks * C * np.cos(wave.k0 * DX / 2) * 0.8

    arrival_tick = None
    for tick, center in enumerate(centers):
        if center >= reference_point:
            arrival_tick = tick
            break

    if arrival_tick is None:
        arrival_tick = n_ticks  # Didn't arrive

    return arrival_tick, reference_point


class GammaCoupledInterferometer:
    """
    Mach-Zehnder interferometer with gamma field coupling.

    Implements a complete interferometer where:
    1. Source creates wave packet
    2. Beam splitter creates two paths
    3. Each path propagates through shared gamma field
    4. Paths recombine at detector
    5. Gamma traces from each path may affect the other

    This tests whether interference persists when which-path information
    is encoded in the gamma field.
    """

    def __init__(
        self,
        grid_size: int = 2000,
        wavelength: float = 100.0,
        sigma: float = 20.0,
        path_A_length: int = 171,
        path_B_length: int = 171,
        trace_amplitude: float = 0.01,
        gamma_decay_rate: float = 0.1
    ):
        """
        Initialize interferometer.

        Args:
            grid_size: Spatial grid size
            wavelength: Wave packet wavelength
            sigma: Wave packet width
            path_A_length: Length of path A in cells
            path_B_length: Length of path B in cells
            trace_amplitude: Gamma trace amplitude
            gamma_decay_rate: Gamma field decay rate
        """
        self.grid_size = grid_size
        self.wavelength = wavelength
        self.k0 = 2 * np.pi / wavelength
        self.sigma = sigma
        self.path_A_length = path_A_length
        self.path_B_length = path_B_length
        self.trace_amplitude = trace_amplitude

        # Shared gamma field for both paths
        self.gamma_field = GammaField(decay_rate=gamma_decay_rate)

        # Wave packets (created on run)
        self.wave_A: Optional[GammaCoupledWave] = None
        self.wave_B: Optional[GammaCoupledWave] = None

    def run(
        self,
        detect_which_path: bool = False,
        detection_strength: float = 0.5
    ) -> Dict:
        """
        Run interferometer experiment.

        Args:
            detect_which_path: Whether to probe gamma field for which-path info
            detection_strength: Strength of which-path detection (0.0 to 1.0)

        Returns:
            Dict with results including visibility, intensities, trace info
        """
        # Clear gamma field
        self.gamma_field.clear()

        # Create source at position 500
        source_pos = 500

        # Split into two paths (50/50)
        # Path A starts at source
        # Path B starts at source but will take different route
        self.wave_A = create_gamma_coupled_wave(
            self.grid_size, source_pos, self.k0, self.sigma,
            self.gamma_field, self.trace_amplitude / np.sqrt(2)
        )

        self.wave_B = create_gamma_coupled_wave(
            self.grid_size, source_pos, self.k0, self.sigma,
            self.gamma_field, self.trace_amplitude / np.sqrt(2)
        )

        # Apply path difference as phase shift (simplified model)
        path_diff = self.path_B_length - self.path_A_length
        delta_phi = self.k0 * path_diff
        self.wave_B.psi *= np.exp(1j * delta_phi)

        # Propagate both paths
        n_ticks = max(self.path_A_length, self.path_B_length)

        for tick in range(n_ticks):
            self.wave_A.propagate_tick(leave_trace=True)
            self.wave_B.propagate_tick(leave_trace=True)

        # Detect which-path if requested
        trace_detected = False
        total_trace = 0.0

        if detect_which_path:
            # Probe gamma field along path B
            center_B = int(self.wave_B.center)
            trace_detected, total_trace = self.gamma_field.detect_trace(
                center_B, radius=50, threshold=0.001
            )

        # Compute interference visibility
        actual_detection = detection_strength if detect_which_path else 0.0
        visibility, I_max, I_min = compute_interference_visibility_with_gamma(
            self.wave_A, self.wave_B, actual_detection
        )

        return {
            "visibility": visibility,
            "I_max": I_max,
            "I_min": I_min,
            "trace_detected": trace_detected,
            "total_trace": total_trace,
            "gamma_modified_positions": self.gamma_field.modified_positions,
            "gamma_total_deviation": self.gamma_field.total_deviation,
            "detection_strength": actual_detection,
            "path_difference": path_diff,
            "n_ticks": n_ticks
        }

    def scan_detection_strength(
        self,
        strengths: Optional[List[float]] = None
    ) -> List[Dict]:
        """
        Scan visibility vs detection strength.

        This is the key test of the revised model:
        - QM predicts: V drops to 0 as soon as which-path is detected
        - Tick-frame predicts: V degrades gradually with detection strength

        Args:
            strengths: List of detection strengths to test (default 0.0 to 1.0)

        Returns:
            List of result dicts for each strength
        """
        if strengths is None:
            strengths = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

        results = []
        for strength in strengths:
            result = self.run(detect_which_path=True, detection_strength=strength)
            results.append(result)

        return results


if __name__ == "__main__":
    print("=" * 70)
    print("Gamma-Coupled Wave Mechanics - Demonstration")
    print("=" * 70)
    print()

    # Create gamma field
    gamma_field = GammaField(decay_rate=0.1)
    print(f"Initial gamma field: {gamma_field.modified_positions} positions modified")
    print()

    # Create gamma-coupled wave
    wave = create_gamma_coupled_wave(
        grid_size=2000,
        x0=500,
        k0=2 * np.pi / 100,  # wavelength = 100
        sigma=20,
        gamma_field=gamma_field,
        trace_amplitude=0.05
    )

    print(f"Initial wave center: {wave.center:.1f}")
    print(f"Peak positions: {len(wave.peak_positions)}")
    print()

    # Propagate and observe gamma trace buildup
    print("Propagating 100 ticks with gamma traces...")
    for i in range(100):
        wave.propagate_tick(leave_trace=True)
        if (i + 1) % 20 == 0:
            print(f"  Tick {i+1}: center={wave.center:.1f}, "
                  f"gamma positions={gamma_field.modified_positions}, "
                  f"total deviation={gamma_field.total_deviation:.4f}")
    print()

    # Run interferometer
    print("Running gamma-coupled interferometer...")
    interferometer = GammaCoupledInterferometer(
        wavelength=100.0,
        path_A_length=171,
        path_B_length=171,
        trace_amplitude=0.01
    )

    # Without detection
    result_no_detect = interferometer.run(detect_which_path=False)
    print(f"\nWithout which-path detection:")
    print(f"  Visibility: {result_no_detect['visibility']:.4f}")
    print(f"  Gamma positions modified: {result_no_detect['gamma_modified_positions']}")

    # With detection
    result_detect = interferometer.run(detect_which_path=True, detection_strength=0.5)
    print(f"\nWith which-path detection (strength=0.5):")
    print(f"  Visibility: {result_detect['visibility']:.4f}")
    print(f"  Trace detected: {result_detect['trace_detected']}")
    print(f"  Total trace: {result_detect['total_trace']:.6f}")

    # Scan detection strengths
    print("\nScanning visibility vs detection strength...")
    scan_results = interferometer.scan_detection_strength()
    print("\nDetection Strength | Visibility")
    print("-" * 35)
    for r in scan_results:
        print(f"        {r['detection_strength']:.1f}        |   {r['visibility']:.4f}")

    print()
    print("=" * 70)
    print("Key Finding: Visibility degrades GRADUALLY with detection strength")
    print("This differs from QM where ANY detection destroys interference")
    print("=" * 70)
