#!/usr/bin/env python3
"""
Binding Detection for Experiment 56 Phase 3b

Implements γ-well field computation and binding detection for composite objects.
Adapts field dynamics from Experiment 51 to detect when particles should form bound states.
"""

import numpy as np
from typing import List, Tuple, Optional
from scipy.ndimage import laplace
import sys
from pathlib import Path

# Import from Experiment 56
from composite_structure import CompositeObject, ConstituentParticle, CompositeType, Pattern


class GammaWellDetector:
    """
    Detects and analyzes γ-wells (time-flow minima) created by particles.

    Used to determine when particles should bind into composite objects.
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
        work_threshold: float = 0.5 # Minimum energy for work
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

        # Field state
        self.L = np.zeros((grid_size, grid_size), dtype=float)  # Load field
        self.E = np.ones((grid_size, grid_size), dtype=float) * E_max  # Energy field

        # Derived γ-field (computed on demand)
        self._gamma_cache = None
        self._gamma_dirty = True

    def compute_source_from_patterns(
        self,
        patterns: List[Tuple[Pattern, np.ndarray]]
    ) -> np.ndarray:
        """
        Compute source field S(x) from list of patterns and their positions.

        Args:
            patterns: List of (Pattern, position) tuples
                     position is (x, y) in grid coordinates

        Returns:
            Source field S as (grid_size, grid_size) array
        """
        S = np.zeros((self.grid_size, self.grid_size), dtype=float)

        for pattern, position in patterns:
            ix = int(position[0]) % self.grid_size
            iy = int(position[1]) % self.grid_size

            # Source strength: mass × energy / E_max
            # Simplified from v11: assume stationary particles (no velocity factor)
            contribution = pattern.mass * (pattern.energy / self.E_max)
            S[ix, iy] += self.scale * contribution

        return S

    def update_fields(
        self,
        patterns: List[Tuple[Pattern, np.ndarray]],
        dt: float = 1.0,
        num_steps: int = 100
    ):
        """
        Evolve load and energy fields to steady state with given patterns.

        Args:
            patterns: List of (Pattern, position) tuples
            dt: Time step for field evolution
            num_steps: Number of evolution steps to reach steady state
        """
        # Compute source term from patterns
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

        Returns:
            γ-field as (grid_size, grid_size) array
            Values >= 1.0, where higher γ = slower time = deeper well
        """
        if not self._gamma_dirty and self._gamma_cache is not None:
            return self._gamma_cache

        # Capacity from load (saturation effect)
        capacity_from_load = 1.0 / (1.0 + self.L)

        # Capacity from energy (availability effect)
        capacity_from_energy = self.E / (self.E + self.work_threshold)

        # Combined capacity
        capacity_eff = capacity_from_load * capacity_from_energy
        capacity_eff = np.maximum(capacity_eff, self.capacity_min)

        # Time dilation: gamma = 1 / capacity
        gamma_field = 1.0 / capacity_eff

        # Cache result
        self._gamma_cache = gamma_field
        self._gamma_dirty = False

        return gamma_field

    def get_gamma_at_position(self, position: np.ndarray) -> float:
        """
        Get γ value at specific position.

        Args:
            position: (x, y) coordinates in grid space

        Returns:
            γ value at that position
        """
        gamma_field = self.compute_gamma_field()

        ix = int(position[0]) % self.grid_size
        iy = int(position[1]) % self.grid_size

        return float(gamma_field[ix, iy])

    def find_local_minima(
        self,
        threshold: float = 1.2
    ) -> List[Tuple[int, int, float]]:
        """
        Find local minima in γ-field (wells where particles can be trapped).

        Note: γ-well is actually a MAXIMUM in the γ-field (higher γ = time dilation).
        But conceptually it's a "well" in the time-flow rate.

        Args:
            threshold: Minimum γ value to be considered a well

        Returns:
            List of (x, y, gamma) tuples for well centers
        """
        gamma_field = self.compute_gamma_field()

        wells = []

        # Find local maxima in γ-field
        for ix in range(1, self.grid_size - 1):
            for iy in range(1, self.grid_size - 1):
                gamma_center = gamma_field[ix, iy]

                # Check if this is a local maximum and exceeds threshold
                if gamma_center < threshold:
                    continue

                # Check 8 neighbors
                is_maximum = True
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue

                        gamma_neighbor = gamma_field[ix + dx, iy + dy]
                        if gamma_neighbor >= gamma_center:
                            is_maximum = False
                            break

                    if not is_maximum:
                        break

                if is_maximum:
                    wells.append((ix, iy, float(gamma_center)))

        return wells

    def compute_binding_energy(
        self,
        position: np.ndarray,
        radius: float = 5.0
    ) -> float:
        """
        Compute binding energy at a position.

        Binding energy = integral of (γ - 1) over nearby region
        Approximated as sum over grid cells within radius

        Args:
            position: (x, y) center position
            radius: Radius to integrate over

        Returns:
            Binding energy (negative = bound, positive = unbound)
        """
        gamma_field = self.compute_gamma_field()

        ix_center = int(position[0]) % self.grid_size
        iy_center = int(position[1]) % self.grid_size

        # Sum (γ - 1) over cells within radius
        binding = 0.0
        count = 0

        for ix in range(self.grid_size):
            for iy in range(self.grid_size):
                # Distance from center (periodic boundary conditions)
                dx = min(abs(ix - ix_center), self.grid_size - abs(ix - ix_center))
                dy = min(abs(iy - iy_center), self.grid_size - abs(iy - iy_center))
                r = np.sqrt(dx**2 + dy**2)

                if r <= radius:
                    binding += (gamma_field[ix, iy] - 1.0)
                    count += 1

        # Return negative (bound state convention: E_bind < 0)
        return -binding / max(count, 1)

    def detect_shared_well(
        self,
        positions: List[np.ndarray],
        well_radius: float = 5.0,
        gamma_threshold: float = 1.1
    ) -> bool:
        """
        Detect if multiple positions share the same γ-well.

        Args:
            positions: List of (x, y) positions to check
            well_radius: Radius defining "same well"
            gamma_threshold: Minimum γ value to constitute a well

        Returns:
            True if positions share a well, False otherwise
        """
        if len(positions) < 2:
            return False

        gamma_field = self.compute_gamma_field()

        # Check if all positions have γ > threshold
        for pos in positions:
            gamma = self.get_gamma_at_position(pos)
            if gamma < gamma_threshold:
                return False

        # Check if all positions are within well_radius of each other
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i+1:]:
                dx = min(abs(pos1[0] - pos2[0]), self.grid_size - abs(pos1[0] - pos2[0]))
                dy = min(abs(pos1[1] - pos2[1]), self.grid_size - abs(pos1[1] - pos2[1]))
                r = np.sqrt(dx**2 + dy**2)

                if r > well_radius:
                    return False

        return True

    def compute_orbital_parameters(
        self,
        center: np.ndarray,
        particle_position: np.ndarray,
        particle_mass: float = 0.001
    ) -> Tuple[float, float, float]:
        """
        Compute orbital parameters for a particle in a γ-well.

        Simplified orbital dynamics:
        - Orbital velocity v = sqrt(γ_gradient × r) (analog of v = sqrt(GM/r))
        - Period T = 2πr / v

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
        gamma_gradient = (gamma_at_particle - gamma_at_center) / orbital_radius

        # Orbital velocity (simplified: v ∝ sqrt(γ_gradient × r))
        # Clamped to reasonable values (0.01c to 0.5c)
        v_orbital = np.sqrt(abs(gamma_gradient) * orbital_radius)
        v_orbital = np.clip(v_orbital, 0.01, 0.5)

        # Orbital period
        orbital_period = 2 * np.pi * orbital_radius / v_orbital
        orbital_frequency = 1.0 / orbital_period if orbital_period > 0 else 0.0

        return (orbital_radius, orbital_period, orbital_frequency)

    def get_field_statistics(self) -> dict:
        """Return statistics about current field state."""
        gamma_field = self.compute_gamma_field()

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
# Composite Binding Manager
# ============================================================================

class CompositeBindingManager:
    """
    Manages composite object binding using γ-well detection.

    Integrates GammaWellDetector with CompositeObject lifecycle.
    """

    def __init__(
        self,
        grid_size: int = 100,
        well_detector: Optional[GammaWellDetector] = None
    ):
        """
        Initialize binding manager.

        Args:
            grid_size: Size of simulation grid
            well_detector: Optional pre-configured GammaWellDetector
        """
        self.grid_size = grid_size
        self.well_detector = well_detector or GammaWellDetector(grid_size=grid_size)

        # Active composites
        self.composites: List[CompositeObject] = []

        # Tracking
        self.tick = 0

    def add_composite(self, composite: CompositeObject):
        """Add a composite to be managed."""
        self.composites.append(composite)

    def remove_composite(self, composite_id: str):
        """Remove a composite by ID."""
        self.composites = [c for c in self.composites if c.composite_id != composite_id]

    def update_all_composites(
        self,
        dt: float = 1.0,
        update_fields: bool = True
    ):
        """
        Update all composites for one tick.

        Args:
            dt: Time step
            update_fields: If True, recompute γ-fields from current composite positions
        """
        if update_fields:
            # Gather all patterns and positions
            patterns = []
            for composite in self.composites:
                for constituent in composite.constituents:
                    # Absolute position = center + relative
                    abs_position = composite.center_of_mass + constituent.relative_position
                    patterns.append((constituent.pattern, abs_position))

            # Update field state
            if patterns:
                self.well_detector.update_fields(patterns, dt=dt, num_steps=50)

        # Update each composite's internal dynamics
        for composite in self.composites:
            composite.update_internal_dynamics(dt)

            # Check stability
            composite.check_stability()

        # Remove unstable composites
        self.composites = [c for c in self.composites if c.stable]

        self.tick += int(dt)

    def analyze_composite_binding(
        self,
        composite: CompositeObject
    ) -> dict:
        """
        Analyze binding properties of a composite.

        Returns:
            Dictionary with binding analysis:
            - gamma_at_center: γ value at composite center
            - binding_energy: Computed from γ-well depth
            - well_radius: Effective radius of γ-well
            - shared_well: Whether constituents share γ-well
        """
        # Get γ at center
        gamma_center = self.well_detector.get_gamma_at_position(composite.center_of_mass)

        # Compute binding energy
        binding_energy = self.well_detector.compute_binding_energy(
            composite.center_of_mass,
            radius=5.0
        )

        # Check if constituents share well
        constituent_positions = [
            composite.center_of_mass + c.relative_position
            for c in composite.constituents
        ]
        shared_well = self.well_detector.detect_shared_well(
            constituent_positions,
            well_radius=5.0
        )

        return {
            'gamma_at_center': gamma_center,
            'binding_energy': binding_energy,
            'well_radius': 5.0,  # Fixed for now
            'shared_well': shared_well,
            'num_constituents': len(composite.constituents)
        }

    def get_summary(self) -> dict:
        """Return summary of all composites."""
        return {
            'tick': self.tick,
            'num_composites': len(self.composites),
            'composites': [c.get_summary() for c in self.composites],
            'field_stats': self.well_detector.get_field_statistics()
        }


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("BINDING DETECTION MODULE - EXPERIMENT 56 PHASE 3b")
    print("=" * 70)
    print()

    # Test 1: gamma-well detection
    print("Test 1: Gamma-Well Detection")
    print("-" * 70)

    detector = GammaWellDetector(grid_size=100)

    # Create a few patterns
    from composite_structure import PatternType

    patterns_and_positions = [
        (Pattern(PatternType.PROTON, energy=10.0, mass=1.0), np.array([50.0, 50.0])),
        (Pattern(PatternType.PROTON, energy=10.0, mass=1.0), np.array([55.0, 50.0])),
        (Pattern(PatternType.PROTON, energy=10.0, mass=1.0), np.array([45.0, 50.0])),
    ]

    # Update fields to steady state
    print("  Updating fields to steady state (100 steps)...")
    detector.update_fields(patterns_and_positions, num_steps=100)

    # Get field statistics
    stats = detector.get_field_statistics()
    print(f"  Field statistics:")
    print(f"    L: mean={stats['L_mean']:.3f}, max={stats['L_max']:.3f}")
    print(f"    E: mean={stats['E_mean']:.3f}, min={stats['E_min']:.3f}")
    print(f"    gamma: mean={stats['gamma_mean']:.3f}, max={stats['gamma_max']:.3f}")
    print()

    # Find wells
    wells = detector.find_local_minima(threshold=1.2)
    print(f"  Found {len(wells)} gamma-wells:")
    for i, (x, y, gamma) in enumerate(wells[:5]):
        print(f"    Well {i+1}: position=({x}, {y}), gamma={gamma:.3f}")
    print()

    # Test 2: Binding energy computation
    print("Test 2: Binding Energy Computation")
    print("-" * 70)

    center = np.array([50.0, 50.0])
    binding_energy = detector.compute_binding_energy(center, radius=5.0)
    print(f"  Binding energy at center: {binding_energy:.3f}")
    print(f"  (Negative = bound, positive = unbound)")
    print()

    # Test 3: Shared well detection
    print("Test 3: Shared Well Detection")
    print("-" * 70)

    # Test close positions (should share well)
    close_positions = [
        np.array([50.0, 50.0]),
        np.array([51.0, 50.0]),
        np.array([50.0, 51.0])
    ]
    shared = detector.detect_shared_well(close_positions, well_radius=5.0)
    print(f"  Close positions (r < 5): shared_well = {shared}")

    # Test far positions (should NOT share well)
    far_positions = [
        np.array([50.0, 50.0]),
        np.array([70.0, 50.0])
    ]
    shared = detector.detect_shared_well(far_positions, well_radius=5.0)
    print(f"  Far positions (r > 5): shared_well = {shared}")
    print()

    # Test 4: Orbital parameters
    print("Test 4: Orbital Parameters")
    print("-" * 70)

    center = np.array([50.0, 50.0])
    particle_pos = np.array([52.0, 50.0])

    r_orb, T_orb, omega_orb = detector.compute_orbital_parameters(
        center,
        particle_pos,
        particle_mass=0.001
    )

    print(f"  Orbital radius: {r_orb:.3f}")
    print(f"  Orbital period: {T_orb:.3f} ticks")
    print(f"  Orbital frequency: {omega_orb:.6f} rad/tick")
    print()

    # Test 5: Composite binding manager
    print("Test 5: Composite Binding Manager")
    print("-" * 70)

    from composite_structure import CompositeBuilder

    manager = CompositeBindingManager(grid_size=100)

    # Create a hydrogen atom
    hydrogen = CompositeBuilder.create_hydrogen_atom(
        composite_id="H_test",
        center_position=np.array([50.0, 50.0]),
        orbital_radius=2.0,
        binding_energy=-13.6
    )

    manager.add_composite(hydrogen)
    print(f"  Added hydrogen atom to manager")
    print(f"  Num composites: {len(manager.composites)}")

    # Update for a few ticks
    print("  Updating for 10 ticks...")
    for tick in range(10):
        manager.update_all_composites(dt=1.0, update_fields=(tick % 5 == 0))

    # Analyze binding
    analysis = manager.analyze_composite_binding(hydrogen)
    print(f"  Binding analysis:")
    print(f"    gamma at center: {analysis['gamma_at_center']:.3f}")
    print(f"    Binding energy: {analysis['binding_energy']:.3f}")
    print(f"    Shared well: {analysis['shared_well']}")
    print()

    # Get summary
    summary = manager.get_summary()
    print(f"  Manager summary:")
    print(f"    Tick: {summary['tick']}")
    print(f"    Active composites: {summary['num_composites']}")
    print()

    print("=" * 70)
    print("Binding detection module completed successfully!")
    print("=" * 70)
