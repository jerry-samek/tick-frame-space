#!/usr/bin/env python3
"""
Collision Integration for Experiment 52 V13

Integrates Experiment 55's three-regime collision physics into field simulation loop.

This module:
1. Detects collisions (same grid cell)
2. Resolves collisions using three-regime framework
3. Creates/destroys/modifies entities
4. Tracks conservation laws
"""

import numpy as np
from typing import List, Tuple, Dict
from collections import defaultdict
import sys
from pathlib import Path

# Import collision framework from Experiment 55
sys.path.append(str(Path(__file__).parent.parent.parent / "55_collision_physics"))
from pattern_overlap import Pattern, PatternType
from collision_regimes import (
    CollisionRegimeClassifier,
    MergeResolver,
    ExplosionResolver,
    ExcitationResolver,
    CollisionEvent,
    CollisionOutcome
)

# Import entity adapter
from entity_adapter import PatternEntity


class CollisionManager:
    """
    Manages collision detection and resolution for PatternEntity objects.

    Integrates Experiment 55 framework with field simulation.
    """

    def __init__(
        self,
        E_max: float = 15.0,
        grid_size: int = 100,
        c: float = 1.0
    ):
        """
        Args:
            E_max: Cell capacity limit
            grid_size: Size of simulation grid
            c: Speed of light (for speed clamping)
        """
        self.E_max = E_max
        self.grid_size = grid_size
        self.c = c

        # Collision framework components
        self.classifier = CollisionRegimeClassifier(E_max=E_max)
        self.merge_resolver = MergeResolver()
        self.explosion_resolver = ExplosionResolver(E_max=E_max)
        self.excitation_resolver = ExcitationResolver()

        # Statistics
        self.total_collisions = 0
        self.collisions_by_regime = {
            "merge": 0,
            "explode": 0,
            "excite": 0
        }
        self.collision_history: List[CollisionEvent] = []

        # Conservation tracking
        self.initial_momentum = None
        self.initial_energy = None

    def detect_collisions(
        self,
        entities: List[PatternEntity],
        tick: int
    ) -> Dict[Tuple[int, int], List[PatternEntity]]:
        """
        Detect entities in same grid cell.

        Args:
            entities: List of PatternEntity objects
            tick: Current simulation tick

        Returns:
            Dict mapping cell coordinates to list of entities in that cell
            (Only cells with 2+ entities are included)
        """
        cell_map: Dict[Tuple[int, int], List[PatternEntity]] = defaultdict(list)

        for entity in entities:
            cell = entity.get_cell_coordinates()
            cell_map[cell].append(entity)

        # Filter to only cells with collisions
        collisions = {cell: entities_in_cell
                     for cell, entities_in_cell in cell_map.items()
                     if len(entities_in_cell) >= 2}

        return collisions

    def resolve_collision(
        self,
        entities_in_cell: List[PatternEntity],
        cell: Tuple[int, int],
        tick: int
    ) -> CollisionOutcome:
        """
        Resolve collision in a single cell.

        Args:
            entities_in_cell: List of entities in same cell
            cell: Cell coordinates
            tick: Current simulation tick

        Returns:
            CollisionOutcome with results
        """
        # Extract patterns
        patterns = [e.to_pattern() for e in entities_in_cell]
        entity_ids = [e.entity_id for e in entities_in_cell]

        # Classify collision regime
        regime, E_overlap, E_total = self.classifier.classify(patterns, cell, tick)

        # Resolve based on regime
        if regime == "merge":
            outcome = self.merge_resolver.resolve(patterns, entity_ids, cell, tick)
        elif regime == "explode":
            outcome = self.explosion_resolver.resolve(patterns, entity_ids, cell, E_overlap, tick)
        elif regime == "excite":
            outcome = self.excitation_resolver.resolve(patterns, entity_ids, cell, E_overlap, tick)
        else:
            raise ValueError(f"Unknown collision regime: {regime}")

        # Update statistics
        self.total_collisions += 1
        self.collisions_by_regime[regime] += 1
        if outcome.event:
            self.collision_history.append(outcome.event)

        return outcome

    def convert_outcome_to_entities(
        self,
        outcome: CollisionOutcome,
        original_entities: List[PatternEntity],
        cell: Tuple[int, int]
    ) -> List[PatternEntity]:
        """
        Convert CollisionOutcome back to PatternEntity objects.

        Args:
            outcome: Collision outcome with new/modified patterns
            original_entities: Original entities before collision
            cell: Cell coordinates

        Returns:
            List of PatternEntity objects after collision
        """
        result_entities = []

        # Process new entities (from merge or explosion)
        for i, new_pattern in enumerate(outcome.new_entities):
            # Position: center of cell + small random offset
            pos = np.array([float(cell[0]) + 0.5 + np.random.uniform(-0.1, 0.1),
                           float(cell[1]) + 0.5 + np.random.uniform(-0.1, 0.1)])

            # Velocity: average of original entities (or random for fragments)
            if len(original_entities) > 0:
                avg_velocity = np.mean([e.velocity for e in original_entities], axis=0)
            else:
                avg_velocity = np.array([0.0, 0.0])

            # For explosion regime, add random scatter
            if outcome.event and outcome.event.regime == "explode":
                scatter_angle = np.random.uniform(0, 2*np.pi)
                scatter_speed = np.random.uniform(0.1, 0.3) * self.c
                avg_velocity += np.array([scatter_speed * np.cos(scatter_angle),
                                         scatter_speed * np.sin(scatter_angle)])

            # Create entity
            entity = PatternEntity.from_pattern(
                pattern=new_pattern,
                position=pos,
                velocity=avg_velocity,
                entity_id=f"collision_product_{self.total_collisions}_{i}",
                tick_budget=1
            )

            # Clamp speed
            entity.clamp_speed(self.c)

            result_entities.append(entity)

        # Process surviving modified entities
        # (For excitation regime, patterns are modified in-place)
        for modified_entity in outcome.surviving_entities:
            # Find corresponding original entity
            for orig_entity in original_entities:
                if orig_entity.entity_id not in outcome.destroyed_entity_ids:
                    # Update pattern with modified one
                    # For now, assume modified_entity is a Pattern
                    if isinstance(modified_entity, Pattern):
                        orig_entity.pattern = modified_entity
                        result_entities.append(orig_entity)
                        break

        return result_entities

    def process_all_collisions(
        self,
        entities: List[PatternEntity],
        tick: int
    ) -> Tuple[List[PatternEntity], Dict]:
        """
        Detect and resolve all collisions in current tick.

        Args:
            entities: List of all entities
            tick: Current simulation tick

        Returns:
            (updated_entities, statistics) tuple where:
                updated_entities: List of entities after collision resolution
                statistics: Dict with collision stats for this tick
        """
        # Detect collisions
        collision_cells = self.detect_collisions(entities, tick)

        if len(collision_cells) == 0:
            # No collisions this tick
            return entities, {
                "num_cells_with_collisions": 0,
                "total_colliding_entities": 0,
                "collisions_by_regime": {"merge": 0, "explode": 0, "excite": 0}
            }

        # Track which entities are involved in collisions
        colliding_entity_ids = set()
        for entities_in_cell in collision_cells.values():
            for entity in entities_in_cell:
                colliding_entity_ids.add(entity.entity_id)

        # Resolve each collision (pairwise if multiple entities in cell)
        non_colliding_entities = [e for e in entities if e.entity_id not in colliding_entity_ids]
        collision_products = []

        regime_counts = {"merge": 0, "explode": 0, "excite": 0}

        for cell, entities_in_cell in collision_cells.items():
            # For cells with 2 entities: resolve directly
            # For cells with 3+ entities: resolve first pair only (simplified)
            if len(entities_in_cell) >= 2:
                # Take first two entities for collision
                pair = entities_in_cell[:2]
                non_pair = entities_in_cell[2:]

                # Resolve collision
                outcome = self.resolve_collision(pair, cell, tick)

                # Count regime
                if outcome.event:
                    regime_counts[outcome.event.regime] += 1

                # Convert outcome to entities
                result_entities = self.convert_outcome_to_entities(
                    outcome,
                    pair,
                    cell
                )

                collision_products.extend(result_entities)
                collision_products.extend(non_pair)  # Add remaining entities unchanged

                # Mark entities as having collided
                for entity in result_entities:
                    entity.mark_collision(tick)
            else:
                # Single entity in cell (shouldn't happen, but be safe)
                collision_products.extend(entities_in_cell)

        # Combine non-colliding + collision products
        updated_entities = non_colliding_entities + collision_products

        # Statistics
        stats = {
            "num_cells_with_collisions": len(collision_cells),
            "total_colliding_entities": len(colliding_entity_ids),
            "collisions_by_regime": regime_counts,
            "entities_before": len(entities),
            "entities_after": len(updated_entities)
        }

        return updated_entities, stats

    def compute_total_momentum(self, entities: List[PatternEntity]) -> np.ndarray:
        """
        Compute total momentum of all entities.

        Args:
            entities: List of entities

        Returns:
            Total momentum vector (px, py)
        """
        total_p = np.zeros(2)
        for entity in entities:
            p = entity.pattern.mass * entity.velocity
            total_p += p
        return total_p

    def compute_total_energy(self, entities: List[PatternEntity]) -> float:
        """
        Compute total kinetic energy of all entities.

        Args:
            entities: List of entities

        Returns:
            Total kinetic energy
        """
        total_E = 0.0
        for entity in entities:
            v2 = np.dot(entity.velocity, entity.velocity)
            KE = 0.5 * entity.pattern.mass * v2
            total_E += KE + entity.pattern.energy  # KE + internal energy
        return total_E

    def check_conservation(
        self,
        entities: List[PatternEntity],
        tick: int,
        verbose: bool = False
    ) -> Dict:
        """
        Check momentum and energy conservation.

        Args:
            entities: Current entity list
            tick: Current tick
            verbose: If True, print warnings

        Returns:
            Dict with conservation statistics
        """
        p_total = self.compute_total_momentum(entities)
        E_total = self.compute_total_energy(entities)

        if self.initial_momentum is None:
            self.initial_momentum = p_total
            self.initial_energy = E_total

        dp = p_total - self.initial_momentum
        dE = E_total - self.initial_energy

        dp_magnitude = np.linalg.norm(dp)
        dE_magnitude = abs(dE)

        if verbose and (dp_magnitude > 0.01 or dE_magnitude > 0.01):
            print(f"  [CONSERVATION WARNING at tick {tick}]")
            print(f"    Momentum drift: {dp_magnitude:.6f} (dp = {dp})")
            print(f"    Energy drift: {dE_magnitude:.6f} (dE = {dE:.6f})")

        return {
            "p_total": p_total,
            "E_total": E_total,
            "dp": dp,
            "dE": dE,
            "dp_magnitude": dp_magnitude,
            "dE_magnitude": dE_magnitude
        }

    def get_statistics(self) -> Dict:
        """Get collision statistics summary."""
        return {
            "total_collisions": self.total_collisions,
            "merge_count": self.collisions_by_regime["merge"],
            "explode_count": self.collisions_by_regime["explode"],
            "excite_count": self.collisions_by_regime["excite"],
            "collision_history_length": len(self.collision_history)
        }


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("COLLISION INTEGRATION MODULE - EXPERIMENT 52 V13")
    print("=" * 70)
    print()

    from entity_adapter import create_proton_entity, create_electron_entity

    # Create collision manager
    manager = CollisionManager(E_max=15.0, grid_size=100, c=1.0)

    # Test 1: Detect collisions
    print("Test 1: Collision Detection")
    print("-" * 70)

    # Create two entities in same cell
    e1 = create_proton_entity("p1", np.array([50.3, 50.2]), np.array([0.1, 0.0]), energy=8.0)
    e2 = create_electron_entity("e1", np.array([50.7, 50.8]), np.array([-0.1, 0.0]), energy=4.0)

    entities = [e1, e2]

    collisions = manager.detect_collisions(entities, tick=0)
    print(f"  Entities: {len(entities)}")
    print(f"  Cells with collisions: {len(collisions)}")
    if collisions:
        for cell, ents in collisions.items():
            print(f"    Cell {cell}: {len(ents)} entities")
    print()

    # Test 2: Process collisions
    print("Test 2: Process Collisions")
    print("-" * 70)

    updated_entities, stats = manager.process_all_collisions(entities, tick=0)

    print(f"  Stats: {stats}")
    print(f"  Entities before: {stats['entities_before']}")
    print(f"  Entities after: {stats['entities_after']}")
    print(f"  Collisions by regime: {stats['collisions_by_regime']}")
    print()

    # Test 3: Conservation check
    print("Test 3: Conservation Check")
    print("-" * 70)

    conservation = manager.check_conservation(updated_entities, tick=0, verbose=True)
    print(f"  Total momentum: {conservation['p_total']}")
    print(f"  Total energy: {conservation['E_total']:.3f}")
    print()

    print("=" * 70)
    print("Collision integration module loaded successfully!")
    print("=" * 70)
