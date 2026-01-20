from structures.tree import Tree
from structures.attraction_point import generate_attraction_points_from_terrain
from visualization.vispy_scene import TreeScene
from vispy import app
from environment.terrain import Terrain
from structures.forest import Forest

def main():
    terrain = Terrain(scale=8.0, height_amp=2.0)

    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        n_candidates=8000,
        area_size=15.0,
        trunk_height=4.0
    )

    trees = []
    positions = [(-3, 0), (0, 0), (3, 1)]

    for i, (x, y) in enumerate(positions):
        root_z = terrain.height(x, y)
        tree = Tree(
            root_position=(x, y, root_z),
            attraction_points=attraction_points,
            terrain=terrain,
            tree_id=i,
            influence_radius=3.0,
            kill_radius=1.0,
            step_size=0.5
        )
        trees.append(tree)

    forest = Forest(trees, attraction_points)
    TreeScene(forest, terrain)

    app.run()

if __name__ == "__main__":
    main()
