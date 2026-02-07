import numpy as np

# ==========================
# Constants
# ==========================

WORLD_SIZE = 200               # 200x200 grid
DELTA_H = 0.2                  # global hill increment per commit
ALPHA_IMPRINT = 0.3            # imprint influence coefficient (was 1.2 — 1D reduced)
MOVE_COST = 0.05
COMP_COST = 0.02
IMPRINT_COST_BASE = 0.08      # base imprint cost (scales with window — 1C)
SPREAD_SIGMA = 1.0             # 2D Gaussian spread sigma

PASSIVE_ENERGY_RATE = 0.02     # slope-based passive energy (Doc 03 Sec 7.1) — boosted for [0,1] hill
BASE_ENERGY_RATE = 0.06        # guaranteed income per tick — enough for ~1 move at the edge
POSITION_ENERGY_RATE = 0.04    # bonus from hill height (h in [0,1])
STASIS_COST = 0.03             # penalty per tick for not moving
ENERGY_CAP = 2.0               # max energy before radiation bleeds excess
DECAY = 0.995                  # hill natural sink per commit (Doc 03 Sec 2.1)
BETA_IMPRINT = 0.7             # imprint field decay per commit (was 0.9 — 1E faster decay)
EPSILON_STABLE = 0.05          # stabilization condition (Doc 02 Sec 4.1.7)
EPSILON_DH = 0.01              # DeltaH threshold for correction logic (Doc 03 Sec 5)
REPLICATION_DH_THRESHOLD = 0.08 # (was 0.3 — lowered for [0,1] normalized hill, typical ΔH ~0.05–0.15)
REPLICATION_DDH_THRESHOLD = -0.02  # (was -0.1 — normalized hill second derivative ~±0.01)
REPLICATION_ENERGY_COST = 0.15     # (was 0.5 — at ~0.02/tick surplus, reachable after ~8 ticks)
REPLICATION_COOLDOWN = 15      # min ticks between replications (1G)
WINDOW_GROWTH = 1
MAX_ENTITIES = 50
MAX_LOCAL_TICKS = 20
LEAK_DECAY = 0.95
RADIATION_SCALE = 0.3
MERGE_COMPAT_THRESHOLD = 0.5
MERGE_ENERGY_TRANSFER = 0.8
RING_DISTANCE = 5
MIN_REPLICATION_AGE = 20       # (was 10 — 1G conservative)
PATTERN_DECAY = 0.9            # EMA decay for pattern (1B)
INERTIA = 0.6                  # heading inertia (2B)

# Entity colors for visualization
ENTITY_COLORS = [
    (0, 255, 0), (255, 255, 0), (0, 255, 255), (255, 128, 0),
    (128, 255, 0), (0, 128, 255), (255, 0, 128), (128, 0, 255),
    (255, 128, 128), (128, 255, 128),
]

# Precomputed 2D render offsets — cycled through for imprint placement
RENDER_OFFSETS = [
    (0, 0), (1, 0), (0, 1), (-1, 0), (0, -1),
    (1, 1), (-1, 1), (-1, -1), (1, -1),
]

DIRS = [
    (0, -1), (1, -1), (1, 0), (1, 1),
    (0, 1), (-1, 1), (-1, 0), (-1, -1)
]  # N, NE, E, SE, S, SW, W, NW
DIR_COSTS = [
    1.0, np.sqrt(2), 1.0, np.sqrt(2),
    1.0, np.sqrt(2), 1.0, np.sqrt(2)
]  # diagonal movement costs sqrt(2)x
