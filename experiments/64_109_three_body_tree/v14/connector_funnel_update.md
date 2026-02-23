# v14 Update: Connector Funnel Topology

## Date: February 21, 2026

## The Problem

Phase 0 showed the gamma pipe problem: all curvature within r=0-3, flat beyond.
Gamma drops from 10^6 to 10^-2 in 2-3 hops. Self-gravitation concentrates gamma
near the source. A planet at r=10 sees uniform edges — no tilt, no binding.

Tuning G doesn't fix it. Low G: gamma spreads but too thin. High G: gamma stays
concentrated. No sweet spot gives an hourglass profile.

## The Solution: Connector as a Narrowing Funnel

The 1/r² force law shouldn't come from gamma decaying through 3D space. It should
come from the connector TOPOLOGY narrowing with distance.

### The Hourglass Shape

A connector between two bodies is a bundle of parallel paths:

```
Star end:     ████  (4 parallel paths — wide, high bandwidth)
r = 5:        ██    (2 paths — narrowing)
Midpoint:     █     (1 path — bottleneck)
r = 15:       ██    (2 paths — widening toward planet)
Planet end:   ████  (4 paths — wide again)
```

Gamma flows at FULL STRENGTH through every path. But there are fewer paths at
distance. Total signal weakens because the funnel narrows, not because gamma decays.

This IS Gauss's law: flux through a sphere at radius r spreads over 4πr² area.
More paths near source (small sphere), fewer far away (big sphere).

### Why Connectors Narrow: Maintenance Cost

Connectors must be FED and MAINTAINED by ticks. Each path costs energy to keep
alive per unit length.

- At r=1: star can maintain 4 paths (short, cheap)
- At r=10: maintaining 4 paths costs 10× more per path
- At r=20: budget only supports 1 path

The hourglass shape is the STEADY STATE of a connector under energy budget
constraints. Wide where energy is abundant (near mass), narrow where energy
is scarce (far from mass).

Path count at radius r ∝ 1/r (maintenance budget from 3D energy dilution).
Signal per path = constant (full strength).
Total signal at r ∝ 1/r.
Force = gradient of signal ∝ 1/r².

### Implementation

Instead of spreading gamma uniformly through all 6 neighbors every tick,
gamma should CREATE and MAINTAIN directed paths.

#### Option A: Active Edge Model

Each edge has an "active" state based on local gamma flow:

```python
def spread_with_maintenance(self):
    """Gamma flows through maintained paths, not uniform diffusion."""
    for node in range(self.n_nodes):
        gamma_here = self.gamma[node]
        
        # How many outgoing paths can this node maintain?
        # More gamma = more paths affordable
        max_paths = min(6, max(1, int(gamma_here / maintenance_cost)))
        
        # Sort neighbors by gamma gradient (preferring downhill flow)
        neighbor_gammas = [(d, self.gamma[self.neighbor_dirs[node, d]])
                          for d in range(6) if self.neighbor_dirs[node, d] >= 0]
        neighbor_gammas.sort(key=lambda x: x[1])  # lowest gamma first = steepest downhill
        
        # Flow gamma through top max_paths directions only
        active_dirs = [d for d, g in neighbor_gammas[:max_paths]]
        
        flow_per_path = gamma_here * spread_alpha / len(active_dirs)
        for d in active_dirs:
            nb = self.neighbor_dirs[node, d]
            # transfer flow_per_path from node to nb
```

This naturally creates a funnel: near the star, gamma is high → 6 active paths
(spherical spread). Far from star, gamma is low → 1-2 active paths (directed beam).

#### Option B: Weighted Flow by Gradient

Simpler: keep flowing to all neighbors, but weight by gradient direction.
Gamma preferentially flows toward lower-gamma regions (downhill).

```python
def spread_weighted(self):
    """Weight spread by gradient direction — more flow downhill."""
    for each node:
        for each neighbor:
            gradient_toward_neighbor = gamma[neighbor] - gamma[node]
            if gradient_toward_neighbor < 0:  # downhill
                weight = abs(gradient_toward_neighbor)
            else:
                weight = small_baseline  # trickle uphill
            flow to neighbor proportional to weight
```

This concentrates flow into the strongest gradient direction (toward far
vacuum) while reducing flow toward already-gamma-rich regions (back to star).
The result: fewer effective paths at distance, hourglass shape.

#### Option C: Path Count from Solid Angle (Simplest)

Don't change the spread at all. Instead, when computing the EDGE GROWTH
rule, account for how many parallel paths exist at this distance from mass.

The number of graph nodes at hop distance r from a source on k=6 lattice is
approximately the surface of a cube: ~6r² for small r, approaching 4πr² for
large r on a smooth graph.

The gamma at distance r from steady-state diffusion is already ∝ 1/r.
The EDGE GROWTH sees γ_A + γ_B at its endpoints. For an edge at distance r:

```
γ(r) ∝ deposit_strength / r
```

So the edge equation becomes:

```
de/dt = H / (1 + α × deposit_strength / r)
```

Which IS Result 6: de/dt = H / (1 + α × M/r).

The problem isn't the math — it's that self-gravitation (G > 0) prevents
gamma from actually following 1/r. So:

**Try G=0 (no self-gravitation on gamma spread).** Let gamma diffuse freely
to 1/r steady state. Use tagged fields so bodies read external gamma only.
The edge growth reads total gamma at endpoints — which at distance r from
the star will be ∝ M/r. Exactly Result 6 without imposing it.

### Recommended Approach: Try G=0 First

Before building active edges or weighted flow:

1. Set G=0 (gamma diffuses freely, no self-gravitation)
2. Star deposits strongly every tick
3. Let gamma reach 1/r steady state (may need many formation ticks)
4. Edges grow by two-endpoint rule: de/dt = H / (1 + α(γ_A + γ_B))
5. Check: does the edge profile at r=1-20 now show smooth variation?
6. Run planet on this profile with geodesic frame rotation

If G=0 produces an hourglass gamma profile and bound orbits, then the
self-gravitation (G>0) was the problem all along — it was fighting the
very diffusion that creates the metric.

If G=0 gamma spreads too thin (uniform everywhere, no gradient), then
we need Option A or B to maintain directed flow.

### Connection to Phase 0 Results

Phase 0 with current settings:
- G causes gamma to pile up at r=0-3
- Edge ratio 50:1 but all within r=3
- Planet at r=10 sees flat edges

Phase 0 with G=0 (prediction):
- Gamma spreads to 1/r steady state
- Edge variation extends to r=20+
- Smooth hourglass profile
- Planet at r=10 sees meaningful tilt

### Updated Phase Sequence

1. **Phase 0a**: G=0, long formation (50000 ticks). Measure gamma profile.
   Verify 1/r. Measure edge profile. Does it extend to r=20?

2. **Phase 0b**: If 0a works, compare edge profiles:
   - G=0 (free diffusion)
   - G=0.01 (mild self-gravitation)
   - G=0.1 (moderate)
   Plot all three. Find the crossover.

3. **Phase 1**: Best profile from Phase 0 + geodesic frame rotation.
   Does it bind? Does it orbit?

4. **Phases 2-3**: Equal masses, three-body (same as before).

## The Key Physics

The connector between two bodies:
- Is MAINTAINED by continuous gamma deposit + spread
- NARROWS with distance (fewer paths survive maintenance cost)
- Carries FULL strength gamma per path
- Produces 1/r² force from TOPOLOGY, not signal decay
- Costs energy proportional to path length × path count

This is why gravity is weak: maintaining long-range connectors across the
entire graph is expensive. Only the 1/r survivors remain. EM is strong:
direct photon exchange, no maintenance cost, but must be emitted/absorbed.

Gravity is infrastructure. EM is mail. Infrastructure is always there but
expensive to maintain at distance. Mail is point-to-point but free to send.
