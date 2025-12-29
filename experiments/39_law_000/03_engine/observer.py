class Observer:
    def __init__(self, substrate, sample_interval=20):
        self.substrate = substrate
        self.sample_interval = sample_interval
        self.last_edges = self.edge_set(substrate.graph)

    def edge_set(self, graph):
        edges = set()
        for a, nbrs in graph.items():
            for b in nbrs:
                if a < b:
                    edges.add((a, b))
                else:
                    edges.add((b, a))
        return edges

    def observe(self, tick):
        # jen na sample ticku
        if tick % self.sample_interval != 0:
            return None

        current_edges = self.edge_set(self.substrate.graph)

        added = current_edges - self.last_edges
        removed = self.last_edges - current_edges

        diff = {
            "tick": tick,
            "added_edges": list(added),
            "removed_edges": list(removed)
        }

        # update last snapshot
        self.last_edges = current_edges

        return diff
