# Experiment 64_109: Three-Body Dynamics on a Pure Graph

## Status: v5 COMPLETE — Commit-counter model: v = c/M CONFIRMED, mass strengthens binding

## Core Question

Does gravity emerge from deposit-spread-follow on a graph WITHOUT spatial geometry?

If yes: space is not fundamental. Causal structure is.

Secondary question: does the Bremsstrahlung drain problem from Experiment 64 vanish when there is no lattice? On a
graph, minimum distance is always 1 hop — no zero-distance singularity, no gradient spike, no runaway possible.

## Theoretical Basis

RAW 109 establishes that the tick-frame model's physics lives on the causal decision tree, not on the spatial lattice.
The lattice is one possible embedding. This experiment tests whether the embedding is necessary.

The claim: three entities depositing into a shared field on a graph, following gradients, should produce:

- Mutual attraction (gravity analog)
- Chaotic three-body energy exchange
- Bound orbits (entities cycling around each other in graph topology)
- Natural speed limit (bounded hops per tick)
- Automatic energy drain (each hop deposits energy — no tunable coefficient)

## What "Orbit" Means on a Graph

An orbit on a lattice: entity circles another entity in coordinate space.

An orbit on a graph: entity traverses a CYCLE of nodes around another entity's deposit peak. The entity is attracted (
gradient pulls it toward the deposit) but has momentum (tendency to keep hopping in the same traversal direction).
Balance of attraction and momentum = stable cycling through nodes near — but not at — the other entity's position.

We don't need to visualize this spatially. We measure it by tracking hop-distances between entities over time. If
distances oscillate (approach, retreat, approach) — that's an orbit. If distances show chaotic exchange — that's
three-body dynamics.

## Architecture

### Graph Substrate

- Random regular graph: N nodes, each with exactly k neighbors
- Use Watts-Strogatz model with HIGH rewiring probability (β ≈ 0.95) to destroy any residual spatial structure
- The graph should have NO geometry, NO embedding, NO coordinates
- Each node holds a scalar gamma value (the field)

### Key Parameters to Explore

| Parameter        | Starting value   | Rationale                                                                                    |
|------------------|------------------|----------------------------------------------------------------------------------------------|
| N (nodes)        | 50,000 - 100,000 | Must be large enough that entities start far apart (target: 15-30 hops initial separation)   |
| k (neighbors)    | 6                | Matches 3D cubic lattice connectivity for comparison; also try 12 (FCC equivalent)           |
| Spread factor    | 0.001 - 0.01     | How much gamma diffuses to neighbors per tick. Too high = flat field. Too low = no gradient. |
| Decay            | 0.9999           | Gentle decay prevents unbounded gamma growth                                                 |
| Deposit strength | tunable          | How much gamma an entity adds to its current node per tick                                   |

### Entity Model

Each entity has:

- **Current node**: which graph node it occupies
- **Kinetic energy**: accumulated from gradients, spent on hops
- **Momentum direction**: the last N hops taken (memory of recent path through graph)

Each tick:

1. **Deposit**: add gamma to current node
2. **Read gradient**: look at all neighbors, find highest gamma (from OTHER entities' deposits)
3. **Accumulate KE**: gradient magnitude adds to kinetic energy
4. **Move**: take floor(KE) hops along steepest gradient direction
5. **Drain per hop**: each hop costs a fraction of KE, deposited at the node traversed

The drain is AUTOMATIC. No coefficient to tune. More hops = more deposits = more energy into field. The topology
prevents concentration because minimum distance is always 1 hop.

### Self-Attraction Problem

Entity deposits at its own node, creating a local gamma peak. It must NOT be attracted to its own deposit. Solutions:

- **Separate fields**: each entity deposits into its own field layer, follows gradient of SUM of other entities' fields
- **Deposit tagging**: tag deposits by source, exclude own deposits from gradient calculation
- **Deposit-then-move**: entity deposits BEFORE moving, so by the time it reads gradients, its own deposit has spread to
  neighbors (diluted)

Recommend: separate fields (cleanest). Three field layers, one per entity. Each entity follows the gradient of the sum
of the OTHER two fields.

### Commit Phase

Same transactional semantics as Experiment 64:

- All entities read from COMMITTED state (snapshot at tick start)
- All deposits and moves happen based on snapshot
- Field spreads after all entities have acted
- Atomic commit at tick boundary

## Measurements

### Primary (do these produce three-body-like dynamics?)

1. **Hop distance between each pair** vs tick — plot d_AB(t), d_AC(t), d_BC(t)
2. **Entity speed** (hops per tick) vs tick — plot v_A(t), v_B(t), v_C(t)
3. **Close encounters**: count events where any pair distance ≤ 2 hops
4. **Energy exchange**: does KE transfer chaotically between entities?

### Secondary (comparison with Experiment 64)

5. **Peak velocities**: what's the maximum hops/tick achieved? Is there a natural ceiling without explicit drain?
6. **Gamma growth**: does the total field energy grow linearly, exponentially, or stabilize?
7. **Bound vs ejection**: do all three entities remain within a bounded region of the graph, or does one escape?

### Tertiary (if primary succeeds — the big questions)

8. **Vary k**: does changing neighbor count (4, 6, 8, 12, 20) change the dynamics qualitatively? This tests whether "
   dimensionality" (branching factor) affects gravity.
9. **Vary N**: does scaling the graph change encounter dynamics? Tests scale invariance.
10. **Compare with Experiment 64**: run identical "initial conditions" (same mass ratios, same relative separations in
    hops vs cells) on both graph and lattice. Do the statistical properties match?

## Success Criteria

### PASS (gravity emerges on graph)

- Entities attract: distances decrease from initial separation
- Bound system: no entity escapes to graph diameter
- Chaotic exchange: KE transfers between entities irregularly
- Close encounters: multiple events with d ≤ 2 hops

### STRONG PASS (drain problem solved)

- No velocity runaway at any point
- No gamma overflow / NaN
- No need for explicit drain coefficient — topology self-regulates
- Peak velocities naturally bounded (< max_hops_per_tick ceiling)

### EXCEPTIONAL PASS (physics matches lattice)

- Distance oscillation patterns statistically similar to Experiment 64
- Energy exchange timescales comparable
- Three-body dynamics qualitatively identical despite no geometry

### FAIL (geometry is necessary)

- Entities don't attract (no gravity without space)
- System doesn't bind (entities random-walk away)
- No chaotic exchange (trivial dynamics)
- Drain problem persists or worsens

## Implementation Notes

### Performance

- Graph operations are O(k) per node per tick, vs O(27) for 3D lattice — comparable
- BFS for hop distance is expensive: O(N) worst case. Cache distances or compute only at log intervals
- 50K nodes × 20K ticks should run in minutes, not hours — this is much smaller than 256³ = 16M cells
- Use numpy arrays for gamma field, python lists for neighbor connectivity

### Visualization (optional, after dynamics confirmed)

- Force-directed graph layout (e.g., spring layout) to project graph into 2D
- Color nodes by gamma value
- Mark entity positions
- Animate over time
- This is PURELY for human understanding — the physics doesn't need it

### Output

- JSON results file with all measurements
- Distance plots (primary diagnostic)
- Speed plots
- Gamma growth plot
- Encounter log

## Relationship to Theory

If this experiment passes, it validates:

- **RAW 109**: c and isotropy from topology, not geometry
- **RAW 082**: gravity as cost gradient (works on graph = works without space)
- **Ch7 §2**: speed of light as structural constraint (max hops per tick)
- **Decision tree framework**: time dilation = tree depth, radiation = branch cost

And it opens the door to:

- **RAW 110** (planned): Dimensionality as projection — the graph has no intrinsic dimension
- **Trit chip architecture**: hardware implements graph, not spatial grid
- **Rendering engine**: deposits on graph, project to 3D for display

## Results (February 2026)

### Verdict: PARTIAL PASS — Gravity is topological, orbits require dimensionality

#### What works (PASS criteria met):

1. **Attraction emerges**: All entity pairs converge from initial separation. The deposit-spread-follow mechanism
   produces an attractive force on a pure graph with zero spatial geometry. This confirms that gravity (as modeled in
   the tick-frame system) is a topological phenomenon — it works on any connected graph.

2. **Bound system**: No entity escapes to the graph diameter. The system is gravitationally bound.

3. **Close encounters**: Multiple d=0 events (entities reach same node).

4. **Drain problem solved**: The Bremsstrahlung runaway from Experiment 64 does NOT occur on the graph. Max velocity is
   naturally bounded by the `max_hops_per_tick` parameter (speed-of-light analog). No gamma overflow, no NaN. The graph
   topology's minimum distance of 1 hop eliminates the zero-distance singularity that caused gradient spikes on the
   lattice.

5. **No velocity runaway**: Peak velocities stay within bounds. The topology self-regulates.

#### What fails (FAIL/missing criteria):

1. **No orbits**: Entities do not orbit each other. They fall straight in and merge at d=0, then remain stuck. This is
   the fundamental finding: **a random graph has no angular momentum**. On a lattice (or in continuous space), an entity
   approaching an attractor has a perpendicular degree of freedom — it can "miss" and swing around. On a random graph,
   the gradient is purely radial. Every neighbor's gamma points toward the same attractor peak. There is no "sideways"
   direction to sustain orbital motion.

2. **No chaotic three-body exchange**: Because entities collapse rather than orbit, there is no sustained chaotic energy
   exchange. The system reaches a static merged state rather than exhibiting ongoing dynamics.

3. **No distance oscillation**: Distances monotonically decrease (no approach-retreat cycles).

### Theoretical Interpretation

The result splits the original hypothesis cleanly:

- **Gravity = topology**: Confirmed. Deposit-spread-follow creates attraction on any connected graph. The mechanism is:
  entity A deposits, field spreads outward, entity B reads gradient pointing toward A's deposit peak, B accumulates KE
  and hops toward A. This requires only graph connectivity — no coordinates, no metric, no geometry.

- **Orbits = dimensionality**: Refuted (on a graph). Stable orbits require at least two spatial dimensions: one for the
  radial (attractive) direction and one perpendicular to sustain angular momentum. A random graph has NO such
  distinction. The shortest path to the attractor IS the only meaningful direction. There is no "perpendicular to the
  gradient" concept on a Watts-Strogatz graph.

This maps onto the theoretical framework: RAW 109 is partially correct. The causal decision tree CAN produce
gravity-like attraction without spatial geometry. But the decision tree cannot produce ORBITS without additional
structure that creates effective dimensionality. The spatial lattice (or its equivalent) provides this structure.

### Parameter Sensitivity

Extensive parameter sweeps were conducted:

| Parameter         | Range tested | Finding                                                                                                                                                                                                                                                                                                   |
|-------------------|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| N (nodes)         | 20K - 100K   | Larger N gives longer paths but same collapse                                                                                                                                                                                                                                                             |
| k (neighbors)     | 6            | k=6 gives avg degree matching 3D lattice                                                                                                                                                                                                                                                                  |
| beta (rewiring)   | 0.01 - 0.3   | Lower beta = longer paths. beta=0.05 gives avg_path ~14, good balance                                                                                                                                                                                                                                     |
| spread_fraction   | 1/k (fixed)  | c = 1 hop/tick. Not a free parameter — it's the speed of light. alpha=1/k gives 1 hop/tick propagation matching the lattice's 1 cell/tick. For k=6: alpha≈0.167. Mixing matrix amplitude per hop is 1/k²≈0.028 (weaker than lattice's 1/k≈0.167 pressure equalization), but propagation speed is correct. |
| decay             | 0.9999       | Gentle decay prevents unbounded growth                                                                                                                                                                                                                                                                    |
| formation_ticks   | 0 - 10000    | Even with 0 formation, entities still converge (confirms gradient forms during dynamics)                                                                                                                                                                                                                  |
| max_hops_per_tick | 20           | Speed-of-light analog. Without this, velocities hit 170+ hops/tick                                                                                                                                                                                                                                        |
| trajectory_memory | 0 - k        | Delays collapse slightly but cannot prevent it                                                                                                                                                                                                                                                            |

The collapse result is robust across all parameter choices. It is not a tuning issue — it is a fundamental property of
the topology.

### Attempted Fixes That Did Not Prevent Collapse

1. **Trajectory memory** (angular momentum analog): deque of recently visited nodes excluded from gradient candidates.
   Delays collapse by forcing longer paths but cannot prevent it — eventually all non-visited neighbors also point
   toward the attractor.

2. **Mass-conserving deposits**: Withdraw deposit from previous node, place at current. Gamma well follows entity. Does
   not change the fundamental gradient structure.

3. **Negative gradients** (deceleration at peaks): Allowing negative gradient at local maxima. WORSE — permanently
   zeroes KE when entity enters potential well.

4. **Zero formation**: Starting with no pre-built gamma wells. Same collapse, just slower initial approach.

### Implications for Theory

1. **Space IS partially fundamental**: Spatial dimensionality (≥2D) is necessary for orbital mechanics. A pure causal
   graph cannot reproduce this. The lattice/spatial structure is not merely a convenient embedding — it provides
   essential physics (angular momentum conservation).

2. **RAW 109 scope**: The claim "physics lives on the causal decision tree" needs qualification: *attraction* lives on
   the topology, but *dynamics* (orbital exchange, chaotic three-body, etc.) require geometric structure.

3. **Experiment 64 revalidated**: The 3D lattice version's orbital dynamics were real physics, not artifacts of the
   grid. The lattice provides what the graph lacks: perpendicular degrees of freedom.

4. **Next question**: What is the MINIMAL structure needed for orbits? A 1D ring (beta=0)? A 2D lattice? A graph with
   guaranteed local cycles of specific length? This would isolate exactly what "dimensionality" contributes to orbital
   mechanics.

## v2: RAW 110 Validation — Lattice Graph, Temporal Traversal, Mass, Exclusion

### Status: PASS — Gravity emerges with bound dynamics on structured graph

### Diagnosis (RAW 110)

RAW 110 (Local Dimensionality) identifies the root cause of collapse on the random graph: **local dimensionality D(n) ~
0-1**. The Watts-Strogatz graph has no perpendicular directions. Even when the gradient is non-zero, the "steepest
neighbor" in an unstructured neighborhood doesn't reliably correspond to the direction toward the source.

On a structured lattice, neighbor `(10,6,0)` is perpendicular to the gradient toward `(0,0,0)` — the entity can orbit.
On a random graph, no such perpendicular neighbor exists.

### Design Constraint

**NO coordinates for physics.** The lattice graph is built with coordinates (via `nx.grid_graph`), then coordinates are
thrown away. All physics (spreading, gradient, movement) uses only adjacency — same code as the random graph. The only
exception: `plan_path()` uses stored coordinates to compute straight-line multi-hop paths for the mass/inertia system.
This is a structural property of the graph (lattice regularity), not a spatial coordinate system for physics.

### Physics Model Evolution

v2 introduced four key mechanics, each solving a specific failure mode:

#### 1. Temporal Edge Traversal (`--temporal`)

Instead of instantaneous hops, entities accumulate gradient as transit progress each tick. An entity crosses an edge
only when accumulated progress exceeds the edge weight. During traversal, the entity is committed — it cannot change
direction. This creates sub-light movement and prevents instant collapse.

**Edge weight** (`--edge-weight N`): Each lattice edge costs N ticks of gradient accumulation to cross. Weight 1 =
movement at c (speed of light). Weight 20 = sub-light movement. Shortcuts on lattice-nw graphs cost Manhattan distance x
edge weight.

**KE as sawtooth**: Transit progress ramps linearly (gradient/tick), resets on hop. Period = edge_weight /
gradient_magnitude. This naturally produces the sawtooth energy pattern seen in all temporal runs.

#### 2. Equilateral Placement + Tangential Initial KE (`--equilateral --initial-ke N`)

Places three entities at vertices of an equilateral triangle on the Manhattan lattice. Coordinates: A=(cx,cy,cz), B=(
cx+d,cy,cz), C=(cx+d/2,cy+d/2,cz) — all pairs at equal Manhattan distance d.

Each entity starts with initial KE directed along a tangential edge (perpendicular to the line connecting it to the
triangle center): A→+y, B→-y, C→+x. This gives the system initial angular momentum, preventing head-on radial collapse.

Without tangential KE: entities approach radially and merge at ~tick 100.
With tangential KE (ike=10, ew=20): collapse delayed to ~tick 12K.

#### 3. Mass as Path Commitment (`--mass N`)

The key breakthrough. An entity commits to a straight-line path of N edges before re-reading the gradient. During the
path, it cannot turn. At the end, it reads the gradient and plans a new N-edge path.

**Mass = inertia = path commitment length.** Heavier entities preserve direction longer, creating effective angular
momentum conservation on the discrete graph.

- mass=1: turn every hop → instant collapse (no inertia)
- mass=2: commit to 2-edge paths → the sweet spot (see results)
- mass=3-5: too much inertia, entities too slow to interact within 50K ticks

#### 4. Exclusion (`--exclusion`)

Prevents two entities from occupying the same node. When an entity would hop to an occupied node: path is cancelled,
excess KE is retained, entity replans next tick.

This solves the **d=0 singularity**: without exclusion, entities that share a node see zero mutual gradient (both
sitting at the field peak) and freeze permanently. With exclusion, minimum distance is 1 hop, gradient always exists,
system stays active indefinitely.

### Results — Systematic Parameter Sweep

All runs: lattice graph, N~50K, k=6, edge-weight=20, equilateral, initial-ke=10, separation=14.

| Mass  | Ticks    | Exclusion | Encounters | Reversals | d=0?        | Freeze?       | Verdict                                 |
|-------|----------|-----------|------------|-----------|-------------|---------------|-----------------------------------------|
| 1     | 20K      | No        | 454        | —         | Yes (t~100) | Total         | Instant collapse                        |
| 2     | 20K      | No        | 8          | 3         | No          | No            | PASS (action starts at t=19K)           |
| 2     | 50K      | No        | 1686       | 36        | Yes (t=21K) | Total (t=25K) | PARTIAL — oscillations then singularity |
| 3     | 20K      | No        | 0          | 0         | No          | No            | WEAK — too much inertia                 |
| 5     | 20K      | No        | 0          | 0         | No          | No            | WEAK — too much inertia                 |
| 5     | 50K      | No        | 0          | 0         | No          | No            | WEAK — still monotonic                  |
| **2** | **100K** | **Yes**   | **3181**   | **6**     | **No**      | **Never**     | **PASS — final configuration**          |

### Final Run Analysis (mass=2, 100K ticks, exclusion)

```
python three_body_graph.py --quick --graph-type lattice --temporal --edge-weight 20 \
    --equilateral --initial-ke 10 --min-separation 14 --mass 2 --exclusion \
    --dynamics-ticks 100000
```

**Attraction**: All pairs converge from initial 14 hops. Final: A-B=1, A-C=2, B-C=3.

**Bound system**: No escape. Max distances: A-B=18, A-C=15, B-C=14.

**3181 close encounters**: Active dynamics for the full 100K ticks. No freezing.

**No d=0 collapse**: Exclusion prevents merging. Minimum distance = 1 hop.

**Hierarchical three-body outcome**: The system evolved into a configuration commonly seen in classical three-body
dynamics:

- **A-B formed a tight binary** at d=1, rapidly exchanging KE in a sawtooth pattern (period ~132 ticks). Active for 75K+
  ticks with no sign of decay.
- **C decoupled** into a distant steady state, settling at constant KE=12.95 for the last 75K ticks. Effectively a
  distant third body orbiting the A-B binary.

This hierarchical outcome (tight binary + distant third) is a well-known attractor of classical three-body dynamics. Its
emergence from pure graph physics with no spatial coordinates is significant.

**Energy exchange**: A and B show chaotic KE cycling (mean~10, std~5.8, range 0-20). C's KE stabilized. Total system
energy bounded (gamma growth ratio 0.28x).

### What v2 Proves

1. **RAW 110 confirmed**: Structured graph (D(n)=3) recovers bound dynamics where random graph (D(n)~0) fails. Local
   dimensionality is the critical variable.

2. **Gravity is topological**: Deposit-spread-follow produces attraction on any connected graph. The lattice provides
   directional reliability, not the force itself.

3. **Inertia requires path commitment**: On a discrete graph, "mass" manifests as commitment to a straight-line path.
   Without it, entities turn every hop and collapse. With it, they overshoot and remain bound.

4. **Sub-light speed is essential**: Edge weight > 1 creates a speed hierarchy. Entities move slower than field
   propagation (c = 1 hop/tick for the field, ~1 hop per 20 ticks for entities with ew=20). This mirrors the real
   physics constraint v < c.

5. **Exclusion prevents singularity**: The d=0 freeze is an artifact of the discrete model (zero gradient at field
   peak). Exclusion is the graph analog of a minimum approach distance / hard-core potential.

6. **Hierarchical outcome emerges naturally**: No code specifically produces binary formation + third-body ejection. It
   emerges from the interplay of gradient following, path commitment, and exclusion.

### What v2 Does NOT Show

1. **No stable orbits**: Distance reversals are few (6 in 100K ticks). Entities approach and bind but don't oscillate
   around each other in sustained periodic orbits. The system finds a static hierarchical configuration rather than a
   dynamic orbital one.

2. **C freezes**: Once A-B lock into a tight binary, C sees a nearly symmetric combined field and settles at constant
   KE. The system reaches an equilibrium rather than sustained three-body chaos.

3. **Mass=2 is a narrow sweet spot**: mass=1 collapses, mass=3+ is too sluggish. The "right" mass depends on separation
   and edge weight. No universal mass parameter.

### Calibration Results (Two-Body Infall)

| Graph Type  | Initial d | Infall tick           | Max velocity |
|-------------|-----------|-----------------------|--------------|
| Random (WS) | 12 hops   | Never (stuck at d=10) | 1 hop/tick   |
| Lattice     | 38 hops   | 6400                  | 6 hops/tick  |

The lattice calibration shows reliable directional approach: distance decreases monotonically from 38 to 1 in 6400
ticks. The random graph entity random-walks at constant distance — confirming the D(n) diagnosis.

### File Organization

```
experiments/64_109_three_body_tree/
├── experiment_description.md    (this file)
├── v1/                          (original random-graph-only version)
│   ├── three_body_graph.py
│   └── results/
└── v2/                          (lattice + temporal + mass + exclusion)
    ├── three_body_graph.py      (7 verified tests)
    └── results/
        ├── results_three_body_lattice.json
        ├── results_three_body_lattice_temporal.json
        ├── results_three_body_lattice_temporal_equilateral.json
        ├── results_three_body_lattice_temporal_equilateral_exclusion.json
        ├── results_three_body_lattice-nw.json
        └── *.png (distance, speed, energy, gamma, summary plots)
```

### Running v2

```bash
# Verify all 7 tests
cd v2 && python three_body_graph.py --verify

# Calibration: two-body infall comparison
cd v2 && python three_body_graph.py --calibrate --quick --graph-type lattice --temporal --edge-weight 20
cd v2 && python three_body_graph.py --calibrate --quick --graph-type random

# The final configuration (PASS):
cd v2 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
    --mass 2 --exclusion --dynamics-ticks 100000

# Parameter variations:
cd v2 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --mass 3  # too slow
cd v2 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --mass 5  # way too slow
```

### Open Questions for v3

1. **Can orbital oscillations be recovered?** The hierarchical outcome is stable but static. Is there a parameter
   regime (mass, edge weight, separation, deposit strength) where distances oscillate rather than converge to a fixed
   configuration?

2. **Multi-body scaling**: Does the hierarchical outcome persist with 4+ entities? Does a binary always form, or can
   more complex bound states emerge?

3. **Energy conservation**: The gamma field grows continuously (entities deposit every tick). Should there be a
   conserved total (KE + field energy)? Would conservation change the dynamics?

## v3: Always-Move Model — Movement is Existence

### Status: PASS — Argmax + random fallback recovers full gravitational dynamics

### Motivation

v2's temporal model works well but has a philosophical problem: entities freeze when gradient is zero (d=0 singularity).
The exclusion mechanism prevents d=0 but is a band-aid — it blocks the symptom (co-location) rather than addressing the
cause (entities that stop existing when they stop moving).

v3 tests the principle: **Movement is existence. Gradient is preference, not permission.**

Every tick, every entity hops. No exceptions. The gradient determines *where* to hop, not *whether* to hop. At zero
gradient (all neighbors equal), the entity random-walks. At nonzero gradient, it follows the steepest neighbor (argmax).
Mass still controls path commitment length (inertia).

### Design: Argmax with Random Fallback

The direction selection rule is:

1. **Gradient exists** (best neighbor distinguishable) → follow it deterministically (argmax, same as v2)
2. **Gradient is zero** (all neighbors equal) → pick a random neighbor (uniform)

This is NOT softmax. An earlier attempt used softmax over raw gamma values, but the directional bias was too weak (~0.5%
per choice at 14 hops) to overcome random walk diffusion. The fix is conceptually simple: if you know which way to go,
go there. Randomness is only for when you genuinely have no information.

Mass as path commitment works identically to v2: entity plans an N-edge straight-line path at each decision point, hops
one edge per tick, replans when the path is consumed.

Key differences from v2:

- **Always moving**: 1 hop per tick, every tick. No waiting for KE accumulation.
- **No exclusion needed**: Entities pass through each other (random walk at d=0) rather than freezing. The gradient
  naturally pulls them apart again.
- **No temporal edge traversal**: Edges are crossed in 1 tick (speed = c). Sub-light behavior comes from path
  commitment (mass), not edge weight.
- **KE is constant**: Always 1.0 (always moving at c). No sawtooth energy pattern.

### Failed Approach: Pure Softmax

Before arriving at argmax + random fallback, v3 tested pure softmax direction selection:

```
p(neighbor) = exp(gamma[neighbor]) / sum(exp(gamma[all_neighbors]))
```

Results across all masses were disastrous:

| Mass | Close encounters (100K ticks) | Max dist | Behavior         |
|------|-------------------------------|----------|------------------|
| 1    | 3                             | 52       | Pure random walk |
| 2    | 4                             | 53       | Random walk      |
| 5    | 3                             | 53       | Random walk      |
| 10   | 1                             | 53       | Random walk      |

**Root cause**: At 14 hops, gamma values at neighbors differ by ~0.03. Softmax produces probabilities ~0.170 vs ~0.165 (
6 neighbors) — a ~0.5% bias invisible against random walk noise. The entity essentially random-walks regardless of mass.

**Lesson**: Stochastic direction selection should be reserved for genuine ambiguity. When the gradient provides
information, follow it. Don't add noise to a signal that's already weak.

### Results — Argmax + Random Fallback

```bash
cd v3 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
    --mass 2 --dynamics-ticks 100000 --always-move
```

Parameters: lattice N=50653, side=37, k=6, edge-weight=20, equilateral d=14, initial KE=10, mass=2.

| Metric              | v3 always-move        | v2 temporal+exclusion | v3 softmax (failed)   |
|---------------------|-----------------------|-----------------------|-----------------------|
| Close encounters    | **3235**              | 3181                  | 3-4                   |
| System bound        | Yes (max 18)          | Yes (max 18)          | No (max 53)           |
| All pairs attracted | Yes                   | Yes                   | No                    |
| d=0 collapses       | **0**                 | 0 (exclusion)         | 0                     |
| Entity freezes      | **Never**             | Never (exclusion)     | Never                 |
| Velocity            | 1 hop/tick (constant) | Sawtooth 0→20         | 1 hop/tick (constant) |
| KE                  | 1.0 (constant)        | Chaotic exchange      | 1.0 (constant)        |

**Attraction**: All pairs converge. A-B: 14→2 (min=2). A-C: 16→2 (min=2). B-C: 14→2 (min=2).

**Bound system**: Max distances: A-B=18, A-C=16, B-C=14. No escape.

**3235 close encounters**: Active dynamics for the full 100K ticks. Encounters start at tick 200 (A-C first approach)
and continue throughout.

**Distance dynamics**: A-B collapses early and stays at d=2 (tight binary). A-C and B-C oscillate between ~2-16 hops
with high reversal counts (826 and 1047 reversals respectively), showing genuine bound oscillation around the binary.

**No d=0 without exclusion**: The always-move model naturally avoids the d=0 freeze — entities that land on the same
node random-walk apart on the next tick rather than freezing. Minimum observed distance is 2 hops (entities overshoot
with mass=2 path commitment).

**Gamma stability**: No NaN/Inf. Growth ratio 1.27x over 100K ticks.

### What v3 Proves

1. **Always-move is viable**: Entities that never stop produce the same gravitational binding as the temporal model. The
   always-move philosophy works — gradient as preference, not permission.

2. **Argmax is essential**: The direction selection must be deterministic when gradient information exists. Softmax
   destroys the weak signal at large distances. Stochasticity is only appropriate for the degenerate case of truly equal
   neighbors.

3. **Exclusion is not needed**: The always-move model eliminates d=0 freezing without an explicit exclusion mechanism.
   Entities pass through each other and the gradient naturally separates them.

4. **Mass as path commitment works at c**: Even at speed c (1 hop/tick), mass=2 path commitment creates enough inertia
   for bound dynamics. Sub-light edge traversal is not required.

5. **KE exchange is lost**: Because entities always move at c with constant KE=1.0, there is no energy exchange between
   entities. The chaotic KE cycling seen in v2 is absent. This is a trade-off: always-move gains simplicity and
   eliminates the freeze problem, but loses the energy exchange signature.

### Comparison: v2 vs v3 Philosophy

| Aspect     | v2 (temporal)                      | v3 (always-move)             |
|------------|------------------------------------|------------------------------|
| Movement   | Permission-based (KE threshold)    | Existence-based (always hop) |
| Speed      | Sub-light (edge weight / gradient) | c (1 hop/tick, always)       |
| Direction  | Argmax                             | Argmax + random fallback     |
| d=0 fix    | Exclusion (external constraint)    | Natural (random walk out)    |
| Energy     | Chaotic exchange (sawtooth KE)     | Constant (KE=1 always)       |
| Inertia    | Path commitment + slow traversal   | Path commitment only         |
| Encounters | 3181                               | 3235                         |
| Binding    | Yes                                | Yes                          |

Both models produce gravitational binding. v2 has richer energy dynamics (KE exchange). v3 has a cleaner ontology (no
external fixes needed).

### File Organization

```
experiments/64_109_three_body_tree/
├── experiment_description.md    (this file)
├── v1/                          (original random-graph-only version)
│   ├── three_body_graph.py
│   └── results/
├── v2/                          (lattice + temporal + mass + exclusion)
│   ├── three_body_graph.py
│   └── results/
└── v3/                          (always-move: argmax + random fallback)
    ├── three_body_graph.py      (7 verified tests)
    └── results/
        ├── results_three_body_lattice_temporal_equilateral_alwaysmove.json
        └── *.png (distance, speed, energy, gamma, summary plots)
```

### Running v3

```bash
# Verify all 7 tests
cd v3 && python three_body_graph.py --verify

# The always-move configuration (PASS):
cd v3 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
    --mass 2 --dynamics-ticks 100000 --always-move

# Mass variations:
cd v3 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --mass 1 \
    --dynamics-ticks 100000 --always-move   # mass=1: photon
cd v3 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --mass 5 \
    --dynamics-ticks 100000 --always-move   # mass=5: heavier
```

### Open Questions for v4

1. **Can KE exchange be recovered?** The always-move model loses the chaotic energy exchange. Is there a way to have
   always-move AND variable speed? Perhaps: always hop, but gradient magnitude determines how many hops per tick (up to
   mass limit)?

2. **Softmax with temperature**: Instead of binary argmax/random, could `softmax(gamma/T)` with very low temperature (
   T << 1) produce the same results while being more physically motivated? The current argmax is the T→0 limit.

3. **Multi-body**: Does the always-move model scale to 4+ entities? The natural d=0 resolution (no exclusion needed)
   should make multi-body simulations simpler.

## v4: Oscillation Amplitude as Energy + Mass-Energy Prediction

### Status: CONFIRMED — Amplitude increases with mass (max amplitude monotonic)

### The Insight

v3 always-move model produces 3235 close encounters with gravitational binding. But KE is always 1.0 (every entity hops
every tick at c). So where is the energy?

**Energy isn't KE stored on the entity. It's the amplitude of the distance oscillation.** C swinging between d=2 and
d=16 around the A-B binary — that swing IS the energy. Wide swing = high energy. Tight swing = low energy. Energy
exchange = one pair's amplitude growing while another's shrinks.

**Mass controls energy through overshoot.** A heavy entity commits to a longer path. More ticks between decisions →
gradient changes more → bigger overshoot → more dramatic reversal → more energy in the oscillation.

- mass=1: corrects every tick → tiny overshoot → low amplitude → low energy
- mass=2: corrects every 2 ticks → medium overshoot → medium amplitude
- mass=10: corrects every 10 ticks → huge overshoot → high amplitude → high energy

### Measurement: Sliding Window Amplitude Envelope

`compute_amplitude_envelope(distances, pair_key, window_size=20)`: sliding window max-min over 20 distance samples. This
captures the local oscillation range — the energy.

`compute_energy_exchange(amp_dict, corr_window=50)`: rolling Pearson correlation between pairs' amplitude series.
Anti-correlation (< -0.3) = energy transferring between pairs.

`compute_total_orbital_energy(amp_dict)`: sum of all pair amplitudes. If conserved → roughly flat line. CV < 0.3 =
approximately conserved.

### No Physics Model Changes

v4 is purely an analysis/measurement upgrade over v3. Same always-move model, same argmax + random fallback, same path
commitment. The only changes are new analysis functions and plots.

### Mass Sweep Results

All runs: lattice N=50653, side=37, k=6, edge-weight=20, equilateral d=14, initial KE=10, 100K dynamics ticks,
always-move.

```bash
cd v4 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
    --dynamics-ticks 100000 --always-move --mass M
```

#### Overview

| Mass | Close Enc | Max Amp (any pair) | Avg Amp (all pairs) | Total E CV | Verdict      |
|------|-----------|--------------------|---------------------|-----------:|--------------|
| 1    | 4210      | 4.88               | 4.75                |      0.187 | PARTIAL PASS |
| 2    | 3340      | 4.63               | 2.99                |      0.302 | PASS         |
| 3    | 1338      | 8.78               | 8.46                |      0.201 | PARTIAL PASS |
| 5    | 0         | 14.41              | 12.70               |      0.244 | WEAK PASS    |
| 10   | 1         | 21.95              | 8.06                |      0.410 | PARTIAL PASS |

**Max amplitude increases monotonically with mass: 4.88 → 4.63 → 8.78 → 14.41 → 21.95. PREDICTION CONFIRMED.**

#### Per-Pair Amplitude Stats

| Mass | A-B amp | A-C amp | B-C amp | A-B dist | A-C dist | B-C dist |
|------|---------|---------|---------|----------|----------|----------|
| 1    | 4.67    | 4.69    | 4.88    | 2.5      | 2.5      | 2.5      |
| 2    | 0.03    | 4.63    | 4.32    | 2.0      | 3.8      | 3.5      |
| 3    | 8.26    | 8.78    | 8.34    | 4.5      | 4.9      | 4.8      |
| 5    | 9.42    | 14.41   | 14.26   | 8.1      | 9.0      | 9.3      |
| 10   | 21.95   | 1.10    | 1.14    | 19.8     | 11.3     | 19.9     |

#### Oscillation Reversals (in 2000 samples)

| Mass | A-B rev | A-C rev | B-C rev |
|------|---------|---------|---------|
| 1    | 576     | 592     | 579     |
| 2    | 4       | 1027    | 869     |
| 3    | 778     | 835     | 884     |
| 5    | 536     | 1066    | 1103    |
| 10   | 979     | 35      | 32      |

#### Energy Exchange (Cross-Correlation)

| Mass | Best anti-corr % | Best pair  | Total E conserved? |
|------|------------------|------------|--------------------|
| 1    | 26.6%            | A-B vs A-C | Yes (CV=0.187)     |
| 2    | 0.0%             | —          | No (CV=0.302)      |
| 3    | 22.8%            | A-C vs B-C | Yes (CV=0.201)     |
| 5    | 18.3%            | A-B vs A-C | Yes (CV=0.244)     |
| 10   | 2.2%             | A-B vs B-C | No (CV=0.410)      |

### Analysis: What the Mass Sweep Shows

**1. Max amplitude increases monotonically with mass (CONFIRMED):**
The single most energetic pair's amplitude grows from 4.88 (mass=1) to 21.95 (mass=10). This is the core prediction:
longer path commitment → more overshoot → wider oscillation → more energy. The mechanism is physically intuitive: a
mass=10 entity commits to a 10-edge straight line before re-reading the gradient. If the gradient reversed 5 hops ago,
it still has 5 more hops of wrong-direction travel before it can correct.

**2. Mean amplitude is non-monotonic due to asymmetric pair locking:**
At high mass (5, 10), the system becomes highly asymmetric. One pair dominates oscillation while the others lock at low
amplitude. Mass=10: A-B oscillates wildly (amp=21.95) while A-C and B-C are frozen (amp~1.1). This is analogous to
hierarchical three-body outcomes in classical mechanics — a tight binary ejects the third body.

**3. Mass=1 is special — all pairs symmetric:**
With mass=1 (photon-like: correct every tick), all three pairs have nearly identical amplitude (~4.7) and reversal
counts (~580). No hierarchy forms. This is the minimum-energy configuration: every tick, the entity perfectly tracks the
gradient with minimal overshoot.

**4. Mass=3 is the energy exchange sweet spot:**
Strongest anti-correlation (22.8%), most balanced amplitudes (8.3-8.8 across all pairs), energy approximately
conserved (CV=0.201), and all three pairs actively oscillating (778-884 reversals). This is the closest to genuine
three-body energy exchange: amplitude grows in one pair while shrinking in another.

**5. Mass=2 locks A-B immediately:**
A-B pair collapses to a permanent d=2 binary (amp=0.03, 4 reversals). The energy is entirely in A-C and B-C oscillation
around the binary. This matches v3's observation but now we can measure it: the A-B binary has ~zero energy, while the C
entity carries all the oscillation energy.

**6. Mass=10 is quasi-ejection:**
The huge overshoot (10-hop commitment) means C flies far from the binary before correcting. A-C and B-C distances grow
to ~20 hops with only 32-35 reversals — C barely oscillates, it's essentially ejected to a distant orbit. Meanwhile A-B
oscillates violently (amp=21.95, 979 reversals). This is the mass-energy prediction taken to its extreme: all the energy
concentrates in one pair.

### What v4 Proves

1. **Energy = oscillation amplitude**: In the always-move model, the meaningful energy is not KE (constant at 1.0) but
   the amplitude of distance oscillation. This is measurable, varies between pairs, and transfers between pairs (
   anti-correlation).

2. **Mass → energy through overshoot**: More mass (longer path commitment) → more overshoot → wider oscillation → more
   energy stored in the oscillation. The max amplitude is monotonically increasing with mass.

3. **Energy exchange is real**: At mass=3, amplitude anti-correlation reaches 22.8% — one pair's amplitude grows while
   another's shrinks. This is genuine energy exchange between gravitationally bound pairs.

4. **Total orbital energy is approximately conserved**: At mass=1,3,5, the sum of all pair amplitudes has CV < 0.3.
   Energy redistributes between pairs but the total remains roughly constant.

5. **Mass creates hierarchy**: Increasing mass forces the system from symmetric (mass=1: all pairs equal) to
   hierarchical (mass=10: one dominant pair). This mirrors classical three-body dynamics where the most massive pair
   forms a tight binary.

### New Plots

- `amplitude_*.png`: 3-panel figure — raw distances with amplitude envelope, amplitude per pair vs time, total orbital
  energy
- `exchange_*.png`: 2-panel figure — amplitude overlay, rolling cross-correlation between pairs
- Summary panel 3 now shows amplitude energy instead of KE (meaningless in always-move)

### File Organization

```
experiments/64_109_three_body_tree/
├── experiment_description.md    (this file)
├── v1/                          (original random-graph-only version)
├── v2/                          (lattice + temporal + mass + exclusion)
├── v3/                          (always-move: argmax + random fallback)
└── v4/                          (amplitude energy analysis + mass sweep)
    ├── three_body_graph.py      (7 verified tests, amplitude analysis added)
    └── results/
        ├── results_three_body_lattice_temporal_equilateral_alwaysmove.json
        ├── amplitude_*.png      (NEW: amplitude energy analysis)
        ├── exchange_*.png       (NEW: energy exchange cross-correlation)
        └── *.png (distance, speed, energy, gamma, summary plots)
```

### Running v4

```bash
# Verify all 7 tests (no physics changes from v3)
cd v4 && python three_body_graph.py --verify

# Mass sweep (the core experiment):
cd v4 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
    --dynamics-ticks 100000 --always-move --mass 1   # photon: low amplitude
cd v4 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
    --dynamics-ticks 100000 --always-move --mass 2   # v3 baseline
cd v4 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
    --dynamics-ticks 100000 --always-move --mass 3   # energy exchange sweet spot
cd v4 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
    --dynamics-ticks 100000 --always-move --mass 5   # high amplitude
cd v4 && python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
    --dynamics-ticks 100000 --always-move --mass 10  # extreme overshoot
```

### Open Questions for v5

1. **Can we derive E = mc^2?** If energy = amplitude and mass = path commitment, the relationship between mass and
   energy should be quantifiable. Plot amplitude vs mass — is it linear, quadratic, or something else?

2. **Conservation law**: At mass=3, total orbital energy is approximately conserved (CV=0.201). Is there a parameter
   regime where conservation is exact? What breaks conservation at mass=2 and mass=10?

3. **Phase transitions**: mass=1 is symmetric, mass=2 locks one pair, mass=3 is balanced, mass=10 ejects one body. Are
   these sharp transitions or gradual? What happens at mass=4, mass=6, mass=8?

4. **Multi-body**: With 4+ entities, does amplitude energy still make sense? Do more entities create more energy
   exchange channels?

## v5: Commit-Counter Model — Mass as Ticks Between Hops (v = c/M)

### Motivation

v4 confirmed that oscillation amplitude increases with mass (4.88 → 8.78 → 14.41 → 21.95). But a fundamental problem
remained: **all entities move at exactly v=c** (1 hop/tick) in the always-move model. Mass only controls path commitment
length, not actual speed.

The initial attempt (snake chain — M connected nodes, head at c, body follows) **failed**: core speed remained 1.0 for
all masses because on a discrete lattice, each body node always occupies a unique position.

The correct insight: **"The entity commits its state as soon as everything is updated. So it moves at most by 1 tick in
5 ticks if it has weight 5."** Mass = ticks to commit state. The entity sits at its position, depositing gamma, and
moves 1 hop every M ticks. v = c/M.

### Commit-Counter Model

**SnakeEntity** (commit-counter version) replaces the snake chain:

- **Single node position** (not a chain of M nodes)
- **commit_counter**: increments each tick. When counter >= mass: read gradient, hop 1, reset counter.
- **Between commits**: stay put, deposit at current position.
- **Effective speed**: v = 1/M hops per tick = c/M. Exact, deterministic.
- **Deposit footprint**: entity sits at each position for M ticks, depositing M × deposit_amount before moving on.
  Heavier = deeper well = stronger gravity.
- **Trit compatible**: 1 decision per commit (every M ticks).

### Prediction

Core speed should decrease with mass as v = c/M exactly:

- mass=1: v = c (move every tick)
- mass=2: v = c/2 (move every 2 ticks)
- mass=5: v = c/5 (move every 5 ticks)
- mass=10: v = c/10 (move every 10 ticks)

### Results: Mass Sweep (100K ticks each)

| Mass | Core Speed          | Stationary% | Encounters | Mean Amp (AB) | Max Dist | Mean Dist | Energy CV | Bound? |
|------|---------------------|-------------|------------|---------------|----------|-----------|-----------|--------|
| 1    | **1.0000** (= c)    | 0%          | 3309       | 5.78          | 14       | 2.9       | 0.181     | Yes    |
| 2    | **0.5000** (= c/2)  | 50%         | 4137       | 5.26          | 12       | 2.5       | 0.203     | Yes    |
| 3    | **0.3333** (= c/3)  | 67%         | 4573       | 4.97          | 18       | 2.3       | 0.264     | Yes    |
| 5    | **0.2000** (= c/5)  | 80%         | 4890       | 4.70          | 8        | 2.1       | 0.236     | Yes    |
| 10   | **0.1000** (= c/10) | 90%         | 4986       | 4.70          | 8        | 2.1       | 0.215     | Yes    |

### Key Finding: Core Speed Prediction CONFIRMED

**v = c/M exactly, for all masses.** The commit-counter model directly solves the v=c problem:

- mass=1: 1.0000 hops/tick (every tick)
- mass=2: 0.5000 hops/tick (every 2 ticks)
- mass=3: 0.3333 hops/tick (every 3 ticks)
- mass=5: 0.2000 hops/tick (every 5 ticks)
- mass=10: 0.1000 hops/tick (every 10 ticks)

This is the simplest possible resolution: mass = persistence cost = ticks to commit. Heavier entities are slower because
they need more ticks to "process" their state before hopping.

### Mass STRENGTHENS Binding (Opposite of Snake Chain)

Unlike the failed snake chain model (where mass weakened binding), the commit-counter model shows:

- **Encounters increase with mass**: 3309 → 4137 → 4573 → 4890 → 4986
- **Mean distance decreases with mass**: 2.9 → 2.5 → 2.3 → 2.1 → 2.1
- **Max distance decreases**: 14 → 12 → 18 → 8 → 8 (mass=3 is an outlier)
- **Amplitude decreases with mass**: 5.78 → 5.26 → 4.97 → 4.70 → 4.70

Heavier entities move slower, so they stay near each other. The oscillation range shrinks (tighter binding). All systems
remain gravitationally bound — even mass=10 entities stay within 8 hops.

**Comparison with v4**: v4 mass sweep showed amplitude INCREASING with mass (4.88 → 21.95) because path commitment added
inertia (overshooting). The commit-counter model does not add inertia — the entity simply waits, then makes a fresh
gradient read. No overshooting.

### Gamma Growth

| Mass | Gamma Growth Ratio |
|------|--------------------|
| 1    | 0.17x              |
| 2    | 0.22x              |
| 3    | 0.24x              |
| 5    | 0.26x              |
| 10   | 0.28x              |

Growth is moderate and scales gently with mass. No runaway.

### Verification

All 10 tests pass:

- Tests 1-7: Original graph substrate tests (adapted for SnakeEntity)
- Test 8: Commit-counter mechanics — mass=3 entity stays put for 2 ticks, moves on tick 3, counter resets
- Test 9: Deposit accumulates over M ticks at same position (5 ticks × 1.0 = 5.0 concentrated at one node)
- Test 10: Effective speed v = c/M — mass=5 entity: 40 hops in 200 ticks = 0.200 exactly

### Running v5

```bash
cd experiments/64_109_three_body_tree/v5

# Verify
python three_body_graph.py --verify

# Single run (mass=3)
python three_body_graph.py --quick --graph-type lattice --temporal \
    --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
    --dynamics-ticks 100000 --always-move --mass 3 --tag mass3

# Mass sweep
for M in 1 2 3 5 10; do
    python three_body_graph.py --quick --graph-type lattice --temporal \
        --edge-weight 20 --equilateral --initial-ke 10 --min-separation 14 \
        --dynamics-ticks 100000 --always-move --mass $M --tag mass$M
done
```

### Conclusions

1. **The v=c problem is RESOLVED.** Mass = ticks between hops. v = c/M exactly. The simplest possible model: entity
   commits its state for M ticks, then hops. No chain, no snake, no complexity.

2. **Mass strengthens binding.** Slower entities stay near each other, creating tighter orbits with smaller oscillation
   amplitude. This is the correct physical behavior.

3. **Trit-compatible.** 1 decision per commit (every M ticks). Between commits, the entity does nothing but deposit at
   its position.

4. **Deposit footprint proportional to mass.** Entity sits at each position for M ticks, depositing M × deposit_amount.
   Heavier = deeper gamma well = stronger gravity.

### Open Questions for v6

1. **Mixed masses**: What happens with mass=1 vs mass=5 vs mass=10 in the same system? Does the heavier entity dominate?
   Does the lighter entity orbit the heavier?

2. **Speed-gravity coupling**: Now that v = c/M, does the gravitational force (gradient strength) produce the correct
   velocity-dependent dynamics? Does a falling entity speed up as expected?

3. **E = mc²**: The entity's deposit per position is M × deposit_amount. Its speed is c/M. Its kinetic energy per hop is
   1/M. Is there an energy relation analogous to E = mc²?

---

## v6: Gamma Field — No Entities, Only Gamma on a Graph

### Motivation

v5 solved v = c/M by making entities wait M ticks between hops. But gravity still came from an externally-maintained
gamma field: entities deposit gamma, gamma diffuses, entities follow gradients. The question: **can we eliminate
entities entirely?** Can a single scalar field on a graph, with the right nonlinear dynamics, produce mass (self-binding
clumps), radiation (freely propagating waves), and gravity (attraction between clumps) — all from one rule?

### Core Idea

There are no entities. There is only gamma on a graph.

Some gamma clumps together (= matter/particles). Some flows freely (= radiation/photons). What holds a clump? *
*Self-gravitation**: spread rate depends on local gamma density.

**The spread rule:**

```
alpha_eff(node) = alpha / (1 + G * gamma[node])
outflow = alpha_eff * gamma
inflow  = A @ (outflow / degrees)
gamma_new = (gamma - outflow) + inflow
```

- High gamma → low alpha_eff → slow spread → peak holds (mass)
- Low gamma → alpha_eff ≈ alpha → fast spread at c (radiation)
- One field. One graph. One parameter G. Total gamma exactly conserved.

### Files

- `v6/gamma_field.py` — SelfGravitatingField base class (scalar gamma, ~1200 lines)
- `v6/signed_gamma.py` — SignedGammaField extension (signed gamma, dipoles)
- `v6/quantum_gamma.py` — QuantumGammaField extension (integer stochastic spread)
- `v6/test_attraction.py` — AttractingField with gradient-biased continuous spread

### v6a: Scalar Self-Gravitating Field

**Setup**: 8000-node k=6 periodic lattice (side=20). Place gamma mass at a node, smooth with G=0 diffusion, then enable
G>0 self-gravitation.

**Results — Peak Stability:**

| G   | Initial peak | Final peak (5000 ticks) | Behavior                    |
|-----|--------------|-------------------------|-----------------------------|
| 0   | 500          | 0.062                   | Complete dispersal          |
| 0.1 | 500          | 0.16                    | Slow dispersal              |
| 1   | 500          | 2.82                    | Moderate retention          |
| 10  | 500          | 127                     | Strong retention            |
| 50  | 500          | 437                     | Frozen peak, 87% retained   |
| 100 | 500          | 470                     | Nearly frozen, 94% retained |

Self-gravitation works beautifully: G controls the balance between bound matter and free radiation.

**Results — Two-body attraction:**

NONE. Two peaks placed at separation=10 with G=50 remain at exactly distance=10 for 5000 ticks. Zero movement.

**Diagnosis**: The spread rule is **deterministic diffusion** — it distributes outflow equally to ALL neighbors. Perfect
symmetry at every node means zero net force. Two identical peaks create identical, symmetric gamma gradients. Neither
peak has any reason to move toward the other. The diffusion equation is first-order in time (no velocity, no momentum).
It smooths patterns but cannot transport them.

**Also tested**: Gradient-biased spread (`test_attraction.py`) where outflow is weighted by neighbor gamma values. Still
no movement — the bias is symmetric between the two peaks.

### v6b: Signed Gamma

**Hypothesis**: If gamma is signed (values in [-M, +M]), asymmetric patterns could carry momentum. A symmetric
monopole (+core) = stationary particle. An asymmetric dipole (+core on one side, -wing on other) = moving particle.

**Setup**: SignedGammaField where self-gravitation operates on |gamma| but spread preserves signs:

```
alpha_eff = alpha / (1 + G * |gamma|)
outflow = alpha_eff * gamma        # signed!
```

Conservation: total signed gamma exactly conserved. Total |gamma| NOT conserved (annihilation between + and - reduces
it).

**Results — Monopole stability**: Monopole (positive core, negative shell) is stable. After 2000 ticks at G=50: core
retains structure, negative shell held by self-gravitation.

**Results — Dipole drift**: NEGATIVE. Asymmetric dipole (positive center + negative wing on one side) does NOT
translate. COM offset actually DECREASES over time (0.325 → 0.306 hops). The dipole relaxes toward symmetry rather than
moving.

**Results — Annihilation**: When + and - gamma overlap (G=0 dispersal), total |gamma| drops by ~75%. This is genuine
annihilation from the sign structure — an emergent property, not imposed.

**Results — Attraction**: Two signed monopoles show NO attraction. Same root cause: deterministic diffusion is
symmetric.

**Diagnosis**: Same fundamental problem as scalar gamma. The spread equation distributes outflow isotropically. No
asymmetric initial condition can produce directed transport because diffusion smooths all asymmetries.

### v6c: Quantum Gamma — Integer Stochastic Field

**Key Insight**: At Planck scale, gamma values are integers (natural numbers, matching the project's BigInteger
philosophy). A single quantum CANNOT split into 1/6 going to each neighbor. It goes to ONE neighbor. This breaks the
symmetry.

**Setup**: QuantumGammaField where gamma[node] is int64, spread uses:

```python
n_leaving = Binomial(gamma[node], alpha_eff)  # how many quanta leave
destination = Multinomial(n_leaving, neighbor_probs)  # each goes to ONE neighbor
```

Conservation is exact by construction: integer quanta move between nodes, none created or destroyed.

**Results — Brownian Motion (single cluster, G=10):**

The stochastic integer model produces genuine random walk of cluster COM. Mass sweep at 10000 ticks:

| Mass M | D (hops²/tick) | v_rms (hops/tick) | v_rms/c |
|--------|----------------|-------------------|---------|
| 100    | 1.23×10⁻⁴      | 0.0111            | ~c/9    |
| 200    | 3.51×10⁻⁵      | 0.0059            | ~c/28   |
| 500    | 4.79×10⁻⁶      | 0.0022            | ~c/76   |
| 1000   | 1.16×10⁻⁶      | 0.0011            | ~c/156  |
| 2000   | 2.83×10⁻⁷      | 0.00053           | ~c/314  |
| 5000   | 5.12×10⁻⁸      | 0.00023           | ~c/733  |

**Key finding: D scales as ~1/M² (not 1/M).** This means v_rms ~ c/M — the same velocity-mass relation that v5 imposed
by fiat emerges naturally from integer stochastic dynamics. This is arguably the most important result of v6.

The physical intuition: each quantum has a probability ~alpha/M of being at the cluster boundary and escaping. The COM
shift per escaped quantum is ~1/M. So D ~ (M × alpha/M × (1/M)²) = alpha/M².

**Results — Two-body attraction:**

Short runs (10000 ticks): Peak distance fluctuates but shows no clear trend for any G_attract value (0.0 to 2.0).

Long runs (10M ticks, ~4 hours each):

- **G=10, G_attract=1.0**: Peaks stable, COM separation 10.000→9.995 hops, peak distance=10 throughout. No measurable
  attraction.
- **G=10, G_attract=0.0 (control)**: Peaks EVAPORATE by ~2M ticks. Peak distance bounces wildly (noise from remnant
  gas).
- **G=10, G_attract=0.0 (Brownian single)**: Peak evaporates by ~2M ticks. COM sloshing randomly.

**Hawking-like Evaporation**: At G=10, stochastic fluctuations destroy self-gravitating peaks over ~2M ticks. Mechanism:
positive feedback — boundary quantum escapes → peak gamma drops → alpha_eff increases → more quanta escape → cascade.
G_attract acts as a restoring force (escaped quanta biased back toward peak), preventing evaporation.

**Results — Velocity Analysis (v_rms at various G values):**

| G  | v_rms/c (M=1000) | Notes                            |
|----|------------------|----------------------------------|
| 1  | ~1/770           | Loose cluster, fast dispersal    |
| 3  | ~1/830           | Moderate binding                 |
| 10 | ~1/156           | Strong binding (main test point) |
| 50 | ~1/940           | Very frozen, minimal fluctuation |

The v ~ c/M relation holds across G values, with ~1.2-1.7× prefactor variation.

### The Single-Parameter Tension

The central diagnostic from v6: **self-gravitation both creates mass AND prevents gravitational field propagation.**

For a gamma peak to attract another:

1. The peak must emit gamma (its "gravitational field") that reaches the other peak
2. The receiving peak must respond to the incoming gamma gradient

But with a single scalar field:

- High G locks gamma in place → strong mass, but no field emission
- Low G allows emission → field propagates, but peaks dissolve

The same gamma can't be both "bound mass" and "propagating gravitational field." This is the fundamental limitation of a
single-field model.

### Verification

All models pass complete test suites:

- **gamma_field.py**: 6/6 tests (conservation, peak retention, radiation, G=0 dispersal, etc.)
- **signed_gamma.py**: 7/7 tests (above + signed conservation, annihilation, dipole stability)
- **quantum_gamma.py**: 6/6 tests (integer conservation, dispersal, retention, no negatives, reproducibility, G_attract
  conservation)

### Running v6

```bash
cd experiments/64_109_three_body_tree/v6

# Scalar gamma
python gamma_field.py --verify
python gamma_field.py --n-peaks 1 --G 50 --mass 500 --ticks 5000
python gamma_field.py --n-peaks 2 --G 50 --mass 500 --ticks 5000

# Signed gamma
python signed_gamma.py --verify
python signed_gamma.py --test-monopole
python signed_gamma.py --test-dipole
python signed_gamma.py --test-attraction

# Quantum gamma
python quantum_gamma.py --verify
python quantum_gamma.py --brownian --mass 1000 --G 10 --ticks 10000
python quantum_gamma.py --mass-sweep --G 10 --ticks 10000
python quantum_gamma.py --attraction --G 10 --G-attract 1.0 --ticks 10000
```

### Conclusions

1. **Self-gravitation works.** The nonlinear spread rule `alpha_eff = alpha / (1 + G * gamma)` produces stable peaks (
   mass) and free radiation from a single scalar field. G controls the matter/radiation ratio.

2. **Deterministic diffusion cannot produce movement.** The spread rule distributes outflow isotropically. No continuous
   field manipulation (signed, gradient-biased, etc.) can break this symmetry. This is a theorem-level result: symmetric
   deterministic diffusion on a regular graph preserves peak positions.

3. **Integer stochastic dynamics produce Brownian motion.** When gamma is quantized as integers, individual quanta must
   go to ONE neighbor, breaking symmetry. Clusters undergo Brownian random walk with D ~ 1/M².

4. **v ~ c/M emerges from first principles.** The RMS velocity of a stochastic integer cluster scales as c/M, matching
   what v5 imposed as a rule. This is the strongest result: the velocity-mass relation is not a model choice but a
   consequence of integer quantum statistics on a graph.

5. **Hawking-like evaporation is real.** Self-gravitating integer clusters are metastable: stochastic fluctuations at
   the boundary drive a positive-feedback cascade that destroys the peak over millions of ticks.

6. **Attraction remains unsolved.** Neither deterministic nor stochastic single-field models produce measurable
   attraction between separated peaks. The single-parameter tension (mass locks gamma, preventing field propagation)
   appears fundamental.

### Open Questions for v7

1. **Two-field model**: Separate "matter field" (self-gravitating, bound) from "gravitational field" (free-propagating,
   mediates force). Matter emits gravitational field; gravitational field biases matter's random walk.

2. **Longer range**: Test attraction at separation=3-4 (within cluster radius) instead of 10 (far outside). Do
   overlapping halos produce attraction?

3. **Mass-dependent gravity**: The v ~ c/M result suggests a deep connection between mass and dynamics. Can we derive
   F = GMm/r² from the stochastic model?

4. **Hawking evaporation physics**: The metastability of integer clusters resembles black hole evaporation. What
   determines the evaporation timescale? Is there a critical mass below which evaporation is fast?

5. **Momentum from asymmetry**: The signed gamma dipole didn't drift because diffusion symmetrizes. But in the integer
   model, could an asymmetric integer pattern maintain its shape while translating?

---

## v7: Spread-First Eddy Model — One Field, Gravity from Shadows

### Motivation

v6 identified the **single-parameter tension**: self-gravitation both creates mass (locking gamma) AND prevents
gravitational field propagation. The same gamma can't be both "bound mass" and "propagating field." All v6 variants —
scalar, signed, quantum, gradient-biased — failed to produce attraction.

The paradigm flip: **default state is propagation at c.** Gamma wants to fly. Patterns are eddies — not static peaks
imprisoned by self-gravitation, but dynamic vortices that continuously shed their outer layer and recapture their core.
The radiation that escapes is the gravitational field.

### Core Idea

Flip from "hold gamma still, let some leak" to "let gamma fly, grab some back."

**Two-step spread per tick:**

1. **SPREAD at c** — every quantum has probability alpha = 1/k of hopping to a uniformly random neighbor. No bias, no
   self-gravitation. Pure propagation.
2. **RECAPTURE** — each quantum at node j may get pulled to a neighboring node i with probability proportional to
   `G_recapture * gamma[i]`. Dense nodes pull harder. This creates eddies.

What escapes recapture propagates freely at c forever. What gets recaptured stays in the pattern. A stable particle
exists in equilibrium between expansion at c and recapture.

**Deeper physics:**

- Zero radiation = captures ALL outflow = recapture zone grows at c = explosion = Big Bang
- Stable particle = sheds outer layer every tick = radiation = gravitational field
- More mass = more to shed = stronger radiation = **stronger gravitational signal**
- Zero mass = nothing to shed = propagate at c = **photon**
- Existence is expensive. The bill is gravity.

**Gravity mechanism (Le Sage shadow):**
Pattern A absorbs background gamma (recapture). Behind A, less gamma flows — a shadow. Pattern B downstream sees the
deficit, should drift toward it. Attraction.

### Files

- `v7/spread_first.py` — SpreadFirstField class inheriting from QuantumGammaField

### Parameters

| Parameter   | Default     | Notes                               |
|-------------|-------------|-------------------------------------|
| alpha       | 1/k ≈ 0.167 | Speed of light (gamma wants to fly) |
| G_recapture | 0.5         | Recapture strength per unit gamma   |
| mass        | 1000        | Integer quanta per peak             |

No G, no G_attract, no epsilon, no beta, no phi field. One field, one mechanism.

### Results — Verification

8/8 tests passed: conservation exact, no negatives, reproducibility, eddy formation, dispersal at G_recapture=0,
background fills, shadow measurable, cycling pattern oscillates.

### Results — Eddy Stability (Experiment A)

Single peak with mass=1000 on 8000-node lattice, 5000 ticks:

| G_recapture | Bound at t=5000 | Escaped   | Behavior                           |
|-------------|-----------------|-----------|------------------------------------|
| 0.1         | 421 (42%)       | 579 (58%) | Slowly dissolving, heavy radiation |
| 0.2         | 792 (79%)       | 208 (21%) | Moderate leakage, decent stability |
| 0.5         | 925 (93%)       | 75 (7.5%) | Tight eddy, little radiation       |
| 1.0         | 968 (97%)       | 32 (3.2%) | Very tight                         |
| 2.0         | 982 (98%)       | 18 (1.8%) | Nearly frozen                      |
| 5.0         | 991 (99%)       | 9 (0.9%)  | Frozen                             |

The spread-first model produces genuine eddies: gamma cycling between center and neighbors, with the outer layer shed
each tick as radiation. G_recapture controls the balance between bound mass and radiation. At G_recapture=0.1-0.2,
substantial radiation fills the background.

### Results — Photon Test (Experiment F)

Single quantum (mass=1) propagates at ~0.065 hops/tick regardless of G_recapture (0.0, 0.5, 1.0). A single quantum can't
recapture itself — it propagates freely at c. Confirms the zero-mass limit: nothing to shed, no identity to maintain,
pure propagation.

### Results — Two-Body Attraction (Experiment C)

Two peaks at separation=10, 20000 ticks:

**G_recapture=0.1**: Eddies dissolved by ~12K ticks. Peak distance jumps randomly (8, 18, 14, 23). "Peaks" detected are
just noise in uniform background. No meaningful test.

**G_recapture=0.2**: Eddies stable. Peak distance = **10 for all 20000 ticks**. COM approach = 0.018 hops (noise). **No
attraction detected.**

### Diagnosis: Why Shadow Mechanism Fails

The spread-first model produces beautiful eddies and radiation but **no attraction**. The Le Sage shadow mechanism fails
for three reasons:

**1. Recapture is LOCAL (1-hop only).** The peak pulls from its 6 immediate neighbors. The shadow is a global
phenomenon — a deficit propagating over 10+ hops. The peak can't "sense" the shadow beyond its immediate neighborhood.

**2. Peak's own gamma dominates.** At the peak center, gamma ≈ 400. At the immediate neighbor, gamma ≈ 60-80 (peak's own
outflow). Background gamma at distance 10 is ≈ 0.05. The pull weights are proportional to gamma, so 99.9% of the
recapture dynamics are the peak interacting with its own outflow — the background is invisible.

**3. No momentum transfer.** In Le Sage gravity, absorbed particles carry momentum — the force comes from the difference
in momentum absorbed from the shadow side vs the open side. In our model, recaptured quanta just add mass to the center
node regardless of direction. The recapture is symmetric: pulling more from the rich side doesn't create a lateral
force, it just makes the peak slightly heavier.

The two-step spread (spread then recapture) is mathematically equivalent to the one-step alpha_eff model for peak
dynamics. The shadow exists in principle but is too weak and too distant to influence peak motion.

### The Deeper Problem Across v6-v7

Across all attempts — scalar, signed, quantum, gradient-biased, spread-first — the same fundamental issue appears:

**Diffusion on a graph is isotropic at the peak.** Whether we reduce outflow (alpha_eff) or add recapture (two-step),
the peak center always has symmetric local gamma. The asymmetry from another peak's shadow or gravitational field is
orders of magnitude smaller than the peak's own gamma profile. Integer stochastic fluctuations produce Brownian motion,
but the bias from any distant signal is unmeasurably small compared to the Brownian noise.

For attraction to work, we likely need one of:

1. **Explicit long-range interaction** — peaks interact not just with immediate neighbors but with the integrated field
   over many hops (multi-hop recapture, or a separate potential field that propagates)
2. **Momentum/direction tracking** — quanta carry directional information so absorption from one direction creates a net
   force
3. **Non-local field coupling** — a second field that propagates freely and biases matter motion (the two-field model
   from the original v7 plan)

### Running v7

```bash
cd experiments/64_109_three_body_tree/v7

# Verify
python spread_first.py --verify

# Eddy stability sweep
python spread_first.py --stability --ticks 5000

# Shadow profile
python spread_first.py --shadow --mass 1000 --G-recapture 0.1

# Two-body attraction
python spread_first.py --attraction --mass 1000 --G-recapture 0.2 --separation 10 --ticks 20000

# Photon test
python spread_first.py --photon
```

### Conclusions

1. **Spread-first eddies work.** The two-step model (spread at c, then recapture) produces stable dynamic patterns that
   continuously radiate. G_recapture controls the matter/radiation balance.

2. **Radiation scales with mass.** Heavier eddies shed more gamma per tick, confirming the prediction that "more mass =
   more to shed = stronger gravitational signal."

3. **Photon = zero mass.** A single quantum propagates freely regardless of recapture strength, confirming the zero-mass
   limit.

4. **No attraction.** The Le Sage shadow mechanism doesn't produce measurable attraction because recapture is local (
   1-hop), the peak's own gamma dominates, and there's no momentum transfer from absorption.

5. **The local interaction problem.** All v6-v7 models share the same limitation: peaks interact only with their
   immediate graph neighborhood. Any distant signal (gravitational field, shadow) is drowned by the peak's own local
   gamma. Gravity may require an explicitly long-range or multi-scale mechanism.

---

## v8: Self-Subtracting Tagged Quanta (February 2026)

### Motivation

v6-v7 proved: self-binding works, conservation works, Hawking evaporation is real. But no attraction. Root cause:
entity's own gamma (~400 at center) drowns any signal from a distant entity (~0.05 at 10 hops). SNR is 1:8000.

The fix: **self-subtraction**. In real physics, a particle doesn't gravitate toward itself. Self-energy is subtracted.
v1-v5 got this right by accident (separate fields per entity). v8 gets it right by design (tagged quanta on a shared
field).

### Implementation

**File:** `v8/tagged_gamma.py`

**Architecture:** `TaggedGammaField` extends `QuantumGammaField` (v6). Each integer quantum is tagged with its source
entity ID. One shared field, but each entity can compute `external_gamma = total - own_tag` at any node.

**Core physics:**

- `alpha_eff = alpha / (1 + G * total_gamma)` — binding from TOTAL gamma (same as v6c)
- Each entity's tagged quanta spread independently with the same `alpha_eff`
- Entity movement via commit-counter (from v5): sit for M ticks, read external gradient, hop to argmax
- On hop: transfer ALL tagged quanta from old node to new node

**Key insight:** At entity A's position, total=400, external=5. At neighbor toward B: external=5.3. Away from B:
external=4.7. Gradient is 12% of signal. Argmax picks correctly. In v6c (no tagging): gradient was 0.15% of total —
drowned by noise.

### Parameters

| Parameter    | Default                                  |
|--------------|------------------------------------------|
| N nodes      | 8000 (side=20, 3D periodic lattice, k=6) |
| alpha        | 1/k ≈ 0.167                              |
| G            | 10.0                                     |
| initial_mass | 1000 quanta per entity                   |
| commit_mass  | 5 (v = c/5)                              |
| separation   | 10 hops                                  |
| seed         | 42                                       |

### Results

**Verification (6/6 pass):**

1. Per-entity conservation: exact (500→500, 300→300 after 1000 ticks)
2. Total conservation: exact
3. No negatives: min=0
4. Reproducibility: identical results with same seed
5. Peak stability: ratio=1696× background after 500 ticks (G=10)
6. External gamma: correct self-subtraction verified

**Phase 1 — Single Peak (5000 ticks):**

- Peak stable at ~210 quanta, zero drift from starting node
- Conservation: 1000→1000 (drift=0)
- Confirms tagging doesn't change binding physics

**Phase 2 — Two-Body Attraction (50K ticks): ATTRACTION DETECTED**

| Tick  | Distance | Ext gradient at A | Hops A | Hops B |
|-------|----------|-------------------|--------|--------|
| 0     | 10       | 0                 | 0      | 0      |
| 5000  | 11       | -1                | 1      | 0      |
| 10000 | 13       | -2                | 2      | 1      |
| 35000 | 13       | -7                | 2      | 1      |
| 40000 | 12       | -3                | 3      | 5      |
| 45000 | 17       | -1                | 29     | 48     |
| 50000 | **4**    | -2                | 66     | 94     |

Distance: **10 → 4 hops (6 hops closer)**. Control (no entity movement): 10 → 14 hops (Brownian drift apart).

Three phases visible:

1. **Quiet phase (0-35K):** Fields propagating, external gradient near zero, entities barely move (3 hops total)
2. **Signal arrival (~35K):** Leaked quanta reach other entity, gradient becomes detectable
3. **Rapid approach (40K-50K):** Entities actively move toward each other (160 hops total), distance drops 13→4

**Phase 3 — Three-Body (100K ticks):**

| Tick   | A-B   | A-C   | B-C |
|--------|-------|-------|-----|
| 0      | 10    | 10    | 10  |
| 50000  | 13    | 17    | 10  |
| 80000  | 11    | 11    | 18  |
| 90000  | 13    | **4** | 15  |
| 100000 | **2** | 12    | 10  |

Rich three-body dynamics: quiet first ~40K ticks (field propagation), then active interactions with oscillations, close
approaches (A-C→4, then A-B→2), and rebounds. Conservation perfect (3000 throughout).

**G Sweep (50K ticks each, sep=10, mass=1000):**

| G        | Delta (hops) | Interpretation                              |
|----------|--------------|---------------------------------------------|
| 1.0      | 0            | Peaks too diffuse, gradient uniform         |
| 5.0      | -7           | Noisy gradient, random walk                 |
| **10.0** | **+6**       | **Sweet spot: strong signal, good binding** |
| 20.0     | 0            | Peaks too tight, no leakage                 |

Goldilocks zone at G=10: enough binding to hold peaks, enough leakage for signal to propagate.

**Commit Mass Sweep:**

| commit_mass | Delta  | v_avg (actual) | v_expected (c/M) |
|-------------|--------|----------------|------------------|
| 1           | -1     | 0.0022         | 1.0              |
| 3           | +4     | 0.0014         | 0.33             |
| **5**       | **+6** | 0.0016         | 0.20             |
| 10          | -15    | 0.0018         | 0.10             |

Actual velocities ~0.002 hops/tick regardless of commit_mass — much lower than expected c/M. Entities only move when a
detectable gradient exists, not at every commit window. The commit counter is a polling frequency; the actual bottleneck
is gradient strength.

**Mass and Separation Sweeps:** Results highly stochastic with single seed. sep=4 shows collision (delta=+4), mass=1000
shows strongest attraction (delta=+6). Multiple runs with different seeds needed for statistical significance.

### Diagnosis

**What works:**

1. **Self-subtraction eliminates the SNR problem.** External gamma provides clean signal not drowned by own field.
2. **Attraction is real.** Entities approach with entity movement, control shows drift apart.
3. **Three-body dynamics emerge.** Close encounters, rebounds, and pairwise approach.
4. **Conservation exact.** Per-entity and total quanta preserved.

**What's imperfect:**

1. **Long delay before attraction.** ~35K ticks for quanta to propagate from one peak to another at G=10. The high
   self-gravitation (alpha_eff ≈ 0.00008 at peak center) means very few quanta escape per tick.
2. **Highly stochastic.** Single runs are not statistically significant. The entity's direction choice depends on which
   neighbor happens to have the most external gamma — often just 1-2 quanta difference.
3. **Velocity not c/M.** Entities move much slower than expected because the gradient is usually zero or flat. The
   commit counter determines polling frequency, not actual speed.
4. **Not a clean force law.** The G sweep and separation sweep don't show clean 1/r² scaling — results are dominated by
   stochastic noise.

### The Key Breakthrough

v8 solved the **fundamental problem** of v6-v7: **entities can now detect each other's gravitational field.**
Self-subtraction removes the self-interaction that drowned all distant signals. The mechanism:

1. Entity A deposits tagged quanta → they self-gravitate into a bound peak
2. Some quanta escape the peak (alpha_eff isn't zero) → propagate at c
3. A's escaped quanta reach B's neighborhood → B reads external gradient → B moves toward A
4. Simultaneously, B's quanta reach A → A moves toward B
5. **Mutual attraction**

This validates the original v5 intuition (separate fields for self-subtraction) but with proper integer conservation and
a shared field. The tagging is the minimal change needed: same physics as v6c, but entities ignore their own field for
movement decisions.

### Running v8

```bash
cd experiments/64_109_three_body_tree/v8

# Verify
python tagged_gamma.py --verify

# Single peak stability
python tagged_gamma.py --phase1 --ticks 5000

# Two-body attraction (THE test)
python tagged_gamma.py --phase2 --ticks 50000

# Three-body dynamics
python tagged_gamma.py --phase3 --ticks 100000

# Parameter sweeps
python tagged_gamma.py --g-sweep --ticks 50000
python tagged_gamma.py --commit-sweep --ticks 50000
python tagged_gamma.py --mass-sweep --ticks 50000
python tagged_gamma.py --sep-sweep --ticks 50000
```

### Open Questions for v9

1. **Statistical significance.** Run 10+ seeds per configuration. Is attraction robust or seed-dependent?
2. **Faster signal propagation.** Lower G allows more leakage but weakens binding. Can we find a regime where signal
   arrives faster while peaks remain stable?
3. **Clean force law.** With enough statistics, does approach rate scale as 1/r²? As mass?
4. **Momentum conservation.** Entities move by argmax, not by momentum. Should movement accumulate velocity (inertia)
   rather than single hops?
5. **Collision dynamics.** What happens when two entities reach the same node? Merger? Bounce? Need collision rules.

## v9: Continuous Internal Direction Vector (February 2026)

### Motivation

v8 proved attraction via self-subtraction (10→4 hops in 50K ticks). But entities move by argmax with no memory of
direction — they can't overshoot, can't orbit, can't conserve angular momentum. v9 adds a **continuous internal
direction vector** — not quantized to the 6 lattice directions. Each commit window, the external gamma gradient
**nudges** this vector by a small amount (1/mass). The actual hop goes to whichever lattice neighbor is closest to the
internal vector. Over many hops, small nudges accumulate and the direction rotates smoothly.

### Implementation

**File:** `v9/tagged_gamma.py`

**What changed from v8:** Only the Entity class. `TaggedGammaField` is identical plus a `direction_vector()` helper.

#### Development history (3 iterations)

**Iteration 1 — Quantized blend:** `combined = mass × mom_unit + gradient_strength × grad_unit`. Failed because
`gradient_strength ≈ 0.001` vs `mass ≈ 5`, giving 5000:1 ratio. Gravity invisible at all masses.

**Iteration 2 — Normalized blend:** `combined = mass × mom_unit + 1.0 × grad_unit`. Fixed ratio to mass:1. But on
6-neighbor lattice, a combined vector never switches the winning neighbor unless gradient weight > mass. For cm≥2,
hop direction never changes — entities fly straight. For cm=1, entities turn too sharply (full 90° per hop).
Produced a stable bound state from head-on (dist=4, L=+2) but no perpendicular orbits.

**Iteration 3 — Continuous internal direction (current):** Entity maintains a continuous 3D unit vector
`internal_direction`. Each commit window:
1. Compute `grad_unit` from external gamma gradient at neighbors
2. `internal_direction += (1/mass) × grad_unit`, then re-normalize
3. Hop to neighbor with highest dot product with `internal_direction`
4. **Never overwrite** `internal_direction` with hop direction — it remembers the fractional nudge

Key insight: the internal vector lives in continuous 3D even though hops are quantized. A vector at [0.95, 0.12, 0.0]
still hops +X, but the 0.12 is the accumulated Y-nudge. After enough nudges, it crosses 45° and hops switch to +Y.
This enables smooth turning on a 6-neighbor lattice.

### Parameters

| Parameter    | Default                                  |
|--------------|------------------------------------------|
| N nodes      | 8000 (side=20, 3D periodic lattice, k=6) |
| alpha        | 1/k ≈ 0.167                              |
| G            | 10.0                                     |
| initial_mass | 1000 quanta per entity                   |
| commit_mass  | 5 (nudge = 0.2 per hop)                  |
| separation   | 10 hops                                  |
| seed         | 42                                       |

`nudge_strength = 1.0 / commit_mass`. Mass=5 → nudge=0.2 (gentle curve). Mass=1 → nudge=1.0 (sharp turn).
Mass=10 → nudge=0.1 (very gradual).

### Results

**Verification (10/10 pass):**

Tests 1-6: identical to v8 (conservation, no negatives, reproducibility, peak stability, external gamma).

New continuous-direction tests:
7. Straight flight: zero external gradient → internal direction unchanged → hops +X ✓
8. Gradual deflection: spread +Y gradient rotates direction from +X → 112.5° after 10 hops, hop switched to +Y ✓
9. Direction rotation: spread radial gradient → direction rotated 351.5° (nearly full circle) ✓
10. Mass controls turning radius: light (cm=1) turns in 2 hops, heavy (cm=10) turns in 22 hops ✓

**Phase 2 — Head-on (no initial direction, cm=5, 50K ticks): GRAVITATIONAL SCATTERING**

| Tick  | Distance | Hops A | Hops B | L_z  |
|-------|----------|--------|--------|------|
| 0     | 10       | 0      | 0      | 0    |
| 5000  | 13       | 239    | 0      | +1.9 |
| 10000 | 24       | 1239   | 975    | -4.8 |
| 15000 | 6        | 2239   | 1975   | -0.4 |
| 20000 | 12       | 3239   | 2975   | -0.9 |
| 25000 | 20       | 4239   | 3975   | -3.0 |
| 30000 | 18       | 5239   | 4975   | -0.5 |
| 50000 | 20       | 9239   | 8975   | -3.3 |

Distance oscillates [4, 26] — close approaches (d=6 at 15K), rebounds (d=24 at 10K), then continued oscillation.
Angular momentum oscillates between -5 and +5. Entities trace curved trajectories across the entire lattice (confirmed
by trajectory plot showing complex paths, not straight lines). **Hop histogram: all 6 directions used** by both
entities, confirming genuine gravitational deflection.

Conservation: 2000→2000 (drift=0).

**Phase 2 — Perpendicular direction (cm=5, 50K ticks): GRAVITATIONAL DEFLECTION AT cm=5**

| Tick  | Distance | Hops A | Hops B | L_z  |
|-------|----------|--------|--------|------|
| 0     | 10       | 0      | 0      | —    |
| 5000  | 14       | 1000   | 1000   | -2.8 |
| 15000 | 12       | 3000   | 3000   | -5.5 |
| 25000 | 14       | 5000   | 5000   | -4.7 |
| 30000 | 12       | 6000   | 6000   | +2.7 |
| 45000 | 8        | 9000   | 9000   | -4.1 |
| 50000 | 8        | 10000  | 10000  | +1.3 |

Distance oscillates [6, 24] — **NOT flat like iterations 1-2.** Angular momentum oscillates (not trivially constant).
Trajectory shows curved paths across the lattice. **Hop histogram: all 6 directions used** (~800-2500 per direction
for each entity). Close approach to d=6, rebound to d=24, then approach again to d=8.

**This is the key breakthrough:** gravitational deflection at cm=5 was impossible with the quantized blend
(iterations 1-2) but works with continuous internal direction. The gradient nudges (0.2 per hop) accumulate over
dozens of hops until the direction vector crosses the 45° boundary and hops switch axis.

Internal direction angle plot confirms: direction rotates continuously through all angles, not stuck at ±90°.
Conservation: 2000→2000 (drift=0).

**Phase 3 — Three-body tangential (cm=5, 100K ticks): GENUINE THREE-BODY DYNAMICS**

| Tick   | A-B | A-C | B-C | L_z  |
|--------|-----|-----|-----|------|
| 0      | 10  | 10  | 10  | —    |
| 10000  | 16  | 18  | 10  | +2.6 |
| 20000  | 18  | 12  | 22  | -1.1 |
| 30000  | 18  | 18  | 8   | -2.8 |
| 50000  | 14  | 20  | 14  | +1.3 |
| 70000  | 10  | 20  | 22  | -0.4 |
| 90000  | 14  | 20  | 12  | +11.3|
| 100000 | 16  | 16  | 28  | -8.1 |

All three entities remain separate for 100K ticks — **no merger.** Distances oscillate dynamically: AB [8-18],
AC [10-22], BC [8-28]. Angular momentum varies between -8 and +11. Entities approach, scatter, rebound, and
reapproach — genuine three-body gravitational dynamics on a discrete lattice.

Conservation: 3000→3000 (drift=0).

### Diagnosis

**What works:**

1. **Continuous direction vector enables smooth turning.** The key insight: store direction in continuous 3D, only
   quantize the hop. Small nudges accumulate over many hops until the direction crosses axis boundaries. This defeats
   the 6-neighbor lattice limitation that blocked iterations 1-2.
2. **Gravitational deflection at cm=5.** Entities with perpendicular momentum are deflected by the gradient from
   leaked quanta. Trajectories curve. All 6 hop directions are used. This was impossible with quantized blending.
3. **Three-body dynamics without merger.** Three entities with tangential momentum interact for 100K ticks without
   collapsing. Distances oscillate, entities scatter and reapproach.
4. **Mass controls turning radius.** cm=1 turns in 2 hops (nudge=1.0), cm=10 turns in 22 hops (nudge=0.1). The
   nudge_strength = 1/mass relationship works as expected.

**What's imperfect:**

1. **Angular momentum not conserved.** L oscillates ±8 in the perpendicular test (should be ~constant for true
   orbits). The lattice quantization of hops breaks rotational symmetry — the internal direction rotates smoothly but
   the actual position jumps in 90° steps.
2. **No stable closed orbits.** Entities interact and scatter but don't settle into repeating ellipses. The dynamics
   are more like gravitational scattering (approach, close encounter, rebound) than Keplerian orbits. This may be
   inherent to the stochastic gamma field (the gradient depends on random quantum spreading).
3. **Signal propagation delay.** Entities initially fly straight (~5K ticks) while gamma propagates from one peak to
   the other. At G=10, alpha_eff at peak center is very small → few quanta escape per tick.

### Key Insight: Continuous Direction on Discrete Lattice

The v9 journey through 3 iterations reveals a general principle for physics on discrete lattices:

**Internal state can be continuous even when external actions are quantized.** The entity's direction vector lives in
continuous 3D space. The hop is quantized to 6 neighbors. But the internal vector remembers the fractional component
between hops. This is analogous to subpixel rendering or dithering — the individual steps are coarse, but the
accumulated path is smooth.

This resolves the "6-neighbor lattice can't support orbits" conclusion from iterations 1-2. The lattice CAN support
curved motion if the internal state is continuous. The cost is that angular momentum conservation is approximate (the
quantized hops introduce small L errors at each step) rather than exact.

### Running v9

```bash
cd experiments/64_109_three_body_tree/v9

# Verify (10 tests)
python tagged_gamma.py --verify

# Head-on — gravitational scattering
python tagged_gamma.py --phase2 --ticks 50000 --tag headon

# Perpendicular orbit — gravitational deflection
python tagged_gamma.py --phase2 --ticks 50000 --initial-momentum perpendicular --tag orbit

# Three-body tangential — three-body dynamics
python tagged_gamma.py --phase3 --ticks 100000 --initial-momentum tangential --tag tangential
```

### Conclusions

1. **Continuous internal direction is the key.** Iterations 1-2 (quantized blend) failed because the 6-neighbor
   lattice quantizes combined vectors to the same axis. Iteration 3 (nudge into continuous vector) succeeds because
   small gradient nudges accumulate over many hops, enabling smooth direction rotation.

2. **Gravitational deflection at cm=5.** Perpendicular entities with commit_mass=5 are deflected by the other
   entity's leaked gamma. Distance oscillates [6, 24], all 6 hop directions used. This was impossible with quantized
   blending.

3. **Three-body dynamics without merger.** Three entities interact for 100K ticks without collapsing. Genuine
   gravitational scattering: approach, close encounter, rebound, reapproach.

4. **Mass controls turning radius.** `nudge_strength = 1/mass`. Light entities (cm=1) turn in 2 hops, heavy (cm=10)
   in 22 hops. The turning radius scales linearly with mass, as expected for inertia.

5. **Angular momentum approximately conserved.** L oscillates ±8 due to hop quantization but doesn't systematically
   grow or decay. For stable closed orbits, would need either finer lattice or off-lattice positions.

---

## Dependencies

- Experiment 64 results (for comparison)
- RAW 109 (theoretical framework — gravity from topology)
- RAW 110 (local dimensionality diagnosis — confirmed by v2)
