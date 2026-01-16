"""
GPU-Accelerated Dimensional Wave Equation Solver with Explicit Time Dimension
VARIANT A: Time as Physical Dimension

Implements damped wave equation with time as an EXPLICIT coordinate dimension:
    d²A/dt² = c² (∇²A_spatial + ∇²A_temporal) - 2γ dA/dt + J(x,t)

The Laplacian includes BOTH spatial and temporal dimensions.
Grid shape: (spatial_dims..., time_window_size)

Supports Intel Arc GPU via Intel Extension for PyTorch (IPEX).
Falls back to CPU if GPU is unavailable.
"""

import torch
import numpy as np
from typing import Tuple, List, Optional
import warnings

# Try to import Intel Extension for PyTorch
try:
    import intel_extension_for_pytorch as ipex
    IPEX_AVAILABLE = True
except ImportError:
    IPEX_AVAILABLE = False
    warnings.warn("Intel Extension for PyTorch not available. Using standard PyTorch.")

# Device selection
def get_device():
    """Get best available device: Intel GPU > CUDA > CPU"""
    if torch.cuda.is_available():
        return torch.device('cuda')
    elif hasattr(torch, 'xpu') and torch.xpu.is_available():
        return torch.device('xpu')  # Intel GPU
    else:
        return torch.device('cpu')

DEVICE = get_device()
print(f"GPU Wave Solver using device: {DEVICE}")


class GPUWaveSolver:
    """
    GPU-accelerated wave equation solver with explicit time dimension.

    VARIANT A: Time is treated as a TRUE physical dimension.
    Grid shape: (*spatial_grid_sizes, time_window_size)

    Uses PyTorch tensors for automatic GPU acceleration.
    """

    def __init__(self, dimension: int, grid_sizes: tuple, L: float, c: float,
                 dt: float, gamma: float, time_window_size: int = 10,
                 device: Optional[torch.device] = None):
        """
        Initialize GPU solver with explicit time dimension.

        Args:
            dimension: Spatial dimension (1-5)
            grid_sizes: Grid size in each SPATIAL dimension
            L: Domain size
            c: Wave speed
            dt: Time step
            gamma: Damping coefficient
            time_window_size: Size of explicit time dimension
            device: PyTorch device (None = auto-select)
        """
        self.spatial_dim = dimension
        self.spatial_grid_sizes = grid_sizes
        self.time_window_size = time_window_size

        # Total dimension = spatial + 1 (time)
        self.dim = dimension + 1

        # Full grid includes time dimension
        self.grid_sizes = (*grid_sizes, time_window_size)

        self.L = L
        self.c = c
        self.dt = dt
        self.gamma = gamma
        self.device = device if device is not None else DEVICE

        # Grid spacings (spatial + temporal)
        # For time dimension, use dt as the grid spacing
        self.dx = tuple(L / (n - 1) for n in grid_sizes) + (dt,)

        # CFL check (only for spatial dimensions)
        spatial_dx_min = min(L / (n - 1) for n in grid_sizes)
        cfl = c * dt / spatial_dx_min
        if cfl > 1.0:
            raise ValueError(f"CFL condition violated: {cfl:.3f} > 1.0")

        # Initialize fields on GPU with time dimension
        self.A_curr = torch.zeros(self.grid_sizes, dtype=torch.float32, device=self.device)
        self.A_prev = torch.zeros(self.grid_sizes, dtype=torch.float32, device=self.device)

        # Precompute constants
        self.c2_dt2 = (c * dt) ** 2

        # Simple damping (matching V5)
        self.gamma_dt = gamma * dt

        # Agent salience
        self.psi = 0.0

        # Time tracking
        self.t = 0.0
        self.step_count = 0

        # Current time slice index (circular buffer)
        self.current_time_idx = 0

    def laplacian(self, field: torch.Tensor) -> torch.Tensor:
        """
        Compute Laplacian in arbitrary dimensions INCLUDING TIME.

        VARIANT A: The Laplacian includes the time dimension as a true coordinate.
        ∇²A = ∂²A/∂x² + ∂²A/∂y² + ... + ∂²A/∂t²

        GPU-accelerated using torch.roll for shifted arrays.
        Time dimension has periodic boundary conditions (circular).
        """
        lapl = torch.zeros_like(field)

        # Iterate over ALL dimensions (spatial + time)
        for axis in range(self.dim):
            # Roll field forward and backward along axis
            # Time dimension (last axis) uses periodic BC via roll
            f_plus = torch.roll(field, -1, dims=axis)
            f_minus = torch.roll(field, 1, dims=axis)

            # Second derivative
            lapl += (f_plus - 2*field + f_minus) / (self.dx[axis]**2)

        return lapl

    def step(self, source_emissions: List[Tuple[tuple, float]]) -> None:
        """
        Advance one time step using leapfrog integration.

        VARIANT A: Sources inject across ALL time slices simultaneously
        since time is a coordinate dimension, not an evolution parameter.

        All operations on GPU for maximum speed.
        """
        # Compute Laplacian (GPU operation) - includes time dimension
        lapl = self.laplacian(self.A_curr)

        # Source term (build on GPU)
        # VARIANT A: Inject sources at ALL time slices
        J = torch.zeros_like(self.A_curr)
        for spatial_idx, amplitude in source_emissions:
            # Extend spatial index to include all time slices
            for time_idx in range(self.time_window_size):
                full_idx = (*spatial_idx, time_idx)
                J[full_idx] += amplitude

        # V5-style leapfrog update:
        # A_next = 2*A_curr - A_prev + dt²*(c²*∇²A - γ*(A_curr-A_prev)/dt + src)
        # Simplified: A_next = (2-γdt)*A_curr - (1-γdt)*A_prev + c²dt²*∇²A + dt²*src
        A_next = ((2.0 - self.gamma_dt) * self.A_curr -
                  (1.0 - self.gamma_dt) * self.A_prev +
                  self.c2_dt2 * lapl + (self.dt**2) * J)

        # Clamp to prevent overflow
        A_next = torch.clamp(A_next, -1000.0, 1000.0)

        # Update fields
        self.A_prev = self.A_curr.clone()
        self.A_curr = A_next

        # Update time
        self.t += self.dt
        self.step_count += 1

        # Rotate circular time buffer index
        self.current_time_idx = (self.current_time_idx + 1) % self.time_window_size

    def compute_salience(self, window_center: tuple = None, window_width: float = None) -> float:
        """
        Compute agent salience from GLOBAL field energy.

        VARIANT A: Integrates over ENTIRE spacetime grid (spatial + temporal).

        GPU-accelerated energy integration over entire domain.
        """
        # Field energy (GPU) - global integral over spacetime
        field_clamped = torch.clamp(self.A_curr, -100.0, 100.0)
        energy = field_clamped**2

        # Sum over entire field (spatial + temporal)
        salience = torch.sum(energy).item()

        # Multiply by grid spacing (geometric mean of ALL dimensions including time)
        # For (N+1)-D (spatial + time), use geometric mean of spacings
        dx_mean = np.prod(self.dx) ** (1.0 / self.dim)
        salience *= dx_mean

        # Safety check
        if not np.isfinite(salience):
            return 0.0

        return salience


class DimensionalSourceConfig:
    """
    Configuration for multi-source emissions in N dimensions.
    (Same as NumPy version - no GPU needed for source logic)
    """

    def __init__(self, num_sources: int, positions: List[tuple], amplitudes: List[float],
                 phases: Optional[List[int]] = None):
        self.num_sources = num_sources
        self.positions = positions
        self.amplitudes = amplitudes
        self.phases = phases if phases is not None else [0] * num_sources

    def get_emissions(self, tick: int, grid_sizes: tuple, L: float) -> List[Tuple[tuple, float]]:
        """Get source emissions for current tick."""
        emissions = []

        for i in range(self.num_sources):
            if tick % 1 == self.phases[i] % 1:
                # Convert position to grid index
                idx = tuple(int(p / L * (n - 1)) for p, n in zip(self.positions[i], grid_sizes))
                idx = tuple(max(0, min(n-1, i)) for i, n in zip(idx, grid_sizes))
                emissions.append((idx, self.amplitudes[i]))

        return emissions


def create_symmetric_config_nd(num_sources: int, dimension: int, L: float,
                                alpha_0: float) -> DimensionalSourceConfig:
    """Create symmetrically distributed sources in N dimensions."""
    if num_sources == 1:
        center = tuple([L / 2.0] * dimension)
        positions = [center]
    else:
        positions = []
        for i in range(num_sources):
            pos = [L * (i + 1) / (num_sources + 1)]
            pos += [L / 2.0] * (dimension - 1)
            positions.append(tuple(pos))

    amplitudes = [alpha_0] * num_sources
    return DimensionalSourceConfig(num_sources, positions, amplitudes)


def create_clustered_config_nd(num_sources: int, dimension: int, L: float,
                                alpha_0: float) -> DimensionalSourceConfig:
    """Create clustered sources in N dimensions."""
    if num_sources == 1:
        center = tuple([L / 2.0] * dimension)
        positions = [center]
    else:
        positions = []
        for i in range(num_sources):
            t = 0.25 + 0.5 * i / (num_sources - 1) if num_sources > 1 else 0.5
            pos = tuple([L * t] * dimension)
            positions.append(pos)

    amplitudes = [alpha_0] * num_sources
    return DimensionalSourceConfig(num_sources, positions, amplitudes)


def run_gpu_simulation(config: DimensionalSourceConfig, dimension: int,
                        grid_sizes: tuple, alpha_0: float, alpha_1: float,
                        gamma: float, M: int, T: float,
                        time_window_size: int = 10,
                        device: Optional[torch.device] = None) -> Optional[dict]:
    """
    Run one dimensional simulation on GPU with explicit time dimension.

    VARIANT A: Time is treated as a physical dimension.

    Args:
        dimension: SPATIAL dimension (1-5)
        grid_sizes: Grid sizes for SPATIAL dimensions only
        time_window_size: Size of explicit time dimension

    Returns:
        Result dictionary or None if CFL violated
    """
    # Constants
    L = 1.0
    c = 1.0
    psi_threshold = 1.01

    # Adaptive time step for CFL stability
    dx_min = L / (max(grid_sizes) - 1)

    # Increased CFL factors for faster time steps (still stable)
    if dimension <= 2:
        cfl_factor = 0.6  # Was 0.4 - 1.5x fewer steps
    elif dimension == 3:
        cfl_factor = 0.5  # Was 0.3 - 1.7x fewer steps
    else:
        cfl_factor = 0.4  # Was 0.2 - 2x fewer steps

    dt = cfl_factor * dx_min / c
    dt = max(dt, 0.0001)
    dt = min(dt, 0.01)

    # CFL check
    cfl = c * dt / dx_min
    if cfl > 1.0:
        return None

    # Initialize GPU solver with explicit time dimension
    solver = GPUWaveSolver(dimension, grid_sizes, L, c, dt, gamma,
                           time_window_size=time_window_size, device=device)

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
    source_emission_counts = [tick] * config.num_sources

    # Extract final_psi before discarding history (to save memory in multiprocessing)
    final_psi = psi_history[-1][1] if psi_history else 0.0

    result = {
        'parameters': {
            'spatial_dimension': dimension,  # Spatial dimension only
            'total_dimension': dimension + 1,  # Spatial + time
            'num_sources': config.num_sources,
            'alpha_0': alpha_0,
            'alpha_1': alpha_1,
            'gamma': gamma,
            'M': M,
            'T': T,
            'grid_sizes': grid_sizes,  # Spatial grid only
            'time_window_size': time_window_size,
            'variant': 'A_physics',  # Mark as Variant A
        },
        'statistics': {
            'has_commits': has_commits,
            'agent_commit_count': len(agent_commits),
            'commit_rate': commit_rate,
            'first_commit_time': agent_commits[0] if has_commits else None,
            'last_commit_time': agent_commits[-1] if has_commits else None,
            'final_psi': final_psi,
            'max_salience': max_salience,
            'source_emission_counts': source_emission_counts,
        },
        # NOTE: psi_history and commits removed to reduce IPC memory usage
        # These can hold 1M+ entries for long simulations
    }

    return result


if __name__ == "__main__":
    print("=" * 80)
    print("VARIANT A: Time as Physical Dimension - GPU Wave Solver")
    print("=" * 80)
    print(f"Device: {DEVICE}")
    print(f"IPEX available: {IPEX_AVAILABLE}")

    # Test 2D + time (should behave like 3D?)
    print("\nTesting 2D + time (Variant A)...")
    config = create_symmetric_config_nd(1, 2, 1.0, 2.0)
    result = run_gpu_simulation(config, 2, (48, 48), 2.0, 0.0, 0.001, 1, 50.0,
                                time_window_size=10)
    if result:
        print(f"  Spatial dim: {result['parameters']['spatial_dimension']}")
        print(f"  Total dim (with time): {result['parameters']['total_dimension']}")
        print(f"  Grid: {result['parameters']['grid_sizes']} + time({result['parameters']['time_window_size']})")
        print(f"  Commits: {result['statistics']['agent_commit_count']}")
        print(f"  Commit rate: {result['statistics']['commit_rate']:.4f}")
    else:
        print("  2D+t test: CFL violated")

    # Test 3D + time (should behave like 4D?)
    print("\nTesting 3D + time (Variant A)...")
    config = create_symmetric_config_nd(1, 3, 1.0, 2.0)
    result = run_gpu_simulation(config, 3, (24, 24, 24), 2.0, 0.0, 0.001, 1, 50.0,
                                time_window_size=10)
    if result:
        print(f"  Spatial dim: {result['parameters']['spatial_dimension']}")
        print(f"  Total dim (with time): {result['parameters']['total_dimension']}")
        print(f"  Grid: {result['parameters']['grid_sizes']} + time({result['parameters']['time_window_size']})")
        print(f"  Commits: {result['statistics']['agent_commit_count']}")
        print(f"  Commit rate: {result['statistics']['commit_rate']:.4f}")
    else:
        print("  3D+t test: CFL violated")

    print("\n" + "=" * 80)
    print("Variant A GPU wave solver ready!")
    print("=" * 80)
