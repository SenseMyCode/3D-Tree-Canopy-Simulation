from structures.node import Node

class Tree:
    def __init__(self, root_position: tuple[float, float, float]):
        self.nodes: list[Node] = []
        self.edges: list[tuple[int, int]] = []

        root = Node(*root_position, parent=None)
        self.nodes.append(root)

    def add_node(self, position: tuple[float, float, float], parent_index: int):
        node = Node(*position, parent=self.nodes[parent_index])
        self.nodes.append(node)
        self.edges.append((parent_index, len(self.nodes) - 1))