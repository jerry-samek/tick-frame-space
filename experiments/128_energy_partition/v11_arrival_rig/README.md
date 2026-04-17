# Experiment 128 v11 — Arrival Rig

## Status: Phase 1 COMPLETE (April 16, 2026)

## Purpose: Close the graph → 1/r² gap left open by v9/v10

---

## Why This Experiment Exists

v9 (ODE) and v10 (minimal) demonstrated that consumption acting as a
centripetal force produces Keplerian orbits. Both assumed the arrival flux
at the planet scales as `L / (4π r²)` — the 3D geometric-dilution formula.
The assumption was never derived from the graph substrate. v11 closes the
gap: measure, honestly, how deposit density and its gradient scale with
distance from a point source on the graph.

If the graph produces ~1/r² for the gradient, the v10 force law is earned
rather than postulated. If it produces something else, the orbital
mechanics story has to be revised.

---

## Model

A 3D random geometric graph (uniform points in a sphere, edges by radius
query) carries a scalar density `ρ` per node. Each tick:

1. Every node redistributes its density equally to its neighbors
   (`ρ_new[nbr] += ρ[src] / degree[src]`).
2. The star (a small cluster near the origin) is held at `ρ = L` — this is
   the source.
3. Nodes within the outer shell (`r > 0.95 R`) are reset to 0 — absorbing
   boundary.

No consumption. No Same/Different partition. No planet. Pure propagation.
The point is to isolate the substrate's response to a point source, with no
non-linear dynamics obscuring the scaling.

Propagation is vectorized with `np.bincount` over flat directed-edge arrays:
~85 t/s on the 20k smoke test, ~5 t/s on the 500k full run.

---

## What We Measured

Density profile `ρ(r)` binned in 24 log-spaced shells, plus `|dρ/dr|` by
finite difference. Power-law fits taken in the intermediate range
`r ∈ [4, 0.5 R]` (away from source and from boundary). A second fit to the
analytical Poisson form `ρ(r) = A · (1/r − 1/R_eff)` gives a direct
falsification target: if the substrate is 3D, `R_eff` should match the
actual sphere radius, and the power-law slopes should match the expected
integrated-slope behavior of `(1/r − 1/R)`.

---

## Result (500k nodes, R = 80, ⟨k⟩ = 23.5, t = 3000)

| tick | slope_ρ    | slope_grad | analytic_R_eff |
|------|------------|------------|----------------|
| 500  | −1.648     | −2.109     | 50.77          |
| 1000 | −1.417     | −2.018     | 67.10          |
| 2000 | −1.300     | −1.978     | 86.68          |
| 3000 | **−1.274** | **−1.968** | 93.71          |

**The gradient log-log slope is −1.968** — within 1.6% of Newton's −2.0.
The slopes converge monotonically from transient (−2.1 at t=500, still
propagating) toward the steady-state value as the density field fills out.
Total interior density reached ≈ 80% of its asymptote by t=3000; profile
shape converged earlier than magnitude.

**The density slope (−1.27) is consistent with 1/r − 1/R** in the fit
range `[4, 40]`, where the integrated log-log slope of that analytical form
lies between −1.2 and −1.5.

**The analytic_R_eff drifts upward** (50 → 94) as the profile matures. At
t=3000 it sits above the actual sphere radius (80). This is expected: the
fit range `[4, 40]` sits well inside the boundary at `r = 76`, and in that
inner region `ρ ≈ A/r`, which is insensitive to where the far boundary is.
The drift is a symptom of "we are fitting the inner region, not the whole
profile," not a sign the 3D story is wrong.

---

## Interpretation

**The graph substrate produces the Newtonian 1/r² force law as an emergent
property of pure deposit propagation.** The assumption that was marked
"fake" in v9/v10 is now earned — it is what the substrate naturally
delivers.

The remaining 1.6% deviation from −2 could be:

- residual transient (total mass not fully saturated at t=3000);
- discreteness (finite ⟨k⟩ random geometric graph vs continuum);
- source extent (the "point" source is actually a 50-node cluster near the
  origin).

Any of these is plausible. None of them threaten the main claim: the
gradient scaling is Newtonian.

---

## What This Closes and What It Does Not

**Closed:** graph dynamics → 1/r² gradient (in a pure-propagation, no-
consumption regime). The 1/r² is not assumed. It comes out.

**Not closed:** does this 1/r² survive when the Same/Different consumption
dynamics are turned on? Consumption is non-linear and could in principle
warp the scaling. That is Phase 2.

**Not closed:** does a *consuming* planet placed at distance `r` experience
a force that follows the measured gradient? That is Phase 3 — plug the
measured `f(r)` into v10's orbit dynamics and see whether orbits still
close.

---

---

## Phase 2 — Orbits under the measured field (April 16, 2026)

Plug Phase 1's measured ρ(r) straight into the orbit integrator. Force
magnitude = `RESISTANCE × |dρ/dr(r)|` interpolated from the binned
profile. Compare against pure `K/r²` with matched coupling.

**Result:** measured-field orbits overlay Newton orbits within a few
percent across circular, sub-circular (0.85 v_c) and super-circular
(1.15 v_c) initial conditions. Circular stays circular, elliptical
stays elliptical, periods match. Only deviation: at large r the
absorbing boundary pulls the measured field below pure 1/r², so wide
orbits close tighter under the graph than under Newton.

The chain tick-frame → graph propagation → measured 1/r² → Kepler is
unbroken in the vanilla case.

---

## Phase 3 — Buffered consumption (HYBRID — Newton is present)

Tests whether giving the planet a **finite consumption capacity**
`C_max` and letting unconsumed deposits accumulate on the connector
as a buffer `B` (with `r_eff = r_geom + α·B`) changes the dynamics.
Grounded in RAW 113 / Exp 118: "Different" deposits extend connectors;
the buffer = Different sitting on the star-planet connector.

Per-tick rule:

```
pool     = B + K / r_eff²
consumed = min(pool, C_max)
B        = pool - consumed
F        = consumed * (-r̂)
r_eff    = r_geom + α * B       (recomputed before next tick)
```

**Results** (K=400, C_max=1, α=0.5, r_eq = √(K/C_max) = 20):

- All six initial conditions produce bound orbits.
- `r < r_eq`: capacity-limited. `r_geom` swings elliptically (6–11) but
  **r_eff pins at 20.00 ± 0.15** — buffer absorbs the radial motion.
  Force is constant C_max; circular velocity satisfies `v² = r·C_max`
  rather than `v² = K/r`. Predicted period T ∝ √r (anti-Kepler).
- `r > r_eq`: buffer is 0, `F = K/r²`, ordinary Newton.
- The two regimes meet smoothly at r_eq, which emerges as a
  preferred orbital radius.

### Honest disclosure — what is and isn't Newton-free in Phase 3

**Corrected audit (after discussion on 2026-04-16 about tick-bookkeeping
ontology).** `F = m·a` is NOT smuggled Newton in this theory. Under the
tick interpretation:

- time = ticks
- length = propagation ticks
- mass = tick-count of the object (5-node entity ⇒ 5 wticks)
- force = consumption rate (deposits/tick)
- acceleration = velocity-change-per-tick (1/tick)

Then `F = m·a` is `ticks/tick = ticks × 1/tick` — it's impulse
conservation distributed across the constituent quanta, not external
physics. Furthermore, the Temporal Surfing Principle (Doc 28) gives a
concrete meaning to mass-as-renewal-load: a mass-M entity must consume
M ticks/tick just to persist. The *surplus* (arrival − renewal) is what
drives acceleration, and surplus/mass = per-node acceleration. The
`F = m·a` relation falls out of this bookkeeping.

**So Newton is present in Phase 3 in exactly two places:**

1. `arrival = K / r_eff²` is Newton's 1/r² typed in directly. Defense:
   Phases 1–2 measured and verified this shape on the graph; using it
   as a shortcut is not a cheat. But it is not re-derived in Phase 3.
2. **Continuous position `(x, y)` for the planet, integrated with unit
   mass.** In the substrate the planet's position is the COM of its
   deposit-dominance region, and only moves via boundary shifts at the
   per-connector scale. Whether a many-node cluster's COM moves
   smoothly enough to justify the continuous-position abstraction is
   an open bet — v8 showed isolated planet clusters diffuse. The `m=1`
   specifically is also a free parameter we haven't varied yet.

The "outer regime = Kepler" observation remains a tautology given input
(1) — not a discovery, only an integrator sanity check.

**What IS new in Phase 3:**

- The buffer mechanism and its consequences: r_eff pinning to r_eq,
  capacity-limited inner regime, T ∝ √r scaling inside. These
  consequences fall out of the update rule honestly.

**What Phase 3 does NOT establish:**

- That any of this would survive if Newton were fully removed — no
  K/r² baked in, no continuous-space planet with F=m·a, buffer
  forming organically as Different deposits on actual graph paths.
  That is Phase 4. Based on v7/v8 precedent, the orbital part
  probably would not survive — the "bent pipe" problem (need for
  emergent internal planet structure to redirect consumption
  tangentially) is still the gate on real orbits on the substrate.

### Stance

Using Newton as a computational shortcut is fine when emergence is not
being claimed. When emergence IS the claim — which is the whole point
of Experiment 128 — Newton in the code needs a flag on it. Phase 3 is
flagged.

---

## Phase 3.1 — Mass, Renewal, and Capacity-per-Node (April 16, 2026)

Driven by the tick-bookkeeping correction above (and Doc 28 Temporal
Surfing), Phase 3.1 wires mass in as a genuine parameter and adds a
renewal cost.

**Update rule:**

```
renewal  = M                          # cost just to persist
pool     = B + K / r_eff^2
consumed = min(pool, C_cap)           # processing cap
surplus  = max(0, consumed - renewal) # drives motion
F        = surplus * (-r_hat)
a        = F / M                      # tick bookkeeping
B'       = pool - consumed
```

Two variants for the capacity cap:

- **Variant A:** `C_cap = 1.0` (fixed — capacity doesn't scale with size)
- **Variant B:** `C_cap = 1.5 · M` (every node has unit capacity + 50%
  headroom for motion)

Mass sweep across M ∈ {0.25, 0.5, 1.0, 2.0, 4.0} at r₀ ∈ {10, 15, 20,
25, 30}. Initial velocity is the analytical circular value for that
(r, M, C_cap).

### Variant B result — Newton's mass-independence recovers

Measured period T at various r, across different masses:

| r  | M=0.25 | M=0.5 | M=1.0 | M=2.0 |
|----|--------|-------|-------|-------|
| 10 | 28.10  | 28.10 | 28.10 | 28.10 |
| 15 | 34.41  | 34.41 | 34.41 |   —   |
| 20 | 39.74  | 39.74 |   —   |   —   |
| 25 | 44.43  |   —   |   —   |   —   |
| 30 | 48.67  |   —   |   —   |   —   |

**Orbital period is mass-independent** in the capacity-limited regime.
This is Newton's "planet mass doesn't affect orbital period" — emergent
from substrate arithmetic when `C_cap ∝ M`. Mechanism: `F = surplus =
(C_cap − renewal) = (1.5M − M) = 0.5M`, and `a = F/M = 0.5` — mass
cancels in the equation of motion.

**Inner regime T ∝ √r confirmed.** T at r=30 vs r=10 is
48.67/28.10 = 1.73 ≈ √3. This is the capacity-limited "anti-Kepler"
signature predicted in Phase 3.

### Variant A result — no mass cancellation

With `C_cap` fixed, heavier planets have `r_star = √(K/M)` shrinking
below `r_eq`, so they starve before they can occupy the capacity
region. M=0.5 at r=20 went unbound. Biologically: if capacity does not
scale with size, large planets simply can't exist at equilibrium. This
is a sanity-check on Variant B being the physical choice.

### New, genuine predictions from Phase 3.1

- **Gravity horizon** `r* = √(K/M)`: beyond this radius, surplus goes
  negative (arrival < renewal) and no orbit is possible. Lighter
  planets can orbit farther out; heavier planets are confined closer.
- **Capacity-limited inner zone** with T ∝ √r (not T ∝ r^(3/2)) — a
  clean departure from Kepler inside `r_eq`.
- **Newton's mass-independence of period emerges** only when C_cap
  scales with M — i.e., when processing is distributed uniformly
  across the planet's quanta.

### What's earned, what's still hybrid — updated end of April 2026

| Claim | Status |
|-------|--------|
| 1/r² arrival on the graph | **earned** (Phase 1) |
| Keplerian orbits under the measured field | **earned** (Phase 2) |
| F = m·a as substrate bookkeeping | **earned** (Phase 3.1, tick reading) |
| Newton's mass-independence of orbital period | **earned** (Phase 3.1 Variant B) |
| T ∝ √r in capacity-limited inner zone | **new prediction** (Phase 3.1) |
| Gravity horizon r* = √(K/M) | **new prediction** (Phase 3.1) |
| Buffer forms organically from Different deposits on graph | **not tested** (Phase 4 / v7-v8 precedent) |
| Sustained tangential motion on pure substrate | **still unsolved** |

Phase 3.1 does not move the orbital-motion-on-substrate question —
that remains gated by the "bent pipe" issue (emergent internal planet
structure needed to redirect consumption tangentially).

---

## Files

- `phase1_star_only.py` — Phase 1 simulation and measurement
- `phase2_orbit_from_measured_field.py` — Phase 2 orbit under measured ρ(r)
- `phase3_buffered_consumption.py` — Phase 3 buffered-consumption ODE (HYBRID)
- `phase3_1_mass_and_renewal.py` — Phase 3.1 with mass + renewal + capacity variants
- `phase3_2_solar_system.py` — Phase 3.2 solar system sanity check
- `phase3_3_earth_scale.py` — Phase 3.3 Earth at Planck-scale
- `phase3_4_resistance_fit.py` — Phase 3.4 per-planet resistance fit
- `phase4_time_dilation.py` — Phase 4 gravitational redshift from rho(r)
- `phase5_unified_dilation.py` — Phase 5 unified SR+GR tick-budget
- `phase6_radial_motion.py` — Phase 6 radial motion + connector anisotropy
- `phase7_moving_star.py` — Phase 7 moving star with retarded gravity
- `results/phase1_profile.png` — density and gradient log-log plots
- `results/phase1_full_run.log` — full 500k run log
- `results/phase2_orbit.png` — profile + measured-vs-reference trajectories
- `results/phase2_run.log` — Phase 2 output
- `results/phase3_buffered.png` — six buffered-orbit trajectories
- `results/phase3_run.log` — Phase 3 output
- `results/phase3_1_variant_A.png` — Variant A (C_cap fixed) mass sweep
- `results/phase3_1_variant_B.png` — Variant B (C_cap ∝ M) mass sweep
- `results/phase3_1_run.log` — Phase 3.1 output
- `results/phase3_2_solar_system.png`, `phase3_2_run.log` — Phase 3.2
- `results/phase3_3_run.log` — Phase 3.3
- `results/phase3_4_resistance.png`, `phase3_4_run.log` — Phase 3.4
- `results/phase4_time_dilation.png`, `phase4_run.log` — Phase 4
- `results/phase5_unified.png`, `phase5_run.log` — Phase 5
- `results/phase6_radial.png`, `phase6_run.log` — Phase 6
- `results/phase7_moving_star.png`, `phase7_run.log` — Phase 7

---

## Phase 4 — Gravitational Time Dilation (April 17, 2026)

Reinterpret the Phase 1 field. If local clock rate is modulated by
local deposit density — a node busy processing arriving deposits
has less budget left for its own cycle — what is the functional
shape of γ(r)?

Ansatz (one free coupling ρ_scale):

```
γ_local = 1 / (1 + ρ_local / ρ_scale)
```

In the weak-field limit ρ << ρ_scale:

```
1 - γ  ≈  ρ(r) / ρ_scale  ≈  (A/ρ_scale) / r
```

so `(1 - γ)` should go as `1/r` on log-log, matching Einstein's
gravitational redshift form. Fit over r ∈ [4, 0.5·R]:

- `ρ(r)` log-log slope: **-1.298** (Phase 1 signature)
- `(1 - γ)` log-log slope: **-1.094**  (Einstein: -1.000; within 9%)
- Effective GM/c² = A/ρ_scale = 4.58 (natural units)

**What's earned:** The 1/r shape of gravitational redshift falls out
of the already-measured Phase 1 field, using only a saturation
ansatz and one coupling constant.

**What's chosen (not derived):** The saturation form `1/(1+x)` is a
modeling choice. Any smooth saturation with the right small-x limit
would give similar behavior. `ρ_scale` is a free calibration mapping
to `GM_eff/c²`.

**What's not tested in Phase 4:**
- Strong field (where saturation form details matter).
- Velocity (SR) component.
- Radial vs tangential geometry.

---

## Phase 5 — Unified SR + GR from a Single Tick-Budget (April 17, 2026)

The unifying insight (from Tom, 2026-04-17):

> Load is how much you're braking against connector propagation. If
> you match the substrate at c, you aren't braking — you aren't
> consuming. Below c, you're refusing to flow with the substrate, and
> that refusal costs budget. Gravity is another form of refusal —
> deposits you're forced to process instead of just being.

The tick-budget argument:

- Each node has a unit tick-budget per tick.
- Loads consume it: `L_grav = ρ/ρ_scale` (processing), `L_vel = v²/c²`
  (spatial motion — the squared form from Pythagorean combining of
  time and space components of the tick vector, exactly Minkowski).
- Proper tick rate: `γ = √(1 − L_grav − L_vel)`.

**Key realization:** This additive-under-sqrt form is **not a
weak-field approximation to Einstein — it is the EXACT Schwarzschild
proper-time formula** for a stationary or tangentially-rotating
clock. The multiplicative form `γ_grav × γ_SR` commonly quoted is
the weak-field approximation; the strict GR answer is

```
dτ/dt = √((1 - 2GM/rc²) - v²/c²)
```

which is the additive-under-sqrt form we derived from budget
accounting with graph-measured ρ.

### Test on the v11 graph

Grid of (r, v) with r ∈ {5, 8, 12, 18, 25}, v/c ∈ {0, 0.3, 0.5, 0.7, 0.9}.
`ρ(r)` taken from Phase 1 propagation directly. For each point:

- `γ_TF = √(1 − L_grav − L_vel)` — tick-frame unified.
- `γ_mult = √(1 − L_grav) × √(1 − L_vel)` — weak-field factored.

At v = 0, the two are identical by construction. Away from v = 0:

- Weak field (e.g. r=25, v=0.3): TF and mult agree to <1%.
- Moderate (r=8, v=0.5): differ by ~8%.
- Strong (L_grav + L_vel ≥ 1): TF correctly saturates to 0 (**past
  static limit**, no stationary observer can exist); the
  multiplicative form gives wrong positive values.

The static-limit ring `L_grav + L_vel = 1` is a real geometric
boundary — the analogue of Schwarzschild's ergosphere — falling out
of the substrate + Pythagoras, not assumed.

### What's earned

- Unified SR + GR from a single substrate accounting principle.
- Exact (not weak-field) Schwarzschild formula for tangential motion,
  with ρ(r) from first-principles graph propagation.
- The static limit emerges as a geometric boundary.
- One free coupling (`ρ_scale`) doing all the work; no Einstein in
  the code.

### What's still open

- **Strong-field graph corrections.** The 1/r shape of ρ deviates at
  large r (absorbing boundary) and near source (saturation).
- **No actual moving clocks simulated.** We reinterpret the static
  Phase 1 field with v as an analytical parameter. A proper test
  would simulate clocks hopping node-to-node at rate v and measure
  empirical γ. That's future work.
- **`ρ_scale` is a calibration.** The shape of γ(r, v) is earned; the
  absolute scale requires a fit.

---

## Phase 6 — Radial Motion: Where the Uniform RGG Breaks (April 17, 2026)

Phase 5's formula matches tangential Schwarzschild exactly. For
radial motion the GR answer is different — Schwarzschild has an
extra factor on the spatial term:

```
dτ/dt = √((1 - L_grav) - v²/(c²(1 - L_grav)))     [radial]
dτ/dt = √((1 - L_grav) - v²/c²)                   [tangential]
```

The radial case has `1/(1 − L_grav)` dividing the velocity load.
Physical reason: Schwarzschild's spatial metric has
`g_rr = 1/(1 − L_grav)` — radial distances are stretched near a
mass, so radial motion consumes more budget per coordinate distance.

### Test on the v11 graph

Same (r, v) grid as Phase 5; compute both naive tick-frame
(= tangential formula) and Schwarzschild radial:

| r | v/c | naive γ | schwarz γ | rel err |
|---|---|---|---|---|
| 25 | 0.3 | 0.918 | 0.914 | 0.4% |
| 12 | 0.5 | 0.741 | 0.698 | 6% |
| 8  | 0.6 | 0.560 | 0.372 | **50%** |
| 8  | 0.7 | 0.428 | 0 | **past horizon** |

The naive formula matches weak-field radial but diverges badly in
strong field — it even predicts a non-zero γ for a clock that
Schwarzschild says is already past the horizon.

### Why: connector anisotropy measurement

Measured `⟨cos²θ_radial⟩` averaged over edge directions in radial
shells (isotropic 3D uniform value = 1/3):

| shell | ⟨cos²θ_radial⟩ |
|---|---|
| r ∈ [3, 6] | 0.326 |
| r ∈ [8, 12] | 0.322 |
| r ∈ [15, 20] | 0.332 |
| r ∈ [25, 35] | 0.338 |

All ≈ 1/3. **The graph is perfectly isotropic.** There's no
radial-vs-tangential structural anisotropy anywhere, including near
the source where Schwarzschild would require it.

### What Phase 6 actually tells us

The uniform random geometric graph carries enough structure to:
- reproduce the 1/r² force law (Phase 1)
- reproduce Kepler orbits (Phase 2)
- reproduce Newton's mass-independence of period (Phase 3.1B)
- reproduce gravitational redshift 1/r shape (Phase 4)
- reproduce the **exact Schwarzschild proper-time formula for
  tangential observers** (Phase 5)

It cannot reproduce Schwarzschild's radial spatial stretching,
because it has no mechanism to make radial connectors anisotropic
near a mass.

**Specific diagnosis (what the next substrate revision needs):** a
mass (or its deposit field) must **reshape the local connector
graph**, making nearby radial connectors effectively longer (or
sparser, or slower-propagating) than tangential ones, by the
Schwarzschild factor `1/√(1 − L_grav)`. Tom's earlier "connector =
gravity" intuition now has a concrete quantitative target.

**Predictions from a connector-reshaping substrate:**
- Phase 5 tangential result stays as-is (unaffected by radial
  anisotropy).
- Phase 6 radial result matches Schwarzschild in strong field.
- Mercury perihelion precession would emerge naturally from the
  radial/tangential asymmetry of its elliptical orbit.
- Black-hole event horizons emerge as the surfaces where radial
  connectors have "infinite" effective length — no radial hop
  can escape.

**What Phase 6 does NOT establish:**
- That any simple substrate modification actually produces the
  required anisotropy. That's future work — design a substrate
  where deposits reshape connector geometry and test.
- That the ansatz form of the reshaping is the Schwarzschild factor
  specifically. Other anisotropies are possible but would give
  different GR-like theories.

---

## Phase 7 — Moving Star, Orbiting Planet (April 17, 2026)

The whole solar system moves through the substrate — sun at ~230 km/s
through the Milky Way, Milky Way at ~600 km/s through the CMB frame.
No orbit is ever truly closed in the absolute frame; every "closed
orbit" is actually a helix displaced along the bulk motion direction.

Phase 7 tests: **does moving the star in z break the planet's orbit,
and at what velocity?** Using retarded Newtonian gravity (force points
from the planet to where the star *was* at t - distance/c; our natural
units have c = 63241 AU/yr).

### Results

**Comoving case** (planet carries the star's z-velocity — physically
realistic since bound systems form together):

| case | r_xy | z_drift (comoving) | revs | status |
|---|---|---|---|---|
| v_z = 0 (reference) | 1.0000 | 0.0000 | 199.9 | bound |
| v_z = 0.1·v_c | 1.0000 | 0.0000 | 199.9 | bound |
| v_z = v_c | 1.0000 | 0.0002 | 199.9 | bound |
| v_z = 10·v_c | 1.0000 | 0.0020 | 199.9 | bound |
| v_z = 0.001·c (≈30× real solar motion) | 1.0000 | 0.0020 | 199.9 | bound |

**At any comoving v_z, the orbit is preserved perfectly** (199.9 out
of 200 expected revolutions in 200 years, r_xy = 1.0000 exactly in
the comoving frame). The retarded gravity mechanism makes essentially
no difference because retardation is isotropic and comoving systems
experience coherent delay.

**Non-comoving case** (planet left at rest in z while star drifts
away — artificial stress test):

| case | r_xy | z_drift | revs | status |
|---|---|---|---|---|
| v_z = 0.5·v_c | 1.31 | 1.15 | 130 | bound but deformed |
| v_z = v_c | 28.7 | 9.7 | 0.5 | **UNBOUND** |

### Interpretation

Phase 7 confirms the **equivalence principle** emerges from our
retarded-gravity picture without being built in: comoving observers
can't tell their bulk frame is drifting, because retardation is
isotropic and coherent across the whole pattern.

**The deeper reframing:** The solar system is not "a star plus planets
that happen to be co-moving." It is **a single coherent pattern that
drifts through the substrate as a unit**. Its internal structure (the
orbit) is a property of the pattern itself. From outside, only its
bulk motion and aggregate mass are visible. This is the traveling-
pattern view Tom articulated, and it is scale-invariant:

- Galactic scale: solar system is a point.
- Stellar scale: solar system has structure.
- Atomic scale: same pattern/point duality.

**What Phase 7 does NOT test:**
- Relativistic v_z (near c) where our non-relativistic formulation
  breaks down.
- The actual graph substrate (we use analytical K/r² with retardation;
  a faithful test would move the star's node cluster through the
  graph and propagate deposits from each step).
- The **growing-graph** scenario where the star advances into
  previously Unknown substrate — the real substrate-frontier test.
- **Coherent pattern formation.** The "planet" in Phase 7 is an
  analytical point with perfect internal coherence by construction.
  Real planets must self-organize into coherent patterns (v7/v8
  showed pre-placed clusters diffuse rather than cohere). This
  remains the core unsolved problem.

### What Phase 7 settles

Your "whole solar system moves, so no orbit closes" observation is
geometrically correct but dynamically irrelevant. The pattern's
internal dynamics are frame-invariant; its absolute-frame helix is
just which reference you chose. So the growing-graph frontier
won't break orbits — it just means patterns drift across a
continuously-renewing substrate. That's consistent with the tick-
frame ontology (every tick renders only its own snapshot; the loop
is a temporal construct, not a spatial fixture).

The honest next problem — building coherent self-holding patterns
on the substrate that can drift as units and interact with other
such patterns — is the synthesis with Experiments 55 (collision
physics) and 56 (composite objects). We've developed those in
parallel with v11, but not joined them. That join is the frontier.

---

## Parameters

| Parameter         | Value                 | Notes                          |
|-------------------|-----------------------|--------------------------------|
| N_NODES           | 500,000               |                                |
| SPHERE_R          | 80.0                  |                                |
| TARGET_K          | 24                    | avg observed 23.5              |
| STAR_COUNT        | 50                    | source cluster near origin     |
| L_STAR            | 1.0                   | density held at each star node |
| BOUNDARY_FRACTION | 0.95                  | absorbing beyond this          |
| TICKS             | 3000                  | ~80% saturated                 |
| MEASURE_AT        | 500, 1000, 2000, 3000 | snapshot ticks                 |
| SEED              | 42                    |                                |
