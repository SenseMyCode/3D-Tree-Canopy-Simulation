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


# --- logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# -------------------------------------------------
# Funkcje pomocnicze do metryk
# -------------------------------------------------

def crown_radius(tree):
    """Średni promień korony (na podstawie convex hull)."""
    hull = canopy_hull(tree)
    if hull is None:
        return 0.0
    center = hull.mean(axis=0)
    radii = np.linalg.norm(hull - center, axis=1)
    return float(radii.mean())


def count_ap_in_growth_radius(tree, attraction_points):
    """Liczba AP w zasięgu wzrostu pnia."""
    trunk_pos = tree.trunk_end.position()
    radius = tree.growth_radius()

    count = 0
    for ap in attraction_points:
        if np.linalg.norm(ap.position() - trunk_pos) <= radius:
            count += 1
    return count


def count_neighboring_trees(tree, all_trees, radius=8.0):
    """
    Liczba innych drzew w danym promieniu od pnia tego drzewa (konkurencja).
    """
    if tree.trunk_end is None:
        return 0
    
    trunk_pos = tree.trunk_end.position()
    count = 0
    
    for other_tree in all_trees:
        if other_tree.tree_id == tree.tree_id or other_tree.trunk_end is None:
            continue
        
        other_pos = other_tree.trunk_end.position()
        dist = np.linalg.norm(np.array(trunk_pos) - np.array(other_pos))
        
        if dist <= radius:
            count += 1
    
    return count


# -------------------------------------------------
# Konfiguracja rozmieszczenia drzew w siatce
# -------------------------------------------------

def create_tree_grid(num_trees_total, spacing=1.5):
    grid_size = math.ceil(math.sqrt(num_trees_total))
    positions = []
    
    for i in range(grid_size):
        for j in range(grid_size):
            if len(positions) < num_trees_total:
                x = i * spacing - (grid_size - 1) * spacing / 2
                y = j * spacing - (grid_size - 1) * spacing / 2
                positions.append((x, y))
    
    return positions[:num_trees_total]


# -------------------------------------------------
# Symulacja lasu z konkurencją
# -------------------------------------------------

def run_simulation(num_trees, seed, max_steps=3000):
    np.random.seed(seed)
    
    logger.info(f"Starting run seed={seed} num_trees={num_trees}")
    
    terrain = Terrain(scale=8.0, height_amp=2.0)
    sun = Sun(position=(30.0, 0.0, 30.0))  # Ustalone położenie słońca
    
    # Generujemy wspólny basen AP dla wszystkich drzew
    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        sun=sun,
        n_candidates=25000,  # Więcej AP dla konkurencji
        area_size=20.0,  # Większa powierzchnia
        trunk_height=4.0,
    )
    
    logger.debug(f"Generated {len(attraction_points)} attraction points")
    
    tree_positions = create_tree_grid(num_trees, spacing=1.5)
    
    trees = []
    for tree_id, (x, y) in enumerate(tree_positions):
        root_z = terrain.height(x, y)
        
        tree = Tree(
            root_position=(x, y, root_z),
            attraction_points=attraction_points,
            terrain=terrain,
            tree_id=tree_id,
            influence_radius=3.0,
            kill_radius=1.0,
            step_size=0.5,
        )
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
            
            if (stagnant_counts[tree.tree_id] > 500 or 
                tree.consumed_attraction_points >= tree.max_attraction_points):
                active_trees.discard(tree.tree_id)
        
        free_aps = [ap for ap in attraction_points if ap.claimed_by is None]
        if not free_aps:
            logger.info(f"Run seed={seed}: no free AP left at step={steps}")
            break
    
    records = []
    for tree in trees:
        x, y, _ = tree.nodes[0].position()
        
        h = tree.height()
        cv = crown_volume(tree)
        cr = crown_radius(tree)
        ar = asymmetry_radius(tree)
        consumed = int(tree.consumed_attraction_points)
        ap_in_radius = count_ap_in_growth_radius(tree, attraction_points)
        neighbors = count_neighboring_trees(tree, trees, radius=8.0)
        
        records.append({
            "seed": int(seed),
            "num_trees": num_trees,
            "tree_id": tree.tree_id,
            "x": float(x),
            "y": float(y),
            "steps": int(steps),
            "height": float(h),
            "crown_volume": float(cv),
            "crown_radius": float(cr),
            "asymmetry_radius": float(ar),
            "consumed_AP": consumed,
            "AP_in_growth_radius": int(ap_in_radius),
            "neighboring_trees": neighbors,
        })
    
    logger.info(
        f"Finished run seed={seed} num_trees={num_trees}: steps={steps}"
    )
    
    return records


# -------------------------------------------------
# GŁÓWNA FUNKCJA
# -------------------------------------------------

def main():
    tree_counts = [1, 4, 9, 16]
    
    trials_per_count = 5  # Liczba powtórzeń dla każej konfiguracji
    
    results = []
    
    total_runs = len(tree_counts) * trials_per_count
    logger.info(f"Running {total_runs} simulations across {tree_counts}")
    
    run_id = 0
    with tqdm(total=total_runs, desc="Exp3 runs") as pbar:
        for tree_count in tree_counts:
            for trial in range(trials_per_count):
                run_id += 1
                seed = 3000 + run_id
                
                tree_records = run_simulation(tree_count, seed)
                results.extend(tree_records)
                
                pbar.update(1)
    
    df = pd.DataFrame(results)
    
    out_path = "exp3_results.csv"
    df.to_csv(out_path, index=False)
    logger.info(f"Full results written to {out_path}")
    
    agg = df.groupby("num_trees").agg(
        mean_height=("height", "mean"),
        std_height=("height", "std"),
        mean_crown_radius=("crown_radius", "mean"),
        std_crown_radius=("crown_radius", "std"),
        mean_crown_volume=("crown_volume", "mean"),
        std_crown_volume=("crown_volume", "std"),
        mean_asymmetry=("asymmetry_radius", "mean"),
        std_asymmetry=("asymmetry_radius", "std"),
        mean_consumed_AP=("consumed_AP", "mean"),
        mean_neighbors=("neighboring_trees", "mean"),
        runs=("seed", "count"),
    ).reset_index()
    
    summary_path = "exp3_summary.csv"
    agg.to_csv(summary_path, index=False)
    logger.info(f"Summary written to {summary_path}")
    
    print("\n" + "="*70)
    print("EXP3 — wpływ konkurencji drzew na morfologię korony")
    print("="*70)
    print(agg.to_string(index=False))
    print("="*70)
    print(f"\nWyniki zapisane:")
    print(f"  - Pełne dane:  {out_path}")
    print(f"  - Podsumowanie: {summary_path}")


if __name__ == "__main__":
    main()
