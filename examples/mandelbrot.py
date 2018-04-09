#!/usr/bin/env python

"""
mandelbrot.py - An example of brick artwork.

Copyright (C) 2012 David Boddie <david@boddie.org.uk>

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
from ldraw.library.colours import (Blue_Violet, Blue, Light_Blue,
                                   Light_Green, Green, Yellow,
                                   Orange, Red, Magenta, Purple,
                                   Black, White)
from ldraw.library.parts.others import Brick1X1
from ldraw.pieces import *

colours = [Blue_Violet, Blue, Light_Blue, Light_Green, Green, Yellow,
           Orange, Red, Magenta, Purple]


def draw_mandelbrot(x1, z1, x2, z2, r1, i1, r2, i2):
    y = 0
    z = z1
    while z <= z2:

        i = i1 + (z - z1) * (i2 - i1) / (z2 - z1)

        x = x1
        while x <= x2:

            r = r1 + (x - x1) * (r2 - r1) / (x2 - x1)

            ci = r + i * 1j
            c = ci
            count = 0
            while count < 10 and abs(c) <= 2:
                c = c * c + ci
                count += 1

            if count == 10:
                colour = Black
            else:
                colour = colours[count]

            print(Piece(colour, Vector(x * 20, y, z * 20), Identity(), Brick1X1))
            x += 1

        z += 1


draw_mandelbrot(-16, -12, 16, 12, -2.4, -1.2, 0.8, 1.2)

print(Piece(White, Vector(150, -100, 150), Identity(), "LIGHT"))
