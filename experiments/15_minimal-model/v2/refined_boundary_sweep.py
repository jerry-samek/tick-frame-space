"""
Refined boundary sweep: High-resolution mapping of the onset curve.
Focus: α₀ ∈ [1.6, 2.2] with fine granularity
Varies: gamma, M to map the 2D threshold surface
"""

import math
import numpy as np
import json
import csv
from datetime import datetime

# -----------------------------
# Refined parameter ranges
# -----------------------------
# Fine-grained alpha_0 sweep around the critical threshold
alpha_0_values = np.arange(1.6, 2.21, 0.05)  # 1.6, 1.65, 1.70, ..., 2.20
alpha_1_values = [0.0]  # Keep fixed for now

# Test multiple damping values to see how threshold shifts
gamma_values = [0.01, 0.005, 0.001, 0.0005]

# Test multiple sampling factors
M_values = [1, 2, 4]

# Fixed parameters
A = np.array([[-0.1, 0.0],
              [0.0, -0.1]], dtype=float)
b = np.array([0.0, 0.0], dtype=float)

omega_P = 1.0
delta = 0.1
T = 100.0  # Long simulation to catch late commits
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
    """Run simulation and return key statistics."""

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
    first_commit_tick = None

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
                        first_commit_tick = tick_count
                    Psi = 0.0

        # Wave field step
        A_next = wave_step_leapfrog(A_field, A_prev, dt, c, gamma, dx, src_idx, emitted_source_impulse)

        A_prev[:] = A_field[:]
        A_field[:] = A_next[:]

        time += dt

    # Calculate statistics
    avg_salience = np.mean(salience_history) if salience_history else 0.0
    final_psi = Psi  # Accumulated salience at end

    return {
        "parameters": {
            "alpha_0": float(alpha_0),
            "alpha_1": float(alpha_1),
            "gamma": float(gamma),
            "M": int(M)
        },
        "statistics": {
            "tick_count": tick_count,
            "agent_commit_count": agent_commit_count,
            "first_commit_time": float(first_commit_time) if first_commit_time else None,
            "first_commit_tick": int(first_commit_tick) if first_commit_tick else None,
            "max_salience": float(max_salience),
            "avg_salience": float(avg_salience),
            "final_psi": float(final_psi),
            "has_commits": agent_commit_count > 0
        }
    }

# -----------------------------
# Main sweep
# -----------------------------
print("=" * 80)
print("REFINED BOUNDARY SWEEP - HIGH RESOLUTION ONSET CURVE")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nFocused region: alpha_0 in [{alpha_0_values[0]:.2f}, {alpha_0_values[-1]:.2f}]")
print(f"Resolution: delta_alpha_0 = {alpha_0_values[1] - alpha_0_values[0]:.3f}")
print(f"\nParameter ranges:")
print(f"  alpha_0: {len(alpha_0_values)} values from {alpha_0_values[0]:.2f} to {alpha_0_values[-1]:.2f}")
print(f"  gamma:   {gamma_values}")
print(f"  M:       {M_values}")
print(f"\nTotal combinations: {len(alpha_0_values) * len(gamma_values) * len(M_values)}")
print("=" * 80)

results = []
run_number = 0
total_runs = len(alpha_0_values) * len(alpha_1_values) * len(gamma_values) * len(M_values)

# Progress tracking
commits_found = {}  # Track first commit for each (gamma, M) combo

for gamma in gamma_values:
    for M in M_values:
        print(f"\n--- gamma={gamma:.4f}, M={M} ---")
        first_commit_alpha = None

        for alpha_0 in alpha_0_values:
            for alpha_1 in alpha_1_values:
                run_number += 1

                result = run_simulation(alpha_0, alpha_1, gamma, M)

                if result is None:
                    print(f"  α₀={alpha_0:.2f}: SKIPPED (CFL violation)")
                    continue

                results.append(result)
                stats = result['statistics']

                # Track threshold crossing
                if stats['has_commits'] and first_commit_alpha is None:
                    first_commit_alpha = alpha_0
                    commits_found[(gamma, M)] = alpha_0
                    print(f"  a0={alpha_0:.2f}: *** ONSET *** (first commit at t={stats['first_commit_time']:.3f}s)")
                elif stats['has_commits']:
                    print(f"  a0={alpha_0:.2f}: {stats['agent_commit_count']:2d} commits, max_sal={stats['max_salience']:.6f}")
                else:
                    print(f"  a0={alpha_0:.2f}: no commits, max_sal={stats['max_salience']:.6f}, final_Psi={stats['final_psi']:.6f}")

        # Summary for this (gamma, M) combination
        if first_commit_alpha is not None:
            print(f"  -> Threshold for (gamma={gamma:.4f}, M={M}): alpha_0 ~= {first_commit_alpha:.2f}")
        else:
            print(f"  -> No commits found for (gamma={gamma:.4f}, M={M})")

# -----------------------------
# Save results
# -----------------------------
print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save full JSON
json_file = "refined_boundary_results.json"
with open(json_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Full results saved to: {json_file}")

# Save CSV for easy analysis
csv_file = "refined_boundary_results.csv"
with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'alpha_0', 'gamma', 'M',
        'has_commits', 'agent_commit_count', 'first_commit_time', 'first_commit_tick',
        'max_salience', 'avg_salience', 'final_psi'
    ])
    writer.writeheader()
    for r in results:
        p = r['parameters']
        s = r['statistics']
        writer.writerow({
            'alpha_0': p['alpha_0'],
            'gamma': p['gamma'],
            'M': p['M'],
            'has_commits': s['has_commits'],
            'agent_commit_count': s['agent_commit_count'],
            'first_commit_time': s['first_commit_time'] if s['first_commit_time'] else '',
            'first_commit_tick': s['first_commit_tick'] if s['first_commit_tick'] else '',
            'max_salience': s['max_salience'],
            'avg_salience': s['avg_salience'],
            'final_psi': s['final_psi']
        })
print(f"CSV data saved to: {csv_file}")

# -----------------------------
# Threshold summary
# -----------------------------
print("\n" + "=" * 80)
print("THRESHOLD SUMMARY")
print("=" * 80)

print("\nOnset thresholds for each (gamma, M) configuration:")
print(f"{'gamma':<10} {'M':<5} {'Threshold a0':<15} {'Notes'}")
print("-" * 60)

for gamma in gamma_values:
    for M in M_values:
        key = (gamma, M)
        if key in commits_found:
            threshold = commits_found[key]
            print(f"{gamma:<10.4f} {M:<5d} {threshold:<15.2f} First commit observed")
        else:
            print(f"{gamma:<10.4f} {M:<5d} {'>':<15s}{alpha_0_values[-1]:.2f} No commits in tested range")

# Find trend: does threshold decrease with lower damping?
print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)

print("\nEffect of damping (gamma) on threshold (for M=1):")
m1_thresholds = [(g, commits_found.get((g, 1), None)) for g in gamma_values]
for g, t in m1_thresholds:
    if t:
        print(f"  gamma={g:.4f} -> threshold alpha_0 ~= {t:.2f}")
    else:
        print(f"  gamma={g:.4f} -> threshold > {alpha_0_values[-1]:.2f}")

print("\nEffect of sampling (M) on threshold (for gamma=0.001):")
gamma_001_thresholds = [(m, commits_found.get((0.001, m), None)) for m in M_values]
for m, t in gamma_001_thresholds:
    if t:
        print(f"  M={m} -> threshold alpha_0 ~= {t:.2f}")
    else:
        print(f"  M={m} -> threshold > {alpha_0_values[-1]:.2f}")

print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
