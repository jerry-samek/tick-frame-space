# Experiment 118 v4: Buffer-Driven Orbital Mechanics

## Status: READY FOR IMPLEMENTATION
## Date: March 31, 2026
## Author: Tom (theory), Claude (spec)

---

## Overview

v4 represents a fundamental architecture change from v1–v3. Previous versions
treated connectors as mutable state that entities consume from and modify. This
version enforces the append-only axiom strictly: **connectors are immutable
history. Deposits are only appended, never subtracted.** The orbital mechanism
is the production-consumption balance of an append-only buffer between star and
planet.

### Theory basis

- **RAW 112** — The Single Mechanism: deposit → hop → connector extends
- **RAW 113** — Same/Different/Unknown as the complete alphabet
- **RAW 118** — Gravity as consumption and transformation
- **RAW 126** — The trit is a capacitor: one discharge = one quantum = one deposit
- **RAW 127** — The trit has depth: charging phase, discharge event
- **RAW 125** — Reading direction: most recent deposits encountered first

### What v1–v3 got wrong

v1–v3 implemented consumption as subtraction from connectors:
```python
# v3 do_hop — WRONG: modifies connector history
c.dep[t] = amt - eaten            # subtracts from existing deposits
c.dep[tag] = c.dep.get(tag, 0.0) + eaten  # transforms in place
c.length *= (1 + EXTEND_RATE * diff_frac)  # parameterized extension
```
This violates the append-only axiom and requires three free parameters
(CONSUME_FRAC, EXTEND_RATE, DIFF_FRAC_MIN) that have no theoretical basis.

### What the trie_stream_filtering experiments showed

The v4–v10 trie experiments (now in `experiments/trie_stream_filtering/`)
demonstrated that consumption-rejection filtering produces gravitational
binding and hierarchical structure WITHOUT any force law. The root entity
(star) consumed matching patterns, rejected non-matching patterns, and
planets formed from the reject stream at equilibrium distances. v4 of that
line produced radial oscillation of bound planets (see planet_distance plot).

What was missing: no distinction between old and new deposits, so no
dynamic field response, so no tangential motion, so no orbits.

---

## Core Mechanic: One Quantum, One Tick, One Connector

### The single operation

Each node, each tick, performs exactly one operation:

1. **READ**: Examine deposits on all k connectors. For each connector, read the
   most recent deposits (the ones nearest to this node — RAW 125 reading
   direction). Compute a routing signal per connector.

2. **DECIDE**: Does any connector's deposit pattern match my spectrum?
   - **Same**: Yes — threshold reached, capacitor fires. Choose the connector
     with the strongest match (highest density of matching deposits).
   - **Different**: Deposits present but don't match. Capacitor charging.
     No discharge this tick. Node stays put.
   - **Unknown**: No deposits on connector. Nothing to evaluate.

3. **FIRE**: If Same was triggered:
   - Produce exactly **one quantum** (one deposit with the node's group tag)
   - Append it to the chosen connector (the one the node routes toward)
   - Hop to the neighbor at the other end of that connector
   - The connector's length increases by exactly 1 (one deposit appended)

4. **IDLE**: If no Same triggered this tick, the node does nothing. It sits and
   accumulates charge (the deposits continue arriving on its connectors from
   neighbors). Next tick, try again.

### What this means

- **No CONSUME_FRAC parameter.** There is no fractional consumption. The
  capacitor either fires (one quantum out) or doesn't (zero quanta out).

- **No EXTEND_RATE parameter.** Connector growth is exactly 1 unit per
  deposit appended. No compound growth. No scaling factor. The connector
  length IS the deposit count.

- **No DIFF_FRAC_MIN parameter.** There is no floor. If all deposits match,
  the extension from this hop is still exactly 1 (the node's own deposit).
  If none match, the node doesn't fire, doesn't hop, doesn't deposit.

- **No consumption-by-subtraction.** The connector's deposit history is never
  modified. Old deposits remain. New deposits are appended on top.

- **Connector length = total deposit count on that connector.** This is not
  a separate tracked value — it IS the number of deposits. One deposit = one
  unit of length. No other definition of "length" exists.

---

## The Connector as Buffer

The connector between two entities is a production-consumption buffer:

```
Star node → deposits star-pattern quanta → [CONNECTOR/BUFFER] → planet reads deposits
            (producer)                      (append-only queue)    (consumer)
```

### Buffer dynamics

- **Star produces** by depositing quanta onto connectors during internal
  Same-routing hops. Most deposits go onto internal star connectors, but
  star nodes at the boundary occasionally deposit onto outward-facing
  connectors (the "leak" — this is radiation).

- **The buffer grows** when the planet cannot consume deposits as fast as
  the star produces them. Unconsumed deposits pile up on the connector.
  The connector gets longer. The planet is physically pushed farther away
  because the buffer between it and the star has grown.

- **The buffer drains** (conceptually) when the planet consumes faster than
  the star produces. The planet's capacitors fire on the incoming deposits,
  and it deposits its own quanta onto the connector. The planet moves inward
  (the net routing signal pulls it toward the richer Same field).

- **Equilibrium distance** is where production rate = consumption rate. The
  buffer size is stable. The connector length is stable (only growing by
  the equal contribution from both ends). The planet neither falls nor
  retreats.

### Eccentricity from capacity mismatch

A small entity (few nodes, low consumption capacity) at close range receives
more flux than it can consume. Buffer overflows → pushed outward violently.
At aphelion, the flux is weak, the entity can consume it all, buffer
stabilizes. Once buffer is processed, the entity falls inward again.
**High eccentricity = low consumption capacity relative to peak flux.**

A massive planet (many nodes, high consumption capacity) at moderate range
can handle the incoming flux. Buffer barely fluctuates. Nearly circular
orbit. **Low eccentricity = high consumption capacity relative to local flux.**

This maps onto the solar system: Mercury (small, close, eccentric), Jupiter
(massive, moderate distance, low eccentricity), comets (tiny, extreme
eccentricity).

---

## Same/Different Routing — What Matches What

### Group structure

Entities belong to groups. Groups define the spectrum — what patterns the
entity's capacitors discharge on.

- **Star groups**: s0, s1, s2, s3 (4 groups for internal structure)
- **Planet groups**: p0, p1 (2 groups for internal cohesion)
- **Cross-group rules**:
  - Star groups are mutually Same (s0 matches s1, s2, s3 — they're all "star")
  - Planet groups are mutually Same (p0 matches p1)
  - Star and planet groups are mutually Different (s0 does NOT match p0)

### Routing signal

Each node reads its k connectors and computes a routing score for each.
The score should reflect the **recent** deposit composition, weighted by
density:

```
For node with spectrum S, examining connector C:

  matching_deposits = count of deposits on C whose group ∈ S
  total_deposits    = count of all deposits on C (= connector length)
  
  routing_score = matching_deposits / total_deposits
```

The node routes toward the connector with the highest routing_score —
the densest matching deposit field. This IS Same-routing. This IS gravity.

### The "recent deposits" question

The connector is append-only. Old deposits are buried under new ones. The
entity reads from its end of the connector (RAW 125 reading direction).

For v4 Phase 1: use the **full** deposit composition (total matching / total
length). This is the simplest implementation and already produced radial
oscillation in the trie_stream_filtering v4 experiment.

For v4 Phase 2 (if Phase 1 shows only radial oscillation): introduce a
**read window** — the entity only reads the most recent W deposits on each
connector. This makes routing responsive to the star's instantaneous
asymmetry, which is what should generate tangential motion. W could be
proportional to the entity's node count (mass = receptor count, RAW 124).

**Do NOT introduce exponential decay or any time-based weighting.** The
temporal filtering should come from the read window or from the connector
growth itself, not from an added decay parameter.

---

## Star Radiation: Why the Star Leaks

The star doesn't have an explicit radiation mechanism. The leak emerges
from the internal dynamics:

1. Star nodes route toward the richest Same field (inward, toward other
   star nodes).

2. At the center, all connectors are saturated with star deposits. No
   gradient exists. Nodes hop randomly.

3. Random hops occasionally take nodes to the boundary, where they deposit
   onto outward-facing connectors.

4. Those outward deposits are the star's "radiation" — the reject stream
   in trie_stream_filtering terms.

5. The radiation rate is NOT a parameter. It emerges from the star's
   internal dynamics: the fraction of nodes at the boundary × the fraction
   of their hops that go outward × the deposit per hop (= 1 quantum).

6. **Critical: as the star grows internally (all internal connectors
   growing from traffic), the deposit density drops, capacitors charge
   slower, discharge rate drops. This is gravitational time dilation.**
   The star's internal clock slows down as it ages. The radiation rate
   changes over time. This is not a bug — it's the theory.

---

## ⚠️ TRAPS FROM v1–v3 (DO NOT REPEAT)

All traps from the main `experiment_description.md` still apply. In addition:

### Trap 8: Consumption by Subtraction
v1–v3 modified connector deposit state by subtracting consumed deposits.
**Do NOT subtract from connectors. Append only.**

### Trap 9: Parameterized Extension
v1–v3 used EXTEND_RATE, DIFF_FRAC_MIN, compound growth formulas.
**Connector length = deposit count. Period. No extension parameters.**

### Trap 10: All-At-Once Deposit
Do not deposit onto ALL connectors per hop. One quantum, one connector,
one tick. This is the one-quantum-per-tick-per-node constraint from
RAW 126 (trit as capacitor — one discharge per cycle).

### Trap 11: Treating the Buffer as State to Manage
The connector/buffer should not be "managed" — no garbage collection, no
pruning, no cleaning of old deposits. The buffer IS append-only history.
The only operation is: append one deposit when a node fires.

### Trap 12: External Stream
v4 of the trie_stream_filtering experiment used an external random stream
as input. The orbital mechanics experiment should NOT have an external
stream. The star's own deposits ARE the stream. The "input" is the star's
internal dynamics radiating outward. No external token generator.

---

## Implementation Phases

### Phase 0: Graph and Data Structures

Build the graph substrate. Define the connector as an append-only structure
with efficient tracking of deposit composition by group.

**Implementation note on connector representation:**

Tracking every individual deposit on every connector is memory-expensive.
An efficient approximation: each connector tracks `{group: count}` for
total deposits, and optionally `{group: count}` for recent deposits
(last W ticks). The connector length is `sum(all counts)`. This loses
ordering information but preserves composition and density.

```python
class Connector:
    """Append-only buffer between two nodes."""
    
    def __init__(self, initial_length):
        self.initial_length = initial_length  # geometric distance (graph construction)
        self.deposits = {}   # {group_tag: count} — total deposits by group
        self.total = 0       # total deposit count
    
    @property
    def length(self):
        """Length = initial geometric distance + total deposits appended."""
        return self.initial_length + self.total
    
    def append(self, group_tag):
        """Append one quantum. The only mutation operation."""
        self.deposits[group_tag] = self.deposits.get(group_tag, 0) + 1
        self.total += 1
    
    def matching_density(self, spectrum):
        """Deposit density of groups matching the given spectrum."""
        matching = sum(v for k, v in self.deposits.items() if k in spectrum)
        return matching / self.length if self.length > 0 else 0.0
    
    def foreign_density(self, spectrum):
        """Deposit density of groups NOT matching the spectrum."""
        foreign = sum(v for k, v in self.deposits.items() if k not in spectrum)
        return foreign / self.length if self.length > 0 else 0.0
```

### Phase 1: Star Equilibrium (NO PLANET)

**Goal:** Demonstrate that a distributed star cluster reaches internal
equilibrium using only the one-quantum-per-tick mechanic.

**Setup:**
- Graph: random geometric graph, N=5000 nodes, k≈24, sphere radius=20
- Star: 80 nodes placed near origin, 4 groups (s0–s3)
- Star spectrum: {s0, s1, s2, s3} — all star groups are mutually Same
- No planet. Star only.
- Run for 50,000 ticks minimum.

**Each tick, each star node:**
1. Read all k connectors. Compute matching_density(star_spectrum) for each.
2. Choose the connector with highest matching density.
   - Tie-breaking: random among tied connectors.
   - If ALL connectors have zero matching deposits: hop to random neighbor.
3. Append one quantum (the node's group tag) to the chosen connector.
4. Hop to the neighbor at the other end.

**Measurements (every 500 ticks):**
- Star center of mass (COM) position
- Star mean radius (mean distance of star nodes from COM)
- Star max radius
- Mean connector length for star-internal connectors (both endpoints are
  star nodes)
- Max connector length for star-internal connectors
- Mean connector length for star-boundary connectors (one endpoint is star,
  one is non-star)
- Total deposits on boundary connectors (the "radiation" — deposits leaking
  outward)
- Discharge rate: how many star nodes actually fired this tick (vs idled)

**Success criteria:**
1. Star COM stays approximately stationary (drift < 2 units over full run)
2. Star mean radius stabilizes (σ < 15% of mean over last 20k ticks)
3. Star internal connectors grow, but at a BOUNDED rate — no runaway to
   1e6+ lengths. Growth should be roughly linear in time (one deposit per
   hop, bounded by star traffic), not exponential.
4. Star boundary connectors accumulate deposits (evidence of radiation)
5. Discharge rate eventually stabilizes (the star reaches a quasi-steady
   internal state)

**If this fails:** The star collapse/explosion problem is NOT the extension
bug from v1–v3 (there is no extension parameter to bug). It would indicate
a routing problem. Debug the routing signal before proceeding.

### Phase 2: Planet Introduction — Radial Binding

**Goal:** Introduce a planet and demonstrate radial gravitational binding
via the buffer mechanism.

**Setup:**
- Same graph as Phase 1
- Star: 80 nodes, pre-equilibrated from Phase 1 (run Phase 1 first, then
  introduce planet without resetting)
- Planet: 5–10 nodes, placed at distance ~2× star mean radius from star COM
- Planet groups: p0, p1
- Planet spectrum: {p0, p1} — planet groups are mutually Same
- Zero initial velocity
- Run for 50,000+ ticks after planet introduction

**Planet node tick operation:**
Same as star nodes, but with planet spectrum. Each planet node:
1. Read all k connectors. Compute matching_density(planet_spectrum).
2. Choose highest matching density connector.
3. If no matching deposits anywhere: look for FOREIGN deposits instead
   (the star's deposits). Route toward the highest foreign_density.
   **This is the gravitational attraction** — the planet routes toward
   the star's deposit field because it's the richest source of ANYTHING
   in an otherwise empty graph. Even Different deposits trigger charging.
   The planet moves toward them because moving toward deposits is better
   than sitting in Unknown.
4. Append one quantum (planet group tag) onto the chosen connector.
5. Hop.

**CRITICAL ROUTING QUESTION:**

What does the planet route toward? Two candidates:

(a) **Matching deposits** — the planet routes toward its own deposits
    (planet-pattern). But initially, the planet hasn't deposited much.
    The star's deposits dominate. The planet would route toward star
    deposits by default (they're the only non-zero signal).

(b) **Any deposits vs Unknown** — the planet routes toward ANY deposits
    over no deposits. It prefers Same deposits if available, but will
    move toward Different deposits over Unknown because Different at least
    means "something is here" while Unknown means "frontier."

Option (b) is more physically grounded in the capacitor model: deposits
arrive and charge the capacitor regardless of whether they match the
spectrum. The capacitor charges from ANY deposits. It only FIRES on
matching deposits. But routing toward deposits is about charging the
capacitor — you move toward the source of charge, regardless of whether
you'll fire on it.

**Recommended: use option (b)** — route toward highest total deposit
density (any group), with a preference for matching deposits:

```
routing_score = (matching_density * MATCH_WEIGHT + total_density) / length
```

Actually, even simpler: route toward highest total_density. Don't weight
matching vs foreign. The planet goes where the deposits are. It will
naturally approach the star because that's where the deposits are densest.

When it gets close and the star's deposits overwhelm its capacity (buffer
fills), the connector grows, pushing it back. This is the buffer mechanism.

**Measurements (every 200 ticks):**
- Planet COM distance from star COM
- Planet COM velocity (derived from position change)
- Planet mean radius (cohesion)
- Buffer status: total deposits on connectors between star and planet
  surface nodes
- Star radiation rate: deposits per tick on boundary connectors

**Success criteria:**
1. Planet moves toward star (attraction works)
2. Planet reaches minimum distance and bounces back (buffer overflow)
3. Planet oscillates radially (bound state, not escape)
4. Oscillation period is roughly stable (not chaotic)
5. Equilibrium distance correlates with planet size (more nodes = closer
   equilibrium, because higher consumption capacity)

### Phase 3: Tangential Velocity — The Orbit

**Goal:** Demonstrate that tangential motion emerges or can be seeded,
producing a quasi-orbit.

**Two approaches — try both:**

**3a: Seeded tangential velocity.** Give the planet an initial velocity
perpendicular to the radial direction. The planet starts at the Phase 2
equilibrium distance with v_tangential = some fraction of v_radial_max
(the max radial velocity observed in Phase 2). See if the radial
oscillation rotates into a 2D orbit.

**3b: Emergent tangential velocity (Phase 2 with read window).** If
Phase 2 shows only radial oscillation, introduce the read window (W)
so the planet reads only recent deposits. The star's instantaneous
asymmetry should provide tangential nudges. Track angular momentum
over time.

**Measurements:**
- Full 2D (or 3D) trajectory of planet COM
- Radial velocity and tangential velocity decomposition
- Angular momentum L = r × v_tangential over time
- Cumulative angle (revolutions)
- Orbital period (if orbit exists)
- Trajectory shape: fit ellipse, measure eccentricity

**Success criteria:**
1. Tangential velocity is nonzero and sustained (not just noise)
2. Planet traces a 2D trajectory (not purely radial)
3. Angular momentum is at least quasi-conserved (doesn't fluctuate more
   than ±50% around its mean)
4. The trajectory resembles a (possibly precessing) ellipse

### Phase 4: Quantitative Verification (STRETCH)

Only after Phase 3 succeeds.

**Goal:** Compare simulation results to known physical relationships.

**Tests:**
1. **Force vs distance.** Measure the "force" (acceleration) on a test
   particle at various distances from the star. Plot force vs distance.
   Check for 1/r² or identify the actual scaling law.

2. **Kepler's third law.** If multiple stable orbits exist (different
   initial conditions), measure T² vs r³. Check proportionality.

3. **Energy conservation.** Define kinetic energy (½mv²) and potential
   energy (some function of distance). Check if total energy is
   approximately conserved over one orbit.

4. **Angular momentum conservation.** Already measured in Phase 3.
   Quantify the conservation quality.

**The key test (Tom's criterion):** Can ANY quantitative relationship
be derived from the mechanism without fitting parameters? If the force
scaling, orbital period, or equilibrium distance can be predicted from
the star's node count, planet's node count, and graph connectivity
alone — without tuning — that's the threshold for this being physics
rather than a simulation framework.

---

## Parameters

v4 has deliberately fewer parameters than v1–v3:

| Parameter | Value | Justification |
|-----------|-------|---------------|
| N_NODES | 5000 | Same as v1–v3, adequate graph size |
| SPHERE_R | 20.0 | Same as v1–v3 |
| TARGET_K | 24 | Same as v1–v3, sufficient connectivity |
| STAR_COUNT | 80 | Distributed mass, same as v1–v3 |
| STAR_GROUPS | 4 | Internal structure for circulation |
| PLANET_COUNT | 5–10 | Multi-node for receptor count, smaller than star |
| PLANET_GROUPS | 2 | Internal cohesion |

**Eliminated parameters:**
- ~~CONSUME_FRAC~~ → no fractional consumption (capacitor fires or doesn't)
- ~~EXTEND_RATE~~ → connector length = deposit count (no rate)
- ~~DIFF_FRAC_MIN~~ → no floor (append-only eliminates the bug)
- ~~DAMPING~~ → no artificial damping (energy dissipation comes from
  depositing quanta onto connectors — each hop converts kinetic energy
  into connector growth)
- ~~FORCE_INTERVAL~~ → routing is evaluated every tick (each node makes
  its own routing decision independently)
- ~~HOP_FLOOR_FACTOR~~ → no hop threshold (the node either fires and
  hops, or it doesn't fire and stays)
- ~~WARMUP parameter~~ → still need warmup period for star equilibration,
  but it's Phase 1 of the experiment, not a magic number
- ~~H~~ → no global expansion (was already 0 in v3)

**Remaining free parameters:** STAR_COUNT, PLANET_COUNT, graph connectivity.
These have physical meaning (mass of each body, local dimensionality of
space). They are not tuning knobs — they define the physical setup.

**One potential new parameter:** READ_WINDOW (W) — how many recent deposits
the entity reads per connector. Only introduced in Phase 3b if needed.
Physical interpretation: receptor count ∝ entity mass (RAW 124).

---

## Momentum and Velocity

v1–v3 used an explicit velocity vector with inertia and force calculations.
v4 should attempt **pure routing first** — no velocity, no momentum, no
force computation. The entity simply hops toward the highest-density
connector each tick. Its "velocity" is an emergent property of how many
hops it makes and in what direction.

**Problem:** pure routing is noisy. A 10-node planet cluster with each
node independently routing will disperse quickly — nodes hop in different
directions based on local gradients.

**Solution options (in order of preference):**

1. **Shared routing decision.** Compute the routing signal at ALL planet
   nodes, average the direction, and have all nodes hop in the averaged
   direction. This is what v2–v3 did (PlanetCluster with shared momentum).
   It's a simplification but keeps the planet coherent.

2. **Internal binding.** Planet nodes route toward each other (mutual Same
   deposits) AND toward the star (Different/total deposit field). The
   internal Same-routing keeps them bound as a cluster. The external
   routing moves the cluster as a unit. This is more physically correct
   but harder to implement — the planet must be self-binding before it
   can orbit.

3. **Post-hoc tracking.** Let planet nodes move independently. Track the
   center of mass. If the cluster stays coherent (mean radius stays
   bounded), the COM trajectory IS the orbit. If the cluster disperses,
   internal binding is needed.

**Recommendation:** Start with option 3 (independent routing, track COM).
If the cluster disperses within the first 5000 ticks, switch to option 1
(shared routing). Option 2 is the correct physics but may need the star
equilibrium to be solved first.

---

## What This Experiment Does NOT Attempt

- No float velocity vectors (unless option 1 shared routing is needed)
- No force law (force is implicit in routing)
- No global expansion (H = 0, always was)
- No external stream (the star's radiation IS the stream)
- No consumption-by-subtraction (append-only connectors)
- No parameterized extension (length = deposit count)
- No decay factor (temporal filtering from connector growth or read window)
- No predetermined orbital mechanics (Kepler's laws are a test, not input)

---

## Expected Outcomes

### If it works:
- Radial binding (Phase 2) should reproduce the oscillation already seen
  in trie_stream_filtering v4, but now on an explicit graph substrate
  with growing connectors
- Tangential motion (Phase 3) would be new — never achieved in any
  experiment version
- If orbits emerge, the force scaling and orbital period are genuinely
  derived quantities — not fitted

### If it fails:
- **Star doesn't equilibrate:** The routing signal (matching_density /
  length) doesn't produce stable internal dynamics. May need a different
  routing metric.
- **Planet doesn't bind:** The buffer mechanism doesn't create enough
  attraction. The total_density signal may be too weak at the planet's
  initial distance.
- **Planet falls in and stays:** The buffer overflow mechanism doesn't
  push the planet out. May need the read window to make routing
  responsive to recent deposits rather than accumulated history.
- **Cluster disperses:** Internal Same-routing isn't strong enough to
  keep the planet coherent. Need shared routing (option 1).

**All failure modes are informative.** Document them as carefully as
successes.

---

## Connection to the Broader Theory

If this experiment produces stable quasi-orbits from the buffer mechanism:

1. It validates RAW 118 (gravity as consumption-transformation) on the
   graph substrate
2. It validates the append-only axiom as sufficient for orbital mechanics
   (no subtraction needed)
3. It validates RAW 126's one-quantum-per-tick constraint as producing
   physically meaningful dynamics
4. The equilibrium distance, orbital period, and force scaling become
   derived quantities that can be compared against Newtonian predictions
5. The precession rate (if orbits precess) becomes a prediction distinct
   from both Newton and GR

If it fails, the failure mode tells us which theoretical assumption
breaks first.

---

## File Structure

```
v4/
├── README.md              (this file)
├── phase1_star.py         (star equilibrium — run first)
├── phase2_binding.py      (planet introduction — run after phase1)
├── phase3_orbit.py        (tangential velocity test)
├── phase4_kepler.py       (quantitative verification — stretch goal)
└── results/
    ├── phase1_results.csv
    ├── phase1_results.png
    ├── phase2_results.csv
    ├── phase2_results.png
    ├── phase3_results.csv
    ├── phase3_results.png
    └── ...
```

**Runtime notes:**
- Use `PYTHONUNBUFFERED=1` or `python -u` for all runs (unbuffered output)
- Phase 1 may need 50k+ ticks — expect 10+ minutes at ~1000 t/s
- Log every 500–1000 ticks for progress visibility
- Save intermediate state (star node positions, connector deposits) after
  Phase 1 so Phase 2 can resume without re-running warmup

---

*Supersedes: v1–v3 (which used consumption-by-subtraction and parameterized extension)*
*Related: trie_stream_filtering v4–v10 (validated the consumption-rejection mechanism on linear streams)*
*Key theoretical insight: the connector is a buffer. Orbital distance is where production = consumption. Eccentricity is capacity mismatch.*
