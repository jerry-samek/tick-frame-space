# Experiment Plan: Next Steps (SPBI & LHB Validation)

## 🎯 Objectives
- Confirm SPBI metrics in the last universe‑like zone (γ = 0.004).
- Document the sharp damping threshold between γ = 0.004 and γ = 0.0045.
- Validate geometry/phase neutrality (GPN).
- Extend horizons for γ = 0.003 to tighten LHB detection.
- Produce auditable Markdown summaries and plots.

---

## ✅ Task Checklist

### 1. Goldilocks Zone Validation (γ = 0.004)
- [ ] Run SPBI calculations for γ = 0.004 at T = 500 (3D, 4D, 5D).
- [ ] Run SPBI calculations for γ = 0.004 at T = 1000 (3D, 4D, 5D).
- [ ] Record CV, ρ, SLF, SPBI per dimension.
- [ ] Summarize results in `SPBI_goldilocks_summary.md`.

### 2. Critical Boundary Documentation
- [ ] Compare γ = 0.004 vs γ = 0.0045 outcomes.
- [ ] Note dimension‑independent onset of saturation.
- [ ] Record cap constants:
  - 3D → 23,530,212.77
  - 4D → 43,690,666.67
  - 5D → 64,150,029.91
- [ ] Document curve: `T_LHB(γ=0.004) > 1000`, `T_LHB(γ=0.0045) = 500`.

### 3. Geometry & Phase Neutrality (GPN)
- [ ] At γ = 0.004, T = 500, α₀ = 1.8, num_sources = 2:
  - Run geometry ∈ {symmetric, clustered}.
  - Run phase_offset ∈ {0, 1}.
- [ ] Compute SPBI for each variant.
- [ ] Summarize neutrality in `GPN_summary.md`.

### 4. Extended Horizons (γ = 0.003)
- [ ] Run γ = 0.003 at T = 1000 (3D, 4D, 5D).
- [ ] Optionally extend to T = 2000 if runtime permits.
- [ ] Record SPBI and anomaly flags.
- [ ] Update LHB table in `SPBI_LHB_extended.md`.

### 5. Documentation & Visualization
- [ ] Aggregate results into:
  - `SPBI_LHB_summary_3D_4D_5D.md` (fine slice).
  - `SPBI_LHB_summary_finest.md` (critical boundary slice).
- [ ] Generate plots:
  - SPBI vs γ for each dimension.
  - Highlight Goldilocks zone (γ = 0.004).
  - Show collapse at γ ≥ 0.0045.
- [ ] Commit plots and summaries to repo.

---

## 📌 Notes
- These runs are **fast**: limited combinations (γ = 0.004 focus + small GPN slice).
- Prioritize γ = 0.004 buckets for detailed SPBI; suppress SPBI in SAT_CAP regimes.
- Geometry/phase micro‑batches are minimal (4 runs per dimension).
- Extended horizons at γ = 0.003 may take longer but are still manageable.

---

## 🧭 Expected Outcomes
- Confirmed SPBI metrics in the last viable universe‑like zone.
- Clear documentation of the critical damping threshold.
- Verified neutrality across geometry/phase.
- Extended LHB curves for γ = 0.003.
- Auditable Markdown + plots ready for repo inclusion.