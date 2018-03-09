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

from PyQt4.QtCore import QPointF, QT_VERSION
from PyQt4.QtGui import QPainterPath, QPolygonF

from ldraw.geometry import Vector
from ldraw.writers.svg import SVGWriter, SVG_PREAMBLE

if QT_VERSION < 0x40400:
    raise ImportError("This module requires PyQt4, built against Qt 4.4 or higher.")


class Polygon:
    def __init__(self, zmin, points, colour, piece):
        self.zmin = zmin
        self.points = points
        self.colour = colour
        self.piece = piece

    def __lt__(self, other):
        return self.zmin < other.zmin

class QTSVGWriter(SVGWriter):
    """SVGWriter Using QT"""

    def _write(self, shapes, svg_file, svg_args):
        width = svg_args.width
        height = svg_args.height
        stroke_width = svg_args.stroke_width
        background_colour = svg_args.background_colour

        svg_file.write('<?xml version="1.0" standalone="no"?>\n'
                       '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n'
                       '  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
        svg_file.write('<svg width="%.6fcm" height="%.6fcm" ' % (width, height))
        svg_file.write('viewBox="%.6f %.6f %.6f %.6f" '
                       'xmlns="http://www.w3.org/2000/svg" '
                       'version="1.1">\n' % (0.0, 0.0, width, height))
        if stroke_width is None:
            stroke_width = "0.1%"
        if background_colour is not None:
            svg_file.write('<polygon fill="%s" ' % background_colour)
            svg_file.write('points="%.6f,%.6f %.6f,%.6f %.6f,%.6f %.6f,%.6f" />\n' % (
                0.0, 0.0, width, 0.0, width, height, 0.0, height))
        path = QPainterPath()
        shapes.reverse()
        new_shapes = OrderedDict()
        for points, polygon in shapes:
            new_points = []
            for point in points:
                new_points.append(QPointF(point.x + width / 2.0, height / 2.0 - point.y))
            new_polygon = QPolygonF(new_points)
            new_path = QPainterPath()
            new_path.addPolygon(new_polygon)
            if path.contains(new_path):
                continue
            inter = path.intersected(new_path)
            remaining = new_path.subtracted(inter)
            # Combine the new path with the accumulated path and simplify
            # the result.
            path = path.united(new_path)
            path = path.simplified()
            piece_dict = new_shapes.setdefault(polygon.piece, OrderedDict())
            colour_path = piece_dict.get(polygon.colour, QPainterPath())
            piece_dict[polygon.colour] = colour_path.united(remaining)
        for piece, piece_dict in new_shapes.items():
            svg_file.write('<g>\n')
            for colour, colour_path in piece_dict.items():
                if colour_path.isEmpty():
                    continue
                rgb = self.parts.colours.get(colour, "#ffffff")
                shape = '<path style="fill:%s; opacity:%f" d="' % (
                    rgb, self._opacity_from_colour(colour))
                i = 0
                in_path = False
                while i < colour_path.elementCount():
                    p = colour_path.elementAt(i)
                    if p.type == QPainterPath.MoveToElement:
                        if in_path:
                            shape += 'Z '
                        shape += 'M %.6f %.6f ' % (p.x, p.y)
                        in_path = True
                    elif p.type == QPainterPath.LineToElement:
                        shape += 'L %.6f %.6f ' % (p.x, p.y)
                    i += 1
                if in_path:
                    shape += 'Z'
                shape += '" />\n'
                svg_file.write(shape)
            svg_file.write('</g>\n')
        svg_file.write("</svg>\n")
        svg_file.close()
