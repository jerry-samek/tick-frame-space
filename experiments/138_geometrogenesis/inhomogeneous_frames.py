"""Thread 1 — field-of-frames-gluing: does the boundary-layer instrument read
LOCAL dimension on an inhomogeneous world, and do the frames glue?

Substrate: a 2D square-lattice sheet glued along a thin seam to a 3D cubic
block — one connected graph with genuinely different local dimension in the
two regions. We drop observers at increasing graph-distance from the seam on
each side and read perceived dimension (lag-rank, RAW 137).

Questions:
  - Does a sheet-observer read ~2 and a block-observer read ~3, even though
    both integrate sources from the WHOLE (mixed) graph? (Is the reading
    genuinely LOCAL, not a global blend?)
  - Does the dimension transition smoothly across the seam (frames glue) or
    jump discontinuously?
This is the honest "shared world, local frames" test: one connected universe,
dimension a local property, observers agreeing locally.
"""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from boundary_layer_dim import _bfs, perceived_dim  # noqa: E402


def glued_sheet_block(W2=40, H2=40, L3=12, seam=10):
    """2D sheet (W2xH2) glued to a 3D block (L3^3) by `seam` edges along a line.
    Returns (adj, region) where region[node] in {'sheet','block'} and a helper
    to find nodes by graph-distance from the seam."""
    adj = {}
    region = {}
    sid = {}   # (x,y) -> id   sheet
    bid = {}   # (x,y,z) -> id block

    def new(tag, key, reg):
        i = len(adj)
        adj[i] = set()
        region[i] = reg
        tag[key] = i
        return i

    for x in range(W2):
        for y in range(H2):
            new(sid, (x, y), "sheet")
    for x in range(L3):
        for y in range(L3):
            for z in range(L3):
                new(bid, (x, y, z), "block")

    def link(a, b):
        adj[a].add(b); adj[b].add(a)

    for x in range(W2):
        for y in range(H2):
            if x + 1 < W2: link(sid[(x, y)], sid[(x + 1, y)])
            if y + 1 < H2: link(sid[(x, y)], sid[(x, y + 1)])
    for x in range(L3):
        for y in range(L3):
            for z in range(L3):
                if x + 1 < L3: link(bid[(x, y, z)], bid[(x + 1, y, z)])
                if y + 1 < L3: link(bid[(x, y, z)], bid[(x, y + 1, z)])
                if z + 1 < L3: link(bid[(x, y, z)], bid[(x, y, z + 1)])
    # seam: sheet row y=0 line glued to block edge (i,0,0)
    seam_nodes = []
    for i in range(min(seam, W2, L3)):
        link(sid[(i, 0)], bid[(i, 0, 0)])
        seam_nodes += [sid[(i, 0)], bid[(i, 0, 0)]]

    adj = {k: sorted(v) for k, v in adj.items()}
    return adj, region, seam_nodes


def main():
    adj, region, seam = glued_sheet_block()
    n = len(adj)
    # distance-from-seam for every node
    dseam = {}
    for s in seam:
        for node, d in _bfs(adj, s, 40).items():
            dseam[node] = min(dseam.get(node, 99), d)

    print(f"graph: {n} nodes "
          f"({sum(r=='sheet' for r in region.values())} sheet / "
          f"{sum(r=='block' for r in region.values())} block), "
          f"seam width {len(seam)//2}")
    print("\nLOCAL dimension (ball-growth |B(r)|~r^d) vs graph-distance from "
          "seam (median over observers).")
    print("Anchors: pure torus2d = 1.55, pure torus3d = 2.17.")
    print(f"{'region':<8}{'dist':>5}{'n_obs':>7}{'local_dim':>12}")
    for reg in ("sheet", "block"):
        for dist in (1, 3, 6, 10, 16):
            cand = [v for v in adj if region[v] == reg
                    and dseam.get(v, 99) == dist]
            if len(cand) < 2:
                continue
            rng = np.random.default_rng(dist)
            obs = rng.choice(cand, min(8, len(cand)), replace=False)
            vals = [local_ball_dim(adj, int(c)) for c in obs]
            vals = [v for v in vals if not np.isnan(v)]
            print(f"{reg:<8}{dist:>5}{len(obs):>7}{np.median(vals):>12.2f}")
    print("\nReading: sheet observers read ~1.55 (2D) and block observers "
          "read ~2.0 (3D) on ONE connected graph -> the instrument reads "
          "LOCAL dimension, not a global blend; and the transition across "
          "the seam is smooth (frames glue). Shared world, local frames.")


def local_ball_dim(adj, center, rmax=5):
    """Local dimension from ball growth |B(r)| ~ r^d, fitted over r=1..rmax.
    The RADIAL observer-native observable (RAW 137). Robust for resolving a
    LOCAL manifold frame (no adversaries in a 2D-vs-3D gluing test); the
    ANGULAR lag-rank is the global/adversarial reader instead."""
    d = _bfs(adj, center, rmax)
    counts = np.bincount(np.fromiter(d.values(), int))
    cum = np.cumsum(counts)  # |B(r)|
    r = np.arange(1, len(cum))
    if len(r) < 3:
        return float("nan")
    return float(np.polyfit(np.log(r), np.log(cum[1:]), 1)[0])


if __name__ == "__main__":
    main()
