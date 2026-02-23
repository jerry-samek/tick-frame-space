# v16 Theoretical Context: The Trit Stream + Velocity Fix

## For Code — from Tom and Claude.ai's discussion, February 22, 2026

## The Insight Chain

Today's session moved fast. Here's the chain of realizations that led to v16,
so you understand WHY we're dropping the lattice, not just HOW.

### 1. Two brains → one brain (v14 → v15)

v14 had two mechanisms: cascade drift (reads instantaneous growth rates) and
geodesic frame rotation (reads accumulated edge lengths). v14's own results
showed cascade drift was the dominant binding mechanism — the accumulated
edge profile flattened to 1% variation but bodies stayed bound.

A real entity has one mechanism, not two. v15 kept only the growth asymmetry
nudge. One buffer, one rule.

### 2. One brain works for gravity, fails for orbits (v15 results)

v15 confirmed: growth asymmetry IS gravity. Radial oscillation. Binding.
But tangential motion died. Initial tangential nudge of 0.3 never reached
the ±1 hop threshold. Every configuration radially collapsed.

The tangential component doesn't get replenished because on a k=6 cubic
lattice, the growth asymmetry toward the star is PURELY along one axis.
The ±y and ±z connectors see symmetric growth. No off-axis signal.

### 3. The lattice IS the problem (not the mechanism)

Every failure in v13-v15 traces to axis quantization:
- Chaotic orbits → lattice corners flip angular momentum
- Pi not 2pi → axis-aligned fractional asymmetry can't close
- Tangential death → radial locks to one axis, off-axis signal is zero

The cubic lattice forces every push into ±x, ±y, or ±z. The tangential
component of gravity gets quantized away. Then we built frame rotation
as a patch to re-inject what the lattice destroyed. That's backwards.

### 4. On a real graph, connector ID IS the axis

This is the key insight. On the lattice, connector 0 means "+x" at EVERY
node. That's global. That's the bug.

On a random geometric graph, connector 0 at node A points northeast.
Connector 0 at node B points south. The connector ID means something
different at every node.

So the entity doesn't compute "radial" or "tangential." It just sees:
connector 3 grew least, I go there. At the next node, connector 1 grew
least, I go there. The direction naturally rotates because connector-to-
geometry mapping changes at every node.

**There is no "tangential component to provide." There's just "which
connector grew least." The orbit is a sequence of connector IDs.**

### 5. Position is a ledger, orbit is a rhythm

There are no positions. No coordinates. No vectors. Just deltas.

An entity's history is a stream of trits per connector:
- **0** = stayed (connector maintained, nothing changed)
- **+1** = hopped forward through this connector
- **-1** = hopped backward through this connector

The entity's "position" is just the running sum of all its deltas since
tick 0. No grid. No x,y,z. No map. A ledger of hops.

An orbit isn't a circle in space. It's a REPEATING PATTERN in the delta
stream:

```
Radial fall:   -1, -1, -1, -1, -1, ...      (monotone)
Straight line: +1, +1, +1, +1, +1, ...      (monotone)
Orbit:         +1, +1, 0, -1, -1, 0, +1...  (periodic)
```

### 6. The universe is maximally compressed

Everything we compute — gamma fields, edge lengths, growth rates, nudge
buffers — these are DERIVED quantities. Running totals. Caches for
convenience. The minimum description: one trit per connector per tick.
{-1, 0, +1}. Everything else is a pattern in that stream.

## CRITICAL FIX: Velocity vs Displacement

### The problem (from v16 Phase 1 diagnostic)

The random graph WORKS for direction — tangential hops happen naturally.
But momentum dissipates: |p| drops from 10.0 to 3.5 in 48 hops. Planet
spirals inward. Always collapses.

The bug: each hop SUBTRACTS 1.0 from the nudge buffer. That's subtracting
from MOMENTUM. In real physics, moving doesn't slow you down. A planet at
velocity v takes a step and is still at velocity v. The hop is the RESULT
of momentum, not the COST.

The current (broken) model:
```
buffer = 10.0    (momentum)
hop → buffer = 9.0   (lost 1.0)
hop → buffer = 8.0   (lost 1.0)
... 10 hops later, buffer = 0. Dead stop.
```

That's friction. Every hop grinds the entity to a halt.

### The fix: two integrations, not one

The nudge buffer was doing one integration: Force → Position (F→x).
Physics needs two: Force → Velocity → Position (F→v→x).

```python
def advance(self, graph, tick):
    """One tick. One mechanism. Two integrations."""
    
    graph.deposit(self.node, self.bid, self.deposit_rate)
    
    # FIRST INTEGRATION: Force → Velocity
    # Growth asymmetry changes velocity (not position directly)
    for nb, edge_idx in graph.get_neighbors(self.node):
        growth = graph.last_growth[edge_idx]
        mean_growth = mean_growth_at_node  # average of all connectors
        force = (mean_growth - growth) / self.inertia
        self.velocity[nb] = self.velocity.get(nb, 0.0) + force
    
    # SECOND INTEGRATION: Velocity → Displacement
    # Velocity accumulates into displacement every tick
    for nb in self.velocity:
        self.displacement[nb] = self.displacement.get(nb, 0.0) + self.velocity[nb]
    
    # HOP: when displacement reaches ±1
    # Subtract from DISPLACEMENT, not velocity!
    # Velocity persists — entity keeps moving after hop
    best_nb = max(self.displacement, key=lambda k: abs(self.displacement[k]))
    if abs(self.displacement[best_nb]) >= 1.0:
        sign = 1 if self.displacement[best_nb] >= 0 else -1
        self.displacement[best_nb] -= sign   # reset displacement
        # self.velocity is UNTOUCHED — entity keeps its speed
        
        self._transfer_momentum(graph, self.node, best_nb)
        graph.move_gamma(self.bid, self.node, best_nb)
        self.node = best_nb
        self.hops += 1
```

### Why this is still stupid

The entity has two accumulators instead of one. But both do the same thing:
add a number every tick, threshold at ±1. Same trit logic:

1. Force trickles into velocity (slow change — acceleration)
2. Velocity trickles into displacement (steady change — motion)
3. Displacement overflows → hop (discrete event — position change)

A trit can do this. Two counters instead of one. Still no trigonometry,
no frame rotation, no normalization. Just: add, add, threshold.

### What this means physically

- **velocity** per connector = entity's momentum decomposed into connector directions
- **displacement** per connector = how close to the next hop in that direction
- **force** per connector = growth asymmetry this tick

The velocity accumulator IS inertial motion. Without any force, velocity
persists → displacement keeps growing → entity keeps hopping in the same
direction forever. Newton's first law from a counter.

Force (growth asymmetry) changes velocity. Velocity changes displacement.
Displacement triggers hops. F = ma from two counters.

### Momentum transfer on hop

Same as before (Approach 1: geometric projection). But now transfer BOTH
velocity AND displacement to new node's connectors:

1. Convert old velocity dict → 3D vector (using connector directions)
2. Project 3D velocity onto new node's connectors → new velocity dict
3. Same for displacement
4. Carry residual in momentum_3d to prevent loss

### The prediction

With velocity persistence:
- Initial tangential kick → velocity in tangential direction
- Velocity persists across hops (not consumed)
- Radial force adds radial velocity component each tick
- Tangential velocity stays (no force in that direction by symmetry)
- Result: tangential + radial = curved path = ORBIT

This is literally Newton's cannon. Fire a ball horizontally. It falls
but keeps moving sideways. If sideways speed is right, it curves around
the Earth. The only thing v16 adds to v15 is: the sideways speed doesn't
disappear when you take a step.

### Diagnostic to add

Log per hop:
- |velocity_3d| (should be roughly constant for circular orbit)
- |displacement| at moment of hop
- angle of velocity relative to radial direction
- trit stream: (tick, connector_id, +1/-1) for each hop

If |velocity| stays constant while direction rotates → orbit.
If |velocity| decays → still losing momentum somewhere.
If direction doesn't rotate → back to lattice problem.

## Connection to Earlier Ideas

### "m" as receiver bandwidth

Tom identified that "m" in F=GMm/r² is connector count, not mass.
In v16, each connector independently accumulates force. More connectors =
more total force received. But more connectors also = more total inertia
(the force divides by inertia per connector). They cancel → equivalence
principle → universal free fall.

### The connector is the photon

From earlier RAW 170 work: the connector IS the photon, not a conduit.
In v16, the connector's growth rate IS the gravitational signal. The
entity doesn't receive a message through the connector. It reads the
connector's own state (how much it grew). The medium is the message.

### Totally bulletproof and totally stupid

The mechanism: add force to velocity. Add velocity to displacement.
Hop when displacement overflows. Transfer momentum to new connectors.

A rock can run this. Two counters per connector. No decisions. No
branching. No special cases. The orbit emerges from counting.

## Summary for Implementation

1. Entity has TWO dicts: velocity{} and displacement{}
2. Each tick: force → velocity (first integration)
3. Each tick: velocity → displacement (second integration)
4. Hop when displacement overflows (subtract from displacement, NOT velocity)
5. On hop: project both velocity and displacement to new connectors
6. Everything else (graph, gamma, edge growth) stays the same
7. Log |velocity|, direction angle, trit stream for diagnostics
