# Experiment 77 v1 — Gamma field dissolution & geometric dilution (1D vs 2D vs 3D)

---

## 1. Goal

**Goal:** Empirically show that a localized gamma “well”:

- in **1D**: mainly spreads by smoothing, with no true geometric dilution,
- in **2D**: weakens faster as it spreads over area,
- in **3D**: weakens even faster, following a Newtonian‑like \( \sim 1/r^2 \) behavior from pure geometry.

All with **no explicit decay constant**—only the field update rule.

---

## 2. Common setup

**Field type:** scalar gamma field.  
**Background:** uniform \(\gamma_0\).  
**Imprint:** single localized peak of amplitude \(A\) at the center.

**Per‑tick update (all variants):**

1. **Smoothing/diffusion:** local averaging via small kernel.
2. **Optional normalization:** keep total gamma “mass” constant.
3. **No explicit decay term** (no \(-k \cdot \gamma\)).

You’re only allowed to use:  
**local smoothing + time + dimensionality.**

---

## 3. Variant A — 1D line

**Field:** \(\gamma(x)\) on a 1D array of length \(N\).

**Initialization:**

- Set all cells:  
  \(\gamma(x) = \gamma_0\).
- Add central peak:  
  \(\gamma(x_0) = \gamma_0 + A\), where \(x_0 = N/2\).

**Tick update:**

- Apply 1D kernel, e.g.:

  \[
  \gamma'(x) = 0.25 \cdot \gamma(x-1) + 0.5 \cdot \gamma(x) + 0.25 \cdot \gamma(x+1)
  \]

- Optionally renormalize:

  \[
  \sum_x \gamma'(x) = \sum_x \gamma(x)
  \]

**Measurements per tick:**

- **Peak:**  
  \(\gamma_{\text{max}}(t) = \max_x \gamma_t(x)\)
- **Width:** number of cells with \(\gamma_t(x) > \gamma_0 + \epsilon\)
- **Total mass:** \(\sum_x \gamma_t(x)\)

**Expected behavior (1D):**

- Peak decreases **slowly**, mostly due to smoothing.
- No geometric dilution—pattern just spreads along the line.
- With normalization, total mass constant.

---

## 4. Variant B — 2D grid

**Field:** \(\gamma(x, y)\) on an \(N \times N\) grid.

**Initialization:**

- Set all cells:  
  \(\gamma(x, y) = \gamma_0\).
- Add central peak:  
  \(\gamma(x_0, y_0) = \gamma_0 + A\), where \(x_0 = y_0 = N/2\).

**Tick update:**

- Apply 2D kernel, e.g. 3×3:

  \[
  K = \frac{1}{16}
  \begin{bmatrix}
  1 & 2 & 1 \\
  2 & 4 & 2 \\
  1 & 2 & 1
  \end{bmatrix}
  \]

  \[
  \gamma'(x, y) = \sum_{i,j} K_{i,j} \cdot \gamma(x+i, y+j)
  \]

- Optional normalization:

  \[
  \sum_{x,y} \gamma'(x,y) = \sum_{x,y} \gamma(x,y)
  \]

**Measurements per tick:**

- **Peak:**  
  \(\gamma_{\text{max}}(t) = \max_{x,y} \gamma_t(x,y)\)
- **Radial profile:** for radius \(r\), average over ring:

  \[
  \bar{\gamma}(r, t) = \text{mean of } \gamma_t(x,y) \text{ with } \sqrt{(x-x_0)^2 + (y-y_0)^2} \approx r
  \]

- **Total mass:** \(\sum_{x,y} \gamma_t(x,y)\)

**Expected behavior (2D):**

- Peak drops **faster** than in 1D.
- Pattern spreads radially; amplitude falls as area \(\sim r^2\) grows.
- With normalization, total mass constant, but local strength clearly diluted.

---

## 5. Variant C — 3D grid (Newtonian‑like behavior)

**Field:** \(\gamma(x, y, z)\) on an \(N \times N \times N\) grid (can be coarse).

**Initialization:**

- Set all cells:  
  \(\gamma(x, y, z) = \gamma_0\).
- Add central peak:  
  \(\gamma(x_0, y_0, z_0) = \gamma_0 + A\), where all centers are \(N/2\).

**Tick update:**

- Apply 3D smoothing kernel, e.g. separable or small 3×3×3 Gaussian‑like kernel.
- Optional normalization:

  \[
  \sum_{x,y,z} \gamma'(x,y,z) = \sum_{x,y,z} \gamma(x,y,z)
  \]

**Measurements per tick:**

- **Peak:**  
  \(\gamma_{\text{max}}(t) = \max_{x,y,z} \gamma_t(x,y,z)\)
- **Radial profile:** for radius \(r\), average over sphere:

  \[
  \bar{\gamma}(r, t) = \text{mean of } \gamma_t(x,y,z) \text{ with } \sqrt{(x-x_0)^2 + (y-y_0)^2 + (z-z_0)^2} \approx r
  \]

- **Total mass:** \(\sum_{x,y,z} \gamma_t(x,y,z)\)

**Expected behavior (3D, Newtonian‑like):**

- Peak drops **even faster** than in 2D.
- Radial profile should approximate a falloff consistent with spreading over spherical shells (area \(\sim 4\pi r^2\)).
- With normalization, total mass constant, but local strength decays roughly like a Newtonian field:  
  \(\bar{\gamma}(r) \propto 1/r^2\) (up to kernel/finite‑grid effects).

---

## 6. What Experiment 77 v1 proves

- **Same update rule**, no decay constant, no propagation rule.
- **Only dimensionality changes.**

We should see:

- 1D: strong coupling, slow weakening, no true geometric dilution.
- 2D: faster weakening via area growth.
- 3D: Newtonian‑like dilution via spherical expansion.

That’s the **Geometric Dilution Principle** made visible.
