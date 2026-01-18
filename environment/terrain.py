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
    
    # ---- Spawn probability dla attraction points ----
    def spawn_probability(self, x: float, y: float) -> float:
        h = self.height(x, y)
        s = self.slope(x, y)

        # Dolina = h < -0.5 → wysokie prawdopodobieństwo
        # Stok = -0.5 <= h <= 0.5 → średnie prawdopodobieństwo
        # Szczyt = h > 0.5 → niskie prawdopodobieństwo
        if h < -0.5:
            base_prob = 0.75
        elif h <= 0.5:
            base_prob = 0.5
        else:
            base_prob = 0.1

        # Stromość zmniejsza spawn na stokach
        prob = base_prob * np.exp(-2.0 * s)
        return np.clip(prob, 0.05, 1.0)
