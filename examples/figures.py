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
from __future__ import print_function
from ldraw.library.colours import *
from ldraw.figure import *
from ldraw.library.parts.minifig.accessories import HelmetClassicWithThickChinGuardAndVisorDimples as HelmetClassic, Torch, MetalDetector
from ldraw.library.parts.minifig.torsos import TorsoWithClassicSpacePattern
from ldraw.library.parts.others import Baseplate16X16, Rock1X1Crystal5Point
from ldraw.pieces import Piece

figure = Person(Vector(0, 0, -10))
print(figure.head(Yellow, 30))
print(figure.hat(White, HelmetClassic))
print(figure.torso(White, TorsoWithClassicSpacePattern))
print(figure.backpack(White, Vector(0, -2, 0)))
print(figure.hips_and_legs(White))
print(figure.left_arm(White, -45))
print(figure.left_hand(White, 0))
print(figure.left_hand_item(Light_Grey,
                            Vector(0, -11, -12), 0, Torch))  # Torch
print(figure.right_arm(White, 0))
print(figure.right_hand(White, 0))
print(figure.right_hand_item(Light_Grey,
                             Vector(0, -23, -12), 90, MetalDetector))  # Metal detector

figure = Person(Vector(97.5, 0, 57.5),
                Identity().rotate(45, YAxis))
print(figure.head(Yellow, -15))
print(figure.hat(Red, HelmetClassic))
print(figure.torso(Red, TorsoWithClassicSpacePattern))
print(figure.backpack(Red, Vector(0, -2, 0)))
print(figure.hips(Red))
print(figure.left_leg(Red, -55))
print(figure.right_leg(Red, 0))
print(figure.left_arm(Red, -45))
print(figure.left_hand(Red, 0))
print(figure.right_arm(Red, -30))
print(figure.right_hand(Red, 0))
print(figure.right_hand_item(Light_Grey, Vector(0, -11, -12), 0, Torch))  # Torch
print('')
print(Piece(Light_Grey, Vector(0, 72, 0), Identity(), Baseplate16X16))
print(Piece(Light_Grey, Vector(60, 72, -60), Identity(), Rock1X1Crystal5Point))

# Camera should be at 160.0,-80.0,-240.0 in LDraw coordinates.
