class OptionalLine(object):
    def __init__(self, colour, p1, p2, p3, p4):
        self.colour = colour
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4


class Quadrilateral(object):
    def __init__(self, colour, p1, p2, p3, p4):
        self.colour = colour
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4


class Line(object):
    def __init__(self, colour, p1, p2):
        self.colour = colour
        self.p1 = p1
        self.p2 = p2


class Triangle(object):
    def __init__(self, colour, p1, p2, p3):
        self.colour = colour
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3


class MetaCommand(object):
    def __init__(self, text):
        self.text = text


class Comment(object):
    def __init__(self, text):
        self.text = text


class BlankLine:
    pass