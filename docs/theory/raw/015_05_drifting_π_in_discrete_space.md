# 15‑05 Drifting π in Discrete Space

### *An example of a “constant” that is not constant*

## 🧭 Context

In previous chapters we established that:

- the substrate is memoryless (tick‑frame, no stored state),
- dimensions are observer reconstructions, not substrate properties,
- “constants” can only be emergent, not fundamental (Slow Drift Hypothesis).

This chapter presents a concrete example:  
**π is not truly constant in a discrete space.**

---

## 1. π in continuous geometry

In classical (continuous) Euclidean geometry, π is defined as:

\[
\pi = \frac{O}{D}
\]

where:

- \(O\) is the circumference of a circle,
- \(D\) is its diameter.

This value is:

- scale‑invariant,
- position‑invariant,
- time‑invariant,
- treated as a fundamental constant.

But this only holds in a **smooth, continuous** space — which does **not** exist at the substrate level in the
tick‑frame model.  
It exists only in the observer’s reconstruction.

---

## 2. π in discrete space

In a discrete space:

- a circle is approximated by a finite number of cells (pixels, voxels, grid units),
- the circumference is a stepwise path, not a smooth curve,
- the diameter is a count of steps, not a continuous distance.

We define an effective:

\[
\pi(t, R) = \frac{O_{\text{disc}}(t, R)}{D_{\text{disc}}(t, R)}
\]

where:

- \(t\) is the tick (time),
- \(R\) is the chosen radius in discrete units,
- \(O_{\text{disc}}(t, R)\) is the discrete circumference,
- \(D_{\text{disc}}(t, R)\) is the discrete diameter.

In such a space:

- for small circles, \(\pi(t, R)\) differs significantly from 3.14159…,
- for larger circles, \(\pi(t, R)\) approaches the continuous value,
- the exact π is never reached — the grid is finitely coarse.

Conclusion: **π is not a constant but a function of scale \(R\).**

---

## 3. Drift of π as space and horizon grow

In tick‑frame cosmology:

- space is not stored but generated tick‑to‑tick,
- the horizon grows with time \(t\) (Genesis experiment),
- the maximum realizable circle (maximum \(R\)) grows with the horizon.

Therefore:

- as \(t\) increases, the available scale \(R_{\max}(t)\) increases,
- as \(R_{\max}(t)\) increases, the possible values of \(\pi(t, R)\) shift,
- for larger \(R\), \(\pi(t, R)\) approaches the continuous value but never reaches it,
- the effective “observed” π may drift as the universe’s resolution improves.

Formally:

\[
\pi_{\text{eff}}(t) = \pi(t, R_{\max}(t))
\]

Thus, in a well‑scaled simulation we expect:

- **drift of π\_{\text{eff}}(t)** as the horizon expands,
- π is not a fixed constant but a **horizon‑dependent reconstruction parameter**.

---

## 4. How to measure this drift (experimental outline)

In a discrete 2D or 3D substrate:

1. **For each tick \(t\):**
    - determine the current horizon \(H(t)\),
    - choose the maximum possible radius \(R_{\max}(t) \leq H(t)\).

2. **Construct a discrete “circle”** with radius \(R\):
    - e.g., the set of cells at distance \(R \pm \epsilon\) from the center under a chosen metric (Manhattan, Chebyshev,
      Euclidean approximation).

3. **Compute:**
    - discrete circumference \(O_{\text{disc}}(t, R)\),
    - discrete diameter \(D_{\text{disc}}(t, R)\),
    - effective \(\pi(t, R) = O_{\text{disc}}(t, R)/D_{\text{disc}}(t, R)\).

4. **Log:**
    - \(t\), \(R\), \(\pi(t, R)\),
    - optionally \(\pi_{\text{eff}}(t)\) for \(R = R_{\max}(t)\).

This experiment directly reveals:

- scale dependence of π,
- drift of π with horizon growth,
- the influence of discrete metrics on geometric “constants.”

---

## 5. Interpretation within the Slow Drift Hypothesis

Drifting π fits directly into the **Slow Drift Hypothesis**:

- the substrate stores nothing — not geometry, not constants,
- “constants” are emergent reconstructions by the observer,
- π is merely a **stable summary** of discrete geometry at a given scale and time,
- when the horizon, scale, or reconstruction metric changes, π **shifts**.

Thus:

> π in this model is not a fundamental constant.  
> It is a **function of reconstruction, horizon, and discrete scale**.

---

## 6. Summary

- In discrete space, there is no single universal value of π.
- π depends on scale, metric, horizon, and approximation method.
- As the universe “grows” (Genesis, tick‑frame cosmology), the resolution at which circles can be approximated changes —
  and so does the effective π.
- π therefore serves as a clear example of a **constant that drifts** in the tick‑frame model.

> **This chapter demonstrates that even the most iconic “constants” of geometry are products of reconstruction, not
fixed substrate values.**
