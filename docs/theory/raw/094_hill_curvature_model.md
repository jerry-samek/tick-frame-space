### 1. Core idea: curvature‑only, overdamped hill

We strip the model down so that:

- **No absolute gamma strength** enters the dynamics.
- Only **normalized curvature** (shape) and **sign of slope** matter.
- Motion is **overdamped** to kill jitter.

**Field:**

- Hill \(H(x)\) is always **renormalized** each tick:
  \[
  H'(x) = \frac{H(x) - \min H}{\max H - \min H + \epsilon}
  \]
- Dynamics use only:
  \[
  s(x) = \frac{\partial H'}{\partial x}
  \]
  not the absolute value of \(H\).

**Process dynamics (overdamped):**

- No inertia, no oscillation:
  \[
  x_p \leftarrow x_p - k \cdot s(x_p)
  \]
- That’s it. No velocity state, no mass, no gamma strength.

This alone removes:

- dependence on field strength,
- most sources of numerical jitter (no v‑overshoot).

---

### 2. Hill update without strength

Imprint raises the hill **shape**, not its absolute amplitude:

- Use a **fixed‑area kernel**:
  \[
  H(x) \leftarrow H(x) + \alpha \cdot K(x - x_p)
  \]
- Then **renormalize** \(H\) again (as above), so:
    - only *relative* bumps and valleys remain,
    - no runaway growth in amplitude.

So:

- Gamma field strength never appears as a free parameter.
- Only **where** the hill is higher/steeper matters.

---

### 3. Why this should kill jitter

Jitter in your older runs likely came from:

- inertia + discrete steps → overshoot around minima,
- competing scales (big gamma vs small corrections),
- mixed “well” and “hill” behavior.

Here:

- **Overdamped step** → no oscillation around equilibrium.
- **Renormalization** → no huge gradients from field strength.
- **Curvature‑only** → dynamics depend only on shape, not magnitude.

If the model still jitters under these conditions, the cause is structural (e.g. conflicting curvatures), not numerical
or gamma‑strength‑related.

---

### 4. Minimal test

1. 1D hill, flat start.
2. One process, overdamped update using only normalized slope.
3. Imprint raises hill via kernel, then renormalize.
4. Watch:
    - Does the process settle into a stable position / orbit?
    - Does the hill stabilize around it without micro‑tremor?
