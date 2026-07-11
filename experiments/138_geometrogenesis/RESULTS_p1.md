# Exp 138 Phase P1/P1b — RESULTS: directed growth + renewal selection

**Dates:** 2026-07-10 (P1 smoke-invalidation, P1b freeze, P1b-r1 correction) → 2026-07-11 (production, skeptic pass, skeptic-battery T1/T2/T3/T5, this doc).
**Pre-registrations:** `PREREG_P1.md` (invalidated at smoke, kept), `PREREG_P1b.md` + P1b-r1 (frozen pre-production).
**Code/data:** `p1_growth.py`, `p1_evaluate.py`, `p1_skeptic_tests.py`; `results_p1_console.txt`, `results_p1_verdict_console.txt`, `results_p1_skeptic_console.txt`, `results_p1_t5_geometry_console.txt`, `results_p1_recon_console.txt`; `results/p1.json`, `results/p1_verdict.json`, `results/p1_skeptic_tests.json`.

## Verdict

**Registered: HONEST NEGATIVE, exactly as frozen.** 160/160 grid runs ended in explosion (the 30 `not-stationary`/`max-births` labels are explosions mislabeled by a cap-check-ordering artifact — every one has final_alive 40k–48k at 1.6×/tick terminal growth; skeptic catch, evaluator conclusion unaffected); zero runs met stationarity; controls exactly as registered (no-decay 10/10 explosion, any-cycle 10/10 explosion, extinct-side 10/10 extinct).

**Skeptic-corrected attribution — the registered interpretation was WRONG and is replaced:**

1. **There was no tug-of-war.** Total selection engagement across the grid: **1,239 deaths / 5,750,818 births (0.022%)**; 10/16 cells had zero deaths. The registered sentence "re-convergence selection cannot stabilize an intermediate dimension" is retracted: the selector never functioned. Two independent degeneracies, both skeptic-diagnosed and battery-confirmed: (i) the younger-element clause is a **fertility filter** — your own child born within W certifies your cycle (control (b) any-cycle is bit-identical to control (a) at L=6 cells; the clause bites only at the L=4/W=8 corner); (ii) **deaths have no channel into births** — the frontier (age ≤ W) is untouchable by selection and spawns unconditionally, so the alive count is bounded below by an age-structured branching process independent of selection, L, and the graph.
2. **The outcome map was a theorem, and T2 proved it as one:** Euler–Lotka criticality (supercritical iff qW > 1) predicts 29/32 scan cells exactly (the 3 misses are labeling cosmetics at the line); deaths spike near criticality (4,550 at qW=1.0) and vanish deep in the supercritical regime (0 at qW=4.8); **zero stationary cells from-seed anywhere, including the previously unprobed q-band**. The grid negative is thereby upgraded from grid-empirical to **rule-family theorem for seed-grown populations**: a Galton–Watson process has no stationary phase, and this design was one. (The fourth rediscovered-textbook-theorem of the arc — logged as such.)
3. **"Equilibrium annealing is load-bearing" is NOT licensed by P1b** (retracted from the registered wording): the non-equilibrium selector space was sampled at zero functioning points. What survives: P0 (equilibrium) reached a condensed phase; P1b (directed growth, degenerate selector) could not — the comparison is uninformative about non-degenerate directed selection.
4. **The skeptic's battery then found the missing pieces of the real experiment:**
   - **T3:** the **non-descendant** younger-element rule (re-convergence by the rest of the world, not self-certification) raises engagement **43×** (0.33% → 14.33% at the corner cell) — genuine selection exists in this rule family.
   - **T5:** a **stationary tug-of-war fixed point exists, reached by quench hysteresis**: grow at q=0.3 to 2,000 alive, quench to q=0.05 (qW=0.4 — pure branching predicts death) → the mature, cycle-protected population neither dies nor explodes; it holds ~2,000 alive with births balancing deaths (3,334 deaths, trajectory flat for the entire tail). Seed-grown populations cannot reach this phase (T2); mature ones sustain it. **Hysteresis is the signature of a genuine dynamical phase, not a tuning artifact.**
   - **T5 geometry (diagnostic):** the stationary state's graph reads *ambiguously* at 2k nodes — classification flip-flops (poly/exp), gaps mostly sub-margin, final checkpoint `exp` (gap −0.050) at ê 2.14. **Population stationarity and geometric phase are separable properties**; whether a quenched, non-descendant-selected stationary state becomes geometric is an open, now well-posed question.

**The honest headline:** directed growth with the registered selector has no stationary phase (theorem-grade negative) — but the skeptic-driven diagnostics found both a functioning selector (non-descendant, 43× engagement) and a hysteretic stationary phase (mature quench), without yet finding geometry in it. The bridge question — can directed dynamics do what equilibrium annealing did in P0 — is **not answered negative; it is re-posed with working parts**, as P1c.

## Skeptic review

| # | objection | resolution |
|---|---|---|
| 1 | Cap-check ordering mislabels explosions as `max-births`; "q=0.6 behaves differently" is a phantom. | **FIXED** — Verdict; the phantom third phenomenon deleted; 160/160 = explosion. |
| 2 | Selection never engaged (0.022%); "tug-of-war has no fixed point" unearned. | **FIXED via T1** (census in `results/p1_skeptic_tests.json`) + retraction (Verdict 1). |
| 3 | Negative was decidable by inspection (Euler–Lotka); textbook-theorem rediscovery. | **FIXED via T2** — confirmed 29/32 and adopted as the *strongest legitimate form* of the negative (Verdict 2); rediscovery logged against the arc-diagnosis pattern. |
| 4 | P1b re-implemented P1's degeneracy one generation later (fertility filter). | **CONFIRMED via T3** — 43× engagement jump under the non-descendant rule (Verdict 4). |
| 5 | "Equilibrium is load-bearing" smuggles a universal from an existence failure. | **FIXED** — retracted (Verdict 3); spec's framing corrected in the synthesis. |
| 6 | Controls hollow: (b) ≡ (a) bit-for-bit; (c) letter-only (subcritical die-off, not selection winning). | **ACCEPTED** — recorded; T5 supplies the missing "selection acts on a mature population" observation. |
| 7 | Evaluator drift: eligibility ordering; near-boundary count grid-only; KNIFE-EDGE extension. | **ACCEPTED** — all three logged; none verdict-relevant (checked). |
| 8 | Instrument saturation (96.5% of grid final readings sub-margin); gate asymmetric (positive hostage to flapping instrument). | **ACCEPTED** — irrelevant to this outcome-based negative; a P1c PASS criterion must be instrument-robust (larger stationary populations and/or spectral-dimension observable per P0 autopsy A4). |
| 9 | Unexplored q-band could hide a phase. | **CLOSED via T2** — no stationary cell in q ∈ [0.05, 0.6] × W ∈ [2, 16] from-seed; the phase found (T5) is hysteretic, not a hidden from-seed band. |
| 10 | Mature-population extinction never observed ("selection wins" untested). | **FIXED via T5** — better than expected: the mature quench neither dies nor explodes; it is stationary. |

## What this proves / does not prove

- **Proves:** the registered grid negative (explosion everywhere, controls as registered); the Euler–Lotka structure of seed-grown dynamics in this family (29/32, deaths concentrated at the critical line); the registered selector's degeneracy (0.022% engagement; fertility-filter mechanism); existence of a functioning selector variant (T3, 14.3%); existence of a hysteretic stationary phase under mature quench (T5); separability of population-stationarity from geometric readability (T5 geometry).
- **Does not prove:** anything about claim-level geometrogenesis under directed dynamics (the well-posed test has not run); "equilibrium is load-bearing" (retracted); that the T5 phase survives seeds/parameters (single seed, diagnostic label); the T3/T5 findings are post-hoc skeptic diagnostics — **no claims ride on them until P1c is pre-registered**.

## Banked next phase (P1c, requires fresh PREREG before any run)

Quench protocol (grow supercritical → subcritical drive on a mature population) × non-descendant selector × multiple quench targets (2k / 8k / 32k alive) × ≥10 seeds; PASS criterion instrument-robust (spectral dimension + anchors per P0 autopsy, not the flapping classifier alone); reachable-range check on the new decision rule against T5's measured ambiguity BEFORE freezing. The question it answers is the bridge question in its corrected form: **does a hysteretic stationary phase under genuinely-engaged directed selection crystallize geometry, as equilibrium annealing does?**
