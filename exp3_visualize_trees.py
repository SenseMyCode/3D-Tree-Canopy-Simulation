"""
Wizualizacja eksperymentu 3 — interaktywne wizualizacje lasów z konkurencją

Uruchamia symulacje lasów z różną liczbą drzew rozmieszczonych w siatce,
następnie wyświetla każdy las w osobnym oknie TreeScene.

Uruchomienie:
    python exp3_visualize_trees.py

Zamknij okno, aby przejść do następnego lasu.
"""

import math
import numpy as np
import logging
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


# -------------------------------------------------
# Pomocnicze funkcje
# -------------------------------------------------

def create_tree_grid(num_trees_total, spacing=1.5):
    """Tworzy sieć drzew w siatce kwadratowej."""
    grid_size = math.ceil(math.sqrt(num_trees_total))
    positions = []
    
    for i in range(grid_size):
        for j in range(grid_size):
            if len(positions) < num_trees_total:
                x = i * spacing - (grid_size - 1) * spacing / 2
                y = j * spacing - (grid_size - 1) * spacing / 2
                positions.append((x, y))
    
    return positions[:num_trees_total]


def run_simulation_headless(num_trees, seed, max_steps=3000):
    """Uruchomienie symulacji lasu bez GUI."""
    np.random.seed(seed)

    terrain = Terrain(scale=8.0, height_amp=2.0)
    sun = Sun(position=(30.0, 0.0, 30.0))  # Ustalone położenie słońca

    logger.info(f"Symulacja: num_trees={num_trees} (seed={seed})")

    # Generujemy wspólny basen AP dla wszystkich drzew
    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        sun=sun,
        n_candidates=25000,
        area_size=20.0,
        trunk_height=4.0,
    )

    logger.debug(f"Generated {len(attraction_points)} attraction points")

    # Umieszczamy drzewa w siatce
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

    # Symulacja bez GUI
    steps = 0
    stagnant_counts = {tree.tree_id: 0 for tree in trees}
    last_node_counts = {tree.tree_id: len(tree.nodes) for tree in trees}
    active_trees = set(tree.tree_id for tree in trees)

    while steps < max_steps and active_trees:
        forest.grow()
        steps += 1

        # Warunek zatrzymania
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

        # Jeśli żadnych dostępnych AP
        free_aps = [ap for ap in attraction_points if ap.claimed_by is None]
        if not free_aps:
            logger.info(f"  Koniec dostępnych AP (step={steps})")
            break

    # Statystyki
    total_height = sum(tree.height() for tree in trees)
    avg_height = total_height / len(trees) if trees else 0.0
    total_nodes = sum(len(tree.nodes) for tree in trees)

    logger.info(
        f"  Koniec: steps={steps}, trees={len(trees)}, total_nodes={total_nodes}, "
        f"avg_height={avg_height:.2f}"
    )

    return forest, terrain, sun


def main():
    """Główna funkcja."""
    
    # Liczby drzew do wizualizacji
    tree_counts = [1, 4, 9, 16]
    
    results = []

    print("\n" + "="*70)
    print("WIZUALIZACJA EKSPERYMENTU 3 — konkurencja drzew w lesie")
    print("="*70 + "\n")

    for i, num_trees in enumerate(tree_counts, start=1):
        logger.info(f"\n[{i}/{len(tree_counts)}] Preparing visualization: {num_trees} trees")
        seed = 3000 + i
        
        forest, terrain, sun = run_simulation_headless(num_trees, seed)
        results.append({
            "num_trees": num_trees,
            "forest": forest,
            "terrain": terrain,
            "sun": sun,
        })

    # Wizualizacja każdego lasu
    print("\n" + "="*70)
    print(f"Wyświetlanie {len(results)} scen wizualizacji lasów...")
    print("Zamknij okno, aby przejść do następnego lasu (konkurencja rosnąca)")
    print("="*70 + "\n")

    for idx, result in enumerate(results, start=1):
        num_trees = result["num_trees"]
        forest = result["forest"]
        terrain = result["terrain"]
        sun = result["sun"]

        # Oblicz statystyki dla wyświetlenia
        total_height = sum(tree.height() for tree in forest.trees)
        avg_height = total_height / len(forest.trees) if forest.trees else 0.0
        total_nodes = sum(len(tree.nodes) for tree in forest.trees)

        print(f"\nScene {idx}/{len(results)}: {num_trees} drzew w lesie")
        print(f"  • Średnia wysokość: {avg_height:.2f} j.")
        print(f"  • Łączna liczba gałęzi: {total_nodes}")
        print(f"  • Konkurencja: {'niska   🌳' if num_trees <= 4 else 'średnia 🌲' if num_trees <= 9 else 'wysoka 🌴'}")

        scene = TreeScene(forest, terrain, sun, debug=True)
        app.run()

    print("\n" + "="*70)
    print("✨ Koniec wizualizacji!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
