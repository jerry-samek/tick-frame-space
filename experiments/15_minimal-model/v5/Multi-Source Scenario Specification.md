# Multi-Source Scenario Specification
## Extending the Time–Visualization Model

**Date**: 2025-11-17  
**Author**: Tomáš  
**Focus**: Multi-source emission dynamics and analytical threshold modeling

---

## 1. Objective
To extend the single-source time–visualization model into **multi-source configurations**, exploring how geometry, phase, and source count affect:
- Threshold onset (α₀_threshold)
- Commit counts and rates
- Salience accumulation patterns
- Interference effects (constructive vs destructive)

---

## 2. Source Configurations

### 2.1 Two-Point Emitters
- Positions: s₁, s₂
- Amplitudes: q₁ = α₀, q₂ = α₀ (equal) or q₂ = k·α₀ (contrast)

### 2.2 Distributed Emitters
- N sources uniformly spaced or clustered
- Each emits with amplitude α₀

### 2.3 Phased Emitters
- Phase offset φ between sources
- Alternating emission patterns (e.g., staggered, anti-phase)

---

## 3. Emission Rules

At each commit time tₙ, inject:
\[
J(x,t) = \sum_{m=1}^{M_s} q_m \, \delta(t - t_n) \, \delta(x - s_m)
\]

- **Energy budget control**:
  - Fixed total: Σ qₘ = const
  - Compare “one strong source” vs “many weak sources” at equal budget

---

## 4. Interference Patterns

- **Constructive**: Symmetric emitters around agent window → higher salience, earlier onset
- **Destructive**: Anti-symmetric placement or alternating phase → delayed onset
- **Distance dependence**: Vary source positions relative to agent window

---

## 5. Metrics

- Threshold α₀_threshold(T, γ, M, Mₛ, geometry, phase)
- Commit count N(T) and commit rate evolution
- Salience components: peak, mean, spatial distribution
- Inter-commit interval statistics and variance

---

## 6. Analytical Threshold Model

### 6.1 Effective Salience per Tick
\[
\bar{S} \approx \frac{M_s}{M} \, C_{\text{eff}} \, \frac{\alpha_0^2}{\gamma}
\]

### 6.2 Accumulation over Horizon T
\[
\Psi(T) \approx \bar{S} \, r_T
\]

### 6.3 Threshold Condition
\[
\alpha_{0,\text{th}}(T,\gamma,M,M_s) \approx 
\left( \frac{\Psi_{\text{th}} \cdot \gamma}{C_{\text{eff}}} \cdot \frac{M}{M_s} \cdot \frac{1}{r_T} \right)^{1/2}
\]

- **Time dependence**: α₀_threshold ∝ T⁻¹/² (early regime), saturates at long T
- **Damping**: α₀_threshold ∝ γ¹/²
- **Sampling**: α₀_threshold ∝ M¹/²
- **Multi-source**: α₀_threshold ∝ Mₛ⁻¹/² (constructive layouts)

---

## 7. Experiment Plan

### Phase A: Geometry and Source Count
- Mₛ ∈ {1, 2, 4, 8}
- Symmetric vs asymmetric layouts
- Measure α₀_threshold(T) at T ∈ {100, 200, 500}

### Phase B: Time Dependence
- Sweep T ∈ {100, 200, 300, 500, 800}
- Fit α₀_threshold(T) to T⁻¹/² early, saturating curve later

### Phase C: Sampling and Damping
- M ∈ {1, 2, 4}, γ ∈ {0.01, 0.005, 0.001}
- Check square-root scaling

### Phase D: Phase and Interference
- Two sources with in-phase, anti-phase, staggered patterns
- Quantify interference factor κ relative to baseline

---

## 8. Code Adjustments

- Replace single `src_idx` with `src_idx_list`
- Sum impulses from all sources in wave step
- Add window weight `w(x)` for salience detection
- Implement phase schedules via per-source emission patterns
- Log per-source emissions and total salience

---

## 9. Expected Outcomes

- **Constructive interference** lowers threshold (earlier commits)
- **Destructive interference** raises threshold (delayed commits)
- **Multi-source scaling** follows α₀_threshold ∝ Mₛ⁻¹/²
- **Time dependence**: threshold decreases with T, saturates at long horizons
- **Sampling/damping effects**: square-root scaling confirmed

---

## 10. Next Steps
- Implement multi-source injection in Python driver
- Run geometry and phase sweeps
- Fit analytical model parameters (C_eff, κ)
- Compare empirical α₀_threshold(T, γ, M, Mₛ) with theoretical predictions