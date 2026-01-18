# hydrogen_mz_test.py
import numpy as np
import matplotlib.pyplot as plt

# Constants
h = 6.62607015e-34
m_H = 1.6735575e-27  # kg

# User parameters
T = 300.0  # K (set small T for larger lambda)
v = np.sqrt(3 * 1.380649e-23 * T / m_H)  # thermal RMS speed
lam = h / (m_H * v)
L = 0.5  # path length (m)
det_x = np.linspace(-1e-6, 1e-6, 2000)  # detector coordinate (m)

# Geometry: small-angle approx maps x -> path diff ΔL ≈ x * (L/d)
d = 0.01  # effective interferometer arm separation (m)
deltaL = det_x * (L / d)

# Phase difference and intensity
delta_phi = 2 * np.pi * deltaL / lam
I0 = 1.0
I = I0 * (1 + np.cos(delta_phi))  # normalized fringe intensity

plt.figure(figsize=(8, 4))
plt.plot(det_x * 1e6, I, lw=1)
plt.xlabel('Detector x (µm)')
plt.ylabel('Normalized intensity')
plt.title(f'H-like matter-wave fringes: T={T}K, λ={lam:.2e} m')
plt.grid(True)
plt.tight_layout()
plt.show()
