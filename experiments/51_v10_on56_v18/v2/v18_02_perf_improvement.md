# V18.1 Performance Improvement: Wake-Driven Incremental Spreading

**Date**: 2026-02-11  
**Applies to**: V18.1 canvas spreading mechanism  
**Core insight**: Past decisions are immutable. Only new paint needs to propagate.

---

## The Problem

The naive `spread_gamma()` iterates ALL painted cells every tick:

```python
for pos, gamma_here in canvas.gamma.items():  # ALL cells, every tick
    for neighbor in 6_neighbors:
# compute transfer...
```

After 500 ticks with 100 processes, there are ~50,000+ painted cells. Each checked against 6 neighbors = 300,000
operations per tick. After 5000 ticks: millions of cells, millions of operations, most doing nothing because the field
settled long ago.

**The field is 99% frozen. We're recomputing 100% of it.**

---

## The Insight

The decision tree is immutable. A cell that reached equilibrium with its neighbors at tick 200 is still in equilibrium
at tick 5000. The only cells that need spreading are cells that CHANGED — cells where new paint arrived or where a
neighbor's spreading just reached them.

The wake field (`∂γ/∂t`) already tracks exactly this. If `wake[pos] == 0`, that cell is settled. If `wake[pos] != 0`,
that cell just changed and needs to spread.

**Wake is not just physics. Wake is the computational work list.**

---

## Implementation

### Replace `spread_gamma()` with `spread_gamma_incremental()`

```python
def spread_gamma_incremental(self):
    """Pressure equalization — only from cells that changed.
    
    Uses wake field as work list. Cells with zero wake are 
    in equilibrium and cost nothing. Only active wavefronts
    and freshly painted cells do work.
    
    Properties preserved:
    - Total gamma conserved (transfers only)
    - Synchronous update (compute all, apply all)
    - spread_fraction = 1/6 (geometry, not parameter)
    - Identical results to full spreading (just faster)
    """
    SPREAD_FRACTION = 1.0 / len(self.NEIGHBOR_OFFSETS)  # 1/6

    # Collect cells that need work:
    # 1. Cells with nonzero wake (changed last tick)
    # 2. Neighbors of wake cells (they might now be unequal)
    work_set = set()

    for pos in self.wake:
        if abs(self.wake[pos]) < 1e-10:
            continue
        work_set.add(pos)
        # Also check neighbors — they now border a changed cell
        for offset in self.NEIGHBOR_OFFSETS:
            neighbor = (
                pos[0] + offset[0],
                pos[1] + offset[1],
                pos[2] + offset[2],
            )
            if self.gamma.get(neighbor, 0.0) > 0:
                work_set.add(neighbor)

    # Compute transfers only from work set
    transfers = {}

    for pos in work_set:
        gamma_here = self.gamma.get(pos, 0.0)
        if gamma_here <= 0:
            continue
        for offset in self.NEIGHBOR_OFFSETS:
            neighbor = (
                pos[0] + offset[0],
                pos[1] + offset[1],
                pos[2] + offset[2],
            )
            gamma_there = self.gamma.get(neighbor, 0.0)
            if gamma_here > gamma_there:
                transfer = (gamma_here - gamma_there) * SPREAD_FRACTION
                transfers[pos] = transfers.get(pos, 0.0) - transfer
                transfers[neighbor] = transfers.get(neighbor, 0.0) + transfer

    # Apply transfers synchronously
    new_wake = {}
    for pos, delta in transfers.items():
        if abs(delta) > 1e-10:
            new_val = self.gamma.get(pos, 0.0) + delta
            if new_val > 1e-10:
                self.gamma[pos] = new_val
            elif pos in self.gamma:
                del self.gamma[pos]
            new_wake[pos] = delta
            self._update_bounds(pos)

    # Wake = ONLY what changed this tick
    self.wake = new_wake
```

### Key detail: work set includes neighbors of changed cells

If cell A changed, its neighbor B might now have a different pressure differential with A than before. So B needs
rechecking even if B itself didn't change. The work set is: `changed_cells ∪ neighbors_of_changed_cells`.

This is still much smaller than all cells. The wavefront is a shell, not a volume.

---

## Performance Analysis

### Scaling comparison

| Phase                         | Full spreading            | Incremental                             | Ratio                         |
|-------------------------------|---------------------------|-----------------------------------------|-------------------------------|
| Formation (tick 1-500)        | O(painted × 6) growing    | O(wavefront × 6)                        | ~equal during active painting |
| Stabilization (tick 500-1000) | O(all_cells × 6)          | O(shrinking_wavefront × 6)              | 10-100× faster                |
| Orbital test (tick 1000-5000) | O(all_cells × 6) constant | O(active_processes × wake_radius × 6)   | 100-1000× faster              |
| Long run (tick 5000+)         | O(all_cells × 6) grows    | O(active_processes × 6) nearly constant | Unbounded improvement         |

### Concrete estimate for orbital test

```
Full spreading:
  50,000 painted cells × 6 neighbors = 300,000 operations/tick
  × 5,000 ticks = 1.5 billion operations

Incremental:
  Formation (500 ticks):  ~50,000 ops/tick avg (wavefront growing)
  Stabilization (500 ticks): ~5,000 → 100 ops/tick (wavefront dying)  
  Orbital test (4000 ticks): ~200 ops/tick (5 test processes × ~40 wake cells)
  Total: ~26 million operations

  Speedup: ~60×
```

### Memory

Incremental spreading doesn't change peak memory — same cells get painted eventually. But `wake` dict is much smaller
than `gamma` dict at any given time (active wavefront vs total history), so the work-set iteration is cache-friendlier.

---

## Wake Field: Three Purposes, One Structure

After this change, `canvas.wake` serves three roles simultaneously:

| Role            | How                                  | Who uses it                                               |
|-----------------|--------------------------------------|-----------------------------------------------------------|
| **Physics**     | ∂γ/∂t tracks field change rate       | Processes read wake gradient for pressure sensing         |
| **Performance** | Nonzero wake = needs recomputation   | `spread_gamma_incremental()` uses as work list            |
| **Observation** | Wake magnitude shows where action is | Visualization, dark matter detection, activity monitoring |

No separate data structure needed. The physics IS the optimization.

---

## Correctness Guarantee

The incremental version produces **identical results** to full spreading, not approximate results. Proof:

1. A cell in equilibrium (all neighbors equal) produces zero transfer in full spreading.
2. Zero transfer means zero wake.
3. Incremental skips cells with zero wake.
4. Therefore: incremental skips exactly the cells that would produce zero transfer.
5. All non-zero transfers are computed identically.

**Test**: Run both versions for 100 ticks, compare gamma dicts cell-by-cell. They must be identical within float
tolerance.

```python
def test_incremental_matches_full():
    """Correctness test: incremental == full spreading."""
    canvas_full = Canvas3D_V18()
    canvas_incr = Canvas3D_V18()

    # Same initial conditions
    for pos in [(0, 0, 0), (1, 0, 0), (0, 1, 0)]:
        canvas_full.gamma[pos] = 100.0
        canvas_incr.gamma[pos] = 100.0
        canvas_full.wake[pos] = 100.0
        canvas_incr.wake[pos] = 100.0

    for tick in range(100):
        canvas_full.spread_gamma()  # Full version
        canvas_incr.spread_gamma_incremental()  # Incremental

    # Compare all cells
    all_positions = set(canvas_full.gamma.keys()) | set(canvas_incr.gamma.keys())
    for pos in all_positions:
        g_full = canvas_full.gamma.get(pos, 0.0)
        g_incr = canvas_incr.gamma.get(pos, 0.0)
        assert abs(g_full - g_incr) < 1e-6, f"Mismatch at {pos}: {g_full} vs {g_incr}"
```

---

## Integration Notes

### Tick loop with incremental spreading

```python
def evolve_one_tick(self):
    self.tick_count += 1

    # 1. Create new process
    new_process = self.create_new_process()
    self.processes.append(new_process)

    # 2. Each process steps (paint + move)
    #    paint_imprint() already updates wake for freshly painted cells
    for process in self.processes[:]:
        continues = process.step(self.canvas)
        if not continues:
            self.processes.remove(process)

    # 3. Incremental spreading (only from cells with nonzero wake)
    self.canvas.spread_gamma_incremental()

    # 4. Record statistics
    self._record_stats()
```

### paint_imprint() must seed the wake

When a process paints, the painted cell gets a wake entry. This is already in `canvas_v18.py`:

```python
def paint_imprint(self, process_id, profile, center):
    for rel_pos, strength in profile.items():
        pos = (center[0] + rel_pos[0], center[1] + rel_pos[1], center[2] + rel_pos[2])
        old_gamma = self.gamma.get(pos, 0.0)
        self.gamma[pos] = old_gamma + strength
        # Wake tracks the change — this seeds incremental spreading
        self.wake[pos] = self.wake.get(pos, 0.0) + strength
```

This means: process paints → wake is nonzero at painted cell → next tick's `spread_gamma_incremental()` picks it up →
spreading wavefront begins → propagates at 1 cell/tick until equilibrium.

No changes needed to `paint_imprint()`. It already does the right thing.

### Wake decay is replaced, not needed

The old `canvas.decay_wake(decay_rate=0.05)` is no longer appropriate. In the incremental model, wake is not a decaying
field — it's a precise record of what changed this tick. `spread_gamma_incremental()` replaces `self.wake` entirely each
tick with exactly the transfers that occurred.

**Remove `canvas.decay_wake()` from the tick loop.** Wake is now managed exclusively by `spread_gamma_incremental()` and
`paint_imprint()`.

---

## For Model C (Storage Engine)

The same optimization applies directly:

```
Write to key "user.project.task"
→ wake["user.project.task"] = delta
→ next tick: spread influence to adjacent keys
→ wavefront propagates outward at bounded speed
→ settled regions cost nothing
→ work proportional to ACTIVITY, not DATA SIZE
```

A database with 10 million keys where 50 are being written to does work proportional to 50, not 10 million. Queries
navigating through settled regions read from equilibrium field — O(1) lookups, no recomputation.

This is why the canvas model can scale. The denominator isn't data size — it's an activity rate. A cold database with
occasional writes is nearly free to maintain.

---

## Summary

| Aspect            | Full spreading         | Incremental spreading                  |
|-------------------|------------------------|----------------------------------------|
| Iterates          | ALL painted cells      | ONLY changed cells + their neighbors   |
| Work per tick     | O(total_painted × 6)   | O(wavefront × 6)                       |
| Steady state cost | Same as peak           | Nearly zero                            |
| Result            | Exact                  | Identical to full                      |
| Wake role         | Separate physics field | Physics + work list + activity monitor |
| Implementation    | Simple loop over gamma | Loop over wake, seed from paint        |

**One sentence**: Don't recompute what hasn't changed. The wake field already knows.
