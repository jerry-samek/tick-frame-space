### Experimental specification: fixed‑tick energy and growing grid

#### 1. Objective

Test a cellular‑automaton universe where:

- **Each entity** receives exactly **1 tick of energy per tick** (1 update, 1 cell, 1 state change max).
- The **grid grows in time** such that the **global ratio**  
  \[
  \frac{\text{total available energy per tick}}{\text{number of entities}} = 1
  \]
  is always preserved.
- **Jitter** and **gamma field** only affect *how* the one tick is used, not *how many* ticks entity gets.

---

#### 2. Core assumptions

1. **Discrete substrate**
    - Time is discrete: \(t = 0,1,2,\dots\)
    - Space is a 2D grid of cells (boxes).
    - Each cell hosts at most **one entity**.

2. **Energy per entity**
    - Each entity has exactly **1 energy quantum per tick**.
    - This corresponds to **exactly one state update per tick**.
    - No entity may:
        - skip a tick,
        - perform multiple updates per tick,
        - occupy multiple cells.

3. **Grid growth**
    - The grid expands in time (e.g. by adding a layer of cells at the boundary).
    - When a new cell becomes active (new entity appears), it is assumed to come with its own **1 tick energy budget**.
    - The global constraint:
      \[
      \frac{E_{\text{total}}(t)}{N_{\text{entities}}(t)} = 1
      \]
      must hold at every tick \(t\).

---

#### 3. Fields and parameters

1. **Gamma field \(\gamma(x,t)\)**
    - Represents effective gravitational potential / curvature at cell \(x\) and time \(t\).
    - Can be derived from mass distribution or defined by a rule.

2. **Jitter field \(J(x,t)\)**
    - Decomposed into:
      \[
      J(x,t) = J_0(t) + \delta J(x,t)
      \]
    - **\(J_0(t)\)**: global background jitter (cosmological component), same for all cells at given tick.
    - **\(\delta J(x,t)\)**: local deviation (structure‑forming component), depends on local configuration.

3. **State of entity**
    - Each entity at cell \(x\) has a state \(S(x,t)\) (e.g. mass, velocity flag, bound/free, etc.).

---

#### 4. Update rule (per tick, per entity)

For each cell \(x\) at time \(t\):

1. **Inputs to the rule**
    - Current state: \(S(x,t)\)
    - Neighbor states: \(S(\text{neighbors of }x,t)\)
    - Local gamma: \(\gamma(x,t)\)
    - Global jitter: \(J_0(t)\)
    - Local jitter: \(\delta J(x,t)\)

2. **Single update constraint**
    - Exactly **one** application of the update function:
      \[
      S(x,t+1) = F\big(S(x,t), S_{\text{neighbors}}(t), \gamma(x,t), J_0(t), \delta J(x,t)\big)
      \]
    - No additional sub‑steps or multiple moves per tick.

3. **Interpretation of jitter**
    - Jitter **does not** change the number of updates.
    - Jitter modifies **how the one update is “spent”**, e.g.:
        - probability or tendency to:
            - stay bound vs. become free,
            - move vs. remain,
            - collapse vs. disperse,
        - sensitivity to \(\gamma(x,t)\).

---

#### 5. Grid growth protocol

1. **Expansion schedule**
    - Define a rule for grid growth, e.g.:
        - every \(k\) ticks, add one cell layer around the existing grid, or
        - grow boundary by 1 cell per tick.
2. **New entities**
    - When a new cell is added:
        - initialize its state \(S(x,t)\),
        - assign it the same **1 tick energy** (one update) as all others.
3. **Energy consistency check**
    - At each tick:
        - count entities \(N_{\text{entities}}(t)\),
        - verify that the model semantics preserve:
          \[
          E_{\text{total}}(t) = N_{\text{entities}}(t)
          \]
          (one energy quantum per entity per tick).

---

#### 6. Experimental goals

1. **Stability under growth**
    - Check whether structures (bound regions, “galaxies”) remain stable as the grid grows and \(J_0(t)\) possibly
      changes.

2. **Effect of global jitter \(J_0(t)\)**
    - Vary \(J_0(t)\) slowly in time and observe:
        - whether global behavior changes (e.g. tendency to expand/collapse),
        - while respecting the “1 tick per entity” constraint.

3. **Effect of local jitter \(\delta J(x,t)\)**
    - Introduce localized variations in \(\delta J\) and observe:
        - formation, survival, or dissolution of structures,
        - sensitivity to \(\gamma(x,t)\).

4. **Conservation principle**
    - Verify that:
        - no entity ever performs more than one update per tick,
        - no entity ever occupies more than one cell,
        - global ratio energy/entities remains 1 at all times.
