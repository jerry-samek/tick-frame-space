# **Black Hole Behavior in the Tick‑Frame Universe**

### *A Strong‑Field Analysis of Emergent Time‑Gradient Gravity*

**Author:** Tom  
**Date:** January 2026

---

## **Abstract**

This paper investigates the strong‑field behavior of the tick‑frame universe, a discrete computational ontology in which
gravity emerges from gradients in local time‑flow (γ) rather than from spacetime curvature. Previous work demonstrated
that geodesics and orbital mechanics arise naturally from entities following ∇γ, with no force laws or geometric
assumptions. Here we extend the analysis to extreme mass configurations to test whether the tick‑frame model reproduces
general relativity’s predictions for black holes, including event horizons, singularities, and the absence of stable
orbits inside the Schwarzschild radius.

Across three iterations—10×, 10× (uncapped), and 100× mass—we find that the tick‑frame universe **does not produce
GR‑style black holes**. Instead, it exhibits a distinct strong‑field regime characterized by:

- finite load saturation
- finite γ everywhere except a localized divergent core
- a **stable c‑speed orbital ring** at the edge of the core
- **stable orbits at all radii**
- no collapse to r = 0
- no event horizon
- no singularity

These results constitute a **distinctive, falsifiable prediction** of the tick‑frame ontology. While the model
reproduces GR in weak fields, it diverges sharply in the strong‑field limit. This paper summarizes the mechanism,
results, and implications for future observational tests.

---

## **1. Introduction**

The tick‑frame universe is a discrete, deterministic computational model in which:

- time is primary
- space is emergent
- entities receive and spend ticks
- load and regeneration fields determine local time dilation
- gravity emerges from gradients in γ
- motion follows the rule:  
  \[
  \mathbf{a} = k \nabla \gamma_{\text{grav}}, \quad |\mathbf{v}| \le c
  \]

Previous experiments (v9–v10) demonstrated:

- emergent time dilation consistent with special relativity
- emergent gravitational time dilation
- emergent geodesics
- stable circular and elliptical orbits
- 100% orbital success rate without force laws

The natural next question is whether **black holes**—as predicted by general relativity—also emerge.

General relativity predicts:

- a Schwarzschild radius \( r_s = 2GM/c^2 \)
- a sharp event horizon at \( r_s \)
- γ → ∞ at the horizon
- no stable orbits inside \( 3r_s \)
- no photon orbits except an unstable one at \( 1.5r_s \)
- inevitable collapse to a singularity

This paper tests whether the tick‑frame universe reproduces these features.

---

## **2. Methods**

We simulate a central “planet” composed of many stationary entities, which generate a load field L(x,y) and
corresponding γ(x,y). Mobile test entities follow the gradient‑following rule:

\[
\mathbf{v}_{t+1} = \text{clamp}_c\left(\mathbf{v}_t + k \nabla \gamma \, dt\right),
\quad
\mathbf{x}_{t+1} = \mathbf{x}_t + \mathbf{v}_{t+1} dt
\]

Three iterations were performed:

### **Iteration 1 — 10× mass, γ capped at 10**

- Planet: 7,000 entities
- γ capped at 10
- 36 test entities

### **Iteration 2 — 10× mass, γ uncapped**

- Same mass
- γ allowed to reach ~1,000,000
- capacity_min = 1e‑6

### **Iteration 3 — 100× mass, γ uncapped**

- Planet: 70,000 entities
- scale = 75.0
- γ diverges inside r ≈ 10

All simulations ran for 5000 ticks.

---

## **3. Results**

### **3.1 No Event Horizon Forms**

Across all iterations:

- No entity ever crossed a radius beyond which escape was impossible
- No entity collapsed to r = 0
- No sharp boundary in γ or ∇γ was observed
- γ remained finite everywhere except a localized divergent core

### **3.2 Stable Orbits at All Radii**

Even in extreme fields:

- Entities formed stable orbits at radii as small as r = 1.2 (iteration 2)
- In iteration 3, entities formed a **stable c‑speed ring** at r ≈ 10.1
- No unstable photon sphere was observed
- No region existed where all trajectories collapsed inward

### **3.3 Divergent Core Without Collapse**

In iteration 3:

- γ reached 1,000,000 at r = 10
- Entities never entered this region
- Entities instead stabilized at r ≈ 10.1 with v = c

### **3.4 Speed Limit Prevents Runaway Infall**

Because |v| ≤ c:

- Entities cannot accelerate arbitrarily fast
- Even extreme ∇γ cannot produce super‑c infall
- Instead, entities “surf” the gradient until tangential velocity balances inward pull

This produces the **stable last orbit**.

---

## **4. Comparison with General Relativity**

| Feature           | GR Prediction         | Tick‑Frame Result            |
|-------------------|-----------------------|------------------------------|
| Event horizon     | Sharp boundary at r_s | ❌ None                       |
| γ at horizon      | → ∞                   | Finite except core           |
| Photon sphere     | Unstable at 1.5 r_s   | **Stable c‑ring at r≈10.1**  |
| Orbits inside r_s | Impossible            | **Stable orbits everywhere** |
| Collapse          | Mandatory             | ❌ None                       |
| Singularity       | Yes                   | ❌ None                       |

The tick‑frame universe **matches GR in weak fields** but **diverges in strong fields**.

---

## **4.5 Srovnání teorií silného gravitačního pole**

| Teorie                                      | Event horizon               | Singularita             | Stabilní orbity uvnitř      | Photon sphere               | Pozorovací stav           | Distinktivní predikce                                     |
|---------------------------------------------|-----------------------------|-------------------------|-----------------------------|-----------------------------|---------------------------|-----------------------------------------------------------|
| **General Relativity (Schwarzschild/Kerr)** | Ano (ostrý)                 | Ano                     | Ne (uvnitř r_s)             | Ano, **nestabilní**         | Silná podpora (EHT, LIGO) | Ostrý stín, kolaps do singularity                         |
| **Gravastar / BH mimickers**                | Ne (povrch místo horizontu) | Ne                      | Možné (model‑dependent)     | Nejasné                     | Teoretické návrhy         | Hladký vnitřek, žádný horizont                            |
| **Loop Quantum Gravity / Planck star**      | Ne (kvantové korekce)       | Ne                      | Možné (remnant)             | Modifikovaná                | Teoretické                | Kvantový „odraz", Planck‑remnant                          |
| **Emergent gravity (Verlinde)**             | Model‑dependent             | Ne v některých řešeních | Záleží na řešení            | Záleží                      | Konceptuální              | Gravitace jako emergentní jev, modifikované stíny         |
| **Tick‑frame (naše)**                       | **Ne**                      | **Ne**                  | **Ano (všechny r > jádro)** | **Ano, stabilní c‑kroužek** | Simulační důkazy          | **Žádný horizont, žádná singularita, stabilní c‑kroužek** |

*Poznámka: Tick‑frame výsledky vyžadují validaci s kolizní fyzikou (viz Sekce 6.5)*

---

## **5. Interpretation**

### **5.1 Why No Horizon Forms**

1. **Finite load saturation**  
   Reaction–diffusion dynamics reach equilibrium  
   Load never becomes infinite  
   γ remains finite except at the core

2. **Gradient-following rule**  
   Entities accelerate toward higher γ  
   ∇γ remains finite → acceleration remains finite

3. **Speed limit**  
   |v| ≤ c prevents runaway collapse  
   Entities cannot “fall faster” than c

4. **Dynamic equilibrium**  
   Entities settle into stable orbits where:  
   \[
   \text{inward pull from ∇γ} \approx \text{tangential motion}
   \]

### **5.2 What Tick‑Frame Black Holes Actually Are**

They are not GR black holes.

They are:

- regions of **extreme time dilation**
- surrounded by a **stable c‑speed ring**
- with **no collapse**
- **no horizon**
- **no singularity**
- **no causal disconnection** except dynamically

This is a **distinctive ontology**.

---

## **6. Predictions and Falsification**

The tick‑frame model predicts:

1. **No event horizons exist in nature**
2. **No singularities exist**
3. **Stable orbits exist arbitrarily close to the core**
4. **A stable last orbit exists at the speed of light**
5. **Time dilation is extreme but finite outside the core**

These predictions are **falsifiable**:

- If astrophysical black holes show sharp horizons → tick‑frame falsified
- If no stable orbits exist inside r_s → tick‑frame falsified
- If γ diverges at a finite radius → tick‑frame falsified
- If stable ultra‑close orbits are observed → tick‑frame supported

---

## **6.5 Critical Limitation: Collision-Less Physics**

⚠️ **IMPORTANT CAVEAT**: The results presented in this paper are based on a **ghost particle approximation**.

### Current Model Assumptions

The v10–v11 experiments use the following simplifications:

1. **No collision detection**: Entities do not collide with each other
2. **Unlimited overlap**: Multiple entities can occupy the same grid cell without interaction
3. **Additive field contributions**: S[ix, iy] += contribution (no hard-body physics)
4. **No momentum exchange**: Entities pass through each other without scattering
5. **No Pauli exclusion**: Unlimited density allowed (no degeneracy pressure)

### Implications for the c-Speed Ring

The **stable c-speed ring at r ≈ 10.1** observed in iteration 3 may be a **modeling artifact**.

With realistic collision physics, the ring would likely exhibit:

1. **Scattering** (hard-sphere collisions)
   → Ring disperses into wide annulus

2. **Repulsion** (Pauli-like exclusion)
   → Ring spreads into thick structure

3. **Merging** (coalescence)
   → Fewer, more massive entities

4. **Energy dissipation** (inelastic collisions)
   → Ring decay inward over time

### Scientific Status

- ✅ **Mathematical result**: c-ring emerges robustly in collision-less model
- ❌ **Physical prediction**: **Requires validation** with collision physics
- ⏳ **Future work**: Experiments v11b-v11d will test with realistic interactions

### Validation Plan

**Planned experiments**:

- **v11b**: Hard-sphere collision detection + elastic scattering
- **v11c**: Soft repulsion force (Pauli-like exclusion)
- **v11d**: Inelastic collisions (energy dissipation)

**Key question**: Does the c-speed ring survive with realistic collision physics?

- If **YES** → Validated distinctive prediction (testable, falsifiable)
- If **NO** → Artifact of ghost particle approximation

**Recommendation**: Treat c-ring as **suggestive result requiring validation**, not definitive prediction until
collision physics is tested.

---

## **7. Conclusion**

The tick‑frame universe successfully reproduces:

- gravitational time dilation
- geodesics
- orbital mechanics
- weak‑field GR behavior

However, in the strong‑field regime, it diverges sharply from general relativity:

- no event horizons
- no singularities
- stable orbits at all radii
- a stable c‑speed ring instead of a photon sphere

This constitutes a **distinctive, testable alternative** to GR’s black hole predictions.  
Future work will explore observer‑dependent horizons, length contraction, and the behavior of multi‑body strong‑field
systems.
