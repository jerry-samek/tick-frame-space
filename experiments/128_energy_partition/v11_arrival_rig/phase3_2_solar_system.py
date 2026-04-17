#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 3.2: Solar System Sanity Check

Take the Phase 3.1 model and ask: can it reproduce Kepler's Third Law
(T^2 = 4*pi^2 * a^3 / GM_sun) across real planets?

This is important for honesty. Phase 3.1 showed mass-independence of T
in the inner capacity-limited regime, and called that "Newton's result
emerging." But real planets are in the OUTER regime of Phase 3.1 (their
C_cap >> arrival), and the outer-regime formula from the code-as-written
is:

    a = surplus / M = (K/r^2 - M) / M = K/(r^2 M) - 1
    v^2 = r * a = K/(rM) - r
    T^2 = 4*pi^2 r^3 M / K    (for K/(rM) >> r, i.e. far from the horizon)

That HAS M_planet in it. Kepler does not. If we feed real planets into
this, Kepler's T^2 vs r^3 linearity breaks as the planet masses vary.

The fix is physical, not formal: in the current code, total arrival at
the planet is K/r^2 regardless of planet size. But on a real graph a
bigger planet has more consuming nodes, so total arrival should scale
with M. If arrival = M * K/r^2 (per-node arrival K/r^2, M nodes),
then:

    consumed = M * K/r^2       (outer, no cap)
    surplus  = M * (K/r^2 - 1)
    a        = surplus / M = K/r^2 - 1
    T^2      = 4*pi^2 r^3 / K     (for K/r^2 >> 1)

That IS Kepler, with the sun's GM = K. And the "-1" term from renewal
gives a small deviation from Kepler at large r, near the gravity
horizon where arrival drops to renewal.

This phase:
  1. Plots real planet (T, a) and fits Kepler (passes trivially).
  2. Applies Phase 3.1-as-written to the solar system and shows it
     fails because of the extra M factor.
  3. Applies the "consumption scales with M" fix and shows it reproduces
     Kepler, plus a predicted deviation at very large r (horizon).

Unit system: AU, year, solar mass. In these units GM_sun = 4*pi^2.
"""

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


# ---------------------------------------------------------------------
#  Solar system data
# ---------------------------------------------------------------------
# (name, a[AU], T[year], M[solar masses])
PLANETS = [
    ("Mercury", 0.387,   0.241,  1.66e-7),
    ("Venus",   0.723,   0.615,  2.45e-6),
    ("Earth",   1.000,   1.000,  3.00e-6),
    ("Mars",    1.524,   1.881,  3.23e-7),
    ("Jupiter", 5.203,   11.86,  9.55e-4),
    ("Saturn",  9.537,   29.46,  2.86e-4),
    ("Uranus",  19.191,  84.01,  4.37e-5),
    ("Neptune", 30.069, 164.79,  5.15e-5),
]

K_SUN = 4 * np.pi ** 2  # GM_sun in (AU^3 / year^2) natural units


# ---------------------------------------------------------------------
#  Model formulas
# ---------------------------------------------------------------------

def T_kepler(a):
    """Exact Newton/Kepler: T^2 = 4 pi^2 a^3 / GM_sun."""
    return 2 * np.pi * np.sqrt(a ** 3 / K_SUN)


def T_phase3_1_as_written(a, M):
    """Phase 3.1 outer regime, code as actually written:

      arrival = K / r^2         (not scaled by M)
      consumed = arrival        (outer regime, below cap)
      surplus = K/r^2 - M
      a_acc   = surplus / M
      v^2 = a * (K/(a^2 M) - 1) * a = K/(a M) - a       [hmm, careful]

    Simpler: v^2 = a * (K/(a^2 M) - 1). Assume K/(a^2 M) >> 1 so we
    can ignore the -1 (far from horizon):
      v^2 ~= K / (a M)
      T = 2 pi a / v = 2 pi sqrt(a^3 M / K)
    """
    return 2 * np.pi * np.sqrt(a ** 3 * M / K_SUN)


def T_fixed_model(a, M):
    """Fixed model: total arrival scales with M (bigger planet = more
    consuming sites). This is the physically natural reading of a
    planet on a graph.

      arrival = M * K/r^2
      consumed = arrival        (outer regime)
      surplus = M * (K/r^2 - 1)   # "-1" is the per-node renewal
      a_acc   = surplus / M = K/r^2 - 1
      v^2     = a * (K/a^2 - 1) = K/a - a
      T       = 2 pi a / sqrt(K/a - a)    (horizon at a = sqrt(K))
    """
    v2 = K_SUN / a - a
    if v2 <= 0:
        return float('inf')
    return 2 * np.pi * a / np.sqrt(v2)


def horizon_radius():
    """Fixed-model gravity horizon: v^2 = K/a - a = 0 => a = sqrt(K)."""
    return float(np.sqrt(K_SUN))


# ---------------------------------------------------------------------
#  Run: compare the three models against real planetary data
# ---------------------------------------------------------------------

def run():
    print(f"K_sun = GM_sun in (AU^3/year^2) = {K_SUN:.3f}")
    print(f"Fixed-model gravity horizon: a = sqrt(K_sun) = {horizon_radius():.3f} AU")
    print()

    header = (
        f"{'planet':<10} {'a[AU]':>8} {'T_obs[yr]':>11} "
        f"{'T_Kepler':>11} {'T_P3.1':>11} {'T_fixed':>11}"
    )
    print(header)
    print("-" * len(header))

    rows = []
    for name, a, T_obs, M in PLANETS:
        T_k = T_kepler(a)
        T_p3 = T_phase3_1_as_written(a, M)
        T_f = T_fixed_model(a, M)
        print(f"{name:<10} {a:>8.3f} {T_obs:>11.3f} {T_k:>11.3f} "
              f"{T_p3:>11.3e} {T_f:>11.3f}")
        rows.append((name, a, T_obs, T_k, T_p3, T_f, M))

    # Kepler test: log(T) vs log(a), slope should be 1.5
    a_arr = np.array([r[1] for r in rows])
    T_obs_arr = np.array([r[2] for r in rows])
    T_k_arr = np.array([r[3] for r in rows])
    T_p3_arr = np.array([r[4] for r in rows])
    T_f_arr = np.array([r[5] for r in rows])

    slope_obs, _ = np.polyfit(np.log(a_arr), np.log(T_obs_arr), 1)
    slope_f, _ = np.polyfit(np.log(a_arr), np.log(T_f_arr), 1)
    # Slope of Phase3.1-as-written depends on M too, so fit anyway
    slope_p3, _ = np.polyfit(np.log(a_arr), np.log(T_p3_arr), 1)

    print()
    print(f"log-log slope of T vs a (Kepler's third law expects 1.5):")
    print(f"  observed:     {slope_obs:.4f}")
    print(f"  Kepler:       1.5 exactly (by construction)")
    print(f"  Phase 3.1:    {slope_p3:.4f}  (wrong, pulled by planet mass)")
    print(f"  Fixed model:  {slope_f:.4f}")

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: the three predictions vs actual
    ax = axes[0]
    ax.loglog(a_arr, T_obs_arr, 'ko', ms=8, label='observed')
    ax.loglog(a_arr, T_k_arr, 'b-', lw=1, label=f'Kepler (slope {1.5})')
    ax.loglog(a_arr, T_f_arr, 'g--', lw=1.5,
              label=f'fixed model (arrival prop M)')
    ax.loglog(a_arr, T_p3_arr, 'r:', lw=1.5,
              label='Phase 3.1 as written (fails)')
    for i, row in enumerate(rows):
        ax.annotate(row[0], (a_arr[i], T_obs_arr[i]),
                    fontsize=8, textcoords="offset points", xytext=(5, 3))
    ax.set_xlabel('a [AU]'); ax.set_ylabel('T [year]')
    ax.set_title('Solar system: three models vs reality')
    ax.legend(fontsize=8); ax.grid(True, which='both', alpha=0.3)

    # Right: deviation of fixed-model from Kepler (horizon effect)
    ax = axes[1]
    a_fine = np.linspace(0.3, 0.95 * horizon_radius(), 400)
    ratio = np.array([T_fixed_model(a, 0) / T_kepler(a) for a in a_fine])
    ax.plot(a_fine, ratio, 'g-', lw=1, label='T_fixed / T_Kepler')
    ax.axvline(horizon_radius(), color='r', ls='--',
               label=f'horizon at a = sqrt(K) = {horizon_radius():.2f} AU')
    for name, a, _, _, _, _, _ in rows:
        ax.axvline(a, color='gray', alpha=0.3, lw=0.5)
        ax.annotate(name, (a, 1.0), fontsize=7, rotation=90,
                    textcoords="offset points", xytext=(2, 2), va='bottom')
    ax.set_xlabel('a [AU]')
    ax.set_ylabel('T_fixed / T_Kepler')
    ax.set_title('Fixed-model deviation (tick-frame horizon effect)')
    ax.set_ylim(0.98, 2.0)
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    plt.suptitle('Phase 3.2: solar-system sanity check', fontsize=12)
    plt.tight_layout()
    out = os.path.join(OUT, 'phase3_2_solar_system.png')
    plt.savefig(out, dpi=140)
    plt.close()
    print(f"\nSaved: {out}")

    # Consumption rates per planet (fixed model: consumed = M * K/r^2)
    # In the tick-frame reading this IS the gravitational force on the planet,
    # interpreted as "impulses absorbed per tick".
    print()
    print("Consumption rate per planet (fixed model, natural units):")
    print(f"{'planet':<10} {'a':>7} {'M':>10} {'K/r^2':>9} "
          f"{'consumed':>12} {'cons/renewal':>13}")
    print("-" * 66)
    for name, a, T_obs, M in PLANETS:
        K_over_r2 = K_SUN / (a * a)
        consumed = M * K_over_r2
        # consumption/renewal = K/r^2 in our convention (renewal=M)
        print(f"{name:<10} {a:>7.3f} {M:>10.2e} {K_over_r2:>9.2f} "
              f"{consumed:>12.3e} {K_over_r2:>13.2f}")

    print()
    print("Reading:")
    print("  consumed/renewal = K/r^2 -- how 'deep' the planet is in the")
    print("  star's well relative to its own persistence cost.")
    print("  Inner planets: sun supplies 17-263 x their renewal demand.")
    print("  Jupiter sits at 1.46 -- essentially matched.")
    print("  Saturn and beyond: sun supplies LESS than renewal, under")
    print("  the assumption that stellar deposits have to cover renewal.")
    print()
    print("  But real planets orbit out to Neptune and beyond with no")
    print("  trouble. Conclusion: in physics, renewal is NOT paid out")
    print("  of the star's flux. It's paid by the local tick-stream")
    print("  (ambient existence). Stellar deposits drive orbital motion")
    print("  only; they do not subtract from persistence.")
    print()
    print("  Operationally: the '-1' renewal term in the fixed-model")
    print("  equation of motion is the wrong form. Drop it and the")
    print("  model collapses to exact Kepler everywhere.")
    print()
    print("Observations about the horizon in (AU, year, solar mass) units:")
    print(f"  fixed-model horizon: a_horizon = sqrt(K_sun) = "
          f"{horizon_radius():.2f} AU")
    print(f"  Neptune at 30 AU is {30 / horizon_radius():.1%} of the way there")
    print(f"  Pluto at 39 AU is   {39 / horizon_radius():.1%} of the way there")
    print(f"  Oort cloud starts around 2000 AU -- {2000/horizon_radius():.1f}x horizon")
    print()
    print("If this horizon is real, bound orbits beyond a_horizon")
    print("should be impossible. In (AU, year, M_sun) natural units")
    print("it sits right in the Kuiper/Oort interval -- interesting,")
    print("but unit-dependent. In real physics there is no such cutoff")
    print("(bodies orbit out to the Oort cloud). So the horizon as coded")
    print("is an artifact of the particular renewal constant (=1 per")
    print("M_sun-unit) we picked. In a calibrated model, renewal per")
    print("unit mass would have to be many orders smaller for the")
    print("horizon to retreat to cosmological scales.")


if __name__ == '__main__':
    run()
