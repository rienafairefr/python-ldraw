#!/usr/bin/env python

"""
ldr2svg.py - An LDraw to SVG convertor tool.

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
from ldraw.geometry import Vector, CoordinateSystem
from ldraw.parts import Part, Parts, PartError
from ldraw.tools import widthxheight, vector_position, UP_DIRECTION
from ldraw.writers.svg import SVGArgs


def main():
    """ ldr2svg main function """
    description = """Converts the LDraw file to a SVG file.
    
The viewport size is specified as a pair of floating point numbers representing
lengths in LDraw scene coordinates separated by an \"x\" character.

The camera and look-at positions are x,y,z argument in LDraw scene coordinates
where each coordinate should be specified as a floating point number.

The optional sky background colour is an SVG colour, either specified as
#rrggbb or as a named colour.

This tool requires PyQt4, built against Qt 4.4 or higher.

"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('ldraw_file')
    parser.add_argument('svg_file')
    parser.add_argument('viewport_size', type=widthxheight)
    parser.add_argument('camera_position', type=vector_position)
    parser.add_argument('look_at_position', type=vector_position,
                        required=False, default=vector_position("0,0,0"))
    parser.add_argument('--sky')
    parser.add_argument('--qt', default=True)

    args = parser.parse_args()
    svg_args = SVGArgs(args.viewport_size[0],
                       args.viewport_size[1],
                       background_colour=args.background_colour)

    ldr2svg(args.ldraw_file, args.svg_file,
            args.camera_position, args.look_at_position, args.qt, svg_args)


def ldr2svg(ldraw_path, svg_path, camera_position, look_at_position, use_qt, svg_args): # pylint: disable=too-many-arguments
    """ ldr2svg actual implementation """
    config = get_config()
    parts_path = config['parts.lst']

    parts = Parts(parts_path)

    try:
        model = Part(ldraw_path)
    except PartError:
        sys.stderr.write("Failed to read LDraw file: %s\n" % ldraw_path)
        sys.exit(1)

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

    with open(svg_path, "w") as svg_file:
        if use_qt:
            from ldraw.writers.qtsvg import QTSVGWriter
            writer = QTSVGWriter(camera_position, (x_axis, y_axis, z_axis), parts)
        else:
            from ldraw.writers.svg import SVGWriter
            writer = SVGWriter(camera_position, (x_axis, y_axis, z_axis), parts)
        writer.write(model, svg_file, svg_args)


if __name__ == "__main__":
    main()
