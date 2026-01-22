import numpy as np

class ForestState:
    def __init__(self, forest):
        self.forest = forest

    def tree_nodes(self):
        return {
            tree.tree_id: np.array([n.position() for n in tree.nodes])
            for tree in self.forest.trees
        }

    def tree_edges(self):
        result = {}
        for tree in self.forest.trees:
            edges = []
            for i, j in tree.edges:
                edges.append(tree.nodes[i].position())
                edges.append(tree.nodes[j].position())
            result[tree.tree_id] = np.array(edges)
        return result

    def tree_heights(self):
        return {
            tree.tree_id: max(n.z for n in tree.nodes)
            for tree in self.forest.trees
        }

    def attraction_points_2d(self):
        xy = np.array([[p.x, p.y] for p in self.forest.attraction_points])
        owner = np.array([
            -1 if p.claimed_by is None else p.claimed_by
            for p in self.forest.attraction_points
        ])
        return xy, owner
