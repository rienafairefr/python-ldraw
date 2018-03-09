"""
svg.py - An SVG writer for the ldraw Python package.

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

from ldraw.geometry import Identity, Vector, Vector2D
from ldraw.parts import Parts
from ldraw.lines import Quadrilateral, Line, Triangle
from ldraw.pieces import Piece


class Polygon(object):
    def __init__(self, zmin, points, colour):
        self.zmin = zmin
        self.points = points
        self.colour = colour

    def __lt__(self, other):
        return self.zmin < other.zmin


def _current_colour(colour, current_colour):
    if colour.code == 16:
        return current_colour
    else:
        return colour.code


SVG_PREAMBLE = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="{width:.6f}cm" \
height="{width:.6f}cm" \
viewBox="{view1:.6f} {view2:.6f} {width:.6f} {height:.6f}" \
xmlns="http://www.w3.org/2000/svg" version="1.1">
"""


SVG_LINE = """<line stroke="{rgb}" \
stroke-width="{stroke_width}" \
opacity="{opacity:.6f}" \
x1="{point1.x:.6f}" \
y1="{point1.y:.6f}" \
x2="{point2.x:.6f}" \
y2="{point2.y:.6f}" />
"""

SVG_POLYGON_PREAMBLE ="""<polygon fill="{rgb}" \
stroke="{stroke_colour}" \
stroke-width="{stroke_width}" \
opacity="{opacity:.6f}" \
points=\""""


class SVGWriter(object):
    def __init__(self, camera_position, axes, parts):
        self.parts = parts
        self.lights = []
        self.minimum = Vector(0, 0, 0)
        self.maximum = Vector(0, 0, 0)
        self.bbox_cache = {}
        self.camera_position = camera_position
        self.axes = axes

    def write(self, model, svg_file, width, height, stroke_colour=None, stroke_width=None, background_colour=None):
        polygons = self._polygons_from_objects(model)
        self._sort_polygons(polygons)
        shapes = self._project_polygons(width, height, polygons)
        self._write(shapes, svg_file, width, height, stroke_colour, stroke_width, background_colour)

    def _write(self, shapes, svg_file, width, height, stroke_colour=None, stroke_width=None, background_colour=None):
        svg_file.write(SVG_PREAMBLE.format(view1=0.0, view2=0.0, width=width, height=height))
        if stroke_width is None:
            stroke_width = "0.1%"
        if background_colour is not None:
            svg_file.write('<polygon fill="%s" ' % background_colour)
            svg_file.write('points="%.6f,%.6f %.6f,%.6f %.6f,%.6f %.6f,%.6f" />\n' % (
                0.0, 0.0, width, 0.0, width, height, 0.0, height))
        for points, colour in shapes:
            rgb = self.parts.colours.get(colour, "#ffffff")
            if len(points) == 2:
                point1 = Vector2D(points[0][0] + width / 2.0, height / 2.0 - points[0][1])
                point2 = Vector2D(points[1][0] + width / 2.0, height / 2.0 - points[1][1])

                svg_file.write(SVG_LINE.format(rgb=rgb, stroke_width=stroke_width, opacity=self._opacity_from_colour(colour),
                                               point1=point1, point2=point2))
            else:
                svg_file.write(SVG_POLYGON_PREAMBLE.format(rgb=rgb,
                                                           stroke_colour=stroke_colour if stroke_colour else rgb,
                                                           stroke_width=stroke_width,
                                                           opacity=self._opacity_from_colour(colour)))
                for x, y in points:
                    point = Vector2D(x + width / 2.0, height / 2.0 - y)
                    svg_file.write('{point.x:.6f},{point.y:.6f} '.format(point=point) )
                svg_file.write('" />\n')
        svg_file.write("</svg>\n")
        svg_file.close()

    def _opacity_from_colour(self, colour):
        return self.parts.alpha_values.get(colour, 255) / 255.0

    def _polygons_from_objects(self, model, current_colour=15, current_matrix=Identity(),
                               current_position=Vector(0, 0, 0)):
        # Extract polygons from objects, filtering out those behind the camera.
        polygons = []
        c = self.camera_position
        x, y, z = self.axes
        for obj in model.objects:
            if isinstance(obj, Piece):
                if obj.part == "LIGHT":
                    continue
                colour = _current_colour(obj.colour, current_colour)
                part = self.parts.part(code=obj.part)
                if part:
                    matrix = obj.matrix
                    polygons += self._polygons_from_objects(
                        part, colour, current_matrix * matrix,
                        current_position + current_matrix * obj.position)
                else:
                    sys.stderr.write("Part not found: %s\n" % obj.part)
            elif isinstance(obj, Line):
                p1 = current_matrix * obj.p1 + current_position - c
                p2 = current_matrix * obj.p2 + current_position - c
                r1 = Vector(p1.dot(x), p1.dot(y), p1.dot(z))
                r2 = Vector(p2.dot(x), p2.dot(y), p2.dot(z))
                if r1.z >= 0 or r2.z >= 0:
                    continue
                colour = _current_colour(obj.colour, current_colour)
                polygons.append(Polygon(min(r1.z, r2.z), [r1, r2], colour))
            elif isinstance(obj, Triangle):
                p1 = current_matrix * obj.p1 + current_position - c
                p2 = current_matrix * obj.p2 + current_position - c
                p3 = current_matrix * obj.p3 + current_position - c
                if abs((p3 - p1).cross(p2 - p1)) == 0:
                    continue
                r1 = Vector(p1.dot(x), p1.dot(y), p1.dot(z))
                r2 = Vector(p2.dot(x), p2.dot(y), p2.dot(z))
                r3 = Vector(p3.dot(x), p3.dot(y), p3.dot(z))
                if r1.z >= 0 or r2.z >= 0 or r3.z >= 0:
                    continue
                colour = _current_colour(obj.colour, current_colour)
                polygons.append(Polygon(min(r1.z, r2.z, r3.z), [r1, r2, r3], colour))
            elif isinstance(obj, Quadrilateral):
                p1 = current_matrix * obj.p1 + current_position - c
                p2 = current_matrix * obj.p2 + current_position - c
                p3 = current_matrix * obj.p3 + current_position - c
                p4 = current_matrix * obj.p4 + current_position - c
                if abs((p3 - p1).cross(p2 - p1)) == 0:
                    continue
                if abs((p3 - p1).cross(p4 - p1)) == 0:
                    continue
                r1 = Vector(p1.dot(x), p1.dot(y), p1.dot(z))
                r2 = Vector(p2.dot(x), p2.dot(y), p2.dot(z))
                r3 = Vector(p3.dot(x), p3.dot(y), p3.dot(z))
                r4 = Vector(p4.dot(x), p4.dot(y), p4.dot(z))
                if r1.z >= 0 or r2.z >= 0 or r3.z >= 0 or r4.z >= 0:
                    continue
                colour = _current_colour(obj.colour, current_colour)
                polygons.append(Polygon(min(r1.z, r2.z, r3.z, r4.z), [r1, r2, r3, r4], colour))
        return polygons

    def _sort_polygons(self, polygons):
        polygons.sort()

    def _project_polygons(self, width, height, polygons):
        # vx' = width + az
        # vy' = height + bz
        a = 0.5
        b = 0.5
        w = width / 2.0
        h = height / 2.0
        new_polygons = []
        for polygon in polygons:
            new_points = []
            for point in polygon.points:
                new_points.append((w * (point.x / (w + a * -point.z)),
                                   h * (point.y / (h + b * -point.z))))
            new_polygons.append((new_points, polygon.colour))
        return new_polygons
