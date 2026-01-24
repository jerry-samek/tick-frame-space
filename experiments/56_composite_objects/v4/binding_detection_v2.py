#!/usr/bin/env python3
"""
Binding Detection V2 for Experiment 56 Phase 4

PHASE 4 CHANGES:
- Gradient-following dynamics (replaces frozen orbits)
- Velocity-dependent source terms
- Dynamic γ-field recomputation as constituents move

Implements γ-well field computation and binding detection for composite objects.
Adapts field dynamics from Experiment 51 v10/v11 with full gradient-following.
"""

import numpy as np
from typing import List, Tuple, Optional
from scipy.ndimage import laplace
import math


# ============================================================================
# Physics Utilities (from v10)
# ============================================================================

def lorentz_gamma(velocity: np.ndarray, c: float = 1.0) -> float:
    """
    Compute Lorentz gamma factor for given velocity.

    gamma = 1 / sqrt(1 - v^2/c^2)

    Args:
        velocity: (vx, vy) velocity vector
        c: Speed of light (default 1.0)

    Returns:
        Lorentz gamma factor (>= 1.0)
    """
    v_squared = np.dot(velocity, velocity)
    v_over_c_squared = v_squared / (c**2)

    # Clamp to avoid numerical issues near v = c
    if v_over_c_squared >= 0.9999:
        v_over_c_squared = 0.9999

    gamma = 1.0 / math.sqrt(1.0 - v_over_c_squared)
    return gamma


def compute_gamma_gradient(
    position: np.ndarray,
    gamma_field: np.ndarray,
    grid_size: int = 100,
    dx: float = 1.0
) -> np.ndarray:
    """
    Compute gradient of gamma field at given position.

    Uses finite difference approximation:
    ∇γ ≈ (γ(x+dx) - γ(x-dx)) / (2*dx)

    Args:
        position: (x, y) position
        gamma_field: 2D array of gamma values
        grid_size: Size of grid
        dx: Grid spacing

    Returns:
        (grad_x, grad_y) gradient vector as numpy array
    """
    x, y = position
    ix = int(x)
    iy = int(y)

    # Boundary handling
    ix = np.clip(ix, 1, grid_size - 2)
    iy = np.clip(iy, 1, grid_size - 2)

    # Finite difference gradient (central difference)
    grad_x = (gamma_field[ix + 1, iy] - gamma_field[ix - 1, iy]) / (2 * dx)
    grad_y = (gamma_field[ix, iy + 1] - gamma_field[ix, iy - 1]) / (2 * dx)

    return np.array([grad_x, grad_y], dtype=float)


# ============================================================================
# Pattern Class (adapted from composite_structure.py)
# ============================================================================

class Pattern:
    """Pattern representing a particle (proton, electron, neutron)."""
    def __init__(self, pattern_type: str, energy: float, mass: float):
        self.pattern_type = pattern_type
        self.energy = energy
        self.mass = mass


# ============================================================================
# Gamma-Well Detector (V2 with Gradient-Following)
# ============================================================================

class GammaWellDetector:
    """
    Detects and analyzes γ-wells (time-flow minima) created by particles.

    V2 CHANGES:
    - compute_gamma_gradient() for gradient-following dynamics
    - Velocity-dependent source terms
    - Dynamic field updates as particles move
    """

    def __init__(
        self,
        grid_size: int = 100,
        alpha: float = 0.012,       # Diffusion coefficient for load field
        gamma_damp: float = 0.0005, # Nonlinear damping for load field
        scale: float = 0.75,        # Source strength scaling
        R: float = 1.2,             # Energy regeneration rate
        D: float = 0.01,            # Load-dependent drainage
        E_max: float = 15.0,        # Maximum energy capacity
        capacity_min: float = 0.1,  # Minimum effective capacity
        work_threshold: float = 0.5,# Minimum energy for work
        c: float = 1.0              # Speed of light
    ):
        """
        Initialize γ-well detector with field parameters.

        Parameters use defaults from Experiment 51 v11 baseline config.
        """
        self.grid_size = grid_size

        # Field parameters
        self.alpha = alpha
        self.gamma_damp = gamma_damp
        self.scale = scale
        self.R = R
        self.D = D
        self.E_max = E_max
        self.capacity_min = capacity_min
        self.work_threshold = work_threshold
        self.c = c

        # Field state
        self.L = np.zeros((grid_size, grid_size), dtype=float)  # Load field
        self.E = np.ones((grid_size, grid_size), dtype=float) * E_max  # Energy field

        # Derived γ-field (computed on demand)
        self._gamma_cache = None
        self._gamma_dirty = True

    def compute_source_from_patterns(
        self,
        patterns: List[Tuple[Pattern, np.ndarray, np.ndarray]]
    ) -> np.ndarray:
        """
        Compute source field S(x) from list of patterns, positions, and velocities.

        V2 CHANGE: Now includes velocity-dependent corrections!
        S = scale × mass × (energy / E_max) × (1 + v²/c²) × γ_SR

        Args:
            patterns: List of (Pattern, position, velocity) tuples
                     position is (x, y) in grid coordinates
                     velocity is (vx, vy) in units of c

        Returns:
            Source field S as (grid_size, grid_size) array
        """
        S = np.zeros((self.grid_size, self.grid_size), dtype=float)

        for pattern, position, velocity in patterns:
            ix = int(position[0]) % self.grid_size
            iy = int(position[1]) % self.grid_size

            # Base source strength: mass × energy / E_max
            base_contribution = pattern.mass * (pattern.energy / self.E_max)

            # V2 ADDITION: Velocity corrections
            v_squared = np.dot(velocity, velocity)
            gamma_SR = lorentz_gamma(velocity, self.c)

            # Full velocity-dependent source (from v11)
            velocity_factor = (1.0 + v_squared / (self.c ** 2)) * gamma_SR

            contribution = base_contribution * velocity_factor
            S[ix, iy] += self.scale * contribution

        return S

    def update_fields(
        self,
        patterns: List[Tuple[Pattern, np.ndarray, np.ndarray]],
        dt: float = 1.0,
        num_steps: int = 100
    ):
        """
        Evolve load and energy fields to steady state with given patterns.

        V2 CHANGE: Now accepts velocity as third element in pattern tuples

        Args:
            patterns: List of (Pattern, position, velocity) tuples
            dt: Time step for field evolution
            num_steps: Number of evolution steps to reach steady state
        """
        # Compute source term from patterns (with velocity corrections)
        S = self.compute_source_from_patterns(patterns)

        # Evolve fields to steady state
        for _ in range(num_steps):
            # Update load field (reaction-diffusion)
            laplacian_L = laplace(self.L)
            dL_dt = self.alpha * laplacian_L + S - self.gamma_damp * (self.L ** 2)
            self.L = self.L + dt * dL_dt
            self.L = np.maximum(self.L, 0.0)  # Ensure non-negative

            # Update energy field (regeneration-drainage)
            dE_dt = self.R - self.D * self.L
            self.E = self.E + dt * dE_dt
            self.E = np.clip(self.E, 0.0, self.E_max)  # Clamp to [0, E_max]

        # Mark γ-field for recomputation
        self._gamma_dirty = True

    def compute_gamma_field(self) -> np.ndarray:
        """
        Compute γ-field (gravitational time dilation) from current L and E fields.

        gamma_grav = 1 / capacity_eff
        capacity_eff = capacity_from_load × capacity_from_energy

        Returns:
            Gamma field as (grid_size, grid_size) array
            Values >= 1.0, where higher γ = slower time = deeper well
        """
        # Capacity from load (saturation effect)
        # High load → low capacity → high gamma (time dilation)
        capacity_from_load = 1.0 / (1.0 + self.L)

        # Capacity from energy (availability effect)
        # Low energy → low capacity → high gamma
        capacity_from_energy = self.E / (self.E + self.work_threshold)

        # Combined effective capacity
        capacity_eff = capacity_from_load * capacity_from_energy
        capacity_eff = np.maximum(capacity_eff, self.capacity_min)

        # Time dilation: gamma = 1 / capacity
        gamma_field = 1.0 / capacity_eff

        # Cache for efficiency
        self._gamma_cache = gamma_field
        self._gamma_dirty = False

        return gamma_field

    def get_gamma_field(self) -> np.ndarray:
        """Get gamma field (use cached if available)."""
        if self._gamma_dirty or self._gamma_cache is None:
            return self.compute_gamma_field()
        return self._gamma_cache

    def get_gamma_at_position(self, position: np.ndarray) -> float:
        """Sample gamma field at given position."""
        gamma_field = self.get_gamma_field()
        ix = int(position[0]) % self.grid_size
        iy = int(position[1]) % self.grid_size
        return float(gamma_field[ix, iy])

    def compute_gradient_at_position(self, position: np.ndarray) -> np.ndarray:
        """
        V2 NEW METHOD: Compute ∇γ at given position for gradient-following.

        Args:
            position: (x, y) position in grid coordinates

        Returns:
            (grad_x, grad_y) gradient vector
        """
        gamma_field = self.get_gamma_field()
        return compute_gamma_gradient(position, gamma_field, self.grid_size, dx=1.0)

    def find_local_minima(
        self,
        threshold_gamma: float = 1.5,
        min_separation: float = 2.0
    ) -> List[Tuple[np.ndarray, float]]:
        """
        Find local minima in gamma field (gamma-well centers).

        Note: Gamma-wells are regions of HIGH gamma (time dilation).
        Local minima in proper time rate = local MAXIMA in gamma.

        Args:
            threshold_gamma: Minimum gamma value to consider as well
            min_separation: Minimum distance between wells

        Returns:
            List of (position, gamma_value) tuples for well centers
        """
        gamma_field = self.get_gamma_field()
        wells = []

        # Find local maxima in gamma field (= minima in proper time rate)
        for i in range(1, self.grid_size - 1):
            for j in range(1, self.grid_size - 1):
                gamma_val = gamma_field[i, j]

                # Check if local maximum and above threshold
                if gamma_val < threshold_gamma:
                    continue

                # Check if maximum in 3x3 neighborhood
                neighborhood = gamma_field[i-1:i+2, j-1:j+2]
                if gamma_val < np.max(neighborhood) - 1e-6:
                    continue

                position = np.array([float(i), float(j)])

                # Check minimum separation from existing wells
                too_close = False
                for existing_pos, _ in wells:
                    dist = np.linalg.norm(position - existing_pos)
                    if dist < min_separation:
                        too_close = True
                        break

                if not too_close:
                    wells.append((position, float(gamma_val)))

        return wells

    def compute_binding_energy(
        self,
        center: np.ndarray,
        radius: float = 5.0
    ) -> float:
        """
        Compute binding energy in γ-well around center position.

        E_bind = -∫ (γ - 1) dV over region

        Negative binding energy = bound state

        Args:
            center: (x, y) center of well
            radius: Integration radius

        Returns:
            Binding energy (negative if bound)
        """
        gamma_field = self.get_gamma_field()

        cx, cy = center
        ix = int(cx)
        iy = int(cy)

        # Integrate (gamma - 1) over circular region
        total = 0.0
        count = 0

        r_int = int(radius) + 1
        for di in range(-r_int, r_int + 1):
            for dj in range(-r_int, r_int + 1):
                # Check if within radius
                r = math.sqrt(di**2 + dj**2)
                if r > radius:
                    continue

                # Sample gamma at this point
                sample_ix = (ix + di) % self.grid_size
                sample_iy = (iy + dj) % self.grid_size
                gamma_val = gamma_field[sample_ix, sample_iy]

                total += (gamma_val - 1.0)
                count += 1

        # Binding energy (negative of integral)
        binding_energy = -total / max(count, 1)

        return binding_energy

    def detect_shared_well(
        self,
        position1: np.ndarray,
        position2: np.ndarray,
        well_radius: float = 3.0
    ) -> bool:
        """
        Check if two positions share the same γ-well.

        Args:
            position1: First particle position
            position2: Second particle position
            well_radius: Maximum separation to consider "shared"

        Returns:
            True if particles share gamma-well
        """
        distance = np.linalg.norm(position1 - position2)
        return distance < well_radius

    def compute_orbital_parameters(
        self,
        center: np.ndarray,
        particle_position: np.ndarray,
        particle_mass: float = 0.001
    ) -> Tuple[float, float, float]:
        """
        Compute equilibrium orbital parameters for a particle in a γ-well.

        V2 NOTE: These are now INITIAL CONDITIONS only!
        Actual orbital motion will emerge from gradient-following.

        Args:
            center: (x, y) position of well center
            particle_position: (x, y) position of orbiting particle
            particle_mass: Mass of orbiting particle

        Returns:
            (orbital_radius, orbital_period, orbital_frequency) tuple
        """
        # Compute orbital radius
        dx = particle_position[0] - center[0]
        dy = particle_position[1] - center[1]
        orbital_radius = float(np.sqrt(dx**2 + dy**2))

        if orbital_radius < 0.1:
            # Particle at center (not orbiting)
            return (0.0, 0.0, 0.0)

        # Estimate γ gradient at particle position
        gamma_at_particle = self.get_gamma_at_position(particle_position)
        gamma_at_center = self.get_gamma_at_position(center)
        gamma_gradient_mag = abs(gamma_at_particle - gamma_at_center) / orbital_radius

        # Equilibrium orbital velocity (analog of v = sqrt(GM/r))
        # v ∝ sqrt(γ_gradient × r)
        v_orbital = np.sqrt(gamma_gradient_mag * orbital_radius)
        v_orbital = np.clip(v_orbital, 0.01, 0.5)  # Clamp to reasonable range

        # Orbital period
        orbital_period = 2 * np.pi * orbital_radius / v_orbital
        orbital_frequency = 1.0 / orbital_period if orbital_period > 0 else 0.0

        return (orbital_radius, orbital_period, orbital_frequency)

    def get_field_statistics(self) -> dict:
        """Return statistics about current field state."""
        gamma_field = self.get_gamma_field()

        return {
            'L_mean': float(np.mean(self.L)),
            'L_max': float(np.max(self.L)),
            'L_std': float(np.std(self.L)),
            'E_mean': float(np.mean(self.E)),
            'E_min': float(np.min(self.E)),
            'E_std': float(np.std(self.E)),
            'gamma_mean': float(np.mean(gamma_field)),
            'gamma_max': float(np.max(gamma_field)),
            'gamma_min': float(np.min(gamma_field)),
        }


# ============================================================================
# Constituent Particle with Gradient-Following Dynamics
# ============================================================================

class ConstituentParticle:
    """
    Particle within a composite object with gradient-following dynamics.

    V2 CHANGES:
    - Tracks velocity and acceleration
    - update_velocity_gradient_following() method
    - Position updates from velocity integration
    """

    def __init__(
        self,
        pattern: Pattern,
        relative_position: np.ndarray,
        velocity: np.ndarray,
        orbital_radius: float = 0.0,
        orbital_period: float = 0.0
    ):
        """
        Initialize constituent particle.

        Args:
            pattern: Pattern object (proton, electron, neutron)
            relative_position: Position relative to composite center
            velocity: Velocity vector (vx, vy)
            orbital_radius: Initial orbital radius (for reference)
            orbital_period: Initial orbital period (for reference)
        """
        self.pattern = pattern
        self.relative_position = np.array(relative_position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.orbital_radius = orbital_radius
        self.orbital_period = orbital_period
        self.orbital_frequency = (1.0 / orbital_period) if orbital_period > 0 else 0.0

        # V2 ADDITIONS: Acceleration tracking
        self.acceleration = np.zeros(2, dtype=float)
        self.acceleration_history = []
        self.velocity_history = []
        self.position_history = []

    def update_velocity_gradient_following(
        self,
        gamma_gradient: np.ndarray,
        dt: float = 1.0,
        coupling_constant: float = 0.01,
        c: float = 1.0
    ):
        """
        V2 CORE PHYSICS: Update velocity by following time-flow gradient.

        Particles are attracted to regions of HIGHER γ_grav (time dilation).
        ∇γ points toward DECREASING γ, so acceleration is -k∇γ (toward well center).

        This is the geodesic equation: particles fall toward time-flow minima.

        Args:
            gamma_gradient: ∇γ_grav at current position (2D vector)
            dt: Time step
            coupling_constant: Strength of gradient coupling (tunable)
            c: Speed of light
        """
        # Acceleration TOWARD high-gamma regions
        # ∇γ points toward increasing gamma (toward well center)
        # Particles follow the gradient toward high gamma
        self.acceleration = coupling_constant * gamma_gradient

        # Update velocity
        self.velocity += self.acceleration * dt

        # Enforce speed limit c
        speed = np.linalg.norm(self.velocity)
        if speed > c:
            self.velocity *= c / speed

        # Record history
        self.acceleration_history.append(np.copy(self.acceleration))
        self.velocity_history.append(np.copy(self.velocity))

    def update_position(
        self,
        dt: float = 1.0
    ):
        """
        Update position based on current velocity.

        Args:
            dt: Time step
        """
        self.relative_position += self.velocity * dt
        self.position_history.append(np.copy(self.relative_position))

    @property
    def speed(self) -> float:
        """Current speed (magnitude of velocity)."""
        return float(np.linalg.norm(self.velocity))


if __name__ == "__main__":
    # Basic test: Create detector and compute gamma-well
    print("Testing GammaWellDetector V2...")

    detector = GammaWellDetector(grid_size=100)

    # Create proton at center
    proton = Pattern("PROTON", energy=10.0, mass=1.0)
    proton_pos = np.array([50.0, 50.0])
    proton_vel = np.array([0.0, 0.0])

    # Update fields
    patterns = [(proton, proton_pos, proton_vel)]

    # Check source first
    S = detector.compute_source_from_patterns(patterns)
    print(f"Source max: {np.max(S):.6f}, at position: {np.unravel_index(np.argmax(S), S.shape)}")
    print(f"Load before: L_max={np.max(detector.L):.6f}")

    detector.update_fields(patterns, num_steps=100)

    # Check field statistics
    stats = detector.get_field_statistics()
    print(f"Load after: L_max={stats['L_max']:.6f}")
    print(f"Field stats: gamma_max={stats['gamma_max']:.3f}, gamma_mean={stats['gamma_mean']:.3f}")

    # Find gamma-wells (lower threshold for testing)
    wells = detector.find_local_minima(threshold_gamma=1.1)
    print(f"Found {len(wells)} gamma-wells")

    if wells:
        center, gamma_val = wells[0]
        print(f"Well center: {center}, gamma: {gamma_val:.3f}")

        # Compute gradient at offset position
        test_pos = np.array([52.0, 50.0])
        gradient = detector.compute_gradient_at_position(test_pos)
        print(f"Gradient at {test_pos}: {gradient}")

        # Binding energy
        E_bind = detector.compute_binding_energy(center, radius=5.0)
        print(f"Binding energy: {E_bind:.3f}")

    print("\n[OK] GammaWellDetector V2 test passed!")
