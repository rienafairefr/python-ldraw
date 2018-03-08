"""
png.py - A PNG writer for the ldraw Python package.

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

import numpy
from PyQt4.QtGui import QColor, QImage, \
    qRed, qGreen, qBlue, qRgb

from ldraw.geometry import Identity, Vector
from ldraw.library.colours import Main_Colour, White
from ldraw.lines import Quadrilateral, Triangle
from ldraw.pieces import Piece


class Edge(object):
    def __init__(self, point1, point2):
        """
        :param point1:
        :type point1: Vector
        :param point2:
        :type point2: Vector
        """

        self.point1 = point1
        self.point2 = point2

        self.x1 = point1.x
        self.y1 = point1.y
        self.y2 = point2.y
        self.z1 = point1.z

        self.dx_dy = (point2.x - point1.x) / (point2.y - point1.y)
        self.dz_dy = (point2.z - point1.z) / (point2.y - point1.y)

    @property
    def t(self):
        return (self.y1, self.y2,
                self.x1, self.dx_dy,
                self.z1, self.dz_dy)


class Polygon(object):
    """
    Describes a polygon for PNG rendering
    """

    def __init__(self, points, rgb, alpha):
        self.points = points
        colour = QColor(rgb)
        self.red = colour.red()
        self.green = colour.green()
        self.blue = colour.blue()
        colour.setAlphaF(alpha)
        self.alpha = alpha
        self.rgba = colour.rgb()
        self.projected = []

    def project(self, distance):
        # px/c = x/(c + z)
        # px = c * x / (c + z)
        for point in self.points:
            self.projected.append(
                ((distance * point.x) / (distance + -point.z),
                 (distance * point.y) / (distance + -point.z))
            )

    def render(self, image, depth, viewport_scale, stroke_colour):
        # Sort the edges of the polygon by their minimum projected y
        # coordinates, discarding horizontal edges.
        width = image.width()
        height = image.height()
        z_max = 1 << 16
        edges = []
        len_points = len(self.points)
        for i in range(len_points):
            pxa, pya = self.projected[i]
            pxa = width / 2 + (pxa * viewport_scale)
            pya = height / 2 - (pya * viewport_scale)
            za = -self.points[i].z
            j = (i + 1) % len_points
            pxb, pyb = self.projected[j]
            pxb = width / 2 + (pxb * viewport_scale)
            pyb = height / 2 - (pyb * viewport_scale)
            zb = -self.points[j].z
            # Append the starting and finishing y coordinates, the starting
            # x coordinate, the dx/dy gradient of the edge, the starting
            # z coordinate and the dz/dy gradient of the edge.
            if int(pya) < int(pyb):
                edges.append((pya, pyb, pxa, (pxb - pxa) / (pyb - pya),
                              za, (zb - za) / (pyb - pya)))
            elif int(pya) > int(pyb):
                edges.append((pyb, pya, pxb, (pxa - pxb) / (pya - pyb),
                              zb, (za - zb) / (pya - pyb)))
        if not edges:
            return
        edges.sort()
        end_py = edges[-1][1]
        if end_py < 0:
            return
        py1, end_py1, px1, dx1, z1, dz1 = edges.pop(0)
        if py1 >= height:
            return
        py2, end_py2, px2, dx2, z2, dz2 = edges.pop(0)
        py = int(py1)
        if py < py1 or py < py2:
            py += 1
        while py <= end_py and py < height:
            # Retrieve new edges as required.
            if py >= end_py1:
                if not edges:
                    break
                py1, end_py1, px1, dx1, z1, dz1 = edges.pop(0)
            if py >= end_py2:
                if not edges:
                    break
                py2, end_py2, px2, dx2, z2, dz2 = edges.pop(0)
            if py < 0:
                py += 1
                continue
            # Calculate the starting and finishing x coordinates of the span
            # at the current y coordinate.
            sx1 = px1 + dx1 * (py - py1)
            sx2 = px2 + dx2 * (py - py2)
            # Calculate the starting and finishing z coordinates of the span
            # at the current y coordinate.
            sz1 = z1 + dz1 * (py - py1)
            sz2 = z2 + dz2 * (py - py2)
            # Do not render the span if it lies outside the image or has
            # values that cannot be stored in the depth buffer.
            # Truncate the span if it lies partially within the image.
            if sx1 > sx2:
                sx1, sx2 = sx2, sx1
                sz1, sz2 = sz2, sz1
            # Only calculate a depth gradient for the span if it is more than
            # one pixel wide.
            if sx1 != sx2:
                dz = (sz2 - sz1) / (sx2 - sx1)
            else:
                dz = 0.0
            if sz1 <= 0 and sz2 <= 0:
                py += 1
                continue
            elif sz1 >= z_max and sz2 >= z_max:
                py += 1
                continue
            sx, end_sx = int(sx1), int(sx2)
            if sx < sx1:
                sx += 1
            if sx >= width:
                py += 1
                continue
            elif end_sx < 0:
                py += 1
                continue
            if sx < 0:
                sx = 0
            if end_sx >= width:
                end_sx = width - 1
            # Draw the span.
            while sx <= end_sx:
                sz = sz1 + dz * (sx - sx1)
                if 0 < sz <= depth[int(sx)][int(py)]:
                    if self.alpha < 1.0:
                        pixel = image.pixel(sx, py)
                        dr = qRed(pixel)
                        dg = qGreen(pixel)
                        db = qBlue(pixel)
                        r = (1 - self.alpha) * dr + self.alpha * self.red
                        g = (1 - self.alpha) * dg + self.alpha * self.green
                        b = (1 - self.alpha) * db + self.alpha * self.blue
                        image.setPixel(sx, py, qRgb(r, g, b))
                    else:
                        depth[int(sx)][int(py)] = sz
                        image.setPixel(sx, py, self.rgba)
                sx += 1
            if stroke_colour:
                if 0 <= sx1 < width and 0 < sz1 <= depth[int(sx1)][int(py)]:
                    image.setPixel(sx1, py, stroke_colour)
                if 0 <= sx2 < width and 0 < sz2 <= depth[int(sx2)][int(py)]:
                    image.setPixel(sx2, py, stroke_colour)
            py += 1

class PNGArgs(object):
    def __init__(self, distance, image_size, stroke_colour=None, background_colour=None):
        """
        :param distance: distance of the camera
        :param image_size: size of the image as a string (e.g. '800x800')
        :param stroke_colour: colour of the edges
        :param background_colour: colour of the background
        """
        self.distance = distance
        self.image_size = image_size
        self.stroke_colour = stroke_colour
        self.background_colour = background_colour


def _current_colour(colour, current_colour):
    return current_colour if colour == Main_Colour else colour.code


class PNGWriter(object):
    """
    Renders a LDR model into a PNG
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, camera_position, axes, parts):
        self.parts = parts
        self.lights = []
        self.minimum = Vector(0, 0, 0)
        self.maximum = Vector(0, 0, 0)
        self.bbox_cache = {}
        self.camera_position = camera_position
        self.axes = axes

    def write(self, model, png_path, png_args):
        """
        Writes the model's polygons to the provided PNG file

        :param model: LDR model
        :type model: Part
        :param png_path: where to output the PNG
        :param png_args: Arguments for the rendering (distance, etc.)
        :type png_args: PNGArgs

        :return:
        """
        distance = png_args.distance
        image_size = png_args.image_size
        stroke_colour = png_args.stroke_colour
        background_colour = png_args.background_colour
        image = QImage(image_size[0], image_size[1], QImage.Format_RGB16)
        depth = numpy.empty((image_size[0], image_size[1]), "f")
        depth[:] = 1 << 32 - 1
        polygons = self._polygons_from_objects(model)
        if stroke_colour:
            stroke_colour = QColor(stroke_colour).rgb()
        if background_colour is not None:
            image.fill(QColor(background_colour).rgb())
        viewport_scale = min(float(image_size[0]), float(image_size[1]))
        # Draw opaque polygons first.
        for polygon in polygons:
            if polygon.alpha == 1.0:
                polygon.project(distance)
                polygon.render(image, depth, viewport_scale, stroke_colour)
        # Draw translucent polygons last.
        for polygon in polygons:
            if polygon.alpha < 1.0:
                polygon.project(distance)
                polygon.render(image, depth, viewport_scale, stroke_colour)
        image.save(png_path)

    def _opacity_from_colour(self, colour):
        return self.parts.alpha_values.get(colour, 255) / 255.0

    def _triangle_get_poly(self,
                           obj,
                           current_matrix,
                           current_colour,
                           current_position):
        camera_position = self.camera_position

        points = [current_matrix * p + current_position - camera_position for p in obj.points]
        if abs((points[2] - points[0]).cross(points[1] - points[0])) == 0:
            return False

        return self._common_get_poly(obj, current_colour, points)

    def _common_get_poly(self, obj, current_colour, points):
        x_axis, y_axis, z_axis = self.axes
        proj_points = [Vector(p.dot(x_axis), p.dot(y_axis), p.dot(z_axis)) for p in points]

        if any(p.z >= 0 for p in proj_points):
            return False

        colour = _current_colour(obj.colour, current_colour)
        rgb = self.parts.colours.get(colour, "#ffffff")
        alpha = self._opacity_from_colour(colour)
        return [Polygon(proj_points, rgb, alpha)]

    def _quadrilateral_get_poly(self,
                                obj,
                                current_matrix,
                                current_colour,
                                current_position):
        camera_position = self.camera_position

        points = [current_matrix * p + current_position - camera_position for p in obj.points]

        if abs((points[2] - points[0]).cross(points[1] - points[0])) == 0:
            return False
        if abs((points[2] - points[0]).cross(points[3] - points[0])) == 0:
            return False

        return self._common_get_poly(obj, current_colour, points)

    def _polygons_from_objects(self,
                               model,
                               current_colour=White.code,
                               current_matrix=Identity(),
                               current_position=Vector(0, 0, 0)):
        # Extract polygons from objects, filtering out those behind the camera.
        polygons = []

        poly_handlers = {
            Piece: self._subpart_get_poly,
            Triangle: self._triangle_get_poly,
            Quadrilateral: self._quadrilateral_get_poly,
        }

        for obj in model.objects:
            if isinstance(obj, Piece) and obj.part == "LIGHT":
                continue
            try:
                args = (obj, current_matrix, current_colour, current_position)
                poly = poly_handlers[type(obj)](*args)
            except KeyError:
                continue
            if poly:
                polygons.extend(poly)
            else:
                continue

        return polygons

    def _subpart_get_poly(self, obj, current_matrix, current_colour, current_position):
        colour = _current_colour(obj.colour, current_colour)
        part = self.parts.part(code=obj.part)
        if part:
            matrix = obj.matrix
            return self._polygons_from_objects(
                part, colour, current_matrix * matrix,
                              current_position + current_matrix * obj.position)
        sys.stderr.write("Part not found: %s\n" % obj.part)
        return False
