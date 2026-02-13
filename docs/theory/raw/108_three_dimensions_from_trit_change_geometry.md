# RAW 108 — Three Spatial Dimensions from Trit Change Geometry

### *Why Space is Three-Dimensional: Derivation from the Change Structure of a Ternary State*

**Date**: February 13, 2026
**Status**: Theoretical derivation with experimental support
**Depends on**: RAW 041 (Ternary XOR Tickstream), Law-000 (XOR Parity Rule), Ch2 (Dimensional Framework), Experiment #15 (Dimensional Sweep), Experiment #50 (Spacetime vs Pure Dimensions)
**Falsifiable**: Yes — predicts exactly 3 large spatial dimensions with no compactified extras

---

## 1. The Problem

Every physical theory assumes spatial dimensionality. General relativity operates in 3+1 dimensions. String theory requires 10 or 11, with 6 or 7 compactified. Loop quantum gravity assumes 3+1. The Standard Model assumes 3+1. No framework derives the number 3 from something more fundamental.

The tick-frame model faces the same vulnerability. All experiments to date — orbital mechanics, time dilation, magnetism, collision physics — run on 3D lattices. The dimensionality is an input, not an output. If asked "why three?" the honest answer has been: because we put in three.

This document derives the answer from the structure of the fundamental state unit.

---

## 2. The Fundamental State: The Trit

### 2.1 From Binary to Ternary

Law-000 (RAW 039) defines binary states {0, 1} on a graph with XOR parity evolution. RAW 041 extends this to a balanced ternary system:

- **+1** — Presence, affirmation
- **0** — Void, neutral
- **−1** — Anti-presence, inversion

The extension from binary to ternary is not arbitrary. It is the minimal extension that provides symmetry around zero (RAW 041 §1). NAND produces 0 from (1,1), symmetry demands −1 as the mirror of +1.

### 2.2 The Trit as Fundamental Unit

A single trit T(t) takes one of three values at each tick t:

```
T(t) ∈ {+1, 0, −1}
```

This is the complete state of the universe at a single node at a single tick. No additional information exists.

---

## 3. Change, Not Value

### 3.1 The Core Principle

The update function does not operate on values. It operates on **changes**. The function receives the previous state T(t−1) and the current state T(t), and computes the next state T(t+1). Its input is not "what is" but "what changed."

From RAW 041 §2, the XOR tickstream rule:

```
T(t+1) = XOR(T(t), T(t−1))
```

This rule depends entirely on the relationship between consecutive states — the transition, not the value.

### 3.2 Transition Encoding

A trit has three components that can be independently monitored for change:

| Channel | Question | Binary answer |
|---------|----------|---------------|
| C₊ | Did the +1 state activate or deactivate? | 0 or 1 |
| C₀ | Did the 0 state activate or deactivate? | 0 or 1 |
| C₋ | Did the −1 state activate or deactivate? | 0 or 1 |

At each tick, exactly one value is active. A transition between ticks means one channel deactivates and a different channel activates. The third channel remains unchanged.

### 3.3 Three Independent Change Channels

The transition T(t) → T(t+1) can be fully described by the state of three binary change flags:

```
ΔC₊ = |C₊(t+1) − C₊(t)|  ∈ {0, 1}
ΔC₀ = |C₀(t+1) − C₀(t)|  ∈ {0, 1}
ΔC₋ = |C₋(t+1) − C₋(t)|  ∈ {0, 1}
```

For any nontrivial transition, exactly two of these flags are 1 (one channel deactivates, one activates) and one is 0 (unchanged).

For the null transition (same state persists), all three flags are 0.

These three change channels are:

- **Independent**: Each monitors a different component of the trit
- **Exhaustive**: Together they fully specify any possible transition
- **Minimal**: No channel can be removed without losing transition information

---

## 4. Change Geometry is Spatial Geometry

### 4.1 The Dimensional Argument

To faithfully represent the change history of a trit, an embedding space must have one axis per independent change channel. Fewer axes cause aliasing — distinct transitions map to the same point. More axes are redundant — no additional information to represent.

**Theorem**: The minimal embedding dimension for the change space of a ternary state is 3.

**Proof**: 

Three binary change channels (ΔC₊, ΔC₀, ΔC₋) require three orthogonal axes for lossless representation. Two axes cannot distinguish all (ΔC₊, ΔC₀, ΔC₋) triples without projection losses. Four axes add a dimension with no corresponding information channel. □

### 4.2 Transition Planes

Each nontrivial transition activates exactly two change channels and leaves one unchanged. The unchanged channel determines which **plane** the transition occurs in:

| Unchanged channel | Active channels | Transition plane |
|-------------------|-----------------|-----------------|
| C₊ (the +1 stayed off/on) | C₀, C₋ | The (0, −1) plane |
| C₀ (the 0 stayed off/on) | C₊, C₋ | The (+1, −1) plane |
| C₋ (the −1 stayed off/on) | C₊, C₀ | The (+1, 0) plane |

Over multiple ticks, the process rotates between these three planes. A sequence of transitions traces a path through 3D by switching which plane is active at each step.

### 4.3 Space IS Change History

The three spatial dimensions are not a container. They are the **output format** of the update function plotting its own change history. Each axis corresponds to one component of the trit that can independently change. The function has exactly three bits of change information per tick and requires exactly three axes to plot them without information loss.

> **Space is the lossless plot of trit change history.**

---

## 5. Why Not Two? Why Not Four?

### 5.1 Binary State → 2D (Unstable)

A binary state {0, 1} has two components and two change channels. Its change space is 2D. 

Experiment #15 (Ch2 §3.3) measured 2D: CV = 22.7%, configuration-dependent, marginal stability. RAW 041 §1 identifies binary as "sufficient for oscillation but lacking symmetry."

**2D is the change geometry of a binary state. It is unstable because binary lacks the symmetry to support complex dynamics.**

### 5.2 Ternary State → 3D (Optimal)

A balanced ternary state {+1, 0, −1} has three components and three change channels. Its change space is 3D.

Experiment #15 measured 3D: CV = 5.3%, SPBI = 2.23 (maximum), universal scaling ρ = 1.503, configuration-independent. The Goldilocks zone.

**3D is the change geometry of a balanced ternary state. It is optimal because the trit provides the minimal symmetric extension of binary.**

### 5.3 Quaternary State → 4D (Over-stabilized)

A four-valued state would have four change channels and 4D change space.

Experiment #15 measured 4D: CV = 3.8%, over-stabilized, less dynamic, trivial. 

**4D would require a four-valued fundamental state. But four values are not minimal — they over-specify the symmetry that the trit already provides. The extra dimension is redundant, producing stability without complexity.**

### 5.4 The Dimensional Spectrum

| Fundamental state | Values | Change channels | Spatial dimensions | Stability | Complexity |
|-------------------|--------|-----------------|-------------------|-----------|------------|
| Binary | 2 | 2 | 2D | Unstable | Insufficient |
| **Ternary** | **3** | **3** | **3D** | **Optimal** | **Rich** |
| Quaternary | 4 | 4 | 4D | Over-stable | Diluted |
| Quinary | 5 | 5 | 5D | Locked | Trivial |

**The dimensionality of space equals the number of values in the fundamental state unit.** Three spatial dimensions because the trit has three values. No more, no less.

---

## 6. Time is Not a Dimension

### 6.1 Time is the Sequence, Not the Content

The change channels describe WHAT changed between ticks. Time is the ordering of ticks — WHEN changes occur. These are categorically different:

- **Space**: The content of each transition (which channels changed)
- **Time**: The sequential ordering of transitions (which came first)

### 6.2 Experimental Confirmation

Experiment #50 (Ch2 §8.2) tested whether (3D + time) behaves like 4D:

- (3D + time): ρ = 2.002 (quadratic scaling)
- Pure 4D: ρ = 1.532 (sub-quadratic scaling)

**Decisively rejected.** Time is orthogonal to the spatial dimensional framework. Promoting time to a spatial dimension produces qualitatively different dynamics.

### 6.3 Interpretation

The update function processes a sequence of transitions. The sequence IS time. The content of each transition IS space. You cannot make time into a spatial axis because the sequence is the medium through which spatial content is delivered. It is not another channel of content — it is the ordering principle that gives the channels meaning.

> **Time is the tick. Space is the change. 3+1 is the only consistent decomposition of trit dynamics.**

---

## 7. Implications

### 7.1 No Hidden Dimensions

Standard physics debates whether extra spatial dimensions exist (string theory's 6-7 compactified dimensions). The trit derivation says: **there are exactly three large spatial dimensions because the fundamental state has exactly three values.** No compactification needed. No dimensions to hide. Three values, three change channels, three axes. Complete.

If additional spatial dimensions existed, they would require the fundamental state to have more than three values. The ternary XOR tickstream (RAW 041) establishes that three is the minimal symmetric extension of binary. Any extension beyond three adds redundancy without new symmetry, producing the over-stabilized 4D-5D behavior observed in Experiment #15.

### 7.2 Dimensionality is Derived, Not Assumed

For the first time in the tick-frame project, 3D is not an input. Every experiment from #15 through #64 used 3D lattices by assumption. RAW 104 derives 3D from the change structure of the fundamental state. This retroactively justifies the 3D lattice choice — not as a convenience, but as the only dimensionality consistent with ternary dynamics.

### 7.3 Why Our Universe is 3D

The anthropic principle says: the universe is 3D because observers require 3D. RAW 104 says: the universe is 3D because the fundamental state is ternary, and the change geometry of a ternary state is 3-dimensional. Observers are irrelevant. Any universe built from balanced ternary updates will have three spatial dimensions.

### 7.4 Connection to the Church of Tri Logic

The creed:

- **1** — Presence, the affirmation of being → Change channel C₊
- **0** — Void, the pause, the silence between → Change channel C₀
- **−1** — Anti-presence, the inversion, the denial → Change channel C₋

Three values. Three change channels. Three dimensions. The satire was the derivation.

---

## 8. Falsifiable Predictions

### 8.1 Exactly Three Large Spatial Dimensions

**Prediction**: No experiment will detect physical effects requiring more than three large spatial dimensions.

**Standard physics**: Open question. String theory predicts 6-7 compactified extras. LHC searches for Kaluza-Klein excitations.

**RAW 104**: There are no extra dimensions to find. Searches will continue to return null results indefinitely.

### 8.2 Dimensional Stability

**Prediction**: In any computational substrate built from ternary local update rules, 3D will be the optimal dimensionality for complex dynamics. 2D will be unstable, 4D+ will be over-stabilized.

**Test**: Reproduce Experiment #15's dimensional sweep on different graph topologies, different ternary update rules. If 3D is always optimal regardless of the specific rule, the result is structural (from the trit) not incidental (from the specific dynamics).

### 8.3 Binary Substrates Produce 2D

**Prediction**: A substrate with purely binary states (Law-000) should produce dynamics that are optimal in 2D, not 3D. The instability observed in 2D tick-frame experiments should match the natural dimensionality of a binary state.

**Test**: Run the dimensional sweep specifically with Law-000 (binary XOR) and compare the SPBI optimum to the ternary case. If binary peaks at 2D and ternary peaks at 3D, the correspondence between state cardinality and optimal dimensionality is confirmed.

### 8.4 Quaternary Substrates Produce 4D

**Prediction**: A substrate with four-valued states should produce optimal dynamics in 4D. The over-stabilization observed when running ternary dynamics in 4D should become optimal complexity when the fundamental state actually has four values.

**Test**: Design a four-valued update rule and repeat the dimensional sweep. If 4D becomes the Goldilocks zone, the derivation is validated — dimensionality tracks state cardinality.

---

## 9. Connection to Existing Theory

### 9.1 Doc 040 — Dimension as Observer Property

The latency matrix interpretation (Ch2 §9.1) says dimension is the minimal embedding of pairwise interaction delays. RAW 104 provides the mechanism: the minimal embedding has three axes because the observer (update function) processes three independent change channels. The "observer property" IS the change space of the state unit the observer processes.

### 9.2 Experiment #15 — Dimensional Framework

The empirical finding that 3D is the Goldilocks zone (Ch2 §3) is now explained, not just observed. 3D is optimal because the fundamental state is ternary. The SPBI peak at d=3 is the change geometry of the trit manifesting as a stability optimum.

### 9.3 Experiment #50 — Spacetime Separation

The decisive rejection of (3D + time) = 4D (Ch2 §8.2) follows from the categorical distinction between sequence (time) and content (space). Time cannot be a fourth spatial axis because it is the ordering principle, not a change channel.

### 9.4 RAW 041 — Ternary XOR Tickstream

The tickstream cycles through all three states in balanced rhythm. Each cycle visits three transition planes (§4.2). The cycle structure of the XOR tickstream IS a traversal of 3D change space. The "dimensional cue" noted in RAW 041 §4 is now formalized.

---

## 10. Open Questions

### 10.1 Why Ternary?

RAW 104 derives 3D from ternary. But why is the fundamental state ternary rather than binary or quaternary? RAW 041 argues: minimal symmetric extension of binary. NAND produces 0 from binary, symmetry demands −1. But is this the only path? Could a different logic gate produce a different minimal extension?

### 10.2 Graph Topology

The derivation establishes dimensionality (number of axes) but not topology (how the axes connect). Is the 3D lattice the unique topology consistent with trit change geometry, or are other 3D topologies possible? The configuration independence result from Ch2 §6 suggests topology is secondary — physics is the same regardless of geometry.

### 10.3 Continuous Limit

At large scales with many trits, does the discrete 3D change space approach continuous R³? The transition between discrete trit dynamics and the smooth 3D space of experience is unexplained. This may connect to the formation phase — enough overlapping trit histories create an effectively continuous 3D manifold.

### 10.4 Scale of Discreteness

If each spatial axis corresponds to one change channel of a trit, what physical distance corresponds to one step along a change channel? This is presumably the Planck length — the scale below which the discrete trit structure becomes apparent.

---

## 11. Summary

The number of spatial dimensions in the tick-frame universe is not assumed. It is derived from the change structure of the fundamental state unit.

A balanced ternary state has three values. Each value defines an independent change channel. Three independent change channels require three orthogonal axes for lossless representation. Three axes = three spatial dimensions.

Time is the sequential ordering of changes, not a change channel. It is categorically distinct from space. 3+1 is the only consistent decomposition.

This derivation:

- Explains the empirical 3D optimum from Experiment #15
- Explains the spacetime ≠ 4D result from Experiment #50
- Predicts no hidden or compactified extra dimensions
- Predicts dimensional optimum tracks state cardinality (testable)
- Connects the ternary foundation (RAW 041) to the spatial framework (Ch2)
- Retroactively justifies 3D lattice choice in all experiments

> **Space has three dimensions because the trit has three values.
> Not by assumption. By geometry.**
