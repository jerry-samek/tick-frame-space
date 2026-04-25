#!/usr/bin/env python3
"""
Experiment 132 Phase 4 — Tangential Walker (does Phase 5 survive anisotropy?)

v11 Phase 5 earned EXACT Schwarzschild tangential proper time on the
isotropic substrate:
  gamma_tang_schw = sqrt((1-L) - v^2/c^2)
The unified tick-budget formula matched it identically.

Phase 1 turned on anisotropy. We need to verify the tangential result
survives. Per the rule:
  stretch^2(edge) = cos^2 * 1/(1-L) + (1-cos^2)
For purely tangential edges (cos^2 = 0), stretch^2 = 1 — no anisotropy
contribution. So a walker that stays on tangential edges should see
gamma_substrate = sqrt(1 - L - v^2 * 1) = sqrt((1-L) - v^2) = exact
Schwarzschild tangential. Test: does it?

Selective tangential walker:
  - Start at node near r=target_r.
  - Each step: pick edge with MIN cos^2(edge_dir, r_hat) (most tangential),
    excluding the previous node to avoid trivial back-and-forth.
  - Stop if |r - target_r| / target_r > R_TOLERANCE (drifted out of shell)
    or out of edges.
  - Record per-step metrics.

Then path-integrated:
  gamma_walker  = sqrt(1 - <L>_path - v^2 * <s^2>_path)
  gamma_schwarz = sqrt((1-<L>) - v^2)         # (no factor; tangential)

If the per-step <s^2>_path stays near 1 (walker IS tangential),
gamma_walker == gamma_schwarz to machine precision. If the walker
can't find tangential edges in inner shells (graph isotropy fails),
<s^2>_path > 1 and gamma_walker < gamma_schwarz — Phase 5 broke.
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
from phase3_selective_walker import build_csr

TARGET_RS = [5.0, 8.0, 12.0, 18.0, 25.0]
R_TOLERANCE = 0.15
MAX_STEPS = 500

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def selective_tangential_walker(pos, offsets, nbr_dst, nbr_edge, edge_dir,
                                cos2_e, L_e, edge_rate, start_node, target_r,
                                r_tolerance, max_steps):
  path = []
  n = int(start_node)
  prev = -1
  for step in range(max_steps):
    r_pos = pos[n]
    r_norm = float(np.linalg.norm(r_pos))
    if r_norm < 1e-6:
      break
    if abs(r_norm - target_r) / target_r > r_tolerance:
      break  # drifted out of shell
    r_hat = (r_pos / r_norm).astype(np.float32)
    e_lo, e_hi = int(offsets[n]), int(offsets[n + 1])
    if e_lo == e_hi:
      break
    nbrs = nbr_dst[e_lo:e_hi]
    edges = nbr_edge[e_lo:e_hi]
    edge_dirs = edge_dir[edges]
    dots = edge_dirs @ r_hat
    cos2_rhat = dots * dots
    # Exclude returning to prev node
    valid = nbrs != prev
    if not valid.any():
      break
    cos2_pick = np.where(valid, cos2_rhat, 2.0)  # 2.0 > any cos² so excluded
    best = int(np.argmin(cos2_pick))
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
    prev = n
    n = m
  return path


def gamma_substrate(L, v, s2):
  arg = 1.0 - L - v * v * s2
  return np.sqrt(max(arg, 0.0))

def gamma_schwarz_tangential(L, v):
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
  return dict(L=L, s2=s2, c2_rhat=c2_rhat, c2_field=c2_field, rs=rs)


def report_walker(label, summary, target_r):
  print(f"\n--- {label} ---")
  if summary is None or len(summary['L']) == 0:
    print("  (empty path)"); return None
  steps = len(summary['L'])
  L_mean = float(summary['L'].mean())
  s2_mean = float(summary['s2'].mean())
  c2_rhat_mean = float(summary['c2_rhat'].mean())
  r_min = float(summary['rs'].min()); r_max = float(summary['rs'].max())
  drift = (r_max - r_min) / target_r
  print(f"  steps={steps}  r_range=[{r_min:.2f}, {r_max:.2f}]  "
        f"drift_frac={drift:.4f} (tol={R_TOLERANCE})")
  print(f"  <L>={L_mean:.4f}  <s^2>={s2_mean:.4f}  "
        f"(target for tangential = 1.0)  excess={s2_mean - 1.0:+.4f}")
  print(f"  <cos^2 vs rhat>={c2_rhat_mean:.4f}  (target for tangential = 0)")
  return dict(L=L_mean, s2=s2_mean, c2_rhat=c2_rhat_mean, steps=steps,
              target_r=target_r, drift=drift)


def gamma_table(summaries):
  print("\n=== Walker-path gamma comparison (tangential motion) ===")
  print(f"  {'r':>5}  {'v':>5}  {'<L>':>7}  {'<s^2>':>7}  "
        f"{'g_walker':>9}  {'g_schw':>8}  {'rel_err':>8}")
  rows = []
  for s in summaries:
    if s is None: continue
    L = s['L']; s2 = s['s2']; r0 = s['target_r']
    for v in TEST_V:
      gw = gamma_substrate(L, v, s2)
      gsch = gamma_schwarz_tangential(L, v)
      e = abs(gw - gsch) / max(gsch, 1e-10) if gsch > 0 else float('nan')
      print(f"  {r0:>5.1f}  {v:>5.2f}  {L:>7.4f}  {s2:>7.4f}  "
            f"{gw:>9.4f}  {gsch:>8.4f}  {e:>8.4f}")
      rows.append((r0, v, L, s2, gw, gsch, e))
  errs = [r[6] for r in rows if np.isfinite(r[6])]
  if errs:
    print(f"\n  walker vs Schwarz tangential: mean={np.mean(errs):.5f}  "
          f"max={np.max(errs):.5f}")
    print(f"  (Phase 5 survival: should be ~0 if anisotropy turn-on "
          f"doesn't break tangential)")
  return rows


def plot(summaries, paths_by_r, rows):
  fig, axes = plt.subplots(2, 2, figsize=(14, 10))

  # (0,0) cos^2_rhat along path
  ax = axes[0, 0]
  for r0, path in paths_by_r.items():
    if not path: continue
    s = summarize_path(path)
    ax.plot(np.arange(len(s['c2_rhat'])), s['c2_rhat'], label=f'r={r0:.0f}',
            alpha=0.7, lw=1)
  ax.axhline(0.0, color='k', linestyle='--', alpha=0.5, label='target=0')
  ax.axhline(1/3, color='gray', linestyle=':', alpha=0.4, label='isotropic 1/3')
  ax.set_xlabel('step'); ax.set_ylabel('cos^2 (edge vs r_hat)')
  ax.set_title('walker tangentiality')
  ax.set_ylim(-0.05, 1.05); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

  # (0,1) stretch^2 along path
  ax = axes[0, 1]
  for r0, path in paths_by_r.items():
    if not path: continue
    s = summarize_path(path)
    ax.plot(np.arange(len(s['s2'])), s['s2'], label=f'r={r0:.0f}',
            alpha=0.7, lw=1)
  ax.axhline(1.0, color='k', linestyle='--', alpha=0.5, label='target=1')
  ax.set_xlabel('step'); ax.set_ylabel('s^2 (per-step)')
  ax.set_title('per-step stretch^2 (1.0 = no anisotropy effect)')
  ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

  # (1,0) per-r0 <s²> excess vs L
  ax = axes[1, 0]
  Ls, excesses = [], []
  for s in summaries:
    if s is None: continue
    Ls.append(s['L']); excesses.append(s['s2'] - 1.0)
  ax.plot(Ls, excesses, 'o-')
  ax.axhline(0.0, color='k', linestyle='--', alpha=0.5, label='target excess=0')
  ax.set_xlabel('<L>_path'); ax.set_ylabel('<s^2>_path - 1.0')
  ax.set_title('how far stretch² strays from 1 (broke tangential by how much?)')
  ax.legend(); ax.grid(True, alpha=0.3)

  # (1,1) gamma error per r
  ax = axes[1, 1]
  arr = np.array(rows)
  for r0 in TARGET_RS:
    rmask = arr[:, 0] == r0
    if rmask.sum() == 0: continue
    vs = arr[rmask, 1]
    e = arr[rmask, 6]
    ax.plot(vs, e, 'o-', label=f'r={r0:.0f}')
  ax.set_xlabel('v/c'); ax.set_ylabel('rel err vs Schwarz tangential')
  ax.set_title('walker gamma error vs Schwarzschild tangential')
  ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

  plt.suptitle('Exp 132 Phase 4: tangential walker (Phase 5 survival)', fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase4_tangential_walker.png')
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

  print("\n=== Walking tangential trajectories ===")
  paths_by_r = {}
  summaries = []
  for r0 in TARGET_RS:
    candidates = np.argsort(np.abs(r_of - r0))[:20]
    start = int(candidates[0])
    actual_r = float(r_of[start])
    print(f"\n  target_r={r0:.1f}  start_node={start}  actual_r={actual_r:.3f}")
    path = selective_tangential_walker(pos, offsets, nbr_dst, nbr_edge, edge_dir,
                                        cos2_e, L_e, edge_rate, start, r0,
                                        R_TOLERANCE, MAX_STEPS)
    paths_by_r[r0] = path
    s = summarize_path(path)
    summaries.append(report_walker(f"r={r0:.1f}", s, r0))

  rows = gamma_table(summaries)
  plot(summaries, paths_by_r, rows)


if __name__ == '__main__':
  run()
