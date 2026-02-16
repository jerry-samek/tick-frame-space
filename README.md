# Tick-Frame Space: Dimensional Physics Experiments
*Coherence over Orthodoxy: a model is valid if it is internally consistent, falsifiable, and explanatory, regardless of its alignment with current physical dogma.*

Welcome to the Tick-Frame Space project. My pet project on "garden leave." This repository contains a "working" **Java substrate model**, theoretical documentation, and experimental validation of discrete tick-frame physics. However, don't take it too seriously and feel free to correct me if I'm wrong (I definitely am). I'm an engineer, not a scientist. And I have plenty of spare memory-time to just think about crazy stuff.

## Overview

This is an exploration of how far the current Java can be pushed before collapsing, while testing a speculative physics model where:
- **Time is discrete** (advances in ticks, not continuous flow)
- **Space expands** with each tick following dimensional growth rules
- **Entities are collision patterns** that persist through temporal renewal
- **Everything is deterministic** at the substrate layer (no randomness, no infinity)
- **Everything is natural numbers** (BigInteger) - no fractions allowed
- **Energy is a function of time** (linear, not conserved from the initial state)

Every programmer is welcome to propose suggestions, optimizations, or tweaks. If you want to rewrite this model in another language, you are more than welcome.

Every physicist is welcome to review the theory and help map it to the real universe.

### Key Constraints

- **Strict substrate vs. visualization distinction** - substrate is deterministic, visualization is observer-dependent
- **No randomness at root** - finite rules generate infinite diversity
- **Motion as tick budget** - e.g., position {0,0}, vector (1,0), cost 20 → takes 20 ticks to reach (1,0)
- **Initial condition** - starts with 1×1×1 grid (simulating infinite energy density at universe origin)
- **Expansion dilutes energy** - as grid grows, density decreases structurally

---

## 🚀 Quick Start

### Run the Substrate Simulation

The **tick-space-runner** Java implementation is the primary way to run and interact with the tick-frame substrate model.

```bash
# Build the project
mvn clean package

# Run the substrate simulation
mvn exec:java -pl tick-space-runner -Dexec.mainClass="eu.jerrysamek.tickspace.runner.LocalApp"
```

**Output:** JSON snapshots of entity states exported to `W:\data\snapshots\` every 1000 ticks.

📖 **Full documentation:** [tick-space-runner/README.md](tick-space-runner/README.md)

### Analyze Snapshots

Once the simulation is running, use Python scripts to analyze the generated snapshots:

```bash
# Statistical analysis by radial shells
python scripts/snapshot-stats.py W:\data\snapshots\time-frame.5000.json

# 3D visualization
python scripts/snapshot-visualization.py W:\data\snapshots\time-frame.5000.json

# Energy distribution and density profiles
python scripts/snapshot-energy-histogram.py W:\data\snapshots\time-frame.5000.json
```

📖 **Full documentation:** [scripts/README.md](scripts/README.md)

---

## 🧩 Substrate Model Implementation

The **tick-space-runner** module contains the operational Java (25) implementation of tick-frame physics.

### Core Components

- **TickTimeModel** - Discrete time engine that advances the universe tick by tick
- **SubstrateModel** - Dimensional substrate that expands with each tick (typically 3D)
- **EntitiesRegistry** - Manages all entities with spatial indexing and collision detection
- **EntityModel** - Base abstraction for entities (single, colliding, composite)
- **LocalApp** - Primary runner that executes simulation and exports JSON snapshots

### Key Features

✅ **Parallel execution** - Work-stealing thread pool for entity updates
✅ **Collision-based persistence** - Entities are patterns, not static objects
✅ **Dimensional expansion** - Space grows at each tick following growth rules
✅ **JSON snapshots** - Export complete entity state every 1000 ticks
✅ **Performance monitoring** - Per-tick timing statistics (update, execution, total)

### Theoretical Implementation

**Note:** The current Java implementation is based on the earlier **Chapter 15** model ("Minimal Model Recommendation" and dimensional experiments). The theoretical framework has since evolved to Chapter 49's refined ontology, but the Java codebase has not yet been updated to reflect these newer concepts.

**Current Theoretical Framework (Chapter 49):**
- **Temporal Ontology of the Tick-Frame Universe** (Doc 49) - unified framework establishing temporal primacy, tick-stream as absolute substrate, space as emergent visualization, and temporal integrity laws

**Implemented Principles (Chapter 15 basis):**
- **Temporal Surfing Principle** (Doc 28) - entities persist through continual renewal
- **Collision Persistence Principle** (Doc 30) - particles as collision patterns
- **Imbalance Theory** (Doc 29) - matter-antimatter asymmetry from expansion geometry
- **Horizon Boundaries** (Doc 26) - observable limits in causal cones
- **Void Asymmetry Principle** (Doc 43) - matter surplus via ternary state stabilization
- **Observer-Relative Big Bang** (Doc 37) - Big Bang as observer event, not substrate event
- **Fallible Commit Principle** (Doc 44) - irreversible decisions with inherent lag
- **Physical Formalization** (Docs 47-48) - complete Planck-scale axioms and observer model

### Current Status

**Last Updated:** February 2026

**Theory Development:** 120+ theoretical documents, 11/13 computational validations complete

**Major Breakthroughs (January-February 2026):**
- ✅ **Time dilation validated** (Exp #51 v9: r ≈ 0.999 correlation with GR+SR)
- ✅ **Geodesics emerged naturally** (Exp #53 v10: 100% orbital success, NO force laws programmed!)
- ✅ **Graph-lattice gravity validated** (Exp #64_109 v9: self-subtracting tagged quanta, three-body dynamics, exact integer conservation — **second independent gravity implementation!**)
- ✅ **Collision physics validated** (Exp #55: 6/6 test cases, exact energy conservation)
- ✅ **Pauli exclusion discovered** (Exp #55: emerged from cell capacity - NOT programmed!)
- ✅ **Jitter stability range** (Exp #56 v13: 0.119 is NOT special, stable range [0.075, 0.5])
- ✅ **Canvas/Renderer ontology** (Exp #56 v17: O(entities) sparse storage, stable clustering)
- ✅ **Interferometry validated** (Exp #62: 26/26 tests, which-path WITHOUT collapse - FALSIFIABLE!)
- ⚠️ **Black hole c-ring discovered** (Exp #52 v11: stable at v≈c, awaiting collision validation)
- 🔄 **Composite objects** (Exp #56: H, He, H₂ structures implemented, binding validation pending)
- 🔬 **ZPE cosmological hypothesis** (Docs 072-073: jitter scales with expansion, explains early universe)

**Implementation observations:**
- ✅ Entities exhibit temporal surfing behavior
- ✅ Collision patterns create composite structures
- ✅ Expansion follows dimensional growth rules
- ⚠️ Over-coherence: structures too uniform (anisotropy deficit)
- ⚠️ Java implementation based on Doc 15, theory evolved to Doc 49

**Typical performance:** ~100ms per tick (~10-20ms updates, ~80-90ms execution)

📖 **Complete architecture & API:** [tick-space-runner/README.md](tick-space-runner/README.md)

---

## 📊 Snapshot Analysis Tools

Python scripts for analyzing JSON snapshots from LocalApp:

| Script | Purpose |
|--------|---------|
| `snapshot-stats.py` | Shell-wise statistics (Manhattan distance) |
| `snapshot-visualization.py` | 3D scatter plots colored by energy |
| `snapshot-energy-histogram.py` | Energy distribution & radial density |

**Snapshot format:** JSON arrays with entity position, energy, depth, momentum

📖 **Usage examples:** [scripts/README.md](scripts/README.md)

---

## 📚 Documentation

### Theory (76+ Documents - V2 Consolidated)

- **V2 Consolidated Framework** (January-February 2026)
    - [Theory README](docs/theory/README.md) - Complete framework guide and reading paths
    - [Ch1 Temporal Ontology](docs/theory/ch001_temporal_ontology.md) - Time as primary substrate
    - [Ch2 Dimensional Framework](docs/theory/ch002_dimensional_framework.md) - 3D optimality (SPBI=2.23)
    - [Ch3 Entity Dynamics](docs/theory/ch003_entity_dynamics.md) - Temporal surfing, collisions
    - [Ch7 Physical Formalization](docs/theory/ch007_physical_formalization.md) - Planck-scale axioms
    - [Ch8 Integration & Falsification](docs/theory/ch008_integration_falsification.md) - Validation status

- **Reference Documents** (Critical)
    - [REFERENCE_doc015_minimal_model](docs/theory/REFERENCE_doc015_minimal_model.md) - Java implementation basis
    - [REFERENCE_doc049_temporal_ontology](docs/theory/REFERENCE_doc049_temporal_ontology.md) - Theoretical constitution
    - [REFERENCE_doc050_01](docs/theory/REFERENCE_doc050_01_dimensional_equivalence_rejection.md) - ρ=2.0 smoking gun

- **Supporting Materials**
    - [honest_status.md](docs/theory/honest_status.md) - Brutally honest assessment of validated vs speculation
    - [experiment_index.md](docs/theory/experiment_index.md) - Cross-reference of all experiments
    - [glossary.md](docs/theory/glossary.md) - 85+ terms, 20+ symbols

- **New Theoretical Developments (February 2026)** - in `docs/theory/raw/`
    - **Docs 055-058**: Speed of light, propulsion limits
    - **Docs 063-066**: Electromagnetism framework
    - **Docs 072-073**: ZPE hypothesis (jitter scaling with expansion)
    - **Doc 074**: Ternary substrate correction axiom
    - **Doc 075**: Metabolic time dilation interpretation
    - **Docs 104-110**: Emission recoil, well-hill unification, Cooper pairs, 3D from trits, isotropy of c
    - **Docs 120-160**: Ontological reparameterization, photon imprint, GR geodesics, conservation laws
    - **Doc 200**: Foundational axioms and dependency graph ("RAW Constitution")
    - **Doc 300**: Complete ontological stack

### Model & Implementation

- [Computational Gravity Model](docs/model/01%20Computational%20Gravity%20-%20A%20Physics-Inspired%20Model%20for%20Tick-Based%20Resource%20Allocation.md)
- [Rendering Pipeline](docs/model/03%20Rendering%20pipeline.md)
- [Tick‑Frame Engine Documentation](docs/model/04%20Tick‑Frame%20Engine%20Documentation.md)

### Experimental Validation

**Tier 0 - Foundational (3,960+ simulations):**
- [SPBI Executive Summary](experiments/15_minimal-model/v6-gpu/SPBI_EXECUTIVE_SUMMARY.md) - 3D optimality validation
- [Dimensional Equivalence Rejection](docs/theory/REFERENCE_doc050_01_dimensional_equivalence_rejection.md) - ρ=2.0 signature

**Tier 1 - Physics Mechanisms (January-February 2026):**
- [Exp #51 Time Dilation](experiments/51_emergent_time_dilation/) - v1-v9, r≈0.999 GR+SR correlation
- [Exp #55 Collision Physics](experiments/55_collision_physics/) - Three regimes, emergent Pauli exclusion
- [Exp #56 Composite Objects](experiments/56_composite_objects/) - v1-v17, canvas ontology, jitter stability
- [Exp #64_109 Graph-Lattice Gravity](experiments/64_109_three_body_tree/) - Second independent gravity, three-body dynamics

---

## 🧪 Experiments

### Physics Mechanism Experiments (51-64 Series) - January-February 2026

- **51: Emergent Time Dilation** ✅ VALIDATED
    - [EXPERIMENTAL_ARC.md](experiments/51_emergent_time_dilation/EXPERIMENTAL_ARC.md) - Complete v1-v9 journey
    - **v9 Result:** r ≈ 0.999 correlation with GR+SR predictions
    - **v10 Result:** 100% orbital success (geodesics emerged, no force laws!)
    - **v11 Result:** Stable c-speed ring at r≈10.1 (black hole preliminary)

- **55: Collision Physics** ✅ VALIDATED
    - Three regimes (merge/explode/excite), 6/6 test cases
    - **DISCOVERY:** Pauli exclusion emerged naturally (NOT programmed!)
    - Energy conservation exact (ratio 1.000)

- **56: Composite Objects** 🔄 IN PROGRESS
    - [README](experiments/56_composite_objects/README.md) - Atoms, molecules, binding physics
    - **v4:** 200k tick stability (6.52% drift, 0/50 escapes)
    - **v13:** Jitter stability range [0.075, 0.5] validated (0.119 NOT special)
    - **v17:** [Canvas/Renderer ontology](experiments/56_composite_objects/v17/README.md) - O(entities) sparse storage

- **62: Interferometry** ✅ VALIDATED - FALSIFIABLE PREDICTION
    - 26/26 tests passed
    - Which-path detection WITHOUT wavefunction collapse
    - **Prediction:** V > 0.9 after path readout (vs QM: V → 0)

- **64_109: Three-Body on Graph Lattice** ✅ VALIDATED - SECOND GRAVITY IMPLEMENTATION
    - [Experiment Description](experiments/64_109_three_body_tree/experiment_description.md) - Complete v1-v9 journey
    - Self-subtracting integer-tagged quanta on 3D periodic lattice (8000 nodes, k=6)
    - **v8:** Attraction confirmed (distance 10→4 hops)
    - **v9:** Three-body dynamics (100K ticks, no merger, exact integer conservation)
    - **Key Insight:** Continuous internal direction on discrete lattice — gradient nudges accumulate, enabling smooth turning
    - **Convergence:** Completely different implementation from Exp #51, yet BOTH produce gravity

### Dimensional Physics Experiments (15 Series)

- **v6-gpu: Dimensional Sweeps** (3,960 simulations)
    - [SPBI Executive Summary](experiments/15_minimal-model/v6-gpu/SPBI_EXECUTIVE_SUMMARY.md)
    - 3D optimal (SPBI=2.23), phase transition at d=3

- **v7-final: Goldilocks Zone Validation**
    - [Experiment Plan](experiments/15_minimal-model/v7-final/Experiment%20Plan%20-%20SPBI%20and%20LHB%20validation.md)

### Temporal Rendering Experiments (44-49 Series)

- **44_05: Double Buffer Rendering** ✅ Validated
    - [RESULTS](experiments/44_05_double_buffer_rendering/RESULTS.md) - 2.78× speedup
    - O(n) bucketing vs O(n log n) sorting confirmed

- **49: Sliding Window Rendering** ✅ Validated
    - [RESULTS](experiments/49_sliding_window_rendering/RESULTS.md)
    - 120 FPS @ 6.6k entities | 75 FPS @ 10k entities

---

## 📊 Data & Visualizations

- Results CSVs:
    - [1D Results](experiments/15_minimal-model/v6-gpu/v6_gpu_1d_results.csv)
    - [2D Results](experiments/15_minimal-model/v6-gpu/v6_gpu_2d_results.csv)
    - [3D Results](experiments/15_minimal-model/v6-gpu/v6_gpu_3d_results.csv)
    - [4D Results](experiments/15_minimal-model/v6-gpu/v6_gpu_4d_results.csv)
    - [5D Results](experiments/15_minimal-model/v6-gpu/v6_gpu_5d_results.csv)

- Visualizations:
    - [Comprehensive Visualizations](experiments/15_minimal-model/v6-gpu/create_comprehensive_visualizations.py)

---

## 🔬 Scientific Status

**Theory Development:** 120+ documents spanning foundation to physical formalization, cosmological implications, and gamma-field ontology

**Computational Validation (February 2026):**
- **11/13 experiments validated** (4 Tier 0 foundational + 7 Tier 1 physics mechanisms)
- **Time dilation validated:** r ≈ 0.999 correlation with combined GR+SR predictions (Exp #51 v9)
- **Geodesics emerged naturally:** 100% orbital success without programming force laws (Exp #53 v10)
- **Graph-lattice gravity validated:** Self-subtracting tagged quanta produce three-body dynamics with exact integer conservation (Exp #64_109 v9) — **second independent gravity implementation!**
- **Collision physics validated:** Three regimes (merge/explode/excite), exact energy conservation (Exp #55)
- **Pauli exclusion discovered:** Emerged from cell capacity - genuinely surprising, NOT programmed! (Exp #55)
- **Jitter stability range:** 0.119 is within stable range [0.075, 0.5], NOT a fundamental constant (Exp #56 v13)
- **Canvas/Renderer ontology:** O(entities) sparse storage vs O(grid³), stable clustering (Exp #56 v17)
- **Interferometry validated:** Which-path detection WITHOUT wavefunction collapse - FALSIFIABLE prediction! (Exp #62)

**Key Scientific Contributions:**
- **Two Independent Gravity Implementations Converge:** Exp #51 (continuous fields) and Exp #64_109 (integer quanta on graph) both produce gravity — strongest evidence against "just a simulation artifact"
- **Emergent Gravity:** Geodesic motion from time gradients, NOT force laws
- **Continuous Direction on Discrete Lattice:** Internal state can be continuous even when hops are quantized — gradient nudges accumulate between hops, enabling smooth turning on a 6-neighbor lattice
- **Emergent Pauli Exclusion:** Arises from pattern overlap + cell capacity limits, NOT explicit programming
- **Void Asymmetry Principle:** Matter-antimatter asymmetry from ternary state stabilization ({-1, 0, +1})
- **Observer-Relative Cosmology:** Big Bang, dimensions, multiverse are observer properties, not substrate events
- **Memory as Indexing:** Brain indexes historical ticks; explains trauma, déjà vu, dreams
- **ZPE Hypothesis:** Jitter decreases with cosmic expansion, potentially explains early universe anomalies

**First Falsifiable Prediction:**
- **Interferometry:** Which-path information can be obtained WITHOUT destroying interference fringes
- **QM Prediction:** Visibility V → 0 after which-path measurement
- **Tick-Frame Prediction:** Visibility V > 0.9 after which-path measurement
- **Test:** Cold atom or neutron interferometer, delayed-choice quantum eraser (~$500K-$2M, 1-2 years)

**New Theoretical Developments (February 2026):**
- **Graph-Lattice Gravity (Exp #64_109):** Second independent gravity implementation using integer-tagged quanta on discrete graph
- **Continuous Direction on Discrete Lattice:** Key insight — internal state can be continuous even when hops are quantized
- **Foundational Axioms (RAW 200):** "RAW Constitution" — axiom hierarchy and dependency graph of the gamma-field ontology
- **ZPE/Jitter Scaling (Docs 072-073):** J(t) ∝ 1/a(t), explains early SMBHs and massive galaxies at z > 10
- **Ternary Substrate Correction (Doc 074):** Stability via integer corrections {-1, 0, +1}
- **Metabolic Time Dilation (Doc 075):** Entities "skip" rendering to conserve energy, not temporal slowdown
- **Electromagnetism Framework (Docs 063-066):** Theoretical foundation for EM in tick-frame substrate

**Defined Limitations:**
1. Still no connection to real-world physics experiments
2. Lorentz invariance recovery not yet demonstrated
3. ZPE hypothesis is pure speculation with no validation yet
4. Black hole c-ring needs collision validation (ghost particle limitation)

⚠️ **Speculation disclaimer:** This is a speculative computational model exploring discrete physics. Major computational validations achieved, but real-world experimental tests are still needed. The interferometry prediction (which-path without collapse) is the first truly testable difference from standard QM.

---

## 📝 Further Reading

### Quick Start Paths

1. **New Readers:** [Ch1 Temporal Ontology](docs/theory/ch001_temporal_ontology.md) → [Ch2 Dimensional Framework](docs/theory/ch002_dimensional_framework.md) → [experiment_index.md](docs/theory/experiment_index.md)
2. **Skeptics:** [REFERENCE_doc050_01](docs/theory/REFERENCE_doc050_01_dimensional_equivalence_rejection.md) (smoking gun) → [honest_status.md](docs/theory/honest_status.md) (reality check)
3. **Implementers:** [REFERENCE_doc015](docs/theory/REFERENCE_doc015_minimal_model.md) (Java basis) → [Ch3 Entity Dynamics](docs/theory/ch003_entity_dynamics.md)
4. **Breakthrough Results:** [Exp #51 v10](experiments/51_emergent_time_dilation/) (geodesics emerged!) → [Exp #55](experiments/55_collision_physics/) (Pauli emerged!) → [Exp #64_109](experiments/64_109_three_body_tree/) (graph gravity!)
5. **Latest Work:** [Exp #64_109](experiments/64_109_three_body_tree/experiment_description.md) (graph-lattice gravity) → [honest_status.md](docs/theory/honest_status.md)

### V2 Consolidated Theory (120+ Documents)

See [docs/theory/README.md](docs/theory/README.md) for complete framework:
- **Ch1-2:** Temporal Ontology, Dimensional Framework (validated)
- **Ch3:** Entity Dynamics (partially validated)
- **Ch4-5:** Observer & Consciousness, Free Will (speculative)
- **Ch6:** Rendering Theory (validated)
- **Ch7:** Physical Formalization (analytical)
- **Ch8:** Integration & Falsification (synthesis)
- **Ch9-13:** Gamma Field Foundations, Entity Physics, EM & Curvature, Hill Ontology
- **Raw 055-200:** ZPE, EM, metabolic dilation, graph gravity, foundational axioms

---

## 🤖 AI-Assisted Development

This project represents a novel approach to theoretical physics development: **AI as a tool for materialization, not invention.**

**The theory itself** — the core ideas, principles, and conceptual framework — **originates from human thought** during a period of "garden leave" exploration. The tick-frame universe, discrete time substrate, collision persistence, void asymmetry, and observer-relative cosmology are all products of human speculation and insight.

**AI's role** has been to help **materialize** these ideas:
- **Claude (Anthropic)** - Theory formalization, mathematical expression, documentation synthesis, experimental design, cross-consistency verification
- **GitHub Copilot** - Code implementation, Java substrate development, pattern completion, refactoring support

**This distinction matters:** AI is being used as an advanced tool for expression and implementation — much like using LaTeX for typesetting or MATLAB for simulations — not as the source of theoretical creativity. The human provides the vision; AI helps make it concrete, testable, and reproducible.

Without Claude and Copilot, this theory would still exist as scattered thoughts. With them, it has become 120+ formalized documents, 11/13 validated experiments, two independent gravity implementations, a working Java implementation, and the first falsifiable prediction distinguishing tick-frame from standard QM (interferometry without collapse). This collaboration demonstrates how AI can amplify human theoretical work without replacing human creativity.

**Acknowledgment:** This project would not have been possible in its current form without the assistance of Claude (Anthropic) and GitHub Copilot. They served as tireless partners in the work of bringing speculative ideas into rigorous form.
