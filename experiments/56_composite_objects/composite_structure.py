#!/usr/bin/env python3
"""
Composite Object Structure for Experiment 56

Defines data structures for multi-particle bound states:
- CompositeObject: Main container for bound particles
- ConstituentParticle: Individual particle within composite
- CompositeType: Classification of composite types

Builds on Pattern from Experiment 55, adding internal structure and binding.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import numpy as np
import math
import sys
from pathlib import Path

# Import Pattern from Experiment 55
sys.path.append(str(Path(__file__).parent.parent / "55_collision_physics"))
from pattern_overlap import Pattern, PatternType


# ============================================================================
# Composite Type Classification
# ============================================================================

class CompositeType(Enum):
    """
    Classification of composite object types.

    Based on constituent particles and internal structure.
    """
    # Atoms (nucleus + electrons)
    HYDROGEN = "hydrogen"  # 1 proton + 1 electron
    DEUTERIUM = "deuterium"  # 1 proton + 1 neutron + 1 electron
    HELIUM = "helium"  # 2 protons + 2 neutrons + 2 electrons
    CARBON = "carbon"  # 6 protons + 6 neutrons + 6 electrons

    # Nuclei (protons + neutrons)
    DEUTERIUM_NUCLEUS = "deuterium_nucleus"  # 1 proton + 1 neutron
    TRITIUM_NUCLEUS = "tritium_nucleus"  # 1 proton + 2 neutrons
    HELIUM_NUCLEUS = "helium_nucleus"  # 2 protons + 2 neutrons (alpha particle)

    # Molecules (bound atoms)
    H2_MOLECULE = "h2_molecule"  # 2 hydrogen atoms
    H2O_MOLECULE = "h2o_molecule"  # 2 hydrogen + 1 oxygen
    CO2_MOLECULE = "co2_molecule"  # 1 carbon + 2 oxygen

    # Generic composites
    GENERIC_NUCLEUS = "generic_nucleus"  # Unspecified proton/neutron cluster
    GENERIC_ATOM = "generic_atom"  # Unspecified nucleus + electrons
    GENERIC_MOLECULE = "generic_molecule"  # Unspecified atomic cluster

    def is_nucleus(self) -> bool:
        """Check if composite is a nucleus (no electrons)."""
        return "nucleus" in self.value.lower()

    def is_atom(self) -> bool:
        """Check if composite is an atom (nucleus + electrons)."""
        return self in [CompositeType.HYDROGEN, CompositeType.DEUTERIUM,
                       CompositeType.HELIUM, CompositeType.CARBON,
                       CompositeType.GENERIC_ATOM]

    def is_molecule(self) -> bool:
        """Check if composite is a molecule (bound atoms)."""
        return "molecule" in self.value.lower()


# ============================================================================
# Constituent Particle
# ============================================================================

@dataclass
class ConstituentParticle:
    """
    Individual particle within a composite object.

    Tracks particle's position and motion relative to composite center.
    """
    # Identity
    constituent_id: str
    pattern: Pattern  # From Experiment 55

    # Position within composite (relative to center of mass)
    relative_position: np.ndarray  # (x, y) in composite frame
    velocity: np.ndarray  # (vx, vy) in composite frame

    # Orbital parameters (if particle is in orbit)
    orbital_radius: float = 0.0
    orbital_period: float = 0.0
    orbital_phase: float = 0.0  # Current phase in orbit (0 to 2π)
    orbital_frequency: float = 0.0  # ω = 2π / period

    # Binding
    binding_energy: float = 0.0  # Energy binding this particle to composite

    def __post_init__(self):
        """Ensure arrays are numpy arrays."""
        if not isinstance(self.relative_position, np.ndarray):
            self.relative_position = np.array(self.relative_position, dtype=float)
        if not isinstance(self.velocity, np.ndarray):
            self.velocity = np.array(self.velocity, dtype=float)

    @property
    def speed(self) -> float:
        """Speed magnitude in composite frame."""
        return float(np.linalg.norm(self.velocity))

    @property
    def distance_from_center(self) -> float:
        """Distance from composite center of mass."""
        return float(np.linalg.norm(self.relative_position))

    def update_orbital_position(self, dt: float):
        """
        Update position based on orbital motion.

        For circular orbits: r(t) = r₀ * (cos(ωt), sin(ωt))

        Args:
            dt: Time step (in ticks)
        """
        if self.orbital_frequency > 0:
            # Update phase
            self.orbital_phase += self.orbital_frequency * dt
            self.orbital_phase = self.orbital_phase % (2 * math.pi)

            # Update position (circular orbit)
            self.relative_position[0] = self.orbital_radius * math.cos(self.orbital_phase)
            self.relative_position[1] = self.orbital_radius * math.sin(self.orbital_phase)

            # Update velocity (tangential)
            v_tangent = self.orbital_radius * self.orbital_frequency
            self.velocity[0] = -v_tangent * math.sin(self.orbital_phase)
            self.velocity[1] = v_tangent * math.cos(self.orbital_phase)


# ============================================================================
# Composite Object
# ============================================================================

@dataclass
class CompositeObject:
    """
    Multi-particle bound state.

    Represents atoms, molecules, or nuclei with internal structure.
    Constituents are bound by shared γ-well (time-flow minimum).
    """
    # Identity
    composite_id: str
    composite_type: CompositeType

    # Constituents
    constituents: List[ConstituentParticle] = field(default_factory=list)

    # Spatial state (center of mass)
    center_of_mass: np.ndarray = field(default_factory=lambda: np.zeros(2))
    velocity_cm: np.ndarray = field(default_factory=lambda: np.zeros(2))  # Center of mass velocity

    # Physical properties
    total_mass: float = 0.0
    total_energy: float = 0.0

    # Binding
    binding_energy: float = 0.0  # Total energy binding constituents
    gamma_well_depth: float = 0.0  # Depth of γ-well at composite center

    # Internal state
    vibrational_mode: int = 0  # Vibrational quantum number
    rotational_mode: int = 0  # Rotational quantum number
    excitation_energy: float = 0.0  # Energy in internal modes

    # Lifecycle
    formation_tick: int = 0
    age: int = 0
    stable: bool = True

    # Grid cell position (for collision detection)
    grid_position: Tuple[int, int] = (0, 0)

    def __post_init__(self):
        """Initialize composite properties from constituents."""
        if not isinstance(self.center_of_mass, np.ndarray):
            self.center_of_mass = np.array(self.center_of_mass, dtype=float)
        if not isinstance(self.velocity_cm, np.ndarray):
            self.velocity_cm = np.array(self.velocity_cm, dtype=float)

        # Compute derived properties
        self.update_properties()

    def update_properties(self):
        """Recompute total mass, energy, center of mass from constituents."""
        if not self.constituents:
            return

        # Total mass
        self.total_mass = sum(c.pattern.mass for c in self.constituents)

        # Total energy (constituents + binding + excitation)
        constituent_energy = sum(c.pattern.energy for c in self.constituents)
        self.total_energy = constituent_energy + self.binding_energy + self.excitation_energy

        # Center of mass (in lab frame, if absolute positions available)
        # For now, center_of_mass is set externally

    def add_constituent(
        self,
        pattern: Pattern,
        relative_position: np.ndarray,
        velocity: np.ndarray,
        orbital_radius: float = 0.0
    ) -> ConstituentParticle:
        """
        Add a constituent particle to the composite.

        Args:
            pattern: Pattern object (from Experiment 55)
            relative_position: Position relative to center of mass
            velocity: Velocity in composite frame
            orbital_radius: Orbital radius (0 = non-orbiting)

        Returns:
            ConstituentParticle instance
        """
        constituent_id = f"{self.composite_id}_constituent_{len(self.constituents)}"

        constituent = ConstituentParticle(
            constituent_id=constituent_id,
            pattern=pattern,
            relative_position=relative_position,
            velocity=velocity,
            orbital_radius=orbital_radius
        )

        self.constituents.append(constituent)
        self.update_properties()

        return constituent

    def get_constituent_by_type(self, pattern_type: PatternType) -> List[ConstituentParticle]:
        """Get all constituents of a given pattern type."""
        return [c for c in self.constituents if c.pattern.pattern_type == pattern_type]

    def count_by_type(self, pattern_type: PatternType) -> int:
        """Count constituents of a given pattern type."""
        return len(self.get_constituent_by_type(pattern_type))

    def update_internal_dynamics(self, dt: float = 1.0):
        """
        Update internal constituent positions and velocities.

        Args:
            dt: Time step (in ticks)
        """
        for constituent in self.constituents:
            # Update orbital motion if applicable
            if constituent.orbital_frequency > 0:
                constituent.update_orbital_position(dt)

        self.age += int(dt)

    def check_stability(self, energy_threshold: float = 0.0) -> bool:
        """
        Check if composite is still stable.

        Composite becomes unstable if:
        - Binding energy becomes positive (unbound)
        - External energy injection exceeds binding energy

        Args:
            energy_threshold: Threshold for stability (default 0.0 = unbound)
                              Negative binding energy = bound/stable
                              Positive binding energy = unbound/unstable

        Returns:
            True if stable, False if dissolving
        """
        # Stable if binding energy is negative (bound state)
        if self.binding_energy >= energy_threshold:
            self.stable = False
            return False

        return True

    def dissolve(self) -> List[Pattern]:
        """
        Dissolve composite into constituent patterns.

        Returns:
            List of Pattern objects (freed constituents)
        """
        self.stable = False
        freed_patterns = [c.pattern for c in self.constituents]
        self.constituents.clear()
        return freed_patterns

    def get_summary(self) -> dict:
        """Return dictionary summary of composite state."""
        return {
            'id': self.composite_id,
            'type': self.composite_type.value,
            'num_constituents': len(self.constituents),
            'center_of_mass': tuple(self.center_of_mass),
            'velocity_cm': tuple(self.velocity_cm),
            'total_mass': self.total_mass,
            'total_energy': self.total_energy,
            'binding_energy': self.binding_energy,
            'gamma_well_depth': self.gamma_well_depth,
            'age': self.age,
            'stable': self.stable
        }


# ============================================================================
# Composite Builder (Factory Methods)
# ============================================================================

class CompositeBuilder:
    """
    Factory methods for creating common composite types.

    Provides templates for hydrogen atoms, helium nuclei, molecules, etc.
    """

    @staticmethod
    def create_hydrogen_atom(
        composite_id: str,
        center_position: np.ndarray,
        orbital_radius: float = 1.0,
        binding_energy: float = -13.6  # eV analog
    ) -> CompositeObject:
        """
        Create hydrogen atom (1 proton + 1 electron).

        Args:
            composite_id: Unique identifier
            center_position: Position in lab frame
            orbital_radius: Electron orbital radius (Bohr radius analog)
            binding_energy: Binding energy (negative = bound)

        Returns:
            CompositeObject representing hydrogen atom
        """
        composite = CompositeObject(
            composite_id=composite_id,
            composite_type=CompositeType.HYDROGEN,
            center_of_mass=center_position,
            binding_energy=binding_energy
        )

        # Add proton at center
        proton = Pattern(PatternType.PROTON, energy=10.0, mass=1.0)
        composite.add_constituent(
            pattern=proton,
            relative_position=np.array([0.0, 0.0]),
            velocity=np.array([0.0, 0.0]),
            orbital_radius=0.0  # Stationary
        )

        # Add electron in orbit
        electron = Pattern(PatternType.ELECTRON, energy=5.0, mass=0.001)
        electron_constituent = composite.add_constituent(
            pattern=electron,
            relative_position=np.array([orbital_radius, 0.0]),
            velocity=np.array([0.0, 0.0]),  # Will be set by orbital motion
            orbital_radius=orbital_radius
        )

        # Set orbital parameters (circular orbit)
        # v_orbital = sqrt(GM/r) analog, but using γ-well strength
        # Simplified: assume v_orbital ~ c/10 for typical binding
        v_orbital = 0.1  # Units of c
        orbital_period = 2 * math.pi * orbital_radius / v_orbital
        electron_constituent.orbital_period = orbital_period
        electron_constituent.orbital_frequency = 2 * math.pi / orbital_period
        electron_constituent.orbital_phase = 0.0

        composite.update_properties()

        return composite

    @staticmethod
    def create_helium_nucleus(
        composite_id: str,
        center_position: np.ndarray,
        binding_energy: float = -28.0  # MeV analog
    ) -> CompositeObject:
        """
        Create helium-4 nucleus (2 protons + 2 neutrons).

        Args:
            composite_id: Unique identifier
            center_position: Position in lab frame
            binding_energy: Total binding energy (negative = bound)

        Returns:
            CompositeObject representing alpha particle
        """
        composite = CompositeObject(
            composite_id=composite_id,
            composite_type=CompositeType.HELIUM_NUCLEUS,
            center_of_mass=center_position,
            binding_energy=binding_energy
        )

        # Nuclear radius (very small, ~1 fm analog)
        r_nucleus = 0.1

        # Add 2 protons and 2 neutrons in tetrahedral configuration
        positions = [
            np.array([r_nucleus, 0.0]),
            np.array([-r_nucleus, 0.0]),
            np.array([0.0, r_nucleus]),
            np.array([0.0, -r_nucleus])
        ]

        particles = [
            Pattern(PatternType.PROTON, energy=15.0, mass=1.0),
            Pattern(PatternType.PROTON, energy=15.0, mass=1.0),
            Pattern(PatternType.NEUTRON, energy=15.0, mass=1.0),
            Pattern(PatternType.NEUTRON, energy=15.0, mass=1.0)
        ]

        for i, (particle, position) in enumerate(zip(particles, positions)):
            composite.add_constituent(
                pattern=particle,
                relative_position=position,
                velocity=np.array([0.0, 0.0]),  # Frozen structure (for now)
                orbital_radius=0.0
            )

        composite.update_properties()

        return composite

    @staticmethod
    def create_h2_molecule(
        composite_id: str,
        center_position: np.ndarray,
        bond_length: float = 1.5,
        binding_energy: float = -4.5  # eV analog
    ) -> CompositeObject:
        """
        Create H₂ molecule (2 hydrogen atoms bound).

        Args:
            composite_id: Unique identifier
            center_position: Position in lab frame
            bond_length: Distance between nuclei
            binding_energy: Molecular binding energy (negative = bound)

        Returns:
            CompositeObject representing H₂ molecule
        """
        composite = CompositeObject(
            composite_id=composite_id,
            composite_type=CompositeType.H2_MOLECULE,
            center_of_mass=center_position,
            binding_energy=binding_energy
        )

        # Two protons separated by bond length
        proton1 = Pattern(PatternType.PROTON, energy=10.0, mass=1.0)
        proton2 = Pattern(PatternType.PROTON, energy=10.0, mass=1.0)

        composite.add_constituent(
            pattern=proton1,
            relative_position=np.array([-bond_length/2, 0.0]),
            velocity=np.array([0.0, 0.0])
        )

        composite.add_constituent(
            pattern=proton2,
            relative_position=np.array([bond_length/2, 0.0]),
            velocity=np.array([0.0, 0.0])
        )

        # Two electrons in shared orbital (simplified: position between protons)
        electron1 = Pattern(PatternType.ELECTRON, energy=5.0, mass=0.001)
        electron2 = Pattern(PatternType.ELECTRON, energy=5.0, mass=0.001)

        composite.add_constituent(
            pattern=electron1,
            relative_position=np.array([0.0, 0.5]),  # Above bond axis
            velocity=np.array([0.0, 0.0])
        )

        composite.add_constituent(
            pattern=electron2,
            relative_position=np.array([0.0, -0.5]),  # Below bond axis
            velocity=np.array([0.0, 0.0])
        )

        composite.update_properties()

        return composite


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("COMPOSITE STRUCTURE MODULE - EXPERIMENT 56")
    print("=" * 70)
    print()

    # Test 1: Hydrogen Atom
    print("Test 1: Create Hydrogen Atom")
    print("-" * 70)
    hydrogen = CompositeBuilder.create_hydrogen_atom(
        composite_id="H_001",
        center_position=np.array([50.0, 50.0]),
        orbital_radius=1.0,
        binding_energy=-13.6
    )

    print(f"  Composite type: {hydrogen.composite_type.value}")
    print(f"  Num constituents: {len(hydrogen.constituents)}")
    print(f"  Total mass: {hydrogen.total_mass:.3f}")
    print(f"  Binding energy: {hydrogen.binding_energy:.1f}")
    print(f"  Proton count: {hydrogen.count_by_type(PatternType.PROTON)}")
    print(f"  Electron count: {hydrogen.count_by_type(PatternType.ELECTRON)}")

    # Check orbital parameters
    electrons = hydrogen.get_constituent_by_type(PatternType.ELECTRON)
    if electrons:
        e = electrons[0]
        print(f"  Electron orbital radius: {e.orbital_radius:.3f}")
        print(f"  Electron orbital period: {e.orbital_period:.3f}")
        print(f"  Electron orbital frequency: {e.orbital_frequency:.6f}")
    print()

    # Test 2: Update internal dynamics
    print("Test 2: Update Internal Dynamics (10 ticks)")
    print("-" * 70)
    print(f"  Initial electron phase: {electrons[0].orbital_phase:.3f}")
    print(f"  Initial electron position: {electrons[0].relative_position}")

    for tick in range(10):
        hydrogen.update_internal_dynamics(dt=1.0)

    print(f"  Final electron phase: {electrons[0].orbital_phase:.3f}")
    print(f"  Final electron position: {electrons[0].relative_position}")
    print(f"  Electron distance from center: {electrons[0].distance_from_center:.3f}")
    print()

    # Test 3: Helium Nucleus
    print("Test 3: Create Helium Nucleus")
    print("-" * 70)
    helium = CompositeBuilder.create_helium_nucleus(
        composite_id="He4_001",
        center_position=np.array([60.0, 60.0]),
        binding_energy=-28.0
    )

    print(f"  Composite type: {helium.composite_type.value}")
    print(f"  Num constituents: {len(helium.constituents)}")
    print(f"  Proton count: {helium.count_by_type(PatternType.PROTON)}")
    print(f"  Neutron count: {helium.count_by_type(PatternType.NEUTRON)}")
    print(f"  Total mass: {helium.total_mass:.3f}")
    print(f"  Binding energy: {helium.binding_energy:.1f}")
    print()

    # Test 4: H2 Molecule
    print("Test 4: Create H2 Molecule")
    print("-" * 70)
    h2 = CompositeBuilder.create_h2_molecule(
        composite_id="H2_001",
        center_position=np.array([70.0, 70.0]),
        bond_length=1.5,
        binding_energy=-4.5
    )

    print(f"  Composite type: {h2.composite_type.value}")
    print(f"  Num constituents: {len(h2.constituents)}")
    print(f"  Proton count: {h2.count_by_type(PatternType.PROTON)}")
    print(f"  Electron count: {h2.count_by_type(PatternType.ELECTRON)}")
    print(f"  Total mass: {h2.total_mass:.3f}")
    print(f"  Binding energy: {h2.binding_energy:.1f}")
    print()

    # Test 5: Stability check
    print("Test 5: Stability Check")
    print("-" * 70)
    print(f"  Hydrogen stable: {hydrogen.check_stability()}")
    print(f"  Helium stable: {helium.check_stability()}")

    # Inject energy (simulate ionization)
    hydrogen.binding_energy += 20.0  # Exceed binding threshold
    print(f"  After energy injection: Hydrogen stable: {hydrogen.check_stability()}")
    print()

    print("=" * 70)
    print("Composite structure module loaded successfully!")
    print("=" * 70)
