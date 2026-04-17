#!/usr/bin/env python3
"""
Experiment 128 v11 - Arrival Rig, Phase 3: Buffered Consumption Orbit

Phase 1 showed the graph produces 1/r^2. Phase 2 showed the measured
field gives Keplerian orbits. Both assume the planet consumes a fixed
fraction of arriving flux - which means any starting (r, v) not matching
circular balance gives an ellipse. Orbits are delicate integrals.

This Phase tests a different hypothesis: **the planet has a MAX
consumption rate C_max**. Anything the planet can't process accumulates
on the star-planet connector as a buffer of unconsumed deposits - the
Same/Different extension rule from RAW 113 applied to one connector.
The buffer IS the connector's Different deposits.

The buffer physically extends the connector:
  r_eff = r_geom + alpha * B
and the force the planet experiences is computed at r_eff, not r_geom.

Consequence: orbits become **attractors**. A planet starting too close
overloads (arrival > C_max), buffer fills, r_eff grows, force drops,
planet drifts out. A planet starting too far underloads (arrival < C_max),
buffer drains, r_eff shrinks, force rises, planet drifts in. System
relaxes to the equilibrium where arrival = C_max exactly.

Equilibrium:
  arrival = k / r_eff^2 = C_max
  => r_eff_eq = sqrt(k / C_max)
  centripetal balance at r_geom:  v^2 = r_geom * C_max

Per-tick dynamics:
  pool = B + k / r_eff^2              (new arrivals join buffer)
  consumed = min(pool, C_max)          (planet consumes what it can)
  B' = pool - consumed                 (remaining stays buffered)
  F = consumed * (-r_hat)              (consumption IS the force)
"""

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


# -- Force / coupling --
# k is the "gravitational coupling"; same role as GM or L/4pi in Newton.
K = 400.0
C_MAX = 1.0           # planet max consumption rate (deposits per tick)
ALPHA = 0.5           # r_eff per unit of buffer (connector-length per unconsumed deposit)

# Equilibrium: r_eff_eq = sqrt(K / C_MAX) = 20.0
R_EQ = float(np.sqrt(K / C_MAX))

# -- Integration --
DT = 0.005
STEPS = 400_000
SNAP_EVERY = 100


def simulate(r0, vt0, label, buffer_init=0.0):
    """Integrate one planet under the buffered-consumption force.

    State: x, y, vx, vy, B (buffer).
    Returns trajectory (N, 6): x, y, r_geom, r_eff, speed, buffer.
    """
    x, y = r0, 0.0
    vx, vy = 0.0, vt0
    B = buffer_init

    traj = np.empty((STEPS // SNAP_EVERY + 1, 6), dtype=np.float64)
    k = 0

    for step in range(STEPS):
        r = max(np.hypot(x, y), 1e-6)
        r_eff = r + ALPHA * B

        # Arrivals this tick, pool = buffer + new arrivals
        arrival = K / (r_eff * r_eff)
        pool = B + arrival
        consumed = min(pool, C_MAX)
        B = pool - consumed  # remaining sits on the connector

        # Force magnitude = consumption (consumption IS the force, v10/v9 doctrine)
        f_mag = consumed
        rx, ry = x / r, y / r
        fx, fy = -f_mag * rx, -f_mag * ry

        vx += fx * DT
        vy += fy * DT
        x += vx * DT
        y += vy * DT

        if step % SNAP_EVERY == 0:
            traj[k] = (x, y, r, r_eff, np.hypot(vx, vy), B)
            k += 1

        # safety
        if r > 5 * R_EQ or r < 0.1:
            traj = traj[:k]
            return traj, label + " (unbound/crash)"

    traj = traj[:k]
    return traj, label


def run():
    print(f"K = {K}, C_MAX = {C_MAX}, ALPHA = {ALPHA}")
    print(f"  => equilibrium r_eff = {R_EQ:.3f}")
    print(f"  => at r_geom = r_eff_eq, v_circ = sqrt(r * C_MAX) = "
          f"{np.sqrt(R_EQ * C_MAX):.3f}")
    print()

    # Circular velocity: differs by regime
    #   inside r_eq: capacity-limited, F = C_MAX,    v^2 = r * C_MAX
    #   outside:     arrival-limited, F = K / r^2,   v^2 = K / r
    def v_circ(r):
        if r <= R_EQ:
            return np.sqrt(r * C_MAX)
        return np.sqrt(K / r)

    # Set of initial conditions to probe the attractor.
    # Use the CORRECT v_circ for each regime. Things still interesting are
    # (a) does the planet sit stably at the starting r? (b) does the buffer
    # adjust r_eff? (c) what happens to off-tuned initial velocities?
    cases = [
        ("inside, v_circ  (r0=10)",   10.0, v_circ(10.0),       0.0),
        ("at  eq, v_circ  (r0=20)",   20.0, v_circ(20.0),       0.0),
        ("outside, v_circ (r0=30)",   30.0, v_circ(30.0),       0.0),
        ("inside,  slow  (80% v_c)",  10.0, 0.8 * v_circ(10.0), 0.0),
        ("outside, slow  (80% v_c)",  30.0, 0.8 * v_circ(30.0), 0.0),
        ("inside,  fast (120% v_c)",  10.0, 1.2 * v_circ(10.0), 0.0),
    ]

    results = [simulate(r0, vt, lab, B0) for lab, r0, vt, B0 in cases]

    # Summary
    print(f"{'label':<30} {'r_geom':>14} {'r_eff':>14} {'B_final':>9}  status")
    print("-" * 78)
    for traj, label in results:
        if len(traj) < 2:
            print(f"  {label:<28} (empty)")
            continue
        r_g = traj[:, 2]
        r_e = traj[:, 3]
        B_f = traj[-1, 5]
        status = "unbound" if "unbound" in label else "bound"
        # last 25% of trajectory — call it settled
        tail = traj[int(0.75 * len(traj)):]
        r_g_mean = tail[:, 2].mean()
        r_e_mean = tail[:, 3].mean()
        r_g_amp = tail[:, 2].max() - tail[:, 2].min()
        r_e_amp = tail[:, 3].max() - tail[:, 3].min()
        print(f"  {label:<28} {r_g_mean:>6.2f}+-{r_g_amp:<5.2f} "
              f"{r_e_mean:>6.2f}+-{r_e_amp:<5.2f} {B_f:>9.2f}  {status}")

    plot(results)


def plot(results):
    n = len(results)
    fig = plt.figure(figsize=(16, 4 * n))
    gs = fig.add_gridspec(n, 4, hspace=0.4, wspace=0.3)

    for row, (traj, label) in enumerate(results):
        if len(traj) < 2:
            continue
        t = np.arange(len(traj)) * SNAP_EVERY * DT

        # Panel 1: trajectory in xy
        ax = fig.add_subplot(gs[row, 0])
        lim = max(traj[:, :2].max(), -traj[:, :2].min(), R_EQ * 1.3)
        lim = min(lim, 5 * R_EQ)
        n_pts = min(len(traj), 4000)
        colors = plt.cm.viridis(np.linspace(0, 1, n_pts))
        for i in range(1, n_pts):
            ax.plot(traj[i-1:i+1, 0], traj[i-1:i+1, 1],
                    '-', color=colors[i], lw=0.3)
        ax.plot(0, 0, 'y*', ms=10)
        circ_eq = plt.Circle((0, 0), R_EQ, fill=False, edgecolor='gray',
                             linestyle='--', linewidth=0.8)
        ax.add_patch(circ_eq)
        ax.plot(traj[0, 0], traj[0, 1], 'go', ms=5)
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
        ax.set_aspect('equal')
        ax.set_title(f'{label}\nxy (dashed = r_eq)', fontsize=9)
        ax.grid(True, alpha=0.3)

        # Panel 2: r_geom and r_eff over time
        ax = fig.add_subplot(gs[row, 1])
        ax.plot(t, traj[:, 2], 'b-', lw=0.5, label='r_geom')
        ax.plot(t, traj[:, 3], 'r-', lw=0.5, alpha=0.7, label='r_eff')
        ax.axhline(R_EQ, color='gray', ls='--', alpha=0.5, label='r_eq')
        ax.set_ylabel('radius'); ax.set_xlabel('time')
        ax.set_title('r_geom and r_eff'); ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        # Panel 3: buffer over time
        ax = fig.add_subplot(gs[row, 2])
        ax.plot(t, traj[:, 5], 'purple', lw=0.5)
        ax.set_ylabel('buffer B'); ax.set_xlabel('time')
        ax.set_title('connector buffer (Different deposits)')
        ax.grid(True, alpha=0.3)

        # Panel 4: speed
        ax = fig.add_subplot(gs[row, 3])
        ax.plot(t, traj[:, 4], 'g-', lw=0.5)
        ax.axhline(np.sqrt(R_EQ * C_MAX), color='gray', ls='--', alpha=0.5,
                   label='v_circ(r_eq)')
        ax.set_ylabel('speed'); ax.set_xlabel('time')
        ax.set_title('orbital speed'); ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.suptitle(f'v11 Phase 3: Buffered consumption - '
                 f'K={K}, C_max={C_MAX}, alpha={ALPHA}, r_eq={R_EQ:.1f}',
                 fontsize=13, y=0.995)
    out = os.path.join(OUT, 'phase3_buffered.png')
    plt.savefig(out, dpi=130, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {out}")


if __name__ == '__main__':
    run()
