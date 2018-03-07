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
import sys

from ldraw.config import get_config
from ldraw.geometry import Vector
from ldraw.parts import Part, Parts, PartError
from ldraw.writers.png import PNGWriter


def main():
    # "<LDraw parts file> <LDraw file> <PNG file> <image size> <camera position> [<look-at position>] [--distance <eye to viewport distance>] [--stroke-colour <stroke colour>] [--sky <background colour>]"

    parser = argparse.ArgumentParser(description="Converts the LDraw file to a PNG file.\n\n"
                                                 "The image size must be specified in the format <width>x<height> where the width\n"
                                                 "and height are measured in pixels.\n\n"
                                                 "The camera and look-at positions are x,y,z arguments in LDraw scene coordinates\n"
                                                 "where each coordinate should be specified as a floating point number.\n\n"
                                                 "The eye to viewport distance is specified as a floating point number representing\n"
                                                 "a length in LDraw scene coordinates. Its default value is 1.0.\n\n"
                                                 "The optional sky background and stroke colours are PNG colours, either specified as\n"
                                                 "#rrggbb or as a named colour.\n\n")
    parser.add_argument('ldraw_file')
    parser.add_argument('png_file')
    parser.add_argument('image_size')
    parser.add_argument('camera_position')
    parser.add_argument('look_at_position', required=False, default="0,0,0")
    parser.add_argument('--distance', type=float, default=1.0)
    parser.add_argument('--stroke-colour', dest='stroke_colour')
    parser.add_argument('--sky')

    args = parser.parse_args()

    ldr2png(args.ldraw_file, args.png_file,
            args.distance, args.image_size, args.camera_position, args.look_at_position,
            args.sky, args.stroke_colour)


def ldr2png(ldraw_path, png_path,
            distance, image_size, camera_position, look_at_position,
            sky, stroke_colour):
    config = get_config()
    parts_path = config['parts.lst']

    image_dimensions = image_size.split("x")
    if len(image_dimensions) != 2:
        sys.stderr.write("Incorrect number of values specified for the image size: %s\n" % image_size)
        sys.exit(1)
    try:
        image_size = map(int, image_dimensions)
    except ValueError:
        sys.stderr.write("Non-integer value specified for the image size: %s\n" % image_size)
        sys.exit(1)

    camera_position = Vector(*map(float, camera_position.split(",")))
    look_at_position = Vector(*map(float, look_at_position.split(",")))

    parts = Parts(parts_path)

    try:
        model = Part(ldraw_path)
    except PartError:
        sys.stderr.write("Failed to read LDraw file: %s\n" % ldraw_path)
        sys.exit(1)

    if sky:
        background_colour = sky
    else:
        background_colour = "#000000"

    if camera_position == look_at_position:
        sys.stderr.write("Camera and look-at positions are the same.\n")
        sys.exit(1)

    z_axis = (camera_position - look_at_position)
    z_axis = z_axis / abs(z_axis)

    up = Vector(0, -1.0, 0)

    x_axis = up.cross(z_axis)
    if abs(x_axis) == 0.0:
        up = Vector(1.0, 0, 0)
        x_axis = z_axis.cross(up)

    x_axis = x_axis / abs(x_axis)
    y_axis = z_axis.cross(x_axis)

    writer = PNGWriter(camera_position, (x_axis, y_axis, z_axis), parts)
    writer.write(model, png_path, distance, image_size,
                 background_colour=background_colour,
                 stroke_colour=stroke_colour)


if __name__ == "__main__":
    main()
