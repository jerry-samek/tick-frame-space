# V3 Experiment Index

**Date:** March 19, 2026
**Status:** Current as of v24 Phase 2

---

## Purpose

This document catalogs all experiments with explicit substrate identification. It replaces the
V2 experiment index (`v2_archive/experiment_index.md`).

**Critical rule:** V2-substrate experiments (lattice, continuous field, Euclidean grid) do NOT
validate the V3 substrate (random geometric graph). They validate mechanisms that may transfer.
Each entry below states the substrate, not just the result.

---

## Substrate-Independent Results

These results depend on properties of discrete time or kinematic constraints, not on the
spatial substrate. They survive the V2-to-V3 transition without qualification.

---

### Exp #50: Dimensional Equivalence Rejection

- **Substrate:** Substrate-independent (discrete tick dynamics, tested across 1095 configurations)
- **Status:** Validated
- **Key result:** All (n+t) configurations show rho=2.0 (quadratic source scaling) vs rho~1.5 for pure spatial
  dimensions, proving time is NOT a spatial dimension.
- **V3 transfer:** Substrate-independent. The rho=2.0 signature is a property of discrete time itself, not of the
  spatial substrate. Validates Doc 49 (Temporal Ontology): time is primary substrate, space is emergent. Dimensional
  closure (4D-5D) refers to spatial dimensions only.
- **Reference:** `review/050_01_experimental_results_dimensional_equivalence_rejection.md`

---

### Exp #44_03: Rotation Asymmetry

- **Substrate:** Substrate-independent (kinematic constraint of discrete time)
- **Status:** Validated
- **Key result:** 933x rotation asymmetry between temporal-depth rendering axes, confirming time has fundamentally
  different kinematic properties than space.
- **V3 transfer:** Substrate-independent. Rotation asymmetry is a consequence of discrete tick updates, not spatial
  geometry. Applies equally on lattice, field, or graph substrates.
- **Reference:** `v2_archive/experiment_index.md` (Exp #44_03)

---

### Exp #44_05: O(n) Bucketing

- **Substrate:** Substrate-independent (discrete time rendering optimization)
- **Status:** Validated
- **Key result:** 2.78x speedup from O(n) bucketing that eliminates sorting in tick-frame rendering, confirming sorting
  is theoretically unnecessary.
- **V3 transfer:** Substrate-independent. Bucketing exploits the discrete tick structure, not the spatial substrate.
  Works on any discrete-time simulation.
- **Reference:** `raw/046_01_experimental_validation_bucketing_eliminates_sorting.md`

---

## V2-Substrate Results (Mechanism May Transfer)

These experiments were conducted on substrates that predate the V3 graph-first framework:
continuous reaction-diffusion fields, regular cubic lattices, or Euclidean grids. The V3
substrate is a random geometric graph with deposit chains. These are different substrates.

The mechanisms demonstrated here -- gradient-following, deposit-based attraction, collision
dynamics -- may transfer to the V3 graph substrate. In some cases partial transfer has already
been observed (gradient-following on graph: Exp #64_109 v21-v24). But "mechanism may transfer"
is not "validated on graph."

---

### Exp #15: Dimensional Sweep

- **Substrate:** Regular grid (Euclidean lattice, 1D-5D salience field dynamics)
- **Status:** Validated
- **Key result:** 3D achieves maximum SPBI=2.23 across 3,960 configurations. 4D-5D show diminishing returns (SPBI~2.0).
  Goldilocks zone confirmed at 3 spatial dimensions.
- **V3 transfer:** Mechanism may transfer. The 3D optimality result concerns dimensional scaling of salience fields, not
  the specific substrate. In V3, dimension is an observer property (RAW 110), not a substrate property -- the derivation
  path is different even if the conclusion (3D natural embedding) may survive.
- **Reference:** `experiments/15_minimal-model/v6-gpu/EXECUTIVE_SUMMARY.md`

---

### Exp #44: Lag-Based Rendering

- **Substrate:** 2D Euclidean grid + temporal lag as depth axis
- **Status:** Validated
- **Key result:** Temporal depth rendering produces 3D visualization from 2D space + time, with lag functioning as a
  genuine geometric axis.
- **V3 transfer:** Mechanism may transfer. Rendering uses lag-as-depth, which depends on discrete tick structure (
  substrate-independent) but was tested on a Euclidean grid. The lag principle survives; the specific grid geometry does
  not.
- **Reference:** `v2_archive/experiment_index.md` (Exp #44 series)

---

### Exp #51 v9: Time Dilation

- **Substrate:** Continuous reaction-diffusion field on a 2D grid
- **Status:** Validated
- **Key result:** Gravitational and special-relativistic time dilation reproduced simultaneously with r~0.999
  correlation between measured and predicted effective gamma.
- **V3 transfer:** Mechanism may transfer. The underlying mechanism (gradient-following produces effective time
  dilation) is general. The r~0.999 quantitative precision almost certainly will NOT transfer directly -- it depends on
  the smoothness of the continuous field, which the graph substrate lacks. The mechanism transfers; the precision is
  substrate-specific.
- **Reference:** V3_ch007 Section 1.1; `experiments/51_emergent_time_dilation/v9/`

---

### Exp #53 v10: Geodesic Orbits

- **Substrate:** Continuous reaction-diffusion field on a 2D grid
- **Status:** Validated
- **Key result:** 100% orbital completion -- all 18 entities achieved stable circular or elliptical orbits from
  gradient-following alone, no programmed force law.
- **V3 transfer:** Mechanism may transfer. The qualitative result (gradient-following produces orbits) is the strongest
  candidate for substrate transfer. Transfer to a cubic lattice was confirmed in Exp #64_109 v8-v10. Transfer to a
  random geometric graph is the current experimental frontier (Exp #64_109 v21-v24).
- **Reference:** V3_ch007 Section 1.2; `experiments/51_emergent_time_dilation/v10/`

---

### Exp #55: Collision Physics

- **Substrate:** Lattice substrate with discrete cell occupancy
- **Status:** Validated
- **Key result:** Three-regime collision framework (merge, explosion, excitation) validated. Emergent Pauli exclusion
  from cell occupancy limits -- no exclusion principle programmed.
- **V3 transfer:** Mechanism may transfer. Pauli exclusion emerged from cell occupancy constraints on a regular lattice.
  Whether the same exclusion emerges from node occupancy on a random graph has not been tested. The collision
  framework (energy-based regime selection) is substrate-independent; the specific exclusion mechanism is
  lattice-dependent.
- **Reference:** V3_ch007 Section 1.3

---

### Exp #56 v13: Jitter Stability

- **Substrate:** Lattice substrate
- **Status:** Validated
- **Key result:** ZPE-like jitter magnitude 0.119 is NOT a fundamental constant -- measured range [0.075, 0.5] across
  parameter space. Jitter scales with local field density, not fixed.
- **V3 transfer:** Mechanism may transfer. Jitter scaling with field density is a general property of discrete dynamics
  with noise floors. The specific magnitudes are lattice-dependent.
- **Reference:** `v2_archive/experiment_index.md` (Exp #56 v13)

---

### Exp #56 v17: Canvas Ontology

- **Substrate:** Lattice substrate
- **Status:** Validated
- **Key result:** O(entities) sparse storage confirmed -- gamma field acts as canvas, entities write to it. Memory
  scales with entity count, not substrate size.
- **V3 transfer:** Mechanism may transfer. The sparse storage principle (track entities, not substrate nodes) applies on
  any substrate. The specific implementation (lattice hash map) would need adaptation for a graph substrate.
- **Reference:** `v2_archive/experiment_index.md` (Exp #56 v17)

---

### Exp #62: Interferometry

- **Substrate:** Lattice substrate
- **Status:** Validated
- **Key result:** 26/26 tests passed. Gradual visibility emergence, NOT instantaneous collapse. Which-path information
  available WITHOUT destroying interference -- a falsifiable prediction against standard QM.
- **V3 transfer:** Mechanism may transfer. Interference via deposit addition/subtraction from overlapping paths is
  substrate-independent in principle. The specific lattice geometry affects path structure. Needs re-validation on
  graph.
- **Reference:** `v2_archive/experiment_index.md` (Exp #62)

---

### Exp #64_109 v1-v9: Graph-Lattice Gravity

- **Substrate:** Cubic lattice (3D, k=6 connectivity, integer gamma quanta)
- **Status:** Validated
- **Key result:** Integer gamma quanta on a cubic lattice produce attractive force with measured exponent ~1/r^2.2.
  Self-subtracting transport creates gradient. Three-body dynamics emerge. Hawking-like evaporation observed at small
  separations.
- **V3 transfer:** Mechanism may transfer. Deposit-gradient-following as gravity mechanism transfers directly -- this is
  the same mechanism used in v21-v24 on the random geometric graph. The force exponent (2.2 vs 2.0) may differ on a
  different substrate topology. The integer quanta model is closer to V3's intended substrate physics than the
  continuous field experiments.
- **Reference:** `docs/theory/raw/200_open_questions_experimental_status.md`;
  `experiments/64_109_three_body_tree/experiment_description.md`

---

## V3-Substrate Results (Current Frontier)

These experiments use a random geometric graph (RGG) substrate -- nodes embedded in 3D
Euclidean space, connected by k nearest neighbors, with no regular lattice structure. This is
the V3 substrate. All results here are on the actual V3 substrate.

The experimental arc progresses v21 -> v22 -> v23 -> v24, each building on the previous.
No closed orbit has been achieved. The architecture (leapfrog force, 3D displacement, local
hop threshold) is validated. The remaining problem as of v24 is force law behavior under
float gamma approximation.

---

### Exp #64_109 v21: Force-on-Hop

- **Substrate:** Random geometric graph (30k nodes, k=24, radius=30)
- **Status:** Exploratory (warm-up diagnostic)
- **Key result:** Validated force-on-hop architecture and eliminated velocity runaway from v18-v20. Discovered "frozen
  planet" problem: planet at r=8 fell to r=0.8 in 5000 ticks, only 3-5 hops per 5000 ticks due to connector projection
  blind spots.
- **V3 transfer:** This IS V3 substrate. Result is native.
- **What worked:** Force-on-hop removes per-tick velocity pumping. Velocity bounded (no runaway). Concept of emergent
  time dilation from hop interval validated in principle.
- **What failed:** Per-connector displacement projection causes blind spots. Fixed hop threshold becomes stale as graph
  expands. Planet effectively frozen.
- **Reference:** `experiments/64_109_three_body_tree/v21/experiment_description.md`

---

### Exp #64_109 v22: Leapfrog Force + 3D Displacement

- **Substrate:** Random geometric graph (30k nodes, k=24, radius=30)
- **Status:** Validated (architecture), not validated (closed orbit)
- **Key result:** First curved trajectories in the entire v21-v24 arc. Leapfrog force (every 10 ticks, decoupled from
  hops) + true 3D displacement accumulation. Best particle survived 16,041 ticks with velocity declining 28% (active
  gravitational deceleration). Star formation from seed and derived orbital velocity (v_circ=0.00396 from measured
  F_radial).
- **V3 transfer:** This IS V3 substrate. Result is native.
- **What worked:** Leapfrog gives ~60 force corrections per orbit vs ~20 with force-on-hop. True 3D displacement
  eliminates blind spots. Star formation from seed deposit established. Orbital velocity derived from field measurement,
  not guessed.
- **What failed:** Domain too small (radius=30). Orbit's natural radius exceeds graph boundary. Two bugs found and fixed
  mid-session (frozen hop threshold, unimplemented 3D displacement).
- **Discoveries:** Field self-pinning -- dense bodies resist expansion automatically via deposit density in growth
  denominator. This is emergent Hubble flow (galaxies don't expand, voids do).
- **Reference:** `experiments/64_109_three_body_tree/v22/experiment_description.md`

---

### Exp #64_109 v23: Larger Domain

- **Substrate:** Random geometric graph (80k nodes, k=24, radius=45)
- **Status:** Validated (radial dynamics), not validated (closed orbit)
- **Key result:** Radial reversal achieved (particle p8: r went 21.1 -> 17.1 -- first time a particle turned around and
  came back toward the star). Dissipative capture observed (particle p19: locked at r=25.9 for 27,000 consecutive ticks
  with |v|=0.00040). Five runs completed across stable/radiating star configurations.
- **V3 transfer:** This IS V3 substrate. Result is native.
- **What worked:** Larger domain eliminates boundary artifacts. All best-3 particles still bound at 60k ticks (Run C).
  Leapfrog force genuinely decelerates and curves trajectories. Stable star (no mass loss) eliminates late-run field
  decay.
- **What failed:** No closed orbit. No perihelion/aphelion oscillation. Gradient drops faster than 1/r^2 and cannot
  provide enough centripetal force at natural settling radii. Run C's equilibrium was dissipative capture (particle bled
  kinetic energy over 33k ticks of outward spiral), not orbital mechanics.
- **What it proved:** The remaining problem is force strength, not domain size or architecture.
- **Reference:** `experiments/64_109_three_body_tree/v23/experiment_description.md`

---

### Exp #64_109 v24: M=1M Star

- **Substrate:** Random geometric graph (80k nodes, k=24, radius=45)
- **Status:** In progress (Phase 2 running)
- **Key result:** Anti-Newtonian scaling discovered -- 10x heavier star produced 15x WEAKER force at r=8. This is a
  float gamma arithmetic artifact: more mass deposits more gamma uniformly, increasing the growth denominator
  everywhere, suppressing gradient asymmetry. In the true integer substrate (gamma in {0,1} per node), this pathological
  self-suppression cannot occur because the denominator is bounded at 2x maximum.
- **V3 transfer:** This IS V3 substrate. Result is native. The anti-Newtonian artifact is specific to the float
  approximation and does not invalidate the graph substrate itself.
- **What worked:** Internally consistent at the weaker force level (F_radial matches centripetal requirement for
  v_circ=0.00101). Phase 2 proceeding at derived velocity.
- **What failed:** Point-star + float gamma = pathological self-suppression of gradient. Force DECREASED with more mass.
- **Key insight:** The true integer substrate bounds gamma to {0,1} per node. The force law denominator maximum is 2x.
  The anti-Newtonian scaling is a float approximation artifact, not physics. A distributed star (body_radius=3-5) would
  eliminate the worst artifacts even in the float model.
- **v25 direction:** Distributed star eliminates point-star self-suppression. Integer gamma field is the correct
  theoretical direction but requires significant code changes.
- **Reference:** `experiments/64_109_three_body_tree/v24/experiment_description.md`;
  `experiments/64_109_three_body_tree/v24/results_phase1.md`

---

## Status Summary

| Category                 | Count | Examples                                                                                                                                                                                                            |
|--------------------------|-------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Substrate-independent    | 3     | rho=2.0 signature (#50), rotation asymmetry (#44_03), O(n) bucketing (#44_05)                                                                                                                                       |
| V2-substrate validated   | 9     | time dilation (#51), geodesic orbits (#53), collision/Pauli (#55), 3D optimality (#15), interferometry (#62), jitter (#56v13), canvas ontology (#56v17), lag rendering (#44), graph-lattice gravity (#64_109 v1-v9) |
| V3-substrate in progress | 4     | force-on-hop (v21), leapfrog+3D (v22), radial reversal (v23), anti-Newtonian artifact (v24)                                                                                                                         |
| Closed orbit achieved    | 0     | --                                                                                                                                                                                                                  |

---

## The Honest Gap

The V3 graph substrate has demonstrated:

- Star formation from seed deposit (v22 Phase 0)
- Gamma gradient at orbital radii (v22 Phase 1)
- Derived orbital velocity from field measurement (v22)
- Curved trajectories under gravitational force (v22)
- Active gravitational deceleration (v22, v23)
- Radial reversal (v23, particle p8)
- Dissipative radial capture (v23, particle p19)
- Anti-Newtonian scaling diagnosis (v24 -- float artifact, not physics)

The V3 graph substrate has NOT demonstrated:

- ~~Closed orbit (perihelion/aphelion oscillation)~~ ACHIEVED in ODE abstraction (Exp 128 v9, April 2026) but NOT on the graph itself
- 1/r^2 force law from deposit gradient on graph (measured as flux dilution, not as force)
- Quantitative time dilation from self-pinning
- Kepler's third law — ACHIEVED in ODE (T²∝r³ from F=-consumed/r²), not on graph
- Angular momentum conservation over multiple revolutions — ACHIEVED in ODE (1812 rev)
- Orbital stability for 10k+ ticks after first full cycle — ACHIEVED in ODE

The gap has shifted: from "curved trajectories → closed orbit" to
"graph deposit dynamics → 1/r² force law."

---

## Experiment 118: Consumption-Transformation Gravity (April 1-3, 2026)

**CLOSED.** 17 versions. Superseded by Experiment 128.

| Version | Key Result |
|---------|-----------|
| v1-v3 | Radial oscillation, compound extension runaway (1e28+) |
| v4 | Extension bug solved (linear growth). Weak routing (3.8x expansion) |
| v5 | Fixed-graph propagation engine. Wrong ontology (empty substrate) |
| v6 | Density routing saturates on finite graphs |
| v7 | **First "orbit"** with seeded kick. Time well (20:1 ratio). But v9 diagnostic proved it's a bound random walk |
| v8-v9 | Store/move partition barely engages. v9 diagnostic: all orbits = random walks |
| v10 | Aristotle's deadlock. Pure reactive entities freeze. |
| v11 | Newton I (forward default). No deadlock. Weak deflection. |
| v12 | **Same/Different rule.** Star expansion IS diffusion, not inflation. |
| v13 | Three mechanisms combined. g/f=63:1 but inverted gradient. |
| v14 | Star fills 73% of ANY graph (scale-invariant thermal equilibrium). |
| v15 | Propagating deposits saturate the graph. |
| v16 | **Consumption rule:** Same consumes Different. Connectors can shrink. |
| v17 | Inter-group rotation — groups too mixed for organized circulation. |

**Key findings:** Gravitational binding works. Coherent orbits don't emerge at N=80.
Star fills 73% of graph volume regardless of scale. Entity hopping on graphs
produces random walks, not orbits.

## Experiment 128: Energy Partition / Deposit Patterns (April 3-6, 2026)

**Current.** 10 versions. Supersedes Experiment 118.

| Version | Key Result |
|---------|-----------|
| v1 Phase 0 | 1D chain: consumption equilibrium at midpoint. No dilution in 1D. |
| v1 Phase 1 | **Deposit regions form from geometric dilution.** Mass = source count. |
| v1 Phase 2 | Pattern drift = gravitational attraction. Hand-coded momentum: coherence 0.44 (first >0.3 but not emergent). |
| v3 | 500k graph, 10k star, 5 planet. Probability cloud. Ejection event. Binding survives. |
| v4/v5 | 500 planet nodes. Vectorized (535 t/s, 38x speedup). Planet merges with star. |
| v6 | **Deposit dominance tracking.** Regions at dist=12.2 (stable equilibrium!). |
| v7 | Tangential velocity bias: one-time 25-degree deflection, dies at equilibrium. |
| v8 | Tangential acceleration: noisy oscillation. |
| v9 ODE | **Keplerian orbits from F=-consumed/r².** 1812 revolutions. Kepler I, II, III. |
| v10 | Consumption IS movement. Minimal orbit: perfect circles. Newton renamed. |

**Key findings:**
- Radial equilibrium from consumption (deposit distance 12.2, stable)
- Entities ARE deposit dominance regions, not objects at nodes
- Consumption IS centripetal force → Kepler's laws (RAW 130)
- GM = L × R / 4π (star emission × planet resistance / geometry)
- **Gap: graph → 1/r² force not yet derived from graph dynamics**

## Key RAW Documents (April 2026)

- **RAW 128:** Energy Partition — Store, Move, or Radiate
- **RAW 129:** Experimental Connections — Breit-Wheeler, quantum batteries, CME, planetary structure
- **RAW 130:** It Rotates Because It Consumes — orbital mechanics from consumption

---

*Date: March 19, 2026 (initial), April 6, 2026 (updated with Exp 118 + 128)*
*Next: prove graph → 1/r² force law (mathematical, not simulation?)*
