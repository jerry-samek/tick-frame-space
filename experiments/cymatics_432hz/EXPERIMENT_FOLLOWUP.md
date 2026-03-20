# Followup Experiment: Graph-Substrate Wave Propagation vs Euclidean Chladni

## Context

Previous experiment (chladni_patterns.py) tested 432 Hz symmetry on a standard
Euclidean 2D membrane (500x500 grid, classical wave equation). Result: NULL — 432 Hz
showed no intrinsic symmetry privilege. Verdict: ARTIFACT of eigenmode proximity,
plate-geometry dependent.

**Critical weakness of that experiment:**

The Euclidean membrane has no knowledge of Fibonacci, tick-frame substrate, or local
summation rules. It was testing classical physics — not tick-frame predictions.

## Tick-Frame Prediction

In the tick-frame model, gamma propagates on a graph substrate where each node sums
its neighbors — exactly like Fibonacci. The hypothesis is:

432 = 3 × F(12) = 3 × 12²

Where F(12) = 144 is the ONLY Fibonacci perfect square > 1 (Cohn 1964).
At step 12, a 1D Fibonacci chain first converges to φ with <0.01% error.
In 3D (3 independent tick-series), this gives 3 × 144 = 432.

If this has physical meaning, it should appear as a natural resonance on a
GRAPH substrate with local summation — NOT on a Euclidean membrane.

## Experiment Design

### 1. Graph Construction

Build a 2D grid graph (N×N nodes) where each node connects to its 4 or 8 neighbors.
This is structurally identical to a Euclidean membrane BUT the wave propagation rule
will be different.

### 2. Wave Propagation Rule — Fibonacci-local vs Classical

**Classical (already tested):**
∂²u/∂t² = c² ∇²u  (continuous Laplacian)

**Graph-Fibonacci (new):**
u(n+1, i) = u(n, i-1) + u(n, i-2)  [1D Fibonacci rule along each axis]

Or equivalently — at each tick, each node's new value is the SUM of its two
nearest neighbors along each axis, independently. Three independent tick-series
(x, y, z axes). No cross-coupling.

Test both:
- Pure Fibonacci recurrence: u(t+1) = u(t) + u(t-1) per node per axis
- Graph Laplacian with Fibonacci-weighted edges: w(hop_n) = F(n)/F(n+1)

### 3. Frequencies to Test

Same as before for comparison:
- 267 Hz  (3 × F(11) = 3 × 89)
- 360 Hz  (control, non-Fibonacci)
- 420 Hz  (near 432, control)
- 432 Hz  ← hypothesis: privileged on graph substrate
- 440 Hz  (modern standard)
- 528 Hz  (another "sacred" frequency, control)
- 699 Hz  (3 × F(13) = 3 × 233) ← won on Euclidean
- 1131 Hz (3 × F(14) = 3 × 377)

### 4. Symmetry Metric

Same composite symmetry score as before:
- Rotational symmetry (90°, 45°)
- Bilateral symmetry
- Nodal region count
- Entropy of pattern

### 5. Sensitivity Analysis

Vary graph size (N = 50, 100, 200) and connectivity (4-neighbor vs 8-neighbor).
A real signal should be geometry-independent.
An artifact will vary with graph parameters (like Euclidean result).

### 6. Direct Comparison

Produce side-by-side output:
- Euclidean membrane result (from previous experiment)
- Graph-Fibonacci result (this experiment)

If results AGREE → tick-frame adds nothing, classical physics sufficient
If results DIFFER → graph substrate changes the physics, 432 may behave differently

## Null Hypothesis

432 Hz shows no symmetry privilege on graph substrate either.
Any apparent advantage is geometry/parameter dependent.

## Output Required

1. Symmetry scores table: all frequencies × all graph parameters
2. Pattern visualizations: graph-substrate nodal patterns at key frequencies
3. Direct comparison plot: Euclidean C-scores vs Graph C-scores
4. Fibonacci convergence overlay: mark F(n)×3 series on frequency axis
5. Honest verdict: does graph substrate change anything, or is it still `y==9`?

## Important Notes

- Keep graph size manageable (N=100 sufficient for first pass)
- The Fibonacci propagation rule is NOT standard wave equation — implement carefully
- If 432 wins on graph but loses on Euclidean: interesting, needs explanation
- If 699 wins again: Fibonacci×3 series may be consistently privileged (also interesting)
- If everything is random: null result holds across substrates

## Reference

Previous experiment: chladni_patterns.py (Euclidean, null result, p=0.27)
Theoretical basis: tick-frame RAW 108-113, append-only graph substrate
Mathematical anchor: Cohn (1964) — F(12)=144=12² is unique Fibonacci perfect square
