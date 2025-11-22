"""
Extended Time Horizon: Threshold Stability Analysis

Tests whether the critical α₀ threshold shifts with longer simulation times.

Key question: Is the threshold time-invariant or time-dependent?
"""

import math
import numpy as np
import json
import csv
from datetime import datetime

# -----------------------------
# Extended time test parameters
# -----------------------------
# Test α₀ values around the known threshold
alpha_0_values = [1.88, 1.89, 1.90, 1.91, 1.92]
alpha_1 = 0.0

# Multiple time horizons
time_horizons = [100.0, 200.0, 500.0]

# Optimal parameters from v3
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
# Run simulation with extended time
# -----------------------------
def run_simulation(alpha_0, alpha_1, gamma, M, T):
    """Run simulation for time T and return commit statistics."""

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
    commit_times = []

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
                Psi += S * 1.0

                if Psi >= 1.0 + epsilon:
                    agent_commit_count += 1
                    commit_times.append(commit_time)
                    if first_commit_time is None:
                        first_commit_time = commit_time
                        first_commit_tick = tick_count
                    Psi = 0.0

        # Wave field step
        A_next = wave_step_leapfrog(A_field, A_prev, dt, c, gamma, dx, src_idx, emitted_source_impulse)

        A_prev[:] = A_field[:]
        A_field[:] = A_next[:]

        time += dt

    final_psi = Psi

    # Calculate commit rate
    commit_rate = agent_commit_count / T if T > 0 else 0.0

    return {
        "parameters": {
            "alpha_0": float(alpha_0),
            "gamma": float(gamma),
            "M": int(M),
            "T": float(T)
        },
        "statistics": {
            "tick_count": tick_count,
            "agent_commit_count": agent_commit_count,
            "first_commit_time": float(first_commit_time) if first_commit_time else None,
            "first_commit_tick": int(first_commit_tick) if first_commit_tick else None,
            "commit_rate": float(commit_rate),
            "max_salience": float(max_salience),
            "final_psi": float(final_psi),
            "has_commits": agent_commit_count > 0
        },
        "commit_times": commit_times[:100]  # Limit to first 100 to save space
    }

# -----------------------------
# Main analysis
# -----------------------------
print("=" * 80)
print("EXTENDED TIME HORIZON: THRESHOLD STABILITY ANALYSIS")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nResearch question: Does threshold shift with longer simulation time?")
print(f"\nTest parameters:")
print(f"  alpha_0 values: {alpha_0_values}")
print(f"  Time horizons: {time_horizons}s")
print(f"  Fixed: gamma={gamma:.4f}, M={M}")
print(f"\nTotal runs: {len(alpha_0_values) * len(time_horizons)}")
print("=" * 80)

results = []
thresholds_by_time = {}

for T in time_horizons:
    print(f"\n{'='*70}")
    print(f"TIME HORIZON: T = {T:.0f}s")
    print(f"{'='*70}")

    first_commit_alpha = None
    last_no_commit_alpha = None

    for alpha_0 in alpha_0_values:
        print(f"\n  Testing alpha_0 = {alpha_0:.2f}...")

        result = run_simulation(alpha_0, alpha_1, gamma, M, T)

        if result is None:
            print(f"    SKIPPED: CFL violation")
            continue

        results.append(result)
        stats = result['statistics']

        if stats['has_commits']:
            if first_commit_alpha is None:
                first_commit_alpha = alpha_0
                print(f"    *** THRESHOLD CROSSED ***")
                print(f"    First commit at: t={stats['first_commit_time']:.3f}s (tick {stats['first_commit_tick']})")
                print(f"    Total commits: {stats['agent_commit_count']}")
                print(f"    Commit rate: {stats['commit_rate']:.6f} commits/s")
            else:
                print(f"    Commits: {stats['agent_commit_count']}")
                print(f"    Commit rate: {stats['commit_rate']:.6f} commits/s")
                if len(result['commit_times']) > 0:
                    print(f"    First commit: t={result['commit_times'][0]:.1f}s")
                    if len(result['commit_times']) > 1:
                        print(f"    Last commit: t={result['commit_times'][-1]:.1f}s")
        else:
            last_no_commit_alpha = alpha_0
            print(f"    No commits")
            print(f"    Final Psi: {stats['final_psi']:.6f} (deficit: {1.01 - stats['final_psi']:.6f})")
            print(f"    Max salience: {stats['max_salience']:.6f}")

    # Record threshold for this time horizon
    if first_commit_alpha is not None:
        thresholds_by_time[T] = {
            'onset': first_commit_alpha,
            'last_no_commit': last_no_commit_alpha
        }
        print(f"\n  >>> THRESHOLD SUMMARY for T={T:.0f}s <<<")
        if last_no_commit_alpha is not None:
            print(f"      No commits: alpha_0 <= {last_no_commit_alpha:.2f}")
            print(f"      Commits:    alpha_0 >= {first_commit_alpha:.2f}")
            print(f"      Bracket:    [{last_no_commit_alpha:.2f}, {first_commit_alpha:.2f}]")
        else:
            print(f"      Onset at alpha_0 = {first_commit_alpha:.2f}")
    else:
        print(f"\n  >>> No commits found for T={T:.0f}s <<<")

# -----------------------------
# Save results
# -----------------------------
print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save full JSON
json_file = "extended_time_threshold_results.json"
with open(json_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Full results saved to: {json_file}")

# Save CSV
csv_file = "extended_time_threshold_results.csv"
with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'alpha_0', 'T', 'gamma', 'M',
        'has_commits', 'agent_commit_count', 'first_commit_time',
        'commit_rate', 'final_psi', 'max_salience'
    ])
    writer.writeheader()
    for r in results:
        p = r['parameters']
        s = r['statistics']
        writer.writerow({
            'alpha_0': p['alpha_0'],
            'T': p['T'],
            'gamma': p['gamma'],
            'M': p['M'],
            'has_commits': s['has_commits'],
            'agent_commit_count': s['agent_commit_count'],
            'first_commit_time': s['first_commit_time'] if s['first_commit_time'] else '',
            'commit_rate': s['commit_rate'],
            'final_psi': s['final_psi'],
            'max_salience': s['max_salience']
        })
print(f"CSV data saved to: {csv_file}")

# -----------------------------
# Analysis Summary
# -----------------------------
print("\n" + "=" * 80)
print("THRESHOLD STABILITY ANALYSIS")
print("=" * 80)

print("\nThreshold boundaries across time horizons:")
print(f"{'T (s)':<10} {'Lower bound':<15} {'Upper bound':<15} {'Time-invariant?'}")
print("-" * 70)

reference_threshold = None
is_time_invariant = True

for T in sorted(thresholds_by_time.keys()):
    bounds = thresholds_by_time[T]
    lower = bounds.get('last_no_commit', '---')
    upper = bounds['onset']

    if reference_threshold is None:
        reference_threshold = upper
        invariant_str = "Reference"
    else:
        if upper == reference_threshold:
            invariant_str = "YES"
        else:
            invariant_str = f"NO (shifted by {upper - reference_threshold:+.2f})"
            is_time_invariant = False

    if isinstance(lower, float):
        print(f"{T:<10.0f} {lower:<15.2f} {upper:<15.2f} {invariant_str}")
    else:
        print(f"{T:<10.0f} {lower:<15s} {upper:<15.2f} {invariant_str}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if is_time_invariant:
    print("\n✓ THRESHOLD IS TIME-INVARIANT")
    print(f"  The critical α₀ threshold remains at {reference_threshold:.2f}")
    print(f"  across all tested time horizons (T = {min(time_horizons):.0f}-{max(time_horizons):.0f}s)")
    print("\n  Interpretation:")
    print("  - The threshold is a fundamental property of the system")
    print("  - Longer observation time does NOT enable weaker emissions to cross threshold")
    print("  - Event visibility is determined by emission strength, not integration time")
else:
    print("\n✗ THRESHOLD IS TIME-DEPENDENT")
    print("  The critical α₀ threshold shifts with simulation time:")
    for T in sorted(thresholds_by_time.keys()):
        print(f"    T={T:.0f}s: α₀ ≈ {thresholds_by_time[T]['onset']:.2f}")
    print("\n  Interpretation:")
    print("  - Longer integration time allows weaker emissions to accumulate past threshold")
    print("  - Event visibility depends on both emission strength AND observation duration")

print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
