import csv, math
import numpy as np
import sys
from pathlib import Path
from tickspace_snapshot import read_snapshot

# Load snapshot (use command line arg or default to "frame.snap")
snapshot_file = sys.argv[1] if len(sys.argv) > 1 else "frame.snap"
snapshot = read_snapshot(snapshot_file)

# Extract positions and momenta
positions = np.array([e.position for e in snapshot.entities], dtype=np.float64)
momenta = np.array([e.momentum_vector for e in snapshot.entities], dtype=np.float64)

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
output_csv = Path(snapshot_file).stem + "_metrics.csv"
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Snapshot", "COM_X", "COM_Y", "COM_Z", "COM_Magnitude", "Radial_Flux"])
    writer.writerow([snapshot_file, float(com[0]), float(com[1]), float(com[2]), com_mag, radial_flux])

print(f"Metrics saved to {output_csv}")
