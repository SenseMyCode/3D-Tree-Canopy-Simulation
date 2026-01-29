import numpy as np


class Sun:

    def __init__(self, position=(25.0, -20.0, 30.0)):
        self.position = np.array(position, dtype=float)

    def direction_to(self, x, y, z):
        v = self.position - np.array([x, y, z], dtype=float)
        n = np.linalg.norm(v)
        if n < 1e-6:
            return np.array([0.0, 0.0, 1.0])
        return v / n
