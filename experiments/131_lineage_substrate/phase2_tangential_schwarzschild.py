#!/usr/bin/env python3
"""
Experiment 131 - Phase 2: Tangential Schwarzschild on a Lineage Tree

Phase 1 earned rho(r) ~ 1/r on the lineage tree (slope -0.99 +/- 0.16 across
three seeds). Experiment 128 Phase 5 already showed that when rho(r) has 1/r
form, the formula

    gamma = sqrt(1 - L_grav - L_vel)
    where L_grav = rho(r) / rho_scale
          L_vel  = v^2 / c^2

IS the exact Schwarzschild proper-time formula for tangential (circular)
observers -- not a weak-field approximation, the exact formula.

Phase 2 confirms this transfers to the tree substrate by:
  1. Running the Phase 1 tree once to extract rho(r).
  2. Fitting rho(r) = A/r in the mid-range.
  3. Calibrating rho_scale so that the effective Schwarzschild radius
     r_s_eff = A/rho_scale = 1 (natural units).
  4. Computing gamma_substrate at each (r, v_tangential) on a grid.
  5. Comparing to gamma_Schwarzschild_tangential = sqrt(1 - r_s_eff/r - v^2).

Success criterion: machine-precision agreement in the fit range.

This is a transfer check, not a new physical claim. If it passes, Phase 5 of
Exp 128 transfers to the tree substrate at zero cost. If it fails, rho(r)'s
shape on the tree is not clean enough, and Phase 1 needs to be revisited.
"""

import os
import sys
import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_newton_from_tree import (
    build_tree, get_descendants, bin_rho_by_r,
    prepare_neighbor_counts, propagate_step,
    BRANCHING, DEPTH, R_ROOT, SCALE, STAR_DEPTH, BOUNDARY_FRACTION,
)

SEED = 42
N_TICKS = 8000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def run_tree_and_measure_rho():
  pos, parent, level = build_tree(SEED)
  N = len(pos)

  depth_nodes = np.where(level == STAR_DEPTH)[0]
  dists = np.linalg.norm(pos[depth_nodes], axis=1)
  order = np.argsort(dists)
  star_root = depth_nodes[order[len(order) // 2]]
  star_mask = get_descendants(parent, level, star_root)
  star_pos = pos[star_mask].mean(axis=0)
  r_of = np.linalg.norm(pos - star_pos, axis=1)
  r_max = float(r_of.max())

  boundary_mask = (r_of > BOUNDARY_FRACTION * r_max) & ~star_mask
  print(f"  tree: N={N}, star_subtree={int(star_mask.sum())}, "
        f"boundary={int(boundary_mask.sum())}, R_max={r_max:.2f}")

  rho = np.zeros(N, dtype=np.float32)
  rho[star_mask] = 1.0
  neighbor_count, valid = prepare_neighbor_counts(parent)

  t0 = time.time()
  for tick in range(1, N_TICKS + 1):
    rho = propagate_step(rho, parent, valid, neighbor_count,
                         star_mask, 1.0, boundary_mask)
    if tick % 2000 == 0:
      interior = ~(star_mask | boundary_mask)
      print(f"    t={tick}  mean_rho={float(rho[interior].mean()):.6f}")
      sys.stdout.flush()
  print(f"  propagated {N_TICKS} ticks in {time.time() - t0:.1f}s")

  centers, mean, _ = bin_rho_by_r(rho, r_of, r_min=0.3, r_max=1.2 * r_max,
                                  skip_mask=(star_mask | boundary_mask))
  return centers, mean, r_max


def fit_A_over_r(centers, mean_rho, r_lo, r_hi):
  """Fit rho = A/r in the range [r_lo, r_hi]. Returns A."""
  m = (centers >= r_lo) & (centers <= r_hi) & (mean_rho > 0)
  if m.sum() < 4:
    return float('nan'), float('nan')
  # rho = A/r  =>  log(rho) = log(A) - log(r)
  # Constrain slope to -1 exactly, fit only A:
  log_A = float(np.mean(np.log(mean_rho[m]) + np.log(centers[m])))
  A = float(np.exp(log_A))
  # Also do unconstrained fit for diagnostic
  slope, logc = np.polyfit(np.log(centers[m]), np.log(mean_rho[m]), 1)
  return A, float(slope)


def run():
  print("-- Running Phase 1 propagation (single seed) --")
  centers, mean, r_max = run_tree_and_measure_rho()

  # Fit rho = A/r in mid-range (avoid innermost & near-boundary)
  r_lo = 1.0
  r_hi = 0.4 * r_max
  A, slope_free = fit_A_over_r(centers, mean, r_lo, r_hi)
  print(f"\n-- rho(r) fit --")
  print(f"  fit range      [{r_lo:.2f}, {r_hi:.2f}]")
  print(f"  free-slope fit slope = {slope_free:+.3f}  (target -1.0)")
  print(f"  constrained A/r: A = {A:.4f}")

  # Calibrate rho_scale so r_s_eff = A / rho_scale = 1.0 (natural units)
  r_s_eff = 1.0
  rho_scale = A / r_s_eff
  print(f"\n-- calibration --")
  print(f"  rho_scale chosen so r_s_eff = {r_s_eff}")
  print(f"  rho_scale = {rho_scale:.4f}")

  # Build L_grav(r) on the tree: interpolate binned rho
  def L_grav_tree(r):
    return np.interp(r, centers, mean, left=mean[0], right=0.0) / rho_scale

  def L_grav_schwarz(r):
    return r_s_eff / np.maximum(r, 1e-9)

  # Test grid
  r_vals = np.array([1.5, 2.0, 3.0, 5.0, 8.0, 12.0])
  v_vals = np.array([0.0, 0.1, 0.3, 0.5, 0.7])

  print(f"\n-- gamma comparison (tangential) --")
  print(f"  {'r':>5} {'v_tan':>6} {'L_tree':>8} {'L_schw':>8} "
        f"{'gamma_sub':>10} {'gamma_sch':>10} {'abs_err':>10}")
  print("  " + "-" * 65)
  all_rows = []
  for r in r_vals:
    Lt = float(L_grav_tree(r))
    Ls = float(L_grav_schwarz(r))
    for v in v_vals:
      # Substrate gamma using MEASURED rho
      g_sub_sq = 1.0 - Lt - v * v
      g_sub = float(np.sqrt(max(0.0, g_sub_sq)))
      # Schwarzschild tangential exact
      g_sch_sq = 1.0 - Ls - v * v
      g_sch = float(np.sqrt(max(0.0, g_sch_sq)))
      abs_err = abs(g_sub - g_sch)
      print(f"  {r:>5.1f} {v:>6.2f} {Lt:>8.4f} {Ls:>8.4f} "
            f"{g_sub:>10.5f} {g_sch:>10.5f} {abs_err:>10.2e}")
      all_rows.append((r, v, Lt, Ls, g_sub, g_sch, abs_err))

  # Global stats on fit-range points (exclude r < r_lo and r > r_hi)
  in_range = [(r, v, Lt, Ls, gs, gc, e) for (r, v, Lt, Ls, gs, gc, e) in all_rows
              if r_lo <= r <= r_hi]
  if in_range:
    errs = [row[6] for row in in_range if np.isfinite(row[6])]
    print()
    print(f"  in fit range [{r_lo}, {r_hi}]:  "
          f"max |gamma_sub - gamma_sch| = {max(errs):.2e}, "
          f"mean = {np.mean(errs):.2e}")

  # ── Plots ─────────────────────────────────────────────────────────
  fig, axes = plt.subplots(1, 2, figsize=(14, 5))

  # A: L_grav(r) — measured vs Schwarzschild 1/r
  ax = axes[0]
  r_fine = np.linspace(0.5, r_max, 200)
  L_tree_fine = np.array([L_grav_tree(rr) for rr in r_fine])
  L_schw_fine = np.array([L_grav_schwarz(rr) for rr in r_fine])
  ax.loglog(r_fine, L_tree_fine, 'k-', lw=1.4, label='L_grav(r) from tree (measured)')
  ax.loglog(r_fine, L_schw_fine, 'r--', lw=1.2,
            label=f'L_grav = r_s/r (target, r_s={r_s_eff})')
  ax.axvspan(r_lo, r_hi, color='gray', alpha=0.12, label=f'fit range')
  ax.set_xlabel('r'); ax.set_ylabel('L_grav')
  ax.set_title('A: L_grav(r) on tree vs Schwarzschild 1/r')
  ax.grid(True, which='both', alpha=0.3); ax.legend(fontsize=8)

  # B: gamma vs v_tangential at each r, tree (solid) vs Schwarzschild (dashed)
  ax = axes[1]
  r_plot = [1.5, 2.0, 3.0, 5.0, 8.0, 12.0]
  colors = plt.cm.viridis(np.linspace(0, 1, len(r_plot)))
  v_fine = np.linspace(0, 0.9, 30)
  for r, c in zip(r_plot, colors):
    Lt = float(L_grav_tree(r))
    Ls = float(L_grav_schwarz(r))
    g_sub = np.sqrt(np.maximum(0, 1 - Lt - v_fine ** 2))
    g_sch = np.sqrt(np.maximum(0, 1 - Ls - v_fine ** 2))
    ax.plot(v_fine, g_sub, '-', color=c, lw=1.2, label=f'tree r={r}')
    ax.plot(v_fine, g_sch, '--', color=c, lw=0.8, alpha=0.7)
  ax.set_xlabel('v_tangential / c')
  ax.set_ylabel('gamma (proper-time rate)')
  ax.set_title('B: gamma vs v_tan | solid=tree, dashed=Schwarzschild')
  ax.grid(True, alpha=0.3); ax.legend(fontsize=7, ncol=2)

  plt.suptitle(f'Exp 131 Phase 2: tangential Schwarzschild on lineage tree '
               f'(seed={SEED})', fontsize=12)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase2_tangential.png')
  plt.savefig(path, dpi=140)
  plt.close()
  print(f"\n  saved: {path}")


if __name__ == '__main__':
  run()
