import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.spatial import KDTree
from scipy.stats import pearsonr, spearmanr

from analysis.canopy import canopy_hull
from analysis.crown_metrics import crown_metrics


def crown_radius(tree):
    hull = canopy_hull(tree)
    if hull is None:
        return 0.0

    center = hull.mean(axis=0)
    radii = np.linalg.norm(hull - center, axis=1)
    return radii.mean()

def build_tree_dataframe(forest, terrain):
    records = []

    for tree in forest.trees:
        metrics = crown_metrics(tree)

        x, y, _ = tree.nodes[0].position()

        record = {
            "tree_id": tree.tree_id,
            "x": x,
            "y": y,

            "height": metrics["height"],
            "crown_volume": metrics["crown_volume"],
            "crown_radius": crown_radius(tree),

            "asymmetry_pca": metrics["asymmetry_pca"],
            "asymmetry_inertia": metrics["asymmetry_inertia"],
            "asymmetry_hemispheres": metrics["asymmetry_hemispheres"],

            "slope": terrain.slope(x, y),
            "moisture": terrain.moisture(x, y),
        }

        records.append(record)

    return pd.DataFrame(records)

def add_neighbor_distances(df):
    xy = df[["x", "y"]].values
    tree = KDTree(xy)

    distances, _ = tree.query(xy, k=2)  
    df["nearest_neighbor_dist"] = distances[:, 1]

    return df

def analyze_radius_vs_slope(df):
    r, p = spearmanr(df["crown_radius"], df["slope"])
    print(f"Crown radius vs slope: r={r:.3f}, p={p:.4f}")

    plt.figure()
    plt.scatter(df["slope"], df["crown_radius"])
    plt.xlabel("Slope")
    plt.ylabel("Crown radius")
    plt.title("Crown radius vs slope")

def analyze_radius_vs_moisture(df):
    r, p = pearsonr(df["crown_radius"], df["moisture"])
    print(f"Crown radius vs moisture: r={r:.3f}, p={p:.4f}")

    plt.figure()
    plt.scatter(df["moisture"], df["crown_radius"])
    plt.xlabel("Moisture")
    plt.ylabel("Crown radius")
    plt.title("Crown radius vs moisture")


def analyze_height_vs_neighbors(df):
    r, p = pearsonr(df["height"], df["nearest_neighbor_dist"])
    print(f"Height vs neighbor distance: r={r:.3f}, p={p:.4f}")

    plt.figure()
    plt.scatter(df["nearest_neighbor_dist"], df["height"])
    plt.xlabel("Distance to nearest neighbor")
    plt.ylabel("Tree height")
    plt.title("Height vs competition")

def analyze_light_vs_asymmetry(df):
    r, p = spearmanr(df["nearest_neighbor_dist"], df["asymmetry_pca"])
    print(f"Light proxy vs asymmetry: r={r:.3f}, p={p:.4f}")

    plt.figure()
    plt.scatter(df["nearest_neighbor_dist"], df["asymmetry_pca"])
    plt.xlabel("Nearest neighbor distance (light proxy)")
    plt.ylabel("Asymmetry PCA")
    plt.title("Nearest neighbor vs asymmetry")

def run_environment_stats(forest, terrain):
    df = build_tree_dataframe(forest, terrain)
    df = add_neighbor_distances(df)

    print(df)

    analyze_radius_vs_slope(df)
    analyze_radius_vs_moisture(df)
    analyze_height_vs_neighbors(df)
    analyze_light_vs_asymmetry(df)

    plt.show()
