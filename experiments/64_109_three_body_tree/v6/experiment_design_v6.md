# Experiment 64_109 V6: Entity as Gamma Pattern — Self-Sustaining Field Structures on a Graph

## Status: DESIGN — ready for implementation

## Core Question

Can a self-sustaining gamma peak on a graph reproduce the gravitational dynamics of Experiment 65 WITHOUT a separate entity object?

If yes: the entity/field distinction is artificial. There is only gamma on a graph. Matter is bound gamma. Light is free gamma. Mass is how much gamma is in the clump. Energy conservation is gamma conservation.

## Motivation: Why Experiment 65 Saturates

Experiment 64_109 (v1-v3) demonstrated gravity, binding, hierarchical triples, and orbital dynamics on a pure graph. But the energy accounting doesn't close:

- Entities deposit gamma into the field every tick → gamma grows without bound
- Field saturates → dynamics slow down
- No back-reaction → gamma doesn't attract gamma
- Entity and field are separate objects → energy appears from external source

The root cause: the entity is a faucet, the field is a bathtub. Of course it fills up.

In general relativity, mass IS spacetime curvature. The particle IS the field configuration. There is no separate object creating a field. The field is the object.

## The Model: Gamma-Only Physics

### No Entities. Only Gamma.

Remove the entity object entirely. The simulation contains:
- A graph (nodes + edges)
- A scalar gamma value at each node
- A spread rule
- A self-gravitation rule

Nothing else. No entity position. No entity KE. No entity mass. No deposits. No withdrawals.

### Initial Conditions

Place three gamma peaks on the graph — concentrated gamma at three separated regions:

```
Peak A: nodes near node 1000, total gamma = M_A
Peak B: nodes near node 2000, total gamma = M_B  
Peak C: nodes near node 3000, total gamma = M_C
```

Each peak is a Gaussian-like distribution over ~5-10 nodes centered on the peak node. The shape doesn't matter much — self-gravitation will reshape it.

### The Two Competing Rules

Each tick, two things happen to gamma at every node:

**1. Spread (diffusion)** — gamma flows to neighbors, trying to flatten the field:

```
For each node n:
    outflow = spread_rate * gamma[n]
    distribute outflow equally to all neighbors
```

This dissolves structure. Without opposition, every peak flattens to uniform background in O(diameter) ticks.

**2. Self-gravitation (contraction)** — gamma flows TOWARD regions of high gamma:

```
For each node n:
    For each neighbor m:
        if gamma[m] > gamma[n]:
            flow toward m proportional to (gamma[m] - gamma[n])
```

This concentrates structure. Gamma flows uphill — toward peaks, not away from them.

### The Balance

- **Spread alone**: everything flattens. No structure. No particles. Heat death.
- **Self-gravitation alone**: everything collapses to one node. Singularity. Big crunch.
- **Both together**: a self-sustaining peak. The spread tries to dissolve it. The self-gravitation holds it together. The balance IS the particle.

The ratio of spread_rate to gravitation_rate determines whether structures are stable:
- Too much spread → peaks dissolve → no matter exists
- Too much gravitation → everything collapses → singularity
- Balance → stable peaks that persist, move, and interact

Finding this balance point is the primary experimental objective.

### Movement

Nobody moves the peak. The peak moves itself.

When two peaks are nearby, the gradient from peak B biases the gamma flow around peak A. Gamma on the B-facing side of A gets reinforced. Gamma on the far side gets less support. The net effect: peak A shifts toward B. One node per tick, maximum. Speed of light.

Movement isn't an entity hopping between nodes. It's the gamma distribution asymmetrically redistributing itself in response to gradients from other peaks. The "position" of the entity is wherever the peak currently is. The "velocity" is how fast the peak is shifting. The "momentum" is the asymmetry of the distribution — a peak leaning one direction will keep shifting that way even after the external gradient changes, because the internal gamma flow takes time to rebalance.

Inertia falls out for free. A heavier peak (more total gamma) has more internal gamma flow to redirect. It takes longer to change its drift direction. That's F = ma. Not programmed. Emergent from the time it takes to rebalance a larger gamma distribution.

### Mass

Mass = total gamma in the peak.

```
M = sum(gamma[n] for n in peak_nodes)
```

No separate counter. No property on an entity. Mass is literally how much field you are.

A heavier peak:
- Has a deeper gamma well → attracts more strongly (gravity ∝ mass)
- Takes longer to redirect → more inertia (inertia ∝ mass)
- Spreads more slowly → more stable (binding energy ∝ mass)
- Creates stronger gradients → larger influence radius

All four properties of mass from a single quantity: total gamma.

### Radiation

Gamma that escapes the self-sustaining structure = radiation.

The balance between spread and self-gravitation isn't perfect. Some gamma leaks from the edge of each peak every tick. This leaked gamma spreads freely through the graph at one hop per tick. It's not bound. It doesn't self-gravitate (too dilute). It propagates at c.

That's a photon. A photon is gamma that escaped a bound structure.

A peak that moves fast (large asymmetry) leaks more gamma from its trailing edge — the redistribution can't keep up. That's Bremsstrahlung. Accelerating charges radiate because the gamma pattern can't maintain itself during rapid repositioning.

No explicit radiation mechanism. No drain. No Bremsstrahlung formula. Just: gamma that fails to stay bound to the peak. The physics decides what radiates. We don't.

### Energy Conservation

Total gamma is conserved. Always. No creation, no destruction.

```
sum(gamma[n] for ALL nodes) = constant at every tick
```

This is the ONLY conservation law needed. Everything else follows:

- Mass conservation: if peaks don't merge or shed gamma, their total gamma is constant
- Energy conservation: gamma redistributes but never appears or disappears
- Radiation carries energy: gamma leaving a peak reduces its mass (E = mc² as gamma accounting)
- Gravitational potential energy: when two peaks approach, their combined gamma distribution is more concentrated → the "saved" spread energy goes into kinetic energy of the peaks (asymmetric redistribution)

The saturation problem vanishes because there are no deposits. The total gamma was set at initialization and never changes.

## Implementation

### Graph Setup

Same as Experiment 65:
- Lattice graph: N ≈ 50,000 nodes, k = 6 neighbors
- Watts-Strogatz with low rewiring to maintain local dimensionality

### Gamma Initialization

Three peaks, each a Gaussian-like blob:

```python
def initialize_peak(graph, center_node, total_mass, radius=5):
    """Distribute total_mass as a peaked distribution around center_node."""
    distances = bfs_distances(graph, center_node)
    for node, d in distances.items():
        if d <= radius:
            gamma[node] = total_mass * exp(-d**2 / (2 * sigma**2))
    # Normalize so sum = total_mass
    normalize(gamma, peak_nodes, total_mass)
```

### Tick Update

```python
def tick(gamma, graph, spread_rate, grav_rate):
    new_gamma = gamma.copy()
    
    for node in graph.nodes:
        for neighbor in graph.neighbors(node):
            # Spread: flow from high to low (diffusion)
            spread_flow = spread_rate * (gamma[node] - gamma[neighbor])
            
            # Self-gravitation: flow from low to high (contraction)
            # Only when neighbor has MORE gamma (flow toward peaks)
            if gamma[neighbor] > gamma[node]:
                grav_flow = grav_rate * (gamma[neighbor] - gamma[node])
            else:
                grav_flow = 0
            
            # Net flow: spread pushes out, gravitation pulls in
            net_flow = spread_flow - grav_flow
            
            new_gamma[node] -= net_flow / k  # distribute among neighbors
            new_gamma[neighbor] += net_flow / k
    
    # Verify conservation
    assert abs(sum(new_gamma) - sum(gamma)) < 1e-10
    
    return new_gamma
```

**CRITICAL**: The update must be transactional. Read from committed state (gamma), write to new state (new_gamma). Swap at tick boundary. Same commit semantics as all previous experiments.

### Key Parameters

| Parameter | Starting value | Role |
|-----------|---------------|------|
| spread_rate | 0.01 - 0.1 | How fast gamma diffuses (destroys structure) |
| grav_rate | 0.01 - 0.1 | How fast gamma self-attracts (creates structure) |
| total_mass_per_peak | 100 - 10000 | How much gamma in each initial peak |
| peak_radius | 3 - 10 nodes | How spread out the initial peak is |
| separation | 15 - 30 hops | Initial distance between peak centers |

The critical ratio is **grav_rate / spread_rate**. This determines the regime:
- ratio < 1: spread wins, peaks dissolve
- ratio ≈ 1: metastable peaks, interesting dynamics
- ratio > 1: gravitation wins, everything collapses
- ratio >> 1: instant singularity

The experiment should sweep this ratio to find the stable regime.

## Measurements

### Phase 1: Can a single peak sustain itself?

Before three-body dynamics, verify that ONE peak survives:

1. Initialize single peak with mass M at center of graph
2. Run 10K ticks
3. Measure: does the peak persist? Does it dissolve? Does it collapse?
4. Find the spread_rate / grav_rate ratio where the peak is stable

**Success**: Peak maintains its shape (total gamma within peak region stays > 90% of initial) for 10K ticks without collapsing to a single node.

### Phase 2: Do two peaks attract?

1. Initialize two peaks separated by 20 hops
2. Run 50K ticks
3. Measure: do the peaks move toward each other? Do they merge? Do they orbit?

**Success**: Peaks approach each other (gravity). If they have initial tangential asymmetry, they orbit.

### Phase 3: Three-body dynamics

1. Initialize three peaks in equilateral configuration
2. Run 100K ticks
3. Measure same metrics as Experiment 65: distances, encounters, reversals, binding

**Success criteria** (same as Experiment 65):

| Criterion | Description |
|-----------|-------------|
| PASS | Peaks attract, bind, produce encounters |
| STRONG PASS | Hierarchical triple or chaotic exchange |
| EXCEPTIONAL PASS | Energy conservation verified to machine precision |
| FAIL | Peaks dissolve or immediately collapse |

### Phase 4: Radiation detection

1. During three-body dynamics, measure gamma outside all three peak regions
2. If gamma is increasing in the "background" (far from all peaks), that's radiation
3. Verify: radiation gamma + bound gamma = constant (energy conservation)

**Success**: Detectable radiation during close encounters. Total gamma conserved.

### Phase 5: Mass change

1. Track total gamma within each peak region over time
2. During close encounters, does gamma transfer between peaks?
3. After radiation events, does peak mass decrease?

**Success**: Mass changes correlate with energy exchange. Radiation carries mass away from peaks.

## What This Would Prove

### If it works:

1. **Entity/field unification**: There is no entity. There is only gamma. Matter is self-bound gamma. The point-particle approximation (Experiments 64-65) was useful scaffolding but not fundamental.

2. **Energy conservation from gamma conservation**: The saturation problem vanishes. Total gamma is constant. Energy isn't created or destroyed, just redistributed between bound (mass) and free (radiation) forms.

3. **E = mc²**: The energy of a peak IS its mass (total gamma). When a peak radiates, it loses mass. When peaks merge, combined mass can be less than sum of parts — the difference radiated away. That's binding energy. That's nuclear physics.

4. **Radiation as escaped gamma**: Bremsstrahlung, synchrotron radiation, gravitational radiation — all the same thing: gamma that the bound structure couldn't hold onto during acceleration. No separate radiation mechanism needed.

5. **Back-reaction**: Gamma attracts gamma. The field gravitates. This is the missing piece from Experiment 65. GR's key insight — energy curves spacetime — implemented as gamma flow toward gamma peaks.

6. **Self-gravity = stability**: The reason matter exists at all is because gamma can attract itself strongly enough to resist diffusion. The balance point between spread and self-gravitation IS the particle. If the universe's spread_rate were slightly higher, nothing would hold together. If grav_rate were slightly higher, everything would collapse. The fact that stable matter exists constrains the ratio.

### If it fails:

- Peaks dissolve → self-gravitation mechanism is wrong. Need different contraction rule.
- Peaks collapse to points → need repulsive core at short range (quantum pressure analog).
- No movement → peak redistribution doesn't produce drift. Need to revisit movement mechanism.
- No binding → inter-peak attraction too weak. Need to adjust initialization or parameters.

Even failure is informative. It would tell us exactly which property of matter requires something beyond gamma-on-a-graph.

## Connection to Theory

- **RAW 108**: Dimensionality from trit. Self-gravitating peaks need D(n) ≥ 3 to orbit instead of collapse — same requirement as Experiment 65.
- **RAW 109**: c from topology. Gamma propagation at one hop per tick. Peak movement speed ≤ c.
- **RAW 110**: Local dimensionality. Peak stability may depend on local D(n). Peaks in D=1 regions collapse (black holes). Peaks in D=3 regions orbit.
- **Early documents**: Mass as temporal footprint. The peak's "pattern length" is how many ticks it takes for the internal gamma flow to complete one circulation. That's the mass.

## Relationship to the Anemone Model

Experiment 66 is not the anemone model. The graph is still pre-built.

But if Experiment 66 succeeds, the anemone model (Experiment 67) becomes clear:
- Start with no graph
- A gamma peak creates nodes around itself (deposits create space)
- Self-gravitation holds the created nodes together
- Two peaks' node-creation zones overlap → connection forms → attraction begins
- The graph grows FROM the gamma, not the other way around

Experiment 66 is the last step before the graph itself becomes emergent.

## Estimated Effort

- Phase 1 (single peak stability): 1-2 hours
- Phase 2 (two-body attraction): 2-3 hours  
- Phase 3 (three-body dynamics): 3-4 hours
- Phase 4-5 (radiation and mass tracking): 1-2 hours
- Parameter sweeps: 2-3 hours

Total: 1-2 days at 620 t/s. Most time is parameter tuning, not waiting for results.

## Dependencies

- Experiment 64_109 v5 codebase (graph infrastructure)
- RAW 110 (local dimensionality requirement)

## Key Principle

> **There is no entity. There is no field. There is only gamma on a graph.**
> **Some gamma clumps. That's matter.**
> **Some gamma flows. That's light.**
> **The clumps attract each other. That's gravity.**
> **The clumps resist dissolution. That's mass.**
> **The balance between spread and self-attraction IS the universe.**
