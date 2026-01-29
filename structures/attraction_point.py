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
    sun,
    n_candidates=15000,
    area_size=20.0,
    trunk_height=2.0,
    z_min=0.5,
    z_max=14.0,
):
    """
    Attraction points:
    - pełne pokrycie obszaru (siatka + jitter)
    - gęstość silnie zależy od słońca
    - liczba punktów ograniczona globalnie
    """

    points: list[AttractionPoint] = []

    # ===== PARAMETRY KLUCZOWE =====
    target_points = int(0.25 * n_candidates)   # więcej punktów niż wcześniej
    min_prob = 0.05                            # minimalna szansa w cieniu
    max_prob = 0.95                            # maksymalna szansa w pełnym słońcu
    sunlight_gamma = 2.2                       # mocny kontrast jasne/cieniste

    # siatka = gwarancja pokrycia całej przestrzeni
    grid_res = int(np.sqrt(n_candidates))
    xs = np.linspace(-area_size, area_size, grid_res)
    ys = np.linspace(-area_size, area_size, grid_res)

    for x in xs:
        for y in ys:
            # jitter przestrzenny
            xj = x + np.random.uniform(-0.4, 0.4)
            yj = y + np.random.uniform(-0.4, 0.4)

            sun_val = terrain.sunlight(xj, yj, sun)  # 0.05 .. 1.0

            # normalizacja do [0,1]
            sun_norm = (sun_val - 0.05) / (1.0 - 0.05)
            sun_norm = np.clip(sun_norm, 0.0, 1.0)

            # nieliniowość – jasne miejsca dostają DUŻO większą wagę
            sun_weight = sun_norm ** sunlight_gamma

            prob = min_prob + (max_prob - min_prob) * sun_weight

            if np.random.rand() > prob:
                continue

            ground_z = terrain.height(xj, yj)

            height_factor = 0.4 + 0.6 * sun_weight
            z = ground_z + trunk_height + np.random.uniform(
                z_min,
                z_max * height_factor
            )

            points.append(AttractionPoint(xj, yj, z))

    # Po przejściu całej siatki możemy mieć za dużo punktów → losowo przycinamy
    if len(points) > target_points:
        idx = np.random.choice(len(points), size=target_points, replace=False)
        points = [points[i] for i in idx]

    return points
