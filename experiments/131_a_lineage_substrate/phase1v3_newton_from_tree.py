#!/usr/bin/env python3
"""
Experiment 131 - Phase 1 v3: Cleaner rho(r) on a Lineage Tree

Phase 1 v1/v2 produced rho(r) approximately 1/r but with significant
curvature (fit slope depends on window; -0.92 over one range, -1.35 over
another). Phase 2 revealed this: rho(r) is not a clean power law, which
breaks the tangential Schwarzschild transfer.

Three changes in this version:

  (a) Uniform-in-sphere offsets, not Gaussian.
      Gaussian(0, R) concentrates children near parent; uniform-in-sphere
      distributes them uniformly across the ball. The latter gives
      3D-uniform density on average, not a concentration profile, which
      should produce cleaner 1/r behavior.

  (b) Spatial star, not subtree star.
      Previous runs used all descendants of one depth-3 node as the star.
      That cluster sits offset from the origin and has its own sub-structure.
      Better: pick the 50 nodes nearest to the origin (regardless of
      lineage). That matches Exp 128 RGG's setup: spatial cluster at the
      center of the volume.

  (c) Larger boundary (0.5), longer run (30000 ticks).
      With a bigger sink, steady state is reached faster; with more ticks,
      interior mean is no longer growing meaningfully.

Run 3 seeds; check whether rho(r) is now clean 1/r.
"""

import os
import sys
import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ── Tree parameters ──
BRANCHING = 8
DEPTH = 5
R_ROOT = 10.0
SCALE = float(BRANCHING) ** (1.0 / 3.0)
SEEDS = [42, 7, 101]

# ── Simulation ──
N_TICKS = 30_000
REPORT_EVERY = 3000

# ── Source ──
STAR_N = 50        # nearest-to-origin nodes form the star

# ── Boundary ──
BOUNDARY_FRACTION = 0.90

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


# ------------------------------------------------------------------
#  Tree construction — uniform-in-sphere offsets
# ------------------------------------------------------------------

def sample_in_sphere(rng, R, n):
  """Return n uniform-random points inside a ball of radius R."""
  direction = rng.normal(size=(n, 3))
  direction /= np.linalg.norm(direction, axis=1, keepdims=True)
  radii = R * (rng.uniform(size=n) ** (1.0 / 3.0))
  return (direction * radii[:, None]).astype(np.float32)


def build_tree(seed):
  print(f"Building tree: k={BRANCHING}, D={DEPTH}, scale={SCALE:.3f}, seed={seed}")
  rng = np.random.default_rng(seed)
  t0 = time.time()

  nodes_pos = [np.zeros(3, dtype=np.float32)]
  nodes_parent = [-1]
  nodes_level = [0]
  current_indices = [0]

  R = R_ROOT
  for d in range(1, DEPTH + 1):
    R /= SCALE
    next_indices = []
    n_parents = len(current_indices)
    # Batch all children for this level for speed
    for parent_idx in current_indices:
      offsets = sample_in_sphere(rng, R, BRANCHING)
      parent_pos = nodes_pos[parent_idx]
      for off in offsets:
        child_idx = len(nodes_pos)
        nodes_pos.append(parent_pos + off)
        nodes_parent.append(parent_idx)
        nodes_level.append(d)
        next_indices.append(child_idx)
    print(f"  depth {d}: {n_parents} parents -> {len(next_indices)} children, R_level={R:.3f}")
    current_indices = next_indices

  pos = np.array(nodes_pos, dtype=np.float32)
  parent = np.array(nodes_parent, dtype=np.int32)
  level = np.array(nodes_level, dtype=np.int32)
  print(f"  total {len(pos)} nodes in {time.time() - t0:.2f}s")
  return pos, parent, level


# ------------------------------------------------------------------
#  Propagation (reused from v2)
# ------------------------------------------------------------------

def prepare_neighbor_counts(parent):
  N = len(parent)
  has_parent = (parent >= 0).astype(np.int32)
  child_count = np.zeros(N, dtype=np.int32)
  valid = parent >= 0
  np.add.at(child_count, parent[valid], 1)
  return has_parent + child_count, valid


def propagate_step(rho, parent, valid, neighbor_count, source_mask,
                   source_value, boundary_mask):
  children_sum = np.zeros_like(rho)
  np.add.at(children_sum, parent[valid], rho[valid])
  parent_rho = np.where(valid, rho[parent], 0).astype(np.float32)
  total = children_sum + parent_rho
  safe_count = np.maximum(neighbor_count, 1).astype(np.float32)
  rho_new = (total / safe_count).astype(np.float32)
  rho_new[source_mask] = source_value
  rho_new[boundary_mask] = 0.0
  return rho_new


# ------------------------------------------------------------------
#  Measurement
# ------------------------------------------------------------------

def bin_rho_by_r(rho, r, r_min, r_max, n_bins=28, skip_mask=None):
  bin_edges = np.logspace(np.log10(r_min), np.log10(r_max), n_bins + 1)
  centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
  mean = np.zeros(len(centers))
  counts = np.zeros(len(centers), dtype=int)
  for i in range(len(centers)):
    mask = (r >= bin_edges[i]) & (r < bin_edges[i + 1])
    if skip_mask is not None:
      mask &= ~skip_mask
    counts[i] = int(mask.sum())
    if counts[i] > 0:
      mean[i] = rho[mask].mean()
  return centers, mean, counts


def fit_slope(centers, values, r_lo, r_hi):
  m = (centers >= r_lo) & (centers <= r_hi) & (values > 0)
  if m.sum() < 4:
    return float('nan'), int(m.sum())
  slope, _ = np.polyfit(np.log(centers[m]), np.log(values[m]), 1)
  return float(slope), int(m.sum())


def fit_A_over_r(centers, mean_rho, r_lo, r_hi):
  """Fit rho = A / r constrained to slope -1; report A and residual RMS in log."""
  m = (centers >= r_lo) & (centers <= r_hi) & (mean_rho > 0)
  if m.sum() < 4:
    return float('nan'), float('nan')
  log_A_vals = np.log(mean_rho[m]) + np.log(centers[m])
  A = float(np.exp(np.mean(log_A_vals)))
  residual_rms = float(np.std(log_A_vals))  # in natural-log units
  return A, residual_rms


# ------------------------------------------------------------------
#  Run one seed
# ------------------------------------------------------------------

def run_one_seed(seed):
  pos, parent, level = build_tree(seed)
  N = len(pos)

  # Star: 50 nearest to origin
  r_of = np.linalg.norm(pos, axis=1)
  star_indices = np.argsort(r_of)[:STAR_N]
  star_mask = np.zeros(N, dtype=bool); star_mask[star_indices] = True
  star_pos = np.zeros(3, dtype=np.float32)  # origin by construction
  r_max = float(r_of.max())
  print(f"  Star: {STAR_N} nearest-origin nodes, max star r = {r_of[star_indices].max():.3f}")
  print(f"  Tree spatial extent: R_max = {r_max:.2f}")

  boundary_mask = (r_of > BOUNDARY_FRACTION * r_max) & ~star_mask
  print(f"  Boundary: {int(boundary_mask.sum())} nodes at r > {BOUNDARY_FRACTION * r_max:.2f}")

  rho = np.zeros(N, dtype=np.float32)
  rho[star_mask] = 1.0

  neighbor_count, valid = prepare_neighbor_counts(parent)
  interior_mask = ~(star_mask | boundary_mask)

  t0 = time.time()
  last_report = t0
  last_mean = 0.0
  for tick in range(1, N_TICKS + 1):
    rho = propagate_step(rho, parent, valid, neighbor_count,
                         star_mask, 1.0, boundary_mask)
    if tick % REPORT_EVERY == 0:
      now = time.time()
      tps = REPORT_EVERY / max(0.001, now - last_report)
      last_report = now
      current = float(rho[interior_mask].mean())
      delta = current - last_mean
      last_mean = current
      print(f"    t={tick:6d}  interior_mean={current:.6f}  "
            f"(delta={delta:+.6f})  ({tps:.0f} t/s)")
      sys.stdout.flush()
  print(f"  Done: {N_TICKS} ticks in {time.time() - t0:.1f}s")

  centers, mean, counts = bin_rho_by_r(rho, r_of, r_min=0.3, r_max=1.2 * r_max,
                                       skip_mask=star_mask | boundary_mask)
  # Choose fit range: exclude innermost (star + near-star) AND the
  # boundary-cliff region (last ~15% of interior radius where rho
  # crashes to zero near the absorbing shell).
  r_lo = 1.0
  r_hi = BOUNDARY_FRACTION * r_max * 0.70  # stay well clear of boundary cliff

  slope_free, n_free = fit_slope(centers, mean, r_lo, r_hi)
  A, residual = fit_A_over_r(centers, mean, r_lo, r_hi)

  # Also measure gradient cleanly
  with np.errstate(divide='ignore', invalid='ignore'):
    grad = np.abs(np.gradient(mean, centers))
  slope_grad, _ = fit_slope(centers, grad, r_lo, r_hi)

  print(f"  Fit [{r_lo:.2f}, {r_hi:.2f}]:")
  print(f"    rho: free slope = {slope_free:+.3f} (target -1.0)")
  print(f"    rho: A/r fit:   A = {A:.4f}, residual RMS = {residual:.4f} (log units)")
  print(f"    grad: slope = {slope_grad:+.3f} (target -2.0)")

  return {
    'seed': seed,
    'centers': centers,
    'mean': mean,
    'grad': grad,
    'slope_free': slope_free,
    'slope_grad': slope_grad,
    'A': A,
    'residual': residual,
    'r_max': r_max,
    'r_lo': r_lo,
    'r_hi': r_hi,
  }


# ------------------------------------------------------------------
#  Plot + summary
# ------------------------------------------------------------------

def summarize(results):
  print()
  print("=" * 72)
  print(f"{'seed':>5}  {'slope_free':>11}  {'A':>7}  {'residual_log':>14}  "
        f"{'slope_grad':>11}")
  print("-" * 72)
  for r in results:
    print(f"{r['seed']:>5}  {r['slope_free']:>+11.3f}  {r['A']:>7.4f}  "
          f"{r['residual']:>14.4f}  {r['slope_grad']:>+11.3f}")
  slopes_f = [r['slope_free'] for r in results if np.isfinite(r['slope_free'])]
  resids = [r['residual'] for r in results if np.isfinite(r['residual'])]
  slopes_g = [r['slope_grad'] for r in results if np.isfinite(r['slope_grad'])]
  if slopes_f:
    print()
    print(f"  slope_rho  : mean={np.mean(slopes_f):+.3f}  std={np.std(slopes_f):.3f}  (target -1.0)")
    print(f"  residual   : mean={np.mean(resids):.4f}  (lower = cleaner 1/r)")
    print(f"  slope_grad : mean={np.mean(slopes_g):+.3f}  std={np.std(slopes_g):.3f}  (target -2.0)")

  fig, axes = plt.subplots(1, 2, figsize=(14, 5))
  colors = plt.cm.viridis(np.linspace(0, 1, len(results)))

  for color, r in zip(colors, results):
    axes[0].loglog(r['centers'], np.maximum(r['mean'], 1e-12), 'o-',
                   color=color, lw=1, ms=3,
                   label=f"seed={r['seed']}  slope={r['slope_free']:+.2f}")
    axes[1].loglog(r['centers'], np.maximum(r['grad'], 1e-12), 's-',
                   color=color, lw=1, ms=3,
                   label=f"seed={r['seed']}  slope={r['slope_grad']:+.2f}")

  # Reference lines anchored on first seed's mid-range
  r0 = results[0]['centers']; m0 = results[0]['mean']
  r_lo = results[0]['r_lo']; r_hi = results[0]['r_hi']
  valid = (r0 >= r_lo) & (r0 <= r_hi) & (m0 > 0)
  if valid.sum() > 0:
    anchor_idx = np.argmax(valid)
    r_anchor = r0[anchor_idx]; y_anchor = m0[anchor_idx]
    ref_r = np.array([r_lo, r_hi])
    for ax, p, lbl, ay in [
        (axes[0], -1, '~ 1/r (Newton)', y_anchor),
        (axes[1], -2, '~ 1/r^2 (Newton)', np.abs(-1) * y_anchor / r_anchor),
    ]:
      y_ref = ay * (ref_r / r_anchor) ** p
      ax.plot(ref_r, y_ref, 'k--', alpha=0.55, lw=1.3, label=f'ref {lbl}')
      ax.axvspan(r_lo, r_hi, color='gray', alpha=0.08)

  axes[0].set_xlabel('r'); axes[0].set_ylabel('mean rho(r)')
  axes[0].set_title(f'Phase 1 v3: rho(r), uniform offsets, N_ticks={N_TICKS}')
  axes[0].grid(True, which='both', alpha=0.3); axes[0].legend(fontsize=8)

  axes[1].set_xlabel('r'); axes[1].set_ylabel('|d rho / d r|')
  axes[1].set_title('gradient (finite difference)')
  axes[1].grid(True, which='both', alpha=0.3); axes[1].legend(fontsize=8)

  plt.suptitle(
    f'Phase 1 v3: k={BRANCHING}, D={DEPTH}, uniform-in-sphere offsets, '
    f'spatial star, BOUNDARY_FRACTION={BOUNDARY_FRACTION}',
    fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase1v4_rho_profile.png')
  plt.savefig(path, dpi=140)
  plt.close()
  print(f"\n  saved: {path}")


def run():
  results = []
  for seed in SEEDS:
    print(f"\n=== Seed {seed} ===")
    results.append(run_one_seed(seed))
  summarize(results)


if __name__ == '__main__':
  run()
