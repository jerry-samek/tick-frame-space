# Cymatics 432 Hz — Computational Experiment Results

**Date:** 2026-03-20
**Status:** ARTIFACT — H1 rejected, H0 supported
**Script:** `cymatics.py` (grid=500, max_mode=20, Q=100, f_scale sensitivity across 5 values)

---

## Executive Summary

Tested whether 432 Hz = 3 x F(12) = 3 x 144 produces measurably higher symmetry in Chladni patterns compared to neighboring frequencies. The f_scale sensitivity analysis (the honesty check) reveals that 432 Hz has **no intrinsic symmetry privilege**. Its apparent advantage at f_scale=1.5 vanishes at other plate parameters — ranking anywhere from 4th to dead last (18th/18). The verdict is ARTIFACT: eigenmode proximity, not Fibonacci numerology. The surprise winner at default parameters was 699 Hz = 3 x F(14).

---

## Hypotheses Tested

**H1 (Primary):** 432 Hz should exhibit measurably more symmetric Chladni patterns than adjacent frequencies, due to its position as 3 x F(12) where F(12) = 12^2 = 144 is the only Fibonacci perfect square > 1.

**H2 (Secondary):** The full series 3 x F(n) should show higher symmetry than non-series frequencies.

**H0 (Null):** Chladni patterns at 432 Hz are no more symmetric than at neighboring frequencies. Pattern symmetry depends on plate geometry, not frequency numerology.

**H3 (Tick-frame specific):** Not testable computationally — requires physical experiment or tick-frame substrate simulation.

---

## Method

**Approach:** Analytical eigenmode superposition (not time-domain simulation). Closed-form computation of Chladni patterns for a square plate with free-free boundary conditions.

**Pattern computation:**
- Eigenmodes (m,n): mode shape = cos(m*pi*x)*cos(n*pi*y) + cos(n*pi*x)*cos(m*pi*y)
- Eigenfrequency: f_mn = f_scale * (m^2 + n^2)
- Lorentzian response: A_mn = 1 / ((f_drive - f_mn)^2 + gamma^2), gamma = f_mn / (2*Q)
- Sum weighted modes, normalize to [-1, 1]

**Symmetry metrics (5 measures + composite):**
- C4: correlation with 90-degree rotation
- C8: correlation with 45-degree rotation (circular mask to avoid corner artifacts)
- Bilateral: mean of 4 mirror correlations (x-flip, y-flip, transpose, anti-transpose)
- Sharpness: normalized gradient magnitude at nodal lines
- Complexity: normalized nodal region count
- Composite: 0.3*C4 + 0.2*C8 + 0.3*bilateral + 0.1*sharpness + 0.1*complexity

**Frequencies tested (18 total):**
- Fibonacci series (3 x F(n)): 267, 432, 699 Hz
- Fine scan (2 Hz steps): 420, 422, 424, ..., 440 Hz
- Controls: 360, 400, 450, 500, 528 Hz

**Honesty check:** Full sweep repeated at f_scale = {1.0, 1.25, 1.5, 1.75, 2.0} to test whether any advantage is plate-dependent or intrinsic.

---

## Results

### Ranking at Default Parameters (f_scale=1.5)

| Rank | Frequency | Composite | Category |
|------|-----------|-----------|----------|
| 1 | 699.0 Hz | 0.7365 | Fibonacci [3xF(14)] |
| 2 | 430.0 Hz | 0.4448 | Fine scan |
| 3 | 438.0 Hz | 0.4362 | Fine scan |
| **4** | **432.0 Hz** | **0.3841** | **Fibonacci [3xF(12)]** |
| 5 | 428.0 Hz | 0.3414 | Fine scan |
| 6 | 440.0 Hz | 0.2262 | Fine scan |
| 7 | 426.0 Hz | 0.1751 | Fine scan |
| 8 | 420.0 Hz | 0.0922 | Fine scan |
| 9 | 528.0 Hz | 0.0852 | Control |
| 10 | 422.0 Hz | 0.0843 | Fine scan |

432 Hz ranks 4th/18 at default f_scale — decent but not special. Its neighbors 430 and 438 Hz outscore it.

### Statistical Tests

**Mann-Whitney U (432 vs fine-scan neighbors):**
- U = 8.0, p = 0.2727 — **not significant**
- 432 composite: 0.3841 vs fine-scan mean: 0.1882 +/- 0.1597

**Category comparison (Fibonacci series vs Controls):**
- Fibonacci mean: 0.3055 +/- 0.3880
- Controls mean: 0.0144 +/- 0.0825
- U = 10.0, p = 0.2857 — **not significant**
- Note: the enormous Fibonacci std (0.388) is driven by 699 Hz pulling the mean up and 267 Hz pulling it down

### f_scale Sensitivity (The Honesty Check)

This is the critical result. If 432's advantage were intrinsic to its mathematical structure, it would persist across plate parameters.

| f_scale | 432 Hz Rank | Composite | Advantage vs Mean |
|---------|-------------|-----------|-------------------|
| 1.00 | 13/18 | 0.1040 | -0.1023 |
| 1.25 | **18/18** | -0.2217 | **-0.4325** |
| 1.50 | 4/18 | 0.3841 | +0.2379 |
| 1.75 | 10/18 | 0.0395 | -0.0192 |
| 2.00 | 14/18 | -0.1733 | -0.3951 |

- Mean advantage: **-0.1422 +/- 0.2487** (negative — 432 Hz is worse than average on balance)
- In top half of frequencies: **only 20% of the time** (1 out of 5 f_scale values)
- At f_scale=1.25, 432 Hz ranks **dead last**

**Verdict: ARTIFACT** — strongly f_scale dependent.

---

## Analysis

### Why ARTIFACT, Not NULL

A NULL verdict would mean 432 Hz shows no advantage anywhere. The actual situation is more informative: 432 Hz shows a strong apparent advantage at f_scale=1.5 (rank 4/18) but catastrophic performance at f_scale=1.25 (rank 18/18). This pattern is characteristic of eigenmode proximity — at f_scale=1.5, the eigenmode (m,n) with m^2 + n^2 near 432/1.5 = 288 happens to produce a symmetric pattern. Change the plate and the lucky alignment vanishes.

### Why 699 Hz Dominates

699 Hz = 3 x F(14) = 3 x 233 scored highest (composite 0.7365) at default parameters. This is also an eigenmode proximity artifact. At f_scale=1.5, the nearest eigenmode to 699/1.5 = 466 ≈ m^2 + n^2 lands on a highly symmetric mode combination. The same frequency would rank differently on a different plate. 699 Hz has no more intrinsic privilege than 432 Hz — it just got luckier at this particular f_scale.

### Fine-Scan Variance

The fine-scan region (420-440 Hz) shows wild variance in composite scores: from -0.0227 (436 Hz) to 0.4448 (430 Hz). Adjacent frequencies differ by factors of 10x or more. This demonstrates how sensitively Chladni symmetry depends on exact eigenmode alignment — small frequency shifts cross eigenmode boundaries, dramatically changing the pattern structure. This high sensitivity is itself evidence against any frequency having intrinsic privilege.

### H2: Series Property

The Fibonacci series (267, 432, 699) shows no consistent advantage over controls. The series mean (0.3055) is higher than controls (0.0144), but the p-value (0.2857) is far from significant, and the huge standard deviation (0.388) reveals this is driven entirely by 699 Hz while 267 Hz actually scores worst of all frequencies (-0.2042).

---

## Implications for Tick-Frame Model

1. **Classical plate acoustics shows no Fibonacci frequency privilege.** This is the expected result — eigenmode frequencies depend on plate geometry (material, shape, size), not on number-theoretic properties of the driving frequency.

2. **H3 remains untested.** The tick-frame prediction (that 3D space as three independent Fibonacci tick-series would create substrate-level resonance at 3 x F(n)) cannot be tested with classical Chladni computation. It requires either:
   - A physical experiment where the plate is a real physical object coupled to whatever the substrate actually is
   - A tick-frame substrate simulation where the membrane is modeled as a discrete graph with gamma deposits

3. **The experiment successfully distinguishes claims.** "432 Hz is special in classical acoustics" (refuted) is a different claim from "432 Hz is special in tick-frame substrate dynamics" (untested). This distinction is valuable.

---

## What Was Learned

1. **The honesty check was the most valuable design decision.** Running only at f_scale=1.5 would have produced a misleading "WEAK" result (432 Hz at rank 4/18 with some apparent advantage). The f_scale sweep caught the artifact.

2. **Single-parameter results are unreliable for resonance claims.** Any frequency can appear "special" if you pick the right plate. The scientific claim requires robustness across plate parameters.

3. **Chladni patterns are hypersensitive to frequency.** Adjacent frequencies (2 Hz apart) can produce dramatically different symmetry scores. This sensitivity means pattern comparisons must account for eigenmode structure, not just frequency values.

---

## Generated Artifacts

All in `experiments/cymatics_432hz/results/`:

| File | Description |
|------|-------------|
| `chladni_patterns.png` | Grid of pattern visualizations with nodal lines at key frequencies |
| `symmetry_vs_frequency.png` | All 5 symmetry metrics plotted against frequency, 432 Hz highlighted |
| `fibonacci_convergence.png` | F(n+1)/F(n) ratio convergence to phi + 3xF(n) series with 432 marked |
| `statistical_comparison.png` | Violin/bar plots comparing Fibonacci, fine-scan, and control categories |
| `statistical_summary.txt` | Full numerical results table, statistical tests, and programmatic verdict |
