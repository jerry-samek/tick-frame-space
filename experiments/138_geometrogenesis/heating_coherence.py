"""Heat as an INTERNAL coherence limit (Tom, 2026-07-13): a maximum stable
pattern size = the framework's Eddington/Chandrasekhar limit.

Heat is not external gravitational absorption (dissolved, RAW 135 §13.5). It is
the pattern's OWN metabolic flux, produced throughout its VOLUME, that must be
shed through its SURFACE. A single/simple pattern channels it directly (core =
surface, no bottleneck). A COMPOSITE pattern must transport flux from its core
out through its layers; production ~ volume (R^3), shedding ~ surface (R^2), so
the per-node core load grows with size. Past a critical size the core saturates,
the surface cannot shed the excess, it is forced to re-incorporate deposits, and
the overload DECOHERES the pattern.

Model (substrate-native): a ball of radius R in a 3D lattice. Every node
produces p flux/tick; flux diffuses along edges; boundary nodes shed (radiate to
the outside). Steady-state PEAK node load = the core temperature. Decoherence
when peak load exceeds a coherence threshold theta. Sweep R and p -> the
coherence limit R_max(p).
"""

import sys
from collections import deque
from pathlib import Path

import numpy as np
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))


def ball_graph(R):
    """3D cubic-lattice ball of radius R (nodes with |offset| <= R). Returns
    adjacency + which nodes are on the boundary (can shed to the outside)."""
    nodes = [(x, y, z) for x in range(-R, R + 1) for y in range(-R, R + 1)
             for z in range(-R, R + 1) if x*x + y*y + z*z <= R*R]
    idx = {c: i for i, c in enumerate(nodes)}
    adj = [[] for _ in nodes]
    boundary = np.zeros(len(nodes), dtype=bool)
    for c, i in idx.items():
        deg_inside = 0
        for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            n = (c[0]+d[0], c[1]+d[1], c[2]+d[2])
            if n in idx:
                adj[i].append(idx[n]); deg_inside += 1
        if deg_inside < 6:            # touches the outside -> can shed
            boundary[i] = True
    return adj, boundary


def _M(adj):
    n = len(adj)
    rows, cols, vals = [], [], []
    for i in range(n):
        d = len(adj[i]) or 1
        for j in adj[i]:
            rows.append(i); cols.append(j); vals.append(1.0 / d)
    return sp.csr_matrix((vals, (rows, cols)), shape=(n, n))


def peak_load(adj, boundary, p=1.0, shed=0.5, lam=0.8, iters=3000, M=None):
    """Steady-state peak per-node flux load. Every node produces p; flux
    diffuses; boundary nodes shed fraction `shed` each tick (radiate out)."""
    n = len(adj)
    if M is None:
        M = _M(adj)
    F = np.zeros(n)
    for _ in range(iters):
        F = (1 - lam) * F + lam * (M @ F) + p     # diffuse + produce
        F[boundary] *= (1 - shed)                  # surface sheds to outside
        np.clip(F, 0.0, None, out=F)
    return float(F.max()), float(F.mean())


def main():
    theta = 60.0   # coherence threshold: a node forced to hold > theta decoheres
    print("Peak internal load (core 'temperature') vs pattern radius R. "
          f"Decoherence threshold theta={theta}.")
    print("production p per node/tick, surface sheds 50%/tick.\n")
    print(f"{'R':>4}{'#nodes':>8}{'vol/surf':>9}{'peak load':>11}{'mean':>8}"
          f"   status")
    for R in (1, 2, 3, 4, 5, 6, 8, 10):
        adj, boundary = ball_graph(R)
        pk, mn = peak_load(adj, boundary, p=1.0)
        vs = len(adj) / max(int(boundary.sum()), 1)
        status = "DECOHERES" if pk > theta else "coherent"
        print(f"{R:>4}{len(adj):>8}{vs:>9.2f}{pk:>11.1f}{mn:>8.1f}   {status}")

    print("\n=== coherence limit R_max vs metabolic rate p (higher metabolism "
          "-> smaller max stable size) ===")
    print(f"{'p':>6}{'R_max (last coherent R)':>26}")
    for p in (0.3, 0.5, 1.0, 2.0, 4.0):
        rmax = 0
        for R in range(1, 12):
            adj, boundary = ball_graph(R)
            pk, _ = peak_load(adj, boundary, p=p)
            if pk <= theta:
                rmax = R
            else:
                break
        print(f"{p:>6.1f}{rmax:>26}")

    print("\nReading: peak core load grows with R (volume production ~R^3 vs "
          "surface shedding ~R^2 -> vol/surf ratio climbs), crossing the "
          "coherence threshold at a critical size = a MAXIMUM STABLE PATTERN. "
          "Higher metabolism p -> smaller R_max. This is the framework's "
          "Eddington/Chandrasekhar limit, emergent from surface-shedding vs "
          "volume-production -- a single/simple pattern sheds directly (no "
          "limit); a composite one is bounded by how much its top layers can "
          "channel out before forced re-incorporation decoheres it.")


if __name__ == "__main__":
    main()
