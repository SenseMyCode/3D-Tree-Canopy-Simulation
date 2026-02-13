import numpy as np
import pandas as pd
from tqdm import tqdm
import logging

from environment.terrain import Terrain
from environment.sun import Sun
from structures.attraction_point import generate_attraction_points_from_terrain
from structures.tree import Tree
from structures.forest import Forest

from analysis.crown_metrics import crown_volume, asymmetry_radius
from analysis.canopy import canopy_hull


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Pomocnicze metryki
# ------------------------------------------------------------
def crown_radius(tree):
    hull = canopy_hull(tree)
    if hull is None:
        return 0.0
    center = hull.mean(axis=0)
    radii = np.linalg.norm(hull - center, axis=1)
    return float(radii.mean())


def count_ap_in_growth_radius(tree, attraction_points):
    trunk_pos = tree.trunk_end.position()
    radius = tree.growth_radius()

    count = 0
    for ap in attraction_points:
        if np.linalg.norm(ap.position() - trunk_pos) <= radius:
            count += 1
    return count


# ------------------------------------------------------------
# Siatka pozycji drzew
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
# Symulacja lasu z konkurencją
# ------------------------------------------------------------
def run_simulation(trunk_heights, seed, max_steps=3000):
    np.random.seed(seed)

    logger.info(f"Starting run seed={seed} trunk_heights={trunk_heights}")

    terrain = Terrain(scale=8.0, height_amp=2.0)
    sun = Sun(position=(30.0, 0.0, 30.0))

    FIXED_AP_TRUNK_HEIGHT = 4.0

    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        sun=sun,
        n_candidates=25000,
        area_size=20.0,
        trunk_height=FIXED_AP_TRUNK_HEIGHT,
    )

    positions = create_tree_grid(len(trunk_heights), spacing=1.0)
    TREE_OFFSET = (8.0, 0.0)

    trees = []

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
            logger.info(f"Run seed={seed}: no free AP left at step={steps}")
            break

    records = []

    for tree, th in zip(trees, trunk_heights):
        h = tree.height()
        cv = crown_volume(tree)
        cr = crown_radius(tree)
        ar = asymmetry_radius(tree)
        consumed = int(tree.consumed_attraction_points)
        ap_in_radius = count_ap_in_growth_radius(tree, attraction_points)

        records.append({
            "seed": int(seed),
            "tree_id": tree.tree_id,
            "trunk_height": float(th),
            "steps": int(steps),
            "height": float(h),
            "crown_volume": float(cv),
            "crown_radius": float(cr),
            "asymmetry_radius": float(ar),
            "consumed_AP": consumed,
            "AP_in_growth_radius": int(ap_in_radius),
        })

    logger.info(f"Finished run seed={seed}: steps={steps}")
    return records


# ------------------------------------------------------------
# Główna funkcja
# ------------------------------------------------------------
def main():
    trunk_heights = [1.0, 2.0, 4.0, 6.0, 8.0, 10.0]
    trials_per_run = 6

    results = []

    total_runs = trials_per_run
    logger.info(f"Running {total_runs} simulations (each run = full forest)")

    run_id = 0
    with tqdm(total=total_runs, desc="Exp5 runs") as pbar:
        for t in range(trials_per_run):
            run_id += 1
            seed = 5000 + run_id
            recs = run_simulation(trunk_heights, seed)
            results.extend(recs)
            pbar.update(1)

    df = pd.DataFrame(results)

    out_path = "exp5_results.csv"
    df.to_csv(out_path, index=False)

    agg = df.groupby("trunk_height").agg(
        mean_height=("height", "mean"),
        mean_crown_radius=("crown_radius", "mean"),
        mean_crown_volume=("crown_volume", "mean"),
        mean_asymmetry=("asymmetry_radius", "mean"),
        mean_consumed_AP=("consumed_AP", "mean"),
        runs=("tree_id", "count")
    ).reset_index()

    summary_path = "exp5_summary.csv"
    agg.to_csv(summary_path, index=False)

    print(f"Results written to {out_path} and summary to {summary_path}")


if __name__ == "__main__":
    main()
