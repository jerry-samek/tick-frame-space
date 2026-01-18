# Next Experiments: Gravity/Relativity Validation Suite (#52-55)

**Date**: January 2026 (Original Plan)
**Status**: **PARTIALLY COMPLETE** - Experiments diverged from this plan
**Based on**: Experiment #51 v9 validation (r ≈ 0.999 correlation)

---

## ⚠️ IMPORTANT: ACTUAL IMPLEMENTATION DIVERGED FROM THIS PLAN

**Original Plan** (this document): Experiments #52-55 as gravity/relativity validation

**What Actually Happened**:
- ✅ **#53 (v10)**: Geodesics - **COMPLETED** exactly as planned - 100% success!
- ⚠️ **#52 (v11)**: Black Holes - **COMPLETED** with ghost particle limitation (c-ring discovery at r≈10.1)
- ❌ **#54 (v12)**: Length Contraction - **NOT YET IMPLEMENTED** (deferred)
- 🔀 **#55**: **DIVERGED** - Instead of "Observer-Dependent Horizons", implemented **Collision Physics** (three regimes + emergent Pauli exclusion!)
- 🆕 **#56**: **NEW** - Composite Objects (atoms/molecules) - not in original plan
- 🔄 **#57**: Observer-Dependent Horizons renumbered (was #55, now awaiting implementation)

**Why the Divergence**:
After v10/v11 success, research naturally pivoted to collision physics (Docs 053-060) based on theoretical developments. This opened a new research direction (composite objects, matter-antimatter asymmetry) that took priority over completing the original gravity/relativity suite.

**See**:
- `experiments/55_collision_physics/` - What #55 actually became
- `experiments/56_composite_objects/` - New experiment not in this plan
- `docs/theory/proposed_experiments_gravity_relativity.md` - Updated with actual results

---

## Context

### V9 Achievement

Experiment 51 v9 successfully validated **combined gravitational + special relativistic time dilation**:

- ✅ r ≈ 0.999 correlation between predicted and measured γ_total
- ✅ 100% validation rate at 0.1c, 0.5c
- ✅ 90% validation rate at 0.9c
- ✅ Multiplicative combination γ_total = γ_grav × γ_SR emerged naturally (not programmed!)

### Critical Observation

**Stationary entities immediately collapsed into the gravitational source!**

This is crucial evidence that:

1. The field gradient creates real attraction (not just rendering artifact)
2. Velocity is required for stable orbits (exactly like real gravity)
3. Black hole formation might be natural consequence of high load saturation
4. Geodesic motion might emerge from following time gradients

---

## Strategic Goals

### Objective

Complete experiments #52-55 to **definitively validate or falsify** whether tick-frame physics can reproduce GR/SR from
computational substrate alone.

### Scope Decision

- **Current scale**: ~700 entity "planet" (atomic-scale analog)
- **Approach**: Prove mechanism works at ANY scale → physics validity
- **Scale testing**: Future work after mechanism validated
- **v3 definition**: New research direction (QM, observer, cosmology) after gravity/relativity arc complete

### Success Criteria

If ALL experiments succeed → Tick-frame validated as alternative ontology to GR/SR
If ANY experiment fails → Identify failure mode, document limitations

---

## Experiment #53: Emergent Geodesics (v10)

### Priority

**HIGHEST** - V9 collapse strongly suggests this will work

### Hypothesis

Entities naturally follow geodesics (curved paths) by following time-flow gradients, without any force laws programmed.

### Implementation Plan

**Setup**:

1. Copy v9 codebase → `v10/` directory
2. Remove forced circular trajectories from `entity_motion.py`
3. Keep validated field parameters: α=0.012, γ=0.0005, scale=0.75, R=1.2, E_max=15

**New Physics - Gradient Following**:

```python
def update_velocity_gradient_following(entity, fields, dt, coupling_constant=1.0):
    """
    Entity seeks direction of increasing γ_eff (faster proper time).
    This is the geodesic equation in disguise.
    """
    # Compute time-flow gradient at entity position
    gamma_gradient = compute_gamma_gradient(entity.position, fields)

    # Acceleration follows gradient (entities seek faster time)
    acceleration = coupling_constant * gamma_gradient

    # Update velocity and position
    entity.velocity += acceleration * dt
    entity.position += entity.velocity * dt

    # Enforce speed limit c=1.0
    speed = np.linalg.norm(entity.velocity)
    if speed > 1.0:
        entity.velocity *= 1.0 / speed
```

**Test Configuration**:

- 700 stationary entities (planet cluster at center)
- 20 mobile entities with random initial conditions:
    - Positions: r = 30, 35, 40, 45 (distributed)
    - Velocities: 0.1c - 0.5c (random directions)
- Run 5000 ticks
- Track all trajectories

### Success Criteria

**Qualitative**:

- ✅ Circular or elliptical orbits emerge naturally
- ✅ Entities don't all collapse (some achieve stable orbits)
- ✅ Entities don't all escape (gradient creates binding)
- ✅ Orbital shapes match expectations (closed curves)

**Quantitative**:

- ✅ Orbital velocity v ≈ √(GM/r) within 20%
- ✅ Orbital period T² ∝ r³ (Kepler's third law) within 20%
- ✅ Escape velocity v_escape ≈ √(2GM/r) within 20%
- ✅ Energy conservation: E = KE + PE remains constant per orbit (within 10%)

### If It Fails

- Geodesics don't emerge → Need explicit force laws
- Mechanism doesn't work without programming orbits
- **STOP HERE** - No point continuing to #52, #54, #55
- Document failure mode and conclude tick-frame requires forces

### Estimated Effort

2-3 days (gradient computation, parameter tuning, trajectory analysis)

---

## Experiment #52: Black Hole Event Horizons (v11)

### Priority

**SECOND** - Only if #53 succeeds

### Hypothesis

Event horizons form naturally at extreme load saturation, with no singularities inside (substrate continues updating).

### Implementation Plan

**Setup**:

1. Copy v10 codebase → `v11/` directory
2. Increase planet mass 10× (7,000 entities instead of 700)
3. Increase field source strength proportionally (scale = 7.5)
4. Use validated gradient-following physics from v10

**Test Configuration**:

- 7,000 stationary entities (massive planet cluster)
- 40 test entities at various distances: r = 10, 15, 20, 25, 30, 35, 40, 45, 50, 60
- Various initial velocities: stationary, 0.3c, 0.5c, 0.7c
- Run 10,000 ticks to observe long-term behavior

### Success Criteria

**Event Horizon Formation**:

- ✅ Critical radius r_horizon exists where γ_grav → ∞ (field saturates)
- ✅ r_horizon ≈ 2GM/c² within 30% (emergent Schwarzschild radius!)
- ✅ Behavior changes sharply at r = r_horizon

**Inside Horizon (r < r_horizon)**:

- ✅ Entities rapidly collapse toward center
- ✅ γ_eff → 0 (observer loses ability to track)
- ✅ Escape impossible (all trajectories lead inward)
- ✅ **Substrate continues updating** (no singularity in physics!)

**Outside Horizon (r > r_horizon)**:

- ✅ Stable orbits possible (with sufficient velocity)
- ✅ Escape possible (with v > v_escape)
- ✅ Smooth time dilation (no discontinuity)

**At Horizon (r ≈ r_horizon)**:

- ✅ Asymptotic approach (entities slow down, time appears to freeze)
- ✅ Photon orbit radius (light can orbit at r ≈ 1.5 r_s)

### If It Fails

- No natural horizon forms OR
- Horizon requires ad-hoc cutoffs OR
- Behavior doesn't match GR predictions
- → Black hole claim falsified

### Estimated Effort

3-4 days (saturation testing, horizon detection, long simulations)

---

## Experiment #54: Length Contraction (v12)

### Priority

**THIRD** - Tests spatial SR effects (time dilation already validated)

### Hypothesis

Length contraction emerges from sparse sampling of fast-moving objects, matching Lorentz formula L' = L√(1-v²/c²).

### Implementation Plan

**Setup**:

1. Create new `v12/` directory (simpler than v10/v11)
2. No gravity field needed (flat space test)
3. Focus on pure special relativistic effects

**Test Configuration**:

**Scenario 1: Rest Frame Measurement**

- Place 2 entities A and B separated by d = 40 units
- Both stationary in substrate frame
- Measure separation: should be d_rest = 40

**Scenario 2: Moving Frame Measurement**

- Same entities A and B
- Observer moving at velocity v = 0.5c relative to substrate
- Observer measures separation d_moving
- Expected: d_moving = d_rest × √(1 - v²/c²) = 40 × √(1 - 0.25) = 40 × 0.866 = 34.6

**Scenario 3: Reciprocity Test**

- Entity C moves at v = 0.8c
- Measures separation between stationary entities D and E
- Entity D measures separation of moving entity C's "length"
- Both should see contraction (validates relativity principle)

### Success Criteria

**Quantitative**:

- ✅ Measured contraction matches Lorentz formula within 15%
- ✅ Effect scales correctly with velocity (test v = 0.3c, 0.5c, 0.7c, 0.9c)
- ✅ Reciprocal (both frames see contraction of the other)

**Qualitative**:

- ✅ No preferred frame (SR relativity principle holds)
- ✅ Effect emerges from sampling, not programmed
- ✅ Combines correctly with time dilation

### If It Fails

- Spatial effects don't match SR
- Time dilation works but not full relativity
- → Partial validation only

### Estimated Effort

2-3 days (requires observer frame implementation)

---

## Experiment #55: Observer-Dependent Horizons (v13)

### Priority

**FOURTH** - Most ambitious, tests distinctive prediction

### Hypothesis

Event horizon radius varies with observer capacity (tick_budget_capacity), making horizons observer-dependent rather
than objective.

**This is a DISTINCTIVE PREDICTION that differs from GR!**

### Implementation Plan

**Setup**:

1. Copy v11 codebase → `v13/` directory
2. Implement an explicit observer model with tick_budget_capacity
3. Use the same massive planet (7,000 entities) from v11

**Observer Implementation**:

```python
class Observer:
    def __init__(self, capacity):
        self.tick_budget_capacity = capacity
        self.tracked_entities = {}

    def observe_tick(self, all_entities, substrate_tick):
        """
        Observer can only track entities whose tick_budget sum <= capacity.
        Entities beyond capacity are 'beyond the horizon'.
        """
        available_budget = self.tick_budget_capacity
        tracked = []

        # Sort by distance (closest first)
        sorted_entities = sorted(all_entities, key=lambda e: distance_to_observer(e))

        for entity in sorted_entities:
            if available_budget >= entity.tick_budget:
                tracked.append(entity)
                available_budget -= entity.tick_budget
            else:
                # Beyond horizon for this observer
                break

        return tracked
```

**Test Configuration**:

- Observer A: capacity = 5000 ticks/tick
- Observer B: capacity = 10000 ticks/tick
- Same black hole (7,000 entity planet)
- Measure horizon radius seen by each

### Success Criteria

**Observer-Dependent Horizon**:

- ✅ Observer A sees a horizon at r_A
- ✅ Observer B sees a horizon at r_B
- ✅ r_A > r_B (lower capacity → larger horizon)
- ✅ Relationship: r_horizon ∝ 1/capacity (inverse)

**Substrate Independence**:

- ✅ Substrate continues updating everywhere
- ✅ Entities inside Observer A's horizon are still tracked by Observer B
- ✅ No objective horizon exists (unlike GR!)

**Distinctive Prediction**:

- This **differs from GR** where event horizons are objective
- Provides testable way to distinguish tick-frame from GR
- If confirmed in reality → validates tick-frame ontology

### If It Fails

- Horizons are objective (same for all observers)
- Observer capacity doesn't affect horizon
- → GR is correct, tick-frame is wrong about observer dependence

### Estimated Effort

4-5 days (observer model, capacity testing, multiple runs)

---

## Implementation Order and Dependencies

```
v9 (validated)
  ↓
  ├─→ v10 (Experiment #53 - Geodesics) ← START HERE
  │     ↓
  │     ├─ SUCCESS → Continue to v11
  │     └─ FAIL → STOP (no point continuing)
  │
  ├─→ v11 (Experiment #52 - Black Holes) ← Requires v10 success
  │     ↓
  │     ├─ SUCCESS → Continue to v12
  │     └─ FAIL → Document limitation
  │
  ├─→ v12 (Experiment #54 - Length Contraction) ← Independent path
  │     ↓
  │     ├─ SUCCESS → Continue to v13
  │     └─ FAIL → Partial validation (time but not space)
  │
  └─→ v13 (Experiment #55 - Observer Horizons) ← Requires v11 + v12
        ↓
        ├─ SUCCESS → FULL VALIDATION! Move to v3 (new research)
        └─ FAIL → GR is correct on this point
```

---

## Documentation Requirements

After each experiment, update:

1. **Create version RESULTS.md**:
    - `v10/RESULTS.md` - Geodesic findings
    - `v11/RESULTS.md` - Black hole findings
    - `v12/RESULTS.md` - Length contraction findings
    - `v13/RESULTS.md` - Observer horizon findings

2. **Update EXPERIMENTAL_ARC.md**:
    - Add new version section
    - Update conclusion with cumulative findings

3. **Update honest_status.md**:
    - Move validated claims from "Unvalidated" to "Validated"
    - Update risk assessments
    - Update "Is This Real Physics?" scores

4. **Update experiment_index.md**:
    - Add experiments #52-55 entries
    - Update validation statistics

5. **Update proposed_experiments_gravity_relativity.md**:
    - Mark experiments complete
    - Document results

---

## Timeline Estimate

| Experiment               | Estimated Time | Cumulative   |
|--------------------------|----------------|--------------|
| #53 (Geodesics)          | 2-3 days       | 3 days       |
| #52 (Black Holes)        | 3-4 days       | 7 days       |
| #54 (Length Contraction) | 2-3 days       | 10 days      |
| #55 (Observer Horizons)  | 4-5 days       | 15 days      |
| **Total**                | **12-15 days** | **~3 weeks** |

This assumes focused work without interruptions. Includes implementation, simulation runs, analysis, and documentation.

---

## Scale Considerations

### Current Approach (Validated)

- **700 entities** = "planet" (atomic-scale analog)
- **Sufficient** to test mechanism validity
- If mechanism works at ANY scale → real physics

### Why This Works

1. Physics principles should be scale-invariant
2. Gravitational time dilation ratio should match regardless of absolute mass
3. Geodesic curvature should emerge at any energy scale
4. Event horizon formation should follow same r_s ∝ M relationship

### Future Scale Testing (Post-v3)

- Scale to 10⁶ entities (realistic mass ratios)
- Test if same parameters work at macro scale
- Becomes engineering/performance challenge, not physics question

---

## Success Scenarios

### Scenario 1: Full Validation (Best Case)

**If all experiments #52-55 succeed**:

- ✅ Tick-frame physics validated as a complete alternative to GR/SR
- ✅ Gravity emerges from the computational substrate (no forces needed)
- ✅ Makes distinctive predictions (observer-dependent horizons)
- ✅ Ready for v3: New research directions
    - Quantum mechanics emergence
    - Observer/consciousness implementation
    - Cosmological expansion
    - Energy conservation refinements

### Scenario 2: Partial Validation

**If some experiments succeed, others fail**:

- Identify what works vs. what doesn't
- Document boundary conditions of validity
- Refine theory to match observations
- v3 focuses on fixing failures or exploring working parts

### Scenario 3: Mechanism Failure

**If #53 (geodesics) fails**:

- Mechanism doesn't work without explicit forces
- Document as computational artifact
- v3 becomes a different project (not physics)
- Still valuable as simulation technique

---

## Next Actions

1. **Implement v10 (Geodesics)** - highest priority
2. **If v10 succeeds**: Implement v11 (Black Holes)
3. **If v11 succeeds**: Implement v12 (Length Contraction) + v13 (Observer Horizons)
4. **Update documentation** after each experiment
5. **Make decision** about v3 based on cumulative results

---

**Document Status**: Ready to implement
**Approval**: Plan approved January 2026
**Contact**: See CLAUDE.md for implementation guidance
