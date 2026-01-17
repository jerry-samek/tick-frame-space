# Length Definition in Tick‑Frame Space

---

## Abstract
This paper formalizes temporal invariance in tick‑frame substrates. Unlike classical spatial metrics, the tick‑frame engine defines “length” as a constant temporal horizon. The system maintains this horizon by continuously shifting the buffer: discarding the oldest tick and appending a new tick at the leading edge. This mechanism ensures reproducibility, causality, and invariance of observable dynamics.

---

## 1. Tick‑Frame Universe Model Background

### 1.1 State Space and Dynamics
- **Lattice field:**  
  

\[
  \psi: \mathbb{Z}^d \times \mathbb{Z}_{\ge 0} \to \mathbb{R}^m
  \]



- **Update operator:**  
  

\[
  \psi_{t+1} = F(\psi_t; \gamma, \alpha_0, \theta)
  \]



- **Locality:** Updates depend on a bounded neighborhood \( \mathcal{N}(x) \), enforcing finite propagation speed.

### 1.2 Parameters
- **Propagation speed (\(\gamma\)):** Maximum rate of influence per tick.  
- **Initial amplitude (\(\alpha_0\)):** Sets initial field scales.  
- **Configuration (\(\theta\)):** Encodes rule variants and thresholds.  
- **Seed:** Determines deterministic initialization and reproducibility.

### 1.3 Observers
- **Observer frame:** Perceives the system through a horizon‑limited slice \( \mathcal{H}(t) \).  
- **Narrative stream:** Observables are extracted from the horizon without perturbing dynamics.

---

## 2. Horizon Buffer Formalization

### 2.1 Definition


\[
\mathcal{H}(t) = \{ \psi(x, t-k) \mid k = 0, 1, \dots, H-1 \}
\]



- Constant buffer size \(H\).  
- Sliding window: drop oldest tick, append newest.  
- Temporal invariance: horizon properties remain constant under translation.

### 2.2 Causal Cone
- **Constraint:**  
  

\[
  \|y-x\| \le \gamma \cdot (t'-t)
  \]

  
- Only influences within the causal cone are valid; superluminal events are culled.

### 2.3 Stability of Observables
- **Persistence:**  
  

\[
  \text{age}(u) = \max \{ k \le H \mid u \text{ detected at } t-k \}
  \]

  
- Drift and variance computed over the horizon.

---

## 3. Measurement Without Absolute Length

### 3.1 Temporal Meter


\[
L_{\text{temporal}} := H \text{ ticks}
\]



### 3.2 Effective Wavelength


\[
\lambda_{\text{eff}}(u) = \frac{H}{n_{\text{cycles}}(u)}
\]



### 3.3 Drift Normalization


\[
\ell_{\text{eff}}(u) = \frac{\|\Delta x\|}{\gamma \cdot H}
\]



- No fixed meters; scale inferred from propagation rhythms.

---

## 4. Invariants and Scaling

### 4.1 Horizon Invariants


\[
\sum_{x} E(\psi_t(x)) \approx \text{const} \quad \text{for } t \in [t-H+1, t]
\]



### 4.2 Scaling Behavior
- Larger \(H\): finer temporal resolution, higher compute cost.  
- Larger \(\gamma\): expands causal cone, alters effective wavelengths.

### 4.3 Ergodicity
- Trade‑off between mixing and persistence defines emergent structures.  
- Falsifiability: parameter changes yield measurable shifts.

---

## 5. Cosmological Comparison

### 5.1 Observations
- Accelerating expansion attributed to dark energy.  
- Hubble tension between early and late universe measurements.  
- DESI hints at evolving dark energy → possible slowing.  
- Observable universe bounded by cosmic horizon.

### 5.2 Comparative Framework

| **Concept**                  | **Cosmology**                                                                 | **Tick‑Frame Model**                                                                 |
|-------------------------------|-------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| **Expansion driver**          | Dark energy / cosmological constant                                           | Horizon buffer invariance; expansion emerges from sliding tick window                 |
| **Scale definition**          | Distances via redshift                                                        | “Length” = number of ticks in horizon buffer                                          |
| **Causal horizon**            | Observable universe limited by speed of light                                 | Causal cone enforced by γ; superluminal events culled                                 |
| **Expansion rate**            | Hubble constant (H₀)                                                          | Effective scaling rate defined by γ and buffer size H                                 |
| **Acceleration vs. slowing**  | Debate: accelerating vs. slowing expansion                                    | Changing H mimics acceleration/deceleration                                           |
| **Measurement protocol**      | Redshift surveys, CMB, supernovae                                             | Tick counts, cycles, drift variance; deterministic logs                               |
| **Falsifiability**            | Competing models tested against observational data                            | Parameters (γ, H, θ) versioned; replay with seeds ensures falsifiability              |

---

## 6. Conceptual Bridge
- Cosmology: expansion observed as galaxies receding faster over time.  
- Tick‑frame: expansion encoded in sliding buffer; observables scale with time.  
- Shared challenge: both replace fixed rulers with dynamic horizons.

---

## 7. Implications
- Tick‑frame model provides computational analogue to cosmological expansion.  
- Tuning \(H\) and \(\gamma\) simulates accelerating, constant, or slowing expansion.  
- Framework is falsifiable and auditable, bridging computation and cosmology.

---
