#!/usr/bin/env python3
"""
Experiment 132 Phase 5 — Map the horizon explicitly

Phase 4b found the saturated core (r=5 in baseline params) is the
substrate's analogue of an event horizon: where L = rho/rho_scale
approaches 1, gradient direction loses meaning, tangential/radial
separation breaks down. This is exactly Schwarzschild's r_s behavior.

Quantitative test: r_horizon should scale linearly with source strength
(L_STAR or STAR_COUNT), matching Schwarzschild's r_s = 2GM/c^2 ~ M.

Two sweeps:
  1. L_STAR ∈ {0.3, 0.5, 0.7, 1.0, 1.5, 2.0}  (STAR_COUNT=50 fixed)
  2. STAR_COUNT ∈ {25, 50, 100, 200}            (L_STAR=1.0 fixed)

For each variant: re-converge field, measure rho(r) profile, find
r_horizon as the radius where rho(r)/rho_scale crosses thresholds
{0.3, 0.5, 0.7, 0.9}.

Expectation: r_horizon(L_t=0.5) ∝ source_strength, with slope giving
the substrate's analogue of 2G/c^2.

Uses Phase 1 (vanilla, no smoothing) — smoothing affects rates not
rho(r) shape, and we want the cleanest possible field measurement.
"""

import os, sys, time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_anisotropic_field import (
    build_graph, propagate_step, compute_node_gradient, compute_edge_rates,
    BOUNDARY_FRACTION, RHO_SCALE, L_MAX, SPHERE_R, N_NODES,
    N_ITERATIONS, TICKS_PER_ITER, DAMPING, CONVERGE_TOL,
)

L_STAR_VALUES = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
STAR_COUNT_VALUES = [25, 50, 100, 200]
THRESHOLDS = [0.3, 0.5, 0.7, 0.9]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def converge_with(pos, src, dst, edge_dir, edge_len, l_star, star_count):
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
    rate_target, _, _ = compute_edge_rates(rho, grad, src, dst, edge_dir, RHO_SCALE, L_MAX)
    edge_rate = ((1.0 - DAMPING) * edge_rate + DAMPING * rate_target).astype(np.float32)
    total_rate = np.bincount(src, weights=edge_rate, minlength=n_nodes).astype(np.float32)

    interior = ~boundary_mask; interior[star_ids] = False
    m = float(rho[interior].mean())
    rel = abs(m - prev) / max(m, 1e-10)
    if rel < CONVERGE_TOL and it >= 5: break
    prev = m
  return rho, r_of, boundary_mask, star_ids


def find_horizons(rho, r_of, thresholds):
  """For each threshold L_t, find smallest r where L(r) crosses below L_t (going outward)."""
  bin_edges = np.logspace(np.log10(0.3), np.log10(0.9 * SPHERE_R), 60)
  centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
  L_shell = np.zeros(len(centers))
  for i in range(len(centers)):
    m = (r_of >= bin_edges[i]) & (r_of < bin_edges[i + 1])
    if m.sum() > 0:
      L_shell[i] = float(rho[m].mean()) / RHO_SCALE

  horizons = {}
  for L_t in thresholds:
    horizons[L_t] = float('nan')
    for i in range(1, len(centers)):
      if L_shell[i] < L_t and L_shell[i - 1] >= L_t:
        # log-linear interp
        r_lo, L_lo = centers[i - 1], L_shell[i - 1]
        r_hi, L_hi = centers[i], L_shell[i]
        if L_hi == L_lo:
          horizons[L_t] = float(r_lo); break
        frac = (L_t - L_lo) / (L_hi - L_lo)
        log_r = np.log(r_lo) + frac * (np.log(r_hi) - np.log(r_lo))
        horizons[L_t] = float(np.exp(log_r))
        break
  return horizons, centers, L_shell


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


def plot_results(L_results, SC_results):
  fig, axes = plt.subplots(2, 2, figsize=(14, 10))

  ax = axes[0, 0]
  for l_star, _, centers, L_shell in L_results:
    ax.loglog(centers, np.maximum(L_shell, 1e-12), 'o-', ms=3,
              label=f'L_STAR={l_star}')
  for L_t in THRESHOLDS:
    ax.axhline(L_t, color='gray', linestyle=':', alpha=0.4)
  ax.set_xlabel('r'); ax.set_ylabel('L(r) = rho(r)/rho_scale')
  ax.set_title(f'L(r) profile, varying L_STAR (STAR_COUNT=50)')
  ax.legend(fontsize=8); ax.grid(True, which='both', alpha=0.3)

  ax = axes[0, 1]
  for sc, _, centers, L_shell in SC_results:
    ax.loglog(centers, np.maximum(L_shell, 1e-12), 'o-', ms=3,
              label=f'STAR_COUNT={sc}')
  for L_t in THRESHOLDS:
    ax.axhline(L_t, color='gray', linestyle=':', alpha=0.4)
  ax.set_xlabel('r'); ax.set_ylabel('L(r)')
  ax.set_title(f'L(r) profile, varying STAR_COUNT (L_STAR=1.0)')
  ax.legend(fontsize=8); ax.grid(True, which='both', alpha=0.3)

  ax = axes[1, 0]
  for L_t in THRESHOLDS:
    xs = [r[0] for r in L_results]
    ys = [r[1].get(L_t, float('nan')) for r in L_results]
    slope, intercept = linear_fit(xs, ys)
    ax.plot(xs, ys, 'o-', label=f'L_t={L_t}, slope={slope:.2f}')
  ax.set_xlabel('L_STAR'); ax.set_ylabel('r_horizon')
  ax.set_title('r_horizon vs L_STAR (linear fit shown)')
  ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

  ax = axes[1, 1]
  for L_t in THRESHOLDS:
    xs = [r[0] for r in SC_results]
    ys = [r[1].get(L_t, float('nan')) for r in SC_results]
    slope, intercept = loglog_fit(xs, ys)
    ax.loglog(xs, ys, 'o-', label=f'L_t={L_t}, log-slope={slope:.2f}')
  ax.set_xlabel('STAR_COUNT'); ax.set_ylabel('r_horizon')
  ax.set_title('r_horizon vs STAR_COUNT (log-log slope shown)')
  ax.legend(fontsize=8); ax.grid(True, which='both', alpha=0.3)

  plt.suptitle('Exp 132 Phase 5: horizon mapping', fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase5_horizon_mapping.png')
  plt.savefig(path, dpi=130); plt.close()
  print(f"\nSaved: {path}")


def report(L_results, SC_results):
  print("\n" + "=" * 70)
  print("L_STAR SWEEP RESULTS (STAR_COUNT=50 fixed)")
  print("=" * 70)
  print(f"  {'L_STAR':>7}  " + "  ".join([f'r_h(L={L_t})' for L_t in THRESHOLDS]))
  for l_star, hor, _, _ in L_results:
    row = "  ".join([f'{hor.get(L_t, float("nan")):>10.3f}' for L_t in THRESHOLDS])
    print(f"  {l_star:>7.2f}  {row}")

  print("\n  Linear fit: r_horizon = slope * L_STAR + intercept")
  for L_t in THRESHOLDS:
    xs = [r[0] for r in L_results]
    ys = [r[1].get(L_t, float('nan')) for r in L_results]
    slope, intercept = linear_fit(xs, ys)
    print(f"    L_t={L_t}: slope={slope:.4f}  intercept={intercept:.4f}")

  print("\n" + "=" * 70)
  print("STAR_COUNT SWEEP RESULTS (L_STAR=1.0 fixed)")
  print("=" * 70)
  print(f"  {'STAR_C':>7}  " + "  ".join([f'r_h(L={L_t})' for L_t in THRESHOLDS]))
  for sc, hor, _, _ in SC_results:
    row = "  ".join([f'{hor.get(L_t, float("nan")):>10.3f}' for L_t in THRESHOLDS])
    print(f"  {sc:>7d}  {row}")

  print("\n  Log-log fit: r_horizon ~ STAR_COUNT^slope")
  for L_t in THRESHOLDS:
    xs = [r[0] for r in SC_results]
    ys = [r[1].get(L_t, float('nan')) for r in SC_results]
    slope, intercept = loglog_fit(xs, ys)
    print(f"    L_t={L_t}: log-slope={slope:.4f}  (Newton/Schwarz expects ~1.0)")


def run():
  print("Phase 5: horizon mapping")
  print(f"  L_STAR sweep:    {L_STAR_VALUES}")
  print(f"  STAR_COUNT sweep: {STAR_COUNT_VALUES}")
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
                                             l_star, 50)
    horizons, centers, L_shell = find_horizons(rho, r_of, THRESHOLDS)
    print(f"  ({time.time()-t0:.1f}s)  horizons = " +
          ", ".join([f"L={L_t}: r={horizons.get(L_t, float('nan')):.3f}"
                     for L_t in THRESHOLDS]))
    L_results.append((l_star, horizons, centers, L_shell))
    sys.stdout.flush()

  SC_results = []
  for sc in STAR_COUNT_VALUES:
    print(f"=== STAR_COUNT={sc} L_STAR=1.0 ===")
    t0 = time.time()
    rho, r_of, bm, star_ids = converge_with(pos, src, dst, edge_dir, edge_len,
                                             1.0, sc)
    horizons, centers, L_shell = find_horizons(rho, r_of, THRESHOLDS)
    print(f"  ({time.time()-t0:.1f}s)  horizons = " +
          ", ".join([f"L={L_t}: r={horizons.get(L_t, float('nan')):.3f}"
                     for L_t in THRESHOLDS]))
    SC_results.append((sc, horizons, centers, L_shell))
    sys.stdout.flush()

  report(L_results, SC_results)
  plot_results(L_results, SC_results)


if __name__ == '__main__':
  run()
