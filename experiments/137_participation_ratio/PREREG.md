# Exp 137 — Observer-Rank (Participation-Ratio) Test — PRE-REGISTRATION

**Date registered:** 2026-07-03 (before any experiment code was run)
**Implements:** RAW 134 §8.1 (banked program, Tests 1–4) + RAW 134 Addendum A §13.4 (N(r) exponent, later phase)
**Lineage:** Exp 136 discipline (null-first calibration gate, benchmark-relative criteria, pre-registered falsifier); `feedback_honest_emergence_claims`; `project_observer_not_consciousness` (observer = functional comparison bundle, nothing more).

## Question

Does an N-tap observer bundle's measured effective dimension **honestly track the geometry of the substrate it taps** — reading low-rank on genuinely low-dimensional substrates, reading degenerate/high on expanders and trees — and never hallucinate ~3 where there is none?

This is deliberately NOT an emergence experiment. Phase 0 builds and calibrates the **instrument** (the observer-rank readout). Emergence claims (Tests 3–4, N(r) growth) are gated behind the instrument passing calibration.

## Phase 0 — Calibration gate (this build)

### Fixtures (known-geometry substrates)

| fixture | construction | n | expected class |
|---|---|---|---|
| `lattice3d` | 3D torus, 12×12×12, von Neumann (6-neighbor) | 1728 | low-d, d=3 |
| `lattice2d` | 2D torus, 42×42, von Neumann (4-neighbor) | 1764 | low-d, d=2 |
| `expander` | random 3-regular graph | 1750 | expander |
| `tree` | balanced binary tree, depth 10 | 2047 | hyperbolic/ultrametric |
| `null_indep` | 64 channels of pure white noise (no graph) | — | D_PR ≈ N_tap |
| `null_corr` | one common signal + 1% independent noise per channel | — | D_PR ≈ 1 |

### Dynamics (frozen)

AR(1) diffusion on the graph: `x_{t+1} = λ · P x_t + ξ_t`, where `P = D⁻¹A` (random-walk matrix), `ξ_t ~ N(0, I)` i.i.d. per node per step.

- `λ = 0.9` (correlation length of a few hops; frozen before any run)
- burn-in = 1,000 steps; record T = 20,000 steps
- Rationale: the simplest local, isotropic, assumption-free way to make graph geometry visible in correlations. No force law, no consumption, no entities — deliberately inert, because Phase 0 tests the *readout*, not a mechanism.

### Observer bundle (frozen)

- Center node drawn uniformly (per seed); taps = `N_tap = 64` nodes sampled uniformly without replacement from the graph-distance ball of radius `R = 6` around the center (re-draw center if ball < 64 nodes).
- The bundle records only its taps' time series (inside-out: no access to the graph).

### Observables (frozen)

- **O1** `dpr_raw`: participation ratio `(Σλᵢ)² / Σλᵢ²` of the eigenvalues of the 64×64 tap correlation matrix.
- **O2** `dpr_sub`: same after removing the top eigenvector (global mode) — the explicit *whitening* form of self-subtraction required by RAW 134 §8.
- **O3** `mds_dim90`: classical MDS on `d_ij = sqrt(2(1 − r_ij))`; smallest k such that the top-k positive eigenvalues carry ≥ 90% of total positive eigenvalue mass.
- **O4** `corr_decay`: mean |r| at graph distance 1 vs at distance 6 within the ball (positive control).

### Runs

10 seeds (0–9) per fixture. Noise, center, tap sample, and (for `expander`) the graph itself are re-drawn per seed. Report mean ± sd per fixture per observable.

### Gate criteria (pre-registered — the experiment PASSES Phase 0 only if all hold)

- **G1 (separation):** `lattice3d`, `lattice2d`, `expander`, `tree` are pairwise separated by ≥ 2× pooled sd on at least one of {O2, O3}.
- **G2 (ordering):** mean O3(`lattice3d`) > mean O3(`lattice2d`). Absolute values are NOT required to equal 3 and 2 — per the Exp 136 calibration lesson, estimators are biased and the WIN is **benchmark-relative** (separation + ordering). Absolute readings get frozen as calibration findings.
- **G3 (honesty / RAW 134 Tests 1–2):** if the `expander` reading on any observable lands in [2.5, 3.5], that observable is **disqualified as prior-measuring** for all subsequent phases. If ALL observables are disqualified, Phase 0 FAILS.
- **G4 (nulls):** `null_indep` → O1 > 0.8·N_tap; `null_corr` → O1 < 1.5.
- **G5 (positive control):** O4 on both lattices shows decay (mean |r| at d=1 ≥ 2× mean |r| at d=6). If correlations don't see the geometry at all, the dynamics parameters (λ, R) — not the thesis — are wrong; record and retune ONCE, as a logged deviation.

### Program falsifier (A.4-style, pre-registered)

If no observable separates the four graph fixtures (G1 fails after the single permitted G5 retune), then **observer-rank readout is not a usable instrument on this class of substrate**, RAW 134 §8.1 loses its operational form, and Tests 3–4 are moot. That result would be reported as the finding.

## Phase 1 (only if Phase 0 gate passes) — Test 3: stability-selection

On Exp 134's substrate: measure D_PR / mds_dim90 of tap bundles on **surviving** self-maintaining patterns vs dissolved/decohered configurations. Pre-registered falsifier (RAW 134 §12.3): if survivors' rank **expands** (cf. biological 3→7 dimension expansion), claim 5 is refuted as stated.

## Phase 2 (only if Phase 0 passes) — Test 4: objectivity-as-invariance

Two bundles with overlapping balls must agree on the recovered geometry (procrustes distance of shared-tap MDS embeddings vs null). Design details deferred to its own pre-registration.

## Phase 3 (needs its own design pass — NOT specced here) — N(r) growth exponent

Observer-rooted grown DAGs under candidate merge rules; distinct-branch count N(r) vs causal depth; 3D ⟺ N(r) ∝ r² (RAW 134 Addendum A §13.4). Uses Exp 136's calibrated battery. Explicitly deferred: no build before its design pass.

## Deviations

Any deviation from the frozen choices above must be recorded in RESULTS with before/after values. (Exp 04 lesson: an unregistered deviation inflated a hypothesis by 65%.)
