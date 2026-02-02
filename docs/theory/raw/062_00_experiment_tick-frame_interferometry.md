# Tick-Frame Interferometry: Direct Phase Measurement in Discrete Spacetime

**Document 062 - Experimental Framework for Wave Interference**
**Status**: Draft 1 (Theory Complete, Implementation Pending)
**Author**: Tom
**Date**: January 2026
**Purpose**: Define theoretical framework and experimental design for interferometry in discrete tick-frame spacetime with Planck-scale precision

---

## Executive Summary

This document establishes the theoretical foundation for **interferometry experiments in tick-frame physics**, leveraging validated discrete wave mechanics (Ch7) and phase representation (Exp #55) to demonstrate:

1. **Wave interference in discrete spacetime** (validating Ch7 dispersion relation)
2. **Direct phase measurement without wavefunction collapse** (impossible in quantum mechanics)
3. **Temporal vs spatial interference separation** (unique to tick-frame)
4. **Planck-scale precision** (t_planck ≈ 5.39×10⁻⁴⁴ s resolution)

**Key Advantage**: Tick-frame interferometry can measure phase at every tick without disturbing the wave, providing experimental transparency impossible in real laboratories due to the quantum measurement problem.

---

## 1. Theoretical Foundation

### 1.1 Validated Components (Prerequisites)

**From Chapter 7 (Physical Formalization)**:
- ✅ Discrete wave equation: `A(n+1,i) = 2×A(n,i) - A(n-1,i) + [A(n,i+1) - 2×A(n,i) + A(n,i-1)]`
- ✅ Dispersion relation: `ω(k) = (2/Δt) × sin(k×Δx/2)` (differs from continuous ω = ck)
- ✅ Nyquist limit: `f_max = 1/(2×t_planck) ≈ 9.3×10⁴² Hz`

**From Experiment #55 (Collision Physics)**:
- ✅ Phase representation: Pattern structure includes phase φ ∈ [0, 2π]
- ✅ Phase measurement: Pattern overlap computes cos(Δφ) directly
- ✅ Phase-sensitive interactions: Collision energy depends on phase alignment

**From Document 051 (Photon Model)**:
- ✅ Photon definition: Periodic imprint in tick-stream (not a particle)
- ✅ Wavelength λ = period in ticks
- ✅ Frequency ν = 1/λ ticks⁻¹
- ✅ Propagation speed: Always 1 spatial quantum/tick (c = constant)

### 1.2 Wave Packet Representation

**Gaussian Wave Packet**:

```
ψ(x,t) = A₀ × exp(-(x-x₀-vt)²/(2σ²)) × exp(i(kx - ωt + φ₀))
```

Where:
- **A₀**: Amplitude (energy density)
- **x₀**: Initial center position
- **σ**: Spatial width (coherence length)
- **k**: Wave number (k = 2π/λ)
- **ω**: Angular frequency (ω = 2πν)
- **φ₀**: Initial phase
- **v**: Group velocity (v_g = dω/dk)

**Discrete Representation**:

```python
A[n, i] = A0 * exp(-(i - i0 - v*n)**2 / (2*sigma**2)) * exp(1j * (k*i - omega*n + phi0))
```

Where:
- **n**: Tick index (time)
- **i**: Cell index (space)
- **Δx**: Cell size (1 spatial quantum = l_planck)
- **Δt**: Tick duration (1 tick = t_planck)

### 1.3 Dispersion in Discrete Spacetime

**Continuous Spacetime** (standard QM):
```
ω = c × k  (linear, no dispersion)
v_phase = ω/k = c  (constant for all wavelengths)
v_group = dω/dk = c  (constant)
```

**Discrete Spacetime** (tick-frame, Ch7 §4):
```
ω(k) = (2/Δt) × sin(k×Δx/2)  (nonlinear, dispersive!)
v_phase = ω/k = (2/k×Δt) × sin(k×Δx/2)
v_group = dω/dk = (Δx/Δt) × cos(k×Δx/2) = c × cos(k×Δx/2)
```

**Key Predictions**:
1. **Low k (long wavelengths)**: v_group ≈ c (no dispersion, matches continuous)
2. **High k (short wavelengths)**: v_group < c (dispersive, unique to discrete)
3. **Nyquist limit k_max = π/Δx**: v_group → 0 (standing wave)

**Experimental Test**: Create wave packet with varying k, measure arrival time vs wavelength.

---

## 2. Interferometry Principles in Tick-Frame

### 2.1 Superposition in Deterministic Substrate

**Standard QM**: Superposition is fundamental, measurement causes collapse

**Tick-Frame**: Superposition emerges from substrate evolution, no collapse

```
If two patterns overlap at cell (i) at tick (n):
  - Pattern A: amplitude A₁, phase φ₁
  - Pattern B: amplitude A₂, phase φ₂

Combined amplitude:
  A_total = A₁ × exp(i×φ₁) + A₂ × exp(i×φ₂)

Intensity (measurable):
  I = |A_total|² = |A₁|² + |A₂|² + 2|A₁||A₂|cos(φ₂ - φ₁)

  I = I₁ + I₂ + 2√(I₁×I₂) × cos(Δφ)  ← INTERFERENCE TERM
```

**Phase Difference**:
```
Δφ = φ₂ - φ₁ = k × ΔL  (path difference in space)
     or
Δφ = Δω × Δt  (path difference in time, if frequencies differ)
```

### 2.2 Fringe Visibility

**Visibility Definition**:
```
V = (I_max - I_min) / (I_max + I_min)
```

**Ideal Interference** (perfect coherence, equal amplitudes):
```
I_max = (A₁ + A₂)² = 4A² when Δφ = 0, 2π, 4π, ...  (constructive)
I_min = (A₁ - A₂)² = 0   when Δφ = π, 3π, 5π, ...  (destructive)

V = (4A² - 0) / (4A² + 0) = 1.00  (perfect)
```

**Real Experiment** (imperfect coherence, unequal amplitudes):
```
V < 1.0

Degradation factors:
  - Partial coherence (σ_coherence < path difference)
  - Amplitude mismatch (A₁ ≠ A₂)
  - Phase noise (dispersion, numerical errors)
```

**Validation Criterion**: V > 0.9 indicates high-quality interference

### 2.3 Unique Advantage: Direct Phase Access

**Quantum Mechanics**:
- Cannot measure phase without disturbing wavefunction
- Measurement collapses superposition
- Phase information lost after detection
- Heisenberg uncertainty: Δφ × ΔN ≥ 1

**Tick-Frame Physics**:
- ✅ Phase stored as variable in pattern: `pattern.phase`
- ✅ Reading phase doesn't modify substrate evolution
- ✅ Can measure phase at EVERY tick along BOTH paths
- ✅ Complete trajectory reconstruction possible
- ✅ No uncertainty principle at substrate level

**Experimental Capability**: "Which-path" measurement without destroying interference

```python
# At tick n, measure phase in Path B
phase_B_intermediate = pattern_B.phase  # Direct read, no collapse!

# Continue propagation to recombination point
# Interference STILL OCCURS (unlike QM, where measurement destroys it)

# At recombination:
phase_A_final = pattern_A.phase
phase_B_final = pattern_B.phase
delta_phi = phase_B_final - phase_A_final

# Predict interference:
I_predicted = I1 + I2 + 2*sqrt(I1*I2)*cos(delta_phi)
```

**This is impossible in real experiments!** Distinguishes tick-frame from quantum mechanics.

---

### 2.4 REVISED: Photon-Gamma Coupling and Which-Path (February 2026)

**Important Update**: The original claim in §2.3 has been revised based on theoretical analysis of photon-gamma field coupling. See Doc 051 §6 for full derivation.

#### The Contradiction Discovered

The original claim ("which-path without collapse") conflicts with established tick-frame theory:

| Theory Component | Implication |
|-----------------|-------------|
| Doc 051: Photons are "periodic imprints in tick-stream" | Imprints must manifest somewhere |
| Doc 065: "Light IS gamma oscillation" | Photons modify gamma field |
| Exp 56 v17: All entity actions = gamma modifications | The canvas IS gamma |

**If light IS gamma oscillation → photons modify gamma → which-path info exists in gamma field**

#### Original Claim (SUPERSEDED)

> "Which-path information can be obtained WITHOUT destroying interference"

This assumed that reading the pattern's phase variable was a passive operation with no coupling to the underlying gamma field.

#### Revised Understanding

Photons leave **gamma traces** along their path:

```
Photon passage at position x:
  γ(x) = γ_background + A_photon × oscillation

Trace decay:
  γ(x, t+Δt) = γ_background + (γ(x,t) - γ_background) × exp(-Δt/τ_decay)
```

These traces:
1. **Encode which-path information** in the gamma field
2. **Are theoretically detectable** via gamma field measurement
3. **May affect interference** through gamma-phase coupling

#### New Falsifiable Prediction

The degree of interference degradation depends on:
- **Gamma trace amplitude** (photon energy)
- **Detection sensitivity threshold**
- **Coupling strength** between gamma field and phase evolution

```
V(detection_strength) = V_max × f(E_probe / E_photon, k_coupling)
```

**Key Difference from QM**:
- QM: ANY which-path detection destroys interference immediately (complementarity)
- Tick-frame: Interference degradation is **gradual** and depends on detection strength

This produces a **continuous visibility curve** rather than a **binary collapse**:

```
Standard QM:          V = V_max if no detection, V = 0 if detected
Tick-frame (revised): V = V_max × (1 - k × detection_strength)
```

#### Experimental Test (Updated)

The original test (Phase 7 in Exp #62) validated that reading `pattern.phase` does not affect interference. This remains valid for the abstract wave mechanics layer.

The revised test requires **gamma-coupled wave mechanics**:

1. Implement gamma field that photons modify
2. Implement phase evolution dependent on local gamma: `dφ/dt = ω × γ(x,t)`
3. Implement gamma trace detection mechanism
4. Measure visibility vs detection strength
5. Compare to QM prediction (immediate collapse) vs tick-frame (gradual degradation)

See `experiments/62_interferometry/gamma_coupled_wave.py` for implementation.

---

## 3. Mach-Zehnder Interferometer Design

### 3.1 Geometry

```
Source
  ↓
  BS1 (Beam Splitter 1, 50/50)
  ├─→ Path A (transmitted) ─→ Mirror A ─→┐
  └─→ Path B (reflected 90°) ─→ Mirror B ─→ BS2 (Beam Splitter 2)
                                            ├─→ Detector 1 (transmitted)
                                            └─→ Detector 2 (reflected)
```

**Coordinates** (2D substrate):
- Source: (0, 0)
- BS1: (50, 0)
- Mirror A: (100, 0)
- Mirror B: (50, 50)
- BS2: (100, 50)
- Detector 1: (150, 50) [transmitted from BS2]
- Detector 2: (100, 100) [reflected from BS2]

**Path Lengths**:
- Path A: 50 cells (source→BS1) + 50 cells (BS1→Mirror A) + 71 cells (Mirror A→BS2) = 171 cells
- Path B: 50 cells (source→BS1) + 71 cells (BS1→Mirror B) + 71 cells (Mirror B→BS2) = 192 cells
- **Path difference**: ΔL = 192 - 171 = 21 cells (adjustable by moving mirrors)

**Phase Difference**:
```
Δφ = k × ΔL = (2π/λ) × 21

For λ = 100 cells:
Δφ = (2π/100) × 21 = 0.42π radians

For λ/2 path difference (destructive):
ΔL = λ/2 = 50 cells → Δφ = π
```

### 3.2 Beam Splitter Physics

**Definition**: Partially transmitting/reflecting boundary at E_max interface

**Transmission/Reflection Coefficients**:
```
At interface between E_max_low and E_max_high:

Transmission: T = 2×√(E_low/E_high) / (1 + E_low/E_high)
Reflection:   R = (1 - E_low/E_high) / (1 + E_low/E_high)

Energy conservation: T + R = 1
```

**For 50/50 Beam Splitter**:
```
Set E_low/E_high = 1/3 (specific ratio)
→ T = 2×√(1/3) / (4/3) = 0.866 / 1.333 ≈ 0.65
→ R = (2/3) / (4/3) = 0.5

Actually, for exactly 50/50:
Use specialized boundary condition (not simple E_max interface)
T = R = 0.5 (50% each path)
```

**Phase Preservation**:
- Transmitted path: No phase shift (φ → φ)
- Reflected path: Possible π/2 shift (φ → φ + π/2, depending on boundary condition)
- **Convention**: Assume NO phase shift for simplicity (can be calibrated out)

**Implementation**:
```python
def beam_splitter_50_50(incident_amplitude, incident_phase):
    """
    Split incident wave into transmitted and reflected paths.
    """
    # Amplitudes (energy conservation)
    A_transmitted = incident_amplitude / sqrt(2)  # 50% intensity
    A_reflected = incident_amplitude / sqrt(2)    # 50% intensity

    # Phases (no shift in this model)
    phi_transmitted = incident_phase
    phi_reflected = incident_phase

    return (A_transmitted, phi_transmitted), (A_reflected, phi_reflected)
```

### 3.3 Mirror Physics

**Definition**: Total reflection boundary (E_max → ∞, impenetrable cell)

**Reflection Law**:
```
Incident: velocity v⃗ = (vx, vy)
Normal: n⃗ (perpendicular to mirror surface)

Reflected: v⃗' = v⃗ - 2(v⃗·n⃗)n⃗  (elastic reflection)
```

**For vertical mirror** (normal n⃗ = (1, 0)):
```
Incident: (vx, vy)
Reflected: (-vx, vy)  (x-component reverses, y-component unchanged)
```

**For horizontal mirror** (normal n⃗ = (0, 1)):
```
Incident: (vx, vy)
Reflected: (vx, -vy)  (y-component reverses, x-component unchanged)
```

**Phase Shift**:
```
Hard boundary (E_max → ∞): Phase shift π (amplitude flips sign)
Soft boundary (finite E_max): No phase shift

Convention: Use soft boundary (no π shift)
```

**Implementation**:
```python
def mirror_reflection(velocity, normal):
    """
    Elastic reflection from mirror with normal vector.
    """
    # Reflect velocity
    v_reflected = velocity - 2 * np.dot(velocity, normal) * normal

    # Phase shift (soft boundary, no shift)
    phase_shift = 0.0  # or π for hard boundary

    return v_reflected, phase_shift
```

### 3.4 Path Synchronization

**Critical Requirement**: Both paths must arrive at BS2 at SAME TICK for interference

**Path Lengths**:
```
Path A: L_A cells → requires t_A = L_A ticks (since v = 1 cell/tick)
Path B: L_B cells → requires t_B = L_B ticks
```

**Synchronization**:
```
If L_A ≠ L_B:
  - Early path waits at buffer cell before BS2
  - Both arrive at BS2 simultaneously

OR adjust geometry so L_A = L_B exactly
```

**For Phase Control** (tunable path difference):
```
Move Mirror B by Δx cells:
  - Path B increases by 2×Δx (to mirror and back)
  - Path difference: ΔL = 2×Δx
  - Phase difference: Δφ = k × 2×Δx = (4π/λ) × Δx
```

---

## 4. Experimental Tests

### 4.1 Test Suite Overview

| Test | Goal | Success Criterion |
|------|------|-------------------|
| **1** | Wave packet propagation | Maintains coherence 1000+ ticks |
| **2** | Dispersion relation | v_group = c×cos(k×Δx/2) validated |
| **3** | Nyquist aliasing | f > f_max shows aliasing |
| **4** | Two-source constructive | Δφ=0 → I=4I₀ |
| **5** | Two-source destructive | Δφ=π → I=0 |
| **6** | Variable phase difference | I ∝ (1 + cos(Δφ)) |
| **7** | Beam splitter | 50/50 split, T+R=1 |
| **8** | Mirror | Elastic reflection, phase preserved |
| **9** | Mach-Zehnder equal paths | Δφ=0 → constructive at D1 |
| **10** | Mach-Zehnder λ/2 difference | Δφ=π → destructive at D1 |
| **11** | Mach-Zehnder scan | Fringes vs ΔL, V>0.9 |
| **12** | Discrete dispersion | High-k waves slower than c |
| **13** | Direct phase measurement | Read phase without collapse |
| **14** | Temporal interference | γ-field modulation creates Δφ |

### 4.2 Test 1: Wave Packet Propagation

**Setup**:
```python
# Initialize Gaussian wave packet
lambda_0 = 100  # cells (wavelength)
k0 = 2 * pi / lambda_0
sigma = 20  # cells (width)
x0 = 500  # starting position
A0 = 1.0  # amplitude

psi[0, :] = A0 * exp(-(x - x0)**2 / (2*sigma**2)) * exp(1j * k0 * x)

# Evolve for 1000 ticks using discrete wave equation
for n in range(1000):
    psi[n+1, :] = evolve_discrete_wave(psi[n, :], psi[n-1, :])
```

**Expected**:
- Wave packet travels at v_group = c×cos(k0×Δx/2) ≈ c (for long λ)
- Width σ remains approximately constant (minimal dispersion)
- Amplitude preserved (energy conservation)

**Success Criterion**:
```
After 1000 ticks:
- Position: x = x0 + v_group × 1000 (within 5%)
- Width: σ_final ≈ σ_initial (within 10%)
- Energy: ∫|ψ|²dx = E_initial (within 1%)
```

### 4.3 Test 2: Dispersion Relation

**Setup**:
```python
# Create wave packets with different wavelengths
wavelengths = [50, 100, 200, 400, 800]  # cells
k_values = [2*pi/λ for λ in wavelengths]

for k in k_values:
    # Create packet with wave number k
    psi = create_wave_packet(k0=k, sigma=20)

    # Propagate 1000 ticks
    psi_final = evolve(psi, n_ticks=1000)

    # Measure group velocity
    x_initial = measure_center(psi[0])
    x_final = measure_center(psi_final)
    v_group_measured = (x_final - x_initial) / 1000

    # Compare to theory
    v_group_theory = c * cos(k * Delta_x / 2)
```

**Expected**:
```
Low k (long λ): v_group ≈ c (no dispersion)
High k (short λ): v_group < c (dispersive)

Plot: v_group vs k should match Ch7 prediction
```

**Success Criterion**:
```
Correlation r > 0.99 between measured and theoretical v_group
Maximum deviation < 5% for all k values
```

### 4.4 Test 6: Two-Source Variable Phase

**Setup**:
```python
# Two coherent sources at same position
x_source = 500
lambda_0 = 100
k0 = 2*pi / lambda_0

# Detector at distance L
x_detector = 1000
L = x_detector - x_source

# Vary phase difference by changing source 2 phase
for delta_phi in linspace(0, 2*pi, 100):
    # Source 1: phase = 0
    psi1 = create_source(x_source, k0, phi=0)

    # Source 2: phase = delta_phi
    psi2 = create_source(x_source, k0, phi=delta_phi)

    # Propagate both to detector
    psi1_final = evolve(psi1, ticks=L)
    psi2_final = evolve(psi2, ticks=L)

    # Measure intensity at detector
    A1 = psi1_final[x_detector]
    A2 = psi2_final[x_detector]
    I_total = |A1 + A2|**2

    # Theoretical prediction
    I_theory = I1 + I2 + 2*sqrt(I1*I2)*cos(delta_phi)
```

**Expected**:
```
I(Δφ) = I₀ × (1 + cos(Δφ))

Maximum: I_max = 2I₀ at Δφ = 0, 2π, 4π, ...
Minimum: I_min = 0   at Δφ = π, 3π, 5π, ...
```

**Success Criterion**:
```
Fit to cos² pattern: r² > 0.99
Fringe visibility: V = (I_max - I_min)/(I_max + I_min) > 0.95
```

### 4.5 Test 11: Mach-Zehnder Fringe Scan

**Setup**:
```python
# Build Mach-Zehnder with adjustable path difference
lambda_0 = 100  # cells
k0 = 2*pi / lambda_0

# Scan mirror position (vary path difference)
path_differences = linspace(0, 2*lambda_0, 200)  # 0 to 2λ

for delta_L in path_differences:
    # Set up interferometer with path difference delta_L
    interferometer = MachZehnder(
        source_wavelength=lambda_0,
        path_A_length=171,
        path_B_length=171 + delta_L
    )

    # Run experiment
    I_D1, I_D2 = interferometer.run()

    # Calculate phase difference
    delta_phi = k0 * delta_L

    # Theoretical prediction
    I_D1_theory = I0 * (1 + cos(delta_phi))
```

**Expected**:
```
I_D1(ΔL) oscillates sinusoidally with period λ
I_D2(ΔL) complementary (out of phase by π)

Constructive at ΔL = 0, λ, 2λ, ...
Destructive at ΔL = λ/2, 3λ/2, 5λ/2, ...
```

**Success Criterion**:
```
Fringe visibility V > 0.9
Period matches λ within 2%
Energy conservation: I_D1 + I_D2 = I_source (within 1%)
```

### 4.6 Test 13: Direct Phase Measurement (UNIQUE)

**Setup**:
```python
# Run Mach-Zehnder with equal paths (Δφ = 0)
interferometer = MachZehnder(path_A_length=171, path_B_length=171)

# DURING propagation, measure phase in Path B
# (This is impossible in QM - measurement would collapse wavefunction!)

intermediate_tick = 500  # halfway through
phase_B_measured = interferometer.measure_phase_in_path_B(tick=intermediate_tick)

# Continue propagation to recombination
I_D1_final = interferometer.run_to_completion()

# Check if interference still occurs
# QM: Would destroy interference (which-path information gained)
# Tick-frame: Should preserve interference (deterministic substrate)
```

**Expected (Tick-Frame)**:
```
Interference PERSISTS even after intermediate phase measurement
I_D1 = I_max (constructive, since Δφ = 0)
Fringe visibility V > 0.9 (no degradation from measurement)
```

**Success Criterion**:
```
Interference quality UNCHANGED by intermediate measurement
This PROVES tick-frame ≠ quantum mechanics
```

**Interpretation**:
- **QM**: Measuring which-path destroys interference (fundamental limit)
- **Tick-frame**: Measurement is passive read (no collapse) → interference persists
- **This is a DISTINCTIVE PREDICTION** that differs from QM!

### 4.7 Test 14: Temporal Interference (UNIQUE)

**Setup**:
```python
# Mach-Zehnder with γ-field modulation in Path B
# (Creates temporal path difference, not spatial)

# Path A: γ = 1.0 (normal time flow)
# Path B: γ = 0.8 (slowed time flow, entity takes longer)

# Even if spatial paths are EQUAL length:
# L_A = L_B = 171 cells

# Time elapsed differs:
# t_A = L_A / c = 171 ticks (γ=1.0)
# t_B = L_B / (γ×c) = 171 / 0.8 = 214 ticks (γ=0.8, slower)

# Phase accumulation:
# φ_A = ω × t_A = ω × 171
# φ_B = ω × t_B = ω × 214

# Phase difference from TIME difference:
# Δφ = ω × (t_B - t_A) = ω × 43 ticks
```

**Expected**:
```
Temporal path difference creates phase shift
Can be ISOLATED from spatial path difference
Allows testing: Is interference spatial or temporal?
```

**Success Criterion**:
```
Case 1: Equal spatial paths, different γ → Interference from temporal Δφ
Case 2: Different spatial paths, equal γ → Interference from spatial Δφ
Case 3: Both → Combined interference

This validates temporal contribution to interference
UNIQUE to tick-frame (cannot be done in standard optics)
```

---

## 5. Implementation Plan

### 5.1 Module Structure

```
experiments/62_interferometry/
├── README.md                    # Experiment overview
├── wave_mechanics.py            # Core wave packet and evolution
├── optical_components.py        # Beam splitter, mirror
├── interferometer.py            # Mach-Zehnder assembly
├── tests/
│   ├── test_wave_propagation.py     # Tests 1-3
│   ├── test_simple_interference.py  # Tests 4-6
│   ├── test_components.py           # Tests 7-8
│   ├── test_interferometer.py       # Tests 9-11
│   └── test_advanced.py             # Tests 12-14
├── analysis/
│   ├── plot_dispersion.py       # Visualize v_group vs k
│   ├── plot_fringes.py          # Interference patterns
│   └── plot_phase_measurement.py  # Direct phase access demo
└── RESULTS.md                   # Experimental findings
```

### 5.2 Core Equations (wave_mechanics.py)

**Discrete Wave Evolution**:
```python
def evolve_2d_wave(psi_n, psi_n_minus_1, dt=1.0, dx=1.0):
    """
    Evolve wave amplitude using 2D finite-difference equation.

    A(n+1,i,j) = 2×A(n,i,j) - A(n-1,i,j)
                 + (Δt/Δx)² × [A(n,i+1,j) + A(n,i-1,j)
                               + A(n,i,j+1) + A(n,i,j-1) - 4×A(n,i,j)]
    """
    c_squared = (dt / dx)**2  # Should be ≤ 1 for stability

    laplacian = (np.roll(psi_n, 1, axis=0) + np.roll(psi_n, -1, axis=0) +
                 np.roll(psi_n, 1, axis=1) + np.roll(psi_n, -1, axis=1) -
                 4 * psi_n)

    psi_n_plus_1 = 2 * psi_n - psi_n_minus_1 + c_squared * laplacian

    return psi_n_plus_1
```

**Gaussian Wave Packet Initialization**:
```python
def create_gaussian_wave_packet(x0, k0, sigma, phi0=0.0, grid_size=2000):
    """
    Create Gaussian wave packet.

    ψ(x,0) = A₀ × exp(-(x-x₀)²/(2σ²)) × exp(i(k₀x + φ₀))
    """
    x = np.arange(grid_size)

    # Gaussian envelope
    envelope = np.exp(-(x - x0)**2 / (2 * sigma**2))

    # Oscillatory carrier
    carrier = np.exp(1j * (k0 * x + phi0))

    # Combined wave packet
    psi = envelope * carrier

    # Normalize
    norm = np.sqrt(np.sum(np.abs(psi)**2))
    psi /= norm

    return psi
```

**Group Velocity Measurement**:
```python
def measure_group_velocity(psi_initial, psi_final, n_ticks):
    """
    Measure group velocity from center-of-mass motion.
    """
    # Intensity distributions
    I_initial = np.abs(psi_initial)**2
    I_final = np.abs(psi_final)**2

    # Center positions
    x = np.arange(len(psi_initial))
    x_initial = np.sum(x * I_initial) / np.sum(I_initial)
    x_final = np.sum(x * I_final) / np.sum(I_final)

    # Group velocity
    v_group = (x_final - x_initial) / n_ticks

    return v_group
```

### 5.3 Optical Components (optical_components.py)

**Beam Splitter**:
```python
class BeamSplitter:
    def __init__(self, position, transmission=0.5):
        self.position = position  # (x, y)
        self.T = transmission     # Transmission coefficient
        self.R = 1.0 - transmission  # Reflection coefficient

    def split(self, psi_incident):
        """
        Split incident wave into transmitted and reflected paths.
        """
        # Amplitudes (energy conservation)
        A_transmitted = np.sqrt(self.T) * psi_incident
        A_reflected = np.sqrt(self.R) * psi_incident

        return A_transmitted, A_reflected
```

**Mirror**:
```python
class Mirror:
    def __init__(self, position, normal):
        self.position = position  # (x, y)
        self.normal = normal / np.linalg.norm(normal)  # Unit normal

    def reflect(self, velocity):
        """
        Elastic reflection: v' = v - 2(v·n)n
        """
        v_parallel = np.dot(velocity, self.normal) * self.normal
        v_reflected = velocity - 2 * v_parallel

        return v_reflected
```

### 5.4 Mach-Zehnder Interferometer (interferometer.py)

```python
class MachZehnderInterferometer:
    def __init__(self, wavelength, path_A_length, path_B_length):
        self.wavelength = wavelength
        self.k = 2 * np.pi / wavelength

        # Components
        self.bs1 = BeamSplitter(position=(50, 0), transmission=0.5)
        self.bs2 = BeamSplitter(position=(100, 50), transmission=0.5)
        self.mirror_A = Mirror(position=(100, 0), normal=(0, 1))
        self.mirror_B = Mirror(position=(50, 50), normal=(1, 0))

        # Path lengths
        self.L_A = path_A_length
        self.L_B = path_B_length

    def run(self, psi_source):
        """
        Run full interferometer experiment.
        """
        # Split at BS1
        psi_A, psi_B = self.bs1.split(psi_source)

        # Propagate Path A
        psi_A = self.propagate(psi_A, length=self.L_A)

        # Propagate Path B
        psi_B = self.propagate(psi_B, length=self.L_B)

        # Recombine at BS2
        psi_D1, psi_D2 = self.bs2.split(psi_A + psi_B)

        # Measure intensities
        I_D1 = np.sum(np.abs(psi_D1)**2)
        I_D2 = np.sum(np.abs(psi_D2)**2)

        return I_D1, I_D2

    def measure_phase_in_path_B(self, tick):
        """
        Direct phase measurement at intermediate tick.
        """
        psi_B_intermediate = self.get_path_B_state(tick)
        phase = np.angle(psi_B_intermediate[self.mirror_B.position])

        return phase
```

---

## 6. Expected Results

### 6.1 Validation Outcomes

**Qualitative**:
- ✅ Wave packets maintain coherence over 1000+ ticks
- ✅ Interference fringes observed with V > 0.9
- ✅ Mach-Zehnder produces tunable interference pattern
- ✅ Direct phase measurement doesn't destroy interference

**Quantitative**:
- ✅ Dispersion relation: v_group = c×cos(k×Δx/2) validated (r > 0.99)
- ✅ Fringe period: Δφ = 2π when ΔL = λ (within 2%)
- ✅ Energy conservation: I_D1 + I_D2 = I_source (within 1%)
- ✅ Visibility: V > 0.9 for all interferometer tests

### 6.2 Unique Tick-Frame Predictions

**Prediction 1: Dispersion in Discrete Spacetime**
```
High-frequency waves (short λ) travel slower than c
v_group(k) = c × cos(k×Δx/2) < c  for k > 0

This DIFFERS from continuous QM where v_group = c always
```

**Prediction 2: Direct Phase Access Without Collapse**
```
Measuring phase in Path B does NOT destroy interference
Tick-frame: Deterministic substrate → no wavefunction collapse
QM: Measurement collapses → interference destroyed

THIS IS A FALSIFIABLE DIFFERENCE between tick-frame and QM
```

**Prediction 3: Temporal Interference**
```
γ-field modulation creates phase shift from TIME difference
Δφ = Δω × Δt  (even if spatial paths equal!)

Can isolate temporal vs spatial contributions to interference
UNIQUE to tick-frame (cannot be done in standard optics)
```

**Prediction 4: Nyquist Aliasing**
```
Waves with f > f_max = 1/(2×t_planck) alias to lower frequencies
Create wave packet with k > π/Δx → appears as k' = 2π/Δx - k

This CANNOT occur in continuous spacetime
```

### 6.3 Significance

**If Validated**:
1. ✅ **Wave mechanics works in discrete spacetime** (Ch7 confirmed)
2. ✅ **Phase is directly accessible** (unique advantage over QM)
3. ✅ **Dispersion emerges from discreteness** (distinctive prediction)
4. ✅ **Temporal interference testable** (space vs time separation)

**If Failed**:
- Wave packets decohere → discrete wave equation invalid
- Interference doesn't match theory → phase representation wrong
- Dispersion differs → Ch7 derivation has errors

**Either Way**: Honest, falsifiable test of tick-frame wave mechanics.

---

## 7. Comparison to Quantum Mechanics

| Feature | Quantum Mechanics | Tick-Frame Physics |
|---------|-------------------|-------------------|
| **Wavefunction** | Fundamental (ψ exists) | Emergent (pattern in substrate) |
| **Phase** | Not directly measurable | Stored variable, direct access |
| **Measurement** | Collapses wavefunction | Passive read, no collapse |
| **Which-path** | Destroys interference | Preserves interference |
| **Uncertainty** | ΔE×Δt ≥ ℏ/2 (fundamental) | Emerges from sampling limits |
| **Dispersion** | None (v_group = c) | Yes (v_group < c for high k) |
| **Nyquist limit** | None | f_max = 1/(2×t_planck) |
| **Temporal interference** | Not separable | Isolatable via γ-field |

**Key Difference**: Tick-frame interferometry can measure phase at every tick without disturbing evolution → complete experimental transparency impossible in QM.

---

## 8. Experimental Roadmap

### Phase 1: Wave Propagation (Weeks 1-4)
- Implement discrete wave equation solver
- Create Gaussian wave packets
- Test propagation and coherence
- Validate dispersion relation

**Deliverable**: `wave_mechanics.py` + Tests 1-3 passed

### Phase 2: Simple Interference (Weeks 5-6)
- Two-source interference
- Variable phase difference
- Fringe visibility measurement

**Deliverable**: Tests 4-6 passed, V > 0.95

### Phase 3: Optical Components (Weeks 7-9)
- Beam splitter implementation
- Mirror implementation
- Energy conservation validation

**Deliverable**: `optical_components.py` + Tests 7-8 passed

### Phase 4: Full Interferometer (Weeks 10-11)
- Mach-Zehnder assembly
- Path control and synchronization
- Fringe scanning

**Deliverable**: `interferometer.py` + Tests 9-11 passed, V > 0.9

### Phase 5: Advanced Validation (Week 12)
- Discrete dispersion test
- Direct phase measurement
- Temporal interference (if time)

**Deliverable**: Tests 12-14, RESULTS.md documented

---

## 9. Success Criteria

### Minimum (Must Achieve):
- ✅ Wave packets propagate 1000+ ticks without decoherence
- ✅ Two-source interference: V > 0.95
- ✅ Mach-Zehnder interference: V > 0.9
- ✅ Energy conservation: <1% error

### Target (Aim For):
- ✅ Dispersion relation validated: r > 0.99
- ✅ Direct phase measurement: No interference degradation
- ✅ Fringe period matches λ: <2% error

### Stretch (If Time Permits):
- ✅ Temporal interference demonstrated
- ✅ Nyquist aliasing observed
- ✅ Which-path without collapse proven

---

## 10. Conclusion

**Tick-frame interferometry is feasible and offers unique advantages**:

1. **Planck-scale precision** (cannot be achieved in real labs)
2. **Direct phase access** (no quantum measurement problem)
3. **Discrete spacetime tests** (dispersion, Nyquist aliasing)
4. **Temporal vs spatial separation** (unique to tick-frame)

**This experiment will either**:
- ✅ **Validate** discrete wave mechanics (Ch7) with interferometric precision
- ❌ **Falsify** current wave description, revealing limitations

**Both outcomes are scientifically valuable** - honest, rigorous testing of tick-frame physics.

---

**Document Status**: Theoretical Framework Complete
**Next Step**: Begin implementation (Phase 1: Wave Propagation)
**Timeline**: 12 weeks for full interferometer validation
**Priority**: HIGH - Core wave mechanics validation

**References**:
- Chapter 7 §4: Discrete wave equations and dispersion
- Experiment #55: Pattern phase representation
- Document 051: Photon model (periodic imprints)
- Honest Status: Update after experimental validation
