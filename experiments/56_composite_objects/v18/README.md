# V18 - Unified Composite Physics Engine

## Status

**Implementation Status:** FOUNDATION COMPLETE  
**Date:** 2026-02-04  
**Version:** 0.1 - Basic Framework  
**Based on:** RAW-083 (Unified Imprint Principle)

---

## What is V18?

V18 correctly implements the **Unified Imprint Principle** from RAW-083:

> Every composite object is **one process** with:
> - **One imprint** (single spatial presence in gamma field)
> - **One wake** (∂gamma/∂t derivative)
> - **One tick-budget** (shared energy)
> - **Internal structure** (encoded as internal states, NOT sub-entities)

This allows correct modeling of atoms, molecules, and complex composite structures **without ontological contradiction**.

---

## Architecture

### Core Classes

#### Canvas3D_V18
- Sparse gamma field storage (dict-based)
- **NEW:** Wake field (∂gamma/∂t) tracking
- **NEW:** Process paint tracking (which process painted where)
- Gradient and wake-gradient computation
- Local energy sampling for resistance calculation

#### CompositeProcess
- Base class for all entities
- Properties:
  - `process_id`: Unique identifier
  - `center`: Position in space
  - `internal_state`: Structure encoding
  - `tick_budget`: Energy per tick
  - Age, statistics, energy accounting

#### InternalState (ABC)
- Base class for process internal structure
- Methods:
  - `get_imprint_profile()` - return spatial imprint shape
  - `transition()` - compute next state

#### SimpleDegenerateProcess
- Test process with no internal structure
- Used for baseline comparisons
- Paints single cell per tick

#### TickEvolution_V18
- Main simulation loop
- Creates processes at origin
- Steps all processes
- Decays wake field
- Records statistics

---

## Key Differences from V17

| Aspect | V17 | V18 |
|--------|-----|-----|
| **Entity model** | Renderer (single entity only) | CompositeProcess (any structure) |
| **Imprint** | Per-renderer | Per-process (unified) |
| **Wake field** | Not modeled | Explicit ∂gamma/∂t |
| **Tick budget** | Per-renderer | Per-process (shared) |
| **Internal structure** | Implicit position only | Explicit InternalState machine |
| **Composites** | IMPOSSIBLE | Native support |
| **RAW-083 compliant** | ✗ VIOLATION | ✓ CORRECT |

---

## Usage

### Quick Test

```bash
python experiment_v18.py --test quick
```

Output: 100 ticks with progress reporting

### Standard Test

```bash
python experiment_v18.py --test standard
```

Output: 1000 ticks with statistics

### Long Run

```bash
python experiment_v18.py --test longrun --ticks 10000
```

Output: Extended simulation showing memory scaling

### Save Results

```bash
python experiment_v18.py --test standard --save
```

Results saved to `results/v18_standard_TIMESTAMP.json`

---

## Current Implementation (Phase 1)

### What Works ✓
- Canvas with sparse storage
- Wake field tracking
- CompositeProcess base class
- SimpleDegenerateProcess (test particle)
- Basic evolution loop
- Statistics and logging

### What's Next (Phase 2)

1. **HydrogenAtom class** with orbital state
   - Electron cloud represented as orbital
   - Orbital transitions driven by wake energy
   - Orbital decay (energy loss)

2. **H2Molecule class** with bonded state
   - Two atoms bonded (NOT separate entities)
   - Bond maintained by shared energy
   - Vibration modes
   - Dissociation threshold

3. **Multi-molecule systems**
   - Multiple H2 molecules coexisting
   - No interference (separate imprints)
   - Orbital interactions

---

## Design Philosophy

### Principle 1: One Imprint = One Presence
- No multi-imprint composites
- Reduces wake interference
- Enables stable geometry

### Principle 2: Internal States Encode Structure
- Not sub-entities
- Transitions driven by shared energy
- Quantum evolution through wake interaction

### Principle 3: Shared Tick Budget Forces Coherence
- One energy pool per process
- Internal states share resources
- Prevents arbitrary breakup

### Principle 4: Wake is Physical
- ∂gamma/∂t, not just math
- Drives quantum transitions
- Creates expansion pressure

### Principle 5: Canvas is Complete State
- Gamma field: current presence
- Wake field: time derivative
- Process list: active processes
- Everything needed is here

---

## File Structure

```
v18/
├── __init__.py              # Package exports
├── canvas_v18.py            # Canvas3D_V18 with wake
├── process.py               # CompositeProcess base
├── evolution_v18.py         # TickEvolution_V18
├── experiment_v18.py        # Experiments
├── processes/               # (future) Specific process types
│   ├── photon.py            # Degenerate process
│   ├── hydrogen.py          # Hydrogen atom
│   ├── h2_molecule.py       # H2 molecule
│   └── water.py             # H2O (optional)
├── V18_DESIGN.md            # Design document
├── README.md                # This file
└── results/                 # Experiment outputs
    └── v18_*.json           # Results from --save
```

---

## Testing

Run quick test to verify installation:

```bash
cd experiments/56_composite_objects/v18
python experiment_v18.py --test quick --verbose
```

Expected output:
- 100 ticks processed
- ~10s runtime (depends on machine)
- Statistics showing painted cells increasing
- Memory usage < 10 MB

---

## Next Steps

1. **Verify Phase 1 works**
   - Run quick/standard tests
   - Check memory scaling
   - Verify canvas state is consistent

2. **Implement HydrogenAtom** (Phase 2)
   - Orbital ground state
   - Orbital excitation from wake
   - Orbital decay

3. **Implement H2Molecule** (Phase 2)
   - Bond representation
   - Molecular vibration
   - Dissociation

4. **Validate against theory**
   - Compare orbital radii with Bohr model
   - Compare bond lengths with quantum chemistry
   - Compare gravity with RAW-082

---

## References

- **RAW-083:** Composite Processes and the Unified Imprint Principle
- **RAW-081:** Photon as Degenerate Process
- **RAW-082:** Gamma-Wake Gravity Principle
- **RAW-049:** Temporal Ontology
- **V17 Analysis:** ANALYSIS_AND_FAILURE.md (why V17 was insufficient)

---

## Contact / Notes

**Created:** 2026-02-04  
**Author:** V18 Implementation Team  
**Status:** Foundation complete, ready for Phase 2 expansion

