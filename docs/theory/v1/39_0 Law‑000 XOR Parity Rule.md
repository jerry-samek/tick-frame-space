# Law‑000: XOR Parity Rule

**Status:** Draft 1  
**Purpose:** Define the minimal, parameter‑free evolution rule for a discrete substrate.  
**Scope:** Substrate, node state, local update rule.  
**Assumptions:** No coordinates, no dimensions, no geometry, no physical constants.

---

## 1. Substrate: A Coordinate‑Free Graph

Law‑000 assumes the universe is represented by:

- **Nodes**  
  A set \(N\) of nodes (finite or countably infinite).

- **Edges**  
  A set of edges \(E \subseteq N \times N\).  
  Edges represent adjacency only — no distance, no orientation, no coordinates.  
  For simplicity, adjacency is symmetric:
  \[
  (n,m) \in E \Rightarrow (m,n) \in E.
  \]

- **Node State**  
  Each node has a binary state at tick \(t\):
  \[
  S_t : N \rightarrow \{0,1\}.
  \]

- **Tick**  
  A global discrete iteration index \(t \in \mathbb{Z}_{\ge 0}\).  
  Each tick applies Law‑000 to all nodes simultaneously.

The substrate contains **no**:

- spatial coordinates,
- metric or distance,
- physical parameters,
- objects or entities.

All geometry and physics must emerge from the rule’s iteration.

---

## 2. Local Quantities

For a node \(n \in N\):

- **Neighbors**
  \[
  \mathrm{Nbr}(n) = \{ m \in N \mid (n,m) \in E \}.
  \]

- **Active Neighbor Count**
  \[
  K_t(n) = \sum_{m \in \mathrm{Nbr}(n)} S_t(m).
  \]

- **Parity of Active Neighbors**
  \[
  P_t(n) = K_t(n) \bmod 2.
  \]
  Thus:
    - \(P_t(n) = 0\) if the number of active neighbors is even,
    - \(P_t(n) = 1\) if it is odd.

These quantities are strictly local and require no global information.

---

## 3. The Evolution Rule (Law‑000)

The state of node \(n\) at tick \(t+1\) is:

\[
S_{t+1}(n) = S_t(n) \oplus P_t(n)
\]

where \(\oplus\) is logical XOR.

### 3.1 Verbal Description

- Count active neighbors of node \(n\).
- Compute the parity (even/odd).
- If the parity is **even**, the node **keeps** its state.
- If the parity is **odd**, the node **flips** its state.

### 3.2 Properties

- **Binary:** Uses only \(\{0,1\}\).
- **Local:** Depends only on neighbors.
- **Deterministic:** Same input → same evolution.
- **Parameter‑free:** No thresholds, weights, or constants.
- **Minimal:** Uses only XOR and modulo‑2 arithmetic.
- **Iterative:** Universe = repeated application of one rule.

---

## 4. Global Evolution

Law‑000 is applied **synchronously** to all nodes:

\[
\forall n \in N:\quad
S_{t+1}(n) = S_t(n) \oplus \left( \sum_{m \in \mathrm{Nbr}(n)} S_t(m) \bmod 2 \right).
\]

This produces a global trajectory:

\[
S_0 \rightarrow S_1 \rightarrow S_2 \rightarrow \dots
\]

Law‑000 does **not** define how the graph \((N,E)\) changes over time.  
Graph growth or rewiring rules belong to separate laws.

---

## 5. Worked Examples

### 5.1 Example 1: 3‑Node Line

Graph: `0 — 1 — 2`

Initial state:
\[
S_0 = (0,1,0)
\]

Tick 1:
- Node 0: neighbors = {1}, active = 1 → parity = 1 → flip → 1
- Node 1: neighbors = {0,2}, active = 0 → parity = 0 → stays 1
- Node 2: neighbors = {1}, active = 1 → parity = 1 → flip → 1

\[
S_1 = (1,1,1)
\]

Tick 2:
- Node 0: active neighbors = 1 → flip → 0
- Node 1: active neighbors = 2 → stay → 1
- Node 2: active neighbors = 1 → flip → 0

\[
S_2 = (0,1,0)
\]

Period‑2 oscillation emerges.

---

### 5.2 Example 2: 4‑Node Cycle

Graph: `0 — 1 — 2 — 3 — 0`

Initial:
\[
S_0 = (1,0,0,0)
\]

Tick 1:
\[
S_1 = (1,1,0,1)
\]

Further ticks show oscillatory and propagating patterns.

---

## 6. Relation to Observer and Emergent Physics

Law‑000 defines only:

- the substrate (graph),
- the binary state,
- the local update rule.

It does **not** define:

- space,
- time as experienced,
- motion,
- entities,
- forces,
- geometry.

These emerge from:

- the structure of the graph,
- the iteration of Law‑000,
- the sampling limitations of the observer,
- the embedding chosen for visualization.

Thus:

- **Fractal:** the raw evolution of \(S_t\).
- **Reality:** the observer’s sampled interpretation of that evolution.

---

## 7. Summary

Law‑000 is the minimal evolution rule for a discrete universe:

\[
S_{t+1}(n) = S_t(n) \oplus \left( \sum_{m \in \mathrm{Nbr}(n)} S_t(m) \bmod 2 \right)
\]

It is:

- binary,
- local,
- deterministic,
- parameter‑free,
- coordinate‑free,
- and capable of producing rich emergent structure.

It serves as the foundational law for experiments in emergent geometry, entities, and physics.
