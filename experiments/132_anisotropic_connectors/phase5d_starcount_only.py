#!/usr/bin/env python3
"""
Experiment 132 Phase 5d — STAR_COUNT sweep only (phase 5c hung during LSTAR=2.0)

Phase 5c showed the field-only horizon DOES scale with L_STAR (log-log
slope ~0.85 for L_t=0.3). But the STAR_COUNT sweep was cut short by a
hang. This script runs just the STAR_COUNT sweep with a tighter iteration
cap to confirm r_horizon ∝ STAR_COUNT at weak-field thresholds.

If STAR_COUNT also gives slope ~1 at low L_t, r_horizon ∝ M = STAR_COUNT
× L_STAR is earned — Schwarzschild r_s ∝ M recovered.
"""

import os, sys, time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_anisotropic_field import (
    build_graph, propagate_step, compute_node_gradient, compute_edge_rates,
    BOUNDARY_FRACTION, RHO_SCALE, SPHERE_R, N_NODES,
    TICKS_PER_ITER, DAMPING,
)
from phase5c_field_horizon import find_field_horizons, loglog_fit

L_MAX_NEW = 0.99
STAR_COUNT_VALUES = [25, 50, 100, 200]
THRESHOLDS = [0.1, 0.3, 0.5, 0.7, 0.9]
N_ITERATIONS_CAP = 15    # hard cap to avoid hang

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def converge_with(pos, src, dst, edge_dir, edge_len, l_star, star_count, l_max,
                   n_iter_cap):
  n_nodes = len(pos)
  r_of = np.linalg.norm(pos, axis=1)
  star_ids = np.argsort(r_of)[:star_count]
  boundary_mask = r_of > BOUNDARY_FRACTION * SPHERE_R

  edge_rate = np.ones(len(src), dtype=np.float32)
  total_rate = np.bincount(src, weights=edge_rate, minlength=n_nodes).astype(np.float32)
  rho = np.zeros(n_nodes, dtype=np.float32); rho[star_ids] = l_star

  for it in range(1, n_iter_cap + 1):
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
    print(f"    iter {it:2d}: mean_rho={m:.4f}", flush=True)
  return rho, r_of, boundary_mask, star_ids


def run():
  print(f"Phase 5d: STAR_COUNT sweep only, L_STAR=1.0, L_MAX={L_MAX_NEW}, "
        f"N_ITER={N_ITERATIONS_CAP}")
  print()
  print("=== Building graph ===")
  t0 = time.time()
  pos, src, dst, edge_dir, edge_len = build_graph()
  print(f"  built in {time.time()-t0:.1f}s\n")

  results = []
  for sc in STAR_COUNT_VALUES:
    print(f"=== STAR_COUNT={sc} ===")
    t0 = time.time()
    rho, r_of, bm, star_ids = converge_with(pos, src, dst, edge_dir, edge_len,
                                              1.0, sc, L_MAX_NEW, N_ITERATIONS_CAP)
    horizons, centers, L_shell, counts, lmf, cR = find_field_horizons(
        rho, r_of, star_ids, THRESHOLDS)
    print(f"  ({time.time()-t0:.1f}s)  cluster_R={cR:.3f}  L_max_field={lmf:.4f}")
    print(f"    horizons: " +
          ", ".join([f"L={L_t}: r={horizons.get(L_t, float('nan')):.3f}"
                     for L_t in THRESHOLDS]))
    results.append((sc, horizons, centers, L_shell, counts, lmf, cR))
    sys.stdout.flush()

  print("\n" + "=" * 78)
  print(f"STAR_COUNT SWEEP (L_STAR=1.0, field-only, L_MAX={L_MAX_NEW})")
  print("=" * 78)
  print(f"  {'STAR_C':>7}  {'cluster_R':>10}  {'L_max_fld':>10}  " +
        "  ".join([f'r_h(L={L_t})' for L_t in THRESHOLDS]))
  for x, hor, _, _, _, lmf, cR in results:
    row = "  ".join([f'{hor.get(L_t, float("nan")):>10.3f}' for L_t in THRESHOLDS])
    print(f"  {x:>7d}  {cR:>10.3f}  {lmf:>10.4f}  {row}")

  print("\nSTAR_COUNT log-log fit  r_horizon ~ STAR_COUNT^slope")
  for L_t in THRESHOLDS:
    xs = [r[0] for r in results]
    ys = [r[1].get(L_t, float('nan')) for r in results]
    slope, _ = loglog_fit(xs, ys)
    print(f"  L_t={L_t}: log-slope={slope:>8.4f}  (Newton expects ~1.0)")


if __name__ == '__main__':
  run()
