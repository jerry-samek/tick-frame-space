"""
Experiment 49: Dynamic Sliding Window Temporal Rendering

Demonstrates O(n) bucketing with dynamic sliding window that adapts to performance budget,
enabling temporal effects (trails, motion blur, playback) and holographic horizon compression.

Theory: Extends 44_05's O(n) bucketing to implement Theory Doc 49's "existence buffer" concept,
where temporal addressability is computationally bounded and adapts dynamically to entity count.

Usage:
    python sliding_window_rendering.py

Controls:
    Space       - Pause/resume simulation
    Left/Right  - Rewind/fast-forward through window
    Home/End    - Jump to oldest/live frame
    T           - Toggle temporal trails
    B           - Toggle motion blur
    G           - Toggle ghost images
    H           - Toggle holographic horizon
    F           - Cycle FPS target (30/60/120/144/unlimited)
    +/-         - Increase/decrease entity count
    M           - Toggle sorting mode (for comparison)
    D           - Toggle HUD display
    ESC         - Exit
"""

import pygame
import numpy as np
import time
import random
import math
from dataclasses import dataclass
from typing import Optional, List, Iterator
from itertools import chain
import uuid


# ======================================================================================
# CONFIGURATION
# ======================================================================================

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
MAX_HISTORY = 100  # Number of lag buckets (0-99)
MAX_WINDOW_SIZE = 100  # Maximum ticks to retain in ring buffer

# Visual settings
BASE_RADIUS = 4
DEPTH_FACTOR = 0.002
CAMERA_X = SCREEN_WIDTH // 2
CAMERA_Y = SCREEN_HEIGHT // 2

# Simulation settings
TICK_RATE = 30  # Ticks per second (simulation rate)
INITIAL_ENTITY_COUNT = 10000

# Holographic horizon settings
HORIZON_GRID_RES = (100, 100)
HORIZON_DECAY = 0.95  # Slower decay for more persistent horizon


# ======================================================================================
# DATA STRUCTURES
# ======================================================================================

@dataclass
class Entity:
    """Entity in the simulation."""
    uuid: str
    x: float
    y: float
    temporal_lag: int  # 0-99, discrete temporal depth
    velocity_x: float
    velocity_y: float
    color: tuple
    lag_velocity: float = 0.0  # Rate of lag change


class EntityNode:
    """Linked list node for temporal bucketing."""
    __slots__ = ['entity', 'next']

    def __init__(self, entity: Entity, next: Optional['EntityNode'] = None):
        self.entity = entity
        self.next = next

    def stream(self) -> Iterator[Entity]:
        """Stream entities from this node forward as an iterator."""
        current = self
        while current:
            yield current.entity
            current = current.next


# ======================================================================================
# SLIDING WINDOW WITH DYNAMIC SIZING
# ======================================================================================

class SlidingWindow:
    """
    Ring buffer for temporal entity storage with dynamic window sizing.

    Structure: buffer[lag][time_offset] = EntityNode (linked list head)
    - lag: 0-99 (temporal depth buckets)
    - time_offset: 0 to max_window_size-1 (ring buffer index)

    Window size adapts dynamically to maintain target FPS:
    - More entities → smaller window (stay within budget)
    - Fewer entities → larger window (use spare capacity)
    """

    def __init__(self, max_history: int = MAX_HISTORY, max_window_size: int = MAX_WINDOW_SIZE):
        self.max_history = max_history
        self.max_window_size = max_window_size
        self.current_window_size = 5  # Start with small window

        # Ring buffer: [lag][time_offset] → EntityNode
        self.buffer = [[None for _ in range(max_window_size)] for _ in range(max_history)]

        self.head = 0  # Current write position (advances circularly)
        self.frame_count = 0

        # Statistics
        self.total_entities_bucketed = 0
        self.bucket_time_ms = 0.0

    def on_tick(self, entities: List[Entity]) -> Optional[List[Entity]]:
        """
        Bucket entities into current head position and advance.

        Returns expired frame if one is being overwritten (for holographic compression).
        """
        start_time = time.perf_counter()

        # Save old frame before overwriting (for holographic horizon)
        expired_frame = None
        if self.frame_count >= self.current_window_size:
            expired_frame = self._extract_frame_entities(self.head)

        # Clear current head position
        for lag in range(self.max_history):
            self.buffer[lag][self.head] = None

        # Bucket entities by temporal lag
        for entity in entities:
            lag = entity.temporal_lag
            # Prepend to linked list at [lag][head]
            self.buffer[lag][self.head] = EntityNode(entity, next=self.buffer[lag][self.head])

        # Advance head (circular)
        self.head = (self.head + 1) % self.max_window_size
        self.frame_count += 1

        # Statistics
        self.total_entities_bucketed += len(entities)
        self.bucket_time_ms = (time.perf_counter() - start_time) * 1000

        return expired_frame

    def on_tick_fast(self, entities: List[Entity]):
        """
        Fast path: bucket entities without extracting expired frame.
        Use when holographic horizon is disabled.
        """
        start_time = time.perf_counter()

        # Clear current head position
        for lag in range(self.max_history):
            self.buffer[lag][self.head] = None

        # Bucket entities by temporal lag
        for entity in entities:
            lag = entity.temporal_lag
            self.buffer[lag][self.head] = EntityNode(entity, next=self.buffer[lag][self.head])

        # Advance head (circular)
        self.head = (self.head + 1) % self.max_window_size
        self.frame_count += 1

        # Statistics
        self.total_entities_bucketed += len(entities)
        self.bucket_time_ms = (time.perf_counter() - start_time) * 1000

    def _extract_frame_entities(self, index: int) -> List[Entity]:
        """Extract all entities from a frame at given index."""
        entities = []
        for lag in range(self.max_history):
            node = self.buffer[lag][index]
            if node:
                entities.extend(node.stream())
        return entities

    def get_frame(self, offset: int = 0) -> Optional[List[Optional[EntityNode]]]:
        """
        Get frame N ticks in the past.

        Args:
            offset: 0 = current frame (head-1), 1 = one tick back, etc.

        Returns:
            List of linked list heads for each lag bucket, or None if out of bounds.
        """
        if offset >= self.current_window_size or offset >= self.frame_count:
            return None

        # Ring buffer index calculation
        index = (self.head - 1 - offset) % self.max_window_size

        # Return array of linked list heads for all lags
        return [self.buffer[lag][index] for lag in range(self.max_history)]

    def adjust_window_size(self, frame_time_ms: float, target_fps: int) -> int:
        """
        Dynamically adjust window size based on performance budget.

        Logic:
        - Target frame time = 1000 / target_fps
        - If frame_time < target_time: Can afford larger window
        - If frame_time > target_time: Must shrink window

        Returns new window size.
        """
        target_time = 1000 / target_fps

        if frame_time_ms < 0.1:  # Safety: avoid division by zero
            return self.max_window_size

        # How many frames can we afford?
        affordable_size = int(target_time / frame_time_ms)

        # Clamp to bounds [1, max_window_size]
        new_size = max(1, min(affordable_size, self.max_window_size))

        # Smooth adjustment (avoid thrashing on small fluctuations)
        if abs(new_size - self.current_window_size) > 1:
            self.current_window_size = new_size

        return self.current_window_size

    def get_stats(self) -> dict:
        """Return statistics for HUD display."""
        return {
            'window_size': self.current_window_size,
            'max_window': self.max_window_size,
            'frame_count': self.frame_count,
            'bucket_time_ms': self.bucket_time_ms,
            'total_bucketed': self.total_entities_bucketed,
        }


# ======================================================================================
# HOLOGRAPHIC HORIZON LAYER
# ======================================================================================

class HolographicHorizon:
    """
    Compresses expired frames beyond sliding window into statistical representation.

    Theory: Implements "horizon boundary" concept from Theory Doc 26, where information
    beyond the observable window is encoded as aggregate density/energy fields.
    """

    def __init__(self, grid_resolution: tuple = HORIZON_GRID_RES):
        self.grid_resolution = grid_resolution
        self.density_grid = np.zeros(grid_resolution, dtype=np.float32)
        self.energy_grid = np.zeros(grid_resolution, dtype=np.float32)
        self.total_frames_compressed = 0
        self.decay_factor = HORIZON_DECAY
        self.compress_time_ms = 0.0

    def compress_frame(self, entities: List[Entity]):
        """Add expired frame to holographic layer by binning entities into grid."""
        if not entities:
            return

        start_time = time.perf_counter()

        # Decay existing data (exponential fade)
        self.density_grid *= self.decay_factor
        self.energy_grid *= self.decay_factor

        # Bin entities into grid
        for entity in entities:
            grid_x = int((entity.x / SCREEN_WIDTH) * self.grid_resolution[0])
            grid_y = int((entity.y / SCREEN_HEIGHT) * self.grid_resolution[1])

            # Clamp to bounds
            grid_x = max(0, min(grid_x, self.grid_resolution[0] - 1))
            grid_y = max(0, min(grid_y, self.grid_resolution[1] - 1))

            # Accumulate density and energy
            self.density_grid[grid_y, grid_x] += 1.0
            self.energy_grid[grid_y, grid_x] += entity.temporal_lag

        self.total_frames_compressed += 1
        self.compress_time_ms = (time.perf_counter() - start_time) * 1000

    def render(self, screen: pygame.Surface):
        """Render holographic horizon as background heat map."""
        max_density = self.density_grid.max()
        if max_density < 0.01:
            return  # Nothing to render

        normalized = self.density_grid / max_density

        cell_width = SCREEN_WIDTH // self.grid_resolution[0]
        cell_height = SCREEN_HEIGHT // self.grid_resolution[1]

        for y in range(self.grid_resolution[1]):
            for x in range(self.grid_resolution[0]):
                density = normalized[y, x]
                if density > 0.01:  # Visibility threshold
                    # Color gradient: blue (low) → purple → red (high)
                    color = (
                        int(255 * density),
                        int(100 * (1 - density)),
                        int(255 * (1 - density))
                    )
                    alpha = int(100 * density)  # Semi-transparent

                    rect = pygame.Rect(
                        x * cell_width,
                        y * cell_height,
                        cell_width,
                        cell_height
                    )

                    # Draw with transparency
                    surface = pygame.Surface((cell_width, cell_height))
                    surface.set_alpha(alpha)
                    surface.fill(color)
                    screen.blit(surface, rect)

    def get_stats(self) -> dict:
        """Return statistics for HUD display."""
        return {
            'frames_compressed': self.total_frames_compressed,
            'max_density': float(self.density_grid.max()),
            'compress_time_ms': self.compress_time_ms,
        }


# ======================================================================================
# PLAYBACK CONTROLLER
# ======================================================================================

class PlaybackController:
    """
    Manages temporal playback state and navigation controls.

    Modes:
    - LIVE: Real-time simulation, render current frame (offset=0)
    - PAUSED: Frozen at specific frame, can navigate
    """

    def __init__(self):
        self.mode = 'LIVE'
        self.playback_offset = 0  # How many frames back from current

    def handle_input(self, event: pygame.event.Event, max_offset: int):
        """Handle keyboard input for playback control."""
        if event.key == pygame.K_SPACE:
            self.toggle_pause()
        elif event.key == pygame.K_LEFT:
            self.rewind(max_offset)
        elif event.key == pygame.K_RIGHT:
            self.fastforward()
        elif event.key == pygame.K_HOME:
            self.jump_to_oldest(max_offset)
        elif event.key == pygame.K_END:
            self.jump_to_live()

    def toggle_pause(self):
        """Toggle between LIVE and PAUSED modes."""
        if self.mode == 'LIVE':
            self.mode = 'PAUSED'
            self.playback_offset = 0
        else:
            self.mode = 'LIVE'
            self.playback_offset = 0

    def rewind(self, max_offset: int):
        """Step backward one frame."""
        self.mode = 'PAUSED'
        self.playback_offset = min(self.playback_offset + 1, max_offset - 1)

    def fastforward(self):
        """Step forward one frame."""
        if self.mode == 'PAUSED':
            self.playback_offset = max(0, self.playback_offset - 1)
            if self.playback_offset == 0:
                self.mode = 'LIVE'

    def jump_to_oldest(self, max_offset: int):
        """Jump to oldest frame in window."""
        self.mode = 'PAUSED'
        self.playback_offset = max(0, max_offset - 1)

    def jump_to_live(self):
        """Return to live simulation."""
        self.mode = 'LIVE'
        self.playback_offset = 0

    def get_render_offset(self) -> int:
        """Get current frame offset for rendering."""
        return self.playback_offset

    def get_stats(self) -> dict:
        """Return statistics for HUD display."""
        return {
            'mode': self.mode,
            'offset': self.playback_offset,
        }


# ======================================================================================
# SIMULATION
# ======================================================================================

class Simulation:
    """Tick-based entity simulation (30 ticks/sec)."""

    def __init__(self, entity_count: int):
        self.entities: List[Entity] = []
        self.tick_count = 0
        self.update_time_ms = 0.0
        self.create_entities(entity_count)

    def create_entities(self, count: int):
        """Initialize entities in a grid pattern."""
        self.entities.clear()

        # Grid layout
        grid_size = int(math.sqrt(count)) + 1
        spacing = min(SCREEN_WIDTH, SCREEN_HEIGHT) // (grid_size + 1)

        for i in range(count):
            row = i // grid_size
            col = i % grid_size

            x = (col + 1) * spacing + random.uniform(-spacing * 0.2, spacing * 0.2)
            y = (row + 1) * spacing + random.uniform(-spacing * 0.2, spacing * 0.2)

            # Random velocity
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)  # pixels per second
            vx = math.cos(angle) * speed / TICK_RATE  # convert to per-tick velocity
            vy = math.sin(angle) * speed / TICK_RATE

            # Initial lag (centered around 50)
            lag = random.randint(20, 80)
            lag_vel = random.uniform(-2, 2)

            # Color based on initial lag
            hue = lag / MAX_HISTORY
            color = pygame.Color(0, 0, 0)
            color.hsva = (hue * 360, 80, 100, 100)

            entity = Entity(
                uuid=str(uuid.uuid4()),
                x=x,
                y=y,
                temporal_lag=lag,
                velocity_x=vx,
                velocity_y=vy,
                color=(color.r, color.g, color.b),
                lag_velocity=lag_vel
            )
            self.entities.append(entity)

    def update_tick(self):
        """Update all entities for one simulation tick."""
        start_time = time.perf_counter()

        for entity in self.entities:
            # Update position
            entity.x += entity.velocity_x
            entity.y += entity.velocity_y

            # Bounce off walls
            if entity.x < 0 or entity.x > SCREEN_WIDTH:
                entity.velocity_x *= -1
                entity.x = max(0, min(SCREEN_WIDTH, entity.x))

            if entity.y < 0 or entity.y > SCREEN_HEIGHT:
                entity.velocity_y *= -1
                entity.y = max(0, min(SCREEN_HEIGHT, entity.y))

            # Update temporal lag (oscillate to create depth waves)
            lag_change = math.sin(self.tick_count * 0.01 + entity.x * 0.001) * 0.5
            entity.temporal_lag += int(lag_change)
            entity.temporal_lag = max(0, min(MAX_HISTORY - 1, entity.temporal_lag))

        self.tick_count += 1
        self.update_time_ms = (time.perf_counter() - start_time) * 1000

    def scale_entity_count(self, multiplier: float):
        """Scale entity count by multiplier."""
        new_count = max(100, int(len(self.entities) * multiplier))
        self.create_entities(new_count)

    def get_stats(self) -> dict:
        """Return statistics for HUD display."""
        return {
            'entity_count': len(self.entities),
            'tick_count': self.tick_count,
            'update_time_ms': self.update_time_ms,
        }


# ======================================================================================
# RENDERER
# ======================================================================================

class Renderer:
    """Handles all rendering operations."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.render_time_ms = 0.0
        self.render_mode = 'bucketed'  # 'bucketed' or 'sorted'

        # Temporal effect toggles
        self.show_trails = False
        self.show_motion_blur = False
        self.show_ghosts = False
        self.show_horizon = True
        self.show_hud = True

        self.trail_length = 5
        self.blur_samples = 3
        self.ghost_interval = 3

    def render_frame(self, sliding_window: SlidingWindow, playback_controller: PlaybackController,
                    holographic_horizon: HolographicHorizon):
        """Main render entry point."""
        start_time = time.perf_counter()

        self.screen.fill((0, 0, 0))  # Clear screen

        # Render holographic horizon first (background layer)
        if self.show_horizon:
            holographic_horizon.render(self.screen)

        # Get frame based on playback state
        offset = playback_controller.get_render_offset()

        # Render based on mode and effects
        if self.show_trails:
            self.render_with_trails(sliding_window, offset)
        elif self.show_motion_blur:
            self.render_with_motion_blur(sliding_window, offset)
        elif self.show_ghosts:
            self.render_with_ghosts(sliding_window, offset)
        else:
            self.render_bucketed(sliding_window, offset)

        self.render_time_ms = (time.perf_counter() - start_time) * 1000

    def render_bucketed(self, sliding_window: SlidingWindow, offset: int):
        """Render using O(n) bucketing (painter's algorithm)."""
        frame = sliding_window.get_frame(offset)
        if not frame:
            return

        # Render back-to-front (high lag → low lag)
        # Use direct while loop instead of generator for performance
        for lag in reversed(range(len(frame))):
            current = frame[lag]
            while current:
                self.draw_entity(current.entity, lag)
                current = current.next

    def render_with_trails(self, sliding_window: SlidingWindow, base_offset: int):
        """Render entities with temporal trails."""
        max_trail = min(self.trail_length, sliding_window.current_window_size)

        for trail_offset in range(max_trail):
            frame = sliding_window.get_frame(base_offset + trail_offset)
            if not frame:
                break

            # Fade older positions
            fade = 1.0 - (trail_offset / max_trail)
            alpha = int(255 * fade * 0.7)

            # Render all entities in this frame with fade
            # Use direct while loop for performance
            for lag in reversed(range(len(frame))):
                current = frame[lag]
                while current:
                    self.draw_entity(current.entity, lag, alpha=alpha, scale=fade)
                    current = current.next

    def render_with_motion_blur(self, sliding_window: SlidingWindow, base_offset: int):
        """Render entities with motion blur by blending positions."""
        # Accumulate entity positions across frames
        blended = {}

        for blur_offset in range(min(self.blur_samples, sliding_window.current_window_size)):
            frame = sliding_window.get_frame(base_offset + blur_offset)
            if not frame:
                break

            weight = 1.0 / (blur_offset + 1)

            # Use direct while loop for performance
            for lag in range(len(frame)):
                current = frame[lag]
                while current:
                    entity = current.entity
                    key = entity.uuid

                    if key not in blended:
                        blended[key] = {
                            'x': 0, 'y': 0, 'lag': lag,
                            'color': entity.color, 'weight_sum': 0
                        }

                    blended[key]['x'] += entity.x * weight
                    blended[key]['y'] += entity.y * weight
                    blended[key]['weight_sum'] += weight

                    current = current.next

        # Render blended positions
        for data in blended.values():
            if data['weight_sum'] < 0.01:
                continue

            x = data['x'] / data['weight_sum']
            y = data['y'] / data['weight_sum']

            # Create temporary entity for rendering
            blended_entity = Entity(
                uuid='',
                x=x,
                y=y,
                temporal_lag=data['lag'],
                velocity_x=0,
                velocity_y=0,
                color=data['color']
            )
            self.draw_entity(blended_entity, data['lag'])

    def render_with_ghosts(self, sliding_window: SlidingWindow, base_offset: int):
        """Render ghost images at discrete intervals."""
        for ghost_idx in range(0, sliding_window.current_window_size, self.ghost_interval):
            frame = sliding_window.get_frame(base_offset + ghost_idx)
            if not frame:
                break

            # Ghosts become more transparent with age
            alpha = int(200 * (1.0 - ghost_idx / sliding_window.current_window_size))

            # Use direct while loop for performance
            for lag in reversed(range(len(frame))):
                current = frame[lag]
                while current:
                    self.draw_entity(current.entity, lag, alpha=alpha)
                    current = current.next

    def draw_entity(self, entity: Entity, lag: int, alpha: int = 255, scale: float = 1.0):
        """Draw a single entity with depth scaling."""
        depth_scale = 1.0 / (1.0 + lag * DEPTH_FACTOR)

        screen_x = int(entity.x * depth_scale + CAMERA_X * (1 - depth_scale))
        screen_y = int(entity.y * depth_scale + CAMERA_Y * (1 - depth_scale))
        radius = max(1, int(BASE_RADIUS * depth_scale * scale))

        # Apply depth fade
        depth_fade = depth_scale * 0.7 + 0.3
        color = tuple(int(c * depth_fade) for c in entity.color)

        # Draw with optional alpha
        if alpha < 255:
            surface = pygame.Surface((radius * 2 + 2, radius * 2 + 2))
            surface.set_colorkey((0, 0, 0))
            surface.set_alpha(alpha)
            pygame.draw.circle(surface, color, (radius + 1, radius + 1), radius)
            self.screen.blit(surface, (screen_x - radius - 1, screen_y - radius - 1))
        else:
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)

    def draw_hud(self, simulation: Simulation, sliding_window: SlidingWindow,
                 playback_controller: PlaybackController, holographic_horizon: HolographicHorizon,
                 fps: float, target_fps: int):
        """Draw HUD overlay with statistics."""
        if not self.show_hud:
            return

        sim_stats = simulation.get_stats()
        window_stats = sliding_window.get_stats()
        playback_stats = playback_controller.get_stats()
        horizon_stats = holographic_horizon.get_stats()

        y = 10
        line_height = 25

        def draw_text(text: str, color=(255, 255, 255)):
            nonlocal y
            surface = self.font.render(text, True, color)
            self.screen.blit(surface, (10, y))
            y += line_height

        # Performance metrics
        draw_text(f"FPS: {fps:.1f} / {target_fps} target", (0, 255, 0))
        draw_text(f"Entities: {sim_stats['entity_count']:,}")
        draw_text(f"Frame time: {self.render_time_ms + sim_stats['update_time_ms']:.2f}ms")
        draw_text(f"  ├─ Simulation: {sim_stats['update_time_ms']:.2f}ms")
        draw_text(f"  ├─ Bucketing: {window_stats['bucket_time_ms']:.2f}ms")
        draw_text(f"  └─ Rendering: {self.render_time_ms:.2f}ms")

        y += 10

        # Window stats
        window_color = (255, 255, 0) if window_stats['window_size'] < 5 else (255, 255, 255)
        draw_text(f"Window: {window_stats['window_size']} / {window_stats['max_window']} ticks", window_color)
        temporal_memory_ms = (window_stats['window_size'] / TICK_RATE) * 1000
        draw_text(f"Temporal memory: {temporal_memory_ms:.0f}ms")

        y += 10

        # Playback state
        if playback_stats['mode'] == 'PAUSED':
            draw_text(f"⏸ PAUSED (offset: -{playback_stats['offset']} ticks)", (255, 255, 0))
        else:
            draw_text(f"▶ LIVE", (0, 255, 0))

        y += 10

        # Horizon stats
        draw_text(f"Horizon: {horizon_stats['frames_compressed']} frames compressed")
        draw_text(f"Max density: {horizon_stats['max_density']:.1f}")

        y += 10

        # Effects status (stream-based filter)
        effects_str = ", ".join(filter(None, (
            "Trails" if self.show_trails else None,
            "Blur" if self.show_motion_blur else None,
            "Ghosts" if self.show_ghosts else None,
            "Horizon" if self.show_horizon else None
        ))) or "None"
        draw_text(f"Effects: {effects_str}")

        # Controls hint
        y = SCREEN_HEIGHT - 120
        hints = [
            "Space: Pause | ←/→: Rewind/FF | Home/End: Jump",
            "T: Trails | B: Blur | G: Ghosts | H: Horizon",
            "F: FPS target | +/-: Scale entities | D: HUD | ESC: Exit"
        ]
        for hint in hints:
            surface = self.small_font.render(hint, True, (150, 150, 150))
            self.screen.blit(surface, (10, y))
            y += 20


# ======================================================================================
# MAIN LOOP
# ======================================================================================

def main():
    """Main application loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Experiment 49: Dynamic Sliding Window Temporal Rendering")
    clock = pygame.time.Clock()

    # Initialize components
    simulation = Simulation(INITIAL_ENTITY_COUNT)
    sliding_window = SlidingWindow()
    holographic_horizon = HolographicHorizon()
    playback_controller = PlaybackController()
    renderer = Renderer(screen)

    # Performance tracking
    target_fps = 60
    fps_samples = []
    last_tick_time = time.time()
    tick_interval = 1.0 / TICK_RATE

    running = True
    while running:
        frame_start = time.perf_counter()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    # Cycle FPS target
                    targets = [30, 60, 120, 144, 999]
                    current_idx = targets.index(target_fps) if target_fps in targets else 1
                    target_fps = targets[(current_idx + 1) % len(targets)]
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    simulation.scale_entity_count(1.5)
                elif event.key == pygame.K_MINUS:
                    simulation.scale_entity_count(1 / 1.5)
                elif event.key == pygame.K_t:
                    renderer.show_trails = not renderer.show_trails
                    renderer.show_motion_blur = False
                    renderer.show_ghosts = False
                elif event.key == pygame.K_b:
                    renderer.show_motion_blur = not renderer.show_motion_blur
                    renderer.show_trails = False
                    renderer.show_ghosts = False
                elif event.key == pygame.K_g:
                    renderer.show_ghosts = not renderer.show_ghosts
                    renderer.show_trails = False
                    renderer.show_motion_blur = False
                elif event.key == pygame.K_h:
                    renderer.show_horizon = not renderer.show_horizon
                elif event.key == pygame.K_d:
                    renderer.show_hud = not renderer.show_hud
                else:
                    # Playback controls
                    playback_controller.handle_input(event, sliding_window.current_window_size)

        # Simulation tick (30 Hz, independent of render rate)
        current_time = time.time()
        if current_time - last_tick_time >= tick_interval and playback_controller.mode == 'LIVE':
            simulation.update_tick()

            # Only extract/compress if a horizon is enabled (performance optimization)
            if renderer.show_horizon:
                expired_frame = sliding_window.on_tick(simulation.entities)
                if expired_frame:
                    holographic_horizon.compress_frame(expired_frame)
            else:
                sliding_window.on_tick_fast(simulation.entities)  # Skip extraction

            last_tick_time = current_time

        # Rendering
        renderer.render_frame(sliding_window, playback_controller, holographic_horizon)

        # Calculate FPS
        frame_time = (time.perf_counter() - frame_start) * 1000
        fps_samples.append(1000 / frame_time if frame_time > 0 else 0)
        if len(fps_samples) > 60:
            fps_samples.pop(0)
        avg_fps = sum(fps_samples) / len(fps_samples)

        # Dynamic window adjustment
        sliding_window.adjust_window_size(frame_time, target_fps)

        # Draw HUD
        renderer.draw_hud(simulation, sliding_window, playback_controller,
                         holographic_horizon, avg_fps, target_fps)

        pygame.display.flip()
        clock.tick(target_fps)

    pygame.quit()
    print("\nExperiment 49 completed.")
    print(f"Final stats:")
    print(f"  Entities: {len(simulation.entities):,}")
    print(f"  Window size: {sliding_window.current_window_size}")
    print(f"  Frames compressed: {holographic_horizon.total_frames_compressed}")


if __name__ == '__main__':
    main()
