"""
Experiment 44_04: Multi-Entity Temporal Depth

Tests simplified rendering when temporal_lag is used DIRECTLY as z-coordinate.
Key hypothesis: If z IS temporal, rendering should be trivial.

Extends 44_03 findings to 100+ entities with dramatically simpler code.
"""

import json
import math
import random
from datetime import datetime
from pathlib import Path

import pygame

# ============================================================================
# CONFIGURATION
# ============================================================================

WIDTH, HEIGHT = 1400, 900
FPS = 30

# Energy and movement
ENERGY_INCREMENT = 1
MOVEMENT_COST = 10
LAG_COST_INCREASE = 5     # Cost to increase lag (fall behind)
LAG_COST_DECREASE = 50    # Cost to decrease lag (catch up) - 10x penalty

# Rendering
CAMERA_X, CAMERA_Y = WIDTH // 2, HEIGHT // 2
DEPTH_FACTOR = 0.015      # How much depth affects scale
BASE_RADIUS = 5           # Base entity size
MAX_Z_DISPLAY = 100       # Maximum lag for visualization

# Entity patterns
INITIAL_PATTERN = "grid"  # "grid", "random", "shells", "wave"
ENTITY_COUNT = 1000

# Logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ============================================================================
# EXPERIMENT LOGGER
# ============================================================================

class ExperimentLogger:
    """Logs experiment interactions"""

    def __init__(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = LOG_DIR / f"experiment_{timestamp}.json"
        self.events = []
        self.session_start = datetime.now().isoformat()

    def log_event(self, event_type, data):
        event = {
            "tick": data.get("tick", 0),
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.events.append(event)

    def log_force_attempt(self, direction, tick, successes, failures, avg_lag_before, avg_lag_after):
        self.log_event("force_attempt", {
            "tick": tick,
            "direction": direction,
            "successes": successes,
            "failures": failures,
            "success_rate": successes / (successes + failures) if (successes + failures) > 0 else 0,
            "avg_lag_before": avg_lag_before,
            "avg_lag_after": avg_lag_after
        })

    def log_pattern_change(self, tick, pattern, entity_count):
        self.log_event("pattern_change", {
            "tick": tick,
            "pattern": pattern,
            "entity_count": entity_count
        })

    def save(self):
        with open(self.log_file, 'w') as f:
            json.dump({
                "session_start": self.session_start,
                "session_end": datetime.now().isoformat(),
                "total_events": len(self.events),
                "events": self.events
            }, f, indent=2)
        print(f"\nLog saved to: {self.log_file}")

# ============================================================================
# ENTITY MODEL
# ============================================================================

class Entity:
    """
    Entity in 2D space with temporal lag as z-coordinate.

    KEY SIMPLIFICATION: z = temporal_lag (direct, not transformed)
    """

    def __init__(self, x, y, z=0, color=(255, 255, 255), velocity=(0, 0)):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)  # Temporal lag IS the z-coordinate
        self.color = color
        self.energy = 1000  # Initial energy
        self.velocity = velocity
        self.base_color = color

    def update(self, tick):
        """Update entity - movement in XY creates lag in Z"""
        self.energy += ENERGY_INCREMENT

        # Move in XY plane if we have velocity
        dx, dy = self.velocity
        if dx != 0 or dy != 0:
            distance = math.sqrt(dx*dx + dy*dy)
            cost = int(distance * MOVEMENT_COST)

            if self.energy >= cost:
                self.x += dx
                self.y += dy
                self.energy -= cost

                # Movement in XY creates temporal lag
                # (entities fall behind when they spend energy on spatial movement)
                self.z += distance * 0.1

    def increase_lag(self, amount):
        """Increase temporal lag (fall behind in time) - should WORK"""
        cost = int(amount * LAG_COST_INCREASE)
        if self.energy >= cost:
            self.energy -= cost
            self.z += amount
            return True
        return False

    def decrease_lag(self, amount):
        """Decrease temporal lag (catch up to present) - should FAIL"""
        if self.z <= 0:
            return False  # Already at present, can't go to future

        cost = int(amount * LAG_COST_DECREASE)  # 10x more expensive
        if self.energy >= cost:
            reduction = min(amount, self.z)
            self.energy -= cost
            self.z -= reduction
            return True
        return False

# ============================================================================
# ENTITY PATTERNS
# ============================================================================

def spawn_grid(count=100):
    """Grid pattern with diagonal lag gradient"""
    entities = []
    grid_size = int(math.sqrt(count))
    spacing = min(WIDTH, HEIGHT) // (grid_size + 2)
    start_x = (WIDTH - spacing * grid_size) // 2
    start_y = (HEIGHT - spacing * grid_size) // 2

    for i in range(grid_size):
        for j in range(grid_size):
            x = start_x + i * spacing
            y = start_y + j * spacing
            z = (i + j) * 3  # Diagonal gradient
            color = (200, 100 + i * 10, 100 + j * 10)
            entities.append(Entity(x, y, z, color))

    return entities

def spawn_random(count=100):
    """Random cloud with random lag distribution"""
    entities = []
    for _ in range(count):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        z = random.randint(0, 50)
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        entities.append(Entity(x, y, z, color))

    return entities

def spawn_shells(count=100):
    """Concentric shells with increasing lag"""
    entities = []
    num_shells = 8
    points_per_shell = count // num_shells

    for shell in range(num_shells):
        radius = 80 + shell * 40
        lag = shell * 8
        color_intensity = 255 - shell * 20

        for i in range(points_per_shell):
            angle = (i / points_per_shell) * 2 * math.pi
            x = CAMERA_X + radius * math.cos(angle)
            y = CAMERA_Y + radius * math.sin(angle)
            color = (color_intensity, color_intensity, 255)
            entities.append(Entity(x, y, lag, color))

    return entities

def spawn_wave(count=100):
    """Wave pattern - entities at different phases"""
    entities = []
    spacing = WIDTH // (count + 1)

    for i in range(count):
        x = spacing * (i + 1)
        y = HEIGHT // 2
        z = 0  # Will oscillate based on tick
        phase = (i / count) * 2 * math.pi
        color = (int(128 + 127 * math.sin(phase)),
                int(128 + 127 * math.cos(phase)), 200)

        entity = Entity(x, y, z, color)
        entity.wave_phase = phase  # Store phase for wave motion
        entities.append(entity)

    return entities

PATTERNS = {
    "grid": spawn_grid,
    "random": spawn_random,
    "shells": spawn_shells,
    "wave": spawn_wave
}

# ============================================================================
# SIMPLIFIED RENDERING (THE KEY INNOVATION)
# ============================================================================

def render_entities(screen, entities, show_lag_values=False):
    """
    SIMPLIFIED RENDERING: Use temporal_lag directly as z.

    This should be < 15 lines vs 44_03's 50+ lines.
    The simplicity itself validates the theory.
    """
    # Sort by z (temporal lag) for correct depth order - entities with higher lag appear "behind"
    sorted_entities = sorted(entities, key=lambda e: -e.z)

    font = pygame.font.SysFont('monospace', 10) if show_lag_values else None

    for entity in sorted_entities:
        # Simple depth scaling - entities further in time appear smaller and closer to center
        depth_scale = 1.0 / (1.0 + entity.z * DEPTH_FACTOR)

        # Screen position with simple perspective (scale toward camera)
        screen_x = int(entity.x * depth_scale + CAMERA_X * (1 - depth_scale))
        screen_y = int(entity.y * depth_scale + CAMERA_Y * (1 - depth_scale))

        # Size scales with depth
        radius = max(1, int(BASE_RADIUS * depth_scale))

        # Color fades with depth (optional visual enhancement)
        fade = depth_scale * 0.7 + 0.3  # Fade to 30% at max depth
        color = tuple(int(c * fade) for c in entity.color)

        # Draw entity
        pygame.draw.circle(screen, color, (screen_x, screen_y), radius)

        # Optionally show lag value
        if show_lag_values and entity.z > 0:
            lag_text = font.render(f"{int(entity.z)}", True, (150, 150, 150))
            screen.blit(lag_text, (screen_x + 8, screen_y - 5))

# That's it! ~20 lines including comments and lag display.
# Compare to 44_03's complex perspective projection code.

# ============================================================================
# DEPTH STATISTICS
# ============================================================================

def get_depth_stats(entities):
    """Calculate statistics about temporal depth distribution"""
    if not entities:
        return {}

    lags = [e.z for e in entities]
    energies = [e.energy for e in entities]

    return {
        "count": len(entities),
        "min_lag": min(lags),
        "max_lag": max(lags),
        "avg_lag": sum(lags) / len(lags),
        "median_lag": sorted(lags)[len(lags) // 2],
        "total_energy": sum(energies),
        "avg_energy": sum(energies) / len(energies)
    }

# ============================================================================
# HUD
# ============================================================================

def draw_hud(screen, font, tick, pattern_name, stats, mode, show_lag_values):
    """Draw HUD with information"""
    y_offset = 10
    line_height = 22

    lines = [
        f"Experiment 44_04: Multi-Entity Temporal Depth",
        f"Tick: {tick}",
        f"Pattern: {pattern_name} ({stats['count']} entities)",
        f"Mode: {mode}",
        "",
        f"Depth Stats:",
        f"  Min lag: {stats.get('min_lag', 0):.1f}",
        f"  Max lag: {stats.get('max_lag', 0):.1f}",
        f"  Avg lag: {stats.get('avg_lag', 0):.1f}",
        f"  Avg energy: {stats.get('avg_energy', 0):.0f}",
        "",
        "Controls:",
        "  1-4: Switch pattern (grid/random/shells/wave)",
        "  W: Forward force (reduce lag) - should FAIL",
        "  S: Backward force (increase lag) - should WORK",
        "  Q/A: Rotate in XY plane - unrestricted",
        "  Space: Reset pattern",
        "  L: Toggle lag values",
        "  P: Pause",
        "  +/-: Adjust entity count",
    ]

    for i, line in enumerate(lines):
        color = (200, 200, 200) if line and not line.startswith(" ") else (150, 150, 150)
        img = font.render(line, True, color)
        screen.blit(img, (10, y_offset + i * line_height))

    # Draw depth legend
    legend_x = WIDTH - 200
    legend_y = HEIGHT - 100

    legend_font = pygame.font.SysFont('monospace', 12)
    title = legend_font.render("Temporal Depth:", True, (200, 200, 200))
    screen.blit(title, (legend_x, legend_y))

    # Gradient bar
    gradient_width = 150
    gradient_height = 15
    gradient_y = legend_y + 20

    for i in range(gradient_width):
        factor = i / gradient_width
        gray = int(255 * (1 - factor * 0.7))
        pygame.draw.line(screen, (gray, gray, 255),
                        (legend_x + i, gradient_y),
                        (legend_x + i, gradient_y + gradient_height))

    near_text = legend_font.render("Near (lag=0)", True, (200, 200, 255))
    far_text = legend_font.render(f"Far (lag={MAX_Z_DISPLAY})", True, (100, 100, 200))
    screen.blit(near_text, (legend_x, gradient_y + gradient_height + 5))
    screen.blit(far_text, (legend_x + 60, gradient_y + gradient_height + 22))

# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Experiment 44_04: Multi-Entity Temporal Depth")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 14)

    # State
    tick = 0
    pattern_name = INITIAL_PATTERN
    entity_count = ENTITY_COUNT  # Use local variable
    entities = PATTERNS[pattern_name](entity_count)
    logger = ExperimentLogger()

    mode = "Ready"
    show_lag_values = False
    paused = False

    # Statistics for experiment
    force_attempts = {
        "forward": {"success": 0, "failure": 0},
        "backward": {"success": 0, "failure": 0},
        "rotate": {"success": 0, "failure": 0}
    }

    logger.log_pattern_change(tick, pattern_name, len(entities))

    running = True
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Reset pattern
                    entities = PATTERNS[pattern_name](entity_count)
                    mode = "Reset"
                    logger.log_pattern_change(tick, pattern_name, len(entities))

                elif event.key == pygame.K_1:
                    pattern_name = "grid"
                    entities = PATTERNS[pattern_name](entity_count)
                    mode = f"Pattern: {pattern_name}"
                    logger.log_pattern_change(tick, pattern_name, len(entities))

                elif event.key == pygame.K_2:
                    pattern_name = "random"
                    entities = PATTERNS[pattern_name](entity_count)
                    mode = f"Pattern: {pattern_name}"
                    logger.log_pattern_change(tick, pattern_name, len(entities))

                elif event.key == pygame.K_3:
                    pattern_name = "shells"
                    entities = PATTERNS[pattern_name](entity_count)
                    mode = f"Pattern: {pattern_name}"
                    logger.log_pattern_change(tick, pattern_name, len(entities))

                elif event.key == pygame.K_4:
                    pattern_name = "wave"
                    entities = PATTERNS[pattern_name](entity_count)
                    mode = f"Pattern: {pattern_name}"
                    logger.log_pattern_change(tick, pattern_name, len(entities))

                elif event.key == pygame.K_w:
                    # Forward force: try to reduce lag for all entities
                    avg_lag_before = sum(e.z for e in entities) / len(entities)
                    successes = sum(1 for e in entities if e.decrease_lag(5))
                    failures = len(entities) - successes
                    avg_lag_after = sum(e.z for e in entities) / len(entities)

                    force_attempts["forward"]["success"] += successes
                    force_attempts["forward"]["failure"] += failures

                    success_rate = successes / len(entities) * 100
                    mode = f"Forward force: {success_rate:.1f}% success (SHOULD FAIL)"
                    logger.log_force_attempt("forward", tick, successes, failures,
                                           avg_lag_before, avg_lag_after)

                elif event.key == pygame.K_s:
                    # Backward force: try to increase lag for all entities
                    avg_lag_before = sum(e.z for e in entities) / len(entities)
                    successes = sum(1 for e in entities if e.increase_lag(5))
                    failures = len(entities) - successes
                    avg_lag_after = sum(e.z for e in entities) / len(entities)

                    force_attempts["backward"]["success"] += successes
                    force_attempts["backward"]["failure"] += failures

                    success_rate = successes / len(entities) * 100
                    mode = f"Backward force: {success_rate:.1f}% success (SHOULD WORK)"
                    logger.log_force_attempt("backward", tick, successes, failures,
                                           avg_lag_before, avg_lag_after)

                elif event.key == pygame.K_q or event.key == pygame.K_a:
                    # Rotate in XY plane (should be unrestricted)
                    angle = 0.1 if event.key == pygame.K_q else -0.1
                    cx = sum(e.x for e in entities) / len(entities)
                    cy = sum(e.y for e in entities) / len(entities)

                    for e in entities:
                        dx = e.x - cx
                        dy = e.y - cy
                        new_dx = dx * math.cos(angle) - dy * math.sin(angle)
                        new_dy = dx * math.sin(angle) + dy * math.cos(angle)
                        e.x = cx + new_dx
                        e.y = cy + new_dy

                    force_attempts["rotate"]["success"] += len(entities)
                    mode = "Z-rotation (2D plane) - unrestricted"

                elif event.key == pygame.K_l:
                    show_lag_values = not show_lag_values
                    mode = f"Lag values: {'ON' if show_lag_values else 'OFF'}"

                elif event.key == pygame.K_p:
                    paused = not paused
                    mode = "Paused" if paused else "Running"

                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    # Increase entity count
                    entity_count = min(2000, len(entities) + 50)
                    entities = PATTERNS[pattern_name](entity_count)
                    mode = f"Entity count: {len(entities)}"
                    logger.log_pattern_change(tick, pattern_name, len(entities))

                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    # Decrease entity count
                    entity_count = max(10, len(entities) - 50)
                    entities = PATTERNS[pattern_name](entity_count)
                    mode = f"Entity count: {len(entities)}"
                    logger.log_pattern_change(tick, pattern_name, len(entities))

        # Update
        if not paused:
            tick += 1

            # Update wave pattern entities
            if pattern_name == "wave" and hasattr(entities[0], 'wave_phase'):
                for e in entities:
                    # Oscillate z based on wave phase
                    e.z = max(0, 20 + 15 * math.sin(tick * 0.05 + e.wave_phase))

            # Update all entities
            for entity in entities:
                entity.update(tick)

        # Render
        screen.fill((0, 0, 0))

        # Draw camera center point
        pygame.draw.circle(screen, (50, 50, 50), (CAMERA_X, CAMERA_Y), 3)

        # Draw entities with SIMPLIFIED rendering
        render_entities(screen, entities, show_lag_values)

        # Draw HUD
        stats = get_depth_stats(entities)
        draw_hud(screen, font, tick, pattern_name, stats, mode, show_lag_values)

        pygame.display.flip()
        clock.tick(FPS)

    # Save log and print results
    logger.save()

    print("\n" + "="*60)
    print("EXPERIMENT 44_04 RESULTS")
    print("="*60)
    print(f"\nTotal ticks: {tick}")
    print(f"\nForce Attempts:")

    for direction, stats in force_attempts.items():
        total = stats["success"] + stats["failure"]
        if total > 0:
            success_rate = stats["success"] / total * 100
            print(f"\n{direction.capitalize()}:")
            print(f"  Successes: {stats['success']}")
            print(f"  Failures: {stats['failure']}")
            print(f"  Success rate: {success_rate:.2f}%")

    # Calculate asymmetry
    fwd_total = force_attempts["forward"]["success"] + force_attempts["forward"]["failure"]
    bwd_total = force_attempts["backward"]["success"] + force_attempts["backward"]["failure"]

    if fwd_total > 0 and bwd_total > 0:
        fwd_rate = force_attempts["forward"]["success"] / fwd_total
        bwd_rate = force_attempts["backward"]["success"] / bwd_total

        if fwd_rate > 0:
            ratio = bwd_rate / fwd_rate
            print(f"\nAsymmetry ratio (backward/forward): {ratio:.2f}x")
        else:
            print(f"\nAsymmetry ratio: ∞ (forward: 0%, backward: {bwd_rate*100:.1f}%)")

        if bwd_rate > fwd_rate:
            print("\n✓ HYPOTHESIS SUPPORTED: Backward > Forward")
        else:
            print("\n✗ HYPOTHESIS REJECTED: No asymmetry")

    print("="*60)
    pygame.quit()


if __name__ == "__main__":
    main()
