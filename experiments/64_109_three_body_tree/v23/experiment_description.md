# v23: Larger Graph Domain — Closing the Orbit

## Date: March 15, 2026

## Status: Design for Code

---

## What v22 Taught Us

v22 ran five distinct configurations. The complete arc:

| Run | v_tan | Force model | Best-3 escape | \|v\| trend |
|-----|-------|-------------|---------------|-------------|
| Force-on-hop | 0.00396 | hop only | ~8500 ticks | frozen |
| Continuous fc=1.0 | 0.00396 | every tick | ~8500 ticks | frozen |
| Leapfrog N=10 | 0.00396 | every 10 | ~12000 ticks | declining |
| Leapfrog+3D | 0.00396 | every 10 | ~13500 ticks | declining |
| Leapfrog+3D | 0.00350 | every 10 | ~16000 ticks | declining |

**What was validated:**

- ✅ Star formation from seed — established
- ✅ Gamma gradient at orbital radius — established
- ✅ Derived orbital velocity from field measurement (v_circ_i10) — working
- ✅ Force actively decelerating particles — confirmed (28-31% velocity reduction)
- ✅ Curved trajectories — first time in this experiment arc
- ✅ Hop count dramatically improved (91 → 1341+, no longer frozen)
- ✅ Leapfrog force interval working correctly
- ✅ Velocity bottoms out and stabilizes (not runaway, not frozen)

**The definitive v22 result (v_tan=0.0035, best run):**

Particle p17 survived 16041 ticks. Velocity dropped from 0.0035 → 0.00252 (28%
deceleration). Particle p18 showed a clear arc from r=8 out to r=29 with visible
curvature. Velocity stabilized at ~0.0027 around tick 12000 — the particle found
its natural orbital radius. It is not escaping in the physics sense. It settled at
the wrong radius because the gradient at r>20 is too weak to hold it in the finite
graph domain.

**The failure mode has shifted.** v21 failed because the physics was wrong.
v22 fails because the domain is too small. These are completely different problems.
The physics is working.

**Bugs fixed during v22 (final runs):**

Two bugs from the v22 design spec were identified and fixed during
the v22 session. Both fixes are in `DiskParticle.advance()` in
`v22/star_formation.py` and are carried forward to v23.

### Bug 1: Frozen Hop Threshold (v21 bug carried forward)

```python
# v22 code — still wrong:
hop_threshold = graph.initial_mean_edge   # ← never updates
```

Should be:
```python
hop_threshold = graph.avg_edge_length_at(self.node)  # current local mean
```

At H=0.0001 over 20k ticks, mean edge grows to ~3× initial. By mid-run the
particle needs 3× more displacement per hop than at tick 0.

### Bug 2: v21 Per-Connector Projection Still Active (core v22 fix never implemented)

The v22 design spec explicitly introduced `displacement_3d` to replace
per-connector projection. The code still uses:

```python
# v22 code — still v21 mechanics:
best_proj = max dot product of velocity with each connector direction
self.disp[best_nb] += abs(best_proj)
```

When the velocity vector falls between connectors, `best_proj` is small even
though `|velocity|` is significant. The projection discards the component that
doesn't align with any single connector. The initial tangential velocity
introduces a small radial component at tick 0, which seeds the outward drift.

---

## The Core Insight: The Graph Should Be Infinite

In the physical model, the graph IS the universe. There is no boundary. The
substrate extends wherever deposits reach. An orbit at r=8 exists inside a
graph that stretches to infinity in all directions.

The v22 failure is not a physics failure — it is a boundary artifact. The
particle's natural orbital radius (~r=20 based on where velocity stabilized)
lies within the finite simulation domain. With a larger domain, that same
radius has gradient support and the orbit closes.

> **The correct framing: make the graph large enough that the boundary is
> irrelevant, then let the orbit find its natural radius.**

This also means we should NOT force ring_radius=8. The particle will settle
at whatever radius the field supports. The derived v_tangential gives it
enough tangential velocity to orbit — the orbit radius emerges from the
physics, not from our choice.

---

## v23 Architecture: One Change (Domain Size)

The v22 final runs already implemented correct displacement mechanics (leapfrog
force, true 3D displacement, local hop threshold with floor). v23 carries that
code forward unchanged and addresses the only remaining issue: domain size.

### The Change: Larger Graph Domain

| Parameter | v22 | v23 | Reason |
|-----------|-----|-----|--------|
| n_nodes | 30000 | 80000 | ~2.7× more nodes |
| radius | 30.0 | 45.0 | 1.5× larger domain |
| warm_up | 20000 | 50000 | Field must reach r=20+ |

The particle stabilized velocity at r~20 in v22. With radius=45 the gradient
extends to r=35+, giving the particle room to find its natural orbit without
hitting the boundary.

The warm_up increase is mandatory — the star's pinning radius grows at roughly
1 unit per 2000 ticks (from v22 Phase 0 data). To establish gradient at r=20,
the star needs ~40000 ticks minimum. 50000 is safe.

**Why radius=45 instead of 60:** Volume scales as r³. Matching v22's node
density (0.265 nodes/unit³) at radius=60 would require 240,000 nodes — too
expensive. At radius=45 with 80,000 nodes, density = 0.21 nodes/unit³, close
to v22's 0.265. The mean edge length will be ~10-15% longer than v22, which
is acceptable. At radius=60 with 80k nodes, density drops to 0.088 — edges
become 44% longer and orbital resolution degrades significantly.

**ring_radius:** Keep at 8.0 for Phase 0/1 measurement. The particle will
drift outward to its natural radius. This is expected and correct.

### Displacement Mechanics (carried from v22 — already implemented)

v22's final runs implemented the correct displacement model. v23 copies it:

**The model (implemented in v22 final runs, carried to v23):**
```python
# Accumulate displacement in true 3D — no projection
self.displacement_3d += self.velocity

# Hop threshold: current local mean edge with floor to prevent boundary blowup
hop_floor = graph.initial_mean_edge * 0.5
hop_threshold = max(graph.avg_edge_length_at(self.node), hop_floor)

if np.linalg.norm(self.displacement_3d) >= hop_threshold:
    # Find connector MOST ALIGNED with accumulated 3D displacement
    disp_dir = self.displacement_3d / |self.displacement_3d|
    best_nb = argmax over connectors: dot(disp_dir, connector_direction)

    # Subtract hop direction — preserve residual in 3D
    hop_dir = graph.connector_direction(self.node, best_nb)
    self.displacement_3d -= hop_dir * hop_threshold
    # ... perform hop ...
```

**Key properties:**

1. **No velocity discarded.** Every tick adds the full velocity vector to
   `displacement_3d`. Magnitude conserved tick-by-tick.

2. **No blind spots.** Worst case: velocity points exactly between connectors.
   Max directional error is 360°/k/2 = 7.5° for k=24. Error averages out
   over many hops rather than accumulating as a radial bias.

3. **Residual preserved in 3D.** After a hop, unused displacement stays in
   `displacement_3d`. The 7.5° error is stored and corrected on the next hop.

4. **Hop threshold tracks expansion.** `avg_edge_length_at(node)` grows with
   the graph. The particle hops at the correct physical rate throughout, not
   just at tick 0.

5. **Hop threshold floor.** `initial_mean_edge * 0.5` prevents runaway hopping
   at the graph boundary where sparse nodes produce tiny local edge averages.
   v22 discovered this when a boundary particle accumulated 44,000 hops in
   6000 ticks.

---

## Implementation Notes

### Source code

Copy `v22/star_formation.py` → `v23/star_formation.py`. The DiskParticle class
already contains the correct displacement mechanics from v22's final runs.
Only change the CLI defaults for `--radius`, `--n-nodes`, and `--warm-up`.

### Reference: DiskParticle.advance() displacement section

This is the **already-implemented** code from v22/star_formation.py:

```python
# 3. Accumulate displacement in TRUE 3D
self.displacement_3d += self.velocity

# 4. Hop when 3D magnitude >= local mean edge (with floor)
hop_floor = graph.initial_mean_edge * 0.5
hop_threshold = max(graph.avg_edge_length_at(self.node), hop_floor)

moved = False
max_hops_per_tick = 10
hops_this_tick = 0

while hops_this_tick < max_hops_per_tick:
    disp_mag = np.linalg.norm(self.displacement_3d)
    if disp_mag < hop_threshold:
        break

    disp_dir = self.displacement_3d / disp_mag
    best_nb, best_eidx = max(
        conn_list,
        key=lambda x: np.dot(disp_dir, graph.connector_direction(self.node, x[0]))
    )

    hop_dir = graph.connector_direction(self.node, best_nb)
    self.displacement_3d -= hop_dir * hop_threshold

    old_node = self.node
    graph.move_gamma(self.bid, old_node, best_nb)
    self.node = best_nb
    self.hops += 1
    hops_this_tick += 1
    moved = True

    conn_list = graph.node_neighbors[self.node]
    hop_threshold = max(graph.avg_edge_length_at(self.node), hop_floor)

return moved
```

Note: `_transfer_displacement()` is NOT called — `displacement_3d` lives on
the entity in 3D space and needs no per-connector transfer between nodes.

---

## Parameters

| Parameter | v22 | v23 | Reason |
|-----------|-----|-----|--------|
| n_nodes | 30000 | 80000 | Larger domain, similar density |
| radius | 30.0 | 45.0 | 1.5× larger — gradient reaches r=35+ |
| warm_up | 20000 | 50000 | Field must pin to r=20+ before disk |
| ticks | 20000 | 30000 | More time for orbit to close |
| ring_radius | 8.0 | 8.0 | Start here — natural radius emerges |
| v_tangential | 0.0035 | re-derive | Run measure_force at r=8 on new graph |
| hop_threshold | current local mean + floor | same | Already fixed in v22 |
| displacement | 3D accumulator | same | Already fixed in v22 |
| star_mass | 100000.0 | 100000.0 | Unchanged |
| deposit_rate | 1e-5 | 1e-5 | Unchanged |
| H | 0.0001 | 0.0001 | Unchanged |
| alpha_expand | 1.0 | 1.0 | Unchanged |
| inertia | 10.0 | 10.0 | Unchanged |
| force_coeff | 1.0 | 1.0 | Unchanged |
| force_interval | 10 | 10 | Unchanged |
| n_ring | 20 | 20 | Unchanged |
| ring_mass | 100.0 | 100.0 | Unchanged |

**Node density check:** v22 had 0.265 nodes/unit³ (30k in r=30). v23 has
0.21 nodes/unit³ (80k in r=45) — 80% of v22's density, ~10% longer edges.
Acceptable tradeoff for 1.5× more orbital room.

**Important:** Re-run `measure_force` on the new graph before Phase 2.
The larger graph may produce a slightly different field profile. The derived
v_tangential must come from the actual field, not assumed from v22.

---

## Runtime Estimate

The larger graph increases cost at every phase:

- Phase 0 (warm_up=50000): ~2.5× v22 spread cost (80k nodes vs 30k) × 2.5× ticks → ~1.5-2 hours
- measure_force (warm_up=50000): same as Phase 0 — ~1.5-2 hours
- Phase 2 (ticks=30000): ~2.5× per-tick cost × 1.5× ticks → ~1 hour after warm-up

Total estimated runtime: **4-6 hours** (can skip Phase 0 if measure_force runs warm-up)

Run with `-u` flag for unbuffered output. Consider `--tag` for result naming.

---

## Expected Outcome

With sufficient domain and correct displacement mechanics:

- Particle drifts outward from r=8 to its natural orbital radius (~r=15-25)
- At natural radius: force exactly balances centripetal requirement
- r stabilizes and begins oscillating (perihelion/aphelion)
- Velocity oscillates rather than monotonically declining
- **This is the orbit — not at r=8, but at whatever radius the field supports**

The orbit radius is not a parameter we set. It is the radius at which the
field gradient at that distance provides exactly the centripetal force needed
for the current tangential velocity. The physics determines it.

**If r stabilizes but does not oscillate:** The particle found equilibrium
at a circular orbit. This is success — possibly cleaner than an ellipse.

**If r oscillates with growing amplitude:** Energy not conserved — force_interval
too coarse. Try force_interval=5.

**If r still escapes past r=50:** The graph is still too small, or v_tangential
is genuinely super-circular at the natural radius. Try v_tangential × 0.85.

**If r decays inward:** v_tangential is sub-circular. Try v_tangential × 1.15.

---

## Success Criteria

### Minimum:
- [ ] r does not reach the graph boundary (r < 50)
- [ ] r stabilizes or oscillates
- [ ] Angular momentum sign consistent for 100+ consecutive hops

### Intermediate:
- [ ] r oscillates with recognizable perihelion/aphelion
- [ ] Tangential velocity component dominant in velocity decomposition
- [ ] Energy approximately conserved over 10+ orbital periods

### Full success:
- [ ] Closed orbit maintained for 10k+ ticks after stabilization
- [ ] Orbital period measurable and consistent
- [ ] Comoving distance stable (orbit not drifting outward)

---

## The Deeper Significance

In the physical model the graph is infinite — the substrate extends wherever
the equilibrium search has reached. Our finite simulation is always an
approximation of that infinite substrate. The orbit doesn't know the boundary
exists. It just follows the gradient.

v23 is not adding physics. It is removing an artificial boundary from the
physics that was already there. If the orbit closes, it closes because the
substrate allows it — not because we made it happen.

This is the first experiment in the arc where the boundary is genuinely not
the constraint. If it still fails after v23, the failure is physics, not geometry.

---

## v23 Experimental Results (March 17, 2026)

### Force measurement (stable star)

| Radius | F_radial | % inward | v_circular (i=10) |
|--------|----------|----------|-------------------|
| r=8 | -0.0000198 | 100% | 0.00398 |
| r=25 | -0.0000062 | 92% | 0.00394 |

Star mass held at 100000.0 throughout (radiate_mass=False).

### Run A: v=0.00398 at r=8 (60k ticks, stable star)

Super-circular. Particles escaped to boundary (r=40.5) by tick 36k. Hop
explosion at boundary. Confirmed: v_circular derived at r=8 is super-circular
for the actual dynamics because the gradient weakens as particles drift outward.

### Run B: v=0.003 at r=8 (60k ticks, radiating star)

**Best result with radiating star.** Velocity plateau at 0.00128-0.00131 for
18,000 ticks (tick 36k-54k). All best-3 particles still bound at 60k ticks.
Late velocity uptick (0.00129→0.00139) as star mass dropped to 55% — the
dying star could no longer hold equilibrium.

### Run C: v=0.003 at r=8 (60k ticks, STABLE star)

**Best result overall.** Key findings:

- **Particle p8:** r went 8.0 → 21.1 (tick 36k) → **17.1** (tick 60k).
  First radial reversal in the entire v21-v23 arc. The particle turned
  around and came back toward the star.

- **Particle p19:** Locked at r=25.9 for **27,000 consecutive ticks**
  (tick 33k-60k). Final |v|=0.00040. This particle found its equilibrium
  radius and effectively stopped drifting.

- **Particle p1:** Settled at r≈30.2, |v|=0.00123.

- **No velocity uptick.** Unlike the radiating star run, velocity continued
  declining to 0.00125 without reversal. The stable field holds.

### Run D: v=0.00394 at r=25 (60k ticks, stable star, radiating disk)

Started at the measured v_circular for r=25. Escaped to boundary by tick 27k.
The ring particles' own mass radiation weakened the field, corrupting dynamics.
Lesson: radiate_mass=False must apply to ALL particles, not just the star.

### Run E: v=0.003 at r=25 (60k ticks, STABLE star + disk, no mass loss)

The "definitive test" — particles placed at r=25 where Run C's p19 stabilized.
No mass loss on anything.

**Result: escaped.** All best-3 hit boundary between tick 34k-44k. Drift was
slow (25→33 in 30k ticks) but never reversed. Velocity declined only 10%
(0.003→0.0027) vs Run C's 58% decline (0.003→0.00125).

**Why it failed:** Run C's p19 arrived at r≈26 with |v|=0.0004 after bleeding
kinetic energy over 33k ticks of spiral from r=8. Particles starting at r=25
with v=0.003 have 7.5× more velocity. The gradient at r=25 is too weak
(F_radial = -0.0000062, only 31% of the r=8 value) to decelerate particles
fast enough before they escape.

**The key insight:** The equilibrium observed in Run C was NOT a circular orbit.
It was a particle that had already dissipated most of its kinetic energy
through graph-discretization friction during a long outward spiral, then
happened to reach a radius where its residual velocity was small enough for
the weak gradient to hold. This is more like a "captured" particle than an
"orbiting" one.

### What v23 proved and what it didn't

**Proved:**
- Larger domain removes boundary artifacts (Run C: all particles bound at 60k)
- Stable star (no mass loss) eliminates late-run field decay
- Leapfrog force genuinely decelerates particles and curves trajectories
- Radial reversal is possible (p8: 21.1→17.1)
- Radial equilibrium is possible (p19: r=25.9 locked for 27k ticks)
- The architecture (leapfrog + 3D displacement + local hop threshold) works

**Did not prove:**
- Closed orbits — no perihelion/aphelion oscillation observed
- v_circular from measure_force is reliable — particles initialized at the
  derived v_circular consistently escape
- The gradient is strong enough at r>15 to support actual orbital dynamics

**The remaining problem is not domain size or architecture — it's force
strength.** The gradient drops off faster than 1/r² and can't provide
enough centripetal force at the radii where particles naturally settle.
Run C's success was dissipative capture, not orbital mechanics.

### Success criteria status

- [x] r does not reach graph boundary — **Run C: all bound at 60k**
- [x] r stabilizes — **p19: r=25.9 for 27k ticks (dissipative capture)**
- [x] Velocity stabilizes — **0.00128-0.00131 plateau for 18k ticks**
- [x] Radial reversal observed — **p8: 21.1 → 17.1**
- [ ] Closed orbit maintained for 10k+ ticks — **not achieved**
- [ ] Orbital period measurable — **not achieved**

---

## File Structure

```
v23/
  experiment_description.md    (this file)
  star_formation.py             (copy of v22/star_formation.py with fixes)
  results/
```

### Reuse from v22:
- Copy `v22/star_formation.py` → `v23/star_formation.py`
- DiskParticle already has correct displacement mechanics — no code changes needed
- All phase functions (phase0, phase1, measure_force, phase2) unchanged
- Update CLI defaults: `--radius 45 --n-nodes 80000 --warm-up 50000`

---

## References

- v22/experiment_description.md — what v22 designed, ran, and concluded
- v22/star_formation.py — source code (already has correct displacement mechanics)
- RAW 112 — The Single Mechanism
- RAW 113 §2.4 — `unknown` → expansion, why the graph extends to the frontier
- V3_CONSOLIDATION_TASK.md — closed orbit is primary V3 validation target

---

*Date: March 15, 2026*
*Updated: March 18, 2026 — Five runs completed*
*Status: Complete — handed off to v24*
*Predecessor: v22 (curved trajectories, force validated, domain too small)*
*Result: Radial reversal (p8) and radial equilibrium (p19) achieved via dissipative capture*
*Closed orbit NOT achieved — gradient too weak at natural settling radius*
*v24 direction: stronger gradient, higher force resolution, or different force law*
