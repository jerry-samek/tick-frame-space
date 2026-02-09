"""Entity: memory-driven imprints in the gamma field.

V4 entity model -- tick energy, memory, heading, imprint:
  - Each tick: gain 1 energy from tick, deposit 1 to gamma (imprint)
  - Movement is FREE (1 cell/tick = c, surfing the gradient)
  - Direction from gradient (when slope exists) + memory heading (always)
  - Memory fills one slot per tick; when full -> replicate (parent dies, N children)
  - Memory size = birth tick (entity born at global tick T has T memory slots)

Entity lifecycle:
  - Birth: single cell, memory from direction-filtered parent (or empty for seed)
  - Living: imprint, move, record decision each tick
  - Replication: memory full -> fill all free neighbors -> parent dies
"""

from __future__ import annotations

import math

import numpy as np

from grid import Grid, Position, HEX_DIRS, HEX_DIR_VECTORS

_next_id = 0


def reset_entity_ids() -> None:
    global _next_id
    _next_id = 0


def next_entity_id() -> int:
    global _next_id
    _next_id += 1
    return _next_id


def _snap_to_hex(vx: float, vy: float) -> int:
    """Snap a Cartesian direction vector to the nearest hex direction index (0-5).

    Returns the hex direction index that is closest to the given vector.
    If vector is zero, returns -1 (no direction).
    """
    if abs(vx) < 1e-12 and abs(vy) < 1e-12:
        return -1

    best_idx = 0
    best_dot = -2.0
    for i, (ux, uy) in enumerate(HEX_DIR_VECTORS):
        dot = vx * ux + vy * uy
        if dot > best_dot:
            best_dot = dot
            best_idx = i
    return best_idx


def _direction_to_vector(dir_idx: int) -> tuple[float, float]:
    """Convert hex direction index (0-5) to Cartesian unit vector."""
    if dir_idx < 0 or dir_idx > 5:
        return 0.0, 0.0
    return HEX_DIR_VECTORS[dir_idx]


class Entity:
    """An imprint in the gamma field -- a memory-driven persistent pattern."""

    def __init__(self, entity_id: int, pos: Position, memory_size: int,
                 initial_memory: np.ndarray | None = None, generation: int = 0):
        self.id = entity_id
        self.pos = pos
        self.energy = 0.0
        self.alive = True
        self.generation = generation

        # Memory: fixed-size array of hex direction indices (0-5), -1 = empty
        self.memory_size = max(1, memory_size)
        self.memory = np.full(self.memory_size, -1, dtype=np.int8)
        self.memory_cursor = 0

        # Initialize with compacted parent memory
        if initial_memory is not None:
            n = min(len(initial_memory), self.memory_size)
            self.memory[:n] = initial_memory[:n]
            self.memory_cursor = n

    @property
    def memory_fill_pct(self) -> float:
        """Fraction of memory filled (0.0 to 1.0)."""
        return self.memory_cursor / self.memory_size

    def heading(self) -> tuple[float, float]:
        """Compute heading vector from recent memory entries.

        Uses exponentially weighted average of recent decisions.
        More recent decisions have more weight.
        """
        hx, hy = 0.0, 0.0
        weight_sum = 0.0

        # Walk backwards from most recent decision
        for i in range(self.memory_cursor - 1, -1, -1):
            dir_idx = self.memory[i]
            if dir_idx < 0:
                continue
            # Exponential decay: recent decisions matter more
            age = self.memory_cursor - 1 - i
            w = 0.7 ** age
            dx, dy = _direction_to_vector(dir_idx)
            hx += w * dx
            hy += w * dy
            weight_sum += w

        if weight_sum > 1e-12:
            hx /= weight_sum
            hy /= weight_sum

        return hx, hy

    def tick_energy(self) -> None:
        """Rule 1: Each tick, entity gains 1 energy from the tick itself."""
        self.energy += 1.0

    def imprint_energy(self) -> float:
        """Rule 2: Entity deposits all tick energy to gamma at its position.

        Returns amount to deposit. Resets entity energy to 0.
        """
        amount = self.energy
        self.energy = 0.0
        return amount

    def choose_direction(self, gradient: tuple[float, float, float],
                         occupancy_gradient: tuple[float, float, float] | None = None) -> int:
        """Rule 5: Blend gradient + heading + occupancy pressure, snap to hex.

        Three-way blend by magnitude:
        - Gamma gradient: points toward high energy (attraction)
        - Heading: points where entity has been going (inertia)
        - Occupancy gradient: points toward free space (reproductive pressure)

        Returns hex direction index (0-5).
        """
        gx, gy, g_mag = gradient
        hx, hy = self.heading()
        h_mag = math.sqrt(hx * hx + hy * hy)

        if occupancy_gradient is not None:
            ox, oy, o_mag = occupancy_gradient
        else:
            ox, oy, o_mag = 0.0, 0.0, 0.0

        if g_mag < 1e-12 and h_mag < 1e-12 and o_mag < 1e-12:
            return self.id % 6

        # Normalize each to unit vectors
        if g_mag > 1e-12:
            gnx, gny = gx / g_mag, gy / g_mag
        else:
            gnx, gny = 0.0, 0.0

        if h_mag > 1e-12:
            hnx, hny = hx / h_mag, hy / h_mag
        else:
            hnx, hny = 0.0, 0.0

        if o_mag > 1e-12:
            onx, ony = ox / o_mag, oy / o_mag
        else:
            onx, ony = 0.0, 0.0

        # Three-way blend by magnitude (no tuning parameters)
        total = g_mag + h_mag + o_mag
        gw = g_mag / total
        hw = h_mag / total
        ow = o_mag / total

        bx = gw * gnx + hw * hnx + ow * onx
        by = gw * gny + hw * hny + ow * ony

        result = _snap_to_hex(bx, by)
        return result if result >= 0 else self.id % 6

    def record_decision(self, dir_idx: int) -> None:
        """Rule 6: Record movement direction to memory."""
        if self.memory_cursor < self.memory_size:
            self.memory[self.memory_cursor] = dir_idx
            self.memory_cursor += 1

    def is_memory_full(self) -> bool:
        """Check if memory is full -> ready to replicate."""
        return self.memory_cursor >= self.memory_size

    def compact_memory(self) -> np.ndarray:
        """Compress parent memory for child inheritance.

        Takes every other entry -> half-resolution copy.
        This creates generational inheritance: each child carries
        a compressed version of all ancestors' decisions.
        """
        filled = self.memory[:self.memory_cursor]
        if len(filled) <= 1:
            return filled.copy()
        return filled[::2].copy()

    def filter_memory_for_direction(self, direction: int) -> np.ndarray:
        """Filter memory for a child at hex direction `direction`.

        Keeps entries in the forward hemisphere: direction ±1 (mod 6).
        """
        filled = self.memory[:self.memory_cursor]
        if len(filled) == 0:
            return np.empty(0, dtype=np.int8)

        d0 = direction
        d1 = (direction - 1) % 6
        d2 = (direction + 1) % 6
        mask = (filled == d0) | (filled == d1) | (filled == d2)
        return filled[mask].copy()

    def prepare_replication_all(self) -> None:
        """Mark parent dead for fill-all replication.
        Callers use filter_memory_for_direction() per child."""
        self.alive = False

    def prepare_replication(self) -> np.ndarray:
        """Separate memory compaction (entity's job) from spatial placement (world's job).

        Returns compacted memory and marks parent dead.
        """
        compacted = self.compact_memory()
        self.alive = False
        return compacted

    def replicate(self, grid: Grid, birth_tick: int) -> tuple[Entity, Entity] | None:
        """Replication: parent dies, 2 children spawned at adjacent cells.

        Children get:
          - Memory size = birth_tick (longer memory = longer life)
          - Initial memory = compacted parent memory
          - Position = two adjacent cells near parent

        Returns (child1, child2) or None if no space.
        """
        neighbors = grid.neighbors(self.pos)
        if len(neighbors) < 2:
            return None

        compacted = self.compact_memory()
        child_memory_size = birth_tick

        child1 = Entity(
            entity_id=next_entity_id(),
            pos=neighbors[0],
            memory_size=child_memory_size,
            initial_memory=compacted,
            generation=self.generation + 1,
        )
        child2 = Entity(
            entity_id=next_entity_id(),
            pos=neighbors[1],
            memory_size=child_memory_size,
            initial_memory=compacted,
            generation=self.generation + 1,
        )

        self.alive = False
        return child1, child2

    def __repr__(self) -> str:
        return (f"Entity(id={self.id}, pos={self.pos}, "
                f"mem={self.memory_cursor}/{self.memory_size}, "
                f"gen={self.generation})")
