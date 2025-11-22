# Discrete Time–Space Model: Velocity and Relativistic Effects

---

## ⚙️ Velocity Definition

### Fundamental Definition
In continuous physics:
\[
v = \frac{\Delta x}{\Delta t}
\]

In your discrete model:
- **Δx** = number of Planck-length steps  
- **Δt** = number of Planck-time ticks  
- **Velocity becomes**:
\[
v = \frac{n_{\text{steps}} \cdot \ell_P}{n_{\text{ticks}} \cdot t_P}
\]

In natural units (\(c = 1\), \(\ell_P = t_P = 1\)):
\[
v = \frac{n_{\text{steps}}}{n_{\text{ticks}}}
\]

---

### Velocity Constraints
- **Maximum velocity**:
  \[
  v_{\text{max}} = \frac{1 \cdot \ell_P}{1 \cdot t_P} = c
  \]
  → One spatial step per tick = lightlike motion

- **Massive motion**:
  \[
  v < c \Rightarrow n_{\text{ticks}} > n_{\text{steps}}
  \]
  → Timelike worldlines require more ticks than steps

- **Stationary**:
  \[
  v = 0 \Rightarrow n_{\text{steps}} = 0
  \]

---

### Velocity as a Testable Ratio
- **Discrete velocity**:
  \[
  v_{\text{discrete}} = \frac{\text{steps taken}}{\text{ticks elapsed}}
  \]

- **Effective velocity**:
  \[
  v_{\text{eff}} = \frac{\|\mathbf{x}_{\text{final}} - \mathbf{x}_{\text{start}}\|}{\text{ticks elapsed}}
  \]

This allows tracking motion across dimensions and comparing agents or sources.

---

### Velocity and Interval Classification
Use velocity to classify motion:
- If \(v = 1\): lightlike  
- If \(v < 1\): timelike  
- If \(v > 1\): invalid (violates causality)

Check with discrete Minkowski interval:
\[
s^2 = (\Delta t)^2 - \|\Delta \mathbf{x}\|^2
\]
- \(s^2 = 0\) → lightlike  
- \(s^2 > 0\) → timelike  
- \(s^2 < 0\) → forbidden

---

## ⏱️ Relativistic Effects: Tick vs Frame

### Time Dilation
- **Ticks**: substrate heartbeat, one Planck update per tick.  
- **Frames**: aggregated snapshots, rendered after many ticks.  
- **Effect**: At high velocity, agents consume nearly one tick per step.  
  - Tick-level: motion appears normal.  
  - Frame-level: fewer commits per frame → clocks appear slower.  

### Length Contraction
- **Distance**: defined by Planck steps.  
- **Frame aggregation**: coarse sampling can make paths appear shorter.  
- **Interpretation**: contraction is a perceptual artifact of frame granularity.

---

## 🔢 Numerical Example

### Setup
- Natural units: \(c=1, \ell_P = t_P = 1\).  
- Displacement: \(D = 10\) steps.  
- True velocity: \(v_{\text{true}} = 0.8c\).  
- Ticks per frame: 10, 100, 1000.

---

### Tick-Level Ground Truth
- Ticks required:
  \[
  N_{\text{ticks}} = \frac{10}{0.8} = 12.5 \Rightarrow 13
  \]
- Interval:
  \[
  s^2 = 13^2 - 10^2 = 69 > 0
  \]
→ Timelike motion, consistent with causality.

---

### Frame-Level Observations

**Case A: 10 ticks/frame**
- Frames: \(13/10 \approx 2\).  
- Rendered time: 20 ticks.  
- Naïve velocity: \(10/20 = 0.5\).  
- Corrected velocity: \(10/13 \approx 0.769\).

**Case B: 100 ticks/frame**
- Frames: \(13/100 \approx 1\).  
- Rendered time: 100 ticks.  
- Naïve velocity: \(10/100 = 0.1\).  
- Corrected velocity: \(10/13 \approx 0.769\).

**Case C: 1000 ticks/frame**
- Frames: \(13/1000 \approx 1\).  
- Rendered time: 1000 ticks.  
- Naïve velocity: \(10/1000 = 0.01\).  
- Corrected velocity: \(10/13 \approx 0.769\).

---

### Comparison Table

| Case | Ticks per frame | Frames elapsed | Naïve rendered velocity | Corrected rendered velocity | True velocity |
|------|-----------------|----------------|--------------------------|-----------------------------|---------------|
| A    | 10              | 2              | 0.50                     | 0.769                       | 0.769         |
| B    | 100             | 1              | 0.10                     | 0.769                       | 0.769         |
| C    | 1000            | 1              | 0.01                     | 0.769                       | 0.769         |

---

## ✅ Takeaway
- **Distance and velocity are tick-level quantities.**  
- **Frames are perceptual aggregations** that can distort apparent kinematics.  
- **Relativistic effects** (time dilation, length contraction) emerge as artifacts of the mismatch between tick-level causality and frame-level rendering.  
- To preserve physics, always compute kinematics from tick logs; treat frames as visualization boundaries, not clocks.