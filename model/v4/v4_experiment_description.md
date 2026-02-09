# V4: Memory-Driven Gamma Field with Depth-2 Occupancy + Fill-All Replication

## Mechanism

V4 is a zero-parameter tick-frame simulation on a hex grid (radius 60, ~10K cells). Each tick:

1. **Tick energy** -- each entity gains +1 energy
2. **Imprint** -- each entity deposits its energy to the gamma field at its position (builds hill)
3. **Expansion** -- gamma[all] += 1.0 (sole field energy source)
4. **Diffusion** -- hex averaging (self + 6 neighbors) / 7, propagation at c = 1 cell/tick
5. **Movement** -- three-way blend of gamma gradient (uphill attraction), memory heading (inertia), and depth-2 occupancy gradient (seek free neighbors) -> move 1 cell
6. **Memory** -- each entity records its direction decision
7. **Replication** -- entities with full memory -> parent dies -> N children spawned at ALL free neighbors (fill-all replication). Children inherit direction-filtered parent memory.

Key innovations over V3:
- **Zero physics parameters** -- all dynamics from geometry + tick energy
- **Memory-driven lifecycle** -- memory size = birth tick, so later entities live longer
- **Fill-all replication** -- parent fills every free neighbor, not just 2
- **Depth-2 occupancy sensing** -- entities sense free space 2 cells deep, not just immediate neighbors

## Results (200 ticks, single seed at origin)

- **Population**: peaks then settles to ~96 entities in a single stable vortex
- **Structure**: entities cluster into one rotating vortex around the gamma hill they collectively build
- **Replication**: ~1,445 total entities created, but most dissolve or are crowded out
- **Energy**: system energy grows linearly (expansion-dominated)

## Conclusion

V4 successfully demonstrates:
- Gravitational attraction (entities cluster on gamma hills)
- Self-organized rotation (vortex formation from heading + gradient)
- Population regulation (fill-all replication + crowding dissolution)

**Core problem identified**: gamma gradient attracts entities to the same hills they build -- self-reinforcing clustering that occupancy gradient alone cannot break. Entities need a way to sense other entities at range and move away to find better replication conditions.

This leads to **V5: Photonic Emission** -- adding a second field carrying entity-presence information, creating repulsion that balances the gamma attraction.
