"""
Lower threshold search: Finding where commits stop appearing.
Testing values between 10 and 50.
"""

import math
import numpy as np
import json
from datetime import datetime

# -----------------------------
# Lower threshold sweep
# -----------------------------
alpha_0_values = [10.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]
alpha_1_values = [0.0]
gamma_values = [0.001]
M_values = [1]

# Fixed parameters
A = np.array([[-0.1, 0.0],
              [0.0, -0.1]], dtype=float)
b = np.array([0.0, 0.0], dtype=float)

omega_P = 1.0
delta = 0.1
T = 100.0
dt = 0.005

# Wave field parameters
c = 1.0
L = 1.0
Nx = 201
dx = L / (Nx - 1)
source_pos = 0.5
src_idx = int(round(source_pos / dx))

# Agent parameters
epsilon = 0.01

# -----------------------------
# Helper functions
# -----------------------------
def linear_flow_step(x, A, b, dt):
    return x + dt * (A @ x + b)

def update_theta(Theta, omega_P, F_val, dt):
    return Theta + dt * (omega_P * F_val)

def emit_source_amplitude(x, alpha_0, alpha_1):
    return alpha_0 + alpha_1 * np.linalg.norm(x)

def wave_step_leapfrog(A_curr, A_prev, dt, c, gamma, dx, src_idx, source_impulse):
    Nx = len(A_curr)
    A_next = np.empty_like(A_curr)

    for i in range(Nx):
        if i == 0:
            u_xx = (A_curr[1] - A_curr[0]) / (dx**2)
        elif i == Nx - 1:
            u_xx = (A_curr[Nx - 2] - A_curr[Nx - 1]) / (dx**2)
        else:
            u_xx = (A_curr[i + 1] - 2.0 * A_curr[i] + A_curr[i - 1]) / (dx**2)

        src = source_impulse if i == src_idx else 0.0
        u_t = (A_curr[i] - A_prev[i]) / dt
        A_next[i] = (2.0 * A_curr[i] - A_prev[i]
                     + (dt ** 2) * (c ** 2 * u_xx - gamma * u_t + src))

    return A_next

def agent_salience(A_field, dx):
    return float(np.sum(A_field ** 2) * dx)

# -----------------------------
# Run single simulation
# -----------------------------
def run_simulation(alpha_0, alpha_1, gamma, M):
    """Run simulation with given parameters and return summary statistics."""

    # State initialization
    x = np.array([1.0, -0.5], dtype=float)
    Theta = 0.0
    n_threshold = 0.0
    tick_count = 0

    A_field = np.zeros(Nx, dtype=float)
    A_prev = np.zeros(Nx, dtype=float)
    A_next = np.zeros(Nx, dtype=float)
    A_prev[:] = A_field[:]

    # Agent accumulators
    Psi = 0.0
    agent_commit_count = 0
    first_commit_time = None

    # CFL check
    cfl = c * dt / dx
    if cfl > 1.0:
        return None

    time = 0.0
    next_commit_threshold = n_threshold + 1.0 + delta

    max_salience = 0.0
    salience_history = []

    while time < T:
        # Root substrate step
        x = linear_flow_step(x, A, b, dt)

        # Tick generator
        F_val = 1.0
        Theta = update_theta(Theta, omega_P, F_val, dt)

        # PoF commit check
        emitted_source_impulse = 0.0
        if Theta >= next_commit_threshold:
            tick_count += 1
            commit_time = time

            # Emission
            q_n = emit_source_amplitude(x, alpha_0, alpha_1)
            emitted_source_impulse = q_n

            # Advance threshold
            n_threshold += 1.0
            next_commit_threshold = n_threshold + 1.0 + delta

            # Agent subset rule
            if tick_count % M == 0:
                S = agent_salience(A_field, dx)
                max_salience = max(max_salience, S)
                salience_history.append(S)
                Psi += S * 1.0

                if Psi >= 1.0 + epsilon:
                    agent_commit_count += 1
                    if first_commit_time is None:
                        first_commit_time = commit_time
                    Psi = 0.0

        # Wave field step
        A_next = wave_step_leapfrog(A_field, A_prev, dt, c, gamma, dx, src_idx, emitted_source_impulse)

        A_prev[:] = A_field[:]
        A_field[:] = A_next[:]

        time += dt

    # Calculate statistics
    avg_salience = np.mean(salience_history) if salience_history else 0.0

    return {
        "parameters": {
            "alpha_0": alpha_0,
        },
        "statistics": {
            "tick_count": tick_count,
            "agent_commit_count": agent_commit_count,
            "first_commit_time": first_commit_time,
            "max_salience": float(max_salience),
            "avg_salience": float(avg_salience),
        }
    }

# -----------------------------
# Main sweep
# -----------------------------
print("=" * 80)
print("LOWER THRESHOLD SEARCH")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nSearching for where commits STOP appearing...")
print(f"Testing alpha_0 values: {alpha_0_values}")
print(f"Simulation time: T={T}s, gamma=0.001, M=1")
print("=" * 80)

results = []

for alpha_0 in alpha_0_values:
    for alpha_1 in alpha_1_values:
        for gamma in gamma_values:
            for M in M_values:
                result = run_simulation(alpha_0, alpha_1, gamma, M)

                if result is None:
                    print(f"alpha_0={alpha_0:5.1f}: SKIPPED (CFL violation)")
                    continue

                results.append(result)
                stats = result['statistics']

                if stats['agent_commit_count'] > 0:
                    print(f"alpha_0={alpha_0:5.1f}: COMMITS={stats['agent_commit_count']:3d}, "
                          f"first_at t={stats['first_commit_time']:6.3f}s, "
                          f"max_sal={stats['max_salience']:8.4f}")
                else:
                    print(f"alpha_0={alpha_0:5.1f}: NO COMMITS, "
                          f"max_sal={stats['max_salience']:8.4f}")

# -----------------------------
# Summary
# -----------------------------
print("\n" + "=" * 80)
print("THRESHOLD ANALYSIS")
print("=" * 80)

runs_with_commits = [r for r in results if r['statistics']['agent_commit_count'] > 0]
runs_without_commits = [r for r in results if r['statistics']['agent_commit_count'] == 0]

if runs_without_commits and runs_with_commits:
    max_no_commit = max(r['parameters']['alpha_0'] for r in runs_without_commits)
    min_with_commit = min(r['parameters']['alpha_0'] for r in runs_with_commits)
    print(f"\nCRITICAL THRESHOLD IDENTIFIED:")
    print(f"  No commits: alpha_0 <= {max_no_commit:.1f}")
    print(f"  Commits:    alpha_0 >= {min_with_commit:.1f}")
    print(f"\n  => THRESHOLD is between {max_no_commit:.1f} and {min_with_commit:.1f}")
    print(f"\nFor the tested parameters (gamma=0.001, M=1, T=100s):")
    print(f"  - Artefacts with alpha_0 > {max_no_commit:.1f} are strong enough to be detected")
    print(f"  - Artefacts with alpha_0 <= {max_no_commit:.1f} dissipate before reaching threshold")
elif runs_with_commits:
    min_with_commit = min(r['parameters']['alpha_0'] for r in runs_with_commits)
    print(f"\nAll tested values produced commits.")
    print(f"  Minimum tested: alpha_0 = {min_with_commit:.1f}")
    print(f"  Threshold is below {min_with_commit:.1f}")
else:
    max_no_commit = max(r['parameters']['alpha_0'] for r in runs_without_commits)
    print(f"\nNo commits found in any configuration.")
    print(f"  Maximum tested: alpha_0 = {max_no_commit:.1f}")
    print(f"  Threshold is above {max_no_commit:.1f}")

# Save results
output_file = "parameter_sweep_lower_threshold_results.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to: {output_file}")

print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
