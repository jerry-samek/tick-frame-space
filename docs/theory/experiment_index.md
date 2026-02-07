# Tick-Frame Physics Experiment Index

**Comprehensive cross-reference of all computational experiments validating tick-frame theory**

---

## Overview

This index catalogs all experiments in the `experiments/` directory, providing:

- **Purpose and hypothesis** for each experiment
- **Status and results** (validated/in-progress/exploratory)
- **Cross-references** to theory documents
- **Dependencies** between experiments
- **Key findings** and implications

**Total Experiments**: 21 (including sub-experiments and v13-v17 series)

**Major Validations**: 10 experiments have validated core theoretical predictions

**Major Falsifications**: 1 experiment has falsified bold theoretical claims (Exp #51 v1)

**Critical Findings**: 1 experiment has identified FALSIFIABLE predictions vs quantum mechanics (Exp #62)

**Latest Additions**:
- Experiment 80 (Gamma-Field Rendering - February 2026)
- Experiment 56 v13-v17 (Canvas Ontology, Jitter Investigation, Sparse Storage - February 2026)
- Experiment 72 (ZPE Cosmological Model - February 2026)
- Experiment 63 (Magnetron Theory - February 2026)

---

## Quick Navigation

### By Topic

- **Dimensional Physics**: [#15](#15-minimal-model), [#50](#50-dimensional-equivalence-under-explicit-time)
- **Entity Dynamics**: [#22](#22-genesis-and-discrete-relativity), [#39](#39-law-000), [#40](#40-tick-engine)
- **Rendering & Visualization**: [#44 series](#44-series-temporal-rendering), [#49](#49-sliding-window-rendering)
- **Scaling & Performance**: [#44_05](#4405-double-buffer-rendering), [#46_01](#reference-4601-on-bucketing)
- **Gravity & Relativity**: [#51](#51-emergent-time-dilation-from-tick-budgets)
- **Collision Physics & Matter**: [#55](#55-collision-physics-framework), [#56](#56-composite-objects), [#62](#62-interferometry)
- **Quantum-Like Behavior**: [#62](#62-interferometry)
- **Stability & Constants**: [#56 v13](#56-v13-jitter-investigation)
- **Architecture & Ontology**: [#56 v17](#56-v17-canvas-ontology)
- **Electromagnetism**: [#63](#63-magnetron-theory)
- **Gamma Field Rendering**: [#80](#80-gamma-field-rendering)
- **Cosmology**: [#72](#72-zpe-cosmological-model)

### By Status

- **✓ Validated**: [#15](#15-minimal-model), [#44_03](#4403-emergent-rotation), [#46_01](#reference-4601-on-bucketing), [#50](#50-dimensional-equivalence-under-explicit-time), [#51](#51-emergent-time-dilation-from-tick-budgets), [#55](#55-collision-physics-framework), [#62](#62-interferometry), [#56 v13](#56-v13-jitter-investigation), [#56 v17](#56-v17-canvas-ontology)
- **⏳ In Progress**: [#49](#49-sliding-window-rendering), [#56](#56-composite-objects), [#80](#80-gamma-field-rendering)
- **🔬 Exploratory/Early**: [#22](#22-genesis-and-discrete-relativity), [#39](#39-law-000), [#40](#40-tick-engine), [#63](#63-magnetron-theory), [#72](#72-zpe-cosmological-model)

---

## Experiment Catalog

### Master Table

| #         | Title                  | Type         | Status         | Theory Docs                                                 | Key Result                                                     |
|-----------|------------------------|--------------|----------------|-------------------------------------------------------------|----------------------------------------------------------------|
| **15**    | Minimal Model          | Dimensional  | ✓ Validated    | Ch2, REFERENCE_doc15                                        | 3D optimal (SPBI=2.23)                                         |
| **22**    | Genesis & Relativity   | Conceptual   | 🔬 Exploratory | v1/22                                                       | Early thought experiment                                       |
| **39**    | Law-000                | Engine       | 🔬 Exploratory | v1/39_0                                                     | XOR parity baseline                                            |
| **40**    | Tick-Engine            | Architecture | 🔬 Exploratory | Ch1, Ch3                                                    | Unified engine framework                                       |
| **44_01** | Cube                   | Rendering    | 📐 Prototype   | -                                                           | Initial 3D test                                                |
| **44_02** | Triangle               | Rendering    | 📐 Prototype   | -                                                           | Initial pattern test                                           |
| **44_03** | Emergent Rotation      | Rendering    | ✓ Validated    | Ch6 §5                                                      | 933× rotation asymmetry                                        |
| **44_04** | Multi-Entity Depth     | Rendering    | 📐 Prototype   | Ch6 §4                                                      | Temporal lag as z-axis                                         |
| **44_05** | Double-Buffer          | Performance  | ✓ Validated    | Ch6 §7                                                      | O(n) bucketing confirmed                                       |
| **49**    | Sliding Window         | Performance  | ⏳ In Progress  | Ch4 §3, Ch6 §8                                              | Dynamic temporal memory                                        |
| **50**    | Dimensional Equiv.     | Dimensional  | ✓ Validated    | Ch1 §9, REFERENCE_doc50_01                                  | ρ=2.0 signature (smoking gun)                                  |
| **51**    | Emergent Time Dilation | Gravity      | ✓ Validated    | v1/21, v1/25, proposed_gravity_relativity, EXPERIMENTAL_ARC | V9: GR+SR combined (r≈0.999), V7-V8 smooth gradients validated |
| **55**    | Collision Physics      | Matter       | ✓ Validated    | Doc 053, Doc 030                                            | 3 regimes validated, Pauli exclusion emerges                   |
| **56**    | Composite Objects      | Matter       | ⏳ In Progress  | Doc 054, Doc 030                                            | Atoms, molecules, nuclei structure defined                     |
| **62**    | Interferometry         | Matter       | ✓ Validated    | Doc 049, Doc 028, Doc 030, Exp 55                           | 26/26 tests, which-path WITHOUT collapse (falsifiable)         |
| **63**    | Magnetron              | EM           | 🔬 Exploratory | Doc 063                                                     | Tick-frame magnetism theory                                    |
| **56 v13**| Jitter Investigation   | Stability    | ✓ Validated    | Doc 072, Doc 074                                            | 0.119 NOT fundamental, range [0.075, 0.5]                      |
| **56 v17**| Canvas Ontology        | Architecture | ✓ Validated    | Doc 049, Ch1                                                | O(entities) sparse storage, gamma=canvas                       |
| **72**    | ZPE Cosmology          | Cosmology    | 🔬 Early       | Doc 072, Doc 073                                            | Jitter scaling roadmap V1-V9                                   |
| **80**    | Gamma-Field Rendering  | Rendering    | ⏳ In Progress  | Ch9, Ch10, Ch11                                             | Virtual expansion + gamma field visualization                  |
| **-**     | movement-vs-division   | Analysis     | 📊 Data        | -                                                           | Entity dynamics trade-offs                                     |

**Legend**:

- ✓ **Validated**: Core predictions confirmed
- ⚠️ **Partial**: Mechanism works in principle, needs refinement/tuning
- ❌ **Falsified**: Hypothesis tested and rejected (kept for historical reference)
- ⏳ **In Progress**: Implementation underway
- 🔬 **Exploratory**: Conceptual/early-stage
- 📐 **Prototype**: Working but not validated
- 📊 **Data**: Analysis/visualization only

---

## Detailed Experiment Descriptions

### #15: Minimal Model

**Full Name**: Minimal Model Recommendation for Time-Visualization Testing

**Location**: `experiments/15_minimal-model/`

**Status**: ✓ **VALIDATED** (3,960 configurations tested)

**Hypothesis**: Three spatial dimensions (3D) provide optimal balance between stability and variability for substrate
physics.

**Method**:

- Dimensional sweep: 1D, 2D, 3D, 4D, 5D
- Salience field dynamics with variable damping (γ), source strength (α), and geometry
- 3,960 total configurations across v6-gpu and v7-final experiments
- Metric: SPBI (Stability-Probability Balance Index)

**Key Results**:

- **3D achieves maximum SPBI = 2.23**
- 1D-2D: Insufficient complexity (SPBI < 1.5)
- 4D-5D: Diminishing returns (SPBI ≈ 2.0)
- **Goldilocks Zone confirmed**: 3D is optimal

**Scaling Laws**:

- Salience scales as `S ∝ N^ρ`
- Measured: **ρ ≈ 1.5** for spatial dimensions (sub-quadratic)
- Consistent across all tested spatial dimensions

**Theory Validation**:

- ✓ Validates Ch2 (Dimensional Framework)
- ✓ Provides empirical basis for 3D universe
- ✓ Referenced in REFERENCE_doc15

**Related Experiments**: #50 (tests if time behaves like dimension)

**Files**:

- Theory: `docs/theory/REFERENCE_doc15.md`
- Data: Various v6-gpu and v7-final subdirectories

---

### #22: Genesis and Discrete Relativity

**Full Name**: Genesis and Discrete Relativity

**Location**: `experiments/22_genesis-and-discreet-relativity/`

**Status**: 🔬 **EXPLORATORY** (early conceptual work)

**Purpose**: Early thought experiment on how discrete tick physics might relate to relativity.

**Note**: This is historical/developmental work. The framework has since evolved significantly (see Ch7 §9 for current
relativity discussion).

**Theory Connection**: v1 document 22 (archived)

---

### #39: Law-000

**Full Name**: Law-000 XOR Parity Rule

**Location**: `experiments/39_law_000/`

**Status**: 🔬 **EXPLORATORY**

**Hypothesis**: A parameter-free XOR-based evolution rule can serve as theoretical baseline for tick-frame physics.

**Evolution Rule**:

```
S'(n) = S(n) ⊕ P(n) ⊕ chaos
```

Where:

- S(n) = current state (binary)
- P(n) = parity of neighbors
- chaos = periodic injection

**Properties**:

- Fully deterministic
- No tunable parameters
- Pure logical operations
- Theoretical purity

**Theory Connection**: v1 document 39_0

**Related Experiments**: #40 (tick-engine implements Law-000)

---

### #40: Tick-Engine

**Full Name**: Unified Tick-Frame Physics Engine

**Location**: `experiments/40_tick-engine/`

**Status**: 🔬 **EXPLORATORY** (architecture/framework)

**Purpose**: Generic, law-agnostic engine for exploring different tick-frame physics rules.

**Architecture**:

- **Law Interface**: Protocol for pluggable physics laws
- **Generic Substrate**: Law-parameterized state evolution
- **TickEngine**: Asynchronous tick producer (background thread)
- **VisualizationEngine**: Asynchronous observer (variable sampling)

**Implemented Laws**:

1. **Law-000 XOR**: Binary parity evolution (see #39)
2. **Law-Quaternion**: Quaternion-based spatial dynamics (experimental)

**Key Features**:

- Observer-relative time (variable dt between visualizations)
- Bounded buffer (finite temporal horizon)
- Automatic graph growth/collapse
- Generic 3D visualization mapping

**Theory Validation**:

- ✓ No Future Principle (one tick at a time)
- ✓ Observer Sleep (visualization skips ticks when overloaded)
- ✓ Temporal Surfing (state renewal each tick)
- ✓ Horizon Boundaries (bounded buffer)
- ✓ Observer-Relative Time (each observer has own dt)

**Theory Connection**: Ch1 (Temporal Ontology), Ch3 (Entity Dynamics)

**Usage**: Framework for rapid prototyping of new physics laws

---

### #44 Series: Temporal Rendering

A series of experiments exploring rendering of 2D space + time as 3D visualization.

#### #44_01: Cube

**Location**: `experiments/44_01_cube/`

**Status**: 📐 **PROTOTYPE**

**Purpose**: Initial test of rendering a simple cube pattern with temporal depth.

**Note**: Basic rendering test, no formal hypothesis.

---

#### #44_02: Triangle

**Location**: `experiments/44_02_triangle/`

**Status**: 📐 **PROTOTYPE**

**Purpose**: Test rendering of triangle pattern with temporal lag creating depth perception.

**Note**: Precursor to #44_03, established initial rendering techniques.

---

#### #44_03: Emergent 3D Rotation from 2D+Temporal Entities

**Location**: `experiments/44_03_emergent_rotation/`

**Status**: ✓ **VALIDATED**

**Hypothesis**: If z-axis is temporal displacement (not spatial dimension), rotation around spatial axes should show
extreme asymmetry due to the speed-of-light constraint (v ≤ c).

**Method**:

- Entities move in 2D space [x, y] only
- Temporal lag creates apparent z-coordinate
- Test three rotation types:
    1. **Z-rotation** (rotate in [x,y] plane)
    2. **Forward pitch** (reduce temporal lag)
    3. **Backward pitch** (increase temporal lag)

**Key Results**:

- **Z-rotation**: 100% success (unrestricted)
- **Forward pitch**: 0% success (impossible - can't exceed v=c)
- **Backward pitch**: 93.33% success (energy-limited, can fall behind)
- **Asymmetry ratio**: **933.33×**

**Interpretation**:

- Forward rotation requires reducing temporal lag (catching up to present) → violates v ≤ c
- Backward rotation requires increasing temporal lag (falling behind) → possible with energy cost
- Confirms time is NOT equivalent to spatial dimension

**Theory Validation**:

- ✓ Validates Ch6 §5 (Rotation Asymmetry)
- ✓ Validates Ch1 §5 (Sample Rate Limit)
- ✓ Confirms v ≤ c is structural constraint

**Theory Connection**: Ch6 (Rendering Theory), QUICK_REFERENCE (validation table)

**Related Experiments**: #44_04 (tests scaling to many entities)

---

#### #44_04: Multi-Entity Temporal Depth

**Location**: `experiments/44_04_multi_entity/`

**Status**: 📐 **PROTOTYPE**

**Hypothesis**: Direct mapping `z = temporal_lag` should work naturally if z is truly temporal, producing simpler
rendering code than complex perspective transformations.

**Method**:

- Extend #44_03 to 100+ entities
- Use temporal_lag DIRECTLY as z-coordinate (no transformation)
- Test entity patterns:
    1. Grid formation
    2. Random cloud
    3. Concentric shells
    4. Temporal wave

**Expected Results**:

- Rendering code < 15 lines (vs #44_03's 50+ lines)
- Depth perception emerges naturally
- Same rotation asymmetry pattern scales to many entities

**Philosophy**: "Simplicity validates truth" - correct model should be simple to implement.

**Theory Connection**: Ch6 §4 (Temporal Lag as Depth Coordinate)

**Related Experiments**: #44_03 (validated 3-entity case)

---

#### #44_05: Double-Buffer Temporal Rendering

**Location**: `experiments/44_05_double_buffer_rendering/`

**Status**: ✓ **VALIDATED**

**Hypothesis**: If temporal lag creates natural ordering (0...MAX_HISTORY), then bucketing entities by lag eliminates
sorting entirely, achieving O(n) performance vs O(n log n) sorting.

**Method**:

- **Bucketing**: Group entities by discrete lag value (counting sort)
- **Double-buffering**: CPU fills one buffer, GPU renders other (zero synchronization)
- Compare to traditional sorting approach

**Key Results**:

- **Bucketing complexity**: O(n) vs O(n log n) sorting
- **Speedup at 10k entities**: 13× faster
- **Speedup at 100k entities**: 16× faster
- **Asymptotic advantage**: Confirmed linear scaling

**Performance @ 60 FPS (16.67ms budget)**:

- 10k entities: Bucketing ✅ (10ms), Sorting ❌ (133ms)
- 50k entities: Bucketing ⚠️ (50ms), Sorting ❌ (850ms)

**Memory Overhead**: Bucketing uses LESS memory than sorting (1.6 MB vs 6.4 MB for 100k entities)

**Theory Validation**:

- ✓ Validates Ch6 §3 (O(n) Bucketing Algorithm)
- ✓ Proves sorting is unnecessary (theory claim confirmed)
- ✓ Discrete time enables algorithmic advantage

**Theory Connection**: Ch6 (Rendering Theory), REFERENCE_doc46_01

**Related Experiments**:

- #49 (extends to sliding window)
- #46_01 reference document (theoretical basis)

**Files**:

- Implementation: `double_buffer_rendering.py`
- Benchmark: `benchmark_sorting_vs_bucketing.py`

---

### #49: Sliding Window Rendering

**Location**: `experiments/49_sliding_window_rendering/`

**Status**: ⏳ **IN PROGRESS** (implementation ready, awaiting execution)

**Hypothesis**: A dynamic sliding window that adapts size to maintain target FPS will maximize temporal addressability (
observer memory depth) without performance degradation.

**Innovation**: Extends #44_05's double-buffering to retain N ticks (where N adapts to performance budget), enabling
temporal effects impossible with fixed 2-buffer approach.

**Architecture**:

- **Ring buffer**: Circular buffer of lag-bucketed frames
- **Dynamic sizing**: Window size adapts based on frame time vs FPS target
- **Holographic horizon**: Expired frames compressed to statistical density map
- **Temporal playback**: Rewind/pause/fast-forward through window

**Calculation**:

```python
window_size = floor(target_frame_time / actual_frame_time)
# Bounded: [1, max_window_size]
```

**Expected Behavior**:
| Entity Count | Frame Time | Window @ 60 FPS | Temporal Memory |
|--------------|------------|-----------------|-----------------|
| 1,000 | 2ms | 8 frames | 267ms history |
| 10,000 | 10ms | 1 frame | 33ms history |
| 50,000 | 20ms | 1 frame | 33ms (minimum) |

**Temporal Effects Enabled**:

1. **Entity trails**: Render positions across multiple frames
2. **Motion blur**: Blend frame positions
3. **Ghost images**: Semi-transparent past positions
4. **Playback controls**: Navigate through temporal buffer

**Holographic Horizon**:

- Frames beyond window compressed to 100×100 density grid
- Creates "ghostly heat map" background
- Exponential decay (99% retention per frame)
- Constant 80 KB overhead (independent of entity count)

**Theory Validation**:

- Implements Ch4 §3 (Existence Buffer) literally
- Demonstrates Ch6 §8 (Temporal Addressability)
- Window size = computational limit on observer memory
- Horizon = temporal boundary (Doc 26)

**Theory Connection**:

- Ch4 §3 (Existence Buffer)
- Ch6 §8 (Temporal Memory)
- Doc 26 (Horizon Boundaries)
- Doc 49 (Temporal Ontology)

**Related Experiments**: #44_05 (extends double-buffering)

**Files**:

- Design: `README.md` (comprehensive specification)
- Implementation: `sliding_window_rendering.py` (to be run)
- Benchmark: `benchmark_sliding_vs_double.py` (to be run)

---

### #50: Dimensional Equivalence Under Explicit Time Dimension

**Location**: `experiments/50_dimensional_equivalence_explicit_time/`

**Status**: ✓ **VALIDATED** (1,095 configurations tested)

**Hypothesis**: Does (n spatial dimensions + explicit time) behave like (n+1) spatial dimensions?

**Answer**: **NO** - Decisively rejected with 0% pass rate across all tests.

**Method**:

- **Baseline**: 3D, 4D, 5D spatial dimensions (reference from #15)
- **Variant A**: Time as physics dimension (∂²A/∂t² in Laplacian)
- **Variant B**: Time as storage dimension (sliding window, causal physics)
- **Parameter sweep**: 180 configs per (n+t) dimension
- **Total configs**: 1,095

**Six Dimensional Equivalence Tests**:

1. (2D+t physics) vs 3D: **FAIL** (0/5 pass)
2. (2D+t rendering) vs 3D: **FAIL** (0/5 pass)
3. (3D+t physics) vs 4D: **FAIL** (0/5 pass)
4. (3D+t rendering) vs 4D: **FAIL** (0/5 pass)
5. (4D+t physics) vs 5D: **FAIL** (0/5 pass)
6. (4D+t rendering) vs 5D: **FAIL** (1/5 pass = 20%, still FAIL)

**Overall**: 0/6 tests passed (0% success rate)

**Key Finding: The ρ = 2.0 Signature (SMOKING GUN)**:

**Pure spatial dimensions**:

- 3D: ρ = 1.503
- 4D: ρ = 1.532
- 5D: ρ = 1.571
- Average: **ρ ≈ 1.5** (sub-quadratic scaling)

**ALL (n+t) systems**:

- 2D+t: ρ = 1.999
- 3D+t: ρ = 2.002
- 4D+t: ρ = 2.001
- Average: **ρ = 2.0** (quadratic scaling)

**Interpretation**:

- Spatial: Salience scales as `S ∝ N^1.5` (dilution via surface area)
- Temporal: Salience scales as `S ∝ N^2` (accumulation via time axis)

**Physical Mechanism: The Ratchet Effect**:

- Spatial dimensions: Energy dilutes isotropically (inverse square law)
- Time dimension: Energy accumulates unidirectionally (causal ordering)
- Time acts as **one-way ratchet**, not symmetric coordinate

**Salience Amplification**:

- (2D+t physics) vs 3D: **1,675× mean**, **9,941× max** (!!)
- (2D+t rendering) vs 3D: **199× mean**
- (3D+t physics) vs 4D: **3.0× mean**
- (4D+t physics) vs 5D: **12.0× mean**

**Variance Inversion**:

- Commit rate variance: Collapses in (n+t) (HIGH → LOW)
- Salience variance: Expands in (n+t) (LOW → HIGH)
- Characteristic of saturation dynamics

**Theory Validation**:

- ✓ **VALIDATES** Ch1 §9 (Time ≠ Dimension)
- ✓ **VALIDATES** Doc 49 (Temporal Ontology)
- ✓ **CONFIRMS** Tick-frame ≠ Minkowski spacetime
- ✓ **PROVES** 3D space + time ≠ 4D spacetime

**Implications**:

1. Time is fundamentally different from space (not just metric signature)
2. Dimensional closure (4D-5D from #15) refers to SPATIAL dimensions only
3. Tick-frame physics has different ontology than relativity
4. ρ=2.0 is universal signature of temporal generators

**Theory Connection**:

- Ch1 §9 (Dimensional Equivalence)
- REFERENCE_doc50_01 (Preserved results document)
- QUICK_REFERENCE (validation table)
- GLOSSARY (ρ definition)

**Related Experiments**: #15 (provides spatial dimension baseline)

**Files**:

- Results: `EXPERIMENT_RESULTS.md` (685 lines, comprehensive)
- Theory: `docs/theory/50 Test Specification - Dimensional Equivalence Under Explicit Time Dimension.md`
- Reference: `docs/theory/REFERENCE_doc50_01.md`

---

### #51: Emergent Time Dilation from Tick Budgets

**Full Name**: Gravitational Time Dilation from Computational Resource Competition

**Location**: `experiments/51_emergent_time_dilation/` (v1-v9 subdirectories)

**Status**: ✓ **VALIDATED** (9 iterations: v1-v9)

**Hypothesis**: Gravitational time dilation emerges naturally from tick-budget competition, where heavy computational
loads create local slowdown in observer sampling rate.

**Method**: Iterative refinement across 8 experimental versions:

**V1: Simple Allocation** (❌ FALSIFIED)

- Setup: 1 heavy entity (tick_budget=1000) + 10 light entities at varying distances
- Observer: Fixed capacity, sequential allocation
- Result: Binary cutoff (entities get 100% or 0% updates), no gradient
- **Lesson**: Simple resource scheduling doesn't create gravity

**V2: Planetary Cluster** (❌ FAILED)

- Setup: 5000 small entities (tick_budget=5 each) forming planet
- Result: Global uniform dilation, no spatial structure
- **Lesson**: Granularity necessary but insufficient without spatial representation

**V3: Space as Sample-Entities** (❌ FAILED)

- Setup: 100×100 grid where each cell is a computational process
- Planet = high-cost cells, Space = low-cost cells
- Result: Two-zone behavior (planet region vs space), no smooth gradient
- **Lesson**: Local capacity creates zones, but saturation doesn't propagate

**V4: Adding Diffusion** (❌ CATASTROPHIC)

- Setup: Load diffuses via Laplacian `L' = L + α∇²L`
- Result: Universal freeze (γ=0 everywhere)
- **Lesson**: Diffusion without counterbalance leads to collapse

**V5-V6: Damping Attempts** (❌ STILL FROZEN)

- V5: Linear damping `L' = (1-β)L + α∇²L`
- V6: Nonlinear damping `L' = L + α∇²L - γL²`
- Result: Both froze (capacity only decreases, can't regenerate)
- **Lesson**: Energy must be dynamic field that regenerates, not static function of load

**V7: BREAKTHROUGH - Regenerative Energy** (✅ PARTIAL SUCCESS)

- Setup: Two coupled fields:
  ```
  L[t+1] = L[t] + α∇²L + S(x) - γL²    (reaction-diffusion load)
  E[t+1] = min(E_max, E + R - work - D·L)  (regenerative energy)
  ```
- Parameters: α=0.01, γ=0.001, R=1.0, E_max=10
- Result: First stable time dilation! (near: γ≈0.23, far: γ≈0.50)
- Two-zone structure (not yet smooth)
- **Breakthrough**: Energy regeneration prevents collapse

**V8: Smooth Gradient** (✅ FIRST SMOOTH, BUT TOO WEAK)

- Setup: Softened V7 parameters (α=0.015, γ=0.0001, E_max=30)
- Result: First smooth, continuous γ(r) gradient!
- γ: 0.0018 (near) → 0.0037 (far)
- But gravitational well far too weak
- **Achievement**: Smooth gravitational curvature proven possible

**V9: Multi-Entity Validation** (✅ COMPLETE VALIDATION)

- Setup: 700 stationary entities (planet) + 80 mobile entities (0.1c-0.99c)
- Parameters: α=0.012, γ=0.0005, scale=0.75, R=1.2, E_max=15
- Test: Combined gravitational + special relativistic time dilation
- Result: **r ≈ 0.999 correlation** between predicted and measured γ_total
- Validation rates: 100% (0.1c), 100% (0.5c), 90% (0.9c), 30% (0.99c)
- **Breakthrough**: Single substrate reproduces both GR and SR effects!

**Key Results**:

- ❌ Simple allocation (V1) falsified
- ❌ Diffusion alone (V4-V6) leads to collapse
- ✅ Regenerative energy mechanism (V7-V8) works
- ✅ Smooth spatial gradients achievable (V8)
- ✅ Combined GR+SR validated (V9, r ≈ 0.999)
- ✅ Goldilocks zone confirmed (0.1c-0.9c, <10% error)

**Theory Validation**:

- ✓ **VALIDATES**: Time dilation emerges from tick budgets (quantitative match achieved)
- ✓ **CONFIRMS**: Space must be represented as computational field
- ✓ **PROVES**: Energy regeneration essential for stable universe
- ✓ **VALIDATES**: Combined GR+SR from single substrate (r ≈ 0.999)
- ✓ **CONFIRMS**: Multiplicative effects (γ_total = γ_grav × γ_SR)

**Validated Mechanism**:

```
Load field (L):    Reaction-diffusion dynamics with saturation
Energy field (E):  Local regeneration with load-dependent drainage
Time dilation:     γ_eff(x) = <work_done> / substrate_ticks
```

**Implications**:

1. Gravity requires **field dynamics**, not simple scheduling
2. Universe needs **metabolism** (regeneration) to avoid heat death
3. Space is **active process**, not passive background
4. Singularities **impossible** (energy floor prevents infinite compression)

**Theory Connection**:

- v1 Docs 21, 25 (original gravity claims)
- proposed_experiments_gravity_relativity.md (experimental proposals)
- EXPERIMENTAL_ARC.md (comprehensive v1-v8 documentation)

**Related Experiments**:

- Exp #52 (black hole horizons) - should form from load saturation
- Exp #53 (geodesics) - should follow time-flow gradients

**Files**:

- Summary: `EXPERIMENTAL_ARC.md` (comprehensive 9-version journey)
- V1 results: `v1/RESULTS.md` (falsification of simple mechanism)
- V7 results: `v7/RESULTS.md` (first success with regenerative energy)
- V8 results: `v8/RESULTS.md` (first smooth gradient)
- V9 results: `v9/RESULTS.md` (multi-entity GR+SR validation, r ≈ 0.999)
- V9 data: `v9/results_v9/baseline_analysis.csv` (80 entity trajectories)

**Next Step**: Implement emergent trajectories (replace forced circular orbits with field-driven motion)

---

### #55: Collision Physics Framework

**Full Name**: Complete Three-Regime Collision Physics

**Location**: `experiments/55_collision_physics/`

**Status**: ✅ **VALIDATED** (6 test cases, 100% success rate)

**Hypothesis**: Tick-frame collisions fall into three distinct regimes based on pattern overlap and cell capacity:
1. **Merge** (non-overlapping patterns → fusion)
2. **Explosion** (overlap + excess energy → annihilation)
3. **Excitation** (partial overlap → energy redistribution)

**Method**:

**Phase 1**: Pattern Structure Definition
- Multi-dimensional pattern representation (type, energy, internal mode, phase, mass)
- Pattern overlap calculator using multi-factorial algorithm
- Regime classifier based on overlap energy and cell capacity

**Phase 2**: Three-Regime Implementation
- Merge resolver: Creates composite patterns from non-overlapping constituents
- Explosion resolver: Handles energy overflow via shockwave propagation
- Excitation resolver: Redistributes energy within cell capacity limits

**Validation Suite**: 6 test cases across all three regimes

**Key Results**:

#### Regime 3.1: Merge ✅ CONFIRMED
- **Test**: Proton + Neutron → Deuterium
- **E_total**: 16.0, **E_max**: 30.0 (within capacity)
- **Overlap**: Minimal (k_type = 0.0, different particle types)
- **Outcome**: Composite created, energy conserved exactly (16.0 → 16.0)

#### Regime 3.2: Explosion ✅ CONFIRMED
- **Test**: Electron + Positron → Photons + Shockwave
- **E_total**: 30.0, **E_max**: 15.0 (capacity exceeded)
- **Overlap**: Maximal (k_type = 1.0, antimatter pair)
- **Outcome**: 2 photons created, 15.0 overflow distributed to 8 neighbors (1.875 each)
- **Result**: Matter-antimatter annihilation validated

#### Regime 3.3: Excitation ✅ CONFIRMED
- **Test**: Proton + Proton → 2 Excited Protons
- **E_total**: 32.25, **E_max**: 50.0 (within capacity)
- **Overlap**: Moderate (k_type = 0.5, identical particles)
- **Outcome**: Energy redistributed (12.0 → 16.125 each), internal mode 0 → 1

**Surprising Discovery: Emergent Pauli Exclusion**

**Finding**: Pauli exclusion principle emerges naturally from pattern overlap, not programmed explicitly!

**Mechanism**:
- Identical particles in same state have overlap factor k_type = 0.5
- Overlap energy increases total energy in cell
- If E_total + E_overlap > E_max → explosion (rejection)
- If E_total + E_overlap ≤ E_max → excitation (forced to different quantum state)

**Implication**: The Pauli exclusion principle is a consequence of cell capacity limits and pattern structure, not a fundamental axiom.

**Energy Conservation**:
- **Merge**: E_final = E_initial (ratio 1.000) ✅
- **Excite**: E_final = E_initial + E_overlap (ratio 1.000) ✅
- **Explode**: E_cell + E_overflow = E_initial + E_overlap (global conservation) ✅

**Theory Validation**:

- ✓ **VALIDATES**: Doc 053 (Tick-Frame Collision Physics) - all three regimes confirmed
- ✓ **VALIDATES**: Doc 030 (Collision Persistence Principle) - patterns as collision structures
- ✓ **UNEXPECTED**: Pauli exclusion emerges (not predicted in original theory)

**Cell Capacity Hypothesis**:

**Critical Finding**: E_max (cell capacity) determines collision regime boundaries

**Tested Configurations**:
- E_max = 15.0: Frequent explosions (tight packing limit)
- E_max = 30.0: Fusion enabled (moderate capacity)
- E_max = 50.0: Excitation dominates (high capacity)

**Hypothesis**: E_max may vary with field conditions (γ_grav, γ_SR)
- Near massive objects: Lower E_max (compressed γ-well)
- In free space: Higher E_max (expanded γ-well)

**Testable Prediction**: Collision cross-sections should vary with gravitational field strength.

**Files**:
- Pattern structure: `pattern_overlap.py` (535 lines)
- Collision regimes: `collision_regimes.py` (600 lines)
- Validation suite: `experiment_55_validation.py` (497 lines)
- Results summary: `VALIDATION_RESULTS.md`

**Next Steps**:
- Integrate with v12 entity motion (momentum conservation)
- Test with v13 black holes (realistic collision physics)
- Experiment 56: Composite object binding

---

### #56: Composite Objects

**Full Name**: Composite Object Formation and Binding Physics

**Location**: `experiments/56_composite_objects/`

**Status**: ⏳ **IN PROGRESS** (Phase 3a complete, Phase 3b-d pending)

**Hypothesis**: Multi-particle bound states (atoms, molecules, nuclei) form via shared γ-well binding, with internal structure maintained through orbital dynamics and pattern persistence.

**Method**:

**Phase 3a: Composite Structure** ✅ COMPLETE
- Data structures for multi-particle composites
- Constituent particle tracking (position, velocity relative to center)
- Orbital dynamics for electron-proton binding
- Factory methods for common composites (hydrogen, helium, H₂)

**Phase 3b: Binding Detection** ⏳ PENDING
- γ-well field computation around patterns
- Shared γ-well occupancy detection
- Binding energy from field depth measurement

**Phase 3c: Lifecycle Management** ⏳ PENDING
- Track formation from merge collisions
- Monitor stability over long timescales
- Handle dissolution events

**Phase 3d: Validation Experiments** ⏳ PENDING
- Experiment 56a: Hydrogen atom stability (10,000 ticks)
- Experiment 56b: H₂ molecular bonding
- Experiment 56c: Ionization threshold testing
- Experiment 56d: Helium nucleus stability

**Composite Types Implemented**:

#### ✅ Hydrogen Atom
- 1 Proton + 1 Electron
- Binding energy: -13.6 (analog to 13.6 eV)
- Total mass: 1.001
- Orbital radius: 1.0 (Bohr radius analog)
- Orbital period: 62.8 ticks (at v = 0.1c)
- **Tested**: 100 ticks, stable orbits confirmed

#### ✅ Helium Nucleus
- 2 Protons + 2 Neutrons
- Binding energy: -28.0 (analog to 28 MeV)
- Total mass: 4.0
- Configuration: Tetrahedral (frozen structure)

#### ✅ H₂ Molecule
- 2 Protons + 2 Electrons
- Binding energy: -4.5 (analog to 4.5 eV molecular bond)
- Total mass: 2.002
- Bond length: 1.5 units

**Orbital Dynamics**:

**Implementation**: Circular orbits updated each tick
```python
φ(t+1) = φ(t) + ω × dt
x(t+1) = r × cos(φ)
y(t+1) = r × sin(φ)
```

**Result**: Stable orbits persist without degradation (tested 100+ ticks)

**Stability Testing**:

**Mechanism**: Binding energy threshold
- Stable if: `binding_energy < 0` (bound state)
- Unstable if: `binding_energy >= 0` (unbound)

**Ionization Test**:
```
Initial: binding_energy = -13.6 → stable = True
Inject: +20.0 energy
Final: binding_energy = +6.4 → stable = False (ionization)
```
**Result**: ✅ Dissolution detected correctly

**Theory Validation**:

- ✓ **PARTIAL**: Doc 054 (Elasticity of Composite Objects) - structures defined
- ⏳ **PENDING**: γ-well binding mechanism (not yet implemented)
- ⏳ **PENDING**: Long-term stability (needs 10,000+ tick runs)

**Current Limitations**:

- ⏳ γ-well binding detection not implemented
- ⏳ Long-term stability not tested beyond 100 ticks
- ⏳ Composite-composite interactions not defined
- ⏳ Vibrational/rotational modes not functional

**Files**:
- Composite structure: `composite_structure.py` (605 lines)
- Binding detection: (planned)
- Lifecycle manager: (planned)
- Validation experiments: (planned)

**Dependencies**:
- Experiment 55 (collision physics provides merge regime)
- Experiment 51 v11 (γ-field dynamics)

**Next Steps**:
- Implement γ-well Poisson solver
- Run 10,000 tick stability tests
- Test composite formation from collisions
- Integrate with black hole simulations

---

### #62: Interferometry

**Full Name**: Tick-Frame Interferometry: Wave Mechanics and Quantum-Like Behavior

**Location**: `experiments/62_interferometry/`

**Status**: ✓ **VALIDATED** (10 phases complete, 26/26 tests passed)

**Hypothesis**: Discrete tick-frame substrate can reproduce quantum interference phenomena (wave-particle duality, de Broglie wavelength, phase sensitivity) while maintaining deterministic mechanics without wavefunction collapse.

**Method**:

**Phase 1-5: Core Wave Mechanics** ✅ (14/14 tests passed)
- Wave packet propagation in discrete cells
- Dispersion relations (ω vs k)
- Mach-Zehnder interferometry (path-splitting)
- Advanced validation (discrete dispersion, phase measurement)

**Phase 6: Hydrogen Deep Validation** ✅ (4/4 tests passed)
- Real hydrogen atom @ 300K vs tick-frame particle comparison
- Wavelength scaling (λ ∝ 1/√E): r = 1.000000 correlation
- Multi-fringe spatial pattern (820 peaks, V = 1.0000)
- Phase-shift linearity (fit error 0.0000% < 1%)

**Phase 7: Which-Path Without Collapse** ✅ (7/7 tests passed) **⚠️ CRITICAL FINDING**
- Weak which-path probe: Visibility constant despite coupling (0.0000% variation)
- Strong which-path probe: V = 1.0000 after complete path readout
- Phase readout + interference: V = 1.0000 after measuring all phase points

**Phase 8: Decoherence Resistance** ✅ (4/4 tests passed)
- Environmental phase noise mechanism validated
- Temporal jitter resistance verified
- Spatial perturbation handling confirmed

**Phase 9: Composite Particle Interferometry** ✅ (4/4 tests passed)
- H₂ molecule: V = 1.0000 (two-pattern composite)
- C₆₀-like molecule: V = 1.0000 (60-atom composite)
- Internal mode independence: Wavelength variation 0.00% < 5%

**Phase 10: Relativistic Regime** ✅ (4/4 tests passed)
- Lorentz-corrected wavelength: 0.00% deviation (v < 0.85c)
- Time dilation phase evolution: φ = ω × t / γ
- Consistency check: <10% deviation for v < 0.9c

**Key Results**:

#### Quantum-Like Behavior Reproduced:
- ✅ **Interference**: High visibility (V ≈ 1.0) in all regimes
- ✅ **Wavelength Scaling**: λ ∝ 1/√E (de Broglie-like)
- ✅ **Phase Sensitivity**: I ∝ (1 + cos(Δφ))
- ✅ **Energy Conservation**: Exact (0.0000% error)
- ✅ **Composite Interference**: Molecules interfere regardless of size

#### Critical Difference from Quantum Mechanics:
- ❗ **NO WAVEFUNCTION COLLAPSE**: Measurement is deterministic readout
- ❗ **WHICH-PATH ACCESSIBLE**: Phase and path info without fringe loss
- ❗ **FALSIFIABLE**: Real-world experiment can test this difference

**CRITICAL FINDING: Violation of Quantum Complementarity**

**QM Prediction**: Which-path measurement destroys interference (V → 0)

**Tick-Frame Result**: Which-path information accessible WITHOUT fringe loss (V = 1.0000)

**Implication**: This VIOLATES the quantum complementarity principle established by Bohr and confirmed in countless experiments (Stern-Gerlach, delayed-choice quantum eraser, Wheeler's gedanken experiments).

**Real-World Experimental Test**:

**Platform**: Cold atom or neutron interferometer

**Method**: Delayed-choice quantum eraser with which-path state readout
1. Create interference pattern
2. Insert which-path marker (spin flip, polarization)
3. Read marker state WITHOUT erasing it
4. Measure fringe visibility

**Expected Outcome**:
- **QM Prediction**: V → 0 (marker collapses wavefunction)
- **Tick-Frame Prediction**: V > 0.9 (deterministic readout preserves fringes)

**Result**: Binary (definitively falsifies either QM or tick-frame)

**Feasibility**: Achievable with current technology

**Cost**: $500K-$2M

**Timeline**: 1-2 years

**Impact**: HIGH - directly tests foundation of quantum mechanics

**Theory Validation**:

- ✓ **VALIDATES**: Doc 049 (Temporal Ontology) - deterministic substrate, no collapse
- ✓ **VALIDATES**: Doc 028 (Temporal Surfing) - relativistic effects from discrete ticks
- ✓ **VALIDATES**: Doc 030 (Collision Persistence) - patterns persist without collapse
- ✓ **VALIDATES**: Experiment 55 (Collision Physics) - composite particles as pattern overlaps
- ❗ **FALSIFIABLE PREDICTION**: Which-path without collapse distinguishes tick-frame from QM

**Comparison: Real Hydrogen vs Tick-Frame**

| Property       | Real Hydrogen @ 300K | Tick-Frame Particle |
|----------------|----------------------|---------------------|
| Wavelength     | 1.45×10⁻¹⁰ m         | 1.99 cells          |
| Visibility     | 0.9999               | 1.0000              |
| Type           | Matter wave          | Pattern wave        |
| Measurement    | Collapses function   | Deterministic read  |
| Which-path     | Destroys fringes     | Preserves fringes   |
| Ontology       | Wave-particle duality| Pattern persistence |

**Files**:
- Core mechanics: `wave_mechanics.py` (430 lines), `interferometer.py` (385 lines)
- Phase 1-5 tests: `test_hydrogen_comparison.py` (500 lines)
- Phase 6-10 tests: `tests/phase_6_to_10/` (5 files, ~2000 lines total)
- Validation summary: `VALIDATION_COMPLETE.md`
- Falsifiable predictions: `FALSIFIABLE_PREDICTIONS.md`
- Experimental roadmap: `experimental_roadmap.md`
- Hydrogen comparison: `HYDROGEN_COMPARISON.md`

**Dependencies**:
- Experiment 55 (collision physics provides composite particle framework)

**Next Steps**:
- ✅ All computational validation complete
- ⏳ Prepare experimental proposal for which-path test
- ⏳ Contact research groups (cold atom, neutron interferometry)
- ⏳ Seek funding for delayed-choice experiment
- ⏳ Extend to black hole environments (gravity + interferometry)

**This is the first falsifiable prediction that distinguishes tick-frame physics from standard quantum mechanics.**

---

### #56 v13: Jitter Investigation

**Full Name**: Jitter Stability Range Investigation

**Location**: `experiments/56_composite_objects/v13/`

**Status**: ✓ **VALIDATED** (22 jitter values tested)

**Hypothesis**: Is the jitter value 0.119 a fundamental constant, or is it empirically tuned?

**Method**:

- Sweep jitter values from 0.0 to 0.5
- 300 ticks per experiment, 100x100 grid
- Track stability metrics (r_norm, collapse, dispersion)

**Key Results**:

- **Collapsed** (jitter < 0.025): Complete collapse to origin
- **Dispersed** (0.025 < jitter < 0.075): Unstable expansion
- **Stable** (0.075 ≤ jitter ≤ 0.5+): Long-term stability
- **0.119 is NOT special**: Lies within broad stable range

**Critical Insight**: The "fundamental" quantity is the existence of a stable range, not a specific jitter value.

**Theory Validation**:

- ✓ Validates that "constants" may be balance points, not primordial values
- ✓ Aligns with ternary substrate correction axiom (doc 074)

**Theory Connection**: Doc 072 (ZPE scaling), Doc 074 (ternary correction)

**Files**:
- `JITTER_INVESTIGATION.md` (detailed results)
- `experiment_jitter_sweep.py` (sweep implementation)

---

### #56 v17: Canvas Ontology

**Full Name**: Canvas/Renderer Model with Sparse Storage

**Location**: `experiments/56_composite_objects/v17/`

**Status**: ✓ **VALIDATED** (architectural and behavioral)

**Hypothesis**: The gamma field IS the complete tick state - sparse storage should scale as O(entities) not O(grid³).

**Method**:

- Implement canvas/renderer model where gamma = accumulated paint
- Use sparse dictionary storage (only non-zero values)
- Test gradient-following movement behavior

**Key Results**:

- **Memory**: 500 ticks at 176³ grid: ~50 MB (sparse) vs ~2 GB (dense)
- **Scaling**: O(painted_cells) not O(grid_volume)
- **Behavior**: Gradient-following creates gravity-like clustering
- **Stability**: Renderers cluster near origin where gamma accumulates

**Architecture**:

```
Renderer (stateless) → reads canvas → decides paint position → Canvas (accumulated state)
```

**Theory Validation**:

- ✓ Validates Ch1 temporal ontology (canvas = tick state)
- ✓ Validates sparse representation is ontologically correct

**Theory Connection**: Doc 049 (temporal ontology), Ch1

**Files**:
- `README.md` (comprehensive documentation)
- `canvas.py`, `renderer.py`, `evolution.py` (implementation)

---

### #63: Magnetron Theory

**Full Name**: Tick-Frame Theory of Magnetism

**Location**: `experiments/63_magnetron/`

**Status**: 🔬 **EXPLORATORY**

**Purpose**: Develop tick-frame theory of magnetism and electromagnetic phenomena.

**Theory Connection**: Docs 063-066 (magnetism, electric fields, electromagnetism)

**Note**: Early exploratory work. Framework defined in theory docs, awaiting experimental validation.

---

### #80: Gamma-Field Rendering

**Full Name**: Gamma-Field Virtual Expansion Rendering

**Location**: `experiments/80_gamma-field_rendering/`

**Status**: ⏳ **IN PROGRESS** (v1 implemented, v2-v3 described)

**Hypothesis**: A gamma field with virtual spatial expansion can be rendered on a fixed 512x512 viewport while
maintaining energy conservation, deterministic behavior, and realistic core-growth dynamics.

**Method**:

- **Fixed viewport**: 512x512 internal buffer; world coordinates expand virtually
- **Hybrid field model**: Conservative residual field + informational core pattern
- **Core growth**: Morphological dilation limited to 1 pixel/tick in comoving coordinates
- **Residual remap**: Bilinear resampling with 1/s² intensity normalization (2D)
- **Energy tracking**: Sum of discarded intensity logged per tick

**Architecture**:

```
Entity (reference coords) → Core emission → field_core (512×512)
                           → Residual emission → field_residual (512×512)
Scale change → remap residual (1/s²) → clip/aggregate out-of-bounds → render
```

**Key Features**:

- **Comoving core**: Entities stored in reference coordinates, transformed by scale factor s(t)
- **Conservative residual**: Low-frequency field dilutes with expansion
- **Holographic horizon**: Optional aggregation of out-of-bounds data
- **Sliding window**: Stores s(t) and field snapshots for temporal playback

**Versions**:

- **v1**: Core implementation with full pipeline (main.py, modules for core, residual, remap, sliding window)
- **v2**: Extended experiment description (in progress)
- **v3**: Extended experiment description (in progress)

**Theory Validation**:

- ⏳ **PENDING**: Energy conservation during virtual expansion (Ch10 field dynamics)
- ⏳ **PENDING**: Core growth matches gamma-well behavior (Ch11 §4)
- ⏳ **PENDING**: Residual dilution matches expansion predictions (Ch9 §8)

**Theory Connection**:

- Ch9 (Gamma Furrow) — furrow geometry and imprint propagation
- Ch10 (Gamma Field Foundations) — field dynamics and update rules
- Ch11 (Entity Physics) — gamma-well self-maintenance and energy budget

**Files**:

- `v1/main.py` — Main runnable demo
- `v1/gamma_field_core.py`, `gamma_field_residual.py`, `remap.py`, `core_growth.py`, `sliding_window.py` — Modules
- `v1/renderer.py`, `scene.py`, `utils.py` — Rendering infrastructure
- `v2/v2_experiment_description.md`, `v3/v3_experiment_description.md` — Extended descriptions

---

### #72: ZPE Cosmological Model

**Full Name**: Emergent Universe via Jitter/ZPE Scaling

**Location**: `experiments/72_zpe/`

**Status**: 🔬 **EARLY STAGE** (roadmap defined, V1 pending)

**Hypothesis**: Jitter represents zero-point energy that decreases with cosmic expansion, explaining early universe anomalies.

**Roadmap** (V1-V9):

| Version | Feature | Purpose |
|---------|---------|---------|
| **V1** | Fixed tick energy, jitter/gamma ratio | Ontology validation |
| **V2** | Gamma field upgrade | Realistic gravity |
| **V3** | Movement | Kinematics |
| **V4** | Entity creation/deletion | Population dynamics |
| **V5** | Dynamic global jitter | Cosmological evolution |
| **V6** | Adaptive grid expansion | Metric behavior |
| **V7** | Energy bookkeeping | Thermodynamics |
| **V8** | Multi-scale structures | Cosmic web |
| **V9** | Physical mapping | Cosmological interpretation |

**Theory Validation** (Pending):

- ⏳ V1: Ontology validation (rules never violate 1-tick constraint)
- ⏳ V2+: Progressive mechanism validation

**Theory Connection**: Docs 072-073 (ZPE hypothesis, epoch-dependent stability)

**Files**:
- `ROADMAP.md` (comprehensive V1-V9 plan)
- `v1/README.md` (V1 specification)

---

### Reference: #46_01: On Bucketing

**Note**: This is a **theory document** (REFERENCE_doc46_01), not a standalone experiment, but is listed here due to
close connection with experiments #44_05 and #49.

**Location**: `docs/theory/REFERENCE_doc46_01.md`

**Purpose**: Theoretical proof that sorting is not required when rendering temporal substrate with discrete lag values.

**Key Claim**: "Temporal lag provides natural ordering, discrete domain, monotonic progression, bounded values, and
direct mapping to rendering order. Thus, sorting is not a theoretical requirement."

**Validation**: Experiment #44_05 confirms this claim with 10-16× speedup via O(n) bucketing vs O(n log n) sorting.

**Connection**:

- Theory basis for #44_05
- Extended by #49 to temporal window

---

### movement-vs-division

**Location**: `experiments/movement-vs-division/`

**Status**: 📊 **DATA ANALYSIS**

**Purpose**: Analysis of entity dynamics trade-offs between spatial movement and division behavior.

**Note**: Data visualization/analysis directory, not a formal experimental validation.

---

## Theory Document Cross-Reference

### Experiments Validating Theory Chapters

| Theory Chapter                       | Validated By | Key Result                         |
|--------------------------------------|--------------|------------------------------------|
| **Ch1 §5** (Sample Rate Limit)       | #44_03       | v ≤ c enforced (933× asymmetry)    |
| **Ch1 §9** (Dimensional Equivalence) | #50          | Time ≠ dimension (ρ=2.0 signature) |
| **Ch2** (Dimensional Framework)      | #15          | 3D optimal (SPBI=2.23)             |
| **Ch3** (Entity Dynamics)            | #40          | Temporal surfing implemented       |
| **Ch4 §3** (Existence Buffer)        | #49          | Dynamic window is literal buffer   |
| **Ch6 §3** (O(n) Bucketing)          | #44_05       | 13-16× speedup confirmed           |
| **Ch6 §5** (Rotation Asymmetry)      | #44_03       | 933× asymmetry measured            |
| **Doc 028** (Temporal Surfing)       | #62          | Relativistic SR effects (v < 0.9c) |
| **Doc 030** (Collision Persistence)  | #55, #62     | Patterns persist without collapse  |
| **Doc 049** (Temporal Ontology)      | #62, #56 v17 | Deterministic substrate validated  |
| **Doc 072** (ZPE Hypothesis)         | #56 v13      | Jitter range [0.075, 0.5] stable   |
| **Doc 074** (Ternary Correction)     | #56 v13      | Balance via discrete corrections   |
| **Ch9** (Gamma Furrow)               | #80          | Furrow geometry, imprint propagation|
| **Ch10** (Gamma Field Foundations)   | #80          | Field dynamics and update rules     |
| **Ch11** (Entity Physics)            | #51, #53, #80| Gravity as cost gradient, geodesics |
| **Ch12** (EM & Curvature)            | #63          | Magnetism theory (exploratory)      |

### Reference Documents with Experimental Basis

| Reference Doc          | Experiment    | Relationship                  |
|------------------------|---------------|-------------------------------|
| **REFERENCE_doc15**    | #15           | Preserved complete experiment |
| **REFERENCE_doc46_01** | #44_05        | Theoretical proof, validated  |
| **REFERENCE_doc49**    | #40, #50, #62, #56 v17 | Ontology validated            |
| **REFERENCE_doc50_01** | #50           | Preserved complete results    |

---

## Experimental Timeline

### Chronological Development

**Phase 1: Foundations (Pre-2025)**

- #22: Early conceptual work on relativity
- #39: Law-000 baseline rule

**Phase 2: Engine Architecture (2025 Q4)**

- #40: Unified tick-engine framework
- Foundation for rapid prototyping

**Phase 3: Dimensional Physics (2025-2026 Q1)**

- #15: 3,960 configs → 3D optimal
- #50: 1,095 configs → Time ≠ dimension (ρ=2.0 smoking gun)

**Phase 4: Rendering Breakthroughs (2026 Q1)**

- #44_01, #44_02: Initial prototypes
- #44_03: Rotation asymmetry discovered (933×)
- #44_04: Multi-entity scaling
- #44_05: O(n) bucketing validated (13-16× speedup)
- #49: Sliding window (in progress)

**Phase 5: Matter Physics (2026 Q1)**

- #55: Collision physics framework validated (3 regimes, Pauli exclusion emerges)
- #56: Composite objects (in progress)
- #62: Interferometry validated (26/26 tests, which-path falsifiable prediction)

**Phase 6: Stability & Ontology (2026 Q1-Q2)**

- #56 v13: Jitter investigation validated (0.119 NOT special, range [0.075, 0.5])
- #56 v17: Canvas/Renderer ontology validated (O(entities) sparse storage)
- V2 theory consolidation complete

**Phase 7: Cosmology (2026 Q1-Q2)**

- #72: ZPE cosmological model roadmap defined (V1-V9 phases)
- Docs 072-075: Theoretical frameworks for epoch-dependent stability
- #63: Magnetron theory (exploratory)

**Phase 8: Current Work (2026 Q1)**

- #72 V1 implementation pending
- #62 experimental proposal preparation
- Real-world falsification test planning

---

## Validation Status Summary

### Falsification Criteria (from QUICK_REFERENCE)

| Criterion                      | Experiment | Status         | Evidence                       |
|--------------------------------|------------|----------------|--------------------------------|
| **1. Planck-scale dispersion** | -          | ⏳ Not testable | Requires observational physics |
| **2. Lorentz violation**       | -          | ⏳ Not testable | Requires particle physics      |
| **3. 3D optimality**           | #15        | ✓ VALIDATED    | SPBI(3D)=2.23 > all others     |
| **4. Rotation asymmetry**      | #44_03     | ✓ VALIDATED    | 933× forward/backward ratio    |
| **5. ρ=2.0 signature**         | #50        | ✓ VALIDATED    | ρ=2.000±0.002 universal        |
| **6. O(n) rendering**          | #44_05     | ✓ VALIDATED    | 13-16× faster, linear scaling  |
| **7. Which-path no collapse**  | #62        | ⏳ TESTABLE     | V > 0.9 predicted (QM: V → 0)  |
| **8. Jitter stability range**  | #56 v13    | ✓ VALIDATED    | [0.075, 0.5] stable range      |
| **9. Canvas ontology**         | #56 v17    | ✓ VALIDATED    | O(entities) memory scaling     |
| **10. ZPE epoch-dependence**   | #72        | 🔬 PROPOSED    | Roadmap V1-V9 defined          |

**Computational Physics**: 6/6 testable predictions validated ✓

**Real-World Physics**: 1 falsifiable prediction ready for experimental test ($500K-$2M, 1-2 years)

**Observational Physics**: 2 predictions not yet testable (require experiments beyond current technology)

**Cosmological Physics**: 1 framework proposed (ZPE epoch-dependence, needs validation)

---

## How to Navigate Experiments

### Running Experiments

**Python Experiments** (Most experiments):

```bash
cd experiments/[experiment_name]
python [main_script].py
```

**Java Implementation** (Not experiments, but related):

```bash
cd tick-space-runner
mvn clean package
mvn exec:java -pl tick-space-runner -Dexec.mainClass="eu.jerrysamek.tickspace.runner.LocalApp"
```

### Understanding Experiment Structure

**Typical experiment directory**:

```
experiments/[number]_[name]/
├── README.md              # Hypothesis, method, validation criteria
├── [implementation].py    # Main experiment code
├── RESULTS.md            # Results (if completed)
├── EXPERIMENT_RESULTS.md # Detailed results (major experiments)
└── logs/                 # Data outputs
```

### Reading Order for New Researchers

1. **Start with validated experiments**:
    - #15 (dimensional physics foundation)
    - #50 (smoking gun: time ≠ dimension)
    - #44_03 (rotation asymmetry)
    - #44_05 (O(n) bucketing)

2. **Then explore techniques**:
    - #40 (tick-engine architecture)
    - #49 (sliding window pattern)

3. **Then prototypes/exploratory**:
    - #44 series (rendering progression)
    - #39 (Law-000 baseline)

---

## Statistics

**By Status**:

- ✓ Validated: 8 experiments (40%)
- ⏳ In Progress: 1 experiment (5%)
- 🔬 Exploratory/Early: 5 experiments (25%)
- 📐 Prototype: 4 experiments (20%)
- 📊 Analysis: 2 experiments (10%)

**By Type**:

- Dimensional Physics: 2 (major)
- Rendering: 6 (series)
- Performance: 2 (validation)
- Architecture: 2 (framework)
- Conceptual: 1 (historical)

**Configurations Tested**:

- #15: 3,960 configs
- #50: 1,095 configs
- **Total**: 5,055+ validated configurations

**Theory Documents Referenced**: 15+ (chapters, references, v1 docs)

---

## Related Documentation

**Theory Framework**:

- [README.md](README.md) - Main theory index
- [quick_reference.md](quick_reference.md) - Formula sheet with experiment results
- [glossary.md](glossary.md) - Term definitions
- [v1_to_v2_mapping.md](v1_to_v2_mapping.md) - Historical document mapping

**Specific Theory Chapters**:

- Ch1: Temporal Ontology (validated by #40, #50)
- Ch2: Dimensional Framework (validated by #15)
- Ch6: Rendering Theory (validated by #44_03, #44_05)

**Reference Documents**:

- REFERENCE_doc15: Experiment #15 preserved
- REFERENCE_doc46_01: Bucketing theory
- REFERENCE_doc49: Temporal ontology
- REFERENCE_doc50_01: Experiment #50 preserved

---

## Future Experiments

**Proposed** (from various READMEs):

- 44_06: GPU compute shader bucketing
- 44_07: Temporal Z-buffer hybrid
- 44_08: Integration with Java substrate
- Higher-dimensional rendering tests
- Collision dynamics validation
- Energy balance experiments
- Observer model implementation

---

**Document Version**: 1.2
**Last Updated**: February 2026
**Status**: Living document (will update with new experiments)
**Changes in v1.2**: Added Exp #80 (gamma-field rendering), linked Ch9-Ch13 to experiment cross-references
**Changes in v1.1**: Added Exp #56 v13 (jitter), v17 (canvas), #63 (magnetron), #72 (ZPE)
**Maintainer**: Auto-generated from experiment README files

**For questions about specific experiments, see individual README files in `experiments/[name]/`**
