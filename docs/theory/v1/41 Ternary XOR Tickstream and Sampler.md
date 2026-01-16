# Ternary XOR Tickstream and Sampler

## 1. Why Three Values?

We begin with binary logic: 0 (absence) and 1 (presence). This is sufficient for oscillation, but it lacks symmetry. To restore balance, we introduce a third value:

* **+1** → presence, affirmation
* **0** → neutral horizon, nothingness
* **−1** → anti‐presence, mirror of +1

This triad is the minimal extension that allows:

* **Symmetry around zero** (balanced ternary)
* **Rich dynamics** (oscillation + stability)
* **Dimensional cues** (three states map naturally to axes or directions)

Thus, three values are not arbitrary — they emerge from the need for symmetry and progression beyond binary.

---

## 1a. Theory 1: NAND → 0, Symmetry Need Leads to −1

* **NAND operation:** foundational binary operator that outputs 0 only when both inputs are 1.
* **Emergence of 0:** from NAND logic, the neutral state 0 arises as a necessary balance point.
* **Symmetry need:** to maintain balanced ternary logic, the system requires the negative state −1 as a mirror to +1.
* **Interpretation:** the −1 state emerges naturally to fulfill symmetry demands beyond binary NAND constraints.

---

## 2. Tickstream (pure ternary XOR)

* **Rule:** (T(n+1) = XOR(T(n), T(n-1)))
* **Behavior:**
    * Guarantees variation (no stagnation)
    * Cycles through all three states in balanced rhythm
    * Local memory: depends only on the last two ticks
* **Emergence:** produces a raw stream of states — the heartbeat of the system.

---

## 3. Sampler (grouping into cycles)

* **Purpose:** detect when the tickstream has covered all three states, then emit a “Forget” pulse and toggle orientation.
* **Mechanism:**
    * Track coverage of states or edges
    * When {−1, 0, +1} (or all required edges) are seen → Forget = 1
    * Orientation toggles A ↔ B
* **Patterns:**
    * **A‐cycle:** +1 → 0 → −1 → Forget
    * **B‐cycle:** −1 → +1 → 0 → Forget
* **Effect:** converts raw XOR rhythm into structured beats or grouped cycles.

---

## 4. Emergent Properties

* **Restorative bias:** cycles through −1 and 0 always resolve back into +1 before Forget.
* **Dual attractors:**
    * Oscillation loop (+1 ↔ −1)
    * Neutral fixed point (0)
* **Symmetry:** orientation alternates, ensuring balanced traversal of clockwise and counterclockwise cycles.
* **Dimensional cue:** tickstream = raw substrate motion; sampler = higher‐order grouping into cycles.

---

## 5. Summary

* **Tickstream:** pure XOR rotor, generating raw ternary rhythm.
* **Sampler:** grouping layer, detecting full coverage, emitting Forget, and alternating orientation.
* **Three values:** necessary for symmetry, richer dynamics, and dimensional emergence.
* **Theory 1:** NAND → 0, a symmetry need leads to −1 as a foundational principle.
