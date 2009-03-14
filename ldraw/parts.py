"""
parts.py - Part management classes for the Python ldraw package.

Copyright (C) 2008 David Boddie <david@boddie.org.uk>

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

import os
from colours import Colour
from geometry import Matrix, Vector
from pieces import Piece

class PartError(Exception):

    pass


class Parts:

    def __init__(self, path):
    
        self.path = None
        self.parts_dir = None
        self.parts = {}
        self.colours = {}
        
        self.Hats = {}
        self.Heads = {}
        self.Torsos = {}
        self.Hips = {}
        self.Legs = {}
        self.Arms = {}
        self.Hands = {}
        
        self.sections = {
            "Cap":    self.Hats,
            "Hat":    self.Hats,
            "Helmet": self.Hats,
            "Hair":   self.Hats,
            "Mask":   self.Hats,
            "Plume":  self.Hats,
            
            "Minifig Head":    self.Heads,
            "Mechanical Head": self.Heads,
            "Skull":  self.Heads,
            
            "Torso":  self.Torsos,
            
            "Hips":   self.Hips,
            
            "Leg":    self.Legs,
            "Legs":   self.Legs,
            
            "Arm":    self.Arms,
            
            "Hand":   self.Hands
            }
        
        self.load(path)
    
    def load(self, path):
    
        try:
            f = open(path)
            for line in f.readlines():
            
                pieces = line.split(".DAT")
                if len(pieces) != 2:
                    break
                
                code = pieces[0]
                description = pieces[1].strip()
                self.parts[description] = code
                
                for key, section in self.sections.items():
                
                    at = description.find(key)
                    if at != -1 and (
                        at + len(key) == len(description) or \
                        description[at+len(key)] == " "):
                    
                        if description.startswith("Minifig "):
                            description = description[8:]
                            if description.startswith("(") and description.endswith(")"):
                                description = description[1:-1]
                            
                        section[description] = code
                        break
        except IOError:
            return
        
        # If we successfully loaded the file then record the path and look for
        # part files.
        
        self.path = path
        directory = os.path.split(self.path)[0]
        for item in os.listdir(directory):
            if item.lower() == "parts" and \
                os.path.isdir(os.path.join(directory, item)):
            
                self.parts_dir = os.path.join(directory, item)
            
            elif item.lower() == "ldconfig" + os.extsep + "ldr":
                self._load_colours(os.path.join(directory, item))
    
    def part(self, description = None, code = None):
    
        if not self.path:
            return None
        
        if description:
            try:
                code = self.parts[description]
            except KeyError:
                return None
        
        elif not code:
            return None
        
        return self._load_part(code)
    
    def _load_part(self, code):
    
        paths = (os.path.join(self.parts_dir, code.lower()) + os.extsep + "dat",
                 os.path.join(self.parts_dir, code.upper()) + os.extsep + "DAT")
        
        for path in paths:
            part = Part(path)
            if part:
                return part
        
        return None
    
    def _load_colours(self, path):
    
        try:
            colours_part = Part(path)
        except PartError:
            return
        
        for obj in colours_part.objects:
        
            if isinstance(obj, MetaCommand) and obj.text.startswith("!COLOUR"):
            
                pieces = obj.text.split()
                try:
                    name = pieces[1]
                    code = int(pieces[pieces.index("CODE") + 1])
                    value = pieces[pieces.index("VALUE") + 1]
                    self.colours[name] = value
                    self.colours[code] = value
                except (ValueError, IndexError):
                    pass


class Part:

    def __init__(self, path):
    
        self._handlers = {
            "0": self._comment_or_meta,
            "1": self._subfile,
            "2": self._line,
            "3": self._triangle,
            "4": self._quadrilateral,
            "5": self._optional_line
            }
        self.load(path)
    
    def load(self, path):
    
        self.path = path
        
        try:
            lines = open(path).readlines()
        except IOError:
            raise PartError, "Failed to read part file: %s" % path
        
        objects = []
        number = 0
        for line in lines:
        
            number += 1
            
            pieces = line.split()
            if not pieces:
                objects.append(BlankLine)
                continue
            
            try:
                handler = self._handlers[pieces[0]]
            except KeyError:
                raise PartError, "Unknown command (%s) in %s at line %i" % (path, pieces[0], number)
            
            objects.append(handler(pieces[1:], number))
        
        self.objects = objects
    
    def _comment_or_meta(self, pieces, line):
    
        if not pieces:
            return Comment("")
        elif pieces[0][:1] == "!":
            return MetaCommand(" ".join(pieces))
        else:
            return Comment(" ".join(pieces))
    
    def _subfile(self, pieces, line):
    
        if len(pieces) != 14:
            raise PartError, "Invalid part data in %s at line %i" % (self.path, line)
        
        colour = int(pieces[0])
        position = map(float, pieces[1:4])
        rows = [map(float, pieces[4:7]),
                map(float, pieces[7:10]),
                map(float, pieces[10:13])]
        part = pieces[13].upper()
        if part.endswith(".DAT"):
            part = part[:-4]
        
        return Piece(Colour(colour), Vector(*position), Matrix(rows), part)
    
    def _line(self, pieces, line):
    
        if len(pieces) != 7:
            raise PartError, "Invalid line data in %s at line %i" % (self.path, line)
        
        colour = int(pieces[0])
        p1 = map(float, pieces[1:4])
        p2 = map(float, pieces[4:7])
        
        return Line(Colour(colour), Vector(*p1), Vector(*p2))
    
    def _triangle(self, pieces, line):
    
        if len(pieces) != 10:
            raise PartError, "Invalid triangle data in %s at line %i" % (self.path, line)
        
        colour = int(pieces[0])
        p1 = map(float, pieces[1:4])
        p2 = map(float, pieces[4:7])
        p3 = map(float, pieces[7:10])
        
        return Triangle(Colour(colour), Vector(*p1), Vector(*p2), Vector(*p3))
    
    def _quadrilateral(self, pieces, line):
    
        if len(pieces) != 13:
            raise PartError, "Invalid quadrilateral data in %s at line %i" % (self.path, line)
        
        colour = int(pieces[0])
        p1 = map(float, pieces[1:4])
        p2 = map(float, pieces[4:7])
        p3 = map(float, pieces[7:10])
        p4 = map(float, pieces[10:13])
        
        return Quadrilateral(Colour(colour), Vector(*p1), Vector(*p2),
                                             Vector(*p3), Vector(*p4))
    
    def _optional_line(self, pieces, line):
    
        if len(pieces) != 13:
            raise PartError, "Invalid line data in %s at line %i" % (self.path, line)
        
        colour = int(pieces[0])
        p1 = map(float, pieces[1:4])
        p2 = map(float, pieces[4:7])
        p3 = map(float, pieces[7:10])
        p4 = map(float, pieces[10:13])
        
        return OptionalLine(Colour(colour), Vector(*p1), Vector(*p2),
                                            Vector(*p3), Vector(*p4))


class BlankLine:

    pass

class Comment:

    def __init__(self, text):
    
        self.text = text

class MetaCommand:

    def __init__(self, text):
    
        self.text = text

class Line:

    def __init__(self, colour, p1, p2):
    
        self.colour = colour
        self.p1 = p1
        self.p2 = p2

class Triangle:

    def __init__(self, colour, p1, p2, p3):
    
        self.colour = colour
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

class Quadrilateral:

    def __init__(self, colour, p1, p2, p3, p4):
    
        self.colour = colour
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

class OptionalLine:

    def __init__(self, colour, p1, p2, p3, p4):
    
        self.colour = colour
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
