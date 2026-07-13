"""Per-tick metrics + post-hoc entity clustering.

Spec §5: per-tick metrics include total_energy, n_firing_cells, max/mean E,
and cluster centroids (analyst-side, using saved coordinates).
"""

import numpy as np


def per_tick_summary(E, src):
    """Compute lightweight per-tick metrics.

    Args:
        E: (N,) int64 — current cell energy
        src: (2M,) int64 — to compute per-cell degree

    Returns:
        dict with keys: total_energy, max_E, mean_E, n_firing_cells
        where n_firing_cells = #cells with E ≥ degree (proxy: E ≥ 1
        is the looser proxy used here; "firing" defined per edge).
    """
    degree = np.bincount(src, minlength=E.shape[0]).astype(np.int64)
    firing = (E >= degree) & (degree > 0)

    return {
        'total_energy': int(E.sum()),
        'max_E': int(E.max()),
        'mean_E': float(E.mean()),
        'n_firing_cells': int(firing.sum()),
    }


def cluster_high_energy(E, coords, threshold_quantile=0.95):
    """Identify high-energy clusters via thresholding + spatial neighbors.

    Analyst-side use only — uses coordinates. NOT used by the substrate.

    Args:
        E: (N,) int — cell energy
        coords: (N, 3) float — analyst coords
        threshold_quantile: only cells with E above this quantile considered

    Returns:
        list of dicts: [{'centroid': (x,y,z), 'mass': total_E, 'cell_count': n}, ...]
        sorted descending by mass
    """
    from scipy.cluster.hierarchy import fcluster, linkage

    threshold = np.quantile(E, threshold_quantile)
    high_idx = np.where(E > threshold)[0]
    if len(high_idx) < 2:
        if len(high_idx) == 1:
            i = high_idx[0]
            return [{'centroid': tuple(coords[i]), 'mass': int(E[i]), 'cell_count': 1}]
        return []

    high_coords = coords[high_idx]
    high_E = E[high_idx]

    # Single-linkage clustering with cutoff distance
    # Cutoff chosen as roughly the typical edge length of the RGG
    # (caller can adjust by passing a different threshold_quantile).
    linkage_matrix = linkage(high_coords, method='single')
    cluster_ids = fcluster(linkage_matrix, t=0.05, criterion='distance')

    clusters = []
    for cid in np.unique(cluster_ids):
        mask = cluster_ids == cid
        cells = high_idx[mask]
        masses = E[cells]
        total_mass = int(masses.sum())
        if total_mass == 0:
            continue
        # Mass-weighted centroid
        centroid = (coords[cells] * masses[:, None]).sum(axis=0) / total_mass
        clusters.append({
            'centroid': tuple(centroid.tolist()),
            'mass': total_mass,
            'cell_count': int(mask.sum()),
        })

    clusters.sort(key=lambda c: -c['mass'])
    return clusters
