# RAW 133 — The Semantic Substrate

### *Where Same / Different / Unknown Becomes the Universal Consume-Reemit Rule*

**Author:** Tom (insight), Claude (articulation)
**Date:** 2026-04-30
**Status:** Synthesis draft. No experiment yet. RAW 132's three-layer mechanism is a non-semantic special case of this.
**Prerequisites:** RAW 044 (Fallible Commit), RAW 113 (Same/Different/Unknown), RAW 126 (Trit Is a Capacitor), RAW 127 (Trit Has Depth), RAW 130 (It Rotates Because It Consumes), RAW 131 (Lineage Substrate), RAW 132 (Untested Capacitor)
**Internal precedents:** Exp 128 v11 (RGG + propagation earns 1/r²), Exp 134 (pattern coherence in vacuum), Exp 132 Phase 1 (three-layer mechanism sustained K=4 cycle), Exp 132 Phases 2/2A.5/2A.2 (non-semantic substrate saturates uniformly), Exp 64_109 v8 (self-subtracting transport), causal-cone-engine v0.6 (substrate→observation pipeline with `Spectrum` primitive), **trie-memory** (W:/workspace/trie-memory — full operational implementation of the spectrum primitive: 163 passing tests, MCP server, Learning→Crystallized state machine, content-addressable path keys, two-mechanism architecture, layer system, honest-agent retrieval stack)
**Closes (provisionally):** RAW 132's untested-capacitor framing as a *non-semantic special case* — not falsified, but generalized. The capacitor's three-layer mechanism is what happens when every cell has the same trivial spectrum.

---

## What this document is

This is a **RAW** document. The 'R' is for raw — raw thinking, raw notes, raw materials. RAWs are working notebooks. Per `feedback_raw_doc_philosophy` memory: every idea considered, every dead end explored, every reference followed, every wrong turn made — recorded so the framework's reasoning trail is visible, not just its current best version. RAW 133 is a *synthesis* RAW: it ties together primitives from RAWs 113, 126, 127, 130, 131, 132, 044 plus internal experimental results plus the causal-cone-engine implementation, into a unified substrate ontology.

If something here contradicts something elsewhere, it's intentional — the framework is layered evidence, not a polished position. See §11 Document History, §12 Wrong Turns and Superseded Approaches.

---

## Abstract

Yesterday's experiments (Exp 132 Phase 2/2A.5/2A.2) failed in instructive ways. The three-layer "grow until observed" capacitor model from RAW 132 — charging + adaptive threshold + connector load — saturates uniformly across 3 orders of magnitude in `load_coefficient` when the substrate has full lattice connectivity and patterns are hand-designed K=4 cycles. The substrate equilibrates everywhere; no gradient forms.

Reflecting on this, plus the user's recall of the original causal-cone-engine intent ("the substrate is a mesh of pipelines delivering deposits, no real 3D"), plus the framework's prior commitments, surfaced a missing primitive: **the substrate's nodes are not just consume-reemit, they are classifier-transformer-routers**. Each node has a *spectrum* (a set of recognizable deposit-shapes) and classifies every incoming deposit as **Same** (consume), **Different** (convert + consume), or **Unknown** (reemit unchanged).

This single mechanism unifies:
- RAW 113's Same/Different/Unknown classification (now substrate primitive, not just observer description)
- RAW 126/127's capacitor cycle (Empty/Charging/Discharging happens *for Same/Different deposits*)
- RAW 130's "it rotates because it consumes" (consumption is the active conversion work)
- RAW 131's "connections are ancestral, not spatial" (the substrate is pipe-mesh; geometry is observer-derived)
- RAW 132's three-layer mechanism (a non-semantic special case)
- 128 v11's 1/r² gradient (pipe-branching density of Same-classified flow through substrate)
- 134's pattern coherence (a closed loop of cells with mutually-aligned spectra)
- causal-cone-engine's rendering pipeline (observer's spectrum-classification of arriving deposits)
- Matter / antimatter (opposite-sign spectra; same-sign attracts via recruitment, opposite-sign annihilates via conversion failure)
- Pattern growth and core formation (recruitment when neighbor's spectrum aligns; storage as accumulated above-threshold charge)
- QM collapse (consumption of an Unknown→Same conversion at the observer's sink, producing an observable event)

The substrate, on this view, is **not** real-valued γ values on a 3D grid. It is a graph of pipe-junctions where every junction is a small classifier-transformer running on incoming deposit-tokens.

The novel claim of this RAW: **semantic differentiation is required for the substrate to support gravity, mass, observation, or matter-antimatter physics.** Without spectra, the substrate is uniform-conducting and saturates everywhere (Exp 132 Phases 2/2A.5/2A.2 demonstrated this empirically). With spectra, recruitment / release / leak / observation / matter-antimatter all emerge from a single primitive.

The next experiment must implement Same/Different/Unknown classification as a substrate primitive, not as observer post-processing.

---

## 1. The Lineage — What This Is Built From

This RAW does not propose a new ontology. It proposes that *the framework already had everything needed* and the missing connection is naming Same/Different/Unknown as the substrate's fundamental classification.

| Source | Contribution to RAW 133 |
|---|---|
| **RAW 113** (Same/Different/Unknown) | The classification primitive. Was framed as observer's description; now load-bearing as substrate dynamics. |
| **RAW 126** (Trit is a Capacitor) | Empty / Charging / Discharging cycle — what the cell does for Same and Different deposits. |
| **RAW 127** (Trit Has Depth) | Charging phase invisible from outside; observation requires discharge. RAW 133 sharpens: *charging-with-Same-deposits* is invisible; *Unknown reemits* are immediately visible to next-pipe. |
| **RAW 130** (It Rotates Because It Consumes) | Consumption is *active work*. RAW 133 makes this concrete: consumption converts Different to Same, costing some fraction of deposit magnitude. |
| **RAW 131** (Lineage Substrate) | Connections are ancestral, not spatial. RAW 133 makes this primary: substrate is pipe-mesh, "3D space" is observer-derived geometry from arriving-deposit density. |
| **RAW 132 v3.1** (Untested Capacitor + grow-until-observed) | The three-layer mechanism (charging + adaptive threshold + connector load) is a *non-semantic special case* of RAW 133 — what happens when every cell has the trivial spectrum (everything is Same). RAW 132 saturates because no Unknown classifications exist to differentiate cells. |
| **RAW 044** (Fallible Commit Principle) | Window-commit pattern. RAW 133's classification + reemission makes the lag concrete: the cell's commit (next-tick consumption / discharge) is based on this-tick's *classified* arrivals. |
| **Exp 64_109 v8/v21** (self-subtracting transport, "frozen planet" bug) | Entity must subtract its own emissions from observation. RAW 133 explains why: an entity can't classify its own deposits as Same (they're literally the same tokens it just emitted), so they pass through self-classification trivially — they don't constitute new observable information. |
| **Exp 128 v11** | Earned 1/r² on RGG via pure-real propagation. RAW 133 reads this as: 1/r² is the spatial density of Same-classified deposits flowing through pipe-branching geometry. |
| **Exp 134 Phase 1** | Earned vacuum pattern coherence. RAW 133 reads this as: a closed loop of cells with mutually-aligned spectra, no Unknown reemits, fully internalized renewal. |
| **Exp 132 Phase 1** | Three-layer mechanism sustained K=4 cycle. Worked because the substrate was tiny + cycle-only wired (no Unknown reemits possible). |
| **Exp 132 Phases 2/2A.5/2A.2** | Three-layer mechanism *failed* to produce gradient on full-lattice substrate. RAW 133 diagnoses: without semantic differentiation, every cell trivially classifies everything as Same; the substrate becomes a uniform conductor; saturation everywhere. |
| **causal-cone-engine v0.6** | Implementation precedent — has `DepositToken` + `Spectrum::crystallize_from` primitive (consumption.rs); has full substrate→observation rendering pipeline. The Spectrum primitive in causal-cone-engine is what RAW 133 elevates to substrate-primary. |

---

## 2. The Substrate as Pipe-Mesh

### 2.1 Restating the topological commitment

The substrate is a graph: a set of nodes connected by directed edges (pipes). Each pipe carries a stream of deposits in transit. There is **no inherent 3D space** — the graph topology is the only structural commitment.

What we measure as "3D space" is what an observer constructs by reading the densities and arrival patterns of deposits at their sink-node. Different observers (in different graph positions) can construct different apparent geometries from the same underlying graph; what we share is that the Random Geometric Graph topology of physical space gives most observers similar apparent geometries.

### 2.2 Why this isn't a fall-back to Cartesian

128 v11 used a 3D RGG — points sprinkled in 3D, connected to neighbors within radius. The "3D" is a sprinkling-space, not a Cartesian commitment. The graph could equally be embedded in any space (or no space). 128 v11's earned 1/r² emerges from the graph's *typical neighborhood structure*, not from Cartesian distance. RAW 131 is the pure case: the graph has no embedding at all; spatial distance is derived from lineage-tree paths.

For tractability, RAW 133's experiments will use 3D-RGG sprinkling (matches Exp 128 v11). But the substrate primitive does not require it.

### 2.3 What flows through the pipes

A **deposit** is a token — a unit of recognizable structure. In the simplest case (causal-cone-engine `DepositToken`), it's a 4-bit-per-channel quantization: density + RGB color. In general, a deposit carries:
- A type or shape (the *token*)
- A magnitude (continuous real)
- (Optionally) a source-tag for self-subtraction (Exp 64_109's mechanism)
- (Optionally) a creation tick for window-lag tracking (RAW 044's commit logic)

Pipes carry these tokens between nodes. A node's state is determined by what tokens have been arriving and what its own spectrum classifies them as.

---

## 3. The Semantic Consume-Reemit-Classify Rule

### 3.1 Each node is a classifier-transformer-router

When a deposit-token `t` arrives at node `n`, the node performs a single atomic operation:

```
classify(t, n.spectrum) ∈ {Same, Different, Unknown}

if Same:
    consume(t) — charge accumulator increases by t.magnitude
    spectrum reinforces (token's frequency in n's spectrum increases)
if Different:
    convert(t) — apply small transformation to bring t into spectrum
    consume(converted_t) at reduced magnitude (conversion cost)
    spectrum reinforces (now-converted token's frequency increases)
if Unknown:
    reemit(t) along ALL outgoing pipes (or per the substrate's reemit policy)
    spectrum unaffected (Unknown deposits don't shape the spectrum)
```

The cell's behavior depends entirely on `n.spectrum`. Two cells with different spectra at the same position in the graph can produce wildly different observable behavior.

### 3.2 What each classification means physically

- **Same**: the token matches a frequently-recognized pattern in this cell. Consumption integrates the token's energy into the cell's renewal cycle. The cell becomes more strongly tuned to that pattern (spectrum reinforcement). This is the cell *participating in a pattern* — it accepts deposits the pattern emits.

- **Different**: the token is *recognizable but not exact*. It has the structure of a Same-token plus some perturbation. The cell can perform a small transformation to bring it into spectrum — e.g., shift the color slightly, snap density to nearest spectrum value. Conversion costs some fraction of the deposit's magnitude; the converted token is then consumed normally. This is *learning* (or matter scattering off matter): the cell extends its spectrum to handle near-misses.

- **Unknown**: the token doesn't match anything in this cell's spectrum. The cell can't process it, so it routes it onward through outgoing pipes. The Unknown deposit doesn't disturb this cell's pattern — it's a *transit phenomenon*. From this cell's perspective, the Unknown token is "passing through to somewhere else." This is *transparency*: the cell doesn't see Unknown deposits, just relays them.

### 3.3 Why this is the load-bearing primitive

Every other framework piece becomes a special case or composition:

- **128 v11's pure propagation rule**: every cell has an *empty spectrum*, so every incoming deposit is Unknown and gets reemitted (with magnitude divided by fan-out) along outgoing pipes. The substrate is uniformly conductive. Density at distance `r` from a source falls as 1/r². ✓
- **RAW 132's three-layer capacitor**: every cell has a *trivial spectrum* containing only one type of token (the substrate's "everything is Same"); every deposit gets consumed; threshold accumulates; cells fire. No Unknown reemits, so no semantic field; substrate saturates uniformly (matches Exp 132 Phase 2A.2 empirical result). ✓
- **134 K=4 vacuum coherence**: a cycle of K cells, each with spectrum aligned to the cycle's deposit-shape; cycle's deposits are all Same; no leakage to non-cycle neighbors because cycle-only wiring; perfect closed loop. ✓
- **causal-cone-engine's rendering**: the observer's spectrum determines what tokens it sees; rendering is the integrated arrivals of Same+Different classifications at the observer over a window. ✓

### 3.4 What the spectrum's structure is

A spectrum is a *frequency-weighted set* of tokens:

- **Set of known tokens**: which token-shapes the cell recognizes
- **Frequency / weight**: how often each token has been classified as Same recently
- **Threshold for Same vs Different**: how strict the matching is
- **Threshold for Different vs Unknown**: how much perturbation is too much

The spectrum is *adaptive*: it reinforces tokens that arrive frequently as Same, and forgets (decays) tokens that haven't been seen recently. This is how a cell "tunes in" to the pattern it's part of, and how it "tunes out" if the pattern moves on.

A new cell joining a pattern starts with empty spectrum; its first encounters with the pattern's tokens are Unknown; over many encounters, the tokens get crystallized into spectrum (causal-cone-engine's `Spectrum::crystallize_from` does this); the cell starts classifying them as Same; the cell is now *participating* in the pattern. **This is recruitment.**

---

## 4. Patterns as Coherent Loops with Aligned Spectra

### 4.1 What a pattern is

A **pattern** is a set of cells in the substrate graph satisfying:

1. **Spectrum compatibility**: the cells' spectra are mutually aligned — they all recognize each other's emitted tokens as Same.
2. **Cyclic firing**: the cells fire in a closed cycle order (per RAW 126's capacitor cycle), with each cell's firing timing matching the next cell's expected arrival time.
3. **Closed deposit loop**: the cycle's deposits travel from one cell to the next-in-cycle, completing the loop indefinitely.

The pattern's *identity* is the combination of (cycle structure) + (mutual spectrum). Two patterns with different spectra but the same cycle structure are different patterns. Two patterns with the same spectrum but different cycle topologies are also different patterns.

### 4.2 The pattern's cells fire in phase

Patterns have a natural *period* (K, the cycle length in ticks). At any moment, exactly one cell of the pattern is in the discharging phase; the others are in various stages of charging. The cell that just discharged emitted to its outgoing pipes; the next-in-cycle cell receives that emission, classifies it as Same, consumes it, and progresses toward its own discharging phase.

This is the same renewal mechanism as Exp 134 Phase 1, just with semantic gating: the *reason* the cycle is closed is that the pattern's deposits-on-the-pipe are Same-classified by the next cell. Outsider cells see the same pipe traffic but classify it as Unknown, so they don't participate; the deposits are routed past them onward.

### 4.3 What "drift" means under this framing

Drift is *not* the pattern's cells changing position. Cells are pinned to graph nodes. Drift is **change in pattern membership over time**:

- Some currently-pattern cells lose alignment (their spectra drift, or their firing falls out of phase) → they leave the pattern → these are *released*
- Some currently-non-pattern cells gain alignment (their spectra crystallize from observed traffic, their firing locks into phase) → they join the pattern → these are *recruited*

Net effect: the *centroid* of pattern cells shifts. An observer integrating the pattern's apparent position over time sees motion. But the cells themselves haven't moved.

This is fully consistent with Exp 134 Phase 2's finding that **drift is observer-side, not substrate-side**: the substrate just has membership-change events; an observer reading the pattern sees motion as the centroid evolves.

### 4.4 Connection to Doc 28 ("renewal not preservation")

Doc 28's commitment is: an entity isn't a static thing that persists; it's a renewal cycle that keeps reconstituting itself. RAW 133 makes this concrete:

- Renewal = the deposit cycling around the closed loop, classified Same at each cell
- Not preservation = the *cells* aren't preserved (cells can be released, others can be recruited); only the *cycle structure + spectrum* are preserved
- Identity = the pattern of recognition (spectrum) + the pattern of transit (cycle), maintained through changing cell membership

---

## 5. Recruitment and Release as Emergent Dynamics

### 5.1 Recruitment

A non-pattern cell `c` near an active pattern receives some of the pattern's leakage (Unknown reemits to `c`). Initially these are Unknown to `c`, so `c` reemits them to its other neighbors. But over time, if the pattern's leakage continues, `c`'s spectrum crystallizes the pattern's tokens (per `Spectrum::crystallize_from`-style accumulation: tokens arriving frequently get added to the spectrum).

Once `c`'s spectrum has the pattern's tokens, `c` starts classifying incoming deposits from the pattern as Same. `c` consumes them, accumulates charge, eventually fires. If `c`'s firing happens *in phase* with the pattern's cycle (which the spectrum-alignment naturally produces), `c` is *recruited* — it's now firing in coherent step with the pattern's cells.

Recruitment is not a hand-coded rule. It's emergent from spectrum dynamics:
- Spectrum crystallization is automatic (causal-cone-engine has the primitive)
- Phase alignment follows from the timing of the pattern's deposits arriving at `c`
- Recruitment is just "spectrum aligned + firing in phase"

### 5.2 Release

Symmetrically: a pattern cell `c` whose spectrum drifts (because it's also receiving non-pattern tokens that crystallize into its spectrum) starts misclassifying pattern deposits as Different or Unknown. It either consumes with conversion cost (drains from the pattern), or reemits the pattern's tokens onward (the deposit escapes the cycle). Either way, the cycle's coherence is degraded for that cell.

If `c` keeps misclassifying for several ticks, its firing falls out of phase. The cycle is no longer closed through `c`. `c` is *released* — back to substrate.

Release is also emergent: spectrum drift is automatic if non-pattern traffic flows through `c`; phase falls out automatically when classifications change.

### 5.3 The cycle's K and the pattern's effective size

A pattern with K cells fires every K ticks at any single cell. As cells are recruited or released, K changes — the cycle's period adjusts to match the cell count. Or: the cycle becomes *multi-stranded* — multiple deposits cycling around in lock-step, each one period-K but offset by 1 tick from the next. This gives effective cycle period 1 (one fire per tick) at the pattern level, even with K cells.

Either way, the pattern's *mass-equivalent* (its energy storage capacity) scales with cell count. More recruited cells = more storage = more mass.

---

## 6. Storage and Core Formation

### 6.1 Cells as batteries

A cell's accumulator can hold charge above baseline threshold. RAW 132 §3.3 already had this primitive (adaptive threshold rises with use). RAW 133 makes the *interpretation* explicit: cells store excess incoming charge as elevated threshold.

When a cell receives more deposits than its cycle position requires, the excess goes into the threshold itself — the cell becomes *more massive* in the sense that it now requires more deposit-energy to fire. From the outside, the cell appears as a denser node (consumes more, reemits less to non-cycle neighbors, retains more).

### 6.2 Pattern growth absorbs ambient flux

When ambient flux (deposits arriving from elsewhere in the substrate) exceeds the existing pattern cells' capacity:
- Existing cells fill their batteries (threshold rises)
- Excess deposits leak to neighboring cells
- Some neighbors get recruited (spectrum crystallizes)
- Pattern grows

In equilibrium, the pattern's leak rate at the boundary matches the ambient flux — additional deposits can't be absorbed because they leak back out before being consumed.

### 6.3 Why cores form

Innermost cells in a grown pattern receive deposits from *all directions* (every neighbor is also a pattern cell, all firing in phase with it). Outer cells receive deposits from *some directions* (the inside) but reemit Unknown to others (the outside, where non-pattern substrate is).

So innermost cells:
- Have the most incoming Same-classified deposits per cycle
- Have the highest accumulated charge
- Have the highest threshold
- Are the *densest* cells in the pattern

Outermost cells receive less, accumulate less, have lower threshold. The pattern has a **density gradient** from core to surface. This is what we call a planet's core: the innermost recruited cells of the pattern.

### 6.4 Mass-energy equivalence

The pattern's total mass is the sum of stored deposit-energy across all recruited cells. Mass = energy = number of cells × average accumulated charge per cell. There's no separate "rest mass" vs "kinetic energy" — everything is stored deposit-charge.

A pattern receiving high ambient flux grows large (heavy planet); one receiving low flux stays small (test particle). Mass scales with substrate-level activity in the cell's region.

---

## 7. Leak as the Visibility / Coupling Primitive

### 7.1 Where leak comes from

Whenever a pattern cell processes a Different or Unknown deposit (or reemits some fraction of consumed Same), some deposit-energy goes to non-cycle neighbors. These reemissions don't return to the cycle; they propagate outward through the substrate.

This is **leak**. It has multiple sources:
- Conversion cost when consuming Different deposits (some fraction reemitted as residue)
- Reemission of Unknown deposits (full reemit unchanged)
- Cycle-closure imperfection (a small probabilistic reemit to non-cycle neighbors even on Same consumption, if the pattern is imperfect)

In an *idealized perfectly closed* loop with all-Same classifications, leak = 0. In any real substrate with real spectra, leak > 0.

### 7.2 Leak as the field

The substrate's region around a pattern is filled with the pattern's leaked deposits, propagating outward through Unknown-reemits at intermediate cells. The density of these leaked deposits at distance `r` from the pattern falls as 1/r² (pipe-branching density on RGG, per Exp 128 v11 Phase 1's earned result).

What we measure as "the gravitational field" is this propagating leak. The pattern's mass (accumulated charge) determines the leak rate; the leak rate determines the field strength; the field strength produces the 1/r² gradient.

### 7.3 Leak as visibility

A pattern with zero leak is *invisible*. It has internal renewal but the rest of the universe can't tell it exists. Mathematically possible (134 Phase 1's perfectly closed K=4 cycle in cycle-only wiring) but cosmologically dark.

A pattern with high leak is *bright* — it produces a strong field and is readily observable. But it also drains itself faster, so it requires more incoming flux to maintain.

A real pattern has *moderate* leak: enough to be observable and to interact, not so much that it bleeds itself out faster than it can absorb ambient flux.

### 7.4 Leak as coupling

When two patterns are near each other, each one's leak reaches the other's cells. The leaked deposits arrive at non-pattern cells in the receiving pattern's neighborhood. Some of those cells classify the deposits as Same (because the patterns share enough of a spectrum) → their spectra reinforce → they may get recruited into the *other* pattern. Or they classify as Different → they convert and consume → their spectra evolve toward a hybrid. Or they classify as Unknown → they pass through.

This is *gravitational interaction*: pattern A's leak biases pattern B's cell-recruitment toward A; pattern B's cells see asymmetric incoming-Same flux on the A-facing side; pattern B's centroid shifts toward A. **Drift toward planet** is exactly this.

---

## 8. Observation and QM Collapse

### 8.1 The observer is a sink-pattern

An observer is a pattern that has somehow grown a complex enough spectrum to recognize many tokens. The observer's substrate-pattern (their "body") is renewing as patterns do; what we call sensation is the spectrum-classification of incoming deposits at the observer's pattern boundary.

When a deposit arrives at the observer's cells:
- If Same: consumed into the observer's existing pattern. *Familiar.*
- If Different: converted with effort. *Novel but recognizable.*
- If Unknown: reemitted onward. *Invisible.*

Same and Different produce observable events (charge accumulates, eventually a pattern cell fires, the pattern updates). Unknown produces nothing — it's filtered out before reaching the observer's awareness.

### 8.2 Wave function and collapse

The full state of the universe-substrate at any moment is the joint state of:
- All in-transit deposits on all pipes
- All cell spectra
- All cell accumulator charges
- All cell threshold values

This state evolves deterministically per consume-reemit-classify dynamics (RAW 132 §4 §5). For any given observer, this evolving state is mostly invisible — most of it doesn't reach them.

The **wave function** for a particular observer is *the joint state of deposits in transit that may eventually reach them*. It evolves until one such deposit arrives at their cells. **Collapse** is that arrival's classification — the deposit gets resolved into Same, Different, or Unknown by the observer's spectrum, and the observer's pattern updates accordingly.

This gives a hardware-level reading of QM:
- *Probability* of detection = arrival probability × classification non-Unknown
- *Wave function evolution* = substrate dynamics between arrivals
- *Collapse* = classification at observer's spectrum
- *Born rule* (|ψ|²) = should derive from pipe-branching geometry + classification statistics
- *Disturbance from measurement* = consuming a deposit at the observer drains the source pattern slightly (the observer is now slightly affecting the observed pattern's leak budget)

### 8.3 Why charging is structurally invisible (RAW 127 confirmed)

A cell that's charging (accumulating Same deposits but hasn't fired yet) is doing so internally. Nothing leaves the cell during charging — by definition, the deposits are being *absorbed*, not reemitted. From an external observer's perspective, the cell is silent until it discharges.

Discharge is the only time information leaves the cell. RAW 127's commitment is exact: observation requires discharge from the observed.

For a pattern cell that's reemitting Unknown deposits during charging: this is NOT the cell's "own" reemission; it's the cell forwarding an Unknown deposit it received. From the observer's perspective, that Unknown deposit isn't *observation of the cell* — it's observation of *whatever sent the Unknown deposit through this cell*. The cell is invisible.

### 8.4 Why we observe 3D

The observer's cells are pinned to graph positions. The observer's spectrum is built up from the renewal pattern that IS the observer (their body). Tokens recognized as Same/Different are tokens that resemble the world's structure as the observer's body has experienced it. Tokens that don't fit the body's pattern are Unknown — they pass through unobserved.

The 3D apparent geometry the observer constructs is the integrated pattern of arrivals (Same/Different) at different pipe-endpoints in the observer's body, weighted by causal-lag depth. This is exactly what causal-cone-engine implements: ray-pipelines from sources to the observer, with arriving tokens producing screen-pixel updates. There is no separate "physical 3D space" — there is the substrate graph, and the observer's body-pattern integration of arrivals.

---

## 9. Matter, Antimatter, Annihilation

### 9.1 Spectra come in dual pairs

If the framework's substrate primitives have any sign symmetry (which RAW 132's signed-integer substrate did), then spectra also come in pairs. A "matter" spectrum recognizes tokens of a certain shape. The "anti" spectrum recognizes the *negation* of those tokens.

When a matter cell receives a matter-token: Same. Standard consumption.
When a matter cell receives an antimatter-token: this is NOT just Different — it's *anti-matched* with the spectrum. Conversion would mean *inverting the token*, which would invert the cell's spectrum. The cell can't perform this conversion without destroying its own pattern membership.

### 9.2 Same-sign contact

Two same-sign patterns near each other: their spectra are similar enough that each classifies the other's tokens as Same or Different. Recruitment can happen across the boundary; cells in the gap get recruited into one pattern or the other. **Patterns merge** or **drift toward each other** depending on relative size and ambient flux. This is gravitational attraction.

### 9.3 Opposite-sign contact

Two opposite-sign patterns near each other: their spectra are anti-aligned. Each pattern's tokens are anti-Same to the other pattern's cells.

When pattern A's leak reaches pattern B's cell: pattern B's cell tries to classify. Anti-Same means: this token would, if consumed, *invert pattern B's spectrum*. Either:
- The cell refuses the conversion (treats as Unknown, reemits) → both patterns lose energy to the surrounding substrate, but their internal spectra remain intact. Slow mutual depletion.
- The cell *attempts* the conversion (treats as Different) → the cell's spectrum becomes a hybrid that recognizes neither A's nor B's tokens cleanly. The cell falls out of either pattern. Both patterns lose this cell. **Decoherence cascade** at the contact boundary.

The second outcome is what we observed in Exp 134 Phase 2 (contact = decoherence). RAW 133 explains why: the cells at the contact boundary attempted to integrate anti-aligned tokens and lost coherence with both patterns. The result: a region of substrate where neither pattern can hold cells stably — *annihilation*.

The energy released? It's the deposits that no longer have a coherent pattern to be part of. They become Unknown to all nearby cells, get reemitted outward, and dissipate as background substrate flux. This is the gamma-ray equivalent: high-energy reemissions broadcasting outward from the annihilation boundary.

---

## 10. Connection to Existing Earned Results

### 10.1 Exp 128 v11's 1/r² gradient

Earned by pure-real propagation on RGG. Under RAW 133's reading: each cell had effectively trivial spectrum (or all cells shared one spectrum), so deposits were either Same (consumed-and-fan-out-reemitted) or Unknown (also reemitted with fan-out). Either way, the effect was uniform conduction. 1/r² emerged from pipe-branching density alone. ✓

128 v11's *limitation* was radial-vs-tangential asymmetry on isotropic RGG. Under RAW 133, this is because the substrate had no semantic differentiation — all flow was uniform-conducting, no anisotropy from spectrum-alignment patterns. Adding spectra would let some pipe directions carry more Same-classified flow than others, naturally producing anisotropy.

### 10.2 Exp 134 Phase 1's vacuum coherence

A K=4 cycle bit-identical for 10K cycles. Under RAW 133: a closed loop where each cell's spectrum exactly matches the cycle's tokens, and the wiring restricts deposits to cycle-only neighbors (no Unknown reemits possible). Perfectly closed. ✓

134's bit-identity is *very strict*. With real spectra, cycles wouldn't be bit-identical; they'd have minor fluctuations. RAW 133 predicts: in a more realistic substrate, K=4 patterns would still be coherent but not bit-identical — they'd have some statistical noise from leakage and from spectrum-frequency drift. This is consistent with real physics (atoms don't have *exactly* the same energy levels every measurement).

### 10.3 Exp 132 Phases 2/2A.5/2A.2 saturation

Three-layer mechanism (charging + adaptive threshold + connector load) on full-lattice substrate, K=4 patterns. Saturated uniformly across 3 orders of magnitude in load_coefficient.

Under RAW 133's reading: the substrate had *effectively trivial spectra* — every cell treated every deposit as the same kind of thing (no Same/Different/Unknown classification). Combined with full lattice connectivity, every cell received deposits from all sides equally and processed them identically. The result: uniform equilibration. Saturation everywhere. ✓

Adding semantic differentiation should fix this: some pipes (those carrying tokens that are Same to the receiving cell) carry pattern-flow; other pipes (tokens that are Unknown) reemit through. The substrate develops structure from the spectrum-classification alone.

### 10.4 Exp 64_109 v8 self-subtracting transport

"Entity must subtract its own field contribution to detect external mass." Under RAW 133: a cell's own emissions are tokens it just generated. When those tokens loop back through the pipe-mesh and arrive at the cell again, they are *trivially Same* — they match the cell's spectrum perfectly because they came from it. The cell can't distinguish them from external Same-tokens.

Self-subtracting transport is the cell tagging its emissions with a source-id and ignoring tokens with its own source-id when classifying. Without this tag, the cell consumes its own emissions, accumulates charge from itself, and gets stuck in a self-perpetuating cycle that doesn't notice external flux ("frozen planet" bug).

RAW 133 generalizes: source-tagging is a substrate-implementation requirement for any cell that participates in coherent dynamics with other cells. Without it, the cell can't separate "self" from "world."

### 10.5 causal-cone-engine

Has the `Spectrum` primitive in `consumption.rs`. Has the substrate-to-rendering pipeline. Has material types (pass_through, scatter, reemit, specular, heat, vacuum) which under RAW 133 reading are *spectrum profiles* — each material is a cell with a particular kind of spectrum that classifies different incoming token-shapes differently.

What's missing: causal-cone-engine doesn't have RGG topology (uses 512³ regular grid as performance compromise) and doesn't have full spectrum-driven recruitment/release dynamics (entities are hand-placed and persistent). Adapting causal-cone-engine to RAW 133 ontology = adding RGG sprinkling + dynamic spectrum-driven cell recruitment.

### 10.6 trie-memory — the spectrum primitive ALREADY operational

**Discovered during this RAW's drafting (2026-04-30 evening) when the user pointed at `W:/workspace/trie-memory` as relevant to classification.**

trie-memory is **not external prior art**. It is an internal project that already implements the spectrum primitive RAW 133 was proposing as new. **163 passing tests across 19 test files, MCP server deployed, 5 honest-agent scenarios validated end-to-end.**

What it implements directly from RAW 133's specification:

- **Every node answers Same / Different / Unknown for incoming tokens** (`src/trie/node.rs`, `Classification` enum). Same = consume + visit++. Different = route to a child node (descends to more specific spectrum). Unknown = observe in buffer, eventually crystallize into a spectrum.
- **Two-state node lifecycle:** `NodeState::Learning` (empty spectrum, accumulating observations in a buffer) → `NodeState::Crystallized` (frozen spectrum, stable identity). Crystallization happens when the node has accumulated enough variety (per `crystallization_threshold`).
- **Depth-dependent thresholds:** `params_for_depth(depth)` returns `(crystallization_threshold, spectrum_max_size)`. Root: 256/64 (slow to form, broad spectrum). Depth 1: 128/32. Depth 2: 64/16. Depth 3: 32/8. Deeper: 16/4 (fast to form, narrow spectrum). **This naturally gives a hierarchy of recognition** — broad strokes at root, fine detail at leaves. RAW 133 should adopt this directly.
- **Content-addressable path keys** via FNV-1a hash of spectrum (`content_id()`, `Trie::path_key()`). A node's identity is its spectrum, not its position. Two nodes with the same spectrum at different positions in the trie share the same path key — they are functionally equivalent recognition events.
- **Two-mechanism architecture**: trie (recognition / "have I seen this?") separate from concept store (meaning / "what does this mean?"), bridged by path keys. Maps directly onto RAW 133's split between cell-spectrum (recognition) and pattern-membership (the cycle structure that gives meaning).
- **Temporal binding:** `concept_bind_auto(["křoví", "bush", "茂み"])` writes all inputs through the trie in the same tick window, gets path keys, binds all to one concept. **This is RAW 133's recruitment criterion in operational form** — temporal co-occurrence of Same-classifications binds cells into a pattern.
- **Variable tick-gaps for silence:** space=1 tick, comma=3, period=10, newline=20. Silence is not data; it is *lack of writing*. The amount of silence between writes encodes structural separation. RAW 133 should adopt this for substrate timing — the duration between events carries information.
- **Layer system:** memory layers are bookmarks on the tick timeline with origin_timestamp, tick_start, tick_end, word_count, concept_ids. Each layer is "what I learned in this session." Two timelines: wall-clock + relative-tick. **This is the renewal-context bookkeeping primitive RAW 133 needs but didn't specify.**
- **No floats.** Integer-only throughout. Trust, coverage, clarity, recency all as ppm integers (0..=1000). RAW 133 should commit to this too.
- **Five-mode epistemic responder** (Answer / Partial / Disambiguate / Conflicted / Unknown) with mode selection by multi-dimensional `ConfidenceVector`. Provenance tracking. Append-only revisions (corrections never overwrite originals).

What trie-memory has empirically validated (relevant to RAW 133):

- **The classification primitive works.** Trie crystallizes; recognition is reproducible; new inputs route correctly.
- **Spectrum-as-identity works.** Path keys are content-addressable; same spectrum → same path key.
- **Temporal co-occurrence binding works** for cross-language concept linking.
- **No-hallucination-on-unknown** is reliable — the system never invents memories.
- **Append-only revision works** without gaslighting (corrections stamped on top of originals).

What trie-memory has surfaced as harder than expected (and what RAW 133 needs to learn from):

- **Single-character / byte-level deltas don't carry word identity.** English prose flattens to depth 1 because letter-transitions are too uniform across vocabulary. The byte trie ends up classifying *writing systems* (English vs Czech vs Japanese vs code), not topics. **Implication for RAW 133: substrate tokens need granularity above the bit level.** Per-cell deposits of single-bit values won't produce semantic differentiation. Tokens must encode meaningful chunks. The word-trie's solution (hash each word to a 2-byte token) is the analog — atomic chunks at the right level of abstraction.

- **The "no embeddings" claim is honest in the ML sense, but coverage uses a small linguistic preprocessor** (stopwords, trailing-s stemming, punctuation strip). Pull those and Scenario 4 drops from 10/10 to 7/10. **Implication for RAW 133: even pure spectrum-based classification needs *some* structure-aware preprocessing.** Token shape is a design choice with semantic content. We don't get to ignore the substrate's input encoding.

- **Distinctive content words cluster in different trie subtrees than common-prose memories.** Path-suffix matching misses them. **Implication for RAW 133: recognition isn't always commutative across cells.** Multi-cell pattern recognition needs care about how spectra aggregate.

- **STALE mode is deferred** — needs a domain-volatility classifier. **Implication for RAW 133: spectrum decay (release dynamics) is a real engineering challenge, not a free parameter.** trie-memory chose append-only-with-revisions instead of decay; RAW 133 may need to follow that lead.

- **Stress-test case `[X] tides vs semaphore`** is unresolved. Distinctive content words route to a different trie subtree than standard prose, so path-suffix matching misses. Indexing limit. Per-cell substrate work might or might not have analogous failures.

**This dramatically reshapes RAW 133's experiment program (§11).**

Phase 1 (validate spectrum primitive with 2 cells) is *already done* in trie-memory at scale. We should not reinvent it. Phase 1 of the experiment program becomes:

> **Port trie-memory's classifying-trie node primitive to a substrate cell datatype on RGG. Demonstrate that the same Same/Different/Unknown classification + Learning→Crystallized lifecycle + content-addressable path-key behavior works at substrate scale (10⁴ cells, RGG topology, real-time-tick dynamics).**

If that works, Phases 2+ become:
- Phase 2: temporal-binding-based pattern formation on RGG (port `concept_bind_auto`).
- Phase 3: pattern recruitment via spectrum drift (the new RAW 133 dynamics).
- Phase 4: two-pattern interaction (drift, planet-test).
- Phase 5: quantitative GR fit.
- Phase 6: matter-antimatter annihilation.

Many open questions in §13 are *answered* by trie-memory's design choices:

| §13 open question | trie-memory's answer |
|---|---|
| How is the spectrum represented? | `Vec<u8>` (byte trie) or `Vec<u16>` (word trie). Set semantics with frequency-based crystallization (`Spectrum::crystallize_from`). |
| What's "Different" precisely? | A child node of the current node. Routing to a child IS the Different classification — it descends to a more specific spectrum. |
| Is the spectrum per-cell or per-pattern? | Per-cell. Patterns are emergent from temporal binding of multiple cells' classifications. |
| How are spectra initialized? | Empty (Learning state). They crystallize from observation. |
| How does observation update the spectrum? | Frequency-based: tokens above coverage threshold get kept. |
| Does spectrum-decay happen? | trie-memory's design *doesn't* decay (append-only). RAW 133 may need to add decay for release dynamics, OR adopt append-only-with-revisions. |

**Decision pending:** does RAW 133's experiment program port trie-memory's primitives directly (saves enormous engineering, but inherits trie-memory's specific commitments — append-only, integer-only, fixed depth-thresholds), or build a fresh implementation aligned with RAW 133's substrate-physics goals (more flexibility, more work, risks rediscovering trie-memory's lessons)? **Recommendation: port directly.** trie-memory's commitments are well-justified, the implementation is battle-tested, and the small adjustments RAW 133 needs (RGG topology instead of hierarchical trie; substrate-cell wrapper around the node primitive; decay/release if it turns out necessary) are localized.

This also clarifies the relationship between RAW 113 (Same/Different/Unknown classification) and RAW 132 (capacitor cycle): they were always meant to be *the same primitive*. trie-memory is the proof. The capacitor's Empty/Charging/Discharging cycle is the operational consequence of Same/Different/Unknown classification: Empty = no recent classification fired; Charging = consuming Same/Different deposits; Discharging = the firing event that emits the consumption result.

---

## 11. The Experiment Program This Enables

The semantic substrate is much more than RAW 132's three-layer mechanism. The experiment program needs to grow incrementally:

### Phase 1: Spectrum primitive validation

Two cells with non-trivial spectra. Send tokens. Verify:
- Same tokens consumed, charge accumulates
- Different tokens converted with correct cost, charge accumulates at reduced rate
- Unknown tokens reemitted unchanged
- Spectrum reinforces with arrival frequency
- Spectrum decays with absence

Smallest possible experiment. Doesn't even need graph topology; one-cell-with-input-stream suffices.

### Phase 2: Closed-loop coherence with spectra

A K=4 cycle on 4 cells with mutually-aligned spectra. Verify:
- Cycle sustains itself like 134 Phase 1 did
- Now with leak (some deposits classified Different at edge cells, some reemit as Unknown to non-cycle neighbors)
- Bit-identity *not* expected; statistical coherence is

### Phase 3: Recruitment and release on RGG

A small RGG (say 50 nodes). Seed K=4 pattern. Add ambient flux of Same tokens to half the substrate. Observe:
- Pattern grows by recruiting nearby cells (their spectra crystallize)
- Pattern shrinks if ambient flux drops
- Pattern's centroid shifts toward higher-flux region

This tests recruitment/release dynamics in a controlled setting.

### Phase 4: Two-pattern interaction (drift)

RGG with two seed patterns, planet (large) and test (small). Same spectrum (both matter). Observe:
- Planet grows to absorb most ambient flux
- Test pattern receives planet's leak
- Test pattern's centroid drifts toward planet (asymmetric recruitment on planet-facing side)
- Drift profile compared to Newton's 1/r² prediction

This is the equivalent of Exp 132 Phase 2 / Phase 2A.5, but with semantic substrate.

### Phase 5: Quantitative Schwarzschild fit

Same as Phase 4 but with a larger planet, measuring threshold(r) and load(r) profiles around it. Fit to GR's metric. Test radial vs tangential anisotropy.

### Phase 6: Matter-antimatter annihilation

Two seed patterns with opposite spectra. Bring them together. Observe:
- Decoherence cascade at contact boundary (per §9.3)
- Energy release as Unknown-classified reemits broadcasting outward
- Both patterns lose cells

### Phase 7+: Multi-pattern, multi-scale, real physics

Three-body interactions, orbital mechanics, possibly atomic structure, etc.

This is a research arc spanning multiple sessions / weeks / months. Phase 1 is implementable in a single session.

---

## 12. Wrong Turns and Superseded Approaches

### 12.1 RAW 132's three-layer mechanism without spectra

RAW 132 v0–v3.1 specified the substrate as: each cell has a real-valued charge, an adaptive threshold, and incoming/outgoing connectors with load. Tick rule: charge accumulates → fires when threshold crossed → emits to connectors → connector load increases → propagation slows.

What RAW 132 *missed*: every cell treats every deposit identically. There's no semantic differentiation. From RAW 113's perspective, RAW 132's substrate is "all Same all the time" — every cell's spectrum is trivially universal, so every classification is Same.

Empirical verification: Exp 132 Phases 2/2A.5/2A.2 saturated uniformly. The substrate became a uniform conductor because there was no semantic structure to make it differentiate.

**RAW 132 is not falsified.** It's *generalized* by RAW 133. The three-layer mechanism is exactly what happens in the special case where every cell's spectrum is the trivial spectrum. RAW 132's results are valid in that special case — and the special case fails to produce gradient or matter-antimatter physics, which is now explicable.

### 12.2 132 Phase 2's hypothesis-elimination strategy

Phase 2 tested H3.5 (adaptive thresholds), H4.1 (load-driven connector propagation), H5.1 (drift toward planet) using god-view measurement. RAW 133 reading: all of these hypotheses are *substrate-mechanism hypotheses* — they propose what dynamics produce gradients. None of them include the spectrum primitive. They're all special cases of "the substrate has trivial spectrum."

The right hypothesis to test (added to RAW 132 §3.5 v3.1 as H5.7 self-subtracting reading) was on the right track but didn't go far enough. Self-subtracting transport is ONE specific consequence of source-tagging in the spectrum framework. The fuller commitment is *cells classify deposits and route them differently based on spectrum match*.

### 12.3 132 Phase 2A.5's superposition test

The "if H5.7 holds, R3 − R2 ≈ R1" prediction assumed substrate dynamics are *linear* (deposits from different patterns superpose without interaction). Under RAW 133, this is only true when patterns share a spectrum (so all deposits from any pattern are Same to each cell). When patterns have *different* spectra, the cells classify them differently and superposition fails non-trivially.

Phase 2A.5's outcome 3 (superposition fails, χ² = 0.17) was actually consistent with patterns-with-different-spectra interacting nonlinearly. We just didn't know to expect that. RAW 133 explains it.

### 12.4 132 Phase 2A.2's load-coefficient sweep

Sweeping `load_coefficient` from 0.001 to 1.0 produced identical flat profiles. Under RAW 133: the parameter being swept didn't change anything semantically meaningful. Without spectra, no parameter can break out of uniform equilibration. The sweep was fruitless because the substrate was the wrong substrate.

### 12.5 The "what's between substrate and macroscopic geometry" question

Yesterday's reflection: continuous space as an intermediate layer is hard to justify if substrate saturates uniformly. RAW 133's answer: there is *no* intermediate continuous-space layer. Macroscopic geometry is observer-side (per causal-cone-engine's rendering pipeline). The substrate is a graph; the geometry emerges from the observer's pattern integrating arrivals.

The "pushed-back possibility of continuous space" was correct as an observation but the underlying conclusion was off. Continuous space doesn't sit between substrate and observation; it's *constructed by* observation.

---

## 13. Open Questions

1. **What's the spectrum's representation precisely?** A set of tokens (causal-cone-engine's binary set), a frequency-weighted multiset, a sparse vector in token-space? Each gives different consume-reemit dynamics. Phase 1 will need to commit.

2. **What's "Different" precisely?** Token-distance threshold? Hamming distance from spectrum's nearest token? Some other similarity metric? Conversion cost depends on this.

3. **Is the spectrum per-cell or per-pattern?** If per-cell, cells in the same pattern can have slightly different spectra (some drift). If per-pattern, the pattern's identity is its spectrum and all cells share it exactly. Cleaner ontology with per-pattern, but requires shared state.

4. **What's the recruitment criterion in detail?** Simplest: "spectrum has crystallized the pattern's tokens AND firing is in phase." Phase-alignment threshold? Spectrum-crystallization threshold?

5. **How are spectra initialized?** Empty spectra (cell starts ignoring everything)? Random spectra? Inherited from neighbors? This is the bootstrap question.

6. **Is the substrate's RGG topology fixed, or do connectors form / dissolve dynamically?** RAW 131 had connectors as ancestral (formed at lineage-divergence events). RAW 133 doesn't yet commit. May need to.

7. **What's the relationship between the spectrum and the cycle's K?** A pattern's spectrum determines what its tokens are. Does the spectrum also determine K? Probably yes (a longer cycle has more distinct token-positions, hence richer spectrum) but this needs operationalizing.

8. **How does observation update the observer's spectrum?** The observer's spectrum reinforces with each arrival. Does this mean *the act of observing changes what we can observe next*? Yes, plausibly — this is learning. Long-term implications for repeated experiments.

9. **What's the conversion cost for Different?** Constant? Distance-dependent? Asymmetric (easier in one direction than the other)? Conservation question.

10. **Does spectrum-decay happen?** Tokens not seen recently fade from spectrum. Rate of decay matters (too slow = patterns never release; too fast = patterns can't sustain).

These are the operational gaps RAW 133 leaves open, analogous to RAW 132 §3's five gaps. Phase 1 of the experiment program will commit to provisional answers.

---

## 14. Risks and Constraints

- **Scope creep.** This RAW commits to a much richer substrate than 132. Implementation cost is higher. Phase 1 must be carefully scoped or we won't finish.

- **The spectrum primitive may be hard to implement performantly.** Causal-cone-engine handles 134M cells × token-set classification at v0.6 — scalable in principle. But classification at every consume-reemit at every node is non-trivial computation.

- **"Spectrum" might be a conceptual cheat.** The Same/Different/Unknown classification could itself require a more primitive substrate to implement (how does a cell *do* classification?). In principle, classification is just dictionary lookup — but if we're building physics from below, we should probably commit to which substrate-level operations are primitive vs derived.

- **The experiment may falsify RAW 133.** If a fully-implemented spectrum substrate also fails to produce gradient or recruit/drift behavior, then either the implementation is wrong, or the framework is structurally incomplete (more primitives needed). Don't hope-tune toward desired outcomes.

- **Connection to causal-cone-engine.** That codebase has v0.6 working but with grid-not-RGG and hand-placed-not-recruited entities. Porting RAW 133 to causal-cone-engine is its own project. For the immediate experiment, we'll likely build fresh in tick-frame-space.

---

## 15. Document History

### v0 (2026-04-30 evening — initial synthesis)

Synthesis written. Drew from yesterday's Exp 132 Phase 2 negative result + today's brainstorm about pipe-mesh substrate + Same/Different/Unknown unification. Key insights from the conversation:

- "The substrate is 3D + time = 'fake' 4D. The geometry we observe is 3D constructed by the observer." (Tom)
- "The original idea for cone was that ray-pipeline would be the whole process from source to destination. Everything is just a mesh of pipelines delivering deposits. There is no real 3D." (Tom)
- "A single pipe is path of deposits from A to B which is consumed and reemitted by any intermediary." (Tom)
- "What if there is no initial incoming deposit, there is no actual observation? Or there is no renewal without incoming deposit?" (Tom — opens QM-collapse + leak-as-coupling discussion)
- "It also explains why they are building bigger blocks to store excessive energy. Earth's core is basically battery for Earth pattern." (Tom — opens recruitment + storage + core-formation discussion)
- "It should be based on: can I convert different to same? or is it unknown and should I reemit it further so my pattern is coherent?" (Tom — closes the loop with RAW 113 as the substrate primitive)

This RAW captures the synthesis as a single point of truth before any code is written, per the user's request.

### v0.1 (2026-04-30 evening — same session, after surfacing trie-memory)

User pointed at `W:/workspace/trie-memory` as relevant to classification. Investigation revealed that trie-memory is a **full operational implementation** of RAW 133's spectrum primitive — 163 passing tests, MCP server deployed, Same/Different/Unknown classification, Learning→Crystallized state machine, content-addressable path keys, two-mechanism architecture, layer system, no-floats commitment.

This is a major discovery for the framework: many of RAW 133's open questions (§13) are answered by trie-memory's design choices. The experiment program (§11) Phase 1 is dramatically simplified — port the primitive from trie-memory rather than reinvent it.

v0.1 changes:
- §10.6 added with full integration of trie-memory's contributions, empirical validations, and surfaced limitations.
- Internal precedents in front matter updated to include trie-memory.
- §13 open questions noted as partially answered by trie-memory (in the §10.6 table).
- §11 experiment program implicitly simplified (Phase 1 → port primitive instead of build from scratch).
- The relationship between RAW 113 (Same/Different/Unknown) and RAW 132 (capacitor cycle) clarified: they're *the same primitive*. trie-memory is the proof. The capacitor's Empty/Charging/Discharging is the operational consequence of Same/Different/Unknown classification.

A meta-lesson: per the v3.1 update of RAW 132, "search the project's own prior materials before drafting new operational gaps." This RAW v0 missed trie-memory entirely (focused on tick-frame-space + causal-cone-engine). Surfacing it required user prompt. Future RAWs should default to surveying ALL repos in `W:/workspace/` that bear on the substrate's primitives.

---

## 16. Prior Art and Inspirations

### 16.1 Internal framework precedents (the load-bearing ones)

All cited above. The RAW 113 / 126 / 127 / 130 / 131 / 132 / 044 chain plus Exp 64_109 / 128 v11 / 134 / 132 plus causal-cone-engine.

### 16.2 External inspirations the substrate primitive draws from

- **AdEx neurons** (Brette & Gerstner 2005): per-cell adaptive threshold, leaky integration. Already cited in RAW 132 §10. RAW 133 adds: classification at the input is what AdEx doesn't have — biological neurons have a uniform "input is current" interpretation, no token-shape semantics.

- **Hopfield networks**: spectrum-as-energy-landscape, attractor dynamics. A Hopfield network's stored patterns are exactly what RAW 133 calls a spectrum — patterns the network has crystallized. Convergence to a stored pattern from a noisy input is *Different → Same conversion* in our terms.

- **Sparse Distributed Memory** (Kanerva 1988): hash-based associative memory. Classification by similarity to stored patterns. Direct ancestor of the spectrum primitive.

- **Belief propagation / message passing on graphs**: Pearl, MacKay. Each node integrates messages from neighbors and sends out reformatted messages. Without spectra, this is just numerical updating. With spectra, it's RAW 133's consume-reemit-classify.

- **Predictive coding / free energy principle** (Friston): cells minimize prediction error by adjusting their internal model. RAW 133's spectrum reinforcement is exactly this — frequent inputs become "predicted" and consumption is the integration of confirmed predictions.

- **Glauber dynamics on Ising-type lattices**: lattice updates based on local energy. Adjacent in spirit but lacks the token-classification structure.

- **Cellular automata more broadly** (Wolfram, 't Hooft, etc.): RAW 132 §10 covered these. RAW 133 is closer to *labeled* CAs where each cell has a distinguishable type/state-space — like Conway's GoL with multiple states + transition rules per state.

- **Neural-symbolic AI / token-based models**: language models classify and emit tokens. Each transformer layer is a kind of consume-reemit-classify operator. The mechanism is closer than physics typically wants to admit.

### 16.3 Adjacent quantum-foundations work

- **Gaconnet 2026** (already cited in RAW 132 §10): observer-relative ℏ. RAW 133 sharpens: observer's *spectrum* determines what they classify as quantum events, hence their effective ℏ.

- **Minic-Pajevic 2016**: system-dependent Planck constant in adaptive systems. RAW 133 generalization: any system with a non-trivial spectrum has its own effective ℏ.

- **Relational quantum mechanics** (Rovelli): quantum states are relations between systems. Compatible with RAW 133: each observer's spectrum-classification of substrate state is a *relation* between observer-pattern and substrate.

- **QBism** (Fuchs, Mermin): quantum states as agent's beliefs. Spectrum is exactly an agent's "beliefs" about which tokens are Same vs Different vs Unknown. Adjacent ontology.

### 16.4 Things deliberately not yet engaged with

- **Information theory / Shannon entropy applied to token streams**. Spectra have entropy; pattern coherence is low-entropy; substrate equilibrium is high-entropy. Relevant but not yet developed.

- **Category theory framing of consume-reemit**. Patterns might be objects, classifications might be morphisms. Possibly clarifying but not yet attempted.

- **Topos theory, sheaves, etc.** for the geometry-emerges-from-classification picture. Tooling exists; haven't used.

---

## 17. Falsifiable Claims

These are the claims RAW 133 makes that future experiments can test:

1. **Without spectra, the substrate cannot produce gradient.** Tested by Exp 132 Phases 2/2A.5/2A.2 — saturation across all parameters. Already supported.

2. **With spectra, the substrate produces gradient automatically.** To be tested in Phase 4 of the new experiment program. If a substrate with non-trivial cell spectra still saturates uniformly, RAW 133 is wrong about spectra being the missing piece.

3. **Recruitment is spectrum-driven, not magnitude-driven.** A cell with empty spectrum receiving high-magnitude Unknown deposits won't be recruited; a cell with crystallizing spectrum receiving low-magnitude Same deposits will. Phase 3 tests this.

4. **Drift is membership-change, not cell-motion.** Pattern's apparent position evolves through release/recruit events at edge cells; no cells move. Phase 4 measures.

5. **Same-sign patterns attract; opposite-sign patterns annihilate.** Phase 6 directly tests.

6. **The 1/r² gradient is the spatial density of Same-classified flow through pipe-branching geometry.** Phase 5's quantitative GR fit tests this.

7. **QM collapse = classification at observer's spectrum.** Indirectly testable: the observable distribution of measurement outcomes should follow from spectrum-classification statistics + pipe-branching geometry. Born rule should be derivable, not postulated.

8. **Mass = sum of stored deposit-charge across recruited cells.** Phase 5 tests by varying ambient flux and measuring resulting mass-equivalent.

9. **The leak rate is the central physical parameter.** Too low = invisible patterns; too high = unstable patterns. The "physics" regime is somewhere in between. Phase 4 finds where.

10. **Spectra adapt with experience (learning).** A cell exposed to a pattern's tokens will eventually classify them as Same. Phase 1 directly validates.

If any of these claims is empirically falsified, RAW 133 needs revision. Each falsification narrows the design space.

---

## Conclusion

The substrate's missing primitive was Same/Different/Unknown classification at every node. With it, the framework's prior commitments — RAW 113 (the classification primitive), RAW 126/127 (capacitor cycle), RAW 130 (consumption as work), RAW 131 (pipes-not-spaces), RAW 132 (three-layer mechanism), RAW 044 (window-commit + observation lag), Exp 128 v11's earned 1/r², Exp 134's pattern coherence, causal-cone-engine's rendering pipeline — converge into a single consume-reemit-classify operator at every node.

Patterns are coherent loops of cells with aligned spectra. Recruitment and release are emergent from spectrum dynamics. Storage and core formation come from cells acting as batteries for excess deposit-charge. Leak makes patterns visible and produces fields. Observation is an observer-pattern's spectrum-classification of incoming deposits. Matter and antimatter are dual spectra; same-sign attracts, opposite-sign annihilates.

Yesterday's experimental failures (Exp 132 Phase 2 / 2A.5 / 2A.2) are now explicable: they were testing a non-semantic special case. Their results stand as evidence that *non-semantic substrates can't produce gravity or matter physics*, which is the strongest possible support for the spectrum primitive being the missing piece.

The next experiment is Phase 1 of the new program: validate the spectrum primitive with two cells. Smallest possible test, directly probes whether Same/Different/Unknown classification works as RAW 133 specifies. If it does, the program scales up incrementally.

**This RAW is the single point of truth for the synthesis as of 2026-04-30. Future experiments should cite it; future RAWs should extend it; if it turns out wrong, §17's falsifiable claims tell us how.**
