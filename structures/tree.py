from structures.node import Node
from scipy.spatial import KDTree
import numpy as np

#ograniczyć rośnięcie drzewa względem nawilżenia ale poprzez obszar nie ilośc nodów
#consumed attraction points też musi być zależny od moisture. Może do usunięcia


class Tree:
    def __init__(
        self,
        root_position: tuple[float, float, float],
        attraction_points: list,
        influence_radius: float = 2.0,
        kill_radius: float = 1.0,
        step_size: float = 0.5
    ):
        self.nodes: list[Node] = []
        self.edges: list[tuple[int, int]] = []
        self.attraction_points = attraction_points

        self.influence_radius = influence_radius
        self.kill_radius = kill_radius
        self.step_size = step_size

        self.grow_radius = 5.0 #zależny od moisture

        self.trunk_height = 4.0

        root = Node(*root_position, parent=None)
        self.nodes.append(root)

        self.max_attraction_points = 80
        self.consumed_attraction_points = 0
        self.trunk_end: Node = None

    def add_node(self, position, parent_index):
        node = Node(*position, parent=parent_index)
        self.nodes.append(node)
        self.edges.append((parent_index, len(self.nodes) - 1))

    # ---------------- TRUNK ----------------
    def grow_trunk(self):
        direction = np.array([0.0, 0.0, 1.0])
        last_idx = len(self.nodes) - 1
        last_node = self.nodes[last_idx]

        new_pos = last_node.position() + direction * self.step_size
        self.add_node(tuple(new_pos), last_idx)

        # Sprawdzenie czy pień osiągnął docelową wysokość
        if new_pos[2] >= self.nodes[0].z + self.trunk_height:
            self.trunk_done = True
            last_idx = len(self.nodes) - 1
            trunk_end = self.nodes[last_idx] #ostatni node z trunk, żeby z niego liczyć radius

    # ---------------- MAIN GROW ----------------
    def grow(self):
        if self.consumed_attraction_points >= self.max_attraction_points:
            return
        if not self.attraction_points:
            return
        if not self.trunk_done:
            self.grow_trunk()
            return

        node_positions = np.array([n.position() for n in self.nodes])
        kd_tree = KDTree(node_positions)
        growth_vectors = {i: [] for i in range(len(self.nodes))}

        # 1. Attraction point -> nearest node
        for ap in self.attraction_points:
            if ap <= kula o promieniu 5 dookoła trunk_end
                dist, idx = kd_tree.query(ap.position())
                if dist < self.influence_radius:
                    direction = ap.position() - self.nodes[idx].position()
                    norm = np.linalg.norm(direction)
                    if norm == 0:
                        continue
                    growth_vectors[idx].append(direction / norm)

        # Snapshot BEFORE adding new nodes
        nodes_snapshot = self.nodes.copy()
        new_nodes = []

        # 2. Average direction -> new node
        for node_idx, directions in growth_vectors.items():
            if not directions:
                continue
            avg_dir = np.mean(directions, axis=0)
            norm = np.linalg.norm(avg_dir)
            if norm == 0:
                continue
            avg_dir /= norm
            parent_node = self.nodes[node_idx]
            new_pos = parent_node.position() + avg_dir * self.step_size
            new_nodes.append((new_pos, node_idx))

        # 3. Collision-safe adding
        for pos, parent_idx in new_nodes:
            if all(np.linalg.norm(pos - n.position()) > self.step_size * 0.9
                   for n in self.nodes):
                self.add_node(tuple(pos), parent_idx)

        # 4. Kill attraction points
        remaining = []
        for ap in self.attraction_points:
            kill = False
            for node in nodes_snapshot:
                if np.linalg.norm(ap.position() - node.position()) < self.kill_radius:
                    kill = True
                    self.consumed_attraction_points += 1
                    break
            if not kill:
                remaining.append(ap)
        self.attraction_points = remaining
