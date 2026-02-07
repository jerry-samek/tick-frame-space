# Experiment 56: Composite Objects in the Gamma Field

**Status:** V18 ACTIVE (V17 DEPRECATED)  
**Date:** 2026-02-04  
**Focus:** Unified Imprint Principle (RAW-083)

---

## Overview

Experiment 56 explores how **composite objects** (atoms, molecules, organisms) are correctly modeled in the tick-frame/gamma-field universe.

The key insight from **RAW-083**:

> Composite objects **cannot** be collections of independent entities.
> They must be **ONE process** with:
> - ONE imprint
> - ONE wake
> - ONE tick-budget
> - Internal structure encoded as states (not sub-entities)

---

## Project Structure

```
56_composite_objects/
├── README.md                          # This overview
├── COMPARISON_V17_VS_V18.md           # Architecture evolution
├── ISSUE.md                           # RAW-083 (composite principle)
├── ANALYSIS_AND_FAILURE.md            # Why V17 failed
│
├── v17/                               # DEPRECATED
│   ├── README.md                      # V17 documentation
│   ├── ANALYSIS_AND_FAILURE.md        # Detailed failure analysis
│   ├── ISSUE.md                       # RAW-083 requirements
│   ├── canvas.py                      # Sparse gamma storage
│   ├── renderer.py                    # Single-entity renderers
│   ├── evolution.py                   # Evolution loop
│   ├── config_v17.py                  # Configuration
│   ├── experiment_v17.py              # Experiments
│   └── results/                       # Experiment outputs
│
├── v18/                               # ACTIVE (correct implementation)
│   ├── README.md                      # V18 documentation
│   ├── V18_DESIGN.md                  # Architecture design
│   ├── canvas_v18.py                  # Gamma + wake fields
│   ├── process.py                     # CompositeProcess base class
│   ├── internal_state.py              # (planned) State machine base
│   ├── evolution_v18.py               # Unified evolution loop
│   ├── processes/                     # (planned)
│   │   ├── photon.py                  # Degenerate process
│   │   ├── hydrogen.py                # Hydrogen atom
│   │   ├── h2_molecule.py             # H₂ molecule
│   │   └── water.py                   # H₂O (future)
│   ├── experiment_v18.py              # Experiments
│   ├── __init__.py                    # Package exports
│   └── results/                       # Experiment outputs
│
└── (future experiments)
    └── v19/                           # (optional) Evolution
```

---

## Key Documents

### For Quick Start
1. **README.md** (this file) - Overview
2. **v18/README.md** - How to use V18
3. **COMPARISON_V17_VS_V18.md** - Why V18 vs V17

### For Understanding the Theory
1. **ISSUE.md** (or v17/ISSUE.md) - RAW-083 principle
2. **v17/ANALYSIS_AND_FAILURE.md** - What V17 got wrong
3. **v18/V18_DESIGN.md** - V18 design philosophy

### For Implementation
1. **v18/canvas_v18.py** - Canvas with wake tracking
2. **v18/process.py** - CompositeProcess base class
3. **v18/evolution_v18.py** - Main simulation loop

### For References
- **RAW-083:** Composite Processes and the Unified Imprint Principle
- **RAW-081:** Photon as Degenerate Process
- **RAW-082:** Gamma-Wake Gravity Principle
- **RAW-049:** Temporal Ontology

---

## Quick Start

### Run V18 Quick Test
```bash
cd v18
python experiment_v18.py --test quick
```

Output: 100 ticks in ~0.16s showing:
- Process creation at origin
- Canvas paint accumulation
- Wake field evolution
- Memory usage

### Run V18 Standard Test
```bash
cd v18
python experiment_v18.py --test standard
```

Output: 1000 ticks showing memory scaling and performance.

### Save Results
```bash
cd v18
python experiment_v18.py --test standard --save
```

Results saved to `v18/results/v18_standard_TIMESTAMP.json`

---

## V17: Why It Failed

V17 attempted canvas ontology but had fatal flaws:

### Problem 1: Multi-Imprint Collections
Each renderer (entity) maintains independent state:
- `last_paint_pos` - position
- `total_skips`, `total_acts` - history
- `time_dilation_factor` - personal time

If you try to model H₂ molecule as 2 renderers:
- They immediately desynchronize
- Different drift rates
- Different skip patterns
- Wake interference
- **Composite disintegrates**

This is exactly what RAW-083 §4 predicts: **multi-imprint composites fail**.

### Problem 2: No Wake Model
Canvas only stores `gamma` (paint):
```python
self.gamma: Dict[Pos3D, float]  # No wake field
```

Missing:
- Expansion resistance
- Quantum pressure
- Time dilation cause
- Gravity generation

### Problem 3: Split State
Claims "Canvas IS the state" but actually:
- Canvas stores paint only
- Renderer list stores positions
- External state = incomplete state

**Result:** Cannot model composites correctly.

---

## V18: The Correct Approach

V18 implements RAW-083 correctly:

### Feature 1: Wake Field
```python
self.gamma: Dict[Pos3D, float]  # Current presence
self.wake: Dict[Pos3D, float]   # ∂gamma/∂t (derivative)
```

Wake is **physically real**, not mathematical convenience:
- Drives quantum transitions
- Creates expansion pressure
- Enables orbital dynamics
- Necessary for gravity (RAW-082)

### Feature 2: CompositeProcess
Single entity type for all objects:
- Photon (degenerate process)
- Hydrogen atom (orbital state)
- H₂ molecule (bonded state)
- Complex molecules (hierarchical states)

Each process has:
- **ONE imprint** (unified spatial presence)
- **ONE wake** (shared time derivative)
- **ONE tick-budget** (shared energy)
- **internal_state** (encodes structure)

### Feature 3: Internal State Machine
Structure is explicit data, not implicit position:
```python
class H2Molecule(CompositeProcess):
    class MolecularState(InternalState):
        proton_separation: float
        bond_angle: np.ndarray
        vibration_phase: float
        
        def transition(self, canvas, center, budget):
            # Compute next state
            # Energy is SHARED
            return (continues, energy_used)
```

Result: Can model:
- Orbital transitions
- Molecular vibration
- Bond dissociation
- Chemical reactions

---

## Implementation Phases

### Phase 1: Foundation ✓ COMPLETE
- [x] Canvas3D_V18 with wake tracking
- [x] CompositeProcess base class
- [x] SimpleDegenerateProcess (test particle)
- [x] TickEvolution_V18 loop
- [x] Basic experiments

**Status:** Foundation works, tested, documented.

### Phase 2: Atomic Physics (NEXT)
- [ ] HydrogenAtom class
- [ ] Orbital state machine
- [ ] Orbital excitation/decay
- [ ] Spectrum generation

**Expected:** 2-3 days

### Phase 3: Molecular Physics
- [ ] H2Molecule class
- [ ] Bond representation
- [ ] Vibrational modes
- [ ] Dissociation

**Expected:** 3-5 days

### Phase 4: Reaction Physics
- [ ] Composite tracking
- [ ] Reaction pathways
- [ ] Product formation
- [ ] Energy accounting

**Expected:** 1-2 weeks

### Phase 5: Validation
- [ ] Compare orbitals with Bohr model
- [ ] Compare bonds with quantum chemistry
- [ ] Compare gravity with RAW-082
- [ ] Publish results

**Expected:** 1-2 weeks

---

## Success Criteria

V18 is successful when:

1. ✓ **Foundation works**
   - Canvas with wake ✓
   - CompositeProcess ✓
   - Evolution loop ✓

2. **Hydrogen atom**
   - Atom forms and remains stable
   - Orbital represents electron
   - Orbital transitions via wake energy

3. **H₂ molecule**
   - Two atoms form one bond
   - Molecule moves as ONE entity
   - Bond breaks at dissociation energy

4. **Multi-molecule system**
   - Multiple molecules coexist
   - No mutual interference
   - Correct gravitational behavior

5. **Validation**
   - Orbital radii match Bohr model
   - Bond lengths match quantum chemistry
   - Gravity matches RAW-082

---

## Testing

### Run All Tests
```bash
cd v18
python experiment_v18.py --test all --save
```

### Benchmark Performance
```bash
cd v18
time python experiment_v18.py --test longrun --ticks 10000
```

### Compare V17 vs V18
```bash
cd v17
python experiment_v17.py --test standard
cd ../v18
python experiment_v18.py --test standard
```

V17 should be faster (~138 ticks/s vs ~82 ticks/s) but both show same memory scaling.

---

## Architecture Diagram

```
┌─────────────────────────────────────┐
│     TickEvolution_V18               │
│  Main simulation loop               │
└────────┬────────────────────────────┘
         │
    ┌────┴────────────────────┐
    │                         │
    ▼                         ▼
┌──────────────┐       ┌──────────────┐
│   Canvas3D   │       │  Processes   │
│   _V18       │       │   List       │
│              │       │              │
│ • gamma      │       │ • hydrogen   │
│ • wake       │       │ • h2_mol     │
│ • process_   │       │ • complex    │
│   paint      │       │   molecules  │
└──────────────┘       └──────────────┘
     │                      │
     │      step()          │
     ├──────────────────────┤
     │                      │
     ▼                      ▼
┌───────────────────────────────────┐
│   Unified Composite Physics       │
│                                   │
│ • One imprint per process         │
│ • One wake per process            │
│ • Shared tick-budget              │
│ • Internal state transitions      │
└───────────────────────────────────┘
```

---

## Related Theories

### RAW-083: Unified Imprint Principle
The core requirement: composites must be ONE process with ONE imprint, not collections of entities.

**Key prediction:** Multi-imprint composites fail due to:
- Different drift rates
- Different tick budgets
- Wake interference
- No shared resistance

**V17 exhibits all these failures.**

### RAW-082: Gamma-Wake Gravity Principle
Gravity emerges from the wake field (∂gamma/∂t).

**Key insight:** Wake is physically real, not just math.

**V18 implementation:** Explicit wake field enables correct gravity.

### RAW-081: Photon as Degenerate Process
Photon is the simplest process: NO internal structure.

**V18 implementation:** SimpleDegenerateProcess / Photon class.

### RAW-049: Temporal Ontology
Time emerges from process interactions in the tick frame.

**V18 implementation:** time_dilation_factor from skip_count.

---

## Contributing

### To Implement Phase 2 (Hydrogen Atom)

1. Create `v18/processes/hydrogen.py`
2. Implement `HydrogenAtom` class (extends CompositeProcess)
3. Implement `OrbitalState` (extends InternalState)
4. Add orbital transitions driven by wake energy
5. Test with `experiment_v18.py --test hydrogen`

### To Add New Process Types

1. Create `v18/processes/your_process.py`
2. Extend `CompositeProcess`
3. Define custom `InternalState` subclass
4. Implement `get_imprint_profile()` and `transition()`
5. Register in evolution loop

### To Extend Canvas Physics

1. Add new methods to `Canvas3D_V18`
2. Update `paint_imprint()` if needed
3. Add new field types if needed
4. Test with existing experiments

---

## References

### Theory Documents
- `/docs/theory/raw/083_*` - RAW-083 (Unified Imprint)
- `/docs/theory/raw/082_*` - RAW-082 (Gamma-Wake Gravity)
- `/docs/theory/raw/081_*` - RAW-081 (Photon)
- `/docs/theory/raw/049_*` - RAW-049 (Temporal Ontology)

### Experiment Documentation
- `v17/README.md` - V17 design (deprecated)
- `v17/ANALYSIS_AND_FAILURE.md` - V17 failures
- `v18/README.md` - V18 quickstart
- `v18/V18_DESIGN.md` - V18 architecture
- `COMPARISON_V17_VS_V18.md` - Evolution

---

## Status Summary

| Component | Status | Date |
|-----------|--------|------|
| **V17 Analysis** | COMPLETE | 2026-02-04 |
| **V18 Design** | COMPLETE | 2026-02-04 |
| **V18 Foundation** | COMPLETE | 2026-02-04 |
| **V18 Testing** | COMPLETE | 2026-02-04 |
| **Phase 2 (Hydrogen)** | PENDING | 2026-02-XX |
| **Phase 3 (H₂)** | PENDING | 2026-02-XX |
| **Phase 4 (Reactions)** | PENDING | 2026-03-XX |
| **Phase 5 (Validation)** | PENDING | 2026-03-XX |

---

## Contact

**Created:** 2026-02-04  
**Last Updated:** 2026-02-04  
**Status:** ACTIVE (V18)

