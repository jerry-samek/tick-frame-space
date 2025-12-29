from collections import deque


class Substrate:
    def __init__(self, graph, initial_state):
        self.graph = graph  # dict: node -> [neighbors]
        self.state = initial_state  # dict: node -> quaternion (w, x, y, z)

    def grow(self, parity_map):
        # najdeme další volné ID
        if self.graph:
            next_id = max(self.graph.keys()) + 1
        else:
            next_id = 0

        for node, parity in parity_map.items():
            if parity == 1:
                new_node = next_id
                next_id += 1

                # pokud node ještě není v grafu, inicializuj
                if node not in self.graph:
                    self.graph[node] = []

                # přidáme novou hranu, staré NESMAŽEME
                self.graph[node].append(new_node)
                self.graph[new_node] = [node]

                # nový uzel začíná s identity quaternionem
                self.state[new_node] = (1.0, 0.0, 0.0, 0.0)

    def prune_to_horizon(self, root, H):
        keep = bfs_horizon(self.graph, root, H)

        # Remove nodes outside the horizon
        for node in self.graph.keys():
            if node not in keep:
                del self.graph[node]
                if node in self.state:
                    del self.state[node]

        # Remove edges to deleted nodes
        for node, neighbors in self.graph.items():
            self.graph[node] = [n for n in neighbors if n in keep]

    def collapse_to_last_edge(self):
        # najdeme poslední vytvořený uzel
        if not self.graph:
            return

        last = max(self.graph.keys())

        # najdeme jeho rodiče (mělo by být 1)
        parents = self.graph[last]
        if not parents:
            return

        parent = parents[0]

        # vytvoříme nový minimalní graf
        self.graph = {
            parent: [last],
            last: [parent]
        }

        # zachováme stavy jen těchto dvou uzlů
        self.state = {
            parent: self.state.get(parent, (1.0, 0.0, 0.0, 0.0)),
            last: self.state.get(last, (1.0, 0.0, 0.0, 0.0))
        }

    def collapse_to_last_n_edges(self, n=10):
        # posbíráme všechny hrany
        all_edges = set()
        for a, nbrs in self.graph.items():
            for b in nbrs:
                edge = (min(a, b), max(a, b))
                all_edges.add(edge)

        if not all_edges:
            self.graph = {}
            self.state = {}
            return

        # seřadíme podle času (max uzlu)
        sorted_edges = sorted(all_edges, key=lambda e: max(e))

        # vezmeme posledních n
        selected = sorted_edges[-n:]

        # vytvoříme nový graf
        new_graph = {}
        new_state = {}

        for a, b in selected:
            new_graph.setdefault(a, []).append(b)
            new_graph.setdefault(b, []).append(a)
            new_state[a] = self.state.get(a, (1.0, 0.0, 0.0, 0.0))
            new_state[b] = self.state.get(b, (1.0, 0.0, 0.0, 0.0))

        self.graph = new_graph
        self.state = new_state


def bfs_horizon(graph, root, H):
    visited = {root}
    queue = deque([(root, 0)])

    while queue:
        node, dist = queue.popleft()
        if dist >= H:
            continue
        for nbr in graph[node]:
            if nbr not in visited:
                visited.add(nbr)
                queue.append((nbr, dist + 1))

    return visited
