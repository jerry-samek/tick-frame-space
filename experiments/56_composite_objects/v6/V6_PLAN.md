# V6 Grid-Based Tick-Frame Model - Implementation Plan

**Date**: 2026-01-24
**Status**: Planning
**Purpose**: Implement true tick-frame physics using discrete Planck cell grid

---

## Executive Summary

V6 is a **complete architectural rewrite** that implements the tick-frame ontology correctly:

- ✅ **Discrete 2D Planck cell grid** (not continuous coordinates)
- ✅ **Ternary field states** {-1, 0, +1} per cell (not float/integer positions)
- ✅ **Sample cells** (5×5 blocks) as pattern canvas (not point particles)
- ✅ **Patterns** as local field configurations (not velocity vectors)
- ✅ **Jitter at Planck level** (±1 per cell per tick, not Gaussian velocity kicks)
- ✅ **Cellular automaton evolution** (not Newtonian force integration)

**Key Insight**: Particles are **emergent stable patterns**, not fundamental objects.

---

## Core Architecture

### 1. Planck Cell Grid

```python
class PlanckGrid:
    """2D grid of discrete Planck cells."""

    def __init__(self, width: int, height: int):
        self.width = width    # Grid width in Planck cells
        self.height = height  # Grid height in Planck cells

        # Grid state: 2D array of ternary values {-1, 0, +1}
        # Shape: (height, width)
        self.field = np.zeros((height, width), dtype=np.int8)

        # Gamma field: radial confinement modulator
        # Shape: (height, width), values in range [0, 255]
        self.gamma = np.zeros((height, width), dtype=np.uint8)
```

**Design decisions**:
- **Grid size**: 200×200 Planck cells (or 400×400 for higher resolution)
- **Boundary conditions**: Periodic (wrap-around) or reflective (TBD)
- **Data type**: `np.int8` for field (-1/0/+1), `np.uint8` for gamma (0-255)
- **Memory**: 200×200 × 2 bytes = 80 KB (very efficient)

---

### 2. Sample Cells and Patterns

```python
class SampleCell:
    """5×5 block of Planck cells forming a pattern canvas."""

    def __init__(self, origin_x: int, origin_y: int, size: int = 5):
        self.origin_x = origin_x  # Top-left corner (Planck grid coords)
        self.origin_y = origin_y
        self.size = size          # 5×5 recommended

    def extract_pattern(self, grid: PlanckGrid) -> np.ndarray:
        """Extract 5×5 pattern from grid at this sample's location."""
        x, y, s = self.origin_x, self.origin_y, self.size
        return grid.field[y:y+s, x:x+s].copy()

    def apply_pattern(self, grid: PlanckGrid, pattern: np.ndarray):
        """Write pattern back to grid."""
        x, y, s = self.origin_x, self.origin_y, self.size
        grid.field[y:y+s, x:x+s] = pattern
```

**Pattern representation**:
```python
# Example: Simple 5×5 dipole pattern
PATTERN_DIPOLE = np.array([
    [ 0,  0,  0,  0,  0],
    [ 0, +1, +1, +1,  0],
    [ 0, +1,  0, +1,  0],
    [ 0, -1, -1, -1,  0],
    [ 0,  0,  0,  0,  0],
], dtype=np.int8)

# Example: Stable monopole pattern
PATTERN_MONOPOLE = np.array([
    [ 0,  0,  0,  0,  0],
    [ 0,  0, +1,  0,  0],
    [ 0, +1, +1, +1,  0],
    [ 0,  0, +1,  0,  0],
    [ 0,  0,  0,  0,  0],
], dtype=np.int8)
```

---

### 3. Pattern Library

```python
class PatternLibrary:
    """Registry of known stable patterns."""

    def __init__(self):
        self.patterns = {
            "monopole": PATTERN_MONOPOLE,
            "dipole": PATTERN_DIPOLE,
            "quadrupole": PATTERN_QUADRUPOLE,
            "rotating": PATTERN_ROTATING,
            # ... more patterns
        }

        # Pattern hashes for fast detection
        self.pattern_hashes = {
            name: self._hash_pattern(p)
            for name, p in self.patterns.items()
        }

    def _hash_pattern(self, pattern: np.ndarray) -> int:
        """Hash pattern for fast lookup."""
        # Convert 5×5 ternary to base-3 number
        flat = pattern.flatten() + 1  # Map {-1,0,+1} -> {0,1,2}
        return sum(int(v) * (3**i) for i, v in enumerate(flat))

    def detect_pattern(self, sample: np.ndarray) -> str | None:
        """Identify pattern in 5×5 sample, or None if unknown."""
        h = self._hash_pattern(sample)
        for name, pattern_hash in self.pattern_hashes.items():
            if h == pattern_hash:
                return name
        return None
```

**Pattern stability**:
- Patterns are **stable** if they reproduce themselves after one tick + jitter + evolution
- Patterns are **unstable** if they dissolve or morph into different patterns
- Collision = two patterns overlap → new composite pattern created

---

### 4. Jitter at Planck Level

```python
class PlanckJitter:
    """Apply integer jitter at the Planck cell level."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def apply_jitter(self, grid: PlanckGrid):
        """
        Each Planck cell receives ±1 jitter with equal probability.

        Jitter modifies field values but respects bounds {-1, 0, +1}:
        - If cell = -1 and jitter = -1 → stays -1 (clamped)
        - If cell = 0 and jitter = +1 → becomes +1
        - etc.
        """
        # Generate ±1 jitter for entire grid
        jitter = self.rng.choice([-1, 0, +1], size=grid.field.shape, p=[0.25, 0.5, 0.25])

        # Apply jitter with clamping to {-1, 0, +1}
        grid.field = np.clip(grid.field + jitter, -1, 1)
```

**Jitter equivalence to V4**:
From STRUCTURE.md:
```
J_planck = J_float / A_pattern
```

For V4: `J_float = 0.0005`, `A_pattern = 25` (5×5 sample)
```
J_planck = 0.0005 / 25 = 0.00002
```

But in discrete model, each cell gets ±1 per tick with probability:
```
P(±1) = 0.25 each
P(0) = 0.5
Expected jitter per cell = 0
Variance per cell = 0.25×1² + 0.25×(-1)² + 0.5×0² = 0.5
```

This creates a random walk with σ² = 0.5 per tick per cell.

**Tuning**: Adjust `p=[p_minus, p_zero, p_plus]` to match V4 diffusion rate.

---

### 5. Gamma Field as Modulator

```python
class GammaField:
    """Radial gamma field modulating pattern stability."""

    def __init__(self, grid: PlanckGrid, center_x: int, center_y: int, k: float):
        self.grid = grid
        self.center_x = center_x
        self.center_y = center_y
        self.k = k  # Field strength

        # Precompute gamma values for entire grid
        self._compute_gamma_field()

    def _compute_gamma_field(self):
        """
        Compute gamma(r) = 1 + k/r² at each Planck cell.

        Stored as uint8 (0-255) representing gamma ∈ [1.0, 2.0]:
        gamma_uint8 = min(255, int((gamma - 1.0) * 255))
        """
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                dx = x - self.center_x
                dy = y - self.center_y
                r_squared = dx*dx + dy*dy

                if r_squared < 1:
                    gamma_val = 2.0  # Maximum at origin
                else:
                    gamma_val = 1.0 + self.k / r_squared

                # Clamp to [1.0, 2.0] and store as uint8
                gamma_clamped = min(2.0, max(1.0, gamma_val))
                self.grid.gamma[y, x] = int((gamma_clamped - 1.0) * 255)

    def get_gamma(self, x: int, y: int) -> float:
        """Get gamma value at cell (x, y)."""
        gamma_uint8 = self.grid.gamma[y, x]
        return 1.0 + (gamma_uint8 / 255.0)
```

**Gamma field role**:
- NOT a force field (no acceleration)
- Modulates **pattern transition probabilities**
- High gamma → patterns more stable (resist jitter)
- Low gamma → patterns less stable (easily disrupted)

---

### 6. Cellular Automaton Evolution

```python
class TickFrameEvolution:
    """Cellular automaton rules for tick-to-tick pattern evolution."""

    def __init__(self, grid: PlanckGrid, gamma_field: GammaField, jitter: PlanckJitter):
        self.grid = grid
        self.gamma_field = gamma_field
        self.jitter = jitter

    def evolve_one_tick(self):
        """
        Execute one tick of evolution:
        1. Apply jitter to all Planck cells
        2. Apply local evolution rules (modulated by gamma)
        3. Detect and track patterns
        """
        # 1. Apply Planck-level jitter
        self.jitter.apply_jitter(self.grid)

        # 2. Apply local evolution rules (Conway-like, but modulated by gamma)
        new_field = self._apply_local_rules()

        # 3. Update grid
        self.grid.field = new_field

    def _apply_local_rules(self) -> np.ndarray:
        """
        Local evolution rules (example - needs refinement):

        For each cell (x, y):
        - Count neighbors with same sign
        - If majority same sign and gamma > threshold → reinforce
        - If minority or gamma < threshold → decay toward zero
        """
        new_field = self.grid.field.copy()

        for y in range(1, self.grid.height - 1):
            for x in range(1, self.grid.width - 1):
                cell_value = self.grid.field[y, x]
                gamma = self.gamma_field.get_gamma(x, y)

                # Count 3×3 neighborhood
                neighbors = self.grid.field[y-1:y+2, x-1:x+2]
                same_sign_count = np.sum(neighbors == cell_value)

                # Evolution rule (example):
                if same_sign_count >= 5 and gamma > 1.5:
                    # Strong consensus + high gamma → persist
                    new_field[y, x] = cell_value
                elif same_sign_count < 3:
                    # Weak consensus → decay toward zero
                    new_field[y, x] = 0
                # else: keep current value

        return new_field
```

**Evolution rules** (to be refined experimentally):
- Similar to Conway's Game of Life but with ternary states {-1, 0, +1}
- Gamma field biases survival/birth probabilities
- Goal: stable patterns emerge near high-gamma regions

---

## Implementation Phases

### Phase 1: Grid and Patterns (Week 1)

**Deliverables**:
1. `planck_grid.py` - PlanckGrid class with field storage
2. `sample_cell.py` - SampleCell class for 5×5 extraction
3. `pattern_library.py` - PatternLibrary with initial patterns
4. `test_grid_basic.py` - Unit tests for grid operations

**Success criteria**:
- Can create 200×200 grid
- Can extract/apply 5×5 patterns
- Can detect patterns via hash lookup
- Grid operations < 1ms

---

### Phase 2: Jitter and Evolution (Week 2)

**Deliverables**:
1. `planck_jitter.py` - PlanckJitter with ±1 random walk
2. `evolution_rules.py` - TickFrameEvolution with CA rules
3. `test_jitter.py` - Validate jitter statistics
4. `test_evolution.py` - Test pattern persistence

**Success criteria**:
- Jitter produces σ² ≈ 0.5 per cell per tick
- Simple patterns (monopole) persist for 1000 ticks
- Unstable patterns dissolve within 100 ticks

---

### Phase 3: Gamma Field and Confinement (Week 3)

**Deliverables**:
1. `gamma_field_v6.py` - GammaField with 1/r² modulation
2. `config_v6.py` - Configuration for V6 parameters
3. `experiment_v6_10k.py` - 10k tick validation
4. `test_gamma_modulation.py` - Test gamma effect on patterns

**Success criteria**:
- Gamma field computes in < 10ms
- Patterns near origin (high gamma) more stable than periphery
- 50 patterns confined to r < 5.0 for 10k ticks

---

### Phase 4: Multi-Pattern Systems (Week 4)

**Deliverables**:
1. `pattern_tracker.py` - Track pattern positions and identities
2. `collision_detection_v6.py` - Detect pattern overlaps
3. `experiment_v6_200k.py` - Full 200k validation
4. `visualization_v6.py` - Visualize grid + patterns

**Success criteria**:
- Initialize 50 patterns at r ≈ 2.0
- Detect collisions when patterns overlap
- Cloud stability: drift < 10% over 200k ticks
- Performance: > 100 ticks/second

---

## Key Differences from V5

| Aspect | V5 (Point Particles) | V6 (Grid-Based) |
|--------|---------------------|-----------------|
| **Space** | Continuous (x, y) floats | Discrete Planck grid |
| **Entity** | Point particle | 5×5 pattern |
| **State** | Position + velocity | Field values {-1, 0, +1} |
| **Jitter** | Gaussian velocity kick | ±1 per Planck cell |
| **Motion** | v → x += v | Pattern shifts on grid |
| **Collision** | Momentum conservation | Pattern overlap/merge |
| **Confinement** | Force F = -k×r | Gamma modulates stability |
| **Evolution** | Newtonian integration | Cellular automaton |

---

## Success Criteria for V6

### Minimal Success (V6.0)
- [ ] 50 patterns initialized at r ≈ 2.0
- [ ] Patterns persist for 10k ticks without dissolving
- [ ] Cloud drift < 50% over 10k ticks
- [ ] No crashes, no NaN values

### Target Success (V6.1)
- [ ] Cloud drift < 10% over 200k ticks (match V4 target)
- [ ] Patterns exhibit stable/unstable classification
- [ ] Collision detection works (patterns merge/fragment)
- [ ] Performance > 100 ticks/second

### Stretch Success (V6.2)
- [ ] Emergent orbital motion (patterns circle origin)
- [ ] Angular momentum conservation (emergent, not enforced)
- [ ] Quantized energy levels (from pattern types)
- [ ] Reproduces V4 statistical distribution

---

## Open Questions

1. **Evolution rules**: What CA rules produce stable patterns?
   - Start with simple majority-rule + gamma bias
   - Refine based on experimentation

2. **Pattern motion**: How do patterns move on the grid?
   - Option A: Shift entire 5×5 block by 1 Planck cell per tick
   - Option B: Patterns dissolve/reform at new location (true CA)
   - **Recommendation**: Start with B (true ontology), try A if too chaotic

3. **Gamma field effect**: How does gamma modulate CA rules?
   - Option A: Gamma increases survival threshold (harder to die)
   - Option B: Gamma biases jitter (less randomness near origin)
   - **Recommendation**: Start with A

4. **Collision dynamics**: What happens when two patterns overlap?
   - Option A: Superposition (add field values, clamp to {-1, 0, +1})
   - Option B: Annihilation (both patterns dissolve)
   - Option C: Merger (new composite pattern created)
   - **Recommendation**: Start with A, observe emergent behavior

5. **Boundary conditions**: Periodic or reflective?
   - **Recommendation**: Periodic (toroidal topology, simpler)

---

## Technical Stack

**Language**: Python 3.11+
**Core libraries**:
- `numpy` - Grid storage and array operations
- `numba` - JIT compilation for CA evolution (10-100× speedup)
- `matplotlib` - Visualization

**Optional (for stretch goals)**:
- `cupy` - GPU acceleration for large grids
- `h5py` - Efficient storage of grid snapshots

---

## Next Steps

1. Create `v6/` directory structure:
   ```
   experiments/56_composite_objects/v6/
   ├── V6_PLAN.md (this file)
   ├── planck_grid.py
   ├── sample_cell.py
   ├── pattern_library.py
   ├── planck_jitter.py
   ├── evolution_rules.py
   ├── gamma_field_v6.py
   ├── config_v6.py
   ├── experiment_v6_10k.py
   ├── experiment_v6_200k.py
   ├── tests/
   │   ├── test_grid_basic.py
   │   ├── test_jitter.py
   │   └── test_evolution.py
   └── results/
   ```

2. Implement Phase 1 (Grid and Patterns)
   - Start with `planck_grid.py`
   - Then `pattern_library.py` with 3-5 basic patterns
   - Write unit tests

3. Validate with simple experiment:
   - Single pattern on 50×50 grid
   - Apply jitter for 1000 ticks
   - Measure pattern persistence

---

## References

- `v5/ONTOLOGY.md` - Core tick-frame concepts
- `v5/STRUCTURE.md` - Spatial hierarchy (Planck cells, samples, patterns)
- `v5/V5_SUMMARY.md` - Lessons learned from V5 failures
- `v4/` - V4 float-based implementation (baseline for comparison)

---

**Status**: READY TO IMPLEMENT
**Estimated timeline**: 4 weeks (Phase 1-4)
**Risk level**: Medium (CA rules need experimentation)
**Confidence**: High (ontology-aligned architecture)
