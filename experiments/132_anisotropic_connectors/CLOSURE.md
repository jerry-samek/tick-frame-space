# Experiment 132 — Closure

**Status:** Closed. April 20, 2026.
**Outcome:** Schwarzschild radial earned at the per-edge level on a
static RGG with anisotropic-connector rule. Tangential preserved via
gradient smoothing. Horizon exists qualitatively but does NOT scale as
Schwarzschild r_s ∝ M. Deeper ontological issue surfaced (our
"connectors" are thin scaffolding, not deposit chains; hopping walker
is non-native to tick-frame) — not resolved here.
**Supersedes:** —
**Succeeded by:** Next experiment (TBD number), observer-as-cut-through-
deposit-structure ontology.

---

## Trajectory Summary (Phases 1 → 5c)

Exp 132 took v11 Phase 6's diagnosis literally ("substrate must make
radial connectors effectively longer than tangential by 1/√(1−L_grav)")
and imposed it as a rule on the v11 RGG: per-edge propagation rate
function of local L and edge orientation vs ∇ρ.

Rule:
```
L        = min(ρ_avg / ρ_scale, L_MAX)
cos²θ    = (ê_edge · ∇̂ρ)²
stretch  = √(cos²θ × 1/(1−L) + (1−cos²θ))
rate     = 1 / stretch
```

### Phase 1 — Self-consistent anisotropic field (100k RGG)

Iterate ρ → ∇ρ → rates → ρ until fixed point. Converged in 13 iterations
(~7.7 min). Bulk profile preserved:

- slope_ρ = −1.22 (vs v11 baseline −1.27)
- slope_grad = −1.99 (vs v11 −1.97)

Newton 1/r² survived. Anisotropy rule operates without breaking bulk.

### Phase 2 — Radial motion vs Schwarzschild (point evaluations)

At fixed (r, v) on grid, computed γ_substrate from cos²-weighted shell
average vs γ_schwarzschild. Result:

- Outer shells (r ≥ 18): match to 1–3%
- Inner shells (r ≤ 8): 50%+ miss

Diagnosis: shell-averaged s²_eff dilutes radial signal in inner shells
where most edges aren't radial. Rule was fine; projection was not.

### Phase 2b — Threshold-filtered edges (the cleanest positive)

Restrict averaging to edges with cos²θ > T.

| r | L | T=0 (all) | T=0.5 | T=0.7 | **T=0.9** |
|---|---|-----------|-------|-------|-----------|
| 5.0  | 0.78 | 0.54 | 0.71 | 0.83 | **1.01** |
| 8.0  | 0.56 | 0.83 | 0.90 | 0.97 | **1.04** |
| 12.0 | 0.36 | 0.88 | 0.92 | 0.96 | **1.00** |
| 18.0 | 0.20 | 0.93 | 0.96 | 0.98 | **1.00** |
| 25.0 | 0.12 | 0.96 | 0.97 | 0.99 | **1.00** |

**At cos²θ > 0.9: per-edge s² = 1/(1−L) within 0–4% at every L,
including strong-field r=5.** Schwarzschild g_rr recovered per-edge.

### Phase 3 — Selective radial walker

Real trajectory: walker starts at r₀, picks max-cos²(edge, r̂) per step,
integrates proper time along path.

| r₀ | steps | <L>_path | <s²>_path | target | ratio | <cos²_rhat> |
|----|-------|----------|-----------|--------|-------|-------------|
| 5  | 14 | 0.239 | 1.442 | 1.313 | 1.10 | 0.835 |
| 8  | 12 | 0.184 | 1.170 | 1.225 | 0.96 | 0.907 |
| 12 | 13 | 0.119 | 1.113 | 1.135 | 0.98 | 0.828 |
| 18 | 8  | 0.106 | 1.055 | 1.118 | 0.94 | 0.914 |
| 25 | 6  | 0.068 | 1.029 | 1.072 | 0.96 | 0.905 |

Path-integrated s² matches 1/(1−<L>) within 6%. γ error 3.83% mean
vs naive's 7.66% (2× better). Caveat: walker exits in 6–14 steps, so
<L>_path is dominated by the outer weak-field leg.

### Phase 4 — Tangential walker (regression discovered)

Walker picks min-cos²(edge, r̂). Stays perfectly tangential (cos²_rhat
≈ 0.001–0.006) but shows inflated s²:

| r | <L> | <s²> | excess | γ error vs Schwarz tang |
|---|-----|------|--------|-------------------------|
| 5  | 0.904 | 2.16 | +1.16 | 100% |
| 8  | 0.479 | 1.31 | +0.31 | up to 100% |
| 12 | 0.362 | 1.21 | +0.21 | up to 44% |
| 18 | 0.183 | 1.04 | +0.04 | ~3% |
| 25 | 0.115 | 1.02 | +0.02 | ~1% |

v11 Phase 5's exact Schwarzschild tangential was **broken** in inner
shells. Diagnosis: rule fires on cos²(edge, ∇ρ̂), but ∇ρ̂ wobbles off
r̂ due to discrete-graph gradient noise; "tangential-to-motion" edges
end up non-tangential-to-∇ρ̂ and get stretched.

### Phase 4b — Gradient smoothing fix

Smooth ∇ρ̂ over N neighbor-hops (N ∈ {0, 2, 5}). Both directions
improved:

| n_smooth | RADIAL γ-err | TANG γ-err |
|----------|--------------|------------|
| 0 | 3.83% | 19.5% |
| 2 | 2.33% | 14.7% |
| **5** | **2.13%** | **7.5%** |

Tangential restored to <1% error at r ≥ 8. Only saturated-core r=5
remains noisy — because ρ is at L_MAX there, ∇ρ has no meaningful
direction. This is the substrate's analogue of an event horizon.

### Phase 5 + 5b + 5c — Horizon mapping

Tested whether r_horizon ∝ source "mass" (STAR_COUNT × L_STAR).

- Phase 5 (L_MAX=0.95): flat. Diagnosed as cap artifact.
- Phase 5b (L_MAX=0.99): still flat across STAR_COUNT. Diagnosed
  as measurement bug (shell L averages star + field nodes).
- Phase 5c (field nodes only, L_MAX=0.99): **scaling recovered but
  sub-linear.** Log-log slopes 0.19–0.58 across (L_STAR, STAR_COUNT)
  sweeps. Schwarzschild target 1.0.

Cluster geometric extent (∝ N^(1/3)) dominates r_h scaling. Our
"mass" is distributed over cluster_R ≈ 5–8; Schwarzschild's r_s
∝ M applies to point masses or concentrated mass within r_s. Our
setup is in the distributed-matter regime where GR says no
horizon should exist at all.

---

## Load-Bearing Results

1. **Per-edge Schwarzschild radial earned.** At cos²θ > 0.9, s² =
   1/(1−L) to within 0–4% across full L range (Phase 2b). The
   radial GR factor that Exp 128 Phase 6's four diagnostics
   localized as missing is now present in the substrate.

2. **Tangential Schwarzschild preserved (with smoothing).** γ error
   <3% at r ≥ 8, <1% at r ≥ 12 (Phase 4b).

3. **Horizon-like saturation feature exists.** Where L → L_MAX,
   gradient direction loses meaning; walkers can't find clean
   radial or tangential edges. This IS the substrate's event-
   horizon analogue. But its scaling with source strength is
   sub-Schwarzschild.

---

## Load-Bearing Negatives / Caveats

1. **Horizon does not scale as r_s ∝ M.** Phase 5/5b/5c swept
   L_STAR and STAR_COUNT across 6× and 8× ranges; log-log slope
   on r_horizon is 0.19–0.58, not 1.0. Distributed-source geometry
   dominates.

2. **The rule is imposed, not derived.** The 1/√(1−L) radial
   endpoint came from Phase 6 reverse-engineering what factor
   closes the Phase 5 gap. The Pythagorean blend matches
   Schwarzschild's spatial-metric line element analytically —
   which means our rule has reproduced the metric it was
   engineered to reproduce.

3. **Saturated-core r=5 tangential failure was reinterpreted as
   an event-horizon feature.** The interpretation is defensible
   but motivated by the failure, not predicted in advance.

---

## The Deeper Ontological Issue (April 20 discussion)

Late in the experiment, a discussion surfaced that our "connectors"
in Exp 132 are:
- Pre-existing fixed geometric edges (random geometric graph)
- Carry zero state between ticks (pure flux scaffolding)
- Not the deposit-chain connectors of RAW 113 / RAW 128 (where
  the connector IS its accumulated deposits)

Exp 118 v15–v17 implemented the deposit-chain ontology faithfully
(propagating quanta build connectors as they traverse). It produced
binding but NOT coherent orbits (proven as bound random walks in
v9). The trajectory has been:

- Exp 118: faithful ontology, no orbits
- Exp 128 v9+: ansatz-based ODE on measured field, real orbits
  (at cost of treating substrate as given)
- Exp 132: ansatz-based rule dressing, per-edge Schwarzschild
  radial earned

The discussion also surfaced that **entity-hopping is non-native to
tick-frame**. Walkers, entities-at-nodes, particle-like movement —
all classical dressing on a framework whose own documents (Doc 28
Temporal Surfing, RAW 49 Temporal Ontology) say movement is
appearance-of-traversal across a static/append-only structure. Our
code keeps writing particles; our theory keeps saying there aren't
any.

This gap has been there since Exp 128 closure. 132 did not resolve
it. No experiment has.

---

## What This Experiment Costs in Assumptions

- **Pre-built RGG substrate** — treated as given, not emergent from
  deposit dynamics.
- **Imposed anisotropy rule** — reverse-engineered to match
  Schwarzschild, not derived from first principles.
- **Static-field assumption** — moving sources / time-dependent
  fields not addressed (Phase 7 of v11 handled it, not integrated
  here).
- **Walker-as-probe** — classical particle-like observer; not a
  native tick-frame object.
- **L_MAX cap** — numerical shim; the true behavior at L → 1 is
  not explored.

---

## Files and Pointers

- `experiment_description.md` — original spec
- `phase1_anisotropic_field.py` — self-consistent field iteration
- `phase2_radial_motion.py` — point-eval γ comparison
- `phase2b_threshold_radial.py` — cos² threshold sweep (cleanest positive)
- `phase3_selective_walker.py` — radial trajectory integrator
- `phase4_tangential_walker.py` — tangential walker (regression)
- `phase4b_smoothed_gradient.py` — gradient smoothing fix
- `phase5_horizon_mapping.py` — initial horizon sweep (measurement bug)
- `phase5b_lmax_sweep.py` — L_MAX cap test (still bug)
- `phase5c_field_horizon.py` — field-only horizon (bug fixed, sub-linear scaling)
- `phase5d_starcount_only.py` — STAR_COUNT confirmation
- `results/` — logs and plots for all phases

---

## One-Line Closure

Exp 132 took Exp 128 v11's radial-Schwarzschild diagnosis literally,
imposed it as an anisotropic-connector rule on the RGG, and earned
per-edge Schwarzschild radial and tangential (with gradient smoothing)
— at the cost of treating the substrate as pre-built scaffolding and
leaving the question of what a "native" moving entity even IS
completely unresolved.
