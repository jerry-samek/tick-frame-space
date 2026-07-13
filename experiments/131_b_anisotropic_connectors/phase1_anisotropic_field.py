#!/usr/bin/env python3
"""
Experiment 132 Phase 1 — Self-Consistent Anisotropic Field on RGG

Builds the v11-style 3D random geometric graph with a static star at the
origin. Per-edge propagation rate depends on local field:

  L         = min(rho_avg / rho_scale, L_max)
  cos²θ     = (ê_edge · ∇̂ρ)²              (1 = radial, 0 = tangential)
  stretch   = sqrt(cos²θ × 1/(1−L) + (1−cos²θ))   (Pythagorean blend)
  rate      = 1 / stretch

Per-edge flow each tick: rho[src] × rate / total_rate[src] (mass-conserving;
falls back to v11's uniform-1/degree when all rates are 1).

Iteration: propagate field with current rates → recompute ∇ρ at every node
→ recompute rates → damp → repeat. Stops when interior_mean's relative
change between iterations drops below CONVERGE_TOL or N_ITERATIONS hits.

Measures: rho(r) profile, per-shell <cos²θ> weighted by edge midpoint,
per-shell mean stretch vs the 1/sqrt(1−L) target.
"""

import os, sys, time
import numpy as np
from scipy.spatial import cKDTree

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Graph
N_NODES = 100_000
SPHERE_R = 60.0
TARGET_K = 24
SEED = 42

# Source / boundary
STAR_COUNT = 50
L_STAR = 1.0
BOUNDARY_FRACTION = 0.95

# Anisotropy rule
RHO_SCALE = 1.0
L_MAX = 0.95

# Iteration scheme
N_ITERATIONS = 30
TICKS_PER_ITER = 400
DAMPING = 0.3
CONVERGE_TOL = 1e-3   # relative change in interior_mean

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def build_graph():
  rng = np.random.default_rng(SEED)
  pts = []
  while len(pts) < N_NODES:
    batch = rng.uniform(-SPHERE_R, SPHERE_R, (N_NODES * 2, 3))
    good = batch[np.linalg.norm(batch, axis=1) <= SPHERE_R]
    pts.extend(good.tolist())
  pos = np.array(pts[:N_NODES], dtype=np.float32)
  rc = SPHERE_R * (TARGET_K / N_NODES) ** (1.0 / 3.0)
  pairs = cKDTree(pos).query_pairs(rc, output_type='ndarray').astype(np.int32)
  src = np.concatenate([pairs[:, 0], pairs[:, 1]]).astype(np.int32)
  dst = np.concatenate([pairs[:, 1], pairs[:, 0]]).astype(np.int32)
  edge_vec = (pos[dst] - pos[src]).astype(np.float32)
  edge_len = np.linalg.norm(edge_vec, axis=1).astype(np.float32)
  edge_dir = (edge_vec / np.maximum(edge_len[:, None], 1e-10)).astype(np.float32)
  return pos, src, dst, edge_dir, edge_len


def propagate_step(rho, src, dst, edge_rate, total_rate, n_nodes,
                   star_ids, star_value, boundary_mask):
  safe = np.maximum(total_rate, 1e-10)
  flow = (rho[src] * edge_rate / safe[src]).astype(np.float32)
  rho_new = np.bincount(dst, weights=flow, minlength=n_nodes).astype(np.float32)
  rho_new[star_ids] = star_value
  rho_new[boundary_mask] = 0.0
  return rho_new


def compute_node_gradient(rho, src, dst, edge_dir, edge_len, n_nodes):
  """∇ρ[n] ≈ mean over outgoing edges (n→m) of (ρ[m]−ρ[n]) × ê_{nm} / |edge|.
  Crude per-node finite-difference estimate; sufficient to define orientation."""
  delta = (rho[dst] - rho[src]).astype(np.float32)
  contrib = ((delta / np.maximum(edge_len, 1e-10))[:, None]
             * edge_dir).astype(np.float32)
  grad = np.zeros((n_nodes, 3), dtype=np.float32)
  for d in range(3):
    grad[:, d] = np.bincount(src, weights=contrib[:, d], minlength=n_nodes)
  deg = np.bincount(src, minlength=n_nodes).astype(np.float32)
  grad /= np.maximum(deg, 1.0)[:, None]
  return grad


def compute_edge_rates(rho, grad, src, dst, edge_dir, rho_scale, L_max):
  rho_avg = ((rho[src] + rho[dst]) * 0.5).astype(np.float32)
  L = np.minimum(rho_avg / rho_scale, L_max)
  grad_avg = ((grad[src] + grad[dst]) * 0.5).astype(np.float32)
  grad_norm = np.linalg.norm(grad_avg, axis=1)
  has_grad = grad_norm > 1e-8
  cos2 = np.zeros(len(src), dtype=np.float32)
  if has_grad.any():
    g_dir = grad_avg[has_grad] / grad_norm[has_grad, None]
    cos2[has_grad] = np.einsum('ij,ij->i', edge_dir[has_grad], g_dir) ** 2
  inv = 1.0 / (1.0 - L)
  stretch = np.sqrt(cos2 * inv + (1.0 - cos2)).astype(np.float32)
  rate = (1.0 / np.maximum(stretch, 1e-10)).astype(np.float32)
  return rate, cos2.astype(np.float32), L.astype(np.float32)


def run():
  print(f"Phase 1: anisotropic RGG, N={N_NODES}, R={SPHERE_R}, k={TARGET_K}")
  print(f"  rho_scale={RHO_SCALE}  L_max={L_MAX}")
  print(f"  outer iters={N_ITERATIONS}  ticks/iter={TICKS_PER_ITER}  "
        f"damping={DAMPING}  tol={CONVERGE_TOL}")
  t0 = time.time()
  pos, src, dst, edge_dir, edge_len = build_graph()
  r_of = np.linalg.norm(pos, axis=1)
  print(f"  built graph in {time.time()-t0:.1f}s, {len(src)} directed edges, "
        f"avg_k={len(src)/N_NODES:.1f}")

  star_ids = np.argsort(r_of)[:STAR_COUNT]
  boundary_mask = r_of > BOUNDARY_FRACTION * SPHERE_R
  interior = ~boundary_mask; interior[star_ids] = False
  print(f"  star r_max={r_of[star_ids].max():.2f}  "
        f"boundary nodes={int(boundary_mask.sum())}  "
        f"interior nodes={int(interior.sum())}")

  edge_rate = np.ones(len(src), dtype=np.float32)
  total_rate = np.bincount(src, weights=edge_rate, minlength=N_NODES).astype(np.float32)
  rho = np.zeros(N_NODES, dtype=np.float32)
  rho[star_ids] = L_STAR

  history = []
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

    interior_mean = float(rho[interior].mean())
    edge_in = interior[src] & interior[dst]
    mean_L = float(L_e[edge_in].mean())
    mean_cos2 = float(cos2_e[edge_in].mean())
    mean_rate = float(edge_rate[edge_in].mean())
    rel_change = abs(interior_mean - prev_mean) / max(interior_mean, 1e-10)
    history.append((it, interior_mean, mean_L, mean_cos2, mean_rate, rel_change))
    print(f"  iter {it:2d}: mean_rho={interior_mean:.4f}  rel_d={rel_change:.5f}  "
          f"<L>={mean_L:.4f}  <cos2>={mean_cos2:.4f}  <rate>={mean_rate:.4f}  "
          f"({time.time()-t_iter:.1f}s)")
    sys.stdout.flush()
    if rel_change < CONVERGE_TOL and it >= 5:
      print(f"  converged (rel_change < {CONVERGE_TOL})")
      break
    prev_mean = interior_mean

  print(f"\nTotal: {time.time()-t0:.1f}s")
  measure_and_plot(pos, r_of, rho, src, dst, edge_rate, cos2_e, L_e,
                   star_ids, boundary_mask, history)


def measure_and_plot(pos, r_of, rho, src, dst, edge_rate, cos2, L,
                     star_ids, boundary_mask, history):
  interior = ~boundary_mask; interior[star_ids] = False
  r_min, r_max = 2.0, 0.9 * SPHERE_R
  bin_edges = np.logspace(np.log10(r_min), np.log10(r_max), 25)
  bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])

  mean_rho = np.zeros(len(bin_centers))
  for i in range(len(bin_centers)):
    m = (r_of >= bin_edges[i]) & (r_of < bin_edges[i + 1]) & interior
    if m.sum() > 0:
      mean_rho[i] = rho[m].mean()

  edge_r = np.linalg.norm((pos[src] + pos[dst]) * 0.5, axis=1)
  edge_inner = interior[src] & interior[dst]
  stretch = 1.0 / np.maximum(edge_rate, 1e-10)
  mean_cos2_shell = np.zeros(len(bin_centers))
  mean_stretch_shell = np.zeros(len(bin_centers))
  mean_L_shell = np.zeros(len(bin_centers))
  for i in range(len(bin_centers)):
    m = (edge_r >= bin_edges[i]) & (edge_r < bin_edges[i + 1]) & edge_inner
    if m.sum() > 0:
      mean_cos2_shell[i] = cos2[m].mean()
      mean_stretch_shell[i] = stretch[m].mean()
      mean_L_shell[i] = L[m].mean()

  fit_lo, fit_hi = 4.0, 0.5 * SPHERE_R
  fit_mask = (bin_centers >= fit_lo) & (bin_centers <= fit_hi) & (mean_rho > 0)
  slope = float('nan')
  if fit_mask.sum() >= 4:
    slope, _ = np.polyfit(np.log(bin_centers[fit_mask]),
                          np.log(mean_rho[fit_mask]), 1)
  with np.errstate(divide='ignore', invalid='ignore'):
    grad_rho = np.abs(np.gradient(mean_rho, bin_centers))
  slope_g = float('nan')
  vg = fit_mask & (grad_rho > 0) & np.isfinite(grad_rho)
  if vg.sum() >= 4:
    slope_g, _ = np.polyfit(np.log(bin_centers[vg]), np.log(grad_rho[vg]), 1)

  print(f"\nFit [{fit_lo}, {fit_hi}]:")
  print(f"  slope_rho  = {slope:+.3f}  (v11 baseline: -1.27 at this size)")
  print(f"  slope_grad = {slope_g:+.3f}  (v11 baseline: -1.97)")
  print(f"\nPer-shell anisotropy summary (edges with midpoint in shell):")
  print(f"  {'r':>6}  {'<cos2>':>8}  {'<stretch>':>10}  {'1/sqrt(1-L)':>12}  {'<L>':>7}")
  for i in range(len(bin_centers)):
    if mean_L_shell[i] > 0:
      target = 1.0 / np.sqrt(max(1.0 - mean_L_shell[i], 1e-10))
      print(f"  {bin_centers[i]:>6.2f}  {mean_cos2_shell[i]:>8.4f}  "
            f"{mean_stretch_shell[i]:>10.4f}  {target:>12.4f}  "
            f"{mean_L_shell[i]:>7.4f}")

  fig, axes = plt.subplots(2, 2, figsize=(14, 10))

  ax = axes[0, 0]
  ax.loglog(bin_centers, np.maximum(mean_rho, 1e-12), 'o-')
  if fit_mask.sum() > 0:
    ref_r = np.array([fit_lo, fit_hi])
    a_idx = np.argmax(fit_mask)
    ax.plot(ref_r, mean_rho[a_idx] * (ref_r / bin_centers[a_idx]) ** -1,
            'k--', alpha=0.5, label='~ 1/r')
    ax.axvspan(fit_lo, fit_hi, color='gray', alpha=0.08)
  ax.set_xlabel('r'); ax.set_ylabel('mean rho(r)')
  ax.set_title(f'rho(r), slope={slope:+.2f}')
  ax.legend(); ax.grid(True, which='both', alpha=0.3)

  ax = axes[0, 1]
  ax.semilogx(bin_centers, mean_cos2_shell, 'o-')
  ax.axhline(1.0 / 3.0, color='k', linestyle='--', alpha=0.5,
             label='isotropic = 1/3')
  ax.set_xlabel('r'); ax.set_ylabel('<cos^2 theta_edge>')
  ax.set_title('per-shell anisotropy (>1/3 = radial alignment)')
  ax.legend(); ax.grid(True, which='both', alpha=0.3)

  ax = axes[1, 0]
  ax.semilogx(bin_centers, mean_stretch_shell, 'o-', label='measured <stretch>')
  v = mean_L_shell > 0
  if v.sum() > 0:
    target = 1.0 / np.sqrt(np.maximum(1.0 - mean_L_shell, 1e-10))
    ax.semilogx(bin_centers[v], target[v], 'r--',
                label='1/sqrt(1-L) (radial endpoint)')
  ax.set_xlabel('r'); ax.set_ylabel('mean stretch in shell')
  ax.set_title('shell-mean stretch vs radial-Schwarzschild target')
  ax.legend(); ax.grid(True, which='both', alpha=0.3)

  ax = axes[1, 1]
  if history:
    h = np.array(history)
    ax.plot(h[:, 0], h[:, 1] / max(h[-1, 1], 1e-10), 'o-', label='mean rho (norm)')
    ax.plot(h[:, 0], h[:, 2] / max(h[-1, 2], 1e-10), 's-', label='mean L (norm)')
    ax.plot(h[:, 0], h[:, 4], '^-', label='mean rate')
  ax.set_xlabel('iteration'); ax.set_ylabel('value')
  ax.set_title('iteration convergence')
  ax.legend(); ax.grid(True, alpha=0.3)

  plt.suptitle(f'Exp 132 Phase 1: anisotropic RGG, N={N_NODES} R={SPHERE_R} '
               f'rho_scale={RHO_SCALE}', fontsize=11)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase1_anisotropic_field.png')
  plt.savefig(path, dpi=130); plt.close()
  print(f"\nSaved: {path}")


if __name__ == '__main__':
  run()
