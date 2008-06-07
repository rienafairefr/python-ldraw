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

class Parts:

    def __init__(self, path):
    
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
            pass
