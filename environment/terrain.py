import numpy as np

class Terrain:
    def __init__(self, scale=10.0, height_amp=2.5):
        self.scale = scale
        self.height_amp = height_amp

    # ---- Terrain Generation ----

    def height(self, x: float, y: float) -> float:
        return (
            np.sin(x / self.scale) * np.cos(y / self.scale)
            + 0.5 * np.sin(2 * x / self.scale)
        ) * self.height_amp
    
    def slope(self, x: float, y: float, eps=0.1) -> float:
        dzdx = (self.height(x + eps, y) - self.height(x - eps, y)) / (2 * eps)
        dzdy = (self.height(x, y + eps) - self.height(x, y - eps)) / (2 * eps)
        return np.sqrt(dzdx**2 + dzdy**2)
    
    # ---- Moist ----

    def moisture(self, x: float, y: float) -> float:
        h = self.height(x, y)
        s = self.slope(x, y)

        moisture = (
            np.exp(-0.5 * h**2)   # doliny wilgotniejsze
            * np.exp(-s)          # stoki suchsze
        )

        return np.clip(moisture, 0.05, 1.0)