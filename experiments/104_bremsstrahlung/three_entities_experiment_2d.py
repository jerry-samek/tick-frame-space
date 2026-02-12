import numpy as np
import matplotlib.pyplot as plt

# -----------------------------------------
# PARAMETERS
# -----------------------------------------
steps = 1000

gravity_strength = 0.01
emission_strength = 0.03
photon_speed = 0.01
coupling_strength = 1 - photon_speed

# entities: (x, y)
initial_positions = np.array([
    [-1.0,  2.0],   # E0 top
    [ 0.0,  1.0],   # E1 middle
    [ 1.0,  0.0],   # E2 bottom
], dtype=float)

# -----------------------------------------
# SIMULATION
# -----------------------------------------
def simulate(curvature_sign):
    """
    curvature_sign = +1 for hill, -1 for well
    Gravity acts along -y; photons emitted along +y.
    """
    positions = initial_positions.copy()
    velocities = np.zeros_like(positions)

    # logging
    pos_history = [positions.copy()]
    rad_kick_history = [np.zeros_like(positions)]  # per-step radiative kicks

    # photons: list of [x, y, dir_y]
    photons = []

    for _ in range(steps):

        # 1. Gravity (downward in y)
        velocities[:, 1] += curvature_sign * (-gravity_strength)

        # 2. Emission from each entity
        for i in range(len(positions)):
            x, y = positions[i]
            # photon emitted upward in +y
            photons.append([x, y, +1.0])
            # recoil downward in y
            velocities[i, 1] -= emission_strength

        # 3. Photon propagation
        new_photons = []
        for p_x, p_y, p_dir_y in photons:
            # hill: photons keep going upward
            # well: photons bend downward
            effective_dir_y = p_dir_y if curvature_sign > 0 else -1.0
            p_y += effective_dir_y * photon_speed

            # keep photons in a window
            if -20.0 < p_y < 20.0:
                new_photons.append([p_x, p_y, p_dir_y])
        photons = new_photons

        # 4. Radiative coupling
        step_rad_kicks = np.zeros_like(positions)
        for i in range(len(positions)):
            x, y = positions[i]
            for p_x, p_y, p_dir_y in photons:
                # simple proximity check in 2D
                if np.hypot(p_x - x, p_y - y) < 0.2:
                    # hill: upward push; well: downward push
                    kick_dir_y = p_dir_y if curvature_sign > 0 else -1.0
                    kick = coupling_strength * kick_dir_y
                    velocities[i, 1] += kick
                    step_rad_kicks[i, 1] += kick

        # 5. Update entities
        positions += velocities

        pos_history.append(positions.copy())
        rad_kick_history.append(step_rad_kicks)

    return np.array(pos_history), np.array(rad_kick_history)


# -----------------------------------------
# RUN BOTH CASES
# -----------------------------------------
hill_pos, hill_rad = simulate(+1)
well_pos, well_rad = simulate(-1)

# -----------------------------------------
# SIMPLE LOGGING INSPECTION
# -----------------------------------------
# Example: total radiative kick in y per entity
hill_total_rad_y = hill_rad[:, :, 1].sum(axis=0)
well_total_rad_y = well_rad[:, :, 1].sum(axis=0)

print("Hill total radiative kick (y) per entity:", hill_total_rad_y)
print("Well total radiative kick (y) per entity:", well_total_rad_y)

# -----------------------------------------
# PLOT Y-POSITIONS OVER TIME
# -----------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(14, 5))

labels = ["Top (E0)", "Middle (E1)", "Bottom (E2)"]
colors = ["tab:blue", "tab:orange", "tab:green"]

t = np.arange(hill_pos.shape[0])

# Hill
for i in range(3):
    axs[0].plot(t, hill_pos[:, i, 1], label=labels[i], color=colors[i])
axs[0].set_title("Hill geometry (positive curvature) – y(t)")
axs[0].set_xlabel("Time step")
axs[0].set_ylabel("y position")
axs[0].legend()
axs[0].grid(True)

# Well
for i in range(3):
    axs[1].plot(t, well_pos[:, i, 1], label=labels[i], color=colors[i])
axs[1].set_title("Well geometry (negative curvature) – y(t)")
axs[1].set_xlabel("Time step")
axs[1].set_ylabel("y position")
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()
