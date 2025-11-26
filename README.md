# Tick-Frame Space: Dimensional Physics Experiments

Welcome to the Tick-Frame Space project. My pet project on "garden leave." This repository contains a "working" **Java substrate model**, theoretical documentation, and experimental validation of discrete tick-frame physics. However, don't take it too seriously and feel free to correct me if I'm wrong (I definitely am). I'm an engineer, not a scientist. And I have plenty of spare memory-time to just think about crazy stuff.

## Overview

This is an exploration of how far the current Java can be pushed before collapsing, while testing a speculative physics model where:
- **Time is discrete** (advances in ticks, not continuous flow)
- **Space expands** with each tick following dimensional growth rules
- **Entities are collision patterns** that persist through temporal renewal
- **Everything is deterministic** at the substrate layer (no randomness, no infinity)
- **Everything is natural numbers** (BigInteger) - no fractions allowed
- **Energy is a function of time** (linear, not conserved from initial state)

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

The **tick-space-runner** module contains the operational Java implementation of tick-frame physics.

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

The substrate model implements these theoretical principles:

- **Temporal Surfing Principle** (Doc 28) - entities persist through continual renewal
- **Collision Persistence Principle** (Doc 30) - particles as collision patterns
- **Imbalance Theory** (Doc 29) - matter-antimatter asymmetry from expansion geometry
- **Horizon Boundaries** (Doc 26) - observable limits in causal cones

### Current Status

**Phase 7 (Operational Substrate):** IN PROGRESS

**Observations:**
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

- **Theory & Model**
    - [Computational Gravity Model](docs/model/01%20Computational%20Gravity%20-%20A%20Physics-Inspired%20Model%20for%20Tick-Based%20Resource%20Allocation.md)
    - [Rendering Pipeline](docs/model/03%20Rendering%20pipeline.md)
    - [Tick‑Frame Engine Documentation](docs/model/04%20Tick‑Frame%20Engine%20Documentation.md)
    - [Meta-Critical Theory Log](docs/theory/00%20Meta-Critical%20Theory%20Development%20Log.md)

- **Experiment Analysis & Validation**
    - [SPBI Executive Summary](experiments/15_minimal-model/v6-gpu/SPBI_EXECUTIVE_SUMMARY.md)
    - [SPBI Analysis Report](experiments/15_minimal-model/v6-gpu/SPBI_ANALYSIS_REPORT.md)
    - [Validation Summary](experiments/15_minimal-model/v6-gpu/VALIDATION_SUMMARY.md)
    - [Theoretical Implications](experiments/15_minimal-model/v6-gpu/THEORETICAL_IMPLICATIONS.md)
    - [5D Analysis Summary](experiments/15_minimal-model/v6-gpu/5D_ANALYSIS_SUMMARY.md)

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

## Scientific Note (Optional)

While primarily a modeling framework, the tick‑frame universe can be read as a speculative physics analogy:
- **Matter–antimatter asymmetry:** Structural necessity of expansion.
- **Energy distribution:** Emerges as a function of time, always less than 100% after expansion.
- **Edge generation:** Even if energy appears at boundaries, imbalance persists due to parity constraints.

⚠️ **Speculation disclaimer:** The model does not define matter emergence. Physics parallels are exploratory, not predictive.

---

## 📝 Further Reading

- [Tick‑Frame Engine Documentation](docs/model/04%20Tick‑Frame%20Engine%20Documentation.md)
- [Meta-Critical Theory Log](docs/theory/00%20Meta-Critical%20Theory%20Development%20Log.md)
- [SPBI Test Framework](experiments/15_minimal-model/v7/Stability–Probability%20Balance%20Test%20Framework.md)
