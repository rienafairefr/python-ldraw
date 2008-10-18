#!/usr/bin/env python

"""
figures.py - An example of figure construction.

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
from ldraw.pieces import Piece

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
print figure.right_hand_item(Grey, Vector(0, -23, -12), 90, "4479") # Metal detector
print

figure = Person(Vector(97.5, 0, 57.5), Identity().rotate(45, YAxis))
print figure.head(Yellow, -15)
print figure.hat(Red, "193B")
print figure.torso(Red, "973P90")
print figure.backpack(Red, Vector(0, -2, 0))
print figure.hips(Red)
print figure.left_leg(Red, -55)
print figure.right_leg(Red, 0)
print figure.left_arm(Red, -45)
print figure.left_hand(Red, 0)
print figure.right_arm(Red, -30)
print figure.right_hand(Red, 0)
print figure.right_hand_item(Grey, Vector(0, -11, -12), 0, "3959") # Torch
print

print Piece(Grey, Vector(0, 72, 0), Identity(), "3867")
print Piece(Grey, Vector(60, 72, -60), Identity(), "52")
