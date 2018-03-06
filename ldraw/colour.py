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


class Colour(object):
    def __init__(self, code=None, name=None, rgb=None, alpha=None, colour_attributes=None):
        self.code = code
        self.name = name
        self.rgb = rgb
        self.alpha = alpha
        self.colour_attributes = colour_attributes

    def __eq__(self, other):
        if isinstance(other, Colour):
            return self.code == other.code
        else:
            return self.code == other

    def __hash__(self):
        return hash(self.code)
