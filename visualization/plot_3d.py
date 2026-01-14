import matplotlib.pyplot as plt
import numpy as np

def plot_scene(tree):
    if not hasattr(plot_scene, "fig"):
        plot_scene.fig = plt.figure()
        plot_scene.ax = plot_scene.fig.add_subplot(111, projection="3d")

    ax = plot_scene.ax
    ax.cla()

    if tree.attraction_points:
        aps = np.array([p.position() for p in tree.attraction_points])
        ax.scatter(aps[:, 0], aps[:, 1], aps[:, 2],
                   c="gold", s=10, alpha=0.5)

    nodes = np.array([n.position() for n in tree.nodes])
    ax.scatter(nodes[:, 0], nodes[:, 1], nodes[:, 2],
               c="green", s=30)

    for i, j in tree.edges:
        p1 = tree.nodes[i].position()
        p2 = tree.nodes[j].position()
        ax.plot(
            [p1[0], p2[0]],
            [p1[1], p2[1]],
            [p1[2], p2[2]],
            c="brown"
        )

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_zlim(0, 15)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    plt.pause(0.05)
