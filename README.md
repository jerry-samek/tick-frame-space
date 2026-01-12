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

The **tick-space-runner** module contains the operational Java (26) implementation of tick-frame physics.

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

**Phase 8 (Physical Formalization):** COMPLETED (2026-01)
**Phase 9 (Integration & Synthesis):** IN PROGRESS

**Theory achievements:**
- ✅ **48 theoretical documents** covering foundation through physical formalization
- ✅ **Complete axiomatic system** at Planck scale (Docs 47-48)
- ✅ **Observer cognitive model** explaining memory, consciousness, trauma, déjà vu, dreams, death
- ✅ **Experimental validation** (3,960 dimensional simulations, 99.9% success rate)
- ✅ **Dimensional phase transition** discovered at d=3
- ✅ **3D optimality validated** (SPBI = 2.23, minimal sufficient dimension)
- ✅ **Void asymmetry** explains matter-antimatter surplus from symmetric rules
- ✅ **Rendering theory** validated (O(n) temporal bucketing eliminates sorting)
- ✅ **Free will & consciousness** formalized (bounded operator manipulation)

**Implementation observations:**
- ✅ Entities exhibit temporal surfing behavior
- ✅ Collision patterns create composite structures
- ✅ Expansion follows dimensional growth rules
- ⚠️ Over-coherence: structures too uniform (anisotropy deficit)
- ⚠️ Collision dynamics tuning needed (persistence vs. dissolution balance)

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

### Theory (48 Documents)

- **Foundation & Overview**
    - [00 Meta-Critical Theory Development Log](docs/theory/00%20Meta-Critical%20Theory%20Development%20Log.md) - Complete development history through Phase 8
    - [97 Meta-Critical Theory — Integrated Spec](docs/theory/97%20Meta-Critical%20Theory%20—%20Integrated%20Spec.md) - Comprehensive integration
    - [99 Closure Improvement Plan](docs/theory/99%20Closure%20Improvement%20Plan.md) - Development roadmap and status
    - [Theory README](docs/theory/README.md) - Full index of all 48 documents

- **Physical Formalization**
    - [47 Tick‑Frame Universe - Physical Formalization](docs/theory/47%20Tick‑Frame%20Universe%20-%20Physical%20Formalization.md) - Complete axiomatic system at Planck scale
    - [48 Observer Model in the Tick‑Frame Universe](docs/theory/48%20Observer%20Model%20in%20the%20Tick‑Frame%20Universe.md) - Cognitive formalization: identity, memory, dreams, death

- **Key Principles**
    - [49 Temporal Ontology of the Tick-Frame Universe](docs/theory/49%20Temporal%20Ontology%20of%20the%20Tick‑Frame%20Universe.md) - Unified framework: temporal primacy, absolute tick-stream, emergent space
    - [28 Temporal Surfing Principle](docs/theory/28%20Temporal%20Surfing%20Principle.md) - Persistence through continual renewal
    - [30 Collision Persistence Principle](docs/theory/30%20Collision%20Persistence%20Principle%20in%20Tick-Frame.md) - Entities as collision patterns
    - [37 Observer‑Relative Big Bang Principle](docs/theory/37%20Observer‑Relative%20Big%20Bang%20Principle.md) - Big Bang as observer event
    - [40 Dimension Definition in Tick‑Frame Space](docs/theory/40%20Dimension%20Definition%20in%20Tick‑Frame%20Space.md) - Dimension as observer property
    - [43 Void Asymmetry Principle](docs/theory/43%20Void%20Asymmetry%20Principle.md) - Matter surplus via void stabilization
    - [44 Fallible Commit Principle](docs/theory/44%20Fallible%20Commit%20Principle.md) - Irreversible decisions with inherent lag

### Model & Implementation

- [Computational Gravity Model](docs/model/01%20Computational%20Gravity%20-%20A%20Physics-Inspired%20Model%20for%20Tick-Based%20Resource%20Allocation.md)
- [Rendering Pipeline](docs/model/03%20Rendering%20pipeline.md)
- [Tick‑Frame Engine Documentation](docs/model/04%20Tick‑Frame%20Engine%20Documentation.md)

### Experimental Validation (3,960 Simulations)

- [SPBI Executive Summary](experiments/15_minimal-model/v6-gpu/SPBI_EXECUTIVE_SUMMARY.md) - 3D optimality validation
- [SPBI Analysis Report](experiments/15_minimal-model/v6-gpu/SPBI_ANALYSIS_REPORT.md) - Dimensional scaling analysis
- [Validation Summary](experiments/15_minimal-model/v6-gpu/VALIDATION_SUMMARY.md) - Hypothesis testing results
- [Theoretical Implications](experiments/15_minimal-model/v6-gpu/THEORETICAL_IMPLICATIONS.md) - Impact on foundation theory
- [5D Analysis Summary](experiments/15_minimal-model/v6-gpu/5D_ANALYSIS_SUMMARY.md) - High-dimensional behavior

---

## 🧪 Experiments

- **v6-gpu: Dimensional Sweeps**
    - [1D](experiments/15_minimal-model/v6-gpu/v6_gpu_1d.py)
    - [2D](experiments/15_minimal-model/v6-gpu/v6_gpu_2d.py)
    - [3D](experiments/15_minimal-model/v6-gpu/v6_gpu_3d.py)
    - [4D](experiments/15_minimal-model/v6-gpu/v6_gpu_4d.py)
    - [5D](experiments/15_minimal-model/v6-gpu/v6_gpu_5d.py)

- **v7: Focused Saturation & Analysis**
    - [Saturation 3D](experiments/15_minimal-model/v7/v7a_saturation_3d.py)
    - [Saturation 4D](experiments/15_minimal-model/v7/v7a_saturation_4d.py)
    - [Saturation 5D](experiments/15_minimal-model/v7/v7a_saturation_5d.py)
    - [Normalized Analysis](experiments/15_minimal-model/v7/v7b_normalized_analysis.py)
    - [Causal Comparison](experiments/15_minimal-model/v7/v7c_causal_comparison.py)

- **v7-final: Goldilocks Zone & LHB Validation**
    - [3D](experiments/15_minimal-model/v7-final/v7_final_3d.py)
    - [4D](experiments/15_minimal-model/v7-final/v7_final_4d.py)
    - [5D](experiments/15_minimal-model/v7-final/v7_final_5d.py)
    - [Experiment Plan](experiments/15_minimal-model/v7-final/Experiment%20Plan%20-%20SPBI%20and%20LHB%20validation.md)

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

**Theory Development:** 48 documents spanning foundation to complete physical formalization

**Experimental Validation:**
- **3,960 simulations** across 1D-5D dimensions (99.9% success rate)
- **Dimensional phase transition** discovered at d=3
- **3D optimality validated** via SPBI framework (minimal sufficient dimension)
- **Rendering theory validated** (O(n) temporal bucketing experimentally confirmed)
- **45% hypothesis validation rate** with falsification leading to theory refinement

**Key Scientific Contributions:**
- **Void Asymmetry Principle:** Matter-antimatter asymmetry arises from ternary state stabilization ({-1, 0, +1}), not CP violation. Symmetric rules yield asymmetric outcomes.
- **Observer-Relative Cosmology:** Big Bang, dimensions, and multiverse are observer properties, not substrate events.
- **Dimensional Determinism Emergence:** Probabilistic behavior decreases exponentially with dimension: CV(d) ≈ 80% × exp(-0.82×d). Free will perception may be dimensional artifact.
- **Consciousness from Tick One:** Consciousness fundamental, not emergent. Free will = bounded operator manipulation at commit points.
- **Memory as Indexing:** Brain is indexing mechanism, not storage device. Explains trauma (high indexing priority), déjà vu (index collision), dreams (non-causal traversal).

**Computational Insights:**
- **Planck-scale observer cost:** 10⁴⁹-10⁵⁵ ops/s
- **Earth's capacity:** 10²² ops/s (gap of 10⁻²⁷ to 10⁻³³)
- **Implication:** Compression essential; Planck-scale simulation computationally extreme

**Defined Limitations:**
1. Quantum-classical correspondence conceptually mapped but not mathematically rigorous
2. Lorentz invariance recovery not yet demonstrated
3. Matter emergence mechanism (void asymmetry) lacks defined dynamics
4. Consciousness predictions testable in principle but not yet empirically validated

⚠️ **Speculation disclaimer:** This is a speculative computational model exploring discrete physics. Physics parallels are exploratory and falsifiable, not predictive of experimental outcomes without further validation.

---

## 📝 Further Reading

### Quick Start Paths

1. **Theory Overview:** Start with [00 Meta-Critical Theory Development Log](docs/theory/00%20Meta-Critical%20Theory%20Development%20Log.md) for complete history
2. **Physical Formalization:** Jump to [47 Tick‑Frame Universe](docs/theory/47%20Tick‑Frame%20Universe%20-%20Physical%20Formalization.md) and [48 Observer Model](docs/theory/48%20Observer%20Model%20in%20the%20Tick‑Frame%20Universe.md)
3. **Experimental Validation:** See [SPBI Executive Summary](experiments/15_minimal-model/v6-gpu/SPBI_EXECUTIVE_SUMMARY.md) for dimensional optimality results
4. **Implementation:** Read [Tick‑Frame Engine Documentation](docs/model/04%20Tick‑Frame%20Engine%20Documentation.md)
5. **Integrated Spec:** Review [97 Meta-Critical Theory — Integrated Spec](docs/theory/97%20Meta-Critical%20Theory%20—%20Integrated%20Spec.md)

### All 48 Theory Documents

See [docs/theory/README.md](docs/theory/README.md) for complete index organized by topic:
- Foundation (Docs 01-08)
- Core Equations (Docs 09-15)
- Physical Quantities (Docs 16-25)
- Collision Theory (Docs 26-30)
- Energy & Conservation (Docs 31-34)
- Observer Cosmology (Docs 35-38)
- Ternary Logic (Docs 39-43)
- Free Will & Consciousness (Doc 44)
- Rendering Theory (Docs 45-46)
- Physical Formalization (Docs 47-48)
- Meta-Documents (Docs 97-99)

---

## 🤖 AI-Assisted Development

This project represents a novel approach to theoretical physics development: **AI as a tool for materialization, not invention.**

**The theory itself** — the core ideas, principles, and conceptual framework — **originates from human thought** during a period of "garden leave" exploration. The tick-frame universe, discrete time substrate, collision persistence, void asymmetry, and observer-relative cosmology are all products of human speculation and insight.

**AI's role** has been to help **materialize** these ideas:
- **Claude (Anthropic)** - Theory formalization, mathematical expression, documentation synthesis, experimental design, cross-consistency verification
- **GitHub Copilot** - Code implementation, Java substrate development, pattern completion, refactoring support

**This distinction matters:** AI is being used as an advanced tool for expression and implementation — much like using LaTeX for typesetting or MATLAB for simulations — not as the source of theoretical creativity. The human provides the vision; AI helps make it concrete, testable, and reproducible.

Without Claude and Copilot, this theory would still exist as scattered thoughts. With them, it has become 48 formalized documents, 3,960 validation experiments, a working Java implementation, and a falsifiable framework. This collaboration demonstrates how AI can amplify human theoretical work without replacing human creativity.

**Acknowledgment:** This project would not have been possible in its current form without the assistance of Claude (Anthropic) and GitHub Copilot. They served as tireless partners in the work of bringing speculative ideas into rigorous form.
