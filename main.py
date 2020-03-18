import matplotlib.pyplot as plt
from laspy.file import File
import numpy as np
from plot import plot_points
from triangle import Triangle, Edge

# Read LAZ File
# inFile = File('data/GK_462_100.laz', mode='r')
#
# I = inFile.Classification == 2
#
# # laz_points = inFile.points[:100]
# points = list(zip(inFile.get_x()[:100], inFile.get_y()[:100]))
#


# Read points
file = open('data/test.txt', 'r')
Lines = file.readlines()

points = []

# Point with highest lexicographic order
min_x, min_y = None, None

for line in Lines:
    if '#' not in line:
        point = np.array(line.strip().split(), dtype=int)
        points.append((point[0], point[1]))

print(points)


# Create imaginary triangle with root in a node with the highest lexicographic order.
# A point (x,y) is higher than other (u,v) in lexicographic order if if either x < u or both x = u and y < v

x_list = np.asarray([x[0] for x in points], dtype=int)
y_list = np.asarray([y[1] for y in points], dtype=int)
max_M = int(max(x_list.max(), x_list.min(), y_list.max(), y_list.min(), key=abs))
root_triangle = [(3 * max_M, 0), (0, 3 * max_M), (-3 * max_M, -3 * max_M)]

# This is root DAG structure with root triangle
# D for Delaunay
D = Triangle(root_triangle)


def in_circle(v1, v2, v3, p):
    # in_circle
    # Returns true if p lies in the circumcircle of triangle (v1, v2, v3)
    d = np.array([
        [v1[0], v1[1], v1[0] ** 2 + v1[1] ** 2, 1],
        [v2[0], v2[1], v2[0] ** 2 + v2[1] ** 2, 1],
        [v3[0], v3[1], v3[0] ** 2 + v3[1] ** 2, 1],
        [p[0], p[1], p[0] ** 2 + p[1] ** 2, 1]
    ])

    # if det equal 0 then d is on C

    # if det greater 0 then d is inside C
    return np.linalg.det(d) > 0

print()

# Plot points
plot_points(points)

print("Start inserting points:")
# Loop remaining points
for p in points:
    # Locate triangle that encloses the point
    # find where on the DAG point is located
    parent = D.find_child(p)
    print(parent.to_string())
    print("")

    # TODO on the edge of triangle check is missing (where we create 4 triangles)
    # Create 3 or 4 new triangles
    # construct 3 edges to connect new point to points of found leaf triangle
    # TODO make sure they are CCW
    new_triangles = []
    v1, v2, v3 = parent.points

    t1 = Triangle([p, v1, v2], parent=parent)
    t2 = Triangle([p, v2, v3], parent=parent)
    t3 = Triangle([p, v3, v1], parent=parent)

    # Check if parent edges are valid
    # parent = (v1, v2)
    # neighbour = parent.neighbours.get(sorted(v1) + ":" + sorted(v2))
    # Get neighbour of edge v1 & v2
    neighbour = t1.get_neighbour(v1, v2)
    if neighbour and neighbour != t1:
        # Check if p is in neighbour's circumcircle
        flip = neighbour.in_circumcicle(p)
        print("Should flip edge: " + str(flip))
        if flip:
            print("SHOULD FLIP IMPLEMENT")
            # TODO imam t1 in neighbour
            # torej odstraniti moram edge (v1, v2) (pazi na self.edges, ce se kje uporabi sploh)
            # self.edges obsolete?
            # kreirati edge izmed remaining dveh vozlisc (p, NEIGHBOUR tretje vozslice)

            # Remove old edge
            D.remove_edge
            (neighbour_root) = list(set(neighbour.points).difference(set([v1, v2])))[0]  # must be nicer!
            flip_edge = Edge(p, neighbour_root, t1, neighbour)

        # Flip edge

        # Repeat validation for new triangles after flip

    neighbour = t2.get_neighbour(v2, v3)
    if neighbour and neighbour != t2:
        # Check if p is in neighbour's circumcircle
        flip = neighbour.in_circumcicle(p)
        print("Should flip edge: " + str(flip))
        if flip:
            print("SHOULD FLIP IMPLEMENT")

        # Flip edge

        # Repeat validation for new triangles after flip

    neighbour = t3.get_neighbour(v3, v1)
    if neighbour and neighbour != t3:
        # Check if p is in neighbour's circumcircle
        flip = neighbour.in_circumcicle(p)
        print("Should flip edge: " + str(flip))
        if flip:
            print("SHOULD FLIP IMPLEMENT")

        # Flip edge

        # Repeat validation for new triangles after flip



    parent.children = [t1, t2, t3]


    D.plot_all_edges()
    # D.find_bad_triangles(p)
    # bad = D.bad
    # print(bad)
    # Update the DCEL and the tree with the new triangles.

    # Check if any edge is not a Delaunay edge and flip it if not.

