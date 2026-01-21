from structures.node import Node
from scipy.spatial import KDTree
import numpy as np

class Tree:
    def __init__(
        self,
        root_position: tuple[float, float, float],
        attraction_points: list,
        terrain,
        tree_id: int,
        influence_radius: float = 2.0,
        kill_radius: float = 1.0,
        step_size: float = 0.5,
    ):
        self.tree_id = tree_id

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

        root = Node(*root_position, parent=None)
        self.nodes.append(root)

        root_x, root_y, _ = root_position
        root_moisture = self.terrain.moisture(root_x, root_y)

        self.max_attraction_points = int(30 + 200 * root_moisture)
        self.consumed_attraction_points = 0

        self.beta = 0.05   # nachylenie terenu
        self.gamma = 0.03 # wilgotność


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
        if self.consumed_attraction_points >= self.max_attraction_points:
            return

        if not self.attraction_points:
            return

        if not self.trunk_done:
            self.grow_trunk()
            return

        trunk_pos = self.trunk_end.position()
        growth_radius = self.growth_radius()

        node_positions = np.array([n.position() for n in self.nodes])
        node_tree = KDTree(node_positions)

        free_aps = [
            ap for ap in self.attraction_points
            if ap.claimed_by is None or ap.claimed_by == self.tree_id
        ]

        if not free_aps:
            return

        ap_positions = np.array([ap.position() for ap in free_aps])
        ap_tree = KDTree(ap_positions)

        ap_indices = ap_tree.query_ball_point(trunk_pos, growth_radius)
        if not ap_indices:
            return

        growth_vectors = {i: [] for i in range(len(self.nodes))}

        for i in ap_indices:
            ap = free_aps[i]   

            dist, node_idx = node_tree.query(ap.position())
            if dist < self.influence_radius:
                direction = ap.position() - self.nodes[node_idx].position()
                norm = np.linalg.norm(direction)
                if norm > 0:
                    growth_vectors[node_idx].append(direction / norm)

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

        for pos, parent_idx in new_nodes:
            if all(
                np.linalg.norm(pos - n.position()) > self.step_size * 0.9
                for n in self.nodes
            ):
                self.add_node(tuple(pos), parent_idx)

        for ap in self.attraction_points:
            if ap.claimed_by is not None:
                continue

            for node in self.nodes:
                if np.linalg.norm(ap.position() - node.position()) < self.kill_radius:
                    ap.claimed_by = self.tree_id
                    self.consumed_attraction_points += 1
                    break

    # ---------------- RADIUS ----------------

    def growth_radius(self) -> float:
        x, y, _ = self.trunk_end.position()
        m = self.terrain.moisture(x, y)  # 0.05..1.0

        min_radius = 2.0
        max_radius = 8.0  # większa różnica
        alpha = 1.0         # pełny wpływ wilgotności

        return min_radius + (max_radius - min_radius) * (m*0.8) * alpha


