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
# pylint: disable=too-few-public-methods

import os
import re
import codecs


import inflect
from attrdict import AttrDict

from ldraw.colour import Colour
from ldraw.config import get_config
from ldraw.geometry import Matrix, Vector
from ldraw.lines import OptionalLine, Quadrilateral, Line, Triangle, MetaCommand, Comment
from ldraw.pieces import Piece
from ldraw.utils import camel


class PartError(Exception):
    """ An exception happening during Part file processing """
    pass


DOT_DAT = re.compile(r"\.DAT", flags=re.IGNORECASE)
ENDS_DOT_DAT = re.compile(r"\.DAT$", flags=re.IGNORECASE)


class Parts(object):
    # pylint: disable=too-many-instance-attributes
    """ Part class """
    ColourAttributes = ("CHROME", "PEARLESCENT", "RUBBER", "MATTE_METALLIC",
                        "METAL")

    def __init__(self, path=get_config()['parts.lst']):
        self.path = None
        self.parts_dirs = []
        self.parts_subdirs = {}
        self.parts_by_name = {}
        self.parts_by_code = {}

        self.primitives_by_name = {}
        self.primitives_by_code = {}

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
        inflect_engine = inflect.engine()

        self.minifig_descriptions = {
            k: camel(inflect_engine.singular_noun(k)) for k in self.parts['minifig']
        }

        self.load(path)

    def load(self, path):
        """ load a Part from a path """
        try:
            self.try_load(path)
        except IOError:
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

    def try_load(self, path):
        """ try loading a Part from a path """
        part_file = codecs.open(path, 'r', encoding='utf-8')
        for line in part_file.readlines():
            pieces = re.split(DOT_DAT, line)
            if len(pieces) != 2:
                break

            code, description = self.section_find(pieces)
            self.parts_by_name[description] = code
            self.parts_by_code[code] = description

    def section_find(self, pieces):
        """ returns code, description from a pieces element """
        code = pieces[0]
        description = pieces[1].strip()
        for key, section in self.parts['minifig'].items():
            searched = self.minifig_descriptions[key]
            index_find = description.find(searched)

            if index_find != -1 and (
                    index_find + len(searched) == len(description) or
                    description[index_find + len(searched)] == " "):
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
        return code, description

    def part(self, description=None, code=None):
        """
        Gets a Part from its description or code
        :param description:
        :param code:
        :return:
        """
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
            if not isinstance(obj, MetaCommand) or not obj.text.startswith("!COLOUR"):
                continue
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

            alpha = self.alpha_values.get(name, 255)
            colour = Colour(code, name, rgb,
                            alpha, colour_attributes)
            self.colours_by_name[name] = colour
            self.colours_by_code[code] = colour

    def _load_primitives(self, path):
        try:
            part_path = codecs.open(path, 'r', encoding='utf-8')
            for line in part_path.readlines():
                pieces = re.split(DOT_DAT, line)
                if len(pieces) != 2:
                    break
                code = pieces[0]
                description = pieces[1].strip()
                self.primitives_by_name[description] = code
                self.primitives_by_code[code] = description
        except IOError:
            raise PartError("Failed to load primitives file: %s" % path)


def colour_from_str(colour_str):
    """ gets a Colour from a string """
    try:
        return int(colour_str)
    except ValueError:
        if colour_str.startswith('0x2'):
            return Colour(rgb="#" + colour_str[3:], alpha=255)


def _comment_or_meta(pieces):
    if not pieces:
        return Comment("")
    elif pieces[0][:1] == "!":
        return MetaCommand(" ".join(pieces))
    return Comment(" ".join(pieces))


def _sub_file(pieces):
    if len(pieces) != 14:
        raise PartError("Invalid part data")
    colour = colour_from_str(pieces[0])
    position = list(map(float, pieces[1:4]))
    rows = [list(map(float, pieces[4:7])),
            list(map(float, pieces[7:10])),
            list(map(float, pieces[10:13]))]
    part = pieces[13].upper()
    if re.search(ENDS_DOT_DAT, part):
        part = part[:-4]
    return Piece(Colour(colour), Vector(*position), Matrix(rows), part)


def _line(pieces):
    if len(pieces) != 7:
        raise PartError("Invalid line data")
    colour = colour_from_str(pieces[0])
    point1 = map(float, pieces[1:4])
    point2 = map(float, pieces[4:7])
    return Line(Colour(colour), Vector(*point1), Vector(*point2))


def _triangle(pieces):
    if len(pieces) != 10:
        raise PartError("Invalid triangle data")
    colour = colour_from_str(pieces[0])
    point1 = map(float, pieces[1:4])
    point2 = map(float, pieces[4:7])
    point3 = map(float, pieces[7:10])
    return Triangle(Colour(colour), Vector(*point1), Vector(*point2), Vector(*point3))


def _quadrilateral(pieces):
    if len(pieces) != 13:
        raise PartError("Invalid quadrilateral data")
    colour = colour_from_str(pieces[0])
    point1 = map(float, pieces[1:4])
    point2 = map(float, pieces[4:7])
    point3 = map(float, pieces[7:10])
    point4 = map(float, pieces[10:13])
    return Quadrilateral(Colour(colour), Vector(*point1), Vector(*point2),
                         Vector(*point3), Vector(*point4))


def _optional_line(pieces):
    if len(pieces) != 13:
        raise PartError("Invalid line data")
    colour = colour_from_str(pieces[0])
    point1 = map(float, pieces[1:4])
    point2 = map(float, pieces[4:7])
    point3 = map(float, pieces[7:10])
    point4 = map(float, pieces[10:13])
    return OptionalLine(Colour(colour), Vector(*point1), Vector(*point2),
                        Vector(*point3), Vector(*point4))


class Part(object):
    """
    Contains data from a LDraw part file
    """
    def __init__(self, path):
        self._handlers = {
            "0": _comment_or_meta,
            "1": _sub_file,
            "2": _line,
            "3": _triangle,
            "4": _quadrilateral,
            "5": _optional_line
        }
        self.path = path
        self.objects = []

        """ Load the Part from its path """
        try:
            lines = codecs.open(path, 'r', encoding='utf-8').readlines()
        except IOError:
            raise PartError("Failed to read part file: %s" % path)
        number = 0
        for line in lines:
            number += 1
            pieces = line.split()
            if not pieces:
                # self.objects.append(BlankLine)
                continue
            try:
                handler = self._handlers[pieces[0]]
            except KeyError:
                raise PartError("Unknown command (%s) in %s at line %i" % (path, pieces[0], number))
            try:
                obj = handler(pieces[1:])
                self.objects.append(obj)
            except PartError as parse_error:
                raise PartError(parse_error.message + ' in %s at line %i' % (self.path, number))
