# Exp 137 Test 3 — RESULTS: stability-selection vs observer-rank

**Date run:** 2026-07-04 (registration → run → traces → skeptic pass → skeptic-mandated tests → this doc, one session).
**Pre-registration:** `PREREG_test3.md` (frozen before any Test-3 code existed).
**Code:** `test3_run.py` (registered run), `test3_skeptic_tests.py` (post-run distinguishing tests F1–F5, demanded by the skeptic pass, run before this doc).
**Raw output:** `results_test3_console.txt`, `results_test3_skeptic_console.txt`, `results/test3.json`, `results/test3_skeptic_tests.json`.

---

## Verdict

**Registered scorecard: T3-A CLUSTER-LOW · T3-B FAIL (ρ = 0.771 < 0.8) · T3-C INCONCLUSIVE.** No mid-run changes, no patches, failure branches reported verbatim.

**Skeptic-corrected content — what the run actually established:**

1. **T3-A's CLUSTER-LOW is a zero-power pass and its claim-5 support is WITHDRAWN.** The skeptic predicted, and F1/F2 confirmed: **all 80 non-surviving cycle classes cluster low too** (K=8: 9/9 with pos ≤ 0.5, median 0.000; K=10: 71/71, median 0.005), and the pos ceiling over the *entire census* is 0.322 (K=8) / 0.166 (K=10) — the registered EXPAND falsifier (pos ≥ ~1) was **unreachable by construction**. K≤10 lattice cycles carry at most ~5 chords, so every constructible ring graph is spectrally near C_K. T3-A measured the geometry of the fixture class, not stability-selection. Selection was never in the experiment (zero non-survivors were read in the registered design — the census contrast came only from the skeptic's F1).
2. **The instrument has no demonstrated survivor-specificity.** F3: M-style divergence readouts on *non-surviving* K=8 classes land at dpr_sub 4.83–6.70 — inside and above the survivor range (4.36–6.90). The readout reads "the coupling-graph structure of whatever corpse you kick." The phrase "observer-rank of self-maintaining patterns" currently has no operational content beyond "rank of the damage field of a pattern that happens to sustain."
3. **The survivability premise behind readout M is false, and the error is two documents deep.** The kick battery + time-to-death trace: **112/128 single on-ring ±1 kicks kill the K8 patterns, median 3 ticks, max 7 — 100% dead before M's W=48 horizon.** Only 2K phase-aligned kicks (those mimicking the rule's own next action) are absorbed; remnant census at t=48: 12.5% alive (phase-shifted), 44% six-cell remnants, 20% four-cell remnants, 23% empty canvas. Root cause traced to `RESULTS_phase1.md` Core data ("damage persists as a bounded on-ring phase-shift; it does not collapse") — divergence-field persistence misread as pattern survival; dated correction appended there. Phase 1b's discrimination results (G-M1, T-A/T-B replication) are unaffected — they concern the field's discriminating power — but the instrument's honest description is now: **M reads the structure of the pattern's death transients and remnants, referenced against a memory.** Spatial confinement stays true (remnants are ring cells), which is exactly why the error stayed hidden.
4. **G-M4's inside-consistency needs re-scoping (proposed, pending user approval).** "Reference = the observer's own memorized period" presumes the observer survives; in 87.5% of the ensemble the pattern is dead within ~3 ticks, and in 23% the divergence is a corpse differenced against a memory the pattern no longer holds. The reading remains inside-consistent **for a persistent third-party observer tapping the pattern's cells** (any bundle holding the period in memory — Addendum A's objects-as-tapped-bundles), but NOT for the pattern reading itself. Proposed RAW 134 refinement: M is an *other-observer's* reading of a pattern, valid from inside the substrate but not self-reading.
5. **T3-B (FAIL, 0.771) is honest per the frozen settings but settings-fragile.** The miss is produced by two rank swaps; the FLAT_K6/FLAT_K8 swap rides on ΔRG = 0.029, and F5 shows it **flips at lam = 0.95** (ρ would be 0.829 = PASS). The robust content: **M is period-dominated; the bare ring graph is not** (planar RGs are nearly flat at 2.00–2.29 while M climbs 2.85→5.45); within-K concordance between M and RG is 2/2 pairs at every setting tested. "Attribution does not generalize" should read: *RG lacks M's dominant (K/ensemble) axis; on the structure axis they agree.*
6. **T3-C is INCONCLUSIVE with half its power missing, not evidence-balanced.** S2 (noise time-to-death) is structure-blind — within-pair per-seed death ticks are element-wise near-identical (K8: [2,42,20,2,…] vs [2,42,21,2,…]) because death is jitter first-passage at fixed K; S2 measures K only (medians 84/56/38/33, monotone). The informative score, S1, gave claim-5-direction signs in **both** pairs (3D member less robust AND higher rank), robust to stratum reweighting (cube ≤ flat in *every* stratum; same for the K10 pair). But the geometric common-cause null stands un-excluded: 3D compactness ⟹ more chords (raises rank via the graph spectrum) AND denser collar exposure (lowers off-ring/deletion survival: 0.432 vs 0.728). With only flat-vs-3D pairs available at K ≤ 10, claim 5 and the common-cause null are **indistinguishable in principle** on this family.

**Claim 5 status after Test 3: neither supported nor falsified — the question is unreachable on this fixture class.** Reaching it requires (a) a family where the EXPAND falsifier is attainable (higher-chord classes: K=12+ enumeration, or a different rule), and (b) a selection contrast at fixed (K, chord count) with error bars — the faint hint there (survivors sit slightly below non-survivor medians at fixed chords: −0.075 vs +0.055 at K=8; −0.099 vs +0.005 at K=10; chords=5: tie) is descriptive, tiny-n, and unpowered.

## Registered results

| item | registered rule | outcome |
|---|---|---|
| T3-A | CLUSTER-LOW iff pos ≤ 0.5 ∀6; EXPAND iff any RG ≥ LAT−2sd | CLUSTER-LOW (pos: 0.000, 0.017, −0.075, 0.322, −0.099, 0.165) — **downgraded to no-power, see Verdict 1** |
| T3-B | ρ ≥ 0.8 = generalizes | 0.771 → registered failure branch; traced + fragility-bounded (Verdict 5) |
| T3-C | ≥3/4 signs | 2 negative (both S1), 1 positive (S2, noise), 1 tie (S2) → INCONCLUSIVE (Verdict 6) |
| T3-D | reported | M/(K−1): 0.950, 0.756, 0.623, 0.692, 0.605, 0.766 — no monotone trend toward ambient |

Readings and anchors: see `results/test3.json` (M and RG per fixture; CK/LAT/EXP per K). S1: 0.493 / 0.404 / 0.408 / 0.256 / 0.380 / 0.223 (FLAT_K4/K6/K8, CUBE_K8, FLAT_K10, TOWER_K10); no kicked pattern ever "mutated" — survive or die, nothing in between.

## Skeptic review

Fresh-context skeptic pass on the raw bundle before any narrative. Verdict carried: "1 pass / 1 fail / 1 inconclusive — and the pass is the hollow one." Objections and resolutions:

| # | objection | resolution |
|---|---|---|
| 1 | T3-A is zero-power: fixture-class geometry decided CLUSTER-LOW before any measurement; EXPAND unreachable. | **FIXED via F1/F2 (confirmed).** All 80 non-survivors cluster low; ceiling 0.322/0.166. Claim-5 support withdrawn; T3-A reported as a geometry fact about K≤10 lattice cycles. |
| 2 | No selection contrast — zero non-survivors measured; "self-maintaining patterns read low rank" had no comparison class. | **FIXED via F1** (census sweep is the selection baseline) — and the contrast at fixed chords is a faint, unpowered hint only. |
| 3 | Dead-pattern baseline missing: M may read any corpse alike. | **FIXED via F3 (confirmed).** Non-survivors read 4.83–6.70 — survivor-like. No survivor-specificity demonstrated. |
| 4 | Operator's forensics stopped a document early: the survivability premise DOES have a source — RESULTS_phase1.md's "does not collapse" sentence, still standing. | **FIXED.** Verified; dated Correction appended to `RESULTS_phase1.md` (divergence-persistence ≠ pattern survival). |
| 5 | G-M4 inside-consistency damaged (corpse-vs-memory for 23% of ensemble); bundle didn't say so. | **ACCEPTED + scoped.** Verdict 4; RAW 134 refinement proposed, pending user approval. |
| 6 | T3-B swap rides on ΔRG=0.029 with no error model; verdict may be a settings artifact. | **FIXED via F5 (confirmed fragile).** Ordering flips at lam=0.95; registered verdict stands (frozen settings) with fragility stated; robust content = K-dominance + 2/2 within-K concordance. |
| 7 | LAT anchor may be effectively global (LAT≈EXP). | **FIXED via F4 (partly refuted).** Ball(r=6) = 374/1728 nodes — genuinely local; r=3 anchor moves little (6.48 vs 6.82 at K=8). LAT≈EXP is a property of small tap bundles, not a sampling bug. Anchor label stands. |
| 8 | T3-C framing: "INCONCLUSIVE" hides that S2 (half the registered power) cannot measure the quantity; claim-5-consistent needed an S2 coin-flip. | **ACCEPTED.** Verdict 6 states it; S1-only recomputation (2/2 negative < 3) reported descriptively, verdict unchanged per anti-rescue. |
| 9 | Common-cause null (3D ⟹ chords ∧ collar exposure) indistinguishable from claim 5 on flat-vs-3D pairs. | **ACCEPTED as designed-in.** Unbreakable at K≤10 (Phase 1b known limitation); K=12 enumeration priced as the decoupling path, not run (cost: hours). |
| 10 | Unregistered tie-handling logic in T3-C (zero-variance label; <3-usable rule). | **ACCEPTED + disclosed.** Written pre-run, changes nothing here (2+1 < 3 either way); noted as post-registration decision logic. |
| 11 | Bit-reproducibility: bootstrap seeds use salted `hash()`; CUBE reads 4.841 vs Phase 1b's 4.839. | **ACCEPTED.** Within bootstrap sd (±0.019); flagged as sloppiness — future runs must use a stable hash (e.g. crc32) or fixed PYTHONHASHSEED. |
| 12 | Per-stratum S1 check left on the table (it helps the operator). | **FIXED (skeptic ran it; verified).** Cube ≤ flat in every stratum; K10 pair likewise — the S1 signs are not reweighting artifacts. |
| 13 | Narrative weight-shift onto the weakest-by-construction branch (T3-A headline). | **ACCEPTED.** This doc leads with the scorecard and the no-power downgrade, not with CLUSTER-LOW. |

## New substrate/instrument findings (the run's real yield)

1. **Exp 134 survivors are far more fragile than any prior doc stated:** 87.5% of minimal on-ring kicks are lethal within ~3 ticks; the only absorbed kicks are the 2K that mimic the rule's own next action. Kill-or-survive is binary — no mutations, ever, across 2,668 kicks.
2. **Readout M = death-transient/remnant spectroscopy.** Discriminating (Phase 1b stands), inside-valid for a persistent tapping observer, but not a "survivor steady-state response" and (per F3) not survivor-specific.
3. **S2-style noise driving measures the jitter process, not the pattern** (first-passage at fixed K). Any future robustness score must be event-driven with independent streams.
4. **3D members of both same-K pairs are less kick-robust than their planar partners** — direction consistent with claim 5, attribution blocked by the common-cause null.

## Known limitations

- n = 6 survivors (complete census, but a complete census of a 2-member-per-K family); T3-C is four signs, two from a blind instrument.
- pos scale's zero is not a floor (chords can push RG below C_K: −0.075, −0.099) — "0 = intrinsic-like" is broken semantics at the low end; harmless here (verdict driven by the ceiling), must be redefined before reuse.
- F3's dead-pattern baseline uses an evolved reference (god-view for aperiodic patterns) — diagnostic only, labeled as such.
- K=12 enumeration (chord/3D decoupling + possibly reachable EXPAND) priced but not run.
- Two RAW 134 proposals were **approved by the user 2026-07-04** and recorded as RAW 134 Addendum D (§16): (i) M as *other-observer* reading — "the reading belongs to the tapper" (Verdict 4); (ii) claim-5 test requirements (reachable falsifier + fixed-structure selection contrast + structure-sensitive robustness score) as the banked redesign, plus the reachable-range process rule.

## What this proves / does not prove

- **Proves:** the K≤10 fixture class cannot reach claim 5's falsifier (census-wide pos ceiling 0.32); the survivability premise of PREREG_phase1b was false (root error located and corrected); M reads death/remnant graph structure without demonstrated survivor-specificity; S2 noise-driving is structure-blind; within-K rank concordance between substrate readout and abstract graph holds at all tested settings.
- **Does not prove:** anything about claim 5 in either direction; that survivors differ from non-survivors on any rank observable (the faint fixed-chords hint is unpowered); that the instrument reads anything a bare graph spectrum plus a death process wouldn't.
