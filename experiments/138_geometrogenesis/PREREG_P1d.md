# PREREG P1d — dissipation channel + two-legged gate (FROZEN before running the channel)

**Date frozen:** 2026-07-13. **Prereg discipline:** Exp 137/138 lessons (reachable-range
before freezing; instrument null+false-positive validated; engagement census before
interpreting). Supersedes the 2026-07-12 P1d annealing-tension spec on the instrument
side (that spec's god-view shell/cycle gate was invalidated at P1c; the reader here is
the inside-out two-legged gate).

## Hypothesis (RAW 136 §5/§9, Addendum A)
Adding a **shed → dilute(1/N(r)) → reconsume (Eddington cap)** dissipation loop to the
directed-growth substrate (multiplicative growth + re-convergence selection, `p1_growth.py`)
drives it toward a **finite low-dimensional manifold** (the survivor set, Addendum A.3)
rather than a tree or expander. Exp 138 P1 had drive + causality but **no dissipation**
(pure removal) → explode/freeze. P1d adds the missing driven-dissipative loop.

## Prerequisite gate (MUST pass before any channel output is read)
The **two-legged re-convergence gate** (Addendum A.8): a channel output is called a
manifold only if BOTH legs agree —
- **local leg** `Qg`: girth-aware re-convergence density (`plaquette_closure_probe.plaquette_Q`).
  Manifold high; tree/expander ~0.
- **global leg** `D`: lag-correlation rank (`boundary_layer_dim.perceived_dim`, the RAW 137
  reader). Low-d manifold low; expander high; **small-world elevated** (A.8: 2.4–4.5 vs
  honeycomb 1.1).

**Validation requirement (this is the gate's own null+false-positive test):** thresholds
are fixed from the calibration triple {torus2d = manifold, binary_tree = tree,
random_regular d=4 = expander} ONLY. The gate PASSES iff, under those frozen thresholds,
the held-out graphs classify correctly — decisively **small_world p=0.1 must be rejected
as NON-manifold** (the solo local leg false-positived it). If small_world is not cleanly
separated, the gate is **not P1d-ready** and the channel result is NOT interpretable
(§12.6). Honeycomb (a real 6-cycle manifold) must be accepted.

## Channel spec (`p1d_channel.py`, extends `p1_growth.grow`)
Per-element deposit `D_e`. Each tick, after growth+selection:
1. **consume**: each alive element spends `c` deposit to persist (metabolism).
2. **shed**: spent deposit becomes flux injected at the element.
3. **dilute**: flux diffuses one step (row-stochastic), i.e. spreads ∝ 1/local-degree
   (the 1/N(r) dilution).
4. **reconsume** (Eddington-capped at `cap`): each element reabsorbs flux by
   `reconsume_mode` — the **ablation knob**:
   - `none` (CONTROL): no reconsumption (dissipation = pure loss).
   - `scalar_flux`: reabsorb ∝ local flux density. **A.8 predicts this is BLIND to
     plaquettes → no geometric selection** (pre-registered expectation).
   - `reconvergence`: reabsorb ∝ local re-convergence of flux (flux that returns via a
     short cycle). **Smuggling risk, flagged (§7/§12.2): this keys on the neighborhood
     structure it is supposed to PRODUCE; a positive here is weaker than a positive from
     `scalar_flux` and must be reported as such.**
5. elements with `D_e < D_min` **die** (starved); high-`D_e` reinforced.
Drive/dissipation ratio = growth `q` vs `c`; sweep it.

## Reachable-range check (before freezing the read)
Confirm the gate's three classes {manifold, tree, expander/crumple} are each reachable by
SOME channel setting (e.g. no-dissipation control should read tree/expander; a hand-built
low-d manifold must read manifold). If a class is unreachable, the decision rule is
underpowered — fix before interpreting.

## Engagement census (P1b lesson — before interpreting any run)
Report per run: fraction of deposit **shed** and **reconsumed** per tick, and the fraction
of deaths attributable to starvation vs selection. If the dissipation loop moves <1% of
deposit, it is not engaged and the run tests nothing (as P1b's selector engaged 0.022%).

## Pre-registered outcomes (RAW 136 §9; frozen)
Read the final LCC of each channel setting with the validated gate:
- **(a) low-d manifold** (gate: Qg high, D low), scale-free/comoving growth → **mode-selection earned.** If reached by `scalar_flux`, strong; if only by `reconvergence`, weaker (smuggling caveat).
- **(b) scale-free but crumple/expander** (gate: D high, or small-world signature) → **§7 gap real**: dissipation self-organizes but does not PRODUCE finite-d locality from a structureless DAG. Confirms A.8's flux-is-blind negative at the dynamics level.
- **(c) no critical band** (explode/freeze even with dissipation) → **RAW 135 engine wrong** (its §12.1 kill switch fires).
Each is decisive. A NEGATIVE ((b) or (c)) is a real result, not a failure to be tuned away.

## Process
Skeptic pass (fresh context) before any RESULTS/CLOSURE doc. Commit when asked. No
goal-post moves: the thresholds, the ablation, and the outcome map above are frozen.
