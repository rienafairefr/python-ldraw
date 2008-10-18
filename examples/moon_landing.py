#!/usr/bin/env python

"""
moon_landing.py - An example of figure construction.

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

import random
from ldraw.colours import *
from ldraw.figure import *
from ldraw.pieces import Group, Piece

figure = Person(Vector(0, 0, -10))
print figure.head(Yellow, 30)
print figure.hat(White, "193B")
print figure.torso(White, "973P90")
print figure.backpack(White, Vector(0, -2, 0))
print figure.hips(White)
print figure.left_leg(White, 0)
print figure.right_leg(White, 0)
print figure.left_arm(White, -45)
print figure.left_hand(White, 0)
print figure.left_hand_item(Grey, Vector(0, -11, -12), 0, "3959") # Torch
print figure.right_arm(White, 0)
print figure.right_hand(White, 0)
print

rover = Group(Vector(80, 48, 20), Identity())
print Piece(Grey, Vector(0, 0, 0), Identity(), "122C01", rover)
print Piece(Black, Vector(30, 6, 0), Identity().rotate(90, YAxis), "3641", rover)
print Piece(Black, Vector(-30, 6, 0), Identity().rotate(90, YAxis), "3641", rover)
print Piece(Grey, Vector(0, 0, -80), Identity(), "122C01", rover)
print Piece(Black, Vector(30, 6, -80), Identity().rotate(90, YAxis), "3641", rover)
print Piece(Black, Vector(-30, 6, -80), Identity().rotate(90, YAxis), "3641", rover)

print Piece(Grey, Vector(0, 0, -40), Identity(), "3022", rover)

print Piece(Grey, Vector(0, -24, -10), Identity().rotate(180, YAxis), "3039", rover)
print Piece(Grey, Vector(0, -32, -10), Identity().rotate(180, YAxis), "3829", rover)
print Piece(Grey, Vector(0, -24, -60), Identity().rotate(180, YAxis), "4079", rover)
print Piece(Grey, Vector(0, -8, -60), Identity(), "3022", rover)
print Piece(Grey, Vector(0, -16, -60), Identity(), "3022", rover)
print Piece(Grey, Vector(0, -24, -90), Identity(), "3004P90", rover)
print Piece(Grey, Vector(-10, -32, -90), Identity(), "3957", rover)
print Piece(Colour(34), Vector(10, -48, -90), Identity(), "3062A", rover)
print Piece(Colour(15), Vector(10, -48, -90), Identity(), "LIGHT", rover)


# Duplicate the rover with a different position and orientation.

rover.position = Vector(-85, 45, 115)
rover.matrix = Identity().rotate(-190, YAxis).rotate(-20, XAxis).rotate(-6, ZAxis)
for piece in rover.pieces:
    print piece

# Add a seated figure to the rover.

figure = Person(Vector(0, -76, -50), Identity().rotate(180, YAxis), group = rover)
print figure.head(Yellow, 0)
print figure.hat(Red, "193B")
print figure.torso(Red, "973P90")
print figure.backpack(Red, Vector(0, -2, 0))
print figure.hips(Red)
print figure.left_leg(Red, -90)
print figure.right_leg(Red, -90)
print figure.left_arm(Red, -35)
print figure.left_hand(Red, 0)
print figure.right_arm(Red, -35)
print figure.right_hand(Red, 0)
print

#print Piece(Grey, Vector(0, 72, 0), Identity(), "3867")
print Piece(Colour(15), Vector(200, -300, -400), Identity(), "LIGHT")
print Piece(Grey, Vector(0, 72, 0), Identity(), "3947")
#print Piece(Grey, Vector(60, 72, -60), Identity(), "52")
