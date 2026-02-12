import numpy as np
import matplotlib.pyplot as plt

# -----------------------------------------
# PARAMETERS
# -----------------------------------------
steps = 200
emission_strength = 0.05     # recoil per photon
gravity_strength = 0.02      # curvature pull
photon_speed = 0.3           # outward photon velocity

# -----------------------------------------
# SIMULATION FUNCTION
# -----------------------------------------
def simulate(curvature_sign):
    """
    curvature_sign = +1 for hill, -1 for well
    """
    pos = 0.0
    vel = 0.0
    positions = []
    photon_positions = []

    for _ in range(steps):
        # Gravity effect (hill pushes outward, well pulls inward)
        vel += curvature_sign * gravity_strength

        # Emit photon outward
        photon_positions.append(pos)  # photon starts at entity position
        vel -= emission_strength      # recoil pushes opposite direction

        # Update entity
        pos += vel
        positions.append(pos)

        # Update photons (all move outward)
        photon_positions = [p + photon_speed for p in photon_positions]

    return np.array(positions), np.array(photon_positions)

# -----------------------------------------
# RUN BOTH SIMULATIONS
# -----------------------------------------
hill_entity, hill_photons = simulate(+1)
well_entity, well_photons = simulate(-1)

# -----------------------------------------
# PLOT RESULTS
# -----------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(14, 5))

# Entity trajectories
axs[0].plot(hill_entity, label="Hill entity")
axs[0].plot(well_entity, label="Well entity")
axs[0].set_title("Entity Trajectories")
axs[0].set_xlabel("Time step")
axs[0].set_ylabel("Position")
axs[0].legend()
axs[0].grid(True)

# Photon clouds
axs[1].scatter(range(len(hill_photons)), hill_photons, s=5, label="Hill photons")
axs[1].scatter(range(len(well_photons)), well_photons, s=5, label="Well photons")
axs[1].set_title("Photon Positions After Simulation")
axs[1].set_xlabel("Photon index")
axs[1].set_ylabel("Position")
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()
