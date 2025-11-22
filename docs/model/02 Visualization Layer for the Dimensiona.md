# Visualization Layer for the Dimensional Substrate

## 🎯 Goals
- **Clarity:** Show occupied cells, motion, births/decays, and horizons without clutter.  
- **Dimensional honesty:** Preserve locality and one-cell-per-tick rule.  
- **Auditability:** Every frame traceable to simulation state.  
- **Scalability:** Handle growing grids and long runs smoothly.

---

## 🖼️ Visual Mapping

- **Cells (mass = 1):**  
  - Glyph: voxels or point sprites  
  - Color: occupancy age or state (alive/decaying)  
  - Size: constant

- **Motion and velocity:**  
  - Arrows: displacement vectors (≤1 cell/tick)  
  - Trails: faded polylines over K ticks

- **Births/decays:**  
  - Birth glow: halo on new cells  
  - Decay fade: alpha drop before removal

- **Tick pressure (density field):**  
  - Volume: semi-transparent fog with colormap  
  - Isosurfaces: contours for thresholds

- **Horizon boundary (LHB):**  
  - Shell: semi-transparent surface at saturation  
  - Distortion: subtle lensing inside horizon

- **Anomalies:**  
  - Badges: SAT_CAP, FLATLINE, TIMEOUT pinned to regions

---

## 🎥 3D Renderer Design

- **Scene composition:**  
  - Primary: instanced voxels for occupied cells  
  - Aux: volume ray-march or slice stack for tick pressure  
  - Overlay: arrows, trails, anomaly badges

- **Camera modes:**  
  - Orbit (global)  
  - Follow (lock onto cluster)  
  - Free-fly

- **Color science:**  
  - Pressure: perceptually uniform colormap (viridis/magma)  
  - States: distinct hues for birth/survival/decay

- **Performance:**  
  - GPU instancing for cells  
  - LOD downsampling for distant voxels  
  - Chunk culling for empty volumes  
  - Async streaming of deltas

---

## 🌌 Higher-Dimensional Strategies (4D/5D)

- **Orthogonal slicing:**  
  - Interactive hyperplane slices (fix w or v axis)  
  - Composite slice grids for cross-dimensional dynamics

- **Projection/embedding:**  
  - Map extra axes to color or glyph deformation  
  - Optionally map one axis into short time trails

- **Linked views:**  
  - 3D anchor + slice panel  
  - Focus linking across slices

---

## 🕹️ Interaction and UX

- **Tick controls:** Play/Pause/Step, speed slider, jump to tick N  
- **Seed/rule exploration:** Seed browser (line, plane, cube, shell, glider), rule toggles  
- **Metrics panel:** Live stats (mass, births/deaths, displacement, densities), SPBI suite, conservation check  
- **Annotations/export:** Frame notes, snapshots/video, CSV deltas, JSON scene state

---

## 🛠️ Implementation Roadmap

- **Phase 1 — Minimal visuals:**  
  - Occupied cells (voxels/points)  
  - Motion vectors (arrows)  
  - HUD: tick counter, totals, births/deaths

- **Phase 2 — Field/horizon:**  
  - Pressure volume slices  
  - Isosurfaces for thresholds  
  - LHB shell + anomaly badges

- **Phase 3 — Dimensional tooling:**  
  - Interactive hyperplane navigation (4D/5D)  
  - Linked anchor + slice grids

- **Phase 4 — Audit/export:**  
  - Delta streaming (frame-to-frame changes)  
  - Deterministic replay  
  - Export videos and metric logs  
  - Performance tuning (LOD, chunk culling, instancing)

---