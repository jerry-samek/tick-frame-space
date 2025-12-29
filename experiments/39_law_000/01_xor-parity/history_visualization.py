class HistoryVisualization:
    def __init__(self, width=40, height=20, horizon=10):
        self.width = width
        self.height = height
        self.horizon = horizon
        self.history = []  # posledních N gridů

    # ----------------------------------------
    # Build grid from diff (indexed bucketování)
    # ----------------------------------------
    def build_grid_from_diff(self, diff):
        edges = diff["added_edges"] + diff["removed_edges"]
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        for idx, edge in enumerate(edges):
            x = idx % self.width
            y = (idx * 7) % self.height
            grid[y][x] += 1

        return grid

    # ----------------------------------------
    # Update history buffer
    # ----------------------------------------
    def update_history(self, grid):
        self.history.append(grid)
        if len(self.history) > self.horizon:
            self.history.pop(0)

    # ----------------------------------------
    # Accumulate persistent history
    # ----------------------------------------
    def accumulate_history(self):
        acc = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for grid in self.history:
            for y in range(self.height):
                for x in range(self.width):
                    acc[y][x] += grid[y][x]
        return acc

    # ----------------------------------------
    # Normalize grid to 0..1
    # ----------------------------------------
    def normalize_grid(self, grid):
        max_val = max(max(row) for row in grid) or 1
        return [[val / max_val for val in row] for row in grid]

    # ----------------------------------------
    # Composite frame (persistence + current)
    # ----------------------------------------
    def composite_frame(self, acc, cur):
        acc_norm = self.normalize_grid(acc)
        cur_norm = self.normalize_grid(cur)

        p_scale = " .:-=+*#%@"   # persistence
        c_scale = " .:oO@"       # current

        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                p = acc_norm[y][x]
                c = cur_norm[y][x]

                if c > 0:
                    idx = int(c * (len(c_scale) - 1))
                    ch = c_scale[idx]
                else:
                    idx = int(p * (len(p_scale) - 1))
                    ch = p_scale[idx]

                line += ch
            lines.append(line)

        return lines

    # ----------------------------------------
    # Public API: process diff → ASCII vizualizace
    # ----------------------------------------
    def render(self, diff):
        cur = self.build_grid_from_diff(diff)
        self.update_history(cur)

        acc = self.accumulate_history()
        composite = self.composite_frame(acc, cur)

        return "\n".join(composite)
