# Tick-Frame Physics: Open Questions and Research Frontier

**Consolidated list of unresolved questions, research priorities, and future experimental directions**

---

## Overview

This document consolidates open questions from across the tick-frame physics framework, organized by:

- **Priority** (Critical / High / Medium / Low)
- **Type** (Theoretical / Experimental / Implementation)
- **Status** (Active / Speculative / Deferred)

**Total Open Questions**: 39+ (32 original + 7 new gamma-field questions from Ch9-Ch13)

**Research Areas**: 10 major domains

---

## TLDR: Top Questions at a Glance

### 🔥 Currently Active (Being Worked On)

- **Q7.1**: Why is the simulation "over-coherent"? (structures too uniform)
    - *Issue*: Need chaotic emergence, but getting stable patterns
    - *Fix*: Tune expansion coupling λ, improve collision model
    - *Status*: Mentioned in CLAUDE.md as current priority

### ⚡ Ready to Execute (Can Do Now)

- **Q9.1**: Does sliding window implement existence buffer correctly?
    - *Test*: Run Experiment #49 (already designed, awaiting execution)
    - *Validates*: Ch4 §3 observer memory model

- **🚀 NEW: Gravity/Relativity Experiments** (Experiments #51-55)
    - *Test*: Emergent time dilation, black holes, geodesics from computational load
    - *Based on*: Bold claims in archived v1 Docs 21, 25, 17_02
    - *See*: [proposed_experiments_gravity_relativity.md](proposed_experiments_gravity_relativity.md)
    - *Priority*: **HIGH** - Tests foundational mechanisms

### 🎯 Critical Theoretical Questions

1. **Q1.2**: Why exactly ρ=2.0 for temporal systems?
    - *Status*: Empirically confirmed (Exp #50), mechanism understood qualitatively
    - *Need*: Analytical derivation from discrete wave equation

2. **Q1.1**: Why ρ≈1.5 for spatial dimensions?
    - *Status*: Measured across 3D-5D, but no proof
    - *Hypotheses*: Surface-area law, diffusion scaling, percolation theory

3. **Q2.1**: Can Lorentz transforms emerge from discrete symmetries?
    - *Stakes*: Determines if tick-frame is compatible with relativity
    - *Challenge*: Exp #50 shows tick-frame ≠ Minkowski spacetime

### 🔬 High-Impact Experiments Needed

- **Q5.1**: Does expansion coupling create matter-antimatter imbalance?
    - *Prediction*: Asymmetry from geometry even with symmetric initial conditions
    - *Problem*: Not observed yet (relates to Q7.1 over-coherence)

- **Q1.4**: Can we measure ρ in real physical systems?
    - *If yes*: Direct empirical connection to real physics
    - *Difficulty*: Requires experimental physics access

### 🏗️ Implementation Gaps

- **Q6.3**: How to implement the observer model?
    - *Status*: Fully theoretical (Ch4), no code exists
    - *Blocks*: Sleep mechanism, selective perception, temporal indexing

- **Q7.2**: Should Java update from Ch15 to Doc 49 ontology?
    - *Trade-off*: Better theory alignment vs major refactoring risk

### 🧠 Deep Physics Mysteries

- **Q4.1**: Can quantum mechanics emerge from discrete substrate?
    - *If yes*: Unifies QM with tick-frame
    - *Challenge*: Requires proof that continuous QM is low-energy limit

- **Q3.1**: Can we derive G from expansion rate λ?
    - *If yes*: Gravity is emergent, not fundamental
    - *Formula*: G ∝ λ × (l_planck)³ / (t_planck)²?

- **Q3.4**: ✅ **VALIDATED** - How does gravity emerge from tick budgets?
    - *Answer*: Coupled reaction-diffusion + regenerative energy creates unified GR+SR
    - *Status*: V9 complete - r ≈ 0.999 correlation, 100% pass (0.1c-0.5c), 90% pass (0.9c)
    - *See*: Exp #51 v9/RESULTS.md, EXPERIMENTAL_ARC.md

### 🤔 Philosophical Questions

- **Q6.1**: Can qualia emerge from self-referential indexing?
    - *Stakes*: Naturalistic explanation for consciousness
    - *Status*: Highly speculative (Ch4 marked as speculative)

- **Q8.1**: Can we measure "choice" as tick budget allocation?
    - *If yes*: Computational measure of free will
    - *Requires*: Observer implementation (Q6.3)

---

## Quick Navigation by Urgency

**Do This Week**:

- Run Experiment #49 (Q9.1)
- Tune λ parameter to fix over-coherence (Q7.1, Q5.1)

**Do This Month**:

- Derive ρ=2.0 analytically (Q1.2)
- Test ternary logic dynamics (Q8.2)

**Do This Quarter**:

- Implement observer model (Q6.3)
- Attempt Lorentz transform derivation (Q2.1)

**Long-Term Research**:

- QM emergence (Q4.1)
- Gravity derivation (Q3.1)
- Real-world ρ measurement (Q1.4)

---

## Quick Stats

**By Difficulty**:

- 3 questions are low-hanging fruit (can do quickly)
- 13 questions need focused effort (weeks-months)
- 11 questions need deep expertise (months-years)
- 8 questions may require new physics/philosophy (years-decades)

**By Impact**:

- 4 questions are foundational (could change framework)
- 8 questions validate core predictions
- 12 questions extend to new domains
- 11 questions are refinements

**Already Answered**: 8 major questions fully resolved (3 NEW in January 2026!)

- Time ≠ dimension (Exp #50) - ✓ Complete
- Sorting unnecessary (Exp #44_05) - ✓ Complete
- 3D optimal (Exp #15) - ✓ Complete
- Rotation asymmetry (Exp #44_03) - ✓ Complete
- Gravity from tick budgets (Exp #51 v1-v9) - ✓ Complete (r ≈ 0.999 validation)
- **Geodesics without force laws (Exp #53 v10)** - ✓ **NEW** (100% orbital success)
- **Collision physics (Exp #55)** - ✓ **NEW** (three regimes + emergent Pauli exclusion!)
- **Matter-antimatter asymmetry (Doc 061 + Exp #55)** - ✓ **NEW** (pattern diversity explanation)

---

## Priority Classification

### Critical (Foundational)

Questions that could invalidate or fundamentally alter the framework if answered differently.

### High Priority (Validation)

Questions whose answers would significantly strengthen or clarify core predictions.

### Medium Priority (Extension)

Questions that extend the framework into new domains without challenging foundations.

### Low Priority (Refinement)

Questions about details, optimizations, or minor theoretical points.

---

## I. Dimensional Physics

### Critical Questions

#### Q1.1: Why exactly ρ ≈ 1.5 for spatial dimensions?

**Current Status**: Empirically measured in Experiment #15 (3D, 4D, 5D all show ρ ≈ 1.5), but no analytical derivation.

**Question**: Can we derive ρ ≈ 1.5 from first principles?

**Hypotheses**:

- **Surface-area hypothesis**: ρ ≈ 1.5 emerges from (d-1)-dimensional surface area law with corrections
- **Diffusion hypothesis**: Related to random walk scaling on d-dimensional lattice
- **Percolation hypothesis**: Critical exponent from percolation theory

**Implications**:

- If derivable: Confirms dimensional framework is not ad-hoc
- If not derivable: May require new physical principle

**Difficulty**: High (requires analytical physics or rigorous simulation theory)

**Related**: Ch2 §3, Ch7 §6, QUICK_REFERENCE

**Proposed Approach**:

1. Analytical: Solve wave equation on d-dimensional lattice with multiple sources
2. Numerical: Vary lattice structure to test surface-area hypothesis
3. Statistical mechanics: Connect to known critical exponents

---

#### Q1.2: Why exactly ρ = 2.0 for temporal systems?

**Current Status**: **SMOKING GUN** - Experiment #50 shows ρ = 2.000 ± 0.002 universally across all (n+t) systems
tested.

**Question**: Why is the convergence so precise? What is the analytical mechanism?

**Hypotheses**:

- **Ratchet effect**: Temporal accumulation creates quadratic scaling
- **Coherence amplification**: Sources interfere constructively along time axis
- **Causal coupling**: Each tick couples to previous tick, creating chain effect

**Implications**:

- ρ=2.0 is the **signature of temporal generators**
- Could enable detection of "temporal vs spatial" character in unknown systems
- May relate to fundamental constants

**Difficulty**: Medium-High (mechanism is understood qualitatively, analytical proof needed)

**Related**: Ch1 §9, REFERENCE_doc50_01, EXPERIMENT_INDEX #50

**Proposed Approach**:

1. Derive from discrete wave equation with temporal coupling term
2. Show quadratic scaling emerges from ∑(n=0 to T) contributions
3. Connect to known physics (energy-time uncertainty relation?)

---

### High Priority Questions

#### Q1.3: How does dimensional stability extend beyond 5D?

**Current Status**: Experiment #15 tested up to 5D, found diminishing returns (SPBI ≈ 2.0 for 4D-5D).

**Question**: Is there a "critical dimension" where behavior changes qualitatively? Or does it asymptote smoothly?

**Proposed Test**: Extend #15 to 6D, 7D, 8D, 10D

**Difficulty**: Medium (computational - high-dimensional grids are expensive)

**Related**: Ch2 §8 (Dimensional Closure)

---

#### Q1.4: Can ρ be measured in real physical systems?

**Current Status**: Only computational experiments. No physical measurements yet.

**Question**: Could we measure ρ in:

- Multi-particle physics experiments?
- Cosmological observations (CMB, large-scale structure)?
- Condensed matter systems with known dimensionality?

**Implications**: Would provide empirical connection between tick-frame theory and real physics.

**Difficulty**: Very High (requires experimental physics access)

**Related**: Ch8 §5 (Falsification Criteria)

---

### Medium Priority Questions

#### Q1.5: Does configuration independence hold at d < 3?

**Current Status**: Hypothesis H2 (configuration independence) falsified at d ≥ 3 but behavior at d=1, 2 unclear.

**Question**: Are 1D/2D substrates more sensitive to initial geometry?

**Proposed Test**: Extend #15 with focused 1D-2D sweep with varied geometries

**Difficulty**: Low (easy to test computationally)

**Related**: Ch2 §6

---

## II. Relativity and Lorentz Transforms

**🚀 NEW: See [proposed_experiments_gravity_relativity.md](proposed_experiments_gravity_relativity.md) for detailed
experimental proposals testing emergent relativity mechanisms from v1 documents (Experiments #51-55).**

### Critical Questions

#### Q2.1: Can Lorentz transforms be derived from discrete symmetries?

**Current Status**: Ch7 §9 speculates on connection, but no derivation attempted.

**Question**: Does tick-frame physics naturally produce Lorentz-like effects, or are they fundamentally incompatible?

**Sub-questions**:

- Can time dilation emerge from differential tick rates?
- Can length contraction emerge from spatial lattice effects?
- What role does v ≤ c constraint play?

**Implications**:

- If YES: Tick-frame could be compatible with relativity
- If NO: Tick-frame and relativity are fundamentally different ontologies

**Difficulty**: Very High (requires deep theoretical physics)

**Related**: Ch7 §9, Ch8 §8 (Minkowski vs Tick-Frame)

**Note**: Experiment #50 shows tick-frame spacetime ≠ Minkowski spacetime (ρ=2.0 vs ρ=1.5), suggesting fundamental
difference.

---

#### Q2.2: How does causality work at relativistic speeds?

**Current Status**: Tick-frame assumes global tick sequence. Relativity has relative simultaneity.

**Question**: Can tick-frame accommodate relative simultaneity, or is absolute tick-stream required?

**Hypotheses**:

- **Global tick-stream**: Preferred reference frame (violates relativity)
- **Emergent relativity**: Apparent relative simultaneity from observer limitations
- **Hybrid**: Absolute substrate, relative frame physics

**Implications**: Major ontological question about nature of time.

**Difficulty**: Very High (foundational)

**Related**: Ch5 §2 (Substrate Determinism), Ch7 §9

---

### High Priority Questions

#### Q2.3: Does tick-frame predict Planck-scale Lorentz violation?

**Current Status**: Listed as falsification criterion #1, but no concrete prediction.

**Question**: What specific violations should we expect? At what energy scale?

**Proposed Test**: Derive predicted dispersion relation for high-energy photons.

**Difficulty**: High (requires QFT-level calculation)

**Related**: Ch8 §5, QUICK_REFERENCE (Falsification Criteria)

---

## III. Gravity and Expansion

**🚀 NEW: See [proposed_experiments_gravity_relativity.md](proposed_experiments_gravity_relativity.md) for experimental
proposals testing emergent gravity as time-flow gradients (Experiments #51-53, #55).**

### High Priority Questions

#### Q3.1: Is G derivable from substrate expansion rate?

**Current Status**: Ch7 §8 speculates that gravitational constant G might emerge from expansion coupling λ.

**Question**: Can we derive G = 6.674×10⁻¹¹ m³/(kg·s²) from tick-frame parameters?

**Proposed Relationship**:

```
G ∝ λ × (l_planck)³ / (t_planck)² ?
```

**Implications**:

- If YES: Gravity is emergent from substrate expansion
- Provides explanation for why G has its specific value

**Difficulty**: Very High (requires quantum gravity-level physics)

**Related**: Ch7 §8, Ch3 §4 (Expansion Coupling)

---

#### Q3.2: What is the correct expansion coupling value λ?

**Current Status**: λ ≈ 0 in current implementation (expansion not active).

**Question**: What value of λ produces realistic physics?

**Sub-questions**:

- Should λ be constant or time-varying?
- Does λ relate to cosmological expansion (Hubble constant)?
- What range of λ is stable?

**Proposed Test**: Sweep λ values in Java implementation, measure structural stability.

**Difficulty**: Medium (requires implementation work)

**Related**: Ch3 §4, Ch7 §7, Ch8 §4 (Over-Coherence Problem)

---

#### Q3.3: Can tick-frame explain dark energy?

**Current Status**: Not addressed in current framework.

**Question**: Does substrate expansion create apparent accelerating expansion?

**Speculation**: If space expands by fixed Δx per tick, but observers measure in non-expanding units, would this appear
as accelerating expansion?

**Difficulty**: Very High (requires cosmology expertise)

**Related**: Ch7 §8

---

### Medium Priority Questions

#### Q3.4: How does gravity emerge from time-flow gradients?

**Current Status**: ✅ **VALIDATED** by Experiment #51 (v1-v9)

**Question**: Can we make this concrete? What is the metric?

**Answer from Exp #51**:

- ✅ Time dilation DOES emerge from tick-budget competition (quantitatively validated)
- ❌ Simple resource allocation doesn't work (v1 falsified)
- ✅ **Requires coupled field dynamics** (v7-v9 validated):
    - Load field L(x,t): Reaction-diffusion with saturation
    - Energy field E(x,t): Local regeneration with load drainage
    - γ_eff(x) = <work_done> / substrate_ticks

**Validated Mechanism** (V7-V9):

```
∂L/∂t = α∇²L + S(x) - γL²       (load diffuses and saturates)
∂E/∂t = R - W(L,E) - D·L        (energy regenerates and drains)
γ_grav(x) = f(L, E)             (gravitational time dilation)
γ_SR(v) = 1/√(1-v²/c²)          (special relativistic factor)
γ_total = γ_grav × γ_SR         (multiplicative combination)
```

**Key Findings**:

- V7: Two-zone time dilation (γ: 0.23 → 0.50)
- V8: First smooth gradient (γ: 0.0018 → 0.0037, but too weak)
- V9: **Combined GR+SR validated** (r ≈ 0.999 correlation)
    - 100% validation at 0.1c, 0.5c
    - 90% validation at 0.9c
    - Goldilocks zone confirmed
- Regenerative energy essential to prevent collapse
- Space must be represented as computational field

**Remaining Questions**:

- Can we implement emergent trajectories (replace forced circular orbits)?
- Does gradient create geodesic motion? (Exp #53)
- Can ultra-relativistic regime (>0.9c) be improved?

**Difficulty**: Medium → **VALIDATED**

**Related**:

- Ch4 §6, Ch7 §9 (original speculation)
- Exp #51 v1-v8 (experimental validation)
- `experiments/51_emergent_time_dilation/EXPERIMENTAL_ARC.md` (full journey)

---

## IV. Quantum Mechanics

### Critical Questions

#### Q4.1: How does QM emerge from discrete substrate?

**Current Status**: Ch7 §4 shows discrete Schrödinger equation, but no emergence proof.

**Question**: Can we derive quantum behavior from tick-frame as a low-energy approximation?

**Sub-questions**:

- Does uncertainty principle emerge from sampling limits?
- Does superposition emerge from observer limitations?
- Does entanglement emerge from shared causal history?

**Implications**: If quantum mechanics is emergent, it would unify QM and tick-frame.

**Difficulty**: Very High (requires quantum foundation expertise)

**Related**: Ch7 §4, Ch7 §10

---

#### Q4.2: How does QFT work on tick-lattice?

**Current Status**: Not addressed beyond speculation in Ch7 §10.

**Question**: Can we formulate quantum field theory on discrete spacetime lattice?

**Known Work**: Lattice QCD exists, but uses different ontology.

**Difficulty**: Very High (requires QFT expertise)

**Related**: Ch7 §10, Ch8 §8

---

### High Priority Questions

#### Q4.3: Does discrete time create novel quantum effects?

**Current Status**: Not explored.

**Question**: Are there quantum phenomena unique to discrete time that don't exist in continuous theories?

**Examples**:

- Temporal aliasing of quantum states?
- Nyquist-like limit on quantum frequencies?
- Discrete-time quantum walks?

**Proposed Test**: Simulate quantum system on discrete vs continuous time, compare.

**Difficulty**: High (requires quantum simulation)

**Related**: Ch7 §4

---

## V. Energy and Conservation Laws

### High Priority Questions

#### Q5.1: Does imbalance theory create matter-antimatter asymmetry?

**Current Status**: Predicted in Ch3 §4, but NOT observed in current implementation.

**Question**: Why doesn't expansion coupling λ create expected imbalance?

**Current Problem**: "Over-coherence" - structures are too uniform (Ch8 §4).

**Hypotheses**:

- λ is too small (≈ 0) in current implementation
- Collision model is too naive
- Need chaotic initial conditions

**Proposed Test**: Increase λ systematically, measure structural asymmetry.

**Difficulty**: Medium (implementation refinement)

**Related**: Ch3 §4, Ch3 §11, Ch8 §4

**Status**: **Active research priority** (mentioned in CLAUDE.md as current work)

---

#### Q5.2: Is energy truly linear with time or conserved?

**Current Status**: Ch3 §5 implements E(t) = t - t_birth (linear growth).

**Question**: Is this correct, or should energy be conserved from initial conditions?

**Implications**:

- Linear growth: Energy is a function of existence duration
- Conservation: Energy is an initial property

**Current Behavior**: Linear growth creates issues (entities accumulate infinite energy if they persist).

**Proposed Resolution**: Energy growth rate may depend on activity, not just existence.

**Difficulty**: Medium (requires entity dynamics refinement)

**Related**: Ch3 §5, Ch7 §3

---

### Medium Priority Questions

#### Q5.3: Can we derive E = mc² from tick-frame?

**Current Status**: Not attempted.

**Question**: Does rest energy emerge from tick-rate?

**Speculation**: If each tick contributes E_planck, and entity persists T ticks, then E = T × E_planck. Connection to
mass?

**Difficulty**: High (requires relativistic physics connection)

**Related**: Ch7 §3

---

## VI. Consciousness and Observer Model

### Critical Questions

#### Q6.1: Can qualia emerge from self-referential indexing?

**Current Status**: Speculated in Ch4 §4, but no mechanism proposed.

**Question**: Is subjective experience an inevitable consequence of self-referential temporal processes?

**Sub-questions**:

- What is the minimal complexity for qualia?
- Do simpler observers (e.g., thermostats) have any qualia?
- Can we test this computationally?

**Implications**: If yes, provides naturalistic explanation for consciousness.

**Difficulty**: Very High (philosophy of mind)

**Related**: Ch4 §4

**Status**: Highly speculative (Chapter 4 is marked as speculative)

---

#### Q6.2: Is sleep computationally necessary, or just analogous?

**Current Status**: Ch4 §6 proposes sleep as buffer clearing to prevent collapse.

**Question**: Can we demonstrate an observer that MUST sleep or loses coherence?

**Proposed Test**: Implement observer model with bounded buffer, show performance degrades without periodic clearing.

**Difficulty**: Medium (requires implementation)

**Related**: Ch4 §6

---

### High Priority Questions

#### Q6.3: Can we implement the observer model?

**Current Status**: Observer model is theoretical (Ch4), not implemented in Java codebase.

**Question**: What are the practical steps to implement TickTimeConsumer<ObserverState>?

**Sub-questions**:

- How to represent selective perception?
- How to implement historical indexing?
- What is the buffer structure?
- How to trigger "sleep" cycles?

**Difficulty**: Medium-High (requires architecture design)

**Related**: Ch4, CLAUDE.md (Implementation Status)

**Status**: Mentioned as gap in CLAUDE.md

---

### Medium Priority Questions

#### Q6.4: Do trauma, déjà vu, and dreams have testable predictions?

**Current Status**: Explained qualitatively in Ch4 §7 as tick patterns.

**Question**: Can we derive quantitative predictions about these phenomena?

**Examples**:

- Trauma: High-salience ticks should have measurably lower activation thresholds
- Déjà vu: Should correlate with similar spatial patterns at different times
- Dreams: Should show higher entropy than waking state

**Difficulty**: Very High (requires neuroscience/psychology data)

**Related**: Ch4 §7

---

## VII. Implementation and Simulation

### High Priority Questions

#### Q7.1: Why is the current implementation "over-coherent"?

**Current Status**: **Active problem** - Ch3 §11, Ch8 §4, CLAUDE.md all mention this.

**Question**: What parameters need adjustment to create realistic chaos?

**Hypotheses**:

1. **Expansion coupling λ ≈ 0**: Need to increase to create imbalance
2. **Collision model too naive**: Need full collision dynamics from Doc 30
3. **Initial conditions too ordered**: Need chaotic seeding
4. **Energy model wrong**: Linear growth creates too much stability

**Proposed Tests**:

1. Sweep λ from 0 to 0.1
2. Implement full collision model
3. Randomize initial conditions
4. Add energy decay or leakage

**Difficulty**: Medium (requires experimentation)

**Related**: Ch3 §11, Ch8 §4, CLAUDE.md

**Status**: **Current research priority**

---

#### Q7.2: Should Java implementation update to Doc 49 ontology?

**Current Status**: Java is based on Ch15 (earlier model), but theory has evolved to Doc 49 (Ch1).

**Question**: What are the practical benefits and costs of updating?

**Benefits**:

- Aligns implementation with current theory
- May resolve over-coherence
- Cleaner conceptual model

**Costs**:

- Major refactoring
- Risk of introducing new bugs
- Existing experiments may break

**Proposed Approach**: Incremental update, validate at each step.

**Difficulty**: High (major engineering effort)

**Related**: CLAUDE.md (Known Issues)

---

#### Q7.3: Can we reach 1M entities @ 60 FPS?

**Current Status**: Experiment #44_05 achieves ~297k @ 60 FPS with O(n) bucketing.

**Question**: What optimizations are needed to reach 1M?

**Proposed Techniques**:

1. GPU compute shaders for bucketing
2. Spatial hashing for collision detection
3. Instanced rendering
4. Parallel tick execution

**Difficulty**: Medium-High (requires GPU programming)

**Related**: EXPERIMENT_INDEX #44_05, proposed #44_06

---

### Medium Priority Questions

#### Q7.4: ✅ **RESOLVED** - Should collision dynamics use naive or full model?

**Status**: **Full model validated** by Experiment #55.

**Answer**: Full collision model with pattern overlap is necessary and validated.

- ✅ Three-regime framework works (merge/explode/excite)
- ✅ Pattern structure (type, energy, mode, phase) required for realistic physics
- ✅ Pauli exclusion emerged from pattern overlap + cell capacity
- Full model is theoretically correct AND produces emergent physics

**Related**: Ch3 §3, Exp #55, Doc 053

---

#### Q7.5: Is cell capacity E_max universal or scenario-dependent?

**Current Status**: Experiment #55 used E_max = 20.0 for all test cases. Needs broader validation.

**Question**: Can a single E_max value work across all collision scenarios (particles, atoms, molecules, black holes)?

**Sub-questions**:

- Should E_max be constant across all cells?
- Does E_max scale with spatial dimension or energy density?
- Is E_max a fundamental constant (like Planck energy)?

**Implications**:

- If universal: Strong evidence for fundamental physics
- If scenario-dependent: May be artifact of computational limits

**Proposed Test**: Test Exp #55 collision framework with varied E_max values, measure outcome distributions.

**Difficulty**: Medium (requires parameter sweep)

**Related**: Exp #55, Doc 053, honest_status.md (Failure Mode 5 - Overfitting)

---

#### Q7.6: Can γ-well binding create stable composite objects?

**Current Status**: Experiment #56 structures implemented (H atom, He nucleus, H2 molecule), binding validation pending.

**Question**: Do γ-wells from time-flow minima naturally hold multi-particle composites together?

**Sub-questions**:

- What minimum γ-gradient strength is required for binding?
- Can orbital dynamics maintain stability over 1000+ ticks?
- Do composite objects dissolve under external perturbation?

**Proposed Test**: Run Exp #56 Phase 3b validation (long-duration stability test).

**Difficulty**: Medium (requires completion of Exp #56)

**Related**: Exp #56, Doc 054, Ch3 §4

**Status**: **NEXT IMMEDIATE PRIORITY** (Exp #56 Phase 3b)

---

## VIII. Free Will and Ternary Logic

### High Priority Questions

#### Q8.1: Can tick budget allocation be measured?

**Current Status**: Theoretical (Ch5 §5) - no implementation or measurement.

**Question**: If we implement observer model, can we quantify "choice" as tick allocation?

**Implications**: Would provide computational measure of agency.

**Difficulty**: High (requires observer implementation)

**Related**: Ch5 §5

---

#### Q8.2: Does ternary logic {-1, 0, +1} create richer dynamics?

**Current Status**: Theoretical (Ch5 §6) - XOR rule proposed but not validated.

**Question**: Does ternary system show emergent properties binary systems lack?

**Proposed Test**: Implement binary vs ternary tick-engine, compare complexity.

**Difficulty**: Low-Medium (straightforward implementation)

**Related**: Ch5 §6, Experiment #39 (Law-000 uses binary currently)

---

### Medium Priority Questions

#### Q8.3: Is void asymmetry observable?

**Current Status**: Theoretical principle (Ch5 §9) - presence (+1) costs energy, absence (0) is default.

**Question**: Does this create measurable bias in simulations?

**Proposed Test**: Measure distribution of {-1, 0, +1} states over time, check if skewed.

**Difficulty**: Low (analysis of existing data)

**Related**: Ch5 §9

---

## IX. Gamma Field Theory

### Critical Questions

#### Q9.5: Is the gamma field a scalar field or a tensor field?

**Current Status**: Ch10 treats γ(x,t) as scalar. But EM unification (Ch12) decomposes curvature into radial and
tangential components, suggesting tensor structure.

**Question**: Does the gamma field require tensor representation to accommodate electromagnetism?

**Sub-questions**:

- Can a scalar field support the radial/tangential decomposition needed for EM unification?
- Does the hill model require directional (tensor) curvature?
- What is the minimal mathematical structure needed?

**Implications**:

- If scalar: Simpler implementation, but EM unification may be approximate
- If tensor: Richer physics, but much harder to simulate

**Difficulty**: High (requires mathematical physics)

**Related**: Ch10 (scalar definition), Ch12 §3 (EM decomposition), Ch12 §7 (curvature duality)

---

#### Q9.6: Can the well-to-hill transition be made rigorous?

**Current Status**: Ch12 §6-§10 argues that well and hill are dual interpretations of the same geometry, but the
energetic consequences differ radically. The hill interpretation (entities gain surplus from curvature) is preferred.

**Question**: Under what precise conditions does the well interpretation break down and the hill interpretation become
necessary?

**Hypotheses**:

- **Frame-dependent**: Well and hill are always dual; choice is conventional
- **Energy-dependent**: Below some threshold → well behavior; above → hill behavior
- **Topology-dependent**: The transition depends on global field structure, not local curvature

**Difficulty**: High (foundational theoretical question)

**Related**: Ch12 §6 (debate), Ch12 §7 (duality), Ch12 §8 (hill energetics)

---

### High Priority Questions

#### Q9.7: Does the gamma field predict dark matter distribution?

**Current Status**: Ch9 §3-§5 proposes dark matter as frozen gamma-field geometry — fossil imprints from early universe
expansion. No quantitative prediction yet.

**Question**: Can gamma-field dynamics reproduce observed dark matter halos and large-scale structure?

**Proposed Test**: Simulate gamma-field evolution with expansion, check if fossil geometry matches rotation curve data.

**Difficulty**: Very High (requires cosmological simulation and observational comparison)

**Related**: Ch9 §3-§5, Ch10 (field dynamics), Exp #80 (gamma-field rendering)

---

#### Q9.8: How does charge arise from lag-flow asymmetry?

**Current Status**: Ch12 §4 proposes charge as geometric handedness of imprint shear. This is qualitative; no
mechanism produces discrete charge values (+1, -1, 0).

**Question**: What gamma-field geometry produces quantized charge?

**Sub-questions**:

- Why is charge quantized (not continuous)?
- How does charge conservation emerge from field dynamics?
- Can fractional charges (quarks) arise from partial shear configurations?

**Difficulty**: Very High (requires deep field-theory connection)

**Related**: Ch12 §4 (charge definition), Ch11 §2 (photon), Ch12 §5 (EM interactions)

---

#### Q9.9: Can the hill ontology of life be experimentally tested?

**Current Status**: Ch13 §7 proposes 10 axioms for life as self-reinforcing slow-time structure. These are
philosophical/geometric, not yet connected to measurable quantities.

**Question**: Is there a measurable quantity (e.g., local time dilation, entropy production rate) that distinguishes
living from non-living matter in gamma-field terms?

**Proposed Test**: Compare local gamma-field properties of biological vs non-biological systems in simulation.

**Difficulty**: Very High (requires bridge between physics and biology)

**Related**: Ch13 §7 (10 axioms), Ch13 §6 (cooperation), Ch13 §8 (reproduction)

---

### Medium Priority Questions

#### Q9.10: What is the gamma-field analogue of the electromagnetic spectrum?

**Current Status**: Ch9 §8.5 hypothesizes that all wave phenomena are gamma-field imprint propagation at different
scales. Ch12 §3 decomposes EM into radial/tangential curvature.

**Question**: Can we derive the full EM spectrum (radio → gamma rays) from gamma-field dynamics?

**Proposed Test**: Simulate oscillating charge (lag-shear source) in gamma field, measure radiated wave properties.

**Difficulty**: High (requires wave simulation in gamma field)

**Related**: Ch9 §8.5 (gamma spectrum hypothesis), Ch12 §3 (EM unification), Exp #63 (magnetron)

---

#### Q9.11: Can the cooperative curvature principle explain multicellularity?

**Current Status**: Ch13 §6 argues cooperation is geometric necessity — cooperating processes raise the hill faster.
This is axiomatic, not derived.

**Question**: Does gamma-field simulation show that cooperating entities achieve higher curvature than isolated ones?

**Proposed Test**: Simulate N isolated entities vs N cooperating entities, compare hill height over time.

**Difficulty**: Medium (requires gamma-field simulation with entity interaction)

**Related**: Ch13 §6 (cooperation), Ch10 §8 (compatibility maximization)

---

## X. Rendering and Visualization

### High Priority Questions

#### Q9.1: Can sliding window implement full existence buffer?

**Current Status**: Experiment #49 designed but awaiting execution.

**Question**: Does dynamic window correctly implement Ch4 §3 existence buffer concept?

**Sub-questions**:

- Does window size correlate with "memory capacity"?
- Does holographic horizon preserve meaningful information?
- Can temporal playback simulate "observer navigation"?

**Proposed Test**: Run #49, validate against Ch4 predictions.

**Difficulty**: Low (experiment ready to run)

**Related**: EXPERIMENT_INDEX #49, Ch4 §3

**Status**: **Next immediate experimental validation**

---

#### Q9.2: Does temporal rendering reveal physics insights?

**Current Status**: Experiment #44 series shows rendering techniques, but unclear if they reveal new physics.

**Question**: Are temporal trails, motion blur, etc. just visualizations, or do they reveal substrate properties?

**Proposed Exploration**: Use rendering to detect anomalies or patterns not visible in raw data.

**Difficulty**: Medium (requires creative analysis)

**Related**: EXPERIMENT_INDEX #44 series

---

## Research Priorities (Ordered)

### Tier 1: Critical and Feasible

1. **Q7.1**: Resolve over-coherence problem ← **CURRENT PRIORITY**
2. **Q9.1**: Execute Experiment #49 (sliding window)
3. **Q5.1**: Validate imbalance theory with active λ
4. **Q1.2**: Derive ρ=2.0 analytically
5. **Q9.6**: Rigorize well-to-hill transition (Ch12)

### Tier 2: High Impact, High Difficulty

5. **Q2.1**: Lorentz transform derivation
6. **Q4.1**: QM emergence from discrete substrate
7. **Q3.1**: Derive G from expansion rate
8. **Q6.3**: Implement observer model
9. **Q9.5**: Scalar vs tensor gamma field (Ch10/Ch12)
10. **Q9.8**: Charge quantization from lag-flow asymmetry (Ch12)

### Tier 3: Experimental Validation

11. **Q1.4**: Measure ρ in real physical systems
12. **Q2.3**: Predict Planck-scale Lorentz violation
13. **Q6.4**: Test psychological phenomena predictions
14. **Q9.7**: Dark matter from gamma-field fossil geometry (Ch9)

### Tier 4: Extensions and Refinements

15. **Q8.2**: Ternary logic validation
16. **Q7.3**: Optimize to 1M entities
17. **Q1.3**: Extend dimensionality tests to 10D
18. **Q9.10**: EM spectrum from gamma-field dynamics (Ch12)
19. **Q9.11**: Cooperative curvature and multicellularity (Ch13)

---

## Questions by Difficulty

### Low Difficulty (Can be addressed quickly)

- Q1.5: Configuration independence at d < 3
- Q8.3: Void asymmetry observation
- Q9.1: Run Experiment #49 (already designed)

### Medium Difficulty (Require focused effort)

- Q3.2: Determine correct λ value
- Q5.2: Refine energy model
- Q6.2: Implement observer sleep mechanism
- Q7.1: Resolve over-coherence
- Q7.4: Full vs naive collision model
- Q8.2: Ternary logic dynamics

### High Difficulty (Require deep expertise)

- Q1.1: Derive ρ ≈ 1.5 analytically
- Q1.2: Derive ρ = 2.0 analytically
- Q2.3: Predict Lorentz violations
- Q3.1: Derive G from λ
- Q4.3: Novel quantum effects
- Q6.3: Implement full observer model
- Q7.2: Update Java to Doc 49

### Very High Difficulty (Require new physics/philosophy)

- Q2.1: Derive Lorentz transforms
- Q2.2: Reconcile with relativity
- Q3.3: Explain dark energy
- Q3.4: Emergent gravity mechanism
- Q4.1: QM emergence
- Q4.2: QFT on tick-lattice
- Q5.3: Derive E = mc²
- Q6.1: Qualia emergence

---

## Questions by Status

### Active Investigation

- Q7.1: Over-coherence (mentioned in CLAUDE.md as current work)
- Q5.1: Imbalance theory (part of over-coherence problem)

### Ready to Test

- Q9.1: Experiment #49 (implementation complete, awaiting execution)
- Q1.5: Low-dimensional configuration tests (easy extension of #15)
- Q8.2: Ternary logic (can use existing tick-engine framework)

### Requires Implementation

- Q6.3: Observer model (no code exists yet)
- Q7.4: Full collision model (theoretical basis exists in Doc 30)
- Q3.2: Expansion coupling (λ parameter exists but ≈ 0)

### Requires Theory Development

- Q1.1, Q1.2: Analytical derivations of ρ
- Q2.1: Lorentz transform derivation
- Q3.1: Gravitational constant derivation
- Q4.1: QM emergence proof

### Deferred (Speculative)

- Q6.1: Qualia emergence (philosophy of mind)
- Q6.4: Psychological predictions (requires neuroscience data)
- Q3.3: Dark energy connection (requires cosmology)

---

## Connections to Existing Documentation

**QUICK_REFERENCE** lists 5 open questions:

1. Lorentz transforms (Q2.1)
2. ρ≈1.5 derivation (Q1.1)
3. Imbalance validation (Q5.1)
4. QFT formulation (Q4.2)
5. Gravity mechanism (Q3.1)

**EXPERIMENT_INDEX** proposes future experiments:

- 44_06: GPU bucketing (addresses Q7.3)
- 44_07: Z-buffer hybrid
- 44_08: Java integration (addresses Q7.2)
- Collision dynamics (addresses Q7.4)
- Energy balance (addresses Q5.1, Q5.2)
- Observer implementation (addresses Q6.3)

**CLAUDE.md** mentions current work:

- Over-coherence (Q7.1) ← **ACTIVE**
- Collision dynamics tuning (Q7.4)
- Performance scaling (Q7.3)

**Theory Chapters** ending sections:

- Ch1: Dimensional equivalence (validated by Exp #50)
- Ch2: Dimensional closure (Q1.3)
- Ch3: Imbalance theory (Q5.1), energy model (Q5.2)
- Ch4: Observer implementation (Q6.3), qualia (Q6.1)
- Ch5: Ternary logic (Q8.2), tick allocation (Q8.1)
- Ch7: Lorentz (Q2.1), gravity (Q3.1), QFT (Q4.2)

---

## How to Contribute

### For Researchers

1. **Choose a question** from Tier 1 or Tier 3 (feasible + important)
2. **Consult related documentation** (links provided for each question)
3. **Design experiment or analysis** following existing experiment structure
4. **Document results** in experiments/ directory
5. **Update this document** with findings

### For Theorists

1. **Focus on analytical derivations** (Q1.1, Q1.2, Q2.1)
2. **Connect to known physics** (relativity, QM, statistical mechanics)
3. **Document proofs** in theory/ directory
4. **Update relevant chapters** with derivations

### For Implementers

1. **Address implementation gaps** (Q6.3, Q7.2, Q7.4)
2. **Optimize performance** (Q7.3)
3. **Resolve current issues** (Q7.1 over-coherence)
4. **Document in CLAUDE.md** implementation notes

---

## Answered Questions (Archive)

Questions that were once open but have been resolved:

### ✓ Does time behave like a spatial dimension?

**Status**: **NO** - Decisively answered by Experiment #50.

- All (n+t) systems show ρ=2.0 (temporal) vs ρ=1.5 (spatial)
- 0% pass rate across all dimensional equivalence tests
- See: REFERENCE_doc50_01

### ✓ Is sorting required for temporal rendering?

**Status**: **NO** - Confirmed by Experiment #44_05.

- O(n) bucketing achieves 13-16× speedup vs O(n log n) sorting
- Discrete lag values enable counting sort
- See: REFERENCE_doc46_01, EXPERIMENT_INDEX #44_05

### ✓ Is 3D optimal for substrate physics?

**Status**: **YES** - Validated by Experiment #15.

- 3D achieves maximum SPBI = 2.23
- 4D-5D show diminishing returns
- See: REFERENCE_doc15, Ch2

### ✓ Does temporal surfing create rotation asymmetry?

**Status**: **YES** - Validated by Experiment #44_03.

- Forward pitch: 0% success (violates v ≤ c)
- Backward pitch: 93% success (energy-limited)
- Asymmetry ratio: 933×
- See: EXPERIMENT_INDEX #44_03, Ch6 §5

### ✅ Can gravity emerge from tick-budget competition?

**Status**: **VALIDATED** - Answered by Experiment #51 (v1-v9).

- ❌ Simple resource allocation doesn't work (v1 falsified)
- ✅ Sophisticated field dynamics DO work (v7-v9 validated)
- Requires coupled reaction-diffusion load field + regenerative energy
- V7: First stable time dilation (γ: 0.23 → 0.50)
- V8: First smooth gradient (γ: 0.0018 → 0.0037, but too weak)
- V9: **Combined GR+SR validated** (r ≈ 0.999, 100% pass at 0.1c-0.5c, 90% at 0.9c)
- Breakthrough: Single substrate reproduces both gravitational AND special relativistic time dilation
- See: EXPERIMENTAL_ARC.md, experiment_index #51, v9/RESULTS.md, honest_status.md

### ✅ Do geodesics emerge without programming force laws?

**Status**: **VALIDATED** - Answered by Experiment #53 (v10).

- ✅ **100% orbital success** - All 18 test entities achieved stable orbits
- ✅ Gradient-following mechanism: entities seek faster proper time (higher γ)
- ✅ Self-stabilization: too fast → larger radius → weaker gradient → slows down
- Circular orbits: 78% (14/18 entities, e < 0.1)
- Elliptical orbits: 22% (4/18 entities, 0.1 < e < 0.5)
- NO force laws programmed - orbits emerged purely from time-flow gradients
- See: experiments/51_emergent_time_dilation/v10/RESULTS.md, honest_status.md

### ✅ How does particle collision physics work in tick-frame?

**Status**: **VALIDATED** - Answered by Experiment #55.

- ✅ Three collision regimes: Merge (fusion), Explosion (annihilation), Excitation (redistribution)
- ✅ Pattern overlap algorithm validated (6/6 test cases passed)
- ✅ Energy conservation exact (ratio 1.000)
- ✅ **Pauli exclusion EMERGED** - NOT predicted or programmed!
  - Identical particles have moderate overlap (k_type = 0.5)
  - If E_total + E_overlap > E_max → explosion (rejection)
  - If E_total + E_overlap ≤ E_max → excitation (forced to different modes)
  - Emergence validates computational basis for quantum mechanics
- See: experiments/55_collision_physics/, docs/theory/raw/053_tick_frame_collision_physics.md

### ✅ Why didn't matter and antimatter completely annihilate in early universe?

**Status**: **EXPLAINED** - Framework provided by Doc 061 + validated by Exp #55.

- ✅ Annihilation requires precise multi-dimensional pattern matching (type, mode, phase, energy, timing, position)
- ✅ Pattern mismatch → merge, excitation, or scattering instead
- ✅ Pattern diversity prevents global annihilation
- ✅ No CP violation or baryogenesis needed - emerges naturally from pattern structure
- Residual matter is natural emergent outcome, not paradox
- See: docs/theory/raw/061_matter-antimatter_asymetry.md, Exp #55 validation

---

## Document Maintenance

**How to update this document**:

1. When a question is answered, move it to "Answered Questions" section
2. When new questions arise from experiments, add to appropriate section
3. Update priority/status as research progresses
4. Link to new experiments or theory documents as created
5. Archive deferred questions that are no longer relevant

**Review schedule**: After each major experiment or theory update

---

**Document Version**: 1.2
**Last Updated**: February 2026
**Total Questions**: 39 active + 8 answered
**Status**: Living document (will evolve with research)
**Major Update v1.2**: Added 7 gamma-field questions (Q9.5-Q9.11) from Ch9-Ch13 consolidation
**Major Update v1.1**: Added Exp #55 (collision physics + emergent Pauli exclusion), Exp #53 (geodesics), Doc 061 (matter-antimatter asymmetry)

**For specific question details, see cross-referenced theory chapters and experiments**
