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

from ldraw.geometry import Identity, Vector
from ldraw.parts import Parts, Quadrilateral, Triangle, Line
from ldraw.pieces import Piece

class SVGWriter:

    ColourAttributes = {
        "CHROME": ("metallic 1.0", "specular 0.8", "brilliance 3", "diffuse 0.6"),
        "PEARLESCENT": ("diffuse 0.7", "specular 0.8"),
        "RUBBER": ("diffuse 1.0",),
        "MATTE_METALLIC": ("metallic 0.5", "roughness 0.2"),
        "METAL": ("metallic 0.8", "specular 0.8", "reflection 0.5")
        }
    
    def __init__(self, camera_position, axes, parts):
    
        self.parts = parts
        self.lights = []
        self.minimum = Vector(0, 0, 0)
        self.maximum = Vector(0, 0, 0)
        self.bbox_cache = {}
        self.camera_position = camera_position
        self.axes = axes
    
    def write(self, model, svg_file, width, height, stroke_colour = None, stroke_width = None, background_colour = None):
    
        svg_file.write('<?xml version="1.0" standalone="no"?>\n'
                            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n'
                            '  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
        
        polygons = self._polygons_from_objects(model)
        self._sort_polygons(polygons)
        polygons = self._project_polygons(width, height, polygons)
        
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
        
        current_colour = None
        
        for points, colour in polygons:
        
            rgb = self.parts.colours.get(colour, "#ffffff")
            if current_colour != rgb:
                if current_colour is not None:
                    svg_file.write('</g>\n')
                
                svg_file.write('<g>\n')
                current_colour = rgb
            
            if len(points) == 2:
            
                svg_file.write('<line stroke="%s" ' % rgb)
                svg_file.write('stroke-width="%s" ' % stroke_width)
                svg_file.write('opacity="%.6f" ' % self._opacity_from_colour(colour))
                svg_file.write('x1="%.6f" y1="%.6f" ' % (points[0][0] + width/2.0, height/2.0 - points[0][1]))
                svg_file.write('x2="%.6f" y2="%.6f" ' % (points[1][0] + width/2.0, height/2.0 - points[1][1]))
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
                    svg_file.write('%.6f,%.6f ' % (x + width/2.0, height/2.0 - y))
                
                svg_file.write('" />\n')
        
        if current_colour is not None:
            svg_file.write("</g>\n")
        
        svg_file.write("</svg>\n")
        svg_file.close()
    
    def _current_colour(self, colour, current_colour):
    
        if colour.value == 16:
            return current_colour
        else:
            return colour.value
    
    def _opacity_from_colour(self, colour):
    
        return self.parts.alpha_values.get(colour, 255) / 255.0
    
    def _polygons_from_objects(self, model, current_colour = 15, current_matrix = Identity(),
                               current_position = Vector(0, 0, 0)):
    
        # Extract polygons from objects, filtering out those behind the camera.
        
        polygons = []
        c = self.camera_position
        x, y, z = self.axes
        
        for obj in model.objects:
        
            if isinstance(obj, Piece):
            
                if obj.part == "LIGHT":
                    continue
                
                colour = self._current_colour(obj.colour, current_colour)
                part = self.parts.part(code = obj.part)
                
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
                polygons.append((min(r1.z, r2.z), (r1, r2), colour))
            
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
                polygons.append((min(r1.z, r2.z, r3.z), (r1, r2, r3), colour))
            
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
                polygons.append((min(r1.z, r2.z, r3.z, r4.z), (r1, r2, r3, r4), colour))
        
        return polygons
    
    def _sort_polygons(self, polygons):
    
        polygons.sort()
    
    def _project_polygons(self, width, height, polygons):
    
        # vx' = width + az
        # vy' = height + bz
        
        a = 0.5
        b = 0.5
        w = width/2.0
        h = height/2.0
        
        new_polygons = []
        for zmin, points, colour in polygons:
        
            new_points = []
            for point in points:
            
                new_points.append((w * (point.x/(w + a * -point.z)),
                                   h * (point.y/(h + b * -point.z))))
            
            new_polygons.append((new_points, colour))
        
        return new_polygons
