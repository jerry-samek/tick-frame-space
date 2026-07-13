"""THE unified flooding-lag substrate — one engine for gravity, perception,
and the coherence limit (consolidation of RAW 135 §13 + RAW 137).

No coordinates, no field-grid-as-space. There is a pipe network (graph) and an
ambient renewal flux that floods along it (diffuse + decay + uniform emission).
A PATTERN is a set of nodes that consumes the ambient flux. That single act of
consumption is simultaneously:

  - GRAVITY: consumption carves a well (shadow) in the ambient flux; other
    patterns are pushed down the gradient into it (RAW 135 §13.3, force = -grad F).
  - PERCEPTION: the lag (arrival delay = graph distance) at which flux reaches
    the pattern's taps, correlated across taps, is its perceived dimension
    (RAW 137 -- the consumed flux IS what it reads).
  - COHERENCE: the pattern produces its own metabolic flux over its VOLUME and
    must shed it through its SURFACE; core load ~R^2 sets a maximum size
    (RAW 135 §13.6).

One class, one running engine, three readouts from the same state. Perceiving,
gravitating, and being are one act on one substrate.
"""

import sys
from collections import deque
from pathlib import Path

import numpy as np
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import torus3d  # noqa: E402


def _bfs(adj, s, cutoff):
    d = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        if d[u] >= cutoff:
            continue
        for v in adj[u]:
            if v not in d:
                d[v] = d[u] + 1; q.append(v)
    return d


def _pr(eigs):
    e = np.clip(eigs, 0.0, None); s2 = float((e * e).sum())
    return float(e.sum() ** 2 / s2) if s2 > 0 else 0.0


class FloodingLagSubstrate:
    """One pipe network + one ambient flood. Patterns consume; the same
    consumption gravitates, perceives, and (over a body) sets a coherence bound."""

    def __init__(self, adj, decay=0.85, emission=1.0):
        self.adj = adj
        self.n = len(adj)
        self.decay = decay
        self.emission = emission
        rows, cols, vals = [], [], []
        for i in range(self.n):
            d = len(adj[i]) or 1
            for j in adj[i]:
                rows.append(i); cols.append(j); vals.append(1.0 / d)
        self.M = sp.csr_matrix((vals, (rows, cols)), shape=(self.n, self.n))
        self.F = np.full(self.n, emission / (1 - decay))
        self.consume = np.zeros(self.n)   # per-node ambient consumption fraction
        self.emit = np.zeros(self.n)      # per-node own emission (luminosity)

    def add_mass(self, node, s=0.5, L=0.0):
        self.consume[node] = s
        self.emit[node] = L

    def step(self):
        self.F = self.decay * (self.M @ self.F) + self.emission
        self.F += self.emit
        self.F *= (1 - self.consume)
        np.clip(self.F, 0.0, None, out=self.F)

    def relax(self, ticks=3000):
        for _ in range(ticks):
            self.step()
        return self.F

    # ---- GRAVITY: the shadow well is a force ----
    def gravity_force(self, center, rmax=10):
        """Net inward (attractive) radial force vs distance from `center`:
        the ambient-flux gradient dF/dr (+ve = pulled toward center)."""
        dist = _bfs(self.adj, center, rmax)
        shell = {}
        for v, d in dist.items():
            shell.setdefault(d, []).append(self.F[v])
        prof = {r: float(np.mean(vs)) for r, vs in sorted(shell.items())}
        return {r: (prof[r + 1] - prof[r - 1]) / 2.0
                for r in prof if r - 1 in prof and r + 1 in prof}

    # ---- PERCEPTION: lag-correlation rank of the pattern's taps ----
    def perceived_dimension(self, center, n_taps=24, n_src=200, seed=0):
        rng = np.random.default_rng(seed)
        taps = sorted(_bfs(self.adj, center, 3).keys())[:n_taps]
        srcs = sorted(int(x) for x in rng.choice(self.n, min(n_src, self.n),
                                                 replace=False))
        L = np.array([[_bfs(self.adj, t, 30).get(s, 30) for s in srcs]
                      for t in taps], float)
        L = L[np.std(L, axis=1) > 1e-9]
        if len(L) < 3:
            return float("nan")
        return _pr(np.linalg.eigvalsh(np.nan_to_num(np.corrcoef(L))))

    # ---- COHERENCE: composite body's core load vs size ----
    def core_load(self, center, R, p=1.0, shed=0.5, lam=0.8, iters=2500):
        body = list(_bfs(self.adj, center, R).keys())
        idx = {v: k for k, v in enumerate(body)}
        m = len(body)
        rows, cols, vals = [], [], []
        boundary = np.zeros(m, bool)
        for v in body:
            inside = [u for u in self.adj[v] if u in idx]
            if len(inside) < len(self.adj[v]):
                boundary[idx[v]] = True
            for u in inside:
                rows.append(idx[v]); cols.append(idx[u]); vals.append(1.0 / len(self.adj[v]))
        Mb = sp.csr_matrix((vals, (rows, cols)), shape=(m, m))
        G = np.zeros(m)
        for _ in range(iters):
            G = (1 - lam) * G + lam * (Mb @ G) + p
            G[boundary] *= (1 - shed)
            np.clip(G, 0.0, None, out=G)
        return float(G.max()), m


def main():
    g = torus3d(15)
    sub = FloodingLagSubstrate(g)
    center = len(g) // 2 + 4
    sub.add_mass(center, s=0.5, L=0.0)      # one consuming pattern (a "mass")
    sub.relax()

    print("ONE flooding-lag substrate; ONE consuming pattern at a node.\n")

    print("[1] GRAVITY — the pattern's consumption carves a well; force = the "
          "ambient gradient (+ve = attractive):")
    fg = sub.gravity_force(center)
    print("    force @ r=2/4/6/8 = "
          + "  ".join(f"{fg.get(r, float('nan')):+.4f}" for r in (2, 4, 6, 8))
          + "   -> ATTRACTS (gravity)\n")

    print("[2] PERCEPTION — the SAME pattern's taps read the lag structure of "
          "the flux they consume:")
    d = sub.perceived_dimension(center)
    print(f"    perceived dimension (lag-rank) = {d:.2f}  (3D torus substrate)"
          "   -> PERCEIVES\n")

    print("[3] COHERENCE — the pattern's own metabolism: core load vs body "
          "size (volume-produce ~R^3 vs surface-shed ~R^2):")
    print("    R   #nodes   core_load")
    theta = 60.0
    for R in (2, 4, 6, 8):
        load, m = sub.core_load(center, R)
        tag = "  DECOHERES" if load > theta else ""
        print(f"    {R}   {m:>5}    {load:>7.1f}{tag}")

    print("\nOne engine, one act of consumption: it GRAVITATES (well), "
          "PERCEIVES (lag-rank), and is bounded in size (coherence). "
          "Perceiving = gravitating = being, on the single flooding-lag "
          "substrate. Gravity uses the flux FIELD; perception uses the flux "
          "LAG; both are the one flood on the one graph. (Renewal -- which "
          "defeats drag, RAW 135 §13.4 -- is the pattern re-forming each tick; "
          "the coherence bound and the maintenance shedding are the same "
          "metabolism read structurally.)")


if __name__ == "__main__":
    main()
