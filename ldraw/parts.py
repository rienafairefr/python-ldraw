"""
parts.py - Part management classes for the Python ldraw package.

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

import os
import re
import inflect
from attrdict import AttrDict

from ldraw.colour import Colour
from ldraw.geometry import Matrix, Vector
from ldraw.lines import OptionalLine, Quadrilateral, Line, Triangle, MetaCommand, Comment, BlankLine
from ldraw.pieces import Piece
import codecs

from ldraw.utils import camel, clean


class PartError(Exception):
    pass


p = inflect.engine()

DOT_DAT = re.compile(r"\.DAT", flags=re.IGNORECASE)
ENDS_DOT_DAT = re.compile(r"\.DAT$", flags=re.IGNORECASE)


class Parts(object):
    ColourAttributes = ("CHROME", "PEARLESCENT", "RUBBER", "MATTE_METALLIC",
                        "METAL")

    def __init__(self, path):
        self.path = None
        self.parts_dirs = []
        self.parts_subdirs = {}
        self.parts_by_name = {}
        self.parts_by_code = {}

        self.colours = {}
        self.alpha_values = {}
        self.colour_attributes = {}

        self.colours_by_name = {}
        self.colours_by_code = {}

        self.parts = {
            'minifig': {
                'hats': {},
                'heads': {},
                'torsos': {},
                'hips': {},
                'legs': {},
                'arms': {},
                'hands': {},
                'accessories': {},
            },
            'others': {

            }}

        self.minifig_descriptions = {k: camel(p.singular_noun(k)) for k in self.parts['minifig']}

        self.load(path)

    def load(self, path):
        try:
            f = codecs.open(path, 'r', encoding='utf-8')
            for line in f.readlines():
                pieces = re.split(DOT_DAT, line)
                if len(pieces) != 2:
                    break
                code = pieces[0]
                description = pieces[1].strip()
                for key, section in self.parts['minifig'].items():
                    searched = self.minifig_descriptions[key]
                    at = description.find(searched)

                    if at != -1 and (
                            at + len(searched) == len(description) or
                            description[at + len(searched)] == " "):
                        if description.startswith("Minifig "):
                            description = description[8:]
                            if description.startswith("(") and description.endswith(")"):
                                description = description[1:-1]
                            section[description] = code
                        break
                else:
                    # The accessories are those Minifig items which do not fall into any
                    # of the above categories.
                    if description.startswith("Minifig "):
                        description = description[8:]
                        if description.startswith("(") and description.endswith(")"):
                            description = description[1:-1]
                        self.parts['minifig']['accessories'][description] = code
                    else:
                        self.parts['others'][description] = code
                self.parts_by_name[description] = code
                self.parts_by_code[code] = description
        except IOError, e:
            raise PartError("Failed to load parts file: %s" % path)
        # If we successfully loaded the files then record the path and look for
        # part files.
        self.path = path
        directory = os.path.split(self.path)[0]
        for item in os.listdir(directory):
            obj = os.path.join(directory, item)
            if item.lower() == "parts" and os.path.isdir(obj):
                self.parts_dirs.append(obj)
                self._find_parts_subdirs(obj)
            elif item.lower() == "p" and os.path.isdir(obj):
                self.parts_dirs.append(obj)
                self._find_parts_subdirs(obj)
            elif item.lower() == "ldconfig" + os.extsep + "ldr":
                self._load_colours(obj)
            elif item.lower() == "p" + os.extsep + "lst" and os.path.isfile(obj):
                self._load_primitives(obj)

        self.parts['minifig'] = AttrDict(self.parts['minifig'])
        self.parts = AttrDict(self.parts)

    def part(self, description=None, code=None):
        if not self.path:
            return None
        if description:
            try:
                code = self.parts_by_name[description]
            except KeyError:
                return None
        elif not code:
            return None
        return self._load_part(code)

    def _find_parts_subdirs(self, directory):
        for item in os.listdir(directory):
            obj = os.path.join(directory, item)
            if os.path.isdir(obj):
                self.parts_subdirs[item] = obj
                self.parts_subdirs[item.lower()] = obj
                self.parts_subdirs[item.upper()] = obj

    def _load_part(self, code):
        code = code.replace("\\", os.sep)
        code = code.replace("/", os.sep)
        if os.sep in code:
            pieces = code.split(os.sep)
            if len(pieces) != 2:
                return None
            try:
                parts_dirs = [self.parts_subdirs[pieces[0]]]
            except KeyError:
                return None
            code = pieces[1]
        else:
            parts_dirs = self.parts_dirs
        paths = []
        for parts_dir in parts_dirs:
            paths.append(os.path.join(parts_dir, code.lower()) + os.extsep + "dat")
            paths.append(os.path.join(parts_dir, code.upper()) + os.extsep + "DAT")
        for path in paths:
            try:
                part = Part(path)
                part.path = os.path.relpath(path, self.path)
            except PartError:
                continue
            else:
                return part
        return None

    def _load_colours(self, path):
        try:
            colours_part = Part(path)
        except PartError:
            return
        for obj in colours_part.objects:
            if isinstance(obj, MetaCommand) and obj.text.startswith("!COLOUR"):
                pieces = obj.text.split()
                try:
                    name = pieces[1]
                    code = int(pieces[pieces.index("CODE") + 1])
                    rgb = pieces[pieces.index("VALUE") + 1]

                    self.colours[name] = rgb
                    self.colours[code] = rgb

                    colour = Colour(code, name, rgb)
                    self.colours_by_name[name] = colour
                    self.colours_by_code[code] = colour

                except (ValueError, IndexError):
                    continue
                try:
                    alpha_at = pieces.index("ALPHA")
                    alpha = int(pieces[alpha_at + 1])
                    self.alpha_values[name] = alpha
                    self.alpha_values[code] = alpha
                except (IndexError, ValueError):
                    pass

                colour_attributes = []
                for attribute in Parts.ColourAttributes:
                    if attribute in pieces:
                        colour_attributes.append(attribute)

                self.colour_attributes[name] = colour_attributes
                self.colour_attributes[code] = colour_attributes

                colour_name = clean(camel(name))
                colour = Colour(code, name, rgb, self.alpha_values.get(name, 255), colour_attributes)
                self.colours_by_name[name] = colour
                self.colours_by_code[code] = colour

    def _load_primitives(self, path):
        try:
            f = codecs.open(path, 'r', encoding='utf-8')
            for line in f.readlines():
                pieces = re.split(DOT_DAT, line)
                if len(pieces) != 2:
                    break
                code = pieces[0]
                description = pieces[1].strip()
                self.parts_by_name[description] = code
        except IOError:
            raise PartError("Failed to load primitives file: %s" % path)


class Part(object):
    def __init__(self, path):
        self._handlers = {
            "0": self._comment_or_meta,
            "1": self._subfile,
            "2": self._line,
            "3": self._triangle,
            "4": self._quadrilateral,
            "5": self._optional_line
        }
        self.load(path)

    def load(self, path):
        self.path = path
        try:
            lines = codecs.open(path, 'r', encoding='utf-8').readlines()
        except IOError:
            raise PartError("Failed to read part file: %s" % path)
        objects = []
        number = 0
        for line in lines:
            number += 1
            pieces = line.split()
            if not pieces:
                objects.append(BlankLine)
                continue
            try:
                handler = self._handlers[pieces[0]]
            except KeyError:
                raise PartError("Unknown command (%s) in %s at line %i" % (path, pieces[0], number))
            objects.append(handler(pieces[1:], number))
        self.objects = objects

    def _comment_or_meta(self, pieces, line):
        if not pieces:
            return Comment("")
        elif pieces[0][:1] == "!":
            return MetaCommand(" ".join(pieces))
        else:
            return Comment(" ".join(pieces))

    def colour_from_str(self, colour_str):
        try:
            return int(colour_str)
        except ValueError:
            if colour_str.startswith('0x2'):
                return Colour(rgb="#" + colour_str[3:], alpha=255)

    def _subfile(self, pieces, line):
        if len(pieces) != 14:
            raise PartError("Invalid part data in %s at line %i" % (self.path, line))
        colour = self.colour_from_str(pieces[0])
        position = map(float, pieces[1:4])
        rows = [map(float, pieces[4:7]),
                map(float, pieces[7:10]),
                map(float, pieces[10:13])]
        part = pieces[13].upper()
        if re.search(ENDS_DOT_DAT, part):
            part = part[:-4]
        return Piece(Colour(colour), Vector(*position), Matrix(rows), part)

    def _line(self, pieces, line):
        if len(pieces) != 7:
            raise PartError("Invalid line data in %s at line %i" % (self.path, line))
        colour = self.colour_from_str(pieces[0])
        p1 = map(float, pieces[1:4])
        p2 = map(float, pieces[4:7])
        return Line(Colour(colour), Vector(*p1), Vector(*p2))

    def _triangle(self, pieces, line):
        if len(pieces) != 10:
            raise PartError("Invalid triangle data in %s at line %i" % (self.path, line))
        colour = self.colour_from_str(pieces[0])
        p1 = map(float, pieces[1:4])
        p2 = map(float, pieces[4:7])
        p3 = map(float, pieces[7:10])
        return Triangle(Colour(colour), Vector(*p1), Vector(*p2), Vector(*p3))

    def _quadrilateral(self, pieces, line):
        if len(pieces) != 13:
            raise PartError("Invalid quadrilateral data in %s at line %i" % (self.path, line))
        colour = self.colour_from_str(pieces[0])
        p1 = map(float, pieces[1:4])
        p2 = map(float, pieces[4:7])
        p3 = map(float, pieces[7:10])
        p4 = map(float, pieces[10:13])
        return Quadrilateral(Colour(colour), Vector(*p1), Vector(*p2),
                             Vector(*p3), Vector(*p4))

    def _optional_line(self, pieces, line):
        if len(pieces) != 13:
            raise PartError("Invalid line data in %s at line %i" % (self.path, line))
        colour = self.colour_from_str(pieces[0])
        p1 = map(float, pieces[1:4])
        p2 = map(float, pieces[4:7])
        p3 = map(float, pieces[7:10])
        p4 = map(float, pieces[10:13])
        return OptionalLine(Colour(colour), Vector(*p1), Vector(*p2),
                            Vector(*p3), Vector(*p4))
