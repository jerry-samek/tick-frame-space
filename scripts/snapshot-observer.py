import numpy as np
import sys
import matplotlib.pyplot as plt
from tickspace_snapshot import read_snapshot

# --- 1. Načtení dat ze snapshotu ---
snapshot = read_snapshot(sys.argv[1])
points = np.array([entity.position for entity in snapshot.entities])

# --- 2. Parametry pozorovatele ---
observer_position = np.array([0.0, 0.0, 0.0])
fov_radius = 100.0
resolution = (256, 256)

# --- 3. Funkce pro vykreslení ---
def update_view():
    pts_obs = points - observer_position
    x = pts_obs[:, 0]
    y = pts_obs[:, 1]

    img, _, _ = np.histogram2d(
        x, y, bins=resolution,
        range=[[-fov_radius, fov_radius], [-fov_radius, fov_radius]]
    )
    ax.clear()
    ax.imshow(img.T, origin="lower", cmap="inferno",
              extent=[-fov_radius, fov_radius, -fov_radius, fov_radius])
    ax.set_title(f"Observer view at {observer_position}")
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    plt.draw()

# --- 4. Ovládání kláves ---
def on_key(event):
    global observer_position
    step = 5.0  # krok posunu
    if event.key == "up":
        observer_position[1] += step
    elif event.key == "down":
        observer_position[1] -= step
    elif event.key == "left":
        observer_position[0] -= step
    elif event.key == "right":
        observer_position[0] += step
    elif event.key == "pageup":
        observer_position[2] += step
    elif event.key == "pagedown":
        observer_position[2] -= step
    update_view()

# --- 5. Inicializace ---
fig, ax = plt.subplots(figsize=(6,6))
fig.canvas.mpl_connect("key_press_event", on_key)
update_view()
plt.show()
