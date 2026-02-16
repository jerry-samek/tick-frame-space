# Tick-Frame Physics Theory (Version 2)

**Consolidated theoretical framework** - January 2026

This directory contains the v2 consolidated theory of tick-frame physics, synthesizing 76 raw documents (archived in
`raw/`) into a coherent framework with experimental validation.

---

## Quick Start

**New readers**: Start with **Ch1 (Temporal Ontology)** → **Ch2 (Dimensional Framework)** → **experiment_index.md** (see Exp 51, 55 breakthroughs!) → **Ch8 (Integration)**.

**Implementers**: Read **REFERENCE_doc15** (Java basis) → **Ch3 (Entity Dynamics)** → **Ch6 (Rendering)** → **experiments/55_collision_physics/** (reference implementation).

**Researchers**: Read **Ch7 (Formalization)** → **Ch8 (Falsification)** → **honest_status.md** (updated Jan 2026) → experimental docs in `../../experiments/`.

**Skeptics**: Read **REFERENCE_doc50_01** (smoking gun evidence) → **experiments/51_emergent_time_dilation/v10/RESULTS.md** (geodesics emerged!) → **experiments/55_collision_physics/** (Pauli exclusion emerged!) → **honest_status.md** (reality check).

---

## Framework Overview

### Core Thesis

**Time is discrete at the Planck scale and serves as the primary substrate from which space and entities emerge.**

**Key principles**:

1. **Temporal Primacy**: Entities are temporal processes, not objects in time (Ch1)
2. **3D Optimality**: Three spatial dimensions are optimal, not exclusive (Ch2)
3. **Sample Rate Limit**: Maximum speed v = c = 1 spatial quantum / tick (Ch1, Ch6, Ch7)
4. **Discrete Time Advantage**: O(n) rendering vs O(n log n) sorting (Ch6)
5. **Time ≠ Dimension**: Temporal systems show rho=2.0 vs spatial rho≈1.5 (Ch1)

### Validation Status (January 2026 Update)

✅ **MAJOR BREAKTHROUGH**: Core physics mechanisms validated computationally!

**Foundational Properties (Tier 0)**:
- Experiment #15: 3D optimal in certain field dynamics (3,960 simulations)
- Experiment #44: Kinematic constraint v ≤ c enforceable (rotation asymmetry)
- Experiment #50: ρ=2.0 signature (time ≠ dimension, 1,095 configs)
- Experiment #46_01: O(n) bucketing works (2.78× speedup @ 100k entities)

**Physics Mechanisms (Tier 1)** - January-February 2026:
- ✅ **Experiment #51 (v1-v9)**: Emergent time dilation VALIDATED (r ≈ 0.999 correlation with GR+SR)
- ✅ **Experiment #53 (v10)**: Geodesic motion VALIDATED (100% orbital success, NO FORCE LAWS programmed!)
- ✅ **Experiment #55**: Three-regime collision physics VALIDATED (6/6 test cases, exact energy conservation)
- ✅ **Experiment #55 DISCOVERY**: Pauli exclusion emerged naturally (NOT predicted - genuinely surprising!)
- ✅ **Experiment #64_109 (v8-v9)**: Graph-lattice gravity VALIDATED (self-subtracting tagged quanta, three-body dynamics, exact integer conservation) — **Second independent gravity implementation!**
- ⚠️ **Experiment #52 (v11)**: Black hole c-ring discovered (awaiting collision validation v12)
- 🔄 **Experiment #56**: Composite objects (atoms/molecules) implemented, binding validation pending

**Current Status**: 10/11 validations successful (6/8 Tier 1 complete). Two independent gravity implementations (continuous fields + integer quanta on graph) converge on the same physics.

**Confidence Level**: MODERATE-HIGH for emergent gravity/relativity mechanisms. Two independent implementations converging is strong evidence against simulation artifacts.

⚠ **Implementation partial**: Java tick-space-runner realizes core patterns but has gaps (see Ch8 §4).

☐ **Real physics connection**: Still zero observational tests. But computational evidence now strong enough to warrant proposing real-world experiments.

---

## Document Structure

### Reference Documents (Required Reading)

Critical docs preserved at top level for permanent access:

- **[REFERENCE_doc015_minimal_model.md](REFERENCE_doc015_minimal_model.md)**: Java implementation basis (Chapter 15 model)
- **[REFERENCE_doc049_temporal_ontology.md](REFERENCE_doc049_temporal_ontology.md)**: Theoretical constitution (12 ontological principles)
- **[REFERENCE_doc050_01_dimensional_equivalence_rejection.md](REFERENCE_doc050_01_dimensional_equivalence_rejection.md)**: Smoking gun evidence (rho=2.0 signature)
- **[REFERENCE_doc046_01_bucketing_validation.md](REFERENCE_doc046_01_bucketing_validation.md)**: O(n) rendering validation (2.78× speedup)

**Why preserved?**:

- **Doc 15**: Current Java implementation uses this model
- **Doc 49**: Theoretical apex (supersedes Doc 15 ontologically)
- **Doc 50_01**: Decisive experimental evidence (0% dimensional equivalence)
- **Doc 46_01**: Computational feasibility proof (game-scale rendering)

### Supplementary Documents (Quick Access)

Essential reference materials for navigation and lookup:

- **[glossary.md](glossary.md)**: Comprehensive glossary of terms, symbols, and acronyms (85+ terms, 20+ symbols)
- **[quick_reference.md](quick_reference.md)**: One-page formula sheet with core principles, experimental results, and
  falsification criteria
- **[raw_to_current_mapping.md](raw_to_current_mapping.md)**: Complete traceability table mapping 76 raw documents to
  current chapters
- **[experiment_index.md](experiment_index.md)**: Comprehensive cross-reference of all computational experiments with
  results and theory connections
- **[open_questions.md](open_questions.md)**: Consolidated list of unresolved questions, research priorities, and future
  directions (35+ active questions)
- **[proposed_experiments_gravity_relativity.md](proposed_experiments_gravity_relativity.md)**: Detailed experimental
  proposals to test emergent gravity and relativity mechanisms from v1 documents (HIGH PRIORITY)
- **[honest_status.md](honest_status.md)**: Brutally honest assessment of what's validated vs speculation - READ THIS
  for reality check

**Use these for**:

- Looking up unfamiliar terms (Glossary)
- Quick formula/principle lookup (Quick Reference)
- Tracing concept origins from v1 to v2 (Mapping)
- Finding experimental validations (Experiment Index)
- Understanding research frontiers (Open Questions)

### V2 Chapters (Consolidated Framework)

#### **[Chapter 1: Temporal Ontology](ch001_temporal_ontology.md)** (~20 pages)

**Status**: Experimentally validated

**Core content**:

- Time as primary substrate (tick-stream is fundamental)
- Entities as temporal processes (not objects in time)
- Causal structure and ratchet effect (ρ=2.0 signature)
- Emergent space from temporal gradients
- Sample rate limit (v <= 1 tick/tick)

**Key evidence**:

- Experiment #50: rho=2.0 in ALL (n+t) systems (smoking gun)
- Experiment #44: Rotation asymmetry 933× (kinematic validation)

**Read this if**: You want the ontological foundation.

---

#### **[Chapter 2: Dimensional Framework](ch002_dimensional_framework.md)** (~25 pages)

**Status**: Experimentally validated

**Core content**:

- 3D Goldilocks zone (SPBI=2.23, optimal balance)
- Dimensional scaling laws (rho ≈ 1.5 in spatial dimensions)
- Phase transition at d=3 (rho becomes universal)
- Configuration independence (H2 falsified)
- 4D-5D stability (more stable, less optimal)

**Key evidence**:

- Experiment #15: 3,960 simulations (180 configs × 5 dimensions)
- Statistical validation: CV(d) ≈ 80%×exp(-0.82×d)

**Read this if**: You want to understand why 3D space is optimal.

---

#### **[Chapter 3: Entity Dynamics](ch003_entity_dynamics.md)** (~28 pages)

**Status**: Partially validated (over-coherence challenge)

**Core content**:

- Temporal Surfing Principle (renewal per tick)
- Collision Persistence Principle (collisions as entity types)
- Imbalance Theory (asymmetry from expansion)
- Energy mechanics (E = t - t_birth, linear growth)
- Java implementation patterns (TickTimeConsumer, value classes)

**Key evidence**:

- Java tick-space-runner (functional implementation)
- Naive vs full collision models (tuning in progress)

**Read this if**: You're implementing tick-frame physics or want to understand entity behavior.

---

#### **[Chapter 4: Observer & Consciousness](ch004_observer_consciousness.md)** (~26 pages)

**Status**: Speculative framework (no experimental validation)

**Core content**:

- Identity as continuity (observer = function tick n → tick n+1)
- Memory as addressing (brain indexes historical ticks, doesn't store)
- Consciousness as presence (current tick defines "now")
- Sleep as computational necessity (buffer clearing prevents collapse)
- Psychological phenomena (trauma, déjà vu, dreams as tick patterns)

**Key evidence**:

- None (theoretical framework only)
- Integration with Ch1 (temporal ontology) and Ch3 (entity dynamics)

**Read this if**: You're interested in consciousness, observer models, or perception in tick-frame physics.

---

#### **[Chapter 5: Free Will & Ternary Logic](ch005_free_will_ternary_logic.md)** (~25 pages)

**Status**: Philosophical framework (highly speculative)

**Core content**:

- Substrate determinism (tick-stream fully causal)
- Frame-level uncertainty (observers perceive probabilities)
- Auditable agency (free will = bounded choice within determinism)
- Ternary logic {-1, 0, +1} (symmetry and rich dynamics)
- Choice as tick allocation (how observer spends budget)

**Key evidence**:

- None (philosophical framework only)
- Compatibilist approach to free will problem

**Read this if**: You're interested in free will, agency, or want to complete the philosophical framework.

---

#### **[Chapter 6: Rendering Theory](ch006_rendering_theory.md)** (~25 pages)

**Status**: Experimentally validated

**Core content**:

- O(n) temporal bucketing (vs O(n log n) sorting)
- Lag-as-depth rendering (2D space + time → 3D visualization)
- Rotation asymmetry (933× forward/backward difference)
- Temporal velocity constraint (v <= 1 tick/tick validation)
- 297k entities @ 60 FPS achievable

**Key evidence**:

- Experiment #46_01: 2.78× speedup @ 100k entities
- Experiment #44: 0% forward pitch success (impossible to "speed up")

**Read this if**: You're building visualizations or want computational performance insights.

---

#### **[Chapter 7: Physical Formalization](ch007_physical_formalization.md)** (~20 pages)

**Status**: Analytical framework (derivations partial)

**Core content**:

- Planck-scale discretization (tick = t_planck = 5.39×10^-44 s)
- Energy-time relation (E = hbar/t_planck × n)
- Discrete wave mechanics (finite-difference equations)
- Dimensional scaling derivation (rho ≈ 1.5 from surface-area law)
- Relativity compatibility (speculative)

**Key results**:

- Speed of light: c = l_planck / t_planck (structural constant)
- Maximum frequency: f_max ≈ 9.3×10^42 Hz (Nyquist limit)
- Wave dispersion: High-frequency waves travel slower than c

**Read this if**: You want mathematical rigor or connection to established physics.

---

#### **[Chapter 8: Integration & Falsification](ch008_integration_falsification.md)** (~22 pages)

**Status**: Framework synthesis

**Core content**:

- Cross-chapter integration and dependencies
- Validated vs speculative components
- Implementation gaps (Doc 15 vs Doc 49, expansion coupling, collision tuning)
- Falsification criteria (6 testable predictions)
- Roadmap (6-phase plan to close gaps)

**Key insights**:

- 4 major predictions validated computationally
- 3 implementation gaps identified
- Clear falsification criteria established
- Comparison to alternative frameworks (Minkowski, LQG, Causal Sets)

**Read this if**: You want the big picture, validation status, or research roadmap.

---

#### **[Chapter 9: The Gamma Furrow and the Origin of Dark Matter](ch009_the_gamma_furrow_and_the_origin_of_dark_matter.md)** (~15 pages)

**Status**: Speculative (no experimental validation)

**Core content**:

- Gamma furrow (observer's causal boundary in the gamma field)
- Dark matter as imprints that missed us (no exotic particles needed)
- Dark energy as geometric dilution of the gamma field
- Gamma Imprint Principle (all observation is retrospective)
- Dimensional diffusion (geometry alone produces inverse-square laws)
- Philosophical interlude: technology as furrow-bridging

**Key principles**: Gamma Furrow Principle, Dark Matter Principle, Gamma Imprint Principle, Gamma Spectrum Hypothesis

**Read this if**: You want the cosmological foundations of the gamma-field ontology.

---

#### **[Chapter 10: Gamma Field Foundations](ch010_gamma_field_foundations.md)** (~20 pages)

**Status**: Speculative (theoretical framework)

**Core content**:

- Seven foundational principles (temporal surfing, gamma attraction, existential drag, rotational persistence, gamma slingshot, existential boundary, compatibility maximization)
- Attractor and wave dynamics (expansion-driven propagation)
- Well dynamics and propagation (gradient basins, stability conditions)
- Dissolution regime (five stages of entity death)
- Semantic reconstruction and retrodictive coherence
- Master diagram: unified geometry of all gamma-field phenomena

**Key evidence**: Partial — Exp #51 (time dilation), Exp #53 (geodesic motion)

**Read this if**: You want to understand what the gamma field IS — its principles, dynamics, and geometry.

---

#### **[Chapter 11: Gamma Field Entity Physics](ch011_gamma_field_entity_physics.md)** (~18 pages)

**Status**: Speculative (conceptual framework)

**Core content**:

- Photon as degenerate process (stationary imprint, field propagates at c)
- Gravity as energetic optimization (cost-gradient, not force)
- Entity as self-maintained gamma well (energy budget, lag as energy source)
- Fragments: subcritical wells, emission modes, absorption
- Dissolution: energy starvation survival sequence
- Eight predictive phenomena with real-world analogues

**Key evidence**: Partial — Exp #51 (cost-gradient gravity), Exp #53 (geodesics), Exp #55 (collision physics)

**Read this if**: You want to understand how entities BEHAVE in the gamma field.

---

#### **[Chapter 12: Electromagnetism and Curvature Geometry](ch012_electromagnetism_curvature_geometry.md)** (~20 pages)

**Status**: Speculative (theoretical framework)

**Core content**:

- Magnetism as tangential curvature of the gamma well
- EM unification: W = W_radial + W_tangential
- Charge as lag-flow asymmetry (geometric, not intrinsic)
- Lorentz-like effects, induction, EM waves from curvature
- The well-vs-hill debate: curvature duality
- Hill interpretation: surplus energy → complexity → life
- Directional framework: physical vs gamma-gradient axes
- Formal hill model (normalized curvature, overdamped dynamics)

**Key insight**: Same curvature, opposite universes — only the hill interpretation supports life.

**Read this if**: You want the EM theory and the resolution of the well-vs-hill debate.

---

#### **[Chapter 13: Hill Ontology — From Existence to Life](ch013_hill_ontology.md)** (~20 pages)

**Status**: HIGHLY SPECULATIVE (philosophical capstone)

**Core content**:

- Existence vs antiexistence (geometric distinction, curvature-based)
- Black holes as terminal hill states (maximal curvature, perfect coherence)
- Horizon geometry and the illusion of frozen time
- Stellar collapse and explosive reconfiguration (supernovae seed new existence)
- Cooperative curvature principle (cooperation as geometric necessity)
- Ten axioms of hill ontology (life, sentience, value, reproduction)
- Reproduction as window reset and hill consolidation

**Key insight**: Life is the inevitable fixed point of recursive physics.

**Read this if**: You want the philosophical capstone — from geometry through astrophysics to biology.

---

## Reading Paths

### Path 1: For New Readers (Conceptual Understanding)

1. **Ch1 (Temporal Ontology)** - Foundation
2. **Ch2 (Dimensional Framework)** - Structure
3. **REFERENCE_doc050_01** - Evidence (smoking gun)
4. **Ch8 §2-3** - What's validated vs speculative
5. **raw/README.md** - Historical context (if curious)

**Time**: 2-3 hours
**Outcome**: Understand core framework and evidence.

### Path 2: For Implementers (Code Focus)

1. **REFERENCE_doc015** - Current Java model
2. **Ch3 (Entity Dynamics)** - Implementation patterns
3. **Ch6 (Rendering Theory)** - Visualization & performance
4. **Ch8 §4** - Implementation gaps
5. **CLAUDE.md** (root) - Development commands, architecture

**Time**: 3-4 hours
**Outcome**: Ready to contribute to tick-space-runner.

### Path 3: For Researchers (Full Framework)

1. **All chapters in order** (Ch1 → Ch2 → Ch3 → Ch4 → Ch5 → Ch6 → Ch7 → Ch8)
2. **All 4 reference docs**
3. **Experimental reports** (`../../experiments/*/EXPERIMENT_RESULTS.md`)
4. **raw archive** (selected docs for deep dives)

**Time**: 10-15 hours
**Outcome**: Complete understanding of framework, experiments, gaps, and philosophical implications.

### Path 4: For Skeptics (Evidence First)

1. **REFERENCE_doc050_01** - rho=2.0 signature (smoking gun)
2. **Ch6 §5** - Rotation asymmetry (v <= c validation)
3. **Ch8 §5** - Falsification criteria
4. **Ch8 §11** - Framework assessment (strengths & weaknesses)
5. **Experiments #15, #44, #50, #46_01** - Raw data

**Time**: 2 hours
**Outcome**: Judge for yourself based on evidence.

---

## Key Questions Answered

### Q1: Is this a replacement for relativity/quantum mechanics?

**A**: No. Tick-frame explores discrete time at Planck scale as fundamental axiom. It's compatible with QM/relativity in
appropriate limits (see Ch7 §9), but formalization is incomplete. Think of it as **exploratory research**, not a rival
theory.

### Q2: What's the strongest evidence?

**A**: **Experiment 50** (rho=2.0 signature) - 1,095 configurations tested, 0% pass rate for dimensional equivalence,
universal quadratic scaling when time is treated as dimension. This is the **smoking gun** that time ≠ spatial
dimension.

### Q3: What's the weakest part?

**A**: **Relativity compatibility** (Ch7 §9) - Lorentz transforms not yet derived from discrete symmetries. Time
dilation mechanism is speculative. No observational tests yet.

### Q4: Can I test this experimentally?

**A**: **Computational**: Yes! Run experiments 15, 44, 50, 46_01 yourself (Python code in `../../experiments/`).

**Observational physics**: Not yet. Planck-scale effects (Ch7 §10) require ultra-high-energy cosmic rays or
gravitational wave dispersion measurements beyond current sensitivity.

### Q5: How does this relate to the Java code?

**A**: Java implements the **Doc 15 model** (see REFERENCE_doc015). Theory has evolved to **Doc 49** (see
REFERENCE_doc049). There's a gap (ontological refinement), but code is functionally correct. See Ch8 §4 for details.

### Q6: Is time travel possible in this framework?

**A**: **No**. Tick-stream is strictly ordered (Ch1 §2). You cannot move backward in tick sequence (v <= 1 tick/tick
limit). Rotation asymmetry (Ch6 §5) experimentally confirms this: 0% success for "forward pitch" (moving toward
present).

### Q7: What about free will and consciousness?

**A**: **Ch4 (Observer & Consciousness)** establishes observer as temporal trajectory with memory-as-indexing model. *
*Ch5 (Free Will & Ternary Logic)** presents compatibilist framework (free will = auditable agency within determinism).
Both are **highly speculative** with no experimental validation. Treat as philosophical exploration, not validated
science.

---

## Experimental Validation Summary

### Tier 0: Foundational Properties

| Experiment | Prediction                           | Result                          | Status      | Chapter |
|------------|--------------------------------------|---------------------------------|-------------|---------|
| **#15**    | 3D optimal (SPBI max)                | 3D: 2.23, 4D: 2.20, 5D: 2.11    | ✓ Validated | Ch2     |
| **#44**    | v <= c enforced (rotation asymmetry) | 933× (forward 0%, backward 93%) | ✓ Validated | Ch6     |
| **#50**    | rho=2.0 in (n+t) systems             | 2.0 ± 0.002 (all configs)       | ✓ Validated | Ch1     |
| **#46_01** | O(n) bucketing faster                | 2.78× @ 100k entities           | ✓ Validated | Ch6     |

### Tier 1: Physics Mechanisms (January-February 2026)

| Experiment  | Prediction                          | Result                                  | Status          | Chapter |
|-------------|-------------------------------------|-----------------------------------------|-----------------|---------|
| **#51 v9**  | Emergent GR+SR time dilation        | r ≈ 0.999 correlation, multiplicative!  | ✅ VALIDATED    | Ch7     |
| **#53 v10** | Geodesic motion (no force laws)     | 100% orbital success (18/18 entities)   | ✅ VALIDATED    | Ch7     |
| **#52 v11** | Black hole event horizons           | Stable c-ring @ r≈10.1 (not r_s)        | ⚠️ Preliminary  | Ch7     |
| **#55**     | Three-regime collision physics      | 6/6 test cases, E_ratio = 1.000         | ✅ VALIDATED    | Ch3     |
| **#55**     | *(Emergent Pauli exclusion)*        | Emerged from cell capacity (surprise!)  | ✅ **DISCOVERY** | Ch3    |
| **#64_109** | Graph-lattice gravity               | Three-body dynamics, exact int conservation | ✅ VALIDATED | Ch10, Ch11 |
| **#56**     | Composite atoms/molecules           | H, He, H₂ structures implemented        | 🔄 In Progress  | Ch3     |
| **#56 v13** | Jitter stability range              | [0.075, 0.5] stable, 0.119 NOT special  | ✅ VALIDATED    | Ch7     |
| **#56 v17** | Canvas/Renderer ontology            | O(entities) sparse storage works        | ✅ VALIDATED    | Ch1     |
| **#62**     | Interferometry (which-path)         | 26/26 tests, V=1.0 after path readout   | ✅ VALIDATED    | Ch7     |
| **#72**     | ZPE cosmological model              | Roadmap V1-V9 defined                   | 🔬 Early Stage  | Ch7     |

**Overall**: **11/13 validations successful** (4 Tier 0 + 7 Tier 1). 1 preliminary (ghost particle limitation), 1 in progress.

**Major Achievements**:
- Geodesics emerged WITHOUT programming force laws - strongest evidence this is real physics!
- **Two independent gravity implementations converge**: Exp #51 (continuous fields) + Exp #64_109 (integer quanta on graph) both produce gravity
- Graph-lattice gravity: self-subtracting tagged quanta produce three-body dynamics with exact integer conservation (Exp #64_109)
- Key insight: continuous internal direction on discrete lattice — small gradient nudges accumulate, enabling smooth turning
- Interferometry validated: which-path detection WITHOUT wavefunction collapse (Exp #62)
- Jitter stability validated: 0.119 is within stable range [0.075, 0.5], NOT a fundamental constant (Exp #56 v13)
- Canvas/Renderer ontology: sparse O(entities) memory instead of O(grid³) (Exp #56 v17)

**New Theoretical Developments (Feb 2026)**:
- **ZPE Hypothesis** (docs 072-073): Jitter decreases with cosmic expansion, explains early universe anomalies
- **Ternary Substrate Correction** (doc 074): Stability via discrete integer corrections {-1, 0, +1}
- **Metabolic Time Dilation** (doc 075): Entities "skip" rendering to conserve energy, not temporal slowdown
- **Electromagnetism Framework** (docs 063-066): Theoretical foundation for EM in tick-frame substrate
- **Gamma Field Theory** (docs 076-101, consolidated into Ch9-Ch13): Complete gamma-field ontology from foundations through entity physics, electromagnetism, curvature duality, to hill ontology of life

**Next**: Complete ZPE cosmological model (Exp #72), validate epoch-dependent stability predictions, explore graph-lattice gravity extensions (stable orbits, finer lattices)

---

## Version History

### V2 (January 2026) - This Version

**Changes from V1**:

- Consolidated 76 chronological docs → 5 chapters + 4 references
- Removed contradictions (early vs late docs)
- Added experimental validation status to each chapter
- Created coherent narrative for new readers
- Separated validated (Ch1, 2, 6) from speculative (Ch7 relativity, Ch3 imbalance)

**Why consolidation?**:

- V1 grew organically over time (contradictions emerged)
- New readers faced 76-document overwhelm
- Experimental validation required clear framework
- Implementation needed theoretical guidance

**Raw status**: Fully archived in `raw/` subdirectory with complete README. Nothing deleted.

### Raw (2024-2026) - Archived + New (2026)

**Location**: `raw/` subdirectory

**Contents**: 102+ theory documents (76 original + 26 new in 076-101 range, plus earlier 055-075)

**Key docs** (preserved as references):

- raw/015: Minimal Model Recommendation
- raw/046: Why Sorting Is Not Required
- raw/049: Temporal Ontology
- raw/050: Dimensional Equivalence Test Specification

**New raw documents (055-075)** - February 2026:

| Range | Topic | Key Findings |
|-------|-------|--------------|
| **055-058** | Speed of light, propulsion | Substrate vs pattern speed distinction, active propulsion limits |
| **059-060** | Causal cell scale, overlap | Effective causal cell experiments, brute-force vs engineered patterns |
| **061** | Matter-antimatter | Asymmetry emergence from collision dynamics |
| **062** | Interferometry | Which-path detection WITHOUT wavefunction collapse (FALSIFIABLE!) |
| **063-066** | Electromagnetism | Magnetron theory, electric fields, EM framework |
| **067-069** | Advanced topics | Anti-gravity, time crystals, computational bootstrapping |
| **070 series** | Emergent atoms | Fragmented electron cloud, collision-driven stabilization, field rotation |
| **071** | Double-slit | Tick-frame interpretation of interference |
| **072-073** | ZPE hypothesis | Jitter scaling with expansion, epoch-dependent stability |
| **074** | Ternary correction | Axiom of ternary substrate correction {-1, 0, +1} |
| **075** | Metabolic dilation | Time dilation as energy-saving skip, not temporal slowdown |

**New raw documents (076-101)** - February 2026 (consolidated into Ch9-Ch13):

| Range | Topic | Consolidated Into |
|-------|-------|-------------------|
| **076-077, 089** | Gamma field principles, dynamics, master diagram | Ch10 (Gamma Field Foundations) |
| **078-080** | Imprint principle, dimensional diffusion, philosophical interlude | Ch9 (expanded) |
| **081-085, 090** | Photon, gravity, entity wells, fragments, dissolution, predictions | Ch11 (Entity Physics) |
| **086-088, 091_00-01, 092-094** | Magnetism, EM unification, charge, well-vs-hill, curvature duality | Ch12 (EM and Curvature) |
| **091_02-05, 095-101** | Existence/antiexistence, black holes, cooperation, life, reproduction | Ch13 (Hill Ontology) |

**See**: `raw/README.md` for complete archive guide.

---

## Implementation Status

### Java Tick-Space-Runner

**Location**: `../../tick-space-runner/` (Maven project, Java 25)

**Implements**:

- ✓ TickTimeConsumer<E> pattern (temporal processes)
- ✓ SingleEntityModel, CollidingEntityModel (entity dynamics)
- ✓ Discrete tick evolution (BigInteger tickCount)
- ✓ Spatial hash map (O(1) collision detection)
- ⚠ Doc 15 model (not Doc 49 ontology yet)

**Gaps** (see Ch8 §4):

- Expansion coupling insufficient (lambda ≈ 0)
- Collision dynamics using naive model (full model exists but not active)
- Energy balance tracking incomplete (feature/#3 branch)

**See**: `../../CLAUDE.md` for development commands and architecture.

---

## Future Work (6-Phase Roadmap)

**From Ch8 §6** (Updated January 2026):

1. **Phase 1: Documentation** (✅ **COMPLETE** - January 2026 consolidation)
2. **Phase 2: Collision Physics** (✅ **COMPLETE** - Exp #55 validated three regimes + emergent Pauli exclusion!)
3. **Phase 3: Composite Objects** (🔄 **IN PROGRESS** - Exp #56, structures implemented, binding validation pending)
4. **Phase 4: Black Hole Validation** (⏳ NEXT - v12 collision physics for c-ring test)
5. **Phase 5: Energy Balance & Expansion Coupling** (⏳ Planned - feature/#3 branch + Imbalance Theory validation)
6. **Phase 6: Observational Predictions** (⏳ Research - propose real-world experiments based on validated mechanisms)

**Major Milestone Achieved**: Phases 1-2 complete! Collision physics framework fully validated with **emergent Pauli exclusion discovery**.

**Current priority**: Complete Exp #56 (composite object validation via γ-well binding), then validate black hole c-ring with collision physics (v12).

---

## Citation

If referencing this work:

**Framework**:
> Tick-Frame Physics Theory (Version 2), January 2026.
> https://github.com/jerrysamek/tick-frame-space
> docs/theory/README.md

**Specific chapters**:
> [Chapter Title], Tick-Frame Physics Theory v2, January 2026.
> docs/theory/ch[N]_[name].md

**Experiments**:
> Experiment #[N]: [Title], Tick-Frame Space Project, [Date].
> experiments/[N]_[name]/EXPERIMENT_RESULTS.md

**Original raw docs**:
> Theory Document [N]: [Title], Tick-Frame Physics (raw), [Date].
> docs/theory/raw/[N]_[Title].md

---

## Contributing

**Theoretical work**:

- Propose refinements via issues
- Identify contradictions or gaps
- Suggest experimental tests

**Implementation**:

- Follow CLAUDE.md development guide
- Focus on closing gaps (Ch8 §4)
- Test against falsification criteria (Ch8 §5)

**Experiments**:

- Replicate existing experiments (verify results)
- Propose new tests (see Ch8 §10 for ideas)
- Share results (even null results are valuable)

---

## License

This is a research project on "garden leave" (exploratory, speculative). Feel free to:

- Read and critique
- Replicate experiments
- Build on ideas
- Correct assumptions

Not a claim to replace established physics - an exploration of what emerges from discrete time.

---

## Contact

**Repository**: https://github.com/jerrysamek/tick-frame-space
**Issues**: Submit via GitHub issues
**Discussions**: Use GitHub discussions for questions

---

**Last updated**: February 2026 (v2.2 update: consolidated docs 076-101 into Ch9 expansion + Ch10-Ch13 new)
**Document count**: 14 chapters + 4 references + 7 supplements + v1 archive (120+ docs, including 076-101 gamma field theory, 104-110, 120-200)
**Computational validation**: 11/13 successful (4 Tier 0 foundational + 7 Tier 1 physics mechanisms)
**Physics claims**: **PARTIALLY VALIDATED** - Time dilation (✅), geodesics (✅), graph-lattice gravity (✅ NEW), collision physics (✅), Pauli exclusion (✅ emergent!), interferometry (✅), jitter stability (✅), black holes (⚠️ preliminary), composites (🔄 in progress)
**Confidence level**: MODERATE-HIGH for emergent gravity/relativity mechanisms. Two independent gravity implementations converge — strong evidence against artifacts.
**Implementation status**: Partial (tier 2/5 complete, Ch4-5 not implemented)
**New theoretical developments**: ZPE/jitter scaling hypothesis (docs 072-073), ternary substrate correction (doc 074), metabolic time dilation (doc 075), canvas ontology (exp 56 v17), graph-lattice gravity (exp 64_109), foundational axiom hierarchy (RAW 200)
**Next milestone**: Complete ZPE cosmological model (Exp #72), explore stable orbits on graph lattice
