# Exp 138 Phase P1 — directed accretion + renewal decay — PRE-REGISTRATION

**Date frozen:** 2026-07-10, before `p1_growth.py` exists; production gated on G-P0 PASS.
**Question (spec §5):** does selection-as-survival under directed causal growth (immutable past, no equilibrium annealing, no global energy) select polynomial ball growth?

## Substrate rules (frozen; every choice point seeded-rng over id-sorted candidates)

- **Elements:** immutable record (id, birth_tick, parent ids); an `alive` flag is the only mutable state. Live graph = undirected parent/child edges between alive elements. Dead elements remain in the record, unattachable (tick-stream immutability).
- **Growth:** seed = element 0. Each tick, `m_new = 4` births. Per birth: anchor f drawn uniformly from FRONTIER = alive elements with age ≤ W (extinction ends the run if empty); parents = {f} ∪ (p_parents − 1) draws without replacement from the alive ball of graph-distance ≤ ρ_att around f in the live graph (fewer available → take all; duplicate parents forbidden). No coordinates anywhere.
- **Renewal decay (the selector):** each tick, every alive element with age ≥ W dies UNLESS it currently lies on an undirected cycle of length ≤ L in the live graph (test: some pair of its live neighbors connected by a path of length ≤ L−2 in the live graph with the element removed; bounded BFS). Continuous re-verification — an element that loses its cycle (neighbor died) loses its protection (Doc 28 renewal).
- **Stopping:** 20,000 births, or live-count stationarity (±5% over 2,000 births), or extinction.

## Grid and in-grid signed controls (frozen)

- Grid: p_parents ∈ {2,3} × ρ_att ∈ {2,3} × L ∈ {4,6} × W ∈ {8,16} — 16 cells; 10 seeds each.
- Control (a) **no-decay** (`decay=False`, p=2, ρ=2, W=8): pure accretion — the Bolognesi control; expected `exp`/tree.
- Control (b) **harsh decay** (W=1, p=2, ρ=2, L=4): expected extinction.
- Both control outcomes are part of the gate: if (a) reads `poly` the instrument or growth rule is leaking geometry and P1 is INVALID; if (b) fails to go extinct the decay rule is not engaging.

## Observables

Every 1,000 births: I0c classification of the live graph's **largest connected component** (declared: the LCC is the object under test; fragment census reported), alive count, cumulative deaths, mean degree. Exponent trajectory = the size-sweep view (growth epochs).

## Decision rules (frozen; numeric bands imported ONLY from `results/i0.json`: band_2d, band_3d, control_margin)

- **Eligibility:** a run counts only if its final LCC ≥ 256 alive elements; smaller = category `too-small` (reported; a grid where nothing reaches 256 is outcome EXTINCTION-DOMINATED, a parameter statement, not a verdict on the question).
- **GEOMETRIC SELECTION:** ≥ 8/10 eligible seeds classified `poly` with ê inside band_2d or band_3d at the final 3 checkpoints, in ≥ 2 grid cells that are not adjacent (differ in ≥ 2 parameters). Near-boundary flags (|R² gap| < control_margin = 0.0258) reported per reading.
- **HONEST NEGATIVE:** no cell meets it AND control (a) reads `exp` (as predicted) — recorded as "renewal-decay under directed growth is insufficient; equilibrium is load-bearing."
- **KNIFE-EDGE:** exactly one cell meets it → negative per RAW 134 §12.1.
- Anti-rescue: no post-hoc regimes, no re-weighting, no added cells without a fresh PREREG. Skeptic pass mandatory before RESULTS.

---

## INVALIDATED AT SMOKE (2026-07-10, before production; superseded by PREREG_P1b.md)

Two design errors surfaced by the smoke run + a 3-seed accretion diagnostic (`results_p1_recon_console.txt`), both structural:

1. **The selector never selects.** Any child with p ≥ 2 parents drawn from a radius-ρ ball is born on a cycle of length ≤ ρ+2 ≤ L for most grid cells — survival is guaranteed at birth, deaths = 0 everywhere (including the W=1 "harsh" control), and 12/16 cells degenerate to the no-decay control.
2. **Additive growth forces d = 1.** With constant births/tick, the attachable frontier is bounded (W·m_new ≈ 32 elements); a bounded boundary can only extrude a constant-width filament. Measured: pure accretion reads `poly` transiently (ê ≈ 1.1–1.5 at 1k births) then collapses (ê ≈ 0.34–0.46 at 20k, monotonically falling) — the tube signature. Control (a) reading `poly` at small sizes also triggers this PREREG's own invalidity clause.

Consequence, kept as a mini-result: **shells ∝ r require a growing boundary — dimension needs multiplicative growth pruned by selection** (exactly RAW 134 §13.4's "prune bʳ to r²"); this design had no bʳ to prune. Redesign in PREREG_P1b.md.
