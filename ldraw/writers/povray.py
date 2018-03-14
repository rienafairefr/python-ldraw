"""
povray.py - A POV-Ray writer for the ldraw Python package.

Copyright (C) 2009 David Boddie <david@boddie.org.uk>

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

from ldraw.library.colours import Main_Colour as Current
from ldraw.geometry import Vector
from ldraw.lines import Quadrilateral, Triangle
from ldraw.pieces import Piece

POV_OBJECT2 = """object {
%s
"""

POV_OBJECT = """  object {
    %s
"""

POV_DECLARE = """#declare %%s = %s {
"""

POV_DECLARE_OBJECT = POV_DECLARE % 'object'
POV_DECLARE_UNION = POV_DECLARE % 'union'

POV_PREAMBLE = POV_DECLARE_UNION % 'scene'

POV_LIGHTSOURCE = """light_source {
  <%1.3f, %1.3f, %1.3f>, %s
}

"""

POV_POSTAMBLE = """}
object {
  scene
  matrix <1.0, 0.0, 0.0,
          0.0, -1.0, 0.0,
          0.0, 0.0, 1.0,
          0.0, 0.0, 0.0>
}
"""

POV_FORMAT_STRING_TRIANGLE = "  <%1.3f, %1.3f, %1.3f>, " \
                             "<%1.3f, %1.3f, %1.3f>, " \
                             "<%1.3f, %1.3f, %1.3f>\n"

POV_FORMAT_STRING = """matrix <%1.3f, %1.3f, %1.3f,
%1.3f, %1.3f, %1.3f,
%1.3f, %1.3f, %1.3f,
%1.3f, %1.3f, %1.3f>"""


def _rgb_line(alpha, red, green, blue):
    rgb = (red, green, blue)
    if alpha:
        return "rgbt <%1.1f, %1.1f, %1.1f, %1.1f>" % (rgb + (alpha,))
    return "rgb <%1.1f, %1.1f, %1.1f>" % rgb


def _object_name(part):
    # Replace forbidden characters to produce a valid object name.
    return "part" + part.replace("-", "_").replace("\\", "_").replace("#", "_")


class POVRayWriter(object):
    # pylint: disable=too-few-public-methods
    """
        Writes a POV file from a model
    """
    ColourAttributes = {
        "CHROME": ("metallic 1.0", "specular 0.8", "brilliance 3", "diffuse 0.6"),
        "PEARLESCENT": ("diffuse 0.7", "specular 0.8"),
        "RUBBER": ("diffuse 1.0",),
        "MATTE_METALLIC": ("metallic 0.5", "roughness 0.2"),
        "METAL": ("metallic 0.8", "specular 0.8", "reflection 0.5")
    }

    def __init__(self, parts, pov_file):
        self.parts = parts
        self.pov_file = pov_file
        self.lights = []
        self.minimum = Vector(0, 0, 0)
        self.maximum = Vector(0, 0, 0)
        self.warnings = []

    def write(self, model):
        """
        Writes the provided model to self.pov_file
        :param model: a Part from a .ldr file
        :return:
        """

        # Define objects for the pieces first.
        objects = {}
        ordered_objects = []
        for obj in model.objects:
            if isinstance(obj, Piece):
                ordered_objects += self._create_piece_objects(obj, objects)
        # Write the objects, discarding any that are invalid in any way.
        for part in ordered_objects:
            if not self._write_object_definition(part, objects):
                del objects[part]
        # Write the pieces using the objects.
        self.pov_file.write(POV_PREAMBLE)
        for obj in model.objects:
            if isinstance(obj, Piece):
                self._write_piece(obj, objects)
            elif isinstance(obj, Triangle):
                self._write_triangle_1(obj)
            elif isinstance(obj, Quadrilateral):
                self._write_triangle_1(obj)
                self._write_triangle_2(obj)
        self.pov_file.write(POV_POSTAMBLE)

    def _write_triangle_2(self, obj):
        if abs((obj.point3 - obj.point1).cross(obj.point4 - obj.point1)) != 0:
            self._write_triangle(obj.colour, obj.point3, obj.point4, obj.point1)

    def _write_triangle_1(self, obj):
        if abs((obj.point3 - obj.point1).cross(obj.point2 - obj.point1)) != 0:
            self._write_triangle(obj.colour, obj.point1, obj.point2, obj.point3)

    def _write_piece(self, obj, objects):
        if obj.part in objects:
            obj_position = (obj.position.x, obj.position.y, obj.position.z)
            self.pov_file.write(POV_OBJECT2 % _object_name(obj.part))
            self._write_colour(obj.colour, 2)
            transposed_matrix = obj.matrix.transpose().flatten()
            pov_line = transposed_matrix + obj_position
            self.pov_file.write(POV_FORMAT_STRING % pov_line)
            self.pov_file.write("}\n\n")
        elif obj.part == "LIGHT":
            obj_position = (obj.position.x, obj.position.y, obj.position.z)
            pov_line = obj_position + (self._colour_string(obj.colour),)
            self.pov_file.write(POV_LIGHTSOURCE % pov_line)
            self.lights.append(obj)

    def _write_piece_2(self, obj):
        # Refer to the object for the other piece.
        self.pov_file.write(POV_OBJECT % _object_name(obj.part))
        # Apply a transformation for this particular piece.
        transposed_matrix = obj.matrix.transpose().flatten()
        obj_position = (obj.position.x, obj.position.y, obj.position.z)
        pov_line = transposed_matrix + obj_position
        self.pov_file.write(POV_FORMAT_STRING % pov_line)
        self._write_colour(obj.colour, 2)
        self.pov_file.write("  }\n")

    def _rgb_from_colour(self, colour):
        colour = self.parts.colours.get(colour.code, "#FFFFFF")
        red = int(colour[1:3], 16) / 255.0
        green = int(colour[3:5], 16) / 255.0
        blue = int(colour[5:7], 16) / 255.0
        return red, green, blue

    def _alpha_from_colour(self, colour):
        return self.parts.alpha_values.get(colour.code, 0) / 255.0

    def _colour_string(self, colour):
        red, green, blue = self._rgb_from_colour(colour)
        alpha = self._alpha_from_colour(colour)
        return _rgb_line(alpha, red, green, blue)

    def _finish_string(self, colour):
        attributes = self.parts.colour_attributes.get(colour.code, [])
        if attributes:
            attributes = POVRayWriter.ColourAttributes.get(attributes[0], [])
            return "\n    ".join(attributes)
        return ""

    def _write_triangle(self, colour, *vectors):
        indent = 2
        assert len(vectors) == 3
        self.minimum = Vector(min(self.minimum.x, vectors[0].x, vectors[1].x, vectors[2].x),
                              min(self.minimum.y, -vectors[0].y, -vectors[1].y, -vectors[2].y),
                              min(self.minimum.z, vectors[0].z, vectors[1].z, vectors[2].z))
        self.maximum = Vector(max(self.maximum.x, vectors[0].x, vectors[1].x, vectors[2].x),
                              max(self.maximum.y, -vectors[0].y, -vectors[1].y, -vectors[2].y),
                              max(self.maximum.z, vectors[0].z, vectors[1].z, vectors[2].z))
        triangle = (
            vectors[0].x, vectors[0].y, vectors[0].z,
            vectors[1].x, vectors[1].y, vectors[1].z,
            vectors[2].x, vectors[2].y, vectors[2].z
        )
        lines = ["triangle", "{", POV_FORMAT_STRING_TRIANGLE % triangle]
        self.pov_file.write("\n".join(indent * " " + x for x in lines))
        self._write_colour(colour, indent + 2)
        self.pov_file.write(" " * indent + "}\n\n")

    def _write_object_definition(self, part, objects):
        definition = objects[part]
        # Examine the constituent objects, keeping only those that refer to
        # known pieces and that are described using non-singular matrices.
        allowed = []
        for obj in definition:
            if not isinstance(obj, Piece):
                allowed.append(obj)
                continue
            if obj.part not in objects:
                self.warnings.append(("Discarding reference to %s", obj.part))
                continue
            if obj.matrix.fix_diagonal():
                self.warnings.append(("Correcting diagonal matrix elements for %s.", obj.part))
            if obj.matrix.det() == 0.0:
                self.warnings.append(("Discarding %s with singular matrix.", obj.part))
                continue
            allowed.append(obj)
        if not allowed:
            return False
        self.pov_file.write("// Part %s\n\n" % part)
        if len(definition) > 1:
            self.pov_file.write(POV_DECLARE_UNION % _object_name(part))
        else:
            self.pov_file.write(POV_DECLARE_OBJECT % _object_name(part))
        for obj in allowed:
            if isinstance(obj, Piece):
                self._write_piece_2(obj)
            elif isinstance(obj, Triangle):
                if abs((obj.point3 - obj.point1).cross(obj.point2 - obj.point1)) != 0:
                    self._write_triangle(obj.colour, obj.point1, obj.point2, obj.point3)
        self.pov_file.write("}\n\n")
        return True

    def _write_colour(self, colour, indent):
        if colour == Current:
            return
        self.pov_file.write(indent * " ")
        self.pov_file.write("pigment { color %s }\n" % self._colour_string(colour))
        finish = self._finish_string(colour)
        if finish.strip():
            self.pov_file.write(indent * " ")
            self.pov_file.write("finish { %s }\n" % finish)

    def _create_piece_objects(self, this_obj, objects):
        if this_obj.part in objects:
            return []
        part = self.parts.part(code=this_obj.part)
        if not part:
            sys.stderr.write("Part not found: %s\n" % this_obj.part)
            return []
        definition = []
        ordered_objects = []
        for obj in part.objects:
            if isinstance(obj, Piece):
                # Define this piece, too.
                ordered_objects = ordered_objects + self._create_piece_objects(obj, objects)
                # Record the object as part of the piece's definition.
                definition.append(obj)
            elif isinstance(obj, Triangle):
                # Record the object as part of the piece's definition.
                definition.append(obj)
            elif isinstance(obj, Quadrilateral):
                # Split the quadrilateral into two triangles.
                triangle1 = Triangle(obj.colour, obj.point1, obj.point2, obj.point3)
                triangle2 = Triangle(obj.colour, obj.point3, obj.point4, obj.point1)
                definition.append(triangle1)
                definition.append(triangle2)
        if definition:
            objects[this_obj.part] = definition
            ordered_objects.append(this_obj.part)
        return ordered_objects
