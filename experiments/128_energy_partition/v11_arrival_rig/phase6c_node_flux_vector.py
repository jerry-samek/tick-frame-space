#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 6c: Per-Node Net Flux Vector

Second observable on the Phase 1 graph. Phase 6b looked per edge and found
the radial/tangential net-flux ratio is a constant ~2.85, not the 1/(1-L_grav)
Schwarzschild radial factor.

Phase 6c looks per node. At each node i, the net outflow VECTOR is

    V[i] = sum over directed edges (i -> j) of
           (rho[i]/k[i] - rho[j]/k[j]) * e_hat(i,j)

where e_hat(i,j) is the unit vector pointing from i to j. V[i] measures
how directionally imbalanced the flow at i is. By symmetry around a point
source, V[i] should be radial (outward) on average with vanishing
tangential component.

Questions:
  1. Is V radial as expected? (<V . r_hat> > 0, <|V_tangential|> ~= 0)
  2. How does |V_radial| scale with r?
       - If ~1/r^2 (matches dρ/dr): same answer as Phase 6b, flat r-dependence
         when normalized by rho (~1/r): simple Newtonian gradient, no strong field.
       - If faster growth near source: strong field signature consistent with
         Schwarzschild radial factor.
  3. How does |V_radial|/rho compare to L_grav = rho/rho_scale?
       - Equal scaling (both 1/r): same Newton, no enhancement.
       - |V_radial|/rho grows faster than L_grav near source: Schwarzschild-like
         radial stretching IS present (just read through this observable).
"""

import os
import sys
import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_star_only import build_graph, propagate_step
import phase1_star_only as p1

p1.N_NODES = 100_000
p1.SPHERE_R = 60.0
p1.TARGET_K = 24
p1.STAR_COUNT = 50
p1.L_STAR = 1.0
p1.BOUNDARY_FRACTION = 0.95
p1.SEED = 42

PROP_TICKS = 2000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def measure_field():
  print("-- Phase 1 propagation (reused) --")
  pos, src, dst, degrees = build_graph()
  r_of = np.linalg.norm(pos, axis=1)
  star_ids = np.argsort(r_of)[:p1.STAR_COUNT]
  boundary_mask = r_of > p1.BOUNDARY_FRACTION * p1.SPHERE_R

  rho = np.zeros(p1.N_NODES, dtype=np.float32)
  rho[star_ids] = p1.L_STAR

  t0 = time.time()
  for tick in range(1, PROP_TICKS + 1):
    rho = propagate_step(rho, src, dst, degrees, p1.N_NODES)
    rho[star_ids] = p1.L_STAR
    rho[boundary_mask] = 0.0
    if tick % 500 == 0:
      interior = ~boundary_mask; interior[star_ids] = False
      print(f"  t={tick}  total={float(rho[interior].sum()):.1f}")
      sys.stdout.flush()
  print(f"  propagation: {time.time() - t0:.1f}s")
  return pos, r_of, rho, boundary_mask, star_ids, src, dst, degrees


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


def node_flux_vectors(pos, rho, src, dst, degrees):
  """For each directed edge (u -> v), contribution to V[u] is
       (rho[u]/k[u] - rho[v]/k[v]) * (p[v] - p[u]) / |p[v] - p[u]|
  Sum into V[u] via np.add.at (scatter-add).
  """
  d_safe = np.maximum(degrees, 1).astype(np.float32)
  flow_u = rho[src] / d_safe[src]
  flow_v = rho[dst] / d_safe[dst]
  weight = (flow_u - flow_v).astype(np.float32)   # scalar per edge

  vec = (pos[dst] - pos[src]).astype(np.float32)
  L = np.linalg.norm(vec, axis=1)
  safe = np.maximum(L, 1e-9)
  e_hat = vec / safe[:, None]

  contrib = weight[:, None] * e_hat              # (E, 3)
  V = np.zeros_like(pos, dtype=np.float32)
  np.add.at(V, src, contrib)
  return V


def analyse(pos, r_of, rho, boundary_mask, star_ids, V,
            bin_centers, mean_rho, rho_scale):
  interior = ~boundary_mask
  interior[star_ids] = False

  shells = [(3.0, 5.0), (5.0, 8.0), (8.0, 12.0),
            (12.0, 18.0), (18.0, 27.0), (27.0, 45.0)]

  # Per-node radial component and tangential magnitude
  r_hat = pos / np.maximum(r_of[:, None], 1e-9)
  V_rad = np.sum(V * r_hat, axis=1)              # signed (+outward)
  V_tan_vec = V - V_rad[:, None] * r_hat
  V_tan_mag = np.linalg.norm(V_tan_vec, axis=1)
  V_mag = np.linalg.norm(V, axis=1)

  print()
  print("  Per-node net-outflow vector V[i] = sum_j (rho[i]/k[i] - rho[j]/k[j]) * e_hat(i,j)")
  print()
  hdr = (f"  {'shell':<14} {'n_nodes':>8} {'<rho>':>8} "
         f"{'<V_rad>':>11} {'<|V_tan|>':>11} {'<|V|>':>10} "
         f"{'V_rad/rho':>10} {'L_grav':>8}")
  print(hdr); print("  " + "-" * (len(hdr) - 2))

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
    mean_Vmag = float(V_mag[m].mean())
    Vrad_over_rho = mean_Vrad / mean_rho_s if mean_rho_s > 0 else float('nan')
    Lg = mean_rho_s / rho_scale
    print(f"  r=[{r_lo:4.1f},{r_hi:4.1f}] {n:>8} {mean_rho_s:>8.4f} "
          f"{mean_Vrad:>11.4e} {mean_Vtan:>11.4e} {mean_Vmag:>10.4e} "
          f"{Vrad_over_rho:>10.4e} {Lg:>8.4f}")
    rows.append((mean_r, mean_rho_s, mean_Vrad, mean_Vtan, mean_Vmag,
                 Vrad_over_rho, Lg))

  # Scaling checks
  r_centers = np.array([r[0] for r in rows])
  V_rad_arr = np.array([r[2] for r in rows])
  V_tan_arr = np.array([r[3] for r in rows])
  V_rad_over_rho = np.array([r[5] for r in rows])
  Lg_arr = np.array([r[6] for r in rows])

  valid = (V_rad_arr > 0) & (r_centers > 0)
  slope_Vrad, _ = np.polyfit(np.log(r_centers[valid]),
                             np.log(V_rad_arr[valid]), 1)
  valid_vr = (V_rad_over_rho > 0) & (r_centers > 0)
  slope_VR, _ = np.polyfit(np.log(r_centers[valid_vr]),
                           np.log(V_rad_over_rho[valid_vr]), 1)
  valid_l = (Lg_arr > 0) & (r_centers > 0)
  slope_L, _ = np.polyfit(np.log(r_centers[valid_l]),
                          np.log(Lg_arr[valid_l]), 1)

  print()
  print(f"  power-law slope: <V_rad>  vs r  : {slope_Vrad:+.3f}   "
        f"(Newton expects -2)")
  print(f"  power-law slope: <V_rad>/<rho> vs r : {slope_VR:+.3f}   "
        f"(pure 1/r = -1 matches L_grav)")
  print(f"  power-law slope: L_grav vs r      : {slope_L:+.3f}   "
        f"(reference, expect -1)")

  # Enhancement over Newton: if V_rad/rho ∝ L_grav, they track identically.
  # If V_rad/rho grows faster than L_grav near source, strong-field signature.
  print()
  print(f"  {'r_c':>5} {'L_grav':>8} {'V_rad/rho':>12} "
        f"{'ratio (Vr/rho)/L_grav':>22} {'1/(1-L_grav)':>14}")
  print("  " + "-" * 66)
  for r_c, _, Vr, Vt, Vm, VrR, Lg in rows:
    ratio = VrR / Lg if Lg > 0 else float('nan')
    schwarz = 1.0 / (1.0 - Lg) if Lg < 1.0 else float('inf')
    print(f"  {r_c:>5.1f} {Lg:>8.4f} {VrR:>12.4e} "
          f"{ratio:>22.4f} {schwarz:>14.4f}")

  # Plots
  fig, axes = plt.subplots(1, 3, figsize=(18, 5))

  # A: |V_rad| and |V_tan| vs r on log-log
  ax = axes[0]
  ax.loglog(r_centers, V_rad_arr, 'ko-', lw=1.2, label='<V_rad> (radial outflow)')
  ax.loglog(r_centers, V_tan_arr, 's--', color='tab:blue', lw=1.0,
            label='<|V_tan|> (tangential leak)')
  # Reference 1/r^2
  y_ref = V_rad_arr[0] * (r_centers / r_centers[0]) ** -2
  ax.loglog(r_centers, y_ref, 'r:', lw=1, alpha=0.6, label='1/r^2 ref (Newton)')
  ax.set_xlabel('r_center'); ax.set_ylabel('<V> magnitude')
  ax.set_title(f'A: per-node net flux vector (slope fit {slope_Vrad:+.2f})')
  ax.grid(True, which='both', alpha=0.3); ax.legend(fontsize=8)

  # B: V_rad/rho vs r, compared to L_grav
  ax = axes[1]
  ax.loglog(r_centers, V_rad_over_rho, 'ko-', lw=1.2, label='<V_rad>/<rho>')
  ax.loglog(r_centers, Lg_arr, 'g--', lw=1, label='L_grav = rho/rho_scale')
  ax.set_xlabel('r_center'); ax.set_ylabel('value')
  ax.set_title('B: directional imbalance vs gravitational load')
  ax.grid(True, which='both', alpha=0.3); ax.legend(fontsize=8)

  # C: (V_rad/rho)/L_grav  compared to 1/(1-L_grav)
  ax = axes[2]
  ratio = np.array([r[5] / r[6] if r[6] > 0 else np.nan for r in rows])
  schwarz_arr = np.array([1.0 / (1.0 - r[6]) if r[6] < 1 else np.nan for r in rows])
  ax.plot(r_centers, ratio, 'ko-', lw=1.2, label='measured (V_rad/rho)/L_grav')
  ax.plot(r_centers, schwarz_arr, 'r--', lw=1.2, label='Schwarzschild 1/(1-L_grav)')
  ax.axhline(1.0, color='gray', ls=':', alpha=0.4, label='constant ratio (Newton)')
  ax.set_xlabel('r_center'); ax.set_ylabel('ratio')
  ax.set_title('C: strong-field enhancement check')
  ax.grid(True, alpha=0.3); ax.legend(fontsize=8)

  plt.suptitle('Phase 6c: per-node net flux vector (second observable)',
               fontsize=12)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase6c_node_flux_vector.png')
  plt.savefig(path, dpi=140)
  plt.close()
  print(f"\n  saved: {path}")


def run():
  (pos, r_of, rho, boundary_mask, star_ids,
   src, dst, degrees) = measure_field()
  bin_centers, mean_rho = bin_rho(r_of, rho, boundary_mask, star_ids)
  rho_scale = float(mean_rho.max()) * 2.0

  print()
  print("-- Building per-node net outflow vectors --")
  t0 = time.time()
  V = node_flux_vectors(pos, rho, src, dst, degrees)
  print(f"  per-node V built in {time.time()-t0:.1f}s")

  analyse(pos, r_of, rho, boundary_mask, star_ids, V,
          bin_centers, mean_rho, rho_scale)


if __name__ == '__main__':
  run()
