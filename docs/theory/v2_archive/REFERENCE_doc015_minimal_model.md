# REFERENCE: Minimal Model Recommendation (Doc 15)

**Original**: v1/15 Minimal Model Recommendation for Time–Visualization Testing
**Status**: **IMPLEMENTED IN JAVA** (tick-space-runner)
**Date**: Original theory document
**Note**: This is the **Chapter 15 model** that forms the basis of the current Java implementation. The theoretical
framework has since evolved to **Doc 49 (Temporal Ontology)**, which refines the ontological status of time and space,
but the Java codebase still implements the Chapter 15 model described here.

---

## Why This Document Is Preserved

This document is **critical for understanding the current Java implementation**:

1. **Implementation Basis**: The tick-space-runner module directly implements this model
2. **Validated Experimentally**: Experiments #15 (3,960 simulations) used this framework
3. **Bridge Document**: Links theory → code → experiments
4. **Dimensional Framework**: Provides foundation for 3D optimality findings

**Gap Note**: While this model works computationally, **Doc 49 (Temporal Ontology)** represents the current theoretical
apex. The ontological shift is:

- **Chapter 15**: Time as tick counter, space as coordinates
- **Doc 49**: Time as primary substrate, space as emergent

See v2 Ch8 (Integration & Falsification) for implementation roadmap to align code with Doc 49.

---

## 1. Goals

- Provide a **continuous root evolution** to preserve relativity compatibility.
- Implement **discrete commits** via PoF thresholding to exercise tick rules.
- Generate **observable artefacts** to embed "past" into the present tick.
- Keep parameters minimal for easy tuning, auditing, and falsification.

---

## 2. Core Minimal Model

### Root Substrate

- **State:** \(x(t)\in\mathbb{R}^{d}\) with small dimension (e.g., \(d=2\) or \(4\)).
- **Dynamics:**
  \[
  \dot{x}(t)=A x(t)+b
  \]
  where \(A\) is stable (negative real eigenvalues).
- **Reason:** Linear flow ensures analytic solutions and controlled complexity.

### Tick Generator and PoF

- **Clock:**
  \[
  \dot{\Theta}(t)=\omega_P\,F(x(t))
  \]
- **Commit rule:**
  \[
  \Theta(t^-)\!<\!n+\delta \land \Theta(t)\!\ge\!n+\delta \Rightarrow \text{emit PoF at }t_n
  \]
- **Hysteresis:** \(\delta>0\) prevents chattering.
- **Reason:** Directly tests temporal rules and stability guards.

### Artefact Field (Seeing the Past)

- **Carrier equation (scalar wave):**
  \[
  \partial_{tt}\mathcal{A}-c^2\nabla^2 \mathcal{A}+\gamma\,\partial_t\mathcal{A}=J(x,t)
  \]
- **Emission:**
  \[
  J(x,t)=\sum_{n} q_n\,\delta(t-t_n)\,\delta(x-x_n)
  \]
  with \(q_n=\alpha_0+\alpha_1\|x(t_n)\|\).
- **Reason:** Wave equation provides causal propagation; artefacts are easy to tag and observe.

### Agent Refresh and Observation

- **Subset refresh:**
  \[
  r_a(t)=\frac{1}{M}\,\omega_P F(x(t)),\quad M\in\mathbb{N}^+
  \]
- **Accumulator:**
  \[
  \dot{\Psi}(t)=r_a(t)\,S(\mathcal{A}(\cdot,t),a)
  \]
  Commit when \(\Psi\ge 1+\varepsilon\).
- **Salience functional:**
  \[
  S=\int w(x)\,\mathcal{A}(x,t)^2\,dx
  \]
- **Reason:** Minimal percept loop to validate synchronization and embedded memory reading.

---

## 3. Modulation Choices for \(F(x)\)

- **Constant baseline:** \(F(x)\equiv 1\) → pure Planck ticks.
- **Energy-coupled:**
  \[
  F(x)=\text{clip}(a_0+a_1\|x\|,\ \epsilon,\ F_{\max})
  \]
- **Velocity proxy (optional):**
  \[
  F(x,v)=F_0(x)\,\sqrt{1-\frac{v^2}{c^2}}
  \]
- **Curvature proxy (optional):**
  \[
  F(x)=F_0(x)\,(1+\beta\,\|x\|)
  \]

---

## 4. Starter Configuration and Outputs

### Parameters

- Linear flow:
  \[
  A=\begin{bmatrix}-\lambda & 0\\ 0 & -\lambda\end{bmatrix},\quad b=0,\quad \lambda>0
  \]
- Clock: \(\omega_P=1/t_P,\ F(x)\equiv 1,\ \delta=0.1\).
- Wave: 1D lattice, \(c=1,\ \gamma=0.01\).
- Emission: \(x_n=x(t_n),\ q_n=\alpha_0+\alpha_1\|x_n\|\).

### Logged Outputs

- **Root commits:** \((n, t_n, \Theta(t_n), x(t_n), F(x_n), \text{Mode}=\text{COMMIT})\).
- **Artefacts:** \((n, q_n, x_n, \text{Tag}_n)\) and \(\mathcal{A}(x,t_n)\) snapshots.
- **Agent frames:** \((k, t_k, \Psi(t_k), S, M, \text{Mode})\).

---

## 5. Why This Is the Simplest That Works

- **Few moving parts:** Linear ODE + scalar wave + thresholding.
- **Direct tests:** Time commits, embedded memory, agent synchronization.
- **Extensible knobs:** Swap \(F(x)\) from constant to energy/velocity/curvature to reproduce dilation effects.
- **Audit-ready:** Every event taggable; chattering and ordering handled via hysteresis and merge policy.

---

## 6. Java Implementation

### Current Status (tick-space-runner)

**Implemented Components**:

- **TickTimeModel**: Discrete tick generator (`BigInteger tickCount`)
- **SubstrateModel**: N-dimensional spatial substrate
- **EntityModel**: Entities with position, energy, momentum
- **EntitiesRegistry**: Spatial hash map (`ConcurrentHashMap<Position, EntityModel>`)
- **Collision Detection**: Atomic position updates, `CollidingEntityModel` creation

**Key Classes**:

- `TickTimeConsumer<E>`: Interface for tick-responsive entities
- `SingleEntityModel`: Basic entity with movement and division
- `CollidingEntityModel`: Handles multi-entity collisions
- `Position`: N-dimensional coordinate record (immutable)
- `Momentum`: Movement vector with cost

**Update Pattern**:

```java
interface TickTimeConsumer<E> {
  Stream<TickAction<E>> onTick(BigInteger tickCount);
}
```

Entities return `WAIT` or `UPDATE` actions. Updates execute in parallel via work-stealing pool.

### Mapping Theory → Code

| Theory Concept    | Java Implementation                          |
|-------------------|----------------------------------------------|
| Tick generator    | `TickTimeModel.start()` (scheduled executor) |
| Root substrate    | `SubstrateModel` (dimensional size, offsets) |
| Entities          | `EntityModel` (position, energy, momentum)   |
| Commits           | `onTick()` returns `TickAction.UPDATE`       |
| PoF threshold     | Energy-based division threshold              |
| Artefact field    | Not yet implemented                          |
| Agent observation | Not yet implemented                          |

### What's Missing

Components from Chapter 15 model **not yet in Java**:

- ❌ Artefact field (wave equation propagation)
- ❌ Agent/observer models
- ❌ Salience accumulation
- ❌ Modulation functions F(x)
- ❌ Hysteresis on commit rules

These are **research features** not needed for core substrate validation.

---

## 7. Experimental Validation

### Experiment #15 (v6-gpu, v7-final)

**Scope**: 3,960 simulations, 1D-5D dimensional sweep

**Used this model for**:

- Salience propagation (wave-like dynamics)
- Commit rules (PoF thresholding)
- Source emission (artefact generation)
- Dimensional stability testing

**Key findings**:

- 3D is optimal (Goldilocks zone), not exclusive
- ρ=2.0 phase transition @ d=3
- Dimensional scaling laws validated

**See**: `experiments/15_minimal-model/`, v2 Ch2 (Dimensional Framework)

---

## 8. Relation to Doc 49 (Temporal Ontology)

### Conceptual Shift

**Chapter 15 (this document)**:

- Time = tick counter (discrete evolution parameter)
- Space = coordinate system (N-dimensional grid)
- Entities = objects with position and state
- **Ontology**: Computational substrate model

**Doc 49 (Temporal Ontology)**:

- Time = primary substrate (tick-stream is fundamental)
- Space = emergent visualization (from tick differences)
- Entities = temporal processes (not objects in time)
- **Ontology**: Time generates space

### Why Both Are Valid

- **Chapter 15**: Works computationally, implemented, experimentally validated
- **Doc 49**: Refines ontological status, explains why time ≠ dimension

**The ρ=2.0 signature** (Experiment 50) validates Doc 49: time behaves fundamentally differently from spatial
dimensions.

### Implementation Roadmap

To align Java with Doc 49:

1. **Keep Chapter 15 substrate** (it works!)
2. **Add explicit temporal ordering** (tick-stream as primary)
3. **Treat Position as emergent** (derived from temporal evolution, not fundamental)
4. **Entities as temporal processes** (emphasize `onTick()` pattern over state)

See v2 Ch8 (Integration & Falsification) for detailed roadmap.

---

## 9. References

**Full specification**: See v1/15 for complete original document

**Related theory**:

- **Doc 49**: Temporal Ontology (theoretical apex)
- **Doc 28**: Temporal Surfing Principle (implemented)
- **Doc 29**: Imbalance Theory (implemented)
- **Doc 30**: Collision Persistence Principle (implemented)

**Experiments**:

- **Experiment #15**: 3,960 simulations validating this framework
- **Experiment #50**: ρ=2.0 signature validates Doc 49 refinement

**Implementation**:

- **CLAUDE.md**: Project documentation
- **tick-space-runner**: Java implementation
- **v2 Ch3**: Entity Dynamics (implementation details)
- **v2 Ch8**: Integration & Falsification (roadmap)

---

**Document Status**: REFERENCE (implementation basis)
**Java Status**: IMPLEMENTED
**Theoretical Status**: Superseded by Doc 49 ontologically, but validated computationally
**Experimental Status**: VALIDATED (Experiment #15)
