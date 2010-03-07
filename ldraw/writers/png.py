"""
png.py - An PNG writer for the ldraw Python package.

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

from PyQt4.QtCore import QPointF, Qt
from PyQt4.QtGui import QBrush, QColor, QImage, QPainter, QPen, QPolygonF

class Polygon:

    def __init__(self, zmin, points, colour):
    
        self.zmin = zmin
        self.points = points
        self.colour = colour
    
    def __lt__(self, other):
    
        return self.zmin < other.zmin
    
class PNGWriter:

    def __init__(self, camera_position, axes, parts):
    
        self.parts = parts
        self.lights = []
        self.minimum = Vector(0, 0, 0)
        self.maximum = Vector(0, 0, 0)
        self.bbox_cache = {}
        self.camera_position = camera_position
        self.axes = axes
    
    def write(self, model, png_path, viewport_size, image_size, stroke_colour = None, stroke_width = None, background_colour = None):
    
        image = QImage(image_size[0], image_size[1], QImage.Format_RGB16)
        
        polygons = self._polygons_from_objects(model)
        self._sort_polygons(polygons)
        shapes = self._project_polygons(viewport_size[0], viewport_size[1], polygons)
        
        pen = QPen()
        stroke_pen = QPen()
        if stroke_width is None:
            pen.setCosmetic(True)
            stroke_pen.setCosmetic(True)
        else:
            pen.setWidth(stroke_width)
            stroke_pen.setWidth(stroke_width)
        
        if stroke_colour:
            stroke_pen.setColor(QColor(stroke_colour))
        
        if background_colour is not None:
            image.fill(QColor(background_colour))
        
        current_colour = None
        current_alpha = None
        
        viewport_scale_x = image_size[0] / viewport_size[0]
        viewport_scale_y = image_size[1] / viewport_size[1]
        
        painter = QPainter()
        painter.begin(image)
        
        for points, colour in shapes:
        
            rgb = self.parts.colours.get(colour, "#ffffff")
            alpha = self._opacity_from_colour(colour)
            
            if current_colour != rgb or alpha != current_alpha:
                color = QColor(rgb)
                color.setAlphaF(alpha)
                pen.setColor(color)
                current_colour = rgb
                current_alpha = alpha
                painter.setBrush(QBrush(color))
            
            if len(points) == 2:
            
                if stroke_colour:
                    painter.setPen(stroke_pen)
                else:
                    painter.setPen(pen)
                painter.drawLine(viewport_scale_x * (points[0][0] + viewport_size[0]/2.0),
                                 viewport_scale_y * (viewport_size[1]/2.0 - points[0][1]),
                                 viewport_scale_x * (points[1][0] + viewport_size[0]/2.0),
                                 viewport_scale_y * (viewport_size[1]/2.0 - points[1][1]))
            
            else:
            
                painter.setPen(Qt.NoPen)
                new_points = []
                for x, y in points:
                    new_points.append(QPointF(viewport_scale_x * (x + viewport_size[0]/2.0),
                                              viewport_scale_y * (viewport_size[1]/2.0 - y)))
                
                polygon = QPolygonF(new_points)
                painter.drawPolygon(polygon)
        
        painter.end()
        image.save(png_path)
    
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
        w = width/2.0
        h = height/2.0
        
        new_polygons = []
        for polygon in polygons:
        
            new_points = []
            for point in polygon.points:
            
                new_points.append((w * (point.x/(w + a * -point.z)),
                                   h * (point.y/(h + b * -point.z))))
            
            new_polygons.append((new_points, polygon.colour))
        
        return new_polygons
