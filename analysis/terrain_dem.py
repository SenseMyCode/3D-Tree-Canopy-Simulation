import numpy as np

def terrain_dem(terrain, size=20.0, resolution=200):
    xs = np.linspace(-size, size, resolution)
    ys = np.linspace(-size, size, resolution)

    Z = np.zeros((resolution, resolution))

    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            Z[j, i] = terrain.height(x, y)

    return xs, ys, Z
