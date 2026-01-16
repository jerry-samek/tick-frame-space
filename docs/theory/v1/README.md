# Theory Documentation v1 Archive

**Status**: ARCHIVED (2026-01-15)
**Current Version**: See `docs/theory/` for v2 consolidated chapters

---

## About This Archive

This directory contains the **chronological development history** of tick-frame physics theory (v1), comprising 76 documents written between the project's inception and January 2026. These documents represent the iterative, exploratory process of theory development, including early concepts, experimental designs, and theoretical refinements.

**This archive is preserved for:**
- Historical reference and development traceability
- Detailed derivations and proofs
- Understanding the evolution of key concepts
- Accessing specific experimental designs and raw data

**For current theory, see**: `docs/theory/` (v2 consolidated chapters)

---

## V1 → V2 Transition

### Why Consolidate?

**V1 Characteristics:**
- 76 documents (chronological order)
- Theory evolved from Doc 15 (Chapter 15 model) → Doc 49 (Temporal Ontology)
- Some contradictions between early and late documents
- Hard to navigate for new readers
- Experimental validations scattered

**V2 Improvements:**
- 8 cohesive chapters (topic-based organization)
- Contradictions resolved with explicit gap documentation
- Validated vs speculative content clearly separated
- Integrated experimental evidence
- Clear reading order for new readers

### What Changed?

**Content**: Nothing lost, everything consolidated or preserved
- Critical docs preserved as references (15, 49, 50_01, 46_01)
- Experimental validations integrated into chapters
- Early speculative content archived here
- Falsifications documented prominently

**Structure**: Chronological → Topical
- V1: Doc 01 → Doc 51 (development timeline)
- V2: 8 chapters by theme (ontology, dimensions, entities, etc.)

---

## Critical V1 Documents Preserved as References

These documents are so important they remain accessible at `docs/theory/` root:

### REFERENCE_doc15_minimal_model.md
- **Original**: v1/15 Minimal Model Recommendation
- **Why preserved**: BASIS FOR JAVA IMPLEMENTATION
- **Status**: IMPLEMENTED in tick-space-runner
- **Note**: Java uses Chapter 15 model; Doc 49 (Temporal Ontology) is theoretical target

### REFERENCE_doc49_temporal_ontology.md
- **Original**: v1/49 Temporal Ontology of the Tick-Frame Universe
- **Why preserved**: THEORETICAL FOUNDATION (constitution of tick-frame physics)
- **Status**: Cited extensively in v2 Ch1
- **Key principle**: Time is primary substrate, space is emergent

### REFERENCE_doc50_01_dimensional_equivalence_rejection.md
- **Original**: v1/50_01 Experimental Results
- **Why preserved**: SMOKING GUN EVIDENCE
- **Key finding**: ρ=2.0 signature (time ≠ dimension)
- **Validation**: 1,095 configurations tested, 0/6 tests passed
- **Convergent**: Experiment 44 (rotation asymmetry) + Experiment 50 (ρ=2.0) confirm same constraint

### REFERENCE_doc46_01_bucketing_validation.md
- **Original**: v1/46_01 Experimental Validation
- **Why preserved**: RENDERING VALIDATION
- **Key finding**: O(n) complexity confirmed (2.78× speedup @ 100k entities)
- **Validates**: Temporal bucketing theory (Doc 46)

---

## Experimental Validations Summary

### Experiment #15 (v6-gpu, v7-final) - 3,960 simulations
- **3D is optimal** (Goldilocks zone), not exclusive
- ρ=2.0 phase transition @ d=3
- Dimensional scaling laws discovered
- **See v2 Ch2**

### Experiment #44 Series - Lag-based rendering
- **Rotation asymmetry: 933×** (forward 0%, backward 93%)
- Temporal velocity constraint: v ≤ 1 tick/tick
- **See v2 Ch6**

### Experiment #50 - Dimensional equivalence
- **0/6 tests passed** (hypothesis rejected)
- **ρ=2.0 SIGNATURE** discovered (smoking gun)
- Time is special generator, not dimension
- **See v2 Ch1, REFERENCE_doc50_01**

---

## How to Use This Archive

### For New Readers
**Don't start here!** Read v2 consolidated chapters first:
1. `docs/theory/README.md` (v2 overview)
2. `docs/theory/REFERENCE_doc49_temporal_ontology.md` (constitution)
3. `docs/theory/v2_ch01_temporal_ontology.md` (foundations)
4. Then consult v1 for detailed derivations

### For Researchers
**Use v1 for:**
- Tracing concept evolution (Doc 15 → Doc 49)
- Accessing detailed proofs
- Understanding experimental methodology
- Finding specific calculations or diagrams

### For Implementers
**Key v1 docs for Java codebase:**
- **v1/15**: Minimal Model (current Java basis)
- **v1/28**: Temporal Surfing
- **v1/29**: Imbalance Theory
- **v1/30**: Collision Persistence

---

## V2 Chapter Structure (Current)

1. **Ch1**: Temporal Ontology
2. **Ch2**: Dimensional Framework
3. **Ch3**: Entity Dynamics
4. **Ch4**: Observer & Consciousness
5. **Ch5**: Free Will & Ternary Logic
6. **Ch6**: Rendering Theory
7. **Ch7**: Physical Formalization
8. **Ch8**: Integration & Falsification

**Plus 4 reference documents** (critical v1 docs preserved)

---

## Complete V1 Document List

See files in this directory:
- **00-14**: Foundational principles and meta-theory
- **15-series**: Experimental framework (Chapter 15 model - IMPLEMENTED)
- **16-25**: Physical quantities (velocity, mass, gravity, etc.)
- **26-30**: Collision & persistence trilogy (IMPLEMENTED)
- **31-34**: Energy & conservation
- **35-38**: Observer cosmology
- **39-43**: Ternary logic & dimensions
- **44-44_01**: Free will & consciousness
- **45-46**: Rendering theory (VALIDATED)
- **47-48**: Physical formalization
- **49**: Temporal Ontology (CURRENT FOUNDATION)
- **50-50_01**: Dimensional equivalence test (SMOKING GUN)
- **51**: Photon theory
- **96-99**: Meta-documents, references, improvement plans

**Total**: 76 documents

---

**Archive Created**: 2026-01-15
**v2 Consolidation**: In progress
**Questions?**: See `docs/theory/README.md`
