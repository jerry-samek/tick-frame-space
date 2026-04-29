#!/usr/bin/env python3
"""
Experiment 132 Phase 2b — Threshold-filter on radial-edge selection

Phase 2 used cos^2-weighted average over ALL edges in a shell to compute
s²_eff. In strong-field inner shells, that average diluted the anisotropy
because most edges aren't radial. Question: if we restrict to genuinely
radial edges (cos^2θ > T for some threshold T), does s²_eff recover the
1/(1−L) target?

Sweep T ∈ {0.0, 0.5, 0.7, 0.9}. T=0.0 reproduces Phase 2's all-edge
cos^2-weighted average. T=0.7 takes only edges within ~33° of radial.
T=0.9 takes only edges within ~18° of radial.

If a high-T threshold recovers s²_eff ≈ 1/(1−L) in inner shells, the
per-edge rule is correctly imposing the right factor and the Phase 2
miss was purely about how the radial-walker projection averages over
graph edges. If even T=0.9 falls short, the per-edge rule itself isn't
delivering 1/(1−L) at the radial endpoint and needs revision.
"""

import os, sys, time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_anisotropic_field import (
    BOUNDARY_FRACTION, RHO_SCALE, L_MAX, STAR_COUNT, SPHERE_R,
)
from phase2_radial_motion import (
    converge_field, gamma_substrate, gamma_schwarz_radial, gamma_naive,
    TEST_R, TEST_V, SHELL_HALFWIDTH,
)

THRESHOLDS = [0.0, 0.5, 0.7, 0.9]   # 0.0 = original (cos^2-weighted, no filter)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def measure_with_threshold(state, test_r, threshold):
  pos, src, dst, rho, edge_rate, cos2_e, L_e, edge_dir, star_ids, boundary_mask = state
  r_of = np.linalg.norm(pos, axis=1)
  interior = ~boundary_mask; interior[star_ids] = False
  edge_r = np.linalg.norm((pos[src] + pos[dst]) * 0.5, axis=1)
  edge_in = interior[src] & interior[dst]
  stretch2 = (1.0 / np.maximum(edge_rate, 1e-10)) ** 2

  results = []
  for r in test_r:
    rlo = r * (1.0 - SHELL_HALFWIDTH)
    rhi = r * (1.0 + SHELL_HALFWIDTH)
    node_mask = (r_of >= rlo) & (r_of < rhi) & interior
    edge_mask = (edge_r >= rlo) & (edge_r < rhi) & edge_in

    L_shell = float((rho[node_mask] / RHO_SCALE).mean()) if node_mask.sum() > 0 else float('nan')
    L_shell = min(L_shell, L_MAX)

    if threshold <= 0.0:
      # Phase 2 original: cos^2-weighted average over all edges in shell
      cos2_sub = cos2_e[edge_mask]
      s2_sub = stretch2[edge_mask]
      sum_w = float(cos2_sub.sum())
      s2_eff = float((cos2_sub * s2_sub).sum() / max(sum_w, 1e-10))
      n_used = int(edge_mask.sum())
    else:
      # Filter: only edges with cos^2 >= threshold, take simple mean of stretch²
      filt = edge_mask & (cos2_e >= threshold)
      n_used = int(filt.sum())
      if n_used == 0:
        s2_eff = float('nan')
      else:
        s2_eff = float(stretch2[filt].mean())

    results.append(dict(r=r, L=L_shell, s2_eff=s2_eff,
                        threshold=threshold, n_used=n_used))
  return results


def report(results, threshold):
  print(f"\n=== Threshold = {threshold} "
        f"({'cos^2-weighted, all edges' if threshold == 0 else f'edges with cos^2 >= {threshold}'}) ===")
  print(f"  {'r':>5}  {'L':>7}  {'s2_eff':>8}  {'1/(1-L)':>9}  "
        f"{'ratio':>7}  {'n_used':>7}")
  for d in results:
    if not np.isnan(d['s2_eff']):
      target = 1.0 / max(1.0 - d['L'], 1e-10)
      ratio = d['s2_eff'] / target
      print(f"  {d['r']:>5.2f}  {d['L']:>7.4f}  {d['s2_eff']:>8.4f}  "
            f"{target:>9.4f}  {ratio:>7.4f}  {d['n_used']:>7d}")
    else:
      print(f"  {d['r']:>5.2f}  {d['L']:>7.4f}      NaN              "
            f"  ----   {d['n_used']:>7d}")


def gamma_grid(results):
  rows = []
  for d in results:
    if np.isnan(d['s2_eff']): continue
    L = d['L']; s2 = d['s2_eff']
    for v in TEST_V:
      gs = float(gamma_substrate(L, v, s2))
      gsch = float(gamma_schwarz_radial(L, v))
      gn = float(gamma_naive(L, v))
      err_sub = abs(gs - gsch) / max(gsch, 1e-10) if gsch > 0 else float('nan')
      err_n = abs(gn - gsch) / max(gsch, 1e-10) if gsch > 0 else float('nan')
      rows.append((d['r'], v, gs, gsch, gn, err_sub, err_n))
  return rows


def aggregate(rows, threshold):
  errs_sub = [r[5] for r in rows if np.isfinite(r[5])]
  errs_n = [r[6] for r in rows if np.isfinite(r[6])]
  if not errs_sub:
    print(f"  threshold={threshold}: no valid γ comparisons")
    return None, None
  m_sub = float(np.mean(errs_sub))
  mx_sub = float(np.max(errs_sub))
  m_n = float(np.mean(errs_n))
  print(f"  threshold={threshold}: substrate err mean={m_sub:.4f} max={mx_sub:.4f}  "
        f"(naive mean={m_n:.4f})  improv={m_n/max(m_sub,1e-10):.2f}x")
  return m_sub, mx_sub


def plot_thresholds(all_results):
  fig, axes = plt.subplots(1, 2, figsize=(14, 5))

  ax = axes[0]
  for thresh, results in all_results:
    rs, ratios = [], []
    for d in results:
      if not np.isnan(d['s2_eff']):
        target = 1.0 / max(1.0 - d['L'], 1e-10)
        rs.append(d['r']); ratios.append(d['s2_eff'] / target)
    label = (f'cos^2-weighted (T=0)' if thresh == 0
             else f'cos^2 ≥ {thresh}')
    ax.semilogx(rs, ratios, 'o-', label=label)
  ax.axhline(1.0, color='k', linestyle='--', alpha=0.5, label='target ratio = 1.0')
  ax.set_xlabel('r'); ax.set_ylabel('s²_eff / (1/(1−L))')
  ax.set_title('How close to Schwarzschild radial endpoint per shell')
  ax.legend(); ax.grid(True, which='both', alpha=0.3)

  ax = axes[1]
  for thresh, results in all_results:
    rows = gamma_grid(results)
    err_means = []
    err_rs = []
    for r in TEST_R:
      r_errs = [row[5] for row in rows if row[0] == r and np.isfinite(row[5])]
      if r_errs:
        err_rs.append(r); err_means.append(float(np.mean(r_errs)))
    if err_rs:
      label = (f'cos^2-weighted' if thresh == 0
               else f'cos^2 ≥ {thresh}')
      ax.semilogx(err_rs, err_means, 'o-', label=label)
  ax.set_xlabel('r'); ax.set_ylabel('mean γ rel err vs Schwarz (over v)')
  ax.set_title('Substrate-vs-Schwarzschild γ error per shell, by threshold')
  ax.legend(); ax.grid(True, which='both', alpha=0.3)

  plt.suptitle('Exp 132 Phase 2b: threshold-filter sweep on radial-edge selection',
               fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase2b_threshold.png')
  plt.savefig(path, dpi=130); plt.close()
  print(f"\nSaved: {path}")


def run():
  state = converge_field()

  all_results = []
  print("\n" + "=" * 70)
  print("THRESHOLD SWEEP")
  print("=" * 70)
  for thresh in THRESHOLDS:
    results = measure_with_threshold(state, TEST_R, thresh)
    report(results, thresh)
    all_results.append((thresh, results))

  print("\n" + "=" * 70)
  print("AGGREGATE γ-ERROR (substrate vs Schwarzschild) BY THRESHOLD")
  print("=" * 70)
  for thresh, results in all_results:
    rows = gamma_grid(results)
    aggregate(rows, thresh)

  plot_thresholds(all_results)


if __name__ == '__main__':
  run()
