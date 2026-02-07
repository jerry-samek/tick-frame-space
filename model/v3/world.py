import numpy as np
from collections import defaultdict
from dataclasses import dataclass

from constants import (
    BETA_IMPRINT, LEAK_DECAY, BASE_ENERGY_RATE, POSITION_ENERGY_RATE,
    PASSIVE_ENERGY_RATE, COMP_COST, EPSILON_STABLE,
    MAX_LOCAL_TICKS, ENERGY_CAP, RADIATION_SCALE,
    REPLICATION_ENERGY_COST, MAX_ENTITIES, WINDOW_GROWTH,
    MERGE_COMPAT_THRESHOLD, MERGE_ENERGY_TRANSFER, RING_DISTANCE,
    WORLD_RADIUS,
)
from entity import Entity, next_entity_id
from hill import Hill
from hex_grid import (
    HEX_DIRS, hex_get, hex_add, hex_ring_cells,
    is_valid_hex, hex_neighbors,
)


# ==========================
# World (hex grid)
# ==========================

@dataclass
class World:
    hill: Hill
    entities: list
    imprint_field: np.ndarray   # shape (2R+1, 2R+1)
    leak_field: np.ndarray      # shape (2R+1, 2R+1)
    replication_events: int = 0
    merge_events: int = 0

    def commit_step(self, tick: int = 0):
        self.replication_events = 0
        self.merge_events = 0
        R = self.hill.radius

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

            # Energy acquisition — from non-normalized hill height
            new_h = hex_get(new_heights, e.q, e.r, R)
            e.energy += BASE_ENERGY_RATE + POSITION_ENERGY_RATE * new_h

            # Passive slope energy
            grad_vec = self.hill.gradient_at(e.q, e.r)
            slope_energy = PASSIVE_ENERGY_RATE * np.linalg.norm(grad_vec)
            e.energy += slope_energy

            # DeltaH and DeltaDeltaH
            e.delta_h = new_h - e.baseline_h
            e.delta_delta_h = e.delta_h - e.prev_delta_h
            e.prev_delta_h = e.delta_h

            # --- Imprint phase (before movement — build hill under yourself) ---
            if e.ready_to_imprint():
                gamma = e.local_gamma(self.hill, self.imprint_field, self.leak_field)
                dI = e.imprint_value(gamma)

                # Gaussian-weighted imprint in hex rings around entity
                kernel_radius = 1 + (len(e.memory) - 4) // 3
                for ring_r in range(kernel_radius + 1):
                    sigma = max(kernel_radius * 0.6, 0.1)
                    weight = np.exp(-0.5 * (ring_r / sigma) ** 2)
                    if ring_r == 0:
                        cells = [(e.q, e.r)]
                    else:
                        cells = hex_ring_cells(e.q, e.r, ring_r)
                    for cq, cr in cells:
                        if is_valid_hex(cq, cr, R):
                            hex_add(self.imprint_field, cq, cr, R, dI * weight)

                e.energy -= e.imprint_cost()

            # --- Local tick loop ---
            orig_grad = self.hill.gradient_at(e.q, e.r)
            for tick_i in range(MAX_LOCAL_TICKS):
                if e.energy <= 0:
                    break

                gamma = e.local_gamma(self.hill, self.imprint_field, self.leak_field)

                spent = e.move(self.hill, gamma)
                e.energy -= spent

                # Memory update from actual movement outcome
                if e.energy > COMP_COST:
                    e.update_memory(e.last_move_height_diff)
                    e.energy -= COMP_COST
                else:
                    break

                e.update_pattern(gamma)

                # Stabilization condition
                if tick_i >= 1:
                    current_grad = self.hill.gradient_at(e.q, e.r)
                    grad_diff = np.linalg.norm(current_grad - orig_grad)
                    if grad_diff < EPSILON_STABLE:
                        break

            # --- Radiation phase ---
            if e.energy > ENERGY_CAP:
                excess = e.energy - ENERGY_CAP
                radiation = RADIATION_SCALE * np.log1p(excess)
                hex_add(self.leak_field, e.q, e.r, R, radiation)
                e.energy = ENERGY_CAP

            # --- Replication check ---
            if e.can_replicate(tick) and len(self.entities) + len(new_entities) < MAX_ENTITIES:
                # Find first valid adjacent hex cell
                child_q, child_r = e.q, e.r
                for dq, dr in HEX_DIRS:
                    nq, nr = e.q + dq, e.r + dr
                    if is_valid_hex(nq, nr, R):
                        child_q, child_r = nq, nr
                        break

                child_window_size = len(e.memory) + WINDOW_GROWTH
                child_memory = np.zeros(child_window_size, dtype=int)
                child_memory[:len(e.memory)] = e.memory
                child_memory[0] = -1  # antiexistence

                child = Entity(
                    id=next_entity_id(),
                    q=child_q,
                    r=child_r,
                    memory=child_memory,
                    baseline_h=self.hill.height_at(child_q, child_r),
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
        """Position-based collision detection with hex (q, r) keys."""
        pos_groups = defaultdict(list)
        for e in self.entities:
            pos_groups[(e.q, e.r)].append(e)

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
        """Hex encirclement detection.
        Check if neighbors exist in 4+ of 6 direction sectors within RING_DISTANCE."""
        positions = {(e.q, e.r) for e in self.entities}
        for e in self.entities:
            sectors_occupied = 0
            for dir_idx in range(6):
                dq, dr = HEX_DIRS[dir_idx]
                found = False
                for d in range(1, RING_DISTANCE + 1):
                    if (e.q + dq * d, e.r + dr * d) in positions:
                        found = True
                        break
                if found:
                    sectors_occupied += 1

            if sectors_occupied >= 4:
                e.energy = max(0.0, e.energy - 0.1)
