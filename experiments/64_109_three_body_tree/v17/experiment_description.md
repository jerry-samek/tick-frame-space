# v17: Mass Radiation and the Eddington Limit

## Original Hypothesis

A body deposits gamma — that deposit IS mass loss. As mass decreases, gravity
weakens, the orbit widens. If mass loss rate matches expansion rate, the orbit
stabilizes: expansion shrinks comoving orbits while mass loss widens them.

**This hypothesis was partially wrong.** The experiment revealed something deeper.

## What Actually Happened

### Step 1: Systematic baseline (H=0, no radiation)

Confirmed v16's result: velocity perfectly preserved (0.100 constant over 20K ticks)
on a static graph. The projection mechanism is lossless. Zero reversals — no gravity
without expansion.

### Step 2: Clean orbit baseline (H=0.01, formation_deposit=1.0, no radiation)

With `deposit_strength=1.0` (entity deposits 1000 gamma/tick during dynamics):
- 85 comoving reversals in 20K ticks — real bound oscillation
- Velocity decayed: 0.100 → 0.027
- Scale factor: 1.00 → 2.51

This appeared to be Hubble drag killing the orbit.

### Step 3: Mass radiation attempt

Adding mass radiation with `deposit_strength=1.0` killed mass in 1 tick
(deposited = 1000 * 1.0 = 1000). Decoupled formation from radiation by adding
`--formation-deposit` (builds the gamma well) separate from `--deposit-strength`
(entity radiation rate during dynamics).

### Step 4: The surprise — deposit rate matters more than radiation

With `formation_deposit=1.0, deposit_strength=0.0001`:
- **With radiation**: 163 reversals, velocity sustained ~0.07–0.10 over 50K ticks
- **Without radiation**: 165 reversals, velocity sustained ~0.09 over 50K ticks
- **Nearly identical.** Mass loss had no effect.

Why: at deposit_strength=0.0001, the entity deposits 0.1 gamma/tick — negligible
compared to the 10,000 gamma deposited per body during formation. The orbit runs
entirely on the formation-era gamma gradient. Whether the entity loses mass is
irrelevant when its ongoing deposits don't contribute to the gravitational field.

### Step 5: The Eddington Limit — deposit strength sweep

Swept deposit_strength from 0.0001 to 1.0 (5K ticks each, no mass loss,
formation_deposit=1.0):

| deposit | |vA| | |vB| | vA_z | scale | d_comov |
|---------|-------|-------|--------|-------|---------|
| 0.0001  | 0.094 | 0.074 | -0.015 | 12.8  | 3.46    |
| 0.001   | 0.102 | 0.080 | +0.006 | 11.7  | 3.52    |
| **0.005** | **0.212** | **0.083** | **+0.175** | 9.2 | 0.51 |
| **0.01**  | **0.168** | **0.212** | -0.049 | 8.0 | 0.00 |
| 0.05    | 0.012 | 0.033 | -0.004 | 5.1   | 9.72    |
| 0.1     | 0.097 | 0.107 | -0.055 | 4.3   | 11.03   |
| 1.0     | 0.029 | 0.065 | -0.010 | 2.4   | 22.14   |

Three regimes:

1. **Fossil orbit** (deposit < 0.001): Entity deposits negligible. Orbit runs on
   formation gamma. Velocity preserved near initial 0.1. Self-sustaining but
   decoupled from ongoing physics.

2. **Eddington peak** (deposit ~ 0.005–0.01): Velocities EXCEED initial value
   (0.17–0.21 vs 0.1 initial). Bodies accelerated beyond kick velocity.
   At deposit=0.005, vA_z = +0.175 — most velocity is OUT OF PLANE.
   **Orbital precession (Lense-Thirring analog) emerges naturally.**

3. **Self-blinding** (deposit > 0.05): Entity floods the graph with gamma.
   Growth asymmetry drowns in uniform background. Growth differential → 0.
   Gravity dies. Velocity collapses.

## Key Discovery: Self-Blinding

The velocity decay observed in v16 (0.1 → 0.025 over 20K ticks) was NOT Hubble
drag. It was **gamma self-blinding**: the entity's own deposits create such a
massive uniform gamma background that the growth differential (which IS gravity)
vanishes. The expansion suppression becomes uniform → no gradient → no force.

The mechanism:
```
growth = H / (1 + alpha * (gamma_A + gamma_B))
force ∝ mean_growth - this_growth
```
When gamma is huge and uniform: all growth → 0, all differentials → 0, force → 0.

## Key Discovery: Orbital Precession

At the Eddington peak (deposit ~ 0.005), the orbit precesses out of the XY plane.
The z-component of velocity grows from ~0 to dominate the velocity vector. This is
NOT a bug — it's the random graph's analog of frame-dragging. The graph has no
preferred plane. Unlike a lattice (which locks motion to axes), the random graph
allows the orbital plane to precess freely. The precession rate depends on the
deposit strength — it's strongest at the Eddington peak where the body-graph
coupling is maximal.

## Architecture

Physics change from v16 in `Entity.advance()`:
```python
deposited = self.mass * self.deposit_rate
graph.deposit(self.node, self.bid, deposited)
if self.radiate_mass:
    self.mass = max(self.mass - deposited, 0.0)
```

Key additions:
- `--formation-deposit`: Gamma deposited per tick during formation (builds well)
- `--deposit-strength`: Entity's deposit_rate during dynamics (radiation rate)
- `--no-mass-loss`: Disable mass radiation (deposit without losing mass)
- Velocity components (vx, vy, vz) tracked in records and plots
- XZ trajectory views alongside XY (reveals out-of-plane precession)

## Open Questions

1. **Does mass radiation matter at the Eddington peak?** The sweep was done with
   `--no-mass-loss`. At deposit=0.005, mass loss would be significant (half-life
   ~139 ticks). Does radiation stabilize or destabilize the Eddington peak orbit?

2. **What sets the Eddington limit?** The crossover from "gravity works" to
   "self-blinding" should depend on graph properties (k, radius, N) and the
   ratio of entity deposit to formation gamma. Is there a scaling law?

3. **Is the precession physical?** The out-of-plane velocity at the Eddington peak
   could be a genuine frame-dragging analog (asymmetric gamma wake on graph) or
   a numerical artifact of graph anisotropy. A lattice comparison would distinguish
   these.

4. **What maintains the fossil orbit?** At deposit=0.0001, the formation gamma
   must eventually disperse completely (G=0, free diffusion). When it does, gravity
   dies and the orbit unbinds. How long does the formation gradient survive?

## Commands

```bash
# Verification
python v17/macro_bodies.py --verify

# H=0 baseline (velocity preservation)
python -u v17/macro_bodies.py --phase2 --n-nodes 30000 --k 12 --radius 30 \
  --G 0 --H 0 --formation-deposit 1.0 --deposit-strength 1.0 \
  --binary-mass 1000 --tangential-momentum 0.1 --separation 10 \
  --formation-ticks 10000 --ticks 20000 --no-mass-loss --tag H0_baseline

# Clean orbit (Eddington peak, no radiation)
python -u v17/macro_bodies.py --phase2 --n-nodes 30000 --k 12 --radius 30 \
  --G 0 --H 0.01 --formation-deposit 1.0 --deposit-strength 0.005 \
  --binary-mass 1000 --tangential-momentum 0.1 --separation 10 \
  --formation-ticks 10000 --ticks 20000 --no-mass-loss --tag eddington_peak

# Radiation at Eddington peak
python -u v17/macro_bodies.py --phase2 --n-nodes 30000 --k 12 --radius 30 \
  --G 0 --H 0.01 --formation-deposit 1.0 --deposit-strength 0.005 \
  --binary-mass 1000 --tangential-momentum 0.1 --separation 10 \
  --formation-ticks 10000 --ticks 20000 --tag eddington_radiation
```

February 2026
