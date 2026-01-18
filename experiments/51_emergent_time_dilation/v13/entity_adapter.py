#!/usr/bin/env python3
"""
Entity Adapter for Experiment 52 V13

Bridges MovingEntity (from v12) with Pattern (from Experiment 55).

This allows field dynamics (which expects MovingEntity) to work with
collision physics (which expects Pattern).
"""

import numpy as np
from typing import Tuple, List
import sys
from pathlib import Path

# Import Pattern from Experiment 55
sys.path.append(str(Path(__file__).parent.parent.parent / "55_collision_physics"))
from pattern_overlap import Pattern, PatternType

# Import MovingEntity from v11/v12
from entity_motion import MovingEntity, StationaryEntity


class PatternEntity:
    """
    Entity that carries both MovingEntity interface (for fields) and Pattern (for collisions).

    This is the core entity type for v13, combining:
    - Position, velocity, motion (from MovingEntity)
    - Pattern type, energy, internal structure (from Pattern)
    - Field interaction (field_contribution)
    - Collision physics (to_pattern, from_pattern)
    """

    def __init__(
        self,
        entity_id: str,
        position: np.ndarray,
        velocity: np.ndarray,
        pattern: Pattern,
        tick_budget: int = 1
    ):
        """
        Args:
            entity_id: Unique identifier
            position: (x, y) position in grid
            velocity: (vx, vy) velocity in grid units/tick
            pattern: Pattern object from Experiment 55
            tick_budget: Computational ticks per substrate tick
        """
        self.entity_id = entity_id
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.pattern = pattern
        self.tick_budget = tick_budget

        # Tracking
        self.age = 0
        self.last_collision_tick = -1

    # ========================================================================
    # MovingEntity Interface (for field dynamics)
    # ========================================================================

    def field_contribution(self, cell_position: Tuple[int, int], E_max: float) -> float:
        """
        Compute source field contribution at this cell.

        Used by field dynamics to compute S(x,t).

        Args:
            cell_position: Grid cell coordinates (ignored, entity at single position)
            E_max: Maximum energy for normalization

        Returns:
            Source strength contribution
        """
        # Use pattern mass and energy for source
        # Source = mass × (energy / E_max) × velocity_factor

        # Velocity factor (stationary entities contribute more)
        speed = np.linalg.norm(self.velocity)
        velocity_factor = 1.0 / (1.0 + speed)  # Slower entities = stronger source

        contribution = self.pattern.mass * (self.pattern.energy / E_max) * velocity_factor
        return float(contribution)

    def update_position(self, dt: float = 1.0):
        """
        Update position based on current velocity.

        Args:
            dt: Time step
        """
        self.position += self.velocity * dt
        self.age += int(dt)

    def apply_acceleration(self, acceleration: np.ndarray):
        """
        Apply acceleration to velocity (from field gradient).

        Args:
            acceleration: (ax, ay) acceleration vector
        """
        self.velocity += acceleration

    def clamp_speed(self, c: float = 1.0):
        """
        Enforce speed limit (v ≤ c).

        Args:
            c: Speed of light in grid units/tick
        """
        speed = np.linalg.norm(self.velocity)
        if speed > c:
            self.velocity = (self.velocity / speed) * c

    # ========================================================================
    # Pattern Interface (for collision physics)
    # ========================================================================

    def to_pattern(self) -> Pattern:
        """Return Pattern object for collision detection."""
        return self.pattern

    @classmethod
    def from_pattern(
        cls,
        pattern: Pattern,
        position: np.ndarray,
        velocity: np.ndarray,
        entity_id: str = None,
        tick_budget: int = 1
    ):
        """
        Create PatternEntity from Pattern (used after collision).

        Args:
            pattern: Pattern object
            position: Position in grid
            velocity: Velocity vector
            entity_id: Optional entity ID (generates default if None)
            tick_budget: Computational ticks per substrate tick

        Returns:
            PatternEntity instance
        """
        if entity_id is None:
            entity_id = f"pattern_{pattern.pattern_type.value}_{id(pattern)}"

        return cls(
            entity_id=entity_id,
            position=position,
            velocity=velocity,
            pattern=pattern,
            tick_budget=tick_budget
        )

    # ========================================================================
    # Collision Tracking
    # ========================================================================

    def mark_collision(self, tick: int):
        """Mark that this entity participated in a collision."""
        self.last_collision_tick = tick

    def ticks_since_collision(self, current_tick: int) -> int:
        """Get number of ticks since last collision."""
        if self.last_collision_tick < 0:
            return current_tick  # Never collided
        return current_tick - self.last_collision_tick

    # ========================================================================
    # Utility
    # ========================================================================

    def get_cell_coordinates(self) -> Tuple[int, int]:
        """Get grid cell coordinates."""
        ix = int(np.floor(self.position[0]))
        iy = int(np.floor(self.position[1]))
        return (ix, iy)

    def __repr__(self):
        return (
            f"PatternEntity(id={self.entity_id}, "
            f"pos={tuple(self.position)}, "
            f"v={tuple(self.velocity)}, "
            f"pattern={self.pattern.pattern_type.value}, "
            f"E={self.pattern.energy:.1f})"
        )


# ============================================================================
# Factory Functions
# ============================================================================

def create_proton_entity(
    entity_id: str,
    position: np.ndarray,
    velocity: np.ndarray = None,
    energy: float = 10.0
) -> PatternEntity:
    """
    Create a proton PatternEntity.

    Args:
        entity_id: Unique identifier
        position: (x, y) position
        velocity: (vx, vy) velocity (defaults to zero)
        energy: Energy value

    Returns:
        PatternEntity with PROTON pattern
    """
    if velocity is None:
        velocity = np.array([0.0, 0.0])

    proton_pattern = Pattern(
        pattern_type=PatternType.PROTON,
        energy=energy,
        mass=1.0,
        internal_mode=0,
        phase=0.0
    )

    return PatternEntity(
        entity_id=entity_id,
        position=position,
        velocity=velocity,
        pattern=proton_pattern,
        tick_budget=1
    )


def create_electron_entity(
    entity_id: str,
    position: np.ndarray,
    velocity: np.ndarray = None,
    energy: float = 5.0
) -> PatternEntity:
    """
    Create an electron PatternEntity.

    Args:
        entity_id: Unique identifier
        position: (x, y) position
        velocity: (vx, vy) velocity (defaults to zero)
        energy: Energy value

    Returns:
        PatternEntity with ELECTRON pattern
    """
    if velocity is None:
        velocity = np.array([0.0, 0.0])

    electron_pattern = Pattern(
        pattern_type=PatternType.ELECTRON,
        energy=energy,
        mass=0.001,
        internal_mode=0,
        phase=0.0
    )

    return PatternEntity(
        entity_id=entity_id,
        position=position,
        velocity=velocity,
        pattern=electron_pattern,
        tick_budget=1
    )


def create_neutron_entity(
    entity_id: str,
    position: np.ndarray,
    velocity: np.ndarray = None,
    energy: float = 10.0
) -> PatternEntity:
    """
    Create a neutron PatternEntity.

    Args:
        entity_id: Unique identifier
        position: (x, y) position
        velocity: (vx, vy) velocity (defaults to zero)
        energy: Energy value

    Returns:
        PatternEntity with NEUTRON pattern
    """
    if velocity is None:
        velocity = np.array([0.0, 0.0])

    neutron_pattern = Pattern(
        pattern_type=PatternType.NEUTRON,
        energy=energy,
        mass=1.0,
        internal_mode=0,
        phase=0.0
    )

    return PatternEntity(
        entity_id=entity_id,
        position=position,
        velocity=velocity,
        pattern=neutron_pattern,
        tick_budget=1
    )


# ============================================================================
# Batch Creation Functions
# ============================================================================

def create_planet_cluster_pattern_entities(
    center: Tuple[float, float],
    radius: float,
    count: int,
    energy: float = 10.0
) -> List[PatternEntity]:
    """
    Create a cluster of stationary proton entities (planet/black hole core).

    Args:
        center: (x, y) center position
        radius: Cluster radius
        count: Number of entities
        energy: Energy per entity

    Returns:
        List of PatternEntity objects
    """
    entities = []

    for i in range(count):
        # Random position in sphere
        r = radius * np.sqrt(np.random.random())
        theta = 2 * np.pi * np.random.random()

        x = center[0] + r * np.cos(theta)
        y = center[1] + r * np.sin(theta)

        entity = create_proton_entity(
            entity_id=f"planet_{i}",
            position=np.array([x, y]),
            velocity=np.array([0.0, 0.0]),  # Stationary
            energy=energy
        )

        entities.append(entity)

    return entities


def create_test_particles_mixed(
    center: Tuple[float, float],
    distances: List[float],
    velocities: List[float],
    c: float = 1.0
) -> List[PatternEntity]:
    """
    Create test particles at various distances with mixed types.

    Args:
        center: (x, y) center position
        distances: List of radii to place particles
        velocities: List of tangential velocities (in units of c)
        c: Speed of light

    Returns:
        List of PatternEntity objects
    """
    entities = []
    entity_id_counter = 0

    for distance in distances:
        for v_frac in velocities:
            # Alternate between protons and electrons
            if entity_id_counter % 2 == 0:
                pattern_type = "proton"
                energy = 10.0
            else:
                pattern_type = "electron"
                energy = 5.0

            # Position at distance (start at θ=0, will be distributed)
            angle = (entity_id_counter * 137.5) % 360  # Golden angle distribution
            theta = np.radians(angle)

            x = center[0] + distance * np.cos(theta)
            y = center[1] + distance * np.sin(theta)

            # Tangential velocity
            v_mag = v_frac * c
            vx = -v_mag * np.sin(theta)
            vy = v_mag * np.cos(theta)

            # Create entity
            if pattern_type == "proton":
                entity = create_proton_entity(
                    entity_id=f"test_{pattern_type}_{entity_id_counter}",
                    position=np.array([x, y]),
                    velocity=np.array([vx, vy]),
                    energy=energy
                )
            else:
                entity = create_electron_entity(
                    entity_id=f"test_{pattern_type}_{entity_id_counter}",
                    position=np.array([x, y]),
                    velocity=np.array([vx, vy]),
                    energy=energy
                )

            entities.append(entity)
            entity_id_counter += 1

    return entities


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ENTITY ADAPTER MODULE - EXPERIMENT 52 V13")
    print("=" * 70)
    print()

    # Test 1: Create proton entity
    print("Test 1: Create Proton Entity")
    print("-" * 70)
    proton = create_proton_entity(
        entity_id="test_proton",
        position=np.array([50.0, 50.0]),
        velocity=np.array([0.1, 0.0]),
        energy=10.0
    )
    print(f"  {proton}")
    print(f"  Pattern type: {proton.pattern.pattern_type.value}")
    print(f"  Mass: {proton.pattern.mass}")
    print(f"  Energy: {proton.pattern.energy}")
    print()

    # Test 2: Field contribution
    print("Test 2: Field Contribution")
    print("-" * 70)
    contribution = proton.field_contribution((50, 50), E_max=15.0)
    print(f"  Field contribution: {contribution:.3f}")
    print()

    # Test 3: Pattern conversion
    print("Test 3: Pattern Conversion")
    print("-" * 70)
    pattern = proton.to_pattern()
    print(f"  Extracted pattern: type={pattern.pattern_type.value}, E={pattern.energy}")
    print()

    # Test 4: Create from pattern
    print("Test 4: Create from Pattern")
    print("-" * 70)
    new_entity = PatternEntity.from_pattern(
        pattern=pattern,
        position=np.array([60.0, 60.0]),
        velocity=np.array([0.2, 0.1]),
        entity_id="recreated"
    )
    print(f"  {new_entity}")
    print()

    # Test 5: Create planet cluster
    print("Test 5: Create Planet Cluster")
    print("-" * 70)
    planet_cluster = create_planet_cluster_pattern_entities(
        center=(50.0, 50.0),
        radius=10.0,
        count=100,
        energy=10.0
    )
    print(f"  Created {len(planet_cluster)} planet entities")
    print(f"  Sample: {planet_cluster[0]}")
    print()

    # Test 6: Create mixed test particles
    print("Test 6: Create Mixed Test Particles")
    print("-" * 70)
    test_particles = create_test_particles_mixed(
        center=(50.0, 50.0),
        distances=[20.0, 30.0],
        velocities=[0.0, 0.3],
        c=1.0
    )
    print(f"  Created {len(test_particles)} test particles")
    protons = [e for e in test_particles if e.pattern.pattern_type == PatternType.PROTON]
    electrons = [e for e in test_particles if e.pattern.pattern_type == PatternType.ELECTRON]
    print(f"  Protons: {len(protons)}")
    print(f"  Electrons: {len(electrons)}")
    print(f"  Sample proton: {protons[0]}")
    print(f"  Sample electron: {electrons[0]}")
    print()

    print("=" * 70)
    print("Entity adapter module loaded successfully!")
    print("=" * 70)
