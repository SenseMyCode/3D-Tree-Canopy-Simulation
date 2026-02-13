import logging
import numpy as np
from vispy import app

from environment.terrain import Terrain
from environment.sun import Sun
from structures.attraction_point import generate_attraction_points_from_terrain
from structures.tree import Tree
from structures.forest import Forest
from visualization.vispy_scene import TreeScene


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Tworzenie siatki pozycji drzew
# ------------------------------------------------------------
def create_tree_grid(num_trees, spacing=1.0):
    grid_size = int(np.ceil(np.sqrt(num_trees)))
    positions = []

    for i in range(grid_size):
        for j in range(grid_size):
            if len(positions) < num_trees:
                x = i * spacing - (grid_size - 1) * spacing / 2
                y = j * spacing - (grid_size - 1) * spacing / 2
                positions.append((x, y))

    return positions


# ------------------------------------------------------------
# Symulacja lasu z różnymi trunk_height
# ------------------------------------------------------------
def run_simulation_headless(trunk_heights, seed, max_steps=3000):
    np.random.seed(seed)

    terrain = Terrain(scale=8.0, height_amp=2.0)
    sun = Sun(position=(30.0, 0.0, 30.0))

    logger.info(f"Symulacja lasu: trunk_heights={trunk_heights} (seed={seed})")

    # --------------------------------------------------------
    # Attraction Points generujemy ZAWSZE tak samo
    # --------------------------------------------------------
    FIXED_AP_TRUNK_HEIGHT = 4.0

    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        sun=sun,
        n_candidates=25000,
        area_size=20.0,
        trunk_height=FIXED_AP_TRUNK_HEIGHT,
    )

    # ------------------------------------------------------------
    # Tworzymy drzewa w siatce
    # ------------------------------------------------------------
    positions = create_tree_grid(len(trunk_heights), spacing=1.0)
    trees = []

    TREE_OFFSET = (8.0, 0.0)   # przesunięcie drzew w stronę większej chmury AP

    for tree_id, ((x, y), th) in enumerate(zip(positions, trunk_heights)):
        x_shifted = x + TREE_OFFSET[0]
        y_shifted = y + TREE_OFFSET[1]

        root_z = terrain.height(x_shifted, y_shifted)

        tree = Tree(
            root_position=(x_shifted, y_shifted, root_z),
            attraction_points=attraction_points,
            terrain=terrain,
            tree_id=tree_id,
            influence_radius=3.0,
            kill_radius=1.0,
            step_size=0.5,
        )

        tree.trunk_height = float(th)
        trees.append(tree)


    forest = Forest(trees, attraction_points)

    # --------------------------------------------------------
    # Pętla wzrostu
    # --------------------------------------------------------
    steps = 0
    stagnant_counts = {tree.tree_id: 0 for tree in trees}
    last_node_counts = {tree.tree_id: len(tree.nodes) for tree in trees}
    active_trees = set(tree.tree_id for tree in trees)

    while steps < max_steps and active_trees:
        forest.grow()
        steps += 1

        for tree in trees:
            node_count = len(tree.nodes)
            if node_count == last_node_counts[tree.tree_id]:
                stagnant_counts[tree.tree_id] += 1
            else:
                stagnant_counts[tree.tree_id] = 0
                last_node_counts[tree.tree_id] = node_count

            if stagnant_counts[tree.tree_id] > 500:
                active_trees.discard(tree.tree_id)

            if tree.consumed_attraction_points >= tree.max_attraction_points:
                active_trees.discard(tree.tree_id)

        free_aps = [ap for ap in attraction_points if ap.claimed_by is None]
        if not free_aps:
            logger.info("  Koniec dostępnych AP")
            break

    logger.info(f"  Koniec: steps={steps}, active_trees={len(active_trees)}")
    return forest, terrain, sun


# ------------------------------------------------------------
# Główna funkcja wizualizacji
# ------------------------------------------------------------
def main():
    # Dodane drzewo o trunk_height = 8.0
    trunk_heights = [1.0, 2.0, 4.0, 6.0, 8.0, 10.0]

    seed = 9000
    forest, terrain, sun = run_simulation_headless(trunk_heights, seed)

    print("\nWizualizacja lasu — różne wysokości pnia, wspólna konkurencja\n")
    print(f"Trunk heights: {trunk_heights}")

    scene = TreeScene(forest, terrain, sun, debug=True)
    app.run()


if __name__ == "__main__":
    main()
