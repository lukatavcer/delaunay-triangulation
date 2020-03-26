import matplotlib.pyplot as plt
import matplotlib.colors as mcd

import numpy as np
from scipy.spatial import Delaunay
import random

AXIS_TICKS = 3.0


def plot_edges(edges, step):
    plt.figure()
    xes = []
    yes = []

    for _, e in edges.items():
        x = [
            e.point_from[0],
            e.point_to[0]
        ]
        y = [
            e.point_from[1],
            e.point_to[1]
        ]

        xes += x
        yes += y

        plt.plot(x, y)
        plt.plot(x, y, 'or')

    # Bounding triangle
    xes = np.array(xes)
    yes = np.array(yes)
    max_M = int(max(xes.max(), xes.min(), yes.max(), yes.min(), key=abs))
    triangle_x = (max_M, 0, -max_M)
    triangle_y = (0, max_M, -max_M)
    plt.triplot(triangle_x, triangle_y)

    # Set tick step
    r = np.arange(-max_M, max_M + 1, AXIS_TICKS)
    plt.xticks(r)
    plt.yticks(r)

    # Set grid
    plt.grid()

    # Show plot
    plt.show()
    # plt.savefig('plots/step_{}.png'.format(step), bbox_inches='tight')
    plt.close()


def plot_triangles(triangles):
    plt.figure()
    xes = []
    yes = []
    colors = list(mcd.TABLEAU_COLORS.keys())

    for _, t in triangles.items():
        triangle_x = []
        triangle_y = []

        for point in t.points:
            triangle_x.append(point[0])
            triangle_y.append(point[1])
            xes.append(point[0])
            yes.append(point[1])

            plt.plot(point[0], point[1], 'or')
        color = random.choice(colors)
        plt.triplot(triangle_x, triangle_y, c=color)

    # Bounding triangle
    xes = np.array(xes)
    yes = np.array(yes)
    max_M = int(max(xes.max(), xes.min(), yes.max(), yes.min(), key=abs))

    # Set tick step
    r = np.arange(-max_M, max_M + 1, AXIS_TICKS)
    plt.xticks(r)
    plt.yticks(r)

    # Set grid
    plt.grid()

    # Show plot
    plt.show()


def plot_points(points):
    # Plot points
    x_list = np.asarray([x[0] for x in points], dtype=int)
    y_list = np.asarray([y[1] for y in points], dtype=int)

    plt.figure()
    plt.plot(x_list, y_list, 'or')

    # Plot imaginary dummy triangle
    max_M = int(max(x_list.max(), x_list.min(), y_list.max(), y_list.min(), key=abs))

    # triangle = [(3*M, 0), (0, 3*M), (-3*M, -3*M)]
    triangle_x = (3*max_M, 0, -3*max_M)
    triangle_y = (0, 3*max_M, -3*max_M)
    plt.triplot(triangle_x, triangle_y)

    # Set plot axis labels
    # plt.xlabel('x')
    # plt.ylabel('y')

    # Set tick step
    # r = np.arange(-10, 10 + 1, 1.0)
    r = np.arange(-3*max_M, 3*max_M + 1, AXIS_TICKS)
    plt.xticks(r)
    plt.yticks(r)

    # Set grid
    plt.grid()

    # Show plot
    plt.show()

    # points = np.array(points, dtype=int)

    # tri = Delaunay(points)
    # plt.triplot(points[:, 0], points[:, 1], tri.simplices)
    # plt.plot(points[:, 0], points[:, 1], 'o')
    # plt.xticks(r)
    # plt.yticks(r)
    # plt.grid()
    # plt.show()
