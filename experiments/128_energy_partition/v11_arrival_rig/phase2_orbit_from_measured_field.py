#!/usr/bin/env python3
"""
Experiment 128 v11 - Arrival Rig, Phase 2: Orbit from the Measured Field

Close the loop. Phase 1 measured the density profile of deposit propagation
on the graph and found a gradient scaling ~ r^-1.97. Phase 2 takes that
measured profile directly (not an analytical fit, not a Newtonian ansatz)
and drops it into the orbital ODE. The question:

  Do orbits close under the force the GRAPH actually delivers?

If yes: the full chain tick-frame -> graph propagation -> Kepler is
unbroken, with no faked link.

Pipeline:
  1. Build a 3D RGG and run pure propagation (same as Phase 1) until
     the inner profile is converged.
  2. Bin rho(r) into log-spaced radial shells. This is the graph's
     empirical potential.
  3. Build a smooth interpolator for rho(r) and its radial derivative.
     Force = -resistance * d(rho)/dr * r_hat (inward, since rho drops
     with r).
  4. Integrate a test planet's orbit under that force (leapfrog).
  5. Compare against a pure Newtonian 1/r^2 reference with the same
     effective coupling constant extracted from the graph fit.

This is the smallest honest test. The graph does the work; the ODE
is only the integrator.
"""

import os
import sys
import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Reuse Phase 1 graph + propagator
from phase1_star_only import build_graph, propagate_step

# -- Phase 1 parameters (overrides for speed - smoke-scale works fine) --
import phase1_star_only as p1
p1.N_NODES = 100_000
p1.SPHERE_R = 60.0
p1.TARGET_K = 24
p1.STAR_COUNT = 50
p1.L_STAR = 1.0
p1.BOUNDARY_FRACTION = 0.95
p1.SEED = 42

PROP_TICKS = 2000     # enough for inner profile to settle

# -- Orbit parameters --
RESISTANCE = 0.10     # planet consumes this fraction of local flux
INITIAL_R = 20.0      # starting orbital radius (well inside boundary)
DT = 0.01
STEPS = 600_000       # enough for many orbital periods

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


# ===================================================================
#  Step 1 & 2: propagate on graph, get rho(r) binned
# ===================================================================

def measure_field():
    print("-- Phase 1 measurement (reused) --")
    pos, src, dst, degrees = build_graph()
    r_of = np.linalg.norm(pos, axis=1)

    star_ids = np.argsort(r_of)[:p1.STAR_COUNT]
    boundary_mask = r_of > p1.BOUNDARY_FRACTION * p1.SPHERE_R

    rho = np.zeros(p1.N_NODES, dtype=np.float32)
    rho[star_ids] = p1.L_STAR

    t0 = time.time()
    last_total = 0.0
    for tick in range(1, PROP_TICKS + 1):
        rho = propagate_step(rho, src, dst, degrees, p1.N_NODES)
        rho[star_ids] = p1.L_STAR
        rho[boundary_mask] = 0.0
        if tick % 500 == 0:
            interior = ~boundary_mask
            interior[star_ids] = False
            total = float(rho[interior].sum())
            delta = total - last_total
            last_total = total
            print(f"  t={tick}  total={total:.1f}  delta/500={delta:.1f}")
            sys.stdout.flush()
    print(f"  propagation: {time.time()-t0:.1f}s")

    # Bin rho(r) with many bins for a smoother interpolator
    interior = ~boundary_mask
    interior[star_ids] = False
    r_min = 2.0
    r_max = p1.BOUNDARY_FRACTION * p1.SPHERE_R
    bin_edges = np.logspace(np.log10(r_min), np.log10(r_max), 60)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    mean_rho = np.zeros(len(bin_centers))
    counts = np.zeros(len(bin_centers), dtype=np.int64)
    for i in range(len(bin_centers)):
        m = (r_of >= bin_edges[i]) & (r_of < bin_edges[i+1]) & interior
        c = int(m.sum())
        counts[i] = c
        if c > 0:
            mean_rho[i] = rho[m].mean()

    # Also record the analytical fit (for reference comparison)
    v = mean_rho > 0
    A_fit, C_fit = np.polyfit(1.0 / bin_centers[v], mean_rho[v], 1)
    print(f"  analytic fit:  rho(r) ~ {A_fit:.3f}*(1/r) + {C_fit:.3f}  "
          f"(R_eff = {-A_fit/C_fit:.1f})")

    return bin_centers, mean_rho, A_fit


# ===================================================================
#  Step 3: smooth interpolator + radial derivative
# ===================================================================

def build_force_interpolator(bin_centers, mean_rho):
    """Return callables rho(r) and grad(r) from the binned profile.

    rho(r) is log-log interpolated between bins (monotone, smooth).
    grad(r) is the numerical derivative d rho / d r at the midpoints,
    then interpolated. Linear extrapolation near the edges.
    """
    valid = mean_rho > 0
    rc = bin_centers[valid]
    rv = mean_rho[valid]
    log_r = np.log(rc)
    log_rho = np.log(rv)

    def rho_of(r):
        return np.exp(np.interp(np.log(r), log_r, log_rho))

    # Finite-difference derivative in real space, at bin centers
    grad_mid_r = 0.5 * (rc[:-1] + rc[1:])
    grad_mid = (rv[1:] - rv[:-1]) / (rc[1:] - rc[:-1])   # negative
    log_gr = np.log(grad_mid_r)
    # magnitude in log space; keep sign separate (always negative here)
    log_absg = np.log(np.abs(grad_mid))

    def abs_grad_of(r):
        return np.exp(np.interp(np.log(r), log_gr, log_absg))

    return rho_of, abs_grad_of


# ===================================================================
#  Step 4: orbit integrator (leapfrog) under measured force
# ===================================================================

def integrate_orbit(force_fn, v_init, label):
    x, y = INITIAL_R, 0.0
    vx, vy = 0.0, v_init

    traj = np.empty((STEPS // 500 + 1, 4), dtype=np.float64)
    k = 0

    for step in range(STEPS):
        r = max(np.sqrt(x*x + y*y), 1e-6)
        rx, ry = x/r, y/r
        f_mag = force_fn(r)
        fx, fy = -f_mag * rx, -f_mag * ry       # inward

        vx += fx * DT
        vy += fy * DT
        x += vx * DT
        y += vy * DT

        if step % 500 == 0:
            traj[k] = (x, y, r, np.sqrt(vx*vx + vy*vy))
            k += 1
        # bail-outs
        if r > 3 * p1.SPHERE_R or r < 0.1:
            traj = traj[:k]
            return traj, label + " (diverged)"

    traj = traj[:k]
    return traj, label


# ===================================================================
#  Step 5: run and plot
# ===================================================================

def run():
    bin_centers, mean_rho, A_fit = measure_field()
    rho_of, abs_grad_of = build_force_interpolator(bin_centers, mean_rho)

    # Measured-field force: F_mag(r) = RESISTANCE * |d rho / d r|
    def F_measured(r):
        return RESISTANCE * float(abs_grad_of(r))

    # Reference 1/r^2 force: F_ref(r) = RESISTANCE * A_fit / r^2
    # (Using the same A from the graph fit so scales match.)
    def F_reference(r):
        return RESISTANCE * A_fit / (r * r)

    # Determine circular velocity at INITIAL_R under each force
    v_circ_meas = np.sqrt(F_measured(INITIAL_R) * INITIAL_R)
    v_circ_ref  = np.sqrt(F_reference(INITIAL_R) * INITIAL_R)
    print(f"\n-- Orbit setup --")
    print(f"  INITIAL_R       = {INITIAL_R}")
    print(f"  F_measured(r)   = {F_measured(INITIAL_R):.5f}")
    print(f"  F_reference(r)  = {F_reference(INITIAL_R):.5f}")
    print(f"  v_circ measured = {v_circ_meas:.5f}")
    print(f"  v_circ reference= {v_circ_ref:.5f}")

    runs = []
    for vt_frac in [1.0, 0.85, 1.15]:
        runs.append(integrate_orbit(
            F_measured,  v_circ_meas * vt_frac,
            f"measured,  vt={vt_frac}xv_c"))
        runs.append(integrate_orbit(
            F_reference, v_circ_ref * vt_frac,
            f"reference, vt={vt_frac}xv_c"))

    # Summary table
    print(f"\n{'label':<30} {'r_min':>7} {'r_max':>7} {'revs':>7}  status")
    print("-" * 72)
    for traj, label in runs:
        if len(traj) < 2:
            print(f"  {label:<28} (too short)")
            continue
        r = traj[:, 2]
        ang = np.unwrap(np.arctan2(traj[:, 1], traj[:, 0]))
        revs = (ang[-1] - ang[0]) / (2 * np.pi)
        status = "OK"
        if "diverged" in label: status = "DIVERGED"
        print(f"  {label:<28} {r.min():>7.2f} {r.max():>7.2f} "
              f"{revs:>7.1f}  {status}")

    plot(runs, bin_centers, mean_rho, A_fit)


def plot(runs, bin_centers, mean_rho, A_fit):
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3)

    # Panel A: density profile + fit
    ax = fig.add_subplot(gs[0, 0])
    valid = mean_rho > 0
    ax.loglog(bin_centers[valid], mean_rho[valid], 'bo-', ms=3, lw=0.8,
              label='measured rho(r)')
    rr = np.linspace(bin_centers[0], bin_centers[-1], 200)
    ax.loglog(rr, A_fit / rr, 'r--', lw=1, alpha=0.7, label=f'A/r fit (A={A_fit:.2f})')
    ax.set_xlabel('r'); ax.set_ylabel('rho(r)')
    ax.set_title('Density profile (graph-measured)')
    ax.legend(fontsize=8); ax.grid(True, which='both', alpha=0.3)

    # Panel B: gradient
    ax = fig.add_subplot(gs[0, 1])
    rc = bin_centers[valid]
    rv = mean_rho[valid]
    grad_mid_r = 0.5 * (rc[:-1] + rc[1:])
    grad_mid = np.abs((rv[1:] - rv[:-1]) / (rc[1:] - rc[:-1]))
    ax.loglog(grad_mid_r, grad_mid, 'go-', ms=3, lw=0.8, label='|drho/dr| measured')
    ax.loglog(rr, A_fit / rr**2, 'r--', lw=1, alpha=0.7, label='A/r^2 reference')
    ax.set_xlabel('r'); ax.set_ylabel('|drho/dr|')
    ax.set_title('Gradient (force magnitude / RESISTANCE)')
    ax.legend(fontsize=8); ax.grid(True, which='both', alpha=0.3)

    # Panel C: empty / notes
    ax = fig.add_subplot(gs[0, 2])
    ax.axis('off')
    notes = (
        "Phase 2: orbit under the measured field\n\n"
        f"N = {p1.N_NODES}, R = {p1.SPHERE_R}, <k> target = {p1.TARGET_K}\n"
        f"RESISTANCE = {RESISTANCE}\n"
        f"INITIAL_R  = {INITIAL_R}\n"
        f"STEPS = {STEPS}, DT = {DT}\n\n"
        "Each 'measured' trajectory uses F(r) = Rx|drho/dr(r)|\n"
        "interpolated from the binned graph profile.\n"
        "Each 'reference' uses F(r) = RxA/r^2 with the A extracted\n"
        "from the graph's analytic fit. Orbits should match if the\n"
        "graph really does produce 1/r^2.\n"
    )
    ax.text(0.02, 0.98, notes, family='monospace', fontsize=9,
            va='top', ha='left')

    # Bottom row: trajectories (measured vs reference, three vt fractions)
    trimmed = []
    for traj, label in runs:
        trimmed.append((traj, label))
    titles = ['vt = 1.0 x v_c', 'vt = 0.85 x v_c', 'vt = 1.15 x v_c']
    for col in range(3):
        ax = fig.add_subplot(gs[1, col])
        t_m, lab_m = trimmed[2*col]
        t_r, lab_r = trimmed[2*col + 1]
        lim = max(INITIAL_R * 1.5,
                  np.abs(t_m[:, :2]).max() if len(t_m) else INITIAL_R,
                  np.abs(t_r[:, :2]).max() if len(t_r) else INITIAL_R)
        lim = min(lim, 3 * p1.SPHERE_R)
        if len(t_m):
            ax.plot(t_m[:, 0], t_m[:, 1], '-', color='C0', lw=0.5,
                    alpha=0.8, label='measured')
        if len(t_r):
            ax.plot(t_r[:, 0], t_r[:, 1], '-', color='C3', lw=0.5,
                    alpha=0.6, label='reference')
        ax.plot(0, 0, 'y*', ms=10)
        ax.plot(INITIAL_R, 0, 'go', ms=4)
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
        ax.set_aspect('equal')
        ax.set_title(titles[col], fontsize=10)
        ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

    plt.suptitle('v11 Phase 2: orbits under the graph-measured field', fontsize=13)
    plt.tight_layout()
    out = os.path.join(OUT, 'phase2_orbit.png')
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"\nSaved: {out}")


if __name__ == '__main__':
    run()
