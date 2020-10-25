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
from collections import defaultdict

from attrdict import AttrDict

from ldraw.colour import Colour
from ldraw.config import get_config
from ldraw.geometry import Matrix, Vector
from ldraw.lines import OptionalLine, Quadrilateral, Line, Triangle, MetaCommand, Comment
from ldraw.pieces import Piece


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

    def __init__(self, parts_lst=None, others_threshold=None):
        config = get_config()
        if parts_lst is None:
            parts_lst = config['parts.lst']
        if others_threshold is None:
            others_threshold = config.get('others_threshold', 5)
        self.path = None
        self.parts_dirs = []
        self.parts_subdirs = {}
        self.parts_by_name = {}
        self.parts_by_code = {}
        self.parts_by_code_name = {}

        self.primitives_by_name = {}
        self.primitives_by_code = {}

        self.colours = {}
        self.alpha_values = {}
        self.colour_attributes = {}

        self.colours_by_name = {}
        self.colours_by_code = {}

        self.parts = AttrDict(
            minifig=AttrDict(
                hats={},
                heads={},
                torsos={},
                hips={},
                legs={},
                arms={},
                hands={},
                accessories={}
            )
        )

        self.minifig_descriptions = {
            'torsos': 'Torso',
            'hips': 'Hip',
            'arms': 'Arm',
            'heads': 'Head',
            'accessories': 'Accessory',
            'hands': 'Hand',
            'hats': 'Hat',
            'legs': 'Leg'
        }

        self.parts_by_category = defaultdict(lambda: {})

        self.load(parts_lst)

        # relatively useless categories
        for k in list(self.parts_by_category.keys()):
            if len(self.parts_by_category.get(k)) < others_threshold:
                self.parts_by_category['others'].update(self.parts_by_category.pop(k))

        # reference in others
        for v in self.parts_by_category.values():
            self.parts_by_category['others'].update(v)

        for k in list(self.parts_by_category.keys()):
            split = k.split()
            if len(split) == 1:
                value = self.parts_by_category.pop(k)
                if k in self.parts:
                    self.parts[k][''] = value
                else:
                    self.parts[k] = value
        pass

    def load(self, parts_lst):
        """ load parts from a path """
        try:
            self.try_load(parts_lst)
        except IOError:
            raise PartError("Failed to load parts file: %s" % parts_lst)

        # If we successfully loaded the files then record the path and look for
        # part files.
        self.path = parts_lst
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

        def get_category(part_description):
            return part_description.strip(' ~=_|').split()[0]

        for code, description in self.parts_by_code_name:
            part = self.part(code=code)
            self.parts_by_code_name[(code, description)] = part
            default_category = get_category(description)
            category = part.category
            self.parts_by_category[default_category.lower()][description] = code
            if category:
                self.parts_by_category[category.lower()][description] = code

    def try_load(self, parts_lst):
        """ try loading parts from a parts.lst file """
        parts_lst_file = codecs.open(parts_lst, 'r', encoding='utf-8')
        for line in parts_lst_file.readlines():
            pieces = re.split(DOT_DAT, line)
            if len(pieces) != 2:
                break

            code, description = self.section_find(pieces)
            self.parts_by_name[description] = code
            self.parts_by_code[code] = description
            self.parts_by_code_name[(code, description)] = None

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
                pass
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
            if os.path.exists(path):
                return Part(path)
            continue
        raise PartError('part file not found: %s' % code)

    def _load_colours(self, path):
        try:
            colours_part = Part(path)
        except PartError:
            return
        for obj in colours_part.objects:
            if not isinstance(obj, MetaCommand) or not obj.type == "COLOUR":
                continue
            pieces = obj.text.split()
            try:
                name = pieces[0]
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
                alpha = int(pieces[alpha_at])
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
        return MetaCommand(pieces[0][1:], " ".join(pieces[1:]))
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


HANDLERS = {
    "0": _comment_or_meta,
    "1": _sub_file,
    "2": _line,
    "3": _triangle,
    "4": _quadrilateral,
    "5": _optional_line
}


class Part(object):
    """
    Contains data from a LDraw part file
    """

    def __init__(self, path):
        self.path = path
        self._category = None
        self._description = None

    @property
    def lines(self):
        try:
            for line in codecs.open(self.path, 'r', encoding='utf-8'):
                yield line
        except IOError:
            raise PartError("Failed to read part file: %s" % self.path)

    @property
    def objects(self):
        """ Load the Part from its path """
        for number, line in enumerate(self.lines):
            pieces = line.split()
            if not pieces:
                # self.objects.append(BlankLine)
                continue
            try:
                handler = HANDLERS[pieces[0]]
            except KeyError:
                raise PartError("Unknown command (%s) in %s at line %i" % (self.path, pieces[0], number))
            try:
                yield handler(pieces[1:])
            except PartError as parse_error:
                raise PartError(parse_error.message + ' in %s at line %i' % (self.path, number))

    @property
    def description(self):
        if self._description is None:
            self._description = ' '.join(next(self.lines).split()[1:])
        return self._description

    @property
    def category(self):
        if self._category is None:
            for obj in self.objects:
                if not isinstance(obj, Comment) and not isinstance(obj, MetaCommand):
                    self._category = None
                    break
                elif isinstance(obj, MetaCommand) and obj.type == 'CATEGORY':
                    self._category = obj.text
                    break

        return self._category
