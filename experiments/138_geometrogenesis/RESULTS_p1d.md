# Exp 138 P1d — RESULTS: dissipation channel + two-legged gate

**Date:** 2026-07-13. **Status:** CLOSED, skeptic-passed. **Prereg:** `PREREG_P1d.md` (frozen before the channel ran). **Supersedes** the dissipation-free recon `RESULTS_p1d_recon.md`.

## Question
Does adding the RAW 135 driven-dissipative "exhaust" loop (shed metabolism → dilute one hop 1/N(r) → reabsorb, Eddington cap → net deposit → starvation) to the directed-growth substrate drive it toward a finite low-dimensional manifold? (RAW 136 §5/§9: dissipation was the "missing ingredient" — Exp 138 P1 had drive + causality but no dissipation and only exploded/froze.)

## Outcome: **QUALIFIED (a)** — dissipation partially closes the wall
The blind `scalar_flux` dissipation loop drives the directed-growth substrate to a **finite-dimensional (that early god-view "d≈2.2" is superseded — the trustworthy reader later resolved it to >2D, crumpled-leaning, not a clean low-d manifold; see the dimension resolution below), degree-regularized (cv≈0.57 vs bare/growth-null 0.71–0.79), gate-MANIFOLD** graph on **large graphs (~2200–2800 nodes)**, **reproducibly across all surviving seeds**, in a **low-q critical band (q ≤ 0.30)**. Dissipation is **load-bearing** — bare growth never crosses cv=0.60 at any q; dissipation lowers cv by ~0.15 at matched q and is *required* to cross into the manifold regime. This is the RAW 135/136 "missing ingredient" doing what was predicted.

| q | #ext (of 6) | #manif (of survivors) | cv(diss) | ball-growth d | cv(bare) |
|---|---|---|---|---|---|
| 0.40 | 2 | 0 | 0.67–0.68 | 2.7 | 0.76 |
| **0.30** | 3 | **3/3** | **0.56–0.58** | **2.2** | 0.71 |
| 0.25 | 4 | 2/2 | 0.51–0.55 | 1.6 | 0.67 |
| 0.20 | 4 | 2/2 | 0.44–0.48 | — (too small) | 0.63 |

(`p1d_channel.py --plane`, c=1.5, scalar_flux, 6 seeds; gate `two_legged_gate.py`, frozen Qg_lo=0.13 D_lo=2.43 cv_hi=0.60.)

## The process error this closure records (the skeptic caught it)
The pre-registered `--fine` strength sweep **fixed q=0.40 — the single worst growth rate** — and on that basis I first concluded **outcome (b)** ("no manifold ever forms, dissipation erodes hubs but never regularizes"). That was **wrong**: it was an artifact of never lowering q. A fresh-context skeptic ran the (q,c) plane, found the q≤0.30 manifold window, and refuted (b). This is the fresh-context-skeptic pattern working exactly as intended — the operator's under-sweep was invisible from inside the operator's own framing. **Lesson (banked):** sweep the decision variable across its reachable range *before* freezing a conclusion; a negative from one slice of a plane is not a negative.

## The mechanism (a correction to the skeptic's "contra-A.8" framing)
The skeptic called this a "strong contra-A.8 positive." More precisely: **A.8 stands, and the manifold forms by a *different* route than A.5 proposed.** A.8 showed scalar flux is blind to *plaquette* structure — and indeed **Qg (the plaquette leg) stays low (~0.26)**, barely above threshold; the MANIFOLD verdict is **not** carried by plaquette reinforcement. It is carried by the **cv (degree-regularity) and D legs**: dissipation regularizes the degree distribution by **starving hubs** (a hub consumes over many edges but the diluted flux it reabsorbs cannot keep pace → it starves), collapsing the growth engine's preferential-attachment hubs (cv 0.79 → 0.57). So dissipation earns finite-d locality via **degree-regularization**, not via the A.5 plaquette-reinforcement route (which A.8 correctly killed). The `reconvergence` (topology-gated) arm adds nothing over blind `scalar_flux` — consistent both with A.8 (topology-gating of flux is irrelevant) and with the mechanism being degree-regularization rather than cycle-reinforcement.

## Three mandatory caveats (frozen prereg forbids tuning these away)
1. **It is a high-extinction CRITICAL BAND, not a broad basin.** 50–67% of seeds go extinct in the manifold window. Prereg (a)'s "low extinction" criterion is **not** met. This is a **self-organized-critical attractor** (narrow, dissipation-driven, high-mortality) — which is *exactly* the picture RAW 136 predicted (geometry as an SOC critical phase, not a knife-edge and not a broad basin). It vindicates the RAW 136 recipe (directed time + drive + dissipation → critical band) while denying any "robust basin" reading.
2. **d ≈ 2–3, NOT a pristine 2D lattice; the gate's D-leg OVERSTATES the low-dimensionality.** Out-of-gate ball-growth reads d≈2.2 (q=0.30) while the gate's lag-rank D reads ≈1.0. Report "finite-d, degree-regularized, cv≈0.57," **not** "a 2D manifold." Only the tiny q=0.20 graphs (≈140 nodes, mostly extinct) approach d≈2, and they are too small to bank.
3. **cv 0.51–0.58 clears the frozen cv_hi=0.60 by <0.05** → the MANIFOLD verdict is threshold-sensitive. But cv_hi was frozen pre-registration, so it **cannot** be moved to resurrect (b) — nor moved to make the positive look cleaner. Integrity cuts both ways.

## Net
Dissipation **partially closes** the geometrogenesis wall in this channel: finite-dimensional, degree-regularized locality is **earned from blind flux via hub-starvation**, in a high-extinction SOC critical band, on a substrate that without dissipation is a firmly crumpled hub (cv≥0.63, d≈4). It does **not** produce a pristine low-d manifold, and it does **not** leave the wall untouched (the recon's and my own first read). RAW 136 §7's "does a from-scratch DAG *produce* locality" is **partially answered YES** — locality (finite-d + degree-regularity) is produced, dimension is not pinned to 2/3 and the basin is critical not broad.

## Scope limits (honest, not tuned)
- One realization of the exhaust loop: **1-hop dilution**, this reabsorption rule, this Eddington cap. A different dilution/reabsorption could differ (the skeptic's multi-hop-dilution attack was not exhausted).
- `max_births` 3000; finite-size. The d≈2 corner needs larger graphs to bank.
- The gate D-leg / ball-growth **disagreement** (D≈1 vs d≈2.2) is an unresolved instrument issue — the D-leg understates dimension on these graphs; a future gate should reconcile lag-rank with ball-growth.
- The manifold verdict rests on the **cv leg** with a <0.05 margin; the plaquette (Qg) leg is near-floor. A stricter instrument might reclassify.

## Banked next (fresh prereg required)
Fully map the (q,c) plane and the extinction boundary; larger `max_births` to test whether d→2 is reachable off the extinction edge; reconcile the D-leg/ball-growth dimension disagreement; test multi-hop dilution (the one skeptic attack not run to ground); characterize the SOC band (avalanche/mortality statistics) to test the RAW 136 SOC claim directly.

## Map addendum — full (q,c)-plane (2026-07-13)
`p1d_channel.py --map` (7×7 grid, 5 seeds/cell, frozen gate; `results/p1d_map.log`). Characterizes the closed (a) — not a new hypothesis; the gate is unchanged.

```
        0.20  0.25  0.30  0.35  0.40  0.45  0.50   (q)
c=1.0    M     M     h     h     h     h     h
c=1.1    m     m     h     h     h     h     h
c=1.2    m     m     h     h     h     h     h
c=1.3    m     m     h     h     h     h     h
c=1.4    m     m     h     h     h     h     h
c=1.5    m     m     M     h     h     h     h
c=1.6    X     X     m     m     m     h     h
```
(M=manifold&survives, m=manifold&high-ext, h=hub, X=mostly extinct)

- **q is the manifold axis; c is the extinction/size axis.** cv rises monotonically with q at every c (manifold cv<0.60 only at q≤0.25); raising c mainly raises extinction and *shrinks* the survivor (q=0.20: n 2208→44 as c 1.0→1.6, d dropping toward filament). The manifold window is a **low-q strip (q≤0.25)**, robust across c.
- **Caveat #1 (high-extinction critical band) STANDS across the whole plane** — never below 2/5 extinction in the manifold strip.
- **Caveat #2 REFINED (mild):** the "d≈2 only in tiny ~140-node graphs" limit was a high-c artifact. At **(q=0.20, c=1.0)** survivors are degree-regularized (cv 0.52), gate-MANIFOLD, **~2200 nodes**, ball-growth d≈2.0, 2/5 extinct — the manifold regime is reachable **at scale**, bankable.
- **Instrument finding (sharpens caveat #2):** the gate-**D leg is FLAT at ~1.0–1.5 across the ENTIRE plane** and does NOT track the ball-growth gradient (d 1.0→3.05 with q). D is uninformative as a dimension reader on these graphs; the verdict is carried by **cv**, corroborated by ball-growth. So "d≈2 at (0.20,1.0)" rests on the P1c-discredited shell classifier with the D-leg disagreeing → **exact dimension UNRESOLVED**. The solid claim is *degree-regularized, finite-d, gate-MANIFOLD at scale*, **not** a certified 2D lattice. A trustworthy dimension instrument is the prerequisite to firm any "d≈2."
- **Sweet spot = the low-q/low-c corner** (q≤0.25, c≤1.2): manifold + large + lowest-d + moderate extinction. No goal-post move (frozen gate); the map confirms (a), refines the scale caveat, and hardens the open instrument gap. *(The d_ball numbers here are god-view shell-classifier readings, now known saturated/uncalibrated — see the dimension-probe section below; the absolute dimension is UNRESOLVED.)*

## Dimension probe + skeptic pass (2026-07-13) — dimension stays UNRESOLVED, heterogeneity CONFIRMED
Built `local_ballgrowth.py`, an inside-out local ball-growth reader (per-observer cumulative ball B(r), poly-vs-exp by R², field-of-frames distribution) to resolve the dimension the flat lag-rank D-leg could not. A fresh-context skeptic attacked it.

- **The instrument is NOT a trustworthy dimension reader (skeptic-refuted).** (i) Tree-rejection is a **knife-edge overfit**: a binary tree reads poly d≈1.8 (a "2D manifold") at R_max≤10 and only flips to `exp` at **R_max=12 = the fixture's depth+1**; a deeper tree would re-break it. (ii) At R_max=12 the observer cone covers **70–80%** of the P1d/torus3d graphs → **semi-global**, defeating the "inside-out/local" claim. (iii) The d value **saturates above ~d3** (hypercube d=10 reads 2.5 ≈ torus3d 2.3), so absolute dimension is uncalibrated off clean lattices. (iv) The frac_exp=0.5 cutoff is arbitrary (the only real gap is 0.00 vs ≥0.32).
- **"≥3D" WITHDRAWN; dimension UNRESOLVED.** The ≥3D reading sat on the saturation floor and flipped sign vs torus3d at small windows. Both dimension numbers in this document — the map's god-view d_ball≈2.0 and the probe's d≈2.5 — are untrustworthy. **The dimension of the P1d manifold regime is not resolved.**
- **One robust survivor (skeptic-confirmed across R_max∈{6…16}, sat, seeds):** clean lattices (2D *through* 10D) read a local-expander fraction of **exactly 0**; every P1d channel graph reads a **nonzero, window-stable fraction (≥0.2, ~0.35 at default)**. So the P1d "manifold" regime is **degree-regularized but topologically HETEROGENEOUS — NOT a clean low-d lattice.** This qualifies (a): "gate-MANIFOLD" = degree-regular + finite-d-ish + has-cycles (true), but the pattern is not a pristine manifold and carries a nonzero locally-expander fraction.
### Resolution via the v2 reader (`ballgrowth_fixedK.py`, 2 skeptic passes)
The v1 refutation banked a fixture-independent rebuild: a **fixed-K local cone** (grow each observer's ball to K absolute nodes) — coverage ~12% at K=200 (genuinely local), stable across K∈{80…500}, validated against a **deeper tree (depth 14)** and a **same-N (~2300) random-4-regular**, with no v1-style knife-edge (both trees flagged frac_exp 0.89–0.98 across *all* K; clean lattices frac_exp exactly 0.00, a genuine win not a fit near-tie). A 4th fresh-context skeptic confirmed it as a **low-d + expander discriminator** (trust below ~d3; any absolute d>3 rests on 3–4-shell fits and is ordinal only, not a dimension) and ruled on the P1d verdict:

- **HETEROGENEOUS — CONFIRMED, robust.** The P1d manifold cell reads **frac_exp ≈ 0.47–0.56, FLAT across K∈{80…500} and R_FIT_MIN∈{2,3}** (no swing, unlike v1's 0.21→0.40) — a *majority* of local neighbourhoods are locally-expander, decisively above the clean-lattice floor of 0.00. The single strongest P1d dimension finding: **the manifold regime is NOT a clean low-d manifold.**
- **>2D, but NOT ≥3D, and SCALE-UNSTABLE (crumpled-leaning).** The growth exponent is robustly above the 2D-lattice reading (~2.5–2.8 vs torus2d 1.8, gap 0.7–0.9). But it does **not** clear torus3d (gap only +0.09 at K200; flips negative at K80; torus3d itself saturates at 2.5). Decisively, the P1d local dimension **inflates with the window (2.38→2.75) far more than true manifolds do (torus2d +0.08)** — the signature of **crumpling, not a scale-stable d-manifold.** "≥3D" is **WITHDRAWN**; honest reading: **">2D, dimension not scale-stable → ~3D-or-crumpled."**
- **frac_exp rises monotonically manifold→mid→hub** (0.52<0.57<0.63<0.69), a genuine (uncalibrated) discrimination — "increasingly expander-like with growth rate q," not a dimension ladder.

**Net for (a):** the trustworthy local reader confirms the gate-MANIFOLD regime is degree-regularized (cv) with cycles (Qg) but **substantially heterogeneous and crumpled-leaning — >2D, scale-unstable, not a pristine low-d manifold.** The (a) result stands (dissipation earns degree-regularity + finite-d-ish locality from blind flux in an SOC band), but the *product* is a crumpled-leaning heterogeneous graph; its dimension is not a clean single value. **Remaining open:** whether a stronger substrate/rule can push this toward a scale-stable low-d manifold (the crumpling is now a measured target, not a vague gap).

## Provenance
Prereg frozen `1c21e61`; channel `159611c`; gate hardened `7002e78`; wiring+sweeps `962c0ee`; (q,c)-map `002a766`; ball-growth v1 `e4bfd14`; dimension closure `d6dad45`; ball-growth v2 `596b35c`. **Four** fresh-context skeptic passes: (1) gate/probe recon → A.8; (2) channel result → refuted the operator's (b), established qualified (a); (3) ball-growth v1 → refuted as a trustworthy reader (knife-edge, semi-global), withdrew "≥3D"; (4) ball-growth v2 → CONFIRMED the reader (as a low-d+expander discriminator) and the heterogeneity finding, again refuted "≥3D" down to ">2D, scale-unstable, crumpled-leaning". Three operator overclaims caught and one confirmation — the discipline working. The manifold regime is degree-regularized but crumpled-leaning; its dimension is >2D and not a clean single value.
