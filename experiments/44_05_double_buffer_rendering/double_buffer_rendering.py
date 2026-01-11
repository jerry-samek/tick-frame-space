#!/usr/bin/env python3
"""
Experiment 44_05: Double-Buffer Temporal Rendering

Demonstrates O(n) bucketing approach with double-buffering for
continuous simulation + rendering without blocking.

Architecture:
- CPU: Continuous tick loop, fills one buffer while GPU renders the other
- GPU: Renders from stable buffer, no synchronization needed
- Swap: Atomic pointer swap every SWAP_INTERVAL ms (8.33ms @ 120 FPS)

This addresses the O(n log n) sorting bottleneck identified in theory doc 45_01.
"""

import pygame
import time
import math
import random
from dataclasses import dataclass
from typing import List
from collections import deque


# Configuration
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
CAMERA_X = SCREEN_WIDTH // 2
CAMERA_Y = SCREEN_HEIGHT // 2

MAX_HISTORY = 100  # Maximum temporal lag
DEPTH_FACTOR = 0.02  # Perspective depth scaling
BASE_RADIUS = 5  # Entity base radius

# FPS modes
FPS_MODES = [30, 60, 120, 144, 0]  # 0 = unlimited
FPS_MODE_NAMES = {30: "30 FPS", 60: "60 FPS", 120: "120 FPS", 144: "144 FPS", 0: "UNLIMITED"}

TARGET_FPS = 60  # Rendering FPS (will be modified by user)
SWAP_INTERVAL = 1.0 / 120  # Buffer swap frequency (120 Hz)

TICKS_PER_SECOND = 30  # Simulation tick rate


@dataclass
class Entity:
    """Minimal entity with 2D position and temporal lag"""
    x: float
    y: float
    temporal_lag: int
    color: tuple = (100, 200, 255)
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    energy: int = 1000


class EntityNode:
    """
    Linked list node for temporal bucketing.

    Represents the temporal chain of entities at the same lag value.
    This structure naturally mirrors the recursive/temporal nature of tick-frame theory:
    - Each entity points to the "next" entity in the same temporal slice
    - Clearing buckets is O(1) - just set head to None
    - Insertion is O(1) - prepend to head
    """
    __slots__ = ['entity', 'next']  # Memory optimization

    def __init__(self, entity: Entity, next=None):
        self.entity = entity
        self.next = next


class DoubleBuffer:
    """
    Double-buffer system for lock-free CPU/GPU coordination.

    Uses linked lists instead of Python lists for O(1) bucket clearing.
    Each buffer is an array of linked list heads (one per temporal lag value).
    """

    def __init__(self, max_history=MAX_HISTORY):
        self.max_history = max_history

        # Two buffers: A and B
        # Each buffer is an array of linked list heads (one per lag value)
        # None = empty bucket
        self.buffer_a = [None] * max_history
        self.buffer_b = [None] * max_history

        # Pointers to current buffers
        self.fill_buffer = self.buffer_a  # CPU writes here
        self.render_buffer = self.buffer_b  # GPU reads here

        # Timing
        self.last_swap_time = time.time()
        self.swap_count = 0

    def bucket_entities(self, entities: List[Entity]):
        """
        Bucket entities by temporal lag into fill_buffer using linked lists.

        Complexity:
        - Clear: O(1) - just reset array to None values
        - Bucket: O(n) - insert each entity at head of linked list

        Total: O(n) - eliminates the O(MAX_HISTORY) clear loop!
        """
        # Clear buckets: O(1) - reset all heads to None
        # (Previous list approach required O(MAX_HISTORY) to clear each bucket)
        self.fill_buffer[:] = [None] * self.max_history

        # Bucket entities by lag: O(n)
        # Insert at head of linked list - O(1) per entity
        for entity in entities:
            lag = min(max(0, entity.temporal_lag), self.max_history - 1)

            # Prepend to linked list (like push to stack)
            # Creates temporal chain: new_entity -> old_head -> ...
            self.fill_buffer[lag] = EntityNode(entity, next=self.fill_buffer[lag])

    def try_swap(self) -> bool:
        """
        Attempt to swap buffers if SWAP_INTERVAL has elapsed.
        Returns True if swap occurred.
        """
        now = time.time()
        if (now - self.last_swap_time) >= SWAP_INTERVAL:
            # Atomic pointer swap - no locking needed
            self.fill_buffer, self.render_buffer = self.render_buffer, self.fill_buffer
            self.last_swap_time = now
            self.swap_count += 1
            return True
        return False

    def get_render_buffer(self):
        """Get current render buffer (stable, won't change during render)"""
        return self.render_buffer

    def get_stats(self):
        """Get buffer statistics"""
        # Count nodes in linked lists
        def count_linked_list(head):
            count = 0
            current = head
            while current:
                count += 1
                current = current.next
            return count

        fill_count = sum(count_linked_list(head) for head in self.fill_buffer)
        render_count = sum(count_linked_list(head) for head in self.render_buffer)

        return {
            'fill_count': fill_count,
            'render_count': render_count,
            'swap_count': self.swap_count,
            'time_since_swap': time.time() - self.last_swap_time
        }


class Simulation:
    """Tick-based simulation (runs on CPU continuously)"""

    def __init__(self, entity_count=1000):
        self.tick_count = 0
        self.entities = self.create_entities(entity_count)
        self.tick_times = deque(maxlen=100)

    def create_entities(self, count: int) -> List[Entity]:
        """Create initial entity grid"""
        entities = []
        grid_size = int(math.sqrt(count))

        for i in range(grid_size):
            for j in range(grid_size):
                x = 200 + i * 30
                y = 200 + j * 30
                lag = (i + j) % MAX_HISTORY  # Diagonal gradient

                # Random gentle motion
                vx = random.uniform(-0.5, 0.5)
                vy = random.uniform(-0.5, 0.5)

                entities.append(Entity(
                    x=x, y=y,
                    temporal_lag=lag,
                    velocity_x=vx,
                    velocity_y=vy
                ))

        return entities

    def update_tick(self):
        """Run one simulation tick - updates all entities"""
        start = time.perf_counter()

        for entity in self.entities:
            # Update position
            entity.x += entity.velocity_x
            entity.y += entity.velocity_y

            # Bounce off screen edges
            if entity.x < 0 or entity.x > SCREEN_WIDTH:
                entity.velocity_x *= -1
            if entity.y < 0 or entity.y > SCREEN_HEIGHT:
                entity.velocity_y *= -1

            # Update temporal lag (oscillate for visual effect)
            lag_delta = int(math.sin(self.tick_count * 0.01 + entity.x * 0.01) * 5)
            entity.temporal_lag = max(0, min(MAX_HISTORY - 1,
                                            entity.temporal_lag + lag_delta))

            # Energy accumulation
            entity.energy = min(10000, entity.energy + 1)

        self.tick_count += 1
        elapsed = (time.perf_counter() - start) * 1000
        self.tick_times.append(elapsed)

    def get_stats(self):
        """Get simulation statistics"""
        avg_tick = sum(self.tick_times) / len(self.tick_times) if self.tick_times else 0
        return {
            'tick_count': self.tick_count,
            'entity_count': len(self.entities),
            'avg_tick_ms': avg_tick
        }


class Renderer:
    """Render from stable buffer (runs at fixed FPS)"""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.frame_times = deque(maxlen=100)
        self.bucket_mode = True  # Toggle between bucketing and sorting

    def render_bucketed(self, double_buffer: DoubleBuffer):
        """
        Render using bucketing approach with linked lists (O(n)).
        Iterates buckets back-to-front (high lag -> low lag).
        Traverses linked list for each lag bucket.
        """
        start = time.perf_counter()

        self.screen.fill((0, 0, 0))
        buffer = double_buffer.get_render_buffer()

        # Iterate buckets back-to-front (painter's algorithm)
        entities_drawn = 0
        for lag in reversed(range(len(buffer))):
            head = buffer[lag]

            if not head:  # Empty bucket
                continue

            # Depth scaling based on lag
            depth_scale = 1.0 / (1.0 + lag * DEPTH_FACTOR)

            # Traverse linked list for this lag value
            current = head
            while current:
                entity = current.entity

                # Screen position with perspective
                screen_x = int(entity.x * depth_scale + CAMERA_X * (1 - depth_scale))
                screen_y = int(entity.y * depth_scale + CAMERA_Y * (1 - depth_scale))

                # Size and color by depth
                radius = max(1, int(BASE_RADIUS * depth_scale))
                fade = depth_scale * 0.7 + 0.3
                color = tuple(int(c * fade) for c in entity.color)

                # Draw entity
                pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)
                entities_drawn += 1

                # Move to next in temporal chain
                current = current.next

        elapsed = (time.perf_counter() - start) * 1000
        self.frame_times.append(elapsed)

        return entities_drawn

    def render_sorted(self, double_buffer: DoubleBuffer):
        """
        Render using sorting approach (O(n log n)) - for comparison.
        Flattens linked list buckets and sorts.
        """
        start = time.perf_counter()

        self.screen.fill((0, 0, 0))
        buffer = double_buffer.get_render_buffer()

        # Flatten linked list buckets into single list
        all_entities = []
        for head in buffer:
            # Traverse each linked list
            current = head
            while current:
                all_entities.append(current.entity)
                current = current.next

        # Sort by temporal lag (back to front)
        sorted_entities = sorted(all_entities, key=lambda e: -e.temporal_lag)

        # Render
        entities_drawn = 0
        for entity in sorted_entities:
            depth_scale = 1.0 / (1.0 + entity.temporal_lag * DEPTH_FACTOR)

            screen_x = int(entity.x * depth_scale + CAMERA_X * (1 - depth_scale))
            screen_y = int(entity.y * depth_scale + CAMERA_Y * (1 - depth_scale))

            radius = max(1, int(BASE_RADIUS * depth_scale))
            fade = depth_scale * 0.7 + 0.3
            color = tuple(int(c * fade) for c in entity.color)

            pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)
            entities_drawn += 1

        elapsed = (time.perf_counter() - start) * 1000
        self.frame_times.append(elapsed)

        return entities_drawn

    def render(self, double_buffer: DoubleBuffer):
        """Render frame using current mode"""
        if self.bucket_mode:
            return self.render_bucketed(double_buffer)
        else:
            return self.render_sorted(double_buffer)

    def draw_hud(self, sim_stats, buffer_stats, entities_drawn, fps, target_fps, fps_mode_name):
        """Draw HUD with statistics"""
        avg_frame = sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0

        mode_text = "BUCKETING O(n)" if self.bucket_mode else "SORTING O(n log n)"

        # Color code FPS based on target
        fps_color = (100, 255, 100)  # Green
        if target_fps > 0:
            if fps < target_fps * 0.9:
                fps_color = (255, 100, 100)  # Red - below target
            elif fps < target_fps * 0.95:
                fps_color = (255, 200, 100)  # Orange - close

        hud_lines = [
            f"Render Mode: {mode_text}",
            f"FPS Target: {fps_mode_name}  (press F to cycle)",
            f"Entities: {sim_stats['entity_count']:,}  Drawn: {entities_drawn:,}",
            f"Tick: {sim_stats['tick_count']:,}  Tick time: {sim_stats['avg_tick_ms']:.2f}ms",
            f"Frame time: {avg_frame:.2f}ms",
            f"Buffer swaps: {buffer_stats['swap_count']:,}  ({buffer_stats['time_since_swap']*1000:.1f}ms since last)",
            "",
            "Controls:",
            "  M: Toggle bucketing O(n) / sorting O(n log n)",
            "  F: Cycle FPS target (30/60/120/144/unlimited)",
            "  +/-: Adjust entity count (×1.5 / ×0.67)",
            "  SPACE: Reset simulation",
            "  ESC: Quit"
        ]

        y = 10
        for i, line in enumerate(hud_lines):
            # Use colored text for FPS line
            if i == 1 and "FPS Target" in line:
                text = self.font.render(line, True, fps_color)
            else:
                text = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (10, y))
            y += 25

        # Big FPS indicator
        fps_text = f"{fps:.1f}" if target_fps > 0 else f"{fps:.0f}"
        big_font = pygame.font.Font(None, 72)
        fps_surface = big_font.render(fps_text, True, fps_color)
        self.screen.blit(fps_surface, (SCREEN_WIDTH - 150, 10))

    def get_stats(self):
        """Get renderer statistics"""
        avg_frame = sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0
        return {
            'avg_frame_ms': avg_frame,
            'mode': 'bucketing' if self.bucket_mode else 'sorting'
        }


def main():
    """Main experiment loop"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Experiment 44_05: Double-Buffer Temporal Rendering")
    clock = pygame.time.Clock()

    # Initialize systems
    simulation = Simulation(entity_count=10000)  # Start with 10k entities
    double_buffer = DoubleBuffer(max_history=MAX_HISTORY)
    renderer = Renderer(screen)

    # FPS mode management
    fps_mode_index = 1  # Start at 60 FPS
    target_fps = FPS_MODES[fps_mode_index]

    # Timing
    last_tick_time = time.time()
    tick_interval = 1.0 / TICKS_PER_SECOND

    running = True
    frame_count = 0
    fps_timer = time.time()
    current_fps = 0

    print("="*70)
    print("Experiment 44_05: Double-Buffer Temporal Rendering")
    print("="*70)
    print(f"\nInitial configuration:")
    print(f"  Entities: {len(simulation.entities):,}")
    print(f"  Max temporal lag: {MAX_HISTORY}")
    print(f"  Swap interval: {SWAP_INTERVAL*1000:.1f}ms ({1/SWAP_INTERVAL:.0f} Hz)")
    print(f"  Target render FPS: {FPS_MODE_NAMES[target_fps]}")
    print(f"  Simulation tick rate: {TICKS_PER_SECOND} tps")
    print(f"\nControls:")
    print(f"  M: Toggle bucketing O(n) / sorting O(n log n)")
    print(f"  F: Cycle FPS target (30/60/120/144/unlimited)")
    print(f"  +/-: Adjust entity count")
    print("="*70)

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    renderer.bucket_mode = not renderer.bucket_mode
                    mode = "BUCKETING O(n)" if renderer.bucket_mode else "SORTING O(n log n)"
                    print(f"Switched to {mode}")
                elif event.key == pygame.K_f:
                    # Cycle FPS mode
                    fps_mode_index = (fps_mode_index + 1) % len(FPS_MODES)
                    target_fps = FPS_MODES[fps_mode_index]
                    print(f"FPS target: {FPS_MODE_NAMES[target_fps]}")
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    # Add more entities
                    new_count = int(len(simulation.entities) * 1.5)
                    simulation = Simulation(entity_count=new_count)
                    print(f"Entity count: {new_count:,}")
                elif event.key == pygame.K_MINUS:
                    # Remove entities
                    new_count = max(100, int(len(simulation.entities) * 0.67))
                    simulation = Simulation(entity_count=new_count)
                    print(f"Entity count: {new_count:,}")
                elif event.key == pygame.K_SPACE:
                    # Reset
                    simulation = Simulation(entity_count=len(simulation.entities))
                    print("Reset simulation")

        # Simulation tick (independent of render FPS)
        now = time.time()
        if (now - last_tick_time) >= tick_interval:
            simulation.update_tick()
            double_buffer.bucket_entities(simulation.entities)
            double_buffer.try_swap()
            last_tick_time = now

        # Rendering
        entities_drawn = renderer.render(double_buffer)

        # HUD
        sim_stats = simulation.get_stats()
        buffer_stats = double_buffer.get_stats()
        renderer.draw_hud(sim_stats, buffer_stats, entities_drawn, current_fps,
                         target_fps, FPS_MODE_NAMES[target_fps])

        pygame.display.flip()

        # Tick clock at target FPS (0 = unlimited)
        if target_fps > 0:
            clock.tick(target_fps)
        else:
            clock.tick()  # No limit

        # FPS calculation
        frame_count += 1
        if (now - fps_timer) >= 1.0:
            current_fps = frame_count
            frame_count = 0
            fps_timer = now

    # Cleanup
    pygame.quit()

    # Final stats
    print("\n" + "="*70)
    print("EXPERIMENT COMPLETE")
    print("="*70)
    sim_stats = simulation.get_stats()
    buffer_stats = double_buffer.get_stats()
    renderer_stats = renderer.get_stats()

    print(f"\nFinal statistics:")
    print(f"  Total ticks: {sim_stats['tick_count']:,}")
    print(f"  Total buffer swaps: {buffer_stats['swap_count']:,}")
    print(f"  Avg tick time: {sim_stats['avg_tick_ms']:.2f}ms")
    print(f"  Avg frame time: {renderer_stats['avg_frame_ms']:.2f}ms")
    print(f"  Final mode: {renderer_stats['mode']}")
    print(f"  Entity count: {sim_stats['entity_count']:,}")


if __name__ == "__main__":
    main()
