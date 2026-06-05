"""Null / calibration geometries with KNOWN dimension.

poisson_3d -> d=3 (positive benchmark)   grid_2d -> d=2   random_tree -> d_s=4/3
eden_blob -> compact "cloud-with-clumps" negative   diffusion_field -> over-smoothing negative
"""
import numpy as np
import networkx as nx
from scipy.spatial import cKDTree


def poisson_3d(n, seed, radius=None):
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 3))
    if radius is None:
        # mean degree ~8 (sparser -> larger diameter -> more shells for clean dimension reading)
        radius = (8.0 / (n * 4.18879)) ** (1.0 / 3.0)
    tree = cKDTree(pts)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for i, j in tree.query_pairs(radius):
        g.add_edge(i, j)
    comp = max(nx.connected_components(g), key=len)
    g = g.subgraph(comp).copy()
    return g, pts[list(g.nodes())] if len(g) < n else pts


def grid_2d(side):
    return nx.convert_node_labels_to_integers(nx.grid_2d_graph(side, side))


def random_tree(n, seed):
    for name in ("random_labeled_tree", "random_tree"):
        f = getattr(nx, name, None)
        if f is not None:
            try:
                return f(n, seed=seed)
            except TypeError:
                return f(n)
    raise RuntimeError("no random tree generator in this networkx")


def eden_blob(n, seed):
    rng = np.random.default_rng(seed)
    g = nx.Graph(); g.add_node((0, 0)); occ = {(0, 0)}
    frontier = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while g.number_of_nodes() < n and frontier:
        c = frontier.pop(int(rng.integers(len(frontier))))
        if c in occ:
            continue
        occ.add(c); g.add_node(c)
        for d in dirs:
            nb = (c[0] + d[0], c[1] + d[1])
            if nb in occ:
                g.add_edge(c, nb)
            else:
                frontier.append(nb)
    return nx.convert_node_labels_to_integers(g)


def diffusion_field(n, seed, steps=200):
    g, pts = poisson_3d(n, seed)
    nodes = list(g.nodes())
    A = nx.to_scipy_sparse_array(g, nodelist=nodes).astype(float)
    deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1.0
    x = np.zeros(len(nodes)); x[0] = 1.0
    for _ in range(steps):
        x = (A @ x) / deg
    return g, pts, {nodes[i]: float(x[i]) for i in range(len(nodes))}
