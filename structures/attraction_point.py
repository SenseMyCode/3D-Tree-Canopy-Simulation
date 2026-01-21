from dataclasses import dataclass
import numpy as np


@dataclass
class AttractionPoint:
    x: float
    y: float
    z: float
    claimed_by: int | None = None

    def position(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])



def generate_attraction_points_from_terrain(
        terrain,
        n_candidates=5000,
        area_size=20.0,
        trunk_height=2.0,  # wysokość pnia
        z_min=0.5,
        z_max=10.0,
):
    points = []

    for _ in range(n_candidates):
        x = np.random.uniform(-area_size, area_size)
        y = np.random.uniform(-area_size, area_size)

        prob = terrain.spawn_probability(x, y)
        if np.random.rand() > prob:
            continue

        ground_z = terrain.height(x, y)

        height_factor = 0.3 + 0.7 * prob

        z = ground_z + trunk_height + np.random.uniform(z_min, z_max * height_factor)

        points.append(AttractionPoint(x, y, z))

    return points
