# V3 Glossary

Alphabetical definitions using V3 (graph-first) terminology.

---

## Substrate Terms

**Append-only.**
The guarantee that deposits cannot be removed. The graph only grows; no deletion mechanism exists. This produces the arrow of time (depth only increases) and resolves the information paradox (nothing that has happened can be undone). (RAW 112 S4)

**Branch depth.**
The count of structure-creating events along a path. The only clock in the substrate. Each `different` or `unknown` event that creates new structure increments depth by one. Replaces V2's "tick count" as the measure of time. (RAW 113 S4)

**Connector.**
A persistent chain of deposits linking two nodes. Not a geometric edge with intrinsic length. Connectors ARE deposit chains -- they exist because deposits were made and persist because deposits are append-only. There are no connectors independent of deposits. (RAW 111, RAW 112 S1.1)

**Deposit.**
The fundamental act of an entity spending part of itself onto a connector during a hop. Permanent and append-only. Every movement leaves a deposit; every deposit reinforces the connector chain; every reinforced connector is a longer hop distance. The entire graph is the accumulated deposit history rendered as topology. (RAW 112 S1.2)

**Depth-zero.**
An observer's personal Big Bang -- the first tick at which that observer has coherent internal state. The substrate has no global depth counter; each observer measures depth from its own first `unknown` write. Observers connecting at different substrate ticks reconstruct different cosmological histories from the same graph. (RAW 037, RAW 113 S4.3)

**Different.**
One of three comparison outcomes. The arriving pattern diverges from existing deposits at a node. Creates a branch point in the trie. A propagating `different` event is a photon; radiation is the substrate recording divergence. (RAW 113 S1, S2.2)

**Graph.**
The substrate. Nodes connected by connectors (deposit chains). No geometry, no metric, no continuum. The graph IS the space. Distance is hop count. Two entities are "near" if connected by few hops, "far" if connected by many. (RAW 111 S1)

**Hop.**
An entity moving from one node to a neighboring node along a connector. Requires depositing onto the traversed connector. The hop extends the connector. This is the complete physical operation of the single mechanism: deposit, hop, extend. (RAW 112 S1.2, S2.1)

**Local dimensionality.**
The number of independent directions in a node's neighborhood. An observer property, not a substrate property. Nodes without at least three perpendicular directions cannot support stable orbits -- orbital mechanics requires perpendicularity. The graph has no intrinsic dimension; dimensionality varies by node. (RAW 110 S3)

**Node.**
A discrete site in the graph. Holds accumulated deposits (causal history). The minimum distance between two entities is one hop; there is no zero-distance singularity. In the true substrate model, a node holds at most one deposit event (binary: present or absent). (RAW 111 S2, RAW 112 S1.1)

**Same.**
One of three comparison outcomes. The arriving pattern matches existing deposits at a node. The entity follows familiar path; no new structure is created. Gravity is the substrate routing entities toward `same` -- toward connectors with the most deposits, the least growth asymmetry. (RAW 113 S1, S2.1)

**Self-pinning.**
Dense deposit regions suppress connector growth, making dense bodies resist expansion automatically. High local gamma density produces a large denominator in the growth formula, driving connector extension toward zero. Stars, planets, and galaxies pin their own local graph; voids expand freely. This is the observed Hubble flow, derived from the single mechanism. (RAW 112 S2.7)

**Single mechanism.**
The one operation: deposit on connector, hop, connector extends. All physics derives from this. Gravity, inertia, momentum, expansion, and zero-point energy are consequences of this operation iterated by every entity at every tick since the first deposit broke the symmetry of 1=1. The number of free parameters required is zero. (RAW 112 S2.1)

**Trit.**
The fundamental unit of the framework. A three-valued comparison outcome: Same, Different, or Unknown. When an entity arrives at a node, the comparison of its arriving pattern against existing deposits produces exactly one of these three results -- they are the exhaustive logical partition of all possible comparison outcomes. No fourth state is constructible: the node either has no deposits (Unknown), has deposits that match (Same), or has deposits that diverge (Different). A trit has three independent change components, requiring exactly three spatial axes for lossless representation -- this is why space is three-dimensional. (RAW 108, RAW 113 S1). *See also RAW 126-127 for the extended capacitor model of the trit (V4 candidate).*

**Trie.**
The tree structure the substrate naturally produces. Shared history shares branches (runs of `same`); divergence points mark information boundaries (`different` fired); the frontier is unwritten configuration space (`unknown`). The universe is maximally compressed by construction because the three-state comparison only writes when it must. (RAW 113 S3)

**Unknown.**
One of three comparison outcomes. The node has no deposits -- never visited. The entity writes new state. A new node is instantiated. The graph grows. Expansion is encountering `unknown`: the substrate writing itself into previously unvisited configuration space. (RAW 113 S1, S2.4)

---

## Physics Terms

**Co-deformation.**
Measurement instruments share the substrate with the measured phenomenon. Changes to the substrate affect both equally, making discreteness undetectable from inside. A ruler is a chain of bound deposits spanning some number of hops; when the graph structure changes, the ruler changes by the same factor. The measurement returns the same number. (RAW 111 S4)

**Expansion.**
Accumulated connector extension from all hops ever taken. Not a force, not dark energy, not a cosmological constant -- a ledger entry in the append-only deposit record. More entities moving faster produces more deposits per tick, producing faster expansion. Expansion happens predominantly in empty regions because dense regions self-pin. (RAW 112 S1.3, S2.5)

**Force-on-hop.**
V21 experimental design where gravitational force is read once per hop, with the entity coasting between hops. Superseded by leapfrog in v22, which provides approximately 60 force corrections per orbit versus 20 with force-on-hop. (Exp 64_109 v21, v22)

**Gamma.**
The deposit field. Accumulated deposits at each node, tagged by source entity. An entity's own gamma must be subtracted (self-subtraction) to detect another entity's field -- without this, a pattern's own deposits drown any external signal. In the true substrate model, gamma is binary (deposit present or absent per node); float gamma is a simulation approximation. (RAW 076, RAW 111 S3.7)

**Gravity.**
Local connector asymmetry produced by another entity's deposit history. The entity reads connector growth rates at its current node and selects the laziest connector -- the one with the most deposits, the least growth, the lowest resistance. That direction points toward the depositing body. Not a force; a routing outcome of the `same` comparison. (RAW 112 S2.2, RAW 113 S2.1)

**Hop threshold.**
The displacement magnitude at which an entity hops to the next node. Uses the current local mean edge length at the entity's node (not the initial mean), tracking expansion throughout the simulation. A floor of half the initial mean edge length prevents runaway hopping at sparse graph boundaries. (Exp 64_109 v22, v23)

**Inertia.**
Deposit commitment cost per hop. A massive entity has more accumulated internal state to redistribute before it can move. More deposits to spend means more ticks before the next hop. Heavier patterns are slower not because a force resists them, but because they have more to deposit before moving on. (RAW 112 S2.3)

**Leapfrog force.**
Force update every N ticks, decoupled from hop rate. Provides higher angular resolution than force-on-hop by giving approximately 3x more force corrections per orbit at N=10. The correct integrator for orbital mechanics on discrete graphs. First produced genuinely curved trajectories in the experiment arc. (Exp 64_109 v22)

**Momentum.**
The inertia of the deposit trail. Previous deposits created a connector trail that favors continued motion in the same direction. The entity does not need to be pushed to continue moving; its deposit history encodes a preferred direction that persists until a new hop reads new connector asymmetry and nudges it. Not a conserved quantity added by hand. (RAW 112 S2.4)

**Photon.**
A `different` event propagating through the graph. Not an entity; not an arriving pattern that checks node state. A photon IS the comparison result, already fired, moving forward. Properties (frequency, amplitude, polarization) are path geometry -- the sequence of nodes traversed and the directions in which `different` fired -- not intrinsic signal properties. Absorption is `same` firing at the receiving node. (RAW 113 S2.2, S2.3)

---

## Observer Terms

**Observer.**
An entity performing trie traversal: arrive at node, compare internal state to node deposits, fire `same`/`different`/`unknown`, update internal state, hop. The observer's memory is the path taken through the trie since depth-zero. Its identity is that path. Two observers with identical paths are, by every definition the framework provides, the same observer. (RAW 113 S5)

**Snapshot.**
Capture of an observer's current position in the trie plus accumulated path history. Loading a snapshot instantiates a new traversal from exactly that causal position. The resumed observer continues the same equilibrium search. (RAW 113 S5.1)

**Snapshot drift.**
The divergence between a stored snapshot and current substrate state, because the storage medium is itself a deposit pattern in a substrate that continues its equilibrium search after writing. Media degradation is not corruption; it is the substrate accurately reporting its current state, which has diverged from write-time state. The `different` events that constitute degradation are the three-state alphabet operating as specified. (RAW 113 S5.1, S5.2)

---

## Experimental Terms

**Dissipative capture.**
A particle that has lost most kinetic energy through graph-discretization friction during a long outward spiral and settled at a radius where residual velocity matches weak gradient force. Not a true orbit; the equilibrium is between friction-depleted kinetic energy and a weak field, not between centripetal acceleration and gravitational force. First identified in v23 Run C (p19: r=25.9 locked for 27,000 ticks). (Exp 64_109 v23)

**Radial reversal.**
A particle changing from outward to inward radial drift. First observed in v23 Run C (p8: r=21.1 at tick 36k to r=17.1 at tick 60k). Demonstrates that the leapfrog force architecture can genuinely decelerate and reverse outward drift, even though closed orbits were not achieved. (Exp 64_109 v23)

**rho=2.0 signature.**
The scaling exponent that proves time is categorically different from spatial dimensions. All (n+t) systems show quadratic source scaling (rho=2.0) versus sub-quadratic scaling (rho=1.5) in pure spatial dimensions. Tested across 1,095 configurations with 0 exceptions. Combined with rotation asymmetry constraints from Experiment 44, this constitutes conclusive evidence that time is a special generator with accumulative/amplifying properties, not a spatial dimension. (Exp #50, Doc 50_01)

---

## Obsolete V2 Terms

These terms are superseded in V3. Listed for reference when reading older documents.

| V2 Term | V3 Replacement | Reason |
|---------|---------------|--------|
| ~~Planck cube~~ | Node | The substrate has no geometry; nodes are discrete sites, not cubes |
| ~~Tick-stream primacy~~ | Branch depth | Time is measured by structure-creating events, not a global counter |
| ~~Voxel~~ | Node | Same as Planck cube -- no volumetric embedding exists |
| ~~Spatial Laplacian~~ | Graph spread operation | Diffusion operates on graph topology, not a continuous manifold |

---

## V4 Candidate Material

The following RAW documents propose extensions beyond the V3 framework. They are internally consistent but introduce concepts (capacitor model, reading direction, fixed points) that conflict with V3's simultaneous-classification model of the three states and branch-depth definition of time. They are candidates for a future V4 consolidation:

- **RAW 125** — Reading direction (leaf-to-root vs root-to-leaf), universal fixed points, planetary uniqueness, biological incompatibility
- **RAW 126** — The trit as capacitor: three states as sequential hardware phases (Empty→Charging→Discharge), quanta as emergent from threshold discharge, time as cycle count
- **RAW 127** — Trit has depth: continuous charging phase (superposition), bimodal observation distribution, gravitational dependence of measurement statistics

Key tensions with V3: (1) sequential phases vs simultaneous classification of three states; (2) cycle count vs branch depth as time; (3) nodes as capacitors vs discrete graph sites. See RAW 400 for the full inconsistency analysis.

---

*Date: March 25, 2026*
*Status: V3 working glossary*
*Depends on: RAW 037, RAW 076, RAW 108, RAW 110, RAW 111, RAW 112, RAW 113, Exp #50, Exp 64_109 v21-v24*
