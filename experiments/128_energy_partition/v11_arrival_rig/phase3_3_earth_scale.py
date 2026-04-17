#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 3.3: Earth at substrate scale

The fixed-model equation consumed = M * K / r^2 is dimensionless / natural
in our units. What are the physical numbers for Earth?

  - How many "tick-quanta" (nodes) make up Earth?
  - How many deposits per tick does Earth consume from the sun?
  - How many connectors from the sun reach Earth at any moment?
  - What is the deposit rate per connector?

This is a scale exercise. It only makes sense once you pick a mapping
from our abstract tick-frame units to physical ones. The most obvious
(and most commonly assumed in TFU work) is:

    1 tick       = 1 Planck time     t_P = 5.391e-44 s
    1 node_mass  = 1 Planck mass     m_P = 2.176e-8 kg
    1 hop        = 1 Planck length   L_P = 1.616e-35 m
    1 deposit    = 1 Planck impulse  p_P = m_P * c = 6.527 kg*m/s

Under these choices:
  - Earth's mass as node count = M_E / m_P
  - Gravitational force on Earth (= our "consumption" in physical terms)
    converted to deposit-rate = F / p_P deposits/s
  - Deposits per Planck tick = (F / p_P) * t_P
  - Connector count reaching Earth = (pi * R_E^2 / L_P^2)    (the Earth
    cross-section in Planck-area cells), assuming one connector per
    Planck cell crossing Earth's disk at its orbital radius

Under ANY consistent choice of base units the dimensionless ratios
(consumptions-per-connector-per-tick, fraction-of-sun's-output-earth-
intercepts, etc.) remain the same. So the results below are not unique
numbers, but they are scale-consistent reference values.
"""

import numpy as np


# --- Physical constants ---
G = 6.674e-11                # m^3 / (kg s^2)
c = 2.998e8                  # m/s
hbar = 1.055e-34             # J s

# Planck units
L_P = np.sqrt(hbar * G / c**3)      # 1.616e-35 m
t_P = np.sqrt(hbar * G / c**5)      # 5.391e-44 s
m_P = np.sqrt(hbar * c / G)         # 2.176e-8 kg
p_P = m_P * c                       # 6.527 kg*m/s (Planck momentum)

# Sun and Earth
M_SUN = 1.989e30     # kg
M_E = 5.972e24       # kg
R_E = 6.371e6        # m (Earth radius)
R_S = 6.957e8        # m (Sun radius)
R_ORBIT = 1.496e11   # m (1 AU)

# --- Mass as node count (several interpretations, pick Planck-mass) ---
N_nodes_PlanckMass = M_E / m_P
N_atoms           = 1.33e50              # order-of-magnitude atoms in Earth
N_nucleons        = M_E / 1.67e-27       # nucleons
N_PlanckVolumes   = (4/3 * np.pi * R_E**3) / L_P**3  # Planck-cells in Earth

# --- Consumption: take gravitational force as the "impulse rate" ---
F_grav = G * M_SUN * M_E / R_ORBIT**2    # N (= kg m / s^2)
deposits_per_sec = F_grav / p_P
deposits_per_Ptick = deposits_per_sec * t_P

# --- Connector count reaching Earth ---
# Assume each connector occupies one Planck-cell of Earth's cross-section.
# Total cross-section = pi * R_E^2
earth_cross_sec = np.pi * R_E**2
connector_cells = earth_cross_sec / L_P**2

# Full sky at Earth's orbital radius:
sky_area_at_orbit = 4 * np.pi * R_ORBIT**2
sky_cells = sky_area_at_orbit / L_P**2
fraction_intercepted = earth_cross_sec / sky_area_at_orbit

# Deposit rate per connector = (deposits/tick arriving at Earth) /
#                              (number of connectors carrying them)
rate_per_connector_per_tick = deposits_per_Ptick / connector_cells
ticks_between_deposits_per_connector = 1 / rate_per_connector_per_tick if rate_per_connector_per_tick > 0 else float('inf')

# --- Report ---
def sci(x):
    return f"{x:.3e}"

print("=" * 68)
print("Earth at the tick-frame substrate scale")
print("=" * 68)
print()
print("Base units (Planck):")
print(f"  1 tick  = 1 t_P      = {sci(t_P)} s")
print(f"  1 node  = 1 m_P      = {sci(m_P)} kg")
print(f"  1 hop   = 1 L_P      = {sci(L_P)} m")
print(f"  1 deposit impulse    = {sci(p_P)} kg*m/s")
print()

print("Earth (M_E = 5.97e24 kg, R_E = 6371 km):")
print(f"  mass as Planck-mass nodes        = {sci(N_nodes_PlanckMass)}")
print(f"  mass as atoms                    = {sci(N_atoms)}")
print(f"  mass as nucleons                 = {sci(N_nucleons)}")
print(f"  volume in Planck-cells           = {sci(N_PlanckVolumes)}")
print()

print("Consumption from the Sun (gravitational force interpreted as")
print("impulse arrival rate, 1 deposit = 1 Planck impulse):")
print(f"  gravitational force on Earth     = {sci(F_grav)} N")
print(f"  deposits per second              = {sci(deposits_per_sec)}")
print(f"  deposits per Planck tick         = {sci(deposits_per_Ptick)}")
print(f"  Planck ticks between deposits    = {sci(1/deposits_per_Ptick)}")
print()

print("Connectors reaching Earth (Planck cells across Earth's disk at 1 AU):")
print(f"  Earth cross-section              = {sci(earth_cross_sec)} m^2")
print(f"  connector count                  = {sci(connector_cells)}")
print(f"  (compare: full sky at Earth)     = {sci(sky_cells)} cells")
print(f"  fraction of sun's emission Earth intercepts")
print(f"                                   = {sci(fraction_intercepted)}")
print()

print("Per-connector activity:")
print(f"  deposits per connector per tick  = {sci(rate_per_connector_per_tick)}")
print(f"  Planck ticks per deposit per conn= {sci(ticks_between_deposits_per_connector)}")
print(f"  (in seconds)                     = {sci(ticks_between_deposits_per_connector * t_P)}")
print()

# --- Ratios the user might want ---
print("Scale ratios:")
print(f"  deposits / renewal (if renewal = M per tick):")
print(f"    deposits per tick               = {sci(deposits_per_Ptick)}")
print(f"    nodes to renew per tick (m_P)   = {sci(N_nodes_PlanckMass)}")
print(f"    ratio consumed / renewal         = {sci(deposits_per_Ptick / N_nodes_PlanckMass)}")
print()
print("  The sun's contribution to Earth's total 'tick budget' is")
print(f"  about {deposits_per_Ptick / N_nodes_PlanckMass:.1e} of Earth's renewal demand.")
print("  Essentially zero. Renewal cannot be paid from the star.")
print()

# --- Consumption as gravitational acceleration ---
g_earth_at_sun = F_grav / M_E
print("Sanity:")
print(f"  Earth's gravitational acceleration at 1 AU = {g_earth_at_sun:.3e} m/s^2")
print(f"  (this IS our 'consumption per unit mass')")
