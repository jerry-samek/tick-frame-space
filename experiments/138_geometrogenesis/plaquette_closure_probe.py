"""RAW 136 Addendum A.5/A.7 — PLAQUETTE-CLOSURE PROBE (instrument recon, NOT the P1d).

A.5 asks: under dissipation, do short cycles (plaquette-closing edges) survive
preferentially over long chords (-> crumple) and non-closing branches (-> tree)?
A.7 sharpens: the manifold signature is COMMUTING neighbour-chains -> closing
4-cycles (plaquettes); Gromov: commutativity = finite dimension.

The flooding-lag substrate takes a FIXED graph (it floods flux, it does not
rewire), so the literal survival dynamics are the banked P1d. This script does the
two honest prerequisites:

  PART 1 (instrument calibration, P1c-mandated). Define an inside-out, LOCAL
  plaquette observable Q (a return-statistic an embedded pattern can compute) and
  a per-edge RANGE r_e (shortest cycle through the edge). Calibrate on the zoo,
  INCLUDING the two nulls that broke previous instruments:
    - random 4-regular (locally tree-like) -- the graph on which spectral d_s
      false-positived to ~2.0 (Exp 138 P1c). Q must reject it.
    - honeycomb -- a real 2D manifold whose shortest cycle is 6, not 4. The naive
      4-cycle Q is EXPECTED to false-NEGATIVE here; a girth-aware Q must rescue it.
  If Q cannot separate manifold from tree/expander, the probe is dead on arrival.

  PART 2 (mechanism prerequisite). A flux-driven dissipation rule can only
  preferentially starve long chords if the substrate's FLUX distinguishes them.
  On torus2d + random chords, measure gross edge-flux and edge-CURRENT |dF|
  against edge range r_e, homogeneous and with a consuming mass. Report the SIGN.

PRE-REGISTERED expectations (before running -- do not move):
  P1.Q  torus2d/torus3d/hypercube: Q high (4-cycle tilings).
        binary_tree: Q ~ 0.  random_regular(d=4): Q ~ 0  [KEY null -- reject expander].
        honeycomb: naive-Q ~ 0 (false negative, EXPECTED); girth-Q must lift it > 0.
        torus2d+chords: Q high but < clean torus2d (chords dilute).
  P2    A.5 NEEDS long chords to carry systematically DIFFERENT flux/current than
        plaquette edges (so a rule has purchase). Sign matters:
          - current |dF| LARGER on long chords -> a shed-proportional-to-current
            rule would STARVE them (A.5 sign, mechanism plausible).
          - flux/current INDISTINGUISHABLE by range -> flux is BLIND to plaquettes;
            A.5's flux-driven starving has no purchase (honest negative; the real
            dissipation channel must key on re-convergence, not scalar flux).
          - chords carry MORE gross flux and a delivery/reinforce rule would GROW
            them -> WRONG sign (toward expander) -- the danger case.
"""

import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import torus2d, torus3d, random_regular, binary_tree  # noqa: E402
from boundary_layer_dim import honeycomb, hypercube  # noqa: E402
from flooding_lag_substrate import FloodingLagSubstrate  # noqa: E402


# ---------------------------------------------------------------- observables
def plaquette_Q(adj, sample_nodes, rng, girth_cap=8):
    """Local plaquette-closure ratio, two variants, averaged over sampled nodes.

    naive (4-cycle): from node u, count multiplicity of distance-2 targets; a
      target reached by >=2 distinct 2-paths is a closed 4-cycle (a plaquette).
      Q4 = (# re-converging 2-path pairs) / (# 2-path pairs). Tree -> 0.
    girth: same, but at the node's SHORTEST re-convergence length s in [3..cap]
      (so a hexagonal manifold, whose 2-paths first re-converge at length 6, still
      scores). Qg = fraction of 2-walk endpoints that re-converge at length s_min.
    Returns (Q4_mean, Qg_mean, s_min_median).
    """
    q4s, qgs, smins = [], [], []
    for u in sample_nodes:
        # multiplicity of distance-2 targets (excluding u and direct neighbours)
        nbr = set(adj[u])
        cnt = {}
        for a in adj[u]:
            for w in adj[a]:
                if w != u and w not in nbr:
                    cnt[w] = cnt.get(w, 0) + 1
        if cnt:
            tot = sum(cnt.values())
            reconv = sum(m * (m - 1) // 2 for m in cnt.values())
            pairs = tot * (tot - 1) // 2
            q4s.append(reconv / pairs if pairs else 0.0)
        # girth-aware: shortest re-convergence length s_min via BFS layers
        smin, qg = _girth_reconv(adj, u, girth_cap)
        if smin is not None:
            smins.append(smin)
            qgs.append(qg)
    return (float(np.mean(q4s)) if q4s else 0.0,
            float(np.mean(qgs)) if qgs else 0.0,
            float(np.median(smins)) if smins else float("nan"))


def _girth_reconv(adj, u, cap):
    """Shortest length s at which two distinct shortest-paths from u re-converge
    on a common node (a smallest cycle through u ~ 2s or 2s-1), and the fraction
    of that shell's nodes that are so reached (re-convergence strength)."""
    paths = {u: 1}          # count of distinct shortest paths to each node
    dist = {u: 0}
    q = deque([u])
    while q:
        x = q.popleft()
        if dist[x] >= cap:
            continue
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                paths[y] = paths[x]
                q.append(y)
            elif dist[y] == dist[x] + 1:
                paths[y] += paths[x]
    # smallest shell with any node reached by >1 shortest path
    shells = {}
    for v, d in dist.items():
        if v != u:
            shells.setdefault(d, []).append(paths[v])
    for d in sorted(shells):
        mult = shells[d]
        reconv = sum(1 for m in mult if m > 1)
        if reconv:
            return d, reconv / len(mult)
    return None, 0.0


def edge_range(adj, u, v, cutoff=10):
    """Shortest cycle length through edge (u,v) = 1 + shortest u->v path that does
    NOT use the direct edge. Plaquette edge -> 4; hex manifold edge -> 6; long
    chord -> large; bridge (tree edge) -> None (infinite)."""
    dist = {u: 0}
    q = deque([u])
    while q:
        x = q.popleft()
        if dist[x] >= cutoff:
            continue
        for y in adj[x]:
            if (x == u and y == v) or (x == v and y == u):
                continue
            if y not in dist:
                if y == v:
                    return dist[x] + 2
                dist[y] = dist[x] + 1
                q.append(y)
    return None


def torus2d_plus_chords(L, n_chords, rng):
    """A clean 2D manifold contaminated with random long-range chords."""
    adj = [list(a) for a in torus2d(L)]
    n = len(adj)
    added = 0
    while added < n_chords:
        u, v = int(rng.integers(n)), int(rng.integers(n))
        if u != v and v not in adj[u]:
            adj[u].append(v); adj[v].append(u); added += 1
    return adj


def _spearman_sign(x, y):
    """Spearman rho via ranks (no scipy dependency), returns (rho, n)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    if np.std(rx) < 1e-9 or np.std(ry) < 1e-9:
        return float("nan"), len(x)
    return float(np.corrcoef(rx, ry)[0, 1]), len(x)


# ---------------------------------------------------------------- experiment
def part1_calibration(rng):
    print("=" * 78)
    print("PART 1 -- plaquette observable calibrated on the zoo (P1c null check)")
    print("=" * 78)
    zoo = [
        ("torus2d(30)",       torus2d(30),            "manifold-4cyc", "Q4 high"),
        ("torus3d(11)",       torus3d(11),            "manifold-4cyc", "Q4 high"),
        ("hypercube(10)",     hypercube(10),          "manifold-4cyc", "Q4 high"),
        ("honeycomb(24)",     honeycomb(24),          "manifold-6cyc", "Q4~0, Qg>0"),
        ("binary_tree(11)",   binary_tree(11),        "tree",          "Q4~0, Qg~0"),
        ("random_reg(n,d=4)", random_regular(1600, 4, rng), "EXPANDER-null", "Q4~0"),
        ("torus2d+chords",    torus2d_plus_chords(30, 300, rng), "manifold+chords", "Q4 high,<clean"),
    ]
    print(f"{'graph':<20}{'truth':<16}{'Q4':>8}{'Qg':>8}{'s_min':>7}   expectation")
    for name, g, truth, exp in zoo:
        nodes = sorted(int(x) for x in rng.choice(len(g), min(300, len(g)), replace=False))
        q4, qg, smin = plaquette_Q(g, nodes, rng)
        print(f"{name:<20}{truth:<16}{q4:>8.4f}{qg:>8.3f}{smin:>7.1f}   {exp}")
    print("\nReading: Q4 (4-cycle) should be HIGH on square/cubic/hypercube, ~0 on")
    print("tree AND random-regular (the P1c null -- if Q4~0 here, plaquette-Q")
    print("rejects the expander that spectral d_s could not). honeycomb is the")
    print("honest limitation: Q4~0 (false neg, 6-cycles) but girth-Q (Qg,s_min=3)")
    print("must recover it.\n")


def part2_mechanism(rng):
    print("=" * 78)
    print("PART 2 -- does the substrate FLUX distinguish plaquette edges from chords?")
    print("=" * 78)
    L, n_chords = 30, 300
    adj = torus2d_plus_chords(L, n_chords, rng)
    n = len(adj)
    deg = np.array([len(a) for a in adj])

    # sample edges, classify by range (short cycle vs long chord vs bridge)
    all_edges = [(u, v) for u in range(n) for v in adj[u] if u < v]
    idx = rng.choice(len(all_edges), min(600, len(all_edges)), replace=False)
    edges = [all_edges[i] for i in idx]
    ranges = [edge_range(adj, u, v) for (u, v) in edges]

    def _measure(F):
        gross, curr, rr = [], [], []
        for (u, v), r in zip(edges, ranges):
            if r is None:
                continue
            gross.append(F[u] / deg[u] + F[v] / deg[v])
            curr.append(abs(F[u] - F[v]))
            rr.append(min(r, 20))          # cap infinite-ish for ranking
        return np.array(gross), np.array(curr), np.array(rr)

    short = sum(1 for r in ranges if r is not None and r <= 4)
    longc = sum(1 for r in ranges if r is not None and r >= 8)
    print(f"edge population (sample {len(edges)}): plaquette(r<=4)={short}  "
          f"long-chord(r>=8)={longc}  bridge(inf)={sum(r is None for r in ranges)}")

    for label, mass in [("homogeneous (no mass)", None),
                        ("with consuming mass @ center", n // 2 + L // 2)]:
        sub = FloodingLagSubstrate(adj)
        if mass is not None:
            sub.add_mass(int(mass), s=0.6, L=0.0)
        sub.relax(2000)
        gross, curr, rr = _measure(sub.F)
        rho_g, _ = _spearman_sign(rr, gross)
        rho_c, ncmp = _spearman_sign(rr, curr)
        print(f"\n[{label}]  (n={ncmp} cyclic edges)")
        print(f"   Spearman(range, gross_flux)   = {rho_g:+.3f}")
        print(f"   Spearman(range, current|dF|)  = {rho_c:+.3f}")
        # bucketed means for readability
        for lo, hi, tag in [(3, 4, "plaquette r<=4"), (8, 20, "long-chord r>=8")]:
            m = (rr >= lo) & (rr <= hi)
            if m.any():
                print(f"     {tag:<16} mean gross={gross[m].mean():.4f}  "
                      f"mean |dF|={curr[m].mean():.4f}  (n={int(m.sum())})")

    print("\nReading (pre-registered): A.5 needs long chords to carry a")
    print("SYSTEMATICALLY DIFFERENT (ideally larger current) signal so a")
    print("dissipation rule can preferentially starve them. rho~0 => flux is BLIND")
    print("to plaquette structure and the flux-driven mechanism has no purchase")
    print("(the real dissipation channel must key on RE-CONVERGENCE, not scalar")
    print("flux). Positive rho(range, gross_flux) => chords carry MORE flux (a")
    print("reinforce rule would GROW them -> expander -- the danger sign).")


def main():
    rng = np.random.default_rng(0)
    print("RAW 136 A.5/A.7 plaquette-closure probe -- INSTRUMENT RECON (not P1d).")
    print("Fixed-graph substrate: this prototypes + null-calibrates the instrument")
    print("and tests the flux-distinguishes-plaquettes prerequisite. It does NOT")
    print("run the survival dynamics (that needs the banked edge-rewiring channel).\n")
    part1_calibration(rng)
    part2_mechanism(rng)


if __name__ == "__main__":
    main()
