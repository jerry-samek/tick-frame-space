# V6 Summary: Orbital Program — What We Learned

## What V6 Set Out To Do
Transform V5's uniform entity soup (~8,573 entities, all identical behavior) into
a hydrogen-atom analog: stable central vortex with quantized orbital shells.

## What Was Implemented
1. **Two-phase entity lifecycle**: learning (fill memory with gradient blend) ->
   execution (replay memory cyclically as orbital program)
2. **Orbit closure check**: after one execution cycle, if entity returns within
   hex_distance <= 1 of start -> orbit closed, entity lives indefinitely
3. **Binary fission**: failed orbits trigger 2-child replication (not fill-all-6)
4. **Standing wave quantization**: memory_size = birth_tick, closed orbits at
   R = birth_tick / (6k)

## Key Experiments and Findings

### Experiment 1: V6 with expansion (original)
- Entities scatter to boundary, identical to V5
- Gamma field flat: field_max/field_mean = 1.01x at tick 1000
- **Finding**: Universal expansion (gamma += 1.0 everywhere) drowns entity imprints.
  118 entities depositing 1.0/tick are 1% of the 10,981/tick expansion energy.

### Experiment 2: Remove expansion (entities = sole gamma source)
- Hill forms at center initially (16x above mean at tick 100)
- But entities still scatter outward (mean_R = 195.5 at tick 200 with R=200 grid)
- Diffusion destroys the hill faster than 1 entity can build it
- **Finding**: Without expansion, a real hill exists but entities move at c=1 and
  never return. The gradient is too weak vs heading inertia.

### Experiment 3: Peak-following (entity moves to highest gamma, can STAY)
- **Breakthrough**: Entities stay near center. mean_R = 14.8 at tick 300 (vs 195.5)
- Gamma hill forms at origin: 5.37 at center, falling to 0.59 at R=35
- 5 entities orbit stably, 598 orbit closures in 1000 ticks
- **Problem**: System is dead. Entities glue to self-made peaks and never move.
  Each deposit creates a local max, so entity always stays. No dynamics.

### Experiment 4: Braking radiation (direction change emits photon)
- When entity changes direction, its tick energy goes to gamma deposit at
  lowest-gamma neighbor (downhill) instead of at its own position
- Tested with both mandatory movement and stay-on-peak
- **Problem with mandatory movement**: entities scatter (photons again)
- **Problem with stay-on-peak**: entities sit forever (parking lot again)

## The Fundamental Tension Discovered

Two failure modes, no stable middle ground found:

| Mode | Behavior | Problem |
|---|---|---|
| Must move (c=1) | Entities scatter outward at lightspeed | No hill forms, no orbits |
| Can stay (peak-following) | Entities glue to self-made peaks | No dynamics, dead system |

The chicken-and-egg: entities need a hill to orbit, but the hill needs entities
to stay and deposit. A single entity can't bootstrap because diffusion (1/7 per
tick) destroys the hill faster than 1.0/tick deposit can build it.

## Key Physics Insights (Theory)

These emerged from V6 discussion and inform V7:

1. **Entity is a pattern, not a point**: The entity IS its trail of imprints (gamma
   deposits). A concentrated trail = massive particle. A thin streak = photon.

2. **Mass = staying still**: Concentrated imprints at one location build a tall hill.
   Movement spreads imprints thin. Speed is inversely related to mass.

3. **Hill model of gravity**: High gamma = top of hill (like Lagrangian potential
   visualization). Entity on the hill tries to stay on top. "Falling" = moving
   toward lower gamma = outward.

4. **Braking radiation**: Direction changes cost energy, emitted as photon directed
   downhill (toward lower gamma). Gentle curves = cheap (orbits). Sharp turns =
   expensive (energy loss). This is Bremsstrahlung analog.

5. **Time dilation as tick-skipping**: Entity on high gamma accumulates more energy
   per movement (needs more ticks before it can move = appears slower from outside).
   Deeper well = more massive = slower = more time to build complex patterns.

6. **No universal expansion needed**: Entity deposits ARE the energy source. Diffusion
   propagates the hill outward = expansion of spacetime. The hill IS curved spacetime.

## What V7 Should Do

The bootstrapping problem cannot be solved by tweaking single-entity dynamics alone.
V7 should create a **controlled environment** with pre-built gamma hills to study
entity behavior in a known gravitational landscape, isolating the orbital dynamics
from the hill-building chicken-and-egg problem.

## Files
- `entity.py` — Two-phase lifecycle, STAY direction, braking tracking
- `world.py` — Peak-following + gradient blend, braking radiation, binary fission
- `experiment.py` — V6 visualization with phase coloring
- `metrics.py` — Phase counts, orbit tracking, braking emissions
- `grid.py`, `field.py`, `constants.py` — Unchanged from V5
