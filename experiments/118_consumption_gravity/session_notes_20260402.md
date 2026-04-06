# Session Notes — April 2, 2026 (UPDATED — evening session added)

## Context
Continuation of Experiment 118 orbital mechanics. Started with v9
diagnostic results, ended with v14 on 50k-node graph.

## The Day's Journey: v10 → v14

| Version | Key Change | Star r | Coherence | What It Proved |
|---------|-----------|--------|-----------|---------------|
| v10 | Reactive entities (Aristotelian) | frozen | - | Deadlock. Newton > Aristotle. |
| v11 | Forward default + charging + deflection | 14.5 | 0.20 | Newton works. Deflection too weak. |
| v12 | Same/Different extension rule | 14.5 | 0.24 | **Expansion ≠ connector growth.** Diffusion. |
| v13 | Accumulated density + Same rule + length momentum | 14.4 | 0.19 | Density gradient inverted (forms at cloud, not center) |
| v14 | Same as v13, bigger graph (50k, R=80) | ~60 | **0.27** | 73% volume fraction is scale-invariant |

## Top Insights (in order of importance)

### 1. Star expansion is scale-invariant diffusion at 73% volume fraction
The star expands to fill ~73% of any bounded spherical graph regardless
of graph size. This was proven by v12 (zero connector growth, still
expands) and v14 (50k nodes, same fraction). No mechanism tested in
v4-v14 prevents it. This is a fundamental property of biased random
walks on bounded spherical RGGs.

### 2. Newton's first law is mandatory (v10 deadlock)
Purely reactive entities deadlock. Forward continuation is the default
state. Energy changes direction, not maintains motion. v10's deadlock
is the most elegant proof.

### 3. Same/Different extension rule validated (v12)
Same deposits reinforce (no growth). Different deposits extend. Internal
connectors stay at initial length. The rule works perfectly. It just
doesn't solve the star binding problem because that's diffusion, not
connector inflation.

### 4. v7-v9 "orbits" were random walks (v9 diagnostic)
The most important diagnostic in the experiment's history. All tangential
motion in v7-v9 was graph topology asymmetry + random walk, confirmed
by D3 (pure random walk produces same angular displacement per hop).

### 5. Coherence approaching threshold
v14's coherence of 0.27 is the best of any version, approaching the
0.3 target. The larger graph gives the planet more room for systematic
angular motion. Whether this trends toward real orbits with more room
or saturates at ~0.3 is unknown.

## The Remaining Problem: Star Compaction

The star binding problem is now fully characterized:
- NOT connector inflation (v12 proved: zero growth, still expands)
- NOT weak routing signal (v13 proved: g/f ratio 63:1, still expands)
- NOT graph scale (v14 proved: 73% on any graph)
- IS diffusion of 80 random-walking nodes on a bounded graph
- The density gradient forms WHERE THE NODES ARE, not at the origin
- The gradient is self-consistent (binds cloud to itself) but diffuse

The question: is compaction required for coherent orbits, or can the
mechanism produce orbits within a diffuse star?

Evidence for "orbits within diffuse star":
- Coherence trending up (0.20 → 0.24 → 0.27)
- Planet is bound in every version since v7
- Radial oscillation is robust
- v14 trajectory shows loop-like structure

Evidence for "compaction required":
- No version has passed coherence > 0.3
- The density gradient is 1.35:1 (too weak for strong deflection)
- The g/f ratio at the planet is typically < 1 (forward dominates)

## Theoretical Questions Sharpened by Today

### The stream origin question (deeper than ever)
If the star can't be made compact by any mechanism, and the stream
must be structured for entities to form, and entities must be seeded
with designed spectra... the framework may be a simulation tool with
interesting emergent properties, not a candidate physical theory.

### Zero constants
BASE_WEIGHT and CHARGING_TIME are still parameters. Both might be
eliminable: BASE_WEIGHT → 0 with random tie-breaking; CHARGING_TIME →
connector length (natural rhythm). A version with zero parameters is
the theoretical target.

### Entity emergence (Experiment 119)
Can entities form from an undifferentiated substrate? Every version
since v4 seeds entities with designed labels. The orbital mechanics
validate the mechanism but not the ontology.

## What's Been Built (Validated Components)

These components work and should be carried forward:

1. **Connector = deposits** (v4 ontology, confirmed across all versions)
2. **Same/Different extension rule** (v12, zero internal growth)
3. **Traversal time ∝ connector length** (v7, time dilation confirmed)
4. **Deposit-on-arrival** (v7, one deposit per completed traversal)
5. **Forward default** (v11, Newton's first law on graph)
6. **Accumulated density routing** (v6+v12, gradient exists when Same
   rule prevents length inflation)
7. **Length-proportional momentum** (v13, short = weak inertia, long = strong)

The mechanism is sound. The star binding is the bottleneck.

## RAW Documents Updated
- RAW 128 — The Energy Partition (corrected twice: choice → no choice,
  two outcomes → three outcomes)

## Next Session Priorities
1. Decide: pursue star compaction or accept diffuse star?
2. If accepting diffuse star: can coherence be pushed past 0.3?
3. If pursuing compaction: what mechanism could oppose diffusion?
   (Possibilities: attractive potential from initial graph geometry,
   longer charging time, reduced BASE_WEIGHT, or accepting that
   80 nodes on 5000 is too sparse and testing with 400+ star nodes)
4. The zero-parameter version (v15?)
5. The stream origin / entity emergence question

## Evening Session (continued)

### v14 Deep Analysis
- Angular velocity vs distance: no correlation (flat, not Keplerian)
- Autocorrelation of angular increments: zero (no orbital memory)
- Hop rate FLAT at 0.019 hops/tick/node regardless of distance
- Root cause: CHARGING_TIME=50 dominates cycle time, overriding any flux-dependent velocity
- Coherent episodes: 37% of time above threshold, but barely distinguishable from incoherent

### Deposit Flux Analysis (the key finding)
- Star neighbors per node vs distance from origin:
  d=0-5: 19, d=5-10: 12, d=10-15: 2.7, d=15-20: 0.03, d>20: ZERO
- Gravitational reach limited to ~15 Euclidean units by rc=6.3
- This explains everything: star nodes can only influence direct graph neighbors

### The Connector Insight (Tom)
"The photon from 13B LY away is on the connector connected to you."
The connector between star and planet is a chain of deposits with NO length
limit. The limit is the current tick number. The initial graph topology
(rc=6.3) should NOT limit the gravitational reach.

### v15: Propagating Deposits Build Connectors (started evening)
The synthesis of v5 + v4 ontology:
- Quanta propagate at c=1 hop/tick through the graph (v5 physics)
- Each quantum DEPOSITS on every connector it traverses, GROWING it (v4 ontology)
- The quantum builds the road as it travels — no empty tubes
- Reactive charging: entity velocity = local quantum flux (Keplerian profile)
- Same/Different rule: quanta produce Different deposits on non-matching connectors

Running overnight on 50k-node graph. Forward table took 76s. Slow due to
quantum propagation overhead on 574k edges.

## Session Statistics
- Duration: ~12 hours
- Versions: v10, v11, v12, v13, v14 (complete), v15 (running overnight)
- Key results: star diffusion scale-invariant at 73%, hop rate flat (no Kepler),
  gravitational reach = 15 units (rc-limited)
- Key insight: photon builds the road, propagation + ontology must unify
- Two-day total: 15 versions, v15 running overnight
