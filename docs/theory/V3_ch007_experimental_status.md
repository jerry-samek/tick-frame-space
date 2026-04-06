# Chapter 7: Experimental Status

---

## Abstract

This chapter is a status report, not a validation claim. It catalogues every experimental result
that bears on the tick-frame framework, identifies which substrate each experiment used, and states
plainly what has been demonstrated and what has not. The central distinction throughout is between
results obtained on V2-era substrates (continuous reaction-diffusion fields, regular cubic lattices,
Euclidean grids) and results obtained on the V3 substrate (random geometric graph with deposit
chains). These are different substrates. A mechanism that works on one does not automatically
transfer to the other. Where transfer is plausible, we say so. Where it has not been tested, we
say that instead.

As of March 19, 2026, the V3 graph substrate has produced curved trajectories, radial reversal,
velocity stabilization, and star formation from seed deposits. It has not produced a closed orbit,
a measured 1/r^2 force law, or quantitative time dilation from self-pinning. The gap between what
the theory claims and what experiments have shown is significant. This chapter maps that gap
precisely.

---

## 1. V2-Substrate Validated Results

The results in this section were obtained on substrates that predate the V3 graph-first framework.
Each used a different computational substrate: continuous reaction-diffusion fields, regular cubic
lattices, or Euclidean grids. The V3 theory proposes a raw graph with no intrinsic geometry as the
physical substrate. These are not the same thing.

The mechanisms demonstrated in V2 experiments -- gradient-following, deposit-based attraction,
discrete-tick dynamics -- may transfer to the V3 graph substrate. In several cases, the results
concern properties of discrete time itself and are plausibly substrate-independent. But
"plausibly transfers" is not "validated on graph." This section is explicit about that
distinction for every result.

### 1.1 Time Dilation from Gradient Following

**Experiment:** #51, version 9 (January 2026)
**Substrate:** Continuous reaction-diffusion field on a 2D grid
**Reference:** `experiments/51_emergent_time_dilation/v9/RESULTS.md`

**What was demonstrated:**

- Gravitational time dilation and special-relativistic time dilation reproduced simultaneously
  in a multi-entity system
- Correlation between measured and predicted effective gamma: r = 0.999
- Combined effects obey the multiplicative rule: gamma_total = gamma_grav x gamma_SR, with
  error below 10% for entities at velocities up to 0.9c
- 100% validation rate at 0.1c and 0.5c; ~90% at 0.9c; ~30% at 0.99c
- Stable gravitational gradient confirmed (monotonic decrease with distance from cluster)

**What was not demonstrated:**

- Emergent trajectories. All orbits in v9 were forced circular trajectories, not self-organizing.
  The field remained stable under these forced conditions, but the experiment did not show that
  entities would naturally orbit.
- The result was specific to a continuous field substrate with smooth gradients. The V3 graph
  substrate has discrete, irregular connectivity. Whether the r = 0.999 correlation holds on a
  random geometric graph has not been tested.

**Transfer assessment:** The underlying mechanism (gradient-following produces effective time
dilation) is general enough that it should survive substrate changes. The quantitative precision
(r = 0.999) almost certainly will not transfer directly -- it depends on the smoothness of the
continuous field, which the graph substrate lacks. The mechanism may transfer; the precision is
substrate-specific.

### 1.2 Geodesic Orbits from Gradient Following

**Experiment:** #53, version 10 (January 2026)
**Substrate:** Continuous reaction-diffusion field on a 2D grid
**Reference:** `experiments/51_emergent_time_dilation/v10/RESULTS.md`

**What was demonstrated:**

- 100% orbital completion: all 18 entities achieved stable circular or elliptical orbits
- Orbits emerged from gradient-following alone, with no programmed force law or trajectory
  constraints
- 14 entities (78%) in near-circular orbits with eccentricity below 0.1
- 4 entities (22%) in stable elliptical orbits with eccentricity 0.26-0.37
- Zero collapses, zero escapes

**What was not demonstrated:**

- Long-term orbital stability. The simulation ran for 5000 ticks. Whether orbits remain stable
  over 100,000+ ticks is unknown.
- The acceleration rule was `acceleration = k * grad(gamma_grav)`, applied on a smooth continuous
  field. On the V3 graph substrate, the gradient is noisy, sparse, and has no continuous Euclidean
  embedding. This specific result has not been replicated on a graph.

**Transfer assessment:** The qualitative result (gradient-following produces orbits) is the
strongest candidate for substrate transfer, because it depends on the existence of a field
gradient, not on the specific substrate topology. The Exp #64_109 lattice gravity experiments
(Section 1.8) confirm this transfer to a cubic lattice. Transfer to a random geometric graph
is the current experimental frontier (Section 2).

### 1.3 Collision Physics and Emergent Pauli Exclusion

**Experiment:** #55 (January 2026)
**Substrate:** Lattice substrate with discrete cell occupancy
**Reference:** `experiments/55_collision_physics/VALIDATION_RESULTS.md`

**What was demonstrated:**

- Three-regime collision framework validated: merge, explosion, excitation
- Energy conservation exact in merge and excitation regimes
- Matter-antimatter annihilation producing photon pairs with shockwave
- Fusion reactions producing composite objects (deuterium, hydrogen)
- Pauli exclusion emerged from cell capacity limits -- not programmed, not anticipated
- All validation criteria met

**What was not demonstrated:**

- The collision dynamics were tested on a lattice substrate with discrete cell occupancy limits.
  The V3 graph substrate does not have fixed cell capacity -- nodes are points in a random
  geometric graph with variable connectivity. Whether Pauli exclusion still emerges when cells
  are replaced by graph nodes of variable degree is an open question.
- Pattern types (electron, proton, photon) were explicitly defined. The V3 theory claims these
  should emerge from the three-state alphabet (same/different/unknown). This emergence has not
  been demonstrated.

**Transfer assessment:** The collision dynamics (merge, explosion, excitation) depend on energy
accounting and overlap computation, which are substrate-independent mechanisms. Pauli exclusion
depends on occupancy limits, which are lattice-specific. The mechanism of occupancy limits
plausibly has a graph analog (node deposit saturation), but this has not been tested.

### 1.4 Three-Dimensional Optimality

**Experiment:** #15, version 6-gpu (January 2026)
**Substrate:** Regular grid substrate, 1D through 5D
**Reference:** `experiments/15_minimal-model/v6-gpu/`

**What was demonstrated:**

- 3,960 simulations across 1D, 2D, 3D, 4D, and 5D grid substrates
- 3D achieved optimal balance: SPBI (Stability-Probability Balance Index) = 2.23
- 3D showed lowest coefficient of variation: CV = 5.3%
- 4D showed secondary stability peak
- 1D and 2D showed fundamental instability
- 5D showed saturation effects

**What was not demonstrated:**

- The "3D optimality" result was measured on regular Euclidean grids with uniform connectivity.
  The V3 theory claims dimension is an observer property of a raw graph with no intrinsic
  dimension. Whether random geometric graphs produce optimal behavior at any embedding dimension
  has not been tested.
- The SPBI metric measures stability of a salience field under spreading rules. Whether this
  metric captures physical stability on a graph substrate is assumed but not verified.

**Transfer assessment:** The result that 3-4 spatial dimensions produce optimal stability is
likely a property of connectivity degree and spreading dynamics, not of the specific Euclidean
grid structure. The V3 framework predicts that random geometric graphs with k=24 connectivity
produce effective 3D embedding. This prediction has not been quantitatively tested against the
SPBI metric.

### 1.5 Dimensional Equivalence Rejection

**Experiment:** #50 (January 2026)
**Substrate:** Grid substrate with explicit time dimension variants
**Reference:** `experiments/50_dimensional_equivalence_explicit_time/EXPERIMENT_RESULTS.md`

**What was demonstrated:**

- 1,095 configurations tested across (2D+t, 3D+t, 4D+t) and baseline (3D, 4D, 5D)
- Hypothesis that (n spatial + time) behaves like (n+1 spatial) was decisively rejected: 0/6
  tests passed
- All (n+t) systems showed quadratic source scaling (rho = 2.0) versus sub-quadratic scaling
  (rho approximately 1.5) in pure spatial dimensions
- Time exhibited qualitatively different behavior from spatial dimensions: extreme salience
  amplification, commit saturation, and different scaling laws

**Transfer assessment:** This result is substrate-independent. It concerns the mathematical
properties of an accumulative generator (time) versus spatial generators (dimensions). The
conclusion -- that time is not a spatial dimension -- holds regardless of whether the substrate
is a grid, a lattice, or a random graph. This is one of the few V2 results that transfers
directly to V3 without qualification.

### 1.6 Rotation Asymmetry

**Experiment:** #44_03 (January 2026)
**Substrate:** Tick-frame with temporal lag model
**Reference:** `experiments/44_03_emergent_rotation/RESULTS.md`

**What was demonstrated:**

- 933x asymmetry between forward and backward pitch rotation
- Forward pitch (reducing temporal lag below zero): 0% success (0/12 attempts)
- Backward pitch (increasing temporal lag): 93% success (14/15 attempts)
- Z-axis rotation in the 2D plane: 100% success (14/14 attempts)
- The asymmetry emerges from the constraint that entities cannot advance past the present tick

**Transfer assessment:** This result is a kinematic constraint of discrete time, not a property
of any spatial substrate. The conclusion -- that rotation involving the time axis is asymmetric
-- holds on any substrate with discrete, irreversible tick advancement. It transfers directly
to V3.

### 1.7 O(n) Bucketing Performance

**Experiment:** #44_05 (January 2026)
**Substrate:** Discrete temporal rendering pipeline
**Reference:** `experiments/44_05_double_buffer_rendering/RESULTS.md`

**What was demonstrated:**

- O(n) bucketing achieves 2.78x speedup over O(n log n) sorting at 100,000 entities
- 297,000 entities renderable at 60 FPS with bucketing
- Double-buffering enables lock-free simulation/rendering coordination

**Transfer assessment:** This is a computational performance result about temporal rendering
pipelines. It depends on discrete tick structure, not spatial substrate topology. It transfers
directly to any discrete-time framework, including V3.

### 1.8 Interferometry Without Collapse

**Experiment:** #62 (January 2026)
**Substrate:** Lattice substrate with wave-packet propagation
**Reference:** `experiments/62_interferometry/VALIDATION_COMPLETE.md`,
`experiments/62_interferometry/FALSIFIABLE_PREDICTIONS.md`

**What was demonstrated:**

- 26/26 simulation tests passed across 10 phases
- Wave-packet propagation, dispersion relations, and Mach-Zehnder interferometry reproduced
- Which-path information extracted without destroying interference (fringe visibility V = 1.0000
  after complete state readout)
- Gradual visibility response to coupling strength rather than binary collapse
- Falsifiable experimental prediction identified: tick-frame predicts V > 0.9 after which-path
  readout; standard QM predicts V = 0

**What was not demonstrated:**

- These results were obtained in a simulation that implements the tick-frame wave model on a
  lattice. They show internal consistency of the tick-frame wave model, not a physical
  experimental result. The prediction has not been tested against a real quantum system.
- The wave model operates on a lattice substrate. Whether it reproduces on a random graph
  substrate is untested.

**Transfer assessment:** The interferometry prediction is about the deterministic substrate
model versus wavefunction collapse. If the V3 substrate is deterministic (as claimed), the
prediction transfers. The specific numerical results (V = 1.0000) depend on the lattice
implementation and may differ on a graph. The falsifiable prediction itself -- that which-path
does not destroy interference -- is substrate-independent within the tick-frame framework.

**Important caveat:** The simulation tests the tick-frame model against itself. The real
scientific question is whether the prediction holds in a physical experiment. As of March 2026,
no such experiment has been conducted. The prediction remains unfalsified, not validated.

### 1.9 Graph-Lattice Gravity

**Experiment:** #64_109, versions 1-9 (January-February 2026)
**Substrate:** Cubic lattice (k=6) with integer gamma quanta
**Reference:** `experiments/64_109_three_body_tree/experiment_description.md`,
`docs/theory/raw/200_open_questions_experimental_status.md`

**What was demonstrated:**

- Integer gamma quanta on a cubic lattice produce attractive force via self-subtracting transport
- Three-body dynamics emerge without special-casing
- Force law measured at approximately 1/r^2.2 (0.2 excess attributed to lattice anisotropy, k=6)
- v8: Self-subtraction resolves the SNR problem -- entities detect each other's field
- v9: Continuous internal direction enables gravitational deflection and three-body scattering

**Experiment:** #64_109, version 10 (February 2026)
**Substrate:** Cubic lattice (k=6), 100x100x100 = 10^6 nodes
**Reference:** `experiments/64_109_three_body_tree/v10/experiment_description.md`

**What was demonstrated (v10):**

- 433 stable revolutions at r approximately 2 on a 64K-node lattice
- Force acts as turning rate, not acceleration: speed is constant, gravity rotates the velocity
  vector between radial and tangential components (geodesic motion)
- Bresenham-like hop accumulator provides infinite angular resolution on a 6-direction lattice
- Gravitational time dilation (variable edge length) required for orbit stability
- Without time dilation: orbits unstable (inspiral or escape within approximately 50 ticks)
- Hawking-like evaporation behavior in energy drain dynamics

**What was not demonstrated (v10):**

- Equal-mass orbits: both bodies see identical symmetric gradients, no differential turning.
  This is a real limitation, not a parameter issue.
- Conservation laws: energy and angular momentum approximately conserved but not exactly. No
  formal conservation proof for the discrete system.
- Force law convergence: whether the 1/r^2.2 exponent converges to exactly 2.0 at higher
  connectivity has not been tested.

**Transfer assessment:** v1-v9 used a cubic lattice, which has Euclidean geometry baked in. v10
used the same. The V3 substrate is a random geometric graph with no fixed geometry. The
integer-gamma, self-subtracting transport mechanism is substrate-independent, but the specific
orbital dynamics (433 revolutions, geodesic turning) depended on the regularity of the cubic
lattice and the Bresenham accumulator. Whether these results transfer to a random geometric graph
is the explicit subject of the v21-v24 experimental arc described in Section 2.

### 1.10 Summary Table: V2-Substrate Results

| Result                     | Experiment    | Substrate          | Key metric            | Transfers to V3?                   |
|----------------------------|---------------|--------------------|-----------------------|------------------------------------|
| Time dilation              | #51 v9        | Continuous field   | r = 0.999             | Mechanism yes, precision unknown   |
| Geodesic orbits            | #53 v10       | Continuous field   | 100% orbital          | Mechanism yes, not tested on graph |
| Collision physics          | #55           | Lattice            | 3 regimes validated   | Mechanism yes, Pauli unknown       |
| 3D optimality              | #15 v6-gpu    | Regular grid       | SPBI = 2.23           | Plausible, not tested              |
| Dim. equivalence rejection | #50           | Grid + time        | 0/6 passed, rho = 2.0 | Yes, substrate-independent         |
| Rotation asymmetry         | #44_03        | Temporal lag       | 933x ratio            | Yes, substrate-independent         |
| O(n) bucketing             | #44_05        | Temporal rendering | 2.78x speedup         | Yes, substrate-independent         |
| Interferometry             | #62           | Lattice            | 26/26 tests           | Prediction transfers, not physical |
| Lattice gravity            | #64_109 v1-v9 | Cubic lattice      | 1/r^2.2 force         | Mechanism yes, specifics untested  |
| Stable orbits              | #64_109 v10   | Cubic lattice      | 433 revolutions       | Mechanism yes, specifics untested  |

Three results are substrate-independent (dimensional equivalence rejection, rotation asymmetry,
O(n) bucketing). The remaining seven use substrates that differ from the V3 graph. In all seven
cases, the underlying mechanism plausibly transfers but the specific quantitative results have
not been reproduced on the V3 substrate.

---

## 2. V3-Substrate Work In Progress

The V3 graph substrate is a random geometric graph with 3D Euclidean node positions and k-nearest
neighbor connectivity. Connectors are weighted edges that grow under expansion. Gravity is
implemented through gamma deposits: entities deposit field quanta, the field spreads via
diffusion, and entities follow gradients of other entities' deposits. This substrate differs
from the V2 lattice in three fundamental ways: irregular connectivity, non-uniform edge lengths,
and no axis alignment.

The experimental frontier is Experiment #64_109, versions 21-24, which attempt to demonstrate
orbital mechanics on this substrate. This section reports the complete arc.

### 2.1 The v21-v24 Experimental Arc

This arc began on February 25, 2026, and is ongoing as of March 19, 2026. Each version
addressed a specific failure mode identified in the previous version. The arc demonstrates
steady progress in qualitative behavior and steady identification of quantitative obstacles.

#### v21: Force-on-Hop (February 25, 2026)

**Reference:** `experiments/64_109_three_body_tree/v21/experiment_description.md`

**What it addressed:** Versions 18-20 applied force every tick, causing velocity runaway.
An entity sitting at a node for 100 ticks between hops received 100 force applications from
the same connectors -- like being pushed 100 times before taking a step.

**What it introduced:** Force applied only at the moment of hopping to a new node. Between
hops, the entity coasts on pure inertia. This is the graph analog of a symplectic integrator.

**What it found:**

- Warm-up diagnostic revealed the "frozen planet" bug: planet placed next to a star with zero
  established field escapes immediately
- Bootstrap deadlock identified: planet cannot orbit before field exists, but field does not
  form with planet present
- Velocity bounded (no runaway), confirming force-on-hop eliminates the pumping artifact
- Very few hops achieved (3-5 per 5000 ticks) due to velocity-to-connector projection failure

**Status:** Completed. Identified architectural problems rather than solving orbital mechanics.
Handed off to v22.

#### v22: Star Formation Before Planet Formation (March 14-15, 2026)

**Reference:** `experiments/64_109_three_body_tree/v22/experiment_description.md`

**What it addressed:** The frozen planet bug and preset velocity problem from v21. Introduced
the principle that the star must form first, establish its gravitational field, and only then
can a planet exist in that field.

**What it introduced:**

- Phase 0: Star formation from seed deposit (mass 1.0, not 100,000). Star grows via
  self-reinforcing accumulation over 20,000+ ticks.
- Phase 1: Orbital velocity derived from measured force, not guessed.
- Leapfrog force integration (every 10 ticks, decoupled from hops).
- True 3D displacement accumulation replacing per-connector projection.
- Local hop threshold tracking expansion.

**Key measurements:**

- F_radial at r=8: -0.0000196 (100% inward, 395 nodes sampled)
- v_circular derived: 0.00396 (from measured force, inertia=10, force_coeff=1.0)
- Mean ticks/hop: 611 +/- 49 (k=24, radius=30)

**Key results:**

- First curved trajectories in the entire experiment arc (leapfrog N=10 configuration)
- Best particle (p14 in leapfrog run) survived 11,945 ticks with velocity declining 30%
  (0.00396 to 0.00278) -- gravity actively decelerating outward drift
- Two bugs discovered during v22: frozen hop threshold (never updated with expansion) and
  v21 per-connector projection still active despite v22 design specifying 3D displacement
- After bug fixes, best particle (p17) survived 16,041 ticks. Velocity dropped 28%
  (0.0035 to 0.00252). Velocity stabilized at approximately 0.0027 around tick 12,000.

**Discovery: Field self-pinning.** Dense regions resist expansion automatically. The expand_edges
formula suppresses growth near high gamma:

```
growth = H / (1 + alpha * (gamma_A + gamma_B))
```

Bodies that deposit continuously maintain high local gamma, so their neighborhood barely expands.
Empty voids expand freely. This reproduces the qualitative Hubble flow -- galaxies do not expand,
the space between them does -- from the deposit mechanism alone, with no additional parameters.

**Status:** Completed. Proved the physics works qualitatively. Failure mode identified as domain
size: the orbit's natural radius exceeds the graph boundary (radius=30). Handed off to v23.

#### v23: Larger Graph Domain (March 15-18, 2026)

**Reference:** `experiments/64_109_three_body_tree/v23/experiment_description.md`

**What it addressed:** Domain size. The particle's natural orbital radius in v22 exceeded the
finite simulation domain. v23 enlarged the graph to 80,000 nodes with radius=45 (from 30,000
nodes and radius=30 in v22).

**What it kept unchanged:** All v22 final mechanics: leapfrog force, true 3D displacement, local
hop threshold with floor, derived orbital velocity from measured force.

**Key measurements (v23):**

| Radius | F_radial   | % inward | v_circular (i=10) |
|--------|------------|----------|-------------------|
| r=8    | -0.0000198 | 100%     | 0.00398           |
| r=25   | -0.0000062 | 92%      | 0.00394           |

**Five runs completed:**

**Run A** (v=0.00398 at r=8, stable star): Super-circular. Particles escaped to boundary
(r=40.5) by tick 36k. The derived v_circular at r=8 is super-circular for actual dynamics
because the gradient weakens as particles drift outward.

**Run B** (v=0.003 at r=8, radiating star): Velocity plateau at 0.00128-0.00131 for 18,000
ticks (tick 36k-54k). All best-3 particles still bound at 60k ticks. Late velocity uptick
(0.00129 to 0.00139) as star mass dropped to 55%.

**Run C** (v=0.003 at r=8, stable star): **Best result in the arc.**

- Particle p8: r went 8.0 to 21.1 (tick 36k) to 17.1 (tick 60k). **First radial reversal
  in the entire v21-v24 arc.** The particle turned around and moved back toward the star.
- Particle p19: Locked at r=25.9 for 27,000 consecutive ticks (tick 33k-60k).
  Final |v|=0.00040.
- All best-3 particles bound at 60k ticks.

**Run D** (v=0.00394 at r=25, stable star, radiating disk): Escaped to boundary by tick 27k.
Ring particles' own mass radiation corrupted field dynamics.

**Run E** (v=0.003 at r=25, stable star + disk, no mass loss): **The definitive control test.**
Escaped. All best-3 hit boundary between tick 34k-44k. Drift was slow (25 to 33 in 30k ticks)
but never reversed.

**The critical diagnosis:** Run E showed that Run C's p19 equilibrium was NOT a circular orbit.
It was dissipative capture. Particle p19 arrived at r approximately 26 with |v|=0.0004 after
bleeding kinetic energy over 33,000 ticks of outward spiral from r=8. Particles starting
directly at r=25 with v=0.003 had 7.5x more velocity and escaped. The gradient at r=25
(F_radial = -0.0000062, only 31% of the r=8 value) was too weak to decelerate them.

**What v23 proved:**

- Larger domain removes boundary artifacts (Run C: all particles bound at 60k)
- Stable star (no mass loss) eliminates late-run field decay
- Leapfrog force genuinely decelerates particles and curves trajectories
- Radial reversal is physically possible on this substrate (p8: 21.1 to 17.1)
- Radial equilibrium is physically possible (p19: locked at r=25.9 for 27k ticks)

**What v23 did not prove:**

- Closed orbits. No perihelion/aphelion oscillation observed.
- That the gradient supports actual orbital dynamics at radii where particles settle.
- That v_circular derived from measure_force is reliable -- particles initialized at the
  derived v_circular consistently escape.

**Honest assessment from the experiment log:**

> "The remaining problem is not domain size or architecture -- it's force strength. The gradient
> drops off faster than 1/r^2 and can't provide enough centripetal force at the radii where
> particles naturally settle. Run C's success was dissipative capture, not orbital mechanics."

**Status:** Completed. Handed off to v24. The failure mode shifted from architecture (v21),
to domain size (v22), to force strength (v23).

#### v24: Stronger Gradient -- M=1M Star (March 18, 2026)

**Reference:** `experiments/64_109_three_body_tree/v24/experiment_description.md`,
`experiments/64_109_three_body_tree/v24/results_phase1.md`

**What it addressed:** Force strength. v23 showed the gradient was too weak at orbital radii.
v24 increased star mass by 10x (from 100,000 to 1,000,000) to strengthen the gradient.

**What it discovered: Anti-Newtonian scaling.**

| Metric            | v23 (M=100k) | v24 (M=1M)  | Ratio               |
|-------------------|--------------|-------------|---------------------|
| F_radial at r=8   | -0.0000198   | -0.00000129 | 0.065x (15x weaker) |
| v_circular (i=10) | 0.00398      | 0.00101     | 0.25x               |

**The 10x heavier star produced a 15x weaker force.** This is the opposite of Newtonian scaling.

**Explanation:** The force law denominator is `1 + alpha * (gamma_A + gamma_B)`. More mass
produces more gamma everywhere. The denominator grows uniformly. Growth is uniformly suppressed.
Force depends on asymmetry between connectors, not absolute growth. Uniform suppression kills
the asymmetry. The field self-pins so strongly it suppresses its own gradient.

**The critical insight:** This anti-Newtonian scaling is a **float arithmetic artifact**, not
physics. In the true substrate model, gamma is binary: a node either has a deposit (gamma=1) or
does not (gamma=0). No node can accumulate more than one deposit. The force law denominator
is bounded:

```
growth = H / (1 + alpha * 0) = H        (empty node)
growth = H / (1 + alpha * 1) = H/2      (one deposit, alpha=1)
```

Maximum suppression factor: 2x. The pathological self-suppression observed in v24 (denominator
reaching 10,000x) is impossible in the integer model. The float gamma field allows unbounded
accumulation at a single node (10 gamma units per tick with M=1M), which is physically
meaningless in the discrete substrate.

**Additional insight:** A point star (all deposits at one node) is physically wrong. A real star
distributes deposits across a volume of nodes. The `body_radius` parameter exists in the code
but was set to zero. Using body_radius = 3-5 would distribute deposits across 30-500 nodes
and eliminate the worst self-suppression artifacts.

**Status:** Phase 2 running (v=0.00101 at r=8). Force and v_circular are internally consistent
at the weaker level: centripetal requirement = 0.00000128, measured F_radial = -0.00000129.

### 2.2 V3-Substrate: What Has Been Established

Across v21-v24, the following behaviors have been demonstrated on the random geometric graph
substrate:

**Star formation gradient:** A seed deposit at a central node, with continuous deposition and
diffusion, produces a radially decreasing gamma profile. The gradient is 100% inward at r=8
(v22 Phase 0, v23 force measurement). This is the gravitational field analog on a graph.
*Established in v22 Phase 0, confirmed in v23.*

**Force measurement and v_circular derivation:** Radial force can be measured from the gamma
gradient at any radius, and v_circular can be derived from F = mv^2/r. The derivation produces
internally consistent values.
*Established in v22 Phase 1, confirmed in v23 and v24.*

**Curved trajectories:** Leapfrog force integration (every 10 ticks) with true 3D displacement
accumulation produces the first genuinely curved particle trajectories on a random geometric
graph. Gravity actively decelerates outward-drifting particles.
*Established in v22 Phase 2 (leapfrog run), confirmed in v23.*

**Radial reversal:** Particle p8 in v23 Run C reversed radial direction: r = 21.1 at tick 36k
to r = 17.1 at tick 60k. This is the first time a particle on this substrate moved back toward
the gravitating body rather than monotonically drifting outward.
*Established in v23 Run C.*

**Velocity stabilization:** Particles decelerate under gravitational braking and reach velocity
plateaus. v22 best particle: 0.0035 to 0.00252 (28% reduction). v23 Run B: plateau at
0.00128-0.00131 for 18,000 ticks. Velocity does not run away and does not freeze.
*Established in v22, confirmed in v23.*

**Self-pinning:** Dense gamma regions resist expansion automatically. The expansion suppression
formula produces correct qualitative cosmological behavior: dense bodies pin their local graph,
voids expand freely. This is the Hubble flow from a single mechanism.
*Discovered in v22 Phase 0.*

**Dissipative capture:** A particle that spirals outward while losing kinetic energy can reach
a radius where its residual velocity is small enough for the weak gradient to hold it. This
produces radial equilibrium (v23 Run C, p19: locked at r=25.9 for 27,000 ticks) but is not
the same as orbital mechanics.
*Observed in v23 Run C, diagnosed via v23 Run E.*

### 2.3 V3-Substrate: What Has NOT Been Established

The following behaviors have NOT been demonstrated on the random geometric graph substrate, and
each is necessary for the V3 theory to make quantitative contact with physics. These gaps are
listed in approximate order of importance.

**No closed orbit.** No particle on the V3 substrate has completed a perihelion/aphelion
oscillation, let alone a full revolution. All trajectories are outward spirals with varying
degrees of deceleration and curvature. The radial reversal of p8 (21.1 to 17.1) is the closest
approach, but it occurred over 24,000 ticks of monotonic inward drift -- not oscillation around
an equilibrium radius.

**No 1/r^2 force law from deposit gradient.** The force law has been measured at two radii
(r=8 and r=25 in v23), giving F_radial values of -0.0000198 and -0.0000062. This is a factor
of 3.2x difference across a factor of 3.1x in radius, suggesting approximately 1/r scaling.
But two data points do not establish a power law, and the measurements are contaminated by the
float gamma model's self-suppression artifact. On the earlier cubic lattice (v1-v9), the
measured exponent was 2.2. Whether the random geometric graph reproduces 1/r^2 remains unknown.

**No angular momentum conservation over orbital timescale.** Angular momentum has not been
tracked systematically across the v21-v24 arc. v21 predicted that L_z should maintain sign
for many consecutive hops. This prediction has not been quantitatively tested. The trajectory
visualizations show curved paths, but whether angular momentum is conserved, approximately
conserved, or drifting is not known.

**No Kepler's third law.** Since no closed orbit has been produced, there is no orbital period
to measure. Kepler's third law (T^2 proportional to r^3) requires stable orbits at multiple
radii, which do not exist on this substrate.

**No time dilation from self-pinning.** Self-pinning has been observed: dense regions resist
expansion. The theory claims this produces gravitational time dilation (entities in dense
regions accumulate depth faster relative to entities in sparse regions). This claim has not
been measured. Specifically: the ratio of hop rates at two different gamma densities has not
been compared to the predicted time dilation ratio. The mechanism is present; the quantitative
prediction is untested.

**No three-state alphabet as observable physical states.** The V3 theory proposes that all
physical phenomena reduce to three comparison outcomes: same, different, and unknown. These
states have not been instantiated in any simulation. No experiment has implemented the
comparison operation or measured its physical consequences. The three-state framework remains
a theoretical construct without experimental grounding.

**No photon properties from path geometry.** The theory claims photon frequency, amplitude,
and polarization emerge from the geometry of `different` events propagating along paths. No
quantitative derivation of photon properties from path geometry has been produced. No
simulation has generated photon-like behavior from graph-substrate mechanics.

**No traversal-driven expansion replacing global H.** The current simulations use a global
expansion parameter H applied to all edges every tick. The theory (RAW 112) claims expansion
should be driven by entity traversals: each hop extends the traversed connector, and expansion
is the cumulative effect of all hops. This mechanism has not been implemented. H remains a
free parameter in all simulations to date.

### 2.4 Progression of Failure Modes

The v21-v24 arc shows a clear progression in the nature of failures:

| Version | Primary failure mode              | Root cause                                       |
|---------|-----------------------------------|--------------------------------------------------|
| v21     | Frozen planet, bootstrap deadlock | Architectural: planet placed before field exists |
| v22     | Domain too small                  | Boundary artifact: natural radius exceeds graph  |
| v23     | Force too weak at settling radius | Physics: gradient drops faster than 1/r^2        |
| v24     | Anti-Newtonian mass scaling       | Float artifact: gamma self-suppression           |

The failures are qualitatively different at each stage. v21 failed because the architecture
was wrong. v22 failed because the domain was too small. v23 failed because the force law is
wrong at large radii. v24 revealed that the float gamma model itself has pathological behavior
at high mass.

This progression is evidence of genuine progress: each version solves the previous problem and
exposes a deeper one. But it is not evidence of success. The V3 substrate has not yet produced
the orbital mechanics that the V2 lattice substrate achieved in version 10 (433 revolutions).

---

## 3. Gap Analysis

### 3.1 The Theory-Experiment Gap

The V3 theoretical framework (RAW 108-113) makes the following core claims:

1. A raw graph with deposit-based dynamics produces gravity, radiation, and expansion from one
   operation.
2. Three comparison states (same/different/unknown) generate all physical phenomena.
3. Geometry is reconstructed by observers from causal latency, not embedded in the substrate.
4. Time is branch depth, not an external parameter.
5. Expansion is driven by entity traversals, not a cosmological constant.

The experimental status of each claim:

| Claim                           | Theoretical basis | Experimental status                                                                      |
|---------------------------------|-------------------|------------------------------------------------------------------------------------------|
| Deposit-based gravity           | RAW 112           | Qualitative: curved trajectories, radial reversal. Quantitative: no orbit, no force law. |
| Three comparison states         | RAW 113           | No experimental instantiation. Theoretical only.                                         |
| Observer-reconstructed geometry | RAW 110           | Not tested. Simulations use embedded 3D coordinates.                                     |
| Time as branch depth            | RAW 113, V3 Ch.4  | Self-pinning observed but time dilation not measured from it.                            |
| Traversal-driven expansion      | RAW 112           | Not implemented. Global H used in all simulations.                                       |

**Of the five core claims, one has qualitative experimental support, and zero have quantitative
experimental support on the V3 substrate.**

### 3.2 What Transferred and What Did Not

Three categories of V2 results can be distinguished:

**Transferred cleanly (3 results):** Dimensional equivalence rejection (#50), rotation asymmetry
(#44_03), and O(n) bucketing (#44_05) are substrate-independent. They concern properties of
discrete time itself and hold on any discrete-tick substrate, including V3's graph.

**Mechanism plausibly transfers (7 results):** Time dilation (#51 v9), geodesic orbits (#53 v10),
collision physics (#55), 3D optimality (#15), interferometry (#62), and lattice gravity
(#64_109 v1-v10). These use mechanisms (gradient-following, deposit dynamics, occupancy limits)
that could work on a graph. But "could" is not "does." The v21-v24 arc is the ongoing attempt
to verify transfer for the gravity mechanism. As of v24, the mechanism produces qualitatively
correct behavior but has not reproduced the quantitative success of v10's 433-revolution orbit.

**Not yet testable on V3 (all three-state claims):** The three-state alphabet, observer
reconstruction, and traversal-driven expansion have no V3 experimental protocol. These claims
are theoretical constructs that cannot currently be tested because the simulation does not
implement the relevant operations.

### 3.3 The Float Gamma Problem

A cross-cutting issue affects all V3-substrate experiments: the gamma field is implemented as
float64 values, not as the binary deposits the theory describes.

The theory (RAW 112) claims:

- Each deposit event places exactly one unit at one node
- Deposits are binary (present or absent at each node)
- The field propagates only via entity hops at c
- No diffusion operation

The simulation implements:

- Continuous float gamma values that accumulate without bound
- A diffusion (spread) operation that propagates field instantaneously
- Continuous velocity vectors in Euclidean 3D space

These approximations are justified as continuum limits of the discrete physics, and they are
adequate for qualitative exploration. But v24's anti-Newtonian scaling shows they can produce
pathological behavior that the true discrete model would not exhibit. Any quantitative result
on the V3 substrate must be interpreted with this caveat: the simulation approximates the
theoretical substrate, and the approximation can fail in specific regimes.

---

## 4. What Would Constitute Validation

This section defines specific, falsifiable criteria for validating the V3 framework's core
claims. Each criterion specifies what must be observed, on what substrate, and what it would
prove.

### 4.1 Closed Orbit from Proto-Disk with Derived Velocity

**The test:** A star forms from a seed deposit. A proto-disk of small deposits is placed at
orbital radius after the field reaches quasi-equilibrium. Orbital velocity is derived from the
measured field gradient, not preset. Particles coalesce from the disk and execute at least one
complete radial oscillation (perihelion/aphelion) without escaping or collapsing.

**Why this matters:** This is the single most important validation target. If the deposit-based
mechanism on a random graph can produce a stable orbit without preset initial conditions, it
demonstrates that gravity emerges from graph topology alone. The V2 lattice achieved this
(#64_109 v10, 433 revolutions). V3 has not.

**What it would prove:** That the gradient-following mechanism transfers from regular lattices
to random geometric graphs. That the graph's irregular connectivity does not destroy orbital
stability. That the continuum approximation (float gamma) is adequate for orbital mechanics.

**What it would not prove:** That the three-state alphabet is the correct description of the
underlying mechanism. That traversal-driven expansion works. That time dilation emerges from
self-pinning.

**Current status:** Not achieved. Best result is v23 Run C (radial reversal and dissipative
capture, not orbital mechanics).

### 4.2 1/r^2 Force Law Measured at Multiple Radii

**The test:** Measure F_radial at five or more radii (e.g., r = 5, 8, 12, 18, 25) on a stable
star with fixed mass. Fit to F = -A/r^n. Report the exponent n and the goodness of fit.

**Why this matters:** The force law is the quantitative bridge between the deposit mechanism and
Newtonian gravity. On the cubic lattice, the measured exponent was approximately 2.2. On the
random geometric graph, only two radii have been measured (r=8 and r=25 in v23). Two points
cannot establish a power law.

**What it would prove:** The exponent would reveal whether the deposit gradient naturally
produces inverse-square force on a graph, or whether the force law is different (inverse linear,
inverse cubic, or distance-dependent exponent). This is a direct measurement of the theory's
most basic quantitative prediction.

**Current status:** Not achieved. Two data points exist; five or more are needed.

### 4.3 Time Dilation Ratio Matching Self-Pinning Density Ratio

**The test:** Place two identical entities at different distances from a massive body. Measure
their hop rates (hops per N ticks) over a long period. The theory predicts that the entity
closer to the mass hops faster (stronger gradient, larger force nudge, faster displacement
accumulation). The ratio of hop rates should correlate with the ratio of local gamma densities.

**Why this matters:** Gravitational time dilation is one of the most precisely tested predictions
of general relativity. The V3 theory claims it emerges from self-pinning: dense regions have
shorter effective edge lengths and faster local dynamics. If the hop rate ratio matches the
density ratio, it would be the first quantitative derivation of time dilation from graph topology.

**What it would prove:** That self-pinning produces measurable, quantitatively correct time
dilation without programming it in. This is distinct from the v9 result (which measured time
dilation on a continuous field with forced trajectories).

**Current status:** Self-pinning observed (v22 Phase 0). Hop rate measurements exist (v22:
611 +/- 49 ticks/hop at one radius). Systematic comparison across radii has not been done.
The predicted correlation has not been tested.

### 4.4 Same/Different/Unknown as Explicit Observable States in Simulation

**The test:** Implement the comparison operation from RAW 113 explicitly in the simulation.
At each tick, each entity compares its current node's state to the previous tick's state and
classifies the result as `same` (no change), `different` (change detected), or `unknown`
(new, never-before-seen node). Track the frequency and distribution of each state. Verify that
`same` events correlate with gravitational binding, `different` events correlate with radiation,
and `unknown` events correlate with expansion.

**Why this matters:** The three-state alphabet is the theoretical core of V3. It is the most
novel claim and the least tested. If the three states cannot be observed in simulation as
distinct, measurable events with the predicted physical correlates, the theoretical framework
loses its central organizing principle.

**Current status:** Not implemented. No simulation uses the comparison operation. The three
states exist only in theoretical documents (RAW 113).

### 4.5 Quantitative Photon Frequency from Different Firing Rate

**The test:** Generate `different` events propagating along a path in the graph. Measure the
rate at which these events pass a stationary observer node. Verify that this rate corresponds
to a frequency, and that the frequency shifts as predicted when the source or observer moves
(Doppler effect) or when the path passes through a gamma gradient (gravitational redshift).

**Why this matters:** The V3 theory claims that photons are not particles but propagating
`different` events. If the `different` firing rate produces measurable frequency, and that
frequency obeys the expected relativistic transformations, it would validate the most radical
claim of the framework: that light emerges from the comparison operation rather than from a
separate force carrier.

**Current status:** Not attempted. Requires implementation of the comparison operation
(Section 4.4) as a prerequisite.

### 4.6 Validation Hierarchy

The five criteria above form a natural hierarchy, ordered by what they would prove and what they
depend on:

```
Level 1: Closed orbit on graph (Section 4.1)
   Proves: gradient mechanism transfers to random graph
   Depends on: nothing (can be tested now)
   Status: IN PROGRESS (v21-v24 arc)

Level 2: 1/r^2 force law (Section 4.2)
   Proves: deposit gradient produces correct force law
   Depends on: stable gamma field (partially available)
   Status: NOT STARTED (needs systematic measurement)

Level 3: Time dilation from self-pinning (Section 4.3)
   Proves: depth accumulation rate = gravitational time dilation
   Depends on: stable orbits or at least stable hop rates (partially available)
   Status: NOT STARTED (self-pinning observed, ratio not measured)

Level 4: Three-state alphabet observable (Section 4.4)
   Proves: theoretical framework has experimental correlates
   Depends on: comparison operation implementation (not available)
   Status: NOT STARTED (requires new code)

Level 5: Photon from different events (Section 4.5)
   Proves: radiation emerges from comparison operation
   Depends on: Level 4 complete
   Status: NOT STARTED (depends on Level 4)
```

Level 1 is the current experimental frontier. Level 2 could be addressed immediately with
existing infrastructure (force measurement at multiple radii). Level 3 requires modest
additional instrumentation. Levels 4 and 5 require new code that does not yet exist.

---

## 5. Known Artifacts and Methodological Caveats

### 5.1 Float Gamma vs. Integer Deposits

As discussed in Section 3.3, all V3-substrate experiments use a float64 gamma field as a
continuum approximation of the theorized binary deposit substrate. This approximation:

- Allows unbounded gamma accumulation at single nodes
- Uses diffusion (spread) rather than hop-carried propagation
- Represents velocity as continuous 3D Euclidean vectors

The v24 anti-Newtonian scaling is the most dramatic demonstration of where this approximation
fails. But subtler artifacts may exist in all prior experiments. Any quantitative result should
be interpreted as "what the float approximation produces," not necessarily "what the discrete
substrate would produce."

### 5.2 Embedded Coordinates

The random geometric graph has 3D Euclidean node positions by construction. Force computation,
velocity tracking, and trajectory visualization all use these coordinates. The V3 theory claims
that geometry is an observer reconstruction, not a substrate property. The simulations embed
geometry from the start. This means the experiments cannot test the observer-reconstruction
claim -- they assume what the theory says should be derived.

### 5.3 Global Expansion Parameter

All V3-substrate experiments use a global Hubble parameter H applied to all edges every tick.
The theory claims expansion should be traversal-driven (each hop extends the connector). The
global H is a stand-in for this mechanism. It was observed in v22 that self-pinning partially
compensates for H (dense regions resist expansion), which provides qualitative support for the
traversal-driven picture. But the actual mechanism has not been implemented.

### 5.4 Forced Initial Conditions

In v22-v24, particles are placed at specified radii with specified velocities. Although v22
introduced the principle that velocity should be derived from the measured field, the initial
placement at a ring radius is still a manual choice. A fully validated orbit would need to
emerge from a proto-disk without specifying where the planet forms or at what radius it orbits.
This has not been achieved.

---

## 6. Honest Summary

The tick-frame framework has a substantial body of experimental evidence. It is unevenly
distributed across two different substrates.

**On V2 substrates (continuous fields, regular lattices):** The evidence is strong. Time
dilation at r = 0.999 correlation. 100% geodesic orbital completion. 433 stable revolutions
on a cubic lattice. Collision physics with emergent Pauli exclusion. 3,960 simulations
establishing 3D optimality. Decisive rejection of dimensional equivalence. These are real
results on real substrates.

**On the V3 substrate (random geometric graph):** The evidence is qualitative. Curved
trajectories. Radial reversal. Velocity stabilization. Star formation. Self-pinning. These
are genuine, non-trivial behaviors that did not exist before v22 and represent steady progress.
They are not orbits. They are not force laws. They are not quantitative time dilation.

**The honest gap:** The V3 theory makes claims that go well beyond what V2 experiments showed
and well beyond what V3 experiments have shown. The three-state alphabet, observer-reconstructed
geometry, and traversal-driven expansion are theoretical constructs with no experimental support
of any kind. The graph-substrate gravity mechanism has qualitative support and zero quantitative
validation.

**What has not been acknowledged as prominently as it should be:**

- No closed orbit on any graph substrate (random or otherwise), despite the cubic lattice
  achieving 433 revolutions.
- No force law measurement beyond two data points.
- No three-state comparison operation in any simulation.
- The float gamma approximation produces artifacts that may contaminate results.
- All graph simulations embed 3D coordinates, which the theory says should be emergent.

**What is genuinely encouraging:**

- The failure modes are progressing from architectural to physical, suggesting the architecture
  is converging toward something correct.
- Self-pinning emerged unprogrammed and qualitatively reproduces the Hubble flow.
- The v21-v24 arc demonstrates systematic, honest experimental methodology: each version
  identifies its own failure mode and proposes the correct next step.
- The anti-Newtonian scaling in v24, while a failure, correctly diagnosed the float model's
  limitations and pointed toward the integer substrate as the resolution.

**The assessment:**

> The graph-first framework is theoretically coherent. It has produced correct qualitative
> behavior (curved trajectories, radial reversal, velocity stabilization, self-pinning).
> Quantitative validation of core claims (closed orbit, force law, time dilation from depth)
> is in progress but not achieved. The gap between theoretical ambition and experimental
> evidence is large. Closing it requires solving the float gamma problem (either via distributed
> star, integer deposits, or both) and achieving at least one stable orbit on a random geometric
> graph.

---

## References

### V2-Substrate Experiments

- Exp #15 v6-gpu: 3,960 dimensional simulations. `experiments/15_minimal-model/v6-gpu/`
- Exp #44_03: Rotation asymmetry, 933x ratio. `experiments/44_03_emergent_rotation/RESULTS.md`
- Exp #44_05: O(n) bucketing, 2.78x speedup. `experiments/44_05_double_buffer_rendering/RESULTS.md`
- Exp #50: Dimensional equivalence rejection.
  `experiments/50_dimensional_equivalence_explicit_time/EXPERIMENT_RESULTS.md`
- Exp #51 v9: Time dilation, r = 0.999 correlation. `experiments/51_emergent_time_dilation/v9/RESULTS.md`
- Exp #53 v10: Geodesic orbits, 100% completion. `experiments/51_emergent_time_dilation/v10/RESULTS.md`
- Exp #55: Collision physics, Pauli exclusion. `experiments/55_collision_physics/VALIDATION_RESULTS.md`
- Exp #62: Interferometry, 26/26 tests. `experiments/62_interferometry/VALIDATION_COMPLETE.md`
- Exp #64_109 v1-v9: Integer gamma gravity on cubic lattice. `experiments/64_109_three_body_tree/`
- Exp #64_109 v10: 433 revolutions, geodesic turning. `experiments/64_109_three_body_tree/v10/`

### V3-Substrate Experiments

- Exp #64_109 v21: Force-on-hop. `experiments/64_109_three_body_tree/v21/experiment_description.md`
- Exp #64_109 v22: Star formation, curved trajectories.
  `experiments/64_109_three_body_tree/v22/experiment_description.md`
- Exp #64_109 v23: Larger domain, radial reversal. `experiments/64_109_three_body_tree/v23/experiment_description.md`
- Exp #64_109 v24: M=1M star, anti-Newtonian scaling. `experiments/64_109_three_body_tree/v24/experiment_description.md`

### Theoretical Foundation

- RAW 108: Three dimensions from trit change geometry
- RAW 109: Apparent isotropy of c
- RAW 110: Local dimensionality
- RAW 111: Space is connections
- RAW 112: The single mechanism
- RAW 113: Semantic isomorphism -- same/different/unknown
- RAW 120: Sparse unknown routing
- RAW 200: Open questions and experimental status

---

## April 2026 Update: Experiments 118 and 128

### Experiment 118: Entity Hopping Model (April 1-3, 17 versions, CLOSED)

Tested whether entities hopping on a random geometric graph produce orbital
mechanics from the consumption-transformation mechanism. Key results:

**What was established:**
- Gravitational BINDING (attraction + confinement) from deposit routing (v7+)
- Same/Different consumption rule: Same reclassifies Different, connectors can
  shrink (v16). First connector dynamics that allow equilibrium distances.
- Star thermal equilibrium fills 73% of graph volume, SCALE-INVARIANT (v12, v14).
  This is thermodynamics at N=80, not a model limitation.
- Aristotle's deadlock (v10): pure reactive entities freeze. Newton I required.
- Traversal time ∝ connector length creates time dilation (v7, deposit-per-tick)

**What was NOT established:**
- Coherent orbits. v9 diagnostic PROVED all "orbits" are bound random walks
  (per-hop angular displacement same as pure random walk). Best coherence: 0.27.
- Star compaction (always r~14 on 5k graph, r~59 on 50k graph).
- Keplerian velocity profile (hop rate flat, not distance-dependent).

**Closure reason:** Entity hopping on graphs cannot produce orbits at N=80.
The model was exhausted. Superseded by Experiment 128.

### Experiment 128: Deposit Pattern Model (April 3-6, 10 versions, CURRENT)

Fundamental reframing: entities ARE deposit dominance regions, not objects
at graph nodes. Movement IS the statistical shift of the deposit pattern.

**What was established:**
- Radial equilibrium from production/consumption balance on graph (v6:
  deposit distance 12.2, stable for 200k+ ticks)
- Deposit dominance tracking reveals structure invisible to node positions
- Mass = source count (more emission sources = wider deposit territory)
- Consumption IS centripetal force (v9 ODE): F = -consumed/r² produces
  perfect Keplerian orbits. 1,812 revolutions. T² ∝ r³. All three of
  Kepler's laws from consumption. (RAW 130)
- The gravitational constant: GM = L × R / 4π (star emission × planet
  absorption fraction / geometry)
- Tangential thrust (from excess or redirect) DESTABILIZES orbits —
  continuously pumps energy → escape. Angular momentum must be INHERITED,
  not generated. (v9 ODE)
- Consumption IS movement: each consumed deposit shifts the pattern center
  by the deposit's direction (v10). RAW 028 temporal surfing.

**What was NOT established (the remaining gap):**
- That graph deposit dynamics produce a 1/r² force law. The ODE uses
  flux = L/(4πr²) which is geometric dilution in 3D — ASSUMED, not derived
  from graph dynamics. The ODE relabels GM as L×R/4π. This is a
  reinterpretation of Newton, not a derivation from the mechanism.
- Emergent planet formation from star's reject stream (Phase 3)
- Internal planet structure producing directed processing

**Honest assessment:** The consumption mechanism is validated for producing
radial equilibrium (on graphs) and Keplerian orbits (in the ODE). The gap
is the connection: graph deposit dilution → measurable 1/r² force → orbit.
This may be a mathematical proof rather than a simulation problem.

### New RAW Documents (April 2026)

- RAW 128 — The Energy Partition: Store, Move, or Radiate
- RAW 129 — Experimental Connections (Breit-Wheeler, quantum batteries, CME,
  planetary structure, quantum-classical transition)
- RAW 130 — It Rotates Because It Consumes

### Updated Status Table

| Claim | March 2026 Status | April 2026 Status |
|-------|-------------------|-------------------|
| Gravitational binding | Partial (v22-v24) | **Confirmed** (Exp 118 v7+, Exp 128 v6) |
| Closed orbit | Not achieved | **Achieved in ODE** (1812 rev). Not on graph. |
| 1/r² force law | Not measured | **Derived in ODE** from geometric dilution. Not from graph dynamics. |
| Kepler's laws | Not tested | **All three from ODE** (RAW 130). Not from graph. |
| Same/Different mechanics | Not implemented | **Working** (Exp 118 v12+, Exp 128 v6) |
| Consumption equilibrium | Not tested | **Confirmed** (Exp 128 v6: dist=12.2, stable) |
| Entities as patterns | Not considered | **Validated** (Exp 128 v6: deposit regions ≠ node positions) |
| Newton I required | Not tested | **Confirmed** (Exp 118 v10: Aristotle deadlocks) |
| Graph → 1/r² | Not tested | **NOT ACHIEVED.** The remaining gap. |

---

*Date: March 19, 2026 (initial), April 6, 2026 (updated with Exp 118-128)*
*Substrate coverage: V2 (10 experiments), V3 graph (Exp 64_109 v21-24, Exp 118 v1-17,
Exp 128 v1-10), V3 ODE abstraction (Exp 128 v9-10)*
*Honest assessment: Consumption mechanism validated. Radial equilibrium confirmed.
Keplerian orbits derived in ODE. The graph → force law gap remains the frontier.*
