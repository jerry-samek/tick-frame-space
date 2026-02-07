import numpy as np
from collections import deque
from dataclasses import dataclass, field

from constants import (
    EPSILON_DH, MOVE_COST, COMP_COST, IMPRINT_COST_BASE,
    PATTERN_DECAY, INERTIA,
    REPLICATION_ENERGY_COST, REPLICATION_COOLDOWN,
    REPLICATION_DH_THRESHOLD, REPLICATION_DDH_THRESHOLD,
    MIN_REPLICATION_AGE, WORLD_RADIUS,
)
from hex_grid import HEX_DIRS, HEX_DIR_VECTORS, hex_get, is_valid_hex


# ==========================
# Helper functions
# ==========================

def next_entity_id():
    next_entity_id.counter += 1
    return next_entity_id.counter
next_entity_id.counter = 0


# ==========================
# Entity (hex grid adaptation)
# ==========================

@dataclass
class Entity:
    id: int
    q: int
    r: int
    memory: np.ndarray
    pattern: float = 0.0
    energy: float = 0.0
    render_offset_idx: int = 0
    baseline_h: float = 0.0
    prev_delta_h: float = 0.0
    age: int = 0
    delta_h: float = 0.0
    delta_delta_h: float = 0.0
    last_move_height_diff: float = 0.0
    last_downhill: np.ndarray = field(default_factory=lambda: np.zeros(2))
    last_perp: np.ndarray = field(default_factory=lambda: np.zeros(2))
    last_mem_bias: float = 0.0
    last_gamma_signal: float = 0.0
    last_direction: np.ndarray = field(default_factory=lambda: np.zeros(2))
    last_step: tuple = (0, 0)
    heading: np.ndarray = field(default_factory=lambda: np.array([1.0, 0.0]))
    tick_count: int = 0
    last_outcome: str = ""
    trail: deque = field(default_factory=lambda: deque(maxlen=50))
    last_replication_tick: int = -100

    def update_memory(self, height_diff: float):
        """Movement-outcome memory based on actual movement result.
        +1 = gained height, 0 = level, -1 = lost height."""
        if height_diff > EPSILON_DH:
            symbol = 1
        elif height_diff < -EPSILON_DH:
            symbol = -1
        else:
            symbol = 0

        self.memory = np.roll(self.memory, -1)
        self.memory[-1] = symbol

        if -1 not in self.memory:
            self.memory[0] = -1

    def local_gamma(self, hill, imprint_field, leak_field):
        """Enriched gamma field using hex accessors."""
        R = hill.radius
        grad_vec = hill.gradient_at(self.q, self.r)
        grad = np.linalg.norm(grad_vec)
        imp = hex_get(imprint_field, self.q, self.r, R)
        leak = hex_get(leak_field, self.q, self.r, R)
        h = hill.height_at(self.q, self.r)
        mem_coherence = np.mean(np.abs(self.memory))
        return grad + 0.5 * imp + 0.2 * leak + 0.1 * h * mem_coherence

    def move(self, hill, gamma: float) -> float:
        """Contour-following with heading inertia, snapping to 6 hex directions."""
        R = hill.radius
        old_h = hill.height_at(self.q, self.r)

        # Flat-ground safety: no meaningful gradient → stay put
        grad_vec = hill.gradient_at(self.q, self.r)
        grad_mag = np.linalg.norm(grad_vec)
        if grad_mag < 1e-4:
            self.last_outcome = "flat"
            self.last_step = (0, 0)
            self.last_move_height_diff = 0.0
            return 0.0

        # Smooth chirality from memory
        chirality = np.tanh(2.0 * np.mean(self.memory))

        grad_mag += 1e-8  # safe divisor

        # Contour-following: perpendicular + slight uphill bias
        perp = np.array([-grad_vec[1], grad_vec[0]]) * chirality / grad_mag
        uphill = grad_vec / grad_mag
        desired = perp + 0.1 * uphill

        # Blend with heading inertia
        self.heading = INERTIA * self.heading + (1 - INERTIA) * desired
        heading_mag = np.linalg.norm(self.heading) + 1e-8
        self.heading = self.heading / heading_mag

        # Snap heading to nearest of 6 hex directions (dot product)
        best_dir_idx = 0
        best_dot = -2.0
        for i, (vx, vy) in enumerate(HEX_DIR_VECTORS):
            dot = self.heading[0] * vx + self.heading[1] * vy
            if dot > best_dot:
                best_dot = dot
                best_dir_idx = i

        dq, dr = HEX_DIRS[best_dir_idx]
        self.last_step = (dq, dr)

        # Uniform move cost (no diagonal penalty)
        move_cost = MOVE_COST

        # Compute target position
        nq = self.q + dq
        nr = self.r + dr

        # Boundary check: if invalid, stay put
        if not is_valid_hex(nq, nr, WORLD_RADIUS):
            nq, nr = self.q, self.r

        # Classify movement outcome
        h_diff = hill.height_at(nq, nr) - old_h
        if h_diff > EPSILON_DH:
            self.last_outcome = "success+"
        elif h_diff >= -EPSILON_DH:
            self.last_outcome = "success"
        else:
            self.last_outcome = "failure"

        self.tick_count += 1

        # Store diagnostics
        self.last_downhill = (-grad_vec / grad_mag).copy()
        self.last_perp = perp.copy()
        self.last_mem_bias = float(chirality)
        self.last_gamma_signal = float(np.sign(gamma))
        self.last_direction = self.heading.copy()

        # Execute move
        if self.energy > move_cost:
            self.q = nq
            self.r = nr
            new_h = hill.height_at(self.q, self.r)
            self.last_move_height_diff = new_h - old_h
            self.trail.append((self.q, self.r))
            return move_cost
        self.last_move_height_diff = 0.0
        return 0.0

    def update_pattern(self, gamma: float):
        """EMA pattern update."""
        self.pattern = PATTERN_DECAY * self.pattern + (1 - PATTERN_DECAY) * gamma

    def imprint_cost(self) -> float:
        """Imprint cost scales with window size."""
        return IMPRINT_COST_BASE * len(self.memory) / 4.0

    def ready_to_imprint(self) -> bool:
        return self.energy > self.imprint_cost() and (-1 in self.memory)

    def imprint_value(self, gamma: float) -> float:
        """Window-scaled imprint strength.
        Minimum deposit of 0.3 ensures bootstrapping on flat ground."""
        window_factor = len(self.memory) / 4.0
        raw = window_factor * (1.0 + abs(self.pattern)) * np.tanh(gamma)
        # Entity presence always deposits at least 0.3 — survival requires building
        return np.clip(raw, 0.3, 3.0)

    def can_replicate(self, current_tick: int) -> bool:
        if self.age < MIN_REPLICATION_AGE:
            return False
        if self.energy < REPLICATION_ENERGY_COST:
            return False
        if (current_tick - self.last_replication_tick) < REPLICATION_COOLDOWN:
            return False
        return (abs(self.delta_h) > REPLICATION_DH_THRESHOLD or
                self.delta_delta_h < REPLICATION_DDH_THRESHOLD)
