#!/usr/bin/env python3
"""
Experiment 128 v1 — Phase 2G: Elliptical Orbit Attempt

Gravity from ACTUAL deposit density gradient at the planet's position.
No gravity_strength parameter — gravity IS the deposit field.
Longer run (50k ticks) for multiple orbits.
"""

import os
import numpy as np
from collections import deque

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from graph import Graph

SEED = 42
N_NODES = 5000
SPHERE_R = 20.0
TARGET_K = 24
TICKS = 50000
MEASURE_EVERY = 50

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


class FwdTable:
    def __init__(self, graph):
        self._t = {}
        pos = graph.pos
        for node in range(graph.n_nodes):
            for nb in graph.neighbors(node):
                d = pos[node] - pos[nb]
                dl = np.linalg.norm(d)
                if dl < 1e-15:
                    others = [n2 for n2 in graph.neighbors(node) if n2 != nb]
                    self._t[(nb, node)] = others[0] if others else nb
                    continue
                d /= dl
                best, bd = nb, -2.0
                for n2 in graph.neighbors(node):
                    if n2 == nb: continue
                    od = pos[n2] - pos[node]
                    ol = np.linalg.norm(od)
                    if ol < 1e-15: continue
                    dot = np.dot(d, od / ol)
                    if dot > bd: bd, best = dot, n2
                self._t[(nb, node)] = best
    def next(self, f, a):
        return self._t.get((f, a), a)


class Q:
    __slots__ = ('fam', 'node', 'frm', 'age')
    def __init__(self, f, n, fr):
        self.fam = f; self.node = n; self.frm = fr; self.age = 0


def find_planet_com(g, center_pos):
    total_w = 0; wpos = np.zeros(3)
    seen = set()
    for (i, j), c in g.connectors.items():
        if (i, j) in seen: continue
        seen.add((i, j))
        if c.planet_deposits > c.star_deposits:
            net = c.planet_deposits - c.star_deposits
            wpos += net * (g.pos[i] + g.pos[j]) / 2
            total_w += net
    return wpos / total_w if total_w > 0 else center_pos


def gravity_at(g, pos, center_pos):
    """Compute gravity vector from the deposit field at a position.

    For each nearby node, read star deposit density on its connectors.
    The gravity direction = toward regions with higher star density.
    The gravity strength = the density gradient magnitude.
    No parameters — gravity IS the deposit field.
    """
    # Find the nearest graph node to the position
    dists = np.linalg.norm(g.pos - pos, axis=1)
    nearest = np.argmin(dists)

    gravity = np.zeros(3)
    for nb in g.neighbors(nearest):
        c = g.connectors[g.edge_key(nearest, nb)]
        # Star deposit density on this connector
        star_density = c.star_deposits / c.length if c.length > 0 else 0
        direction = g.pos[nb] - g.pos[nearest]
        dn = np.linalg.norm(direction)
        if dn > 1e-15:
            gravity += star_density * (direction / dn)

    return gravity


def run():
    print("Building graph...")
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print("Building forward table...")
    fwd = FwdTable(g)
    center = g.nearest_to_origin(1)[0]
    center_pos = g.pos[center]
    rng = np.random.default_rng(SEED)

    star_sources = g.nearest_to_origin(80)
    dists = np.linalg.norm(g.pos - center_pos, axis=1)

    # Planet at r~10 with tangential initial momentum
    p_seed = np.argsort(np.abs(dists - 10.0))[0]
    nb_d = np.linalg.norm(g.pos - g.pos[p_seed], axis=1)
    nb_d[p_seed] = np.inf
    planet_init = [p_seed] + np.argsort(nb_d)[:2].tolist()

    radial = g.pos[p_seed] - center_pos
    radial /= np.linalg.norm(radial)
    tangential = np.array([-radial[1], radial[0], 0.0])
    tangential /= np.linalg.norm(tangential)

    print(f"Star: 80 sources. Planet at r={dists[p_seed]:.2f}")
    print(f"Initial tangential direction: {tangential[:2]}")
    print(f"Running {TICKS} ticks...")

    # Reset
    for c in g.connectors.values():
        c.star_deposits = 0; c.planet_deposits = 0
        c.different_count = 0; c.consumed_count = 0

    quanta = []
    current_planet = list(planet_init)
    rows = []
    prev_com = g.pos[planet_init].mean(axis=0)
    momentum = tangential * 1.0  # initial tangential kick

    MOMENTUM_DECAY = 0.9      # momentum persists strongly
    MOMENTUM_UPDATE = 0.1     # small update from actual motion
    STEP_SIZE = 2.0           # how far ahead to place new source
    UPDATE_INTERVAL = 100     # ticks between source relocation

    for tick in range(1, TICKS + 1):
        # Star emits
        for sn in star_sources:
            nbrs = g.neighbors(sn)
            if nbrs:
                nb = nbrs[rng.integers(len(nbrs))]
                quanta.append(Q('star', nb, sn))
                g.connectors[g.edge_key(sn, nb)].deposit_star()

        # Planet emits
        for pn in current_planet:
            nbrs = g.neighbors(pn)
            if nbrs:
                nb = nbrs[rng.integers(len(nbrs))]
                quanta.append(Q('planet', nb, pn))
                g.connectors[g.edge_key(pn, nb)].deposit_planet()

        # Propagate
        surviving = []
        for q in quanta:
            q.age += 1
            if q.age > 50: continue
            nn = fwd.next(q.frm, q.node)
            ek = g.edge_key(q.node, nn)
            if ek not in g.connectors: continue
            if q.fam == 'star': g.connectors[ek].deposit_star()
            else: g.connectors[ek].deposit_planet()
            q.frm = q.node; q.node = nn
            surviving.append(q)
        quanta = surviving

        if tick % MEASURE_EVERY == 0:
            p_com = find_planet_com(g, center_pos)
            p_dist = np.linalg.norm(p_com - center_pos)
            rows.append({
                'tick': tick, 'px': p_com[0], 'py': p_com[1],
                'pz': p_com[2], 'dist': p_dist,
            })

        # Update planet source: momentum + deposit-field gravity
        if tick % UPDATE_INTERVAL == 0:
            new_com = find_planet_com(g, center_pos)

            # Gravity from actual deposit field (no parameter!)
            grav = gravity_at(g, new_com, center_pos)
            grav_mag = np.linalg.norm(grav)

            # Momentum update from actual motion
            delta = new_com - prev_com
            dn = np.linalg.norm(delta)
            if dn > 1e-10:
                motion_dir = delta / dn
                momentum = MOMENTUM_DECAY * momentum + MOMENTUM_UPDATE * motion_dir
            mn = np.linalg.norm(momentum)
            if mn > 1e-10:
                momentum /= mn

            # Combine: momentum + gravity (gravity is from deposit field)
            combined = momentum * 1.0 + grav * 0.01  # scale gravity to be comparable
            cn = np.linalg.norm(combined)
            if cn > 1e-10:
                combined /= cn

            target = new_com + combined * STEP_SIZE
            target_dists = np.linalg.norm(g.pos - target, axis=1)
            current_planet = np.argsort(target_dists)[:3].tolist()
            prev_com = new_com.copy()

        if tick % 5000 == 0:
            r = rows[-1]
            print(f"  t={tick:6d}  dist={r['dist']:.2f}")

    print(f"Done: {TICKS} ticks")

    # Analysis
    angles = []
    for i in range(1, len(rows)):
        p0 = np.array([rows[i-1]['px'], rows[i-1]['py']])
        p1 = np.array([rows[i]['px'], rows[i]['py']])
        s = center_pos[:2]
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        angles.append(np.degrees(np.arctan2(cross, dot)))

    total_net = sum(angles)
    total_abs = sum(abs(a) for a in angles)
    revolutions = total_net / 360

    # Coherence
    cs = len(angles) // 10
    coh = [abs(np.mean(np.sign(angles[c*cs:(c+1)*cs]))) for c in range(10)] if cs > 0 else [0]
    mean_coh = np.mean(coh)

    print(f"\nNet: {total_net:.1f} deg ({revolutions:.2f} revolutions)")
    print(f"Total: {total_abs:.1f} deg")
    print(f"Coherence: {mean_coh:.3f}")
    print(f"Final dist: {rows[-1]['dist']:.2f}")

    # Distance stats
    all_dists = [r['dist'] for r in rows]
    print(f"Distance: min={min(all_dists):.2f}  max={max(all_dists):.2f}  "
          f"mean={np.mean(all_dists):.2f}")

    # Plot
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f'Experiment 128: Elliptical Orbit Attempt '
                 f'({revolutions:.1f} rev, coherence={mean_coh:.3f})', fontsize=14)

    ticks_p = [r['tick'] for r in rows]
    px = [r['px'] for r in rows]
    py = [r['py'] for r in rows]
    n = len(px)
    colors = plt.cm.viridis(np.linspace(0, 1, n))

    # 1. XY trajectory
    ax = axes[0, 0]
    for i in range(1, n):
        ax.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], linewidth=0.8)
    ax.plot(px[0], py[0], 'go', markersize=10, label='start')
    ax.plot(px[-1], py[-1], 'ro', markersize=10, label='end')
    ax.plot(center_pos[0], center_pos[1], 'y*', markersize=15, label='star')
    ax.set_aspect('equal'); ax.set_title('Trajectory (XY)')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 2. Distance
    ax = axes[0, 1]
    ax.plot(ticks_p, all_dists, 'b-', linewidth=0.8)
    ax.set_ylabel('Distance'); ax.set_title('Planet-Star Distance')
    ax.grid(True, alpha=0.3)

    # 3. Angular position
    ax = axes[0, 2]
    ax.plot(ticks_p[1:], np.cumsum(angles), 'g-', linewidth=0.8)
    ax.set_ylabel('Degrees'); ax.set_title(f'Angular Position ({revolutions:.1f} rev)')
    ax.grid(True, alpha=0.3)

    # 4. Polar plot
    ax = axes[1, 0]
    theta = np.cumsum([0] + list(np.radians(angles)))
    ax_polar = fig.add_subplot(2, 3, 4, projection='polar')
    axes[1, 0].set_visible(False)
    c = ax_polar.scatter(theta[::5], [r['dist'] for r in rows[::5]],
                         c=range(0, len(rows), 5), cmap='viridis', s=3, alpha=0.7)
    ax_polar.set_title('Polar (r vs angle)')

    # 5. Angular velocity vs distance
    ax = axes[1, 1]
    mid_dist = [(all_dists[i] + all_dists[i+1])/2 for i in range(len(angles))]
    ax.scatter(mid_dist, [abs(a) for a in angles], s=2, alpha=0.3, c='purple')
    ax.set_xlabel('Distance'); ax.set_ylabel('|Angular velocity| (deg/step)')
    ax.set_title('Angular Speed vs Distance (Kepler II)')
    ax.grid(True, alpha=0.3)

    # 6. r * v_angular (angular momentum proxy)
    ax = axes[1, 2]
    L = [mid_dist[i] * abs(angles[i]) for i in range(len(angles))]
    ax.plot(ticks_p[1:], L, 'purple', linewidth=0.3, alpha=0.7)
    ax.set_ylabel('r * |omega|'); ax.set_xlabel('Tick')
    ax.set_title('Angular Momentum Proxy')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "phase2g_ellipse.png"), dpi=150)
    plt.close()
    print(f"Saved: phase2g_ellipse.png")


if __name__ == '__main__':
    run()
