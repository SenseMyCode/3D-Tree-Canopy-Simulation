from structures.tree import Tree
from structures.attraction_point import generate_attraction_points_from_terrain
from visualization.vispy_scene import TreeScene
from vispy import app
from environment.terrain import Terrain
from structures.forest import Forest
from analysis.plots_2d import (
    plot_dem,
    plot_seed_points,
    plot_canopy_footprints
)
from analysis.crown_metrics import crown_metrics
import matplotlib.pyplot as plt


def main():
    # ---------------- TERRAIN ----------------
    terrain = Terrain(scale=8.0, height_amp=2.0)

    # ---------------- ATTRACTION POINTS ----------------
    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        n_candidates=8000,
        area_size=15.0,
        trunk_height=4.0
    )

    # ---------------- TREES ----------------
    trees = []
    positions = [(-3, 0), (0, 0), (3, 1), (7, 1)]

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

    # ---------------- VISUALIZATION ----------------
    TreeScene(forest, terrain)
    app.run()  # <- symulacja wzrostu

    # ---------------- 2D PLOTS ----------------
    plot_dem(terrain)
    plot_seed_points(attraction_points)
    plot_canopy_footprints(forest)
    plt.show()

    # ---------------- METRICS OUTPUT ----------------
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

    print(f" Metryki zapisane do pliku: {output_path}")


if __name__ == "__main__":
    main()
