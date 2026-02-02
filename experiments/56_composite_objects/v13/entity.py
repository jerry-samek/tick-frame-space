"""
V13 Entity - An entity with its own field layer.

Each entity:
- Has a unique ID = birth tick
- Owns one layer in the MultiLayerGrid
- Is born at origin [0, 0] (head prepending)
- Persists forever (no death at substrate level)

Key insight: Like Prolog lists, new entities prepend:
    [NewEntity | ExistingUniverse]

Author: V13 Implementation
Date: 2026-01-31
Based on: V12d substrate model + head-prepending concept
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Entity:
    """An entity with its own field layer.

    Entities are born at origin and own a dedicated layer.
    Layer index = entity_id = birth_tick.
    """

    entity_id: int
    """Unique entity identifier (= birth tick)."""

    birth_tick: int
    """Tick at which entity was created."""

    layer_id: int
    """Layer index in MultiLayerGrid (same as entity_id)."""

    position: Tuple[int, int] = field(default_factory=lambda: (0, 0))
    """Current position (center of pattern). Always [0,0] at birth."""

    @property
    def age(self) -> int:
        """Age of entity in ticks (requires external tick count)."""
        # Note: This is a placeholder - age = current_tick - birth_tick
        # Must be calculated externally
        return 0

    def get_age_at_tick(self, current_tick: int) -> int:
        """Calculate age at a specific tick.

        Args:
            current_tick: Current tick count

        Returns:
            Age in ticks
        """
        return current_tick - self.birth_tick

    def __repr__(self) -> str:
        return (
            f"Entity(id={self.entity_id}, "
            f"birth={self.birth_tick}, "
            f"layer={self.layer_id}, "
            f"pos={self.position})"
        )


def create_entity(tick: int, layer_id: int, origin: Tuple[int, int] = (0, 0)) -> Entity:
    """Factory function to create an entity.

    Args:
        tick: Current tick (becomes entity_id and birth_tick)
        layer_id: Layer index in MultiLayerGrid
        origin: Birth position (default: origin [0, 0])

    Returns:
        New Entity instance
    """
    return Entity(
        entity_id=tick,
        birth_tick=tick,
        layer_id=layer_id,
        position=origin
    )


if __name__ == "__main__":
    print("Entity Demo")
    print("=" * 70)

    # Create entities at different ticks
    e1 = create_entity(tick=1, layer_id=0)
    e2 = create_entity(tick=2, layer_id=1)
    e3 = create_entity(tick=3, layer_id=2)

    print("Created entities:")
    print(f"  {e1}")
    print(f"  {e2}")
    print(f"  {e3}")
    print()

    # Calculate ages at tick 10
    current_tick = 10
    print(f"Ages at tick {current_tick}:")
    for e in [e1, e2, e3]:
        age = e.get_age_at_tick(current_tick)
        print(f"  Entity {e.entity_id}: age = {age} ticks")
    print()

    print("=" * 70)
