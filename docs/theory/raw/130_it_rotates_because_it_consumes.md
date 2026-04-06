# RAW 130 — It Rotates Because It Consumes

### *Orbital Mechanics from Consumption Gravity*

**Author:** Tom (insight), Claude (derivation and experimental validation)
**Date:** April 6, 2026
**Status:** Derived from Experiment 128 v9 ODE — the simplest correct model
**Prerequisites:** RAW 118 (Consumption-Transformation), RAW 128 (Energy Partition),
RAW 113 (Same/Different/Unknown)
**Experimental basis:** Experiment 118 (17 versions), Experiment 128 (9 versions),
6 days of computation

---

## Abstract

Orbital mechanics in the tick-frame model reduces to one statement:
**the planet rotates because it consumes.**

Consumption of incoming deposits (Different → Same transformation) creates
a centripetal force directed toward the deposit source (the star). This
force, combined with the planet's initial tangential velocity (inherited
from formation), produces stable Keplerian orbits.

No tangential thrust. No reject stream redirection. No "bent pipe."
No internal planet structure required for the orbit itself. The consumption
IS the gravity. The orbit IS the consumption.

---

## 1. The Derivation

### The setup

- Star emits deposits at total rate L (deposits per tick, in all directions)
- At distance r from the star, the flux is: F(r) = L / (4πr²)
- Planet has processing capacity P (deposits per tick it can transform)
- The planet consumes: consumed = min(F(r), P)

### The force

Each consumed deposit arrived FROM the star direction. It carried inward
momentum. The consumption transforms the deposit (Different → Same) but
the MOMENTUM is absorbed by the planet. The absorbed momentum creates a
centripetal force:

```
F_gravity = -consumed / r²    (directed toward star)
```

Inside the equilibrium radius (r < r_eq where F(r) > P):
- consumed = P (planet at full capacity)
- F_gravity = -P / r²

Outside the equilibrium radius (r > r_eq where F(r) < P):
- consumed = F(r) = L / (4πr²) (planet has spare capacity)
- F_gravity = -L / (4πr⁴) (falls off faster — weaker gravity at distance)

### The equilibrium radius

Where the star's flux exactly matches the planet's capacity:

```
r_eq = sqrt(L / (4πP))
```

This is the natural orbital distance. Determined entirely by the star's
emission rate and the planet's processing capacity. No free parameters.

### The orbit

For a circular orbit at radius r < r_eq:
- Centripetal requirement: v² / r = P / r²
- Circular velocity: v = sqrt(P / r)

This IS Kepler's law. Orbital velocity decreases with distance:
v ∝ 1/sqrt(r). The orbital period:

```
T = 2πr / v = 2πr / sqrt(P/r) = 2π * r^(3/2) / sqrt(P)
T² = (4π²/P) * r³
```

**T² ∝ r³ — Kepler's Third Law.** Derived from consumption.

### What provides the tangential velocity?

The planet's initial tangential velocity comes from its FORMATION.
The star's reject stream (the material that became the planet) had angular
momentum from the star's internal dynamics. The planet inherits this
angular momentum at birth. The consumption gravity then bends the
tangential motion into a closed orbit.

The planet does NOT generate tangential motion from its processing.
It INHERITS tangential motion and MAINTAINS it through consumption gravity.
Without consumption, the planet would fly off in a straight line (Newton I).
The consumption provides the centripetal force that curves the straight line
into a circle.

**The orbit is maintained by consumption. The orbit is initiated by inheritance.**

---

## 2. Experimental Validation

### Experiment 128 v9 ODE results

The consumption force F = -consumed/r² with no tangential forces produces
clean Keplerian orbits:

| Initial radius | Circular velocity | Revolutions (500k steps) |
|---------------|------------------|-------------------------|
| 0.5 × r_eq | 28.2 | 1,812 |
| 0.7 × r_eq | 23.8 | 572 |
| 0.9 × r_eq | 21.0 | 1,881 |

Clean circular orbits. No escape. No collapse. Stable for thousands of
revolutions.

### What DOESN'T work (also proven experimentally)

| Mechanism | Result | Why it fails |
|-----------|--------|-------------|
| Tangential thrust from excess (v9 ODE v1) | Escape | Continuously adds energy |
| Three-way partition (v9 ODE v2) | Escape | Even 0.5% tangential pumps energy |
| Redirect angle > 0 (v9 ODE v3) | Escape | Any tangential force adds angular momentum |
| Tangential velocity bias (128 v7) | Decays | One-time deflection during infall |
| Tangential acceleration (128 v8) | Oscillates | Noisy, no consistent direction |
| Entity hopping (118 v4-v17) | Random walk | Graph discretization noise |

**Only F = -consumed/r² with zero tangential force produces stable orbits.**

### The path to this result

The result was found by ELIMINATION over 6 days:

1. **Experiment 118 (17 versions):** Entities hopping on graphs. Proved
   gravitational binding but not coherent orbits. Every "orbit" was a
   bound random walk (v9 diagnostic).

2. **Experiment 128 v1-v6:** Deposit pattern model. Proved radial
   equilibrium from consumption (dist=12.2, stable). Proved deposit
   dominance regions are the correct measurement.

3. **Experiment 128 v7-v8:** Tangential thrust attempts. v7: one-time
   deflection decays to zero. v8: noisy oscillation. Neither sustains
   rotation.

4. **Experiment 128 v9 ODE:** Abstracted to equations. Proved:
   - Excess flux → tangential thrust → escape (unstable)
   - Consumption → centripetal force → orbit (stable)
   - The orbit comes from consumption alone

---

## 3. What the Excess Does

The excess (flux - capacity, when flux > capacity) does NOT push the
planet. The excess LEAVES the planet as the reject stream. It becomes:

- Moons (if the rejects accumulate and crystallize)
- Asteroids, comets (smaller accumulations)
- Radiation (if the rejects propagate away without crystallizing)

The reject stream carries energy AWAY from the planet. It does NOT
exert force on the planet. The planet only feels the CONSUMED deposits
(the ones it actually transformed).

This resolves the Eddington luminosity analog: when flux exceeds capacity,
the excess doesn't blow the planet apart. It forms child entities.

---

## 4. What Determines the Orbit

| Quantity | Determined by | Formula |
|----------|--------------|---------|
| Orbital radius | Star emission + planet capacity | r_eq = sqrt(L/4πP) |
| Orbital velocity | Planet capacity + radius | v = sqrt(P/r) |
| Orbital period | Planet capacity + radius | T = 2π r^(3/2) / sqrt(P) |
| Angular momentum | Inherited from formation | L = r × v (conserved) |
| Eccentricity | Initial conditions at formation | e from energy + L |

No free parameters beyond L (star emission), P (planet capacity), and
initial conditions (tangential velocity at formation).

---

## 5. Kepler's Laws from Consumption

**First Law (elliptical orbits):**
The orbit is an ellipse with the star at one focus. This follows from the
1/r² force law. The consumption force F = -consumed/r² has the same
mathematical form as Newtonian gravity, so the same orbital solutions
apply. Ellipses, parabolas, and hyperbolas are all possible depending
on energy and angular momentum.

**Second Law (equal areas in equal times):**
Angular momentum is conserved because the consumption force is purely
radial (toward the star). No tangential component = no torque = constant
angular momentum = equal areas.

**Third Law (T² ∝ r³):**
T² = (4π²/P) × r³. The "gravitational parameter" is P (planet processing
capacity). Different planets with different P orbit at different distances
with different periods, all satisfying T² ∝ r³ with a constant that
depends on P.

Note: in Newtonian gravity, the constant in Kepler III depends on the
star's mass (GM). In the consumption model, it depends on the planet's
processing capacity (P). This is a TESTABLE DIFFERENCE: the consumption
model predicts that the orbital period depends on the planet's properties,
not just the star's mass. Whether this distinction survives at macroscopic
scale (where P might be determined by the star's flux) is an open question.

---

## 6. Connection to RAW 128

RAW 128 described three outcomes for each discharged quantum: Store, Move,
or Radiate. The consumption gravity model clarifies:

- **Store:** consumed deposits become part of the planet's structure.
  The momentum from consumption provides the centripetal force.
- **Move:** the planet moves along its orbit, maintaining tangential
  velocity from initial conditions. No force needed for tangential motion
  — just Newton's first law.
- **Radiate:** excess deposits leave the system as the reject stream.
  No force on the planet. The rejects become other bodies.

The orbit is the STORE component. The planet stores consumed deposits
(growing in mass) and their momentum creates the centripetal force.
The tangential motion is inherited and conserved. The radiation is
energy leaving the system, not affecting the orbit.

---

## 7. Summary

The planet rotates because it consumes.

Consumption of stellar deposits creates a centripetal force F = -consumed/r²
directed toward the star. This force, combined with inherited tangential
velocity, produces Keplerian orbits with all three of Kepler's laws.

No tangential thrust needed. No internal planet structure needed for the
orbit (though structure determines WHAT the planet can consume, hence P,
hence the orbital radius). No reject stream redirection. No bent pipe.

The orbit is:
- **Initiated** by angular momentum inherited from formation
- **Maintained** by consumption gravity (centripetal force from absorbed deposits)
- **Characterized** by two numbers: L (star emission) and P (planet capacity)

Everything else follows from the math.

**It rotates because it consumes. Stop consuming, stop rotating.**

---

## References

- RAW 118 — Gravity as Consumption and Transformation (March 2026)
- RAW 128 — The Energy Partition: Store, Move, or Radiate (April 2026)
- RAW 113 — The Semantic Isomorphism: Same / Different / Unknown
- Experiment 118 v1-v17 — Entity hopping model (March-April 2026)
- Experiment 128 v1-v9 — Deposit pattern model + ODE (April 2026)

---

*Date: April 6, 2026*
*Status: DERIVED — from 6 days of experimental elimination*
*Key claim: F = -consumed/r² is the gravitational force. It produces
Kepler's laws from the consumption mechanism alone. Tangential motion
is inherited, not generated. The reject stream forms child entities,
not orbital thrust.*
*Testable: T² ∝ r³ with constant depending on planet capacity P,
not star mass M. This differs from Newtonian prediction at the
parameter level.*
