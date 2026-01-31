# V8: Particle Accelerator Experiments

**Status**: IN PROGRESS
**Date**: 2026-01-30
**Based on**: V6 stable cloud + V7 motion dynamics (complete)

---

## Overview

V8 will study **non-equilibrium collisions** by firing projectiles at the stabilized V6 "atom". This mimics real particle accelerator physics with perfect control and measurement.

**Key idea: "Shoot the Stabilized Atom"**

Unlike V6 (equilibrium thermalization), V8 studies:
- High-speed projectiles fired at the stable cloud
- Variable energies: thermal to relativistic-like
- Precise targeting: impact parameter, angle, timing
- Observation: scattering, excitation, ionization, fragmentation

---

## Advantages of Tick-Frame Simulation

Real particle accelerators face limitations:
- **Uncertainty**: Cannot perfectly control collision parameters
- **Detection**: Limited measurement precision
- **Repeatability**: Statistical ensembles required

Tick-frame simulation enables:
- **Perfect control**: Exact projectile position, velocity, timing
- **Perfect measurement**: Track every fragment at every tick
- **Perfect repeatability**: Identical initial conditions, deterministic evolution
- **Systematic scanning**: Exhaustive parameter space testing

---

## Proposed Experiments

### 1. High-Speed vs Low-Speed Projectiles

**Low-speed** (thermal):
- Velocity ~ 0.01-0.05 (similar to cloud fragments)
- Expected: Elastic scattering, slight excitation

**High-speed** (energetic):
- Velocity ~ 0.5-1.0 (10-100× cloud velocity)
- Expected: Ionization, fragmentation, deep penetration

### 2. Variable Projectile Masses

**Light projectiles** (electron-like):
- Expected: Elastic scattering, small momentum transfer

**Heavy projectiles** (alpha/proton-like):
- Expected: Large momentum transfer, recoil, fragmentation

### 3. Precise Targeting

**Impact parameter scanning**:
- b = 0: Head-on collision
- b = 0.5-1.0: Grazing collision
- b > 2.0: Miss

**Radial targeting**:
- Cloud center (r = 0)
- Shell peaks (r ≈ 0.9, 1.5, 1.9 from V4 quantization)
- Cloud edge (r ≈ 2.5-3.0)

---

## Observables

### Scattering
- Scattering angle θ distribution (dσ/dΩ)
- Energy transfer ΔE (inelastic vs elastic)
- Fragment count change Δn

### Cloud Response
- Excitation level and relaxation time
- Ionization threshold (minimum energy for ejection)
- Structural damage and recovery

---

## Comparison with Real Physics

If successful, V8 validates:
- Collision cross-sections emerge from tick-frame dynamics
- Energy thresholds match quantum predictions
- Scattering distributions follow classical/quantum formulas

---

## Prerequisites

1. **V6 Complete**: Stable confined cloud (DONE)
2. **V7 Complete**: Motion dynamics characterized (PENDING)
   - Need to understand baseline motion before perturbing with projectiles

---

## File Structure

```
v8/
├── README.md                    # This file
├── config_v8.py                 # Accelerator + gamma well configuration
├── projectile.py                # Projectile with gamma well support
├── gamma_wells.py               # Multiple moving gamma wells (NEW)
├── experiment_accelerator.py    # Main experiment runner
├── RESULTS_SUMMARY.md           # Detailed results analysis
└── results/                     # JSON output files
```

---

## Moving Gamma Wells (NEW)

V8 now supports **projectiles carrying their own gamma wells** that move with them and superimpose with the target's well:

```python
# Configuration
target_gamma_k = 50.0      # Static well at grid center
projectile_gamma_k = 20.0  # Moving well with projectile

# Total field at any point:
# γ(x,y) = 1.0 + k_target/r_target² + k_proj/r_proj²
```

**Key finding**: Projectile wells retain ~20 more energy during collision than without wells, suggesting field-mediated interaction dynamics.

---

**Status**: MOVING GAMMA WELLS COMPLETE ✅
**Date**: 2026-01-30
**Finding**: Projectile gamma wells interact with cloud, affecting energy dynamics
**See**: RESULTS_SUMMARY.md for analysis
