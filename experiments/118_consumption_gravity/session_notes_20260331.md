# Session Notes — March 31, 2026 (evening)

## Context
Continuation of "Vortex theory for measurable lift generation" discussion,
focused on Experiment 118 v4 orbital mechanics.

## Key Theoretical Corrections Made Tonight

### 1. Append-only applies to connectors, deposits are consumable-by-transformation
- Connector = road (permanent, append-only)
- Deposits = cargo (travels on road, consumed by capacitor discharge)
- Consumption = transformation (Different → Same), not subtraction
- Arrived at: deposits QUEUE at nodes when capacitor is busy (option B)

### 2. Connectors don't grow from deposits
- Deposits TRAVEL on connectors (push-driven, 1 hop/tick)
- Deposits don't EXTEND connectors — that makes everything a light sail
- Connector length is fixed at graph construction
- What grows connectors: only Unknown events at frontier (not applicable
  in bounded gravitational system)
- This invalidates v4's "connector length = deposit count" equation

### 3. The connector as production-consumption buffer
- Star leaks Different quanta onto connectors (radiation)
- Quanta propagate to planet
- Planet consumes (transforms) what it can, rest queues
- Orbital distance = where consumption rate matches production rate
- Eccentricity = consumption capacity vs flux mismatch
- Comets: small capacity → buffer overflow at perihelion → long aphelion
  processing time → high eccentricity

### 4. The orbit is a graph cycle, not a spatial curve
- No inherent geometry — connectors are relations, not roads in space
- "Outward" doesn't exist in the graph — only routing choices
- Planet routes AWAY from saturated connectors (not "pushed outward")
- The ellipse is a projection of a graph-topological cycle

### 5. Star radiation emerges from append-only preventing perfect Same
- Internal traffic → connectors grow → density drops → capacitor
  charging slows → more idle ticks → more Different state → more leakage
- This IS gravitational time dilation (core slows down from its own mass)
- Luminosity should be derivable from node count and connectivity alone
- Potential "first clean derived number"

## Documents Produced
- `experiments/118_consumption_gravity/v4/README.md` — spec for Code
  (uses the connector-extension model — now known to be partially wrong)
- `experiments/118_consumption_gravity/v5/README.md` — corrected spec
  (fixed graph, deposit propagation, queue mechanics)
- `experiments/trie_stream_filtering/experiment_description.md` — already
  existed, confirmed separation of trie experiments from gravity line

---

## v4 Phase 1 Results (from Code, same evening)

### What WORKED — the extension bug is dead
- Internal connectors grow LINEARLY: mean ~80, max ~97 at 50k ticks
- Compare v1: connectors reached 1e28+. The append-only deposit-count
  model completely eliminates runaway compound growth.
- Star is alive — nodes actually moving, not frozen
- Mean radius fluctuates between 13.5–15.5 (real dynamics)
- Radius stability: CV=0.028 over last 20k ticks (well within 15% threshold)
- Radiation accumulating on boundary connectors — star leaks outward

### What FAILED
- **COM drift: 3.27 (max 3.64) — exceeds the <2.0 threshold.** Star
  wanders via random walk. Drift scales as ~sqrt(ticks). Expected for
  80 nodes doing weighted random walks.
- **Star expanded: initial radius 3.84 → final ~14.5.** Star puffed up.
  Routing signal (1 + recent_other_group) is too weak vs base exploration
  weight (1). Only 2:1 preference for signal-rich connectors. Nodes
  mostly random-walk → dispersal.

### Interpretation
Code asked whether to add a signal-strength parameter (α) to fix the
weak routing. **Answer: NO. Don't add parameters.**

The weak signal is telling us the v4 mechanism doesn't produce tight
gravitational binding on its own. This is expected — v4's deposit-count
model is wrong (deposits extend connectors = light sail problem). The
v5 correction (fixed-graph, deposit propagation, spatial accumulation
from multiple neighbors) should naturally produce stronger routing
signals without added parameters: a node with 6 star neighbors receives
6× the deposit flux, giving much stronger center-preference.

### v4 Phase 1 Verdict
- **Core extension bug: SOLVED** ✅
- **Star alive with real dynamics: YES** ✅
- **Star self-binding: WEAK** ⚠️ (star expands 4× from initial radius)
- **Star radiation: EXISTS** ✅ (boundary deposits accumulate)
- **Proceed to Phase 2 (planet)?** Could try, but the weak binding
  suggests the star's field won't produce strong enough attraction.
  v5 likely needed.

---

## The Unresolved Problem: Stream Origin

The session's deepest open question, raised at the very end:

**The consumption mechanism requires a structured stream to produce
hierarchical structure.** The trie_stream_filtering v7 experiment showed
that random input produces no meaningful hierarchy. But the most principled
stream source (XOR/NAND on the graph itself, RAW 039) produces
pseudo-random output.

This creates a potential falsification:
- If the only stream that produces gravity is a DESIGNED stream → the
  framework is a simulation tool, not physics
- If graph TOPOLOGY creates structure in the XOR stream (dense regions →
  correlated outputs → proto-Same) → the framework self-bootstraps
- This is testable: run XOR on a random geometric graph, measure entropy
  of output near dense center vs sparse boundary

**This is the most important open question in the framework right now.**
More important than orbital mechanics. If the stream must be designed,
everything downstream is fitting, not derivation.

Counterargument (noted at session end): "no structure in random stream"
might not be a problem — it might be the answer. If the universe HAS
structure, and the mechanism only produces structure from structured
input, then the stream ISN'T random. The existence of structure is
evidence of a structured source. The question becomes: what IS the
structure, and can we identify it?

---

## Next Session Priorities

### 1. Evaluate v4 fully
- Check if Code ran Phase 2 (planet introduction)
- Review all v4 plots and data
- Document whether v4's weak binding is fundamental or tunable

### 2. Decide: v5 implementation or v4 iteration?
- If v4 Phase 2 shows any radial binding despite weak signal → iterate v4
- If v4 Phase 2 fails completely → move to v5 (fixed-graph model)
- The v5 spec is ready at `experiments/118_consumption_gravity/v5/README.md`

### 3. The stream origin experiment
- Design a minimal test: XOR rule (RAW 039) on random geometric graph
- Measure: is the output entropy lower near dense clusters than near
  sparse boundary?
- If yes → topology creates structure → framework can self-bootstrap
- If no → stream must be externally structured → fundamental limitation
- This could be a small standalone experiment (Experiment 119?)

### 4. Revisit the "one clean derived number" criterion
- v4 Phase 1 data has a measurable boundary deposit flux (star luminosity)
- Can this flux be predicted from: node count (80), connectivity (k≈24),
  and the routing rule alone?
- If luminosity = f(N_star, k) with no free parameters → first derived
  number
- Compare: does the predicted luminosity match the measured boundary
  deposit rate?

---

## Session Statistics
- Duration: ~2 hours (19:38 – 21:40 CET)
- Messages: 8 exchanges
- Theory documents read: RAW 113, 126, 127, 039
- Experiment code read: v3/phase1_equilibrium.py, trie_stream_filtering/v4
- Key insight: deposits travel on connectors, they don't extend them
- Key concern: stream origin as potential falsification
- Mood: productive but ended on the hardest possible question
