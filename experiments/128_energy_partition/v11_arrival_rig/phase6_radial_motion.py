#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 6: Radial Motion and the Spatial Metric

Phase 5 showed that our tick-budget formula

    gamma = sqrt(1 - L_grav - L_vel)

is the EXACT Schwarzschild proper-time formula for tangential motion.
Phase 6 asks the same question for RADIAL motion, where Schwarzschild
has an extra factor on the spatial term:

    dtau/dt = sqrt((1 - L_grav) - v^2/(c^2 (1 - L_grav)))   [radial]

versus

    dtau/dt = sqrt((1 - L_grav) - v^2/c^2)                  [tangential]

The radial formula differs because the Schwarzschild spatial metric
has  g_rr = 1/(1 - L_grav) — radial distances are STRETCHED near a
mass, so radial motion consumes more budget per coordinate distance
than tangential does.

Our v11 graph is a uniform 3D random geometric graph. Connectors
have roughly the same length regardless of direction. There's no
radial-vs-tangential anisotropy built in. So the naive tick-frame
formula gives the same answer for radial and tangential velocities,
and matches GR only in the tangential case.

This phase:
  1. Computes three gammas at each (r, v) point:
       gamma_naive   = sqrt(1 - L_grav - v^2/c^2)
       gamma_corr    = sqrt(1 - L_grav - v^2/(c^2(1 - L_grav)))
       gamma_schwarz = sqrt((1 - L_grav)^2 - v^2/c^2) / sqrt(1 - L_grav)
     The second and third are algebraically identical and equal the
     Schwarzschild radial formula. The first is our naive v11 result.
  2. Shows how large the discrepancy is (naive vs Schwarzschild radial)
     across (r, v).
  3. Documents what structural feature the substrate would need to
     produce the extra 1/(1-L_grav) factor — namely, radial anisotropy
     of the connector graph near the source.
"""

import os
import sys
import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_star_only import build_graph, propagate_step
import phase1_star_only as p1

p1.N_NODES = 100_000
p1.SPHERE_R = 60.0
p1.TARGET_K = 24
p1.STAR_COUNT = 50
p1.L_STAR = 1.0
p1.BOUNDARY_FRACTION = 0.95
p1.SEED = 42

PROP_TICKS = 2000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def measure_field():
    print("-- Phase 1 propagation (reused) --")
    pos, src, dst, degrees = build_graph()
    r_of = np.linalg.norm(pos, axis=1)
    star_ids = np.argsort(r_of)[:p1.STAR_COUNT]
    boundary_mask = r_of > p1.BOUNDARY_FRACTION * p1.SPHERE_R

    rho = np.zeros(p1.N_NODES, dtype=np.float32)
    rho[star_ids] = p1.L_STAR

    t0 = time.time()
    for tick in range(1, PROP_TICKS + 1):
        rho = propagate_step(rho, src, dst, degrees, p1.N_NODES)
        rho[star_ids] = p1.L_STAR
        rho[boundary_mask] = 0.0
        if tick % 500 == 0:
            interior = ~boundary_mask; interior[star_ids] = False
            print(f"  t={tick}  total={float(rho[interior].sum()):.1f}")
            sys.stdout.flush()
    print(f"  propagation: {time.time() - t0:.1f}s")
    return pos, r_of, rho, boundary_mask, star_ids


def bin_rho(r_of, rho, boundary_mask, star_ids):
    interior = ~boundary_mask; interior[star_ids] = False
    edges = np.logspace(np.log10(2.0),
                        np.log10(p1.BOUNDARY_FRACTION * p1.SPHERE_R), 40)
    centers = np.sqrt(edges[:-1] * edges[1:])
    mean = np.zeros(len(centers))
    for i in range(len(centers)):
        m = (r_of >= edges[i]) & (r_of < edges[i+1]) & interior
        if m.sum() > 0:
            mean[i] = rho[m].mean()
    return centers, mean


def measure_connector_anisotropy(pos, r_of, degrees, star_ids):
    """Empirical check: do the graph's connectors show radial/tangential
    anisotropy near the source? If yes, the naive model might
    partially reproduce the Schwarzschild radial factor already."""
    # For each node, look at its neighbors and compute fraction of
    # edge vectors that are radial vs tangential, relative to origin.
    # A pure uniform RGG would give 1/3 radial (cos^2(theta) averaged
    # over 3D sphere, theta is angle between edge and radial direction).
    # If near-source edges are MORE radial, that would induce the
    # stretching naturally.
    print("\n-- Measuring graph connector anisotropy --")
    print("  (uniform RGG expects <cos^2(theta_radial)> = 1/3 everywhere)")

    # We'd need the edge arrays; easier: reconstruct for a sample of nodes
    # using their positions and nearest-neighbor structure
    from scipy.spatial import cKDTree
    tree = cKDTree(pos)
    rc = p1.SPHERE_R * (p1.TARGET_K / p1.N_NODES) ** (1.0 / 3.0)

    # Sample in radial shells
    shells = [(3.0, 6.0), (8.0, 12.0), (15.0, 20.0), (25.0, 35.0)]
    print(f"  {'shell':<14} {'nodes':>8} {'<cos^2 theta>':>14}")
    print("  " + "-" * 40)
    for r_lo, r_hi in shells:
        mask = (r_of >= r_lo) & (r_of < r_hi)
        node_idx = np.where(mask)[0][:200]   # sample 200 nodes in shell
        if len(node_idx) == 0:
            continue
        cos2s = []
        for i in node_idx:
            if r_of[i] < 0.01:
                continue
            r_hat = pos[i] / r_of[i]
            nbrs = tree.query_ball_point(pos[i], rc)
            for j in nbrs:
                if j == i:
                    continue
                d = pos[j] - pos[i]
                dn = np.linalg.norm(d)
                if dn < 1e-9:
                    continue
                e_hat = d / dn
                cos2s.append(float(np.dot(e_hat, r_hat)) ** 2)
        mean_cos2 = np.mean(cos2s) if cos2s else 0.0
        label = f"r=[{r_lo:.0f},{r_hi:.0f}]"
        print(f"  {label:<14} {len(node_idx):>8} {mean_cos2:>14.4f}")


def run():
    pos, r_of, rho, boundary_mask, star_ids = measure_field()
    bin_centers, mean_rho = bin_rho(r_of, rho, boundary_mask, star_ids)

    rho_scale = float(mean_rho.max()) * 2.0

    def rho_of_r(r):
        return np.interp(r, bin_centers, mean_rho, left=mean_rho[0], right=0.0)

    r_vals = np.array([5, 8, 12, 18, 25])
    v_over_c = np.array([0.0, 0.3, 0.5, 0.7, 0.9])

    print()
    print("-- Radial motion: three gammas compared --")
    print(f"  rho_scale = {rho_scale:.3f}")
    print()
    print(f"{'r':>4} {'v/c':>5} {'L_grav':>8} "
          f"{'naive':>9} {'schwarz':>9} {'naive-sch':>11}")
    print("  (naive = our v11 model; schwarz = GR radial answer)")
    print("-" * 58)

    rows = []
    for r in r_vals:
        L_grav = float(rho_of_r(r)) / rho_scale
        for v in v_over_c:
            # Naive tick-frame (same as tangential)
            naive_sq = 1.0 - L_grav - v * v
            gamma_naive = float(np.sqrt(max(0.0, naive_sq)))
            # Schwarzschild radial
            inner = (1.0 - L_grav) ** 2 - v * v
            if inner < 0 or (1.0 - L_grav) <= 0:
                gamma_sch = 0.0
            else:
                gamma_sch = float(np.sqrt(inner) / np.sqrt(1.0 - L_grav))
            rel_err = (abs(gamma_naive - gamma_sch)
                       / max(gamma_sch, 1e-9)
                       if gamma_sch > 0 else float('nan'))
            print(f"{r:>4.1f} {v:>5.2f} {L_grav:>8.4f} "
                  f"{gamma_naive:>9.5f} {gamma_sch:>9.5f} {rel_err:>11.3e}")
            rows.append((r, v, L_grav, gamma_naive, gamma_sch, rel_err))

    print()
    print("-- Analysis --")
    # How far off in weak field and strong field
    for label, (r, v) in [("weak (r=25, v=0.3)", (25, 0.3)),
                           ("moderate (r=12, v=0.5)", (12, 0.5)),
                           ("strong (r=8, v=0.6)", (8, 0.6))]:
        L = float(rho_of_r(r)) / rho_scale
        gamma_naive = float(np.sqrt(max(0, 1 - L - v*v)))
        inner = (1-L)**2 - v*v
        gamma_sch = float(np.sqrt(max(0,inner)) / np.sqrt(max(1e-9, 1-L)))
        if gamma_sch > 1e-9:
            rel = abs(gamma_naive - gamma_sch) / gamma_sch
            print(f"  {label}: naive={gamma_naive:.4f}, "
                  f"schwarz={gamma_sch:.4f}, rel-err={rel:.3e}")
        else:
            print(f"  {label}: naive={gamma_naive:.4f}, "
                  f"schwarz~0 (past radial horizon -- naive fails to capture it)")

    measure_connector_anisotropy(pos, r_of, None, star_ids)

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = plt.cm.viridis(np.linspace(0, 1, len(r_vals)))

    # Panel A: gamma vs v/c, naive and schwarz overlaid
    ax = axes[0]
    for i, r in enumerate(r_vals):
        sel = [row for row in rows if row[0] == r]
        vs = [row[1] for row in sel]
        gn = [row[3] for row in sel]
        gs = [row[4] for row in sel]
        ax.plot(vs, gn, 'o-', color=colors[i], lw=1, ms=4,
                label=f'naive r={r}')
        ax.plot(vs, gs, 'x--', color=colors[i], lw=0.8, ms=5, alpha=0.6)
    ax.set_xlabel('v / c (radial)'); ax.set_ylabel(r'$\gamma$')
    ax.set_title('Radial motion: naive TF (solid) vs Schwarzschild (dashed)')
    ax.legend(fontsize=7, ncol=2); ax.grid(True, alpha=0.3)

    # Panel B: relative error heatmap
    ax = axes[1]
    err = np.zeros((len(r_vals), len(v_over_c)))
    for row in rows:
        i = list(r_vals).index(row[0])
        j = list(v_over_c).index(row[1])
        err[i, j] = row[5] if np.isfinite(row[5]) else 0.0
    im = ax.imshow(err, origin='lower', aspect='auto',
                   extent=[v_over_c[0], v_over_c[-1], r_vals[0], r_vals[-1]],
                   cmap='viridis')
    ax.set_xlabel('v/c (radial)'); ax.set_ylabel('r')
    ax.set_title('|gamma_naive - gamma_schwarz| / gamma_schwarz')
    plt.colorbar(im, ax=ax, label='rel err')

    plt.suptitle('Phase 6: radial motion test -- where the naive model fails',
                 fontsize=12)
    plt.tight_layout()
    path = os.path.join(OUT, 'phase6_radial.png')
    plt.savefig(path, dpi=140)
    plt.close()
    print(f"\n  saved: {path}")


if __name__ == '__main__':
    run()
