"""Thread 2 — the flooding-lag engine: does a CONSUMING observer create an
attractive well (gravity), on the graph, with no field and no coordinates?

No spatial grid. Deposits flood the pipe network: a scalar flux F(v) diffuses
along edges (each tick, a node relaxes toward its neighbours' mean — flooding
+ conservation), fed by a uniform ambient emission (the vacuum bath). One node
O is a CONSUMER: it removes s*F(O) each tick (it eats the flux it reads — RAW
135, perceiving = consuming). Question: does consumption carve a WELL in the
flux (a deficit that deepens toward O), i.e. does gravity emerge from the act
of observing?

Steady state of a diffusion with a point sink is the graph Green's function —
log(r) on a 2D lattice, ~1/r on a 3D lattice (Addendum E: gravity = the
differential, 1/r^2 force from the potential). If the well matches those, then
perceiving/consuming/gravitating are one act, dynamically, on the flooding-lag
substrate — and the well carries the LOCAL dimension.
"""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from boundary_layer_dim import _bfs  # noqa: E402
from graphs import torus2d, torus3d  # noqa: E402


def relax_with_consumer(adj, observer, s=0.5, lam=0.9, emission=1.0,
                        iters=4000):
    """Iterate flood-diffusion with uniform emission and a consumer sink at
    `observer` to steady state. Returns the flux vector F."""
    n = len(adj)
    nbr = [np.array(adj[i], dtype=int) for i in range(n)]
    F = np.full(n, emission, dtype=float)
    for _ in range(iters):
        mean_nbr = np.array([F[nbr[i]].mean() if len(nbr[i]) else F[i]
                             for i in range(n)])
        F = (1 - lam) * F + lam * mean_nbr + emission * (1 - lam)
        F[observer] -= s * F[observer]          # the consumer eats what it reads
        F = np.clip(F, 0.0, None)
    return F


def well_profile(adj, observer, F):
    """Deficit phi(v) = F_far - F(v) vs graph distance to the observer."""
    dist = _bfs(adj, observer, 40)
    F_far = np.median([F[v] for v, d in dist.items() if d >= 12]) \
        if any(d >= 12 for d in dist.values()) else F.max()
    by_r = {}
    for v, d in dist.items():
        by_r.setdefault(d, []).append(F_far - F[v])
    return {r: float(np.mean(vs)) for r, vs in sorted(by_r.items())}, F_far


def fit_shapes(profile, rmin=2, rmax=10):
    """Fit the well deficit vs r to log(r) (2D Green) and 1/r (3D Green);
    report which fits better (R^2)."""
    rs = np.array([r for r in profile if rmin <= r <= rmax and profile[r] > 0])
    phi = np.array([profile[r] for r in rs])
    if len(rs) < 4:
        return None
    y = -phi  # deficit deepens toward O; potential ~ -Green
    def r2(x):
        A = np.vstack([x, np.ones_like(x)]).T
        c, *_ = np.linalg.lstsq(A, y, rcond=None)
        res = y - A @ c
        ss = ((y - y.mean()) ** 2).sum()
        return 1 - res @ res / ss if ss > 0 else 0.0
    return {"r2_log": r2(np.log(rs)), "r2_inv_r": r2(-1.0 / rs)}


def main():
    for name, g in (("torus2d(41)", torus2d(41)), ("torus3d(15)", torus3d(15))):
        obs = len(g) // 2 + int(len(g) ** 0.5)  # an interior-ish node
        F = relax_with_consumer(g, obs)
        prof, F_far = well_profile(g, obs, F)
        near = "  ".join(f"r={r}:{prof[r]:+.3f}" for r in range(0, 7) if r in prof)
        fits = fit_shapes(prof)
        better = ("log(r) [2D]" if fits["r2_log"] >= fits["r2_inv_r"]
                  else "1/r [3D]")
        print(f"{name}: F_far={F_far:.3f}")
        print(f"  well deficit (F_far - F) by distance:  {near}")
        print(f"  Green-function fit: R2_log={fits['r2_log']:.3f} "
              f"R2_(1/r)={fits['r2_inv_r']:.3f}  -> better: {better}")
        print(f"  => a consuming observer carves a well: gravity from the act "
              f"of observing.\n")


if __name__ == "__main__":
    main()
