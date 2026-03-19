# Active Propulsion Limit in Tick-Frame Space

**Version:** Draft 1  
**Author:** Internal notes (Tom’s tick-frame library)  
**Scope:** Conceptual limit on how fast a complex pattern (e.g. rocket + human) can move via *active propulsion* in a discrete tick-frame substrate.

---

## 1. Ontological setup

In tick-frame space:

- **Substrate:** Discrete causal grid, updated in ticks.
- **Cell:** A causal sample (local update site), no internal geometry.
- **Pattern:** A structured configuration of states across one or more cells that persists by regenerating itself each tick.
- **Tick-budget:** The amount of “update work” available per tick for a given region/pattern.

Key idea:

> A pattern exists only if it can **regenerate its internal structure** within the available tick-budget.  
> Movement is not continuous motion, but **discrete relocation of the pattern** across cells via local update rules.

---

## 2. Complexity, regeneration cost, and motion

Let:

- \(C_{\text{int}}\) = internal complexity of the pattern  
  (number of independent degrees of freedom / states that must be updated per tick to maintain identity)
- \(B_{\text{tot}}\) = total tick-budget available to that pattern per tick  
  (how much “work” the substrate allocates to it)
- \(B_{\text{int}}\) = tick-budget spent on internal regeneration
- \(B_{\text{move}}\) = tick-budget left for motion (positional update)

By definition:

\[
B_{\text{tot}} = B_{\text{int}} + B_{\text{move}}
\]

A pattern is **stable** only if:

\[
B_{\text{int}} \geq C_{\text{int}}
\]

i.e. it can at least keep up with its own internal complexity.

Whatever remains:

\[
B_{\text{move}} = B_{\text{tot}} - B_{\text{int}}
\]

is all that’s available to change its position in the grid.

---

## 3. Substrate speed and effective velocity

Define:

- \(c_{\text{sub}}\) = substrate causal speed  
  (maximum rate at which influence can propagate: 1 cell per tick in the simplest case)
- \(v_{\text{eff}}\) = effective velocity of the pattern as seen from an external frame  
  (average displacement per tick)

In the simplest discrete model:

- **1 unit of motion work** (one “movement quantum”) = enough tick-budget to shift the pattern by 1 cell in 1 tick.
- If \(B_{\text{move}} = 1\), the pattern can move at \(v_{\text{eff}} = c_{\text{sub}}\).
- If \(B_{\text{move}} < 1\), the pattern can only move 1 cell every \(\frac{1}{B_{\text{move}}}\) ticks on average.

So:

\[
v_{\text{eff}} = c_{\text{sub}} \cdot B_{\text{move}}
\]

with \(0 \leq B_{\text{move}} \leq 1\) in the normalized case.

Substituting:

\[
v_{\text{eff}} = c_{\text{sub}} \cdot (B_{\text{tot}} - B_{\text{int}})
\]

---

## 4. Active propulsion and its fundamental limit

**Active propulsion** means:

> The pattern itself (e.g. rocket + payload) is trying to change its position by expending its own tick-budget on motion.

But:

- The more complex the pattern, the larger \(C_{\text{int}}\).
- The more energy you pump into it (heat, turbulence, internal dynamics), the larger \(B_{\text{int}}\) must be to keep it coherent.
- That leaves **less** budget for motion.

In the limiting case:

\[
B_{\text{int}} \to B_{\text{tot}} \quad \Rightarrow \quad B_{\text{move}} \to 0 \quad \Rightarrow \quad v_{\text{eff}} \to 0
\]

So **trying to push a complex pattern harder** (more internal excitation) actually **reduces** the budget available for motion.

This is the tick-frame analogue of “relativistic mass increase” and the impossibility of accelerating massive objects to \(c\).

---

## 5. Formal statement of the active propulsion limit

Let:

- \(B_{\text{tot}} = 1\) (normalized tick-budget per tick for the pattern)
- \(C_{\text{int}}\) = minimal internal complexity cost per tick to maintain identity
- Assume **no borrowing** from external fields (purely self-driven motion)

Then:

1. **Stability condition:**

   \[
   B_{\text{int}} \geq C_{\text{int}}
   \]

2. **Motion budget:**

   \[
   B_{\text{move}} = 1 - B_{\text{int}} \leq 1 - C_{\text{int}}
   \]

3. **Effective velocity:**

   \[
   v_{\text{eff}} = c_{\text{sub}} \cdot B_{\text{move}} \leq c_{\text{sub}} \cdot (1 - C_{\text{int}})
   \]

4. **Active propulsion limit:**

   \[
   v_{\text{eff}}^{\text{(active)}} \leq c_{\text{sub}} \cdot (1 - C_{\text{int}})
   \]

Where:

- For **simple patterns** (e.g. photons), \(C_{\text{int}} \approx 0\) → \(v_{\text{eff}}^{\text{(active)}} \approx c_{\text{sub}}\).
- For **highly complex patterns** (e.g. rockets, humans), \(C_{\text{int}}\) is large → \(v_{\text{eff}}^{\text{(active)}} \ll c_{\text{sub}}\).

In the extreme:

- If \(C_{\text{int}} \to 1\), then \(v_{\text{eff}}^{\text{(active)}} \to 0\).  
  The pattern is so complex that **all** tick-budget is consumed just to keep it coherent; it cannot actively move at all.

---

## 6. Relation to relativity

This tick-frame limit reproduces the spirit of special relativity:

- **Nothing complex can be accelerated to the speed of light** by its own propulsion, because:
    - increasing energy → increasing internal activity → increasing \(B_{\text{int}}\) → decreasing \(B_{\text{move}}\) → saturating \(v_{\text{eff}}\) below \(c_{\text{sub}}\).

- **Light is special** because:
    - it is the **simplest possible pattern**, with minimal internal complexity,
    - almost all tick-budget can be used for motion,
    - so it naturally travels at \(c_{\text{sub}}\).

The key difference in ontology:

- SR: limit arises from spacetime geometry and Lorentz transformations.
- Tick-frame: limit arises from **local tick-budget allocation and pattern complexity**.

---

## 7. Active vs passive motion

This limit applies to **active propulsion**:

> The pattern itself is spending its own tick-budget to move.

It does **not** forbid:

- **Passive motion** along geodesics in a time-gradient field,
- Being **carried** by substrate-level flows (e.g. cosmological expansion, gravitational free fall).

In those cases:

- The pattern’s internal tick-budget is mostly spent on regeneration,
- While its *position* changes because the **field configuration itself** is evolving,
- So its **effective velocity relative to another frame** can be high, even if its own active motion budget is small.

---

## 8. Summary

- Every pattern has a **minimal internal regeneration cost** \(C_{\text{int}}\).
- Tick-budget per tick is finite: \(B_{\text{tot}}\).
- Whatever remains after internal regeneration, \(B_{\text{move}} = B_{\text{tot}} - B_{\text{int}}\), is all that’s available for motion.
- Effective velocity under active propulsion is:

  \[
  v_{\text{eff}} = c_{\text{sub}} \cdot B_{\text{move}} \leq c_{\text{sub}} \cdot (1 - C_{\text{int}})
  \]

- **Complex patterns (rockets, humans) cannot be actively accelerated anywhere near \(c_{\text{sub}}\)**, because their internal complexity consumes most of their tick-budget.
- **Light** is fast not because it is “special by decree”, but because it is the **simplest possible pattern**.

This is the **Active Propulsion Limit** in tick-frame space.
