#!/usr/bin/env python

"""
diver.py - An example of figure construction.

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

figure = Person(Vector(0, 0, -10), Identity().rotate(-15, ZAxis).rotate(20, XAxis))
print figure.head(Yellow, -15)
print figure.hat(Black, "30090") # Diver Mask
print figure.hat(Black, "3901")  # Hair Male
print figure.torso(Yellow, "973") # Torso
print figure.backpack(Black, Vector(0, -2, 0), "3838") # Airtanks
print figure.hips(Green)
print figure.left_leg(Yellow, 30)
print figure.left_shoe(Black, 10, "2599") # Flipper
print figure.right_leg(Yellow, -10)
print figure.right_shoe(Black, -10, "2599") # Flipper
print figure.left_arm(Yellow, -45)
print figure.left_hand(Yellow, 10)
print figure.left_hand_item(Grey, Vector(0, 0, -12), -15, "30148") # Camera Movie
print figure.right_arm(Yellow, 60)
print figure.right_hand(Yellow, 0)
print

print Piece(Colour(15), Vector(-50, -50, -100), Identity(), "LIGHT")
