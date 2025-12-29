def apply_law000(graph, state, tick):
    new_state = {}
    for node, neighbors in graph.items():
        active_neighbors = sum(state[n] for n in neighbors)
        parity = active_neighbors % 2

        # chaos injector: flip every second tick
        chaos = tick & 1

        new_state[node] = state[node] ^ parity ^ chaos

    return new_state
