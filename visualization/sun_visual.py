from vispy.scene.visuals import Sphere
from vispy.scene import transforms


class SunVisual:

    def __init__(self, parent, sun):
        self.visual = Sphere(
            radius=1.3,
            color=(1.0, 0.9, 0.2, 1.0),
            parent=parent
        )
        self.visual.transform = transforms.STTransform(
            translate=sun.position
        )
