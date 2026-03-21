# Theory Corpus Refactoring Task

**Date:** March 15, 2026  
**Author:** Tom  
**For:** Claude Code  
**Status:** Ready for execution

---

## Background

The theory corpus in `docs/theory/raw/` contains ~113 documents written over several months.
The documents were written in roughly chronological order and reflect a major paradigm shift
that occurred around RAW 108-111:

**Before RAW 108:** The substrate was assumed to be a discrete geometric lattice (Euclidean
space with Planck-scale voxels). Connectors were edges on a fixed grid. Distance, dimensionality,
and geometry were primitives.

**After RAW 108:** The substrate is a raw graph with no geometry. Geometry is an emergent
observer property — reconstructed from causal latency matrices (RAW 040, RAW 110). Connectors
are deposit chains (RAW 111, RAW 112). Dimensionality is a reader property, not a substrate
property. The graph is the only primitive.

RAW 113 (March 15, 2026) is the current frontier document.

This paradigm shift means a significant portion of the older documents are either:
1. **Superseded** — derived from geometric assumptions that are now wrong at the foundation
2. **Transitional** — conclusions may still hold but substrate descriptions need updating
3. **Still valid** — observer behavior, rendering theory, experimental results that survive
   the substrate change

---

## Objective

Reorganise the corpus into a structure that makes the current state of the theory clear,
preserves historical documents without deleting anything, and gives future readers a clean
entry point into the graph-first framework.

---

## Proposed Directory Structure

```
docs/theory/
  raw/              ← ACTIVE: current graph-first theory documents
  archive/          ← SUPERSEDED: geometric-era documents, kept for reference
  review/           ← TRANSITIONAL: needs case-by-case human decision
  REFACTORING_TASK.md   ← this file (delete after completion)
```

---

## Triage Criteria

### Move to `archive/` if the document:
- Derives physics directly from Euclidean/lattice geometry as a substrate primitive
- Defines distance, mass, or velocity in terms of Planck-unit grid coordinates
- Treats connectors as fixed geometric edges rather than deposit chains
- Has been explicitly superseded by a later document that says so
- Is a `.tex` duplicate of an `.md` document

### Move to `review/` if the document:
- Has conclusions that likely survive the substrate change but uses geometric language
- Is an experimental result document (results may be valid even if substrate model changed)
- References both geometric and graph concepts (transitional era)
- You are uncertain about

### Keep in `raw/` if the document:
- Is explicitly graph-first (no geometric substrate assumption)
- Is about observer behavior, rendering, consciousness, or simulation (substrate-independent)
- Is RAW 108 or later (written after the paradigm shift)
- Is an experimental result from experiments 51+ (these used graph substrate)
- Is a meta-document (000, 997, 998, 999, readme)

---

## Specific Guidance by Document Range

### RAW 001-015: Almost certainly `archive/`
Early framework. Discrete sufficiency, oscillation-convergence, temporal equations.
Written entirely in geometric framing. Check for anything that is purely logical/mathematical
(not geometry-dependent) before archiving.

### RAW 016-030: Likely `archive/`, some `review/`
Distance via Planck units (016), velocity (016-017), mass (019), black holes (020),
gravity (021-025), movement theory (023) — all geometric derivations → `archive/`.
Free will (024), horizon boundaries (026) — may survive → `review/`.

### RAW 031-050: Mixed — read each one
Energy constant (031), Planck cube ledger (032), persistence axioms (033) — `review/`.
Observer sleep (035), Big Bang (037), multiverse (038) — observer-relative, likely `raw/`.
XOR parity (039) — graph-compatible, `raw/`.
Dimension via latency (040) — explicitly graph-first, `raw/`.
Ternary XOR (041), temporal choice (042), void asymmetry (043) — `raw/`.
Fallible commit (044), rendering theory (045-046) — `raw/`.
Physical formalization (047), observer model (048) — `review/` (may have geometric remnants).

### RAW 051-070: Mostly `review/`
Photon (051), black holes (052), collision (053), elasticity (054) — written during
transition period. Check substrate assumptions in each.
Speed of light (055-056), propulsion (057), geodesic drive (058) — likely `review/`.
Pattern matching (060), matter-antimatter (061) — `review/`.
Interferometry (062), magnetism (063), electric fields (064-066) — `review/`.
Anti-gravity (067), time crystals (068), computational cost (069) — `review/`.

### RAW 070-107: Mostly `raw/` — written in graph/gamma-field era
Electron cloud (070), double-slit (071), jitter/ZPE (072-073) — `raw/`.
Ternary correction (074), time dilation (075), gamma field principles (076-083) — `raw/`.
Subcritical wells (084-085), EM unification (086-092) — `raw/`.
Curvature (092-099), hill ontology (100-103) — `raw/`.
Emission recoil (104), well/hill saturation (106-108) — `raw/`.

### RAW 108-113: All `raw/` — current graph-first frontier
These are the active documents. Do not move.

### Special files:
- `039_law_000_xor_parity_rule.tex` — duplicate of `039_0_law000_xor_parity_rule.md` → `archive/`
- `000_meta_critical_theory_development_log.md` — historical log, keep in `raw/`
- `996_constants_dictionary.tex` — `review/` (constants may have changed meaning)
- `997_meta_critical_theory_integrated_spec.md` — `raw/` (synthesis document)
- `998_references.md` — `raw/`
- `999_closure_improvement_plan.md` — `raw/`
- `readme.md` — update after moves, keep in `raw/`

---

## Required Outputs

### 1. Execute the moves
Create `docs/theory/archive/` and `docs/theory/review/` directories.
Move documents according to triage criteria above.
Do NOT delete anything.

### 2. Create `docs/theory/raw/README_PARADIGM_SHIFT.md`
A short document (1 page) explaining:
- What changed at RAW 108-111
- How to read archived documents (conclusions may be valid, substrate descriptions are not)
- Entry points for new readers: start with RAW 111 → 112 → 113

### 3. Create `docs/theory/archive/README.md`
Brief note: these documents used geometric substrate assumptions. The graph-first
framework supersedes the substrate descriptions but some conclusions remain valid.
List which archived documents have known-valid conclusions despite wrong substrate.

### 4. Create `docs/theory/review/README.md`
Brief note: these documents are transitional — written during or after the paradigm
shift but not yet audited for geometric remnants. Conclusions are probably valid.
Substrate language may need updating.

### 5. Update `docs/theory/raw/readme.md`
Reflect the new structure. List active documents in logical reading order.

---

## Constraints

- **Do not delete any document.** Move only.
- **Do not edit document content** during this task. Content updates are a separate task.
- **Do not move RAW 108-113.** These are the active frontier.
- **When uncertain, use `review/`** rather than `archive/`. It is safer to under-archive
  than to over-archive.
- **Preserve filenames exactly** — other documents cross-reference by filename.

---

## Definition of Done

- [ ] `archive/` directory exists with moved documents and README
- [ ] `review/` directory exists with moved documents and README  
- [ ] `raw/` contains only graph-first and substrate-independent documents
- [ ] `raw/README_PARADIGM_SHIFT.md` created
- [ ] `raw/readme.md` updated
- [ ] No documents deleted
- [ ] Summary report of what was moved where and why

---

*This task file can be deleted after completion.*
