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
import argparse
import sys

from ldraw.config import get_config
from ldraw.parts import Part, Parts, PartError
from ldraw.tools import vector_position
from ldraw.writers.povray import POVRayWriter


def main():
    """ ldr2pov main function """

    description = """Converts the LDraw file to a POV-Ray file.
    
The camera position is a single x,y,z argument where each coordinate
should be specified as a floating point number.
The look at position is a single x,y,z argument where each coordinate
should be specified as a floating point number.
The optional sky colour is a single red,green,blue argument where
each component should be specified as a floating point number between
0.0 and 1.0 inclusive.

"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('ldraw_file')
    parser.add_argument('pov_file')
    parser.add_argument('camera_position', type=vector_position)
    parser.add_argument('look_at_position', type=vector_position, required=False,
                        default=vector_position("0,0,0"))
    parser.add_argument('--sky')

    args = parser.parse_args()

    ldr2pov(args.ldraw_file, args.pov_file,
            args.camera_position, args.look_at_position, args.sky)


def ldr2pov(ldraw_path, pov_path,
            camera_position, look_at_position, sky):
    config = get_config()
    ldraw_parts_path = config['parts.lst']
    parts = Parts(ldraw_parts_path)

    try:
        model = Part(ldraw_path)
    except PartError:
        sys.stderr.write("Failed to read LDraw file: %s\n" % ldraw_path)
        sys.exit(1)

    with open(pov_path, "w") as pov_file:
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
            "}\n" % (", ".join(str(p) for p in [camera_position.x, camera_position.y, camera_position.z]),
                     ", ".join(str(p) for p in [look_at_position.x, look_at_position.y, look_at_position.z]))
        )

        if sky:
            pov_file.write(
                "sky_sphere {\n"
                "  pigment\n"
                "  {\n"
                "    rgb <%s>\n"
                "  }\n"
                "}\n" % sky
            )

    for message, part in writer.warnings:
        sys.stderr.write((message + "\n") % part)


if __name__ == "__main__":
    main()
