"""Entity: memory as orbital program with two-phase lifecycle.

V6 entity model -- learning phase + execution phase:
  - Each tick: gain 1 energy from tick, deposit 1 to gamma (imprint)
  - Movement: entity prefers to STAY on its gamma peak (direction 6 = stay)
  - Only moves when forced: gradient pulls it, exclusion pushes it, or
    its current position is not the local gamma maximum.

  The entity IS its pattern of imprints. Staying still = concentrated hill
  = massive particle. Moving at c = thin streak = photon.

Two-phase lifecycle:
  Phase 1 -- Learning (memory_size ticks):
    - If on local gamma max -> stay (record STAY=6 to memory)
    - Otherwise -> four-way blend: gamma gradient + heading + occupancy + anti-photon
    - Records direction to memory, 1 slot/tick
    - When memory full -> transition to execution phase

  Phase 2 -- Execution (indefinite):
    - Replays memory[0..memory_cursor-1] cyclically, including stays
    - No gradient evaluation -- follows learned program
    - At end of each replay cycle: check orbit closure
    - If orbit closed (hex_distance <= 1 from start) -> reset cycle, loop forever
    - If orbit failed -> binary fission (2 children), parent dies

Standing wave quantization:
  Learning window W = memory_size = birth_tick
  Hex orbit at radius R has circumference 6R
  Closed orbit: W = k * 6R  ->  R = birth_tick / (6k)
"""

from __future__ import annotations

import math

import numpy as np

from grid import Position, HEX_DIRS, HEX_DIR_VECTORS, hex_distance

# Direction 6 = stay at current position (0-5 = hex movement directions)
STAY = 6

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
    """An imprint in the gamma field -- a memory-driven persistent pattern.

    Two-phase lifecycle: learning (fill memory) -> execution (replay program).
    """

    def __init__(self, entity_id: int, pos: Position, memory_size: int,
                 initial_memory: np.ndarray | None = None, generation: int = 0):
        self.id = entity_id
        self.pos = pos
        self.energy = 0.0
        self.alive = True
        self.generation = generation

        # Memory: fixed-size array of direction indices (0-5=hex, 6=stay), -1 = empty
        self.memory_size = max(1, memory_size)
        self.memory = np.full(self.memory_size, -1, dtype=np.int8)
        self.memory_cursor = 0

        # Initialize with compacted parent memory
        if initial_memory is not None:
            n = min(len(initial_memory), self.memory_size)
            self.memory[:n] = initial_memory[:n]
            self.memory_cursor = n

        # V6: Phase logic
        self.phase = 'learning'           # 'learning' or 'execution'
        self.execution_start_pos = None   # position when execution phase began
        self.cycle_cursor = 0             # index into memory during execution replay
        self.completed_cycles = 0         # number of successful orbit closures

        # Braking radiation: track last direction to detect changes
        self.last_direction = -1          # -1 = no previous direction

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
            if dir_idx < 0 or dir_idx == STAY:
                continue  # skip empty slots and stay decisions
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

    def compute_blend_vector(self, gradient: tuple[float, float, float],
                             occupancy_gradient: tuple[float, float, float] | None = None,
                             photon_gradient: tuple[float, float, float] | None = None
                             ) -> tuple[float, float]:
        """Compute the four-way blend vector (unnormalized).

        Returns (bx, by) -- used for both movement direction and replication scoring.
        """
        gx, gy, g_mag = gradient
        hx, hy = self.heading()
        h_mag = math.sqrt(hx * hx + hy * hy)

        if occupancy_gradient is not None:
            ox, oy, o_mag = occupancy_gradient
        else:
            ox, oy, o_mag = 0.0, 0.0, 0.0

        if photon_gradient is not None:
            px, py, p_mag = photon_gradient
        else:
            px, py, p_mag = 0.0, 0.0, 0.0

        if g_mag < 1e-12 and h_mag < 1e-12 and o_mag < 1e-12 and p_mag < 1e-12:
            return 0.0, 0.0

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

        # Photon anti-gradient: negate direction, keep magnitude
        if p_mag > 1e-12:
            pnx, pny = -px / p_mag, -py / p_mag
        else:
            pnx, pny = 0.0, 0.0

        # Four-way blend by magnitude (no tuning parameters)
        total = g_mag + h_mag + o_mag + p_mag
        gw = g_mag / total
        hw = h_mag / total
        ow = o_mag / total
        pw = p_mag / total

        bx = gw * gnx + hw * hnx + ow * onx + pw * pnx
        by = gw * gny + hw * hny + ow * ony + pw * pny

        return bx, by

    def choose_direction(self, gradient: tuple[float, float, float],
                         occupancy_gradient: tuple[float, float, float] | None = None,
                         photon_gradient: tuple[float, float, float] | None = None) -> int:
        """Rule 5: Four-way blend of gamma + heading + occupancy + anti-photon, snap to hex.

        Returns hex direction index (0-5).
        """
        bx, by = self.compute_blend_vector(gradient, occupancy_gradient, photon_gradient)
        if abs(bx) < 1e-12 and abs(by) < 1e-12:
            return self.id % 6
        result = _snap_to_hex(bx, by)
        return result if result >= 0 else self.id % 6

    def record_decision(self, dir_idx: int) -> None:
        """Rule 6: Record movement direction to memory (learning phase only)."""
        if self.memory_cursor < self.memory_size:
            self.memory[self.memory_cursor] = dir_idx
            self.memory_cursor += 1

    def is_memory_full(self) -> bool:
        """Check if learning phase is complete (memory filled)."""
        return self.phase == 'learning' and self.memory_cursor >= self.memory_size

    # --- V6: Execution phase methods ---

    def get_program_direction(self) -> int:
        """Execution phase: return next direction from recorded program.

        Returns 0-5 for hex movement, STAY (6) for staying at current position.
        """
        if self.memory_cursor == 0:
            return self.id % 6
        dir_idx = int(self.memory[self.cycle_cursor % self.memory_cursor])
        self.cycle_cursor += 1
        return dir_idx if 0 <= dir_idx <= STAY else self.id % 6

    def start_execution(self, current_pos: Position) -> None:
        """Transition from learning to execution phase."""
        self.phase = 'execution'
        self.execution_start_pos = current_pos
        self.cycle_cursor = 0

    def is_cycle_complete(self) -> bool:
        """Check if one full execution cycle has completed."""
        return self.phase == 'execution' and self.cycle_cursor >= self.memory_cursor

    def check_orbit_closure(self, current_pos: Position) -> bool:
        """After one execution cycle, check if orbit closed (returned near start).

        Minimum program length for a valid orbit is 6 steps (one full hex ring
        at radius 1). Shorter programs always fail — they can't form a
        physically meaningful closed trajectory.
        """
        if self.execution_start_pos is None:
            return False
        if self.memory_cursor < 6:
            return False
        return hex_distance(current_pos, self.execution_start_pos) <= 1

    def reset_cycle(self, current_pos: Position) -> None:
        """Start another execution cycle from current position."""
        self.execution_start_pos = current_pos
        self.cycle_cursor = 0
        self.completed_cycles += 1

    def should_replicate(self, current_pos: Position) -> bool:
        """Replicate if execution cycle complete and orbit did NOT close."""
        if not self.is_cycle_complete():
            return False
        return not self.check_orbit_closure(current_pos)

    # --- Memory operations ---

    def compact_memory(self) -> np.ndarray:
        """Compress parent memory for child inheritance.

        Takes every other entry -> half-resolution copy.
        """
        filled = self.memory[:self.memory_cursor]
        if len(filled) <= 1:
            return filled.copy()
        return filled[::2].copy()

    def filter_memory_for_direction(self, direction: int) -> np.ndarray:
        """Filter memory for a child at hex direction `direction`.

        Keeps entries in the forward hemisphere: direction +/-1 (mod 6).
        """
        filled = self.memory[:self.memory_cursor]
        if len(filled) == 0:
            return np.empty(0, dtype=np.int8)

        d0 = direction
        d1 = (direction - 1) % 6
        d2 = (direction + 1) % 6
        mask = (filled == d0) | (filled == d1) | (filled == d2)
        return filled[mask].copy()

    def __repr__(self) -> str:
        return (f"Entity(id={self.id}, pos={self.pos}, "
                f"phase={self.phase}, "
                f"mem={self.memory_cursor}/{self.memory_size}, "
                f"gen={self.generation}, cycles={self.completed_cycles})")
