import numpy as np
import matplotlib.pyplot as plt

# -----------------------------------------
# PARAMETERS
# -----------------------------------------
steps = 1000
gravity_strength = 0.01
emission_strength = 0.03
photon_speed = 0.2
coupling_strength = 0.01   # tweak this to explore regimes

initial_positions = np.array([2.0, 1.0, 0.0])  # top, middle, bottom


# -----------------------------------------
# SIMULATION
# -----------------------------------------
def simulate(curvature_sign):
    """
    curvature_sign = +1 for hill, -1 for well
    """
    positions = initial_positions.copy().astype(float)
    velocities = np.zeros_like(positions)
    history = [positions.copy()]

    # photons: list of [position, direction]
    photons = []

    for _ in range(steps):

        # 1. Gravity
        velocities += curvature_sign * gravity_strength

        # 2. Emission from each entity
        for i in range(len(positions)):
            photons.append([positions[i], +1.0])  # photon always emitted outward
            velocities[i] -= emission_strength    # recoil inward

        # 3. Photon propagation
        new_photons = []
        for p_pos, p_dir in photons:

            # Hill: photons move outward
            # Well: photons bend inward
            effective_dir = p_dir if curvature_sign > 0 else -1.0
            p_pos += effective_dir * photon_speed

            # keep photons in simulation window
            if -20.0 < p_pos < 20.0:
                new_photons.append([p_pos, p_dir])

        photons = new_photons

        # 4. Radiative coupling (photon hits entity)
        for i in range(len(positions)):
            for p_pos, p_dir in photons:
                if abs(p_pos - positions[i]) < 0.1:

                    # Hill: outward push
                    # Well: inward push (no escape channel)
                    kick_dir = p_dir if curvature_sign > 0 else -1.0

                    velocities[i] += coupling_strength * kick_dir

        # 5. Update entity positions
        positions += velocities
        history.append(positions.copy())

    return np.array(history)


# -----------------------------------------
# RUN BOTH CASES
# -----------------------------------------
hill_hist = simulate(+1)
well_hist = simulate(-1)


# -----------------------------------------
# PLOT RESULTS
# -----------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(14, 5))

labels = ["Top (E0)", "Middle (E1)", "Bottom (E2)"]
colors = ["tab:blue", "tab:orange", "tab:green"]

# Hill
for i in range(3):
    axs[0].plot(hill_hist[:, i], label=labels[i], color=colors[i])
axs[0].set_title("Hill geometry (positive curvature)")
axs[0].set_xlabel("Time step")
axs[0].set_ylabel("Position")
axs[0].legend()
axs[0].grid(True)

# Well
for i in range(3):
    axs[1].plot(well_hist[:, i], label=labels[i], color=colors[i])
axs[1].set_title("Well geometry (negative curvature)")
axs[1].set_xlabel("Time step")
axs[1].set_ylabel("Position")
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()
