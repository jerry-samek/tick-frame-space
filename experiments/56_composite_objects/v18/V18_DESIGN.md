# V18 Design: Unified Imprint Composite Physics Engine

**Status:** DESIGN  
**Version:** 1.0  
**Date:** 2026-02-04  
**Based on:** RAW-083 (Unified Imprint Principle), RAW-081, RAW-082

---

## Vision

V18 implements the **Unified Imprint Principle** correctly:

> Every composite object is **one process**, with **one imprint**, **one wake**, **one tick-budget**, and **internal structure encoded as internal states** (not sub-entities).

This enables correct modeling of molecules, atoms, particles, and composite structures **within the gamma-field ontology**.

---

## Core Data Structures

### 1. CompositeProcess (replaces Renderer)

```python
class CompositeProcess:
    """A single unified process with internal structure.
    
    Properties:
    - ONE imprint (gamma deformation in field)
    - ONE wake (∂gamma/∂t)
    - ONE tick_budget (total energy)
    - Internal state (structure encoding)
    """
    
    process_id: int
    
    # Imprint & position
    imprint_center: Pos3D          # Where the imprint is painted
    imprint_profile: np.ndarray    # Spatial shape of imprint
    imprint_strength: float        # Total gamma deposited
    
    # Wake tracking
    wake_field: Dict[Pos3D, float] # ∂gamma/∂t - time derivative
    
    # Energy & tick budget
    tick_budget: float             # Total energy available this tick
    tick_spent: float              # Energy used this tick
    
    # Internal structure
    internal_state: InternalState  # Process-specific state machine
    
    # History
    age_ticks: int                 # How many ticks this process has existed
    birth_tick: int                # When was this process created
    
    def step(self, canvas: Canvas3D) -> bool:
        """Execute one tick of this process.
        
        Returns:
            True if process continues, False if expired
        """
        # 1. Read shared imprint + wake from canvas
        # 2. Compute internal state transition
        # 3. Paint unified imprint
        # 4. Update wake derivative
        # 5. Account for tick_budget
```

### 2. InternalState (process-specific structure)

```python
class InternalState:
    """Base class for process internal structure.
    
    Different processes have different internal states:
    - Photon: no internal structure (degenerate)
    - Electron: spin, helicity
    - Atom: nuclear position, electron cloud state
    - Molecule: atomic positions, bond angles, vibration modes
    - Composite object: multi-layer hierarchy
    """
    
    def transition(self, imprint_gamma: float, wake_field: Dict, dt: int) -> bool:
        """Compute next internal state.
        
        Args:
            imprint_gamma: Total gamma in shared imprint
            wake_field: Wake derivative (∂gamma/∂t)
            dt: Timestep (always 1)
            
        Returns:
            True to continue, False to expire
        """
        pass
    
    def get_imprint_profile(self) -> np.ndarray:
        """Return imprint shape based on current internal state."""
        pass
```

### 3. Extended Canvas with Wake

```python
class Canvas3D_V18:
    """Gamma field with wake tracking.
    
    Stores:
    - gamma[pos] = current gamma at position
    - wake[pos] = ∂gamma/∂t at position
    - process_paint[process_id] = which cells this process painted
    """
    
    gamma: Dict[Pos3D, float]
    wake: Dict[Pos3D, float]              # NEW: time derivative
    process_paint: Dict[int, Set[Pos3D]]  # NEW: track process contributions
    
    def paint_imprint(self, process: CompositeProcess):
        """Paint unified imprint for one process.
        
        Adds to wake calculation since paint is new:
        wake[pos] += imprint[pos]  # Derivative of paint accumulation
        """
        pass
    
    def compute_process_gradient(self, process: CompositeProcess) -> np.ndarray:
        """Get gradient seen by this process.
        
        Computes gradient of unified imprint + wake field at process center.
        """
        pass
    
    def get_wake_field(self, center: Pos3D, radius: int) -> Dict[Pos3D, float]:
        """Extract wake field (∂gamma/∂t) around position."""
        pass
```

---

## Example: Hydrogen Atom (H)

```python
class HydrogenAtom(CompositeProcess):
    """Single proton + electron cloud.
    
    Internal state: electron_orbit_radius (quantum level)
    """
    
    class ElectronState(InternalState):
        def __init__(self):
            self.orbital_level = 1      # Ground state
            self.orbital_radius = 1     # In local coordinates
            
        def get_imprint_profile(self) -> np.ndarray:
            # Proton at center (sharp)
            # Electron cloud as diffuse sphere around it
            return create_bohr_orbital(self.orbital_level)
    
    def __init__(self, process_id: int, pos: Pos3D):
        self.process_id = process_id
        self.imprint_center = pos
        self.internal_state = HydrogenAtom.ElectronState()
        self.tick_budget = 1.0
        
    def step(self, canvas: Canvas3D_V18) -> bool:
        # 1. Compute gradient at imprint center
        gradient = canvas.compute_process_gradient(self)
        
        # 2. Get wake field (quantum pressure from expansion)
        wake = canvas.get_wake_field(self.imprint_center, radius=5)
        
        # 3. Electron state transition (driven by wake energy)
        can_continue = self.internal_state.transition(
            imprint_gamma=canvas.get_gamma(self.imprint_center),
            wake_field=wake,
            dt=1
        )
        
        # 4. Paint unified imprint (proton + electron cloud as ONE object)
        self.paint_unified_imprint(canvas)
        
        # 5. Update wake derivative
        self.update_wake(canvas)
        
        return can_continue
```

## Example: H₂ Molecule

```python
class H2Molecule(CompositeProcess):
    """Two hydrogen atoms bonded.
    
    Internal state:
    - proton_sep: distance between protons
    - bond_angle: orientation
    - vibration_phase: oscillation mode
    
    KEY: This is ONE process, NOT two separate hydrogen atoms.
    """
    
    class MolecularState(InternalState):
        def __init__(self):
            self.proton_sep = 2.0           # Equilibrium ~1.4 Bohr radii
            self.bond_angle = np.array([0, 0, 0])
            self.vibration_phase = 0.0
            
        def transition(self, imprint_gamma: float, wake_field: Dict, dt: int) -> bool:
            # 1. Energy available this tick (from tick_budget)
            # 2. Wake pushes protons apart (expansion resistance)
            # 3. Internal oscillator tries to maintain bond length
            # 4. Gradient from canvas pulls whole molecule
            
            # Update: proton_sep, bond_angle, vibration_phase
            # Based on shared energy pool
            
            return True  # H2 is stable
            
        def get_imprint_profile(self) -> np.ndarray:
            # Two protons + two electron clouds
            # Bonded geometry - NOT two separate hydrogen imprints
            # Returns: unified electron density for H2
            return create_h2_electron_density(
                self.proton_sep,
                self.bond_angle
            )
    
    def __init__(self, process_id: int, pos: Pos3D):
        self.process_id = process_id
        self.imprint_center = pos
        self.internal_state = H2Molecule.MolecularState()
        self.tick_budget = 2.0  # TWO atoms worth of energy
        
    def step(self, canvas: Canvas3D_V18) -> bool:
        # Unified molecular physics:
        # - ONE imprint (bonded electron density)
        # - ONE wake (from consolidated presence)
        # - ONE tick_budget (shared energy)
        # - Internal state (molecular structure)
        
        # Single energy accounting prevents breakup
        # Unified imprint prevents drift
        # Wake field drives quantum evolution
        
        return super().step(canvas)
```

---

## Tick Evolution Loop (V18)

```python
class TickEvolution_V18:
    """Main simulation loop with unified composite physics."""
    
    def __init__(self, config: Config18):
        self.canvas = Canvas3D_V18()
        self.processes: List[CompositeProcess] = []
        self.tick_count = 0
        
    def evolve_one_tick(self):
        """Execute one tick of unified physics."""
        self.tick_count += 1
        
        # 1. Create new process at origin (if appropriate for test)
        if self.should_create_process():
            process = self.create_new_process()
            self.processes.append(process)
        
        # 2. Each process executes its step (unified)
        for process in self.processes[:]:
            continues = process.step(self.canvas)
            if not continues:
                self.processes.remove(process)  # Expired
        
        # 3. Update canvas wake field
        self.canvas.update_wake_derivative()
        
        # 4. Log statistics
        self.record_stats()
```

---

## Key Design Principles for V18

### Principle 1: One Imprint = One Presence
- No multi-imprint composites
- Reduces wake interference
- Enables stable geometry

### Principle 2: Internal State Encodes Structure
- Not sub-entities
- Transitions computed from shared energy
- Quantum evolution driven by wake

### Principle 3: Shared Tick Budget Forces Coherence
- One energy pool per process
- Internal states compete for energy
- Prevents arbitrary breakup

### Principle 4: Wake Field is Physical
- ∂gamma/∂t is not just math
- Drives quantum transitions
- Creates pressure (expansion resistance)

### Principle 5: Canvas is Complete State
- Gamma field: current presence
- Wake field: time derivative
- Process collection: active processes
- NO additional state outside canvas + processes

---

## Implementation Phases

### Phase 1: Foundation (now)
- [ ] Canvas3D_V18 with wake tracking
- [ ] CompositeProcess base class
- [ ] Simple test: single photon (degenerate process)
- [ ] Basic evolution loop

### Phase 2: Hydrogen Atom
- [ ] HydrogenAtom class with ElectronState
- [ ] Orbital transitions driven by wake
- [ ] Orbital decay (energy loss)
- [ ] Test: hydrogen decay, absorption

### Phase 3: H₂ Molecule
- [ ] H2Molecule class with MolecularState
- [ ] Bond maintenance through shared energy
- [ ] Vibration modes
- [ ] Dissociation threshold

### Phase 4: Multi-Molecule Systems
- [ ] Composite tracking (which atoms in which molecules)
- [ ] Orbital alignment (bonding geometry)
- [ ] Chemical reactions (process transitions)

### Phase 5: Validation
- [ ] Compare with quantum mechanics (orbitals)
- [ ] Compare with molecular dynamics (bond lengths)
- [ ] Compare with gravity (wake-based attraction)

---

## Files to Create

```
v18/
├── __init__.py
├── config_v18.py              # Configuration for V18
├── canvas_v18.py              # Canvas3D_V18 with wake
├── process.py                 # CompositeProcess base
├── internal_state.py          # InternalState base + examples
├── evolution_v18.py           # TickEvolution_V18
├── processes/
│   ├── photon.py              # Degenerate process
│   ├── hydrogen.py            # Hydrogen atom
│   ├── h2_molecule.py         # H2 molecule
│   └── water.py               # H2O (optional)
├── experiment_v18.py          # Experiments
├── V18_DESIGN.md              # This file
└── README.md
```

---

## Success Criteria

V18 is successful when:

1. ✓ Hydrogen atom can form and remain stable
2. ✓ H₂ molecule can form with two atoms maintaining bond
3. ✓ Bond breaks when energy insufficient (dissociation)
4. ✓ Atom/molecule moves as unified entity (one imprint)
5. ✓ Wake field correctly models pressure (expansion resistance)
6. ✓ Quantum transitions driven by wake energy
7. ✓ Multiple molecules can coexist without interference
8. ✓ All state fits in Canvas + Process list (no external memory)

---

## Comparison: V17 vs V18

| Aspect | V17 | V18 |
|--------|-----|-----|
| **Entity type** | Renderer (single-entity only) | CompositeProcess (any structure) |
| **Imprint model** | Per-renderer (multi-imprint) | Per-process (unified) |
| **Wake tracking** | None | ∂gamma/∂t field |
| **Tick budget** | Per-renderer | Per-process (shared) |
| **Internal structure** | Implicit position only | Explicit state machine |
| **Composites** | IMPOSSIBLE | Native |
| **RAW-083 compliant** | ✗ VIOLATION | ✓ CORRECT |
| **Scalability** | Single entities only | Atoms, molecules, organisms |

---

## References

- **RAW-083:** Composite Processes and the Unified Imprint Principle
- **RAW-081:** Photon as Degenerate Process
- **RAW-082:** Gamma-Wake Gravity Principle
- **RAW-049:** Temporal Ontology

