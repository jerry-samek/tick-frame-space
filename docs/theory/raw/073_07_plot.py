import matplotlib.pyplot as plt
import numpy as np

# Distances (Mly)
d = np.array([2.54, 2.88, 10.7, 11.4, 11.99, 12.0, 12.0, 23.5, 31.1, 53.5])

# Normalized jitter (alpha = 1)
J_tilde = np.array([0.86, 0.21, 0.036, 0.071, 0.12, 0.19, 1.18, 0.0087, 6.7, 0.54])

names = ["M31", "M33", "IC342", "NGC253", "M81", "M82", "CenA", "M51", "M104", "M87"]

plt.figure(figsize=(7, 5))
plt.scatter(d, J_tilde, color="cyan")

for x, y, name in zip(d, J_tilde, names):
    plt.text(x * 1.02, y * 1.02, name, fontsize=8)

plt.xscale("log")
plt.yscale("log")
plt.xlabel("Distance (Mly)")
plt.ylabel("Normalized jitter $\~J$ (α=1)")
plt.title("Distance vs. Normalized Jitter for Selected Galaxies")
plt.grid(True, which="both", ls="--", alpha=0.4)
plt.tight_layout()
plt.show()
