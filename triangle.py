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


    @staticmethod
    def cross(p, v1, v2):
        """
            Check if point p lies on the line between v1 and v2 points.
            https://stackoverflow.com/questions/11907947/how-to-check-if-a-point-lies-on-a-line-between-2-other-points
        """
        dxc = p[0] - v1[0]
        dyc = p[1] - v1[1]

        dxl = v2[0] - v1[0]
        dyl = v2[1] - v1[1]

        return dxc * dyl - dyc * dxl == 0

    def get_neighbour(self, e):
        if e.triangle1 and self == e.triangle1:
            return e.triangle2
        elif e.triangle2 and self == e.triangle2:
            return e.triangle1

        return None

    def print(self):
        print(self.points)

    def find_child(self, point):

        if self.point_inside(point):
            # Traverse triangle's children to get to the leaf node (triangle) which contains current point
            if self.children:
                # If triangle has children, one of them must contain the point,
                # if not, the point is on the edge of one child.
                for child in self.children:
                    found, point_on_edge = child.find_child(point)
                    if found:
                        return found, point_on_edge

                for child in self.children:
                    # Check on which child the point lies
                    if not child.children:
                        v1, v2, v3 = child.points
                        if self.cross(point, v1, v2):
                            return self, (v1, v2)
                        elif self.cross(point, v1, v3):
                            return self, (v1, v3)
                        elif self.cross(point, v2, v3):
                            return self, (v2, v3)

            return self, None

        return None, None

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

    def point_inside(self, point):
        """
        check if point provided as parameter is inside this triangle.
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
