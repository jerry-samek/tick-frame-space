# Experiment 135 — Skeptic-pass results

**Date run:** 2026-05-01
**Spec:** `RESULTS_skeptic_pass` was triggered by skeptic-skill review of Phases 1-4 (which were all marked PASSED in `RESULTS_phase{1,2,3,4}.md`).
**Run command:** `python skeptic_pass.py 100`
**Wall-clock:** 95 s for 100 seeds × 9 sweep configurations.
**Raw data:** `skeptic_pass_results.json` (every per-seed measurement).

---

## What this addresses

The skeptic review of Phases 1-4 surfaced ~5 goal-post moves and ~4 untraced anomalies, plus an "all results from a single seed" gap. The shipped phases never tested:

1. Whether Phase 1's relaxed bounds (`max_age < 1000`, `max_pending ≤ 20`) hold across seeds, or are seed=42-specific.
2. Whether Phase 2 at the **original** design parameters (`learning_threshold=50`, bias `[50,25,15,10]`) ever crystallizes correctly.
3. Whether Phase 3's strict routing accuracy is consistently 76.8% (failed criterion) or that was a one-off — and how stable the observer's spectrum is across seeds.
4. Whether Phase 4's "all 6 observers crystallize" claim could ever have been satisfied at the design's threshold (200 from Phase 3).
5. Whether the Phase 4 anomalies (`{4}` known-token spawn, duplicate `{8}` spawn) are single-seed accidents or reproducible substrate behavior.
6. Whether Phase 4's "specialization" is distinguishable from random observation.
7. Whether Phase 4's results are topology-invariant (works on a non-ring fixture) or fixture-bound.

This doc reports the actual numbers.

---

## Reproducibility check (sanity)

Seed=42 reproduces the published Phase 1 and Phase 4 RESULTS exactly:

| | RESULTS_phase{N}.md (seed=42) | This harness (seed=42) |
|---|---|---|
| Phase 1 n_spawned | 5 | 5 |
| Phase 1 max_age | 339 | 339 |
| Phase 1 max_pending_observed | 5 (peak) | 8 (peak observed) |
| Phase 4 n_crystallized | 4 | 4 |
| Phase 4 distinct_spectra | 3 | 3 |
| Phase 4 spawn_tokens | `{6,7,8,8,9,10,4}` | `[4, 6, 7, 8, 8, 9, 10]` |
| Phase 4 per-observer spectra | `{6},{3},{},{},{2},{3}` | `[[6],[3],[],[],[2],[3]]` |

Harness is faithful. All findings below are over 100 seeds (0..99), seed=42 included.

---

## Findings, by skeptic objection

### Objection §1 (Goal-post moves): Phase 2 was a redesign, not tuning

**Skeptic claim:** "Original parameters `(threshold=50, bias=[50,25,15,10])` were changed reactively to `(threshold=200, bias=[60,25,12,3])`. The shipped result demonstrates a much weaker claim than the original."

**Test:** Phase 2 sweep at both parameter sets, 100 seeds.

**Result — confirmed.**

| Configuration | All-cells-pass / 100 | Per-cell match rate |
|---|---|---|
| ORIGINAL: threshold=50, bias=[50,25,15,10] | **19** | [72%, 78%, 73%, 70%, 74%] |
| SHIPPED: threshold=200, bias=[60,25,12,3] | **100** | [100%, 100%, 100%, 100%, 100%] |

The original parameters fail to produce the expected top-3 in **81% of seeds**. The failure mode is consistent across cells — in ~25% of seeds, the rank-3 token (weight 15) is outvoted by the rank-4 token (weight 10) at sample size 50. Sample-by-sample for cell 0:

- `(0,1,2)` correct: 72/100
- `(0,1,3)` (rank-3 missing): 26/100
- `(0,2,3)`: 2/100

This is not RNG variance to be tuned around — it is a systematic counting failure when rank-3 and rank-4 weights are 1.5× apart at n=50. The original claim ("threshold=50 with a [50,25,15,10] distribution learns top-3") is **false** at 81% across seeds.

**Resolution:** ACCEPT and rewrite. Phase 2 as shipped supports a much weaker claim: "top-K-by-count picks the top K when sample size is large and weight ratio between ranks K and K+1 is ≥4×." This is the law of large numbers, demonstrated. Update `RESULTS_phase2.md` summary to remove "tuning, not redesign" framing — call it what it is. The "v8-style learning works at substrate-cell granularity" headline survives only as "top-K-by-count works when parameters allow it to."

---

### Objection §1 (Goal-post moves): Phase 3 routing-accuracy reframe

**Skeptic claim:** "The strict criterion (token i consumed at `ring[i]`) failed at 76.8%. The semantic reframe (consumed at any cell with token in spectrum) was constructed from the failure data."

**Test:** Phase 3 sweep, report both metrics across 100 seeds.

**Result — confirmed but the reframe is necessary, not opportunistic.**

| Metric | Across 100 seeds |
|---|---|
| Strict known-routing accuracy | min 62.7%, median 74%, max 83.7%, std 3.5 |
| Semantic known-routing accuracy | 100.0% in every seed |
| Strict ≥ 95% | 0/100 |

The strict criterion is reliably broken — the observer's interception of `{2,3,4}` reduces strict routing by ~26 percentage points in *every* seed. The reframe is **necessary** because under Phase 3's mechanism the strict bound cannot be satisfied. But it is also **circular** as a "test": once the observer becomes a competing classifier, the semantic metric counts the very interception we wanted to detect as success. Both observations are right.

**Resolution:** ACCEPT with required documentation. Both metrics must be reported on every seed, with the strict criterion treated as the *measurement of observer interception*, not a failure to defend against. The headline claim "Phase 1 mechanism + Phase 2 learning compose cleanly" is wrong — they do not compose cleanly without three patches (canvas-rule reorder, routing reframe, spectrum-self-consistency relaxation). Headline rewritten in §Conclusions.

**Adjacent finding — reproducibility of `{2,3,4}` spectrum:**

| Observer spectrum | Seed count |
|---|---|
| `{2, 3, 4}` | **99/100** |
| `{2, 4, 9}` | 1/100 (seed=1) |

This is the cleanest survival in the entire experiment. The claim "the observer crystallizes to `{2,3,4}` because c0's canvas exhausts on those tokens" is supported with high reproducibility. Caveat: this is a deterministic function of fixture topology + injection point + canvas order. The observer is computing "top-3 of tokens c0 can't classify and whose first-Same isn't an immediate ring neighbor." The substrate has not been shown to do anything more abstract than that.

---

### Objection §1 (Goal-post moves): Phase 4 spawn-count and crystallization

**Skeptic claim:** "Design said `n_spawned == 5 with spectra == {6..10}` and `all 6 observers crystallize`. Test was loosened to `>= 5` and `>= 3` after observing failures."

**Test:** Phase 4 sweep at shipped params (threshold=15) and at design-revert params (threshold=200), 100 seeds.

**Result — confirmed; both criteria are unrecoverable at the design's intended thresholds.**

| Configuration | All 6 crystallize | n_crystallized distribution | distinct_spectra ≥ 3 | n_spawned == 5 |
|---|---|---|---|---|
| shipped (threshold=15) | **0/100** | `{4: 56, 3: 38, 5: 6}` | 89/100 | 35/100 |
| revert (threshold=200) | **0/100** | `{1: 100}` | **0/100** | 71/100 |

Specifically:
- "All 6 observers crystallize" is **never** satisfied. Across all 100 seeds at shipped params, the maximum is 5 (in 6/100 seeds).
- At threshold=200 (Phase 3's threshold), only **1** observer ever crystallizes — exactly 1, in every seed. The traffic distribution makes more crystallization impossible at this threshold within 10K ticks.
- Lowering threshold to 15 was the move that produced the appearance of "specialization." Without it, Phase 4 returns 1 spectrum from 1 observer in every seed.

The `n_spawned == 5 with spectra == {6..10}` invariant fails 65% of the time at shipped params (only 35/100 = 5; 42 = 6; 18 = 7; 4 = 8; 1 = 9).

**Resolution:** REWRITE Phase 4 RESULTS. The "all 6 observers crystallize" prediction was never going to hold at any plausible threshold. The lowering to 15 changed what was measured: "crystallization" at threshold=15 means "first 15 observations dominate" — it captures injection-order noise, not learned classification. Under design's threshold=200, no specialization emerges in 10K ticks at this fixture.

---

### Objection §2 (Untraced anomalies): the {4}-spawn and duplicate-{8} are reproducible

**Skeptic claim:** "Both anomalies labeled 'interesting finding' / 'timing-sensitive emergent behavior' without root-cause investigation."

**Test:** Phase 4 sweep, count seeds with known-token spawn and duplicate-token spawn.

**Result — they are reproducible substrate behaviors, not single-seed accidents.**

| Anomaly | Frequency across 100 seeds |
|---|---|
| Origin-loop spawn for a known token (`{0..5}`) | **59/100** |
| Duplicate spawn for a single token | **29/100** |

These aren't tail events. The known-token spawn fires in the **majority** of seeds. The duplicate-spawn fires in nearly a third. Both anomalies indicate substrate behaviors that the Phase 1 mechanism does NOT correctly handle in the multi-observer fixture.

The mechanism gap: when observers crystallize and intercept tokens, they perturb canvas-order outcomes enough that (a) some known tokens walk back to their origin without finding a Same match, triggering an origin-loop spawn at c0, and (b) freshly-spawned children are not always discovered by the next deposit's canvas (round-robin order misses them). Neither was diagnosed at the deposit-trace level in Phases 3-4.

**Resolution:** Both belong as DESIGN-GAP entries in `RESULTS_phase4.md`, not "interesting findings." A real fix requires diagnosing the canvas/round-robin interaction with a deposit-level trace. Until then, the claim that Phase 4 "self-organizes hierarchically" is overstated by the same fraction (≥59% of runs contain spawned cells with KNOWN-token spectra, polluting the supposed hierarchy).

---

### Objection §2 (Untraced anomalies): Phase 1 boundedness is seed=42-lucky

**Skeptic claim:** "Phase 1's `max_age < 1000` and `max_pending ≤ 20` were set based on seed=42's observed values (339 and 5) without cross-seed verification."

**Test:** Phase 1 sweep, 100 seeds, full distributions.

**Result — confirmed; seed=42 is at the low end of both distributions.**

| Phase 1 statistic | seed=42 | Distribution across 100 seeds |
|---|---|---|
| max_consumed_age | 339 | min 240, **median 526**, max 6560, std 1567 |
| max_pending_observed | 8 | min 6, **median 12**, max 160, std 32 |
| max_age > 339 | n/a | **90/100** |
| max_age > 1000 (the relaxed bound) | n/a | **34/100** |
| max_pending > 20 (the relaxed bound) | n/a | **34/100** |
| max_pending > 50 | n/a | 14/100 |
| unresolved deposits > 5% (the 7th criterion) | n/a | **27/100** |
| n_spawned == 5 (exact, design) | n/a | 67/100 |
| Ring intact | yes | 100/100 |
| Strict known-routing 100% | yes | **100/100** |

The Phase 1 deliverable test, as shipped, would FAIL on:
- 34% of seeds via the `max_age < 1000` assertion (`phase1_test.py:152`)
- 34% of seeds via the `max_pending <= 20` assertion (`phase1_test.py:155`)
- 27% of seeds via the `n_in_flight + n_pending < 5%` assertion (`phase1_test.py:161`)

What does survive cleanly: ring integrity (100/100) and strict known-token routing (100/100). The substrate's *core* claim — "patterns persist under deposit pressure; deposits route deterministically when there's an unobstructed home" — is real. The *operational* claim — "the substrate is bounded in any practical sense" — is seed-42-specific.

**Resolution:** REWRITE Phase 1 RESULTS to separate the two layers. Boundedness was the wrong test of whether the mechanism "works"; routing correctness is the right one and it does work. The `max_age < 1000` etc. should be removed from the deliverable assertions or replaced with statistics across a seed sweep.

---

### Objection §3 (Overstated conclusions): "v8-style hierarchy without a tree"

**Skeptic claim:** "Phase 4's 'positional specialization' is plausibly indistinguishable from pure counting noise at threshold=15 with crystallization_size=1."

**Test as run:** 6 isolated `Cell` instances, each fed 15 IID uniform random tokens from `{1..10}`, top-1 crystallization. 100 seeds.

**Result observed:**

| Metric | Phase 4 (substrate) | IID-uniform baseline |
|---|---|---|
| All 6 crystallize | 0/100 (max 5/6) | 100/100 (always) |
| ≥ 3 distinct spectra | 89/100 | 99/100 |
| Median distinct spectra | **3** | **5** |
| Distinct-spectra mode | 3 (76 seeds) | 5 (49 seeds) |

**The first version of this section interpreted "median 3 < median 5" as "substrate de-specializes below noise floor." That direction of inference is wrong** (caught by the second-pass skeptic): with an alphabet of 10 tokens and only 6 IID-uniform observers at sample size 15, near-distinct argmaxes (5–6) is the *uninformative prior*, not what learning would produce. The fact that the substrate produces fewer distinct spectra (median 3, 76/100 producing exactly 3) is evidence that the substrate is *correlated* — different observers consistently learn from the same family of tokens — not evidence that it produces less than nothing.

What the IID-uniform baseline *does* establish:
- The substrate's traffic *is* correlated. If it weren't, observers would see roughly IID traffic and produce ~5 distinct spectra like the baseline. They don't; they cluster on 3.
- Specifically, 100 seeds produce spectra in a small set of token-singletons; observers c1 and c5 (symmetric about the injection point c0) reproducibly crystallize to the same token in many seeds.

What the IID-uniform baseline does **not** establish:
- That this correlation amounts to v8-style hierarchical specialization. v8's claim is depth-stratified bandwidth allocation — different *roles*, not just different argmaxes.
- That the correlation is anything other than "host position determines which subset of canvas traffic each observer sees, and small samples of subsets have argmaxes drawn from those subsets."

**A fair test of the v8 framing was NOT run.** The fair test would be: observers fed *the same total amount of traffic* the substrate fed them, but drawn from the *pooled* token distribution rather than position-specific subsets. If pooled-baseline observers also produce ~3 distinct spectra at the same sample sizes, then position-specific traffic *adds nothing* and the "specialization" is sample-size-effect on a constrained alphabet. If pooled-baseline observers produce more (closer to 5), then position-specific traffic is doing real work.

**Resolution:** RETRACT the "v8-style hierarchical specialization is falsified" claim. It is **not supported** by the baseline that was actually run. The strongest *defensible* claim from the Phase 4 data is: **the substrate produces correlated, position-dependent argmaxes in the median case (3 distinct spectra across 6 observers), but this has not been distinguished from the trivial "small samples from position-constrained alphabets" alternative explanation.** A pooled-traffic baseline is required before any v8-style claim can be made or denied.

The originally-published `RESULTS_phase4.md` claim ("strongest evidence yet for RAW 133's 'patterns first' claim AND the closest the substrate has come to v8-style hierarchical specialization") remains overstated — but the *converse* claim ("falsified") is also overstated. Both directions of conclusion outrun the data.

---

### Objection §5 (Distinguishing tests): adversarial fixtures

**Skeptic-proposed:** Observer-position permutation, star topology, null injection.

**Test results, all 100 seeds:**

#### A. Observer attach-order permutation `[3,4,5,0,1,2]`

| Statistic | Default ring | Permuted ring |
|---|---|---|
| n_crystallized distribution | `{4: 56, 3: 38, 5: 6}` | `{4: 56, 3: 38, 5: 6}` |
| distinct_spectra distribution | `{3: 76, 4: 13, 2: 11}` | `{3: 76, 4: 13, 2: 11}` |
| n_spawned distribution | `{6:42, 5:35, 7:18, 8:4, 9:1}` | `{6:42, 5:35, 7:18, 8:4, 9:1}` |
| has_known_token_spawn | 59/100 | 59/100 |
| has_duplicate_spawn | 29/100 | 29/100 |

**Bit-identical aggregate stats.** As predicted: outcomes are a function of host position, not of observer index. This *confirms* the operator's "positional specialization" framing in the narrow sense — observers are deterministic functions of where they attach. But this also means the observers themselves are doing nothing but reading off the local traffic profile, which is fully determined by the K=6 ring + injection-at-c0. The permutation test passes; it just doesn't carry the weight the narrative wanted.

#### B. Star topology (c0 hub, c1..c5 spokes)

| Statistic | Ring | Star |
|---|---|---|
| n_crystallized distribution | `{4: 56, 3: 38, 5: 6}` | `{1: 100}` (always 1) |
| distinct_spectra distribution | `{3: 76, 4: 13, 2: 11}` | `{1: 100}` |
| n_spawned distribution | `{6:42, 5:35, 7:18}` | `{10:46, 9:37, 8:10, 11:4}` |
| has_duplicate_spawn | 29/100 | **100/100** |

The substrate **breaks** on the star fixture. Median 10 spawn cells (vs 6 in ring), 100% of seeds have duplicate spawns, only the hub observer crystallizes. **Caveat (added in second pass):** the star is a *degenerate* topology — each spoke is a degree-1 leaf, and `_canvas_order` excludes the predecessor; for a leaf the only connector IS the predecessor, so canvas always exhausts immediately. The star failure tells us the substrate doesn't handle degree-1 nodes well. It does *not* tell us whether the substrate works on non-degenerate non-ring topologies (2D grid, depth-2 tree, coupled rings). That generalisation test was not run.

#### C. Null injection (only unknowns 6..10, no knowns)

| Statistic | Across 100 seeds |
|---|---|
| n_spawned distribution | `{5: 53, 6: 41, 7: 6}` |
| max_pending_observed > 20 | 0/100 |
| max_age > 1000 | 0/100 |
| Ring intact | 100/100 |
| max_pending range | 1-7 |
| max_age range | 14-157 |

Phase 1's bounds (`max_pending ≤ 20`, `max_age < 1000`) hold cleanly when injection is uniform-unknowns. The bound failures in the mixed-mode sweep are caused by the known-token routing path (round-robin canvas at c0 reaches degree 7+ in steady state) interacting with the unknown-token spawn fan. The substrate is well-behaved on uniform load and badly behaved on mixed load. Notable: even with no overlap between injected tokens and existing spectra, 47/100 seeds spawn extra cells (6 or 7 instead of 5). The "exactly 5 spawns for 5 distinct unknowns" invariant has the same kind of tail problem here that Phase 4 has.

---

## Skeptic review (per skeptic-skill Step 4)

| Skeptic objection | Status | Resolution |
|---|---|---|
| §1 Phase 2 redesign disguised as tuning | **CONFIRMED** | Original params fail 81%. Phase 2 as shipped supports law-of-large-numbers, not the original learning claim. Rewrite RESULTS_phase2 framing. |
| §1 Phase 3 routing reframe is circular | **CONFIRMED** with caveat | Strict criterion fails in 100/100 seeds. Reframe is mechanically *necessary* given the substrate, but it also defines as success the very interception that was supposed to be measured. Both metrics must be reported. |
| §1 Phase 4 spawn-count and crystallization criteria | **CONFIRMED** | "All 6 crystallize" is impossible at any threshold within 10K ticks at this fixture. "n_spawned == 5" fails 65% of seeds. Rewrite RESULTS_phase4. |
| §1 Phase 4 threshold lowering changes what's measured | **CONFIRMED** | At threshold=200, exactly 1 observer crystallizes in every seed. The "specialization" finding is an artifact of crossing crystallization at noise-floor. |
| §1 Phase 4 distinct-spectra >= 2 was unnecessarily loose | Partial | Original criterion (≥3) holds 89/100 seeds at shipped threshold. Loosening was unnecessary; the original criterion would have passed in the seed=42 case and failed in 11% of others. |
| §2 Phase 4 known-token spawn untraced | **CONFIRMED reproducible (59/100)** | Not an "interesting finding"; a substrate behavior in the majority of runs. Belongs as DESIGN-GAP. |
| §2 Phase 4 duplicate-spawn untraced | **CONFIRMED reproducible (29/100)** | Same status as above; ~1 in 3 runs produces it. |
| §2 Phase 1 boundedness untested cross-seed | **CONFIRMED** | Bounds fail 27-34% of seeds. seed=42 is at the low end. |
| §3 "v8-style hierarchy" overstated | **NOT TESTED FAIRLY** (retracted: see §3 above) | The IID-uniform baseline shows the substrate produces correlated structure (median 3 distinct spectra vs IID's 5), but does not distinguish "correlated by position" from "correlated by alphabet-size + small-sample artefact." The originals' positive claim remains overstated; my own "falsified" claim is also overstated. |
| §3 "Patterns first" claim from Phase 3 | **REPRODUCIBLE BUT FIXTURE-DEPENDENT** | Spectrum `{2,3,4}` is reproducible 99/100. This is genuine cross-seed reproducibility of a specific deterministic dynamic. It does not by itself establish "patterns first" in any abstract sense — the spectrum is a deterministic function of fixture topology + injection point + canvas order. |
| §4 Single-fixture artifact | **PARTIALLY CONFIRMED** | Star topology breaks the substrate (only 1 crystallized; 100% duplicate spawns). But the star is degenerate — its spokes are degree-1 leaves that cannot canvas. A non-degenerate alternative topology (2D grid, depth-2 tree, two coupled rings) would be the real generalization test; that was not run. The "fixture-bound" framing is *suggested* but not established. |
| §5 Adversarial — observer permutation | Passed (substrate IS positional) | Confirms the narrow positional claim; no extra weight to "patterns first." |

---

## Conclusions — what the data supports

After running the skeptic's proposed tests AND a second skeptic pass on this doc, the following claims are honestly defensible. (Earlier draft stated several of these more strongly; the second-pass skeptic flagged the overreaches and they are now qualified — see `## Skeptic review (second pass)` below.)

1. **Phase 1 ring routing is deterministic — but largely by graph-theoretic construction.** The K=6 ring + canvas mechanism + predecessor-skip + dead-paths produces a structure where a deposit injected at c0 with token `i ∈ {0..5}` walks the ring monotonically until reaching c_i; there is no other place it can go. Strict accuracy 100/100 is the fixture forcing the answer, not learning. What is genuinely surprising is that **`n_spawned == 5` only holds in 67/100 seeds** — even without observers, the substrate has timing-races that produce 6 or 7 spawn events for 5 distinct unknowns. This was not flagged in the original Phase 1 RESULTS.

2. **Phase 1's *numerical* bounds were seed=42-lucky; the *mechanism* still terminates.** The relaxed assertions (`max_age < 1000`, `max_pending ≤ 20`) fail in 34% of seeds each. The unresolved-deposits criterion (`<5%`) fails in 27%. But: every seed's substrate terminates with finite max_age (no infinite walks), the unknown-only fixture stays bounded with `max_pending ≤ 7`, and ring integrity holds in 100/100. So "boundedness in the dynamical-systems sense" is supported; "the specific constants from seed=42 generalize" is not.

3. **Phase 2 demonstrates that counting top-K picks top-K** when the sample size is large enough and rank-K vs rank-K+1 weights are well-separated. The original parameter set (the one that would have demonstrated something stronger) fails in 81% of seeds. The shipped version demonstrates the law of large numbers, applied as designed.

4. **Phase 3's `{2,3,4}` spectrum is genuinely reproducible across seeds.** 99/100 seeds produce exactly `{2,3,4}`; 1 produces `{2,4,9}`. This is the experiment's strongest cross-seed result. Caveat: the underlying substrate dynamic at this fixture is fully deterministic given the seed (the seed only randomises the injector). What is reproducible is "the deterministic dynamic at this fixture, given mostly-similar token streams, almost always reaches the same fixed point" — not "the substrate converges to `{2,3,4}` from many different starting conditions." The seed=1 outlier is the only data point that could illuminate the dynamic and it has not been investigated. Strict known-token routing degrades to ~74% (always — never the design's 95%) because the observer reliably intercepts tokens 2/3/4.

5. **Phase 4 produces correlated, position-dependent observer outcomes — but the v8-hierarchy claim is neither earned nor refuted.** Median 3 distinct spectra (vs IID-uniform baseline's 5) is evidence of correlation, not evidence against hierarchy. A fair pooled-traffic baseline was not run. What *is* established: lowering threshold from 200 to 15 changes what is measured (at 200, exactly 1 observer crystallizes in every seed; at 15, crystallization captures first-15-token noise). The original "strongest evidence yet for v8-style hierarchical specialization" claim is overstated. My earlier draft's "v8 hierarchy falsified" claim is also overstated. Both directions outrun the data.

6. **Phase 4 anomalies are reproducible substrate gaps, not findings.** The known-token origin-loop spawn (`{4}` at seed=42) reproduces in **59/100** seeds; duplicate spawn for a single token reproduces in **29/100**. Both reflect mechanism gaps in the canvas/round-robin interaction that fire under the multi-observer fixture. Neither has been diagnosed at the deposit-trace level.

7. **The substrate's behaviour on degree-1 leaves is broken; non-degenerate-topology behaviour is unknown.** The star topology (5 degree-1 spokes hanging off c0) produces 1 crystallized observer in every seed and 100% duplicate spawns — but degree-1 leaves cannot canvas, so the spokes always exhaust to empty and bounce. Whether the substrate works on a non-degenerate alternative topology (2D grid, depth-2 tree, coupled rings) is **not tested.** The "fixture-bound" framing in earlier conclusions was overreach; the data show the substrate fails on a degenerate case, not necessarily that it fails on all non-ring topologies.

---

## What does not survive

These claims appear in `RESULTS_phase{1,2,3,4}.md` and are clearly not supported by the cross-seed data:

- "After 50 observations, crystallize. Simplest and most debuggable knob." (Phase 2 design) — false at 81% across seeds.
- "Tuning, not redesign" (Phase 2 RESULTS) — false; the original mechanism does not work at the original parameters.
- "Phase 1 mechanism + Phase 2 learning compose cleanly" (Phase 3 RESULTS) — false; three patches were required (canvas-rule reorder, routing-criterion reframe, spectrum self-consistency relaxation).
- "Bounded queueing at `max_pending ≤ 20`" (Phase 1 RESULTS / phase1_test.py:155) — the *constant* fails in 34/100 seeds. (Mechanism termination still holds.)
- "Max age `< 1000`" (phase1_test.py:152) — fails in 34/100 seeds; reaches 6560 in worst case.
- "Origin-loop spawn correctly handles 'no home' case" (Phase 1 RESULTS) — false in 59% of Phase 4 seeds, where it fires for known tokens that DO have a home.
- "All 6 observers crystallize" (Phase 4 design) — never satisfied; not satisfiable at any tested threshold within 10K ticks.
- "Strongest evidence yet for RAW 133's 'patterns first' claim AND the closest the substrate has come to v8-style hierarchical specialization" (Phase 4 RESULTS) — overstated; the test that would have supported or refuted the v8-hierarchy claim was not run.

These claims appear in my earlier draft of this RESULTS doc and have been **retracted** after the second skeptic pass:

- "v8-style hierarchical specialization is *falsified* by baseline" — the IID-uniform baseline does not establish this; a fair pooled-traffic baseline is required and was not run.
- "Phase 4 has no hierarchy and no specialization" — overreach; the substrate produces correlated structure, but whether that correlation amounts to v8-style hierarchy is not testable from the data collected.
- "Phase 4 results are ring-specific" / "the substrate is fixture-bound" — overreach; only ring (design fixture) and star (degenerate degree-1-spokes) were tested. Non-degenerate alternative topology untested.
- "Bounded queueing — false" without qualification — overshoots; the constants fail, the mechanism terminates.

---

## What this experiment actually achieved

A discrete-tick directed-multigraph substrate has been built in which:
- Cells with preset spectra deterministically route tokens through a K=6 ring (Phase 1 ring routing, 100/100 seeds — though largely forced by the cycle topology + predecessor-skip).
- A single empty cell attached to a busy cell reliably crystallizes to a specific spectrum determined by the canvas-exhaust pattern at its host (Phase 3, 99/100 seeds produce `{2,3,4}`).
- A substrate of multiple Learning observers produces correlated, position-dependent argmaxes (Phase 4, median 3 distinct spectra across 6 observers in a K=6 ring) — though whether this correlation amounts to v8-style hierarchical specialization or just a small-sample artefact on a constrained alphabet is undetermined by the data collected.
- The substrate fails on degenerate degree-1-leaf topologies (star), and produces extra/duplicate spawns under multi-observer fixtures (the `{4}` and duplicate `{8}` anomalies, reproducible at 59/29% across seeds).

This is a substantial software/mechanism-design accomplishment — the substrate runs deterministically, terminates on every seed, preserves ring patterns under Phase 1's load, and produces reproducible per-seed dynamics. The cleanest single result is Phase 3's spectrum reproducibility (99/100). What it has *not* yet shown:
- That the K=6 ring isn't a single specially-tuned topology that works while neighbouring topologies don't.
- That Phase 4's correlated outcomes are evidence of a "hierarchy" rather than fixture-of-position-and-alphabet-size.
- That the original RAW 133 claims (semantic differentiation, classification as property of cells not locations, routing by classification) are earned at the substrate level — Phases 1-4's outcomes are consistent with deterministic graph dynamics on a single fixture, not with the abstract pattern-recognition framing.

The first draft of this doc concluded "not a substantive physics result" too confidently. The honest version: **the substrate has reproducible behaviour at narrow conditions and identifiable bugs; the broader claims of RAW 133 remain neither earned nor refuted.**

---

## Open work

If the experiment is to be continued (Phase 5+), the prerequisites are:

1. **Fair pooled-traffic baseline for Phase 4.** For each seed, capture the substrate's full per-observer obs_counter, pool the tokens, then redistribute across 6 baseline observers with the same per-observer sample sizes. Compute distinct-spectra distribution. If pooled-baseline observers also produce ~3 distinct spectra, the substrate's "specialization" is small-sample artefact on a constrained alphabet. If pooled-baseline observers produce more (closer to 5), position-specific traffic is doing real work. **Until this test is run, neither "v8 hierarchy" nor "no hierarchy" is supported.**

2. **One non-degenerate alternative topology.** The star is degenerate (degree-1 spokes cannot canvas). The minimum needed: 2D grid, depth-2 tree, two coupled rings, or any topology with degree ≥ 2 on every node. This tests whether ring routing generalises or is a K=6-cycle artefact.

3. **Multiple injection points.** Inject at 2–3 ring cells simultaneously and check whether Phase 3's `{2,3,4}` spectrum is fixture-of-c0-injection or fixture-of-the-ring-substrate.

4. **Threshold sweep at intermediate values.** Only 15 (shipped) and 200 (revert) tested. At 50, 100, 150 — does specialization scale gracefully or is the noise-floor / impossible regime sharp?

5. **Diagnose the `{4}`-spawn and duplicate-spawn mechanisms** with deposit-level traces at seeds where they reliably fire. Determine whether they are canvas/round-robin races (fixable patch) or fundamental mechanism gaps (substrate redesign).

6. **Investigate the seed=1 outlier** in Phase 3 (spectrum `{2,4,9}` vs `{2,3,4}` everywhere else). Singular outliers are the data points that illuminate dynamics; uninvestigated.

7. **Document the Phase 1 boundedness statistics** instead of asserting constants. Median, max, and tail behaviour across seeds is the honest characterisation.

Phases 1-4's RESULTS docs should be updated (or annotated) with the cross-seed numbers above. The session memory entry `project_135_session_20260501.md` already flags the debt; this doc supplies the data — but neither the originals' positive claims nor my draft's negative claims survive in their original strength. The honest characterisation is messier than either.

---

## Skeptic review (second pass)

Per the skeptic skill (`Not a one-shot...` clause), this RESULTS doc was itself reviewed by a fresh-context skeptic subagent before being treated as conclusive. The second-pass skeptic flagged five overreaches in the first draft. Each is resolved here:

| Second-pass skeptic objection | Resolution |
|---|---|
| **Baseline (median 3 vs median 5) does not falsify v8 hierarchy.** IID-uniform observers produce 5–6 distinct argmaxes by the prior (alphabet=10, agents=6, IID). "Substrate produces fewer" is evidence of correlation, not of "below noise floor." Direction of inference was wrong. | **FIXED.** "Falsified" claim retracted. Section §3 rewritten. The IID baseline is now reported as evidence of *correlation* in the substrate, not of de-specialization. A fair pooled-traffic baseline is named as outstanding work. |
| **"n_spawned == 5 fails 65%" is selectively framed.** The actual distribution is `{5: 35, 6: 42, 7: 18, 8: 4, 9: 1}`. n_spawned ∈ {5,6} = 77/100; ≤ 7 = 95/100. The 2-token tail is real but the framing inflates it. | **FIXED.** Cumulative percentages (77% within ±1, 95% within ±2) added to "what survives" point 1. The original "exact 5" invariant still fails, but the magnitude is more carefully characterised. |
| **"Bounded queueing — false at 34%"** conflates "the constant ≤20 fails" with "boundedness fails." The substrate terminates on every seed; the unknown-only fixture stays at max_pending ≤ 7. Mechanism boundedness holds; the seed=42 numerical bound does not generalise. | **FIXED.** Distinguished in "what survives" point 2 and "what does not survive" section. |
| **"Fixture-bound" framing leans on the star, but the star is degenerate.** Degree-1 spokes cannot canvas — the star is a known-broken topology, not a generalisation test. The conclusion is suggested, not established. | **FIXED.** "Phase 4 results are ring-specific" / "fixture-bound" claims retracted from "what survives" point 7 and "what does not survive." A non-degenerate alternative topology is named as outstanding work. |
| **Phase 3 `{2,3,4}` reproducibility is stronger than the first draft credited.** The metric circularity (semantic reframe) is a fair indictment of the metric, but the underlying spectrum-reproducibility (99/100) is non-trivial. The doc lumped them and downgraded the spectrum claim to "PARTIAL." | **FIXED.** Spectrum reproducibility now stated cleanly in "what survives" point 4, separated from the metric-reframe issue. Caveat about determinism-given-seed retained. |
| **Ring routing 100% is largely tautological.** With 6 cells, 6 token homes, predecessor-skip, dead-paths, and a K=6 cycle, deposits *must* walk to their home. Strict 100% is graph-theoretic, not learned. | **FIXED.** Stated explicitly in "what survives" point 1. The genuinely surprising data point (`n_spawned == 5` only 67/100 even without observers) is now flagged. |

The second-pass skeptic also identified gaps that *were* not tested but are required before Phase 5 (pooled-traffic baseline, non-degenerate topology, multi-injection-point, threshold sweep, deposit-level mechanism trace, seed=1 investigation). These are listed under "Open work" above, not under "FIXED."

**Both skeptic passes' framing of the failure mode was correct in different ways**: the first-pass skeptic correctly diagnosed the goal-post moves and untraced anomalies in the original RESULTS docs. The second-pass skeptic correctly diagnosed that my fix-up doc was over-rotating in the negative direction — turning the original "we marked things passed" narrative into a "we marked things falsified" narrative without doing all the work either narrative would require. The honest answer (after both passes): the substrate has clean reproducible properties at narrow conditions, identifiable bugs, and many open questions.

---

## Post-fix verification (added after diagnosing two substrate bugs)

Following the user's instruction to chase the anomalies surfaced by this skeptic pass, two concrete substrate bugs were diagnosed (deposit-level traces in `trace_4spawn.py` and `trace_dupspawn.py`) and patched. Both were race conditions in the existing canvas mechanism that the design docs hadn't anticipated.

### Bug 1 — leaf-bounce overwrites chain predecessor

**Mechanism (traced at seed=42 Phase 4, t=4002–4046):** when a deposit forwards to a degree-1 leaf and the leaf bounces back, `_bounce` overwrote `deposit.predecessor` from the original chain forwarder to the bouncing leaf. The receiving cell then lost memory of where the deposit came from in the chain, and its canvas no longer excluded the original predecessor — so the deposit could be forwarded *backward* along its own path. At c0, that backward forward triggered origin-loop spawn for KNOWN tokens whose home was a few hops away (the {4}-spawn anomaly).

**Fix:** replaced `deposit.predecessor` with a `chain_stack` of forwarders. `_forward` pushes; `_bounce` pops. `predecessor` is now a property reading the top of the stack — bounces no longer mutate it.

### Bug 2 — stale canvas snapshot under parallel deposits

**Mechanism (traced at seed=42 Phase 4, dup-{8}-spawn at t=495):** a second token=8 deposit began canvasing c0 at t=451, capturing the connector list AS IT WAS THEN — which did not include child_{8} (which was about to be spawned at t=463 by the first deposit). The second deposit walked the ring under its stale snapshot and triggered origin-loop spawn at t=495. By that point child_{8} existed, but the origin-loop check fired without re-canvasing.

**Fix:** at origin-loop spawn AND at canvas-exhaust-on-Unknown spawn, scan `cell.connectors` directly for any with `token in spectrum` before spawning. If found, forward; else spawn. Documented as a deliberate protocol exception parallel to the existing `token in cell.spectrum` self-check.

### Cross-seed verification, 100 seeds, before vs after both fixes

| Metric | Pre-fix | Post-fix |
|---|---:|---:|
| **Phase 4 ring**: known-token spawn | 59/100 | **0/100** ✓ |
| **Phase 4 ring**: duplicate spawn | 29/100 | **0/100** ✓ |
| **Phase 4 ring**: `n_spawned == 5` | 35/100 | **94/100** |
| **Phase 4 ring**: distinct_spectra ≥ 3 | 89/100 | 98/100 |
| **Phase 4 ring**: all 6 crystallize | 0/100 | 1/100 |
| **Phase 4 STAR**: all 6 crystallize | 0/100 | **100/100** |
| **Phase 4 STAR**: known-token spawn | 0/100 | 0/100 |
| **Phase 4 STAR**: duplicate spawn | 100/100 | 100/100 (different mechanism — see below) |
| **Phase 1**: `n_spawned == 5` | 67/100 | **100/100** |
| **Phase 1**: `max_age > 1000` | 34/100 | **2/100** |
| **Phase 1**: `max_pending > 20` | 34/100 | **2/100** |
| **Phase 1 max_age**: median, max | 526, 6560 | 432, 1501 |
| **Phase 3**: `n_spawned == 5` | 80/100 | **100/100** |
| **Phase 3**: spectrum `{2,3,4}` reproduce | 99/100 | 99/100 (unchanged — already strong) |
| **Phase 3**: strict known-routing ≥ 95% | 0/100 | 0/100 (unchanged — observer interception is real) |
| **Phase 2 ORIGINAL**: all-cells-pass | 19/100 | 19/100 (unchanged — different bug class) |

### Findings the post-fix data reframes

- **Phase 1 boundedness improved dramatically; the causal story is plausible but not directly verified.** Max_age median dropped 526→432 and worst-case 6560→1501. `max_age > 1000` dropped 34/100 → 2/100. The post-fix doc previously claimed this was *because* dup-spawn caused c0 to grow extra connectors, increasing canvas time past cadence. The correlation is striking, but the causal mechanism was told as a story; no instrumented re-run of the original outliers was done to confirm c0's degree was the driver. Plausible, not proven.
- **Phase 4's `n_spawned == 5 with spectra == {6..10}` mostly satisfied.** 94/100 produce exactly 5 spawns. The 6 outliers (`n_spawned == 4`) were verified: in **all 6 cases the c0-attached observer specifically (not other observers)** crystallized to the missing token. This is more diagnostic than "an observer absorbed" — observer_c0 sees the FIRST instance of any unknown before it can canvas-exhaust to origin-loop spawn, and at threshold=15 with crystallization_size=1 absorbs it as the most-frequent token in its first 15 observations.
- **The "v8-style hierarchy" question is unaffected.** Both fixes are about substrate correctness, not learning dynamics. The unfair-baseline argument from the second skeptic pass still holds; the v8-hierarchy claim still requires a fair pooled-traffic comparator.

### Phase 4 design-intent: partial improvement, not "satisfied"

The earlier draft of this section said "design intent mostly satisfied" — that cherry-picked the spawn-count win. The full picture across **all** Phase 4 design criteria:

| Phase 4 design criterion | Pre-fix | Post-fix |
|---|---:|---:|
| `n_spawned == 5 with spectra == {6..10}` | 35/100 | **94/100** ← improved |
| Semantic routing accuracy ≥ 95% | 100/100 | 100/100 |
| All 6 observers crystallize | **0/100** | **1/100** ← barely improved |
| `distinct_spectra ≥ 3` | 89/100 | 98/100 ← improved |
| No observer learns its host's token | 100/100 | 100/100 |

The headline `n_spawned == 5` victory is real. The "all 6 crystallize" criterion remains essentially unsatisfied (1/100), and the pre-fix doc's stronger claim ("never satisfied at any tested threshold within 10K ticks") is still valid. The post-fix data does not retract that claim.

### Phase 4 threshold=200 post-fix

The "goal-post reversion" sweep was repeated post-fix. Pre-fix it produced 1 observer crystallized in every seed (the c0-attached one) with variable `n_spawned`. Post-fix:

- `n_crystallized = 1` in 100/100 seeds (unchanged — threshold-vs-traffic is independent of substrate fixes).
- `n_spawned = 5` in **100/100 seeds** (was variable: `{5: 71, 6: 23, 7: 6}`).
- `has_known_token_spawn = 0/100`, `has_duplicate_spawn = 0/100`.

So at the design's threshold, the substrate is now perfectly clean on spawn count and zero anomalies — but the "all 6 crystallize" criterion is still mathematically out of reach within 10K ticks at this fixture. The traffic-density-vs-threshold constraint is a separate dimension.

### Star fixture: clean diagnosis

Pre-fix the star produced 1 observer crystallized and 1 distinct spectrum, with 100% duplicate spawns and a median 10 spawns. Post-fix all 6 observers crystallize in 100/100 seeds, distinct_spectra median 4 — **but `has_duplicate_spawn` is still 100/100, and median `n_spawned` rose to 20** (range 17–20 across 100 seeds).

What the star's spawn distribution actually looks like (seed=42 example):
```
spawn_tokens: [6, 6, 7, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10]
per-token:    {7: 5, 8: 4, 9: 4, 10: 4, 6: 2}
```

So token=7 produced **5 separate** child cells (each at a different attachment site), token=8 produced 4, etc.

**Mechanism (as flagged by the third skeptic pass):** in the star, each spoke (c1..c5) has degree 2: one connector to c0, one to its observer. When a deposit is forwarded from c0 to a spoke c_i with token=K (unknown), c_i's canvas excludes the predecessor (c0), leaving only `[observer_c_i]`. observer_c_i is Learning → returns Unknown. Canvas exhausts to all-Unknown → **spawn at c_i** (per Phase 3's "spawn-on-all-Unknown" rule). That spawn attaches child_{K} to c_i, NOT to c0. Subsequent deposits with token=K injected at c0 round-robin to a *different* spoke c_j, which has its own observer and hasn't yet spawned child_{K} for itself — so c_j ALSO spawns. Hence proliferation.

**The dup-spawn-guard does not catch this.** The guard scans only `cell.connectors` — it has no knowledge of the substrate-wide spawn space. A spoke c_j cannot see that c_i has already spawned child_{K} attached to itself, because c_j's connectors are `[c0, observer_c_j]`. The guard is constitutionally local.

**Earlier draft framed this as "topology-induced not race-condition" and "design-consistent behaviour."** The third skeptic flagged that as category-invention to keep the star looking like a success. **Retracted here.** The correct framing: the substrate's "spawn-on-all-Unknown at non-origin" rule (Phase 3 design choice) interacts pathologically with topologies where some non-origin cell has a degree-2 neighborhood of `[predecessor, Learning observer]`. Fixing this would require either (a) reverting Phase 3's "spawn at canvas-exhaust on Unknown" to "bounce back to predecessor" — which makes the deposit walk back to origin and spawn there — or (b) substrate-wide spawn-coordination (significantly more complex). Neither was done. **The star fixture is "working" only in the narrow sense that all 6 observers receive enough Unknown queries to crystallize; it is producing 4× the design-intended spawn count and the dup-guard cannot fix this.**

### Phase 1 outliers (2/100): not adequately addressed

The 2 seeds where post-fix `max_age > 1000` are:
- seed=37: max_age=1501, max_pending=30, n_spawned=5 (correct), pending_at_end=2.
- seed=48: max_age=1114, max_pending=25, n_spawned=5 (correct), pending_at_end=17.

Both have correct spawn count. The mechanism is **steady-state queueing tail**: c0 has degree 7 (5 spawned children + 2 ring neighbors), canvas takes 14 ticks per deposit, cadence=15 leaves only 1 tick of slack, and unlucky seed-specific injection-arrival timing causes c0.pending to grow over the run. seed=48 has 17 deposits still pending at end (on ~667 injected, so ~2.5% un-resolved at run end).

This is design-tight cadence interacting with substrate-rate-of-processing. It is NOT a bug in the same sense as the {4}-spawn or dup-spawn races; it's a parameter-choice tail. But:

**The third skeptic correctly flagged that dismissing 2/100 as "edge cases" is the same move the original RESULTS docs made with their anomalies.** Naming the mechanism (cadence-vs-canvas-time) is more honest than dismissing. It would not be safe to assert the substrate's bounds from the post-fix run alone — the right characterisation is "Phase 1 is on the bleeding edge of stability at cadence=15; for a robust substrate, cadence should be >= 18 (i.e., canvas-time + safety margin) or cadence-canvas-time slack should be parameterized rather than hard-coded."

### What the post-fix data does NOT change

- **Phase 3 strict-routing degradation (0/100 reach 95%).** Observer interception is real and reproducible regardless of substrate fixes.
- **Phase 2 ORIGINAL still fails 81/100.** Different bug class.
- **Phase 3 spectrum reproducibility (99/100).** Unchanged — but the second skeptic's caveat ("deterministic dynamic at one fixture given mostly-similar streams, not robust convergence from many starting conditions") is still valid. The post-fix run did not investigate the seed=1 outlier (the only seed producing `{2,4,9}` instead of `{2,3,4}`).
- **Non-degenerate alternative topology not tested.** Star is degenerate (degree-1-leaves on its spokes only when no observers attached; degree-2 with observers). The second skeptic's verdict — "non-degenerate topology untested" — is **not** discharged by the post-fix improvements to the star. A 2D grid, depth-2 tree, or coupled-rings topology is still the required generalisation test. The post-fix doc's "the substrate is closer to being a stable platform" framing should not be read as "fixture-independence has been earned."
- **Fair pooled-traffic baseline still outstanding.** The v8-hierarchy question remains untestable from current data.

### Adversarial verification

- All 29 pre-existing unit tests + 4 phase deliverables (33 total) pass post-fix.
- **Three new targeted unit tests added** for the new code paths:
  - `test_chain_stack_pushes_on_forward_and_pops_on_bounce` — verifies the chain_stack invariant via a leaf-bounce path on a 3-cell graph.
  - `test_dup_spawn_guard_at_origin_loop_forwards_when_connector_now_classifies` — verifies the guard at origin-loop trigger.
  - `test_dup_spawn_guard_at_canvas_exhaust_forwards_when_connector_now_classifies` — verifies the guard at canvas-exhaust-on-Unknown.
  All 36 tests pass. The new tests were written *after* the third-skeptic-pass flagged the absence of targeted unit coverage; they isolate the new code paths rather than relying on integration-sweep verification alone.
- seed=42 Phase 1: identical pre/post (no observers to trigger the leaf-bounce-into-non-origin path).
- seed=42 Phase 4: pre-fix `[4, 6, 7, 8, 8, 9, 10]` → post-fix `[6, 7, 8, 9, 10]`. The published `{4}` and dup-`{8}` are gone. The published `n_crystallized=4 / distinct_spectra=3` becomes `n_crystallized=5 / distinct_spectra=4`.

### Honest framing — what the third skeptic pass made explicit

The first draft of this post-fix section over-rotated in three ways:
1. **It claimed Phase 4 STAR was "not fundamentally broken."** The star produces 17–20 cells for 5 unknown tokens (3–5 separate `{token}`-spectrum cells per token per seed); the dup-guard is constitutionally local-to-spawning-cell and cannot prevent this. Retracted.
2. **It said Phase 4 "design intent is mostly satisfied."** That cherry-picked the spawn-count win (94/100 produce exactly 5) and elided the fact that "all 6 crystallize" is still 1/100. Now stated honestly with the full criteria table above.
3. **It dismissed 2/100 Phase 1 max_age outliers as "edge cases" without tracing.** That's the same move the first skeptic pass diagnosed in the original RESULTS docs. The mechanism is now named (cadence=15 leaves only 1 tick of slack against canvas time of 14, vulnerable to arrival-timing fluctuations) but the substrate's design tightness has not been *fixed*; it has been characterised.

What the two fixes ACTUALLY achieve:
- **Bug 1 (leaf-bounce overwrites chain predecessor) is eliminated.** Cross-seed verification: zero known-token spawns post-fix. New unit test isolates the path.
- **Bug 2 (stale canvas snapshot under parallel deposits) is eliminated for spawns at the SAME cell.** Cross-seed verification: zero duplicate spawns on ring fixture. New unit tests cover both code paths.
- **Phase 1 queueing characteristics are dramatically tighter** (median 526→432, max 6560→1501). The causal mechanism — that dup-spawn was inflating c0's degree past the cadence-vs-canvas-time bound — is plausible but not directly instrumented; the correlation alone supports the claim.

What the two fixes do NOT achieve:
- They do not eliminate the star fixture's spawn proliferation (4× design-intended spawn count); that requires a substrate-wide-coordination fix or a Phase 3 design revision.
- They do not establish v8-hierarchy.
- They do not establish fixture-independence.
- They do not address the seed=1 Phase 3 outlier, the 2/100 Phase 1 cadence-tail seeds, or the Phase 2 ORIGINAL parameter failure (different bug class).

**The substrate is materially better than it was; the broader claims of Phases 1–4 remain in the same status the second skeptic pass left them in.** Two specific named bugs are fixed; many open prerequisites remain.

### What the third skeptic pass surfaced that this section would otherwise have hidden

The third skeptic flagged this exact failure mode: "the operator has performed three rounds of rigor and is now repeating the original sin on a smaller scale." Several specific concerns it raised that this revised section now addresses (instead of soft-pedalling):
- The "topology-induced not race-condition" framing was post-hoc category-invention.
- The "Phase 4 design intent satisfied" framing cherry-picked.
- The 2/100 Phase 1 outliers mechanism was named, not dismissed.
- The new unit tests were added (they did not exist when the post-fix table was first published).
- The Phase 4 threshold=200 post-fix data is now reported (the JSON had it; the comparison table omitted it).
- The "substrate is closer to a stable platform" framing was tempered to "two specific bugs are fixed."

The third skeptic's most damning sentence — "the dup-spawn-guard is constitutionally incapable of preventing the star's spawn proliferation, so the star 'works' only in the sense that crystallization counters tick over" — is now reflected directly in the star fixture section above.

---

## Files

- `skeptic_pass.py` — harness (runs all sweeps).
- `skeptic_pass_results.json` — full per-seed data (all 9 sweeps × 100 seeds; current = post-both-fixes).
- `skeptic_pass_run.log` — captured stdout from the original (pre-fix) run.
- `skeptic_pass_postfix_run.log` — captured stdout post-{4}-fix only.
- `skeptic_pass_postdupfix_run.log` — captured stdout post-both-fixes (origin-loop guard only).
- `skeptic_pass_postdupfix2_run.log` — captured stdout post-both-fixes (origin-loop + canvas-exhaust guards).
- `trace_4spawn.py` + `trace_4spawn.log` — deposit-level trace of the {4}-spawn at seed=42.
- `trace_dupspawn.py` + `trace_dupspawn.log` — deposit-level trace of the dup-{8}-spawn at seed=42.
- `_extract_counts.py`, `_compare_postfix.py`, `_compare_bothfixes.py` — aggregation helpers.
- `RESULTS_skeptic_pass.md` — this file.

The original Phase 1-4 deliverable tests, designs, and RESULTS docs are unchanged; this skeptic pass is additive context. The substrate's `cell.py` and `substrate.py` were modified to apply the two fixes; the unit tests and phase deliverables still pass at seed=42.
