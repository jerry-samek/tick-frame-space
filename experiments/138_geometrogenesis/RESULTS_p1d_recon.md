# Exp 138 P1d — first-cut RECON (not the full experiment)

**Date:** 2026-07-13. **Status:** recon only — informs whether a full P1d is worth pre-registering; no result claimed.
**What changed since the P1d plan:** the plan's Phase I0' god-view instrument (shell+cycle gate) was invalidated this session (failed its adversarial null — hypercube false-positive), and we built the validated inside-out **boundary-layer** instrument (RAW 137, `boundary_layer_dim.py`). So P1d must be re-approached with that instrument, not the obsolete gate. This recon is the first look.

## Question

Does the Exp 138 growth engine (multiplicative growth + re-convergence selection; **drive + directed time, NO dissipation**) grow a substrate that reads as a low-dimensional *manifold*, or as a tree/expander?

## Method

Grow to ~8k births at four parameter cells (incl. a `decay=False` no-selection control), read the final LCC with two observer-native observables: **angular** lag-correlation rank (`perceived_dim`, the validated RAW 137 reader) and **radial** ball-growth (shell classifier — the *god-view* reader, used only to attempt tree-vs-manifold discrimination and flagged as untrusted).

## Result (`results_p1d_dimension_console.txt`)

| params | lcc | lag-rank | shell | e_hat | reads as |
|---|---|---|---|---|---|
| q0.3 p2 L4 W8 | 9476 | 1.1 | poly | 2.98 | low-angular |
| q0.3 p3 L6 W16 | 9202 | 3.9 | exp | 3.91 | tree-ish |
| q0.6 p2 L4 W8 | 11275 | 1.3 | poly | 3.47 | low-angular |
| **q0.3 p2 L4 W8, decay=FALSE (no selection)** | 9505 | 1.1 | poly | 3.01 | low-angular |

## Reading (honest, negative-leaning)

- The grown substrates read **low angular lag-rank (1.1–1.3), NOT expander (~11)** — so multiplicative growth does not produce a random expander. But low angular rank cannot distinguish a 1-manifold/filament from a tree (RAW 137's own caveat), and a branching-growth graph is filament/tree-like, so "low" here most plausibly means **filament/tree, not a 2D/3D manifold.**
- **The decisive tell: the `decay=FALSE` no-selection control reads IDENTICALLY to the selected cell** (1.1 / poly / ~3.0). So the reading is a **topological artifact of multiplicative branching, not something the selection produces.** Whatever geometry-flavored signal exists, the selection is not responsible for it — consistent with Exp 138 P1b (selection engaged 0.022%) and RAW 136 (no dissipation → selection cannot select geometry).
- The "poly, e_hat≈3" is the **god-view shell classifier** — the instrument this session specifically discredited (P1c hypercube false-positive). It is not leaned on; only the sign of the boundary-layer lag-rank + the control comparison carry weight.

## Verdict

**The growth engine's selection does not produce geometry** (no-decay control identical). This confirms, rather than overturns, RAW 136 §5 (the substrate-side wall — directed growth *alone* does not select locality) and Exp 138 P1b. A P1d that could plausibly produce geometry requires the **dissipation/exhaust channel** that RAW 135/136 identified as the missing ingredient (Exp 138 froze/exploded *because* it had no exhaust), integrated into the growth engine and measured with the validated boundary-layer instrument under a fresh pre-registration (reachable-range + skeptic discipline). That is the real P1d, banked; this recon establishes the first cut and its honest negative lean.
