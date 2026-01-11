"""
Experiment 44_03: Emergent 3D Rotation from 2D+Temporal Entities

Tests whether individual entities in 2D space can create patterns that appear
as 3D rotation when visualized with temporal depth buffer.

Key constraint: Entities can only slow down (increase temporal lag), never speed up.
"""

import json
import math
from datetime import datetime
from pathlib import Path

import pygame

# ============================================================================
# CONFIGURATION
# ============================================================================

WIDTH, HEIGHT = 1200, 800
MAX_HISTORY = 60  # Temporal buffer depth
FPS = 30

# Energy and movement parameters
ENERGY_INCREMENT = 1  # Energy gained per tick
MOVEMENT_COST = 10     # Energy cost to move 1 unit
LAG_COST = 5          # Energy cost to increase lag by 1 tick

# Triangle geometry (in 2D space)
TRIANGLE_SIZE = 150
TRIANGLE_CENTER = [WIDTH // 2, HEIGHT // 2]

# Visualization
VANISHING_POINT = [WIDTH // 2, HEIGHT // 2]
DEPTH_SCALE = 0.98  # Scale reduction per tick of lag

# Logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ============================================================================
# EXPERIMENT LOGGER
# ============================================================================

class ExperimentLogger:
    """Logs all experiment interactions to a JSON file"""

    def __init__(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = LOG_DIR / f"experiment_{timestamp}.json"
        self.events = []
        self.session_start = datetime.now().isoformat()

    def log_event(self, event_type, data):
        """Log an event with timestamp"""
        event = {
            "tick": data.get("tick", 0),
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.events.append(event)

    def log_rotation_attempt(self, direction, tick, success, entities_state):
        """Log a rotation attempt with full state"""
        self.log_event("rotation_attempt", {
            "tick": tick,
            "direction": direction,
            "success": success,
            "vertex_states": [
                {
                    "role": e.role,
                    "x": e.x,
                    "y": e.y,
                    "energy": e.energy,
                    "temporal_lag": e.temporal_lag
                }
                for e in entities_state if 'vertex' in e.role
            ]
        })

    def log_reset(self, tick):
        """Log a reset event"""
        self.log_event("reset", {"tick": tick})

    def log_phase_change(self, tick, phase):
        """Log phase change"""
        self.log_event("phase_change", {"tick": tick, "phase": phase})

    def save(self):
        """Save log to file"""
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
    Individual entity in 2D space with temporal lag.

    Attributes:
        x, y: Position in 2D space
        energy: Accumulated energy for movement
        temporal_lag: How many ticks behind 'present' this entity is
        color: RGB tuple for visualization
        birth_tick: When this entity was created
        role: 'vertex_0', 'vertex_1', 'vertex_2', or 'fill'
    """

    def __init__(self, x, y, color, role='fill', birth_tick=0):
        self.x = float(x)
        self.y = float(y)
        self.energy = 0
        self.temporal_lag = 0
        self.color = color
        self.role = role
        self.birth_tick = birth_tick
        self.target_x = x  # For pattern maintenance
        self.target_y = y

    def add_energy(self, amount=ENERGY_INCREMENT):
        """Entities gain energy each tick (surfing forward in time)"""
        self.energy += amount

    def move_to(self, target_x, target_y):
        """
        Attempt to move toward target position.
        Returns True if move succeeded, False if insufficient energy.
        """
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance < 1:
            return True  # Already at target

        cost = int(distance * MOVEMENT_COST)

        if self.energy >= cost:
            self.energy -= cost
            self.x = target_x
            self.y = target_y
            return True

        return False

    def increase_lag(self, lag_amount):
        """
        Increase temporal lag (fall behind in time).
        This creates apparent depth in visualization.
        Returns True if successful, False if insufficient energy.
        """
        cost = lag_amount * LAG_COST

        if self.energy >= cost:
            self.energy -= cost
            self.temporal_lag += lag_amount
            return True

        return False

    def decrease_lag(self, lag_amount):
        """
        Attempt to DECREASE temporal lag (catch up to present).

        THIS IS THE KEY CONSTRAINT:
        - Should be impossible or require infinite energy
        - Entities cannot speed up past 1 tick/tick
        - Can only reach lag=0, never negative
        """
        if self.temporal_lag <= 0:
            return False  # Already at present, cannot go to future

        # In theory, this should cost infinite energy or be impossible
        # For experiment, we'll make it cost 10x more than increasing lag
        cost = lag_amount * LAG_COST * 10

        if self.energy >= cost and self.temporal_lag >= lag_amount:
            self.energy -= cost
            self.temporal_lag -= lag_amount
            return True

        return False

    def clone(self):
        """Create a copy of this entity"""
        e = Entity(self.x, self.y, self.color, self.role, self.birth_tick)
        e.energy = self.energy
        e.temporal_lag = self.temporal_lag
        e.target_x = self.target_x
        e.target_y = self.target_y
        return e


# ============================================================================
# PATTERN MANAGEMENT
# ============================================================================

class TrianglePattern:
    """
    Manages emergent triangle pattern from individual entities.
    The pattern has no rigid structure - it's maintained through entity rules.
    """

    def __init__(self, center, size, tick=0):
        self.center = list(center)
        self.size = size
        self.entities = []
        self.tick = tick
        self.rotation_z = 0  # Rotation around temporal axis (2D rotation)
        self.rotation_x = 0  # Rotation around x-axis (pitch)
        self.initial_center = list(center)
        self.initial_size = size

        # Create initial vertex entities
        self._spawn_vertices(tick)

    def reset(self, tick):
        """Properly reset the pattern to initial state"""
        self.center = list(self.initial_center)
        self.size = self.initial_size
        self.entities = []
        self.tick = tick
        self.rotation_z = 0
        self.rotation_x = 0
        self._spawn_vertices(tick)

    def _spawn_vertices(self, tick):
        """Spawn three vertex entities to form triangle"""
        angles = [math.pi/2, math.pi/2 + 2*math.pi/3, math.pi/2 + 4*math.pi/3]
        colors = [(255, 50, 50), (50, 255, 50), (50, 50, 255)]

        for i, (angle, color) in enumerate(zip(angles, colors)):
            x = self.center[0] + self.size * math.cos(angle)
            y = self.center[1] + self.size * math.sin(angle)
            entity = Entity(x, y, color, role=f'vertex_{i}', birth_tick=tick)
            entity.target_x = x
            entity.target_y = y
            entity.energy = 1000  # Give vertices initial energy
            self.entities.append(entity)

    def get_centroid(self):
        """Calculate current centroid from vertex entities"""
        vertices = [e for e in self.entities if 'vertex' in e.role]
        if not vertices:
            return self.center
        cx = sum(e.x for e in vertices) / len(vertices)
        cy = sum(e.y for e in vertices) / len(vertices)
        return [cx, cy]

    def apply_2d_rotation(self, angle_delta):
        """
        Apply rotation in 2D plane (around temporal/z axis).
        This should work naturally - no temporal constraint.
        """
        self.rotation_z += angle_delta
        centroid = self.get_centroid()

        vertices = [e for e in self.entities if 'vertex' in e.role]

        for entity in vertices:
            # Rotate around centroid
            dx = entity.target_x - centroid[0]
            dy = entity.target_y - centroid[1]

            new_dx = dx * math.cos(angle_delta) - dy * math.sin(angle_delta)
            new_dy = dx * math.sin(angle_delta) + dy * math.cos(angle_delta)

            entity.target_x = centroid[0] + new_dx
            entity.target_y = centroid[1] + new_dy

    def apply_pitch_forward(self, angle_delta):
        """
        Attempt to pitch triangle FORWARD (toward viewer).

        This requires top vertex to REDUCE temporal lag (speed up).
        Should FAIL or require excessive energy.
        """
        self.rotation_x -= angle_delta

        vertices = [e for e in self.entities if 'vertex' in e.role]
        if len(vertices) < 3:
            return False

        # Top vertex needs to reduce lag (come closer in time)
        # Bottom vertices need to increase lag (go further in time)
        top = vertices[0]
        bottom_left = vertices[1]
        bottom_right = vertices[2]

        # Calculate required lag changes
        max_lag = abs(math.sin(self.rotation_x) * self.size / 10)

        # Try to reduce top vertex lag (THIS SHOULD FAIL)
        top_success = top.decrease_lag(int(max_lag))

        # Try to increase bottom vertices lag
        bottom_left.increase_lag(int(max_lag / 2))
        bottom_right.increase_lag(int(max_lag / 2))

        return top_success

    def apply_pitch_backward(self, angle_delta):
        """
        Attempt to pitch triangle BACKWARD (away from viewer).

        This requires top vertex to INCREASE temporal lag (slow down).
        Should SUCCEED with finite energy cost.
        """
        self.rotation_x += angle_delta

        vertices = [e for e in self.entities if 'vertex' in e.role]
        if len(vertices) < 3:
            return False

        # Top vertex needs to increase lag (go further in time)
        # Bottom vertices stay near present
        top = vertices[0]
        bottom_left = vertices[1]
        bottom_right = vertices[2]

        # Calculate required lag changes
        max_lag = abs(math.sin(self.rotation_x) * self.size / 10)

        # Increase top vertex lag (THIS SHOULD WORK)
        top_success = top.increase_lag(int(max_lag))

        # Optionally reduce bottom vertices lag slightly
        bottom_left.decrease_lag(int(max_lag / 4))
        bottom_right.decrease_lag(int(max_lag / 4))

        return top_success

    def update(self, tick):
        """Update all entities - they try to reach their target positions"""
        self.tick = tick

        for entity in self.entities:
            entity.add_energy()

            # Try to move toward target
            if 'vertex' in entity.role:
                # Gradual movement
                dx = entity.target_x - entity.x
                dy = entity.target_y - entity.y
                distance = math.sqrt(dx*dx + dy*dy)

                if distance > 1:
                    # Move small step
                    step = min(2, distance)
                    new_x = entity.x + (dx / distance) * step
                    new_y = entity.y + (dy / distance) * step
                    entity.move_to(new_x, new_y)


# ============================================================================
# VISUALIZATION
# ============================================================================

def project_with_temporal_depth(entity, tick):
    """
    Project entity position with perspective based on temporal lag.

    temporal_lag = how many ticks behind present
    Higher lag = appears further away (smaller, toward vanishing point)
    """
    if entity.temporal_lag < 0:
        entity.temporal_lag = 0

    depth_factor = min(entity.temporal_lag / MAX_HISTORY, 0.99)

    # Scale position toward vanishing point
    px = entity.x * (1 - depth_factor) + VANISHING_POINT[0] * depth_factor
    py = entity.y * (1 - depth_factor) + VANISHING_POINT[1] * depth_factor

    # Scale size with depth
    radius = max(2, int(8 * (1 - depth_factor)))

    # Fade color with depth
    age_factor = min(entity.temporal_lag / MAX_HISTORY, 1.0)
    r = int(entity.color[0] * (1 - age_factor * 0.7))
    g = int(entity.color[1] * (1 - age_factor * 0.7))
    b = int(entity.color[2] * (1 - age_factor * 0.7))

    return int(px), int(py), radius, (r, g, b)


def draw_entity(screen, entity, tick):
    """Draw single entity with temporal perspective"""
    px, py, radius, color = project_with_temporal_depth(entity, tick)
    pygame.draw.circle(screen, color, (px, py), radius)

    # Draw role indicator for vertices
    if 'vertex' in entity.role:
        pygame.draw.circle(screen, (255, 255, 255), (px, py), radius + 2, 1)


def draw_connections(screen, pattern, tick):
    """Draw lines connecting triangle vertices"""
    vertices = [e for e in pattern.entities if 'vertex' in e.role]
    if len(vertices) < 3:
        return

    points = []
    for v in vertices:
        px, py, _, _ = project_with_temporal_depth(v, tick)
        points.append((px, py))

    # Draw triangle edges
    pygame.draw.polygon(screen, (100, 100, 100), points, 2)


def draw_temporal_lag_visualization(screen, pattern, tick):
    """
    Visualize temporal lag gradient as colored overlay.
    Shows which vertices are "further in time" (higher lag).
    """
    vertices = [e for e in pattern.entities if 'vertex' in e.role]
    if len(vertices) < 3:
        return

    # Find min/max lag for normalization
    lags = [v.temporal_lag for v in vertices]
    min_lag = min(lags)
    max_lag = max(lags)
    lag_range = max(max_lag - min_lag, 1)

    # Draw lag indicators near each vertex
    for v in vertices:
        px, py, radius, color = project_with_temporal_depth(v, tick)

        # Normalize lag to 0-1
        normalized_lag = (v.temporal_lag - min_lag) / lag_range

        # Draw lag bar
        bar_width = 60
        bar_height = 8
        bar_x = px + 15
        bar_y = py - 20

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))

        # Filled portion based on lag
        filled_width = int(bar_width * normalized_lag)
        lag_color = (
            int(50 + 205 * normalized_lag),   # More lag = more red
            int(50 + 205 * (1 - normalized_lag)),  # Less lag = more green
            50
        )
        if filled_width > 0:
            pygame.draw.rect(screen, lag_color, (bar_x, bar_y, filled_width, bar_height))

        # Border
        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height), 1)

        # Lag value text
        lag_text = f"lag:{int(v.temporal_lag)}"
        font = pygame.font.SysFont('monospace', 12)
        text_surf = font.render(lag_text, True, (200, 200, 200))
        screen.blit(text_surf, (bar_x, bar_y - 15))


def draw_depth_gradient_overlay(screen, pattern):
    """
    Draw a visual representation of the temporal depth gradient.
    Shows how temporal lag creates apparent 3D depth.
    """
    # Draw legend in bottom-right
    legend_x = WIDTH - 220
    legend_y = HEIGHT - 120

    font = pygame.font.SysFont('monospace', 12)

    # Title
    title = font.render("Temporal Depth:", True, (200, 200, 200))
    screen.blit(title, (legend_x, legend_y))

    # Gradient bar
    gradient_width = 180
    gradient_height = 20
    gradient_y = legend_y + 25

    for i in range(gradient_width):
        factor = i / gradient_width
        color = (
            int(50 + 150 * factor),
            int(200 - 150 * factor),
            100
        )
        pygame.draw.line(screen, color, (legend_x + i, gradient_y), (legend_x + i, gradient_y + gradient_height))

    # Labels
    near_text = font.render("Near (lag=0)", True, (100, 255, 100))
    far_text = font.render(f"Far (lag={MAX_HISTORY})", True, (255, 100, 100))
    screen.blit(near_text, (legend_x, gradient_y + gradient_height + 5))
    screen.blit(far_text, (legend_x + gradient_width - 100, gradient_y + gradient_height + 5))


def draw_hud(screen, font, pattern, phase, mode):
    """Draw HUD with information"""
    y_offset = 10
    line_height = 25

    lines = [
        f"Tick: {pattern.tick}",
        f"Phase: {phase}",
        f"Mode: {mode}",
        f"Rotation Z (2D): {pattern.rotation_z:.2f} rad",
        f"Rotation X (pitch): {pattern.rotation_x:.2f} rad",
        "",
        "Controls:",
        "  Q/A: Z-rotation (2D rotation)",
        "  W: Pitch FORWARD (should fail)",
        "  S: Pitch BACKWARD (should work)",
        "  Space: Reset",
        "  Tab: Next phase",
        "  L: Toggle lag visualization",
        "  G: Toggle depth gradient",
        "  P: Pause",
        "",
    ]

    # Show vertex stats
    vertices = [e for e in pattern.entities if 'vertex' in e.role]
    for i, v in enumerate(vertices):
        lines.append(f"Vertex {i}: lag={int(v.temporal_lag)} energy={int(v.energy)}")

    for i, line in enumerate(lines):
        color = (200, 200, 200) if line else (100, 100, 100)
        img = font.render(line, True, color)
        screen.blit(img, (10, y_offset + i * line_height))


# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Experiment 44_03: Emergent 3D Rotation from 2D+Time")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 16)

    # Experiment state
    tick = 0
    phase = 1  # Current test phase
    mode = "Formation"
    pattern = TrianglePattern(TRIANGLE_CENTER, TRIANGLE_SIZE, tick)

    # Experiment log
    energy_log = []
    logger = ExperimentLogger()

    # Visualization toggles
    show_lag_vis = True
    show_depth_gradient = True

    running = True
    paused = False

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Reset - use proper reset method
                    pattern.reset(tick)
                    mode = "Reset"
                    logger.log_reset(tick)
                elif event.key == pygame.K_TAB:
                    # Next phase
                    phase = (phase % 5) + 1
                    mode = f"Phase {phase}"
                    logger.log_phase_change(tick, phase)
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_l:
                    # Toggle lag visualization
                    show_lag_vis = not show_lag_vis
                elif event.key == pygame.K_g:
                    # Toggle gradient overlay
                    show_depth_gradient = not show_depth_gradient
                elif event.key == pygame.K_q:
                    # Z-rotation clockwise (2D rotation)
                    pattern.apply_2d_rotation(0.1)
                    mode = "Z-Rotation CW (2D)"
                    logger.log_rotation_attempt("z_cw", tick, True, pattern.entities)
                elif event.key == pygame.K_a:
                    # Z-rotation counter-clockwise
                    pattern.apply_2d_rotation(-0.1)
                    mode = "Z-Rotation CCW (2D)"
                    logger.log_rotation_attempt("z_ccw", tick, True, pattern.entities)
                elif event.key == pygame.K_w:
                    # Pitch FORWARD (should fail)
                    success = pattern.apply_pitch_forward(0.1)
                    mode = f"Pitch FORWARD ({'success' if success else 'FAILED'})"
                    energy_log.append(('forward', tick, success))
                    logger.log_rotation_attempt("forward", tick, success, pattern.entities)
                elif event.key == pygame.K_s:
                    # Pitch BACKWARD (should succeed)
                    success = pattern.apply_pitch_backward(0.1)
                    mode = f"Pitch BACKWARD ({'success' if success else 'FAILED'})"
                    energy_log.append(('backward', tick, success))
                    logger.log_rotation_attempt("backward", tick, success, pattern.entities)

        if not paused:
            tick += 1
            pattern.update(tick)

        # Render
        screen.fill((0, 0, 0))

        # Draw vanishing point
        pygame.draw.circle(screen, (50, 50, 50), VANISHING_POINT, 5)

        # Draw pattern
        draw_connections(screen, pattern, tick)

        for entity in pattern.entities:
            draw_entity(screen, entity, tick)

        # Draw temporal lag visualization
        if show_lag_vis:
            draw_temporal_lag_visualization(screen, pattern, tick)

        # Draw depth gradient overlay
        if show_depth_gradient:
            draw_depth_gradient_overlay(screen, pattern)

        # Draw HUD
        draw_hud(screen, font, pattern, phase, mode)

        pygame.display.flip()
        clock.tick(FPS)

    # Save experiment log
    logger.save()

    # Print experiment results
    print("\n" + "="*60)
    print("EXPERIMENT 44_03 RESULTS")
    print("="*60)
    print(f"\nTotal ticks: {tick}")
    print(f"\nRotation attempts:")

    forward_attempts = [x for x in energy_log if x[0] == 'forward']
    backward_attempts = [x for x in energy_log if x[0] == 'backward']

    print(f"  Forward pitch attempts: {len(forward_attempts)}")
    print(f"    Successful: {sum(1 for x in forward_attempts if x[2])}")
    print(f"    Failed: {sum(1 for x in forward_attempts if not x[2])}")

    print(f"\n  Backward pitch attempts: {len(backward_attempts)}")
    print(f"    Successful: {sum(1 for x in backward_attempts if x[2])}")
    print(f"    Failed: {sum(1 for x in backward_attempts if not x[2])}")

    if forward_attempts and backward_attempts:
        forward_success_rate = sum(1 for x in forward_attempts if x[2]) / len(forward_attempts)
        backward_success_rate = sum(1 for x in backward_attempts if x[2]) / len(backward_attempts)

        print(f"\nSuccess rates:")
        print(f"  Forward: {forward_success_rate:.2%}")
        print(f"  Backward: {backward_success_rate:.2%}")
        print(f"  Ratio (backward/forward): {backward_success_rate / max(forward_success_rate, 0.001):.2f}x")

        if backward_success_rate > forward_success_rate:
            print("\n✓ HYPOTHESIS SUPPORTED: Asymmetry observed")
            print("  Backward rotation has higher success rate than forward")
        else:
            print("\n✗ HYPOTHESIS REJECTED: No significant asymmetry")

    print("="*60)

    pygame.quit()


if __name__ == "__main__":
    main()
