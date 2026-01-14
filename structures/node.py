from dataclasses import dataclass
import numpy as np

@dataclass
class Node:
    x:float
    y:float
    z:float
    parent: int | None = None

    def position(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])