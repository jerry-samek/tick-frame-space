# v13 Update: Cascade Compensation Model

## Date: February 21, 2026

## The Problem with Current Approach

The current simulation updates everything simultaneously each tick:
- All edges expand
- All gamma spreads
- All bodies read gradients
- All bodies move

This is wrong. In the real model, updates cascade through the graph causally.
Nothing happens simultaneously. Everything happens in sequence, parent before child.

## The Key Insight: Movement is Compensation for Expansion

Entities don't move because they read a gradient and decide to turn. Entities move
because their connector changed underneath them and they MUST compensate.

The sequence for a single entity in a single tick:

1. **Incoming connector expands** (edge grows by de/dt)
2. **Entity detects the change** (it's now at a different effective position)
3. **Entity compensates internally** (adjusts its state to rebalance)
4. **Entity commits** (internal processing complete)
5. **Entity propagates the result to outgoing connectors**
6. **Children receive the changed signal** → repeat from step 1 for each child

This is NOT a global field update. This is a LOCAL cascade rippling through the graph
from parent to child to grandchild.

## Transaction Model (Atomic Commit)

Each entity processes in a transaction:

```
RECEIVE: incoming connector changed (edge grew, or parent propagated)
PROCESS: internal state adjusts (compensate for the change)
COMMIT:  processing complete, state is now well-defined
PROPAGATE: push result to all outgoing connectors
```

Children see NOTHING until the parent commits and propagates. They see the RESULT
of the parent's compensation, not the raw expansion. The parent absorbs, processes,
and passes on a transformed signal.

### Mass = Processing Time

A heavy entity (mass = N) takes N ticks to complete its internal processing before
it can commit. A light entity takes fewer ticks.

```python
class Entity:
    mass: int               # N entities in the vortex
    commit_time: int        # = mass (ticks to process)
    commit_counter: int     # progress toward commit
    
    incoming_change: float  # buffered change from parent
    state: float            # current internal state
    
    def receive(self, change):
        """Parent propagated a change to our incoming connector."""
        self.incoming_change = change
        self.commit_counter = 0  # start processing
    
    def tick(self):
        """One tick of internal processing."""
        if self.incoming_change is None:
            return None  # nothing to process
        
        self.commit_counter += 1
        
        if self.commit_counter < self.commit_time:
            return None  # still processing, not ready to commit
        
        # COMMIT: apply the compensation
        compensation = self.compensate(self.incoming_change)
        self.state += compensation
        self.incoming_change = None
        
        # PROPAGATE: return what children should receive
        return self.outgoing_signal()
```

### The Cascade

```python
def cascade_tick(graph, root_expansion):
    """Process one expansion event through the graph."""
    
    # Start at root: edge expands
    queue = [(root_node, root_expansion)]
    
    while queue:
        node, change = queue.pop(0)  # BFS order = causal order
        
        entity = graph.entities[node]
        entity.receive(change)
        
        # Entity might take multiple ticks to process
        # For now, simplified: process immediately
        # Full version: entity.tick() called each global tick until commit
        
        outgoing = entity.commit()
        
        if outgoing is not None:
            for child in entity.outgoing_connectors:
                queue.append((child, outgoing))
```

## What This Changes About Gravity

### Old model (v10, wrong):
- Body reads gradient of external field
- Gradient tells it which direction to turn
- Body hops toward gradient
- This is action-at-a-distance mediated by a field

### New model (cascade, correct):
- Expansion changes the entity's incoming connector
- Entity compensates: adjusts its position/direction to rebalance
- The compensation propagates outward to children
- "Gravity" is the entity's RESPONSE to its parent's expansion pattern

The entity never reads a global field. It only knows about its own connectors.
Local information only. One hop. That's it.

### Why This Produces Attraction

Star expands. Its outgoing connectors grow. But growth is suppressed near mass
(Result 6). So connectors toward dense regions grow LESS than connectors toward
empty space.

The planet receives asymmetric changes: connector toward star grew less, connector
away from star grew more. The planet compensates by shifting toward the side that
changed less (the star side). That's attraction.

Nobody computed F = GMm/r². The planet just compensated for asymmetric expansion.

## Gravitational Time Dilation from Processing Delay

The signal cascade slows down as it passes through massive entities:

```
Edge expands (tick 0)
  → Star receives (tick 1)
  → Star processes... mass=1000, takes 1000 ticks
  → Star commits, propagates (tick 1001)
    → Planet receives (tick 1002)
    → Planet processes... mass=10, takes 10 ticks
    → Planet commits, propagates (tick 1012)
      → Moon receives (tick 1013)
      → Moon processes... mass=1, takes 1 tick  
      → Moon commits (tick 1014)
```

The moon responds 1014 ticks after the original expansion. Most of that delay
is the star's processing time. That's gravitational time dilation — not from
edge lengths, but from the commit cycle of massive entities.

Both effects exist and compound:
- **Edge-length time dilation**: shorter edges near mass = less physical distance
- **Processing time dilation**: massive entities commit slower = signal delayed

## How to Implement in v13

### Option A: Full Cascade (Correct but Complex)
- Each tick: expand one edge (or a batch)
- Cascade the change through the graph via BFS
- Each entity buffers, processes, commits, propagates
- Multiple global ticks may pass before one cascade completes
- True causal ordering

### Option B: Approximation (Simpler, may work)
- Each tick: expand ALL edges simultaneously (as before)
- BUT: process entities in causal order (root first, leaves last)
- Each entity reads ONLY its incoming connectors, not a global field
- Propagation is within the same tick but ordered
- Approximates the cascade without multi-tick delays

### Option C: Hybrid (Recommended for first attempt)
- Keep the gamma field for long-range effects (it works for force law)
- ADD the compensation mechanism: each body reads its local edge changes
  and adjusts direction based on asymmetric expansion, not gradient
- The commit delay (mass-dependent) naturally creates time dilation
- Compare results with pure-field approach to see which produces better orbits

## Key Differences from Current v13

| Feature | Current v13 | Cascade v13 |
|---------|-------------|-------------|
| What drives motion | Reading external gradient | Compensating for connector change |
| Information | Global field | Local connectors only |
| Update order | Simultaneous | Parent before child |
| Time dilation source | Edge length only | Edge length + processing delay |
| Gravity mechanism | Gradient → turning | Asymmetric expansion → compensation |

## Success Test

If the cascade model is correct, it should produce orbits WITHOUT a gradient_coupling
parameter. The coupling is built in — it's the ratio of expansion asymmetry to the
entity's compensation response. There's nothing to tune. Either the orbit emerges
from local compensation or it doesn't.

That's the real test. No tuning parameters. Just expand and compensate. If orbits
form, the theory is right. If they don't, something fundamental is wrong.

## Connection to the Dino Scene

This same cascade is how the dino renders:
- Sun expands → radiation propagates outward
- Atmosphere entities receive, process, propagate
- Surface entities receive light, compensate (absorb/scatter)
- Observer receives the final propagated signal

Same mechanism. Same cascade. Gravity and light are both compensation
cascades on the same graph. One carries density changes (gravity).
The other carries direction changes (light).
