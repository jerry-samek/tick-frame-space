#!/usr/bin/env python3
"""
Minimal Collision Physics Module for Experiment 52 (V12)

SIMPLIFIED MODEL: This is a minimal collision framework for validating c-ring stability.
For full collision physics (three regimes, pattern overlap, composites), see Experiment 55.

Implements:
- Basic collision detection (same cell check)
- Elastic scattering (hard-sphere approximation)
- Momentum conservation

Does NOT implement:
- Pattern overlap computation
- Cell capacity limits
- Energy overflow (explosion regime)
- Pattern merging
- Composite object binding
- Pauli exclusion

Based on theory docs: raw/053, raw/054
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass
import numpy as np
import math


@dataclass
class CollisionEvent:
    """Record of a collision between two entities"""
    entity_ids: Tuple[str, str]
    position: Tuple[int, int]  # Grid cell where collision occurred
    tick: int
    collision_type: str  # "elastic_scatter" for this minimal model


class CollisionDetector:
    """
    Detects when multiple entities occupy the same grid cell.

    This is the fundamental collision detection for tick-frame:
    Collision = pattern allocation conflict (same cell, same tick)
    """

    def __init__(self, grid_spacing: float = 1.0):
        """
        Args:
            grid_spacing: Size of grid cells (default 1.0)
        """
        self.grid_spacing = grid_spacing
        self.collision_history: List[CollisionEvent] = []

    def get_cell_coordinates(self, position: np.ndarray) -> Tuple[int, int]:
        """
        Convert continuous position to discrete grid cell coordinates.

        Args:
            position: (x, y) continuous coordinates

        Returns:
            (ix, iy) grid cell indices
        """
        x, y = position
        ix = int(math.floor(x / self.grid_spacing))
        iy = int(math.floor(y / self.grid_spacing))
        return (ix, iy)

    def detect_collisions(self, entities, tick: int) -> Dict[Tuple[int, int], List]:
        """
        Group entities by grid cell and identify collisions.

        Args:
            entities: List of MovingEntity objects
            tick: Current simulation tick

        Returns:
            Dictionary mapping cell coordinates to list of entities in that cell
            (Only cells with 2+ entities are included)
        """
        # Build cell map: (ix, iy) -> [entity1, entity2, ...]
        cell_map: Dict[Tuple[int, int], List] = {}

        for entity in entities:
            cell = self.get_cell_coordinates(entity.position)
            if cell not in cell_map:
                cell_map[cell] = []
            cell_map[cell].append(entity)

        # Filter to only cells with collisions (2+ entities)
        collisions = {cell: entities_in_cell
                     for cell, entities_in_cell in cell_map.items()
                     if len(entities_in_cell) >= 2}

        # Record collision events
        for cell, entities_in_cell in collisions.items():
            if len(entities_in_cell) == 2:
                event = CollisionEvent(
                    entity_ids=(entities_in_cell[0].entity_id, entities_in_cell[1].entity_id),
                    position=cell,
                    tick=tick,
                    collision_type="elastic_scatter"
                )
                self.collision_history.append(event)

        return collisions


class ElasticScatteringResolver:
    """
    Resolves collisions using elastic scattering (hard-sphere approximation).

    Physics:
    - Conserves momentum: p_total_before = p_total_after
    - Conserves kinetic energy (elastic)
    - Uses center-of-mass frame transformation

    Limitations:
    - NO pattern overlap computation (assumes non-overlapping patterns, Regime 3.1)
    - NO cell capacity checks (no explosion regime)
    - NO inelastic collisions (no energy dissipation)
    - NO composite formation
    """

    def __init__(self, restitution: float = 1.0):
        """
        Args:
            restitution: Coefficient of restitution (1.0 = fully elastic, 0.0 = fully inelastic)
                        For minimal model, keep at 1.0
        """
        self.restitution = restitution
        self.total_collisions_resolved = 0

    def resolve_pairwise_collision(self, entity_A, entity_B) -> Tuple:
        """
        Resolve elastic collision between two entities.

        Uses 2D elastic collision formula in center-of-mass frame.

        Args:
            entity_A, entity_B: MovingEntity objects

        Returns:
            (velocity_A_new, velocity_B_new): Updated velocities as numpy arrays
        """
        # Extract masses (use tick_budget as proxy for mass)
        m_A = float(entity_A.tick_budget) if entity_A.tick_budget > 0 else 1.0
        m_B = float(entity_B.tick_budget) if entity_B.tick_budget > 0 else 1.0

        # Extract velocities
        v_A = np.array(entity_A.velocity, dtype=float)
        v_B = np.array(entity_B.velocity, dtype=float)

        # Compute center of mass velocity
        v_cm = (m_A * v_A + m_B * v_B) / (m_A + m_B)

        # Transform to CM frame
        v_A_cm = v_A - v_cm
        v_B_cm = v_B - v_cm

        # Elastic collision: velocities reverse in CM frame (for equal mass head-on)
        # For general 2D elastic collision, use momentum conservation

        # Position difference vector (collision normal)
        pos_A = np.array(entity_A.position, dtype=float)
        pos_B = np.array(entity_B.position, dtype=float)
        delta_pos = pos_B - pos_A

        # If entities are at exactly same position, use velocity difference as normal
        if np.linalg.norm(delta_pos) < 1e-10:
            delta_pos = v_B - v_A

        # Normalize collision normal
        if np.linalg.norm(delta_pos) > 1e-10:
            normal = delta_pos / np.linalg.norm(delta_pos)
        else:
            # Degenerate case: use arbitrary perpendicular direction
            normal = np.array([1.0, 0.0])

        # Relative velocity in CM frame
        v_rel_cm = v_A_cm - v_B_cm

        # Velocity component along collision normal
        v_normal = np.dot(v_rel_cm, normal)

        # Only apply collision if entities are approaching (v_normal < 0)
        if v_normal >= 0:
            # Already separating, no collision response needed
            return v_A, v_B

        # Impulse magnitude (2D elastic collision formula)
        impulse_magnitude = -(1 + self.restitution) * v_normal / (1/m_A + 1/m_B)

        # Apply impulse in CM frame
        v_A_cm_new = v_A_cm + (impulse_magnitude / m_A) * normal
        v_B_cm_new = v_B_cm - (impulse_magnitude / m_B) * normal

        # Transform back to lab frame
        v_A_new = v_A_cm_new + v_cm
        v_B_new = v_B_cm_new + v_cm

        # Enforce speed limit (c = 1.0)
        v_A_speed = np.linalg.norm(v_A_new)
        v_B_speed = np.linalg.norm(v_B_new)

        if v_A_speed > 0.9999:
            v_A_new = v_A_new / v_A_speed * 0.9999

        if v_B_speed > 0.9999:
            v_B_new = v_B_new / v_B_speed * 0.9999

        self.total_collisions_resolved += 1

        return v_A_new, v_B_new

    def resolve_multi_entity_collision(self, entities_in_cell) -> List[np.ndarray]:
        """
        Resolve collision involving 3+ entities.

        Simplified approach: Resolve pairwise sequentially.

        Args:
            entities_in_cell: List of MovingEntity objects in same cell

        Returns:
            List of updated velocities
        """
        # For simplicity, resolve pairwise collisions sequentially
        # This is not physically rigorous for 3+ simultaneous collisions
        # but works as a first approximation

        updated_velocities = [np.array(e.velocity, dtype=float) for e in entities_in_cell]

        # Resolve all pairs
        for i in range(len(entities_in_cell)):
            for j in range(i+1, len(entities_in_cell)):
                entity_i = entities_in_cell[i]
                entity_j = entities_in_cell[j]

                # Temporarily update entity velocities for next iteration
                entity_i.velocity = updated_velocities[i]
                entity_j.velocity = updated_velocities[j]

                v_i_new, v_j_new = self.resolve_pairwise_collision(entity_i, entity_j)

                updated_velocities[i] = v_i_new
                updated_velocities[j] = v_j_new

        return updated_velocities


def process_collisions(entities, detector: CollisionDetector, resolver: ElasticScatteringResolver, tick: int):
    """
    Main collision processing function.

    1. Detect all collisions (same cell)
    2. Resolve each collision (update velocities)
    3. Return modified entities

    Args:
        entities: List of MovingEntity objects
        detector: CollisionDetector instance
        resolver: ElasticScatteringResolver instance
        tick: Current simulation tick

    Returns:
        entities with updated velocities
    """
    # Detect collisions
    collisions = detector.detect_collisions(entities, tick)

    if not collisions:
        return entities  # No collisions, nothing to do

    # Resolve each collision
    for cell, entities_in_cell in collisions.items():
        if len(entities_in_cell) == 2:
            # Pairwise collision
            v_A_new, v_B_new = resolver.resolve_pairwise_collision(
                entities_in_cell[0], entities_in_cell[1]
            )
            entities_in_cell[0].velocity = v_A_new
            entities_in_cell[1].velocity = v_B_new

        else:
            # Multi-entity collision (3+)
            updated_velocities = resolver.resolve_multi_entity_collision(entities_in_cell)
            for entity, new_velocity in zip(entities_in_cell, updated_velocities):
                entity.velocity = new_velocity

    return entities


# ============================================================================
# Diagnostic Functions
# ============================================================================

def compute_total_momentum(entities) -> np.ndarray:
    """
    Compute total momentum of all entities.

    Used to verify momentum conservation.
    """
    total_momentum = np.zeros(2)
    for entity in entities:
        mass = float(entity.tick_budget) if entity.tick_budget > 0 else 1.0
        total_momentum += mass * np.array(entity.velocity)
    return total_momentum


def compute_total_kinetic_energy(entities) -> float:
    """
    Compute total kinetic energy of all entities.

    Used to verify energy conservation (elastic collisions).
    """
    total_KE = 0.0
    for entity in entities:
        mass = float(entity.tick_budget) if entity.tick_budget > 0 else 1.0
        v_squared = np.dot(entity.velocity, entity.velocity)
        total_KE += 0.5 * mass * v_squared
    return total_KE
