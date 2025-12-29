# 22‑X Substrate Update Rule
### *Canonical definition of the tick‑frame universe transition function*

This chapter defines the update rule \(U\) used by the substrate engine.  
It is the only mechanism by which the universe evolves:

\[
A(t+1) = U(A(t))
\]

The rule is **local**, **memoryless**, **synchronous**, and **geometry‑free**.  
It operates purely on adjacency.

---

# 1. Requirements for the Update Rule

The update rule must satisfy:

- **Locality:** depends only on adjacency neighborhoods
- **Memorylessness:** no history is stored
- **Statelessness:** no global variables
- **Synchronous updates:** applied everywhere each tick
- **Geometry‑free:** no coordinates, distances, or forces
- **Adjacency‑only:** modifies edges and local patterns

The substrate does not contain geometry, fields, forces, particles, or constants.  
These emerge only in the observer layer.

---

# 2. Canonical Form of the Update Rule

The substrate update rule consists of three components:

\[
A(t+1) =
\underbrace{\text{Expand}(A(t))}_{\text{growth}}
\;\cup\;
\underbrace{\text{Mutate}(A(t))}_{\text{decay/rewire}}
\;\cup\;
\underbrace{\text{Bias}(A(t))}_{\text{interaction}}
\]

Where:

- **Expand** adds new adjacency edges
- **Mutate** removes or rewires edges
- **Bias** applies local pattern‑dependent adjustments

All three operate locally and independently for each node or edge.

---

# 3. Expand Component
### *Adjacency growth / causal spread*

Each node expands adjacency into its local neighborhood:

\[
\text{Expand}(i) = \{(i,k) \mid k \in \text{LocalNeighborhood}(i)\}
\]

This produces:

- horizon growth
- adjacency shells
- π drift
- entropy increase
- early‑tick Genesis behavior

Expand is the substrate analogue of “propagation.”

---

# 4. Mutate Component
### *Decay and rewiring*

Each adjacency edge may:

- **decay** with probability \(p_d\)
- **rewire** to a nearby node with probability \(p_r\)
- **remain unchanged** otherwise

Formally:

\[
(i,j) \rightarrow
\begin{cases}
\text{removed} & p_d \\
(i,k) & p_r \\
(i,j) & \text{otherwise}
\end{cases}
\]

Mutation produces:

- clustering
- adjacency loops (particle‑like structures)
- drift of constants
- structural diversity

---

# 5. Bias Component
### *Local pattern‑dependent adjustments*

Bias applies deterministic or probabilistic adjustments based on local adjacency motifs:

\[
\text{Bias}(i,j) = f(\text{local adjacency pattern})
\]

This is the substrate origin of all “interactions”:

- gravity → adjacency deviation
- electromagnetism → adjacency rotation
- strong force → adjacency locking
- weak force → adjacency reconfiguration

The substrate does not know these names; it only applies the bias function.

---

# 6. Final Canonical Update Rule

\[
\boxed{
A(t+1) =
\text{Expand}(A(t))
\;\cup\;
\text{Mutate}(A(t))
\;\cup\;
\text{Bias}(A(t))
}
\]

This is the complete substrate transition function.  
Everything else — geometry, forces, particles, constants, spacetime — is reconstructed by observers.

---

# 7. Implementation Notes

- Expand, Mutate, and Bias are **local** and **independent**.
- The engine applies them synchronously each tick.
- Observers interpret the resulting adjacency patterns.
- No component references geometry or stored state.

This rule is ready for direct implementation in the substrate engine.
