### Experiment brief — visualization of unified gamma‑field geometries (V2/V3 prototype)

#### 1. Goal

**Visualize all core gamma‑field geometries in one interactive experiment:**

- radial curvature (gravity)
- tangential curvature (magnetism)
- unified EM curvature
- charge handedness
- fragment trajectories
- dissolution
- extreme compression

The point is **not** physical accuracy, but **faithful ontology**: the visuals must reflect RAW 081–088 logic.

---

#### 2. Scene setup

- **Space:**
    - 2D plane (for first prototype), normalized coordinates \([-1, 1] \times [-1, 1]\).
- **Field resolution:**
    - grid or texture (e.g. 512×512 or 1024×1024).
- **Time:**
    - discrete ticks, mapped to `dt` in your engine.

- **Core objects:**
    - **Entity:** position, lag `L`, rotation `ω`, well depth `W`, charge sign `Q`.
    - **Fragments:** list of subcritical wells with position, velocity, decay.
    - **Residual field:** scalar “noise/heat” texture.
    - **Gamma field:** conceptual—visualized via derived quantities (curvature, flow).

---

#### 3. Visual encodings

**a) Radial curvature (gravitational well)**
- Render as **brightness or depth** around entity.
- Higher curvature → darker or deeper.
- Use radial falloff from entity center.

**b) Tangential curvature (magnetic well)**
- Render as **vector field** (arrows/streamlines) circling entity.
- Direction encodes charge sign (clockwise vs counterclockwise).
- Magnitude encodes magnetic strength `M`.

**c) Unified EM field**
- Combine:
    - radial curvature → scalar channel (e.g. brightness)
    - tangential curvature → vector overlay (arrows/lines)
- Optionally:
    - use color hue for tangential, intensity for radial.

**d) Charge**
- Positive charge: one color (e.g. blue), clockwise flow.
- Negative charge: another color (e.g. red), counterclockwise flow.
- Neutral: desaturated / no tangential flow.

**e) Fragments**
- Render as small moving dots or pulses.
- Their paths are bent by tangential curvature.
- Fade out over time (decay → residual).

**f) Residual field**
- Low‑frequency noise texture.
- Brightening where fragments dissipate.
- Slowly diffuses over time.

**g) Dissolution**
- Entity well shallows (brightness/depth decreases).
- Tangential field weakens.
- Entity core fades into residual noise.

**h) Extreme compression**
- Very deep radial well (strong brightness/depth contrast).
- Very strong tangential flow (dense streamlines).
- Fragments spiral inward and get trapped.

---

#### 4. Core update loop (per tick)

1. **Update entity state**
    - Apply energy regime (normal / starvation / extreme) from RAW 083, 085.
    - Update `L`, `W`, `ω`, `Q`.

2. **Compute radial curvature field**
    - For each pixel:
        - compute distance to entity
        - compute radial curvature scalar `C_r(x,y)`.

3. **Compute tangential curvature field**
    - For each pixel:
        - compute direction around entity
        - compute tangential curvature vector `C_t(x,y)` based on `ω`, `L`, `Q`.

4. **Update fragments**
    - Move fragments according to:
        - base velocity
        - plus deflection from `C_t(x,y)`
    - Apply decay; when below threshold → add to residual.

5. **Update residual**
    - Add fragment decay energy.
    - Apply diffusion blur.

6. **Render**
    - Combine:
        - radial curvature → scalar channel
        - tangential curvature → vector overlay
        - fragments → particles
        - residual → background texture
        - entity → core marker (●).

---

#### 5. Experimental scenarios

Run at least these modes:

1. **Pure gravity:**
    - `ω = 0`, `Q = 0`.
    - Only radial well visible.

2. **Pure magnetism:**
    - `W` small, `ω ≠ 0`, `L > 0`.
    - Tangential field visible, weak radial.

3. **Charged entity:**
    - `Q > 0` and `Q < 0` cases.
    - Show opposite handedness of flow.

4. **Fragment emission & deflection:**
    - Entity with excess energy (RAW 084).
    - Emit fragments and visualize their curved paths.

5. **Energy starvation:**
    - Gradually reduce ΔE_in.
    - Watch well shallow, tangential field collapse, entity dissolve.

6. **Extreme compression:**
    - Push `W`, `L`, `ω` to high values.
    - Show deep well, strong tangential flow, fragment trapping.

---

#### 6. Success criteria

- **Clarity:**
    - You can visually distinguish radial vs tangential behavior at a glance.
- **Polarity:**
    - Charge sign is obvious from flow orientation.
- **Dynamics:**
    - Fragments clearly respond to tangential curvature.
- **Regimes:**
    - Normal, starvation, and extreme compression look qualitatively different but ontologically consistent.
- **Coherence:**
    - No visual element contradicts RAW 081–088.
