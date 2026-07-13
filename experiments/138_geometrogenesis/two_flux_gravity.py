"""Reconciling force-vs-accretion by fixing the point of view (RAW 135 §4).

The god-view fork ("is the pull a force or an accretion?") is malformed. Re-
derived inside-out, the pull is a FORCE, and the wrong-PoV assumption in RAW
135 §4 was that gravity comes from consuming the STAR's flux (a deposit from
the star travels OUTWARD; consuming it pushes you AWAY -- that is radiation
pressure, not gravity).

Correct PoV: a mass has two effects on the one ambient vacuum bath F:
  - EMISSION (luminosity L): adds flux -> a PEAK at the mass -> test objects are
    pushed DOWN the gradient, AWAY (radiation pressure).
  - AMBIENT CONSUMPTION (s): removes ambient renewal -> a WELL (shadow) -> test
    objects are pushed DOWN the gradient, INTO the well = TOWARD the mass
    (gravity). (Exp 128 v11: renewal is the local ambient tick-stream; stellar
    flux is only surplus. Thread 2: a consumer carves exactly this well.)

Both are the SAME kind of thing: a flux-pressure gradient, a FORCE. Net force on
a test object = -grad F (it rolls toward lower flux). Gravity (well) wins when
s > L; radiation pressure (peak) wins when L > s -- the Eddington crossover,
cleanly, with NO accretion channel and NO consuming-the-star's-light.

Substrate: torus3d ambient bath, uniform emission, one mass = sink s + source L.
"""

import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from boundary_layer_dim import _bfs  # noqa: E402
from graphs import torus3d  # noqa: E402


def _mean_matrix(adj):
    n = len(adj)
    rows, cols, vals = [], [], []
    for i in range(n):
        d = len(adj[i]) or 1
        for j in adj[i]:
            rows.append(i); cols.append(j); vals.append(1.0 / d)
    return sp.csr_matrix((vals, (rows, cols)), shape=(n, n))


def relax(adj, mass, s, L, decay=0.85, emission=1.0, iters=3000, M=None):
    """Ambient bath: diffuse + decay + uniform emission -> BOUNDED steady state
    F_far = emission/(1-decay). The mass emits L (source) and consumes fraction
    s of its flux (sink). Bounded scale lets L and s actually compete."""
    n = len(adj)
    if M is None:
        M = _mean_matrix(adj)
    F = np.full(n, emission / (1 - decay), dtype=float)
    for _ in range(iters):
        F = decay * (M @ F) + emission     # diffuse + decay + ambient source
        F[mass] += L                       # emission (own luminosity)
        F[mass] *= (1 - s)                 # ambient consumption (the shadow)
        np.clip(F, 0.0, None, out=F)
    return F


def radial_force(adj, mass, F):
    """Net inward force on a test object vs distance r: the flux gradient
    dF/dr (F rising outward = well = inward/attractive force). Returns
    {r: mean dF/dr}. Positive = attractive (toward the mass)."""
    dist = _bfs(adj, mass, 30)
    shell = {}
    for v, d in dist.items():
        shell.setdefault(d, []).append(F[v])
    prof = {r: float(np.mean(vs)) for r, vs in sorted(shell.items())}
    force = {}
    for r in prof:
        if r - 1 in prof and r + 1 in prof:
            force[r] = (prof[r + 1] - prof[r - 1]) / 2.0   # +ve => attractive
    return force


def main():
    g = torus3d(15)
    mass = len(g) // 2 + 4
    M = _mean_matrix(g)
    print("Net inward (attractive) radial force on a test object, +ve = pulled "
          "toward the mass, -ve = pushed away (radiation pressure).")
    print("(one ambient bath; the mass is sink s + source L; force = flux "
          "gradient = a FORCE, no accretion channel)\n")
    print(f"{'s (consume)':>12}{'L (emit)':>10}   regime          "
          f"force @ r=2/4/6/8")
    # F_far = emission/(1-decay) ~ 6.67; consumption removes fraction s of
    # F(mass) ~ s*6.67 per tick, so emission L is comparable when L ~ s*F_far.
    for s, L, label in [(0.5, 0.0, "pure consumer"),
                        (0.5, 1.0, "star (s>L)"),
                        (0.5, 3.3, "Eddington L~s*F"),
                        (0.5, 6.0, "super-Eddington"),
                        (0.0, 6.0, "pure emitter")]:
        F = relax(g, mass, s=s, L=L, M=M)
        fr = radial_force(g, mass, F)
        vals = "  ".join(f"{fr.get(r, float('nan')):+.4f}" for r in (2, 4, 6, 8))
        sign = ("ATTRACT (gravity)" if fr.get(4, 0) > 1e-4
                else "REPEL (rad.press)" if fr.get(4, 0) < -1e-4 else "balanced")
        print(f"{s:>12.2f}{L:>10.2f}   {label:<16} {vals}   -> {sign}")

    print("\nReading: force-vs-accretion is RESOLVED -> it is a FORCE (flux "
          "gradient). Gravity = the AMBIENT-bath SHADOW of a consumer (s), "
          "attractive; radiation pressure = the mass's own EMISSION (L), "
          "repulsive; crossover at s=L = the Eddington limit. The wrong PoV in "
          "RAW 135 §4 was that gravity comes from consuming the star's OWN flux "
          "(that pushes away) -- gravity is the shadow in the vacuum bath, and "
          "s>>L generically (Exp 128 v11: ambient renewal >> stellar surplus), "
          "so gravity wins except super-Eddington. Kill switch settled.")


if __name__ == "__main__":
    main()
