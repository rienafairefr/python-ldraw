"""
Common code for all the Writers
"""
import sys

from ldraw.geometry import Identity, Vector
from ldraw.library.colours import White, Main_Colour
from ldraw.lines import Triangle, Quadrilateral, Line
from ldraw.pieces import Piece


def _current_colour(colour, current_colour):
    return current_colour if colour == Main_Colour else colour.code


class Current(object):
    """ an instance of this is passed around during rendering """
    # pylint: disable=too-few-public-methods

    def __init__(self, matrix, colour, position):
        self.matrix = matrix
        self.colour = colour
        self.position = position


class Writer(object):
    # pylint: disable=too-many-arguments, too-few-public-methods
    """ Common logic for PNG, SVG, POV writers """

    def __init__(self, camera_position, system, parts):
        self.camera_position = camera_position
        self.system = system
        self.parts = parts

    def _opacity_from_colour(self, colour):
        return self.parts.alpha_values.get(colour, 255) / 255.0

    def _polygons_from_objects(self,
                               model,
                               top_level_piece=None,
                               current=Current(Identity(), White.code, Vector(0, 0, 0))):
        # Extract polygons from objects, filtering out those behind the camera.
        polygons = []

        poly_handlers = {
            Piece: self._subpart_get_poly,
            Line: self._line_get_poly,
            Triangle: self._triangle_get_poly,
            Quadrilateral: self._quadrilateral_get_poly,
        }

        for obj in model.objects:
            if isinstance(obj, Piece) and obj.part == "LIGHT":
                continue
            try:
                args = (obj,
                        top_level_piece or obj,
                        current)
                poly = poly_handlers[type(obj)](*args)
            except KeyError:
                continue
            if poly:
                polygons.extend(poly)
            else:
                continue

        return polygons

    def _line_get_poly(self,
                       obj,
                       top_level_piece,
                       current):
        pass

    def _subpart_get_poly(self,
                          obj,
                          top_level_piece,
                          current):
        colour = _current_colour(obj.colour, current.colour)
        part = self.parts.part(code=obj.part)
        if part:
            matrix = obj.matrix
            new_current = Current(current.matrix * matrix,
                                  colour,
                                  current.position + current.matrix * obj.position)
            return self._polygons_from_objects(part,
                                               top_level_piece,
                                               new_current)
        sys.stderr.write("Part not found: %s\n" % obj.part)
        return False

    def _triangle_get_poly(self,
                           obj,
                           top_level_piece,
                           current):
        camera_position = self.camera_position

        points = [current.matrix * p + current.position - camera_position for p in obj.points]
        if abs((points[2] - points[0]).cross(points[1] - points[0])) == 0:
            return False

        return self._common_get_poly(obj, top_level_piece, current.colour, points)

    def _common_get_poly(self,
                         obj,
                         top_level_piece,
                         current_colour,
                         points):
        projections = [self.system.project(p) for p in points]
        if any(p.z >= 0 for p in projections):
            return False
        colour = _current_colour(obj.colour, current_colour)

        return self._get_polygon(top_level_piece, colour, projections)

    def _quadrilateral_get_poly(self,
                                obj,
                                top_level_piece,
                                current):
        camera_position = self.camera_position

        points = [current.matrix * p + current.position - camera_position for p in obj.points]

        if abs((points[2] - points[0]).cross(points[1] - points[0])) == 0:
            return False
        if abs((points[2] - points[0]).cross(points[3] - points[0])) == 0:
            return False

        return self._common_get_poly(obj, top_level_piece, current.colour, points)

    def _get_polygon(self, top_level_piece, colour, projections):
        pass
