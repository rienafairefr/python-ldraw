import codecs
import re

from ldraw.colour import Colour
from ldraw.errors import PartError
from ldraw.geometry import Matrix, Vector
from ldraw.lines import (
    OptionalLine,
    Quadrilateral,
    Line,
    Triangle,
    MetaCommand,
    Comment,
)
from ldraw.pieces import Piece


ENDS_DOT_DAT = re.compile(r"\.DAT$", flags=re.IGNORECASE)


def colour_from_str(colour_str):
    """ gets a Colour from a string """
    try:
        return int(colour_str)
    except ValueError:
        if colour_str.startswith("0x2"):
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
    rows = [
        list(map(float, pieces[4:7])),
        list(map(float, pieces[7:10])),
        list(map(float, pieces[10:13])),
    ]
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
    return Quadrilateral(
        Colour(colour),
        Vector(*point1),
        Vector(*point2),
        Vector(*point3),
        Vector(*point4),
    )


def _optional_line(pieces):
    if len(pieces) != 13:
        raise PartError("Invalid line data")
    colour = colour_from_str(pieces[0])
    point1 = map(float, pieces[1:4])
    point2 = map(float, pieces[4:7])
    point3 = map(float, pieces[7:10])
    point4 = map(float, pieces[10:13])
    return OptionalLine(
        Colour(colour),
        Vector(*point1),
        Vector(*point2),
        Vector(*point3),
        Vector(*point4),
    )


HANDLERS = {
    "0": _comment_or_meta,
    "1": _sub_file,
    "2": _line,
    "3": _triangle,
    "4": _quadrilateral,
    "5": _optional_line,
}


class Part(object):
    """
    Contains data from a LDraw part file
    """

    def __init__(self, path=None, file=None):
        if path is None and file is None:
            raise ValueError('Part loading: needs path or file')

        if path is not None:
            self.path = path
            self.file = codecs.open(self.path, "r", encoding="utf-8")
        elif file is not None:
            self.file = file
            self.path ='%file-like object%'
        self._category = None
        self._description = None

    @property
    def lines(self):
        try:
            for line in self.file:
                yield line
            self.file.seek(0)
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
                raise PartError(
                    "Unknown command (%s) in %s at line %i"
                    % (pieces[0], self.path, number)
                )
            try:
                yield handler(pieces[1:])
            except PartError as parse_error:
                raise PartError(
                    parse_error.message + " in %s at line %i" % (self.path, number)
                )

    @property
    def description(self):
        if self._description is None:
            self._description = " ".join(next(self.lines).split()[1:])
        return self._description

    @property
    def category(self):
        if self._category is None:
            for obj in self.objects:
                if not isinstance(obj, Comment) and not isinstance(obj, MetaCommand):
                    self._category = None
                    break
                elif isinstance(obj, MetaCommand) and obj.type == "CATEGORY":
                    self._category = obj.text
                    break

        return self._category
