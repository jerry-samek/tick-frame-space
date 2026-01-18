# Experiment 52 (V12): Black Holes with Minimal Collision Physics

**Date**: January 2026
**Status**: In Development
**Based on**: Experiment 52 v11 (black hole event horizons) + minimal collision physics

---

## ⚠️ Important Note: Simplified Collision Model

**This experiment uses a MINIMAL collision framework** to validate whether the stable c-speed ring observed in v11 survives with basic collision physics.

### What V12 Implements

✅ **Collision detection**: Entities in same grid cell
✅ **Elastic scattering**: Hard-sphere approximation
✅ **Momentum conservation**: Basic 2D elastic collision
✅ **Speed limit enforcement**: v ≤ c

### What V12 Does NOT Implement

❌ **Pattern overlap computation** (from Doc 053)
❌ **Cell capacity limits** (no explosion regime)
❌ **Energy overflow propagation** (no shockwaves)
❌ **Pattern merging** (no fusion/chemistry)
❌ **Composite object binding** (from Doc 054)
❌ **Pauli exclusion** (no degeneracy pressure)
❌ **Three collision regimes** (merge/explode/excite from Doc 053)

### For Full Collision Physics

See **Experiment 55 (Collision Physics Framework)** which will implement:
- All three collision regimes (Doc 053)
- Pattern overlap algorithms
- Cell capacity and energy overflow
- Composite object formation (Doc 054)
- Complete elasticity framework

---

## Key Question

**Does the stable c-speed ring (v11 iteration 3) survive with realistic collision physics?**

### Possible Outcomes

1. **Ring survives** → Validates tick-frame prediction (distinctive vs GR)
2. **Ring disperses** → Ghost particle artifact confirmed
3. **Ring transforms** → New physics emerges (e.g., accretion disk)

---

## Comparison with V11

| Feature | V11 (Ghost Particles) | V12 (Minimal Collisions) |
|---------|----------------------|--------------------------|
| Collision detection | ❌ None | ✅ Same cell check |
| Entity interaction | ❌ Pass through each other | ✅ Elastic scattering |
| Momentum conservation | ❌ Independent motion | ✅ Conserved in collisions |
| Overlap handling | ❌ Unlimited density | ⚠️ Scattering only (no capacity limit) |
| Pattern structure | ❌ Point particles | ❌ Point particles (same) |
| Composite objects | ❌ No binding | ❌ No binding (same) |

---

## Experimental Setup

Same as v11 iteration 3:

### Supermassive Planet
- **Count**: 70,000 stationary entities
- **Radius**: 10 units
- **Mass**: 100× baseline (10× from v11 iteration 2)
- **Field strength**: scale = 75.0

### Test Entities
- **Distances**: r = 10, 15, 20, 25, 30, 35, 40, 50, 60
- **Velocities**: v = 0.0c, 0.1c, 0.3c, 0.5c
- **Total**: 36 test entities

### Field Parameters
- α (diffusion): 0.012
- γ (damping): 0.0005
- scale (source): 75.0
- R (regeneration): 1.2
- E_max (capacity): 15.0

### Simulation Duration
- 5000 ticks
- Snapshot every 100 ticks

---

## Success Criteria

### Qualitative

✅ Simulation remains stable with collisions enabled
✅ Momentum/energy conserved (or systematic behavior documented)
✅ Clear outcome: ring survives vs disperses vs transforms

### Quantitative

✅ Compare c-ring properties with v11:
   - Radius (r ≈ 10.1 in v11)
   - Thickness (single-entity thin in v11)
   - Stability over time
   - Orbital speeds (v ≈ c in v11)

✅ Track collision statistics:
   - Number of collisions per tick
   - Momentum conservation (should be exact)
   - Energy conservation (elastic → conserved)

---

## Implementation Notes

### Collision Physics Module

**File**: `collision_physics.py`

**Classes**:
- `CollisionDetector`: Detects entities in same grid cell
- `ElasticScatteringResolver`: Resolves 2D elastic collisions
- `CollisionEvent`: Records collision metadata

**Key Function**:
```python
process_collisions(entities, detector, resolver, tick)
```

### Integration into Main Loop

```python
# After entity motion update, before field update
entities = process_collisions(entities, detector, resolver, tick)
```

---

## Running the Experiment

```bash
cd experiments/51_emergent_time_dilation/v12

# Run with default configuration (100× mass, collisions enabled)
python experiment_52_v12.py

# Monitor collision statistics
tail -f collision_log.txt
```

---

## Expected Computational Cost

**V11 (ghost particles)**: ~10 minutes for 5000 ticks
**V12 (with collisions)**: ~15-20 minutes (collision detection overhead)

**Collision complexity**:
- Worst case: O(N²) if all entities in one cell
- Typical case: O(N) with spatial hashing (grid already provides this)

---

## Validation Checklist

Before considering results valid:

- [ ] Momentum conserved every tick (check diagnostics)
- [ ] Energy conserved every tick (elastic collisions)
- [ ] No entities exceed c (speed limit enforcement)
- [ ] Collision count scales reasonably with density
- [ ] Results reproducible (deterministic simulation)

---

## Next Steps After V12

### If C-Ring Survives
- Document as validated distinctive prediction
- Update Doc 052 (Black Hole Behavior) with collision-validated results
- Proceed to Experiment 54 (Length Contraction) or 55 (Observer Horizons)

### If C-Ring Disperses
- Confirm ghost particle artifact
- Analyze dispersion mechanism (radial vs tangential scattering)
- Determine if Experiment 55 (full collision framework) needed

### If New Behavior Emerges
- Document unexpected phenomena (e.g., accretion disk formation)
- Analyze mechanism
- Consider implications for black hole theory

---

## Files

- **collision_physics.py**: Minimal collision framework
- **experiment_52_v12.py**: Main simulation (to be created)
- **entity_motion.py**: Same as v11
- **field_dynamics.py**: Same as v11
- **config.py**: Same as v11
- **README.md**: This file

---

## References

**Theory Documents**:
- `docs/theory/raw/052_black_hole_behavior_tick_frame.md` - Black hole theory (ghost particle limitation documented)
- `docs/theory/raw/053_tick_frame_collision_physics.md` - Full collision framework (three regimes)
- `docs/theory/raw/054_elasticity_of_composite_objects.md` - Composite object theory

**Previous Experiments**:
- `v11/` - Black hole with ghost particles (baseline)
- `v10/` - Geodesics (100% orbital success)
- `v9/` - Combined SR + gravity time dilation

**Future Experiments**:
- `Experiment 55` - Full collision physics framework
- `Experiment 54` - Length contraction (independent)
- `Experiment 56` - Observer-dependent horizons

---

**This is a critical validation experiment: does tick-frame black hole theory survive with realistic collision physics?**

If yes → we have a testable alternative to GR.
If no → we learn about limitations and refine the model.

Either way → progress toward honest, falsifiable physics.
