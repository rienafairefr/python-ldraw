"""
qtsvg.py - An SVG writer for the ldraw Python package.

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
from collections import OrderedDict

# pylint: disable=no-name-in-module
from PyQt4.QtCore import QPointF, QT_VERSION
from PyQt4.QtGui import QPainterPath, QPolygonF

from ldraw.writers.svg import SVGWriter, write_preamble

if QT_VERSION < 0x40400:
    raise ImportError("This module requires PyQt4, built against Qt 4.4 or higher.")


def _get_new_path(new_path, new_shapes, path, polygon):
    inter = path.intersected(new_path)
    remaining = new_path.subtracted(inter)
    # Combine the new path with the accumulated path and simplify
    # the result.
    path = path.united(new_path)
    path = path.simplified()
    piece_dict = new_shapes.setdefault(polygon.piece, OrderedDict())
    colour_path = piece_dict.get(polygon.colour, QPainterPath())
    piece_dict[polygon.colour] = colour_path.united(remaining)
    return path


class QTSVGWriter(SVGWriter):
    """SVGWriter Using QT"""
    # pylint: disable=too-few-public-methods
    def _write(self, shapes, svg_file, args):

        write_preamble(args, svg_file)

        path = QPainterPath()
        shapes.reverse()
        new_shapes = OrderedDict()
        for points, polygon in shapes:
            new_points = []
            for point in points:
                new_points.append(QPointF(point.x + args.width / 2.0, args.height / 2.0 - point.y))
            new_polygon = QPolygonF(new_points)
            new_path = QPainterPath()
            new_path.addPolygon(new_polygon)
            if path.contains(new_path):
                continue

            path = _get_new_path(new_path, new_shapes, path, polygon)

        self._write_pieces(new_shapes.values(), svg_file)

    def _write_pieces(self, new_shapes, svg_file):
        for piece_dict in new_shapes:
            svg_file.write('<g>\n')
            for colour, colour_path in piece_dict.items():
                if colour_path.isEmpty():
                    continue
                rgb = self.parts.colours.get(colour, "#ffffff")
                shape = '<path style="fill:%s; opacity:%f" d="' % (
                    rgb, self._opacity_from_colour(colour))
                counter = 0
                in_path = False
                while counter < colour_path.elementCount():
                    path = colour_path.elementAt(counter)
                    if path.type == QPainterPath.MoveToElement:
                        if in_path:
                            shape += 'Z '
                        shape += 'M %.6f %.6f ' % (path.x, path.y)
                        in_path = True
                    elif path.type == QPainterPath.LineToElement:
                        shape += 'L %.6f %.6f ' % (path.x, path.y)
                    counter += 1
                if in_path:
                    shape += 'Z'
                shape += '" />\n'
                svg_file.write(shape)
            svg_file.write('</g>\n')
        svg_file.write("</svg>\n")
        svg_file.close()
