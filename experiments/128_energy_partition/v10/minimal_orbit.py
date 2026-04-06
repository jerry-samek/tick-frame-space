#!/usr/bin/env python3
"""
Experiment 128 v10 — Minimal Orbit: One Star, One Planet, One Connector

Strip EVERYTHING to minimum. No graph. No nodes. Just:
  - Star: produces L deposits per tick, pushes onto the connector
  - Connector: carries deposits from star to planet, has a length
  - Planet: consumes from connector, consumption IS movement
  - Radiation: /dev/null (excess leaves the system)
  - 10% resistance: planet consumes 10% of arriving flux per tick

The planet has continuous position (r, theta).
Radial force: from consumption on the connector.
Tangential: from initial velocity (inherited).

Does this single connector produce orbital dynamics?
"""

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)

# ── Star ──
L_STAR = 1000.0       # total emission rate (deposits/tick, all directions)

# ── Planet ──
RESISTANCE = 0.10      # planet consumes 10% of arriving flux
INITIAL_R = 40.0       # starting distance

# ── Simulation ──
DT = 0.01
STEPS = 2000000


def sim(initial_vt, label):
    """Simulate one orbit attempt.

    The star emits L deposits/tick isotropically. At distance r, the
    flux on the star-planet connector is L / (4*pi*r^2).

    The deposit propagates along the connector (push mechanism).
    The connector length IS the distance r.

    Each tick:
      1. Flux arrives at planet: f = L / (4*pi*r^2)
      2. Planet consumes: consumed = f * RESISTANCE
      3. Excess = f - consumed -> /dev/null (radiation, child bodies)
      4. Consumed deposit had direction TOWARD planet (from star)
         -> this IS the inward force (gravity)
      5. Planet position updates: velocity += consumed_force * dt
         position += velocity * dt
    """
    # State: position in polar-ish coordinates but tracked as x,y
    x = INITIAL_R
    y = 0.0
    vx = 0.0
    vy = initial_vt

    traj = []
    total_consumed = 0.0

    for step in range(STEPS):
        r = max(np.sqrt(x*x + y*y), 0.01)
        rx, ry = x/r, y/r    # radial outward
        tx, ty = -ry, rx      # tangential

        # Flux at distance r (geometric dilution)
        flux = L_STAR / (4 * np.pi * r * r)

        # Planet consumes RESISTANCE fraction of flux
        consumed = flux * RESISTANCE

        # The consumed deposit's momentum is INWARD (from star to planet)
        # This IS the gravitational force — not assumed, but from
        # the consumption of directional deposits
        # Force magnitude = consumed (momentum per tick absorbed)
        # Force direction = -radial (toward star)
        fx = -consumed * rx
        fy = -consumed * ry

        # Update velocity and position
        vx += fx * DT
        vy += fy * DT
        x += vx * DT
        y += vy * DT

        total_consumed += consumed

        if step % 500 == 0:
            traj.append((x, y, r, np.sqrt(vx*vx+vy*vy), total_consumed))

    return np.array(traj), label


def run():
    # Equilibrium: where consumed provides circular orbit
    # F = consumed = L*R / (4*pi*r^2) (inward)
    # For circular: F = v^2/r -> L*R/(4*pi*r^2) = v^2/r
    # v^2 = L*R/(4*pi*r) -> v = sqrt(L*R/(4*pi*r))
    # At r=40: v_circ = sqrt(1000*0.1 / (4*pi*40)) = sqrt(100/502.7) = 0.446

    v_circ_40 = np.sqrt(L_STAR * RESISTANCE / (4 * np.pi * INITIAL_R))
    print(f"L_star={L_STAR}, Resistance={RESISTANCE}")
    print(f"v_circular at r={INITIAL_R}: {v_circ_40:.4f}")
    print(f"Running {STEPS} steps at dt={DT}...")

    results = []

    # Sweep tangential velocities around v_circ
    for vt_frac in [0.0, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0]:
        vt = v_circ_40 * vt_frac
        results.append(sim(vt, f"vt={vt_frac:.1f}*vc={vt:.4f}"))

    # Print results
    print(f"\n{'Label':<30} {'r_min':>8} {'r_max':>8} {'r_final':>8} {'revs':>8} {'consumed':>10}")
    print("-" * 80)
    for traj, label in results:
        r = traj[:, 2]
        ang = np.unwrap(np.arctan2(traj[:, 1], traj[:, 0]))
        rev = (ang[-1] - ang[0]) / (2 * np.pi)
        esc = " ESC" if r[-1] > 1000 else ""
        coll = " COLL" if r.min() < 0.1 else ""
        print(f"  {label:<28} {r.min():>8.2f} {r.max():>8.2f} {r[-1]:>8.2f} "
              f"{rev:>8.1f} {traj[-1,4]:>10.0f}{esc}{coll}")

    plot(results)


def plot(results):
    n_res = len(results)
    fig, axes = plt.subplots(3, n_res, figsize=(4*n_res, 12))
    fig.suptitle(f'v10 Minimal Orbit: L={L_STAR}, R={RESISTANCE}, r0={INITIAL_R}',
                 fontsize=14)

    for col, (traj, label) in enumerate(results):
        n = len(traj)
        colors = plt.cm.viridis(np.linspace(0, 1, min(n, 4000)))

        # Row 1: XY trajectory
        ax = axes[0, col]
        px, py = traj[:, 0], traj[:, 1]
        lim = min(max(abs(px).max(), abs(py).max(), INITIAL_R) * 1.2, 200)
        for i in range(1, min(n, 4000)):
            ax.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], lw=0.3)
        ax.plot(0, 0, 'y*', ms=8)
        ax.plot(px[0], py[0], 'go', ms=5)
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
        ax.set_aspect('equal')
        ang = np.unwrap(np.arctan2(traj[:, 1], traj[:, 0]))
        rev = (ang[-1] - ang[0]) / (2 * np.pi)
        ax.set_title(f'{label}\n{rev:.1f} rev', fontsize=8)
        ax.grid(True, alpha=0.3)

        # Row 2: distance
        ax = axes[1, col]
        ax.plot(range(n), traj[:, 2], 'b-', lw=0.3)
        ax.axhline(INITIAL_R, color='gray', ls='--', alpha=0.3)
        ax.set_ylabel('r')
        ax.grid(True, alpha=0.3)

        # Row 3: speed
        ax = axes[2, col]
        ax.plot(range(n), traj[:, 3], 'g-', lw=0.3)
        ax.set_ylabel('speed')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "minimal_orbit.png"), dpi=150)
    plt.close()
    print(f"\nSaved: minimal_orbit.png")


if __name__ == '__main__':
    run()
