"""
Experiment #64_109 — Three-Body Dynamics on a Pure Graph
=========================================================
Tests whether gravity emerges from deposit-spread-follow on a random graph
WITHOUT spatial geometry. If yes: space is not fundamental — causal structure is.

Secondary question: does the Bremsstrahlung drain problem from Experiment 64
vanish when there is no lattice? On a graph, minimum distance is always 1 hop —
no zero-distance singularity, no gradient spike, no runaway.

Graph substrate: Watts-Strogatz small-world graph, 3D periodic lattice, or
lattice + Newman-Watts shortcuts.
Each entity deposits into its own field, follows gradient of other entities' fields.
Movement is discrete hops — no coordinates, no velocity vectors.

KEY FINDING (v1 — random graph):
  Gravity (attraction) DOES emerge on a pure graph — entities attract and converge.
  However, orbits do NOT form. Without spatial dimensions, there is no angular
  momentum: entities fall straight into each other and merge. The gradient is
  purely radial (pointing toward the attractor) and there is no perpendicular
  degree of freedom to sustain orbital motion.

  This is a PARTIAL PASS: gravity is topological (works on any connected graph),
  but stable orbits require dimensionality (at least 2 spatial dimensions providing
  a perpendicular escape route from the radial gradient).

  RAW 110 diagnoses the root cause: the Watts-Strogatz graph has local
  dimensionality D(n) ~ 0-1. Even with a non-zero gradient, the "steepest
  neighbor" in an unstructured neighborhood doesn't reliably correspond to
  the direction toward the source. On a structured lattice, perpendicular
  neighbors exist — the entity can orbit rather than collapse.

  v2 adds --graph-type lattice to test RAW 110 Prediction 1: "Structured
  graph recovers orbits."

  v2 also adds --temporal: edges have temporal length. Traversal takes as many
  ticks as it took to create the edge. Gradient accumulates as transit progress.
  Entity is COMMITTED during traversal (inertia). No KE>=1.0 threshold — any
  positive gradient eventually produces movement. Lattice edges cost 1 tick,
  shortcuts cost Manhattan distance. This prevents d=0 singularity and creates
  angular momentum from committed multi-tick traversals.

  spread_fraction = 1/k (c = 1 hop/tick) is the physically correct value, not a
  free parameter. Each tick, gamma propagates one hop — matching the lattice's
  1 cell/tick spreading speed. With k=6: alpha = 1/6 ≈ 0.167.

  See experiment_description.md for full analysis.

Usage:
    python three_body_graph.py --verify
    python three_body_graph.py --calibrate
    python three_body_graph.py --calibrate --quick --graph-type lattice
    python three_body_graph.py --calibrate --quick --graph-type lattice --temporal
    python three_body_graph.py --quick --graph-type lattice --temporal
    python three_body_graph.py --quick --graph-type lattice-nw --beta 0.05 --temporal
    python three_body_graph.py --quick --graph-type lattice
    python three_body_graph.py --quick --graph-type lattice-nw --beta 0.05
    python three_body_graph.py
    python three_body_graph.py --quick
    python three_body_graph.py --n-nodes 100000 --k 6 --beta 0.3
    python three_body_graph.py --dynamics-ticks 50000
    python three_body_graph.py --spread-fraction 0.005 --decay 0.9999

Date: February 2026
Substrate: Configurable — random graph (WS), 3D lattice, or lattice-NW
"""

import math
import json
import time
import argparse
import numpy as np
from pathlib import Path
from collections import deque

import networkx as nx
import scipy.sparse as sp

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS_DIR = Path(__file__).parent / "results"

import random


# ===========================================================================
# Amplitude Energy Analysis — Energy IS oscillation amplitude
# ===========================================================================

def compute_amplitude_envelope(distances, pair_key, window_size=20):
    """Sliding window max-min amplitude. This IS the energy.

    Energy isn't KE stored on the entity (always 1.0 in always-move).
    It's the amplitude of the distance oscillation. C swinging between
    d=2 and d=16 around the A-B binary — that swing IS the energy.
    Wide swing = high energy. Tight swing = low energy.
    """
    values = np.array([d[pair_key] for d in distances])
    ticks = np.array([d['tick'] for d in distances])
    n_windows = len(values) - window_size + 1
    if n_windows <= 0:
        return np.array([]), np.array([]), np.array([])

    center_ticks = np.array([ticks[i + window_size // 2] for i in range(n_windows)])
    amplitudes = np.array([values[i:i+window_size].max() - values[i:i+window_size].min()
                           for i in range(n_windows)])
    means = np.array([values[i:i+window_size].mean() for i in range(n_windows)])

    return center_ticks, amplitudes, means


def compute_energy_exchange(amp_ticks, amp_dict, corr_window=50):
    """Rolling cross-correlation between amplitude envelopes.

    Anti-correlation = energy transferring between pairs.
    One pair's amplitude grows while another's shrinks.
    """
    pairs = list(amp_dict.keys())
    results = {}
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            a, b = amp_dict[pairs[i]], amp_dict[pairs[j]]
            min_len = min(len(a), len(b))
            if min_len < corr_window:
                continue
            a, b = a[:min_len], b[:min_len]
            n_corr = min_len - corr_window + 1
            correlations = np.empty(n_corr)
            for k in range(n_corr):
                wa, wb = a[k:k+corr_window], b[k:k+corr_window]
                if np.std(wa) < 1e-10 or np.std(wb) < 1e-10:
                    correlations[k] = 0.0
                else:
                    correlations[k] = np.corrcoef(wa, wb)[0, 1]
            label = f"{pairs[i]} vs {pairs[j]}"
            results[label] = {
                'correlations': correlations,
                'frac_anticorrelated': float(np.mean(correlations < -0.3)),
                'mean_correlation': float(np.mean(correlations)),
            }
    return results


def compute_total_orbital_energy(amp_dict):
    """Sum of all pair amplitudes. If conserved -> roughly flat line."""
    if not amp_dict:
        return np.array([]), float('inf')
    min_len = min(len(v) for v in amp_dict.values())
    if min_len == 0:
        return np.array([]), float('inf')
    total = sum(v[:min_len] for v in amp_dict.values())
    cv = np.std(total) / np.mean(total) if np.mean(total) > 0 else float('inf')
    return total, cv


# ===========================================================================
# GammaFieldGraph — Sparse graph-based gamma field
# ===========================================================================

class GammaFieldGraph:
    """Gamma field on a graph substrate.

    Supports multiple graph types:
    - 'random': Watts-Strogatz small-world graph. D(n) ~ 0-1.
    - 'lattice': 3D periodic cubic lattice. D(n) = 3. All nodes degree 6.
      Coordinates used for construction only, then discarded.
    - 'lattice-nw': Lattice + Newman-Watts shortcuts (random edges added
      WITHOUT removing existing ones). Preserves D(n) = 3 while adding
      small-world routing. beta controls shortcut fraction.

    Each node holds scalar gamma values (one array per entity label).
    Spreading uses precomputed sparse matrix: S = (1-alpha)*I + (alpha/k)*A
    where A is the adjacency matrix and alpha = spread_fraction.

    NO coordinates for physics. All physics (spreading, gradient, movement)
    uses only adjacency — same code for all graph types.
    """

    def __init__(self, n_nodes, k=6, beta=0.3, spread_fraction=None,
                 decay=0.9999, seed=42, graph_type='random',
                 lattice_edge_weight=1):
        self.k = k
        self.beta = beta
        self.decay = decay
        self.seed = seed
        self.graph_type = graph_type
        self.graph_info = {}
        self.lattice_edge_weight = lattice_edge_weight

        # Edge weights for temporal traversal.
        # Lattice edges: weight = lattice_edge_weight (default 1).
        #   Weight 1 = movement at c (1 hop per tick of transit progress).
        #   Weight 10-50 = sub-light (entity committed for many ticks per hop).
        # NW shortcuts: weight = Manhattan distance * lattice_edge_weight
        #   (traversal costs proportionally more for longer shortcuts).
        # Random graph: weight = lattice_edge_weight (uniform).
        self.default_edge_weight = float(lattice_edge_weight)
        self.edge_weights = {}  # sparse: only non-default weights stored

        # Build graph based on type
        t0 = time.time()
        if graph_type == 'lattice' or graph_type == 'lattice-nw':
            side = round(n_nodes ** (1/3))
            actual_n = side ** 3
            print(f"  Generating {'lattice-nw' if graph_type == 'lattice-nw' else 'lattice'} "
                  f"graph: side={side}, N={actual_n} (periodic, D(n)=3, "
                  f"edge_weight={lattice_edge_weight})")
            G_grid = nx.grid_graph(dim=[side, side, side], periodic=True)

            # Build coordinate map (sorted for deterministic label assignment)
            sorted_nodes = sorted(G_grid.nodes())
            coord_map = {i: node for i, node in enumerate(sorted_nodes)}

            self.graph = nx.convert_node_labels_to_integers(G_grid, ordering='sorted')
            # Store coordinate map for placement (NOT used for physics)
            self.node_coords = coord_map  # int_node -> (x, y, z)
            self.coord_to_node = {v: k for k, v in coord_map.items()}
            self.side = side
            n_nodes = actual_n  # may differ from requested
            self.graph_info['side'] = side
            self.graph_info['actual_n'] = actual_n
            self.graph_info['lattice_edge_weight'] = lattice_edge_weight

            if graph_type == 'lattice-nw':
                # Add Newman-Watts shortcuts: random edges WITHOUT removing
                # existing ones. Preserves all lattice connectivity -> D(n)=3.
                # Each shortcut's temporal weight = lattice Manhattan distance
                # between its endpoints (periodic). Shortcuts don't cheat c.
                rng = np.random.default_rng(seed)
                n_edges = self.graph.number_of_edges()
                n_shortcuts = int(n_edges * beta)
                added = 0
                attempts = 0
                max_attempts = n_shortcuts * 10
                total_shortcut_weight = 0
                while added < n_shortcuts and attempts < max_attempts:
                    u = int(rng.integers(0, n_nodes))
                    v = int(rng.integers(0, n_nodes))
                    if u != v and not self.graph.has_edge(u, v):
                        # Temporal weight = lattice Manhattan distance * edge_weight
                        uc, vc = coord_map[u], coord_map[v]
                        lat_dist = sum(min(abs(a - b), side - abs(a - b))
                                       for a, b in zip(uc, vc))
                        w = lat_dist * lattice_edge_weight
                        self.graph.add_edge(u, v)
                        self.edge_weights[(u, v)] = w
                        self.edge_weights[(v, u)] = w
                        total_shortcut_weight += w
                        added += 1
                    attempts += 1
                avg_w = total_shortcut_weight / added if added > 0 else 0
                print(f"    Added {added} Newman-Watts shortcuts "
                      f"(beta={beta}, target={n_shortcuts}, "
                      f"avg_temporal_weight={avg_w:.1f})")
                self.graph_info['n_shortcuts'] = added
                self.graph_info['avg_shortcut_weight'] = avg_w

            # Coordinates used for construction only — now discarded.
            # coord_map goes out of scope. All physics uses adjacency only.
        else:
            # Default: Watts-Strogatz random graph
            print(f"  Generating Watts-Strogatz graph: N={n_nodes}, k={k}, "
                  f"beta={beta}, seed={seed}")
            self.graph = nx.watts_strogatz_graph(n_nodes, k, beta, seed=seed)
            self.graph_info['type'] = 'watts_strogatz'

        elapsed = time.time() - t0
        print(f"    Graph generated in {elapsed:.1f}s")

        self.n_nodes = n_nodes

        # spread_fraction = 1/k gives c = 1 hop/tick: each tick, a node shares
        # alpha/k = 1/k² of its gamma with each neighbor, propagating the signal
        # one hop per tick. This is NOT a tuning parameter — it's the speed of
        # light. On the lattice (Exp 64), gamma spreads 1 cell/tick; here we
        # match that with 1 hop/tick. Note: the mixing matrix amplitude per hop
        # (1/k² ≈ 0.028 for k=6) is weaker than the lattice's pressure
        # equalization (1/k ≈ 0.167), so gradients are ~k× weaker at the same
        # distance. Propagation speed is the same; coupling strength differs.
        if spread_fraction is None:
            spread_fraction = 1.0 / k  # c = 1 hop/tick
        self.spread_fraction = spread_fraction

        # Adjacency list for O(1) neighbor access
        self.neighbors = [list(self.graph.neighbors(i)) for i in range(n_nodes)]

        # Build sparse spread matrix.
        # S = (1-alpha)*I + alpha * A * D_inv  where D_inv = diag(1/degree_j)
        # Each node j distributes alpha/degree_j to each neighbor, keeping (1-alpha).
        # Column sums of S = 1 => total gamma conserved (before decay).
        print(f"  Building spread matrix (alpha={spread_fraction:.4f}, decay={decay})")
        t0 = time.time()
        A = nx.adjacency_matrix(self.graph, dtype=np.float64)  # CSR
        I = sp.eye(n_nodes, dtype=np.float64, format='csr')
        degrees = np.array(A.sum(axis=1)).flatten()
        degrees[degrees == 0] = 1.0  # avoid division by zero for isolated nodes
        D_inv = sp.diags(1.0 / degrees, format='csr')
        alpha = spread_fraction
        self.spread_matrix = (1.0 - alpha) * I + alpha * (A @ D_inv)
        self.spread_matrix = self.spread_matrix.tocsr()
        elapsed = time.time() - t0
        print(f"    Spread matrix built in {elapsed:.1f}s")

        # Per-entity fields
        self.fields = {}

    def add_field(self, label):
        """Register a per-entity gamma field."""
        self.fields[label] = np.zeros(self.n_nodes, dtype=np.float64)

    def deposit(self, label, node, amount):
        """Deposit gamma at a node into a specific entity's field."""
        self.fields[label][node] += amount

    def spread_all(self):
        """Spread all fields using precomputed sparse matrix, then apply decay."""
        for label in self.fields:
            self.fields[label] = self.spread_matrix @ self.fields[label]
            self.fields[label] *= self.decay

    def external_gamma_at(self, node, exclude_label):
        """Combined gamma at node from all fields except exclude_label."""
        total = 0.0
        for label, field in self.fields.items():
            if label != exclude_label:
                total += field[node]
        return total

    def gradient_at(self, node, exclude_label):
        """Gradient for entity at node: best neighbor direction and magnitude.

        Returns (best_neighbor, gradient_magnitude).
        Gradient = max_neighbor_external - current_external (can be negative!).
        Negative gradient at local maxima causes deceleration.
        Direction = neighbor node with highest external gamma.
        """
        current = self.external_gamma_at(node, exclude_label)
        best_neighbor = -1
        best_gamma = -1.0

        for nb in self.neighbors[node]:
            nb_gamma = self.external_gamma_at(nb, exclude_label)
            if nb_gamma > best_gamma:
                best_gamma = nb_gamma
                best_neighbor = nb

        grad_mag = max(0.0, best_gamma - current)
        return best_neighbor, grad_mag

    def gradient_at_excluding_node(self, node, exclude_label, excluded_node):
        """Like gradient_at but excludes a specific node from candidates (no-backtrack).

        Returns (best_neighbor, gradient_magnitude).
        """
        current = self.external_gamma_at(node, exclude_label)
        best_neighbor = -1
        best_gamma = -1.0

        for nb in self.neighbors[node]:
            if nb == excluded_node:
                continue
            nb_gamma = self.external_gamma_at(nb, exclude_label)
            if nb_gamma > best_gamma:
                best_gamma = nb_gamma
                best_neighbor = nb

        # If all neighbors are excluded, fall back to any neighbor
        if best_neighbor == -1:
            for nb in self.neighbors[node]:
                nb_gamma = self.external_gamma_at(nb, exclude_label)
                if nb_gamma > best_gamma:
                    best_gamma = nb_gamma
                    best_neighbor = nb

        grad_mag = max(0.0, best_gamma - current)
        return best_neighbor, grad_mag

    def hop_distance(self, a, b, max_dist=500):
        """BFS shortest path distance between nodes a and b.

        Returns distance or max_dist if not reachable within limit.
        """
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

    def edge_weight(self, u, v):
        """Temporal weight of edge (u, v).

        Lattice edges: lattice_edge_weight. NW shortcuts: Manhattan * edge_weight.
        Returns default_edge_weight for edges not in edge_weights dict.
        """
        return self.edge_weights.get((u, v), self.default_edge_weight)

    def total_gamma(self, label):
        """Total gamma in a single field."""
        return float(np.sum(self.fields[label]))

    def total_gamma_all(self):
        """Total gamma across all fields."""
        return sum(float(np.sum(f)) for f in self.fields.values())

    def graph_stats(self, n_samples=200):
        """Sampled average path length and clustering coefficient."""
        rng = np.random.default_rng(self.seed + 1000)
        nodes = rng.choice(self.n_nodes, size=min(n_samples, self.n_nodes), replace=False)
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
# GraphEntity — Discrete entity on graph
# ===========================================================================

class GraphEntity:
    """An entity that moves on a graph by following gamma gradients.

    Two movement modes:

    **Classic mode** (temporal=False): KE accumulates from gradient magnitude,
    spent on hops (1 KE per hop). Binary: KE >= 1 → move, KE < 1 → stuck.

    **Temporal mode** (temporal=True): Gradient accumulates as transit progress
    toward the next node. Traversal takes edge_weight ticks at gradient ~0.01.
    Entity is COMMITTED to a PATH of N edges (N = mass). Can't turn mid-path.
    At the end of the path, reads gradient, picks a new N-edge straight-line
    path. This creates inertia proportional to mass: heavier entities commit
    to longer paths, preserving angular momentum.

    Each edge in the path costs edge_weight ticks of gradient accumulation.
    Total commitment = mass * edge_weight ticks.

    Mass-conserving existence: during dynamics, the entity withdraws its
    deposit from the previous node and places it at the current node.
    """

    def __init__(self, label, start_node, deposit_amount=1.0, drain_deposit=0.5,
                 max_hops_per_tick=20, k_neighbors=6, color='blue',
                 temporal=False, mass=1):
        self.label = label
        self.node = start_node
        self.deposit_amount = deposit_amount
        self.drain_deposit = drain_deposit
        self.max_hops_per_tick = max_hops_per_tick
        self.color = color
        self.temporal = temporal
        self.mass = mass  # path length = number of edges per commitment

        self.ke = 0.0
        self.last_node = None
        self.hops_this_tick = 0
        self.prev_deposit_node = start_node  # for mass-conserving motion

        # Trajectory memory: recent nodes visited (angular momentum analog).
        self.recent_path = deque(maxlen=k_neighbors)
        self.k_neighbors = k_neighbors

        # Temporal traversal state
        self.committed_path = []     # list of nodes to visit (remaining path)
        self.transit_target = None   # next node in committed path
        self.transit_progress = 0.0  # accumulated gradient toward target
        self.transit_weight = 1.0    # temporal weight of current edge

        self.trajectory = []

    def read_gradient(self, field_graph):
        """Read gradient at current position from external fields.

        Returns (target_neighbor, gradient_magnitude).
        Uses trajectory memory: excludes recently visited nodes from candidates.
        """
        excluded = set(self.recent_path)
        if excluded:
            return self._gradient_excluding_set(field_graph, self.node, excluded)
        return field_graph.gradient_at(self.node, self.label)

    def _gradient_excluding_set(self, field_graph, node, excluded_nodes):
        """Gradient excluding a set of nodes (trajectory memory)."""
        current = field_graph.external_gamma_at(node, self.label)
        best_nb = -1
        best_gamma = -1.0

        # First try: neighbors not in excluded set
        for nb in field_graph.neighbors[node]:
            if nb in excluded_nodes:
                continue
            nb_gamma = field_graph.external_gamma_at(nb, self.label)
            if nb_gamma > best_gamma:
                best_gamma = nb_gamma
                best_nb = nb

        # Fallback: any neighbor
        if best_nb == -1:
            for nb in field_graph.neighbors[node]:
                nb_gamma = field_graph.external_gamma_at(nb, self.label)
                if nb_gamma > best_gamma:
                    best_gamma = nb_gamma
                    best_nb = nb

        grad_mag = max(0.0, best_gamma - current)
        return best_nb, grad_mag

    def accumulate(self, grad_mag):
        """Add gradient magnitude to kinetic energy (always >= 0)."""
        self.ke += grad_mag

    def plan_path(self, field_graph):
        """Plan a straight-line path of self.mass edges from current position.

        Reads gradient to pick direction, then continues straight for mass edges.
        On lattice: uses coordinates to compute "straight" (same direction vector).
        On other graphs: follows steepest at each step.

        Returns list of nodes to visit (not including current node).
        """
        target_nb, grad_mag = self.read_gradient(field_graph)
        if target_nb < 0 or grad_mag == 0:
            return []

        path = [target_nb]
        if self.mass <= 1:
            return path

        # Lattice: straight line in the initial hop direction
        if hasattr(field_graph, 'node_coords') and hasattr(field_graph, 'side'):
            side = field_graph.side
            cur_c = field_graph.node_coords[self.node]
            next_c = field_graph.node_coords[target_nb]
            # Direction = periodic difference (each component is -1, 0, or +1)
            direction = tuple(
                (b - a + side) % side if (b - a + side) % side <= side // 2
                else (b - a + side) % side - side
                for a, b in zip(cur_c, next_c)
            )

            current = target_nb
            for _ in range(self.mass - 1):
                cur_coord = field_graph.node_coords[current]
                next_coord = tuple((c + d) % side for c, d in zip(cur_coord, direction))
                if next_coord in field_graph.coord_to_node:
                    nxt = field_graph.coord_to_node[next_coord]
                    path.append(nxt)
                    current = nxt
                else:
                    break
        else:
            # Non-lattice fallback: follow steepest at each step
            current = target_nb
            for _ in range(self.mass - 1):
                nbs = list(field_graph.graph.neighbors(current))
                best_nb, best_val = -1, -1.0
                for nb in nbs:
                    val = field_graph.external_gamma_at(nb, self.label)
                    if val > best_val:
                        best_val = val
                        best_nb = nb
                if best_nb >= 0:
                    path.append(best_nb)
                    current = best_nb
                else:
                    break

        return path

    def plan_path_stochastic(self, field_graph):
        """Plan a path of self.mass edges — argmax when gradient exists, random when flat.

        If the gradient provides direction (best neighbor distinguishable),
        follow it deterministically (argmax). Random choice ONLY when all
        neighbors are truly equal (no gradient information).

        Always returns a path — entity always moves.
        """
        # Try argmax first (uses trajectory memory to avoid backtracking)
        path = self.plan_path(field_graph)
        if path:
            return path

        # Gradient is zero — pick randomly among neighbors
        nbs = list(field_graph.graph.neighbors(self.node))
        if not nbs:
            return []

        first_nb = nbs[np.random.randint(len(nbs))]

        path = [first_nb]
        if self.mass <= 1:
            return path

        # Lattice: straight line in the random direction
        if hasattr(field_graph, 'node_coords') and hasattr(field_graph, 'side'):
            side = field_graph.side
            cur_c = field_graph.node_coords[self.node]
            next_c = field_graph.node_coords[first_nb]
            direction = tuple(
                (b - a + side) % side if (b - a + side) % side <= side // 2
                else (b - a + side) % side - side
                for a, b in zip(cur_c, next_c)
            )

            current = first_nb
            for _ in range(self.mass - 1):
                cur_coord = field_graph.node_coords[current]
                next_coord = tuple((c + d) % side for c, d in zip(cur_coord, direction))
                if next_coord in field_graph.coord_to_node:
                    nxt = field_graph.coord_to_node[next_coord]
                    path.append(nxt)
                    current = nxt
                else:
                    break
        else:
            # Non-lattice: random walk
            current = first_nb
            for _ in range(self.mass - 1):
                step_nbs = list(field_graph.graph.neighbors(current))
                if not step_nbs:
                    break
                nxt = step_nbs[np.random.randint(len(step_nbs))]
                path.append(nxt)
                current = nxt

        return path

    def advance_always_move(self, field_graph, occupied_nodes=None):
        """Always-move: entity hops every tick. No exceptions.

        Movement is existence. Gradient is preference, not permission.

        Each tick:
        1. If no committed path, plan one (softmax-sampled direction, mass edges)
        2. Hop to next node in path (always, 1 hop/tick)
        3. At end of path, plan new path immediately

        At zero gradient (d=0): softmax produces uniform probabilities → random walk.
        At strong gradient: softmax is nearly deterministic → directed movement.
        """
        self.hops_this_tick = 0

        # Plan path if needed
        if not self.committed_path:
            self.committed_path = self.plan_path_stochastic(field_graph)

        if not self.committed_path:
            return  # isolated node (shouldn't happen)

        target = self.committed_path[0]

        # Exclusion check (optional, separate toggle)
        if occupied_nodes and target in occupied_nodes:
            # Bounce: cancel path, replan next tick
            self.committed_path = []
            return

        # Hop (always, every tick)
        field_graph.deposit(self.label, self.node, self.drain_deposit)
        self.recent_path.append(self.node)
        self.last_node = self.node
        self.node = target
        self.hops_this_tick = 1
        self.committed_path.pop(0)

        self.ke = 1.0  # always moving at c = 1 hop/tick

    def advance_temporal(self, field_graph, occupied_nodes=None):
        """Temporal traversal with path commitment (mass = path length).

        Each tick:
        1. If no committed path, plan one (mass edges in gradient direction)
        2. Add gradient magnitude to transit_progress
        3. If progress >= current edge weight: hop, advance to next edge in path
        4. At end of path: plan new path (re-read gradient)

        The entity is COMMITTED to the full path — it cannot turn mid-path.
        Mass = path length = inertia. Heavier entities commit to longer paths,
        preserving direction for more hops → angular momentum conservation.

        If occupied_nodes is provided (exclusion mode), the entity cannot hop
        to a node occupied by another entity. On collision: path is cancelled,
        excess KE is retained, and entity replans next tick.
        """
        self.hops_this_tick = 0

        # Plan path if needed
        if not self.committed_path:
            self.committed_path = self.plan_path(field_graph)
            if self.committed_path:
                self.transit_target = self.committed_path[0]
                self.transit_weight = field_graph.edge_weight(
                    self.node, self.committed_path[0])

        # Read gradient for accumulation (always from current position)
        _, grad_mag = self.read_gradient(field_graph)
        self.transit_progress += grad_mag

        # Process hops along committed path
        while (self.transit_target is not None and
               self.transit_progress >= self.transit_weight and
               self.hops_this_tick < self.max_hops_per_tick):

            excess = self.transit_progress - self.transit_weight

            # Exclusion: cannot hop to an occupied node
            if occupied_nodes and self.transit_target in occupied_nodes:
                # Bounce: cancel path, keep excess KE, replan next tick
                self.committed_path = []
                self.transit_target = None
                self.transit_progress = excess
                break

            # Deposit drain at departed node
            field_graph.deposit(self.label, self.node, self.drain_deposit)

            # Arrive at next node in path
            self.recent_path.append(self.node)
            self.last_node = self.node
            self.node = self.transit_target
            self.hops_this_tick += 1
            self.transit_progress = excess

            # Advance path
            self.committed_path.pop(0)

            if self.committed_path:
                # More edges in path — continue committed
                self.transit_target = self.committed_path[0]
                self.transit_weight = field_graph.edge_weight(
                    self.node, self.committed_path[0])
            else:
                # Path complete — plan new one if excess momentum
                self.transit_target = None
                if excess > 0:
                    self.committed_path = self.plan_path(field_graph)
                    if self.committed_path:
                        self.transit_target = self.committed_path[0]
                        self.transit_weight = field_graph.edge_weight(
                            self.node, self.committed_path[0])
                    else:
                        break
                else:
                    break

        self.ke = self.transit_progress  # diagnostics compatibility

    def move(self, field_graph):
        """Take min(floor(KE), max_hops_per_tick) greedy hops along gradient.

        Uses trajectory memory (recent_path) to avoid revisiting recently
        traversed nodes. This creates angular-momentum-like behavior: the
        entity is forced to take longer paths around attractors rather than
        falling straight in and bouncing back.

        Each hop:
        1. Evaluate external gamma at neighbors not in recent_path
        2. Move to highest-gamma non-recent neighbor
        3. Deposit drain_deposit into own field at departed node
        4. Deduct 1 KE
        """
        n_hops = min(int(self.ke), self.max_hops_per_tick)
        self.hops_this_tick = 0

        for _ in range(n_hops):
            excluded = set(self.recent_path)
            best_nb, _ = self._gradient_excluding_set(
                field_graph, self.node, excluded)

            if best_nb == -1:
                break

            # Deposit drain at departed node (Bremsstrahlung)
            field_graph.deposit(self.label, self.node, self.drain_deposit)

            # Move
            self.recent_path.append(self.node)
            self.last_node = self.node
            self.node = best_nb
            self.ke -= 1.0
            self.hops_this_tick += 1

        # Excess KE beyond max_hops_per_tick is lost (radiated as drain)
        if self.ke > 0 and self.hops_this_tick >= self.max_hops_per_tick:
            excess = self.ke - (self.ke % 1.0)  # integer part of remaining KE
            if excess > 0:
                field_graph.deposit(self.label, self.node, self.drain_deposit * excess)
                self.ke -= excess

        # KE retains fractional part
        self.ke = max(0.0, self.ke)

    def deposit_formation(self, field_graph):
        """Formation deposit: accumulate gamma at current node (no withdrawal)."""
        field_graph.deposit(self.label, self.node, self.deposit_amount)

    def deposit_dynamics(self, field_graph):
        """Mass-conserving existence deposit.

        Withdraw deposit_amount from previous node, deposit at current node.
        The gamma well FOLLOWS the entity. Capped at available gamma to
        prevent going negative (the deficit is gravitational radiation).
        """
        # Withdraw from previous position
        prev = self.prev_deposit_node
        available = field_graph.fields[self.label][prev]
        withdraw = min(self.deposit_amount, available)
        field_graph.fields[self.label][prev] -= withdraw

        # Deposit at current position
        field_graph.deposit(self.label, self.node, self.deposit_amount)

        self.prev_deposit_node = self.node

    def record(self, tick, field_graph, distances=None):
        """Record state for diagnostics."""
        self.trajectory.append({
            'tick': tick,
            'node': self.node,
            'ke': self.ke,
            'hops': self.hops_this_tick,
            'field_total': field_graph.total_gamma(self.label),
        })


# ===========================================================================
# Mass Entity — Mass as Commit Time (v = c/M)
# ===========================================================================

class SnakeEntity:
    """An entity where mass = ticks between commits. v = c/M.

    The entity takes M ticks to commit its state. Each tick it deposits
    gamma at its current position (building its well deeper). Every M ticks
    it reads the gradient, hops 1 position, and resets the counter.

    This directly solves v=c:
    - mass=1: moves every tick → v = c
    - mass=2: moves every 2 ticks → v = c/2
    - mass=5: moves every 5 ticks → v = c/5

    Deposit footprint is naturally proportional to mass: the entity
    sits at each position for M ticks, depositing M × deposit_amount
    before moving on. Heavier = deeper well = stronger gravity.

    Trit compatible: 1 decision per commit (every M ticks).
    """

    def __init__(self, label, start_node, field_graph, deposit_amount=1.0,
                 drain_deposit=0.5, k_neighbors=6, color='blue', mass=2):
        self.label = label
        self.field_graph = field_graph
        self.mass = mass
        self.deposit_amount = deposit_amount
        self.drain_deposit = drain_deposit
        self.color = color
        self.k_neighbors = k_neighbors

        # Single node position
        self.node = start_node
        self.prev_deposit_node = start_node

        # Commit counter: entity moves when this reaches mass
        self.commit_counter = 0

        # Trajectory memory: avoid backtracking
        self.recent_path = deque(maxlen=k_neighbors)

        # Diagnostics
        self.trajectory = []
        self.ke = 0.0
        self.hops_this_tick = 0
        self.max_hops_per_tick = 1

    def _read_gradient_at(self, node, excluded_nodes=None):
        """Read external gradient at a given node.

        Returns (best_neighbor, gradient_magnitude).
        """
        fg = self.field_graph
        current_gamma = fg.external_gamma_at(node, self.label)

        candidates = list(fg.neighbors[node])
        if excluded_nodes:
            filtered = [n for n in candidates if n not in excluded_nodes]
            if filtered:
                candidates = filtered

        if not candidates:
            return -1, 0.0

        best_nb = -1
        best_gamma = -1.0
        for nb in candidates:
            nb_gamma = fg.external_gamma_at(nb, self.label)
            if nb_gamma > best_gamma:
                best_gamma = nb_gamma
                best_nb = nb

        grad_mag = max(0.0, best_gamma - current_gamma)
        return best_nb, grad_mag

    def advance_snake(self):
        """Commit-counter movement: move 1 hop every M ticks.

        Each tick:
        1. Increment commit_counter
        2. If commit_counter >= mass: READ gradient, HOP 1 position, RESET
        3. Otherwise: stay put (still committing state)

        Returns 1 if entity moved this tick, 0 otherwise.
        """
        self.hops_this_tick = 0
        self.commit_counter += 1

        if self.commit_counter >= self.mass:
            # COMMIT: read gradient, hop 1 position
            self.commit_counter = 0

            excluded = set(self.recent_path)
            target_nb, grad_mag = self._read_gradient_at(self.node, excluded)

            if target_nb < 0 or grad_mag == 0:
                # Zero gradient — pick random neighbor
                nbs = list(self.field_graph.neighbors[self.node])
                if nbs:
                    target_nb = nbs[np.random.randint(len(nbs))]
                else:
                    return 0

            self.recent_path.append(self.node)
            self.node = target_nb
            self.hops_this_tick = 1
            self.ke = 1.0 / self.mass  # effective speed = c/M
            return 1

        # Not yet committed — stay put
        self.ke = 0.0
        return 0

    def deposit_formation(self, field_graph):
        """Formation deposit: deposit at current position."""
        field_graph.deposit(self.label, self.node, self.deposit_amount)

    def deposit_dynamics(self, field_graph):
        """Mass-conserving existence deposit.

        Withdraw from previous position, deposit at current position.
        Entity sits at each position for M ticks → M deposits per position.
        """
        prev = self.prev_deposit_node
        available = field_graph.fields[self.label][prev]
        withdraw = min(self.deposit_amount, available)
        field_graph.fields[self.label][prev] -= withdraw

        field_graph.deposit(self.label, self.node, self.deposit_amount)
        self.prev_deposit_node = self.node

    def record(self, tick, field_graph, distances=None):
        """Record state for diagnostics."""
        self.trajectory.append({
            'tick': tick,
            'node': self.node,
            'ke': self.ke,
            'hops': self.hops_this_tick,
            'field_total': field_graph.total_gamma(self.label),
        })

    def read_gradient(self, field_graph):
        """Compatibility: read gradient at current position."""
        excluded = set(self.recent_path)
        return self._read_gradient_at(self.node, excluded)


# ===========================================================================
# Entity Placement
# ===========================================================================

def place_entities_apart(field_graph, n_entities=3, min_separation=10,
                         max_separation=None, seed=42):
    """Place entities on graph nodes with target hop separation.

    Uses BFS to find nodes with min_separation <= distance <= max_separation.
    If max_separation is None, uses 2 * min_separation.
    Returns list of node indices.
    """
    rng = np.random.default_rng(seed)
    if max_separation is None:
        max_separation = min_separation * 2
    placed = []

    # First entity: random node
    first = int(rng.integers(0, field_graph.n_nodes))
    placed.append(first)

    attempts = 0
    max_attempts = 2000

    while len(placed) < n_entities and attempts < max_attempts:
        candidate = int(rng.integers(0, field_graph.n_nodes))
        ok = True
        for p in placed:
            d = field_graph.hop_distance(candidate, p, max_dist=max_separation + 1)
            if d < min_separation or d > max_separation:
                ok = False
                break
        if ok:
            placed.append(candidate)
        attempts += 1

    if len(placed) < n_entities:
        print(f"  WARNING: Could only place {len(placed)}/{n_entities} entities "
              f"with separation {min_separation}-{max_separation}. Relaxing bounds.")
        return place_entities_apart(field_graph, n_entities,
                                    max(2, min_separation - 2),
                                    max_separation + 5, seed + 1)

    # Log actual separations
    print(f"  Placed {n_entities} entities (target separation: {min_separation}-{max_separation}):")
    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            d = field_graph.hop_distance(placed[i], placed[j])
            print(f"    Node {placed[i]} <-> Node {placed[j]}: {d} hops")

    return placed


def place_equilateral(field_graph, separation, seed=42):
    """Place 3 entities in an equilateral triangle on a lattice graph.

    Uses lattice coordinates: A=(cx, cy, cz), B=(cx+d, cy, cz),
    C=(cx+d//2, cy+d//2, cz) gives Manhattan distance d between all pairs
    (requires even d). Coordinates are periodic.

    Returns (nodes, tangential_neighbors) where tangential_neighbors[i] is
    the neighbor of nodes[i] that preserves distances to the other two
    (perpendicular to radial direction), with consistent rotational sense.
    """
    assert hasattr(field_graph, 'node_coords'), \
        "Equilateral placement requires lattice graph (has node_coords)"
    s = field_graph.side
    d = separation
    if d % 2 != 0:
        d += 1  # need even d for exact equilateral
        print(f"  Adjusted separation to {d} (must be even for equilateral)")

    # Center the triangle in the lattice
    cx, cy, cz = s // 2, s // 2, s // 2

    # Equilateral triangle in xy-plane (Manhattan distance d between all pairs)
    coords = [
        ((cx) % s, (cy) % s, cz % s),
        ((cx + d) % s, (cy) % s, cz % s),
        ((cx + d // 2) % s, (cy + d // 2) % s, cz % s),
    ]
    nodes = [field_graph.coord_to_node[c] for c in coords]

    # Verify equilateral
    dists = []
    for i in range(3):
        for j in range(i + 1, 3):
            dist = field_graph.hop_distance(nodes[i], nodes[j])
            dists.append(dist)
    print(f"  Equilateral placement (d={d}):")
    labels = ["A", "B", "C"]
    idx = 0
    for i in range(3):
        for j in range(i + 1, 3):
            print(f"    {labels[i]}-{labels[j]}: {dists[idx]} hops")
            idx += 1

    # Find tangential neighbors: for each entity, pick the neighbor that
    # preserves sum of distances to the other two (delta ≈ 0) AND creates
    # consistent CCW rotation in the xy-plane.
    # CCW tangential directions for our triangle:
    #   A at (cx, cy): tangent = +y direction
    #   B at (cx+d, cy): tangent = -y direction
    #   C at (cx+d/2, cy+d/2): tangent = +x direction
    tangent_coords = [
        ((cx) % s, (cy + 1) % s, cz % s),          # A: +y
        ((cx + d) % s, (cy - 1) % s, cz % s),      # B: -y
        ((cx + d // 2 + 1) % s, (cy + d // 2) % s, cz % s),  # C: +x
    ]
    tangential = [field_graph.coord_to_node[c] for c in tangent_coords]

    # Verify tangential neighbors are actual graph neighbors
    for i, (n, t) in enumerate(zip(nodes, tangential)):
        assert field_graph.graph.has_edge(n, t), \
            f"Tangential node {t} is not a neighbor of {n}"
        # Check distance preservation
        others = [nodes[j] for j in range(3) if j != i]
        d_before = sum(field_graph.hop_distance(n, o) for o in others)
        d_after = sum(field_graph.hop_distance(t, o) for o in others)
        delta = d_after - d_before
        print(f"    {labels[i]} tangent: node {n} -> {t} "
              f"(delta_d={delta:+d})")

    return nodes, tangential


# ===========================================================================
# Formation Phase
# ===========================================================================

def run_formation(field_graph, entities, formation_ticks, log_interval=100):
    """Formation phase: entities deposit (no movement), fields spread.

    Builds gamma wells at starting positions.
    """
    print(f"  Formation: {formation_ticks} ticks")
    t0 = time.time()

    for tick in range(formation_ticks):
        for entity in entities:
            entity.deposit_formation(field_graph)
        field_graph.spread_all()

        if (tick + 1) % log_interval == 0:
            elapsed = time.time() - t0
            rate = (tick + 1) / elapsed if elapsed > 0 else 0
            gamma_total = field_graph.total_gamma_all()
            print(f"    Formation tick {tick + 1:5d}/{formation_ticks} "
                  f"({elapsed:6.1f}s, {rate:.0f} t/s) "
                  f"gamma_total={gamma_total:.2f}")

    elapsed = time.time() - t0
    gamma_total = field_graph.total_gamma_all()
    print(f"  Formation done in {elapsed:.1f}s, gamma_total={gamma_total:.2f}")


# ===========================================================================
# Dynamics Phase
# ===========================================================================

def run_dynamics(field_graph, entities, dynamics_ticks, log_interval=100,
                 distance_interval=50, close_encounter_threshold=2,
                 temporal=False, exclusion=False, always_move=False):
    """Main dynamics loop.

    Classic mode: SPREAD -> HALF-KICK -> MOVE -> HALF-KICK -> DEPOSIT
    Temporal mode: SPREAD -> ADVANCE (gradient drives transit progress) -> DEPOSIT
    Always-move mode: SPREAD -> HOP (softmax-sampled, every tick) -> DEPOSIT

    If exclusion=True: entities cannot hop to a node occupied by another entity.

    Returns diagnostics dict.
    """
    diagnostics = {
        'energy': [],
        'distances': [],
        'events': [],
        'speeds': [],
        'core_speeds': {e.label: [] for e in entities},
    }

    # Detect if we're using snake entities
    is_snake = any(isinstance(e, SnakeEntity) for e in entities)

    print(f"  Dynamics: {dynamics_ticks} ticks, log_interval={log_interval}, "
          f"distance_interval={distance_interval}, snake={is_snake}")
    t0 = time.time()
    n_close_encounters = 0

    for tick in range(dynamics_ticks):
        # === COMMIT: spread all fields ===
        field_graph.spread_all()

        if always_move:
            # === ALWAYS-MOVE MODE ===
            # Every tick, every entity hops. Movement is existence.
            for entity in entities:
                if is_snake:
                    core_moved = entity.advance_snake()
                    diagnostics['core_speeds'][entity.label].append(core_moved)
                else:
                    if exclusion:
                        occupied = {e.node for e in entities if e is not entity}
                    else:
                        occupied = None
                    entity.advance_always_move(field_graph, occupied_nodes=occupied)
                    diagnostics['core_speeds'][entity.label].append(entity.hops_this_tick)
        elif temporal:
            # === TEMPORAL MODE ===
            # Gradient drives transit progress. Entity committed during traversal.
            for entity in entities:
                if exclusion:
                    occupied = {e.node for e in entities if e is not entity}
                else:
                    occupied = None
                entity.advance_temporal(field_graph, occupied_nodes=occupied)
        else:
            # === CLASSIC MODE: leapfrog half-kick ===
            grad_mags = {}
            for entity in entities:
                _, grad_mag = entity.read_gradient(field_graph)
                entity.accumulate(grad_mag * 0.5)
                grad_mags[entity.label] = grad_mag
            for entity in entities:
                entity.move(field_graph)
            for entity in entities:
                _, grad_mag = entity.read_gradient(field_graph)
                entity.accumulate(grad_mag * 0.5)
                grad_mags[entity.label] = (grad_mags[entity.label] + grad_mag) / 2.0

        # === WRITE: mass-conserving existence deposits ===
        for entity in entities:
            entity.deposit_dynamics(field_graph)

        # Record entity states
        for entity in entities:
            entity.record(tick, field_graph)

        # === DIAGNOSTICS ===
        if (tick + 1) % log_interval == 0:
            # Energy: KE per entity + field totals
            energy_entry = {'tick': tick + 1}
            total_ke = 0.0
            for entity in entities:
                energy_entry[f"KE_{entity.label}"] = entity.ke
                total_ke += entity.ke
            energy_entry['KE_total'] = total_ke
            energy_entry['gamma_total'] = field_graph.total_gamma_all()
            for entity in entities:
                energy_entry[f"gamma_{entity.label}"] = field_graph.total_gamma(entity.label)
            diagnostics['energy'].append(energy_entry)

            # Speeds
            speed_entry = {'tick': tick + 1}
            for entity in entities:
                speed_entry[entity.label] = entity.hops_this_tick
            diagnostics['speeds'].append(speed_entry)

            # Progress
            elapsed = time.time() - t0
            rate = (tick + 1) / elapsed if elapsed > 0 else 0
            if is_snake:
                # Show rolling core speed for snake entities
                body_info = "  ".join(
                    f"{e.label}:core_v={np.mean(diagnostics['core_speeds'][e.label][-20:]):.2f}"
                    for e in entities
                )
            else:
                body_info = "  ".join(
                    f"{e.label}:h={e.hops_this_tick},ke={e.ke:.2f}"
                    for e in entities
                )
            print(f"    Tick {tick + 1:6d}/{dynamics_ticks} "
                  f"({elapsed:6.1f}s, {rate:.0f} t/s) {body_info}")

        # === DISTANCES (expensive BFS, do less often) ===
        if (tick + 1) % distance_interval == 0:
            dist_entry = {'tick': tick + 1}
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    key = f"{entities[i].label}-{entities[j].label}"
                    d = field_graph.hop_distance(entities[i].node, entities[j].node)
                    dist_entry[key] = d

                    if d <= close_encounter_threshold:
                        n_close_encounters += 1
                        event = (f"CLOSE ENCOUNTER: {entities[i].label}-"
                                 f"{entities[j].label} at tick {tick+1}, d={d} hops")
                        diagnostics['events'].append({
                            'type': 'close_encounter',
                            'entities': [entities[i].label, entities[j].label],
                            'tick': tick + 1,
                            'distance': d,
                            'msg': event,
                        })
                        if n_close_encounters <= 20:
                            print(f"    *** {event}")

            diagnostics['distances'].append(dist_entry)

    elapsed = time.time() - t0
    print(f"  Dynamics done in {elapsed:.1f}s")
    print(f"  Close encounters (d <= {close_encounter_threshold}): {n_close_encounters}")
    return diagnostics


# ===========================================================================
# Plotting
# ===========================================================================

def plot_distances(diagnostics, tag):
    """Hop distances between all pairs vs tick."""
    if not diagnostics['distances']:
        return

    fig, ax = plt.subplots(figsize=(12, 5))
    ticks = [d['tick'] for d in diagnostics['distances']]
    pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
    colors_cycle = ['red', 'green', 'blue', 'orange', 'purple']

    for i, key in enumerate(pair_keys):
        vals = [d.get(key, 0) for d in diagnostics['distances']]
        ax.plot(ticks, vals, '-', color=colors_cycle[i % len(colors_cycle)],
                linewidth=0.8, label=key)

    ax.set_xlabel("Tick")
    ax.set_ylabel("Hop Distance")
    ax.set_title(f"Pairwise Distances — {tag}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"distances_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: distances_{tag}.png")


def plot_speeds(diagnostics, entities, tag):
    """Hops per tick for each entity."""
    if not diagnostics['speeds']:
        return

    fig, ax = plt.subplots(figsize=(12, 5))
    ticks = [s['tick'] for s in diagnostics['speeds']]
    colors_cycle = ['red', 'green', 'blue']

    for i, entity in enumerate(entities):
        vals = [s.get(entity.label, 0) for s in diagnostics['speeds']]
        ax.plot(ticks, vals, '-', color=colors_cycle[i % len(colors_cycle)],
                linewidth=0.8, label=entity.label, alpha=0.8)

    ax.set_xlabel("Tick")
    ax.set_ylabel("Hops / Tick")
    ax.set_title(f"Entity Speeds — {tag}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"speeds_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: speeds_{tag}.png")


def plot_energy(diagnostics, entities, tag):
    """KE per entity + total field gamma vs tick."""
    if not diagnostics['energy']:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"Energy — {tag}", fontsize=14)
    ticks = [e['tick'] for e in diagnostics['energy']]
    colors_cycle = ['red', 'green', 'blue']

    # KE per entity
    for i, entity in enumerate(entities):
        vals = [e.get(f"KE_{entity.label}", 0) for e in diagnostics['energy']]
        ax1.plot(ticks, vals, '-', color=colors_cycle[i % len(colors_cycle)],
                 linewidth=0.8, label=f"KE {entity.label}")
    total_ke = [e.get('KE_total', 0) for e in diagnostics['energy']]
    ax1.plot(ticks, total_ke, 'k-', linewidth=1.2, label='KE total')
    ax1.set_xlabel("Tick")
    ax1.set_ylabel("Kinetic Energy")
    ax1.set_title("Kinetic Energy")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Gamma growth
    gamma_total = [e.get('gamma_total', 0) for e in diagnostics['energy']]
    ax2.plot(ticks, gamma_total, 'k-', linewidth=1.0, label='Total gamma')
    for i, entity in enumerate(entities):
        vals = [e.get(f"gamma_{entity.label}", 0) for e in diagnostics['energy']]
        ax2.plot(ticks, vals, '--', color=colors_cycle[i % len(colors_cycle)],
                 linewidth=0.6, label=f"gamma {entity.label}", alpha=0.7)
    ax2.set_xlabel("Tick")
    ax2.set_ylabel("Total Gamma")
    ax2.set_title("Field Gamma Growth")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"energy_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: energy_{tag}.png")


def plot_gamma_growth(diagnostics, tag):
    """Total gamma across all fields vs tick."""
    if not diagnostics['energy']:
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    ticks = [e['tick'] for e in diagnostics['energy']]
    gamma_total = [e.get('gamma_total', 0) for e in diagnostics['energy']]

    ax.plot(ticks, gamma_total, 'k-', linewidth=1.0)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Total Gamma (all fields)")
    ax.set_title(f"Gamma Growth — {tag}")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"gamma_growth_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: gamma_growth_{tag}.png")


def plot_summary(diagnostics, entities, tag):
    """4-panel summary figure."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"Three-Body Graph Dynamics — {tag}", fontsize=14)
    colors_cycle = ['red', 'green', 'blue']

    # Panel 1: Distances
    ax = axes[0, 0]
    if diagnostics['distances']:
        ticks = [d['tick'] for d in diagnostics['distances']]
        pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
        for i, key in enumerate(pair_keys):
            vals = [d.get(key, 0) for d in diagnostics['distances']]
            ax.plot(ticks, vals, '-', color=colors_cycle[i % len(colors_cycle)],
                    linewidth=0.8, label=key)
        ax.legend(fontsize=7)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Hop Distance")
    ax.set_title("Pairwise Distances")
    ax.grid(True, alpha=0.3)

    # Panel 2: Core Speed (snake) or Hops/Tick (classic)
    ax = axes[0, 1]
    has_core_speeds = any(len(v) > 0 for v in diagnostics.get('core_speeds', {}).values())
    if has_core_speeds:
        # Snake mode: rolling average core speed
        window = 50
        for i, entity in enumerate(entities):
            speeds_raw = diagnostics['core_speeds'][entity.label]
            if len(speeds_raw) > window:
                rolling = np.convolve(speeds_raw, np.ones(window)/window, mode='valid')
                ticks_arr = np.arange(window, len(speeds_raw) + 1)
                ax.plot(ticks_arr, rolling, '-', color=colors_cycle[i % len(colors_cycle)],
                        linewidth=0.8, label=f"{entity.label} (mean={np.mean(speeds_raw):.3f})",
                        alpha=0.8)
        ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=0.5, alpha=0.5, label='c=1')
        ax.legend(fontsize=7)
        ax.set_xlabel("Tick")
        ax.set_ylabel("Core Speed (rolling avg)")
        ax.set_title("Core Speed (< c during turns)")
    elif diagnostics['speeds']:
        ticks = [s['tick'] for s in diagnostics['speeds']]
        for i, entity in enumerate(entities):
            vals = [s.get(entity.label, 0) for s in diagnostics['speeds']]
            ax.plot(ticks, vals, '-', color=colors_cycle[i % len(colors_cycle)],
                    linewidth=0.8, label=entity.label, alpha=0.8)
        ax.legend(fontsize=7)
        ax.set_xlabel("Tick")
        ax.set_ylabel("Hops / Tick")
        ax.set_title("Entity Speeds")
    ax.grid(True, alpha=0.3)

    # Panel 3: Amplitude Energy (replaces KE — meaningless in always-move)
    ax = axes[1, 0]
    if diagnostics['distances'] and len(diagnostics['distances']) >= 25:
        pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
        for i, key in enumerate(pair_keys):
            center_ticks, amplitudes, _ = compute_amplitude_envelope(
                diagnostics['distances'], key, window_size=20)
            if len(center_ticks) > 0:
                ax.plot(center_ticks, amplitudes, '-',
                        color=colors_cycle[i % len(colors_cycle)],
                        linewidth=0.8, label=f"amp {key}", alpha=0.8)
        ax.legend(fontsize=7)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Amplitude (= Energy)")
    ax.set_title("Oscillation Amplitude Energy")
    ax.grid(True, alpha=0.3)

    # Panel 4: Gamma growth
    ax = axes[1, 1]
    if diagnostics['energy']:
        ticks = [e['tick'] for e in diagnostics['energy']]
        gamma_total = [e.get('gamma_total', 0) for e in diagnostics['energy']]
        ax.plot(ticks, gamma_total, 'k-', linewidth=1.0)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Total Gamma")
    ax.set_title("Field Gamma Growth")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"summary_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: summary_{tag}.png")


def plot_amplitude_energy(diagnostics, tag, window_size=20):
    """3-panel amplitude energy figure.

    Top: Raw distance time series with shaded amplitude envelope (max/min bands).
    Middle: Amplitude (= energy) per pair vs time.
    Bottom: Total orbital energy (sum of amplitudes). Flat = conserved.
    """
    if not diagnostics['distances'] or len(diagnostics['distances']) < window_size + 5:
        return

    pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
    colors_cycle = ['red', 'green', 'blue']
    ticks_raw = [d['tick'] for d in diagnostics['distances']]

    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    fig.suptitle(f"Amplitude Energy Analysis — {tag}", fontsize=14)

    # Top: Raw distances with amplitude envelope
    ax = axes[0]
    for i, key in enumerate(pair_keys):
        raw_vals = [d[key] for d in diagnostics['distances']]
        ax.plot(ticks_raw, raw_vals, '-', color=colors_cycle[i % len(colors_cycle)],
                linewidth=0.5, alpha=0.4, label=f"{key} (raw)")
        center_ticks, amplitudes, means = compute_amplitude_envelope(
            diagnostics['distances'], key, window_size)
        if len(center_ticks) > 0:
            upper = means + amplitudes / 2
            lower = means - amplitudes / 2
            ax.fill_between(center_ticks, lower, upper,
                            color=colors_cycle[i % len(colors_cycle)],
                            alpha=0.15)
            ax.plot(center_ticks, means, '-',
                    color=colors_cycle[i % len(colors_cycle)],
                    linewidth=1.0, label=f"{key} (mean)")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Hop Distance")
    ax.set_title("Distance with Amplitude Envelope")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # Middle: Amplitude per pair
    ax = axes[1]
    amp_dict = {}
    for i, key in enumerate(pair_keys):
        center_ticks, amplitudes, _ = compute_amplitude_envelope(
            diagnostics['distances'], key, window_size)
        if len(center_ticks) > 0:
            ax.plot(center_ticks, amplitudes, '-',
                    color=colors_cycle[i % len(colors_cycle)],
                    linewidth=1.0, label=f"amp {key}")
            amp_dict[key] = amplitudes
    ax.set_xlabel("Tick")
    ax.set_ylabel("Amplitude (= Energy)")
    ax.set_title("Oscillation Amplitude per Pair")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # Bottom: Total orbital energy
    ax = axes[2]
    if amp_dict:
        total, cv = compute_total_orbital_energy(amp_dict)
        if len(total) > 0:
            # Use center_ticks from the last pair computed (all should be same length)
            min_len = len(total)
            ax.plot(center_ticks[:min_len], total, 'k-', linewidth=1.0,
                    label=f"Total (CV={cv:.3f})")
            ax.axhline(y=np.mean(total), color='gray', linestyle='--',
                       linewidth=0.5, alpha=0.5)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Total Amplitude Energy")
    ax.set_title("Total Orbital Energy (Flat = Conserved)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"amplitude_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: amplitude_{tag}.png")


def plot_energy_exchange(diagnostics, tag, window_size=20, corr_window=50):
    """2-panel energy exchange figure.

    Top: Amplitude overlay for all 3 pairs.
    Bottom: Rolling cross-correlation for each pair combination.
    Anti-correlation (< -0.3) = energy transferring between pairs.
    """
    if not diagnostics['distances'] or len(diagnostics['distances']) < window_size + corr_window + 5:
        return

    pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
    colors_cycle = ['red', 'green', 'blue']
    exchange_colors = ['purple', 'orange', 'brown']

    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle(f"Energy Exchange Analysis — {tag}", fontsize=14)

    # Top: Amplitude overlay
    ax = axes[0]
    amp_dict = {}
    amp_ticks = None
    for i, key in enumerate(pair_keys):
        center_ticks, amplitudes, _ = compute_amplitude_envelope(
            diagnostics['distances'], key, window_size)
        if len(center_ticks) > 0:
            ax.plot(center_ticks, amplitudes, '-',
                    color=colors_cycle[i % len(colors_cycle)],
                    linewidth=1.0, label=f"amp {key}")
            amp_dict[key] = amplitudes
            amp_ticks = center_ticks
    ax.set_xlabel("Tick")
    ax.set_ylabel("Amplitude (= Energy)")
    ax.set_title("Amplitude Overlay")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # Bottom: Rolling cross-correlation
    ax = axes[1]
    if amp_dict and amp_ticks is not None:
        exchange = compute_energy_exchange(amp_ticks, amp_dict, corr_window)
        for i, (label, data) in enumerate(exchange.items()):
            corrs = data['correlations']
            n_corr = len(corrs)
            # Center ticks for correlation windows
            corr_ticks = amp_ticks[corr_window // 2: corr_window // 2 + n_corr]
            if len(corr_ticks) == n_corr:
                ax.plot(corr_ticks, corrs, '-',
                        color=exchange_colors[i % len(exchange_colors)],
                        linewidth=0.8, label=f"{label} (anti={data['frac_anticorrelated']:.1%})")
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        ax.axhline(y=-0.3, color='red', linestyle='--', linewidth=0.5, alpha=0.5,
                   label="anti-correlation threshold")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Rolling Correlation")
    ax.set_title("Amplitude Cross-Correlation (< -0.3 = energy exchange)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1.1, 1.1)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"exchange_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: exchange_{tag}.png")


def plot_core_speed(diagnostics, entities, tag, window=50):
    """2-panel core speed figure (v5 snake model).

    Top: Rolling average core speed per entity vs time.
    Bottom: Cumulative core displacement vs time. Slope = effective velocity.
    """
    core_speeds = diagnostics.get('core_speeds', {})
    if not any(len(v) > 0 for v in core_speeds.values()):
        return

    colors_cycle = ['red', 'green', 'blue']

    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle(f"Core Speed Analysis (Snake Model) — {tag}", fontsize=14)

    # Top: Rolling average core speed
    ax = axes[0]
    for i, entity in enumerate(entities):
        speeds_raw = core_speeds.get(entity.label, [])
        if len(speeds_raw) > window:
            rolling = np.convolve(speeds_raw, np.ones(window)/window, mode='valid')
            ticks_arr = np.arange(window, len(speeds_raw) + 1)
            mean_v = np.mean(speeds_raw)
            ax.plot(ticks_arr, rolling, '-', color=colors_cycle[i % len(colors_cycle)],
                    linewidth=0.8, label=f"{entity.label} (mean={mean_v:.3f})", alpha=0.8)
    ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=0.5, alpha=0.5, label='c=1')
    ax.set_xlabel("Tick")
    ax.set_ylabel("Core Speed (rolling avg)")
    ax.set_title("Core Speed vs Time (< 1.0 = mass slowing)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.15)

    # Bottom: Cumulative displacement
    ax = axes[1]
    for i, entity in enumerate(entities):
        speeds_raw = core_speeds.get(entity.label, [])
        if len(speeds_raw) > 0:
            cumulative = np.cumsum(speeds_raw)
            ticks_arr = np.arange(1, len(speeds_raw) + 1)
            slope = cumulative[-1] / len(speeds_raw) if len(speeds_raw) > 0 else 0
            ax.plot(ticks_arr, cumulative, '-', color=colors_cycle[i % len(colors_cycle)],
                    linewidth=0.8, label=f"{entity.label} (v_eff={slope:.3f})", alpha=0.8)
    # Reference: displacement at c=1
    if core_speeds:
        max_len = max(len(v) for v in core_speeds.values())
        ax.plot([0, max_len], [0, max_len], 'k--', linewidth=0.5, alpha=0.3, label='c=1 ref')
    ax.set_xlabel("Tick")
    ax.set_ylabel("Cumulative Core Displacement")
    ax.set_title("Core Displacement (slope = effective velocity)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"core_speed_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: core_speed_{tag}.png")


# ===========================================================================
# Verification Tests
# ===========================================================================

def run_verification():
    """Quick verification tests for graph substrate correctness."""
    print("=" * 60)
    print("VERIFICATION TESTS")
    print("=" * 60)
    all_passed = True

    # Test 1: Spreading conservation (with decay=1.0 → should conserve exactly)
    print("\n  Test 1: Spreading conservation (decay=1.0)")
    fg = GammaFieldGraph(n_nodes=1000, k=6, beta=0.3,
                         spread_fraction=0.1, decay=1.0, seed=42)
    fg.add_field("test")
    fg.deposit("test", 500, 1000.0)
    gamma_before = fg.total_gamma("test")
    for _ in range(500):
        fg.spread_all()
    gamma_after = fg.total_gamma("test")
    drift = abs(gamma_after - gamma_before) / gamma_before
    passed = drift < 1e-10
    print(f"    Before: {gamma_before:.6f}, After: {gamma_after:.6f}, "
          f"Drift: {drift:.2e} -> {'PASS' if passed else 'FAIL'}")
    all_passed &= passed

    # Test 2: Gradient direction — deposit at one node, neighbors should
    # have positive gradient toward it
    print("\n  Test 2: Gradient direction (points toward deposit)")
    fg2 = GammaFieldGraph(n_nodes=1000, k=6, beta=0.3,
                          spread_fraction=0.1, decay=0.9999, seed=42)
    fg2.add_field("source")
    fg2.add_field("observer")
    # Deposit heavily at node 100
    for _ in range(200):
        fg2.deposit("source", 100, 10.0)
        fg2.spread_all()
    # Check gradient at a neighbor of node 100
    nbs = fg2.neighbors[100]
    if nbs:
        test_node = nbs[0]
        target, grad_mag = fg2.gradient_at(test_node, "observer")
        # Target should be node 100 (the deposit peak)
        passed = (target == 100) and (grad_mag > 0)
        print(f"    Deposit at node 100, test at neighbor {test_node}")
        print(f"    Gradient target={target} (expect 100), mag={grad_mag:.6f}")
        print(f"    -> {'PASS' if passed else 'FAIL'}")
        all_passed &= passed

    # Test 3: BFS correctness
    print("\n  Test 3: BFS hop distance")
    # Distance from a node to itself = 0
    d_self = fg2.hop_distance(42, 42)
    passed_self = (d_self == 0)
    # Distance from a node to its neighbor = 1
    nb = fg2.neighbors[42][0]
    d_nb = fg2.hop_distance(42, nb)
    passed_nb = (d_nb == 1)
    passed = passed_self and passed_nb
    print(f"    d(42, 42) = {d_self} (expect 0) -> {'PASS' if passed_self else 'FAIL'}")
    print(f"    d(42, {nb}) = {d_nb} (expect 1) -> {'PASS' if passed_nb else 'FAIL'}")
    all_passed &= passed

    # Test 4: Movement — entity with KE=3 takes exactly 3 hops
    print("\n  Test 4: Entity takes floor(KE) hops")
    fg3 = GammaFieldGraph(n_nodes=1000, k=6, beta=0.3,
                          spread_fraction=0.1, decay=0.9999, seed=42)
    fg3.add_field("mover")
    fg3.add_field("attractor")
    # Build a gradient: heavy deposits at node 0
    for _ in range(300):
        fg3.deposit("attractor", 0, 10.0)
        fg3.spread_all()
    # Place entity far from node 0 with KE=3.5
    entity = GraphEntity("mover", start_node=500, deposit_amount=0, drain_deposit=0)
    entity.ke = 3.5
    start_node = entity.node
    entity.move(fg3)
    passed = entity.hops_this_tick == 3 and abs(entity.ke - 0.5) < 1e-10
    print(f"    Start node: {start_node}, KE before=3.5")
    print(f"    Hops taken: {entity.hops_this_tick} (expect 3), "
          f"KE after: {entity.ke:.2f} (expect 0.5)")
    print(f"    -> {'PASS' if passed else 'FAIL'}")
    all_passed &= passed

    # Test 5: No self-attraction — entity at own deposit peak sees gradient=0
    print("\n  Test 5: No self-attraction (external fields only)")
    fg4 = GammaFieldGraph(n_nodes=1000, k=6, beta=0.3,
                          spread_fraction=0.1, decay=0.9999, seed=42)
    fg4.add_field("self")
    fg4.add_field("other")
    # Heavy self-deposits at node 200
    for _ in range(300):
        fg4.deposit("self", 200, 10.0)
        fg4.spread_all()
    # Gradient from external fields at node 200 should be ~0
    _, grad_mag = fg4.gradient_at(200, "self")
    passed = grad_mag < 1e-10
    print(f"    Self-deposited at node 200, external gradient = {grad_mag:.2e}")
    print(f"    -> {'PASS' if passed else 'FAIL'}")
    all_passed &= passed

    # Test 6: Lattice graph construction and lattice-nw shortcuts
    print("\n  Test 6: Lattice graph construction (RAW 110)")
    fg5 = GammaFieldGraph(n_nodes=1000, k=6, beta=0.3,
                          spread_fraction=0.1, decay=1.0, seed=42,
                          graph_type='lattice')
    # side=10 -> 1000 nodes, each with degree 6 (3D periodic cubic)
    degrees = [fg5.graph.degree(i) for i in range(fg5.n_nodes)]
    all_deg_6 = all(d == 6 for d in degrees)
    passed_deg = all_deg_6
    print(f"    Lattice: N={fg5.n_nodes}, side={fg5.graph_info.get('side')}")
    print(f"    All nodes degree 6: {all_deg_6}")

    # Verify spreading conservation on lattice (decay=1.0)
    fg5.add_field("test_lat")
    fg5.deposit("test_lat", 0, 1000.0)
    gamma_before_lat = fg5.total_gamma("test_lat")
    for _ in range(200):
        fg5.spread_all()
    gamma_after_lat = fg5.total_gamma("test_lat")
    drift_lat = abs(gamma_after_lat - gamma_before_lat) / gamma_before_lat
    passed_cons = drift_lat < 1e-10
    print(f"    Spreading conservation: before={gamma_before_lat:.2f}, "
          f"after={gamma_after_lat:.6f}, drift={drift_lat:.2e}")
    print(f"    Conservation: {'PASS' if passed_cons else 'FAIL'}")

    # Verify lattice-nw adds shortcuts
    fg6 = GammaFieldGraph(n_nodes=1000, k=6, beta=0.1,
                          spread_fraction=0.1, decay=1.0, seed=42,
                          graph_type='lattice-nw')
    n_shortcuts = fg6.graph_info.get('n_shortcuts', 0)
    # lattice-nw should have higher average degree than pure lattice
    degrees_nw = [fg6.graph.degree(i) for i in range(fg6.n_nodes)]
    avg_deg_nw = sum(degrees_nw) / len(degrees_nw)
    # All original lattice edges preserved: min degree >= 6
    min_deg_nw = min(degrees_nw)
    passed_nw = n_shortcuts > 0 and min_deg_nw >= 6
    print(f"    Lattice-NW: shortcuts={n_shortcuts}, avg_degree={avg_deg_nw:.2f}, "
          f"min_degree={min_deg_nw}")
    print(f"    Shortcuts added and lattice preserved: {'PASS' if passed_nw else 'FAIL'}")

    passed = passed_deg and passed_cons and passed_nw
    print(f"    -> {'PASS' if passed else 'FAIL'}")
    all_passed &= passed

    # Test 7: Temporal edge traversal
    print("\n  Test 7: Temporal edge traversal")
    # Build larger lattice with weak gradient so we can test accumulation
    fg7 = GammaFieldGraph(n_nodes=1000, k=6, beta=0.0,
                          spread_fraction=1/6, decay=0.9999, seed=42,
                          graph_type='lattice')
    fg7.add_field("src")
    fg7.add_field("mover")
    # Deposit at node 0 to create gradient — use 1/k spread for realistic c
    for _ in range(200):
        fg7.deposit("src", 0, 1.0)
        fg7.spread_all()

    # Place entity 3 hops from node 0 (far enough for weak gradient)
    # Find a node at distance 3
    from collections import deque
    q = deque([(0, 0)])
    visited = {0: 0}
    while q:
        node, dist = q.popleft()
        if dist == 3:
            break
        for nb in fg7.graph.neighbors(node):
            if nb not in visited:
                visited[nb] = dist + 1
                q.append((nb, dist + 1))
    start_node = node

    entity_t = GraphEntity("mover", start_node=start_node,
                           deposit_amount=1.0, drain_deposit=0.5,
                           max_hops_per_tick=20, k_neighbors=6,
                           temporal=True)
    target_nb, grad_mag = entity_t.read_gradient(fg7)
    print(f"    Entity at node {start_node} (3 hops from src), gradient={grad_mag:.6f}")

    # With temporal mode: gradient accumulates. After ceil(1/grad_mag) ticks,
    # transit_progress >= 1.0 (edge weight) → hop.
    ticks_to_hop = int(np.ceil(1.0 / grad_mag)) if grad_mag > 0 else 99999
    print(f"    Expected ticks to first hop: ~{ticks_to_hop}")

    # Before hopping: verify transit_progress accumulates
    entity_t.advance_temporal(fg7)
    progress_after_1 = entity_t.transit_progress
    print(f"    After 1 tick: transit_progress={progress_after_1:.6f}, "
          f"transit_target={entity_t.transit_target}")
    accumulates = entity_t.transit_target is not None and progress_after_1 > 0

    # Run until hop or timeout
    hop_tick = None
    for tick in range(2, ticks_to_hop + 10):
        fg7.spread_all()
        entity_t.advance_temporal(fg7)
        entity_t.deposit_dynamics(fg7)
        if entity_t.node != start_node:
            hop_tick = tick
            break

    moved = entity_t.node != start_node
    print(f"    Entity moved: {moved}, hop at tick {hop_tick}, "
          f"from {start_node} to {entity_t.node}")

    # Verify moved closer to source (d decreased from 3)
    d_after = fg7.hop_distance(entity_t.node, 0)
    moved_closer = d_after < 3
    print(f"    Distance to source: 3 -> {d_after} (moved closer: {moved_closer})")

    # Test temporal with weight > 1: create a lattice-nw with a known shortcut
    fg8 = GammaFieldGraph(n_nodes=1000, k=6, beta=0.5,
                          spread_fraction=0.1, decay=1.0, seed=42,
                          graph_type='lattice-nw')
    # Check that edge_weights dict has entries with weight > 1
    heavy_edges = {k: v for k, v in fg8.edge_weights.items() if v > 1}
    has_heavy = len(heavy_edges) > 0
    print(f"    Lattice-NW heavy edges (weight>1): {len(heavy_edges)}")
    if has_heavy:
        sample_edge = list(heavy_edges.items())[0]
        print(f"    Sample: edge {sample_edge[0]} weight={sample_edge[1]}")

    passed = moved and moved_closer and accumulates and has_heavy
    print(f"    -> {'PASS' if passed else 'FAIL'}")
    all_passed &= passed

    # Test 8: Commit-counter mechanics — mass=M means 1 hop every M ticks
    print("\n  Test 8: Commit-counter mechanics (move every M ticks)")
    fg_snake = GammaFieldGraph(n_nodes=1000, k=6, beta=0.0,
                               spread_fraction=1/6, decay=0.9999, seed=42,
                               graph_type='lattice')
    fg_snake.add_field("snake_test")
    # Deposit at node 0 to create gradient
    for _ in range(200):
        fg_snake.deposit("snake_test", 0, 1.0)
        fg_snake.spread_all()

    # Create mass=3 entity at a node far from source
    start = 500
    snake = SnakeEntity("snake_test", start_node=start, field_graph=fg_snake,
                        deposit_amount=1.0, drain_deposit=0.5, mass=3)
    assert snake.node == start, "Should start at start node"
    assert snake.commit_counter == 0, "Counter should start at 0"

    # Tick 1: counter 0→1, should NOT move
    moved1 = snake.advance_snake()
    at_start_1 = snake.node == start
    # Tick 2: counter 1→2, should NOT move
    moved2 = snake.advance_snake()
    at_start_2 = snake.node == start
    # Tick 3: counter 2→3 >= mass(3), should MOVE and reset counter
    moved3 = snake.advance_snake()
    has_moved = snake.node != start
    counter_reset = snake.commit_counter == 0

    passed_snake = (moved1 == 0 and at_start_1 and
                    moved2 == 0 and at_start_2 and
                    moved3 == 1 and has_moved and counter_reset)
    print(f"    mass=3 entity at node {start}")
    print(f"    Tick 1: moved={moved1}, still at start={at_start_1}")
    print(f"    Tick 2: moved={moved2}, still at start={at_start_2}")
    print(f"    Tick 3: moved={moved3}, left start={has_moved}, counter reset={counter_reset}")
    print(f"    -> {'PASS' if passed_snake else 'FAIL'}")
    all_passed &= passed_snake

    # Test 9: Deposit accumulates while stationary (M deposits per position)
    print("\n  Test 9: Deposit accumulates over M ticks at same position")
    fg_dep = GammaFieldGraph(n_nodes=1000, k=6, beta=0.0,
                             spread_fraction=1/6, decay=1.0, seed=42,
                             graph_type='lattice')
    fg_dep.add_field("dep1")
    fg_dep.add_field("dep5")

    snake1 = SnakeEntity("dep1", start_node=100, field_graph=fg_dep,
                         deposit_amount=1.0, mass=1)
    snake5 = SnakeEntity("dep5", start_node=500, field_graph=fg_dep,
                         deposit_amount=1.0, mass=5)

    # Run 5 ticks of formation deposit for each
    for _ in range(5):
        snake1.deposit_formation(fg_dep)
        snake5.deposit_formation(fg_dep)

    total_dep1 = fg_dep.total_gamma("dep1")
    total_dep5 = fg_dep.total_gamma("dep5")

    # Both deposit 1.0 per tick × 5 ticks = 5.0 total.
    # But mass=1 moves every tick (deposits spread across positions),
    # while mass=5 stays put for 5 ticks (all 5 deposits at same node).
    # In formation mode (no movement), both accumulate 5.0 total.
    # The key difference is spatial concentration: mass=5 puts it all at one node.
    deposit_at_node_1 = fg_dep.fields["dep1"][100]
    deposit_at_node_5 = fg_dep.fields["dep5"][500]

    passed_dep = (abs(total_dep1 - 5.0) < 1e-10 and
                  abs(total_dep5 - 5.0) < 1e-10 and
                  abs(deposit_at_node_5 - 5.0) < 1e-10)
    print(f"    mass=1: total deposit = {total_dep1:.2f}, at node 100 = {deposit_at_node_1:.2f}")
    print(f"    mass=5: total deposit = {total_dep5:.2f}, at node 500 = {deposit_at_node_5:.2f}")
    print(f"    Both deposit same total, but mass=5 concentrated at one node: {abs(deposit_at_node_5 - 5.0) < 1e-10}")
    print(f"    -> {'PASS' if passed_dep else 'FAIL'}")
    all_passed &= passed_dep

    # Test 10: Effective speed = 1/M for mass=M entity
    print("\n  Test 10: Effective speed v = c/M")
    fg_cs = GammaFieldGraph(n_nodes=8000, k=6, beta=0.0,
                            spread_fraction=1/6, decay=0.9999, seed=42,
                            graph_type='lattice')
    fg_cs.add_field("cs_src")
    fg_cs.add_field("cs_entity")
    # Create a gradient from node 0
    for _ in range(300):
        fg_cs.deposit("cs_src", 0, 1.0)
        fg_cs.spread_all()

    # mass=5 entity starting 10 hops from source
    q = deque([(0, 0)])
    vis = {0: 0}
    target_node = 0
    while q:
        nd, dist = q.popleft()
        if dist == 10:
            target_node = nd
            break
        for nb in fg_cs.graph.neighbors(nd):
            if nb not in vis:
                vis[nb] = dist + 1
                q.append((nb, dist + 1))

    snake_heavy = SnakeEntity("cs_entity", start_node=target_node, field_graph=fg_cs,
                              deposit_amount=1.0, drain_deposit=0.5, mass=5)
    hops_test = []
    for _ in range(200):
        fg_cs.spread_all()
        cm = snake_heavy.advance_snake()
        hops_test.append(cm)
        snake_heavy.deposit_dynamics(fg_cs)

    mean_speed = np.mean(hops_test)
    expected_speed = 1.0 / 5.0  # = 0.2
    # Should be very close to 0.2 (moves exactly 1 hop every 5 ticks)
    passed_cs = abs(mean_speed - expected_speed) < 0.02
    total_hops = sum(hops_test)
    expected_hops = 200 // 5  # = 40
    print(f"    mass=5 entity, 200 ticks: mean speed = {mean_speed:.3f} (expect {expected_speed:.3f})")
    print(f"    Total hops = {total_hops} (expect {expected_hops})")
    print(f"    Speed matches c/M: {passed_cs}")
    print(f"    -> {'PASS' if passed_cs else 'FAIL'}")
    all_passed &= passed_cs

    print(f"\n  {'=' * 40}")
    print(f"  Overall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print(f"  {'=' * 40}")
    return all_passed


# ===========================================================================
# Calibration — Two-body infall
# ===========================================================================

def run_calibration(n_nodes=50000, k=6, beta=0.3, spread_fraction=None,
                    decay=0.9999, formation_ticks=2000, dynamics_ticks=10000,
                    seed=42, graph_type='random', temporal=False,
                    lattice_edge_weight=1):
    """Two-body calibration: pin entity A (deposits only), release entity B.

    Measures infall time, peak velocity, whether naturally bounded.
    """
    mode_str = "temporal" if temporal else "classic"
    print("=" * 60)
    print(f"CALIBRATION: Two-body infall on graph ({graph_type}, {mode_str})")
    print("=" * 60)

    fg = GammaFieldGraph(n_nodes=n_nodes, k=k, beta=beta,
                         spread_fraction=spread_fraction, decay=decay,
                         seed=seed, graph_type=graph_type,
                         lattice_edge_weight=lattice_edge_weight)

    # Graph stats
    avg_path, clustering = fg.graph_stats()
    print(f"  Graph stats: avg_path_length ~ {avg_path:.1f}, "
          f"clustering = {clustering:.4f}")

    # Place two entities far apart
    min_sep = max(5, int(avg_path * 0.8))
    nodes = place_entities_apart(fg, n_entities=2, min_separation=min_sep, seed=seed)
    node_a, node_b = nodes[0], nodes[1]
    initial_dist = fg.hop_distance(node_a, node_b)
    print(f"  Initial separation: {initial_dist} hops")

    fg.add_field("A")
    fg.add_field("B")

    # Entity A: deposits only (pinned — manually deposit, don't move)
    # Entity B: follows gradient
    entity_b = GraphEntity("B", start_node=node_b, deposit_amount=1.0,
                           drain_deposit=0.5, color='blue', temporal=temporal)

    # Formation: A deposits, B deposits, fields spread
    print(f"\n  Formation phase ({formation_ticks} ticks):")
    t0 = time.time()
    for tick in range(formation_ticks):
        fg.deposit("A", node_a, 1.0)  # A is pinned, just deposits
        fg.deposit("B", node_b, 1.0)  # B deposits at start position
        fg.spread_all()
        if (tick + 1) % 500 == 0:
            elapsed = time.time() - t0
            rate = (tick + 1) / elapsed if elapsed > 0 else 0
            print(f"    Formation tick {tick + 1:5d}/{formation_ticks} "
                  f"({elapsed:6.1f}s, {rate:.0f} t/s) "
                  f"gamma_total={fg.total_gamma_all():.2f}")

    elapsed = time.time() - t0
    print(f"  Formation done in {elapsed:.1f}s")

    # Check gradient at B's position
    _, grad_at_b = fg.gradient_at(node_b, "B")
    print(f"  Gradient at B's starting node: {grad_at_b:.6f}")

    # Dynamics: A keeps depositing (pinned), B follows gradient
    print(f"\n  Dynamics phase ({dynamics_ticks} ticks):")
    t0 = time.time()

    distances = []
    speeds = []
    ke_history = []
    max_speed = 0
    infall_tick = None

    for tick in range(dynamics_ticks):
        # Spread
        fg.spread_all()

        # A deposits (pinned)
        fg.deposit("A", node_a, 1.0)

        # B: advance toward A
        if temporal:
            entity_b.advance_temporal(fg)
        else:
            _, grad_mag = entity_b.read_gradient(fg)
            entity_b.accumulate(grad_mag * 0.5)
            entity_b.move(fg)
            _, grad_mag2 = entity_b.read_gradient(fg)
            entity_b.accumulate(grad_mag2 * 0.5)
        entity_b.deposit_dynamics(fg)

        if entity_b.hops_this_tick > max_speed:
            max_speed = entity_b.hops_this_tick

        # Distance check every 50 ticks
        if (tick + 1) % 50 == 0:
            d = fg.hop_distance(entity_b.node, node_a)
            distances.append({'tick': tick + 1, 'distance': d})
            speeds.append({'tick': tick + 1, 'hops': entity_b.hops_this_tick})
            ke_history.append({'tick': tick + 1, 'ke': entity_b.ke})

            if d <= 1 and infall_tick is None:
                infall_tick = tick + 1
                print(f"    *** INFALL at tick {infall_tick}, d={d}")

        if (tick + 1) % 1000 == 0:
            elapsed = time.time() - t0
            rate = (tick + 1) / elapsed if elapsed > 0 else 0
            d = fg.hop_distance(entity_b.node, node_a)
            print(f"    Tick {tick + 1:6d}/{dynamics_ticks} "
                  f"({elapsed:6.1f}s, {rate:.0f} t/s) "
                  f"d={d}, hops={entity_b.hops_this_tick}, ke={entity_b.ke:.2f}")

    elapsed = time.time() - t0
    print(f"  Dynamics done in {elapsed:.1f}s")
    print(f"\n  Calibration results:")
    print(f"    Max velocity:    {max_speed} hops/tick")
    print(f"    Infall tick:     {infall_tick}")
    print(f"    Initial dist:    {initial_dist} hops")

    # Plot calibration
    if distances:
        cal_parts = ["calibration_infall"]
        if graph_type != 'random':
            cal_parts.append(graph_type)
        if temporal:
            cal_parts.append("temporal")
        cal_tag = "_".join(cal_parts)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f"Calibration: Two-Body Infall ({graph_type}, {mode_str})", fontsize=14)

        ticks_d = [d['tick'] for d in distances]
        dists = [d['distance'] for d in distances]
        ax1.plot(ticks_d, dists, 'b-', linewidth=0.8)
        ax1.set_xlabel("Tick")
        ax1.set_ylabel("Hop Distance to A")
        ax1.set_title("Infall Distance")
        ax1.grid(True, alpha=0.3)

        ticks_s = [s['tick'] for s in speeds]
        hops = [s['hops'] for s in speeds]
        ax2.plot(ticks_s, hops, 'r-', linewidth=0.8)
        ax2.set_xlabel("Tick")
        ax2.set_ylabel("Hops / Tick")
        ax2.set_title("Speed vs Time")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        fig.savefig(RESULTS_DIR / f"{cal_tag}.png", dpi=150)
        plt.close(fig)
        print(f"  Saved: {cal_tag}.png")

    return {
        'initial_dist': initial_dist,
        'max_speed': max_speed,
        'infall_tick': infall_tick,
        'distances': distances,
        'speeds': speeds,
        'ke_history': ke_history,
    }


# ===========================================================================
# Three-Body Run
# ===========================================================================

def run_three_body(n_nodes=50000, k=6, beta=0.3, spread_fraction=None,
                   decay=0.9999, formation_ticks=2000, dynamics_ticks=20000,
                   deposit_amount=1.0, drain_deposit=0.5,
                   max_hops_per_tick=20,
                   min_separation=10, seed=42,
                   log_interval=100, distance_interval=50,
                   graph_type='random', temporal=False,
                   lattice_edge_weight=1,
                   equilateral=False, initial_ke=0, mass=1,
                   exclusion=False, always_move=False,
                   custom_tag=None):
    """Full three-body experiment on graph."""
    print("=" * 60)
    print(f"THREE-BODY DYNAMICS ON GRAPH ({graph_type})")
    print("=" * 60)
    print(f"  N={n_nodes}, k={k}, beta={beta}, decay={decay}")
    print(f"  graph_type={graph_type}, temporal={temporal}, "
          f"edge_weight={lattice_edge_weight}")
    if equilateral:
        print(f"  equilateral=True, initial_ke={initial_ke}")
    entity_type = "SnakeEntity" if always_move else "GraphEntity"
    print(f"  mass={mass} ({entity_type}: {'chain length' if always_move else 'path commitment'} "
          f"= {mass}), exclusion={exclusion}, always_move={always_move}")
    print(f"  formation={formation_ticks}, dynamics={dynamics_ticks}")
    print(f"  deposit={deposit_amount}, drain={drain_deposit}, max_hops={max_hops_per_tick}")

    fg = GammaFieldGraph(n_nodes=n_nodes, k=k, beta=beta,
                         spread_fraction=spread_fraction, decay=decay,
                         seed=seed, graph_type=graph_type,
                         lattice_edge_weight=lattice_edge_weight)

    # Graph stats
    avg_path, clustering = fg.graph_stats()
    print(f"  Graph stats: avg_path ~ {avg_path:.1f}, clustering = {clustering:.4f}")

    # Place three entities
    tangential = [None, None, None]
    if equilateral and graph_type in ('lattice', 'lattice-nw'):
        nodes, tangential = place_equilateral(fg, min_separation, seed=seed)
    else:
        # Random placement with target separation
        min_sep = max(3, min(min_separation, int(avg_path * 0.4)))
        max_sep = max(min_sep + 2, int(avg_path * 0.8))
        print(f"  Target separation: {min_sep}-{max_sep} hops")
        nodes = place_entities_apart(fg, n_entities=3, min_separation=min_sep,
                                     max_separation=max_sep, seed=seed)

    # Create fields and entities
    labels = ["A", "B", "C"]
    colors = ["red", "green", "blue"]
    entities = []
    for i, (label, color) in enumerate(zip(labels, colors)):
        fg.add_field(label)
        if always_move:
            # v5: Snake entity — mass = chain length
            entity = SnakeEntity(label, start_node=nodes[i],
                                 field_graph=fg,
                                 deposit_amount=deposit_amount,
                                 drain_deposit=drain_deposit,
                                 k_neighbors=k, color=color,
                                 mass=mass)
            print(f"    {label}: SnakeEntity mass={mass} at node {nodes[i]}")
        else:
            entity = GraphEntity(label, start_node=nodes[i],
                                 deposit_amount=deposit_amount,
                                 drain_deposit=drain_deposit,
                                 max_hops_per_tick=max_hops_per_tick,
                                 k_neighbors=k, color=color,
                                 temporal=temporal, mass=mass)
            # Set initial tangential velocity if equilateral + temporal
            if temporal and tangential[i] is not None and initial_ke > 0:
                # Build initial tangential path of mass edges in tangent direction
                if hasattr(fg, 'node_coords') and mass > 1:
                    side = fg.side
                    cur_c = fg.node_coords[nodes[i]]
                    tan_c = fg.node_coords[tangential[i]]
                    direction = tuple(
                        (b - a + side) % side if (b - a + side) % side <= side // 2
                        else (b - a + side) % side - side
                        for a, b in zip(cur_c, tan_c)
                    )
                    path = [tangential[i]]
                    current = tangential[i]
                    for _ in range(mass - 1):
                        cc = fg.node_coords[current]
                        nc = tuple((c + d) % side for c, d in zip(cc, direction))
                        if nc in fg.coord_to_node:
                            nxt = fg.coord_to_node[nc]
                            path.append(nxt)
                            current = nxt
                    entity.committed_path = path
                else:
                    entity.committed_path = [tangential[i]]
                entity.transit_target = entity.committed_path[0]
                entity.transit_weight = fg.edge_weight(nodes[i], entity.committed_path[0])
                entity.transit_progress = float(initial_ke)
                print(f"    {label}: initial KE={initial_ke} toward tangent node "
                      f"{tangential[i]} (weight={entity.transit_weight})")
        entities.append(entity)

    # Formation
    print()
    run_formation(fg, entities, formation_ticks, log_interval=max(100, formation_ticks // 10))

    # Check gradients after formation
    print(f"\n  Gradients at entity positions after formation:")
    for entity in entities:
        target, grad_mag = entity.read_gradient(fg)
        print(f"    {entity.label} at node {entity.node}: "
              f"grad_mag={grad_mag:.6f}, target={target}")

    # Initial distances
    print(f"\n  Initial distances:")
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            d = fg.hop_distance(entities[i].node, entities[j].node)
            print(f"    {entities[i].label}-{entities[j].label}: {d} hops")

    # Dynamics
    print()
    diagnostics = run_dynamics(fg, entities, dynamics_ticks,
                               log_interval=log_interval,
                               distance_interval=distance_interval,
                               temporal=temporal,
                               exclusion=exclusion,
                               always_move=always_move)

    # Analysis
    print(f"\n  Events: {len(diagnostics['events'])}")
    for event in diagnostics['events'][:20]:
        print(f"    {event['msg']}")

    # Peak speeds
    for entity in entities:
        if entity.trajectory:
            max_hops = max(t['hops'] for t in entity.trajectory)
            max_ke = max(t['ke'] for t in entity.trajectory)
            print(f"  {entity.label}: peak_hops={max_hops}, peak_ke={max_ke:.2f}")

    # Analysis
    analysis = analyze_results(diagnostics, entities, fg)

    # Plots
    tag = "three_body"
    if graph_type != 'random':
        tag += f"_{graph_type}"
    if temporal:
        tag += "_temporal"
    if equilateral:
        tag += "_equilateral"
    if exclusion:
        tag += "_exclusion"
    if always_move:
        tag += "_alwaysmove"
    if custom_tag:
        tag += f"_{custom_tag}"
    plot_distances(diagnostics, tag)
    plot_speeds(diagnostics, entities, tag)
    plot_energy(diagnostics, entities, tag)
    plot_gamma_growth(diagnostics, tag)
    plot_summary(diagnostics, entities, tag)
    plot_amplitude_energy(diagnostics, tag)
    plot_energy_exchange(diagnostics, tag)
    plot_core_speed(diagnostics, entities, tag)

    # Save results (include analysis)
    save_results(diagnostics, entities, fg, tag, analysis=analysis)

    return entities, diagnostics, analysis


# ===========================================================================
# Analysis — Evaluate against success criteria
# ===========================================================================

def analyze_results(diagnostics, entities, field_graph):
    """Evaluate dynamics against experiment success criteria.

    Returns dict with verdict and supporting metrics.
    """
    print("\n" + "=" * 60)
    print("ANALYSIS: Evaluating Success Criteria")
    print("=" * 60)

    result = {}

    # --- Criterion 1: Attraction (distances decrease from initial) ---
    if diagnostics['distances'] and len(diagnostics['distances']) >= 2:
        pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
        initial_dists = {k: diagnostics['distances'][0][k] for k in pair_keys}
        final_dists = {k: diagnostics['distances'][-1][k] for k in pair_keys}
        min_dists = {k: min(d[k] for d in diagnostics['distances']) for k in pair_keys}

        all_attracted = all(final_dists[k] < initial_dists[k] for k in pair_keys)
        any_collapsed = any(min_dists[k] == 0 for k in pair_keys)

        print(f"\n  1. ATTRACTION:")
        for k in pair_keys:
            print(f"     {k}: {initial_dists[k]} -> {final_dists[k]} "
                  f"(min={min_dists[k]})")
        print(f"     All pairs attracted: {all_attracted}")
        print(f"     Any pair collapsed (d=0): {any_collapsed}")

        result['attraction'] = all_attracted
        result['collapsed'] = any_collapsed
        result['initial_distances'] = initial_dists
        result['final_distances'] = final_dists
        result['min_distances'] = min_dists
    else:
        print("\n  1. ATTRACTION: No distance data")
        result['attraction'] = None

    # --- Criterion 2: Bound system (no escape to graph diameter) ---
    if diagnostics['distances']:
        pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
        max_dists = {k: max(d[k] for d in diagnostics['distances']) for k in pair_keys}
        graph_diam_est = field_graph.n_nodes  # loose upper bound

        bound = all(max_dists[k] < graph_diam_est * 0.5 for k in pair_keys)
        print(f"\n  2. BOUND SYSTEM:")
        for k in pair_keys:
            print(f"     {k}: max_distance = {max_dists[k]}")
        print(f"     System bound (no escape): {bound}")
        result['bound'] = bound

    # --- Criterion 3: Close encounters ---
    n_encounters = len([e for e in diagnostics['events']
                        if e.get('type') == 'close_encounter'])
    print(f"\n  3. CLOSE ENCOUNTERS: {n_encounters}")
    result['close_encounters'] = n_encounters

    # --- Criterion 4: Amplitude energy analysis ---
    # In always-move, KE is always 1.0 (meaningless). The REAL energy is the
    # amplitude of the distance oscillation. Anti-correlated amplitudes = exchange.
    if diagnostics['distances'] and len(diagnostics['distances']) >= 25:
        pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
        amp_stats = {}
        amp_dict = {}
        for key in pair_keys:
            center_ticks, amplitudes, means = compute_amplitude_envelope(
                diagnostics['distances'], key, window_size=20)
            if len(amplitudes) > 0:
                amp_stats[key] = {
                    'mean_amplitude': float(np.mean(amplitudes)),
                    'max_amplitude': float(np.max(amplitudes)),
                    'std_amplitude': float(np.std(amplitudes)),
                    'mean_distance': float(np.mean(means)),
                }
                amp_dict[key] = amplitudes

        print(f"\n  4. AMPLITUDE ENERGY (oscillation = energy):")
        for key, stats in amp_stats.items():
            print(f"     {key}: mean_amp={stats['mean_amplitude']:.2f}, "
                  f"max_amp={stats['max_amplitude']:.2f}, "
                  f"mean_dist={stats['mean_distance']:.1f}")

        # Cross-correlation: anti-correlation = energy exchange
        exchange = compute_energy_exchange(None, amp_dict, corr_window=50)
        print(f"     Cross-correlations:")
        any_exchange = False
        for label, data in exchange.items():
            frac = data['frac_anticorrelated']
            mean_corr = data['mean_correlation']
            print(f"       {label}: mean_corr={mean_corr:.3f}, "
                  f"frac_anticorrelated={frac:.1%}")
            if frac > 0.1:
                any_exchange = True

        # Total energy conservation
        total_energy, total_cv = compute_total_orbital_energy(amp_dict)
        print(f"     Total energy CV: {total_cv:.3f} "
              f"({'conserved' if total_cv < 0.3 else 'not conserved'})")

        result['amplitude_stats'] = amp_stats
        result['exchange_correlations'] = {
            label: {'frac_anticorrelated': d['frac_anticorrelated'],
                    'mean_correlation': d['mean_correlation']}
            for label, d in exchange.items()
        }
        result['total_energy_cv'] = total_cv
        result['energy_conserved'] = total_cv < 0.3
        result['energy_exchange'] = any_exchange
    else:
        print(f"\n  4. AMPLITUDE ENERGY: Insufficient distance data")
        result['energy_exchange'] = False

    # --- Criterion 5: Peak velocities ---
    peak_speeds = {}
    for entity in entities:
        if entity.trajectory:
            peak = max(t['hops'] for t in entity.trajectory)
            peak_speeds[entity.label] = peak

    print(f"\n  5. PEAK VELOCITIES:")
    for label, peak in peak_speeds.items():
        print(f"     {label}: {peak} hops/tick")
    max_peak = max(peak_speeds.values()) if peak_speeds else 0
    velocity_bounded = max_peak <= entities[0].max_hops_per_tick if entities else True
    print(f"     Velocity bounded (no runaway): {velocity_bounded}")
    result['peak_speeds'] = peak_speeds
    result['velocity_bounded'] = velocity_bounded

    # --- Criterion 6: Gamma stability (no overflow/NaN) ---
    if diagnostics['energy']:
        gamma_values = [e.get('gamma_total', 0) for e in diagnostics['energy']]
        gamma_ok = all(np.isfinite(g) for g in gamma_values)
        gamma_growth = gamma_values[-1] / gamma_values[0] if gamma_values[0] > 0 else float('inf')
        print(f"\n  6. GAMMA STABILITY:")
        print(f"     No NaN/Inf: {gamma_ok}")
        print(f"     Growth ratio: {gamma_growth:.2f}x")
        result['gamma_ok'] = gamma_ok
        result['gamma_growth_ratio'] = gamma_growth

    # --- Criterion 7: Distance oscillation (orbits?) + amplitude ---
    if diagnostics['distances'] and len(diagnostics['distances']) >= 10:
        pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
        oscillation = {}
        for k in pair_keys:
            values = [d[k] for d in diagnostics['distances']]
            # Count direction changes (approach/retreat transitions)
            reversals = 0
            for i in range(2, len(values)):
                if (values[i] - values[i-1]) * (values[i-1] - values[i-2]) < 0:
                    reversals += 1
            oscillation[k] = reversals

        print(f"\n  7. DISTANCE OSCILLATION (orbit signature):")
        for k, rev in oscillation.items():
            amp_info = ""
            if result.get('amplitude_stats') and k in result['amplitude_stats']:
                amp_info = f", mean_amp={result['amplitude_stats'][k]['mean_amplitude']:.2f}"
            print(f"     {k}: {rev} reversals in {len(diagnostics['distances'])} samples{amp_info}")

        any_oscillation = any(rev > 5 for rev in oscillation.values())
        print(f"     Orbital behavior detected: {any_oscillation}")
        result['oscillation'] = oscillation
        result['orbital_behavior'] = any_oscillation

    # --- Criterion 8: Core speed analysis (v5 snake model) ---
    core_speeds = diagnostics.get('core_speeds', {})
    has_core_data = any(len(v) > 0 for v in core_speeds.values())
    if has_core_data:
        print(f"\n  8. CORE SPEED (snake model):")
        core_speed_stats = {}
        for label, speeds in core_speeds.items():
            if len(speeds) > 0:
                mean_v = float(np.mean(speeds))
                std_v = float(np.std(speeds))
                frac_stationary = float(np.mean(np.array(speeds) == 0))
                core_speed_stats[label] = {
                    'mean_speed': mean_v,
                    'std_speed': std_v,
                    'frac_stationary': frac_stationary,
                }
                print(f"     {label}: mean_core_v={mean_v:.4f}, std={std_v:.4f}, "
                      f"stationary={frac_stationary:.1%}")
        result['core_speed_stats'] = core_speed_stats

        # Check if all core speeds are < 1.0 (the key v5 prediction)
        all_sub_c = all(s['mean_speed'] < 1.0 for s in core_speed_stats.values())
        print(f"     All cores sub-light: {all_sub_c}")
        result['all_cores_sub_c'] = all_sub_c

    # --- VERDICT ---
    print(f"\n  {'=' * 50}")

    bound = result.get('bound', False)
    encounters = result.get('close_encounters', 0)
    orbital = result.get('orbital_behavior', False)
    velocity_ok = result.get('velocity_bounded', False)
    gamma_ok = result.get('gamma_ok', False)
    collapsed = result.get('collapsed', False)

    # Check if ANY pair attracted (not just all)
    any_attracted = False
    all_attracted = result.get('attraction', False)
    if result.get('initial_distances') and result.get('min_distances'):
        any_attracted = any(
            result['min_distances'][k] < result['initial_distances'][k]
            for k in result['initial_distances']
        )

    if collapsed and encounters > 0:
        if orbital:
            verdict = ("PARTIAL PASS — Gravity emerges, some oscillation detected, "
                       "but entities eventually collapse (no stable orbits)")
        else:
            verdict = ("PARTIAL PASS — Gravity emerges (entities attract and merge) "
                       "but no orbits form. Dimensionality required for angular momentum.")
    elif any_attracted and bound and encounters > 0:
        verdict = "PASS — Gravity emerges (attraction + binding + encounters)"
    elif any_attracted:
        verdict = "WEAK PASS — Attraction observed for some pairs"
    elif all_attracted:
        verdict = "PASS — All pairs attracted"
    else:
        verdict = "INCONCLUSIVE — Try longer dynamics or stronger formation"

    if velocity_ok and gamma_ok:
        verdict += " | Drain problem SOLVED (no runaway, no overflow)"

    energy_exchange_detected = result.get('energy_exchange', False)
    energy_conserved = result.get('energy_conserved', False)
    if energy_exchange_detected:
        verdict += " | ENERGY EXCHANGE detected (anti-correlated amplitudes)"
    if energy_conserved:
        verdict += " | Total orbital energy approximately CONSERVED"

    if result.get('all_cores_sub_c'):
        verdict += " | CORE SPEED < c (snake mass slowing confirmed)"

    print(f"  VERDICT: {verdict}")
    print(f"  {'=' * 50}")
    result['verdict'] = verdict

    return result


# ===========================================================================
# JSON Export
# ===========================================================================

def save_results(diagnostics, entities, field_graph, tag, analysis=None):
    """Save results to JSON."""
    def make_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, dict):
            return {str(k): make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        return obj

    results = {
        'graph': {
            'n_nodes': field_graph.n_nodes,
            'k': field_graph.k,
            'beta': field_graph.beta,
            'spread_fraction': field_graph.spread_fraction,
            'decay': field_graph.decay,
            'type': field_graph.graph_type,
            'graph_info': field_graph.graph_info,
        },
        'energy': diagnostics['energy'],
        'distances': diagnostics['distances'],
        'speeds': diagnostics['speeds'],
        'events': diagnostics['events'],
        'trajectories': {e.label: e.trajectory for e in entities},
    }

    # Add amplitude envelope data (downsampled to keep file size reasonable)
    if diagnostics['distances'] and len(diagnostics['distances']) >= 25:
        pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
        amplitude_data = {}
        for key in pair_keys:
            center_ticks, amplitudes, means = compute_amplitude_envelope(
                diagnostics['distances'], key, window_size=20)
            if len(center_ticks) > 0:
                # Downsample if more than 1000 points
                step = max(1, len(center_ticks) // 1000)
                amplitude_data[key] = {
                    'ticks': center_ticks[::step].tolist(),
                    'amplitudes': amplitudes[::step].tolist(),
                    'means': means[::step].tolist(),
                }
        results['amplitude_envelopes'] = amplitude_data

        # Add exchange correlation summary
        amp_dict = {key: amplitudes for key in pair_keys
                    for center_ticks, amplitudes, _ in [compute_amplitude_envelope(
                        diagnostics['distances'], key, window_size=20)]
                    if len(amplitudes) > 0}
        # Rebuild amp_dict properly
        amp_dict = {}
        for key in pair_keys:
            _, amplitudes, _ = compute_amplitude_envelope(
                diagnostics['distances'], key, window_size=20)
            if len(amplitudes) > 0:
                amp_dict[key] = amplitudes
        exchange = compute_energy_exchange(None, amp_dict, corr_window=50)
        results['exchange_summary'] = {
            label: {'frac_anticorrelated': d['frac_anticorrelated'],
                    'mean_correlation': d['mean_correlation']}
            for label, d in exchange.items()
        }

    # Add core speed data (v5 snake model)
    core_speeds = diagnostics.get('core_speeds', {})
    if any(len(v) > 0 for v in core_speeds.values()):
        core_speed_summary = {}
        for label, speeds in core_speeds.items():
            if len(speeds) > 0:
                core_speed_summary[label] = {
                    'mean_speed': float(np.mean(speeds)),
                    'std_speed': float(np.std(speeds)),
                    'frac_stationary': float(np.mean(np.array(speeds) == 0)),
                    'n_ticks': len(speeds),
                }
        results['core_speed_summary'] = core_speed_summary

    if analysis:
        results['analysis'] = analysis

    clean = make_serializable(results)
    path = RESULTS_DIR / f"results_{tag}.json"
    with open(path, 'w') as f:
        json.dump(clean, f, indent=2, default=str)
    print(f"  Results saved to: {path}")


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Experiment #64_109 — Three-Body Dynamics on a Pure Graph"
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="Run verification tests only",
    )
    parser.add_argument(
        "--calibrate", action="store_true",
        help="Run two-body infall calibration",
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Quick mode: N=50K, formation=5K, dynamics=20K ticks",
    )
    parser.add_argument(
        "--n-nodes", type=int, default=None,
        help="Number of graph nodes (default: 50000)",
    )
    parser.add_argument(
        "--k", type=int, default=6,
        help="Neighbors per node (default: 6)",
    )
    parser.add_argument(
        "--beta", type=float, default=0.05,
        help="Watts-Strogatz rewiring probability (default: 0.05)",
    )
    parser.add_argument(
        "--graph-type", type=str, default='random',
        choices=['random', 'lattice', 'lattice-nw'],
        help="Graph topology: 'random' = Watts-Strogatz (D(n)~0-1), "
             "'lattice' = 3D periodic cubic (D(n)=3, tests RAW 110), "
             "'lattice-nw' = lattice + Newman-Watts shortcuts (D(n)=3 + small-world)",
    )
    parser.add_argument(
        "--temporal", action="store_true",
        help="Temporal edge traversal: gradient accumulates as transit progress. "
             "Edge weight = temporal cost (ticks to traverse). Creates inertia.",
    )
    parser.add_argument(
        "--edge-weight", type=int, default=1,
        help="Temporal weight of each lattice edge (default: 1 = movement at c, "
             "10-50 = sub-light). Entity takes this many ticks of gradient accumulation "
             "to cross one hop. Shortcuts cost Manhattan distance * edge-weight.",
    )
    parser.add_argument(
        "--mass", type=int, default=1,
        help="Commit counter (ticks between hops). "
             "Mass = ticks to commit state: v = c/M. "
             "mass=1 = hop every tick (v=c). "
             "mass=5 = hop every 5 ticks (v=c/5).",
    )
    parser.add_argument(
        "--exclusion", action="store_true",
        help="Prevent entities from occupying the same node. "
             "On would-be collision: path cancelled, KE retained, entity replans. "
             "Prevents the d=0 singularity where mutual gradient drops to zero.",
    )
    parser.add_argument(
        "--always-move", action="store_true",
        help="Always-move stochastic model: every tick, every entity hops. "
             "Direction sampled from softmax(gamma[neighbors]). Zero gradient = "
             "random walk, strong gradient = directed movement. "
             "Movement is existence. Gradient is preference, not permission.",
    )
    parser.add_argument(
        "--equilateral", action="store_true",
        help="Place entities in equilateral triangle (requires lattice graph). "
             "All pairs at equal hop distance. Combined with --initial-ke, gives "
             "each entity tangential velocity for orbital dynamics.",
    )
    parser.add_argument(
        "--initial-ke", type=float, default=0,
        help="Initial kinetic energy (transit progress) along tangential edge. "
             "Only used with --equilateral --temporal. Good value: edge_weight/2.",
    )
    parser.add_argument(
        "--spread-fraction", type=float, default=None,
        help="Spread fraction alpha (default: 1/k = speed of light). "
             "Overriding this changes c. Use 1/k for physically correct propagation.",
    )
    parser.add_argument(
        "--decay", type=float, default=0.9999,
        help="Decay factor per tick (default: 0.9999)",
    )
    parser.add_argument(
        "--formation-ticks", type=int, default=None,
        help="Override formation ticks (default: 2000)",
    )
    parser.add_argument(
        "--dynamics-ticks", type=int, default=None,
        help="Override dynamics ticks (default: 20000)",
    )
    parser.add_argument(
        "--deposit", type=float, default=1.0,
        help="Deposit amount per tick (default: 1.0)",
    )
    parser.add_argument(
        "--drain-deposit", type=float, default=0.5,
        help="Gamma deposited at each hop (default: 0.5)",
    )
    parser.add_argument(
        "--max-hops", type=int, default=20,
        help="Maximum hops per tick (speed of light analog, default: 20)",
    )
    parser.add_argument(
        "--min-separation", type=int, default=10,
        help="Minimum initial hop separation (default: 10)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--log-interval", type=int, default=100,
        help="Log diagnostics every N ticks (default: 100)",
    )
    parser.add_argument(
        "--distance-interval", type=int, default=50,
        help="Compute BFS distances every N ticks (default: 50)",
    )
    parser.add_argument(
        "--tag", type=str, default=None,
        help="Custom tag suffix for output files (e.g. 'mass5')",
    )
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.verify:
        run_verification()
        return

    # Quick mode defaults (use 'is not None' to allow 0 as valid)
    # With alpha=1/k, gradients are weaker (1/k² per neighbor vs alpha/k with
    # alpha=0.1), so entities accumulate KE more slowly — physically correct
    # (sub-light orbital velocities) but needs more ticks to see dynamics.
    if args.quick:
        n_nodes = args.n_nodes if args.n_nodes is not None else 50000
        formation = args.formation_ticks if args.formation_ticks is not None else 5000
        dynamics = args.dynamics_ticks if args.dynamics_ticks is not None else 20000
    else:
        n_nodes = args.n_nodes if args.n_nodes is not None else 100000
        formation = args.formation_ticks if args.formation_ticks is not None else 10000
        dynamics = args.dynamics_ticks if args.dynamics_ticks is not None else 50000

    if args.calibrate:
        run_calibration(
            n_nodes=n_nodes, k=args.k, beta=args.beta,
            spread_fraction=args.spread_fraction, decay=args.decay,
            formation_ticks=formation, dynamics_ticks=dynamics,
            seed=args.seed, graph_type=args.graph_type,
            temporal=args.temporal,
            lattice_edge_weight=args.edge_weight,
        )
        return

    # Default: three-body run
    run_three_body(
        n_nodes=n_nodes, k=args.k, beta=args.beta,
        spread_fraction=args.spread_fraction, decay=args.decay,
        formation_ticks=formation, dynamics_ticks=dynamics,
        deposit_amount=args.deposit, drain_deposit=args.drain_deposit,
        max_hops_per_tick=args.max_hops,
        min_separation=args.min_separation, seed=args.seed,
        log_interval=args.log_interval, distance_interval=args.distance_interval,
        graph_type=args.graph_type,
        temporal=args.temporal,
        lattice_edge_weight=args.edge_weight,
        equilateral=args.equilateral,
        initial_ke=args.initial_ke,
        mass=args.mass,
        exclusion=args.exclusion,
        always_move=args.always_move,
        custom_tag=args.tag,
    )

    print("\n" + "=" * 60)
    print("EXPERIMENT #64_109 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
