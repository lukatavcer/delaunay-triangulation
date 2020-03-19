from plots.plot import plot_edges


class Triangle:
    all_edges = dict()

    def __init__(self, points=list, parent=None, create_edges=True):
        self.points = points
        self.parent = parent
        self.children = set()

        if create_edges:
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
                    if self.parent:
                        if self.parent == edge.triangle1:
                            edge.triangle1 = self
                        else:
                            edge.triangle2 = self
                    else:
                        edge.triangle2 = self
                else:
                    edge = Edge(p1, p2, self)
                    self.all_edges[key] = edge

    @classmethod
    def add_edge(cls, key, edge):
        cls.all_edges[key] = edge

    @classmethod
    def delete_edge(cls, key):
        # Delete edge from all edges in DAG
        del cls.all_edges[key]

    @classmethod
    def plot_all_edges(cls):
        plot_edges(cls.all_edges)

    def replace_edge(self, old_edge_key, new_edge):
        # Replace edge from triangle's edges, this will make it open
        del self.edges[old_edge_key]
        self.edges[new_edge.key] = new_edge

    def get_neighbour(self, e):
        if e.triangle1 and self == e.triangle1:
            return e.triangle2
        elif e.triangle2 and self == e.triangle2:
            return e.triangle1

        return None

    def to_string(self):
        p1, p2, p3 = self.points
        return "{}, {}, {}".format(p1, p2, p3)

    def print(self):
        print(self.points)

    def print_parent(self):
        self.parent.print()

    def find_child(self, point):
        found = None
        is_on_edge = True

        # Traverse triangle children to get to the leaf node (triangle) which contains current point
        if self.children:
            # If triangle has children, one of them must contain the point,
            # if not, the point is on the edge of one child.
            for child in self.children:
                found, is_on_edge = child.find_child(point)
                if found:
                    return found, False

        elif self.point_inside(point):
                return self, False

        return found, is_on_edge

    def in_circumcicle(self, p):
        # Returns true if p lies in the circumcircle of triangle (v1, v2, v3)
        v1, v2, v3 = self.points

        ax_ = v1[0]-p[0]
        ay_ = v1[1]-p[1]
        bx_ = v2[0]-p[0]
        by_ = v2[1]-p[1]
        cx_ = v3[0]-p[0]
        cy_ = v3[1]-p[1]
        return ((ax_ * ax_ + ay_ * ay_) * (bx_ * cy_ - cx_ * by_) - (bx_ * bx_ + by_ * by_) * (ax_ * cy_ - cx_ * ay_) + (cx_ * cx_ + cy_ * cy_) * (ax_ * by_ - bx_ * ay_)) > 0

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

        c1 = (v2[0] - v1[0]) * (point[1] - v1[1]) - (v2[1] - v1[1]) * (point[0] - v1[0])
        c2 = (v3[0] - v2[0]) * (point[1] - v2[1]) - (v3[1] - v2[1]) * (point[0] - v2[0])
        c3 = (v1[0] - v3[0]) * (point[1] - v3[1]) - (v1[1] - v3[1]) * (point[0] - v3[0])
        if (c1 < 0 and c2 < 0 and c3 < 0) or (c1 > 0 and c2 > 0 and c3 > 0):
            return True
        else:
            return False


class Edge:

    def __init__(self, point_from=None, point_to=None, triangle1=None, triangle2=None):
        point_from, point_to = sorted((point_from, point_to))
        self.key = "{}:{}".format(str(point_from), str(point_to))
        self.point_from = point_from
        self.point_to = point_to
        self.triangle1 = triangle1
        self.triangle2 = triangle2

        # TODO triangles should be dict with 2 triangles, easy to update
        # MUST DO THAT! also much nicer code