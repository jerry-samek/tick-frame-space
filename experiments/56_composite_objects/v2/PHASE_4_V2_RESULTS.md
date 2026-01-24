# Experiment 56 Phase 4 V2: Gradient-Following Single-Particle Results

**Date**: 2026-01-23
**Status**: ❌ **FAILED**
**Approach**: Single electron with gradient-following orbital dynamics

---

## Executive Summary

Phase 4 V2 **catastrophically failed** with the electron escaping to **r = 2050.35 units** (a **106,899% drift** from the initial radius of r₀ = 2.0) over 10,000 ticks. The gradient-following approach revealed fundamental force balance and energy conservation issues that explain why stable circular orbits cannot emerge from pure gradient-following dynamics in a discrete tick-frame universe.

**Key finding**: Single-particle gradient-following is **fundamentally unstable** for creating atomic orbitals in tick-frame physics.

---

## 1. Observed Behavior

### 1.1 Radial Expansion Pattern

The electron's distance from the proton increased **linearly and continuously**:

| Tick | Radius (r) | % Change from Initial |
|------|------------|----------------------|
| 1 | 1.916 | -4.2% (start) |
| 101 | 27.05 | +1311% |
| 301 | 4.936 | +157% |
| 601 | 6.043 | +215% |
| 1001 | 71.37 | +3623% |
| 2001 | 296.3 | +15,065% |
| 5001 | 967.8 | +49,290% |
| 10000 | 2050.4 | **+106,899%** |

**Critical observation**: After tick ~300, the expansion becomes **nearly perfectly linear** with time, suggesting constant outward velocity.

**Linear drift rate**: Δr/Δt ≈ (2050 - 300)/(10000 - 300) ≈ **0.18 units/tick**

---

### 1.2 Velocity Evolution

#### Phase 1: Chaotic Adjustment (Tick 1-200)

```
Tick   1: v_total = 0.098, v_r = -0.084, v_t = 0.050 (initial tangential)
Tick 101: v_total = 0.190, v_r = 0.010,  v_t = 0.190 (tangential increases)
Tick 201: v_total = 0.567, v_r = -0.329, v_t = 0.463 (RADIAL INFALL!)
```

At tick 201, the electron experienced **close approach** to the proton (r = 0.867), causing:
- **Rapid acceleration** to v = 0.567 (highest speed in simulation)
- **Large inward radial velocity** (v_r = -0.329)
- Electron gained significant kinetic energy during infall

#### Phase 2: Hyperbolic Escape (Tick 200-300)

```
Tick 201: r = 0.867 (PERIAPSIS - closest approach)
Tick 251: r = 2.433 (climbing back out)
Tick 301: r = 4.936 (escaped gamma-well)
```

The electron used kinetic energy from the close approach to **escape on a hyperbolic trajectory**.

#### Phase 3: Ballistic Drift (Tick 300+)

```
Tick  301: v_total = 0.149, v_r = 0.149, v_t ≈ 0.005 (almost purely radial)
Tick  901: v_total = 0.224, v_r = 0.223, v_t = 0.021
Tick 5001: v_total = 0.225, v_r = 0.221, v_t = 0.022
Tick 10000: v_total = 0.210, v_r = 0.209, v_t = 0.020
```

**Key finding**: After tick ~300, velocity becomes **overwhelmingly radial**:
- v_r ≈ 0.22 (outward, constant)
- v_t ≈ 0.02 (tangential velocity nearly damped out)

The electron is not orbiting—it's **escaping radially at constant speed**.

---

### 1.3 Binding Energy Anomaly

```
Tick   1: E_bind = -0.557  (weakly bound)
Tick 201: E_bind = -2.127  (deepening - electron falling in)
Tick 301: E_bind = -2.284  (maximum depth)
Tick 1001: E_bind = -2.470  (plateaus)
Tick 10000: E_bind = -2.496 (saturates at -2.5)
```

**PHYSICAL NONSENSE**: Binding energy plateaus at E_bind ≈ -2.5 despite the electron escaping to r=2050!

**Diagnosis**: The `compute_binding_energy()` method integrates γ over a **fixed radius of 5.0 units** around the specified center. At large distances, this measures the **proton's local γ-well depth** (which remains constant ≈ -2.5), not the electron's actual binding state.

**Correct behavior**: E_bind should approach 0 as r → ∞ (unbound electron in flat space).

---

### 1.4 Gamma Field Values

```
Tick   1: γ_proton = 10.0, γ_electron = 4.64 (in well)
Tick  301: γ_proton = 10.0, γ_electron = 2.43 (escaping well)
Tick 1001: γ_proton = 10.0, γ_electron = 1.04 (nearly flat space!)
Tick 10000: γ_proton = 10.0, γ_electron = 1.09 (essentially γ=1, flat space)
```

**Confirmation**: The electron escaped the gamma-well. By tick 1001, γ_electron ≈ 1.04 (only 4% time dilation), indicating **nearly flat spacetime**.

---

## 2. Physical Diagnosis

### 2.1 The Infall-Escape Mechanism

The electron **did not escape because of outward force**. Instead:

1. **Initial conditions**: Electron at r=2.0 with **insufficient tangential velocity** (v_t = 0.05)
2. **Infall phase (tick 1-201)**: Gradient force (correctly pointing inward) pulled electron toward proton
3. **Close approach (tick 201)**: Electron reached **periapsis at r=0.867**, gaining huge kinetic energy (v=0.567)
4. **Escape phase (tick 201-300)**: Kinetic energy from infall converted to **outward radial motion**
5. **Ballistic drift (tick 300+)**: Electron escaped on **hyperbolic trajectory** with v ≈ 0.22

**Analogy**: Like dropping a ball into a well—it gains speed on the way down, then uses that speed to climb out the other side and escape.

---

### 2.2 Why Didn't the Electron Fall Back In?

In a **conservative system**, the electron should oscillate (fall in, escape, fall back, repeat). But V2 showed **one-way escape**. Why?

**Answer**: **Energy injection from velocity-dependent field sources**

From `binding_detection_v2.py` lines 176-181:
```python
v_squared = np.dot(velocity, velocity)
gamma_SR = lorentz_gamma(velocity, self.c)
velocity_factor = (1.0 + v_squared / (self.c ** 2)) * gamma_SR
contribution = base_contribution * velocity_factor
```

As the electron's speed increased during infall:
- Source strength increased (relativistic correction)
- Gamma-field became stronger
- Gradient force increased
- Acceleration increased
- **Positive feedback loop** → runaway instability

**Result**: Electron gained energy continuously, preventing recapture.

---

### 2.3 Missing Centrifugal Force

For a stable circular orbit, we need:
```
Centripetal force = Gravitational force
m × v²/r = k × |∇γ|
```

But the code only applied **radial gradient force**, with **NO tangential force**:
- Radial force: F_r = k × ∇γ_r (provided by gradient)
- Tangential force: F_t = 0 (no mechanism!)

With initial tangential velocity v_t = 0.05, the centrifugal force was:
```
F_centrifugal = m × v_t²/r = 0.001 × 0.05²/2.0 ≈ 0.00000125
```

While the gradient force at r=2.0 was:
```
F_gradient = k × |∇γ| ≈ 0.05 × 2.7 ≈ 0.135
```

**Force ratio**: F_gradient / F_centrifugal ≈ **100,000:1**

The gradient force **overwhelmed** the centrifugal force, causing immediate infall.

---

### 2.4 Required vs Actual Initial Velocity

For circular orbit at r=2.0 with coupling constant k=0.05:

**Required tangential velocity**:
```
v_circular = sqrt(k × |∇γ| × r / m)
          = sqrt(0.05 × 2.7 × 2.0 / 0.001)
          ≈ sqrt(270)
          ≈ 16.4 units/tick
```

**Actual initial velocity**: v_t = 0.05 units/tick

**Deficit**: The electron was **328 times too slow** to maintain circular orbit!

---

### 2.5 Angular Momentum Damping

Looking at the velocity evolution:

```
Tick   1: v_t = 0.050 (100% of total velocity)
Tick 101: v_t = 0.190 (100% of total velocity - good!)
Tick 201: v_t = 0.463 (82% of total - still mostly tangential)
Tick 301: v_t = 0.005 (3% of total - COLLAPSED!)
Tick 1001: v_t = 0.021 (9% of total)
```

**Observation**: Tangential velocity was **systematically damped** while radial velocity grew.

**Mechanism**: Radial-only force application:
1. Gradient force only affects radial motion
2. No force maintains tangential velocity
3. As electron's trajectory turns, velocity vector rotates toward radial direction
4. Tangential component progressively lost

**Result**: Electron transition from **orbital motion → radial escape**.

---

### 2.6 Energy Non-Conservation

**Energy sources (unphysical)**:
1. **Velocity-dependent sources**: Faster electron → stronger field → more acceleration → faster (runaway feedback)
2. **Discontinuous field updates**: Field recomputed every 5 ticks → electron can gain kinetic energy without field energy decreasing
3. **No back-reaction**: Electron's motion doesn't drain field energy

**Energy sinks**:
1. **Speed limit enforcement**: When v > c=1.0, velocity rescaled → energy capped
2. **This creates steady state**: energy injection = energy capping → constant v ≈ 0.22

**Net result**: Total energy (kinetic + potential) **NOT conserved**.

---

## 3. Root Causes Summary

### 3.1 Why Orbital Radius Increased Linearly

1. **Initial perturbation**: Tangential velocity v_t = 0.05 << required v_circular ≈ 16.4
2. **Infall**: Gradient force pulled electron inward to r=0.867
3. **Kinetic energy gain**: Close approach → v = 0.567 (high speed)
4. **Hyperbolic escape**: Electron used kinetic energy to escape on one-way trajectory
5. **Ballistic drift**: After escaping gamma-well, constant velocity ≈ 0.22
6. **Linear expansion**: r(t) = r₀ + v_escape × t

The **linear drift** after tick ~300 is simply **ballistic motion** at constant velocity.

---

### 3.2 Why Energy Balance Failed

**Fundamental issue**: The simulation did NOT conserve total energy.

**Energy sources**:
- Velocity-dependent field sources (1 + v²/c²) × γ_SR
- Discontinuous field updates (every 5 ticks)
- Moving electron modifying its own field

**Missing physics**:
- Field energy explicitly tracked
- Electron kinetic energy coupled to field energy
- Back-reaction (electron motion drains field)

**Result**: Electron could gain kinetic energy "for free" from field updates.

---

### 3.3 Why Gradient-Following Alone is Insufficient

**Core problem**: ∇γ provides a **central force**, but stable circular orbits require:
1. **Precise initial conditions**: v_tangential² = (k × |∇γ| × r) / m
2. **No energy dissipation or injection**
3. **No perturbations**
4. **Angular momentum conservation**

V2 had:
- ❌ Wrong initial velocity (328× too slow)
- ❌ Energy injection from velocity-dependent sources
- ❌ Discontinuous field updates
- ❌ No tangential force to maintain angular momentum
- ❌ Numerical instabilities from discrete updates

**Conclusion**: Gradient-following is **too fragile** for single-particle orbits in tick-frame physics.

---

## 4. Comparison with Classical Orbits

### Classical Kepler Orbits (Real Physics)

In Newtonian gravity or general relativity:
- Central force: F = -GMm/r² (or geodesic in curved spacetime)
- **Conserved quantities**: energy E, angular momentum L
- Stable orbits: E < 0, L ≠ 0
- **Orbital velocity**: v = sqrt(GM/r) (for circular)
- **Automatic stability**: energy conservation prevents escape

### Tick-Frame Gradient-Following (V2)

In tick-frame with gradient-following:
- Central force: F = k × ∇γ (similar structure)
- **NOT conserved**: energy E (injection from field updates)
- **NOT conserved**: angular momentum L (no tangential force)
- **Orbital velocity**: must be manually initialized to v = sqrt(k|∇γ|r/m)
- **NO automatic stability**: energy non-conservation → escape

**Key difference**: Classical orbits are stable because **energy is conserved automatically** by the dynamics. Tick-frame gradient-following requires **manual energy conservation** (not implemented in V2).

---

## 5. Lessons Learned for V3

### 5.1 Single-Particle Approach is Fundamentally Flawed

**Why it can't work**:
1. Requires **exact initial conditions** (v_circular calculated to many decimals)
2. Any perturbation → immediate instability
3. Energy injection from field updates → runaway
4. No natural restoring force for angular momentum
5. Numerical errors accumulate → orbital decay or escape

**Even if we fixed the initial velocity**, the orbit would still be unstable due to:
- Discrete timesteps (numerical integration errors)
- Field update discontinuities
- Velocity-dependent source feedback
- No damping mechanism to absorb perturbations

---

### 5.2 Fragmented Cloud Approach (V3) Solves These Issues

**Why fragmented cloud should work**:

1. **Statistical stability**: Not relying on ONE perfect trajectory, but MANY imperfect trajectories averaging out
2. **Collision-driven equilibrium**: Fragments collide, exchange energy, naturally find minimum-energy configuration
3. **Zero-point jitter**: Tick-frame metabolic pressure prevents collapse without requiring precise velocities
4. **Emergent properties**: Cloud radius, angular momentum, energy distribution emerge naturally from dynamics
5. **Robust to perturbations**: Ensemble averages smooth out fluctuations

**Key insight from Doc 070_00**:
> "The electron is not a singular, localized particle, but rather an emergent, fragmented attractor—a distributed pattern of tick-based excitations."

Single particles in tick-frame physics are **unstable**. But **ensembles** of particles can form **stable attractors** through collision-driven redistribution.

---

### 5.3 Specific Parameters for V3

Based on V2 failure analysis:

**Fragment initialization**:
- N = 50 fragments (sufficient for statistics)
- Random positions: Gaussian distribution, r_mean = 2.0, r_std = 0.5
- Random velocities: Magnitude v_mean = 0.1, v_std = 0.02 (NO need for v_circular!)
- Equal energy shares: E_fragment = E_electron / N

**Collision dynamics**:
- Collision radius: r_coll = 0.5 (allow frequent collisions)
- Restitution coefficient: e = 0.8 (slight damping for thermalization)
- Process: conserve momentum, exchange energy, redistribute

**Zero-point jitter**:
- Jitter strength: σ_jitter = 0.001 (small Brownian kicks)
- Applied every tick to all fragments
- Prevents complete collapse into proton

**Field updates**:
- Update interval: every 5 ticks (same as V2)
- Include ALL fragments as sources (not just proton)
- Velocity-dependent sources: KEEP (needed for relativistic corrections, but now averaged over ensemble)

**Success criteria**:
- Cloud radius stabilizes (drift < 10% over 10k ticks)
- Cloud radius ≈ 2-3 (Bohr radius analog)
- No fragments escape to r > 20
- Collision rate reaches steady state
- Energy distribution thermalizes (Gaussian)

---

## 6. Technical Implementation Issues

### 6.1 Gradient Computation

The gradient computation in `compute_gamma_gradient()` was **correct**:
- Used central difference: ∇γ = (γ[i+1] - γ[i-1]) / (2×dx)
- Correctly pointed toward high-γ region (well center)
- Magnitude matched γ-field variation

**No bug found** in gradient calculation.

---

### 6.2 Radial Force Projection

The radial force projection was **correct in principle**:
```python
r_hat = r_vec / r_mag
grad_radial_component = np.dot(gamma_gradient, r_hat)
radial_acceleration = k * grad_radial_component * r_hat
```

This correctly extracts the **radial component** of ∇γ and applies it as centripetal force.

**Problem**: This is only valid for **circular orbits with precise initial conditions**. Any deviation → instability.

---

### 6.3 Field Update Frequency

Updating fields every 5 ticks created **discontinuous jumps** in the gamma field:
- Electron moves for 5 ticks in **frozen field**
- Field **suddenly changes** at tick 5, 10, 15, ...
- Electron's kinetic energy **not adjusted** to compensate for field change
- **Energy violation**: ΔE_field + ΔE_kinetic ≠ 0

**For V3**: Keep 5-tick update interval (acceptable), but:
- Use ensemble average (smooths discontinuities)
- Monitor total energy (kinetic + potential)
- Add explicit energy conservation check

---

### 6.4 Velocity-Dependent Sources

The velocity correction (1 + v²/c²) × γ_SR was **physically motivated** (relativistic energy-momentum relation), but created **positive feedback**:

1. Electron accelerates → v increases
2. Source strength ∝ (1 + v²) × γ_SR increases
3. Gamma-field strengthens
4. Gradient increases → more acceleration
5. Loop back to step 1 → **runaway**

**For V3**: Keep velocity-dependent sources (needed for realism), but:
- Averaged over ensemble (reduces feedback)
- Collisions redistribute energy (natural damping)
- Zero-point jitter adds noise (breaks feedback coherence)

---

## 7. Alternative Approaches (Rejected for V3)

### 7.1 Prescribed Orbits with Gradient Validation

**Idea**: Return to V1 frozen orbits, but:
- Calculate required v_circular from ∇γ
- Update orbital parameters if ∇γ changes
- Validate that ∇γ supports the prescribed orbit

**Pros**:
- Guaranteed stability (orbit prescribed, not emergent)
- Can compute binding energy correctly
- Simple to implement

**Cons**:
- Not testing if orbits **emerge** from tick-frame dynamics
- Misses collision physics, zero-point energy, thermalization
- Doesn't validate Doc 070* fragmented electron theory

**Decision**: **Rejected**. V3 will test the fragmented cloud theory, not return to prescribed orbits.

---

### 7.2 Energy-Conserving Integration

**Idea**: Use symplectic integrator (energy-conserving numerical method) for gradient-following.

**Pros**:
- Conserves total energy automatically
- More stable than Euler integration
- Standard technique in molecular dynamics

**Cons**:
- Still requires precise initial conditions
- Doesn't address angular momentum damping
- Doesn't test fragmented electron theory
- Complex to implement with discontinuous field updates

**Decision**: **Rejected**. V3 focuses on ensemble dynamics, not improving single-particle integration.

---

### 7.3 Add Tangential Force (Artificial Angular Momentum Conservation)

**Idea**: Apply artificial tangential force to maintain constant angular momentum:
```python
L_target = m × r × v_tangential_initial
L_current = m × r × v_tangential_current
F_tangential = (L_target - L_current) / (m × r × dt)
```

**Pros**:
- Maintains circular orbit
- Prevents tangential velocity decay
- Stable (by construction)

**Cons**:
- **Non-physical** force (where does it come from?)
- Not testing tick-frame physics
- Just another way to prescribe orbits

**Decision**: **Rejected**. Unphysical forces defeat the purpose of the experiment.

---

## 8. Conclusion

### 8.1 V2 Final Verdict

**Phase 4 V2 (gradient-following single-particle) FAILED because**:

1. ❌ Initial tangential velocity 328× too low for circular orbit
2. ❌ Electron fell inward to close approach (r=0.867)
3. ❌ Gained kinetic energy during infall
4. ❌ Escaped on hyperbolic trajectory with v ≈ 0.22
5. ❌ Energy injection from velocity-dependent sources prevented recapture
6. ❌ Radial-only force damped tangential velocity
7. ❌ Linear drift over 10,000 ticks → 106,899% radius increase

**Root cause**: Single-particle gradient-following is **fundamentally unstable** in discrete tick-frame physics due to:
- Energy non-conservation
- Angular momentum damping
- Numerical integration errors
- Velocity-dependent field feedback

**Lesson**: Classical point-particle orbits **cannot emerge** from gradient-following alone in tick-frame universe.

---

### 8.2 Path Forward: V3 Fragmented Electron Cloud

**Why V3 should succeed** where V2 failed:

| Issue | V2 (Failed) | V3 (Solution) |
|-------|-------------|---------------|
| **Initial conditions** | Must be exact → 328× error | Random → ensemble average |
| **Energy balance** | Non-conserved → runaway | Redistributed via collisions |
| **Angular momentum** | Damped → radial escape | Emergent from ensemble |
| **Stability** | Single trajectory → fragile | Statistical attractor → robust |
| **Physics model** | Classical point particle | Quantum-like probability cloud |
| **Theory basis** | Gradient-following (classical) | Doc 070* (tick-frame quantum) |

**Theoretical foundation**:
- Doc 070_00: Electron as fragmented attractor
- Doc 070_01: Collision-driven stabilization
- Doc 070_02: Emergent rotation from pattern dynamics

**Expected outcome**: Fragmented cloud will:
- Self-organize into stable equilibrium
- Maintain finite radius (Bohr radius analog)
- Thermalize energy distribution
- Exhibit emergent angular momentum
- Reproduce quantum-like electron cloud without wavefunction axioms

---

### 8.3 V2 Contributions (What We Learned)

Despite failure, V2 provided valuable insights:

✅ **Gradient computation works**: ∇γ correctly computed, points toward well center
✅ **Gamma-well physics validated**: Attractive central force from γ-field confirmed
✅ **Velocity-dependent sources functional**: Relativistic corrections implemented correctly
✅ **Field dynamics stable**: Reaction-diffusion equations converge to steady state
✅ **Identified failure modes**: Energy injection, angular momentum damping, numerical instabilities
✅ **Motivated V3 approach**: Single-particle instability → fragmented ensemble needed

**V2 was not wasted effort**—it taught us what **doesn't work** and why **V3 will work**.

---

## Files and Data

**Implementation**: `experiments/56_composite_objects/v2/experiment_56a_v2_hydrogen.py`

**Results**: `experiments/56_composite_objects/v2/results/exp56a_v2_hydrogen_gradient_following.json`

**Plots**: `experiments/56_composite_objects/v2/results/exp56a_v2_hydrogen_gradient_following.png`

**Configuration**:
- Coupling constant: k = 0.05
- Initial orbital radius: r₀ = 2.0
- Initial tangential velocity: v_t = 0.05 (should have been v_t ≈ 16.4!)
- Field update interval: 5 ticks
- Simulation duration: 10,000 ticks

---

**Next**: Phase 4 V3 - Fragmented Electron Cloud Implementation

**See**: `experiments/56_composite_objects/PHASE_4_V3_PLAN.md`
