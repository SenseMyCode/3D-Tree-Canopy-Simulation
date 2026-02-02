from vispy import app
import matplotlib.pyplot as plt

from environment.terrain import Terrain
from environment.sun import Sun

from structures.tree import Tree
from structures.forest import Forest
from structures.attraction_point import generate_attraction_points_from_terrain

from visualization.vispy_scene import TreeScene


def main_intro():
    terrain = Terrain(scale=8.0, height_amp=2.0)
    sun = Sun(position=(25.0, -20.0, 30.0))

    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        sun=sun,
        n_candidates=15000,
        area_size=12.0,
        trunk_height=4.0
    )

    x, y = 0.0, 0.0
    root_z = terrain.height(x, y)

    tree = Tree(
        root_position=(x, y, root_z),
        attraction_points=attraction_points,
        terrain=terrain,
        tree_id=0,
        influence_radius=3.0,
        kill_radius=1.0,
        step_size=0.5
    )

    forest = Forest([tree], attraction_points)

    print("Intro: wzrost jednego drzewa")
    TreeScene(forest, terrain, sun, debug=True)
    app.run()


def main():
    terrain = Terrain(scale=8.0, height_amp=2.0)
    sun = Sun(position=(25.0, -20.0, 30.0))

    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        sun=sun,
        n_candidates=20000,   
        area_size=15.0,
        trunk_height=4.0
    )

    trees = []
    positions = [
        (-3, -3), (-3, -2), (-3, -1), (-3, 3),
        (2, -3), (2, -2), (2, -1), (2, 3),
        (5, -3), (5, -2), (5, -1), (5, 3),
    ]

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

    TreeScene(forest, terrain, sun)
    app.run()

    # ---- ANALIZA ----
    """plot_dem(terrain)
    plot_seed_points(attraction_points)
    plot_canopy_footprints(forest)
    plt.show()

    run_environment_stats(forest, terrain)

    output_path = "crown_metrics.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("TREE CROWN METRICS\n")
        f.write("===================\n\n")

        for tree in forest.trees:
            metrics = crown_metrics(tree)
            f.write(f"Tree ID: {tree.tree_id}\n")
            f.write("-------------------\n")
            for key, value in metrics.items():
                f.write(f"{key}: {value:.4f}\n")
            f.write("\n")

    print(f"Metryki zapisane do pliku: {output_path}")"""


if __name__ == "__main__":
    main_intro()
    main()
