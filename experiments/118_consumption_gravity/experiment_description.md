# Experiment 118: Consumption-Transformation Gravity

## Overview

This experiment tests the central claim of RAW 118: that gravity emerges from
**consumption and transformation of deposits on connectors**, and that the balance
between consumption routing (inward) and traversal-driven connector extension
(outward) produces stable gravitational binding without any global expansion
parameter.

**Theory document:** `docs/theory/raw/118_gravity_as_consumption_transformation.md`

**This experiment supersedes:** Experiment 64_109 (v1–v24), which is now closed.
Do NOT reuse code from 64_109 — it implements the wrong mechanism (passive field
reading without traversal effects). Start fresh.

---

## ⚠️ CRITICAL: Traps from Previous Experiments (DO NOT REPEAT)

The 64_109 experiment arc (24 versions, ~3 months) systematically discovered what
does NOT work. Every trap listed here was encountered at least once. Read this
section BEFORE writing any code.

### Trap 1: Point-Mass Stars
**What went wrong:** All v1–v24 versions represented the star as a SINGLE NODE
with a mass label (mass=1000, mass=1000000, etc.). A single node has only k
connectors (~24 on random geometric graph). Regardless of the mass label, it has
the same consumption/radiation capacity as any other single node.

**The fix:** Mass MUST be distributed across many nodes. A star with mass M should
occupy N_nodes ∝ M nodes. Each node deposits and consumes independently. The star's
gravitational field emerges from the collective deposits of all its constituent
nodes. There is no mass parameter — mass IS the number of nodes in the pattern.

### Trap 2: Passive Field Reading (No Write-on-Traversal)
**What went wrong:** In v1–v24, entities read connector growth asymmetry to
determine direction, but their traversal did NOT affect the connectors. The entity
was a ghost — it read the field without changing it. This removes the outward
pressure mechanism entirely. Result: no equilibrium possible, everything collapses
or escapes.

**The fix:** Every hop MUST:
1. Consume deposits from the traversed connector (transform Different → Same)
2. Deposit the entity's own pattern onto the connector
3. Extend the connector (because deposits are append-only — old + new = longer)

This is the ENTIRE POINT of this experiment. If traversal doesn't transform
connectors, you're running v25 of the old experiment, not experiment 118.

### Trap 3: Global H as Expansion Mechanism
**What went wrong:** All v1–v24 versions used a global parameter H applied to all
connectors every tick, suppressed by local gamma density:
`growth = H / (1 + alpha * (gamma_A + gamma_B))`
This produces the WRONG pressure profile: dense regions expand LESS, sparse regions
expand MORE. The correct mechanism (traversal-driven extension) predicts the
opposite: dense regions have more traffic → more extension → more pressure.

**The fix:** Set H = 0. There is no global expansion parameter. ALL connector
extension comes from entity traversal. If connectors don't extend, it's because
nothing traversed them. If they extend a lot, it's because they carry heavy traffic.

### Trap 4: Float Gamma with Self-Suppression
**What went wrong:** v24 discovered that float-valued gamma deposited by a massive
point source creates a self-suppression artifact: the star's own deposits are so
large that they suppress connector growth in their own vicinity, producing
anti-Newtonian force scaling (force INCREASES with distance instead of decreasing).

**The fix:** Use integer gamma or carefully normalized deposit values. But more
importantly, with distributed mass (Trap 1 fix), no single node deposits an
enormous value — each of the star's N nodes deposits a small amount. The self-
suppression problem disappears when mass is distributed correctly.

### Trap 5: Continuous Float Direction Vectors
**What went wrong:** v9+ used continuous float direction vectors for entity velocity,
with the actual hop going to whichever lattice neighbor was closest to the float
direction. This works as an approximation but means results depend on continuous
math, not true integer substrate mechanics.

**The lesson:** Be aware of this limitation. Document clearly which parts of the
simulation use float approximation and which are true integer/graph operations. The
goal is to eventually eliminate all float dependencies, but for this experiment it's
acceptable to use float positions on a random geometric graph (as v22–v24 did) as
long as the MECHANISM (consumption-transformation-extension) is correct.

### Trap 6: Force-on-Hop vs Leapfrog
**What went wrong:** v21 used force-on-hop (read gradient once per hop, coast
between hops). This gives too few force corrections per orbit (~20). v22 switched
to leapfrog (force update every N ticks, independent of hop rate), which gave ~60
corrections per orbit and produced the first curved trajectories.

**The lesson:** Use leapfrog or equivalent frequent force updates, decoupled from
hop rate. But note that in the consumption model, "force" is not a separate
computation — it's the consumption asymmetry at the current node. The entity reads
its connectors, consumes from the richest one, and hops. The "force" is implicit
in which connector gets chosen. You may not need a separate force computation at
all — the consumption routing IS the force.

### Trap 7: Insufficient Graph Domain
**What went wrong:** v22 used radius=30 (~30k nodes). Particles escaped because
the graph boundary was too close to the orbital region. v23 increased to radius=60
(~80k nodes) which helped but was still marginal.

**The fix:** Use a graph large enough that the boundary is far from the action.
For the equilibrium test (Phase 1), radius=30 may be sufficient. For the orbit
test (Phase 2), radius=60+ is needed.

### Trap 8: Star Must Form Before Planet Can Orbit
**What went wrong:** v21 placed a star and planet simultaneously. The planet
escaped before the star's gradient could extend to orbital distances. v22 fixed
this by running Phase 0 (star formation, ~20k ticks) before introducing particles.

**The lesson:** Always run a warm-up phase where the star's deposit field
establishes itself. In this experiment, that means: seed the distributed star
cluster, let it reach internal equilibrium (stable mean radius), let its deposit
field extend to orbital distances, THEN introduce the test particle.

---

## Phase 1: Equilibrium Distance Test

### Objective
Demonstrate that two entities achieve stable separation using only the consumption-
transformation mechanism, with H=0. This is the minimum viable test of RAW 118.

### Setup
- **Graph:** Random geometric graph, N=10000–20000 nodes, k=24, radius=30
- **Entity A (heavy):** Cluster of ~50–100 nodes, each depositing every tick
- **Entity B (light):** 1–3 nodes, depositing and consuming
- **H = 0** (no global expansion — this is non-negotiable)
- **Initial separation:** ~15–20 hops between cluster center and entity B

### The Core Mechanism (implement this EXACTLY)

Each entity, each tick:

```
for each of my nodes:
    1. READ: examine deposits on all k local connectors
       - for each connector, compute: how much of the deposit is
         Different (foreign signature) vs Same (my signature)?
    
    2. CHOOSE: select the connector with the richest Different deposits
       (this is the gravitational routing — toward the most transformable)
    
    3. CONSUME: absorb a fraction of the Different deposits from that connector
       - the fraction depends on the entity's receptor efficiency
       - consumed deposits are transformed: Different → Same
       - the entity's internal directional state is updated by the absorbed pattern
    
    4. DEPOSIT: write my own pattern onto the connector
       - append-only: this ADDS to the connector, it does not replace
       - the connector now carries: remaining old deposits + my new deposit
    
    5. EXTEND: the connector is now longer
       - new length = old length + extension_amount
       - extension_amount is proportional to the deposit added
       - THIS is the outward pressure mechanism
    
    6. HOP: move to the neighboring node along the chosen connector
```

### Key Implementation Details

**Deposit identity tagging:** Each deposit must carry a source tag (which entity
deposited it). This is how an entity distinguishes Same from Different. An entity's
own prior deposits are Same — they are NOT consumed (consumption is specifically
Different → Same transformation). Foreign deposits are Different — they ARE consumed.

This naturally implements self-subtraction: the entity ignores its own deposits
when computing the consumption gradient. No separate self-subtraction mechanism
is needed.

**Extension amount:** Start with a simple rule: each hop extends the traversed
connector by a fixed fraction of the entity's deposit size. Tuning this fraction
is the primary free parameter of the experiment. If extension is too large →
everything flies apart. If too small → everything collapses. The sweet spot is the
equilibrium prediction of RAW 118.

**No velocity vector needed initially:** In the purest implementation, the entity
doesn't have a velocity. It just reads, consumes, deposits, extends, and hops —
every tick. Its "velocity" is an emergent property of which connectors it chooses.
For Phase 1 (equilibrium test), start with this pure implementation. If it's too
slow or noisy, add a momentum accumulator (continuous direction vector nudged by
consumption asymmetry each tick, as v9+ did).

### Measurements
- Distance between A's center-of-mass and B, every 100 ticks
- Total connector length in the system (should increase monotonically — expansion)
- Deposit signature distribution (what fraction of graph is A-signature vs B-signature)
- B's velocity magnitude over time

### Success Criteria
1. B initially moves toward A (attraction works)
2. B decelerates as it approaches (extension pressure increases at close range)
3. B reaches a minimum distance and approximately maintains it for >5000 ticks
4. The equilibrium distance is NOT at zero (not collapse) and NOT at the boundary (not escape)

### Failure Modes (all are informative)
- **B collapses onto A:** Extension too weak. Increase extension_amount per hop.
- **B escapes:** Extension too strong. Decrease extension_amount per hop.
- **B oscillates wildly:** No dissipation. The consumption mechanism may need a
  damping channel (energy lost to connector extension = kinetic energy dissipation).
- **A flies apart:** Internal traversal pressure exceeds internal binding. The
  distributed cluster isn't self-stable. May need to start with a pre-bound cluster.

---

## Phase 2: Orbital Test

**Only proceed to Phase 2 after Phase 1 succeeds.**

### Objective
Demonstrate a stable (or quasi-stable) orbit of a test particle around a
distributed star cluster, using only the consumption-transformation mechanism.

### Setup
- **Graph:** Random geometric graph, N=50000–80000 nodes, k=24, radius=60
- **Star:** Cluster of ~200–500 nodes, allowed to reach internal equilibrium first
- **Test particle:** 1–3 nodes, given initial tangential velocity
- **H = 0**

### Protocol
1. **Phase 2a — Star Formation (warm-up):**
   Seed star entities at nearby nodes (within radius ~5 of center). Run consumption-
   transformation dynamics for the cluster alone until it reaches internal
   equilibrium: stable mean radius, no further contraction or expansion. This might
   take 10000–50000 ticks. If the cluster collapses to a point, Phase 2 fails —
   go back and fix the extension/consumption balance.

2. **Phase 2b — Field Establishment:**
   Continue running with the stable star. Monitor the radial deposit profile.
   Wait until the deposit gradient extends to ~40 hops from center and shows
   approximately 1/r behavior on a log-log plot. Record the gradient profile.

3. **Phase 2c — Orbit Test:**
   Place test particle at ~30–40 hops from star center. Give it tangential initial
   velocity (perpendicular to the radial direction). The correct velocity for a
   circular orbit should be derivable from the deposit gradient measured in Phase 2b:
   v_circular = sqrt(gradient_force × r). Run for >50000 ticks. Track position,
   velocity, radius, angle.

### Success Criteria
1. Test particle completes at least 1 full orbit (360° angular displacement)
2. Orbital radius varies by less than 50% (quasi-stable, not necessarily circular)
3. Angular momentum is approximately conserved (|ΔL/L| < 20% over one orbit)
4. Star cluster maintains its structure throughout

### Stretch Goals
- Multiple test particles at different radii showing different orbital periods
  (Kepler's third law: T² ∝ r³)
- Two-body interaction where both entities are distributed clusters (binary star)

---

## Implementation Notes

### Graph Infrastructure
The random geometric graph from v21+ is fine as a starting point. Nodes placed
uniformly in a 3D sphere, edges between nodes within a connectivity radius. Key
properties needed:
- Node positions (3D coordinates — this is the embedding, not the substrate)
- Edge list with mutable lengths
- Deposit storage per connector (tagged by source entity)
- Neighbor lookup per node

### What's New vs v24
| Component | v24 (old) | Experiment 118 (new) |
|-----------|-----------|---------------------|
| Star representation | Single node, mass label | Distributed cluster, many nodes |
| Hop effect on connector | None | Consume + deposit + extend |
| Expansion mechanism | Global H, suppressed by gamma | Traversal-driven only, H=0 |
| Force computation | Read growth asymmetry | Implicit in consumption choice |
| Gamma type | Float, source-tagged | Float or integer, source-tagged |
| Self-subtraction | Explicit filter on field read | Automatic: own deposits are Same, not consumed |

### Output Format
- **Plots:** Position (x,y) trajectory, radius vs time, velocity vs time,
  total connector length vs time, deposit profile (radial)
- **Data:** CSV with columns: tick, entity_id, node, x, y, z, radius_from_star,
  velocity_magnitude, n_hops_total
- **Diagnostics:** Mean connector length, max connector length, deposit mass
  conservation check (total deposits in graph should increase monotonically)
- **Use unbuffered output** (`python -u` or `PYTHONUNBUFFERED=1`) for real-time
  progress monitoring

### Performance Considerations
- Phase 1 should run in minutes (small graph, two entities)
- Phase 2 may take hours (large graph, hundreds of star nodes + test particle,
  many ticks). Optimize the inner loop. Profile if slow.
- The consumption step (scanning k connectors per node per tick) is O(N_entity_nodes × k)
  per entity per tick. For a 500-node star, that's 12000 connector reads per tick.
  This is fine.

---

## What This Experiment Is NOT

- It is NOT a parameter sweep. The mechanism is fixed. The only tunable is
  extension_amount per hop, and even that should eventually be derivable from
  entity mass (deposit size).
- It is NOT trying to reproduce Newtonian gravity quantitatively. It is testing
  whether the consumption-transformation mechanism produces QUALITATIVELY correct
  gravitational binding: attraction at long range, repulsion at short range,
  stable equilibrium in between.
- It is NOT continuing the 64_109 experiment arc. Fresh code. Fresh approach.
  The only thing carried forward is the random geometric graph infrastructure.

---

---

## Version History

| Version | Name | Result | Status |
|---------|------|--------|--------|
| v1 | Equilibrium distance | Radial oscillation around r~14-16, H=0 | Done |
| v2 | Momentum model | Multi-node planet, Different-fraction extension | Done |
| v3 | Planet from core | Entity spirals outward from star center | Done |
| v4 | Connector-as-deposit-count | Extension bug SOLVED, star alive but weak binding (3.8x expansion) | Done |
| v5 | Fixed-graph deposit propagation | Conservation perfect, propagation works, but no gradient → no binding | Done |
| v6 | Accumulated-density routing | Density flat at 97% everywhere — signal saturated, no gradient | Done |
| v7 | Traversal-time model | **FIRST ORBIT.** Time well binds star (20:1 int/bnd ratio). Planet orbits in 3D. | Done |
| v8 | Store/move energy partition | Emergent orbit WITHOUT kick (1869 deg). Partition mechanism barely engaged (absorbed=0). | Done |
| v9 | Three-way partition + diagnostic | "Orbit" is a bound random walk, not real orbit. Partition doesn't engage. | Done |
| v10 | Reactive entities (fire on trigger) | Deadlock. Aristotle's physics: everything waits for a push, nobody pushes first. | Done |
| v11 | Newtonian (forward default + deflection) | No deadlock. 1252 net deg, 8k total. Deflection ~1.0 (too weak). | Done |
| v12 | Same reinforces, Different extends | Internal connectors stay at 2.9 (no growth!). Star STILL r=14.5 — pure diffusion. | Done |
| v13 | Density + Same rule + length momentum | g/f=63:1 but inverted gradient. Star r=14.4. Gravity pulls toward cloud, not center. | Done |
| v14 | Larger graph (50k nodes, R=80) | Star fills 73% of ANY graph (scale-invariant). Coherence 0.27 (best yet). | Done |
| v15 | Propagating deposits build connectors | 3B deposits, saturated. Reactive charging works but flux uniform. | Done |
| v16 | Same consumes Different | Connectors CAN shrink. Consumed(19k) > Different(8k). 37 oscillations. | Done |
| v17 | Inter-group rotation + consumption | Rotation didn't help (groups spatially mixed in diffuse cloud). | Done |

**Note:** Former v4-v10 (stream filtering, trie memory, video decomposition) were
separated to `experiments/trie_stream_filtering/` on March 31, 2026. Those experiments
validate RAW 123 (The Stream and the Trie), not RAW 118 (Gravity). See that directory
for the complete stream filtering arc and results.

## Results Summary

### v1-v3: Radial binding (March 21, 2026)
- Demonstrated equilibrium oscillation using compound connector extension
- Star core connector runaway to 1e28+ (the extension bug)
- No tangential motion, no Kepler verification

### v4: Connector-as-deposit-count model (March 31, 2026)
- **SOLVED the extension bug**: connector length = initial + deposit count. Linear
  growth (max ~97 at 50k ticks), not exponential.
- **Star has real dynamics**: weighted random walk routing produces actual node movement.
- **Star binding WEAK**: mean radius 3.84 → 14.5 (3.8x expansion). Routing signal
  (1 + recent_other_group) too weak vs base exploration weight (1).
- Three routing iterations: deterministic (frozen), exclude-own-group (frozen),
  weighted random walk (alive but dispersed).
- Key insight: deterministic routing on graphs converges to stable cycles.
  Stochastic routing needed for dynamics.

### v5: Fixed-graph deposit propagation (April 1, 2026)
- **Corrected physics**: connectors are fixed-length roads, deposits TRAVEL at 1 hop/tick.
  Eliminates "light sail" problem from v4 where every deposit extended space.
- **Propagation engine**: double-buffered numpy arrays, vectorized at 42-76 t/s.
  Perfect conservation across all runs.
- **Three absorption iterations:**
  1. No absorption (all transparent): 4M deposits uniform, no gradient, 3.8x expansion
  2. Full absorption (entity nodes opaque): deposits stuck at 80, total sink, nothing escapes
  3. Partial absorption (other-group only): 3.2M deposits, ~16 absorbed/tick, but
     uniform distribution — absorption too small vs total field
- **The chicken-and-egg problem identified**: no gradient → no binding → star
  expands → weaker sink → less gradient. The 80 entity nodes (1.6% of graph)
  cannot maintain a deposit density gradient against diffusion once dispersed.

### v6: Accumulated-density routing (April 1, 2026)
- **Returned to v4 ontology** (connector = deposits, length = deposit count).
  v5's fixed-graph propagation was an ontological wrong turn — it postulated
  an empty substrate that doesn't exist in the theory.
- **Accumulated matching_density routing** (matching/length) instead of v4's
  recent-only signal. Expected 40:1 ratios from heavy vs light connectors.
- **Result: density FLAT at 97% everywhere.** With 4M star deposits across 55k
  connectors, the deposit fraction is ~0.97 on every connector. Less than 0.3%
  variation across the graph. Routing ratio collapsed from 127 (early) to 1.0
  (saturated). Star expanded to r=14.4, same as v4/v5.
- **The saturation problem:** accumulated deposits grow without bound while
  differences stay small. After 50k ticks of 80 random-walking nodes, star
  deposits are everywhere. The signal saturates the graph.
- **Conservation: PERFECT** (4M = 80×50k). Max connector length 96. No runaway.
- **Key insight:** in a finite graph, any process that deposits uniformly
  eventually saturates and destroys gradients. v1's compound extension
  (EXTEND_RATE) worked because it made heavily-used connectors exponentially
  longer, creating genuine density differences. Without differential growth,
  density is flat.

### v7: Traversal-time model — FIRST ORBIT (April 1, 2026)

**The breakthrough.** Two key innovations:

1. **Traversal time proportional to connector length.** A node traversing a
   connector of length L takes L ticks. This creates gravitational time dilation:
   nodes deep in the star (long connectors) are trapped for thousands of ticks.
   Boundary nodes (short connectors) move freely. The star self-binds via a
   TIME WELL, not a field gradient.

2. **Deposit-on-arrival (RAW 126).** The node READS during transit (capacitor
   charging) and WRITES one deposit on arrival (capacitor discharge). One deposit
   per traversal, not one per tick. This keeps nodes making routing decisions
   regularly (~every 100-200 ticks) while preserving time dilation.

**Phase 1 results (star equilibrium, 100k ticks):**

| Metric | v4-v6 (best) | v7 deposit-per-tick | v7 deposit-on-arrival |
|--------|-------------|---------------------|----------------------|
| COM drift | 3.3-4.6 | **0.77** | 4.24 |
| Mean radius | 14-16 | **8.5** (2.2x) | 12.0 (3.1x) |
| Int/bnd ratio | ~1 | **20:1** | 2.2:1 |
| Max connector | 97-597k | 597k | **498** |
| Total hops | 3.5k-292k | 3,496 | **292,396** |
| Performance | 42-264 t/s | **50,000 t/s** | 8,478 t/s |

Deposit-on-arrival chosen for Phase 2: weaker binding but nodes active enough
to test orbital mechanics.

**Phase 2 results (planet introduction, 200k ticks):**

- **Phase 2a (no kick):** Planet attracted to star, radial oscillation between
  r=1.25 and r=10.84. BOUND but purely radial (36 deg tangential). First
  attraction + binding in entire experiment 118 line.

- **Phase 2b (tangential kick):** **FIRST ORBIT.** 3.9 net revolutions, 24.5
  radial oscillations, 6202 total degrees of angular motion over 200k ticks.
  Period ~8k ticks. Planet orbits star in 3D. 3D trajectory confirms sustained
  looping motion around star.

- **Phase 2c (different placement, tangential kick):** Orbit robust. 2.1 net
  revolutions, 28 oscillations, 7392 total degrees. Net rotation reversed
  direction (topology-dependent). Binding confirmed.

**Planet placement issue:** All Phase 2 tests had planet inside star body
(r=4-6, star r=12). The 5 planet nodes scatter around the star when picked
by distance threshold. Fix needed: cluster placement (find one node outside
star, take its nearest neighbors).

**Key findings:**
1. Traversal time creates time dilation — the binding mechanism is a time well
2. The orbit is sustained — tangential motion doesn't decay over 200k ticks
3. Orbit direction is topology-dependent (different start → different rotation)
4. Tangential motion requires seeding — the mechanism preserves angular momentum
   but doesn't generate it spontaneously (corrected in v8: emergent orbit without kick)
5. Self-limiting compound growth: connector length ~ t (linear in real time)
   despite doubling per traversal, because traversal time also doubles

### v8: Store/Move energy partition (April 1, 2026)

Implemented the store/move partition from RAW 128: discharged quanta check the
receiving node's capacitor availability. Idle → absorbed (stored). Busy → continues
propagating forward (momentum wake). In-flight quanta propagate at c=1 hop/tick
using forward-continuation, depositing on connectors they traverse.

**Phase 2 results (200k ticks, NO seeded tangential kick):**

- **Attraction: PASS.** Initial distance 19.57 (properly outside star at r=17.5),
  minimum 2.25. Planet fell inward.
- **Bound: PASS.** Final distance 5.42. Planet oscillating, not escaping.
- **Tangential motion WITHOUT kick: PASS.** 1869 total degrees, net -193 degrees.
  The planet orbits without any seeded tangential velocity. First emergent orbit.
- **9.5 radial oscillations** over 200k ticks.
- **Planet cluster placement FIXED.** Find one node beyond star_r + 3, take nearest
  neighbors. Planet starts as a coherent cluster outside the star body.

**But the partition mechanism barely engaged:**
- Total absorbed: 0. No quanta absorbed by idle capacitors.
- In-flight quanta at steady state: ~4. Almost none.
- Store fraction: 0.000. All discharges either stored directly on the arrival
  connector (deposit-on-arrival from v7) or expired.
- The tangential motion comes from graph topology asymmetry (same as v7's
  unsolicited component), not from the forward-momentum wake predicted by RAW 128.

**Diagnosis:** The deposit-on-arrival mechanic (from v7) deposits directly on the
connector at arrival, bypassing the store/move check at the destination node. The
partition mechanism only sees the DischargeEvent destination, but by then the deposit
is already placed. The forward-propagation quanta are too few and short-lived (max
age 50) to create a significant momentum wake.

**RAW 128 updated to v2:** Added third outcome — radiation (quanta that go sideways,
not forward). The three-way partition (store/move/radiate) provides the energy outlet
needed for orbital stability. Without radiation, orbits spiral outward from energy
accumulation. With radiation, the energy budget self-corrects.

### v9: Three-way partition + diagnostic (April 1-2, 2026)

Replaced deposit-on-arrival with full three-way partition: all deposits flow
through store/move/radiate classification. Partition still barely engaged
(store=0, move=99.3%, radiate=0.7%).

**The v9 diagnostic (April 2) was the most important analysis.** Four tests
to determine the tangential motion mechanism:

| Test | Total deg | Finding |
|------|-----------|---------|
| v9 reference | 2,254 | The "orbit" to explain |
| D3 random walk (20 trials) | 1,770,372 | 784x more — hop count difference |
| D4 frozen star | 2,135 | Same as v9 — star dynamics not needed |
| D5 no planet deposit | 5,667 | MORE — planet trail slows things down |

**Verdict: the "orbit" is a bound random walk.** Per-hop angular displacement
is the same for random walk as for routed motion. The deposits and routing
are irrelevant for tangential motion. The traversal-time model (v7) confines
the planet (can't escape), and the random walk within the well produces
apparent rotation. Coherence = 0.20 (target >0.3).

### v10: Reactive entities — Aristotle's deadlock (April 2, 2026)

Entities fire ONLY when triggered by incoming deposits (RAW 126 strict
interpretation). Result: **total deadlock.** Every node waits for a push.
Nobody pushes first. Universe frozen. 0 hops across 200k ticks.

Aristotle's physics implemented literally: motion requires a mover. But
there is no first mover. The universe is dead. Aristotle was wrong.

### v11: Newtonian entities (April 2, 2026)

Newton's first law on the graph: forward continuation as default. Deposits
during charging phase (50 ticks) accumulate a deflection vector (gravity).
No deadlock — entities always have a direction.

**Results:** 24,762 hops, 7,966 total degrees, 1,252 net degrees, 32
oscillations. Most dynamic planet behavior yet. But deflection magnitude
is flat at ~1.0 regardless of distance (only ~1 deposit per 50-tick
charging phase). Forward default produces inertia but gravity is too weak
to coherently bend the path. Coherence = 0.20.

### v12: Same reinforces, Different extends (April 2, 2026)

RAW 113 extension rule: Same deposits don't grow connectors (reinforcement).
Different deposits grow connectors (new structure). Star-internal connectors
stay at initial length 2.9 — no inflation.

**Critical finding: star expansion is pure diffusion, not connector growth.**
With zero connector growth (Same rule active, internal length stable at 2.9),
the star STILL expands to r=14.5. The expansion that plagued v4-v11 was
NEVER caused by connector inflation. It's 80 nodes random-walking on a
finite graph, diffusing to fill ~70% of the volume.

The Same/Different rule works correctly but targets the wrong cause.

### v13: Accumulated density + Same rule + length momentum (April 2, 2026)

Three failed mechanisms combined: v6's density routing (now viable because
Same rule prevents denominator growth) + v12's Same/Different rule + new
length-proportional momentum (forward = L × arrival_dir).

**Results:** Gravity/forward ratio 63:1 — gravity massively dominates. But
the density gradient is INVERTED (d0-1=7.2, d4-5=12.1). Deposits are densest
where the nodes ARE (r=10-15 shell), not at the center. The gravity pulls
nodes toward the existing cloud, not toward the origin. Star r=14.4.

Planet: 10,124 total degrees, 753 net, 28.5 oscillations. Bound but
coherence 0.19 (random walk). The most angular motion of any version.

### v14: Larger graph, 50k nodes, R=80 (April 2, 2026)

Accepted star thermal equilibrium. Scaled graph to 50k nodes (R=80) so
star at r~14 would be only 18% of the universe. **Result: star expanded
to r=59 (73% of R=80).** The thermal equilibrium is SCALE-INVARIANT.
Star fills 73% of any graph regardless of size.

Coherence 0.27 — the best of any version. The larger graph gives the
planet more room for systematic angular motion. Hop rate flat at 0.019
regardless of distance (CHARGING_TIME=50 dominates). No Keplerian velocity.

Deep analysis revealed: deposit flux from star neighbors drops to ZERO at
r=20 (limited by rc=6.3). Gravitational reach is purely local.

### v15: Propagating deposits build connectors (April 2-3, 2026)

The synthesis of v5 (propagation) + v4 (ontology). Quanta propagate at c=1
hop/tick, depositing on every connector they traverse — BUILDING the
connector as they go. The photon creates the road.

**Result: 3 BILLION deposits saturated the graph.** Density flat (d0/d5=1.02).
Reactive charging works (99.996% quantum-triggered) but flux is uniform —
10,000 active quanta pass through every node every tick. No distance
dependence. Same=2.97B, Different=0 (all star-dominated, all Same).

### v16: Same consumes Different (April 3, 2026)

The consumption rule: Same deposits CONSUME one Different deposit on the
connector (reclassify Different->Same, reducing different_count). Connectors
can now SHRINK from Same traffic and GROW from Different traffic.

**Result: consumption IS working.** Consumed=19,148 > Different=8,318.
Star's Same deposits consume planet's Different deposits faster than the
planet creates them. Boundary connectors oscillate in length. 37 radial
oscillations (the most ever). But star still r=14, coherence 0.157.

### v17: Inter-group rotation + consumption (April 3, 2026)

Inter-group routing for internal circulation: s0 routes toward {s1,s2,s3}.
Intended to create a spinning star body instead of a diffusing cloud.

**Result: rotation didn't help.** Star r=14.1 (no improvement). The 4 groups
are spatially mixed in the diffuse cloud — no spatial separation means no
organized circulation. Net angular dropped to -14 degrees (near zero).
Rotation requires spatial group structure, which requires a compact star.

## Experimental Summary (v4-v17, March 31 - April 3, 2026)

### What's proven:
1. **Gravitational binding works.** Planet attracted and bound in every version v7+.
2. **Connector = deposits ontology is correct** (v4, confirmed through v17).
3. **Same/Different rule correctly models internal vs external** (v12+).
4. **Consumption (Same consumes Different) creates equilibrium distances** (v16-v17).
5. **Newton's first law is necessary** (v10 deadlock, v11 fix).
6. **Traversal time proportional to length creates time dilation** (v7).
7. **Star thermal equilibrium is scale-invariant at 73% volume fraction** (v12, v14).

### What doesn't work:
1. **No coherent orbits.** Best angular coherence: 0.27 (v14). Target: 0.3. All
   "orbits" are bound random walks (v9 diagnostic proved this definitively).
2. **Star won't compact.** Every version v4-v17 produces star r~14 on 5k graph,
   r~59 on 50k graph. Thermal diffusion is scale-invariant.
3. **Deposit fields saturate.** Any mechanism depositing on a finite graph eventually
   fills it uniformly (v6, v15). Gradients are temporary.
4. **Velocity is distance-independent.** Fixed charging time (v11-v14) or uniform
   flux (v15) makes hop rate constant. Keplerian v~1/sqrt(r) not achieved.

### Key theoretical insights:
1. **The graph doesn't move. What moves is statistics and visualization.**
   Entity "position" is the statistical center of its deposit pattern.
   "Movement" is the deposit pattern shifting through the connector network.
2. **The universe can only grow** (append-only). Connectors extend from Different
   deposits. The ONLY shrinkage is consumption (Same reclassifies Different).
   This means orbital mechanics must be a balance of growth and consumption.
3. **Aristotle was wrong** (v10). Motion doesn't need continuous energy input.
   Newton's first law (forward continuation) is necessary on the graph.
4. **The photon builds the road** (v15). Propagating deposits ARE the connector
   structure. The gravitational field is the accumulated radiation trail.
5. **If the star can transform everything, there is no planet.** The planet
   exists because the star's spectrum is incomplete. The planet IS what the
   star can't digest. (RAW 118 + trie_stream_filtering connection).

## Open Questions for Theory

1. **How does the tick-frame model represent the static gravitational field?**
   The model has accumulated deposits (historical) and propagating quanta
   (radiative). Neither is equivalent to a static field that reflects where
   mass IS right now. The gravitational field should be a property of the
   graph STRUCTURE (connector lengths, deposit density), not just the
   deposit HISTORY.

2. **Is the random geometric graph the right substrate?** The theory says
   space IS connections, and connections grow from deposits. Maybe the graph
   should GROW from entity activity, not be pre-built. Start with just the
   star cluster, expand as entities explore the frontier (Unknown).

3. **What IS movement in the model?** Entities hopping between fixed graph
   nodes is a simplification. The theory suggests movement = deposit pattern
   shifting through the graph. The graph doesn't move. Statistics move.
   Visualization is a projection of deposit statistics, not of node positions.

4. **Can the star compaction problem be solved, or is it thermodynamics?**
   80 nodes diffuse to 73% volume fraction on any graph. Is this correct
   physics (the star IS this diffuse) or a model limitation?

## Known Issues (Resolved)

1. ~~**Star core connector runaway.**~~ SOLVED in v4.
2. ~~**Planet placement.**~~ SOLVED in v8.
3. ~~**Connector inflation causes expansion.**~~ DISPROVED in v12.
4. ~~**Aristotle's deadlock.**~~ SOLVED in v11 (Newton's first law).

4. **Star fills 73% of any graph (v4-v14).** 80 nodes diffuse to fill ~73%
   of the graph volume. v14 proved this is scale-invariant: on a 50k-node
   graph (R=80), the star expanded to r=59 (73%). Same fraction as r=14
   on R=20. Larger graphs don't help. The star's thermal equilibrium is a
   fixed fraction of available volume, not a fixed absolute radius.

5. **Tangential motion is random walk (v9 diagnostic).** No version has
   produced coherent orbital motion (angular coherence > 0.3). The planet
   random-walks within the gravitational well. Forward default (v11+)
   increases angular displacement but doesn't make it coherent.

6. **No Kepler verification.** Blocked by issues 4 and 5.

---

## References

- RAW 111 — Space Is Connections
- RAW 112 — The Single Mechanism
- RAW 113 — The Semantic Isomorphism: Same / Different / Unknown
- RAW 118 — Gravity as Consumption and Transformation of Connectors
- RAW 126 — The Trit Is a Capacitor
- RAW 127 — The Trit Has Depth
- RAW 128 — The Energy Partition: Store, Move, or Radiate
- Experiment 64_109 CLOSURE — Results and lessons learned

---

## Closure

Experiment 118 is CLOSED. 17 versions, 4 days (March 31 - April 3, 2026).

The experiment answered its core question — "does gravity emerge from
consumption and transformation of deposits on connectors?" — with a
qualified YES. Gravitational binding (attraction + confinement) emerges
from every mechanism tested since v7. The planet is attracted to the star's
deposit field, oscillates radially, and cannot escape.

The experiment did NOT produce coherent Keplerian orbits. The v9 diagnostic
proved that all apparent orbital motion is a bound random walk on the graph.
Angular coherence peaked at 0.27 (v14), below the 0.3 threshold for
systematic rotation.

The deeper finding: **entity hopping on a graph is the wrong model of
movement.** The graph is the substrate. It doesn't move. What changes is
the deposit STATISTICS — which patterns dominate at each position. Movement
in the tick-frame model should be the statistical center of a deposit pattern
shifting through the connector network, not an entity teleporting between
graph nodes.

This insight motivates **Experiment 128** — testing the deposit-statistics
model of motion, where entities ARE patterns and movement IS statistical shift.

### What Experiment 118 contributed to the theory:
- RAW 128 (Energy Partition: Store, Move, or Radiate)
- The Same/Different extension rule (derived from RAW 113)
- The consumption mechanism (Same reclassifies Different)
- Aristotle's deadlock (v10) — proof that Newton I is necessary
- Star thermal equilibrium at 73% volume fraction (scale-invariant)
- The photon builds the road (propagating deposits create connectors)
- If the star can transform everything, there is no planet

### Superseded by: Experiment 128 (The Energy Partition)

---

*Date: March 21, 2026 (initial), April 3, 2026 (closure)*
*Author: Tom (theory), Claude (experiment design and implementation)*
*Status: CLOSED. Superseded by Experiment 128.*
