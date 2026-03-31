# Trie Stream Filtering

## Origin

These experiments (v4-v10) originated within Experiment 118 (Consumption-Transformation
Gravity) but diverged from the gravitational binding question into stream filtering,
hierarchical self-organization, and trie-based memory. They validate **RAW 123** (The
Stream and the Trie) rather than RAW 118 (Gravity as Consumption-Transformation).

Separated from Experiment 118 on March 31, 2026 to keep the gravity experiment focused
on its original orbital mechanics goal.

## Theory Documents

- **RAW 123** — The Stream, the Trie, and What the Data Tells Us
- **RAW 113** — The Semantic Isomorphism: Same / Different / Unknown
- **RAW 118** — Gravity as Consumption and Transformation (origin mechanism)

## Version History

| Version | Name | Key Idea | Key Result |
|---------|------|----------|------------|
| v4 | Producer-consumer | Seed accepts known types, rejects unknown | First consume/reject filtering |
| v5 | Recursive filtering | Same algorithm at all levels, hierarchy emerges | Recursive self-similarity |
| v6 | Token-addressed routing | K-element tokens, decision trie | Designed tokens -> designed depth (trie by construction) |
| **v7** | **N-gram stream filtering** | **Raw bytes, learned spectra, N=1,2,4,8** | **Mechanism discovers sequential structure: consumed depth increases with N for English, collapses for random** |
| **v8** | **Causal window** | **learning_window = max(1, birth_tick)** | **Inverted hierarchy: deeper entities learn better. Spectrum coverage improves with depth** |
| **v9** | **Video decomposition** | **Frame diffs as byte stream** | **Root learns "no change" (byte 128). Hierarchy separates static/motion/noise without being told** |
| **v10** | **Store and reconstruct** | **Consumption logging + agent traversal** | **100% lossless pixel recovery at 26.3 dB PSNR. Trie is a functional reversible memory** |

## Key Findings

1. **The mechanism discovers sequential structure (v7)** — discriminates structured from
   random data without being told what structure looks like
2. **The causal window inverts the hierarchy (v8)** — deeper entities learn better,
   matching "heavy elements form later" pattern
3. **Video temporal structure discovery (v9)** — root learns "no change", children handle
   motion, rediscovers video compression principles
4. **The trie is a reversible memory (v10)** — 100% lossless reconstruction, progressive
   retrieval by depth
5. **Progressive retrieval is the killer feature (v10)** — stop at any depth for partial
   answer (22% -> 45% -> 71% -> 84% -> 93% -> 100%)
6. **The trie does not compress (v10)** — 4.6x expansion, trades compactness for
   hierarchical queryability

## Status

**Complete.** The arc from v4 (first filtering) to v10 (lossless memory) is closed.

---

*Date: March 21-22, 2026 (experiments), March 31, 2026 (separated from Experiment 118)*
*Author: Tom (theory), Claude (experiment design and implementation)*
