# V3 Chapter 8: Open Questions

### *What the Framework Does Not Yet Know, and What Answers Would Look Like*

**Version:** 3.0
**Date:** March 2026
**Status:** Consolidated from V3 chapters 1-4, RAW 112-117, Experiment 64_109 v22-v24
**Depends on:** V3_ch001 (Graph Substrate), V3_ch002 (Three States), V3_ch003 (Emergent Geometry), V3_ch004 (Time and Depth)

---

## Abstract

This chapter catalogues the primary open questions in the V3 tick-frame theory as of
March 2026. Each question is stated precisely, its importance to the framework is
explained, the form of a satisfactory answer is described, and the current status is
assessed honestly.

The questions are ordered roughly by foundational priority: those that bear on the
internal consistency of the framework come first, those that bear on quantitative
predictions come next, and those that connect to specific observational targets come last.
The ordering does not reflect ease of resolution. Some foundational questions may be
harder to answer than some observational ones.

The framework is internally coherent and has produced qualitatively correct gravitational
behaviour on graph substrates. It has not produced a single quantitative prediction that
distinguishes it from standard physics. The gap between the theory's claims and its
validated consequences is large. This chapter maps that gap precisely so that future work
can close it in the right order.

---

## 8.1 Formal Definition of the `Same` Comparison Operator

### The Question

What is the precise mathematical definition of "pattern match" between an arriving
entity's deposit signature and a node's accumulated deposit state?

### Why It Matters

The entire three-state alphabet (Chapter 2) rests on a binary comparison: does the
arriving pattern match the existing deposits, or does it not? This comparison is the
substrate-level operation from which gravity, radiation, and expansion are claimed to
follow. Without a formal definition of the comparison operator, the three-state framework
is a qualitative narrative, not a computable theory.

The qualitative description is clear: an entity reads local connector states and follows
the laziest connector -- the one whose deposit history most closely resembles the entity's
own accumulated signature. "Most closely resembles" is doing all the work and is undefined.

The problem is not that a plausible definition is hard to imagine. Several candidates
exist:

- **Hamming distance** on a balanced ternary deposit string (matching trit-by-trit).
- **Dot product** of deposit vectors (treating the entity's signature and the node's
  state as vectors in some deposit space).
- **Topological overlap** of path history (the fraction of the entity's prior traversal
  that shares branches with the node's deposit ancestry in the trie).
- **Simple threshold** on the absolute difference of cumulative deposit counts (the
  integer gamma values at each node).

The problem is that different definitions produce different physics. Hamming distance
produces a discrete, threshold-based comparison. A dot product produces a continuous
similarity measure that varies smoothly. Topological overlap produces a comparison
sensitive to the deep history of both entity and node. A simple integer threshold produces
a local, memoryless comparison.

Each yields different predictions for the boundary between Same and Different -- which
means different predictions for when gravity operates, when radiation is emitted, and
where expansion occurs. The framework cannot make quantitative predictions until this
definition is fixed.

### What an Answer Would Look Like

A satisfactory answer would be a formal definition of the comparison operator that:

1. **Produces a binary outcome** (match or no match) or a continuous similarity measure
   with a threshold that separates Same from Different.
2. **Is computable** from the local state available at a single node (the arriving
   pattern and the existing deposit state) without requiring global information.
3. **Reproduces the laziest-connector routing** already demonstrated in Experiment
   64_109 v1-v24 as a special case or approximation.
4. **Generates the correct force law** when applied to deposit gradients from a massive
   body (ideally, inverse-square falloff in a locally 3D graph region).
5. **Is derivable** from the substrate primitives (nodes, deposits, append-only) without
   introducing new free parameters.

A weaker but still valuable answer would be a demonstration that two or more candidate
definitions produce equivalent physics in the regimes already tested -- establishing that
the choice does not matter until higher-resolution experiments probe the boundary.

### Current Status

**Undefined.** The simulations use a proxy: the laziest-connector rule, implemented as
"follow the neighbor with the largest gamma gradient" in a continuous float field. This
proxy has produced gravitational attraction, curved trajectories, and dissipative capture.
It has not been shown to be equivalent to any formal comparison operator on deposit
signatures. The proxy operates on aggregate field values, not on the pattern-matching
semantics that the three-state framework describes.

---

## 8.2 Photon Properties as Path Geometry

### The Question

Chapter 2 claims that frequency, amplitude, and polarization are not intrinsic properties
of a photon signal but properties of the path the signal traversed -- the sequence of
Same, Different, and Unknown firings along the propagation route. Frequency is claimed to
be the firing rate of Different events per unit branch depth. Does mapping this firing rate
onto the electromagnetic spectrum reproduce observed spectral line ratios?

### Why It Matters

If the path-geometry account of photon properties is correct, it would constitute a
substrate-level derivation of spectroscopy. The Balmer series of hydrogen has precise
frequency ratios (described by the Rydberg formula). The theory claims these ratios
emerge from the structure of hydrogen's deposit pattern in the trie -- specifically, from
the rate at which a propagating Different event encounters non-matching deposits as it
traverses the hydrogen atom's internal structure.

This is a strong, falsifiable claim. The Rydberg formula is:

```
1/lambda = R_inf * (1/n1^2 - 1/n2^2)
```

where R_inf is the Rydberg constant and n1, n2 are principal quantum numbers. If the
path-geometry account can reproduce this formula from deposit-density profiles of
hydrogen-like structures in the graph, it would be the first quantitative prediction of
the three-state framework that connects to measured physical constants.

If it cannot -- if no arrangement of deposit densities in a graph produces the 1/n^2
spacing of hydrogen energy levels from Different firing rates -- the photon-as-path-
geometry claim is falsified in its current form.

### What an Answer Would Look Like

A satisfactory answer would demonstrate, either analytically or computationally:

1. A deposit structure in the graph that represents a hydrogen-like bound state (a
   self-sustaining pattern with discrete internal modes).
2. A propagating Different event traversing this structure at different entry conditions.
3. The Different firing rate per depth varying with the internal mode, producing a
   discrete spectrum.
4. The spacing of that spectrum matching 1/n^2 to within the resolution of the
   simulation.

A weaker but significant result would be demonstrating that Different firing rates through
any structured deposit region produce a discrete spectrum at all -- showing that the
mechanism can generate spectral lines in principle, even if the specific ratios are not yet
matched to hydrogen.

### Current Status

**No work done.** No simulation has implemented a propagating Different event. All
radiation in the current experiments is modeled as continuous field diffusion, not as
comparison-outcome propagation. The photon-as-path-geometry account remains entirely
theoretical.

---

## 8.3 Depth as Proper Time: Quantitative Correspondence

### The Question

Chapter 4 proposes that branch depth -- the count of structure-creating events along an
observer's path -- is proper time. Dense deposit regions accumulate depth slowly (because
Same dominates and few novel events occur). Sparse regions accumulate depth quickly.
This qualitatively reproduces gravitational time dilation. Does the ratio of two
observers' depth accumulation rates reproduce the Lorentz factor quantitatively?

Specifically: for an observer at distance r from a mass M, does the depth accumulation
rate satisfy

```
depth_rate(r) / depth_rate(infinity) = sqrt(1 - r_s / r)
```

where r_s = 2GM/c^2 is the Schwarzschild radius? And for an observer moving at velocity v,
does it satisfy

```
depth_rate(v) / depth_rate(0) = sqrt(1 - v^2 / c^2)
```

### Why It Matters

This is the critical quantitative bridge between the V3 framework and known physics.
If the depth accumulation ratio reproduces the Lorentz factor, the framework derives
special and general relativistic time dilation from the single mechanism -- a major
result. If it produces only qualitative agreement (slower near mass, but with the wrong
functional form), the framework is an incomplete model that captures the direction of
time dilation but not its magnitude.

V2-substrate experiments (Experiment 51, v9) achieved correlation r = 0.999 with the
GR prediction for time dilation using a continuous reaction-diffusion field substrate.
This validates the mechanism (gradient-following produces correct dilation ratios) but
does not validate the V3 graph substrate. The mechanism may transfer. It has not been
tested on a graph with deposit chains.

### What an Answer Would Look Like

A satisfactory answer requires two things:

1. **A formal derivation** relating local deposit density to depth accumulation rate.
   The derivation would start from the growth suppression formula
   `growth = H / (1 + alpha * (gamma_A + gamma_B))` and show that the ratio of
   growth rates at two radii from a massive deposit source converges to the
   Schwarzschild factor in the appropriate limit.

2. **An experimental measurement** on the graph substrate. Place two depth counters at
   different distances from a self-pinning star in Experiment 64_109. Run for sufficient
   ticks. Compare the measured depth ratio to the GR prediction.

The derivation alone would be significant. The measurement alone would be significant.
Both together would be conclusive.

### Current Status

**Qualitative only.** Self-pinning has been observed (v22 Phase 0), confirming that
dense regions suppress connector growth. Depth accumulation rate has not been measured
in any simulation. No per-observer depth counter exists in the current codebase. The
formal derivation from growth suppression to the Lorentz factor has not been attempted.

---

## 8.4 Semantic Encoding: Minimum Energy to Write One Bit

### The Question

The universe's information structure is a trie (Chapter 5). Shared history occupies
shared branches. Divergence creates branch points that record distinctions. Given this
structure, can an external encoder deliberately write structured information into the
graph? What is the minimum perturbation required to write one bit?

### Why It Matters

This question connects the tick-frame framework to the thermodynamics of computation --
specifically to Landauer's principle, which states that erasing one bit of information
dissipates at least kT ln 2 of energy (approximately 3 * 10^-21 joules at room
temperature).

In the graph substrate, writing one bit means creating one branch point -- a single
Different event at a node where Same would otherwise have fired. The minimum perturbation
is the minimum deposit required to flip the comparison outcome from Same to Different at
one node. This quantity should be derivable from the formal comparison operator (once
defined -- see 8.1) and the local deposit density.

If the minimum perturbation can be derived, the framework produces a substrate-level
Landauer bound. If this bound matches kT ln 2 at the appropriate temperature and scale,
the framework has derived a thermodynamic constant from graph topology. If it does not
match, the discrepancy reveals either a flaw in the framework or a refinement needed in
the connection between deposit density and thermodynamic temperature.

### What an Answer Would Look Like

A satisfactory answer would:

1. Define "one bit" in terms of the trie structure (one branch point, encoding a
   binary distinction).
2. Derive the minimum deposit perturbation needed to create that branch point, as a
   function of local deposit density and the comparison operator.
3. Connect deposit density to thermodynamic temperature (this requires a statistical
   mechanics of the graph, which does not yet exist).
4. Show that the resulting energy-per-bit either matches or systematically relates to
   the Landauer bound.

A weaker but valuable result would be demonstrating that the graph substrate has a
well-defined minimum information cost at all -- that there exists a finite lower bound
on the perturbation required to flip a comparison outcome, and that this bound scales
sensibly with local field conditions.

### Current Status

**Theoretical question, no work done.** The comparison operator is undefined (8.1),
so the minimum perturbation to flip it is undefined. No statistical mechanics of the
graph substrate has been developed. The connection to Landauer's principle is a research
direction, not a result.

---

## 8.5 Snapshot Drift Rate

### The Question

Chapter 4 establishes that perfect storage is impossible: every physical storage medium
participates in the substrate's ongoing dynamics and therefore drifts from its written
state. Can the drift rate of a snapshot be derived from the local Different event rate?

### Why It Matters

If the drift rate is derivable, it gives the framework a substrate-derived prediction for
the half-life of stored information on any physical medium. Different media in different
environments would have different drift rates determined by their local position in the
graph -- specifically, by how many Different events occur per tick in their vicinity.

This would connect to:
- **Magnetic media degradation**: higher temperature (higher Different event rate) means
  faster drift. Room-temperature magnetic storage has a characteristic half-life.
- **Geological record persistence**: deep underground storage (lower Different event
  rate, shielded from radiation) drifts slower.
- **Biological memory**: neural patterns in a high-activity environment (brain) drift
  rapidly compared to DNA in a cold, low-radiation environment.

Each of these is qualitatively correct. The question is whether the framework can
produce quantitative predictions -- specific drift rates as a function of local deposit
density and Different event frequency -- that match measured media degradation timescales.

### What an Answer Would Look Like

A satisfactory answer would:

1. Define "drift rate" precisely as the probability per tick that a stored deposit
   pattern at a node flips from Same to Different under ambient substrate dynamics.
2. Express this probability as a function of local deposit density, local Different
   event rate, and the comparison operator threshold.
3. Derive a half-life formula: the number of ticks after which the stored pattern has
   a 50% probability of having been modified beyond recognition.
4. Apply this formula to a known physical system (e.g., room-temperature magnetic
   storage) and compare the predicted half-life to the measured value.

Even establishing that the framework produces a well-defined half-life that scales
correctly with temperature (faster degradation at higher temperature) would be a
meaningful qualitative result.

### Current Status

**Theoretical claim, no derivation.** The impossibility of perfect storage is derived
from the append-only axiom (Chapter 4, Section 4.5). The specific drift rate as a
function of local conditions has not been derived. No simulation has measured snapshot
drift on the graph substrate.

---

## 8.6 Connector Formation Rule

### The Question

Chapter 1 claims that connectors are deposit chains -- not independent primitives.
If this is correct, what determines which nodes become connected? Does sufficient deposit
density between two previously unconnected nodes automatically create a connector? Is
there a threshold? What is it?

### Why It Matters

This is arguably the most consequential open question in the V3 framework. The answer
determines whether the graph topology is fully derived from the deposit field or whether
it requires an additional rule.

If connectors form automatically when deposit density between nodes reaches a threshold,
then the graph topology is entirely determined by the deposit field history. The initial
graph can be minimal (or empty), and all observed topology is built by the single
mechanism over time. The number of independent substrate properties drops to the
absolute minimum: nodes and deposit state. Everything else -- edges, topology, geometry,
dimensionality -- is derived.

If connectors require an explicit formation rule with its own parameter (a density
threshold, a proximity condition, a probability function), then that rule is a second
mechanism alongside deposit-hop-extend. The single-mechanism claim fails. The framework
has two operations, not one.

The current simulations sidestep this question entirely: they begin with a pre-built
graph (random geometric graph in v22-v24, cubic lattice in v1-v9) and never create new
edges during the simulation. The topology is given, not derived. Every graph experiment
to date is therefore testing the single mechanism on a substrate whose topology was not
produced by that mechanism.

### What an Answer Would Look Like

A satisfactory answer would:

1. Specify the formation rule precisely. For example: "Two nodes A and B become
   connected when the sum of deposit events along any chain of existing nodes
   linking A to B exceeds threshold T, where T is determined by [some derivable
   quantity]."
2. Show that the rule introduces no new free parameters -- that T is derivable from
   the existing primitives.
3. Demonstrate in simulation that a minimal initial graph (a few nodes, few or no
   edges) grows into a graph with the correct local dimensionality (D(n) = 3 in
   mature regions) under the deposit-hop-extend operation with the connector
   formation rule active.
4. Demonstrate that the resulting graph topology produces gravitational attraction
   comparable to what has already been demonstrated on pre-built graphs.

This is the planned target of Experiment 66 (the "anemone model" -- graph growth from
deposits alone). It has not been implemented.

### Current Status

**Unspecified.** No formal connector formation rule has been proposed. All simulations
use pre-built graphs. The claim that connectors are deposit chains is theoretical.

---

## 8.7 Deposit Strength from Entity Mass

### The Question

Deposit strength -- the amount of gamma an entity deposits per hop -- is the single
remaining tunable parameter in the framework. The theory claims it should emerge from
the entity's internal structure: an entity with more accumulated deposits should
naturally spend more per hop. What is the precise functional relationship between
an entity's mass (accumulated deposit count) and its deposit-per-hop?

### Why It Matters

A universe described by one mechanism and zero free parameters is the framework's stated
target. As of March 2026, four previously tunable parameters have been eliminated
(decay rate, drag coefficient, jitter amplitude) or are claimed eliminable (expansion
rate H). Deposit strength remains. If it can be derived from entity mass, the parameter
count reaches zero. If it cannot be derived without introducing a new assumption, the
framework has exactly one free parameter -- which is a significant reduction from
standard physics but falls short of the zero-parameter claim.

The relationship matters practically because it determines the strength of the
gravitational field produced by entities of different masses. In the current simulations,
deposit strength is set manually (e.g., `deposit_rate = 1e-5` in v24). The resulting
field strength determines whether orbits close, whether forces scale correctly with mass,
and whether the mass-force relationship matches Newtonian gravity.

Candidate relationships include:

- **Linear**: deposit = k * mass. Each unit of accumulated deposit contributes equally
  to spending. Simple but may produce runaway: massive entities deposit more, attracting
  more mass, depositing more.
- **Square root**: deposit = k * sqrt(mass). Diminishing returns on deposit spending.
  Naturally limits the growth rate of gravitational influence.
- **Logarithmic**: deposit = k * log(mass). Asymptotic limit on deposit spending.
  Very heavy entities barely deposit more than moderately heavy ones.
- **Unity**: deposit = 1 per hop regardless of mass. Each hop deposits exactly one
  quantum. Mass affects only the hop rate (v = c/M), not the deposit per hop. This is
  the simplest option and may be the correct one in the integer substrate where gamma
  is in {0, 1}.

### What an Answer Would Look Like

A satisfactory answer would:

1. Derive the deposit-per-hop from the entity's internal structure using only the
   single mechanism. No new assumptions.
2. Show that the derived relationship produces the correct gravitational force scaling
   (F proportional to M for large M, at fixed distance).
3. Demonstrate in simulation that the derived deposit strength produces stable dynamics
   -- not runaway accretion, not vanishing influence.

### Current Status

**Tunable parameter.** Set manually in all simulations. No derivation attempted. The
integer substrate model (gamma in {0, 1} per node) suggests deposit = 1 per hop as the
natural choice, which would eliminate the parameter entirely by making deposit strength
non-tunable. But the integer substrate has not been implemented in the graph experiments.

---

## 8.8 Traversal-Driven Expansion Replacing H

### The Question

The theory predicts that connectors extend only when traversed by an entity making a
deposit. The simulations use a global expansion parameter H applied to all connectors
every tick, regardless of whether any entity traversed them. Can H be eliminated and
replaced by true traversal-driven expansion?

### Why It Matters

H is the last global constant in the framework. It applies expansion uniformly -- to
connectors in dense regions and empty voids alike. The self-pinning mechanism (v22
Phase 0) partially corrects for this by suppressing growth in dense regions through the
denominator of the growth formula. But the correction is approximate: under global H,
connectors in perfectly empty voids still expand at rate H even though no entity has
ever traversed them. Under the correct mechanism, those connectors would not extend at all.

The self-pinning discovery demonstrates that H is a placeholder. Dense regions already
behave approximately as if expansion were traversal-driven, because their high deposit
density suppresses the growth formula's numerator. The correction happens automatically.
But the voids do not behave correctly: they expand whether traversed or not.

Replacing H with traversal-driven expansion would:

- **Eliminate the last global constant.** The expansion rate becomes a local, emergent
  quantity determined by the entity traffic on each connector.
- **Make self-pinning exact** rather than approximate. Dense regions resist expansion
  not because of a formula denominator but because entities within them traverse local
  connectors that then extend by small amounts offset by the deposit density.
- **Predict that a two-body system with one stationary star and one slow planet
  experiences nearly zero expansion.** Only the connectors traversed by the planet
  extend. The vast majority of the graph is untraversed and static.
- **Enable quantitative comparison with the observed Hubble constant.** H_0 should
  equal the mean connector extension per tick from all traversals in the observable
  volume. This is a derivable quantity once traversal statistics are known.

### What an Answer Would Look Like

A satisfactory answer would:

1. Implement traversal-driven expansion in the simulation: remove the global H loop
   and instead extend each connector only when an entity deposits on it during a hop.
2. Demonstrate that self-pinning still works (dense bodies remain geometrically
   stable).
3. Demonstrate that voids expand (they must, or expansion does not occur). This
   requires at least occasional entity or signal traversal of void connectors, which
   connects to the question of whether Different events (radiation) propagating
   through voids extend connectors as they traverse them.
4. Measure the effective expansion rate and compare it to the previous H-driven rate.

A partial result -- implementing traversal-driven expansion and showing it does not
immediately break the simulation's existing dynamics -- would already be significant.

### Current Status

**Not implemented.** All versions of Experiment 64_109 (v1-v24) use global H. The
transition to traversal-driven expansion is identified as a primary implementation
target. The main technical challenge is determining how radiation (propagating Different
events) interacts with connector extension -- whether a signal traversal extends the
connector it propagates along, and if so, by how much.

---

## 8.9 Closed Orbit from Proto-Disk

### The Question

Can the single mechanism produce a complete closed orbit -- perihelion to aphelion to
perihelion -- on a graph substrate, starting from a self-organised proto-disk with no
preset orbital velocity?

### Why It Matters

A closed orbit is the most basic gravitationally bound dynamical system. Newtonian
gravity produces closed elliptical orbits as its generic solution for two-body problems.
Any framework claiming to derive gravity must eventually produce closed orbits.

As of March 2026, no version of Experiment 64_109 has achieved this on any substrate.
The progression:

| Version | Substrate | Best result |
|---------|-----------|-------------|
| v1-v9 | Cubic lattice | Three-body scattering, 100k ticks, but no closed orbit |
| v22 | Random geometric | Curved trajectories, escape at ~16k ticks |
| v23 | Random geometric | Radial reversal, dissipative capture, partial lock |
| v24 | Random geometric | Anti-Newtonian scaling discovered, forcing rethink |

The lattice experiments demonstrated that the deposit-spread-follow mechanism produces
gravitational attraction, inertia, mass-velocity relation, and chaotic scattering. The
graph experiments demonstrated force, deceleration, curved trajectories, and capture. But
the trajectory has never closed. The planet always escapes or spirals into the star.

This is the primary experimental target. If a closed orbit emerges from the self-
organised deposit field of a star on a graph substrate, it demonstrates that the single
mechanism is sufficient for Keplerian dynamics. If it cannot be achieved despite correct
force scaling, the framework is missing something -- possibly an angular momentum
conservation mechanism that the current implementation lacks.

### What an Answer Would Look Like

A satisfactory answer would demonstrate:

1. A star that forms by depositing gamma onto its local graph for sufficient ticks
   to establish a stable gradient to orbital radii (following the v22 Phase 0
   protocol).
2. A planet (or proto-disk fragment) that acquires tangential velocity from the
   disk's velocity field (not from a hand-tuned initial condition).
3. The planet completing at least one full perihelion-aphelion-perihelion cycle
   without escaping or collapsing.
4. The orbital parameters (semi-major axis, eccentricity, period) remaining
   approximately stable over multiple orbits.

A weaker but still valuable result would be a single radial oscillation (infall,
turnaround, outward motion, turnaround) with the second perihelion occurring at
approximately the same radius as the first.

### Current Status

**Not achieved.** v24 is the most recent attempt. It increased star mass to M=1000 to
strengthen the gradient but discovered that the force law itself has pathological
scaling in the float approximation (see 8.11). The next step requires resolving the
force law issue before a closed orbit can be expected.

---

## 8.10 Baryon Asymmetry: Quantitative Prediction

### The Question

The framework posits three equally probable ground states (the balanced ternary: +1, 0,
-1) as the substrate alphabet. With three equally probable states, the framework claims
that matter-antimatter asymmetry is a necessary consequence of the initial symmetry
breaking. The observed baryon asymmetry -- approximately 1 excess baryon per 10^9
baryon-antibaryon pairs -- should be derivable from the statistics of three-state
encounters in an expanding deposit field. Can it?

### Why It Matters

The baryon asymmetry is one of the great unsolved problems of standard cosmology.
The Standard Model of particle physics does not naturally produce the observed ratio.
Proposed mechanisms (baryogenesis via leptogenesis, electroweak baryogenesis, Affleck-Dine
mechanism) all require extensions beyond the Standard Model.

The tick-frame framework has a structural feature that standard physics lacks: three
ground states instead of two. In a two-state system (matter/antimatter or +1/-1),
perfect symmetry produces exact cancellation. In a three-state system (+1, 0, -1), the
neutral state (0 / Unknown) acts as a buffer that can absorb asymmetry. When a +1 and
-1 encounter each other, the outcome depends on the local field state. If the local
field is non-zero (biased by prior deposits), the encounter does not produce perfect
cancellation. A residual remains.

The observed ratio of approximately 10^-9 is a specific number. The framework must
derive this number from the three-state encounter statistics, not merely argue that a
residual exists. The derivation would need to account for the expansion rate (which
dilutes encounters), the encounter cross-section (which depends on deposit density),
and the probability of asymmetric outcomes at each encounter (which depends on the
comparison operator).

### What an Answer Would Look Like

A satisfactory answer would:

1. Model the early-universe epoch as a high-density, high-temperature deposit field
   where +1 and -1 patterns encounter each other at high frequency.
2. Calculate the probability per encounter that the outcome is asymmetric (one sign
   surviving) versus symmetric (exact cancellation).
3. Integrate this probability over the expansion history to obtain the residual
   fraction after annihilation has run to completion.
4. Show that the residual is approximately 10^-9 without fitting -- that is, derived
   from the three-state statistics and the expansion dynamics alone.

A weaker result would be demonstrating that the three-state encounter statistics
produce a residual in the correct order of magnitude (somewhere between 10^-8 and
10^-10) for physically motivated parameter ranges.

### Current Status

**No work done.** The three-state encounter statistics have not been modeled. The
connection between the balanced ternary alphabet and baryon asymmetry is a theoretical
proposal in RAW 113. No quantitative derivation has been attempted. The framework
does not yet have a model of particle-antiparticle annihilation on the graph substrate.

---

## 8.11 Anti-Newtonian Scaling in the Float Model

### The Question

Experiment 64_109 v24 discovered that increasing star mass by 10x (from M=100 to
M=1000) produced approximately 15x weaker gravitational force at the orbital radius.
This is anti-Newtonian: in Newtonian gravity, 10x more mass produces 10x stronger
force at fixed distance. The cause was identified as gamma self-suppression in the
float model: the force law's denominator grows with local gamma density, so a more
massive star suppresses its own gradient.

The growth formula is:

```
growth = H / (1 + alpha * (gamma_A + gamma_B))
```

A more massive star deposits more gamma. Higher gamma means a larger denominator. A
larger denominator means less growth difference between connectors. Less growth
difference means a shallower gradient. A shallower gradient means weaker force.

The theory's response: this is an artifact of the continuous float approximation. In
the true integer substrate, gamma takes values in {0, 1} per node. The denominator is
bounded: at any node, gamma is either 0 or 1, so the maximum denominator per node is
(1 + alpha * 2). The denominator cannot grow without bound. A more massive star spreads
its deposits over more nodes (each carrying gamma = 1), producing a wider gradient rather
than a deeper one. The gradient depth is bounded but its extent is not.

This response is plausible but unvalidated.

### Why It Matters

If the anti-Newtonian scaling persists in the integer substrate, the single mechanism
cannot produce correct gravitational dynamics. More mass would always mean weaker force,
which contradicts the most basic observation about gravity. The framework would be
falsified.

If the integer substrate resolves the scaling -- producing a force that increases with
mass as expected -- then the float model's pathological behavior is an artifact of the
approximation, and the transition to integer gamma is not merely desirable but necessary
for correct physics.

### What an Answer Would Look Like

A satisfactory answer would:

1. Implement integer gamma deposits (gamma in {0, 1} per node) with hop-carried
   propagation (no float diffusion) on the graph substrate.
2. Measure the effective gravitational force at a test radius for two different star
   masses (e.g., M=100 and M=1000).
3. Show that force scales approximately linearly with mass (F proportional to M) rather
   than inversely.
4. Verify that the gradient extends over a wider region for larger mass, with the
   gradient depth bounded by the integer constraint.

A weaker but valuable result would be an analytical argument showing that the bounded
denominator in the integer model necessarily produces correct mass-force scaling,
without requiring a full simulation.

### Current Status

**Identified, not resolved.** The anti-Newtonian scaling was discovered in v24 (March
2026). The integer substrate explanation has been proposed as the resolution. No integer
gamma simulation has been implemented on the graph substrate. The float model remains the
only implementation, and it produces the wrong mass-force relationship.

---

## 8.12 4D Leakage as Dark Matter and Gravity's Weakness

### The Question

Chapter 3 established that local dimensionality D(n) is a property of each node's
neighbourhood. Regions with D(n) slightly below 3 exhibit modified gravitational dynamics
-- excess infall compared to 3D Newtonian predictions. This was proposed as a possible
account of dark matter (Chapter 3, Section 3.5.6).

A related and more speculative question: if regions of extreme density (galactic centres,
galaxy clusters) locally develop D(n) > 3 -- transitioning toward 4D connectivity --
then the deposit field acquires a fourth spatial degree of freedom. From the perspective
of a 3D observer, field contributions that leak into the fourth dimension are
gravitationally present (they affect the deposit gradient) but electromagnetically
invisible (Different events propagating in the fourth dimension do not reach the 3D
observer). This would appear, from 3D, as mass that gravitates but does not radiate.

Additionally, if gravity (Same routing) operates across all D(n) dimensions while
radiation (Different propagation) is confined to the 3D subspace that observers
reconstruct, then gravity has access to a larger volume of the graph than radiation
does. This dilutes gravity's apparent strength relative to radiation. The hierarchy
problem -- why gravity is 10^36 times weaker than electromagnetism -- might be a
consequence of gravitational Same operating in D > 3 while electromagnetic Different
operates in D = 3.

### Why It Matters

Dark matter and the hierarchy problem are two of the deepest unsolved problems in
fundamental physics. If dimensional leakage in the graph substrate can account for
either or both, it would be a major result. But the proposal is currently speculative --
it has no quantitative backing and may not survive careful analysis.

The dark matter connection is more tractable: if a graph region with D(n) = 2.8 produces
a gravitational anomaly that matches the Navarro-Frenk-White profile used to fit dark
matter halos, the prediction is testable. If no value of D(n) reproduces the NFW profile,
the hypothesis is falsified.

The hierarchy problem connection is more speculative: deriving gravity's weakness from
dimensional leakage requires knowing how deposit gradients project from higher-dimensional
to lower-dimensional subspaces, which requires the connector formation rule (8.6) and the
formal comparison operator (8.1) to be specified first. This question depends on answers
to other open questions.

### What an Answer Would Look Like

**For dark matter:**

1. Construct a graph region with controlled D(n) slightly below 3 (e.g., 2.7, 2.8, 2.9).
2. Measure the effective gravitational force on test entities at various radii.
3. Compare the force profile to the 3D Newtonian prediction and to the NFW profile.
4. If a specific D(n) value produces the NFW profile without fitting, the prediction is
   strong.

**For the hierarchy problem:**

1. Derive the ratio of gravitational to electromagnetic coupling as a function of the
   dimensional mismatch between Same (operating in D dimensions) and Different (operating
   in 3 dimensions).
2. Show that for the observed graph topology (locally 3D with occasional higher-
   dimensional leakage), the ratio is approximately 10^36.

Both would require a graph substrate where local dimensionality can be measured and
controlled. This is not available in the current experiments.

### Current Status

**Speculative.** The dark matter interpretation was proposed in Chapter 3 (Section
3.5.6). No quantitative work has been done. No experiment has measured gravitational
anomalies from dimensional deficit on the graph substrate. The hierarchy problem
interpretation has not been published in any raw document -- it is noted here as a
research direction that follows from the local dimensionality framework.

---

## 8.13 Summary of Open Questions

The following table summarises the twelve open questions, their foundational priority,
and their current status.

| # | Question | Priority | Status |
|---|----------|----------|--------|
| 8.1 | `Same` comparison operator | **Foundational** | Undefined |
| 8.2 | Photon properties as path geometry | **Foundational** | No work done |
| 8.3 | Depth as proper time (quantitative) | **Critical bridge** | Qualitative only |
| 8.4 | Semantic encoding (minimum bit cost) | **Theoretical** | No work done |
| 8.5 | Snapshot drift rate | **Theoretical** | No derivation |
| 8.6 | Connector formation rule | **Foundational** | Unspecified |
| 8.7 | Deposit strength from entity mass | **Parameter elimination** | Tunable parameter |
| 8.8 | Traversal-driven expansion (replace H) | **Implementation** | Not implemented |
| 8.9 | Closed orbit from proto-disk | **Experimental target** | Not achieved |
| 8.10 | Baryon asymmetry prediction | **Quantitative prediction** | No work done |
| 8.11 | Anti-Newtonian scaling (integer fix) | **Implementation blocker** | Identified, not resolved |
| 8.12 | 4D leakage (dark matter / hierarchy) | **Speculative** | No quantitative work |

### Dependencies Between Questions

Several questions are interdependent:

- **8.1 (comparison operator) blocks 8.2, 8.4, 8.5, 8.10, and 8.12.** Without a formal
  comparison operator, the photon account, semantic encoding, drift rate, baryon
  asymmetry, and dimensional leakage calculations cannot be made precise.

- **8.6 (connector formation) blocks 8.12.** Without knowing how connectors form, the
  question of whether dense regions develop higher-dimensional connectivity cannot be
  answered.

- **8.11 (integer gamma) blocks 8.9.** The anti-Newtonian scaling in the float model
  prevents closed orbits from forming. Resolving the force law is a prerequisite for
  achieving the orbital target.

- **8.7 (deposit strength) and 8.8 (traversal expansion) are independent** of most
  other questions and can be pursued in parallel.

- **8.3 (depth as proper time)** can be tested experimentally with the current codebase
  by adding per-entity depth counters, independent of the other foundational questions.

### Recommended Attack Order

Based on dependencies and achievability:

1. **8.11 (integer gamma)** -- Resolves the force law blocker. Implementation work,
   not theoretical. Enables 8.9.
2. **8.9 (closed orbit)** -- The primary experimental target. Demonstrates viability
   of the framework for basic gravitational dynamics. Requires 8.11.
3. **8.3 (depth as proper time)** -- Testable with current codebase. Add depth counters,
   measure. Independent of other questions.
4. **8.8 (traversal expansion)** -- Implementation target. Eliminates H. Independent
   of other questions.
5. **8.1 (comparison operator)** -- Foundational but hard. Theoretical work. Unblocks
   many downstream questions.
6. **8.7 (deposit strength)** -- Parameter elimination. May be resolved by the integer
   substrate (deposit = 1 per hop).
7. **8.6 (connector formation)** -- Foundational but requires a working simulation
   with correct force law first. Enables Experiment 66.
8. **8.2, 8.4, 8.5, 8.10, 8.12** -- Downstream questions that require 8.1 and other
   foundations. These are future work.

---

## 8.14 What Would Falsify the Framework

The open questions above describe what the framework does not yet know. It is equally
important to state what results would falsify it.

**The framework is falsified if:**

1. **Integer gamma produces the same anti-Newtonian scaling as float gamma.** If
   the bounded denominator in the integer model does not resolve the mass-force
   relationship, the growth formula itself is wrong, not just its approximation.

2. **No closed orbit can be achieved on any graph substrate with any force law
   derivable from deposit-hop-extend.** If the single mechanism is fundamentally
   incapable of producing bound orbits, it cannot describe gravity.

3. **The depth accumulation ratio at two radii from a massive body does not correlate
   with the Schwarzschild factor.** If self-pinning produces time dilation that is
   qualitatively correct but quantitatively unrelated to GR, the framework is not a
   refinement of existing physics but an unrelated model that accidentally mimics some
   features.

4. **The three-state partition has an observable fourth outcome.** If an experiment
   or theoretical analysis identifies a comparison outcome that is neither Same, nor
   Different, nor Unknown, the exhaustiveness claim fails and the unification of gravity,
   radiation, and expansion into three outcomes of one operation is incorrect.

5. **Deposit-grown graphs never develop D(n) = 3.** If the deposit-hop-extend operation,
   starting from a minimal graph, produces graphs with local dimensionality that never
   reaches 3, the framework cannot explain why observers reconstruct 3D space.

These are specific, testable conditions. Any one of them, if met, would require
fundamental revision of the framework. The open questions in this chapter are the
research programme designed to determine whether any of these conditions is met.

---

## References

- **V3_ch001** -- The Graph Substrate (deposit chains, single mechanism, append-only)
- **V3_ch002** -- The Three-State Alphabet (Same / Different / Unknown)
- **V3_ch003** -- Emergent Geometry (latency matrix, local dimensionality, self-pinning)
- **V3_ch004** -- Time and Depth (branch depth, time dilation, snapshot drift)
- **RAW 112** -- The Single Mechanism (March 2026)
- **RAW 112_01** -- The Hubble Tension Is Not a Tension (H as running total)
- **RAW 113** -- Semantic Isomorphism: Same / Different / Unknown
- **RAW 117** -- Teleios and the Origin Event
- **Experiment 64_109 v22** -- Star formation, self-pinning, curved trajectories
- **Experiment 64_109 v23** -- Radial reversal, dissipative capture
- **Experiment 64_109 v24** -- Anti-Newtonian scaling from float self-suppression
- **Experiment 51 v9** -- Time dilation correlation r = 0.999 (V2 substrate)
- **Experiment 15** -- Dimensional sweep, 3D stability optimum
- **Experiment 50** -- Dimensional equivalence rejection (rho = 2.0 result)

---

*Date: March 19, 2026*
*Status: V3 CONSOLIDATED*
*Depends on: V3_ch001, V3_ch002, V3_ch003, V3_ch004, RAW 112-117, Experiments 15, 50, 51, 64_109*
*Defines: The complete set of open questions as of March 2026*
*Recommended next action: 8.11 (integer gamma) -> 8.9 (closed orbit) -> 8.3 (depth measurement)*
