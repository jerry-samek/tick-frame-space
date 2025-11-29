import numpy as np
import matplotlib.pyplot as plt
import sys
from tickspace_snapshot import read_snapshot

# Load snapshot
snapshot = read_snapshot(sys.argv[1])

# Extract energy and positions
energies = np.array([e.energy for e in snapshot.entities], dtype=float)
coords = np.array([e.position for e in snapshot.entities], dtype=float)
r = np.linalg.norm(coords, axis=1)  # Euclidean radius

# ---- Plot 1: Energy histogram ----
plt.figure(figsize=(7, 4))
bins = np.linspace(energies.min(), energies.max(), 25)
plt.hist(energies, bins=bins, color="#8bd3c7", edgecolor="#1b1f23")
plt.title("Energy distribution")
plt.xlabel("Energy")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# ---- Plot 2: Radial density ----
plt.figure(figsize=(7, 4))
# Choose shell thickness; adjust for your scale
dr = max(1.0, (r.max() - r.min()) / 30)
radial_bins = np.arange(0, r.max() + dr, dr)
counts, edges = np.histogram(r, bins=radial_bins)
centers = 0.5 * (edges[1:] + edges[:-1])

plt.plot(centers, counts, color="#e07a5f", lw=2)
plt.fill_between(centers, counts, step="mid", alpha=0.25, color="#e07a5f")
plt.title("Radial density")
plt.xlabel("Radius from origin")
plt.ylabel("Entities per shell")
plt.tight_layout()
plt.show()
