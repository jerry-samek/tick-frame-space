import pygame
import numpy as np
import csv
import os
from dataclasses import dataclass, field
from typing import Optional

# ==========================
# Constants
# ==========================

WORLD_SIZE = 400
DELTA_H = 0.2              # global hill increment per commit
ALPHA_IMPRINT = 1.2         # imprint influence coefficient
MOVE_COST = 0.05
COMP_COST = 0.02
IMPRINT_COST = 0.08

PASSIVE_ENERGY_RATE = 0.005  # slope-based passive energy (Doc 03 Sec 7.1)
ENERGY_CAP = 2.0             # max energy before radiation bleeds excess
DECAY = 0.995               # hill natural sink per commit (Doc 03 Sec 2.1)
BETA_IMPRINT = 0.9          # imprint field decay per commit (Doc 02 Sec 7)
EPSILON_STABLE = 0.05       # stabilization condition (Doc 02 Sec 4.1.7)
EPSILON_DH = 0.01           # DeltaH threshold for correction logic (Doc 03 Sec 5)
REPLICATION_DH_THRESHOLD = 0.5   # |DeltaH| trigger for replication (Doc 03 Sec 6.1)
REPLICATION_DDH_THRESHOLD = -0.1 # DeltaDeltaH trigger for replication
REPLICATION_ENERGY_COST = 0.5
WINDOW_GROWTH = 1           # child window grows by 1 (Doc 03 Sec 3.2)
MAX_ENTITIES = 50
MAX_LOCAL_TICKS = 20
LEAK_DECAY = 0.95
RADIATION_SCALE = 0.3       # Lambda(E) = 0.3 * log1p(E)
MERGE_COMPAT_THRESHOLD = 0.5  # >50% memory overlap for constructive merge
MERGE_ENERGY_TRANSFER = 0.8   # 80% energy transfer on constructive merge
RING_DISTANCE = 5           # encirclement detection range (Doc 03 Sec 8.2)
MIN_REPLICATION_AGE = 10

# Gaussian diffusion kernel (Doc 02 Sec 1.3)
SPREAD_KERNEL = np.array([0.06, 0.24, 0.4, 0.24, 0.06])

# Entity colors for visualization
ENTITY_COLORS = [
    (0, 255, 0), (255, 255, 0), (0, 255, 255), (255, 128, 0),
    (128, 255, 0), (0, 128, 255), (255, 0, 128), (128, 0, 255),
    (255, 128, 128), (128, 255, 128),
]

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
# Entity (Doc 03 Sec 1, Doc 02 Sec 2)
# ==========================

@dataclass
class Entity:
    id: int
    x: int
    memory: np.ndarray
    pattern: float = 0.0
    energy: float = 0.0
    render_offset: int = 0
    baseline_h: float = 0.0       # height at creation (Doc 03 Sec 1)
    prev_delta_h: float = 0.0     # previous tick's DeltaH (Doc 03 Sec 4.2)
    age: int = 0                  # ticks since creation
    delta_h: float = 0.0          # current DeltaH
    delta_delta_h: float = 0.0    # current DeltaDeltaH

    def update_memory(self, delta_h: float):
        """DeltaH-based correction logic (Doc 03 Sec 5).
        Replaces NAND memory update with correction symbols."""
        if delta_h > EPSILON_DH:
            symbol = 1   # reinforce
        elif delta_h < -EPSILON_DH:
            symbol = -1  # reverse
        else:
            symbol = 0   # continue

        # FIFO: roll left, append new symbol
        self.memory = np.roll(self.memory, -1)
        self.memory[-1] = symbol

        # Antiexistence constraint: inject -1 at index 0 if none present
        if -1 not in self.memory:
            self.memory[0] = -1

    def local_gamma(self, hill, imprint_field, leak_field):
        """Enriched gamma field (Doc 02 Sec 2.1).
        Gamma = grad + 0.5*imp + 0.2*leak + 0.1*h*mem_coherence"""
        grad = hill.gradient_at(self.x)
        imp = imprint_field[self.x]
        leak = leak_field[self.x]
        h = hill.height[self.x]
        mem_coherence = np.mean(np.abs(self.memory))
        return grad + 0.5 * imp + 0.2 * leak + 0.1 * h * mem_coherence

    def move(self, hill, gamma: float) -> float:
        """Movement uses memory + gamma weighted vote (Doc 02 Sec 4.1.4).
        Direction = weighted: gradient (0.5) + memory bias (0.3) + gamma sign (0.2)"""
        grad = hill.gradient_at(self.x)
        grad_signal = -np.sign(grad)
        mem_bias = np.sign(np.mean(self.memory))
        gamma_signal = np.sign(gamma)

        direction = 0.5 * grad_signal + 0.3 * mem_bias + 0.2 * gamma_signal
        step = int(np.sign(direction))

        if step == 0:
            return 0.0
        if self.energy > MOVE_COST:
            self.x += step
            self.x = clamp(self.x, 0, len(hill.height) - 1)
            return MOVE_COST
        return 0.0

    def update_pattern(self, gamma: float):
        self.pattern += gamma

    def ready_to_imprint(self) -> bool:
        return self.energy > IMPRINT_COST and (-1 in self.memory)

    def imprint_value(self, gamma: float) -> float:
        return (1.0 + abs(self.pattern)) * np.tanh(gamma)

    def can_replicate(self) -> bool:
        """Replication trigger (Doc 03 Sec 6.1):
        |DeltaH| > threshold OR DeltaDeltaH < negative threshold,
        AND sufficient energy AND minimum age."""
        if self.age < MIN_REPLICATION_AGE:
            return False
        if self.energy < REPLICATION_ENERGY_COST:
            return False
        return (abs(self.delta_h) > REPLICATION_DH_THRESHOLD or
                self.delta_delta_h < REPLICATION_DDH_THRESHOLD)


# ==========================
# Hill (Doc 03 Sec 2)
# ==========================

@dataclass
class Hill:
    height: np.ndarray
    delta_H: float = DELTA_H
    alpha: float = ALPHA_IMPRINT
    decay: float = DECAY
    source: np.ndarray = field(default=None, repr=False)

    def __post_init__(self):
        n = len(self.height)
        center = n // 2
        x = np.arange(n)
        self.source = self.delta_H * np.exp(-0.5 * ((x - center) / 30.0) ** 2)

    def gradient_at(self, x: int) -> float:
        if x <= 0:
            return self.height[1] - self.height[0]
        if x >= len(self.height) - 1:
            return self.height[-1] - self.height[-2]
        return self.height[x + 1] - self.height[x - 1]

    def spread(self):
        """Gaussian diffusion (Doc 02 Sec 1.3).
        Replaces max-pooling expand_boundaries."""
        self.height = np.convolve(self.height, SPREAD_KERNEL, mode='same')

    def commit(self, imprint_field: np.ndarray):
        """Hill update: growth + imprint + spread + decay (no volume normalization)."""
        self.height += self.source
        self.height += self.alpha * imprint_field
        self.spread()

        # Global decay — hill naturally sinks (Doc 03 Sec 2.1)
        self.height *= self.decay
        # Floor at zero
        np.maximum(self.height, 0.0, out=self.height)


# ==========================
# World (Doc 01, Doc 02, Doc 03)
# ==========================

@dataclass
class World:
    hill: Hill
    entities: list
    imprint_field: np.ndarray
    leak_field: np.ndarray
    replication_events: int = 0
    merge_events: int = 0

    def commit_step(self):
        self.replication_events = 0
        self.merge_events = 0

        # --- Hill commits once ---
        old_heights = self.hill.height.copy()
        self.hill.commit(self.imprint_field)
        new_heights = self.hill.height.copy()

        # --- Imprint field decay (Doc 02 Sec 7) ---
        self.imprint_field *= BETA_IMPRINT

        # --- Leak field decay ---
        self.leak_field *= LEAK_DECAY

        # --- Process each entity ---
        new_entities = []
        for e in self.entities:
            e.age += 1

            # Energy acquisition (Doc 02 Sec 3)
            old_h = old_heights[e.x]
            new_h = new_heights[e.x]
            e.energy += max(0.0, new_h - old_h)

            # Passive slope energy (Doc 03 Sec 7.1)
            slope_energy = PASSIVE_ENERGY_RATE * abs(self.hill.gradient_at(e.x))
            e.energy += slope_energy

            # Compute DeltaH and DeltaDeltaH (Doc 03 Sec 4.1-4.2)
            e.delta_h = new_h - e.baseline_h
            e.delta_delta_h = e.delta_h - e.prev_delta_h
            e.prev_delta_h = e.delta_h

            # --- Local tick loop (Doc 02 Sec 4) ---
            orig_grad = self.hill.gradient_at(e.x)
            for tick_i in range(MAX_LOCAL_TICKS):
                if e.energy <= 0:
                    break

                gamma = e.local_gamma(self.hill, self.imprint_field, self.leak_field)

                # Memory transformation (Doc 03 Sec 5)
                if e.energy > COMP_COST:
                    e.update_memory(e.delta_h)
                    e.energy -= COMP_COST
                else:
                    break

                # Movement (Doc 02 Sec 4.1.4)
                spent = e.move(self.hill, gamma)
                e.energy -= spent

                # Pattern update (Doc 02 Sec 4.1.5)
                e.update_pattern(gamma)

                # Stabilization condition (Doc 02 Sec 4.1.7)
                if tick_i >= 1:
                    current_grad = self.hill.gradient_at(e.x)
                    if abs(current_grad - orig_grad) < EPSILON_STABLE:
                        break

            # --- Imprint phase (Doc 02 Sec 5) ---
            if e.ready_to_imprint():
                gamma = e.local_gamma(self.hill, self.imprint_field, self.leak_field)
                dI = e.imprint_value(gamma)

                e.render_offset = (e.render_offset + 1) % len(e.memory) - len(e.memory) // 2
                ix = clamp(e.x + e.render_offset, 0, len(self.imprint_field) - 1)

                kernel = [0.1, 0.8, 0.1]
                for k, w in enumerate(kernel):
                    px = ix + (k - 1)
                    if 0 <= px < len(self.imprint_field):
                        self.imprint_field[px] += dI * w

                e.energy -= IMPRINT_COST

            # --- Radiation phase (Doc 02 Sec 6) ---
            if e.energy > ENERGY_CAP:
                excess = e.energy - ENERGY_CAP
                radiation = RADIATION_SCALE * np.log1p(excess)
                self.leak_field[e.x] += radiation
                e.energy = ENERGY_CAP

            # --- Replication check (Doc 03 Sec 6) ---
            if e.can_replicate() and len(self.entities) + len(new_entities) < MAX_ENTITIES:
                child_x = clamp(e.x + 1, 0, len(self.hill.height) - 1)
                child_window_size = len(e.memory) + WINDOW_GROWTH
                child_memory = np.zeros(child_window_size, dtype=int)
                child_memory[0] = -1  # antiexistence

                child = Entity(
                    id=next_entity_id(),
                    x=child_x,
                    memory=child_memory,
                    baseline_h=self.hill.height[child_x],
                    energy=0.0,
                )
                e.energy -= REPLICATION_ENERGY_COST
                # Energy can go negative from replication cost; clamp
                e.energy = max(0.0, e.energy)
                new_entities.append(child)
                self.replication_events += 1

        # Add new entities
        self.entities.extend(new_entities)

        # --- Inter-entity interactions (Doc 03 Sec 8) ---
        self._resolve_collisions()
        self._detect_rings()

    def _resolve_collisions(self):
        """Position-based collision detection and merge logic (Doc 03 Sec 8.1)."""
        from collections import defaultdict
        pos_groups = defaultdict(list)
        for e in self.entities:
            pos_groups[e.x].append(e)

        to_remove = set()
        for pos, group in pos_groups.items():
            if len(group) < 2:
                continue
            # Pairwise merge: first two at same position
            while len(group) >= 2:
                a = group.pop(0)
                b = group.pop(0)
                if a.id in to_remove or b.id in to_remove:
                    continue

                # Compatibility: >50% memory overlap
                min_len = min(len(a.memory), len(b.memory))
                if min_len > 0:
                    overlap = np.sum(a.memory[:min_len] == b.memory[:min_len]) / min_len
                else:
                    overlap = 0.0

                if overlap > MERGE_COMPAT_THRESHOLD:
                    # Constructive merge — b absorbed into a
                    a.energy += b.energy * MERGE_ENERGY_TRANSFER
                    a.pattern += b.pattern * 0.5
                    to_remove.add(b.id)
                else:
                    # Destructive collision — energy loss
                    loss = min(a.energy, b.energy) * 0.5
                    a.energy -= loss
                    b.energy -= loss
                    a.energy = max(0.0, a.energy)
                    b.energy = max(0.0, b.energy)

                self.merge_events += 1

        self.entities = [e for e in self.entities if e.id not in to_remove]

    def _detect_rings(self):
        """Ring detection in 1D (Doc 03 Sec 8.2).
        Entity flanked within RING_DISTANCE on both sides → energy drain."""
        positions = {e.x for e in self.entities}
        for e in self.entities:
            has_left = any((e.x - d) in positions for d in range(1, RING_DISTANCE + 1)
                          if (e.x - d) != e.x)
            has_right = any((e.x + d) in positions for d in range(1, RING_DISTANCE + 1)
                           if (e.x + d) != e.x)
            if has_left and has_right:
                # Encirclement pressure: energy drain
                e.energy = max(0.0, e.energy - 0.1)


# ==========================
# CSV Output (Phase 6)
# ==========================

class CSVLogger:
    def __init__(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.entity_file = open(os.path.join(output_dir, "entities.csv"), "w", newline="")
        self.summary_file = open(os.path.join(output_dir, "summary.csv"), "w", newline="")
        self.entity_writer = csv.writer(self.entity_file)
        self.summary_writer = csv.writer(self.summary_file)

        self.entity_writer.writerow([
            "tick", "entity_id", "x", "baseline_h", "current_h", "energy",
            "delta_h", "delta_delta_h", "memory", "window_size", "pattern", "age"
        ])
        self.summary_writer.writerow([
            "tick", "entity_count", "total_energy", "avg_delta_h", "min_delta_h",
            "max_delta_h", "max_hill_height", "total_imprint", "total_leak",
            "replication_events", "merge_events"
        ])

    def log_tick(self, tick: int, world: 'World'):
        entities = world.entities

        # Per-entity detail
        for e in entities:
            current_h = world.hill.height[e.x]
            mem_str = "".join(str(int(m)) for m in e.memory)
            self.entity_writer.writerow([
                tick, e.id, e.x, f"{e.baseline_h:.4f}", f"{current_h:.4f}",
                f"{e.energy:.4f}", f"{e.delta_h:.4f}", f"{e.delta_delta_h:.4f}",
                mem_str, len(e.memory), f"{e.pattern:.4f}", e.age
            ])

        # Per-tick summary
        if entities:
            delta_hs = [e.delta_h for e in entities]
            total_energy = sum(e.energy for e in entities)
            avg_dh = np.mean(delta_hs)
            min_dh = min(delta_hs)
            max_dh = max(delta_hs)
        else:
            total_energy = 0.0
            avg_dh = min_dh = max_dh = 0.0

        self.summary_writer.writerow([
            tick, len(entities), f"{total_energy:.4f}",
            f"{avg_dh:.4f}", f"{min_dh:.4f}", f"{max_dh:.4f}",
            f"{np.max(world.hill.height):.4f}",
            f"{np.sum(world.imprint_field):.4f}",
            f"{np.sum(world.leak_field):.4f}",
            world.replication_events, world.merge_events
        ])

        # Flush periodically
        if tick % 100 == 0:
            self.entity_file.flush()
            self.summary_file.flush()

    def close(self):
        self.entity_file.close()
        self.summary_file.close()


# ==========================
# Pygame visualization
# ==========================

def run():
    pygame.init()
    width = WORLD_SIZE
    scale_x = 2
    screen_w = width * scale_x
    screen_h = 600

    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("1D Hill + Entities (Spec-aligned)")

    clock = pygame.time.Clock()

    x = np.arange(width)
    h0 = 5.0 * np.exp(-0.5 * ((x - width // 2) / 20.0) ** 2)

    hill = Hill(height=h0)

    # Initial entities — one on each side of the hill
    entity0 = Entity(
        id=next_entity_id(),
        x=width // 2 + 5,
        memory=np.array([1, 0, -1, 1], dtype=int),
        baseline_h=h0[width // 2 + 5],
        energy=1.0,
    )
    entity1 = Entity(
        id=next_entity_id(),
        x=width // 2 - 5,
        memory=np.array([1, 0, -1, 1], dtype=int),
        baseline_h=h0[width // 2 - 5],
        energy=1.0,
    )
    entity2 = Entity(
        id=next_entity_id(),
        x=width // 2 ,
        memory=np.array([1, 0, -1, 1], dtype=int),
        baseline_h=h0[width // 2 - 0],
        energy=1.0,
    )
    imprint = np.zeros(width, dtype=float)
    leak = np.zeros(width, dtype=float)

    world = World(hill=hill, entities=[entity0, entity1, entity2], imprint_field=imprint, leak_field=leak)

    # CSV logger
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    logger = CSVLogger(output_dir)

    running = True
    tick = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        world.commit_step()
        tick += 1

        logger.log_tick(tick, world)

        screen.fill((0, 0, 0))

        baseline_y = 400
        # Adaptive Y scaling (Phase 1d)
        max_h = np.max(world.hill.height)
        scale_y = 300.0 / max(max_h, 1.0)

        # Draw hill
        for x in range(width):
            h = world.hill.height[x]
            y = int(baseline_y - h * scale_y)
            pygame.draw.line(screen, (200, 200, 200),
                             (x * scale_x, baseline_y),
                             (x * scale_x, y), 1)

            if world.imprint_field[x] != 0:
                pygame.draw.circle(screen, (80, 80, 255),
                                   (x * scale_x, y), 2)

            if world.leak_field[x] != 0:
                pygame.draw.circle(screen, (255, 80, 80),
                                   (x * scale_x, y), 2)

        # Draw entities with distinct colors
        for i, e in enumerate(world.entities):
            color = ENTITY_COLORS[i % len(ENTITY_COLORS)]
            ex = e.x * scale_x
            ey = int(baseline_y - world.hill.height[e.x] * scale_y)
            pygame.draw.circle(screen, color, (ex, ey), 5)

        # HUD (Phase 5)
        font = pygame.font.SysFont("consolas", 14)
        hud_y = 10

        # Global info
        txt = font.render(
            f"tick={tick}  entities={len(world.entities)}  "
            f"max_h={max_h:.2f}  repl={world.replication_events}  merge={world.merge_events}",
            True, (200, 200, 200)
        )
        screen.blit(txt, (10, hud_y))
        hud_y += 18

        # Per-entity info (show first 5)
        for i, e in enumerate(world.entities[:5]):
            color = ENTITY_COLORS[i % len(ENTITY_COLORS)]
            mem_str = "".join(str(int(m)) for m in e.memory)
            txt = font.render(
                f"#{e.id} x={e.x} E={e.energy:.2f} dH={e.delta_h:.3f} "
                f"ddH={e.delta_delta_h:.3f} W={mem_str} age={e.age}",
                True, color
            )
            screen.blit(txt, (10, hud_y))
            hud_y += 16

        if len(world.entities) > 5:
            txt = font.render(f"... +{len(world.entities) - 5} more", True, (150, 150, 150))
            screen.blit(txt, (10, hud_y))

        pygame.display.flip()
        clock.tick(60)

    logger.close()
    pygame.quit()

if __name__ == "__main__":
    run()
