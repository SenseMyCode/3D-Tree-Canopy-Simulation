from structures.tree import Tree
from structures.attraction_point import generate_attraction_points_from_terrain
from visualization.vispy_scene import TreeScene
from vispy import app
from environment.terrain import Terrain

def main():
    terrain = Terrain(scale=8.0, height_amp=2.0)

    trunk_height = 2.0  # wysokość pnia
    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        n_candidates=8000,
        area_size=15.0,
        trunk_height=4.0
    )

    root_z = terrain.height(0, 0)

    tree = Tree(
        root_position=(0, 0, root_z),
        attraction_points=attraction_points,
        terrain=terrain,
        influence_radius=3.0,
        kill_radius=1.0,
        step_size=0.5
    )

    TreeScene(tree, terrain)
    app.run()


if __name__ == "__main__":
    main()
