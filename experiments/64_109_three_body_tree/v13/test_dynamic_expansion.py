"""Task 2: Dynamic expansion test.

The real test of v13. Start with uniform edges. Let de/dt = H/(1+alpha*|gamma|)
build the edge profile during formation. Then run with geodesic frame rotation.
No hand-set profiles. No tuning.

The full chain: expansion -> asymmetric edges -> frame rotation -> orbit.
If this works, v13 is done and Result 6 is confirmed.

Usage:
    python test_dynamic_expansion.py [--H 0.01] [--alpha 1.0] [--side 40]
"""

import argparse
import math
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Import from macro_bodies
import sys
sys.path.insert(0, str(Path(__file__).parent))
from macro_bodies import (
    ContinuousGammaField, MacroBody, DIR_VECTORS,
    unwrap_coords, compute_angular_momentum,
    plot_edge_profile, RESULTS_DIR
)


def run_dynamic_test(side=40, G=10.0, H=0.001, alpha_expand=1.0,
                     star_mass=1000.0, planet_mass=1.0,
                     star_commit=999999, planet_commit=5,
                     deposit_strength=1.0, separation=10,
                     formation_ticks=5000, dynamics_ticks=30000,
                     tag='dynamic'):
    """Run the full chain: formation -> edge profile -> geodesic orbit."""

    print("=" * 70)
    print("DYNAMIC EXPANSION TEST")
    print("  Start uniform -> expand -> geodesic frame rotation -> orbit?")
    print("=" * 70)

    n = side ** 3
    body_ids = ['star', 'planet']
    field = ContinuousGammaField(n, k=6, G=G, H=H, alpha_expand=alpha_expand,
                                  body_ids=body_ids)

    cx, cy, cz = side // 2, side // 2, side // 2
    node_star = field.place_at_coords(cx, cy, cz)
    node_planet = field.place_at_coords(cx + separation, cy, cz)

    # Initialize star gamma well (large mass for deep well)
    field.initialize_peak('star', node_star, star_mass * 50, smooth_ticks=30)

    bodies = [
        MacroBody('star', node_star, mass=star_mass, commit_mass=star_commit,
                  deposit_strength=deposit_strength),
        MacroBody('planet', node_planet, mass=planet_mass,
                  commit_mass=planet_commit,
                  deposit_strength=deposit_strength * planet_mass / star_mass),
    ]
    bodies[1].internal_direction = np.array([0.0, 1.0, 0.0])  # tangential

    print(f"\n  Lattice: side={side}, N={field.n_nodes}")
    print(f"  Star: mass={star_mass}, commit={star_commit}")
    print(f"  Planet: mass={planet_mass}, commit={planet_commit}")
    print(f"  Separation: {separation} hops")
    print(f"  H={H}, alpha_expand={alpha_expand}")
    print(f"  Formation: {formation_ticks} ticks, Dynamics: {dynamics_ticks} ticks")

    # ===== PHASE A: Formation (edges expand, no body movement) =====
    print(f"\n  --- FORMATION ({formation_ticks} ticks) ---")
    t0 = time.time()
    for tick in range(formation_ticks):
        for body in bodies:
            field.deposit(body.node, body.bid,
                          body.mass * body.deposit_strength)
        field.spread()
        field.expand_edges()

        if (tick + 1) % max(formation_ticks // 5, 1) == 0:
            near_e = field.avg_edge_length(node_star)
            far_node = field.place_at_coords(0, 0, 0)
            far_e = field.avg_edge_length(far_node)
            planet_e = field.avg_edge_length(node_planet)
            print(f"    tick {tick+1:6d}: e_star={near_e:.4f}, "
                  f"e_planet={planet_e:.4f}, e_far={far_e:.4f}, "
                  f"ratio={far_e/max(near_e,1e-10):.2f}")

    elapsed_form = time.time() - t0
    print(f"  Formation done in {elapsed_form:.1f}s")

    # Measure edge profile
    profile = field.edge_profile_at(node_star, max_r=min(25, side // 2 - 1))
    print(f"\n  Edge profile after formation:")
    print(f"    {'r':>4s}  {'avg_e':>10s}  {'e_ratio':>10s}")
    r_keys = sorted(profile.keys())
    if r_keys:
        e_at_1 = profile.get(1, profile[r_keys[0]])
        for r in r_keys:
            if r <= 20:
                print(f"    {r:4d}  {profile[r]:10.4f}  {profile[r]/e_at_1:10.3f}")

    # Compute effective r_s from the edge profile
    # e(r) = e_far / (1 + r_s_eff / r)
    # At r=sep: e(sep)/e(far) = 1/(1 + r_s_eff/sep)
    # r_s_eff = sep * (e_far/e(sep) - 1)
    e_far = profile.get(max(r_keys), 1.0)
    e_at_sep = profile.get(separation, profile.get(separation - 1, e_far))
    if e_at_sep > 0 and e_far > e_at_sep:
        r_s_eff = separation * (e_far / e_at_sep - 1)
    else:
        r_s_eff = 0
    print(f"\n  Effective r_s at r={separation}: {r_s_eff:.2f}")
    print(f"  (e_far={e_far:.4f}, e_planet={e_at_sep:.4f})")

    # Predict tilt per hop at r=separation
    if r_s_eff > 0:
        tilt_pred = r_s_eff / (2 * separation * (separation + r_s_eff))
        total_tilt = 2 * math.pi * separation * tilt_pred
        print(f"  Predicted tilt per hop: {tilt_pred:.6f}")
        print(f"  Total tilt per orbit: {total_tilt:.3f} rad "
              f"(need 2pi={2*math.pi:.3f})")

    # Plot edge profile with Schwarzschild fit
    def theory_func(r):
        return e_far / (1.0 + r_s_eff / max(r, 0.1))

    plot_edge_profile(profile,
                      RESULTS_DIR / f'edge_profile_{tag}.png',
                      f'Edge Profile After Formation (H={H}, alpha={alpha_expand})',
                      theory_func=theory_func if r_s_eff > 0 else None)

    # ===== PHASE B: Dynamics with geodesic frame rotation =====
    print(f"\n  --- DYNAMICS ({dynamics_ticks} ticks, CASCADE mode) ---")

    # Reduce star deposit (well already formed)
    bodies[0].deposit_strength *= 0.001
    total_gamma = field.total_gamma()
    print(f"  Pre-dynamics gamma: {total_gamma:.0f}")

    # Diagnostic: tilt at planet position
    tilt_at_start = np.zeros(3)
    for ax in range(3):
        d_plus = ax * 2
        d_minus = ax * 2 + 1
        e_plus = field.edge_lengths[node_planet, d_plus]
        e_minus = field.edge_lengths[node_planet, d_minus]
        e_sum = e_plus + e_minus
        if e_sum > 0:
            tilt_at_start[ax] = -(e_plus - e_minus) / e_sum
    print(f"  Tilt at planet start: [{tilt_at_start[0]:.6f}, "
          f"{tilt_at_start[1]:.6f}, {tilt_at_start[2]:.6f}]")
    print(f"  |tilt| = {np.linalg.norm(tilt_at_start):.6f}")

    # Option: freeze edges during dynamics to isolate the test
    # (expanding edges during dynamics changes the profile continuously)
    field.H = 0.0  # Freeze edges — test the profile as-is
    print(f"  Edges FROZEN for dynamics (testing formed profile)")

    # Run cascade dynamics
    diag_interval = max(dynamics_ticks // 100, 1)
    record_interval = max(dynamics_ticks // 2000, 1)
    records = []
    ang_records = []
    tilt_samples = []  # (tick, r, |tilt|)

    t0 = time.time()
    for tick in range(dynamics_ticks):
        field.spread()
        for body in bodies:
            body.advance_cascade(field, tick, other_bodies=bodies)

        if (tick + 1) % record_interval == 0:
            for body in bodies:
                body.record(tick + 1, field)

        if (tick + 1) % diag_interval == 0:
            d = field.euclidean_distance(bodies[0].node, bodies[1].node)
            d_hop = field.hop_distance(bodies[0].node, bodies[1].node)
            records.append({'tick': tick + 1, 'd_AB': d, 'd_AB_hop': d_hop})

            L = compute_angular_momentum(bodies, field)
            L_total = sum(L.values())
            ang_records.append((tick + 1, L_total))

            # Sample tilt at planet
            planet_node = bodies[1].node
            tilt = np.zeros(3)
            for ax in range(3):
                d_plus = ax * 2
                d_minus = ax * 2 + 1
                e_plus = field.edge_lengths[planet_node, d_plus]
                e_minus = field.edge_lengths[planet_node, d_minus]
                e_sum = e_plus + e_minus
                if e_sum > 0:
                    tilt[ax] = -(e_plus - e_minus) / e_sum
            tilt_samples.append((tick + 1, d, np.linalg.norm(tilt)))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 10) == 0:
                print(f"    Tick {tick+1:7d}: d={d:.1f} (hop={d_hop}) "
                      f"|tilt|={np.linalg.norm(tilt):.6f} "
                      f"L={L_total:+.2f} ({elapsed:.1f}s)")

    # Results
    final_d = field.euclidean_distance(bodies[0].node, bodies[1].node)
    print(f"\n  Distance: {separation} -> {final_d:.1f}")
    print(f"  Hops: star={bodies[0].hops}, planet={bodies[1].hops}")

    if records:
        dists = [r['d_AB'] for r in records]
        print(f"  Range: [{min(dists):.1f}, {max(dists):.1f}]")
        reversals = sum(1 for i in range(2, len(dists))
                        if (dists[i] - dists[i-1]) * (dists[i-1] - dists[i-2]) < 0)
        print(f"  Reversals: {reversals}")

    # ===== PLOTS =====
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    # 1. Trajectory XY
    ax = axes[0, 0]
    s = field.side
    for body in bodies:
        if body.coord_history:
            uw = unwrap_coords(body.coord_history, s)
            xs = [c[1] for c in uw]
            ys = [c[2] for c in uw]
            ax.plot(xs, ys, '-', linewidth=0.5, alpha=0.7, label=body.bid)
            ax.plot(xs[0], ys[0], 'o', markersize=8)
            ax.plot(xs[-1], ys[-1], 's', markersize=6)
    ax.set_aspect('equal')
    ax.set_title('Trajectories (XY)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. Distance vs time
    ax = axes[0, 1]
    if records:
        ax.plot([r['tick'] for r in records], [r['d_AB'] for r in records],
                'b-', linewidth=0.8)
        ax.axhline(y=separation, color='gray', linestyle='--', alpha=0.4)
        ax.set_xlabel('Tick')
        ax.set_ylabel('Distance')
        ax.set_title(f'Distance (reversals={reversals})')
        ax.grid(True, alpha=0.3)

    # 3. Edge profile
    ax = axes[0, 2]
    rs_prof = sorted(profile.keys())
    es_prof = [profile[r] for r in rs_prof]
    ax.plot(rs_prof, es_prof, 'bo-', markersize=4, label='Measured')
    if r_s_eff > 0:
        r_th = np.linspace(1, max(rs_prof), 200)
        e_th = [theory_func(r) for r in r_th]
        ax.plot(r_th, e_th, 'r--', label=f'Fit: r_s_eff={r_s_eff:.1f}')
    ax.set_xlabel('Distance from star (hops)')
    ax.set_ylabel('Avg edge length')
    ax.set_title('Edge Profile')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. Angular momentum
    ax = axes[1, 0]
    if ang_records:
        ax.plot([r[0] for r in ang_records], [r[1] for r in ang_records],
                'r-', linewidth=0.8)
        ax.set_xlabel('Tick')
        ax.set_ylabel('L_z')
        ax.set_title('Angular Momentum')
        ax.grid(True, alpha=0.3)

    # 5. Tilt vs radius (from samples)
    ax = axes[1, 1]
    if tilt_samples:
        rs_t = [t[1] for t in tilt_samples]
        tilts_t = [t[2] for t in tilt_samples]
        ax.scatter(rs_t, tilts_t, s=2, alpha=0.3, c='blue')
        if r_s_eff > 0:
            r_th = np.linspace(1, max(rs_t) + 1, 200)
            t_th = r_s_eff / (2 * r_th * (r_th + r_s_eff))
            ax.plot(r_th, t_th, 'r-', linewidth=2, label=f'r_s_eff={r_s_eff:.1f}')
            ax.legend()
        ax.set_xlabel('Distance from star')
        ax.set_ylabel('|tilt|')
        ax.set_title('Tilt vs Radius (measured)')
        ax.grid(True, alpha=0.3)
        if max(tilts_t) > 10 * min(t for t in tilts_t if t > 0):
            ax.set_yscale('log')
            ax.set_xscale('log')

    # 6. Direction evolution
    ax = axes[1, 2]
    planet = bodies[1]
    if planet.coord_history and len(planet.coord_history) > 5:
        uw = unwrap_coords(planet.coord_history, s)
        v_ticks = []
        v_angles = []
        for i in range(1, len(uw)):
            dx = uw[i][1] - uw[i-1][1]
            dy = uw[i][2] - uw[i-1][2]
            if abs(dx) > 0 or abs(dy) > 0:
                angle = math.atan2(dy, dx) * 180 / math.pi
                v_ticks.append(uw[i][0])
                v_angles.append(angle)
        if v_angles:
            ax.plot(v_ticks, v_angles, '.', markersize=1, alpha=0.3)
            ax.set_xlabel('Tick')
            ax.set_ylabel('Velocity angle (deg)')
            ax.set_title('Direction Evolution')
            ax.grid(True, alpha=0.3)

    fig.suptitle(f'Dynamic Expansion: H={H}, alpha={alpha_expand}, '
                 f'M={star_mass}, r={separation}', fontsize=14, fontweight='bold')
    fig.tight_layout()
    out = RESULTS_DIR / f'dynamic_expansion_{tag}.png'
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"\n  Saved: {out}")

    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dynamic expansion test')
    parser.add_argument('--side', type=int, default=40)
    parser.add_argument('--H', type=float, default=0.001)
    parser.add_argument('--alpha', type=float, default=1.0)
    parser.add_argument('--star-mass', type=float, default=1000.0)
    parser.add_argument('--planet-mass', type=float, default=1.0)
    parser.add_argument('--planet-commit', type=int, default=5)
    parser.add_argument('--separation', type=int, default=10)
    parser.add_argument('--formation', type=int, default=5000)
    parser.add_argument('--dynamics', type=int, default=30000)
    parser.add_argument('--G', type=float, default=10.0)
    parser.add_argument('--tag', type=str, default='')
    args = parser.parse_args()

    tag = args.tag or f'H{args.H}_a{args.alpha}'
    run_dynamic_test(
        side=args.side, G=args.G, H=args.H, alpha_expand=args.alpha,
        star_mass=args.star_mass, planet_mass=args.planet_mass,
        planet_commit=args.planet_commit, separation=args.separation,
        formation_ticks=args.formation, dynamics_ticks=args.dynamics,
        tag=tag,
    )
