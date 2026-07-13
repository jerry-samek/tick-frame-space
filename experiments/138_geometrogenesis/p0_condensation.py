"""Exp 138 Phase P0 — cycle condensation on triangle-free 4-regular graphs
(PREREG_P0.md). Action H = -J * sum_edges kappa_exact (fast matching path);
Metropolis double-edge swaps with hard-core (no-triangle) constraint.
"""

import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from curvature import kappa_exact_regular  # noqa: E402
from graphs import random_regular  # noqa: E402
from instrument import classify  # noqa: E402

N_NODES = 256
K_DEG = 4
SWEEPS = 1500
CHECK_EVERY = 25
LADDER = (0.5, 1.0, 2.0, 4.0, 8.0)
N_SEEDS = 10


def _has_common_neighbor(adj, a, c):
    return bool(adj[a] & adj[c])


def _triangle_free(adj):
    return all(not (adj[i] & adj[j]) for i in range(len(adj)) for j in adj[i]
               if i < j)


def make_trianglefree_rrg(n, k, rng):
    """RRG repaired to triangle-free via rejected-triangle double swaps."""
    lists = random_regular(n, k, rng)
    adj = [set(x) for x in lists]
    edges = sorted({(min(i, j), max(i, j)) for i in range(n) for j in adj[i]})
    for _ in range(200000):
        tri = [(i, j) for (i, j) in edges if adj[i] & adj[j]]
        if not tri:
            return adj, edges
        i, j = tri[int(rng.integers(len(tri)))]
        c, d = edges[int(rng.integers(len(edges)))]
        ok, new = _try_swap(adj, (i, j), (c, d), rng)
        if ok:
            edges = _apply_swap(adj, edges, (i, j), (c, d), new)
    raise RuntimeError("triangle repair did not converge")


def _try_swap(adj, e1, e2, rng):
    """Propose rewiring e1=(a,b), e2=(c,d) -> (a,c),(b,d) or (a,d),(b,c)
    (chosen by rng); return (valid, ((x1,y1),(x2,y2)))."""
    a, b = e1
    c, d = e2
    if len({a, b, c, d}) < 4:
        return False, None
    if rng.random() < 0.5:
        p1, p2 = (a, c), (b, d)
    else:
        p1, p2 = (a, d), (b, c)
    for (x, y) in (p1, p2):
        if y in adj[x]:
            return False, None
    # hard-core: no triangle creation
    tmp_removed = [(a, b), (c, d)]
    for (x, y) in tmp_removed:
        adj[x].discard(y)
        adj[y].discard(x)
    ok = not (_has_common_neighbor(adj, *p1) or _has_common_neighbor(adj, *p2))
    # also the two new edges together must not form a triangle with each other
    if ok:
        for (x, y) in (p1, p2):
            adj[x].add(y)
            adj[y].add(x)
        ok2 = not (adj[p1[0]] & adj[p1[1]] or adj[p2[0]] & adj[p2[1]])
        for (x, y) in (p1, p2):
            adj[x].discard(y)
            adj[y].discard(x)
        ok = ok2
    for (x, y) in tmp_removed:
        adj[x].add(y)
        adj[y].add(x)
    return (ok, (p1, p2)) if ok else (False, None)


def _apply_swap(adj, edges, e1, e2, new):
    for (x, y) in (e1, e2):
        adj[x].discard(y)
        adj[y].discard(x)
    for (x, y) in new:
        adj[x].add(y)
        adj[y].add(x)
    es = set(edges)
    es.discard((min(e1[0], e1[1]), max(e1[0], e1[1])))
    es.discard((min(e2[0], e2[1]), max(e2[0], e2[1])))
    for (x, y) in new:
        es.add((min(x, y), max(x, y)))
    return sorted(es)


def _incident_edges(adj, verts):
    """Edges with an endpoint within distance 1 of `verts` (radius-1 ball) —
    the widened local set for delta-H (kappa reaches distance-2 structure;
    residual error is monitored via energy_drift and resynced)."""
    ball = set(verts)
    for v in verts:
        ball |= adj[v]
    out = set()
    for v in ball:
        for u in adj[v]:
            out.add((min(u, v), max(u, v)))
    return sorted(out)


def _lists(adj):
    return [sorted(s) for s in adj]


def _energy_edges(adj, edge_list, J):
    # kappa fast path accepts sets directly (order-invariant matching min)
    return -J * sum(kappa_exact_regular(adj, i, j) for (i, j) in edge_list)


def _squares_per_edge(adj, edges):
    total = 0
    for (u, v) in edges:
        nu = adj[u] - {v}
        nv = adj[v] - {u}
        total += sum(len(adj[x] & nv) for x in nu)
    return total / (4 * len(edges))


def metropolis_run(n, k, coupling, sweeps, seed, check_every=CHECK_EVERY):
    rng = np.random.default_rng(seed)
    adj, edges = make_trianglefree_rrg(n, k, rng)
    energy = _energy_edges(adj, edges, coupling)
    cls0 = classify(_lists(adj), np.random.default_rng(seed * 7919))
    trace, checkpoints = [], [{"sweep": 0, "energy_full": energy,
                               "energy_drift": 0.0, "cls": cls0["cls"],
                               "e_hat": cls0["e_hat"],
                               "r2_gap": cls0["r2_poly"] - cls0["r2_exp"],
                               "squares_per_edge": _squares_per_edge(adj, edges),
                               "accept_rate": 0.0}]
    accept = 0
    tries = 0
    t0 = time.time()
    for sweep in range(1, sweeps + 1):
        for _ in range(n):
            tries += 1
            i1, i2 = rng.integers(len(edges)), rng.integers(len(edges))
            if i1 == i2:
                continue
            e1, e2 = edges[int(i1)], edges[int(i2)]
            ok, new = _try_swap(adj, e1, e2, rng)
            if not ok:
                continue
            old_local = _incident_edges(adj, set(e1) | set(e2))
            e_old = _energy_edges(adj, old_local, coupling)
            edges2 = _apply_swap(adj, edges, e1, e2, new)
            new_local = _incident_edges(adj, set(e1) | set(e2))
            e_new = _energy_edges(adj, new_local, coupling)
            dh = e_new - e_old
            if dh <= 0 or rng.random() < np.exp(-dh):
                edges = edges2
                energy += dh
                accept += 1
            else:  # revert
                edges = _apply_swap(adj, edges2, new[0], new[1], (e1, e2))
        if sweep % check_every == 0:
            full = _energy_edges(adj, edges, coupling)
            cls = classify(_lists(adj), np.random.default_rng(seed * 7919 + sweep))
            checkpoints.append({"sweep": sweep, "energy_full": full,
                                "energy_drift": full - energy,
                                "cls": cls["cls"], "e_hat": cls["e_hat"],
                                "r2_gap": cls["r2_poly"] - cls["r2_exp"],
                                "squares_per_edge": _squares_per_edge(adj, edges),
                                "accept_rate": accept / max(tries, 1)})
            energy = full  # resync against local-approximation drift
        trace.append(round(energy, 6))
    return {"adj": _lists(adj), "energy_trace": trace,
            "checkpoints": checkpoints, "seed": seed, "coupling": coupling,
            "wall_sec": round(time.time() - t0, 1)}


def _cell(args):
    J, seed = args
    r = metropolis_run(N_NODES, K_DEG, J, SWEEPS, seed)
    last = r["checkpoints"][-1]
    print(f"  J={J} seed={seed}: cls={last['cls']} e_hat={last['e_hat']:.2f} "
          f"sq/edge={last['squares_per_edge']:.3f} "
          f"drift={last['energy_drift']:+.4f} ({r['wall_sec']}s)", flush=True)
    r.pop("adj")  # keep JSON small; final class stats suffice
    return r


def main():
    if "--smoke" in sys.argv:
        r = metropolis_run(128, 4, 4.0, 200, seed=0)
        for c in r["checkpoints"]:
            print(c)
        return
    t0 = time.time()
    cells = [(J, 1000 + s) for J in LADDER for s in range(N_SEEDS)]
    with Pool(16) as pool:
        results = pool.map(_cell, cells)
    out = {"prereg": "PREREG_P0.md", "runs": results, "gate": {}}
    g = {}
    for J in LADDER:
        finals = [r["checkpoints"][-1]["cls"] for r in results
                  if r["coupling"] == J]
        g[f"poly_count_J{J}"] = finals.count("poly")
    n_low = g[f"poly_count_J{LADDER[0]}"]
    g["exists_condensing_J"] = any(g[f"poly_count_J{J}"] >= 8 for J in LADDER)
    g["low_J_stays_exp"] = (N_SEEDS - n_low) >= 8
    g["G_P0_PASS"] = bool(g["exists_condensing_J"] and g["low_J_stays_exp"])
    out["gate"] = g
    print("\n=== gate G-P0 ===")
    for k, v in g.items():
        print(f"  {k}: {v}")
    print(f"wall clock: {round(time.time() - t0, 1)}s")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p0.json").write_text(json.dumps(out, indent=2,
                                                         default=float))


if __name__ == "__main__":
    main()
