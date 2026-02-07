import numpy as np
from collections import deque
from dataclasses import dataclass, field

from constants import (
    EPSILON_DH, MOVE_COST, COMP_COST, IMPRINT_COST_BASE,
    PATTERN_DECAY, INERTIA, DIRS, DIR_COSTS,
    REPLICATION_ENERGY_COST, REPLICATION_COOLDOWN,
    REPLICATION_DH_THRESHOLD, REPLICATION_DDH_THRESHOLD,
    MIN_REPLICATION_AGE,
)

# ==========================
# Helper functions
# ==========================

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def next_entity_id():
    next_entity_id.counter += 1
    return next_entity_id.counter
next_entity_id.counter = 0


# ==========================
# Entity (2D adaptation)
# ==========================

@dataclass
class Entity:
    id: int
    x: int
    y: int
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
    heading: np.ndarray = field(default_factory=lambda: np.array([1.0, 0.0]))  # persistent direction (2B)
    tick_count: int = 0
    last_outcome: str = ""          # "success+", "success", or "failure"
    trail: deque = field(default_factory=lambda: deque(maxlen=50))
    last_replication_tick: int = -100  # (1G) cooldown tracking

    def update_memory(self, height_diff: float):
        """Movement-outcome memory based on actual movement result (2F).
        +1 = gained height, 0 = level (nothing learned), -1 = lost height."""
        if height_diff > EPSILON_DH:
            symbol = 1    # gained height — good
        elif height_diff < -EPSILON_DH:
            symbol = -1   # lost height — bad
        else:
            symbol = 0    # level — nothing learned

        self.memory = np.roll(self.memory, -1)
        self.memory[-1] = symbol

        if -1 not in self.memory:
            self.memory[0] = -1

    def local_gamma(self, hill, imprint_field, leak_field):
        """Enriched gamma field (Doc 02 Sec 2.1).
        After hill renormalization (1A), gradient magnitudes are naturally bounded."""
        grad_vec = hill.gradient_at(self.x, self.y)
        grad = np.linalg.norm(grad_vec)
        imp = imprint_field[self.y, self.x]
        leak = leak_field[self.y, self.x]
        h = hill.height[self.y, self.x]
        mem_coherence = np.mean(np.abs(self.memory))
        return grad + 0.5 * imp + 0.2 * leak + 0.1 * h * mem_coherence

    def move(self, hill, gamma: float) -> float:
        """Contour-following with heading inertia (Doc 094, overdamped motion).
        Computes desired contour direction, blends with persistent heading,
        snaps to nearest of 8 grid directions."""
        n = hill.height.shape[0]
        old_h = hill.height[self.y, self.x]

        # Smooth chirality from memory (2C)
        chirality = np.tanh(2.0 * np.mean(self.memory))

        # Gradient vector
        grad_vec = hill.gradient_at(self.x, self.y)
        grad_mag = np.linalg.norm(grad_vec) + 1e-8

        # Contour-following direction (2D): perpendicular + slight uphill bias
        perp = np.array([-grad_vec[1], grad_vec[0]]) * chirality / grad_mag
        uphill = grad_vec / grad_mag
        desired = perp + 0.1 * uphill

        # Blend with heading inertia (2B)
        self.heading = INERTIA * self.heading + (1 - INERTIA) * desired
        heading_mag = np.linalg.norm(self.heading) + 1e-8
        self.heading = self.heading / heading_mag

        # Snap heading to nearest of 8 directions (2A)
        best_dir_idx = 0
        best_dot = -2.0
        for i, (dx, dy) in enumerate(DIRS):
            d_vec = np.array([float(dx), float(dy)])
            d_mag = np.linalg.norm(d_vec)
            dot = (self.heading[0] * dx + self.heading[1] * dy) / (d_mag + 1e-8)
            if dot > best_dot:
                best_dot = dot
                best_dir_idx = i

        dx, dy = DIRS[best_dir_idx]
        move_cost = MOVE_COST * DIR_COSTS[best_dir_idx]  # diagonal costs more
        self.last_step = (dx, dy)

        # Classify movement outcome
        nx = clamp(self.x + dx, 0, n - 1)
        ny = clamp(self.y + dy, 0, n - 1)
        h_diff = hill.height[ny, nx] - old_h
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
            self.x = nx
            self.y = ny
            new_h = hill.height[self.y, self.x]
            self.last_move_height_diff = new_h - old_h
            self.trail.append((self.x, self.y))
            return move_cost
        self.last_move_height_diff = 0.0
        return 0.0

    def update_pattern(self, gamma: float):
        """EMA pattern update (1B) — bounded, tracks recent gamma history."""
        self.pattern = PATTERN_DECAY * self.pattern + (1 - PATTERN_DECAY) * gamma

    def imprint_cost(self) -> float:
        """Imprint cost scales with window size (1C)."""
        return IMPRINT_COST_BASE * len(self.memory) / 4.0

    def ready_to_imprint(self) -> bool:
        return self.energy > self.imprint_cost() and (-1 in self.memory)

    def imprint_value(self, gamma: float) -> float:
        """Window-scaled imprint strength (1C)."""
        window_factor = len(self.memory) / 4.0
        raw = window_factor * (1.0 + abs(self.pattern)) * np.tanh(gamma)
        return np.clip(raw, -3.0, 3.0)

    def can_replicate(self, current_tick: int) -> bool:
        if self.age < MIN_REPLICATION_AGE:
            return False
        if self.energy < REPLICATION_ENERGY_COST:
            return False
        if (current_tick - self.last_replication_tick) < REPLICATION_COOLDOWN:
            return False
        return (abs(self.delta_h) > REPLICATION_DH_THRESHOLD or
                self.delta_delta_h < REPLICATION_DDH_THRESHOLD)
