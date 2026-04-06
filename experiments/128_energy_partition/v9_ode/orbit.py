#!/usr/bin/env python3
"""
Experiment 128 v9 — The ODE: Orbital Mechanics from Consumption Dynamics

No graph. No nodes. No deposits. No connectors.
Just the equations that the graph experiments discovered:

  Star emits at rate L (total deposits/tick)
  At distance r, flux = L / (4 * pi * r^2)
  Planet has processing capacity P (deposits/tick it can transform)
  Intake = flux at planet's distance
  Consumed = min(intake, P)
  Excess = max(0, intake - P)

  Radial force: consumption pulls inward, excess pushes outward
  Tangential force: excess redirected by angle alpha -> orbital thrust

  r_eq = sqrt(L / (4 * pi * P))  — where intake = capacity
"""

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)

# ── Parameters ──
L_STAR = 10000.0       # star total emission rate (deposits/tick)
P_PLANET = 500.0       # planet processing capacity (deposits/tick)
M_PLANET = 1.0         # planet "mass" (inertia)
DT = 0.01              # time step
STEPS = 500000

# Equilibrium distance
R_EQ = np.sqrt(L_STAR / (4 * np.pi * P_PLANET))
print(f"Parameters: L_star={L_STAR}, P_planet={P_PLANET}")
print(f"Equilibrium distance: r_eq = {R_EQ:.3f}")


def simulate(r0, v_tangential_0, redirect_angle_deg, label):
    """Simulate orbital dynamics from consumption equations.

    r0: initial distance from star
    v_tangential_0: initial tangential velocity
    redirect_angle_deg: angle of reject stream (0=radial out, 90=tangential)
    """
    alpha = np.radians(redirect_angle_deg)

    # State: [x, y, vx, vy]
    x = r0
    y = 0.0
    vx = 0.0
    vy = v_tangential_0

    trajectory = []

    for step in range(STEPS):
        r = np.sqrt(x*x + y*y)
        if r < 0.01:
            r = 0.01  # prevent singularity

        # Star flux at distance r
        flux = L_STAR / (4 * np.pi * r * r)

        # Planet consumption
        consumed = min(flux, P_PLANET)
        excess = max(0.0, flux - P_PLANET)

        # Radial direction (from star to planet)
        rx, ry = x / r, y / r

        # Tangential direction (perpendicular, consistent handedness)
        tx, ty = -ry, rx

        # FORCES from consumption dynamics:
        # 1. Consumption pull (inward) - shortening star-facing connectors
        #    Proportional to consumption rate and distance
        f_consumption = -consumed / r  # inward, stronger when closer

        # 2. Radiation pressure (outward) - excess deposits extend connectors
        f_radiation = excess / r  # outward, only when flux > capacity

        # 3. Tangential thrust from redirected excess
        f_tangential = excess * np.sin(alpha)  # sideways

        # Net radial force
        f_radial = f_consumption + f_radiation

        # Acceleration
        ax = f_radial * rx + f_tangential * tx
        ay = f_radial * ry + f_tangential * ty

        # Update velocity and position (Euler integration)
        vx += ax * DT / M_PLANET
        vy += ay * DT / M_PLANET
        x += vx * DT
        y += vy * DT

        if step % 100 == 0:
            trajectory.append((x, y, r, np.sqrt(vx*vx+vy*vy)))

    return np.array(trajectory), label


def run():
    print(f"\nRunning ODE simulations ({STEPS} steps each)...\n")

    results = []

    # Test 1: No tangential, starting at r_eq (should stay)
    results.append(simulate(R_EQ, 0.0, 0, "At r_eq, no kick, alpha=0"))

    # Test 2: No tangential, starting far (should fall in)
    results.append(simulate(R_EQ * 2, 0.0, 0, "Far, no kick, alpha=0"))

    # Test 3: Tangential kick at r_eq, no redirect
    v_circ = np.sqrt(P_PLANET / R_EQ)  # rough circular velocity estimate
    results.append(simulate(R_EQ, v_circ, 0, f"At r_eq, v_circ={v_circ:.2f}, alpha=0"))

    # Test 4: Tangential kick + 45 degree redirect
    results.append(simulate(R_EQ, v_circ * 0.5, 45, "At r_eq, half v_circ, alpha=45"))

    # Test 5: Tangential kick + 90 degree redirect (full tangential exhaust)
    results.append(simulate(R_EQ, v_circ * 0.3, 90, "At r_eq, 0.3*v_circ, alpha=90"))

    # Test 6: Start inside r_eq with tangential kick (excess flux -> thrust)
    results.append(simulate(R_EQ * 0.5, v_circ, 90, "Inside r_eq, v_circ, alpha=90"))

    # Test 7: Various redirect angles at same initial conditions
    for alpha in [0, 30, 45, 60, 90]:
        results.append(simulate(R_EQ * 0.7, v_circ * 0.5, alpha,
                                f"r=0.7*r_eq, 0.5*v, alpha={alpha}"))

    # Print summary
    for traj, label in results:
        r_final = traj[-1, 2]
        r_min = traj[:, 2].min()
        r_max = traj[:, 2].max()
        # Angular displacement
        angles = np.arctan2(traj[:, 1], traj[:, 0])
        total_angle = np.abs(np.diff(np.unwrap(angles))).sum()
        net_angle = np.unwrap(angles)[-1] - np.unwrap(angles)[0]
        revolutions = net_angle / (2 * np.pi)

        print(f"  {label}")
        print(f"    r: {r_min:.3f} - {r_max:.3f} (final {r_final:.3f}, eq={R_EQ:.3f})")
        print(f"    angle: {np.degrees(net_angle):.1f} deg ({revolutions:.2f} rev)")
        print()

    plot(results)


def plot(results):
    # Separate plots: trajectories, distance vs time, phase portraits
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f'Experiment 128 v9: Consumption ODE (r_eq={R_EQ:.2f})', fontsize=14)

    colors = plt.cm.tab10(np.linspace(0, 1, len(results)))

    # 1. XY trajectories (first 6)
    ax = axes[0, 0]
    for i, (traj, label) in enumerate(results[:6]):
        ax.plot(traj[:, 0], traj[:, 1], '-', color=colors[i], linewidth=0.5,
                label=label[:30], alpha=0.7)
    ax.plot(0, 0, 'y*', markersize=15)
    circle = plt.Circle((0, 0), R_EQ, fill=False, color='gray', linestyle='--', alpha=0.3)
    ax.add_patch(circle)
    ax.set_aspect('equal'); ax.set_title('Trajectories')
    ax.legend(fontsize=6); ax.grid(True, alpha=0.3)

    # 2. Distance vs time (first 6)
    ax = axes[0, 1]
    for i, (traj, label) in enumerate(results[:6]):
        ax.plot(range(len(traj)), traj[:, 2], '-', color=colors[i], linewidth=0.5,
                label=label[:30], alpha=0.7)
    ax.axhline(R_EQ, color='gray', linestyle='--', alpha=0.3, label=f'r_eq={R_EQ:.2f}')
    ax.set_ylabel('Distance'); ax.set_title('Distance vs Time')
    ax.legend(fontsize=6); ax.grid(True, alpha=0.3)

    # 3. Speed vs time (first 6)
    ax = axes[0, 2]
    for i, (traj, label) in enumerate(results[:6]):
        ax.plot(range(len(traj)), traj[:, 3], '-', color=colors[i], linewidth=0.5,
                label=label[:30], alpha=0.7)
    ax.set_ylabel('Speed'); ax.set_title('Speed vs Time')
    ax.legend(fontsize=6); ax.grid(True, alpha=0.3)

    # 4. Alpha sweep trajectories
    ax = axes[1, 0]
    alpha_results = [r for r in results if "alpha=" in r[1] and "r=0.7" in r[1]]
    for i, (traj, label) in enumerate(alpha_results):
        ax.plot(traj[:, 0], traj[:, 1], '-', linewidth=0.8, label=label[-10:])
    ax.plot(0, 0, 'y*', markersize=15)
    circle = plt.Circle((0, 0), R_EQ, fill=False, color='gray', linestyle='--', alpha=0.3)
    ax.add_patch(circle)
    ax.set_aspect('equal'); ax.set_title('Alpha Sweep (r=0.7*r_eq)')
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    # 5. Alpha sweep distances
    ax = axes[1, 1]
    for i, (traj, label) in enumerate(alpha_results):
        ax.plot(range(len(traj)), traj[:, 2], '-', linewidth=0.8, label=label[-10:])
    ax.axhline(R_EQ, color='gray', linestyle='--', alpha=0.3)
    ax.set_ylabel('Distance'); ax.set_title('Alpha Sweep Distance')
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    # 6. Best orbit (if any shows multiple revolutions)
    ax = axes[1, 2]
    # Find the result with the most revolutions
    best_rev = 0
    best_idx = 0
    for i, (traj, label) in enumerate(results):
        angles = np.unwrap(np.arctan2(traj[:, 1], traj[:, 0]))
        rev = abs(angles[-1] - angles[0]) / (2 * np.pi)
        if rev > best_rev:
            best_rev = rev
            best_idx = i
    traj, label = results[best_idx]
    n = len(traj)
    colors_t = plt.cm.viridis(np.linspace(0, 1, n))
    for i in range(1, n):
        ax.plot(traj[i-1:i+1, 0], traj[i-1:i+1, 1], '-', color=colors_t[i], linewidth=0.8)
    ax.plot(0, 0, 'y*', markersize=15)
    circle = plt.Circle((0, 0), R_EQ, fill=False, color='gray', linestyle='--', alpha=0.3)
    ax.add_patch(circle)
    ax.set_aspect('equal')
    ax.set_title(f'Best orbit: {label}\n({best_rev:.1f} rev)')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "results.png"), dpi=150)
    plt.close()
    print(f"Saved: results.png")


if __name__ == '__main__':
    run()
