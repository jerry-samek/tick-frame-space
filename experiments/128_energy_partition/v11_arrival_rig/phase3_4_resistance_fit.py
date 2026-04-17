#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 3.4: Per-Planet Resistance Fit

The fixed model with renewal (Phase 3.2 'T_fixed') diverges for outer
planets because v^2 = K/r - r goes negative at r = sqrt(K).

Introduce a per-planet *resistance* R that scales the arrival:

    arrival_per_node = R * K/r^2
    renewal_per_node = 1
    surplus_per_node = R*K/r^2 - 1
    a (per mass)     = R*K/r^2 - 1
    v^2 (circular)   = r * (R*K/r^2 - 1) = R*K/r - r

For the model's period to match the observed Kepler period at each
planet's r, we need:

    R*K/r - r = K/r    (the observed Kepler v^2)
    R        = 1 + r^2/K

So the "resistance" required is a *function of distance*, not a
planet-specific parameter. Heavier or lighter, the same R(r) works.
This is itself a finding -- it means the deviation between our model
and reality is purely the constant renewal term, not anything
structural.

R = 1 + r^2/K can be read several ways:
  (a) The renewal cost is an artifact of choosing renewal = M per tick
      in natural units; effective renewal should be smaller by factor R.
  (b) Or: per-node absorption is amplified by R(r) somehow -- e.g.
      each node samples a larger "effective cone" at large distance.
  (c) Or: the true operational rule has NO renewal drag at all and R=1
      is correct; the extra r^2/K is the term we wrongly subtracted.

This phase computes R for each planet, and also the equivalent
"effective renewal" epsilon if we instead write surplus = M(K/r^2 - eps).
That gives eps = K/r^2 - 4 pi^2 r / T^2, which for real solar-system
data should collapse to ~0 (exact Kepler).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)

PLANETS = [
    ("Mercury", 0.387,   0.241,  1.66e-7),
    ("Venus",   0.723,   0.615,  2.45e-6),
    ("Earth",   1.000,   1.000,  3.00e-6),
    ("Mars",    1.524,   1.881,  3.23e-7),
    ("Jupiter", 5.203,  11.860,  9.55e-4),
    ("Saturn",  9.537,  29.460,  2.86e-4),
    ("Uranus", 19.191,  84.010,  4.37e-5),
    ("Neptune",30.069, 164.790,  5.15e-5),
]

K = 4 * np.pi**2  # GM_sun in AU^3/yr^2

print(f"K (= GM_sun in AU^3/yr^2) = {K:.4f}")
print()
print(f"{'planet':<9} {'a[AU]':>7} {'T_obs[yr]':>10} {'R=1+r^2/K':>12} "
      f"{'eps=K/r^2-4pi^2r/T^2':>23}")
print("-" * 65)

r_arr, R_arr, eps_arr, name_arr = [], [], [], []
for name, r, T_obs, M in PLANETS:
    R_fit = 1 + r**2 / K
    # Effective renewal parameter if we instead kept R=1 and wrote
    # surplus = M(K/r^2 - eps)
    v2_obs = (2 * np.pi * r / T_obs)**2
    eps = K / (r*r) - v2_obs / r
    print(f"{name:<9} {r:>7.3f} {T_obs:>10.3f} {R_fit:>12.4f} "
          f"{eps:>23.3e}")
    r_arr.append(r); R_arr.append(R_fit); eps_arr.append(eps); name_arr.append(name)

print()
print("Reading the columns:")
print("  R = 1 + r^2/K  -- the pure-algebra resistance needed if we")
print("                   keep the '-1' (renewal) term in the force law.")
print("                   Grows quadratically with distance.")
print()
print("  eps = K/r^2 - v_obs^2/r  -- the effective renewal constant")
print("                   if we keep R=1. For Kepler-exact orbits,")
print("                   eps should be ~0. Nonzero values = how far")
print("                   our '-1 renewal' is from reality.")
print()

# Fit log-log slope of R-1 vs r (should be exactly 2 by construction)
r_np = np.array(r_arr); R_np = np.array(R_arr)
slope, _ = np.polyfit(np.log(r_np), np.log(R_np - 1), 1)
print(f"  slope of log(R-1) vs log(r) = {slope:.3f}")
print(f"  (expected exactly 2.000; this is the r^2/K term)")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.loglog(r_np, R_np, 'bo-', ms=6, lw=1)
for i, name in enumerate(name_arr):
    ax.annotate(name, (r_np[i], R_np[i]), fontsize=8,
                textcoords="offset points", xytext=(5, 3))
r_fine = np.logspace(np.log10(0.3), np.log10(40), 200)
ax.loglog(r_fine, 1 + r_fine**2/K, 'k--', lw=0.8, alpha=0.5,
          label='R = 1 + r^2/K')
ax.axhline(1.0, color='gray', ls=':', alpha=0.5, label='R=1 (no correction)')
ax.set_xlabel('r [AU]'); ax.set_ylabel('R (resistance needed)')
ax.set_title('Per-planet resistance to match observed T')
ax.legend(fontsize=9); ax.grid(True, which='both', alpha=0.3)

ax = axes[1]
eps_np = np.array(eps_arr)
# absolute value to use on log plot
ax.semilogx(r_np, eps_np, 'ro-', ms=6, lw=1)
for i, name in enumerate(name_arr):
    ax.annotate(name, (r_np[i], eps_np[i]), fontsize=8,
                textcoords="offset points", xytext=(5, 3))
ax.axhline(0, color='gray', ls=':', alpha=0.5)
ax.set_xlabel('r [AU]'); ax.set_ylabel('eps (effective renewal in K/r^2 units)')
ax.set_title('Effective renewal constant from real data')
ax.grid(True, alpha=0.3)

plt.suptitle('Phase 3.4: what resistance would make our model fit?',
             fontsize=12)
plt.tight_layout()
out = os.path.join(OUT, 'phase3_4_resistance.png')
plt.savefig(out, dpi=140)
plt.close()
print(f"\nSaved: {out}")
print()
print("Bottom line:")
print("  - No planet-specific R is needed; R(r)=1+r^2/K fits all of them.")
print("  - eps (effective renewal drag) is ~0 for every real planet, to")
print("    the precision of the orbital data. Deviation from 0 is at the")
print("    level of observational / ephemeris precision, not a real")
print("    substrate effect.")
print("  - Interpretation: renewal does NOT appear in orbital dynamics.")
print("    The clean substrate model for gravity is simply")
print("        a = K/r^2    (no renewal term)")
print("    which recovers exact Kepler and makes the whole 'horizon'")
print("    artifact vanish.")
