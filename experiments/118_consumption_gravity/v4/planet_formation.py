#!/usr/bin/env python3
"""
Experiment 118 v4: Producer-Consumer Planet Formation

Core idea (producer-consumer filtering):
  1. Single seed entity at origin
  2. Random stream of typed particles arrives each tick
  3. Entity keeps "known" types -> grows (claims neighbor nodes)
  4. Entity rejects "unknown" types -> routed outward, extending connectors
  5. Same unknown type -> routed to same seed location
  6. Seed accumulates mass -> promoted to planet (new entity)
  7. Planet absorbs its type from star's rejects -> grows

No momentum, no velocity, no force. Distance emerges from connector
extension during the rejection process. The connector pushes the seed
outward before it accumulates enough mass to become a planet.
"""

import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict
import os, time, csv

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# -- Configuration --------------------------------------------------------
RNG_SEED         = 42
N_NODES          = 5000
SPHERE_R         = 20.0
TARGET_K         = 24

N_TYPES          = 6                    # types in the random stream
STAR_SPECTRUM    = frozenset(range(3))  # star knows types 0-2 (50%)
GROWTH_COST      = 10     # absorptions needed to claim one new node
PLANET_THRESHOLD = 100    # rejections before seed -> planet
REJECTION_HOPS   = 5      # hops outward per rejection event
EXTEND_RATE      = 0.01   # connector extension per hop

TICKS            = 30000
LOG_EVERY        = 1000
MEASURE_EVERY    = 100

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# -- Connector ------------------------------------------------------------
class Conn:
    __slots__ = ('length', 'length0')

    def __init__(self, length):
        self.length = length
        self.length0 = length


# -- Graph substrate ------------------------------------------------------
def build_graph(rng):
    pts = []
    while len(pts) < N_NODES:
        batch = rng.uniform(-SPHERE_R, SPHERE_R, (N_NODES * 2, 3))
        good = batch[np.linalg.norm(batch, axis=1) <= SPHERE_R]
        pts.extend(good.tolist())
    pos = np.array(pts[:N_NODES])

    rc = SPHERE_R * (TARGET_K / N_NODES) ** (1 / 3)
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
    return pos, adj, conn


def get_conn(conn, i, j):
    return conn[(i, j) if i < j else (j, i)]


# -- Entity ---------------------------------------------------------------
class Entity:
    def __init__(self, name, node, spectrum, birth_tick=0):
        self.name = name
        self.nodes = {node}
        self.frontier = {node}          # nodes with unclaimed neighbors
        self.spectrum = frozenset(spectrum)
        self.energy = 0
        self.consumed = 0
        self.birth_tick = birth_tick

    def mass(self):
        return len(self.nodes)

    def com(self, pos):
        return np.mean([pos[n] for n in self.nodes], axis=0)

    def radius(self, pos):
        if len(self.nodes) < 2:
            return 0.0
        c = self.com(pos)
        return np.mean([np.linalg.norm(pos[n] - c) for n in self.nodes])

    def absorb(self, adj, claimed, rng):
        """Known type arrived: energy++, claim a neighbor when full."""
        self.consumed += 1
        self.energy += 1
        if self.energy < GROWTH_COST:
            return False
        self.energy = 0

        # Claim a random unclaimed neighbor from frontier
        for src in sorted(self.frontier):
            unclaimed = [nb for nb in adj[src] if nb not in claimed]
            if not unclaimed:
                self.frontier.discard(src)
                continue

            new = unclaimed[rng.integers(len(unclaimed))]
            self.nodes.add(new)
            self.frontier.add(new)
            claimed.add(new)

            if not any(nb not in claimed for nb in adj[src]):
                self.frontier.discard(src)
            return True
        return False


# -- Seed (proto-planet) --------------------------------------------------
class Seed:
    def __init__(self, node, stype, tick):
        self.node = node
        self.stype = stype
        self.mass = 1
        self.birth_tick = tick


# -- Rejection: route unknown outward, extend connectors ------------------
def reject(entity, stype, pos, adj, conn, claimed, seeds, rng):
    """
    Route unknown type outward from entity surface.
    Each hop extends the traversed connector.
    Returns the endpoint node.
    """
    com = entity.com(pos)

    frontier = sorted(entity.frontier)
    if not frontier:
        return None

    # Pick ejection point
    if stype in seeds:
        target = pos[seeds[stype].node]
        src = min(frontier, key=lambda n: np.linalg.norm(pos[n] - target))
    else:
        src = frontier[rng.integers(len(frontier))]

    # Hop outward, extending each connector
    cur = src
    for _ in range(REJECTION_HOPS):
        nbrs = adj[cur]
        if not nbrs:
            break

        if stype in seeds:
            target = pos[seeds[stype].node]
            nxt = min(nbrs,
                      key=lambda nb: np.linalg.norm(pos[nb] - target))
        else:
            d = pos[cur] - com
            n = np.linalg.norm(d)
            d = d / n if n > 1e-15 else rng.standard_normal(3)
            nxt = max(nbrs,
                      key=lambda nb: np.dot(pos[nb] - pos[cur], d))

        # Extend connector (only outside the entity)
        if nxt not in entity.nodes:
            get_conn(conn, cur, nxt).length *= (1 + EXTEND_RATE)
        cur = nxt

    return cur


def push_seed(seed, pos, adj, conn, star_com):
    """Push seed one hop further from star. Extends the connector."""
    d = pos[seed.node] - star_com
    n = np.linalg.norm(d)
    if n < 1e-15:
        return
    d /= n

    nbrs = adj[seed.node]
    if not nbrs:
        return

    nxt = max(nbrs, key=lambda nb: np.dot(pos[nb] - pos[seed.node], d))
    if np.linalg.norm(pos[nxt] - star_com) > np.linalg.norm(
            pos[seed.node] - star_com):
        get_conn(conn, seed.node, nxt).length *= (1 + EXTEND_RATE)
        seed.node = nxt


# -- Simulation -----------------------------------------------------------
def run():
    rng = np.random.default_rng(RNG_SEED)

    print("Building graph...")
    t0 = time.time()
    pos, adj, conn = build_graph(rng)
    print(f"  ({time.time() - t0:.1f}s)")

    # Single seed at origin
    origin_node = int(np.argmin(np.linalg.norm(pos, axis=1)))
    star = Entity("star", origin_node, STAR_SPECTRUM)
    claimed = {origin_node}

    entities = [star]
    seeds = {}       # type -> Seed
    events = []      # (tick, description)

    unknown_types = sorted(set(range(N_TYPES)) - STAR_SPECTRUM)
    print(f"\nStream:           {N_TYPES} types")
    print(f"Star spectrum:    {sorted(STAR_SPECTRUM)} "
          f"({len(STAR_SPECTRUM)}/{N_TYPES})")
    print(f"Unknown types:    {unknown_types}")
    print(f"Growth cost:      {GROWTH_COST} absorptions/node")
    print(f"Planet threshold: {PLANET_THRESHOLD} rejections")

    # Recording
    rec = defaultdict(list)
    seed_hist = defaultdict(list)      # type -> [(t, mass, dist)]
    planet_dist = defaultdict(list)    # name -> [(t, dist)]
    planet_mass = defaultdict(list)    # name -> [(t, mass)]

    print(f"\n{'=' * 60}")
    print(f"SIMULATION  ({TICKS} ticks)")
    print(f"{'=' * 60}")

    t0 = time.time()
    for tick in range(TICKS):
        # 1. Draw from stream
        stream_type = int(rng.integers(N_TYPES))

        # 2. Route through entity chain (producer -> consumer pipeline)
        absorbed = False
        for ent in entities:
            if stream_type in ent.spectrum:
                ent.absorb(adj, claimed, rng)
                absorbed = True
                break

        if not absorbed:
            # 3. Reject from star
            endpoint = reject(star, stream_type, pos, adj, conn,
                              claimed, seeds, rng)

            if endpoint is not None:
                if stream_type in seeds:
                    seeds[stream_type].mass += 1
                    push_seed(seeds[stream_type], pos, adj, conn,
                              star.com(pos))
                else:
                    seeds[stream_type] = Seed(endpoint, stream_type, tick)
                    events.append((tick + 1, f"seed_t{stream_type}"))

                # 4. Promote seed -> planet?
                sd = seeds.get(stream_type)
                if sd and sd.mass >= PLANET_THRESHOLD:
                    planet = Entity(f"planet_t{sd.stype}", sd.node,
                                    {sd.stype}, tick)
                    entities.append(planet)
                    claimed.add(sd.node)
                    del seeds[stream_type]
                    events.append((tick + 1, f"PLANET {planet.name}"))
                    print(f"  *** t={tick + 1}: {planet.name} formed!")

        # 5. Measure
        if (tick + 1) % MEASURE_EVERY == 0:
            sc = star.com(pos)
            exts = [c.length / c.length0 for c in conn.values()]

            rec['t'].append(tick + 1)
            rec['star_mass'].append(star.mass())
            rec['star_r'].append(star.radius(pos))
            rec['n_planets'].append(len(entities) - 1)
            rec['n_seeds'].append(len(seeds))
            rec['mean_ext'].append(np.mean(exts))
            rec['max_ext'].append(max(exts))

            for st, sd in seeds.items():
                seed_hist[st].append((
                    tick + 1, sd.mass,
                    np.linalg.norm(pos[sd.node] - sc)))

            for e in entities[1:]:
                planet_dist[e.name].append((
                    tick + 1, np.linalg.norm(e.com(pos) - sc)))
                planet_mass[e.name].append((tick + 1, e.mass()))

        # 6. Log
        if (tick + 1) % LOG_EVERY == 0:
            rate = (tick + 1) / (time.time() - t0)
            seeds_s = " ".join(
                f"t{s.stype}:{s.mass}" for s in seeds.values())
            planets_s = " ".join(
                f"{e.name}({e.mass()})" for e in entities[1:])
            print(f"  t={tick + 1:5d}  star={star.mass():4d}  "
                  f"planets=[{planets_s}]  seeds=[{seeds_s}]  "
                  f"({rate:.0f} t/s)")

    elapsed = time.time() - t0
    print(f"\nDone ({elapsed:.1f}s, {TICKS / elapsed:.0f} t/s)")

    # -- Summary ----------------------------------------------------------
    sc = star.com(pos)
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Star: {star.mass()} nodes, consumed={star.consumed}, "
          f"radius={star.radius(pos):.2f}")
    for e in entities[1:]:
        d = np.linalg.norm(e.com(pos) - sc)
        print(f"  {e.name}: {e.mass()} nodes, dist={d:.2f}, "
              f"consumed={e.consumed}, born t={e.birth_tick + 1}")
    for st, sd in seeds.items():
        d = np.linalg.norm(pos[sd.node] - sc)
        print(f"  seed_t{st}: mass={sd.mass}, dist={d:.2f}")
    print(f"  Claimed: {len(claimed)}/{N_NODES}")
    print(f"  Extension: mean={rec['mean_ext'][-1]:.4f}, "
          f"max={rec['max_ext'][-1]:.4f}")
    print(f"\n  Events:")
    for t, ev in events:
        print(f"    t={t:5d}: {ev}")

    # -- CSV --------------------------------------------------------------
    os.makedirs(OUT, exist_ok=True)
    csv_path = os.path.join(OUT, "v4_results.csv")
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['tick', 'star_mass', 'star_radius', 'n_planets',
                     'n_seeds', 'mean_ext', 'max_ext'])
        for i in range(len(rec['t'])):
            w.writerow([
                rec['t'][i], rec['star_mass'][i],
                f"{rec['star_r'][i]:.4f}",
                rec['n_planets'][i], rec['n_seeds'][i],
                f"{rec['mean_ext'][i]:.6f}",
                f"{rec['max_ext'][i]:.6f}",
            ])
    print(f"\nCSV: {csv_path}")

    # -- Plots ------------------------------------------------------------
    fig, ax = plt.subplots(3, 3, figsize=(18, 15))
    fig.suptitle(
        "Exp 118 v4: Producer-Consumer Planet Formation\n"
        f"types={N_TYPES}  star_spectrum={sorted(STAR_SPECTRUM)}  "
        f"grow_cost={GROWTH_COST}  threshold={PLANET_THRESHOLD}  "
        f"reject_hops={REJECTION_HOPS}",
        fontsize=11)

    # (0,0) Star mass
    ax[0, 0].plot(rec['t'], rec['star_mass'], 'b-', lw=0.8)
    ax[0, 0].set(xlabel='tick', ylabel='nodes', title='Star mass')

    # (0,1) Star radius
    ax[0, 1].plot(rec['t'], rec['star_r'], 'r-', lw=0.8)
    ax[0, 1].set(xlabel='tick', ylabel='radius', title='Star radius')

    # (0,2) Entity count
    ax[0, 2].plot(rec['t'], rec['n_planets'], 'g-', lw=1, label='planets')
    ax[0, 2].plot(rec['t'], rec['n_seeds'], 'orange', lw=1, ls='--',
                  label='seeds')
    ax[0, 2].set(xlabel='tick', ylabel='count', title='Entities')
    ax[0, 2].legend()

    # (1,0) Planet distances
    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    for i, (name, hist) in enumerate(planet_dist.items()):
        ts, ds = zip(*hist)
        ax[1, 0].plot(ts, ds, color=colors[i], lw=0.8, label=name)
    ax[1, 0].set(xlabel='tick', ylabel='dist',
                 title='Planet distance from star')
    if planet_dist:
        ax[1, 0].legend(fontsize=7)

    # (1,1) Planet masses
    for i, (name, hist) in enumerate(planet_mass.items()):
        ts, ms = zip(*hist)
        ax[1, 1].plot(ts, ms, color=colors[i], lw=0.8, label=name)
    ax[1, 1].set(xlabel='tick', ylabel='nodes', title='Planet mass')
    if planet_mass:
        ax[1, 1].legend(fontsize=7)

    # (1,2) Connector extension
    ax[1, 2].plot(rec['t'], rec['mean_ext'], 'purple', lw=0.8,
                  label='mean')
    ax[1, 2].plot(rec['t'], rec['max_ext'], 'red', lw=0.5, alpha=0.5,
                  label='max')
    ax[1, 2].set(xlabel='tick', ylabel='ratio',
                 title='Connector extension')
    ax[1, 2].legend()

    # (2,0) Seed growth
    for st, hist in seed_hist.items():
        ts, ms, _ = zip(*hist)
        ax[2, 0].plot(ts, ms, lw=0.8, label=f'type {st}')
    ax[2, 0].axhline(PLANET_THRESHOLD, color='k', ls='--', alpha=0.4)
    ax[2, 0].set(xlabel='tick', ylabel='mass',
                 title='Seed growth (dashed = threshold)')
    if seed_hist:
        ax[2, 0].legend(fontsize=7)

    # (2,1) Seed push distance
    for st, hist in seed_hist.items():
        ts, _, ds = zip(*hist)
        ax[2, 1].plot(ts, ds, lw=0.8, label=f'type {st}')
    ax[2, 1].set(xlabel='tick', ylabel='dist from star',
                 title='Seed push distance')
    if seed_hist:
        ax[2, 1].legend(fontsize=7)

    # (2,2) XY spatial map
    star_xy = pos[list(star.nodes)][:, :2]
    ax[2, 2].scatter(star_xy[:, 0], star_xy[:, 1],
                     s=2, c='gold', alpha=0.3, label='star')
    for i, e in enumerate(entities[1:]):
        xy = pos[list(e.nodes)][:, :2]
        ax[2, 2].scatter(xy[:, 0], xy[:, 1],
                         s=5, color=colors[i], alpha=0.5, label=e.name)
    for st, sd in seeds.items():
        ax[2, 2].plot(pos[sd.node][0], pos[sd.node][1],
                      'rx', ms=10)
    ax[2, 2].set(xlabel='x', ylabel='y', title='Final XY map')
    ax[2, 2].set_aspect('equal')
    ax[2, 2].legend(fontsize=7)

    plt.tight_layout()
    fig_path = os.path.join(OUT, "v4_results.png")
    plt.savefig(fig_path, dpi=150)
    print(f"Plot: {fig_path}")


if __name__ == '__main__':
    run()
