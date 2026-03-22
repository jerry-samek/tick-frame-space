#!/usr/bin/env python3
"""
Experiment 118 v6: Token-Addressed Routing

Token = K-element address. Each entity resolves one position of the
address and forwards to the appropriate child. Every entity on the
path does work (grows). Seeds form at the tree frontier where the
path can't be resolved further.

   token (2,0,1,2) arrives at star
     star reads pos[0]=2 → routes to child_2
     child_2 reads pos[1]=0 → routes to grandchild_0
     grandchild reads pos[2]=1 → routes further
     ...until leaf or seed

No absorb/reject. Every token is routed. Hierarchy = decision trie
built from the stream. Depth emerges from token length.
"""

import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict, Counter
import os, time, csv

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# -- Config ---------------------------------------------------------------
RNG_SEED         = 42
N_NODES          = 10000
SPHERE_R         = 20.0
TARGET_K         = 24

TOKEN_K          = 4       # token length = max tree depth
TOKEN_V          = 3       # values per position = branching factor
# → 81 unique tokens, up to 1+3+9+27 = 40 entities

GROWTH_COST      = 10      # tokens processed per new node
SEED_THRESHOLD   = 60      # tokens before seed → child
REJECTION_HOPS   = 8       # hops outward for seed placement
EXTEND_RATE      = 0.01

TICKS            = 100000
LOG_EVERY        = 5000
MEASURE_EVERY    = 500

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


def mask_str(mask):
    """Human-readable mask: '2.0._._' for {0:2, 1:0}."""
    return '.'.join(str(mask[i]) if i in mask else '_'
                    for i in range(TOKEN_K))


# -- Entity ---------------------------------------------------------------
class Entity:
    def __init__(self, name, node, mask, pos,
                 parent=None, depth=0, birth_tick=0):
        self.name = name
        self.nodes = {node}
        self.frontier = {node}
        self.mask = dict(mask)           # path from root: {pos: val}
        self.children = {}               # value -> Entity
        self.seeds = {}                  # value -> Seed
        self.parent = parent
        self.depth = depth
        self.energy = 0
        self.processed = 0               # total tokens routed through
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

    def grow(self, adj, node_owner, rng, pos):
        """Claim a neighbor node from processing energy."""
        self.processed += 1
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
            m = len(self.nodes)
            self._com = (self._com * (m - 1) + pos[new]) / m
            if not any(nb not in node_owner for nb in adj[src]):
                self.frontier.discard(src)
            return


# -- Seed -----------------------------------------------------------------
class Seed:
    def __init__(self, node, value, tick):
        self.node = node
        self.value = value           # the address value at this position
        self.mass = 0
        self.birth_tick = tick

    def feed(self):
        self.mass += 1


# -- Spatial routing for seed placement -----------------------------------
def route_to_seed(entity, value, pos, adj, conn, rng):
    """Route outward from entity toward seed, extending connectors."""
    com = entity.com()
    frontier = sorted(entity.frontier)
    if not frontier:
        return None

    seed = entity.seeds.get(value)
    if seed:
        tp = pos[seed.node]
        src = min(frontier, key=lambda n: np.linalg.norm(pos[n] - tp))
    else:
        src = frontier[rng.integers(len(frontier))]
        tp = None

    cur = src
    for _ in range(REJECTION_HOPS):
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
        if nxt not in entity.nodes:
            get_conn(conn, cur, nxt).length *= (1 + EXTEND_RATE)
        cur = nxt
    return cur


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


# -- Process: route token through the tree ---------------------------------
def process(entity, token, tick, pos, adj, conn,
            node_owner, all_entities, events, rng):
    """
    Each entity resolves one position of the token address.
    1. Grow from processing this token
    2. Read token[depth] to determine next hop
    3. Forward to child (if exists) or feed seed (if forming)
    """
    # 1. This entity does work → grow
    entity.grow(adj, node_owner, rng, pos)

    # 2. What position do I route on?
    route_pos = entity.depth
    if route_pos >= TOKEN_K:
        return  # fully resolved — I'm a leaf

    route_val = token[route_pos]

    # 3. Forward to child or feed seed
    child = entity.children.get(route_val)
    if child:
        # Child exists → forward (child resolves next position)
        process(child, token, tick, pos, adj, conn,
                node_owner, all_entities, events, rng)
        return

    # 4. No child yet → feed/create seed at this frontier
    if route_val in entity.seeds:
        entity.seeds[route_val].feed()
        push_seed(entity.seeds[route_val], pos, adj, conn, entity.com())
    else:
        endpoint = route_to_seed(entity, route_val, pos, adj, conn, rng)
        if endpoint is None:
            return
        sd = Seed(endpoint, route_val, tick)
        sd.feed()
        entity.seeds[route_val] = sd

    # 5. Promote seed → child?
    sd = entity.seeds.get(route_val)
    if sd and sd.mass >= SEED_THRESHOLD:
        child_mask = dict(entity.mask)
        child_mask[route_pos] = route_val
        child_name = f"{entity.name}/{mask_str(child_mask)}"
        child = Entity(child_name, sd.node, child_mask, pos,
                       parent=entity, depth=entity.depth + 1,
                       birth_tick=tick)
        entity.children[route_val] = child
        node_owner[sd.node] = child
        all_entities.append(child)
        del entity.seeds[route_val]
        events.append((tick + 1, child_name, child.depth))
        indent = '  ' * child.depth
        print(f"  {indent}*** t={tick + 1}: [{mask_str(child_mask)}] "
              f"(depth={child.depth})")


# -- Human-friendly output ------------------------------------------------
DEPTH_NAMES = {0: 'star', 1: 'planets', 2: 'moons', 3: 'dust', 4: 'grains'}


def print_flow(entity, pos, ticks_done, prefix="", is_last=True,
               parent_com=None, parent_processed=None):
    """Print entity tree as a routing diagram."""
    com = entity.com()
    ms = mask_str(entity.mask)

    dist_s = ""
    if parent_com is not None:
        dist_s = f", {np.linalg.norm(com - parent_com):.1f} away"
    born_s = f", born t={entity.birth_tick + 1}" if entity.depth > 0 else ""
    print(f"{prefix}{'`-- ' if entity.depth > 0 else ''}"
          f"[{ms}]  {entity.mass()} nodes{dist_s}{born_s}")

    child_prefix = prefix + ("    " if is_last else "|   ")

    # Routing stats
    if parent_processed and parent_processed > 0:
        pct = 100.0 * entity.processed / parent_processed
        print(f"{child_prefix}  routed {pct:5.1f}%  "
              f"of parent ({entity.processed})")
    else:
        print(f"{child_prefix}  routed 100%  ({entity.processed})")

    # Children and seeds
    items = ([(v, entity.children[v]) for v in sorted(entity.children)] +
             [(v, entity.seeds[v]) for v in sorted(entity.seeds)])
    for i, (val, item) in enumerate(items):
        last = (i == len(items) - 1)
        print(f"{child_prefix}|")
        if isinstance(item, Entity):
            print_flow(item, pos, ticks_done,
                       prefix=child_prefix,
                       is_last=last,
                       parent_com=com,
                       parent_processed=entity.processed)
        else:
            connector = child_prefix + ("`-- " if last else "|-- ")
            d = np.linalg.norm(pos[item.node] - com)
            pct = 100.0 * item.mass / SEED_THRESHOLD
            print(f"{connector}[seed val={val}: {item.mass} tokens, "
                  f"{d:.1f} away -- {pct:.0f}% to threshold]")


# -- Simulation -----------------------------------------------------------
def run():
    rng = np.random.default_rng(RNG_SEED)

    print("Building graph...")
    t0 = time.time()
    pos, adj, conn = build_graph(rng)
    print(f"  ({time.time() - t0:.1f}s)")

    # Star: root of the routing tree, empty mask
    origin_node = int(np.argmin(np.linalg.norm(pos, axis=1)))
    star = Entity("star", origin_node, {}, pos)
    node_owner = {origin_node: star}

    all_entities = [star]
    events = []

    n_tokens = TOKEN_V ** TOKEN_K
    print(f"\nToken: K={TOKEN_K} positions, V={TOKEN_V} values "
          f"({n_tokens} unique addresses)")
    print(f"Star: root router (resolves position 0)")
    print(f"Growth cost:    {GROWTH_COST}")
    print(f"Seed threshold: {SEED_THRESHOLD}")
    print(f"Routing hops:   {REJECTION_HOPS}")

    rec = defaultdict(list)

    print(f"\n{'=' * 60}")
    print(f"SIMULATION  ({TICKS} ticks)")
    print(f"{'=' * 60}")

    t0 = time.time()
    ticks_done = TICKS
    graph_full_warned = False
    for tick in range(TICKS):
        token = tuple(int(x) for x in rng.integers(TOKEN_V, size=TOKEN_K))
        process(star, token, tick, pos, adj, conn,
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
            max_d = max(by_depth.keys())
            parts = []
            for d in range(1, max_d + 1):
                n = by_depth.get(d, 0)
                if n > 0:
                    label = DEPTH_NAMES.get(d, f'd{d}')
                    parts.append(f"{n} {label}")
            hierarchy = ", ".join(parts) if parts else "forming..."
            print(f"  t={tick + 1:6d}  star({star.mass()}) > {hierarchy}  |  "
                  f"claimed {len(node_owner)}/{N_NODES}  ({rate:.0f} t/s)")

        if len(node_owner) >= N_NODES and not graph_full_warned:
            print(f"  Graph fully claimed at t={tick + 1}")
            graph_full_warned = True

    elapsed = time.time() - t0
    print(f"\nDone ({elapsed:.1f}s, {ticks_done / elapsed:.0f} t/s)")

    # -- Summary ----------------------------------------------------------
    by_depth = defaultdict(int)
    mass_by_depth = defaultdict(int)
    for e in all_entities:
        by_depth[e.depth] += 1
        mass_by_depth[e.depth] += e.mass()
    total_claimed = len(node_owner)
    max_depth = max(e.depth for e in all_entities)

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Simulation:  {ticks_done} ticks in {elapsed:.1f}s "
          f"({ticks_done / elapsed:.0f} t/s)")
    print(f"  Graph:       {total_claimed}/{N_NODES} nodes claimed "
          f"({100 * total_claimed / N_NODES:.1f}%)")
    print(f"  Entities:    {len(all_entities)} (max depth {max_depth})")
    print()
    print(f"  Mass distribution:")
    for d in sorted(by_depth.keys()):
        label = DEPTH_NAMES.get(d, f'depth {d}')
        pct = 100.0 * mass_by_depth[d] / total_claimed if total_claimed else 0
        print(f"    {label:10s}  {by_depth[d]:3d} entities  "
              f"{mass_by_depth[d]:5d} nodes  ({pct:5.1f}%)")

    # -- Routing tree -----------------------------------------------------
    print(f"\n{'=' * 60}")
    print(f"ROUTING TREE  ({ticks_done} tokens, K={TOKEN_K}, V={TOKEN_V})")
    print(f"{'=' * 60}")
    print()
    print_flow(star, pos, ticks_done)

    print(f"\n  Formation timeline:")
    for t, name, depth in events:
        print(f"    t={t:5d}  {'  ' * depth}{name}")

    # -- CSV --------------------------------------------------------------
    os.makedirs(OUT, exist_ok=True)
    csv_path = os.path.join(OUT, "v6_results.csv")
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
        f"Exp 118 v6: Token-Addressed Routing\n"
        f"K={TOKEN_K}  V={TOKEN_V}  "
        f"grow_cost={GROWTH_COST}  threshold={SEED_THRESHOLD}  "
        f"hops={REJECTION_HOPS}",
        fontsize=11)

    ax[0, 0].plot(rec['t'], rec['star_mass'], 'b-', lw=0.8)
    ax[0, 0].set(xlabel='tick', ylabel='nodes', title='Star mass')

    ax[0, 1].plot(rec['t'], rec['n_entities'], 'g-', lw=1, label='entities')
    ax01b = ax[0, 1].twinx()
    ax01b.plot(rec['t'], rec['max_depth'], 'r--', lw=0.8, label='max depth')
    ax01b.set_ylabel('depth', color='r')
    ax[0, 1].set(xlabel='tick', ylabel='count', title='Entities & depth')
    ax[0, 1].legend(loc='upper left')
    ax01b.legend(loc='upper right')

    claimed_frac = [c / N_NODES for c in rec['claimed']]
    ax[0, 2].plot(rec['t'], claimed_frac, 'purple', lw=0.8)
    ax[0, 2].set(xlabel='tick', ylabel='fraction',
                 title=f'Claimed nodes (/{N_NODES})')
    ax[0, 2].set_ylim(0, 1.05)

    colors_list = [depth_colors[min(e.depth, len(depth_colors) - 1)]
                   for e in all_entities]
    ax[1, 0].barh(range(len(all_entities)),
                  [e.mass() for e in all_entities],
                  color=colors_list, height=0.8)
    ax[1, 0].set_yticks(range(len(all_entities)))
    ax[1, 0].set_yticklabels(
        [mask_str(e.mask) for e in all_entities], fontsize=5)
    ax[1, 0].set(xlabel='nodes', title='Entity masses (final)')

    child_ents = [e for e in all_entities if e.parent]
    if child_ents:
        dists = [np.linalg.norm(e.com() - e.parent.com())
                 for e in child_ents]
        bar_colors = [depth_colors[min(e.depth, len(depth_colors) - 1)]
                      for e in child_ents]
        ax[1, 1].barh(range(len(child_ents)), dists,
                      color=bar_colors, height=0.8)
        ax[1, 1].set_yticks(range(len(child_ents)))
        ax[1, 1].set_yticklabels(
            [mask_str(e.mask) for e in child_ents], fontsize=5)
    ax[1, 1].set(xlabel='distance', title='Distance from parent')

    ax[1, 2].plot(rec['t'], rec['mean_ext'], 'purple', lw=0.8, label='mean')
    ax[1, 2].plot(rec['t'], rec['max_ext'], 'red', lw=0.5, alpha=0.5,
                  label='max')
    ax[1, 2].set(xlabel='tick', ylabel='ratio', title='Connector extension')
    ax[1, 2].legend()

    if events:
        max_d_ev = max(d for _, _, d in events)
        for t, name, depth in events:
            c = depth_colors[min(depth, len(depth_colors) - 1)]
            ax[2, 0].scatter(t, depth, s=60, c=c, zorder=5,
                             edgecolors='k', linewidths=0.5)
        ax[2, 0].set_yticks(range(max_d_ev + 1))
        ax[2, 0].set_yticklabels(
            [DEPTH_NAMES.get(d, f'd{d}') for d in range(max_d_ev + 1)],
            fontsize=7)
    ax[2, 0].set(xlabel='tick', title='Formation events')

    for e in all_entities:
        xy = pos[list(e.nodes)][:, :2]
        c = depth_colors[min(e.depth, len(depth_colors) - 1)]
        s = max(1, 5 - e.depth)
        label = mask_str(e.mask) if e.mass() > 5 else None
        ax[2, 1].scatter(xy[:, 0], xy[:, 1], s=s, c=c, alpha=0.4,
                         label=label)
    ax[2, 1].set(xlabel='x', ylabel='y', title='Final XY map')
    ax[2, 1].set_aspect('equal')
    handles, labels = ax[2, 1].get_legend_handles_labels()
    if handles:
        ax[2, 1].legend(handles[:15], labels[:15], fontsize=4,
                        loc='upper right')

    by_depth2 = defaultdict(int)
    mass_by_depth2 = defaultdict(int)
    for e in all_entities:
        by_depth2[e.depth] += 1
        mass_by_depth2[e.depth] += e.mass()
    depths = sorted(by_depth2.keys())
    ax[2, 2].bar([d - 0.15 for d in depths],
                 [by_depth2[d] for d in depths],
                 width=0.3, label='count', color='steelblue')
    ax22b = ax[2, 2].twinx()
    ax22b.bar([d + 0.15 for d in depths],
              [mass_by_depth2[d] for d in depths],
              width=0.3, label='total mass', color='coral', alpha=0.7)
    ax[2, 2].set(xlabel='depth', ylabel='count', title='Entities by depth')
    ax[2, 2].legend(loc='upper left')
    ax22b.set_ylabel('total mass')
    ax22b.legend(loc='upper right')
    ax[2, 2].set_xticks(depths)

    plt.tight_layout()
    fig_path = os.path.join(OUT, "v6_results.png")
    plt.savefig(fig_path, dpi=150)
    print(f"Plot: {fig_path}")


if __name__ == '__main__':
    run()
