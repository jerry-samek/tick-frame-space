# V2 experimental theory — entity as regulated gamma well

## 1. Goals of V2

- **Make the entity explicit**: no longer “just a moving dot”, but a process with:
    - internal energy budget
    - gamma well
    - lag
    - emission
- **Test regulation**: entity should:
    - absorb potential difference
    - convert it to motion
    - shed excess as fragments
    - stay stable over long runs
- **Preserve gamma field**: fragments must dissipate mostly into residual, not distort the global metric.

---

## 2. Core objects

- **Gamma field**
    - Smooth background metric.
    - Expanded each tick by `Δs`.
    - Not directly “kicked” by entities—only slowly shaped by long‑term wells.

- **Entity**
    - Position: `pos(t)`
    - Angle / phase: `θ(t)`
    - Gamma well state: `well(t)`
    - Internal energy: `E(t)`
    - Lag: `L(t)` (effective delay between state and imprint)

- **Residual / fragments**
    - Fast, small‑scale excitations.
    - Carry away excess energy.
    - Do not form stable wells on their own.

---

## 3. Tick flow (per entity)

Each tick:

1. **Field expansion**
    - `scale(t+1) = scale(t) + Δs`
    - This creates a potential difference between old and new space.

2. **Energy intake from potential difference**
    - Compute effective energy gain:
      \[
      \Delta E_{\text{in}} = f(\text{lag}, \Delta s, \text{well geometry})
      \]
    - Update:
      \[
      E(t) \leftarrow E(t) + \Delta E_{\text{in}}
      \]

3. **Energy budget split**
    - Choose fractions or rules:
        - `E_bind` — maintain well
        - `E_move` — radial / angular motion
        - `E_excess` — anything above safe capacity
    - Conceptually:
      \[
      E_{\text{bind}} + E_{\text{move}} \le E_{\text{safe}}(t)
      \]
      \[
      E_{\text{excess}} = \max(0, E(t) - E_{\text{safe}}(t))
      \]

4. **Well maintenance**
    - Use `E_bind` to:
        - keep well depth/shape near target
        - prevent collapse or uncontrolled growth
    - If `E_bind` < required:
        - well shallows
        - entity becomes less stable

5. **Motion**
    - Use `E_move` to update:
        - radial position (spiral / orbit)
        - angle `θ(t)`
    - Motion is constrained:
      \[
      \|\Delta pos\| \le v_{\max}(E_{\text{move}})
      \]
      \[
      |\Delta \theta| \le \omega_{\max}(E_{\text{move}})
      \]

6. **Lag regulation**
    - If `E_excess` is high:
        - **reduce lag** `L(t)` slightly
        - entity “snaps” closer to its own imprint
    - If `E` is low:
        - lag may slowly increase again
    - Lag is both:
        - source of energy (bigger separation → bigger ΔE)
        - and safety valve (too much → collapse + emission)

7. **Fragment emission**
    - Convert `E_excess` into fragments:
        - spawned at/near entity’s position
        - propagate at max shell speed
        - minimal interaction with gamma field, mostly with residual
    - Fragments are:
        - short‑lived
        - non‑binding
        - visually: fast outward ripples / specks

8. **Residual / field update**
    - Residual absorbs fragments, diffuses them.
    - Gamma field remains mostly unchanged at large scale.

---

## 4. Experimental knobs for V2

You don’t need perfect laws yet—just tunable parameters:

- **Δs** — expansion per tick
- **E_safe(t)** — how much energy the entity can hold before shedding
- **Lag dynamics**:
    - `L(t+1) = L(t) + g(E(t), E_safe(t))`
- **Fragment strength**:
    - how much visual / residual impact per unit `E_excess`
- **Well stiffness**:
    - how quickly well reacts to under/over‑binding

---

## 5. What to look for in experiments

You’ll know V2 is “right” if you see:

- entity **stays coherent** over long runs
- spiral / orbit remains smooth even with bursts of emission
- when energy spikes:
    - lag briefly drops
    - fragments shoot out
    - entity returns to a stable regime
- gamma field pattern remains globally calm—no runaway distortions
- residual shows a subtle “history” of past emissions, but doesn’t dominate

---

## 6. Minimal success criteria

V2 is a success if:

- the entity **does not**:
    - explode numerically
    - freeze
    - drift off uncontrollably
- and **does**:
    - self‑regulate via emission
    - maintain a recognizable well
    - show consistent behavior across large scales
