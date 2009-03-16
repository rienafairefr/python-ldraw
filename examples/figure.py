#!/usr/bin/env python

"""
figure.py - An example of figure construction.

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

from ldraw.colours import *
from ldraw.figure import *

figure = Person()
print figure.head(Yellow, 35)
print figure.hat(Black, "3901")  # Hair Male
print figure.torso(Red, "973") # Torso
print figure.hips(Blue)
print figure.left_leg(Blue, 5)
print figure.right_leg(Blue, 20)
print figure.left_arm(Red, 0)
print figure.left_hand(Yellow, 0)
print figure.right_arm(Red, -90)
print figure.right_hand(Yellow, 0)
print

print Piece(Colour(15), Vector(150, -100, -150), Identity(), "LIGHT")
print Piece(Colour(15), Vector(-150, -100, -150), Identity(), "LIGHT")
print Piece(Colour(15), Vector(0, -100, 150), Identity(), "LIGHT")

# Camera should be at 120.0,-20.0,-140.0 in LDraw coordinates.
