# RAW 112 — The Single Mechanism: Deposits, Movement, and Expansion as One Process

### *Why There Are No Separate Forces, No Separate Expansion, and No Free Parameters*

**Author:** Tom  
**Date:** March 2026  
**Status:** Working document  
**Prerequisites:** RAW 111 (Space Is Connections), RAW 110 (Local Dimensionality), RAW 076 (Gamma Field Principles)  
**Falsifiable:** Yes — predicts expansion rate is derivable from movement statistics with no free parameter

---

## Abstract

This document establishes that movement, expansion, and all field interactions reduce to a single physical operation:
**an entity spending a deposit on a connector to hop**. There is no separate mechanism for expansion. There is no
separate mechanism for gravity, inertia, or momentum. There is one operation, applied uniformly by every entity at every
tick. All observed phenomena — orbital mechanics, cosmological expansion, gravitational time dilation, zero-point
energy — are consequences of this single operation accumulating across the graph over time. The number of free
parameters required to describe a universe built from this operation is zero.

---

## 1. The Collapse to One Operation

### 1.1 What a Connector Actually Is

RAW 111 establishes that space is connections — nodes linked by edges. This raises an immediate question: what are edges
made of?

The answer is deposits.

A connector between node A and node B is not a primitive object. It is a **persistent chain of deposits** linking A to
B. When entity A deposits gamma at node A and that deposit propagates to node B, the propagation path is the connector.
The connector exists because deposits were made. The connector persists because deposits are append-only and cannot be
removed.

> **A connector IS a deposit chain. There are no connectors independent of deposits.**

This unifies the two primitives of the model — field deposits and graph edges — into one. The graph is not a substrate
on which deposits occur. The graph IS the accumulated deposit history, rendered as topology.

### 1.2 What Movement Actually Is

When an entity moves from node A to node B, it:

1. Reads local field state (connector growth rates)
2. Selects the laziest connector (least resistance path)
3. **Deposits part of itself onto that connector**
4. Hops to the neighboring node

Step 3 is the mechanism. The entity does not teleport. It spends. It leaves a deposit on the connector it traverses.
That deposit is not waste — it is the physical record of the traversal. It reinforces the connector chain. It is the
entity's causal history encoded in the graph topology.

> **Movement = spending deposits on connectors. There is no movement without deposition.**

### 1.3 What Expansion Actually Is

Every hop deposits onto the traversed connector. Every deposit adds to the connector chain. A longer chain is a longer
connector. A longer connector is a larger hop distance.

When every entity in the universe hops every tick — depositing onto every traversed connector — every connector grows
slightly. Across the entire graph, the cumulative effect of all deposits on all connectors is:

**Expansion.**

Dark energy is not a field. It is not a cosmological constant. It is not a force. It is the cumulative record of every
entity that has ever moved, encoded as connector extension, manifesting as the increasing distance between all nodes.

> **Expansion = accumulated connector extension from all hops ever taken.**

---

## 2. One Mechanism, Derived Consequences

### 2.1 The Single Operation

The complete physics of the universe reduces to one operation, applied by every entity at every tick:

```
read local field state
→ select laziest connector
→ deposit on that connector
→ hop
→ connector extends
```

Nothing else exists. No forces. No fields added by hand. No expansion parameter. No decay constant. No drag. No tunable
jitter.

Every observable phenomenon is a consequence of this operation iterated across all entities over all ticks.

### 2.2 Derived: Gravity

The star deposits gamma onto its connectors continuously. Those deposits spread through the graph. At the planet's node,
connectors pointing toward the star carry less growth (suppressed by dense gamma) than connectors pointing away (sparse
gamma). The planet reads this asymmetry and selects the lower-resistance connector — toward the star.

Gravity is not a force. It is **local connector asymmetry** produced by another entity's deposit history.

### 2.3 Derived: Inertia

A massive entity has more deposit history — more committed internal state to redistribute per hop. More deposits to
spend means more ticks before the next hop. Heavier patterns are slower not because a force resists them, but because
they have more to deposit before moving on.

Inertia is not resistance to acceleration. It is **deposit commitment cost per hop**.

### 2.4 Derived: Momentum

Between hops, the entity coasts on its accumulated velocity — the direction of its last deposit sequence. That direction
persists until a new hop reads new connector asymmetry and nudges it. The entity does not need to be pushed to continue
moving. Its previous deposits created a connector trail that favors continued motion in the same direction.

Momentum is not a conserved quantity added by hand. It is **the inertia of the deposit trail**.

### 2.5 Derived: Expansion Rate

The expansion rate of the graph is the mean connector extension per tick, summed across all connectors. This equals the
mean deposit-per-hop, summed across all moving entities. No free parameter governs this. The expansion rate is exactly
the total movement activity of all entities.

More entities moving faster → more deposits per tick → faster expansion.

Fewer entities or slower movement → less deposit → slower expansion.

The accelerating expansion of the observable universe corresponds to increasing total movement activity as structures
form, process, and radiate. Not a mysterious dark energy with arbitrary magnitude — a ledger entry in the append-only
deposit record.

### 2.6 Derived: Zero-Point Energy

An entity embedded in an expanding substrate cannot be perfectly stationary. Expansion continuously extends the
connectors around it. Even without deliberate movement, the substrate shifts beneath the entity — its neighboring nodes
drift. The minimum field disturbance experienced by any entity embedded in a moving substrate is:

**ZPE = minimum connector extension from expansion × local field coupling**

Zero-point energy is not vacuum fluctuation of unknown origin. It is the irreducible jitter produced by the substrate's
own expansion acting on every embedded entity. It is derivable directly from the expansion rate — which is itself
derivable from total movement activity.

No ZPE parameter. No jitter parameter. Both are consequences of one operation.

### 2.7 Derived: Field Self-Pinning — Dense Bodies Resist Expansion

**Empirically confirmed in Experiment 64_109 v22 Phase 0 (March 2026).**

The connector growth rule suppresses expansion near dense gamma:

```
growth = H / (1 + alpha × (gamma_A + gamma_B))
```

A body that deposits ≈ what it receives maintains high local gamma density. High local gamma means:

- Denominator is large
- Connector growth ≈ 0
- Local graph barely extends

**The body pins its own local graph. It opts out of expansion automatically.**

This produces physically correct cosmological behavior without any additional mechanism:

- **Dense bodies** — stars, planets, galaxies — deposit continuously. Local gamma stays high.
  Local connectors barely extend. Their neighborhood stays geometrically stable. Rulers made
  of the same matter don't change. From inside, nothing moves.

- **Empty voids** — no deposits, gamma ≈ 0, denominator ≈ 1, connectors extend at full rate.
  Voids expand freely.

- **Net result**: expansion happens predominantly in empty regions. Dense regions self-regulate
  against expansion through their own field density. No explicit mechanism distinguishes
  expanding voids from stable galaxies — the distinction emerges automatically from deposit density.

This is the observed Hubble flow: **galaxies don't expand, the space between them does.**
Derived from the single operation. Not programmed. Not assumed.

#### 2.7.1 The Pinning Frontier

When a star first forms from a seed deposit, its pinning radius grows outward over time. At early
ticks the star pins only its immediate neighborhood (r < 2-3). As deposits accumulate and the
gamma field spreads, the pinning frontier extends to larger radii.

The ratio g(r₂)/g(r₁) measures whether the field has reached power-law equilibrium between
two radii. When this ratio stabilizes — changes < 0.005 per 1000 ticks — the star has successfully
pinned the graph out to radius r₂. Only then is the field at r₂ stable enough to support
orbital mechanics.

In v22 Phase 0 experiments with H=0.00001:
```
tick 5k:  g10/g5 = 0.321, delta = +0.016/1k
tick 10k: g10/g5 = 0.379, delta = +0.010/1k
tick 15k: g10/g5 = 0.425, delta = +0.009/1k
tick 20k: g10/g5 = 0.463, delta = +0.007/1k
converging toward 0.500 (1/r equilibrium)
```

The star needs ~25-30k ticks to fully pin its field to r=10. This is not a numerical
artifact — it is the time required for the star's deposit pattern to extend its
pinning radius to orbital distances. It is physically real and cannot be shortcut.

#### 2.7.2 Implication for the H Parameter

In the current simulation, H is a global constant applied to all connectors every tick.
This is a placeholder for the correct mechanism: connectors extend only when traversed
(RAW 112 §1.3).

Self-pinning demonstrates that the simulation is already approximating the correct behavior
despite the placeholder. Dense regions resist H through field density. Sparse regions
feel the full H rate. The simulation self-corrects toward traversal-driven expansion without
being explicitly programmed to do so.

The residual discrepancy: H applies even to connectors that were never traversed by any entity.
In the correct mechanism, those connectors would not extend at all. Removing H and implementing
traversal-driven extension is the final parameter elimination. It would make self-pinning exact
rather than approximate.

> **Dense bodies resist expansion automatically. The universe self-organizes into stable
> islands in an expanding void — not because we programmed it that way, but because
> deposits create their own gravitational stability.**

---

## 3. The Parameter Count

### 3.1 What Previous Versions Required

Early simulations required explicit parameters:

| Parameter        | Purpose                             |
|------------------|-------------------------------------|
| Decay rate       | Prevent field saturation            |
| Drag coefficient | Prevent velocity runaway            |
| Jitter amplitude | Introduce ZPE-like noise            |
| Expansion rate H | Control cosmological expansion      |
| Deposit strength | Control gravitational field buildup |

Each parameter was a corner: a mechanism inserted by hand that should have emerged from the architecture.

### 3.2 What the Single Mechanism Requires

| Old parameter    | Status           | Derivation                              |
|------------------|------------------|-----------------------------------------|
| Decay rate       | **Eliminated**   | Expansion dilutes without deletion      |
| Drag coefficient | **Eliminated**   | Force-on-hop prevents runaway structurally |
| Jitter amplitude | **Eliminated**   | Derived from expansion rate             |
| Expansion rate H | **Eliminated**   | Derived from total movement activity    |
| Deposit strength | **Residual**     | Currently tunable; should emerge from entity mass |

The residual deposit strength parameter is the next corner to remove. It encodes how much an entity spends per hop —
which should emerge from the entity's internal structure, not be assigned externally.

A universe with one mechanism has zero free parameters. The current simulation is one corner away from that.

---

## 4. The Append-Only Guarantee

### 4.1 Why Nothing Can Be Destroyed

Every deposit is permanent. Every connector extension is permanent. Every hop leaves a permanent record in the graph
topology. The universe is an append-only ledger. Nothing that has happened can be undone.

This resolves several open problems:

**Information paradox:** Information is never destroyed. It is deposited into the graph and persists forever, diluted by
expansion but structurally present.

**Dark energy:** The expansion of the universe does not require energy injection from an external source. It is the
compound interest on every hop ever taken — append-only, perpetually accumulating.

**Arrow of time:** Time has a direction because the append-only ledger grows in one direction only. The past is encoded
in the current graph state as accumulated deposits. The future is the next deposit. There is no mechanism for reversal.

### 4.2 The Connector Cannot Be Destroyed

Since connectors are deposit chains, and deposits are permanent, connectors cannot be destroyed. They can be weakened —
if no new deposits reinforce them, expansion dilutes their relative density. But the deposit history remains.

This means entangled particles remain connected. The connector between them was never destroyed by spatial separation.
It was diluted by expansion until it carries negligible signal — but the graph edge persists. The correlation is not
spooky action. It is a persistent connector that expansion made very long but did not delete.

---

## 5. Dimensional Transition as Local Wave

### 5.1 Why Dimensions Change Locally, Not Globally

The single mechanism operates locally. Each entity reads only its local field state. Each hop deposits only on local
connectors. There is no global coordination.

This means dimensional transitions cannot be global events. A region saturates locally when its local deposit density
exhausts the available configuration space for three-dimensional dynamics. That region transitions to four-dimensional
stability locally — its connectors become over-dense, its dynamics become trivially predictable, its contribution to
interesting complexity decreases.

The transition propagates as a wave because local saturation changes the field density in neighboring regions, which
either accelerates or delays their own saturation.

### 5.2 The Dimensional Landscape

The universe is not at one uniform dimensional phase. It is a patchwork:

| Region                    | Local deposit density | Dimensional phase          |
|---------------------------|-----------------------|----------------------------|
| Leaf nodes at frontier    | Minimal               | 1D → 2D bootstrapping      |
| Cosmic voids              | Low                   | Early 3D, sparse dynamics  |
| Galaxy filaments          | Moderate              | Mature 3D, rich dynamics   |
| Galaxy centers            | High                  | Late 3D, approaching saturation |
| Black hole interiors      | Maximum               | Local 4D transition complete |

All connected by the same gamma field. All depositing into the same append-only substrate. All different phases of the
same single mechanism operating at different local densities.

### 5.3 The Frontier is Permanently Young

Because the graph is always expanding — new leaf nodes always added at the frontier — the frontier always has minimal
deposit density. New regions always bootstrap fresh complexity from 1D through 2D to 3D.

The universe cannot end. It can only age locally, while perpetually renewing at its frontier. The interesting 3D
complexity wave propagates outward indefinitely, finding fresh graph at the edges as dense interior regions transition
toward 4D stability.

> **The universe is not dying. It is molting.**

The heat death scenario requires a closed, finite universe with no new nodes. An append-only expanding graph with
perpetual leaf node creation has no heat death. The frontier is always young. Complexity always propagates forward.

---

## 6. The Equation That Doesn't Exist

### 6.1 Why There Is No Master Equation

Classical physics sought a master equation — a Lagrangian or Hamiltonian from which all physics follows by variation.
The tick-frame model has no such equation because the single mechanism is not a function to be minimized or extremized.
It is an operation to be iterated.

There is no potential energy surface. There is no least action principle. There is no variational calculus. There is:

```
for each entity at each tick:
    read local field
    select laziest connector
    deposit
    hop
    connector extends
```

The "equation" is a loop. The "physics" is the aggregate behavior of many loops running simultaneously.

The loop has no free parameters. Its behavior is determined entirely by the initial graph topology and the initial
deposit state. Both of these are themselves consequences of prior loop iterations, extending back to the first tick.

### 6.2 The First Tick

Before any loop iteration: perfect equality. 1 = 1. No distinction possible. No gradient. No connector asymmetry. No
laziest path.

The first deposit breaks this symmetry. A single deposit creates a distinction: this node has gamma, that node does not.
The first asymmetry creates the first gradient. The first gradient creates the first lazy connector. The first lazy
connector creates the first hop. The first hop extends the first connector.

From that point forward: the loop runs. Everything else is consequence.

The first deposit is the only underived event in the framework. It is not explained. It is the minimum unearned
assumption — smaller than any assumption in any existing physics framework. Not a singularity. Not a quantum fluctuation
with a probability amplitude. Not a divine act. Just: the loop had to start somewhere.

> **1 = 1 was disturbed once. Everything since is bookkeeping.**

---

## 7. Connection to Existing Documents

| Concept                          | This document              | Prior document |
|----------------------------------|----------------------------|----------------|
| Space as connections             | Connectors are deposit chains | RAW 111     |
| Local dimensionality             | Dimensional transition as local wave | RAW 110 |
| Three dimensions from trit       | Unchanged — still the derivation | RAW 108  |
| Matter/antimatter asymmetry      | Three states → 1/3 nothing probability | RAW 061 |
| Gravity from field gradient      | Unchanged — connector asymmetry = gravity | RAW 082 |
| ZPE from expansion               | Jitter derived from expansion rate | RAW 072  |
| Expansion without decay          | Connector extension replaces decay | RAW 077  |
| Self-pinning                     | Dense bodies resist expansion automatically | v22 Phase 0 |

---

## 8. Open Questions

1. **Deposit strength from entity mass.** The single remaining tunable parameter should emerge from the entity's
   internal deposit structure. An entity with more accumulated deposits should naturally spend more per hop. The precise
   relationship requires formal derivation.

2. **Connector formation rule.** If connectors are deposit chains, what determines which nodes become connected? Does
   sufficient deposit density between two nodes automatically create a connector? If so, the graph topology is fully
   determined by the deposit field — space is entirely derived from field history.

3. **Baryon asymmetry from three-state probability.** With three equally probable ground states (+1, 0, -1),
   matter-antimatter pairs annihilate through maximum deposit incompatibility. The residual matter fraction should be
   derivable from the three-state probability distribution and the encounter statistics in an expanding field. This is
   the primary candidate for the first quantitative prediction distinguishing the framework from standard physics. The
   observed ratio is approximately 1 in 10⁹ matter particles per photon — the framework should derive this from
   geometry rather than assume it.

4. **4D leakage as dark matter and gravity weakness.** If dense regions locally transition toward 4D stability, their
   field contributions leak into the higher-dimensional substrate. From 3D, these deposits appear as
   gravitationally-influencing but electromagnetically-invisible mass — dark matter. Separately, gravity's anomalous
   weakness relative to other forces may reflect that the gravitational field couples to the full substrate (including
   4D regions) while electromagnetic fields remain confined to 3D connectors.

5. **Expansion rate as movement ledger.** The claim that expansion = accumulated connector extension is qualitative. A
   quantitative derivation should connect the observed Hubble constant H₀ ≈ 70 km/s/Mpc to the mean deposit-per-hop
   across all entities in the observable universe. If the two quantities agree without fitting, this constitutes a
   strong quantitative validation.

6. **Star formation before planet formation.** Experiment 64_109 v21 revealed that placing a planet next to a star that
   has not yet built its gamma gradient produces no orbital dynamics — the planet escapes before gravity can act. The
   correct physical sequence is: seed deposit → star grows via self-reinforcing accumulation → star's pinning radius
   extends to orbital distances → proto-disk forms from field density fluctuations → planet coalesces inheriting
   tangential velocity from local field motion. This sequence eliminates all preset initial conditions for planetary
   formation. Implementation is the primary target for v22.

7. **Traversal-driven expansion replacing H.** The self-pinning result (§2.7) demonstrates that H is a placeholder.
   The correct mechanism — connectors extend only when traversed — would make self-pinning exact rather than
   approximate and eliminate the final global constant from the simulation. In a two-body system with one stationary
   star and one slowly moving planet, correct expansion should be nearly zero. This is the path to zero free
   parameters.

---

## 9. Summary

The tick-frame universe requires one operation:

> **Deposit on the connector. Hop. The connector extends.**

From this operation, iterated by every entity at every tick since the first deposit broke the symmetry of 1=1:

- Gravity emerges from connector asymmetry
- Inertia emerges from deposit commitment cost
- Momentum emerges from deposit trail persistence
- Expansion emerges from cumulative connector extension
- Zero-point energy emerges from expansion acting on embedded entities
- **Dense bodies resist expansion automatically** — field self-pinning produces stable
  islands in an expanding void without any programmed distinction
- Dimensional transitions emerge from local deposit saturation
- The perpetual frontier emerges from append-only graph growth

No free parameters. No separate expansion mechanism. No forces added by hand. No decay. No drag. No jitter parameter.

One mechanism. Everything else is what it looks like when you watch from inside.

---

## References

- RAW 076 — Gamma Field Principles
- RAW 077 — Gamma Field Dynamics
- RAW 082 — The Gamma-Wake Gravity Principle
- RAW 108 — Three Dimensions from Trit Change Geometry
- RAW 109 — Apparent Isotropy of c
- RAW 110 — Local Dimensionality
- RAW 111 — Space Is Connections
- RAW 061 — Matter-Antimatter Asymmetry
- RAW 072 — Jitter Scaling and Matter Growth (ZPE)
- Experiment 64_109 v1–v21 — Three-Body Dynamics on Graph Substrate
- Experiment 64_109 v22 Phase 0 — Star Formation and Field Self-Pinning

---

*Date: March 14, 2026*  
*Status: DRAFT*  
*Depends on: RAW 108, 109, 110, 111*  
*Opens: Baryon asymmetry quantitative prediction, connector formation rule, deposit strength derivation,
traversal-driven expansion (replacing H), v22 star formation architecture*  
*Updated: March 14, 2026 — Added §2.7 Field Self-Pinning from v22 Phase 0 experimental results*
