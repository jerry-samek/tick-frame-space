#!/usr/bin/env python3
"""
Three-Regime Collision Framework for Experiment 55

Implements the complete collision physics from Doc 053:
- Regime 3.1: Merge (non-overlapping patterns → fusion)
- Regime 3.2: Explosion (overlap + excess energy → annihilation/fission)
- Regime 3.3: Excitation (partial overlap → energy redistribution)

This extends v12's minimal elastic scattering to full tick-frame collision physics.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import numpy as np
import math

from pattern_overlap import (
    Pattern, PatternType, PatternOverlapCalculator,
    create_matter_antimatter_pair
)


# ============================================================================
# Collision Event Data Structures
# ============================================================================

@dataclass
class CollisionEvent:
    """
    Record of a collision between patterns.

    Extended from v12 to include regime and energy tracking.
    """
    entity_ids: Tuple[str, ...]  # IDs of colliding entities
    cell_position: Tuple[int, int]  # Grid cell where collision occurred
    tick: int
    regime: str  # "merge", "explode", or "excite"
    E_overlap: float  # Overlap energy
    E_total: float  # Total energy before collision
    E_final: float  # Total energy after collision
    outcome: str  # Description of what happened


@dataclass
class CollisionOutcome:
    """
    Result of resolving a collision.

    Can produce:
    - New entities (merge → composite, explode → fragments)
    - Modified entities (excite → adjusted patterns)
    - Energy overflow (explode → shockwave to neighbors)
    """
    # Entities after collision
    surviving_entities: List = field(default_factory=list)  # Modified existing entities
    new_entities: List = field(default_factory=list)  # Newly created entities
    destroyed_entity_ids: List[str] = field(default_factory=list)  # Entities that were destroyed

    # Energy accounting
    energy_overflow: float = 0.0  # Energy that couldn't fit in cell
    overflow_distribution: Dict[Tuple[int, int], float] = field(default_factory=dict)  # Cell → energy

    # Metadata
    event: Optional[CollisionEvent] = None


# ============================================================================
# Collision Regime Classifier
# ============================================================================

class CollisionRegimeClassifier:
    """
    Classifies collision type based on pattern overlap and cell capacity.

    Uses PatternOverlapCalculator to determine regime.
    """

    def __init__(
        self,
        E_max: float = 15.0,
        overlap_calculator: Optional[PatternOverlapCalculator] = None
    ):
        """
        Args:
            E_max: Cell capacity limit (default from v12 config)
            overlap_calculator: Pattern overlap calculator (creates default if None)
        """
        self.E_max = E_max
        self.overlap_calculator = overlap_calculator or PatternOverlapCalculator()

    def classify(
        self,
        patterns: List[Pattern],
        cell_position: Tuple[int, int],
        tick: int
    ) -> Tuple[str, float, float]:
        """
        Classify collision regime for patterns in same cell.

        Args:
            patterns: List of Pattern objects in collision
            cell_position: Grid cell coordinates
            tick: Current simulation tick

        Returns:
            (regime, E_overlap, E_total) where:
                regime: "merge", "explode", or "excite"
                E_overlap: Energy from pattern overlap
                E_total: Total energy (patterns + overlap)
        """
        if len(patterns) < 2:
            raise ValueError("Need at least 2 patterns for collision")

        # For now, handle pairwise collisions only
        # Multi-pattern collisions (3+) are resolved sequentially
        if len(patterns) == 2:
            p_A, p_B = patterns[0], patterns[1]
            regime, E_overlap = self.overlap_calculator.classify_overlap(
                p_A, p_B, self.E_max
            )
            E_total = p_A.energy + p_B.energy + E_overlap
            return regime, E_overlap, E_total
        else:
            # Multi-collision: resolve first pair, then recurse
            # This is a simplification - real multi-collision physics TBD
            p_A, p_B = patterns[0], patterns[1]
            regime, E_overlap = self.overlap_calculator.classify_overlap(
                p_A, p_B, self.E_max
            )
            E_total = sum(p.energy for p in patterns) + E_overlap
            return regime, E_overlap, E_total


# ============================================================================
# Regime 3.1: Merge Resolver
# ============================================================================

class MergeResolver:
    """
    Resolves merge collisions: non-overlapping patterns → composite.

    Physics:
    - Patterns combine into new composite pattern
    - Total energy conserved: E_composite = E_A + E_B
    - Like fusion: hydrogen + hydrogen → helium
    """

    def __init__(self):
        self.merges_resolved = 0

    def resolve(
        self,
        patterns: List[Pattern],
        entity_ids: List[str],
        cell_position: Tuple[int, int],
        tick: int
    ) -> CollisionOutcome:
        """
        Create composite pattern from merging patterns.

        Args:
            patterns: List of Pattern objects to merge
            entity_ids: IDs of entities being merged
            cell_position: Grid cell coordinates
            tick: Current simulation tick

        Returns:
            CollisionOutcome with new composite entity
        """
        if len(patterns) != 2:
            raise NotImplementedError("Multi-pattern merge (3+) not yet implemented")

        p_A, p_B = patterns

        # Create composite pattern
        # For now, use simple rules (can be refined)
        composite_type = self._determine_composite_type(p_A.pattern_type, p_B.pattern_type)
        composite_energy = p_A.energy + p_B.energy
        composite_mass = p_A.mass + p_B.mass
        composite_mode = (p_A.internal_mode + p_B.internal_mode) // 2  # Average
        composite_phase = (p_A.phase + p_B.phase) / 2  # Average

        composite_pattern = Pattern(
            pattern_type=composite_type,
            energy=composite_energy,
            internal_mode=composite_mode,
            phase=composite_phase,
            mass=composite_mass
        )

        # Create collision event
        event = CollisionEvent(
            entity_ids=tuple(entity_ids),
            cell_position=cell_position,
            tick=tick,
            regime="merge",
            E_overlap=0.0,  # By definition, merge has minimal overlap
            E_total=composite_energy,
            E_final=composite_energy,
            outcome=f"Merged {p_A.pattern_type.value} + {p_B.pattern_type.value} -> {composite_type.value}"
        )

        self.merges_resolved += 1

        return CollisionOutcome(
            surviving_entities=[],
            new_entities=[composite_pattern],
            destroyed_entity_ids=entity_ids,
            energy_overflow=0.0,
            event=event
        )

    def _determine_composite_type(
        self,
        type_A: PatternType,
        type_B: PatternType
    ) -> PatternType:
        """
        Determine composite pattern type from constituents.

        Fusion rules (simplified):
        - Proton + Neutron → Deuterium
        - Proton + Proton → Helium (if energies high enough)
        - Generic: Use placeholder composite type
        """
        fusion_rules = {
            (PatternType.PROTON, PatternType.NEUTRON): PatternType.DEUTERIUM,
            (PatternType.NEUTRON, PatternType.PROTON): PatternType.DEUTERIUM,
            (PatternType.ELECTRON, PatternType.PROTON): PatternType.HYDROGEN,
            (PatternType.PROTON, PatternType.ELECTRON): PatternType.HYDROGEN,
        }

        composite = fusion_rules.get((type_A, type_B), None)
        if composite:
            return composite

        # Default: create generic composite
        # (In full implementation, would track composite structure)
        return PatternType.HYDROGEN  # Placeholder


# ============================================================================
# Regime 3.2: Explosion Resolver
# ============================================================================

class ExplosionResolver:
    """
    Resolves explosion collisions: overlap + excess energy → energy release.

    Physics:
    - Total energy exceeds cell capacity
    - Overflow energy released to neighboring cells (shockwave)
    - Patterns may be destroyed, fragmented, or scattered
    - Like annihilation: electron + positron → photons
    """

    def __init__(self, E_max: float = 15.0):
        """
        Args:
            E_max: Cell capacity limit
        """
        self.E_max = E_max
        self.explosions_resolved = 0

    def resolve(
        self,
        patterns: List[Pattern],
        entity_ids: List[str],
        cell_position: Tuple[int, int],
        E_overlap: float,
        tick: int
    ) -> CollisionOutcome:
        """
        Release energy overflow and handle pattern destruction.

        Args:
            patterns: List of Pattern objects in collision
            entity_ids: IDs of colliding entities
            cell_position: Grid cell coordinates
            E_overlap: Overlap energy
            tick: Current simulation tick

        Returns:
            CollisionOutcome with energy overflow distribution
        """
        if len(patterns) != 2:
            raise NotImplementedError("Multi-pattern explosion (3+) not yet implemented")

        p_A, p_B = patterns

        # Calculate total energy and overflow
        E_total = p_A.energy + p_B.energy + E_overlap
        E_overflow = E_total - self.E_max

        # Distribute overflow to neighbors
        overflow_distribution = self._distribute_overflow_to_neighbors(
            cell_position, E_overflow
        )

        # Determine outcome: annihilation vs scattering
        if p_A.pattern_type.is_antimatter_of(p_B.pattern_type):
            # Matter-antimatter annihilation -> photons
            outcome_description = f"Annihilation: {p_A.pattern_type.value} + {p_B.pattern_type.value} -> photons"
            new_entities = self._create_photon_pair(E_total - E_overflow)
            destroyed_ids = entity_ids
        else:
            # Scattering or fragmentation
            outcome_description = f"Explosion: fragments scattered"
            new_entities = []  # Simplified: patterns destroyed
            destroyed_ids = entity_ids

        # Create collision event
        event = CollisionEvent(
            entity_ids=tuple(entity_ids),
            cell_position=cell_position,
            tick=tick,
            regime="explode",
            E_overlap=E_overlap,
            E_total=E_total,
            E_final=E_total - E_overflow,  # Energy remaining in cell
            outcome=outcome_description
        )

        self.explosions_resolved += 1

        return CollisionOutcome(
            surviving_entities=[],
            new_entities=new_entities,
            destroyed_entity_ids=destroyed_ids,
            energy_overflow=E_overflow,
            overflow_distribution=overflow_distribution,
            event=event
        )

    def _distribute_overflow_to_neighbors(
        self,
        cell_position: Tuple[int, int],
        E_overflow: float
    ) -> Dict[Tuple[int, int], float]:
        """
        Distribute overflow energy to 8 neighboring cells.

        Shockwave propagation: energy spreads isotropically.

        Args:
            cell_position: Origin cell (ix, iy)
            E_overflow: Total overflow energy

        Returns:
            Dictionary mapping neighbor cells to energy amounts
        """
        ix, iy = cell_position

        # 8 neighbors (Moore neighborhood)
        neighbors = [
            (ix - 1, iy - 1), (ix, iy - 1), (ix + 1, iy - 1),
            (ix - 1, iy),                   (ix + 1, iy),
            (ix - 1, iy + 1), (ix, iy + 1), (ix + 1, iy + 1),
        ]

        # Equal distribution to all neighbors
        E_per_neighbor = E_overflow / len(neighbors)

        distribution = {neighbor: E_per_neighbor for neighbor in neighbors}

        return distribution

    def _create_photon_pair(self, E_available: float) -> List[Pattern]:
        """
        Create photon pair from annihilation energy.

        Args:
            E_available: Energy available for photons

        Returns:
            List of photon Pattern objects
        """
        # Create two photons with equal energy (symmetric emission)
        E_photon = E_available / 2

        photon_1 = Pattern(
            pattern_type=PatternType.PHOTON,
            energy=E_photon,
            internal_mode=0,
            phase=0.0,
            mass=0.0
        )

        photon_2 = Pattern(
            pattern_type=PatternType.PHOTON,
            energy=E_photon,
            internal_mode=0,
            phase=math.pi,  # Opposite phase
            mass=0.0
        )

        return [photon_1, photon_2]


# ============================================================================
# Regime 3.3: Excitation Resolver
# ============================================================================

class ExcitationResolver:
    """
    Resolves excitation collisions: partial overlap → energy redistribution.

    Physics:
    - Patterns overlap but total energy within capacity
    - Overlap energy redistributed within patterns
    - No energy released externally
    - Like photon absorption: atom + photon → excited atom
    """

    def __init__(self):
        self.excitations_resolved = 0

    def resolve(
        self,
        patterns: List[Pattern],
        entity_ids: List[str],
        cell_position: Tuple[int, int],
        E_overlap: float,
        tick: int
    ) -> CollisionOutcome:
        """
        Redistribute energy among patterns.

        Args:
            patterns: List of Pattern objects in collision
            entity_ids: IDs of colliding entities
            cell_position: Grid cell coordinates
            E_overlap: Overlap energy to redistribute
            tick: Current simulation tick

        Returns:
            CollisionOutcome with modified patterns
        """
        if len(patterns) != 2:
            raise NotImplementedError("Multi-pattern excitation (3+) not yet implemented")

        p_A, p_B = patterns

        # Redistribute overlap energy proportionally
        E_total_initial = p_A.energy + p_B.energy
        fraction_A = p_A.energy / E_total_initial if E_total_initial > 0 else 0.5
        fraction_B = p_B.energy / E_total_initial if E_total_initial > 0 else 0.5

        E_A_new = p_A.energy + fraction_A * E_overlap
        E_B_new = p_B.energy + fraction_B * E_overlap

        # Create modified patterns
        p_A_excited = p_A.copy()
        p_A_excited.energy = E_A_new
        p_A_excited.internal_mode += 1  # Transition to excited state

        p_B_excited = p_B.copy()
        p_B_excited.energy = E_B_new
        p_B_excited.internal_mode += 1

        # Create collision event
        event = CollisionEvent(
            entity_ids=tuple(entity_ids),
            cell_position=cell_position,
            tick=tick,
            regime="excite",
            E_overlap=E_overlap,
            E_total=E_total_initial + E_overlap,
            E_final=E_A_new + E_B_new,
            outcome=f"Excitation: patterns redistributed energy (dE = {E_overlap:.3f})"
        )

        self.excitations_resolved += 1

        return CollisionOutcome(
            surviving_entities=[p_A_excited, p_B_excited],
            new_entities=[],
            destroyed_entity_ids=[],  # Patterns survive, just modified
            energy_overflow=0.0,
            event=event
        )


# ============================================================================
# Main Collision Processor
# ============================================================================

class ThreeRegimeCollisionProcessor:
    """
    Main collision processor integrating all three regimes.

    Replaces v12's ElasticScatteringResolver with full tick-frame physics.
    """

    def __init__(self, E_max: float = 15.0):
        """
        Args:
            E_max: Cell capacity limit
        """
        self.E_max = E_max

        # Components
        self.classifier = CollisionRegimeClassifier(E_max=E_max)
        self.merge_resolver = MergeResolver()
        self.explosion_resolver = ExplosionResolver(E_max=E_max)
        self.excitation_resolver = ExcitationResolver()

        # Statistics
        self.collision_history: List[CollisionEvent] = []

    def process_collision(
        self,
        patterns: List[Pattern],
        entity_ids: List[str],
        cell_position: Tuple[int, int],
        tick: int
    ) -> CollisionOutcome:
        """
        Process collision using appropriate regime.

        Args:
            patterns: List of Pattern objects in collision
            entity_ids: IDs of colliding entities
            cell_position: Grid cell coordinates
            tick: Current simulation tick

        Returns:
            CollisionOutcome describing result
        """
        # Classify regime
        regime, E_overlap, E_total = self.classifier.classify(
            patterns, cell_position, tick
        )

        # Resolve based on regime
        if regime == "merge":
            outcome = self.merge_resolver.resolve(
                patterns, entity_ids, cell_position, tick
            )
        elif regime == "explode":
            outcome = self.explosion_resolver.resolve(
                patterns, entity_ids, cell_position, E_overlap, tick
            )
        elif regime == "excite":
            outcome = self.excitation_resolver.resolve(
                patterns, entity_ids, cell_position, E_overlap, tick
            )
        else:
            raise ValueError(f"Unknown regime: {regime}")

        # Record event
        if outcome.event:
            self.collision_history.append(outcome.event)

        return outcome

    def get_statistics(self) -> dict:
        """Return collision statistics."""
        return {
            'total_collisions': len(self.collision_history),
            'merges': self.merge_resolver.merges_resolved,
            'explosions': self.explosion_resolver.explosions_resolved,
            'excitations': self.excitation_resolver.excitations_resolved,
        }


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("THREE-REGIME COLLISION FRAMEWORK - EXPERIMENT 55")
    print("=" * 70)
    print()

    processor = ThreeRegimeCollisionProcessor(E_max=15.0)

    # Test 1: Matter-Antimatter Annihilation (Explosion)
    print("Test 1: Matter-Antimatter Annihilation")
    print("-" * 70)
    electron, positron = create_matter_antimatter_pair(energy=10.0, particle_type=PatternType.ELECTRON)
    outcome = processor.process_collision(
        patterns=[electron, positron],
        entity_ids=["e1", "e2"],
        cell_position=(50, 50),
        tick=1000
    )
    print(f"  Regime: {outcome.event.regime}")
    print(f"  Outcome: {outcome.event.outcome}")
    print(f"  New entities: {len(outcome.new_entities)}")
    print(f"  Energy overflow: {outcome.energy_overflow:.3f}")
    print(f"  Neighbors receiving energy: {len(outcome.overflow_distribution)}")
    print()

    # Test 2: Fusion (Merge)
    print("Test 2: Proton-Neutron Fusion")
    print("-" * 70)
    proton = Pattern(PatternType.PROTON, energy=10.0, mass=1.0)
    neutron = Pattern(PatternType.NEUTRON, energy=10.0, mass=1.0)
    outcome = processor.process_collision(
        patterns=[proton, neutron],
        entity_ids=["p1", "n1"],
        cell_position=(50, 50),
        tick=1001
    )
    print(f"  Regime: {outcome.event.regime}")
    print(f"  Outcome: {outcome.event.outcome}")
    print(f"  New entities: {len(outcome.new_entities)}")
    if outcome.new_entities:
        composite = outcome.new_entities[0]
        print(f"  Composite type: {composite.pattern_type.value}")
        print(f"  Composite energy: {composite.energy:.3f}")
    print()

    # Test 3: Statistics
    print("Test 3: Collision Statistics")
    print("-" * 70)
    stats = processor.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    print("=" * 70)
    print("Three-regime collision framework loaded successfully!")
    print("=" * 70)
