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
    spread: float = 5.0
):
    points = []
    for _ in range(n):
        x = np.random.normal(center[0], spread)
        y = np.random.normal(center[1], spread)
        z = np.random.uniform(2, 10)
        points.append(AttractionPoint(x, y, z))
    return points