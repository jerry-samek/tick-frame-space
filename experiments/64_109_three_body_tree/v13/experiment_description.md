# v13: Entity-Vortex Orbital Mechanics — Full RAW 170 Implementation

## Goal

Implement the core physics from RAW 170 (Entity-Vortex Theory) and test whether
a three-body system (star + planet + moon) produces Keplerian dynamics on a graph
WITHOUT any Newtonian equations.

The target: reproduce the trajectory from v12's Newtonian reference simulation
(three_body_trajectory.png) using only graph rules.

## What We Learned from v10 (Read This First)

v10 achieved stable orbits but exposed critical issues:

1. **Constant speed + uniform lattice = no stable orbits.** Without variable edge
   length, there's no restoring force for radial perturbations. All parameter sweeps
   produced chaotic scattering (50-80 reversals, ranges 2-40 hops).

2. **Time dilation stabilizes orbits.** When edge length varies with local gamma
   density (shorter near mass), bodies effectively slow in the well. This prevents
   runaway infall. Achieved 433 stable revolutions at r~2.

3. **BUT only at lattice minimum.** The stable orbit always collapsed to r~2 regardless
   of starting separation. Only one "shell" — the lattice floor. No orbits at larger radii.

4. **Force law n ≈ 2.2** in mid-field (r=3-20) on k=6 cubic lattice. The 0.2 excess over
   Newton's 2.0 is lattice anisotropy. Far field steepens to ~3.5 (propagation horizon).

5. **Square orbits** from k=6 lattice (4 in-plane directions).

6. **Gravity is turning rate, not acceleration.** Bodies move at v = c/M always. Gradient
   changes direction, not speed. This is GR geodesic motion.

## The Theory (RAW 170 Essentials for Implementation)

### Core Axiom
Entities hop at c = 1 hop/tick on an expanding graph. Forward vector deflected by
local density gradient via integer Bresenham accumulator.

### Result 6: The Edge Length Equation (CRITICAL)
```
de/dt = 1 / (1 + α × M/r)
```
- In vacuum (M=0 or r=∞): de/dt = 1 → full expansion
- Near mass: de/dt → 0 → expansion suppressed
- NEVER negative — edges can slow but never shrink

This is the metric tensor. Variable edge length = variable geometry = GR.

### What Variable Edge Length Does for Orbits
- Near mass: edges are short → hop covers less physical distance → body effectively
  slower → spends more time near mass → gradient has more time to turn it
- Far from mass: edges are long → hop covers more distance → body effectively faster
  → gradient has less turning time

This creates the speed variation that Kepler orbits need — NOT by changing hop rate
(always 1 per tick) but by changing what each hop MEANS physically.

### Result 21: F = ma from Atomic Commit
A vortex of N entities completes one internal rotation in N ticks. This is the commit
cycle. The vortex reads gradient every tick but only updates macroscopic direction
once per cycle.

For macro bodies: commit_mass = N. Body hops once every N ticks. Speed = c/N.
Heavier body = slower. Same as v10.

### Accelerating Expansion (Updated Result 16)
Early universe: dense → expansion suppressed globally → slow expansion
Late universe: mass dilutes → suppression lifts → expansion accelerates
No dark energy needed — acceleration comes from mass getting out of the way.

For the simulation: H increases over time as average density drops.

## v13 Architecture

### Graph Structure
Use a 3D lattice BUT with variable edge weights.

```python
class Node:
    position: np.ndarray       # 3D coordinates (for visualization only)
    neighbors: list[int]       # connected node indices
    edge_lengths: list[float]  # length of each edge (VARIABLE, key innovation)

class Graph:
    nodes: list[Node]
    side: int                  # lattice side length
    
    def expand(self, bodies):
        """Each tick, grow all edges. Suppress near mass."""
        for node in self.nodes:
            for i, neighbor in enumerate(node.neighbors):
                # Result 6: de/dt = 1 / (1 + α × M/r)
                local_mass_influence = 0.0
                for body in bodies:
                    r = distance_in_hops(node, body.node)
                    if r > 0:
                        local_mass_influence += body.mass / r
                
                growth = H / (1.0 + alpha * local_mass_influence)
                node.edge_lengths[i] += growth
```

### Macro Bodies (Same concept as v10, improved)
```python
class MacroBody:
    node: int                    # current graph node
    mass: float                  # determines commit cycle and deposit strength
    internal_dir: np.ndarray     # continuous 3D direction vector
    hop_accumulator: np.ndarray  # Bresenham accumulator for sub-axis movement
    commit_counter: int          # ticks since last hop
    commit_mass: int             # ticks per hop (= mass proxy)
    
    # NEW: track physical distance traveled
    physical_distance: float     # sum of edge lengths traversed
```

### Gamma Field
Same as v10: continuous float64 field with self-subtraction.

```python
class GammaField:
    values: dict[int, dict[int, float]]  # node → {source_id: gamma_value}
    
    def deposit(self, node, source_id, amount):
        """Body deposits gamma at its current node."""
        
    def spread(self, graph):
        """Spread gamma along edges. KEY: spread rate depends on edge length."""
        # Shorter edges → faster spread (more gamma per tick)
        # Longer edges → slower spread (gamma takes longer to cross)
        # spread_amount = gamma * spread_rate / edge_length
        
    def gradient(self, node, exclude_source, graph):
        """Gradient accounts for edge length in neighbor weighting."""
        # Neighbor gamma values weighted by 1/edge_length
        # Closer neighbors (shorter edges) contribute more to gradient
```

### Movement: The Critical Change from v10

v10 treated every hop as equal physical distance. v13: each hop's physical meaning
depends on the edge length.

```python
def advance(body, graph, gamma_field):
    body.commit_counter += 1
    
    if body.commit_counter < body.commit_mass:
        return  # not ready to hop yet
    
    body.commit_counter = 0
    
    # 1. Read gradient (exclude self)
    grad = gamma_field.gradient(body.node, body.source_id, graph)
    
    # 2. Nudge internal direction (turning rate = gradient strength)
    #    Scale by edge length: shorter edges = stronger effective gradient
    local_edge_avg = average_edge_length(graph, body.node)
    effective_gradient = grad / local_edge_avg  # stronger where edges are short
    
    body.internal_dir += gradient_coupling * effective_gradient
    body.internal_dir /= np.linalg.norm(body.internal_dir)
    
    # 3. Bresenham hop selection (same as v10)
    body.hop_accumulator += body.internal_dir
    hop_axis = argmax(abs(body.hop_accumulator))
    hop_sign = sign(body.hop_accumulator[hop_axis])
    body.hop_accumulator[hop_axis] -= hop_sign
    
    # 4. Hop to neighbor along chosen axis
    neighbor, edge_length = graph.get_neighbor(body.node, hop_axis, hop_sign)
    body.node = neighbor
    
    # 5. Track physical distance (for diagnostics)
    body.physical_distance += edge_length
```

### The Speed Variation Mechanism (Why This Produces Orbits)

Body hops at 1 hop per commit_mass ticks. Always. But:

- Near star: edges are short (expansion suppressed) → physical distance per hop is small
  → effective physical speed is LOW
- Far from star: edges are long (full expansion) → physical distance per hop is large
  → effective physical speed is HIGH

The body is FASTER at apoapsis and SLOWER at periapsis. Not because hop rate changes.
Because the ruler changes size. This is Kepler's second law (equal areas in equal times)
from graph geometry.

## Experiment Phases

### Phase 0: Verify Edge Expansion
- Place single massive body at center
- Run expansion for 10,000 ticks
- Measure edge length vs distance from mass
- Expected: edges near mass stay short, edges far away grow
- Plot: edge_length(r) — should show suppression near mass matching Result 6

### Phase 1: Two-Body with Variable Edges
- Star (mass=1000) at center, planet (mass=1) at r=15
- Tangential initial momentum
- Run 50,000 ticks
- Measure: orbital radius over time, period, eccentricity
- Compare with Newtonian prediction for same mass ratio and separation
- SUCCESS: planet maintains orbit at r≈15 (not collapsing to r=2 like v10)
- STRONG SUCCESS: orbital period matches T² ∝ r³

### Phase 2: Force Law with Variable Edges
- Measure gradient at various distances from central mass
- WITH variable edge lengths (not uniform lattice)
- Expected: edge length weighting should correct the 2.2 exponent toward 2.0
- This tests whether variable edges fix the lattice anisotropy

### Phase 3: Three-Body (The Target)
- Star (mass=1000) at center
- Planet (mass=10) at r=15, tangential velocity for circular orbit
- Moon (mass=0.1) at r=3 from planet, tangential velocity for planet-orbit
- Run 200,000 ticks
- Plot XY trajectories
- Compare with v12 Newtonian reference (three_body_trajectory.png)
- SUCCESS: planet orbits star, moon orbits planet
- STRONG SUCCESS: moon shows epicyclic pattern matching reference

### Phase 4: Kepler Verification
- Run multiple two-body experiments at different separations (r=10, 15, 20, 25, 30)
- Measure orbital period at each
- Plot T² vs r³
- SUCCESS: linear relationship (Kepler's third law)

### Phase 5: Expansion Effects
- Run two-body orbit with H > 0
- Measure: does orbit gradually widen as edges grow?
- At what H does the orbit unbind? (cosmological constant analog)
- Does orbital period change as expansion proceeds?

## Parameters to Tune

| Parameter | Starting Value | Role |
|-----------|---------------|------|
| side | 80 | Lattice size (512K nodes) |
| k | 6 | Neighbors (start cubic, upgrade later) |
| H | 0.001 | Expansion rate per tick |
| alpha | 1.0 | Expansion suppression strength |
| G | 0.0 | Self-gravitation (start without) |
| gradient_coupling | TBD | Turning rate per unit gradient |
| star_mass | 1000 | Heavy central body |
| planet_mass | 10 | Intermediate |
| moon_mass | 0.1 | Light |
| deposit_strength | 1.0 | Gamma per tick per unit mass |
| formation_ticks | 10000 | Field establishment before dynamics |

### Tuning Strategy (IMPORTANT — avoid v10's blind sweeps)

1. First get Phase 0 working — verify edge expansion profile matches Result 6
2. Then Phase 1 — tune gradient_coupling so planet orbits at r≈15, not r≈2
3. The KEY tuning: gradient_coupling × gradient(r=15) / avg_edge_length(r=15) ≈ v_planet / r
   This balances turning rate with orbital velocity. Calculate it BEFORE running.
4. If orbit collapses: coupling too strong OR time dilation too weak (increase alpha)
5. If orbit escapes: coupling too weak OR time dilation too strong (decrease alpha)
6. Do NOT sweep randomly. Calculate expected values from the theory and test those.

## What's Different from v10

| Feature | v10 | v13 |
|---------|-----|-----|
| Edge lengths | Uniform (all = 1) | Variable (expansion + suppression) |
| Speed variation | None (constant c/M) | Physical speed varies with edge length |
| Orbital stability | Only at lattice minimum (r=2) | Should work at any radius |
| Orbit shape | Square (k=6 artifact) | Should be rounder (edge weighting) |
| Force law | 2.2 on uniform lattice | Closer to 2.0 with edge correction |
| Three-body | Not attempted | Primary target |
| Expansion | Gamma dilution only | Geometric (edge growth) |

## Success Criteria

- **PASS**: Stable two-body orbit at r > 5 (not collapsed to lattice minimum)
- **STRONG PASS**: T² ∝ r³ verified at 3+ radii, three-body shows hierarchy
- **EXCEPTIONAL**: Three-body trajectory qualitatively matches Newtonian reference
- **FAIL**: All orbits collapse to r~2 (same as v10 = edge length variation insufficient)

## Files

```
experiments/64_109_three_body_tree/
├── v12/                          (Newtonian reference — the target)
│   └── three_body_trajectory.png
├── v13/                          (this experiment)
│   ├── experiment_description.md (this file)
│   ├── macro_bodies.py           (main simulation — build from v10 base)
│   └── results/
└── 170_entity_vortex_theory.md   (the theory — READ THIS for context)
```

## Key Principle

Everything emerges from the edge length equation:
```
de/dt = 1 / (1 + α × M/r)
```

This single equation gives:
- Time dilation (shorter edges near mass = slower physical clock)
- Gravitational potential (edge length profile = metric)
- Orbital speed variation (faster far, slower near)
- No singularities (de/dt ≥ 0 always)
- Expansion (H > 0 in vacuum)

If v13 works, it confirms that one equation + one graph rule (hop and turn) produces
planetary mechanics. If it fails, we know which part of RAW 170 needs revision.
