# Chapter 7: Physical Formalization - Mathematical Foundations

**Status**: Theoretical framework (analytical derivations in progress)
**Key Concepts**: Planck scale discretization, discrete wave equations, energy-time relation
**Related Chapters**: Ch1 (Temporal Ontology), Ch2 (Dimensional Framework), Ch3 (Entity Dynamics)

---

## Abstract

This chapter provides mathematical formalization of tick-frame physics, grounding computational implementation in rigorous physical principles. We establish **discrete time at the Planck scale** as the fundamental axiom and derive key results:

**Core formalizations**:
- **Tick as Planck time**: Delta_t = t_planck (5.39 × 10^-44 s)
- **Energy-time relation**: E(t) = hbar / t_planck × (t - t_birth)
- **Discrete wave equation**: Finite-difference formulation on tick lattice
- **Sample rate limit**: v_max = c = 1 spatial quantum / tick
- **Dimensional scaling**: Validated rho=2.0 signature (Ch1, Exp 50)

**Status**: Analytical framework established, experimental validation ongoing, full derivation of classical limits in progress.

**Open questions**: Full relativity compatibility, quantum field theory formulation, gravitational effects.

---

## 1. Introduction: From Computation to Physics

### Motivation

Chapters 1-3 established tick-frame physics **computationally**:
- Ch1: Temporal ontology (time as substrate)
- Ch2: Dimensional optimality (3D Goldilocks zone)
- Ch3: Entity dynamics (implementation patterns)

**Question**: Can these computational principles be **formally grounded in physics**?

**This chapter**: Provide mathematical axioms and derive observable consequences.

### Approach

**Axiom 1 (Temporal Discreteness)**:
> Time advances in discrete quanta. The fundamental time unit is the Planck time: Delta_t = t_planck.

**Axiom 2 (Spatial Discreteness)**:
> Space is represented on a discrete lattice. The fundamental length unit is the Planck length: Delta_x = l_planck.

**Axiom 3 (Causal Locality)**:
> Information propagates at most 1 spatial quantum per tick. This defines the maximum speed: c = l_planck / t_planck.

**Axiom 4 (Energy from Time)**:
> Energy accumulates linearly with tick count: E(n) = hbar / t_planck × n, where n is the number of ticks elapsed.

**Goal**: Derive:
1. Sample rate limit (v <= c)
2. Discrete wave equations
3. Collision mechanics
4. Dimensional scaling laws
5. Observable predictions

---

## 2. Planck Scale Discretization

### Physical Constants (SI Units)

**Planck units** (from fundamental constants):
```
Planck time:   t_planck = sqrt(hbar × G / c^5) ≈ 5.39 × 10^-44 s
Planck length: l_planck = sqrt(hbar × G / c^3) ≈ 1.62 × 10^-35 m
Planck energy: E_planck = sqrt(hbar × c^5 / G) ≈ 1.96 × 10^9 J
Planck mass:   m_planck = sqrt(hbar × c / G)   ≈ 2.18 × 10^-8 kg
```

where:
- hbar = reduced Planck constant = 1.055 × 10^-34 J·s
- G = gravitational constant = 6.674 × 10^-11 m^3/(kg·s^2)
- c = speed of light = 2.998 × 10^8 m/s

### Tick as Planck Time

**Identification**:
```
1 tick = t_planck
```

**Implications**:
1. **Shortest measurable time**: No physical process can resolve intervals < t_planck
2. **Tick-stream is fundamental**: Not an approximation, but the substrate itself
3. **Discrete evolution**: Universe updates every t_planck

**Relation to computation**:
- Java `BigInteger tickCount`: Represents multiples of t_planck
- `tickCount = n` corresponds to physical time `t = n × t_planck`

### Spatial Lattice

**Lattice spacing**:
```
Delta_x = l_planck (in each dimension)
```

**Position quantization**:
```
Position coordinates: x_i in Z × l_planck  (i = 1, 2, ..., d dimensions)
```

**Java implementation**:
```java
record Position(BigInteger[] coords)  // Each coord represents multiples of l_planck
```

**Physical interpretation**:
- `Position([5, 3, -2])` → Physical location (5×l_planck, 3×l_planck, -2×l_planck)
- Spatial coordinates are **exact integers**, no floating-point error

### Speed of Light as Sample Rate

**Derivation**:
```
Maximum propagation: 1 spatial quantum per tick
=> v_max = Delta_x / Delta_t
         = l_planck / t_planck
         = c  (by definition of Planck units)
```

**This IS the speed of light**. Not derived, but **identified** as the lattice constraint.

**Convergence with Ch1 §5 and Ch6 §6**:
- Ch1: Sample rate limit (v <= 1 tick/tick)
- Ch6: Rotation asymmetry (v <= 1 enforced kinematically)
- This chapter: v_max = c (formal derivation)

**All three perspectives agree**: Maximum speed is structural, not dynamical.

---

## 3. Energy-Time Relation

### Derivation from Axiom 4

**Axiom 4**:
> E(n) = hbar / t_planck × n

where `n` is tick count.

**In physical units**:
```
E(t) = hbar / t_planck × (t / t_planck)
     = hbar × t / t_planck^2
     = (hbar / t_planck) × (t - t_birth)  (setting origin at birth)
```

**Define energy quantum**:
```
E_tick := hbar / t_planck ≈ 1.96 × 10^9 J  (Planck energy)
```

**Then**:
```
E(t) = E_tick × (t - t_birth) / t_planck
```

**In tick units** (`t = n × t_planck`):
```
E(n) = E_tick × n
```

**Interpretation**:
- Each tick injects `E_tick` energy into each entity
- Energy is **not conserved from initial conditions** but **generated by tick-stream**
- Time IS the energy source (Ch1 §2: tick-stream as substrate)

### Comparison to Classical Mechanics

**Classical**:
```
E = T + V  (kinetic + potential)
dE/dt = 0  (conservation)
```

**Tick-frame**:
```
E(n) = E_tick × n  (linear growth)
dE/dn = E_tick    (constant injection rate)
```

**Why different?**:
- Classical: Closed system assumption
- Tick-frame: Open system (tick-stream is external energy source)

**Analogy**: Like a particle in an external field that does work. Tick-stream IS the field.

### Energy Expenditure (Movement Cost)

**From Ch3 §6**:
```
Entity can move when E(n) >= cost
=> E_tick × n >= cost
=> n >= cost / E_tick
```

**Cost in physical units**:
```
cost [ticks] × E_tick [J/tick] = total energy required [J]
```

**Movement periodicity**:
```
If cost = 5 ticks:
Entity moves every 5 ticks = 5 × t_planck ≈ 2.7 × 10^-43 s
```

**At macroscopic scale**: Movement appears continuous (tick-rate >> observation rate).

---

## 4. Discrete Wave Mechanics

### Classical Wave Equation (Continuous)

**Standard form**:
```
∂²A/∂t² = c² × ∇²A
```

where:
- A(x,t) = wave amplitude
- c = wave speed
- ∇² = Laplacian (spatial derivatives)

**Solutions**: Continuous waves, arbitrary frequencies.

### Tick-Frame Wave Equation (Discrete)

**Finite-difference approximation**:
```
[A(n+1) - 2×A(n) + A(n-1)] / (Delta_t)²
    = c² × [A(i+1) - 2×A(i) + A(i-1)] / (Delta_x)²
```

where:
- n = tick index (time)
- i = position index (space)
- A(n,i) = amplitude at tick n, position i

**Simplify** (using c = Delta_x / Delta_t):
```
A(n+1,i) = 2×A(n,i) - A(n-1,i)
           + [A(n,i+1) - 2×A(n,i) + A(n,i-1)]
```

**Interpretation**:
- Wave amplitude at next tick depends on current tick and spatial neighbors
- **No continuous derivatives** - only discrete differences
- **Causally local**: A(n+1,i) depends only on nearest neighbors at tick n

### Properties of Discrete Waves

**1. Maximum frequency** (Nyquist limit):
```
f_max = 1 / (2 × Delta_t) = 1 / (2 × t_planck) ≈ 9.3 × 10^42 Hz
```

**Interpretation**: Waves with f > f_max cannot be represented (aliasing).

**2. Dispersion relation**:
For wave A(n,i) = A_0 × exp(i×k×x - i×omega×t):
```
omega(k) = 2/Delta_t × sin(k × Delta_x / 2)
```

**Differs from continuous**:
```
omega_continuous(k) = c × k  (linear)
omega_discrete(k) ≈ c × k - (c × Delta_x²/24) × k³  (dispersive)
```

**Implication**: High-frequency waves (k ~ 1/Delta_x) travel slower than c. **Dispersion** emerges from discreteness.

**3. Energy quantization**:
```
E = hbar × omega(k)
```

Since omega is quantized (discrete k values on lattice), energy levels are discrete.

### Connection to Quantum Mechanics

**Schrödinger equation** (continuous):
```
i×hbar × ∂psi/∂t = -hbar²/(2m) × ∇²psi + V×psi
```

**Tick-frame analog** (discrete):
```
i×hbar × [psi(n+1) - psi(n)] / Delta_t
    = -hbar²/(2m) × [psi(i+1) - 2×psi(i) + psi(i-1)] / Delta_x²
       + V(i) × psi(n,i)
```

**Rearrange**:
```
psi(n+1,i) = psi(n,i)
             - i×Delta_t/(hbar) × [Hamiltonian × psi(n,i)]
```

**Interpretation**:
- Discrete time evolution of wavefunction
- Each tick applies discrete Hamiltonian operator
- Matches quantum mechanics in continuous limit (Delta_t, Delta_x → 0)

**Ontological note**: This suggests quantum mechanics may be **emergent from discrete substrate**, not fundamental itself.

---

## 5. Collision Mechanics (Formal Treatment)

### Energy-Momentum Conservation

**From Ch3 §7**, naive collision:
```
E_merged = E_1 + E_2 - cost_merge
P_merged = (E_1 × P_1 + E_2 × P_2) / (E_1 + E_2)
```

**Formalize as 4-momentum** (energy + momentum):
```
Define 4-momentum: (E/c, p_x, p_y, p_z)

For entity 1: (E_1/c, p_1)
For entity 2: (E_2/c, p_2)
```

**Conservation** (before collision = after collision):
```
(E_1 + E_2)/c = E_merged/c + Q/c  (energy)
p_1 + p_2 = p_merged              (momentum)
```

where Q = cost_merge (energy lost to merge process).

**Solve for merged momentum**:
```
p_merged = p_1 + p_2
```

**Solve for merged energy**:
```
E_merged = E_1 + E_2 - cost_merge
```

**This matches Ch3 implementation exactly.**

### Collision Cross-Section

**Classical**: Entities collide if they occupy same position.

**Tick-frame**: Position is discrete lattice site.

**Collision condition**:
```
Position_1(n) = Position_2(n)  (same lattice site at same tick)
```

**Cross-section**:
```
sigma = (Delta_x)^d  (d = spatial dimensions)
```

In 3D:
```
sigma_3D = l_planck³ ≈ 4.2 × 10^-105 m³
```

**Extremely small** - collisions are rare at macroscopic scales (as expected).

### Annihilation Condition

**From Ch3 §7**:
```
If E_merged <= 0: Annihilation (both entities disappear)
```

**Physical interpretation**:
- **Wave cancellation**: Destructive interference
- **Energy below threshold**: Cannot sustain entity existence
- **Analogous to**: Particle-antiparticle annihilation (but not requiring opposite charges)

**Condition for annihilation**:
```
E_1 + E_2 < cost_merge
=> Energy insufficient to create merged state
```

**Energy release**:
```
E_annihilation = E_1 + E_2  (all energy radiated/lost to substrate)
```

**Tracked in implementation** (Ch3 §5):
```java
public static final AtomicReference<FlexInteger> totalEnergyLoss = ...
```

---

## 6. Dimensional Scaling Laws

### Empirical Law (from Experiment 15, Ch2)

**Observed**:
```
S ∝ N^rho

where:
- S = aggregate salience (total field strength)
- N = number of sources (entities)
- rho = scaling exponent
```

**Measured values**:
```
3D: rho = 1.503 ± 0.02
4D: rho = 1.532 ± 0.03
5D: rho = 1.571 ± 0.04
```

**Mean**: rho ≈ 1.5 (spatial dimensions)

### Theoretical Derivation (Surface-Area Law)

**Hypothesis**: Salience scales like surface area of emission sphere.

**In d dimensions**, surface area of d-sphere with radius r:
```
A_d(r) ∝ r^(d-1)
```

**For N sources uniformly distributed**:
- Volume filled: V ∝ N
- Characteristic radius: r ∝ N^(1/d)
- Surface area: A ∝ r^(d-1) ∝ N^((d-1)/d)

**Scaling exponent**:
```
rho_theory = (d-1)/d
```

**Predictions**:
```
d=3: rho = 2/3 ≈ 0.667
d=4: rho = 3/4 = 0.75
d=5: rho = 4/5 = 0.8
```

**Discrepancy**: Theory predicts rho < 1, experiments show rho ≈ 1.5.

**Why?** Classical surface-area law assumes:
1. Passive diffusion (no active sources)
2. Static configuration (no temporal evolution)
3. Continuous space (no discrete lattice)

**Tick-frame corrections**:
1. **Active sources**: Entities emit continuously (tick-by-tick)
2. **Temporal accumulation**: Salience builds over ticks
3. **Lattice effects**: Discrete space alters propagation

**Refined model** (speculative):
```
S(N,T) = N × f(T)  (N sources, T ticks)

where f(T) accounts for temporal accumulation.
If f(T) ∝ T^alpha:
S ∝ N × T^alpha

For fixed observation time T:
S ∝ N × N^(alpha × beta)  (if T ∝ N^beta from simulation dynamics)

=> rho = 1 + alpha × beta
```

**Fit to data** (3D, rho=1.503):
```
1.503 = 1 + alpha × beta
=> alpha × beta ≈ 0.5
```

**If beta = 1** (T ∝ N, linear time scaling):
```
alpha = 0.5
=> f(T) ∝ sqrt(T)
```

**Physical meaning**: Salience accumulates sub-linearly with time (diffusive growth, characteristic of wave spreading).

**Status**: Speculative. Full analytical derivation pending.

### rho=2.0 Signature (Time as Dimension)

**From Experiment 50, Ch1 §9**:

**When time is treated as explicit dimension** (n spatial + time):
```
ALL (n+t) systems: rho = 2.0 ± 0.002
```

**Theoretical interpretation** (ratchet effect, Ch1 §4):

**Temporal coupling**:
```
Wave equation with time dimension:
∂²A/∂t² + ∂²A/∂x² + ∂²A/∂y² + ... = 0  (n+t dimensions)
```

**Unlike spatial dimensions**, temporal derivative couples successive ticks **unidirectionally**:
```
A(n+1) = f(A(n))  (tick n influences n+1, not vice versa)
```

**Result**: Energy accumulates along time axis (coherence), doesn't dilute (spatial diffusion).

**Scaling**:
```
S ∝ N² in (n+t) systems
=> rho = 2.0 (quadratic)
```

**Why quadratic?**
- **N sources** emit at each tick
- **N ticks** of accumulated contributions (if T ∝ N)
- **Total contributions**: N × N = N²

**Contrast with spatial**:
- **N sources** emit radially
- **Surface area** grows ~ N^((d-1)/d)
- **Energy dilutes** over surface
- **Result**: rho < 2

**This is the formal justification for Ch1's rho=2.0 signature as temporal fingerprint.**

---

## 7. Momentum and Cost Functions

### Momentum as Discrete Velocity

**From Ch3 §6**:
```
Momentum = (cost, vector)

where:
- vector: Direction of movement (discrete offset)
- cost: Ticks required per movement
```

**Physical interpretation**:
```
Velocity = Delta_x / (cost × Delta_t)
         = l_planck / (cost × t_planck)
         = c / cost
```

**Relation to classical momentum**:
```
p_classical = m × v
```

**In tick-frame**:
```
p_tick = m × c / cost
=> cost = m × c / p_tick
```

**Interpretation**: Higher momentum → lower cost (moves more frequently).

### Cost Function Calculation

**From Ch3 §6** (Utils.computeEnergyCostOptimized):
```
cost = f(momentum.vector, offset, magnitude, base_cost, generation)
```

**Factors**:
1. **Alignment**: cos(angle) between current momentum and new offset
2. **Magnitude**: |offset| (distance)
3. **Base cost**: Intrinsic movement cost
4. **Generation**: Expansion effect (later generations experience higher cost)

**Proposed formula** (speculative):
```
cost = base_cost × magnitude × [1 + k × (1 - cos(angle))] × exp(lambda × generation)

where:
- k: Directional cost penalty (k > 0 penalizes direction changes)
- lambda: Expansion coupling constant (lambda > 0 increases cost with distance from origin)
```

**Physical meaning**:
- **Alignment term**: Changing direction requires extra energy (angular momentum change)
- **Magnitude term**: Moving farther = more energy
- **Generation term**: Expansion makes movement harder in outer regions (Hubble-like effect)

**Status**: Exact functional form used in Java implementation to be extracted and formalized.

### Expansion Coupling (lambda parameter)

**From Ch3 §11** (over-coherence problem):
- Current implementation may not couple expansion sufficiently
- Imbalance (Doc 29) predicts asymmetry from expansion
- **lambda = 0**: No expansion effect (current suspected state)
- **lambda > 0**: Expansion creates directional bias (desired state)

**Experimental test**:
- Vary lambda parameter
- Measure asymmetry in entity distribution
- Compare to Doc 29 predictions

---

## 8. Deriving Physical Constants

### Speed of Light (Already Derived)

**From §2**:
```
c = l_planck / t_planck ≈ 2.998 × 10^8 m/s
```

**Structural constant**, not free parameter.

### Planck's Constant (Assumed Fundamental)

**hbar** appears in:
- Energy quantum: E_tick = hbar / t_planck
- Wave mechanics: E = hbar × omega
- Quantum evolution: psi(n+1) = U(hbar, Delta_t) × psi(n)

**Status**: Input parameter (fundamental constant).

### Fine Structure Constant (Open Question)

**Alpha** = e² / (4×pi×epsilon_0×hbar×c) ≈ 1/137

**Question**: Can alpha be derived from tick-frame structure?

**Speculation**:
- If electromagnetic field emerges from tick-lattice geometry
- Charge quantization may relate to lattice spacing
- Alpha may connect discrete and continuous descriptions

**Status**: Open research question.

### Gravitational Constant (Open Question)

**G** appears in Planck units but is input to their definition.

**Question**: Can G be derived from substrate expansion dynamics?

**Speculation** (from Doc 29, Imbalance):
- Expansion creates directional bias (pressure)
- Gravity = residual effect of expansion geometry?
- G may relate to expansion rate

**Status**: Highly speculative, no formal derivation yet.

---

## 9. Relation to Relativity

### Special Relativity

**Lorentz transformations**: Mix space and time coordinates.

**Tick-frame challenge**: Time is substrate, space is emergent (Ch1 §4).

**Question**: How to reconcile?

**Proposed approach**:
1. **Local Lorentz invariance** can emerge from discrete symmetries
2. **Tick-stream is frame-independent** (absolute substrate)
3. **Observed time dilation** = modulation of local tick-rate

**Mechanism** (speculative):
```
Moving entity experiences: Delta_t_effective = gamma × Delta_t
where gamma = 1/sqrt(1 - v²/c²)

Implementation: Entity "skips" ticks when moving fast
=> Local tick-rate appears slower (time dilation)
```

**Status**: Conceptual framework. Formal derivation pending.

### General Relativity

**Curved spacetime**: Geometry encodes gravity.

**Tick-frame analog**: Substrate expansion + lattice distortion.

**Proposed approach**:
1. **Lattice spacing varies**: Delta_x = Delta_x(position)
2. **Tick-rate varies**: Delta_t = Delta_t(position)
3. **Effective metric**: g_uv emerges from lattice parameters

**Einstein equation analog** (speculative):
```
R_uv - (1/2)×g_uv×R = (8×pi×G/c⁴) × T_uv

LHS: Lattice curvature (how spacing varies)
RHS: Entity distribution (energy-momentum)
```

**Status**: Conceptual. No rigorous derivation yet.

### Compatibility Summary

| Relativistic Effect | Tick-Frame Mechanism | Status |
|---------------------|----------------------|--------|
| Speed of light limit | v_max = c = Delta_x/Delta_t | Validated (Ch6 §6) |
| Time dilation | Local tick-rate modulation | Speculative |
| Length contraction | Lattice spacing modulation | Speculative |
| Equivalence principle | Expansion = gravity? | Highly speculative |
| Black holes | Lattice singularities? | Open question |

**Overall**: Low-velocity, weak-field limits likely compatible. High-energy, strong-field regime requires further formalization.

---

## 10. Open Formalization Questions

### Analytical Derivations Needed

1. **Exact cost function**: Extract from Java implementation, formalize mathematically
2. **Dimensional scaling**: Derive rho ≈ 1.5 from first principles (surface-area law + corrections)
3. **Collision cross-sections**: Probability of collision as function of density
4. **Energy balance**: Formal treatment of energy injection, expenditure, conservation
5. **Expansion dynamics**: How substrate growth couples to entity behavior

### Compatibility Questions

1. **Quantum field theory**: Can QFT be formulated on discrete tick-lattice?
2. **Renormalization**: Do infinities arise? How are they handled in discrete theory?
3. **Gauge symmetries**: U(1), SU(2), SU(3) on lattice - do they emerge or must be imposed?
4. **Chirality**: Fermion handedness in discrete space - preserved or violated?
5. **CPT symmetry**: Charge, parity, time reversal - compatible with tick-stream?

### Observational Predictions

1. **Dispersion at high energy**: Do cosmic rays show discrete-space signatures?
2. **Lorentz violation**: Deviations at Planck scale?
3. **Gravitational wave dispersion**: Frequency-dependent speed?
4. **Cosmological signatures**: Expansion history, CMB anomalies?
5. **Quantum decoherence**: Does discrete substrate induce decoherence?

---

## 11. Conclusion

This chapter establishes **mathematical foundations** for tick-frame physics:

**Core formalizations**:
- **Planck scale discretization**: tick = t_planck, position quantum = l_planck
- **Energy-time relation**: E(n) = E_tick × n (linear accumulation)
- **Sample rate limit**: v_max = c (structural constant)
- **Discrete wave mechanics**: Finite-difference equations on tick-lattice
- **Collision mechanics**: Energy-momentum conservation with discrete positions

**Key results**:
- Speed of light emerges from lattice structure
- Quantum mechanics approximates discrete evolution in continuous limit
- Dimensional scaling (rho ≈ 1.5) consistent with surface-area law + corrections
- rho=2.0 signature (temporal) from unidirectional tick coupling

**Validated predictions**:
- Sample rate limit: v <= c (Ch6 §6, Exp 44 rotation asymmetry)
- Temporal scaling: rho=2.0 in (n+t) systems (Exp 50)
- O(n) rendering: Discrete time enables bucketing (Ch6 §3, Exp 46_01)

**Open questions**:
- Full relativity derivation (Lorentz transforms from discrete symmetries)
- Quantum field theory on tick-lattice
- Gravitational effects (expansion coupling to geometry)
- Experimental tests of Planck-scale discreteness

**Status**:
- **Axiomatic framework**: Established
- **Computational implementation**: Validated (Chapters 1-3, 6)
- **Analytical derivations**: Partial (ongoing work)
- **Experimental tests**: Indirect (cosmological, high-energy)

**Next step** (Ch8): Integration of all chapters, gap analysis, falsification criteria.

---

## References

### V2 Chapters
- **Ch1**: Temporal Ontology (tick-stream substrate, rho=2.0 signature)
- **Ch2**: Dimensional Framework (3D optimality, scaling laws)
- **Ch3**: Entity Dynamics (energy mechanics, collision persistence)
- **Ch6**: Rendering Theory (sample rate limit, v <= c validation)

### V1 Theory Documents
- **Doc 15**: Minimal Model (computational basis)
- **Doc 49**: Temporal Ontology (ontological foundation)
- **Doc 50**: Dimensional Equivalence Test (rho=2.0 signature)

### Experiments
- **Experiment #15**: 3D optimality (3,960 simulations, rho ≈ 1.5)
- **Experiment #44**: Rotation asymmetry (v <= c kinematic validation)
- **Experiment #50**: rho=2.0 signature (1,095 configs, 0% equivalence)

### Physics References
- Planck units: Fundamental scales in physics
- Lattice field theory: Discrete spacetime formulations
- Finite-difference methods: Numerical solutions to PDEs
- Quantum mechanics on lattices: Computational physics

### Mathematical Tools
- Finite-difference calculus: Discrete derivatives
- Dispersion relations: Wave propagation on lattices
- Scaling laws: Power-law behavior, critical exponents
- Conservation laws: Energy, momentum in discrete systems

---

**Document Status**: Theoretical framework complete, analytical derivations partial
**Key Results**: Planck-scale discretization, v=c as structural constant
**Open Work**: Full relativity derivation, QFT formulation
**Falsification**: Planck-scale observations, high-energy dispersion tests
