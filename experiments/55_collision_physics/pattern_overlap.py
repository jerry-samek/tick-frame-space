#!/usr/bin/env python3
"""
Pattern Structure and Overlap Computation for Experiment 55

FOUNDATIONAL MODULE: Defines what a "pattern" IS at single-cell scale.

Key Question: What is the structure of an atomic pattern?

This implementation proposes a multi-dimensional pattern representation:
- Pattern type (discrete: particle species)
- Energy level (continuous: excitation state)
- Internal mode (discrete: spin/rotation quantum number)
- Phase (continuous: wavefunction phase 0-2π)

Overlap computation combines multiple contributions:
- Type compatibility (matter vs antimatter → maximal overlap)
- Energy resonance (similar energies → higher overlap)
- Mode interference (matching quantum numbers → overlap)
- Phase alignment (coherent phases → constructive interference)

This is EXPLORATORY - the model may need refinement based on experimental results.
"""

from dataclasses import dataclass
from typing import Tuple, Optional
from enum import Enum
import numpy as np
import math


# ============================================================================
# Pattern Type Classification
# ============================================================================

class PatternType(Enum):
    """
    Discrete pattern types (particle species).

    These represent fundamentally different collision behaviors.
    Matter-antimatter pairs have maximal overlap → annihilation.
    """
    # Fundamental particles (placeholder - expand as needed)
    PHOTON = "photon"
    ELECTRON = "electron"
    POSITRON = "positron"  # antimatter counterpart
    PROTON = "proton"
    ANTIPROTON = "antiproton"
    NEUTRON = "neutron"
    ANTINEUTRON = "antineutron"

    # Composite patterns (for future use)
    HYDROGEN = "hydrogen"
    DEUTERIUM = "deuterium"
    HELIUM = "helium"

    # Generic placeholders
    MATTER_TYPE_A = "matter_A"
    MATTER_TYPE_B = "matter_B"
    ANTIMATTER_TYPE_A = "antimatter_A"
    ANTIMATTER_TYPE_B = "antimatter_B"

    def is_antimatter_of(self, other: 'PatternType') -> bool:
        """Check if this pattern is the antimatter counterpart of another."""
        antimatter_pairs = [
            (PatternType.ELECTRON, PatternType.POSITRON),
            (PatternType.PROTON, PatternType.ANTIPROTON),
            (PatternType.NEUTRON, PatternType.ANTINEUTRON),
            (PatternType.MATTER_TYPE_A, PatternType.ANTIMATTER_TYPE_A),
            (PatternType.MATTER_TYPE_B, PatternType.ANTIMATTER_TYPE_B),
        ]

        return (self, other) in antimatter_pairs or (other, self) in antimatter_pairs

    def is_photon(self) -> bool:
        """Check if pattern is a photon (special case: massless, no antimatter)."""
        return self == PatternType.PHOTON


# ============================================================================
# Pattern Data Structure
# ============================================================================

@dataclass
class Pattern:
    """
    Atomic pattern stored in a single cell.

    A pattern is indivisible - it either exists entirely in one cell or not at all.
    However, patterns have internal structure that determines collision behavior.

    Attributes:
        pattern_type: Discrete particle species
        energy: Energy content (E_pattern, not field energy)
        internal_mode: Discrete quantum number (spin, rotation state, etc.)
        phase: Wavefunction phase (0 to 2π)
        mass: Rest mass (for momentum calculations)
    """
    pattern_type: PatternType
    energy: float
    internal_mode: int = 0  # Default: ground state
    phase: float = 0.0      # Default: zero phase
    mass: float = 1.0       # Default: unit mass

    def __post_init__(self):
        """Validate pattern parameters."""
        assert self.energy >= 0, "Pattern energy must be non-negative"
        assert 0 <= self.phase <= 2 * math.pi, "Phase must be in [0, 2π]"
        assert self.mass >= 0, "Mass must be non-negative"

        # Photons have zero mass
        if self.pattern_type.is_photon():
            self.mass = 0.0

    def copy(self) -> 'Pattern':
        """Create a deep copy of this pattern."""
        return Pattern(
            pattern_type=self.pattern_type,
            energy=self.energy,
            internal_mode=self.internal_mode,
            phase=self.phase,
            mass=self.mass
        )


# ============================================================================
# Pattern Overlap Computation
# ============================================================================

class PatternOverlapCalculator:
    """
    Computes overlap energy between two patterns occupying the same cell.

    The overlap determines collision regime:
    - Zero overlap → merge (new composite pattern)
    - Partial overlap → excitation (energy redistribution)
    - Full overlap (matter-antimatter) → annihilation (explosion)

    Overlap computation is multi-factorial:
    1. Type compatibility (k_type)
    2. Energy resonance (k_energy)
    3. Mode interference (k_mode)
    4. Phase alignment (k_phase)

    E_overlap = k_type × k_energy × k_mode × k_phase × f(E_A, E_B)
    """

    def __init__(
        self,
        type_weight: float = 1.0,
        energy_weight: float = 0.3,
        mode_weight: float = 0.2,
        phase_weight: float = 0.1
    ):
        """
        Args:
            type_weight: Importance of pattern type matching (1.0 = dominant)
            energy_weight: Importance of energy resonance
            mode_weight: Importance of internal mode matching
            phase_weight: Importance of phase alignment
        """
        self.type_weight = type_weight
        self.energy_weight = energy_weight
        self.mode_weight = mode_weight
        self.phase_weight = phase_weight

    def compute_type_compatibility(self, p_A: Pattern, p_B: Pattern) -> float:
        """
        Compute type compatibility factor (0 to 1).

        Returns:
            1.0: Matter-antimatter pair (maximal overlap → annihilation)
            0.5: Same type (moderate overlap)
            0.0: Different types (minimal overlap → merge)
        """
        if p_A.pattern_type.is_antimatter_of(p_B.pattern_type):
            # Matter-antimatter: MAXIMAL overlap
            return 1.0
        elif p_A.pattern_type == p_B.pattern_type:
            # Same type: moderate overlap (Pauli exclusion relevant here)
            return 0.5
        else:
            # Different types: minimal overlap
            return 0.0

    def compute_energy_resonance(self, p_A: Pattern, p_B: Pattern) -> float:
        """
        Compute energy resonance factor (0 to 1).

        Particles with similar energies have stronger overlap.

        Returns:
            1.0: Identical energies (resonance)
            0.0: Very different energies (off-resonance)
        """
        if p_A.energy < 1e-10 and p_B.energy < 1e-10:
            return 1.0  # Both zero energy

        E_avg = (p_A.energy + p_B.energy) / 2
        E_diff = abs(p_A.energy - p_B.energy)

        # Gaussian-like resonance: exp(-(ΔE/E_avg)^2)
        if E_avg > 1e-10:
            resonance = math.exp(-(E_diff / E_avg) ** 2)
        else:
            resonance = 1.0

        return resonance

    def compute_mode_interference(self, p_A: Pattern, p_B: Pattern) -> float:
        """
        Compute internal mode interference factor (0 to 1).

        Quantum numbers (spin, rotation state) affect overlap.

        Returns:
            1.0: Same mode (constructive interference)
            0.5: Adjacent modes (partial interference)
            0.0: Opposite modes (destructive interference)
        """
        mode_diff = abs(p_A.internal_mode - p_B.internal_mode)

        if mode_diff == 0:
            return 1.0  # Same mode
        elif mode_diff == 1:
            return 0.5  # Adjacent modes
        else:
            return 0.0  # Distant modes

    def compute_phase_alignment(self, p_A: Pattern, p_B: Pattern) -> float:
        """
        Compute phase alignment factor (0 to 1).

        Wavefunction phase determines constructive vs destructive interference.

        Returns:
            1.0: Aligned phases (constructive)
            0.0: Opposite phases (destructive)
        """
        phase_diff = abs(p_A.phase - p_B.phase)

        # Handle wraparound (2π ≈ 0)
        if phase_diff > math.pi:
            phase_diff = 2 * math.pi - phase_diff

        # Cosine alignment: cos(Δφ) scaled to [0, 1]
        alignment = (math.cos(phase_diff) + 1) / 2

        return alignment

    def compute_overlap_energy(self, p_A: Pattern, p_B: Pattern) -> float:
        """
        Compute total overlap energy E_overlap.

        This is the ADDITIONAL energy generated by pattern interference.

        Args:
            p_A, p_B: Two patterns in the same cell

        Returns:
            E_overlap: Energy contribution from overlap (>= 0)

        Physics:
            E_overlap = 0           → patterns can merge cleanly (Regime 3.1)
            E_overlap > 0 (small)   → excitation (Regime 3.3)
            E_overlap >> 0 (large)  → explosion/annihilation (Regime 3.2)
        """
        # Compute compatibility factors
        k_type = self.compute_type_compatibility(p_A, p_B)
        k_energy = self.compute_energy_resonance(p_A, p_B)
        k_mode = self.compute_mode_interference(p_A, p_B)
        k_phase = self.compute_phase_alignment(p_A, p_B)

        # Weighted combination
        k_total = (
            self.type_weight * k_type +
            self.energy_weight * k_energy +
            self.mode_weight * k_mode +
            self.phase_weight * k_phase
        )

        # Normalize by total weight
        total_weight = (self.type_weight + self.energy_weight +
                       self.mode_weight + self.phase_weight)
        k_total /= total_weight

        # Base energy scale: geometric mean of pattern energies
        E_base = math.sqrt(p_A.energy * p_B.energy) if p_A.energy > 0 and p_B.energy > 0 else 0.0

        # Overlap energy scales with compatibility and base energy
        E_overlap = k_total * E_base

        return E_overlap

    def classify_overlap(
        self,
        p_A: Pattern,
        p_B: Pattern,
        E_max: float
    ) -> Tuple[str, float]:
        """
        Classify overlap regime based on total energy vs cell capacity.

        Args:
            p_A, p_B: Two patterns
            E_max: Cell capacity limit

        Returns:
            (regime, E_overlap) where regime is:
                "merge": No overlap, patterns can combine
                "excite": Partial overlap, energy within capacity
                "explode": Overlap + excess energy beyond capacity
        """
        E_overlap = self.compute_overlap_energy(p_A, p_B)
        E_total = p_A.energy + p_B.energy + E_overlap

        # Check type compatibility first
        k_type = self.compute_type_compatibility(p_A, p_B)

        if k_type < 0.1:
            # Different types, minimal overlap → merge regime
            if E_total <= E_max:
                return ("merge", E_overlap)
            else:
                return ("explode", E_overlap)  # Too much total energy

        elif E_total > E_max:
            # Overlap + excess energy → explosion regime
            return ("explode", E_overlap)

        elif E_overlap > 0.01 * E_total:
            # Significant overlap, within capacity → excitation regime
            return ("excite", E_overlap)

        else:
            # Negligible overlap → merge regime
            return ("merge", E_overlap)


# ============================================================================
# Convenience Functions
# ============================================================================

def create_matter_antimatter_pair(
    energy: float = 10.0,
    particle_type: PatternType = PatternType.ELECTRON
) -> Tuple[Pattern, Pattern]:
    """
    Create a matter-antimatter pair for testing annihilation.

    Returns:
        (matter_pattern, antimatter_pattern)
    """
    matter_map = {
        PatternType.ELECTRON: PatternType.ELECTRON,
        PatternType.PROTON: PatternType.PROTON,
        PatternType.NEUTRON: PatternType.NEUTRON,
        PatternType.MATTER_TYPE_A: PatternType.MATTER_TYPE_A,
    }

    antimatter_map = {
        PatternType.ELECTRON: PatternType.POSITRON,
        PatternType.PROTON: PatternType.ANTIPROTON,
        PatternType.NEUTRON: PatternType.ANTINEUTRON,
        PatternType.MATTER_TYPE_A: PatternType.ANTIMATTER_TYPE_A,
    }

    matter_type = matter_map.get(particle_type, PatternType.ELECTRON)
    antimatter_type = antimatter_map.get(particle_type, PatternType.POSITRON)

    matter = Pattern(
        pattern_type=matter_type,
        energy=energy,
        internal_mode=0,
        phase=0.0,
        mass=1.0
    )

    antimatter = Pattern(
        pattern_type=antimatter_type,
        energy=energy,
        internal_mode=0,
        phase=0.0,
        mass=1.0
    )

    return matter, antimatter


def create_identical_patterns(
    pattern_type: PatternType = PatternType.PROTON,
    energy: float = 10.0,
    count: int = 2
) -> list:
    """
    Create multiple identical patterns (for Pauli exclusion testing).

    Returns:
        List of Pattern objects
    """
    return [
        Pattern(
            pattern_type=pattern_type,
            energy=energy,
            internal_mode=0,
            phase=0.0,
            mass=1.0
        )
        for _ in range(count)
    ]


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PATTERN OVERLAP MODULE - EXPERIMENT 55")
    print("=" * 70)
    print()

    calculator = PatternOverlapCalculator()

    # Test 1: Matter-Antimatter Annihilation
    print("Test 1: Matter-Antimatter Annihilation")
    print("-" * 70)
    electron, positron = create_matter_antimatter_pair(energy=10.0)
    E_overlap = calculator.compute_overlap_energy(electron, positron)
    regime, _ = calculator.classify_overlap(electron, positron, E_max=15.0)
    print(f"  Electron + Positron")
    print(f"  E_overlap = {E_overlap:.3f}")
    print(f"  Regime: {regime}")
    print(f"  Expected: 'explode' (annihilation)")
    print()

    # Test 2: Identical Particles (Pauli Exclusion)
    print("Test 2: Identical Particles (Pauli Exclusion)")
    print("-" * 70)
    protons = create_identical_patterns(PatternType.PROTON, energy=10.0, count=2)
    E_overlap = calculator.compute_overlap_energy(protons[0], protons[1])
    regime, _ = calculator.classify_overlap(protons[0], protons[1], E_max=25.0)
    print(f"  Proton + Proton (same state)")
    print(f"  E_overlap = {E_overlap:.3f}")
    print(f"  Regime: {regime}")
    print(f"  Expected: 'excite' or 'merge'")
    print()

    # Test 3: Different Types (Fusion)
    print("Test 3: Different Pattern Types (Fusion)")
    print("-" * 70)
    proton = Pattern(PatternType.PROTON, energy=10.0, mass=1.0)
    neutron = Pattern(PatternType.NEUTRON, energy=10.0, mass=1.0)
    E_overlap = calculator.compute_overlap_energy(proton, neutron)
    regime, _ = calculator.classify_overlap(proton, neutron, E_max=25.0)
    print(f"  Proton + Neutron")
    print(f"  E_overlap = {E_overlap:.3f}")
    print(f"  Regime: {regime}")
    print(f"  Expected: 'merge' (fusion)")
    print()

    # Test 4: Photon Absorption
    print("Test 4: Photon Absorption (Excitation)")
    print("-" * 70)
    photon = Pattern(PatternType.PHOTON, energy=5.0, mass=0.0)
    atom = Pattern(PatternType.HYDROGEN, energy=10.0, mass=1.0)
    E_overlap = calculator.compute_overlap_energy(photon, atom)
    regime, _ = calculator.classify_overlap(photon, atom, E_max=20.0)
    print(f"  Photon + Hydrogen")
    print(f"  E_overlap = {E_overlap:.3f}")
    print(f"  Regime: {regime}")
    print(f"  Expected: 'merge' or 'excite'")
    print()

    print("=" * 70)
    print("Pattern overlap module loaded successfully!")
    print("=" * 70)
