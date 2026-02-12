import numpy as np
import matplotlib.pyplot as plt

# -----------------------------------------
# PARAMETERS
# -----------------------------------------
steps = 1000

gravity_strength = 0.05
emission_strength = 0.03
base_photon_speed = 0.20

alpha = 1.0   # curvature influence on photon speed

# entities: (x, y)
initial_positions = np.array([
    [-1.0,  2.0],   # E0 top
    [ 0.0,  1.0],   # E1 middle
    [ 1.0,  0.0],   # E2 bottom
], dtype=float)

# -----------------------------------------
# GEOMETRY
# -----------------------------------------
def hill_potential(x, y):
    return np.sqrt(x*x + y*y)

def well_potential(x, y):
    return -np.sqrt(x*x + y*y)

def local_slope(potential_fn, x, y):
    eps = 1e-3
    dVdx = (potential_fn(x+eps, y) - potential_fn(x-eps, y)) / (2*eps)
    dVdy = (potential_fn(x, y+eps) - potential_fn(x, y-eps)) / (2*eps)
    return np.hypot(dVdx, dVdy)

# -----------------------------------------
# SIMULATION
# -----------------------------------------
def simulate(potential_fn, curvature_sign):
    positions = initial_positions.copy()
    velocities = np.zeros_like(positions)

    pos_history = [positions.copy()]
    rad_kick_history = [np.zeros_like(positions)]

    # photon format: [x, y, dir_y, coupling_strength]
    photons = []

    for _ in range(steps):

        # 1. Gravity (downward)
        velocities[:, 1] += curvature_sign * (-gravity_strength)

        # 2. Emission
        for i in range(len(positions)):
            x, y = positions[i]
            # initial coupling placeholder (will be overwritten next step)
            photons.append([x, y, +1.0, 1.0])
            velocities[i, 1] -= emission_strength

        # 3. Photon propagation with curvature-dependent speed
        new_photons = []
        for p_x, p_y, p_dir_y, _ in photons:

            slope = local_slope(potential_fn, p_x, p_y)

            # curvature-dependent photon speed
            actual_photon_speed = base_photon_speed / (1 + alpha * slope)

            # coupling depends on actual photon speed
            coupling_strength = max(0.0, 1.0 - actual_photon_speed)

            # hill: photons go outward (+y)
            # well: photons bend inward (-y)
            effective_dir_y = p_dir_y if curvature_sign > 0 else -1.0

            p_y += effective_dir_y * actual_photon_speed

            if -20 < p_y < 20:
                new_photons.append([p_x, p_y, p_dir_y, coupling_strength])

        photons = new_photons

        # 4. Radiative coupling
        step_rad_kicks = np.zeros_like(positions)
        for i in range(len(positions)):
            x, y = positions[i]
            for p_x, p_y, p_dir_y, coupling_strength in photons:
                if np.hypot(p_x - x, p_y - y) < 0.2:

                    kick_dir_y = p_dir_y if curvature_sign > 0 else -1.0
                    kick = coupling_strength * kick_dir_y

                    velocities[i, 1] += kick
                    step_rad_kicks[i, 1] += kick

        # 5. Update
        positions += velocities

        pos_history.append(positions.copy())
        rad_kick_history.append(step_rad_kicks)

    return np.array(pos_history), np.array(rad_kick_history)


# -----------------------------------------
# RUN BOTH CASES
# -----------------------------------------
hill_pos, hill_rad = simulate(hill_potential, +1)
well_pos, well_rad = simulate(well_potential, -1)

# -----------------------------------------
# PLOT Y-POSITIONS
# -----------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(14, 5))

labels = ["Top (E0)", "Middle (E1)", "Bottom (E2)"]
colors = ["tab:blue", "tab:orange", "tab:green"]

t = np.arange(hill_pos.shape[0])

# Hill
for i in range(3):
    axs[0].plot(t, hill_pos[:, i, 1], label=labels[i], color=colors[i])
axs[0].set_title("Hill geometry – curvature-dependent photon speed & coupling")
axs[0].set_xlabel("Time step")
axs[0].set_ylabel("y position")
axs[0].legend()
axs[0].grid(True)

# Well
for i in range(3):
    axs[1].plot(t, well_pos[:, i, 1], label=labels[i], color=colors[i])
axs[1].set_title("Well geometry – curvature-dependent photon speed & coupling")
axs[1].set_xlabel("Time step")
axs[1].set_ylabel("y position")
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()
