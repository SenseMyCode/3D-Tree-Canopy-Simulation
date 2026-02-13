import math
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


def run_simulation(sun_pos, seed, max_steps=3000):
    np.random.seed(seed)

    logger.info(f"Starting run seed={seed} sun={sun_pos}")

    terrain = Terrain(scale=8.0, height_amp=2.0)
    sun = Sun(position=sun_pos)

    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        sun=sun,
        n_candidates=15000,
        area_size=12.0,
        trunk_height=4.0,
    )

    logger.debug(f"Generated {len(attraction_points)} attraction points")

    x, y = 0.0, 0.0
    root_z = terrain.height(x, y)

    tree = Tree(
        root_position=(x, y, root_z),
        attraction_points=attraction_points,
        terrain=terrain,
        tree_id=0,
        influence_radius=3.0,
        kill_radius=1.0,
        step_size=0.5,
    )

    forest = Forest([tree], attraction_points)

    steps = 0
    stagnant = 0
    last_node_count = len(tree.nodes)

    while steps < max_steps:
        forest.grow()
        steps += 1

        node_count = len(tree.nodes)
        if node_count == last_node_count:
            stagnant += 1
        else:
            stagnant = 0
            last_node_count = node_count

        if stagnant > 500:
            break

        if tree.consumed_attraction_points >= tree.max_attraction_points:
            break

        free_aps = [ap for ap in attraction_points if ap.claimed_by is None]
        if not free_aps:
            logger.info(f"Run seed={seed}: no free AP left at step={steps}")
            break

    # Metryki
    h = tree.height()
    cv = crown_volume(tree)
    cr = crown_radius(tree)
    ar = asymmetry_radius(tree)
    consumed = int(tree.consumed_attraction_points)
    ap_in_radius = count_ap_in_growth_radius(tree, attraction_points)

    logger.info(
        f"Finished run seed={seed}: steps={steps}, nodes={len(tree.nodes)}, consumed_AP={consumed}"
    )

    return {
        "seed": int(seed),
        "sun_x": float(sun_pos[0]),
        "sun_y": float(sun_pos[1]),
        "sun_z": float(sun_pos[2]),
        "steps": int(steps),
        "height": float(h),
        "crown_volume": float(cv),
        "crown_radius": float(cr),
        "asymmetry_radius": float(ar),
        "consumed_AP": consumed,
        "AP_in_growth_radius": int(ap_in_radius),
    }


def main():
    azimuths = np.linspace(0, 2 * math.pi, 8, endpoint=False)  # 8 kierunków
    radii = [30.0]  # odległość słońca od środka
    heights = [10.0, 30.0, 60.0]  # różne wysokości słońca

    trials_per_position = 5

    params = []
    for r in radii:
        for h in heights:
            for a in azimuths:
                x = r * math.cos(a)
                y = r * math.sin(a)
                z = h
                params.append((x, y, z))

    results = []

    total_runs = len(params) * trials_per_position
    logger.info(f"Running {total_runs} simulations ({len(params)} positions x {trials_per_position} trials)")

    run_id = 0
    with tqdm(total=total_runs, desc="Exp2 runs") as pbar:
        for pos in params:
            for t in range(trials_per_position):
                run_id += 1
                seed = 1000 + run_id
                res = run_simulation(pos, seed)
                results.append(res)
                pbar.update(1)

    df = pd.DataFrame(results)

    out_path = "exp2_results.csv"
    df.to_csv(out_path, index=False)

    agg = df.groupby(["sun_x", "sun_y", "sun_z"]).agg(
        mean_height=("height", "mean"),
        mean_crown_radius=("crown_radius", "mean"),
        mean_crown_volume=("crown_volume", "mean"),
        mean_asymmetry=("asymmetry_radius", "mean"),
        runs=("seed", "count")
    ).reset_index()

    summary_path = "exp2_summary.csv"
    agg.to_csv(summary_path, index=False)

    print(f"Results written to {out_path} and summary to {summary_path}")


if __name__ == "__main__":
    main()
