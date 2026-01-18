# Test Specification: Dimensional Equivalence Under Explicit Time Dimension

**Version:** 1.0  
**Author:** Tom  
**Purpose:** Verify whether dimensional stability results (1D–5D) remain valid when the system is reformulated as *
*n‑space + explicit tick‑time dimension**.

---

## 1. Objective

Determine whether the stability, variance, and salience behavior observed in the original dimensional experiments remain
consistent when the model is expressed as:

\[
\text{(n spatial dimensions)} + \text{(explicit tick‑time dimension)}
\]

This test evaluates whether tick‑time behaves like a true dimension or whether it is a fundamentally different causal
generator.

---

## 2. Hypothesis

### If tick‑time behaves like a dimension:

- **3D + t** should reproduce the behavior of **4D**
- **4D + t** should reproduce the behavior of **5D**
- **5D + t** should reproduce the behavior expected for **6D+** (trivial stability)

### If tick‑time is a special generator:

- (n + t) systems will diverge from the original (n+1) dimensional behavior
- stability, variance, and salience scaling will not align
- new anomaly classes may appear

---

## 3. Method

### 3.1 Construct an (n + 1)-dimensional substrate

For each \( n \in \{3,4,5\} \):

- Build a substrate with **n spatial dimensions**
- Add **one explicit tick‑time dimension** \( t \)
- Evolve the system using the same update rules as in the original dimensional experiments

### 3.2 Apply identical update rules

Use the same:

- salience propagation
- damping parameters
- horizon limits
- commit rules
- PoF thresholding
- artefact emission
- stability metrics

Only the dimensionality changes.

### 3.3 Measure the same metrics

Record for each run:

- salience growth curves
- coefficient of variation (CV)
- source/geometry independence (ρ)
- commit stability
- horizon behavior
- anomaly types (saturation, overflow, aliasing)

### 3.4 Compare against baseline results

Compare:

- **(3D + t)** vs **original 4D**
- **(4D + t)** vs **original 5D**
- **(5D + t)** vs **expected 6D+**

Look for:

- matching stability regimes
- matching variance envelopes
- matching salience scaling laws
- matching anomaly patterns

---

## 4. Success Criteria

### Tick‑time behaves like a dimension if:

- (3D + t) ≈ 4D
- (4D + t) ≈ 5D
- (5D + t) ≈ 6D
- variance and salience curves align within tolerance
- no new anomaly classes appear

### Tick‑time is a special generator if:

- any (n + t) system diverges from the original (n+1) behavior
- stability does not shift as expected
- variance envelopes differ significantly
- salience scaling laws break
- new anomaly types appear

---

## 5. Deliverables

- Full logs for each (n + t) run
- Overlay plots comparing (n + t) vs original (n+1)
- Summary table of CV, ρ, stability class, and anomalies
- Final conclusion: **dimensional equivalence** vs **generator distinction**

---

## 6. Interpretation Checklist

Use this checklist to interpret results:

### ✔ Stability Comparison

- [ ] Does (3D + t) show the same stability regime as 4D?
- [ ] Does (4D + t) match 5D stability?
- [ ] Does (5D + t) collapse into trivial 6D‑like stability?

### ✔ Variance & Salience

- [ ] Are CV curves within the same envelope as the baseline?
- [ ] Does salience follow the same scaling law?
- [ ] Are growth curves monotonic or do they diverge?

### ✔ Anomaly Patterns

- [ ] Do anomalies match the original dimension (saturation, overflow, aliasing)?
- [ ] Are there any new anomaly classes?
- [ ] Are anomalies operational or physical?

### ✔ Horizon & Visibility

- [ ] Does horizon behavior match the baseline dimension?
- [ ] Any unexpected aliasing or recession effects?

### ✔ Structural Behavior

- [ ] Does adding t shift the system exactly one dimension up?
- [ ] Or does it produce qualitatively different behavior?

### ✔ Final Determination

- [ ] **Tick‑time behaves like a dimension**
- [ ] **Tick‑time is a special generator**
- [ ] **Inconclusive — requires further testing**

---

## 7. Summary

This test determines whether the dimensional closure observed in earlier experiments (4D–5D stability lock) is a
property of **dimensionality itself**, or a property of **substrates under tick‑time evolution**.
The result directly informs whether:

- 3D is a true spatial dimension, or
- a **temporal condensate** of a higher‑dimensional substrate.

---

## 8. Experimental Results (COMPLETED: 2026-01-15)

### 8.1 Status

**EXPERIMENT COMPLETE**
**Date:** 2026-01-15
**Experiment ID:** #50
**Results Document:** Theory Doc 50_01 - Experimental Results: Dimensional Equivalence Rejection

### 8.2 Verdict

**GENERATOR DISTINCTION CONFIRMED**

The hypothesis that (n spatial dimensions + explicit time) behaves like (n+1) spatial dimensions is **decisively
rejected**.

**Test Results:**

- **0/6 dimensional equivalence tests passed** (0% success rate)
- **1,095 configurations tested** (15 baseline + 1,080 variants)
- **ALL (n+t) systems diverge** from (n+1) baseline behavior

### 8.3 Checklist Completion

#### ✔ Stability Comparison

- [✗] Does (3D + t) show the same stability regime as 4D? **NO** - saturated commits (99%) vs moderate (51%)
- [✗] Does (4D + t) match 5D stability? **NO** - amplified salience vs controlled
- [✗] Does (5D + t) collapse into trivial 6D-like stability? **NO** - still shows 12x amplification

#### ✔ Variance & Salience

- [✗] Are CV curves within the same envelope as the baseline? **NO** - inverted pattern (commit collapses, salience
  expands)
- [✗] Does salience follow the same scaling law? **NO** - ρ=2.0 vs ρ=1.5
- [✗] Are growth curves monotonic or do they diverge? **DIVERGE** - extreme amplification (up to 1,675x mean, 9,941x
  max)

#### ✔ Anomaly Patterns

- [✗] Do anomalies match the original dimension? **NO** - saturation vs selective behavior
- [✓] Are there any new anomaly classes? **YES** - temporal accumulation/ratchet effect
- [✓] Are anomalies operational or physical? **PHYSICAL** - from causal structure

#### ✔ Horizon & Visibility

- [−] Does horizon behavior match the baseline dimension? **NOT TESTED** in this experiment
- [−] Any unexpected aliasing or recession effects? **NOT TESTED** in this experiment

#### ✔ Structural Behavior

- [✗] Does adding t shift the system exactly one dimension up? **NO** - fundamentally different behavior
- [✓] Or does it produce qualitatively different behavior? **YES** - amplification regime with ρ=2.0 signature

#### ✔ Final Determination

- [✗] **Tick-time behaves like a dimension** - REJECTED
- [✓] **Tick-time is a special generator** - CONFIRMED
- [✗] **Inconclusive — requires further testing** - Not needed, result is decisive

### 8.4 Key Findings

**1. The ρ=2.0 Signature (Smoking Gun)**

Most compelling quantitative evidence:

**Pure spatial dimensions:**

- 3D: ρ = 1.503
- 4D: ρ = 1.532
- 5D: ρ = 1.571
- **Mean: ρ ≈ 1.5** (sub-quadratic scaling)

**ALL (n+t) systems:**

- 2D+t: ρ = 1.999
- 3D+t: ρ = 2.002
- 4D+t: ρ = 2.001
- **Mean: ρ = 2.0** (quadratic scaling)

**Interpretation:** Time acts as **coherence amplifier** (energy accumulates) rather than **dilution dimension** (energy
spreads). This is a **universal signature** independent of all tested parameters (α, γ, geometry, time horizon).

**2. Salience Amplification**

- (2D+t) vs 3D: **1,675x mean**, **9,941x max** amplification
- Most extreme at low dimensions, persists at higher dimensions
- Example: 3D max salience ~10, 2D+t max salience >100,000

**3. Variance Inversion**

- Commit rate variance: **collapses** from CV=0.64 to CV=0.04 (93% reduction)
- Salience variance: **expands** from CV=1.03 to CV=2.13 (107% increase)
- System transitions from selective to saturated dynamics

**4. Physical Mechanism: The Ratchet Effect**

- Time is strictly ordered (tick n → tick n+1 only)
- Temporal derivatives create **constructive interference** along time axis
- Energy **accumulates** rather than dilutes
- One-way causal flow ≠ bidirectional spatial diffusion

### 8.5 Convergent Validation with Experiment 44

**Experiment 44 (kinematic constraints)** independently confirms the same asymmetry:

**44 Findings:**

- Forward pitch (toward viewer): 0% success - **PHYSICALLY IMPOSSIBLE** (can't exceed 1 tick/tick)
- Backward pitch (away from viewer): 93% success - energy-limited
- **Asymmetry ratio: 933x**
- Root cause: Temporal velocity constraint v ≤ 1 tick/tick

**50 Findings:**

- Source scaling: ρ=2.0 (quadratic) vs ρ=1.5 (sub-quadratic)
- **Amplification ratio: 1,675x** mean
- Root cause: Causal ordering creates ratchet effect

**Synthesis:** Both experiments reveal **the same constraint from different angles**:

- Experiment 44: Can't speed up, only slow down (kinematics)
- Experiment 50: Energy accumulates, doesn't dilute (dynamics)

### 8.6 Theoretical Implications

**Validates Theory Doc 49 (Temporal Ontology):**

✓ **Temporal Primacy** - Time is fundamentally different from space
✓ **Tick-Stream as Substrate** - Time is generator, not coordinate
✓ **Space as Emergent** - Space has no causal power
✓ **Dimensional Closure (4D-5D)** - Refers to **spatial dimensions only**
✓ **3D Space + Time ≠ 4D Spacetime** - Not Minkowski spacetime

**The ρ=2.0 signature is proposed as a fundamental law:**

**Law of Temporal Scaling**: In any system where time is treated as an explicit dimension while preserving causal
ordering, source scaling will converge to ρ=2.0 (quadratic) rather than ρ≈1.5 (sub-quadratic) characteristic of pure
spatial dimensions.

### 8.7 Implementation Guidance

**Current Java Implementation (VALIDATED as correct):**

- Uses tick-based evolution ✓
- Does NOT treat time as coordinate dimension ✓
- Time remains evolution parameter, not Position component ✓

**Confirmed correct approach:**

- Keep `TickTimeConsumer<E>` pattern
- Do NOT add time to `Position` record
- Dimensional closure (4D-5D) refers to spatial dimensions only

### 8.8 References

**Detailed results:** Theory Doc 50_01
**Experimental data:** `experiments/50_dimensional_equivalence_explicit_time/EXPERIMENT_RESULTS.md`
**Kinematic validation:** Experiments #44 series (especially 44_03, 44_04)
**Theoretical foundation:** Theory Doc 49 (Temporal Ontology)

---

**Status:** COMPLETE
**Conclusion:** Time is a **special generator**, not a dimension. The ρ=2.0 signature is the mathematical fingerprint of
temporal causality.
