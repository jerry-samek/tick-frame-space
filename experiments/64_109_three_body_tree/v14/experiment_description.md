 # v14: Connector Bandwidth Gravity — The Two-Endpoint Edge Rule

## Date: February 21, 2026
## Status: Next experiment after v13 (pathfinder)

## v13 Legacy (Pathfinder)

v13 proved one critical thing: **geodesic frame rotation produces gravitationally
bound trajectories without any coupling parameter.** The body always goes "forward"
but the asymmetric edge lengths rotate the local frame. Bound orbits at r > 2.
Chaotic due to lattice discreteness, not physics.

v13 is done. It found the path. v14 walks it.

## The Key Insight: What is "m" in F = GMm/r²?

Newton's formula has two masses. In our framework:

- **M** = what the source broadcasts (gamma strength, entity count)
- **1/r²** = 3D geometric dilution (Gauss's law, standard)
- **m** = NOT mass. It's **bandwidth**. How many connectors the receiver has.

A size-1 entity sits on one node with k connectors. That's the maximum signal
it can receive. A star broadcasting on a million channels doesn't matter — the
planet only has k antennas.

The bottleneck is ALWAYS the receiver, not the sender.

### Why this still looks like F = GMm/r²

A vortex of N entities has N × k connectors total. More entities = more connectors
= more signal received. Connector count scales linearly with entity count.
So m_connectors ∝ m_mass. Same formula. Different meaning.

- Newton: "heavy things attract more because they're heavy"
- RAW 170: "connected things drift more because they receive more expansion signal"

### Why the equivalence principle still holds

Both the reception (force) AND the anchoring (inertia) scale with connector count.
More connectors = more pull BUT also more resistance to displacement.
They cancel. Free fall is universal. Every entity drifts the same.

## The New Edge Rule

v13 used: de/dt = 1 / (1 + α × M/r)

This only knows about ONE mass at distance r. The edge doesn't know its own endpoints.
That's a background metric imposed by hand, not emergent from local rules.

### v14 Rule: Edges know their TWO endpoints only

```
de/dt = H / (1 + α × (γ_A + γ_B))
```

Where:
- γ_A = total gamma at endpoint A
- γ_B = total gamma at endpoint B
- The edge knows NOTHING about distant masses
- Local information only — one hop, two nodes

### What this changes

| Feature | v13 (pathfinder) | v14 (connector bandwidth) |
|---------|-----------------|--------------------------|
| Edge rule | de/dt = H/(1 + αM/r) | de/dt = H/(1 + α(γ_A + γ_B)) |
| Information | Global (needs M and r) | Local (only endpoint gamma) |
| Metric source | Imposed from star mass | Emerges from gamma field |
| Two-body | Star curves space, planet rides | Both endpoints contribute |
| Planet affects edges | No | Yes (planet's gamma matters) |

### Why this is better

1. **Truly local.** Edge only reads its own endpoints. No action at distance.
   No "M" or "r" in the equation — just local gamma values.

2. **Mutual.** The star affects edges near it. The planet ALSO affects edges
   near it. Both masses shape the geometry. Not one background + one test particle.

3. **Self-consistent.** The gamma field comes from entity deposits + spreading.
   The edge lengths come from gamma at endpoints. The frame rotation comes from
   edge length asymmetry. Everything feeds back into everything. One loop.

4. **Receiver bandwidth.** The planet's gamma at its node determines how much
   it contributes to suppressing its own local edges. A heavier planet
   suppresses more = sits in a deeper local well = more anchored. That's inertia.

## Implementation Plan

### Phase 0: Edge Formation Test

Start with uniform edges. Place star (deposits gamma). Let gamma spread.
Let edges evolve by the two-endpoint rule. Measure the resulting edge
length profile.

**Expected:** Edges near star are short (both endpoints have high gamma).
Edges far away are long (low gamma at both endpoints). Profile should
approximate 1/r Schwarzschild-like shape — but emerging from local rules,
not imposed.

### Phase 1: Two-Body Geodesic on Emergent Metric

Same as v13 Phase 1, but edges form dynamically from gamma:

1. Formation phase: star deposits gamma, gamma spreads, edges evolve
2. Insert planet with tangential direction
3. Planet deposits its OWN gamma (weak, but nonzero)
4. Run with continuous edge evolution + frame rotation

**Success:** Planet orbits at r > 5. Frame rotation from emergent
edge profile produces binding.

**Strong success:** Planet's own gamma creates a small local well
that it carries with it — a self-gravitating test particle.

### Phase 2: Two Comparable Masses

Two bodies of equal mass. Neither is "the star." Neither is a test particle.

**The acid test:** Do they orbit each other? Both contribute to the
geometry. Both respond to the geometry. The edge profile between them
is shaped by BOTH.

If two equal masses orbit their common center of mass — the local
two-endpoint rule produces real gravity, not a background approximation.

### Phase 3: Three-Body

Star + planet + moon. Same target as the Newtonian reference.
Now with mutual geometry: planet's gamma slightly warps edges near it,
which the moon responds to. Hierarchical gravity from one local rule.

## Parameters

| Parameter | Starting Value | Notes |
|-----------|---------------|-------|
| side | 80 | Same as v13 |
| H | 0.001 | Start small, increase if edges barely grow |
| alpha | 1.0 | Suppression strength |
| deposit_strength | proportional to mass | Star deposits more |
| spread_alpha | 1/k | Standard diffusion rate |
| formation_ticks | 20000 | Longer — need gamma to reach steady state |
| commit_mass | proportional to mass | Heavy = slow commit |

### No gradient_coupling

There is no gradient_coupling parameter. The coupling comes from:
- Edge asymmetry strength (from gamma profile)
- Frame rotation magnitude (from edge ratios at neighboring nodes)
- Both set by H and alpha — the expansion physics

If orbits require a separate coupling constant, the theory is wrong.

## The Full Chain

```
Entity deposits gamma at its node
  → Gamma spreads through graph (diffusion, 1/r profile)
  → Edges grow: de/dt = H / (1 + α(γ_A + γ_B))
  → Edges near mass stay short, far edges grow long
  → Body hops "forward" (Bresenham, commit cycle)
  → At new node: local frame rotated by edge asymmetry
  → "Forward" now points slightly toward mass
  → Over many hops: orbit emerges

No forces. No gradient reading. No coupling parameter.
Just deposit, spread, expand, hop, rotate frame. Repeat.
```

## Connection to v13 Results

v13 proved the bottom half works: hand-set Schwarzschild edges + frame
rotation = bound orbits. v14 tests the top half: does gamma deposit +
spread + two-endpoint expansion PRODUCE the right edge profile?

If yes: the full chain works. Gravity from one local rule.
If no: the gamma-to-edge-profile mapping is wrong and Result 6 needs revision.

## File Structure

```
experiments/64_109_three_body_tree/
├── v13/                           (pathfinder — proved frame rotation binds)
│   ├── experiment_description.md
│   ├── cascade_update.md
│   ├── test_k26_geodesic.py
│   └── macro_bodies.py
├── v14/                           (this experiment)
│   ├── experiment_description.md  (this file)
│   └── macro_bodies.py            (build from v13 base)
└── 170_entity_vortex_theory.md    (the theory)
```

## Success Criteria

- **PASS**: Emergent edge profile from gamma produces bound orbit (r > 5)
- **STRONG PASS**: Two equal masses orbit their center of mass
- **EXCEPTIONAL**: Three-body hierarchy matches Newtonian reference
- **FAIL**: Emergent edge profile too weak/wrong shape for frame rotation to bind
