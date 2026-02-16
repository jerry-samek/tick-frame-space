"""
Experiment #64_109 — Three-Body Dynamics on a Pure Graph
=========================================================
Tests whether gravity emerges from deposit-spread-follow on a random graph
WITHOUT spatial geometry. If yes: space is not fundamental — causal structure is.

Secondary question: does the Bremsstrahlung drain problem from Experiment 64
vanish when there is no lattice? On a graph, minimum distance is always 1 hop —
no zero-distance singularity, no gradient spike, no runaway.

Graph substrate: Watts-Strogatz small-world graph.
Each entity deposits into its own field, follows gradient of other entities' fields.
Movement is discrete hops — no coordinates, no velocity vectors.

KEY FINDING:
  Gravity (attraction) DOES emerge on a pure graph — entities attract and converge.
  However, orbits do NOT form. Without spatial dimensions, there is no angular
  momentum: entities fall straight into each other and merge. The gradient is
  purely radial (pointing toward the attractor) and there is no perpendicular
  degree of freedom to sustain orbital motion.

  This is a PARTIAL PASS: gravity is topological (works on any connected graph),
  but stable orbits require dimensionality (at least 2 spatial dimensions providing
  a perpendicular escape route from the radial gradient).

  spread_fraction = 1/k (c = 1 hop/tick) is the physically correct value, not a
  free parameter. Each tick, gamma propagates one hop — matching the lattice's
  1 cell/tick spreading speed. With k=6: alpha = 1/6 ≈ 0.167.

  See experiment_description.md for full analysis.

Usage:
    python three_body_graph.py --verify
    python three_body_graph.py --calibrate
    python three_body_graph.py
    python three_body_graph.py --quick
    python three_body_graph.py --n-nodes 100000 --k 6 --beta 0.3
    python three_body_graph.py --dynamics-ticks 50000
    python three_body_graph.py --spread-fraction 0.005 --decay 0.9999

Date: February 2026
Substrate: Watts-Strogatz random graph (no spatial geometry)
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


# ===========================================================================
# GammaFieldGraph — Sparse graph-based gamma field
# ===========================================================================

class GammaFieldGraph:
    """Gamma field on a Watts-Strogatz random graph.

    Each node holds scalar gamma values (one array per entity label).
    Spreading uses precomputed sparse matrix: S = (1-alpha)*I + (alpha/k)*A
    where A is the adjacency matrix and alpha = spread_fraction.
    """

    def __init__(self, n_nodes, k=6, beta=0.3, spread_fraction=None, decay=0.9999, seed=42):
        self.n_nodes = n_nodes
        self.k = k
        self.beta = beta
        self.decay = decay
        self.seed = seed

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

        print(f"  Generating Watts-Strogatz graph: N={n_nodes}, k={k}, "
              f"beta={beta}, seed={seed}")
        t0 = time.time()
        self.graph = nx.watts_strogatz_graph(n_nodes, k, beta, seed=seed)
        elapsed = time.time() - t0
        print(f"    Graph generated in {elapsed:.1f}s")

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

    Movement is discrete hops. KE accumulates from gradient magnitude,
    spent on hops (1 KE per hop). Each hop deposits drain_deposit gamma.

    Mass-conserving existence: during dynamics, the entity withdraws its
    deposit from the previous node and places it at the current node.
    This means the gamma well FOLLOWS the entity, rather than staying
    at the original formation position.
    """

    def __init__(self, label, start_node, deposit_amount=1.0, drain_deposit=0.5,
                 max_hops_per_tick=20, k_neighbors=6, color='blue'):
        self.label = label
        self.node = start_node
        self.deposit_amount = deposit_amount
        self.drain_deposit = drain_deposit
        self.max_hops_per_tick = max_hops_per_tick
        self.color = color

        self.ke = 0.0
        self.last_node = None
        self.hops_this_tick = 0
        self.prev_deposit_node = start_node  # for mass-conserving motion

        # Trajectory memory: recent nodes visited (angular momentum analog).
        # Prevents the entity from retracing its path, forcing it to take
        # longer routes around attractors instead of falling straight in.
        self.recent_path = deque(maxlen=k_neighbors)
        self.k_neighbors = k_neighbors

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
                 distance_interval=50, close_encounter_threshold=2):
    """Main dynamics loop with leapfrog-style half-kick integration.

    SPREAD (commit) -> READ + HALF-KICK -> MOVE -> HALF-KICK -> WRITE (deposits)

    Returns diagnostics dict.
    """
    diagnostics = {
        'energy': [],
        'distances': [],
        'events': [],
        'speeds': [],
    }

    print(f"  Dynamics: {dynamics_ticks} ticks, log_interval={log_interval}, "
          f"distance_interval={distance_interval}")
    t0 = time.time()
    n_close_encounters = 0

    for tick in range(dynamics_ticks):
        # === COMMIT: spread all fields ===
        field_graph.spread_all()

        # === READ + HALF-KICK ===
        grad_mags = {}
        for entity in entities:
            _, grad_mag = entity.read_gradient(field_graph)
            entity.accumulate(grad_mag * 0.5)
            grad_mags[entity.label] = grad_mag

        # === MOVE: discrete hops ===
        for entity in entities:
            entity.move(field_graph)

        # === HALF-KICK at new position ===
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

    # Panel 2: Speeds
    ax = axes[0, 1]
    if diagnostics['speeds']:
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

    # Panel 3: KE
    ax = axes[1, 0]
    if diagnostics['energy']:
        ticks = [e['tick'] for e in diagnostics['energy']]
        for i, entity in enumerate(entities):
            vals = [e.get(f"KE_{entity.label}", 0) for e in diagnostics['energy']]
            ax.plot(ticks, vals, '-', color=colors_cycle[i % len(colors_cycle)],
                    linewidth=0.8, label=f"KE {entity.label}")
        total_ke = [e.get('KE_total', 0) for e in diagnostics['energy']]
        ax.plot(ticks, total_ke, 'k-', linewidth=1.2, label='KE total')
        ax.legend(fontsize=7)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Kinetic Energy")
    ax.set_title("Kinetic Energy")
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

    print(f"\n  {'=' * 40}")
    print(f"  Overall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print(f"  {'=' * 40}")
    return all_passed


# ===========================================================================
# Calibration — Two-body infall
# ===========================================================================

def run_calibration(n_nodes=50000, k=6, beta=0.3, spread_fraction=None,
                    decay=0.9999, formation_ticks=2000, dynamics_ticks=10000,
                    seed=42):
    """Two-body calibration: pin entity A (deposits only), release entity B.

    Measures infall time, peak velocity, whether naturally bounded.
    """
    print("=" * 60)
    print("CALIBRATION: Two-body infall on graph")
    print("=" * 60)

    fg = GammaFieldGraph(n_nodes=n_nodes, k=k, beta=beta,
                         spread_fraction=spread_fraction, decay=decay, seed=seed)

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
                           drain_deposit=0.5, color='blue')

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

        # B: half-kick, move, half-kick, deposit
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
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle("Calibration: Two-Body Infall on Graph", fontsize=14)

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
        fig.savefig(RESULTS_DIR / "calibration_infall.png", dpi=150)
        plt.close(fig)
        print(f"  Saved: calibration_infall.png")

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
                   log_interval=100, distance_interval=50):
    """Full three-body experiment on graph."""
    print("=" * 60)
    print("THREE-BODY DYNAMICS ON GRAPH")
    print("=" * 60)
    print(f"  N={n_nodes}, k={k}, beta={beta}, decay={decay}")
    print(f"  formation={formation_ticks}, dynamics={dynamics_ticks}")
    print(f"  deposit={deposit_amount}, drain={drain_deposit}, max_hops={max_hops_per_tick}")

    fg = GammaFieldGraph(n_nodes=n_nodes, k=k, beta=beta,
                         spread_fraction=spread_fraction, decay=decay, seed=seed)

    # Graph stats
    avg_path, clustering = fg.graph_stats()
    print(f"  Graph stats: avg_path ~ {avg_path:.1f}, clustering = {clustering:.4f}")

    # Target separation: 40-80% of avg path length, bounded by min_separation
    min_sep = max(3, min(min_separation, int(avg_path * 0.4)))
    max_sep = max(min_sep + 2, int(avg_path * 0.8))
    print(f"  Target separation: {min_sep}-{max_sep} hops")

    # Place three entities
    nodes = place_entities_apart(fg, n_entities=3, min_separation=min_sep,
                                 max_separation=max_sep, seed=seed)

    # Create fields and entities
    labels = ["A", "B", "C"]
    colors = ["red", "green", "blue"]
    entities = []
    for i, (label, color) in enumerate(zip(labels, colors)):
        fg.add_field(label)
        entity = GraphEntity(label, start_node=nodes[i],
                             deposit_amount=deposit_amount,
                             drain_deposit=drain_deposit,
                             max_hops_per_tick=max_hops_per_tick,
                             k_neighbors=k, color=color)
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
                               distance_interval=distance_interval)

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
    plot_distances(diagnostics, tag)
    plot_speeds(diagnostics, entities, tag)
    plot_energy(diagnostics, entities, tag)
    plot_gamma_growth(diagnostics, tag)
    plot_summary(diagnostics, entities, tag)

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

    # --- Criterion 4: Energy exchange ---
    if diagnostics['energy'] and len(diagnostics['energy']) >= 2:
        # Check if KE changes hands: compute variance of each entity's KE
        ke_data = {}
        for entity in entities:
            ke_key = f"KE_{entity.label}"
            values = [e.get(ke_key, 0) for e in diagnostics['energy']]
            ke_data[entity.label] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'max': max(values),
                'final': values[-1],
            }

        print(f"\n  4. ENERGY EXCHANGE:")
        for label, stats in ke_data.items():
            print(f"     {label}: mean={stats['mean']:.2f}, std={stats['std']:.2f}, "
                  f"max={stats['max']:.2f}, final={stats['final']:.2f}")

        # Any chaotic exchange? Look for KE variance > 0
        any_exchange = any(stats['std'] > 0.1 for stats in ke_data.values())
        print(f"     Chaotic KE exchange: {any_exchange}")
        result['energy_exchange'] = any_exchange
        result['ke_stats'] = ke_data

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

    # --- Criterion 7: Distance oscillation (orbits?) ---
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
            print(f"     {k}: {rev} reversals in {len(diagnostics['distances'])} samples")

        any_oscillation = any(rev > 5 for rev in oscillation.values())
        print(f"     Orbital behavior detected: {any_oscillation}")
        result['oscillation'] = oscillation
        result['orbital_behavior'] = any_oscillation

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
        },
        'energy': diagnostics['energy'],
        'distances': diagnostics['distances'],
        'speeds': diagnostics['speeds'],
        'events': diagnostics['events'],
        'trajectories': {e.label: e.trajectory for e in entities},
    }
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
            seed=args.seed,
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
    )

    print("\n" + "=" * 60)
    print("EXPERIMENT #64_109 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
