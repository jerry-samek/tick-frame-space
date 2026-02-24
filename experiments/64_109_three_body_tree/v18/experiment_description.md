# v18: Self-Sustaining Gravity — Radiation vs Expansion

## Date: February 25, 2026
## Status: Design for Code

## What v17 Taught Us

Every regime at G=0 failed for a different reason:

| Regime | Problem |
|--------|---------|
| Fossil (low deposit) | Formation gradient disperses. Orbit dies slowly. |
| Eddington peak (medium deposit) | Self-blinding. Gamma accumulates, gradient drowns. |
| Radiation (any deposit + mass loss) | Mass dies instantly. Dark inertial coasting. |
| G=1.0 | Gradient preserved but collapsed to spike. Bodies merge. |
| G=10.0 | Gradient too narrow. Bodies can't feel it at orbital distance. |

The fundamental tension: something must MAINTAIN the gradient against expansion.
G > 0 was us adding a third knob. But the model only has two mechanisms:

1. **Expansion** — edges grow, dilutes gamma outward
2. **Radiation** — entity deposits gamma, creates the field

Nothing else is allowed. The answer is in the balance of these two alone.

## The v18 Hypothesis

The entity builds and maintains its own gravitational field in real time.
No formation well. No fossil gamma. No G. Just: deposit and expand.

**Near the entity:** fresh deposits every tick. Gamma high.
**Far from entity:** expansion has been diluting deposits for many ticks. Gamma low.
**Result:** steady-state 1/r profile from the balance of source vs dilution.

This is a LIVING gradient. Not a fossil. Not self-gravitating. Just: the entity
keeps pumping gamma into its local node, expansion keeps carrying it away. The
profile is the wake of a continuous source in an expanding medium.

**With mass loss:** the entity can't self-blind because it loses mass as it deposits.
Deposit creates the field. Mass loss limits the source. Expansion dilutes the far
field. Three effects, two mechanisms, one steady state.

## The Key Insight: No Formation Phase

Previous versions used 10K ticks of strong external deposits to build a gamma well
BEFORE dynamics started. The entity then orbited in this pre-built field. That's
artificial — like building a mountain and then watching a ball roll on it.

v18 has NO formation phase. Both bodies start on a blank graph. They deposit gamma
from tick 1. The field builds itself. The gradient emerges. The orbit forms as the
field forms. Everything is self-consistent from the start.

This is how the real universe works. Stars don't form in pre-built gravitational
wells. The matter condenses, the field builds as the matter concentrates, the
orbits form as the field forms. Self-consistent from the start.

## Architecture

### Graph
Same random geometric graph as v17:
- N=30000, k=12, radius=30, seed=42
- All edges start at Euclidean distance (no pre-expansion)

### Edge growth
Same two-endpoint rule:
```
growth = H / (1 + alpha * (gamma_A + gamma_B))
edge_length += growth
```

### Entity
Same v17 entity with velocity/displacement, BUT:
- No formation phase deposits
- Entity deposits from tick 1
- Mass loss ON by default (self.mass -= deposited each tick)
- deposit_rate is THE parameter to tune

### The Balance Equation

At steady state, the gradient must satisfy:
- Gamma deposited per tick at entity node = gamma lost per tick to diffusion + expansion
- deposit_rate * mass = diffusion_outflow + expansion_dilution

If deposit_rate too low: diffusion wins, gradient disperses, no gravity.
If deposit_rate too high: mass dies fast, gravity is transient burst.
Sweet spot: mass survives long enough to complete multiple orbits while
maintaining a gradient that reaches orbital distance.

### Mass Half-Life Constraint

For the orbit to work, mass must survive for at least ~10 orbital periods.
If one orbit takes ~5000 ticks (rough estimate from v17 arc), we need
mass half-life > 50,000 ticks.

half_life = ln(2) / deposit_rate ≈ 0.693 / deposit_rate

| deposit_rate | half_life | mass at 50K ticks |
|-------------|-----------|-------------------|
| 0.001 | 693 | ~0 (dead) |
| 0.0001 | 6,932 | ~0.07% (dead) |
| 0.00001 | 69,315 | ~49% (alive!) |
| 0.000001 | 693,147 | ~93% (barely touched) |

**deposit_rate ~ 0.00001** gives half-life ~70K ticks. Mass survives 50K ticks
at ~50%. But does it deposit enough gamma per tick to maintain a gradient?

At mass=1000, deposit = 1000 * 0.00001 = 0.01 gamma/tick.
Over 1000 ticks, that's 10 gamma deposited. Is that enough?

Compare to v17 formation: deposited 1.0 * 10000 = 10000 gamma per body.
v18 at 0.00001 deposits 0.01/tick... would take 1M ticks to match formation.
That's too slow. The gradient won't form before the orbit needs it.

### The Resolution: Higher Mass

If deposit_rate must be low (for survival) but total deposit must be high
(for gradient), increase mass.

mass=100000, deposit_rate=0.00001:
- deposit = 100000 * 0.00001 = 1.0 gamma/tick (same as v17 formation!)
- half_life = 69,315 ticks (plenty of time)
- mass at 50K ticks: ~49,000 (still strong)

OR mass=10000, deposit_rate=0.0001:
- deposit = 10000 * 0.0001 = 1.0 gamma/tick
- half_life = 6,932 ticks (marginal — 7 half-lives in 50K)
- mass at 50K ticks: ~7 (dying but not dead)

The first option is better. High mass, low deposit_rate.

### Alternative: Separate Deposit and Mass Loss Rates

Maybe the entity deposits at one rate but loses mass at a different rate.
Physical justification: not all deposited gamma comes from mass conversion.
Some comes from converting kinetic energy, some from internal state changes.
The entity is more complex than a simple mass-to-gamma converter.

BUT: this adds a knob. Tom's rule: only expansion and radiation. Keep it
simple. One deposit_rate, one mass loss rate, same number.

## Implementation

### Changes from v17

1. **Remove formation phase entirely.** No --formation-ticks, no --formation-deposit.
   The graph starts blank. Entities deposit from tick 1.

2. **Warm-up period.** First N ticks: entities deposit and gamma spreads, but
   entities don't move (velocity/displacement frozen). This lets the gamma
   field build to a quasi-steady state before dynamics begin. Entities are
   still losing mass during warm-up. This is NOT the same as formation — the
   entity is doing it with its own mass, not external magic deposits.

   Alternative: no warm-up at all. Entities move from tick 1. The orbit
   forms as the field forms. Messier but more honest.

   **Recommendation: try both. --warm-up 5000 and --warm-up 0.**

3. **G=0 always.** Remove --G from CLI or fix at 0.

4. **Mass loss ON by default.** --no-mass-loss disables for comparison.

5. **Higher default mass.** --binary-mass default 100000.

6. **Inertia scales with mass.** inertia = mass (not constant). As mass
   decreases from radiation, entity becomes more responsive to nudges.
   Lighter = faster. This is physical — a dying star's remnant responds
   more strongly to external gravity.

   WAIT: if inertia = mass and mass decreases, acceleration = force/mass
   increases over time. That might cause velocity to GROW as mass drops.
   Could compensate Hubble drag naturally.

   Test both: inertia = initial_mass (constant) and inertia = current_mass.

### Diagnostics

For each run, log:
- Gamma at entity's node and at r=5, r=10, r=20 (does gradient reach?)
- Gradient magnitude at planet distance (is there force?)
- mass(t) curve
- velocity(t) curve
- deposit/tick vs diffusion_loss/tick at entity node (balance check)

### Phases

**Phase 0: Gradient Formation Test**
Single massive body, no partner. mass=100000, deposit_rate=0.00001.
Does the gamma profile reach 1/r at orbital distances (r=10-20)?
How many ticks to reach quasi-steady state?
Plot gamma vs distance at t=1000, 5000, 10000, 50000.

**Phase 1: Star-Planet**
Star: mass=100000, deposit_rate=0.00001 (stationary)
Planet: mass=1, inertia=1, tangential_momentum=0.1
separation=10
No warm-up. Both deposit from tick 1.
Does the planet orbit as the star's field builds?

**Phase 2: Equal Mass Binary**
Both: mass=100000, deposit_rate=0.00001
Opposing tangential momentum=0.1
separation=10
No warm-up. Both build fields simultaneously.
The acid test: do they orbit their center of mass while building their
own gravity in real time?

**Phase 3: Parameter Sweep**
Sweep deposit_rate at fixed mass=100000:
0.000001, 0.000005, 0.00001, 0.00005, 0.0001
For each: 50K ticks, log velocity at end, reversals, gradient shape.
Find the sweet spot: strong enough gradient, slow enough mass loss.

## Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| N | 30000 | Graph nodes |
| k | 12 | Neighbors per node |
| radius | 30 | Graph radius |
| H | 0.01 | Expansion rate |
| G | 0.0 | ALWAYS ZERO. Not a parameter. |
| binary-mass | 100000 | High mass for low deposit_rate |
| deposit-strength | 0.00001 | Entity radiation rate |
| inertia | mass | Decreases with mass loss |
| warm-up | 0 | Ticks before dynamics (0 = fully self-consistent) |
| tangential-momentum | 0.1 | Initial kick |
| separation | 10 | Starting distance |
| ticks | 50000 | Dynamics duration |

## CLI

```bash
# Phase 0: Does gradient form?
python -u v18/macro_bodies.py --phase0 --n-nodes 30000 --k 12 --radius 30 \
  --H 0.01 --binary-mass 100000 --deposit-strength 0.00001 --ticks 50000

# Phase 1: Star-Planet
python -u v18/macro_bodies.py --phase1 --n-nodes 30000 --k 12 --radius 30 \
  --H 0.01 --star-mass 100000 --planet-mass 1 --deposit-strength 0.00001 \
  --tangential-momentum 0.1 --separation 10 --ticks 50000

# Phase 2: Equal mass binary (THE test)
python -u v18/macro_bodies.py --phase2 --n-nodes 30000 --k 12 --radius 30 \
  --H 0.01 --binary-mass 100000 --deposit-strength 0.00001 \
  --tangential-momentum 0.1 --separation 10 --ticks 50000

# Phase 3: deposit_rate sweep
python -u v18/macro_bodies.py --sweep-deposit --n-nodes 30000 --k 12 --radius 30 \
  --H 0.01 --binary-mass 100000 --tangential-momentum 0.1 --separation 10 \
  --ticks 50000
```

## The Prediction

With mass=100000 and deposit_rate=0.00001:
- Each tick: 1.0 gamma deposited at entity's node
- Gamma diffuses outward, expansion carries it further
- Steady state: gamma ~ deposit_rate * mass / (diffusion_rate * r) near entity
- Half-life: ~70K ticks. Mass at 50K: ~49,000. Still depositing 0.49/tick.
- The gradient should be strong enough at r=10 to produce orbital dynamics
- The orbit should sustain itself because the field is continuously maintained

If this works: gravity is self-sustaining from radiation alone. No formation.
No fossil. No G. No pre-built wells. Just an entity existing on a graph,
depositing gamma because it exists, losing mass because it deposits,
creating a gravitational field because expansion carries the gamma away
asymmetrically.

Existence → radiation → gradient → gravity → orbits. From nothing but
expansion and deposit. Two mechanisms. One rule.

## File Structure

```
v18/
  experiment_description.md  (this file)
  macro_bodies.py            (copy v17 graph + entity, remove formation, add warm-up)
  results/
```

## Reminder for Code

1. NO FORMATION PHASE. Entities build their own field from tick 1.
2. G=0 always. Self-gravitation is not a mechanism in this model.
3. Mass loss ON by default. The entity pays for its own gravity.
4. Start with Phase 0 — verify the gradient forms before testing orbits.
5. If gradient doesn't reach r=10 by tick 10000, increase mass or deposit_rate.
6. The two mechanisms are expansion and radiation. Nothing else.
