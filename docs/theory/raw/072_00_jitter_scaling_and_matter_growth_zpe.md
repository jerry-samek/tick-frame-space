# **Draft Concept for a Future Paper:

Jitter Scaling and Matter Growth in an Expanding CA Universe**

## **1. Motivation**

In the current V6 framework, jitter acts as a zero‑point‑like kinetic term that counterbalances gravitational collapse.
In the static regime, a single critical jitter value (≈ 0.119) produces long‑term macroscopic stability.

However, once the universe is allowed to expand, a constant jitter becomes physically inconsistent:

- as the lattice expands, the *same physical fluctuation* corresponds to a *smaller displacement in lattice units*,
- older matter appears “larger” in lattice coordinates than newly created matter,
- and the balance between jitter and gravity cannot remain stable unless the **amount of matter increases over time**.

This motivates a dynamic jitter model tied to expansion and matter creation.

---

## **2. Core Idea**

A stable expanding universe requires **two coupled processes**:

1. **Jitter scaling** — the effective jitter amplitude in lattice units must decrease as the universe grows.
2. **Matter growth** — the total amount of matter must increase to compensate for the energy injected by jitter.

These two processes must be linked; adjusting one without the other breaks stability.

---

## **3. Jitter Scaling Candidates**

Several families of scaling laws satisfy the requirement that jitter decreases with the size of the universe while
remaining locally meaningful:

### **3.1 Scale‑factor laws**

\[
J(a) = \frac{J_*}{a^k}
\]

- \(a\) is a global scale factor derived from the COM‑tracked radius or mean radius.
- \(k\) controls how fast jitter decays.
- Ensures that physical jitter remains constant while lattice jitter shrinks.

### **3.2 Age‑based local laws**

\[
J(\tau) = \frac{J_0}{(1 + \tau/\tau_0)^k}
\]

- \(\tau\) is the age of a pattern.
- New matter is “hotter”; old matter “cools”.
- Fully local, no global parameters required.

### **3.3 Density or gamma‑based laws**

\[
J = J_0 \cdot f(\rho, \gamma)
\]

- Jitter depends on local density or gravitational potential.
- Allows spatial variation in jitter without global coordination.

### **3.4 Hybrid laws**

\[
J_{\text{eff}} = \frac{J_*}{a^k} \cdot f(\tau, \rho, \gamma)
\]

- Most flexible and physically expressive.
- Global expansion + local corrections.

---

## **4. Matter Creation Requirement**

A key insight is that **jitter scaling alone is insufficient**.

To maintain long‑term stability:

- the universe must **gain matter over time**,
- at a minimum rate of **one new entity per tick**,
- or more generally:

\[
\Delta M \propto \eta \cdot J(t)
\]

This expresses the idea that jitter injects energy into the system, and the only way to prevent runaway expansion or
collapse is to convert part of that energy into new matter.

This leads to a self‑regulating loop:

\[
\text{ZPE (jitter)} \rightarrow \text{matter creation} \rightarrow \text{gravity} \rightarrow \text{expansion}
\rightarrow \text{jitter scaling}
\]

---

## **5. Future Work**

This concept is intentionally left open for later development.  
Once you introduce:

- expansion of the lattice,
- collisions,
- and dynamic gamma profiles,

you’ll be able to revisit this framework and determine:

- which scaling law is physically consistent,
- what matter‑creation rate yields stability,
- and whether a new critical jitter\*(t) emerges in the expanding regime.

At that point, this outline can be turned into a full formal principle.
