#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 6d: Proper-Time Discrepancy Under Our Ansatz

Phase 6c suggested that our substrate's radial observable V_rad/rho scales
like (1 - L_grav), not 1/(1 - L_grav) as Schwarzschild requires. If true,
the tick-frame ansatz for radial motion would be

    gamma_substrate = sqrt((1 - L_grav)^2 - v^2)          [ours, linear]

versus Schwarzschild radial:

    gamma_schwarz = sqrt((1 - L_grav) - v^2/(1 - L_grav))
                  = sqrt((1 - L_grav)^2 - v^2) / sqrt(1 - L_grav)

So by construction:

    gamma_substrate / gamma_schwarz == sqrt(1 - L_grav)

This script:

  1. Verifies that identity numerically on a grid of (r, v).
  2. Integrates a Newtonian radial free-fall trajectory (v = sqrt(2 L_grav)),
     and reports cumulative proper time under both gammas. Shows how much
     our ansatz under-counts proper time relative to Schwarzschild as the
     observer falls deeper.
  3. Plots.

Units: c = 1, use analytic L_grav(r) = rs/r where rs = 2 (Schwarzschild radius
in code units). This avoids re-running Phase 1 graph; the L_grav shape is
precisely what Phase 4 measured and Phase 6 used.
"""

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)

RS = 2.0   # Schwarzschild radius in natural units


def L_grav(r):
  return RS / r


def gamma_substrate(r, v):
  """Our ansatz: motion_capacity linear in (1 - L_grav)."""
  L = L_grav(r)
  inner = (1 - L) ** 2 - v * v
  return np.sqrt(np.maximum(0.0, inner))


def gamma_schwarz_radial(r, v):
  """Schwarzschild radial proper time formula."""
  L = L_grav(r)
  inner = (1 - L) - v * v / np.maximum(1 - L, 1e-12)
  return np.sqrt(np.maximum(0.0, inner))


def check_identity():
  """Verify gamma_substrate / gamma_schwarz = sqrt(1 - L_grav) on a grid."""
  rs_vals = np.linspace(2.2, 30.0, 40)      # keep r > RS
  vs_vals = np.linspace(0.0, 0.4, 12)       # sub-horizon velocities

  print("-- Identity check: gamma_sub / gamma_sch vs sqrt(1 - L_grav) --")
  print(f"{'r':>6} {'L_grav':>8} {'v':>6} "
        f"{'gamma_sub':>11} {'gamma_sch':>11} "
        f"{'ratio':>10} {'sqrt(1-Lg)':>11} {'err':>9}")
  print("-" * 80)

  # Sample a few representative points
  for r in [2.5, 3, 5, 10, 20]:
    for v in [0.0, 0.1, 0.2]:
      gs = float(gamma_substrate(r, v))
      gc = float(gamma_schwarz_radial(r, v))
      ratio = gs / gc if gc > 0 else float('nan')
      target = float(np.sqrt(1 - L_grav(r)))
      err = abs(ratio - target) / max(target, 1e-12) if np.isfinite(ratio) else float('nan')
      print(f"{r:>6.2f} {L_grav(r):>8.4f} {v:>6.2f} "
            f"{gs:>11.6f} {gc:>11.6f} "
            f"{ratio:>10.6f} {target:>11.6f} {err:>9.2e}")

  # Global numerical check
  RR, VV = np.meshgrid(rs_vals, vs_vals, indexing='ij')
  gs = gamma_substrate(RR, VV)
  gc = gamma_schwarz_radial(RR, VV)
  target = np.sqrt(1 - L_grav(RR))
  valid = (gc > 0) & (gs > 0)
  err = np.max(np.abs(gs[valid] / gc[valid] - target[valid]))
  print(f"\nmax |gamma_sub/gamma_sch - sqrt(1-L_grav)| over grid: {err:.2e}")
  return rs_vals, vs_vals, target


def integrate_infall(r0=30.0, r_stop=2.05, dt=1e-3, max_steps=2_000_000):
  """Schwarzschild radial free-fall from rest at infinity (coordinate velocity):

      v(r) = (1 - L_grav) * sqrt(L_grav)

  Stays sub-luminal for all r > r_s, unlike Newton's v = sqrt(2 L_grav)
  which exceeds c when L_grav > 0.5 (r < 2 r_s).

  We integrate coordinate time t along this trajectory and accumulate
  proper time under each gamma ansatz:

      tau_sub(t)   = integral gamma_substrate(r(t), v(t)) dt
      tau_schw(t)  = integral gamma_schwarz_radial(r(t), v(t)) dt

  The trajectory r(t) is defined by dr/dt = -v(r) (coordinate velocity).
  Same r(t) for both models; only the proper-time accumulations differ.
  """
  r = r0
  t = 0.0
  tau_sub = 0.0
  tau_sch = 0.0

  rec_t, rec_r, rec_v, rec_L = [], [], [], []
  rec_tau_sub, rec_tau_sch = [], []
  rec_g_sub, rec_g_sch = [], []

  for step in range(max_steps):
    Lr = L_grav(r)
    if Lr >= 1.0:
      break
    v = float((1 - Lr) * np.sqrt(Lr))   # Schwarzschild coord velocity, c = 1
    gs = float(gamma_substrate(r, v))
    gc = float(gamma_schwarz_radial(r, v))

    # Leapfrog-ish step in r
    tau_sub += gs * dt
    tau_sch += gc * dt
    t += dt
    r_new = r - v * dt

    if step % max(1, max_steps // 2000) == 0:
      rec_t.append(t); rec_r.append(r); rec_v.append(v); rec_L.append(Lr)
      rec_tau_sub.append(tau_sub); rec_tau_sch.append(tau_sch)
      rec_g_sub.append(gs); rec_g_sch.append(gc)

    r = r_new
    if r <= r_stop:
      break

  # Snap final record
  rec_t.append(t); rec_r.append(max(r, r_stop))
  rec_v.append(v); rec_L.append(L_grav(max(r, r_stop)))
  rec_tau_sub.append(tau_sub); rec_tau_sch.append(tau_sch)
  rec_g_sub.append(gs); rec_g_sch.append(gc)

  return {
    't': np.array(rec_t), 'r': np.array(rec_r), 'v': np.array(rec_v),
    'L': np.array(rec_L),
    'tau_sub': np.array(rec_tau_sub), 'tau_sch': np.array(rec_tau_sch),
    'g_sub': np.array(rec_g_sub), 'g_sch': np.array(rec_g_sch),
  }


def run():
  rs_vals, vs_vals, _ = check_identity()

  print()
  print("-- Radial free-fall: cumulative proper time --")
  print("   (Schwarzschild coord velocity v = (1-L) sqrt(L); RS = 2, r0 = 30, r_stop = 2.05)")
  sim = integrate_infall(r0=30.0, r_stop=2.05, dt=1e-3)

  print()
  print(f"{'r':>7} {'L_grav':>8} {'v':>7} "
        f"{'g_sub':>9} {'g_sch':>9} "
        f"{'tau_sub':>10} {'tau_sch':>10} {'d_tau':>10}")
  print("-" * 82)
  snapshots_r = [25, 15, 10, 7, 5, 4, 3, 2.5, 2.2, 2.1]
  for target_r in snapshots_r:
    idx = int(np.argmin(np.abs(sim['r'] - target_r)))
    r = sim['r'][idx]; Lr = sim['L'][idx]; v = sim['v'][idx]
    gs = sim['g_sub'][idx]; gc = sim['g_sch'][idx]
    ts = sim['tau_sub'][idx]; tc = sim['tau_sch'][idx]
    print(f"{r:>7.2f} {Lr:>8.4f} {v:>7.4f} "
          f"{gs:>9.5f} {gc:>9.5f} "
          f"{ts:>10.4f} {tc:>10.4f} {ts - tc:>10.4f}")

  final_ratio = sim['tau_sub'][-1] / sim['tau_sch'][-1]
  print()
  print(f"  final cumulative tau_substrate    = {sim['tau_sub'][-1]:.4f}")
  print(f"  final cumulative tau_schwarz      = {sim['tau_sch'][-1]:.4f}")
  print(f"  ratio tau_sub / tau_sch           = {final_ratio:.4f}")
  print(f"  coordinate time to fall r0 -> r_s = {sim['t'][-1]:.4f}")

  # Plot
  fig, axes = plt.subplots(2, 2, figsize=(14, 10))

  # A: trajectory r(t) and v(r)
  ax = axes[0, 0]
  ax.plot(sim['t'], sim['r'], 'k-', lw=1.2)
  ax.set_xlabel('coordinate time t'); ax.set_ylabel('r')
  ax.set_title('A: radial infall r(t)')
  ax.grid(True, alpha=0.3)
  ax.axhline(RS, color='r', ls='--', lw=1, alpha=0.6, label=f'r_s = {RS}')
  ax.legend(fontsize=8)

  # B: gammas along trajectory
  ax = axes[0, 1]
  ax.plot(sim['r'], sim['g_sub'], 'k-', lw=1.2, label='gamma_substrate (ours)')
  ax.plot(sim['r'], sim['g_sch'], 'r--', lw=1.2, label='gamma_schwarz (GR)')
  ax.set_xlabel('r'); ax.set_ylabel('gamma = d tau / dt')
  ax.set_title('B: proper-time rate along trajectory')
  ax.grid(True, alpha=0.3); ax.legend(fontsize=8)
  ax.set_xscale('log')

  # C: ratio vs L_grav, compared to sqrt(1 - L_grav)
  ax = axes[1, 0]
  ratio = sim['g_sub'] / np.maximum(sim['g_sch'], 1e-12)
  target = np.sqrt(np.maximum(0, 1 - sim['L']))
  ax.plot(sim['L'], ratio, 'ko', ms=3, label='measured g_sub / g_sch')
  ax.plot(sim['L'], target, 'r-', lw=1, label='sqrt(1 - L_grav)')
  ax.set_xlabel('L_grav'); ax.set_ylabel('ratio')
  ax.set_title('C: identity check (substrate / schwarz)')
  ax.grid(True, alpha=0.3); ax.legend(fontsize=8)

  # D: cumulative proper time under each, and their difference
  ax = axes[1, 1]
  ax.plot(sim['t'], sim['tau_sub'], 'k-', lw=1.2, label='tau_substrate')
  ax.plot(sim['t'], sim['tau_sch'], 'r--', lw=1.2, label='tau_schwarz')
  ax2 = ax.twinx()
  dtau = sim['tau_sch'] - sim['tau_sub']
  ax2.plot(sim['t'], dtau, 'b-', lw=1, alpha=0.6, label='tau_sch - tau_sub')
  ax.set_xlabel('coordinate time t'); ax.set_ylabel('cumulative proper time')
  ax2.set_ylabel('difference (tau_sch - tau_sub)', color='b')
  ax.set_title('D: cumulative proper time accumulated during infall')
  ax.grid(True, alpha=0.3); ax.legend(loc='upper left', fontsize=8)
  ax2.legend(loc='center right', fontsize=8)

  plt.suptitle(f'Phase 6d: proper-time discrepancy under (1 - L_grav) ansatz',
               fontsize=12)
  plt.tight_layout()
  path = os.path.join(OUT, 'phase6d_proper_time.png')
  plt.savefig(path, dpi=140)
  plt.close()
  print(f"\n  saved: {path}")


if __name__ == '__main__':
  run()
