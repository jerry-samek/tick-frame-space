#!/usr/bin/env python3
"""
Experiment 128 v9 — ODE v2: Three-Way Partition

Excess flux splits THREE ways (RAW 128):
  1. Tangential thrust (orbit) — fraction f_t
  2. Radial pressure (outward push) — fraction f_r
  3. Radiation (energy LEAVES the system) — fraction f_rad

f_t + f_r + f_rad = 1

Radiation is the energy sink that stabilizes orbits.
Without it, tangential thrust always wins → escape.
"""

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

L_STAR = 10000.0
P_PLANET = 500.0
M_PLANET = 1.0
DT = 0.01
STEPS = 500000

R_EQ = np.sqrt(L_STAR / (4 * np.pi * P_PLANET))
print(f"r_eq = {R_EQ:.3f}")


def simulate(r0, vt0, f_tangential, f_radial, f_radiation, label):
    """Three-way partition orbital dynamics.

    f_tangential: fraction of excess going to orbital thrust
    f_radial: fraction of excess going to outward push
    f_radiation: fraction of excess radiated away (energy sink)
    """
    assert abs(f_tangential + f_radial + f_radiation - 1.0) < 0.001

    x, y = r0, 0.0
    vx, vy = 0.0, vt0

    traj = []
    for step in range(STEPS):
        r = max(np.sqrt(x*x + y*y), 0.01)
        rx, ry = x/r, y/r
        tx, ty = -ry, rx

        flux = L_STAR / (4 * np.pi * r * r)
        consumed = min(flux, P_PLANET)
        excess = max(0.0, flux - P_PLANET)

        # Consumption: inward pull (gravity from connector shortening)
        f_grav = -consumed / r

        # Three-way partition of excess:
        f_thrust = excess * f_tangential  # tangential orbital thrust
        f_push = excess * f_radial        # radial outward pressure
        # f_radiation * excess is LOST — not applied as force

        f_rad_net = f_grav + f_push / r   # net radial (inward + outward)

        ax = f_rad_net * rx + f_thrust * tx / r
        ay = f_rad_net * ry + f_thrust * ty / r

        vx += ax * DT / M_PLANET
        vy += ay * DT / M_PLANET
        x += vx * DT
        y += vy * DT

        if step % 100 == 0:
            traj.append((x, y, r, np.sqrt(vx*vx + vy*vy)))

    return np.array(traj), label


def run():
    print(f"\nThree-way partition ODE ({STEPS} steps)\n")

    results = []

    # Baseline: classical orbit (no excess partitioning, just initial velocity)
    v_circ = np.sqrt(P_PLANET / R_EQ)
    results.append(simulate(R_EQ * 0.7, v_circ * 0.5, 0, 0, 1.0,
                            "alpha=0 (classical)"))

    # Sweep radiation fraction: how much excess must be radiated for stable orbit?
    for f_rad in [0.0, 0.5, 0.8, 0.9, 0.95, 0.99]:
        f_t = (1 - f_rad) * 0.5   # half of non-radiated goes tangential
        f_r = (1 - f_rad) * 0.5   # half goes radial
        results.append(simulate(R_EQ * 0.7, v_circ * 0.3, f_t, f_r, f_rad,
                                f"rad={f_rad:.2f} t={f_t:.3f} r={f_r:.3f}"))

    # Sweep tangential/radial split at fixed radiation
    for f_t_frac in [0.0, 0.2, 0.5, 0.8, 1.0]:
        f_rad = 0.9
        f_t = (1 - f_rad) * f_t_frac
        f_r = (1 - f_rad) * (1 - f_t_frac)
        results.append(simulate(R_EQ * 0.7, v_circ * 0.3, f_t, f_r, f_rad,
                                f"90%rad: t_frac={f_t_frac:.1f}"))

    # Print summary
    print(f"{'Label':<35} {'r_min':>8} {'r_max':>8} {'r_final':>8} {'revs':>8}")
    print("-" * 75)
    for traj, label in results:
        r = traj[:, 2]
        angles = np.unwrap(np.arctan2(traj[:, 1], traj[:, 0]))
        rev = (angles[-1] - angles[0]) / (2 * np.pi)
        # Check if escaped
        escaped = "ESC" if r[-1] > 100 else ""
        print(f"  {label:<33} {r.min():>8.3f} {r.max():>8.3f} {r[-1]:>8.3f} {rev:>8.2f} {escaped}")

    plot(results)


def plot(results):
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f'v9 ODE v2: Three-Way Partition (r_eq={R_EQ:.2f})', fontsize=14)

    # 1. Radiation sweep trajectories
    ax = axes[0, 0]
    rad_results = [r for r in results if "rad=" in r[1]]
    for traj, label in rad_results:
        if traj[-1, 2] < 100:  # only plot non-escaped
            ax.plot(traj[:, 0], traj[:, 1], '-', linewidth=0.5, label=label[:20])
        else:
            ax.plot(traj[:200, 0], traj[:200, 1], '--', linewidth=0.3,
                    label=label[:20]+" (esc)", alpha=0.5)
    ax.plot(0, 0, 'y*', ms=12)
    c = plt.Circle((0,0), R_EQ, fill=False, color='gray', ls='--', alpha=0.3)
    ax.add_patch(c)
    ax.set_aspect('equal'); ax.set_title('Radiation Sweep')
    ax.legend(fontsize=6); ax.grid(True, alpha=0.3)

    # 2. Radiation sweep distance
    ax = axes[0, 1]
    for traj, label in rad_results:
        r = np.minimum(traj[:, 2], 10)  # cap for display
        ax.plot(range(len(r)), r, '-', linewidth=0.8, label=label[:20])
    ax.axhline(R_EQ, color='gray', ls='--', alpha=0.3)
    ax.set_ylabel('Distance'); ax.set_title('Distance (radiation sweep)')
    ax.legend(fontsize=6); ax.grid(True, alpha=0.3)

    # 3. Tangential/radial split trajectories (90% radiation)
    ax = axes[0, 2]
    split_results = [r for r in results if "90%rad" in r[1]]
    for traj, label in split_results:
        if traj[-1, 2] < 100:
            ax.plot(traj[:, 0], traj[:, 1], '-', linewidth=0.5, label=label[-15:])
        else:
            ax.plot(traj[:500, 0], traj[:500, 1], '--', linewidth=0.3,
                    label=label[-15:]+" (esc)", alpha=0.5)
    ax.plot(0, 0, 'y*', ms=12)
    c = plt.Circle((0,0), R_EQ, fill=False, color='gray', ls='--', alpha=0.3)
    ax.add_patch(c)
    ax.set_aspect('equal'); ax.set_title('T/R Split (90% radiated)')
    ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

    # 4. Best stable orbit (most revolutions without escaping)
    best_rev = 0
    best_idx = 0
    for i, (traj, label) in enumerate(results):
        if traj[-1, 2] > 100:
            continue  # escaped
        angles = np.unwrap(np.arctan2(traj[:, 1], traj[:, 0]))
        rev = abs(angles[-1] - angles[0]) / (2 * np.pi)
        if rev > best_rev:
            best_rev = rev
            best_idx = i

    ax = axes[1, 0]
    traj, label = results[best_idx]
    n = len(traj)
    colors = plt.cm.viridis(np.linspace(0, 1, n))
    for i in range(1, n):
        ax.plot(traj[i-1:i+1, 0], traj[i-1:i+1, 1], '-', color=colors[i], lw=0.8)
    ax.plot(0, 0, 'y*', ms=12)
    c = plt.Circle((0,0), R_EQ, fill=False, color='gray', ls='--', alpha=0.3)
    ax.add_patch(c)
    ax.set_aspect('equal')
    ax.set_title(f'Best orbit: {label}\n({best_rev:.0f} rev)')
    ax.grid(True, alpha=0.3)

    # 5. Best orbit distance over time
    ax = axes[1, 1]
    ax.plot(range(len(traj)), traj[:, 2], 'b-', lw=0.5)
    ax.axhline(R_EQ, color='gray', ls='--', alpha=0.3)
    ax.set_ylabel('Distance'); ax.set_title('Best orbit: distance')
    ax.grid(True, alpha=0.3)

    # 6. Best orbit speed over time
    ax = axes[1, 2]
    ax.plot(range(len(traj)), traj[:, 3], 'g-', lw=0.5)
    ax.set_ylabel('Speed'); ax.set_title('Best orbit: speed')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "results_v2.png"), dpi=150)
    plt.close()
    print(f"\nSaved: results_v2.png")


if __name__ == '__main__':
    run()
