import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
from tickspace_snapshot import read_snapshot

# Load snapshot
snapshot = read_snapshot(sys.argv[1])

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

all_x, all_y, all_z, all_energy, normalized_energy = [], [], [], [], []

normalizer = len(snapshot.entities)

for entity in snapshot.entities:
    x, y, z = entity.position
    energy = entity.energy
    all_x.append(x)
    all_y.append(y)
    all_z.append(z)
    all_energy.append(energy)
    normalized = energy / normalizer
    normalized_energy.append(normalized)


# Scatter plot with per-entity coloring by energy
sc = ax.scatter(all_x, all_y, all_z, c=normalized_energy, cmap="plasma", s=1) # use 1 item per cube to get a clear resolution

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title(f"Entity positions colored by energy")

# Add colorbar to show energy scale
cbar = plt.colorbar(sc, ax=ax, shrink=0.6)
cbar.set_label("Energy")

plt.tight_layout()
plt.show()
