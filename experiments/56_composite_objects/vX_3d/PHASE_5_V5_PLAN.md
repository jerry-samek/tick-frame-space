# Experiment 56 Phase 5 V5: 3D Fragmented Cloud Implementation

**Date**: 2026-01-23
**Status**: PLANNED
**Based on**: V4 2D implementation (failed long-term stability test)
**Goal**: Implement 3D fragmented electron cloud to test if dimensional upgrade resolves instability

---

## I. Motivation

### A. V4 Revealed Fundamental 2D Instability

Phase 4 V4 **failed** due to intrinsic 2D long-term instability:
- **50 fragments**: Runaway at tick ~51,600 (appeared stable until 50k)
- **100 fragments**: Runaway at tick ~69,000 (earlier due to lighter fragments)
- **Root cause**: Energy injection (jitter) > dissipation (collisions) over long timescales
- **Not fixable** by parameter tuning - fundamental to 2D physics

### B. Theory Predicted This

**Doc 015_01** (Dimensional Closure Framework):
> "3D is transitional, not terminal. Closure boundary: 4D–5D are the terminal stability substrates."
> "2D: Surfaces fail to capture volumetric causality and stable horizons."

**Doc 040_01** (Why 3D Emerges):
> "2D: Surfaces allow more variation, but fail to capture volumetric causality and stable horizons."

**Doc 050_01** (Dimensional Equivalence Rejection):
> Proved (2D+t) ≠ 3D through 1,095 experimental configurations.

**Lesson**: We should have started with 3D. 2D was a false economy.

### C. What We Learned from 2D (V3, V4)

Despite the instability, 2D experiments validated key concepts:
- ✓ Collision dynamics DO create shell-like structures (3 shells detected)
- ✓ Zero-point jitter prevents collapse
- ✓ Fragmented cloud model is computationally tractable
- ✗ 2D cannot maintain long-term stability (runaway after 50k-70k ticks)
- ✗ Energy level gaps did not emerge in 2D
- ✗ Angular momentum (scalar L_z) did not converge

**V5 Goal**: Test if 3D resolves these issues.

---

## II. Scientific Hypothesis

### A. Primary Hypothesis (3D Stability)

**H₁**: 3D fragmented cloud with full angular momentum vector and 3D collision phase space will maintain long-term stability for 200k+ ticks.

**Evidence required**:
- Cloud radius drift < 10% over 200k ticks
- 0 fragment escapes
- Energy conservation < 5% drift (no runaway)
- Angular momentum vector converges to stable orientation

**Mechanism**: 3D provides:
1. **Full angular momentum conservation**: L = (Lx, Ly, Lz) vs scalar L_z
2. **Larger collision phase space**: More ways to redistribute energy without escape
3. **Volumetric causality**: Proper 1/r potential in 3D volume element (r²dr)
4. **Theory compliance**: Meets minimum 3D requirement from Doc 015_01

### B. Secondary Hypothesis (Quantization)

**H₂**: If 3D is stable, extended 200k-tick runs will reveal quantization signatures.

**Expected signatures**:
1. **Radial shells**: ≥3 discrete shells (2D showed this, should persist in 3D)
2. **Energy level gaps**: Forbidden energy regions (didn't appear in 2D)
3. **Maxwell-Boltzmann**: Velocity distribution equilibrates (inconclusive in 2D)
4. **Angular momentum quantization**: L vector converges (not possible in 2D)

### C. Null Hypothesis

**H₀**: 3D also exhibits long-term runaway, indicating the fragmented cloud model itself (not dimensionality) is flawed.

**If true, next steps**:
- Add magnetic field interactions (Doc 070_02)
- Reduce jitter strength (energy injection)
- Implement spin dynamics
- Consider 4D spatial dimensions (Doc 015_01 terminal stability)

---

## III. Implementation Plan

### Phase 1: Convert Core Physics to 3D

#### A. Fragmented Cloud (`fragmented_cloud.py`)

**Current (2D)**:
```python
position: np.ndarray  # (x, y) relative to proton
velocity: np.ndarray  # (vx, vy)
```

**Target (3D)**:
```python
position: np.ndarray  # (x, y, z) relative to proton
velocity: np.ndarray  # (vx, vy, vz)
```

**Changes needed**:

1. **Fragment initialization** (line 138-202):
   ```python
   # Current: 2D polar (r, θ)
   theta = random angles [0, 2π]
   x = r * cos(theta)
   y = r * sin(theta)

   # New: 3D spherical (r, θ, φ)
   theta = random angles [0, 2π]  # azimuthal
   phi = arccos(1 - 2*random)  # polar, uniform on sphere
   x = r * sin(phi) * cos(theta)
   y = r * sin(phi) * sin(theta)
   z = r * cos(phi)
   ```

2. **Center of mass** (line 138):
   ```python
   # Current
   self.center_of_mass = np.array([0.0, 0.0])

   # New
   self.center_of_mass = np.array([0.0, 0.0, 0.0])
   ```

3. **Angular momentum** (line 265-277):
   ```python
   # Current: scalar L_z
   L_z = Σ (x*vy - y*vx)
   self.angular_momentum = L_z

   # New: vector L = r × p
   L = np.zeros(3)
   for fragment in self.fragments:
       L += np.cross(fragment.position, fragment.mass * fragment.velocity)
   self.angular_momentum = L  # Now a 3D vector
   self.angular_momentum_magnitude = np.linalg.norm(L)
   ```

4. **Radial density profile** (line 303-318):
   ```python
   # Current: 2D normalization
   bin_area = 2 * np.pi * bin_centers * dr  # circumference × width
   density = counts / bin_area / n_fragments

   # New: 3D normalization
   bin_volume = 4 * np.pi * bin_centers**2 * dr  # surface area × width
   density = counts / bin_volume / n_fragments
   ```

5. **Maxwell-Boltzmann test** (line 369-400):
   ```python
   # Current: 2D Rayleigh distribution
   # v in 2D follows Rayleigh: p(v) ∝ v * exp(-v²/2σ²)

   # New: 3D Maxwell-Boltzmann
   # v in 3D follows Maxwell: p(v) ∝ v² * exp(-v²/2σ²)
   # Use scipy.stats.maxwell for distribution
   ```

#### B. Zero-Point Jitter (`zero_point_jitter.py`)

**Current (2D)**:
```python
jitter = np.random.normal(0, jitter_strength, size=2)  # (dx, dy)
```

**Target (3D)**:
```python
jitter = np.random.normal(0, jitter_strength, size=3)  # (dx, dy, dz)
```

**Changes**: Line 34, 68 - change `size=2` to `size=3`

#### C. Collision Dynamics (`collision_dynamics.py`)

**Good news**: Already dimension-agnostic!

```python
# Uses np.linalg.norm() which works for any dimension
distance = np.linalg.norm(frag_i.position - frag_j.position)

# Collision response uses vector operations
v_rel = vi - vj
v_cm = (mi * vi + mj * vj) / (mi + mj)
```

**Changes**: ✓ **None required!** Code already handles 3D.

#### D. Binding Detection (`binding_detection_v2.py`)

**Question**: Does gamma-field need 3D grid?

**Current**: 2D grid (100×100)

**Options**:
1. **Keep 2D field** (proton at center, cylindrical symmetry)
   - Fragment positions projected to (x, y) plane for field lookup
   - Z-component ignored for gamma-well
   - **Advantage**: No code changes, faster computation
   - **Disadvantage**: Not physically accurate

2. **Upgrade to 3D field** (100×100×100 grid)
   - Full 3D field solver
   - **Advantage**: Physically correct
   - **Disadvantage**: 100× more memory, 10× slower

**Recommendation**: Start with **Option 1** (2D field, cylindrical symmetry).
- Proton at origin creates radially symmetric field anyway
- Gradient force: F = -k * grad(γ) points radially → naturally 3D
- If V5 fails, revisit 3D field as potential issue

#### E. Config (`config_v5.py`)

**New parameter**:
```python
spatial_dimensions: int = 3
```

**All other parameters unchanged** (start with V3/V4 proven values):
- `n_fragments = 50`
- `coupling_constant = 0.001`
- `jitter_strength = 0.001`
- `restitution_coefficient = 0.8`
- `collision_radius = 0.5`
- `proton_mass = 100.0`
- `electron_total_mass = 0.1`

#### F. Experiment Runner (`experiment_56a_v5_3d.py`)

**Changes**:
1. Update gamma-gradient application (line 114-130):
   ```python
   # Current: 2D gradient
   gamma_gradient = self.detector.compute_gradient_at_position(abs_position)  # 2D vector

   # New: 3D gradient
   # If using 2D field: project to (x,y), compute 2D gradient, extend to 3D
   abs_pos_2d = abs_position[:2]  # (x, y)
   gamma_gradient_2d = self.detector.compute_gradient_at_position(abs_pos_2d)
   gamma_gradient = np.array([gamma_gradient_2d[0], gamma_gradient_2d[1], 0.0])

   # Apply radial-only force (already 3D-compatible)
   r_mag = np.linalg.norm(frag.position)
   if r_mag > 0.01:
       r_hat = frag.position / r_mag
       grad_radial = np.dot(gamma_gradient, r_hat)
       accel = self.config.coupling_constant * grad_radial * r_hat
   ```

2. Update snapshot reporting:
   ```python
   # Add angular momentum magnitude
   snapshot['angular_momentum_magnitude'] = np.linalg.norm(self.electron_cloud.angular_momentum)
   snapshot['angular_momentum_vector'] = self.electron_cloud.angular_momentum.tolist()
   ```

---

## IV. Testing Strategy

### A. Phase 5a: 3D Baseline Stability Test

**Configuration**:
- Fragments: 50
- Ticks: 100,000
- All V3/V4 parameters unchanged
- **Only change: 2D → 3D**

**Success Criteria**:
| Criterion | Threshold | V4 (2D) Result |
|-----------|-----------|----------------|
| Cloud radius drift | < 10% | 876,638% ✗ |
| Fragment escapes | 0 | 15/50 ✗ |
| Energy conservation | < 10% | +256% ✗ |
| No runaway by 100k | True | False ✗ |

**Expected Outcome**:
- **If PASS**: 3D resolves stability issue → proceed to Phase 5b
- **If FAIL**: Fundamental model problem → see Section VII

**Runtime**: ~7 minutes (same as V3)

### B. Phase 5b: Extended Quantization Study

**Configuration**:
- Fragments: 50
- Ticks: 200,000 (2× Phase 5a)
- Test long-term stability (2D failed at 51k ticks)

**Success Criteria**:
| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| Cloud stable at 200k | r_drift < 10% | Critical test |
| 0 escapes | 0/50 | Must maintain binding |
| Energy conserved | |E_drift| < 5% | Better than V4's +256% |
| L convergence | σ(L)/|L| < 0.1 | Vector should stabilize |

**Quantization Analysis**:
1. Radial shells: Should see ≥3 discrete peaks
2. Energy gaps: Check energy histogram for forbidden regions
3. MB distribution: Velocity magnitudes should fit Maxwell distribution
4. L quantization: Angular momentum vector should converge

**Runtime**: ~15 minutes

---

## V. Expected Results

### Scenario 1: 3D Stability Success (Optimistic)

**Observations**:
- Cloud radius stable for 200k ticks (drift ~ 3-5%)
- 0 fragment escapes
- Energy conserved (drift < 5%)
- Angular momentum vector converges: L → L_0, |L| stable

**Quantization signatures**:
- ✓ 3-5 radial shells detected
- ✓ Energy histogram shows 1-2 forbidden gaps
- ✓ Velocity distribution fits 3D Maxwell-Boltzmann (p > 0.05)
- ✓ Angular momentum magnitude converges (σ < 0.001)

**Interpretation**:
- **3D resolves 2D instability** ✓
- **Doc 070_01 quantization hypothesis validated** ✓
- Fragmented cloud is a viable quantum analog
- Theory vindicated: 3D minimum requirement confirmed

**Next Steps**:
- Test with more fragments (N = 100) - should be stable now
- Extend to multi-electron atoms (Helium, Lithium)
- Compare quantitatively with Schrödinger solutions
- Publish findings

### Scenario 2: 3D Marginal Stability (Realistic)

**Observations**:
- Cloud stable to 100k ticks, marginal at 200k (drift ~ 15-20%)
- 1-2 fragments escape at very late times (>150k ticks)
- Energy drift improving but not < 5% (~ 8-12%)
- Angular momentum partially converges

**Quantization signatures**:
- ✓ Radial shells present (2-3 shells)
- ? Energy gaps weak or absent
- ✓ MB distribution approximately fits
- ? Angular momentum slowly converging

**Interpretation**:
- 3D improves stability but doesn't fully resolve it
- May need longer equilibration (500k+ ticks)
- Or parameter tuning (reduce jitter, adjust coupling)
- Quantization emerging slowly

**Next Steps**:
- Run ultra-long test (500k ticks)
- Parameter scan: jitter × coupling × restitution
- Implement 3D gamma-field (remove cylindrical approximation)
- Consider adding magnetic interactions

### Scenario 3: 3D Also Fails (Pessimistic)

**Observations**:
- Runaway still occurs (delayed to ~80k-100k but still present)
- Energy continues to increase → positive
- Fragments escape
- System disintegrates

**Interpretation**:
- Dimensionality NOT the root cause
- **Fragmented cloud model itself may be flawed**:
  - Zero-point jitter too strong?
  - Need velocity-dependent damping?
  - Missing magnetic interactions?
  - Need spin dynamics?

**Next Steps (Major Model Revision)**:
1. **Reduce jitter**: Test jitter = 0.0005, 0.0001, 0.0
2. **Add damping**: Velocity-dependent friction term
3. **Magnetic field**: Doc 070_02 mentions field rotation
4. **Spin dynamics**: Fragments need internal degrees of freedom?
5. **4D spatial**: Doc 015_01 says 4D-5D are terminal stability substrates
6. **Different potential**: Not 1/r but something else?

---

## VI. Comparison Matrix: 2D vs 3D

| Feature | 2D (V3, V4) | 3D (V5) |
|---------|-------------|---------|
| **Position** | (x, y) | (x, y, z) |
| **Velocity** | (vx, vy) | (vx, vy, vz) |
| **Angular momentum** | Scalar L_z | Vector (Lx, Ly, Lz) |
| **Initialization** | Polar (r, θ) | Spherical (r, θ, φ) |
| **Radial normalization** | 2πr·dr | 4πr²·dr |
| **Velocity distribution** | Rayleigh (2D MB) | Maxwell (3D MB) |
| **Phase space** | 4D (2 pos + 2 vel) | 6D (3 pos + 3 vel) |
| **Collision cross section** | σ ∝ r | σ ∝ r² |
| **Orbital structure** | Limited (no p, d orbitals) | Full (s, p, d, f...) |
| **Stability (V4 test)** | ✗ Runaway at 51k | ? TBD |
| **Theory compliance** | Below minimum | Minimum 3D |

---

## VII. Failure Contingencies

### If V5 Also Exhibits Runaway

**Diagnosis Tree**:

1. **Check Energy Budget**:
   - Measure: E_injection (jitter), E_dissipation (collisions), E_work (gradient)
   - If E_injection > E_dissipation: Reduce jitter OR increase dissipation

2. **Parameter Scan**:
   - Jitter: [0.0001, 0.0005, 0.001]
   - Restitution: [0.6, 0.7, 0.8, 0.9]
   - Coupling: [0.0005, 0.001, 0.002]
   - Find stable region in parameter space

3. **Add Damping**:
   - Velocity-dependent friction: F_drag = -γ * v
   - Ensures energy dissipation > injection at high energies
   - γ ~ 0.0001 (weak damping)

4. **Remove Jitter**:
   - Test with jitter = 0 (no zero-point energy)
   - If stable: jitter was the problem
   - If collapses: jitter is necessary but too strong

5. **Add Magnetic Interactions**:
   - Doc 070_02: Field rotation stabilizes patterns
   - Implement B-field: F = q(v × B)
   - Magnetic force provides additional binding

6. **Upgrade to 4D Spatial**:
   - Doc 015_01: "4D–5D are terminal stability substrates"
   - Position: (x, y, z, w)
   - May provide additional phase space for stability

---

## VIII. File Structure

```
experiments/56_composite_objects/v5/
├── PHASE_5_V5_PLAN.md               # This document
├── config_v5.py                     # Configuration (spatial_dimensions=3)
├── fragmented_cloud.py              # 3D fragment dynamics (MODIFIED)
├── zero_point_jitter.py             # 3D jitter (MODIFIED)
├── collision_dynamics.py            # Collision physics (unchanged)
├── binding_detection_v2.py          # Gamma-well (2D field with 3D gradient)
├── experiment_56a_v5_3d.py          # Main experiment (3D runner)
├── analyze_quantization.py          # Analysis tools (update for 3D)
└── results/
    ├── exp56a_v5_50frags_100k.json  # Phase 5a baseline
    ├── exp56a_v5_50frags_200k.json  # Phase 5b quantization
    └── analysis/                     # Plots and statistics
```

---

## IX. Implementation Checklist

### Phase 1: Code Conversion (30-60 minutes)

- [ ] `fragmented_cloud.py`:
  - [ ] Change position/velocity to 3D (add z-component)
  - [ ] Update initialization: 2D polar → 3D spherical
  - [ ] Fix angular momentum: scalar → vector
  - [ ] Update radial density: 2πr → 4πr²
  - [ ] Fix MB test: Rayleigh → Maxwell

- [ ] `zero_point_jitter.py`:
  - [ ] Change jitter from `size=2` to `size=3`

- [ ] `collision_dynamics.py`:
  - [ ] Verify dimension-agnostic (already OK)

- [ ] `binding_detection_v2.py`:
  - [ ] Add 3D gradient projection (2D field → 3D gradient)

- [ ] `config_v5.py`:
  - [ ] Add `spatial_dimensions = 3` parameter

- [ ] `experiment_56a_v5_3d.py`:
  - [ ] Update gradient force to handle 3D
  - [ ] Add L magnitude and L vector to snapshots

### Phase 2: Testing (15 minutes)

- [ ] Run Phase 5a: 50 fragments, 100k ticks
- [ ] Verify no errors during execution
- [ ] Check results: drift, escapes, energy

### Phase 3: Analysis (30 minutes)

- [ ] If Phase 5a passes: Run Phase 5b (200k ticks)
- [ ] Generate plots: r(t), E(t), L(t)
- [ ] Quantization analysis: shells, gaps, MB, L convergence
- [ ] Write PHASE_5_V5_RESULTS.md

---

## X. Success Metrics Summary

**Critical Success (Phase 5a)**:
- ✓ Cloud stable to 100k ticks (no runaway)
- ✓ 0 fragments escaped
- ✓ Energy drift < 10%
- ✓ Better than 2D (which failed at 51k)

**Full Success (Phase 5b)**:
- ✓ Cloud stable to 200k ticks
- ✓ 0 escapes
- ✓ Energy conserved < 5%
- ✓ Angular momentum converges
- ✓ ≥2 quantization signatures (shells, gaps, MB, or L)

**Failure**:
- ✗ Runaway before 100k ticks
- ✗ Multiple fragment escapes
- ✗ Energy drift > 20%
- → Proceed to contingency analysis (Section VII)

---

## XI. Timeline

**Estimated Total Time**: 2-3 hours

1. **Code conversion**: 30-60 minutes
   - Most changes are straightforward (2D → 3D)
   - Angular momentum: vector operations
   - Initialization: spherical coordinates

2. **Phase 5a execution**: 7 minutes
   - 50 fragments, 100k ticks

3. **Phase 5a analysis**: 10 minutes
   - Quick validation: drift, escapes, energy

4. **Phase 5b execution**: 15 minutes
   - 50 fragments, 200k ticks (if Phase 5a passes)

5. **Phase 5b analysis**: 30 minutes
   - Quantization analysis
   - Generate plots

6. **Documentation**: 30 minutes
   - Write PHASE_5_V5_RESULTS.md

---

## XII. References

**Theory Documents**:
- Doc 015_01: Dimensional Closure Framework
- Doc 040_01: Why 3D Emerges as Natural Equilibrium
- Doc 050_01: Dimensional Equivalence Rejection
- Doc 070_00: Fragmented Electron Cloud as Emergent Attractor
- Doc 070_01: Collision-Driven Stabilization
- Doc 070_02: Field Rotation (magnetic interactions)

**Previous Experiments**:
- V1: Initial composite structure (2D, failed)
- V2: Single-particle gradient-following (2D, failed)
- V3: 50 fragments, 10k ticks (2D, appeared successful)
- V4: Extended 200k ticks (2D, **revealed fundamental instability**)

**Key V4 Results**:
- 50 fragments: Runaway at tick 51,600
- 100 fragments: Runaway at tick 69,000
- 2D long-term unstable regardless of parameters
- Radial shells DO form (3 shells detected before runaway)
- Energy gaps did NOT appear in 2D

---

**Document Status**: COMPLETE
**Implementation Status**: READY TO BEGIN
**Expected Completion**: 2026-01-23 evening

---

## XIII. Key Question

**Can 3D resolve the fundamental instability of the fragmented cloud model?**

**V5 will definitively answer**:
- Is 2D the problem? (3D fixes it)
- Or is the model itself flawed? (3D also fails)

If 3D succeeds → Fragmented cloud theory validated, proceed to quantization study.

If 3D fails → Major model revision required (damping, magnetic fields, 4D, or abandon approach).

**Next**: Execute Phase 1 (Code Conversion).
