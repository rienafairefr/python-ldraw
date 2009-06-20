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

from ldraw.geometry import Identity, Vector
from ldraw.parts import Parts, Quadrilateral, Triangle
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
    
    def write(self, model, current_colour = 15, current_matrix = Identity(),
              current_position = Vector(0, 0, 0), level = 0):
    
        for obj in model.objects:
        
            if isinstance(obj, Piece):
            
                colour = self._current_colour(obj.colour, current_colour)
                
                part = self.parts.part(code = obj.part)
                if part:
                    self.pov_file.write("// Part %s\n\n" % obj.part)
                    
                    matrix = obj.matrix
                    
                    if level == 0:
                    
                        bbox = self._bounding_box(part)
                        if bbox:
                            xp, yp, zp = bbox
                            width = (xp[1] - xp[0]) or 1.0
                            height = (yp[1] - yp[0]) or 1.0
                            depth = (zp[1] - zp[0]) or 1.0
                            matrix = matrix.scale(
                                (width - 0.5)/width,
                                (height - 0.5)/height,
                                (depth - 0.5)/depth
                                )
                    
                    self.write(part, colour, current_matrix * matrix,
                               current_position + current_matrix * obj.position,
                               level + 1)
                else:
                    sys.stderr.write("Part not found: %s\n" % obj.part)
                
                if obj.part == "LIGHT":
                
                    position = current_matrix * obj.position + current_position
                    self._write_light_source(position, colour)
                    self.lights.append(obj)
            
            elif isinstance(obj, Triangle):
            
                colour = self._current_colour(obj.colour, current_colour)
                p1 = current_matrix * obj.p1 + current_position
                p2 = current_matrix * obj.p2 + current_position
                p3 = current_matrix * obj.p3 + current_position
                if abs((p3 - p1).cross(p2 - p1)) != 0:
                    self._write_triangle(p1, p2, p3, colour)
            
            elif isinstance(obj, Quadrilateral):
            
                colour = self._current_colour(obj.colour, current_colour)
                p1 = current_matrix * obj.p1 + current_position
                p2 = current_matrix * obj.p2 + current_position
                p3 = current_matrix * obj.p3 + current_position
                p4 = current_matrix * obj.p4 + current_position
                if abs((p3 - p1).cross(p2 - p1)) != 0:
                    self._write_triangle(p1, p2, p3, colour)
                if abs((p3 - p1).cross(p4 - p1)) != 0:
                    self._write_triangle(p3, p4, p1, colour)
    
    def _current_colour(self, colour, current_colour):
    
        if colour.value == 16:
            return current_colour
        else:
            return colour.value
    
    def _rgb_from_colour(self, colour):
    
        colour = self.parts.colours.get(colour, "#FFFFFF")
        
        red = int(colour[1:3], 16) / 255.0
        green = int(colour[3:5], 16) / 255.0
        blue = int(colour[5:7], 16) / 255.0
        
        return red, green, blue
    
    def _alpha_from_colour(self, colour):
    
        return self.parts.alpha_values.get(colour, 0) / 255.0
    
    def _colour_string(self, colour):
    
        red, green, blue = self._rgb_from_colour(colour)
        alpha = self._alpha_from_colour(colour)
        if alpha:
            return "rgbt <%1.1f, %1.1f, %1.1f, %1.1f>" % (red, green, blue, alpha)
        else:
            return "rgb <%1.1f, %1.1f, %1.1f>" % (red, green, blue)
    
    def _finish_string(self, colour):
    
        attributes = self.parts.colour_attributes.get(colour, [])
        if attributes:
            attributes = POVRayWriter.ColourAttributes.get(attributes[0], [])
            return "\n    ".join(attributes)
        else:
            return ""
    
    def _write_triangle(self, v1, v2, v3, colour):
    
        self.minimum = Vector(min(self.minimum.x, v1.x, v2.x, v3.x),
                              min(self.minimum.y, -v1.y, -v2.y, -v3.y),
                              min(self.minimum.z, v1.z, v2.z, v3.z))
        self.maximum = Vector(max(self.maximum.x, v1.x, v2.x, v3.x),
                              max(self.maximum.y, -v1.y, -v2.y, -v3.y),
                              max(self.maximum.z, v1.z, v2.z, v3.z))
        
        self.pov_file.write(
            "triangle\n"
            "{\n"
            "  <%1.3f, %1.3f, %1.3f>, <%1.3f, %1.3f, %1.3f>, <%1.3f, %1.3f, %1.3f>\n"
            "  pigment\n"
            "  {\n"
            "    color %s\n"
            "  }\n"
            "  finish\n"
            "  {\n"
            "    %s\n"
            "  }\n"
            "}\n\n" % (v1.x, -v1.y, v1.z,
                       v2.x, -v2.y, v2.z,
                       v3.x, -v3.y, v3.z,
                       self._colour_string(colour),
                       self._finish_string(colour))
            )
    
    def _write_light_source(self, position, colour):
    
        self.pov_file.write(
            "light_source {\n"
            "  <%1.3f, %1.3f, %1.3f>, %s\n"
            "}\n\n" % (position.x, -position.y, position.z,
                       self._colour_string(colour))
            )
    
    def _bounding_box(self, part):
    
        if self.bbox_cache.has_key(part):
            return self.bbox_cache[part]
        
        x = []
        y = []
        z = []
        
        for obj in part.objects:
        
            if isinstance(obj, Triangle):
                x.append(min(obj.p1.x, obj.p2.x, obj.p3.x))
                x.append(max(obj.p1.x, obj.p2.x, obj.p3.x))
                y.append(min(obj.p1.y, obj.p2.y, obj.p3.y))
                y.append(max(obj.p1.y, obj.p2.y, obj.p3.y))
                z.append(min(obj.p1.z, obj.p2.z, obj.p3.z))
                z.append(max(obj.p1.z, obj.p2.z, obj.p3.z))
            
            elif isinstance(obj, Quadrilateral):
                x.append(min(obj.p1.x, obj.p2.x, obj.p3.x, obj.p4.x))
                x.append(max(obj.p1.x, obj.p2.x, obj.p3.x, obj.p4.x))
                y.append(min(obj.p1.y, obj.p2.y, obj.p3.y, obj.p4.y))
                y.append(max(obj.p1.y, obj.p2.y, obj.p3.y, obj.p4.y))
                z.append(min(obj.p1.z, obj.p2.z, obj.p3.z, obj.p4.z))
                z.append(max(obj.p1.z, obj.p2.z, obj.p3.z, obj.p4.z))
        
        if x:
            return (min(x), max(x)), (min(y), max(y)), (min(z), max(z))
        else:
            return None
