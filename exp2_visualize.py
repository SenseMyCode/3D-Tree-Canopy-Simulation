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


def run_simulation_headless(sun_pos, seed, max_steps=3000):
    np.random.seed(seed)

    terrain = Terrain(scale=8.0, height_amp=2.0)
    sun = Sun(position=sun_pos)

    logger.info(f"Symulacja: Sun={sun_pos} (seed={seed})")

    attraction_points = generate_attraction_points_from_terrain(
        terrain=terrain,
        sun=sun,
        n_candidates=15000,
        area_size=12.0,
        trunk_height=4.0,
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
            logger.info(f"  Brak postępu (stagnant > 500)")
            break

        if tree.consumed_attraction_points >= tree.max_attraction_points:
            logger.info(f"  Limit AP osiągnięty")
            break

        free_aps = [ap for ap in attraction_points if ap.claimed_by is None]
        if not free_aps:
            logger.info(f"  Koniec dostępnych AP")
            break

    logger.info(f"  Koniec: steps={steps}, nodes={len(tree.nodes)}, height={tree.height():.2f}")
    return forest, terrain, sun


def main():
    sun_positions = [
        # Północ (y ujemne), różne wysokości
        (0.0, -30.0, 15.0),    # Północ, nisko
        (0.0, -30.0, 45.0),    # Północ, wysoko
        
        # Wschód (x dodatnie)
        (30.0, 0.0, 30.0),     # Wschód, średnio
        
        # Południe (y dodatnie)
        (0.0, 30.0, 30.0),     # Południe, średnio
        
        # Zachód (x ujemne)
        (-30.0, 0.0, 30.0),    # Zachód, średnio
        
        # Diagonalne
        (21.0, -21.0, 30.0),   # NW
        (21.0, 21.0, 30.0),    # SE
    ]

    results = []

    print("\n" + "="*70)
    print("WIZUALIZACJA EKSPERYMENTU 2 — wpływ położenia słońca")
    print("="*70 + "\n")

    for i, sun_pos in enumerate(sun_positions, start=1):
        logger.info(f"\n[{i}/{len(sun_positions)}] Sun position: {sun_pos}")
        seed = 2000 + i
        
        forest, terrain, sun = run_simulation_headless(sun_pos, seed)
        results.append({
            "sun_pos": sun_pos,
            "forest": forest,
            "terrain": terrain,
            "sun": sun,
        })

    # Wizualizacja każdego drzewa
    print("\n" + "="*70)
    print(f"Wyświetlanie {len(results)} scen wizualizacji...")
    print("Zamknij okno, aby przejść do następnej sceny")
    print("="*70 + "\n")

    for idx, result in enumerate(results, start=1):
        sun_pos = result["sun_pos"]
        forest = result["forest"]
        terrain = result["terrain"]
        sun = result["sun"]

        print(f"\nScene {idx}/{len(results)}: Sun = {sun_pos}")

        scene = TreeScene(forest, terrain, sun, debug=True)
        app.run()


if __name__ == "__main__":
    main()
