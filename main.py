import numpy as np
from triangle import Triangle, Edge

# Read LAZ File
# inFile = File('data/GK_462_100.laz', mode='r')
#
# I = inFile.Classification == 2
#
# # laz_points = inFile.points[:100]
# points = list(zip(inFile.get_x()[:100], inFile.get_y()[:100]))
#

f = 'data/test.txt'
# f = 'data/armin.txt'

# Read points
file = open(f, 'r')
Lines = file.readlines()

points = []

# Point with highest lexicographic order
min_x, min_y = None, None

for line in Lines:
    if '#' not in line:
        point = np.array(line.strip().split(), dtype=int)
        points.append((point[0], point[1]))

# Create imaginary triangle that contains all points
x_list = np.asarray([x[0] for x in points], dtype=int)
y_list = np.asarray([y[1] for y in points], dtype=int)
max_M = int(max(x_list.max(), x_list.min(), y_list.max(), y_list.min(), key=abs))
root_triangle = [(3 * max_M, 0), (0, 3 * max_M), (-3 * max_M, -3 * max_M)]

# This is root DAG structure with root triangle
D = Triangle(root_triangle)

# Plot points
# plot_points(points)


def counterclockwise(a, b, c):
    # Return points in counterclockwise direction
    ccw = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]) > 0  # > 0 is CCW

    if ccw:
        return a, b, c

    return a, c, b


def validate(p, t, v1, v2):
    old_edge_from, old_edge_to = sorted((v1, v2))
    key = "{}:{}".format(old_edge_from, old_edge_to)
    e = D.all_edges.get(key)
    neighbour = t.get_neighbour(e)

    if neighbour and neighbour != t:
        # Check if p is in neighbour's circumcircle
        flip = neighbour.in_circumcicle(p)
        if flip:
            print("FLIP EDGE")
            D.plot_all_edges()

            # Remove old edge
            print("Remove edge: " + key)
            D.delete_edge(key)

            # Add new edge
            # TODO make use of points, update when removing edges -> use edges to find adjacent point
            (neighbour_root) = list(set(neighbour.points).difference(set([v1, v2])))[0]  # must be nicer!

            # Create new triangles
            t1 = Triangle([p, v1, neighbour_root], parent=t, create_edges=False)
            t2 = Triangle([p, neighbour_root, v2], parent=t, create_edges=False)

            fr, to = sorted((p, neighbour_root))
            new_edge = Edge(fr, to, t1, t2)
            key = new_edge.key
            print("Add edge: " + key)
            D.add_edge(key, new_edge)  # Add edge to DAG all edges

            # * * * * * * +
            #    FIX t2
            # * * * * * * +
            e_from, e_to = sorted((v2, p))
            key = "{}:{}".format(e_from, e_to)
            change_edge = D.all_edges.get(key)

            D.plot_all_edges()
            # Set edge triangle1 and triangle2
            if change_edge.triangle1 == t:
                change_edge.triangle1 = t2
            elif change_edge.triangle2 == t:
                change_edge.triangle2 = t2
            else:
                print("ERROR")

            e_from, e_to = sorted((v2, neighbour_root))
            key = "{}:{}".format(e_from, e_to)
            change_edge = D.all_edges.get(key)

            # Set edge triangle1 and triangle2
            if change_edge.triangle1 == neighbour:
                change_edge.triangle1 = t2
            elif change_edge.triangle2 == neighbour:
                change_edge.triangle2 = t2
            else:
                print("ERROR")

            # * * * * * * +
            #    FIX t1
            # * * * * * * +
            e_from, e_to = sorted((neighbour_root, v1))
            key = "{}:{}".format(e_from, e_to)
            change_edge = D.all_edges.get(key)

            # Set edge triangle1 and triangle2
            if change_edge.triangle1 == neighbour:
                change_edge.triangle1 = t1
            elif change_edge.triangle2 == neighbour:
                change_edge.triangle2 = t1
            else:
                print("ERROR")

            e_from, e_to = sorted((v1, p))
            key = "{}:{}".format(e_from, e_to)
            change_edge = D.all_edges.get(key)

            # Set edge triangle1 and triangle2
            if change_edge.triangle1 == t:
                change_edge.triangle1 = t1
            elif change_edge.triangle2 == t:
                change_edge.triangle2 = t1
            else:
                print("ERROR")

            D.plot_all_edges()

            # Must determine and put edge in CW direction
            # Validate T1
            adj_edge = t1.points[:]  # fastest way to copy list
            adj_edge.remove(p)
            a, b, c = counterclockwise(p, adj_edge[0], adj_edge[1])
            validate(p, t1, b, c)

            # Validate T2
            adj_edge = t2.points[:]  # fastest way to copy list
            adj_edge.remove(p)
            a, b, c = counterclockwise(p, adj_edge[0], adj_edge[1])
            validate(p, t2, b, c)

            print(" -------------------- ")

            # Add parent pointer to new triangles
            t.children.update([t1, t2])

            # Neighbour also gets new triangles as children
            neighbour.children.update([t1, t2])


print("Start inserting points:")
# Loop remaining points
for p in points:
    print("Insert point: " + str(p))

    if p[0] == -2 and p[1] == 2:
        print("")
    if p[0] == 0 and p[1] == 9:
        print("")

    # Locate triangle that encloses the point
    # find where in the DAG point is located
    parent, is_on_edge = D.find_child(p)
    print("Parent:")
    parent.print()
    print("")

    # TODO on the edge of triangle check is missing (where we create 4 triangles)
    # Create 3 or 4 new triangles
    # construct 3 edges to connect new point to points of found leaf triangle
    new_triangles = []
    v1, v2, v3 = counterclockwise(*parent.points)

    t1 = Triangle([p, v1, v2], parent=parent)
    t2 = Triangle([p, v2, v3], parent=parent)
    t3 = Triangle([p, v3, v1], parent=parent)

    # Store new triangles to Delaunay tree graph
    parent.children.update([t1, t2, t3])

    # Check if parent triangle's edges are valid
    validate(p, t1, v1, v2)
    validate(p, t2, v2, v3)
    validate(p, t3, v3, v1)

    D.plot_all_edges()


# # Remove edges that connect to root triangle
# for edge in D.all_edges:
#     if edge.point_from in root_triangle or edge.point_to in root_triangle:
#         D.delete_edge(edge.key)

D.plot_all_edges()
