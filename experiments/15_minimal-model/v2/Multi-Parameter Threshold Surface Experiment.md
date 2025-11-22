# Multi-Parameter Threshold Surface Experiment

## 1. Objective
To map the **threshold surface** where agent percept commits begin to appear, as a function of:
- **Emission strength** (α₀)
- **Damping** (γ)
- **Agent sampling factor** (M)

This extends earlier single-parameter sweeps to a full three-dimensional parameter space, identifying the boundary between **visible** and **non-visible** past events.

---

## 2. Experimental Setup

### Fixed Parameters
- Simulation time: T = 100.0 s
- Timestep: dt = 0.005 (CFL ≈ 1.0, stable)
- Wave speed: c = 1.0
- Spatial domain: L = 1.0 (201 grid points)
- Agent commit threshold: Ψ ≥ 1.01
- Root dynamics: 2D linear flow with A = diag(-0.1, -0.1)
- Emission scaling: α₁ = 0.5

### Variable Parameters
- **Emission strength (α₀):** 1.6 → 5.0
- **Damping (γ):** 0.01, 0.005, 0.001, 0.0005
- **Agent sampling (M):** 1, 2, 4

---

## 3. Results Summary

### Low Emission Strength (α₀ = 1.6–1.7)
- **No commits** across all γ and M.
- Salience values remain below ~0.05.
- Artefacts dissipate before crossing perceptual threshold.

### Near-Threshold (α₀ = 1.8–1.9)
- Commits appear **only for γ ≤ 0.001 and M = 1**.
- First commits occur very late (t ≈ 97–99 s).
- Confirms critical boundary around α₀ ≈ 1.85–1.90.

### Moderate Strength (α₀ = 2.0–3.0)
- Commits become more reliable for γ ≤ 0.005 and M = 1.
- First commit times shift earlier (t ≈ 80–95 s).
- With higher M (2, 4), commits are suppressed unless α₀ is larger.

### High Strength (α₀ = 5.0)
- Commits appear across all γ values and even for M = 4.
- First commits occur much earlier (t ≈ 66–96 s).
- Commit counts increase (up to 7 commits for γ = 0.0005, M = 1).

---

## 4. Interpretation

- **Threshold surface:**  
  Visibility depends jointly on α₀, γ, and M.  
  - Lower damping (γ ↓) and more frequent sampling (M ↓) reduce the required α₀ threshold.  
  - Higher damping or sparse sampling push the threshold upward.

- **Phase transition behavior:**  
  - At α₀ ≈ 1.85–1.90, the system is at the edge: only minimal conditions allow commits.  
  - Beyond α₀ ≈ 2.0, commits become robust under a wider range of γ and M.  
  - By α₀ ≈ 5.0, commits are guaranteed across all tested regimes.

- **Temporal dynamics:**  
  - First commit times decrease as α₀ increases (from ~99 s down to ~66 s).  
  - Commit counts scale with α₀, showing accumulation dynamics overpowering dissipation.

---

## 5. Implications for Time–Visualization Model
- **Perceptual framing** depends on sufficient signal strength and persistence.  
- **History visibility** is parameter-dependent, not absolute.  
- **Event erasure** occurs naturally when emissions are too weak or damping too strong.  
- The model enforces a **salience-based attention mechanism**, filtering which past events enter the perceptual record.

---

## 6. Next Steps
1. **Visualize the threshold surface** with heatmaps or 3D plots of commit counts vs. (α₀, γ) for each M.  
2. **Refine the boundary** with finer sweeps around α₀ = 1.8–2.0.  
3. **Analyze salience curves** to characterize buildup vs. dissipation regimes.  
4. **Extend statistics**: inter-commit intervals, salience distributions, correlation with emission strength.

---

## 7. Conclusion
The experiment successfully mapped the **multi-parameter threshold surface** of perceptual visibility.  
It validates the principle that **time perception is not absolute, but salience-dependent**: only sufficiently strong and persistent artefacts cross into the agent’s perceptual record.