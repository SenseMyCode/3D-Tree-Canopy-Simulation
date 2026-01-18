import numpy as np
from vispy import scene, app
from vispy.scene import visuals
from visualization.terrain_visual import TerrainVisual
from vispy.scene.visuals import Mesh
from vispy.geometry import create_sphere


class TreeScene(scene.SceneCanvas):
    def __init__(self, tree, terrain):
        super().__init__(keys="interactive", size=(900, 700), show=True, bgcolor="black")
        
        self.unfreeze()  # <-- pozwala na dodawanie nowych atrybutów
        self.tree = tree
        self.terrain = terrain

        # --- toggle dla kuli ---
        self.show_growth_sphere = True
        self.growth_spheres = []

        # --- widok 3D ---
        self.view = self.central_widget.add_view()
        self.camera = scene.cameras.FlyCamera(center=(0,0,0), fov=60, scale_factor=3.0)
        self.view.camera = self.camera
        self.camera.speed_factor = 0.5

        # --- visuals drzewa ---
        self.attraction_visual = visuals.Markers(parent=self.view.scene)
        self.node_visual = visuals.Markers(parent=self.view.scene)
        self.edge_visual = visuals.Line(parent=self.view.scene)

        # --- PNG teren ---
        self.terrain_visual = TerrainVisual(
            parent=self.view.scene,
            terrain=terrain,
            texture_path="assets/terrain_texture.png",
            size=20,
            resolution=120
        )

        # --- start kamery ---
        self.camera.center = (-10, -10, 10)

        # --- timer do wzrostu drzewa ---
        self.timer = app.Timer(interval=0.016, connect=self._timer_event, start=True)

        self.freeze()  # <-- blokujemy ponownie, po dodaniu nowych atrybutów


    def _timer_event(self, event):
        self.tree.grow()        # lub pętlę po wszystkich drzewach, jeśli jest kilka
        self.update_scene()

        if self.show_growth_sphere:
            self._add_growth_sphere()
        else:
            # jeśli wyłączone – usuń wszystkie widoczne kule
            for gs in self.growth_spheres:
                gs.parent = None
            self.growth_spheres = []



    def update_scene(self):
        # Attraction points
        if self.tree.attraction_points:
            aps = np.array([p.position() for p in self.tree.attraction_points])
            self.attraction_visual.set_data(aps, face_color=(1,0.8,0.2,0.4), size=6)

        # Nodes i krawędzie
        nodes = np.array([n.position() for n in self.tree.nodes])
        self.node_visual.set_data(nodes, face_color=(0.2,1,0.2,1), size=8)
        segments = []
        for i,j in self.tree.edges:
            segments.append(self.tree.nodes[i].position())
            segments.append(self.tree.nodes[j].position())
        if segments:
            self.edge_visual.set_data(np.array(segments), color=(0.6,0.3,0.1,1), width=2, connect="segments")

    def _add_growth_sphere(self):
        if self.tree.trunk_end is None:
            return

        center = self.tree.trunk_end.position()
        radius = self.tree.growth_radius()

        mesh_data = create_sphere(rows=20, cols=20, radius=radius)
        vertices = mesh_data.get_vertices() + center
        faces = mesh_data.get_faces()

        # jeśli jest już kula, usuń starą
        for gs in self.growth_spheres:
            gs.parent = None
        self.growth_spheres = []

        # stwórz nową
        gs = Mesh(
            vertices=vertices,
            faces=faces,
            color=(0.2, 0.5, 1.0, 0.3),
            parent=self.view.scene,
            shading='smooth',
            mode='triangles'
        )
        self.growth_spheres.append(gs)


    def on_key_press(self, event):
        if event.key == 'G':  # np. klawisz G
            self.show_growth_sphere = not self.show_growth_sphere
            print(f"Growth spheres {'ON' if self.show_growth_sphere else 'OFF'}")


