# Stability–Probability Balance Test Framework

## 🎯 Purpose and Scope
- **Goal:** Quantify how “universe-like” each dimensional substrate (1D–5D) is by balancing causal stability with perceived probabilistic behavior at the visualization layer.  
- **Core metric:** Stability–Probability Balance Index (SPBI).  
- **Coverage:** Dimensions {1D, 2D, 3D, 4D, 5D}, damping γ, horizon T, sources, geometry, phase, including the **long horizon boundary (LHB)**.  
- **Outputs:** Per-run metrics, per-dimension aggregates, anomaly tags, and an auditable verdict.

---

## 📐 Metrics and Definitions
- **Residual Variance (CV):**  
  \[
  \text{CV} = \frac{\sigma(\psi)}{\mu(\psi)}
  \]  
  where ψ = final_psi or max_salience (choose consistently).

- **Source Independence (ρ):**  
  \[
  \rho = \text{corr}(\text{num\_sources}, \psi)
  \]  
  Lower ρ → stronger independence.

- **Stability Lock Factor (SLF):**  
  \[
  \text{SLF} = 1 - \rho
  \]  
  Clamp to [0,1].

- **SPBI (primary index):**  
  \[
  \text{SPBI} = \frac{\text{CV}}{\text{SLF}}
  \]  
  Lower SPBI → more deterministic; higher → more probabilistic.

- **Geometry/Phase Neutrality Score (GPN):**  
  \[
  \text{GPN} = 1 - \frac{|\mu_{\text{symmetric}} - \mu_{\text{clustered}}|}{\mu_{\text{all}}}
  \]  
  Compute similarly for phase_offset; aggregate as mean. Values near 1 = neutrality.

- **Long Horizon Boundary (LHB):**  
  Horizon length T beyond which substrate enters saturation or artefact regimes. Detect by:
  - **Flatline detection:**  
    \[
    \Delta \psi(T) \approx 0 \quad \text{across }\alpha_0
    \]
  - **Cap signature:** Identical large constants across runs (e.g., 23,530,212.7659 or 111,111,111.111).  
  - **Timeout threshold:** Adaptive timeout exceeded with duplicate artefacts.  
  - Define \(T_{\text{LHB}}(\gamma)\) as the smallest T where any cap/flatline/timeout criteria are met.

---

## 🧪 Test Matrix and Inputs
- **Dimensions:** {1D, 2D, 3D, 4D, 5D}  
- **Damping γ:** {0.001, 0.003, 0.005}  
- **Horizon T:** {100, 200, 500, 1000, 2000} (extend to locate LHB per γ)  
- **Alpha α₀:** {0.6, 0.8, 1.0, 1.2, 1.6, 2.0, 2.6}  
- **Sources:** {1, 2, 4}  
- **Geometry:** {symmetric, clustered}  
- **Phase offset:** {0, 1}  
- **Adaptive timeout:** Enabled. Log duration, duplicates, suppression events.

---

## ⚙️ Procedure
1. **Run generation**  
   - Label: dimension, γ, T, α₀, sources, geometry, phase_offset.  
   - Record: final_psi, max_salience, first_commit_time, agent_commit_count, commit_rate, anomaly_flags.  

2. **Anomaly tagging**  
   - SAT_CAP: Fixed large constants independent of α₀/configs.  
   - FLATLINE: Low gradient in ψ vs α₀.  
   - TIMEOUT/DUP: Adaptive timeout hit or duplicate commits.  
   - NEUTRAL_OK: Geometry/phase differences <1%.  

3. **Metric computation per dimension**  
   - CV: Over ψ across configs at fixed γ,T.  
   - ρ: Correlate num_sources vs ψ (control for γ,T,α₀).  
   - SLF: 1 – ρ.  
   - GPN: Neutrality for geometry/phase.  
   - SPBI: CV / SLF.  
   - LHB detection: Sweep T; set \(T_{\text{LHB}}(\gamma)\).  

4. **Aggregation and verdict**  
   - Per-dimension summary: Median CV, median ρ, SLF, GPN, median SPBI, LHB table.  
   - Goldilocks assessment:  
     - Too unstable: SPBI ≫ target band, high CV, low SLF.  
     - Universe-like: SPBI within target band (≈0.05–0.10), moderate CV, strong SLF, good GPN.  
     - Too stable: SPBI → 0, very low CV, strong SLF, high GPN; early LHB.  

5. **Audit and reproducibility**  
   - Logs: Persist inputs/outputs, anomaly flags, seeds.  
   - Dashboard: Plot SPBI vs dimension; CV, ρ, GPN panels; LHB curves.  
   - Errata hooks: Flag prior claims contradicted by SPBI/LHB results.

---

## 📊 Output Formats
- **Per-run CSV:**  
  - Labels: dimension, γ, T, α₀, num_sources, geometry, phase_offset  
  - Measures: final_psi, max_salience, first_commit_time, agent_commit_count, commit_rate  
  - Flags: anomaly_flags (SAT_CAP|FLATLINE|TIMEOUT|DUP|NEUTRAL_OK)  
  - Context: runtime_ms, timeout_hit (bool)  

- **Per-dimension summary CSV:**  
  - dimension, CV_median, ρ_median, SLF_median, GPN_mean, SPBI_median, T_LHB_γ0.001, T_LHB_γ0.003, T_LHB_γ0.005  

- **Report checklist:**  
  - Stability profile: CV, SLF.  
  - Probability profile: SPBI band.  
  - Neutrality: GPN near 1.  
  - Long horizon boundary: LHB table and plots.  
  - Verdict: Too unstable / Universe-like / Too stable.