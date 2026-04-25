#!/usr/bin/env python3
"""
Experiment 132 Phase 4b — Smoothed gradient, re-test radial + tangential

Phase 4 found tangential broken in inner shells: walker picked perfectly
tangential-to-r_hat edges (cos^2_rhat ~ 0.002) but the rule fired on
cos^2_field, and noisy gradient in inner shells gave cos^2_field ~ 0.41,
inflating s^2 to 2.16 at r=5.

Fix attempt: smooth the gradient field before using it in the rate
calculation. Each node's gradient becomes (self + neighbors) / (deg+1),
applied N_SMOOTH passes. This averages out high-frequency direction
noise on grad_dir while preserving the bulk radial structure.

Test on the smoothed field:
  1. Tangential walker (Phase 4 logic) — does s^2 drop back toward 1?
  2. Radial walker   (Phase 3 logic) — did smoothing degrade Phase 3?

Sweep N_SMOOTH ∈ {0, 2, 5} to see the trade-off.
"""

import os, sys, time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_anisotropic_field import (
    build_graph, propagate_step, compute_edge_rates,
    BOUNDARY_FRACTION, RHO_SCALE, L_MAX, STAR_COUNT, L_STAR, SPHERE_R,
    N_NODES, N_ITERATIONS, TICKS_PER_ITER, DAMPING, CONVERGE_TOL,
)
from phase2_radial_motion import (
    gamma_substrate, gamma_schwarz_radial, gamma_naive, TEST_V,
)
from phase3_selective_walker import (
    build_csr, selective_walker, summarize_path as summarize_radial,
    MAX_R, MAX_STEPS as MAX_STEPS_RADIAL, START_RS,
)
from phase4_tangential_walker import (
    selective_tangential_walker, summarize_path as summarize_tang,
    gamma_schwarz_tangential, R_TOLERANCE, MAX_STEPS as MAX_STEPS_TANG,
    TARGET_RS,
)

SMOOTH_VARIANTS = [0, 2, 5]   # number of smoothing passes (0 = baseline Phase 4)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def compute_node_gradient_smoothed(rho, src, dst, edge_dir, edge_len, n_nodes,
                                    n_smooth):
  delta = (rho[dst] - rho[src]).astype(np.float32)
  contrib = ((delta / np.maximum(edge_len, 1e-10))[:, None]
             * edge_dir).astype(np.float32)
  grad = np.zeros((n_nodes, 3), dtype=np.float32)
  for d in range(3):
    grad[:, d] = np.bincount(src, weights=contrib[:, d], minlength=n_nodes)
  deg = np.bincount(src, minlength=n_nodes).astype(np.float32)
  grad /= np.maximum(deg, 1.0)[:, None]

  if n_smooth > 0:
    weight = (deg + 1.0)[:, None]
    for _ in range(n_smooth):
      nbr_sum = np.zeros_like(grad)
      for d in range(3):
        nbr_sum[:, d] = np.bincount(src, weights=grad[dst, d], minlength=n_nodes)
      grad = (grad + nbr_sum) / weight
  return grad


def converge_field_smoothed(n_smooth):
  print(f"\n=== Converging field, n_smooth={n_smooth} ===")
  t0 = time.time()
  pos, src, dst, edge_dir, edge_len = build_graph()
  r_of = np.linalg.norm(pos, axis=1)
  star_ids = np.argsort(r_of)[:STAR_COUNT]
  boundary_mask = r_of > BOUNDARY_FRACTION * SPHERE_R

  edge_rate = np.ones(len(src), dtype=np.float32)
  total_rate = np.bincount(src, weights=edge_rate, minlength=N_NODES).astype(np.float32)
  rho = np.zeros(N_NODES, dtype=np.float32); rho[star_ids] = L_STAR

  prev_mean = 0.0
  for it in range(1, N_ITERATIONS + 1):
    for _ in range(TICKS_PER_ITER):
      rho = propagate_step(rho, src, dst, edge_rate, total_rate, N_NODES,
                           star_ids, L_STAR, boundary_mask)
    grad = compute_node_gradient_smoothed(rho, src, dst, edge_dir, edge_len,
                                           N_NODES, n_smooth)
    rate_target, cos2_e, L_e = compute_edge_rates(
        rho, grad, src, dst, edge_dir, RHO_SCALE, L_MAX)
    edge_rate = ((1.0 - DAMPING) * edge_rate + DAMPING * rate_target).astype(np.float32)
    total_rate = np.bincount(src, weights=edge_rate, minlength=N_NODES).astype(np.float32)

    interior = ~boundary_mask; interior[star_ids] = False
    interior_mean = float(rho[interior].mean())
    rel = abs(interior_mean - prev_mean) / max(interior_mean, 1e-10)
    print(f"  iter {it:2d}: mean_rho={interior_mean:.4f}  rel_d={rel:.5f}")
    sys.stdout.flush()
    if rel < CONVERGE_TOL and it >= 5: break
    prev_mean = interior_mean
  print(f"  converged in {time.time()-t0:.1f}s")
  return (pos, src, dst, rho, edge_rate, cos2_e, L_e, edge_dir,
          star_ids, boundary_mask)


def test_radial(state):
  pos, src, dst, rho, edge_rate, cos2_e, L_e, edge_dir, star_ids, bm = state
  r_of = np.linalg.norm(pos, axis=1)
  offsets, nbr_dst, nbr_edge = build_csr(src, dst, len(pos))
  results = []
  for r0 in START_RS:
    start = int(np.argsort(np.abs(r_of - r0))[0])
    path = selective_walker(pos, offsets, nbr_dst, nbr_edge, edge_dir,
                            cos2_e, L_e, edge_rate, start, MAX_R,
                            MAX_STEPS_RADIAL)
    s = summarize_radial(path)
    if s is None:
      results.append(None); continue
    L_mean = float(s['L'].mean()); s2_mean = float(s['s2'].mean())
    target = 1.0 / max(1.0 - L_mean, 1e-10)
    results.append(dict(r0=r0, L=L_mean, s2=s2_mean, target=target,
                         ratio=s2_mean/target,
                         c2_rhat=float(s['c2_rhat'].mean()),
                         steps=len(s['L'])))
  return results


def test_tangential(state):
  pos, src, dst, rho, edge_rate, cos2_e, L_e, edge_dir, star_ids, bm = state
  r_of = np.linalg.norm(pos, axis=1)
  offsets, nbr_dst, nbr_edge = build_csr(src, dst, len(pos))
  results = []
  for r0 in TARGET_RS:
    start = int(np.argsort(np.abs(r_of - r0))[0])
    path = selective_tangential_walker(pos, offsets, nbr_dst, nbr_edge, edge_dir,
                                        cos2_e, L_e, edge_rate, start, r0,
                                        R_TOLERANCE, MAX_STEPS_TANG)
    s = summarize_tang(path)
    if s is None or len(s['L']) == 0:
      results.append(None); continue
    L_mean = float(s['L'].mean()); s2_mean = float(s['s2'].mean())
    results.append(dict(r0=r0, L=L_mean, s2=s2_mean,
                         excess=s2_mean - 1.0,
                         c2_rhat=float(s['c2_rhat'].mean()),
                         c2_field=float(s['c2_field'].mean()),
                         steps=len(s['L'])))
  return results


def report_radial(results, n_smooth):
  print(f"\n--- RADIAL walker  (n_smooth={n_smooth}) ---")
  print(f"  {'r0':>5}  {'steps':>6}  {'<L>':>7}  {'<s^2>':>7}  "
        f"{'target':>7}  {'ratio':>7}  {'<cos2rh>':>9}")
  for d in results:
    if d is None: print("  (empty)"); continue
    print(f"  {d['r0']:>5.1f}  {d['steps']:>6d}  {d['L']:>7.4f}  "
          f"{d['s2']:>7.4f}  {d['target']:>7.4f}  {d['ratio']:>7.4f}  "
          f"{d['c2_rhat']:>9.4f}")
  ratios = [d['ratio'] for d in results if d is not None]
  if ratios:
    print(f"  mean ratio = {np.mean(ratios):.4f}  "
          f"(target 1.0; baseline n_smooth=0 was 0.94-1.10)")


def report_tangential(results, n_smooth):
  print(f"\n--- TANGENTIAL walker  (n_smooth={n_smooth}) ---")
  print(f"  {'r0':>5}  {'steps':>6}  {'<L>':>7}  {'<s^2>':>7}  "
        f"{'excess':>8}  {'<cos2rh>':>9}  {'<cos2fld>':>9}")
  for d in results:
    if d is None: print("  (empty)"); continue
    print(f"  {d['r0']:>5.1f}  {d['steps']:>6d}  {d['L']:>7.4f}  "
          f"{d['s2']:>7.4f}  {d['excess']:>+8.4f}  "
          f"{d['c2_rhat']:>9.4f}  {d['c2_field']:>9.4f}")
  excesses = [d['excess'] for d in results if d is not None]
  if excesses:
    print(f"  mean excess = {np.mean(excesses):+.4f}  max = {max(excesses):+.4f}  "
          f"(target 0.0; Phase 4 baseline mean +0.31 max +1.16)")


def gamma_grid(radial_results, tang_results):
  rows_r = []
  for d in radial_results:
    if d is None: continue
    for v in TEST_V:
      gw = gamma_substrate(d['L'], v, d['s2'])
      gsch = gamma_schwarz_radial(d['L'], v)
      e = abs(gw - gsch) / max(gsch, 1e-10) if gsch > 0 else float('nan')
      rows_r.append((d['r0'], v, gw, gsch, e))
  rows_t = []
  for d in tang_results:
    if d is None: continue
    for v in TEST_V:
      gw = gamma_substrate(d['L'], v, d['s2'])
      gsch = gamma_schwarz_tangential(d['L'], v)
      e = abs(gw - gsch) / max(gsch, 1e-10) if gsch > 0 else float('nan')
      rows_t.append((d['r0'], v, gw, gsch, e))
  err_r = [r[4] for r in rows_r if np.isfinite(r[4])]
  err_t = [r[4] for r in rows_t if np.isfinite(r[4])]
  return rows_r, rows_t, err_r, err_t


def plot_summary(all_runs):
  fig, axes = plt.subplots(2, 2, figsize=(14, 10))

  ax = axes[0, 0]
  for n_smooth, (rad, _) in all_runs.items():
    rs = [d['r0'] for d in rad if d is not None]
    ratios = [d['ratio'] for d in rad if d is not None]
    ax.plot(rs, ratios, 'o-', label=f'n_smooth={n_smooth}')
  ax.axhline(1.0, color='k', linestyle='--', alpha=0.5, label='target')
  ax.set_xlabel('r0'); ax.set_ylabel('<s²>_path / (1/(1-<L>))')
  ax.set_title('RADIAL: path-integrated stretch² ratio')
  ax.legend(); ax.grid(True, alpha=0.3); ax.set_ylim(0, 1.5)

  ax = axes[0, 1]
  for n_smooth, (_, tang) in all_runs.items():
    rs = [d['r0'] for d in tang if d is not None]
    excess = [d['excess'] for d in tang if d is not None]
    ax.plot(rs, excess, 'o-', label=f'n_smooth={n_smooth}')
  ax.axhline(0.0, color='k', linestyle='--', alpha=0.5, label='target')
  ax.set_xlabel('r0'); ax.set_ylabel('<s²>_path − 1.0  (excess)')
  ax.set_title('TANGENTIAL: stretch² excess (lower is better)')
  ax.legend(); ax.grid(True, alpha=0.3)

  ax = axes[1, 0]
  for n_smooth, (rad, tang) in all_runs.items():
    _, _, err_r, err_t = gamma_grid(rad, tang)
    label = f'n={n_smooth}'
    ax.bar([f'rad\n{label}', f'tan\n{label}'],
           [np.mean(err_r) if err_r else 0, np.mean(err_t) if err_t else 0],
           alpha=0.6)
  ax.set_ylabel('mean rel err vs Schwarzschild')
  ax.set_title('Aggregated γ error: radial + tangential by smoothing')
  ax.grid(True, alpha=0.3)

  ax = axes[1, 1]
  for n_smooth, (_, tang) in all_runs.items():
    rs = [d['r0'] for d in tang if d is not None]
    cf = [d['c2_field'] for d in tang if d is not None]
    ax.plot(rs, cf, 'o-', label=f'n_smooth={n_smooth}')
  ax.axhline(0.0, color='k', linestyle='--', alpha=0.5)
  ax.set_xlabel('r0')
  ax.set_ylabel('<cos²_field> on tangential walker path')
  ax.set_title('TANG: gradient-direction noise (lower=cleaner)')
  ax.legend(); ax.grid(True, alpha=0.3)

  plt.suptitle('Exp 132 Phase 4b: smoothed-gradient comparison', fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase4b_smoothed.png')
  plt.savefig(path, dpi=130); plt.close()
  print(f"\nSaved: {path}")


def run():
  all_runs = {}
  for n_smooth in SMOOTH_VARIANTS:
    state = converge_field_smoothed(n_smooth)
    rad = test_radial(state)
    tang = test_tangential(state)
    report_radial(rad, n_smooth)
    report_tangential(tang, n_smooth)
    rows_r, rows_t, err_r, err_t = gamma_grid(rad, tang)
    print(f"\n  >> n_smooth={n_smooth} aggregate gamma error:")
    if err_r: print(f"     RADIAL:     mean={np.mean(err_r):.4f}  max={np.max(err_r):.4f}")
    if err_t: print(f"     TANGENTIAL: mean={np.mean(err_t):.4f}  max={np.max(err_t):.4f}")
    all_runs[n_smooth] = (rad, tang)

  print("\n\n" + "=" * 70)
  print("CROSS-VARIANT SUMMARY")
  print("=" * 70)
  print(f"{'n_smooth':>9}  {'rad ratio':>10}  {'tan excess':>11}  "
        f"{'rad γ-err':>10}  {'tan γ-err':>10}")
  for n_smooth in SMOOTH_VARIANTS:
    rad, tang = all_runs[n_smooth]
    rad_ratio = np.mean([d['ratio'] for d in rad if d is not None])
    tan_excess = np.mean([d['excess'] for d in tang if d is not None])
    _, _, err_r, err_t = gamma_grid(rad, tang)
    er = np.mean(err_r) if err_r else float('nan')
    et = np.mean(err_t) if err_t else float('nan')
    print(f"{n_smooth:>9d}  {rad_ratio:>10.4f}  {tan_excess:>+11.4f}  "
          f"{er:>10.4f}  {et:>10.4f}")
  print("(rad ratio target=1.0, tan excess target=0.0, γ-err target=0.0)")
  plot_summary(all_runs)


if __name__ == '__main__':
  run()
