"""
geometry.py - Geometry classes for the ldraw Python package.

Copyright (C) 2008 David Boddie <david@boddie.org.uk>

This file is part of the ldraw Python package.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import copy
import math


class MatrixError(Exception):
    pass


class Axis(object):
    pass


class XAxis(Axis):
    pass


class YAxis(Axis):
    pass


class ZAxis(Axis):
    pass


class AngleUnits(object):
    pass


class Radians(AngleUnits):
    pass


class Degrees(AngleUnits):
    pass


class Matrix(object):
    def __init__(self, rows):
        self.rows = rows

    def __repr__(self):
        values = reduce(lambda x, y: x + y, self.rows)
        format = ("((%f, %f, %f),\n"
                  " (%f, %f, %f),\n"
                  " (%f, %f, %f))")
        return format % tuple(values)

    def ___mul___(self, r1, r2):
        rows = [[r1[0][0] * r2[0][0] + r1[0][1] * r2[1][0] + r1[0][2] * r2[2][0],
                 r1[0][0] * r2[0][1] + r1[0][1] * r2[1][1] + r1[0][2] * r2[2][1],
                 r1[0][0] * r2[0][2] + r1[0][1] * r2[1][2] + r1[0][2] * r2[2][2]],
                [r1[1][0] * r2[0][0] + r1[1][1] * r2[1][0] + r1[1][2] * r2[2][0],
                 r1[1][0] * r2[0][1] + r1[1][1] * r2[1][1] + r1[1][2] * r2[2][1],
                 r1[1][0] * r2[0][2] + r1[1][1] * r2[1][2] + r1[1][2] * r2[2][2]],
                [r1[2][0] * r2[0][0] + r1[2][1] * r2[1][0] + r1[2][2] * r2[2][0],
                 r1[2][0] * r2[0][1] + r1[2][1] * r2[1][1] + r1[2][2] * r2[2][1],
                 r1[2][0] * r2[0][2] + r1[2][1] * r2[1][2] + r1[2][2] * r2[2][2]]]
        return rows

    def __mul__(self, other):
        if isinstance(other, Matrix):
            r1 = self.rows
            r2 = other.rows
            return Matrix(self.___mul___(r1, r2))
        elif isinstance(other, Vector):
            r = self.rows
            x, y, z = other.x, other.y, other.z
            return Vector(r[0][0] * x + r[0][1] * y + r[0][2] * z,
                          r[1][0] * x + r[1][1] * y + r[1][2] * z,
                          r[2][0] * x + r[2][1] * y + r[2][2] * z)
        else:
            raise MatrixError

    def __rmul__(self, other):
        if isinstance(other, Matrix):
            r1 = other.rows
            r2 = self.rows
            return Matrix(self.___mul___(r1, r2))
        elif isinstance(other, Vector):
            r = self.rows
            x, y, z = other.x, other.y, other.z
            return Vector(x * r[0][0] + y * r[1][0] + z * r[2][0],
                          x * r[0][1] + y * r[1][1] + z * r[2][1],
                          x * r[0][2] + y * r[1][2] + z * r[2][2])
        else:
            raise MatrixError

    def copy(self):
        return Matrix(copy.deepcopy(self.rows))

    def rotate(self, angle, axis, units=Degrees):
        if units == Degrees:
            c = math.cos(angle / 180.0 * math.pi)
            s = math.sin(angle / 180.0 * math.pi)
        else:
            c = math.cos(angle)
            s = math.sin(angle)
        if axis == XAxis:
            rotation = Matrix([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == YAxis:
            rotation = Matrix([[c, 0, -s], [0, 1, 0], [s, 0, c]])
        elif axis == ZAxis:
            rotation = Matrix([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        else:
            raise MatrixError("Invalid axis specified.")
        return self * rotation

    def scale(self, sx, sy, sz):
        return Matrix([[sx, 0, 0], [0, sy, 0], [0, 0, sz]]) * self

    def transpose(self):
        r = self.rows
        return Matrix([[r[0][0], r[1][0], r[2][0]],
                       [r[0][1], r[1][1], r[2][1]],
                       [r[0][2], r[1][2], r[2][2]]])

    def det(self):
        r = self.rows
        terms = [r[0][0] * (r[1][1] * r[2][2] - r[1][2] * r[2][1]),
                 r[0][1] * (r[1][2] * r[2][0] - r[1][0] * r[2][2]),
                 r[0][2] * (r[1][0] * r[2][1] - r[1][1] * r[2][0])]
        return sum(terms)

    def flatten(self):
        return tuple(reduce(lambda x, y: x + y, self.rows))


def Identity():
    return Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])


class Vector(object):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __repr__(self):
        return "<Vector: (%f, %f, %f)>" % (self.x, self.y, self.z)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        # Return a new object.
        return Vector(x, y, z)

    __radd__ = __add__

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        # Return a new object.
        return Vector(x, y, z)

    def __rsub__(self, other):
        x = other.x - self.x
        y = other.y - self.y
        z = other.z - self.z
        # Return a new object.
        return Vector(x, y, z)

    def __cmp__(self, other):
        # This next expression will only return zero (equals) if all
        # expressions are false.
        return self.x != other.x or self.y != other.y or self.z != other.z

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def __rmul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector(self.x * other, self.y * other, self.z * other)
        raise ValueError("Cannot multiply %s with %s" % (self.__class__, type(other)))

    def __div__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector(self.x / other, self.y / other, self.z / other)
        raise ValueError("Cannot divide %s with %s" % (self.__class__, type(other)))

    def copy(self):
        """vector = copy(self)
        Copy the vector so that new vectors containing the same values
        are passed around rather than references to the same object.
        """
        return Vector(self.x, self.y, self.z)

    def cross(self, other):
        return Vector(self.y * other.z - self.z * other.y,
                      self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
