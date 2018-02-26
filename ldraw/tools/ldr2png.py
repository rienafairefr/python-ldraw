#!/usr/bin/env python

"""
ldr2png.py - An LDraw to PNG convertor tool.

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
import argparse

from PIL import ImageColor

from ldraw.tools import (widthxheight, vector_position, get_model,
                         get_coordinate_system, verify_camera_look_at)
from ldraw.writers.png import PNGWriter, PNGArgs


def main():
    """ ldr2png main function """
    description = """Converts the LDraw file to a PNG file.
    
The image size must be specified in the format <width>x<height> where the width
and height are measured in pixels.

The camera and look-at positions are x,y,z arguments in LDraw scene coordinates
where each coordinate should be specified as a floating point number.

The eye to viewport distance is specified as a floating point number representing
a length in LDraw scene coordinates. Its default value is 1.0.

The optional sky background and stroke colours are PNG colours, either specified as
#rrggbb or as a named colour.

"""

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('ldraw_file')
    parser.add_argument('png_file')
    parser.add_argument('image_size', type=widthxheight)
    parser.add_argument('camera_position', type=vector_position)
    parser.add_argument('look_at_position', required=False, default=vector_position('0,0,0'))
    parser.add_argument('--distance', type=float, default=1.0)
    parser.add_argument('--stroke-colour', dest='stroke_colour', type=ImageColor.getrgb)
    parser.add_argument('--sky', default=ImageColor.getrgb('#000000'), type=ImageColor.getrgb)

    args = parser.parse_args()

    png_args = PNGArgs(args.distance, args.image_size, args.stroke_colour, args.sky)

    ldr2png(args.ldraw_file, args.png_file, args.look_at_position, args.camera_position, png_args)


def ldr2png(ldraw_path, png_path, look_at_position, camera_position, png_args):
    """ Implementation of ldr2png """
    verify_camera_look_at(camera_position, look_at_position)

    model, parts = get_model(ldraw_path)

    system = get_coordinate_system(camera_position, look_at_position)

    writer = PNGWriter(camera_position, system, parts)
    writer.write(model, png_path, png_args)


if __name__ == "__main__":
    main()
