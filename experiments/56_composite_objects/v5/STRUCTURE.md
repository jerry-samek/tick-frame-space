# 🧩 Spatial Hierarchy and Pattern Structure in the Tick‑Frame Model

## 1. Planck Cell
The smallest granular unit of space.

- represents the **atomic grid unit**
- carries a field value: `−1`, `0`, or `+1`
- receives **exactly 1 quantum of jitter per tick**
- acts as the fundamental “pixel of reality”

**Interpretation:**  
A Planck cell is the minimal carrier of information, energy, and jitter.

---

## 2. Sample Cell
A block composed of multiple Planck cells.

- typically **3×3**, **5×5**, or **7×7**
- defines the **maximum spatial extent of a pattern**
- acts as the “canvas” on which a local field configuration can exist

**Recommended default:**  
**5×5 Planck cells**  
→ enough room for gradients, asymmetry, direction, and phase  
→ still small enough to remain a local field fragment

---

## 3. Pattern
A specific configuration of `−1/0/+1` values inside a single sample cell.

- represents a **local fragment of the field**
- not a classical “particle”
- a small, self‑maintaining structure that interacts with the gamma field
- can encode direction, phase, internal gradients, and local dynamics

**Pattern jitter:**

\[
J_{\text{pattern}} = \sum_{\text{active Planck cells}} J_{\text{Planck}}
\]

For a 5×5 sample:

\[
J_{\text{pattern,max}} = 25 \cdot J_{\text{Planck}}
\]

---

## 4. Field Fragment
The tick‑frame equivalent of what used to be a “particle” in the float‑based design.

- **one field fragment = one pattern inside one sample cell**
- an “electron” is **not** a point
- an electron is a **stable, emergent configuration of many field fragments**
- field fragments collectively form structures (orbital, wave‑like, binding)

**Key shift:**  
In the float world, an electron was a **point**.  
In the tick‑frame world, an electron is a **process** made of many patterns.

---

# 🔄 Matching the Old Float Behavior

## 1. Choosing the Sample Size
Pick a sample size that corresponds to the old “interaction zone” (e.g., collision radius 0.5).

- 3×3 → too small, limited structure
- **5×5 → ideal balance**
- 7×7 → richer patterns, less local

---

## 2. Jitter Equivalence
A float‑based particle had jitter `J_float`.

To match that behavior:

\[
J_{\text{Planck}} = \frac{J_{\text{float}}}{A_{\text{pattern}}}
\]

where  
\( A_{\text{pattern}} \) = number of active Planck cells (max 25 for 5×5).

This preserves the **energy scale** of the original system.

---

## 3. Field Density Equivalence
In the float world:

- 50 fragments = 50 point particles

In the tick‑frame world:

- 50 fragments = 50 patterns (each 5×5)

The field becomes **richer and more structured**, because each fragment now has internal geometry.

---

# 🧭 Summary

- **Planck cell** = atomic spatial unit, 1 jitter
- **Sample cell** = canvas for a pattern (recommended 5×5)
- **Pattern** = local field fragment, not a particle
- **Field fragment** = one pattern; electrons are emergent multi‑fragment structures
- **Pattern jitter** = active Planck cells × jitter_per_cell
- **Float equivalence** is achieved by tuning jitter_per_cell and sample size
