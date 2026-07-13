# RAW 132 — The Untested Capacitor

### *Why Four Experiments Triangulated Around the Synthesis Without Finding It*

**Author:** Tom (insight), Claude (articulation)
**Date:** 2026-04-28
**Status:** Synthesis draft. No experiment yet built on the basis of this reframe.
**Prerequisites:** RAW 126 (Trit Is a Capacitor), RAW 127 (Trit Has Depth), RAW 128 (Energy Partition), RAW 130 (It Rotates Because It Consumes), RAW 131 (Lineage Substrate)
**Closes (provisionally):** Experiments 131, 132, 133, 134 — as a set, not individually. Each remains a valid negative result on its own substrate; this RAW reframes the *pattern* across them.

---

## What this document is

This is a **RAW** document. The 'R' is for raw — raw thinking, raw notes,
raw materials. RAWs are the project's working notebooks: every idea
considered, every dead end explored, every reference followed,
every wrong turn made — recorded here so the framework's actual reasoning
trail is visible, not just its current best version. RAWs are explicitly
*not* polished publication-ready papers. They include:

- Provisional commitments alongside the alternatives that lost.
- Hypothesis sets where most candidates will be falsified.
- References to inspirations even when those inspirations turned out
  irrelevant or wrong.
- A document-history record of how the thinking evolved.
- "Wrong turns" sections capturing ideas that were considered and rejected,
  with reasoning for why.

If something in this RAW seems to contradict something else, that's
*intentional* — it's the layered record of thinking, not a polished
synthesis. Where contradictions matter operationally (e.g., for the
next experiment), they're called out explicitly.

This particular RAW evolved across multiple sessions and brainstorming
arcs on 2026-04-28. See §11 (Document History) for the trace.

---

## Abstract

Four experiments, four substrates, four different negative results. Each
earned a piece of the picture and falsified another. None combined honest
entity coherence with field-at-distance; the shared failure was read in
RAW 132 v0 as evidence that *no discrete substrate can do both*. This
document withdraws that reading.

The reframe: every one of those four experiments **dropped half of the
capacitor model**. RAW 126 specified the substrate's hardware as a
charge-discharge cycle with continuous internal accumulation and discrete
external events. RAW 127 added that the charging phase has *depth* — the
trit is not point-like, it has internal real-valued state invisible until
discharge. The framework's substrate is therefore neither integer-only
nor real-only; it is **both, in the same hardware unit**. Each of
Experiments 131/132/133/134 picked one half — integer-only flow, or
real-only diffusion — and lost the other. The synthesis target may
already be specified in RAW 126/127 and simply has not been
operationally implemented.

Five operational questions remain unanswered in RAW 126/127 themselves
and must be pinned down before the capacitor can be tested as a substrate
primitive: **when does a capacitor count as an entity?** **When does it
really fire?** **How big is it (and what determines its size)?** **What
mechanism produces spatial stretching?** **What is the observer's
reading function** (i.e., how does substrate state get interpreted as
"where is the entity")? This document articulates each gap as a set of
mutually exclusive falsifiable hypotheses, commits provisional leading
candidates, and lays out a scientific-elimination strategy that
distinguishes them in future experiments. The substrate has three
simultaneous "growth" registers — charge level (RAW 127), threshold
(adaptive sizing), connector load (current edge state) — and discharge
is the only event by which information leaves a cell. The slogan is
**"grow until observed."** Drift, in this framework, is not a substrate
phenomenon — it is the observer's reading function (§3.5) constructing
"where-is-the-entity" from the spatial distribution of recent firings,
and that reading drifts as substrate state evolves.

The capacitor model is positioned as going *beyond* quantum mechanics
rather than as a tick-frame restatement of it: the same "grow until
observed" structure that QM postulates as wave-function-evolution +
measurement-collapse becomes hardware mechanism — three layered substrate
states that grow privately and crystallize publicly only at discharge.
Time dilation, spatial stretching, the Heisenberg structural-invisibility
of the charging phase, and the bimodal observation distribution from
RAW 127 all fall out of the same three-layer mechanism.

The falsifiable claim that closes this RAW is sharper than v0's: *if a
substrate that implements the three-layer "grow until observed"
mechanism also fails to combine entity coherence with field propagation,
then the discrete-substrate-limit claim is supported; if it succeeds,
the failures of 131–134 were artifacts of simplification, and the
framework remains whole with the synthesis target operational rather
than aspirational.*

---

## 1. The Four Experiments and What Each Simplified Away

| Exp | Substrate primitive | What it earned | What it dropped from the capacitor model |
|---|---|---|---|
| **131** | Lineage tree + integer flow per tick | Tree topology as a permanent backbone | Continuous charging; discharge thresholds. Flow was instantaneous-discrete. |
| **132** | Anisotropic-connector RGG + propagation | Per-edge Schwarzschild radial (ratio 1.01 at r=5) | Discrete discharge events; threshold dynamics. Propagation was pure-real, no firing. |
| **133** | Closed-loop integer hold-and-fire on RGG | Exact conservation; ρ ∝ r⁻¹ with sink | Continuous internal charging *between* fires. "Hold" was zero-state; "fire" was binary instantaneous; no charging phase visible. |
| **134** | Integer paint + decay on cubic lattice; per-cell threshold = K | Exact fixed-point pattern coherence; sign-blind matter/antimatter | Continuous internal state; gradual charging. Paint instantaneous, decay instantaneous, no real "charging" between paint events. |

Each experiment's negative result is well-founded *on its own substrate*.
The lineage tree doesn't recover Newton; the anisotropic RGG doesn't get
horizon scaling; closed-loop integer dynamics give the wrong exponent;
discrete CA renewal can't reach across vacuum. Each diagnosis is
specific to that substrate's commitments and is correctly captured in
its closure.

What the four experiments **have not done together**, and what RAW 132 v0
nearly missed: none of them implemented the **continuous-internal /
discrete-external duality** that RAW 126/127 identified as the
substrate's core hardware. Each picked a half. The synthesis may live
in the unselected half.

---

## 2. What the Capacitor Model Already Specifies

RAW 126's central commitment, restated:

> The connector carries continuous deposits. The capacitor accumulates
> them. When accumulated charge crosses a threshold, the capacitor
> discharges as a discrete event. Quanta are not properties of the signal;
> they are *emergent* properties of the consumer's threshold-triggered
> discharge.

RAW 127 sharpens it:

> The charging phase is itself continuous and has internal structure
> that is invisible to external observers until discharge. The trit has
> *depth* — it is not a dimensionless three-state switch but a process
> with real-valued internal state. Observation can only happen via
> another trit's discharge; the charging phase is structurally invisible.

The two RAWs together commit the framework to a hardware substrate where
each cell is **simultaneously**:

1. **A continuous-state accumulator** during charging — internal real-valued
   charge level, dynamics unobservable from outside.
2. **A discrete-event source** at discharge — fires a quantum, propagates
   deposits to neighbors via connectors, returns to Empty.
3. **A neighbor consumer** between firings — receiving deposits from
   other capacitors' discharges, accumulating them into its own
   charging state.

This is not "real-valued substrate" *or* "integer substrate." It is *both
at once*, in the same hardware unit, with the duality being the central
mechanism rather than a limitation.

Exp 131/132 implemented (1) and (3) but not (2). Exp 133/134 implemented
(2) and (3) but degenerated (1) into instantaneous transitions. None
implemented all three.

---

## 3. The Five Operational Gaps in RAW 126/127

The capacitor model is specified as hardware, but five operational questions
remain underdetermined. They are not framework gaps in principle — they
are gaps in operational pinning that any substrate-implementation must
resolve before code can be written.

**Each gap is treated as a set of mutually exclusive hypotheses.**
Provisional commitments select one hypothesis per gap as the leading
candidate, but the alternatives are explicitly preserved as falsifiable
sibling claims. The next experiment program is structured around
*scientifically eliminating* the alternatives — running configurations
that each non-selected hypothesis predicts to fail, until the survivors
are the framework's actual answers. This is the only discipline that
keeps the project from parameter-tuning toward desired outcomes (the
failure mode flagged in Exp 134 brainstorming as "honest emergence
claims" — see memory `feedback_honest_emergence_claims.md`).

The five gaps emerged across two brainstorming sessions on 2026-04-28:

| Gap | Question | Hypotheses |
|---|---|---|
| §3.1 | When does a capacitor count as an entity? | H1.1–H1.5 |
| §3.2 | When does it really fire? | H2.1–H2.4 |
| §3.3 | How big is it? | H3.1–H3.5 |
| §3.4 | What stretches space? | H4.1–H4.5 |
| §3.5 | What is the observer's reading function? | H5.1–H5.6 |

### 3.1 When Does a Capacitor Count as an Entity?

A capacitor at charge ≈ 0 for many ticks isn't an entity — it's just
hardware sitting there. A capacitor that has just discharged isn't an
entity in this tick — it's the *event of an entity firing*. A capacitor
mid-charge — at, say, 47% — is *something* but not yet a fired event.

**Hypotheses:**

- **H1.1** (provisional): An entity is any capacitor whose charge has
  remained above 50% of its threshold for at least one tick.
- **H1.2**: An entity is any capacitor with charge above *any* non-trivial
  level (e.g., > 10% of threshold). Wider definition; everything that's
  charging counts.
- **H1.3**: An entity is any capacitor that has fired at least once
  within a recent window (e.g., last K ticks). Identity is *defined by*
  past discharge.
- **H1.4**: An entity is only a capacitor currently participating in a
  renewal cycle (a recurring firing schedule). Isolated charging cells
  don't count; only stable patterns do.
- **H1.5**: An entity is any capacitor with active connectors (non-zero
  current load). Identity = communicating.

**Provisional commitment:** H1.1. Makes "entity" a *temporal phase* of
the capacitor cycle, not a static cell property.

**Falsification path:** Each hypothesis predicts a different cell-count
when an observer asks "how many entities exist on this substrate now?"
Experiments measuring entity-count vs. parameter sweeps distinguish
them. H1.4 is most exclusive (only stable patterns); H1.2 and H1.5 are
most inclusive (transients count). The observer-reading function (§3.5)
operationalizes which one the framework commits to.

### 3.2 When Does a Capacitor Really Fire?

RAW 126 says firing happens when charge crosses threshold. RAW 127 adds
that observation outcomes follow a probability distribution that is
*bimodal* (peaked at empty and at threshold) but doesn't operationalize
the threshold itself.

**Hypotheses:**

- **H2.1** (provisional): Fixed threshold, deterministic firing.
  Discharge fires at exactly 100% charge. Simplest; closest to a TTL
  inverter; matches Exp 133's hold-and-fire approximation. Preserves
  substrate determinism. **Cost:** RAW 127's bimodal observation
  distribution must emerge from aggregate dynamics (many capacitors),
  not from per-cell randomness.
- **H2.2**: Probabilistic threshold. At any charge level above some
  floor, there is a probability of firing per tick. P(fire | charge)
  produces the bimodal distribution directly. Matches QM's
  wave-function intuition. **Cost:** introduces per-cell randomness,
  which the framework explicitly avoids ("everything is deterministic
  at the substrate layer").
- **H2.3**: Rate-dependent threshold. Firing happens when charge *rate*
  (charge per tick) crosses a threshold. A capacitor charging fast
  fires sooner than one charging slowly. Most "capacitor-like" in
  electrical-engineering terms.
- **H2.4**: Threshold itself is dynamic per cell, varying with charging
  speed or recent history. A combined version of H2.3 + adaptive
  threshold dynamics from §3.3.

**Provisional commitment:** H2.1. Preserves substrate determinism;
defers the bimodality question to aggregate-level emergence.

**Falsification path:** H2.1 vs. H2.2 distinguish on observed firing
distribution shape under controlled identical inputs (H2.1 gives
deterministic timings; H2.2 gives probabilistic ones). H2.3 vs. H2.1
distinguish on whether two cells with identical accumulated charge
but different charging *speeds* fire at different times — H2.3
predicts yes; H2.1 predicts no. Phase 2+ experiments with multiple
patterns at different distances from a planet (different deposit-arrival
rates) distinguish H2.1 from H2.3.

### 3.3 How Big Is a Capacitor?

RAW 127 said the trit has "depth," but didn't pin down whether all
trits have the same depth.

**Hypotheses:**

- **H3.1**: Uniform threshold (all capacitors identical). Simplest,
  fully homogeneous substrate. **Falsification predictions:** doesn't
  address Exp 118's saturation problem (flat field), "star fills any
  graph" problem (no characteristic size), or Exp 128 v11 Phase 6's
  radial isotropy. Probably too flat to support physics.
- **H3.2**: Sized by structural rule (e.g. connectivity). Threshold
  scales with degree of connectivity, lineage age, or another
  graph-topology property. Gives natural scale separation;
  high-connectivity regions are slower. Partially addresses Exp 118's
  saturation and "star fills any graph"; doesn't directly address
  radial isotropy. **Cost:** rule itself needs justification.
- **H3.3**: Adaptive thresholds (use-history at the cell level).
  Threshold rises with firing history; cells become "fatigued" with
  use. Like neuronal homeostasis. **Directly addresses** Exp 118's
  saturation (fatigue prevents saturation) and "star fills any graph"
  (homeostasis caps growth at characteristic radius). **Plausibly
  addresses** Exp 128 v11 Phase 6's radial problem via fatigue
  gradient near mass.
- **H3.4**: Heterogeneous by fiat (initial distribution). Doesn't fix
  any of 118 or 128's failures dynamically; only as good as the
  initial distribution chosen.
- **H3.5** (provisional): H3.2 + H3.3 combined. Initial threshold from
  connectivity-degree (H3.2); threshold then adapts with firing history
  (H3.3). Captures both structural baseline and dynamic homeostasis.

**Provisional commitment:** H3.5. Validated by Exp 132 Phase 1
(2026-04-28) — the K=4 cycle sustained 5,000 cycles with adaptive
thresholds and connectivity-uniform baseline (cubic lattice has
uniform degree 6 except at boundaries, so H3.2 and H3.1 are
indistinguishable on cubic; H3.3 was the operative addition).

**Falsification path:** Phase 2 with planet pattern. H3.1 predicts
flat threshold(r) profile; H3.3/H3.5 predict threshold rises near
planet (cells in heavy deposit traffic fatigue more). Direct
comparison of measured threshold(r) vs. predictions falsifies the
losing hypotheses.

The "no history" objection to H3.3/H3.5 is real but answerable:
cell-level threshold drift IS history, but it lives at the *firmware*
layer (slow-evolving hardware property), not the entity-state layer
(where RAW 134's decay-everything principle most matters).
Threshold-as-firmware is admissible the way decay-rate-as-firmware
is admissible — both are slow, hardware-level, not entity-history.

### 3.4 What Mechanism Produces Spatial Stretching?

Exp 128 v11 Phase 6 proved the substrate gets gravitational time dilation
(slope −1.094 vs Einstein's −1.000) but fails radial spatial stretching
on isotropic graph. Exp 131_b (formerly Exp 132 — the anisotropic
connectors experiment, now renamed under the RAW 131 family) tried
built-in connector anisotropy and earned per-edge Schwarzschild radial
(ratio 1.01 at r=5) but failed horizon scaling (r_s ∝ M off by factor
0.19–0.58).

**Hypotheses:**

- **H4.1** (provisional): Connector load (current state). Each connector
  has a `current_load` (deposits in transit); propagation time scales
  with load. Near a massive star, deposit traffic is heavy → connectors
  loaded → propagation slowed → radial paths through high-traffic
  regions effectively longer than tangential. Spatial stretching as
  current substrate state, no history beyond moving-window load.
- **H4.2**: Built-in connector anisotropy (Exp 131_b approach).
  Connectors near mass have geometrically different lengths by
  construction. **Status:** falsified for horizon scaling (r_s ∝ M
  failed). Per-edge Schwarzschild radial earned, but only as a
  parameter-tuned profile, not from substrate dynamics.
- **H4.3**: Lineage tree structure (RAW 131 / Exp 131_a approach).
  Spatial distance derives from lineage-tree relationships;
  spatial stretching = stretching of lineage-paths near mass.
  **Status:** falsified for Newton recovery (lineage tree + local
  conductance flow does NOT recover Newton, per Exp 131_a closure).
- **H4.4**: Capacitor size at the cell level (cell-level threshold
  drives propagation indirectly). High-threshold cells fire slower →
  longer interval between deposits leaving them → effectively slower
  propagation through them. Not directly tested; collapses with
  H3.3 / H3.5 if both are taken seriously simultaneously.
- **H4.5**: Discharge wave timing / refractory periods asymmetric near
  mass. Cells that just fired have a brief unresponsive period; near a
  massive star, cells fire often, refractory periods overlap, deposits
  arriving during refractory are dropped or delayed. Could give an
  emergent "horizon" where refractory period equals firing rate.

**Provisional commitment:** H4.1, with H4.4 as a possible co-mechanism
(if H3.3/H3.5 holds, H4.4 is partly automatic and may be hard to
disentangle from H4.1). H4.2 and H4.3 falsified by prior experiments.

**Falsification path:** Phase 2 with planet pattern, measure
connector_load(r) profile around planet. If it matches GR's `g_rr`
shape (1/(1−2M/r)), H4.1 supported. If load is flat regardless of
distance, H4.1 falsified — would force a return to H4.2 with new
mechanism (perhaps tuning connector anisotropy from current substrate
state rather than initialization). H4.5 distinguishable by per-cell
firing-history measurements: do cells near mass spend more time in
refractory than expected from H3.3 alone?

The "no history" principle is preserved at the connector level under
H4.1 — exactly where it most matters for substrate ontology, since the
connector is the relational primitive (RAW 131). History stays confined
to the firmware layer of the cell (§3.3), not the relational layer.

| Mechanism | Where it lives | What it produces | Requires history? | Status |
|---|---|---|---|---|
| H3.3/H3.5 (adaptive capacitor) | Nodes | Time dilation | Yes — firmware-level | Phase 1 PASS |
| H4.1 (load-driven connectors) | Edges | Spatial stretching | No — current state only | Provisional, Phase 2 will test |
| H4.2 (built-in anisotropy) | Edges | Spatial stretching | No | Falsified (Exp 131_b) |
| H4.3 (lineage geometry) | Tree edges | Spatial stretching | Embedded structure | Falsified (Exp 131_a) |

### 3.5 What Is the Observer's Reading Function?

This gap was surfaced 2026-04-28 after Exp 132 Phase 1 PASS, when the
question "what does it mean for a pattern to drift toward a planet?"
revealed that drift is not a substrate phenomenon — there's no rule
that moves patterns. Patterns are sets of cells; cells don't move;
substrate state evolves. **What we call "drift" is what an observer
reads when interpreting substrate state.**

The substrate has no notion of "the entity is at position X." That's
constructed by an observer integrating substrate state into a
"where-is-the-entity" reading. As substrate state evolves (cells fire,
thresholds rise, loads accumulate), the observer's reading evolves,
and this is drift. The reading function is therefore an *observer
commitment*, not a substrate rule — but it must be specified explicitly
for any experiment that claims to measure motion.

This connects directly to RAW 77 ("All observations are detections of
past imprints in the gamma field. Therefore, every measurement reveals
the historical position of an entity, not its present state.") and
RAW 127 ("Observation requires discharge from the observed").

**Hypotheses:**

- **H5.1** (provisional): Centroid of cells fired in last N ticks.
  Simplest. Observer reads the spatial distribution of recent firing
  events, computes the geometric centroid. Drift = centroid trajectory
  over many cycles. Choice of N is itself an observer parameter
  (small N → noisy; large N → laggy).
- **H5.2**: Charge-weighted centroid. All cells with non-zero charge
  contribute, weighted by charge level. Captures cells in the
  charging phase, not just dischargers. Conflicts with RAW 127's
  "charging is structurally invisible" — falsifiable IF observer can
  somehow read charge level (which the framework says they can't).
- **H5.3**: Threshold-elevation centroid. Cells whose threshold has
  risen above baseline contribute. Picks up "anywhere the substrate
  has been doing recent work." Equivalent to a long-window firing
  history.
- **H5.4**: Discharge-density map peak. Construct a 3D density map of
  recent firing events; the entity's "position" is the peak of the
  map. More robust than centroid for non-spherical patterns; can
  represent multiple-peak (multi-entity) configurations.
- **H5.5**: Connectivity-of-firing centroid. Centroid of the
  connected component of recently-fired cells (cells that fired in
  last N ticks AND are face-adjacent to at least one other recent
  firer). Distinguishes coherent patterns from scattered noise.
- **H5.6**: Bayesian inference. Observer maintains a prior over
  "where might the entity be," updates with each observed discharge.
  Most powerful but introduces an explicit prior (parameter choice).
- **H5.7** (added 2026-04-28 after Phase 2): **Self-subtracting
  reading.** When an entity-as-observer measures its own environment,
  it must subtract its own contribution from substrate state.
  Equivalent under H5.x for an external god-observer with no "self,"
  but materially different for any entity-relative measurement.
  Without this, an entity reads its own dominant field and sees
  itself as static (the "frozen planet" failure mode documented in
  Exp 64_109 v8/v21).

**This hypothesis (H5.7) is not a new free choice — it is a prior
framework commitment that RAW 132 §3.5's earlier formulation overlooked.**
Two prior anchors:
- **RAW 044 (Fallible Commit Principle):** *"Every commit is an
  irreversible choice that closes the observer's buffer ... Buffer
  closure: the commit fixes a tick sequence that already belongs
  to the past. New buffer: a new window immediately opens to collect
  further ticks ... Lag of reality: the observer always reconstructs
  the past, never the live tick stream."* Establishes the window-commit
  pattern: observer reads buffer N, commits at end of N, opens N+1.
- **Exp 64_109 v8 (operational, February 2026):** *"Self-subtraction
  resolves the SNR problem — entities detect each other's field."*
  Self-subtracting transport on a cubic lattice produced attractive
  force; without self-subtraction, the "frozen planet" bug manifests
  (planet placed next to a star with zero established field escapes
  immediately because it perceives only its own deposit pattern).

**Provisional commitment:** H5.1 with N = K (one full cycle worth of
firings) **plus self-subtraction (H5.7) for any entity-relative
measurement.** External-observer measurements (the "god view" RAW 132
implicitly used through Phase 2) do NOT need self-subtraction; an
external observer has no self-contribution to subtract.

**Falsification path:** Each hypothesis predicts a different drift
trajectory under the same substrate dynamics. Phase 2 measures
trajectory under H5.1, then re-analyzes the same recorded firing data
under H5.3, H5.4, H5.5 (no new substrate runs needed; these are
post-hoc readings of the same recorded data). H5.6 requires more
machinery and is deferred. **H5.7 (self-subtracting) requires a new
experimental setup:** the observation must distinguish "from outside"
(god view, no self to subtract) from "from inside the test pattern"
(must subtract test pattern's own contribution). Phase 2 measured god
view; Phase 2A.5 will measure entity-relative.

**This is the key insight that distinguishes Phase 2 from Exp 134
Phase 2.** Exp 134 Phase 2 measured connected-component identity and
centroid trajectory of *tagged* test pattern cells, found contact =
decoherence. With H5.x reading functions, the same substrate behavior
might read as "entity transitioned to neighboring cells" rather than
"entity died." Drift, not decoherence — depending on the reading. And
under H5.7, **the substrate behavior viewed by the test pattern
(self-subtracted) is materially different from the god view we
recorded in Phase 2.** Phase 2's flat-load and non-monotonic-threshold
profiles likely reflect god-view contamination by the test pattern's
own halo; the test pattern's actual perceived environment is yet
to be measured.

### 3.6 Falsification Strategy: Scientific Elimination

The five gaps above commit to provisional hypotheses (H1.1, H2.1,
H3.5, H4.1, H5.1). The next experiment program is structured to
*systematically falsify the alternatives*, not to confirm the
provisional commitments.

| Hypothesis | Status | Falsification experiment |
|---|---|---|
| H1.1–H1.5 | All open; provisional H1.1 | Entity-count vs. parameter sweep, Phase 2 |
| H2.1 | Provisional | Phase 2 firing-distribution measurement; aggregate bimodality test |
| H2.2 | Open | Same — H2.2 predicts per-cell stochasticity that H2.1 doesn't |
| H2.3 | Open | Multi-distance pattern test — H2.3 predicts firing-rate-dependent firing |
| H2.4 | Open | Combined with §3.3 dynamics; harder to isolate |
| H3.1 | Probably-falsified by Exp 118 saturation | Re-run with uniform threshold, see if saturation returns |
| H3.2 (alone) | Open | Disable adaptation in §3.3; see if structural baseline alone supports patterns |
| H3.3 (alone) | Open | Enable adaptation but uniform baseline; compare to H3.5 |
| H3.4 | Probably-falsified by reasoning, not experiment | Skip unless 3.5 fails |
| **H3.5** | **Provisional, supported by Exp 132 Phase 1** | Phase 2 + planet → threshold(r) match GR's time dilation? |
| H4.1 | Provisional | Phase 2 + planet → connector_load(r) match GR's g_rr? |
| H4.2 | Falsified (Exp 131_b) | — |
| H4.3 | Falsified (Exp 131_a) | — |
| H4.4 | Open, may collapse with H3.3 | Hard to disentangle from H3.3; defer |
| H4.5 | Open | Per-cell refractory-period measurement near mass, Phase 2+ |
| H5.1 | Provisional | Phase 2 trajectory under H5.1; compare to predicted-Newton |
| H5.2 | Conflicts with RAW 127 | Theoretical — falsified by RAW 127's charging-invisibility commitment |
| H5.7 (self-subtracting reading) | Required by RAW 044 + Exp 64_109 v8 | Phase 2A.5 (planet-only vs. test-only vs. combined) — superposition test |
| H5.3 | Open | Re-analyze Phase 2 data; compare trajectory to H5.1 |
| H5.4 | Open | Same — post-hoc analysis of Phase 2 data |
| H5.5 | Open | Same — post-hoc analysis of Phase 2 data |
| H5.6 | Open, requires extra machinery | Deferred |

**Phase 2 is therefore not "tune until drift appears"** — it is a
single experimental run that:

1. Implements the substrate per provisional commitments (H1.1, H2.1,
   H3.5, H4.1) and runs with planet + test pattern for many cycles.
2. Records *all* substrate state per tick (charge, threshold, load,
   firing events).
3. Post-hoc applies multiple §3.5 reading functions (H5.1, H5.3,
   H5.4, H5.5) to the same recorded data, comparing trajectories.
4. Measures threshold(r) and connector_load(r) profiles to test
   H3.5 and H4.1 against GR shapes.
5. Reports which hypotheses are supported, which falsified.

This is the experimental discipline that keeps the next phase from
being a parameter-tuning exercise toward a desired outcome.

### 3.6.1 Phase 2 result (2026-04-28): falsification of provisional H3.5, H4.1, H5.1 at trial parameters

**Phase 2 was run on 2026-04-28 immediately after this RAW v3.** Result:
**honest negative.** Three of four hypothesis tests falsified at provisional
parameters; one inconclusive.

| Hypothesis | Phase 2 Result | Evidence |
|---|---|---|
| H3.5 (threshold(r) monotonic) | **Falsified at provisional parameters** | Profile non-monotonic, hump at r=8 (test pattern halo confound) |
| H4.1 (load(r) monotonic) | **Falsified at provisional parameters** | Load profile flat ~1.3 across all radii (saturation under full connectivity) |
| H5.1 (drift toward planet) | **Not supported** | +0.244 cells in x (away from planet, within K-window noise) |
| H5.3/H5.4/H5.5 panel | **Inconclusive — readings collapsed** | All readings agree within 0.05 cells; reading-function distinction collapsed for symmetric/stable patterns |

**Setup:** 21×21×3 cubic lattice, planet K=4 + test K=4 at distance 5,
load_coefficient=0.1, 5,000 cycles, no parameter tuning to chase signal.

**Three honest observations from the falsification:**
1. The test pattern itself confounds the planet's profile measurement — cells at r=5–8 sample both halos simultaneously. **Phase 2A.1 (planet-only) would isolate the planet's signature.**
2. load_coefficient=0.1 may be too weak, OR load equilibrates too fast under full connectivity. **Phase 2A.2 (load coefficient sweep) would resolve.**
3. 21×21×3 may be too small. Patterns 5 cells apart in a 21-cell substrate; halo can't develop a clean radial profile. **Phase 2A.3 (larger substrate, e.g. 41×41×3) would resolve.**

**This does NOT falsify the three-layer "grow until observed" mechanism categorically.** What's been falsified is the simplest implementation at trial parameters in a small substrate with confounded measurement. The hypothesis space narrows; it doesn't collapse.

**Per RAW 132's no-puffery commitment:** Phase 2 reports the falsification honestly. Phase 3 (quantitative GR-fit) is now deferred. Phase 2A (planet-only profile, load sweep, larger lattice, partial connectivity) is the natural next experiment program — each addresses a specific confound from the Phase 2 result.

See `experiments/132_grow_until_observed/RESULTS_phase2.md` for the full per-hypothesis result table.

---

## 4. Why the Capacitor Goes Beyond Quantum Mechanics

Quantum mechanics describes outcomes — discharge events, their
probabilities, their correlations. The capacitor model describes the
*hardware that produces those outcomes*. The two are not in conflict;
they are at different levels of description.

What QM has:
- Probability distributions for measurement outcomes
- Superposition of states until observed
- Wave-function collapse at observation
- Entanglement (correlated discharges across separated systems)

What QM does not have:
- A notion of "entity-formation" as a *temporal phase* distinct from
  "entity-existence." For QM, a particle either exists with some state
  or doesn't. There is no "currently forming, halfway to existing."
- A hardware substrate beneath the wave function. The wave function is
  the description, not the mechanism. QM is famously agnostic about
  what (if anything) is beneath it.
- A reason for the bimodality of observation outcomes other than
  postulate. Born's rule is given, not derived.
- A reason for *why* observation requires interaction. QM postulates
  measurement collapse; it doesn't explain why measurement and collapse
  must coincide.

The capacitor model proposes hardware-level answers to all four:

- "Entity-formation" is the charging phase. A capacitor at 47% charge
  is in a temporal phase that QM has no name for, because QM doesn't
  see the charging phase at all.
- The hardware substrate is the capacitor cycle: connector + accumulator
  + threshold + discharge.
- Bimodality of outcomes follows from the dynamics of charging itself:
  the integral over the charging trajectory weights the endpoints
  (empty and threshold) more heavily than the middle, because the middle
  is unstable — it either drains or fires.
- Observation requires the observed to discharge because the charging
  phase is *structurally* invisible — there are no deposits propagating
  out of a charging capacitor, by construction. Discharge is the only
  way information leaves a capacitor.

This is the sense in which the capacitor model is *beyond* QM, not a
restatement of it. QM describes what observers see; the capacitor model
proposes what happens between observations. If correct, it predicts the
QM observations as derived statistics — and predicts new ones (the
*temporal* phase of entity-formation, with potentially measurable
consequences for how entities respond to external fields during
formation).

---

## 5. The Synthesis: Grow Until Observed

The four operational gaps from §3 and the beyond-QM claims from §4
converge into a single mechanism. Three layered substrate states grow
privately, in parallel; only discharge crystallizes any of them into
public, observable form.

| Layer | What grows | While charging | At discharge |
|---|---|---|---|
| **Charging phase** (RAW 127) | Internal charge level (real, continuous, 0–100% of threshold) | Invisible from outside | Resets to Empty; emits a quantum down all connectors |
| **Adaptive threshold** (§3.3) | Threshold value, slowly with firing history | Cell becomes "heavier"; firing rate drops with fatigue | Each discharge contributes incrementally to its own threshold growth — feedback closes the loop |
| **Connector load** (§3.4) | Deposits in transit on each edge | Local propagation slowed in proportion to load | Discharge releases load downstream — neighbors receive a packet, their charge levels rise |

Each is a "growth" register. Each is invisible from outside between
discharges. Each is reset (or partially released) at discharge. The
discharge event is the **only** mechanism by which information leaves a
cell. This is not a measurement convention; it is hardware constraint:
connectors carry deposits only on discharge events, by construction.

### What this is, expressed in QM language

- **The wave function** = current joint state of (charge level, threshold,
  connector loads) at and around a cell. Real, physical hardware values.
  Not mathematics describing nature; the substrate's own internal state.
- **Wave function evolution** = the three-layer growth, deterministic,
  invisible from outside.
- **Measurement / collapse** = discharge. The only event at which any
  of those values become observable. There is no collapse problem
  because there is no other way for information to leave; "observation
  causes collapse" is "observation is discharge" reread structurally.
- **Heisenberg uncertainty** = the structural invisibility of the
  charging phase. Not an epistemic limit, not a measurement-disturbance
  artifact. The substrate physically cannot share its internal state
  without discharging — connectors aren't carrying anything between
  discharge events.
- **Born rule (probability proportional to |ψ|²)** = derivable in
  principle from charging-trajectory dynamics; the bimodal observation
  distribution in RAW 127 is a first sketch of how this might work.
- **Disturbance from measurement** = mechanical: discharge propagates
  deposits through all connected edges, raising their loads and the
  charging states of receiving cells. The "disturbance" is a real
  physical perturbation, not a metaphysical projection.

### Time dilation and spatial stretching from the same substrate

The same three-layer mechanism produces both relativistic effects:

- **Time dilation** = adaptive thresholds (§3.3). Capacitors near a
  massive concentration receive heavy deposit traffic → fire often →
  thresholds climb → firing rate drops → cell-local "tick rate" slows.
  This is gravitational time dilation as substrate firmware, not as
  postulated metric.
- **Spatial stretching** = connector load (§3.4). Edges near a massive
  concentration carry heavy deposit traffic → propagation slowed →
  effective distance of any path through that region grows. This is
  the radial g_rr stretch as connector load, not as postulated geometry.

Both are *current-state* properties of the substrate. Both vary with
mass concentration (more mass → more discharges → more deposits in
flight). Neither requires a metric tensor as input; the metric is
*read out* of the substrate's current load and threshold state.

The synthesis: **the substrate's three-layer state, frozen at any
moment, IS the spacetime metric.** Time dilation and spatial stretching
are two readings of the same substrate quantity (current local
threshold + current local connector load), not two postulates that
have to be consistent.

### What "grow until observed" predicts that QM doesn't

The slogan isn't decorative. It implies four things QM can describe
but doesn't *derive*:

1. **Bimodal observation outcomes.** In QM, the Born rule gives |ψ|²;
   the distribution shape is a postulate. In capacitor model, the
   distribution shape comes from how a charging trajectory splits
   between "drains back to empty" and "reaches threshold and fires."
   The bimodality (peaks at empty and at threshold) emerges from
   the dynamics, not from a postulate.
2. **Why observation needs interaction.** QM says it does; doesn't
   explain. Capacitor model says: discharge is the *only* mechanism
   by which information leaves a cell, by hardware construction.
3. **Why the world is quantum.** QM says it is. Capacitor model says:
   because the substrate's only emission mechanism is discrete
   threshold-triggered discharge — quantization is hardware, not law.
4. **What "the universe before measurement" is.** QM is famously
   ambivalent (Copenhagen punts; Many-Worlds says all branches; etc.).
   Capacitor model: it is the current real-valued joint state of
   charge + threshold + connector load across all cells. Real,
   physical, deterministic, just unobservable.

These are not claims to have *proved* QM is wrong or incomplete. They
are claims to have *grounded* what QM postulates in a hardware-level
mechanism that, if testable, would either confirm the grounding or
falsify it.

---

## 6. The Falsifiable Claim

The original RAW 132 v0 framing — *"no discrete substrate can combine
honest entity coherence with field-at-distance"* — was a generalization
from four specific failures. This document withdraws that generalization
in favor of a sharper claim that distinguishes the four experiments'
shared simplification from a true substrate limit:

> **If a substrate that implements the three-layer "grow until observed"
> mechanism — (a) continuous internal charging per RAW 127, (b) adaptive
> thresholds per §3.3, (c) load-driven connector propagation per §3.4,
> with discharge as the only emission event — *also* fails to combine
> entity coherence (in the §3.1 sense: capacitors sustained above-threshold
> across many ticks) with field-at-distance (gradient-following at
> distances ≫ 1 cell), then the discrete-substrate limit is real and the
> four experiments' shared failure is structural, not artifactual. If,
> instead, the three-layer model exhibits both properties — and as a
> bonus reproduces the GR metric (time dilation from §3.3, spatial
> stretching from §3.4) — the failures of 131/132/133/134 were artifacts
> of the specific simplifications each experiment made, and the framework
> is whole.**

This claim is testable by a single experiment that:
- Implements all three layers of §5 in one substrate.
- Initializes a coherent renewal pattern (a chain of capacitors firing in
  sequence).
- Initializes a stationary "planet" pattern (a denser cluster of capacitors
  firing periodically).
- Observes whether the test pattern's centroid drifts toward the planet
  cluster over many cycles, while remaining a coherent renewal pattern.
- *Bonus targets:* threshold-vs-r profile around the planet (does it match
  GR's time-dilation factor?); connector-load-vs-r profile (does it match
  g_rr's spatial-stretching factor?).

The expected-result table:

| Outcome | Reading |
|---|---|
| Test pattern dissolves on contact with planet field | Phase 1 of the experiment confirms what 134 found; the three-layer mechanism doesn't rescue the contact-decoherence failure. |
| Test pattern stays coherent at distance but doesn't drift | Connector load propagates but doesn't bias the renewal pattern; field-without-force result. |
| Test pattern stays coherent and drifts toward planet | The synthesis. The three-layer mechanism rescues both halves. |
| Drift's quantitative profile matches Newton's 1/r² | First honest gravity from the substrate without smuggled Newton. |
| Threshold(r) and connector-load(r) match GR's metric components | The full Schwarzschild metric earned as substrate firmware. The strongest possible result. |

Of these, the third onward are partial wins; the fifth is the ambitious
target. The first is the pessimistic result that would finally close
the discrete-substrate question with a positive falsification.

---

## 7. What a Capacitor-Substrate Experiment Would Require

Five things, none of which we have built end-to-end:

1. **A capacitor cell datatype.** Each substrate cell carries
   `(charge_level: real, threshold: real, last_discharge_tick: int,
   state: {Empty, Charging, Discharged})`. Charge accumulates from
   incoming deposits. State machine drives transitions per the
   firing dynamics in §3.2.

2. **Adaptive threshold dynamics (§3.3).** Threshold is a real-valued
   firmware quantity per cell, initialized from connectivity (option
   B baseline). Each discharge contributes a small increment to the
   threshold (the cell becomes more "fatigued" with use). A slow
   relaxation term decreases threshold over inactive ticks (the cell
   recovers if not used). Two parameters (increment per discharge,
   relaxation rate per inactive tick) — these are the *first*
   experimental knobs after threshold itself.

3. **Connectors with deposit propagation and load (§3.4).** Each cell
   has a list of connectors. Each connector carries a `current_load`
   (count of deposits in transit). When a cell discharges, it emits
   deposits along each connector — these enter the connector's load.
   Deposits propagate along the connector at a rate inversely
   proportional to current load (more load → slower propagation),
   arrive at the destination cell, and add to that cell's
   charging state.

4. **Operational definitions from §3 pinned down.** Specifically:
   - §3.1: H1.1 — entity is a cell sustained at charge ≥ 50% of
     current threshold for ≥1 tick (provisional).
   - §3.2: H2.1 — firing is deterministic at 100% of current threshold
     (provisional; bimodality from RAW 127 deferred).
   - §3.3: H3.5 — thresholds are connectivity-initialized + adaptive
     (B + C combined). **Phase 1 PASS verified this** (Exp 132).
   - §3.4: H4.1 — connector propagation time scales linearly with
     current load (provisional functional form).
   - §3.5: H5.1 — observer reads "where-is-entity" as centroid of
     cells fired in last K ticks. Multiple alternative readings
     (H5.3–H5.5) post-hoc applied to same recorded data.

5. **Observer instrumentation.** The substrate produces firing events;
   the experiment must record them per tick and apply at least one
   §3.5 reading function to construct entity trajectories. Phase 2
   should record full firing-event history so multiple H5.x readings
   can be compared post-hoc on a single substrate run — this is the
   §3.6 falsification strategy applied to §3.5.

6. **Substrate choice and validation order.** The substrate could be
   either a cubic lattice (simplest, debuggable) or an RGG (closer to
   the synthesis target with 128 v11's earned 1/r²). Either works.
   Recommended order: cubic first to validate the three-layer
   mechanism in isolation (Exp 132 Phase 1 done, PASS); then add
   planet pattern (Phase 2 — measure threshold(r), load(r), trajectory
   under H5.x readings); then port to RGG (Phase 3+).

These are not minor implementation details. Each is a substantial
design commitment that previous experiments avoided by simplification.
The right next experiment is the smallest implementation that holds
all six together; for Phase 2: cubic lattice, K=4 test pattern, single
K=4 planet, all five §3 commitments plus the observer reading
instrumentation.

---

## 8. What Stays Unaddressed

This RAW does not resolve:

- **Family 2 / spontaneous pattern emergence.** The capacitor model
  gives hardware for entities but doesn't explain how *coherent*
  renewal patterns form spontaneously rather than being hand-designed.
  The NAND-cloud precedent (see Exp 134 brainstorming memory) suggests
  this remains hard regardless of substrate. This is a separate,
  parallel question.

- **The bimodal probability distribution from RAW 127.** The
  provisional §3.2 answer (fixed deterministic threshold) sets aside
  RAW 127's bimodal-distribution gesture. If the bimodality is taken
  seriously as a framework commitment, the firing rule must be
  probabilistic or rate-dependent. This RAW deferred that choice; if
  the synthesis succeeds with deterministic firing, the bimodality
  must emerge from aggregate dynamics, not per-cell randomness — that
  prediction is itself testable.

- **The functional forms in §3.3 and §3.4.** The provisional commitments
  (adaptive thresholds with linear feedback; connector propagation time
  linear in load) are first-pass choices. Whether these specific shapes
  give Newton's 1/r² and Schwarzschild's 1/(1−2M/r) — versus some other
  power law that's similar in spirit but quantitatively wrong — is an
  empirical question. Alternative functional forms (logarithmic,
  exponential, threshold-with-saturation) may fit better; only running
  it tells us.

- **What "deposit" means in detail beyond §3.4.** Whether deposits are
  real-valued amounts or quantized packets, whether they sum linearly
  or attenuate with load, the exact propagation delay function — these
  are sub-questions of §3.4 that an implementation must commit to.

- **Whether "no history at the connector level" is preserved under load.**
  §3.4's claim is that connector load is current state, not history.
  But if discharges keep adding deposits and propagation-time scales
  with load, then load is effectively a moving average over recent
  discharge events. That's a *short* history at the connector level,
  even if it's nominally "current state." Whether this counts as
  history depends on how strict the principle is interpreted. RAW 132
  proposes this is acceptable; some readers may disagree.

These omissions are intentional. The point of RAW 132 is to identify
*what* has been left untested and *why* the four-experiment
triangulation has not yet hit the synthesis — not to build the
capacitor experiment in detail.

---

## 9. Conclusion

The four experiments closed individually with valid negative results.
The pattern across them suggested a discrete-substrate-limit; this
document withdraws that suggestion. The pattern is better read as four
simplifications of a richer model — the capacitor of RAW 126/127 — that
has never been operationally implemented in any of the experiments.

Four operational gaps in RAW 126/127 must be pinned down before a
capacitor-substrate experiment can be written: when does a capacitor
count as an entity (§3.1), when does it really fire (§3.2), how big is
it (§3.3), and what mechanism produces spatial stretching (§3.4).
Provisional answers commit to: deterministic threshold-firing,
connectivity-baseline + adaptive threshold (option B + C), and
load-driven connector propagation. These four choices, taken together,
constitute the "three-layer grow-until-observed substrate" of §5.

The substrate's central principle is now expressible in five words:
**grow until observed**. Charge level grows. Threshold grows. Connector
load grows. All three are invisible from outside between discharges;
discharge is the only event by which information leaves a cell, by
hardware construction. The same mechanism produces gravitational time
dilation (from threshold growth, §3.3) and spatial stretching (from
connector load, §3.4) — the GR metric becomes substrate firmware,
not postulated geometry.

The capacitor model is positioned as going *beyond* QM rather than
restating it: QM describes discharge statistics, the capacitor model
proposes the hardware producing them. The bimodal distribution from
RAW 127, the temporal phase of entity-formation, the structural
invisibility of charging, the requirement that observation involve
discharge — all are framework predictions that QM cannot derive but
can in principle test.

The next experiment, if undertaken, should implement the three-layer
"grow until observed" substrate on either cubic lattice or RGG, with
the operational §3 commitments made explicit. If that experiment also
fails to combine entity coherence with field-at-distance, the
discrete-substrate-limit claim becomes strongly supported. If it
succeeds — and if as a bonus the threshold-vs-r and connector-load-vs-r
profiles match GR's metric components — four prior negative results
were artifacts of partial implementation, and the framework remains
whole with both gravity and quantum measurement earned together.

Either way, RAW 132 narrows the question. Triangulation has done its
work. The next move is implementation of what was already specified
but never built.

---

## 10. Prior Art and Inspirations

This RAW does not propose ideas in isolation. The framework draws on
multiple research traditions; the synthesis (capacitor + adaptive
threshold + observer-relative quanta in one substrate) appears novel,
but each pillar has prior art and several "near-miss" frameworks
deserve explicit acknowledgment. This section is intended to be
exhaustive: works that directly inspired, works adjacent but
mechanistically different, and works explored but found less directly
relevant — included so future readers know what was considered.

A web survey on 2026-04-28 (recorded in memory `reference_dynamic_quanta_prior_art.md`) is the source.

### 10.1 Closest published precedents (observer/system-relative ℏ)

These three are the strongest matches found for RAW 132's central
claim that quantum size emerges from receiver/consumer threshold
rather than being a fundamental constant.

- **Gaconnet (2026), "Planck's Constant as Observer Signature: A Membrane Resolution Model of Quantum Measurement"** — LifePillar Institute preprint, January 2026. Argues ℏ is "the resolution grain of the membrane" of an observer, not a fundamental constant. Uses an explicit threshold-crossing operator (Heaviside step) and proposes an adaptive effective constant `ℏ_eff = ℏ₀ / C(R)` where `C(R)` varies with membrane configuration. Threshold-crossing + observer-relative + variable-h all present. Not capacitor-framed mechanically, but the closest single conceptual match found. Worth reading carefully before any RAW 132 novelty claim.
  URL: https://www.lifepillarinstitute.org/scientific-papers/planck-s-constant-as-observer-signature-a-membrane-resolution-model-of-quantum-measurement

- **Minic & Pajevic (2016), "On the emergent 'Quantum' theory in complex adaptive systems"** — Modern Physics Letters B, also arXiv:2310.14100. Direct quote: *"the actual value of the mock Planck constant is system-dependent and not in general universal"* and *"the environment too is expected to be adaptive."* Mechanism is noise-cancellation rather than capacitor discharge — adjacent in spirit, distinct in substrate.
  URL: https://arxiv.org/pdf/2310.14100

- **Berera, Calderón, Hassan, Magueijo (2021), "A Contextual Planck Parameter and the Classical Limit in Quantum Cosmology"** — Foundations of Physics. Effective Planck parameter depends on the comoving region under study; explicitly contextual / observable-dependent. Different motivation (cosmology) but related framing.
  URL: https://link.springer.com/article/10.1007/s10701-021-00433-0

### 10.2 Mechanistic inspirations (capacitor + adaptive threshold)

The exact "leaky capacitor + spike-triggered threshold elevation"
mechanism RAW 132 §3.3 commits to is well-established in
computational neuroscience. Citing these grounds the substrate
hardware in concrete prior work rather than appearing to reinvent it.

- **Brette & Gerstner (2005), "Adaptive Exponential Integrate-and-Fire Model as an Effective Description of Neuronal Activity"** — Journal of Neurophysiology 94:3637–3642. The AdEx model: leaky integration + spike-triggered threshold elevation + slow recovery. Mathematically the closest published mechanism to RAW 132 §3.3.
  URL: https://journals.physiology.org/doi/full/10.1152/jn.00686.2005

- **Fuortes & Mantegazzini (1962), "Interpretation of Repetitive Firing of Nerve Cells"** — Journal of General Physiology 45:1163–1179. The original biological "leaky integrator with adaptive threshold" model. Historical root of AdEx.

- **Hodgkin & Huxley (1952), "A Quantitative Description of Membrane Current and Its Application to Conduction and Excitation in Nerve"** — Journal of Physiology 117:500–544. Foundational biophysical model of action-potential generation. RAW 132 doesn't use H-H detail (we use the simpler integrate-and-fire abstraction), but H-H is the underlying physical model neuroscience builds on.

- **Izhikevich (2003), "Simple Model of Spiking Neurons"** — IEEE Transactions on Neural Networks 14:1569–1572. Computationally efficient simplification of biological spiking dynamics; widely cited alternative to AdEx with similar capacitor-fire-adapt structure.

- **Turrigiano (2008), "The Self-Tuning Neuron: Synaptic Scaling of Excitatory Synapses"** — Cell 135:422–435. Homeostatic adjustment of neural firing thresholds — the biological precedent for RAW 132 §3.3's "thresholds adapt with use" commitment.

### 10.3 Discrete-substrate / cellular-automaton frameworks (adjacent)

Programs that propose discrete substrates underlying physics. RAW 132
shares the discrete-substrate commitment but differs on the substrate
*mechanism* — specifically the capacitor-fire dynamic.

- **'t Hooft (2014, 2016), "The Cellular Automaton Interpretation of Quantum Mechanics"** — Springer 2016, originally arXiv:1405.1548. Discrete deterministic substrate underlying QM, with quanta arising from automaton equivalence classes. No capacitor mechanism, no consumer-relative quanta.
  URL: https://arxiv.org/abs/1405.1548

- **Wolfram (2002), "A New Kind of Science"** — broader CA-based physics program; foundational text for treating physics as cellular computation.

- **Wolfram Physics Project (2020+)** — discrete hypergraph rewriting model with rule-firing events and a fundamental rate ρ in tokens/sec. No capacitor mechanism, no consumer-relative quantum size in the public material.
  URL: https://writings.stephenwolfram.com/2021/04/the-wolfram-physics-project-a-one-year-update/

- **Bombelli, Lee, Meyer & Sorkin (1987), "Spacetime as a Causal Set"** — Physical Review Letters 59:521. Discrete spacetime as a partial order of events. Foundational text for causal set theory.
  URL (review): https://link.springer.com/article/10.1007/s41114-019-0023-1

- **Loop Quantum Gravity** — Rovelli, Smolin, Ashtekar; foundational works 1986–. Discrete quantum geometry with spin networks; no threshold-emission story.

- **Causal Dynamical Triangulations (CDT)** — Ambjørn, Loll, Jurkiewicz; 2000s. Discrete-spacetime path-integral approach.

- **Finkelstein (1969+), "Process Physics"** — early pregeometric program treating physics as discrete process rather than continuous geometry. Process Studies and related publications. Distant ancestor of all CA-physics programs.

### 10.4 Variable / emergent fundamental constants

These programs vary fundamental constants, including ℏ in some cases.
Different from RAW 132 — they vary by *cosmological* time, not by
*observer/consumer* threshold — but the broader theme of "constants
aren't constant" is shared.

- **Albrecht & Magueijo (1999), "A time varying speed of light as a solution to cosmological puzzles"** — Physical Review D 59:043516. Foundational variable-speed-of-light (VSL) cosmology paper.
  URL: https://arxiv.org/abs/astro-ph/9811018

- **Moffat (1992), "Superluminary Universe: A Possible Solution to the Initial Value Problem in Cosmology"** — International Journal of Modern Physics D 2:351. Independent VSL proposal contemporary with Albrecht-Magueijo.

- **Mangano, Lizzi, Porzio (2017+), "Inhomogeneous and Isotropic Cosmology"** — varying fundamental constants in isotropic cosmology.
  URL: https://arxiv.org/abs/1704.07368

- **Mendonça (2020), "Quest for time variation of Planck constant"** — European Physical Journal Plus, foundational review of variable-h cosmology proposals.
  URL: https://link.springer.com/article/10.1140/epjp/s13360-020-01031-1

- **Dirac (1937), "The Cosmological Constants"** — Nature 139:323. The Large Numbers Hypothesis, suggesting fundamental constants may vary across cosmic time. Historical ancestor.

### 10.5 Stochastic processes near threshold-firing

These touch the threshold-firing-with-noise structure RAW 132 uses
mechanically, but treat it as signal-detection or QFT machinery rather
than as substrate ontology.

- **Gammaitoni, Hänggi, Jung & Marchesoni (1998), "Stochastic Resonance"** — Reviews of Modern Physics 70:223. Comprehensive review of threshold-firing-with-noise systems including capacitor implementations. Mechanistically close to RAW 132's substrate, but treated as physics of signal detection, not as origin of ℏ.
  URL: https://link.aps.org/doi/10.1103/RevModPhys.70.223

- **Parisi & Wu (1981), "Perturbation Theory without Gauge Fixing"** — Scientia Sinica 24:483. Stochastic quantization: fictitious-time Langevin dynamics → QFT in equilibrium. Mechanically distant from RAW 132 (no threshold, no consumer), but historically important link between stochastic processes and quantum theory.

- **Gingl, Kiss & Moss (1995+), threshold-system stochastic resonance** — direct studies of capacitor-like threshold devices showing stochastic resonance behavior. Adjacent to RAW 132's substrate dynamics.

### 10.6 Information-theoretic / pre-geometric foundations (resonant but distant)

Programs that propose physics emerges from information / computation /
pregeometric structures. RAW 132 shares the "physics is hardware"
commitment but is more specific about the hardware (capacitors with
thresholds) than these usually are.

- **Wheeler (1990), "Information, Physics, Quantum: The Search for Links"** — proceedings of the 3rd International Symposium on Foundations of Quantum Mechanics. The "It from bit" program: physics derived from information-theoretic primitives. Distant ancestor of RAW 132's substrate-as-hardware framing.

- **Lloyd (2002, 2006), "Computational Capacity of the Universe"** and *Programming the Universe*. The universe as a quantum computer. Distinct from RAW 132 (Lloyd's quantum bits are conventional QM units, not capacitor-emergent) but shares the "physics is computation" theme.

- **Verlinde (2010), "On the Origin of Gravity and the Laws of Newton"** — JHEP 04:029. Entropic gravity: gravity as emergent from holographic information dynamics. Distinct mechanism, shared "fundamental constants emerge from substrate dynamics" theme.
  URL: https://arxiv.org/abs/1001.0785

- **Penrose (1967+), twistor theory** — combinatorial/algebraic pregeometric program. Different mechanism but shares the "geometry from non-geometric primitives" theme.

### 10.7 Quantum measurement and interpretation (referenced but not direct mechanisms)

RAW 132 §4 positions the capacitor model as going *beyond* QM rather
than restating it. For honest engagement, the major QM interpretations
that RAW 132 implicitly takes positions on:

- **Rovelli (1996), "Relational Quantum Mechanics"** — International Journal of Theoretical Physics 35:1637. RQM treats quantum states as relations between systems, not absolute. Conceptually compatible with RAW 132's observer-relative ℏ — RQM may be the easiest interpretive home for the capacitor framework.
  URL: https://arxiv.org/abs/quant-ph/9609002

- **Ghirardi, Rimini & Weber (1986), GRW spontaneous collapse** — Physical Review D 34:470. Wave function collapses spontaneously at random points, quantum-classical transition is dynamical. Conceptually near to RAW 132's "discharge as the only emission event" but mechanism (random collapses) differs from substrate-driven discharge.

- **Pearle (1989), Continuous Spontaneous Localization (CSL)** — Physical Review A 39:2277. Continuous version of GRW. Same conceptual proximity as GRW.

- **Bohm (1952), pilot-wave / Bohmian mechanics** — Physical Review 85:166. Hidden variables underlying QM. RAW 132 differs from Bohm — RAW 132's "hidden" charge level isn't a hidden variable in the usual sense; it's substrate state that's structurally inaccessible until discharge.

- **Everett (1957), Many-Worlds** — Reviews of Modern Physics 29:454. RAW 132 does not need many-worlds; discharge events resolve substrate state into a single observable trajectory.

- **Fuchs, Mermin (1990s+), QBism** — Quantum Bayesianism, treating quantum states as agent's beliefs. RAW 132's observer-side reading function (§3.5) shares some QBism flavor but RAW 132 commits to a real underlying substrate where QBism does not.

- **Zurek (1991+), Decoherence and quantum-to-classical transition** — Physics Today and many follow-ups. Decoherence as the practical mechanism by which quantum becomes classical. RAW 132's discharge-resets-substrate gives a decoherence-like effect at the substrate level.

- **Penrose & Hameroff (1996+), Orchestrated Objective Reduction (Orch-OR)** — Mathematics and Computers in Simulation 40:453. Controversial proposal for consciousness-driven quantum collapse via gravitational effects in microtubules. Included for completeness; RAW 132 makes no claim about consciousness and has no commitment that aligns with Orch-OR.

### 10.8 Things explored but found less directly relevant

For honesty: some traditions were considered during the 2026-04-28
prior-art survey and found less directly relevant. Listed for
transparency.

- **Liquid Neural Networks** (Hasani, Lechner et al. 2020+) — adaptive computational dynamics rooted in machine learning. The mechanism is similar to AdEx but without physics ambitions; not a direct substrate model.

- **Conventional Cellular Automaton physics** beyond Wolfram — Toffoli, Margolus, Fredkin work from the 1980s. Foundational for CA approaches but no capacitor or threshold-emergent ℏ framing.

- **Block Universe / Eternalism debates** — relevant to RAW 132's "tick-frame" temporal commitments but tangential to the §3 operational gaps.

- **Constructor Theory** (Deutsch & Marletto) — physics in terms of "what tasks are possible." Conceptually adjacent (substrate-as-hardware), mechanistically distant.

- **Bekenstein bounds and holographic principles** — entropy/information limits on substrate. Could constrain RAW 132 in principle; not directly invoked.

### 10.9 What this section does and does not claim

This section does NOT claim:

- That RAW 132 is fully novel. The Gaconnet 2026 preprint and the Minic-Pajevic 2016 paper independently propose observer/system-relative ℏ and should be acknowledged as precedents. The mechanism (AdEx adaptive capacitors) is borrowed unchanged from neuroscience.

- That every reference here is a precursor we built on. Some (Penrose-Hameroff Orch-OR, GRW, Many-Worlds) are listed for completeness about the QM interpretive landscape RAW 132 takes positions on, not because RAW 132 builds on them.

This section DOES claim:

- The specific *fusion* — adaptive capacitor-fire dynamics + observer-relative ℏ + discharge-as-only-emission, in a single substrate ontology — has not, as of this survey, been published.

- The novel contribution of the framework is the bridge: AdEx-style neural dynamics + observer-relative h + "the universe is hardware that fires," brought together as a single physics program rather than three disconnected literatures.

- If the framework is to be published externally, a literature review at minimum must include §10.1 (Gaconnet, Minic-Pajevic, Berera) and §10.2 (Brette-Gerstner, Fuortes-Mantegazzini, Hodgkin-Huxley). The other subsections are honest scholarly context.

If a precursor we missed is found later, this section is the place to add it.

### 10.10 Additional references added during RAW expansion

A few additional references that should have been in §10.1–§10.7 originally but were caught only on the second pass:

- **Nelson (1966), "Derivation of the Schrödinger Equation from Newtonian Mechanics"** — Physical Review 150:1079. Stochastic mechanics deriving QM from a classical stochastic process. Closely related to RAW 132's "QM as emergent from substrate dynamics" claim, with a mechanism (Brownian motion) different from capacitor-fire.

- **Adler (2004), *Quantum Theory as an Emergent Phenomenon*** — Cambridge University Press. Derives QM as an emergent statistical mechanics of a deterministic matrix model. Substrate-as-hardware in the same spirit as RAW 132, different specific mechanism.

- **Khrennikov (2014, 2015+), Prequantum Classical Statistical Field Theory (PCSFT)** — multiple monographs and papers. Classical-field substrate that gives QM-like statistics in the appropriate limit. Direct competitor to RAW 132's claim that QM is emergent from substrate; mechanism is field statistics, not capacitor dynamics.

- **Conway & Kochen (2006), "The Free Will Theorem"** — Foundations of Physics 36:1441. If observers have "free will" then particles have it too. Constrains any deterministic hidden-variable theory; RAW 132's deterministic substrate must engage with this.

- **Bell (1964), "On the Einstein Podolsky Rosen Paradox"** — Physics 1:195. Bell's theorem. Any QM-replacement must engage with Bell inequalities. RAW 132 has not yet addressed how/whether the capacitor substrate violates Bell — this is an open future-work question.
  URL: https://cds.cern.ch/record/111654/

- **Friston (2010+), Free Energy Principle and Active Inference** — Nature Reviews Neuroscience 11:127. Adaptive systems minimize prediction error; capacitor-with-threshold-adaptation can be read as a free-energy-minimizing element. Mechanistically very close to AdEx-style dynamics, framed at a higher level (cybernetic / information-theoretic) than RAW 132.

- **Wiener (1948), *Cybernetics*** and **Ashby (1956), *An Introduction to Cybernetics*** — historical precedents for treating physical/biological systems as feedback control structures. Ancestor of modern adaptive-threshold thinking.

- **Tegmark (2014), *Our Mathematical Universe*** — the Mathematical Universe Hypothesis. RAW 132 doesn't take a position on this directly, but the framing "physics is a specific mathematical structure (capacitor substrate) rather than just any computable structure" is a weaker version of MUH.

- **Smolin (2013), *Time Reborn*** — argues time is fundamental, not emergent. RAW 132 commits to the same (tick-frame substrate has a fundamental tick rate). Adjacent ontology.

- **Banks (1980s), reversible cellular automata** — Toffoli, Margolus, Banks, Fredkin programs on reversible CA. Foundational for thinking about substrate-as-computation with conservation laws.

These are still partial — there are likely more precedents this RAW hasn't engaged with. The section grows when found.

### 10.11 Internal framework precedents (rediscovered 2026-04-28)

After Phase 2's negative result, a search through the project's own prior
RAWs and experiments surfaced two foundational commitments that RAW 132
v0–v3 did not engage with explicitly. These are not "prior art" in the
external-literature sense — they are earlier work by this project that
RAW 132 should have referenced from the start.

- **RAW 044, "Fallible Commit Principle"** — establishes the
  **window-commit pattern**: every commit (decision boundary) is an
  irreversible choice that closes the observer's buffer; visualization
  runs on the closed buffer. Buffer N closes, buffer N+1 opens.
  *"Lag of reality: the observer always reconstructs the past, never
  the live tick stream."* Predates RAW 132 by ~94 RAWs and was never
  cited in RAW 132 v0–v3 despite being load-bearing for §3.5's
  observer-reading-function gap. **Now cited** in §3.5's H5.7
  definition.

- **Experiment 64_109 (three-body tree), v8 (February 2026)** —
  operational implementation of **self-subtracting transport**:
  *"Self-subtraction resolves the SNR problem — entities detect each
  other's field. Integer gamma quanta on a cubic lattice produce
  attractive force via self-subtracting transport."* This is the
  cubic-lattice, integer-substrate ancestor of RAW 132's three-layer
  capacitor mechanism, with a working drift mechanism (force law
  approximately 1/r^2.2 measured). Phase 2's negative result is
  consistent with attempting to detect entity-relative drift via
  god-view measurement — Exp 64_109 v8 already showed self-subtraction
  is the principled fix.

- **Experiment 64_109 v21–v22 (March 2026)** — the **"frozen planet" bug**:
  planet placed next to a star with zero established field escapes
  immediately because it perceives only its own deposit pattern, not
  the star's. Bootstrap deadlock identified: planet cannot orbit
  before field exists, but field does not form with planet present.
  *Direct empirical validation* that without self-subtraction, an
  entity sees itself as the dominant signal and cannot detect external
  fields. Phase 2's "test pattern doesn't drift" result echoes this
  exactly — except Phase 2 also lacked self-subtraction in the
  measurement, so we couldn't see the right fields even if they were
  there.

**Why these were missed in v0–v3:** RAW 132's brainstorming arc focused
on the synthesis of capacitor + adaptive threshold + observer-relative
ℏ as a *new* unification, and the §3.5 observer-reading-function
discussion centered on choice of metric (centroid vs. density-peak vs.
threshold-elevation) rather than the *observer's own contribution to
the substrate state being measured*. The specific failure mode of
god-view measurement — the test pattern as confound for the planet's
profile — was visible in Phase 2's actual data but required user
recall of the prior framework finding to be diagnosed correctly.

**Lesson for future RAWs:** before drafting a new operational gap (§3.x)
or a new experiment phase, check the project's own prior RAWs and
experiment closures for foundational commitments that bear on the
question. The framework has accumulated ~130 RAW documents and 50+
experiments; the relevant prior commitment may already exist.

---

## 11. Document History

This RAW evolved across multiple versions, all on 2026-04-28. The
trace below preserves the evolution.

### v0 (initial draft, 2026-04-28 morning)

Original framing: **"discrete-substrate-limit claim."** RAW 132 v0 was written immediately after Exp 134 Phase 1+2 completed. It argued that the four-experiment triangulation (131_a/131_b/133/134) showed *no discrete substrate can combine honest entity coherence with field-at-distance.*

§3 had only TWO operational gaps: §3.1 (when is a capacitor an entity) and §3.2 (when does it fire). The doc sketched a sharper falsifiable claim: *"if a substrate that implements the full capacitor model also fails, then the discrete-substrate-limit is real."*

This framing was withdrawn in v1.

### v1 (same morning)

User insight: *"if there is no external force, the pattern can spend all its energy to exact redraw of itself."* This crystallized the energy-budget framing and led to:
- §3.3 (capacitor sizing) added — hypothesized A/B/C/D options for how big a capacitor is.
- §3.4 (spatial stretching) added — load-driven connectors emerged as a refinement of Exp 132's anisotropy.
- §5 (Synthesis: Grow Until Observed) added — three-layer growth registers tied together.
- The "discrete-substrate-limit claim" was withdrawn in favor of "four simplifications of an unimplemented capacitor model."

### v2 (afternoon)

After Exp 132 Phase 1 PASS (5,000-cycle K=4 cycle sustained), user asked "what is the drift?"

This surfaced §3.5 — the observer-reading-function gap. **Drift is not a substrate phenomenon; it's the observer's reading of substrate state.** The framework's distinct mechanism for drift was rejected in favor of treating reading as observer-side commitment.

§3.6 (Scientific Elimination Strategy) was added in this iteration. Hypotheses were labeled (Hx.y) and tabulated. The falsification table became explicit.

### v3 (later afternoon)

Phase 2 implementation + run completed. Three of four hypotheses falsified at provisional parameters. Section §3.6.1 added documenting the result.

User asked for prior-art search. §10 (Prior Art and Inspirations) added with ~30 references organized by relevance to RAW 132's claims. Closest hits identified:
- Gaconnet 2026 (observer-relative ℏ with adaptive ℏ_eff)
- Minic-Pajevic 2016 (system-dependent mock Planck constant)
- AdEx neurons (Brette-Gerstner 2005, exact mechanism, different field)

User clarified RAW philosophy: **"all our thoughts ... all resources ... all theories no matter how wrong they turn out to be."** This expanded §10.10 with additional references and added §11 (Document History) + §12 (Wrong Turns and Rejected Ideas).

### v3.1 (evening, after Phase 2 negative result)

User recalled a prior framework finding: *"the pattern can't read its own deposits ... it basically commits for next window according the current window it can read"* and *"there was an issue that entity reading itself was basically static and always at the same spot."*

Search through internal materials surfaced:
- **RAW 044 (Fallible Commit Principle)** — establishes window-commit mechanic. Predates RAW 132 by ~94 RAWs.
- **Exp 64_109 v8** — self-subtracting transport as operational mechanism. Empirically produced 1/r^2.2 attractive force.
- **Exp 64_109 v21** — "frozen planet" bug: without self-subtraction, entity sees only its own field and cannot detect external mass.

Both should have been referenced in v0–v3 but were not. RAW 132 §3.5 was missing **H5.7 (self-subtracting reading)** as a hypothesis. Phase 2's god-view measurement of test pattern in same substrate as planet was a known-broken approach (cf. Exp 64_109 v21), not a novel design choice.

v3.1 changes:
- §3.5 expanded with H5.7 (self-subtracting reading), explicitly grounded in RAW 044 + Exp 64_109 v8.
- §3.6 falsification table updated with H5.7's experimental test (Phase 2A.5 superposition).
- §10.11 added — internal framework precedents (RAW 044, Exp 64_109 v8/v21) explicitly.
- §12.13 updated with the framework-precedent context.
- New §12 entry being drafted for the meta-lesson: search prior internal RAWs/experiments before drafting new operational gaps.

### What changed structurally across versions

| Section | v0 | v1 | v2 | v3 |
|---|---|---|---|---|
| §3 gaps | 2 (entity, firing) | 4 (added sizing, stretching) | 5 (added observer reading) | 5 + falsification subsection |
| §5 Synthesis | absent | added (grow-until-observed) | unchanged | unchanged |
| §10 Prior Art | absent | absent | absent | added (~30 refs across 9 subsections, then §10.10 expansion) |
| §11 History | absent | absent | absent | added |
| §12 Wrong Turns | absent | absent | absent | added |
| Central claim | "discrete-substrate-limit" | "untested capacitor" | "untested capacitor + observer-side drift" | unchanged from v2 + falsifications recorded |

---

## 12. Wrong Turns and Rejected Ideas

This section preserves ideas considered during the brainstorming arcs
that produced this RAW, then rejected. They are recorded because
recognizing dead ends saves future effort, and because a future reader
might find one of them less wrong-headed than we did.

### 12.1 Discrete-substrate-limit claim (rejected v0 → v1)

**Idea:** The four-experiment triangulation (131_a/131_b/133/134) showed that no discrete substrate can combine honest entity coherence with field-at-distance.

**Why rejected:** Each experiment dropped half of the capacitor model. The claim was a generalization from four specific failures to a structural impossibility — too strong given that the full capacitor (RAW 126/127) was never operationally implemented.

**Status:** Withdrawn. Replaced by "untested capacitor" reframe.

### 12.2 Phase 2 dichotomy: metric profile (A) vs. rule extension (B) (dissolved v2)

**Idea:** Either Phase 2 measures `threshold(r)` and `load(r)` profiles passively (option A), or Phase 2 extends the rule with explicit recruitment/dropout dynamics to enable drift (option B).

**Why dissolved:** User pointed out that drift isn't a substrate phenomenon — it's an observer's reading. The A/B framing was a false dichotomy because option B was misframed as substrate primitive when drift was always observer-side.

**Status:** Replaced by §3.5 (observer reading function) + §3.6 (single-run-multiple-readings strategy). Both A and B redundant.

### 12.3 NAND-chain spontaneous emergence (rejected during Exp 134 brainstorming, referenced here)

**Idea:** Use NAND-based local update rules to spontaneously generate substrate patterns rather than hand-designing them.

**Why rejected:** User reported prior empirical attempt produced "cloud with minor clumps, more like visual artifact than real patterns." Empirical evidence against any mechanism that produces statistical-field structure rather than coherent self-renewing patterns.

**Status:** Family 2 (spontaneous shape emergence) remains parked across the entire research arc. RAW 132 commits to hand-designed shapes pending future breakthrough.

See memory `project_nand_cloud_artifact.md` for detail.

### 12.4 Halo via paint spreading (rejected during Exp 134 Phase 2 brainstorming)

**Idea:** Each paint event adds small +δ to cells within face-distance H of the painted cell, creating a "halo" field for long-range coupling.

**Why rejected:** Recreates the NAND-cloud failure mode from a different angle. Smoothing a localized concentration into a distributed field is exactly what NAND-based generation produced when used on the raw tick-stream — visual artifacts, not coherent patterns. Adding halo for "drift to work" was rejected on principle (do not smuggle distributed-field machinery to chase desired outcomes).

**Status:** Phase 2 of Exp 134 (and Phase 2 of Exp 132) committed to NO halo. Phase 2's negative result (locality holds across empty cells; contact = decoherence) follows directly from this commitment.

### 12.5 Built-in connector anisotropy (Exp 131_b — falsified)

**Idea:** Connectors near mass have geometrically different lengths by construction, producing GR's spatial stretching.

**Why rejected:** Per-edge Schwarzschild radial earned (ratio 1.01 at r=5), but horizon scaling failed (r_s ∝ M off by factor 0.19–0.58). The built-in anisotropy gave radial profile shapes by construction but did not scale correctly with mass. **Empirically falsified by Exp 131_b.**

**Status:** Replaced by H4.1 (load-driven connectors as current state, scales automatically with mass).

### 12.6 Lineage-tree spatial structure (Exp 131_a — falsified)

**Idea:** Spatial distance is derived from lineage-tree relationships; gravity emerges from local-conductance flow on the lineage tree.

**Why rejected:** Lineage tree + local conductance flow does NOT recover Newton (Exp 131_a v3-v7 ruled out c=1, c=1/ℓ, c=ℓ). Topology is the bottleneck. **Empirically falsified by Exp 131_a closure.**

**Status:** Lineage-tree ontology survives as a worldview (RAW 131 still holds: connections are ancestral, distance derived); the specific flow-based gravitational mechanism is dropped.

### 12.7 Closed-loop pure conservation for sustained fields (Exp 133 — falsified)

**Idea:** Strict closed-loop integer hold-and-fire substrate with conservation gives sustained gravitational fields.

**Why rejected:** Closed-loop pure conservation gives FLAT field. Source+sink yields ρ ∝ r^(-1) but smoothed force law slope -0.65, not Newton's -2. Test patterns dissipate before drifting. **Empirically falsified by Exp 133 closure.**

**Status:** Strict conservation in finite substrate dropped. Real physics gets away with conservation because the universe is effectively infinite on observation timescales — we can't reproduce that on 100k cells.

### 12.8 CA renewal in vacuum produces gravity at distance (Exp 134 — falsified)

**Idea:** A sign-blind transactional renewal rule on a discrete signed-integer 3D substrate would support both pattern coherence AND field-at-distance.

**Why rejected:** Phase 1 sustained patterns exactly (10,000 cycles bit-identical). Phase 2 found contact = decoherence; locality strict; no field-at-distance possible without halo (which was rejected, see §12.4). **Empirically falsified by Exp 134 Phase 2.**

**Status:** Pattern-coherence-via-renewal works in vacuum. Gravity-at-distance does not. RAW 132's reframe extends the lessons forward.

### 12.9 Probabilistic firing (H2.2 — deferred not falsified)

**Idea:** Capacitors fire with a probability per tick proportional to charge level (RAW 127's bimodal-distribution gesture), giving QM's wave-function intuition.

**Why deferred:** Conflicts with substrate determinism principle ("everything is deterministic at the substrate layer"). RAW 127's bimodal distribution may emerge from aggregate dynamics under deterministic firing (H2.1), removing the need for per-cell randomness.

**Status:** Deferred to future falsification — if H2.1 fails to reproduce the bimodal distribution at aggregate scale, H2.2 returns.

### 12.10 Charge-weighted observer reading (H5.2 — falsified by RAW 127)

**Idea:** Observer reads charge level per cell, computes charge-weighted centroid as "where is the entity."

**Why rejected:** Conflicts with RAW 127's structural-invisibility commitment — the charging phase is unobservable from outside; only discharge events are visible. An observer cannot read charge level. **Falsified theoretically by RAW 127.**

**Status:** Removed from the H5.x panel. Charge-weighted reading is structurally inaccessible to any external observer in this framework.

### 12.11 Recruitment/dropout rules for drift (rejected v2)

**Idea:** Add explicit substrate rules where non-pattern cells get "recruited" into a cycle if they reach threshold near firing pattern cells, and cycle cells "drop out" if their firing slot is taken.

**Why rejected:** This was the substrate-side answer to "how does drift happen." But user pointed out drift is observer-side, not substrate-side. The recruitment/dropout machinery was therefore solving a non-problem. **Rejected by reframing rather than falsification.**

**Status:** Replaced by §3.5 observer reading function. The substrate doesn't drift; the reading drifts.

### 12.12 Connector load_coefficient = 0 in Phase 1 + active in Phase 2 (active design choice)

**Idea:** Phase 1 deferred load to keep mechanism simple. Phase 2 turned it on. **At Phase 2 trial parameters (load_coefficient=0.1), load(r) profile turned out flat.** This is not "rejected" but a falsification of the trial parameter value — the load mechanism may need order-of-magnitude larger coefficient to produce gradient before equilibrium.

**Status:** Phase 2A.2 (load coefficient sweep) is the natural follow-up.

### 12.13 Test pattern in same substrate as planet, measured god-view (active design choice → revealed as inadequate, Phase 2)

**Idea:** Place test pattern + planet pattern in the same substrate, measure profile around planet via direct substrate state inspection, measure drift of test from external god-view.

**Why partially rejected (after running):** The test pattern's halo contaminates the planet's profile measurement. Cells at r=5–8 from planet centroid sample BOTH halos. The "planet profile" isn't isolated.

**Deeper reason this was inadequate (recognized 2026-04-28 after Phase 2):** Phase 2 measured **god view** — direct read of full substrate state including all patterns' contributions. But the framework already commits (RAW 044 Fallible Commit Principle, Exp 64_109 v8 self-subtracting transport) to **entity-relative observation**: an entity that observes substrate state must subtract its own contribution, otherwise it perceives only its own dominant field and sees itself as static (Exp 64_109 v21's "frozen planet" bug).

**What Phase 2 should have done (now scheduled as Phase 2A.5):** measured the test pattern's *perceived environment* via self-subtraction, not god-view. The two are materially different and the framework already had the operational solution worked out (Exp 64_109 v8) but RAW 132 §3.5 didn't reference it until now.

**Status:** Phase 2A.1 (planet-only run, no test pattern) is one cleaner measurement. Phase 2A.5 (three-run superposition test) is the principled implementation: run planet-only, run test-only, run combined; verify (combined god-view) − (test-only) ≈ (planet-only) at test cells, which is the framework-implicit superposition for self-subtracting transport.

### 12.14 21×21×3 substrate scale (active design choice, Phase 2)

**Idea:** Small substrate (21×21×3 = 1323 cells) for fast simulation.

**Why partially rejected (after running):** 5 cells between patterns in a 21-cell substrate may not be enough room for halo gradient to develop a clean radial profile before boundary effects.

**Status:** Phase 2A.3 (larger substrate, e.g. 41×41×3 = ~5000 cells) is a follow-up.

### 12.15 Full lattice connectivity (active design choice, Phase 2)

**Idea:** Every face-adjacent cell pair has a connector. This makes the substrate "fully connected" so deposits can flow anywhere.

**Why partially rejected (after running):** With full connectivity and load_coefficient=0.1, load saturates uniformly across the substrate (~1.3 everywhere). No radial structure develops. Either load_coefficient is too small to create gradient before saturation, OR full connectivity floods too quickly.

**Status:** Phase 2A.4 (partial connectivity, only cycle + selective halo connectors) is a follow-up.

### 12.16 Provisional functional forms in §3.3, §3.4

**Idea:** Linear adaptation rate, linear relaxation rate, propagation time linear in load.

**Status:** All linear by simplest-thing-first principle. Phase 2's flat load(r) profile suggests linear may be wrong — could need exponential or threshold-with-saturation behavior. Future iteration.

### 12.17 RAW 132 v0–v3 omission of self-subtracting transport (the meta-lesson)

**The omission:** v0–v3 of RAW 132 designed §3.5 (observer reading function) entirely as a choice between metrics (centroid, density peak, threshold-elevation, etc.) without engaging with **whether the observer is itself a substrate participant whose contribution must be subtracted**. Phase 2's setup (test pattern in same substrate as planet, god-view measurement) was therefore a known-broken approach to the framework — Exp 64_109 v21 had documented the "frozen planet" bug and Exp 64_109 v8 had implemented self-subtracting transport as the operational fix, both ~2 months before RAW 132 was drafted.

**Why it was missed:** the RAW's brainstorming arc treated capacitor + adaptive threshold + observer-relative ℏ as a *new* synthesis, and didn't systematically check what the project's own prior RAWs (~130 of them) and experiments (~50 of them) had already established about the observation problem.

**The meta-lesson (for future RAWs):** before drafting a new operational gap or experiment phase, **search the project's own prior materials for foundational commitments that bear on the question.** The framework has accumulated substantial internal precedent. New RAWs should explicitly cross-reference older ones — not only for what they earned but for what they ruled out and what foundational principles they established.

**Status:** v3.1 corrects the omission. §3.5 now lists H5.7 (self-subtracting reading) explicitly, §10.11 documents the internal precedents, §12.13 updated with the framework context, and Phase 2A.5 is the corresponding experiment. Future RAW updates should include an "internal precedents" cross-reference subsection by default.

---

These wrong turns and rejected ideas are not failures — they are the
narrative of how the framework got to its current state. RAW 132 in its
final form is the survivor of these alternatives. Future versions of
RAW 132 will add more entries to this section as new ideas are
considered and either incorporated or rejected.
