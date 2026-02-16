"""Deeper analysis: how does field energy scale with mass?

Key findings from v1:
- Gamma is NOT proportional to M
- Gamma per entity: 682 (M=1), 852 (M=2), 941 (M=3), 1034 (M=5), 1099 (M=10)
- All fields are SHRINKING (formation deposits decaying away)
- The gamma/M ratio DECREASES: 682, 426, 314, 207, 110

Let's fit the scaling law and check if it's log, sqrt, or power law.
Also: separate the formation contribution from the dynamics contribution.
"""

import json
import numpy as np
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"

masses = [1, 2, 3, 5, 10]

# Collect steady-state gamma per entity
gammas = {}
gamma_timeseries = {}

for M in masses:
    fname = f"results_three_body_lattice_temporal_equilateral_alwaysmove_mass{M}.json"
    fpath = RESULTS_DIR / fname
    with open(fpath) as f:
        data = json.load(f)

    energy = data['energy']
    ticks = np.array([e['tick'] for e in energy])
    g_per_entity = np.array([(e['gamma_A'] + e['gamma_B'] + e['gamma_C']) / 3.0
                              for e in energy])

    # Steady state: last 25% of data
    n = len(ticks)
    ss_start = int(n * 0.75)

    gammas[M] = np.mean(g_per_entity[ss_start:])
    gamma_timeseries[M] = (ticks, g_per_entity)

print("=" * 80)
print("SCALING ANALYSIS: gamma_ss(M) vs various models")
print("=" * 80)
print()

M_arr = np.array(masses, dtype=float)
G_arr = np.array([gammas[M] for M in masses])

print(f"{'Mass':>5} | {'Gamma_ss':>10} | {'log(M)':>8} | {'sqrt(M)':>8} | {'M^0.2':>8}")
print("-" * 55)
for i, M in enumerate(masses):
    print(f"{M:5d} | {G_arr[i]:10.1f} | {np.log(M):8.3f} | {np.sqrt(M):8.3f} | {M**0.2:8.3f}")

# Fit: gamma = a + b * M^alpha
# Try several alpha values
print()
print("Power law fits: gamma = a + b * M^alpha")
print("-" * 55)

best_alpha = None
best_r2 = -1

for alpha in [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    X = M_arr ** alpha
    # Linear regression: gamma = a + b * X
    A = np.vstack([np.ones_like(X), X]).T
    result = np.linalg.lstsq(A, G_arr, rcond=None)
    coefs = result[0]
    a, b = coefs[0], coefs[1]
    predicted = a + b * X
    ss_res = np.sum((G_arr - predicted) ** 2)
    ss_tot = np.sum((G_arr - np.mean(G_arr)) ** 2)
    r2 = 1 - ss_res / ss_tot
    if r2 > best_r2:
        best_r2 = r2
        best_alpha = alpha
        best_a, best_b = a, b
    print(f"  alpha={alpha:.2f}: gamma = {a:.1f} + {b:.1f} * M^{alpha:.2f}  R^2={r2:.6f}")

print()
print(f"BEST FIT: alpha = {best_alpha:.2f}, R^2 = {best_r2:.6f}")
print(f"  gamma = {best_a:.1f} + {best_b:.1f} * M^{best_alpha:.2f}")
print()

# Also try log fit: gamma = a + b * log(M)
X_log = np.log(M_arr)
A_log = np.vstack([np.ones_like(X_log), X_log]).T
result_log = np.linalg.lstsq(A_log, G_arr, rcond=None)
a_log, b_log = result_log[0]
pred_log = a_log + b_log * X_log
r2_log = 1 - np.sum((G_arr - pred_log)**2) / np.sum((G_arr - np.mean(G_arr))**2)
print(f"LOG FIT: gamma = {a_log:.1f} + {b_log:.1f} * ln(M)  R^2={r2_log:.6f}")
print()

# KEY QUESTION: What's the RATE of gamma production in steady state?
# The entity deposits 1.0/tick. After mass-conserving withdrawal, net deposit is small.
# But it also spreads and decays.
# Steady state: deposit rate = decay rate
# gamma_ss = deposit_rate_net / decay_rate
# If deposit_rate_net depends on M, gamma_ss depends on M.
#
# Heavier entity sits M ticks -> deposits M at current node -> withdraws prev_amount from prev
# During M ticks at position:
#   - Tick 1: deposit 1.0, withdraw available_prev
#   - Tick 2: deposit 1.0, withdraw available_prev (now less because decay+spread)
#   - ...
#   - Tick M: deposit 1.0, withdraw whatever's left at prev
# Total deposited at current: M * 1.0 = M
# Total withdrawn from prev: sum of available_prev over M ticks
# Net = M - total_withdrawn
#
# If prev position had ~gamma_ss before entity left, and decays at 0.9999/tick:
# Available at prev after t ticks: gamma_ss * 0.9999^t * (spread_retention)
# But entity ALSO withdraws each tick, depleting prev faster

print("=" * 80)
print("NET DEPOSIT RATE ANALYSIS")
print("=" * 80)
print()
print("In mass-conserving mode:")
print("  Per M-tick cycle: deposit M * 1.0 at current, withdraw sum(available_prev) from prev")
print("  Entity moves at v=c/M = 1/M hops per tick")
print("  Deposits per unit distance = M * 1.0 per hop = M per hop")
print("  But withdrawals ALSO scale with M (more ticks to drain prev)")
print()

# What if we look at gamma * v = gamma * c/M?
# This would be the "energy flux" -- field energy times speed
print("=" * 80)
print("ENERGY FLUX: gamma * v = gamma * c/M")
print("=" * 80)
print()
print(f"{'Mass':>5} | {'Gamma_ss':>10} | {'v=c/M':>8} | {'Gamma*v':>10} | {'Gamma*v/c':>10}")
print("-" * 55)
for i, M in enumerate(masses):
    v = 1.0 / M
    flux = G_arr[i] * v
    print(f"{M:5d} | {G_arr[i]:10.1f} | {v:8.4f} | {flux:10.1f} | {flux:10.1f}")

print()

# What about gamma * v^2 = gamma * (c/M)^2?
print("KINETIC-LIKE: gamma * v^2 = gamma * (c/M)^2")
print("-" * 55)
print(f"{'Mass':>5} | {'Gamma_ss':>10} | {'v^2':>10} | {'Gamma*v^2':>10}")
print("-" * 55)
for i, M in enumerate(masses):
    v2 = (1.0 / M) ** 2
    print(f"{M:5d} | {G_arr[i]:10.1f} | {v2:10.6f} | {G_arr[i]*v2:10.4f}")

print()

# Reverse question: if E = mc^2, what should gamma be?
# In natural units c=1: E = M
# So gamma_ss should be proportional to M
# But it's NOT. It grows sub-linearly.
#
# Unless the "energy" isn't gamma_ss but something else.
# What if energy = gamma_ss * M (total deposits over the entity's lifetime per position)?
# Or energy = gamma_peak (the peak gamma at the entity's position, not the total)?

print("=" * 80)
print("ALTERNATIVE ENERGY MEASURES")
print("=" * 80)
print()
print("Maybe total gamma isn't the right energy measure.")
print("Try: gamma * M (total gamma weighted by mass)")
print()
print(f"{'Mass':>5} | {'Gamma_ss':>10} | {'Gamma*M':>10} | {'Gamma*M/M^2':>10} | {'= Gamma/M':>10}")
print("-" * 60)
for i, M in enumerate(masses):
    print(f"{M:5d} | {G_arr[i]:10.1f} | {G_arr[i]*M:10.1f} | {G_arr[i]*M/M**2:10.2f} | {G_arr[i]/M:10.2f}")

# The decay is key. With decay = 0.9999, the half-life is:
# 0.9999^t = 0.5 -> t = log(0.5)/log(0.9999) = 6931 ticks
half_life = np.log(0.5) / np.log(0.9999)
print()
print(f"Decay half-life: {half_life:.0f} ticks")
print(f"Entity speed (hops/tick) at mass M: c/M = 1/M")
print(f"Hops in one half-life:")
for M in masses:
    hops = half_life / M
    print(f"  Mass={M}: {hops:.0f} hops in {half_life:.0f} ticks")
