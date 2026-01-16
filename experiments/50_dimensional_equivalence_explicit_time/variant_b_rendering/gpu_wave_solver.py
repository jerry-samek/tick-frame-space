"""
GPU-Accelerated Dimensional Wave Equation Solver with Sliding Window Storage
VARIANT B: Time as Rendering Dimension

Implements damped wave equation with SPATIAL Laplacian only:
    d²A/dt² = c² ∇²A_spatial - 2γ dA/dt + J(x,t)

But stores temporal history in a sliding window buffer (from Experiment #49):
    buffer[time_offset] = field_snapshot

Time is explicit in STORAGE but NOT in physics.
Metrics are computed across the temporal window, not just a single snapshot.

Supports Intel Arc GPU via Intel Extension for PyTorch (IPEX).
Falls back to CPU if GPU is unavailable.
"""

import torch
import numpy as np
from typing import Tuple, List, Optional, Deque
from collections import deque
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


class FieldSlidingWindow:
    """
    Sliding window buffer for field snapshots (Variant B).

    Stores temporal history of field states for metric computation.
    Physics remains spatial-only; time is explicit in storage.
    """

    def __init__(self, grid_shape: tuple, window_size: int, device: torch.device):
        """
        Initialize sliding window for field storage.

        Args:
            grid_shape: Shape of spatial grid
            window_size: Number of time snapshots to retain
            device: PyTorch device
        """
        self.grid_shape = grid_shape
        self.window_size = window_size
        self.device = device

        # Ring buffer: deque of field snapshots
        self.buffer: Deque[torch.Tensor] = deque(maxlen=window_size)

        # Initialize with zeros
        for _ in range(window_size):
            self.buffer.append(torch.zeros(grid_shape, dtype=torch.float32, device=device))

        self.frame_count = 0

    def add_snapshot(self, field: torch.Tensor) -> None:
        """Add current field state to sliding window."""
        self.buffer.append(field.clone())  # Clone to avoid reference issues
        self.frame_count += 1

    def get_snapshot(self, offset: int = 0) -> torch.Tensor:
        """
        Get snapshot N ticks in the past.

        Args:
            offset: 0 = most recent, 1 = one tick back, etc.

        Returns:
            Field snapshot
        """
        if offset >= len(self.buffer):
            offset = len(self.buffer) - 1
        return self.buffer[-(offset + 1)]

    def compute_temporal_energy(self) -> float:
        """
        Compute total energy across entire temporal window.

        VARIANT B: Integrates energy over time dimension via stored snapshots.
        """
        total_energy = 0.0
        for snapshot in self.buffer:
            snapshot_clamped = torch.clamp(snapshot, -100.0, 100.0)
            energy = torch.sum(snapshot_clamped ** 2).item()
            total_energy += energy

        return total_energy

    def get_window_size(self) -> int:
        """Get current window size (may be less than max during initialization)."""
        return len(self.buffer)


class GPUWaveSolver:
    """
    GPU-accelerated wave equation solver with sliding window storage.

    VARIANT B: Physics is spatial-only, but temporal history is stored
    in a sliding window for metric computation.

    Uses PyTorch tensors for automatic GPU acceleration.
    """

    def __init__(self, dimension: int, grid_sizes: tuple, L: float, c: float,
                 dt: float, gamma: float, time_window_size: int = 10,
                 device: Optional[torch.device] = None):
        """
        Initialize GPU solver with sliding window storage.

        Args:
            dimension: Spatial dimension (1-5)
            grid_sizes: Grid size in each SPATIAL dimension
            L: Domain size
            c: Wave speed
            dt: Time step
            gamma: Damping coefficient
            time_window_size: Number of temporal snapshots to retain
            device: PyTorch device (None = auto-select)
        """
        self.dim = dimension
        self.grid_sizes = grid_sizes
        self.time_window_size = time_window_size
        self.L = L
        self.c = c
        self.dt = dt
        self.gamma = gamma
        self.device = device if device is not None else DEVICE

        # Grid spacings (spatial only)
        self.dx = tuple(L / (n - 1) for n in grid_sizes)

        # CFL check
        cfl = c * dt / min(self.dx)
        if cfl > 1.0:
            raise ValueError(f"CFL condition violated: {cfl:.3f} > 1.0")

        # Initialize fields on GPU
        self.A_curr = torch.zeros(grid_sizes, dtype=torch.float32, device=self.device)
        self.A_prev = torch.zeros(grid_sizes, dtype=torch.float32, device=self.device)

        # VARIANT B: Sliding window for temporal storage
        self.sliding_window = FieldSlidingWindow(grid_sizes, time_window_size, self.device)

        # Precompute constants
        self.c2_dt2 = (c * dt) ** 2

        # Simple damping (matching V5)
        self.gamma_dt = gamma * dt

        # Agent salience
        self.psi = 0.0

        # Time tracking
        self.t = 0.0
        self.step_count = 0

    def laplacian(self, field: torch.Tensor) -> torch.Tensor:
        """
        Compute Laplacian in SPATIAL dimensions only.

        VARIANT B: Time is NOT part of the physics, only storage.
        ∇²A = ∂²A/∂x² + ∂²A/∂y² + ... (spatial only)

        GPU-accelerated using torch.roll for shifted arrays.
        """
        lapl = torch.zeros_like(field)

        # Iterate over SPATIAL dimensions only
        for axis in range(self.dim):
            # Roll field forward and backward along axis
            f_plus = torch.roll(field, -1, dims=axis)
            f_minus = torch.roll(field, 1, dims=axis)

            # Second derivative
            lapl += (f_plus - 2*field + f_minus) / (self.dx[axis]**2)

        return lapl

    def step(self, source_emissions: List[Tuple[tuple, float]]) -> None:
        """
        Advance one time step using leapfrog integration.

        VARIANT B: After each step, add current field state to sliding window.

        All operations on GPU for maximum speed.
        """
        # Compute Laplacian (GPU operation) - spatial only
        lapl = self.laplacian(self.A_curr)

        # Source term (build on GPU)
        J = torch.zeros_like(self.A_curr)
        for idx, amplitude in source_emissions:
            J[idx] += amplitude

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

        # VARIANT B: Add snapshot to sliding window
        self.sliding_window.add_snapshot(self.A_curr)

        # Update time
        self.t += self.dt
        self.step_count += 1

    def compute_salience(self, window_center: tuple = None, window_width: float = None) -> float:
        """
        Compute agent salience from GLOBAL field energy.

        VARIANT B: Integrates energy across the TEMPORAL WINDOW, not just current snapshot.

        GPU-accelerated energy integration over entire spatial domain across time.
        """
        # VARIANT B: Compute energy across temporal window
        temporal_energy = self.sliding_window.compute_temporal_energy()

        # Multiply by grid spacing (geometric mean of spatial dimensions)
        dx_mean = np.prod(self.dx) ** (1.0 / self.dim)
        salience = temporal_energy * dx_mean

        # Normalize by window size to make comparable to single-snapshot metrics
        # (otherwise salience scales linearly with window size)
        window_size = self.sliding_window.get_window_size()
        if window_size > 0:
            salience /= window_size

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
    Run one dimensional simulation on GPU with sliding window storage.

    VARIANT B: Physics is spatial-only, time is explicit in storage.

    Args:
        dimension: Spatial dimension (1-5)
        grid_sizes: Grid sizes for spatial dimensions only
        time_window_size: Size of temporal sliding window

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

    # Initialize GPU solver with sliding window
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
            'total_dimension': dimension,  # Same as spatial (time not in physics)
            'num_sources': config.num_sources,
            'alpha_0': alpha_0,
            'alpha_1': alpha_1,
            'gamma': gamma,
            'M': M,
            'T': T,
            'grid_sizes': grid_sizes,  # Spatial grid only
            'time_window_size': time_window_size,
            'variant': 'B_rendering',  # Mark as Variant B
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
    print("VARIANT B: Time as Rendering Dimension - GPU Wave Solver")
    print("=" * 80)
    print(f"Device: {DEVICE}")
    print(f"IPEX available: {IPEX_AVAILABLE}")

    # Test 2D with sliding window (time in storage, not physics)
    print("\nTesting 2D with sliding window (Variant B)...")
    config = create_symmetric_config_nd(1, 2, 1.0, 2.0)
    result = run_gpu_simulation(config, 2, (48, 48), 2.0, 0.0, 0.001, 1, 50.0,
                                time_window_size=10)
    if result:
        print(f"  Spatial dim: {result['parameters']['spatial_dimension']}")
        print(f"  Total dim (physics): {result['parameters']['total_dimension']}")
        print(f"  Time window size: {result['parameters']['time_window_size']}")
        print(f"  Commits: {result['statistics']['agent_commit_count']}")
        print(f"  Commit rate: {result['statistics']['commit_rate']:.4f}")
        print(f"  Note: Physics is {result['parameters']['spatial_dimension']}D, time only in storage")
    else:
        print("  2D test: CFL violated")

    # Test 3D with sliding window
    print("\nTesting 3D with sliding window (Variant B)...")
    config = create_symmetric_config_nd(1, 3, 1.0, 2.0)
    result = run_gpu_simulation(config, 3, (24, 24, 24), 2.0, 0.0, 0.001, 1, 50.0,
                                time_window_size=10)
    if result:
        print(f"  Spatial dim: {result['parameters']['spatial_dimension']}")
        print(f"  Total dim (physics): {result['parameters']['total_dimension']}")
        print(f"  Time window size: {result['parameters']['time_window_size']}")
        print(f"  Commits: {result['statistics']['agent_commit_count']}")
        print(f"  Commit rate: {result['statistics']['commit_rate']:.4f}")
        print(f"  Note: Physics is {result['parameters']['spatial_dimension']}D, time only in storage")
    else:
        print("  3D test: CFL violated")

    print("\n" + "=" * 80)
    print("Variant B GPU wave solver ready!")
    print("=" * 80)
