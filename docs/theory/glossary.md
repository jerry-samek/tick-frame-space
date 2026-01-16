# Tick-Frame Physics Glossary

**Comprehensive reference for terms, symbols, and acronyms used in v2 framework**

---

## A

**Adjacency Principle** - The principle that entities can only interact with immediate neighbors in the tick-stream spatial lattice. See v1/15_10.

**Aliasing (Temporal)** - Loss of intermediate states when a process evolves faster than observer's sampling rate, creating perceptual distortions. See Ch1 §10.

**Auditable Agency** - The tick-frame definition of free will: constrained choice within deterministic causality where all decisions are traceable. See Ch5 §4.

---

## B

**Big Bang (Observer-Relative)** - The concept that each observer's "beginning of time" is their birth tick, not a universal event. See Ch4 §8.

**Bucketing** - O(n) rendering algorithm that groups entities by discrete temporal lag instead of sorting. See Ch6 §3, REFERENCE_doc46_01.

**Buffer (Existence)** - The finite temporal window an observer has access to: current tick (consciousness) + past ticks (memory). See Ch1 §3, Ch4 §3.

---

## C

**Causal Locality** - Principle that information propagates at most 1 spatial quantum per tick (v ≤ c). See Ch1 §5, Ch7 §2.

**Causal Readability** - Requirement that State(n+1) must be derivable from State(n) for universe coherence. See Ch1 §7.

**Collision Persistence** - Theory that particles are collision patterns, not objects; collisions are entity types, not events. See Ch3 §3, v1/30.

**Compatibilism** - Philosophical position that free will is compatible with determinism; tick-frame adopts this stance. See Ch5 §4.

**Configuration Independence** - Empirical finding that physics is independent of initial geometry at d≥3 (Hypothesis H2 falsified). See Ch2 §6.

**Consciousness** - In tick-frame: presence at current tick with self-referential awareness. See Ch4 §4.

---

## D

**Déjà Vu** - Explained as index collision: current tick pattern matches historical tick, triggering false recognition. See Ch4 §7.

**Determinism (Substrate)** - The tick-stream is fully causal with no randomness; State(n+1) = F(State(n)). See Ch5 §2.

**Dimensional Closure** - The finding that spatial dimensions beyond 4D-5D provide diminishing returns in stability. Refers to spatial dimensions only, NOT spacetime. See Ch2 §8.

**Dimensional Equivalence** - The hypothesis (falsified) that (n spatial + time) behaves like (n+1) spatial dimensions. See Ch1 §9, REFERENCE_doc50_01.

**Dispersion (Wave)** - High-frequency waves travel slower than c in discrete space due to lattice effects. See Ch7 §4.

**Double-Buffer** - Synchronization technique where simulation fills one buffer while rendering reads another, enabling lock-free coordination. See Ch6 §7.

**Dreams** - Explained as unconstrained buffer traversal during sleep when causal filter weakens. See Ch4 §7.

---

## E

**Energy-Time Relation** - Core formula: E(t) = (t - t_birth) in tick units, or E = hbar/t_planck × n in physical units. See Ch3 §5, Ch7 §3.

**Entity** - Temporal process (not object) that responds to ticks via TickTimeConsumer<E> interface. See Ch1 §1, Ch3.

**Existence Buffer** - See Buffer (Existence).

**Expansion (Substrate)** - Space grows with tick count; later generations experience higher movement costs. See Ch3 §4.

---

## F

**Fallible Commit Principle** - Once observer commits tick allocation, it's irreversible; observers can make mistakes. See Ch5 §8.

**Falsification Criteria** - Six testable predictions for the framework: Planck-scale dispersion, 3D optimality, rotation asymmetry, rho=2.0 signature, O(n) rendering, energy balance. See Ch8 §5.

**Frame (Temporal)** - Bundle of ticks that observers perceive as single unit, hiding substrate details. See Ch5 §3.

**Free Will** - Tick-frame definition: auditable agency within determinism (constrained choice, not escape from causality). See Ch5.

---

## G

**Generation** - Distance from origin in entity lineage; affects movement costs due to expansion. See Ch3 §6.

**Goldilocks Zone (3D)** - Three spatial dimensions are optimal (SPBI=2.23), balancing stability and variability. See Ch2 §3.

**Gravity (Tick-Frame)** - Proposed as time-flow gradient or substrate expansion effect (highly speculative). See Ch4 §6, Ch7 §9.

---

## H

**Horizon Boundary** - Observable limit in causal cones beyond which entities cannot interact within finite ticks. See v1/26.

---

## I

**Identity** - In tick-frame: continuity across ticks (temporal trajectory), not persistent substance. See Ch1 §9, Ch4 §2.

**Imbalance Theory** - Prediction that matter-antimatter asymmetry emerges from expansion geometry even with symmetric initial conditions. See Ch3 §4.

**Index Collision** - See Déjà Vu.

---

## L

**Lag (Temporal)** - How many ticks behind current tick an entity is; used as depth coordinate in rendering. See Ch6 §4.

**Laplace's Demon** - Hypothetical that knows all states and can predict future; possible at substrate level but not for bounded observers. See Ch5 §2.

**Linked List (Temporal Chain)** - Data structure that mirrors temporal entity chains; enables O(1) bucket clearing. See Ch6 §9.

**Lorentz Transform** - Special relativity transformation; tick-frame derivation speculative (not yet completed). See Ch7 §9.

---

## M

**MAX_HISTORY** - Maximum buffer depth (e.g., 100-1000 ticks); determines memory capacity. See Ch4 §3.

**Memory (as Addressing)** - Brain indexes historical ticks rather than storing them; memory is pointer to tick, not copy. See Ch4 §3.

**Minkowski Spacetime** - Relativity framework where time is coordinate; tick-frame decisively different (rho=2.0 vs rho=1.5). See Ch1 §9, Ch8 §8.

**Momentum (Tick-Frame)** - Pair (cost, vector): tick cost to move + spatial direction. See Ch3 §6.

---

## N

**Nyquist Limit** - Maximum frequency f_max = 1/(2×t_planck) ≈ 9.3×10^42 Hz above which waves cannot be represented. See Ch7 §4.

---

## O

**Observer** - Entity with self-referential loop, historical buffer access, and selective perception. Function: tick n → tick n+1. See Ch4.

**O(n) Complexity** - Linear time complexity; bucketing achieves this for rendering vs O(n log n) sorting. See Ch6 §3.

**Ontology (Temporal)** - Framework establishing time as primary substrate, space as emergent. See Ch1, REFERENCE_doc49.

**Over-Coherence** - Current implementation problem: structures too uniform, expected asymmetry not observed. See Ch3 §11, Ch8 §4.

---

## P

**Painter's Algorithm** - Classical rendering: sort by depth, paint back-to-front. Tick-frame uses bucketing instead. See Ch6 §10.

**Perception (Selective)** - Observer actively filters which entities to track based on tick budget. See Ch4 §5.

**Phase Transition (d=3)** - At 3 dimensions, rho becomes universal (configuration-independent). See Ch2 §4.

**Planck Scale** - Fundamental units: t_planck ≈ 5.39×10^-44 s, l_planck ≈ 1.62×10^-35 m. Tick-frame identifies tick = t_planck. See Ch7 §2.

**Position** - N-dimensional spatial coordinate (BigInteger array); represents multiples of l_planck. See Ch3 §1, Ch7 §2.

---

## Q

**Qualia** - Subjective "what it's like" experience; tick-frame suggests emerges from self-referential indexing (speculative). See Ch4 §4.

**Quantum Mechanics** - Tick-frame provides discrete substrate; QM may emerge as continuous limit. See Ch7 §4.

---

## R

**Ratchet Effect** - Temporal coupling creates energy accumulation (not dilution); explains rho=2.0 signature. See Ch1 §4.

**Rendering (Temporal)** - Using lag as depth coordinate to visualize 2D space + time as 3D scene. See Ch6.

**Rho (ρ)** - Scaling exponent in S ∝ N^rho; spatial dimensions show rho≈1.5, temporal systems show rho=2.0. See Ch1 §9, Ch2 §3.

**Rotation Asymmetry** - 933× difference: forward pitch 0% (impossible), backward pitch 93% (energy-limited). Validates v ≤ c. See Ch6 §5.

---

## S

**Sample Rate Limit** - Maximum velocity v = c = 1 spatial quantum / tick; exceeding causes aliasing/breakdown. See Ch1 §5, Ch6 §6.

**Sampling (Observer)** - How observer selects which ticks/entities to process; constrained by tick budget. See Ch4 §5.

**Schrödinger Equation (Discrete)** - Finite-difference version on tick lattice; continuous equation emerges in limit. See Ch7 §4.

**Sleep** - Computational necessity to clear buffer saturation; prevents sampling collapse and coherence loss. See Ch4 §6.

**SPBI (Stability-Probability Balance Index)** - Metric combining stability (low variance) and richness (high probability); 3D achieves maximum SPBI=2.23. See Ch2 §3.

**Substrate** - The fundamental tick-stream that generates existence; discrete, causal, ordered. See Ch1 §2.

**Surfing (Temporal)** - Entities persist through continual renewal each tick, not through static identity. See Ch3 §2.

---

## T

**Temporal Ontology** - See Ontology (Temporal).

**Ternary Logic** - Three-value system {-1, 0, +1} providing symmetry and richer dynamics than binary. See Ch5 §6.

**Tick** - Fundamental time quantum = Planck time (t_planck ≈ 5.39×10^-44 s). Universe updates every tick. See Ch1 §2, Ch7 §2.

**Tick Budget** - Computational resources available to observer per tick; determines perception capacity. See Ch4 §5, Ch5 §5.

**Tick-Stream** - Strictly ordered sequence of universal states: tick 0 → tick 1 → tick 2 → ...; absolute temporal substrate. See Ch1 §2.

**TickTimeConsumer<E>** - Java interface for temporal processes: onTick(tickCount) returns action stream. See Ch3 §9.

**Trauma** - High-salience tick with low activation threshold; disproportionately easy to recall. See Ch4 §7.

---

## U

**Uncertainty (Frame-Level)** - Observers perceive probabilistic outcomes due to coarse-graining, though substrate is deterministic. See Ch5 §3.

**Utility Function** - What observer optimizes when allocating tick budget. See Ch5 §5.

---

## V

**Value Class (Java)** - Immutable class with value semantics; SingleEntityModel is value class representing patterns not objects. See Ch3 §9.

**Velocity (Maximum)** - v_max = c = l_planck / t_planck; structural constant, not derived. See Ch7 §2.

**Void Asymmetry** - Presence (+1) costs energy, absence (0) is default; action requires justification. See Ch5 §9.

---

## W

**Wave Equation (Discrete)** - Finite-difference formulation: A(n+1) = 2A(n) - A(n-1) + spatial Laplacian. See Ch7 §4.

---

## X

**XOR (Ternary)** - Three-value exclusive-or operation generating tickstream rhythm: T(n+1) = XOR(T(n), T(n-1)). See Ch5 §6.

---

## Z

**Z-Buffer** - Classical GPU depth testing; tick-frame bucketing is alternative approach for particles. See Ch6 §10.

---

## Symbols Reference

| Symbol | Meaning | First Use | Notes |
|--------|---------|-----------|-------|
| **ρ** (rho) | Scaling exponent | Ch1 §9, Ch2 §3 | S ∝ N^ρ; spatial: ~1.5, temporal: 2.0 |
| **λ** (lambda) | Expansion coupling | Ch3 §4, Ch7 §7 | Controls cost increase with generation |
| **γ** (gamma) | Damping parameter | Experiment #15 | Field decay rate |
| **α** (alpha) | Source strength | Experiment #15 | Initial field amplitude |
| **α₀** (alpha-zero) | Initial alpha | Experiment #15 | Starting condition |
| **Δt** | Time quantum | Ch7 §2 | = t_planck ≈ 5.39×10^-44 s |
| **Δx** | Space quantum | Ch7 §2 | = l_planck ≈ 1.62×10^-35 m |
| **c** | Speed of light | Ch1 §5, Ch7 §2 | = Δx / Δt = 2.998×10^8 m/s |
| **E** | Energy | Ch3 §5, Ch7 §3 | E(t) = t - t_birth (tick units) |
| **hbar** (ℏ) | Reduced Planck constant | Ch7 §3 | 1.055×10^-34 J·s |
| **G** | Gravitational constant | Ch7 §8 | 6.674×10^-11 m³/(kg·s²) |
| **B** | Buffer / Budget | Ch4 §3, Ch5 §5 | Temporal window or tick budget |
| **T** | Tick count or frame period | Throughout | Context-dependent |
| **N** | Number of entities/sources | Ch2 §3 | Used in scaling laws |
| **S** | Aggregate salience/field | Ch2 §3 | Total field strength |
| **d** | Spatial dimensions | Ch2 | 1D, 2D, 3D, 4D, 5D tested |
| **CV** | Coefficient of variation | Ch2 §5 | std / mean |
| **SPBI** | Stability-Probability Balance | Ch2 §3 | (1/CV) × P × 100 |

---

## Acronyms

| Acronym | Full Form | First Use | Meaning |
|---------|-----------|-----------|---------|
| **SPBI** | Stability-Probability Balance Index | Ch2 §3 | Metric for dimensional optimality |
| **LQG** | Loop Quantum Gravity | Ch8 §8 | Alternative quantum gravity theory |
| **QFT** | Quantum Field Theory | Ch7 §10 | Quantum theory of fields |
| **QM** | Quantum Mechanics | Ch7 §4 | Standard quantum theory |
| **GR** | General Relativity | Ch7 §9 | Einstein's gravity theory |
| **CMB** | Cosmic Microwave Background | Ch7 §10 | Early universe radiation |
| **CPU** | Central Processing Unit | Ch6 §8 | Computer processor |
| **GPU** | Graphics Processing Unit | Ch6 §10 | Graphics accelerator |
| **UUID** | Universally Unique Identifier | Ch3 §8 | Entity identity |
| **SI** | International System of Units | Ch7 §2 | Standard units |
| **NIST** | National Institute of Standards | Ch7 §2 | Standards organization |
| **CA** | Cellular Automaton | Ch8 §8 | Discrete computational model |

---

## Greek Alphabet Reference (Physics Symbols)

For readers unfamiliar with Greek letters commonly used in physics:

| Symbol | Name | Typical Usage in Tick-Frame |
|--------|------|----------------------------|
| α | alpha | Source strength, coupling constant |
| β | beta | (Not heavily used) |
| γ | gamma | Damping parameter, Lorentz factor |
| δ | delta | Small change (Δ for finite change) |
| ε | epsilon | Permittivity, small parameter |
| λ | lambda | Expansion coupling constant |
| μ | mu | (Not heavily used) |
| ρ | rho | **Scaling exponent (critical parameter)** |
| σ | sigma | Cross-section, standard deviation |
| τ | tau | Time constant |
| φ | phi | Phase, field |
| ψ | psi | Wavefunction |
| ω | omega | Angular frequency |
| Δ | Delta | Finite change (Δt, Δx) |
| Σ | Sigma | Summation |
| ∇ | nabla | Gradient operator |

---

## Common Notation Patterns

### Tick-Frame Specific
- **State(n)** - Universe state at tick n
- **T(n)** - Tick n in sequence
- **E(t)** - Energy as function of time
- **O** - Observer
- **F** - Deterministic update function
- **[x, y, z]** - Spatial coordinates (position)
- **{-1, 0, +1}** - Ternary value set

### Mathematical
- **∝** - Proportional to (S ∝ N^ρ)
- **≈** - Approximately equal
- **≤** - Less than or equal (v ≤ c)
- **→** - Maps to, leads to
- **∈** - Element of (n ∈ ℤ)
- **∅** - Empty set
- **ℝ** - Real numbers
- **ℤ** - Integers
- **ℕ** - Natural numbers

### Programming (Java)
- **BigInteger** - Arbitrary precision integer
- **Stream<T>** - Sequence of elements
- **→** - Lambda arrow (in code examples)
- **<E>** - Generic type parameter

---

## Document Cross-References

Terms marked with chapter/document references can be found at:

- **Ch1** - v2_ch01_temporal_ontology.md
- **Ch2** - v2_ch02_dimensional_framework.md
- **Ch3** - v2_ch03_entity_dynamics.md
- **Ch4** - v2_ch04_observer_consciousness.md
- **Ch5** - v2_ch05_free_will_ternary_logic.md
- **Ch6** - v2_ch06_rendering_theory.md
- **Ch7** - v2_ch07_physical_formalization.md
- **Ch8** - v2_ch08_integration_falsification.md
- **REFERENCE_doc[N]** - docs/theory/REFERENCE_doc[N]_*.md
- **v1/[N]** - docs/theory/v1/[N] [Title].md

---

**Last updated**: January 2026
**Alphabetical entries**: 85+
**Symbols**: 20+
**Acronyms**: 11+
**Status**: Living document (will expand with framework)
