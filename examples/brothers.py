#!/usr/bin/env python

"""
brothers.py - An example of figure construction.

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
from ldraw.library.parts.minifig.accessories import GunRevolver, CapWithLongFlatPeak
from ldraw.library.parts.minifig.torsos import Torso
from ldraw.pieces import Group, Piece

group = Group(Vector(0, 0, 0), Identity())

figure = Person(group=group)
print(figure.head(Yellow))
print(figure.hat(Green, CapWithLongFlatPeak))  # Cap
print(figure.torso(Red, Torso))  # Torso
print(figure.left_arm(Red))
print(figure.left_hand(Yellow))
print(figure.right_arm(Red, -60))
print(figure.right_hand(Yellow, -10))
print(figure.right_hand_item(Black,
                             Vector(0, -1, -10), 0, GunRevolver))  # Gun Revolver
print(figure.hips(Blue))
print(figure.left_leg(Blue))
print(figure.right_leg(Blue, -30))

group.position = Vector(60, 0, 0)
group.matrix = Identity().rotate(30, YAxis)
for piece in group.pieces:
    print(piece)

# print Piece(Grey, Vector(0, 72, 0), Identity(), "3867")

# Camera should be at 120.0,0.0,-200.0 in LDraw coordinates.
