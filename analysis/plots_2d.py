import matplotlib.pyplot as plt
import numpy as np

from analysis.terrain_dem import terrain_dem
from analysis.canopy import canopy_hull


def plot_dem(terrain):
    xs, ys, Z = terrain_dem(terrain)

    plt.figure(figsize=(6, 5))
    plt.imshow(
        Z,
        extent=[xs.min(), xs.max(), ys.min(), ys.max()],
        origin="lower",
        cmap="terrain",
        aspect="auto"
    )
    plt.colorbar(label="Height")
    plt.title("DEM (synthetic)")
    plt.xlabel("X")
    plt.ylabel("Y")


def plot_seed_points(attraction_points):
    xs = [p.x for p in attraction_points]
    ys = [p.y for p in attraction_points]
    claimed = [p.claimed_by is not None for p in attraction_points]

    plt.figure(figsize=(6, 6))
    colors = ["#FFD54F" if not c else "#9E9E9E" for c in claimed]
    alphas = [0.6 if not c else 0.2 for c in claimed]
    plt.scatter(xs, ys, s=8, c=colors, alpha=0.8, linewidths=0)

    plt.title("Attraction / Seed Points (2D)")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis("equal")


def plot_canopy_footprints(forest):
    plt.figure(figsize=(6, 6))

    n = max(1, len(forest.trees))
    cmap = plt.get_cmap("tab20")

    for i, tree in enumerate(forest.trees):
        hull = canopy_hull(tree)
        if hull is None:
            continue

        poly = np.vstack([hull, hull[0]])
        plt.plot(poly[:, 0], poly[:, 1], linewidth=1.5, color=cmap(i % 20))

    plt.title("Tree Canopy Footprints (Convex Hull)")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis("equal")