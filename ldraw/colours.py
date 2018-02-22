"""
colours.py - Colour definitions for the Python ldraw package.

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


class Colour:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Colour):
            return self.value == other.value
        else:
            return self.value == other

    def __hash__(self):
        return hash(self.value)


Black = Colour(0)
Blue = Colour(1)
Green = Colour(2)
Teal = Colour(3)
Red = Colour(4)
DarkPink = Colour(5)
Brown = DarkOrange = Colour(6)
Grey = Colour(7)
DarkGrey = Colour(8)
LightBlue = Colour(9)
BrightGreen = Colour(10)
Turquoise = Colour(11)
LightRed = Colour(12)
Pink = Colour(13)
Yellow = Colour(14)
White = Colour(15)
Current = Colour(16)
LightGreen = Colour(17)
LightYellow = Colour(18)
Tan = Colour(19)
LightPurple = Colour(20)
GlowInTheDark = Colour(21)
Purple = Colour(22)
VioletBlue = Colour(23)
Orange = Colour(25)
Magenta = Colour(26)
Lime = Colour(27)
TransBlue = Colour(33)
TransGreen = Colour(34)
TransRed = Colour(36)
TransPurple = Colour(37)
Smoke = Colour(39)
LightTransBlue = Colour(41)
TransNeonGreen = Colour(42)
TransPink = Colour(45)
TransYellow = Colour(46)
Clear = Colour(47)
TransOrange = Colour(57)
BlackRubber = Colour(256)
DarkBlue = Colour(272)
DarkRed = Colour(320)
ChromeGold = Colour(334)
SandRed = Colour(335)
EarthOrange = Colour(366)
SandViolet = Colour(373)
GreyRubber = Colour(375)
SandGreen = Colour(378)
SandBlue = Colour(379)
ChromeSilver = Colour(383)
LightOrange = Colour(462)
DarkOrange = Colour(484)
LightGrey = Colour(503)
