# Variant A: Time as Physical Dimension

## Implementation

Time is included as a true coordinate dimension in the wave equation:

```python
# Grid shape includes time dimension
grid_shape = (*spatial_dims, time_window_size)

# Laplacian computed over ALL dimensions including time
∇²A = ∂²A/∂x² + ∂²A/∂y² + ∂²A/∂z² + ∂²A/∂t²
```

## Theoretical Implication

This treats time **identically** to spatial dimensions at the physics level. If dimensional equivalence holds:
- 2D space + 1D time should behave like 3D space
- Wave propagation occurs in spacetime, not just space

## Key Differences from Original

- **Laplacian**: Extended to include temporal axis
- **Boundary conditions**: Circular in time (periodic) vs spatial (zero/periodic)
- **Source injection**: Across all time slices simultaneously

## Expected Behavior

If time = dimension:
- Stability metrics match (n+1)D
- Same CV, ρ, gradient values
- Temporal and spatial propagations are indistinguishable
