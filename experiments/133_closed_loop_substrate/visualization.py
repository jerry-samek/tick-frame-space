"""Analyst-side visualization for closed-loop substrate experiments.

These helpers use coordinates and have no role in the substrate dynamics.
They produce PNGs and return numerical fit results.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def radial_density_profile(E, coords, center, n_bins=30, r_min=None, r_max=None):
    """Bin cell energies by radial distance from a center point.

    Args:
        E: (N,) int — cell energy
        coords: (N, 3) float
        center: (3,) center coordinates
        n_bins: number of log-spaced radial bins
        r_min, r_max: bin range; defaults: (1.5×min nonzero distance, 0.7×max distance)

    Returns:
        r_centers: (n_bins,) bin centers
        density: (n_bins,) mean E per cell in each bin
    """
    r = np.linalg.norm(coords - np.asarray(center)[None, :], axis=1)
    if r_min is None:
        r_min = np.maximum(r.min(), 1e-3) * 1.5
    if r_max is None:
        r_max = r.max() * 0.7

    bin_edges = np.logspace(np.log10(r_min), np.log10(r_max), n_bins + 1)
    bin_indices = np.digitize(r, bin_edges) - 1

    r_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    density = np.zeros(n_bins)
    for i in range(n_bins):
        mask = bin_indices == i
        if mask.any():
            density[i] = E[mask].mean()

    return r_centers, density


def fit_loglog_slope(r, density, density_floor=1e-6):
    """Fit log-log slope of density vs r in regions where density > floor.

    Returns:
        slope: float — fitted slope (e.g., −2 for 1/r²)
        intercept: float
        r_squared: float — goodness of fit
    """
    mask = (density > density_floor) & (r > 0)
    if mask.sum() < 3:
        return float('nan'), float('nan'), float('nan')

    log_r = np.log(r[mask])
    log_d = np.log(density[mask])
    slope, intercept = np.polyfit(log_r, log_d, 1)
    pred = slope * log_r + intercept
    ss_res = np.sum((log_d - pred) ** 2)
    ss_tot = np.sum((log_d - log_d.mean()) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')

    return float(slope), float(intercept), float(r_squared)


def plot_radial_profile(r, density, slope=None, out_path=None, title=''):
    """Save log-log radial density plot."""
    fig, ax = plt.subplots(figsize=(6, 5))
    mask = density > 0
    ax.loglog(r[mask], density[mask], 'o-', label='measured')
    if slope is not None and not np.isnan(slope):
        # Reference line at fitted slope through first valid point
        idx0 = np.where(mask)[0][0]
        ref = density[idx0] * (r / r[idx0]) ** slope
        ax.loglog(r, ref, 'r--', label=f'slope={slope:.3f}', alpha=0.7)
    ax.set_xlabel('r (graph hop / euclidean distance)')
    ax.set_ylabel('mean energy density')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_trajectory(positions, star_pos=None, out_path=None, title=''):
    """Plot a 2D projection of an orbit trace.

    Args:
        positions: (T, 3) array of centroid positions over time
        star_pos: (3,) optional — star centroid for reference
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(positions[:, 0], positions[:, 1], '-', linewidth=0.8)
    ax.plot(positions[0, 0], positions[0, 1], 'go', label='start')
    ax.plot(positions[-1, 0], positions[-1, 1], 'r^', label='end')
    if star_pos is not None:
        ax.plot(star_pos[0], star_pos[1], 'k*', markersize=15, label='star')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=120)
    plt.close(fig)
