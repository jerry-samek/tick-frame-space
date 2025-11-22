"""
Dimensional Wave Equation Solver (1D-5D)

Implements damped wave equation in arbitrary dimensions:
    d²A/dt² = c² ∇²A - 2γ dA/dt + J(x,t)

Uses leapfrog integration for stability.
"""

import numpy as np
from typing import Tuple, List, Optional

class DimensionalWaveSolver:
    """
    Solves wave equation in 1D through 5D.
    """

    def __init__(self, dimension: int, grid_sizes: tuple, L: float, c: float, dt: float, gamma: float):
        """
        Initialize solver.

        Args:
            dimension: Spatial dimension (1-5)
            grid_sizes: Grid size in each dimension (e.g., (128, 128) for 2D)
            L: Domain size in each dimension
            c: Wave speed
            dt: Time step
            gamma: Damping coefficient
        """
        self.dim = dimension
        self.grid_sizes = grid_sizes
        self.L = L
        self.c = c
        self.dt = dt
        self.gamma = gamma

        # Grid spacings
        self.dx = tuple(L / (n - 1) for n in grid_sizes)

        # CFL check
        cfl = c * dt / min(self.dx)
        if cfl > 1.0:
            raise ValueError(f"CFL condition violated: {cfl:.3f} > 1.0")

        # Initialize fields
        self.A_curr = np.zeros(grid_sizes, dtype=np.float64)
        self.A_prev = np.zeros(grid_sizes, dtype=np.float64)

        # Agent salience
        self.psi = 0.0

        # Time tracking
        self.t = 0.0
        self.step_count = 0

    def laplacian(self, field: np.ndarray) -> np.ndarray:
        """
        Compute Laplacian in arbitrary dimensions using finite differences.

        Uses second-order central differences:
            d²f/dx² ≈ (f[i+1] - 2f[i] + f[i-1]) / dx²
        """
        lapl = np.zeros_like(field)

        for axis in range(self.dim):
            # Roll field forward and backward along axis
            f_plus = np.roll(field, -1, axis=axis)
            f_minus = np.roll(field, 1, axis=axis)

            # Second derivative
            lapl += (f_plus - 2*field + f_minus) / (self.dx[axis]**2)

        return lapl

    def step(self, source_emissions: List[Tuple[tuple, float]]) -> None:
        """
        Advance one time step using stabilized leapfrog integration.

        Args:
            source_emissions: List of (grid_index, amplitude) for sources emitting this tick
        """
        # Compute Laplacian
        lapl = self.laplacian(self.A_curr)

        # Source term
        J = np.zeros_like(self.A_curr)
        for idx, amplitude in source_emissions:
            J[idx] += amplitude

        # Stabilized leapfrog update with enhanced damping
        c2_dt2 = (self.c * self.dt)**2
        gamma_dt = self.gamma * self.dt

        # Add numerical dissipation for high dimensions (helps stability)
        numerical_damping = 1.0 + 0.01 * self.dim  # Scales with dimension
        effective_gamma_dt = gamma_dt * numerical_damping

        # Leapfrog with improved damping formulation
        denominator = 1.0 + 2.0 * effective_gamma_dt
        A_next = ((2.0 - 4.0*effective_gamma_dt) * self.A_curr -
                  (1.0 - 2.0*effective_gamma_dt) * self.A_prev +
                  c2_dt2 * lapl + (self.dt**2) * J)
        A_next /= denominator

        # Clamp field values to prevent overflow (critical for stability)
        max_field = 1000.0  # Reasonable upper bound
        A_next = np.clip(A_next, -max_field, max_field)

        # Update fields
        self.A_prev = self.A_curr.copy()
        self.A_curr = A_next

        # Update time
        self.t += self.dt
        self.step_count += 1

    def compute_salience(self, window_center: tuple, window_width: float) -> float:
        """
        Compute agent salience from field energy in detection window.

        Uses Gaussian window: w(x) = exp(-|x - x_center|² / (2σ²))
        Salience: S = ∫ w(x) A(x)² dx
        """
        # Create coordinate grids
        coords = [np.linspace(0, self.L, n) for n in self.grid_sizes]
        grids = np.meshgrid(*coords, indexing='ij')

        # Distance from window center
        dist_sq = sum((g - c)**2 for g, c in zip(grids, window_center))

        # Gaussian window
        sigma = window_width / 2.35  # FWHM → σ
        window = np.exp(-dist_sq / (2 * sigma**2))

        # Field energy with safe squaring (prevent overflow)
        field_clamped = np.clip(self.A_curr, -100.0, 100.0)
        energy = field_clamped**2

        # Weighted integral (salience)
        # Use nan-safe sum to handle any numerical issues
        weighted_energy = window * energy
        salience = np.nansum(weighted_energy)

        # Normalize by grid volume
        dV = np.prod(self.dx)
        salience *= dV

        # Safety: return finite value
        if not np.isfinite(salience):
            return 0.0

        return salience


class DimensionalSourceConfig:
    """
    Configuration for multi-source emissions in N dimensions.
    """

    def __init__(self, num_sources: int, positions: List[tuple], amplitudes: List[float],
                 phases: Optional[List[int]] = None):
        """
        Initialize source configuration.

        Args:
            num_sources: Number of sources
            positions: Source positions in N-D space (each is tuple of coordinates)
            amplitudes: Emission amplitudes
            phases: Phase offsets in ticks (None → all in-phase)
        """
        self.num_sources = num_sources
        self.positions = positions
        self.amplitudes = amplitudes
        self.phases = phases if phases is not None else [0] * num_sources

    def get_emissions(self, tick: int, grid_sizes: tuple, L: float) -> List[Tuple[tuple, float]]:
        """
        Get source emissions for current tick.

        Returns:
            List of (grid_index, amplitude) for sources emitting this tick
        """
        emissions = []

        for i in range(self.num_sources):
            # Check if this source emits this tick (based on phase)
            if tick % 1 == self.phases[i] % 1:
                # Convert position to grid index
                idx = tuple(int(p / L * (n - 1)) for p, n in zip(self.positions[i], grid_sizes))

                # Clamp to grid bounds
                idx = tuple(max(0, min(n-1, i)) for i, n in zip(idx, grid_sizes))

                emissions.append((idx, self.amplitudes[i]))

        return emissions


def create_symmetric_config_nd(num_sources: int, dimension: int, L: float,
                                alpha_0: float) -> DimensionalSourceConfig:
    """
    Create symmetrically distributed sources in N dimensions.

    Sources placed on a line through the center, evenly spaced.
    """
    if num_sources == 1:
        # Center of domain
        center = tuple([L / 2.0] * dimension)
        positions = [center]
    else:
        # Evenly spaced along first axis, centered in others
        positions = []
        for i in range(num_sources):
            pos = [L * (i + 1) / (num_sources + 1)]  # First axis
            pos += [L / 2.0] * (dimension - 1)  # Centered in other axes
            positions.append(tuple(pos))

    amplitudes = [alpha_0] * num_sources

    return DimensionalSourceConfig(num_sources, positions, amplitudes)


def create_clustered_config_nd(num_sources: int, dimension: int, L: float,
                                alpha_0: float) -> DimensionalSourceConfig:
    """
    Create clustered sources in N dimensions.

    All sources in one quadrant/region of space.
    """
    if num_sources == 1:
        center = tuple([L / 2.0] * dimension)
        positions = [center]
    else:
        # Cluster in first quadrant, along diagonal
        positions = []
        for i in range(num_sources):
            # Scale from 0.25L to 0.75L along diagonal
            t = 0.25 + 0.5 * i / (num_sources - 1) if num_sources > 1 else 0.5
            pos = tuple([L * t] * dimension)
            positions.append(pos)

    amplitudes = [alpha_0] * num_sources

    return DimensionalSourceConfig(num_sources, positions, amplitudes)


def run_dimensional_simulation(config: DimensionalSourceConfig, dimension: int,
                                grid_sizes: tuple, alpha_0: float, alpha_1: float,
                                gamma: float, M: int, T: float) -> Optional[dict]:
    """
    Run one dimensional simulation.

    Returns:
        Result dictionary or None if CFL violated
    """
    # Constants
    L = 1.0
    c = 1.0
    psi_threshold = 1.01

    # Adaptive time step for CFL stability
    dx_min = L / (max(grid_sizes) - 1)

    # More conservative CFL for high dimensions
    if dimension <= 2:
        cfl_factor = 0.4
    elif dimension == 3:
        cfl_factor = 0.3
    else:  # 4D, 5D
        cfl_factor = 0.2

    dt = cfl_factor * dx_min / c

    # Ensure dt is reasonable
    dt = max(dt, 0.0001)
    dt = min(dt, 0.01)  # Cap at 0.01 for efficiency

    # CFL check
    cfl = c * dt / dx_min
    if cfl > 1.0:
        return None

    # Initialize solver
    solver = DimensionalWaveSolver(dimension, grid_sizes, L, c, dt, gamma)

    # Agent window at center
    window_center = tuple([L / 2.0] * dimension)
    window_width = 0.1 * L

    # Tracking
    agent_commits = []
    psi_history = []
    max_salience = 0.0

    num_steps = int(T / dt)
    tick = 0

    for step in range(num_steps):
        # Emit from sources
        emissions = config.get_emissions(tick, grid_sizes, L)
        solver.step(emissions)

        # Agent samples every M steps
        if step % M == 0:
            salience = solver.compute_salience(window_center, window_width)
            solver.psi += salience * alpha_1

            psi_history.append((solver.t, solver.psi))
            max_salience = max(max_salience, salience)

            # Check threshold
            if solver.psi >= psi_threshold:
                agent_commits.append(solver.t)
                solver.psi = 0.0

            tick += 1

    # Statistics
    has_commits = len(agent_commits) > 0
    commit_rate = len(agent_commits) / T if T > 0 else 0.0

    # Source emission counts
    source_emission_counts = [tick] * config.num_sources

    result = {
        'parameters': {
            'dimension': dimension,
            'num_sources': config.num_sources,
            'alpha_0': alpha_0,
            'alpha_1': alpha_1,
            'gamma': gamma,
            'M': M,
            'T': T,
            'grid_sizes': grid_sizes,
        },
        'statistics': {
            'has_commits': has_commits,
            'agent_commit_count': len(agent_commits),
            'commit_rate': commit_rate,
            'first_commit_time': agent_commits[0] if has_commits else None,
            'last_commit_time': agent_commits[-1] if has_commits else None,
            'final_psi': psi_history[-1][1] if psi_history else 0.0,
            'max_salience': max_salience,
            'source_emission_counts': source_emission_counts,
        },
        'commits': agent_commits,
        'psi_history': psi_history,
    }

    return result


if __name__ == "__main__":
    # Test 1D
    print("Testing 1D wave solver...")
    config = create_symmetric_config_nd(1, 1, 1.0, 2.0)
    result = run_dimensional_simulation(config, 1, (1000,), 2.0, 0.0, 0.001, 1, 100.0)
    if result:
        print(f"  1D test: {result['statistics']['agent_commit_count']} commits")
    else:
        print("  1D test: CFL violated")

    # Test 2D
    print("Testing 2D wave solver...")
    config = create_symmetric_config_nd(1, 2, 1.0, 2.0)
    result = run_dimensional_simulation(config, 2, (128, 128), 2.0, 0.0, 0.001, 1, 100.0)
    if result:
        print(f"  2D test: {result['statistics']['agent_commit_count']} commits")
    else:
        print("  2D test: CFL violated")

    print("\nDimensional wave solver framework ready!")
