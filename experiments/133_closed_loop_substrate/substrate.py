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
