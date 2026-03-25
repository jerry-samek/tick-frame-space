# RAW 400: Open Questions and Experimental Status

**Date**: March 25, 2026
**Status**: Working document — consolidates honest open questions for the V3 graph-first framework
**Supersedes**: RAW 200 (February 20, 2026) — which addressed gamma field / lattice questions now obsolete
**See also**: [V3 Ch7 — Experimental Status](../V3_ch007_experimental_status.md), [V3 Ch8 — Open Questions](../V3_ch008_open_questions.md)

---

## Why This Document Exists

RAW 200 tracked open questions for the **gamma field on cubic lattice** model (Exp 64_109, v1–v10).
Between February and March 2026, the theoretical framework shifted to **V3: graph-first, trit-based ontology** (RAW 108–127). The lattice experiment arc was extended to v24 and then **closed** (see `experiments/64_109_three_body_tree/CLOSURE.md`).

Nearly all RAW 200 questions are now either answered, superseded, or reframed. This document:

1. Records what happened to each original question
2. States the current open questions under the V3 framework
3. Maintains the project's commitment to honest self-assessment

---

## What Happened to RAW 200's Questions

### 1. Force Law Convergence (1/r^2.2 exponent) — OBSOLETE

The 0.2 excess was measured on a cubic lattice with passive-reading gravity. RAW 118 (Gravity as Consumption-Transformation) identified the root cause: **passive reading is half the mechanism**. Entities must consume deposits, transform them, and deposit their own pattern. The lattice model was architecturally incomplete, not just poorly tuned.

The force law question now applies to the graph substrate, where it has not yet been measured.

### 2. Conservation Laws — REFRAMED

No longer about energy conservation in a gamma field. The V3 framework reframes this as **information conservation in the trie** (V3 Ch5). The append-only substrate guarantees no information is destroyed. Whether this maps to a conserved physical quantity remains open.

### 3. Equal-Mass Problem — OBSOLETE

Same root cause as #1. The symmetric gradient problem was specific to the passive-reading model. The consumption-transformation mechanism (RAW 118) creates asymmetry through deposit pattern differences, not field gradients.

### 4. Composite Object Stability — OPEN, REFRAMED

Still unanswered, but reframed: what holds a bound state together is now a question about **trie structure** — how do multiple entities sharing overlapping deposit histories maintain coherent identity across ticks? See V3 Ch8.

### 5. Continuum Limit — SUPERSEDED

The V3 framework proposes the substrate is a fundamentally **append-only graph**. RAW 126–127 (The Trit as Capacitor) argues discreteness is emergent at the consumer's discharge threshold — the substrate itself may be continuous underneath. The lattice continuum limit question no longer applies.

### 6. Photon Ontology — PARTIALLY ANSWERED

RAW 113 (Semantic Isomorphism) gives the first formal definition: a photon is a **Different event** propagating through the graph — divergence recorded and forwarded. Not an entity, not a field mode. Whether this produces correct photon properties (speed, polarization, interference) is untested.

### 7. GR Connection — REFRAMED

No longer seeking derivation of Einstein field equations from gamma dynamics. Instead: geodesic-like motion should emerge from **Same routing** (entities follow the laziest/most familiar connector). V3 Ch3 (Emergent Geometry) describes how the observer reconstructs geometry from a latency matrix. Whether this reproduces GR quantitatively is the open question.

---

## Current Open Questions (V3 Framework)

### Foundational

**Q1. Formal definition of the Same comparison operator**

The framework claims entities follow "familiar" connectors (Same routing → gravity). But what is "familiar" formally? Hamming distance on deposit patterns? Dot product? Topological overlap? Threshold match?

Different definitions produce different force laws. This is the single most important open question — it determines whether the framework can make quantitative predictions.

*What would answer this:* A formal definition that, when simulated on a random geometric graph, produces 1/r² attraction without tuning.

**Q2. Deposit pattern matching semantics**

What exactly is the "arriving pattern"? What is the "existing deposit state"? How are they compared? RAW 112 states the mechanism (deposit → hop → extend) but the comparison step is described qualitatively, not formally.

*What would answer this:* A mathematical specification precise enough to implement unambiguously.

**Q3. Where does deposit strength come from?**

The single mechanism has zero free parameters *except* deposit strength per hop, which remains underived. Is it always 1? Does it depend on entity history? Is it the same for all entities?

*What would answer this:* Either a derivation from the framework's axioms (RAW 122) or an experiment showing the value doesn't matter (universality).

### Quantitative Predictions

**Q4. Force law on graph substrate**

Curved trajectories and radial reversal achieved (Exp 64_109 v23). Velocity stabilization achieved (v23). But: no closed orbit, no measured force exponent, no quantitative comparison with 1/r².

*What would answer this:* A graph-substrate experiment producing a closed orbit with measured force law.

**Q5. Time dilation from branch depth**

V3 Ch4 claims time = branch depth. Exp 51 achieved r=0.999 time dilation on a continuous field, but on a **lattice substrate** with hand-tuned metric. On the graph substrate: not tested.

*What would answer this:* Branch depth accumulation producing measurable time dilation on a random geometric graph, without hand-tuned parameters.

**Q6. Three-state alphabet as observable physical states**

The core claim (RAW 113): Same/Different/Unknown exhaust all possible comparison outcomes and map to gravity/radiation/expansion. This has not been tested experimentally — it's a logical argument, not a measured result.

*What would answer this:* An experiment where the three states produce three measurably different physical behaviors, with no fourth behavior observed.

### Structural

**Q7. Extended body composition**

How do multiple entities form a stable composite? What determines binding energy? How does a composite respond to external gradients? This was open in RAW 200 and remains open.

*What would answer this:* Multi-entity bound states on graph substrate with measurable stability and gravitational response.

**Q8. The consumption-transformation balance**

RAW 118 identified that gravity requires both consumption (inward routing) and transformation (outward deposit). Exp 118 v1–v2 showed early results. But: what determines the balance? Too much consumption → collapse. Too much transformation → dispersal.

*What would answer this:* Parameter sweep on consumption/transformation ratio showing a stable regime, ideally with the ratio derived from the framework rather than tuned.

---

## What We Should NOT Claim (Updated)

From RAW 200, still valid:
- ~~"Equations unchanged"~~ — we have custom dynamics, not standard physics
- ~~"Complete ontology"~~ — we have a framework and early experiments, not a complete theory
- ~~"Conservation laws"~~ — not demonstrated on any substrate

New additions:
- ~~"The single mechanism produces all physics"~~ — it's a claim, not a result. The mechanism is stated (RAW 112) but only qualitatively validated
- ~~"Space is emergent"~~ — the argument is logical (RAW 110–111), not experimental. No simulation has produced emergent 3D geometry from a raw graph
- ~~"Consciousness is trie depth"~~ — this belongs in the 500 series (speculation), not in the main framework

---

## What Experiments Have Demonstrated (March 2026)

### On Graph Substrate (V3, random geometric graph)
- Star formation gradient from seed deposit
- Force measurement and derived orbital velocity
- Curved trajectories under gravitational force
- Radial reversal (particle changed direction)
- Velocity stabilization (equilibrium found)
- Self-pinning: dense bodies resist expansion automatically

### On Lattice/Field Substrates (V2, mechanism may transfer)
- 433 stable revolutions at r~2 (Exp 64_109 v10)
- Time dilation r=0.999 (Exp 51)
- Geodesic orbits from time gradients, no force laws (Exp 53)
- Collision physics with emergent Pauli exclusion (Exp 55)

### Substrate-Independent (survives any substrate)
- ρ=2.0 proves time is categorically different from spatial dimensions (Exp 50)
- Rotation asymmetry 933× (Exp 44)
- Natural data produces hierarchy, random data doesn't (Exp 118 v7, RAW 123)

### Stream Filtering Arc (Exp 118)
- v1–v3: Gravitational binding from consumption-transformation
- v4–v6: Producer-consumer filtering, recursive hierarchy, token routing
- v7: N-gram stream filtering — sequential structure in text/DNA/random
- v8: Causal window — inverted hierarchy
- v9: Video frame decomposition — root learns "no change", children handle motion
- v10: Store and reconstruct — trie as reversible memory (26.3 dB PSNR, 100% recovery)

---

## The Right Approach

Same as RAW 200 concluded, and still true:

> Run more experiments, measure more things, let the physics tell us what's true.

The framework is more coherent now (single mechanism, three states, derivation chain from self-recognition). But coherence is not validation. The gap between theoretical claims and experimental demonstration remains large. Close it with experiments, not with more theory documents.

---

*Moved from RAW 200 (February 20, 2026) to RAW 400 (March 25, 2026).*
*The 400 series sits between the main theory sequence (001–399) and the speculation series (500+).*
*Next update when Q1 (Same comparison operator) or Q4 (closed orbit on graph) is resolved.*
