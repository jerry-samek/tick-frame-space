# Threshold Surface Report
## Consolidated Summary of Experiments

**Date**: 2025-11-17  
**Researcher**: Tomáš  
**Scope**: Multi-parameter exploration of time–visualization model thresholds

---

## 1. Objective
To determine the **critical emission strength (α₀)** at which agent percept commits begin to appear, and to map how this threshold depends on:
- **Damping (γ)**
- **Sampling rate (M)**

This validates the principle that **time perception is salience-dependent, not absolute**.

---

## 2. Experimental Phases

### Phase 1: Initial Sweep
- Range: α₀ = 1.8 → 2000  
- Fixed γ = 0.001, M = 1  
- **Finding:** Commits begin at α₀ ≈ 1.90.  
- Scaling: commit frequency increases rapidly with α₀.

### Phase 2: Threshold Surface Mapping
- Range: α₀ = 1.6 → 5.0  
- γ ∈ {0.01, 0.005, 0.001, 0.0005}  
- M ∈ {1, 2, 4}  
- **Finding:**  
  - No commits at α₀ ≤ 1.7.  
  - Onset at α₀ ≈ 1.8–1.9 for γ ≤ 0.001, M = 1.  
  - Higher damping or sparse sampling pushes threshold upward.  
  - At α₀ ≥ 5.0, commits appear across all tested regimes.

### Phase 3: Refined Boundary Sweep
- Resolution: Δα₀ = 0.05 in [1.6, 2.2]  
- Total runs: 156  
- **Finding:**  
  - Precise onset at **α₀ ≈ 1.85–1.90** for γ = 0.001, M = 1.  
  - Threshold shifts to α₀ ≈ 2.15 for γ = 0.005.  
  - No commits for γ = 0.01 up to α₀ = 2.2.  
  - Sparse sampling (M = 2, 4) prevents commits even at α₀ = 2.2.

---

## 3. Key Results

### Critical Threshold
- **α₀ ≈ 1.85–1.90** (γ = 0.001, M = 1, T = 100s)

### Damping Dependence
- Higher γ dissipates artefacts faster → requires stronger emissions.  
- Threshold drops sharply between γ = 0.005 and γ = 0.001.

### Sampling Dependence
- M = 1 (every tick): commits at α₀ ≈ 1.90.  
- M = 2: final Ψ reduced ~35%, no commits up to α₀ = 2.2.  
- M = 4: final Ψ reduced ~69%, no commits up to α₀ = 2.2.

### Onset Curve
- Sharp transition over Δα₀ ≈ 0.05.  
- Linear scaling of Ψ with α₀:  
  \[
  Ψ(α₀) ≈ 2.03·α₀ - 2.68
  \]

---

## 4. Physical Interpretation
- **Accumulation (α₀):** stronger emissions inject more artefact energy.  
- **Dissipation (γ):** damping removes energy; weaker γ allows persistence.  
- **Sampling (M):** sparse sampling misses transient artefacts, reducing integration.  
- **Threshold condition:** commits occur when accumulated salience Ψ ≥ 1.01 before damping erases signals.

---

## 5. Implications
- Time perception in the model is **not absolute**: visibility of past events depends on emission strength, damping, and sampling.  
- The system exhibits a **phase transition** between invisible and visible histories.  
- The sharpness of the onset validates the salience-based framing of time.

---

## 6. Next Steps
1. **Ultra-fine resolution sweep** (Δα₀ = 0.01) around [1.80, 1.95].  
2. **Extended time horizon** (T = 200–500s) to test late commits.  
3. **Dynamic analysis** of Ψ(t) buildup curves.  
4. **Multi-source scenarios** to study interference and superposition.  
5. **Analytical model** for α₀_threshold(γ, M, T).

---

## 7. Conclusion
Across all experiments, the **critical onset threshold** is consistently identified at:

> **α₀ ≈ 1.85–1.90 (γ = 0.001, M = 1)**

This demonstrates that the time–visualization model enforces a **salience-based perceptual boundary**, confirming that *not all past events are observable* — visibility is parameter-dependent.