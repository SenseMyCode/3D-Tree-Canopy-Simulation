# Wizualizacja eksperymentu:
# 2 drzewa na tej samej wysokości, ale z różną liczbą attraction points.
# Cel: zobaczyć różnice w wysokości i koronie przy różnej dostępności zasobów.

import numpy as np
from vispy import app

from environment.terrain import Terrain
from environment.sun import Sun
from structures.tree import Tree
from structures.forest import Forest
from structures.attraction_point import AttractionPoint
from visualization.vispy_scene import TreeScene


# ------------------------------------------------------------
# Sztuczne chmury attraction points
# ------------------------------------------------------------
def generate_custom_ap(terrain):
    points = []

    center_sun = (0.0, -12.0)
    for _ in range(3500):
        x = np.random.normal(center_sun[0], 3.0)
        y = np.random.normal(center_sun[1], 3.0)
        ground_z = terrain.height(x, y)
        z = ground_z + 4.0 + np.random.uniform(1.0, 10.0)
        points.append(AttractionPoint(x, y, z))

    center_shadow = (0.0, 12.0)
    for _ in range(700):
        x = np.random.normal(center_shadow[0], 3.0)
        y = np.random.normal(center_shadow[1], 3.0)
        ground_z = terrain.height(x, y)
        z = ground_z + 4.0 + np.random.uniform(1.0, 10.0)
        points.append(AttractionPoint(x, y, z))

    return points


# ------------------------------------------------------------
# GŁÓWNY PROGRAM Z WIZUALIZACJĄ
# ------------------------------------------------------------
def main():
    print("\n=== WIZUALIZACJA: KOMPENSACJA WZROSTU ===")

    np.random.seed(42)

    terrain = Terrain(scale=8.0, height_amp=2.0)
    sun = Sun(position=(25.0, -20.0, 30.0))

    attraction_points = generate_custom_ap(terrain)

    pos_sun = (0.0, -12.0)
    pos_shadow = (0.0, 12.0)

    trees = []
    for i, (x, y) in enumerate([pos_sun, pos_shadow]):
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

    scene = TreeScene(forest, terrain, sun, debug=True)

    def update(event):
        forest.grow()

        for t in forest.trees:
            print(f"[Tree {t.tree_id}] nodes={len(t.nodes)}, consumed={t.consumed_attraction_points}")

        scene.scene_dirty = True
        scene.update()

    timer = app.Timer(interval=0.03, connect=update, start=True)

    app.run()


if __name__ == "__main__":
    main()
