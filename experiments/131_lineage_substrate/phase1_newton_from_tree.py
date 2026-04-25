#!/usr/bin/env python3
"""
Experiment 131 - Phase 1: Newton from a Lineage Tree

Test whether a 3D-embedded lineage tree with a self-similar branching rule
reproduces Phase 1 of Experiment 128: density ρ(r) falling as 1/r, gradient
as 1/r². That was the foundation of everything downstream in Exp 128 (Kepler,
redshift, tangential Schwarzschild).

If the tree substrate gives the same functional forms at the same cost, we
have the ontology upgrade RAW 131 proposes. If it gives a different falloff
(e.g., 1/r³ from naive k^d counting), we learn immediately that the naive
flow rule is wrong — and that tells us where to go next.

Construction:
  - Tree with branching factor k, depth D.
  - Each level's children scattered around their parent with Gaussian offset
    of std R_level. R_level shrinks geometrically by scale_factor s per level.
  - 3D-self-similar choice: s = k^(1/3), so k children in volume ~s^3 =
    k × (one-child-volume), i.e. local density is preserved across levels.
  - Total leaves at depth D: k^D.

Flow rule (baseline):
  - Each node receives +0 from baseline (we only track the above-baseline
    excess driven by the source).
  - Source subtree held at ρ = 1.0 every tick.
  - Every other node: ρ_new[i] = mean of ρ at its neighbors (parent + children).
  - Iterate until steady state.

Measurement:
  - Bin by spatial distance r to star centroid.
  - Fit power-law slopes of ρ(r) and |∇ρ|(r) in the mid-range.
  - Compare to the clean 1/r (slope -1) and 1/r² (slope -2) expected from
    Exp 128's RGG substrate.
"""

import os
import sys
import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ── Tree parameters ──
BRANCHING = 8                     # k: children per parent
DEPTH = 5                         # D: tree depth (8^5 = 32768 leaves)
R_ROOT = 10.0                     # initial spawn radius (std of gaussian)
SCALE = float(BRANCHING) ** (1.0 / 3.0)  # k^(1/3), gives 3D self-similarity
SEEDS = [42, 7, 101]              # run multiple trees to check robustness

# ── Simulation ──
N_TICKS = 8000
SNAPSHOT_AT = [500, 2000, 5000, 8000]

# ── Source ──
STAR_DEPTH = 3                    # pick a depth-3 node; its subtree is the star

# ── Boundary ──
BOUNDARY_FRACTION = 0.70          # nodes with r > BOUNDARY_FRACTION * r_max are absorbing


OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


# ------------------------------------------------------------------
#  Tree construction
# ------------------------------------------------------------------

def build_tree(seed):
  """Build a 3D-embedded lineage tree with gaussian offsets per level."""
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
    for parent_idx in current_indices:
      offsets = rng.normal(0.0, R, size=(BRANCHING, 3)).astype(np.float32)
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


def get_descendants(parent, level, root_idx):
  """Return boolean mask marking root_idx and all its descendants."""
  N = len(parent)
  is_desc = np.zeros(N, dtype=bool)
  is_desc[root_idx] = True
  root_level = int(level[root_idx])
  max_level = int(level.max())
  for d in range(root_level + 1, max_level + 1):
    d_indices = np.where(level == d)[0]
    inherited = is_desc[parent[d_indices]]
    is_desc[d_indices] = inherited
  return is_desc


# ------------------------------------------------------------------
#  Propagation
# ------------------------------------------------------------------

def prepare_neighbor_counts(parent):
  """Compute per-node neighbor count (parent + children)."""
  N = len(parent)
  has_parent = (parent >= 0).astype(np.int32)
  child_count = np.zeros(N, dtype=np.int32)
  valid = parent >= 0
  np.add.at(child_count, parent[valid], 1)
  return has_parent + child_count, valid


def propagate_step(rho, parent, valid, neighbor_count, source_mask,
                   source_value, boundary_mask):
  """One tick of simple averaging diffusion on the tree."""
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

def bin_rho_by_r(rho, r, r_min, r_max, n_bins=24, skip_mask=None):
  """Log-spaced binning of mean rho vs r."""
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
  """Fit a power law in [r_lo, r_hi]. Returns (slope, valid_count)."""
  m = (centers >= r_lo) & (centers <= r_hi) & (values > 0)
  if m.sum() < 4:
    return float('nan'), int(m.sum())
  slope, _ = np.polyfit(np.log(centers[m]), np.log(values[m]), 1)
  return float(slope), int(m.sum())


# ------------------------------------------------------------------
#  Analysis + plotting
# ------------------------------------------------------------------

def measure_one_seed(pos, rho, star_mask, star_centroid, R_max):
  """Return (centers, mean_rho, slope_rho, slope_grad, R_eff_fit)."""
  r_all = np.linalg.norm(pos - star_centroid, axis=1)
  fit_lo = 0.5
  fit_hi = 0.5 * R_max
  centers, mean, counts = bin_rho_by_r(rho, r_all,
                                       r_min=0.1, r_max=1.5 * R_max,
                                       skip_mask=star_mask)
  slope_rho, _ = fit_slope(centers, mean, fit_lo, fit_hi)
  # Analytic gradient from power-law fit: |d rho / d r| = |slope| * rho / r
  # So slope_grad = slope_rho - 1 (when rho is a clean power law).
  slope_grad_from_fit = slope_rho - 1.0 if np.isfinite(slope_rho) else float('nan')

  # Also do the Exp 128 analytic fit: rho(r) = A*(1/r - 1/R_eff)
  v = (mean > 0) & (centers >= 0.3) & (centers <= BOUNDARY_FRACTION * R_max)
  R_eff = float('nan'); A_fit = float('nan')
  if v.sum() >= 6:
    inv_r = 1.0 / centers[v]
    y = mean[v]
    A_fit, C = np.polyfit(inv_r, y, 1)
    if A_fit > 0 and C < 0:
      R_eff = -A_fit / C
  return centers, mean, slope_rho, slope_grad_from_fit, R_eff, A_fit


def analyse_and_plot(per_seed_results):
  """per_seed_results: list of (seed, centers, mean_rho_final, slope_rho, slope_grad, R_eff, R_max)."""
  print()
  print(f"{'seed':>5}  {'slope_rho':>10}  {'slope_grad_analytic':>20}  "
        f"{'R_eff':>7}  {'R_max':>7}")
  print("-" * 60)
  for seed, _, _, s_rho, s_grad, R_eff, R_max in per_seed_results:
    print(f"{seed:>5}  {s_rho:>10.3f}  {s_grad:>20.3f}  "
          f"{R_eff:>7.2f}  {R_max:>7.2f}")

  # Aggregate slopes
  slopes_rho = [r[3] for r in per_seed_results if np.isfinite(r[3])]
  slopes_grad = [r[4] for r in per_seed_results if np.isfinite(r[4])]
  if slopes_rho:
    print(f"\n  slope_rho  : mean={np.mean(slopes_rho):+.3f}  "
          f"std={np.std(slopes_rho):.3f}  (Newton 1/r target: -1.0)")
    print(f"  slope_grad : mean={np.mean(slopes_grad):+.3f}  "
          f"std={np.std(slopes_grad):.3f}  (Newton 1/r^2 target: -2.0)")

  fig, axes = plt.subplots(1, 2, figsize=(14, 5))
  colors = plt.cm.viridis(np.linspace(0, 1, len(per_seed_results)))

  # Use first seed's R_max as reference for refs line
  R_max_ref = per_seed_results[0][6]
  fit_lo = 0.5; fit_hi = 0.5 * R_max_ref

  for c_idx, (seed, centers, mean, s_rho, s_grad, R_eff, R_max) in enumerate(per_seed_results):
    axes[0].loglog(centers, np.maximum(mean, 1e-12), 'o-', color=colors[c_idx],
                   lw=1, ms=3,
                   label=f'seed={seed}  slope={s_rho:.2f}  R_eff={R_eff:.1f}')
    # Analytic gradient line: |slope| * rho / r
    with np.errstate(divide='ignore', invalid='ignore'):
      grad = np.abs(s_rho) * mean / centers
    axes[1].loglog(centers, np.maximum(grad, 1e-12), 's-', color=colors[c_idx],
                   lw=1, ms=3,
                   label=f'seed={seed}  slope={s_grad:.2f}')

  # Reference lines anchored on first seed's mid-range point
  _, centers0, mean0, *_ = per_seed_results[0]
  valid = (centers0 >= fit_lo) & (centers0 <= fit_hi) & (mean0 > 0)
  if valid.sum() > 0:
    anchor_idx = np.argmax(valid)
    r_anchor = centers0[anchor_idx]
    ref_r = np.array([fit_lo, fit_hi])
    for ax, p, lbl, anchor_y in [
        (axes[0], -1, '~ 1/r  (Newton)', mean0[anchor_idx]),
        (axes[1], -2, '~ 1/r^2 (Newton)', np.abs(-1) * mean0[anchor_idx] / r_anchor),
    ]:
      y_ref = anchor_y * (ref_r / r_anchor) ** p
      ax.plot(ref_r, y_ref, 'k--', alpha=0.5, lw=1.3, label=f'ref {lbl}')
      ax.axvspan(fit_lo, fit_hi, color='gray', alpha=0.08)

  axes[0].set_xlabel('r (spatial distance from star centroid)')
  axes[0].set_ylabel('mean rho(r)')
  axes[0].set_title('Phase 1 v2 - density rho(r) on lineage tree')
  axes[0].grid(True, which='both', alpha=0.3); axes[0].legend(fontsize=7)

  axes[1].set_xlabel('r')
  axes[1].set_ylabel('|d rho / d r|  (analytic from slope fit)')
  axes[1].set_title('Gradient (analytic)')
  axes[1].grid(True, which='both', alpha=0.3); axes[1].legend(fontsize=7)

  plt.suptitle(
    f'Exp 131 Phase 1 v2: k={BRANCHING}, D={DEPTH}, scale={SCALE:.2f}, '
    f'ticks={N_TICKS}, seeds={len(per_seed_results)}',
    fontsize=12)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase1_rho_profile.png')
  plt.savefig(path, dpi=140)
  plt.close()
  print(f"\n  saved: {path}")


# ------------------------------------------------------------------
#  Main
# ------------------------------------------------------------------

def run_one_seed(seed):
  pos, parent, level = build_tree(seed)
  N = len(pos)

  depth_nodes = np.where(level == STAR_DEPTH)[0]
  dists = np.linalg.norm(pos[depth_nodes], axis=1)
  order = np.argsort(dists)
  star_root = depth_nodes[order[len(order) // 2]]
  star_mask = get_descendants(parent, level, star_root)
  star_pos = pos[star_mask].mean(axis=0)
  r_max = float(np.linalg.norm(pos - star_pos, axis=1).max())

  print(f"  Star: subtree size = {int(star_mask.sum())}, centroid "
        f"{star_pos}, R_max = {r_max:.2f}")

  r_of = np.linalg.norm(pos - star_pos, axis=1)
  boundary_mask = r_of > BOUNDARY_FRACTION * r_max
  boundary_mask &= ~star_mask
  print(f"  Boundary: {int(boundary_mask.sum())} nodes "
        f"(of {N}, r > {BOUNDARY_FRACTION * r_max:.2f})")

  rho = np.zeros(N, dtype=np.float32)
  rho[star_mask] = 1.0

  neighbor_count, valid = prepare_neighbor_counts(parent)
  interior_mask = ~(star_mask | boundary_mask)

  t0 = time.time()
  last_report = t0
  last_mean = 0.0
  for tick in range(1, N_TICKS + 1):
    rho = propagate_step(rho, parent, valid, neighbor_count, star_mask, 1.0,
                         boundary_mask)
    if tick % 1000 == 0:
      now = time.time()
      tps = 1000 / max(0.001, now - last_report)
      last_report = now
      current = float(rho[interior_mask].mean())
      delta = current - last_mean
      last_mean = current
      print(f"    t={tick:5d}  interior_mean_rho={current:.6f}  "
            f"(delta={delta:+.6f})  ({tps:.0f} t/s)")
      sys.stdout.flush()
  print(f"  Done: {N_TICKS} ticks in {time.time() - t0:.1f}s")

  # Measurement on final rho only (steady-state-ish)
  centers, mean, slope_rho, slope_grad, R_eff, A_fit = measure_one_seed(
    pos, rho, star_mask, star_pos, r_max
  )
  return seed, centers, mean, slope_rho, slope_grad, R_eff, r_max


def run():
  per_seed_results = []
  for seed in SEEDS:
    print(f"\n=== Seed {seed} ===")
    per_seed_results.append(run_one_seed(seed))
  analyse_and_plot(per_seed_results)


if __name__ == '__main__':
  run()
