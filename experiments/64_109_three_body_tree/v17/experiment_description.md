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

## Overnight Runs (2M ticks, 30K nodes)

Five runs at 2M ticks revealed the long-term fate of each regime:

| Run | deposit | radiation | Final |v| | Reversals | Hops (A+B) | Scale |
|-----|---------|-----------|---------|-----------|------------|-------|
| fossil | 0.0001 | OFF | 0.03 | 316 | 83,075 | 1,053 |
| eddington_norad | 0.005 | OFF | 0.005 | 268 | 17,236 | 57 |
| eddington_rad | 0.005 | ON | 0.05–0.08 | 325 | 121,490 | 4,516 |
| dep01_norad | 0.01 | OFF | 0.004 | 246 | 15,928 | 57 |
| dep01_rad | 0.01 | ON | 0.06–0.09 | 334 | 119,944 | 4,516 |

**Key finding: The Eddington peak was a MIRAGE.**

At 5K ticks, deposit=0.005–0.01 showed the highest velocities (0.17–0.21).
At 2M ticks, these same values collapsed to 0.004–0.005. Self-blinding is slow
but inevitable with constant mass — gamma accumulates tick after tick until the
gradient drowns.

**Radiation runs (mass loss ON):** Mass dies quickly (half-life ~139 ticks at
deposit=0.005), then bodies become dark inertial objects — no deposits, no
gravity, no drag. Velocity sustained at 0.05–0.08 but no physics driving it.
More reversals (325–334) because dark bodies still diffuse on the graph.

**Fossil orbit (deposit=0.0001, no radiation):** Velocity decays 0.1→0.03 over
2M ticks. Formation gradient slowly disperses (G=0 = free diffusion). The orbit
IS dying, just slowly. Answer to Open Question 4: fossil gradients survive for
~1M ticks before becoming too weak to maintain velocity.

## G > 0 Exploration

G controls self-gravitating spread: `alpha_eff = alpha / (1 + G * |gamma|)`.
At G>0, high-gamma regions resist diffusion, preserving peaks.

### Initial tests (G=1.0, G=10.0)

| G | Result |
|-------|--------|
| 1.0 | Bodies merged by tick 15K. Well too deep. |
| 10.0 | Only 3 reversals, 39 hops. Gamma confined to narrow spike. |

### G Sweep (0.001–0.5, fossil setup, 50K ticks)

| G | Reversals | Final d | d_comov | |vA|/|vB| | Gamma r=1→5→10→20 | Peak γ |
|-------|-----------|---------|---------|----------|---------------------|--------|
| 0.001 | 151 | 48.2 | 0.45 | 0.05/0.09 | 1.55→1.05→1.03→1.00 | 2.0 |
| 0.01 | 163 | 32.8 | 0.31 | 0.09/0.08 | 1.16→1.03→1.00→1.02 | 2.1 |
| **0.1** | **219** | **8.2** | **0.08** | **0.06/0.08** | **1.48→1.33→1.22→1.08** | 2.9 |
| 0.3 | 122 | 0.0 | 0.00 | 10.2/10.3 | 5.86→1.50→1.01→0.69 | 6,148 |
| 0.5 | 98 | 6.7 | 0.04 | 0.84/0.48 | 2.69→1.17→0.79→0.50 | 8,568 |

**G=0.1 is the sweet spot:** 219 reversals (most), broad gradient from 1.48→1.08
across r=1–20, comoving distance tight at 0.08. The gradient reaches orbital
distance without collapsing to a spike.

Three G regimes:
1. **G ≤ 0.01**: Too weak. Gradient disperses flat. Equivalent to G=0.
2. **G = 0.1**: Goldilocks. Broad 1/r profile, gradient at orbital distances.
3. **G ≥ 0.3**: Catastrophic. Gamma peaks explode (6K–8.5K), bodies merge or trap.
   Note γ<1 at r=20 — the well steals gamma from surroundings.

**However:** G is a THIRD mechanism beyond expansion and radiation. v18 returns to
the fundamental question: can expansion + radiation alone sustain orbits?

## Conclusions

1. **Self-blinding** is the dominant failure mode at G=0. Any deposit rate that
   creates a useful gradient also eventually floods it.
2. **Mass radiation** prevents self-blinding (mass dies, deposits stop) but also
   kills gravity. Bodies go dark and coast.
3. **Fossil orbits** work for ~1M ticks but are not self-sustaining.
4. **G>0** can maintain gradients (G=0.1 optimal) but adds a third mechanism.
5. **The missing piece:** a self-consistent regime where the entity continuously
   deposits enough to maintain a gradient while losing mass slowly enough to
   survive. This requires: low deposit_rate, high mass, and NO formation phase
   (the entity builds its own field). → v18.

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
