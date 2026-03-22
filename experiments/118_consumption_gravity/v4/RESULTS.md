# Experiment 118 v4: Producer-Consumer Planet Formation

## Model

Single seed at origin. Random stream of 6 typed particles, 1 per tick.
Star knows types {0,1,2} (50%), rejects types {3,4,5} outward.
Rejected unknowns of same type route to same seed. Seed pushed outward
each rejection. At threshold (100 rejections) seed promotes to planet.
Planet then absorbs its type from the stream, growing by claiming nodes.

No momentum, no velocity, no force, no deposits.
Distance emerges purely from connector extension during rejection.

## Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| N_NODES | 5000 | Graph substrate |
| N_TYPES | 6 | Stream diversity |
| STAR_SPECTRUM | {0,1,2} | 50% absorption rate |
| GROWTH_COST | 10 | Absorptions per new node |
| PLANET_THRESHOLD | 100 | Rejections before promotion |
| REJECTION_HOPS | 5 | Hops outward per rejection |
| EXTEND_RATE | 0.01 | Connector extension per hop |
| TICKS | 30000 | |

## Results

### Formation timeline

| Event | Tick | Notes |
|-------|------|-------|
| seed_t4 created | 3 | First rejection of type 4 |
| seed_t5 created | 5 | First rejection of type 5 |
| seed_t3 created | 7 | First rejection of type 3 |
| planet_t3 formed | 532 | 100 rejections accumulated |
| planet_t5 formed | 540 | |
| planet_t4 formed | 644 | |

### Final state (t=30000)

| Entity | Nodes | Consumed | Distance | Born |
|--------|-------|----------|----------|------|
| star | 1492 | 14916 | -- | 0 |
| planet_t3 | 488 | 4876 | 11.50 | 532 |
| planet_t5 | 490 | 4895 | 16.68 | 540 |
| planet_t4 | 502 | 5013 | 10.62 | 644 |

- Claimed: 2972 / 5000 nodes (59.4%)
- Connector extension: mean 1.0004, max 2.678
- Speed: ~15,000 ticks/sec

### Key observations

1. **Mass ratio is natural.** Star absorbs 3/6 types, each planet absorbs 1/6.
   Final ratio star:planet = 1492:~490 = 3.05:1, matching the spectrum ratio
   exactly (3:1). No tuning needed.

2. **Seeds pushed outward before gaining mass.** Seed push distance plot shows
   seeds reaching dist 19-22 from star before promotion at mass=100. The push
   happens while the seed is lightweight (1 node), so no inertia to overcome.

3. **Angular diversity from randomness.** Each unknown type ejects from a
   random frontier node, giving different directions. Three planets end up
   at different angles around the star.

4. **Extension stops after formation.** Once all 3 planets cover all 6 types,
   every stream particle is absorbed. No more rejections = no more connector
   extension. The max extension (2.678) is the fossil record of the formation
   process.

5. **Planet distances fluctuate.** Planet Euclidean distance from star changes
   as the star grows and its COM shifts. Not real orbital motion -- just the
   star expanding toward/away from the planet.

## What's missing: velocity

The model produces distance but not orbital velocity. Planets are static
clusters that grow in place. The distance plot shows fluctuation from the
star's COM shifting, not from planet movement.

Possible sources of velocity in this framework:

### 1. Ongoing rejection asymmetry (radiation pressure)

If the planet doesn't absorb ALL of its incoming types perfectly (e.g.,
some leak, or the planet has a partial spectrum), ongoing rejections from
the planet surface would extend connectors directionally. Each rejection
is a momentum impulse. If the rejection pattern is asymmetric (more
rejections on the star-facing side, where the stream is denser), the net
force pushes the planet outward -- like radiation pressure.

### 2. Differential consumption across the planet's surface

The star-facing hemisphere of the planet sees more "incoming" material
(routed through star-planet connectors) than the far side. This creates
a consumption gradient: connectors on the star-facing side get consumed
(shortened?) while the far side extends. The asymmetry creates net motion
away from the star -- or toward it if consumption dominates extension.

### 3. Cross-type interaction (planet rejects star-types)

If the planet encounters star-type deposits on its local connectors
(left over from the star's early expansion), it would reject them. These
rejections travel outward from the planet, extending connectors. The
direction of these rejections (away from the planet) creates a recoil.
If the star-facing connectors carry more star-type deposits, the recoil
is systematically outward.

### 4. Growth-front pressure

As the star grows (claims new nodes), it physically expands toward the
planet. Connectors between the star frontier and the planet get shorter
(the star claims nodes that were in between). This "pushes" the effective
distance down. If the planet also grows, the two growth fronts create
pressure between them. The smaller entity (planet) would be displaced
more -- yielding net outward velocity.

### Most likely candidate

**Option 3 (cross-type rejection)** seems most natural. The planet sits
in a region where star-type deposits exist on connectors (from early star
expansion). The planet doesn't "know" these types. So it rejects them.
Each rejection extends a connector and imparts a tiny momentum kick.
The kicks are biased toward the star-facing side (more star deposits there),
giving systematic outward drift. This is the same mechanism that created
the planet in the first place -- just continuing at the planet level.

This would also produce tangential velocity if the star's deposit field
has angular structure (which it does, since the star has discrete groups).
The planet would drift along deposit gradients, producing orbital motion.
