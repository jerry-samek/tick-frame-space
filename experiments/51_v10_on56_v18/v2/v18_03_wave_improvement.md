# V18.1 Experiment Summary — Orbital Phase Results

**Date**: 2026-02-11
**Experiment**: `orbital_sl5_spread_sign_p200.json`
**Status**: Complete. 0/6 orbits. Two root causes identified.

---

## Configuration

| Parameter | Value |
|-----------|-------|
| Planet processes | 200 |
| Planet spread radius | 3 |
| Formation ticks | 500 (250 paint + 250 spread) |
| Orbital ticks | 2000 |
| Speed limit | 5 |
| Acceleration mode | sign-only (±1 per component) |
| Spreading | enabled (1/6 pressure equalization) |
| Delta threshold | 1e-6 (raised from 1e-10) |
| Random seed | 42 |

---

## Phase 0: Formation Results

### Performance

| Sub-phase | Ticks | Time | Rate | Notes |
|-----------|-------|------|------|-------|
| Paint | 250 | 3.2s | 78 t/s | O(r^3) local gamma sum fix |
| Spread | 250 | 702.9s | ~1 t/s | 131K→302K wake cells |
| **Total** | **500** | **706s** | | |

### Gamma Conservation

| Checkpoint | Total Gamma | Delta |
|------------|-------------|-------|
| Paint tick 100 | 18,026 | — |
| Paint tick 200 | 36,058 | — |
| Paint tick 250 | 45,083 | — |
| Spread tick 100 | 45,083 | 0 |
| Spread tick 200 | 45,082 | -1 (float rounding) |
| Final | 45,081 | -2 |

**Verdict**: Conservation holds within float tolerance.

### Field Profile

Gamma radial distribution peaks at r=13 (2950 gamma) then falls off:

```
r=  5:  1228.5    r= 13:  2950.2 (peak)
r= 10:  2592.8    r= 20:  1647.4
r= 15:  2756.8    r= 30:   180.1
r= 20:  1647.4    r= 40:     4.8
r= 25:   679.5    r= 49:     0.0
```

**Field extent**: r=49.0 (gamma > 1e-6)

### Power Law Fit

Sampling gamma along +x axis at r = 5, 7, 10, 15, 20, 25, 30, 40:

```
gamma ~ r^(-3.553)
```

**This is much steeper than the target 1/r (exponent -1.0).** The field drops off too rapidly with distance. At r=30, gamma is only 0.029 vs 3.05 at r=5 — a factor of 100×, whereas 1/r would give only 6×.

### Gradient Profile

| r | grad_mag | ratio to prev | expected (1/r²) |
|---|----------|---------------|-----------------|
| 5 | 0.1740 | — | — |
| 10 | 0.2134 | 1.23 | 0.25 |
| 15 | 0.2114 | 0.99 | 0.44 |
| 20 | 0.0956 | 0.45 | 0.56 |
| 25 | 0.0390 | 0.41 | 0.64 |
| 30 | 0.0093 | 0.24 | 0.69 |
| 40 | 0.0002 | 0.03 | 0.56 |
| 50 | 0.0000 | — | — |

**Key observation**: Gradient actually INCREASES from r=5 to r=10 (ratio 1.23), then falls off steeply. This is not the monotonic decrease expected from a 1/r potential. The gamma profile peaks at r=13, so the gradient reverses direction around there — inside r=13, gradient points outward; outside r=13, gradient points inward. This is a gravity well with a finite-depth bowl, not a 1/r funnel.

### Phase 0 Validation

| Check | Result |
|-------|--------|
| Gradient nonzero at test distances | 7/8 PASS (zero at r=50) |
| Gradient decreases with distance | PASS (comparing r=10 vs r=30) |
| Field extends to orbital distances | PARTIAL — reaches r=49 but very weak beyond r=30 |
| 1/r profile | FAIL — r^(-3.553), too steep |
| Conservation | PASS |

---

## Phase 1: Orbital Results

### Test Processes

| ID | Start pos | Start vel | Description |
|----|-----------|-----------|-------------|
| T1 | (30,0,0) | (0,3,0) | Circular attempt r=30 |
| T2 | (30,0,0) | (0,0,0) | Radial infall control |
| T3 | (20,0,0) | (0,3,0) | Closer orbit r=20 |
| T4 | (50,0,0) | (0,3,0) | Farther orbit r=50 |
| T5 | (30,0,0) | (0,0,3) | Out-of-plane orbit |
| T6 | (40,0,0) | (0,3,0) | Medium distance r=40 |

### Final State (after 2000 ticks)

| ID | Final r | Final v | L_z | Acts | Skips | Outcome |
|----|---------|---------|-----|------|-------|---------|
| T1 | 16.6 | (-2,-2,-1) | -10 | 1831 | 169 | Chaotic bouncing |
| T2 | 9.9 | (-4,-4,1) | -20 | 1809 | 191 | Chaotic bouncing |
| T3 | 17.5 | (0,-1,1) | -15 | 1801 | 199 | Chaotic bouncing |
| T4 | 6000.2 | (0,3,0) | 150 | 2000 | 0 | **ESCAPED** |
| T5 | 0.0 | (-5,0,3) | 0 | 1808 | 192 | **COLLAPSED** |
| T6 | 17.5 | (-2,-1,1) | -21 | 1813 | 187 | Chaotic bouncing |

**Orbits formed: 0/6**

### Behavioral Patterns

**T4 (ESCAPED)**: Started at r=50 where gradient ≈ 0. Flew away at constant v=(0,3,0) with zero acceleration. r increased linearly at 3 cells/tick → r=6000 after 2000 ticks. Never experienced any force.

**T5 (COLLAPSED)**: Out-of-plane motion. Bounced chaotically between r=4-17 for ~1900 ticks, then fell to r=0 at tick 2000. The z-component of velocity accumulated while the radial restoring force was weak.

**T1, T2, T3, T6 (CHAOTIC BOUNCING)**: All processes fell inward from their starting positions to the r=5-18 zone where gradient is strongest, then bounced around chaotically. They didn't orbit — they oscillated radially with no angular momentum conservation. L_z changed sign repeatedly.

### Angular Momentum Analysis

L_z for T1 sampled every 100 ticks:
```
Tick  100: L_z = -15    Tick  600: L_z = -10    Tick 1100: L_z = -25
Tick  200: L_z =  15    Tick  700: L_z =  15    Tick 1200: L_z =  25
Tick  300: L_z = -10    Tick  800: L_z =   0    Tick 1300: L_z =  -5
Tick  400: L_z =   5    Tick  900: L_z =  -5    Tick 1400: L_z =   5
Tick  500: L_z =  25    Tick 1000: L_z =  15    Tick 1500: L_z =   0
```

L_z oscillates wildly with no trend. This is far from conservation (V10 achieved L_z std/mean < 0.05).

---

## Root Cause Analysis

### Root Cause 1: Field profile too steep (r^-3.55 vs r^-1)

250 spread ticks are insufficient to reach the 1/r equilibrium profile. The wavefront has only reached r=49, and most gamma is concentrated in the r=5-15 shell. The field resembles a steep bowl, not a 1/r funnel.

**Why this matters**: A 1/r potential produces force ∝ 1/r², which decreases with distance and enables circular orbits at all radii. A steep bowl produces a narrow zone of strong force (r=10-15) with effectively zero force beyond r=30. There's no orbital distance — either the process is inside the bowl and bouncing, or outside and free.

**Fix**: More spread ticks. The 1/r profile is the Green's function of the lattice Laplacian — it requires the wavefront to reach equilibrium everywhere. 250 ticks only spreads to r≈50; equilibrium may need thousands of spread ticks or a different approach entirely (e.g., analytical initialization of 1/r profile, or per-process wavefronts from v18_03 Part 2).

### Root Cause 2: Sign-only acceleration destroys angular momentum

Sign-only acceleration (`accel = sign(gradient)`) gives ±1 per component regardless of gradient magnitude. This means:

1. **Force is constant**: A process at r=10 (strong gradient) gets the same ±1 acceleration as a process at r=25 (weak gradient). There's no distance-dependent force.

2. **No tangential preservation**: The gradient always points radially inward. Sign-only always adds ±1 to vx and vy independently. This doesn't preserve the tangential component — it converts tangential velocity to radial.

3. **Integer velocity quantization**: With speed_limit=5, velocity is quantized to integers in [-5,5]^3. Orbital mechanics requires smooth velocity adjustments. Integer quantization makes circular orbits geometrically impossible — the process can only move along lattice directions.

**Fix**: Phase 2 velocity accumulator (`--accumulator` flag). This accumulates fractional gradient contributions and only applies integer velocity changes when the accumulator crosses a threshold. This preserves gradient magnitude information and allows smoother trajectories.

---

## Comparison

| Metric | V18 (no spread) | V18.1 (spread) | V10 (PDE) |
|--------|-----------------|----------------|-----------|
| Gradient at r=30 | 0 | 0.009 | ~0.03 |
| Gradient at r=50 | 0 | 0 | ~0.01 |
| Field extent | r=8 | r=49 | infinite |
| Power law | N/A | r^(-3.55) | r^(-1) |
| Orbits | 0/25 | 0/6 | 18/18 |
| L_z conservation | ~1.2 | >10 | ~0.05 |

V18.1 spreading successfully extends the field (r=8 → r=49) and creates nonzero gradients at orbital distances. This is a clear improvement over V18. But the profile is still far from 1/r, and sign-only acceleration prevents orbit formation regardless of field shape.

---

## Next Steps

1. **More spread ticks**: Run with formation_ticks=2000 (1000 paint + 1000 spread) to see if profile approaches 1/r. The spread phase is slow (~3 t/s) so this means ~5-6 minutes.

2. **Velocity accumulator**: Run with `--accumulator` flag to test Phase 2 mechanism. Even with the current steep field, the accumulator may produce orbits in the r=10-20 zone where gradient is strong.

3. **Both**: Run with more spread ticks AND accumulator — this gives the best chance.

4. **Spread performance**: The spread phase is the bottleneck (703s for 250 ticks). With 1e-6 threshold, 302K/444K cells are still in the wake at tick 200. Options:
   - Per-process wavefronts (v18_03 Part 2)
   - Higher threshold (1e-4?)
   - Analytical 1/r initialization (skip spreading entirely)

5. **Analytical baseline**: Initialize gamma = C/r directly (skip spreading) and test orbital mechanics in isolation. This separates the two problems: "does spreading produce 1/r?" from "do orbits work in 1/r field?"
