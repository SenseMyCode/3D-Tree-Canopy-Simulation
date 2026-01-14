from structures.tree import Tree
from structures.attraction_point import generate_attraction_points
from visualization.plot_3d import plot_scene

def main():
    tree = Tree(root_position=(0, 0, 0))
    attraction_points = generate_attraction_points()

    # testowe gałęzie
    tree.add_node((0, 0, 1), parent_index=0)
    tree.add_node((0.5, 0.3, 2), parent_index=1)

    plot_scene(tree, attraction_points)

if __name__ == "__main__":
    main()
