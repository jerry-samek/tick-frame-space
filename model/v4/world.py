"""World: tick orchestration with the v4 memory-driven model.

Update order each tick:
  1. Tick energy  -- each entity gets +1 energy from the tick
  2. Imprint      -- each entity deposits 1 to gamma at its position
  3. Expansion    -- gamma[all] += 1.0 (field energy source)
  4. Diffusion    -- average with neighbors (scipy convolve)
  5. Movement     -- each entity: gradient + memory heading + depth-2 occupancy -> move 1 cell
  6. Memory       -- each entity records its direction decision
  7. Replication  -- entities with full memory -> parent dies -> N children (all free neighbors)

Zero physics parameters. All dynamics from geometry + tick energy.
"""

import math

from grid import Grid, HexGrid2D, Position, HEX_DIRS, HEX_DIR_VECTORS
from field import GammaField
from entity import Entity, next_entity_id


def _occupancy_gradient(pos: Position, occupied: set[Position], grid: Grid) -> tuple[float, float, float]:
    """Gradient pointing toward free neighbor cells, sensing 2 cells deep."""
    ox, oy = 0.0, 0.0
    for i, (dq, dr) in enumerate(HEX_DIRS):
        npos = (pos[0] + dq, pos[1] + dr)
        if not grid.is_valid(npos):
            continue
        if npos in occupied:
            continue
        # Distance-1 free
        value = 1.0
        # Depth check: also reward clear space at distance 2
        npos2 = (pos[0] + 2 * dq, pos[1] + 2 * dr)
        if grid.is_valid(npos2) and npos2 not in occupied:
            value += 1.0
        ux, uy = HEX_DIR_VECTORS[i]
        ox += value * ux
        oy += value * uy
    o_mag = math.sqrt(ox * ox + oy * oy)
    return ox, oy, o_mag


class World:
    """Orchestrates the tick-frame simulation with memory-driven entities."""

    def __init__(self, grid: Grid, seed_positions: list[Position] | None = None,
                 initial_memory_size: int = 1):
        self.grid = grid
        self.field = GammaField(grid)
        self.entities: list[Entity] = []
        self.tick = 0
        self.replication_events = 0
        self.dissolution_events = 0
        self.max_generation = 0
        self.blocked_moves = 0
        self.trapped_entities = 0
        self.failed_replications = 0

        if seed_positions:
            for pos in seed_positions:
                e = Entity(
                    entity_id=next_entity_id(),
                    pos=pos,
                    memory_size=initial_memory_size,
                    generation=0,
                )
                self.entities.append(e)

    def step(self) -> None:
        """Execute one tick of the simulation."""
        self.tick += 1

        # Step 1: Tick energy -- each entity gets +1 from the tick itself
        for e in self.entities:
            if e.alive:
                e.tick_energy()

        # Step 2: Imprint -- each entity deposits energy to gamma (builds hill)
        for e in self.entities:
            if e.alive:
                amount = e.imprint_energy()
                if amount > 0:
                    self.field.deposit(e.pos, amount)

        # Step 3: Expansion -- gamma += 1 everywhere (field energy source)
        self.field.expand()

        # Step 4: Diffusion -- smooth gamma (propagation at c = 1 cell/tick)
        self.field.diffuse()

        # Step 5: Movement -- gradient + memory heading + occupancy -> move 1 cell
        # Exclusive positions: max 1 entity per cell
        # Build committed set of positions that will be occupied
        committed: set[Position] = set()

        # Process entities in ID order for determinism
        living = sorted([e for e in self.entities if e.alive], key=lambda e: e.id)

        # Occupancy snapshot: stable view of current positions for all entities
        occupied = {e.pos for e in living}

        for e in living:
            gradient = self.field.gradient_at(e.pos)
            occ_gradient = _occupancy_gradient(e.pos, occupied, self.grid)
            dir_idx = e.choose_direction(gradient, occ_gradient)

            # Try preferred direction first
            dq, dr = HEX_DIRS[dir_idx]
            new_pos = (e.pos[0] + dq, e.pos[1] + dr)

            if self.grid.is_valid(new_pos) and new_pos not in committed:
                # Preferred direction is free
                e.pos = new_pos
                committed.add(new_pos)
                e.record_decision(dir_idx)
            else:
                # Preferred blocked or invalid -- rotate through remaining 5
                moved = False
                for offset in range(1, 6):
                    alt_idx = (dir_idx + offset) % 6
                    adq, adr = HEX_DIRS[alt_idx]
                    alt_pos = (e.pos[0] + adq, e.pos[1] + adr)
                    if self.grid.is_valid(alt_pos) and alt_pos not in committed:
                        e.pos = alt_pos
                        committed.add(alt_pos)
                        e.record_decision(alt_idx)
                        self.blocked_moves += 1
                        moved = True
                        break

                if not moved:
                    # ALL 6 neighbors blocked -> try to stay at current pos
                    if e.pos not in committed:
                        committed.add(e.pos)
                        e.record_decision(dir_idx)
                        self.trapped_entities += 1
                    else:
                        # Current position also taken (another entity moved here)
                        # Entity is displaced -- mark dead (dissolved by crowding)
                        e.alive = False
                        self.trapped_entities += 1

        # Step 7: Replication -- full memory -> parent dies -> N children (all free neighbors)
        new_entities: list[Entity] = []
        for e in living:
            if not e.alive:
                continue
            if not e.is_memory_full():
                continue

            # Find free neighbors with direction indices
            free_directed: list[tuple[int, Position]] = []
            for i, (dq, dr) in enumerate(HEX_DIRS):
                npos = (e.pos[0] + dq, e.pos[1] + dr)
                if self.grid.is_valid(npos) and npos not in committed:
                    free_directed.append((i, npos))

            if len(free_directed) == 0:
                self.failed_replications += 1
                continue

            e.prepare_replication_all()
            committed.discard(e.pos)
            child_memory_size = self.tick

            for dir_idx, child_pos in free_directed:
                filtered = e.filter_memory_for_direction(dir_idx)
                child = Entity(
                    entity_id=next_entity_id(),
                    pos=child_pos,
                    memory_size=child_memory_size,
                    initial_memory=filtered,
                    generation=e.generation + 1,
                )
                committed.add(child_pos)
                new_entities.append(child)

            self.replication_events += 1
            self.max_generation = max(self.max_generation, e.generation + 1)

        self.entities.extend(new_entities)

        # Remove dead entities (parents that replicated)
        dead_count = sum(1 for e in self.entities if not e.alive)
        self.dissolution_events += dead_count
        self.entities = [e for e in self.entities if e.alive]

    def entity_count(self) -> int:
        return len(self.entities)

    def total_entity_energy(self) -> float:
        return sum(e.energy for e in self.entities)

    def total_system_energy(self) -> float:
        """Total energy: field + all entities."""
        return self.field.total_energy() + self.total_entity_energy()

    def population_by_generation(self) -> dict[int, int]:
        """Count entities per generation."""
        counts: dict[int, int] = {}
        for e in self.entities:
            counts[e.generation] = counts.get(e.generation, 0) + 1
        return counts
