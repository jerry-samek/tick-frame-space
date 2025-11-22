## 📌 Next Steps (Post-v7a Saturation Results)

### 1. SPBI/LHB Summary for 3D
- **γ = 0.001, 0.003:** No saturation up to T = 2000 → LHB not reached.
- **γ = 0.005:** Saturation cap at T ≥ 500 (constant 23,530,212.7659) → definitive LHB onset.
- **Implication:** LHB is damping-driven, not horizon-driven alone. γ·T < 1 rule is insufficient.

### 2. Minimal Additions to Close SPBI Loop
- **Source variation:** Add num_sources ∈ {1,2,4} at γ ∈ {0.001,0.003,0.005}, T ∈ {200,500}, α₀ ∈ {0.8,1.8}.
- **Geometry/phase contrasts:** Include clustered and phase_offset = 1 for subset runs.
- **Goal:** Compute ρ, SLF, GPN → full SPBI values.

### 3. Targeted Expansion
- **4D/5D v7a (focused):** Mirror 3D grid at γ ∈ {0.003,0.005}, T ∈ {200,500,1000}.
- **Ultra-fine damping sweep:** γ ∈ {0.004,0.0045,0.00475,0.005} at T ∈ {500,1000} to pinpoint LHB onset curve.

### 4. v7b Analysis Tasks
- **Code path audit:** Inspect for hard-coded saturation constants or precision guards.
- **Trajectory logging:** Capture ψ evolution over ticks in capped runs to distinguish asymptotic vs abrupt convergence.
- **Metric refinement:** Compute CV_norm = σ / log(μ+1) for dimensional discrimination.

### 5. Artifacts to Produce
- `SPBI_LHB_summary_3D.md` (tables + plots)
- `v7a_saturation_4d_results.{csv,json}`
- `v7a_saturation_5d_results.{csv,json}`
- `V7B_NORMALIZED_METRICS.md`
- `saturation_boundary_plot.png` (γ vs T phase diagram)

### 6. Execution Order
1. ✅ Consolidate 3D SPBI/LHB summary.
2. ⏳ Run minimal source/geometry expansions for 3D.
3. ⏳ Launch focused v7a runs for 4D/5D.
4. ⏳ Perform v7b analysis on all results.
5. ⏳ If caps confirmed in 4D/5D, run ultra-fine damping sweep.

---

**Decision Point:** After 3D SPBI closure and initial 4D/5D runs, evaluate whether full v7a expansion (5,940 runs) is warranted or if targeted sweeps suffice.