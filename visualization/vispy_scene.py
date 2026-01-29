import numpy as np
from vispy import scene, app
from vispy.scene import visuals
from visualization.terrain_visual import TerrainVisual
from vispy.scene.visuals import Mesh
from vispy.geometry import create_sphere
from matplotlib import cm


class TreeScene(scene.SceneCanvas):
    def __init__(self, forest, terrain):
        super().__init__(
            keys="interactive",
            size=(900, 700),
            show=True,
            bgcolor="black"
        )

        self.unfreeze()

        self.forest = forest
        self.terrain = terrain

        # ---- FLAGS ----
        self.show_growth_sphere = False
        self.show_attraction_points = False

        self.paused = False  # <<< PRAWDZIWA PAUZA

        self.visible_tree_id: int | None = None
        self.scene_dirty = True
        self.camera_dirty = True

        # ---- VIEW ----
        self.view = self.central_widget.add_view()
        self.view.camera = scene.cameras.TurntableCamera(
            fov=60,
            azimuth=45,
            elevation=30,
            distance=25,
            center=(0, 0, 5)
        )

        # kamera = tylko render
        self.view.events.mouse_move.connect(self._on_camera_change)
        self.view.events.mouse_wheel.connect(self._on_camera_change)
        self.view.events.mouse_press.connect(self._on_camera_change)

        # ---- VISUALS ----
        self.attraction_visual = visuals.Markers(parent=self.view.scene)
        self.node_visual = visuals.Markers(parent=self.view.scene)
        self.edge_visual = visuals.Line(parent=self.view.scene)

        self.growth_spheres = []

        # ---- TERRAIN ----
        self.terrain_visual = TerrainVisual(
            parent=self.view.scene,
            terrain=terrain,
            texture_path="assets/terrain_texture.png",
            size=20,
            resolution=120
        )

        # ---- TIMERS ----
        self.grow_timer = app.Timer(
            interval=0.1,
            connect=self._grow_event,
            start=True
        )

        self.render_timer = app.Timer(
            interval=0.016,
            connect=self._render_event,
            start=True
        )

        self.freeze()

    # ---------------- CAMERA EVENTS ----------------
    def _on_camera_change(self, event):
        self.camera_dirty = True

    # ---------------- GROWTH TIMER ----------------
    def _grow_event(self, event):
        # HARD STOP – zero pracy CPU
        if self.paused:
            return

        before = sum(len(t.nodes) for t in self.forest.trees)
        self.forest.grow(steps_per_tick=1)
        after = sum(len(t.nodes) for t in self.forest.trees)

        if after > before:
            self.scene_dirty = True

    # ---------------- RENDER TIMER ----------------
    def _render_event(self, event):
        if self.scene_dirty or self.camera_dirty:
            self.update_scene()
            self.scene_dirty = False
            self.camera_dirty = False

    # ---------------- DRAW ----------------
    def update_scene(self):
        # ---------- ATTRACTION POINTS ----------
        if self.show_attraction_points:
            aps = np.array([ap.position() for ap in self.forest.attraction_points])
            colors = [
                (1.0, 0.8, 0.2, 0.4) if ap.claimed_by is None else (0.5, 0.5, 0.5, 0.2)
                for ap in self.forest.attraction_points
            ]
            self.attraction_visual.set_data(
                aps,
                face_color=np.array(colors),
                size=6
            )
        else:
            self.attraction_visual.set_data(np.empty((0, 3)))

        # ---------- TREES ----------
        all_nodes = []
        all_edges = []

        for tree in self.forest.trees:
            if self.visible_tree_id is not None and tree.tree_id != self.visible_tree_id:
                continue

            all_nodes.extend([n.position() for n in tree.nodes])

            for i, j in tree.edges:
                all_edges.append(tree.nodes[i].position())
                all_edges.append(tree.nodes[j].position())

        # ---- NODE COLORS ----
        if all_nodes:
            nodes = np.array(all_nodes)
            zs = nodes[:, 2]
            zmin, zmax = zs.min(), zs.max()
            znorm = (zs - zmin) / (zmax - zmin + 1e-6)
            colors = cm.viridis(znorm)
            self.node_visual.set_data(nodes, face_color=colors, size=8)
        else:
            self.node_visual.set_data(np.empty((0, 3)))

        if all_edges:
            self.edge_visual.set_data(
                np.array(all_edges),
                color=(0.6, 0.3, 0.1, 1.0),
                width=2,
                connect="segments"
            )
        else:
            self.edge_visual.set_data(np.empty((0, 3)))

        # ---------- GROWTH SPHERES ----------
        for sphere in self.growth_spheres:
            sphere.parent = None
        self.growth_spheres.clear()

        if self.show_growth_sphere:
            for tree in self.forest.trees:
                if not tree.trunk_done:
                    continue
                if self.visible_tree_id is not None and tree.tree_id != self.visible_tree_id:
                    continue

                center = tree.trunk_end.position()
                radius = tree.growth_radius()

                meshdata = create_sphere(radius=radius, rows=16, cols=16)
                sphere = Mesh(
                    meshdata=meshdata,
                    color=(0.2, 0.4, 1.0, 0.15),
                    parent=self.view.scene
                )
                sphere.transform = scene.transforms.STTransform(translate=center)
                self.growth_spheres.append(sphere)

    # ---------------- INPUT ----------------
    def on_key_press(self, event):
        if event.key == "H":
            self.show_attraction_points = not self.show_attraction_points
            self.scene_dirty = True

        elif event.key == "G":
            self.show_growth_sphere = not self.show_growth_sphere
            self.scene_dirty = True

        elif event.key == "SPACE":
            self.paused = not self.paused

            if self.paused:
                self.grow_timer.stop()
                print("PAUSE – wzrost zatrzymany")
            else:
                self.grow_timer.start()
                print("WZNOWIONO wzrost")

        # ---- TREE VISIBILITY ----
        elif event.text.isdigit():
            value = int(event.text)
            if value == 0:
                self.visible_tree_id = None
                print("Widok: wszystkie drzewa")
            else:
                self.visible_tree_id = value - 1
                print(f"Widok: tylko drzewo {self.visible_tree_id}")

            self.scene_dirty = True
