# Experiment 64_109 — Three-Body Dynamics on Graph Substrate

## Closure Summary

**Duration:** February – March 2026 (24 versions)
**Status:** CLOSED — superseded by RAW 118 (Gravity as Consumption and Transformation)
**Core question:** Does gravity emerge from graph topology, and can orbital mechanics follow?
**Answer:** Gravity yes. Orbits no — and RAW 118 explains why.

---

## The Arc in One Paragraph

Started by showing gravity is topological (v1). Proved orbits need dimensionality (v2). Built up through lattice dynamics (v3–v9), macro-scale transition (v10–v12), connector physics (v13–v17), 3D embedding (v18–v20), and orbital refinement (v21–v24). Achieved attraction, curved trajectories, radial reversals, and dissipative capture — but never a closed orbit. The final version (v24) revealed anti-Newtonian force scaling from float gamma accumulation, pointing to a structural problem deeper than parameter tuning. RAW 118 identified the root cause: the simulation implements only the reading half of the single mechanism. Entities detect connector asymmetry but never consume deposits, transform connectors, or extend connectors through traversal. The missing outward pressure (traversal-driven extension) is why dense regions collapse and orbits cannot close.

---

## Version History

### Phase 1: Foundations (v1–v9)

| Version | What Changed | Key Result |
|---------|-------------|------------|
| v1 | Random graph (Watts-Strogatz, N=50K), deposit-spread-follow | Gravity emerges from topology. No orbits — entities collapse. |
| v2 | Structured 2D lattice | Orbits appear on lattice. Dimensionality is necessary. |
| v3–v5 | Velocity/mass relationship | Confirmed v = c/M (heavier = slower). Commit-counter model works. |
| v6–v9 | Continuous internal direction, self-subtraction | Three-body scattering observed. Topology sufficient for sub-atomic physics. |

**Phase 1 conclusion:** Gravity is topological — it emerges from connectivity alone. Orbits require local dimensionality (lattice or embedded graph, not pure random graph).

### Phase 2: Macro-Scale (v10–v12)

| Version | What Changed | Key Result |
|---------|-------------|------------|
| v10 | Single lattice node per body, aggregated mass M, gravitational time dilation via edge length | 433 stable revolutions. Square orbits (lattice artifact). Force exponent n~2.2 (not Newton's 2.0). |
| v11–v12 | k=26 lattice, variable speed, three-body testing | Multiple stable shells not achieved. Narrow capture basin at r~2. |

**Phase 2 conclusion:** Force is turning rate, not acceleration. Gravity = curved geodesics. Lattice anisotropy prevents correct force law. Single stable orbit at lattice minimum only.

### Phase 3: Connector Physics (v13–v17)

| Version | What Changed | Key Result |
|---------|-------------|------------|
| v13 | Entity-vortex model, edge rule depends on local mass/distance | Orbits emerge but chaotic. Tilt accumulation wrong (pi not 2pi). |
| v14 | **G=0 breakthrough.** Edge rule: `growth = H / (1 + alpha*(gamma_A + gamma_B))`. Free diffusion. | 69 radial reversals. Equal-mass binary bound 200K ticks. Three-body all bound 50K ticks. |
| v15 | Stripped to cascade drift only (no commit cycle, no frame rotation) | FAIL. Radial collapse. Cascade drift alone insufficient without directional memory. |
| v16 | RandomGeometricGraph (3D point cloud, k=12). Per-connector displacement. | 30-33 comoving reversals. External gamma fix (own gamma drowns signal). Expansion scale factor ~10 causes issues. |
| v17 | Refinement of v16 expansion issues | Intermediate. Setup for v18+. |

**Phase 3 conclusion:** G=0 with free diffusion naturally produces 1/r gamma profile. Cascade drift (growth rate asymmetry) binds even when profiles flatten. External gamma fix is critical — entity's own field drowns inter-body signals. But still no closed orbits.

### Phase 4: 3D Embedding (v18–v20)

| Version | What Changed | Key Result |
|---------|-------------|------------|
| v18 | Edge-weighted spread (longer edges = weaker diffusion) | Improved gradient stability. |
| v19 | No formation phase — continuous deposit. Drag=0.001. | 200+ reversals (chaotic bound). But drag kills real energy exchange. |
| v20 | Distributed bodies (body_radius parameter). Star: ~117 nodes. | Nearly identical to v19. Jitter from receiver's connectors, not sender's angular coverage. Force-every-tick causes velocity runaway. |

**Phase 4 conclusion:** Distributed deposit had minimal effect. Force applied every tick (even while stationary) pumps velocity unbounded. Need force-on-hop.

### Phase 5: Orbital Refinement (v21–v24)

| Version | What Changed | Key Result |
|---------|-------------|------------|
| v21 | **Force-on-hop** (force only on tick after hop). Restores commit cycle = gravitational time dilation. Removes drag. | Bounded velocity. Time dilation signature observed. |
| v22 | Star forms FIRST before planet. True 3D displacement accumulator. Hop threshold tracks expansion. | Best: particle survives 16K ticks, visible curvature, 28% velocity decline. Escape due to domain size. |
| v23 | Larger domain (30K→80K nodes, radius 30→45). 50K tick warmup. | **First radial reversal** (p8: r=8→21.1→17.1). p19 locked at r=25.9 for 27K ticks. But p19's equilibrium is dissipative capture, not orbit. |
| v24 | Heavier star test (M=100K vs M=1M). | **Anti-Newtonian scaling:** 10x heavier star → 15x weaker force. Float gamma self-suppression. Root cause: unbounded accumulation at single node. |

**Phase 5 conclusion:** Achieved attraction, curvature, radial reversal, and dissipative capture — but not a closed orbit. v24 exposed the float-gamma structural limitation. The point-mass model is architecturally wrong.

---

## Ten Key Discoveries

1. **Gravity is topological** — emerges from connectivity, not geometry (v1)
2. **Orbits need dimensionality** — angular momentum requires local geometric structure (v1–v2)
3. **Force is turning rate, not acceleration** — gravity curves the path at constant speed (v10)
4. **G=0 works best** — free diffusion produces natural 1/r profile (v14)
5. **Cascade drift is the binding mechanism** — instantaneous growth rate asymmetry attracts even when profiles flatten (v14)
6. **External gamma fix is critical** — own body's gamma drowns inter-body signal (v16)
7. **Force-on-hop solves velocity runaway** — force every tick pumps energy unbounded (v21)
8. **Dissipative capture is not orbital mechanics** — particles can be captured without oscillating (v23)
9. **Float gamma creates anti-Newtonian scaling** — unbounded accumulation at single node suppresses its own gradient (v24)
10. **Point mass is structurally wrong** — mass must be distributed across many nodes with proportional consumption capacity (v24 → RAW 118)

---

## Why It Could Not Succeed

RAW 118 identifies the structural reason: the simulation implements only the **reading half** of the single mechanism from RAW 112.

**What was implemented (all 24 versions):**
```
Entity reads connector growth asymmetry → routes toward lowest growth → hops
```

**What was missing:**
```
Entity CONSUMES deposits from traversed connector (Different → Same)
Entity DEPOSITS own pattern onto connector (now Different to others)
Connector EXTENDS through deposit (traversal-driven expansion)
```

Without traversal-driven extension, there is no outward pressure to balance consumption routing. Dense regions collapse because nothing opposes the inward routing. Global H (the only expansion mechanism) is suppressed in dense regions — the **opposite** of what physics requires (dense regions should experience the most traversal traffic and therefore the most extension).

This is not a parameter problem. It is implementing half an equation.

---

## What Transfers to Experiment 118

**Validated and reusable:**
- RandomGeometricGraph substrate (v16+)
- Deposit-spread-follow architecture
- External gamma fix (entity ignores own field)
- Force-on-hop mechanism (force only after hop, not every tick)
- True 3D displacement accumulator (v22+)
- Dynamic hop threshold tracking expansion (v22+)
- Star-forms-first protocol with phased initialization (v22+)
- Distributed body framework (body_radius parameter, v20+)

**Superseded by RAW 118:**
- Passive field reading → replaced by consumption-transformation
- Global H expansion → replaced by traversal-driven connector extension
- Point mass with mass label → replaced by distributed pattern (mass = receptor count)
- Float gamma field → must move to integer/binary deposits

**RAW 118's two proposed experiments:**
1. Equilibrium distance from single mechanism (H=0, two entities, consume-transform-extend)
2. Distributed star with orbiting test particle (~500-node self-assembled star)

---

## Final Metrics

| Metric | Best Achieved | Target |
|--------|--------------|--------|
| Radial reversals | 69 (v14), 200+ chaotic (v19) | Periodic |
| Sustained bound state | 27K ticks at fixed r (v23 p19) | 10K+ ticks with oscillation |
| Closed orbits | 0 (never achieved on graph) | 1+ full orbit |
| Correct force scaling | Anti-Newtonian at high M (v24) | Newtonian (F ~ M/r^2) |
| Energy conservation | Not measured (no clean orbit) | Within 5% |

---

## Status

**CLOSED.** The experiment achieved its exploratory purpose: mapping the boundary between what passive-reading gravity can and cannot do on a graph substrate. The structural limitation identified (missing consumption-transformation half) is not fixable within this experiment's architecture. RAW 118 defines the correct architecture. Experiment 118 will implement it.

*Experiment 64_109: February – March 2026, 24 versions, closed March 21, 2026.*
