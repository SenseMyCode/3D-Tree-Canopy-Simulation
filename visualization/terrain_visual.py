import numpy as np
from vispy.scene import visuals
from vispy import io

class TerrainVisual:
    def __init__(self, parent, terrain, texture_path, size=20, resolution=100):
        self.terrain = terrain

        texture = io.read_png(texture_path)  

        tex_height, tex_width = texture.shape[:2]

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


        u_idx = (np.linspace(0, tex_width - 1, resolution)).astype(int)
        v_idx = (np.linspace(0, tex_height - 1, resolution)).astype(int)
        colors = np.ones((vertices.shape[0], 4), dtype=np.float32)  

        for i in range(resolution):
            for j in range(resolution):
                tex_x = u_idx[j]
                tex_y = v_idx[i]
                idx = i * resolution + j
                pixel = texture[tex_y, tex_x] / 255.0 
                if pixel.shape[0] == 3:
                    colors[idx, :3] = pixel   
                    colors[idx, 3] = 1.0      
                else:
                    colors[idx] = pixel       


        self.mesh = visuals.Mesh(
            vertices=vertices,
            faces=faces,
            vertex_colors=colors,
            shading='smooth',
            parent=parent
        )
