#!/usr/bin/env python

"""
stairs.py - An example using groups to duplicate parts of a scene.

Copyright (C) 2010 David Boddie <david@boddie.org.uk>

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
from ldraw.figure import *
from ldraw.geometry import Identity
from ldraw.library.colours import *
from ldraw.library.parts.minifig.accessories import ToolMagnifyingGlass
from ldraw.library.parts.minifig.hats import TopHat
from ldraw.library.parts.minifig.heads import HeadWithMonocle_Scar_AndMoustachePattern
from ldraw.library.parts.minifig.torsos import TorsoWithBlackSuit_RedShirt_GoldClaspsPattern
from ldraw.library.parts.others import Plate6X6, Brick2X3, Brick1X1, Arch1X6
from ldraw.pieces import Group, Piece

group = Group(Vector(0, 0, -40), Identity())

figure = Person(group=group)
figure.head(Yellow, part=HeadWithMonocle_Scar_AndMoustachePattern)
figure.hat(Black, TopHat)
figure.torso(Black, TorsoWithBlackSuit_RedShirt_GoldClaspsPattern)
figure.left_arm(Black, 70)
figure.left_hand(White, 0)
figure.right_arm(Black, -30)
figure.right_hand(White, 0)

figure.right_hand_item(Chrome_Silver, Vector(0, -58, -20), 0, ToolMagnifyingGlass)
figure.hips(Black)
figure.left_leg(Black, 50)
figure.right_leg(Black, -40)

group.position = Vector(-100, 40, -120)
group.matrix = Identity().rotate(-30, ZAxis).rotate(90, YAxis)
for piece in group.pieces:
    print(piece)

stairs = Group()

x = -120
y = 144
z = -160
steps = 5
Piece(Dark_Blue, Vector(x, y, z + 40), Identity(), Plate6X6, group=stairs)
for i in range(0, steps):
    for pz in range(z, z + 120, 40):
        Piece(Dark_Blue, Vector(x + 50 + (i * 40), y - 24 - (i * 24), pz),
              Identity(), Brick2X3, group=stairs)

for piece in stairs.pieces:
    print(piece)

staircases = 7
for i in range(1, staircases + 1):
    stairs.position = Vector(0, i * (8 + steps * 24), 0)
    stairs.matrix = Identity().rotate(-90 * i, YAxis)
    for piece in stairs.pieces:
        print(piece)

top_y = y - (steps * 24) - 8
print(Piece(Dark_Blue, Vector(120, top_y, -120), Identity(), Plate6X6))

for i in range(1, 5):
    print(Piece(Dark_Red, Vector(170, top_y - (i * 24), -170),
                Identity(), Brick1X1))
    print(Piece(Dark_Red, Vector(70, top_y - (i * 24), -170),
                Identity(), Brick1X1))

print(Piece(Dark_Red, Vector(120, top_y - (5 * 24), -170),
            Identity(), Arch1X6))

print(Piece(White, Vector(200, -200, 200), Identity(), "LIGHT"))
print(Piece(White, Vector(200, -200, -200), Identity(), "LIGHT"))
print(Piece(White, Vector(-200, -200, 200), Identity(), "LIGHT"))
print(Piece(White, Vector(-200, -200, -200), Identity(), "LIGHT"))
