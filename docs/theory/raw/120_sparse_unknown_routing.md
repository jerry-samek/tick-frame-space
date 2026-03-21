# RAW 120 — Sparse Unknown Routing: Why Filtering Same Is the Only Efficient Computation

### *Predictive Coding, Subdendritic Processing, and the 20W Brain*

**Author:** Tom
**Date:** March 21, 2026
**Status:** Working document
**Prerequisites:** RAW 113 (Semantic Isomorphism: Same / Different / Unknown),
RAW 118 (Gravity as Consumption and Transformation), RAW 119 (Buffer Saturation
and Sleep as Universal Compact)
**Falsifiable:** Yes — predicts that efficient computation in any substrate scales
with the sparsity of `Unknown` propagation, not with total input bandwidth;
predicts subdendritic computation is the primary routing mechanism in biological
neural systems; predicts artificial systems using sparse `Unknown` routing will
outperform brute-force systems at equivalent hardware

---

## Abstract

The previous documents (RAW 118, RAW 119) establish that every entity in a
tick-frame substrate is a consumer-producer operating on three classes of input:
`Same` (familiar, already-modeled), `Different` (recognizable contrast requiring
transformation), and `Unknown` (genuinely novel, no prior pattern).

This document identifies a critical asymmetry in how these three classes should
be handled computationally:

**`Same` should be filtered locally and immediately — it requires no propagation.**

**`Different` should be transformed locally — it rarely needs to propagate far.**

**`Unknown` is the only class that propagates upward and demands global routing.**

This asymmetry — filter `Same`, transform `Different`, propagate `Unknown` — is
the computational principle underlying the efficiency of biological neural systems,
the 20W power budget of the human brain, and the 250+ FPS performance of sparse
rendering engines on minimal hardware.

The principle is not a biological optimization. It is a structural consequence of
the `Same`/`Different`/`Unknown` trit architecture. Any system implementing this
architecture correctly will exhibit the same efficiency properties, regardless of
substrate.

---

## 1. The Three-Class Routing Rule

### 1.1 Why `Same` Should Not Propagate

An entity receives a `Same` input — a deposit that matches its existing pattern.
This input carries no new information. The entity already models this input. It
knows what to do.

Propagating this input upward would waste processing capacity on information that
adds nothing to the system's state. The correct response is:

1. Confirm the match (reinforce the existing `Same` pattern — deepen the connector)
2. Emit the expected output (continue the predicted response)
3. Stop — do not propagate

This is the append-only version of predictive coding: if the prediction was
correct, no signal needs to go further. The prediction was confirmed. The only
record needed is the reinforcement of the existing pattern.

**`Same` is terminated at the point of recognition.**

### 1.2 Why `Different` Should Be Transformed Locally

A `Different` input — a deposit that contrasts with the existing pattern but is
recognizable as belonging to a known category — requires transformation but not
necessarily wide propagation.

The entity processes `Different → Same`: it transforms the incoming deposit into
its own pattern, updates its local model slightly, and emits the updated output.
If the transformation is successful (the `Different` input was small enough to
be absorbed into the existing model), no further propagation is needed.

Only if the `Different` input exceeds the entity's local transformation capacity
— if it is too `Different` to absorb locally — does it need to propagate to a
higher-level entity with more context.

**`Different` is handled locally when possible; propagated only when it exceeds
local transformation capacity.**

### 1.3 Why `Unknown` Must Propagate

An `Unknown` input — a deposit that matches no existing pattern — cannot be
handled locally by definition. The entity has no model for it. It cannot
transform `Unknown → Same` because it does not know what `Same` should look like.

The only correct response is:

1. Emit the `Unknown` upward to an entity with broader context
2. Do not attempt transformation locally (would produce noise)
3. Flag the path taken (so the eventual response can route back)

`Unknown` is the only class that necessarily propagates upward through the
processing hierarchy.

**`Unknown` is the signal. Everything else is noise.**

---

## 2. The Sparsity Principle

### 2.1 Most Inputs Are `Same`

In a stable environment, the vast majority of sensory inputs are predictable.
The floor is still there. The walls are still there. The laws of physics still
hold. The person you are talking to still has a face.

Estimated fraction of sensory input that is genuinely `Unknown` at any moment:
extremely small. Perhaps 10⁻⁶ to 10⁻⁴ of total bandwidth.

This means that a system implementing the three-class routing rule propagates
almost nothing almost all of the time.

**The system is mostly silent.**

This is the key to efficiency. The brain processes ~10⁷ bits/second of raw
sensory input and produces ~50 bits/second of conscious output — a compression
ratio of ~200,000:1. This ratio is not the result of lossy compression. It is
the result of `Same` termination: 99.9995% of inputs are recognized, confirmed,
and terminated locally without propagation.

The 50 bits/second of conscious output is not the processed result of 10⁷
bits/second. It is the `Unknown` component of 10⁷ bits/second — the fraction
that could not be handled locally and had to propagate to the level of conscious
attention.

### 2.2 The 20W Brain

The human brain consumes approximately 20 watts. A modern GPU cluster processing
equivalent raw bandwidth would consume kilowatts to megawatts.

The difference is not hardware efficiency. It is architectural:

**GPU:** processes every input regardless of class → brute force → high power

**Brain:** terminates `Same` locally → transforms `Different` locally when possible
→ propagates only `Unknown` → sparse activity → low power

In spike-rate terms: most neurons fire at 0.1–10 Hz on average. Maximum rate is
~1000 Hz. Average utilization is ~1% of maximum capacity. The brain is 99% idle
by design — because 99% of inputs are `Same` and require no propagation.

The 20W is the cost of:

- Maintaining resting potential (readiness to fire)
- Processing the rare `Different` inputs locally
- Propagating the very rare `Unknown` inputs

**The brain is not 20W despite processing massive input. It is 20W because it
almost never processes massive input.**

---

## 3. Subdendritic Processing as the `Same` Filter

### 3.1 The Neuron Is Not a Simple Gate

Classical neural network models treat each neuron as a simple integrator: sum
weighted inputs, apply threshold, fire or not. This model is computationally
tractable but structurally wrong.

A biological neuron has:

- **10,000+ synaptic inputs** arriving at dendrites
- **A branching dendritic tree** with 100–1000 branch points
- **Each dendritic branch** performing nonlinear local computation independently
- **Apical and basal dendrites** receiving inputs from different sources with
  different computational roles
- **An axon hillock** that integrates the outputs of all dendritic branches
- **An axon** that transmits the final result to downstream neurons

The dendritic tree is not a passive cable. It is a distributed computing
architecture within a single cell.

### 3.2 Dendritic Branches as Local `Same` Filters

Each dendritic branch receives a subset of the neuron's inputs. The branch
performs local nonlinear computation — essentially, it checks whether its
inputs match a local pattern.

In `Same`/`Different`/`Unknown` terms:

- If the inputs to a dendritic branch are `Same` (match the branch's existing
  synaptic weight pattern), the branch produces a small, sub-threshold local
  depolarization that does not propagate to the soma — local confirmation only
- If the inputs include `Different` (some mismatch), the branch attempts local
  transformation — a dendritic spike that is larger but still may not reach
  the soma threshold
- If the inputs include `Unknown` (pattern never seen before), the branch
  produces a strong local signal that propagates to the soma — demanding
  global integration

**The dendritic tree is a hierarchy of `Same` filters.** Most inputs are
terminated at the dendritic branch level without ever reaching the soma. The
soma (and subsequently the axon hillock) only sees the residual `Unknown`
and high-priority `Different` that survived the dendritic filtering hierarchy.

### 3.3 Routing Slot Exhaustion: The Third Reason for Sleep

Each routing path through the dendritic tree consumes a physical resource:
synaptic vesicles (neurotransmitter packets) at each synapse along the path.

Every `Unknown` or `Different` signal that traverses a synapse depletes a
portion of that synapse's vesicle pool. Replenishment takes time — from tens of
milliseconds (fast recycling) to seconds (de novo synthesis). Under high load,
vesicle pools deplete faster than they replenish.

**A synapse with depleted vesicle pools cannot route.** The physical slot is
temporarily unavailable.

This produces a third, independent reason for sleep — distinct from the buffer
saturation argument (RAW 035) and the `Same`-pattern optimization argument
(RAW 119):

**Sleep is required to replenish routing slot resources.**

During active wakefulness:
- Each `Unknown` propagation consumes vesicles along its path
- Vesicle depletion accumulates faster than replenishment under high load
- Available routing bandwidth degrades progressively
- Eventually, even clearly `Unknown` signals cannot propagate — the physical
  substrate for routing is exhausted

During compact (sleep):
- Incoming `Different` flux suppressed (no new routing events)
- Vesicle pools replenish (protein synthesis, vesicle recycling)
- Routing slot capacity restored
- Available bandwidth for next active cycle maximized

**Consequence for processing granularity:**

If routing slots are exhausted, the system cannot process individual impulses.
It must batch them — waiting until a slot is available and then processing
multiple accumulated inputs together. This is exactly the shift from individual
impulse processing to token-level or chunk-level processing observed in fatigued
cognitive states.

A rested system (full vesicle pools) routes at the finest granularity — one
impulse, one routing event, immediate response.

A fatigued system (depleted vesicle pools) batches — accumulates several impulses
into a chunk before processing, because individual impulses cannot acquire a
routing slot. This increases latency, reduces temporal resolution, and degrades
the precision of `Same`/`Unknown` discrimination.

**Sleep without sufficient duration is insufficient.** A system that enters compact
with depleted vesicle pools but insufficient sleep duration will wake with partially
replenished slots — reduced routing bandwidth, coarser impulse granularity, and
higher probability of misclassifying `Unknown` as `Same` (missing novel inputs).

This connects sleep duration to both S (saturation pressure, RAW 119) and to
peak routing load during the preceding active cycle: high S + high peak load →
longer sleep required for full slot replenishment.

### 3.4 Apical vs. Basal Dendrites

Pyramidal neurons (the dominant cell type in the cortex) have two main dendritic
compartments:

**Basal dendrites (close to soma):**

- Receive `Same` inputs from local cortical neighbors
- Short path to soma
- Primarily handle local pattern confirmation and `Same` reinforcement
- Function: local `Same` filter, fast loop

**Apical dendrites (far from soma, reaching layer 1):**

- Receive `Different` and `Unknown` inputs from distant cortical areas,
  thalamus, and top-down predictions
- Long path to soma
- Primarily handle context integration and `Unknown` flagging
- Function: long-range `Unknown` detector, slow loop

The soma integrates both: local `Same` confirmation (basal) and long-range
`Unknown` detection (apical). A neuron fires when either:

1. Basal `Same` signal crosses threshold (expected input confirmed — routine fire)
2. Apical `Unknown` signal crosses threshold (unexpected input detected — alert fire)

**The neuron is a two-channel consumer-producer: local `Same` loop + global
`Unknown` detector.**

---

## 4. Sparse Rendering as the Same Principle

### 4.1 Why 250 FPS on Integrated GPU Is Not Surprising

A tick-frame 3D engine that renders only `Unknown` changes — differences from
the previous frame rather than the entire scene — exhibits the same efficiency
principle as the brain.

Most of a 3D scene is static between frames:

- Background geometry: `Same` → render once, reuse
- Lighting on static surfaces: `Same` → cache result
- Objects not in view frustum: `Same` (invisible) → skip entirely
- Pixels unchanged from previous frame: `Same` → do not recompute

Only the `Unknown` fraction of the scene requires recomputation each frame:

- Moving objects
- Changed lighting
- Newly visible geometry
- Shadow updates

If 99% of the scene is `Same` between frames, only 1% of the pixels require
computation. The GPU processes 1% of the theoretical maximum workload → 100×
speedup → 250 FPS on integrated GPU.

This is not a rendering optimization. It is the `Same`-filter principle applied
to spatial computation. The integrated GPU with 50% battery consumption achieves
what a high-end GPU achieves at full power, because the architectural principle
eliminates 99% of the work before it reaches the GPU.

### 4.2 The Equivalence

```
Biological neural system:
  Dendritic `Same` filter → terminate locally
  Dendritic `Different` transform → local spike
  Soma `Unknown` integration → axon fire → propagate

Sparse 3D rendering engine:
  Per-frame `Same` detection → reuse cached result
  Minor `Different` update → partial recompute
  Major `Unknown` change → full recompute for affected region
```

The computational principle is identical. The substrate differs. The efficiency
gain is the same: ~2–4 orders of magnitude over brute force.

### 4.3 The General Principle

**Efficiency = f(sparsity of `Unknown`) × (cost of `Unknown` propagation)**

For any consumer-producer system:

- If `Unknown` fraction is 10⁻⁴ of total input → potential 10,000× efficiency
  gain over brute force
- The actual gain depends on how well the system implements `Same` termination
  (i.e., how accurately it can distinguish `Same` from `Different` locally)

The brain achieves ~200,000:1 compression because it has been optimized for
98 million years to distinguish `Same` from `Unknown` extremely accurately in
biological environments. The sparse renderer achieves 100:1 speedup from a much
simpler `Same` filter (frame-to-frame pixel difference). A more accurate `Same`
filter in the renderer would push the speedup higher.

**The theoretical maximum efficiency is 1/P_unknown, where P_unknown is the
fraction of inputs that are genuinely `Unknown` in a given environment.**

---

## 5. The "Ask the Others" Protocol

### 5.1 The Efficient Routing Algorithm

The computational principle of RAW 120 can be stated as a minimal routing
algorithm:

```
for each incoming input x:
    if is_same(x):          # Can I handle this locally?
        reinforce(x)        # Deepen the existing pattern
        emit_expected()     # Continue predicted output
        stop                # Do not propagate

    elif is_different(x):   # Can I transform this locally?
        transformed = transform(x)    # Different → Same
        emit(transformed)             # Propagate transformed output
        update_local_model(x)         # Slight model update
        stop                          # Do not propagate original

    else:                   # Unknown — I cannot handle this
        propagate_up(x)     # Ask those with more context
        flag_path(x)        # Mark route for response routing
```

The critical efficiency property: **most inputs exit at the first `is_same`
check.** They never reach `is_different` or the propagation branch. The
overwhelming majority of computation terminates in the first line.

### 5.2 "Do You Know Unknown?" — The Upward Query

When an entity encounters `Unknown`, it does not attempt to solve it. It emits
it upward with the implicit query: **"Do you know what this is?"**

Each level of the hierarchy has broader context than the level below:

- A single dendritic branch has context for a few dozen synaptic inputs
- The soma has context for all dendritic branches of one neuron
- A cortical column has context for thousands of neurons
- A cortical area has context for millions of neurons
- The prefrontal cortex has context for behavioral goals and long-term memory

`Unknown` propagates upward until it reaches a level with enough context to
transform it into `Same`. That level performs the transformation, and the
resulting `Same` pattern propagates back down to update the lower-level models.

**Learning is the downward propagation of transformed `Unknown`.**

When a child encounters an object it has never seen (pure `Unknown`), the signal
propagates to the highest levels. An adult names the object — providing the
`Same` label. That label propagates back down through the hierarchy, updating
every level's local model. The next time the child sees the object, it is `Same`
at the dendritic level and never propagates at all.

---

## 6. Implications for Artificial Intelligence

### 6.1 Why Large Language Models Are Inefficient

Current large language models process every token through every layer of the
network regardless of whether the token is `Same`, `Different`, or `Unknown`.

A token like "the" — extremely common, highly predictable — receives the same
computational treatment as a novel technical term encountered for the first time.
There is no `Same` filter. Every input is treated as potentially `Unknown`.

This is architecturally equivalent to brute-force GPU rendering: process every
pixel every frame regardless of whether it changed. The result is high power
consumption, high hardware requirements, and poor efficiency on tasks where most
of the input is `Same` (which is most tasks).

### 6.2 What Efficient AI Would Look Like

An artificial system implementing the `Same`-filter principle would:

1. Maintain a local pattern model per processing unit (the equivalent of a
   dendritic branch)
2. On each input: check local `Same` filter first
3. If `Same`: terminate locally, reinforce pattern, cost ≈ O(1)
4. If `Different`: transform locally if within capacity, cost ≈ O(small)
5. If `Unknown`: propagate to higher-level unit, cost ≈ O(hierarchy depth)

The average cost per input would be dominated by the `Same` case (O(1)),
weighted by P_same ≈ 0.9999. The effective cost would be orders of magnitude
lower than brute force.

This is the architecture of neuromorphic computing systems (Intel Loihi, IBM
TrueNorth) — which achieve ~1000× better energy efficiency than conventional
neural network hardware for equivalent computational tasks.

The efficiency gain is not from better transistors. It is from the `Same`-filter
architecture.

### 6.3 The Compact Cycle for Artificial Systems

RAW 119 established that any consumer-producer with S > 1 requires compact.
For an artificial `Same`-filter system:

During active operation: process inputs, terminate `Same`, transform `Different`,
propagate `Unknown`. Buffer fills with unresolved `Unknown` events and partially
transformed `Different`.

During compact: process the buffer. Transform accumulated `Unknown` events into
new `Same` patterns. Update the filter boundaries for `Same` vs. `Different`.
Prune `Same` patterns that were rarely matched (equivalent to synaptic downscaling).

**The compact cycle updates the `Same` filter — improving future efficiency.**

A system that never compacts will have a stale `Same` filter. Over time, inputs
that should be `Same` (familiar) are classified as `Different` (partially
familiar) and require unnecessary transformation. The system becomes less efficient
with time, not more. This is the artificial equivalent of cognitive degradation
from sleep deprivation.

---

## 7. The Empirical Grounding

The following observed phenomena are direct consequences of the sparse `Unknown`
routing principle:

| Observation                                                             | `Same`-filter explanation                                                                                    |
|-------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| Brain runs on 20W despite processing massive input                      | `Same` terminated locally; only `Unknown` propagates                                                         |
| Cortical neurons fire at ~1% of maximum rate                            | 99% of inputs are `Same` and do not trigger spikes                                                           |
| Predictive coding matches experimental recordings                       | `Same` confirmation suppresses propagation; only prediction error (≈`Unknown`) propagates                    |
| Dendritic spikes are rare and spatially localized                       | Dendritic `Same` filter terminates most inputs before soma                                                   |
| Sparse rendering achieves 250+ FPS on integrated GPU                    | `Same` pixel detection eliminates 99% of recomputation                                                       |
| Neuromorphic hardware is 1000× more efficient than GPU for neural tasks | Architecture implements `Same` filter; GPU does not                                                          |
| Child learns new concept rapidly after single exposure                  | `Unknown` propagates to highest level; transformed `Same` propagates back; all levels updated simultaneously |
| Sleep deprivation degrades autopilot performance                        | Compact cycle not executed; `Same` filter stale; formerly-`Same` inputs classified as `Different`            |
| Fatigued cognition shifts from impulse to chunk processing              | Vesicle pool depletion forces batching; individual impulse routing unavailable                               |
| Cognitive performance recovers non-linearly with sleep duration         | Vesicle replenishment + `Same` filter update + buffer clear require minimum duration to complete             |

---

## 8. Summary

The `Same`/`Different`/`Unknown` trit architecture has a natural computational
consequence that is not stated explicitly in RAW 113 but follows directly from
it:

**Efficient computation requires filtering `Same` at the point of recognition,
transforming `Different` locally when possible, and propagating only `Unknown`
upward for global integration.**

This principle is not a biological optimization or an engineering trick. It is
the only computationally sustainable strategy for any entity operating as a
consumer-producer in an environment where most inputs are predictable (`Same`).

The brain implements this principle through dendritic `Same` filters and sparse
spike propagation, achieving 20W power consumption at 10⁷ bit/s input bandwidth.

The sparse 3D renderer implements this principle through frame-to-frame `Same`
detection, achieving 250+ FPS at 50% battery on integrated GPU.

Sleep serves three independent but complementary functions, all derivable from
the `Same`/`Different`/`Unknown` architecture:

1. **Buffer clear** (RAW 035): accumulated `Unknown` backlog cleared
2. **`Same` filter update** (RAW 119): pattern set optimized, weak patterns pruned
3. **Routing slot replenishment** (this document): vesicle pools restored,
   impulse-level granularity recovered

The theoretical maximum efficiency gain is 1/P_unknown — the inverse of the
fraction of inputs that are genuinely novel. For most stable environments,
P_unknown is very small, and the efficiency gain is correspondingly very large.

**The universe computes sparsely. Any entity that does not is wasting substrate.**

---

## References

- RAW 035 — The Observer Sleep Principle
- RAW 113 — The Semantic Isomorphism: Same / Different / Unknown
- RAW 118 — Gravity as Consumption and Transformation of Connectors
- RAW 119 — Buffer Saturation and Sleep as Universal Compact
- Rao, R. & Ballard, D. (1999) — "Predictive Coding in the Visual Cortex"
- Norretranders, T. (1998) — "The User Illusion"
- Larkum, M. (2013) — "A cellular mechanism for cortical associations"
- Davies, M. et al. (2018) — "Loihi: A Neuromorphic Manycore Processor"
- Bhaskaran, M. et al. (2017) — "Synaptic vesicle recycling and fatigue at
  cortical synapses" (vesicle depletion timescales under high firing rates)

---

*Date: March 21, 2026*
*Status: DRAFT*
*Depends on: RAW 035, RAW 113, RAW 118, RAW 119*
*Key claim: Efficient computation = sparse Unknown routing via local Same filtering*
*Sleep = three independent restorations: buffer + filter + routing slots*
