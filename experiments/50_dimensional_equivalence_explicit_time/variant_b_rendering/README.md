# Variant B: Time as Rendering Dimension

## Implementation

Time remains an evolution parameter in physics but becomes explicit in storage using sliding window:

```python
# Physics: standard spatial Laplacian
∇²A = ∂²A/∂x² + ∂²A/∂y² + ∂²A/∂z²

# Storage: sliding window buffer
buffer[lag][time_offset] = field_state

# Metrics computed across time slices
```

## Theoretical Implication

This tests whether **temporal addressability** (ability to access past states) affects dimensional behavior without changing the underlying physics.

## Key Differences from Original

- **Physics**: Unchanged (spatial Laplacian only)
- **Storage**: Ring buffer with temporal indexing (from Experiment #49)
- **Metrics**: Computed across time window, not single snapshot
- **Visualization**: Temporal effects enabled (trails, motion blur)

## Expected Behavior

If explicit storage matters:
- Metrics may differ from pure spatial (n+1)D
- Window size affects results
- Temporal correlation emerges

If storage is neutral:
- Results match original nD (not n+1D)
- Window size doesn't affect stability
- Time remains just a parameter
