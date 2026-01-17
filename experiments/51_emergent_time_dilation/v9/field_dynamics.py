#!/usr/bin/env python3
"""
Field Dynamics for Experiment 51i (V9)

Implements reaction-diffusion load field and regenerative energy field
with DYNAMIC sources from moving entities.
"""

import numpy as np
from typing import List, Tuple
from scipy.ndimage import laplace


class FieldState:
    """Container for load and energy field states."""

    def __init__(self, grid_size: int = 100):
        self.grid_size = grid_size
        self.L = np.zeros((grid_size, grid_size), dtype=float)  # Load field
        self.E = np.ones((grid_size, grid_size), dtype=float) * 10.0  # Energy field

    def copy(self):
        """Return deep copy of field state."""
        new_state = FieldState(self.grid_size)
        new_state.L = self.L.copy()
        new_state.E = self.E.copy()
        return new_state


def compute_source_field(
    entities: List,
    grid_size: int,
    E_max: float = 15.0,
    scale: float = 1.0
) -> np.ndarray:
    """
    Compute dynamic source term S(x,t) from ALL entities.

    This is the KEY INNOVATION of V9: Source changes as entities move!

    S(x) = scale * Σ_i [ mass_i * energy_i * velocity_factor_i ] at position x

    Args:
        entities: List of MovingEntity and/or StationaryEntity
        grid_size: Size of grid
        E_max: Maximum energy for normalization
        scale: Overall source strength scaling

    Returns:
        Source field S as (grid_size, grid_size) array
    """
    S = np.zeros((grid_size, grid_size), dtype=float)

    for entity in entities:
        ix = int(entity.position[0]) % grid_size
        iy = int(entity.position[1]) % grid_size

        contribution = entity.field_contribution((ix, iy), E_max)
        S[ix, iy] += scale * contribution

    return S


def update_load_field(
    L: np.ndarray,
    S: np.ndarray,
    alpha: float = 0.012,
    gamma: float = 0.0005,
    dt: float = 1.0
) -> np.ndarray:
    """
    Update load field using reaction-diffusion dynamics.

    L[t+1] = L[t] + dt * (alpha * ∇²L + S - gamma * L²)

    Args:
        L: Current load field
        S: Source term (from entities)
        alpha: Diffusion coefficient
        gamma: Nonlinear damping coefficient
        dt: Time step

    Returns:
        Updated load field L[t+1]
    """
    # Compute Laplacian (diffusion term)
    laplacian_L = laplace(L)

    # Reaction-diffusion update
    dL_dt = alpha * laplacian_L + S - gamma * (L ** 2)
    L_new = L + dt * dL_dt

    # Ensure non-negative
    L_new = np.maximum(L_new, 0.0)

    return L_new


def update_energy_field(
    E: np.ndarray,
    L: np.ndarray,
    R: float = 1.2,
    D: float = 0.01,
    E_max: float = 15.0,
    dt: float = 1.0
) -> np.ndarray:
    """
    Update energy field with regeneration and load-dependent drainage.

    E[t+1] = min(E_max, E[t] + dt * (R - D * L))

    Args:
        E: Current energy field
        L: Current load field
        R: Regeneration rate
        D: Drainage coefficient
        E_max: Maximum energy capacity
        dt: Time step

    Returns:
        Updated energy field E[t+1]
    """
    # Regeneration and drainage
    dE_dt = R - D * L
    E_new = E + dt * dE_dt

    # Clamp to [0, E_max]
    E_new = np.clip(E_new, 0.0, E_max)

    return E_new


def compute_gamma_grav(
    L: np.ndarray,
    E: np.ndarray,
    capacity_min: float = 0.1,
    work_threshold: float = 0.5
) -> np.ndarray:
    """
    Compute gravitational time dilation field from load and energy.

    gamma_grav(x) = 1 / (capacity_effective / capacity_base)

    Where capacity_effective depends on both load saturation and energy availability.

    Args:
        L: Load field
        E: Energy field
        capacity_min: Minimum effective capacity
        work_threshold: Minimum energy required for work

    Returns:
        gamma_grav field (values >= 1.0)
    """
    # Capacity from load (saturation effect)
    capacity_from_load = 1.0 / (1.0 + L)

    # Capacity from energy (availability effect)
    capacity_from_energy = E / (E + work_threshold)

    # Combined capacity
    capacity_eff = capacity_from_load * capacity_from_energy
    capacity_eff = np.maximum(capacity_eff, capacity_min)

    # Time dilation: gamma = 1 / capacity
    # Where capacity < 1.0, entity experiences fewer ticks → time dilation
    gamma_grav = 1.0 / capacity_eff

    return gamma_grav


def compute_work_done(
    E: np.ndarray,
    L: np.ndarray,
    tick_budget: float = 1.0
) -> np.ndarray:
    """
    Compute actual work done at each grid point.

    work = tick_budget if E >= tick_budget, else 0

    Args:
        E: Energy field
        L: Load field
        tick_budget: Required energy per work unit

    Returns:
        Work done field (0 or tick_budget at each point)
    """
    work = np.where(E >= tick_budget, tick_budget, 0.0)
    return work


class FieldDynamics:
    """
    Manages coupled load-energy field dynamics with moving entities.
    """

    def __init__(
        self,
        grid_size: int = 100,
        alpha: float = 0.012,
        gamma: float = 0.0005,
        scale: float = 0.75,
        R: float = 1.2,
        D: float = 0.01,
        E_max: float = 15.0,
        capacity_min: float = 0.1,
        work_threshold: float = 0.5
    ):
        self.grid_size = grid_size

        # Load field parameters
        self.alpha = alpha
        self.gamma = gamma
        self.scale = scale

        # Energy field parameters
        self.R = R
        self.D = D
        self.E_max = E_max

        # Capacity parameters
        self.capacity_min = capacity_min
        self.work_threshold = work_threshold

        # Initialize fields
        self.state = FieldState(grid_size)

        # Statistics
        self.tick_count = 0
        self.L_history = []
        self.E_history = []

    def step(self, entities: List, dt: float = 1.0):
        """
        Perform one timestep of field evolution.

        Args:
            entities: List of all entities (moving + stationary)
            dt: Time step
        """
        # 1. Compute source term from entity positions
        S = compute_source_field(
            entities,
            self.grid_size,
            self.E_max,
            self.scale
        )

        # 2. Update load field (reaction-diffusion)
        self.state.L = update_load_field(
            self.state.L,
            S,
            self.alpha,
            self.gamma,
            dt
        )

        # 3. Update energy field (regeneration-drainage)
        self.state.E = update_energy_field(
            self.state.E,
            self.state.L,
            self.R,
            self.D,
            self.E_max,
            dt
        )

        self.tick_count += 1

    def get_gamma_grav(self) -> np.ndarray:
        """Get current gravitational time dilation field."""
        return compute_gamma_grav(
            self.state.L,
            self.state.E,
            self.capacity_min,
            self.work_threshold
        )

    def get_gamma_at_position(self, position: Tuple[float, float]) -> float:
        """Get gamma_grav at specific position."""
        ix = int(position[0]) % self.grid_size
        iy = int(position[1]) % self.grid_size

        gamma_field = self.get_gamma_grav()
        return float(gamma_field[ix, iy])

    def get_statistics(self) -> dict:
        """Return field statistics."""
        gamma_field = self.get_gamma_grav()

        return {
            'tick': self.tick_count,
            'L_mean': float(np.mean(self.state.L)),
            'L_max': float(np.max(self.state.L)),
            'L_std': float(np.std(self.state.L)),
            'E_mean': float(np.mean(self.state.E)),
            'E_min': float(np.min(self.state.E)),
            'E_std': float(np.std(self.state.E)),
            'gamma_mean': float(np.mean(gamma_field)),
            'gamma_max': float(np.max(gamma_field)),
            'gamma_min': float(np.min(gamma_field)),
        }

    def save_snapshot(self):
        """Save current field state to history."""
        self.L_history.append(self.state.L.copy())
        self.E_history.append(self.state.E.copy())


if __name__ == "__main__":
    # Demo: Test field dynamics
    print("=" * 70)
    print("FIELD DYNAMICS MODULE - DEMO")
    print("=" * 70)
    print()

    # Create field dynamics
    fields = FieldDynamics(
        grid_size=100,
        alpha=0.012,
        gamma=0.0005,
        scale=0.75,
        R=1.2,
        E_max=15.0
    )

    print("Initial state:")
    print(f"  L: mean={np.mean(fields.state.L):.3f}, max={np.max(fields.state.L):.3f}")
    print(f"  E: mean={np.mean(fields.state.E):.3f}, min={np.min(fields.state.E):.3f}")
    print()

    # Create mock entities
    from entity_motion import StationaryEntity
    import numpy as np

    # Planet cluster at center
    entities = []
    for i in range(100):
        r = 10.0 * np.sqrt(np.random.random())
        theta = 2 * np.pi * np.random.random()
        x = 50.0 + r * np.cos(theta)
        y = 50.0 + r * np.sin(theta)

        entities.append(StationaryEntity(
            entity_id=f"planet_{i}",
            position=np.array([x, y]),
            tick_budget=1,
            energy=10.0
        ))

    print(f"Created {len(entities)} entities in planet cluster")
    print()

    # Run for 100 ticks
    print("Simulating 100 ticks...")
    for tick in range(100):
        fields.step(entities, dt=1.0)

        if tick % 20 == 0:
            stats = fields.get_statistics()
            print(f"  Tick {tick}:")
            print(f"    L: mean={stats['L_mean']:.3f}, max={stats['L_max']:.3f}")
            print(f"    E: mean={stats['E_mean']:.3f}, min={stats['E_min']:.3f}")
            print(f"    gamma: mean={stats['gamma_mean']:.3f}, max={stats['gamma_max']:.3f}")

    print()
    print("Final gamma field at different distances from center:")
    for r in [5, 15, 25, 35, 45]:
        gamma = fields.get_gamma_at_position((50.0 + r, 50.0))
        print(f"  r={r:2d}: gamma={gamma:.3f}")
    print()
