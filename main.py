from structures.tree import Tree
from structures.attraction_point import generate_attraction_points
from visualization.plot_3d import plot_scene
import matplotlib.pyplot as plt


def main():
    attraction_points = generate_attraction_points(
        n=500,
        center=(0, 0, 6),
        radii=(5.0,4.0,3.0)
    )

    tree = Tree(
        root_position=(0, 0, 0),
        attraction_points=attraction_points,
        influence_radius=3.0,
        kill_radius=1.0,
        step_size=0.5
    )

    for _ in range(150):
        tree.grow()
        plot_scene(tree)

    plt.show()


if __name__ == "__main__":
    main()
