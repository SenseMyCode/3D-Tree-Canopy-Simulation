import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress


def scatter_with_regression(x, y, xlabel, ylabel, title):
    plt.figure()

    plt.scatter(x, y)

    # regresja liniowa
    slope, intercept, r, p, _ = linregress(x, y)
    x_line = np.linspace(min(x), max(x), 100)
    y_line = slope * x_line + intercept

    plt.plot(x_line, y_line)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"{title}\nR={r:.2f}, p={p:.3f}")


def plot_radius_vs_moisture(df):
    scatter_with_regression(
        df["moisture"],
        df["crown_radius"],
        xlabel="Moisture",
        ylabel="Crown radius",
        title="Crown radius vs moisture"
    )


def plot_radius_vs_neighbors(df):
    scatter_with_regression(
        df["nearest_neighbor_dist"],
        df["crown_radius"],
        xlabel="Distance to nearest neighbor",
        ylabel="Crown radius",
        title="Crown radius vs competition"
    )

def boxplot_by_groups(values, groups, labels, title, ylabel):
    plt.figure()
    plt.boxplot(
        [values[groups == i] for i in np.unique(groups)],
        labels=labels
    )
    plt.ylabel(ylabel)
    plt.title(title)


def boxplot_wet_vs_dry(df):
    median_moisture = df["moisture"].median()
    groups = (df["moisture"] > median_moisture).astype(int)

    boxplot_by_groups(
        df["crown_radius"].values,
        groups.values,
        labels=["Dry", "Wet"],
        title="Crown radius: dry vs wet",
        ylabel="Crown radius"
    )


def boxplot_valley_vs_ridge(df):
    median_slope = df["slope"].median()
    groups = (df["slope"] > median_slope).astype(int)

    boxplot_by_groups(
        df["crown_radius"].values,
        groups.values,
        labels=["Valley / flat", "Ridge / steep"],
        title="Crown radius: valley vs ridge",
        ylabel="Crown radius"
    )

def map_thematic(df, value_col, title):
    plt.figure()
    sc = plt.scatter(
        df["x"],
        df["y"],
        c=df[value_col],
        s=200,
    )
    plt.colorbar(sc, label=value_col)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title(title)
    plt.axis("equal")


def map_crown_radius(df):
    map_thematic(df, "crown_radius", "Spatial distribution of crown radius")


def map_moisture(df):
    map_thematic(df, "moisture", "Spatial distribution of moisture")
