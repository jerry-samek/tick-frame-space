# Experiment 56: 3D Fragmented Cloud (vX_3d)

**Status**: DEFERRED - Not needed after V4 success
**Date**: Originally planned 2026-01-23
**Updated**: 2026-01-24
**Renamed**: v5 → vX_3d (3D implementation deferred until needed)

## Why This Was Deferred

**V4 200k Validation SUCCESS** (2026-01-24):
- V4 achieved complete stability with optimized parameters
- Cloud radius drift: **6.52%** (< 10% threshold) ✓
- Energy conservation: **1.43%** drift (excellent) ✓
- Fragments escaped: **0/50** (perfect retention) ✓
- Collision rate: **4.82/tick** (stable thermalization) ✓

**Optimal Parameters Found**:
- `jitter_strength = 0.0005` (0.001 causes runaway)
- `collision_radius = 0.5` (electron-like, ~5 collisions/tick)

**Conclusion**: 2D fragmented cloud IS STABLE and VIABLE! The issue was **energy balance and collision parameter confusion**, not fundamental dimensionality.

## vX_3d Status: Optional Enhancement (Not Currently Needed)

**Original reason for vX**: 2D appeared fundamentally unstable → needed 3D for stability

**Current situation**:
- ✓ 2D works perfectly with validated parameters
- ✓ 200k tick stability confirmed
- → 3D not urgently needed for stability or basic physics

**Why 3D might still be valuable** (future work):
- Full angular momentum vector (Lx, Ly, Lz) vs scalar L_z
- 3D collision phase space (potentially better thermalization)
- More realistic physics (theory suggests 3D minimum per Doc 015_01)
- Validation and comparison with 2D results
- Required for multi-electron atoms (if 2D proves insufficient)

**Current priority**:
- **V5**: Dual-parameter collision system (based on FUTURE_IMPROVEMENTS.md)
- **V6**: Particle accelerator experiments
- **vX_3d**: Implement when/if 3D becomes necessary

## Quick Summary (Original Motivation)

## Directory Structure

```
v5/
├── README.md                        # This file
├── PHASE_5_V5_PLAN.md              # Detailed implementation plan
├── config_v5.py                    # Configuration (needs spatial_dimensions=3)
├── fragmented_cloud.py             # NEEDS 2D→3D CONVERSION
├── zero_point_jitter.py            # NEEDS 2D→3D CONVERSION
├── collision_dynamics.py           # OK (dimension-agnostic)
├── binding_detection_v2.py         # OK (use 2D field with 3D gradient)
├── experiment_56a_v5_3d.py         # NEEDS MINOR UPDATES
├── analyze_quantization.py         # NEEDS 3D UPDATES
└── results/                        # Will contain results
```

## Implementation Status

Current files are **copies from V4 (2D)** and need conversion:

- [ ] **fragmented_cloud.py** - Convert to 3D (MAJOR)
  - Positions: (x, y) → (x, y, z)
  - Velocities: (vx, vy) → (vx, vy, vz)
  - Initialization: 2D polar → 3D spherical
  - Angular momentum: scalar L_z → vector (Lx, Ly, Lz)
  - Radial density: 2πr·dr → 4πr²·dr
  - MB test: Rayleigh → Maxwell

- [ ] **zero_point_jitter.py** - Add z-component (MINOR)
  - Change `size=2` to `size=3` in np.random.normal()

- [ ] **experiment_56a_v5_3d.py** - Update for 3D (MINOR)
  - Add angular momentum vector to snapshots
  - Update gradient force application

- [x] **collision_dynamics.py** - No changes needed ✓
  - Already dimension-agnostic (uses np.linalg.norm)

- [x] **binding_detection_v2.py** - No changes needed ✓
  - Use 2D field with 3D gradient projection

See **PHASE_5_V5_PLAN.md** for detailed implementation checklist.

## What We Learned from V4 (2D)

**Successes**:
- ✓ Collision dynamics create shell-like structures (3 shells detected)
- ✓ Zero-point jitter prevents collapse
- ✓ Model is computationally tractable

**Failures**:
- ✗ Long-term instability (runaway at 51k-69k ticks)
- ✗ Energy pumping > dissipation
- ✗ No energy level gaps
- ✗ Angular momentum (scalar) didn't converge

## Expected V5 Outcomes

**If 3D succeeds**:
- Cloud stable for 200k+ ticks
- Energy conserved (< 5% drift)
- Angular momentum vector converges
- Quantization signatures emerge
- → Theory validated!

**If 3D also fails**:
- Need major model revision:
  - Reduce jitter strength
  - Add velocity damping
  - Implement magnetic interactions
  - Try 4D spatial dimensions
  - Or abandon fragmented cloud approach

## Current Recommendations

### Option A: Continue in 2D (RECOMMENDED)
- Run 50 fragments, jitter=0.0005, **200k ticks** for quantization study
- Known to work (validated at 100k ticks)
- Fast iteration (~15 minutes)
- Answers quantization question definitively

### Option B: Implement 3D (V5) for Validation
- Compare 2D vs 3D quantization signatures
- Validate 2D is not producing artifacts
- Better physics (full angular momentum)
- More work but theoretically cleaner

## If Proceeding with V5

1. **Read PHASE_5_V5_PLAN.md** for full context
2. **Implement 2D→3D conversions** (estimated 30-60 min)
3. **Run Phase 5a**: 50 fragments, jitter=0.0005, 100k ticks (~7 min)
4. **If stable, run Phase 5b**: 200k ticks (~15 min)
5. **Write PHASE_5_V5_RESULTS.md** with findings
6. **Compare with V4 2D results** for validation

## Quick Start (After Implementation)

```bash
cd experiments/56_composite_objects/v5

# Run baseline stability test
python experiment_56a_v5_3d.py

# Expected: ~7-15 minutes runtime
# Watch for stability (r ≈ 2.0, no escapes)
```

## References

- **V4 Results**: `../v4/PHASE_4_V4_RESULTS.md` - Full V4 story (initial failure → diagnostic success)
- **V4 Breakthrough**: `../v4/ENERGY_DIAGNOSTIC_BREAKTHROUGH.md` - Energy diagnostic success
- **V5 Plan**: `PHASE_5_V5_PLAN.md` - Implementation details (if proceeding)
- **Theory**:
  - Doc 015_01: Dimensional Closure (3D minimum)
  - Doc 070_01: Collision-Driven Stabilization
  - Doc 070_02: Zero-Point Energy
  - Doc 050_01: Dimensional Equivalence Rejection

---

**Status**: V5 is ON HOLD. V4 succeeded with energy tuning (jitter=0.0005).

**Recommendation**: Continue with 2D (V4) for quantization studies. Implement V5 (3D) later for comparison/validation if desired.
