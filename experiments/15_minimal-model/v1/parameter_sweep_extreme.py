"""
Extreme parameter sweep - searching for the threshold where agent commits appear.
Strategy: Longer simulation time + extremely high emission strengths
"""

import math
import numpy as np
import json
from datetime import datetime

# -----------------------------
# Extreme parameter sweep
# -----------------------------
alpha_0_values = [100.0, 200.0, 500.0, 1000.0, 2000.0]
alpha_1_values = [0.0]
gamma_values = [0.001]
M_values = [1]

# Fixed parameters
A = np.array([[-0.1, 0.0],
              [0.0, -0.1]], dtype=float)
b = np.array([0.0, 0.0], dtype=float)

omega_P = 1.0
delta = 0.1
T = 100.0  # Much longer simulation time
dt = 0.005
N_steps = int(T / dt)

# Wave field parameters
c = 1.0
L = 1.0
Nx = 201
dx = L / (Nx - 1)
xgrid = np.linspace(0.0, L, Nx)
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
def run_simulation(alpha_0, alpha_1, gamma, M, verbose=False):
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

    # Logs
    tick_log = []
    emission_log = []
    agent_log = []

    # Agent accumulators
    Psi = 0.0
    agent_frame_count = 0
    agent_commit_count = 0

    # CFL check
    cfl = c * dt / dx
    if cfl > 1.0:
        return None  # Skip unstable configuration

    time = 0.0
    next_commit_threshold = n_threshold + 1.0 + delta

    max_salience = 0.0
    total_emission_strength = 0.0
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

            tick_log.append({
                "TickID": tick_count,
                "time": commit_time,
                "Theta": float(Theta),
            })

            # Emission
            q_n = emit_source_amplitude(x, alpha_0, alpha_1)
            emitted_source_impulse = q_n
            total_emission_strength += q_n
            emission_log.append({
                "TickID": tick_count,
                "time": commit_time,
                "strength": float(q_n)
            })

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
                    agent_frame_count += 1
                    agent_commit_count += 1
                    agent_log.append({
                        "FrameID": agent_frame_count,
                        "time": commit_time,
                        "Psi": float(Psi),
                        "Salience": float(S),
                        "Mode": "COMMIT"
                    })
                    if verbose or agent_commit_count == 1:
                        print(f"    [AGENT COMMIT #{agent_commit_count}!] t={commit_time:.3f} Psi={Psi:.6f} S={S:.6f}")
                    Psi = 0.0
                else:
                    agent_log.append({
                        "FrameID": agent_frame_count,
                        "time": commit_time,
                        "Psi": float(Psi),
                        "Salience": float(S),
                        "Mode": "REPEAT"
                    })

        # Wave field step
        A_next = wave_step_leapfrog(A_field, A_prev, dt, c, gamma, dx, src_idx, emitted_source_impulse)

        A_prev[:] = A_field[:]
        A_field[:] = A_next[:]

        time += dt

    # Calculate statistics
    avg_emission = total_emission_strength / tick_count if tick_count > 0 else 0.0
    avg_salience = np.mean(salience_history) if salience_history else 0.0

    return {
        "parameters": {
            "alpha_0": alpha_0,
            "alpha_1": alpha_1,
            "gamma": gamma,
            "M": M
        },
        "statistics": {
            "tick_count": tick_count,
            "agent_percept_count": len(agent_log),
            "agent_commit_count": agent_commit_count,
            "avg_emission_strength": float(avg_emission),
            "max_salience": float(max_salience),
            "avg_salience": float(avg_salience),
            "cfl": float(cfl)
        },
        "agent_log": agent_log[:100]  # Only save first 100 to keep file size reasonable
    }

# -----------------------------
# Main sweep
# -----------------------------
print("=" * 80)
print("EXTREME PARAMETER SWEEP - SEARCHING FOR AGENT COMMITS")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nStrategy: T={T}s (long simulation) + very high alpha_0")
print(f"\nParameter ranges:")
print(f"  alpha_0: {alpha_0_values}")
print(f"  alpha_1: {alpha_1_values}")
print(f"  gamma:   {gamma_values}")
print(f"  M:       {M_values}")
print(f"\nTotal combinations: {len(alpha_0_values) * len(alpha_1_values) * len(gamma_values) * len(M_values)}")
print("=" * 80)

results = []
run_number = 0
first_commit_found = False

for alpha_0 in alpha_0_values:
    for alpha_1 in alpha_1_values:
        for gamma in gamma_values:
            for M in M_values:
                run_number += 1
                print(f"\n[Run {run_number:03d}] a0={alpha_0:7.1f} a1={alpha_1:5.1f} g={gamma:.4f} M={M}")

                verbose = not first_commit_found

                result = run_simulation(alpha_0, alpha_1, gamma, M, verbose=verbose)

                if result is None:
                    print("  SKIPPED: CFL violation")
                    continue

                results.append(result)
                stats = result['statistics']

                print(f"  Ticks: {stats['tick_count']:3d}")
                print(f"  Agent percepts: {stats['agent_percept_count']:3d}")
                print(f"  Agent COMMITS: {stats['agent_commit_count']:3d} {'***' if stats['agent_commit_count'] > 0 else ''}")
                print(f"  Max salience: {stats['max_salience']:.6f}")
                print(f"  Avg salience: {stats['avg_salience']:.6f}")
                print(f"  Avg emission: {stats['avg_emission_strength']:.3f}")

                if stats['agent_commit_count'] > 0 and not first_commit_found:
                    first_commit_found = True
                    print(f"\n>>> FIRST AGENT COMMIT FOUND! <<<")
                    print(f"    Parameters: alpha_0={alpha_0}, alpha_1={alpha_1}, gamma={gamma}, M={M}")

# -----------------------------
# Summary and save results
# -----------------------------
print("\n" + "=" * 80)
print("SWEEP COMPLETE")
print("=" * 80)

# Count runs with agent commits
runs_with_commits = [r for r in results if r['statistics']['agent_commit_count'] > 0]
print(f"\nRuns with agent commits: {len(runs_with_commits)} / {len(results)}")

if runs_with_commits:
    print("\n" + "=" * 80)
    print("CONFIGURATIONS THAT PRODUCED AGENT COMMITS:")
    print("=" * 80)
    for result in runs_with_commits:
        p = result['parameters']
        s = result['statistics']
        print(f"  a0={p['alpha_0']:7.1f}, a1={p['alpha_1']:5.1f}, g={p['gamma']:.4f}, M={p['M']} "
              f"-> {s['agent_commit_count']} commits (max_sal={s['max_salience']:.6f}, avg_sal={s['avg_salience']:.6f})")

# Save results to JSON
output_file = "parameter_sweep_extreme_results.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nFull results saved to: {output_file}")

print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
