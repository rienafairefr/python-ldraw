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
from __future__ import print_function
import random
from ldraw.library.colours import *
from ldraw.figure import *
from ldraw.library.parts.minifig.accessories import DiverMask, HairMale, Airtanks, Flipper, CameraMovie
from ldraw.library.parts.minifig.torsos import Torso
from ldraw.pieces import Piece

figure = Person(Vector(0, 0, -10),
                Identity().rotate(-15, ZAxis).rotate(20, XAxis))
print(figure.head(Yellow, -15))
print(figure.hat(Black, DiverMask))
print(figure.hat(Black, HairMale))
print(figure.torso(Yellow, Torso))
print(figure.backpack(Black, Vector(0, -2, 0), Airtanks))
print(figure.hips(Green))
print(figure.left_leg(Yellow, 30))
print(figure.left_shoe(Black, 10, Flipper))
print(figure.right_leg(Yellow, -10))
print(figure.right_shoe(Black, -10, Flipper))
print(figure.left_arm(Yellow, -45))
print(figure.left_hand(Yellow, 10))
print(figure.left_hand_item(Light_Grey,
                            Vector(0, 0, -12), -15, CameraMovie))  # Camera Movie
print(figure.right_arm(Yellow, 60))
print(figure.right_hand(Yellow, 0))
print('')
print(Piece(White, Vector(-50, -200, -50), Identity(), "LIGHT"))
print(Piece(White, Vector(50, -200, 0), Identity(), "LIGHT"))
print(Piece(White, Vector(0, -200, 50), Identity(), "LIGHT"))

# Camera should be at 120.0,40.0,-200.0 in LDraw coordinates.
