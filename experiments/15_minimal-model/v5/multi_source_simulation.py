"""
Multi-Source Time-Visualization Model
V5: Multiple emission sources with configurable geometry and phase

Based on V4 findings and Multi-Source Scenario Specification.md
"""

import math
import numpy as np
import json
import csv
from datetime import datetime

# -----------------------------
# Multi-source simulation framework
# -----------------------------

class MultiSourceConfig:
    """Configuration for multi-source emission setup."""

    def __init__(self, num_sources, positions, amplitudes, phases=None):
        """
        Args:
            num_sources: Number of emission sources
            positions: List of source positions in [0, L]
            amplitudes: List of emission amplitudes (can be functions of tick)
            phases: Optional list of phase offsets (in ticks)
        """
        self.num_sources = num_sources
        self.positions = np.array(positions)
        self.amplitudes = amplitudes
        self.phases = phases if phases is not None else [0] * num_sources

    def get_emissions(self, tick_count, x_state, alpha_0, alpha_1):
        """
        Get emission amplitudes for all sources at given tick.

        Returns:
            List of (position_index, amplitude) tuples
        """
        emissions = []
        for i in range(self.num_sources):
            # Check if this source emits at this tick (phase control)
            if (tick_count - self.phases[i]) % 1 == 0 and tick_count >= self.phases[i]:
                # Calculate amplitude
                if callable(self.amplitudes[i]):
                    amplitude = self.amplitudes[i](x_state, alpha_0, alpha_1)
                else:
                    amplitude = self.amplitudes[i]
                emissions.append((i, amplitude))
        return emissions

def create_symmetric_config(num_sources, L, alpha_0):
    """Create symmetrically distributed sources."""
    if num_sources == 1:
        positions = [L / 2.0]
    else:
        # Distribute evenly across domain
        positions = [L * (i + 1) / (num_sources + 1) for i in range(num_sources)]

    # Equal amplitudes
    amplitudes = [alpha_0] * num_sources

    return MultiSourceConfig(num_sources, positions, amplitudes)

def create_asymmetric_config(num_sources, L, alpha_0):
    """Create asymmetrically distributed sources (clustered)."""
    if num_sources == 1:
        positions = [L / 2.0]
    elif num_sources == 2:
        # Two sources close together
        positions = [0.4 * L, 0.6 * L]
    else:
        # Cluster in first half of domain
        positions = [0.3 * L + 0.2 * L * i / (num_sources - 1) for i in range(num_sources)]

    amplitudes = [alpha_0] * num_sources

    return MultiSourceConfig(num_sources, positions, amplitudes)

def create_phased_config(num_sources, L, alpha_0, phase_offset):
    """Create sources with alternating phase."""
    positions = [L * (i + 1) / (num_sources + 1) for i in range(num_sources)]
    amplitudes = [alpha_0] * num_sources
    phases = [i * phase_offset for i in range(num_sources)]

    return MultiSourceConfig(num_sources, positions, amplitudes, phases)

# -----------------------------
# Simulation functions
# -----------------------------

def linear_flow_step(x, A, b, dt):
    return x + dt * (A @ x + b)

def update_theta(Theta, omega_P, F_val, dt):
    return Theta + dt * (omega_P * F_val)

def emit_source_amplitude(x, alpha_0, alpha_1):
    return alpha_0 + alpha_1 * np.linalg.norm(x)

def wave_step_leapfrog_multi(A_curr, A_prev, dt, c, gamma, dx, source_emissions):
    """
    Wave step with multiple source emissions.

    Args:
        source_emissions: List of (grid_index, amplitude) tuples
    """
    Nx = len(A_curr)
    A_next = np.empty_like(A_curr)

    for i in range(Nx):
        if i == 0:
            u_xx = (A_curr[1] - A_curr[0]) / (dx**2)
        elif i == Nx - 1:
            u_xx = (A_curr[Nx - 2] - A_curr[Nx - 1]) / (dx**2)
        else:
            u_xx = (A_curr[i + 1] - 2.0 * A_curr[i] + A_curr[i - 1]) / (dx**2)

        # Sum contributions from all sources
        src = 0.0
        for src_idx, amplitude in source_emissions:
            if i == src_idx:
                src += amplitude

        u_t = (A_curr[i] - A_prev[i]) / dt
        A_next[i] = (2.0 * A_curr[i] - A_prev[i]
                     + (dt ** 2) * (c ** 2 * u_xx - gamma * u_t + src))

    return A_next

def agent_salience(A_field, dx):
    return float(np.sum(A_field ** 2) * dx)

# -----------------------------
# Run multi-source simulation
# -----------------------------

def run_multi_source_simulation(source_config, alpha_0, alpha_1, gamma, M, T,
                                 c=1.0, L=1.0, Nx=201, omega_P=1.0, delta=0.1,
                                 dt=0.005, epsilon=0.01):
    """
    Run simulation with multiple sources.

    Returns:
        Dictionary with simulation results
    """
    # Grid setup
    dx = L / (Nx - 1)

    # Convert source positions to grid indices
    src_indices = [int(round(pos / dx)) for pos in source_config.positions]

    # State initialization
    x = np.array([1.0, -0.5], dtype=float)
    Theta = 0.0
    n_threshold = 0.0
    tick_count = 0

    A_field = np.zeros(Nx, dtype=float)
    A_prev = np.zeros(Nx, dtype=float)
    A_prev[:] = A_field[:]

    # Agent accumulators
    Psi = 0.0
    agent_commit_count = 0
    first_commit_time = None
    commit_times = []

    # Track per-source emissions
    source_emission_counts = [0] * source_config.num_sources

    # CFL check
    cfl = c * dt / dx
    if cfl > 1.0:
        return None

    time = 0.0
    next_commit_threshold = n_threshold + 1.0 + delta

    max_salience = 0.0
    final_psi = 0.0

    while time < T:
        # Root substrate step
        x = linear_flow_step(x, np.array([[-0.1, 0.0], [0.0, -0.1]]),
                           np.array([0.0, 0.0]), dt)

        # Tick generator
        F_val = 1.0
        Theta = update_theta(Theta, omega_P, F_val, dt)

        # PoF commit check
        source_emissions = []
        if Theta >= next_commit_threshold:
            tick_count += 1
            commit_time = time

            # Get emissions from all active sources
            emissions_list = source_config.get_emissions(tick_count, x, alpha_0, alpha_1)

            for src_num, amplitude in emissions_list:
                source_emissions.append((src_indices[src_num], amplitude))
                source_emission_counts[src_num] += 1

            # Advance threshold
            n_threshold += 1.0
            next_commit_threshold = n_threshold + 1.0 + delta

            # Agent subset rule
            if tick_count % M == 0:
                S = agent_salience(A_field, dx)
                max_salience = max(max_salience, S)
                Psi += S * 1.0

                if Psi >= 1.0 + epsilon:
                    agent_commit_count += 1
                    commit_times.append(commit_time)
                    if first_commit_time is None:
                        first_commit_time = commit_time
                    Psi = 0.0

        # Wave field step with multi-source
        A_next = wave_step_leapfrog_multi(A_field, A_prev, dt, c, gamma, dx, source_emissions)

        A_prev[:] = A_field[:]
        A_field[:] = A_next[:]

        time += dt

    final_psi = Psi
    commit_rate = agent_commit_count / T if T > 0 else 0.0

    return {
        "parameters": {
            "num_sources": source_config.num_sources,
            "alpha_0": float(alpha_0),
            "gamma": float(gamma),
            "M": int(M),
            "T": float(T)
        },
        "statistics": {
            "tick_count": tick_count,
            "agent_commit_count": agent_commit_count,
            "first_commit_time": float(first_commit_time) if first_commit_time else None,
            "commit_rate": float(commit_rate),
            "max_salience": float(max_salience),
            "final_psi": float(final_psi),
            "has_commits": agent_commit_count > 0,
            "source_emission_counts": source_emission_counts
        },
        "commit_times": commit_times[:100]
    }

# -----------------------------
# Test function
# -----------------------------

if __name__ == "__main__":
    print("=" * 80)
    print("MULTI-SOURCE SIMULATION FRAMEWORK TEST")
    print("=" * 80)

    # Test configurations
    L = 1.0

    print("\nTest 1: Single source (baseline)")
    config = create_symmetric_config(1, L, 2.0)
    result = run_multi_source_simulation(config, 2.0, 0.0, 0.001, 1, 100.0)
    if result:
        print(f"  Commits: {result['statistics']['agent_commit_count']}")
        print(f"  Rate: {result['statistics']['commit_rate']:.4f}")

    print("\nTest 2: Two symmetric sources")
    config = create_symmetric_config(2, L, 1.5)
    result = run_multi_source_simulation(config, 1.5, 0.0, 0.001, 1, 100.0)
    if result:
        print(f"  Commits: {result['statistics']['agent_commit_count']}")
        print(f"  Rate: {result['statistics']['commit_rate']:.4f}")
        print(f"  Source emissions: {result['statistics']['source_emission_counts']}")

    print("\nTest 3: Four symmetric sources")
    config = create_symmetric_config(4, L, 1.0)
    result = run_multi_source_simulation(config, 1.0, 0.0, 0.001, 1, 100.0)
    if result:
        print(f"  Commits: {result['statistics']['agent_commit_count']}")
        print(f"  Rate: {result['statistics']['commit_rate']:.4f}")
        print(f"  Source emissions: {result['statistics']['source_emission_counts']}")

    print("\n" + "=" * 80)
    print("Framework test complete!")
