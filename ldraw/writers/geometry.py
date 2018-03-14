""" Some geometry elements used in Writers """


class Edge(object):
    # pylint:disable=too-few-public-methods
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

        self.dx_dy = (point2.x - point1.x) / (point2.y - point1.y)
        self.dz_dy = (point2.z - point1.z) / (point2.y - point1.y)

    @property
    def sort_key(self):
        """ used for sorting the edges before rendering """
        return (self.point1.y, self.point2.y,
                self.point1.x, self.dx_dy,
                self.point1.z, self.dz_dy)


Z_MAX = 1 << 16
