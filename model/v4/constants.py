"""V4 constants -- structural only, zero physics parameters.

All dynamics derive from:
  - Hex geometry (6 neighbors, diffusion weight = 1/7)
  - c = 1 cell/tick (movement speed, expansion rate)
  - Tick energy = 1 unit/tick per entity (sole entity energy source)
  - Expansion = 1 unit/tick (sole field energy source)
"""

WORLD_RADIUS = 60  # hex radius (~10K valid cells)
INITIAL_MEMORY_SIZE = 1  # seed entity memory slots (tick 1 -> memory = 1)
