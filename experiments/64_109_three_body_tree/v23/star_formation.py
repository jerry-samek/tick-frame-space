"""v23: Larger Graph Domain — Closing the Orbit.

Carries v22's validated mechanics (leapfrog force, true 3D displacement,
local hop threshold with floor) into a larger domain (80k nodes, radius=45).

Uses v21 graph infrastructure.

Usage:
    python -u v23/star_formation.py --phase0 --ticks 5000 --weighted-spread
    python -u v23/star_formation.py --measure-force --weighted-spread
    python -u v23/star_formation.py --phase2 --ticks 30000 --weighted-spread --tag orbit

March 2026
"""

import argparse
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Import graph + entity from v21
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'v21'))
from macro_bodies import RandomGeometricGraph, Entity

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


FORCE_UPDATE_INTERVAL = 10  # ticks between force reads


class DiskParticle(Entity):
    """Ring/disk particle: deposits gamma, feels TOTAL field (star + disk).

    Leapfrog integrator: force updates every FORCE_UPDATE_INTERVAL ticks,
    displacement every tick.  Decouples force rate from hop rate.
    """

    def __init__(self, bid, node, mass=100.0, deposit_rate=1e-5,
                 inertia=10.0, force_coeff=1.0, radiate_mass=True,
                 force_interval=FORCE_UPDATE_INTERVAL, **kwargs):
        super().__init__(bid, node, mass=mass, deposit_rate=deposit_rate,
                         inertia=inertia, stationary=False,
                         radiate_mass=radiate_mass, **kwargs)
        self.force_coeff = force_coeff
        self.force_interval = force_interval
        self.displacement_3d = np.zeros(3)

    def advance(self, graph, tick=None):
        # --- Deposit gamma from all body nodes ---
        deposited = self.mass * self.deposit_rate
        n_body_nodes = len(self.nodes)
        deposit_per_node = deposited / n_body_nodes
        for n in self.nodes:
            graph.deposit(n, self.bid, deposit_per_node)
        if self.radiate_mass:
            self.mass = max(self.mass - deposited, 0.0)

        # --- Leapfrog force: every N ticks, decoupled from hops ---
        if graph.H > 0 and tick is not None and tick % self.force_interval == 0:
            nbs = graph.node_neighbors[self.node]
            if nbs:
                growths = []
                conn_data = []
                for nb, eidx in nbs:
                    g_a = abs(graph.gamma[self.node])
                    g_b = abs(graph.gamma[nb])
                    growth = graph.H / (1.0 + graph.alpha_expand * (g_a + g_b))
                    growths.append(growth)
                    conn_data.append((nb, eidx, growth))
                mean_growth = sum(growths) / len(growths)

                accel = np.zeros(3)
                for nb, eidx, growth in conn_data:
                    push = self.force_coeff * (mean_growth - growth) / self.inertia
                    direction = graph.connector_direction(self.node, nb)
                    accel += direction * push

                self.velocity += accel

        # --- v22: true 3D displacement, no projection blind spots ---
        self.displacement_3d += self.velocity

        conn_list = graph.node_neighbors[self.node]
        if not conn_list:
            return False

        # --- Hop when |displacement_3d| >= local hop threshold ---
        hop_floor = graph.initial_mean_edge * 0.5
        hop_threshold = max(graph.avg_edge_length_at(self.node), hop_floor)
        moved = False
        max_hops_per_tick = 10
        hops_this_tick = 0
        while hops_this_tick < max_hops_per_tick:
            disp_mag = np.linalg.norm(self.displacement_3d)
            if disp_mag < hop_threshold:
                break

            # Find connector most aligned with displacement direction
            disp_dir = self.displacement_3d / disp_mag
            best_nb, best_eidx = max(
                conn_list,
                key=lambda x: np.dot(disp_dir, graph.connector_direction(self.node, x[0]))
            )

            # Subtract hop from displacement
            hop_dir = graph.connector_direction(self.node, best_nb)
            self.displacement_3d -= hop_dir * hop_threshold

            old_node = self.node
            graph.move_gamma(self.bid, old_node, best_nb)
            self.node = best_nb
            self.hops += 1
            hops_this_tick += 1
            moved = True
            if tick is not None:
                self.hop_log.append((tick, hop_threshold, disp_mag, hop_threshold))

            # Update conn_list and hop_threshold for new node
            conn_list = graph.node_neighbors[self.node]
            hop_threshold = max(graph.avg_edge_length_at(self.node), hop_floor)

        return moved


class TestParticle(Entity):
    """Test particle with continuous force accumulation.

    Unlike v21 Entity (force-on-hop only), this applies force every tick
    with a configurable coefficient.  Prevents the bootstrap deadlock where
    a stationary particle can never reach its first hop.
    """

    def __init__(self, bid, node, inertia=10.0, force_coeff=0.01, **kwargs):
        super().__init__(bid, node, mass=0.0, deposit_rate=0.0,
                         inertia=inertia, stationary=False,
                         radiate_mass=False, **kwargs)
        self.force_coeff = force_coeff

    def advance(self, graph, tick=None):
        # No deposit (test particle)

        # --- Continuous force: every tick, not just on hop ---
        if graph.H > 0:
            connectors = graph.growth_at_node_external(self.node, self.bid)
            if connectors:
                growths = [g for _, _, g in connectors]
                mean_growth = sum(growths) / len(growths)

                accel = np.zeros(3)
                for nb, eidx, growth in connectors:
                    push = self.force_coeff * (mean_growth - growth) / self.inertia
                    direction = graph.connector_direction(self.node, nb)
                    accel += direction * push

                self.velocity += accel

        # --- Velocity -> displacement: best-aligned connector ---
        conn_list = graph.node_neighbors[self.node]
        if not conn_list:
            return False

        best_nb = None
        best_proj = -float('inf')
        for nb, eidx in conn_list:
            direction = graph.connector_direction(self.node, nb)
            v_proj = float(np.dot(self.velocity, direction))
            if v_proj > best_proj:
                best_proj = v_proj
                best_nb = nb

        if best_nb is not None:
            self.disp[best_nb] = self.disp.get(best_nb, 0.0) + abs(best_proj)

        # --- Hop when displacement >= hop_threshold ---
        hop_threshold = graph.initial_mean_edge
        moved = False
        max_hops_per_tick = 10
        hops_this_tick = 0
        while hops_this_tick < max_hops_per_tick:
            best_nb = None
            best_disp = 0.0
            for nb, val in self.disp.items():
                if val > best_disp:
                    best_disp = val
                    best_nb = nb
            if best_disp < hop_threshold:
                break

            self.disp[best_nb] -= hop_threshold
            old_node = self.node
            graph.move_gamma(self.bid, old_node, best_nb)
            self._transfer_displacement(graph, old_node, best_nb)
            self.node = best_nb
            self.hops += 1
            hops_this_tick += 1
            moved = True
            if tick is not None:
                local_edges = [graph.edge_lengths[eidx]
                               for _, eidx in graph.node_neighbors[self.node]]
                local_mean = np.mean(local_edges) if local_edges else 0.0
                self.hop_log.append((tick, local_mean, best_proj, hop_threshold))

        return moved


def radial_profile(graph, center_node, n_bins=30, r_max=None):
    """Compute mean gamma in radial shells around center_node.

    Returns (bin_centers, mean_gamma, node_counts) arrays.
    """
    center_pos = graph.positions[center_node]
    dists = np.linalg.norm(graph.positions - center_pos, axis=1)
    if r_max is None:
        r_max = float(np.max(dists))
    edges = np.linspace(0, r_max, n_bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    mean_g = np.zeros(n_bins)
    counts = np.zeros(n_bins, dtype=int)
    for i in range(n_bins):
        mask = (dists >= edges[i]) & (dists < edges[i + 1])
        counts[i] = int(np.sum(mask))
        if counts[i] > 0:
            mean_g[i] = float(np.mean(graph.gamma[mask]))
    return centers, mean_g, counts


def phase0(n_nodes=30000, k=24, H=0.01, alpha_expand=1.0,
           star_mass=100000.0, deposit_strength=1e-5,
           ticks=5000, seed=42, radius=30.0,
           body_base_radius=5.0, body_ref_mass=100000.0,
           weighted_spread=False, tag=''):
    print("=" * 70)
    print("v22 PHASE 0: Star Formation — Gamma Gradient")
    print("=" * 70)

    graph = RandomGeometricGraph(n_nodes, k=k, G=0.0, H=H,
                                  alpha_expand=alpha_expand,
                                  seed=seed, body_ids=['star'],
                                  radius=radius,
                                  weighted_spread=weighted_spread)

    center = graph.nearest_node(np.array([0.0, 0.0, 0.0]))
    star_body_radius = body_base_radius * (star_mass / body_ref_mass) ** (1.0 / 3.0)

    star = Entity('star', center, mass=star_mass,
                  deposit_rate=deposit_strength,
                  inertia=1.0, stationary=True,
                  radiate_mass=True,
                  graph=graph, body_radius=star_body_radius)

    e0_mean = np.mean(graph.edge_lengths)
    print(f"\n  Graph: N={n_nodes}, k={k}, mean_edge={e0_mean:.2f}")
    print(f"  Star: mass={star_mass}, node={center}, body_radius={star_body_radius:.2f}, "
          f"body_nodes={len(star.nodes)}")
    print(f"  Deposit/tick={star_mass * deposit_strength:.2f}")
    print(f"  Half-life={0.693 / deposit_strength:.0f} ticks")
    print(f"  H={H}, weighted_spread={weighted_spread}")

    # Snapshot schedule: every 1000 ticks + early snapshots
    snapshot_ticks = sorted(set(
        [100, 500] + list(range(1000, ticks + 1, 1000))
    ))
    snapshot_ticks = [t for t in snapshot_ticks if t <= ticks]
    profiles = {}
    prev_ratio = None

    t0 = time.time()
    for tick in range(ticks):
        # Deposit from all body nodes (same as advance() for stationary body)
        deposited = star.mass * star.deposit_rate
        n_body_nodes = len(star.nodes)
        deposit_per_node = deposited / n_body_nodes
        for n in star.nodes:
            graph.deposit(n, star.bid, deposit_per_node)
        if star.radiate_mass:
            star.mass = max(star.mass - deposited, 0.0)

        graph.spread()
        graph.expand_edges()

        if (tick + 1) in snapshot_ticks:
            elapsed = time.time() - t0
            a_scale = np.mean(graph.edge_lengths) / e0_mean
            centers, mean_g, counts = radial_profile(
                graph, center, n_bins=30, r_max=radius)
            profiles[tick + 1] = (centers, mean_g, counts, a_scale)

            # Print probe values at key radii
            peak = float(graph.gamma[center])
            probes = [5.0, 10.0, 15.0, 20.0]
            probe_str = ""
            probe_vals = {}
            for pr in probes:
                idx = np.argmin(np.abs(centers - pr))
                probe_vals[pr] = mean_g[idx]
                probe_str += f" r={pr}:{mean_g[idx]:.4f}"
            ratio_10_5 = probe_vals[10.0] / probe_vals[5.0] if probe_vals[5.0] > 0 else 0.0
            delta_str = ""
            if prev_ratio is not None:
                delta = ratio_10_5 - prev_ratio
                eq_mark = " <-- EQ" if abs(delta) < 0.005 else ""
                delta_str = f" d/1k={delta:+.4f}{eq_mark}"
            prev_ratio = ratio_10_5
            print(f"    Tick {tick+1:6d}: mass={star.mass:.1f} a={a_scale:.2f} "
                  f"peak={peak:.2f}{probe_str} "
                  f"g10/g5={ratio_10_5:.4f}{delta_str} ({elapsed:.1f}s)")

    # ---- Plots ----
    suffix = f"_{tag}" if tag else ""

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 1) Linear radial profile at each snapshot
    ax = axes[0]
    for t, (centers, mean_g, counts, a_scale) in sorted(profiles.items()):
        ax.plot(centers, mean_g, '-', linewidth=1.5, label=f't={t} (a={a_scale:.1f})')
    ax.set_xlabel('Distance from star (Euclidean)')
    ax.set_ylabel('Mean gamma')
    ax.set_title('Gamma vs Distance (linear)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2) Log-log with 1/r reference
    ax = axes[1]
    last_t = max(profiles.keys())
    for t, (centers, mean_g, counts, a_scale) in sorted(profiles.items()):
        mask = mean_g > 0
        if np.any(mask):
            ax.loglog(centers[mask], mean_g[mask], 'o-', markersize=4,
                      linewidth=1.2, label=f't={t}')
    # 1/r reference anchored at r=5 of last snapshot
    _, last_g, _, _ = profiles[last_t]
    idx5 = np.argmin(np.abs(centers - 5.0))
    if last_g[idx5] > 0:
        r_ref = np.linspace(2, radius - 2, 50)
        g_ref = last_g[idx5] * 5.0 / r_ref
        ax.loglog(r_ref, g_ref, 'k--', alpha=0.4, label='1/r reference')
    ax.set_xlabel('Distance (log)')
    ax.set_ylabel('Gamma (log)')
    ax.set_title('Gamma Profile (log-log)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 3) Node density per shell (sanity check)
    ax = axes[2]
    _, _, last_counts, _ = profiles[last_t]
    ax.bar(centers, last_counts, width=(centers[1] - centers[0]) * 0.8,
           alpha=0.7, color='steelblue')
    ax.set_xlabel('Distance from star')
    ax.set_ylabel('Node count per shell')
    ax.set_title('Node Density (sanity check)')
    ax.grid(True, alpha=0.3)

    fig.suptitle(f'v22 Phase 0: Star Formation (M={star_mass}, dep={deposit_strength}, '
                 f'H={H}, N={n_nodes})', fontweight='bold')
    fig.tight_layout()
    out_path = RESULTS_DIR / f'phase0_star_formation{suffix}.png'
    fig.savefig(out_path, dpi=150)
    print(f"\n  Saved: {out_path}")
    plt.close()


def phase1(n_nodes=30000, k=24, H=0.0001, alpha_expand=1.0,
           star_mass=100000.0, deposit_strength=1e-5,
           warm_up=20000, ticks=2000, seed=42, radius=30.0,
           body_base_radius=5.0, body_ref_mass=100000.0,
           weighted_spread=False, n_probes=20, probe_radius=8.0,
           inertia=10.0, force_coeff=0.01,
           tag=''):
    """Phase 1: Test particle natural velocity measurement.

    Place N test particles at r=probe_radius with zero velocity.
    Continuous force accumulation with force_coeff scaling.
    Run ticks of dynamics.  Measure tangential displacement per tick.
    """
    print("=" * 70)
    print("v22 PHASE 1: Test Particle Natural Velocity")
    print(f"  {n_probes} particles at r={probe_radius}, v=0, {ticks} ticks")
    print(f"  Continuous force: coeff={force_coeff}, inertia={inertia}")
    print("=" * 70)

    # All probe particles share one bid — they don't deposit, so no conflict
    body_ids = ['star', 'probe']
    graph = RandomGeometricGraph(n_nodes, k=k, G=0.0, H=H,
                                  alpha_expand=alpha_expand,
                                  seed=seed, body_ids=body_ids,
                                  radius=radius,
                                  weighted_spread=weighted_spread)

    center = graph.nearest_node(np.array([0.0, 0.0, 0.0]))
    star_body_radius = body_base_radius * (star_mass / body_ref_mass) ** (1.0 / 3.0)

    star = Entity('star', center, mass=star_mass,
                  deposit_rate=deposit_strength,
                  inertia=1.0, stationary=True,
                  radiate_mass=True,
                  graph=graph, body_radius=star_body_radius)

    e0_mean = np.mean(graph.edge_lengths)
    print(f"\n  Graph: N={n_nodes}, k={k}, mean_edge={e0_mean:.2f}")
    print(f"  Star: mass={star_mass}, body_nodes={len(star.nodes)}")

    # --- Warm-up: establish gradient ---
    print(f"  Warm-up: {warm_up} ticks ...")
    wu0 = time.time()
    for wt in range(warm_up):
        deposited = star.mass * star.deposit_rate
        n_body_nodes = len(star.nodes)
        deposit_per_node = deposited / n_body_nodes
        for n in star.nodes:
            graph.deposit(n, star.bid, deposit_per_node)
        if star.radiate_mass:
            star.mass = max(star.mass - deposited, 0.0)
        graph.spread()
        graph.expand_edges()
    print(f"  Warm-up done in {time.time()-wu0:.1f}s, star mass={star.mass:.1f}")

    # --- Place test particles at r=probe_radius, evenly spaced in xy-plane ---
    star_pos = graph.positions[center]
    probes = []
    for i in range(n_probes):
        angle = 2 * np.pi * i / n_probes
        target = star_pos + np.array([
            probe_radius * np.cos(angle),
            probe_radius * np.sin(angle),
            0.0
        ])
        node = graph.nearest_node(target)
        actual_pos = graph.positions[node]
        actual_r = np.linalg.norm(actual_pos - star_pos)

        probe = TestParticle('probe', node,
                             inertia=inertia, force_coeff=force_coeff)
        probes.append({
            'entity': probe,
            'init_node': node,
            'init_pos': actual_pos.copy(),
            'init_r': actual_r,
            'init_angle': np.arctan2(actual_pos[1] - star_pos[1],
                                     actual_pos[0] - star_pos[0]),
            'positions': [actual_pos.copy()],
            'angles': [],
            'radii': [],
        })

    print(f"  Placed {n_probes} probes at r~{probe_radius}")
    radii = [p['init_r'] for p in probes]
    print(f"    Actual radii: min={min(radii):.2f}, max={max(radii):.2f}, "
          f"mean={np.mean(radii):.2f}")

    # --- Run dynamics ---
    print(f"\n  Running {ticks} ticks of dynamics ...")
    t0 = time.time()
    print_interval = max(ticks // 10, 1)

    for tick in range(ticks):
        # Star continues depositing (field is live)
        deposited = star.mass * star.deposit_rate
        n_body_nodes = len(star.nodes)
        deposit_per_node = deposited / n_body_nodes
        for n in star.nodes:
            graph.deposit(n, star.bid, deposit_per_node)
        if star.radiate_mass:
            star.mass = max(star.mass - deposited, 0.0)

        graph.spread()
        graph.expand_edges()

        # Advance each probe
        for p in probes:
            p['entity'].advance(graph, tick)
            pos = graph.positions[p['entity'].node]
            p['positions'].append(pos.copy())
            rel = pos - star_pos
            p['radii'].append(np.linalg.norm(rel))
            p['angles'].append(np.arctan2(rel[1], rel[0]))

        if (tick + 1) % print_interval == 0:
            hops = [p['entity'].hops for p in probes]
            vels = [np.linalg.norm(p['entity'].velocity) for p in probes]
            print(f"    Tick {tick+1:5d}: hops={np.mean(hops):.1f}+-{np.std(hops):.1f} "
                  f"|v|={np.mean(vels):.5f}+-{np.std(vels):.5f} "
                  f"({time.time()-t0:.1f}s)")

    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s")

    # --- Measure tangential displacement ---
    print(f"\n  === RESULTS ===")
    tang_rates = []
    radial_rates = []
    for i, p in enumerate(probes):
        if len(p['angles']) < 2:
            continue
        # Tangential displacement: r * delta_theta
        angles = np.array(p['angles'])
        radii_arr = np.array(p['radii'])

        # Unwrap angles to handle +-pi crossings
        angles_uw = np.unwrap(angles)
        total_dtheta = angles_uw[-1] - angles_uw[0]
        mean_r = np.mean(radii_arr)
        tang_disp = mean_r * abs(total_dtheta)
        tang_rate = tang_disp / ticks

        # Radial displacement
        radial_disp = radii_arr[-1] - p['init_r']
        radial_rate = radial_disp / ticks

        tang_rates.append(tang_rate)
        radial_rates.append(radial_rate)

        if i < 5 or i == n_probes - 1:  # print first 5 + last
            print(f"    Probe {i:2d}: r={mean_r:.2f} hops={p['entity'].hops:3d} "
                  f"|v|={np.linalg.norm(p['entity'].velocity):.5f} "
                  f"tang/tick={tang_rate:.6f} rad/tick={radial_rate:.6f}")

    if tang_rates:
        print(f"\n  v_natural (tangential disp/tick):")
        print(f"    mean = {np.mean(tang_rates):.6f}")
        print(f"    std  = {np.std(tang_rates):.6f}")
        print(f"    min  = {np.min(tang_rates):.6f}")
        print(f"    max  = {np.max(tang_rates):.6f}")
        print(f"  Radial drift/tick:")
        print(f"    mean = {np.mean(radial_rates):.6f}")
        print(f"    std  = {np.std(radial_rates):.6f}")

    # --- Plot ---
    suffix = f"_{tag}" if tag else ""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 1) Probe trajectories in xy
    ax = axes[0]
    for p in probes:
        positions = np.array(p['positions'])
        ax.plot(positions[:, 0], positions[:, 1], '-', linewidth=0.8, alpha=0.7)
        ax.plot(positions[0, 0], positions[0, 1], 'go', markersize=4)
        ax.plot(positions[-1, 0], positions[-1, 1], 'r^', markersize=4)
    ax.plot(star_pos[0], star_pos[1], 'k*', markersize=15, label='star')
    circle = plt.Circle((star_pos[0], star_pos[1]), probe_radius,
                         fill=False, color='gray', linestyle='--', alpha=0.5)
    ax.add_patch(circle)
    ax.set_aspect('equal')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(f'Probe Trajectories (r~{probe_radius})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2) Velocity magnitude over time (sample 5 probes)
    ax = axes[1]
    sample_idx = np.linspace(0, n_probes - 1, min(5, n_probes), dtype=int)
    # Re-derive velocity from position differences
    for idx in sample_idx:
        p = probes[idx]
        positions = np.array(p['positions'])
        if len(positions) > 1:
            disps = np.linalg.norm(np.diff(positions, axis=0), axis=1)
            # Smooth with running mean
            window = min(50, len(disps) // 4) if len(disps) > 4 else 1
            if window > 1:
                kernel = np.ones(window) / window
                smoothed = np.convolve(disps, kernel, mode='valid')
                ax.plot(range(len(smoothed)), smoothed, linewidth=0.8,
                        label=f'probe {idx}')
            else:
                ax.plot(disps, linewidth=0.8, label=f'probe {idx}')
    ax.set_xlabel('Tick')
    ax.set_ylabel('Displacement per tick')
    ax.set_title('Displacement Rate Over Time')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 3) Tangential rate histogram
    ax = axes[2]
    if tang_rates:
        ax.hist(tang_rates, bins=min(15, n_probes), alpha=0.7, color='steelblue',
                edgecolor='black')
        ax.axvline(np.mean(tang_rates), color='red', linestyle='--',
                   label=f'mean={np.mean(tang_rates):.6f}')
    ax.set_xlabel('Tangential displacement / tick')
    ax.set_ylabel('Count')
    ax.set_title('v_natural Distribution')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle(f'v22 Phase 1: Test Particles at r={probe_radius} '
                 f'(warm_up={warm_up}, ticks={ticks})', fontweight='bold')
    fig.tight_layout()
    out_path = RESULTS_DIR / f'phase1_v_natural{suffix}.png'
    fig.savefig(out_path, dpi=150)
    print(f"\n  Saved: {out_path}")
    plt.close()


def measure_force(n_nodes=30000, k=24, H=0.0001, alpha_expand=1.0,
                  star_mass=100000.0, deposit_strength=1e-5,
                  warm_up=20000, seed=42, radius=30.0,
                  body_base_radius=5.0, body_ref_mass=100000.0,
                  weighted_spread=False, probe_radius=8.0,
                  force_coeff=1.0, radiate_mass=True):
    """Measure gravitational force at r=probe_radius from Phase 0 field.

    Computes force vector at every node near r=probe_radius,
    decomposes into radial/tangential, derives v_circular.
    """
    print("=" * 70)
    print(f"FORCE MEASUREMENT at r={probe_radius}")
    print("=" * 70)

    body_ids = ['star', 'probe']
    graph = RandomGeometricGraph(n_nodes, k=k, G=0.0, H=H,
                                  alpha_expand=alpha_expand,
                                  seed=seed, body_ids=body_ids,
                                  radius=radius,
                                  weighted_spread=weighted_spread)

    center = graph.nearest_node(np.array([0.0, 0.0, 0.0]))
    star_body_radius = body_base_radius * (star_mass / body_ref_mass) ** (1.0 / 3.0)
    star = Entity('star', center, mass=star_mass,
                  deposit_rate=deposit_strength,
                  inertia=1.0, stationary=True,
                  radiate_mass=radiate_mass,
                  graph=graph, body_radius=star_body_radius)

    star_pos = graph.positions[center]
    e0_mean = np.mean(graph.edge_lengths)

    # --- Warm-up ---
    print(f"  Star radiate_mass={radiate_mass}")
    print(f"  Warm-up: {warm_up} ticks ...")
    wu0 = time.time()
    for wt in range(warm_up):
        deposited = star.mass * star.deposit_rate
        n_body_nodes = len(star.nodes)
        dep_per = deposited / n_body_nodes
        for n in star.nodes:
            graph.deposit(n, star.bid, dep_per)
        if star.radiate_mass:
            star.mass = max(star.mass - deposited, 0.0)
        graph.spread()
        graph.expand_edges()
    print(f"  Warm-up done in {time.time()-wu0:.1f}s, star mass={star.mass:.1f}")

    # --- Find nodes in shell around probe_radius ---
    dists = np.linalg.norm(graph.positions - star_pos, axis=1)
    shell_width = 1.0
    mask = (dists > probe_radius - shell_width) & (dists < probe_radius + shell_width)
    shell_nodes = np.where(mask)[0]
    print(f"\n  Nodes in shell r={probe_radius}+-{shell_width}: {len(shell_nodes)}")

    # --- Compute force at each shell node ---
    f_radials = []
    f_tangentials = []
    f_magnitudes = []

    for node in shell_nodes:
        connectors = graph.growth_at_node_external(node, 'probe')
        if not connectors:
            continue

        growths = [g for _, _, g in connectors]
        mean_growth = sum(growths) / len(growths)

        force = np.zeros(3)
        for nb, eidx, growth in connectors:
            push = force_coeff * (mean_growth - growth)
            direction = graph.connector_direction(node, nb)
            force += direction * push

        # Decompose into radial and tangential
        rel = graph.positions[node] - star_pos
        r_dist = np.linalg.norm(rel)
        if r_dist < 1e-10:
            continue
        r_hat = rel / r_dist

        f_radial = float(np.dot(force, r_hat))
        f_tang_vec = force - f_radial * r_hat
        f_tangential = float(np.linalg.norm(f_tang_vec))

        f_radials.append(f_radial)
        f_tangentials.append(f_tangential)
        f_magnitudes.append(float(np.linalg.norm(force)))

    f_radials = np.array(f_radials)
    f_tangentials = np.array(f_tangentials)
    f_magnitudes = np.array(f_magnitudes)

    print(f"\n  === FORCE at r~{probe_radius} (force_coeff={force_coeff}) ===")
    print(f"  F_radial:     mean={np.mean(f_radials):.8f}  "
          f"std={np.std(f_radials):.8f}")
    print(f"  |F_tangential|: mean={np.mean(f_tangentials):.8f}  "
          f"std={np.std(f_tangentials):.8f}")
    print(f"  |F_total|:    mean={np.mean(f_magnitudes):.8f}  "
          f"std={np.std(f_magnitudes):.8f}")
    print(f"  F_radial sign: {np.sum(f_radials < 0)}/{len(f_radials)} negative (inward)")

    mean_f_rad = np.mean(f_radials)
    v_circ = np.sqrt(abs(mean_f_rad) * probe_radius)

    print(f"\n  >>> v_circular = sqrt(|F_radial| * r)")
    print(f"      = sqrt({abs(mean_f_rad):.8f} * {probe_radius})")
    print(f"      = {v_circ:.6f}")

    # Also compute for inertia=10 (what DiskParticle sees)
    v_circ_i10 = np.sqrt(abs(mean_f_rad / 10.0) * probe_radius)
    print(f"\n  With inertia=10: accel = F/10")
    print(f"      v_circular = sqrt(|F_radial/10| * r) = {v_circ_i10:.6f}")

    return v_circ, v_circ_i10


def phase2(n_nodes=30000, k=24, H=0.0001, alpha_expand=1.0,
           star_mass=100000.0, deposit_strength=1e-5,
           warm_up=20000, ticks=20000, seed=42, radius=30.0,
           body_base_radius=5.0, body_ref_mass=100000.0,
           weighted_spread=False, n_ring=20, ring_radius=8.0,
           ring_mass=100.0, ring_deposit=1e-5,
           v_tangential=0.003, inertia=10.0, force_coeff=1.0,
           force_interval=10, radiate_mass=True, tag=''):
    """Phase 2: Proto-disk ring evolution.

    Ring of small depositing bodies at r=ring_radius with tangential velocity.
    Watch for coalescence, dispersal, or infall.
    """
    print("=" * 70)
    print("v22 PHASE 2: Proto-Disk Ring")
    print(f"  {n_ring} bodies at r={ring_radius}, mass={ring_mass}, "
          f"v_tan={v_tangential}")
    print(f"  force_coeff={force_coeff}, inertia={inertia}, {ticks} ticks")
    print("=" * 70)

    # All ring particles share bid='disk' — they feel total gamma
    body_ids = ['star', 'disk']
    graph = RandomGeometricGraph(n_nodes, k=k, G=0.0, H=H,
                                  alpha_expand=alpha_expand,
                                  seed=seed, body_ids=body_ids,
                                  radius=radius,
                                  weighted_spread=weighted_spread)

    center = graph.nearest_node(np.array([0.0, 0.0, 0.0]))
    star_body_radius = body_base_radius * (star_mass / body_ref_mass) ** (1.0 / 3.0)
    star = Entity('star', center, mass=star_mass,
                  deposit_rate=deposit_strength,
                  inertia=1.0, stationary=True,
                  radiate_mass=radiate_mass,
                  graph=graph, body_radius=star_body_radius)

    e0_mean = np.mean(graph.edge_lengths)
    star_pos = graph.positions[center]
    print(f"\n  Graph: N={n_nodes}, k={k}, mean_edge={e0_mean:.2f}")
    print(f"  Star: mass={star_mass}, body_nodes={len(star.nodes)}, "
          f"radiate_mass={radiate_mass}")

    # --- Warm-up ---
    print(f"  Warm-up: {warm_up} ticks ...")
    wu0 = time.time()
    for wt in range(warm_up):
        deposited = star.mass * star.deposit_rate
        n_body_nodes = len(star.nodes)
        dep_per = deposited / n_body_nodes
        for n in star.nodes:
            graph.deposit(n, star.bid, dep_per)
        if star.radiate_mass:
            star.mass = max(star.mass - deposited, 0.0)
        graph.spread()
        graph.expand_edges()
    print(f"  Warm-up done in {time.time()-wu0:.1f}s, star mass={star.mass:.1f}")

    # --- Place ring particles ---
    ring = []
    for i in range(n_ring):
        angle = 2 * np.pi * i / n_ring
        target = star_pos + np.array([
            ring_radius * np.cos(angle),
            ring_radius * np.sin(angle),
            0.0
        ])
        node = graph.nearest_node(target)
        actual_pos = graph.positions[node]
        actual_r = np.linalg.norm(actual_pos - star_pos)

        p = DiskParticle('disk', node, mass=ring_mass,
                         deposit_rate=ring_deposit,
                         inertia=inertia, force_coeff=force_coeff,
                         radiate_mass=True, force_interval=force_interval)

        # Tangential velocity: perpendicular to radial in xy-plane
        r_hat = (actual_pos - star_pos)
        r_hat = r_hat / (np.linalg.norm(r_hat) + 1e-15)
        t_hat = np.array([-r_hat[1], r_hat[0], 0.0])
        p.set_velocity(t_hat * v_tangential)

        ring.append({
            'entity': p,
            'init_r': actual_r,
            'init_angle': angle,
            'radii': [],
            'angles': [],
            'positions': [actual_pos.copy()],
            'hop_ticks': [0],
        })

    radii = [p['init_r'] for p in ring]
    print(f"  Ring: {n_ring} bodies, mass={ring_mass} each, "
          f"deposit={ring_deposit}")
    print(f"    Actual radii: min={min(radii):.2f}, max={max(radii):.2f}, "
          f"mean={np.mean(radii):.2f}")
    print(f"    v_tangential={v_tangential}, total ring mass={n_ring*ring_mass:.0f}")

    # --- Run ---
    print(f"\n  Running {ticks} ticks ...")
    t0 = time.time()
    print_interval = max(ticks // 20, 1)
    snapshot_ticks = sorted(set([1000, 5000, 10000, 25000, 50000, 75000, ticks]))
    snapshot_ticks = [t for t in snapshot_ticks if t <= ticks]
    snapshots = {}  # tick -> list of (x, y) positions
    best3_idx = None  # set at tick 5000
    escape_radius = radius * 0.9  # 27.0 for radius=30

    for tick in range(ticks):
        # Star deposits
        deposited = star.mass * star.deposit_rate
        n_body_nodes = len(star.nodes)
        dep_per = deposited / n_body_nodes
        for n in star.nodes:
            graph.deposit(n, star.bid, dep_per)
        if star.radiate_mass:
            star.mass = max(star.mass - deposited, 0.0)

        graph.spread()
        graph.expand_edges()

        # Advance ring particles
        for p in ring:
            old_hops = p['entity'].hops
            p['entity'].advance(graph, tick)
            if p['entity'].hops > old_hops:
                p['hop_ticks'].append(tick + 1)
            pos = graph.positions[p['entity'].node]
            rel = pos - star_pos
            p['radii'].append(np.linalg.norm(rel))
            p['angles'].append(np.arctan2(rel[1], rel[0]))
            p['positions'].append(pos.copy())

        # At tick 5000: pick 3 with smallest |r - init_r|
        if (tick + 1) == 5000:
            drifts = [abs(p['radii'][-1] - p['init_r']) for p in ring]
            best3_idx = sorted(range(n_ring), key=lambda i: drifts[i])[:3]
            print(f"\n  === BEST 3 at tick 5000 ===")
            for rank, idx in enumerate(best3_idx):
                p = ring[idx]
                print(f"    #{rank}: particle {idx}, r={p['radii'][-1]:.2f} "
                      f"(init={p['init_r']:.2f}, drift={drifts[idx]:.3f}), "
                      f"|v|={np.linalg.norm(p['entity'].velocity):.5f}, "
                      f"hops={p['entity'].hops}")
            # Record escape tick for best 3
            for idx in best3_idx:
                ring[idx]['escape_tick'] = None
            print()

        # Track escape for best 3
        if best3_idx is not None:
            for idx in best3_idx:
                if ring[idx]['escape_tick'] is None and ring[idx]['radii'][-1] > escape_radius:
                    ring[idx]['escape_tick'] = tick + 1

        if (tick + 1) in snapshot_ticks:
            snapshots[tick + 1] = [
                graph.positions[p['entity'].node].copy() for p in ring
            ]

        if (tick + 1) % print_interval == 0:
            rs = [p['radii'][-1] for p in ring]
            hops = [p['entity'].hops for p in ring]
            vels = [np.linalg.norm(p['entity'].velocity) for p in ring]
            masses = [p['entity'].mass for p in ring]

            # Angular spread: std of angles (clumping metric)
            angs = np.array([p['angles'][-1] for p in ring])
            # Use circular std
            ang_spread = np.sqrt(-2 * np.log(
                max(abs(np.mean(np.exp(1j * angs))), 1e-15)))

            # Best 3 radii
            b3_str = ""
            if best3_idx is not None:
                b3_rs = [ring[i]['radii'][-1] for i in best3_idx]
                b3_str = f" best3=[{b3_rs[0]:.1f},{b3_rs[1]:.1f},{b3_rs[2]:.1f}]"

            print(f"    Tick {tick+1:6d}: r={np.mean(rs):.2f}+-{np.std(rs):.2f} "
                  f"|v|={np.mean(vels):.5f} hops={np.mean(hops):.1f} "
                  f"mass={np.mean(masses):.1f}{b3_str} ({time.time()-t0:.1f}s)")

    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s")

    # --- Summary ---
    print(f"\n  === RESULTS ===")
    final_rs = [p['radii'][-1] for p in ring]
    init_rs = [p['init_r'] for p in ring]
    print(f"  Radii: init={np.mean(init_rs):.2f} -> final={np.mean(final_rs):.2f} "
          f"(delta={np.mean(final_rs)-np.mean(init_rs):+.2f})")
    total_hops = sum(p['entity'].hops for p in ring)
    print(f"  Total hops: {total_hops}")

    # Hop interval stats
    all_intervals = []
    for p in ring:
        if len(p['hop_ticks']) > 1:
            intervals = [p['hop_ticks'][j+1] - p['hop_ticks'][j]
                         for j in range(len(p['hop_ticks'])-1)]
            all_intervals.extend(intervals)
    if all_intervals:
        print(f"\n  === HOP INTERVALS ===")
        print(f"  mean ticks/hop = {np.mean(all_intervals):.0f}")
        print(f"  std            = {np.std(all_intervals):.0f}")
        print(f"  min/max        = {np.min(all_intervals)}/{np.max(all_intervals)}")
        circumference = 2 * np.pi * ring_radius
        hops_per_orbit = circumference / graph.initial_mean_edge
        print(f"  hops/orbit     = {hops_per_orbit:.1f} "
              f"(circumference={circumference:.1f}, hop={graph.initial_mean_edge:.2f})")

    # Best 3 escape report
    if best3_idx is not None:
        print(f"\n  === BEST 3 ORBIT SURVIVAL ===")
        for rank, idx in enumerate(best3_idx):
            p = ring[idx]
            esc = p.get('escape_tick', None)
            final_r = p['radii'][-1]
            if esc is not None:
                print(f"    #{rank} (particle {idx}): escaped at tick {esc} "
                      f"(survived {esc} ticks), final r={final_r:.2f}")
            else:
                print(f"    #{rank} (particle {idx}): STILL BOUND at tick {ticks}, "
                      f"final r={final_r:.2f}")
            print(f"      init_r={p['init_r']:.2f}, hops={p['entity'].hops}, "
                  f"|v|={np.linalg.norm(p['entity'].velocity):.5f}")

    # --- Plots ---
    suffix = f"_{tag}" if tag else ""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    # 1) Best 3 trajectories xy
    ax = axes[0, 0]
    # Dim background: all particles
    for p in ring:
        positions = np.array(p['positions'])
        ax.plot(positions[:, 0], positions[:, 1], '-', linewidth=0.3,
                alpha=0.15, color='gray')
    # Highlight best 3
    b3_colors = ['#e41a1c', '#377eb8', '#4daf4a']
    if best3_idx is not None:
        for rank, idx in enumerate(best3_idx):
            p = ring[idx]
            positions = np.array(p['positions'])
            ax.plot(positions[:, 0], positions[:, 1], '-',
                    linewidth=1.5, color=b3_colors[rank],
                    label=f'#{rank} (p{idx})')
            ax.plot(positions[0, 0], positions[0, 1], 'o',
                    color=b3_colors[rank], markersize=6)
            ax.plot(positions[-1, 0], positions[-1, 1], '^',
                    color=b3_colors[rank], markersize=6)
    ax.plot(star_pos[0], star_pos[1], 'k*', markersize=15)
    circle = plt.Circle((star_pos[0], star_pos[1]), ring_radius,
                         fill=False, color='gray', linestyle='--', alpha=0.5)
    ax.add_patch(circle)
    ax.set_aspect('equal')
    ax.set_title('Best 3 Trajectories')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2) Best 3 radial distance over time
    ax = axes[0, 1]
    if best3_idx is not None:
        for rank, idx in enumerate(best3_idx):
            p = ring[idx]
            ax.plot(p['radii'], linewidth=1.5, color=b3_colors[rank],
                    label=f'#{rank} (p{idx})')
            esc = p.get('escape_tick', None)
            if esc is not None:
                ax.axvline(esc, color=b3_colors[rank], linestyle=':',
                           alpha=0.5)
    ax.axhline(ring_radius, color='gray', linestyle='--', alpha=0.5,
               label=f'init r={ring_radius}')
    ax.axhline(escape_radius, color='red', linestyle='--', alpha=0.3,
               label=f'escape r={escape_radius:.0f}')
    ax.set_xlabel('Tick')
    ax.set_ylabel('Distance from star')
    ax.set_title('Best 3: Radial Evolution')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 3) All particles radial evolution
    ax = axes[0, 2]
    for i, p in enumerate(ring):
        ax.plot(p['radii'], linewidth=0.5, alpha=0.4)
    ax.axhline(ring_radius, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(escape_radius, color='red', linestyle='--', alpha=0.3)
    ax.set_xlabel('Tick')
    ax.set_ylabel('Distance from star')
    ax.set_title('All Particles: Radial Evolution')
    ax.grid(True, alpha=0.3)

    # 4) Best 3 velocity over time
    ax = axes[1, 0]
    if best3_idx is not None:
        for rank, idx in enumerate(best3_idx):
            p = ring[idx]
            positions = np.array(p['positions'])
            if len(positions) > 1:
                disps = np.linalg.norm(np.diff(positions, axis=0), axis=1)
                window = min(200, len(disps) // 8) if len(disps) > 8 else 1
                if window > 1:
                    kernel = np.ones(window) / window
                    smoothed = np.convolve(disps, kernel, mode='valid')
                    ax.plot(smoothed, linewidth=1.0, color=b3_colors[rank],
                            label=f'#{rank} (p{idx})')
    ax.set_xlabel('Tick')
    ax.set_ylabel('Displacement/tick')
    ax.set_title('Best 3: Velocity Evolution')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 5) Snapshots
    ax = axes[1, 1]
    snap_colors = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
    for (t, positions), color in zip(sorted(snapshots.items()), snap_colors):
        positions = np.array(positions)
        ax.scatter(positions[:, 0], positions[:, 1], s=15, color=color,
                   label=f't={t}', alpha=0.8)
    ax.plot(star_pos[0], star_pos[1], 'k*', markersize=15)
    circle = plt.Circle((star_pos[0], star_pos[1]), ring_radius,
                         fill=False, color='gray', linestyle='--', alpha=0.5)
    ax.add_patch(circle)
    ax.set_aspect('equal')
    ax.set_title('Ring Snapshots')
    ax.legend(fontsize=6)
    ax.grid(True, alpha=0.3)

    # 6) Radial histogram: initial vs final
    ax = axes[1, 2]
    ax.hist(init_rs, bins=15, alpha=0.5, label='initial', color='blue')
    ax.hist(final_rs, bins=15, alpha=0.5, label='final', color='red')
    ax.set_xlabel('Distance from star')
    ax.set_ylabel('Count')
    ax.set_title('Radial Distribution')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle(f'v22 Phase 2: Proto-Disk (N={n_ring}, M={ring_mass}, '
                 f'v_tan={v_tangential}, fc={force_coeff})',
                 fontweight='bold')
    fig.tight_layout()
    out_path = RESULTS_DIR / f'phase2_protodisk{suffix}.png'
    fig.savefig(out_path, dpi=150)
    print(f"\n  Saved: {out_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='v22 Star Formation + Disk')
    parser.add_argument('--phase0', action='store_true', help='Run Phase 0: gradient formation')
    parser.add_argument('--phase1', action='store_true', help='Run Phase 1: test particle v_natural')
    parser.add_argument('--measure-force', action='store_true',
                        help='Measure force at probe-radius, compute v_circular')
    parser.add_argument('--phase2', action='store_true', help='Run Phase 2: proto-disk ring')
    parser.add_argument('--n-nodes', type=int, default=80000)
    parser.add_argument('--k', type=int, default=24)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--radius', type=float, default=45.0)
    parser.add_argument('--H', type=float, default=0.0001)
    parser.add_argument('--alpha-expand', type=float, default=1.0)
    parser.add_argument('--star-mass', type=float, default=100000.0)
    parser.add_argument('--deposit-strength', type=float, default=1e-5)
    parser.add_argument('--ticks', type=int, default=5000)
    parser.add_argument('--warm-up', type=int, default=50000,
                        help='Warm-up ticks for Phase 1 (default 20000)')
    parser.add_argument('--body-base-radius', type=float, default=5.0)
    parser.add_argument('--body-ref-mass', type=float, default=100000.0)
    parser.add_argument('--weighted-spread', action='store_true')
    parser.add_argument('--n-probes', type=int, default=20)
    parser.add_argument('--probe-radius', type=float, default=8.0)
    parser.add_argument('--inertia', type=float, default=10.0,
                        help='Test particle inertia (default 10.0)')
    parser.add_argument('--force-coeff', type=float, default=1.0,
                        help='Force coefficient (default 1.0)')
    parser.add_argument('--force-interval', type=int, default=10,
                        help='Ticks between force updates (default 10)')
    parser.add_argument('--n-ring', type=int, default=20,
                        help='Number of ring particles for Phase 2')
    parser.add_argument('--ring-radius', type=float, default=8.0)
    parser.add_argument('--ring-mass', type=float, default=100.0)
    parser.add_argument('--ring-deposit', type=float, default=1e-5)
    parser.add_argument('--v-tangential', type=float, default=0.003)
    parser.add_argument('--no-mass-loss', action='store_true',
                        help='Disable mass radiation (deposit gamma but keep mass constant)')
    parser.add_argument('--tag', type=str, default='')

    args = parser.parse_args()

    if args.phase0:
        phase0(n_nodes=args.n_nodes, k=args.k, H=args.H,
               alpha_expand=args.alpha_expand,
               star_mass=args.star_mass,
               deposit_strength=args.deposit_strength,
               ticks=args.ticks, seed=args.seed,
               radius=args.radius,
               body_base_radius=args.body_base_radius,
               body_ref_mass=args.body_ref_mass,
               weighted_spread=args.weighted_spread,
               tag=args.tag)

    if args.phase1:
        phase1(n_nodes=args.n_nodes, k=args.k, H=args.H,
               alpha_expand=args.alpha_expand,
               star_mass=args.star_mass,
               deposit_strength=args.deposit_strength,
               warm_up=args.warm_up, ticks=args.ticks,
               seed=args.seed, radius=args.radius,
               body_base_radius=args.body_base_radius,
               body_ref_mass=args.body_ref_mass,
               weighted_spread=args.weighted_spread,
               n_probes=args.n_probes,
               probe_radius=args.probe_radius,
               inertia=args.inertia,
               force_coeff=args.force_coeff,
               tag=args.tag)

    if args.measure_force:
        measure_force(n_nodes=args.n_nodes, k=args.k, H=args.H,
                      alpha_expand=args.alpha_expand,
                      star_mass=args.star_mass,
                      deposit_strength=args.deposit_strength,
                      warm_up=args.warm_up, seed=args.seed,
                      radius=args.radius,
                      body_base_radius=args.body_base_radius,
                      body_ref_mass=args.body_ref_mass,
                      weighted_spread=args.weighted_spread,
                      probe_radius=args.probe_radius,
                      force_coeff=args.force_coeff,
                      radiate_mass=not args.no_mass_loss)

    if args.phase2:
        phase2(n_nodes=args.n_nodes, k=args.k, H=args.H,
               alpha_expand=args.alpha_expand,
               star_mass=args.star_mass,
               deposit_strength=args.deposit_strength,
               warm_up=args.warm_up, ticks=args.ticks,
               seed=args.seed, radius=args.radius,
               body_base_radius=args.body_base_radius,
               body_ref_mass=args.body_ref_mass,
               weighted_spread=args.weighted_spread,
               n_ring=args.n_ring,
               ring_radius=args.ring_radius,
               ring_mass=args.ring_mass,
               ring_deposit=args.ring_deposit,
               v_tangential=args.v_tangential,
               inertia=args.inertia,
               force_coeff=args.force_coeff,
               force_interval=args.force_interval,
               radiate_mass=not args.no_mass_loss,
               tag=args.tag)

    if not any([args.phase0, args.phase1, args.measure_force, args.phase2]):
        print("No phase selected. Use --phase0, --phase1, --measure-force, or --phase2.")


if __name__ == '__main__':
    main()
