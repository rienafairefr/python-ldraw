#!/usr/bin/env python

import sys
import cmdsyntax
from ldraw.geometry import Identity, Vector
from ldraw.parts import Part, Parts, PartError, Quadrilateral, Triangle
from ldraw.pieces import Piece


class Writer:

    def __init__(self, parts, pov_file):
    
        self.parts = parts
        self.pov_file = pov_file
        self.lights = []
    
    def write(self, model, current_colour = 15, current_matrix = Identity(),
              current_position = Vector(0, 0, 0)):
    
        for obj in model.objects:
        
            if isinstance(obj, Piece):
            
                colour = self._current_colour(obj.colour, current_colour)
                
                part = self.parts.part(code = obj.part)
                if part:
                    self.pov_file.write("// Part %s\n\n" % obj.part)
                    self.write(part, colour, current_matrix * obj.matrix,
                               current_position + current_matrix * obj.position)
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
    
    def _write_triangle(self, v1, v2, v3, colour):
    
        red, green, blue = self._rgb_from_colour(colour)
        
        self.pov_file.write(
            "triangle\n"
            "{\n"
            "  <%1.3f, %1.3f, %1.3f>, <%1.3f, %1.3f, %1.3f>, <%1.3f, %1.3f, %1.3f>\n"
            "  pigment\n"
            "  {\n"
            "    color rgb <%1.1f, %1.1f, %1.1f>\n"
            "  }\n"
            "}\n\n" % (v1.x, -v1.y, v1.z,
                       v2.x, -v2.y, v2.z,
                       v3.x, -v3.y, v3.z,
                       red, green, blue)
            )
    
    def _write_light_source(self, position, colour):
    
        red, green, blue = self._rgb_from_colour(colour)
        
        self.pov_file.write(
            "light_source {\n"
            "  <%1.3f, %1.3f, %1.3f>, rgb <%1.1f, %1.1f, %1.1f>\n"
            "}\n\n" % (position.x, -position.y, position.z,
                       red, green, blue)
            )
    
    def _order_points(self, points):
    
        edges = []
        for i in range(1, len(points)):
            edge = points[i] - points[0]
            edges.append((edge/abs(edge), points[i]))
    
        normals = []
        reference_edge, reference_point = edges[0]
        for i in range(1, len(edges)):
            edge, point = edges[i]
            normal = edge.cross(reference_edge)
            normals.append((normal, point))
        
        new_points = [(0, reference_point)]
        reference_normal = normals[0][0]
        reference_normal = reference_normal/abs(reference_normal)
        for normal, point in normals:
            new_points.append((normal.dot(reference_normal), point))
        
        new_points.sort()
        return [points[0]] + map(lambda (value, point): point, new_points)


if __name__ == "__main__":

    syntax = "<LDraw parts file> <LDraw file> <POV-Ray file> <camera position> [--sky <sky color>]"
    syntax_obj = cmdsyntax.Syntax(syntax)
    matches = syntax_obj.get_args(sys.argv[1:])
    
    if len(matches) != 1:
        sys.stderr.write("Usage: %s %s\n" % (sys.argv[0], syntax))
        sys.exit(1)
    
    match = matches[0]
    parts_path = match["LDraw parts file"]
    ldraw_path = match["LDraw file"]
    pov_path = match["POV-Ray file"]
    camera_position = match["camera position"]
    
    parts = Parts(parts_path)
    
    try:
        model = Part(ldraw_path)
    except PartError:
        sys.stderr.write("Failed to read LDraw file: %s\n" % ldraw_path)
        sys.exit(1)
    
    pov_file = open(pov_path, "w")
    pov_file.write('#include "colors.inc"\n\n')
    writer = Writer(parts, pov_file)
    writer.write(model)
    
    if not writer.lights:
    
        pov_file.write(
            "light_source {\n"
            "  <0.0, 50.0, -100.0>, rgb <1.0, 1.0, 1.0>\n"
            "}\n\n"
            "light_source {\n"
            "  <50.0, 50.0, -100.0>, rgb <1.0, 1.0, 1.0>\n"
            "}\n\n"
            "light_source {\n"
            "  <-50.0, 50.0, -100.0>, rgb <1.0, 1.0, 1.0>\n"
            "}\n\n"
            )
    
    pov_file.write(
        "camera {\n"
        "  location <%s>\n"
        "  look_at <0.0, 0.0, 0.0>\n"
        "}\n" % ", ".join(camera_position.split(","))
        )
    
    if match.has_key("sky"):
    
        pov_file.write(
            "sky_sphere {\n"
            "  pigment\n"
            "  {\n"
            "    rgb <%s>\n"
            "  }\n"
            "}\n" % match["sky color"]
            )
    
    pov_file.close()
