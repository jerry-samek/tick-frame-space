#!/usr/bin/env python3
"""
Entity Motion Module for Experiment 51i (V9)

Implements moving entities with proper time tracking and trajectory generation.
"""

from dataclasses import dataclass, field
from typing import Tuple, List
import numpy as np
import math


# ============================================================================
# Physics Utilities
# ============================================================================

def lorentz_gamma(velocity: Tuple[float, float], c: float = 1.0) -> float:
    """
    Compute Lorentz gamma factor for given velocity.

    gamma = 1 / sqrt(1 - v^2/c^2)

    Args:
        velocity: (vx, vy) in units of c
        c: Speed of light (default 1.0)

    Returns:
        Lorentz gamma factor (>= 1.0)
    """
    vx, vy = velocity
    v_squared = vx**2 + vy**2
    v_over_c_squared = v_squared / (c**2)

    # Clamp to avoid numerical issues near v = c
    if v_over_c_squared >= 0.9999:
        v_over_c_squared = 0.9999

    gamma = 1.0 / math.sqrt(1.0 - v_over_c_squared)
    return gamma


def velocity_magnitude(velocity: Tuple[float, float]) -> float:
    """Compute magnitude of velocity vector."""
    vx, vy = velocity
    return math.sqrt(vx**2 + vy**2)


def normalize_velocity(velocity: Tuple[float, float], target_speed: float) -> Tuple[float, float]:
    """
    Normalize velocity vector to target speed.

    Args:
        velocity: (vx, vy)
        target_speed: Desired speed magnitude

    Returns:
        (vx_new, vy_new) with magnitude = target_speed
    """
    vx, vy = velocity
    current_speed = math.sqrt(vx**2 + vy**2)

    if current_speed < 1e-10:
        return (target_speed, 0.0)

    scale = target_speed / current_speed
    return (vx * scale, vy * scale)


# ============================================================================
# Moving Entity Class
# ============================================================================

@dataclass
class MovingEntity:
    """
    Entity that moves through space and experiences time dilation.

    Tracks both coordinate time (substrate ticks) and proper time (experienced ticks).
    """
    # Identity
    entity_id: str

    # Spatial state
    position: np.ndarray  # (x, y) position
    velocity: np.ndarray  # (vx, vy) velocity in units of c

    # Physical properties
    tick_budget: int = 1  # Computational cost (mass analog)
    energy: float = 10.0  # Internal energy state

    # Time tracking
    proper_time: float = 0.0  # tau_proper (experienced ticks)
    coordinate_time: int = 0  # t_coordinate (substrate ticks elapsed)

    # Statistics
    gamma_grav_history: List[float] = field(default_factory=list)
    gamma_SR_history: List[float] = field(default_factory=list)
    gamma_total_history: List[float] = field(default_factory=list)
    position_history: List[Tuple[float, float]] = field(default_factory=list)

    # Internal state
    _c: float = 1.0  # Speed of light
    _active: bool = True  # Whether entity participates in simulation

    def __post_init__(self):
        """Ensure arrays are numpy arrays."""
        if not isinstance(self.position, np.ndarray):
            self.position = np.array(self.position, dtype=float)
        if not isinstance(self.velocity, np.ndarray):
            self.velocity = np.array(self.velocity, dtype=float)

    @property
    def speed(self) -> float:
        """Current speed (magnitude of velocity)."""
        return float(np.linalg.norm(self.velocity))

    @property
    def gamma_SR(self) -> float:
        """Special relativistic Lorentz factor from velocity."""
        return lorentz_gamma(tuple(self.velocity), self._c)

    @property
    def gamma_eff_measured(self) -> float:
        """
        Measured effective time dilation factor.

        gamma_eff = t_coordinate / tau_proper

        If gamma_eff > 1.0, entity experiences time dilation.
        """
        if self.proper_time < 1e-10:
            return 1.0
        return self.coordinate_time / self.proper_time

    def update_time(
        self,
        gamma_grav: float,
        dt_substrate: float = 1.0
    ) -> float:
        """
        Update entity's time state given gravitational time dilation.

        Args:
            gamma_grav: Gravitational time dilation factor at current position
            dt_substrate: Substrate time step (default 1 tick)

        Returns:
            d_tau: Proper time increment experienced by entity
        """
        # Combined time dilation
        gamma_total = gamma_grav * self.gamma_SR

        # Proper time increment
        d_tau = dt_substrate / gamma_total

        # Update proper time
        self.proper_time += d_tau

        # Update coordinate time
        self.coordinate_time += int(dt_substrate)

        # Record history
        self.gamma_grav_history.append(gamma_grav)
        self.gamma_SR_history.append(self.gamma_SR)
        self.gamma_total_history.append(gamma_total)

        return d_tau

    def update_position(
        self,
        dt: float = 1.0,
        grid_size: int = 100,
        wrap_boundaries: bool = True
    ):
        """
        Update position based on velocity.

        Args:
            dt: Time step
            grid_size: Size of grid (for boundary handling)
            wrap_boundaries: If True, wrap around boundaries (periodic)
        """
        # Update position
        self.position += self.velocity * dt

        # Handle boundaries
        if wrap_boundaries:
            self.position = np.mod(self.position, grid_size)
        else:
            # Reflect at boundaries
            for i in range(2):
                if self.position[i] < 0:
                    self.position[i] = -self.position[i]
                    self.velocity[i] = -self.velocity[i]
                elif self.position[i] >= grid_size:
                    self.position[i] = 2 * grid_size - self.position[i]
                    self.velocity[i] = -self.velocity[i]

        # Record position
        self.position_history.append(tuple(self.position))

    def field_contribution(
        self,
        position_grid: Tuple[int, int],
        E_max: float = 15.0
    ) -> float:
        """
        Compute this entity's contribution to load field at given grid position.

        contribution = mass_factor × energy_factor × velocity_factor

        Args:
            position_grid: (ix, iy) grid coordinates
            E_max: Maximum energy for normalization

        Returns:
            Load contribution value
        """
        # Check if entity is at this position
        ix_entity = int(self.position[0])
        iy_entity = int(self.position[1])

        if (ix_entity, iy_entity) != position_grid:
            return 0.0

        # Mass factor (tick budget)
        mass_factor = float(self.tick_budget)

        # Energy factor (normalized)
        energy_factor = self.energy / E_max

        # Velocity factor (Lorentz contraction of field)
        velocity_factor = 1.0 / self.gamma_SR

        return mass_factor * energy_factor * velocity_factor

    def get_state_summary(self) -> dict:
        """Return dictionary summary of entity state."""
        return {
            'id': self.entity_id,
            'position': tuple(self.position),
            'velocity': tuple(self.velocity),
            'speed': self.speed,
            'gamma_SR': self.gamma_SR,
            'proper_time': self.proper_time,
            'coordinate_time': self.coordinate_time,
            'gamma_eff_measured': self.gamma_eff_measured,
            'energy': self.energy,
            'active': self._active
        }


# ============================================================================
# Stationary Entity (for planet cluster)
# ============================================================================

@dataclass
class StationaryEntity:
    """
    Entity that doesn't move (part of planet cluster).

    Simpler than MovingEntity - only contributes to field.
    """
    entity_id: str
    position: np.ndarray
    tick_budget: int = 1
    energy: float = 10.0

    def __post_init__(self):
        if not isinstance(self.position, np.ndarray):
            self.position = np.array(self.position, dtype=float)

    def field_contribution(
        self,
        position_grid: Tuple[int, int],
        E_max: float = 15.0
    ) -> float:
        """Compute contribution to load field."""
        ix_entity = int(self.position[0])
        iy_entity = int(self.position[1])

        if (ix_entity, iy_entity) != position_grid:
            return 0.0

        mass_factor = float(self.tick_budget)
        energy_factor = self.energy / E_max
        # Stationary: no velocity factor (gamma_SR = 1.0)

        return mass_factor * energy_factor


# ============================================================================
# Trajectory Generators
# ============================================================================

def generate_circular_orbit(
    center: Tuple[float, float],
    radius: float,
    angular_velocity: float,
    initial_angle: float = 0.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate initial position and velocity for circular orbit.

    Args:
        center: (cx, cy) center of orbit
        radius: Orbital radius
        angular_velocity: Angular velocity in radians per tick
        initial_angle: Starting angle in radians (default 0)

    Returns:
        (position, velocity) as numpy arrays
    """
    cx, cy = center

    # Initial position on circle
    x = cx + radius * math.cos(initial_angle)
    y = cy + radius * math.sin(initial_angle)
    position = np.array([x, y])

    # Tangential velocity (perpendicular to radius)
    vx = -radius * angular_velocity * math.sin(initial_angle)
    vy = radius * angular_velocity * math.cos(initial_angle)
    velocity = np.array([vx, vy])

    return position, velocity


def generate_planet_cluster(
    center: Tuple[float, float],
    radius: float,
    count: int,
    tick_budget: int = 1,
    energy: float = 10.0
) -> List[StationaryEntity]:
    """
    Generate cluster of stationary entities (planet).

    Entities are randomly distributed within radius of center.

    Args:
        center: (cx, cy) center of cluster
        radius: Maximum radius of cluster
        count: Number of entities
        tick_budget: tick_budget for each entity
        energy: Initial energy for each entity

    Returns:
        List of StationaryEntity instances
    """
    entities = []
    cx, cy = center

    for i in range(count):
        # Random position within radius (uniform in disk)
        r = radius * math.sqrt(np.random.random())
        theta = 2 * math.pi * np.random.random()

        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)

        entity = StationaryEntity(
            entity_id=f"planet_{i}",
            position=np.array([x, y]),
            tick_budget=tick_budget,
            energy=energy
        )
        entities.append(entity)

    return entities


def generate_mobile_entities(
    center: Tuple[float, float],
    distances: List[float],
    velocities_per_distance: List[float],
    count_per_velocity: int,
    c: float = 1.0
) -> List[MovingEntity]:
    """
    Generate mobile entities on circular orbits at various velocities.

    Args:
        center: (cx, cy) center of orbits
        distances: List of orbital radii
        velocities_per_distance: List of speeds (in units of c)
        count_per_velocity: Number of entities per (distance, velocity) combination
        c: Speed of light

    Returns:
        List of MovingEntity instances
    """
    entities = []
    entity_counter = 0

    for distance in distances:
        for velocity_magnitude in velocities_per_distance:
            # Angular velocity to achieve desired speed
            # v = r * omega => omega = v / r
            angular_velocity = velocity_magnitude * c / distance

            for i in range(count_per_velocity):
                # Spread entities around orbit
                initial_angle = 2 * math.pi * i / count_per_velocity

                position, velocity = generate_circular_orbit(
                    center=center,
                    radius=distance,
                    angular_velocity=angular_velocity,
                    initial_angle=initial_angle
                )

                entity = MovingEntity(
                    entity_id=f"mobile_{entity_counter}",
                    position=position,
                    velocity=velocity,
                    tick_budget=1,
                    energy=10.0,
                    _c=c
                )
                entity_counter += 1
                entities.append(entity)

    return entities


# ============================================================================
# Utility Functions
# ============================================================================

def distance_to_point(
    entity_position: np.ndarray,
    point: Tuple[float, float]
) -> float:
    """
    Compute Euclidean distance from entity to point.

    Args:
        entity_position: Entity position array
        point: (x, y) point

    Returns:
        Distance
    """
    dx = entity_position[0] - point[0]
    dy = entity_position[1] - point[1]
    return math.sqrt(dx**2 + dy**2)


def compute_trajectory_stats(entity: MovingEntity) -> dict:
    """
    Compute statistics about entity's trajectory.

    Returns dictionary with:
    - min_distance: Minimum distance to planet center
    - max_distance: Maximum distance
    - avg_distance: Average distance
    - orbit_period_estimate: Estimated orbital period (if circular)
    """
    if len(entity.position_history) < 2:
        return {}

    positions = np.array(entity.position_history)

    # Assume planet at (50, 50) - TODO: pass as parameter
    center = np.array([50.0, 50.0])
    distances = np.linalg.norm(positions - center, axis=1)

    stats = {
        'min_distance': float(np.min(distances)),
        'max_distance': float(np.max(distances)),
        'avg_distance': float(np.mean(distances)),
        'distance_std': float(np.std(distances))
    }

    return stats


if __name__ == "__main__":
    # Demo: Create entities and test motion
    print("=" * 70)
    print("ENTITY MOTION MODULE - DEMO")
    print("=" * 70)
    print()

    # Create a planet cluster
    print("Creating planet cluster...")
    planet = generate_planet_cluster(
        center=(50.0, 50.0),
        radius=10.0,
        count=100,
        tick_budget=1
    )
    print(f"  Created {len(planet)} stationary entities")
    print()

    # Create mobile entities
    print("Creating mobile entities...")
    mobile = generate_mobile_entities(
        center=(50.0, 50.0),
        distances=[20.0, 30.0],
        velocities_per_distance=[0.1, 0.5, 0.9],
        count_per_velocity=2,
        c=1.0
    )
    print(f"  Created {len(mobile)} mobile entities")
    print()

    # Test one entity
    entity = mobile[0]
    print(f"Testing entity: {entity.entity_id}")
    print(f"  Initial position: {entity.position}")
    print(f"  Initial velocity: {entity.velocity}")
    print(f"  Speed: {entity.speed:.3f}c")
    print(f"  Lorentz gamma: {entity.gamma_SR:.3f}")
    print()

    # Simulate a few timesteps
    print("Simulating 10 timesteps...")
    for tick in range(10):
        # Assume uniform gravitational field (gamma_grav = 1.1) for demo
        gamma_grav = 1.1
        entity.update_time(gamma_grav, dt_substrate=1.0)
        entity.update_position(dt=1.0, grid_size=100)

        if tick % 3 == 0:
            print(f"  Tick {tick}: pos={entity.position}, tau={entity.proper_time:.2f}")

    print()
    print(f"Final proper time: {entity.proper_time:.3f}")
    print(f"Final coordinate time: {entity.coordinate_time}")
    print(f"Measured gamma_eff: {entity.gamma_eff_measured:.3f}")
    print()
