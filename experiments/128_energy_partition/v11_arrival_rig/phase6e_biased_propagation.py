#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 6e: Per-Node Emission as Biased Propagation

Phases 6b/6c showed the flow on our isotropic-diffusion graph has radial
directionality but only by a constant geometric factor. Phase 6d showed
that reading the anisotropy linearly in (1 - L_grav) gives a proper-time
formula consistent with Schwarzschild × sqrt(1 - L_grav) -- off by one
power.

Hypothesis (user, 2026-04-17): Phase 1 propagation has the STAR as the
only active emitter; every other node just splits received rho uniformly.
But under "persistence ≡ ticking", each node also has a +1/tick budget
to spend -- if it spends that by firing along ONE connector, the
propagation rule is no longer pure isotropic diffusion.

Concrete test: replace the uniform rule

    rho_new[nbr] += rho[node] / degree[node]

with a mix

    rho_new[nbr] += rho[node] * w_eff[node, nbr]

where w_eff = (1 - beta) * (1/k) + beta * w_biased, and w_biased puts all
weight on lower-rho neighbors in proportion to (rho[u] - rho[v]). Mass is
conserved by construction (weights sum to 1).

Sweep beta ∈ {0, 0.3, 0.7, 1.0} and measure:
  1. Steady-state rho(r) -- does 1/r survive?
  2. Per-node net outflow V[i] and V_rad/rho per shell.
  3. (V_rad/rho) / L_grav vs L_grav -- curve flat (our linear ansatz),
     bending upward toward 1/(1-L_grav) (Schwarzschild), or something else.

Reference curves on the final plot:
  - (1 - L_grav)  : linear (our current observable, Phase 6c shape)
  - sqrt(1-L_grav): Schwarzschild complement
  - 1/(1-L_grav) : Schwarzschild g_rr direct
"""

import os
import sys
import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_star_only import build_graph
import phase1_star_only as p1

p1.N_NODES = 100_000
p1.SPHERE_R = 60.0
p1.TARGET_K = 24
p1.STAR_COUNT = 50
p1.L_STAR = 1.0
p1.BOUNDARY_FRACTION = 0.95
p1.SEED = 42

PROP_TICKS = 2000
BETAS = [0.0, 0.3, 0.7, 1.0]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def biased_propagate_step(rho, src, dst, degrees, n_nodes, beta):
  """One tick of mixed isotropic + gradient-biased propagation.

  beta=0: original Phase 1 uniform rule.
  beta=1: all outflow goes to lower-rho neighbors, weighted by pressure
          difference (rho[u] - rho[v]).
  In between: linear mix. Mass conserved per node.
  """
  d_safe = np.maximum(degrees, 1).astype(np.float32)

  # Uniform flow per directed edge = rho[u] / k[u]
  uniform_flow = (rho[src] / d_safe[src]).astype(np.float32)
  if beta <= 0.0:
    return np.bincount(dst, weights=uniform_flow, minlength=n_nodes).astype(np.float32)

  # Biased weights: positive gradient (u has more rho than v)
  diff = (rho[src] - rho[dst]).astype(np.float32)
  diff_pos = np.maximum(0.0, diff)

  # Sum of positive differences per source node
  sum_pos = np.zeros(n_nodes, dtype=np.float32)
  np.add.at(sum_pos, src, diff_pos)
  # Where sum_pos > 0, biased weight = diff_pos / sum_pos; else fallback uniform
  has_grad = sum_pos[src] > 1e-9
  biased_w = np.where(has_grad,
                      diff_pos / np.maximum(sum_pos[src], 1e-12),
                      1.0 / d_safe[src]).astype(np.float32)
  biased_flow = (rho[src] * biased_w).astype(np.float32)

  mixed = ((1.0 - beta) * uniform_flow + beta * biased_flow).astype(np.float32)
  return np.bincount(dst, weights=mixed, minlength=n_nodes).astype(np.float32)


def run_beta(beta, pos, src, dst, degrees, star_ids, boundary_mask):
  rho = np.zeros(p1.N_NODES, dtype=np.float32)
  rho[star_ids] = p1.L_STAR

  t0 = time.time()
  for tick in range(1, PROP_TICKS + 1):
    rho = biased_propagate_step(rho, src, dst, degrees, p1.N_NODES, beta)
    rho[star_ids] = p1.L_STAR
    rho[boundary_mask] = 0.0
    if tick % 500 == 0:
      interior = ~boundary_mask; interior[star_ids] = False
      print(f"    beta={beta:.1f}  t={tick}  total={float(rho[interior].sum()):.1f}")
      sys.stdout.flush()
  print(f"    propagation: {time.time() - t0:.1f}s")
  return rho


def bin_rho(r_of, rho, boundary_mask, star_ids):
  interior = ~boundary_mask; interior[star_ids] = False
  edges = np.logspace(np.log10(2.0),
                      np.log10(p1.BOUNDARY_FRACTION * p1.SPHERE_R), 40)
  centers = np.sqrt(edges[:-1] * edges[1:])
  mean = np.zeros(len(centers))
  for i in range(len(centers)):
    m = (r_of >= edges[i]) & (r_of < edges[i+1]) & interior
    if m.sum() > 0:
      mean[i] = rho[m].mean()
  return centers, mean


def node_flux_vectors(pos, rho, src, dst, degrees, beta, M):
  """Per-node signed flux vector V[n] = sum over incident edges of
     NET_flow × e_hat(n -> other), same structure as Phase 6c.

  NET_flow on edge (u, v) = flow_uv - flow_vu under the mixed rule.
  For beta=0 this reduces to Phase 6c exactly.

  src/dst contain each undirected edge TWICE: first M entries are forward
  (u -> v), last M are reverse (v -> u). reverse_idx pairs each directed
  edge with its reverse counterpart to compute NET flow.
  """
  d_safe = np.maximum(degrees, 1).astype(np.float32)
  uniform_flow = (rho[src] / d_safe[src]).astype(np.float32)

  if beta <= 0.0:
    flow_uv = uniform_flow
  else:
    diff = (rho[src] - rho[dst]).astype(np.float32)
    diff_pos = np.maximum(0.0, diff)
    sum_pos = np.zeros(p1.N_NODES, dtype=np.float32)
    np.add.at(sum_pos, src, diff_pos)
    has_grad = sum_pos[src] > 1e-9
    biased_w = np.where(has_grad,
                        diff_pos / np.maximum(sum_pos[src], 1e-12),
                        1.0 / d_safe[src]).astype(np.float32)
    biased_flow = (rho[src] * biased_w).astype(np.float32)
    flow_uv = ((1.0 - beta) * uniform_flow + beta * biased_flow).astype(np.float32)

  # Reverse index: forward edge at position i pairs with reverse at i + M
  # reverse edge at position i (>= M) pairs with forward at i - M
  idx = np.arange(2 * M)
  reverse_idx = np.where(idx < M, idx + M, idx - M)
  net = (flow_uv - flow_uv[reverse_idx]).astype(np.float32)

  vec = (pos[dst] - pos[src]).astype(np.float32)
  L = np.linalg.norm(vec, axis=1)
  e_hat = vec / np.maximum(L, 1e-9)[:, None]

  contrib = net[:, None] * e_hat
  V = np.zeros_like(pos, dtype=np.float32)
  np.add.at(V, src, contrib)
  return V


def analyse(beta, rho, pos, r_of, V, boundary_mask, star_ids,
            bin_centers, mean_rho, rho_scale, shells):
  interior = ~boundary_mask; interior[star_ids] = False

  r_hat = pos / np.maximum(r_of[:, None], 1e-9)
  V_rad = np.sum(V * r_hat, axis=1)
  V_tan_vec = V - V_rad[:, None] * r_hat
  V_tan_mag = np.linalg.norm(V_tan_vec, axis=1)

  rows = []
  for (r_lo, r_hi) in shells:
    m = (r_of >= r_lo) & (r_of < r_hi) & interior
    n = int(m.sum())
    if n == 0:
      continue
    mean_r = 0.5 * (r_lo + r_hi)
    mean_rho_s = float(rho[m].mean())
    mean_Vrad = float(V_rad[m].mean())
    mean_Vtan = float(V_tan_mag[m].mean())
    Vrad_over_rho = mean_Vrad / mean_rho_s if mean_rho_s > 0 else float('nan')
    Lg = mean_rho_s / rho_scale
    rows.append((mean_r, mean_rho_s, mean_Vrad, mean_Vtan,
                 Vrad_over_rho, Lg))
  return rows


def run():
  print("-- Build graph --")
  pos, src, dst, degrees = build_graph()
  r_of = np.linalg.norm(pos, axis=1)
  star_ids = np.argsort(r_of)[:p1.STAR_COUNT]
  boundary_mask = r_of > p1.BOUNDARY_FRACTION * p1.SPHERE_R

  shells = [(3.0, 5.0), (5.0, 8.0), (8.0, 12.0),
            (12.0, 18.0), (18.0, 27.0), (27.0, 45.0)]

  results = {}
  density_profiles = {}
  for beta in BETAS:
    print(f"\n-- beta = {beta} --")
    rho = run_beta(beta, pos, src, dst, degrees, star_ids, boundary_mask)
    bin_centers, mean_rho = bin_rho(r_of, rho, boundary_mask, star_ids)
    rho_scale = float(mean_rho.max()) * 2.0
    print(f"    rho_scale = {rho_scale:.4f}")

    print("    -- Build V --")
    M = len(src) // 2
    V = node_flux_vectors(pos, rho, src, dst, degrees, beta, M)

    rows = analyse(beta, rho, pos, r_of, V, boundary_mask, star_ids,
                   bin_centers, mean_rho, rho_scale, shells)
    results[beta] = rows
    density_profiles[beta] = (bin_centers, mean_rho, rho_scale)

    # Print per-shell table
    print(f"    {'shell':<14} {'<rho>':>8} {'L_grav':>8} "
          f"{'<V_rad>':>11} {'V_rad/rho':>11} {'(Vr/rho)/Lg':>12}")
    print("    " + "-" * 70)
    for mean_r, mean_rho_s, Vrad, Vtan, VrR, Lg in rows:
      ratio = VrR / Lg if Lg > 0 else float('nan')
      print(f"    r={mean_r:>5.1f}       {mean_rho_s:>8.4f} {Lg:>8.4f} "
            f"{Vrad:>11.4e} {VrR:>11.4e} {ratio:>12.4f}")

  # ── Plots ─────────────────────────────────────────────────────────
  fig, axes = plt.subplots(2, 2, figsize=(14, 11))

  # A: density profiles rho(r) for each beta (does 1/r survive?)
  ax = axes[0, 0]
  colors = plt.cm.viridis(np.linspace(0, 1, len(BETAS)))
  for (beta, color) in zip(BETAS, colors):
    bc, mr, _ = density_profiles[beta]
    ax.loglog(bc, np.maximum(mr, 1e-6), 'o-', color=color, lw=1, ms=3,
              label=f'beta={beta}')
  # Reference 1/r
  bc0 = density_profiles[0.0][0]
  mr0 = density_profiles[0.0][1]
  ref = mr0[5] * (bc0 / bc0[5]) ** -1
  ax.loglog(bc0, ref, 'k--', lw=1, alpha=0.5, label='1/r ref')
  ax.set_xlabel('r'); ax.set_ylabel('mean rho(r)')
  ax.set_title('A: steady-state rho(r) for each beta')
  ax.grid(True, which='both', alpha=0.3); ax.legend(fontsize=8)

  # B: V_rad/rho vs r
  ax = axes[0, 1]
  for (beta, color) in zip(BETAS, colors):
    rows = results[beta]
    rs = np.array([r[0] for r in rows])
    vrs = np.array([r[4] for r in rows])
    ax.loglog(rs, np.maximum(vrs, 1e-6), 'o-', color=color, lw=1, ms=5,
              label=f'beta={beta}')
  ax.set_xlabel('r_center'); ax.set_ylabel('<V_rad>/<rho>')
  ax.set_title('B: directional imbalance per beta')
  ax.grid(True, which='both', alpha=0.3); ax.legend(fontsize=8)

  # C: (V_rad/rho) / L_grav vs L_grav, compared to reference curves
  ax = axes[1, 0]
  L_grid = np.linspace(0.02, 0.95, 200)
  ax.plot(L_grid, 1.0 - L_grid, 'g:', lw=1.2, label='(1 - L_grav) [our linear]')
  ax.plot(L_grid, np.sqrt(1.0 - L_grid), 'b:', lw=1.2,
          label='sqrt(1 - L_grav) [half-step]')
  ax.plot(L_grid, 1.0 / (1.0 - L_grid), 'r:', lw=1.2,
          label='1/(1 - L_grav) [Schwarzschild g_rr]')
  for (beta, color) in zip(BETAS, colors):
    rows = results[beta]
    Lg = np.array([r[5] for r in rows])
    VrR = np.array([r[4] for r in rows])
    # Normalize each series so it starts at 1 at the outermost shell (weak field)
    idx_outer = np.argmin(Lg)
    ratio = (VrR / Lg)
    if ratio[idx_outer] > 0:
      ratio = ratio / ratio[idx_outer]
    ax.plot(Lg, ratio, 'o-', color=color, lw=1, ms=5,
            label=f'beta={beta} (normalized)')
  ax.set_xlabel('L_grav')
  ax.set_ylabel('(V_rad/rho)/L_grav, normalized to weak-field')
  ax.set_title('C: curve shape vs reference metrics')
  ax.set_yscale('log'); ax.grid(True, which='both', alpha=0.3)
  ax.legend(fontsize=7, loc='upper left')

  # D: density-slope fit vs beta (how much does biased rule distort 1/r?)
  ax = axes[1, 1]
  slopes = []
  for beta in BETAS:
    bc, mr, _ = density_profiles[beta]
    # Fit slope in mid-range
    fit_mask = (bc >= 5.0) & (bc <= 30.0) & (mr > 0)
    if fit_mask.sum() >= 4:
      s, _ = np.polyfit(np.log(bc[fit_mask]), np.log(mr[fit_mask]), 1)
    else:
      s = float('nan')
    slopes.append(s)
  ax.plot(BETAS, slopes, 'ko-', lw=1.5, ms=8)
  ax.axhline(-1.0, color='r', ls='--', lw=1, alpha=0.5, label='Newton 1/r (-1)')
  ax.set_xlabel('beta (bias fraction)')
  ax.set_ylabel('fitted power-law slope of rho(r)')
  ax.set_title('D: does bias distort the Poisson profile?')
  ax.grid(True, alpha=0.3); ax.legend(fontsize=8)

  plt.suptitle('Phase 6e: biased propagation -- per-node +1/tick emission',
               fontsize=12)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase6e_biased_propagation.png')
  plt.savefig(path, dpi=140)
  plt.close()
  print(f"\n  saved: {path}")


if __name__ == '__main__':
  run()
