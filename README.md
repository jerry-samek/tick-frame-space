# Tick-Frame Space
*Coherence over Orthodoxy: a model is valid if it is internally consistent, falsifiable, and explanatory, regardless of its alignment with current physical dogma.*

A speculative discrete physics model exploring whether a single operation on a raw graph can produce everything we observe. My pet project on "garden leave." Don't take it too seriously, but feel free to correct me if I'm wrong (I definitely am). I'm an engineer, not a scientist. And I have plenty of spare memory-time to just think about crazy stuff.

## What This Is

An exploration of a universe built from one operation:

> **An entity deposits on a connector, hops, and the connector extends.**

From this, iterated across all entities at every tick:
- **Gravity** emerges from connector asymmetry (entities follow familiar paths)
- **Radiation** emerges from divergence propagating through the graph
- **Expansion** emerges from accumulated connector extension
- **Time** is branch depth (append-only, irreversible)
- **Space** is connections (geometry is observer-reconstructed)
- **Dimensions** are observer properties (3D from ternary change geometry)

Everything is deterministic at the substrate layer. No randomness, no infinity, no continuum.

### The Three States

Every interaction reduces to one of three comparison outcomes:

| State | Physics | Information |
|-------|---------|-------------|
| **Same** | Gravity — follow familiarity | Retrieval — no new structure |
| **Different** | Radiation — record divergence | Information — branch point |
| **Unknown** | Expansion — write the frontier | Learning — new structure |

No fourth state exists. These three exhaust all possible relationships between an arriving pattern and existing deposits.

---

## Quick Start

### Java Substrate Simulation

The **tick-space-runner** module implements an earlier version of the model (Chapter 15 basis).

```bash
mvn clean package
mvn exec:java -pl tick-space-runner -Dexec.mainClass="eu.jerrysamek.tickspace.runner.LocalApp"
```

Output: JSON snapshots to `W:\data\snapshots\` every 1000 ticks.

**Note:** The Java implementation predates the graph-first paradigm shift. It uses a geometric lattice substrate. The current theoretical frontier uses Python experiments on random geometric graphs.

### Python Experiments (Current Frontier)

The orbital mechanics experiments (v21-v24) are the active development area:

```bash
# Run the latest experiment (v24)
cd experiments/64_109_three_body_tree
python -u v24/star_formation.py --measure-force --weighted-spread --no-mass-loss

# Analyze snapshots from Java simulation
python scripts/snapshot-stats.py W:\data\snapshots\time-frame.5000.json
```

### Analysis Tools

| Script | Purpose |
|--------|---------|
| `scripts/snapshot-stats.py` | Shell-wise statistics (Manhattan distance) |
| `scripts/snapshot-visualization.py` | 3D scatter plots colored by energy |
| `scripts/snapshot-energy-histogram.py` | Energy distribution and radial density |

---

## Theory Documentation (V3 — March 2026)

The theory has gone through three versions. **V3 is current** — a graph-first framework where geometry is emergent.

### V3 Chapters

| Chapter | Topic | Status |
|---------|-------|--------|
| [V3 README](docs/theory/V3_README.md) | Entry point, reading paths | Current |
| [Ch1 The Graph Substrate](docs/theory/V3_ch001_the_graph_substrate.md) | Physical foundation: nodes, deposit chains, single mechanism | Core theory |
| [Ch2 Three States](docs/theory/V3_ch002_three_states.md) | Same/Different/Unknown — the complete physical alphabet | Core theory |
| [Ch3 Emergent Geometry](docs/theory/V3_ch003_emergent_geometry.md) | Latency matrix, local dimensionality, self-pinning | Core theory |
| [Ch4 Time and Depth](docs/theory/V3_ch004_time_and_depth.md) | Branch depth, arrow of time, rho=2.0, simulation argument | Core theory |
| [Ch5 Information and Trie](docs/theory/V3_ch005_information_and_trie.md) | Trie structure, compression, particle identity | Extension |
| [Ch6 Observer and Consciousness](docs/theory/V3_ch006_observer_and_consciousness.md) | Trie traversal, memory, sleep, snapshots | Speculative |
| [Ch7 Experimental Status](docs/theory/V3_ch007_experimental_status.md) | Honest assessment — what's proven, what's not | Critical |
| [Ch8 Open Questions](docs/theory/V3_ch008_open_questions.md) | 12 priority questions with falsification criteria | Active |
| [Glossary](docs/theory/V3_glossary.md) | 34 V3-era definitions | Reference |
| [Experiment Index](docs/theory/V3_experiment_index.md) | 16 experiments with substrate identification | Reference |

### Reading Paths

- **Physicists:** Ch1 (Graph Substrate) -> Ch2 (Three States) -> Ch7 (Experimental Status)
- **Computer scientists:** Ch5 (Trie) -> Ch1 -> Ch2
- **Skeptics:** Ch7 (what's actually proven) -> Ch8 (what's not)
- **Quick overview:** V3 README -> Ch7

### Previous Versions

- **V2** (January-February 2026): Geometric lattice substrate. 13 chapters. Archived in `docs/theory/v2_archive/`
- **V1** (2025-January 2026): 76 raw documents. Triage into `docs/theory/raw/`, `archive/`, `review/`

### Raw Theory Documents

120+ documents in `docs/theory/raw/`. The current frontier documents:

| Document | Title |
|----------|-------|
| RAW 112 | The Single Mechanism — one operation, all physics |
| RAW 113 | Semantic Isomorphism — same/different/unknown |
| RAW 111 | Space Is Connections |
| RAW 110 | Local Dimensionality |
| RAW 114-117 | Particle identity, rendering, single entity, origin event |

---

## Experiments

### Current Frontier: Orbital Mechanics on Graph (Exp 64_109)

The active experiment arc, running on random geometric graphs with the graph-first substrate:

| Version | What It Tested | Key Result |
|---------|---------------|------------|
| v21 | Force-on-hop, warm-up | Frozen planet bug, bootstrap deadlock |
| v22 | Leapfrog force, 3D displacement | First curved trajectories (best particle survived 16k ticks) |
| v23 | Larger domain (80k nodes) | Radial reversal (p8: r=21->17), velocity equilibrium (p19: locked 27k ticks) |
| v24 | Heavier star (M=1M) | Anti-Newtonian scaling discovered (float artifact) |

**Status:** Curved trajectories and velocity stabilization achieved. Closed orbit not yet achieved.

### Validated Results (V2-Substrate)

These used lattice/field substrates. Mechanisms may transfer to graph:

| Experiment | Result | Substrate |
|-----------|--------|-----------|
| Exp #15 | 3D optimality (SPBI=2.23), 3,960 sims | Regular grid |
| Exp #50 | rho=2.0 — time is not a dimension (1,095 configs) | **Substrate-independent** |
| Exp #44 | Rotation asymmetry 933x, O(n) bucketing | **Substrate-independent** |
| Exp #51 v9 | Time dilation r=0.999 | Continuous field |
| Exp #53 v10 | Geodesic orbits 100% | Continuous field |
| Exp #55 | Collision physics, emergent Pauli exclusion | Lattice |
| Exp #62 | Interferometry without collapse (falsifiable!) | Lattice |
| Exp #64_109 v1-v9 | Graph-lattice gravity, Hawking evaporation | Cubic lattice |

---

## Scientific Status (March 2026)

### What Has Been Demonstrated

On **graph substrate** (V3, random geometric graph):
- Star formation gradient from seed deposit
- Force measurement and derived orbital velocity
- Curved trajectories under gravitational force (first time in experiment arc)
- Radial reversal (particle changed direction)
- Velocity stabilization (equilibrium found)
- Self-pinning: dense bodies resist expansion automatically

On **lattice/field substrates** (V2, mechanism may transfer):
- Time dilation r=0.999 (Exp #51)
- Geodesic orbits from time gradients, no force laws (Exp #53)
- Collision physics with emergent Pauli exclusion (Exp #55)
- Two independent gravity implementations converge (Exp #51 + #64_109)

**Substrate-independent** (survives any substrate):
- rho=2.0 proves time is categorically different from spatial dimensions (Exp #50)
- Rotation asymmetry 933x (Exp #44)
- O(n) rendering from discrete time (Exp #44)

### What Has NOT Been Demonstrated

- Closed orbit (perihelion/aphelion oscillation)
- 1/r^2 force law from deposit gradient
- Three-state alphabet as observable physical states
- Photon properties from path geometry
- Time dilation from branch depth accumulation
- The single mechanism itself (simulation uses float approximation)
- Any connection to real-world experimental physics

### Honest Summary

> The graph-first framework is theoretically coherent and internally consistent.
> It has produced correct qualitative behavior in orbital experiments (curved trajectories,
> radial reversal, velocity stabilization). Quantitative validation of the core claims
> (closed orbit, force law, time dilation from depth) is in progress but not achieved.

See [V3_ch007](docs/theory/V3_ch007_experimental_status.md) for the full honest assessment.

---

## Project Structure

```
tick-frame-space/
  tick-space-runner/        Java substrate simulation (Chapter 15 model)
  scripts/                  Python analysis tools for JSON snapshots
  experiments/              All experiments (15 series through 64_109)
    64_109_three_body_tree/ Current frontier (v21-v24)
  docs/
    theory/
      V3_*.md               Current theory (V3, graph-first)
      raw/                  120+ raw theory documents
      archive/              Superseded geometric-era documents
      review/               Transitional documents needing audit
      v2_archive/           V2 consolidated chapters (January 2026)
      final/                Early consolidation attempt
    model/                  Implementation documentation
    plans/                  Development plans
  model/                    Model definitions
```

---

## AI-Assisted Development

This project uses AI as a tool for materialization, not invention. The theory originates from human thought during garden leave. AI helps make it concrete:

- **Claude (Anthropic)** — Theory formalization, experimental design, code implementation, cross-consistency verification
- **GitHub Copilot** — Code completion, refactoring support

The human provides the vision; AI helps test it. Without Claude, this would be scattered thoughts. With it: 120+ documents, a working Java simulation, Python experiment arc reaching curved trajectories on random graphs, and V3 consolidated theory.

**Speculation disclaimer:** This is a speculative computational model exploring discrete physics. Significant computational progress has been made, but no real-world experimental validation exists yet. The interferometry prediction (Exp #62 — which-path detection without destroying interference) remains the first testable difference from standard QM.
