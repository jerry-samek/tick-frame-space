# Velocity in Discrete Time–Space

## ⚙️ Fundamental Definition
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

## 🚦 Velocity Constraints
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

## 📏 Velocity as a Testable Ratio
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

## 🧠 Velocity and Interval Classification
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

## ✅ Summary
> **Velocity = number of Planck steps per number of Planck ticks**, bounded by \(v \le c\).  
> It’s a ratio of discrete motion over discrete time, and it directly determines whether motion is lightlike, timelike, or causality-breaking.

## Notes
- We use the **Euclidean norm** for \(\|\Delta \mathbf{x}\|\) unless otherwise noted.
- In cases where ticks < frame size, we log **one full frame plus remainder**.  No partial frames are rendered.