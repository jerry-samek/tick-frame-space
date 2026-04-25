#!/usr/bin/env python3
"""
Experiment 132 Phase 5c — Horizon mapping, star nodes excluded

Phase 5/5b's "horizon insensitive to STAR_COUNT" was a measurement bug:
shell-averaged L included both held source nodes (always at L_STAR) and
free field nodes; the mix in any given inner shell is roughly constant
across STAR_COUNT because graph packing is uniform, so the shell-mean
L was dominated by local node mix rather than by the field.

Fix: compute L_shell from FIELD NODES ONLY (exclude star_ids). Then the
binned L(r) reflects the propagated field outside the source. Expectation,
re-derived: outside the cluster, rho(r) ≈ A·M/r with M = STAR_COUNT × L_STAR
(total source rate). So r_horizon ∝ M, recovering Schwarzschild scaling.

Also report the cluster outer radius for context (not a horizon, just
the geometric extent of the source). Use L_MAX=0.99 from Phase 5b.
"""

import os, sys, time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_anisotropic_field import (
    build_graph, propagate_step, compute_node_gradient, compute_edge_rates,
    BOUNDARY_FRACTION, RHO_SCALE, SPHERE_R, N_NODES,
    N_ITERATIONS, TICKS_PER_ITER, DAMPING, CONVERGE_TOL,
)

L_MAX_NEW = 0.99
L_STAR_VALUES = [0.5, 1.0, 1.5, 2.0]
STAR_COUNT_VALUES = [25, 50, 100, 200]
THRESHOLDS = [0.1, 0.3, 0.5, 0.7, 0.9]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def converge_with(pos, src, dst, edge_dir, edge_len, l_star, star_count, l_max):
  n_nodes = len(pos)
  r_of = np.linalg.norm(pos, axis=1)
  star_ids = np.argsort(r_of)[:star_count]
  boundary_mask = r_of > BOUNDARY_FRACTION * SPHERE_R

  edge_rate = np.ones(len(src), dtype=np.float32)
  total_rate = np.bincount(src, weights=edge_rate, minlength=n_nodes).astype(np.float32)
  rho = np.zeros(n_nodes, dtype=np.float32); rho[star_ids] = l_star

  prev = 0.0
  for it in range(1, N_ITERATIONS + 1):
    for _ in range(TICKS_PER_ITER):
      rho = propagate_step(rho, src, dst, edge_rate, total_rate, n_nodes,
                           star_ids, l_star, boundary_mask)
    grad = compute_node_gradient(rho, src, dst, edge_dir, edge_len, n_nodes)
    rate_target, _, _ = compute_edge_rates(rho, grad, src, dst, edge_dir,
                                            RHO_SCALE, l_max)
    edge_rate = ((1.0 - DAMPING) * edge_rate + DAMPING * rate_target).astype(np.float32)
    total_rate = np.bincount(src, weights=edge_rate, minlength=n_nodes).astype(np.float32)

    interior = ~boundary_mask; interior[star_ids] = False
    m = float(rho[interior].mean())
    rel = abs(m - prev) / max(m, 1e-10)
    if rel < CONVERGE_TOL and it >= 5: break
    prev = m
  return rho, r_of, boundary_mask, star_ids


def find_field_horizons(rho, r_of, star_ids, thresholds, n_bins=120):
  """L_shell over FIELD nodes only (excluding held source nodes)."""
  n = len(rho)
  star_mask = np.zeros(n, dtype=bool); star_mask[star_ids] = True
  field_mask = ~star_mask
  cluster_max_r = float(r_of[star_ids].max())

  bin_edges = np.logspace(np.log10(1.0), np.log10(0.9 * SPHERE_R), n_bins + 1)
  centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
  L_shell = np.zeros(len(centers))
  counts = np.zeros(len(centers), dtype=int)
  for i in range(len(centers)):
    m = (r_of >= bin_edges[i]) & (r_of < bin_edges[i + 1]) & field_mask
    counts[i] = int(m.sum())
    if counts[i] > 0:
      L_shell[i] = float(rho[m].mean()) / RHO_SCALE
  L_max_field = float(L_shell.max())

  horizons = {}
  for L_t in thresholds:
    horizons[L_t] = float('nan')
    for i in range(1, len(centers)):
      if counts[i] == 0 or counts[i - 1] == 0: continue
      if L_shell[i] < L_t and L_shell[i - 1] >= L_t:
        r_lo, L_lo = centers[i - 1], L_shell[i - 1]
        r_hi, L_hi = centers[i], L_shell[i]
        if L_hi == L_lo:
          horizons[L_t] = float(r_lo); break
        frac = (L_t - L_lo) / (L_hi - L_lo)
        log_r = np.log(r_lo) + frac * (np.log(r_hi) - np.log(r_lo))
        horizons[L_t] = float(np.exp(log_r))
        break
  return horizons, centers, L_shell, counts, L_max_field, cluster_max_r


def linear_fit(xs, ys):
  xs = np.array(xs); ys = np.array(ys)
  m = np.isfinite(ys) & (xs > 0)
  if m.sum() < 2: return float('nan'), float('nan')
  slope, intercept = np.polyfit(xs[m], ys[m], 1)
  return float(slope), float(intercept)


def loglog_fit(xs, ys):
  xs = np.array(xs); ys = np.array(ys)
  m = np.isfinite(ys) & (xs > 0) & (ys > 0)
  if m.sum() < 2: return float('nan'), float('nan')
  slope, intercept = np.polyfit(np.log(xs[m]), np.log(ys[m]), 1)
  return float(slope), float(intercept)


def report_sweep(label, results):
  print("\n" + "=" * 78)
  print(label)
  print("=" * 78)
  print(f"  {'param':>7}  {'cluster_R':>10}  {'L_max_fld':>10}  " +
        "  ".join([f'r_h(L={L_t})' for L_t in THRESHOLDS]))
  for x, hor, _, _, _, lmax_field, cluster_R in results:
    row = "  ".join([f'{hor.get(L_t, float("nan")):>10.3f}' for L_t in THRESHOLDS])
    print(f"  {x:>7.2f}  {cluster_R:>10.3f}  {lmax_field:>10.4f}  {row}")


def report_fits(L_results, SC_results):
  print("\n" + "=" * 78)
  print("SCALING FITS  (testing  r_horizon proportional to source 'mass')")
  print("=" * 78)

  print("\nL_STAR sweep — linear fit  r_horizon = slope * L_STAR + intercept")
  for L_t in THRESHOLDS:
    xs = [r[0] for r in L_results]
    ys = [r[1].get(L_t, float('nan')) for r in L_results]
    slope, intercept = linear_fit(xs, ys)
    print(f"  L_t={L_t}: slope={slope:>8.4f}  intercept={intercept:>8.4f}")

  print("\nL_STAR sweep — log-log fit  r_horizon ~ L_STAR^slope")
  for L_t in THRESHOLDS:
    xs = [r[0] for r in L_results]
    ys = [r[1].get(L_t, float('nan')) for r in L_results]
    slope, _ = loglog_fit(xs, ys)
    print(f"  L_t={L_t}: log-slope={slope:>8.4f}  (Newton expects ~1.0)")

  print("\nSTAR_COUNT sweep — log-log fit  r_horizon ~ STAR_COUNT^slope")
  for L_t in THRESHOLDS:
    xs = [r[0] for r in SC_results]
    ys = [r[1].get(L_t, float('nan')) for r in SC_results]
    slope, _ = loglog_fit(xs, ys)
    print(f"  L_t={L_t}: log-slope={slope:>8.4f}  (Newton expects ~1.0)")


def plot_results(L_results, SC_results):
  fig, axes = plt.subplots(2, 2, figsize=(14, 10))

  ax = axes[0, 0]
  for l_star, _, centers, L_shell, counts, _, cR in L_results:
    valid = counts > 0
    ax.loglog(centers[valid], np.maximum(L_shell[valid], 1e-12), 'o-', ms=3,
              label=f'L_STAR={l_star} (cluster_R={cR:.2f})')
  for L_t in THRESHOLDS:
    ax.axhline(L_t, color='gray', linestyle=':', alpha=0.4)
  ax.set_xlabel('r'); ax.set_ylabel('L(r) over field nodes only')
  ax.set_title('L(r) vs L_STAR (STAR_COUNT=50)')
  ax.legend(fontsize=7); ax.grid(True, which='both', alpha=0.3)

  ax = axes[0, 1]
  for sc, _, centers, L_shell, counts, _, cR in SC_results:
    valid = counts > 0
    ax.loglog(centers[valid], np.maximum(L_shell[valid], 1e-12), 'o-', ms=3,
              label=f'STAR_COUNT={sc} (cluster_R={cR:.2f})')
  for L_t in THRESHOLDS:
    ax.axhline(L_t, color='gray', linestyle=':', alpha=0.4)
  ax.set_xlabel('r'); ax.set_ylabel('L(r) over field nodes only')
  ax.set_title('L(r) vs STAR_COUNT (L_STAR=1.0)')
  ax.legend(fontsize=7); ax.grid(True, which='both', alpha=0.3)

  ax = axes[1, 0]
  for L_t in THRESHOLDS:
    xs = [r[0] for r in L_results]
    ys = [r[1].get(L_t, float('nan')) for r in L_results]
    slope, _ = loglog_fit(xs, ys)
    ax.loglog(xs, ys, 'o-', label=f'L_t={L_t}, log-slope={slope:.2f}')
  ax.set_xlabel('L_STAR'); ax.set_ylabel('r_horizon')
  ax.set_title('r_horizon vs L_STAR  (Newton: slope=1)')
  ax.legend(fontsize=7); ax.grid(True, which='both', alpha=0.3)

  ax = axes[1, 1]
  for L_t in THRESHOLDS:
    xs = [r[0] for r in SC_results]
    ys = [r[1].get(L_t, float('nan')) for r in SC_results]
    slope, _ = loglog_fit(xs, ys)
    ax.loglog(xs, ys, 'o-', label=f'L_t={L_t}, log-slope={slope:.2f}')
  ax.set_xlabel('STAR_COUNT'); ax.set_ylabel('r_horizon')
  ax.set_title('r_horizon vs STAR_COUNT  (Newton: slope=1)')
  ax.legend(fontsize=7); ax.grid(True, which='both', alpha=0.3)

  plt.suptitle(f'Exp 132 Phase 5c: horizon mapping, field nodes only, '
               f'L_MAX={L_MAX_NEW}', fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase5c_field_horizon.png')
  plt.savefig(path, dpi=130); plt.close()
  print(f"\nSaved: {path}")


def run():
  print(f"Phase 5c: horizon mapping (field nodes only, L_MAX={L_MAX_NEW})")
  print()
  print("=== Building graph ===")
  t0 = time.time()
  pos, src, dst, edge_dir, edge_len = build_graph()
  print(f"  built in {time.time()-t0:.1f}s\n")

  L_results = []
  for l_star in L_STAR_VALUES:
    print(f"=== L_STAR={l_star} STAR_COUNT=50 ===")
    t0 = time.time()
    rho, r_of, bm, star_ids = converge_with(pos, src, dst, edge_dir, edge_len,
                                              l_star, 50, L_MAX_NEW)
    horizons, centers, L_shell, counts, lmf, cR = find_field_horizons(
        rho, r_of, star_ids, THRESHOLDS)
    print(f"  ({time.time()-t0:.1f}s)  cluster_R={cR:.3f}  L_max_field={lmf:.4f}")
    print(f"    horizons: " +
          ", ".join([f"L={L_t}: r={horizons.get(L_t, float('nan')):.3f}"
                     for L_t in THRESHOLDS]))
    L_results.append((l_star, horizons, centers, L_shell, counts, lmf, cR))
    sys.stdout.flush()

  SC_results = []
  for sc in STAR_COUNT_VALUES:
    print(f"=== STAR_COUNT={sc} L_STAR=1.0 ===")
    t0 = time.time()
    rho, r_of, bm, star_ids = converge_with(pos, src, dst, edge_dir, edge_len,
                                              1.0, sc, L_MAX_NEW)
    horizons, centers, L_shell, counts, lmf, cR = find_field_horizons(
        rho, r_of, star_ids, THRESHOLDS)
    print(f"  ({time.time()-t0:.1f}s)  cluster_R={cR:.3f}  L_max_field={lmf:.4f}")
    print(f"    horizons: " +
          ", ".join([f"L={L_t}: r={horizons.get(L_t, float('nan')):.3f}"
                     for L_t in THRESHOLDS]))
    SC_results.append((sc, horizons, centers, L_shell, counts, lmf, cR))
    sys.stdout.flush()

  report_sweep("L_STAR SWEEP (STAR_COUNT=50, field-only)", L_results)
  report_sweep("STAR_COUNT SWEEP (L_STAR=1.0, field-only)", SC_results)
  report_fits(L_results, SC_results)
  plot_results(L_results, SC_results)


if __name__ == '__main__':
  run()
