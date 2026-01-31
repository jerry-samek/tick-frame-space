"""
Projectile - Moving pattern for collision experiments.

A projectile is a pattern that moves across the grid toward the target cloud.
Unlike the cloud patterns (which evolve via CA), projectiles are explicitly
moved each tick to maintain their velocity.
"""

import math
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass
import sys
from pathlib import Path

v6_path = Path(__file__).parent.parent / "v6"
sys.path.insert(0, str(v6_path))

from planck_grid import PlanckGrid
from pattern_library import PatternLibrary
from sample_cell import SampleCell, PatternInstance


@dataclass
class ProjectileState:
    """Current state of a projectile."""
    x: float  # Current x position (can be fractional)
    y: float  # Current y position
    vx: float  # Velocity x component (cells/tick)
    vy: float  # Velocity y component
    active: bool  # Is projectile still active?
    tick_created: int  # When was it created
    tick_impact: Optional[int]  # When did it hit the cloud (if any)
    gamma_k: float = 0.0  # Gamma well strength (0 = no well)

    @property
    def speed(self) -> float:
        return math.sqrt(self.vx * self.vx + self.vy * self.vy)

    @property
    def r(self) -> float:
        """Distance from origin."""
        return math.sqrt(self.x * self.x + self.y * self.y)


class Projectile:
    """A moving pattern that can collide with the target cloud."""

    def __init__(
        self,
        grid: PlanckGrid,
        library: PatternLibrary,
        pattern_name: str = "monopole",
        start_x: float = 0.0,
        start_y: float = 0.0,
        velocity_x: float = 0.0,
        velocity_y: float = 0.0,
        tick_created: int = 0,
        gamma_k: float = 0.0
    ):
        """
        Create a projectile.

        Args:
            grid: The Planck grid
            library: Pattern library
            pattern_name: Name of pattern to use
            start_x, start_y: Starting position (grid center = 0,0)
            velocity_x, velocity_y: Velocity components (cells/tick)
            tick_created: Tick when projectile was created
            gamma_k: Gamma well strength (0 = no well)
        """
        self.grid = grid
        self.library = library
        self.pattern_name = pattern_name
        self.pattern_size = library.pattern_size

        # Convert from center-relative to grid coordinates
        self.center_x = grid.width // 2
        self.center_y = grid.height // 2

        self.state = ProjectileState(
            x=start_x,
            y=start_y,
            vx=velocity_x,
            vy=velocity_y,
            active=True,
            tick_created=tick_created,
            tick_impact=None,
            gamma_k=gamma_k
        )

        # Track previous grid position for clearing
        self._prev_grid_x: Optional[int] = None
        self._prev_grid_y: Optional[int] = None

    @classmethod
    def create_toward_center(
        cls,
        grid: PlanckGrid,
        library: PatternLibrary,
        pattern_name: str = "monopole",
        start_radius: float = 40.0,
        approach_angle: float = 0.0,
        speed: float = 0.5,
        impact_parameter: float = 0.0,
        tick_created: int = 0,
        gamma_k: float = 0.0
    ) -> "Projectile":
        """
        Create a projectile aimed toward the grid center.

        Args:
            grid: The Planck grid
            library: Pattern library
            pattern_name: Pattern type
            start_radius: Distance from center to start
            approach_angle: Angle of approach (0 = from right, pi/2 = from top)
            speed: Speed in cells/tick
            impact_parameter: Perpendicular offset from center line
            tick_created: When created
            gamma_k: Gamma well strength (0 = no well)

        Returns:
            Configured projectile
        """
        # Starting position: at radius, at given angle
        start_x = start_radius * math.cos(approach_angle)
        start_y = start_radius * math.sin(approach_angle)

        # Apply impact parameter (perpendicular to approach direction)
        perp_angle = approach_angle + math.pi / 2
        start_x += impact_parameter * math.cos(perp_angle)
        start_y += impact_parameter * math.sin(perp_angle)

        # Velocity: toward center (opposite of position direction)
        # But offset by impact parameter to aim at (0, b) instead of (0, 0)
        target_x = impact_parameter * math.cos(perp_angle)
        target_y = impact_parameter * math.sin(perp_angle)

        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            vx = speed * dx / dist
            vy = speed * dy / dist
        else:
            vx = -speed * math.cos(approach_angle)
            vy = -speed * math.sin(approach_angle)

        return cls(
            grid=grid,
            library=library,
            pattern_name=pattern_name,
            start_x=start_x,
            start_y=start_y,
            velocity_x=vx,
            velocity_y=vy,
            tick_created=tick_created,
            gamma_k=gamma_k
        )

    def _grid_coords(self) -> Tuple[int, int]:
        """Convert current position to grid coordinates (top-left of pattern)."""
        gx = int(round(self.center_x + self.state.x - self.pattern_size // 2))
        gy = int(round(self.center_y + self.state.y - self.pattern_size // 2))
        return gx, gy

    def get_gamma_well_position(self) -> Tuple[float, float]:
        """
        Get the position for the gamma well (grid coordinates, center of projectile).

        Returns:
            (x, y) position in grid coordinates
        """
        return (self.center_x + self.state.x, self.center_y + self.state.y)

    def _is_on_grid(self, gx: int, gy: int) -> bool:
        """Check if pattern fits on grid at given position."""
        return (
            0 <= gx < self.grid.width - self.pattern_size and
            0 <= gy < self.grid.height - self.pattern_size
        )

    def write_to_grid(self):
        """Write projectile pattern to current grid position."""
        gx, gy = self._grid_coords()

        if not self._is_on_grid(gx, gy):
            return

        pattern = self.library.get_pattern(self.pattern_name)
        if pattern is not None:
            self.grid.write_region(gx, gy, pattern)

        self._prev_grid_x = gx
        self._prev_grid_y = gy

    def clear_from_grid(self):
        """Clear projectile from previous grid position."""
        if self._prev_grid_x is None or self._prev_grid_y is None:
            return

        gx, gy = self._prev_grid_x, self._prev_grid_y

        if not self._is_on_grid(gx, gy):
            return

        # Write zeros to clear
        zeros = np.zeros((self.pattern_size, self.pattern_size), dtype=np.int8)
        self.grid.write_region(gx, gy, zeros)

    def update(self, tick: int) -> bool:
        """
        Update projectile position for one tick.

        Args:
            tick: Current tick number

        Returns:
            True if projectile is still active
        """
        if not self.state.active:
            return False

        # Clear from previous position
        self.clear_from_grid()

        # Update position
        self.state.x += self.state.vx
        self.state.y += self.state.vy

        # Check if off grid
        gx, gy = self._grid_coords()
        if not self._is_on_grid(gx, gy):
            self.state.active = False
            return False

        # Check if reached center region (impact)
        if self.state.r < 2.0 and self.state.tick_impact is None:
            self.state.tick_impact = tick

        # Write to new position
        self.write_to_grid()

        return True

    def get_local_energy(self, radius: int = 7) -> float:
        """Get field energy around projectile's current position."""
        gx, gy = self._grid_coords()
        cx = gx + self.pattern_size // 2
        cy = gy + self.pattern_size // 2

        total = 0.0
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = cx + dx
                y = cy + dy
                if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                    total += abs(self.grid.get_cell(x, y))

        return total


if __name__ == "__main__":
    # Demo
    print("Projectile Demo")
    print("=" * 50)

    grid = PlanckGrid(100, 100)
    library = PatternLibrary(pattern_size=5)

    # Create projectile from right, heading toward center
    proj = Projectile.create_toward_center(
        grid=grid,
        library=library,
        pattern_name="monopole",
        start_radius=40.0,
        approach_angle=0.0,  # From right
        speed=0.5,
        impact_parameter=0.0,
        tick_created=0
    )

    print(f"Initial position: ({proj.state.x:.1f}, {proj.state.y:.1f})")
    print(f"Velocity: ({proj.state.vx:.3f}, {proj.state.vy:.3f})")
    print(f"Speed: {proj.state.speed:.3f} cells/tick")
    print()

    # Simulate a few ticks
    for tick in range(10):
        proj.update(tick)
        print(f"Tick {tick}: r={proj.state.r:.1f}, pos=({proj.state.x:.1f}, {proj.state.y:.1f})")

    print()
    print(f"Time to reach center: ~{40.0 / 0.5:.0f} ticks")
