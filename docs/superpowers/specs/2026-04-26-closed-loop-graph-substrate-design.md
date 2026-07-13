# Closed-Loop Graph Substrate — Design Spec

**Date:** 2026-04-26
**Status:** Brainstormed and approved by Tom; pending implementation plan.
**Prerequisites:** RAW 28 (Temporal Surfing), RAW 49 (Temporal Ontology), RAW 126 (Trit-as-Capacitor), RAW 128 (Energy
Partition), RAW 130 (It Rotates Because It Consumes), RAW 131 (Lineage Substrate).
**Supersedes:** none — this is a fresh attempt at substrate orbital mechanics, building on closure observations from
Experiments 118, 128 (v1–v11), 131, and 132.
**Goal:** orbital mechanics from a substrate that respects renewal-not-identity, without smuggling Newton, Kepler, or
any geometric ansatz.

---

## 1. Why this attempt

Every prior attempt at substrate orbital mechanics has hit one of three walls:

- **Consumption-based (Exp 118 v4–v17, ~17 versions):** entities consume substrate deposits to create gradient. Earned
  binding, never earned orbits. Closure: entity-as-hopping-walker is non-native to RAW 28's renewal-not-identity
  ontology.
- **Hybrid graph + ODE (Exp 128 v9–v11):** earned 1/r² (slope −1.968), Keplerian orbits, exact tangential Schwarzschild.
  Failed radial Schwarzschild on isotropic RGG. Honesty audit: ODE-based orbits smuggle Newton; graph-based metric
  earned but pattern coherence still hand-coded.
- **Tree / anisotropic substrate (Exp 131 / 132):** explicit topology fixes for radial GR. 131 falsified Newton recovery
  on lineage trees. 132 earned per-edge Schwarzschild radial via reverse-engineered rule, failed horizon scaling. Both
  rules were *imposed*, not derived.

Closure across all three: **the framework keeps writing particles on top of a scaffold, while the theory keeps saying
there are no particles** — only renewal patterns. The code-theory mismatch is the root cause of why "orbital mechanics"
hasn't closed.

This design is the first attempt where:

- No entity is labeled in the substrate (no `entity.pos`, no entity object at all).
- Conservation is global and exact (no `+1/tick` injection).
- Cells see only differences (matches what real measurements actually access).
- The substrate is a closed-loop autoregressive system (no external observer / recognizer / source).
- Patterns are emergent from rule iteration; "movement" is pattern translation through cells, not cell movement.

If this works, orbital mechanics closes. If it fails in a specific way, we learn something concrete about which
commitment is the wrong one.

---

## 2. Ontological commitments

These are the load-bearing axioms. Every later choice cascades from these.

1. **Conservation.** Total substrate energy is fixed across all ticks. No source, no sink. Every tick *restructures* a
   fixed pool.

2. **Differential ontology.** Cells have no access to absolute values. They sense only:
    - spatial differences (am I different from my neighbors?)
    - temporal differences (am I different from myself last tick?)

   This is not a limitation imposed for cleanliness — it matches what real physics actually has. Every measurement is a
   difference.

3. **Closed loop.** Tick(t+1)'s input = Tick(t)'s output. No external stream, no observer, no recognizer. Just
   iteration. Whatever structure exists is whatever the rule's dynamics support under repeated composition.

4. **Renewal-not-identity.** Cells are substrate primitives. *Entities are emergent patterns* — coherent
   reception/emission cycles in the cell layer. Nothing in the code labels something a "planet" or a "star." Entity
   identity is post-hoc clustering on observed energy distributions.

5. **Pure graph.** No coordinates stored in the substrate. RGG used to construct the adjacency list (for the prototype's
   known 1/r² behavior); coordinates are then discarded as substrate data. They survive only analyst-side, used solely
   for visualization and post-hoc measurement. The substrate itself never references them.

6. **Lossy reconstruction = consumption.** Each tick a pattern reconstructs a slightly diminished copy of itself. Lost
   energy goes into the surrounding substrate (nearby cells). The continual lossy-reconstruction-and-replenishment flow
   IS the gravitational field. Mass = leak rate. This unifies RAW 128 (store-or-move) and RAW 130 (consumption-rotation)
   under one mechanism: there is no separate "consumption" rule — consumption is the inevitable consequence of patterns
   existing in a conservative differential substrate.

---

## 3. Substrate spec

### 3.1 Graph construction (one-time, at init)

- Sample N points uniformly in unit cube ⊂ R³.
- Connect any two points within Euclidean radius ρ.
- Discard the coordinates *for the substrate*. Keep them aside in a separate analyst-side array, used only for
  visualization and post-hoc spatial measurement.
- Defaults for prototype: `N = 100,000`, mean degree ≈ 12, ρ chosen accordingly. (Matches 128 v11 scale and connectivity
  profile, where the slope −1.968 is established.)

### 3.2 Per-cell state (substrate-side)

- `energy: int` — non-negative integer; quantized energy count.
- `incoming_last_tick: dict[edge_id → int]` — quanta received from each adjacency edge in the previous tick. Used for
  wake/inertia. Overwritten each tick.

That's it. No position. No mass. No momentum vector. No labels.

### 3.3 Global state

- `total_energy: int` — invariant. Asserted at the end of every tick (cheap conservation check).
- `tick_count: int`.

### 3.4 Initial condition

For the orbit experiment (Phase 4):

- Two seeded concentrations: a "star" (high energy in a small cluster of cells) and a "planet" (smaller concentration at
  some hop-distance from the star).
- Remaining energy distributed uniformly across all other cells, so that `total_energy` is whatever budget we choose (
  chosen so star ≫ planet ≫ background).
- This is the *only* place we put structure by hand. After tick 0, the substrate is on its own.

### 3.5 What we deliberately do not store

- No spatial coordinates per cell (substrate-side).
- No "this cell belongs to entity X" labels.
- No edge weights / lengths / anisotropy fields. All edges are equal; the graph is just adjacency.

---

## 4. Tick rule

Pure parallel cellular update. No global state mutation, no scans, no exceptions. Conservation is exact (integer-only
arithmetic).

### 4.1 Inputs available to cell C at tick t

- `E(t)` — own energy (integer ≥ 0).
- `I(t)[e]` for each adjacent edge e — quanta received from neighbor through e last tick.

That's all. No neighbor absolute values. No coordinates. No graph distance. Only the two differential signals committed
to in §2.

### 4.2 Update procedure (per cell, per tick)

**Step 1: Compute outgoing weight per edge.**

```
w_e = 1 + α · ( mean(I) − I[e] )
```

where `mean(I)` is averaged across the cell's edges. Edges that received a lot last tick get *less* outgoing weight (no
backflow). Edges that received little/nothing get *more* (continuation). At α=0, weights collapse to uniform → pure
diffusion.

`α` is the wake-bias strength — the one free parameter in the rule.

**Step 2: Normalize weights.**
Σ w_e = 1 across the cell's edges.

**Step 3: Hold-and-fire distribution (integer, exact, no fractional sends).**

For each edge e:

- Compute target: `target_e = E(t) · w_e` (real-valued, since Σ w_e = 1).
- Floor to integer: `outgoing[e] = floor(target_e)`.

Compute the residue:

- `R = E(t) − Σ outgoing[e]`  (integer in `[0, k−1]`)

The cell *holds* `R` quanta to next tick. It does not fire fractionally; quanta that don't divide cleanly stay in the
cell until they can. This is RAW 126's "trit is capacitor" rendered literally — the cell charges up across ticks when
its share-per-edge is sub-integer, and discharges when it can do so cleanly.

**Edge case behavior (not separate rule, just consequences):**

- `E(t) = 0`: all targets 0, nothing sent, R = 0. Cell is silent.
- `0 < E(t) < k` with α=0 (uniform w_e = 1/k): all `target_e < 1`, all `outgoing[e] = 0`, R = E(t). The cell hoards
  everything until inflow accumulates enough to cross threshold. Pure threshold-firing.
- `0 < E(t) < k` with α>0: high-w edges may have `target_e ≥ 1` and fire 1+; low-w edges sit at 0. Wake-biased partial
  firing.
- `E(t) ≥ k`: most edges get `outgoing[e] ≥ 1`; residue R = E(t) mod k (approximately) is held.
- `E(t) ≫ k` (e.g., star with E = 1000, k = 12): `outgoing[e] ≈ 80` per edge; cell fires hundreds of quanta, holds small
  residue.

The rule is one expression for all magnitudes. No separate cases.

**Step 4: Receive incoming.**
For each adjacent edge e, `incoming[e]` = whatever the neighbor sent through e in their step 3.

**Step 5: New state.**

- `E(t+1) = R + Σ incoming[e]`  (held residue plus new arrivals)
- `I(t+1) = incoming` (kept for next tick's wake bias)

### 4.4 Conservation invariant

- Every quantum sent through edge e by cell A is received through edge e by cell B (the other endpoint).
- Sum over all cells: `Σ E(t+1) = Σ E(t)` exactly.
- Asserted at the end of every tick. Test fails immediately if violated. (This is the cheapest and strongest sanity
  check we have.)

### 4.5 Initial conditions for the rule

- All cells start with `I = 0` → step 1 gives uniform `w_e` → tick 0 update is pure diffusion.
- Wake bias only activates once `I` has non-zero history (tick 1 onwards).
- No special init code needed.

### 4.6 What the rule gives us

- **Cells are capacitor-conduits.** They hold residue quanta when full distribution would require fractional sends;
  otherwise they pass energy through. RAW 126 trit-as-capacitor is the literal mechanism.
- **Mass** = a flow pattern whose wake bias creates self-reinforcing recirculation, plus held residue in cells where the
  pattern is dense.
- **Field** = the steady-state leakage flow around a pattern.
- **Movement** = consistent wake bias across ticks → pattern drift through cells.
- **Orbits** = wake-biased flow patterns whose drift bends under another pattern's gradient.
- **No floats anywhere** — conservation is exact, not approximate.
- **Self-organized criticality flavor** — structurally close to abelian sandpile models, which exhibit pattern
  formation, avalanches, and 1/f noise without external tuning. Stable patterns may emerge for free.

### 4.7 1/r² recovery

Geometric, not designed. RGG with mean degree 12 in R³ already gave −1.968 slope on radial flux measurement in 128 v11
Phase 1. This rule preserves the geometric falloff because it's still local + radial-in-expectation. The 1/r² *isn't
claimed as emergent from this rule alone* — it's inherited from the graph topology, which is itself an experimental
call (use RGG in prototype, validate dimensionality, then optionally retry on pure random graph in v2).

---

## 5. Test plan

Phased experiment. Each phase has explicit success criteria. We don't go to the next phase until the current phase
passes.

### Phase 1 — Conservation + diffusion sanity

**Setup:** random uniform energy across all cells.

**Run:** 1000 ticks.

**Verify:**

- Total energy invariant every tick (built-in assertion).
- With α=0, distribution stays statistically uniform — pure diffusion baseline.
- With α>0, no obvious instability (no runaway concentration in one cell, no explosive oscillation).

**Failure:** bug, not physics. Must pass before anything else means anything.

### Phase 2 — Static star, field formation

**Setup:** one heavy concentration (1000 quanta in a small cluster, ~50 cells), background uniform.

**Run:** 10,000 ticks.

**Measure:**

- Does the concentration *persist* as a coherent pattern? (centroid stable, total cluster mass stable in steady state)
- Does a steady-state energy gradient form around it?
- Does the gradient slope match −1.968? Fit on log-log radial bins (using analyst-side coordinates only for
  measurement).

**Success:** persistent star + measurable 1/r²-shaped field around it. This is the renewal-not-identity check — the star
exists *as a flow pattern*, no cell is privileged.

**Failure modes:**

- Star dissolves → wake bias too weak, or rule doesn't support static concentration.
- Star collapses to single cell → wake bias too aggressive (toward concentration), runaway.
- Field is 1/r^n with n far from 2 → graph isn't behaving as 3D dimensionally; investigate construction.

### Phase 3 — Test pattern in field

**Setup:** Phase 2's star + a small "test pattern" (10–50 quanta concentration) seeded at hop-distance ~30 from star.

**Run:** 5000 ticks.

**Measure:**

- Does the test pattern experience the gradient? Centroid drift toward star?
- Is drift acceleration consistent with the field gradient measured in Phase 2 (Newton's 2nd law check)?

**Success:** test pattern accelerates toward star at rate matching field. Gravity earned from substrate.

### Phase 4 — Orbit (the goal)

**Setup:** Phase 3's setup, but the test pattern is seeded with a tangential bias (initial wake-bias state non-zero in a
tangential direction relative to star).

**Run:** as long as needed — at least several orbital periods.

**Measure:**

- Closed trajectory (orbit)?
- T² ∝ a³ check across multiple seeded radii (Keplerian)?
- Coherence: planet stays intact over many orbits?

**Success:** stable bound orbit, Keplerian to within 5–10%. **This is the weekend goal.**

### Phase 5 — Emergent orbit (Doc 28 honesty check)

**Setup:** same as Phase 4 but no tangential seed — planet starts radially-symmetric, zero wake-bias state.

**Test:** does a coherent orbit emerge anyway, from substrate dynamics alone?

**Success:** would close renewal-not-identity in the strongest sense — even orbital intent is emergent. If this fails,
it's still informative; everything before Phase 5 is already worth the weekend.

This is the stretch goal. It may not pass on first try; do not block on it.

### Per-tick metrics logged for every phase

- `total_energy` (invariant — checked every tick)
- `n_firing_cells` (cells with `E ≥ k`) — proxy for pattern coherence
- `max_E` and `mean_E` — distribution stats
- `centroid(planet)` and `centroid(star)` — analyst-side, via post-hoc clustering on energy distribution (DBSCAN or
  equivalent on (graph-adjacency, E) features; coordinates used for centroid calculation only)
- `α` and other run parameters logged with run

---

## 6. What this design deliberately does NOT do

To prevent scope drift:

- **No general relativity claims.** Schwarzschild radial / horizon scaling are explicitly out of scope. If they emerge,
  great. If not, we still have orbital mechanics if Phase 4 passes.
- **No multi-pattern collisions / composite objects.** Synthesis with Exp 55/56 (collision physics, composite objects)
  is a follow-up if this design earns its first checkpoint.
- **No quantum effects, EM, thermodynamics.** This is a single-substrate, single-mechanism prototype.
- **No graph evolution.** Adjacency is fixed at init. Lineage-tree-style dynamic topology (RAW 131) is out of scope.
- **No multiple species / two-substrate models.** The substrate is one homogeneous integer-valued field. No
  activator/inhibitor (Turing-pattern flavor) split.
- **No non-RGG topology in v1.** Pure random graph (without R³ embedding) is a v2 follow-up if v1 succeeds.

---

## 7. Open parameters (to be tuned empirically in implementation)

- `α` — wake-bias strength. Sweep across [0, ~5]. Phase 1 will reveal the stable range.
- `N` — number of nodes. Default 100k; may need to scale up for orbits to have room.
- mean degree (via ρ) — default ~12; standard RGG value, validated in 128 v11.
- Star / planet seed mass and seeding cluster size.
- Tangential bias magnitude in Phase 4.

These are knobs we expect to turn; their values are not theoretical claims.

---

## 8. Falsification matrix

| Outcome                                    | What it tells us                                                                                                                            |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Phase 1 fails (conservation violation)     | Implementation bug                                                                                                                          |
| Phase 1 fails (instability at α>0)         | Rule design problem; wake-bias formulation needs revision                                                                                   |
| Phase 2 fails (star dissolves at all α)    | Substrate cannot support static patterns; ontology may need a stabilizing term we haven't named                                             |
| Phase 2 fails (star collapses to point)    | Wake bias is super-critical; nonlinearity is too strong; rule needs damping                                                                 |
| Phase 2 fails (field slope ≠ −2)           | Graph topology issue, not rule issue; revisit RGG construction                                                                              |
| Phase 3 fails (test pattern doesn't drift) | Patterns don't couple through field; either field is too weak or pattern coherence is too low                                               |
| Phase 3 fails (drift wrong magnitude)      | Coupling exists but not as Newtonian gravity; informative — points at where the rule deviates                                               |
| Phase 4 fails (no closed orbit)            | Field response exists but orbital stability mechanism missing; possibly needs Phase 3.1 from 128 v11 (mass-cap reinterpretation) or similar |
| Phase 4 succeeds                           | **Substrate orbital mechanics earned.** First time on any of our designs.                                                                   |
| Phase 5 succeeds                           | Renewal-not-identity earned in strongest form.                                                                                              |
| Phase 5 fails but Phase 4 succeeds         | Tangential intent must be seeded; orbits exist as patterns but not as fully self-organizing ones. Acceptable partial result.                |

---

## 9. Pointers

- **Theory:** RAW 28 (Temporal Surfing), RAW 49 (Temporal Ontology), RAW 126 (Trit-as-Capacitor), RAW 128 (Energy
  Partition), RAW 130 (Rotates Because Consumes), RAW 131 (Lineage Substrate).
- **Prior experiment closures:** `experiments/118_consumption_gravity/` (v17 closed),
  `experiments/128_energy_partition/v11_arrival_rig/` (Phase 1–7 closed),
  `experiments/131_lineage_substrate/CLOSURE.md`, `experiments/132_anisotropic_connectors/CLOSURE.md`.
- **Reference dimensionality result:** 128 v11 Phase 1 — RGG slope −1.968 vs Newton's −2.0.

---

## 10. Next step

Hand off to `superpowers:writing-plans` to produce a detailed implementation plan: directory structure (
`experiments/<num>_<name>/`), phase-by-phase code organization, dependencies, performance budgets, vectorization
strategy, and incremental validation gates aligned with §5.
