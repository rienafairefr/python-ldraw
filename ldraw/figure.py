"""
figure.py - Mini-figure construction classes for the ldraw Python package.

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

from ldraw.geometry import *
from ldraw.pieces import Piece


class Person:
    def __init__(self, position=Vector(0, 0, 0), matrix=Identity(),
                 group=None):
        self.position = position
        self.matrix = matrix
        self.pieces_info = {}
        self.group = group

    def head(self, colour, angle=0, part="3626BPS5"):
        # Displacement from torso
        displacement = self.matrix * Vector(0, -24, 0)
        piece = Piece(colour, self.position + displacement,
                      self.matrix * Identity().rotate(angle, YAxis), part,
                      self.group)
        self.pieces_info["head"] = piece
        return piece

    def hat(self, colour, part="3901"):
        try:
            head = self.pieces_info["head"]
        except KeyError:
            return
        # Displacement from head
        displacement = head.position + head.matrix * Vector(0, 0, 0)
        piece = Piece(colour, displacement, head.matrix, part, self.group)
        return piece

    def torso(self, colour, part="973"):
        return Piece(colour, self.position, self.matrix, part, self.group)

    def backpack(self, colour, displacement=Vector(0, 0, 0), part="3838"):
        # Displacement from torso
        displacement = self.matrix * displacement
        return Piece(colour, self.position + displacement, self.matrix, part,
                     self.group)

    def hips_and_legs(self, colour, part="970C00"):
        # Displacement from torso
        displacement = self.matrix * Vector(0, 32, 0)
        return Piece(colour, self.position + displacement, self.matrix, part,
                     self.group)

    def hips(self, colour, part="970"):
        # Displacement from torso
        displacement = self.matrix * Vector(0, 32, 0)
        return Piece(colour, self.position + displacement, self.matrix, part,
                     self.group)

    def left_arm(self, colour, angle=0, part="981"):
        # Displacement from torso
        displacement = self.matrix * Vector(15, 8, 0)
        piece = Piece(colour, self.position + displacement,
                      self.matrix * Identity().rotate(-10, ZAxis) *
                      Identity().rotate(angle, XAxis), part, self.group)
        self.pieces_info["left arm"] = piece
        return piece

    def left_hand(self, colour, angle=0, part="983"):
        try:
            left_arm = self.pieces_info["left arm"]
        except KeyError:
            return
        # Displacement from left hand
        displacement = left_arm.position + left_arm.matrix * Vector(4, 17, -9)
        matrix = left_arm.matrix * Identity().rotate(40, XAxis) * Identity().rotate(angle, ZAxis)
        piece = Piece(colour, displacement, matrix, part, self.group)
        self.pieces_info["left hand"] = piece
        return piece

    def left_hand_item(self, colour, displacement, angle=0, part=None):
        if not part:
            return
        try:
            left_hand = self.pieces_info["left hand"]
        except KeyError:
            return
        # Displacement from left hand
        displacement = left_hand.position + left_hand.matrix * displacement
        matrix = left_hand.matrix * Identity().rotate(10, XAxis) * Identity().rotate(angle, YAxis)
        piece = Piece(colour, displacement, matrix, part, self.group)
        return piece

    def right_arm(self, colour, angle=0, part="982"):
        # Displacement from torso
        displacement = self.matrix * Vector(-15, 8, 0)
        piece = Piece(colour, self.position + displacement,
                      self.matrix * Identity().rotate(10, ZAxis) *
                      Identity().rotate(angle, XAxis), part, self.group)
        self.pieces_info["right arm"] = piece
        return piece

    def right_hand(self, colour, angle=0, part="983"):
        try:
            right_arm = self.pieces_info["right arm"]
        except KeyError:
            return
        # Displacement from right arm
        displacement = right_arm.position + right_arm.matrix * Vector(-4, 17, -9)
        matrix = right_arm.matrix * Identity().rotate(40, XAxis) * Identity().rotate(angle, ZAxis)
        piece = Piece(colour, displacement, matrix, part, self.group)
        self.pieces_info["right hand"] = piece
        return piece

    def right_hand_item(self, colour, displacement, angle=0, part=None):
        if not part:
            return
        try:
            right_hand = self.pieces_info["right hand"]
        except KeyError:
            return
        # Displacement from right hand
        displacement = right_hand.position + right_hand.matrix * displacement
        matrix = right_hand.matrix * Identity().rotate(10, XAxis) * Identity().rotate(angle, YAxis)
        piece = Piece(colour, displacement, matrix, part, self.group)
        return piece

    def left_leg(self, colour, angle=0, part="972"):
        # Displacement from torso
        displacement = self.matrix * Vector(0, 44, 0)
        piece = Piece(colour, self.position + displacement,
                      self.matrix * Identity().rotate(angle, XAxis), part,
                      self.group)
        self.pieces_info["left leg"] = piece
        return piece

    def left_shoe(self, colour, angle=0, part=None):
        if not part:
            return
        try:
            left_leg = self.pieces_info["left leg"]
        except KeyError:
            return
        # Displacement from left leg
        displacement = left_leg.position + left_leg.matrix * Vector(10, 28, 0)
        matrix = left_leg.matrix * Identity().rotate(angle, YAxis)
        piece = Piece(colour, displacement, matrix, part, self.group)
        return piece

    def right_leg(self, colour, angle=0, part="971"):
        # Displacement from torso
        displacement = self.matrix * Vector(0, 44, 0)
        piece = Piece(colour, self.position + displacement,
                      self.matrix * Identity().rotate(angle, XAxis), part,
                      self.group)
        self.pieces_info["right leg"] = piece
        return piece

    def right_shoe(self, colour, angle=0, part=None):
        if not part:
            return
        try:
            right_leg = self.pieces_info["right leg"]
        except KeyError:
            return
        # Displacement from right leg
        displacement = right_leg.position + right_leg.matrix * Vector(-10, 28, 0)
        matrix = right_leg.matrix * Identity().rotate(angle, YAxis)
        piece = Piece(colour, displacement, matrix, part, self.group)
        return piece


def test():
    import random
    from ldraw.library.colours import Yellow, Light_Green, Blue, Red, Green
    random.seed()
    for x in range(-100, 200, 100):
        for z in range(-100, 200, 100):
            orientation = Identity()
            orientation = orientation.rotate(random.randrange(0, 360), XAxis)
            orientation = orientation.rotate(random.randrange(0, 360), YAxis)
            orientation = orientation.rotate(random.randrange(0, 360), ZAxis)
            figure = Person(Vector(x, 0, z), orientation)
            print figure.head(Yellow)
            print figure.torso(Light_Green, "973P90")
            print figure.hips(Blue)
            angle = random.randrange(-90, 60)
            print figure.left_leg(Red, angle)
            angle = random.randrange(-90, 60)
            print figure.right_leg(Green, angle)
            angle = random.randrange(-120, 60)
            print figure.left_arm(Red, angle)
            angle = random.randrange(-90, 90)
            print figure.left_hand(Yellow, angle)
            angle = random.randrange(-120, 60)
            print figure.right_arm(Green, angle)
            angle = random.randrange(-90, 90)
            print figure.right_hand(Yellow, angle)
            print


if __name__ == "__main__":
    test()
