# Session Notes — April 1, 2026

## Context
Full-day session focused on Experiment 118 orbital mechanics. Started
with v5 results from overnight Code run, ended with first orbital motion
in the experiment's history.

## Timeline of Results

### v5 Phase 2 (morning): Absorption fix
- Conservation perfect, absorption working (80 emit, 16 absorb per tick)
- Star still expands to ~14.5 — same as v4
- Diagnosis: 3.2M deposits in graph, absorption is tiny perturbation
- Chicken-and-egg: no gradient → no binding → expansion → weaker sink

### v5 Forward Propagation variant (afternoon): Beams don't help
- Deposit profile INVERTED — deposits increase with distance, peak at d=7-8
- Follows r³ (shell volume), not 1/r² (surface area)
- Graph too small (9 hops diameter) for geometric divergence
- Beams fill the graph uniformly on a finite RGG

### Key theoretical correction (afternoon): Gravity ≠ Radiation
- Gravity = accumulated deposits on local connectors (permanent history)
- Radiation = deposits traveling along connectors (leaves on a stream)
- Propagating deposits DON'T mark the connectors they ride
- Only entity hops mark connectors

### Deeper correction: There is no empty tube
- The connector IS the chain of deposits. Nothing underneath.
- Remove all deposits → no connector → nodes disconnected
- v5's "fixed immutable graph" was a hidden substrate the theory rejects
- v4 was ontologically correct: connector length = deposit count

### v6 Phase 1: Accumulated density routing
- Saturates to 97% uniform — density ratio flat across entire graph
- The saturation theorem: on a finite graph, any single-type random walk
  deposits everywhere uniformly. No gradient survives.
- Kills ALL routing schemes based on deposit density ratios

### v7 Phase 1: Traversal time ∝ connector length
- **BREAKTHROUGH**: Star binds. COM drift 0.77 (was 3.3-4.6).
  Mean radius 8.5 (was 14-16). Internal/boundary ratio 20:1.
- Time well is real — nodes trapped in center by long traversal times
- Deposit-per-tick variant: too aggressive, nodes frozen (3.5k total hops)
- Deposit-on-arrival variant: weaker binding (r=12) but nodes active
  (292k hops). Chose this for Phase 2.

### v7 Phase 2a: Planet introduction (no tangential kick)
- **PLANET IS BOUND.** First attraction + binding in entire 118 line.
- Oscillates between distance 1.25 and 10.84
- But: purely radial. 36 degrees tangential. No orbit.
- Planet inside star (placement bug)

### v7 Phase 2b: Seeded tangential velocity
- **FIRST ORBIT.** 3.9 net revolutions. 24.5 radial oscillations.
- 6202 total degrees of angular motion over 200k ticks.
- Period ~8k ticks.
- Planet still inside star (placement bug persists)

### v7 Phase 2c: Different placement, same tangential kick
- **ORBIT ROBUST.** 2.1 net revolutions, 28 oscillations, 7392 total degrees.
- Net rotation REVERSED direction — topology-dependent.
- Planet still inside star (scattered node placement)
- Binding confirmed: final distance 4.75, oscillating, not escaping.

## Key Insights (chronological)

1. **There are no empty tubes.** Connectors ARE deposits. This kills v5's
   entire architecture and validates v4's ontology.

2. **Density routing saturates on finite graphs.** The saturation theorem
   means no ratio-based routing can produce gradients. Only absolute
   counts or time-based mechanisms work.

3. **Traversal time ∝ connector length creates gravitational time dilation.**
   This single mechanic produces star binding, the time well, and
   self-limiting compound growth. It's the key innovation of v7.

4. **Deposit-on-arrival, not deposit-per-tick.** The entity READS during
   transit (capacitor charging) and WRITES on arrival (capacitor discharge).
   This keeps nodes active while maintaining time dilation.

5. **Orbital motion requires seeded tangential velocity (currently).**
   The mechanism preserves/amplifies angular momentum but doesn't generate
   it. The missing piece: momentum transfer from absorbed deposits.
   When the planet absorbs star deposits from a direction, it should gain
   a directional bias (forward continuation). This is conservation of
   momentum at the capacitor level.

6. **The orbit direction is topology-dependent.** Different starting
   positions produce opposite rotation directions. This is a prediction
   unique to the graph model — real physics has the same property (orbit
   direction depends on initial conditions) but here it's determined by
   local graph connectivity.

## Open Items for Next Session

### Priority 1: Momentum mechanism
- Add forward-continuation bias to entity routing
- Node tracks which connector it arrived on
- Next hop biased toward continuing that direction
- Strength proportional to incoming deposit density
- Test: does this produce tangential motion WITHOUT seeded kick?

### Priority 2: Planet placement
- Need a CLUSTER of nearby nodes all outside the star
- Current method: 5 nearest nodes beyond distance threshold → scattered
- Fix: find a node outside the star, then take its 4 nearest neighbors
  as the other planet nodes → guaranteed cluster

### Priority 3: Exterior orbit
- All Phase 2 tests had planet inside star (r=4-6, star r=12)
- Need planet at r > star_r + margin to test exterior orbital mechanics
- The gravitational signal outside the star depends on the random walk
  tail — may be too weak

### Priority 4: Quantitative tests (STRETCH)
- Force vs distance
- Kepler's third law (T² vs r³)
- Angular momentum conservation quality

## The Stream Origin Question (from last night)
Still unresolved. Still the most important theoretical question.
Parked while experimental progress is hot.

### v8 Phase 2: Store/move partition (evening)
- RAW 128 store/move energy partition implemented
- In-flight quanta propagate forward, deposit on connectors (momentum wake)
- **EMERGENT ORBIT WITHOUT KICK:** 1869 total degrees, net -193 degrees
- Planet properly placed outside star (initial dist=19.6, star r=17.5)
- BUT: partition barely engaged. stored=0, in-flight=4 steady state
- Tangential motion from graph-topology asymmetry, not momentum wake

### v9 Phase 2: Three-way partition (evening)
- RAW 128 v2: added radiation as third outcome (energy outlet)
- Removed deposit-on-arrival entirely — all deposits through partition
- **ORBIT WITHOUT KICK:** 2254 total degrees, net 474 degrees
- Three-way ratio: store=0%, move=99.3%, radiate=0.7%
- The timing problem: entity idle window is 1 tick out of ~100-200.
  In-flight quanta (~4) almost never coincide with idle capacitor.

## Pending Issues

### P1: The partition timing problem
Entity nodes idle 1 tick out of ~100-200. In-flight quanta = ~4.
Options: (a) emit every tick during transit, (b) longer idle periods,
(c) absorption during transit, (d) rethink "idle capacitor."

### P2: Is the momentum wake needed?
v8-v9 produce orbits without the wake engaging. Graph-topology routing
asymmetry is the actual mechanism. Should the theory explain this?

### P3: Exterior orbit
All planets end up inside the star body. Need exterior orbits.

### P4: Quantitative orbital tests
Force vs distance, Kepler's laws, angular momentum conservation.

## Milestone
**April 1, 2026: First orbital motion on graph substrate.**
- v7 Phase 2b: first orbit with seeded kick (3.9 revolutions)
- v8 Phase 2: first emergent orbit without kick (1869 deg)
- v9 Phase 2: three-way partition orbit without kick (2254 deg)

## Session Statistics
- Duration: ~10 hours
- Versions tested: v5 (3 variants), v6, v7 (4 phases), v8, v9
- Key breakthrough: traversal time ∝ connector length (v7)
- Second breakthrough: emergent orbit without kick (v8)
- Key unsolved: RAW 128 partition timing problem
- The day that produced the first orbits on a graph substrate
