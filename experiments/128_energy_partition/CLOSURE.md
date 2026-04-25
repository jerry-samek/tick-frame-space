# Experiment 128 — Closure

**Status:** Closed. April 18, 2026.
**Outcome:** 1/r² field, Keplerian orbits, and exact Schwarzschild tangential
time dilation earned. Radial Schwarzschild fails on the RGG substrate. Diagnosis
handed off to Experiment 131 (lineage substrate).
**Supersedes:** Experiment 118.
**Succeeded by:** Experiment 131 (RAW 131 — Lineage Substrate).

---

## Trajectory Summary (v1 → v11)

Experiment 128 tested the hypothesis from RAW 128: entities are deposit
patterns on connectors, not objects at nodes. Movement is statistical shift
of the pattern.

### v1–v10 (April 3–6): Graph-layer tests

- **Phase 0 (v1, 1D chain):** consumption equilibrium works in a linear
  chain.
- **Phase 1 (v2, graph):** boundary forms from geometric dilution; planet
  mass = constituent node count.
- **Phase 2 (v2):** coherence 0.438 — first coherent arcs, but with
  hand-coded momentum, not emergent.
- **v3 (500k graph, 5 planet nodes):** probability cloud behavior;
  ejection event observed; binding survives.
- **v4/v5 (500 planet nodes, vectorized):** 38× speedup; planet merges;
  nodes diffuse.
- **v6 (deposit dominance tracking):** stable equilibrium at dist ≈ 12.2.
- **v7–v8 (tangential velocity / acceleration):** one-time deflection at
  best; dies at equilibrium or oscillates noisily.
- **v9 (ODE, consumption force):** Keplerian orbits recovered. RAW 130
  ("it rotates because it consumes") written.
- **v10 (consumption IS movement):** minimal orbit — perfect circles;
  flux `= L/(4πr²) =` Newton renamed.

### v11 (April 16–17): Arrival Rig

Seven phases + four diagnostics, on a 100k-node 3D RGG (R = 60, k ≈ 24)
with a 50-node star and an absorbing boundary at r > 0.95 R.

| Phase | Result | Status |
|---|---|---|
| 1 — star only | ρ(r) slope −1.33 (boundary-steepened from −1); gradient slope −1.968 | **EARNED** — 1/r² on graph |
| 2 — orbit in measured ρ(r) | Kepler orbits to a few % | **EARNED** — pure-Newton on real graph field |
| 3 — buffered consumption (HYBRID) | Inner regime pins r to r_eq; outer Newton | Flagged HYBRID (Newton present in ODE) |
| 3.1 — mass + renewal (HYBRID) | Variant B: T identical across masses (Newton's mass-independence) | Flagged HYBRID |
| 3.2 — solar system sanity | Fixed-model horizon at 6.28 AU is artifact of per-unit-mass renewal constant; "−1" renewal term is **type error** (persistence ≡ ticking, not paid from flux) | Type error corrected (2026-04-18) |
| 3.3 / 3.4 — earth scale / resistance | Renewal local (ambient tick-stream); stellar flux is pure orbital acceleration; clean Newton recovers | Reinterpreted; now archived as ontology fix, not new prediction |
| 4 — gravitational time dilation | `(1 − γ)` slope −1.094 on graph; Einstein weak-field predicts −1.0 | **EARNED** — 1/r redshift shape |
| 5 — unified SR+GR tick budget | `γ = sqrt(1 − L_grav − L_vel)` is the **exact** Schwarzschild formula for tangential observers; static limit at L_total = 1 emerges as geometric boundary | **EARNED** — exact Schwarzschild tangential |
| 6 — radial motion | Naive γ fails vs Schwarzschild radial; measured `⟨cos²θ_radial⟩ = 0.32–0.34` (isotropic) in every shell | **NEGATIVE** — graph has no anisotropy |
| 6b — per-edge flow | Radial/tangential directionality ratio `phi_net/phi_gross ≈ 2.85` constant across all shells; Schwarzschild needs r-dependent 1/(1−L_grav) | **NEGATIVE** |
| 6c — per-node flux vector | `V_rad/ρ ≈ (1 − L_grav)/r`; `(V_rad/ρ)/L_grav` goes from ~0.2 near source to ~2.1 at boundary — opposite r-dependence from Schwarzschild | **NEGATIVE, but specific** — substrate reads complement of GR |
| 6d — proper-time discrepancy | `gamma_substrate / gamma_schwarz = sqrt(1 − L_grav)` to machine precision over full (r, v) grid; substrate observer ages ~8% less than Schwarzschild on same radial infall | **NEGATIVE but self-consistent** |
| 6e — biased propagation | β ∈ {0, 0.3, 0.7, 1.0} sweep of gradient-biased emission; Phase 1's 1/r survives (slopes −1.33 to −1.43); `(V_rad/ρ)/L_grav` shape unchanged — same inverted r-dependence; per-node emission is not the missing rule | **NEGATIVE** |
| 7 — moving star | In comoving case (planet shares star's v_z), orbit preserved perfectly at any v_z up to 0.001·c; **equivalence principle emerges from retardation automatically** | **EARNED** — solar system as coherent drifting pattern |

---

## Load-Bearing Result

**Four independent radial diagnostics (6, 6b, 6c, 6d, 6e) converge:** on a
3D RGG substrate with linear-local propagation rules, the substrate reads
radial gravity as `gamma ∝ (1 − L_grav)` where GR reads
`g_rr = 1/(1 − L_grav)`. These are *reciprocal* in shape — the substrate
tracks "leftover tick budget for directed motion" while GR tracks "space
stretched per unit proper distance." Both describe the same observable
radial slowdown but through inverted ledgers. The gamma-ratio between them
is exactly `sqrt(1 − L_grav)` — machine-precision algebraic identity.

---

## Diagnosis (the handoff to Experiment 131)

Two candidate reasons the radial result fell short:

### (a) Pattern-coherence reading

The substrate is fine. The missing ingredient is composite-object
structure: radial GR emerges from what counts as "the same pattern" when
ρ varies across the pattern's spatial extent. A point particle can't
stretch, so it sees only the `(1 − L_grav)` response we measured. An
extended object must adapt its radial extent to local field conditions
to preserve internal coherence — that adaptation is the Schwarzschild
`g_rr` factor. This ties radial GR directly to the Exp 55/56 "planet
stays planet-shaped" frontier.

### (b) Lineage-substrate reading (RAW 131)

The substrate itself is wrong. The RGG projects spatial geometry into
topology without encoding lineage; but connections in the tick-frame
universe are **ancestral**, established when lineages split. Propagation
doesn't build connections; it flows along them. The `+1/tick` mechanism
is the fluid running through the always-present lineage lattice.
Spatial distance, the speed of light, and Schwarzschild's radial
stretching are all consequences of how the lineage tree is organized,
not of anything happening on a spatial graph.

**Both may be right** (pattern coherence on a lineage substrate is a
sharper version of pattern coherence on a spatial graph). Experiment 131
tests (b) directly. (a) remains a live reading and will be revisited
once the tree substrate can hold composite patterns.

---

## What This Experiment Costs in Assumptions

- Phase 1's 1/r² result was EARNED, but on a substrate (RGG) we now have
  good reasons to doubt ontologically. The **math** of 1/r² survives;
  the **reason** is reopened.
- Phase 5's exact tangential Schwarzschild is a strong positive. It
  relied on local tick-rate reading of ρ, which is ontology-agnostic —
  any substrate that produces ρ(r) with the right shape will reproduce
  tangential Schwarzschild. Expected to transfer.
- Phase 7's moving-star / equivalence-principle result is ontology-
  agnostic (it's about retardation and coherent pattern drift). Expected
  to transfer.
- Phase 3 series's HYBRID flag stays HYBRID. Experiment 131 may or may
  not clean it up.

---

## Files and Pointers

- `experiment_description.md` — original April 3 spec.
- `session_notes_20260403.md` — early-session notes.
- `v1/` through `v11_arrival_rig/` — version history.
- `v11_arrival_rig/README.md` — per-phase writeup.
- `v11_arrival_rig/results/` — plots and logs for all v11 phases.
- `docs/theory/raw/128_energy_partition_store_or_move.md` — RAW 128.
- `docs/theory/raw/129_experimental_connections.md` — RAW 129.
- `docs/theory/raw/130_it_rotates_because_it_consumes.md` — RAW 130.
- `docs/theory/raw/131_lineage_substrate.md` — RAW 131 (handoff).
- `experiments/131_lineage_substrate/` — next experiment.

---

## One-Line Closure

Experiment 128 gave us 1/r², Kepler, tangential Schwarzschild, and
equivalence principle on the right side of the ledger, and a clean,
reproducible failure mode on the radial side that localizes the next
question to pattern coherence and/or substrate ontology — which is
exactly the handoff to Experiment 131.
