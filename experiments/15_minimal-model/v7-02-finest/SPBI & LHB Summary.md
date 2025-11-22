# SPBI & LHB Summary (v7a Finest Results)

## 📊 Overview
This document summarizes Stability–Probability Balance Index (SPBI) and Long Horizon Boundary (LHB) findings for dimensions 3D, 4D, and 5D in the critical damping boundary region:
- γ ∈ {0.004, 0.0045, 0.00475, 0.005}
- T ∈ {500, 1000}
- α₀ ∈ {0.8, 1.8}
- num_sources ∈ {1, 2, 4}
- geometry = symmetric, phase_offset = 0

---

## 🧮 SPBI Results

| Dimension | γ     | T   | CV   | ρ   | SLF  | SPBI | Anomaly Flag |
|-----------|-------|-----|------|-----|------|------|--------------|
| **3D**    | 0.004 | 500 | >0   | ~0.95 | ~0.05 | computable | — |
|           | 0.004 | 1000| >0   | ~0.95 | ~0.05 | computable | — |
|           | 0.0045–0.005 | 500–1000 | 0 | — | — | — | SAT_CAP (23,530,212.77) |
| **4D**    | 0.004 | 500 | >0   | ~0.94 | ~0.06 | computable | — |
|           | 0.004 | 1000| >0   | ~0.94 | ~0.06 | computable | — |
|           | 0.0045–0.005 | 500–1000 | 0 | — | — | — | SAT_CAP (43,690,666.67) |
| **5D**    | 0.004 | 500 | >0   | ~0.94 | ~0.06 | computable | — |
|           | 0.004 | 1000| >0   | ~0.94 | ~0.06 | computable | — |
|           | 0.0045–0.005 | 500–1000 | 0 | — | — | — | SAT_CAP (64,150,029.91) |

*(Values approximate; SPBI suppressed for SAT_CAP buckets.)*

---

## 📐 Long Horizon Boundary (LHB)

| Dimension | γ = 0.004 | γ = 0.0045 | γ = 0.00475 | γ = 0.005 |
|-----------|-----------|------------|-------------|-----------|
| 3D        | > 1000    | 500 (SAT_CAP) | 500 (SAT_CAP) | 500 (SAT_CAP) |
| 4D        | > 1000    | 500 (SAT_CAP) | 500 (SAT_CAP) | 500 (SAT_CAP) |
| 5D        | > 1000    | 500 (SAT_CAP) | 500 (SAT_CAP) | 500 (SAT_CAP) |

---

## 🔎 Interpretation
- **Critical damping threshold:**  
  Lies sharply between γ = 0.004 (universe‑like) and γ = 0.0045 (SAT_CAP) across all dimensions.  
- **Universe‑like regimes:**  
  γ = 0.004 at T = 500 and 1000 → CV > 0, SPBI computable, variance persists.  
- **Artefact regimes:**  
  γ ≥ 0.0045 at T ≥ 500 → immediate saturation caps, dimension‑specific constants.  
- **Cap constants:**  
  - 3D → 23,530,212.77  
  - 4D → 43,690,666.67  
  - 5D → 64,150,029.91  

---

## 🧭 Next Steps
1. Compute detailed SPBI values for γ = 0.004 buckets (T = 500, 1000).  
2. Add geometry/phase contrasts at γ = 0.004 → compute GPN neutrality.  
3. Document critical boundary curve:  
   - `T_LHB(γ=0.004) > 1000`  
   - `T_LHB(γ=0.0045) = 500`  
4. Aggregate into per‑dimension reports with anomaly flags and verdicts.

---

**Verdicts:**  
- **3D:** Universe‑like at γ = 0.004; artefact caps at γ ≥ 0.0045.  
- **4D:** Same profile; cap constant 43,690,666.67.  
- **5D:** Same profile; cap constant 64,150,029.91.  