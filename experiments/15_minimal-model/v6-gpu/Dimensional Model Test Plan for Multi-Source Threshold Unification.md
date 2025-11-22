# Dimensional Model Test Plan: Multi-Source Threshold Unification

## 🧭 Objective
To determine in which field dimensionality the binary threshold duality (single-source vs multi-source collapse) disappears, and whether geometry/phase reintroduce smooth, coherent scaling of the threshold and commit dynamics.

---

## 📐 Dimensions Under Test
- **1D**: Baseline; binary threshold jump observed.
- **2D**: Planar propagation; geometry and interference begin to matter.
- **3D**: Volumetric propagation; spatial integration expected to smooth threshold.
- **4D**: Higher-dimensional diffusion; tests robustness of coherence and scaling.
- **5D**: Asymptotic behavior; checks if threshold law converges and duality vanishes.

---

## 🔬 Core Hypotheses
- **H1**: Binary jump weakens with increasing dimension.
- **H2**: Geometry and phase measurably affect threshold and commit rates for d ≥ 2.
- **H3**: Time-dependent threshold persists across dimensions.
- **H4**: Threshold scales as α₀ ∝ Mₛ^–β(d), with β(d) increasing toward 0.5.
- **H5**: For d ≥ 4, threshold and rate scaling stabilize; duality disappears.

---

## ⚙️ Experimental Design

### Shared Model Components
- **Field**: Damped wave equation generalized to d dimensions.
- **Sources**: Mₛ point emitters at positions s₁…sₘ.
- **Agent Window**: Weighted region w(x) for salience integration.
- **Sampling**: Every M ticks; commit when Ψ ≥ 1.01.

### Variables
- **Dimension**: d ∈ {1, 2, 3, 4, 5}
- **Sources**: Mₛ ∈ {1, 2, 4}
- **Layouts**: symmetric, clustered
- **Phase**: φ ∈ {0, π}
- **Horizon**: T ∈ {100, 200, 500}
- **Damping**: γ ∈ {0.001, 0.005}
- **Sampling**: M = 1 (baseline)

---

## 📊 Metrics

- **Threshold**: α₀_threshold(T, d, Mₛ, γ, M, layout, phase)
- **Commit Dynamics**: first_commit_time, commit_rate, agent_commit_count
- **Salience Profiles**: final_psi, max_salience, avg_salience
- **Coherence Indicators**: geometry_delta_threshold, phase_delta_threshold

---

## 🧮 Run Matrix

### Core Matrix
- Dimensions: 5
- Source counts: 3
- Layouts: 2
- Phases: 2
- Horizons: 3
- Damping: 2

**Total core runs**: 5 × 3 × 2 × 2 × 3 × 2 = **360**

### Onset Bracketing
- Sweep α₀ near threshold with Δα₀ = 0.01
- ~20 α₀ points per config → 360 × 20 = **7200 fine-grained runs**

### Optional Extensions
- Sampling sensitivity: M = 2 for d ∈ {1, 2, 3} → +180 runs
- Long horizon: T = 800 for d ∈ {2, 3} → +48 runs

---

## 📁 Logging Schema

### File Naming
`d{D}_ms{M_s}_{layout}_{phase}_gamma{γ}_M{M}_T{T}_onset.csv`

### Columns
- dimension_d, num_sources, geometry, phase_offset
- alpha_0, gamma, M, T
- has_commits, agent_commit_count, commit_rate
- first_commit_time, last_commit_time
- avg_commit_interval, std_commit_interval
- final_psi, max_salience, avg_salience
- window_energy_mean, window_energy_peak
- C_eff, geometry_delta_threshold, phase_delta_threshold
- status, run_id, seed

### Aggregation Files
- `threshold_summary_d{D}.csv`
- `scaling_fits_d{D}.json`

---

## 📈 Analysis Procedure

### Threshold Estimation
- Bracket α₀ where commits begin
- Report midpoint as α₀_threshold

### Coherence Assessment
- Compare symmetric vs clustered layouts
- Compare φ = 0 vs π
- Significant if Δα₀_threshold ≥ 0.02 or rate delta ≥ 10%

### Scaling Laws
- Fit α₀_threshold vs Mₛ → α₀ ∝ Mₛ^–β(d)
- Fit α₀_threshold(T) → T^–½ early, saturating later
- Fit commit_rate vs Mₛ → Mₛ^ρ(d)

---

## 🔮 Expected Outcomes by Dimension

| Dimension | Threshold Behavior | Coherence Effects | Rate Scaling |
|-----------|--------------------|-------------------|--------------|
| 1D        | Binary jump        | Minimal           | ρ ≈ 0.3–0.5  |
| 2D        | Partial smoothing  | Measurable        | Stronger     |
| 3D        | Smooth scaling     | Clear             | Stable       |
| 4D        | Asymptotic law     | Persistent        | Convergent   |
| 5D        | Unified behavior   | Saturated         | Final form   |

---

## 🛠 Execution Notes

- Validate CFL stability per dimension
- Use moderate grids (e.g., 1D: 1k, 2D: 128×128, 3D: 64³, 4D: 24⁴, 5D: 12⁵)
- Parallelize across configurations
- Log seeds and run_ids for reproducibility

---

## 📦 Deliverables

- Threshold summaries and scaling fits per dimension
- Comparative plots: α₀_threshold vs Mₛ, geometry/phase effects
- Ψ(t) profiles near threshold
- Master report: dimensional unification of threshold behavior

---

## ✅ Summary

This plan tests whether the binary threshold duality disappears in higher dimensions, and whether geometry and phase effects re-emerge. It includes a full run matrix, logging schema, and analysis procedure to systematically explore threshold unification across 1D–5D field models.