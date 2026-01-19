import numpy as np

#dwie funkcje od moisture?

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
            base_prob = 0.95
        elif h <= 0.5:
            base_prob = 0.2
        else:
            base_prob = 0.4

        # Stromość zmniejsza spawn na stokach - czy ten fragment jest potrzebny?
        prob = base_prob * np.exp(-2.0 * s)
        return np.clip(prob, 0.05, 1.0)


    def moisture(self, x: float, y: float) -> float:
        h = self.height(x, y)
        s = self.slope(x, y)

        # normalizacja wysokości (heurystyczna)
        h_norm = np.clip((h + self.height_amp) / (2 * self.height_amp), 0.0, 1.0)
        h_dry = h_norm                  # im wyżej, tym bardziej sucho

        # nachylenie bardzo wysusza
        s_dry = np.clip(s / 1.5, 0.0, 1.0)

        # końcowa wilgotność
        moisture = 1.0 - (0.6 * h_dry + 0.4 * s_dry)

        return np.clip(moisture, 0.05, 1.0)
