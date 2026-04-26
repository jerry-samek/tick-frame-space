"""Closed-loop graph substrate -- core mechanics.

Spec: docs/superpowers/specs/2026-04-26-closed-loop-graph-substrate-design.md

Substrate is a graph (RGG-constructed). Coordinates are returned to caller
but the substrate itself never references them -- they are analyst-side only.

Directed-edge representation enables fully-vectorized tick updates via
numpy scatter operations (np.add.at).
"""

import numpy as np
from scipy.spatial import cKDTree


def build_rgg(n_nodes: int, radius: float, seed: int = 42):
    """Build a 3D random geometric graph.

    Args:
        n_nodes: number of cells
        radius: connection radius in unit cube [0,1]^3
        seed: numpy RNG seed for reproducibility

    Returns:
        coords: (N, 3) float64 -- analyst-side only, never used by substrate
        src: (2M,) int64 -- source cell of each directed edge
        dst: (2M,) int64 -- dest cell of each directed edge
        back_edge: (2M,) int64 -- for directed edge i, the index of (dst, src)
    """
    rng = np.random.default_rng(seed)
    coords = rng.random((n_nodes, 3), dtype=np.float64)

    tree = cKDTree(coords)
    pairs = tree.query_pairs(radius, output_type='ndarray')  # (M, 2), u < v

    if len(pairs) == 0:
        raise ValueError(f"No edges built; radius {radius} too small for n={n_nodes}")

    # Build directed edges: each undirected (u, v) -> two directed (u->v) and (v->u)
    forward_src = pairs[:, 0]
    forward_dst = pairs[:, 1]
    backward_src = pairs[:, 1]
    backward_dst = pairs[:, 0]

    src = np.concatenate([forward_src, backward_src]).astype(np.int64)
    dst = np.concatenate([forward_dst, backward_dst]).astype(np.int64)

    # back_edge[i] = index j such that src[j] == dst[i] and dst[j] == src[i]
    # Forward edges occupy [0, M); backward edges occupy [M, 2M).
    # Forward edge i has back_edge i + M; backward edge i+M has back_edge i.
    M = len(pairs)
    back_edge = np.concatenate([
        np.arange(M, 2 * M, dtype=np.int64),
        np.arange(0, M, dtype=np.int64),
    ])

    return coords, src, dst, back_edge


def init_state(n_nodes: int, n_directed: int, energy_init=None):
    """Initialize cell state and per-edge incoming history.

    Args:
        n_nodes: number of cells
        n_directed: number of directed edges (= 2M)
        energy_init: optional (N,) int array of initial energy per cell.
                     If None, all cells start at 0.

    Returns:
        E: (N,) int64 -- per-cell energy
        received: (2M,) int64 -- quanta received on each directed edge last tick
    """
    if energy_init is None:
        E = np.zeros(n_nodes, dtype=np.int64)
    else:
        E = np.asarray(energy_init, dtype=np.int64).copy()
        if E.shape != (n_nodes,):
            raise ValueError(f"energy_init shape {E.shape} != ({n_nodes},)")

    received = np.zeros(n_directed, dtype=np.int64)
    return E, received


def tick(E, received, src, dst, back_edge, alpha: float):
    """Execute one tick of the closed-loop substrate rule.

    Per spec §4.2:
      1. I_local[i] = received[back_edge[i]] (what came in last tick via back-edge)
      2. w_e = max(0, 1 + α·(mean(I) − I_local)), normalized per cell
      3. target_e = E[src] · w_e; outgoing[e] = floor(target_e)
      4. residue R[c] = E[c] − sum of outgoing on c's outgoing edges (held to next tick)
      5. received_per_cell[c] = sum of outgoing on c's incoming edges
      6. E_new = R + received_per_cell
      7. received_new = outgoing

    Args:
        E: (N,) int64 -- current cell energy
        received: (2M,) int64 -- quanta received on each directed edge last tick
        src, dst, back_edge: (2M,) int64 -- directed-edge structure
        alpha: float -- wake-bias strength

    Returns:
        E_new: (N,) int64 -- cell energy after tick
        received_new: (2M,) int64 -- quanta sent on each directed edge this tick
    """
    assert E.dtype == np.int64 and received.dtype == np.int64, \
        f"tick requires int64 inputs; got E.dtype={E.dtype}, received.dtype={received.dtype}"

    n_nodes = E.shape[0]
    n_directed = src.shape[0]

    # Step 1: incoming-via-back-edge per directed edge
    # For directed edge i (src=c, dst=n), I_local[i] = quanta cell c received from n last tick.
    # That arrived through the back-edge (n->c), whose index is back_edge[i].
    I_local = received[back_edge].astype(np.float64)

    # Step 2: compute mean(I) per cell, broadcast to per directed edge
    sum_I_per_cell = np.zeros(n_nodes, dtype=np.float64)
    np.add.at(sum_I_per_cell, src, I_local)
    degree = np.zeros(n_nodes, dtype=np.int64)
    np.add.at(degree, src, 1)
    mean_I_per_cell = np.zeros(n_nodes, dtype=np.float64)
    nonzero = degree > 0
    mean_I_per_cell[nonzero] = sum_I_per_cell[nonzero] / degree[nonzero]
    mean_I_per_edge = mean_I_per_cell[src]  # (2M,)

    # Wake-bias weights per directed edge
    w = 1.0 + alpha * (mean_I_per_edge - I_local)
    w = np.maximum(w, 0.0)  # clamp negatives (occurs when alpha large)

    # Normalize per cell (sum to 1 across cell's outgoing edges)
    sum_w_per_cell = np.zeros(n_nodes, dtype=np.float64)
    np.add.at(sum_w_per_cell, src, w)
    sum_w_per_edge = sum_w_per_cell[src]
    # Algebraic note: for any cell with degree k >= 1, the unclamped weights
    # sum to exactly k: Σ_e (1 + α·(mean − I_local_e)) = k + α·(k·mean − Σ_e I_local_e) = k.
    # Clamping individual negative entries to 0 can only INCREASE the sum, never zero it.
    # So sum_w_per_edge can only be 0 for degree-0 isolated cells (empty slice -> 0);
    # the np.where guard below covers that case alone.
    sum_w_per_edge = np.where(sum_w_per_edge > 0, sum_w_per_edge, 1.0)
    w = w / sum_w_per_edge

    # Step 3: targets and floors
    E_per_edge = E[src].astype(np.float64)
    target = E_per_edge * w
    outgoing = np.floor(target).astype(np.int64)

    # Step 4: residue per cell (E - sum of outgoing on its outgoing edges)
    sent_per_cell = np.zeros(n_nodes, dtype=np.int64)
    np.add.at(sent_per_cell, src, outgoing)
    residue = E - sent_per_cell

    # Step 5: received per cell (sum of outgoing on its incoming directed edges)
    # An incoming edge to cell c is one with dst[i] == c.
    received_per_cell = np.zeros(n_nodes, dtype=np.int64)
    np.add.at(received_per_cell, dst, outgoing)

    # Step 6: new energy
    E_new = residue + received_per_cell

    # Step 7: new per-edge incoming = this tick's outgoing
    received_new = outgoing

    return E_new, received_new
