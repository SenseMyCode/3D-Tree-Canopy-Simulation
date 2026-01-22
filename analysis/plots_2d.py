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
        cmap="terrain"
    )
    plt.colorbar(label="Height")
    plt.title("DEM (synthetic)")
    plt.xlabel("X")
    plt.ylabel("Y")


def plot_seed_points(attraction_points):
    xs = [p.x for p in attraction_points]
    ys = [p.y for p in attraction_points]

    plt.figure(figsize=(6, 6))
    plt.scatter(xs, ys, s=2, alpha=0.3)
    plt.title("Attraction / Seed Points (2D)")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis("equal")


def plot_canopy_footprints(forest):
    plt.figure(figsize=(6, 6))

    for tree in forest.trees:
        hull = canopy_hull(tree)
        if hull is None:
            continue

        poly = np.vstack([hull, hull[0]])
        plt.plot(poly[:, 0], poly[:, 1], linewidth=2)

    plt.title("Tree Canopy Footprints (Convex Hull)")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis("equal")
