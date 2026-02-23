# v17 Context Update: Formation vs Radiation + The Equalization Principle

## For Code — from Tom and Claude.ai's discussion, February 23, 2026

## The Decoupling

Formation and radiation are physically different processes:

**Formation** = the body already existed for billions of ticks before the
simulation starts. Its gamma field is at steady state. The well is deep
and extended. This is the HISTORY of the body — all the gamma it deposited
over its lifetime, diffused into a 1/r profile. Formation deposits should
be strong (1.0) and run for many ticks to simulate this deep history.

**Radiation** = the body's ongoing mass loss during the simulation. Each tick
it deposits a tiny amount of gamma (creating/maintaining its field) and loses
that mass. This is slow — stars radiate for billions of years. The Sun loses
4 million tons/second but has 2×10^30 kg. That's deposit_rate ~ 10^-21 per
tick equivalent. We don't need it THAT slow, but 0.0001 (half-life ~7000
ticks) is more physical than 0.001 (half-life ~693 ticks).

**Implementation:**
```
--formation-deposit 1.0    # strong, builds deep well in 10K ticks
--deposit-strength 0.0001  # weak, entity radiates slowly during dynamics
```

Formation loop uses formation_deposit directly (as it does now).
Entity.__init__ sets self.deposit_rate = deposit_strength.
Entity.advance deposits self.mass * self.deposit_rate and subtracts from mass.

## The Physics: Why Radiation Exists

Tom's insight from today: gravity and radiation are the same mechanism running
in opposite directions.

The entity sits at a node with k connectors. Each connector has a growth rate.
The universe wants to EQUALIZE — fill deficits, drain surpluses.

- **Connector with LEAST growth** = deficit = entity moves toward it = GRAVITY
- **Connector with MOST growth** = surplus = entity sheds gamma there = RADIATION

Same equalization principle, opposite direction. The entity absorbs from the
minimum and emits toward the maximum. Not two mechanisms. One rule: balance
the books.

This means:
1. A stationary mass in a symmetric field barely radiates (all connectors similar)
2. An accelerating mass has sharp min/max asymmetry → strong radiation
3. An orbiting binary constantly accelerates → gravitational wave emission
4. This is why LIGO detects orbital decay — the binary radiates energy because
   the acceleration creates connector surplus that gets shed

## The Beautiful Arc

The best trajectory plot so far came from:
- N=30K, k=12, r=30
- H=0.01
- deposit_strength=1.0 (constant mass, no radiation)
- formation_ticks=10K
- dynamics_ticks=20K

Two smooth arcs, nearly circular, opposite sides of center of mass.
Half an orbit. Needs more ticks to close.

**Priority: let this configuration run to 50-100K ticks and see if the
arc closes into a full orbit.** This is the no-radiation baseline. The
proof that the mechanism works. Everything else (radiation, mass loss,
Hubble compensation) comes after.

## The Tension: Expansion vs Gravity

Every run so far fights the same battle:

- **H too high** → edges stretch → hops stall → orbit freezes
- **H too low** → gamma field weak → no binding → escape
- **H = 0** → no growth asymmetry → no gravity at all

The sweet spot is where expansion creates enough asymmetry for binding but
doesn't stretch edges so fast that bodies can't keep up. This is the Jeans
criterion in the model — the balance between gravitational binding energy
and expansion energy.

With deposit_strength=1.0 and H=0.01, the scale factor reached only 2.5
in 20K ticks — gentle expansion, strong field suppression. That's the
sweet spot. The arc was smooth because the bodies had time to orbit before
expansion mattered.

With deposit_strength=0.001 and H=0.01, scale factor hit 58 — runaway
expansion because the gamma field was too weak to suppress edge growth.
More reversals (104) but messier because the bodies were fighting a losing
battle against expansion.

## Recommended Run Order

1. **Baseline (no radiation):** formation-deposit=1.0, deposit-strength=1.0,
   H=0.01, 50K ticks. Constant mass. Does the arc close? This is THE test.

2. **Slow radiation:** formation-deposit=1.0, deposit-strength=0.0001,
   H=0.01, 50K ticks. Mass half-life ~7000 ticks. Mass at 50K ticks:
   1000 * 0.9999^50000 ≈ 7. Still alive but fading. Compare orbit shape
   to baseline.

3. **Medium radiation:** formation-deposit=1.0, deposit-strength=0.001,
   H=0.01, 20K ticks. Mass dies by tick 8K. Watch what happens when
   gravity turns off mid-orbit. Bodies should go inertial — straight line
   in comoving coordinates after mass hits zero.

4. **Calibration:** Find the deposit_strength where mass loss exactly
   compensates Hubble drag. Theory predicts M(t) ~ M₀/a(t). If
   a(t) reaches 2.5 in 20K ticks, mass should be ~400 at that point.
   That's deposit_rate where 1000 * (1-rate)^20000 = 400 → rate ≈ 0.0000458.

## The Deeper Principle

The entity doesn't have two operations (absorb + emit). It has one:
equalize. It reads its connectors and moves gamma from surplus to deficit.
Its own mass IS the gamma it carries. Depositing gamma IS losing mass.
The gravitational field IS the radiated mass spread through the graph.

There is no stored "mass" separate from "gamma." The mass IS concentrated
gamma at one node. When it spreads, the entity gets lighter. When it
concentrates, the entity gets heavier. Mass, energy, gravity, radiation —
all the same thing: gamma distribution on the graph.

`self.mass -= deposited` isn't a separate mechanism. It's bookkeeping for
what already happened. The gamma left the entity's node. The entity IS
lighter now. The line just makes the ledger honest.
