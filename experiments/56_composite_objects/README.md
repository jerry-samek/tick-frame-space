# Experiment 56: Composite Objects and Binding Physics

**Date**: January 2026
**Status**: In Development
**Builds on**: Experiment 55 (Collision Physics)

---

## Overview

This experiment implements **composite object formation and binding physics** from theoretical documents 054 and 030, extending the collision framework from Experiment 55.

### Purpose

Validate tick-frame predictions for:
1. **Multi-particle bound states** (atoms, molecules, nuclei)
2. **γ-well binding mechanism** (time-flow minima create attraction)
3. **Composite lifecycle** (formation, stability, dissolution)
4. **Emergent elasticity** (pattern persistence + energy restoration)
5. **Orbital dynamics** within composites

---

## Theoretical Foundation

**Primary Documents**:
- `docs/theory/raw/054_elasticity_of_composite_objects.md` - Composite binding via γ-wells
- `docs/theory/raw/030_collision_persistence_principle.md` - Particles as collision patterns
- `docs/theory/raw/053_tick_frame_collision_physics.md` - Merge regime creates composites

**Key Concepts**:

### γ-Well Binding Principle

Composite objects are bound by **shared γ-wells** (time-flow minima):

```
γ_well(r) = γ_grav(r) + γ_SR(v)

If multiple entities share a γ-well:
  → Bound composite object
  → Orbital motion around common center
  → Like atom: nucleus + electrons bound by EM field → γ-well
```

### Elasticity Emergence

Elastic behavior emerges from:
1. **Pattern persistence** - Patterns renew at each tick (temporal surfing)
2. **Energy restoration** - R parameter in field dynamics
3. **Finite bandwidth** - Speed of light limits response time

Example: Solid materials resist deformation because particles try to restore their original pattern configuration each tick.

### Composite vs Simple Patterns

- **Simple pattern**: Single particle (from Experiment 55)
- **Composite pattern**: Multiple bound particles with internal structure
  - Example: Hydrogen atom = proton + electron in γ-well
  - Example: H₂ molecule = 2 hydrogen atoms sharing γ-well
  - Example: Nucleus = protons + neutrons bound by strong γ-well

---

## Implementation Plan

### Phase 3a: Composite Structure (Week 1)

**Goal**: Define data structures for multi-particle composites

**Tasks**:
- [ ] Create `CompositePattern` class extending `Pattern`
- [ ] Track constituent particles (particle list + relative positions)
- [ ] Compute composite properties (total energy, mass, center of mass)
- [ ] Handle internal degrees of freedom (vibration, rotation)

**Deliverable**: `composite_structure.py`

### Phase 3b: Binding Detection (Week 1-2)

**Goal**: Detect when particles should form bound states

**Tasks**:
- [ ] Implement γ-well field computation around patterns
- [ ] Detect shared γ-well conditions (multiple particles in same well)
- [ ] Calculate binding energy (depth of γ-well)
- [ ] Determine orbital parameters (radius, period)

**Deliverable**: `binding_detection.py`

### Phase 3c: Lifecycle Management (Week 2)

**Goal**: Track composite formation, persistence, and dissolution

**Tasks**:
- [ ] Implement `CompositeLifecycleManager`
- [ ] Handle formation events (merge collisions → composites)
- [ ] Track stability over time (energy monitoring)
- [ ] Detect dissolution conditions (energy injection, field disruption)

**Deliverable**: `composite_lifecycle.py`

### Phase 3d: Validation Experiments (Week 2-3)

**Goal**: Test composite physics with realistic scenarios

**Test Cases**:
1. **Hydrogen atom formation** (proton + electron)
2. **Molecular bonding** (H + H → H₂)
3. **Nucleus stability** (protons + neutrons)
4. **Composite excitation** (vibration, rotation)
5. **Composite dissolution** (high-energy collision)

**Deliverable**: `experiment_56_validation.py`

---

## Success Criteria

### Qualitative

✅ Composite objects form from merge collisions
✅ Composites persist stably over many ticks
✅ γ-well binding energy determines stability
✅ Composites dissolve under sufficient energy injection
✅ Internal structure tracked correctly (constituent positions)
✅ Elastic behavior emerges naturally

### Quantitative

✅ Binding energy matches γ-well depth (within 5%)
✅ Orbital periods match analytical predictions (circular orbits)
✅ Energy conservation: E_composite = Σ E_constituents + E_binding
✅ Composite mass: M_composite = Σ m_constituents (non-relativistic)
✅ Vibrational modes: frequencies match spring-like restoration

---

## Composite Examples

### Example 1: Hydrogen Atom

**Structure**:
```
Composite: Hydrogen
Constituents:
  - Proton (center, stationary)
  - Electron (orbiting at r_Bohr)

Binding mechanism:
  - Proton creates γ_grav well
  - Electron falls into well
  - Orbital motion balances γ gradient

Binding energy:
  E_bind ≈ depth of γ-well at r_Bohr
```

**Test**: Place electron near proton, verify capture into stable orbit.

### Example 2: H₂ Molecule

**Structure**:
```
Composite: H₂ Molecule
Constituents:
  - Hydrogen atom #1
  - Hydrogen atom #2

Binding mechanism:
  - Overlapping γ-wells from both protons
  - Electrons shared between wells
  - Covalent bond = shared γ-well occupancy

Binding energy:
  E_bind ≈ overlap integral of γ-wells
```

**Test**: Bring two hydrogen atoms close, verify molecular bond formation.

### Example 3: Helium Nucleus

**Structure**:
```
Composite: Helium-4 Nucleus
Constituents:
  - 2 Protons
  - 2 Neutrons

Binding mechanism:
  - Strong γ-well from combined mass
  - Pauli exclusion prevents collapse
  - Orbital motion within nucleus

Binding energy:
  E_bind ≈ 28 MeV (real-world value)
  (Tick-frame: depth of composite γ-well)
```

**Test**: Merge 2 deuterium nuclei, verify stable helium formation.

---

## Relation to Experiment 55

**Experiment 55** provides the **collision physics** that creates composites:
- Regime 3.1 (Merge): Non-overlapping patterns → composite formation
- Composite pattern created, but no binding tracked

**Experiment 56** adds the **binding physics** that maintains composites:
- γ-well detection: Which particles should stay together?
- Orbital dynamics: How do constituents move within composite?
- Stability tracking: When do composites persist vs dissolve?

**Integration**:
```python
# Experiment 55: Collision creates composite
outcome = collision_processor.process_collision(...)
if outcome.regime == "merge":
    composite_pattern = outcome.new_entities[0]

# Experiment 56: Binding maintains composite
composite_object = CompositeObject.from_pattern(composite_pattern)
binding_manager.add_composite(composite_object)

# Each tick: Update internal dynamics
for tick in simulation:
    binding_manager.update_all_composites(tick)
    # Check stability, handle orbital motion, detect dissolution
```

---

## Key Challenges

### Challenge 1: γ-Well Computation

**Problem**: How to compute γ-well field around arbitrary pattern?

**Approach**:
- Use field dynamics from v11/v12 (Laplacian diffusion)
- Pattern at position (x,y) creates γ source: S(x,y) = m × E / E_max
- Solve Poisson equation: ∇²γ = -α × S
- γ-well depth = γ(center) - γ(infinity)

### Challenge 2: Multi-Body Binding

**Problem**: How to handle 3+ particles in same γ-well?

**Approach**:
- Start with 2-body (proton-electron, proton-neutron)
- Generalize to N-body (track pairwise binding energies)
- Use hierarchical structure (molecules = bound atoms, atoms = bound particles)

### Challenge 3: Internal Dynamics

**Problem**: How do constituents move within composite?

**Approach**:
- Option 1: **Frozen structure** (constituents fixed relative to center)
- Option 2: **Orbital dynamics** (constituents follow geodesics in composite γ-well)
- Option 3: **Quantum averaging** (constituents in superposition, average position)

Experiment 56 will test **Option 2** first (orbital dynamics).

### Challenge 4: Composite Collisions

**Problem**: What happens when composite collides with another object?

**Approach**:
- Composite as whole enters collision detection (single cell occupancy)
- Collision energy compared to binding energy:
  - E_collision < E_bind → Composite survives (elastic scatter)
  - E_collision ≈ E_bind → Excitation (vibrational/rotational modes)
  - E_collision > E_bind → Dissolution (composite breaks apart)

---

## Validation Experiments

### Experiment 56a: Hydrogen Atom Formation

**Setup**:
- 1 Proton (stationary, center of grid)
- 1 Electron (random position, low velocity)

**Procedure**:
1. Run simulation for 10,000 ticks
2. Track electron trajectory
3. Measure: orbital radius, period, binding energy

**Expected**:
- Electron captured into orbit around proton
- Stable orbit emerges (r ≈ Bohr radius analog)
- Binding energy = γ-well depth

**Success**: Stable orbit persists for 10,000+ ticks

### Experiment 56b: Molecular Bond Formation

**Setup**:
- 2 Hydrogen atoms (separate, approaching slowly)

**Procedure**:
1. Bring atoms together gradually
2. Monitor γ-well overlap
3. Detect bond formation (shared electron cloud)

**Expected**:
- γ-wells overlap when distance < critical radius
- Electrons shared between protons
- Molecule forms with lower total energy (E_H2 < 2×E_H)

**Success**: Stable H₂ molecule persists, binding energy measured

### Experiment 56c: Composite Dissolution

**Setup**:
- 1 Hydrogen atom (stable, at rest)
- 1 High-energy photon (directed at atom)

**Procedure**:
1. Photon collides with hydrogen
2. Energy transferred to electron
3. Monitor whether composite survives

**Expected**:
- Low energy photon: Excitation (electron to higher mode)
- Medium energy: Ionization (electron escapes, composite dissolves)
- High energy: Explosion (proton recoil, electron scatter)

**Success**: Dissolution threshold matches binding energy

### Experiment 56d: Nucleus Stability

**Setup**:
- 2 Protons + 2 Neutrons (helium-4 nucleus configuration)

**Procedure**:
1. Initialize in tight cluster
2. Run 50,000 ticks
3. Monitor: stability, internal motion, binding energy

**Expected**:
- Nucleus remains bound (Pauli exclusion prevents collapse)
- Internal orbital motion (protons/neutrons move within nucleus)
- Binding energy significantly higher than hydrogen (deeper γ-well)

**Success**: Nucleus stable, no spontaneous decay

---

## Technical Specifications

### Composite Object Data Structure

```python
@dataclass
class CompositeObject:
    composite_id: str
    composite_type: CompositeType  # HYDROGEN, H2_MOLECULE, HELIUM_NUCLEUS, etc.

    # Constituents
    constituents: List[ConstituentParticle]

    # Center of mass
    center_of_mass: np.ndarray
    total_mass: float
    total_energy: float

    # Binding
    binding_energy: float
    gamma_well_depth: float

    # Internal state
    vibrational_mode: int
    rotational_mode: int

    # Lifecycle
    formation_tick: int
    age: int
    stable: bool
```

### ConstituentParticle

```python
@dataclass
class ConstituentParticle:
    pattern: Pattern  # From Experiment 55
    relative_position: np.ndarray  # Position relative to center of mass
    velocity: np.ndarray  # Velocity in composite frame
    orbital_radius: float
    orbital_period: float
```

---

## Expected Computational Cost

**Per composite per tick**:
- γ-well computation: O(N_grid) for Poisson solve (can be cached)
- Orbital updates: O(N_constituents) for position/velocity
- Binding check: O(1) for energy comparison

**Scaling**:
- 10 composites: ~1ms per tick
- 100 composites: ~10ms per tick
- 1000 composites: ~100ms per tick

**Optimization strategies**:
- Cache γ-well fields (recompute only when composite moves)
- Use frozen structure for simple composites (no internal dynamics)
- Hierarchical updates (stable composites update less frequently)

---

## Timeline Estimate

**Week 1**: Composite structure + binding detection (Phase 3a-b)
**Week 2**: Lifecycle management + hydrogen validation (Phase 3c + Exp 56a)
**Week 3**: Molecular bonding + nucleus tests (Exp 56b-d)

**Total**: ~3 weeks for complete Phase 3

---

## Files (Planned Structure)

```
experiments/56_composite_objects/
├── README.md                       # This file
├── composite_structure.py          # CompositeObject, ConstituentParticle classes
├── binding_detection.py            # γ-well computation, binding energy
├── composite_lifecycle.py          # Formation, stability, dissolution
├── experiment_56a_hydrogen.py      # Hydrogen atom formation test
├── experiment_56b_molecular.py     # H₂ molecule bonding test
├── experiment_56c_dissolution.py   # Ionization and dissolution test
├── experiment_56d_nucleus.py       # Helium nucleus stability test
├── config.py                       # Configuration parameters
└── VALIDATION_RESULTS.md           # Results summary (to be created)
```

---

## Integration with Other Experiments

**Experiment 55 (Collision Physics)**:
- Provides merge regime that creates composite patterns
- Composite objects track what happens AFTER merge

**Experiment 52 v12 (Black Holes)**:
- Composite objects replace "ghost particles" with realistic matter
- Test: Do hydrogen atoms survive in black hole accretion disk?

**Experiment 51 v10 (Geodesics)**:
- Composites follow geodesics in gravitational field
- Internal constituents follow geodesics in composite γ-well

**Future: Chemistry Simulation**:
- Molecular bonding = shared γ-wells
- Chemical reactions = composite formation/dissolution
- Reaction rates = binding energy thresholds

---

## Open Questions

1. **What is the tick-frame equivalent of Bohr radius?**
   - Depends on γ-well strength from proton mass
   - Can we derive from first principles?

2. **Do electrons actually orbit, or are they frozen?**
   - Orbital dynamics: computationally expensive but realistic
   - Frozen structure: fast but may miss physics

3. **How does binding energy scale with composite size?**
   - Linear: E_bind ∝ N_constituents (additive)
   - Sublinear: E_bind ∝ N^(2/3) (surface effects)
   - Superlinear: E_bind ∝ N² (pairwise interactions)

4. **Can composites form composites? (Hierarchical structure)**
   - Example: Molecules are composites of atoms, which are composites of particles
   - Recursive data structure?

5. **What determines composite type from constituent list?**
   - Pattern matching: 1 proton + 1 electron → hydrogen
   - Or dynamic: any bound pair → generic "composite"?

---

## References

**Theory Documents**:
- `docs/theory/raw/054_elasticity_of_composite_objects.md` - Binding mechanisms
- `docs/theory/raw/030_collision_persistence_principle.md` - Particles as patterns
- `docs/theory/raw/053_tick_frame_collision_physics.md` - Merge regime
- `docs/theory/raw/049_temporal_ontology.md` - Temporal surfing (pattern persistence)

**Related Experiments**:
- `experiments/55_collision_physics/` - Pattern structure and three regimes ✅ VALIDATED
- `experiments/51_emergent_time_dilation/v11/` - γ-field dynamics
- `experiments/51_emergent_time_dilation/v10/` - Geodesic motion

**Real-World Analogies**:
- Quantum chemistry: Molecular orbital theory
- Nuclear physics: Shell model, liquid drop model
- Atomic physics: Bohr model, quantum mechanics

---

**This experiment bridges collision physics (Exp 55) with matter structure (atoms, molecules, nuclei).**

Success here would enable:
- Realistic chemistry simulation
- Molecular dynamics
- Material properties (elasticity, viscosity)
- Life-like structures (self-replicating patterns)

Failure or partial results would:
- Reveal limitations of γ-well binding model
- Guide refinement of composite theory
- Identify which scales work vs which need revision

**Either way → progress toward tick-frame matter physics.**

---

## Version Roadmap (2026-01-22 to 2026-01-24)

### ✅ V1-V3: Development and Initial Validation

**V1**: Initial composite structure (2D, failed)
**V2**: Single-particle gradient-following (2D, failed)
**V3**: 50 fragments, 10k ticks (2D, appeared successful but incomplete - 3.43% drift)

### ✅ V4: 200k Tick Quantization Study (COMPLETE - SUCCESS)

**Date**: 2026-01-23 to 2026-01-24
**Status**: SUCCESS - 2D fragmented cloud STABLE with optimal parameters
**Key Results**:
- ✓ 200k tick stability: 6.52% drift, 1.43% energy conservation, 0/50 escapes
- ✓ Optimal parameters: jitter=0.0005, collision_radius=0.5
- ✓ "Neutrino vs Electron" breakthrough (collision parameters → particle types)
- ⚠ Quantization: PARTIAL (3 radial shells detected, no energy gaps)

**Validated Parameters**:
- `jitter_strength = 0.0005` (0.001 causes runaway - energy balance critical)
- `collision_radius = 0.5` (electron-like, ~5 collisions/tick)

**Documents**:
- `v4/PHASE_4_V4_RESULTS.md` - Complete experimental story
- `v4/ENERGY_DIAGNOSTIC_BREAKTHROUGH.md` - Energy diagnostic success
- `v4/CHECKLIST.md` - Validated parameters
- `v4/results/quantization_analysis_200k_results.json` - Quantization analysis

### 🔢 V5: Integer Arithmetic Conversion (PLANNED)

**Date**: 2026-01-24
**Status**: DESIGN COMPLETE - Ready for implementation
**Goal**: Convert V4 physics to scaled integer arithmetic (eliminate float drift)

**Scaling Factor**: 10^8 (100 million)
- Preserves 8 decimal places for all critical parameters
- Most critical: `jitter_strength = 0.0005` → `50,000` (validated precision)
- Avoids overflow (max values ~200M vs 64-bit limit ~9×10^18)

**Benefits**:
- ✓ **Perfect determinism**: Bit-exact results across all platforms
- ✓ **Zero accumulation errors**: Integer arithmetic is exact
- ✓ **Improved energy conservation**: Target <0.5% drift (vs 1.43% in V4)
- ✓ **2-5× faster**: Integer operations outperform float
- ✓ **Foundation for V6/V7**: Perfect reproducibility for collision experiments

**Implementation Phases**:
1. Fixed-point utility module (multiply, divide, sqrt)
2. Fragment dynamics (positions, velocities, energies)
3. Collision physics (exact energy conservation)
4. Random number generation (integer Gaussian for jitter)
5. Validation against V4 200k baseline

**Documents**:
- `v5/README.md` - Complete design specification and implementation plan

### 🚀 V6: Particle Accelerator Experiments (PLANNED)

**Date**: 2026-01-24
**Status**: DESIGN PENDING - Awaiting V5 integer foundation
**Based on**: V5 integer arithmetic for perfect determinism
**Goal**: Non-equilibrium collision experiments (projectile bombardment)

**Concept**: "Shoot the Stabilized Atom"
- **Projectile patterns**: High/low speed fragments fired at stable cloud
- **Variable energies**: Test scattering, excitation, ionization thresholds
- **Precise targeting**: Control impact parameter, angle, timing
- **Perfect measurement**: Track every fragment at every tick (deterministic from V5)

**Advantages of Integer Foundation**:
- ✓ **Perfect repeatability**: Exact collision trajectories guaranteed
- ✓ **Zero drift**: Million-tick simulations possible
- ✓ **Faster parameter scans**: 2-5× speedup from integer arithmetic
- ✓ **Exact energy accounting**: Track energy transfer with zero error

**Comparisons with Real Physics**:
- Rutherford scattering (alpha particles on gold foil)
- Deep inelastic scattering (electron structure probes)
- Ionization cross-sections (energy thresholds)
- Compton scattering (low vs high energy regimes)

**Documents**:
- `v6/README.md` - Conceptual overview and experimental design

### ⏸️ V7: Dual-Parameter Collision System (DEFERRED)

**Date**: Planned
**Status**: DEFERRED - Awaiting V5 integer arithmetic foundation
**Goal**: Separate collision detection from collision outcome

**Innovation**: Two independent parameters
1. **`collision_radius`**: Spatial detection (WHEN to check collision)
2. **`pattern_overlap_threshold`**: Pattern similarity (WHAT happens - merge/explosion/excitation)

**Physics Motivation**:
- V4 conflates detection with outcome (single parameter does both)
- Real physics: interaction cross-section ≠ interaction type
- Enables particle type differentiation (neutrino-like, electron-like, nuclear-like)

**Three Collision Regimes** (from Experiment 55):
- **High overlap** (> 0.8): Merge (fusion, energy release)
- **Low overlap** (< 0.2): Explosion (annihilation, scatter)
- **Medium overlap** (0.2-0.8): Excitation (energy redistribution, elastic)

**Deferral Rationale**: Will implement on V5 integer base for perfect determinism and zero accumulation errors.

**Documents**:
- `v7/README.md` - Detailed specification (awaiting V5)

### ⏸️ vX_3d: 3D Fragmented Cloud (DEFERRED)

**Date**: Originally planned as V5, renamed 2026-01-24
**Status**: DEFERRED - Not needed after V4 success
**Reason**: 2D proven stable with correct parameters (200k validation PASSED)

**Why 3D might still be valuable** (future work):
- Full angular momentum vector (Lx, Ly, Lz) vs scalar L_z
- 3D collision phase space (potentially better thermalization)
- More realistic physics (theory suggests 3D minimum per Doc 015_01)
- Required for multi-electron atoms (if 2D proves insufficient)

**Current priority**: V6 (integer conversion) → V7 (accelerator) → V5 (dual-parameter) → vX_3d (when/if needed)

**Documents**:
- `vX_3d/README.md` - 3D implementation plan (deferred)

---

## Current State Summary (2026-01-24)

**Validated Foundation (V4)**:
- ✅ 2D fragmented electron cloud IS STABLE (200k ticks)
- ✅ Optimal parameters identified and documented
- ✅ Shell structure observed (3 radial peaks)
- ⚠ Full quantization not yet achieved (partial 1/4 signatures)

**Path Forward**:
1. **Immediate**: V4 quantization analysis complete (shells detected)
2. **Next**: V5 dual-parameter collision system (enables particle type modeling)
3. **Future**: V6 particle accelerator (non-equilibrium physics)
4. **Optional**: vX_3d 3D extension (when/if needed for full quantization)

**Key Lesson**: Energy balance is critical - jitter injection must be less than collision dissipation. The "neutrino vs electron" insight shows collision parameters determine interaction strength, not just detection threshold.
