# exp_visual_shadow_compensation.py
#
# Wizualizacja eksperymentu:
# 2 drzewa na tej samej wysokości, ale z różną liczbą attraction points.
# Po zamknięciu okna wypisuje crown_radius, height, crown_volume, moisture
# oraz liczbę attraction points w growth radius.

import numpy as np
from vispy import app

from environment.terrain import Terrain
from environment.sun import Sun
from structures.tree import Tree
from structures.forest import Forest
from structures.attraction_point import AttractionPoint
from visualization.vispy_scene import TreeScene

from analysis.crown_metrics import crown_metrics
from analysis.canopy import canopy_hull


# ------------------------------------------------------------
# Promień korony
# ------------------------------------------------------------
def crown_radius(tree):
    hull = canopy_hull(tree)
    if hull is None:
        return 0.0
    center = hull.mean(axis=0)
    radii = np.linalg.norm(hull - center, axis=1)
    return radii.mean()


# ------------------------------------------------------------
# Liczenie AP w growth radius
# ------------------------------------------------------------
def count_ap_in_growth_radius(tree, attraction_points):
    trunk_pos = tree.trunk_end.position()
    radius = tree.growth_radius()

    count = 0
    for ap in attraction_points:
        if np.linalg.norm(ap.position() - trunk_pos) <= radius:
            count += 1
    return count


# ------------------------------------------------------------
# Sztuczne chmury attraction points
# ------------------------------------------------------------
def generate_custom_ap(terrain):
    points = []

    # DRZEWO SŁONECZNE — DUŻO AP
    center_sun = (0.0, -12.0)
    for _ in range(3500):
        x = np.random.normal(center_sun[0], 3.0)
        y = np.random.normal(center_sun[1], 3.0)
        ground_z = terrain.height(x, y)
        z = ground_z + 4.0 + np.random.uniform(1.0, 10.0)
        points.append(AttractionPoint(x, y, z))

    # DRZEWO CIENIOWE — MAŁO AP
    center_shadow = (0.0, 12.0)
    for _ in range(700):
        x = np.random.normal(center_shadow[0], 3.0)
        y = np.random.normal(center_shadow[1], 3.0)
        ground_z = terrain.height(x, y)
        z = ground_z + 4.0 + np.random.uniform(1.0, 10.0)
        points.append(AttractionPoint(x, y, z))

    return points


# ------------------------------------------------------------
# DataFrame z metrykami
# ------------------------------------------------------------
def build_tree_dataframe(forest, terrain, attraction_points):
    records = []
    for tree in forest.trees:
        metrics = crown_metrics(tree)
        x, y, _ = tree.nodes[0].position()

        records.append({
            "tree_id": tree.tree_id,
            "x": x,
            "y": y,
            "height": metrics["height"],
            "crown_radius": crown_radius(tree),
            "crown_volume": metrics["crown_volume"],
            "moisture": terrain.moisture(x, y),
            "AP_in_growth_radius": count_ap_in_growth_radius(tree, attraction_points),
        })

    import pandas as pd
    return pd.DataFrame(records)


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

    step_counter = 0

    def update(event):
        nonlocal step_counter
        forest.grow()
        step_counter += 1

        scene.scene_dirty = True
        scene.update()

    timer = app.Timer(interval=0.03, connect=update, start=True)

    # uruchom wizualizację
    app.run()

    # po zamknięciu okna:
    print("\n=== WYNIKI KOŃCOWE ===")
    df = build_tree_dataframe(forest, terrain, attraction_points)
    print(df)

if __name__ == "__main__":
    main()
