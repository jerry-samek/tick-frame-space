#!/usr/bin/env python3
"""
Experiment 118 v5: Recursive Producer-Consumer

Same algorithm at every level:
  absorb known -> grow
  reject unknown -> route outward, extend connectors
  if rejection hits another entity -> that entity processes it (recursive)
  if no interception -> create/grow seed -> promote to child entity

Star is not special. Planets, moons: same code, different sub-stream.
Hierarchy emerges from spatial interception during rejection routing.

Changes from v4:
  - Entity has children, seeds, parent, depth (tree structure)
  - process() is recursive with spatial interception
  - node_owner maps nodes to owning entities
  - N_TYPES=8 for deeper hierarchy potential
"""

import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict
import os, time, csv

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# -- Config ---------------------------------------------------------------
RNG_SEED         = 42
N_NODES          = 20000
SPHERE_R         = 20.0
TARGET_K         = 24

N_TYPES          = 8
STAR_SPECTRUM    = frozenset(range(3))  # 37.5% known
GROWTH_COST      = 10
PLANET_THRESHOLD = 80
REJECTION_HOPS   = 10
EXTEND_RATE      = 0.01

TICKS            = 100000
LOG_EVERY        = 2000
MEASURE_EVERY    = 200

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# -- Connector ------------------------------------------------------------
class Conn:
    __slots__ = ('length', 'length0')
    def __init__(self, length):
        self.length = length
        self.length0 = length


# -- Graph ----------------------------------------------------------------
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
    def __init__(self, name, node, spectrum, pos,
                 parent=None, depth=0, birth_tick=0):
        self.name = name
        self.nodes = {node}
        self.frontier = {node}
        self.spectrum = frozenset(spectrum)
        self.children = []
        self.seeds = {}          # type -> Seed
        self.parent = parent
        self.depth = depth
        self.energy = 0
        self.consumed = 0
        self.rejected = 0
        self.birth_tick = birth_tick
        self._com = pos[node].astype(float).copy()

    def mass(self):
        return len(self.nodes)

    def com(self):
        return self._com

    def radius(self, pos):
        if len(self.nodes) < 2:
            return 0.0
        c = self._com
        return np.mean([np.linalg.norm(pos[n] - c) for n in self.nodes])

    def absorb(self, adj, node_owner, rng, pos):
        """Known type: energy++, claim neighbor when full."""
        self.consumed += 1
        self.energy += 1
        if self.energy < GROWTH_COST:
            return
        self.energy = 0
        for src in sorted(self.frontier):
            unclaimed = [nb for nb in adj[src] if nb not in node_owner]
            if not unclaimed:
                self.frontier.discard(src)
                continue
            new = unclaimed[rng.integers(len(unclaimed))]
            self.nodes.add(new)
            self.frontier.add(new)
            node_owner[new] = self
            # Incremental COM
            m = len(self.nodes)
            self._com = (self._com * (m - 1) + pos[new]) / m
            if not any(nb not in node_owner for nb in adj[src]):
                self.frontier.discard(src)
            return


# -- Seed -----------------------------------------------------------------
class Seed:
    def __init__(self, node, stype, tick):
        self.node = node
        self.stype = stype
        self.mass = 1
        self.birth_tick = tick


# -- Push seed away from parent -------------------------------------------
def push_seed(seed, pos, adj, conn, parent_com):
    d = pos[seed.node] - parent_com
    n = np.linalg.norm(d)
    if n < 1e-15:
        return
    d /= n
    nbrs = adj[seed.node]
    if not nbrs:
        return
    nxt = max(nbrs, key=lambda nb: np.dot(pos[nb] - pos[seed.node], d))
    if np.linalg.norm(pos[nxt] - parent_com) > np.linalg.norm(
            pos[seed.node] - parent_com):
        get_conn(conn, seed.node, nxt).length *= (1 + EXTEND_RATE)
        seed.node = nxt


# -- Process: same algorithm at every level --------------------------------
def process(entity, stream_type, tick, pos, adj, conn,
            node_owner, all_entities, events, rng,
            hops_left=None, visited=None):
    """
    Absorb if known. Reject outward if unknown.
    Spatial interception: if rejection enters another entity, that entity
    processes the particle recursively (same algorithm, smaller sub-stream).
    """
    if hops_left is None:
        hops_left = REJECTION_HOPS
    if hops_left <= 0:
        return
    if visited is None:
        visited = set()
    if id(entity) in visited:
        return
    visited.add(id(entity))

    # 1. Absorb?
    if stream_type in entity.spectrum:
        entity.absorb(adj, node_owner, rng, pos)
        return

    # 2. Find target: child that already covers this type?
    target_child = next(
        (c for c in entity.children if stream_type in c.spectrum), None)
    target_seed = (entity.seeds.get(stream_type)
                   if not target_child else None)
    forming = not target_child          # still in seed phase for this type

    entity.rejected += 1
    com = entity.com()

    frontier = sorted(entity.frontier)
    if not frontier:
        # Child exists but unreachable — absorb directly
        if target_child:
            target_child.absorb(adj, node_owner, rng, pos)
        return

    # Pick ejection point
    if target_child:
        tp = target_child.com()
        src = min(frontier, key=lambda n: np.linalg.norm(pos[n] - tp))
    elif target_seed:
        tp = pos[target_seed.node]
        src = min(frontier, key=lambda n: np.linalg.norm(pos[n] - tp))
    else:
        tp = None
        src = frontier[rng.integers(len(frontier))]

    # Hop outward
    cur = src
    for hop in range(hops_left):
        nbrs = adj[cur]
        if not nbrs:
            break

        if tp is not None:
            nxt = min(nbrs,
                      key=lambda nb: np.linalg.norm(pos[nb] - tp))
        else:
            d = pos[cur] - com
            n = np.linalg.norm(d)
            d = d / n if n > 1e-15 else rng.standard_normal(3)
            nxt = max(nbrs,
                      key=lambda nb: np.dot(pos[nb] - pos[cur], d))

        # Extend connectors only during seed formation (not toward
        # existing children — those paths are already established)
        if forming and nxt not in entity.nodes:
            get_conn(conn, cur, nxt).length *= (1 + EXTEND_RATE)

        # Reached target child?
        if target_child and nxt in target_child.nodes:
            target_child.absorb(adj, node_owner, rng, pos)
            return

        # Intercepted by a different entity?
        if nxt in node_owner and node_owner[nxt] != entity:
            interceptor = node_owner[nxt]
            if interceptor != target_child and id(interceptor) not in visited:
                process(interceptor, stream_type, tick, pos, adj, conn,
                        node_owner, all_entities, events, rng,
                        hops_left=hops_left - hop - 1, visited=visited)
                return

        cur = nxt

    # Endpoint reached
    if target_child:
        # Was routing toward child but didn't reach it — absorb anyway
        target_child.absorb(adj, node_owner, rng, pos)
        return

    # 3. Create/grow seed — only if no child already covers this type
    if stream_type in entity.seeds:
        entity.seeds[stream_type].mass += 1
        push_seed(entity.seeds[stream_type], pos, adj, conn, com)
    else:
        entity.seeds[stream_type] = Seed(cur, stream_type, tick)

    # 4. Promote seed -> child entity?
    sd = entity.seeds.get(stream_type)
    if sd and sd.mass >= PLANET_THRESHOLD:
        child_name = f"{entity.name}/t{sd.stype}"
        child = Entity(child_name, sd.node, {sd.stype}, pos,
                       parent=entity, depth=entity.depth + 1,
                       birth_tick=tick)
        entity.children.append(child)
        node_owner[sd.node] = child
        all_entities.append(child)
        del entity.seeds[stream_type]
        events.append((tick + 1, child_name, child.depth))
        indent = '  ' * child.depth
        print(f"  {indent}*** t={tick + 1}: {child_name} "
              f"(depth={child.depth})")


# -- Human-friendly output ------------------------------------------------
def print_flow(entity, pos, ticks_done, prefix="", is_last=True,
               parent_com=None, parent_total=None):
    """Print entity tree as a pipeline flow diagram."""
    com = entity.com()
    spec = ','.join(str(s) for s in sorted(entity.spectrum))
    total_seen = entity.consumed + entity.rejected

    # Header line
    dist_s = ""
    if parent_com is not None:
        dist_s = f", {np.linalg.norm(com - parent_com):.1f} away"
    born_s = f", born t={entity.birth_tick + 1}" if entity.depth > 0 else ""
    print(f"{prefix}{'`-- ' if entity.depth > 0 else ''}"
          f"{entity.name}  [knows {spec}]  "
          f"{entity.mass()} nodes{dist_s}{born_s}")

    # Flow stats
    child_prefix = prefix + ("    " if is_last else "|   ")
    if entity.depth == 0:
        abs_pct = 100.0 * entity.consumed / ticks_done if ticks_done else 0
        rej_pct = 100.0 * entity.rejected / ticks_done if ticks_done else 0
        print(f"{child_prefix}  absorbed {abs_pct:5.1f}%  ({entity.consumed})  "
              f"--> mass")
        print(f"{child_prefix}  rejected {rej_pct:5.1f}%  ({entity.rejected})  "
              f"--> children")
    else:
        if parent_total and parent_total > 0:
            abs_pct = 100.0 * entity.consumed / parent_total
            print(f"{child_prefix}  absorbed {abs_pct:5.1f}%  "
                  f"of parent rejects ({entity.consumed})")
        if entity.rejected > 0:
            print(f"{child_prefix}  rejected {entity.rejected}  "
                  f"intercepted other types")

    # Children
    items = list(entity.children) + [
        (st, sd) for st, sd in entity.seeds.items()]
    for i, item in enumerate(items):
        last = (i == len(items) - 1)
        connector = child_prefix + ("`-- " if last else "|-- ")
        if isinstance(item, Entity):
            print(f"{child_prefix}|")
            print_flow(item, pos, ticks_done,
                       prefix=child_prefix,
                       is_last=last,
                       parent_com=com,
                       parent_total=entity.rejected or total_seen)
        else:
            st, sd = item
            d = np.linalg.norm(pos[sd.node] - com)
            pct = 100.0 * sd.mass / PLANET_THRESHOLD
            print(f"{child_prefix}|")
            print(f"{connector}[seed t{st}: {sd.mass} particles, "
                  f"{d:.1f} away -- {pct:.0f}% to threshold]")


# -- Simulation -----------------------------------------------------------
def run():
    rng = np.random.default_rng(RNG_SEED)

    print("Building graph...")
    t0 = time.time()
    pos, adj, conn = build_graph(rng)
    print(f"  ({time.time() - t0:.1f}s)")

    origin_node = int(np.argmin(np.linalg.norm(pos, axis=1)))
    star = Entity("star", origin_node, STAR_SPECTRUM, pos)
    node_owner = {origin_node: star}

    all_entities = [star]
    events = []

    unknown_types = sorted(set(range(N_TYPES)) - STAR_SPECTRUM)
    print(f"\nStream:  {N_TYPES} types")
    print(f"Star:    {sorted(STAR_SPECTRUM)} ({len(STAR_SPECTRUM)}/{N_TYPES})")
    print(f"Unknown: {unknown_types}")
    print(f"Growth cost:      {GROWTH_COST}")
    print(f"Planet threshold: {PLANET_THRESHOLD}")
    print(f"Rejection hops:   {REJECTION_HOPS}")

    rec = defaultdict(list)

    print(f"\n{'=' * 60}")
    print(f"SIMULATION  ({TICKS} ticks)")
    print(f"{'=' * 60}")

    t0 = time.time()
    ticks_done = TICKS
    for tick in range(TICKS):
        stream_type = int(rng.integers(N_TYPES))
        process(star, stream_type, tick, pos, adj, conn,
                node_owner, all_entities, events, rng)

        if (tick + 1) % MEASURE_EVERY == 0:
            exts = [c.length / c.length0 for c in conn.values()]
            rec['t'].append(tick + 1)
            rec['star_mass'].append(star.mass())
            rec['n_entities'].append(len(all_entities))
            rec['max_depth'].append(max(e.depth for e in all_entities))
            rec['mean_ext'].append(np.mean(exts))
            rec['max_ext'].append(max(exts))
            rec['claimed'].append(len(node_owner))

        if (tick + 1) % LOG_EVERY == 0:
            rate = (tick + 1) / (time.time() - t0)
            by_depth = defaultdict(int)
            for e in all_entities:
                by_depth[e.depth] += 1
            n_planets = by_depth.get(1, 0)
            n_moons = sum(v for k, v in by_depth.items() if k >= 2)
            hierarchy = f"{n_planets} planet{'s' if n_planets != 1 else ''}"
            if n_moons:
                hierarchy += f", {n_moons} moon{'s' if n_moons != 1 else ''}"
            print(f"  t={tick + 1:5d}  star({star.mass()}) > {hierarchy}  |  "
                  f"claimed {len(node_owner)}/{N_NODES}  ({rate:.0f} t/s)")

        if len(node_owner) >= N_NODES and not hasattr(run, '_full_warned'):
            print(f"  Graph fully claimed at t={tick + 1} "
                  f"-- growth stops, stream continues")
            run._full_warned = True

    elapsed = time.time() - t0
    print(f"\nDone ({elapsed:.1f}s, {ticks_done / elapsed:.0f} t/s)")

    # -- Summary ----------------------------------------------------------
    by_depth = defaultdict(int)
    mass_by_depth = defaultdict(int)
    for e in all_entities:
        by_depth[e.depth] += 1
        mass_by_depth[e.depth] += e.mass()
    total_claimed = len(node_owner)
    n_planets = by_depth.get(1, 0)
    n_moons = sum(v for k, v in by_depth.items() if k >= 2)
    max_depth = max(e.depth for e in all_entities)

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Simulation:  {ticks_done} ticks in {elapsed:.1f}s "
          f"({ticks_done / elapsed:.0f} t/s)")
    print(f"  Graph:       {total_claimed}/{N_NODES} nodes claimed "
          f"({100 * total_claimed / N_NODES:.1f}%)")
    hierarchy = f"1 star, {n_planets} planet{'s' if n_planets != 1 else ''}"
    if n_moons:
        hierarchy += f", {n_moons} moon{'s' if n_moons != 1 else ''}"
    print(f"  Hierarchy:   {hierarchy} (max depth {max_depth})")
    print()
    depth_names = {0: 'star', 1: 'planets', 2: 'moons'}
    print(f"  Mass distribution:")
    for d in sorted(by_depth.keys()):
        label = depth_names.get(d, f'depth {d}')
        pct = 100.0 * mass_by_depth[d] / total_claimed if total_claimed else 0
        print(f"    {label:10s}  {mass_by_depth[d]:5d} nodes  ({pct:5.1f}%)")

    # -- Stream flow ------------------------------------------------------
    print(f"\n{'=' * 60}")
    print(f"STREAM FLOW  ({ticks_done} particles, {N_TYPES} types, 1/tick)")
    print(f"{'=' * 60}")
    print()
    print_flow(star, pos, ticks_done)

    print(f"\n  Formation timeline:")
    for t, name, depth in events:
        print(f"    t={t:5d}  {'  ' * depth}{name}")

    # -- CSV --------------------------------------------------------------
    os.makedirs(OUT, exist_ok=True)
    csv_path = os.path.join(OUT, "v5_results.csv")
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['tick', 'star_mass', 'n_entities', 'max_depth',
                     'mean_ext', 'max_ext', 'claimed'])
        for i in range(len(rec['t'])):
            w.writerow([
                rec['t'][i], rec['star_mass'][i],
                rec['n_entities'][i], rec['max_depth'][i],
                f"{rec['mean_ext'][i]:.6f}",
                f"{rec['max_ext'][i]:.6f}",
                rec['claimed'][i],
            ])
    print(f"\nCSV: {csv_path}")

    # -- Plots ------------------------------------------------------------
    depth_colors = ['gold', 'tab:blue', 'tab:red', 'tab:green',
                    'tab:purple', 'tab:orange']
    fig, ax = plt.subplots(3, 3, figsize=(18, 15))
    fig.suptitle(
        "Exp 118 v5: Recursive Producer-Consumer\n"
        f"types={N_TYPES}  star={sorted(STAR_SPECTRUM)}  "
        f"grow_cost={GROWTH_COST}  threshold={PLANET_THRESHOLD}  "
        f"hops={REJECTION_HOPS}",
        fontsize=11)

    # (0,0) Star mass
    ax[0, 0].plot(rec['t'], rec['star_mass'], 'b-', lw=0.8)
    ax[0, 0].set(xlabel='tick', ylabel='nodes', title='Star mass')

    # (0,1) Entity count + max depth
    ax[0, 1].plot(rec['t'], rec['n_entities'], 'g-', lw=1,
                  label='entities')
    ax01b = ax[0, 1].twinx()
    ax01b.plot(rec['t'], rec['max_depth'], 'r--', lw=0.8,
               label='max depth')
    ax01b.set_ylabel('depth', color='r')
    ax[0, 1].set(xlabel='tick', ylabel='count',
                 title='Entities & max depth')
    ax[0, 1].legend(loc='upper left')
    ax01b.legend(loc='upper right')

    # (0,2) Claimed fraction
    claimed_frac = [c / N_NODES for c in rec['claimed']]
    ax[0, 2].plot(rec['t'], claimed_frac, 'purple', lw=0.8)
    ax[0, 2].set(xlabel='tick', ylabel='fraction',
                 title=f'Claimed nodes (/{N_NODES})')
    ax[0, 2].set_ylim(0, 1.05)

    # (1,0) Entity masses (bar chart)
    colors_list = [depth_colors[min(e.depth, len(depth_colors) - 1)]
                   for e in all_entities]
    ax[1, 0].barh(range(len(all_entities)),
                  [e.mass() for e in all_entities],
                  color=colors_list, height=0.8)
    ax[1, 0].set_yticks(range(len(all_entities)))
    ax[1, 0].set_yticklabels([e.name for e in all_entities], fontsize=5)
    ax[1, 0].set(xlabel='nodes', title='Entity masses (final)')

    # (1,1) Entity distances from parent
    child_ents = [e for e in all_entities if e.parent]
    if child_ents:
        dists = [np.linalg.norm(e.com() - e.parent.com())
                 for e in child_ents]
        bar_colors = [depth_colors[min(e.depth, len(depth_colors) - 1)]
                      for e in child_ents]
        ax[1, 1].barh(range(len(child_ents)), dists,
                      color=bar_colors, height=0.8)
        ax[1, 1].set_yticks(range(len(child_ents)))
        ax[1, 1].set_yticklabels([e.name for e in child_ents], fontsize=5)
    ax[1, 1].set(xlabel='distance', title='Distance from parent')

    # (1,2) Connector extension
    ax[1, 2].plot(rec['t'], rec['mean_ext'], 'purple', lw=0.8,
                  label='mean')
    ax[1, 2].plot(rec['t'], rec['max_ext'], 'red', lw=0.5, alpha=0.5,
                  label='max')
    ax[1, 2].set(xlabel='tick', ylabel='ratio',
                 title='Connector extension')
    ax[1, 2].legend()

    # (2,0) Formation timeline
    if events:
        max_depth = max(d for _, _, d in events)
        for t, name, depth in events:
            c = depth_colors[min(depth, len(depth_colors) - 1)]
            ax[2, 0].scatter(t, depth, s=60, c=c, zorder=5,
                             edgecolors='k', linewidths=0.5)
            ax[2, 0].annotate(name.split('/')[-1], (t, depth),
                              fontsize=5, rotation=30, ha='left',
                              va='bottom')
        ax[2, 0].set_yticks(range(max_depth + 1))
        ax[2, 0].set_yticklabels([f'depth {d}' for d in range(max_depth + 1)],
                                 fontsize=7)
    ax[2, 0].set(xlabel='tick', title='Formation events')

    # (2,1) XY spatial map
    for e in all_entities:
        xy = pos[list(e.nodes)][:, :2]
        c = depth_colors[min(e.depth, len(depth_colors) - 1)]
        s = max(1, 5 - e.depth * 2)
        label = e.name if e.mass() > 5 else None
        ax[2, 1].scatter(xy[:, 0], xy[:, 1], s=s, c=c, alpha=0.4,
                         label=label)
    for e in all_entities:
        for st, sd in e.seeds.items():
            ax[2, 1].plot(pos[sd.node][0], pos[sd.node][1], 'rx', ms=6)
    ax[2, 1].set(xlabel='x', ylabel='y', title='Final XY map')
    ax[2, 1].set_aspect('equal')
    handles, labels = ax[2, 1].get_legend_handles_labels()
    if handles:
        ax[2, 1].legend(handles[:12], labels[:12], fontsize=4,
                        loc='upper right')

    # (2,2) Depth distribution
    by_depth = defaultdict(int)
    mass_by_depth = defaultdict(int)
    for e in all_entities:
        by_depth[e.depth] += 1
        mass_by_depth[e.depth] += e.mass()
    depths = sorted(by_depth.keys())
    ax[2, 2].bar([d - 0.15 for d in depths],
                 [by_depth[d] for d in depths],
                 width=0.3, label='count', color='steelblue')
    ax22b = ax[2, 2].twinx()
    ax22b.bar([d + 0.15 for d in depths],
              [mass_by_depth[d] for d in depths],
              width=0.3, label='total mass', color='coral', alpha=0.7)
    ax[2, 2].set(xlabel='depth', ylabel='count',
                 title='Entities by depth')
    ax[2, 2].legend(loc='upper left')
    ax22b.set_ylabel('total mass')
    ax22b.legend(loc='upper right')
    ax[2, 2].set_xticks(depths)

    plt.tight_layout()
    fig_path = os.path.join(OUT, "v5_results.png")
    plt.savefig(fig_path, dpi=150)
    print(f"Plot: {fig_path}")


if __name__ == '__main__':
    run()
