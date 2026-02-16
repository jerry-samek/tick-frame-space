"""v6: Self-Gravitating Gamma on a Graph

There are no entities. There is only gamma on a graph.

Some gamma clumps together (= matter, particles). Some flows freely (= radiation,
photons). What holds a clump together? Self-gravitation: the spread rate depends on
local gamma density. High gamma -> slow spread -> peak holds. Low gamma -> fast
spread -> free propagation at c.

One field. One graph. One new parameter G (gravitational coupling). Total gamma
strictly conserved. No decay. No deposits. No entities.

Core physics:
    alpha_eff(node) = alpha / (1 + G * gamma[node])
    outflow = alpha_eff * gamma
    inflow  = A @ (outflow / degrees)
    gamma_new = (gamma - outflow) + inflow       # exact conservation

Usage:
    python gamma_field.py --verify                             # run tests
    python gamma_field.py --n-peaks 1 --G 1.0 --ticks 5000    # single peak stability
    python gamma_field.py --n-peaks 2 --G 1.0 --ticks 10000   # two-body attraction
    python gamma_field.py --n-peaks 3 --G 1.0 --ticks 20000   # three-body dynamics

February 2026
"""

import argparse
import json
import time
from collections import deque
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import scipy.sparse as sp

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# ===========================================================================
# SelfGravitatingField -- the only physics object
# ===========================================================================

class SelfGravitatingField:
    """Gamma field on a graph with nonlinear self-gravitating spread.

    There are no entities. Gamma is distributed across nodes. High-gamma
    regions resist spreading (self-gravitation), forming stable clumps.
    Low-gamma regions spread freely at c = 1 hop/tick.

    Total gamma is exactly conserved (no decay, no deposits).
    """

    def __init__(self, n_nodes, k=6, alpha=None, G=1.0, seed=42,
                 graph_type='lattice'):
        self.k = k
        self.G = G
        self.seed = seed
        self.graph_type = graph_type
        self.graph_info = {}

        # Build graph
        t0 = time.time()
        if graph_type == 'lattice':
            side = round(n_nodes ** (1/3))
            actual_n = side ** 3
            print(f"  Building lattice: side={side}, N={actual_n} "
                  f"(periodic, k={k})")
            G_grid = nx.grid_graph(dim=[side, side, side], periodic=True)
            sorted_nodes = sorted(G_grid.nodes())
            coord_map = {i: node for i, node in enumerate(sorted_nodes)}
            self.graph = nx.convert_node_labels_to_integers(
                G_grid, ordering='sorted')
            self.node_coords = coord_map
            self.coord_to_node = {v: k_node for k_node, v in coord_map.items()}
            self.side = side
            n_nodes = actual_n
            self.graph_info['side'] = side
            self.graph_info['actual_n'] = actual_n
        else:
            raise ValueError(f"Unknown graph_type: {graph_type}")

        elapsed = time.time() - t0
        print(f"    Graph built in {elapsed:.1f}s")

        self.n_nodes = n_nodes

        # Speed of light: alpha = 1/k gives c = 1 hop/tick
        if alpha is None:
            alpha = 1.0 / k
        self.alpha = alpha

        # Adjacency list for O(1) neighbor access
        self.neighbors = [list(self.graph.neighbors(i))
                          for i in range(n_nodes)]

        # Sparse adjacency matrix and degree array
        print(f"  Building adjacency matrix (alpha={alpha:.4f}, G={G})")
        t0 = time.time()
        self.A = nx.adjacency_matrix(self.graph, dtype=np.float64)
        self.degrees = np.array(self.A.sum(axis=1)).flatten()
        self.degrees = np.maximum(self.degrees, 1.0)  # safety
        elapsed = time.time() - t0
        print(f"    Adjacency matrix built in {elapsed:.1f}s")

        # The gamma field -- one array for everything
        self.gamma = np.zeros(n_nodes, dtype=np.float64)

    # --- Core physics ---------------------------------------------------

    def spread(self):
        """Nonlinear self-gravitating spread. Conserves gamma exactly.

        alpha_eff(node) = alpha / (1 + G * gamma[node])
        High gamma -> low spread -> peak holds together.
        Low gamma -> full spread -> propagation at c.
        """
        alpha_eff = self.alpha / (1.0 + self.G * self.gamma)
        outflow = alpha_eff * self.gamma
        per_edge = outflow / self.degrees
        inflow = self.A @ per_edge
        self.gamma = (self.gamma - outflow) + inflow

    def total_gamma(self):
        """Total gamma across all nodes."""
        return float(np.sum(self.gamma))

    # --- Initialization -------------------------------------------------

    def initialize_peak(self, center_node, total_mass, smooth_ticks=20):
        """Place gamma at center, smooth with uniform spread.

        Temporarily sets G=0 to spread the delta into a Gaussian-like
        profile, then restores G. Total gamma exactly conserved.
        """
        self.gamma[center_node] += total_mass
        saved_G = self.G
        self.G = 0.0
        for _ in range(smooth_ticks):
            self.spread()
        self.G = saved_G

    def place_peaks_equilateral(self, separation, n_peaks=3):
        """Place peaks in equilateral triangle on lattice.

        Returns list of center nodes.
        """
        assert hasattr(self, 'node_coords'), \
            "Equilateral placement requires lattice graph"
        s = self.side
        d = separation
        if d % 2 != 0:
            d += 1

        cx, cy, cz = s // 2, s // 2, s // 2

        if n_peaks == 1:
            coords = [((cx) % s, (cy) % s, cz % s)]
        elif n_peaks == 2:
            coords = [
                ((cx) % s, (cy) % s, cz % s),
                ((cx + d) % s, (cy) % s, cz % s),
            ]
        else:
            coords = [
                ((cx) % s, (cy) % s, cz % s),
                ((cx + d) % s, (cy) % s, cz % s),
                ((cx + d // 2) % s, (cy + d // 2) % s, cz % s),
            ]

        nodes = [self.coord_to_node[c] for c in coords[:n_peaks]]

        # Verify distances
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                d_ij = self.hop_distance(nodes[i], nodes[j])
                print(f"    P{i}-P{j}: {d_ij} hops")

        return nodes

    # --- Peak detection -------------------------------------------------

    def find_peaks(self, min_gamma=None):
        """Find local maxima: nodes where gamma > all neighbors' gamma.

        Returns list of (node, gamma_value) sorted by gamma descending.
        """
        if min_gamma is None:
            total = self.total_gamma()
            if total > 0:
                min_gamma = total / self.n_nodes * 5.0  # 5x background
            else:
                min_gamma = 0.0

        peaks = []
        for node in range(self.n_nodes):
            g = self.gamma[node]
            if g < min_gamma:
                continue
            is_peak = True
            for nb in self.neighbors[node]:
                if self.gamma[nb] >= g:
                    is_peak = False
                    break
            if is_peak:
                peaks.append((node, g))

        return sorted(peaks, key=lambda x: -x[1])

    def cluster_peaks(self, peaks, merge_radius=3):
        """Merge nearby peaks into particles.

        Returns list of dicts: {center, mass, peak_gamma, width, nodes}
        """
        if not peaks:
            return []

        claimed = set()
        particles = []

        for peak_node, peak_val in peaks:
            if peak_node in claimed:
                continue

            # BFS to collect nodes within merge_radius
            shell_nodes = []
            shell_gamma = []
            visited = {peak_node}
            queue = deque([(peak_node, 0)])
            while queue:
                node, dist = queue.popleft()
                shell_nodes.append(node)
                shell_gamma.append(self.gamma[node])
                claimed.add(node)
                if dist < merge_radius:
                    for nb in self.neighbors[node]:
                        if nb not in visited:
                            visited.add(nb)
                            queue.append((nb, dist + 1))

            total_mass = sum(shell_gamma)
            if total_mass <= 0:
                continue

            # Weighted center (by hop distance from peak)
            # Width = RMS distance weighted by gamma
            distances = []
            visited2 = {peak_node}
            queue2 = deque([(peak_node, 0)])
            sum_d2_g = 0.0
            while queue2:
                node, dist = queue2.popleft()
                g = self.gamma[node]
                sum_d2_g += dist * dist * g
                if dist < merge_radius:
                    for nb in self.neighbors[node]:
                        if nb not in visited2:
                            visited2.add(nb)
                            queue2.append((nb, dist + 1))

            width = np.sqrt(sum_d2_g / total_mass) if total_mass > 0 else 0.0

            particles.append({
                'center': peak_node,
                'mass': total_mass,
                'peak_gamma': peak_val,
                'width': width,
            })

        return particles

    def measure_particle(self, center, radius=5):
        """Measure mass and width of gamma around a node."""
        visited = {center}
        queue = deque([(center, 0)])
        total_mass = 0.0
        sum_d2_g = 0.0
        peak_g = self.gamma[center]

        while queue:
            node, dist = queue.popleft()
            g = self.gamma[node]
            total_mass += g
            sum_d2_g += dist * dist * g
            if g > peak_g:
                peak_g = g
            if dist < radius:
                for nb in self.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist + 1))

        width = np.sqrt(sum_d2_g / total_mass) if total_mass > 0 else 0.0
        return {
            'mass': total_mass,
            'peak_gamma': peak_g,
            'width': width,
        }

    def radial_profile(self, center, max_radius=15):
        """Gamma as function of hop distance from center."""
        visited = {center}
        queue = deque([(center, 0)])
        shells = {}  # dist -> list of gamma values

        while queue:
            node, dist = queue.popleft()
            if dist not in shells:
                shells[dist] = []
            shells[dist].append(self.gamma[node])
            if dist < max_radius:
                for nb in self.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist + 1))

        profile = []
        for d in sorted(shells.keys()):
            vals = shells[d]
            profile.append({
                'distance': d,
                'mean_gamma': np.mean(vals),
                'max_gamma': np.max(vals),
                'n_nodes': len(vals),
            })
        return profile

    # --- Distance -------------------------------------------------------

    def hop_distance(self, a, b, max_dist=500):
        """BFS shortest path distance between nodes a and b."""
        if a == b:
            return 0
        visited = {a}
        queue = deque([(a, 0)])
        while queue:
            node, dist = queue.popleft()
            if dist >= max_dist:
                return max_dist
            for nb in self.neighbors[node]:
                if nb == b:
                    return dist + 1
                if nb not in visited:
                    visited.add(nb)
                    queue.append((nb, dist + 1))
        return max_dist

    def graph_stats(self, n_samples=200):
        """Sampled average path length and clustering coefficient."""
        rng = np.random.default_rng(self.seed + 1000)
        nodes = rng.choice(self.n_nodes,
                           size=min(n_samples, self.n_nodes), replace=False)
        total_dist = 0
        count = 0
        for i in range(len(nodes)):
            for j in range(i + 1, min(i + 10, len(nodes))):
                d = self.hop_distance(int(nodes[i]), int(nodes[j]))
                total_dist += d
                count += 1
        avg_path = total_dist / count if count > 0 else 0
        clustering = nx.average_clustering(self.graph)
        return avg_path, clustering


# ===========================================================================
# Peak tracker -- match particles across ticks by proximity
# ===========================================================================

class PeakTracker:
    """Track identified particles across ticks."""

    def __init__(self, max_match_dist=10):
        self.max_match_dist = max_match_dist
        self.prev_particles = []
        self.histories = {}  # id -> list of snapshots
        self.next_id = 0

    def update(self, tick, particles, field):
        """Match current particles to previous, assign IDs."""
        if not self.prev_particles:
            # First measurement -- assign new IDs
            for p in particles:
                pid = self.next_id
                self.next_id += 1
                p['id'] = pid
                self.histories[pid] = [{
                    'tick': tick, **p
                }]
            self.prev_particles = particles
            return particles

        # Match by closest distance
        used_prev = set()
        for p in particles:
            best_dist = self.max_match_dist + 1
            best_id = None
            for prev_p in self.prev_particles:
                if prev_p['id'] in used_prev:
                    continue
                d = field.hop_distance(p['center'], prev_p['center'],
                                       max_dist=self.max_match_dist + 1)
                if d < best_dist:
                    best_dist = d
                    best_id = prev_p['id']

            if best_id is not None:
                p['id'] = best_id
                used_prev.add(best_id)
                self.histories[best_id].append({'tick': tick, **p})
            else:
                # New particle
                pid = self.next_id
                self.next_id += 1
                p['id'] = pid
                self.histories[pid] = [{'tick': tick, **p}]

        self.prev_particles = particles
        return particles


# ===========================================================================
# Simulation loop
# ===========================================================================

def run_simulation(field, ticks, measure_interval=50, log_interval=500):
    """Main simulation: just spread gamma, measure what happens.

    No entities. No deposits. Just the nonlinear spread rule.
    """
    diagnostics = {
        'conservation': [],
        'peaks': [],
        'distances': [],
        'particle_mass': [],
        'radiation': [],
    }

    tracker = PeakTracker()
    initial_gamma = field.total_gamma()
    t0 = time.time()

    print(f"\n  Running {ticks} ticks (measure every {measure_interval}, "
          f"log every {log_interval})")
    print(f"  Initial gamma: {initial_gamma:.4f}")

    for tick in range(ticks):
        field.spread()

        if (tick + 1) % measure_interval == 0:
            current_gamma = field.total_gamma()
            drift = abs(current_gamma - initial_gamma) / initial_gamma \
                if initial_gamma > 0 else 0.0

            diagnostics['conservation'].append({
                'tick': tick + 1,
                'total_gamma': current_gamma,
                'drift': drift,
            })

            # Peak detection
            raw_peaks = field.find_peaks()
            particles = field.cluster_peaks(raw_peaks)
            particles = tracker.update(tick + 1, particles, field)

            diagnostics['peaks'].append({
                'tick': tick + 1,
                'n_particles': len(particles),
                'particles': [
                    {'id': p['id'], 'center': p['center'],
                     'mass': p['mass'], 'peak_gamma': p['peak_gamma'],
                     'width': p['width']}
                    for p in particles
                ],
            })

            # Pairwise distances
            if len(particles) >= 2:
                dist_entry = {'tick': tick + 1}
                for i in range(len(particles)):
                    for j in range(i + 1, len(particles)):
                        key = f"P{particles[i]['id']}-P{particles[j]['id']}"
                        d = field.hop_distance(
                            particles[i]['center'],
                            particles[j]['center'])
                        dist_entry[key] = d
                diagnostics['distances'].append(dist_entry)

            # Radiation budget
            bound = sum(p['mass'] for p in particles)
            free = current_gamma - bound
            diagnostics['radiation'].append({
                'tick': tick + 1,
                'bound_gamma': bound,
                'free_gamma': max(0, free),
                'frac_bound': bound / current_gamma
                    if current_gamma > 0 else 0,
            })

        if (tick + 1) % log_interval == 0:
            elapsed = time.time() - t0
            rate = (tick + 1) / elapsed if elapsed > 0 else 0
            current = field.total_gamma()
            peak_g = float(np.max(field.gamma))
            drift = abs(current - initial_gamma) / initial_gamma \
                if initial_gamma > 0 else 0.0
            print(f"    Tick {tick+1:6d}/{ticks} ({elapsed:6.1f}s, "
                  f"{rate:.0f} t/s) peak={peak_g:.4f} "
                  f"total={current:.4f} drift={drift:.2e}")

    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s ({ticks/elapsed:.0f} ticks/s)")

    return diagnostics, tracker


# ===========================================================================
# Plotting
# ===========================================================================

def plot_conservation(diagnostics, tag):
    """Plot total gamma over time (should be flat)."""
    cons = diagnostics['conservation']
    ticks = [c['tick'] for c in cons]
    total = [c['total_gamma'] for c in cons]
    drift = [c['drift'] for c in cons]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    ax1.plot(ticks, total, 'b-', linewidth=0.5)
    ax1.set_ylabel('Total gamma')
    ax1.set_title(f'Gamma Conservation [{tag}]')

    ax2.plot(ticks, drift, 'r-', linewidth=0.5)
    ax2.set_ylabel('Relative drift')
    ax2.set_xlabel('Tick')
    ax2.set_yscale('log')

    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"conservation_{tag}.png", dpi=150)
    plt.close()


def plot_distances(diagnostics, tag):
    """Plot pairwise distances between peaks over time."""
    dists = diagnostics['distances']
    if not dists:
        return

    ticks = [d['tick'] for d in dists]
    keys = [k for k in dists[0].keys() if k != 'tick']

    fig, ax = plt.subplots(figsize=(12, 5))
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    for i, key in enumerate(sorted(keys)):
        vals = [d.get(key, None) for d in dists]
        ax.plot(ticks, vals, color=colors[i % len(colors)],
                linewidth=0.5, label=key)

    ax.set_xlabel('Tick')
    ax.set_ylabel('Hop distance')
    ax.set_title(f'Peak Distances [{tag}]')
    ax.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"distances_{tag}.png", dpi=150)
    plt.close()


def plot_particle_mass(diagnostics, tag):
    """Plot mass of each tracked particle over time."""
    peaks = diagnostics['peaks']
    if not peaks:
        return

    # Collect per-particle time series
    particle_data = {}
    for snap in peaks:
        for p in snap['particles']:
            pid = p['id']
            if pid not in particle_data:
                particle_data[pid] = {'ticks': [], 'mass': [],
                                       'peak_gamma': [], 'width': []}
            particle_data[pid]['ticks'].append(snap['tick'])
            particle_data[pid]['mass'].append(p['mass'])
            particle_data[pid]['peak_gamma'].append(p['peak_gamma'])
            particle_data[pid]['width'].append(p['width'])

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    colors = ['blue', 'red', 'green', 'orange', 'purple']

    for i, (pid, data) in enumerate(sorted(particle_data.items())):
        c = colors[i % len(colors)]
        ax1.plot(data['ticks'], data['mass'], color=c,
                 linewidth=0.5, label=f'P{pid}')
        ax2.plot(data['ticks'], data['peak_gamma'], color=c,
                 linewidth=0.5, label=f'P{pid}')
        ax3.plot(data['ticks'], data['width'], color=c,
                 linewidth=0.5, label=f'P{pid}')

    ax1.set_ylabel('Mass (sum gamma in radius)')
    ax1.set_title(f'Particle Properties [{tag}]')
    ax1.legend()
    ax2.set_ylabel('Peak gamma')
    ax2.legend()
    ax3.set_ylabel('Width (RMS hops)')
    ax3.set_xlabel('Tick')
    ax3.legend()

    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"particles_{tag}.png", dpi=150)
    plt.close()


def plot_radiation(diagnostics, tag):
    """Plot bound vs free gamma over time."""
    rad = diagnostics['radiation']
    if not rad:
        return

    ticks = [r['tick'] for r in rad]
    bound = [r['bound_gamma'] for r in rad]
    free = [r['free_gamma'] for r in rad]
    frac = [r['frac_bound'] for r in rad]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax1.plot(ticks, bound, 'b-', linewidth=0.5, label='Bound (matter)')
    ax1.plot(ticks, free, 'r-', linewidth=0.5, label='Free (radiation)')
    ax1.set_ylabel('Gamma')
    ax1.set_title(f'Radiation Budget [{tag}]')
    ax1.legend()

    ax2.plot(ticks, frac, 'b-', linewidth=0.5)
    ax2.set_ylabel('Fraction bound')
    ax2.set_xlabel('Tick')
    ax2.set_ylim(0, 1.05)

    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"radiation_{tag}.png", dpi=150)
    plt.close()


def plot_peak_shape(field, centers, tag, max_radius=15):
    """Plot radial gamma profile around each peak center."""
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['blue', 'red', 'green', 'orange', 'purple']

    for i, center in enumerate(centers):
        profile = field.radial_profile(center, max_radius)
        dists = [p['distance'] for p in profile]
        means = [p['mean_gamma'] for p in profile]
        ax.plot(dists, means, 'o-', color=colors[i % len(colors)],
                markersize=3, label=f'P{i} (node {center})')

    ax.set_xlabel('Hop distance from center')
    ax.set_ylabel('Mean gamma')
    ax.set_title(f'Peak Shape (radial profile) [{tag}]')
    ax.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"peak_shape_{tag}.png", dpi=150)
    plt.close()


def plot_summary(diagnostics, field, peak_centers, tag):
    """4-panel summary dashboard."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Conservation
    ax = axes[0, 0]
    cons = diagnostics['conservation']
    if cons:
        ticks_c = [c['tick'] for c in cons]
        total = [c['total_gamma'] for c in cons]
        ax.plot(ticks_c, total, 'b-', linewidth=0.5)
    ax.set_ylabel('Total gamma')
    ax.set_title('Conservation')

    # Panel 2: Distances
    ax = axes[0, 1]
    dists = diagnostics['distances']
    if dists:
        ticks_d = [d['tick'] for d in dists]
        keys = [k for k in dists[0].keys() if k != 'tick']
        colors_d = ['blue', 'red', 'green']
        for i, key in enumerate(sorted(keys)):
            vals = [d.get(key, None) for d in dists]
            ax.plot(ticks_d, vals, color=colors_d[i % len(colors_d)],
                    linewidth=0.5, label=key)
        ax.legend(fontsize=8)
    ax.set_ylabel('Hop distance')
    ax.set_title('Peak Distances')

    # Panel 3: Particle mass
    ax = axes[1, 0]
    peaks = diagnostics['peaks']
    if peaks:
        particle_data = {}
        for snap in peaks:
            for p in snap['particles']:
                pid = p['id']
                if pid not in particle_data:
                    particle_data[pid] = {'ticks': [], 'peak_gamma': []}
                particle_data[pid]['ticks'].append(snap['tick'])
                particle_data[pid]['peak_gamma'].append(p['peak_gamma'])
        colors_p = ['blue', 'red', 'green']
        for i, (pid, data) in enumerate(sorted(particle_data.items())):
            ax.plot(data['ticks'], data['peak_gamma'],
                    color=colors_p[i % len(colors_p)],
                    linewidth=0.5, label=f'P{pid}')
        ax.legend(fontsize=8)
    ax.set_ylabel('Peak gamma')
    ax.set_title('Peak Height')
    ax.set_xlabel('Tick')

    # Panel 4: Radiation budget
    ax = axes[1, 1]
    rad = diagnostics['radiation']
    if rad:
        ticks_r = [r['tick'] for r in rad]
        bound = [r['bound_gamma'] for r in rad]
        free = [r['free_gamma'] for r in rad]
        ax.plot(ticks_r, bound, 'b-', linewidth=0.5, label='Bound')
        ax.plot(ticks_r, free, 'r-', linewidth=0.5, label='Free')
        ax.legend(fontsize=8)
    ax.set_ylabel('Gamma')
    ax.set_title('Matter vs Radiation')
    ax.set_xlabel('Tick')

    fig.suptitle(f'Self-Gravitating Gamma [{tag}]', fontsize=14)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"summary_{tag}.png", dpi=150)
    plt.close()


# ===========================================================================
# Results save
# ===========================================================================

def make_serializable(obj):
    """Convert numpy types to Python natives for JSON."""
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def save_results(diagnostics, field, tracker, tag, params=None):
    """Save results to JSON."""
    results = {
        'params': params or {},
        'graph': {
            'n_nodes': field.n_nodes,
            'k': field.k,
            'alpha': field.alpha,
            'G': field.G,
            'type': field.graph_type,
            'graph_info': field.graph_info,
        },
        'conservation': diagnostics['conservation'],
        'distances': diagnostics['distances'],
        'peaks': diagnostics['peaks'],
        'radiation': diagnostics['radiation'],
        'particle_histories': {
            str(pid): make_serializable(hist)
            for pid, hist in tracker.histories.items()
        },
    }

    clean = make_serializable(results)
    path = RESULTS_DIR / f"results_{tag}.json"
    with open(path, 'w') as f:
        json.dump(clean, f, indent=2, default=str)
    print(f"  Results saved to: {path}")


# ===========================================================================
# Verification tests
# ===========================================================================

def run_verification():
    """Run all verification tests."""
    print("\n=== VERIFICATION TESTS ===\n")
    passed = 0
    failed = 0

    # Test 1: Conservation with G=0
    print("Test 1: Gamma conservation (G=0)")
    fg = SelfGravitatingField(1000, k=6, G=0.0)
    center = fg.n_nodes // 2
    fg.gamma[center] = 1000.0
    initial = fg.total_gamma()
    for _ in range(500):
        fg.spread()
    final = fg.total_gamma()
    drift = abs(final - initial) / initial
    if drift < 1e-10:
        print(f"  PASS: drift = {drift:.2e} < 1e-10")
        passed += 1
    else:
        print(f"  FAIL: drift = {drift:.2e} >= 1e-10")
        failed += 1

    # Test 2: Conservation with G>0
    print("Test 2: Gamma conservation (G=1.0)")
    fg2 = SelfGravitatingField(1000, k=6, G=1.0)
    center2 = fg2.n_nodes // 2
    fg2.gamma[center2] = 1000.0
    initial2 = fg2.total_gamma()
    for _ in range(500):
        fg2.spread()
    final2 = fg2.total_gamma()
    drift2 = abs(final2 - initial2) / initial2
    if drift2 < 1e-10:
        print(f"  PASS: drift = {drift2:.2e} < 1e-10")
        passed += 1
    else:
        print(f"  FAIL: drift = {drift2:.2e} >= 1e-10")
        failed += 1

    # Test 3: G=0 disperses peak toward uniform
    print("Test 3: G=0 disperses peak")
    fg3 = SelfGravitatingField(1000, k=6, G=0.0)
    center3 = fg3.n_nodes // 2
    fg3.gamma[center3] = 1000.0
    initial_peak = fg3.gamma[center3]
    for _ in range(2000):
        fg3.spread()
    final_peak = fg3.gamma[center3]
    uniform = fg3.total_gamma() / fg3.n_nodes
    ratio = final_peak / initial_peak
    # After 2000 ticks with alpha=1/6, peak should be nearly uniform
    if ratio < 0.01:
        print(f"  PASS: peak ratio = {ratio:.4f} < 0.01 "
              f"(peak={final_peak:.4f}, uniform={uniform:.4f})")
        passed += 1
    else:
        print(f"  FAIL: peak ratio = {ratio:.4f} >= 0.01")
        failed += 1

    # Test 4: G>0 retains peak better than G=0
    print("Test 4: G>0 retains peak (vs G=0 control)")
    fg4a = SelfGravitatingField(1000, k=6, G=0.0)
    fg4b = SelfGravitatingField(1000, k=6, G=1.0)
    center4 = fg4a.n_nodes // 2
    fg4a.gamma[center4] = 1000.0
    fg4b.gamma[center4] = 1000.0
    for _ in range(500):
        fg4a.spread()
        fg4b.spread()
    peak_g0 = fg4a.gamma[center4]
    peak_g1 = fg4b.gamma[center4]
    if peak_g1 > peak_g0 * 1.5:
        print(f"  PASS: G=1 peak ({peak_g1:.4f}) > 1.5x G=0 peak ({peak_g0:.4f})")
        passed += 1
    else:
        print(f"  FAIL: G=1 peak ({peak_g1:.4f}) not > 1.5x G=0 peak ({peak_g0:.4f})")
        failed += 1

    # Test 5: No negative gamma after spread
    print("Test 5: No negative gamma")
    fg5 = SelfGravitatingField(1000, k=6, G=5.0)
    center5 = fg5.n_nodes // 2
    fg5.gamma[center5] = 500.0
    # Also add small amounts elsewhere
    rng = np.random.default_rng(42)
    fg5.gamma += rng.uniform(0, 0.1, fg5.n_nodes)
    for _ in range(500):
        fg5.spread()
    min_gamma = np.min(fg5.gamma)
    if min_gamma >= -1e-15:
        print(f"  PASS: min gamma = {min_gamma:.2e} >= -1e-15")
        passed += 1
    else:
        print(f"  FAIL: min gamma = {min_gamma:.2e} < -1e-15")
        failed += 1

    # Test 6: Peak detection finds initialized peaks
    print("Test 6: Peak detection finds N initialized peaks")
    fg6 = SelfGravitatingField(8000, k=6, G=1.0)
    nodes6 = fg6.place_peaks_equilateral(separation=10, n_peaks=3)
    for node in nodes6:
        fg6.initialize_peak(node, total_mass=100.0, smooth_ticks=10)
    raw_peaks = fg6.find_peaks()
    particles = fg6.cluster_peaks(raw_peaks, merge_radius=3)
    if len(particles) == 3:
        print(f"  PASS: found {len(particles)} particles "
              f"(masses: {[round(p['mass'], 1) for p in particles]})")
        passed += 1
    else:
        print(f"  FAIL: found {len(particles)} particles, expected 3")
        failed += 1

    # Test 7: Mass measurement matches initialization
    print("Test 7: Mass measurement accuracy")
    fg7 = SelfGravitatingField(8000, k=6, G=1.0)
    center7 = fg7.n_nodes // 2
    fg7.initialize_peak(center7, total_mass=200.0, smooth_ticks=10)
    measured = fg7.measure_particle(center7, radius=8)
    total_in_field = fg7.total_gamma()
    # The particle measurement should capture most of the gamma
    mass_frac = measured['mass'] / total_in_field
    if mass_frac > 0.90:
        print(f"  PASS: captured {mass_frac*100:.1f}% of gamma "
              f"(measured={measured['mass']:.1f}, total={total_in_field:.1f})")
        passed += 1
    else:
        print(f"  FAIL: captured only {mass_frac*100:.1f}% of gamma")
        failed += 1

    # Test 8: alpha_eff is correct
    print("Test 8: Effective alpha decreases with gamma")
    fg8 = SelfGravitatingField(1000, k=6, G=2.0)
    fg8.gamma[0] = 100.0  # high gamma node
    fg8.gamma[1] = 0.0    # zero gamma node
    alpha_high = fg8.alpha / (1.0 + fg8.G * fg8.gamma[0])
    alpha_low = fg8.alpha / (1.0 + fg8.G * fg8.gamma[1])
    if alpha_low > alpha_high * 10:
        print(f"  PASS: alpha(g=0) = {alpha_low:.6f} >> "
              f"alpha(g=100) = {alpha_high:.6f}")
        passed += 1
    else:
        print(f"  FAIL: alpha ratio not large enough")
        failed += 1

    # Test 9: Symmetry -- two equal peaks approach symmetrically
    print("Test 9: Two equal peaks approach symmetrically")
    fg9 = SelfGravitatingField(8000, k=6, G=1.0)
    nodes9 = fg9.place_peaks_equilateral(separation=10, n_peaks=2)
    # Initialize both peaks simultaneously (place delta, then smooth once)
    fg9.gamma[nodes9[0]] = 100.0
    fg9.gamma[nodes9[1]] = 100.0
    saved_G = fg9.G
    fg9.G = 0.0
    for _ in range(10):
        fg9.spread()
    fg9.G = saved_G
    # Now measure at actual peak locations (find_peaks)
    raw9 = fg9.find_peaks()
    particles9 = fg9.cluster_peaks(raw9, merge_radius=3)
    mass_before = [p['mass'] for p in particles9[:2]]
    for _ in range(200):
        fg9.spread()
    raw9b = fg9.find_peaks()
    particles9b = fg9.cluster_peaks(raw9b, merge_radius=3)
    mass_after = [p['mass'] for p in particles9b[:2]]
    diff_after = abs(mass_after[0] - mass_after[1]) / max(mass_after[0], 0.01) \
        if len(mass_after) >= 2 else 0.0
    if len(mass_after) >= 2 and diff_after < 0.15:
        print(f"  PASS: masses symmetric after 200 ticks "
              f"(A={mass_after[0]:.1f}, B={mass_after[1]:.1f}, "
              f"diff={diff_after*100:.1f}%)")
        passed += 1
    else:
        ma = mass_after[0] if len(mass_after) >= 1 else 0
        mb = mass_after[1] if len(mass_after) >= 2 else 0
        print(f"  FAIL: masses asymmetric "
              f"(A={ma:.1f}, B={mb:.1f}, "
              f"diff={diff_after*100:.1f}%)")
        failed += 1

    # Test 10: G=0 with initialize_peak conserves total mass exactly
    print("Test 10: initialize_peak conserves mass")
    fg10 = SelfGravitatingField(8000, k=6, G=2.0)
    fg10.initialize_peak(fg10.n_nodes // 2, total_mass=500.0, smooth_ticks=30)
    total10 = fg10.total_gamma()
    drift10 = abs(total10 - 500.0) / 500.0
    if drift10 < 1e-10:
        print(f"  PASS: total gamma = {total10:.6f}, "
              f"drift = {drift10:.2e}")
        passed += 1
    else:
        print(f"  FAIL: total gamma = {total10:.6f}, "
              f"drift = {drift10:.2e}")
        failed += 1

    print(f"\n=== RESULTS: {passed} passed, {failed} failed "
          f"out of {passed + failed} ===\n")
    return failed == 0


# ===========================================================================
# Main orchestration
# ===========================================================================

def run_experiment(n_nodes, k, alpha, G, n_peaks, mass, masses,
                   separation, smooth_ticks, ticks,
                   measure_interval, log_interval, peak_radius,
                   seed, tag):
    """Run a self-gravitating gamma experiment."""

    print(f"\n{'='*70}")
    print(f"v6: Self-Gravitating Gamma on Graph")
    print(f"{'='*70}")
    print(f"  G = {G} (gravitational coupling)")
    print(f"  n_peaks = {n_peaks}, mass = {mass}")
    if masses:
        print(f"  per-peak masses = {masses}")
    print(f"  separation = {separation} hops")
    print(f"  ticks = {ticks}")
    print()

    # Build field
    field = SelfGravitatingField(n_nodes, k=k, alpha=alpha, G=G,
                                  seed=seed)
    avg_path, clustering = field.graph_stats(n_samples=100)
    print(f"  Graph stats: avg_path={avg_path:.1f}, "
          f"clustering={clustering:.4f}")

    # Place peaks
    peak_centers = field.place_peaks_equilateral(
        separation=separation, n_peaks=n_peaks)

    # Parse per-peak masses
    if masses:
        mass_list = [float(m) for m in masses.split(',')]
        assert len(mass_list) == n_peaks, \
            f"--masses has {len(mass_list)} values but --n-peaks is {n_peaks}"
    else:
        mass_list = [mass] * n_peaks

    # Initialize peaks
    print(f"\n  Initializing {n_peaks} peaks (smooth={smooth_ticks} ticks):")
    for i, (center, m) in enumerate(zip(peak_centers, mass_list)):
        field.initialize_peak(center, total_mass=m,
                               smooth_ticks=smooth_ticks)
        peak_g = field.gamma[center]
        print(f"    P{i} at node {center}: mass={m:.1f}, "
              f"peak_gamma={peak_g:.4f}")

    total_init = field.total_gamma()
    print(f"  Total gamma after init: {total_init:.4f} "
          f"(expected {sum(mass_list):.1f})")

    # Record initial peak shapes
    print(f"\n  Initial peak shapes:")
    for i, center in enumerate(peak_centers):
        profile = field.radial_profile(center, max_radius=8)
        print(f"    P{i}: " + " ".join(
            f"d={p['distance']}:{p['mean_gamma']:.3f}"
            for p in profile[:6]))

    # Plot initial peak shape
    plot_peak_shape(field, peak_centers, f"{tag}_initial")

    # Run simulation
    diagnostics, tracker = run_simulation(
        field, ticks,
        measure_interval=measure_interval,
        log_interval=log_interval)

    # Final state
    print(f"\n  Final state:")
    final_gamma = field.total_gamma()
    drift = abs(final_gamma - total_init) / total_init if total_init > 0 else 0
    print(f"    Total gamma: {final_gamma:.4f} (drift={drift:.2e})")
    print(f"    Peak gamma: {float(np.max(field.gamma)):.4f}")

    # Final peak detection
    raw_peaks = field.find_peaks()
    particles = field.cluster_peaks(raw_peaks, merge_radius=peak_radius)
    print(f"    Particles found: {len(particles)}")
    for p in particles:
        print(f"      P{p.get('id', '?')}: center={p['center']}, "
              f"mass={p['mass']:.2f}, peak={p['peak_gamma']:.4f}, "
              f"width={p['width']:.2f}")

    # Final peak shapes
    plot_peak_shape(field, peak_centers, f"{tag}_final")

    # Plots
    plot_conservation(diagnostics, tag)
    plot_distances(diagnostics, tag)
    plot_particle_mass(diagnostics, tag)
    plot_radiation(diagnostics, tag)
    plot_summary(diagnostics, field, peak_centers, tag)

    # Save
    params = {
        'n_nodes': field.n_nodes,
        'k': k,
        'alpha': field.alpha,
        'G': G,
        'n_peaks': n_peaks,
        'masses': mass_list,
        'separation': separation,
        'smooth_ticks': smooth_ticks,
        'ticks': ticks,
        'seed': seed,
    }
    save_results(diagnostics, field, tracker, tag, params)

    return diagnostics, tracker, field


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v6: Self-Gravitating Gamma on a Graph')

    parser.add_argument('--verify', action='store_true',
                        help='Run verification tests')
    parser.add_argument('--quick', action='store_true',
                        help='Quick mode: smaller graph, fewer ticks')

    # Graph
    parser.add_argument('--n-nodes', type=int, default=50000)
    parser.add_argument('--k', type=int, default=6)

    # Physics
    parser.add_argument('--alpha', type=float, default=None,
                        help='Base spread fraction (default: 1/k)')
    parser.add_argument('--G', type=float, default=1.0,
                        help='Gravitational coupling constant')

    # Initial conditions
    parser.add_argument('--n-peaks', type=int, default=3,
                        help='Number of initial gamma peaks')
    parser.add_argument('--mass', type=float, default=100.0,
                        help='Total gamma per peak (uniform)')
    parser.add_argument('--masses', type=str, default=None,
                        help='Comma-separated per-peak masses '
                             '(overrides --mass)')
    parser.add_argument('--separation', type=int, default=14,
                        help='Initial hop separation between peaks')
    parser.add_argument('--smooth-ticks', type=int, default=20,
                        help='Smoothing ticks for initialization')

    # Simulation
    parser.add_argument('--ticks', type=int, default=10000)
    parser.add_argument('--measure-interval', type=int, default=50)
    parser.add_argument('--log-interval', type=int, default=500)
    parser.add_argument('--peak-radius', type=int, default=5,
                        help='BFS radius for peak mass measurement')

    # Misc
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--tag', type=str, default=None,
                        help='Custom output tag')

    args = parser.parse_args()

    if args.verify:
        success = run_verification()
        return 0 if success else 1

    if args.quick:
        if args.n_nodes == 50000:
            args.n_nodes = 8000
        if args.ticks == 10000:
            args.ticks = 2000

    if args.alpha is None:
        args.alpha = 1.0 / args.k

    if args.tag is None:
        args.tag = f"G{args.G}_peaks{args.n_peaks}_m{args.mass}"

    run_experiment(
        n_nodes=args.n_nodes,
        k=args.k,
        alpha=args.alpha,
        G=args.G,
        n_peaks=args.n_peaks,
        mass=args.mass,
        masses=args.masses,
        separation=args.separation,
        smooth_ticks=args.smooth_ticks,
        ticks=args.ticks,
        measure_interval=args.measure_interval,
        log_interval=args.log_interval,
        peak_radius=args.peak_radius,
        seed=args.seed,
        tag=args.tag,
    )

    return 0


if __name__ == '__main__':
    exit(main())
