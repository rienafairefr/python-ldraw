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

import sys
from ldraw.colours import *
from ldraw.figure import *
from ldraw.geometry import Identity, XAxis
from ldraw.parts import Parts
from ldraw.pieces import Group, Piece

if len(sys.argv) != 2:

    sys.stderr.write("Usage: %s <parts file>\n" % sys.argv[0])
    sys.exit(1)

parts = Parts(sys.argv[1])

group = Group(Vector(0, 0, -40), Identity())

figure = Person(group = group)
figure.head(Yellow, part = parts.Heads["Head with Monocle, Scar, and Moustache Pattern"])
figure.hat(Black, parts.Hats["Top Hat"])
figure.torso(Black, parts.Torsos["Torso with Black Suit, Red Shirt, Gold Clasps Pattern"])
figure.left_arm(Black, 70)
figure.left_hand(White, 0)
figure.right_arm(Black, -30)
figure.right_hand(White, 0)
figure.right_hand_item(ChromeSilver, Vector(0, -58, -20), 0, parts.parts["Minifig Tool Magnifying Glass"])
figure.hips(Black)
figure.left_leg(Black, 50)
figure.right_leg(Black, -40)

group.position = Vector(-100, 40, -120)
group.matrix = Identity().rotate(-30, ZAxis).rotate(90, YAxis)
for piece in group.pieces: print piece

stairs = Group()

x = -120
y = 144
z = -160
steps = 5
Piece(DarkBlue, Vector(x, y, z + 40), Identity(), "3958", group = stairs)
for i in range(0, steps):
    for pz in range(z, z + 120, 40):
        Piece(DarkBlue, Vector(x + 50 + (i * 40), y - 24 - (i * 24), pz), Identity(), "3002", group = stairs)

for piece in stairs.pieces: print piece

staircases = 7
for i in range(1, staircases + 1):
    stairs.position = Vector(0, i * (8 + steps * 24), 0)
    stairs.matrix = Identity().rotate(-90 * i, YAxis)
    for piece in stairs.pieces: print piece

top_y = y - (steps * 24) - 8
print Piece(DarkBlue, Vector(120, top_y, -120), Identity(), "3958")

for i in range(1, 5):
    print Piece(DarkRed, Vector(170, top_y - (i * 24), -170), Identity(), "3005")
    print Piece(DarkRed, Vector(70, top_y - (i * 24), -170), Identity(), "3005")

print Piece(DarkRed, Vector(120, top_y - (5 * 24), -170), Identity(), "3455")

print Piece(White, Vector(200, -200, 200), Identity(), "LIGHT")
print Piece(White, Vector(200, -200, -200), Identity(), "LIGHT")
print Piece(White, Vector(-200, -200, 200), Identity(), "LIGHT")
print Piece(White, Vector(-200, -200, -200), Identity(), "LIGHT")

# ldr2pov.py /data2/david/lego/LDraw/LDRAW-modified/parts.lst Models/stairs.ldr Scenes/stairs.pov 130.0,400.0,130.0 10.0,-150.0,-25.0 --sky 0.0,0.0,0.3
# povray +IScenes/stairs.pov +Ostairs.png +FN16 +W2600 +H2000 +V -D +X +Q9
