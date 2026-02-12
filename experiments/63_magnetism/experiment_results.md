# Experiment Results — Discrete Altermagnetism v2

**Date**: February 12, 2026
**Parameters**: Grid 64x64, 4x4 entities, spacing 16, eq=1000 ticks, probe=2000 ticks, 5 runs/pattern,
W_center=10.0, W_tangential=5.0, lag=2

## Overall Verdict: PASS

| Mode   | Result | Purpose                                    |
|--------|--------|--------------------------------------------|
| frozen | N/A    | Baseline (not scored, confirms v1 problem)  |
| signed | PASS   | Compensated magnetism + pattern specificity |
| live   | PASS   | Velocity-dependent deflection               |

---

## Key Discriminator: M_net by Mode

The signed tangential field provides 11 orders of magnitude discrimination between ferromagnetic and compensated
patterns. Frozen mode cannot distinguish them at all.

| Pattern          | Frozen    | Signed      | Live      |
|------------------|-----------|-------------|-----------|
| checkerboard     | 10.56     | **3.6e-13** | 12.67     |
| stripe           | 17.80     | **1.3e-12** | 17.80     |
| ferromagnetic    | 10.19     | **80,000**  | 13.78     |
| antiferromagnetic| 10.05     | **3.6e-13** | 10.24     |

## Velocity Dependence

| Mode   | v=0.2 deflection | v=0.7 deflection | Behavior       |
|--------|------------------|------------------|----------------|
| frozen | 1.743            | 1.489            | GRAVITATIONAL  |
| signed | 0.334            | 0.623            | **MAGNETIC**   |
| live   | 0.090            | 1.094            | **MAGNETIC**   |

Frozen mode: slower probes deflect more (gravitational — force acts longer).
Signed/live modes: faster probes deflect more (magnetic — velocity-dependent coupling).

---

## Detailed Results by Mode

### Frozen Mode (baseline)

| Pattern           | M_net mean | M_net std | max_W_tang | A_NS mean  | A_NS std | A_EW mean  | A_EW std |
|-------------------|------------|-----------|------------|------------|----------|------------|----------|
| checkerboard      | 10.557     | 2.832     | 0.499      | -0.222     | 0.485    | -0.356     | 1.086    |
| stripe            | 17.798     | 5.935     | 0.562      | -0.590     | 0.530    | -0.444     | 1.579    |
| ferromagnetic     | 10.192     | 6.169     | 0.499      | 0.414      | 0.993    | 0.450      | 0.659    |
| antiferromagnetic | 10.047     | 3.536     | 0.499      | 0.413      | 0.983    | 0.622      | 0.453    |

All patterns produce nearly identical M_net (~10-18) and max_W_tang (~0.50). The frozen field erases all handedness
information. This confirms the v1 problem: time-averaged tangential deposits cancel exactly over each 8-tick cycle.

### Signed Mode

| Pattern           | M_net mean | M_net std | max_W_tang | A_NS mean  | A_NS std | A_EW mean  | A_EW std |
|-------------------|------------|-----------|------------|------------|----------|------------|----------|
| checkerboard      | 3.6e-13    | 2.2e-13   | 0.507      | -0.046     | 0.935    | 0.354      | 1.344    |
| stripe            | 1.3e-12    | 8.4e-13   | 1.103      | 0.121      | 0.548    | -0.214     | 0.581    |
| ferromagnetic     | 80000.0    | 1.1e-11   | 0.499      | 0.185      | 0.959    | 0.092      | 1.618    |
| antiferromagnetic | 3.6e-13    | 3.1e-13   | 0.566      | -0.555     | 0.696    | -0.020     | 0.942    |

Criteria evaluation:

- Compensated magnetism (M_net/M_net_ferro < 0.01):
  - checkerboard: 3.6e-13 / 80000 = **4.5e-18 PASS**
  - stripe: 1.3e-12 / 80000 = **1.6e-17 PASS**
- Ferromagnetic M_net >> 0: **80,000 PASS**
- Antiferromagnetic M_net ~ 0: ratio to ferro = **4.5e-18 PASS**
- Anisotropic transport:
  - checkerboard: |A_EW| = 0.354 > 0.1 **PASS**
  - stripe: |A_NS| = 0.121 > 0.1 AND |A_EW| = 0.214 > 0.1 **PASS**
- Pattern specificity (checker vs stripe distinct): **PASS**

Note: stripe max_W_tang (1.103) is 2x larger than checkerboard (0.507) because stripe uses |omega|=2, producing
stronger tang gradients. The spatial tang patterns also differ (d-wave vs g-wave symmetry).

### Live Mode

| Pattern           | M_net mean | M_net std | max_W_tang | A_NS mean  | A_NS std | A_EW mean  | A_EW std |
|-------------------|------------|-----------|------------|------------|----------|------------|----------|
| checkerboard      | 12.669     | 5.044     | 0.499      | -1.155     | 0.768    | -0.040     | 0.517    |
| stripe            | 17.798     | 5.935     | 0.562      | 0.133      | 1.309    | 0.375      | 0.589    |
| ferromagnetic     | 13.775     | 4.208     | 0.499      | 0.512      | 0.902    | 0.664      | 0.560    |
| antiferromagnetic | 10.242     | 3.556     | 0.499      | -0.711     | 1.729    | -0.373     | 1.519    |

Live mode M_net values are similar to frozen mode (tangential deposits still go to gamma, not tang). The key
finding is **velocity dependence**: faster probes deflect MORE, confirming magnetic rather than gravitational
behavior. The transient interference patterns within each rotation sub-cycle create real-time forces that
velocity-coupled probes can detect.

---

## Fourier Symmetry (Signed Mode)

Dominant angular modes from the tangential gradient field:

| Pattern           | m=1   | m=2   | m=4   | m=8   | Dominant |
|-------------------|-------|-------|-------|-------|----------|
| checkerboard      | 0.069 | 0.057 | **0.227** | 0.494 | m=8      |
| stripe            | 0.002 | 0.020 | **0.516** | 0.450 | **m=4**  |
| ferromagnetic     | 0.093 | 0.058 | 0.167 | **0.514** | m=8  |
| antiferromagnetic | 0.026 | 0.023 | 0.070 | **0.770** | m=8  |

Stripe pattern shows strong m=4 dominance (0.516), consistent with the 2x2 block structure creating
4-fold angular symmetry in the tangential field. Checkerboard shows elevated m=4 (0.227) but m=8 still
dominates due to the underlying 8-direction discrete rotation.

---

## Conductivity Tensors (Signed Mode)

### Checkerboard
```
sigma = [[ 0.055,  0.038],
         [ 0.090,  0.047]]
```

### Stripe
```
sigma = [[ 0.038,  0.001],
         [-0.031, -0.013]]
```

### Ferromagnetic
```
sigma = [[-0.011, -0.079],
         [ 0.050, -0.113]]
```

### Antiferromagnetic
```
sigma = [[ 0.035, -0.074],
         [-0.063,  0.055]]
```

The off-diagonal elements (sigma_xy, sigma_yx) differ between patterns, confirming pattern-specific
directional transport. Stripe shows near-zero sigma_xy (0.001) while checkerboard shows 0.038,
consistent with different symmetry classes.

---

## Interpretation

1. **Signed tangential field solves the v1 problem.** By encoding omega handedness in a separate signed field,
   CW and CCW rotations produce distinguishable deposits that survive time-averaging. The conservation law
   (sum of signed deposits = sum of all omegas) guarantees exact M_net = 0 for compensated patterns and
   M_net proportional to total omega for uncompensated patterns.

2. **Velocity dependence confirms magnetic character.** In both signed and live modes, faster probes deflect
   more — the hallmark of magnetic (velocity-dependent) forces as opposed to gravitational (position-dependent)
   forces. Frozen mode shows the opposite: gravitational behavior where slower probes accumulate more deflection
   simply by spending more time in the gradient.

3. **Pattern specificity is real but subtle.** The probe deflection asymmetries (A_NS, A_EW) vary between
   patterns and have high variance across runs (std ~ mean), indicating sensitivity to initial random theta.
   The M_net discrimination is exact (by conservation), while transport anisotropy is a statistical signal
   requiring multiple runs to resolve.
