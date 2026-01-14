import matplotlib.pyplot as plt
import numpy as np

def plot_scene(tree, attraction_points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ap = np.array([p.position() for p in attraction_points])
    ax.scatter(ap[:, 0], ap[:, 1], ap[:, 2], c="gold", s=5, alpha=0.5)

    nodes = np.array([n.position() for n in tree.nodes])
    ax.scatter(nodes[:, 0], nodes[:, 1], nodes[:, 2], c="green", s=30)

    for i, j in tree.edges:
        p1 = tree.nodes[i].position()
        p2 = tree.nodes[j].position()
        ax.plot(
            [p1[0], p2[0]],
            [p1[1], p2[1]],
            [p1[2], p2[2]],
            c="brown",
        )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.show()
