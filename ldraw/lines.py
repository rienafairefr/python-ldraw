# pylint: disable=too-few-public-methods, too-many-arguments

""" classes for lines in parts path """


class OptionalLine:
    """ an optional Line """

    def __init__(self, colour, point1, point2, point3, point4):
        self.colour = colour
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.point4 = point4


class Quadrilateral:
    """ a quadrilateral """

    def __init__(self, colour, point1, point2, point3, point4):
        self.colour = colour
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.point4 = point4

    @property
    def points(self):
        """ returns the points array """
        return [self.point1, self.point2, self.point3, self.point4]


class Line:
    """ a 3D line """

    def __init__(self, colour, point1, point2):
        self.colour = colour
        self.point1 = point1
        self.point2 = point2

    @property
    def points(self):
        """ returns the points array """
        return [self.point1, self.point2]


class Triangle:
    """ a triangle """

    def __init__(self, colour, point1, point2, point3):
        self.colour = colour
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3

    @property
    def points(self):
        """ returns the points array """
        return [self.point1, self.point2, self.point3]


class MetaCommand:
    """ a metacommand """

    def __init__(self, type, text):
        self.type = type
        self.text = text


class Comment:
    """ a comment """

    def __init__(self, text):
        self.text = text
