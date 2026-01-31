# V6 Grid-Based Tick-Frame Model

**Date Started**: 2026-01-24
**Date Completed**: 2026-01-30
**Status**: COMPLETE ✅ - Stability Validated
**Architecture**: Discrete Planck cell grid with ternary field states + CA evolution

---

## Summary of Results

V6 successfully validated **spatial stability** of the tick-frame model:

| Metric | Result |
|--------|--------|
| Critical jitter | **0.119** (zero-point equilibrium) |
| Stable band | 0.115 - 0.119 |
| Radius drift | **0.06%** at optimal jitter |
| COM drift | **0.04** Planck cells |
| Field coverage | **2.9%** (with hybrid_strong confinement) |

### Optimal Configuration (`hybrid_strong`)
```python
jitter_strength = 0.119
creation_sensitivity = 2.0
field_decay_threshold = 1.5
field_decay_rate = 0.05
```

### Key Achievements
- ✅ Phase 1: Grid and patterns
- ✅ Phase 2: Jitter and evolution
- ✅ Phase 3: Gamma field and confinement
- ✅ Phase 4A: Field confinement tuning (97% coverage reduction)
- ✅ Jitter sweep: Critical value 0.119 identified

### Next Steps → V7
Motion dynamics (velocity, MSD, orbital motion, pattern identity) moved to V7.
See `../v7/README.md` for continuation

---

## Overview

V6 is a **complete architectural rewrite** that properly implements the tick-frame ontology described in `ONTOLOGY.md` and `STRUCTURE.md`.

**Key shift from V5**:
- V5: Point particles with continuous (x,y) coordinates → FAILED (architectural mismatch)
- V6: Discrete Planck cell grid with ternary states {-1, 0, +1} → ONTOLOGY-ALIGNED

---

## Core Concepts

### Planck Cell Grid
- Discrete 2D grid (200×200 cells recommended)
- Each cell holds ternary field value: {-1, 0, +1}
- Each cell receives ±1 jitter per tick (quantum random walk)
- Gamma field modulates pattern stability (not a force field)

### Sample Cells
- 5×5 blocks of Planck cells
- Define the "canvas" for patterns
- 50 patterns = 50 sample cells (non-overlapping initially)

### Patterns
- Local field configurations (e.g., monopole, dipole, vortex)
- **Not point particles** - patterns are extended structures
- Stable patterns persist through jitter + evolution
- Unstable patterns dissolve or morph

### Evolution
- Cellular automaton rules (not Newtonian force integration)
- Jitter → Local CA rules (modulated by gamma) → New field state
- Patterns emerge from stable repeating configurations

---

## Files

### Phase 1: Grid and Patterns ✅

#### `planck_grid.py` ✅
- `PlanckGrid`: 2D grid of ternary field values
- Field storage: `np.int8` array (height × width)
- Gamma storage: `np.uint8` array (0-255 → gamma ∈ [1.0, 2.0])
- Operations: get/set cell, extract/write region, statistics
- Demo: Creates 20×20 grid, writes patterns, visualizes

#### `pattern_library.py` ✅
- `PatternLibrary`: Registry of known patterns (5×5 or 7×7)
- Built-in patterns:
  - **monopole**: Radial positive pattern (energy=5)
  - **dipole**: Vertical +/- pair (energy=8)
  - **quadrupole**: Alternating +/- (energy=8)
  - **rotating**: Asymmetric (simulates angular momentum, energy=6)
  - **vortex**: Circular pattern (energy=12)
  - **unstable**: High-energy checkerboard (energy=25)
- Pattern detection via hash (base-3 encoding of ternary values)
- Demo: Lists all patterns, visualizes, tests hash uniqueness

#### `sample_cell.py` ✅
- `SampleCell`: 5×5 block defining pattern location
- Operations: extract/apply pattern, shift, overlap detection
- `PatternInstance`: Combines SampleCell + pattern name + ID
- Operations: read/write from grid, validate pattern persistence
- Demo: Creates 2 pattern instances, writes to grid, tests overlap

### Phase 2: Jitter and Evolution ✅

#### `planck_jitter.py` ✅
- `PlanckJitter`: Apply ±1 jitter to each cell per tick
- Configurable probability distribution (symmetric by default)
- Statistical validation methods (mean, variance, distribution)
- Factory methods: `create_symmetric()`, `create_from_v4_parameters()`
- Demo: 100 ticks on 20×20 grid → 66% nonzero cells

#### `evolution_rules.py` ✅
- `TickFrameEvolution`: Cellular automaton for field evolution
- Ternary CA rules for {-1, 0, +1} states
- 3×3 neighborhood (8 neighbors + center)
- Gamma field modulates survival threshold
- Evolution cycle: jitter → CA rules → update grid
- Demo: 1000 ticks, monopole pattern → energy 5 → 2014

### Documentation

#### `V6_PLAN.md` ✅
- Complete implementation plan (Phases 1-4)
- Architecture details (grid, patterns, jitter, evolution)
- Success criteria for each phase
- Open questions and design decisions

#### `PHASE_2_SUMMARY.md` ✅
- Detailed analysis of jitter and evolution implementation
- Test results from 1000-tick simulation
- Issues identified (confinement, pattern preservation)
- Next steps for Phase 3 (gamma field tuning)

---

## Phase 1 Status: COMPLETE ✅

**Completed**:
- [x] PlanckGrid with ternary field storage
- [x] PatternLibrary with 6 initial patterns
- [x] SampleCell and PatternInstance classes
- [x] All modules tested and working

**Verified**:
- Grid operations (read/write cells, extract/apply regions)
- Pattern detection via hash (all 6 patterns have unique hashes)
- Sample cell overlap detection
- Pattern instance read/write/validate

**Performance**:
- Memory: 200×200 grid = 80 KB (field + gamma)
- Grid operations: < 1ms
- Pattern hash: O(1) lookup

---

## Phase 2 Status: COMPLETE ✅

**Completed**:
- [x] PlanckJitter with ±1 integer jitter per cell
- [x] TickFrameEvolution with ternary CA rules
- [x] Jitter statistics validated (mean≈0, var≈0.5)
- [x] 1000-tick evolution test (emergent patterns observed)

**Key Results**:
- Jitter creates quantum random walk (verified statistically)
- CA rules produce persistent field activity (energy: 5 → 2014 over 1000 ticks)
- Emergent spatial structures form spontaneously
- Gamma modulation affects pattern stability (observable)

**Issues Identified**:
- Pattern confinement weak (spreads throughout grid)
- Original patterns not preserved (dissolved by jitter)
- Field becomes too uniform (~80% coverage)

**Performance**:
- 50×50 grid: ~300-500 ticks/second
- Numerically stable, no overflow/underflow
- Memory: negligible (< 100 KB)

**Documentation**:
- See `PHASE_2_SUMMARY.md` for detailed analysis

---

## Next Steps: Phase 2 (Jitter and Evolution)

### To Implement

1. **`planck_jitter.py`**
   - Apply ±1 jitter to all Planck cells
   - Probability distribution: `p=[-1: 0.25, 0: 0.5, +1: 0.25]`
   - Clamp to {-1, 0, +1} bounds
   - Tunable for V4 jitter equivalence

2. **`evolution_rules.py`**
   - Cellular automaton rules (Conway-like, but ternary)
   - Gamma field modulation (high gamma → more stable)
   - Local neighborhood (3×3) consensus logic
   - Goal: Stable patterns persist, unstable dissolve

3. **Tests**
   - Validate jitter statistics (σ² ≈ 0.5 per cell)
   - Test pattern persistence (monopole survives 1000 ticks?)
   - Test unstable patterns (dissolve within 100 ticks?)

### Success Criteria (Phase 2)

- [ ] Jitter produces correct statistics
- [ ] Simple patterns (monopole) persist for 1000+ ticks
- [ ] Unstable patterns dissolve within 100 ticks
- [ ] Evolution rules numerically stable

---

## Differences from V5

| Aspect | V5 (Point Particles) | V6 (Grid-Based) |
|--------|---------------------|-----------------|
| Space | Continuous (x, y) | Discrete Planck grid |
| Entity | Point particle | 5×5 pattern |
| State | Position + velocity | Field values {-1, 0, +1} |
| Jitter | Gaussian velocity kick | ±1 per Planck cell |
| Motion | v → x += v | Pattern shifts on grid |
| Collision | Momentum conservation | Pattern overlap/merge |
| Confinement | Force F = -k×r | Gamma modulates stability |
| Evolution | Newtonian integration | Cellular automaton |

---

## Design Decisions

1. **Grid size**: 200×200 Planck cells
   - 50 patterns at r≈2.0 → radius ≈ 10-15 Planck cells
   - Grid center: (100, 100)
   - Allows plenty of expansion room

2. **Pattern size**: 5×5 (can test 7×7 later)
   - Matches STRUCTURE.md recommendation
   - Large enough for gradients/asymmetry
   - Small enough for 50 patterns to fit comfortably

3. **Boundary conditions**: Periodic (toroidal topology)
   - Simpler than reflective
   - No edge effects
   - Patterns wrap around edges

4. **Gamma field**: Precomputed at initialization
   - γ(r) = 1 + k/r² (radial potential)
   - Stored as uint8 (0-255)
   - Modulates CA survival probabilities

5. **Evolution approach**: Start with Option B (true CA)
   - Patterns dissolve/reform at new location
   - More aligned with ontology
   - If too chaotic, try Option A (shift patterns)

---

## References

- `../v5/ONTOLOGY.md` - Core tick-frame concepts
- `../v5/STRUCTURE.md` - Spatial hierarchy (Planck cells, samples, patterns)
- `../v5/V5_SUMMARY.md` - Lessons from V5 failure
- `../v4/` - V4 float-based baseline (6.52% drift over 200k ticks)

---

**Timeline**: 4 weeks (Phases 1-4)
**Current progress**: Phase 2 complete (Week 2 complete)
**Confidence**: High (ontology-aligned, core mechanics working)
