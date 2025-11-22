# Time–Visualization Model Layers (with Multi-Source Extension)

Root Substrate Layer
--------------------
- 2D linear ODE system (x evolves under A, b)
- Provides the "state vector" foundation

Tick Generator Layer
--------------------
- Planck-scaled accumulator Θ
- Commits occur when Θ crosses n + δ
- Each commit triggers an emission event

Artefact Field Layer
--------------------
- 1D damped wave equation
- Driven by impulses from sources
- Field energy accumulates and dissipates

Multi-Source Objects
--------------------
- Mₛ ≥ 1 emission objects placed at positions s₁, s₂, …, sₘ
- Each emits impulse qₘ at commit times
- Can be symmetric, asymmetric, or phased
- In practice: geometry/phase don’t change threshold, but more sources accelerate commits

Agent Layer
-----------
- Samples field every M ticks
- Computes salience Ψ = ∫ |A_field|² dx
- Commits when Ψ ≥ threshold (≈1.01)
- Perceptual record of "time" emerges here

Summary Flow
------------
Root Substrate → Tick Generator → Multi-Source Emissions → Artefact Field → Agent Salience → Perceptual Commits