# Test suite for electromagnetism in the tick‑frame universe

Below is a structured proposal for a **simulation test suite** that jointly validates:

- electric fields (gamma gradients),
- magnetic fields (gamma anisotropies),
- full electromagnetism (coupled dynamics, waves, devices).

You can treat each test as an `experiment_XX_*` candidate.

---

## 1. Electric field tests (gamma gradients)

### 1.1 Single source gamma well (Coulomb analog)

- **Goal:** Show that a single static pattern creates a gamma well with a predictable radial profile and induces drift
  in test patterns.
- **Setup:**
    - Place a static pattern at the center of the grid.
    - Spawn light test patterns at various radii with small initial velocities.
- **Metrics:**
    - Radial gamma profile \(\gamma(r)\) vs. distance.
    - Drift velocity vs. radius.
    - Compare to expected monotonic behavior (e.g., approximate inverse‑square in appropriate regime).
- **Pass criteria:**
    - Test patterns accelerate consistently toward/away from the source.
    - Drift magnitude scales with gradient of gamma.

---

### 1.2 Two‑body interaction (Coulomb‑like)

- **Goal:** Show attraction/repulsion and stable orbits/escape depending on initial conditions.
- **Setup:**
    - Two static patterns with opposite/same gamma deformation signatures.
    - One light test pattern initially near one of them.
- **Metrics:**
    - Relative trajectories.
    - Effective force law inferred from motion (fit to \(1/r^2\) where applicable).
- **Pass criteria:**
    - Opposite signatures → attraction.
    - Same signatures → repulsion.
    - Qualitative Coulomb‑like behavior.

---

### 1.3 Dipole field

- **Goal:** Show that two opposite gamma wells form a dipole‑like field.
- **Setup:**
    - Two static patterns separated by fixed distance with opposite signatures.
    - Probe gamma field and test pattern trajectories around them.
- **Metrics:**
    - Field line structure (streamlines of \(\nabla \gamma\)).
    - Torque on a small test dipole.
- **Pass criteria:**
    - Dipole‑like field topology.
    - Correct alignment/torque behavior.

---

## 2. Magnetic field tests (gamma anisotropies)

### 2.1 Single moving pattern (magnetic precursor)

- **Goal:** Show that a moving pattern induces lateral drift in nearby test patterns.
- **Setup:**
    - One pattern moving at constant velocity through the grid.
    - Light test patterns placed near its path.
- **Metrics:**
    - Lateral displacement of test patterns vs. relative velocity and distance.
- **Pass criteria:**
    - Sideways drift appears only when the source pattern moves.
    - Drift direction consistent with “right‑hand rule” analog.

---

### 2.2 Circular current loop

- **Goal:** Show that a loop of moving patterns generates a macroscopic gamma anisotropy (magnetic‑like field).
- **Setup:**
    - Arrange patterns in a ring, moving coherently (current loop).
    - Place test patterns above/below the loop.
- **Metrics:**
    - Gamma anisotropy map.
    - Test pattern trajectories (circular/spiral motion).
- **Pass criteria:**
    - Field concentrated near loop.
    - Test patterns exhibit loop‑like or helical motion.

---

### 2.3 Lorentz‑like motion in crossed gamma

- **Goal:** Reproduce Lorentz‑like behavior from gamma geometry.
- **Setup:**
    - Region with strong gamma gradient (E analog).
    - Superimposed gamma anisotropy (B analog).
    - Inject test patterns with various velocities.
- **Metrics:**
    - Trajectories (spirals, cyclotron‑like orbits).
    - Radius vs. velocity and anisotropy strength.
- **Pass criteria:**
    - Radius ∝ velocity / anisotropy (qualitative scaling).
    - Clear lateral deflection consistent with “v × B” analog.

---

## 3. Electromagnetic wave tests (gamma oscillations)

### 3.1 Local gamma oscillation → wave propagation

- **Goal:** Show that a localized time‑varying gamma disturbance propagates as a wave.
- **Setup:**
    - Oscillate gamma in a small region (source).
    - No patterns needed initially.
- **Metrics:**
    - Gamma(t, x) snapshots.
    - Wavefront speed.
    - Interference from two sources.
- **Pass criteria:**
    - Stable propagation at constant speed.
    - Interference patterns when using two sources.

---

### 3.2 Polarization and directionality

- **Goal:** Show that gamma oscillations can have different polarization modes.
- **Setup:**
    - Create oscillations with different directional structures.
- **Metrics:**
    - Field patterns orthogonal in structure.
    - Response of test patterns to different polarizations.
- **Pass criteria:**
    - Distinct, stable polarization modes.
    - Different pattern responses depending on polarization.

---

## 4. Device‑level tests

### 4.1 Magnetron (rotating pattern + cavity modes)

- **Goal:** Demonstrate self‑excited oscillation via rotating electron pattern and cavity gamma modes.
- **Setup:**
    - Cathode + anode geometry with cavities.
    - Gamma gradient (E analog) + anisotropy (B analog).
    - Emit light patterns (electrons) from cathode.
- **Metrics:**
    - Formation of rotating ring (mean radius, angular velocity).
    - Gamma oscillation amplitude in cavities.
    - Frequency spectrum of cavity gamma.
- **Pass criteria:**
    - Stable rotating ring (space charge wheel analog).
    - Dominant cavity mode frequency.
    - DC → AC conversion in gamma.

---

### 4.2 Railgun (gamma gradient acceleration)

- **Goal:** Show that strong gamma gradients can accelerate a composite pattern along a guided path.
- **Setup:**
    - Rail‑like gamma geometry (channel with strong gradient).
    - Composite pattern (projectile) at rest at one end.
- **Metrics:**
    - Projectile velocity vs. time.
    - Energy transfer from gamma to pattern.
- **Pass criteria:**
    - Monotonic acceleration along rails.
    - Scaling of final velocity with gradient strength.

---

### 4.3 Coil / transformer analog

- **Goal:** Demonstrate inductive coupling via time‑varying gamma anisotropy.
- **Setup:**
    - Primary loop with oscillating pattern flow (current analog).
    - Secondary loop nearby.
- **Metrics:**
    - Induced drift/energy in secondary patterns.
    - Dependence on distance and orientation.
- **Pass criteria:**
    - Clear induced behavior in secondary loop.
    - Strong dependence on coupling geometry.

---

## 5. Cross‑scale and consistency tests

### 5.1 Parameter scaling

- **Goal:** Check that the same rules scale from micro to macro.
- **Setup:**
    - Repeat selected tests (e.g., dipole, loop, wave) at different spatial/temporal scales.
- **Metrics:**
    - Dimensionless quantities (e.g., ratios of radii, frequencies, velocities).
- **Pass criteria:**
    - Invariant behavior under rescaling (within numerical limits).

---

### 5.2 Unification checks

- **Goal:** Ensure that electric, magnetic, and wave behavior are not patched separately but arise from the same gamma
  engine.
- **Setup:**
    - Use a single gamma update pipeline for all tests.
- **Metrics:**
    - No special‑case code paths for “E” vs “B”.
    - All phenomena emerge from gamma gradients + anisotropies + pattern motion.
- **Pass criteria:**
    - Removing anisotropy kills magnetic effects but leaves electric behavior.
    - Removing gradients kills electric behavior but leaves pure wave propagation (if initialized).

