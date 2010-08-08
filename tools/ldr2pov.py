#!/usr/bin/env python

"""
ldr2pov.py - An LDraw to POV-Ray convertor tool.

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
import cmdsyntax
from ldraw.parts import Part, Parts, PartError
from ldraw.writers.povray import POVRayWriter
from ldraw import __version__


if __name__ == "__main__":

    syntax = "<LDraw parts file> <LDraw file> <POV-Ray file> <camera position> [<look at position>] [--sky <sky colour>]"
    syntax_obj = cmdsyntax.Syntax(syntax)
    matches = syntax_obj.get_args(sys.argv[1:])
    
    if len(matches) != 1:
        sys.stderr.write("Usage: %s %s\n\n" % (sys.argv[0], syntax))
        sys.stderr.write("ldr2pov.py (ldraw package version %s)\n" % __version__)
        sys.stderr.write("Converts the LDraw file to a POV-Ray file.\n\n"
                         "The camera position is a single x,y,z argument where each coordinate\n"
                         "should be specified as a floating point number.\n"
                         "The look at position is a single x,y,z argument where each coordinate\n"
                         "should be specified as a floating point number.\n"
                         "The optional sky colour is a single red,green,blue argument where\n"
                         "each component should be specified as a floating point number between\n"
                         "0.0 and 1.0 inclusive.\n\n")
        sys.exit(1)
    
    match = matches[0]
    parts_path = match["LDraw parts file"]
    ldraw_path = match["LDraw file"]
    pov_path = match["POV-Ray file"]
    camera_position = match["camera position"]
    look_at_position = match.get("look at position", "0.0,0.0,0.0")
    
    parts = Parts(parts_path)
    
    try:
        model = Part(ldraw_path)
    except PartError:
        sys.stderr.write("Failed to read LDraw file: %s\n" % ldraw_path)
        sys.exit(1)
    
    pov_file = open(pov_path, "w")
    pov_file.write('#include "colors.inc"\n\n')
    writer = POVRayWriter(parts, pov_file)
    writer.write(model)
    
    if not writer.lights:
    
        pov_file.write(
            "light_source {\n"
            "  <%1.3f, %1.3f, %1.3f>, rgb <1.0, 1.0, 1.0>\n"
            "}\n\n"
            "light_source {\n"
            "  <%1.3f, %1.3f, %1.3f>, rgb <1.0, 1.0, 1.0>\n"
            "}\n\n"
            "light_source {\n"
            "  <%1.3f, %1.3f, %1.3f>, rgb <1.0, 1.0, 1.0>\n"
            "}\n\n"
            "light_source {\n"
            "  <%1.3f, %1.3f, %1.3f>, rgb <1.0, 1.0, 1.0>\n"
            "}\n\n" % (writer.minimum.x - 50.0, writer.maximum.y + 100.0, writer.minimum.z - 50.0,
                       writer.maximum.x + 50.0, writer.maximum.y + 100.0, writer.minimum.z - 50.0,
                       writer.minimum.x - 50.0, writer.maximum.y + 100.0, writer.maximum.z + 50.0,
                       writer.maximum.x + 50.0, writer.maximum.y + 100.0, writer.maximum.z + 50.0)
            )
    
    pov_file.write(
        "camera {\n"
        "  location <%s>\n"
        "  look_at <%s>\n"
        "}\n" % (", ".join(camera_position.split(",")),
                 ", ".join(look_at_position.split(",")))
        )
    
    if match.has_key("sky"):
    
        pov_file.write(
            "sky_sphere {\n"
            "  pigment\n"
            "  {\n"
            "    rgb <%s>\n"
            "  }\n"
            "}\n" % match["sky colour"]
            )
    
    pov_file.close()
    
    for message, part in writer.warnings.keys():
        sys.stderr.write((message+"\n") % part)
    
    sys.exit()
