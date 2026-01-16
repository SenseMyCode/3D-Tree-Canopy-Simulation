import numpy as np
from vispy.scene import visuals
from vispy import io, scene


class TerrainVisual:
    def __init__(self, parent, terrain, texture_path, size=20, resolution=100):
        self.terrain = terrain

        # --- Wczytanie PNG ---
        texture = io.read_png(texture_path)

        # --- ImageVisual w tle ---
        self.terrain_texture = visuals.Image(
            texture,
            parent=parent,
            method='subdivide'  # opcjonalnie
        )

        # Skala i przesunięcie, żeby pasowało do terenu
        tex_height, tex_width = texture.shape[:2]
        scale_x = (size * 2) / tex_width
        scale_y = (size * 2) / tex_height

        self.terrain_texture.transform = scene.transforms.STTransform(
            scale=(scale_x, scale_y, 1.0),
            translate=(-size, -size, 0)
        )

        # --- Siatka terenu (Mesh) ---
        xs = np.linspace(-size, size, resolution)
        ys = np.linspace(-size, size, resolution)
        X, Y = np.meshgrid(xs, ys)
        Z = np.zeros_like(X)
        for i in range(resolution):
            for j in range(resolution):
                Z[i, j] = terrain.height(X[i, j], Y[i, j])

        vertices = np.c_[X.flatten(), Y.flatten(), Z.flatten()]

        faces = []
        for i in range(resolution - 1):
            for j in range(resolution - 1):
                idx = i * resolution + j
                faces.append([idx, idx + 1, idx + resolution])
                faces.append([idx + 1, idx + resolution + 1, idx + resolution])
        faces = np.array(faces)

        # Kolor siatki – biały
        colors = np.ones((vertices.shape[0], 4), dtype=np.float32)
        self.mesh = visuals.Mesh(
            vertices=vertices,
            faces=faces,
            vertex_colors=colors,
            shading='smooth',
            parent=parent
        )
