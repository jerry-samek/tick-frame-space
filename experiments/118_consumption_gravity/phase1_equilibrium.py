#!/usr/bin/env python3
"""
Experiment 118 Phase 1: Equilibrium Distance Test

Core invariant: EVERY HOP TRANSFORMS THE CONNECTOR.
After entity hops from A to B, connector A-B is different:
  - Less foreign deposit (consumed, Different -> Same)
  - More own deposit (added)
  - Longer (extended via compound growth)

Outward pressure mechanism: COMPOUND EXTENSION.
Each hop multiplies connector length by (1 + EXTEND_RATE).
Heavily-traversed center connectors grow exponentially long.
Routing uses deposit DENSITY (foreign / length), so extended
connectors become exponentially less attractive. The density
peak shifts to an intermediate radius — the equilibrium distance.

Star = 80 entity nodes in 4 groups. Planet = 1 node.
H = 0. No global expansion. All extension from traversal.
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
PLANET_DIST   = None    # auto: placed at deposit field edge

DEPOSIT       = 1.0     # deposit per hop
CONSUME_FRAC  = 0.3     # fraction of foreign consumed per hop
EXTEND_RATE   = 0.003   # compound extension: length *= (1 + rate) per hop

WARMUP        = 5000
SIM           = 10000
LOG_EVERY     = 500
MEASURE_EVERY = 50

OUT = os.path.dirname(os.path.abspath(__file__))


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
    print(f"Graph: {N_NODES} nodes, {len(conn)} edges, "
          f"avg_k={np.mean(degs):.1f}, rc={rc:.3f}")
    return pos, adj, conn, rc


def edge(conn, i, j):
    return conn[(i, j) if i < j else (j, i)]


# ── HOP — the core operation ─────────────────────────────────
def do_hop(tag, src, dst, conn_map):
    """
    Entity with `tag` moves from node `src` to node `dst`.

    The connector src-dst is TRANSFORMED:
      1. CONSUME  — foreign deposits → own (Different -> Same)
      2. DEPOSIT  — own signature added
      3. EXTEND   — compound growth: length *= (1 + EXTEND_RATE)

    Compound growth means heavily-traversed connectors grow
    exponentially. Their deposit DENSITY drops, making them
    less attractive to future routing. This is the mechanism
    that prevents collapse.
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

    # 3. EXTEND: compound growth — the more you traverse, the faster it grows
    c.length *= (1 + EXTEND_RATE)


# ── One tick for one entity node ──────────────────────────────
def tick_one(tag, node, adj, conn_map, rng):
    """
    READ  — scan local connectors for foreign deposit DENSITY
    CHOOSE — highest density (foreign/length)
    HOP   — move there, transforming the connector
    """
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
    pos, adj, conn, rc = build_graph(rng)
    print(f"  ({time.time() - t0:.1f}s)\n")

    # ── Place star near origin ──
    origin_d = np.linalg.norm(pos, axis=1)
    near = np.argsort(origin_d)

    star_tags = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_nodes = [int(near[i]) for i in range(STAR_COUNT)]
    print(f"Star: {STAR_COUNT} nodes, {STAR_GROUPS} groups, "
          f"max initial r={origin_d[near[STAR_COUNT - 1]]:.2f}")

    # ── Warmup ──
    print(f"\n{'=' * 60}")
    print(f"WARMUP  ({WARMUP} ticks, star only)")
    print(f"{'=' * 60}")
    t0 = time.time()
    for tick in range(WARMUP):
        for i in range(STAR_COUNT):
            star_nodes[i] = tick_one(
                star_tags[i], star_nodes[i], adj, conn, rng)

        if (tick + 1) % LOG_EVERY == 0:
            com = pos[star_nodes].mean(axis=0)
            dists = np.linalg.norm(pos[star_nodes] - com, axis=1)
            rate = (tick + 1) / (time.time() - t0)
            print(f"  t={tick+1:5d}  star_r={dists.mean():6.2f}  "
                  f"star_rmax={dists.max():6.2f}  ({rate:.0f} t/s)")

    warmup_s = time.time() - t0
    com = pos[star_nodes].mean(axis=0)
    star_r = np.linalg.norm(pos[star_nodes] - com, axis=1).mean()
    print(f"\nWarmup done ({warmup_s:.1f}s)")
    print(f"  Star COM = [{com[0]:.1f}, {com[1]:.1f}, {com[2]:.1f}]")
    print(f"  Star mean radius = {star_r:.2f}")

    field_edge, peak_r = deposit_profile(pos, conn, com)

    # ── Place planet ──
    if PLANET_DIST is not None:
        target_r = PLANET_DIST
    else:
        # Place outside the density peak so the planet approaches
        target_r = max(peak_r + 3, field_edge - 1, star_r + rc)
    print(f"\n  Target planet distance: {target_r:.1f}")

    d_from_com = np.linalg.norm(pos - com, axis=1)
    band = np.where(
        (d_from_com > target_r - 2) & (d_from_com < target_r + 2)
    )[0]
    if len(band) == 0:
        band = np.argsort(np.abs(d_from_com - target_r))[:20]

    p_node = int(band[rng.integers(len(band))])
    p_tag = "p"
    p_dist0 = np.linalg.norm(pos[p_node] - com)
    print(f"  Planet at node {p_node}, dist from COM = {p_dist0:.2f}")

    max_d_start = max(
        (edge(conn, p_node, nb).density(p_tag) for nb in adj[p_node]),
        default=0.0)
    print(f"  Max density at start: {max_d_start:.4f}")

    # ── Main simulation ──
    print(f"\n{'=' * 60}")
    print(f"SIMULATION  ({SIM} ticks)")
    print(f"{'=' * 60}")

    rec = {'t': [], 'd': [], 'v': [], 'sr': [],
           'tl': [], 'px': [], 'py': [], 'pz': [],
           'p_dens': []}
    prev_pos = pos[p_node].copy()

    t0 = time.time()
    for tick in range(SIM):
        for i in range(STAR_COUNT):
            star_nodes[i] = tick_one(
                star_tags[i], star_nodes[i], adj, conn, rng)

        p_node = tick_one(p_tag, p_node, adj, conn, rng)

        if (tick + 1) % MEASURE_EVERY == 0:
            com = pos[star_nodes].mean(axis=0)
            pp = pos[p_node]
            dist = np.linalg.norm(pp - com)
            vel = np.linalg.norm(pp - prev_pos) / MEASURE_EVERY
            sr = np.linalg.norm(pos[star_nodes] - com, axis=1).mean()

            max_d = max(
                (edge(conn, p_node, nb).density(p_tag) for nb in adj[p_node]),
                default=0.0)

            rec['t'].append(tick + 1)
            rec['d'].append(dist)
            rec['v'].append(vel)
            rec['sr'].append(sr)
            rec['tl'].append(sum(c.length for c in conn.values()))
            rec['px'].append(pp[0])
            rec['py'].append(pp[1])
            rec['pz'].append(pp[2])
            rec['p_dens'].append(max_d)
            prev_pos = pp.copy()

        if (tick + 1) % LOG_EVERY == 0:
            rate = (tick + 1) / (time.time() - t0)
            print(f"  t={tick+1:5d}  d={rec['d'][-1]:7.2f}  "
                  f"sr={rec['sr'][-1]:6.2f}  "
                  f"vel={rec['v'][-1]:.4f}  "
                  f"dens={rec['p_dens'][-1]:.2f}  "
                  f"({rate:.0f} t/s)")

        if (tick + 1) % 2000 == 0:
            for c in conn.values():
                c.dep = {k: v for k, v in c.dep.items() if v > 1e-10}

    sim_s = time.time() - t0
    print(f"\nDone ({sim_s:.1f}s, {SIM / sim_s:.0f} t/s)")

    # ── Final deposit profile ──
    print("\nFinal deposit profile:")
    deposit_profile(pos, conn, com, p_tag)

    # ── Save CSV ──
    csv_path = os.path.join(OUT, "phase1_results.csv")
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['tick', 'planet_dist', 'velocity', 'star_radius',
                     'total_length', 'px', 'py', 'pz', 'planet_density'])
        for i in range(len(rec['t'])):
            w.writerow([
                rec['t'][i],
                f"{rec['d'][i]:.4f}", f"{rec['v'][i]:.6f}",
                f"{rec['sr'][i]:.4f}", f"{rec['tl'][i]:.2f}",
                f"{rec['px'][i]:.4f}", f"{rec['py'][i]:.4f}",
                f"{rec['pz'][i]:.4f}", f"{rec['p_dens'][i]:.4f}",
            ])
    print(f"CSV: {csv_path}")

    # ── Plots ──
    fig, ax = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(
        "Experiment 118 Phase 1: Consumption-Transformation Gravity\n"
        f"EXTEND_RATE={EXTEND_RATE} (compound)  CONSUME={CONSUME_FRAC}  "
        f"star={STAR_COUNT}({STAR_GROUPS}grp)  H=0",
        fontsize=12)

    ax[0, 0].plot(rec['t'], rec['d'], 'b-', lw=0.8)
    ax[0, 0].axhline(p_dist0, color='r', ls='--', alpha=0.4, label='initial')
    ax[0, 0].set(xlabel='tick', ylabel='distance',
                 title='Planet dist from star COM')
    ax[0, 0].legend()

    ax[0, 1].plot(rec['t'], rec['v'], 'g-', lw=0.8)
    ax[0, 1].set(xlabel='tick', ylabel='displacement/tick',
                 title='Planet velocity')

    ax[0, 2].plot(rec['t'], rec['sr'], 'r-', lw=0.8)
    ax[0, 2].set(xlabel='tick', ylabel='mean radius',
                 title='Star cluster radius')

    ax[1, 0].plot(rec['t'], rec['tl'], 'm-', lw=0.8)
    ax[1, 0].set(xlabel='tick', ylabel='total length',
                 title='Total connector length')

    ax[1, 1].plot(rec['t'], rec['p_dens'], 'orange', lw=0.8)
    ax[1, 1].set(xlabel='tick', ylabel='density',
                 title='Planet: max local foreign density')

    pp_x = np.array(rec['px'])
    pp_y = np.array(rec['py'])
    ax[1, 2].plot(pp_x, pp_y, 'b-', lw=0.4, alpha=0.6)
    ax[1, 2].plot(pp_x[0], pp_y[0], 'go', ms=8, label='start')
    ax[1, 2].plot(pp_x[-1], pp_y[-1], 'ro', ms=8, label='end')
    ax[1, 2].plot(com[0], com[1], 'y*', ms=15, label='star COM')
    ax[1, 2].set(xlabel='x', ylabel='y', title='Planet trajectory (XY)')
    ax[1, 2].legend()
    ax[1, 2].set_aspect('equal')

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
    if min(d) < p_dist0 * 0.5 and d[-1] > min(d) * 1.3:
        print("  >> PROMISING: approached then retreated (possible equilibrium)")
    elif d[-1] < p_dist0 * 0.7:
        print("  >> Collapsed (extension too weak)")
    elif d[-1] > p_dist0 * 1.3:
        print("  >> Escaped (extension too strong or no attraction)")
    else:
        print("  >> Near initial distance")


if __name__ == '__main__':
    run()
