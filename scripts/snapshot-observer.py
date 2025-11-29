import json
import numpy as np
import sys
import matplotlib.pyplot as plt

# --- 1. Načtení dat z JSON ---
with open(sys.argv[1], "r") as f:
    data = json.load(f)

# Očekáváme list bodů: [{"x":..., "y":..., "z":...}, ...]
points = np.array([entity["position"] for entity in data])

# --- 2. Definice pozorovatele ---
observer_position = np.array([10, 20, 30])  # uprostřed vesmíru
fov_radius = 100.0                        # poloměr pole vidění
resolution = (256, 256)                  # rozlišení senzoru (např. 256x256)

# --- 3. Výběr bodů v poli vidění ---
distances = np.linalg.norm(points - observer_position, axis=1)
visible_points = points[distances < fov_radius]

# --- 4. Projekce na rovinu XY ---
# (můžeš změnit na jinou rovinu podle orientace pozorovatele)
pts_obs = points - observer_position

# Project to XY in observer frame
x = pts_obs[:, 0]
y = pts_obs[:, 1]

#x = visible_points[:, 0]
#y = visible_points[:, 1]

# --- 5. Rasterizace do obrazu ---
img, xedges, yedges = np.histogram2d(
    x, y, bins=resolution, range=[[-fov_radius, fov_radius], [-fov_radius, fov_radius]]
)

# --- 6. Vizualizace ---
plt.figure(figsize=(6,6))
plt.imshow(img.T, origin="lower", cmap="inferno",
           extent=[-fov_radius, fov_radius, -fov_radius, fov_radius])
plt.title("Observer view")
plt.xlabel("X axis")
plt.ylabel("Y axis")
plt.colorbar(label="Counts")
plt.show()
