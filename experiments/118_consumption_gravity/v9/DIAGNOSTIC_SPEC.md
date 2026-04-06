# Experiment 118 v9 Diagnostic: Tangential Motion Analysis

## Status: READY FOR IMPLEMENTATION
## Date: April 2, 2026
## Purpose: Determine what mechanism produces the ~2000 degrees of tangential motion

---

## The Question

v7, v8, and v9 all produce tangential motion (~1800-2400 total degrees
over 200k ticks) without a seeded kick. The RAW 128 partition mechanism
doesn't engage (store = 0 across all runs). Something else is producing
the tangential motion. What is it?

**Three hypotheses:**

1. **Graph topology asymmetry.** The random geometric graph has local
   irregularities. At each routing decision, the "best" connector isn't
   exactly radial — it's offset by some angle. If the offsets are biased
   (e.g., consistently clockwise at certain nodes), tangential motion
   accumulates.

2. **Star emission asymmetry.** The star's 80 nodes deposit at random
   locations each tick. The instantaneous deposit pattern is never
   spherically symmetric. The planet responds to the asymmetric field,
   getting sideways nudges from wherever the star deposited most recently.

3. **Planet's own deposit trail.** The planet deposits as it moves. These
   deposits create a trail on the connectors it traversed. If the trail
   curves (from topology), it creates a self-reinforcing feedback — the
   planet routes toward its own curved trail.

**These are not mutually exclusive.** All three might contribute. The
diagnostic needs to separate their contributions.

---

## Diagnostic Measurements

### D1: Per-Hop Routing Decomposition

At EVERY planet hop (when the planet node arrives at a new node and
makes a routing decision), record:

```python
# At the moment of routing decision:
star_com = current star center of mass position
planet_pos = pos[planet_node]
chosen_pos = pos[chosen_neighbor]

# Radial direction: planet toward star
radial_dir = normalize(star_com - planet_pos)

# Hop direction: planet toward chosen neighbor
hop_dir = normalize(chosen_pos - planet_pos)

# Decompose hop into radial and tangential components
radial_component = dot(hop_dir, radial_dir)  # positive = toward star
tangential_component = cross(hop_dir, radial_dir)  # signed tangential

# Record per hop:
hop_record = {
    'tick': current_tick,
    'planet_pos': planet_pos,
    'star_com': star_com,
    'distance': norm(star_com - planet_pos),
    'chosen_neighbor': chosen_neighbor_id,
    'radial_component': radial_component,    # -1 to +1
    'tangential_component': tangential_component,  # signed vector (3D)
    'tangential_magnitude': norm(tangential_component),
    'tangential_sign': sign of the z-component of the cross product
                       (or use atan2 for a consistent angular measure),
    'n_candidates': number of neighbors considered,
    'best_score': deposit count on chosen connector,
    'second_score': deposit count on second-best connector,
    'radial_best_score': deposit count on the most-radial connector,
}
```

**What this tells us:** If tangential_sign is consistently positive (or
negative) over many hops, there's a systematic bias. If it's random but
with nonzero mean, it's a statistical drift. If it correlates with
distance, the bias depends on the orbital phase.

### D2: Tangential Accumulation vs Time

Plot cumulative tangential displacement (sum of tangential_component
over all hops) vs tick. Compare to cumulative angular position already
measured. They should match — the angular position IS the accumulated
tangential hops.

**Key plot:** tangential_component per hop vs time. Is it noisy but
centered on zero (random walk in angle)? Or is there a visible bias
(systematic deflection)?

### D3: Graph Topology Test — Does the Graph Alone Bias the Path?

**Critical test:** Remove ALL deposits. Let the planet do a pure random
walk on the graph (uniform probability across all neighbors) starting
from the same initial node. Record the angular displacement over 200k
ticks. Repeat 10-20 times with different random seeds.

If the PURE RANDOM WALK produces angular displacement of similar
magnitude to the deposit-routing version (~2000 degrees), then the
graph topology alone provides the tangential motion. The deposits
and routing are irrelevant — any random walk on this graph produces
angular drift.

If the pure random walk produces much LESS angular displacement (say
~200 degrees — sqrt(N) scaling from random walk), then the deposits
and routing are amplifying a small topological bias into coherent
tangential motion.

**Implementation:**
```python
def random_walk_test(graph, start_node, star_com, n_ticks, seed):
    """Pure random walk — no deposits, no routing signal."""
    rng = np.random.default_rng(seed)
    node = start_node
    cumulative_angle = 0.0
    prev_pos = graph.pos[node]
    
    for tick in range(n_ticks):
        neighbors = graph.neighbors(node)
        node = neighbors[rng.integers(len(neighbors))]
        curr_pos = graph.pos[node]
        
        # Track angular displacement around star_com
        delta_angle = angular_displacement(prev_pos, curr_pos, star_com)
        cumulative_angle += delta_angle
        prev_pos = curr_pos
    
    return cumulative_angle
```

Run 20 times. Report mean and std of cumulative angle. Compare to the
~474 net degrees (v9) and ~1869 total degrees (v9).

### D4: Star Asymmetry Test — Frozen Star

**Test:** Run the v9 experiment but FREEZE the star after warmup. Star
nodes stop hopping. The deposit field is static. Only the planet moves.

If tangential motion persists → it's not star emission asymmetry.
The static field plus graph topology are sufficient.

If tangential motion disappears → the star's dynamic emission provides
the sideways kicks. The planet needs the star's time-varying asymmetry
to accumulate angular momentum.

### D5: Planet Trail Test — Planet Without Deposits

**Test:** Run the v9 experiment but the planet does NOT deposit on
connectors when it arrives. It reads the deposit field and routes, but
leaves no trace. Only the star deposits.

If tangential motion persists → it's not the planet's own trail. The
star field plus topology are sufficient.

If tangential motion disappears or weakens significantly → the planet's
own deposits are creating the self-reinforcing feedback.

### D6: Score Margin Analysis

At each routing decision, how close is the competition?

```python
margin = (best_score - second_score) / best_score if best_score > 0 else 0
```

If margin is typically large (>0.5): the routing is strongly determined
by deposits. The chosen connector is clearly the best. Tangential
deviation is from the graph geometry (the best connector doesn't point
exactly radially).

If margin is typically small (<0.1): the routing is nearly random among
several similar-scoring connectors. The tangential motion is effectively
a random walk among near-ties.

---

## Implementation Notes

### Minimal code changes to v9:

1. Add a `hop_log` list to the planet entity
2. At each routing decision in EntityNode.tick(), append a hop_record dict
3. After the run, save hop_log to CSV
4. Add the random walk test as a standalone function
5. Add the frozen-star and no-deposit variants as command-line flags

### Suggested command-line flags:
```
python phase2_diagnostic.py                    # normal run with instrumentation
python phase2_diagnostic.py --random-walk      # D3: pure random walk, no deposits
python phase2_diagnostic.py --frozen-star      # D4: star stops after warmup
python phase2_diagnostic.py --no-planet-deposit # D5: planet doesn't deposit
```

### Output files:
```
results/
├── hop_log.csv              # per-hop routing data (D1)
├── tangential_accumulation.png  # D2: cumulative tangential vs time
├── per_hop_tangential.png   # D2: tangential component per hop
├── random_walk_results.csv  # D3: 20 random walk trials
├── random_walk_comparison.png   # D3: random walk vs routed
├── frozen_star_results.png  # D4: frozen star orbit
├── no_deposit_results.png   # D5: no planet deposits
├── score_margin_histogram.png   # D6: routing decision margins
└── diagnostic_summary.txt   # text summary of all findings
```

### Run order:
1. Normal run with instrumentation (D1, D2, D6) — single run
2. Random walk test (D3) — 20 trials, fast (no deposits to compute)
3. Frozen star (D4) — single run
4. No planet deposits (D5) — single run

Total: ~4 runs, each 200k ticks. Should complete in under an hour.

---

## What the Results Will Tell Us

| D3 result | D4 result | D5 result | Mechanism |
|-----------|-----------|-----------|-----------|
| RW ~ orbit | any | any | Graph topology alone. Deposits don't matter. |
| RW << orbit | frozen ≈ orbit | no-dep ≈ orbit | Static deposit FIELD biases topology. |
| RW << orbit | frozen ≈ orbit | no-dep << orbit | Planet trail creates feedback on static field. |
| RW << orbit | frozen << orbit | any | Star's dynamic asymmetry drives tangential kicks. |
| RW << orbit | frozen << orbit | no-dep << orbit | Both star asymmetry AND planet trail needed. |

The most informative outcome is D3 (random walk). If the random walk
produces similar angular displacement to the routed version, the entire
deposit/routing mechanism is irrelevant for tangential motion — the
graph does it alone. That would be the simplest explanation and would
fundamentally change what we think the orbit mechanism is.

---

*This is a diagnostic, not a new version. Run on v9 code with
minimal modifications. The goal is UNDERSTANDING, not new features.*
