import sys

from ldraw.geometry import Identity, Vector
from ldraw.library.colours import White, Main_Colour
from ldraw.lines import Triangle, Quadrilateral, Line
from ldraw.pieces import Piece


def _current_colour(colour, current_colour):
    return current_colour if colour == Main_Colour else colour.code


class Writer(object):
    def _opacity_from_colour(self, colour):
        return self.parts.alpha_values.get(colour, 255) / 255.0

    def _polygons_from_objects(self,
                               model,
                               top_level_piece=None,
                               current_colour=White.code,
                               current_matrix=Identity(),
                               current_position=Vector(0, 0, 0)):
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
                args = (obj, top_level_piece or obj, current_matrix, current_colour, current_position)
                poly = poly_handlers[type(obj)](*args)
            except KeyError:
                continue
            if poly:
                polygons.extend(poly)
            else:
                continue

        return polygons

    def _line_get_poly(self, obj, top_level_piece, current_matrix, current_colour, current_position):
        pass

    def _subpart_get_poly(self, obj, top_level_piece, current_matrix, current_colour, current_position):
        colour = _current_colour(obj.colour, current_colour)
        part = self.parts.part(code=obj.part)
        if part:
            matrix = obj.matrix
            return self._polygons_from_objects(part, top_level_piece, colour,
                                               current_matrix * matrix,
                                               current_position + current_matrix * obj.position)
        sys.stderr.write("Part not found: %s\n" % obj.part)
        return False

    def _triangle_get_poly(self,
                           obj,
                           top_level_piece,
                           current_matrix,
                           current_colour,
                           current_position):
        camera_position = self.camera_position

        points = [current_matrix * p + current_position - camera_position for p in obj.points]
        if abs((points[2] - points[0]).cross(points[1] - points[0])) == 0:
            return False

        return self._common_get_poly(obj, top_level_piece, current_colour, points)

    def _common_get_poly(self, obj, top_level_piece, current_colour, points):
        x_axis, y_axis, z_axis = self.axes
        projections = [Vector(p.dot(x_axis), p.dot(y_axis), p.dot(z_axis)) for p in points]
        if any(p.z >= 0 for p in projections):
            return False
        colour = _current_colour(obj.colour, current_colour)

        return self._get_polygon(top_level_piece, colour, projections)

    def _quadrilateral_get_poly(self,
                                obj,
                                top_level_piece,
                                current_matrix,
                                current_colour,
                                current_position):
        camera_position = self.camera_position

        points = [current_matrix * p + current_position - camera_position for p in obj.points]

        if abs((points[2] - points[0]).cross(points[1] - points[0])) == 0:
            return False
        if abs((points[2] - points[0]).cross(points[3] - points[0])) == 0:
            return False

        return self._common_get_poly(obj, top_level_piece, current_colour, points)

