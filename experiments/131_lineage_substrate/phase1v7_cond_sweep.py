#!/usr/bin/env python3
"""
Experiment 131 - Phase 1 v7: Conductance-form sweep on D=5 tree.

v6 (D=6, c=1/length) gave slope -3.1 with huge residuals -- short inner
edges dominated. Question: is "tree topology can't recover 1/r" structural,
or is it about conductance form?

Sweep three forms, single seed (42), 3 boundaries, D=5 for speed:
  - c = 1            (uniform; equivalent to v3/v4 naive averaging)
  - c = 1/length     (resistor analogue; v5/v6)
  - c = length       (FVM-style; for diffusion on heterogeneous mesh,
                      conductance scales with edge cross-section ~ length^2,
                      and resistor formula c = A/length gives c ~ length.
                      Re-weights toward longer edges that v5 underweighted.)

Compare slopes and residuals across forms. Whichever (if any) gives clean
slope ~ -1 with low residual is the candidate to scale up to D=6 + multi-seed.
If none does, lineage topology itself is the bottleneck and Scenario A is
done.
"""

import os, sys, time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


BRANCHING = 8
DEPTH = 5
R_ROOT = 10.0
SCALE = float(BRANCHING) ** (1.0 / 3.0)
SEED = 42
BOUNDARY_FRACTIONS = [0.5, 0.7, 0.9]
COND_FORMS = ['uniform', 'inv_length', 'length']

N_TICKS = 30_000
REPORT_EVERY = 6000
STAR_N = 50
R_LO = 1.0

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
  for _ in range(1, DEPTH + 1):
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


def prepare_conductance(parent, pos, form):
  N = len(parent)
  valid = parent >= 0
  edge_len = np.zeros(N, dtype=np.float32)
  edge_len[valid] = np.linalg.norm(pos[valid] - pos[parent[valid]], axis=1)
  edge_cond = np.zeros(N, dtype=np.float32)
  if form == 'uniform':
    edge_cond[valid] = 1.0
  elif form == 'inv_length':
    edge_cond[valid] = 1.0 / np.maximum(edge_len[valid], 1e-10)
  elif form == 'length':
    edge_cond[valid] = edge_len[valid]
  else:
    raise ValueError(form)
  total_cond = np.zeros(N, dtype=np.float32)
  total_cond[valid] += edge_cond[valid]
  np.add.at(total_cond, parent[valid], edge_cond[valid])
  return edge_cond, total_cond, valid


def propagate_step(rho, parent, valid, edge_cond, total_cond,
                   source_mask, source_value, boundary_mask):
  weighted_sum = np.zeros_like(rho)
  parent_rho = np.where(valid, rho[parent], 0).astype(np.float32)
  weighted_sum[valid] += (edge_cond[valid] * parent_rho[valid]).astype(np.float32)
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
  for i in range(len(centers)):
    m = (r >= edges[i]) & (r < edges[i + 1])
    if skip_mask is not None: m &= ~skip_mask
    if m.sum() > 0: mean[i] = rho[m].mean()
  return centers, mean


def fit_slope(centers, values, r_lo, r_hi):
  m = (centers >= r_lo) & (centers <= r_hi) & (values > 0)
  if m.sum() < 4: return float('nan')
  s, _ = np.polyfit(np.log(centers[m]), np.log(values[m]), 1)
  return float(s)


def fit_A_over_r(centers, mean_rho, r_lo, r_hi):
  m = (centers >= r_lo) & (centers <= r_hi) & (mean_rho > 0)
  if m.sum() < 4: return float('nan'), float('nan')
  log_A = np.log(mean_rho[m]) + np.log(centers[m])
  return float(np.exp(np.mean(log_A))), float(np.std(log_A))


def run_one(pos, parent, form, bf):
  N = len(pos)
  r_of = np.linalg.norm(pos, axis=1)
  star_idx = np.argsort(r_of)[:STAR_N]
  star_mask = np.zeros(N, dtype=bool); star_mask[star_idx] = True
  r_max = float(r_of.max())
  boundary_mask = (r_of > bf * r_max) & ~star_mask
  edge_cond, total_cond, valid = prepare_conductance(parent, pos, form)
  rho = np.zeros(N, dtype=np.float32); rho[star_mask] = 1.0
  interior = ~(star_mask | boundary_mask)
  print(f"  form={form:>10}  bf={bf}  R_max={r_max:.2f}")
  t0 = time.time(); last = t0; lm = 0.0
  for tick in range(1, N_TICKS + 1):
    rho = propagate_step(rho, parent, valid, edge_cond, total_cond,
                         star_mask, 1.0, boundary_mask)
    if tick % REPORT_EVERY == 0:
      now = time.time()
      tps = REPORT_EVERY / max(0.001, now - last); last = now
      cur = float(rho[interior].mean()); d = cur - lm; lm = cur
      print(f"    t={tick:6d}  mean={cur:.5f}  d={d:+.5f}  ({tps:.0f} t/s)")
      sys.stdout.flush()
  print(f"  done in {time.time() - t0:.1f}s")
  centers, mean = bin_rho_by_r(rho, r_of, 0.3, 1.2 * r_max,
                               skip_mask=star_mask | boundary_mask)
  r_lo = R_LO; r_hi = bf * r_max * 0.70
  slope = fit_slope(centers, mean, r_lo, r_hi)
  A, resid = fit_A_over_r(centers, mean, r_lo, r_hi)
  print(f"    slope={slope:+.3f}  A={A:.4f}  resid={resid:.4f}")
  return dict(form=form, bf=bf, centers=centers, mean=mean,
              slope=slope, A=A, resid=resid, r_lo=r_lo, r_hi=r_hi, r_max=r_max)


def summary(results):
  print()
  print("=" * 72)
  print(f"{'form':>10}  {'bf':>5}  {'slope':>+8}  {'A':>7}  {'resid':>7}")
  print("-" * 72)
  for r in results:
    print(f"{r['form']:>10}  {r['bf']:>5.2f}  {r['slope']:>+8.3f}  "
          f"{r['A']:>7.4f}  {r['resid']:>7.4f}")
  print()
  print("By form (boundary stability + slope target -1.0):")
  by_form = {}
  for r in results: by_form.setdefault(r['form'], []).append(r)
  for form, rs in by_form.items():
    slopes = [r['slope'] for r in rs if np.isfinite(r['slope'])]
    resids = [r['resid'] for r in rs if np.isfinite(r['resid'])]
    print(f"  {form:>10}: slope mean={np.mean(slopes):+.3f}  std={np.std(slopes):.3f}  "
          f"resid mean={np.mean(resids):.4f}")

  fig, axes = plt.subplots(len(COND_FORMS), len(BOUNDARY_FRACTIONS),
                           figsize=(15, 12), sharex=True, sharey=True)
  for r in results:
    i = COND_FORMS.index(r['form']); j = BOUNDARY_FRACTIONS.index(r['bf'])
    ax = axes[i, j]
    ax.loglog(r['centers'], np.maximum(r['mean'], 1e-12), 'o-', ms=3)
    valid = (r['centers'] >= r['r_lo']) & (r['centers'] <= r['r_hi']) & (r['mean'] > 0)
    if valid.sum() > 0:
      idx = np.argmax(valid); ra = r['centers'][idx]; ya = r['mean'][idx]
      ref = np.array([r['r_lo'], r['r_hi']])
      ax.plot(ref, ya * (ref / ra) ** -1, 'k--', alpha=0.5)
      ax.axvspan(r['r_lo'], r['r_hi'], color='gray', alpha=0.08)
    ax.set_title(f"{r['form']} bf={r['bf']:.2f}\nslope={r['slope']:+.2f}", fontsize=9)
    ax.grid(True, which='both', alpha=0.3)
  for ax in axes[-1, :]: ax.set_xlabel('r')
  for ax in axes[:, 0]: ax.set_ylabel('mean rho(r)')
  plt.suptitle(f'Phase 1 v7: conductance-form sweep, D={DEPTH} seed={SEED}',
               fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase1v7_cond_sweep.png')
  plt.savefig(path, dpi=130); plt.close()
  print(f"\n  saved: {path}")


def run():
  print(f"Phase 1 v7: conductance-form sweep")
  print(f"  k={BRANCHING} D={DEPTH} N_TICKS={N_TICKS} seed={SEED}")
  print(f"  forms={COND_FORMS}  boundaries={BOUNDARY_FRACTIONS}")
  print()
  pos, parent = build_tree(SEED)
  print(f"=== built tree: N={len(pos)} ===\n")
  results = []
  for form in COND_FORMS:
    for bf in BOUNDARY_FRACTIONS:
      results.append(run_one(pos, parent, form, bf))
  summary(results)


if __name__ == '__main__':
  run()
