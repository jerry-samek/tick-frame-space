"""
Deposit dominance region tracking for Experiment 128 v6.

The entity IS where its deposits dominate. This module measures the
deposit dominance map: for each connector, which family has more deposits?
The star region, planet region, boundary, and empty space emerge from
the deposit field directly — independent of where entity nodes are.
"""

import numpy as np
from collections import deque


def dominance_map(substrate):
    """Classify each connector by deposit dominance.

    Returns dict with:
      'star_dominant': count of connectors where star > planet
      'planet_dominant': count where planet > star
      'contested': count where star == planet and both > 0
      'empty': count where both == 0
      'star_volume': sum of star deposits on star-dominant connectors
      'planet_volume': sum of planet deposits on planet-dominant connectors
    """
    s = substrate.conn_star
    p = substrate.conn_planet

    star_dom = (s > p)
    planet_dom = (p > s)
    contested = (s == p) & (s > 0)
    empty = (s == 0) & (p == 0)

    return {
        'star_dominant': int(star_dom.sum()),
        'planet_dominant': int(planet_dom.sum()),
        'contested': int(contested.sum()),
        'empty': int(empty.sum()),
        'star_volume': int(s[star_dom].sum()),
        'planet_volume': int(p[planet_dom].sum()),
    }


def dominance_by_distance(substrate, center_node):
    """Deposit dominance as a function of hop distance from center.

    Returns dict {distance: {star_frac, planet_frac, empty_frac, n_edges}}
    """
    # BFS from center
    n = substrate.n_nodes
    dist = np.full(n, -1, dtype=np.int32)
    dist[center_node] = 0
    queue = deque([center_node])
    while queue:
        node = queue.popleft()
        for k in range(substrate.degree[node]):
            nb = substrate.nbr_node[node, k]
            if nb >= 0 and dist[nb] == -1:
                dist[nb] = dist[node] + 1
                queue.append(nb)

    # Assign each edge to the min distance of its endpoints
    edge_dist = np.minimum(dist[substrate.edges[:, 0]], dist[substrate.edges[:, 1]])

    s = substrate.conn_star
    p = substrate.conn_planet

    star_dom = s > p
    planet_dom = p > s
    empty = (s == 0) & (p == 0)

    max_d = int(edge_dist.max()) + 1
    result = {}
    for d in range(min(max_d, 30)):
        mask = edge_dist == d
        n_edges = int(mask.sum())
        if n_edges == 0:
            continue
        result[d] = {
            'star_frac': float(star_dom[mask].sum() / n_edges),
            'planet_frac': float(planet_dom[mask].sum() / n_edges),
            'empty_frac': float(empty[mask].sum() / n_edges),
            'n_edges': n_edges,
        }
    return result


def dominance_com(substrate):
    """Center of mass of each dominance region.

    Returns (star_com, planet_com) as 3D positions.
    Star COM = weighted average of edge midpoints where star dominates.
    Planet COM = weighted average where planet dominates.
    """
    pos = substrate.pos
    edges = substrate.edges
    midpoints = (pos[edges[:, 0]] + pos[edges[:, 1]]) / 2  # (n_edges, 3)

    s = substrate.conn_star
    p = substrate.conn_planet

    # Star-dominant region COM
    star_mask = s > p
    star_weight = (s - p).astype(np.float32)
    star_weight[~star_mask] = 0
    sw_total = star_weight.sum()
    if sw_total > 0:
        star_com = (star_weight[:, None] * midpoints).sum(axis=0) / sw_total
    else:
        star_com = np.zeros(3)

    # Planet-dominant region COM
    planet_mask = p > s
    planet_weight = (p - s).astype(np.float32)
    planet_weight[~planet_mask] = 0
    pw_total = planet_weight.sum()
    if pw_total > 0:
        planet_com = (planet_weight[:, None] * midpoints).sum(axis=0) / pw_total
    else:
        planet_com = np.zeros(3)

    return star_com, planet_com


def dominance_radius(substrate, com, is_star=True):
    """Mean radius of a dominance region from its COM.

    For star: radius of the star-dominant region.
    For planet: radius of the planet-dominant region.
    """
    pos = substrate.pos
    edges = substrate.edges
    midpoints = (pos[edges[:, 0]] + pos[edges[:, 1]]) / 2

    s = substrate.conn_star
    p = substrate.conn_planet

    if is_star:
        mask = s > p
        weight = (s - p).astype(np.float32)
    else:
        mask = p > s
        weight = (p - s).astype(np.float32)

    weight[~mask] = 0
    w_total = weight.sum()
    if w_total <= 0:
        return 0.0

    dists = np.linalg.norm(midpoints - com, axis=1)
    return float((weight * dists).sum() / w_total)
