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

from ldraw.geometry import Identity, Vector
from ldraw.parts import Parts
from ldraw.lines import Quadrilateral, Line, Triangle
from ldraw.pieces import Piece


class Polygon:
    def __init__(self, zmin, points, colour):
        self.zmin = zmin
        self.points = points
        self.colour = colour

    def __lt__(self, other):
        return self.zmin < other.zmin


class SVGWriter:
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
        # shapes = self._combine_polygons(shapes)
        # shapes = self._remove_obscured_polygons(shapes)
        self._write(shapes, svg_file, width, height, stroke_colour, stroke_width, background_colour)

    def _write(self, shapes, svg_file, width, height, stroke_colour=None, stroke_width=None, background_colour=None):
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
        for points, colour in shapes:
            rgb = self.parts.colours.get(colour, "#ffffff")
            if len(points) == 2:
                svg_file.write('<line stroke="%s" ' % rgb)
                svg_file.write('stroke-width="%s" ' % stroke_width)
                svg_file.write('opacity="%.6f" ' % self._opacity_from_colour(colour))
                svg_file.write('x1="%.6f" y1="%.6f" ' % (points[0][0] + width / 2.0, height / 2.0 - points[0][1]))
                svg_file.write('x2="%.6f" y2="%.6f" ' % (points[1][0] + width / 2.0, height / 2.0 - points[1][1]))
                svg_file.write('/>\n')
            else:
                svg_file.write('<polygon fill="%s" ' % rgb)
                if stroke_colour:
                    svg_file.write('stroke="%s" ' % stroke_colour)
                else:
                    svg_file.write('stroke="%s" ' % rgb)
                svg_file.write('stroke-width="%s" ' % stroke_width)
                svg_file.write('opacity="%.6f" ' % self._opacity_from_colour(colour))
                svg_file.write('points="')
                for x, y in points:
                    svg_file.write('%.6f,%.6f ' % (x + width / 2.0, height / 2.0 - y))
                svg_file.write('" />\n')
        svg_file.write("</svg>\n")
        svg_file.close()

    def _current_colour(self, colour, current_colour):
        if colour.code == 16:
            return current_colour
        else:
            return colour.code

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
                colour = self._current_colour(obj.colour, current_colour)
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
                colour = self._current_colour(obj.colour, current_colour)
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
                colour = self._current_colour(obj.colour, current_colour)
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
                colour = self._current_colour(obj.colour, current_colour)
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

    def _combine_polygons(self, polygons):
        # Create a dictionary mapping adjacent vertices to polygons with those
        # vertices.
        mapping = {}
        new_polygons = []
        for points, colour in polygons:
            len_points = len(points)
            if len_points == 2:
                new_polygons.append((points, colour))
                continue
            for i in range(len_points):
                p1, p2 = points[i], points[(i + 1) % len_points]
                polygon = Poly2(points)
                polygon.colour = colour
                mapping.setdefault((p1, p2), []).append(polygon)
        discarded = {}
        for key, shared in mapping.items():
            colour = shared[0].colour
            shared = filter(lambda polygon: polygon not in discarded and polygon.colour == colour, shared)
            if len(shared) == 1:
                new_polygons.append((shared[0].points, colour))
                discarded[shared[0]] = None
            elif len(shared) >= 2:
                # Join the two polygons where they share vertices.
                while len(shared) > 1:
                    poly1 = shared.pop()
                    poly2 = shared.pop()
                    polygon = poly1.join(key, poly2)
                    new_polygons.append((polygon.points, colour))
                    discarded[poly1] = None
                    discarded[poly2] = None
                if shared:
                    new_polygons.append((shared[0].points, colour))
                    discarded[shared[0]] = None
        return new_polygons

    def _remove_obscured_polygons(self, polygons):
        # Perform an expensive test to remove obscured polygons.
        polygons.reverse()
        i = 0
        while i < len(polygons):
            points, colour = polygons[i]
            j = i + 1
            while j < len(polygons):
                other_points, other_colour = polygons[j]
                if other_colour != colour:
                    j += 1
                    continue
                for p in other_points:
                    if not self._point_within_polygon(p, points):
                        j += 1
                        break
                else:
                    print "Discarding polygon", polygons[j]
                    del polygons[j]
            i += 1
        polygons.reverse()
        return polygons

    def _point_within_polygon(self, p, points):
        x, y = p
        x1, y1 = points[-1]
        inside = False
        for x2, y2 in points:
            if y1 == y2:
                continue
            if y1 <= y <= y2 or y2 <= y <= y1:
                if x <= x1 == x2:
                    inside = not inside
                elif x <= min(x1, x2):
                    inside = not inside
                elif x <= max(x1, x2):
                    x_inter = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    if x <= x_inter:
                        inside = not inside
            x1, y1 = x2, y2
        return inside
