#!/usr/bin/env python3
"""
Experiment 131 - Phase 1 v5: Conductance-weighted flow on the lineage tree.

v3/v4 used naive averaging diffusion (rho_new[i] = mean(rho[neighbors])).
This ignores the spatial geometry the tree is embedded in: a long edge
across a sparse region transports the same way as a short edge in a
dense region. Phase 1 v3/v4 falsified naive averaging on the boundary-
stability test (slope swings -2 -> -0.17 as BOUNDARY_FRACTION moves).

This version uses the resistor-network analogue: per-edge conductance
c_ij = 1 / length(edge). Flow becomes a weighted average:

    rho_new[i] = sum_j c_ij * rho[j] / sum_j c_ij

The tree topology is unchanged (RAW 131 ontology preserved); only the
flow rule respects the 3D embedding.

Falsification: if rho(r) ~ 1/r is now seed- AND boundary-stable across
BOUNDARY_FRACTION in {0.5, 0.7, 0.9}, RAW 131 with conductance flow
lives. If slopes still swing with boundary, the lineage substrate is
the wrong layer and we report and stop.

Sweep: 3 seeds x 3 boundaries = 9 runs.
"""

import os
import sys
import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Tree parameters (parity with v3)
BRANCHING = 8
DEPTH = 5
R_ROOT = 10.0
SCALE = float(BRANCHING) ** (1.0 / 3.0)
SEEDS = [42, 7, 101]
BOUNDARY_FRACTIONS = [0.5, 0.7, 0.9]

N_TICKS = 30_000
REPORT_EVERY = 6000
STAR_N = 50

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def sample_in_sphere(rng, R, n):
  d = rng.normal(size=(n, 3))
  d /= np.linalg.norm(d, axis=1, keepdims=True)
  radii = R * (rng.uniform(size=n) ** (1.0 / 3.0))
  return (d * radii[:, None]).astype(np.float32)


def build_tree(seed):
  rng = np.random.default_rng(seed)
  nodes_pos = [np.zeros(3, dtype=np.float32)]
  nodes_parent = [-1]
  current = [0]
  R = R_ROOT
  for d in range(1, DEPTH + 1):
    R /= SCALE
    nxt = []
    for p_idx in current:
      offsets = sample_in_sphere(rng, R, BRANCHING)
      p_pos = nodes_pos[p_idx]
      for off in offsets:
        nodes_pos.append(p_pos + off)
        nodes_parent.append(p_idx)
        nxt.append(len(nodes_pos) - 1)
    current = nxt
  pos = np.array(nodes_pos, dtype=np.float32)
  parent = np.array(nodes_parent, dtype=np.int32)
  return pos, parent


def prepare_conductance(parent, pos):
  """Per-edge conductance c[i] = 1 / |pos[i] - pos[parent[i]]| (edge i -> parent[i]).
  Per-node total conductance = sum over all incident edges (parent edge + child edges)."""
  N = len(parent)
  valid = parent >= 0
  edge_cond = np.zeros(N, dtype=np.float32)
  edge_len = np.linalg.norm(pos[valid] - pos[parent[valid]], axis=1)
  edge_cond[valid] = 1.0 / np.maximum(edge_len, 1e-10)
  total_cond = np.zeros(N, dtype=np.float32)
  total_cond[valid] += edge_cond[valid]
  np.add.at(total_cond, parent[valid], edge_cond[valid])
  return edge_cond, total_cond, valid


def propagate_step(rho, parent, valid, edge_cond, total_cond,
                   source_mask, source_value, boundary_mask):
  """rho_new[i] = sum_j c_ij rho[j] / sum_j c_ij over tree neighbors."""
  weighted_sum = np.zeros_like(rho)
  # Contribution from parent: node i's parent feeds via edge edge_cond[i]
  parent_rho = np.where(valid, rho[parent], 0).astype(np.float32)
  weighted_sum[valid] += (edge_cond[valid] * parent_rho[valid]).astype(np.float32)
  # Contribution from each child: parent receives c[child] * rho[child]
  np.add.at(weighted_sum, parent[valid],
            (edge_cond[valid] * rho[valid]).astype(np.float32))
  safe = np.maximum(total_cond, 1e-10)
  rho_new = (weighted_sum / safe).astype(np.float32)
  rho_new[source_mask] = source_value
  rho_new[boundary_mask] = 0.0
  return rho_new


def bin_rho_by_r(rho, r, r_min, r_max, n_bins=28, skip_mask=None):
  edges = np.logspace(np.log10(r_min), np.log10(r_max), n_bins + 1)
  centers = np.sqrt(edges[:-1] * edges[1:])
  mean = np.zeros(len(centers))
  counts = np.zeros(len(centers), dtype=int)
  for i in range(len(centers)):
    m = (r >= edges[i]) & (r < edges[i + 1])
    if skip_mask is not None:
      m &= ~skip_mask
    counts[i] = int(m.sum())
    if counts[i] > 0:
      mean[i] = rho[m].mean()
  return centers, mean, counts


def fit_slope(centers, values, r_lo, r_hi):
  m = (centers >= r_lo) & (centers <= r_hi) & (values > 0)
  if m.sum() < 4:
    return float('nan'), int(m.sum())
  s, _ = np.polyfit(np.log(centers[m]), np.log(values[m]), 1)
  return float(s), int(m.sum())


def fit_A_over_r(centers, mean_rho, r_lo, r_hi):
  m = (centers >= r_lo) & (centers <= r_hi) & (mean_rho > 0)
  if m.sum() < 4:
    return float('nan'), float('nan')
  log_A = np.log(mean_rho[m]) + np.log(centers[m])
  return float(np.exp(np.mean(log_A))), float(np.std(log_A))


def run_one(pos, parent, seed, boundary_fraction):
  N = len(pos)
  r_of = np.linalg.norm(pos, axis=1)
  star_idx = np.argsort(r_of)[:STAR_N]
  star_mask = np.zeros(N, dtype=bool); star_mask[star_idx] = True
  r_max = float(r_of.max())
  boundary_mask = (r_of > boundary_fraction * r_max) & ~star_mask
  edge_cond, total_cond, valid = prepare_conductance(parent, pos)
  rho = np.zeros(N, dtype=np.float32)
  rho[star_mask] = 1.0
  interior = ~(star_mask | boundary_mask)
  print(f"  seed={seed} bf={boundary_fraction}  "
        f"R_max={r_max:.2f}  bound={int(boundary_mask.sum())}  "
        f"interior={int(interior.sum())}")
  t0 = time.time(); last = t0; last_mean = 0.0
  for tick in range(1, N_TICKS + 1):
    rho = propagate_step(rho, parent, valid, edge_cond, total_cond,
                         star_mask, 1.0, boundary_mask)
    if tick % REPORT_EVERY == 0:
      now = time.time()
      tps = REPORT_EVERY / max(0.001, now - last); last = now
      cur = float(rho[interior].mean()); d = cur - last_mean; last_mean = cur
      print(f"    t={tick:6d}  mean={cur:.5f}  d={d:+.5f}  ({tps:.0f} t/s)")
      sys.stdout.flush()
  print(f"  {N_TICKS} ticks in {time.time() - t0:.1f}s")

  centers, mean, _ = bin_rho_by_r(rho, r_of, 0.3, 1.2 * r_max,
                                  skip_mask=star_mask | boundary_mask)
  r_lo = 1.0
  r_hi = boundary_fraction * r_max * 0.70
  slope, _ = fit_slope(centers, mean, r_lo, r_hi)
  A, resid = fit_A_over_r(centers, mean, r_lo, r_hi)
  with np.errstate(divide='ignore', invalid='ignore'):
    grad = np.abs(np.gradient(mean, centers))
  slope_g, _ = fit_slope(centers, grad, r_lo, r_hi)
  print(f"    fit [{r_lo:.2f},{r_hi:.2f}]  "
        f"slope_rho={slope:+.3f}  A={A:.4f}  resid={resid:.4f}  "
        f"slope_grad={slope_g:+.3f}")
  return dict(seed=seed, bf=boundary_fraction, centers=centers, mean=mean,
              grad=grad, slope=slope, slope_grad=slope_g, A=A, resid=resid,
              r_lo=r_lo, r_hi=r_hi, r_max=r_max)


def summary(results):
  print()
  print("=" * 78)
  print(f"{'seed':>5} {'bf':>5}  {'slope_rho':>10}  {'A':>7}  "
        f"{'resid':>8}  {'slope_grad':>11}")
  print("-" * 78)
  for r in results:
    print(f"{r['seed']:>5} {r['bf']:>5.2f}  {r['slope']:>+10.3f}  "
          f"{r['A']:>7.4f}  {r['resid']:>8.4f}  {r['slope_grad']:>+11.3f}")
  by_bf = {}
  for r in results:
    by_bf.setdefault(r['bf'], []).append(r['slope'])
  print()
  print("Boundary-stability check (slope_rho across seeds, target -1.0):")
  for bf in sorted(by_bf):
    s = by_bf[bf]
    print(f"  bf={bf:.2f}  mean={np.mean(s):+.3f}  std={np.std(s):.3f}")
  all_s = [r['slope'] for r in results if np.isfinite(r['slope'])]
  print(f"  ALL    mean={np.mean(all_s):+.3f}  std={np.std(all_s):.3f}  "
        f"(target -1.0; cross-boundary std is the falsifier)")

  # 3x3 grid of plots
  fig, axes = plt.subplots(len(SEEDS), len(BOUNDARY_FRACTIONS),
                           figsize=(15, 12), sharex=True, sharey=True)
  for r in results:
    i = SEEDS.index(r['seed']); j = BOUNDARY_FRACTIONS.index(r['bf'])
    ax = axes[i, j]
    ax.loglog(r['centers'], np.maximum(r['mean'], 1e-12), 'o-', ms=3)
    valid = (r['centers'] >= r['r_lo']) & (r['centers'] <= r['r_hi']) & (r['mean'] > 0)
    if valid.sum() > 0:
      idx = np.argmax(valid); ra = r['centers'][idx]; ya = r['mean'][idx]
      ref = np.array([r['r_lo'], r['r_hi']])
      ax.plot(ref, ya * (ref / ra) ** -1, 'k--', alpha=0.5, label='~1/r')
      ax.axvspan(r['r_lo'], r['r_hi'], color='gray', alpha=0.08)
    ax.set_title(f"seed={r['seed']} bf={r['bf']:.2f}\nslope={r['slope']:+.2f}",
                 fontsize=9)
    ax.grid(True, which='both', alpha=0.3)
  for ax in axes[-1, :]:
    ax.set_xlabel('r')
  for ax in axes[:, 0]:
    ax.set_ylabel('mean rho(r)')
  plt.suptitle('Phase 1 v5: conductance-weighted flow, k=8 D=5 tree, '
               'rho(r) across (seed, boundary)', fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase1v5_rho_profile.png')
  plt.savefig(path, dpi=130); plt.close()
  print(f"\n  saved: {path}")


def run():
  print(f"Phase 1 v5: conductance-weighted flow on lineage tree")
  print(f"  k={BRANCHING} D={DEPTH} N_TICKS={N_TICKS} STAR_N={STAR_N}")
  print(f"  seeds={SEEDS}  boundaries={BOUNDARY_FRACTIONS}")
  print()
  results = []
  for seed in SEEDS:
    print(f"=== seed {seed}: build tree ===")
    pos, parent = build_tree(seed)
    print(f"  N={len(pos)} nodes")
    for bf in BOUNDARY_FRACTIONS:
      results.append(run_one(pos, parent, seed, bf))
  summary(results)


if __name__ == '__main__':
  run()
