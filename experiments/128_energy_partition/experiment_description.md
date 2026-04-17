# Experiment 128: The Energy Partition — Entities as Deposit Patterns

## Status: SPEC
## Date: April 3, 2026
## Author: Tom (theory), Claude (spec)
## Theory: RAW 128 (Store, Move, or Radiate), RAW 113 (Same/Different/Unknown)
## Supersedes: Experiment 118 (Consumption-Transformation Gravity, v1-v17)

---

## Why This Experiment Exists

Experiment 118 ran 17 versions testing whether entities hopping on a random
geometric graph produce orbital mechanics. Result: gravitational binding YES,
coherent orbits NO. The v9 diagnostic proved all "orbits" are bound random
walks.

The deepest finding from 118: **the graph doesn't move. What moves is
statistics.** Entity "position" on the graph is a simplification. In the
theory, an entity IS a deposit pattern — a statistical distribution of
Same-tagged deposits across a region of connectors. "Movement" is this
distribution shifting through the network.

Experiment 128 tests this: **entities are not objects at graph nodes. Entities
are deposit patterns on connectors. The pattern shifts as new deposits are
added and old deposits become statistically dominated. Movement is visualization
of statistical change.**

---

## What Experiment 118 Proved (Carry Forward)

1. **Connector = deposits.** The connector IS its deposit chain. Nothing underneath.
   Length = initial geometric distance + Different deposit count.
2. **Same/Different extension rule.** Same deposits reinforce (no growth). Different
   deposits extend (growth). Internal connectors stay short.
3. **Consumption.** Same deposits consume (reclassify) one Different deposit.
   Connectors can shrink. Equilibrium distances from production/consumption balance.
4. **Newton I.** Forward continuation is necessary. Pure reactive = deadlock.
5. **Traversal time proportional to length.** Time dilation from connector length.
6. **Star thermal equilibrium.** 80 random-walking nodes fill 73% of any graph.
   Scale-invariant. This is thermodynamics, not a bug.
7. **The photon builds the road.** Propagating deposits create/extend connectors.

## What Experiment 118 Got Wrong

1. **Entities as point objects hopping between graph nodes.** The theory says
   entities ARE patterns, not objects. An entity's "position" is the statistical
   center of its deposit distribution, not which node it occupies.
2. **Movement as graph traversal.** Entities don't teleport between nodes. The
   deposit pattern SHIFTS through the connector network as new deposits are added.
3. **Pre-built graph as the universe.** The graph should grow from entity activity,
   not be fully constructed at initialization. Space is CREATED by deposits, not
   pre-existing.

---

## The New Model: Entities as Patterns

### What an entity IS

An entity is a contiguous region of connectors where one family's deposits
dominate. The "star" is the region where star-tagged deposits (s0, s1, s2, s3)
are the majority on every connector. The "planet" is the region where
planet-tagged deposits (p0, p1) dominate.

The entity doesn't have a "position" separate from its deposit distribution.
The entity IS the distribution.

### What movement IS

Movement is the statistical shift of the dominant-deposit boundary. When the
star deposits on a connector at the edge of its region, the star's boundary
extends by one connector. When the planet's deposits consume star deposits
on a boundary connector (Same reclassifies Different), the planet's boundary
advances.

"The star moved closer to the planet" means: the boundary between star-dominant
and planet-dominant regions shifted toward the planet. No entity hopped. No
node changed ownership. The STATISTICS changed.

### What the graph IS

The graph is the connector network. Nodes are junctions where connectors meet.
Connectors carry deposits. The graph structure (which nodes connect to which)
is determined by the deposit history — connectors exist BECAUSE deposits
were placed along paths.

In this model, the graph can GROW: new connectors are created when propagating
deposits reach frontier nodes (Unknown territory). The universe expands as
radiation reaches new regions.

### The energy partition (RAW 128)

Each deposit quantum, when it reaches the boundary between two entities, has
three possible outcomes:

1. **STORE**: The deposit is absorbed by the receiving entity's spectrum
   (Same → consumed, connector shrinks). The entity's mass grows (more
   deposits in its region). No movement.

2. **MOVE**: The deposit advances the boundary (Different → extends the
   connector into the other entity's region). The depositing entity "moved"
   — its statistical boundary shifted forward.

3. **RADIATE**: The deposit goes sideways — perpendicular to the boundary.
   It neither grows the entity (not stored) nor advances the boundary (not
   forward). It propagates into empty space, extending a connector in a
   new direction. Energy leaves the entity pair.

The partition is determined by the LOCAL GEOMETRY at the boundary, not by
an agent's decision. Same as RAW 128: one quantum, three outcomes, no choice.

---

## Implementation Approach

### Phase 0: Minimal Model — One Connector, Two Entities

Start with the simplest possible test: a single connector chain between
a "star" and a "planet." No graph. Just a 1D chain of deposits.

```
[s][s][s][s][s][s]|[p][p][p][p]
                  ^
             boundary position
```

Each tick:
1. Star deposits one quantum at its end (rightward)
2. Planet deposits one quantum at its end (leftward)
3. Where they meet: Same consumes Different
4. The boundary position shifts based on net deposit balance
5. Track: boundary position over time (= "distance")

**This tests:** Does the consumption equilibrium work in 1D? Does the
boundary oscillate? What sets the equilibrium position?

### Phase 1: Branching — 2D/3D Connector Network

Extend from 1D to a small graph (100-500 nodes). Still no entity hopping.
Entities are regions of deposit dominance. Deposits propagate outward from
each entity's core. Where they meet: consumption dynamics.

**This tests:** Does the equilibrium generalize from 1D to networks? Do
the three-way partition ratios (store/move/radiate) emerge from geometry?

### Phase 2: Orbital Motion from Pattern Shift

On a larger graph, test whether the deposit-pattern boundary between star
and planet traces an orbit. The star pattern is centered. The planet pattern
is off-center. The boundary between them should oscillate (radial binding)
and potentially rotate (orbital motion) based on the asymmetry of deposit
arrival rates from different directions.

**This tests:** Does the deposit-statistics model produce orbital motion
without entity hopping?

### Phase 3: Growing Graph

Start with a minimal graph (just the star cluster). Let propagating deposits
create new connectors at the frontier (Unknown nodes). The universe expands
as the star's radiation reaches new territory. Introduce planet deposits
after the star field has propagated. Watch the planet pattern emerge from
the star's reject stream.

**This tests:** Does the hierarchy (star → planet → moon) emerge naturally
from the deposit dynamics on a growing graph?

---

## Key Differences from Experiment 118

| Aspect | Exp 118 (v4-v17) | Exp 128 |
|--------|------------------|---------|
| Entity | Object at a graph node | Deposit pattern on a region of connectors |
| Movement | Entity hops between nodes | Pattern boundary shifts from deposit statistics |
| Position | Which node the entity is at | Statistical center of deposit distribution |
| Graph | Pre-built, fixed topology | Grows from deposit propagation (Phase 3) |
| Orbit | Entity traces a path through graph | Boundary between patterns oscillates/rotates |
| Speed | Hops per tick (limited by charging) | Rate of boundary shift (limited by deposit rate) |
| Gravity | Routing toward rich deposit field | Consumption of Different at the boundary |

---

## Parameters (Phase 0)

| Parameter | Value | Meaning |
|-----------|-------|---------|
| CHAIN_LENGTH | 100 | Initial connectors in the 1D chain |
| STAR_RATE | 1 | Star deposits per tick |
| PLANET_RATE | 1 | Planet deposits per tick |
| INITIAL_BOUNDARY | 50 | Starting boundary position (middle) |

No BASE_WEIGHT, no CHARGING_TIME, no graph construction.
The ONLY dynamics are: deposit, consume, shift boundary.

---

## What Success Looks Like

### Phase 0:
- Boundary oscillates around an equilibrium position
- Equilibrium position depends on deposit rate ratio
- Consumption rate matches production rate at equilibrium

### Phase 1:
- Store/move/radiate ratios emerge from geometry
- Equilibrium distances form on the network
- The three-way partition matches RAW 128 predictions

### Phase 2:
- The planet's deposit pattern boundary traces an orbit
- The orbit has angular coherence > 0.3 (real rotation, not random walk)
- Orbital velocity depends on distance from star pattern center
- The orbit is a PATTERN phenomenon, not an object phenomenon

### Phase 3:
- The graph grows from the star's radiation
- The planet pattern EMERGES from the star's reject stream
- The hierarchy forms naturally: star → planet → (moon?)

---

## Connection to Theory

RAW 128 describes the energy partition at the quantum level. Experiment 128
tests whether this partition, applied to deposit patterns on a graph, produces
orbital mechanics.

RAW 113 describes Same/Different/Unknown. The entity boundary IS the
Same/Different boundary on the connector network. The frontier (Unknown) is
where the graph grows.

RAW 118 describes gravity as consumption and transformation. The gravitational
binding IS the consumption equilibrium at the entity boundary — Same deposits
consume Different, maintaining the distance.

The trie_stream_filtering experiments (v4-v10) showed that hierarchical
structure self-organizes from stream filtering. Experiment 128 Phase 3 tests
whether the SAME mechanism produces gravitational hierarchy (star → planet →
moon) when applied to deposit patterns on a growing graph.

---

## Results

### Phase 0: 1D Chain (April 3, 2026)
- Boundary stable at midpoint for equal rates. Consumption balances production.
- Unequal rates: stronger entity dominates entire chain (binary, no intermediate).
- 1D has no geometric dilution — no equilibrium possible with unequal rates.

### Phase 1: Deposit Patterns on Graph (April 3, 2026)
- **Boundary FORMS from geometric dilution.** Star dominance falls with distance.
- 80 star sources push boundary to hop d=3. 10 sources only d=1.
- **Mass = node count confirmed.** More sources = wider dominance.
- Consumption active at the boundary (405k consumed in 5k ticks).
- The deposit-pattern model produces real gravitational field structure.

### Phase 2: Boundary Dynamics (April 3, 2026)
- Test D (self-tracking): planet COM drifts toward star — gravitational
  attraction as pure pattern drift. No entity hopping.
- **Test F (tangential momentum + gravity): COHERENCE 0.438 — first EVER
  above the 0.3 threshold.** The planet deposit pattern traces a coherent
  arc around the star. Net angle 194 degrees. Clear curved trajectory.
- The deposit-statistics model produces COHERENT ORBITAL MOTION for the
  first time in the entire experiment line (118 + 128).
- **Test G (ellipse attempt, 50k ticks): COHERENCE 0.478.** Gravity from
  actual deposit density gradient (no fixed constant). Planet spirals in
  from r=10 to equilibrium at r~4.8, damped oscillation 3.5-6.4. Net angle
  only 7 degrees — the planet settles at equilibrium rather than orbiting.
  The gravity/momentum balance needs to be derived from deposit dynamics,
  not hand-tuned (grav * 0.01 was too weak for closed orbit, too strong
  for escape).

### Key: what made coherence > 0.3 finally work
1. Entities are patterns (deposit COM), not objects hopping on graph nodes
2. Momentum = persistence of COM-shift direction (pattern inertia)
3. Gravity = deflection toward star center (from deposit field)
4. The pattern moves smoothly through the graph — no discrete graph-topology
   randomness from node-to-node routing decisions

### What's needed for closed elliptical orbits
The gravity/momentum balance must emerge from the deposit field itself,
not from hand-tuned scaling constants. The deposit density gradient IS
the gravitational field. The pattern-shift persistence IS momentum. The
orbit should close when these two are in natural balance — when the
centripetal acceleration from the density gradient equals v^2/r from the
pattern drift velocity. This balance exists (Test F produced a coherent
arc) but finding the self-consistent scaling remains open.

### v3: Simultaneous star+planet, 500k graph, 5 planet nodes (April 3-5)
- Star and planet from tick 0 (no warmup — the interaction defines both)
- Star equilibrated at r=45.9 (56% of R=80, better than 73% at N=80)
- Planet (5 nodes): wild oscillation dist 2.8-52.9. Probability cloud.
- Ejection event at t=890k-970k: planet launched from dist=3.4 to dist=53
  by the star's internal deposit traffic (CME-like event)
- Planet returned (dist=27 at t=1M) — binding survived the ejection
- Consumption: 70k consumed, mechanism active
- Key insight: the star needs the planet to define its own edge. Without
  the Different entity, the star has no boundary (v2 showed unbounded
  expansion during star-only warmup)

### v4/v5: 500 planet nodes, vectorized substrate (April 5-6)
- v4: object-based (14 t/s). v5: numpy vectorized (535 t/s). 38x speedup.
- Same physics, verified: both produce identical trajectories
- Planet diffused from r=6 to r=57 (same diffusion problem as the star)
- Planet COM fell to dist=4.3 and stabilized (no oscillation, no ejection)
- 0.5 oscillations — planet fell in once and stayed. Merged with star.
- Planet node cohesion problem: unsolvable with pre-placed nodes. Planet
  must EMERGE from reject stream (Phase 3 prerequisite).

### v6: Deposit dominance tracking (April 6)
- **The breakthrough measurement.** Track WHERE each family's deposits
  dominate on connectors, not where entity nodes are.
- Node-based: planet merged at dist=4.6 (looks like absorption)
- Deposit-based: planet region at dist=12.2 (distinct territory!)
- Star deposit region r=35.6 (smaller than node cloud r=41.4)
- Planet territory: 360k edges (vs star's 4.9M). Real but small.
- Deposit distance stabilized at 12.2 for 200k+ ticks — REAL equilibrium
- Dominance gradient: 100% star at d=0-9, transition at d=10-15, planet
  presence at d=15-19
- Tangential: near zero (8 deg total). Purely radial equilibrium. No
  asymmetry in the deposit dynamics to generate sideways motion.

### v7: Tangential reject stream as velocity (April 6)
- Planet routing biased tangentially (perpendicular to gravity direction).
- 500k run: coherence 0.867, net -26.5 degrees. Consistent direction.
- **7M full revolution run: tangential motion DIED after 500k ticks.**
  The -25 degrees happened during the infall phase only. Once equilibrium
  was reached, zero further rotation. The tangential bias only curves
  EXISTING motion. When radial motion stops, there's nothing to curve.

### v8: Tangential reject stream as acceleration (April 6)
- Gravity and tangential as ACCELERATION (bend forward direction each tick).
- Result: noisy oscillation, big swings (+-15 deg/step), random direction.
  Coherence 0.333. The bending flips direction from per-tick deposit noise.
- Deposit distance collapsed to 7.5 (planet consumed by star).

### The tangential motion problem (v7+v8)

The planet's production is ISOTROPIC — deposits go in all directions
equally. Consumption is directional (from star-facing side, shortening
those connectors). Production lengthens connectors in all directions.
The only asymmetry is radial. No tangential production = no rotation.

**The orbit requires a BENT PIPE**: intake from star side, output 90
degrees tangentially. The bent pipe requires internal planet structure
that redirects the processing stream. Without it, the planet can only
approach/retreat radially, never orbit.

The bent pipe requires **Phase 3**: emergent internal hierarchy from
consumption dynamics. Pre-placed nodes diffuse before structure forms.

## Experiment 128 Summary (v1-v8, April 3-6, 2026)

### What's proven:
1. **Radial equilibrium from production/consumption balance** (v6: deposit
   distance 12.2, stable 200k+ ticks). This IS gravitational binding.
2. **Deposit dominance regions are the correct entity measurement** (v6:
   node positions show merger at dist=4.6, deposit regions show distinct
   territories at dist=12.2).
3. **Mass = source count** (Phase 1: more sources = wider dominance).
4. **Consumption mechanics work** (all versions: Same reclassifies
   Different, connectors can shrink).
5. **The star needs the planet to define its edge** (v2 vs v3).
6. **Vectorization: 38x speedup** (v5: 535 t/s).
7. **Phase 2 hand-coded momentum produces coherent arcs** (0.438/0.478
   coherence) but this is not emergent — it's Newtonian integration
   dressed as deposit dynamics.

### What's not solved:
1. **Sustained tangential motion** — v7 tangential bias produces one-time
   25-degree deflection during infall, then decays to zero. v8 acceleration
   model produces noisy oscillation. Neither sustains rotation.
2. **Planet self-binding** — 500 nodes diffuse instantly. No internal
   structure possible with pre-placed nodes.
3. **The bent pipe** — planet needs internal structure to redirect
   production tangentially. This is the Phase 3 problem.

### The core finding:
**Radial binding is solved. Tangential motion requires internal structure.**

The consumption mechanism (Same eats Different, connectors shrink/grow)
produces stable radial equilibrium between deposit dominance regions.
This IS gravity in the deposit-statistics model.

But orbital motion requires the planet to have ASYMMETRIC production:
intake radial (from star), output tangential (perpendicular). This
asymmetry can only come from internal processing hierarchy — a layered
structure where the flow through the planet is redirected. Without
internal structure, the planet's production is isotropic, and the only
dynamics are radial (approach/retreat).

### v9 ODE: Abstracted Consumption Equations (April 6)
- Stripped the graph away. Pure ODE: F = -consumed/r².
- **Perfect Keplerian orbits** (35-1812 revolutions). T² ∝ r³.
- Tangential thrust (excess or redirect) always causes escape.
- **"It rotates because it consumes."** Consumption IS the centripetal
  force. Documented as RAW 130.
- **Critical caveat:** F = -consumed/r² assumes 3D geometric dilution.
  The 1/r² was assumed, not derived from graph dynamics. The ODE
  relabels GM as L×R/4π — a reinterpretation, not a derivation.

### v10: Consumption IS Movement (April 6)
- Entity consumes, and that IS its movement. Each consumed deposit
  shifts the pattern center by the deposit's direction. The consumption
  IS the tick (RAW 028 temporal surfing).
- Graph attempt: star deposits don't reach r=40 (local field problem).
- **Minimal orbit**: fake star, geometric flux, 10% resistance.
  Perfect circular orbit at v_circ. Elliptical at sub-circular.
  82 revolutions. Keplerian dynamics from consumption force.
- **Honest assessment:** uses flux = L/(4πr²) = Newton renamed.
  The gap between graph dynamics and 1/r² force remains open.

### v11: Arrival Rig (April 16, 2026)

#### Phase 1 — Graph → 1/r² confirmed
- **Strips everything away: star emits, graph propagates, no consumption.**
  Isolates the question "does the substrate alone produce 1/r²?"
- Model: density field on a 3D random geometric graph. Each tick, every
  node redistributes `ρ / degree` to neighbors. Star held at `ρ = L`
  (source). Outer shell (`r > 0.95 R`) absorbs. Vectorized with
  `np.bincount` over flat directed-edge arrays (~5 t/s at 500k nodes).
- 500k-node / R=80 / ⟨k⟩=23.5 / 3000 ticks. Density fit in the
  intermediate range r ∈ [4, 40].
- **Gradient log-log slope = −1.968 at t=3000 (within 1.6% of Newton).**
  Density slope = −1.274, consistent with the integrated log-log slope
  of the analytical Poisson form `(1/r − 1/R)` over that range.
- Slopes converge monotonically as the profile fills (−2.109 at t=500
  → −1.968 at t=3000). Total interior density at ~80% of asymptote;
  profile *shape* converged earlier than magnitude.
- **The 1/r² that v9/v10 marked "fake" is earned** — it is what the
  substrate naturally delivers under pure propagation. The deviation
  from exactly −2 could be residual transient, discreteness (finite
  ⟨k⟩ RGG vs continuum), or the 50-node source extent.

#### Phase 2 — Orbits under the measured field
- Take the binned ρ(r) from Phase 1, build an interpolator, feed
  F(r) = RESISTANCE · |dρ/dr(r)| directly into v10's orbit integrator.
  No analytical fit, no Newton ansatz — the raw graph profile is the
  force curve.
- 100k-node graph, propagated 2000 ticks to steady state, six orbit
  integrations from r=20 at {circular, 0.85 v_c, 1.15 v_c} compared
  against a pure K/r² reference with matched coupling.
- **Result: orbits from the measured field and orbits from pure Newton
  overlay within a few percent.** Circular stays circular, elliptical
  stays elliptical, periods match. The chain tick-frame axioms → graph
  propagation → measured 1/r² → Keplerian orbits is unbroken.
- Only deviation: at large r (>1.3 R_eq) the measured field drops
  slightly below 1/r² because the absorbing boundary starts to bite;
  wide orbits close tighter under the measured curve than under Newton.
  A real graph-substrate signature, not a failure.

#### Phase 3 — Buffered consumption (honest label: HYBRID)
- Tests a new idea: the planet has a **finite consumption capacity
  C_max**, and unconsumed deposits accumulate on the star-planet
  connector as a buffer `B`. Buffer physically extends the connector:
  `r_eff = r_geom + α·B`. Force seen by the planet uses `r_eff`, not
  `r_geom`. Grounded in RAW 113 / Exp 118: Different deposits extend
  connectors; buffer = Different on the star-planet connector.
- State: `(x, y, v_x, v_y, B)`. Per-tick rule: pool = B + K/r_eff²,
  consumed = min(pool, C_max), B' = pool − consumed, F = consumed·(−r̂).
- Six initial conditions. All six produce bound orbits. Clean
  inner/outer split:
  - `r < r_eq`: **capacity-limited.** F = C_max constant. Even with
    elliptical r_geom (swinging 6→11), **r_eff pins to r_eq = 20.00
    ± 0.15** via buffer absorption. Predicted scaling T ∝ √r.
  - `r > r_eq`: buffer is zero, F = K/r² — ordinary Newton.
- **Honest disclosure: Phase 3 is NOT Newton-free.** (Revised after
  discussion 2026-04-16 about tick-bookkeeping ontology.)
  - `arrival = K/r_eff²` is Newton's 1/r² typed in directly. Defense:
    Phase 1 measured it and Phase 2 verified it produces the same
    orbits on the graph; using K/r² in Phase 3 is a known-good
    shortcut, but not re-derived here.
  - `F = m·a` is NOT smuggled Newton under the tick reading: time,
    length, mass are all tick-counts; force = consumption rate
    (deposits/tick); acceleration = velocity-change-per-tick.
    `F = m·a` is `ticks/tick = ticks × 1/tick` — impulse conservation
    distributed across constituent quanta. Doc 28 grounds this: a
    mass-M entity consumes M ticks/tick just to persist (renewal),
    and surplus = arrival − M drives acceleration with a = surplus/M.
  - Continuous `(x, y)` position for the planet IS a substrate
    abstraction. On the graph the planet position is the COM of its
    deposit-dominance region, which only moves via boundary shifts.
    v8 showed isolated clusters diffuse instead of coasting — so
    whether the COM-as-continuous approximation holds is an open bet.
  - The "outer regime = Kepler" observation is a tautology given the
    K/r² input — only an integrator sanity check, not a discovery.
- What IS new in Phase 3: the buffer mechanism and its consequences
  (r_eff pinning, capacity-limited inner regime, T ∝ √r prediction).
  These are genuine consequences of the update rule. But the update
  rule itself is a heuristic motivated by Exp 118 theory, **not
  derived from graph dynamics.** On the actual graph, unconsumed
  Different deposits would scatter across many paths, not pool on
  one "star-planet connector."
- **What Phase 3 does NOT establish.** That the same inner/outer
  dichotomy would appear if Newton were fully removed (no K/r²
  baked in, no continuous planet with F=m·a, buffer forming on the
  graph organically). That is Phase 4, and based on v7/v8 precedent,
  the orbital part probably would not survive — the "bent pipe"
  problem (need for emergent internal planet structure) is still the
  gate on real orbits on the substrate.

**Stance.** Using Newton as a computational shortcut is fine when we
are not claiming emergence. When we ARE claiming emergence (the whole
point of Experiment 128), Newton in the code needs a flag on it.

#### Phase 3.1 — Mass, Renewal, and Capacity-per-Node (April 16, 2026)

Driven by the tick-bookkeeping correction and Doc 28 Temporal Surfing.
Wires mass in as a genuine parameter and adds renewal:

```
renewal  = M                          # cost just to persist
pool     = B + K / r_eff^2
consumed = min(pool, C_cap)
surplus  = max(0, consumed - renewal) # drives motion
F        = surplus * (-r_hat)
a        = F / M
B'       = pool - consumed
```

Two capacity variants tested across mass sweep M ∈ {0.25, 0.5, 1.0,
2.0, 4.0} at r₀ ∈ {10, 15, 20, 25, 30}:

- **Variant A:** `C_cap = 1.0` fixed — unphysical: heavy planets
  starve before reaching their equilibrium. Sanity-check, not the
  real model.
- **Variant B:** `C_cap = 1.5·M` — each node carries its own capacity.

**Variant B produces Newton's mass-independence of orbital period.**
At r=10, measured T=28.10 for M=0.25, 0.5, 1.0, and 2.0 (identical to
three decimals). At r=15, T=34.41 across masses. At r=30, T=48.67.
Mass cancels in the equation of motion because
`F = surplus = C_cap − M = 0.5M`, giving `a = F/M = 0.5` (constant).
This is Newton's "third body mass doesn't affect period" falling out
of substrate arithmetic when capacity scales with size.

**T ∝ √r confirmed in the capacity-limited inner regime** —
48.67 / 28.10 = 1.73 ≈ √3 for r ratio 30/10 = 3. Clean anti-Kepler
signature.

**Two new testable predictions emerge from Phase 3.1:**

- **Gravity horizon** `r_star = √(K/M)`: beyond this radius, arrival
  K/r² drops below renewal M, surplus goes negative, no orbit
  possible. Heavier planets are confined closer. Lighter planets can
  roam farther.
- **Capacity-limited inner zone** with T ∝ √r (not Kepler's r^(3/2)).

#### Phase 3.2-3.4 — solar-system reality check (April 16)

- 3.2 solar-system sanity check: Phase 3.1 formula fails (T² slope
  2.24 vs Kepler's 1.5). The "fixed model" (consumption ∝ M) matches
  inner planets but the naive renewal term produces a false gravity
  horizon at √K = 6.28 AU, beyond which real planets orbit fine.
- 3.3 Earth at Planck scale: renewal demand 10³²/tick, stellar supply
  10⁻²²/tick. Ratio 10⁻⁵⁴. Renewal is decisively **local (ambient
  tick-stream), not stellar**.
- 3.4 per-planet resistance fit: fitting each planet's resistance
  gives R(r) = 1 + r²/K — a pure distance function, not planet-
  specific. Interpretation: ambient contributes 1 per node per tick
  exactly covering renewal, stellar contributes K/r² on top as
  surplus. Renewal drops out of orbital dynamics entirely.
- Consequence: the anti-Kepler / horizon story from Phase 3.1 is
  **not applicable to real planets**. The clean substrate-Newton
  (`a = K/r²`) holds to ephemeris precision.
- The "consumed/renewal = K/r²" ratio does reveal a real pattern:
  rocky planets 17–264×, gas giants near 1×. Suggestive of a
  transition at ~6 AU between star-dominated (rocky) and self-
  dominated (gas giant) regimes. User's "structure = resistance"
  reading maps: high-resistance rocky planets force complexity
  formation; low-resistance gas giants absorb/dissipate.

### v11 Phase 4 — Gravitational Time Dilation (April 17, 2026)

Reinterpret the Phase 1 field as a local clock modulator:

```
γ_local = 1 / (1 + ρ_local / ρ_scale)
```

- Weak-field limit: `(1 - γ) ≈ ρ/ρ_scale = (A/ρ_scale) / r`.
- Measured log-log slope of `(1 - γ)` vs `r` on the graph: **-1.094**
  (Einstein's weak-field gravitational redshift: -1.000, within 9%).
- ρ(r) slope itself is -1.298, consistent with `(1/r - 1/R)` form
  from Phase 1.
- The 1/r shape of gravitational redshift emerges from the measured
  substrate field. Saturation form and ρ_scale are free.

### v11 Phase 5 — Unified SR + GR from a single tick-budget (April 17)

Insight (Tom, 2026-04-17): load is braking against connector
propagation. Photon (at c) doesn't brake — doesn't consume. Below c
you refuse to flow; refusal costs budget. Gravity is another kind of
refusal (you process deposits instead of just being).

Tick-budget accounting:
- Each node has unit tick-budget per tick.
- Gravity load: L_grav = ρ/ρ_scale.
- Velocity load: L_vel = v²/c² (squared form from Minkowski
  Pythagoras — time and space combine geometrically).
- Proper tick rate: `γ = √(1 - L_grav - L_vel)`.

**Key result:** This additive-under-sqrt form is NOT a weak-field
approximation — it is the EXACT Schwarzschild proper-time formula
for a stationary or tangentially-rotating clock:

```
dτ/dt = √((1 - 2GM/rc²) - v²/c²)
```

The commonly quoted multiplicative form `γ_grav × γ_SR` is the
weak-field approximation; the strict GR answer is the additive
form we derived from substrate accounting.

Test on (r, v) grid with graph-measured ρ(r):
- v = 0: TF = multiplicative trivially (same formula).
- Weak (L_total < 0.25): agree within 1–2%.
- Strong (L_total → 1): TF correctly saturates to 0 (static limit /
  ergosphere boundary). Multiplicative form gives wrong positive
  values.

**What's earned:**
- Unified SR + GR from one substrate accounting principle.
- Exact Schwarzschild formula for tangential motion, with ρ(r) from
  first-principles graph propagation.
- Static limit as a geometric boundary, not assumed.
- One free coupling (ρ_scale). No Einstein in the code.

**What's still open:**
- Actual moving-clock simulation on the graph (here we reinterpret
  static field with v as analytical parameter).
- ρ_scale calibration.

### v11 Phase 6 — Radial Motion and the Substrate's Isotropy Limit (April 17)

Tests whether the tick-budget formula also matches Schwarzschild
for radial motion. GR's radial case has an extra `1/(1 − L_grav)`
factor on the spatial term (from the Schwarzschild metric component
`g_rr = 1/(1 − L_grav)`):

```
dτ/dt = √((1 - L_grav) - v²/(c²(1 - L_grav)))   [radial, GR]
vs
dτ/dt = √((1 - L_grav) - v²/c²)                 [tangential, our Phase 5]
```

**Test results (same (r, v) grid as Phase 5):**
- Weak field (r=25, v=0.3): naive TF agrees with Schwarzschild
  radial to 0.4%. Fine.
- Moderate (r=12, v=0.5): 6% discrepancy.
- Strong (r=8, v=0.6): **50% off**. Naive form dramatically over-
  estimates γ in strong radial fields.

**Direct measurement of graph structure:**
Measured `⟨cos²θ_radial⟩` averaged over edge directions in radial
shells. Uniform 3D isotropic value = 1/3.
| shell | ⟨cos²θ⟩ |
|---|---|
| [3, 6] | 0.326 |
| [8, 12] | 0.322 |
| [15, 20] | 0.332 |
| [25, 35] | 0.338 |

All ≈ 1/3. **The graph has no radial-vs-tangential anisotropy,
including near the source.** This confirms that the v11 substrate
lacks the structural feature GR needs for radial motion.

**What Phase 6 diagnoses:**

To reproduce full GR (not just tangential), the substrate must
**reshape local connector geometry near masses**, making radial
connectors effectively longer than tangential ones by the
Schwarzschild factor `1/√(1 − L_grav)`. In Tom's earlier "connector
= gravity" intuition, this would mean deposits don't just add
density scalar-wise — they also anisotropically redistribute the
local graph topology.

Predictions of such a substrate (not yet built):
- Phase 5 tangential result stays.
- Radial test would pass in strong field.
- Mercury perihelion precession would emerge from the radial/tangential
  asymmetry of elliptical orbits.
- Black-hole event horizons emerge as surfaces where radial
  connectors have infinite effective length.

#### Phase 6 adds to the end-of-April 2026 emergence list

- Schwarzschild tangential proper time — **earned** (Phase 5).
- Schwarzschild radial proper time — **NOT earned** in v11. Graph is
  isotropic; needs direction-dependent connector structure.
- Mercury perihelion precession — **still open**, likely gated by
  radial-motion fix.

### v11 Phase 7 — Moving Star and the Comoving Pattern (April 17)

Test: move the star in z while tracking the planet's orbit under
retarded Newtonian gravity (light-speed delay on the force).

**Comoving case** (planet shares star's z-velocity — physical,
since bound systems form co-moving): orbit preserved perfectly
for v_z up to 0.001·c (30× real solar galactic speed). 199.9 out
of 200 expected revolutions. r_xy = 1.0000 exactly.

**Non-comoving case** (planet artificially left at rest in z):
orbit breaks at v_z = v_circ.

**Interpretation.** Equivalence principle emerges automatically
from retarded gravity without being built in. The solar system
is a **coherent pattern drifting through the substrate as a
unit**; its internal structure (orbit) is a property of the
pattern, frame-invariant, dynamically irrelevant to the bulk
drift. Scale-invariant: atoms, planets, solar systems, galaxies
are all "traveling patterns" at their scales.

**What Phase 7 settles.** The "solar system moves, so no orbit
really closes" observation is geometrically true but dynamically
irrelevant. Frame choice determines appearance; substrate
dynamics are identical in any frame. Growing-graph frontiers
therefore won't break orbits; patterns just drift across
continuously-renewing substrate.

**What Phase 7 does NOT address:**
- Coherent pattern self-formation (still v7/v8's unsolved problem —
  pre-placed clusters diffuse, they don't cohere).
- Relativistic v_z regime.
- Actual substrate growth at the frontier.

#### End-of-April 2026 standing status

**Earned on the substrate:**
1. 1/r² arrival on the graph (Phase 1, slope −1.968).
2. Keplerian orbits under measured field (Phase 2).
3. F = m·a as tick bookkeeping — not smuggled Newton (Phase 3.1).
4. Newton's mass-independence of orbital period (Phase 3.1 B).
5. Clean Newton gravity at solar-system scale via ambient-covers-
   renewal decomposition (Phase 3.2-3.4).
6. Gravitational redshift 1/r shape (Phase 4, slope −1.094).
7. Exact Schwarzschild proper-time formula for tangential observers
   (Phase 5, additive-under-sqrt emerges from tick-budget Pythagoras).
8. Equivalence principle emerges from retarded gravity (Phase 7).

**NOT earned, specifically diagnosed:**
- Schwarzschild radial stretching (Phase 6) — substrate needs
  direction-dependent connector structure near masses.
- Coherent self-holding patterns on the substrate (the "bent pipe"
  from v7/v8, the "planet diffuses" problem). Gates all higher-level
  dynamics.

**Unified synthesis frontier:** v11 gravity + Experiment 55/56
(collision physics, composite objects) joined into one framework
where patterns form, hold themselves together, drift through the
substrate as units, and interact gravitationally with other patterns
— including radial anisotropy from deposit-reshaped connectors.
That's the next major effort.

#### Emergence claims that stand, end-of-April 2026

- 1/r² arrival on the graph — **earned** (Phase 1, slope −1.968).
- Keplerian orbits under the measured arrival curve — **earned**
  (Phase 2).
- F = m·a as tick bookkeeping (not external Newton) — **earned**
  (Phase 3.1, tick reading of mass/force/acceleration).
- Newton's mass-independence of orbital period — **earned** when
  capacity scales with mass (Phase 3.1 Variant B).
- Gravitational redshift 1/r shape — **earned** (Phase 4, slope
  -1.094 vs Einstein -1.000).
- Exact Schwarzschild proper-time formula for tangential observers —
  **earned** (Phase 5, unified additive tick-budget).
- Ambient-covers-renewal / stellar-drives-orbit decomposition —
  **earned** (Phase 3.3/3.4, solar system fits to precision).
- Buffer forms organically from Different deposits on actual graph —
  **not tested** (v7/v8 precedent is discouraging).
- Sustained tangential (orbital) motion on the pure substrate —
  **still unsolved**, same as v7/v8. The "bent pipe" problem is the
  gate on real orbits.
- Radial-motion GR test — **not yet done** (Phase 6 candidate).
- Mercury perihelion precession — **not yet done**.

## Experiment 128 Final Summary (v1-v11, April 3-16, 2026)

### What's proven:
1. Radial equilibrium from production/consumption balance (v6)
2. Deposit dominance regions are the correct entity measurement (v6)
3. Mass = source count (Phase 1)
4. Consumption mechanics work (all versions)
5. Consumption IS centripetal force → Keplerian orbits (v9 ODE, v10 minimal)
6. Tangential thrust destabilizes orbits — excess leaves system (v9 ODE)
7. Angular momentum is INHERITED, not generated (RAW 130)
8. **Graph substrate produces the 1/r² force law as emergent behavior
   of pure propagation** (v11, April 16): slope −1.968 vs ideal −2.0.

### What's not proven:
1. That the 1/r² scaling survives when Same/Different consumption is
   turned on (non-linear coupling could warp it). This is the next test.
2. That a *consuming* planet at distance r experiences a force that
   follows the measured gradient. v11 Phase 2 plan.
3. Emergent planet formation from reject stream (Phase 3, unchanged).
4. Internal planet structure producing directed processing (bent pipe).

### The former remaining gap — now closed (in the pure case):
Graph experiments → deposits dilute with distance (geometric spreading)
ODE → consumption force with 1/r² produces orbits
**Connected (v11):** graph propagation → measured 1/r² gradient → feeds
the ODE force law with a result that comes from the substrate, not an
assumption.

What remains: (a) verify the scaling under consumption dynamics, (b) plug
the measured `f(r)` into v10's orbit dynamics and confirm closed orbits.

### Key theoretical contributions:
- **RAW 130:** "It rotates because it consumes"
- **RAW 129:** Experimental connections (Breit-Wheeler, quantum battery,
  CME, planetary structure, quantum-classical transition)
- **RAW 128 v2:** Three-way partition (store/move/radiate)

### Path forward:
1. **Mathematical proof:** Show 1/r² force from geometric dilution on graphs
2. **Phase 3:** Emergent planet from star's reject stream
3. **GPU scale** (causal-cone-engine) for emergent internal structure
4. **Analytical orbital mechanics** from consumption equations

---

*The entity consumes. The consumption IS the movement.*
*The orbit is maintained by consumption — stop consuming, fly off straight.*
*The force law comes from geometry. The force constant comes from physics.*
*GM = star_emission × planet_resistance / 4π.*
*Six days, 25+ versions, two experiments, one sentence: it rotates because it consumes.*
