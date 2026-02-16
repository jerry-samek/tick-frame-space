"""Measure total field energy per entity across mass values.

Question: does total gamma (field integral) per entity relate to mc^2?

For each mass M:
- c = 1 hop/tick (max propagation speed)
- mc = M * 1 = M
- mc^2 = M * 1² = M  (in natural units, c=1, so mc^2 = m trivially)

But the ACTUAL field integral is NOT trivially M. It depends on:
- Deposit rate (1.0 per tick)
- Spread fraction (1/k = 1/6)
- Decay (0.9999 per tick)
- How long the entity has been depositing
- Whether deposits are mass-conserving (withdraw from prev, deposit at current)

The steady-state gamma per entity = deposit_rate / (1 - decay) = 1.0 / 0.0001 = 10,000
(if all deposit stays in the system, balanced by decay)

But the entity also WITHDRAWS from the previous position (mass-conserving).
Net deposit per tick = deposit_amount - withdraw = ~0 (mass-conserving)
So the field should reach a STEADY STATE, not grow linearly.

Key measurement: steady-state gamma per entity as a function of mass M.
"""

import json
import numpy as np
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"

masses = [1, 2, 3, 5, 10]
c = 1.0  # max propagation speed in hops/tick

print("=" * 80)
print("E = mc^2 MEASUREMENT: Total field energy per entity vs mass")
print("=" * 80)
print()

# Parameters (from JSON)
print("Model parameters:")
print("  c = 1 hop/tick (max propagation speed)")
print("  deposit_amount = 1.0 per tick")
print("  spread_fraction = 1/k = 1/6 ~= 0.167")
print("  decay = 0.9999 per tick")
print("  All entities have EQUAL mass in each run")
print()

results = {}

for M in masses:
    fname = f"results_three_body_lattice_temporal_equilateral_alwaysmove_mass{M}.json"
    fpath = RESULTS_DIR / fname

    if not fpath.exists():
        print(f"  mass={M}: MISSING ({fname})")
        continue

    with open(fpath) as f:
        data = json.load(f)

    energy = data['energy']

    # Extract gamma per entity over time
    ticks = [e['tick'] for e in energy]
    gamma_A = [e['gamma_A'] for e in energy]
    gamma_B = [e['gamma_B'] for e in energy]
    gamma_C = [e['gamma_C'] for e in energy]
    gamma_total = [e['gamma_total'] for e in energy]

    # Use last 50% of data as "steady state"
    n = len(ticks)
    ss_start = n // 2

    ss_gamma_A = np.mean(gamma_A[ss_start:])
    ss_gamma_B = np.mean(gamma_B[ss_start:])
    ss_gamma_C = np.mean(gamma_C[ss_start:])
    ss_gamma_total = np.mean(gamma_total[ss_start:])
    ss_gamma_per_entity = np.mean([ss_gamma_A, ss_gamma_B, ss_gamma_C])

    # Also look at initial gamma (first measurement) and final
    init_gamma_per_entity = np.mean([gamma_A[0], gamma_B[0], gamma_C[0]])
    final_gamma_per_entity = np.mean([gamma_A[-1], gamma_B[-1], gamma_C[-1]])

    # Gamma at different time points
    early_gamma = np.mean([gamma_A[0], gamma_B[0], gamma_C[0]])
    mid_gamma = np.mean([gamma_A[n//2], gamma_B[n//2], gamma_C[n//2]])
    late_gamma = np.mean([gamma_A[-1], gamma_B[-1], gamma_C[-1]])

    # Predicted values
    mc = M * c
    mc2 = M * c * c

    results[M] = {
        'ss_gamma_per_entity': ss_gamma_per_entity,
        'final_gamma': final_gamma_per_entity,
        'early_gamma': early_gamma,
        'mid_gamma': mid_gamma,
        'late_gamma': late_gamma,
        'mc': mc,
        'mc2': mc2,
        'ticks': ticks[-1],
        'n_samples': n,
    }

    print(f"Mass = {M}:")
    print(f"  Ticks: {ticks[0]} to {ticks[-1]} (n={n} samples)")
    print(f"  Gamma per entity (early/mid/late): {early_gamma:.1f} / {mid_gamma:.1f} / {late_gamma:.1f}")
    print(f"  Steady-state gamma per entity: {ss_gamma_per_entity:.1f}")
    print(f"  mc  = {mc:.1f}")
    print(f"  mc^2 = {mc2:.1f}")
    print(f"  Ratio gamma/mc  = {ss_gamma_per_entity/mc:.2f}")
    print(f"  Ratio gamma/mc^2 = {ss_gamma_per_entity/mc2:.2f}")
    print()

# Summary table
print()
print("=" * 80)
print("SUMMARY: Steady-state gamma per entity")
print("=" * 80)
print()
print(f"{'Mass':>5} | {'v=c/M':>7} | {'Gamma/entity':>13} | {'mc':>7} | {'mc^2':>7} | {'G/m':>8} | {'G/mc':>8} | {'G/mc^2':>8}")
print("-" * 80)

for M in masses:
    if M not in results:
        continue
    r = results[M]
    g = r['ss_gamma_per_entity']
    print(f"{M:5d} | {c/M:7.4f} | {g:13.1f} | {r['mc']:7.1f} | {r['mc2']:7.1f} | {g/M:8.2f} | {g/r['mc']:8.2f} | {g/r['mc2']:8.2f}")

# Check ratios between masses
print()
print("=" * 80)
print("RATIO TEST: How does gamma scale with mass?")
print("=" * 80)
print()
print("If E = mc^2:  gamma(M) / gamma(1) should equal M")
print("If E = mc:   gamma(M) / gamma(1) should equal M")
print("If E = m:    gamma(M) / gamma(1) should equal M")
print("(In natural units c=1, all three predict the same ratio)")
print()
print("So the real test: is gamma PROPORTIONAL to M at all?")
print()

if 1 in results:
    g1 = results[1]['ss_gamma_per_entity']
    print(f"{'Mass':>5} | {'Gamma/entity':>13} | {'Ratio to M=1':>13} | {'Expected (=M)':>14} | {'Match?':>7}")
    print("-" * 70)
    for M in masses:
        if M not in results:
            continue
        g = results[M]['ss_gamma_per_entity']
        ratio = g / g1
        expected = M / 1.0
        match = "YES" if abs(ratio - expected) / expected < 0.1 else "NO"
        print(f"{M:5d} | {g:13.1f} | {ratio:13.4f} | {expected:14.1f} | {match:>7}")

# Alternative: does gamma scale with deposit footprint?
# Entity deposits 1.0 per tick, sits for M ticks per position
# Deposit per position = M * 1.0 = M
# But mass-conserving: it withdraws from prev. Net deposit per position ~= 0 after first visit
# However: entity moves slower with higher mass, so the well stays deeper longer
print()
print("=" * 80)
print("DEPOSIT FOOTPRINT ANALYSIS")
print("=" * 80)
print()
print("Entity deposits 1.0/tick, sits M ticks per position")
print("Deposit per position (if not mass-conserving): M * 1.0 = M")
print("But model IS mass-conserving: withdraw from prev, deposit at current")
print("Net steady-state deposit = deposit_amount (current) - withdraw (available at prev)")
print()
print("Key: heavier entity sits LONGER, so the well at its position is deeper")
print("Well depth ~= M * deposit_amount (accumulated before withdrawal catches up)")
print()

# Time evolution check: is gamma growing, shrinking, or stable?
print("=" * 80)
print("TIME EVOLUTION: Is gamma per entity stable?")
print("=" * 80)
print()
for M in masses:
    if M not in results:
        continue
    r = results[M]
    trend = "GROWING" if r['late_gamma'] > r['early_gamma'] * 1.05 else \
            "SHRINKING" if r['late_gamma'] < r['early_gamma'] * 0.95 else "STABLE"
    change = (r['late_gamma'] - r['early_gamma']) / r['early_gamma'] * 100
    print(f"  Mass={M}: {r['early_gamma']:.1f} -> {r['late_gamma']:.1f} ({change:+.1f}%) [{trend}]")
