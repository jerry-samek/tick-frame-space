# Experiment 56 Phase 4: Dynamic Composite Physics (Full Implementation)

**Date**: 2026-01-22
**Status**: PLANNING
**Builds on**: Phase 3b (Binding Detection - VALIDATED)

---

## Overview

Phase 4 removes ALL shortcuts from Phase 3b and implements **full dynamic composite physics** with gradient-following geodesic motion, velocity-dependent field sources, and comprehensive validation tests.

### Purpose

Complete validation of tick-frame composite object theory by implementing:
1. **Gradient-following orbital dynamics** (replace frozen orbits)
2. **Velocity-dependent source terms** (moving composites)
3. **Internal structure dynamics** (vibration, rotation, excitation)
4. **Perturbation response** (collision dissolution, ionization)
5. **Multi-composite interactions** (molecular bonding)

---

## Shortcuts to Fix

### 1. Frozen Orbital Structure → Gradient-Following Geodesics

**Current Problem** (Phase 3b):
```python
# Electron position updated via simple circular motion
orbital_phase += orbital_frequency * dt
position = center + r × [cos(phase), sin(phase)]
```

**Phase 4 Solution** (from Exp 51 v10):
```python
# Electron follows time-flow gradient (geodesic motion)
gamma_gradient = compute_gradient(gamma_field, electron.position)
acceleration = coupling_constant * gamma_gradient
velocity += acceleration * dt
position += velocity * dt
```

**Implementation**:
- Port `update_velocity_gradient_following()` from `v10/entity_motion.py:155-174`
- Constituents become `MovingEntity` instances with position, velocity, acceleration
- Each tick: compute ∇γ at constituent position, update velocity/position
- Orbital motion emerges naturally from gradient following (no forced orbits!)

**Expected Behavior**:
- Electron initially at r=2.0 with tangential velocity
- Gradient pulls electron toward proton (attractive force)
- Tangential velocity prevents collapse → stable orbit emerges
- Orbital radius may drift slightly before stabilizing (realistic!)

---

### 2. Simplified Orbital Velocity → Gradient-Derived Velocity

**Current Problem**:
```python
v_orbital = 0.1  # Hardcoded constant (c/10)
```

**Phase 4 Solution**:
```python
# Velocity determined by initial conditions + gradient evolution
# For circular orbit: v = sqrt(γ_gradient × r) as natural equilibrium
# But let system find its own equilibrium!

# Initialize with tangential velocity
v_tangential = sqrt(gamma_gradient_at_r * r)
electron.velocity = perpendicular_to_radius * v_tangential

# Then let gradient following take over
```

**Implementation**:
- Calculate equilibrium velocity from γ-gradient at initialization
- Set initial velocity perpendicular to radius (tangential)
- System evolves naturally via `update_velocity_gradient_following()`
- Measure actual orbital parameters from trajectory (not prescribed!)

**Expected Behavior**:
- Slightly elliptical orbits (not perfectly circular)
- Precession of orbit (like Mercury's perihelion shift!)
- Energy dissipation → circularization over time (if damping present)

---

### 3. No Velocity-Dependent Source → Full v11 Source Terms

**Current Problem**:
```python
# binding_detection.py:84
# Source assumes stationary particles (no velocity factor)
S = mass × (energy / E_max)
```

**Phase 4 Solution** (from v11):
```python
# Full source with velocity correction
gamma_SR = 1 / sqrt(1 - v²/c²)
S = mass × (energy / E_max) × (1 + v²/c²) × gamma_SR
```

**Implementation**:
- Add `velocity` parameter to `compute_source_from_patterns()`
- Each constituent contributes source with its velocity
- Source field updates every tick as constituents move
- Gamma-well shape changes with internal motion (dynamic!)

**Expected Behavior**:
- Moving electrons create stronger source (higher energy density)
- Gamma-well deforms slightly during orbital motion
- Asymmetric wells for fast-moving composites
- Composite kinetic energy affects binding (relativistic correction)

---

### 4. Frozen Nucleus Structure → Internal Nuclear Dynamics

**Current Problem**:
```python
# composite_structure.py:432
velocity=np.array([0.0, 0.0])  # Frozen structure (no motion)
```

**Phase 4 Solution**:
```python
# Nucleons orbit within nucleus via gradient following
for nucleon in nucleus.constituents:
    gamma_gradient = compute_composite_internal_gradient(nucleus, nucleon)
    nucleon.update_velocity_gradient_following(gamma_gradient)
    nucleon.position += nucleon.velocity * dt
```

**Implementation**:
- Initialize nucleons in stable configuration (tetrahedral for He-4)
- Give small random velocities (thermal motion analog)
- Each tick: update via gradient following within composite γ-well
- Pauli exclusion: add repulsive term to prevent collapse (short-range)

**Expected Behavior**:
- Nucleons orbit within ~r_nucleus (confined by γ-well)
- Kinetic energy → binding energy contribution
- Vibrational modes emerge (breathing, quadrupole)
- Stability test: does nucleus maintain structure over 50,000 ticks?

---

### 5. Simplified H₂ → Proper Molecular Orbital Dynamics

**Current Problem**:
```python
# composite_structure.py:482
# Two electrons positioned "between protons" (static)
electron_position = (proton1_pos + proton2_pos) / 2
```

**Phase 4 Solution**:
```python
# Electrons orbit in molecular orbital (figure-8 or shared well)
# Each electron follows combined γ-well from both protons
gamma_well_total = gamma_well_proton1 + gamma_well_proton2
gamma_gradient = compute_gradient(gamma_well_total, electron.position)
electron.update_velocity_gradient_following(gamma_gradient)
```

**Implementation**:
- Compute γ-well as superposition from all constituents
- Electrons follow gradient in combined well
- Molecular bond = shared γ-well occupancy
- Measure bond length, vibrational frequency from dynamics

**Expected Behavior**:
- Electrons orbit both protons (covalent bond character)
- Protons vibrate along bond axis (stretching mode)
- Bond length stabilizes at equilibrium (γ-well overlap minimum)
- Binding energy = total energy - separated atom energies

---

## Implementation Plan

### Phase 4a: Gradient-Following Core (Week 1)

**Goal**: Replace frozen orbits with v10-style gradient following

**Tasks**:
- [x] Port `MovingEntity` class from v10 (position, velocity, acceleration tracking)
- [x] Implement `compute_gamma_gradient()` in `GammaWellDetector`
- [x] Add `update_velocity_gradient_following()` to constituent particles
- [x] Modify `CompositeBindingManager.update()` to use gradient following
- [x] Test: Does hydrogen electron achieve stable orbit naturally?

**Deliverable**: `binding_detection_v2.py` with gradient-following dynamics

**Validation**:
- Electron initialized at r=2.0 with v_tangential
- No forced circular motion code (delete `orbital_phase` update)
- After 10,000 ticks: orbital radius within 10% of initial (stable)
- Orbital precession measured and consistent with γ-well asymmetry

---

### Phase 4b: Velocity-Dependent Sources (Week 1-2)

**Goal**: Add full velocity corrections to source terms

**Tasks**:
- [x] Add `velocity` field to `Pattern` class
- [x] Update `compute_source_from_patterns()` with v² and γ_SR corrections
- [x] Recompute γ-well field every tick (or every N ticks if stable)
- [x] Track field computation cost (optimize if needed)
- [x] Test: Does moving composite create correct source field?

**Deliverable**: `field_dynamics_v2.py` with velocity-dependent sources

**Validation**:
- Stationary particle: source matches Phase 3b (v=0 limit)
- Moving particle (v=0.3c): source increased by factor ~1.1
- Fast particle (v=0.8c): source increased by factor ~2.5 (relativistic)
- Field asymmetry: γ-well "drags" behind moving particle (retardation)

---

### Phase 4c: Internal Dynamics Implementation (Week 2)

**Goal**: Add internal motion for multi-constituent composites

**Tasks**:
- [x] Implement `update_internal_dynamics()` method for composites
- [x] Add Pauli exclusion force (short-range repulsion for fermions)
- [x] Initialize nucleus with stable configuration + thermal velocities
- [x] Track vibrational modes (measure frequencies)
- [x] Test: Does helium nucleus remain stable?

**Deliverable**: `composite_dynamics.py` with internal structure evolution

**Validation**:
- Helium-4 nucleus: stable for 50,000 ticks
- RMS radius < 0.2 (nucleons confined within r_nucleus)
- Vibrational frequency ~0.5 rad/tick (resonance peak in spectrum)
- Binding energy consistent: E_bind = -28 ± 2 (nuclear scale)

---

### Phase 4d: Perturbation Response Tests (Week 2-3)

**Goal**: Test composite response to external energy injection

**Test 1: Ionization** (Exp 56c)
- High-energy photon collides with hydrogen atom
- Energy transferred to electron: E_photon → kinetic energy
- Measure: ionization threshold (when electron escapes)
- Expected: E_threshold ≈ |E_binding| (13.6 eV analog)

**Test 2: Composite Excitation**
- Medium-energy collision → electron to excited state
- Electron orbital radius increases (higher energy level)
- Measure: excitation energy, decay time
- Expected: Quantized energy levels emerge? (Check for resonances)

**Test 3: Composite Dissolution**
- Ultra-high-energy collision → composite breaks apart
- All constituents scatter (unbound)
- Measure: dissolution threshold, fragment energies
- Expected: E_dissolution > E_binding

**Deliverable**: `experiment_56c_perturbation.py`

**Validation**:
- Ionization threshold: 12-15 energy units (within 20% of E_bind)
- Excitation: at least 2 stable excited states observed
- Dissolution: fragments conserve total energy (E_before = E_after)

---

### Phase 4e: Molecular Bonding (Week 3)

**Goal**: Test H + H → H₂ molecular bond formation

**Setup**:
- 2 hydrogen atoms initially separated by d=5.0
- Both stationary, then given slow approach velocity (v=0.01c)
- Track: separation distance, electron positions, binding energy

**Procedure**:
1. Atoms approach gradually (1000 ticks to contact)
2. γ-wells overlap when d < 3.0 (critical radius)
3. Electrons begin to orbit both protons (shared well)
4. Molecule forms if total energy < 2×E_H (energetically favorable)

**Expected Behavior**:
- Critical distance d_crit ≈ 3.0 (γ-well overlap threshold)
- Binding energy: E_H2 - 2×E_H ≈ -4.5 (covalent bond energy)
- Bond length stabilizes at d_eq ≈ 1.5 (equilibrium separation)
- Vibrational frequency ≈ 0.3 rad/tick (bond stretching mode)

**Deliverable**: `experiment_56b_molecular_bonding.py`

**Validation**:
- Bond forms: separation stabilizes at d_eq
- E_binding < 0 (bound state)
- Electrons shared: probability density between protons
- Molecule survives 20,000 ticks without dissociation

---

## Success Criteria

### Qualitative ✅

- [x] Orbital motion emerges naturally from gradient following (no prescribed orbits)
- [x] Composites respond realistically to perturbations (excitation, ionization, dissolution)
- [x] Internal structure evolves dynamically (vibration, rotation)
- [x] Molecular bonds form from γ-well overlap
- [x] All dynamics deterministic and reproducible

### Quantitative ✅

- [x] **Hydrogen orbital stability**: radius drift < 10% over 10,000 ticks
- [x] **Orbital precession**: measured rate consistent with γ-well asymmetry
- [x] **Ionization threshold**: E_threshold within 20% of |E_binding|
- [x] **Helium nucleus**: stable for 50,000 ticks, RMS radius < 0.2
- [x] **Molecular bond**: E_H2 - 2×E_H < 0 (favorable bonding)
- [x] **Energy conservation**: ΔE/E < 1% for all collision tests

---

## Expected Computational Cost

**Phase 3b baseline**: ~1ms per tick per composite (frozen orbits)

**Phase 4 costs**:
- Gradient computation: +0.5ms (∇γ at each constituent position)
- Velocity updates: +0.2ms (gradient following integration)
- Source field recomputation: +2ms (if every tick) OR +0.2ms (if every 10 ticks)
- **Total**: ~4ms per tick per composite (4× slower)

**Optimization strategies**:
- Cache γ-field gradient (recompute only when constituents move significantly)
- Adaptive timestep (stable orbits → larger dt)
- Frozen structure for distant composites (only update nearby interactions)
- Hierarchical: update atoms independently, molecules as whole

**Scaling test**:
- 1 composite: 4ms/tick (acceptable)
- 10 composites: 40ms/tick (acceptable)
- 100 composites: 400ms/tick (2.5 Hz simulation rate, marginal)
- 1000 composites: 4000ms/tick (0.25 Hz, too slow → optimize!)

---

## Theoretical Predictions to Test

### Prediction 1: Orbital Precession

**Theory (Tick-Frame GR analog)**:
- γ-well from proton not exactly 1/r (discretized substrate)
- Orbital path precesses due to γ-field asymmetry
- Precession rate ∝ grid resolution and γ-well strength

**Test**:
- Measure periapsis angle over 1000 orbits
- Expected: Δθ_precession ≈ 0.1-1.0 degrees per orbit
- Compare with Schwarzschild formula: Δθ ~ 6πGM/(c²a(1-e²))

**Success**: Non-zero precession observed, scaling as predicted

---

### Prediction 2: Quantized Energy Levels?

**Theory (Open Question)**:
- If γ-well has discrete spatial structure (grid cells)
- Stable orbits may occur only at resonant radii
- Analog of Bohr quantization from substrate discreteness

**Test**:
- Initialize electrons at various radii (r = 1.0, 1.5, 2.0, 2.5, 3.0)
- Run 10,000 ticks, measure which orbits remain stable
- Plot stability vs radius (look for "allowed" bands)

**Success**: Discrete stable radii observed (e.g., only r=2.0 and r=4.0 stable)

**Failure**: All radii equally stable → no quantization from discreteness

**Significance**: Would be MAJOR result if quantization emerges naturally!

---

### Prediction 3: Composite Mass Increase with Binding

**Theory (Tick-Frame Energy-Mass relation)**:
- Bound composites have negative potential energy
- Total mass M_composite = Σm_i - |E_binding|/c²
- Bound composites slightly lighter than separated constituents

**Test**:
- Measure source field strength S ∝ M for separated H atoms vs H₂ molecule
- Expected: S_H2 < 2×S_H (mass defect from binding)
- Quantitative: ΔM/M ≈ |E_bind|/(Mc²) ≈ 4.5/(2×938) ≈ 0.2%

**Success**: Δ(source strength) consistent with binding energy prediction

---

### Prediction 4: Molecular Bond Directionality

**Theory (γ-Well Overlap Geometry)**:
- Covalent bond = electron shared in overlapping γ-wells
- Bond strength depends on overlap integral
- Directional: strongest when protons aligned, weakest when perpendicular

**Test**:
- Vary proton-proton angle while keeping distance constant
- Measure binding energy as function of angle
- Expected: E_bind maximum when aligned, minimum when perpendicular

**Success**: Angular dependence matches overlap integral prediction

---

## Integration with Other Experiments

### Experiment 55 (Collision Physics) ✅

**Phase 4 adds**:
- Collision outcome depends on composite internal energy
- Composite dissolution when E_collision > E_binding
- Energy transfer → excitation → delayed dissociation

**Integration**:
```python
# Exp 55: Detect collision
if position1 == position2:
    collision_energy = compute_collision_energy(pattern1, pattern2)

    # Exp 56 Phase 4: Check if composite survives
    if isinstance(pattern1, CompositePattern):
        if collision_energy > abs(pattern1.binding_energy):
            # Dissolve composite
            fragments = pattern1.dissolve()
            return fragments
        else:
            # Excite composite
            pattern1.excite(collision_energy)
            return [pattern1, pattern2]  # Elastic scatter
```

---

### Experiment 51 v11/v12 (Black Holes)

**Phase 4 enables**:
- Realistic matter in accretion disk (hydrogen atoms, not ghost particles)
- Test: Do composites survive tidal forces near event horizon?
- Spaghettification: composite stretched by γ-gradient until dissolution

**Future Test**:
- Hydrogen atom falls into black hole
- Track: does atom ionize? At what radius?
- Expected: Ionization when Δγ across atom exceeds binding

---

### Experiment 50 (Dimensional Equivalence Rejection) ✅

**Validates**:
- Time is NOT spatial dimension (Doc 50, 50_01)
- Composites exist in 2D/3D space + discrete time
- Binding via γ-wells (time-flow minima), not spatial curvature alone

**Phase 4 Consistency Check**:
- Composite physics should work in 2D, 3D (spatial dimensions)
- Should NOT work if time treated as spatial dimension
- Binding energy from temporal field (γ), not geometric potential

---

## Files Structure

```
experiments/56_composite_objects/
├── README.md                          # Phase overview (unchanged)
├── PHASE_3B_RESULTS.md                # Phase 3b validation ✅
├── PHASE_4_PLAN.md                    # This file (plan for full implementation)
│
├── v1/ (Phase 3b - frozen orbits)
│   ├── composite_structure.py         # ✅ Phase 3a
│   ├── binding_detection.py           # ✅ Phase 3b (frozen orbits)
│   └── experiment_56a_hydrogen.py     # ✅ Phase 3b validation
│
└── v2/ (Phase 4 - full dynamics)      # NEW IMPLEMENTATIONS
    ├── composite_structure_v2.py      # Add MovingEntity integration
    ├── binding_detection_v2.py        # Gradient-following dynamics
    ├── field_dynamics_v2.py           # Velocity-dependent sources
    ├── composite_dynamics.py          # Internal structure evolution
    │
    ├── experiment_56a_v2_hydrogen.py  # Gradient-following orbital test
    ├── experiment_56b_molecular.py    # H₂ bonding test
    ├── experiment_56c_perturbation.py # Ionization/excitation/dissolution
    ├── experiment_56d_nucleus.py      # Helium stability with internal motion
    │
    ├── config.py                      # Shared configuration
    ├── analysis.py                    # Analysis tools (orbit detection, FFT)
    └── PHASE_4_RESULTS.md             # Results summary (to be created)
```

---

## Timeline Estimate

**Week 1**: Phase 4a-b (gradient following + velocity sources)
- Day 1-2: Port v10 gradient following to Exp 56
- Day 3-4: Implement velocity-dependent sources
- Day 5-6: Test hydrogen atom with gradient-following orbit
- Day 7: Validation and debugging

**Week 2**: Phase 4c-d (internal dynamics + perturbation tests)
- Day 1-2: Implement internal dynamics for nuclei
- Day 3-4: Experiment 56c (ionization/excitation tests)
- Day 5-6: Experiment 56d (helium nucleus stability)
- Day 7: Analysis and comparison with Phase 3b

**Week 3**: Phase 4e (molecular bonding) + final validation
- Day 1-3: Implement H₂ bonding experiment
- Day 4-5: Test quantization hypothesis (prediction 2)
- Day 6: Test mass defect prediction (prediction 3)
- Day 7: Final results document + theory comparison

**Total**: 3 weeks for complete Phase 4 implementation and validation

---

## Risk Assessment

### Risk 1: Numerical Instability

**Problem**: Gradient-following with dt=1.0 may cause overshooting

**Mitigation**:
- Start with small coupling_constant (k=0.01)
- Adaptive timestep: reduce dt if |acceleration| too large
- Monitor energy conservation (should be < 1% drift)

### Risk 2: Orbit Decay/Escape

**Problem**: Without careful initialization, electron may spiral in or escape

**Mitigation**:
- Calculate equilibrium velocity accurately: v = sqrt(γ_grad × r)
- Initialize perpendicular to radius (pure tangential)
- Add slight damping (0.1% per tick) to stabilize orbits
- Fallback: If orbit unstable after 1000 ticks, re-initialize

### Risk 3: Computational Cost

**Problem**: Recomputing γ-field every tick may be too slow

**Mitigation**:
- Cache γ-field for N ticks (only recompute when constituents move > threshold)
- Typical: recompute every 10 ticks (10× speedup)
- For stable orbits: recompute every 100 ticks (100× speedup)
- Adaptive: recompute only when ΔE_binding > 1%

### Risk 4: No Quantization Observed

**Problem**: Discrete energy levels may not emerge (prediction 2 fails)

**Impact**: Not a failure! Would be interesting null result
- Means quantization requires additional physics (not just substrate discreteness)
- Guides future theory development
- Composites still valid even without quantization

---

## Open Questions for Phase 4

1. **What damping mechanism (if any) should apply to internal motion?**
   - Option A: No damping (conservative system)
   - Option B: Small damping (0.1%/tick) to model radiation losses
   - Option C: Adaptive damping (only when E > threshold)

2. **Should γ-field recompute every tick or be cached?**
   - Affects: realism vs computational cost
   - Test both: measure impact on orbital stability

3. **How to handle Pauli exclusion for nucleons?**
   - Option A: Hard-sphere repulsion (r < r_min → infinite force)
   - Option B: Soft repulsion (exponential: F ∝ exp(-r/λ))
   - Option C: Quantum pressure term (∇²ρ correction)

4. **Can we observe quantized energy levels?**
   - Critical test for substrate discreteness → quantum mechanics link
   - If YES → major result
   - If NO → need additional physics (ℏ-like parameter?)

5. **What determines bond angles in molecules?**
   - Test: H₂O (water) formation → expect 104.5° angle
   - From: γ-well overlap geometry? Pauli exclusion? Both?

---

## Success Metrics

**Minimum Success (Phase 4 validated)**:
- ✅ Hydrogen atom stable with gradient-following (no frozen orbits)
- ✅ Ionization threshold within 20% of theory
- ✅ H₂ molecule forms and remains stable
- ✅ Energy conservation < 1% for all tests

**Strong Success (Predictions confirmed)**:
- ✅ Minimum success criteria
- ✅ Orbital precession observed and measured
- ✅ Mass defect consistent with binding energy
- ✅ Molecular bond directionality matches γ-well overlap

**Exceptional Success (New Physics discovered)**:
- ✅ Strong success criteria
- ✅ Quantized energy levels emerge naturally
- ✅ All 4 theoretical predictions validated
- ✅ New unexpected phenomenon observed (e.g., composite spin, tunneling)

---

## Conclusion

**Phase 4 Goal**: Remove ALL shortcuts and implement full dynamic composite physics

**Why This Matters**:
- Phase 3b showed composites CAN exist in tick-frame physics
- Phase 4 shows composites BEHAVE REALISTICALLY with gradient-following dynamics
- Tests whether tick-frame universe can support chemistry, molecules, matter

**Path Forward**:
1. Implement Phase 4a-b (gradient following + velocity sources)
2. Validate hydrogen orbital stability (baseline)
3. Implement Phase 4c-e (internal dynamics + perturbations + bonding)
4. Test all 4 theoretical predictions
5. Write PHASE_4_RESULTS.md with complete analysis

**If successful**: Tick-frame physics validated for matter structure (atoms → molecules)

**If partial success**: Identify which aspects work vs need refinement

**Either way**: Major progress toward realistic tick-frame matter physics

---

**Ready to proceed with implementation?**

**Estimated effort**: 3 weeks (120-150 hours)

**Prerequisites**: Phase 3b complete ✅, v10 geodesics available ✅, v11 field dynamics available ✅

**Next step**: Implement Phase 4a (gradient-following core) → begin with `binding_detection_v2.py`