# Experiment 52 (V13): Black Hole with Full Collision Physics

**Date**: January 2026
**Status**: In Development
**Based on**: V12 (supermassive field) + Experiment 55 (three-regime collision physics)

---

## Critical Improvement Over V12

**V12 FAILED** - C-ring dispersed, conservation laws violated (energy tripled!)

**V13 INTEGRATES FULL COLLISION PHYSICS:**
- ✅ Pattern overlap computation (Doc 053)
- ✅ Three collision regimes (merge/explode/excite)
- ✅ Cell capacity limits (E_max = 15.0)
- ✅ Proper energy conservation
- ✅ Composite object formation potential

---

## Key Question

**What black hole structure emerges with realistic collision physics?**

### Possible Outcomes

1. **Accretion Disk**: Matter spirals inward, collides, forms disk structure
2. **Stable Structures**: Composites form at specific radii (like planetary systems)
3. **Jet Formation**: Explosion regime creates outflows at poles
4. **Event Horizon Behavior**: Matter crosses critical radius, different physics inside/outside
5. **Total Dispersion**: Like v12, but with energy conservation

---

## Experimental Setup

### Supermassive Black Hole (same as v12)

**Central Mass**:
- **Count**: 70,000 stationary entities
- **Radius**: 10 units
- **Mass multiplier**: 100×
- **Field strength**: scale = 75.0
- **Allow divergence**: True (gamma → ∞)

**Expected Features**:
- Strong gamma-well (time dilation)
- Event horizon analog at r ≈ 10-15
- Gravitational acceleration increases inward

### Test Particles

**Initial Distribution**:
- **Distances**: r = 15, 20, 25, 30, 35, 40, 50, 60
- **Velocities**: v = 0.0c, 0.1c, 0.3c, 0.5c (tangential)
- **Count**: 4 entities per distance = 32 total

**Particle Types** (from Experiment 55):
- PROTON (mass=1.0, energy=10.0)
- ELECTRON (mass=0.001, energy=5.0)
- Mix of both for collision diversity

### Collision Physics (Experiment 55 Framework)

**Three Regimes**:

**1. Merge (E_total ≤ E_max, minimal overlap)**:
- Two patterns → composite pattern
- E_composite = E_A + E_B (exact conservation)
- Example: Proton + electron → hydrogen-like composite

**2. Explode (E_total > E_max OR high overlap)**:
- Patterns fragment/scatter
- E_overflow distributed to neighbors (shockwave)
- Example: High-velocity collision → particle shower

**3. Excite (partial overlap, E_total ≤ E_max)**:
- Energy redistribution within patterns
- Patterns gain internal modes
- Example: Glancing collision → excited states

**Cell Capacity**: E_max = 15.0 (same as field E_max)

### Field Parameters (same as v12)

- α (diffusion): 0.012
- γ (damping): 0.0005
- scale (source): 75.0 (10× baseline)
- R (regeneration): 1.2
- E_max (capacity): 15.0
- allow_divergence: True

### Simulation Duration

- **Ticks**: 5000
- **Snapshot interval**: 100 ticks
- **Collision tracking**: Every tick

---

## Success Criteria

### Conservation Laws ✅

**MUST PASS** (unlike v12):
- ✅ Momentum conservation: |dp| < 0.01 at all times
- ✅ Energy conservation: |dE| < 0.01 (excluding field work)
- ✅ Pattern count tracking: created + destroyed = net change

### Physical Outcomes

**Qualitative**:
- ✅ Simulation remains stable with full collision physics
- ✅ Collision regime distribution makes sense (merge at low r, explode at high v)
- ✅ Clear structure emerges (or clear null result)

**Quantitative**:
- Track radial distribution of entities over time
- Measure collision frequencies by regime
- Identify stable radii (if any)
- Compare with v11 ghost particle behavior
- Compare with GR predictions (accretion disk, photon sphere)

---

## Key Improvements from V12

### 1. Pattern-Based Entities

V12: Point particles with velocity
V13: **Pattern objects** with internal structure (type, energy, mode, phase)

This enables:
- Merge regime → composite formation
- Pattern overlap → different collision outcomes
- Internal modes → excitation physics

### 2. Energy Conservation

V12: Energy **tripled** (1.58 → 5.19) - UNPHYSICAL!
V13: **Exact conservation** via:
- Collision outcome enforces E_in = E_out
- Overflow energy distributed to neighbors (no loss)
- Field work accounted for separately

### 3. Cell Capacity Limits

V12: Unlimited density (many entities per cell)
V13: **E_max = 15.0** limit
- Prevents unphysical density buildup
- Triggers explosion regime when exceeded
- Models Pauli exclusion-like physics

### 4. Composite Formation

V12: No structure beyond individual particles
V13: **Merge regime creates composites**
- Can form bound states (atoms, molecules)
- Enables chemistry-like emergence
- Potential for complex structures

---

## Expected Physics

### Near Event Horizon (r < 15)

**High gamma (time dilation)**:
- Entities experience slower computational time
- Gravitational acceleration pulls matter inward
- High-velocity collisions likely

**Expected Regime**: **Explosion**
- E_total likely exceeds E_max
- Overlap energy high (fast collisions)
- Shockwaves and fragmentation

**Analogy**: Accretion disk turbulence, jet formation

### Intermediate Zone (15 < r < 30)

**Moderate gamma**:
- Orbital motion possible
- Mix of collision regimes

**Expected Regime**: **Mix of Merge + Excite**
- Slower collisions → merge
- Tangential collisions → excite
- Composite formation likely

**Analogy**: Planetary formation zone

### Outer Zone (r > 30)

**Weak gamma**:
- Nearly flat spacetime
- Low collision frequency

**Expected Regime**: **Merge (if any collisions)**
- Low-energy collisions
- Composites persist

**Analogy**: Outer solar system, Kuiper belt

---

## Comparison with Related Experiments

### V11 (Ghost Particles)

- ✅ Found c-ring at r ≈ 10.1
- ❌ Artifact (entities pass through each other)

### V12 (Minimal Collisions)

- ✅ Tested collision physics
- ❌ C-ring dispersed
- ❌ Conservation violated
- ❌ Minimal framework insufficient

### V13 (Full Collisions)

- ✅ Proper collision regimes
- ✅ Energy conservation
- ✅ Composite formation
- ❓ **TO BE DETERMINED**: What structure emerges?

---

## Integration Strategy

### Code Reuse

**From V12** (`experiments/51_emergent_time_dilation/v12/`):
- `field_dynamics.py` - Field evolution (L, E, gamma)
- `entity_motion.py` - Basic entity structure (position, velocity)
- `config.py` - Configuration system

**From Experiment 55** (`experiments/55_collision_physics/`):
- `pattern_overlap.py` - Pattern class, overlap calculation
- `collision_regimes.py` - Three regime framework
- `experiment_55_validation.py` - Validation tests

**New for V13**:
- `experiment_52_v13.py` - Main simulation loop
- `entity_adapter.py` - Convert MovingEntity ↔ Pattern
- `black_hole_analysis.py` - Structure analysis tools

### Entity Representation

**Challenge**: V12 uses `MovingEntity`, Exp 55 uses `Pattern`

**Solution**: Create adapter class:
```python
class PatternEntity:
    """Entity that carries a Pattern and moves in field."""
    pattern: Pattern  # From Exp 55
    position: np.ndarray
    velocity: np.ndarray
    tick_budget: int

    def to_pattern(self) -> Pattern:
        return self.pattern

    def from_collision_outcome(outcome: CollisionOutcome):
        # Create PatternEntity from collision result
        ...
```

---

## Timeline

**Week 1** (Current):
- Day 1: Adapt Exp 55 framework to v12 field system ✓
- Day 2: Implement PatternEntity and collision integration
- Day 3: Test conservation laws in simple scenarios

**Week 2**:
- Day 4: Run full black hole simulation (5000 ticks)
- Day 5: Analyze structure, create visualizations
- Day 6: Document results, compare with v12
- Day 7: Write RESULTS.md

---

## Files Structure

```
experiments/51_emergent_time_dilation/v13/
├── README.md                    # This file
├── experiment_52_v13.py         # Main simulation
├── entity_adapter.py            # MovingEntity ↔ Pattern conversion
├── black_hole_analysis.py       # Structure analysis tools
├── config.py                    # Configuration (extends v12)
├── field_dynamics.py            # Copied from v12 (no changes)
├── entity_motion.py             # Extended from v12 (adds Pattern support)
├── collision_integration.py    # Integrates Exp 55 into field simulation
├── RESULTS.md                   # To be created after run
└── plots/                       # Visualizations
    ├── radial_distribution.png
    ├── collision_regime_map.png
    ├── energy_conservation.png
    └── structure_evolution.png
```

---

## Open Questions

1. **Does an accretion disk emerge?**
   - Radial structure with orbital motion?
   - Energy dissipation via collisions?

2. **What role does explosion regime play?**
   - Creates outflows (jets)?
   - Prevents density buildup near horizon?

3. **Do composites form?**
   - Stable bound states at certain radii?
   - Chemistry-like emergence?

4. **Is there a characteristic radius?**
   - Like v11's r ≈ 10.1, but now with proper physics?
   - Corresponds to event horizon, photon sphere, or ISCO?

5. **How does this compare to GR?**
   - Schwarzschild black hole predictions
   - Accretion disk theory
   - Distinctive tick-frame features?

---

## Success Conditions

### Minimal Success

✅ Simulation runs to completion (5000 ticks)
✅ Energy/momentum conserved (|error| < 1%)
✅ Collision framework works without crashes

### Good Success

✅ Clear structure emerges (accretion disk, stable radii, etc.)
✅ Physics makes sense (regime distribution matches expectations)
✅ Quantitative analysis yields insights

### Excellent Success

✅ Distinctive tick-frame prediction (differs from GR)
✅ Testable prediction for real black holes
✅ Beautiful emergent structure from simple rules

### Null Result (Also Valuable!)

✅ Complete dispersion (like v12 but with conservation)
✅ No stable structures
✅ **Conclusion**: Black hole environment too violent for structure

**Either way, we learn something definitive!**

---

**Let's find out what tick-frame black holes really look like.**
