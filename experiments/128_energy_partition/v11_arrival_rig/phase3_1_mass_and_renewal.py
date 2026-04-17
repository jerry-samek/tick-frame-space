#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 3.1: Mass, Renewal, and Capacity-per-Node

Discussion on 2026-04-16 surfaced two clarifications from the tick-frame
ontology:

  1. F = m*a is not smuggled Newton. With mass = tick-count (node count),
     force = consumption rate (deposits/tick), and acceleration =
     velocity-change-per-tick, the relation F = m*a is ticks/tick = ticks
     * 1/tick -- impulse conservation distributed over the object's quanta.
  2. Temporal Surfing (Doc 28): a mass-M entity MUST consume M
     deposits/tick just to persist (renewal). The surplus (arrival - M)
     is what drives acceleration.

So the cleaner Phase 3 uses:

  renewal     = M                  (cost to stay alive)
  pool        = B + arrival        (buffered + new)
  total_consumed = min(pool, C_cap)  (processing limit)
  surplus     = max(0, total_consumed - renewal)
  F           = surplus * (-r_hat)
  a           = F / M               (tick bookkeeping)
  B'          = pool - total_consumed

Two variants of the processing limit:

  A) C_cap = fixed constant          (my Phase 3 -- planet doesn't scale)
  B) C_cap = M * c_per_node          (every node has its own capacity)

Prediction under Variant B, outer regime (arrival < C_cap):
  - F = arrival - M  =  K/r^2 - M  (surplus, not raw arrival!)
  - Equilibrium where F > 0 requires K/r^2 > M.
  - "Gravity horizon" at r* = sqrt(K/M): beyond this, the planet can't
    extract surplus -- it starves. That is NEW and testable.
  - Inside r*: F = K/r^2 - M, which is approximately Newton for r << r*
    (where M term is negligible) and deviates toward r*.

Under Variant A, with C_cap fixed:
  - Inner: F = C_cap - M (still a constant but REDUCED by renewal)
  - Outer: F = K/r^2 - M (same "gravity horizon" structure)

Run mass sweep for both variants, measure:
  - r_eq (inner-outer boundary)
  - r* (gravity horizon -- starvation radius)
  - Orbital period T vs r for each mass -- does m fall out or scale?
"""

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


# -- Coupling + integrator --
K = 400.0
ALPHA = 0.5
DT = 0.005
STEPS = 400_000
SNAP_EVERY = 200


def simulate(r0, vt0, M, C_cap, label):
    """Integrate one orbit.

    Force / acceleration convention (tick bookkeeping):
      renewal  = M
      pool     = B + K/r_eff^2
      consumed = min(pool, C_cap)
      surplus  = max(0, consumed - renewal)
      F        = surplus (magnitude, direction -r_hat)
      a        = F / M
      B'       = pool - consumed
    """
    x, y = r0, 0.0
    vx, vy = 0.0, vt0
    B = 0.0

    traj = np.empty((STEPS // SNAP_EVERY + 1, 7), dtype=np.float64)
    k = 0

    for step in range(STEPS):
        r = max(np.hypot(x, y), 1e-6)
        r_eff = r + ALPHA * B
        arrival = K / (r_eff * r_eff)
        pool = B + arrival
        consumed = min(pool, C_cap)
        surplus = max(0.0, consumed - M)
        B = pool - consumed

        rx, ry = x / r, y / r
        ax, ay = -surplus / M * rx, -surplus / M * ry

        vx += ax * DT
        vy += ay * DT
        x += vx * DT
        y += vy * DT

        if step % SNAP_EVERY == 0:
            traj[k] = (x, y, r, r_eff, np.hypot(vx, vy), B, surplus)
            k += 1

        if r > 20 * np.sqrt(K / max(M, 0.01)) or r < 0.05:
            traj = traj[:k]
            return traj, label + " (unbound/crash)"

    traj = traj[:k]
    return traj, label


def find_r_eq_and_rstar(M, C_cap):
    """Analytic radii for diagnostic comparison:

    r_eq  : where K/r_eq^2 = C_cap (buffer activation)
            sqrt(K / C_cap)
    r_star: where K/r_star^2 = M  (gravity horizon -- starves beyond)
            sqrt(K / M)
    """
    r_eq = float(np.sqrt(K / C_cap))
    r_star = float(np.sqrt(K / M))
    return r_eq, r_star


def circular_v(r, M, C_cap):
    """Circular orbital speed at r under (M, C_cap), using a = surplus/M.

    Outer regime (arrival-limited), surplus = K/r^2 - M:
      v^2/r = (K/r^2 - M) / M
      v^2   = r * (K/r^2 - M) / M = K/(r*M) - r
      Must be > 0 => r < r_star.

    Inner regime (capacity-limited), surplus = C_cap - M (constant):
      v^2/r = (C_cap - M) / M
      v^2   = r * (C_cap - M) / M
      Must be > 0 => C_cap > M.
    """
    r_eq, _ = find_r_eq_and_rstar(M, C_cap)
    if r <= r_eq:
        surplus = C_cap - M
    else:
        surplus = K / (r * r) - M
    if surplus <= 0:
        return 0.0
    return float(np.sqrt(r * surplus / M))


def run_sweep(variant, masses, C_cap_fn, r_tests, out_png):
    """Run a mass sweep for one variant."""
    print(f"\n=== Variant {variant} ===")
    cases = []
    for M in masses:
        C_cap = C_cap_fn(M)
        r_eq, r_star = find_r_eq_and_rstar(M, C_cap)
        print(f"  M = {M:>5.2f}  C_cap = {C_cap:>6.2f}  "
              f"r_eq = {r_eq:>5.2f}  r_star = {r_star:>5.2f}")
        for r0 in r_tests:
            v0 = circular_v(r0, M, C_cap)
            if v0 <= 0:
                continue
            label = f"M={M}, r0={r0:.1f}"
            cases.append((simulate(r0, v0, M, C_cap, label), M, r0, C_cap, v0))

    # Report settled (r, T) for each run, to compare vs Kepler T^2 prop r^3
    print(f"\n  {'label':<28} {'r_mean':>7} {'r_amp':>7} "
          f"{'T_meas':>8} {'T_kepler':>9}")
    print("  " + "-" * 64)
    r_means, T_means, M_of, r0_of, kepler_of = [], [], [], [], []
    for (traj, label), M, r0, C_cap, v0 in cases:
        if len(traj) < 10:
            print(f"    {label:<26} (too short)")
            continue
        # Last 60% of trajectory
        tail = traj[int(0.4 * len(traj)):]
        ang = np.unwrap(np.arctan2(tail[:, 1], tail[:, 0]))
        revs = (ang[-1] - ang[0]) / (2 * np.pi)
        t_elapsed = (len(tail) - 1) * SNAP_EVERY * DT
        T_meas = t_elapsed / abs(revs) if abs(revs) > 0.1 else float('nan')
        r_mean = tail[:, 2].mean()
        r_amp = tail[:, 2].max() - tail[:, 2].min()

        # Kepler reference with mass-independent force: F = K/r^2 directly
        # (no renewal subtraction). Period under this baseline.
        T_kepler = 2 * np.pi * np.sqrt(r_mean ** 3 / K) if r_mean > 0 else float('nan')

        print(f"    {label:<26} {r_mean:>7.2f} {r_amp:>7.2f} "
              f"{T_meas:>8.2f} {T_kepler:>9.2f}")

        r_means.append(r_mean)
        T_means.append(T_meas)
        M_of.append(M)
        r0_of.append(r0)
        kepler_of.append(T_kepler)

    # Plot T(r) per mass, and T/T_kepler to see if Newton is recovered
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    unique_M = sorted(set(M_of))
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_M)))
    for c, M in zip(colors, unique_M):
        idx = [i for i, mm in enumerate(M_of) if mm == M]
        rs = [r_means[i] for i in idx]
        Ts = [T_means[i] for i in idx]
        T_k = [kepler_of[i] for i in idx]
        axes[0].plot(rs, Ts, 'o-', color=c, lw=1, label=f'M={M}')
        ratio = [t/tk if (not np.isnan(t) and tk > 0) else np.nan
                 for t, tk in zip(Ts, T_k)]
        axes[1].plot(rs, ratio, 'o-', color=c, lw=1, label=f'M={M}')

    axes[0].set_xlabel('r_mean')
    axes[0].set_ylabel('measured period T')
    axes[0].set_title(f'Variant {variant}: T vs r per mass')
    axes[0].set_xscale('log'); axes[0].set_yscale('log')
    axes[0].grid(True, which='both', alpha=0.3); axes[0].legend(fontsize=8)

    axes[1].axhline(1.0, color='k', ls='--', alpha=0.4, label='Newton baseline')
    axes[1].set_xlabel('r_mean')
    axes[1].set_ylabel('T_measured / T_kepler_baseline')
    axes[1].set_title(f'Variant {variant}: mass-dependence of period')
    axes[1].grid(True, alpha=0.3); axes[1].legend(fontsize=8)

    plt.suptitle(f'Phase 3.1 mass sweep, {variant}', fontsize=12)
    plt.tight_layout()
    path = os.path.join(OUT, out_png)
    plt.savefig(path, dpi=140)
    plt.close()
    print(f"  Saved: {path}")


def run():
    masses = [0.25, 0.5, 1.0, 2.0, 4.0]
    r_tests = [10.0, 15.0, 20.0, 25.0, 30.0]

    # Variant A: C_cap fixed -- planet capacity unrelated to mass
    run_sweep("A (C_cap fixed = 1.0)",
              masses,
              C_cap_fn=lambda M: 1.0,
              r_tests=r_tests,
              out_png="phase3_1_variant_A.png")

    # Variant B: C_cap scales with mass -- each node has unit capacity
    run_sweep("B (C_cap = 1.5 * M per node)",
              masses,
              C_cap_fn=lambda M: 1.5 * M,
              r_tests=r_tests,
              out_png="phase3_1_variant_B.png")


if __name__ == '__main__':
    run()
