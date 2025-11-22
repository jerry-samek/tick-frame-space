"""
Dynamic Ψ(t) buildup analysis: Track temporal evolution of salience accumulation.

Goals:
1. Measure buildup rate dΨ/dt
2. Identify threshold crossing time
3. Characterize growth regime (linear/exponential/power-law)
4. Compare dynamics below vs. above threshold
"""

import math
import numpy as np
import json
import csv
from datetime import datetime

# -----------------------------
# Parameters for dynamic analysis
# -----------------------------
# Test a range of alpha_0 values around and above threshold
alpha_0_values = [1.80, 1.85, 1.90, 1.95, 2.00, 2.50, 5.00]
alpha_1 = 0.0

# Optimal parameters from v2
gamma = 0.001
M = 1

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

# Logging parameters
log_interval = 10  # Log every N ticks

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
# Run simulation with temporal tracking
# -----------------------------
def run_simulation_with_tracking(alpha_0, alpha_1, gamma, M):
    """Run simulation and track Ψ(t) evolution."""

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
    threshold_crossing_time = None
    threshold_crossing_tick = None

    # CFL check
    cfl = c * dt / dx
    if cfl > 1.0:
        return None

    time = 0.0
    next_commit_threshold = n_threshold + 1.0 + delta

    # Temporal logs
    psi_history = []  # (tick, time, Psi, salience)
    commit_times = []

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
                Psi += S * 1.0

                # Log Psi evolution
                if tick_count % log_interval == 0:
                    psi_history.append({
                        'tick': tick_count,
                        'time': commit_time,
                        'psi': float(Psi),
                        'salience': float(S),
                        'committed': False
                    })

                if Psi >= 1.0 + epsilon:
                    agent_commit_count += 1
                    commit_times.append(commit_time)

                    if threshold_crossing_time is None:
                        threshold_crossing_time = commit_time
                        threshold_crossing_tick = tick_count

                    # Log commit event
                    psi_history.append({
                        'tick': tick_count,
                        'time': commit_time,
                        'psi': float(Psi),
                        'salience': float(S),
                        'committed': True
                    })

                    Psi = 0.0

        # Wave field step
        A_next = wave_step_leapfrog(A_field, A_prev, dt, c, gamma, dx, src_idx, emitted_source_impulse)

        A_prev[:] = A_field[:]
        A_field[:] = A_next[:]

        time += dt

    # Compute buildup rate
    if len(psi_history) > 1:
        # Fit linear model to pre-commit region
        pre_commit = [p for p in psi_history if not p['committed']]
        if len(pre_commit) > 2:
            times = np.array([p['time'] for p in pre_commit])
            psis = np.array([p['psi'] for p in pre_commit])
            # Linear fit
            coeffs = np.polyfit(times, psis, 1)
            buildup_rate = coeffs[0]  # dPsi/dt
        else:
            buildup_rate = None
    else:
        buildup_rate = None

    return {
        "parameters": {
            "alpha_0": float(alpha_0),
            "gamma": float(gamma),
            "M": int(M)
        },
        "statistics": {
            "tick_count": tick_count,
            "agent_commit_count": agent_commit_count,
            "threshold_crossing_time": float(threshold_crossing_time) if threshold_crossing_time else None,
            "threshold_crossing_tick": int(threshold_crossing_tick) if threshold_crossing_tick else None,
            "buildup_rate": float(buildup_rate) if buildup_rate else None,
            "has_commits": agent_commit_count > 0
        },
        "psi_history": psi_history,
        "commit_times": commit_times
    }

# -----------------------------
# Main analysis
# -----------------------------
print("=" * 80)
print("DYNAMIC PSI BUILDUP ANALYSIS")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nGoal: Characterize temporal evolution of salience accumulation")
print(f"\nTesting alpha_0 values: {alpha_0_values}")
print(f"Fixed: gamma={gamma:.4f}, M={M}")
print(f"Tracking resolution: every {log_interval} ticks")
print("=" * 80)

results = []

for alpha_0 in alpha_0_values:
    print(f"\n{'='*70}")
    print(f"alpha_0 = {alpha_0:.2f}")
    print(f"{'='*70}")

    result = run_simulation_with_tracking(alpha_0, alpha_1, gamma, M)

    if result is None:
        print("  SKIPPED: CFL violation")
        continue

    results.append(result)
    stats = result['statistics']

    print(f"  Total ticks: {stats['tick_count']}")
    print(f"  Agent commits: {stats['agent_commit_count']}")

    if stats['has_commits']:
        print(f"  Threshold crossed at: t={stats['threshold_crossing_time']:.3f}s "
              f"(tick {stats['threshold_crossing_tick']})")
        if stats['buildup_rate']:
            print(f"  Buildup rate: dPsi/dt = {stats['buildup_rate']:.6f} /s")
        print(f"  Commit times: {[f'{t:.1f}' for t in result['commit_times'][:5]]}...")
    else:
        print(f"  No commits")
        if stats['buildup_rate']:
            print(f"  Buildup rate: dPsi/dt = {stats['buildup_rate']:.6f} /s")

    # Print sample of Psi evolution
    print(f"  Psi evolution (sample):")
    psi_sample = result['psi_history'][::max(1, len(result['psi_history'])//5)]
    for p in psi_sample:
        status = "COMMIT" if p['committed'] else ""
        print(f"    t={p['time']:5.1f}s, tick={p['tick']:3d}, "
              f"Psi={p['psi']:.6f}, S={p['salience']:.6f} {status}")

# -----------------------------
# Save results
# -----------------------------
print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save full JSON (includes temporal data)
json_file = "dynamic_buildup_results.json"
with open(json_file, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Full results (with temporal data) saved to: {json_file}")

# Save summary CSV
csv_file = "dynamic_buildup_summary.csv"
with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'alpha_0', 'gamma', 'M',
        'has_commits', 'agent_commit_count',
        'threshold_crossing_time', 'threshold_crossing_tick',
        'buildup_rate'
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
            'threshold_crossing_time': s['threshold_crossing_time'] if s['threshold_crossing_time'] else '',
            'threshold_crossing_tick': s['threshold_crossing_tick'] if s['threshold_crossing_tick'] else '',
            'buildup_rate': s['buildup_rate'] if s['buildup_rate'] else ''
        })
print(f"Summary CSV saved to: {csv_file}")

# -----------------------------
# Analysis summary
# -----------------------------
print("\n" + "=" * 80)
print("BUILDUP DYNAMICS SUMMARY")
print("=" * 80)

print("\nBuildup rates (dPsi/dt):")
print(f"{'alpha_0':<10} {'Rate (1/s)':<15} {'Crossing time':<20} {'Status'}")
print("-" * 60)

for r in results:
    p = r['parameters']
    s = r['statistics']
    rate_str = f"{s['buildup_rate']:.6f}" if s['buildup_rate'] else "N/A"
    cross_str = f"{s['threshold_crossing_time']:.3f}s" if s['threshold_crossing_time'] else "---"
    status = "Commits" if s['has_commits'] else "No commits"

    print(f"{p['alpha_0']:<10.2f} {rate_str:<15s} {cross_str:<20s} {status}")

# Analyze scaling
rates_with_commits = [(r['parameters']['alpha_0'], r['statistics']['buildup_rate'])
                      for r in results
                      if r['statistics']['has_commits'] and r['statistics']['buildup_rate']]

if len(rates_with_commits) > 1:
    print("\nBuildup rate scaling:")
    alphas = np.array([a for a, r in rates_with_commits])
    rates = np.array([r for a, r in rates_with_commits])

    # Fit power law: rate ~ alpha_0^n
    log_alphas = np.log(alphas)
    log_rates = np.log(rates)
    coeffs = np.polyfit(log_alphas, log_rates, 1)
    exponent = coeffs[0]

    print(f"  dPsi/dt ~ alpha_0^{exponent:.2f}")

print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
