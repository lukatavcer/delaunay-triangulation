import numpy as np
from laspy.file import File
from triangle import Triangle, Edge, key_from_points
import time
import sys
sys.setrecursionlimit(10000)


test = True
# test = False

if test:
    f = 'data/test.txt'
    # Read points
    file = open(f, 'r')
    lines = file.readlines()
    points = []

    # Point with highest lexicographic order
    min_x, min_y = None, None

    for line in lines:
        if '#' not in line:
            point = np.array(line.strip().split(), dtype=int)
            points.append((point[0], point[1], point[2]))
else:
    # Read LAZ File
    inFile = File('data/GK_462_100.laz', mode='r')

    I = inFile.Classification == 2

    # laz_points = inFile.points[:100]
    point_count = 10000
    points = list(zip(inFile.X[:point_count], inFile.Y[:point_count], inFile.Z[:point_count]))
    # points = np.array(list(zip(inFile.X[:point_count], inFile.Y[:point_count], inFile.Z[:point_count])))

# Create imaginary triangle that contains all points
x_list = np.asarray([x[0] for x in points], dtype='int64')
y_list = np.asarray([y[1] for y in points], dtype='int64')
max_M = int(max(x_list.max(), x_list.min(), y_list.max(), y_list.min(), key=abs))
root_triangle = [(3 * max_M, 0, 0), (0, 3 * max_M, 0), (-3 * max_M, -3 * max_M, 0)]
# root_triangle = np.array( [(3 * max_M, 0, 0), (0, 3 * max_M, 0), (-3 * max_M, -3 * max_M, 0)], dtype=np.float64)

del x_list
del y_list

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
    key = key_from_points(v1, v2)
    e = D.all_edges.get(key)
    neighbour = t.get_neighbour(e)

    if neighbour and neighbour != t:
        # Check if p is in neighbour's circumcircle
        flip = neighbour.in_circumcicle(p)

        if flip:
            # Delete old triangle from all triangles mesh
            D.delete_triangle(neighbour)
            D.delete_triangle(t)

            # Remove old edge
            D.delete_edge(key)

            # Add new edge
            # TODO make use of points, update when removing edges -> use edges to find adjacent point
            # list comprehension is probably faster, use that
            # (neighbour_root) = list(set(neighbour.points).difference(set([v1, v2])))[0]  # must be nicer!
            neighbour_root = neighbour.points[:]  # fastest way to copy list
            neighbour_root.remove(v1)
            neighbour_root.remove(v2)
            neighbour_root = neighbour_root[0]

            # Create new triangles
            t1 = Triangle([p, v1, neighbour_root], parent=t, create_edges=False)
            t2 = Triangle([p, neighbour_root, v2], parent=t, create_edges=False)

            # Add new edge to DAG all edges
            new_edge = Edge(p, neighbour_root, t1, t2)
            D.add_edge(new_edge.key, new_edge)

            # * * * * * * +
            #    FIX t2
            # * * * * * * +
            # Set edge triangle1 and triangle2
            key = key_from_points(v2, p)
            change_edge = D.all_edges.get(key)

            change_edge.replace_neighbour(t, t2)

            # Set edge triangle1 and triangle2
            key = key_from_points(v2, neighbour_root)
            change_edge = D.all_edges.get(key)
            change_edge.replace_neighbour(neighbour, t2)

            # * * * * * * +
            #    FIX t1
            # * * * * * * +
            # Set edge triangle1 and triangle2
            key = key_from_points(neighbour_root, v1)
            change_edge = D.all_edges.get(key)
            change_edge.replace_neighbour(neighbour, t1)

            # Set edge triangle1 and triangle2
            key = key_from_points(v1, p)
            change_edge = D.all_edges.get(key)
            change_edge.replace_neighbour(t, t1)

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

            # Add parent pointer to new triangles
            t.children.update([t1, t2])

            # Neighbour also gets new triangles as children
            neighbour.children.update([t1, t2])


print("Start inserting points")
start_time = time.time()
# Loop remaining points
np.random.shuffle(points)

for p in points:
    # Locate triangle that encloses the point
    # find where in the DAG point is located
    p = tuple(float(c) for c in p)
    t, edge = D.find_child(p)

    if edge:
        # Point lies on the edge of the triangle, create 4 new triangles
        key = key_from_points(*edge)
        edge = D.all_edges[key]
        D.delete_edge(key)

        # Split first triangle
        # Get triangle1 root point (point opposite of the edge
        v1, v2, v3 = edge.triangle1.points
        # (root1) = list(set([v1, v2, v3]).difference(set([edge.point_from, edge.point_to])))[0]  # maybe I overcomplicated this..
        root1 = [v1, v2, v3]
        root1.remove(edge.point_from)
        root1.remove(edge.point_to)
        root1 = root1[0]
        root1, t1v2, t1v3 = counterclockwise(root1, edge.point_from, edge.point_to)

        t1 = Triangle([p, t1v3, root1], parent=edge.triangle1, create_edges=False)
        t2 = Triangle([p, root1, t1v2], parent=edge.triangle1, create_edges=False)
        try:
            edge.triangle1.children.update([t1, t2])
            new_edge = Edge(p, root1, t1, t2)
            D.add_edge(new_edge.key, new_edge)

            # Replace neighbour
            key = key_from_points(root1, t1v2)
            change_edge = D.all_edges.get(key)
            change_edge.replace_neighbour(edge.triangle1, t2)
            key = key_from_points(root1, t1v3)
            change_edge = D.all_edges.get(key)
            change_edge.replace_neighbour(edge.triangle1, t1)

            # Split second triangle
            v1, v2, v3 = edge.triangle2.points
            # TODO ugly, use list iterating, probably faster
            # (root2) = list(set([v1, v2, v3]).difference(set([edge.point_from, edge.point_to])))[0]  # maybe I overcomplicated this..
            root2 = [v1, v2, v3]
            root2.remove(edge.point_from)
            root2.remove(edge.point_to)
            root2 = root2[0]

            root2, t2v2, t2v3 = counterclockwise(root2, edge.point_from, edge.point_to)

            t3 = Triangle([p, root2, t2v2], parent=edge.triangle2, create_edges=False)
            t4 = Triangle([p, t2v3, root2], parent=edge.triangle2, create_edges=False)
            edge.triangle2.children.update([t3, t4])
            new_edge = Edge(p, root2, t3, t4)
            D.add_edge(new_edge.key, new_edge)

            # Replace neighbour
            key = key_from_points(root2, t2v2)
            change_edge = D.all_edges.get(key)
            change_edge.replace_neighbour(edge.triangle2, t3)
            key = key_from_points(root2, t2v3)
            change_edge = D.all_edges.get(key)
            change_edge.replace_neighbour(edge.triangle2, t4)

            # 2 new small edges (long old edge was split into 2 smaller ones while creating 4 new triangles)
            new_edge = Edge(p, t2v2, t1, t3)
            D.add_edge(new_edge.key, new_edge)

            new_edge = Edge(p, t2v3, t2, t4)
            D.add_edge(new_edge.key, new_edge)

            # Delete old triangles from the final mesh
            D.delete_triangle(edge.triangle1)
            D.delete_triangle(edge.triangle2)

            # Validate 4 new triangles
            validate(p, t1, t1v3, root1)
            validate(p, t2, root1, t1v2)
            validate(p, t3, root2, t2v2)
            validate(p, t4, t2v3, root2)
        except Exception as e:
            pass
    else:
        # Create 3 new triangles
        # split triangle to 3
        v1, v2, v3 = counterclockwise(*t.points)

        t1 = Triangle([p, v1, v2], parent=t)
        t2 = Triangle([p, v2, v3], parent=t)
        t3 = Triangle([p, v3, v1], parent=t)

        # Store new triangles to Delaunay tree graph
        t.children.update([t1, t2, t3])

        # Delete old triangle from all triangles mesh
        D.delete_triangle(t)

        # Check if parent triangle's edges are still valid after the new point was inserted
        validate(p, t1, v1, v2)
        validate(p, t2, v2, v3)
        validate(p, t3, v3, v1)

    # D.plot_all_edges()


# Remove triangles that connect to root triangle
root_points = D.points

print("--- %s seconds triangulation ---" % (time.time() - start_time))

f = open("final_triangulation_10k.obj", "w")
f.write('g\n')
f_count = 1
triangle_string = ''

start_time = time.time()
for key in list(D.all_triangles):
    in_mesh = True
    points = ''
    face_string = 'f'

    for point in D.all_triangles[key].points:
        if point in root_points:
            del D.all_triangles[key]
            in_mesh = False
            break
        points += "v {} {} {}\n".format(*point)
        # f_count += 1
        # face_string += " {}".format(f_count)

    if in_mesh:
        triangle_string += points
        triangle_string += "f {} {} {}\n".format(f_count, f_count + 1, f_count + 2)
        f_count += 3
        if f_count % 10000 == 0:
            f.write(triangle_string)
            triangle_string = ''

if triangle_string:
    f.write(triangle_string)

print("--- %s seconds write ---" % (time.time() - start_time))
f.close()

if test:
    D.plot_all_edges()
    D.plot_all_triangles()
