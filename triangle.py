import numpy as np

from plot import plot_edges


class Triangle:
    children = []
    bad = set()
    good = set()
    all_edges = dict()

    def __init__(self, points=list, neighbours=dict, parent=None):
        self.points = points
        self.neighbours = neighbours
        self.parent = parent

        self.edges = dict()

        v1, v2, v3 = points
        combs = [
            sorted((v1, v2)),
            sorted((v1, v3)),
            sorted((v2, v3))
        ]
        for comb in combs:
            p1, p2 = comb

            key = "{}:{}".format(p1, p2)
            edge = self.all_edges.get(key)
            if edge:
                self.edges[key] = edge
                if self.parent:
                    # if self.parent == edge.triangle2:
                    #     edge.triangle2 = self
                    if self.parent == edge.triangle1:
                        edge.triangle1 = self
                    else:
                        edge.triangle2 = self
                else:
                    edge.triangle2 = self
            else:
                edge = Edge(p1, p2, self)
                self.edges[key] = edge
                self.all_edges[key] = edge

    def plot_all_edges(self):
        plot_edges(self.all_edges)

    def get_neighbour(self, v1, v2):
        # TODO parameter edge!
        # Get neighbour by edge
        sort = sorted((v1, v2))
        key = "{}:{}".format(sort[0], sort[1])

        e = self.all_edges.get(key)
        if e.triangle1 and self == e.triangle1:
            return e.triangle2
        elif e.triangle2 and self == e.triangle2:
            return e.triangle1

        print("no neighbours")
        return None


    def to_string(self):
        p1, p2, p3 = self.points
        return "{}, {}, {}".format(p1, p2, p3)

    def print(self):
        print(self.points)

    def print_parent(self):
        self.parent.print()

    def find_child(self, point):
        # traverse triangle children to get to the leaf node (triangle) which contains current point
        if self.point_inside(point):
            if self.children:
                for child in self.children:
                    found = child.find_child(point)
                    if found:
                        return found
            else:
                return self

        return None

    def in_circumcicle(self, p):
        # Returns true if p lies in the circumcircle of triangle (v1, v2, v3)
        v1, v2, v3 = self.points

        d = np.array([
            [v1[0], v1[1], v1[0] ** 2 + v1[1] ** 2, 1],
            [v2[0], v2[1], v2[0] ** 2 + v2[1] ** 2, 1],
            [v3[0], v3[1], v3[0] ** 2 + v3[1] ** 2, 1],
            [p[0], p[1], p[0] ** 2 + p[1] ** 2, 1]
        ])

        # if det equal 0 then d is on C

        # if det greater 0 then d is inside C
        return np.linalg.det(d) > 0

    def find_bad_triangles(self, p=None):
        # Check if not already in bad triangles
        if self not in self.good and self not in self.bad:
            # If bad, add to bad triangles
            if self.in_circumcicle(p):
                self.bad.add(self)
            else:
                self.good.add(self)

        for child in self.children:
            child.find_bad_triangles(p)


    @staticmethod
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    def point_inside(self, point):
        """
        check if point provided as parameter is inside this triangle.
        :param point:
        :return:
        https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
        https://www.gamedev.net/forums/topic.asp?topic_id=295943
        """
        v1, v2, v3 = self.points

        d1 = self.sign(point, v1, v2)
        d2 = self.sign(point, v2, v3)
        d3 = self.sign(point, v3, v1)

        has_neg = d1 < 0 or d2 < 0 or d3 < 0
        has_pos = d1 > 0 or d2 > 0 or d3 > 0

        return not (has_neg and has_pos)

    def point_on_edge(self, point):
        """
        check if point provided as parameter is on any of this triangle's edges.
        :param point:
        :return:
        """

        return False


class Edge:

    def __init__(self, point_from=None, point_to=None, triangle1=None, triangle2=None):
        self.point_from = point_from
        self.point_to = point_to
        self.triangle1 = triangle1
        self.triangle2 = triangle2
