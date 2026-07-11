"""Exp 138 P0 — skeptic-mandated autopsy of a condensed graph (tests 2-4).

Runs on results/p0_condensed_J4_s1000.json (saved by the splice spot-check):
  A1 connectivity census + diameter
  A2 cycle census (4-/6-cycles per edge) + per-vertex square participation
  A3 fraction of vertices whose 1-ball edge pattern matches the square
     lattice (each vertex: 4 neighbors, 0 triangles, >=4 squares through it)
  A4 spectral dimension via lazy random-walk return probability
     d_s(t) = -2 dlog p_ii(t) / dlog t (Kelly-Trugenberger's own diagnostic)
  A5 source-resampling stability: 100 independent 64-source draws -> poly
     fraction + e_hat spread
  A6 structure anchors at N=256 under the frozen instrument: torus2d(16),
     square tube C64 x C4 (the quasi-1D null), triangle-free RRG.
"""

import json
import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import bfs_distances, torus2d  # noqa: E402
from instrument import classify, fit_exponent, shell_counts  # noqa: E402
from p0_condensation import make_trianglefree_rrg, _lists  # noqa: E402


def tube_c64_c4():
    """C_64 x C_4: 4-regular, triangle-free, N=256, sq/edge = 0.5 — the
    quasi-1D null the skeptic demanded."""
    idx = lambda a, b: a * 4 + b  # noqa: E731
    adj = [[] for _ in range(256)]
    for a in range(64):
        for b in range(4):
            adj[idx(a, b)] = sorted({idx((a + 1) % 64, b), idx((a - 1) % 64, b),
                                     idx(a, (b + 1) % 4), idx(a, (b - 1) % 4)})
    return adj


def components(adj):
    n = len(adj)
    seen = set()
    sizes = []
    for s in range(n):
        if s in seen:
            continue
        c = 0
        q = deque([s])
        seen.add(s)
        while q:
            v = q.popleft()
            c += 1
            for u in adj[v]:
                if u not in seen:
                    seen.add(u)
                    q.append(u)
        sizes.append(c)
    return sorted(sizes, reverse=True)


def diameter(adj):
    return max(max(bfs_distances(adj, s).values()) for s in range(len(adj)))


def cycle_census(adj):
    sets = [set(x) for x in adj]
    edges = [(i, j) for i in range(len(adj)) for j in adj[i] if i < j]
    sq_per_edge = []
    sq_per_vertex = np.zeros(len(adj))
    for (u, v) in edges:
        nu = sets[u] - {v}
        nv = sets[v] - {u}
        squares = sum(len(sets[x] & nv) for x in nu)
        sq_per_edge.append(squares)
    # per-vertex square participation: count 4-cycles through each vertex
    for (u, v) in edges:
        nu = sets[u] - {v}
        nv = sets[v] - {u}
        for x in nu:
            common = sets[x] & nv
            for y in common:
                for z in (u, v, x, y):
                    sq_per_vertex[z] += 1
    sq_per_vertex /= 4  # each square counted once per its 4 edges
    return {"sq_per_edge_mean": float(np.mean(sq_per_edge)),
            "sq_per_vertex_hist": np.bincount(
                sq_per_vertex.astype(int), minlength=8)[:8].tolist(),
            "vertices_with_0_squares": int(np.sum(sq_per_vertex < 1))}


def lattice_like_fraction(adj):
    """Vertex is 'square-lattice-local' if: degree 4, no triangle at it,
    and >= 4 distinct squares pass through it (torus2d value: 4)."""
    sets = [set(x) for x in adj]
    good = 0
    for v in range(len(adj)):
        if len(adj[v]) != 4:
            continue
        nb = sorted(adj[v])
        if any(sets[a] & sets[v] for a in nb):
            continue  # triangle
        squares = 0
        for ai in range(len(nb)):
            for bi in range(ai + 1, len(nb)):
                squares += len((sets[nb[ai]] & sets[nb[bi]]) - {v})
        if squares >= 4:
            good += 1
    return good / len(adj)


def spectral_dimension(adj, t_max=200):
    """Lazy random walk return probability; d_s from the slope of
    log p(t) vs log t over t in [20, t_max]."""
    n = len(adj)
    P = np.zeros((n, n))
    for i in range(n):
        for j in adj[i]:
            P[i, j] = 1.0 / (2 * len(adj[i]))
        P[i, i] = 0.5
    p = np.eye(n)
    returns = []
    for t in range(1, t_max + 1):
        p = p @ P
        returns.append(float(np.mean(np.diag(p))))
    ts = np.arange(20, t_max + 1)
    ys = np.log(np.array(returns[19:]))
    A = np.vstack([np.log(ts), np.ones_like(ts, dtype=float)]).T
    slope, _ = np.linalg.lstsq(A, ys, rcond=None)[0]
    return -2.0 * float(slope)


def main():
    data = json.load(open(HERE / "results" / "p0_condensed_J4_s1000.json"))
    adj = [list(map(int, row)) for row in data["adj"]]
    out = {}

    comps = components(adj)
    out["A1"] = {"n_components": len(comps), "sizes_top3": comps[:3],
                 "diameter_lcc": diameter(adj) if len(comps) == 1 else None}
    print(f"A1 connectivity: {len(comps)} component(s), sizes {comps[:3]}, "
          f"diameter={out['A1']['diameter_lcc']}")

    out["A2"] = cycle_census(adj)
    print(f"A2 cycles: sq/edge={out['A2']['sq_per_edge_mean']:.3f} "
          f"sq-per-vertex hist={out['A2']['sq_per_vertex_hist']} "
          f"zero-square vertices={out['A2']['vertices_with_0_squares']}")

    out["A3"] = {"lattice_like_fraction": lattice_like_fraction(adj)}
    print(f"A3 lattice-local fraction: {out['A3']['lattice_like_fraction']:.3f} "
          f"(torus2d = 1.0 by construction)")

    out["A4"] = {"d_spectral": spectral_dimension(adj)}
    print(f"A4 spectral dimension (lazy walk, t=20..200): "
          f"{out['A4']['d_spectral']:.2f}")

    fracs, ehats = [], []
    for s in range(100):
        rng = np.random.default_rng(50000 + s)
        f = classify(adj, rng)
        fracs.append(1 if f["cls"] == "poly" else 0)
        ehats.append(f["e_hat"])
    out["A5"] = {"poly_fraction": float(np.mean(fracs)),
                 "e_hat_mean": float(np.mean(ehats)),
                 "e_hat_sd": float(np.std(ehats))}
    print(f"A5 source-resampling: poly {np.mean(fracs):.2f} "
          f"e_hat {np.mean(ehats):.3f}+/-{np.std(ehats):.3f}")

    print("A6 structure anchors at N=256:")
    anchors = {}
    for name, g in (("torus2d_16", torus2d(16)), ("tube_C64xC4", tube_c64_c4()),
                    ("tf_rrg_256", _lists(make_trianglefree_rrg(
                        256, 4, np.random.default_rng(0))[0]))):
        f = classify(g, np.random.default_rng(60000))
        anchors[name] = f
        ds = spectral_dimension(g)
        anchors[name]["d_spectral"] = ds
        print(f"  {name}: cls={f['cls']} e_hat={f['e_hat']:.3f} "
              f"r2_gap={f['r2_poly']-f['r2_exp']:+.4f} d_s={ds:.2f}")
    out["A6"] = anchors

    (HERE / "results" / "p0_autopsy.json").write_text(
        json.dumps(out, indent=2, default=float))


if __name__ == "__main__":
    main()
