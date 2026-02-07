import numpy as np
from collections import defaultdict
from dataclasses import dataclass

from constants import (
    BETA_IMPRINT, LEAK_DECAY, BASE_ENERGY_RATE, POSITION_ENERGY_RATE,
    PASSIVE_ENERGY_RATE, STASIS_COST, COMP_COST, EPSILON_STABLE,
    MAX_LOCAL_TICKS, ENERGY_CAP, RADIATION_SCALE,
    REPLICATION_ENERGY_COST, MAX_ENTITIES, WINDOW_GROWTH,
    MERGE_COMPAT_THRESHOLD, MERGE_ENERGY_TRANSFER, RING_DISTANCE,
)
from entity import Entity, clamp, next_entity_id
from hill import Hill


# ==========================
# World (2D)
# ==========================

@dataclass
class World:
    hill: Hill
    entities: list
    imprint_field: np.ndarray   # shape (N, N)
    leak_field: np.ndarray      # shape (N, N)
    replication_events: int = 0
    merge_events: int = 0

    def commit_step(self, tick: int = 0):
        self.replication_events = 0
        self.merge_events = 0
        n = self.hill.height.shape[0]

        # --- Hill commits once ---
        self.hill.commit(self.imprint_field)
        new_heights = self.hill.height.copy()

        # --- Imprint field decay ---
        self.imprint_field *= BETA_IMPRINT

        # --- Leak field decay ---
        self.leak_field *= LEAK_DECAY

        # --- Process each entity ---
        new_entities = []
        for e in self.entities:
            e.age += 1

            # Energy acquisition — position-based for [0,1] normalized hill
            new_h = new_heights[e.y, e.x]
            e.energy += BASE_ENERGY_RATE + POSITION_ENERGY_RATE * new_h

            # Passive slope energy
            grad_vec = self.hill.gradient_at(e.x, e.y)
            slope_energy = PASSIVE_ENERGY_RATE * np.linalg.norm(grad_vec)
            e.energy += slope_energy

            # DeltaH and DeltaDeltaH
            e.delta_h = new_h - e.baseline_h
            e.delta_delta_h = e.delta_h - e.prev_delta_h
            e.prev_delta_h = e.delta_h

            # --- Local tick loop ---
            start_x, start_y = e.x, e.y
            orig_grad = self.hill.gradient_at(e.x, e.y)
            for tick_i in range(MAX_LOCAL_TICKS):
                if e.energy <= 0:
                    break

                gamma = e.local_gamma(self.hill, self.imprint_field, self.leak_field)

                spent = e.move(self.hill, gamma)
                e.energy -= spent

                # Memory update from actual movement outcome (2F)
                if e.energy > COMP_COST:
                    e.update_memory(e.last_move_height_diff)
                    e.energy -= COMP_COST
                else:
                    break

                e.update_pattern(gamma)

                # Stabilization condition
                if tick_i >= 1:
                    current_grad = self.hill.gradient_at(e.x, e.y)
                    grad_diff = np.linalg.norm(current_grad - orig_grad)
                    if grad_diff < EPSILON_STABLE:
                        break

            # --- Stasis penalty: staying still is penalized ---
            if e.x == start_x and e.y == start_y:
                e.energy -= STASIS_COST
                e.energy = max(0.0, e.energy)

            # --- Imprint phase (window-scaled kernel, 1C) ---
            if e.ready_to_imprint():
                gamma = e.local_gamma(self.hill, self.imprint_field, self.leak_field)
                dI = e.imprint_value(gamma)

                # Kernel radius grows with window: base=1 (3x3), +1 per 3 extra memory slots
                kernel_radius = 1 + (len(e.memory) - 4) // 3
                kernel_size = 2 * kernel_radius + 1
                sigma = kernel_radius * 0.6
                # 1D Gaussian kernel, normalized
                x_k = np.arange(kernel_size) - kernel_radius
                kernel_1d = np.exp(-0.5 * (x_k / max(sigma, 0.1)) ** 2)
                kernel_1d /= kernel_1d.sum()
                kernel_2d = np.outer(kernel_1d, kernel_1d)

                # Apply centered on entity position
                for ky in range(kernel_size):
                    for kx in range(kernel_size):
                        px = e.x + (kx - kernel_radius)
                        py = e.y + (ky - kernel_radius)
                        if 0 <= px < n and 0 <= py < n:
                            self.imprint_field[py, px] += dI * kernel_2d[ky, kx]

                e.energy -= e.imprint_cost()

            # --- Radiation phase ---
            if e.energy > ENERGY_CAP:
                excess = e.energy - ENERGY_CAP
                radiation = RADIATION_SCALE * np.log1p(excess)
                self.leak_field[e.y, e.x] += radiation
                e.energy = ENERGY_CAP

            # --- Replication check (1G: cooldown) ---
            if e.can_replicate(tick) and len(self.entities) + len(new_entities) < MAX_ENTITIES:
                # Find first empty adjacent cell
                child_x, child_y = e.x + 1, e.y
                child_x = clamp(child_x, 0, n - 1)
                child_y = clamp(child_y, 0, n - 1)

                child_window_size = len(e.memory) + WINDOW_GROWTH
                child_memory = np.zeros(child_window_size, dtype=int)
                child_memory[:len(e.memory)] = e.memory
                child_memory[0] = -1  # antiexistence still required

                child = Entity(
                    id=next_entity_id(),
                    x=child_x,
                    y=child_y,
                    memory=child_memory,
                    baseline_h=self.hill.height[child_y, child_x],
                    energy=0.05,
                    last_replication_tick=tick,
                )
                e.energy -= REPLICATION_ENERGY_COST
                e.energy = max(0.0, e.energy)
                e.last_replication_tick = tick
                new_entities.append(child)
                self.replication_events += 1

        self.entities.extend(new_entities)

        # --- Inter-entity interactions ---
        self._resolve_collisions()
        self._detect_rings()

    def _resolve_collisions(self):
        """Position-based collision detection with 2D keys."""
        pos_groups = defaultdict(list)
        for e in self.entities:
            pos_groups[(e.x, e.y)].append(e)

        to_remove = set()
        for pos, group in pos_groups.items():
            if len(group) < 2:
                continue
            while len(group) >= 2:
                a = group.pop(0)
                b = group.pop(0)
                if a.id in to_remove or b.id in to_remove:
                    continue

                min_len = min(len(a.memory), len(b.memory))
                if min_len > 0:
                    overlap = np.sum(a.memory[:min_len] == b.memory[:min_len]) / min_len
                else:
                    overlap = 0.0

                if overlap > MERGE_COMPAT_THRESHOLD:
                    a.energy += b.energy * MERGE_ENERGY_TRANSFER
                    a.pattern += b.pattern * 0.5
                    to_remove.add(b.id)
                else:
                    loss = min(a.energy, b.energy) * 0.5
                    a.energy -= loss
                    b.energy -= loss
                    a.energy = max(0.0, a.energy)
                    b.energy = max(0.0, b.energy)

                self.merge_events += 1

        self.entities = [e for e in self.entities if e.id not in to_remove]

    def _detect_rings(self):
        """2D encirclement detection.
        Check if neighbors exist in 3+ of 4 quadrants within RING_DISTANCE."""
        positions = {(e.x, e.y) for e in self.entities}
        for e in self.entities:
            # Check 4 quadrants: (+,+), (-,+), (-,-), (+,-)
            quadrants_occupied = 0
            for qx, qy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
                found = False
                for d in range(1, RING_DISTANCE + 1):
                    for d2 in range(0, d + 1):
                        # Check (d, d2) and (d2, d) in this quadrant direction
                        for dx, dy in [(d, d2), (d2, d)]:
                            nx = e.x + qx * dx
                            ny = e.y + qy * dy
                            if (nx, ny) in positions and (nx, ny) != (e.x, e.y):
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    quadrants_occupied += 1

            if quadrants_occupied >= 3:
                e.energy = max(0.0, e.energy - 0.1)
