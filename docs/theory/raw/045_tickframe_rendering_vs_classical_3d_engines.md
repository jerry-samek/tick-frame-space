# Tick‑Frame Rendering vs. Classical 3D Engines

*(Summary and comparison with common frameworks such as Unreal/Unity)*

## 🧭 Introduction

The tick‑frame model interprets the “3D world” as **2D space + temporal lag**.  
Depth (the z‑axis) is not a geometric dimension but a **temporal distance** from the present.

This leads to a surprising result:

> **The rendering pipeline becomes simpler while being more physically accurate than classical 3D.**

---

## 🧩 Core Principles of the Tick‑Frame Model

- An entity exists in `[x, y]` and has a **temporal_lag** (how many ticks behind the present it is).
- Depth = temporal lag.
- Perspective = compression of temporal history.
- Rotation around Z = standard 2D rotation.
- Rotation around X/Y = manipulation of temporal lag gradients.
- 3D objects are not real objects → they are **emergent temporal patterns**.

---

# 1. Geometry

## Tick‑Frame

- No 3D meshes.
- No vertex buffers.
- No normals, UVs, tangents.
- An “object” is a pattern of motion over time.

## Classical 3D (Unreal/Unity)

- Mesh data (vertex/index buffers).
- Normals, tangents, UV maps.
- LOD systems.
- Streaming large models.

### Result

Tick‑frame eliminates most data structures that make up 70–80% of modern render pipelines.

---

# 2. Depth (Z‑buffer)

## Tick‑Frame

- Z = temporal lag.
- Older entities → appear farther away.
- Newer entities → appear closer.
- No Z‑fighting.
- No depth precision issues.

## Classical 3D

- Z‑buffer.
- Hierarchical Z.
- Depth prepass.
- Precision artifacts.
- Z‑flickering.

### Result

Tick‑frame requires no Z‑buffer or its complex optimizations.

---

# 3. Perspective

## Tick‑Frame

- Perspective = how quickly older ticks are compressed.
- FOV = rate of temporal compression.
- Near/far plane = size of the history buffer.

## Classical 3D

- Projection matrices.
- Near/far clipping.
- Singularities at extreme FOV values.

### Result

Perspective is a natural property of the system, not a mathematical projection.

---

# 4. Rotation

## Tick‑Frame

- Z‑rotation = pure 2D rotation.
- X/Y rotation = temporal lag gradient manipulation.
- Forward tilt = impossible (cannot reduce lag below 0).
- Backward tilt = possible (lag can increase).

## Classical 3D

- Rotation matrices.
- Quaternions.
- Gimbal lock.
- Floating‑point drift.

### Result

Rotation becomes a physical phenomenon, not a numerical transformation.

---

# 5. Lighting

## Tick‑Frame

*(theoretical model)*

- Light = interaction between entities with different temporal lags.
- Shadow = region without access to younger ticks.
- Reflection = transfer of temporal information.

## Classical 3D

- Shadow maps.
- Cascaded shadows.
- Ray tracing.
- GI approximations.

### Result

Lighting can emerge naturally from temporal interactions.

---

# 6. Animation

## Tick‑Frame

- Animation = change in movement rules.
- No skeletons.
- No keyframes.
- No blendshapes.

## Classical 3D

- Skeletal animation.
- Skinning.
- IK/FK systems.
- Blendshapes.

### Result

Animation emerges from temporal motion rather than being explicitly authored.

---

# 7. Performance & Parallelization

## Tick‑Frame

- Each entity is independent.
- Perfect for GPU compute.
- No global structures.
- No culling systems.

## Classical 3D

- Transforming millions of vertices.
- Frustum and occlusion culling.
- LOD management.
- Physics + collision systems.

### Result

Tick‑frame scales better and is massively parallelizable.

---

# 8. Physical Accuracy

## Tick‑Frame

- Has a maximum velocity (1 tick per tick).
- Has asymmetry between past and future.
- Has energy‑movement coupling.
- Has emergent objects.
- Has temporal horizons.

## Classical 3D

- Time is just an animation parameter.
- Physics is approximate.
- Depth is geometric, not temporal.

### Result

Tick‑frame aligns more closely with real physical constraints.

---

# 📊 Summary Table

| Area        | Tick‑Frame            | Unreal/Unity         |
|-------------|-----------------------|----------------------|
| Geometry    | 2D + time             | 3D meshes            |
| Depth       | temporal lag          | Z‑buffer             |
| Perspective | history compression   | projection matrix    |
| Rotation    | physical asymmetry    | matrices/quaternions |
| Animation   | temporal surfing      | skeletons, keyframes |
| Lighting    | temporal interactions | shadowmaps, RT       |
| Performance | highly parallel       | complex pipeline     |
| Artefacts   | no Z‑fighting         | common issues        |
| Ontology    | 3D is emergent        | 3D is primary        |

---

# 🧠 Conclusion

The tick‑frame model:

- **simplifies the rendering pipeline**, because it removes most 3D‑specific systems
- **is more physically accurate**, because it treats time as the primary dimension
- **still produces a convincing 3D illusion**, emerging naturally from temporal gradients

It represents a fundamentally different way of thinking about graphics — and a more elegant one.
