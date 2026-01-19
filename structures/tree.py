from structures.node import Node
from scipy.spatial import KDTree
import numpy as np


class Tree:
    def __init__(
        self,
        root_position: tuple[float, float, float],
        attraction_points: list,
        terrain,
        influence_radius: float = 2.0,
        kill_radius: float = 1.0,
        step_size: float = 0.5,
    ):
        self.nodes: list[Node] = []
        self.edges: list[tuple[int, int]] = []
        self.attraction_points = attraction_points

        self.influence_radius = influence_radius
        self.kill_radius = kill_radius
        self.step_size = step_size

        self.trunk_height = 4.0
        self.trunk_done = False
        self.trunk_end: Node | None = None

        self.terrain = terrain

        # --- ROOT ---
        root = Node(*root_position, parent=None)
        self.nodes.append(root)

        # --- LIMIT WZROSTU ZALEŻNY OD MOISTURE ---
        root_x, root_y, _ = root_position
        root_moisture = self.terrain.moisture(root_x, root_y)

        self.max_attraction_points = int(30 + 150 * root_moisture)
        self.consumed_attraction_points = 0

    # -------------------------------------------------

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

        if new_pos[2] >= self.nodes[0].z + self.trunk_height:
            self.trunk_done = True
            self.trunk_end = self.nodes[-1]

    # ---------------- MAIN GROW ----------------

    def grow(self):
        # 1. limit energii
        if self.consumed_attraction_points >= self.max_attraction_points:
            return

        # 2. brak attraction points
        if not self.attraction_points:
            return

        # 3. najpierw pień
        if not self.trunk_done:
            self.grow_trunk()
            return

        # -------------------------------------------------
        # SETUP ITERACJI – growth radius
        trunk_pos = self.trunk_end.position()
        growth_radius = self.growth_radius()

        # KDTree nodów
        node_positions = np.array([n.position() for n in self.nodes])
        node_tree = KDTree(node_positions)

        # KDTree attraction points
        ap_positions = np.array([ap.position() for ap in self.attraction_points])
        ap_tree = KDTree(ap_positions)

        # tylko attraction points w growth radius
        ap_indices = ap_tree.query_ball_point(trunk_pos, growth_radius)

        # jeśli w zasięgu nic nie ma → brak wzrostu
        if not ap_indices:
            return

        # -------------------------------------------------
        # 4. attraction point -> nearest node
        growth_vectors = {i: [] for i in range(len(self.nodes))}

        for i in ap_indices:
            ap = self.attraction_points[i]

            dist, node_idx = node_tree.query(ap.position())

            if dist < self.influence_radius:
                direction = ap.position() - self.nodes[node_idx].position()
                norm = np.linalg.norm(direction)
                if norm == 0:
                    continue
                growth_vectors[node_idx].append(direction / norm)

        # -------------------------------------------------
        # 5. średni kierunek wzrostu
        new_nodes = []
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

        # brak wzrostu → nie marnuj klatek
        if not new_nodes:
            return

        # -------------------------------------------------
        # 6. dodawanie nodów (bez kolizji)
        for pos, parent_idx in new_nodes:
            if all(
                np.linalg.norm(pos - n.position()) > self.step_size * 0.9
                for n in self.nodes
            ):
                self.add_node(tuple(pos), parent_idx)

        # -------------------------------------------------
        # 7. usuwanie attraction points (kill radius)
        remaining = []
        for ap in self.attraction_points:
            killed = False
            for node in self.nodes:
                if np.linalg.norm(ap.position() - node.position()) < self.kill_radius:
                    self.consumed_attraction_points += 1
                    killed = True
                    break
            if not killed:
                remaining.append(ap)

        self.attraction_points = remaining

    # ---------------- RADIUS ----------------

    def growth_radius(self) -> float:
        x, y, _ = self.trunk_end.position()
        m = self.terrain.moisture(x, y)
        return 2.0 + 4.0 * m
