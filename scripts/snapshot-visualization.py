import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys

# List of snapshot filenames

snapshots = [sys.argv[1]]

#snapshots = [
    
#    "time-frame.187812.json",
    # ... add more snapshots
#]

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

all_x, all_y, all_z, all_energy = [], [], [], []

for filename in snapshots:
    with open(filename, "r") as f:
        data = json.load(f)
    for entity in data:
        x, y, z = entity["position"]["coordinates"]
        energy = entity["energy"]
        all_x.append(x)
        all_y.append(y)
        all_z.append(z)
        all_energy.append(energy)

# Scatter plot with per-entity coloring by energy
sc = ax.scatter(all_x, all_y, all_z, c=all_energy, cmap="plasma", s=40)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("Entity positions colored by energy (step 8800)")

# Add colorbar to show energy scale
cbar = plt.colorbar(sc, ax=ax, shrink=0.6)
cbar.set_label("Energy")

plt.tight_layout()
plt.show()