from ldraw.geometry import Vector


class Edge(object):
    """
    Holds an edge of a polygon, used during pixel rendering
    """
    def __init__(self, point1, point2):
        """
        :param point1:
        :type point1: Vector
        :param point2:
        :type point2: Vector
        """

        self.point1 = point1
        self.point2 = point2

        self.x1 = point1.x
        self.y1 = point1.y
        self.y2 = point2.y
        self.z1 = point1.z

        self.dx_dy = (point2.x - point1.x) / (point2.y - point1.y)
        self.dz_dy = (point2.z - point1.z) / (point2.y - point1.y)

    @property
    def t(self):
        return (self.y1, self.y2,
                self.x1, self.dx_dy,
                self.z1, self.dz_dy)


Z_MAX = 1 << 16