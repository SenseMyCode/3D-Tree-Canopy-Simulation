class Forest:
    def __init__(self, trees, attraction_points):
        self.trees = trees
        self.attraction_points = attraction_points

    def grow(self, steps_per_tick: int = 1):
        for _ in range(steps_per_tick):
            for tree in self.trees:
                tree.grow()
