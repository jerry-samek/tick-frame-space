# v10 Theory Notes — From Claude.ai Discussion (Feb 20, 2026)

## Why Orbits Are Chaotic: The Missing Physics

All parameter sweeps produce chaotic scattering (range 2.8-41, 50-80 reversals) regardless
of coupling, G, separation, or formation ticks. This is NOT a parameter problem. It's structural.

### Root Cause: Uniform Lattice + Constant Speed

The model has v = c/M always. Force only changes direction, never speed. In Newton, orbits
are stable because kinetic energy converts to/from potential energy — bodies speed up falling
in, slow down climbing out. This creates a restoring force for radial perturbations.

With constant speed on a uniform lattice, there is NO restoring mechanism. A small inward
perturbation doesn't speed the body up, so there's no increased centrifugal force to push
it back out. Orbit is neutrally unstable at best.

### The Fix: Variable Edge Length (Non-Uniform Lattice)

The key insight: **the entity always hops at c/M. But each hop covers different physical
distance depending on local gamma density.**

- Near mass: gamma well is deep → expansion is suppressed → edges are shorter → same hop
  rate but less physical distance per hop → from outside, body appears to "slow down"
- Far from mass: full expansion → edges are longer → same hop rate covers more distance →
  body appears to "speed up"

This is gravitational length contraction (GR). The planet isn't faster at periapsis. Space
is denser there. The constant-speed walk takes you through more spatial distance when the
grid is compressed.

**Implementation**: edge_length(node) = base_length × (1 + H)^t / (1 + gamma_factor × local_gamma)

- H is expansion rate (stretches all edges each tick)
- local_gamma suppresses expansion locally (mass curves space)
- Far from mass: edge grows normally → long edges → big hops
- Near mass: gamma suppresses growth → short edges → small hops
- The ratio creates apparent speed variation from constant hop rate

### Speed Is a Vector, Not a Scalar

The body's hop direction is the vector sum of:
1. **Connector vector**: where the gamma gradient pulls (radial, toward mass)
2. **Natural movement vector**: where the entity's internal_direction points (tangential)

Both compete for the same constant-speed budget (c/M). Near mass, gradient is strong →
more of the speed goes radial → tangential shrinks. Far from mass, gradient is weak →
speed stays tangential.

**The body never speeds up or slows down. The speed rotates between radial and tangential.**

This IS angular momentum conservation: tangential_v × r ≈ constant. Near mass: small
tangential but small r. Far: large tangential but large r.

### Diagnostic to Add

Plot radial vs tangential components of hop direction over time. If they oscillate out of
phase (radial peaks when tangential troughs), the orbital mechanics are present even if the
raw distance plot looks chaotic.

### Force Law Result (Already Measured)

The gradient exponent in different radial bins:
- Near field (r=3-20): n ≈ 2.2 (close to Newton's 2.0, excess is lattice anisotropy)
- Far field (r>20): n ≈ 3.5 (propagation horizon — gamma hasn't arrived yet)
- G only scales magnitude, doesn't change shape

### Mass Growth (Secondary Effect)

Body absorbs gamma from the well it passes through. Near mass: more absorption → heavier →
slower → turns harder → swings out. Far from mass: less absorption → lighter → faster →
turns less. Creates mass-speed feedback loop that could help stabilize orbits.

Not essential for first attempt. Try variable edge length first.

### Expansion Is Essential

Without expansion, lattice is uniform, every hop is identical length everywhere, no geometry
variation, no apparent speed difference. WITH expansion suppressed near mass, the lattice
breathes — dense near well, stretched far away. Kepler emerges from geometry, not force.

### Priority for Implementation

1. Variable edge length based on local gamma (highest priority — this enables orbits)
2. Track radial vs tangential velocity components (diagnostic)
3. Graph expansion with H parameter (enables cosmological effects)
4. Mass growth from gamma absorption (secondary stabilization)
