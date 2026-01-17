# Experiment 51b: Planetary Time Dilation via Clustered Entities

**Status:** Completed experiment  
**Goal:** Determine whether a *cluster of many small entities* with multi‑tick workloads produces a smoother time‑dilation profile γ(r) than the binary cutoff observed in Experiment 51.

---

## 1. Motivation

Experiment 51 attempted to model gravitational time dilation using a single “heavy” entity with a large tick_budget.  
This produced:

- **global saturation**
- **binary behavior** (γ = 1 or γ = 0)
- **no spatial gradient**
- strong dependence on entity ordering

The core flaw:  
A single hypertrophic entity violates the granular ontology of the tick‑frame model.

Experiment 51b introduces two improvements:

1. Replace the single heavy entity with a **planetary cluster** of many small entities.
2. Introduce **multi‑tick BUSY/IDLE workloads** to smooth temporal behavior.

However, 51b still uses a **global scheduler**, so space is not yet represented.

This experiment is a transitional step toward the fully spatial model in Experiment 51c.

---

## 2. Ontological Assumptions

Experiment 51b still inherits the flawed assumption from 51:

- **Space is not represented**.
- Only entities exist; space is implicit.

But 51b introduces two key corrections:

### 2.1 Planet = cluster of many small entities
A planet is represented as:

- thousands of entities
- each with a small tick_budget
- arranged in a disk‑shaped region

This restores **granularity** missing in 51.

### 2.2 Entities have multi‑tick workloads
Each entity:

- enters BUSY when starting a physical tick
- consumes `tick_budget` units of work over multiple substrate ticks
- returns to IDLE when finished

This introduces **temporal smoothing** and avoids instantaneous heavy loads.

---

## 3. Mechanical Model

### 3.1 Planetary cluster
- N entities (e.g., 5000)
- distributed randomly inside a disk of radius R
- each with `tick_budget = B_planet` (e.g., 5)

### 3.2 Light probes
- A set of test entities placed at increasing distances from the planet
- each with `tick_budget = 1`
- used to measure γ_eff(r)

### 3.3 Global scheduler (same as 51)
- One global tick_budget_capacity per substrate tick
- BUSY entities consume capacity first
- Remaining capacity is distributed randomly among IDLE entities

This is the key limitation:  
**No spatial locality.**

---

## 4. Measurement

For each light probe:

\[
\gamma_{\text{eff}} = \frac{\text{ticks\_processed}}{\text{substrate\_ticks\_elapsed}}
\]

We measure γ_eff for probes at distances:

\[
r \in \{15, 20, 25, \dots, 70\}
\]

and analyze:

- monotonicity of γ(r)
- smoothness
- fit to 1/r²

---

## 5. Results Summary

Experiment 51b produced:

- **γ_eff ≈ 0.16 for all probes**
- **no monotonic gradient**
- **poor fit to 1/r²**
- **100% global capacity saturation**

Interpretation:

- The planetary cluster creates a **global load**
- but the global scheduler distributes this load **uniformly**
- so all probes experience the same time dilation

This confirms:

### ✔ Clustering alone is not enough
### ✔ Multi‑tick workloads smooth behavior but do not create geometry
### ❌ No spatial structure emerges without spatial locality
### ❌ Global scheduling destroys gradients

---

## 6. Conclusions

Experiment 51b demonstrates:

### What works
- Replacing a hypertrophic entity with a granular cluster avoids binary cutoff
- Multi‑tick workloads produce smooth γ_eff values
- Time dilation emerges as a global effect

### What fails
- No spatial gradient γ(r)
- No dependence on distance
- No emergent geometry
- No gravitational falloff

### Why it fails
- The scheduler is global
- Space is not represented
- All entities compete in the same global pool

### What 51b teaches us
51b is a **necessary negative result**:

- It shows that clustering and multi‑tick workloads alone do *not* produce gravity
- It isolates the missing ingredient: **locality of capacity**
- It motivates Experiment 51c, where space itself becomes a field of sample‑entities

---

## 7. Role of 51b in the Research Program

Experiment 51b is a transitional experiment:

- **51 → flawed ontology (hypertrophic entity)**
- **51b → granular ontology, but no spatial substrate**
- **51c → full spatial ontology (sample‑entity space)**

51b confirms that:

### Gravity cannot emerge without representing space as a process.

This insight directly motivates the design of Experiment 51c.
