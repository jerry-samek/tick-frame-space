#!/usr/bin/env python3
"""
Experiment 132 Phase 3 — Selective Walker (radial trajectory integration)

Phase 2b showed: at cos^2 > 0.9, per-edge s^2 = 1/(1-L) within 0-4%.
That was a per-edge measurement; the question now is whether a real
walker, advancing one step at a time and picking max-cos^2 (vs r_hat)
each step, actually keeps cos^2 high enough along its path that the
path-integrated gamma matches Schwarzschild radial.

Selective walker rule:
  - Start at the node nearest r_start.
  - Each step: of outgoing edges with positive radial component, pick
    the one with maximum cos^2(edge_dir, r_hat).
  - Record per-step metrics: cos^2_rhat, cos^2_field (used by Phase 1's
    rule), L_edge, stretch^2_edge, edge_len, dr.
  - Stop at r > MAX_R or out of outgoing-radial edges.

Then for each test velocity v, compute path-averaged gamma:
  gamma_walker     = sqrt(1 - <L>_path - v^2 * <s^2>_path)
  gamma_schwarz    = sqrt((1-<L>) - v^2 / (1-<L>))
  gamma_naive      = sqrt((1-<L>) - v^2)

Decisive: if gamma_walker matches gamma_schwarz, the substrate gives
exact Schwarzschild radial along realistic trajectories. If walker
drifts off-radial and gamma_walker falls between substrate and naive,
we'll see exactly where the trajectory deteriorates.
"""

import os, sys, time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_anisotropic_field import (
    BOUNDARY_FRACTION, RHO_SCALE, L_MAX, SPHERE_R,
)
from phase2_radial_motion import converge_field, TEST_V

START_RS = [5.0, 8.0, 12.0, 18.0, 25.0]
MAX_R = 0.70 * SPHERE_R     # stop walking before boundary
MAX_STEPS = 5000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def build_csr(src, dst, n_nodes):
  """CSR adjacency: for node n, outgoing neighbors are
  nbr_dst[offsets[n]:offsets[n+1]] and edge indices nbr_edge[same]."""
  order = np.argsort(src, kind='stable')
  src_sorted = src[order]
  offsets = np.searchsorted(src_sorted, np.arange(n_nodes + 1))
  return offsets.astype(np.int64), dst[order], order.astype(np.int64)


def selective_walker(pos, offsets, nbr_dst, nbr_edge, edge_dir, cos2_e, L_e,
                     edge_rate, start_node, max_r, max_steps):
  path = []
  n = int(start_node)
  for step in range(max_steps):
    r_pos = pos[n]
    r_norm = float(np.linalg.norm(r_pos))
    if r_norm > max_r or r_norm < 1e-6:
      break
    r_hat = (r_pos / r_norm).astype(np.float32)
    e_lo, e_hi = int(offsets[n]), int(offsets[n + 1])
    if e_lo == e_hi:
      break
    nbrs = nbr_dst[e_lo:e_hi]
    edges = nbr_edge[e_lo:e_hi]
    edge_dirs = edge_dir[edges]
    dots = edge_dirs @ r_hat
    cos2_rhat = dots * dots
    outgoing = dots > 0
    if not outgoing.any():
      break
    cos2_pick = np.where(outgoing, cos2_rhat, -1.0)
    best = int(np.argmax(cos2_pick))
    e = int(edges[best])
    m = int(nbrs[best])
    path.append({
        'step': step, 'node': n, 'r': r_norm, 'edge': e,
        'cos2_rhat': float(cos2_rhat[best]),
        'cos2_field': float(cos2_e[e]),
        'L': float(L_e[e]),
        'stretch2': float((1.0 / max(edge_rate[e], 1e-10)) ** 2),
        'edge_len': float(np.linalg.norm(pos[m] - pos[n])),
        'dr': float(np.linalg.norm(pos[m]) - r_norm),
    })
    n = m
  return path


def gamma_substrate(L, v, s2):
  arg = 1.0 - L - v * v * s2
  return np.sqrt(max(arg, 0.0))

def gamma_schwarz_radial(L, v):
  arg = (1.0 - L) - v * v / max(1.0 - L, 1e-10)
  return np.sqrt(max(arg, 0.0))

def gamma_naive(L, v):
  arg = (1.0 - L) - v * v
  return np.sqrt(max(arg, 0.0))


def summarize_path(path):
  if not path:
    return None
  L = np.array([p['L'] for p in path])
  s2 = np.array([p['stretch2'] for p in path])
  c2_rhat = np.array([p['cos2_rhat'] for p in path])
  c2_field = np.array([p['cos2_field'] for p in path])
  rs = np.array([p['r'] for p in path])
  drs = np.array([p['dr'] for p in path])
  edge_len = np.array([p['edge_len'] for p in path])
  return dict(L=L, s2=s2, c2_rhat=c2_rhat, c2_field=c2_field, rs=rs,
              drs=drs, edge_len=edge_len)


def report_walker(label, summary):
  print(f"\n--- {label} ---")
  if summary is None:
    print("  (empty path)"); return None
  L_mean = float(summary['L'].mean())
  s2_mean = float(summary['s2'].mean())
  s2_target = 1.0 / max(1.0 - L_mean, 1e-10)
  c2_rhat_mean = float(summary['c2_rhat'].mean())
  c2_field_mean = float(summary['c2_field'].mean())
  steps = len(summary['L'])
  r_start = float(summary['rs'][0])
  r_end = float(summary['rs'][-1])
  total_dr = float(summary['drs'].sum())
  total_len = float(summary['edge_len'].sum())
  efficiency = total_dr / max(total_len, 1e-10)  # ratio of radial advance to edge length
  print(f"  steps={steps}  r: {r_start:.2f} -> {r_end:.2f}  "
        f"total_dr={total_dr:.2f}  total_len={total_len:.2f}")
  print(f"  <L>={L_mean:.4f}  <s^2>={s2_mean:.4f}  target=1/(1-<L>)={s2_target:.4f}  "
        f"ratio={s2_mean/s2_target:.4f}")
  print(f"  <cos^2 vs rhat>={c2_rhat_mean:.4f}  "
        f"<cos^2 vs field-grad>={c2_field_mean:.4f}  "
        f"radial_efficiency={efficiency:.4f}")
  return dict(L=L_mean, s2=s2_mean, c2_rhat=c2_rhat_mean, steps=steps,
              r_start=r_start, r_end=r_end, target=s2_target,
              ratio=s2_mean/s2_target, efficiency=efficiency)


def gamma_table(path_summaries):
  print("\n=== Walker-path gamma comparison (averaged over path) ===")
  print(f"  {'r0':>5}  {'v':>5}  {'<L>':>7}  {'<s^2>':>7}  "
        f"{'g_walker':>9}  {'g_schw':>8}  {'g_naive':>8}  "
        f"{'err_walk':>9}  {'err_naive':>9}")
  rows = []
  for s in path_summaries:
    if s is None: continue
    L = s['L']; s2 = s['s2']; r0 = s['r_start']
    for v in TEST_V:
      gw = gamma_substrate(L, v, s2)
      gsch = gamma_schwarz_radial(L, v)
      gn = gamma_naive(L, v)
      e_w = abs(gw - gsch) / max(gsch, 1e-10) if gsch > 0 else float('nan')
      e_n = abs(gn - gsch) / max(gsch, 1e-10) if gsch > 0 else float('nan')
      print(f"  {r0:>5.1f}  {v:>5.2f}  {L:>7.4f}  {s2:>7.4f}  "
            f"{gw:>9.4f}  {gsch:>8.4f}  {gn:>8.4f}  "
            f"{e_w:>9.4f}  {e_n:>9.4f}")
      rows.append((r0, v, L, s2, gw, gsch, gn, e_w, e_n))
  errs_w = [r[7] for r in rows if np.isfinite(r[7])]
  errs_n = [r[8] for r in rows if np.isfinite(r[8])]
  if errs_w:
    print(f"\n  walker vs Schwarz: mean={np.mean(errs_w):.4f}  max={np.max(errs_w):.4f}")
    print(f"  naive  vs Schwarz: mean={np.mean(errs_n):.4f}  max={np.max(errs_n):.4f}")
    print(f"  improvement (mean): {np.mean(errs_n)/max(np.mean(errs_w),1e-10):.2f}x")
  return rows


def plot(path_summaries, paths_by_r0, rows):
  fig, axes = plt.subplots(2, 2, figsize=(14, 10))

  # (0,0) cos^2_rhat along each path (step index)
  ax = axes[0, 0]
  for r0, path in paths_by_r0.items():
    if not path: continue
    s = summarize_path(path)
    ax.plot(np.arange(len(s['c2_rhat'])), s['c2_rhat'], label=f'r0={r0:.0f}',
            alpha=0.7, lw=1)
  ax.axhline(0.9, color='k', linestyle=':', alpha=0.5, label='Phase2b T=0.9')
  ax.axhline(1/3, color='gray', linestyle=':', alpha=0.4, label='isotropic 1/3')
  ax.set_xlabel('walker step'); ax.set_ylabel('cos^2 (edge vs r_hat)')
  ax.set_title('walker alignment along path')
  ax.set_ylim(0, 1.05); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

  # (0,1) s^2 along path vs target 1/(1-L) at each step
  ax = axes[0, 1]
  for r0, path in paths_by_r0.items():
    if not path: continue
    s = summarize_path(path)
    target = 1.0 / np.maximum(1.0 - s['L'], 1e-10)
    ax.plot(s['rs'], s['s2'], 'o-', ms=2, label=f'r0={r0:.0f} measured', alpha=0.6)
    ax.plot(s['rs'], target, '--', alpha=0.5, label=f'r0={r0:.0f} target')
  ax.set_xlabel('r at step'); ax.set_ylabel('s^2 (per-step)')
  ax.set_title('per-step stretch^2 vs 1/(1-L)')
  ax.legend(fontsize=7, ncol=2); ax.grid(True, which='both', alpha=0.3)
  ax.set_yscale('log'); ax.set_xscale('log')

  # (1,0) per-r0 ratio <s^2>_path / target
  ax = axes[1, 0]
  rs = []; ratios = []
  for s in path_summaries:
    if s is None: continue
    rs.append(s['r_start']); ratios.append(s['ratio'])
  ax.plot(rs, ratios, 'o-')
  ax.axhline(1.0, color='k', linestyle='--', alpha=0.5, label='target=1.0')
  ax.set_xlabel('r0'); ax.set_ylabel('<s^2>_path / (1/(1-<L>))')
  ax.set_title('Path-integrated stretch² vs Schwarzschild target')
  ax.legend(); ax.grid(True, alpha=0.3); ax.set_ylim(0, 1.5)

  # (1,1) gamma error per r0 (substrate vs naive)
  ax = axes[1, 1]
  arr = np.array(rows)
  for r0 in START_RS:
    rmask = arr[:, 0] == r0
    if rmask.sum() == 0: continue
    vs = arr[rmask, 1]
    e_w = arr[rmask, 7]
    e_n = arr[rmask, 8]
    ax.plot(vs, e_w, 'o-', label=f'r0={r0:.0f} walker')
    ax.plot(vs, e_n, 'x--', alpha=0.4, label=f'r0={r0:.0f} naive')
  ax.set_xlabel('v/c'); ax.set_ylabel('rel err vs Schwarzschild')
  ax.set_title('walker vs naive gamma error')
  ax.legend(fontsize=6, ncol=2); ax.grid(True, alpha=0.3)

  plt.suptitle('Exp 132 Phase 3: selective-walker radial trajectories', fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase3_selective_walker.png')
  plt.savefig(path, dpi=130); plt.close()
  print(f"\nSaved: {path}")


def run():
  state = converge_field()
  pos, src, dst, rho, edge_rate, cos2_e, L_e, edge_dir, star_ids, boundary_mask = state
  r_of = np.linalg.norm(pos, axis=1)
  print(f"\n=== Building CSR adjacency ===")
  t0 = time.time()
  offsets, nbr_dst, nbr_edge = build_csr(src, dst, len(pos))
  print(f"  built in {time.time()-t0:.2f}s")

  print("\n=== Walking selective trajectories ===")
  paths_by_r0 = {}
  summaries = []
  for r0 in START_RS:
    # Find a starting node near r0 with multiple outgoing radial edges
    candidates = np.argsort(np.abs(r_of - r0))[:20]
    start = int(candidates[0])
    actual_r = float(r_of[start])
    print(f"\n  r0={r0:.1f}  start_node={start}  actual_r={actual_r:.3f}")
    path = selective_walker(pos, offsets, nbr_dst, nbr_edge, edge_dir,
                            cos2_e, L_e, edge_rate, start, MAX_R, MAX_STEPS)
    paths_by_r0[r0] = path
    s = summarize_path(path)
    summaries.append(report_walker(f"r0={r0:.1f}", s))

  rows = gamma_table(summaries)
  plot(summaries, paths_by_r0, rows)


if __name__ == '__main__':
  run()
