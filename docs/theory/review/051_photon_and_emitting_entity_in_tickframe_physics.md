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

## 6. Photon-Gamma Coupling

### 6.1 Light as Gamma Oscillation

Per Doc 065 (Electromagnetism in Tick-Frame), electromagnetic waves are:

> **Traveling oscillations of gamma gradients and anisotropies.**

A photon's periodic imprint manifests as oscillation in the gamma field:
- The pattern [s₀, s₁, ..., sₙ₋₁] modulates local gamma
- Oscillation amplitude: proportional to photon energy
- Oscillation frequency: ν = 1/n (pattern period)

This means the photon **does modify the gamma field** along its path, reconciling:
- Doc 051: Photon as periodic imprint (this document)
- Doc 065: Light IS gamma oscillation
- Exp 56 v17: All entity actions = gamma modifications (canvas ontology)

---

### 6.2 Gamma Trace

As a photon propagates through space:

1. **Trace Creation**: It leaves a transient gamma oscillation along its path
2. **Trace Amplitude**: Proportional to photon energy (E = hν in continuous limit)
3. **Trace Decay**: The trace decays over characteristic time τ_decay
4. **Path Encoding**: The trace IS the "imprint in the tick-stream"

```
Photon at position x, tick t:
  γ(x, t) = γ_background + A_photon × sin(ωt + φ)

where:
  A_photon = k_coupling × E_photon
  ω = 2π/n (angular frequency from pattern period)
  φ = phase index within pattern
```

After the photon passes, the gamma perturbation decays:

```
γ(x, t + Δt) = γ_background + (γ(x, t) - γ_background) × exp(-Δt/τ_decay)
```

---

### 6.3 Implications for Measurement

Since gamma traces exist:

1. **Which-path information IS encoded** in the gamma field
2. **Detecting gamma traces = detecting which-path**
3. **This modifies the "which-path without collapse" claim** (see Doc 062)

The key question becomes: **Does reading the gamma trace disturb the interference?**

In standard QM: ANY which-path measurement destroys interference (complementarity)

In tick-frame physics with gamma coupling:
- **Weak detection**: Sampling gamma trace with energy E_probe ≪ E_photon → minimal disturbance
- **Strong detection**: E_probe ~ E_photon → significant phase perturbation
- **Threshold behavior**: Interference degradation depends on detection strength

This produces a **different falsifiable prediction** than the original claim:

> **Original claim (superseded)**: Which-path without collapse (interference unaffected)
>
> **Revised claim**: Interference degradation depends on gamma trace detection strength

---

### 6.4 Phase Evolution in Gamma Field

Photon phase evolves based on local gamma:

```
dφ/dt = ω × γ(x, t)
```

In regions of higher gamma (faster time flow):
- Phase accumulates faster
- Effective frequency is higher
- This produces gravitational frequency shift (Shapiro delay)

In regions of lower gamma (slower time flow):
- Phase accumulates slower
- This produces effective wavelength stretching

---

### 6.5 Two-Photon Gamma Interaction

When two photons have overlapping paths:
- Their gamma traces superpose
- Each photon's phase evolves in the combined gamma field
- This produces subtle interference effects beyond simple superposition

```
γ_total(x, t) = γ_background + Δγ_photon_A(x, t) + Δγ_photon_B(x, t)
```

This may explain:
- Photon-photon scattering (normally forbidden in classical EM)
- Vacuum birefringence effects
- Nonlinear optical phenomena

---

### 6.6 Reconciliation with Canvas Ontology

From Exp 56 v17, the canvas (gamma field) IS the complete tick state:
- Entities "paint" on the canvas by modifying gamma
- The canvas persists between ticks
- Unpainted regions have no influence on behavior

Applying this to photons:
- Photons paint transient oscillations on the canvas
- These oscillations decay but DO exist
- The canvas records the photon's passage temporarily
- Reading the canvas = obtaining which-path information

This resolves the theoretical contradiction identified in the analysis:
- If light IS gamma oscillation → photons modify gamma ✓
- If the canvas IS gamma → photon imprints exist in gamma ✓
- If imprints exist → which-path info exists in gamma field ✓

---
