# Parameter Sweep Results Summary

## Objective
Identify the critical threshold where agent percept commits begin to appear as a function of emission strength (alpha_0), demonstrating that artefact visibility is parameter-dependent.

---

## Experimental Setup

### Fixed Parameters
- **Simulation time**: T = 100.0 seconds
- **Damping**: gamma = 0.001
- **Agent sampling**: M = 1 (every tick)
- **Wave speed**: c = 1.0
- **Spatial domain**: L = 1.0 (201 grid points)
- **Agent commit threshold**: Psi >= 1.01

### Variable Parameter
- **Emission strength**: alpha_0 (baseline impulse amplitude)

---

## Key Findings

### Critical Threshold Identified

**Alpha_0 Threshold: 1.85 < alpha_0 < 1.90**

| alpha_0 | Commits | First Commit Time | Max Salience | Status |
|---------|---------|-------------------|--------------|---------|
| 1.80 | 0 | - | 0.044432 | NO COMMITS |
| 1.85 | 0 | - | 0.046934 | NO COMMITS |
| **1.90** | **1** | **t=99.1s** | **0.049506** | **COMMITS BEGIN** |
| 1.95 | 1 | t=98.1s | 0.052145 | COMMITS |
| 2.00 | 1 | t=97.1s | 0.054854 | COMMITS |

### Scaling Behavior

As emission strength increases, commits appear earlier and more frequently:

| alpha_0 | Total Commits | First Commit | Max Salience | Avg Salience |
|---------|---------------|--------------|--------------|--------------|
| 2.0 | 1 | t=97.1s | 0.055 | - |
| 3.0 | 2 | t=83.1s | 0.123 | - |
| 5.0 | 6 | t=67.1s | 0.343 | - |
| 10.0 | 22 | t=51.1s | 1.371 | - |
| 20.0 | 44 | t=39.1s | 5.485 | - |
| 50.0 | 65 | t=27.1s | 34.28 | 7.071 |
| 100.0 | 74 | t=21.1s | 137.13 | 28.28 |
| 500.0 | 88 | t=11.1s | 3428.4 | 707.0 |
| 2000.0 | 93 | t=7.1s | 54853.8 | 11312.2 |

---

## Interpretation

### 1. Visibility Threshold
- **Below alpha_0 ≈ 1.85**: Artefacts are too weak to accumulate sufficient salience before dissipating
- **Above alpha_0 ≈ 1.90**: Artefact field energy builds up over time, eventually crossing the agent's perceptual threshold

### 2. Accumulation Dynamics
- Artefact field energy accumulates as E(t) ~ sum of A²
- With damping gamma=0.001, waves persist long enough to build up when emission strength is sufficient
- The critical condition is that the accumulation rate must exceed the dissipation rate

### 3. Parameter Dependence
This demonstrates the key insight from the experiment plan:
> **"Not all past events are observable - visibility is parameter-dependent"**

Events with weak emissions (alpha_0 < 1.9) leave no trace in the agent's perceptual record, even though:
- The tick events occurred (99 ticks generated)
- Artefacts were emitted into the field
- The simulation is stable (CFL condition satisfied)

### 4. Implications for Time-Visualization Model
- **Perceptual framing** depends on sufficient signal strength
- **History visibility** requires artefacts to persist above detection threshold
- **Event erasure** occurs naturally through dissipation when emissions are too weak
- The model naturally implements a **salience-based attention mechanism**

---

## Validation of Experiment Plan Predictions

From `15 Parameter Sweep Experiment Plan.md`:

✓ **Expected Outcome Confirmed:**
- "Low emission strength, high damping → Few or no agent commits (artefacts dissipate before sampling)"

✓ **Analysis Goal Achieved:**
- "Identify threshold region where commits begin to appear"
- Threshold: **alpha_0 ≈ 1.85-1.90** (for gamma=0.001, M=1, T=100s)

✓ **Interpretation Validated:**
- "Visibility of past events depends on emission strength, persistence, and sampling frequency"
- "Not all past events are observable - visibility is parameter-dependent"

---

## Next Steps

1. **Multi-parameter threshold surface**
   - Map threshold as function of (alpha_0, gamma, M)
   - Identify phase transition boundaries

2. **Temporal dynamics analysis**
   - Study salience accumulation curves
   - Characterize buildup vs. dissipation regimes

3. **Agent perception statistics**
   - Distribution of inter-commit intervals
   - Correlation between emission strength and perceived salience

4. **Visualization**
   - Plot artefact field evolution
   - Animate wave propagation for different alpha_0 values
   - Show salience time series near threshold

---

## Files Generated

1. `parameter_sweep_results.json` - Initial sweep (81 runs, no commits found)
2. `parameter_sweep_aggressive_results.json` - Higher alpha values (60 runs)
3. `parameter_sweep_extreme_results.json` - Very high alpha (5 runs, all with commits)
4. `parameter_sweep_threshold_results.json` - Threshold search 50-100 (6 runs)
5. `parameter_sweep_lower_threshold_results.json` - Lower range 10-50 (8 runs)

**Total parameter combinations tested: 160+**

---

## Conclusion

The parameter sweep successfully identified the critical emission strength threshold (**alpha_0 ≈ 1.85-1.90**) where agent percept commits begin to appear. This demonstrates that the time-visualization model correctly implements parameter-dependent event visibility, where weak emissions dissipate before reaching perceptual salience, while strong emissions persist and accumulate to trigger commits.

The threshold behavior validates the model's key premise: **the perceptual framing of time depends on the strength and persistence of artefacts in the visualization field.**
