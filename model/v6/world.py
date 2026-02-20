"""World: tick orchestration with two-phase entity lifecycle.

V6 orbital program -- learning phase + execution phase + binary fission:

Update order each tick:
  1. Tick energy  -- each entity gets +1 energy from the tick
  2. Imprint      -- each entity deposits 1 to gamma at its position
  2b. Photonic emission -- each entity radiates presence to photon field
  3. (no expansion -- entities are the sole gamma source)
  4. Diffusion    -- average with neighbors (scipy convolve) for both fields
  5. Movement     -- entity prefers to STAY on local gamma peak;
                     otherwise: learning = gradient blend, execution = program replay
  6. Memory       -- learning entities record direction decision (including stay)
  7. Phase check  -- learning entities with full memory -> start execution
  8. Orbit check  -- execution entities at cycle end: orbit closed -> loop; failed -> binary fission

Zero physics parameters. All dynamics from geometry + tick energy.
Entity is its pattern of imprints. Staying still = concentrated hill = mass.
"""

import math

from grid import Grid, HexGrid2D, Position, HEX_DIRS, HEX_DIR_VECTORS
from field import GammaField
from entity import Entity, next_entity_id, STAY


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
    """Orchestrates the tick-frame simulation with orbital program."""

    def __init__(self, grid: Grid, seed_positions: list[Position] | None = None,
                 initial_memory_size: int = 1):
        self.grid = grid
        self.field = GammaField(grid)
        self.photon_field = GammaField(grid)
        self.entities: list[Entity] = []
        self.tick = 0
        self.replication_events = 0
        self.dissolution_events = 0
        self.max_generation = 0
        self.blocked_moves = 0
        self.trapped_entities = 0
        self.failed_replications = 0

        # V6: orbital tracking
        self.orbit_closures = 0
        self.orbit_failures = 0
        self.stay_decisions = 0
        self.braking_emissions = 0

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

        # Step 2: Photonic emission -- entity radiates presence to photon field
        for e in self.entities:
            if e.alive:
                self.photon_field.deposit(e.pos, 1.0)

        # Step 3: Diffusion -- smooth both fields (propagation at c = 1 cell/tick)
        # (no universal expansion -- entities are the sole gamma source)
        self.field.diffuse()
        self.photon_field.diffuse()

        # Step 4: Movement -- entity follows gamma peak
        committed: set[Position] = set()
        living = sorted([e for e in self.entities if e.alive], key=lambda e: e.id)
        occupied = {e.pos for e in living}

        for e in living:
            if e.phase == 'learning':
                # Is local gamma strong enough to hold entity? (hill = gravity)
                # Entity stays on strong hills, moves on flat/weak ground.
                current_gamma = self.field.value_at(e.pos)
                max_neighbor_gamma = 0.0
                for dq, dr in HEX_DIRS:
                    npos = (e.pos[0] + dq, e.pos[1] + dr)
                    if self.grid.is_valid(npos):
                        ng = self.field.value_at(npos)
                        if ng > max_neighbor_gamma:
                            max_neighbor_gamma = ng

                if current_gamma > max_neighbor_gamma and current_gamma > 1.0:
                    # On a real hill peak (gamma > 1.0) — stay and build mass
                    dir_idx = STAY
                else:
                    # Moving: gradient + heading blend
                    gradient = self.field.gradient_at(e.pos)
                    occ_gradient = _occupancy_gradient(e.pos, occupied, self.grid)
                    photon_grad = self.photon_field.gradient_at(e.pos)
                    dir_idx = e.choose_direction(gradient, occ_gradient, photon_grad)
            else:
                # Execution phase: replay program (may include STAY)
                dir_idx = e.get_program_direction()

            # --- Movement resolution ---
            actual_dir = dir_idx
            if dir_idx == STAY:
                # STAY only from execution replay — try it, fallback to move
                if e.pos not in committed:
                    committed.add(e.pos)
                    self.stay_decisions += 1
                else:
                    actual_dir = self._resolve_forced_move(e, committed, occupied)
            else:
                dq, dr = HEX_DIRS[dir_idx]
                new_pos = (e.pos[0] + dq, e.pos[1] + dr)

                if self.grid.is_valid(new_pos) and new_pos not in committed:
                    e.pos = new_pos
                    committed.add(new_pos)
                    if e.phase == 'learning':
                        e.record_decision(dir_idx)
                else:
                    # Preferred blocked -- rotate through alternatives
                    moved = False
                    for offset in range(1, 6):
                        alt_idx = (dir_idx + offset) % 6
                        adq, adr = HEX_DIRS[alt_idx]
                        alt_pos = (e.pos[0] + adq, e.pos[1] + adr)
                        if self.grid.is_valid(alt_pos) and alt_pos not in committed:
                            e.pos = alt_pos
                            committed.add(alt_pos)
                            actual_dir = alt_idx
                            if e.phase == 'learning':
                                e.record_decision(alt_idx)
                            self.blocked_moves += 1
                            moved = True
                            break
                    if not moved:
                        # All 6 blocked -- last resort: stay
                        if e.pos not in committed:
                            committed.add(e.pos)
                            actual_dir = STAY
                            self.trapped_entities += 1
                        else:
                            e.alive = False
                            self.trapped_entities += 1

            if not e.alive:
                continue

            # Step 5: Imprint + braking radiation
            # Did entity change direction? If so, emit braking photon.
            braked = (e.last_direction >= 0 and actual_dir != e.last_direction)
            e.last_direction = actual_dir

            amount = e.imprint_energy()  # takes all energy, resets to 0
            if amount <= 0:
                continue

            if braked:
                # Braking: shoot energy toward lowest gamma neighbor
                self._emit_braking_photon(e.pos, amount)
                self.braking_emissions += 1
            else:
                # No braking: deposit as gamma at current position (build hill)
                self.field.deposit(e.pos, amount)

            # Phase transition: learning -> execution
            if e.is_memory_full():
                e.start_execution(e.pos)

        # Step 7: Orbit check + Binary fission replication
        new_entities: list[Entity] = []
        for e in living:
            if not e.alive:
                continue

            # Only execution-phase entities with completed cycles are candidates
            if e.phase != 'execution' or not e.is_cycle_complete():
                continue

            # Orbit closure check
            if e.check_orbit_closure(e.pos):
                # Orbit closed -- reset cycle, entity lives on
                e.reset_cycle(e.pos)
                self.orbit_closures += 1
                continue

            # Orbit failed -- trigger binary fission
            self.orbit_failures += 1

            # Find free neighbors with direction indices
            free_directed: list[tuple[int, Position]] = []
            for i, (dq, dr) in enumerate(HEX_DIRS):
                npos = (e.pos[0] + dq, e.pos[1] + dr)
                if self.grid.is_valid(npos) and npos not in committed:
                    free_directed.append((i, npos))

            if len(free_directed) == 0:
                self.failed_replications += 1
                # Entity with failed orbit and no space: it dies anyway
                e.alive = False
                committed.discard(e.pos)
                continue

            # Binary fission: pick 2 best directions using blend vector
            gradient = self.field.gradient_at(e.pos)
            occ_gradient = _occupancy_gradient(e.pos, occupied, self.grid)
            photon_grad = self.photon_field.gradient_at(e.pos)
            blend_x, blend_y = e.compute_blend_vector(gradient, occ_gradient, photon_grad)

            # Score each free direction by alignment with blend
            scored = []
            for dir_idx, npos in free_directed:
                ux, uy = HEX_DIR_VECTORS[dir_idx]
                score = ux * blend_x + uy * blend_y
                scored.append((score, dir_idx, npos))
            scored.sort(reverse=True)
            best_two = scored[:2]

            # Parent dies
            e.alive = False
            committed.discard(e.pos)
            child_memory_size = self.tick

            for _, dir_idx, child_pos in best_two:
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

        # Remove dead entities
        dead_count = sum(1 for e in self.entities if not e.alive)
        self.dissolution_events += dead_count
        self.entities = [e for e in self.entities if e.alive]

    def _find_peak_direction(self, pos: Position) -> int:
        """Find direction toward highest gamma cell (including current = STAY).

        Pure peak-following: entity wants to sit on the highest point.
        If current cell is highest (or tied) -> STAY.
        Otherwise -> direction index of highest neighbor.
        """
        current_gamma = self.field.value_at(pos)
        best_gamma = current_gamma
        best_dir = STAY

        for i, (dq, dr) in enumerate(HEX_DIRS):
            npos = (pos[0] + dq, pos[1] + dr)
            if not self.grid.is_valid(npos):
                continue
            ng = self.field.value_at(npos)
            if ng > best_gamma:
                best_gamma = ng
                best_dir = i

        return best_dir

    def _resolve_forced_move(self, e: Entity, committed: set[Position],
                             occupied: set[Position]) -> int:
        """Entity can't stay -- move to highest available gamma neighbor.

        Returns the actual direction used (or -1 if dissolved).
        """
        ranked: list[tuple[float, int, Position]] = []
        for i, (dq, dr) in enumerate(HEX_DIRS):
            npos = (e.pos[0] + dq, e.pos[1] + dr)
            if self.grid.is_valid(npos) and npos not in committed:
                ranked.append((self.field.value_at(npos), i, npos))
        ranked.sort(reverse=True)

        for _, dir_idx, new_pos in ranked:
            e.pos = new_pos
            committed.add(new_pos)
            if e.phase == 'learning':
                e.record_decision(dir_idx)
            self.blocked_moves += 1
            return dir_idx

        # Completely stuck -- dissolve
        e.alive = False
        self.trapped_entities += 1
        return -1

    def _emit_braking_photon(self, pos: Position, energy: float) -> None:
        """Braking radiation: shoot energy downhill (toward lowest gamma).

        Hill model: high gamma = top of hill = gravity center.
        Braking photon goes downhill = toward lower gamma = outward.
        The entity loses energy to maintain its orbit on the hill slope.
        """
        lowest_gamma = float('inf')
        target = pos

        for dq, dr in HEX_DIRS:
            npos = (pos[0] + dq, pos[1] + dr)
            if not self.grid.is_valid(npos):
                continue
            ng = self.field.value_at(npos)
            if ng < lowest_gamma:
                lowest_gamma = ng
                target = npos

        self.field.deposit(target, energy)

    def entity_count(self) -> int:
        return len(self.entities)

    def total_entity_energy(self) -> float:
        return sum(e.energy for e in self.entities)

    def total_system_energy(self) -> float:
        """Total energy: gamma field + photon field + all entities."""
        return self.field.total_energy() + self.photon_field.total_energy() + self.total_entity_energy()

    def population_by_generation(self) -> dict[int, int]:
        """Count entities per generation."""
        counts: dict[int, int] = {}
        for e in self.entities:
            counts[e.generation] = counts.get(e.generation, 0) + 1
        return counts

    def phase_counts(self) -> tuple[int, int, int]:
        """Count entities by phase: (learning, execution, orbiting).

        orbiting = execution phase entities that have completed >= 1 cycle.
        """
        learning = 0
        execution = 0
        orbiting = 0
        for e in self.entities:
            if e.phase == 'learning':
                learning += 1
            else:
                if e.completed_cycles >= 1:
                    orbiting += 1
                else:
                    execution += 1
        return learning, execution, orbiting
