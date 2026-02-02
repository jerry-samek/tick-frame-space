"""
V16 Entity - Entity with tick skipping for time dilation.

Identical to V15-3D entity. The entity itself is dimension-agnostic
since position is just a tuple.

Each entity:
- Has a unique ID = birth tick
- Owns one layer in the ExpandingGrid3D
- Is born at origin (center of grid)
- Persists forever (no death at substrate level)
- Tracks skip_accumulator for tick skipping (time dilation)

Author: V16 Implementation
Date: 2026-02-01
Based on: V15-3D entity.py (unchanged)
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Entity:
    """An entity with its own field layer and skip tracking.

    Entities are born at origin and own a dedicated layer.
    Layer index = entity_id = birth_tick.
    """

    entity_id: int
    """Unique entity identifier (= birth tick)."""

    birth_tick: int
    """Tick at which entity was created."""

    layer_id: int
    """Layer index in ExpandingGrid3D (same as entity_id)."""

    position: Tuple[int, int, int] = field(default_factory=lambda: (0, 0, 0))
    """Current position (center of pattern). Shifts as grid expands."""

    skip_accumulator: int = 0
    """Ticks accumulated while skipping.

    When entity skips a tick (due to being in gravitational well):
    - skip_accumulator increments
    - No imprint happens yet

    When entity acts (doesn't skip):
    - Imprints ONCE for the whole accumulated segment
    - skip_accumulator resets to 0

    This prevents runaway gamma accumulation in wells while
    preserving energy conservation (1 action = 1 imprint).
    """

    total_skips: int = 0
    """Total ticks skipped over entity lifetime (for statistics)."""

    total_acts: int = 0
    """Total ticks entity acted (didn't skip) (for statistics)."""

    @property
    def age(self) -> int:
        """Age of entity in ticks (requires external tick count)."""
        # Note: This is a placeholder - age = current_tick - birth_tick
        # Must be calculated externally
        return 0

    @property
    def effective_age(self) -> int:
        """Effective age = ticks entity actually experienced (acted).

        Due to time dilation, effective_age <= calendar age.
        """
        return self.total_acts

    @property
    def time_dilation_factor(self) -> float:
        """Time dilation factor = effective_age / total_ticks_elapsed.

        Returns 1.0 if no skipping (no dilation).
        Returns < 1.0 if entity has been skipping (time dilated).
        """
        total = self.total_acts + self.total_skips
        if total == 0:
            return 1.0
        return self.total_acts / total

    def get_age_at_tick(self, current_tick: int) -> int:
        """Calculate age at a specific tick.

        Args:
            current_tick: Current tick count

        Returns:
            Age in ticks
        """
        return current_tick - self.birth_tick

    def skip_tick(self):
        """Record that entity skipped this tick (time dilation)."""
        self.skip_accumulator += 1
        self.total_skips += 1

    def act_tick(self) -> int:
        """Record that entity acted this tick.

        Returns:
            Number of ticks accumulated (for imprint strength tracking).
            Always 1 for imprint purposes, but accumulator value useful for stats.
        """
        accumulated = self.skip_accumulator
        self.skip_accumulator = 0
        self.total_acts += 1
        return accumulated

    def shift_position(self, delta: int = 1):
        """Shift position by delta in all dimensions (for grid expansion).

        When grid expands, positions need to shift to stay at same relative location.

        Args:
            delta: Amount to shift in each dimension (default 1)
        """
        x, y, z = self.position
        self.position = (x + delta, y + delta, z + delta)

    def __repr__(self) -> str:
        return (
            f"Entity(id={self.entity_id}, "
            f"birth={self.birth_tick}, "
            f"layer={self.layer_id}, "
            f"pos={self.position}, "
            f"dilation={self.time_dilation_factor:.2f})"
        )


def create_entity(tick: int, layer_id: int, origin: Tuple[int, int, int] = (0, 0, 0)) -> Entity:
    """Factory function to create an entity.

    Args:
        tick: Current tick (becomes entity_id and birth_tick)
        layer_id: Layer index in ExpandingGrid3D
        origin: Birth position (default: origin [0, 0, 0] for 3D)

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
    print("V16 Entity Demo")
    print("=" * 70)

    # Create entities at different ticks with 3D positions
    e1 = create_entity(tick=1, layer_id=0, origin=(10, 10, 10))
    e2 = create_entity(tick=2, layer_id=1, origin=(10, 10, 10))
    e3 = create_entity(tick=3, layer_id=2, origin=(10, 10, 10))

    print("Created entities (3D positions):")
    print(f"  {e1}")
    print(f"  {e2}")
    print(f"  {e3}")
    print()

    # Demonstrate position shifting (grid expansion)
    print("Simulating grid expansion (shift positions by 1):")
    for entity in [e1, e2, e3]:
        old_pos = entity.position
        entity.shift_position(1)
        print(f"  Entity {entity.entity_id}: {old_pos} -> {entity.position}")
    print()

    # Simulate tick skipping for e1 (in gravitational well)
    print("Simulating e1 in gravitational well (skips 3 out of 5 ticks):")
    for i in range(5):
        if i in [0, 2, 4]:  # Skip ticks 0, 2, 4
            e1.skip_tick()
            print(f"  Tick {i}: SKIP (accumulator={e1.skip_accumulator})")
        else:
            accumulated = e1.act_tick()
            print(f"  Tick {i}: ACT (imprint once, was {accumulated} skipped)")

    print()
    print(f"e1 after 5 ticks:")
    print(f"  Total acts: {e1.total_acts}")
    print(f"  Total skips: {e1.total_skips}")
    print(f"  Time dilation factor: {e1.time_dilation_factor:.2f}")
    print()

    print("=" * 70)
