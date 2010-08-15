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

import Numeric

from PyQt4.QtCore import QPointF, Qt
from PyQt4.QtGui import QBrush, QColor, QImage, QPainter, QPen, QPolygonF

class Polygon:

    def __init__(self, points, rgb, alpha):
    
        self.points = points
        colour = QColor(rgb)
        colour.setAlphaF(alpha)
        self.rgba = colour.rgb()
        self.projected = []
    
    def project(self, width, height):
    
        # vx' = width + az
        # vy' = height + bz
        
        a = 0.5
        b = 0.5
        w = width/2.0
        h = height/2.0
        
        for point in self.points:
        
            self.projected.append(
                (w * (point.x/(w + a * -point.z)),
                 h * (point.y/(h + b * -point.z)))
                )
    
    def render(self, image, depth, viewport_scale):
    
        # Sort the edges of the polygon by their minimum projected y
        # coordinates, discarding horizontal edges.
        width = image.width()
        height = image.height()
        z_max = 1 << 16
        
        edges = []
        l = len(self.points)
        
        for i in range(l):
        
            pxa, pya = self.projected[i]
            pxa = width/2 + (pxa * viewport_scale[0])
            pya = height/2 - (pya * viewport_scale[1])
            za = -self.points[i].z
            
            j = (i + 1) % l
            pxb, pyb = self.projected[j]
            pxb = width/2 + (pxb * viewport_scale[0])
            pyb = height/2 - (pyb * viewport_scale[1])
            zb = -self.points[j].z
            
            # Append the starting and finishing y coordinates, the starting
            # x coordinate, the dx/dy gradient of the edge, the starting
            # z coordinate and the dz/dy gradient of the edge.
            
            if int(pya) < int(pyb):
                edges.append((pya, pyb, pxa, (pxb - pxa)/(pyb - pya),
                              za, (zb - za)/(pyb - pya)))
            elif int(pya) > int(pyb):
                edges.append((pyb, pya, pxb, (pxa - pxb)/(pya - pyb),
                              zb, (za - zb)/(pya - pyb)))
        
        if not edges:
            #print "Discarding", self.projected
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
                dz = (sz2 - sz1)/(sx2 - sx1)
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
                
                    depth[int(sx)][int(py)] = sz
                    image.setPixel(sx, py, self.rgba)
                
                sx += 1
            
            py += 1


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
        depth = Numeric.empty((image_size[0], image_size[1]), "f")
        depth[:] = 1 << 32 - 1
        
        polygons = self._polygons_from_objects(model)
        
        if stroke_colour:
            stroke_pen.setColor(QColor(stroke_colour))
        
        if background_colour is not None:
            image.fill(QColor(background_colour).rgb())
        
        current_colour = None
        current_alpha = None
        
        viewport_scale = (image_size[0] / viewport_size[0],
                          image_size[1] / viewport_size[1])
        
        for polygon in polygons:
        
            polygon.project(viewport_size[0], viewport_size[1])
            polygon.render(image, depth, viewport_scale)
        
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
            
            #elif isinstance(obj, Line):
            #
            #    p1 = current_matrix * obj.p1 + current_position - c
            #    p2 = current_matrix * obj.p2 + current_position - c
            #    
            #    r1 = Vector(p1.dot(x), p1.dot(y), p1.dot(z))
            #    r2 = Vector(p2.dot(x), p2.dot(y), p2.dot(z))
            #    
            #    if r1.z >= 0 or r2.z >= 0:
            #        continue
            #    
            #    colour = self._current_colour(obj.colour, current_colour)
            #    rgb = self.parts.colours.get(colour, "#ffffff")
            #    alpha = self._opacity_from_colour(colour)
            #    polygons.append(Polygon([r1, r2], rgb, alpha))
            
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
                rgb = self.parts.colours.get(colour, "#ffffff")
                alpha = self._opacity_from_colour(colour)
                polygons.append(Polygon([r1, r2, r3], rgb, alpha))
            
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
                rgb = self.parts.colours.get(colour, "#ffffff")
                alpha = self._opacity_from_colour(colour)
                polygons.append(Polygon([r1, r2, r3, r4], rgb, alpha))
        
        return polygons
