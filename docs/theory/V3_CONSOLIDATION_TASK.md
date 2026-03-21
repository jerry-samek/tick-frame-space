# Theory Corpus V3 Consolidation Task

**Date:** March 15, 2026  
**Author:** Tom  
**For:** Claude Code  
**Status:** Ready for execution (after REFACTORING_TASK.md is complete)  
**Depends on:** REFACTORING_TASK.md — complete the raw/ archive/ review/ restructure first

---

## Background

### What V2 Was

Version 2 (January 2026) consolidated the first ~76 raw documents into 13 chapters
(`ch001` through `ch013`) plus supporting documents (`honest_status.md`, `glossary.md`,
`experiment_index.md`, etc.). It was written under a specific set of assumptions about
the substrate:

> **V2 Core Assumption**: Time is the primary substrate. Entities are temporal processes
> on a tick-stream. Space is emergent from temporal gradients. Geometry is Euclidean at
> the Planck scale. Connectors are edges on a discrete lattice.

This assumption is now superseded.

### What Changed Between V2 and V3

Between February and March 2026, the theoretical foundation shifted fundamentally.
The key documents establishing the new baseline are:

| Document | Date | What It Established |
|----------|------|---------------------|
| RAW 108 | Feb 2026 | Three dimensions from trit change geometry |
| RAW 109 | Feb 2026 | Apparent isotropy of c |
| RAW 110 | Feb 2026 | Local dimensionality — dimension is observer property |
| RAW 111 | Feb 2026 | Space is connections — connectors are deposit chains |
| RAW 112 | Mar 2026 | The single mechanism — one operation, all physics |
| RAW 113 | Mar 2026 | Semantic isomorphism — same/different/unknown |

**The V3 Core Assumption** (replacing V2):

> The substrate is a raw graph with no geometry. Nodes connect via edges.
> The only primitive operation is: deposit on a connector, hop, connector extends.
> Geometry is reconstructed by observers from causal latency matrices.
> Dimension is an observer property, not a substrate property.
> Time is branch depth — the number of append operations since an observer's depth-zero.
> All physical phenomena (gravity, radiation, expansion) are outcomes of three comparison
> states: Same / Different / Unknown.

### The Paradigm Shift in One Table

| Concept | V2 (Geometric Era) | V3 (Graph Era) |
|---------|-------------------|----------------|
| Substrate | Discrete Euclidean lattice | Raw graph, no geometry |
| Space | Emergent from temporal gradients | Emergent from observer latency matrix |
| Time | Primary substrate (tick-stream) | Branch depth — observer property |
| Connectors | Edges on fixed grid | Deposit chains |
| Dimension | Substrate property (3D Goldilocks) | Observer property (minimal embedding) |
| Geometry | Planck-scale voxels | Observer reconstruction |
| Gravity | Time gradient following | `same` — familiarity routing |
| Radiation | Propagating disturbance | `different` — divergence propagating |
| Expansion | Dark energy / field dilution | `unknown` — frontier writing |
| Information | Stored in field values | Stored in branch topology |
| Observer | Temporal trajectory | Trie traversal |

---

## Objective

Produce **Version 3** of the consolidated theory — a clean, accurate, graph-first
document set that reflects the current state of the theory as of March 2026.

V3 must be **honest** about what is validated, what is speculative, and what has
been superseded. It is not a marketing document.

---

## Scope

### What V3 Must Cover

1. **The graph substrate** — nodes, edges, deposit operation, the single mechanism
2. **The three-state alphabet** — same / different / unknown and their physical mappings
3. **Emergent geometry** — latency matrix, observer reconstruction, dimensionality
4. **Branch depth as time** — arrow of time, time dilation, Big Bang as depth-zero
5. **Emergent physics** — gravity, radiation, expansion from the three states
6. **The trie structure** — information storage, compression, similarity search
7. **Observer model** — trie traversal, snapshots, media degradation
8. **Experimental validation status** — honest, current as of March 2026
9. **Open questions** — formal gaps, quantitative derivations needed

### What V3 Must NOT Do

- Retain V2's "time is the primary substrate" framing
- Present Planck-scale Euclidean geometry as physical
- Claim experimental results from V2-era experiments prove the V3 substrate
  (those experiments used lattice/field substrates, not the graph substrate)
- Over-claim. The graph substrate has fewer validated experiments than V2's
  substrate. Be honest about this.

---

## Input Documents

### Primary Sources (Must Read First)

Read these in order — they are the current theoretical foundation:

1. `raw/111_space_is_connections.md`
2. `raw/112_the_single_mechanism.md`
3. `raw/113_semantic_isomorphism_same_different_unknown.md`
4. `raw/110_local_dimensionality.md`
5. `raw/108_three_dimensions_from_trit_change_geometry.md`
6. `raw/040_dimension_definition_in_tickframe_space.md`
7. `raw/037_observerrelative_big_bang_principle.md`
8. `raw/042_temporal_choice_reconstruction_principle.md`
9. `raw/043_void_asymmetry_principle.md`

### Experimental Arc (Current State)

Read these to understand where the simulations actually are:

1. `experiments/64_109_three_body_tree/v22/experiment_description.md` — current frontier
2. `experiments/64_109_three_body_tree/v22/star_formation.py` — current code
3. `experiments/51_emergent_time_dilation/EXPERIMENTAL_ARC.md` — full history
4. `experiments/51_emergent_time_dilation/v10/RESULTS.md` — last major validated result
5. `docs/theory/honest_status.md` — last honest status (February 2026, now outdated)

### V2 Chapters (Reference — Do Not Copy, Rewrite)

Read these to understand what V2 claimed, then assess each against V3 assumptions:

- `ch001_temporal_ontology.md` — superseded at foundation (time is not the substrate)
- `ch002_dimensional_framework.md` — partially salvageable (3D optimality result may
  survive but derivation is wrong)
- `ch003_entity_dynamics.md` — partially salvageable (entity as process, collision
  physics may survive)
- `ch004_observer_consciousness.md` — substantially salvageable (reframe as trie
  traversal)
- `ch005_free_will_ternary_logic.md` — review for compatibility
- `ch006_rendering_theory.md` — review (rendering uses lag-as-depth, may survive)
- `ch007_physical_formalization.md` — largely superseded (Planck-scale Euclidean
  formalization)
- `ch008_integration_falsification.md` — superseded (integration of V2 framework)
- `ch009` through `ch013` — gamma field theory, review for compatibility with
  graph-first substrate

---

## V3 Document Structure

### Core Documents (New Writes)

#### `V3_README.md`
Entry point. Replaces `README.md`.

Contents:
- What the theory claims (graph substrate, three states, emergent everything)
- What is validated vs speculative (honest, current)
- Reading paths for different audiences
- Link to V2 for historical reference
- Brief statement of what changed from V2 and why

#### `V3_ch001_the_graph_substrate.md`
The physical foundation. Replaces ch001 (temporal ontology).

Contents:
- The graph as the only primitive (nodes, edges)
- The single operation: deposit → hop → connector extends (from RAW 112)
- Connectors as deposit chains (not geometric edges)
- The append-only guarantee
- What "nothing can be destroyed" means physically
- Connection to unitarity / information paradox

Key sources: RAW 111, RAW 112

#### `V3_ch002_three_states.md`
The complete physical alphabet. New document (no V2 equivalent).

Contents:
- Same / Different / Unknown — the three comparison outcomes
- Same → gravity (familiarity routing)
- Different → radiation (divergence propagating)
- Unknown → expansion (frontier writing)
- Why these three are exhaustive (no fourth state)
- Photon as `different` event, not entity
- Photon properties as path geometry (frequency, amplitude, polarization)
- Interference as deposit addition/subtraction from two path geometries

Key sources: RAW 113

#### `V3_ch003_emergent_geometry.md`
How space appears from a graph. Replaces ch002 (dimensional framework).

Contents:
- The causal latency matrix: L_ij = t_j - t_i
- Dimension as minimal embedding (observer property, not substrate property)
- Why 3D emerges as the natural minimal embedding for our universe
- Configuration independence
- Local dimensionality (RAW 110)
- Why geometry is not physical — it is a read operation
- Self-pinning: dense bodies resist expansion automatically (from v22 Phase 0)

Key sources: RAW 040, RAW 110, RAW 112 §2.7, experiment 64_109 v22

#### `V3_ch004_time_and_depth.md`
Branch depth as time. New document.

Contents:
- Branch depth as the only clock
- Arrow of time: append-only means depth only increases
- Time dilation: depth accumulation rate differences (from self-pinning)
- Big Bang as depth-zero (observer-relative, from RAW 037)
- Why perfect storage is impossible (snapshot drift)
- Media degradation as substrate honesty
- The simulation argument dissolved (shared axiom at all levels)

Key sources: RAW 037, RAW 113 §4-§6

#### `V3_ch005_information_and_trie.md`
The universe as information structure. New document.

Contents:
- The trie structure: branch points as `different` events
- Information stored as divergence topology (not field values)
- Compression for free: `same` consumes no new structure
- Similarity search = the movement rule (laziest connector)
- Writing = the only creative act (encountering `unknown`)
- Observer as trie traversal
- Identity as accumulated path
- Snapshots and restarts
- Equilibrium is unreachable — information grows forever

Key sources: RAW 113

#### `V3_ch006_observer_and_consciousness.md`
Observer model reframed. Substantially rewrites ch004.

Contents:
- Observer as trie traversal (replaces "temporal trajectory")
- Memory as path history (replaces "buffer addressing")
- Consciousness as active traversal (not passive presence)
- Sleep as buffer suspension (RAW 035 — survives substrate change)
- Death as traversal termination
- The snapshot question: when does identity persist?
- Multiple instances from the same snapshot

Key sources: RAW 035, RAW 042, RAW 113 §5

#### `V3_ch007_experimental_status.md`
Honest current status. Replaces `honest_status.md`.

**CRITICAL: This must be strictly honest.**

Contents:
- Which experiments used V2 substrate (lattice/field) vs V3 substrate (graph)
- V2-substrate results: what they prove about the *mechanism*, not the substrate
- V3-substrate experiments: what has actually been tested on the graph
- Current frontier: experiment 64_109 v22 — what it has and hasn't shown
- The honest gap: v22 has curved trajectories but not closed orbits yet
- What would constitute validation of the V3 substrate specifically

Structure:

```
## V2-Substrate Validated Results (mechanism may transfer, substrate changed)
  - Time dilation: r ≈ 0.999 (Exp 51 v9) — continuous field substrate
  - Geodesic orbits: 100% (Exp 53 v10) — continuous field substrate
  - Collision physics + Pauli exclusion (Exp 55) — lattice substrate
  - Graph-lattice gravity (Exp 64_109 v8-v9) — cubic lattice

## V3-Substrate Work In Progress (random geometric graph + deposit chains)
  - Star formation gradient: established (v22 Phase 0)
  - Proto-disk with derived orbital velocity: first curved trajectories (v22 Phase 2)
  - Status: orbit not yet closed, velocity/threshold bugs identified

## What V3 Needs to Validate
  - Closed orbit from self-organized proto-disk (no preset velocity)
  - 1/r² force law from deposit gradient
  - Time dilation from self-pinning (depth accumulation rate)
  - `same`/`different`/`unknown` as explicit observable states
```

#### `V3_ch008_open_questions.md`
Replaces `open_questions.md`. Current frontier questions only.

Priority open questions as of March 2026:

1. Formal definition of `same` comparison operator
2. Photon properties as path geometry — quantitative derivation
3. Depth as proper time — does ratio of accumulation rates reproduce Lorentz factor?
4. Semantic encoding — minimum perturbation to write one bit
5. Snapshot drift rate — derivable from local `different` event rate?
6. Connector formation rule — what makes two nodes connect?
7. Deposit strength from entity mass — the last free parameter
8. Traversal-driven expansion replacing H
9. Closed orbit from proto-disk (v22 Phase 3 target)
10. Baryon asymmetry quantitative prediction

---

### Supporting Documents (Update, Not Rewrite)

#### `V3_glossary.md`
Update `glossary.md` with V3 definitions.

Key terms needing update or addition:
- **Substrate**: raw graph (not tick-stream, not Euclidean lattice)
- **Connector**: deposit chain (not geometric edge)
- **Time**: branch depth (not tick-stream)
- **Geometry**: observer reconstruction from latency matrix (not Planck voxels)
- **Dimension**: observer property — minimal embedding (not substrate property)
- **Same / Different / Unknown**: the three-state alphabet (new)
- **Trie**: the information structure the substrate naturally produces (new)
- **Depth-zero**: observer's personal Big Bang (was: substrate event)
- **Self-pinning**: dense bodies resist expansion via deposit density (new)
- Remove or mark obsolete: Planck cube, tick-stream primacy, voxel

#### `V3_experiment_index.md`
Update `experiment_index.md` to reflect:
- Which experiments used which substrate
- Current status of 64_109 (v22, not v10 as in current docs)
- Remove claims that V2 experiments validate V3 substrate

---

### Archived V2 Documents

Move all current `ch001` through `ch013` to `docs/theory/v2_archive/`.
Move `README.md` to `docs/theory/v2_archive/README_v2.md`.
Move `honest_status.md` to `docs/theory/v2_archive/honest_status_v2.md`.

Do NOT delete them. V2 is historical record and may contain useful content
for V3 chapters.

Create `docs/theory/v2_archive/README.md` explaining:
- V2 was written January-February 2026
- V2 used geometric/lattice substrate assumptions
- V2 results may be valid but substrate descriptions are superseded
- V3 is the current version

---

## What V3 Must NOT Claim

Be precise about this — it is the most important constraint.

**Do not claim** that Experiment 51 (continuous field time dilation, r=0.999) validates
the V3 graph substrate. It validates a specific mechanism (gradient following → orbits)
on a specific substrate (continuous reaction-diffusion fields). The mechanism may transfer
to the graph substrate, but this has not been shown.

**Do not claim** that Experiment 55 (Pauli exclusion, collision physics) validates the
V3 three-state alphabet. It validates collision dynamics on a lattice substrate. The
three-state alphabet is a theoretical framework that has not yet been experimentally
instantiated.

**Do not claim** that 64_109 v22 has demonstrated stable orbits. It has demonstrated:
- Star formation from seed deposit ✓
- Gamma gradient establishment ✓  
- Derived orbital velocity from field measurement ✓
- Curved trajectories (first time in this experiment arc) ✓
- Velocity decreasing under force ✓

It has NOT demonstrated:
- Closed orbit
- Angular momentum conservation
- Kepler's third law
- Orbital stability over multiple revolutions

**The honest status of V3 theory is:**
> The graph-first framework is theoretically coherent and internally consistent.
> It has produced the correct qualitative behavior in proto-disk experiments (curved
> trajectories, force acting). Quantitative validation of the core claims (closed orbit,
> force law, time dilation from depth) is in progress.

---

## Writing Guidelines

### Tone
- Scientific, precise, honest
- No marketing language ("revolutionary", "breakthrough")
- Acknowledge what is not yet validated
- Distinguish clearly between "the theory predicts X" and "experiments show X"

### Structure
- Each chapter: Abstract → Core Claim → Derivation → Evidence → Open Questions
- Evidence section must be explicit about which substrate each experiment used
- Open Questions section must be specific and falsifiable

### Cross-References
- Reference RAW documents by number and title
- Reference experiments by number and version
- Do not reference V2 chapters as current — reference them as historical if needed

### Length
- Each chapter: 10-20 pages
- Prefer precision over completeness
- If a topic is not yet validated, say so briefly rather than speculating at length

---

## Suggested Reading Order for V3 Author

Before writing a single line of V3, read in this order:

1. `raw/112_the_single_mechanism.md` — the physical foundation
2. `raw/113_semantic_isomorphism_same_different_unknown.md` — the information theory
3. `raw/111_space_is_connections.md` — what connectors are
4. `raw/110_local_dimensionality.md` — what geometry is
5. `experiments/64_109_three_body_tree/v22/experiment_description.md` — where the
   simulation actually is right now
6. `docs/theory/honest_status.md` — what was validated (February 2026, pre-graph era)

Then read V2 chapters only for reference — what was previously claimed, what may
survive the substrate change, what is definitively superseded.

---

## Definition of Done

### Minimum Viable V3

- [ ] `V3_README.md` — entry point with honest status
- [ ] `V3_ch001_the_graph_substrate.md` — physical foundation
- [ ] `V3_ch002_three_states.md` — complete physical alphabet
- [ ] `V3_ch003_emergent_geometry.md` — how space appears
- [ ] `V3_ch004_time_and_depth.md` — branch depth as time
- [ ] `V3_ch007_experimental_status.md` — honest, current status
- [ ] V2 chapters moved to `v2_archive/`

### Full V3

All minimum viable documents plus:

- [ ] `V3_ch005_information_and_trie.md`
- [ ] `V3_ch006_observer_and_consciousness.md`
- [ ] `V3_ch008_open_questions.md`
- [ ] `V3_glossary.md`
- [ ] `V3_experiment_index.md`

### Quality Check

Before marking done, verify:

- [ ] No V3 chapter claims V2-substrate experiments validate V3 substrate
- [ ] No marketing language
- [ ] Every experimental claim cites specific experiment and version
- [ ] honest_status.md equivalent is present and accurate
- [ ] V2 archive exists and is accessible

---

## Execution Order

1. Complete `REFACTORING_TASK.md` first (raw/ restructure)
2. Read all primary sources listed above
3. Write `V3_ch001` through `V3_ch004` (core theory)
4. Write `V3_ch007` (experimental status — must be honest)
5. Write `V3_README.md`
6. Move V2 to archive
7. Write remaining chapters if time permits

Do not start V3 writing before reading RAW 112 and RAW 113 in full. These two documents
are the theoretical foundation of V3. Everything else builds on them.

---

## Notes for Claude Code

### The Hardest Part

The hardest part of this task is accurately representing what is and is not validated.
V2's `honest_status.md` was very good at this. V3 needs the same discipline.

The temptation will be to say "the graph substrate produces gravity because Exp 51
showed gradient-following produces orbits." This is wrong. Exp 51 used a continuous
field substrate. The graph substrate is different. The mechanism may be the same but
the substrate is not. Be precise.

### When In Doubt

If you are uncertain whether a V2 result survives the substrate change:

- Put it in V3 as "mechanism may transfer — not yet validated on graph substrate"
- Do not present it as validated
- Do not omit it entirely — it is useful historical information

### The Goal

A reader who finishes V3 should understand:
1. What the theory claims (graph, three states, emergent everything)
2. What has actually been demonstrated in simulation
3. What the gap between 1 and 2 is
4. What experiments would close that gap

If they understand those four things, V3 has succeeded.

---

*Date: March 15, 2026*  
*Status: Ready for execution after REFACTORING_TASK.md is complete*  
*Estimated effort: 2-3 sessions for minimum viable V3, 4-5 for full V3*
