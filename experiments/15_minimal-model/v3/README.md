# V3 - Advanced Threshold Analysis

## Overview

Version 3 builds on the refined boundary findings from v2, implementing the next-step experiments to deeply characterize the onset dynamics and extend the model's capabilities.

## V2 Key Finding (Baseline)

**Critical threshold: α₀ ≈ 1.85–1.90** (for γ=0.001, M=1, T=100s)

---

## V3 Experimental Goals

### 1. Ultra-Fine Resolution Sweep ✓
- **Objective**: Pinpoint threshold to ±0.01 precision
- **Range**: α₀ ∈ [1.80, 1.95]
- **Resolution**: Δα₀ = 0.01
- **Status**: Ready to implement

### 2. Dynamic Ψ(t) Buildup Analysis ✓
- **Objective**: Characterize temporal evolution of salience accumulation
- **Metrics**:
  - Buildup rate: dΨ/dt
  - Threshold crossing time
  - Growth regime (linear/exponential/power-law)
- **Status**: Ready to implement

### 3. Extended Time Horizon Tests
- **Objective**: Test if late-time commits change threshold
- **Time ranges**: T ∈ {100, 200, 500}s
- **Question**: Do commits saturate or continue growing?
- **Status**: Planned

### 4. Multi-Source Scenarios
- **Objective**: Investigate artefact interference and superposition
- **Configurations**:
  - 2 sources at different positions
  - Synchronous vs. asynchronous emissions
  - Constructive/destructive interference patterns
- **Status**: Planned

### 5. Analytical Threshold Model
- **Objective**: Derive theoretical expression for α₀_threshold(γ, M, T)
- **Approach**:
  - Energy balance analysis
  - Dimensional analysis
  - Fit to numerical data
- **Status**: Planned

---

## Implementation Priorities

1. **Ultra-fine sweep** - Immediate (highest precision threshold)
2. **Dynamic buildup** - High (mechanistic understanding)
3. **Extended time** - Medium (long-term behavior)
4. **Multi-source** - Medium (spatial complexity)
5. **Analytical model** - Ongoing (theoretical foundation)

---

## Expected Outcomes

### Ultra-Fine Sweep
- Threshold precision: ±0.01 (vs. current ±0.05)
- Identify if threshold is continuous or has discrete jumps

### Dynamic Analysis
- Determine growth law: Ψ(t) ~ t^β or Ψ(t) ~ exp(λt)
- Measure threshold crossing time as function of α₀
- Characterize "buildup window" where Ψ approaches 1.01

### Extended Time
- Test if threshold is time-independent
- Check for saturation effects
- Measure long-term commit rate

### Multi-Source
- Map interference patterns in artefact field
- Test if superposition is linear or nonlinear
- Identify optimal source configurations for visibility

---

## Development Notes

- Keep v2 results as baseline for comparison
- Document all findings in consolidated reports
- Generate visualizations for each experiment
- Cross-validate results with v1 and v2 data

---

**Version**: 3.0-dev
**Created**: 2025-11-17
**Based on**: v2 refined boundary analysis
