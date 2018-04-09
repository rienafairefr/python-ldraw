"""
pieces.py - Classes representing pieces and groups for the ldraw Python package.

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
# pylint: disable=too-many-arguments, too-few-public-methods
from ldraw.compat import reduce
from ldraw.geometry import Identity, Vector


class Piece(object):
    """
    a Piece, which is a Part with a certain colour
    at a certain position and rotation
    """
    def __init__(self, colour, position, matrix, part, group=None):
        self.position = position
        self.colour = colour
        self.matrix = matrix
        self.part = part.upper()
        self.group = group
        if group:
            group.add_piece(self)

    def __repr__(self):
        if self.group:
            position = self.group.position + self.group.matrix * self.position
            matrix = self.group.matrix * self.matrix
        else:
            position = self.position
            matrix = self.matrix
        tup = tuple(reduce(lambda row1, row2: row1 + row2, matrix.rows))
        return ("1 %i " % self.colour.code) + \
               ("%f " * 3) % (position.x, position.y, position.z) + \
               ("%f " * 9) % tup + \
               ("%s.DAT" % self.part)


class Group(object):
    """ a Group of Pieces """
    def __init__(self, position=Vector(0, 0, 0), matrix=Identity()):
        self.position = position
        self.matrix = matrix
        self.pieces = []

    def __repr__(self):
        text = []
        for piece in self.pieces:
            text.append(repr(piece))
        return "\n".join(text)

    def add_piece(self, piece):
        """ add a piece to the group """
        self.pieces.append(piece)
        if piece.group and piece.group != self:
            piece.group.remove_piece(piece)
        piece.group = self

    def remove_piece(self, piece):
        """ remove a piece from the group """
        self.pieces.remove(piece)
        piece.group = None
