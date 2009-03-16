#!/usr/bin/env python

"""
buggy.py - An example of materials.

Copyright (C) 2009 David Boddie <david@boddie.org.uk>

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
from ldraw.geometry import YAxis
from ldraw.pieces import Group, Piece

#figure = Person(Vector(0, 0, -10))
#print figure.head(Yellow, 30)
#print figure.hat(White, "193B")
#print figure.torso(White, "973P90")
#print figure.backpack(White, Vector(0, -2, 0))
#print figure.hips(White)
#print figure.left_leg(White, 0)
#print figure.right_leg(White, 0)
#print figure.left_arm(White, -45)
#print figure.left_hand(White, 0)
#print figure.left_hand_item(Grey, Vector(0, -11, -12), 0, "3959") # Torch
#print figure.right_arm(White, 0)
#print figure.right_hand(White, 0)
#print

rover = Group(Vector(0, 48, 60), Identity().rotate(-15, YAxis))
print Piece(Grey, Vector(0, 0, 0), Identity(), "122C01", rover)
print Piece(BlackRubber, Vector(30, 6, 0), Identity().rotate(90, YAxis), "3641", rover)
print Piece(BlackRubber, Vector(-30, 6, 0), Identity().rotate(90, YAxis), "3641", rover)
print Piece(Grey, Vector(0, 0, -80), Identity(), "122C01", rover)
print Piece(BlackRubber, Vector(30, 6, -80), Identity().rotate(90, YAxis), "3641", rover)
print Piece(BlackRubber, Vector(-30, 6, -80), Identity().rotate(90, YAxis), "3641", rover)

print Piece(Grey, Vector(0, 0, -40), Identity(), "3022", rover)

print Piece(ChromeSilver, Vector(0, -24, -10), Identity().rotate(180, YAxis), "3039", rover)
print Piece(ChromeSilver, Vector(0, -32, -10), Identity().rotate(180, YAxis), "3829", rover)
print Piece(ChromeGold, Vector(0, -24, -60), Identity().rotate(180, YAxis), "4079", rover)
print Piece(ChromeGold, Vector(0, -8, -60), Identity(), "3022", rover)
print Piece(ChromeGold, Vector(0, -16, -60), Identity(), "3022", rover)
print Piece(ChromeGold, Vector(0, -24, -90), Identity(), "3004P90", rover)
print Piece(ChromeSilver, Vector(-10, -32, -90), Identity(), "3957", rover)

print Piece(Yellow, Vector(0, 72, 0), Identity(), "3867")
print Piece(Yellow, Vector(0, 72, -320), Identity(), "3867")
print Piece(Blue, Vector(320, 72, 0), Identity(), "3867")
print Piece(Blue, Vector(320, 72, -320), Identity(), "3867")
print Piece(White, Vector(-90, -150, 90), Identity(), "LIGHT")
print Piece(White, Vector(90, -150, 90), Identity(), "LIGHT")
