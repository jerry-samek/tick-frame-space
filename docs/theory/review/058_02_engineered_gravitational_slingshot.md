# TF‑E‑059: Engineered γ‑Corridor Slingshot (Geodesic Railgun)

**Category:** Tick‑Frame Experiment  
**Status:** Design Draft  
**Goal:** Demonstrate a predictable, aimable slingshot using an engineered γ‑corridor and γ‑gate, enabling a test entity to gain escape‑level effective velocity without active propulsion.

---

## 1. Objective

Show that:

1. A deliberately shaped γ‑corridor can **capture and guide** entities along a predefined path (geodesic rail).
2. A γ‑gate at the end of the corridor can **split geodesics** into:
    - bound trajectories (remaining in the system),
    - escape trajectories (leaving the system).
3. The resulting escape trajectories exhibit **higher asymptotic effective velocity** than the initial state, with:
    - no active thrust,
    - all local updates remaining sub‑\(c_{\text{sub}}\).

---

## 2. Base configuration

- **Engine version:** v10 (or later) with validated geodesics and γ‑field behavior.
- **Domain:** 2D or 3D grid (start with 2D for clarity).
- **Boundary conditions:**
    - Preferably open or weakly absorbing boundaries to allow escape trajectories.
- **Natural sources:**
    - Either:
        - remove the main planet cluster, or
        - place it far enough that its γ‑influence is negligible in the experiment region.

---

## 3. Field dynamics with engineered source

Use the standard load field update with an engineered source term:

\[
L'(x,t) = L(x,t) + \alpha \nabla^2 L(x,t) + S_{\text{nat}}(x) + S_{\text{eng}}(x,t) - \gamma L(x,t)^2
\]

Where:

- \(S_{\text{nat}}(x)\): natural sources (can be zero or minimal here),
- \(S_{\text{eng}}(x,t)\): engineered source shaping the γ‑corridor and γ‑gate.

The time‑flow field is:

\[
\gamma(x,t) = \frac{\text{work\_done}(x,t)}{\text{substrate\_ticks}}
\]

Entities move according to:

\[
\vec{a}(x,t) = k \cdot \nabla \gamma(x,t)
\]

---

## 4. Engineered γ‑corridor

### 4.1 Corridor axis

Define a simple straight line as the corridor axis:

- In 2D: \(\Gamma(s) = (x_0 + s, y_0)\), with \(s \in [0, L]\).

### 4.2 Distance from axis

For any position \(x = (x,y)\):

\[
d(x) = |y - y_0|
\]

### 4.3 Corridor source term

Define a tube‑like engineered source:

\[
S_{\text{corr}}(x) = A(s(x)) \cdot \exp\left(-\frac{d(x)^2}{2\sigma^2}\right)
\]

Where:

- \(\sigma\): corridor half‑width (stabilization radius),
- \(A(s)\): longitudinal strength profile along the corridor.

For the first experiment, use a simple constant profile:

\[
A(s) = A_0 \quad \text{for } s \in [0, L]
\]

and zero outside.

This should create:

- **longitudinal gradient** along \(\Gamma\) (pulling forward),
- **transverse gradient** toward \(\Gamma\) (keeping entities inside the corridor).

---

## 5. Engineered γ‑gate (escape vs bound)

Place a γ‑gate at the end of the corridor, around \(s = L\).

### 5.1 Gate position

- Gate center: \(x_{\text{gate}} = (x_0 + L, y_0)\).

### 5.2 Gate source term (sedle‑like)

Define an additional source:

\[
S_{\text{gate}}(x) = B \cdot \exp\left(-\frac{\|x - x_{\text{gate}}\|^2}{2\rho^2}\right) \cdot G(\theta(x))
\]

Where:

- \(\rho\): gate radius,
- \(\theta(x)\): angle of \(x - x_{\text{gate}}\) relative to corridor axis,
- \(G(\theta)\): angular modulation shaping the escape vs bound directions.

For a simple two‑branch gate:

- Let corridor axis be along +x.
- Define:

    - escape direction: small cone around +x,
    - bound direction: small cone around −x or sideways.

Example:

\[
G(\theta) =
\begin{cases}
+1 & \text{if } |\theta| < \theta_{\text{esc}} \\
-1 & \text{if } \theta_{\text{bound,min}} < \theta < \theta_{\text{bound,max}} \\
0 & \text{otherwise}
\end{cases}
\]

This creates:

- a **γ‑slope outward** in the escape cone,
- a **γ‑barrier or return slope** in the bound cone.

### 5.3 Total engineered source

\[
S_{\text{eng}}(x,t) = S_{\text{corr}}(x) + S_{\text{gate}}(x)
\]

(Time dependence can be added later for gating windows; first experiment can be static.)

---

## 6. Test entities and initial conditions

### 6.1 Entity model

- Use the standard test entity model from v10:
    - point‑like or small pattern,
    - no internal propulsion,
    - purely geodesic motion (only field‑driven).

### 6.2 Initial positions

Place entities upstream of the corridor entrance:

- Positions: around \((x_0 - D_{\text{in}}, y_0)\),
- With small lateral offsets: \(y \in [y_0 - \Delta, y_0 + \Delta]\).

### 6.3 Initial velocities

- Magnitude: small, sub‑relativistic (e.g. \(0.01\,c_{\text{sub}}\)),
- Direction: roughly toward the corridor entrance (small angular spread).

---

## 7. Observables and logging

For each entity:

- **Trajectory** \(x(t)\) over the full simulation.
- **γ along path**: \(\gamma(x(t), t)\).
- **Velocity** \(\vec{v}(t)\) and its magnitude \(\|\vec{v}(t)\|\).
- **Fate classification:**
    - captured by corridor (yes/no),
    - exits via escape branch (yes/no),
    - remains bound (yes/no),
    - trapped or chaotic (yes/no).

Global:

- γ‑field snapshots at key times,
- vector field of \(\nabla \gamma\) in the corridor and gate region.

---

## 8. Success criteria

The experiment is considered successful if:

1. **Corridor capture:**  
   A non‑trivial fraction of entities entering the region are:
    - drawn into the corridor,
    - stabilized around the axis,
    - guided along \(\Gamma(s)\) toward the gate.

2. **Geodesic splitting at gate:**  
   At least two distinct classes of trajectories emerge at the gate:
    - **escape trajectories:** entities leaving the system along a well‑defined direction,
    - **bound trajectories:** entities remaining in a bounded region or returning inward.

3. **Velocity gain:**  
   For escape trajectories:

   \[
   \|\vec{v}_{\text{out}}\| > \|\vec{v}_{\text{in}}\|
   \]

   relative to the initial frame, with:

    - no active propulsion,
    - all local updates respecting \(c_{\text{sub}}\).

4. **Predictability:**  
   Small variations in initial conditions (within a designed capture range) lead to:
    - qualitatively similar escape trajectories,
    - similar asymptotic velocities.

---

## 9. Extensions and next steps

If the basic experiment succeeds:

1. **Profile shaping:**
    - Vary \(A(s)\) to create acceleration profiles (slow start, strong mid‑boost, soft exit).
2. **Time‑gated γ‑gate:**
    - Make \(S_{\text{gate}}(x,t)\) time‑dependent to create launch windows.
3. **Curved corridors:**
    - Replace straight \(\Gamma(s)\) with a curved path (e.g. bending around a natural planet).
4. **3D implementation:**
    - Extend to 3D with cylindrical corridors and conical escape regions.

---

## 10. Summary

This experiment defines a concrete, implementable setup to test:

- whether an engineered γ‑corridor can act as a **geodesic railgun**, and
- whether a γ‑gate can provide a **predictable, aimable slingshot** that sends entities onto escape trajectories with higher effective velocities, without any active propulsion.

It is the first explicit engineering‑layer test of **field‑shaped geodesic propulsion** in tick‑frame space.
