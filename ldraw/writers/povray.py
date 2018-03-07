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


class POVRayWriter:
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
        self.bbox_cache = {}

    def write(self, model):
        self.warnings = {}
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
        self.pov_file.write(
            "#declare scene = union {\n"
        )
        for obj in model.objects:
            if isinstance(obj, Piece):
                if obj.part in objects:
                    self.pov_file.write("object {\n" + self._object_name(obj.part) + "\n")
                    self._write_colour(obj.colour, 2)
                    m = obj.matrix.transpose()
                    format_string = """matrix <%1.3f, %1.3f, %1.3f,
%1.3f, %1.3f, %1.3f,
%1.3f, %1.3f, %1.3f,
%1.3f, %1.3f, %1.3f>"""
                    self.pov_file.write(
                        format_string % (m.flatten() + (obj.position.x, obj.position.y, obj.position.z)))
                    self.pov_file.write("}\n\n")
                elif obj.part == "LIGHT":
                    self.pov_file.write(
                        "light_source {\n"
                        "  <%1.3f, %1.3f, %1.3f>, %s\n"
                        "}\n\n" % (obj.position.x, obj.position.y, obj.position.z,
                                   self._colour_string(obj.colour))
                    )
                    self.lights.append(obj)
            elif isinstance(obj, Triangle):
                if abs((obj.p3 - obj.p1).cross(obj.p2 - obj.p1)) != 0:
                    self._write_triangle(obj.p1, obj.p2, obj.p3, obj.colour, indent=2)
            elif isinstance(obj, Quadrilateral):
                if abs((obj.p3 - obj.p1).cross(obj.p2 - obj.p1)) != 0:
                    self._write_triangle(obj.p1, obj.p2, obj.p3, obj.colour, indent=2)
                if abs((obj.p3 - obj.p1).cross(obj.p4 - obj.p1)) != 0:
                    self._write_triangle(obj.p3, obj.p4, obj.p1, obj.colour, indent=2)
        self.pov_file.write("}\n")
        self.pov_file.write(
            "object {\n"
            "  scene\n"
            "  matrix <1.0, 0.0, 0.0,\n"
            "          0.0, -1.0, 0.0,\n"
            "          0.0, 0.0, 1.0,\n"
            "          0.0, 0.0, 0.0>\n"
            "}\n"
        )

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
        if alpha:
            return "rgbt <%1.1f, %1.1f, %1.1f, %1.1f>" % (red, green, blue, alpha)
        else:
            return "rgb <%1.1f, %1.1f, %1.1f>" % (red, green, blue)

    def _finish_string(self, colour):
        attributes = self.parts.colour_attributes.get(colour.code, [])
        if attributes:
            attributes = POVRayWriter.ColourAttributes.get(attributes[0], [])
            return "\n    ".join(attributes)
        else:
            return ""

    def _write_triangle(self, v1, v2, v3, colour, indent=0):
        self.minimum = Vector(min(self.minimum.x, v1.x, v2.x, v3.x),
                              min(self.minimum.y, -v1.y, -v2.y, -v3.y),
                              min(self.minimum.z, v1.z, v2.z, v3.z))
        self.maximum = Vector(max(self.maximum.x, v1.x, v2.x, v3.x),
                              max(self.maximum.y, -v1.y, -v2.y, -v3.y),
                              max(self.maximum.z, v1.z, v2.z, v3.z))
        lines = ["triangle",
                 "{",
                 "  <%1.3f, %1.3f, %1.3f>, "
                 "<%1.3f, %1.3f, %1.3f>, "
                 "<%1.3f, %1.3f, %1.3f>\n" % (
                     v1.x, v1.y, v1.z,
                     v2.x, v2.y, v2.z,
                     v3.x, v3.y, v3.z)]
        self.pov_file.write("\n".join(map(lambda x: indent * " " + x, lines)))
        self._write_colour(colour, indent + 2)
        self.pov_file.write(" " * indent + "}\n\n")

    def _write_object_definition(self, part, objects):
        definition = objects[part]
        # Examine the constituent objects, keeping only those that refer to
        # known pieces and that are described using non-singular matrices.
        allowed = []
        for obj in definition:
            if isinstance(obj, Piece):
                if obj.part not in objects:
                    self.warnings[("Discarding reference to %s", obj.part)] = None
                    continue
                # POV-Ray does not like matrices with zero diagonal elements.
                elements = []
                if obj.matrix.rows[0][0] == 0.0:
                    obj.matrix.rows[0][0] = 0.001
                    elements.append("x")
                if obj.matrix.rows[1][1] == 0.0:
                    obj.matrix.rows[1][1] = 0.001
                    elements.append("y")
                if obj.matrix.rows[2][2] == 0.0:
                    obj.matrix.rows[2][2] = 0.001
                    elements.append("z")
                if elements:
                    self.warnings[("Correcting diagonal matrix elements for %s.", obj.part)] = None
                if obj.matrix.det() == 0.0:
                    self.warnings[("Discarding %s with singular matrix.", obj.part)] = None
                    continue
            allowed.append(obj)
        if not allowed:
            return False
        self.pov_file.write("// Part %s\n\n" % part)
        if len(definition) > 1:
            self.pov_file.write("#declare " + self._object_name(part) + " = union {\n")
        else:
            self.pov_file.write("#declare " + self._object_name(part) + " = object {\n")
        for obj in allowed:
            if isinstance(obj, Piece):
                # Refer to the object for the other piece.
                self.pov_file.write(
                    "  object {\n"
                    "    " + self._object_name(obj.part) + "\n"
                )
                # Apply a transformation for this particular piece.
                m = obj.matrix.transpose()
                format_string = """matrix <%1.3f, %1.3f, %1.3f,
%1.3f, %1.3f, %1.3f,
%1.3f, %1.3f, %1.3f,
%1.3f, %1.3f, %1.3f>"""
                self.pov_file.write(format_string % (m.flatten() + (obj.position.x, obj.position.y, obj.position.z)))
                self._write_colour(obj.colour, 2)
                self.pov_file.write("  }\n")
            elif isinstance(obj, Triangle):
                if abs((obj.p3 - obj.p1).cross(obj.p2 - obj.p1)) != 0:
                    self._write_triangle(obj.p1, obj.p2, obj.p3, obj.colour, indent=2)
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
                ordered_objects += self._create_piece_objects(obj, objects)
                # Record the object as part of the piece's definition.
                definition.append(obj)
            elif isinstance(obj, Triangle):
                # Record the object as part of the piece's definition.
                definition.append(obj)
            elif isinstance(obj, Quadrilateral):
                # Split the quadrilateral into two triangles.
                triangle1 = Triangle(obj.colour, obj.p1, obj.p2, obj.p3)
                triangle2 = Triangle(obj.colour, obj.p3, obj.p4, obj.p1)
                definition.append(triangle1)
                definition.append(triangle2)
        if definition:
            objects[this_obj.part] = definition
            ordered_objects.append(this_obj.part)
        return ordered_objects

    def _object_name(self, part):
        # Replace forbidden characters to produce a valid object name.
        return "part" + part.replace("-", "_").replace("\\", "_").replace("#", "_")
