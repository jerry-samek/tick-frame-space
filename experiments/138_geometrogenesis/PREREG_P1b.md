# Exp 138 Phase P1b — REDESIGNED: multiplicative growth + re-convergence selection — PRE-REGISTRATION

**Date frozen:** 2026-07-10, after PREREG_P1's smoke-time invalidation, before the redesigned engine runs anything but its own smoke. Production still gated on G-P0 PASS.
**The corrected question (sharpened by the invalidation):** additive growth forces d=1 (bounded boundary); unpruned multiplicative growth forces a tree/expander (d=∞). Does **selection-as-survival** find and *stabilize* an intermediate polynomial phase between collapse and explosion — without tuning to a knife-edge?

## Substrate rules (frozen)

- **Growth (multiplicative):** each tick, every FRONTIER element (alive, age ≤ W) independently spawns a child with probability q. Child's parents = {spawner} ∪ (p−1) draws from the alive ball of distance ≤ 2 around it (fewer → take all). Immutable record as before; seeded rng over id-sorted candidates everywhere.
- **Selection (re-convergence — kills the birth-guarantee degeneracy):** an element past age W survives only if it lies on an undirected cycle of length ≤ L **containing at least one element younger than itself**. Your birth cycle is all-older by construction; persistence requires the future to re-converge onto you (Doc 28, literally). Re-verified every tick via a dirty-set (elements within distance L−2 of any edge change), declared as an exact optimization (cycle status cannot change without an edge change within that radius).
- **Explosion cap:** alive > 30,000 ends the run with outcome category `exp-explosion` (multiplicative growth won the tug-of-war). Extinction ends it with `extinct` (selection won). Otherwise stop at 40,000 births or alive-count stationarity (±5% across 3 consecutive checkpoints).

## Grid and controls (frozen)

- Grid: q ∈ {0.3, 0.6} × p ∈ {2, 3} × L ∈ {4, 6} × W ∈ {8, 16} — 16 cells × 10 seeds.
- Control (a) **no-decay** (q=0.3, p=2, W=8): expected `exp-explosion` / cls `exp` (tree-like). If it reads sustained `poly`, P1b is invalid (geometry leaking from growth).
- Control (b) **all-cycles selection** (the invalidated P1 rule: any short cycle counts, younger-element requirement dropped; q=0.3, p=2, L=4, W=8): expected `exp-explosion` (survival guaranteed at birth ⇒ no pruning ⇒ multiplicative explosion). Signed opposite of extinction.

## Decision rules (frozen; imports from `results/i0.json` only)

- **Eligibility:** final LCC ≥ 256 alive; runs ending `exp-explosion` or `extinct` are their own categories (both FAIL directions — the tug-of-war resolved without a phase).
- **GEOMETRIC SELECTION (PASS):** ≥ 8/10 eligible seeds with: cls `poly` at the final 3 checkpoints AND ê at the final checkpoint ≥ 0.75 (at least 2D-like shells; band_2d lower edge) AND ê non-decreasing over the final 5 checkpoints (kills the tube signature, whose measured trademark is monotone ê collapse) — in ≥ 2 non-adjacent grid cells.
- **HONEST NEGATIVE:** every cell resolves to explosion, extinction, or tube-collapse, with controls as predicted — recorded as "re-convergence selection cannot stabilize an intermediate dimension; the tug-of-war has no fixed point under directed growth."
- **KNIFE-EDGE:** exactly one cell passes → negative per RAW 134 §12.1.
- Near-boundary flags per control_margin = 0.0258; anti-rescue clause; mandatory skeptic pass before RESULTS.

## Traps pre-named

- The ê ≥ 0.75 floor and non-decreasing-trend test are frozen NOW, from the measured tube signature and I0 bands — not tunable after production data exists.
- The self-organization claim (if PASS) needs the death-rate feedback shown to regulate effective growth (reported: births/deaths balance trajectory), else a passing cell may be a tuned balance point — the knife-edge criterion covers the grid dimension of this, the feedback trajectory covers the dynamical dimension.
- Bolognesi still looms: control (a) is his negative; the delta remains the selection term.

---

## Pre-production gate correction (P1b-r1, 2026-07-10 — control-driven, before any grid run)

Reachability probes (`results_p1_recon_console.txt`) before production: (i) extinction is reachable (q=0.1, W=4: seed dies pre-spawn) — frozen as **control (c) extinct-side**; (ii) the exploding no-decay control reads `poly` with unbounded rising ê (2.46 → 3.55 at 31k alive) — at reachable sizes, cls alone cannot separate explosion from geometry in this family, and the gate as first frozen (no ê upper bound, no outcome requirement) could be PASSED by an exploding run. Correction, frozen now:

- **GEOMETRIC SELECTION (corrected):** ≥ 8/10 eligible seeds with outcome `stationary` (or `max-births` with the stationarity criterion met on the final 3 checkpoints) AND cls `poly` at the final 3 checkpoints AND final ê ∈ [0.75, 2.25] AND **plateau**: max−min of ê over the final 5 checkpoints ≤ 0.15 (kills both monotone signatures: rising = explosion, falling = tube) — in ≥ 2 non-adjacent cells.
- **Control expectations keyed to OUTCOMES:** (a) no-decay → `exp-explosion` (transient poly readings are expected and do not trigger the invalidity clause; a control (a) run ending `stationary` with in-band plateau = P1b INVALID); (b) any-cycle → `exp-explosion`; (c) q=0.1, W=4 → `extinct`.
- Everything else unchanged. This correction is driven entirely by control/probe data; no grid cell has run.
