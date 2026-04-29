#!/usr/bin/env python3
"""
Experiment 132 Phase 2 — Radial Motion vs Schwarzschild

Re-runs Phase 1 to get the converged anisotropic field, then probes
radial proper-time response.

Test setup
----------

The unified tick-budget formula from v11 Phase 5 reads
  gamma = sqrt(1 - L_grav - L_vel)
with L_vel = v^2/c^2 in the original (isotropic) substrate.

In the anisotropic substrate, an edge has stretch s = 1/sqrt(1-L) at
the radial endpoint (Phase 6's diagnosis, imposed in Phase 1's rule).
A walker moving in a particular direction feels the substrate's edge
geometry through the projection cos^2 theta. The natural reading of
"stretched edges cost more velocity budget" is

  L_vel_effective = v^2 * <cos^2 theta * stretch^2> / <cos^2 theta>  / c^2
                  = v^2 * s_eff^2 / c^2

where s_eff^2 is the cos^2-weighted average of stretch^2 over edges in
the shell. For a walker moving radially:
  - cos^2 ~ 1 picks out radial edges; their stretch^2 = 1/(1-L)
  - tangential edges drop out of the average
  - if the substrate carries the diagnosis cleanly through the average,
    s_eff^2 -> 1/(1-L), and gamma matches Schwarzschild radial exactly

Substrate prediction:
  gamma_substrate = sqrt(1 - L - v^2 * s_eff^2 / c^2)

Schwarzschild radial (the target):
  gamma_schwarz   = sqrt((1-L) - v^2 / ((1-L) * c^2))

v11's negative (naive substrate predicts tangential formula for radial):
  gamma_naive     = sqrt((1-L) - v^2/c^2)

Decisive measurement: how close is gamma_substrate to gamma_schwarz vs
gamma_naive across (r, v)? If close to Schwarzschild, the imposed
anisotropy carried through. If close to naive, anisotropy got washed
out by the cos^2 weighting on a discrete graph.
"""

import os, sys, time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Reuse Phase 1 functions and constants
from phase1_anisotropic_field import (
    build_graph, propagate_step, compute_node_gradient, compute_edge_rates,
    N_NODES, SPHERE_R, TARGET_K, STAR_COUNT, L_STAR, BOUNDARY_FRACTION,
    RHO_SCALE, L_MAX, N_ITERATIONS, TICKS_PER_ITER, DAMPING, CONVERGE_TOL,
)

# Test grid (mirrors v11 Phase 6 for direct comparison)
TEST_R = [5.0, 8.0, 12.0, 18.0, 25.0]
TEST_V = [0.0, 0.3, 0.5, 0.7, 0.9]
SHELL_HALFWIDTH = 0.15  # fractional half-width for shell binning around each r

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def converge_field():
  """Re-run Phase 1's iteration to get converged anisotropic field.
  Returns: pos, src, dst, rho, edge_rate, cos2_e, L_e, edge_dir."""
  print("=== Re-running Phase 1 to get converged field ===")
  t0 = time.time()
  pos, src, dst, edge_dir, edge_len = build_graph()
  r_of = np.linalg.norm(pos, axis=1)
  print(f"  graph built in {time.time()-t0:.1f}s, {len(src)} directed edges")

  star_ids = np.argsort(r_of)[:STAR_COUNT]
  boundary_mask = r_of > BOUNDARY_FRACTION * SPHERE_R

  edge_rate = np.ones(len(src), dtype=np.float32)
  total_rate = np.bincount(src, weights=edge_rate, minlength=N_NODES).astype(np.float32)
  rho = np.zeros(N_NODES, dtype=np.float32)
  rho[star_ids] = L_STAR

  prev_mean = 0.0
  for it in range(1, N_ITERATIONS + 1):
    t_iter = time.time()
    for _ in range(TICKS_PER_ITER):
      rho = propagate_step(rho, src, dst, edge_rate, total_rate, N_NODES,
                           star_ids, L_STAR, boundary_mask)
    grad = compute_node_gradient(rho, src, dst, edge_dir, edge_len, N_NODES)
    rate_target, cos2_e, L_e = compute_edge_rates(
        rho, grad, src, dst, edge_dir, RHO_SCALE, L_MAX)
    edge_rate = ((1.0 - DAMPING) * edge_rate + DAMPING * rate_target).astype(np.float32)
    total_rate = np.bincount(src, weights=edge_rate, minlength=N_NODES).astype(np.float32)

    interior = ~boundary_mask; interior[star_ids] = False
    interior_mean = float(rho[interior].mean())
    rel = abs(interior_mean - prev_mean) / max(interior_mean, 1e-10)
    print(f"  iter {it:2d}: mean_rho={interior_mean:.4f}  rel_d={rel:.5f}  "
          f"({time.time()-t_iter:.1f}s)")
    sys.stdout.flush()
    if rel < CONVERGE_TOL and it >= 5:
      print(f"  converged"); break
    prev_mean = interior_mean
  print(f"  converged field in {time.time()-t0:.1f}s\n")
  return (pos, src, dst, rho, edge_rate, cos2_e, L_e, edge_dir,
          star_ids, boundary_mask)


def measure_radial_stretch(pos, src, dst, rho, edge_rate, cos2_e, L_e,
                            star_ids, boundary_mask, test_r):
  """For each test radius, compute:
      L_shell = mean L over interior nodes in the shell
      s2_eff  = cos^2-weighted mean of stretch^2 over edges in the shell
                (the natural radial-projection of the anisotropy)
      cos2_mean = uniform mean of cos^2 (anisotropy strength check)
  """
  r_of = np.linalg.norm(pos, axis=1)
  interior = ~boundary_mask; interior[star_ids] = False
  edge_r = np.linalg.norm((pos[src] + pos[dst]) * 0.5, axis=1)
  edge_in = interior[src] & interior[dst]
  stretch = 1.0 / np.maximum(edge_rate, 1e-10)
  stretch2 = stretch * stretch

  results = []
  for r in test_r:
    rlo = r * (1.0 - SHELL_HALFWIDTH)
    rhi = r * (1.0 + SHELL_HALFWIDTH)
    node_mask = (r_of >= rlo) & (r_of < rhi) & interior
    edge_mask = (edge_r >= rlo) & (edge_r < rhi) & edge_in

    L_shell = float((rho[node_mask] / RHO_SCALE).mean()) if node_mask.sum() > 0 else float('nan')
    L_shell = min(L_shell, L_MAX)

    if edge_mask.sum() == 0:
      results.append(dict(r=r, L=L_shell, s2_eff=float('nan'),
                          cos2_mean=float('nan'), n_edges=0))
      continue
    cos2 = cos2_e[edge_mask]
    s2 = stretch2[edge_mask]
    sum_cos2 = float(cos2.sum())
    s2_eff = float((cos2 * s2).sum() / max(sum_cos2, 1e-10))
    cos2_mean = float(cos2.mean())
    results.append(dict(r=r, L=L_shell, s2_eff=s2_eff, cos2_mean=cos2_mean,
                        n_edges=int(edge_mask.sum())))
  return results


def gamma_substrate(L, v, s2_eff):
  arg = 1.0 - L - v * v * s2_eff
  return np.sqrt(np.maximum(arg, 0.0))

def gamma_schwarz_radial(L, v):
  arg = (1.0 - L) - v * v / max(1.0 - L, 1e-10)
  return np.sqrt(max(arg, 0.0))

def gamma_naive(L, v):
  arg = (1.0 - L) - v * v
  return np.sqrt(max(arg, 0.0))


def report_grid(shell_data):
  print("=== Per-shell anisotropy summary ===")
  print(f"  {'r':>6}  {'L':>7}  {'s2_eff':>8}  {'1/(1-L)':>9}  "
        f"{'<cos2>':>8}  {'n_edges':>8}")
  for d in shell_data:
    if not np.isnan(d['s2_eff']):
      target = 1.0 / max(1.0 - d['L'], 1e-10)
      print(f"  {d['r']:>6.2f}  {d['L']:>7.4f}  {d['s2_eff']:>8.4f}  "
            f"{target:>9.4f}  {d['cos2_mean']:>8.4f}  {d['n_edges']:>8d}")
  print()

  print("=== Gamma comparison (radial motion) ===")
  print(f"  {'r':>5}  {'v':>5}  {'L':>7}  {'gam_sub':>8}  {'gam_schw':>8}  "
        f"{'gam_naive':>9}  {'err_sub':>9}  {'err_naive':>9}")
  rows = []
  for d in shell_data:
    if np.isnan(d['s2_eff']): continue
    L = d['L']
    s2 = d['s2_eff']
    for v in TEST_V:
      gs = float(gamma_substrate(L, v, s2))
      gsch = float(gamma_schwarz_radial(L, v))
      gn = float(gamma_naive(L, v))
      err_sub = abs(gs - gsch) / max(gsch, 1e-10) if gsch > 0 else float('nan')
      err_n = abs(gn - gsch) / max(gsch, 1e-10) if gsch > 0 else float('nan')
      print(f"  {d['r']:>5.1f}  {v:>5.2f}  {L:>7.4f}  {gs:>8.4f}  {gsch:>8.4f}  "
            f"{gn:>9.4f}  {err_sub:>9.4f}  {err_n:>9.4f}")
      rows.append((d['r'], v, L, s2, gs, gsch, gn, err_sub, err_n))
  print()

  errs_sub = [r[7] for r in rows if np.isfinite(r[7]) and r[5] > 0]
  errs_n = [r[8] for r in rows if np.isfinite(r[8]) and r[5] > 0]
  print(f"  rel_err substrate vs Schwarz:  mean={np.mean(errs_sub):.4f}  "
        f"max={np.max(errs_sub):.4f}")
  print(f"  rel_err naive vs Schwarz:      mean={np.mean(errs_n):.4f}  "
        f"max={np.max(errs_n):.4f}")
  print(f"  improvement factor (mean naive / mean substrate): "
        f"{np.mean(errs_n) / max(np.mean(errs_sub), 1e-10):.2f}x")
  return rows


def plot_grid(shell_data, rows):
  # Plot 1: per-shell s2_eff vs target
  fig, axes = plt.subplots(1, 2, figsize=(14, 5))

  ax = axes[0]
  rs = [d['r'] for d in shell_data if not np.isnan(d['s2_eff'])]
  s2 = [d['s2_eff'] for d in shell_data if not np.isnan(d['s2_eff'])]
  Ls = [d['L'] for d in shell_data if not np.isnan(d['s2_eff'])]
  target = [1.0 / max(1.0 - L, 1e-10) for L in Ls]
  ax.semilogx(rs, s2, 'o-', label='measured s²_eff (cos²-weighted)')
  ax.semilogx(rs, target, 'r--', label='target 1/(1−L)')
  ax.set_xlabel('r'); ax.set_ylabel('s²_eff')
  ax.set_title('Radial-projected stretch² per shell')
  ax.legend(); ax.grid(True, which='both', alpha=0.3)

  ax = axes[1]
  arr = np.array(rows)
  for r in TEST_R:
    rmask = arr[:, 0] == r
    if rmask.sum() == 0: continue
    vs = arr[rmask, 1]
    err_sub = arr[rmask, 7]
    err_n = arr[rmask, 8]
    ax.plot(vs, err_sub, 'o-', label=f'r={r} substrate')
    ax.plot(vs, err_n, 'x--', label=f'r={r} naive', alpha=0.5)
  ax.set_xlabel('v/c'); ax.set_ylabel('relative error vs Schwarzschild')
  ax.set_title('γ error: substrate (solid) vs naive (dashed)')
  ax.legend(fontsize=7, ncol=2); ax.grid(True, alpha=0.3)

  plt.suptitle('Exp 132 Phase 2: radial motion vs Schwarzschild', fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase2_radial_motion.png')
  plt.savefig(path, dpi=130); plt.close()
  print(f"\nSaved: {path}")


def run():
  state = converge_field()
  pos, src, dst, rho, edge_rate, cos2_e, L_e, edge_dir, star_ids, boundary_mask = state
  shell_data = measure_radial_stretch(
      pos, src, dst, rho, edge_rate, cos2_e, L_e,
      star_ids, boundary_mask, TEST_R)
  rows = report_grid(shell_data)
  plot_grid(shell_data, rows)


if __name__ == '__main__':
  run()
