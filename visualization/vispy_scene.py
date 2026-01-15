import numpy as np
from vispy import scene, app
from vispy.scene import visuals

class TreeScene(scene.SceneCanvas):
    def __init__(self, tree):
        super().__init__(keys="interactive", size=(900, 700), show=True, bgcolor="black")
        self.unfreeze()
        self.tree = tree

        # --- widok 3D FPS-style ---
        self.view = self.central_widget.add_view()
        self.camera = scene.cameras.FlyCamera(center=(0,0,0), fov=60)
        self.view.camera = self.camera
        self.camera.speed_factor = 0.5  # prędkość ruchu

        # --- visuals ---
        self.attraction_visual = visuals.Markers(parent=self.view.scene)
        self.node_visual = visuals.Markers(parent=self.view.scene)
        self.edge_visual = visuals.Line(parent=self.view.scene)

        # --- timer do wzrostu drzewa ---
        self.timer = app.Timer(interval=0.016, connect=self._timer_event, start=True)
        self.freeze()

    def _timer_event(self, event):
        self.tree.grow()
        self.update_scene()

    def update_scene(self):
        if self.tree.attraction_points:
            aps = np.array([p.position() for p in self.tree.attraction_points])
            self.attraction_visual.set_data(aps, face_color=(1,0.8,0.2,0.4), size=6)
        nodes = np.array([n.position() for n in self.tree.nodes])
        self.node_visual.set_data(nodes, face_color=(0.2,1,0.2,1), size=8)
        segments = []
        for i,j in self.tree.edges:
            segments.append(self.tree.nodes[i].position())
            segments.append(self.tree.nodes[j].position())
        if segments:
            self.edge_visual.set_data(np.array(segments), color=(0.6,0.3,0.1,1), width=2, connect="segments")
