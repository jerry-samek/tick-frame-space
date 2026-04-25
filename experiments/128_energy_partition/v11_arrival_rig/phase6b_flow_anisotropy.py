#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 6b: Flow Anisotropy on an Isotropic Graph

Phase 6 measured the GEOMETRIC anisotropy of graph connectors (<cos^2 theta_r>
per shell). It came out ~0.33 everywhere -- graph is geometrically isotropic,
so Phase 6 concluded the substrate can't produce the Schwarzschild radial
stretching factor 1/(1 - L_grav) without changes to connector topology.

Phase 6b re-examines that conclusion under the "persistence = ticking" reading.
Even on a geometrically isotropic graph, the *flow* of deposits is not
isotropic: the star is localized, so net per-tick transport points outward
radially. Tangential edges carry near-zero net flux; radial edges carry all
the current.

If "local tick cost" is tied to the NET flow a connector has to transport
(rather than to the connector's static length), then radial connectors are
DYNAMICALLY stretched by their flow burden, even though they're geometrically
identical to tangential ones. That is the anisotropy Schwarzschild demands.

This script measures, at steady state of the Phase 1 propagation:

  per edge (i,j):
    phi_gross = (rho[i]/k[i] + rho[j]/k[j]) / 2    (traffic per direction)
    phi_net   = | rho[i]/k[i] - rho[j]/k[j] |       (net transport per tick)
    cos2      = (e_hat . r_hat_mid)^2
    r_mid     = midpoint distance from star

Bins: (r-shell) x (cos^2 bin: radial / oblique / tangential).

Outputs:
  1. phi_gross per bin (expect flat over cos^2 -- isotropy of propagation)
  2. phi_net   per bin (expect high on radial, ~0 on tangential)
  3. phi_net / phi_gross per bin (DIRECTIONALITY of flow)
  4. Compare radial/tangential ratio of directionality to 1/(1 - L_grav),
     Schwarzschild's radial stretching factor.
"""

import os
import sys
import time
import numpy as np
from scipy.spatial import cKDTree

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


def undirected_edges(src, dst):
  """src/dst contain each undirected edge twice as (a->b, b->a).
  Return unique undirected (a,b) with a<b."""
  a = np.minimum(src, dst)
  b = np.maximum(src, dst)
  key = a.astype(np.int64) * (int(1 << 32)) + b.astype(np.int64)
  _, first_idx = np.unique(key, return_index=True)
  return src[first_idx], dst[first_idx]  # one representative per undirected


def analyse(pos, r_of, rho, boundary_mask, star_ids,
            src_u, dst_u, degrees, rho_scale):
  """Per-edge measurements."""
  # Filter out edges touching star or boundary (endpoints we control)
  keep = ~(boundary_mask[src_u] | boundary_mask[dst_u])
  star_mask = np.zeros(len(pos), dtype=bool); star_mask[star_ids] = True
  keep &= ~(star_mask[src_u] | star_mask[dst_u])
  i = src_u[keep]; j = dst_u[keep]

  d_safe = np.maximum(degrees, 1).astype(np.float32)
  flow_i = rho[i] / d_safe[i]    # per-direction outflow from i (per tick)
  flow_j = rho[j] / d_safe[j]

  phi_gross = 0.5 * (flow_i + flow_j)
  phi_net = np.abs(flow_i - flow_j)

  # Edge midpoint and direction
  pi = pos[i]; pj = pos[j]
  mid = 0.5 * (pi + pj)
  r_mid = np.linalg.norm(mid, axis=1)
  r_hat = mid / np.maximum(r_mid[:, None], 1e-9)
  e_vec = pj - pi
  e_len = np.linalg.norm(e_vec, axis=1)
  e_hat = e_vec / np.maximum(e_len[:, None], 1e-9)
  cos2 = (np.sum(e_hat * r_hat, axis=1)) ** 2

  # Guard: drop edges with r_mid < 2 or > 0.9 * R (match bin_rho domain)
  ok = (r_mid >= 2.0) & (r_mid <= 0.9 * p1.SPHERE_R) & (e_len > 0)
  r_mid = r_mid[ok]; cos2 = cos2[ok]
  phi_gross = phi_gross[ok]; phi_net = phi_net[ok]

  # r-shells
  r_edges = np.array([3.0, 5.0, 8.0, 12.0, 18.0, 27.0, 45.0])
  shells = list(zip(r_edges[:-1], r_edges[1:]))

  # cos^2 bins
  cos2_bins = [
    ("tangential", 0.00, 1.0/3.0),
    ("oblique",    1.0/3.0, 2.0/3.0),
    ("radial",     2.0/3.0, 1.01),
  ]

  print()
  print(f"  rho_scale = {rho_scale:.4f}")
  print()
  hdr = (f"  {'shell':<12} {'bin':<12} {'n_edges':>8} "
         f"{'<cos2>':>7} {'<phi_gross>':>12} {'<phi_net>':>12} "
         f"{'net/gross':>10}")
  print(hdr); print("  " + "-" * (len(hdr) - 2))

  # Table: rows = shells, columns = cos2 bins, values = net/gross
  table_ng = np.zeros((len(shells), len(cos2_bins)))
  table_gross = np.zeros((len(shells), len(cos2_bins)))
  table_net = np.zeros((len(shells), len(cos2_bins)))
  Lgrav_of_shell = np.zeros(len(shells))

  for si, (r_lo, r_hi) in enumerate(shells):
    shell_mask = (r_mid >= r_lo) & (r_mid < r_hi)
    r_center = 0.5 * (r_lo + r_hi)
    # Rough L_grav(r_center) from measured rho profile (later below)
    for bi, (name, c_lo, c_hi) in enumerate(cos2_bins):
      m = shell_mask & (cos2 >= c_lo) & (cos2 < c_hi)
      n = int(m.sum())
      if n == 0:
        print(f"  r=[{r_lo:4.1f},{r_hi:4.1f}] {name:<12} {n:>8} "
              f"{'--':>7} {'--':>12} {'--':>12} {'--':>10}")
        continue
      mean_cos2 = float(cos2[m].mean())
      mean_gross = float(phi_gross[m].mean())
      mean_net = float(phi_net[m].mean())
      ng = mean_net / mean_gross if mean_gross > 0 else float('nan')
      print(f"  r=[{r_lo:4.1f},{r_hi:4.1f}] {name:<12} {n:>8} "
            f"{mean_cos2:>7.3f} {mean_gross:>12.3e} {mean_net:>12.3e} "
            f"{ng:>10.3e}")
      table_ng[si, bi] = ng
      table_gross[si, bi] = mean_gross
      table_net[si, bi] = mean_net

  print()
  print("  -- Directionality ratio: radial / tangential --")
  print(f"  {'shell':<12} {'r_c':>5} {'L_grav':>8} "
        f"{'ng_radial':>11} {'ng_tangential':>14} "
        f"{'ratio':>8} {'1/(1-Lg)':>10}")
  print("  " + "-" * 76)
  return shells, cos2_bins, table_ng, table_gross, table_net


def lgrav_at(r, bin_centers, mean_rho, rho_scale):
  v = np.interp(r, bin_centers, mean_rho, left=mean_rho[0], right=0.0)
  return float(v) / rho_scale


def run():
  (pos, r_of, rho, boundary_mask, star_ids,
   src, dst, degrees) = measure_field()
  bin_centers, mean_rho = bin_rho(r_of, rho, boundary_mask, star_ids)
  rho_scale = float(mean_rho.max()) * 2.0

  src_u, dst_u = undirected_edges(src, dst)

  shells, cos2_bins, table_ng, table_gross, table_net = analyse(
    pos, r_of, rho, boundary_mask, star_ids,
    src_u, dst_u, degrees, rho_scale,
  )

  # Continue directionality-ratio table
  rad_idx = [i for i, cb in enumerate(cos2_bins) if cb[0] == "radial"][0]
  tan_idx = [i for i, cb in enumerate(cos2_bins) if cb[0] == "tangential"][0]
  rows = []
  for si, (r_lo, r_hi) in enumerate(shells):
    r_c = 0.5 * (r_lo + r_hi)
    Lg = lgrav_at(r_c, bin_centers, mean_rho, rho_scale)
    ng_r = table_ng[si, rad_idx]
    ng_t = table_ng[si, tan_idx]
    ratio = ng_r / ng_t if ng_t > 0 else float('nan')
    schwarz = 1.0 / (1.0 - Lg) if Lg < 1.0 else float('inf')
    print(f"  r=[{r_lo:4.1f},{r_hi:4.1f}] {r_c:>5.1f} {Lg:>8.4f} "
          f"{ng_r:>11.3e} {ng_t:>14.3e} {ratio:>8.2f} {schwarz:>10.3f}")
    rows.append((r_c, Lg, ng_r, ng_t, ratio, schwarz))

  # ── Plots ────────────────────────────────────────────────────────────
  fig, axes = plt.subplots(1, 3, figsize=(18, 5))

  # A: phi_gross vs cos^2 bin, per shell  -- isotropy check
  ax = axes[0]
  colors = plt.cm.viridis(np.linspace(0, 1, len(shells)))
  bin_names = [cb[0] for cb in cos2_bins]
  xs = np.arange(len(cos2_bins))
  for si, (r_lo, r_hi) in enumerate(shells):
    ax.plot(xs, table_gross[si, :], 'o-', color=colors[si], lw=1,
            label=f'r=[{r_lo:.0f},{r_hi:.0f}]')
  ax.set_xticks(xs); ax.set_xticklabels(bin_names)
  ax.set_ylabel('mean phi_gross (per-tick traffic)')
  ax.set_title('A: gross flow per direction bin (expect ~flat)')
  ax.set_yscale('log'); ax.grid(True, which='both', alpha=0.3)
  ax.legend(fontsize=7, ncol=2)

  # B: phi_net vs cos^2 bin, per shell  -- anisotropy check
  ax = axes[1]
  for si, (r_lo, r_hi) in enumerate(shells):
    ax.plot(xs, table_net[si, :], 'o-', color=colors[si], lw=1,
            label=f'r=[{r_lo:.0f},{r_hi:.0f}]')
  ax.set_xticks(xs); ax.set_xticklabels(bin_names)
  ax.set_ylabel('mean phi_net (per-tick net transport)')
  ax.set_title('B: net flow per direction bin (radial >> tangential expected)')
  ax.set_yscale('log'); ax.grid(True, which='both', alpha=0.3)
  ax.legend(fontsize=7, ncol=2)

  # C: radial/tangential directionality ratio vs Schwarzschild 1/(1-Lg)
  ax = axes[2]
  rc = np.array([r[0] for r in rows])
  Lg = np.array([r[1] for r in rows])
  ratio = np.array([r[4] for r in rows])
  schwarz = np.array([r[5] for r in rows])
  ax.semilogy(rc, ratio, 'ko-', lw=1.2, ms=6, label='measured rad/tan (net/gross)')
  ax.semilogy(rc, schwarz, 'r--', lw=1.2, label='Schwarzschild 1/(1-L_grav)')
  ax.set_xlabel('r_center (shell midpoint)')
  ax.set_ylabel('ratio')
  ax.set_title('C: directionality ratio vs Schwarzschild radial factor')
  ax.grid(True, which='both', alpha=0.3)
  ax.legend(fontsize=9)

  plt.suptitle('Phase 6b: flow anisotropy on a geometrically isotropic graph',
               fontsize=12)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase6b_flow_anisotropy.png')
  plt.savefig(path, dpi=140)
  plt.close()
  print(f"\n  saved: {path}")


if __name__ == '__main__':
  run()
