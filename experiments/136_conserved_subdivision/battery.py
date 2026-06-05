"""Measurement battery for the leaf-adjacency graph (space) and the history poset.

Every dimension probe is calibrated against geometries with known answers (see tests/).
Probes: hausdorff_dim, diameter_scaling, spectral_dim, poset_ordering_dim, chain_scaling,
loop_density, dirichlet_energy, ricci_summary, betti_from_points. run_battery aggregates.
"""
import numpy as np
import networkx as nx


# ---------- graph dimension ----------
def hausdorff_dim(g, n_sources=40, seed=0, lo_frac=0.01, hi_frac=0.30):
    """Volume growth V(R) ~ R^d via BFS balls; fit log-log slope on the PRE-SATURATION
    power-law window (V between lo_frac*N and hi_frac*N) to avoid finite-graph boundary bias."""
    rng = np.random.default_rng(seed)
    nodes = list(g.nodes())
    N = len(nodes)
    if N < 32:
        return float("nan")
    slopes = []
    for s in rng.choice(N, size=min(n_sources, N), replace=False):
        lengths = nx.single_source_shortest_path_length(g, nodes[s])
        rmax = max(lengths.values()) if lengths else 0
        if rmax < 4:
            continue
        Rs = np.arange(1, rmax + 1)
        V = np.array([sum(1 for d in lengths.values() if d <= R) for R in Rs], float)
        m = (V >= lo_frac * N) & (V <= hi_frac * N) & (Rs > 1)
        if m.sum() >= 3:
            slopes.append(np.polyfit(np.log(Rs[m]), np.log(V[m]), 1)[0])
    return float(np.median(slopes)) if slopes else float("nan")


def diameter_scaling(graphs_by_n):
    ns = sorted(graphs_by_n)
    diam = [nx.approximation.diameter(graphs_by_n[n]) for n in ns]
    pow_exp = float(np.polyfit(np.log(ns), np.log(diam), 1)[0]) if len(ns) > 1 else float("nan")
    looks = "manifold" if pow_exp > 0.2 else "small_world/cloud"
    return {"diam": diam, "pow_exp": pow_exp, "looks": looks}


def spectral_dim(g, tmax=300, n_src=24, seed=0):
    """P(t) ~ t^(-d_s/2): return prob of a lazy random walk averaged over many sources;
    slope on the diffusive plateau window (well inside the mixing time)."""
    nodes = list(g.nodes())
    N = len(nodes)
    if N < 32:
        return float("nan")
    A = nx.to_scipy_sparse_array(g, nodelist=nodes).astype(float)
    deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1.0
    rng = np.random.default_rng(seed)
    srcs = rng.choice(N, size=min(n_src, N), replace=False)
    ret = np.zeros(tmax)
    for src in srcs:
        p = np.zeros(N); p[src] = 1.0
        for t in range(tmax):
            p = 0.5 * p + 0.5 * (A @ (p / deg))
            ret[t] += p[src]
    ret /= len(srcs)
    ts = np.arange(1, tmax + 1)
    lo, hi = max(2, tmax // 15), tmax // 3
    if hi - lo < 3:
        return float("nan")
    return float(-2 * np.polyfit(np.log(ts[lo:hi]), np.log(ret[lo:hi]), 1)[0])


# ---------- poset probes ----------
def _ordering_fraction(rel, n):
    R = sum(len(v) for v in rel.values())          # related (comparable) pairs, transitive closure
    total = n * (n - 1) / 2
    return (R / total) if total else 0.0


def poset_ordering_dim(rel):
    """Product-order ordering dimension: f = R/C(n,2) ~ 2^(1-d)  =>  d = 1 - log2(f).
    Exact for a dominance sprinkle; heuristic on other posets. (Stand-in for Minkowski Myrheim-Meyer.)"""
    n = len(rel)
    f = _ordering_fraction(rel, n)
    if f <= 0:
        return float("nan")
    return float(1.0 - np.log2(f))


def chain_scaling(rels_by_n):
    ns = sorted(rels_by_n)
    heights = []
    for n in ns:
        rel = rels_by_n[n]
        dg = nx.DiGraph()
        for i, js in rel.items():
            for j in js:
                dg.add_edge(i, j)
        heights.append(nx.dag_longest_path_length(dg) if dg.number_of_edges() else 1)
    exp = float(np.polyfit(np.log(ns), np.log(heights), 1)[0]) if len(ns) > 1 else float("nan")
    return {"heights": heights, "height_exp": exp}     # ~1/d : 3D->0.33


# ---------- structure / curvature ----------
def loop_density(g):
    return (g.number_of_edges() - g.number_of_nodes() + nx.number_connected_components(g)) / max(1, g.number_of_nodes())


def dirichlet_energy(g, x):
    return float(sum((x[u] - x[v]) ** 2 for u, v in g.edges()))


def _ricci_edge(g, u, v, alpha=0.5, cutoff=3):
    """Ollivier-Ricci of edge (u,v): kappa = 1 - W1(m_u, m_v)/d(u,v), d=1 for an edge.
    m_x = lazy distribution (alpha on x, (1-alpha) uniform on neighbors). W1 via POT exact EMD."""
    import ot
    nu = list(g.neighbors(u)); nv = list(g.neighbors(v))
    su = [u] + nu; sv = [v] + nv
    pu = np.array([alpha] + [(1 - alpha) / len(nu)] * len(nu)) if nu else np.array([1.0])
    pv = np.array([alpha] + [(1 - alpha) / len(nv)] * len(nv)) if nv else np.array([1.0])
    C = np.empty((len(su), len(sv)))
    for i, a in enumerate(su):
        L = nx.single_source_shortest_path_length(g, a, cutoff=cutoff)
        for j, b in enumerate(sv):
            C[i, j] = L.get(b, cutoff + 1)
    return 1.0 - float(ot.emd2(pu, pv, C))


def ricci_summary(g, max_mean_degree=100, sample_edges=1500, seed=0):
    """Median Ollivier-Ricci over (sampled) edges (POT-based, no networkit).
    Guards on MEAN DEGREE (near-complete substrate graphs -> degenerate), not edge count,
    so it still computes on sparse RGGs/grids while skipping the dense bare substrate."""
    N = g.number_of_nodes(); E = g.number_of_edges()
    if N == 0 or 2 * E / N > max_mean_degree:
        return {"median": float("nan"), "iqr": float("nan"), "degenerate": True}
    edges = list(g.edges())
    if len(edges) > sample_edges:
        rng = np.random.default_rng(seed)
        edges = [edges[i] for i in rng.choice(len(edges), size=sample_edges, replace=False)]
    ks = [_ricci_edge(g, u, v) for u, v in edges]
    return {"median": float(np.median(ks)), "iqr": float(np.subtract(*np.percentile(ks, [75, 25]))), "degenerate": False}


def betti_from_points(points, max_edge, dim=2):
    import gudhi
    rc = gudhi.RipsComplex(points=np.asarray(points, float), max_edge_length=max_edge)
    st = rc.create_simplex_tree(max_dimension=dim + 1)
    st.compute_persistence()
    bn = st.betti_numbers()
    return [int(bn[i]) if i < len(bn) else 0 for i in range(dim + 1)]


# ---------- aggregator ----------
def run_battery(g, rel=None, points=None, max_edge=None):
    out = {
        "n": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "d_hausdorff": hausdorff_dim(g),
        "d_spectral": spectral_dim(g),
        "loop_density": loop_density(g),
        "ricci_median": ricci_summary(g)["median"],
    }
    if rel is not None:
        out["d_poset_ordering"] = poset_ordering_dim(rel)
    if points is not None and max_edge is not None:
        out["betti"] = betti_from_points(points, max_edge)
    return out
