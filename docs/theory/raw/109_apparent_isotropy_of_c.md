# RAW 109 — The Apparent Isotropy of c on a Discrete Substrate

*Why the speed of light measures the same in all directions even if spacetime is a lattice*

---

## 0. Abstract

In the tick-frame universe, the speed of light is structurally fixed at one cell per tick. On any regular lattice, this produces direction-dependent spatial propagation: diagonal paths traverse geometrically longer distances per tick than cardinal paths. Yet every laboratory measurement of c returns the same value in all directions. This document demonstrates that this is not evidence against a discrete substrate but a necessary consequence of it. The measuring apparatus co-deforms with the substrate, making the anisotropy self-cancelling at measurement scale. The anisotropy becomes detectable only statistically, at extreme energies, over cosmological distances — exactly matching the Beane prediction for cosmic ray distributions. The angular momentum non-conservation observed in Experiment 64 is identified as a direct simulation-scale manifestation of this lattice anisotropy.

---

## 1. The Structural Speed Limit

### 1.1 Definition

In the tick-frame substrate:

$$c = \frac{1 \text{ cell}}{1 \text{ tick}}$$

This is not a measured value. It is a structural constraint: information propagates at most one cell per tick. It follows from Axiom 2 (Causality) and Axiom 3 (Granularity) as established in Ch7 §2.

### 1.2 Isotropy in Ticks

The constraint is perfectly isotropic in tick-space. One tick buys one cell of propagation. This holds regardless of direction. The substrate makes no distinction between cardinal and diagonal — the rule is one step per tick, period.

### 1.3 Anisotropy in Space

On a cubic lattice, "one cell" has different spatial extent depending on direction:

| Direction | Neighbors | Spatial distance per cell |
|-----------|-----------|--------------------------|
| Cardinal (±x, ±y, ±z) | 6 | 1.000 |
| Edge diagonal (±xy, ±xz, ±yz) | 12 | √2 ≈ 1.414 |
| Body diagonal (±xyz) | 8 | √3 ≈ 1.732 |

A signal propagating along a body diagonal covers 73% more spatial distance per tick than one along a cardinal axis. The tick-rate is identical. The spatial rate is not.

---

## 2. Why Michelson-Morley Finds Nothing

### 2.1 The Co-Deformation Principle

The measuring apparatus — interferometer arms, mirrors, beam splitters, detectors — is made of atoms. Atoms are processes. Processes are patterns deposited in the gamma field. The gamma field lives on the lattice. Therefore:

> **The ruler is made of the same lattice as the thing being measured.**

If light propagates 1.0 spatial units along X per tick but 1.414 spatial units along XY per tick, the interferometer arm oriented along XY is also 1.414 lattice units long per physical unit of its construction. The arm and the light co-deform. The ratio — which is all the interferometer measures — is always 1.

### 2.2 Formal Statement

Let $d_\theta$ be the spatial distance covered by light per tick in direction $\theta$, and let $L_\theta$ be the physical length of a measuring rod oriented in direction $\theta$. Both are constructed from lattice geometry:

$$d_\theta = f(\theta, \text{lattice}) \quad \text{and} \quad L_\theta = g(\theta, \text{lattice})$$

Since both functions derive from the same lattice metric:

$$\frac{d_\theta}{L_\theta} = \frac{d_\phi}{L_\phi} = c \quad \forall\ \theta, \phi$$

The measured speed of light is direction-independent not because the substrate is isotropic, but because measurement and propagation share the same geometric distortion.

### 2.3 Historical Parallel

This is precisely why Michelson and Morley found no fringe shift in 1887. The standard interpretation: there is no luminiferous aether. The tick-frame interpretation: there IS a substrate, but the instrument cannot detect it because the instrument is made of it. Both interpretations produce identical experimental results. They are empirically indistinguishable at laboratory scale.

---

## 3. Where the Anisotropy Leaks Through

### 3.1 The Beane Prediction (2012)

Beane, Davoudi, and Savage demonstrated that if spacetime is a cubic lattice (analogous to lattice QCD simulations), two observable consequences follow:

1. **Cosmic ray energy cutoff** — matches the observed GZK cutoff
2. **Cosmic ray angular anisotropy** — preferential arrival along lattice axes

The energy cutoff has been observed. The angular anisotropy has not been conclusively detected, which may indicate either:
- The universe is not on a cubic lattice, or
- The lattice is not cubic but uses a more isotropic topology (FCC, network)

### 3.2 Why Extreme Energy Is Required

The co-deformation principle cancels the anisotropy for any measurement conducted within the lattice. To detect the lattice, you need a probe whose wavelength approaches the lattice spacing — i.e., a particle with Planck-scale energy.

Cosmic rays at the GZK cutoff (~10²⁰ eV) have wavelengths approaching the Planck length. At this scale, the discrete structure can no longer hide behind co-deformation. The particle "feels" individual cells. Its trajectory is direction-dependent.

At lower energies — every laboratory experiment ever conducted — the wavelength spans thousands or millions of cells. Statistical averaging over the lattice geometry produces perfect apparent isotropy.

### 3.3 Simulation Evidence: Experiment 64

The three-body gravitational simulation (Experiment 64, 256³ grid, 20,000 ticks) exhibited angular momentum non-conservation:

- Initial L_z: 0.000000
- Final L_z: -974.8
- Range: -5465 to +4591

This is the lattice anisotropy manifesting directly. The simulated entities do NOT have co-deforming rulers. They are point processes moving through a cubic lattice. The 6-neighbor spreading kernel propagates faster along cardinal axes than diagonals. Angular momentum, which requires perfect rotational symmetry, is violated.

In the real universe, this violation would be hidden by co-deformation at laboratory scale but could appear in extreme-energy processes over cosmological distances — exactly as Beane predicted.

---

## 4. Time Dilation as Decision-Tree Depth

### 4.1 The Causal Decision Tree

Each entity, at each tick, traverses a causal decision tree:

1. **Read** the committed field state (gamma gradients, neighbors)
2. **Evaluate** which direction minimizes cost (steepest descent, path of least resistance)
3. **Commit** the chosen move

The number of nodes in this tree depends on the local field complexity.

### 4.2 Flat Space: Shallow Tree

In flat space (uniform gamma, zero gradient), the decision is trivial:
- Few neighbors with significant gradients
- Obvious best direction (or random walk)
- Tree depth: minimal
- Tick completes quickly in subjective terms

### 4.3 Curved Space: Deep Tree

Near a massive body (deep gamma well, steep gradients, many competing influences):
- Many neighbors with strong, competing gradients
- Ambiguous best direction requiring deeper evaluation
- Tree depth: large
- Tick takes longer in subjective terms

This IS time dilation. Not as a stretching of time, but as an increase in computational work per tick. The entity near a massive body processes the same tick as the entity in flat space, but the tick contains more decision work. Its internal clock — counting completed evaluations — runs slower.

### 4.4 Formal Correspondence

The tree depth $D$ at position $x$ is proportional to the local field complexity:

$$D(x) \propto |\nabla \gamma(x)| + \nabla^2 \gamma(x)$$

The subjective tick rate (proper time) is:

$$\frac{d\tau}{dt} \propto \frac{1}{D(x)}$$

In the weak-field limit, this reproduces Schwarzschild time dilation:

$$\frac{d\tau}{dt} = \sqrt{1 - \frac{2GM}{rc^2}}$$

where the gamma well depth plays the role of gravitational potential.

---

## 5. Radiation as Decision Cost

### 5.1 The Branch Cost Principle

At every node in the decision tree, the entity evaluates possible directions. In flat space, evaluation is cheap — one obvious path. In curved space, evaluation is expensive — multiple competing paths.

The energy expended on evaluation does not vanish. It is deposited into the field as radiation.

> **Bremsstrahlung is not friction. It is the cost of making decisions in curved space.**

### 5.2 Why Faster Entities Radiate More

A fast-moving entity in curved space encounters more decision nodes per unit time:
- Higher velocity → more cells traversed per tick
- More cells → more gradient evaluations
- More evaluations → more decision cost
- More cost → more radiation

The radiation scales with velocity because the number of decisions scales with velocity. At v → c, the entity traverses one cell per tick — every single tick requires a gradient evaluation. Decision cost is maximized. Radiation is maximized. This creates the asymptotic barrier: the faster you go, the more energy you lose to decisions, making c unreachable.

### 5.3 Connection to Experiment 64

The Bremsstrahlung drain in Experiment 64 implements this principle:

$$\text{drain} = |\nabla \gamma| \times v^3$$

The cubic velocity dependence reflects the three-dimensional nature of decision complexity. At each cell, the entity must evaluate gradients in all three spatial dimensions. The cost scales as the cube of the traversal rate.

Energy drained from kinetic motion is deposited into the gamma field — exactly as decision cost becomes radiation in the theory.

---

## 6. The Speed of Light as Maximum Traversal Rate

### 6.1 Tree-Theoretic Speed Limit

The maximum number of cells an entity can traverse per tick is bounded by the tree depth available in one tick. Since one tick IS one Planck time, and the tree has finite depth, there exists a maximum traversal rate.

On the lattice: 1 cell per tick along any axis. This is c.

An entity cannot traverse more than one cell per tick because:
1. It must read the committed state of the destination cell
2. The committed state only propagates one cell per tick
3. Therefore the entity cannot "see" beyond one cell ahead
4. Moving two cells in one tick would require information from a cell whose state hasn't propagated yet

This is not a speed limit imposed by fiat. It is a causality limit imposed by the commit propagation rate.

### 6.2 Why c Is the Same for All Observers

Each observer's decision tree is rooted in their local committed state. Their measurement of c is the ratio of cells traversed to ticks elapsed, using rulers and clocks made of the same committed states. The co-deformation principle (§2) guarantees that every observer, regardless of their velocity or position, measures the same ratio.

This reproduces the second postulate of special relativity — the constancy of c for all inertial observers — without invoking Lorentz invariance as a postulate. It emerges from the commit semantics of the substrate.

---

## 7. Lattice Topology and Isotropy

### 7.1 Cubic Lattice Limitations

The cubic lattice (6 face neighbors) has the worst isotropy of any regular space-filling grid:
- 3 distinct neighbor distances (1, √2, √3)
- 3 distinct propagation speeds
- Strong cardinal axis preference

### 7.2 Improved Topologies

| Topology | Equidistant neighbors | Isotropy quality |
|----------|----------------------|------------------|
| Cubic (6-neighbor) | 6 | Poor |
| Cubic (26-neighbor, weighted) | ~26 (weighted) | Moderate |
| BCC | 8 | Good |
| FCC | 12 | Excellent |
| Network (irregular) | Variable | Perfect (statistical) |

FCC provides 12 equidistant neighbors — the most isotropic regular lattice in 3D. An irregular network (as in causal set theory or spin foam models) achieves statistical isotropy at large scales without requiring a regular structure.

### 7.3 Observational Constraints

Saadeh et al. (2016) constrained cosmic anisotropy using Planck CMB data: the odds of an anisotropic universe are 1 in 121,000. Any discrete substrate model must produce anisotropy below this threshold at cosmological scales while permitting it at Planck scale.

The key question: does the anisotropy dilute with scale (as statistical averaging predicts), or persist? If it dilutes, any lattice topology works at sufficient scale. If it persists, only highly isotropic topologies (FCC, irregular network) are viable.

Experiment 64 can test this: run three-body simulations at different scales (128³, 256³, 512³) and measure angular momentum violation as a function of grid size. If violation scales as 1/N (where N is grid size), isotropy emerges at large scale. If it doesn't, the topology is wrong.

---

## 8. Predictions

### 8.1 Testable Within the Simulation Framework

1. **Angular momentum violation should scale with lattice spacing**: Larger grids → smaller violation per unit physics. Test with Experiment 64 at multiple resolutions.

2. **FCC lattice should dramatically reduce angular momentum violation**: Same three-body scenario on FCC grid should show < 10% of cubic grid violation.

3. **26-neighbor weighted kernel should improve cubic grid**: Intermediate improvement between 6-neighbor and FCC.

4. **Orientation-dependent dynamics**: Same three-body scenario rotated 45° relative to lattice axes should show different angular momentum violation pattern.

### 8.2 Testable in the Physical Universe

1. **Cosmic ray anisotropy at GZK energies** (Beane prediction): Statistical preference for arrival along lattice axes. Requires large cosmic ray datasets (Pierre Auger Observatory, Telescope Array).

2. **Gravitational wave speed anisotropy**: Merging black holes in different sky directions should show propagation speed consistent to better than 1 part in 10^15. Any deviation → lattice detection.

3. **Fine-structure constant directional variation**: Webb et al. reported hints of α variation across the sky. If real, this could indicate lattice anisotropy affecting electromagnetic coupling.

---

## 9. Implications

### 9.1 For Special Relativity

The constancy of c is preserved but reinterpreted. It is not a postulate — it is a consequence of co-deformation. Lorentz invariance is emergent, not fundamental. At Planck scale, Lorentz invariance breaks. At laboratory scale, it is exact to all measurable precision.

### 9.2 For the Tick-Frame Model

The lattice anisotropy is not a flaw to be eliminated. It is a prediction to be tested. The model makes the specific claim that rotational symmetry is approximate, not exact, with violations scaling inversely with system size. This is falsifiable.

### 9.3 For the Rendering Engine

The causal cone engine's spreading kernel directly implements the propagation rule. The current 6-neighbor kernel produces visible anisotropy (diamond-shaped wavefronts). Switching to 26-neighbor weighted or FCC kernels will produce nearly spherical wavefronts — matching the observed isotropy of the physical universe at macroscopic scales.

### 9.4 For Consciousness and Decision

If time dilation is tree depth and radiation is decision cost, then:

- **Consciousness** = the process of traversing the decision tree
- **Free will** = the commit at branch points
- **Thought cost** = the radiation emitted by the brain (metabolic heat as Bremsstrahlung)
- **Meditation / flow states** = reduced tree complexity → less decision cost → subjective time speeds up

The brain dissipates ~20W. In the tick-frame interpretation, this is the decision cost of a complex process making ~10^11 neural commits per second in a deeply curved gamma well (Earth's gravitational field).

---

## 10. Conclusion

The speed of light appears constant in all directions not because spacetime is continuous and isotropic, but because the observer's measuring apparatus shares the same discrete geometry as the signal being measured. The anisotropy is real but self-cancelling at measurement scale. It leaks through only at extreme energies (cosmic rays) and in simulations where entities lack co-deforming rulers (Experiment 64).

The deeper insight is that c is not a speed. It is a commit propagation rate. One cell per tick. The maximum rate at which confirmed information can spread through the substrate. Everything else — time dilation, radiation, the relativistic speed limit — is a consequence of this single structural constraint, mediated by the decision-tree complexity of navigation through the gamma field.

---

## References

- **Beane, S.R., Davoudi, Z., Savage, M.J.** (2012). *Constraints on the Universe as a Numerical Simulation.* arXiv:1210.1847
- **Saadeh, D. et al.** (2016). *How Isotropic is the Universe?* Physical Review Letters.
- **Ch7 §2**: Speed of light as lattice constraint.
- **RAW 081**: Photon as degenerate process, field propagation at c.
- **RAW 082**: Gravity as cost gradient in gamma wake.
- **Experiment 64**: Three-body gravitational dynamics, angular momentum non-conservation.
- **Experiment 51 v12**: Special relativistic effects from temporal surfing.

---

*Date: 2026-02-14*
*Status: DRAFT*
*Depends on: Ch7, RAW 081, RAW 082, Experiment 64*
*Validates: Co-deformation principle, decision-tree time dilation, radiation as decision cost*
