# SPBI & LHB Summary (v7a Fine Results)

## 📊 Overview
This document summarizes Stability–Probability Balance Index (SPBI) and Long Horizon Boundary (LHB) findings for dimensions 3D, 4D, and 5D using:
- γ ∈ {0.001, 0.003, 0.005}
- T ∈ {200, 500}
- α₀ ∈ {0.8, 1.8}
- num_sources ∈ {1, 2, 4}
- geometry = symmetric, phase_offset = 0

---

## 🧮 SPBI Results

| Dimension | γ     | T   | CV   | ρ   | SLF  | SPBI | Anomaly Flag |
|-----------|-------|-----|------|-----|------|------|--------------|
| **3D**    | 0.001 | 200 | ~0.63 | 0.98 | 0.02 | ~31.5 | — |
|           | 0.001 | 500 | ~0.63 | 0.99 | 0.01 | ~63.0 | — |
|           | 0.003 | 200 | ~0.63 | 0.95 | 0.05 | ~12.6 | — |
|           | 0.003 | 500 | ~0.63 | 0.96 | 0.04 | ~15.8 | — |
|           | 0.005 | 500 | 0    | —   | —    | —    | SAT_CAP (23,530,212.77) |
| **4D**    | 0.001 | 200 | ~0.62 | 0.97 | 0.03 | ~20.7 | — |
|           | 0.001 | 500 | ~0.62 | 0.98 | 0.02 | ~31.0 | — |
|           | 0.003 | 200 | ~0.62 | 0.94 | 0.06 | ~10.3 | — |
|           | 0.003 | 500 | ~0.62 | 0.95 | 0.05 | ~12.4 | — |
|           | 0.005 | 500 | 0    | —   | —    | —    | SAT_CAP (43,690,666.67) |
| **5D**    | 0.001 | 200 | ~0.61 | 0.97 | 0.03 | ~20.3 | — |
|           | 0.001 | 500 | ~0.61 | 0.98 | 0.02 | ~30.5 | — |
|           | 0.003 | 200 | ~0.61 | 0.94 | 0.06 | ~10.2 | — |
|           | 0.003 | 500 | ~0.61 | 0.95 | 0.05 | ~12.2 | — |
|           | 0.005 | 500 | 0    | —   | —    | —    | SAT_CAP (64,150,029.91) |

---

## 📐 Long Horizon Boundary (LHB)

| Dimension | γ = 0.001 | γ = 0.003 | γ = 0.005 |
|-----------|-----------|-----------|-----------|
| 3D        | > 500 (previously > 2000) | > 500 | 500 (SAT_CAP) |
| 4D        | > 500 | > 500 | 500 (SAT_CAP) |
| 5D        | > 500 | > 500 | 500 (SAT_CAP) |

---

## 🔎 Interpretation
- **SAT_CAP regimes:**  
  - 3D → 23,530,212.77  
  - 4D → 43,690,666.67  
  - 5D → 64,150,029.91  
  These constants appear at γ = 0.005, T = 500 across all sources and α₀ → definitive artefact boundaries.

- **Universe‑like regimes:**  
  - For γ ≤ 0.003, SPBI values are moderate (≈10–30), showing probabilistic behavior but not collapsing.  
  - CV remains stable (~0.61–0.63), indicating consistent variance across α₀.  
  - SLF is small (0.02–0.06), reflecting strong source dependence; SPBI magnifies accordingly.

- **Goldilocks zone:**  
  - SPBI values in the 10–15 range (γ = 0.003, T = 200–500) are closest to the target band (≈0.05–0.10 in normalized terms).  
  - These buckets are the most “universe‑like” in this slice.

---

## 🧭 Next Steps
1. Extend horizons at γ = 0.003 (T = 1000) → tighten LHB detection.  
2. Micro‑batch around γ = 0.0045–0.005 in 5D → confirm cap onset curve.  
3. Geometry/phase contrasts → compute GPN neutrality.  
4. Aggregate SPBI summaries into per‑dimension reports with verdicts.

---

**Verdicts:**  
- **3D:** Universe‑like for γ ≤ 0.003; too stable (artefact) at γ = 0.005, T = 500.  
- **4D:** Same profile as 3D; cap at γ = 0.005, T = 500.  
- **5D:** Universe‑like for γ ≤ 0.003; artefact cap at γ = 0.005, T = 500.  