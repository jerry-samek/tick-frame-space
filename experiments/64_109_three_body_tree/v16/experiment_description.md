# v16: Drop the Lattice — Real Graph, One Stupid Rule

## Date: February 22-23, 2026
## Status: Completed — bound oscillation confirmed, Hubble drag limits orbit lifetime

## What v13-v15 Taught Us

| Version | What worked | What didn't | Why it didn't |
|---------|------------|-------------|---------------|
| v13 | Frame rotation binds orbits | Chaotic, pi not 2pi | Lattice quantizes direction to 6 axes |
| v14 | Two-endpoint edge rule, G=0 diffusion, 1/r profile | Edge profile flattens over time | Accumulated edges lose contrast |
| v14 | Cascade drift binds even when edges flatten | Chaotic bound, not elliptical | Still on lattice, angular momentum flips |
| v15 | Momentum conservation perfect, radial oscillation | Tangential dies, radial collapse | Lattice kills off-axis signal |

Every problem traces back to one thing: **the cubic lattice.**

- 6 directions quantize all motion to axes
- Tangential components get killed by axis rounding
- Frame rotation needed as a patch to re-introduce what the lattice destroyed
- Pi vs 2pi gap is a direct consequence of axis-aligned fractional asymmetry
- Angular momentum flips sign because orbits hit lattice corners

The lattice was never the physics. It was the viewport. We've been debugging
the viewport instead of testing the physics.

## The Core Insight

On a real graph there are no axes. An entity at node 7 connects to nodes
12, 45, 89, 203, 41, 8. Those aren't +x, -x, +y, -y, +z, -z. They're just
neighbors. The "direction" to node 45 isn't an angle — it's just: a connector
that leads to 45.

When the entity follows the laziest connector (lowest growth), it arrives at a
new node where the connectors point in DIFFERENT directions. The nudge direction
rotates naturally hop by hop because the graph topology changes at every node.

No frame rotation formula needed. No Bresenham accumulator. No axis projection.
The geometry IS the direction. The entity follows connectors, not vectors.

## v16: The Architecture

### The Graph (RandomGeometricGraph)

Not a lattice. A 3D point cloud with local connectivity:

1. Scatter N points uniformly in a 3D sphere (rejection sampling)
2. Connect each point to its k nearest neighbors (symmetrized)
3. Each edge has a length (initialized to Euclidean distance between points)
4. Edges grow by the two-endpoint rule: `de/dt = H / (1 + alpha * (|gamma_A| + |gamma_B|))`
5. Sparse adjacency matrix (scipy CSR) for efficient gamma diffusion

The points provide 3D embedding for visualization and momentum transfer.
The physics runs on the graph — entities only know their connectors' growth rates.

### The Entity — Velocity/Displacement Split

Final architecture after multiple iterations:

```python
class Entity:
    velocity = np.zeros(3)     # persistent 3D vector, changed only by acceleration
    disp = {}                  # per-connector displacement accumulator

    def advance(self, graph, tick):
        # 1. Deposit gamma at current node
        # 2. Acceleration: growth asymmetry of EXTERNAL gamma -> 3D force -> velocity
        # 3. Project velocity onto best-aligned connector -> accumulate displacement
        # 4. Hop when any connector's displacement >= initial_mean_edge
        # 5. Transfer residual displacement to new node's best connector
```

Key design decisions (each learned the hard way):

- **External gamma only**: `growth_at_node_external(node, exclude_bid)` — a body's
  own gamma creates symmetric suppression that drowns the asymmetric signal from
  other bodies. Without this fix, binary orbits fail completely (0 reversals).

- **Per-connector displacement** (not 3D vector): progress toward each neighbor is
  independent. A 3D displacement vector captures trajectory curvature, making it
  too conservative for hopping (34x fewer hops in tests). Per-connector correctly
  tracks "how far have I drifted toward this specific neighbor?"

- **Hop threshold = initial mean edge length** (comoving frame): the entity lives
  in graph coordinates. It doesn't know about physical edge lengths. Displacement
  accumulates raw velocity, and when enough displacement toward a neighbor accumulates,
  the entity hops. The threshold is a constant set at graph construction — expansion-
  invariant.

- **Single-best displacement transfer**: after hopping, residual per-connector
  displacement is converted to a 3D vector, projected onto the BEST connector at
  the new node. lstsq-based distribution across all connectors caused displacement
  scatter (including negative values), preventing any single connector from reaching
  the hop threshold.

### Gamma Field

Same algorithm as v14, adapted to graph topology:
- G=0 (free diffusion): `alpha_eff = alpha / (1 + G * |gamma|)` with G=0 gives constant alpha
- Tagged per-body: `gamma = sum(tagged[bid] for bid in body_ids)`
- Sparse matrix multiply for efficient diffusion: `inflow = A @ per_edge`

### Edge Growth

Same two-endpoint rule as v14:
```python
growth = H / (1.0 + alpha_expand * (|gamma_A| + |gamma_B|))
edge_length += growth
last_growth = growth
```

## Results

### Phase 1: Single Body Orbit — 30 comoving reversals

Star (stationary, mass=5000) + planet (mass=1, v_tangential=0.34).
N=30000, k=12, H=0.1, G=0, deposit_strength=1.0, inertia=1.0.

**The planet orbits.** 30 comoving reversals. The prediction was correct:
growth asymmetry on a real graph naturally produces tangential force components
because connectors aren't axis-aligned. No frame rotation needed.

### Phase 2: Equal Mass Binary — iterative debugging

Two equal masses (1000 each) with opposing tangential velocity.

#### Attempt 1: Naive (both bodies feel total gamma)
- Result: 0 reversals, 18-20 hops. Complete failure.
- Diagnosis: each body's own gamma dominated the denominator in the growth formula,
  drowning out the asymmetric signal from the other body.
- Fix: `growth_at_node_external()` — compute growth using only OTHER bodies' gamma.

#### Attempt 2: External gamma fix
- N=30000, k=12, H=0.1, v=0.34, separation=10
- Result: **16 comoving reversals**, 109-111 hops. Bodies bound and oscillating!
- Problem: hops stalled after tick ~6000. Scale factor reached ~10, edges grew 10x,
  making them too long for the hop threshold.

#### Attempt 3: Comoving frame correction
- User insight: "The hop threshold should be constant in graph units, not physical units."
- Removed edge-length normalization from displacement accumulation.
- Set hop threshold to `initial_mean_edge` (constant, expansion-invariant).
- Result: 33 comoving reversals with H=0.1. But bodies collapsed to comoving distance
  less than one mean edge due to rapid expansion (scale factor ~10).

#### Attempt 4: 3D displacement vector (rejected)
- Replaced per-connector displacement with a single 3D vector.
- Result: 34x fewer hops (87 vs 2947 in test 7). The 3D vector captures trajectory
  curvature — when velocity curves in a circular orbit, displacement oscillates without
  crossing the hop threshold. Per-connector is correct for graph motion.

#### Attempt 5: Parameter tuning — best result
- N=30000, k=12, **r=30** (denser: mean_edge=1.79), **H=0.01** (slow expansion)
- v=0.1, separation=10, mass=1000, deposit_strength=1.0
- Result: **77 comoving reversals**, scale factor 2.5, comoving range [8.34, 23.38]
- Bodies remained several edges apart throughout — enough resolution for smooth dynamics.

#### Scaling to 100K nodes
- Naive: N=100K with same deposit collapsed immediately (gamma density 3.3x lower
  per node → edges grew 3.3x faster → scale factor 8.7 in 5K ticks).
- Scaled deposit (3.3x): 61 comoving reversals, scale factor 4.95.
- High deposit (10x): 35 comoving reversals, scale factor 3.03.
- Lesson: deposit_strength must scale with N to maintain gamma density per node.

### H=0 Static Graph Test — Isolating Damping Source

N=100K, r=30, H=0, v=0.1. **No expansion, no gravity.**

- Velocity perfectly preserved at 0.100 for all 20K ticks.
- **Zero damping from the projection mechanism.**
- Bodies flew to the graph boundary in ~30 hops, then stalled (all connectors
  point inward at the boundary — no outward hopping possible).

**Conclusion**: the velocity damping observed in H>0 runs is entirely from
expansion (Hubble drag: v ~ 1/a), not from the displacement projection.

### Summary Table

| Run | N | r | H | v | mean_edge | scale | hops | comoving_rev |
|-----|---|---|---|---|-----------|-------|------|-------------|
| Phase 1 orbit | 30K | 50 | 0.1 | 0.34 | 2.98 | ~10 | ~500 | 30 |
| Binary naive | 30K | 50 | 0.1 | 0.34 | 2.98 | — | 18 | 0 |
| Binary ext-gamma | 30K | 50 | 0.1 | 0.34 | 2.98 | ~10 | 220 | 16 |
| Binary comoving | 30K | 50 | 0.1 | 0.34 | 2.98 | 10.8 | 241 | 33 |
| Binary dense+slow | 30K | 30 | 0.01 | 0.1 | 1.79 | 2.5 | 249 | **77** |
| Binary 100K scaled | 100K | 30 | 0.01 | 0.1 | 1.19 | 4.95 | 425 | 61 |
| Static H=0 | 100K | 30 | 0 | 0.1 | 1.19 | 1.0 | 58 | 0 |

## What v16 Proved

### 1. The lattice was the problem

On a real graph, growth asymmetry naturally produces tangential force components.
The planet orbits the star with 30 comoving reversals. No frame rotation, no
direction vector, no axis projection. The graph's irregular connector geometry
rotates the force direction hop by hop. **v15's mechanism works when the lattice
isn't destroying the tangential signal.**

### 2. Self-gravity must be excluded

A body's own gamma field creates symmetric growth suppression at all its connectors.
This drowns the asymmetric signal from other bodies. Binary orbits require computing
growth asymmetry from external gamma only.

### 3. Per-connector displacement is correct for graph motion

Three displacement strategies were tested:
- **Per-connector with single-best transfer** (final): 2947 hops in test, 77 reversals
- **3D displacement vector**: 87 hops in test, 17 reversals — too conservative
- **Per-connector with lstsq transfer**: scatter to all connectors, prevented hopping

Per-connector correctly models independent progress toward each neighbor. A 3D vector
over-couples the directions through projection math and captures trajectory curvature
that prevents hopping in orbital motion.

### 4. Comoving frame is the right frame for entity dynamics

The entity lives on the graph. It doesn't know about physical edge lengths.
Displacement accumulates raw velocity. The hop threshold is a graph-construction
constant (initial mean edge length), not the current expanding edge length. This
makes hopping expansion-invariant.

### 5. Hubble drag decays comoving velocities

On a static graph (H=0), velocity is perfectly conserved — zero damping from the
projection mechanism. With expansion (H>0), comoving velocities decay as v ~ 1/a
(the cosmological Hubble drag). This is correct physics but limits orbit lifetime:
as velocity decays, the orbit shrinks and eventually stalls.

In the best run (77 reversals), velocity decayed from ~0.1 to ~0.025 as the scale
factor grew from 1.0 to 2.5.

### 6. Graph resolution sets the dynamics floor

Bodies must stay several mean edges apart for the force direction to be well-resolved.
When comoving distance drops below ~2 mean edges, the gravitational force direction
oscillates too fast for displacement to accumulate. Denser graphs (more nodes, smaller
radius) give better resolution but require scaling deposit_strength with N to maintain
gamma density.

## The Remaining Problem — Hubble Drag

The orbits work but they decay. The mechanism is sound: growth asymmetry produces
gravity, irregular graph geometry produces tangential deflection, per-connector
displacement produces hops, and velocity conservation is perfect on a static graph.

But edge expansion decays comoving velocities. The bodies slow down, the orbit
shrinks, and eventually the system stalls. This is analogous to the real cosmological
Hubble drag, where peculiar velocities of unbound objects decay as 1/a.

In real physics, bound systems overcome Hubble drag through gravitational binding
energy. In our simulation, the binding isn't sufficient to fully compensate — the
orbit decays rather than stabilizing.

**Theory for v17**: Mass loss might stabilize the orbit. A body deposits gamma
(creates gravity) but that deposit IS mass loss — the body radiates its mass into
the field. As mass decreases, the orbital radius increases (angular momentum
conservation). If the mass loss rate matches the expansion rate, the orbit stabilizes:
expansion shrinks comoving orbits while mass loss widens them. The same mechanism
that creates gravity also decays it at the right rate. This predicts M(t) ~ M₀/a(t).

## The Simplicity Chain

v13: 2 mechanisms + hand-set profile + gradient coupling + frame rotation
v14: 2 mechanisms + emergent profile + frame rotation
v15: 1 mechanism + lattice (radial only, no orbit)
v16: 1 mechanism + real graph (**bound oscillation from topology**)
v17: 1 mechanism + real graph + mass radiation (stable orbit?)

## File Structure

```
v16/
  experiment_description.md  (this file)
  macro_bodies.py            (RandomGeometricGraph + Entity + phases 0/1/2)
  results/                   (plots from all experiments)
```

## 9/9 Verification Tests

1. Gamma conservation (1000 ticks, drift < 1e-12)
2. Peak retention (G=10, peak/mean > 100)
3. External gamma = total - own
4. Full dispersal at G=0 (peak/mean < 2)
5. Edge expansion suppressed near mass (near/far ratio > 2)
6. last_growth populated by expand_edges
7. Nudge accumulation produces hops from growth asymmetry (2947 hops)
8. Velocity persists through hops (v preserved to 3 decimals)
9. move_gamma conserves gamma exactly
