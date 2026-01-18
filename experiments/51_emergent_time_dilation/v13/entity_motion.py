#!/usr/bin/env python3
"""
Entity Motion Module for Experiment 53 (V10): Emergent Geodesics

KEY CHANGE FROM V9: Entities follow time-flow gradients instead of forced circular orbits.

This tests whether geodesic motion emerges naturally from following ∇γ_grav.
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
    Entity that moves through space following time-flow gradients.

    V10 CHANGE: Velocity updates via gradient following, not forced orbits.
    """
    # Identity
    entity_id: str

    # Spatial state
    position: np.ndarray  # (x, y) position
    velocity: np.ndarray  # (vx, vy) velocity in units of c

    # Physical properties
    tick_budget: int = 1
    energy: float = 10.0

    # Time tracking
    proper_time: float = 0.0
    coordinate_time: int = 0

    # Statistics
    gamma_grav_history: List[float] = field(default_factory=list)
    gamma_SR_history: List[float] = field(default_factory=list)
    gamma_total_history: List[float] = field(default_factory=list)
    position_history: List[Tuple[float, float]] = field(default_factory=list)
    velocity_history: List[Tuple[float, float]] = field(default_factory=list)
    acceleration_history: List[Tuple[float, float]] = field(default_factory=list)

    # Internal state
    _c: float = 1.0
    _active: bool = True

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
        """
        if self.proper_time < 1e-10:
            return 1.0
        return self.coordinate_time / self.proper_time

    def update_time(
        self,
        gamma_grav: float,
        dt_substrate: float = 1.0
    ) -> float:
        """Update entity's time state given gravitational time dilation."""
        gamma_total = gamma_grav * self.gamma_SR
        d_tau = dt_substrate / gamma_total

        self.proper_time += d_tau
        self.coordinate_time += int(dt_substrate)

        self.gamma_grav_history.append(gamma_grav)
        self.gamma_SR_history.append(self.gamma_SR)
        self.gamma_total_history.append(gamma_total)

        return d_tau

    def update_velocity_gradient_following(
        self,
        gamma_gradient: np.ndarray,
        dt: float = 1.0,
        coupling_constant: float = 0.01
    ):
        """
        V10 CORE PHYSICS: Update velocity by following time-flow gradient.

        Entities seek regions of higher γ_grav (faster proper time).
        This is the geodesic equation in disguise!

        Args:
            gamma_gradient: ∇γ_grav at current position (2D vector)
            dt: Time step
            coupling_constant: Strength of gradient coupling (tunable)
        """
        # Acceleration follows gradient
        # (Entities seek to maximize proper time rate)
        acceleration = coupling_constant * gamma_gradient

        # Update velocity
        self.velocity += acceleration * dt

        # Enforce speed limit c = 1.0
        speed = np.linalg.norm(self.velocity)
        if speed > self._c:
            self.velocity *= self._c / speed

        # Record acceleration history
        self.acceleration_history.append(tuple(acceleration))
        self.velocity_history.append(tuple(self.velocity))

    def update_position(
        self,
        dt: float = 1.0,
        grid_size: int = 100,
        wrap_boundaries: bool = True
    ):
        """Update position based on velocity."""
        self.position += self.velocity * dt

        # Handle boundaries
        if wrap_boundaries:
            self.position = np.mod(self.position, grid_size)
        else:
            for i in range(2):
                if self.position[i] < 0:
                    self.position[i] = -self.position[i]
                    self.velocity[i] = -self.velocity[i]
                elif self.position[i] >= grid_size:
                    self.position[i] = 2 * grid_size - self.position[i]
                    self.velocity[i] = -self.velocity[i]

        self.position_history.append(tuple(self.position))

    def field_contribution(
        self,
        position_grid: Tuple[int, int],
        E_max: float = 15.0
    ) -> float:
        """Compute this entity's contribution to load field."""
        ix_entity = int(self.position[0])
        iy_entity = int(self.position[1])

        if (ix_entity, iy_entity) != position_grid:
            return 0.0

        mass_factor = float(self.tick_budget)
        energy_factor = self.energy / E_max
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
    """Entity that doesn't move (part of planet cluster)."""
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

        return mass_factor * energy_factor


# ============================================================================
# Entity Generators - V10 VERSION
# ============================================================================

def generate_planet_cluster(
    center: Tuple[float, float],
    radius: float,
    count: int,
    tick_budget: int = 1,
    energy: float = 10.0
) -> List[StationaryEntity]:
    """
    Generate cluster of stationary entities (planet).

    Unchanged from v9.
    """
    entities = []
    cx, cy = center

    for i in range(count):
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


def generate_mobile_entities_random_velocities(
    center: Tuple[float, float],
    distances: List[float],
    velocities: List[float],
    count_per_config: int,
    c: float = 1.0,
    random_direction: bool = True
) -> List[MovingEntity]:
    """
    V10 VERSION: Generate mobile entities with random initial velocities.

    KEY DIFFERENCE FROM V9: No forced circular orbits!
    Entities start with random velocities and let physics determine motion.

    Args:
        center: (cx, cy) center point (planet location)
        distances: List of initial distances from center
        velocities: List of initial speed magnitudes (in units of c)
        count_per_config: Number of entities per (distance, velocity) combination
        c: Speed of light
        random_direction: If True, random direction; if False, tangential

    Returns:
        List of MovingEntity instances
    """
    entities = []
    entity_counter = 0
    cx, cy = center

    for distance in distances:
        for velocity_magnitude in velocities:
            for i in range(count_per_config):
                # Random position on circle at given distance
                angle = 2 * math.pi * np.random.random()
                x = cx + distance * math.cos(angle)
                y = cy + distance * math.sin(angle)
                position = np.array([x, y])

                # Generate velocity
                if random_direction:
                    # Completely random direction
                    vel_angle = 2 * math.pi * np.random.random()
                    vx = velocity_magnitude * c * math.cos(vel_angle)
                    vy = velocity_magnitude * c * math.sin(vel_angle)
                else:
                    # Tangential direction (like orbit, but won't be maintained)
                    vx = -velocity_magnitude * c * math.sin(angle)
                    vy = velocity_magnitude * c * math.cos(angle)

                velocity = np.array([vx, vy])

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
# Gradient Computation
# ============================================================================

def compute_gamma_gradient(
    position: np.ndarray,
    gamma_field: np.ndarray,
    grid_size: int = 100,
    dx: float = 1.0
) -> np.ndarray:
    """
    Compute gradient of gamma field at given position.

    Uses finite difference approximation:
    ∇γ ≈ (γ(x+dx) - γ(x-dx)) / (2*dx)

    Args:
        position: (x, y) position
        gamma_field: 2D array of gamma values
        grid_size: Size of grid
        dx: Grid spacing

    Returns:
        (grad_x, grad_y) gradient vector
    """
    x, y = position
    ix = int(x)
    iy = int(y)

    # Boundary handling
    ix = np.clip(ix, 1, grid_size - 2)
    iy = np.clip(iy, 1, grid_size - 2)

    # Finite difference gradient
    grad_x = (gamma_field[ix + 1, iy] - gamma_field[ix - 1, iy]) / (2 * dx)
    grad_y = (gamma_field[ix, iy + 1] - gamma_field[ix, iy - 1]) / (2 * dx)

    return np.array([grad_x, grad_y])


# ============================================================================
# Utility Functions
# ============================================================================

def distance_to_point(
    entity_position: np.ndarray,
    point: Tuple[float, float]
) -> float:
    """Compute Euclidean distance from entity to point."""
    dx = entity_position[0] - point[0]
    dy = entity_position[1] - point[1]
    return math.sqrt(dx**2 + dy**2)


def compute_orbital_parameters(
    entity: MovingEntity,
    center: Tuple[float, float]
) -> dict:
    """
    Compute orbital parameters for entity trajectory.

    Checks if trajectory forms stable orbit by analyzing:
    - Distance variation (circular vs elliptical)
    - Angular momentum conservation
    - Energy conservation

    Args:
        entity: MovingEntity with position/velocity history
        center: (cx, cy) gravitational center

    Returns:
        Dictionary with orbital parameters
    """
    if len(entity.position_history) < 10:
        return {'status': 'insufficient_data'}

    positions = np.array(entity.position_history)
    velocities = np.array(entity.velocity_history) if entity.velocity_history else None

    # Distance to center over time
    center_array = np.array(center)
    distances = np.linalg.norm(positions - center_array, axis=1)

    # Basic statistics
    r_min = float(np.min(distances))
    r_max = float(np.max(distances))
    r_mean = float(np.mean(distances))
    r_std = float(np.std(distances))

    # Orbital classification
    eccentricity_estimate = (r_max - r_min) / (r_max + r_min)

    if eccentricity_estimate < 0.1:
        orbit_type = 'circular'
    elif eccentricity_estimate < 0.5:
        orbit_type = 'elliptical'
    else:
        orbit_type = 'highly_eccentric_or_escape'

    # Check for collapse or escape
    recent_distances = distances[-100:]
    if len(recent_distances) > 10:
        trend = np.polyfit(range(len(recent_distances)), recent_distances, 1)[0]
        if trend < -0.1:
            orbit_type = 'collapsing'
        elif trend > 0.1:
            orbit_type = 'escaping'

    return {
        'status': 'computed',
        'r_min': r_min,
        'r_max': r_max,
        'r_mean': r_mean,
        'r_std': r_std,
        'eccentricity_estimate': eccentricity_estimate,
        'orbit_type': orbit_type,
        'trajectory_length': len(positions)
    }


if __name__ == "__main__":
    print("=" * 70)
    print("V10 ENTITY MOTION MODULE - GRADIENT FOLLOWING")
    print("=" * 70)
    print()

    print("Creating planet cluster...")
    planet = generate_planet_cluster(
        center=(50.0, 50.0),
        radius=10.0,
        count=100,
        tick_budget=1
    )
    print(f"  Created {len(planet)} stationary entities")
    print()

    print("Creating mobile entities with RANDOM velocities...")
    mobile = generate_mobile_entities_random_velocities(
        center=(50.0, 50.0),
        distances=[30.0, 40.0],
        velocities=[0.3, 0.5],
        count_per_config=2,
        c=1.0,
        random_direction=True
    )
    print(f"  Created {len(mobile)} mobile entities")
    print()

    entity = mobile[0]
    print(f"Testing entity: {entity.entity_id}")
    print(f"  Initial position: {entity.position}")
    print(f"  Initial velocity: {entity.velocity}")
    print(f"  Speed: {entity.speed:.3f}c")
    print()
