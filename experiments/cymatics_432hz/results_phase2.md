# Cymatics 432 Hz — Phase 2: Graph-Substrate Results

**Date:** 2026-03-20
**Status:** NULL — no frequency privilege on graph substrate
**Script:** `graph_cymatics.py` (grid=100, ticks=2000, sensitivity across 6 configurations)

---

## Executive Summary

Tested whether replacing the classical wave equation with a "phi-wave" equation (golden ratio temporal coefficient) creates a resonance privilege at 432 Hz on a graph substrate. It does not. 432 Hz ranks exactly 12th/18 across all three models and all six grid configurations tested — zero variance. The phi-wave model correlates r=0.997 with classical wave physics, meaning the tick-frame temporal modification barely alters the eigenfrequency structure. This is simultaneously a null result for 432 Hz and a positive result for the tick-frame model's consistency with standard physics.

---

## What Was Tested

Three propagation models on the same 2D grid, driven at the same 18 frequencies:

**Model A — Classical Wave (baseline):**
```
u(t+1) = 2*u(t) - u(t-1) + c^2 * Laplacian(u(t)) + drive
```

**Model B — Fibonacci (phi-wave):**
```
u(t+1) = phi*u(t) - u(t-1) + coupling * Laplacian(u(t)) + drive
```
The ONLY difference: temporal coefficient 2 replaced by phi = 1.618. This is bounded and oscillatory (characteristic equation z^2 - phi*z + 1 = 0 has |z| = 1), but with a shifted eigenfrequency spectrum. The base frequency becomes arccos(phi/2) ~ 0.628 rad/tick instead of 0.

**Model C — Separable Fibonacci:**
Each axis runs independent 1D phi-wave, 2D pattern = outer product. Models the "3 independent tick-series" concept from tick-frame theory.

---

## Results

### 432 Hz Ranking: Identical Across Everything

| Model | 432 Hz Rank | Composite | Top Frequency |
|-------|-------------|-----------|---------------|
| Classical | 12/18 | 0.2421 | 500 Hz (0.7933) |
| Fibonacci | 12/18 | 0.2526 | 500 Hz (0.8343) |
| Separable | 12/18 | 0.2751 | 500 Hz (0.7423) |

### Sensitivity: Perfectly Stable Null

| Grid | Connectivity | 432 Hz Rank | Composite |
|------|-------------|-------------|-----------|
| 50 | 4-neighbor | 12/18 | 0.2539 |
| 50 | 8-neighbor | 12/18 | 0.2445 |
| 100 | 4-neighbor | 12/18 | 0.2526 |
| 100 | 8-neighbor | 12/18 | 0.2426 |
| 200 | 4-neighbor | 12/18 | 0.2539 |
| 200 | 8-neighbor | 12/18 | 0.2508 |

Fraction in top half: **0%** (0 out of 6 configurations).

### Cross-Model Comparison

- 432 Hz (Fibonacci - Classical) difference: +0.0106
- Other frequencies mean difference: +0.0174 +/- 0.0123
- Mann-Whitney U: p = 0.667 — not significant
- 432 Hz benefits **less** from the phi-wave than the average frequency

### The r = 0.997 Correlation

Classical vs Fibonacci model correlation across all 18 frequencies: **r = 0.9970**.

The phi-wave and classical wave produce nearly identical symmetry rankings. The spatial Laplacian dominates the eigenfrequency structure — the 2 vs phi temporal coefficient is a perturbation, not a transformation.

---

## Analysis

### Why r = 0.997 Is the Most Interesting Result

The null result for 432 Hz was expected (and predicted in the Phase 1 writeup). But the near-perfect correlation between classical and phi-wave models is genuinely informative:

1. **The tick-frame temporal modification is consistent with standard physics.** Replacing the wave equation's temporal coefficient with phi doesn't break anything. The eigenmode structure, resonance peaks, and symmetry rankings all survive. This means the tick-frame model doesn't *contradict* classical wave physics — it produces a negligible perturbation.

2. **The spatial Laplacian dominates.** On a regular grid, the spatial coupling (neighbor connectivity) determines the eigenfrequencies far more than the temporal coefficient. The grid geometry is the physics. This is exactly what Phase 1 found for the Euclidean membrane — geometry rules, frequency numerology doesn't.

3. **The 0.3% deviation is real but tiny.** The models aren't identical (r = 0.997, not 1.000). The phi coefficient slightly amplifies lower frequencies relative to higher ones (267 Hz gains more than 528 Hz). This is the expected consequence of the nonzero base frequency in the phi-wave equation. It's a real physical difference — just not one that privileges any specific frequency.

### Why 432 Hz Cannot Win on a Regular Grid

The driving frequency maps to standing wave patterns via the grid's eigenfrequencies, which are:

```
f_mn = c * sqrt((m*pi/N)^2 + (n*pi/N)^2)    [classical]
f_mn shifted by arccos(phi/2)                  [phi-wave]
```

These eigenfrequencies depend on grid size (N), wave speed (c), and mode numbers (m, n). They do NOT depend on Fibonacci numbers. For 432 Hz to be privileged, the eigenfrequency spectrum would need Fibonacci spacing — which a regular grid does not produce.

### What Would Be Needed for a Positive Result

A graph where eigenfrequencies naturally follow Fibonacci spacing would require:
- Non-uniform connectivity (not a regular grid)
- Edge weights following Fibonacci ratios
- Or a graph grown by the tick-frame deposit-extend mechanism itself

This is fundamentally different from testing 432 Hz on a pre-built regular grid. The hypothesis may require a graph that *emerges* from tick-frame dynamics, not one that is *imposed*.

---

## Implications for Tick-Frame Model

1. **No contradiction with standard physics.** The phi-wave perturbation preserves classical wave behavior (r = 0.997). The tick-frame model's temporal dynamics, when projected onto a spatial grid, produce results indistinguishable from classical wave physics at the precision tested.

2. **432 Hz has no privilege on any tested substrate.** Phase 1 (Euclidean eigenmode): ARTIFACT. Phase 2 (graph phi-wave): NULL. The mathematical fact that 432 = 3 x F(12) = 3 x 12^2 does not translate to physical resonance privilege on membranes or grids.

3. **The real test would require an emergent graph.** A graph substrate whose topology is *generated* by tick-frame dynamics (deposit-hop-extend) might have different eigenfrequency structure than a regular grid. That experiment hasn't been done and is substantially harder.

4. **H3 from EXPERIMENT.md remains untested.** The tick-frame specific prediction (that 3D space as three independent Fibonacci tick-series creates substrate-level resonance at 3 x F(n)) cannot be tested on a pre-built grid. It requires the substrate to *be* the Fibonacci process, not just *use* a Fibonacci coefficient.

---

## Generated Artifacts

All in `experiments/cymatics_432hz/results/`:

| File | Description |
|------|-------------|
| `graph_patterns.png` | 3-row comparison: Classical / Fibonacci / Separable patterns at key frequencies |
| `graph_symmetry.png` | Composite score vs frequency for each model |
| `graph_vs_euclidean.png` | Scatter: Phase 1 Euclidean composite vs Phase 2 Fibonacci composite |
| `graph_sensitivity.png` | 432 Hz composite across grid sizes and connectivities |
| `graph_summary.txt` | Full numerical results, statistical tests, and verdict |

---

## Combined Phase 1 + Phase 2 Conclusion

| Phase | Substrate | Model | 432 Hz Verdict | Key Finding |
|-------|-----------|-------|---------------|-------------|
| 1 | Euclidean membrane | Analytical eigenmodes | ARTIFACT | Symmetry depends on plate geometry (f_scale), not frequency |
| 2 | Graph grid | Phi-wave (phi replaces 2) | NULL | Rank 12/18 everywhere, phi-wave ≈ classical (r=0.997) |

**432 Hz = 3 x F(12) has no measurable resonance privilege on any tested substrate.** The mathematical elegance of the identity 3 x 144 = 3 x 12^2 does not translate to physical wave phenomena. The universe's wave physics is governed by geometry (boundary conditions, connectivity), not by number-theoretic properties of the driving frequency.

The r = 0.997 correlation is the silver lining: the tick-frame model's phi-wave modification is consistent with standard physics. It doesn't break anything. Whether it adds anything remains an open question for experiments on emergent (non-regular) graph substrates.
