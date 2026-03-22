#!/usr/bin/env python3
"""
Experiment 118 v3: Planet Formation from Star Core

v3 changes from v2:
  1. Planet starts AT the star center (PLANET_DIST=0), not outside
  2. Zero initial velocity — velocity emerges from consumption asymmetry
  3. Lower INERTIA (500 vs 5000) — dense center field provides strong force
  4. Track angular displacement to verify spiral (not radial escape)

Theory: the planet FORMS inside the star cluster by accumulating Different
deposits, then spirals outward until it reaches equilibrium — the distance
where it can withstand the outward connector push from its own traversals.

Kept from v2: PlanetCluster with shared momentum, mean-subtracted density
force, speed-of-light cap, damping, Different-fraction extension with
DIFF_FRAC_MIN=0.15, compound extension, star pure density routing.
"""

import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict
import os, sys, time, csv

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Configuration ─────────────────────────────────────────────
SEED          = 42
N_NODES       = 5000
SPHERE_R      = 20.0
TARGET_K      = 24

STAR_COUNT    = 80
STAR_GROUPS   = 4
STAR_TAGS     = frozenset(f"s{i}" for i in range(STAR_GROUPS))

PLANET_COUNT  = 10
PLANET_GROUPS = 2       # inter-group consumption provides cohesion
PLANET_TAGS   = frozenset(f"p{i}" for i in range(2))
PLANET_DIST   = 0.0     # v3: planet starts AT the star center

DEPOSIT       = 1.0     # deposit per hop
CONSUME_FRAC  = 0.3     # fraction of foreign consumed per hop
EXTEND_RATE   = 0.003   # compound extension rate per hop
DIFF_FRAC_MIN = 0.15    # star-internal: extend at 15% rate (not zero)

# Momentum parameters (planet only)
FORCE_INTERVAL    = 10    # ticks between force updates
INERTIA           = 500.0 # v3: lower — dense center field is strong enough
MAX_HOPS_PER_TICK = 1     # consumption ∝ mass: 1 hop/node/tick
HOP_FLOOR_FACTOR  = 0.5   # hop_floor = initial_mean_edge * this
DAMPING           = 0.001 # velocity decay per tick (graph friction)

WARMUP        = 10000   # star deposits build up before planet is introduced
SIM           = 10000
LOG_EVERY     = 500
MEASURE_EVERY = 50

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# ── Connector ─────────────────────────────────────────────────
class Conn:
    __slots__ = ('length', 'dep')

    def __init__(self, length):
        self.length = length
        self.dep = {}

    def foreign(self, tag):
        return sum(v for k, v in self.dep.items() if k != tag)

    def density(self, tag):
        """Foreign deposit per unit length — the routing signal."""
        return self.foreign(tag) / self.length if self.length > 0 else 0.0


# ── Graph ─────────────────────────────────────────────────────
def build_graph(rng):
    pts = []
    while len(pts) < N_NODES:
        batch = rng.uniform(-SPHERE_R, SPHERE_R, (N_NODES * 2, 3))
        good = batch[np.linalg.norm(batch, axis=1) <= SPHERE_R]
        pts.extend(good.tolist())
    pos = np.array(pts[:N_NODES])

    rc = SPHERE_R * (TARGET_K / N_NODES) ** (1.0 / 3.0)
    pairs = cKDTree(pos).query_pairs(rc)

    adj = defaultdict(list)
    conn = {}
    for i, j in pairs:
        key = (i, j) if i < j else (j, i)
        conn[key] = Conn(np.linalg.norm(pos[i] - pos[j]))
        adj[i].append(j)
        adj[j].append(i)

    degs = [len(adj[n]) for n in range(N_NODES)]
    mean_edge = np.mean([c.length for c in conn.values()])
    print(f"Graph: {N_NODES} nodes, {len(conn)} edges, "
          f"avg_k={np.mean(degs):.1f}, rc={rc:.3f}, "
          f"mean_edge={mean_edge:.3f}")
    return pos, adj, conn, rc, mean_edge


def edge(conn, i, j):
    return conn[(i, j) if i < j else (j, i)]


def avg_edge_length_at(node, adj, conn):
    """Mean connector length at a node."""
    nbrs = adj[node]
    if not nbrs:
        return 1.0
    return np.mean([edge(conn, node, nb).length for nb in nbrs])


# ── HOP — the core operation ─────────────────────────────────
def do_hop(tag, src, dst, conn_map):
    """
    Entity with `tag` moves from node `src` to node `dst`.

    The connector src-dst is TRANSFORMED:
      1. CONSUME  — foreign deposits → own (Different -> Same)
      2. DEPOSIT  — own signature added
      3. EXTEND   — compound growth scaled by Different fraction
    """
    c = edge(conn_map, src, dst)

    # 1. CONSUME: transform foreign deposits into own
    for t in list(c.dep):
        if t != tag:
            amt = c.dep[t]
            eaten = amt * CONSUME_FRAC
            c.dep[t] = amt - eaten
            c.dep[tag] = c.dep.get(tag, 0.0) + eaten

    # 2. DEPOSIT: leave own signature
    c.dep[tag] = c.dep.get(tag, 0.0) + DEPOSIT

    # 3. EXTEND: compound growth × Different fraction
    total = sum(c.dep.values())
    if total > 0:
        if tag in STAR_TAGS:
            same = sum(v for k, v in c.dep.items() if k in STAR_TAGS)
        elif tag in PLANET_TAGS:
            same = sum(v for k, v in c.dep.items() if k in PLANET_TAGS)
        else:
            same = c.dep.get(tag, 0.0)
        diff_frac = max((total - same) / total, DIFF_FRAC_MIN)
    else:
        diff_frac = DIFF_FRAC_MIN

    c.length *= (1 + EXTEND_RATE * diff_frac)


# ── Star: pure density routing (v1 style) ────────────────────
def tick_star(tag, node, adj, conn_map, rng):
    """Star nodes use simple density routing. No momentum needed."""
    nbrs = adj[node]
    if not nbrs:
        return node

    best_nbr = None
    best_density = -1.0
    for nb in nbrs:
        d = edge(conn_map, node, nb).density(tag)
        if d > best_density:
            best_density = d
            best_nbr = nb

    if best_density <= 0:
        best_nbr = nbrs[rng.integers(len(nbrs))]

    do_hop(tag, node, best_nbr, conn_map)
    return best_nbr


# ── Planet Cluster: shared momentum, independent hops ─────────
class PlanetCluster:
    """
    Multi-node planet with shared velocity/displacement.
    Force is averaged across all nodes. When displacement exceeds
    threshold, each node independently hops along the shared direction.
    Each hop still does the full CONSUME-DEPOSIT-EXTEND cycle.
    """

    def __init__(self, tags, nodes):
        self.tags = tags          # list of per-node tags (p0, p1, ...)
        self.nodes = list(nodes)  # list of graph node IDs
        self.velocity = np.zeros(3)
        self.displacement = np.zeros(3)
        self.hops = 0

    def tick(self, tick, pos, adj, conn, hop_floor):
        n = len(self.nodes)

        # 1. FORCE: density gradient via mean-subtraction (like v22/v23)
        if tick % FORCE_INTERVAL == 0:
            total_force = np.zeros(3)
            for idx in range(n):
                node = self.nodes[idx]
                tag = self.tags[idx]
                nbrs = adj[node]
                if not nbrs:
                    continue

                # Gather densities and directions
                densities = []
                directions = []
                for nb in nbrs:
                    c = edge(conn, node, nb)
                    densities.append(c.density(tag))
                    d = pos[nb] - pos[node]
                    dist = np.linalg.norm(d)
                    directions.append(d / dist if dist > 1e-15 else d)

                mean_dens = sum(densities) / len(densities)
                for dens, dirn in zip(densities, directions):
                    total_force += dirn * (dens - mean_dens)

            self.velocity += (total_force / n) / INERTIA

            # Speed of light: v=1 hop per tick. Cap velocity.
            vmag = np.linalg.norm(self.velocity)
            if vmag > hop_floor:
                self.velocity *= hop_floor / vmag

        # 2. DAMPING: each hop costs energy (consumption + extension = work)
        self.velocity *= (1.0 - DAMPING)

        # 3. ACCUMULATE shared displacement
        self.displacement += self.velocity

        # 4. HOP: each node independently follows the shared direction
        disp_mag = np.linalg.norm(self.displacement)
        if disp_mag < hop_floor:
            return

        hops_this_tick = 0
        while hops_this_tick < MAX_HOPS_PER_TICK:
            disp_mag = np.linalg.norm(self.displacement)
            if disp_mag < hop_floor:
                break

            disp_dir = self.displacement / disp_mag

            # Each node hops toward the shared displacement direction
            hopped_any = False
            for idx in range(n):
                node = self.nodes[idx]
                tag = self.tags[idx]
                nbrs = adj[node]
                if not nbrs:
                    continue

                threshold = max(
                    avg_edge_length_at(node, adj, conn), hop_floor)
                if disp_mag < threshold:
                    continue

                # Best-aligned neighbor for this node
                best_nb = max(
                    nbrs,
                    key=lambda nb: np.dot(
                        disp_dir, _unit(pos[nb] - pos[node])))

                # HOP: full CONSUME-DEPOSIT-EXTEND
                do_hop(tag, node, best_nb, conn)
                self.nodes[idx] = best_nb
                self.hops += 1
                hopped_any = True

            if not hopped_any:
                break

            # Subtract one hop's worth of displacement
            self.displacement -= disp_dir * hop_floor
            hops_this_tick += 1

    def com(self, pos):
        return np.mean([pos[n] for n in self.nodes], axis=0)

    def radius(self, pos):
        c = self.com(pos)
        return np.mean([np.linalg.norm(pos[n] - c) for n in self.nodes])


def _unit(v):
    """Unit vector, safe for zero."""
    n = np.linalg.norm(v)
    return v / n if n > 1e-15 else v


# ── Angular tracking ─────────────────────────────────────────
def angular_displacement(p_prev, p_curr, center):
    """
    Compute angular displacement (radians) of planet COM around center.
    Uses atan2 in the XY plane.
    """
    dp = p_prev - center
    dc = p_curr - center
    angle_prev = np.arctan2(dp[1], dp[0])
    angle_curr = np.arctan2(dc[1], dc[0])
    delta = angle_curr - angle_prev
    # Wrap to [-pi, pi]
    if delta > np.pi:
        delta -= 2 * np.pi
    elif delta < -np.pi:
        delta += 2 * np.pi
    return delta


def radial_tangential_velocity(velocity, pos_vec):
    """
    Decompose velocity into radial and tangential components
    relative to a position vector from center.
    """
    r = np.linalg.norm(pos_vec)
    if r < 1e-15:
        return np.linalg.norm(velocity), 0.0
    r_hat = pos_vec / r
    v_radial = np.dot(velocity, r_hat)
    v_tangential = np.linalg.norm(velocity - v_radial * r_hat)
    return v_radial, v_tangential


# ── Deposit field profile ─────────────────────────────────────
def deposit_profile(pos, conn, star_com, planet_tag="p"):
    bins = np.arange(0, SPHERE_R * 2, 1.0)
    dep_sum = np.zeros(len(bins) - 1)
    len_sum = np.zeros(len(bins) - 1)
    cnt = np.zeros(len(bins) - 1)

    for (i, j), c in conn.items():
        mid = (pos[i] + pos[j]) / 2
        r = np.linalg.norm(mid - star_com)
        star_dep = sum(v for k, v in c.dep.items() if k != planet_tag)
        idx = int(r)
        if 0 <= idx < len(dep_sum):
            dep_sum[idx] += star_dep
            len_sum[idx] += c.length
            cnt[idx] += 1

    print("\n  Deposit field profile (density = avg_deposit / avg_length):")
    print(f"  {'r':>3s}  {'avg_dep':>8s}  {'avg_len':>8s}  {'density':>8s}  {'n':>5s}")
    field_edge = 0
    peak_r = 0
    peak_dens = 0
    for i in range(len(dep_sum)):
        if cnt[i] > 0:
            ad = dep_sum[i] / cnt[i]
            al = len_sum[i] / cnt[i]
            dens = ad / al if al > 0 else 0
            if ad > 0.5:
                print(f"  {i:3d}  {ad:8.1f}  {al:8.2f}  {dens:8.3f}  {cnt[i]:5.0f}")
                if dens > peak_dens:
                    peak_dens = dens
                    peak_r = i
                if dens > 0.01:
                    field_edge = i + 1

    print(f"\n  Density peak at r = {peak_r} (density = {peak_dens:.3f})")
    print(f"  Field edge (density > 0.01): r = {field_edge}")
    return field_edge, peak_r


# ── Simulation ────────────────────────────────────────────────
def run():
    rng = np.random.default_rng(SEED)

    print("Building graph...")
    t0 = time.time()
    pos, adj, conn, rc, mean_edge = build_graph(rng)
    hop_floor = mean_edge * HOP_FLOOR_FACTOR
    print(f"  hop_floor={hop_floor:.3f}  ({time.time() - t0:.1f}s)\n")

    # ── Place star near origin ──
    origin_d = np.linalg.norm(pos, axis=1)
    near = np.argsort(origin_d)

    star_tags = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_nodes = [int(near[i]) for i in range(STAR_COUNT)]
    print(f"Star: {STAR_COUNT} nodes, {STAR_GROUPS} groups, "
          f"max initial r={origin_d[near[STAR_COUNT - 1]]:.2f}")

    # ── Warmup: star only (builds deposit field before planet is born) ──
    print(f"\n{'=' * 60}")
    print(f"WARMUP  ({WARMUP} ticks, star only)")
    print(f"{'=' * 60}")
    t0 = time.time()
    for tick in range(WARMUP):
        for i in range(STAR_COUNT):
            star_nodes[i] = tick_star(
                star_tags[i], star_nodes[i], adj, conn, rng)

        if (tick + 1) % LOG_EVERY == 0:
            com = pos[star_nodes].mean(axis=0)
            dists = np.linalg.norm(pos[star_nodes] - com, axis=1)
            max_core = max(
                (edge(conn, star_nodes[i], nb).length
                 for i in range(min(10, STAR_COUNT))
                 for nb in adj[star_nodes[i]]),
                default=0)
            rate = (tick + 1) / (time.time() - t0)
            print(f"  t={tick+1:5d}  star_r={dists.mean():6.2f}  "
                  f"rmax={dists.max():6.2f}  "
                  f"core_len={max_core:8.1f}  ({rate:.0f} t/s)")

    warmup_s = time.time() - t0
    com = pos[star_nodes].mean(axis=0)
    star_r = np.linalg.norm(pos[star_nodes] - com, axis=1).mean()
    print(f"\nWarmup done ({warmup_s:.1f}s)")
    print(f"  Star COM = [{com[0]:.1f}, {com[1]:.1f}, {com[2]:.1f}]")
    print(f"  Star mean radius = {star_r:.2f}")

    field_edge, peak_r = deposit_profile(pos, conn, com)

    # ── v3: Place planet cluster AT the star center ──
    # Find nodes closest to star COM (i.e. inside the star cluster)
    d_from_com = np.linalg.norm(pos - com, axis=1)
    center_sorted = np.argsort(d_from_com)

    # Skip nodes already used by the star
    star_set = set(star_nodes)
    p_nodes = []
    for idx in center_sorted:
        if int(idx) not in star_set and len(p_nodes) < PLANET_COUNT:
            p_nodes.append(int(idx))
    if len(p_nodes) < PLANET_COUNT:
        print(f"WARNING: only found {len(p_nodes)} non-star nodes near center")

    p_tags = [f"p{k % PLANET_GROUPS}" for k in range(PLANET_COUNT)]
    planet = PlanetCluster(p_tags, p_nodes)

    p_com = planet.com(pos)
    p_dist0 = np.linalg.norm(p_com - com)
    print(f"\n  v3: Planet placed AT star center")
    print(f"  Planet: {PLANET_COUNT} nodes, "
          f"dist from star COM = {p_dist0:.2f}")
    print(f"  Planet node distances from COM: "
          f"min={d_from_com[p_nodes].min():.2f}, "
          f"max={d_from_com[p_nodes].max():.2f}")

    # ── Main simulation ──
    print(f"\n{'=' * 60}")
    print(f"SIMULATION  ({SIM} ticks)")
    print(f"{'=' * 60}")

    rec = {'t': [], 'd': [], 'vmag': [], 'sr': [],
           'tl': [], 'px': [], 'py': [], 'pz': [],
           'planet_r': [], 'max_core_len': [],
           'v_radial': [], 'v_tangential': [], 'angle_cumul': []}

    cumul_angle = 0.0
    prev_p_com = p_com.copy()

    t0 = time.time()
    for tick in range(SIM):
        # Tick all star nodes (v1 pure routing)
        for i in range(STAR_COUNT):
            star_nodes[i] = tick_star(
                star_tags[i], star_nodes[i], adj, conn, rng)

        # Tick planet cluster (shared momentum)
        planet.tick(tick, pos, adj, conn, hop_floor)

        # Record measurements
        if (tick + 1) % MEASURE_EVERY == 0:
            star_com = pos[star_nodes].mean(axis=0)
            sr = np.linalg.norm(pos[star_nodes] - star_com, axis=1).mean()

            p_com = planet.com(pos)
            p_dist = np.linalg.norm(p_com - star_com)
            p_vmag = np.linalg.norm(planet.velocity)
            p_r = planet.radius(pos)

            # Angular tracking
            delta_angle = angular_displacement(prev_p_com, p_com, star_com)
            cumul_angle += delta_angle

            # Radial/tangential velocity decomposition
            pos_from_star = p_com - star_com
            v_rad, v_tan = radial_tangential_velocity(
                planet.velocity, pos_from_star)

            prev_p_com = p_com.copy()

            max_core = max(
                (edge(conn, star_nodes[i], nb).length
                 for i in range(min(10, STAR_COUNT))
                 for nb in adj[star_nodes[i]]),
                default=0)

            rec['t'].append(tick + 1)
            rec['d'].append(p_dist)
            rec['vmag'].append(p_vmag)
            rec['sr'].append(sr)
            rec['tl'].append(sum(c.length for c in conn.values()))
            rec['px'].append(p_com[0])
            rec['py'].append(p_com[1])
            rec['pz'].append(p_com[2])
            rec['planet_r'].append(p_r)
            rec['max_core_len'].append(max_core)
            rec['v_radial'].append(v_rad)
            rec['v_tangential'].append(v_tan)
            rec['angle_cumul'].append(cumul_angle)

        if (tick + 1) % LOG_EVERY == 0:
            total_hops = planet.hops
            rate = (tick + 1) / (time.time() - t0)
            print(f"  t={tick+1:5d}  d={rec['d'][-1]:7.2f}  "
                  f"sr={rec['sr'][-1]:5.2f}  "
                  f"vel={rec['vmag'][-1]:.4f}  "
                  f"v_r={rec['v_radial'][-1]:.4f}  "
                  f"v_t={rec['v_tangential'][-1]:.4f}  "
                  f"ang={rec['angle_cumul'][-1]:.2f}rad  "
                  f"hops={total_hops}  ({rate:.0f} t/s)")

        if (tick + 1) % 2000 == 0:
            for c in conn.values():
                c.dep = {k: v for k, v in c.dep.items() if v > 1e-10}

    sim_s = time.time() - t0
    print(f"\nDone ({sim_s:.1f}s, {SIM / sim_s:.0f} t/s)")

    # ── Final deposit profile ──
    print("\nFinal deposit profile:")
    deposit_profile(pos, conn, pos[star_nodes].mean(axis=0), "p0")

    # ── Save CSV ──
    csv_path = os.path.join(OUT, "phase1_results.csv")
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['tick', 'planet_dist', 'velocity', 'star_radius',
                     'total_length', 'px', 'py', 'pz',
                     'planet_radius', 'max_core_length',
                     'v_radial', 'v_tangential', 'angle_cumul'])
        for i in range(len(rec['t'])):
            w.writerow([
                rec['t'][i],
                f"{rec['d'][i]:.4f}", f"{rec['vmag'][i]:.6f}",
                f"{rec['sr'][i]:.4f}", f"{rec['tl'][i]:.2f}",
                f"{rec['px'][i]:.4f}", f"{rec['py'][i]:.4f}",
                f"{rec['pz'][i]:.4f}",
                f"{rec['planet_r'][i]:.4f}",
                f"{rec['max_core_len'][i]:.4f}",
                f"{rec['v_radial'][i]:.6f}",
                f"{rec['v_tangential'][i]:.6f}",
                f"{rec['angle_cumul'][i]:.6f}",
            ])
    print(f"CSV: {csv_path}")

    # ── Plots ──
    fig, ax = plt.subplots(3, 3, figsize=(18, 15))
    fig.suptitle(
        "Experiment 118 v3: Planet Formation from Star Core\n"
        f"EXTEND={EXTEND_RATE}  CONSUME={CONSUME_FRAC}  INERTIA={INERTIA}  "
        f"star={STAR_COUNT}({STAR_GROUPS}grp)  planet={PLANET_COUNT}  H=0",
        fontsize=11)

    # Row 0: distance, velocity, star radius (same as v2)
    ax[0, 0].plot(rec['t'], rec['d'], 'b-', lw=0.8)
    ax[0, 0].axhline(p_dist0, color='r', ls='--', alpha=0.4, label='initial')
    ax[0, 0].set(xlabel='tick', ylabel='distance',
                 title='Planet COM dist from star COM')
    ax[0, 0].legend()

    ax[0, 1].plot(rec['t'], rec['vmag'], 'g-', lw=0.8)
    ax[0, 1].set(xlabel='tick', ylabel='|velocity|',
                 title='Planet velocity magnitude')

    ax[0, 2].plot(rec['t'], rec['sr'], 'r-', lw=0.8)
    ax[0, 2].set(xlabel='tick', ylabel='mean radius',
                 title='Star cluster radius')

    # Row 1: radial velocity, tangential velocity, cumulative angle
    ax[1, 0].plot(rec['t'], rec['v_radial'], 'b-', lw=0.8)
    ax[1, 0].axhline(0, color='k', ls=':', alpha=0.3)
    ax[1, 0].set(xlabel='tick', ylabel='v_radial',
                 title='Radial velocity (+ = outward)')

    ax[1, 1].plot(rec['t'], rec['v_tangential'], 'orange', lw=0.8)
    ax[1, 1].set(xlabel='tick', ylabel='v_tangential',
                 title='Tangential velocity (spiral signal)')

    ax[1, 2].plot(rec['t'], rec['angle_cumul'], 'm-', lw=0.8)
    ax[1, 2].set(xlabel='tick', ylabel='cumulative angle (rad)',
                 title='Angular displacement')

    # Row 2: core connector length, planet cohesion, XY trajectory
    ax[2, 0].plot(rec['t'], rec['max_core_len'], 'purple', lw=0.8)
    ax[2, 0].set(xlabel='tick', ylabel='max length',
                 title='Max core connector length')

    ax[2, 1].plot(rec['t'], rec['planet_r'], 'orange', lw=0.8)
    ax[2, 1].set(xlabel='tick', ylabel='mean radius',
                 title='Planet cluster radius (cohesion)')

    pp_x = np.array(rec['px'])
    pp_y = np.array(rec['py'])
    ax[2, 2].plot(pp_x, pp_y, 'b-', lw=0.5, alpha=0.7)
    ax[2, 2].plot(pp_x[0], pp_y[0], 'go', ms=8, label='start')
    ax[2, 2].plot(pp_x[-1], pp_y[-1], 'ro', ms=8, label='end')
    star_com_final = pos[star_nodes].mean(axis=0)
    ax[2, 2].plot(star_com_final[0], star_com_final[1],
                  'y*', ms=15, label='star COM')
    ax[2, 2].set(xlabel='x', ylabel='y',
                 title='Planet COM trajectory (XY)')
    ax[2, 2].legend()
    ax[2, 2].set_aspect('equal')

    plt.tight_layout()
    fig_path = os.path.join(OUT, "phase1_results.png")
    plt.savefig(fig_path, dpi=150)
    print(f"Plot: {fig_path}")

    # ── Summary ──
    d = rec['d']
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Initial planet distance:  {p_dist0:.2f}")
    print(f"  Final planet distance:    {d[-1]:.2f}")
    print(f"  Min planet distance:      {min(d):.2f}")
    print(f"  Max planet distance:      {max(d):.2f}")
    print(f"  Final star radius:        {rec['sr'][-1]:.2f}")
    print(f"  Final planet radius:      {rec['planet_r'][-1]:.2f}")
    print(f"  Max core connector len:   {max(rec['max_core_len']):.1f}")
    print(f"  Total planet hops:        {planet.hops}")
    print(f"  --- Spiral diagnostics ---")
    print(f"  Final radial velocity:    {rec['v_radial'][-1]:.6f}")
    print(f"  Final tangential velocity:{rec['v_tangential'][-1]:.6f}")
    print(f"  Cumulative angle:         {rec['angle_cumul'][-1]:.2f} rad "
          f"({rec['angle_cumul'][-1] / (2 * np.pi):.2f} revolutions)")
    # Check verification criteria
    print(f"\n  --- Verification ---")
    print(f"  1. Started near r=0:      {p_dist0 < 1.0} (d0={p_dist0:.2f})")
    print(f"  2. Moved outward:         {d[-1] > p_dist0}")
    print(f"  3. Distance increased:    {d[-1] > d[0]}")
    v_smooth = all(
        abs(rec['vmag'][i+1] - rec['vmag'][i]) < 0.1
        for i in range(min(20, len(rec['vmag']) - 1)))
    print(f"  4. Velocity smooth start: {v_smooth}")
    print(f"  5. Tangential nonzero:    "
          f"{abs(rec['v_tangential'][-1]) > 1e-6} "
          f"(v_t={rec['v_tangential'][-1]:.6f})")


if __name__ == '__main__':
    run()
