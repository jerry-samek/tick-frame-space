# v21: Force-on-Hop — Restoring the Commit Cycle

## Date: February 25, 2026

## Status: Design for Code

## What v20 Taught Us

Distributed star (117 nodes, 2808 angular directions) made almost no difference
to orbit smoothness. The jitter comes from the RECEIVER (planet's 24 connectors),
not the SENDER (star's angular coverage).

The drag experiment revealed the real problem:

| Setup | Final |v| | Hops | Reversals | Outcome |
|-------|----------|------|-----------|---------|
| sep=10, drag=0.001 | 0.072 | 1777 | 246 | Bound but jagged |
| sep=10, drag=0 | 2.808 | 352 | 77 | Velocity runaway |
| sep=20, drag=0.001 | 0.144 | 1154 | 182 | Bound but jagged |
| sep=20, drag=0 | 0.626 | 406 | 152 | Best — bound, stable-ish |

**Key finding:** Without drag, sep=10 has velocity runaway (0.1→2.8). Sep=20
survives (0.1→0.6) because the gradient is weaker. The velocity growth comes
from force being applied EVERY TICK between hops.

Currently: entity sits on a node for ~100 ticks between hops. Every tick, it
reads the same connectors and adds force to velocity. That's like standing still
and being pushed 100 times before taking one step. Of course velocity explodes.

## The v21 Fix: Force on Hop Only

The entity reads its connectors ONCE when it arrives at a node. Gets one force
nudge to velocity. Then coasts on pure inertia until displacement reaches ±1
and it hops. At the new node, reads again. One nudge. Coast. Hop. Read.

```python
def advance(self, graph, tick):
    # Deposit gamma (every tick — entity radiates continuously)
    deposited = self.mass * self.deposit_rate
    for node in self.nodes:
        graph.deposit(node, self.bid, deposited / len(self.nodes))
    if self.radiate_mass:
        self.mass = max(self.mass - deposited, 0.0)

    # Force: ONLY on the tick after a hop (or first tick)
    if self.just_hopped:
        force_3d = self.compute_force(graph)  # read connectors once
        self.velocity += force_3d / self.inertia
        self.just_hopped = False

    # Displacement: every tick (pure inertia between hops)
    self.displacement += self.velocity

    # Hop check
    best_connector, best_dot = self.best_hop_direction(graph)
    if best_dot >= 1.0:
        self.hop(graph, best_connector)
        self.just_hopped = True  # will read force next tick
```

Between hops: pure inertia. No force updates. No velocity changes.
At each hop: one gravitational correction from the new node's connectors.

## Why This Is Better Physics

### 1. Fixes velocity runaway

Currently: 100 ticks × force_per_tick = 100× over-correction.
v21: 1 force read per hop. The correction is proportional to the ACTUAL
position change, not to how long the entity sat still.

### 2. Restores time dilation

The commit cycle IS gravitational time dilation:

**Close to mass:** Strong gradient → large force nudge → displacement fills
fast → hop quickly → few ticks between commits → less "internal time" per
position change → **time runs slower**.

**Far from mass:** Weak gradient → tiny force nudge → displacement fills
slowly → many ticks between hops → more "internal time" per position change
→ **time runs faster**.

This is emergent gravitational time dilation. Not programmed. It falls out
of the commit cycle naturally. v14-v17 had it implicitly through the
Bresenham/commit counter. v18-v20 lost it by applying force every tick.
v21 brings it back.

### 3. Smooth orbits from discrete hops

Each hop is a discrete step. But between hops, the entity moves in a
STRAIGHT LINE (pure velocity, no force). The orbit is a polygon — straight
segments connected by angular corrections at each hop. More hops = finer
polygon = smoother circle.

This is exactly how real numerical integrators work (leapfrog, Verlet).
Apply force at discrete timesteps. Coast between. The orbit is a polygon
that approximates a smooth curve. v21 makes the graph simulation equivalent
to a symplectic integrator — which is known to conserve energy long-term.

### 4. No drag needed

Drag was added in v19 to combat velocity runaway. With force-on-hop-only,
the runaway can't happen — there's no mechanism to pump velocity between
hops. Remove drag entirely.

## Implementation Details

### Changes from v20

1. **Add `self.just_hopped` flag.** Initialize True (so first tick reads force).
   Set True after each hop. Set False after force is applied.

2. **Move force computation inside `if self.just_hopped` block.**
   `compute_force()` only called when flag is True.

3. **Remove drag entirely.** No `--drag` parameter. No velocity damping.
   If velocity grows, it's from gravitational acceleration, not numerical error.

4. **Keep everything else from v20.** Distributed star, weighted spread,
   edge-weighted diffusion, mass radiation, 3D velocity tracking.

### Force Computation (unchanged)

Same as v20 — read growth_at_node_external for each connector, compute
force as (mean_growth - connector_growth) projected to 3D direction.
The only change is WHEN it's called (hop-only vs every-tick).

### Hop Mechanics (unchanged)

Same as v20 — displacement += velocity every tick. When displacement
projects onto best connector ≥ 1.0, hop. Subtract hop direction from
displacement. Project velocity and displacement to new node's connectors.

### What to Watch For

**Velocity should be STABLE.** Without per-tick force pumping, velocity
changes only at hops. Total velocity change over N hops should equal
the sum of N individual force reads. No runaway.

**Hop rate should reflect time dilation.** Count ticks between hops at
different distances from the star. Closer = fewer ticks between hops
(stronger nudge → faster displacement accumulation). Further = more ticks.
Plot ticks_between_hops vs distance. Should show clear correlation.

**Angular momentum should have consistent sign.** With force-on-hop-only,
each correction is small relative to velocity. The orbit shouldn't reverse
direction every few hops. L_z should oscillate around a nonzero mean.

## Experiment Plan

### Phase 1a: Baseline comparison (sep=10, distributed star)

Same as v20 sep=10 but with force-on-hop-only. No drag.

Compare to v20:

- v20 sep=10 drag=0: |v| runaway to 2.8, 352 hops
- v21 sep=10 no drag: |v| should stay bounded, more hops

### Phase 1b: Sep=20 comparison

Same as v20 sep=20 but with force-on-hop-only. No drag.

Compare to v20:

- v20 sep=20 drag=0: |v| grew to 0.6, 406 hops, 152 reversals
- v21 sep=20 no drag: |v| should stay near 0.1-0.2, smoother orbit

### Phase 1c: Time dilation measurement

Run Phase 1a or 1b. Log tick number at each hop. Compute
ticks_between_hops[i] = tick[i+1] - tick[i]. Plot vs distance from star
at each hop.

**Prediction:** ticks_between_hops should INCREASE with distance (weaker
force → slower displacement accumulation → more ticks to reach threshold).
This IS gravitational time dilation.

### Phase 1d: Longer run

Best configuration from 1a/1b, run for 200K ticks. Check:

- Does velocity stay bounded?
- Does comoving distance stabilize?
- Does L_z show sustained rotation?

## Parameters

| Parameter           | Default | Notes                          |
|---------------------|---------|--------------------------------|
| N                   | 30000   | Same as v20                    |
| k                   | 24      | Same as v20                    |
| H                   | 0.01    | Same as v20                    |
| G                   | 0.0     | Always zero                    |
| star mass           | 100000  | Same as v20                    |
| planet mass         | 1       | Same as v20                    |
| deposit_strength    | 1e-5    | Same as v20                    |
| drag                | 0       | REMOVED — not needed           |
| body_base_radius    | 5.0     | Same as v20 (distributed star) |
| separation          | 10, 20  | Test both                      |
| tangential_momentum | 0.1     | Same as v20                    |
| ticks               | 50000   | Standard run                   |

## CLI

```bash
# Phase 1a: sep=10 force-on-hop
python -u v21/macro_bodies.py --phase1 --n-nodes 30000 --k 24 --radius 30 \
  --H 0.01 --star-mass 100000 --planet-mass 1 --deposit-strength 1e-5 \
  --body-base-radius 5.0 --tangential-momentum 0.1 --separation 10 \
  --ticks 50000 --weighted-spread --tag hop_sep10

# Phase 1b: sep=20 force-on-hop
python -u v21/macro_bodies.py --phase1 --n-nodes 30000 --k 24 --radius 30 \
  --H 0.01 --star-mass 100000 --planet-mass 1 --deposit-strength 1e-5 \
  --body-base-radius 5.0 --tangential-momentum 0.1 --separation 20 \
  --ticks 50000 --weighted-spread --tag hop_sep20

# Phase 1c: Time dilation (add --log-hops flag)
python -u v21/macro_bodies.py --phase1 --n-nodes 30000 --k 24 --radius 30 \
  --H 0.01 --star-mass 100000 --planet-mass 1 --deposit-strength 1e-5 \
  --body-base-radius 5.0 --tangential-momentum 0.1 --separation 10 \
  --ticks 50000 --weighted-spread --log-hops --tag timedilation

# Phase 1d: Long run (best from 1a/1b)
python -u v21/macro_bodies.py --phase1 --n-nodes 30000 --k 24 --radius 30 \
  --H 0.01 --star-mass 100000 --planet-mass 1 --deposit-strength 1e-5 \
  --body-base-radius 5.0 --tangential-momentum 0.1 --separation [10 or 20] \
  --ticks 200000 --weighted-spread --tag longrun
```

## The Deeper Point

Force-on-hop isn't a numerical trick. It's the CORRECT physics for a
discrete graph.

An entity on a graph doesn't experience continuous force. It sits at a
node. The node has connectors. The connectors have growth rates. The
entity reads them ONCE when it arrives. That reading determines its
next trajectory. Until it arrives at a new node, it has no new information.
Applying force every tick is pretending the entity has continuous access
to field information. It doesn't. It only knows what it learned at the
last node it visited.

This is also how real physics works at the quantum level. A particle
doesn't continuously sample the gravitational field. It interacts with
the field at discrete events (scattering, absorption, emission). Between
events, it propagates freely (straight worldline in curved spacetime).
The path integral formulation: sum over all possible straight segments
between interaction vertices.

v21's force-on-hop is the graph analog of the path integral: straight
propagation between discrete interaction points. The orbit emerges from
the sum of discrete corrections, not from continuous tracking.

## Predictions

1. **Velocity bounded:** |v| should stay within 2× of initial value
   at sep=10, and within 1.5× at sep=20. No runaway.

2. **Time dilation measurable:** ticks_between_hops should correlate
   with distance from star. Expect 2-5× variation between closest
   approach and farthest point.

3. **L_z sign persistence:** Angular momentum should maintain sign for
   many hops in a row (>10) instead of flipping every 2-3 hops.

4. **Energy approximate conservation:** Total energy (kinetic + potential)
   should not grow monotonically. May oscillate (perihelion/aphelion)
   but should not trend.

## File Structure

```
v21/
  experiment_description.md  (this file)
  macro_bodies.py            (copy v20, add just_hopped flag, remove drag)
  results/
```

February 2026
