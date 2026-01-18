# Dimension Definition in Tick‑Frame Space

## Overview

Dimension is not a property of the substrate, but a **model property of the observer**, who reconstructs space from
temporal latencies, causal relations, and stable gradients of information propagation.  
Dimension is therefore the **minimal number of independent parameters** the observer needs to explain all measured
latencies between events.

---

## Formal Definition

Let there be a set of events \(E = \{E_1, E_2, \dots, E_n\}\) captured by the observer in the tick stream of the
substrate.  
Each event has an arrival time \(t_i\).

Define the **causal latency matrix**:

\[
L_{ij} = t_j - t_i
\]

The observer seeks the smallest integer \(d\) for which there exists an assignment of coordinates:

\[
X_i \in \mathbb{R}^d
\]

such that for all pairs of events:

\[
L_{ij} = \frac{1}{c} \cdot \|X_j - X_i\|
\]

where \(c\) is the effective speed of information propagation in the substrate.

**The dimension of the observer’s space is precisely this minimal \(d\).**

---

## Interpretation

- Dimension corresponds to the **number of independent causal directions** detected by the observer.
- Dimension is the **rank** of the latent space that best explains all latencies.
- Dimension is **subjective**: different observers may reconstruct different dimensions depending on their horizon,
  surfing speed, and filtering rules.

---

## Operational Procedure

1. The observer collects events and their arrival times.
2. Builds the latency matrix \(L\).
3. Seeks the smallest \(d\) for which coordinates \(X_i \in \mathbb{R}^d\) can reproduce \(L\).
4. If three independent latency gradients exist, the observer reconstructs 3D space.
5. If four exist, the observer reconstructs 4D space, and so on.

---

## Worked Examples

### Example 1: 1D Reconstruction

Events:  
\[
t_1 = 0, \quad
t_2 = 3, \quad
t_3 = 4
\]

Latency matrix:
\[
L =
\begin{bmatrix}
0 & 3 & 4 \\
-3 & 0 & 1 \\
-4 & -1 & 0
\end{bmatrix}
\]

Distances are consistent along a line:  
\(x_1 = 0, x_2 = 3, x_3 = 4\).  
✅ Minimal dimension = **1D**.

---

### Example 2: Jump to 2D

Events with distances forming a square:  
\[
X_1 = (0,0), \quad
X_2 = (3,0), \quad
X_3 = (0,4), \quad
X_4 = (3,4)
\]

Latencies cannot be embedded consistently on a line, but fit in a plane.  
✅ Minimal dimension = **2D**.

---

### Example 3: Jump to 3D

Events with distances forming a tetrahedron:  
\[
X_1 = (0,0,0), \quad
X_2 = (1,1,0), \quad
X_3 = (1,0,1), \quad
X_4 = (0,1,1)
\]

Pairwise distances are non‑coplanar, requiring volume.  
✅ Minimal dimension = **3D**.

---

### Example 4: Jump to 4D

Consider five events with equal pairwise distances (a regular 4‑simplex).  
This structure cannot be embedded in 3D without distortion.  
Coordinates (one possible embedding):

\[
X_1 = (1,0,0,0), \quad
X_2 = (0,1,0,0), \quad
X_3 = (0,0,1,0), \quad
X_4 = (0,0,0,1), \quad
X_5 = (-1,-1,-1,-1)
\]

All pairwise distances are equal.  
✅ Minimal dimension = **4D**.

---

### Example 5: Jump to 5D

Consider six events with equal pairwise distances (a regular 5‑simplex).  
This requires five independent axes.  
Coordinates (one possible embedding):

\[
X_1 = (1,0,0,0,0), \quad
X_2 = (0,1,0,0,0), \quad
X_3 = (0,0,1,0,0), \quad
X_4 = (0,0,0,1,0), \quad
X_5 = (0,0,0,0,1), \quad
X_6 = (-1,-1,-1,-1,-1)
\]

Again, all pairwise distances are equal.  
✅ Minimal dimension = **5D**.

---

## Key Insight

Dimension is not fixed at 3D. It is the **minimal number of axes required to embed all causal latencies consistently
**.  
Depending on the structure of events, the observer may reconstruct 1D, 2D, 3D, or higher dimensions.
