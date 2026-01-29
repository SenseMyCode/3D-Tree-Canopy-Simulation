from __future__ import annotations

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

        # --- struktura drzewa ---
        self.nodes: list[Node] = []
        self.edges: list[tuple[int, int]] = []

        # attraction points współdzielone z lasem
        self.attraction_points = attraction_points

        self.influence_radius = influence_radius
        self.kill_radius = kill_radius
        self.step_size = step_size

        self.trunk_height = 4.0
        self.trunk_done = False
        self.trunk_end: Node | None = None

        self.terrain = terrain

        # --- korzeń ---
        root = Node(*root_position, parent=None)
        self.nodes.append(root)

        # CACHE: pozycje node’ów + KDTree
        self._node_positions = np.array([root.position()], dtype=float)
        self._node_tree = KDTree(self._node_positions)

        # --- parametry zależne od wilgotności ---
        root_x, root_y, _ = root_position
        root_moisture = self.terrain.moisture(root_x, root_y)

        self.max_attraction_points = int(30 + 200 * root_moisture)
        self.consumed_attraction_points = 0

        self.beta = 0.05   # nachylenie terenu (na razie nieużywane)
        self.gamma = 0.03  # wilgotność (na razie nieużywane)

    # -------------------------------------------------
    # POMOCNICZE

    def _rebuild_node_tree(self) -> None:
        """Aktualizuje KDTree po dodaniu nowych node’ów."""
        self._node_positions = np.array(
            [n.position() for n in self.nodes],
            dtype=float
        )
        self._node_tree = KDTree(self._node_positions)

    def add_node(self, position, parent_index: int):
        node = Node(*position, parent=parent_index)
        self.nodes.append(node)
        self.edges.append((parent_index, len(self.nodes) - 1))

        # po dodaniu node’a aktualizujemy KDTree
        self._rebuild_node_tree()

    # ---------------- TRUNK ----------------

    def grow_trunk(self):
        direction = np.array([0.0, 0.0, 1.0], dtype=float)
        last_idx = len(self.nodes) - 1
        last_node = self.nodes[last_idx]

        new_pos = last_node.position() + direction * self.step_size
        self.add_node(tuple(new_pos), last_idx)

        if new_pos[2] >= self.nodes[0].z + self.trunk_height:
            self.trunk_done = True
            self.trunk_end = self.nodes[-1]

    # ---------------- MAIN GROW ----------------

    def grow(self):
        # limit na liczbę "zjedzonych" attraction points
        if self.consumed_attraction_points >= self.max_attraction_points:
            return

        if not self.attraction_points:
            return

        # najpierw rośnie pień
        if not self.trunk_done:
            self.grow_trunk()
            return

        trunk_pos = self.trunk_end.position()
        growth_radius = self.growth_radius()

        # używamy zcache’owanego KDTree node’ów
        node_tree = self._node_tree

        # bierzemy tylko AP, które są wolne lub przypisane do tego drzewa
        free_aps = [
            ap for ap in self.attraction_points
            if ap.claimed_by is None or ap.claimed_by == self.tree_id
        ]

        if not free_aps:
            return

        # pozycje AP tylko dla wolnych punktów
        ap_positions = np.array([ap.position() for ap in free_aps], dtype=float)
        ap_tree = KDTree(ap_positions)

        # szukamy AP w zasięgu korony
        ap_indices = ap_tree.query_ball_point(trunk_pos, growth_radius)
        if not ap_indices:
            return

        growth_vectors: dict[int, list[np.ndarray]] = {i: [] for i in range(len(self.nodes))}

        # dla każdego AP szukamy najbliższego node’a
        for i in ap_indices:
            ap = free_aps[i]

            dist, node_idx = node_tree.query(ap.position())
            if dist < self.influence_radius:
                direction = ap.position() - self.nodes[node_idx].position()
                norm = np.linalg.norm(direction)
                if norm > 0:
                    growth_vectors[node_idx].append(direction / norm)

        new_nodes: list[tuple[np.ndarray, int]] = []
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

        # dodajemy nowe node’y, pilnując minimalnego dystansu
        for pos, parent_idx in new_nodes:
            if all(
                np.linalg.norm(pos - n.position()) > self.step_size * 0.9
                for n in self.nodes
            ):
                self.add_node(tuple(pos), parent_idx)

        # zabijamy AP w kill_radius
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
        max_radius = 8.0

        return min_radius + (max_radius - min_radius) * (m * 0.8) 

    # ---------------- HEIGHT ----------------

    def height(self) -> float:
        return max(n.z for n in self.nodes)
