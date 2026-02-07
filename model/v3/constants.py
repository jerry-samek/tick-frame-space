import numpy as np

# ==========================
# Constants (v3 — hex grid)
# ==========================

WORLD_RADIUS = 100             # hex radius (~30K valid cells)
ALPHA_IMPRINT = 1.0            # imprints are primary hill-builder
MOVE_COST = 0.05               # uniform for all 6 directions (no diagonal penalty)
COMP_COST = 0.02
IMPRINT_COST_BASE = 0.03       # base imprint cost (scales with window)
SPREAD_FRACTION = 1.0 / 14.0   # less aggressive diffusion, hills persist

PASSIVE_ENERGY_RATE = 0.02     # slope-based passive energy
BASE_ENERGY_RATE = 0.005       # flat ground ≈ photon state
POSITION_ENERGY_RATE = 0.04    # energy comes from your hill
STASIS_COST = 0.0              # staying still during bootstrap is free
ENERGY_CAP = 2.0               # max energy before radiation bleeds excess
DECAY = 0.995                  # hill natural sink per commit
BETA_IMPRINT = 0.7             # imprint field decay per commit
EPSILON_STABLE = 0.05          # stabilization condition
EPSILON_DH = 0.01              # DeltaH threshold for correction logic
REPLICATION_DH_THRESHOLD = 0.08
REPLICATION_DDH_THRESHOLD = -0.02
REPLICATION_ENERGY_COST = 0.15
REPLICATION_COOLDOWN = 15      # min ticks between replications
WINDOW_GROWTH = 1
MAX_ENTITIES = 50
MAX_LOCAL_TICKS = 3
LEAK_DECAY = 0.95
RADIATION_SCALE = 0.3
MERGE_COMPAT_THRESHOLD = 0.5
MERGE_ENERGY_TRANSFER = 0.8
RING_DISTANCE = 5
MIN_REPLICATION_AGE = 20
PATTERN_DECAY = 0.9            # EMA decay for pattern
INERTIA = 0.6                  # heading inertia

# Entity colors for visualization
ENTITY_COLORS = [
    (0, 255, 0), (255, 255, 0), (0, 255, 255), (255, 128, 0),
    (128, 255, 0), (0, 128, 255), (255, 0, 128), (128, 0, 255),
    (255, 128, 128), (128, 255, 128),
]
