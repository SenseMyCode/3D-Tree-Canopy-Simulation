import numpy as np
from scipy.spatial import ConvexHull

def canopy_points(tree, min_height_ratio=0.6):
    zs = np.array([n.z for n in tree.nodes])
    z_min, z_max = zs.min(), zs.max()

    threshold = z_min + min_height_ratio * (z_max - z_min)

    pts = np.array([
        [n.x, n.y]
        for n in tree.nodes
        if n.z >= threshold
    ])

    return pts


def canopy_hull(tree):
    pts = canopy_points(tree)
    if len(pts) < 3:
        return None

    hull = ConvexHull(pts)
    return pts[hull.vertices]
