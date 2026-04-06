#!/usr/bin/env python3
"""
Experiment 128 v10 — Consumption IS Movement

The entity doesn't hop, then consume as a side effect.
The entity CONSUMES, and that IS its movement.

Each tick:
  1. Entity reads deposit density from nearby graph connectors
  2. The deposit field determines the consumption direction
     (toward the densest matching deposits = toward the star)
  3. The entity consumes one deposit from that direction
  4. The consumed deposit shifts the entity's pattern center
     by the deposit's direction, weighted by the local density

The entity's position is CONTINUOUS (x,y,z) — not a graph node index.
The graph provides the deposit field. The consumption provides the movement.
They are the same operation.

The 1/r^2 isn't assumed — it EMERGES from geometric dilution of deposits
on the graph. The movement IS the consumption. Nothing else moves.
"""

import os
import sys
import time
import csv
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from substrate import Substrate

SEED = 42
N_NODES = 500000
SPHERE_R = 80.0
TARGET_K = 24
STAR_COUNT = 10000
STAR_GROUPS = 4

TICKS = 200000
MEASURE_EVERY = 1000
LOG_EVERY = 10000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


# Copy substrate from v5
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v5'))


class ConsumptionEntity:
    """An entity whose position IS the center of its deposit pattern.

    The entity has continuous position (x, y, z).
    Each tick it reads deposits from nearby graph nodes and consumes.
    The consumption shifts its position — that IS the movement.
    """

    def __init__(self, pos, velocity, capacity, is_star, substrate):
        self.pos = np.array(pos, dtype=np.float64)  # continuous position
        self.vel = np.array(velocity, dtype=np.float64)  # velocity (from formation)
        self.capacity = capacity  # max deposits consumed per tick
        self.is_star = is_star
        self.sub = substrate
        self.total_consumed = 0

    def nearest_node(self):
        """Find the graph node closest to our continuous position."""
        dists = np.linalg.norm(self.sub.pos - self.pos.astype(np.float32), axis=1)
        return int(np.argmin(dists))

    def tick(self, dt=1.0):
        """One tick: read field, consume, shift position.

        The consumption IS the movement. The consumed deposit's direction
        shifts the entity's position. The deposit field from the graph
        determines how much force (consumption) acts from each direction.
        """
        node = self.nearest_node()
        sub = self.sub

        # Read deposit field from all neighbors of nearest node
        consumption_force = np.zeros(3, dtype=np.float64)
        total_flux = 0.0

        for k in range(sub.degree[node]):
            nb = sub.nbr_node[node, k]
            if nb < 0:
                continue
            eid = sub.nbr_edge[node, k]

            # Deposit density on this connector
            if self.is_star:
                matching = float(sub.conn_star[eid])
            else:
                # Planet consumes star deposits (Different → Same)
                matching = float(sub.conn_star[eid])  # consumes STAR deposits

            length = float(sub.conn_length(np.array([eid]))[0])
            density = matching / max(length, 0.01)

            # Direction toward this neighbor
            direction = sub.pos[nb].astype(np.float64) - self.pos
            dist = np.linalg.norm(direction)
            if dist > 1e-10:
                direction /= dist

            # This neighbor's contribution to the consumption force
            # The entity consumes from this direction proportional to density
            consumption_force += density * direction
            total_flux += density

        # The consumption is limited by capacity
        force_mag = np.linalg.norm(consumption_force)
        if force_mag > 0 and total_flux > 0:
            consumed = min(total_flux, self.capacity)
            # Scale the force by consumed/total_flux (capacity limiting)
            consumption_force *= consumed / total_flux
            self.total_consumed += consumed

        # The consumption force IS the acceleration
        # F = consumed_momentum / mass, with mass = 1 for simplicity
        # The force naturally points toward the star (densest deposits)
        self.vel += consumption_force * dt
        self.pos += self.vel * dt

        # Deposit on the nearest connector (the entity refreshes its pattern)
        if sub.degree[node] > 0:
            # Deposit on the connector most aligned with velocity
            best_k = 0
            best_dot = -2.0
            vel_norm = np.linalg.norm(self.vel)
            if vel_norm > 1e-10:
                vel_dir = self.vel / vel_norm
                for k in range(sub.degree[node]):
                    nb = sub.nbr_node[node, k]
                    if nb < 0:
                        continue
                    d = sub.pos[nb].astype(np.float64) - self.pos
                    dn = np.linalg.norm(d)
                    if dn > 1e-10:
                        dot = np.dot(vel_dir, d / dn)
                        if dot > best_dot:
                            best_dot = dot
                            best_k = k
            eid = sub.nbr_edge[node, best_k]
            is_star_arr = np.array([self.is_star])
            sub.deposit(np.array([eid]), is_star_arr)


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print(f"Building substrate: N={N_NODES}, R={SPHERE_R}...")
    sys.stdout.flush()
    sub = Substrate(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)")

    # Star: deposit field from 10k source nodes (static, just deposits)
    print("Seeding star deposit field...")
    star_ids = sub.nearest_to_origin(STAR_COUNT)
    star_com = sub.pos[star_ids].mean(axis=0)

    # Seed star deposits: each star node deposits on all its connectors
    for sid in star_ids:
        for k in range(sub.degree[sid]):
            eid = sub.nbr_edge[sid, k]
            if eid >= 0:
                sub.conn_star[eid] += 10  # strong initial field

    total_star_deps = int(sub.conn_star.sum())
    print(f"  Star: {STAR_COUNT} nodes, {total_star_deps} initial deposits")

    # Planet: single consumption entity at r=40 with tangential velocity
    planet_pos = star_com + np.array([40.0, 0.0, 0.0])

    # Estimate circular velocity from the deposit field
    # At r=40, the flux determines the consumption force
    # v_circ = sqrt(consumed * r) approximately
    test_node = int(np.argmin(np.linalg.norm(sub.pos - planet_pos.astype(np.float32), axis=1)))
    test_flux = 0.0
    for k in range(sub.degree[test_node]):
        eid = sub.nbr_edge[test_node, k]
        if eid >= 0:
            test_flux += float(sub.conn_star[eid]) / max(float(sub.conn_length(np.array([eid]))[0]), 0.01)
    print(f"  Flux at planet position: {test_flux:.2f}")

    # Try various tangential velocities
    v_estimates = [0.5, 1.0, 2.0, 5.0, 10.0]

    results = []
    for vt in v_estimates:
        # Reset star deposits for each run
        sub.conn_star[:] = 0
        sub.conn_planet[:] = 0
        sub.conn_different[:] = 0
        sub.conn_consumed[:] = 0
        for sid in star_ids:
            for k in range(sub.degree[sid]):
                eid = sub.nbr_edge[sid, k]
                if eid >= 0:
                    sub.conn_star[eid] += 10

        planet = ConsumptionEntity(
            pos=planet_pos.copy(),
            velocity=np.array([0.0, vt, 0.0]),  # tangential kick
            capacity=100.0,  # processing capacity
            is_star=False,
            substrate=sub
        )

        rows = []
        print(f"\n  Running vt={vt:.1f}...")
        sys.stdout.flush()

        t0 = time.time()
        for tick in range(1, TICKS + 1):
            planet.tick()

            if tick % MEASURE_EVERY == 0:
                dist = float(np.linalg.norm(planet.pos - star_com))
                speed = float(np.linalg.norm(planet.vel))
                rows.append({
                    'tick': tick,
                    'x': planet.pos[0], 'y': planet.pos[1], 'z': planet.pos[2],
                    'dist': dist,
                    'speed': speed,
                    'consumed': planet.total_consumed,
                })

            if tick % LOG_EVERY == 0:
                r = rows[-1]
                elapsed = time.time() - t0
                tps = tick / max(elapsed, 0.001)
                print(f"    t={tick:7d}  dist={r['dist']:.2f}  speed={r['speed']:.4f}  "
                      f"consumed={r['consumed']:.0f}  ({tps:.0f} t/s)")
                sys.stdout.flush()

        # Compute revolutions
        angles = []
        for i in range(1, len(rows)):
            p0 = np.array([rows[i-1]['x'], rows[i-1]['y']])
            p1 = np.array([rows[i]['x'], rows[i]['y']])
            s = star_com[:2].astype(np.float64)
            v0, v1 = p0 - s, p1 - s
            cross = v0[0]*v1[1] - v0[1]*v1[0]
            dot = v0[0]*v1[0] + v0[1]*v1[1]
            angles.append(np.degrees(np.arctan2(cross, dot)))

        net_angle = sum(angles)
        rev = net_angle / 360
        print(f"    Result: {net_angle:.1f} deg ({rev:.2f} rev), "
              f"r: {min(r['dist'] for r in rows):.2f}-{max(r['dist'] for r in rows):.2f}")

        results.append((rows, vt, net_angle))

    plot(results, star_com)


def plot(results, star_com):
    fig, axes = plt.subplots(2, len(results), figsize=(5*len(results), 10))
    fig.suptitle('v10: Consumption IS Movement (graph-derived force)', fontsize=14)

    for col, (rows, vt, net_angle) in enumerate(results):
        rev = net_angle / 360
        ticks = [r['tick'] for r in rows]
        n = len(rows)

        # Top: XY trajectory
        ax = axes[0, col]
        px = [r['x'] for r in rows]; py = [r['y'] for r in rows]
        colors = plt.cm.viridis(np.linspace(0, 1, n))
        for i in range(1, n):
            ax.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], lw=0.5)
        ax.plot(px[0], py[0], 'go', ms=6)
        ax.plot(px[-1], py[-1], 'ro', ms=6)
        ax.plot(star_com[0], star_com[1], 'y*', ms=10)
        ax.set_aspect('equal')
        ax.set_title(f'vt={vt}, {rev:.1f} rev', fontsize=10)
        ax.grid(True, alpha=0.3)

        # Bottom: distance
        ax = axes[1, col]
        ax.plot(ticks, [r['dist'] for r in rows], 'b-', lw=0.5)
        ax.set_ylabel('Distance')
        ax.set_xlabel('Tick')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "results.png"), dpi=150)
    plt.close()
    print(f"\nSaved: results.png")


if __name__ == '__main__':
    run()
