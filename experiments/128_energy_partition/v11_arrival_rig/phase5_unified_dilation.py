#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 5: Unified SR + GR Time Dilation on the Graph

Idea (from today's discussion):
  - A node has a unit tick-budget per tick.
  - Any "load" on the node consumes that budget.
  - Gravity load: fraction of budget spent processing stellar deposits,
    measured directly as rho_local / rho_scale.
  - Velocity load: fraction spent on spatial motion, v^2 / c^2
    (the Pythagorean split that gives Minkowski's square-root form).
  - Total local proper tick rate gamma = sqrt(1 - total_load).

If the two loads simply add under the square root, we should recover
(to leading order in weak field):
    gamma_total = sqrt(1 - 2GM/rc^2 - v^2/c^2)
               ~~ sqrt(1 - 2GM/rc^2) * sqrt(1 - v^2/c^2)
               = gamma_grav * gamma_SR   (Einstein's combined weak field)

This phase tests:
  1. For fixed v = 0, does the graph's rho(r) give gamma_grav(r) that
     tracks Einstein's 1/r weak-field form? (Already shown in Phase 4.)
  2. For fixed r, does velocity v produce the additional
     sqrt(1 - v^2/c^2) factor?
  3. Does the combined (r, v) dependence match Einstein's
     gamma_grav * gamma_SR across a grid?

We reuse the already-propagated rho(r) profile from Phase 4.

NOTE: we do not actually move clocks on the graph. A true "moving
clock" simulation would require the clock to hop node-to-node each
tick at rate v, and its graph-local rho would change along the
trajectory. That is a harder setup. Here we fix position and use v
as an analytical load parameter. The test is whether, for EACH
(r, v) point, the graph's local rho combined with the velocity
load gives the Einstein prediction. This is the "is the unified
load picture self-consistent" check.
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

# Same setup as Phase 4 for continuity
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
    mean_rho = np.zeros(len(centers))
    for i in range(len(centers)):
        m = (r_of >= edges[i]) & (r_of < edges[i+1]) & interior
        if m.sum() > 0:
            mean_rho[i] = rho[m].mean()
    return centers, mean_rho


def run():
    pos, r_of, rho, boundary_mask, star_ids = measure_field()
    bin_centers, mean_rho = bin_rho(r_of, rho, boundary_mask, star_ids)

    # Choose rho_scale so weak-field holds in the fit range
    rho_scale = float(mean_rho.max()) * 2.0

    # Fit rho(r) ~ A/r in the intermediate range
    fit_lo, fit_hi = 4.0, 0.5 * p1.SPHERE_R
    mask = (mean_rho > 0) & (bin_centers >= fit_lo) & (bin_centers <= fit_hi)
    # Solve rho ~ A * (1/r) via linear fit to rho vs 1/r
    inv_r = 1.0 / bin_centers[mask]
    A_fit = float(np.polyfit(inv_r, mean_rho[mask], 1)[0])
    GM_eff = A_fit / rho_scale     # coefficient of 1/r in (1 - gamma_weak)
    print(f"\n  rho_scale = {rho_scale:.3f}")
    print(f"  A_fit     = {A_fit:.3f}  (from rho ~ A/r)")
    print(f"  GM_eff/c^2 = A/rho_scale = {GM_eff:.4f}")

    # Interpolator for rho(r) from binned profile
    def rho_of_r(r):
        return np.interp(r, bin_centers, mean_rho, left=mean_rho[0], right=0.0)

    # Grid of (r, v) to test
    r_vals = np.array([5, 8, 12, 18, 25])
    v_over_c = np.array([0.0, 0.3, 0.5, 0.7, 0.9])

    # Tick-frame prediction (our unified load picture)
    # gamma_tf(r, v) = sqrt(1 - rho(r)/rho_scale - v^2/c^2)
    # Einstein prediction
    # gamma_E(r, v)  = sqrt(1 - 2 GM/(r c^2)) * sqrt(1 - v^2/c^2)
    # Using GM/c^2 = A/(2 rho_scale) so that rho/rho_scale ~ 2 GM/(r c^2) in weak field
    GM_c2 = A_fit / (2 * rho_scale)    # factor 2 so combined form matches

    # For a stationary clock with tangential velocity in Schwarzschild,
    # the EXACT proper-time formula is gamma = sqrt(1 - 2GM/rc^2 - v^2/c^2).
    # That is the ADDITIVE form under the square root, which is what the
    # tick-budget argument gives directly. The MULTIPLICATIVE
    # gamma_grav * gamma_SR is a weak-field approximation that differs
    # from the strict GR answer at the ab cross-term. We report BOTH,
    # but the TF formula IS the strict answer.
    print()
    print(f"{'r':>4} {'v/c':>5} {'L_grav':>8} {'L_vel':>6} "
          f"{'gamma_TF':>9} {'gamma_mult':>10} {'TF-mult':>9}")
    print("  (TF = exact Schwarzschild; mult = weak-field approx)")
    print("-" * 60)

    rows = []
    for r in r_vals:
        rho_r = float(rho_of_r(r))
        L_grav = rho_r / rho_scale
        for v in v_over_c:
            L_vel = v * v
            # Unified tick-frame (exact Schwarzschild for tangential v)
            total = L_grav + L_vel
            gamma_tf = float(np.sqrt(max(0.0, 1.0 - total)))
            # Multiplicative weak-field approximation
            gg = float(np.sqrt(max(0.0, 1.0 - L_grav)))
            gs = float(np.sqrt(max(0.0, 1.0 - L_vel)))
            gamma_mult = gg * gs
            rel_err = abs(gamma_tf - gamma_mult) / max(gamma_mult, 1e-9)
            if total >= 1.0:
                marker = "  PAST STATIC LIMIT"
            else:
                marker = ""
            print(f"{r:>4.1f} {v:>5.2f} {L_grav:>8.4f} {L_vel:>6.3f} "
                  f"{gamma_tf:>9.5f} {gamma_mult:>10.5f} {rel_err:>9.3e}"
                  f"{marker}")
            rows.append((r, v, L_grav, gamma_tf, gamma_mult, rel_err))

    # Analysis summary: where is weak-field approx good?
    rel_errs = np.array([row[5] for row in rows])
    print()
    print(f"  weak-field approximation quality:")
    print(f"    mean   rel-err = {rel_errs.mean():.3e}")
    print(f"    max    rel-err = {rel_errs.max():.3e}")
    print(f"    (this measures how much gamma_grav * gamma_SR DIFFERS")
    print(f"    from the exact additive Schwarzschild form. TF is the")
    print(f"    exact answer.)")

    plot(rows, bin_centers, mean_rho, rho_scale, GM_c2, r_vals, v_over_c,
         GM_eff)


def plot(rows, bin_centers, mean_rho, rho_scale, GM_c2, r_vals, v_over_c,
         GM_eff):
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))

    # Panel A: rho(r) with fit line and the r_vals marked
    ax = axes[0]
    valid = mean_rho > 0
    ax.loglog(bin_centers[valid], mean_rho[valid], 'bo-', ms=3, lw=0.5,
              label='measured rho(r)')
    rr = np.logspace(np.log10(bin_centers[0]), np.log10(bin_centers[-1]), 200)
    ax.loglog(rr, GM_eff * rho_scale / rr, 'k--', lw=1, alpha=0.5,
              label=f'A/r fit')
    for r in r_vals:
        ax.axvline(r, color='r', alpha=0.2, lw=0.8)
    ax.set_xlabel('r'); ax.set_ylabel('rho(r)')
    ax.set_title('v11 graph field (reused)')
    ax.legend(fontsize=8); ax.grid(True, which='both', alpha=0.3)

    # Panel B: gamma_TF vs v, one curve per r
    ax = axes[1]
    colors = plt.cm.viridis(np.linspace(0, 1, len(r_vals)))
    for i, r in enumerate(r_vals):
        sel = [row for row in rows if row[0] == r]
        vs = [row[1] for row in sel]
        g_tf = [row[3] for row in sel]
        g_e = [row[4] for row in sel]
        ax.plot(vs, g_tf, 'o-', color=colors[i], lw=1, ms=4,
                label=f'TF, r={r}')
        ax.plot(vs, g_e, 'x--', color=colors[i], lw=0.8, ms=5, alpha=0.6)
    ax.set_xlabel('v / c'); ax.set_ylabel(r'$\gamma$')
    ax.set_title('gamma(v) at fixed r: TF (solid) vs Einstein (dashed)')
    ax.legend(fontsize=7, ncol=2); ax.grid(True, alpha=0.3)

    # Panel C: relative error in a (r, v) heatmap
    ax = axes[2]
    err_grid = np.zeros((len(r_vals), len(v_over_c)))
    for row in rows:
        i = list(r_vals).index(row[0])
        j = list(v_over_c).index(row[1])
        err_grid[i, j] = row[5]
    im = ax.imshow(err_grid, origin='lower', aspect='auto',
                   extent=[v_over_c[0], v_over_c[-1], r_vals[0], r_vals[-1]],
                   cmap='viridis')
    ax.set_xlabel('v/c'); ax.set_ylabel('r')
    ax.set_title('Relative |gamma_TF - gamma_E| / gamma_E')
    plt.colorbar(im, ax=ax, label='rel err')

    plt.suptitle('Phase 5: unified SR+GR time dilation from tick-budget',
                 fontsize=13)
    plt.tight_layout()
    path = os.path.join(OUT, 'phase5_unified.png')
    plt.savefig(path, dpi=140)
    plt.close()
    print(f"\n  saved: {path}")


if __name__ == '__main__':
    run()
