### Experiment 80 Definition

#### Overview
This experiment implements a **virtual expansion of 2D space** while keeping a fixed rendering grid of **512×512**. The grid remains constant for performance and visualization, but world coordinates, imprint fields, and entity behavior evolve as if the underlying space were expanding. Any data mapped outside the fixed grid is discarded or optionally aggregated into a holographic horizon. The design supports a hybrid field model with a conserved residual field and a slowly growing core pattern.

---

#### Objectives
- Simulate virtual spatial expansion with a fixed 512×512 viewport.
- Maintain a **conservative residual field** that expands with the virtual metric and dilutes intensity according to dimensional scaling.
- Preserve an **informational core pattern** in comoving coordinates and allow it to grow at most one pixel per tick.
- Discard or aggregate any data that would fall outside the 512×512 grid.
- Provide deterministic, debuggable behavior and instrumentation for energy, residual loss, and pattern stability.

---

#### Core Principles
- **Fixed viewport** The internal buffer is always 512×512. All sampling, rendering, and storage use this fixed grid.
- **Comoving core** Entities and high‑frequency pattern cores are stored in reference coordinates. During render they are transformed by the current scale factor s(t). Core growth is explicitly limited to at most one pixel per tick.
- **Conservative residual** The low‑frequency residual field is remapped conservatively when scale changes. Intensity is normalized by 1/s^2 in 2D to preserve total energy before clipping.
- **Clipping policy** Any sample or remapped value that maps outside the 512×512 grid is discarded unless aggregation into a holographic horizon is enabled.
- **Hybrid pipeline** Combine comoving handling for core and conservative remap for residual to balance identity preservation and energy realism.

---

#### Coordinate Mapping and Transform Rules
- Define baseline physical range R0 that corresponds to the 512×512 grid at s = 1. Current physical range is R(t) = s(t) · R0.
- Map a physical coordinate x_phys to grid index i using linear normalization across the current physical range. Values with i or j outside [0, 511] are treated as out of bounds.
- Residual intensity remap in 2D uses the normalization
  \[
  I' = \frac{I}{s(t)^2}
  \]
  after resampling. Use bilinear or Lanczos resampling for quality.
- Core growth rule
  \[
  r(t+1) \le r(t) + 1
  \]
  where r is core radius in pixels. New core pixels that fall outside the 512×512 grid are discarded.
- If energy conservation is required, compute the sum of discarded intensity during remap and either accept it as loss or aggregate it into a holographic horizon layer.

---

#### Implementation Pipeline
1. State and storage
    - `field_core` and `field_residual` as 512×512 float arrays.
    - Entities stored in reference coordinates with attributes pos_ref, radius_ref, mode, emission.
    - Sliding window stores s(t), entity states, and low‑res snapshots or diffs.

2. Per tick sequence
    - Simulate entity motion in reference coordinates.
    - Bake core emission into `field_core` in reference coordinates.
    - Bake residual emission into `field_residual`.
    - If scale changes from s_old to s_new:
        - Remap `field_residual` into the fixed 512×512 grid corresponding to s_new using physical coordinate mapping and resampling. Normalize intensity by (s_new/s_old)^2 or by 1/s_new^2 relative to baseline. Values that map outside the target grid are discarded or aggregated to horizon.
        - Grow core by morphological dilation limited to one pixel per tick. Distribute growth energy according to a chosen kernel and optionally move a fraction into residual to conserve energy. Clip new core pixels outside the grid.
    - Apply decay to both fields.
    - Save snapshot metadata including s(t) into the sliding window.

3. Render pass
    - For each pixel, compute the physical coordinate for the current s(t). Sample `field_residual` directly from the remapped 512×512 residual. For core, invert the transform to sample core in reference coordinates or sample a pretransformed core buffer. Combine core and residual with configurable weights, apply tone mapping and gamma correction, and draw.

4. Horizon handling
    - Option A discard out‑of‑bounds contributions.
    - Option B aggregate discarded intensity into a small holographic horizon heatmap for visualization and diagnostics.

---

#### Pseudocode
```python
def remap_residual_to_fixed_grid(field_old, s_old, s_new, world_center):
    H, W = 512, 512
    field_new = np.zeros((H, W), dtype=np.float32)
    for j in range(H):
        for i in range(W):
            x_phys, y_phys = pixel_to_physical(i, j, s_new, world_center)
            u_src, v_src = physical_to_source_uv(x_phys, y_phys, s_old, world_center)
            if u_src < 0 or u_src > 1 or v_src < 0 or v_src > 1:
                continue  # out of source bounds -> contributes zero
            value = bilinear_sample(field_old, u_src, v_src)
            field_new[j, i] = value / (s_new / s_old)**2
    return field_new

def grow_core(core_mask, core_values, max_growth=1):
    dilated = morphological_dilate(core_mask, radius=max_growth)
    new_pixels = dilated & (~core_mask)
    added = distribute_growth_energy(core_values, new_pixels)
    core_values[new_pixels] += added
    core_values[core_mask] -= added.sum() * core_mask_fraction
    return dilated, core_values
```

---

#### Tests and Validation
- Energy conservation test Compare sum(field_core)+sum(field_residual) before and after remap. Record discarded energy and verify expected loss or horizon aggregation.
- Core growth test Verify core radius increases by at most one pixel per tick and that pixels outside 512×512 are discarded.
- Residual scaling test Confirm residual intensity scales approximately by 1/s^2 after remap.
- Residual delta visualization Render before/after remap difference to detect interpolation artifacts.
- Playback test Save s(t) and field snapshots in the sliding window and replay to ensure deterministic reproduction.

---

#### Tuning and Operational Notes
- Use 512×512 for interactive prototyping. For faster iteration use 256×256.
- Bilinear resampling is fast; use Lanczos for higher quality when needed.
- Apply remap in multiple smaller steps for large scale jumps to reduce aliasing.
- Expose knobs: decay_core, decay_residual, growth_rate, horizon_aggregation_mode.
- Log discarded energy per tick for theoretical analysis and to decide whether to accept loss or aggregate to horizon.

---

#### Deliverables
- A single runnable demo `main.py` implementing the pipeline above for 2D.
- Modules `gamma_field_core.py`, `gamma_field_residual.py`, `remap.py`, `core_growth.py`, and `sliding_window.py`.
- README describing controls, parameters, and how to toggle horizon aggregation.
- A short test script that runs the energy conservation and core growth tests and outputs diagnostic plots.
