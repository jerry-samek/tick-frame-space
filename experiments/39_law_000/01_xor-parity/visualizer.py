def print_state(diff, tick):
    print(f"\n=== TICK {tick} ===")
    print(f"Added edges: {len(diff['added_edges'])}")
    if diff['added_edges']:
        print(f"  {diff['added_edges'][:10]}{'...' if len(diff['added_edges']) > 10 else ''}")
    print(f"Removed edges: {len(diff['removed_edges'])}")
    if diff['removed_edges']:
        print(f"  {diff['removed_edges'][:10]}{'...' if len(diff['removed_edges']) > 10 else ''}")


def render_heatmap(diff, width=40, height=20):
    grid = [[0 for _ in range(width)] for _ in range(height)]
    changes = diff["added_edges"] + diff["removed_edges"]

    # bucketování
    for (a, b) in changes:
        x = (a + b) % width
        y = (a * 31 + b * 17) % height
        grid[y][x] += 1

    # najdeme maximum
    max_val = max(max(row) for row in grid) or 1

    # ASCII škála
    scale = " .:-=+*#%@"
    levels = len(scale) - 1

    # ANSI barvy (od studených po horké)
    colors = [
        "\033[38;5;240m",  # šedá
        "\033[38;5;244m",  # světlejší šedá
        "\033[38;5;250m",  # skoro bílá
        "\033[38;5;34m",  # zelená
        "\033[38;5;70m",  # světle zelená
        "\033[38;5;142m",  # žlutá
        "\033[38;5;208m",  # oranžová
        "\033[38;5;196m",  # červená
        "\033[38;5;199m",  # růžová
        "\033[38;5;201m",  # fialová
    ]

    lines = ["======================================="]
    for row in grid:
        line = ""
        for val in row:
            norm = val / max_val
            idx = int(norm * levels)
            char = scale[idx]
            color = colors[idx]
            line += f"{color}{char}\033[0m"
        lines.append(line)

    return "\n".join(lines)

def render_heatmap_indexed(diff, width=40, height=20):
    # vezmeme hrany v pořadí, v jakém je observer vrátil
    edges = diff["added_edges"] + diff["removed_edges"]

    # indexy 0..len(edges)-1
    grid = [[0 for _ in range(width)] for _ in range(height)]

    for idx, edge in enumerate(edges):
        # stabilní bucketování podle indexu
        x = idx % width
        y = (idx * 7) % height
        grid[y][x] += 1

    # normalizace
    max_val = max(max(row) for row in grid) or 1
    scale = " .:-=+*#%@"
    levels = len(scale) - 1

    lines = []
    for row in grid:
        line = ""
        for val in row:
            norm = val / max_val
            char = scale[int(norm * levels)]
            line += char
        lines.append(line)

    return "\n".join(lines)
