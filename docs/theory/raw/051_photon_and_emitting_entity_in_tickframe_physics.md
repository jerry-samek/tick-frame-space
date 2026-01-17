# Photon and Emitting Entity in Tick‑Frame Physics

*Specification v1.0*

---

## 1. Overview

In the tick‑frame universe, a photon is not a classical particle nor an object with internal state.  
It is a **periodic imprint in the tick‑stream**, renewed every global tick and shifted by exactly one horizon‑unit per
tick.  
An emitting entity, by contrast, is a **computational object with internal tick‑capacity** capable of creating such an
imprint.

This document defines:

- the structure of a photon,
- its dynamics,
- the mechanism of emission,
- the properties of an emitting entity.

---

## 2. Photon Definition

### 2.1 Photon as an Imprint

A photon is defined by:

- **pattern**: a finite sequence of states (bit, phase, or complex),
- **period**: number of ticks before the pattern repeats,
- **phase**: current index within the pattern,
- **propagation direction**: a unit vector in space,
- **speed**: always 1 horizon‑unit per tick (constant).

A photon **does not have**:

- internal tick‑capacity,
- internal state,
- mass,
- the ability to modify itself.

A photon is purely a **temporal texture** propagating through space.

---

## 2.2 Formal Structure

Photon { Pattern: [s₀, s₁, ..., sₙ₋₁] Period: n // number of ticks Phase: φ ∈ [0, n) Direction: v̂ // unit vector }


---

## 2.3 Photon Dynamics

On every global tick:

1. **Propagation**  
   The photon shifts by 1 horizon‑unit along `v̂`.

2. **Pattern Renewal**  
   Phase increments:  
   `φ = (φ + 1) mod n`

3. **No Internal Evolution**  
   The pattern never changes; the photon has no internal computation.

---

## 2.4 Wavelength and Frequency

- **Wavelength λ** = pattern period = `n` ticks.
- **Frequency ν** = `1 / n`.

Since the photon moves 1 spatial unit per tick:

- temporal periodicity = spatial periodicity.

---

## 2.5 Photon Termination

A photon ceases to exist when:

- the emitting entity stops renewing the imprint,
- an absorbing entity captures the pattern,
- destructive interference eliminates the pattern (if the model supports it).

---

## 3. Emitting Entity

### 3.1 Definition

An emitting entity is an object with:

- **internal tick‑capacity**,
- **internal state**,
- **a horizon buffer**,
- the ability to **create an imprint** in the tick‑stream.

It is effectively a processor capable of generating photons.

---

## 3.2 Structure of an Emitting Entity

EmittingEntity { InternalState: S TickCapacity: T_local HorizonBuffer: H }


---

## 3.3 Emission Mechanism

Emission occurs when:

1. The entity undergoes an internal state transition  
   (e.g., an electron collapses to a lower configuration).

2. This produces **excess tick‑energy** that cannot be retained internally.

3. The excess is written into the tick‑stream as a **new photon imprint**:

EmitPhoton(pattern, period, direction)

4. From that moment on, the photon renews autonomously.

---

## 3.4 What Determines the Photon’s Wavelength

The photon’s period is determined by:

- the number of ticks required for the entity to return to a stable state,
- i.e., the computational “depth” of the internal collapse.

Formally:

λ = Δt_recovery


---

## 3.5 Absorption

An absorbing entity:

- captures the pattern,
- stops its renewal,
- uses the tick‑energy to modify its internal state.

---

## 4. Photon–Material Interaction

### 4.1 Apparent Slowing in Matter

The photon **never slows down**.  
Instead, the material:

- captures the pattern,
- delays it,
- re‑emits it,
- possibly with a modified period.

This produces the effective refractive index.

---

## 5. Summary

- A photon is a **periodic imprint**, not an object.
- It has no internal tick‑capacity → it cannot change itself.
- An emitting entity is a **processor** that creates the imprint.
- Wavelength = pattern period.
- Changing wavelength = creating a new imprint.
- Materials modify photons only via absorption and re‑emission.

---
