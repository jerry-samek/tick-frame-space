import json, math, csv
import numpy as np

# Load frame
with open("frame.json", "r") as f:
    data = json.load(f)

# Extract positions and momenta
positions = np.array([e["position"]["coordinates"] for e in data], dtype=np.float64)
momenta = np.array([e["momentum"]["vector"] for e in data], dtype=np.float64)

# Compute true center-of-mass
com = positions.mean(axis=0)
com_mag = float(np.linalg.norm(com))

# Compute radial unit vectors
radii = np.linalg.norm(positions, axis=1)
hat_r = np.zeros_like(positions)
nonzero = radii > 0
hat_r[nonzero] = (positions[nonzero].T / radii[nonzero]).T

# Compute radial momentum flux
radial_flux = float(np.sum(np.einsum("ij,ij->i", momenta, hat_r)))

# Save to CSV
with open("frame_metrics.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Frame ID", "COM_X", "COM_Y", "COM_Z", "COM_Magnitude", "Radial_Flux"])
    writer.writerow(["frame.json", float(com[0]), float(com[1]), float(com[2]), com_mag, radial_flux])

print("Metrics saved to frame_metrics.csv")
