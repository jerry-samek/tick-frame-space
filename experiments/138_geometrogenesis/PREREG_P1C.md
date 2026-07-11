# Exp 138 Phase P1c — engagement-vs-connectivity tradeoff of directed selection — PRE-REGISTRATION

**Date frozen:** 2026-07-11, after the P1c recon (`p1c_recon.py`, `results_p1c_recon_console.txt`), before the sweep runs.
**Prereqs:** P0 PASS (geometry selectable at equilibrium), P1b HONEST NEGATIVE (registered selector never engaged), RAW 134 Addendum F §18.2 (comoving correction: absolute stationarity is a freeze; geometry is polynomial-in-time growth with stationary shape).

## What the recon forces this phase to be (reachable-range rule)

The recon measured the two candidate arms at their corners and found a **tradeoff that brackets the PASS target**:

- **Anchors (N≈2000, spectral dimension d_s via lazy-walk return):** tube C500×C4 d_s=1.005; torus2d(45) d_s=2.001; torus3d(13) d_s=2.641. Classifier validated (synthetic t², t¹ both read poly-t; P1b production 100/100 exp-t).
- **Registered selector + quench (T5 state, N=2069):** connected (LCC=alive=2069) but geometrically dead and **disengaged** — d_s=1.457, one-time cull (3334 deaths then flat). This is the FAIL baseline the PASS band must exclude.
- **Non-descendant selector + quench (N alive=1741):** **engages continuously** (deaths 155→6066 across windows, sustained turnover) but **shreds connectivity — LCC=17**. Geometrically undefined (no giant component).

So the two knobs are **anticorrelated**: connectivity (registered) ⊥ engagement (non-descendant). The connected-AND-engaged-AND-geometric point is NOT demonstrated reachable by either corner. This phase maps the surface between them and pre-registers whether any intermediate escapes the tradeoff.

## Design (frozen)

- **Engine:** `p1_growth.py` (quench + selector flags already implemented and tested). Grow at q=0.3 to `quench_at_alive=2000`, then quench to q2; measure the stationary state.
- **Sweep:** selector ∈ {registered (self-cert), nondescendant} × q2 ∈ {0.05, 0.10, 0.15, 0.20, 0.25} × 8 seeds = 80 runs. (q2 spans subcritical→near-critical at W=8: qW=0.4→2.0.)
- **Per run, on the largest connected component of the final live graph:** LCC size and **LCC fraction** = LCC/alive; engagement = deaths/births; d_s (sparse lazy-walk, 50 sources) if LCC≥256 else `undefined`; instrument cls/ê.

## Gates (frozen; anchors/baselines from recon above)

- **GEOMETRIC-SELECTION (PASS):** ≥6/8 seeds in ≥2 (selector, q2) cells with ALL of: **LCC fraction ≥ 0.5** (connected — beats the fragmented non-descendant corner), **engagement ≥ 5%** (genuinely selecting — beats the registered corner's ~0%/one-time), **d_s ∈ [1.7, 2.3]** (2D-band — excludes tube 1.0 AND the frozen-registered baseline 1.46 AND torus3d 2.64). Instrument-robust: d_s (not the flapping shell classifier) is decisive; cls reported.
- **TRADEOFF-CONFIRMED (the recon-expected negative):** no cell meets all three; engagement and LCC-fraction remain anticorrelated across the surface (Spearman(engagement, LCC-frac) < 0 across the 10 cells) — recorded as "directed selection strong enough to shape geometry is strong enough to fragment it; the connected geometric phase is unreachable by cycle-closure selection under quench."
- **PARTIAL (report, no rescue):** some cell has connected + engaged but d_s outside band (a connected engaged non-geometric phase), or connected + geometric but disengaged (freeze re-labelled) — tabulated, no PASS claimed.
- Reachable-range statement: PASS is demonstrated *possible only if* an intermediate q2 breaks the corner tradeoff — recon gives no such point, so FAIL/TRADEOFF is the predicted outcome and the gate is honest (both directions have a concrete expected cell). Anti-rescue; mandatory skeptic pass before RESULTS.
