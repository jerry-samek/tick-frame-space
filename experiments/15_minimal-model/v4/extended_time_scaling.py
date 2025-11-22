"""
Extended Time Horizon: Commit Scaling Analysis

Tests how commit count scales with simulation time for α₀ above threshold.

Key question: Do commits grow linearly (constant rate) or show saturation/acceleration?
"""

import math
import numpy as np
import json
import csv
from datetime import datetime

# -----------------------------
# Scaling test parameters
# -----------------------------
# Test α₀ values well above threshold
alpha_0_values = [2.0, 3.0, 5.0, 10.0]
alpha_1 = 0.0

# Multiple time horizons
time_horizons = [100.0, 200.0, 500.0]

# Optimal parameters
gamma = 0.001
M = 1

# Fixed parameters
A = np.array([[-0.1, 0.0],
              [0.0, -0.1]], dtype=float)
b = np.array([0.0, 0.0], dtype=float)

omega_P = 1.0
delta = 0.1
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
# Helper functions (same as threshold test)
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
# Run simulation
# -----------------------------
def run_simulation(alpha_0, alpha_1, gamma, M, T):
    """Run simulation and track commit statistics."""

    x = np.array([1.0, -0.5], dtype=float)
    Theta = 0.0
    n_threshold = 0.0
    tick_count = 0

    A_field = np.zeros(Nx, dtype=float)
    A_prev = np.zeros(Nx, dtype=float)
    A_prev[:] = A_field[:]

    Psi = 0.0
    agent_commit_count = 0
    first_commit_time = None
    last_commit_time = None
    commit_times = []

    cfl = c * dt / dx
    if cfl > 1.0:
        return None

    time = 0.0
    next_commit_threshold = n_threshold + 1.0 + delta

    while time < T:
        x = linear_flow_step(x, A, b, dt)
        F_val = 1.0
        Theta = update_theta(Theta, omega_P, F_val, dt)

        emitted_source_impulse = 0.0
        if Theta >= next_commit_threshold:
            tick_count += 1
            commit_time = time

            q_n = emit_source_amplitude(x, alpha_0, alpha_1)
            emitted_source_impulse = q_n

            n_threshold += 1.0
            next_commit_threshold = n_threshold + 1.0 + delta

            if tick_count % M == 0:
                S = agent_salience(A_field, dx)
                Psi += S * 1.0

                if Psi >= 1.0 + epsilon:
                    agent_commit_count += 1
                    commit_times.append(commit_time)
                    if first_commit_time is None:
                        first_commit_time = commit_time
                    last_commit_time = commit_time
                    Psi = 0.0

        A_next = wave_step_leapfrog(A_field, A_prev, dt, c, gamma, dx, src_idx, emitted_source_impulse)
        A_prev[:] = A_field[:]
        A_field[:] = A_next[:]
        time += dt

    # Calculate metrics
    commit_rate = agent_commit_count / T if T > 0 else 0.0

    # Average inter-commit interval
    if len(commit_times) > 1:
        intervals = np.diff(commit_times)
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
    else:
        avg_interval = None
        std_interval = None

    return {
        "parameters": {
            "alpha_0": float(alpha_0),
            "T": float(T)
        },
        "statistics": {
            "tick_count": tick_count,
            "agent_commit_count": agent_commit_count,
            "first_commit_time": float(first_commit_time) if first_commit_time else None,
            "last_commit_time": float(last_commit_time) if last_commit_time else None,
            "commit_rate": float(commit_rate),
            "avg_commit_interval": float(avg_interval) if avg_interval else None,
            "std_commit_interval": float(std_interval) if std_interval else None
        }
    }

# -----------------------------
# Main analysis
# -----------------------------
print("=" * 80)
print("EXTENDED TIME HORIZON: COMMIT SCALING ANALYSIS")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nResearch question: How do commits scale with simulation time?")
print(f"\nTest parameters:")
print(f"  alpha_0 values: {alpha_0_values}")
print(f"  Time horizons: {time_horizons}s")
print(f"  Fixed: gamma={gamma:.4f}, M={M}")
print(f"\nTotal runs: {len(alpha_0_values) * len(time_horizons)}")
print("=" * 80)

results = []

for alpha_0 in alpha_0_values:
    print(f"\n{'='*70}")
    print(f"alpha_0 = {alpha_0:.2f}")
    print(f"{'='*70}")

    for T in time_horizons:
        print(f"\n  T = {T:.0f}s:")

        result = run_simulation(alpha_0, alpha_1, gamma, M, T)

        if result is None:
            print(f"    SKIPPED: CFL violation")
            continue

        results.append(result)
        stats = result['statistics']

        print(f"    Total commits: {stats['agent_commit_count']}")
        print(f"    Commit rate: {stats['commit_rate']:.6f} commits/s")
        if stats['first_commit_time']:
            print(f"    First commit: t={stats['first_commit_time']:.1f}s")
            print(f"    Last commit: t={stats['last_commit_time']:.1f}s")
        if stats['avg_commit_interval']:
            std_str = f"{stats['std_commit_interval']:.1f}" if stats['std_commit_interval'] else "N/A"
            print(f"    Avg interval: {stats['avg_commit_interval']:.1f}s (+/- {std_str}s)")

# -----------------------------
# Save results
# -----------------------------
print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

json_file = "extended_time_scaling_results.json"
with open(json_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Full results saved to: {json_file}")

csv_file = "extended_time_scaling_results.csv"
with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'alpha_0', 'T', 'agent_commit_count', 'commit_rate',
        'first_commit_time', 'last_commit_time',
        'avg_commit_interval', 'std_commit_interval'
    ])
    writer.writeheader()
    for r in results:
        p = r['parameters']
        s = r['statistics']
        writer.writerow({
            'alpha_0': p['alpha_0'],
            'T': p['T'],
            'agent_commit_count': s['agent_commit_count'],
            'commit_rate': s['commit_rate'],
            'first_commit_time': s['first_commit_time'] if s['first_commit_time'] else '',
            'last_commit_time': s['last_commit_time'] if s['last_commit_time'] else '',
            'avg_commit_interval': s['avg_commit_interval'] if s['avg_commit_interval'] else '',
            'std_commit_interval': s['std_commit_interval'] if s['std_commit_interval'] else ''
        })
print(f"CSV data saved to: {csv_file}")

# -----------------------------
# Scaling Analysis
# -----------------------------
print("\n" + "=" * 80)
print("COMMIT SCALING ANALYSIS")
print("=" * 80)

print("\nCommit counts vs. time horizon:")
print(f"{'alpha_0':<10} {'T=100s':<15} {'T=200s':<15} {'T=500s':<15}")
print("-" * 60)

for alpha_0 in alpha_0_values:
    row_data = [alpha_0]
    for T in time_horizons:
        matching = [r for r in results
                   if r['parameters']['alpha_0'] == alpha_0
                   and r['parameters']['T'] == T]
        if matching:
            count = matching[0]['statistics']['agent_commit_count']
            row_data.append(f"{count}")
        else:
            row_data.append("---")
    print(f"{row_data[0]:<10.2f} {row_data[1]:<15s} {row_data[2]:<15s} {row_data[3]:<15s}")

print("\n" + "=" * 80)
print("SCALING LAW ANALYSIS")
print("=" * 80)

# For each alpha_0, fit N_commits = A * T^beta
for alpha_0 in alpha_0_values:
    print(f"\nalpha_0 = {alpha_0:.2f}:")

    # Extract data for this alpha_0
    data_for_alpha = [r for r in results if r['parameters']['alpha_0'] == alpha_0]
    if len(data_for_alpha) < 2:
        print("  Insufficient data for scaling fit")
        continue

    times = np.array([r['parameters']['T'] for r in data_for_alpha])
    counts = np.array([r['statistics']['agent_commit_count'] for r in data_for_alpha])

    # Fit power law: N ~ T^beta
    if np.all(counts > 0):
        log_times = np.log(times)
        log_counts = np.log(counts)
        coeffs = np.polyfit(log_times, log_counts, 1)
        beta = coeffs[0]
        log_A = coeffs[1]
        A = np.exp(log_A)

        print(f"  Scaling: N_commits ~ {A:.3f} * T^{beta:.3f}")

        if abs(beta - 1.0) < 0.1:
            print(f"  Interpretation: LINEAR scaling (constant commit rate)")
        elif beta < 0.9:
            print(f"  Interpretation: SUBLINEAR scaling (saturation)")
        else:
            print(f"  Interpretation: SUPERLINEAR scaling (acceleration)")

        # Calculate R^2
        predicted = A * (times ** beta)
        residuals = counts - predicted
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((counts - np.mean(counts)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        print(f"  Fit quality: R^2 = {r_squared:.4f}")
    else:
        print("  Contains zero commits, cannot fit power law")

print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
