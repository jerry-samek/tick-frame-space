# Experiment 118 v7: Natural Data Stream — The Hammer-and-Nail Test

## Purpose

v6 demonstrated that a typed event stream, filtered by a single root entity through
consumption-transformation-rejection, self-organizes into a hierarchical trie with
predictable properties: branching factor from filter selectivity, depth from token
address length, formation timescale logarithmic in depth, and roughly equal mass
distribution across depth levels.

**The problem:** v6 used designed tokens (4-position base-3 addresses). The branching
factor (3), depth (4), and entity count (121) were predetermined by the token
structure. The hierarchy emerged because the tokens were designed to produce a
hierarchy. This may be a genuine architectural result or it may be a hammer seeing
nails.

**v7 tests whether the result is robust by removing all three design choices:**
1. Tokens come from natural data, not a designed alphabet
2. The root entity has no pre-assigned spectrum — it learns from the stream
3. There is no fixed token address length — depth emerges from the data

If hierarchical structure still self-organizes from natural data with a learning
root, the result is robust. If it only works with designed tokens, v6 was a
demonstration of trie construction, not a theory of self-organizing systems.

---

## Design

### Data Sources

Feed raw bytes from real data files. Test at least THREE different sources to check
robustness across different statistical distributions:

**Source 1: English text (Zipf distribution)**
- Any novel from Project Gutenberg (plain UTF-8 text)
- Highly non-uniform: space ~18%, 'e' ~10%, 'z' ~0.07%
- Top 5 characters cover ~45% of bytes
- Prediction: very top-heavy hierarchy, root consumes most of the stream

**Source 2: DNA sequence (4-symbol, structured)**
- Any genome segment (FASTA format, just the ACGT lines)
- 4 characters, roughly equal frequency (~25% each) but with motifs/repeats
- Prediction: base-4-like branching, but depth determined by motif complexity

**Source 3: Binary data (high entropy)**
- A JPEG image, a compiled binary, or /dev/urandom output
- Near-uniform byte distribution (256 possible values)
- Prediction: wide branching (many first-level entities), shallow depth
  (not much hierarchical structure in random data)

Each source is fed byte-by-byte into the same filter mechanism. The mechanism
doesn't change — only the input stream changes.

### Learning Root (No Pre-Assigned Spectrum)

This is the critical change from v6.

The root entity starts with an **empty spectrum**. It doesn't know what it can
process. For the first LEARNING_WINDOW ticks, the root observes what arrives and
builds its spectrum from the most frequent bytes:

```
Phase 1 (learning): first LEARNING_WINDOW ticks
  - Count frequency of each byte in the stream
  - Do NOT consume or reject anything yet — just observe and grow the graph
  
Phase 2 (crystallization): at tick LEARNING_WINDOW
  - Root spectrum = the top N most frequent bytes
  - N is chosen so that the root's spectrum covers TARGET_COVERAGE fraction
    of the observed stream (e.g., TARGET_COVERAGE = 0.5 means the root learns
    to consume 50% of the stream)
  - Alternative: N is chosen as a fixed count (e.g., top 10 bytes)
  - TRY BOTH approaches and compare results

Phase 3 (filtering): tick LEARNING_WINDOW+1 onward
  - Normal v6 mechanism: root consumes known bytes, rejects unknown bytes
  - Rejected bytes are routed outward, seeds form, promote to entities
  - Each child entity learns its own spectrum from its incoming rejected stream
    using the same learning window mechanism
```

### Emergent Depth (No Fixed Address Length)

v6 tokens had 4 positions → depth was capped at 4. In v7, there are no token
positions. Each entity receives a byte stream (its parent's reject stream), learns
a spectrum, and rejects what it can't process. The rejected stream goes to the next
level. Depth continues until:

- A leaf entity's incoming stream is too sparse to form children (below
  PLANET_THRESHOLD rejections within a timeout), OR
- The rejected stream has too little structure (near-uniform, no learnable spectrum)

The depth is emergent. It might be 2 for random data. It might be 8 for English
text. The data decides.

### Entity Spectrum Learning

Every entity (not just the root) learns its spectrum:

```
when a new entity is created from seed:
  1. Start with empty spectrum
  2. Observe incoming stream for ENTITY_LEARNING_WINDOW ticks
  3. Set spectrum = top M most frequent bytes in observed stream
     where M is chosen to cover ~50% of incoming traffic
  4. Begin consuming/rejecting
```

This means each entity in the hierarchy specializes on the most common patterns
in its particular branch of the reject stream. No spectrum is ever assigned by the
experimenter.

---

## Parameters

```python
# Data source
DATA_FILE = "path/to/input.txt"        # natural data file

# Graph
N_NODES = 10000
SPHERE_R = 20.0
TARGET_K = 24

# Learning
LEARNING_WINDOW = 2000         # ticks to observe before crystallizing spectrum
TARGET_COVERAGE = 0.5          # fraction of incoming stream the entity learns to consume
ENTITY_LEARNING_WINDOW = 500   # learning window for child entities (shorter — less traffic)

# Formation
GROWTH_COST = 10               # absorptions to claim one new node
PLANET_THRESHOLD = 60          # rejections before seed -> entity
REJECTION_HOPS = 5             # hops outward per rejection
EXTEND_RATE = 0.01             # connector extension per hop
FORMATION_TIMEOUT = 10000      # if seed doesn't reach threshold in this many ticks, give up

# Runtime
TICKS = 100000                 # long enough for deep hierarchies to form
LOG_EVERY = 1000
MEASURE_EVERY = 500
```

---

## Key Measurements

### Per-run (one data source):
1. **Hierarchy depth** — how many levels formed
2. **Branching factor per level** — how many children per parent (may vary!)
3. **Mass distribution by depth** — total nodes per level (is it still ~equal?)
4. **Root spectrum** — what bytes did the root learn to consume?
5. **Root mass fraction** — what % of total mass is the root? (compare to v6's 23%)
6. **Formation timeline** — tick at which each depth level first appears
7. **Time ratio between levels** — does the ~3x slowdown from v6 generalize?

### Cross-run comparisons (all three data sources):
1. **Depth vs Shannon entropy** — does higher entropy input → deeper hierarchy?
2. **Root mass fraction vs input skewness** — does Zipf input → heavier root?
3. **Branching factor vs alphabet size** — DNA (4 symbols) vs text (26+) vs binary (256)
4. **Does the equal-mass-per-level property survive?** If yes for all sources → robust.
   If only for uniform input → artifact of uniformity.

### The killer test:
5. **Run the same mechanism on purely random bytes (uniform distribution over 0-255).**
   If it produces hierarchy → the mechanism creates structure from noise.
   If it produces a flat structure → the mechanism requires input structure to
   create spatial structure. Both results are informative and publishable.

---

## What's Carried Forward from v6

- Graph infrastructure (random geometric graph, connectors, extension)
- Entity growth mechanism (absorb → energy → claim neighbor node)
- Rejection routing (hop outward, extend connectors)
- Seed → entity promotion (threshold-based)
- Compound extension (length *= (1 + rate))
- Density-based routing (foreign deposits / connector length)

## What's New in v7

- **Data-driven stream** instead of random token generator
- **Learning-based spectrum** instead of assigned spectrum
- **Emergent depth** instead of fixed address length
- **Multiple data sources** for cross-comparison
- **Shannon entropy measurement** of each input stream

---

## Implementation Notes

### Reading the Data File

```python
def byte_stream(filepath):
    """Yield one byte at a time from a file."""
    with open(filepath, 'rb') as f:
        while True:
            byte = f.read(1)
            if not byte:
                # Loop back to start if file is shorter than TICKS
                f.seek(0)
                byte = f.read(1)
                if not byte:
                    return
            yield byte[0]  # integer 0-255
```

### Shannon Entropy of Input

```python
from collections import Counter
import math

def shannon_entropy(data_bytes):
    """Compute Shannon entropy in bits per byte."""
    counts = Counter(data_bytes)
    total = sum(counts.values())
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy
```

Measure this on the first 10000 bytes of each input file and record it.
Maximum possible: 8.0 bits/byte (uniform random over 256 values).
English text: ~4.5 bits/byte.
DNA: ~2.0 bits/byte.

### Data Sources — Where to Get Them

- **English text:** Download any plain text novel from https://www.gutenberg.org/
  Save as UTF-8 .txt file. Suggestion: use a long novel (>500KB) so the stream
  doesn't loop too often during 100k ticks.

- **DNA:** Download any genome FASTA file. Strip header lines (starting with >).
  Keep only lines containing A, C, G, T. Many sources available; any segment >100KB
  works.

- **Random bytes:** Generate with Python:
  ```python
  with open('random_bytes.bin', 'wb') as f:
      f.write(os.urandom(500000))
  ```

### Output

Same plot format as v6 but with additional panels:

- **Input stream histogram** — byte frequency distribution of the input data
- **Root spectrum** — which bytes the root learned (highlight on the histogram)
- **Depth vs time** — when each level first appeared
- **Cross-source comparison** (if running all three): depth, branching, mass distribution
  side by side

Save per-entity data:
- entity name, depth, parent, spectrum (list of bytes), mass (nodes), birth tick,
  distance from parent

Save as CSV for analysis.

---

## Success Criteria

### Minimum (v7 passes):
- Hierarchical structure forms from at least ONE natural data source
- Root entity learns a spectrum without assignment
- Depth > 1 (at least star + planets, not just a single blob)

### Strong (publishable result):
- Hierarchical structure forms from ALL THREE data sources
- Depth correlates with Shannon entropy across sources
- Root mass fraction correlates with input skewness
- The result is robust to parameter changes (LEARNING_WINDOW, TARGET_COVERAGE)

### Maximum (breakthrough):
- Equal-mass-per-depth property holds across data sources
- The mechanism produces hierarchy from RANDOM bytes (structure from noise)
- Branching factor is predictable from alphabet statistics

---

## What This Tests

This is the **hammer-and-nail test** for the stream-filtering model.

If it works: the self-organizing hierarchical structure is a genuine property of
consumption-transformation-rejection filtering, independent of input design.
Publishable as a CS result: "Adaptive Self-Organizing Stream Classifier with
Hierarchical Rejection Routing."

If it fails: the v6 result was an artifact of designed tokens, and the model
needs fundamental revision before it can claim to produce spatial structure from
event streams.

Either result is valuable. Only one is exciting.

---

*Date: March 22, 2026*
*Depends on: v6 (Token-Addressed Routing), RAW 118 (Consumption-Transformation)*
*Tests: Robustness of hierarchical self-organization across natural data sources*
