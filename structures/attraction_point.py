from dataclasses import dataclass
import numpy as np

@dataclass
class AttractionPoint:
    x: float
    y: float
    z: float

    def position(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

#Tylko do testowania algorytmu
def generate_attraction_points(
    n: int = 300,
    center: tuple = (0, 0, 5),
    radii: tuple = (5.0, 4.0, 3.0)
):
    points = []

    while len(points) < n:
        x = np.random.uniform(-radii[0], radii[0])
        y = np.random.uniform(-radii[1], radii[1]) 
        z = np.random.uniform(-radii[2], radii[2])

        if (
            (x/radii[0])**2 +
            (y/radii[1])**2 +
            (z/radii[2])**2
        ) <= 1.0:
            points.append(
                AttractionPoint(
                    x + center[0],
                    y + center[1],
                    z + center[2]
                )
            )
    return points

def generate_attraction_points_from_terrain(
        terrain,
        n_candidates=5000,
        area_size=20.0,
        z_min=0.5,
        z_max=6.0,
):
    points = []

    for _ in range(n_candidates):
        x = np.random.uniform(-area_size, area_size) #//2?
        y = np.random.uniform(-area_size, area_size)

        moisture = terrain.moisture(x, y)

        #prawdopodobieństwo spawnu
        if np.random.rand() > moisture:
            continue

        ground_z = terrain.height(x, y)

        z = ground_z + np.random.uniform(z_min, z_max * moisture)

        points.append(AttractionPoint(x, y, z))

    return points