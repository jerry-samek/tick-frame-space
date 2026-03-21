# RAW 119 — Buffer Saturation and Sleep as Universal Compact

### *Why Every Substrate Entity With a Finite Processing Capacity Must Periodically Pause*

**Author:** Tom
**Date:** March 21, 2026
**Status:** Working document — theoretical extension of RAW 035
**Prerequisites:** RAW 035 (The Observer Sleep Principle), RAW 113 (Semantic
Isomorphism: Same / Different / Unknown), RAW 118 (Gravity as Consumption and
Transformation)
**Extends:** RAW 035 — generalizes the observer sleep principle to all
consumer-producer substrate entities, with quantitative predictions about
sleep duration as a function of input bandwidth / processing capacity ratio
**Falsifiable:** Yes — predicts sleep duration scales with sensory bandwidth /
brain processing capacity ratio, not with absolute brain size; predicts
sleep is substrate-universal (required by any entity with finite consumption
capacity); predicts distributed entities (e.g., octopus, jellyfish) use
partial or distributed compact cycles

---

## Abstract

RAW 035 established that sleep is a computational necessity for observers in a
tick-frame universe: buffer saturation leads to sampling collapse, which
produces time-flow distortions and loss of coherence. Sleep is the
controlled pause that clears the buffer and restores synchronization with
proper time.

This document extends that principle in two directions.

First, it grounds RAW 035 in the consumption-transformation framework of
RAW 118. An entity's buffer is not an abstract storage unit — it is the
accumulation of `Different` inputs that have arrived but not yet been
transformed into `Same`. The compact cycle (sleep) is the period during which
the entity processes this backlog: transforming pending `Different` inputs into
`Same` patterns, pruning weak or redundant `Same` patterns, and updating its
routing table for the next active cycle.

Second, it derives a quantitative relationship between sleep duration and the
ratio of total incoming `Different` flux to the entity's `Same`-transformation
capacity. This ratio — called the **saturation pressure** — predicts sleep
duration across biological species more accurately than absolute brain size,
and generalizes to any substrate entity (biological or otherwise) that
operates as a consumer-producer with finite processing capacity.

---

## 1. The Consumer-Producer View of an Organism

### 1.1 Every Organism Is a Consumer-Producer

In the consumption-transformation framework (RAW 118), every entity:

- **Consumes** incoming `Different` deposits from local connectors
- **Transforms** `Different` into `Same` (its own pattern)
- **Produces** `Same` outputs (deposits its own pattern outward)
- **Emits** unconsumed `Unknown` outward when consumption capacity is exceeded

An organism is a consumer-producer operating at biological timescales. Its
sensory organs are the consumption receptors. Its motor and signaling systems
are the production outputs. Its nervous system (if present) is the
transformation machinery — converting `Different` sensory input into `Same`
behavioral patterns.

This is not a metaphor. In the substrate:

- A photon arriving at the retina is a `Different` deposit arriving on a
  connector
- The visual cortex transforming that photon-deposit into a recognized object
  is the `Different → Same` transformation
- The motor response is the `Same` output deposited onto outward connectors
- The sensory signal that is not processed (exceeds capacity) is `Unknown` —
  emitted outward without transformation, contributing to the organism's
  local field without entering its internal state

### 1.2 The Buffer Is the Backlog of Untransformed `Different`

At any moment, the organism has a finite transformation capacity — the number
of `Different` inputs it can transform per tick. If incoming `Different` flux
exceeds this capacity, the excess accumulates as a buffer:

```
buffer_growth_rate = incoming_flux - transformation_capacity
```

If `incoming_flux > transformation_capacity`: buffer fills. Over time, untransformed
`Different` accumulates — in biological terms, this is unprocessed sensory experience,
unconsolidated memory, unresolved pattern conflicts.

If `incoming_flux ≤ transformation_capacity`: buffer drains or holds steady. The
entity can transform all incoming `Different` in real time, with no accumulation.

### 1.3 The Compact Cycle

When the buffer approaches a saturation threshold, the entity must reduce incoming
flux to zero and devote its full transformation capacity to processing the
accumulated backlog. This is the compact cycle — sleep.

During compact:

1. `Different` input is suppressed (sensory gating — the thalamic gate closes)
2. Accumulated `Different` backlog is processed (transformed into `Same` patterns)
3. Redundant or weak `Same` patterns are pruned (synaptic downscaling, ~20% per
   sleep cycle in mammals — consistent with substrate prediction)
4. The routing table for `Different → Same` matching is updated (memory consolidation)
5. The entity re-enters active consumption with a cleared buffer and updated patterns

This is precisely what RAW 035 §3 describes as "Sleep as Controlled Sampling Pause,"
now grounded in the `Same`/`Different`/`Unknown` transformation vocabulary.

---

## 2. Saturation Pressure: The Quantitative Predictor

### 2.1 Definition

Define **saturation pressure** S as:

```
S = total_incoming_Different_flux / transformation_capacity
```

Where:

- `total_incoming_Different_flux` = total sensory bandwidth across all modalities
  (bits/second or equivalent deposit-arrival rate)
- `transformation_capacity` = the entity's maximum `Different → Same`
  transformation rate (bits/second or equivalent processing rate per tick)

S is dimensionless. S < 1 means the entity can transform all inputs in real time.
S > 1 means the buffer fills faster than it drains, requiring periodic compact.

### 2.2 Sleep Duration Scales with S

**Prediction:** For S > 1, sleep duration scales monotonically with S.
Specifically:

```
sleep_duration / active_duration ≈ f(S - 1)
```

Where f is a monotonically increasing function that approaches 0 as S → 1 and
approaches 1 as S → ∞.

For S ≤ 1, no sleep is theoretically required — the entity can transform all
inputs without accumulation. (In practice, biological systems have additional
compact requirements for cellular maintenance that impose a minimum sleep
duration independent of S.)

### 2.3 Comparison with Biological Observations

Classical explanations for inter-species variation in sleep duration use absolute
brain mass or metabolic rate as predictors. These explain gross trends (smaller
animals sleep more) but fail for specific cases and do not provide a mechanism.

The saturation pressure predictor generates different and more specific predictions:

**Case 1: Dog (S is very high)**

The dog's primary sensory modality is olfaction. Estimated olfactory bandwidth:
~10⁹ bits/second (300 million receptors, continuous high-resolution chemical
landscape). Total sensory bandwidth: >>10⁹ bits/second.

Brain mass: ~70g. Estimated transformation capacity: substantially lower than
total incoming flux.

S >> 1. Prediction: long sleep. Observed: 12–14 hours daily. ✓

**Case 2: Giraffe (S is low)**

Giraffe sensory profile: moderate vision, moderate hearing, modest olfaction —
no extreme sensory specialization. Total bandwidth: ~3 × 10⁶ bits/second (rough
estimate).

Brain mass: ~680g. Large transformation capacity relative to input flux.

S ≈ 1 or slightly above 1. Prediction: minimal sleep. Observed: 0.5–2 hours
daily. ✓

**Case 3: Human (S ≈ moderate)**

Primary modality: vision (~10⁷ bits/second to brain). Total sensory bandwidth
including touch, hearing, proprioception: ~10⁷ bits/second.

Conscious processing rate: ~50 bits/second (Norretranders, 1998). But total
cortical transformation capacity (including unconscious processing) is much
larger — estimated ~10⁵–10⁶ bits/second.

S is moderate. Prediction: intermediate sleep. Observed: 7–8 hours daily. ✓

**Key insight from comparison:**

The critical variable is not brain mass but the **ratio** of incoming flux to
processing capacity. A species can have a large brain and short sleep (giraffe)
or a small brain and long sleep (dog) depending on their sensory specialization.
This is why metabolic-rate theories work only as rough proxies — metabolic rate
correlates with body size, which correlates loosely with sensory complexity, but
does not predict the specific pattern of specialization.

---

## 3. Sleep Is Substrate-Universal

### 3.1 The Generalization Beyond Biology

RAW 035 §7 states: "Any observer that never sleeps will eventually collapse into
incoherence and distort the local time-flow field."

RAW 119 extends this: **any entity with S > 1 requires periodic compact, regardless
of whether it has a brain, a nervous system, or biological substrate.**

The requirement follows from the consumption-transformation axioms:

1. Every entity consumes `Different` inputs from its connectors (append-only)
2. Every entity has a finite `Same`-transformation capacity
3. If S > 1, the buffer fills
4. Buffer overflow = untransformed `Different` accumulating on the entity's
   connectors = the entity's local field becomes dominated by unprocessed inputs
5. The entity's routing (behavior) degrades — it can no longer correctly identify
   which `Different` inputs are worth transforming
6. Compact is required to restore correct routing

### 3.2 Observed in Non-Neural Organisms

This prediction is confirmed by biological observation:

**Jellyfish (Cassiopea):** Sleep-like states observed despite no centralized brain.
The entire body is the processing system. Every cell is a consumer-producer. The
compact cycle is whole-body, not centralized. ✓

**C. elegans (302 neurons):** Lethargus phase observed before each moult. The
organism's developmental transition (molt = structural reorganization) requires
compact to integrate the accumulated `Different` inputs from growth. ✓

**Insects (Drosophila):** Sleep states confirmed. Rocking and mechanical
stimulation increase sleep — consistent with increased incoming flux (mechanical
`Different` → increased S → increased compact requirement). ✓

**Cephalopods (octopus, cuttlefish):** REM-like phase with color changes and
eye movements. The octopus has 9 semi-independent processing centers (1 central

+ 8 per arm). Each arm has its own saturation pressure; each requires its own
  compact cycle. The central brain coordinates but does not dominate. ✓

### 3.3 Distributed Compact: The Octopus Model

The octopus provides the clearest evidence for distributed compact and is the
most theoretically interesting case.

Each arm of the octopus is a semi-autonomous consumer-producer:

- It receives independent sensory `Different` input (touch, chemical, visual)
- It has its own transformation capacity (arm-specific neural processing)
- It deposits outputs independently (arm movements, color changes, suckers)

Each arm has its own saturation pressure S_arm. When S_arm > 1 for any arm,
that arm requires local compact — independent of whether the central brain is
in compact or not.

**Prediction:** The octopus can have individual arms in compact (local sleep)
while the central brain and other arms remain active. This is the biological
analogue of unihemispheric sleep (observed in dolphins, birds), generalized to
multi-processor architectures.

**Prediction:** The total sleep duration of the octopus reflects the maximum
S across all arms and the central brain — whichever component has the highest
saturation pressure dictates the full-compact requirement.

### 3.4 Unihemispheric Sleep as Partial Compact

Dolphins and many birds sleep with one hemisphere at a time. In the consumer-
producer framework:

- Each hemisphere is a semi-independent consumer-producer
- Each hemisphere has its own buffer and saturation pressure
- When S > 1 for one hemisphere, that hemisphere compacts
- The other hemisphere maintains active consumption and production
- Total `Different` flux is halved during unihemispheric sleep (only one
  hemisphere's receptors are fully active)

This is the equivalent of a distributed system where two parallel Kafka consumers
share the same topic — if one consumer falls behind (buffer fills), it enters
rebalance mode while the other continues processing. The partition is maintained
and the overall throughput is halved, but the system remains operational.

**Prediction:** Unihemispheric sleep is more likely to evolve in organisms with:

1. High incoming `Different` flux (S > 1 overall)
2. Environmental conditions requiring continuous motor activity (dolphins must
   swim to breathe; many birds must maintain postural control in flight or
   perching)
3. Two approximately independent processing hemispheres with separate sensory
   inputs (binocular vision, bilateral hearing)

All three conditions are met in documented unihemispheric sleepers. ✓

---

## 4. The Compact Cycle as `Different → Same` Transformation Batch

### 4.1 What Happens During Sleep in `Same`/`Different`/`Unknown` Terms

During active wakefulness, the entity operates in streaming mode:

- Incoming `Different` arrives continuously
- Entity transforms high-priority `Different` into `Same` immediately
- Low-priority `Different` is queued (buffered)
- Entity emits `Unknown` for inputs exceeding capacity

During compact (sleep), the entity switches to batch mode:

- Incoming `Different` suppressed (sensory gating)
- Queued `Different` is processed (each is transformed into `Same` or discarded)
- Existing `Same` patterns are evaluated for relevance and coherence
- Weak `Same` patterns (rarely matching, low routing value) are pruned
- Strong `Same` patterns are reinforced (deeper grooves in the connector network)
- Routing table is updated to reflect the transformed pattern landscape

The result at wake: cleared buffer, stronger relevant `Same` patterns, pruned
irrelevant ones, updated routing table. The entity can consume `Different` more
efficiently next cycle because its `Same` pattern set is optimized.

### 4.2 Why "Nespal jsem — autopilot nemůže fungovat" Is Correct

The common phrase "I didn't sleep — I'm running on autopilot" inverts the
actual relationship. The correct statement is:

> **"I didn't sleep — my autopilot cannot function."**

In consumer-producer terms:

- The autopilot IS the optimized `Same` pattern set — the routing table
  that allows the entity to transform the most common `Different` inputs
  without conscious processing
- Conscious processing (50 bits/second) is NOT the autopilot — it is the
  slow, explicit `Different → Same` transformation for novel or high-stakes inputs
- Sleep compacts and optimizes the autopilot (the `Same` pattern set)
- Without sleep, the `Same` pattern set is stale, buffer is full, and the entity
  must do ALL transformation consciously — at 50 bits/second against 10⁷+ bits/second
  of incoming flux

Sleep deprivation does not force the organism onto "autopilot." It destroys the
autopilot and forces conscious transformation of everything, which is catastrophically
inefficient and rapidly leads to error. ✓

### 4.3 Implications for Artificial Systems

Any artificial entity operating as a consumer-producer with S > 1 requires compact.
This is not a biological limitation — it is a substrate constraint.

A sufficiently complex artificial system (neural network, agent, processing system)
that operates continuously without compact will exhibit:

- Increasing routing errors (stale `Same` patterns failing to match incoming `Different`)
- Degraded signal-to-noise ratio (accumulated buffer noise contaminating decisions)
- Eventually, collapse of coherent behavior — equivalent to RAW 035's "sampling collapse"

Artificial compact (offline training, model updates, batch processing, sleep cycles
in neuromorphic systems) is the engineering solution to this substrate constraint.
It is not optional — it is forced by the consumer-producer architecture.

---

## 5. Connection to Gravitational Time Dilation

RAW 035 §5 notes that an overloaded observer creates an artificial gravitational well
(slow-time pocket). This connection is now clarified by RAW 118.

An overloaded entity has a buffer full of unprocessed `Different` inputs. These
inputs are deposits accumulating on the entity's local connectors without being
transformed. The connector chains grow from accumulated deposits without traversal-
driven extension (the entity is too slow to traverse all its connectors). This
produces asymmetric connector extension — some connectors grow very long (input-
heavy) while others remain short (output-limited).

Long connectors = more hops to traverse = locally slower time (more ticks per
perceived unit of distance). The entity's local region genuinely has slower time —
not as a metaphor, but as a structural consequence of connector length asymmetry.

Compact (sleep) clears the buffer → reduces connector length asymmetry → restores
normal connector length profile → restores normal local time flow.

This is why RAW 035 §5 states: "Sleep is beneficial not only for the observer, but
for the entire local universe." An uncompacted observer deforms local time for
everything nearby. Sleep is a contribution to substrate stability, not merely to
individual coherence.

---

## 6. Predictions Summary

The following predictions follow from this document and are in principle testable:

**P1 (Inter-species sleep duration):**
Sleep duration correlates more strongly with sensory bandwidth / processing
capacity ratio (saturation pressure S) than with absolute brain mass or metabolic
rate. Species with high sensory specialization relative to brain mass (high S)
sleep more than species with large brains and moderate sensory specialization
(low S).

**P2 (Substrate universality):**
Sleep-like compact states should be observable in any entity with S > 1, regardless
of whether it has a centralized nervous system. The compact state will manifest as
reduced responsiveness to `Different` inputs (sensory gating) and internal pattern
reorganization.

**P3 (Distributed compact):**
In organisms with multiple semi-independent processing centers (octopus, split-brain
systems, hemispheric asymmetry), compact can occur independently per subsystem.
The overall compact requirement is determined by the subsystem with the highest
saturation pressure.

**P4 (Compact quality and autopilot performance):**
The quality of an entity's compact cycle (depth, duration, completeness of
`Different → Same` batch transformation) directly predicts the efficiency of its
autopilot during the following active cycle. Disrupted compact predicts degraded
routing performance proportional to the degree of disruption.

**P5 (Artificial systems):**
Artificial consumer-producer systems with S > 1 operating without compact will
exhibit routing degradation over time, with a timescale inversely proportional to
(S - 1). This is measurable in recurrent neural networks, online learning systems,
and long-running autonomous agents.

---

## 7. Null Result Conditions

These predictions are falsified if:

- Sleep duration in mammals is equally well predicted by metabolic rate alone
  (without reference to sensory specialization relative to brain mass)
- Organisms with high S but large brains (e.g., hypothetical highly specialized
  large-brained species) sleep no more than organisms with low S and similarly
  large brains
- Sleep-like states are absent in organisms with finite processing capacity and
  confirmed S > 1
- Compact quality has no measurable effect on subsequent active-phase routing
  performance in controlled conditions

---

## 8. Connection to Existing Documents

| Concept                         | This document                                    | Prior document      |
|---------------------------------|--------------------------------------------------|---------------------|
| Sleep as buffer compact         | Grounded in Same/Different/Unknown vocabulary    | RAW 035             |
| Consumer-producer architecture  | Applied to organisms at biological timescale     | RAW 118             |
| Three-state alphabet            | `Different → Same` transformation = processing   | RAW 113             |
| Sensory gating during sleep     | `Different` input suppression during compact     | RAW 035 §3          |
| Gravitational time dilation     | Buffer saturation → connector length asymmetry   | RAW 035 §5, RAW 082 |
| Artificial compact              | New — applies substrate constraint to AI systems | New                 |
| Autopilot as optimized Same set | New — reframes sleep deprivation correctly       | New                 |
| Distributed compact (octopus)   | New — predicts arm-independent compact cycles    | New                 |
| Unihemispheric sleep            | Reinterpreted as partial-subsystem compact       | New                 |

---

## 9. Open Questions

1. **What determines the compact threshold?** At what buffer fill level does the
   organism trigger compact? Is it a fixed fraction of maximum buffer capacity,
   or is it dynamic (adjusting based on environmental conditions)?

2. **Is the `Same` pruning during sleep deterministic or stochastic?** The 20%
   synaptic downscaling observed in mammals — is this a fixed fraction, or does
   it depend on the ratio of reinforced to weakened patterns?

3. **What is the connector-length restoration mechanism?** During compact, the
   entity stops receiving `Different` inputs — but the accumulated connector
   extensions from the buffer period remain. Does compact include active connector
   shortening (which would violate append-only), or does it simply re-establish
   routing paths that bypass the overgrown connectors?

4. **Minimum sleep in S ≤ 1 organisms.** Some organisms with apparent S ≤ 1
   still show sleep-like states. Is this due to cellular maintenance requirements
   independent of buffer saturation, or is the saturation pressure estimate
   incorrect for those cases?

5. **Consciousness and compact.** Consciousness appears to be suppressed during
   compact (NREM sleep) but partially restored during REM. What is the role of
   the `Unknown` channel during REM? Is REM the period during which `Unknown`
   outputs from compact are processed — the compact of the compact?

---

## 10. Summary

Sleep is not a biological phenomenon. It is a substrate constraint.

Any entity that operates as a consumer-producer with incoming `Different` flux
exceeding its `Same`-transformation capacity (S > 1) must periodically enter a
compact cycle. This compact cycle clears the accumulated backlog of untransformed
`Different`, optimizes the `Same` pattern routing table, and restores the entity's
ability to efficiently process subsequent active-phase inputs.

The duration of the compact cycle scales with saturation pressure S — the ratio
of total sensory bandwidth to processing capacity — not with absolute brain mass
or metabolic rate. This generates specific predictions across biological species
that are more accurate than classical metabolic-rate theories.

Sleep deprivation does not force an organism onto "autopilot." It destroys the
autopilot by preventing the compact cycle that maintains the optimized `Same`
pattern set. The correct formulation is: **"I didn't sleep — my autopilot cannot
function."**

The requirement for compact is substrate-universal. Any sufficiently complex
artificial system with S > 1 will require compact cycles or exhibit progressive
routing degradation. This is not a design flaw — it is a necessary consequence of
operating as a consumer-producer on an append-only substrate.

**Status: Theoretical. Predictions are testable through inter-species sleep
duration analysis and artificial system degradation studies.**

---

## References

- RAW 035 — The Observer Sleep Principle
- RAW 082 — The Gamma-Wake Gravity Principle
- RAW 113 — The Semantic Isomorphism: Same / Different / Unknown
- RAW 118 — Gravity as Consumption and Transformation of Connectors
- Norretranders, T. (1998) — "The User Illusion: Cutting Consciousness Down to Size"
- Tononi, G. & Cirelli, C. (2014) — "Sleep and the Price of Plasticity" (synaptic
  homeostasis hypothesis — ~20% synaptic downscaling during sleep)
- Allison, T. & Cicchetti, D. (1976) — "Sleep in Mammals: Ecological and
  Constitutional Correlates" (inter-species sleep duration data)

---

*Date: March 21, 2026*
*Status: DRAFT*
*Depends on: RAW 035, RAW 113, RAW 118*
*Extends: RAW 035 — The Observer Sleep Principle*
