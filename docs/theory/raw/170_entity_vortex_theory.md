# RAW 170: Entity-Vortex Theory — Unified Physics from Graph Dynamics

**Author:** Tom
**Date:** February 2026
**Status:** Working document — consolidation of 21 derived results
**Prerequisites:** RAW 109, RAW 110, RAW 111, Experiments 64_109 v1–v12

---

## Abstract

This document presents a unified physical theory derived from a single axiom: **entities hop at speed c on an expanding
graph built from {-1, 0, +1}**. From this axiom and one dynamical rule — each entity's forward vector is deflected by
the local density gradient — we derive special relativity, Newtonian gravity, general-relativistic corrections, quantum
mechanics, electromagnetism, the strong and weak forces, particle stability, and cosmology.

The theory was developed through a "math first" approach: working out consequences of the axiom before building
simulations, guided by results from Experiments 64_109 v1–v12. Twenty-one results are presented, classified by rigor
from mathematical derivations (Tier 1) to speculative mappings (Tier 4). Gaps and potential falsifications are honestly
assessed.

---

## Part I: Foundations

### 1.1 The Axiom

The model requires exactly three primitives:

1. **Nodes** — discrete sites. A node either exists or does not.
2. **Edges** — connections between nodes. An edge either exists or does not. Each edge has an integer length.
3. **Entities** — objects that occupy nodes and hop along edges. Each entity has a position, a forward vector, and an
   internal frame.

The fundamental alphabet is **{-1, 0, +1}**:

- +1 = existence
- 0 = non-existence
- -1 = anti-existence

All quantities in the model are integers built from these three values. There are no real numbers, no fractions, no
floating point. The model is a fully deterministic integer cellular automaton.

### 1.2 The Update Rule

Each entity follows one rule per tick:

```
State: position n, forward v ∈ {±x, ±y, ±z}, accumulator a ∈ Z³

Each tick:
  1. a += ∇ρ(n)                                    [density gradient, integer]
  2. if |a_component| ≥ 1: turn, a_component -= sign [Bresenham threshold]
  3. hop 1 edge in forward direction                 [always, every tick]
  4. each edge: length += {0 or 1}                   [expansion, never shrinkage]
```

Where:

- `∇ρ(n)` is the integer density gradient at node n: `∇ρ = Σᵢ (nᵢ - ρ_bg) × d_hat_i / k`
- The Bresenham accumulator provides infinite angular resolution on a discrete lattice — the same principle as sub-pixel
  line drawing
- Edge expansion is `+1` in vacuum, `0` near mass (suppressed by self-gravitation). Never `-1`.

In continuous notation, this is: **v' = normalize(v + ∇ρ)**, then hop to the neighbor closest to v'.

### 1.3 What the Rule Produces

| Environment          | ∇ρ        | Behavior                                        |
|----------------------|-----------|-------------------------------------------------|
| Empty space          | 0         | Straight line (geodesic)                        |
| Near mass            | ∝ M/r²    | Deflection toward mass (gravity)                |
| In orbit             | ⊥ to v    | Circular motion (turning rate = field gradient) |
| Between equal masses | symmetric | Equal deflection (equivalence principle)        |

The speed is always |v| = 1 (one hop per tick). Gravity does not accelerate — it turns. This is geodesic motion, not
Newtonian F=ma.

### 1.4 Definitions

A **vortex** is a collection of N entities rotating on cycles of the graph. A vortex is the model's particle.

| Quantity  | Definition                             | Notes                           |
|-----------|----------------------------------------|---------------------------------|
| Energy    | E = N (entity count)                   | Extensive                       |
| Momentum  | P = Σ vₖ (vector sum of forwards)      | Can be zero even when E > 0     |
| Velocity  | V = P / N                              | Always ≤ c                      |
| Rest mass | m₀² = E² - \|P\|²                      | Invariant                       |
| Charge    | Winding number (chirality of rotation) | Intensive, integer, topological |
| Photon    | N = 1, all forward vectors aligned     | Massless, speed = c             |

---

## Part II: Spacetime

### 2.1 Special Relativity from Vortex Kinematics

**Result 1.** Consider a vortex of N entities, each moving at speed c = 1 with forward vector vₖ where |vₖ| = 1.

Define:

- Total energy: E = N
- Net momentum: P = Σ vₖ
- Net velocity: v = |P| / N
- Rest mass: m₀² = E² - |P|² = N² - |P|²

Three limiting cases:

| Configuration              | \|P\| | v   | m₀       | Physical meaning        |
|----------------------------|-------|-----|----------|-------------------------|
| Uniform rotation (at rest) | 0     | 0   | N        | All energy is rest mass |
| All aligned (beam)         | N     | c   | 0        | Photon (massless)       |
| Biased rotation (moving)   | P < N | P/N | √(N²-P²) | Massive body in motion  |

The standard relativistic relations emerge:

- E² - P² = m₀² (energy-momentum relation)
- γ = 1/√(1-v²) = N/m₀ (Lorentz factor)
- v = P/N < 1 always (speed limit)
- E = γm₀ (relativistic energy)

**Physical interpretation:**

- **Inertia is rotation.** Changing a vortex's velocity means redirecting entity forward vectors. More entities
  rotating → more inertia.
- **Speed limit is structural.** A vortex cannot reach c without losing all rotation — becoming a beam (photon).
  Structure requires rotation; rotation limits speed.
- **E = mc².** Rest energy equals entity count. The energy IS the entities.
- **Kinetic energy** is forward-vector bias: aligning more entities in one direction increases translational momentum at
  the expense of rotational symmetry.

**Rigor: Tier 1** — genuine mathematical identity. Given N unit vectors, E²-P² = m₀² is exact.

### 2.2 Edge Length as Metric Tensor

**Result 3.** Each tick, expansion lengthens all edges. Near mass, self-gravitation resists expansion — edges stay
shorter.

The result is position-dependent edge length: the metric tensor.

- Entity always moves 1 hop/tick (speed = c in local coordinates)
- Physical distance per hop = edge length (varies with position)
- Near mass: shorter edges → less physical distance per hop → effective speed < c
- Far from mass: longer edges → more physical distance per hop → effective speed → c

This gives gravitational time dilation:

```
dt_proper / dt_coordinate = e_local / e_far
```

Matches the Schwarzschild metric: g₀₀ = (1 - 2GM/rc²).

Spatial curvature also emerges: more hops needed to cross the same physical distance near mass → radial stretching → the
g_rr component.

### 2.3 Energy Conservation in Comoving Frame

**Result 5.** From the tick-frame axiom (Doc 49): energy is a function of time (linear). Each tick, each entity gains +1
energy. Each tick, each edge grows by +1 length. These are the **same mechanism**.

The math:

- Entity energy at tick t: E(t) = E₀ + t
- Edge length at tick t: e(t) = e₀ + t
- Relative energy: E(t)/e(t) = (E₀ + t)/(e₀ + t)

If E₀ = e₀: the ratio is exactly 1 at all times — **perfect conservation**.
If E₀ ≠ e₀: the ratio → 1 as t → ∞ — **asymptotic conservation**.

Energy "non-conservation" was an artifact of absolute coordinates. In comoving coordinates, energy IS conserved. There
is no dark energy being pumped in — time passes, everything scales together. The entity doesn't get richer; the ruler
grows at the same rate.

**Analogy:** A photon doesn't "lose energy" in comoving coordinates — the observer's ruler expanded (cosmological
redshift). Here, the entity doesn't "gain energy" in comoving coordinates — the edge length expanded by the same amount.

Cosmological quantities:

- Scale factor: a(t) ∝ e₀ + t (linear growth)
- Hubble parameter: H(t) = 1/(e₀ + t) → decreasing with time
- Hubble's law: v = H × d (recession velocity proportional to distance)

**Rigor: Tier 1** — simple ratio argument. E/e = const is exact when E₀ = e₀.

### 2.4 The Metric from Expansion vs Gravity

**Result 6.** Edge growth equation:

```
de/dt = 1 / (1 + α × M/r)
```

This is always ≥ 0. Edges can **never shrink** — only grow slower near mass.

**Critical constraint:** In an ever-expanding universe, de/dt ≥ 0 always. "Gravity" is differential expansion, not
contraction. Edges near mass grow slower; edges far from mass grow faster. The result looks like attraction, but nothing
contracts.

**Consequences:**

1. **Speed limit from expansion.** v = 0: edges grow equally in all directions. v = c: forward edges don't grow at all.
   v > c: would require edges to shrink → impossible → hard speed limit.

2. **No singularities.** de/dt → 0 as r → 0, never negative. Edges freeze but never collapse. Event horizon = expansion
   fully suppressed so ripples can't propagate outward. No Schwarzschild singularity. No information loss. Just
   ultra-slow expansion.

3. **Equivalence principle.** All objects experience the same local expansion rate regardless of mass. Free fall =
   carried by local expansion. No force applied.

4. **Match with Schwarzschild** (weak field, r >> αM):
    - Model: e(r)/e_∞ ≈ 1 - αM/r
    - Schwarzschild: √(1 - r_S/r) ≈ 1 - r_S/(2r)
    - Match: αM = r_S/2 = GM/c²

5. **Energy conservation with position.** E/e = const through TIME (Result 5). E/e varies with POSITION: E/e(r) = 1 +
   αM/r → gravitational potential energy.

6. **v10's 1/r^2.2 explained.** The nonlinear expansion suppression near mass steepens the profile beyond 1/r². This is
   not a numerical bug — it is the entity-level origin of general-relativistic corrections.

**Rigor: Tier 2** — physically motivated equation with correct limits and Schwarzschild match.

---

## Part III: Gravity

### 3.1 Newton's 1/r² from 3D Diffusion

**Result 2.** Why does gravity follow an inverse-square law?

Direct 1D connectors (entity chains) between two bodies give either distance-independent force (δ constant) or
exponential/Yukawa decay (δ decays along chain). Neither gives 1/r².

But entities connected through a **3D graph** via local connections produce 1/r² naturally. The connection strength
between distant nodes equals the sum over all paths through the network — this is steady-state diffusion on a 3D graph:

- Potential: Φ(r) ∝ 1/r (3D Green's function for the Laplace equation)
- Force: F = -∇Φ ∝ 1/r²

This is Gauss's law: any source in 3D gives 1/r² because the flux through a surrounding sphere is constant regardless of
the sphere's radius.

**Rigor: Tier 1** — standard mathematics. The 3D Green's function is textbook.

### 3.2 Connectors Are Ripple Propagation

**Result 7.** A "connector" between two vortices is not a chain of entities, not a physical cable, and not a direct
long-range link. It is the steady-state ripple pattern from entity hops propagating through the 3D graph.

The mechanism:

1. Entity in vortex A hops → creates a disturbance (ripple)
2. Ripple propagates hop-by-hop through the graph at c
3. At distance r: ripple amplitude ∝ N_A/r (3D diffusion)
4. Ripple gradient ∝ N_A/r² → deflects forward vectors of entities in distant vortex B

**Equivalence principle (emergent):**

- Each entity in vortex B is deflected by A's ripple gradient = N_A/r²
- Deflection per entity depends ONLY on source mass N_A → mass-independent acceleration
- This IS the weak equivalence principle

**Newton's third law (emergent):**

- Force on B = N_B × (N_A/r²) = N_A·N_B/r²
- Force on A = N_A × (N_B/r²) = N_A·N_B/r²
- Equal and opposite: F = N_A·N_B/r²

The gamma field from experiments v10/v11, the connector network, and the ripple intensity are three names for the same
thing: 3D diffusion of entity hop disturbances.

**Rigor: Tier 2** — correct physics, but "ripple" is not yet formally defined at entity level.

### 3.3 Gravity Propagates at c

**Result 8.** Ripples propagate at 1 hop/tick = c. Gravity is ripples. Therefore gravity propagates at c.

Consequences:

1. **Retarded potential:** Φ(r,t) = N_A / |r - r_A(t - r/c)| — the field reflects the source's past position
2. **Gravitational waves:** accelerating source → changing ripple pattern → wave propagating at c
3. **Quadrupole radiation:** monopole is conserved, dipole is conserved for bound systems, quadrupole is the first
   radiating multipole (same as GR)
4. **c_gravity = c_light:** both are ripples on the same graph at the same hop speed — this identity is structural, not
   coincidental (confirmed by LIGO/Virgo 2017: GW170817 + GRB 170817A arrived within 1.7 seconds over 130 million
   light-years)
5. **Gravitomagnetic effects:** retarded field of a moving source → frame dragging emerges
6. **Causal horizon:** gravity reaches ct edges → particle horizon → observable universe boundary

**Rigor: Tier 2** — correct qualitative physics, quantitative predictions not yet computed.

### 3.4 F = ma from Atomic Commit

**Result 21.** A vortex of N entities must complete a full internal rotation before its state is well-defined. The cycle
circumference is proportional to N, so the rotation period — the **commit time** — is N ticks.

This is the atomic commit: the vortex reads its environment, processes internally for N ticks, then updates its
macroscopic state.

**F = ma emerges from commit timing:**

- The density gradient ∇ρ pushes each entity each tick
- But the vortex only "responds" (changes macroscopic direction) once per commit cycle
- Acceleration per entity: a = ∇ρ → independent of N → equivalence principle
- Total force: F = N × ∇ρ, mass m = N → F = ma

**Time dilation from mass:**

- More massive vortex → longer commit cycle → slower internal clock
- Near mass: shorter edges → physically slower rotation → additional gravitational time dilation
- Both effects compound: massive objects near other massive objects tick slowest

**Quantum uncertainty from incomplete commits:**

- Between commits, the vortex state is undefined (entities mid-rotation)
- Position and momentum fluctuate during the commit window
- ΔxΔp ≥ 1 emerges from the rotation, not from observer limitation
- Uncertainty IS the rotation

**Rigor: Tier 2** — physically motivated, correctly produces F=ma, but commit mechanism not yet simulated.

---

## Part IV: Quantum Mechanics

### 4.1 Path Integral from Graph Paths

**Result 11.** Quantum mechanics requires multiple paths between nodes, which means cycles in the graph. A tree graph
has exactly one path between any two nodes → classical behavior. A 3D graph with cycles has many paths → quantum
behavior.

This means quantum mechanics and gravity emerge at the **same transition**: from acyclic tree to cyclic 3D graph.

Path integral on the graph:

```
Amplitude at node B = Σ_paths Aₚ × exp(i × Δθ × Lₚ)
```

Phase = forward vector rotation angle × path length. This is the graph version of the Feynman path integral.

What's quantum about this:

1. **Interference:** multiple graph paths → amplitudes add with phases → constructive/destructive
2. **Uncertainty:** ΔxΔp ≥ ½ from the discrete Fourier transform on a finite graph (a mathematical identity, not a
   physical postulate)
3. **Quantized energy:** integer entities on finite cycles → discrete spectrum
4. **Measurement = decoherence:** interaction with external entities randomizes phase → interference vanishes
5. **Entanglement:** correlated forward vectors from parent entity split (no FTL signaling — correlation only, mediated
   by shared graph edge)
6. **Double slit:** two graph paths with different lengths → path length difference → fringe pattern

**The profound connection:** Gravity, quantum mechanics, and massive particles ALL require 3D cyclic graph topology. All
are absent during the tree phase (inflation). All emerge together when the tree crosslinks into a 3D graph.

**Rigor: Tier 3** — correct conceptual mapping, but forward vector rotation ≠ wave function phase is not proven. The
QM-graph connection is suggestive, not derived.

### 4.2 Spin and Pauli Exclusion

**Result 15.** An entity's complete state is: position + forward vector + frame (±1).

The frame is a binary internal degree of freedom. This gives spin-1/2 naturally: two states (up/down) per entity.

**Pauli exclusion = entity uniqueness:**

- Two entities with identical state (position + forward + frame) ARE the same entity
- You cannot duplicate an entity — at most 2 per (position, forward) pair (one per frame value)
- This is not a force. It is a logical impossibility.

**Fermions vs bosons:**

- Fermion: individual entity with frame DOF → exchanging two entities flips frame → phase factor -1
- Boson: collective ripple (no frame coupling) → no exchange constraint → phase factor +1

The same frame degree of freedom gives BOTH spin-1/2 AND antisymmetric exchange. The spin-statistics theorem is not
something to prove — it is built into the entity structure.

**Composites:** Odd number of fermion entities → fermion. Even → boson. Matches observation.

**Rigor: Tier 3** — the frame DOF is added by hand, not derived from the axiom. The mapping to spin-statistics is
plausible but not rigorous.

---

## Part V: Forces

### 5.1 Electromagnetism from Vector Ripples

**Result 12.** An entity hop creates two types of disturbance:

| Mode   | Information carried                             | Sign                    | Force            |
|--------|-------------------------------------------------|-------------------------|------------------|
| Scalar | "An entity was here" (density, always positive) | Always attractive       | Gravity          |
| Vector | "Going this direction" (forward vector, signed) | Attractive or repulsive | Electromagnetism |

**Mediators:**

- Gravity: collective diffusion through the background entity sea (no graviton particle needed)
- EM: photon exchange (free entity with N=1, carrying chirality/polarization information)

**Charge = topological winding number:**

- Mass = N (extensive, entity count) → gravitational coupling
- Charge = winding number (intensive, integer, topological) → electromagnetic coupling
- Charge is quantized, conserved, and has the same magnitude for particles of different mass

**Force signs from chirality:**

- Same chirality (same rotation direction): absorbed photon reinforces rotation → repulsive
- Opposite chirality: absorbed photon cancels rotation → attractive

**Fine structure constant:** α = photon emission probability per tick per charge. In principle computable from graph
properties (vortex balance conditions). The value 1/137 is not yet derived.

**Rigor: Tier 3** — correct conceptual structure, but chirality → EM coupling mechanism is asserted, not derived. No
calculation of α.

### 5.2 Strong Force from Dimensional Reduction

**Result 13.** The key mechanism is confinement from 1D propagation:

- 3D diffusion → potential ∝ 1/r → force ∝ 1/r² (gravity, EM)
- 1D propagation → potential ∝ r → constant force (confinement!)

**Color = rotation plane orientation.** In 3D, there are 3 independent rotation planes → 3 colors. This matches SU(3).

- Color-neutral (isotropic over all 3 planes): ripple spreads in 3D → free particle
- Single color (anisotropic, one plane): ripple confined to 1D channel → confined

**Asymptotic freedom:** At short distance, the graph is locally symmetric → no preferred direction → no confinement. At
long distance, the graph imposes directionality → confinement grows with distance.

**String breaking:** Flux tube energy is proportional to length. When E_tube > 2 × m_quark → pair creation from the
vacuum → tube breaks into two shorter tubes (hadronization).

**Complete force hierarchy from one mechanism:**

| Force   | Ripple type        | Propagation | Potential | Mediator               |
|---------|--------------------|-------------|-----------|------------------------|
| Gravity | Scalar (density)   | 3D          | 1/r       | Collective diffusion   |
| EM      | Vector (direction) | 3D          | 1/r       | Photon (N=1 entity)    |
| Strong  | Tensor (plane)     | 1D confined | r         | Gluon (color-carrying) |

**Rigor: Tier 4** — interesting picture, but the 1D confinement mechanism is not specified. Why does rotation-plane
information propagate in 1D? This needs concrete derivation.

### 5.3 Weak Force from Massive Mediator Exchange

**Result 14.** The W and Z bosons are small vortices (N_W >> 1 entities) exchanged between particles. Their range is
proportional to 1/N_W (Yukawa potential). The force is short-range because creating the mediator vortex costs energy.

**Symmetry breaking = graph cooling:**

- Hot graph: all rotation planes are equivalent → 4 equivalent massless gauge bosons
- Cool graph: a preferred orientation freezes out → 3 modes acquire mass (W±, Z), 1 stays massless (photon)
- The Higgs field corresponds to the graph's local rotation-plane anisotropy

**Parity violation:**

- Left-handed: rotation opposes translation → specific graph paths available for W emission
- Right-handed: those paths are blocked → no weak coupling
- Parity violation is geometric, not mysterious

**Flavor change:** Different particle flavors correspond to different vortex cycle topologies. W exchange rearranges the
cycle structure → flavor change (as in beta decay).

**Electroweak unification:** At high energy, all modes are equivalent (SU(2)×U(1) symmetry). At low energy, symmetry
breaks → EM and weak separate.

**Rigor: Tier 4** — speculative mapping. The vortex exchange mechanism is not specified. No quantitative predictions.

---

## Part VI: Particles

### 6.1 Vortex Stability

**Result 4.** A vortex is N entities rotating on graph cycles. Stability comes from the balance of:

- **Self-gravity** (through the ripple network) pulling entities inward
- **Angular momentum** (rotation) providing centripetal support

Each entity moves 1 hop/tick, but physical velocity varies with position because of variable edge lengths:

```
v_physical(r) = c × e(r) / e_far
```

Near the vortex center, edges are shorter (expansion resisted by self-gravitation), so v_physical << c even though hop
speed = c.

**Consequences:**

- Inner entities: slow physical orbits, tightly bound
- Outer entities: faster orbits, loosely bound
- Outermost boundary where v_physical = c: this is the Schwarzschild radius
- The vortex structure IS a gravitational well, described by the edge-length metric

Vortex stability and orbital stability (e.g. planetary orbits) are the SAME physics: gravity vs angular momentum,
modulated by the metric.

### 6.2 Minimum Vortex Size

**Result 9.** Graph discreteness sets a mass floor for stable particles.

- N = 1: straight line, no rotation → photon (massless)
- N = 2: orbit radius R = 1/2 < 1 edge → impossible on any graph
- N = 3: equilateral triangle with side L = 1 → marginally possible on k ≥ 12 graphs

Variable edge lengths (Result 6) help: edge suppression near mass reduces physical velocity, allowing even 3 entities to
form a bound state at sub-edge physical radius.

The minimum vortex size depends on graph connectivity:

- k = 6 (cubic): minimum cycle length = 4, so N_min ≥ 4
- k ≥ 12 (FCC/triangular): minimum cycle length = 3, so N_min ≥ 3

N = N_min → the lightest massive particle.

### 6.3 Chirality and Charge

Vortex rotation has exactly two directions on any cycle: clockwise and counterclockwise.

- CW → particle, CCW → antiparticle (or vice versa)
- Charge is quantized to ±1 (two directions only)
- Annihilation: CW + CCW → unwinding → photons (entities released as N=1 beams, no rotation)
- CP symmetry: spatial reflection swaps chirality

### 6.4 Dark Matter as Chirality-Neutral Vortices

**Result 19.** A vortex with equal numbers of CW and CCW entities has:

- Net charge Q = 0 (chirality cancels)
- Mass M = N (entity count, always positive)
- Gravitational interaction: yes (mass > 0)
- Electromagnetic interaction: no (charge = 0, no photon emission/absorption)

These Q = 0 vortices are **dark matter**:

- They interact gravitationally but not electromagnetically
- They cannot emit photons → no energy dissipation → cannot cool → remain diffuse
- This matches observed dark matter distribution (extended halos, not disks)

**Abundance:** Symmetric crosslinking during graph formation produces most vortices with Q = 0. A small chirality
asymmetry (from tree branching bias) gives a small fraction with Q ≠ 0 → visible matter. The ~85% dark matter / ~15%
visible matter ratio follows from symmetric statistics with small bias.

**Self-interaction:** The internal CW/CCW spatial separation gives a quadrupole moment → short-range self-interaction (
consistent with SIDM constraints).

**Rigor: Tier 3** — plausible mechanism, but no quantitative prediction of the 85/15 ratio. The link between
crosslinking statistics and observed dark matter fraction is not derived.

---

## Part VII: Cosmology

### 7.1 Big Bang from a Single Node

**Result 10.** The universe begins as a single node with a single entity and zero energy. No edges, no space.

Each tick, the entity gains +1 energy. At threshold: it splits → new node + new edge. At tick t: k^t entities → the
graph is a k-ary tree (no cycles, no 3D structure).

### 7.2 Inflation as the Tree Phase

During tree growth:

- No cycles → no rotation → no vortices → no massive particles → no gravity
- Only photon-like entities (straight-line propagation along branches)
- Expansion is exponential (k^t nodes per tick)

This is inflation: exponential expansion of a causally connected region, with no massive particles and no gravitational
structure.

### 7.3 Reheating as Crosslinking

When branch tips reach sufficient density, they form crosslink edges → cycles appear → 3D topology emerges → vortices
can form → gravity turns on.

- Dimensionality from branching factor: k-ary tree + crosslinks → (k-1)D space
- k = 4 → 3D space + 1D time (tree depth as temporal dimension)
- This explains 3+1 dimensions as a consequence of the branching factor

Phase transition (inflation → matter era):

- Exponential expansion → linear (edge growth only, no new nodes)
- Tree kinetic energy → vortex rotation + gravitational binding (reheating)
- Gravity activates when Gauss's law applies (closed surfaces from crosslinks)

**Consistency with experiments:**

- Doc 50: time ≠ spatial dimension → confirmed (tree depth ≠ crosslinked dimension)
- Doc 15-01: stable substrates at 4D-5D → branching factor k = 4-5

### 7.4 Cosmological Predictions

**Result 16.** Accelerating expansion without dark energy.

Result 6 gives the edge growth equation: `de/dt = 1/(1 + αρ)` where ρ is average density. As the universe expands,
matter dilutes: ρ ∝ 1/a³. Substituting:

```
ȧ = da/dt = 1/(1 + β/a³)    where β = αρ₀a₀³
```

- Early (dense, a small): β/a³ >> 1, so ȧ ≈ a³/β → slow, gravitationally suppressed
- Late (dilute, a large): β/a³ → 0, so ȧ → 1 → approaches linear (coasting limit)

The acceleration is:

```
ä = 3β / [a⁴(1 + β/a³)³]
```

This is **always positive**. The expansion always accelerates because matter is always diluting, always releasing the
gravitational suppression. No dark energy, no cosmological constant — just gravity weakening as mass thins out.

The deceleration parameter, with u = β/a³:

```
q = -aä/ȧ² = -3u/(1+u)
```

- Early (dense, u → ∞): q → -3 (strong acceleration)
- Late (dilute, u → 0): q → 0 (approaching coasting)
- **q is always negative — always accelerating**

**Match with observation:** For q₀ = -0.55, solve 3u/(1+u) = 0.55 → u₀ ≈ 0.224. This means current gravitational
suppression is ~18% of the expansion drive — entirely reasonable for the observed matter density.

In ΛCDM, accelerating expansion requires dark energy (Ω_Λ ≈ 0.7). In this model, acceleration is the natural
consequence of Result 6: gravity suppresses expansion, matter dilutes, suppression weakens, expansion speeds up.
The same equation that gives Schwarzschild in the local limit gives accelerating cosmology in the global limit.

**Expansion history:**

| Era | Mechanism | Expansion |
|---|---|---|
| Tree phase | Node splitting | Exponential (inflation) |
| Post-crosslinking (dense) | Edge growth, heavily suppressed | Slow, accelerating |
| Current epoch | Edge growth, moderate suppression | Accelerating (q₀ ≈ -0.55) |
| Far future | Edge growth, negligible suppression | Approaching linear (q → 0) |

Standard cosmological problems resolved differently from standard inflation:

- **Horizon problem:** All branches share a common ancestor node → causal contact established before tree phase ends
- **Flatness problem:** 3D graph is locally flat by construction (regular connectivity)
- **CMB anisotropies:** From tree branching pattern, not inflationary quantum fluctuations

**Matter/antimatter asymmetry:** Tree branching chirality → biased crosslinking → matter dominance. The same chirality
mechanism as weak force parity violation → unified origin.

**Hubble tension:** The model has a different expansion history from ΛCDM. Fitting early-universe data (CMB) vs
late-universe data (distance ladder) with different assumed expansion histories yields different H₀. The Hubble tension
may be an artifact of assuming ΛCDM when the actual expansion law is ȧ = 1/(1 + β/a³).

**No singularities:** Edges never shrink → no Big Bang singularity, no black hole singularities. Information is
preserved in ultra-slowly-expanding interior regions.

**Rigor: Tier 2** — the derivation follows directly from Result 6 applied to homogeneous cosmology. The q₀ formula is
exact given the edge growth equation. The match with q₀ ≈ -0.55 is achievable with one free parameter (β).

### 7.5 Thermodynamics from Expansion

**Result 17.** The second law of thermodynamics is expansion.

Phase space grows because the graph grows: Ω(t+1) > Ω(t) always. No statistical arguments needed — it is a structural
fact about an expanding graph.

- **S(0) = 0** is a logical necessity: 1 entity on 1 node → Ω = 1 → S = ln(1) = 0. Not a boundary condition to be
  imposed.
- **Arrow of time** = tick direction = expansion direction. Ticks increment, edges grow, entities increase, phase space
  expands. Four descriptions of one process. Irreversible by construction.
- **Temperature:** T = random component of entity velocities. Cooling: T ∝ 1/(e₀ + t) (dilution by expansion).
- **No heat death:** Phase space grows forever → entropy never saturates. The universe is ever-expanding, ever-cooling,
  never in equilibrium.

**Rigor: Tier 2** — the connection between expansion and entropy is sound. S(0) = 0 is exact.

### 7.6 Holographic Principle from Graph Boundaries

**Result 18.** The Bekenstein-Hawking entropy S_BH = A/4 is a bandwidth limit, not a storage limit.

The interior of a region has a volume's worth of microstates, but information must pass through the boundary to reach an
external observer. Throughput is proportional to boundary area → accessible entropy S ∝ A. This is a communication
bottleneck, not a fundamental limit on interior information.

**Hawking radiation:** Edges at the horizon grow slowly (de/dt > 0 always, by the no-shrinkage constraint). Entities
leak out on these slowly growing edges → radiation temperature T ∝ escape rate ∝ 1/M.

**Information paradox resolved:** No singularity (edges never reach zero length) → no information destruction. Entity
states are preserved in the slowly-expanding interior. The evolution is deterministic throughout. Evaporation gradually
releases all information → unitarity preserved.

**Rigor: Tier 3** — the bandwidth argument is sound in principle. The detailed calculation of S = A/4 from graph
properties is not performed.

---

## Part VIII: Critical Assessment

### 8.1 Tier Classification

**Tier 1 — Mathematical derivation (solid):**

- Result 1: SR from vortex kinematics (E² - P² = m₀² is exact for N unit vectors)
- Result 2: 1/r² from 3D diffusion (standard Green's function)
- Result 5: E/e = const (simple ratio, exact when E₀ = e₀)

**Tier 2 — Physically motivated with correct limits:**

- Result 3: Edge length as metric (matches Schwarzschild in weak field)
- Result 6: de/dt = 1/(1+αM/r) (correct limits, no shrinkage, matches v10)
- Result 7: Connectors as ripple propagation (produces equivalence principle and Newton III)
- Result 8: Gravity at c (correct qualitative physics)
- Result 17: Entropy from expansion (S(0) = 0 exact, second law structural)
- Result 20/20b: Local update rule (produces correct classical behavior)
- Result 21: Atomic commit / F=ma (correctly derives Newton's second law)
- Result 16: Cosmological predictions (q = -3u/(1+u) follows directly from Result 6, matches q₀ ≈ -0.55)

**Tier 3 — Plausible mapping, incomplete derivation:**

- Result 4: Vortex stability (correct balance, not quantitatively solved)
- Result 9: Minimum vortex (correct constraint, connectivity dependence unclear)
- Result 10: Big Bang from single node (consistent, but branching factor undetermined)
- Result 11: QM from path integral (correct structure, phase ≠ proven)
- Result 12: EM from vector ripples (correct mode structure, coupling not derived)
- Result 15: Spin from frame DOF (correct statistics, frame DOF is ad hoc)
- Result 18: Holographic principle (correct argument, A/4 not computed)
- Result 19: Dark matter (plausible, abundance not derived)

**Tier 4 — Speculative (interesting picture, minimal derivation):**

- Result 13: Strong force from 1D confinement (mechanism unspecified)
- Result 14: Weak force from massive mediator (mechanism unspecified)

### 8.2 Critical Gaps

**Must resolve before the theory is testable:**

1. **QM phase not derived.** Forward vector rotation angle is proposed as the quantum phase, but the identification is
   not proven. Without this, the path integral (Result 11) is a metaphor, not a derivation.
2. **Graph structure unspecified.** The branching factor k, crosslinking criteria, and detailed 3D topology are not
   determined. The theory works "for some graph" but doesn't specify which one.

**Major gaps:**

3. **Frame DOF is ad hoc.** The binary internal state (±1) giving spin-1/2 is put in by hand, not derived from the
   axiom. This is the weakest part of the fermion story.
4. **Chirality = charge is asserted.** No mechanism is provided for why rotation direction couples to vector ripples (
   photons). This is the weakest part of the EM story.
5. **Strong and weak force mechanisms are unspecified.** The dimensional reduction argument (Result 13) and the vortex
   exchange argument (Result 14) are conceptual pictures without dynamical equations.
6. **Fine structure constant not computed.** The theory claims α is "in principle computable from graph properties" but
   does not compute it.

### 8.3 Potential Falsification

1. **q₀ value.** The model predicts q = -3u/(1+u) where u = β/a³. The current value q₀ ≈ -0.55 is achievable, but the
   model also predicts q was more negative in the past (stronger acceleration when denser) and approaches 0 in the
   future. If observations show q was ever positive (decelerating expansion), the model needs modification. ΛCDM
   predicts a deceleration-to-acceleration transition at z ≈ 0.7 — if this transition is confirmed independently of the
   ΛCDM framework, it would challenge this model.
2. **No graviton.** The theory predicts gravity is collective diffusion, not particle exchange. If a graviton is ever
   detected, the theory is falsified.
3. **Exact conservation laws.** The theory predicts approximate conservation (from integer statistics on a finite
   graph). If exact conservation laws are demonstrated to hold at the Planck scale, the theory is wrong.

### 8.4 What's Genuinely Strong

1. **One axiom.** Everything flows from "entities hop at c on an expanding graph." There is no second law.
2. **Integer arithmetic only.** No real numbers, no renormalization, no infinities. The model is a deterministic
   cellular automaton.
3. **SR is exact.** E²-P² = m₀² is not an approximation. It is a mathematical identity for N unit vectors.
4. **No singularities.** The no-shrinkage constraint (de/dt ≥ 0) eliminates all singularities — Big Bang, black holes,
   point particles — without any additional assumptions.
5. **Gravity and QM unified.** Both emerge at the same phase transition (tree → cyclic graph). They are not separate
   theories that need reconciliation — they are two aspects of graph cyclicity.
6. **Accelerating expansion without dark energy.** The observed q₀ ≈ -0.55 follows directly from the edge growth
   equation applied to a diluting universe. No cosmological constant, no new physics — just gravity weakening as matter
   thins out.
7. **Dark matter explained.** Q = 0 vortices are a natural prediction, not an add-on.
8. **Force hierarchy from one mechanism.** Scalar/vector/tensor ripples in 3D/1D give gravity/EM/strong, all from entity
   hops.

### 8.5 Open Questions

1. What determines the graph's branching factor k? (This sets the number of spatial dimensions.)
2. What are the crosslinking rules? (This determines the detailed 3D structure.)
3. Can the fine structure constant α = 1/137 be computed from graph properties?
4. Does the Bresenham accumulator reproduce known QM experiments (double slit, Stern-Gerlach) in simulation?
5. Can the theory predict particle masses (ratios of N_min for different cycle topologies)?
6. Is the frame DOF derivable from the axiom, or is it an independent postulate?
7. Can the 85/15 dark/visible matter ratio be computed from crosslinking statistics?

---

## Summary

One axiom: **entities hop at c = 1 on an expanding graph built from {-1, 0, +1}**.

One rule: **v' = normalize(v + ∇ρ)**, implemented as an integer Bresenham accumulator.

One constraint: **edges never shrink** (de/dt ≥ 0 always).

From these:

- Special relativity emerges from the kinematics of N unit-speed entities (exact)
- Gravity emerges from 3D diffusion (Gauss's law, 1/r²)
- General relativity emerges from variable edge lengths (expansion vs self-gravitation)
- Quantum mechanics emerges from path interference on cyclic graphs
- Electromagnetism emerges from vector ripple modes
- Particles are vortices (stable rotating entity configurations)
- The strong force emerges from dimensional reduction (1D confinement)
- Dark matter is chirality-neutral vortices
- The Big Bang is a single node splitting into a tree, then crosslinking into 3D
- Accelerating expansion emerges from matter dilution — no dark energy needed (q₀ ≈ -0.55 matches observation)
- Entropy increases because the graph expands
- There are no singularities, anywhere, ever

The theory has genuine mathematical content (Tier 1-2 results), plausible extensions (Tier 3), and speculative
mappings (Tier 4). The accelerating expansion prediction — derived from the same edge growth equation that gives
Schwarzschild locally — matches the observed q₀ ≈ -0.55 without a cosmological constant.

---

## References

- RAW 049 — Temporal Ontology of the Tick-Frame Universe
- RAW 050 — Dimensional Equivalence Rejection (time ≠ spatial dimension)
- RAW 109 — Speed of light and isotropy from graph topology
- RAW 110 — Local dimensionality as critical variable for orbital mechanics
- RAW 111 — Space is connections
- RAW 120 — Open questions and experimental status
- Experiment 64_109 v1–v9 — Three-body dynamics on graph substrate
- Experiment 64_109 v10 — Macro-scale orbits with gravitational time dilation
- Experiment 64_109 v11 — Random geometric graph with self-gravitation
- Experiment 64_109 v12 — Reference Newtonian orbits with connectors and expansion
