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

from ldraw.config import Config
from ldraw.tools import vector_position, get_model


SKY_SPHERE_FORMAT_STRING = """sky_sphere {
  pigment
  {
    rgb <%s>
  }
}
"""

CAMERA_FORMAT_STRING = """camera {
  location <%s>
  look_at <%s>
}
"""

LIGHT_FORMAT_STRING = """light_source {
  <%1.3f, %1.3f, %1.3f>, rgb <1.0, 1.0, 1.0>
}

light_source {
  <%1.3f, %1.3f, %1.3f>, rgb <1.0, 1.0, 1.0>
}

light_source {
  <%1.3f, %1.3f, %1.3f>, rgb <1.0, 1.0, 1.0>
}

light_source {
  <%1.3f, %1.3f, %1.3f>, rgb <1.0, 1.0, 1.0>
}

"""


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
    parser.add_argument("ldraw_file", type=argparse.FileType(mode='r'))
    parser.add_argument("pov_file", type=argparse.FileType(mode='w'))
    parser.add_argument("camera_position", type=vector_position)
    parser.add_argument(
        "--look_at_position",
        type=vector_position,
        required=False,
        default=vector_position("0,0,0"),
    )
    parser.add_argument("--sky")

    args = parser.parse_args()
    config = Config.load()

    ldr2pov(
        config,
        args.ldraw_file,
        args.pov_file,
        args.camera_position,
        args.look_at_position,
        args.sky,
    )


def ldr2pov(config, ldraw_model_file, pov_path, camera_position, look_at_position, sky):
    """ actual ldr2pov implementation """
    model, parts = get_model(config, ldraw_model_file)

    with open(pov_path, "w") as pov_file:
        pov_file.write('#include "colors.inc"\n\n')
        from ldraw.writers.povray import POVRayWriter
        writer = POVRayWriter(parts, pov_file)
        writer.write(model)

        if not writer.lights:
            lights = (
                writer.minimum.x - 50.0,
                writer.maximum.y + 100.0,
                writer.minimum.z - 50.0,
                writer.maximum.x + 50.0,
                writer.maximum.y + 100.0,
                writer.minimum.z - 50.0,
                writer.minimum.x - 50.0,
                writer.maximum.y + 100.0,
                writer.maximum.z + 50.0,
                writer.maximum.x + 50.0,
                writer.maximum.y + 100.0,
                writer.maximum.z + 50.0,
            )
            pov_file.write(LIGHT_FORMAT_STRING % lights)

        pov_file.write(
            CAMERA_FORMAT_STRING % (camera_position.repr, look_at_position.repr)
        )

        if sky:
            if sky.startswith('#') and len(sky) == 7:
                h = sky.lstrip('#')
                rgb = tuple(int(h[i:i + 2], 16)/256 for i in (0, 2, 4))
                sky = ','.join(str(round(s, 4)) for s in rgb)
                pov_file.write(SKY_SPHERE_FORMAT_STRING % sky)
            else:
                print('need sky in hex: #RRGGBB')
                sys.exit(-1)

    for message, part in writer.warnings:
        sys.stderr.write((message + "\n") % part)


if __name__ == "__main__":
    main()
