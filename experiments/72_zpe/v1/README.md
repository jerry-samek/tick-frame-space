# **Experiment 72 — V1: Fixed‑Tick Energy, Growing Grid, Jitter–Gamma Interaction**

## **1. Objective**

Verify a minimal universe model where:

1. **Each entity receives exactly 1 quantum of energy per tick**  
   → exactly **one state update**, no more, no less.

2. The **grid expands over time**, but the global ratio  
   \[
   \frac{\text{total energy per tick}}{\text{number of entities}} = 1
   \]  
   remains automatically satisfied.

3. **Jitter** and **gamma field** influence *how* the single update is used  
   (stability vs. change), not *how many* updates occur.

4. Stable structures (“bound clusters”) can form and persist even as the grid grows.

---

## **2. Substrate**

- **Space:** 2D grid, initial size \(N_0 \times N_0\) (e.g., 64×64).
- **Time:** discrete ticks \(t = 0,1,2,\dots\).
- **Cell:** either empty or containing exactly **one entity**.

---

## **3. Entity State**

Each occupied cell has:

- `mass`: 0 or 1
- `bound`: 0 or 1
- `vel`: optional (ignored in V1)

Minimal V1 uses only:

- `mass`
- `bound`

---

## **4. Fields**

### **4.1 Gamma field \(\gamma(x,t)\)**

V1 definition:

\[
\gamma(x,t) = \text{number of occupied neighbors in the 8‑cell Moore neighborhood}
\]

Interpretation:  
More neighbors → stronger effective gravitational pull.

---

### **4.2 Jitter field \(J(x,t)\)**

Decomposition:

\[
J(x,t) = J_0(t) + \delta J(x,t)
\]

- **Global jitter \(J_0(t)\)**
    - V1: constant, e.g. \(J_0 = 0.5\)

- **Local jitter \(\delta J(x,t)\)**
    - V1: random value in \([-a, a]\), e.g. \(a = 0.1\)

---

## **5. Update Rule (One Update per Entity per Tick)**

For each cell \(x\) at tick \(t\):

1. If `mass = 0`:
    - cell remains empty.

2. If `mass = 1`:
    - compute \(\gamma(x,t)\)
    - compute \(J(x,t)\)
    - compute ratio:
      \[
      R(x,t) = \frac{J(x,t)}{\gamma(x,t) + \epsilon}
      \]
      with \(\epsilon = 0.1\) to avoid division by zero.

3. **Binding rule (V1, no movement):**

    - If `bound = 1` (entity is part of a structure):
        - if \(R < T_{\text{stay}}\): remain bound
        - if \(R \ge T_{\text{stay}}\): become unbound

    - If `bound = 0` (free entity):
        - if \(R < T_{\text{bind}}\) **and** \(\gamma \ge G_{\text{min}}\): become bound
        - otherwise remain free

Typical V1 thresholds:

- \(T_{\text{stay}} = 0.7\)
- \(T_{\text{bind}} = 0.3\)
- \(G_{\text{min}} = 2\)

4. **Energy constraint:**
    - Each entity performs **exactly one** such update.
    - No multi‑step behavior, no extra actions.

---

## **6. Grid Growth**

### **6.1 Growth schedule**

Every \(K\) ticks (e.g., \(K = 50\)):

- expand the grid by 1 cell on each side  
  → from \(N \times N\) to \((N+2) \times (N+2)\)

- new cells start as `mass = 0`

### **6.2 Energy interpretation**

- Number of entities = number of occupied cells
- Each entity has 1 energy quantum per tick
- Therefore:
  \[
  E_{\text{total}}(t) = N_{\text{entities}}(t)
  \]

Grid growth does **not** change energy distribution; it only increases potential space.

---

## **7. Initial Conditions**

- Grid: 64×64
- Randomly occupy 10–20% of cells (`mass = 1`)
- Initial `bound`:
    - either all `bound = 0`, or
    - small random fraction (e.g., 5%) set to `bound = 1`

---

## **8. Metrics to Log**

1. Total number of entities \(N_{\text{entities}}(t)\)
2. Number of bound entities \(N_{\text{bound}}(t)\)
3. Bound fraction:
   \[
   f_{\text{bound}}(t) = \frac{N_{\text{bound}}(t)}{N_{\text{entities}}(t)}
   \]
4. Distribution of \(\gamma(x,t)\)
5. Distribution of \(R(x,t)\)
6. Visual maps of:
    - bound vs. free entities
    - cluster formation over time
    - effect of grid expansion

---

## **9. Success Criteria**

Experiment 72 (V1) is successful if:

1. **Energy rule is never violated**
    - no entity performs more than one update per tick
    - no entity occupies more than one cell

2. **Stable structures form and persist**
    - clusters of bound entities survive grid expansion

3. **Jitter–gamma interaction behaves meaningfully**
    - tuning \(J_0\), \(a\), or thresholds changes structure formation
    - but never breaks the fixed‑tick energy rule
