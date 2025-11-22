# Visibility Boundary Framework for Long Horizon Tick-Frame Experiments

## Purpose and Context
Long horizons amplify subtle dynamics but can exceed what an observer can coherently resolve.  
To preserve scientific validity, we cap horizons where recession or effective motion outpaces the observer’s framerate, preventing perceptual aliasing.  
This framework formalizes a visibility boundary so reported salience remains interpretable and falsifiable.

---

## Definitions
- **Observer framerate:** Number of visualized frames per unit time based on tick aggregation.  
- **Motion budget:** Maximum per-frame displacement that remains perceptually coherent.  
- **Expansion velocity:** Effective recession speed as a function of distance, analogous to cosmological expansion.  
- **Effective motion:** Combined local kinematics plus expansion affecting tracked entities.

---

## Equations

- **Observer framerate**

  \[
  f_{\text{obs}}=\frac{r_{\text{tick}}}{N_{\text{ticks/frame}}},\quad \Delta t_{\text{frame}}=\frac{1}{f_{\text{obs}}}
  \]

- **Per-frame motion budget**

  \[
  v_{\text{frame}}=\frac{d_{\text{max}}}{\Delta t_{\text{frame}}}
  \]

- **Expansion velocity**

  \[
  v_{\text{rec}}(d)=H\cdot d
  \]

- **Visibility condition and horizon distance**

  \[
  v_{\text{rec}}(d)\leq v_{\text{frame}}\ \Rightarrow\ d\leq d_{\text{vis}}=\frac{v_{\text{frame}}}{H}
  \]

- **Aliasing stop rule**

  \[
  v_{\text{eff}}>\,v_{\text{frame}}\ \Rightarrow\ \texttt{beyond\_horizon}=1
  \]

---

## Operationalization

- **Dynamic horizon computation:**  
  - Inputs: \(r_{\text{tick}},\,N_{\text{ticks/frame}},\,d_{\text{max}},\,H\).  
  - Compute: \(f_{\text{obs}}, \Delta t_{\text{frame}}, v_{\text{frame}}, d_{\text{vis}}\).  
  - Track: For each entity and frame, estimate \(v_{\text{eff}}\).  
  - Cap \(T_{\max}\): Choose the smallest \(T\) at which any entity satisfies \(v_{\text{eff}}\leq v_{\text{frame}}\).

- **Guard rails:**  
  - **Early-stop:** Stop when \(v_{\text{eff}}>\,v_{\text{frame}}\) for \(k\) consecutive frames.  
  - **Downsample:** Increase \(N_{\text{ticks/frame}}\) or tighten \(d_{\text{max}}\) to restore visibility.  
  - **Audit logs:** Record \(v_{\text{eff}}, v_{\text{frame}}, d_{\text{vis}}, f_{\text{obs}}, \Delta t_{\text{frame}}\).  
    - Events: aliasing_detected, beyond_horizon_tick, resample_applied, early_stop_triggered.

---

## Dashboard Additions

- **Visibility badge:**  
  - Fields: f_obs, Δt_frame, d_max, v_frame, H, d_vis, T_max.  
  - State: visible / boundary / beyond_horizon (color-coded).

- **Horizon indicators:**  
  - Graphs: \(v_{\text{eff}}\) vs. frame overlaying \(v_{\text{frame}}\).  
  - Events timeline: Mark aliasing_detected and early_stop_triggered ticks.

- **Policy note:**  
  - Rule: We do not report salience or dynamics beyond the visibility horizon; such frames are flagged and excluded from physics summaries.

---

## Recommended Next Steps

- **Calibrate \(d_{\text{max}}\):** Sweep per-frame displacement vs. coherence to set a conservative bound.  
- **Estimate \(v_{\text{eff}}\):** Instrument motion tracking with expansion \(H\) on/off to quantify impact.  
- **Validate \(T_{\max}\):** Bracketing runs around \(T_{\max}\) to confirm boundary behavior.  
- **Integrate into runs:** Adopt visibility guard as a standard precondition for long-horizon experiments.  
- **Document:** Boundary hits and adjustments in the anomaly log.

---

### Concluding Remark
This framework ensures long-horizon experiments remain scientifically interpretable by enforcing a clear, auditable visibility boundary.  
Physics may remain stable beyond the boundary, but observation must not: when effective motion exceeds the observer’s resolvable budget, we stop, flag, or resample — and we log every decision.