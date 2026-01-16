# Baseline: Validation Against Experiment #15

## Purpose

Quick validation runs to ensure our experimental setup produces results consistent with the original Experiment #15 v6-gpu and v7-final.

## Test Cases

Run 5-10 key parameter configurations for each dimension:
- **3D**: 48×48×48 grid
- **4D**: 16×16×16×16 grid
- **5D**: 10×10×10×10×10 grid

Parameters at known stable/unstable points:
- α₀ = 0.8, 1.4, 2.0, 2.4
- γ = 0.1, 0.3
- Ms = 1, 2
- T = 200, 500

## Acceptance Criteria

Metrics must match v7-final within **5%**:
- CV (coefficient of variation)
- ρ (source scaling)
- Gradient (transition sharpness)
- Salience (field energy)

If baseline fails → debug setup before running full (n+t) sweep.

## Expected Runtime

~30 configs × ~5s each = **2-3 minutes**
