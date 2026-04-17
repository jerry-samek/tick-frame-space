#!/usr/bin/env python3
"""
Experiment 128 v11 — Arrival Rig, Phase 1: Star Only

Honest measurement of deposit propagation on a 3D random geometric graph.
No planet, no consumption, no tangential bias. Just: star emits, graph
propagates, boundary absorbs. Measure the steady-state density and
gradient profile as a function of distance from the star.

The point: check whether the graph substrate alone produces the scaling
we've been assuming in the ODE (density ~ 1/r, gradient ~ 1/r^2).

Model:
  - 3D random geometric graph in a sphere of radius R
  - Star: small cluster at origin, held at density L every tick (source)
  - Propagation: each tick, every node's density redistributes to neighbors
    equally (rho_new[nbr] += rho[node] / degree[node])
  - Boundary: outermost shell is absorbing (rho reset to 0 there)
  - Run until steady state, then measure rho(r) binned by distance
"""

import os
import sys
import time
import numpy as np
from scipy.spatial import cKDTree

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Graph parameters ──
N_NODES = 500_000
SPHERE_R = 80.0
TARGET_K = 24
SEED = 42

# ── Source ──
STAR_COUNT = 50        # "point source" — small cluster near origin
L_STAR = 1.0           # density held at each star node every tick

# ── Boundary ──
BOUNDARY_FRACTION = 0.95  # nodes with r > 0.95 * SPHERE_R are absorbing

# ── Simulation ──
TICKS = 3000
LOG_EVERY = 200
MEASURE_AT = [500, 1000, 2000, 3000]  # snapshot ticks

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def build_graph():
    print(f"Building graph: N={N_NODES}, R={SPHERE_R}, target_k={TARGET_K}")
    sys.stdout.flush()
    rng = np.random.default_rng(SEED)
    t0 = time.time()

    # Uniform points in sphere
    pts = []
    while len(pts) < N_NODES:
        batch = rng.uniform(-SPHERE_R, SPHERE_R, (N_NODES * 2, 3))
        good = batch[np.linalg.norm(batch, axis=1) <= SPHERE_R]
        pts.extend(good.tolist())
    pos = np.array(pts[:N_NODES], dtype=np.float32)

    # Edges via radius query
    rc = SPHERE_R * (TARGET_K / N_NODES) ** (1.0 / 3.0)
    pairs = cKDTree(pos).query_pairs(rc, output_type='ndarray').astype(np.int32)

    # Flat directed-edge arrays for fast propagation:
    # every undirected edge (a,b) becomes two directed edges a->b and b->a
    src = np.concatenate([pairs[:, 0], pairs[:, 1]]).astype(np.int32)
    dst = np.concatenate([pairs[:, 1], pairs[:, 0]]).astype(np.int32)

    degrees = np.bincount(src, minlength=N_NODES).astype(np.int32)
    print(f"  {len(pairs)} edges, avg_k={degrees.mean():.1f}, "
          f"rc={rc:.3f}, build={time.time()-t0:.1f}s")
    return pos, src, dst, degrees


def propagate_step(rho, src, dst, degrees, n_nodes):
    """One tick of isotropic density redistribution to neighbors.

    Each node sends rho[node]/degree[node] to each of its neighbors.
    Vectorized via bincount over flat directed-edge arrays.
    """
    d_safe = np.maximum(degrees, 1)
    per_edge = (rho[src] / d_safe[src]).astype(np.float32)
    return np.bincount(dst, weights=per_edge, minlength=n_nodes).astype(np.float32)


def run():
    pos, src, dst, degrees = build_graph()
    r_of = np.linalg.norm(pos, axis=1)

    # Identify star, boundary, interior
    star_ids = np.argsort(r_of)[:STAR_COUNT]
    boundary_mask = r_of > BOUNDARY_FRACTION * SPHERE_R
    n_boundary = int(boundary_mask.sum())
    print(f"Star: {STAR_COUNT} nodes (r<={r_of[star_ids].max():.2f})")
    print(f"Boundary: {n_boundary} nodes (r>{BOUNDARY_FRACTION*SPHERE_R:.1f})")

    rho = np.zeros(N_NODES, dtype=np.float32)
    rho[star_ids] = L_STAR

    snapshots = {}
    t0 = time.time()
    prev_t = t0
    prev_tick = 0

    for tick in range(1, TICKS + 1):
        rho = propagate_step(rho, src, dst, degrees, N_NODES)
        rho[star_ids] = L_STAR         # source
        rho[boundary_mask] = 0.0       # absorbing boundary

        if tick in MEASURE_AT:
            snapshots[tick] = rho.copy()

        if tick % LOG_EVERY == 0:
            now = time.time()
            tps = (tick - prev_tick) / max(0.001, now - prev_t)
            prev_t = now; prev_tick = tick
            interior = ~boundary_mask
            interior[star_ids] = False
            total = float(rho[interior].sum())
            print(f"  t={tick:5d}  total_interior_rho={total:.2f}  "
                  f"({tps:.0f} t/s)")
            sys.stdout.flush()

    print(f"\nDone: {TICKS} ticks in {time.time()-t0:.1f}s")

    measure_and_plot(pos, r_of, snapshots, star_ids, boundary_mask)


def measure_and_plot(pos, r_of, snapshots, star_ids, boundary_mask):
    interior = ~boundary_mask
    interior[star_ids] = False

    # Radial bins (log-spaced) between 2 and 0.9*SPHERE_R
    r_min, r_max = 2.0, 0.9 * SPHERE_R
    bin_edges = np.logspace(np.log10(r_min), np.log10(r_max), 25)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])

    # "Intermediate range" — away from source and from boundary.
    # Power-law scaling is cleanest here; closer in, point-source resolution
    # matters; closer to boundary, the absorbing BC bends the curve.
    fit_lo = 4.0
    fit_hi = 0.5 * SPHERE_R
    fit_mask = (bin_centers >= fit_lo) & (bin_centers <= fit_hi)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    colors = plt.cm.viridis(np.linspace(0, 1, max(len(snapshots), 1)))

    print(f"\nFit range: [{fit_lo:.1f}, {fit_hi:.1f}]  "
          f"(boundary at {BOUNDARY_FRACTION*SPHERE_R:.1f})")
    print(f"{'tick':>6}  {'slope_rho':>10}  {'slope_grad':>10}  "
          f"{'analytic_R':>12}")
    print("-" * 44)

    for c_idx, (tick, rho) in enumerate(sorted(snapshots.items())):
        mean_rho = np.zeros(len(bin_centers))
        for i in range(len(bin_centers)):
            mask = (r_of >= bin_edges[i]) & (r_of < bin_edges[i+1]) & interior
            if mask.sum() > 0:
                mean_rho[i] = rho[mask].mean()

        # Power-law fit over the intermediate range
        valid = fit_mask & (mean_rho > 0)
        if valid.sum() >= 4:
            slope_rho, _ = np.polyfit(
                np.log(bin_centers[valid]), np.log(mean_rho[valid]), 1)
        else:
            slope_rho = np.nan

        # Finite-difference gradient |d rho / d r|
        with np.errstate(divide='ignore', invalid='ignore'):
            grad = np.abs(np.gradient(mean_rho, bin_centers))
        valid_g = fit_mask & (grad > 0) & np.isfinite(grad)
        if valid_g.sum() >= 4:
            slope_grad, _ = np.polyfit(
                np.log(bin_centers[valid_g]), np.log(grad[valid_g]), 1)
        else:
            slope_grad = np.nan

        # Analytical-form fit: rho(r) = A*(1/r - 1/R_eff)
        # If the graph is effectively 3D, this fits the whole profile.
        # A and R_eff are free; good fit => 3D Poisson behavior confirmed.
        v = mean_rho > 0
        R_fit = np.nan
        if v.sum() >= 6:
            inv_r = 1.0 / bin_centers[v]
            y = mean_rho[v]
            # rho = A*inv_r - A/R  =>  y = A*inv_r + C, with C = -A/R
            A, C = np.polyfit(inv_r, y, 1)
            if A > 0 and C < 0:
                R_fit = -A / C

        print(f"{tick:>6}  {slope_rho:>10.3f}  {slope_grad:>10.3f}  "
              f"{R_fit:>12.2f}")

        axes[0].loglog(bin_centers, mean_rho, 'o-', color=colors[c_idx],
                       label=f't={tick} (slope={slope_rho:.2f})')
        axes[1].loglog(bin_centers, grad, 's-', color=colors[c_idx],
                       label=f't={tick} (slope={slope_grad:.2f})')

    # Reference slope lines anchored on the last snapshot's first valid point
    ref_r = np.array([fit_lo, fit_hi])
    anchor_idx = np.argmax(fit_mask & (mean_rho > 0))
    anchor = (bin_centers[anchor_idx], mean_rho[anchor_idx])
    for ax, p, lbl in [(axes[0], -1, '~1/r'), (axes[1], -2, '~1/r²')]:
        y_anchor = anchor[1] if ax is axes[0] else np.abs(grad[anchor_idx]) if anchor_idx < len(grad) else 1.0
        y_ref = y_anchor * (ref_r / anchor[0]) ** p
        ax.plot(ref_r, y_ref, 'k--', alpha=0.4, lw=1.2, label=f'ref {lbl}')
        ax.axvspan(fit_lo, fit_hi, color='gray', alpha=0.08)
        ax.legend(fontsize=8)
        ax.grid(True, which='both', alpha=0.3)
        ax.set_xlabel('r (distance from star)')

    axes[0].set_ylabel('mean density rho(r)')
    axes[0].set_title('Density profile — expect slope ~ -1 for 3D')
    axes[1].set_ylabel('|d rho / d r|')
    axes[1].set_title('Gradient profile — expect slope ~ -2 for 3D')

    plt.suptitle(f'v11 Phase 1: Star-only propagation '
                 f'(N={N_NODES}, R={SPHERE_R}, k={TARGET_K})')
    plt.tight_layout()
    path = os.path.join(OUT, 'phase1_profile.png')
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\nSaved: {path}")


if __name__ == '__main__':
    run()
