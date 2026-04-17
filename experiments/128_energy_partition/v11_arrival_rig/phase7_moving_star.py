#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 7: Moving Star, Orbiting Planet

The whole solar system moves through the substrate. No orbit is
really closed in the absolute frame. Test: if we move the star along
z at various velocities, does the planet's orbit survive? At what
velocity does the motion break?

Setup:
  - Star at position (0, 0, v_z * t)
  - Planet starts at (r0, 0, 0) with circular-orbit velocity in the xy
    plane (in the star's comoving frame)
  - Gravity is retarded: at time t the planet feels the force from where
    the star WAS at t - t_retarded, with t_retarded solving
         |r_planet(t) - star(t_ret)| = c * (t - t_ret)
    (Deposits on the substrate propagate at c = 1 hop/tick. Our natural
    units have c = 1.)
  - Force magnitude = K/r^2 in the retarded direction
  - No relativistic corrections (pure Newtonian retarded gravity, which
    is how any 1/r^2 force looks when you carry c forward)

Observables:
  - Does the orbit close in the star's comoving frame?
  - Does the orbit drift / precess / deform?
  - Does aberration introduce an inward or outward spiral?
  - At what v_z does the system fail to track?

Unit system: AU, year, M_sun. In these units c = 63241 AU/yr (light
crosses 63,241 AU in a year). So "relativistic" is when v_z is a
substantial fraction of 63241 -- far faster than any real star moves.
This matches reality: stellar motions relative to the CMB are tiny in
units of c, so orbit-level effects are negligible. But in substrate
terms, the qualitative test is still meaningful.
"""

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


# Natural units: K = GM_sun, c = 1 hop/tick expressed as AU/yr
K = 4 * np.pi ** 2              # GM_sun (AU^3/yr^2)
C_LIGHT = 63241.08              # AU/yr
DT = 0.001
STEPS = 200_000                 # 200 yr at dt=0.001
SNAP_EVERY = 50                 # 20 samples per orbital period -> clean revs
INITIAL_R = 1.0                 # planet starts at 1 AU
V_CIRC = np.sqrt(K / INITIAL_R) # = 2*pi AU/yr, standard Earth orbital speed


def star_position(t, v_z):
    return np.array([0.0, 0.0, v_z * t])


def retarded_time(t, r_planet, v_z, c=C_LIGHT, max_iter=8):
    """Solve |r_planet - star(t_ret)| = c * (t - t_ret) iteratively.

    t_ret = t - d/c where d = |r_planet - star(t_ret)|. Iterate.
    Usually converges in 3-4 iterations since v_z << c.
    """
    t_ret = t
    for _ in range(max_iter):
        star_ret = star_position(t_ret, v_z)
        dist = float(np.linalg.norm(r_planet - star_ret))
        t_ret_new = t - dist / c
        if abs(t_ret_new - t_ret) < 1e-10:
            break
        t_ret = t_ret_new
    return t_ret, star_ret


def simulate(v_z, label, comoving=True):
    """Simulate with retarded gravity from a z-moving star.

    comoving=True: planet starts with the star's z-velocity as well
    (physical case for a gravitationally bound system carried along)
    comoving=False: planet starts at rest in z (tests "planet left
    behind" scenario; probably unphysical but diagnostic)
    """
    r_p = np.array([INITIAL_R, 0.0, 0.0])
    vz0 = v_z if comoving else 0.0
    v_p = np.array([0.0, V_CIRC, vz0])

    traj = np.empty((STEPS // SNAP_EVERY + 1, 7))
    k = 0

    for step in range(STEPS):
        t = step * DT
        t_ret, star_ret = retarded_time(t, r_p, v_z)
        disp = r_p - star_ret
        dist = max(float(np.linalg.norm(disp)), 1e-9)
        direction = disp / dist
        f_mag = K / (dist * dist)
        accel = -f_mag * direction
        v_p = v_p + accel * DT
        r_p = r_p + v_p * DT

        if step % SNAP_EVERY == 0:
            star_now = star_position(t, v_z)
            traj[k] = (t, r_p[0], r_p[1], r_p[2],
                       star_now[0], star_now[1], star_now[2])
            k += 1

        dist_from_star_now = float(np.linalg.norm(r_p - star_position(t, v_z)))
        if dist_from_star_now > 50 * INITIAL_R:
            return traj[:k], label + " (UNBOUND)"
        if dist_from_star_now < 0.02 * INITIAL_R:
            return traj[:k], label + " (COLLIDED)"

    return traj[:k], label


def run():
    print(f"K = {K:.3f}, c = {C_LIGHT:.0f} AU/yr, v_circ = {V_CIRC:.3f} AU/yr")
    print(f"Simulating {STEPS} steps * DT={DT} = {STEPS * DT:.1f} yr")
    print()

    # Two scenarios:
    #   (a) comoving: planet carries star's z-velocity. Real case.
    #   (b) rest-planet: planet has only xy velocity. Tests "if you
    #       dropped a planet, would a moving star scoop it up?"
    cases = [
        # (v_z, label, comoving)
        (0.0, "rest (reference)", True),
        (0.1 * V_CIRC, "v_z=0.1*v_c comoving", True),
        (V_CIRC,       "v_z=v_c comoving",     True),
        (10 * V_CIRC,  "v_z=10*v_c comoving",  True),
        (0.001 * C_LIGHT, "v_z=0.001*c comoving", True),
        (0.5 * V_CIRC, "v_z=0.5*v_c NOT comoving", False),
        (V_CIRC,       "v_z=v_c NOT comoving",     False),
    ]

    results = []
    print(f"{'case':<32} {'r_mean_xy':>11} {'z_drift':>10} "
          f"{'revs':>7}  {'status':>10}")
    print("-" * 75)
    for v_z, label, comoving in cases:
        traj, tagged = simulate(v_z, label, comoving=comoving)
        if len(traj) < 4:
            continue
        # Comoving frame: subtract star's z trajectory
        rel = traj[:, 1:4].copy()
        rel[:, 2] = rel[:, 2] - traj[:, 6]   # planet_z - star_z
        # mean xy distance
        r_xy = np.sqrt(rel[:, 0]**2 + rel[:, 1]**2)
        # z drift in comoving frame
        z_range = rel[:, 2].max() - rel[:, 2].min()
        # revolutions in xy
        ang = np.unwrap(np.arctan2(rel[:, 1], rel[:, 0]))
        revs = (ang[-1] - ang[0]) / (2 * np.pi)
        status = "UNBOUND" if "UNBOUND" in tagged \
                 else "COLLIDED" if "COLLIDED" in tagged \
                 else "bound"
        print(f"{label:<32} {r_xy.mean():>12.4f} {z_range:>11.4f} "
              f"{revs:>7.1f}  {status:>18}")
        results.append((traj, label, tagged, rel))

    # Plot: comoving-frame trajectories in xy and xz
    n = len(results)
    fig = plt.figure(figsize=(16, 4 * ((n + 1) // 2)))
    for i, (traj, label, tagged, rel) in enumerate(results):
        # xy (comoving)
        ax = fig.add_subplot((n + 1) // 2, 4, 2 * i + 1)
        n_pts = min(len(rel), 4000)
        colors = plt.cm.viridis(np.linspace(0, 1, n_pts))
        for j in range(1, n_pts):
            ax.plot(rel[j-1:j+1, 0], rel[j-1:j+1, 1],
                    '-', color=colors[j], lw=0.3)
        ax.plot(0, 0, 'y*', ms=8)
        ax.plot(rel[0, 0], rel[0, 1], 'go', ms=4)
        ax.set_xlim(-1.5 * INITIAL_R, 1.5 * INITIAL_R)
        ax.set_ylim(-1.5 * INITIAL_R, 1.5 * INITIAL_R)
        ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
        ax.set_title(f'{label}\nxy comoving', fontsize=8)

        # xz (comoving)
        ax = fig.add_subplot((n + 1) // 2, 4, 2 * i + 2)
        for j in range(1, n_pts):
            ax.plot(rel[j-1:j+1, 0], rel[j-1:j+1, 2],
                    '-', color=colors[j], lw=0.3)
        ax.plot(0, 0, 'y*', ms=8)
        ax.plot(rel[0, 0], rel[0, 2], 'go', ms=4)
        ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
        ax.set_title(f'xz comoving', fontsize=8)
        ax.set_xlim(-1.5 * INITIAL_R, 1.5 * INITIAL_R)
        # z range symmetric around 0
        zmax = max(abs(rel[:, 2].max()), abs(rel[:, 2].min()), 0.3)
        ax.set_ylim(-zmax * 1.1, zmax * 1.1)

    plt.suptitle('Phase 7: moving star + retarded gravity',
                 fontsize=13)
    plt.tight_layout()
    out = os.path.join(OUT, 'phase7_moving_star.png')
    plt.savefig(out, dpi=130)
    plt.close()
    print(f"\n  saved: {out}")


if __name__ == '__main__':
    run()
