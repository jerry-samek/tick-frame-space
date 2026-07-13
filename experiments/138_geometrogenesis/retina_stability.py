"""Question 1 (RAW 137 §9.2): does an observer's emergent lag-chart STABILIZE,
and only for a low-dimensional substrate? Plus a touch of Q3 (do two observers
build the SAME universe or private ones?).

No field. Observer = a bundle of taps in a pipe network. Deposits flood from
sources; each tap reads its LAG (path length = graph distance) to each source.
The observer's CHART = the tap x tap correlation of lag-vectors, built up as it
integrates more sources over time. We ask:

  M1 convergence: does perceived dimension (PR rank of the chart) settle as the
     observer integrates more sources?
  M2 drift: does the chart stop changing — ||C(2n) - C(n)||_F / ||C(n)||_F -> 0?
  M3 agreement: do independent observers at different locations read the SAME
     dimension (one shared universe) or scatter (each its own)?

Hypothesis: on a low-d substrate the chart converges fast, drift -> 0, and
observers agree (a shared, stable universe crystallizes). On an expander the
chart never settles (high drift), and observers scatter (no shared universe).
"""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from graphs import random_regular, torus2d, torus3d  # noqa: E402
from boundary_layer_dim import _bfs, _pr, honeycomb, hypercube, small_world  # noqa: E402


def _lag_matrix(adj, taps, srcs):
    L = np.zeros((len(taps), len(srcs)))
    for i, t in enumerate(taps):
        dt = _bfs(adj, t, 30)
        for j, s in enumerate(srcs):
            L[i, j] = dt.get(s, 30)
    return L


def _chart(adj, taps, srcs):
    L = _lag_matrix(adj, taps, srcs)
    keep = np.std(L, axis=1) > 1e-9
    L = L[keep]
    if len(L) < 3:
        return None
    return np.nan_to_num(np.corrcoef(L))


def observer(adj, center, n_taps=24, tap_radius=3):
    ball = sorted(_bfs(adj, center, tap_radius).keys())
    return ball[:n_taps] if len(ball) >= n_taps else ball


def stability_curve(adj, center, seed, stages=(10, 25, 50, 100, 200, 400)):
    """Perceived dim + drift as the observer integrates more sources."""
    rng = np.random.default_rng(seed)
    n = len(adj)
    taps = observer(adj, center)
    dims, drifts, prev = [], [], None
    for m in stages:
        srcs = sorted(int(x) for x in rng.choice(n, min(m, n), replace=False))
        C = _chart(adj, taps, srcs)
        if C is None:
            dims.append(float("nan")); drifts.append(float("nan")); continue
        dims.append(_pr(np.linalg.eigvalsh(C)))
        if prev is not None and prev.shape == C.shape:
            drifts.append(float(np.linalg.norm(C - prev) / (np.linalg.norm(prev) + 1e-9)))
        else:
            drifts.append(float("nan"))
        prev = C
    return dims, drifts


def main():
    cases = [
        ("torus2d(24)", "manifold-2", torus2d(24)),
        ("torus3d(11)", "manifold-3", torus3d(11)),
        ("honeycomb(30)", "manifold-2", honeycomb(30)),
        ("hypercube(10)", "non(d=10)", hypercube(10)),
        ("small_world .1", "expander", small_world(2000, 6, 0.1, 0)),
        ("random_reg 4", "expander", random_regular(2000, 4, np.random.default_rng(0))),
    ]
    stages = (10, 25, 50, 100, 200, 400)
    print("=== M1/M2: single-observer chart convergence (dim @ stages) + final drift ===")
    print(f"{'graph':<16}{'truth':<14}dim @ " + "/".join(str(s) for s in stages)
          + "   final_drift")
    for name, truth, g in cases:
        rng = np.random.default_rng(7)
        c0 = int(rng.integers(len(g)))
        dims, drifts = stability_curve(g, c0, seed=1, stages=stages)
        print(f"{name:<16}{truth:<14}" + "/".join(f"{d:.1f}" for d in dims)
              + f"   {drifts[-1]:.3f}")

    print("\n=== M3: agreement across 8 independent observer locations "
          "(dim mean +/- sd, @400 sources) ===")
    for name, truth, g in cases:
        rng = np.random.default_rng(3)
        vals = []
        for _ in range(8):
            c = int(rng.integers(len(g)))
            srcs = sorted(int(x) for x in
                          np.random.default_rng(c).choice(len(g),
                                                          min(400, len(g)), replace=False))
            C = _chart(g, observer(g, c), srcs)
            if C is not None:
                vals.append(_pr(np.linalg.eigvalsh(C)))
        m, s = float(np.mean(vals)), float(np.std(vals))
        verdict = "AGREE" if s < 0.25 * m else "SCATTER"
        print(f"  {name:<16}{truth:<14} dim = {m:.2f} +/- {s:.2f}   [{verdict}]")


if __name__ == "__main__":
    main()
