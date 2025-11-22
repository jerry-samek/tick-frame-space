# Parameter Sweep Experiment Plan

## 1. Objective
Test how agent percept commits depend on:
- **Emission strength** (`alpha_0`, `alpha_1`)
- **Damping** (`gamma`)
- **Agent sampling factor** (`M`)

Goal: Identify regimes where artefacts are strong enough and persistent enough to cross agent salience thresholds.

---

## 2. Parameters to Sweep

### Emission Strength
- `alpha_0`: baseline impulse amplitude
- `alpha_1`: scaling with root state norm
- Suggested values:
  - `alpha_0 ∈ {0.5, 1.0, 2.0}`
  - `alpha_1 ∈ {0.0, 0.5, 1.0}`

### Damping
- `gamma`: dissipative term in wave equation
- Suggested values:
  - `gamma ∈ {0.01, 0.005, 0.001}`

### Agent Sampling
- `M`: downsampling factor (agent reads every M-th tick)
- Suggested values:
  - `M ∈ {1, 2, 4}`

---

## 3. Experimental Grid
Total combinations: 3 × 3 × 3 = 27 runs.

For each run, log:
- **Tick commits:** number and timing
- **Emission strengths:** average and max
- **Agent salience values:** average and max
- **Agent commits:** count and timing

---

## 4. Expected Outcomes

- **High emission strength, low damping, small M:**  
  → Frequent agent commits (artefacts persist and are sampled often).

- **Low emission strength, high damping, large M:**  
  → Few or no agent commits (artefacts dissipate before sampling).

- **Intermediate regimes:**  
  → Occasional commits, salience values near threshold.

---

## 5. Analysis Plan
- Plot agent commit count vs. parameters (`alpha_0`, `gamma`, `M`).
- Identify threshold region where commits begin to appear.
- Compare salience curves across runs to see how artefact visibility scales.

---

## 6. Interpretation
- **Visibility of past events** depends on emission strength, persistence, and sampling frequency.  
- **Refresh stability** is preserved (CFL ≤ 1), but perceptual commits require artefacts above threshold.  
- This demonstrates that *not all past events are observable* — visibility is parameter-dependent.

---

## 7. Next Step
Implement parameter sweep in Python:
- Loop over parameter sets.
- Run simulation for each.
- Collect logs into structured arrays.
- Post-process to generate commit statistics and salience plots.