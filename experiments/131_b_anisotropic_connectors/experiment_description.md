# Experiment 132 — Anisotropic Connectors on RGG

## Status: SPEC. Date: April 19, 2026.
## Author: Tom (insight via Exp 128 Phase 6 diagnosis), Claude (spec)
## Theory: Exp 128 v11 Phase 6/6b/6c/6d/6e diagnosis
## Supersedes: Experiment 131 (lineage substrate, closed)

---

## Why This Experiment Exists

Experiment 128 v11 earned 1/r² field, Kepler orbits, exact Schwarzschild
**tangential** time dilation, and the equivalence principle on a 3D
random geometric graph (RGG). It failed on Schwarzschild **radial**:
four diagnostics (Phase 6, 6b, 6c, 6d, 6e) converged on the same negative.
The substrate measured `⟨cos²θ_radial⟩ ≈ 1/3` in every shell — the
graph is perfectly isotropic, and no scalar local rule on an isotropic
graph reads `g_rr = 1/(1 − L_grav)`.

Phase 6's diagnosis was unusually specific:

> The substrate works iff radial connectors near mass are effectively
> longer than tangential by exactly `1/√(1 − L_grav)`.

Experiment 131 attempted a different fix (lineage tree substrate) and
was closed: lineage topology + local flow can't even recover 1/r,
let alone radial GR.

Experiment 132 returns to the v11 RGG with a single, surgical change:
**make connector geometry adapt to the local deposit field**. Specifically,
per-edge propagation rate becomes a function of (a) local ρ at the
edge endpoints and (b) edge orientation w.r.t. local ∇ρ. Radial edges
near mass propagate slower (or are effectively longer) by exactly the
factor Phase 6 demands.

If this works, the v11 substrate plus one anisotropy rule produces all
of Newton, Kepler, tangential AND radial Schwarzschild — closing the
last open frontier from Exp 128.

---

## Hypothesis

A modified per-edge propagation rate

```
rate(edge) = base_rate × stretch(orientation, ρ_local)
```

with

```
stretch = 1 / √(1 − L_grav(ρ_local))     for radial edges
        = 1                                for tangential edges
        = smooth interpolation            in between
```

where `L_grav(ρ) = ρ / ρ_scale` is the same coupling Phase 4/5 used,
will reproduce Schwarzschild radial proper time on the otherwise
unchanged v11 RGG.

The orientation of an edge is determined by its alignment with the
**local gradient of the static field**: `ê_edge · ∇̂ρ`.
Radial edges have `|ê_edge · ∇̂ρ| ≈ 1`; tangential edges have ≈ 0.

---

## Phase 1 — Self-Consistent Anisotropic Field

### Goal

Build the static ρ(r) field on the v11 RGG with anisotropic propagation
turned on. The anisotropy depends on ρ; ρ depends on propagation; this
is a fixed-point problem. Solve it iteratively.

### Setup

- Reuse v11's 100k-node RGG (R=60, k≈24) with 50-node star at origin.
  (Drop to 100k from the 500k full-rig for iteration speed; scale up if
  Phase 1 passes.)
- Per-edge propagation rate function:
  ```
  L = min(ρ_avg / ρ_scale, 0.95)              # cap below static limit
  cos²θ = (ê_edge · ∇̂ρ)²                      # 1=radial, 0=tangential
  stretch = √(cos²θ × (1/(1−L)) + (1−cos²θ))  # Pythagorean blend
  rate = 1 / stretch
  ```
  where `ρ_avg = (ρ[i] + ρ[j])/2` and `∇̂ρ` is the local gradient unit
  vector (computed from the field after each iteration).
  Endpoints: tangential → stretch=1; radial → stretch=1/√(1−L). The
  radial endpoint matches Schwarzschild's spatial-metric line-element
  factor `√g_rr = 1/√(1−L)` (which is what v11 Phase 6's diagnosis
  asked for). Treat as provisional: if Phase 2 fails, the interpolation
  form is the first thing to vary.
- Iterate: propagate field with current rates → recompute ∇ρ →
  recompute rates → repeat until ρ(r) stabilizes.

### Observables

- ρ(r) profile after convergence — should remain ~1/r (Phase 1 of
  v11 produced slope −1.33 with boundary effects; we want similar).
- Per-shell anisotropy: `⟨cos²θ_radial⟩` weighted by rate. Should
  now exceed 1/3 in shells with high ρ (asymmetric flow).
- Stretch factor as a function of r — should approach `1/√(1−L_grav)`
  for radial edges near mass.

### Success criteria

- ρ(r) converges (no oscillation between iterations).
- Slope in [−1.5, −1.0] (matching v11 baseline).
- Anisotropy measurable and consistent with the imposed stretch rule.

### Failure modes

- ρ(r) doesn't converge (rate-update loop is unstable).
- ρ(r) converges but to a degenerate profile (e.g. flattens to constant).
- Anisotropy doesn't show up in measurement (rule has no observable
  effect — e.g. rates cancel out in steady state).

Document each.

---

## Phase 2 — Radial Schwarzschild Test

### Goal

Reproduce v11 Phase 6's radial-motion test on the new field. This is
the single decisive test.

### Setup

- Use Phase 1's converged anisotropic field.
- Same (r, v) grid as v11 Phase 6:
  `r ∈ {5, 8, 12, 18, 25}`, `v/c ∈ {0, 0.3, 0.5, 0.7, 0.9}`.
- For radial motion: integrate proper time along a radial trajectory
  using the local edge rates as the clock-rate function.
- Compare against Schwarzschild radial:
  ```
  γ_schw_radial = √((1 − L_grav) − v²/(c²(1 − L_grav)))
  ```

### Observables

- `γ_substrate(r, v)` from anisotropic propagation.
- `γ_schwarzschild(r, v)` analytical.
- Relative error grid.

### Success criteria

- `|γ_substrate − γ_schwarzschild| / γ_schwarzschild < 5%` across the
  full grid, including the strong-field region (v11 Phase 6 saw 50%
  error at r=8, v=0.6).

### What this earns

- Schwarzschild radial earned on the substrate. Closes the last open
  frontier from Exp 128 v11.
- Mercury perihelion precession becomes a derivable consequence
  (ellipses with radial/tangential asymmetry in proper time).
- Black-hole event horizons emerge as surfaces where stretch → ∞
  (no radial hop can escape).

---

## Phase 3 — Tangential Schwarzschild (Sanity Check)

### Goal

Verify Phase 5 of v11 (exact Schwarzschild tangential) still holds with
the new anisotropic propagation. Tangential edges are explicitly
unstretched in our rule, so this should pass trivially.

If it doesn't pass, the rule has a sign error or the orientation
classification is wrong.

---

## Phase 4 — Orbits Under the New Field

### Goal

Run v11 Phase 2's orbit integrator with the new ρ(r) and the radial
proper-time correction. Verify Kepler still holds in weak field; check
for perihelion precession in elliptical orbits.

### Success criteria

- Circular orbits remain circular at periods matching pure Newton
  (within a few percent).
- Elliptical orbits show prograde perihelion precession.
- Precession rate matches GR analytical formula for weak field.

---

## Phase 5 — Pattern Coherence (Exp 55/56 Join)

### Goal

The deferred frontier from Exp 128: place an extended planet pattern
on the substrate, let it consume, ask whether it adapts its radial
extent to preserve internal coherence. With anisotropic connectors
already producing radial stretching, this becomes a much more concrete
test than it was on the isotropic v11 substrate.

Held for after Phases 1–4 succeed.

---

## Open Questions Going In

1. **Interpolation rule.** The smooth interpolation between radial and
   tangential stretch is a modeling choice. The simplest geometric
   form (above) may not be the right one — could need a pure cos² or
   pure |cos| form. Try the simplest first; iterate if Phase 2 fails.
2. **Self-consistency convergence.** Iterating "ρ → ∇ρ → rates → ρ"
   could loop or diverge. Likely needs damping; over-relaxation
   might also help. Be ready to tune.
3. **Strong field stability.** At L_grav approaching 1, stretch → ∞.
   A cap (L ≤ 0.95) is in the rule above to avoid numerics, but it
   means Phase 2 won't test the actual horizon limit. That's OK for
   a first pass; refine later.
4. **Anisotropy origin.** This rule **imposes** anisotropy from
   measured ρ. It does not derive it from a deeper substrate principle.
   That's a deferred question — for now we want to know whether the
   anisotropy, *if present*, gives us the right physics. If yes, the
   "where does it come from" question becomes a serious theory task.

---

## Failure Mode Catalog

| Phase | What's tested | If it fails, what we learn |
|---|---|---|
| 1 | Self-consistent anisotropic field | Rule is unstable or trivial; redesign |
| 2 | Radial Schwarzschild | Anisotropy of this form doesn't give g_rr; the diagnosis was incomplete |
| 3 | Tangential preserved | Rule has structural bug; fix and re-test |
| 4 | Orbits + perihelion precession | Either Kepler breaks (rule has wider effects) or precession is wrong (interpolation form is wrong) |
| 5 | Pattern coherence | Exp 55/56 frontier still open even on anisotropic substrate |

---

## What This Experiment Costs in Assumptions

- **The anisotropy rule is imposed, not derived.** We are asking
  "if the substrate has this property, does it give Schwarzschild?"
  not "why does the substrate have this property?" The latter is
  important but separable.
- **The coupling `ρ_scale` is shared with Phase 4/5.** Same single
  free parameter does all the work. If different physics needs
  different `ρ_scale`, that's a sign the framework is decomposing
  into independent terms.
- **The static field assumption.** Phase 1 solves for steady-state ρ.
  Time-dependent fields (e.g. moving stars from v11 Phase 7) are
  not addressed here; would need extension.

---

## One-Sentence Summary

Experiment 132 takes Experiment 128 v11's RGG substrate plus one
imposed anisotropic-connector rule and tests whether radial
Schwarzschild — the last open frontier from v11 — earns through.
