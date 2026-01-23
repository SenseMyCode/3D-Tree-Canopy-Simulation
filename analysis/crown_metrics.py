import numpy as np
from scipy.spatial import ConvexHull


# -------------------------------------------------
# Pomocnicze: punkty korony (górna część drzewa)
# -------------------------------------------------

def canopy_points_3d(tree, min_height_ratio=0.6):
    """
    Zwraca punkty (x,y,z) należące do korony drzewa
    """
    zs = np.array([n.z for n in tree.nodes])
    z_min, z_max = zs.min(), zs.max()

    threshold = z_min + min_height_ratio * (z_max - z_min)

    pts = np.array([
        n.position()
        for n in tree.nodes
        if n.z >= threshold
    ])

    return pts


def canopy_points_2d(tree, min_height_ratio=0.6):
    """
    Zwraca punkty (x,y) korony drzewa
    """
    pts3d = canopy_points_3d(tree, min_height_ratio)
    return pts3d[:, :2]


# -------------------------------------------------
#  CROWN VOLUME (3D Convex Hull)
# -------------------------------------------------

def crown_volume(tree, min_height_ratio=0.6):
    """
    Objętość korony jako 3D convex hull
    """
    pts = canopy_points_3d(tree, min_height_ratio)

    if len(pts) < 4:
        return 0.0  # za mało punktów na bryłę 3D

    hull = ConvexHull(pts)
    return hull.volume


# -------------------------------------------------
#  ASYMMETRY – METODY
# -------------------------------------------------

def asymmetry_radius(tree, min_height_ratio=0.6):
    """
    Najprostsza asymetria:
    max_promień / min_promień
    """
    pts = canopy_points_2d(tree, min_height_ratio)

    if len(pts) < 3:
        return 0.0

    center = pts.mean(axis=0)
    distances = np.linalg.norm(pts - center, axis=1)

    return distances.max() / distances.min()


def asymmetry_pca(tree, min_height_ratio=0.6):
    """
    Asymetria przez PCA (elongation)
    """
    pts = canopy_points_2d(tree, min_height_ratio)

    if len(pts) < 3:
        return 0.0

    # centrowanie
    pts_centered = pts - pts.mean(axis=0)

    # macierz kowariancji
    cov = np.cov(pts_centered.T)

    # wartości własne
    eigvals, _ = np.linalg.eig(cov)
    eigvals = np.sort(eigvals)[::-1]

    if eigvals[1] <= 1e-6:
        return 0.0

    return eigvals[0] / eigvals[1]


def asymmetry_hemispheres(tree, min_height_ratio=0.6):
    """
    Asymetria półkul (lewo/prawo)
    """
    pts = canopy_points_2d(tree, min_height_ratio)

    if len(pts) < 3:
        return 0.0

    center_x = pts[:, 0].mean()

    left = np.sum(pts[:, 0] < center_x)
    right = np.sum(pts[:, 0] > center_x)

    if left + right == 0:
        return 0.0

    return abs(left - right) / (left + right)


def asymmetry_inertia(tree, min_height_ratio=0.6):
    """
    Asymetria przez moment bezwładności
    """
    pts = canopy_points_2d(tree, min_height_ratio)

    if len(pts) < 3:
        return 0.0

    center = pts.mean(axis=0)
    rel = pts - center

    Ixx = np.sum(rel[:, 1] ** 2)
    Iyy = np.sum(rel[:, 0] ** 2)

    if min(Ixx, Iyy) <= 1e-6:
        return 0.0

    return max(Ixx, Iyy) / min(Ixx, Iyy)


# -------------------------------------------------
#  ZBIORCZA FUNKCJA
# -------------------------------------------------

def crown_metrics(tree, min_height_ratio=0.6):
    """
    Zwraca wszystkie metryki korony w jednym słowniku.
    Height jest liczony względem korzenia tylko w tych analizach.
    """
    root_z = tree.nodes[0].z 
    height_rel = max(n.z for n in tree.nodes) - root_z

    return {
        "height": height_rel,
        "crown_volume": crown_volume(tree, min_height_ratio),
        "asymmetry_radius": asymmetry_radius(tree, min_height_ratio),
        "asymmetry_pca": asymmetry_pca(tree, min_height_ratio),
        "asymmetry_hemispheres": asymmetry_hemispheres(tree, min_height_ratio),
        "asymmetry_inertia": asymmetry_inertia(tree, min_height_ratio),
    }

